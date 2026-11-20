#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2731 survey: count real_new / empty_new per route (no modification)."""
import json, glob, os
from pathlib import Path

PRED = Path("swebench_verified_full/predictions_glm53")
REP = Path("swebench_verified_full/reports")
ROUTES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi", "opencode", "hermes"]
DISP = {"cline-patched": "cline", "deepseek-harness": "deepseek", "claude-code": "cc"}


def lp(f):
    try:
        d = json.loads(f.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]


total_real = 0
for h in ROUTES:
    cum = REP / f"eval_glm53_{h}.json"
    done = set()
    r = 0
    if cum.is_file():
        d = json.loads(cum.read_text())
        for k in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            v = d.get(k, [])
            if isinstance(v, list):
                done.update(v)
        rv = d.get("resolved", [])
        r = len(rv) if isinstance(rv, list) else rv
    preds = sorted(glob.glob(str(PRED / f"{h}__*.json")))
    rn, en = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{h}__", "").replace(".json", "")
        if iid in done:
            continue
        (rn if lp(Path(p)) else en).append(iid)
    total_real += len(rn)
    print(f"{DISP.get(h,h):10s} resolved={r} pred={len(preds)} real_new={len(rn)} empty_new={len(en)} {rn if rn else ''}")
print(f"TOTAL real_new={total_real} (threshold=2 -> {'EVAL' if total_real>=2 else 'no eval'})")