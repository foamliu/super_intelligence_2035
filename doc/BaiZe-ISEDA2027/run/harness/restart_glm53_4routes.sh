#!/bin/bash
# restart_glm53_4routes.sh — resume the 4 incomplete glm53 7x300 routes (2026-10-16 directive)
#
# codex/deepseek/hermes are DONE (300/300) and are NOT relaunched.
# Only cline-patched, opencode, claude-code, pi (140 pending total) are resumed.
# Idempotent: --resume skips resolved/patch-but-failed; retries quota-blocked/blocked.
#
# Prereqs (already done before invoking):
#   - gw_proxy on 127.0.0.1:9092 running (GW_API_KEY = glm53 key, upstream /v1)
#   - opencode config has provider 'gw' -> http://127.0.0.1:9092/v1, model gw/glm-5.3-flash
#   - pi config has provider 'gw' -> http://127.0.0.1:9092/v1 with glm-5.3-flash
#   - cline-patched harness GS openAiBaseUrl = http://127.0.0.1:9092/v1
#   - claude-code uses env only (ANTHROPIC_BASE_URL -> 9092)
#
# Usage: bash restart_glm53_4routes.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_glm53"
mkdir -p "$LOGDIR"

GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
RESULTS_FILE="$HERE/glm53_pilot_results.json"
RUN_SCRIPT="$HERE/run_serial_kimi.py"

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

HARNESSES=("cline-patched" "opencode" "claude-code" "pi")

echo "========================================"
echo "glm53 4-route resume | Start: $(date)"
echo "  Model: $GLM53_MODEL | Results: $RESULTS_FILE"
echo "  4 routes (codex/deepseek/hermes already DONE), each serial (N=1) | --resume"
echo "========================================"

PIDS=()
for h in "${HARNESSES[@]}"; do
  LOG="$LOGDIR/${h}_glm53.log"
  echo "Starting $h -> $LOG"
  nice -n 10 nohup python3 "$RUN_SCRIPT" \
    --harness "$h" --all-prepared --resume \
    > "$LOG" 2>&1 &
  PID=$!
  PIDS+=($PID)
  echo "  PID=$PID"
  sleep 2
done

echo ""
echo "All 4 launched. PIDs: ${PIDS[*]}"
echo "Logs: $LOGDIR/<harness>_glm53.log"
echo "Monitor: ps -eo pid=,etimes=,args= | grep run_serial_kimi | grep -v grep"
echo "Results: $RESULTS_FILE"
