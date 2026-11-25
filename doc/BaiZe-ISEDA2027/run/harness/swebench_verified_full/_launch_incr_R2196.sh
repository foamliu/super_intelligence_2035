#!/bin/bash
# Launcher for incr_eval R2196 — fully detached via setsid.
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 EVAL_MAX_WORKERS=1
exec python3 -u incr_eval_R2196.py >> logs/incr_eval_R2196.log 2>&1
