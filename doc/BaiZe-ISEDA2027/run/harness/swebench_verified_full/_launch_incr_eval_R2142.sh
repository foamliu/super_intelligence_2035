#!/bin/bash
# Launcher: fully detach incr_eval R2142 so it survives the agent shell exit.
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
setsid python3 incr_eval_glm53_R2142.py > logs/incr_eval_R2142.out 2>&1 < /dev/null &
echo "incr_eval R2142 launched PID=$!"
