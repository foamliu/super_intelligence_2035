#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2784 incremental eval launcher — codex sphinx-7462 (deferred from R2783).

Single-instance swebench docker eval for codex's newly-predicted real patch
(sphinx-doc__sphinx-7462, patch 4025B). CPU-limited per 运维令 2026-11-02:
  taskset -ac 0-15  (pin to 16 cores, max 1600% << 8000% kill threshold)
  OMP/OPENBLAS/MKL/NUMEXPR = 1
  nice 19, ionice -c 3 (do not contend pretrain)
Launched via setsid so it survives the cline tool-call timeout. Parsing the
resulting report.json + merging into reports/eval_glm53_codex.json happens
NEXT round (when report.json is on disk).
"""
from __future__ import annotations
import json, subprocess, time
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
ENRICHED = HERE / "enriched_500.json"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
ROUND = "R2784"
PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"
TIMEOUT_EVAL = 1800
CPU_ENV = "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1"
CPU_TASKSET = "taskset -ac 0-15"


def log(m: str):
    print(f"[incr-eval-R2784 {time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    harness = "codex"
    iids = ["sphinx-doc__sphinx-7462"]
    merged = PRED_DIR / f"predictions_{harness}_new_{ROUND}.json"
    all_preds = []
    for iid in iids:
        pf = PRED_DIR / f"{harness}__{iid}.json"
        d = json.loads(pf.read_text())
        if isinstance(d, dict):
            d = [d]
        all_preds.extend(p for p in d if (p.get("model_patch") or "").strip())
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"{harness}: merged {len(all_preds)} patches -> {merged.name}")
    run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
    cmd = (f"{CPU_ENV} {CPU_TASKSET} nice -n 19 ionice -c 3 {PY310} "
           f"-m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(iids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    log(f"{harness}: EVAL {iids} [CPU-limited 16 cores] run_id={run_id}")
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(iids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(
        proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"{harness}: eval rc={proc.returncode} DONE")


if __name__ == "__main__":
    main()
