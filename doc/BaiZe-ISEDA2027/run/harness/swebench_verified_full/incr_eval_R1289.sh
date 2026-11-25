#!/bin/bash
# R1289 incremental eval: 6 NEW real patches (scan_backlog after R1288).
#   codex:  scikit-learn__scikit-learn-14141, -14496, -14629
#   deepseek-harness: django__django-13551, -13568
#   hermes: django__django-13837
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1289.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1289 START $(date) ==="

echo "[$(date)] --- codex: 3 instances ---"
$PY incr_eval_backlog.py codex scikit-learn__scikit-learn-14141 scikit-learn__scikit-learn-14496 scikit-learn__scikit-learn-14629 2>&1

echo "[$(date)] --- deepseek-harness: 2 instances ---"
$PY incr_eval_backlog.py deepseek-harness django__django-13551 django__django-13568 2>&1

echo "[$(date)] --- hermes: 1 instance ---"
$PY incr_eval_backlog.py hermes django__django-13837 2>&1

echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1289 DONE $(date) ==="
