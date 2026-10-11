#!/bin/bash
# run_r2_grading.sh — 手动跑 r2 grading (Step 5/6 已完成, 此为 Step 7.1 run_eval)
# batch=2026_1011_083246, full config, 4 ports 8650/8651/8652/8654
set -euo pipefail
cd /nasdata/app.e0031982/code/eda_fastmcp
export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
set -a; source .env 2>/dev/null || true; set +a
echo "=== GRADING START $(date '+%F %T') ==="
echo "EVAL_FW_DIR=$EVAL_FW_DIR"
echo "SANDBOX_ENDPOINTS=$SANDBOX_ENDPOINTS"
echo "PROXY_PORTS=$PROXY_PORTS"
venv/bin/python scripts/run_eval.py \
  -g completed_code_generation_2026_1011_083246.jsonl \
  --benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl
echo "=== GRADING END $(date '+%F %T') exit=$? ==="
