#!/bin/bash
# Launch incr_eval_R2691 in background with CPU guardrails
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
nohup nice -n 19 ionice -c 3 "$PY" incr_eval_R2691.py > logs_glm53/incr_eval_R2691.log 2>&1 &
echo $! > logs_glm53/incr_eval_R2691.pid
echo "LAUNCHED PID=$(cat logs_glm53/incr_eval_R2691.pid)"
