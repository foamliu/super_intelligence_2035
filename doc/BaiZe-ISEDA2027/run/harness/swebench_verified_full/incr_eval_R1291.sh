#!/bin/bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export EVAL_MAX_WORKERS=4
echo "[R1291] start $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py codex scikit-learn__scikit-learn-14710 scikit-learn__scikit-learn-15100 >> logs/eval_incr_R1291_codex.log 2>&1
echo "[R1291] codex done $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py deepseek-harness django__django-13590 >> logs/eval_incr_R1291_deepseek.log 2>&1
echo "[R1291] deepseek done $(date '+%H:%M:%S')"
python3 incr_eval_backlog.py hermes django__django-13964 >> logs/eval_incr_R1291_hermes.log 2>&1
echo "[R1291] hermes done $(date '+%H:%M:%S')"
echo "[R1291] ALL DONE $(date '+%H:%M:%S')"
