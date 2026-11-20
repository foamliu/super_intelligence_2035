#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Survey unevaluated real/empty patches per route (R2723). Cheap file reads only.
Decision rule: total real_new >= 2 -> incr_eval round; else merge-empties if empty_new>0.
"""
from __future__ import annotations
import json, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
ROUTES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi", "opencode", "hermes"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek", "claude-code": "cc"}


def disp(h): return DISPLAY.get(h, h)


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


if __name__ == "__main__":
    total_real = 0
    total_empty = 0
    print(f"=== R2723 pending survey ===")
    for h in ROUTES:
        real_new, empty_new, done = get_unevaluated(h)
        total_real += len(real_new)
        total_empty += len(empty_new)
        n_pred = len(glob.glob(str(PRED_DIR / f"{h}__*.json")))
        # current resolved count
        cum_file = REPORT_DIR / f"eval_glm53_{h}.json"
        resolved = 0
        if cum_file.is_file():
            cd = json.loads(cum_file.read_text())
            resolved = len(cd.get("resolved", []))
        flag = "EVAL" if real_new else ("MERGE" if empty_new else "skip")
        print(f"{disp(h):10s}: pred={n_pred:3d} done={len(done):3d} resolved={resolved:3d} "
              f"real_new={len(real_new):2d} empty_new={len(empty_new):2d} -> {flag}")
        if real_new:
            print(f"             real_new: {real_new}")
    print(f"--- TOTAL real_new={total_real} empty_new={total_empty} ---")
    if total_real >= 2:
        print("DECISION: incr_eval round (real_new >= 2)")
    elif total_empty > 0:
        print("DECISION: merge-empties round (real_new < 2, empty_new > 0)")
    else:
        print("DECISION: pure monitoring round (nothing pending)")
