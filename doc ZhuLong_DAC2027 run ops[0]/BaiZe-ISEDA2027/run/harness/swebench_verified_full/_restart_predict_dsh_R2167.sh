#!/bin/bash
# _restart_predict_dsh_R2167.sh — restart deepseek-harness predict (parent died ~Nov6 17:19)
# gw_proxy_dsh:9093 verified UP (HTTP 200). Auto-resumes from 174 existing prediction files.
# Env copied from launch_glm53_full500.sh Step 3 + /proc/<alive-codex-parent>/environ.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
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
LOG="$HERE/logs_glm53/predict_deepseek-harness_glm53_R2167.log"
echo "[$(date)] restarting deepseek-harness predict -> $LOG"
nice -n 10 nohup python3 run_verified_full.py predict --harness deepseek-harness >> "$LOG" 2>&1 &
echo "  PID=$!"
sleep 3
if pgrep -f "run_verified_full.py predict --harness deepseek-harness" >/dev/null 2>&1; then
  echo "  OK: deepseek-harness predict ALIVE"
else
  echo "  WARN: predict not seen yet, check log"
fi
