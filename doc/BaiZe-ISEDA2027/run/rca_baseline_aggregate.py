#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggregate step105 baseline (5-run) EDA-Eval-PyAether data into one JSON for RCA report."""
import json, os, glob, collections, re, sys
from datetime import datetime

BASE = "/tmp/posttrain_5run_eval/step105"
BENCH = "/home/app.e0031982/code/EDA-Eval-Framework/benchmarks/v20260602/EDA-Eval-PyAether-v20260311_fixed.jsonl"
EVAL_DIR = os.path.expanduser("~/eda_code_eval")

def iso_to_dt(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

# ---- benchmark metadata ----
meta = {}
for line in open(BENCH):
    r = json.loads(line)
    m = r["metadata"]
    meta[r["task_id"]] = {
        "task_name": m.get("task_name", ""),
        "scenario": m.get("scenario", "?"),
        "category": m.get("category", "?"),
        "apis_used": m.get("apis_used", []),
        "source": m.get("source", ""),
        "lines_of_code": m.get("lines_of_code", 0),
        "entry_point": r.get("entry_point", ""),
    }

# batch id per run from generations_file
run_batch = {}
for i in range(1, 6):
    fr = json.load(open(f"{BASE}/run{i}/final_report.json"))
    gf = fr["generations_file"]
    bm = re.search(r"(\d{8}_\d{6})", gf)
    run_batch[i] = bm.group(1) if bm else None

print("run_batch:", run_batch, file=sys.stderr)

# ---- aggregate final_report per run ----
runs = {}
for i in range(1, 6):
    fr = json.load(open(f"{BASE}/run{i}/final_report.json"))
    det = fr["details_per_task"]
    gen = json.load(open(f"{BASE}/run{i}/result_summary.json")) if os.path.exists(f"{BASE}/run{i}/result_summary.json") else {}
    runs[i] = {
        "pass_rate": fr["metrics"]["pass_rate"],
        "summary": fr["summary"],
        "details": det,
        "result_summary": gen,
        "batch_id": run_batch[i],
    }

# per-task aggregation across 5 runs
tasks = {}
all_ids = sorted(meta.keys())
for tid in all_ids:
    m = meta[tid]
    rec = {
        "task_id": tid, "task_name": m["task_name"], "scenario": m["scenario"],
        "category": m["category"], "entry_point": m["entry_point"],
        "apis_used": m["apis_used"], "source": m["source"], "lines_of_code": m["lines_of_code"],
        "runs": [], "pass_count": 0, "pass_rate": 0.0,
    }
    for i in range(1, 6):
        d = runs[i]["details"].get(tid, {})
        gs = d.get("generation_statuses", ["?"])
        xs = d.get("execution_statuses", ["?"])
        et = d.get("error_types", ["?"])
        passed = d.get("num_correct", 0) > 0
        rec["runs"].append({
            "run": i, "gen": gs[0] if gs else "?", "exec": xs[0] if xs else "?",
            "error_types": et, "passed": passed,
            "batch_id": runs[i]["batch_id"],
        })
        if passed:
            rec["pass_count"] += 1
    rec["pass_rate"] = rec["pass_count"] / 5.0
    tasks[tid] = rec

# overall pass stats
pass_per_run = [runs[i]["pass_rate"] for i in range(1, 6)]
import statistics
mean = statistics.mean(pass_per_run); std = statistics.stdev(pass_per_run)
print(f"per-run pass_rate: {pass_per_run}", file=sys.stderr)
print(f"mean={mean:.4f} std={std:.4f}", file=sys.stderr)

# tasks passing in at least 1 run, and union
union_pass = [t for t, r in tasks.items() if r["pass_count"] > 0]
print(f"union pass (>=1 run): {len(union_pass)}", file=sys.stderr)
print(sorted(union_pass), file=sys.stderr)

out = {
    "mean": mean, "std": std, "mean_pm_std": f"{mean*100:.2f}%+/-{std*100:.2f}%",
    "pass_per_run": pass_per_run,
    "pass_per_run_count": [round(r*158) for r in pass_per_run],
    "tasks": tasks,
    "scenarios": dict(collections.Counter(meta[t]["scenario"] for t in meta)),
    "categories": dict(collections.Counter(meta[t]["category"] for t in meta)),
}
json.dump(out, open("/tmp/rca_baseline_data.json", "w"), ensure_ascii=False, indent=1)
print("WROTE /tmp/rca_baseline_data.json", file=sys.stderr)
