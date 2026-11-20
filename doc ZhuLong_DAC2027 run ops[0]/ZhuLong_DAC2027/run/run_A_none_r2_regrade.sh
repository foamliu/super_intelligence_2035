#!/bin/bash
# Re-grade A_none_r2 with correct PyAether benchmark.
# Generation was real (158 tasks, 11:19-13:00) but eval=NA due to fix#4 race
# (config.yaml git baseline was SkipperTcl → 0 scripts assembled → NA).
# fix#4 now explicit --benchmark; this re-grade uses the correct benchmark.
# Gen file: completed_code_generation_2026_1107_111911.jsonl
set -uo pipefail

EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
EVAL_ROOT_DIR=/nasdata/app.e0031982/code/eda_code_eval   # run_eval.py 读这个 (非 EVAL_ROOT_DIR_OVERRIDE)
# 8664 group (matches ablation runs per A_low_r1 log)
SANDBOX_ENDPOINTS="8664:/proj/train/AI/workdir/t0002596_bak_1,8665:/proj/train/AI/workdir/t0002596_bak,8653:/proj/train/AI/workdir/t0002596_skill,8669:/proj/train/AI/workdir/t0002596"
PROXY_PORTS="8664,8665,8653,8669"
SANDBOX_HOST="10.129.32.75"
export EVAL_FW_DIR EVAL_ROOT_DIR SANDBOX_ENDPOINTS PROXY_PORTS SANDBOX_HOST
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

GEN_FILE="completed_code_generation_2026_1107_111911.jsonl"
BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"  # lowercase p — matches real file
LANG="pyAether"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
RUN_EVAL="/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py"

echo "=== A_NONE_R2 RE-GRADE START $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "GEN_FILE=$GEN_FILE  BENCHMARK=$BENCHMARK  SANDBOX_HOST=$SANDBOX_HOST"

cd "$EVAL_FW_DIR"
"$PYTHON" "$RUN_EVAL" \
  -g "$GEN_FILE" \
  --lang "$LANG" \
  --benchmark "$BENCHMARK" \
  2>&1

echo "=== A_NONE_R2 RE-GRADE END $(date '+%Y-%m-%d %H:%M:%S') ==="
