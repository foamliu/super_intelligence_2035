#!/usr/bin/env bash
# baize_posttrain_mcp_server.sh -- Parameterized MCP Server Launch (R95)
# Port 8091 by default (8090 occupied by MRT)
set -uo pipefail
PORT="8091"
EDA_BASE="$HOME/code/eda_fastmcp"
PYAETHER_PY="$HOME/code/pyaether_venv/bin/python"
LOG_DIR="$HOME/code/BaiZe-ISEDA2027/nemo_experiments"
MODE="start"
while [ $# -gt 0 ]; do
  case "$1" in
    --port)  PORT="$2"; shift 2 ;;
    --check) MODE="check" ;;
    --kill)  MODE="kill" ;;
    --help|-h) echo "Usage: $0 [--port N] [--check] [--kill]"; exit 0 ;;
    *) shift ;;
  esac
  shift 2>/dev/null || true
done
LOG_FILE="$LOG_DIR/mcp_server_$PORT.log"
PID_FILE="/tmp/baize_mcp_server_$PORT.pid"
mkdir -p "$LOG_DIR"
case "$MODE" in
  check)
    [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null && echo "Running PID $(cat $PID_FILE)" || echo "Not running"
    ;;
  kill)
    [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null && echo "Killed" || echo "No PID"
    rm -f "$PID_FILE"
    ;;
  start)
    [ ! -f "$PYAETHER_PY" ] && echo "ERROR: venv missing" && exit 1
    ss -tlnp | grep -q ":$PORT " && echo "ERROR: port in use" && exit 1
    cd "$EDA_BASE"
    setsid bash -c "exec $PYAETHER_PY -m eda_fastmcp.server --port $PORT --host 0.0.0.0" > "$LOG_FILE" 2>&1 < /dev/null &
    echo $! > "$PID_FILE"
    sleep 5
    kill -0 "$(cat "$PID_FILE")" 2>/dev/null && echo "Started PID $(cat $PID_FILE) on $PORT" || echo "FAILED"
    ;;
esac
