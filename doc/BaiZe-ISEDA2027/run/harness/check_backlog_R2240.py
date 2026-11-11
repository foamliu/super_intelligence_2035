#!/usr/bin/env python3
"""Check eval backlog for R2240."""
import json, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}

total_real = 0
total_resolved = 0
total_eval = 0

for h in HARNESSES:
    ef = REPORT_DIR / f"eval_glm53_{h}.json"
    done = set()
    resolved = 0
    failed = 0
    infra = 0
    if ef.is_file():
        d = json.loads(ef.read_text())
        done = set(d.get("resolved", []) + d.get("failed", []) + d.get("infra_or_quota", []))
        resolved = len(d.get("resolved", []))
        failed = len(d.get("failed", []))
        infra = len(d.get("infra_or_quota", []))

    all_preds = sorted(glob.glob(str(PRED_DIR / f"{h}__*.json")))
    n_files = len(all_preds)
    n_real = 0
    n_empty = 0
    backlog = []
    for f in all_preds:
        iid = os.path.basename(f).replace(f"{h}__", "").replace(".json", "")
        pd = json.loads(Path(f).read_text())
        if isinstance(pd, dict):
            pd = [pd]
        has_real = any((p.get("model_patch") or "").strip() for p in pd)
        if has_real:
            n_real += 1
            if iid not in done:
                backlog.append(iid)
        else:
            n_empty += 1

    total_real += n_real
    total_eval += (resolved + failed + infra)
    total_resolved += resolved
    bl_str = f" backlog={len(backlog)} {backlog[:5]}" if backlog else " backlog=0"
    print(f"{DISPLAY.get(h,h):12s}: files={n_files} real={n_real} empty={n_empty} | "
          f"resolved={resolved} failed={failed} infra={infra}{bl_str}")

print(f"\nTOTAL: real={total_real} resolved={total_resolved} evaluated={total_eval}")
