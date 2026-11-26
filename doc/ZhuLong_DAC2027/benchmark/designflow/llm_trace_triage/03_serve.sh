#!/usr/bin/env bash
# 03_serve.sh — 起 llama-server（Qwen3.5-0.8B Q8_0），供 trace triage 调用。
#
# 用法: bash 03_serve.sh [port] [threads] [parallel]
# 默认: port=18081 threads=32 parallel=2（64 核机器；不要占 8090）
#
# 前置（缺则自动调用）:
#   bash doc/ZhuLong_DAC2027/run/setup_llamacpp_qwen35.sh
set -euo pipefail

PORT="${1:-18081}"
THREADS="${2:-32}"
PARALLEL="${3:-2}"
LLAMA_DIR="${LLAMA_DIR:-$HOME/tools/llama.cpp}"
MODEL="${MODEL:-$HOME/models/Qwen3.5-0.8B/Qwen3.5-0.8B-Q8_0.gguf}"
LOG="${LOG:-/tmp/llama_triage_${PORT}.log}"
PIDFILE="/tmp/llama_triage_${PORT}.pid"

HERE="$(cd "$(dirname "$0")" && pwd)"
SETUP="$HERE/../../../run/setup_llamacpp_qwen35.sh"

if [[ ! -x "$LLAMA_DIR/build/bin/llama-server" ]]; then
  echo "[triage] llama-server 缺失 -> 调用 setup（build+download+convert）"
  bash "$SETUP" || { echo "FAIL: setup 失败"; exit 1; }
fi
if [[ ! -f "$MODEL" ]]; then
  if [[ -f "$HOME/models/Qwen3.5-0.8B/Qwen3.5-0.8B-f16.gguf" ]]; then
    MODEL="$HOME/models/Qwen3.5-0.8B/Qwen3.5-0.8B-f16.gguf"
  else
    echo "FAIL: 缺 $MODEL（先跑 setup）"; exit 1
  fi
fi

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "[triage] 已有实例 pid=$(cat "$PIDFILE")"
else
  CTX=$((2048 * PARALLEL))
  OMP_NUM_THREADS=1 setsid nice -n 19 "$LLAMA_DIR/build/bin/llama-server" \
    -m "$MODEL" -t "$THREADS" -tb "$THREADS" \
    -c "$CTX" --parallel "$PARALLEL" \
    --host 127.0.0.1 --port "$PORT" \
    --no-warmup --metrics --slots --cache-prompt \
    --temp 0 --top-k 1 --seed 1234 \
    >"$LOG" 2>&1 &
  echo $! > "$PIDFILE"
  echo "[triage] started pid=$(cat "$PIDFILE") model=$MODEL log=$LOG"
fi

for _ in $(seq 1 180); do
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "[triage] READY http://127.0.0.1:${PORT}"
    exit 0
  fi
  sleep 1
done
echo "[triage] FAIL: 180s 未就绪"; tail -40 "$LOG"; exit 1
