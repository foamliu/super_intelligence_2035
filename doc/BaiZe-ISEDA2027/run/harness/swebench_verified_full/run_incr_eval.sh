#!/bin/bash
# Wrapper to run incremental eval+merge in background
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
python3 incremental_eval_merge.py --route cline-patched --regen >> logs/incr_eval_merge_11240413.log 2>&1
echo "DONE $(date)" >> logs/incr_eval_merge_11240413.log
