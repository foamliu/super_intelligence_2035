#!/bin/bash
# R1175b incremental eval: 2 new backlog items (real patches appeared during R1175 eval).
#   pi     : django__django-11149  (patch_len=7859)
#   hermes : django__django-10914  (patch_len=1488)
# Hard constraint: NEVER commit result JSON (all gitignored).
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1175b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1175b START $(date) ==="
echo "[$(date)] === pi django__django-11149 eval ==="
sg docker -c "$PY -m swebench.harness.run_evaluation --predictions_path $(pwd)/predictions/predictions_pi.json --dataset_name $(pwd)/enriched_500.json --split test --instance_ids django__django-11149 --max_workers 8 --run_id verified_full_pi --timeout 1800" 2>&1
echo "[$(date)] === pi eval DONE ==="
echo "[$(date)] === hermes django__django-10914 eval ==="
sg docker -c "$PY -m swebench.harness.run_evaluation --predictions_path $(pwd)/predictions/predictions_hermes.json --dataset_name $(pwd)/enriched_500.json --split test --instance_ids django__django-10914 --max_workers 8 --run_id verified_full_hermes --timeout 1800" 2>&1
echo "[$(date)] === hermes eval DONE ==="
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval R1175b DONE $(date) ==="
