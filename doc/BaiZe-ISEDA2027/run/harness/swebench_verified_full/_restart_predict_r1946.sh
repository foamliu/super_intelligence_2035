#!/bin/bash
# R1946: restart hermes + deepseek predict (stopped/crashed)
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
export HARNESS_MODEL="glm-5.3-flash"
export OPENAI_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
export MODEL_SUFFIX="glm-5.3-flash"
export RUN_ID_PREFIX="verified_full_glm53"
export EVAL_TAG="glm53_"
export PRED_SUBDIR="predictions_glm53"
export WORKDIR_TAG="_glm53"
export GW_PROXY_PORT="9092"
export GW_DSH_PORT="9093"
export PATH="$HOME/.bun/bin:$PATH"
export PYTHONUNBUFFERED=1
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

setsid nice -n 10 python3 run_verified_full.py predict --harness hermes > logs_glm53/predict_hermes_glm53_r1946.log 2>&1 &
HPID=$!
echo "hermes predict restarted PID=$HPID"

setsid nice -n 10 python3 run_verified_full.py predict --harness deepseek-harness > logs_glm53/predict_deepseek-harness_glm53_r1946.log 2>&1 &
DPID=$!
echo "deepseek predict restarted PID=$DPID"

sleep 3
echo "---verify---"
kill -0 $HPID 2>/dev/null && echo "hermes ALIVE" || echo "hermes DEAD"
kill -0 $DPID 2>/dev/null && echo "deepseek ALIVE" || echo "deepseek DEAD"
