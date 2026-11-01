#!/bin/bash
# incr_eval R1248: 1 backlog item (hermes django__django-13315, real patch 8652 chars)
# Backlog found by scan_backlog (R1248):
#   hermes: django__django-13315 (patchlen=8652)
# Memory self-check (287th) PASSED: avail ~1353GB, no this-line proc >50GB
#   (highest cline daemon 3.0GB, opencode 1.1GB; no partitions()/list() runaway).
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -euo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1248.log

echo "=== incr_eval R1248 START $(date) === (py=$PY)" | tee "$LOG"

cd "$HERE"

# --- 1. hermes: django__django-13315 (via incr_eval_backlog.py: merge+eval+parse+update) ---
export EVAL_MAX_WORKERS=8
echo "[$(date)] === incr_eval hermes django__django-13315 ===" | tee -a "$LOG"
$PY incr_eval_backlog.py hermes django__django-13315 2>&1 | tee -a "$LOG"

# --- 2. Regen eval summaries + HTML report ---
echo "[$(date)] === regen eval summaries ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
echo "[$(date)] === gen report HTML ===" | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"

echo "=== incr_eval R1248 DONE $(date) ===" | tee -a "$LOG"
