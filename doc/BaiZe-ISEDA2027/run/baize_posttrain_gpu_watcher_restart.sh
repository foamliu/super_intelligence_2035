#!/usr/bin/env bash
# baize_posttrain_gpu_watcher_restart.sh — Restart gpu_watcher if current one times out
# R107 (2026-11-09): Original watcher has max_wait=86400s (24h).
# If GPUs aren't freed before it expires, run this to restart with extended timeout.
# Usage:
#   bash baize_posttrain_gpu_watcher_restart.sh                    # Default: 48h timeout
#   bash baize_posttrain_gpu_watcher_restart.sh --check-only       # Just check status
#   bash baize_posttrain_gpu_watcher_restart.sh --max-wait 259200  # 72h
set -uo pipefail
SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
MAX_WAIT=172800; CHECK_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --max-wait) MAX_WAIT="$2"; shift ;;
    --check-only) CHECK_ONLY=1 ;;
    *) echo "Unknown: $1" ;;
  esac; shift
done
EXISTING_PID=$(pgrep -f 'baize_posttrain_gpu_watcher\.sh' | head -1)
if [ -n "$EXISTING_PID" ]; then
  ELAPSED=$(ps -o etimes= -p "$EXISTING_PID" | tr -d ' ')
  echo "gpu_watcher still running: PID=$EXISTING_PID, elapsed=$((ELAPSED/3600))h"
  [ $CHECK_ONLY = 1 ] && exit 0
  echo "To force restart: kill $EXISTING_PID first, then re-run this script"
  exit 0
fi
[ $CHECK_ONLY = 1 ] && { echo "No gpu_watcher running."; exit 1; }
echo "No gpu_watcher running. Starting new one (max_wait=$((MAX_WAIT/3600))h)..."
LOG_DIR="/nas_data/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/gpu_watcher_restart_$(date '+%Y%m%d_%H%M%S').log"
setsid bash -lc "exec bash '$SCRIPT_DIR/baize_posttrain_gpu_watcher.sh' --poll-interval 120 --max-wait $MAX_WAIT --launch-steps 1-5 --log '$LOG_FILE'" > /tmp/gpu_watcher_restart_stdout.log 2>&1 < /dev/null &
NEW_PID=$!
echo "New gpu_watcher started: PID=$NEW_PID"
echo "Log: $LOG_FILE"
echo "Verify: sleep 3 && tail -5 '$LOG_FILE'"
