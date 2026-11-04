#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1592b: force re-eval of 4 cline rerun ids with NEW patches.

The first R1592 attempt used the same run_id (verified_full_cline-patched),
so swebench found old report.json files and skipped re-eval ("already run,
skipping").  This script deletes the old report.json for the 4 instances and
uses a NEW run_id to force a fresh docker eval with the rerun patches.

Instances (previously failed, now have new patches after adapter fix):
  astropy__astropy-7336   django__django-11087
  django__django-14725    django__django-15098
"""
import json, os, subprocess, sys, time, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
TIMEOUT_EVAL = 1800
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"

HARNESS = "cline-patched"
DISPLAY = "cline"
MODEL = f"{DISPLAY}-kimi-k2.6-cloud"
OLD_RUN_ID = f"verified_full_{HARNESS}"
NEW_RUN_ID = f"verified_full_{HARNESS}_rerun_R1592"
EVAL_IDS = [
    "astropy__astropy-7336",
    "django__django-11087",
    "django__django-14725",
    "django__django-15098",
]

def log(m): print(f"[R1592b {time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log(f"=== force re-eval {len(EVAL_IDS)} cline rerun ids with NEW run_id ===")

    # Step 1: delete old report.json files to prevent skip
    old_dir = EVAL_LOG_ROOT / OLD_RUN_ID / MODEL
    for iid in EVAL_IDS:
        old_rj = old_dir / iid / "report.json"
        if old_rj.exists():
            old_rj.unlink()
            log(f"  deleted old report.json: {old_rj}")

    # Step 2: re-merge predictions (include new rerun patches)
    all_preds = []
    for f in sorted(PRED_DIR.glob(f"{HARNESS}__*.json")):
        if f.stat().st_size < 30: continue
        try:
            preds = json.loads(f.read_text())
            if isinstance(preds, dict): preds = [preds]
            for p in preds:
                if p.get("model_patch", "").strip(): all_preds.append(p)
        except Exception: pass
    merged = PRED_DIR / f"predictions_{HARNESS}.json"
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {len(all_preds)} predictions -> {merged}")

    # Step 3: run eval with NEW run_id
    max_workers = 4
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(EVAL_IDS)} --max_workers {max_workers} "
           f"--run_id {NEW_RUN_ID} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {DISPLAY} on {len(EVAL_IDS)} instances (run_id={NEW_RUN_ID})")
    logf = LOG_DIR / f"eval_incr_{NEW_RUN_ID}_{int(time.time())}.log"
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(EVAL_IDS) + 600)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  eval finished rc={proc.returncode}; log -> {logf}")
    # show key lines
    for line in proc.stdout.splitlines():
        if any(k in line for k in ("resolved", "unresolved", "skipping", "submitted", "completed")):
            log(f"  {line}")

    # Step 4: parse results from NEW run_id directory
    new_dir = EVAL_LOG_ROOT / NEW_RUN_ID / MODEL
    summary_file = REPORT_DIR / f"eval_{HARNESS}.json"
    summary = json.loads(summary_file.read_text()) if summary_file.exists() else {}
    for k in ("resolved", "failed", "infra_or_quota", "no_patch"):
        summary.setdefault(k, [])

    for iid in EVAL_IDS:
        rj = new_dir / iid / "report.json"
        # remove from all lists first (re-eval)
        for k in ("resolved", "failed", "infra_or_quota", "no_patch"):
            summary[k] = [x for x in summary[k] if x != iid and not x.startswith(f"{iid}(")]
        if not rj.exists():
            summary["infra_or_quota"].append(iid)
            log(f"  {iid}: NO report.json -> infra")
            continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (summary["resolved"] if resolved else summary["failed"]).append(iid)
            log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")
            log(f"  {iid}: parse error -> infra ({e})")

    summary["n"] = len(summary["resolved"]) + len(summary["failed"]) + len(summary["infra_or_quota"])
    summary_file.write_text(json.dumps(summary, indent=2))
    log(f"updated {summary_file}: resolved={len(summary['resolved'])} "
        f"failed={len(summary['failed'])} infra={len(summary['infra_or_quota'])} n={summary['n']}")

    # Step 5: regen report
    log("=== regen report ===")
    os.chdir(HERE.parent)
    proc2 = subprocess.run([PY, "gen_report_swebench_verified_full500_zh.py"],
                           capture_output=True, text=True, timeout=120)
    logf2 = LOG_DIR / f"regen_R1592b_{int(time.time())}.log"
    logf2.write_text(proc2.stdout + proc2.stderr)
    for line in proc2.stdout.splitlines():
        if "cline" in line.lower():
            log(f"  {line}")
    log("=== R1592b DONE ===")

if __name__ == "__main__":
    main()
