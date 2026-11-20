#!/bin/bash
set -euo pipefail
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1165b.log
ENRICHED=$HERE/enriched_500.json
cd "$HERE"
echo "=== incr_eval R1165b START $(date) ===" | tee "$LOG"
echo "[$(date)] === pi eval: sympy__sympy-12419 ===" | tee -a "$LOG"
sg docker -c "$PY -m swebench.harness.run_evaluation --predictions_path predictions/predictions_pi.json --dataset_name $ENRICHED --split test --instance_ids sympy__sympy-12419 --max_workers 8 --run_id verified_full_pi --timeout 1800" 2>&1 | tee -a "$LOG"
echo "[$(date)] === pi eval DONE ===" | tee -a "$LOG"
echo "[$(date)] === hermes eval: 3 astropy instances ===" | tee -a "$LOG"
sg docker -c "$PY -m swebench.harness.run_evaluation --predictions_path predictions/predictions_hermes.json --dataset_name $ENRICHED --split test --instance_ids astropy__astropy-7166 astropy__astropy-7336 astropy__astropy-7606 --max_workers 8 --run_id verified_full_hermes --timeout 1800" 2>&1 | tee -a "$LOG"
echo "[$(date)] === hermes eval DONE ===" | tee -a "$LOG"
echo "[$(date)] === regen eval summaries ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
echo "[$(date)] === gen report HTML ===" | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"
echo "=== incr_eval R1165b DONE $(date) ===" | tee -a "$LOG"
