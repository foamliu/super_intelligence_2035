#!/usr/bin/env python3
"""merge_R2146_glm53.py — merge R2146 incr eval results into eval_glm53_<h>.json.

The eval was already run by incr_eval_R2146.sh (5 new instances across 2 routes).
This script only does the parse_and_merge step (no re-eval):
  - reads report.json from each R2146 run_id dir
  - classifies resolved/failed
  - merges into eval_glm53_<h>.json (avoiding dups)

Run: python3 merge_R2146_glm53.py
"""
import json, os, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
MODEL_SUFFIX = "glm-5.3-flash"
ROUND = "R2146"

DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
def disp(h): return DISPLAY.get(h, h)

# Only the 2 routes that had new eval; others had 0 new.
NEW_IDS = {
    "opencode": ["pytest-dev__pytest-10051", "pytest-dev__pytest-10081"],
    "hermes": ["django__django-16661", "django__django-16877", "django__django-17087"],
}

def log(msg): print(f"[merge-R2146 {time.strftime('%H:%M:%S')}] {msg}", flush=True)

def parse_and_merge(harness, new_ids, run_id):
    model = f"{disp(harness)}-{MODEL_SUFFIX}"
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    summary = json.loads(ef.read_text()) if ef.exists() else {
        "harness": disp(harness), "harness_code": harness, "run_id": run_id,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": [], "no_patch": 0}
    new_res, new_fail, new_infra = [], [], []
    for iid in new_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            new_infra.append(iid); continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (new_res if resolved else new_fail).append(iid)
        except Exception as e:
            new_infra.append(f"{iid}({e})")
    for lst_name in ("resolved", "failed", "infra_or_quota"):
        summary.setdefault(lst_name, [])
    existing = set(summary["resolved"] + summary["failed"] + summary["infra_or_quota"])
    for iid in new_res:
        if iid not in existing: summary["resolved"].append(iid)
    for iid in new_fail:
        if iid not in existing: summary["failed"].append(iid)
    for iid in new_infra:
        if iid not in existing: summary["infra_or_quota"].append(iid)
    summary["n"] = len(summary["resolved"]) + len(summary["failed"])
    summary["evaluated"] = summary["n"]
    summary["resolved_count"] = len(summary["resolved"])
    summary["total_predictions"] = summary["n"] + len(summary["infra_or_quota"])
    summary["run_id"] = run_id
    ef.write_text(json.dumps(summary, indent=2))
    log(f"  {disp(harness)}: +{len(new_res)} resolved +{len(new_fail)} failed +{len(new_infra)} infra => total resolved={len(summary['resolved'])}")
    return len(new_res), len(new_fail), len(new_infra)

def main():
    total_new_res = 0
    for harness, ids in NEW_IDS.items():
        run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
        nr, nf, ni = parse_and_merge(harness, ids, run_id)
        total_new_res += nr
    log(f"DONE R2146 merge: total new resolved = {total_new_res}")

if __name__ == "__main__":
    main()
