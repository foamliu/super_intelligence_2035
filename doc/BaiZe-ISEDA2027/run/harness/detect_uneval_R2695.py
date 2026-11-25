#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detect unevaluated real-patch predictions across all routes (R2695)."""
import json, glob, os
from pathlib import Path
HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED = HERE / "predictions_glm53"
REP = HERE / "reports"
ROUTES = ["cline-patched", "hermes", "claude-code", "codex", "pi", "opencode", "deepseek-harness"]

def load_pred(f):
    try:
        d = json.loads(f.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]

total_real = 0
for h in ROUTES:
    done = set()
    cf = REP / f"eval_glm53_{h}.json"
    if cf.is_file():
        d = json.loads(cf.read_text())
        for k in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            v = d.get(k, [])
            if isinstance(v, list):
                done.update(v)
    preds = sorted(glob.glob(str(PRED / f"{h}__*.json")))
    real, empty = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{h}__", "").replace(".json", "")
        if iid in done:
            continue
        if load_pred(Path(p)):
            real.append(iid)
        else:
            empty.append(iid)
    total_real += len(real)
    res = len(json.loads(cf.read_text())["resolved"]) if cf.is_file() and "resolved" in json.loads(cf.read_text()) else 0
    print(f"{h}: pred_total={len(preds)} done={len(done)} resolved={res} uneval_real={len(real)} uneval_empty={len(empty)}")
    if real[:10]:
        print("   real:", real[:10])
print(f"TOTAL uneval_real across routes = {total_real}")
