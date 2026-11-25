#!/bin/bash
# launch_predict_batch_glm53.sh — Restart SWE-bench predict with fixed resume code
# Starts 3 harnesses at a time to avoid overwhelming gateway quota.
# Usage: bash launch_predict_batch_glm53.sh <batch_num>
#   batch 1: opencode hermes cline-patched
#   batch 2: codex claude-code pi
#   batch 3: deepseek-harness
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_glm53"
mkdir -p "$LOGDIR"

export HARNESS_MODEL="glm-5.3-flash"
export OPENAI_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
export MODEL_SUFFIX="glm-5.3-flash"
export RUN_ID_PREFIX="verified_full_glm53"
export EVAL_TAG="glm53_"
export PRED_SUBDIR="predictions_glm53"
export WORKDIR_TAG="_glm53"
export GW_PROXY_PORT="9092"
export GW_DSH_PORT="9093"
export PYTHONUNBUFFERED=1
export PATH="$HOME/.bun/bin:$PATH"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

BATCH="${1:-1}"
case "$BATCH" in
  1) HARNESSES=("opencode" "hermes" "cline-patched") ;;
  2) HARNESSES=("codex" "claude-code" "pi") ;;
  3) HARNESSES=("deepseek-harness") ;;
  *) echo "Unknown batch: $BATCH. Use 1|2|3"; exit 1 ;;
esac

echo "=== SWE-bench predict batch $BATCH | $(date) ==="
for h in "${HARNESSES[@]}"; do
  LOG="$LOGDIR/predict_${h}_glm53.log"
  echo "Starting predict $h -> $LOG"
  nice -n 10 nohup python3 "$HERE/run_verified_full.py" predict --harness "$h" > "$LOG" 2>&1 &
  echo "  PID=$!"
  sleep 2
done
echo "Batch $BATCH launched. PIDs above."
