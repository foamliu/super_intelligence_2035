#!/usr/bin/env python3
"""Comprehensive 3-way analysis: cline-patched / Pi / Hermes from kimi_pilot_results.json."""
import json, sys, statistics, re
from collections import Counter, defaultdict

data = json.load(open("kimi_pilot_results.json"))
target = {"cline-patched", "pi", "hermes"}
entries = [e for e in data if e.get("harness") in target]

stats = defaultdict(lambda: {
    "total": 0, "resolved": 0, "pbf": 0, "quota": 0, "infra": 0,
    "walls": [], "patch_sizes": [], "f2p_pass": [], "p2p_pass": [],
    "repos": defaultdict(lambda: {"total": 0, "resolved": 0}),
    "instances": {},
})

for e in entries:
    h = e["harness"]
    hr = e.get("harness_result", {})
    ev = hr.get("eval", {})
    s = stats[h]
    s["total"] += 1
    cls = e.get("classification", "")
    if cls == "resolved": s["resolved"] += 1
    elif cls == "patch-but-failed": s["pbf"] += 1
    elif cls == "quota-blocked": s["quota"] += 1
    else: s["infra"] += 1
    s["walls"].append(hr.get("wall_s", 0))
    s["repos"][e["repo"]]["total"] += 1
    if cls == "resolved": s["repos"][e["repo"]]["resolved"] += 1
    s["instances"][e["instance_id"]] = cls
    s["f2p_pass"].append(ev.get("f2p_pass", 0))
    s["p2p_pass"].append(ev.get("p2p_pass", 0))
    tail = hr.get("stdout_tail", "") or ""
    m = re.search(r"model_patch:\s*(\d+)\s*bytes", tail)
    if m: s["patch_sizes"].append(int(m.group(1)))

print("=" * 70)
print("3-Way Comparison: cline-patched vs Pi vs Hermes")
print("=" * 70)
for h in ["cline-patched", "pi", "hermes"]:
    s = stats[h]
    print(f"\n  {h}:")
    print(f"  Total={s['total']} Resolved={s['resolved']} ({100*s['resolved']/s['total']:.1f}%) PBF={s['pbf']}")
    if s["walls"]:
        print(f"  Wall: mean={statistics.mean(s['walls']):.0f}s median={statistics.median(s['walls']):.0f}s min={min(s['walls']):.0f}s max={max(s['walls']):.0f}s")
    if s["patch_sizes"]:
        print(f"  Patch: mean={statistics.mean(s['patch_sizes']):.0f}B median={statistics.median(s['patch_sizes']):.0f}B")
    for repo, rs in sorted(s["repos"].items()):
        print(f"    {repo}: {rs['resolved']}/{rs['total']}")

# Per-instance
all_instances = sorted(set(e["instance_id"] for e in entries))
print(f"\n{'='*70}")
print("Per-instance:")
print(f"{'Instance':<40} {'cline':>6} {'pi':>6} {'hermes':>6}")
for inst in all_instances:
    c = stats["cline-patched"]["instances"].get(inst, "-")
    p = stats["pi"]["instances"].get(inst, "-")
    he = stats["hermes"]["instances"].get(inst, "-")
    c_s = "Y" if c == "resolved" else "N" if c == "patch-but-failed" else "-"
    p_s = "Y" if p == "resolved" else "N" if p == "patch-but-failed" else "-"
    h_s = "Y" if he == "resolved" else "N" if he == "patch-but-failed" else "-"
    print(f"{inst:<40} {c_s:>6} {p_s:>6} {h_s:>6}")

# Overlap
cr = set(i for i, c in stats["cline-patched"]["instances"].items() if c == "resolved")
pr = set(i for i, c in stats["pi"]["instances"].items() if c == "resolved")
hr = set(i for i, c in stats["hermes"]["instances"].items() if c == "resolved")
print(f"\nOverlap: cline&pi={len(cr&pr)} cline&hermes={len(cr&hr)} pi&hermes={len(pr&hr)} all3={len(cr&pr&hr)}")
print(f"cline_only={len(cr-pr-hr)} pi_only={len(pr-cr-hr)} hermes_only={len(hr-cr-pr)} none={len(set(all_instances)-cr-pr-hr)}")

# Failure evidence
print(f"\n{'='*70}")
print("Failure Evidence:")
for h in ["cline-patched", "pi", "hermes"]:
    print(f"\n--- {h} ---")
    count = 0
    for e in entries:
        if e["harness"] == h and e["classification"] == "patch-but-failed":
            hr2 = e.get("harness_result", {})
            tail = hr2.get("stdout_tail", "") or ""
            ev = hr2.get("eval", {})
            print(f"  [{e['instance_id']}] wall={hr2.get('wall_s',0):.0f}s f2p={ev.get('f2p_pass',0)}/{ev.get('f2p_total',0)} p2p={ev.get('p2p_pass',0)}/{ev.get('p2p_total',0)}")
            print(f"    tail: ...{tail[-400:]}")
            count += 1
            if count >= 4: break
