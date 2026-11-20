#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1597: incr_eval for 2 GENUINE deepseek-harness backlog items.
  matplotlib__matplotlib-25287  (patchlen=2815, R1594 eval -> infra, no report.json)
  matplotlib__matplotlib-26291  (patchlen=647,  predict completed 21:21, never eval'd)

The 4 cline-patched items in scan_backlog (astropy-7336, django-11087,
django-14725, django-15098) are FALSE positives: they were already eval'd in
rerun_R1592/R1594 dirs (all resolved=False -> FAILED) but regen_eval_summaries.py
only scanned the main run dir, misclassifying them as infra.  R1597 fixes
regen_eval_summaries.py to scan ALL verified_full_<h>* dirs, so those 4 are
corrected to `failed` by the regen step below (no re-eval needed).

Discipline: does NOT interrupt running predicts (cline django-16263, codex,
deepseek matplotlib-26342).  Docker eval runs in separate containers.
"""
import json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
LOG_DIR = HERE / "logs"
ENRICHED = HERE / "enriched_500.json"
TIMEOUT_EVAL = 1800
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"

# Genuine backlog to eval (completed predicts with a real patch, NO report.json
# in ANY run dir for that harness).  Verified at 21:33.
#   - cline-patched: django-16429 (rerun, mtime 21:27), django-16527 (rerun, mtime 21:31).
#     django-16263 is STILL being predicted (process alive) -> skipped this round.
#     The 4 older cline items (astropy-7336, django-11087/14725/15098) were already
#     eval'd in rerun_R1592/R1594 dirs (all FAILED) and are correctly classified by
#     the fixed regen -> no re-eval needed.
#   - deepseek-harness: matplotlib-25287 (R1594 eval -> infra, retry), matplotlib-26291
#     (predict completed 21:21, never eval'd).
CONFIGS = [
    {"harness": "cline-patched", "model": "cline-kimi-k2.6-cloud",
     "run_id": "verified_full_cline-patched_rerun_R1597",
     "ids": ["django__django-16429", "django__django-16527"]},
    {"harness": "deepseek-harness", "model": "deepseek-harness-kimi-k2.6-cloud",
     "run_id": "verified_full_deepseek-harness_rerun_R1597",
     "ids": ["matplotlib__matplotlib-25287", "matplotlib__matplotlib-26291"]},
]


def log(m):
    print(f"[R1597 {time.strftime('%H:%M:%S')}] {m}", flush=True)


def merge_predictions(harness):
    all_preds = []
    for f in sorted(PRED_DIR.glob(f"{harness}__*.json")):
        if f.stat().st_size < 30:
            continue
        try:
            preds = json.loads(f.read_text())
            if isinstance(preds, dict):
                preds = [preds]
            for p in preds:
                if p.get("model_patch", "").strip():
                    all_preds.append(p)
        except Exception:
            pass
    merged = PRED_DIR / f"predictions_{harness}.json"
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"  merged {len(all_preds)} predictions -> {merged}")
    return merged


def run_eval(merged, run_id, model, eval_ids):
    max_workers = min(4, len(eval_ids))
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"  EVAL run_id={run_id} on {len(eval_ids)} instances max_workers={max_workers}")
    logf = LOG_DIR / f"eval_incr_{run_id}_{int(time.time())}.log"
    try:
        proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
        logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
        log(f"  eval finished rc={proc.returncode}; log -> {logf}")
        for line in proc.stdout.splitlines():
            if any(k in line for k in ("resolved", "unresolved", "skipping",
                                       "submitted", "completed", "error", "Error")):
                log(f"    {line}")
        return True
    except subprocess.TimeoutExpired:
        logf.write_text("TIMEOUT in run_eval")
        log(f"  eval TIMEOUT; log -> {logf}")
        return False


def main():
    log("=== R1597 incr_eval: 4 genuine backlog items (2 cline + 2 deepseek) ===")
    for cfg in CONFIGS:
        h = cfg["harness"]
        log(f"--- {h}: {len(cfg['ids'])} items {cfg['ids']} ---")
        merged = merge_predictions(h)
        ok = run_eval(merged, cfg["run_id"], cfg["model"], cfg["ids"])
        if not ok:
            log(f"  eval failed for {h}; items stay infra if no report.json")

    # Step 2: run FIXED regen_eval_summaries.py for cline-patched + deepseek-harness.
    # (a) corrects the 4 older cline rerun items infra->failed, and
    # (b) picks up the new R1597 report.json (resolved/failed/infra).
    log("=== regen_eval_summaries.py (fixed: scans all run dirs) cline-patched + deepseek-harness ===")
    os.chdir(str(HERE))
    proc = subprocess.run([PY, "regen_eval_summaries.py", "cline-patched", "deepseek-harness"],
                          capture_output=True, text=True, timeout=120)
    logf = LOG_DIR / f"regen_R1597_{int(time.time())}.log"
    logf.write_text(proc.stdout + proc.stderr)
    for line in proc.stdout.splitlines():
        log(f"  {line}")

    # Step 3: regenerate the full500 HTML report.
    log("=== gen_report_swebench_verified_full500_zh.py ===")
    os.chdir(str(HERE.parent))
    proc = subprocess.run([PY, "gen_report_swebench_verified_full500_zh.py"],
                          capture_output=True, text=True, timeout=120)
    logf2 = LOG_DIR / f"genreport_R1597_{int(time.time())}.log"
    logf2.write_text(proc.stdout + proc.stderr)
    for line in proc.stdout.splitlines():
        if any(k in line.lower() for k in ("cline", "deepseek", "resolved", "report", "wrote")):
            log(f"  {line}")
    log("=== R1597 DONE ===")


if __name__ == "__main__":
    main()
