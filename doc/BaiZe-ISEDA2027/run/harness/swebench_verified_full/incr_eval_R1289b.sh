#!/bin/bash
# R1289b incremental eval: 2 more NEW real patches (scan_backlog after R1289a).
#   codex:  scikit-learn__scikit-learn-14710
#   hermes: django__django-13925
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1289b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1289b START $(date) ==="

echo "[$(date)] --- codex: 1 instance ---"
$PY incr_eval_backlog.py codex scikit-learn__scikit-learn-14710 2>&1

echo "[$(date)] --- hermes: 1 instance ---"
$PY incr_eval_backlog.py hermes django__django-13925 2>&1

echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1289b DONE $(date) ==="
