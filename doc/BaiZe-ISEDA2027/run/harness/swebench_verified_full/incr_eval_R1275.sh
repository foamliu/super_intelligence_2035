#!/bin/bash
# R1275 incremental eval: 4 NEW real patches (scan_backlog after R1274).
#   codex: scikit-learn__scikit-learn-11578, scikit-learn__scikit-learn-12585
#   deepseek-harness: django__django-13401
#   hermes: django__django-13590
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1275.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1275 START $(date) ==="

echo "[$(date)] --- codex: 2 instances ---"
$PY incr_eval_backlog.py codex scikit-learn__scikit-learn-11578 scikit-learn__scikit-learn-12585 2>&1

echo "[$(date)] --- hermes: 1 instance ---"
$PY incr_eval_backlog.py hermes django__django-13590 2>&1

echo "[$(date)] --- deepseek-harness: 1 instance ---"
$PY incr_eval_backlog.py deepseek-harness django__django-13401 2>&1

echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1275 DONE $(date) ==="
