#!/bin/bash
# nightly_rerun_stop.sh — 09:00 窗口结束时停止 infra 重跑 orchestrator
#
# 2026-11-23 用户令·第三步: 重跑时间窗 21:00–09:00，窗口外只 park。
# 本脚本 sleep 到最近一个 09:00，然后:
#   1. 杀掉 orchestrator 进程组 (rerun_infra_verified.py + predict 子树)
#   2. REGEN 7way 报告 (以防有 eval 已完成)
#   3. 重新 ARM nightly_rerun_watcher.sh (下一个 21:00 再次启动)
#
# 用 setsid 启动本脚本可脱离 cline 60min 超时。
# 预测文件逐题落盘，kill 不丢已完成题目 (is_predicted() 重启后跳过非空 patch)。
set -u

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
VF_DIR="$HARNESS_DIR/swebench_verified_full"
WATCHER="$HARNESS_DIR/nightly_rerun_watcher.sh"
LOG="$VF_DIR/logs/rerun_infra_nightly.log"

log() { echo "[stop $(date '+%F %T')] $*"; }

# ── 等到 09:00 ──
# 当前在 21:00–09:00 窗口内时: 下一个 09:00 = 今天(若 <09) 或 明天(若 ≥21)
H=$(date +%H)
if [ "$H" -lt 9 ]; then
  target=$(date -d 'today 09:00:00' +%s)
else
  # ≥21 (窗口晚间段) 或异常 09–21 (兜底明天)
  target=$(date -d 'tomorrow 09:00:00' +%s)
fi
now=$(date +%s)
secs=$((target - now))
if [ "$secs" -le 0 ]; then
  log "WARNING: target already past (secs=$secs); execute immediately"
else
  log "waiting ${secs}s ($(($secs/60))min) until 09:00 (target=$(date -d "@$target" '+%F %T'))"
  sleep "$secs"
fi

# ── 1. 杀 orchestrator 进程组 ──
log "window ended (09:00); stopping orchestrator"
ORCH_PID=$(pgrep -f 'rerun_infra_verified\.py' 2>/dev/null | head -1)
if [ -z "$ORCH_PID" ]; then
  log "no orchestrator running; nothing to stop"
else
  log "found orchestrator PID=$ORCH_PID"
  PGID=$(ps -o pgid= -p "$ORCH_PID" 2>/dev/null | tr -d ' ')
  if [ -n "$PGID" ] && [ "$PGID" != "0" ]; then
    log "killing process group PGID=$PGID"
    kill -- -"$PGID" 2>/dev/null || true
  fi
  sleep 3
  # 兜底: 逐个 kill 残留
  pkill -f 'rerun_infra_verified\.py' 2>/dev/null || true
  # 只杀 rerun 相关的 predict (不碰 MM predict)
  pkill -f 'run_verified_full\.py predict.*rerun' 2>/dev/null || true
  pkill -f 'run_single\.py.*rerun' 2>/dev/null || true
  sleep 1
  log "orchestrator stopped"
fi

# ── 2. REGEN 7way 报告 ──
cd "$HARNESS_DIR"
if [ -f gen_report_glm53_7way.py ]; then
  log "REGEN 7way report..."
  python3 gen_report_glm53_7way.py > /tmp/regen_nightly_stop.log 2>&1
  if [ $? -eq 0 ]; then
    log "REGEN OK"
  else
    log "REGEN FAILED (see /tmp/regen_nightly_stop.log)"
  fi
fi

# ── 3. 重新 ARM watcher (下一个 21:00) ──
if [ -f "$WATCHER" ]; then
  if pgrep -f 'nightly_rerun_watcher\.sh' > /dev/null 2>&1; then
    log "watcher already running; skip re-arm"
  else
    log "re-arming watcher for next 21:00..."
    setsid bash "$WATCHER" > /tmp/nightly_rerun_watcher.log 2>&1 < /dev/null &
    log "watcher PID=$! armed"
  fi
else
  log "WARNING: watcher script not found at $WATCHER"
fi

log "done; orchestrator will resume at next 21:00 via watcher"
