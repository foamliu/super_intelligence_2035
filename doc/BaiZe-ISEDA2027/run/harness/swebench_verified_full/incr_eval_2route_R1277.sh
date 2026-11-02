#!/bin/bash
# R1277 incremental eval: 5 NEW real patches (scan_backlog after R1276).
#   codex: scikit-learn__scikit-learn-12682, scikit-learn__scikit-learn-12973
#   hermes: django__django-13670, django__django-13741, django__django-13786
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1277.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1277 START $(date) ==="

echo "[$(date)] --- codex: 2 instances ---"
$PY incr_eval_backlog.py codex scikit-learn__scikit-learn-12682 scikit-learn__scikit-learn-12973 2>&1

echo "[$(date)] --- hermes: 3 instances ---"
$PY incr_eval_backlog.py hermes django__django-13670 django__django-13741 django__django-13786 2>&1

echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1277 DONE $(date) ==="
