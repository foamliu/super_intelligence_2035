#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental eval merge for R2710 (monitoring round).
0 new real-patch across all 5 active routes -> no docker eval needed.
11 new empty-patch predictions merged into failed/empty_patch buckets:
  cline-patched: 1 empty | codex: 4 empty | claude-code: 5 empty
  deepseek-harness: 1 empty | pi: 0
EVAL_LOG_ROOT = logs/evaluation (R2708 fix applied).
"""
from __future__ import annotations
import json, time, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
ROUND = "R2710"
ROUTES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi"]

def log(m):
    print(f"[incr-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)

def load_pred(iid_file):
    try:
        d = json.loads(iid_file.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]

def get_unevaluated(harness):
    cum_file = REPORT_DIR / f"eval_glm53_{harness}.json"
    done = set()
    if cum_file.is_file():
        d = json.loads(cum_file.read_text())
        for field in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            val = d.get(field, [])
            if isinstance(val, list):
                done.update(val)
    preds = sorted(glob.glob(str(PRED_DIR / f"{harness}__*.json")))
    real_new, empty_new = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{harness}__", "").replace(".json", "")
        if iid in done:
            continue
        if load_pred(Path(p)):
            real_new.append(iid)
        else:
            empty_new.append(iid)
    return real_new, empty_new, done

def merge_empties(harness, empty_ids):
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    cum = json.loads(ef.read_text()) if ef.is_file() else {
        "harness": harness, "harness_code": harness, "run_id": ROUND,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": [],
        "empty_patch": []}
    cum.setdefault("resolved", [])
    cum.setdefault("failed", [])
    cum.setdefault("infra_or_quota", [])
    cum.setdefault("empty_patch", [])
    merged = 0
    for iid in empty_ids:
        if iid not in cum["failed"] and iid not in cum["resolved"]:
            cum["empty_patch"].append(iid)
            cum["failed"].append(iid)
            merged += 1
            log(f"  {iid}: EMPTY PATCH -> failed")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    log(f"{harness}: n={cum['n']} resolved={len(cum['resolved'])} "
        f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} "
        f"empty_patch={len(cum.get('empty_patch', []))} (merged {merged} empty)")
    return cum

if __name__ == "__main__":
    log(f"Starting incr_eval_all {ROUND} (merge-only, 0 real-patch)")
    summary = {}
    for h in ROUTES:
        log(f"--- {h} ---")
        real_new, empty_new, done = get_unevaluated(h)
        log(f"{h}: unevaluated real_patch={len(real_new)} empty_patch={len(empty_new)}")
        if not real_new and not empty_new:
            log(f"{h}: nothing to do")
            continue
        if real_new:
            log(f"ERROR: {h} has {len(real_new)} real-patch but this script is merge-only!")
            continue
        result = merge_empties(h, empty_new)
        summary[h] = {
            "resolved": len(result["resolved"]),
            "failed": len(result["failed"]),
            "infra": len(result["infra_or_quota"]),
            "n": result["n"],
            "new_empty_merged": len(empty_new),
        }
    log("=== SUMMARY ===")
    for h, s in summary.items():
        log(f"{h}: resolved={s['resolved']} failed={s['failed']} infra={s['infra']} "
            f"n={s['n']} (new_empty_merged={s['new_empty_merged']})")
    log("DONE")
