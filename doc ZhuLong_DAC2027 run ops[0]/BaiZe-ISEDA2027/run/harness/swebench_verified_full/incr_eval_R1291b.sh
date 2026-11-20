#!/bin/bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export EVAL_MAX_WORKERS=4
echo "[R1291b] start $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py deepseek-harness django__django-13658 django__django-13670 >> logs/eval_incr_R1291b_deepseek.log 2>&1
echo "[R1291b] deepseek done $(date '+%H:%M:%S')"
echo "[R1291b] ALL DONE $(date '+%H:%M:%S')"
