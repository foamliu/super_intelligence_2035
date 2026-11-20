#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge incr_eval_R2126 report.json results into eval_glm53_{h}.json.

Why: incr_eval_R2126.sh (shell wrapper) runs swebench eval and then calls
regen_eval_summaries.py — but regen writes to kimi-era eval_{h}.json (using
predictions/ + kimi model map), NOT eval_glm53_{h}.json.  So the glm53 summary
files (consumed by gen_report_glm53_7way.py) stay stale.  This script performs
the glm53-specific merge that the python template (incr_eval_glm53_R2124.py)
normally does, WITHOUT re-running docker eval (reuses the report.json already
produced by R2126).

Reusable: re-run anytime after an incr_eval_RXXXX.sh shell-wrapper run.
"""
from __future__ import annotations
import json, glob, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
REPORT_DIR = HERE / "reports"
PRED_DIR = HERE / "predictions_glm53"
ROUND = "R2126"

ALL_H = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
MODEL_SUFFIX = "glm-5.3-flash"


def classify_one(report_path: Path, iid: str) -> str:
    if not report_path.exists():
        return "infra"
    try:
        rep = json.loads(report_path.read_text())
    except Exception:
        return "infra"
    inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
    if not isinstance(inst, dict):
        return "infra"
    if inst.get("infra_failure", False):
        return "infra"
    if inst.get("patch_is_None", False) or not inst.get("patch_exists", True):
        return "infra"
    return "resolved" if inst.get("resolved", False) else "failed"


def disp(h):
    return DISPLAY.get(h, h)


for h in ALL_H:
    eval_file = REPORT_DIR / f"eval_glm53_{h}.json"
    run_id = f"verified_full_glm53_{h}_incr_{ROUND}"
    run_dir = EVAL_LOG_ROOT / run_id
    if not run_dir.is_dir():
        print(f"  {disp(h)}: no {ROUND} incr run dir, skip")
        continue

    # Load existing summary
    existing = {"resolved": [], "failed": [], "infra_or_quota": []}
    if eval_file.is_file():
        try:
            existing = json.loads(eval_file.read_text())
        except Exception:
            pass
    resolved = list(existing.get("resolved", []))
    failed = list(existing.get("failed", []))
    infra = list(existing.get("infra_or_quota", []))
    already = set(resolved + failed + infra)

    # Count real predictions (for total_predictions field)
    real_pred = 0
    for pf in glob.glob(str(PRED_DIR / f"{h}__*.json")):
        try:
            d = json.loads(open(pf).read())
            if isinstance(d, list):
                d = d[0] if d else {}
            if d.get("model_patch", "").strip():
                real_pred += 1
        except Exception:
            pass

    # Scan R2126 report.json files
    model_dir_name = f"{disp(h)}-{MODEL_SUFFIX}" if h != "cline-patched" else f"cline-{MODEL_SUFFIX}"
    # actual model dir: cline-glm-5.3-flash, opencode-glm-5.3-flash, etc.
    candidates = [p for p in run_dir.iterdir() if p.is_dir()]
    model_dir = run_dir / model_dir_name
    if not model_dir.exists() and candidates:
        model_dir = candidates[0]
    n_new = 0
    n_resolved_new = 0
    for iid_dir in sorted(model_dir.iterdir()) if model_dir.exists() else []:
        if not iid_dir.is_dir():
            continue
        iid = iid_dir.name
        rj = iid_dir / "report.json"
        cls = classify_one(rj, iid)
        if iid in already:
            continue
        n_new += 1
        if cls == "resolved":
            resolved.append(iid)
            n_resolved_new += 1
        elif cls == "failed":
            failed.append(iid)
        else:
            infra.append(iid)

    rc = len(resolved)
    n = rc + len(failed) + len(infra)
    no_patch = existing.get("no_patch", [])
    summary = {
        "harness": disp(h), "harness_code": h, "run_id": run_id,
        "n": n, "resolved": sorted(resolved), "failed": sorted(failed),
        "infra_or_quota": sorted(infra), "no_patch": no_patch,
        "total_predictions": real_pred, "evaluated": n, "resolved_count": rc,
    }
    eval_file.write_text(json.dumps(summary, indent=2))
    print(f"  {disp(h)}: merged {n_new} NEW ({n_resolved_new} resolved) -> "
          f"n={n} resolved={rc} failed={len(failed)} infra={len(infra)} "
          f"total_pred={real_pred}")

print(f"\nmerge_{ROUND} done.")
