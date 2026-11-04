#!/bin/bash
# R1598b: re-run deepseek eval (25287+26342) that died when launcher timed out + regen
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=logs/incr_eval_R1598b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1598b START $(date) ==="
export EVAL_MAX_WORKERS=4
echo "[$(date)] --- deepseek-harness matplotlib-25287 + 26342 ---"
python3 incr_eval_backlog.py deepseek-harness matplotlib__matplotlib-25287 matplotlib__matplotlib-26342 2>&1
echo "[$(date)] === regen summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "=== incr_eval R1598b DONE $(date) ==="
