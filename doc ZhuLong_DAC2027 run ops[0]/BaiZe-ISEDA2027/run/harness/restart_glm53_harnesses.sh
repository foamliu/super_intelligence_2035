#!/bin/bash
# restart_glm53_harnesses.sh — Restart 7 harnesses for glm53 7×300 (2026-10-14)
# Proxies (9092, 9093) must already be running.
# Uses --resume to skip completed entries in glm53_pilot_results.json.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_glm53"
mkdir -p "$LOGDIR"

GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
RESULTS_FILE="$HERE/glm53_pilot_results.json"
RUN_SCRIPT="$HERE/run_serial_kimi.py"
PYTHON="python3"
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

export HARNESS_MODEL="$GLM53_MODEL"
export OPENAI_API_KEY="$GLM53_KEY"
export RESULTS_PATH="$RESULTS_FILE"
export GW_PROXY_PORT="9092"
export GW_DSH_PORT="9093"
export PATH="$HOME/.bun/bin:$PATH"
export PYTHONUNBUFFERED=1
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

echo "========================================"
echo "Restarting 7x300 with glm-5.3-flash | $(date)"
echo "  Model: $GLM53_MODEL | Results: $RESULTS_FILE"
echo "  Proxies: gw=9092 dsh=9093"
echo "========================================"

PIDS=()
for h in "${HARNESSES[@]}"; do
  LOG="$LOGDIR/${h}_glm53.log"
  echo "Starting $h -> $LOG"
  setsid nice -n 10 $PYTHON "$RUN_SCRIPT" \
    --harness "$h" --all-prepared --resume \
    > "$LOG" 2>&1 &
  PID=$!
  PIDS+=($PID)
  echo "  PID=$PID"
  sleep 1
done

echo ""
echo "All 7 launched. PIDs: ${PIDS[*]}"
echo "Logs: $LOGDIR/<harness>_glm53.log"
