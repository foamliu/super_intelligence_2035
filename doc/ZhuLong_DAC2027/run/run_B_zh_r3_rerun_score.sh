#!/bin/bash
# Score the B_zh_r3 RERUN (think-lang ablation, axis B=zh, round 3 rerun).
# Generation batch 2026_1112_085105 finished (142 success / 14 fail / 2 timeout)
# but the in-pipeline Step 7.1 run_eval.py failed because the orchestrator's
# run_cline_script.sh used the WRONG benchmark path (uppercase P:
# benchmarks/EDA-Eval-PyAether/EDA-Eval-PyAether-158.jsonl). This script re-runs
# run_eval.py with the CORRECT lowercase-p benchmark, same env as the regrade.
#
# Per 22:4x user order ③/④: rerun zh r3 with SAME config as r1/r3 (thinking=medium,
# LANG_HINT=请使用中文思考。, glm-5.2, -p 8 -n) — generation already done under that
# config; this only does the missing scoring step.
#
# Known pitfalls (same as run_B_zh_r2_regrade.sh — do NOT re-trip):
#   a) benchmark filename is lowercase p: benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl
#   b) run_eval.py reads EVAL_ROOT_DIR (NOT EVAL_ROOT_DIR_OVERRIDE)
#   c) must unset http_proxy/https_proxy and set NO_PROXY.
#
# Concurrency: orchestrator (run_think_lang_ablation) has EXITED (30/30 done);
# r3 rerun generation has EXITED; sandbox ports all free (404). Safe to score.
set -uo pipefail

# ---- arg parsing: -p N controls eval sandbox parallelism (EVAL_SANDBOX_WORKERS) ----
SCORE_PARALLEL=4   # sandbox is free now (no other eval running) -> use 4 of 4 endpoints
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) SCORE_PARALLEL="${2:-4}"; shift 2 ;;
    *)  shift ;;
  esac
done
export EVAL_SANDBOX_WORKERS="$SCORE_PARALLEL"

EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
EVAL_ROOT_DIR=/nasdata/app.e0031982/code/eda_code_eval   # run_eval.py reads this (NOT EVAL_ROOT_DIR_OVERRIDE)
# 8664 group — MUST match the workdirs the generation used (same as .env).
SANDBOX_ENDPOINTS="8664:/proj/train/AI/workdir/t0002596_bak_1,8665:/proj/train/AI/workdir/t0002596_bak,8653:/proj/train/AI/workdir/t0002596_skill,8669:/proj/train/AI/workdir/t0002596"
PROXY_PORTS="8664,8665,8653,8669"
SANDBOX_HOST="10.129.32.75"
export EVAL_FW_DIR EVAL_ROOT_DIR SANDBOX_ENDPOINTS PROXY_PORTS SANDBOX_HOST
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

GEN_FILE="completed_code_generation_2026_1112_085105.jsonl"   # r3 RERUN batch (new)
BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"  # lowercase p — matches real file
LANG="pyAether"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
RUN_EVAL="/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py"

echo "=== B_ZH_R3 RERUN SCORE START $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "GEN_FILE=$GEN_FILE  BENCHMARK=$BENCHMARK  SANDBOX_HOST=$SANDBOX_HOST"
echo "EVAL_ROOT_DIR=$EVAL_ROOT_DIR  EVAL_FW_DIR=$EVAL_FW_DIR  EVAL_SANDBOX_WORKERS=$SCORE_PARALLEL"

cd "$EVAL_FW_DIR"
"$PYTHON" "$RUN_EVAL" \
  -g "$GEN_FILE" \
  --lang "$LANG" \
  --benchmark "$BENCHMARK" \
  2>&1

echo "=== B_ZH_R3 RERUN SCORE END $(date '+%Y-%m-%d %H:%M:%S') ==="
