#!/bin/bash
# Re-grade full_v3 r5 with correct benchmark (auto-grade has benchmark bug)
# Generation file: completed_code_generation_2026_1012_131007.jsonl
# Batch: 2026_1012_131007
# Auto-grade: 3/158 (1.9%) [known bug] | timeout=5, success=153, failure=0
set -euo pipefail

EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
SANDBOX_ENDPOINTS="8650:/proj/train/AI/workdir/t0002997_1,8651:/proj/train/AI/workdir/t0002997_2,8652:/proj/train/AI/workdir/t0002997_3,8654:/proj/train/AI/workdir/t0002997_4"
PROXY_PORTS="8650,8651,8652,8654"
RAG_RECALL_URL="http://localhost:9006/recall"
SANDBOX_HOST="10.129.32.75"
export EVAL_FW_DIR SANDBOX_ENDPOINTS PROXY_PORTS RAG_RECALL_URL SANDBOX_HOST

GEN_FILE="completed_code_generation_2026_1012_131007.jsonl"
BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
LANG="pyAether"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
RUN_EVAL="/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py"

echo "=== FULL_V3 R5 RE-GRADE START $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "EVAL_FW_DIR=$EVAL_FW_DIR"
echo "SANDBOX_ENDPOINTS=$SANDBOX_ENDPOINTS"
echo "PROXY_PORTS=$PROXY_PORTS"
echo "RAG_RECALL_URL=$RAG_RECALL_URL"
echo "SANDBOX_HOST=$SANDBOX_HOST"
echo "GEN_FILE=$GEN_FILE"
echo "BENCHMARK=$BENCHMARK"
echo "LANG=$LANG"

cd "$EVAL_FW_DIR"
"$PYTHON" "$RUN_EVAL" \
  -g "$GEN_FILE" \
  --lang "$LANG" \
  --benchmark "$BENCHMARK" \
  2>&1

echo "=== FULL_V3 R5 RE-GRADE END $(date '+%Y-%m-%d %H:%M:%S') ==="
