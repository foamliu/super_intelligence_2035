#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2718 monitoring round: merge unevaluated empty patches into failed.

real_new total = 0 < 2 threshold -> NO eval.
Only merge empty_new into failed for bookkeeping accuracy.
(detect_uneval_R2695.py survey: cline1/cc3/codex3/pi1 = 8 empties, real_new=0)
"""
from __future__ import annotations
import json, glob, os, time
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
ROUTES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi", "opencode", "hermes"]
REAL_THRESHOLD = 2

def log(m): print(f"[incr-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)

def load_pred(f):
    try: d = json.loads(f.read_text())
    except: return []
    if isinstance(d, dict): d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]

def get_unevaluated(h):
    cum = REPORT_DIR / f"eval_glm53_{h}.json"
    done = set()
    if cum.is_file():
        d = json.loads(cum.read_text())
        for fld in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            v = d.get(fld, [])
            if isinstance(v, list): done.update(v)
    preds = sorted(glob.glob(str(PRED_DIR / f"{h}__*.json")))
    real_new, empty_new = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{h}__", "").replace(".json", "")
        if iid in done: continue
        if load_pred(Path(p)): real_new.append(iid)
        else: empty_new.append(iid)
    return real_new, empty_new, done

def merge_empties(h, empty_ids):
    ef = REPORT_DIR / f"eval_glm53_{h}.json"
    cum = json.loads(ef.read_text()) if ef.is_file() else {"harness": h, "resolved": [], "failed": [], "infra_or_quota": [], "empty_patch": []}
    for k in ["resolved", "failed", "infra_or_quota", "empty_patch"]: cum.setdefault(k, [])
    merged = 0
    for iid in empty_ids:
        if iid not in cum["failed"] and iid not in cum["resolved"]:
            cum["empty_patch"].append(iid); cum["failed"].append(iid); merged += 1
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    cum["evaluated"] = cum["n"]
    cum["total_predictions"] = len(glob.glob(str(PRED_DIR / f"{h}__*.json")))
    ef.write_text(json.dumps(cum, indent=2))
    return merged, len(cum["resolved"]), cum["n"]

if __name__ == "__main__":
    log(f"R2718 monitoring: survey + merge empties (threshold={REAL_THRESHOLD})")
    survey = {h: get_unevaluated(h) for h in ROUTES}
    total_real = sum(len(survey[h][0]) for h in ROUTES)
    log(f"TOTAL real_new={total_real} (threshold={REAL_THRESHOLD}) -> {'EVAL' if total_real >= REAL_THRESHOLD else 'NO EVAL (merge empties only)'}")
    for h in ROUTES:
        real_new, empty_new, done = survey[h]
        if not real_new and not empty_new:
            log(f"{h}: nothing to do"); continue
        merged, resolved, n = merge_empties(h, empty_new)
        log(f"{h}: real_new={len(real_new)} (pending) empty_merged={merged} -> resolved={resolved} n={n}")
    log("DONE")
