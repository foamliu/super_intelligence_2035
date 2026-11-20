#!/usr/bin/env python3
"""Deep analysis of 7x30 cross-eval interaction traces for report_harness_interaction_traces.html."""
import json, re, statistics
from pathlib import Path
from collections import defaultdict, Counter

HERE = Path(__file__).resolve().parent
DATA = json.load(open(HERE / "kimi_pilot_results.json"))
WD = Path("/dev/shm/harness_work/workdirs")
ORDER = ["cline-patched", "pi", "hermes", "opencode", "codex", "claude-code", "deepseek-harness"]
ref_insts = sorted(set(e["instance_id"] for e in DATA if e["harness"] == "cline-patched"))
subset = [e for e in DATA if e["instance_id"] in set(ref_insts)]

print("=" * 80)
print("PART 1: DATA AVAILABILITY INVENTORY")
print("=" * 80)
print("\n--- stdout_tail content analysis ---")
for h in ORDER:
    entries = [e for e in subset if e["harness"] == h]
    tails = [e.get("harness_result", {}).get("stdout_tail", "") or "" for e in entries]
    has_patch_info = sum(1 for t in tails if "model_patch" in t)
    has_error = sum(1 for t in tails if "error" in t.lower())
    avg_len = sum(len(t) for t in tails) / len(tails)
    print(f"  {h:20s} avg_len={avg_len:.0f} patch_info={has_patch_info}/30 errors={has_error}/30")

print("\n--- Predictions files surviving in /dev/shm ---")
for h in ORDER:
    entries = [e for e in subset if e["harness"] == h]
    found = 0
    for e in entries:
        inst = e["instance_id"]
        h_slug = h.replace("-", "_")
        inst_slug = inst.replace("/", "__")
        fpath = WD / f"predictions_kimi_{h_slug}_{inst_slug}.json"
        if not fpath.exists():
            fpath = WD / f"predictions_{h_slug}_{inst_slug}.json"
        if fpath.exists():
            found += 1
    print(f"  {h:20s} {found}/30 predictions files surviving")

# Comprehensive per-harness stats
stats = {}
for h in ORDER:
    entries = [e for e in subset if e["harness"] == h]
    s = {"total": len(entries), "resolved": 0, "pbf": 0, "quota": 0,
         "walls_all": [], "walls_res": [], "walls_fail": [],
         "patch_sizes_all": [], "patch_sizes_res": [], "patch_sizes_fail": [],
         "returncodes": Counter(), "fail_modes": Counter(),
         "repos": defaultdict(lambda: {"total": 0, "resolved": 0})}
    for e in entries:
        hr = e.get("harness_result", {})
        cls = e.get("classification", "")
        wall = hr.get("wall_s", 0)
        s["returncodes"][hr.get("returncode", 0)] += 1
        s["walls_all"].append(wall)
        s["repos"][e["repo"]]["total"] += 1
        tail = hr.get("stdout_tail", "") or ""
        m = re.search(r"model_patch:\s*(\d+)\s*bytes", tail)
        patch_sz = int(m.group(1)) if m else 0
        s["patch_sizes_all"].append(patch_sz)
        if hr.get("quota_blocked"):
            s["quota"] += 1; s["fail_modes"]["quota_blocked"] += 1
        elif cls == "resolved":
            s["resolved"] += 1; s["walls_res"].append(wall); s["patch_sizes_res"].append(patch_sz)
            s["repos"][e["repo"]]["resolved"] += 1
        elif cls == "patch-but-failed":
            s["pbf"] += 1; s["walls_fail"].append(wall); s["patch_sizes_fail"].append(patch_sz)
            ev = hr.get("eval", {})
            if patch_sz == 0: s["fail_modes"]["no_patch"] += 1
            elif not ev.get("patch_applied", False): s["fail_modes"]["patch_not_applied"] += 1
            elif ev.get("f2p_pass", 0) < ev.get("f2p_total", 1): s["fail_modes"]["f2p_fail"] += 1
            else: s["fail_modes"]["p2p_fail"] += 1
        else:
            s["fail_modes"]["other"] += 1; s["walls_fail"].append(wall); s["patch_sizes_fail"].append(patch_sz)
    stats[h] = s

print("\n" + "=" * 80)
print("PART 2: PER-HARNESS STATISTICS")
print("=" * 80)
print(f"\n{'Harness':<20s} {'Res':>4s} {'PBF':>4s} {'Rate':>6s} {'AvgWall':>8s} {'MedWall':>8s} {'AvgPatch':>9s}")
for h in ORDER:
    s = stats[h]
    rate = s["resolved"] / s["total"] * 100
    print(f"  {h:<20s} {s['resolved']:>4d} {s['pbf']:>4d} {rate:>5.1f}% {statistics.mean(s['walls_all']):>7.0f}s {statistics.median(s['walls_all']):>7.0f}s {statistics.mean(s['patch_sizes_all']):>8.0f}B")

print("\n--- Wall time: resolved vs failed ---")
for h in ORDER:
    s = stats[h]
    avg_res = statistics.mean(s["walls_res"]) if s["walls_res"] else 0
    avg_fail = statistics.mean(s["walls_fail"]) if s["walls_fail"] else 0
    print(f"  {h:20s} resolved_avg={avg_res:.0f}s  failed_avg={avg_fail:.0f}s  ratio={avg_fail/max(avg_res,1):.2f}x")

print("\n--- Failure mode distribution ---")
for h in ORDER:
    s = stats[h]; fm = s["fail_modes"]
    print(f"  {h:20s} no_patch={fm.get('no_patch',0)} patch_not_applied={fm.get('patch_not_applied',0)} f2p_fail={fm.get('f2p_fail',0)} p2p_fail={fm.get('p2p_fail',0)}")

print("\n" + "=" * 80)
print("PART 3: PATCH CHARACTERISTICS (from surviving predictions files)")
print("=" * 80)
for h in ORDER:
    entries = [e for e in subset if e["harness"] == h]
    files_touched = []; lines_added = []; lines_removed = []; patches_found = 0
    for e in entries:
        inst = e["instance_id"]; h_slug = h.replace("-", "_"); inst_slug = inst.replace("/", "__")
        fpath = WD / f"predictions_kimi_{h_slug}_{inst_slug}.json"
        if not fpath.exists(): fpath = WD / f"predictions_{h_slug}_{inst_slug}.json"
        if not fpath.exists(): continue
        try:
            pd = json.load(open(fpath))
            patch = (pd[0] if isinstance(pd, list) else pd).get("model_patch", "")
            if not patch: continue
            patches_found += 1
            diff_files = set(); added = 0; removed = 0
            for line in patch.split("\n"):
                if line.startswith("+++ "):
                    f = line[4:].strip()
                    if f != "/dev/null": diff_files.add(f.lstrip("b/"))
                elif line.startswith("+") and not line.startswith("+++"): added += 1
                elif line.startswith("-") and not line.startswith("---"): removed += 1
            files_touched.append(len(diff_files)); lines_added.append(added); lines_removed.append(removed)
        except: pass
    if files_touched:
        print(f"  {h:20s} patches={patches_found}/30 avg_files={statistics.mean(files_touched):.1f} avg_add={statistics.mean(lines_added):.1f} avg_del={statistics.mean(lines_removed):.1f}")
    else:
        print(f"  {h:20s} patches=0/30 (files gone)")

print("\n" + "=" * 80)
print("PART 4: INSTANCE-LEVEL ANALYSIS (why 20pp gap)")
print("=" * 80)
inst_results = defaultdict(dict)
for e in subset: inst_results[e["instance_id"]][e["harness"]] = (e.get("classification") == "resolved")
all_pass = [i for i, v in inst_results.items() if all(v.values())]
none_pass = [i for i, v in inst_results.items() if not any(v.values())]
some_pass = [i for i, v in inst_results.items() if any(v.values()) and not all(v.values())]
print(f"\n  ALL 7 resolved: {len(all_pass)}  NONE: {len(none_pass)}  SOME: {len(some_pass)}")
print("\n--- Nobody-solved ---")
for inst in sorted(none_pass): print(f"  {inst}")
res_sets = {h: set(i for i, c in inst_results.items() if c.get(h)) for h in ORDER}
print("\n--- Superset analysis (cline-patched vs others) ---")
for h in ORDER:
    if h == "cline-patched": continue
    cline_only = res_sets["cline-patched"] - res_sets[h]; h_only = res_sets[h] - res_sets["cline-patched"]
    print(f"  vs {h:20s}: cline_only={len(cline_only)} {h}_only={len(h_only)}")
print("\n--- Harness pair Jaccard ---")
for i, h1 in enumerate(ORDER):
    for h2 in ORDER[i+1:]:
        both = len(res_sets[h1] & res_sets[h2]); either = len(res_sets[h1] | res_sets[h2])
        print(f"  {h1:16s} vs {h2:16s}: both={both:2d} jaccard={both/either if either else 0:.3f}")
print("\n--- Timeout analysis (wall_s > 1700) ---")
for h in ORDER:
    entries = [e for e in subset if e["harness"] == h]
    timeouts = [e for e in entries if e.get("harness_result", {}).get("wall_s", 0) > 1700]
    print(f"  {h:20s} timeouts={len(timeouts)}/30")
print("\n--- Done ---")
