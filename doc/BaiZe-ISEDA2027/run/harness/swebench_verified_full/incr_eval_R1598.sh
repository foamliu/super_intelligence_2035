#!/bin/bash
# R1598 incremental eval: 3 genuine backlog items
#   cline-patched django-16263 (patch finalized 21:24)
#   deepseek-harness matplotlib-25287 (patch finalized 18:16) + 26342 (patch finalized 21:41)
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=logs/incr_eval_R1598.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1598 START $(date) ==="

export EVAL_MAX_WORKERS=4

# cline-patched: 1 item
echo "[$(date)] --- cline-patched django-16263 ---"
python3 incr_eval_backlog.py cline-patched django__django-16263 2>&1

# deepseek-harness: 2 items
echo "[$(date)] --- deepseek-harness matplotlib-25287 + 26342 ---"
python3 incr_eval_backlog.py deepseek-harness matplotlib__matplotlib-25287 matplotlib__matplotlib-26342 2>&1

echo "[$(date)] === regen summaries ==="
python3 regen_eval_summaries.py 2>&1

echo "=== incr_eval R1598 DONE $(date) ==="
