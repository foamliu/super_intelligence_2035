#!/usr/bin/env bash
# baize_posttrain_a5_llamacpp_serve.sh -- serve Qwen3.5-2B Q4_K_M via llama.cpp
# for the A5 single run, then gate it with the preflight.
#
# WHY: the 19:53 probe proved the route is fast enough (132.52 tok/s aggregate)
# but NOT that cline can drive it (tool_calls / streaming / determinism). This
# script starts the server with the same parameters as the probe (so the
# measured throughput carries over) and refuses to leave a "green" server
# behind if any preflight gate fails.
#
# Usage:
#   bash baize_posttrain_a5_llamacpp_serve.sh            # start + preflight
#   bash baize_posttrain_a5_llamacpp_serve.sh status
#   bash baize_posttrain_a5_llamacpp_serve.sh stop
#
# Exit: 0 ok; 2 port busy; 3 server failed; 4 preflight failed.
set -uo pipefail

RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TS="$(date +%Y%m%d_%H%M%S)"
GGUF="${GGUF:-/nas_data/app.e0031982/models/qwen35_gguf/qwen3.5-2b-Q4_K_M.gguf}"
BIN="${BIN:-$HOME/tools/llama.cpp/build/bin/llama-server}"
PORT="${PORT:-8095}"
ALIAS="${ALIAS:-qwen3.5-2b-a5}"
THREADS="${THREADS:-16}"
PARALLEL="${PARALLEL:-8}"
CTX="${CTX:-262144}"
PY="${PY:-/nas_data/app.e0031982/miniforge3/envs/py310/bin/python}"
[ -x "$PY" ] || PY="$(command -v python3 || echo python3)"
LOG="/tmp/a5_llamacpp_server_${TS}.log"
PIDFILE="/tmp/a5_llamacpp_server_${TS}.pid"
LATEST_PID="/tmp/a5_llamacpp_server.latest.pid"

export NO_PROXY="127.0.0.1,localhost,${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,${no_proxy:-}"

stop_pid() {
  local p="$1"
  [ -n "$p" ] || return 0
  kill "$p" 2>/dev/null || true
  for _ in $(seq 1 15); do kill -0 "$p" 2>/dev/null || return 0; sleep 1; done
  kill -9 "$p" 2>/dev/null || true
}

if [ "${1:-start}" = "stop" ]; then
  P=""
  [ -f "$LATEST_PID" ] && P="$(cat "$LATEST_PID")"
  [ -n "$P" ] || { echo "[stop] no pidfile"; exit 0; }
  echo "[stop] killing our llama-server pid=$P"
  stop_pid "$P"
  rm -f "$LATEST_PID"
  exit 0
fi

if [ "${1:-start}" = "status" ]; then
  curl -s --noproxy '*' "http://127.0.0.1:${PORT}/v1/models" | head -c 600; echo
  [ -f "$LATEST_PID" ] && echo "pid=$(cat "$LATEST_PID") alive=$(kill -0 "$(cat "$LATEST_PID")" 2>/dev/null && echo yes || echo no)"
  exit 0
fi

[ -f "$GGUF" ] || { echo "[serve] FATAL gguf missing: $GGUF"; exit 3; }
[ -x "$BIN" ] || { echo "[serve] FATAL llama-server missing: $BIN"; exit 3; }
if ss -ltn 2>/dev/null | grep -q ":${PORT} "; then
  echo "[serve] FATAL port $PORT already in use — pick PORT=18098 (do NOT kill unknown processes)"; exit 2
fi

SHA="$(sha256sum "$GGUF" | cut -d' ' -f1)"
REV="$(git -C "$(dirname "$(dirname "$(dirname "$BIN")")")" rev-parse --short HEAD 2>/dev/null || echo unknown)"

echo "[serve] host=$(hostname) nproc=$(nproc) threads=$THREADS parallel=$PARALLEL ctx=$CTX"
echo "[serve] gguf=$GGUF sha256=$SHA rev=$REV alias=$ALIAS port=$PORT"

PID=""
start_with() {
  local extra="$1"
  echo "[serve] launch extra=[$extra]"
  CUDA_VISIBLE_DEVICES="" nice -n 10 "$BIN" -m "$GGUF" \
      -t "$THREADS" -tb "$THREADS" -c "$CTX" --parallel "$PARALLEL" \
      --alias "$ALIAS" --jinja --metrics \
      --temp 0 --top-k 1 --seed 1234 --host 127.0.0.1 --port "$PORT" \
      --no-warmup --slots $extra > "$LOG" 2>&1 &
  PID=$!
  for _ in $(seq 1 150); do
    if curl -sf --noproxy '*' "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
      return 0
    fi
    kill -0 "$PID" 2>/dev/null || return 1
    sleep 2
  done
  return 1
}


THINK_MODE="enable_thinking=false"
KW='{"enable_thinking":false}'
if ! start_with "--chat-template-kwargs $KW"; then
  if kill -0 "$PID" 2>/dev/null; then
    echo "[serve] FATAL server alive but /health never OK after 300s — see $LOG"
    stop_pid "$PID"; exit 3
  fi
  echo "[serve] WARN --chat-template-kwargs unsupported (see $LOG); retry without it"
  THINK_MODE="none(unverified)"
  if ! start_with ""; then
    echo "[serve] FATAL server failed to start — see $LOG"
    [ -n "$PID" ] && stop_pid "$PID"
    exit 3
  fi
fi
echo "$PID" > "$PIDFILE"
echo "$PID" > "$LATEST_PID"
echo "[serve] up pid=$PID log=$LOG"

export A5S_TS="$TS" A5S_PID="$PID" A5S_PORT="$PORT" A5S_ALIAS="$ALIAS" \
       A5S_GGUF="$GGUF" A5S_SHA="$SHA" A5S_REV="$REV" A5S_THREADS="$THREADS" \
       A5S_PARALLEL="$PARALLEL" A5S_CTX="$CTX" A5S_LOG="$LOG" A5S_THINK="$THINK_MODE"
"$PY" - "$RUN_DIR/a5_llamacpp_server_${TS}.json" <<'PYEOF'
import json, os, sys, time
d = {k[4:].lower(): v for k, v in os.environ.items() if k.startswith("A5S_")}
d["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["hostname"] = os.uname().nodename
json.dump(d, open(sys.argv[1], "w"), indent=2)
print(json.dumps(d, indent=2))
PYEOF

echo "[serve] preflight (identity / tool non-stream / tool stream / roundtrip / determinism / thinking)"
"$PY" "$RUN_DIR/baize_posttrain_a5_llamacpp_preflight.py" \
    --port "$PORT" --expected "$ALIAS" \
    --out "$RUN_DIR/a5_llamacpp_preflight_${TS}.json"
RC=$?
if [ "$RC" -ne 0 ]; then
  echo "[serve] PREFLIGHT FAILED rc=$RC — stopping server; DO NOT run 158 tasks"
  stop_pid "$PID"
  rm -f "$LATEST_PID"
  exit 4
fi

echo "============================================================"
echo " A5 llama.cpp server READY (preflight PASS)"
echo " endpoint = http://127.0.0.1:${PORT}/v1"
echo " model    = ${ALIAS}"
echo " pid      = ${PID}   log=${LOG}"
echo " next: bash run/baize_posttrain_5run_eval.sh \\"
echo "         --endpoint http://127.0.0.1:${PORT}/v1 --model ${ALIAS} \\"
echo "         --label qwen35_q4km_llamacpp --run 1"
echo " stop: bash run/baize_posttrain_a5_llamacpp_serve.sh stop"
echo "============================================================"
exit 0
