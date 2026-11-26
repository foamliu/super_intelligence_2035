#!/usr/bin/env python3
"""RTEXT / RNODE label audit + cleanup advisor for rscalc power-net pre-check.

Parses a virtuoso label-inventory text dump (one label per line), filters out
drawing-purpose labels (GDS net-name tags such as "vblh!"), groups the
remaining RTEXT / RNODE labels by net, and reports:

  * per-net verdict  ALIGNED / GARBAGE / MISSING_RTEXT
  * garbage nets     (RTEXT > 0  but  RNODE == 0)  -> debug leftovers
  * duplicate labels (dedup by (layer, purpose, net, x, y))
  * a suggested-delete list (garbage + duplicate labels, with xy)

The audit is per-net, not a naive total counter: a net with a source point but
no checkpoint is a GARBAGE net and must be deleted, not counted toward "ok".

Usage:
    python3 rtext_rnode_audit.py --inventory <file>

Exit code is 0 once auditing completes (whether the result is ALIGNED or
MISALIGNED). A non-zero exit signals a CLI/parse error.
"""

import argparse
import re
import sys
from collections import Counter, defaultdict

# (LAYER "PURPOSE")  "NET"  xy=(X Y)   -- LAYER may or may not be quoted.
LINE_RE = re.compile(
    r'^\s*\(\s*"?(?P<layer>[^"\s)]+)"?\s+"(?P<purpose>[^"]+)"\s*\)'
    r'\s+"(?P<net>[^"]+)"\s+'
    r'xy=\s*\(\s*(?P<x>-?\d+(?:\.\d+)?)\s+(?P<y>-?\d+(?:\.\d+)?)\s*\)\s*$'
)

VALID_PURPOSES = {"RTEXT", "RNODE"}


def parse_inventory(path):
    """Return (labels, skipped, errors) where labels are RTEXT/RNODE only."""
    labels = []
    skipped = 0
    errors = []
    with open(path, "r") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = LINE_RE.match(line)
            if not m:
                errors.append((lineno, line))
                continue
            purpose = m.group("purpose")
            if purpose not in VALID_PURPOSES:
                skipped += 1  # drawing / anything else: ignore
                continue
            labels.append({
                "layer": m.group("layer"),
                "purpose": purpose,
                "net": m.group("net"),
                "x": float(m.group("x")),
                "y": float(m.group("y")),
                "xstr": m.group("x"),
                "ystr": m.group("y"),
            })
    return labels, skipped, errors


def _key(lab):
    # full dedup identity: same layer + purpose + net + coordinate
    return (lab["layer"], lab["purpose"], lab["net"],
            round(lab["x"], 6), round(lab["y"], 6))


def _coord_key(lab):
    return (lab["layer"], round(lab["x"], 6), round(lab["y"], 6))


def audit(labels):
    """Group by net, dedup, verdict; return a structured result dict."""
    key_counts = Counter(_key(l) for l in labels)
    duplicate_labels = sum(c - 1 for c in key_counts.values() if c > 1)

    by_net = defaultdict(list)
    for lab in labels:
        by_net[lab["net"]].append(lab)

    nets = {}
    for net, labs in by_net.items():
        rtext = {_coord_key(l) for l in labs if l["purpose"] == "RTEXT"}
        rnode = {_coord_key(l) for l in labs if l["purpose"] == "RNODE"}
        layers = sorted({l["layer"] for l in labs})
        rtext_n = len(rtext)
        rnode_n = len(rnode)
        if rtext_n > 0 and rnode_n > 0:
            verdict = "ALIGNED"
        elif rtext_n > 0 and rnode_n == 0:
            verdict = "GARBAGE"
        elif rnode_n > 0 and rtext_n == 0:
            verdict = "MISSING_RTEXT"
        else:
            verdict = "EMPTY"
        nets[net] = {
            "rtext": rtext_n,
            "rnode": rnode_n,
            "layers": layers,
            "verdict": verdict,
        }

    garbage_nets = sorted(n for n, v in nets.items() if v["verdict"] == "GARBAGE")
    missing_nets = sorted(n for n, v in nets.items() if v["verdict"] == "MISSING_RTEXT")

    # suggested delete list: garbage net labels + duplicate (extra) copies
    deletes = []
    for lab in labels:
        if nets[lab["net"]]["verdict"] == "GARBAGE":
            deletes.append((lab, "garbage"))
    seen = set()
    for lab in labels:
        k = _key(lab)
        if k in seen:
            deletes.append((lab, "duplicate"))
        else:
            seen.add(k)

    overall = ("ALIGNED" if duplicate_labels == 0 and not garbage_nets
               and not missing_nets and all(v["verdict"] == "ALIGNED"
                                            for v in nets.values())
               else "MISALIGNED")

    return {
        "nets": nets,
        "garbage_nets": garbage_nets,
        "missing_nets": missing_nets,
        "duplicate_labels": duplicate_labels,
        "deletes": deletes,
        "overall": overall,
        "total_labels": len(labels),
    }


def fmt_xy(lab):
    return "xy=(%s %s)" % (lab["xstr"], lab["ystr"])


def render(res, inventory, skipped):
    lines = []
    lines.append("=== RTEXT / RNODE label audit ===")
    lines.append("inventory       : %s" % inventory)
    lines.append("labels parsed   : %d (RTEXT + RNODE, drawing ignored)" % res["total_labels"])
    lines.append("drawing skipped : %d" % skipped)
    lines.append("nets            : %d" % len(res["nets"]))
    lines.append("")

    lines.append("--- per-net audit ---")
    for net in sorted(res["nets"]):
        v = res["nets"][net]
        lines.append("net=%s  RTEXT=%d  RNODE=%d  layers=%s  verdict=%s"
                     % (net, v["rtext"], v["rnode"], ",".join(v["layers"]),
                        v["verdict"]))
    lines.append("")

    lines.append("--- summary ---")
    lines.append("garbage_nets: %d" % len(res["garbage_nets"]))
    for n in res["garbage_nets"]:
        lines.append("  %s" % n)
    lines.append("missing_rtext_nets: %d" % len(res["missing_nets"]))
    for n in res["missing_nets"]:
        lines.append("  %s" % n)
    lines.append("duplicate_labels: %d" % res["duplicate_labels"])

    lines.append("")
    lines.append("--- suggested delete list (%d) ---" % len(res["deletes"]))
    for lab, reason in res["deletes"]:
        lines.append("DELETE  (%s)  (%s \"%s\")  \"%s\"  %s"
                     % (reason, lab["layer"], lab["purpose"], lab["net"],
                        fmt_xy(lab)))

    lines.append("")
    lines.append("overall: %s" % res["overall"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Audit RTEXT/RNODE label inventory for rscalc readiness.")
    ap.add_argument("--inventory", required=True, metavar="FILE",
                    help="label inventory dump to audit")
    args = ap.parse_args(argv)

    try:
        labels, skipped, errors = parse_inventory(args.inventory)
    except OSError as e:
        print("ERROR: cannot read inventory: %s" % e, file=sys.stderr)
        return 2

    if errors:
        for lineno, line in errors:
            print("WARN: parse error at line %d: %r" % (lineno, line),
                  file=sys.stderr)

    res = audit(labels)
    sys.stdout.write(render(res, args.inventory, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())