#!/usr/bin/env python3
"""Recompute per-task max_tools (tool_call counts) for the 40 subset tasks
from historical think_lang traces, for trajectory-length subgroup split.
Writes run/subset_toolcalls.json: {task_id: max_tools}
"""
import json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from build_compaction_subset import iter_task_messages, analyze_messages

TRACE_BASE = "/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang"
SUBSET = os.path.join(os.path.dirname(__file__), "compaction_subset_40.txt")
OUT = os.path.join(os.path.dirname(__file__), "subset_toolcalls.json")

subset = [l.strip() for l in open(SUBSET) if l.strip()]
subset_set = set(subset)

agg = defaultdict(lambda: {"max_tools": 0, "n_sessions": 0})
n = 0
for tid, path in iter_task_messages(TRACE_BASE):
    if tid not in subset_set:
        continue
    r = analyze_messages(path)
    if r is None:
        continue
    tools, nmsgs, clen, comp = r
    a = agg[tid]
    a["max_tools"] = max(a["max_tools"], tools)
    a["n_sessions"] += 1
    n += 1

out = {t: agg[t]["max_tools"] for t in subset}
with open(OUT, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

import statistics
vals = [out[t] for t in subset]
print(f"scanned sessions (subset only): {n}")
print(f"tasks found: {len([t for t in subset if out[t]>0])}/{len(subset)}")
print(f"max_tools: min={min(vals)} med={statistics.median(vals)} mean={statistics.mean(vals):.1f} max={max(vals)}")
# median split
med = statistics.median(vals)
short = [t for t in subset if out[t] < med]
long_ = [t for t in subset if out[t] >= med]
print(f"split at median={med}: short={len(short)} long={len(long_)}")
print(f"-> {OUT}")
