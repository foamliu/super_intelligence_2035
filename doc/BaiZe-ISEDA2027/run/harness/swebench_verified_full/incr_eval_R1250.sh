#!/bin/bash
# incr_eval R1250: 1 backlog item (codex pytest-dev__pytest-5262, real patch 1153 chars)
# Backlog found by scan_backlog (R1250):
#   codex: pytest-dev__pytest-5262 (patchlen=1153)
# Memory self-check (289th) PASSED: avail ~1352GB, no this-line proc >50GB
#   (highest cline daemon 3.4GB, opencode 1.1GB; no partitions()/list() runaway).
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -euo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1250.log

echo "=== incr_eval R1250 START $(date) === (py=$PY)" | tee "$LOG"

cd "$HERE"

# --- 1. codex: pytest-dev__pytest-5262 (via incr_eval_backlog.py: merge+eval+parse+update) ---
export EVAL_MAX_WORKERS=8
echo "[$(date)] === incr_eval codex pytest-dev__pytest-5262 ===" | tee -a "$LOG"
$PY incr_eval_backlog.py codex pytest-dev__pytest-5262 2>&1 | tee -a "$LOG"

# --- 2. Regen eval summaries + HTML report ---
echo "[$(date)] === regen eval summaries ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
echo "[$(date)] === gen report HTML ===" | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"

echo "=== incr_eval R1250 DONE $(date) ===" | tee -a "$LOG"
