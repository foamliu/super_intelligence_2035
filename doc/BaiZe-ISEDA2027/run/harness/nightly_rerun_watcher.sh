#!/bin/bash
# nightly_rerun_watcher.sh — 等 21:00 窗口开启后启动 infra 重跑
#
# 2026-11-23 用户令·第三步: 重跑时间窗 21:00–09:00
# 本脚本 sleep 到最近一个 21:00，然后调用 launch_infra_rerun.sh（后台 setsid 启动 orchestrator）。
# orchestrator 自管窗口结束（09:00 REGEN+stop），无需本脚本干预。
# 用 setsid 启动本脚本可脱离 cline 60min 超时。
set -u

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCH="$HARNESS_DIR/launch_infra_rerun.sh"

now=$(date +%s)
target=$(date -d 'today 21:00:00' +%s)
if [ "$target" -le "$now" ]; then
  target=$(date -d 'tomorrow 21:00:00' +%s)
fi
secs=$((target - now))
echo "[watcher] $(date '+%F %T') waiting ${secs}s ($(($secs/60))min) until 21:00"
sleep "$secs"
echo "[watcher] $(date '+%F %T') firing launch_infra_rerun.sh"
bash "$LAUNCH"
echo "[watcher] $(date '+%F %T') launch returned; orchestrator running in background"

# ARM stop script for 09:00 (kills orchestrator at window end, then re-arms this watcher)
STOP="$HARNESS_DIR/nightly_rerun_stop.sh"
if [ -f "$STOP" ]; then
  setsid bash "$STOP" > /tmp/nightly_rerun_stop.log 2>&1 < /dev/null &
  echo "[watcher] $(date '+%F %T') armed stop script PID=$! for 09:00"
fi
