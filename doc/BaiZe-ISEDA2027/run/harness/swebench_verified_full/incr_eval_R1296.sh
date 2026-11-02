#!/bin/bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export EVAL_MAX_WORKERS=4
echo "[R1296] start $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py hermes django__django-14017 >> logs/eval_incr_R1296_hermes.log 2>&1
echo "[R1296] hermes done $(date '+%H:%M:%S')"
echo "[R1296] ALL DONE $(date '+%H:%M:%S')"
