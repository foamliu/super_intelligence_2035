#!/bin/bash
# incr_eval R1250b: 1 backlog item (codex pytest-dev__pytest-5631, real patch 3336 chars)
# Found by rescan after R1250 (codex predict produced new patch during R1250 eval).
# Memory self-check (289th) PASSED.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -euo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1250b.log

echo "=== incr_eval R1250b START $(date) === (py=$PY)" | tee "$LOG"
cd "$HERE"

export EVAL_MAX_WORKERS=8
echo "[$(date)] === incr_eval codex pytest-dev__pytest-5631 ===" | tee -a "$LOG"
$PY incr_eval_backlog.py codex pytest-dev__pytest-5631 2>&1 | tee -a "$LOG"

echo "[$(date)] === regen eval summaries ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
echo "[$(date)] === gen report HTML ===" | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"

echo "=== incr_eval R1250b DONE $(date) ===" | tee -a "$LOG"
