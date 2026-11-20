#!/bin/bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export EVAL_MAX_WORKERS=4
echo "[R1292] start $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py deepseek-harness django__django-13741 >> logs/eval_incr_R1292_deepseek.log 2>&1
echo "[R1292] deepseek done $(date '+%H:%M:%S')"
echo "[R1292] ALL DONE $(date '+%H:%M:%S')"
