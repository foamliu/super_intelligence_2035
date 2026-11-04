#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1600: incr_eval for 2 GENUINE cline-patched backlog items.
  django__django-17087      (patchlen=1639, predict finalized 22:05)
  matplotlib__matplotlib-20676 (patchlen=2313, predict finalized 22:18)

genuine scan (checks ALL run dirs for report.json) at 22:19 => GENUINE=2,
both cline-patched.  The other 7 cline items + deepseek matplotlib-26291
flagged by main-dir-only scan_backlog.py are FALSE positives (already
eval'd in rerun dirs; regen_eval_summaries.py scans all dirs correctly).

Discipline: docker eval runs in a separate container (sg docker), does NOT
interrupt the running predicts (cline rerun 28/58 matplotlib-24026,
codex predict, deepseek predict alive).
"""
import json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
LOG_DIR = HERE / "logs"
ENRICHED = HERE / "enriched_500.json"
TIMEOUT_EVAL = 1800
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"

CONFIGS = [
    {"harness": "cline-patched", "model": "cline-kimi-k2.6-cloud",
     "run_id": "verified_full_cline-patched_rerun_R1600",
     "ids": ["django__django-17087", "matplotlib__matplotlib-20676"]},
]


def log(m):
    print(f"[R1600 {time.strftime('%H:%M:%S')}] {m}", flush=True)


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
    log("=== R1600 incr_eval: 2 genuine cline-patched backlog items ===")
    for cfg in CONFIGS:
        h = cfg["harness"]
        log(f"--- {h}: {len(cfg['ids'])} items {cfg['ids']} ---")
        merged = merge_predictions(h)
        ok = run_eval(merged, cfg["run_id"], cfg["model"], cfg["ids"])
        if not ok:
            log(f"  eval failed for {h}; items stay infra if no report.json")

    # Step 2: regen_eval_summaries.py for cline-patched (picks up new R1600 report.json).
    log("=== regen_eval_summaries.py cline-patched ===")
    os.chdir(str(HERE))
    proc = subprocess.run([PY, "regen_eval_summaries.py", "cline-patched"],
                          capture_output=True, text=True, timeout=120)
    logf = LOG_DIR / f"regen_R1600_{int(time.time())}.log"
    logf.write_text(proc.stdout + proc.stderr)
    for line in proc.stdout.splitlines():
        log(f"  {line}")

    # Step 3: regenerate the full500 HTML report.
    log("=== gen_report_swebench_verified_full500_zh.py ===")
    os.chdir(str(HERE.parent))
    proc = subprocess.run([PY, "gen_report_swebench_verified_full500_zh.py"],
                          capture_output=True, text=True, timeout=120)
    logf2 = LOG_DIR / f"genreport_R1600_{int(time.time())}.log"
    logf2.write_text(proc.stdout + proc.stderr)
    for line in proc.stdout.splitlines():
        if any(k in line.lower() for k in ("cline", "deepseek", "resolved", "report", "wrote")):
            log(f"  {line}")
    log("=== R1600 DONE ===")


if __name__ == "__main__":
    main()
