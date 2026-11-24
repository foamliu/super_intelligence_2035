#!/bin/bash
# nightly_rerun_watcher.sh — 等 21:00 窗口开启后启动 infra 重跑
#
# 2026-11-23 用户令·第三步: 重跑时间窗 21:00–09:00
# 本脚本 sleep 到最近一个 21:00，然后调用 launch_infra_rerun.sh（后台 setsid 启动 orchestrator）。
# orchestrator 自管窗口结束（09:00 REGEN+stop），无需本脚本干预。
# 用 setsid 启动本脚本可脱离 cline 60min 超时。
set -u

# ── NFS self-healing: copy self to /tmp (local fs) and re-exec ──
# 2026-11-24 fix: script on NFS → "Stale file handle" crash during long sleep.
_SELF_TMP="/tmp/nightly_rerun_watcher.sh"
if [ "$(readlink -f "$0" 2>/dev/null)" != "$_SELF_TMP" ]; then
  cp "$0" "$_SELF_TMP"
  exec bash "$_SELF_TMP"
fi

HARNESS_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness"
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
# 2026-11-24 fix: copy stop script to /tmp (local fs) before running — avoids NFS
# "Stale file handle" crash during long sleep (was root cause of 09:00 stop failure).
STOP="$HARNESS_DIR/nightly_rerun_stop.sh"
if [ -f "$STOP" ]; then
  cp "$STOP" /tmp/nightly_rerun_stop.sh
  setsid bash /tmp/nightly_rerun_stop.sh > /tmp/nightly_rerun_stop.log 2>&1 < /dev/null &
  echo "[watcher] $(date '+%F %T') armed stop script PID=$! for 09:00 (from /tmp)"
fi
