#!/usr/bin/env bash
# 03_serve_llama_server.sh — 起 llama-server（CPU，低优先级，prompt cache）
#
# 用法:
#   bash 03_serve_llama_server.sh <model.gguf> [port] [threads] [parallel]
#
# 默认: port=8080 threads=32 parallel=2 ctx/slot=2048
#
# 可覆盖环境变量:
#   LLAMA_DIR, CTX_PER_SLOT, LOG, SEED, WAIT_SECONDS
#
# 设计:
#   - nice -n 19 + OMP_NUM_THREADS=1：不抢 S1 / 其它 CPU 评测
#   - --cache-prompt：同一题 4 个候选共享前缀，靠 slot 复用
#   - --temp 0 --top-k 1：打分只需要确定性，不需要采样多样性
#   - 后台运行；PID 写 /tmp/llamacpp_server_<port>.pid
set -euo pipefail

GGUF="${1:?用法: bash 03_serve_llama_server.sh <model.gguf> [port] [threads] [parallel]}"
PORT="${2:-8080}"
THREADS="${3:-32}"
PARALLEL="${4:-2}"

LLAMA_DIR="${LLAMA_DIR:-/nas_train/app.e0031982/tools/llama.cpp}"
BIN="$LLAMA_DIR/build/bin/llama-server"
CTX_PER_SLOT="${CTX_PER_SLOT:-2048}"
SEED="${SEED:-1234}"
WAIT_SECONDS="${WAIT_SECONDS:-120}"
LOG="${LOG:-/tmp/llamacpp_server_${PORT}.log}"
PIDFILE="/tmp/llamacpp_server_${PORT}.pid"

[[ -x "$BIN" ]] || { echo "FAIL: 缺 $BIN（先跑 00_build_llamacpp.sh）" >&2; exit 1; }
[[ -f "$GGUF" ]] || { echo "FAIL: 缺模型 $GGUF" >&2; exit 1; }

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "[serve] 已有实例在跑: pid=$(cat "$PIDFILE") port=$PORT"
else
  CTX=$(( CTX_PER_SLOT * PARALLEL ))
  echo "[serve] model=$GGUF"
  echo "[serve] port=$PORT threads=$THREADS parallel=$PARALLEL ctx/slot=$CTX_PER_SLOT (total $CTX)"
  OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}" \
    setsid nice -n 19 "$BIN" \
      -m "$GGUF" \
      -t "$THREADS" -tb "$THREADS" \
      -c "$CTX" --parallel "$PARALLEL" \
      --host 127.0.0.1 --port "$PORT" \
      --no-warmup --metrics --slots \
      --cache-prompt --temp 0 --top-k 1 --seed "$SEED" \
      >"$LOG" 2>&1 &
  echo $! > "$PIDFILE"
  echo "[serve] started pid=$(cat "$PIDFILE") log=$LOG"
fi

# 等待 /health 就绪
for _ in $(seq 1 "$WAIT_SECONDS"); do
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "[serve] READY http://127.0.0.1:${PORT}"
    exit 0
  fi
  sleep 1
done

echo "[serve] FAIL: ${WAIT_SECONDS}s 内未就绪，日志尾部：" >&2
tail -50 "$LOG" >&2 || true
exit 1
