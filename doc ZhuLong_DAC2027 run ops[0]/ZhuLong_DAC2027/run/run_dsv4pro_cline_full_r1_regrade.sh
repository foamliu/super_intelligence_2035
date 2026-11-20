#!/bin/bash
# Re-grade r1 (cline x deepseek-v4-pro x full) with correct benchmark.
# Batch: 2026_1023_231253  | GEN_FILE: completed_code_generation_2026_1023_231253.jsonl
# Hard-cut from PID 1800419 on 2026-10-24 (user order: r1 硬切, 手动 regrade).
# Status at cut: 149 success / 0 fail / 8 timeout / 1 in-progress(killed->fail).
# Judge 13: timeout 8 <= 10 => valid, mark degraded.
set -uo pipefail

# --- env (template同r5; unset proxy + NO_PROXY + EVAL_FW_DIR + 8650组) ---
unset http_proxy https_proxy
NO_PROXY=10.129.32.75,localhost,127.0.0.1
EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
SANDBOX_ENDPOINTS="8650:/proj/train/AI/workdir/t0002997_1,8651:/proj/train/AI/workdir/t0002997_2,8652:/proj/train/AI/workdir/t0002997_3,8654:/proj/train/AI/workdir/t0002997_4"
PROXY_PORTS="8650,8651,8652,8654"
RAG_RECALL_URL="http://localhost:9006/recall"
SANDBOX_HOST="10.129.32.75"
export NO_PROXY EVAL_FW_DIR SANDBOX_ENDPOINTS PROXY_PORTS RAG_RECALL_URL SANDBOX_HOST

GEN_FILE="completed_code_generation_2026_1023_231253.jsonl"
BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
LANG="pyAether"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
RUN_EVAL="/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py"

echo "=== R1 (dsv4pro x cline x full) RE-GRADE START $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "GEN_FILE=$GEN_FILE  (in ~/eda_code_eval)"
echo "BENCHMARK=$BENCHMARK  LANG=$LANG"
echo "SANDBOX_HOST=$SANDBOX_HOST  PROXY_PORTS=$PROXY_PORTS"
echo "proxy unset; NO_PROXY=$NO_PROXY"

cd "$EVAL_FW_DIR"
"$PYTHON" "$RUN_EVAL" \
  -g "$GEN_FILE" \
  --lang "$LANG" \
  --benchmark "$BENCHMARK" \
  2>&1

echo "=== R1 RE-GRADE END $(date '+%Y-%m-%d %H:%M:%S') ==="
