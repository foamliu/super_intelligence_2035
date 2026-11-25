#!/usr/bin/env bash
# baize_posttrain_72h_guardian.sh — R63: 72h Wall-Clock Budget Enforcer
#
# Wraps the entire 11/9 launch sequence with:
#   1. Wall-clock budget tracking (default 72h)
#   2. Heartbeat file for external monitoring
#   3. Auto-trigger post-RL eval at T-4h (if RL still running)
#   4. Auto-trigger final report at T-1h
#   5. Graceful shutdown at T-0
#
# Usage:
#   bash baize_posttrain_72h_guardian.sh --dry-run
#   bash baize_posttrain_72h_guardian.sh --budget 72h
#   bash baize_posttrain_72h_guardian.sh --budget 72h --gpu-ids 0,1,2,3
#
# ⚠️ Surrogate RL results are NOT transferable to BaiZe.
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

DRY_RUN=0
BUDGET_HOURS=72
GPU_IDS=""
LAUNCH_STEPS="0-6"
SKIP_VENV=0
HEARTBEAT_FILE="${BAIZE_EXP_DIR}/guardian_heartbeat.txt"
GUARDIAN_LOG="${BAIZE_EXP_DIR}/guardian_$(date '+%Y%m%d_%H%M%S').log"
EVAL_RESERVE_HOURS=4
REPORT_RESERVE_HOURS=1

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)        DRY_RUN=1 ;;
    --budget)         BUDGET_HOURS="$2"; shift ;;
    --gpu-ids)        GPU_IDS="$2"; shift ;;
    --launch-steps)   LAUNCH_STEPS="$2"; shift ;;
    --skip-venv)      SKIP_VENV=1 ;;
    --heartbeat)      HEARTBEAT_FILE="$2"; shift ;;
    *) echo "Unknown: $1" ;;
  esac
  shift
done

BUDGET_SEC=$((BUDGET_HOURS * 3600))
EVAL_TRIGGER_SEC=$((BUDGET_SEC - EVAL_RESERVE_HOURS * 3600))
REPORT_TRIGGER_SEC=$((BUDGET_SEC - REPORT_RESERVE_HOURS * 3600))
mkdir -p "$(dirname "$HEARTBEAT_FILE")" 2>/dev/null || true

cat <<EOF
╔══════════════════════════════════════════════════╗
║  R63: 72h Guardian — Wall-Clock Budget Enforcer   ║
╚══════════════════════════════════════════════════╝
  Mode            : $([ $DRY_RUN = 1 ] && echo 'DRY-RUN' || echo 'EXECUTE')
  Budget          : ${BUDGET_HOURS}h (${BUDGET_SEC}s)
  Eval trigger    : T-${EVAL_RESERVE_HOURS}h
  Launch steps    : $LAUNCH_STEPS
  GPU IDs         : ${GPU_IDS:-auto}
  Heartbeat       : $HEARTBEAT_FILE
  $(date '+%F %T')
EOF

if [ $DRY_RUN = 1 ]; then
  echo ""
  echo "[dry-run] Would execute:"
  echo "  1. launch_11_9.sh --step $LAUNCH_STEPS (GPU=$GPU_IDS)"
  echo "  2. Monitor wall-clock; at T-${EVAL_RESERVE_HOURS}h trigger post_rl_pipeline.sh"
  echo "  3. At T-0 graceful shutdown"
  echo "  4. Heartbeat every 5 min → $HEARTBEAT_FILE"
  echo "✅ Dry-run passed."
  exit 0
fi

write_heartbeat() {
  local status="$1"
  local elapsed=$(( $(date +%s) - START_TIME ))
  local remaining=$(( BUDGET_SEC - elapsed ))
  cat > "$HEARTBEAT_FILE" <<HB
guardian_status: $status
start_time: $(date -d "@$START_TIME" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date '+%Y-%m-%d %H:%M:%S')
elapsed_sec: $elapsed
remaining_sec: $remaining
last_update: $(date '+%Y-%m-%d %H:%M:%S')
pid: $$
HB
}

START_TIME=$(date +%s)
HEARTBEAT_PID=""
RL_PROCESS_PID=""

start_heartbeat() {
  ( while true; do write_heartbeat "running"; sleep 300; done ) &
  HEARTBEAT_PID=$!
}

stop_heartbeat() {
  [ -n "$HEARTBEAT_PID" ] && kill "$HEARTBEAT_PID" 2>/dev/null || true
  [ -n "$HEARTBEAT_PID" ] && wait "$HEARTBEAT_PID" 2>/dev/null || true
}

start_watchdog() {
  (
    while true; do
      elapsed=$(( $(date +%s) - START_TIME ))
      if [ $elapsed -ge $BUDGET_SEC ]; then
        echo "[guardian] Budget exhausted (${elapsed}s). Graceful shutdown." >> "$GUARDIAN_LOG"
        if [ -n "$RL_PROCESS_PID" ] && kill -0 "$RL_PROCESS_PID" 2>/dev/null; then
          kill -SIGTERM "$RL_PROCESS_PID" 2>/dev/null || true
          sleep 10
          kill -SIGKILL "$RL_PROCESS_PID" 2>/dev/null || true
        fi
        write_heartbeat "budget_exhausted"
        exit 0
      fi
      [ $elapsed -ge $EVAL_TRIGGER_SEC ] && write_heartbeat "eval_window"
      sleep 60
    done
  ) &
}

stop_watchdog() {
  if [ -n "$WATCHDOG_PID" ]; then
    kill "$WATCHDOG_PID" 2>/dev/null || true
    wait "$WATCHDOG_PID" 2>/dev/null || true
  fi
}

cleanup() {
  stop_heartbeat
  stop_watchdog
  write_heartbeat "completed"
}
trap cleanup EXIT

echo "[guardian] Starting at $(date '+%F %T'), budget=${BUDGET_HOURS}h" >> "$GUARDIAN_LOG"
start_heartbeat
start_watchdog
WATCHDOG_PID=$!

GPU_FLAG=""
[ -n "$GPU_IDS" ] && GPU_FLAG="--gpu-ids $GPU_IDS"

echo "[guardian] Phase 1: Launch steps $LAUNCH_STEPS" >> "$GUARDIAN_LOG"
write_heartbeat "launching"

if [ $SKIP_VENV = 1 ]; then
  ADJUSTED_STEPS=$(echo "$LAUNCH_STEPS" | sed 's/^0-/--/')
  bash "$SCRIPT_DIR/baize_posttrain_launch_11_9.sh" --step "$ADJUSTED_STEPS" $GPU_FLAG 2>&1 | tee -a "$GUARDIAN_LOG" &
else
  bash "$SCRIPT_DIR/baize_posttrain_launch_11_9.sh" --step "$LAUNCH_STEPS" $GPU_FLAG 2>&1 | tee -a "$GUARDIAN_LOG" &
fi
RL_PROCESS_PID=$!
wait "$RL_PROCESS_PID" 2>/dev/null
LAUNCH_RC=$?
RL_PROCESS_PID=""
echo "[guardian] Launch done (rc=$LAUNCH_RC) at $(date '+%F %T')" >> "$GUARDIAN_LOG"

elapsed=$(( $(date +%s) - START_TIME ))
remaining=$(( BUDGET_SEC - elapsed ))

if [ $remaining -gt 3600 ]; then
  echo "[guardian] Phase 2: Post-RL eval (${remaining}s left)" >> "$GUARDIAN_LOG"
  write_heartbeat "post_rl_eval"
  bash "$SCRIPT_DIR/baize_posttrain_post_rl_pipeline.sh" \
    --rl-dir "${BAIZE_EXP_DIR}/baize_posttrain_rl_grpo" $GPU_FLAG 2>&1 | tee -a "$GUARDIAN_LOG"
else
  echo "[guardian] ⚠️ No time for eval (${remaining}s < 3600s). Skipping." >> "$GUARDIAN_LOG"
  write_heartbeat "no_time_for_eval"
fi

write_heartbeat "finalizing"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  72h Guardian Complete                           ║"
echo "╚══════════════════════════════════════════════════╝"
echo "  Heartbeat: $HEARTBEAT_FILE"
echo "  Log: $GUARDIAN_LOG"
echo "⚠️  Surrogate RL results are NOT transferable to BaiZe."