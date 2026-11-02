#!/bin/bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export EVAL_MAX_WORKERS=4
echo "[R1290] start $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py deepseek-harness django__django-13569 >> logs/eval_incr_R1290_deepseek.log 2>&1
echo "[R1290] deepseek done $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py hermes django__django-13925 django__django-13933 >> logs/eval_incr_R1290_hermes.log 2>&1
echo "[R1290] hermes done $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py codex scikit-learn__scikit-learn-14894 >> logs/eval_incr_R1290_codex.log 2>&1
echo "[R1290] codex done $(date '+%H:%M:%S')"
echo "[R1290] ALL DONE $(date '+%H:%M:%S')"
