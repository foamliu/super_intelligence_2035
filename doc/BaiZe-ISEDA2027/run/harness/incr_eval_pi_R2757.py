#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pi-only incr_eval R2757: eval 2 real django patches + merge 2 empties.
Detached via setsid; CPU-limited (taskset 0-15 + OMP=1)."""
from __future__ import annotations
import json, subprocess, time, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2757"
TIMEOUT_EVAL = 1800
PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"
H = "pi"
REAL = ["django__django-15973", "django__django-16100"]
EMPTY = ["django__django-16082", "django__django-16263"]
CPU_LIMIT_ENV = "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1"
CPU_LIMIT_TASKSET = "taskset -ac 0-15"


def log(m): print(f"[pi-incr {time.strftime('%H:%M:%S')}] {m}", flush=True)


def load_pred(f):
    d = json.loads(f.read_text())
    if isinstance(d, dict): d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]


log(f"pi incr_eval {ROUND}: eval {REAL} + merge empties {EMPTY}")
merged = PRED_DIR / f"predictions_{H}_new_{ROUND}.json"
allp = []
for iid in REAL:
    allp.extend(load_pred(PRED_DIR / f"{H}__{iid}.json"))
merged.write_text(json.dumps(allp, indent=2))
run_id = f"verified_full_glm53_{H}_incr_{ROUND}"
cmd = (f"{CPU_LIMIT_ENV} {CPU_LIMIT_TASKSET} nice -n 19 ionice -c 3 {PY310} "
       f"-m swebench.harness.run_evaluation "
       f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
       f"--instance_ids {' '.join(REAL)} --max_workers 1 "
       f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
log(f"EVAL {len(REAL)} django [CPU-limited] -> {run_id}")
EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                      capture_output=True, text=True, timeout=TIMEOUT_EVAL * len(REAL) + 600)
(HERE / "logs" / f"eval_{run_id}.log").write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
log(f"eval rc={proc.returncode}")

ef = REPORT_DIR / f"eval_glm53_{H}.json"
cum = json.loads(ef.read_text()) if ef.is_file() else {"harness": H, "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
for k in ("resolved", "failed", "infra_or_quota", "empty_patch", "no_patch"):
    cum.setdefault(k, [])
for iid in REAL:
    cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
    if not cands or not cands[0].exists():
        cum["infra_or_quota"].append(iid); log(f"  {iid}: NO report -> infra"); continue
    rep = json.loads(cands[0].read_text())
    inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
    if inst.get("resolved"):
        cum["resolved"].append(iid); log(f"  {iid}: RESOLVED")
    else:
        cum["failed"].append(iid); log(f"  {iid}: FAILED")
for iid in EMPTY:
    if iid not in cum["failed"] and iid not in cum["resolved"]:
        cum["empty_patch"].append(iid); cum["failed"].append(iid); log(f"  {iid}: EMPTY -> failed")
cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
cum["total_predictions"] = len(glob.glob(str(PRED_DIR / f"{H}__*.json")))
cum["evaluated"] = cum["n"]
ef.write_text(json.dumps(cum, indent=2))
log(f"PI cum: resolved={len(cum['resolved'])} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} n={cum['n']}")
log("DONE")
