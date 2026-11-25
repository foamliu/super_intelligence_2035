#!/usr/bin/env bash
# ============================================================
# TensorBoard 管理（默认在 .29 上监听 0.0.0.0:6006）
#   bash scripts/tb_6006.sh start|stop|restart|status
# 日志目录 = $EXP_ROOT（nemo_experiments，含各 --name 的 tb_logs/）
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
export BAIZE_LLM_HOME
# shellcheck source=lib.sh
source "$HERE/lib.sh"
# shellcheck source=../configs/common.env
source "$BAIZE_LLM_HOME/configs/common.env"

PIDFILE="/tmp/baize_tb_${TB_PORT}.pid"
TLOG="/tmp/baize_tb_${TB_PORT}.log"

tb_pid() {
  local p=""
  [ -f "$PIDFILE" ] && p="$(cat "$PIDFILE" 2>/dev/null)"
  if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then echo "$p"; return 0; fi
  pgrep -f "tensorboard.*--port ${TB_PORT}" 2>/dev/null | head -1
}

do_start() {
  local p; p="$(tb_pid)"
  if [ -n "$p" ]; then
    log "TensorBoard 已在运行 pid=$p（端口 $TB_PORT）"
    do_status
    return 0
  fi
  if used_port "$TB_PORT"; then
    die "端口 $TB_PORT 被其它进程占用：$(ss -ltnp 2>/dev/null | grep ":$TB_PORT" | head -1)"
  fi
  [ -d "$EXP_ROOT" ] || { mkdir -p "$EXP_ROOT" || die "无法创建 $EXP_ROOT"; }
  log "启动 tensorboard --logdir $EXP_ROOT --host $TB_HOST --port $TB_PORT"
  setsid nohup "$PY/tensorboard" \
      --logdir "$EXP_ROOT" --host "$TB_HOST" --port "$TB_PORT" \
      --reload_interval 30 --samples_per_plugin scalars=100000 \
      > "$TLOG" 2>&1 < /dev/null &
  echo $! > "$PIDFILE"
  sleep 5
  local p2; p2="$(tb_pid)"
  if [ -n "$p2" ]; then
    pass "TensorBoard pid=$p2 → http://$(hostname -I 2>/dev/null | awk '{print $1}'):${TB_PORT}（日志 $TLOG）"
  else
    err "TensorBoard 启动失败，日志尾部："
    tail -20 "$TLOG" >&2
    exit 1
  fi
}

do_stop() {
  local p; p="$(tb_pid)"
  if [ -z "$p" ]; then
    log "未发现运行中的 TensorBoard（端口 $TB_PORT）"
    return 0
  fi
  log "停止 TensorBoard pid=$p"
  kill "$p" 2>/dev/null
  for _ in $(seq 1 10); do kill -0 "$p" 2>/dev/null || break; sleep 1; done
  kill -9 "$p" 2>/dev/null || true
  rm -f "$PIDFILE"
  used_port "$TB_PORT" && warn "端口 $TB_PORT 仍被占用（可能被别的进程接管）" || pass "已停止"
}

do_status() {
  local p; p="$(tb_pid)"
  echo "--- TensorBoard @ $(ts) ---"
  echo "  host/port : $(hostname) / $TB_PORT (bind $TB_HOST)"
  echo "  pid       : ${p:-<none>}"
  echo "  logdir    : $EXP_ROOT"
  echo "  listen    : $(ss -ltn 2>/dev/null | grep ":${TB_PORT}\b" | tr -s ' ' || echo '<none>')"
  if command -v curl >/dev/null 2>&1; then
    local code; code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://127.0.0.1:${TB_PORT}/" 2>/dev/null)"
    echo "  http      : ${code:-<no response>}"
  fi
  echo "  events    :"
  find "$EXP_ROOT" -name 'events.out.tfevents.*' -printf '      %TY-%Tm-%Td %TH:%TM  %10s  %p\n' 2>/dev/null \
    | sort -r | head -5
  echo "  log tail  :"; tail -5 "$TLOG" 2>/dev/null | sed 's/^/      /'
}

case "${1:-status}" in
  start)   do_start ;;
  stop)    do_stop ;;
  restart) do_stop; do_start ;;
  status)  do_status ;;
  *) echo "usage: $0 start|stop|restart|status" >&2; exit 2 ;;
esac
