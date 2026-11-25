#!/bin/bash
# launch_cc_rerun.sh — restart claude-code predict with proper detachment
# Usage: bash launch_cc_rerun.sh

HERE="$(cd "$(dirname "$0")" && pwd)"
VF_DIR="$HERE/swebench_verified_full"
LOG="$HERE/logs_doubao_pro/claude-code_doubao_pro_rerun3.log"

export HARNESS_MODEL="doubao-seed-2.0-pro-cloud"
export MODEL_SUFFIX="doubao-seed-2.0-pro-cloud"
export PRED_SUBDIR="predictions_doubao_pro"
export WORKDIR_TAG="_doubao_pro"
export EVAL_TAG="doubao_pro_"
export PREDICT_WORKERS="1"
export PATH="$HOME/.bun/bin:$PATH"
export PYTHONUNBUFFERED=1
export GW_USAGE_LOG="/tmp/gw_proxy_usage.jsonl"
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"
export OPENAI_API_KEY="dummy-key-for-proxy"
export GW_PROXY_PORT="9090"
export GW_DSH_PORT="9091"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true

cd "$VF_DIR"
setsid nice -n 10 python3 run_verified_full.py predict --harness claude-code --workers 1 \
  > "$LOG" 2>&1 < /dev/null &
PID=$!
disown $PID 2>/dev/null || true
echo "claude-code predict restarted PID=$PID log=$LOG"
