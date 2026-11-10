#!/bin/bash
# Re-grade B_zh_r2 (think-lang ablation, axis B=zh, round 2).
# Generation was real (158 tasks, batch 2026_1110_073833) but grading was cut
# mid-way by the 8h cap (wake#806) -> pass=null. This re-grade runs run_eval.py
# against the correct PyAether-158 benchmark to recover the real pass rate.
#
# Template: run_A_none_r2_regrade.sh (used successfully 11-07 for A_none_r2).
# Changes vs template: GEN_FILE, tag/log strings -> B_zh_r2.
#
# Known pitfalls (from template comments — do NOT re-trip):
#   a) benchmark filename is lowercase p: benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl
#      (uppercase P path does not exist -> 0 tasks -> NA);
#   b) run_eval.py reads EVAL_ROOT_DIR (NOT EVAL_ROOT_DIR_OVERRIDE);
#   c) must unset http_proxy/https_proxy and set NO_PROXY=agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1.
#
# CONCURRENCY NOTE (2026-11-10): the 4 sandbox workdirs below are the SAME as
# eda_fastmcp/.env SANDBOX_ENDPOINTS (shared by every run_cline_script round).
# The eval framework isolates per port-shard (1 workdir : 1 shard : 1 task at a
# time WITHIN one run). Running this regrade concurrently with an in-flight
# run_cline_script round (e.g. B_es_r1) on the same workdirs + same 158-task
# benchmark breaks that isolation -> workdir pollution. Therefore this regrade
# is QUEUED to run only after the orchestrator (run_think_lang_ablation.sh) has
# finished all 30 rounds (see run_B_zh_r2_regrade_wait.sh). Do NOT run it while
# any run_cline_script / run_eval is active.
set -uo pipefail

EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
EVAL_ROOT_DIR=/nasdata/app.e0031982/code/eda_code_eval   # run_eval.py reads this (NOT EVAL_ROOT_DIR_OVERRIDE)
# 8664 group — MUST match the workdirs the generation used (same as .env).
SANDBOX_ENDPOINTS="8664:/proj/train/AI/workdir/t0002596_bak_1,8665:/proj/train/AI/workdir/t0002596_bak,8653:/proj/train/AI/workdir/t0002596_skill,8669:/proj/train/AI/workdir/t0002596"
PROXY_PORTS="8664,8665,8653,8669"
SANDBOX_HOST="10.129.32.75"
export EVAL_FW_DIR EVAL_ROOT_DIR SANDBOX_ENDPOINTS PROXY_PORTS SANDBOX_HOST
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

GEN_FILE="completed_code_generation_2026_1110_073833.jsonl"
BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"  # lowercase p — matches real file
LANG="pyAether"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
RUN_EVAL="/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py"

echo "=== B_ZH_R2 RE-GRADE START $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "GEN_FILE=$GEN_FILE  BENCHMARK=$BENCHMARK  SANDBOX_HOST=$SANDBOX_HOST"
echo "EVAL_ROOT_DIR=$EVAL_ROOT_DIR  EVAL_FW_DIR=$EVAL_FW_DIR"

cd "$EVAL_FW_DIR"
"$PYTHON" "$RUN_EVAL" \
  -g "$GEN_FILE" \
  --lang "$LANG" \
  --benchmark "$BENCHMARK" \
  2>&1

echo "=== B_ZH_R2 RE-GRADE END $(date '+%Y-%m-%d %H:%M:%S') ==="
