#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_cdl.py

Repair the CDL source-netlist "body map" bug that aborts Calibre PEX RCC
extraction ("Terminate LPE running due to CCI-LVS result is NOT Clean !!").

Root cause being fixed
----------------------
The layout ties NMOS bodies to vss! and PMOS bodies to vcc!.  In the source
CDL, some leaf/buffer instance that lives inside the root (top) subcircuit
wires its N/P body pins (vbn/vbp) to the root's floating global body ports
(vbn!/vbp!) instead of the power/ground rails (vss!/vcc!).  That one wrong
body mapping makes CCI-LVS dirty.

What the tool does (fully data driven, no design-specific hardcoding)
---------------------------------------------------------------------
1. Parse every .SUBCKT's ordered port table and every X-line instance.
2. Identify the ROOT subcircuit = the one never instantiated by any other
   subcircuit.  Only instance lines inside that root subcircuit are ever
   touched; every instance inside any sub-module is left byte-for-byte intact.
3. For each instance in the root, the "body pin" position in the instance
   line is taken from the referenced leaf subcircuit's port table (it is never
   assumed to be a fixed column).
4. Only when a body pin is actually connected to a floating body net of the
   same class (n-body -> vbn, p-body -> vbp) is it rewritten; the replacement
   target is the very same ground/power rail that the instance already uses
   for its (correct) ground/power ports, so already-correct instances are left
   untouched.
5. Preserves the total line count and the .SUBCKT/.ENDS pairing (it only does
   in-line token rewrites, never adds/removes lines).
6. Writes a byte-identical backup as <input_cdl>.bak and a JSON diff report.

Usage
-----
    python3 fix_cdl.py <input_cdl> <output_cdl> <diff_report_json>

Exit code: 0 = success, non-zero = error / netlist not well formed.
"""

import json
import shutil
import sys

# --------------------------------------------------------------------------- #
# net-class recognition (standard CDL rail/body net names only)
# --------------------------------------------------------------------------- #

# Conventional *classes*, applied on the lower-cased net name with any trailing
# '!' global marker stripped.  NOT design-specific (vss/gnd=ground, vcc/vdd=
# power, vbn=N body, vbp=P body).
GROUND_NAMES = {"vss", "gnd"}
POWER_NAMES = {"vcc", "vdd"}
NBODY_NAMES = {"vbn"}
PBODY_NAMES = {"vbp"}


def normalize_net(name):
    """Lower-case a net name and strip trailing '!' global markers."""
    n = (name or "").strip()
    while n.endswith("!"):
        n = n[:-1]
    return n.lower()


def net_class(name):
    """Return 'ground', 'power', 'nbody', 'pbody', or None."""
    n = normalize_net(name)
    if n in GROUND_NAMES:
        return "ground"
    if n in POWER_NAMES:
        return "power"
    if n in NBODY_NAMES:
        return "nbody"
    if n in PBODY_NAMES:
        return "pbody"
    return None


# --------------------------------------------------------------------------- #
# parsing
# --------------------------------------------------------------------------- #

def drop_comment_tokens(tokens):
    """Drop trailing SPICE inline-comment tokens ('$...' / '*...')."""
    out = []
    for t in tokens:
        if t.startswith("$") or t.startswith("*"):
            break
        out.append(t)
    return out


def parse_instance(tokens):
    """
    Parse an X-instance line's whitespace tokens.

    Supported forms:
        XI37 n1 n2 n3 vbn! vbp! vcc! vss! / bufLx4      (explicit subckt ref)
        Xb0  A  n1 vbn vbp vcc vss bufLx1                 (ref = last token)

    Returns (instance_name, connections, subckt_ref).
    """
    inst_name = tokens[0]
    tokens = drop_comment_tokens(tokens)

    slash_idx = None
    for i, t in enumerate(tokens):
        if t == "/":
            slash_idx = i
            break

    if slash_idx is not None:
        connections = tokens[1:slash_idx]
        ref = tokens[slash_idx + 1] if slash_idx + 1 < len(tokens) else ""
    else:
        if len(tokens) >= 2:
            connections = tokens[1:-1]
            ref = tokens[-1]
        else:
            connections = []
            ref = ""

    return inst_name, connections, ref


def parse_subckts(lines):
    """
    Parse a list of source lines (with endings intact).

    Returns (subckts, order) where
        subckts[name] = {
            "ports": [ordered formal port names],
            "instances": [{"line_no": int, "tokens": [str, ...]}, ...],
        }
        order = definition order of subckt names.
    """
    subckts = {}
    order = []
    current = None

    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("*") or line.startswith("$"):
            continue
        tokens = line.split()
        if not tokens:
            continue
        head = tokens[0].upper()

        if head == ".SUBCKT":
            tokens = drop_comment_tokens(tokens)
            if len(tokens) >= 2:
                name = tokens[1]
                ports = tokens[2:]
                subckts[name] = {"ports": list(ports), "instances": []}
                order.append(name)
                current = name
        elif head == ".ENDS":
            current = None
        elif head.startswith("X") and current is not None:
            subckts[current]["instances"].append(
                {"line_no": idx, "tokens": tokens}
            )

    return subckts, order


def find_root(subckts, order):
    """Return the subckt name that is never instantiated by any other subckt."""
    instantiated = set()
    for sub in subckts.values():
        for inst in sub["instances"]:
            _, _, ref = parse_instance(inst["tokens"])
            if ref:
                instantiated.add(ref)

    candidates = [n for n in order if n not in instantiated]
    if candidates:
        # The top level is normally declared last; prefer the last candidate.
        return candidates[-1]
    return order[-1] if order else None


def line_ending(raw):
    if raw.endswith("\r\n"):
        return "\r\n"
    if raw.endswith("\n"):
        return "\n"
    return ""


def fix_root(subckts, root, lines):
    """
    Rewrite body-pin nets inside `root` only.

    Returns (out_lines, changed) where `changed` is a list of
    {"line_no", "old", "new"}.
    """
    root_ports = subckts[root]["ports"]

    # Fallback rails from the root's own port list (used only if a leaf cell
    # has no explicit ground/power port to learn the target from).
    root_ground = next((p for p in root_ports if net_class(p) == "ground"), "vss!")
    root_power = next((p for p in root_ports if net_class(p) == "power"), "vcc!")

    out_lines = list(lines)
    changed = []

    for inst in subckts[root]["instances"]:
        line_no = inst["line_no"]
        tokens = inst["tokens"]
        _, connections, ref = parse_instance(tokens)

        if not ref or ref not in subckts:
            continue  # leaf/primitive with no port table available -> skip

        leaf_ports = subckts[ref]["ports"]
        if len(connections) != len(leaf_ports):
            continue  # cannot align connections to ports -> leave untouched

        # Learn the correct ground/power rail as wired by *this* instance
        # through its (correct) ground/power ports.
        ground_conn = None
        power_conn = None
        for i, port in enumerate(leaf_ports):
            cls = net_class(port)
            if cls == "ground" and ground_conn is None:
                ground_conn = connections[i]
            elif cls == "power" and power_conn is None:
                power_conn = connections[i]

        new_tokens = list(tokens)
        modified = False

        for i, port in enumerate(leaf_ports):
            cls = net_class(port)
            conn = connections[i]
            if cls == "nbody" and net_class(conn) == "nbody":
                target = ground_conn if ground_conn is not None else root_ground
                if target != conn:
                    new_tokens[1 + i] = target  # instance name occupies index 0
                    modified = True
            elif cls == "pbody" and net_class(conn) == "pbody":
                target = power_conn if power_conn is not None else root_power
                if target != conn:
                    new_tokens[1 + i] = target
                    modified = True

        if modified:
            raw = lines[line_no - 1]
            ending = line_ending(raw)
            old_text = raw[: len(raw) - len(ending)] if ending else raw
            new_text = " ".join(new_tokens)
            out_lines[line_no - 1] = new_text + ending
            changed.append(
                {"line_no": line_no, "old": old_text, "new": new_text}
            )

    return out_lines, changed


def count_subckt_ends(lines):
    subckt = 0
    ends = 0
    for raw in lines:
        t = raw.strip().split()
        if not t:
            continue
        h = t[0].upper()
        if h == ".SUBCKT":
            subckt += 1
        elif h == ".ENDS":
            ends += 1
    return subckt, ends


def main(argv):
    if len(argv) != 4:
        print(
            "usage: python3 fix_cdl.py <input_cdl> <output_cdl> <diff_report_json>",
            file=sys.stderr,
        )
        return 2

    in_path, out_path, json_path = argv[1], argv[2], argv[3]

    try:
        with open(in_path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print("error: cannot read %s: %s" % (in_path, exc), file=sys.stderr)
        return 1

    lines = text.splitlines(keepends=True)
    original_count = len(lines)

    subckts, order = parse_subckts(lines)
    if not subckts:
        print("error: no .SUBCKT definitions found in %s" % in_path, file=sys.stderr)
        return 1

    root = find_root(subckts, order)
    if root is None:
        print("error: cannot determine root subcircuit", file=sys.stderr)
        return 1

    out_lines, changed = fix_root(subckts, root, lines)

    # Byte-identical backup next to the input file.
    backup_path = in_path + ".bak"
    try:
        shutil.copyfile(in_path, backup_path)
    except OSError as exc:
        print("error: cannot write backup %s: %s"
              % (backup_path, exc), file=sys.stderr)
        return 1

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("".join(out_lines))
    except OSError as exc:
        print("error: cannot write %s: %s" % (out_path, exc), file=sys.stderr)
        return 1

    subckt_count, ends_count = count_subckt_ends(out_lines)
    wellformed = subckt_count == ends_count
    line_count_unchanged = len(out_lines) == original_count

    report = {
        "changed_lines": changed,
        "wellformed": bool(wellformed),
        "line_count_unchanged": bool(line_count_unchanged),
        "subckt_count": subckt_count,
        "ends_count": ends_count,
        "total_lines": len(out_lines),
    }

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except OSError as exc:
        print("error: cannot write %s: %s" % (json_path, exc), file=sys.stderr)
        return 1

    if not wellformed:
        print("error: .SUBCKT/.ENDS count mismatch (%d vs %d)"
              % (subckt_count, ends_count), file=sys.stderr)
        return 1
    if not line_count_unchanged:
        print("error: total line count changed", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))