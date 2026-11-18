#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix R2701 incr_eval mis-parse: swebench v5.0.2 writes per-instance report.json
under logs/evaluation/<run_id>/<model>/<iid>/report.json, but incr_eval_all_R2701
looked in logs/run_evaluation/ (wrong) -> all 5 marked infra.

Authoritative source: logs/evaluation/<run_id>/results.json (resolved_ids /
unresolved_ids). Re-merge correctly into cumulative eval_glm53_<h>.json.
"""
import json
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
EVAL_DIR = HERE / "logs" / "evaluation"
REP = HERE / "reports"

# (harness, run_id, model_subdir)
RUNS = [
    ("cline-patched", "verified_full_glm53_cline-patched_incr_R2701", "cline-glm-5.3-flash"),
    ("pi", "verified_full_glm53_pi_incr_R2701", "pi-glm-5.3-flash"),
]

for harness, run_id, model_sub in RUNS:
    results_f = EVAL_DIR / run_id / "results.json"
    res = json.loads(results_f.read_text())
    resolved_ids = set(res.get("resolved_ids", []))
    unresolved_ids = set(res.get("unresolved_ids", []))
    all_ids = sorted(resolved_ids | unresolved_ids)
    print(f"--- {harness} ({run_id}) ---")
    print(f"  results.json: resolved={len(resolved_ids)} unresolved={len(unresolved_ids)} ids={all_ids}")

    cf = REP / f"eval_glm53_{harness}.json"
    cum = json.loads(cf.read_text())
    for k in ("resolved", "failed", "infra_or_quota", "empty_patch", "no_patch"):
        if not isinstance(cum.get(k), list):
            cum[k] = []

    # Remove the R2701 ids from whichever bucket the broken parse put them (infra_or_quota),
    # then re-place according to results.json.
    moved = []
    for iid in all_ids:
        for bucket in ("infra_or_quota", "failed", "resolved", "empty_patch", "no_patch"):
            if iid in cum[bucket]:
                cum[bucket].remove(iid)
                moved.append((iid, bucket))
    print(f"  removed from buckets: {moved}")

    for iid in all_ids:
        if iid in resolved_ids:
            if iid not in cum["resolved"]:
                cum["resolved"].append(iid)
            print(f"  {iid}: -> resolved")
        else:
            if iid not in cum["failed"]:
                cum["failed"].append(iid)
            print(f"  {iid}: -> failed")

    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    cf.write_text(json.dumps(cum, indent=2))
    print(f"  CUMULATIVE {harness}: n={cum['n']} resolved={len(cum['resolved'])} "
          f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} "
          f"empty_patch={len(cum.get('empty_patch', []))}")

print("FIX DONE")
