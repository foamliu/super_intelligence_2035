#!/usr/bin/env python3
"""158-task per-task peak-context analysis for H_ctx testability.

Goal: on the full 158 PyAether task set, measure per-task peak inputTokens
(context demand) to find tasks that approach/exceed the 128K model window.
These top-k tasks form the candidate subset for testing H_ctx (the hypothesis
that multi-agent beats single-agent when required context > window).

Source: A_none_r1/r2/r3 (glm-5.2, no-thinking, 158 tasks, cline 3.0.51) — the
cleanest baseline closest to the subagent A0 setup.

Method:
  - Each cline worker session processes multiple tasks sequentially; context
    resets (inputTokens drops >50%) mark a new task.
  - For each segment, peak inputTokens = max over assistant turns.
  - Task ID matched by function name in the segment's first user message
    against full_tasks/*.md function signatures.
"""
import json, glob, re, os
from pathlib import Path
from statistics import mean, median, stdev

BASE = Path("/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang")
ROUNDS = ["A_none_r1", "A_none_r2", "A_none_r3"]
BATCH_DIR_NAME = "2026_1107_083036"  # r1 batch; r2/r3 have own batch dirs

# --- 1. build task_id -> func_name map from full_tasks ---
def build_task_map(batch_dir):
    tm = {}
    for md in sorted(glob.glob(str(batch_dir / "full_tasks" / "*.md"))):
        tid = Path(md).stem  # EDA-Eval-PyAether-001
        txt = open(md, encoding="utf-8", errors="ignore").read()
        m = re.search(r"^\s*def\s+(\w+)\s*\(", txt, re.M)
        fn = m.group(1) if m else ""
        tm[tid] = fn
    return tm

# --- 2. per-session segmentation ---
def text_of(content):
    if isinstance(content, list):
        parts = []
        for x in content:
            if isinstance(x, dict):
                parts.append(str(x.get("text", x.get("content", ""))))
            else:
                parts.append(str(x))
        return " ".join(parts)
    return str(content or "")

def segments_of(msgs):
    """Yield (seg_first_user_text, peak_inputTokens, n_assistant_turns)."""
    asst_its = []
    seg_start_user = None
    cur_peak = 0
    cur_n = 0
    prev_it = None
    segs = []
    for m in msgs:
        role = m.get("role")
        if role == "user" and seg_start_user is None:
            seg_start_user = text_of(m.get("content", ""))
        if role == "assistant" and "metrics" in m:
            it = m["metrics"].get("inputTokens", 0)
            # detect reset: drop >50% from prev peak (new task)
            if prev_it is not None and cur_peak > 0 and it < cur_peak * 0.5:
                segs.append((seg_start_user or "", cur_peak, cur_n))
                seg_start_user = None
                # this assistant turn belongs to NEW seg; capture the user msg
                # that preceded it (look back)
                cur_peak = it
                cur_n = 1
            else:
                cur_peak = max(cur_peak, it)
                cur_n += 1
            prev_it = it
    if cur_n > 0:
        segs.append((seg_start_user or "", cur_peak, cur_n))
    return segs

def match_task(user_text, task_map, fn_index):
    # extract function name from the user message (the task prompt ends with def foo(...))
    m = re.search(r"\bdef\s+(\w+)\s*\(", user_text)
    if m:
        fn = m.group(1)
        return fn_index.get(fn, "?")
    # fallback: match by longest distinctive substring
    return "?"

def dist_stats(peaks):
    if not peaks:
        return {}
    s = sorted(peaks)
    n = len(s)
    def pct(p):
        return s[min(n - 1, int(n * p / 100))]
    return {
        "n": n, "min": s[0], "max": s[-1],
        "mean": round(mean(s), 1), "median": median(s),
        "p90": pct(90), "p95": pct(95), "p99": pct(99),
        "n_gt_80k": sum(1 for x in s if x > 80000),
        "n_gt_100k": sum(1 for x in s if x > 100000),
        "n_gt_110k": sum(1 for x in s if x > 110000),
        "n_gt_120k": sum(1 for x in s if x > 120000),
        "n_gt_128k": sum(1 for x in s if x > 128000),
    }

# --- main ---
all_records = []  # (round, task_id, peak, n_turns)
per_round = {}

for rnd in ROUNDS:
    rdir = BASE / rnd
    if not rdir.is_dir():
        print(f"SKIP {rnd}: not found", flush=True)
        continue
    # find batch dirs (formats: 2026_1107_HHMMSS or 20261107_HHMMSS_user)
    batch_dirs = [d for d in rdir.iterdir() if d.is_dir() and re.match(r"2026[_0-9]", d.name)]
    if not batch_dirs:
        continue
    # use first batch dir that has full_tasks/ for the task map; process all
    bdir = batch_dirs[0]
    for bd in batch_dirs:
        if (bd / "full_tasks").is_dir():
            bdir = bd
            break
    task_map = build_task_map(bdir)
    fn_index = {fn: tid for tid, fn in task_map.items() if fn}
    n_sessions = 0
    n_segs = 0
    for bdir2 in batch_dirs:
      for mj in bdir2.rglob("*.messages.json"):
        if mj.name.startswith("agent_"):
            continue
        try:
            d = json.load(open(mj))
        except Exception:
            continue
        msgs = d.get("messages", []) if isinstance(d, dict) else d
        if not msgs:
            continue
        n_sessions += 1
        for user_text, peak, nturns in segments_of(msgs):
            if peak < 5000:  # skip tiny/degenerate
                continue
            tid = match_task(user_text, task_map, fn_index)
            all_records.append((rnd, tid, peak, nturns))
            n_segs += 1
    per_round[rnd] = {"n_sessions": n_sessions, "n_segs": n_segs, "n_tasks_mapped": len(set(r[1] for r in all_records if r[0] == rnd))}

# --- output ---
print("=== per-round ===")
for rnd, info in per_round.items():
    print(f"  {rnd}: sessions={info['n_sessions']} segs={info['n_segs']} tasks_mapped={info['n_tasks_mapped']}")

all_peaks = [r[2] for r in all_records]
print("\n=== pooled per-task-segment peak context (n=%d) ===" % len(all_peaks))
ds = dist_stats(all_peaks)
for k, v in ds.items():
    print(f"  {k}: {v}")

# per-task max across rounds
per_task_max = {}
for rnd, tid, peak, nt in all_records:
    if tid not in per_task_max or peak > per_task_max[tid][0]:
        per_task_max[tid] = (peak, rnd, nt)

print("\n=== per-task MAX peak (across 3 rounds), top 25 ===")
ranked = sorted(per_task_max.items(), key=lambda x: -x[1][0])
print(f"  {'task_id':<28} {'peak':>8} {'round':<12} {'n_turns':>8}")
for tid, (pk, rnd, nt) in ranked[:25]:
    print(f"  {tid:<28} {pk:>8} {rnd:<12} {nt:>8}")

print("\n=== top-25 tasks (for H_ctx subset) ===")
top25 = [tid for tid, _ in ranked[:25]]
print("  " + ",".join(top25))

# how many tasks > 100K (ever, across rounds)
gt100 = [tid for tid, (pk, _, _) in per_task_max.items() if pk > 100000]
gt110 = [tid for tid, (pk, _, _) in per_task_max.items() if pk > 110000]
gt120 = [tid for tid, (pk, _, _) in per_task_max.items() if pk > 120000]
print(f"\n=== tasks ever >100K: {len(gt100)}  >110K: {len(gt110)}  >120K: {len(gt120)} ===")

# save full result
out = {
    "pooled_stats": ds,
    "per_round": per_round,
    "per_task_max": {tid: {"peak": pk, "round": rnd, "n_turns": nt} for tid, (pk, rnd, nt) in per_task_max.items()},
    "top25_task_ids": top25,
    "tasks_gt100k": gt100,
    "tasks_gt110k": gt110,
    "tasks_gt120k": gt120,
    "all_records_n": len(all_records),
}
json.dump(out, open("/tmp/ctx_topk_158.json", "w"), ensure_ascii=False, indent=2)
print("\n=== saved /tmp/ctx_topk_158.json ===")
