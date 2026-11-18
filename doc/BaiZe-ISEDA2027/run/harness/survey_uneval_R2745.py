#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Survey unevaluated real-patch predictions for incr_eval decision (R2745)."""
import json, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED = HERE / "predictions_glm53"
REP = HERE / "reports"
ROUTES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi", "opencode", "hermes"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek", "claude-code": "cc"}

def disp(h): return DISPLAY.get(h, h)

for h in ROUTES:
    cum = REP / f"eval_glm53_{h}.json"
    done = set()
    if cum.is_file():
        d = json.loads(cum.read_text())
        for k in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            v = d.get(k, [])
            done.update(v if isinstance(v, list) else [])
    preds = sorted(glob.glob(str(PRED / f"{h}__*.json")))
    real, empty = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{h}__", "").replace(".json", "")
        if iid in done:
            continue
        try:
            dd = json.loads(Path(p).read_text())
        except Exception:
            dd = []
        if isinstance(dd, dict):
            dd = [dd]
        patches = [x for x in dd if (x.get("model_patch") or "").strip()]
        if patches:
            real.append(iid)
        else:
            empty.append(iid)
    action = "EVAL" if len(real) >= 2 else ("merge-only" if empty else "skip")
    print(f"{disp(h)}: total={len(preds)} done={len(done)} real_new={len(real)} empty_new={len(empty)} -> {action}")
    if real:
        print(f"    real_new: {real}")
