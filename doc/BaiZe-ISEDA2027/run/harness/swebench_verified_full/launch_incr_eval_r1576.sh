#!/bin/bash
# Launch incr_eval_r1576.py fully detached.
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
exec setsid "$PY" incr_eval_r1576.py >> logs/incr_eval_r1576.log 2>&1 </dev/null
