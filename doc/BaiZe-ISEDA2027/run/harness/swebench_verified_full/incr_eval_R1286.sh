#!/bin/bash
# R1286 incremental eval: 2 NEW real patches (scan_backlog after R1285).
#   codex: scikit-learn__scikit-learn-14053
#   hermes: django__django-13820
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1286.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1286 START $(date) ==="

echo "[$(date)] --- codex: 1 instance ---"
$PY incr_eval_backlog.py codex scikit-learn__scikit-learn-14053 2>&1

echo "[$(date)] --- hermes: 1 instance ---"
$PY incr_eval_backlog.py hermes django__django-13820 2>&1

echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1286 DONE $(date) ==="
