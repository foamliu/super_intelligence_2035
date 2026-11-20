#!/usr/bin/env python3
"""Classify cline glm53 empty patches (C2 of 10:10 order)."""
import json, glob
from collections import Counter

PRED_DIR = "predictions_glm53"
PROG_FILE = "reports/progress_glm53_cline-patched.json"

# 1. Get empty instance_ids from predictions_glm53/
empty_ids = set()
for f in glob.glob(f"{PRED_DIR}/cline-patched__*.json"):
    d = json.load(open(f))
    item = d[0] if isinstance(d, list) else d
    patch = item.get("model_patch", "") or ""
    if not patch.strip():
        empty_ids.add(item["instance_id"])
print(f"glm53 empty patches: {len(empty_ids)}")

# 2. Look up in progress file
prog = json.load(open(PROG_FILE))
results = prog.get("results", prog) if isinstance(prog, dict) else prog
prog_map = {r["instance_id"]: r for r in results if "instance_id" in r}

# 3. Classify
classes = Counter()
samples = {}
wall_times = []
for iid in sorted(empty_ids):
    r = prog_map.get(iid, {})
    cls = r.get("classification", "not-in-progress")
    classes[cls] += 1
    wall = r.get("wall_s", 0)
    if wall:
        wall_times.append((iid, wall))
    if cls not in samples:
        samples[cls] = r

print(f"classifications: {dict(classes)}")
print(f"\nWall time distribution (no-patch only):")
no_patch_walls = [(iid, w) for iid, w in wall_times 
                  if prog_map.get(iid, {}).get("classification") == "no-patch"]
if no_patch_walls:
    walls = [w for _, w in no_patch_walls]
    print(f"  count={len(walls)} min={min(walls):.1f}s max={max(walls):.1f}s "
          f"mean={sum(walls)/len(walls):.1f}s median={sorted(walls)[len(walls)//2]:.1f}s")

# 4. Print samples with stdout/stderr tails
for cls, r in sorted(samples.items()):
    iid = r.get("instance_id", "?")
    wall = r.get("wall_s", "?")
    print(f"\n=== SAMPLE: {cls} === instance={iid} wall={wall}s")
    st = r.get("stdout_tail", "")
    se = r.get("stderr_tail", "")
    if st:
        print(f"  stdout_tail: ...{st[-400:]}")
    if se:
        print(f"  stderr_tail: ...{se[-400:]}")
    if not st and not se:
        print("  (no stdout/stderr tail captured)")

# 5. For no-patch: check if any stdout_tail contains error patterns
print("\n=== NO-PATCH error pattern scan ===")
error_patterns = Counter()
for iid in sorted(empty_ids):
    r = prog_map.get(iid, {})
    if r.get("classification") != "no-patch":
        continue
    st = r.get("stdout_tail", "")
    se = r.get("stderr_tail", "")
    combined = (st + " " + se).lower()
    if "429" in combined:
        error_patterns["429-quota"] += 1
    if "500" in combined or "503" in combined or "502" in combined:
        error_patterns["upstream-5xx"] += 1
    if "timeout" in combined or "timed out" in combined:
        error_patterns["timeout"] += 1
    if "forbidden" in combined or "403" in combined:
        error_patterns["forbidden-403"] += 1
    if "rate limit" in combined:
        error_patterns["rate-limit"] += 1
    if "api_key" in combined or "api key" in combined or "unauthorized" in combined or "401" in combined:
        error_patterns["auth-error"] += 1
    if "network" in combined or "connection" in combined or "econnrefused" in combined:
        error_patterns["network-error"] += 1
    if not combined.strip():
        error_patterns["no-output"] += 1
    if combined.strip() and not any(k in combined for k in ["429","500","503","502","timeout","forbidden","403","rate limit","api_key","api key","unauthorized","401","network","connection","econnrefused"]):
        error_patterns["other-output"] += 1

print(f"  pattern counts: {dict(error_patterns)}")
print(f"  total no-patch: {classes.get('no-patch', 0)}")
