#!/usr/bin/env bash
# baize_llamacpp_full_eval.sh — 全量 llama.cpp 8 集评测 (多服务器并行)
#
# 用法: bash baize_llamacpp_full_eval.sh <hf_model_dir> <output_dir> [num_servers]
#
# 策略:
#   - 启动 N 个 llama-server 实例 (默认 4), 各 56 线程 8 slot
#   - 8 任务分配到 N 个服务器, 大任务 (hellaswag) 独占 1 个
#   - 各 gguf_lmeval_run.py 进程并行运行
#   - 合并结果
set -euo pipefail

MODEL="${1:?用法: bash baize_llamacpp_full_eval.sh <hf_model_dir> <output_dir> [num_servers]}"
OUT="${2:?缺 output_dir}"
NUM_SERVERS="${3:-4}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GGUF_DIR="/nas_train/app.e0031982/models/baize2b_gguf"
LLAMA_DIR="/nas_train/app.e0031982/tools/llama.cpp"
BIN="$LLAMA_DIR/build/bin/llama-server"

# 查找或生成 GGUF
GGUF="$GGUF_DIR/bz2b-$(basename "$MODEL" | sed 's/hf_iter_//')-f16.gguf"
if [[ ! -f "$GGUF" ]]; then
  echo "[full_eval] GGUF not found at $GGUF, converting..."
  bash "$SCRIPT_DIR/pretrain_cpu_eval_gguf/01_convert_hf_to_gguf.sh" "$MODEL" "$GGUF" f16
fi

echo "============================================================"
echo "  Full llama.cpp eval: model=$MODEL"
echo "  GGUF=$GGUF  servers=$NUM_SERVERS  output=$OUT"
echo "============================================================"

mkdir -p "$OUT"

# ── 启动 N 个 llama-server ──
THREADS_PER=$((224 / NUM_SERVERS))
if [[ $THREADS_PER -gt 56 ]]; then THREADS_PER=56; fi
BASE_PORT=8080

SERVER_PIDS=()
for i in $(seq 0 $((NUM_SERVERS - 1))); do
  PORT=$((BASE_PORT + i))
  PIDFILE="/tmp/llamacpp_server_${PORT}.pid"
  # 如果已有实例在跑, 先杀掉
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[full_eval] Killing existing server on port $PORT (pid=$(cat "$PIDFILE"))"
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
    sleep 2
  fi
  CTX=$((2048 * 8))
  echo "[full_eval] Starting server $i on port $PORT (threads=$THREADS_PER, parallel=8)"
  OMP_NUM_THREADS=1 setsid nice -n 19 "$BIN" \
    -m "$GGUF" -t "$THREADS_PER" -tb "$THREADS_PER" \
    -c "$CTX" --parallel 8 \
    --host 127.0.0.1 --port "$PORT" \
    --no-warmup --metrics --slots \
    --cache-prompt --temp 0 --top-k 1 --seed 1234 \
    > "/tmp/llamacpp_server_${PORT}.log" 2>&1 &
  echo $! > "$PIDFILE"
  SERVER_PIDS+=($!)
done

# 等待所有服务器就绪
echo "[full_eval] Waiting for servers to be ready..."
for i in $(seq 0 $((NUM_SERVERS - 1))); do
  PORT=$((BASE_PORT + i))
  for _ in $(seq 1 120); do
    if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
      echo "[full_eval] Server $i (port $PORT) READY"
      break
    fi
    sleep 1
  done
done

# ── 分配任务到服务器 ──
# hellaswag 最大 (10042 docs), 独占 server 0
# 其余 7 任务分配到 server 1..N-1
ALL_TASKS="arc_challenge arc_easy boolq hellaswag openbookqa piqa sciq winogrande"
declare -A TASK_SERVER
TASK_SERVER[hellaswag]=0

OTHER_TASKS="arc_challenge arc_easy boolq openbookqa piqa sciq winogrande"
idx=1
for task in $OTHER_TASKS; do
  TASK_SERVER[$task]=$((idx % NUM_SERVERS))
  idx=$((idx + 1))
done

echo "[full_eval] Task assignment:"
for task in $ALL_TASKS; do
  echo "  $task -> server ${TASK_SERVER[$task]} (port $((BASE_PORT + ${TASK_SERVER[$task]})))"
done

# ── 启动评测进程 ──
EVAL_PIDS=()
T_START=$(date +%s)

for task in $ALL_TASKS; do
  server_idx=${TASK_SERVER[$task]}
  PORT=$((BASE_PORT + server_idx))
  task_out="$OUT/${task}"
  mkdir -p "$task_out"
  echo "[full_eval] Launching eval for $task on port $PORT -> $task_out"

  export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
  export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
  export HF_HOME="/nas_train/app.e0031982/.cache"
  export HF_DATASETS_OFFLINE=1
  export HF_HUB_OFFLINE=1

  setsid bash -c "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python '$SCRIPT_DIR/pretrain_cpu_eval_gguf/gguf_lmeval_run.py' \
    --base-url http://127.0.0.1:${PORT} \
    --hf-dir '$MODEL' \
    --output '$task_out' \
    --tasks '$task' \
    --parallel 8 \
    --batch-size 32 \
    --gguf '$GGUF'" > "$task_out.log" 2>&1 &
  EVAL_PIDS+=($!)
done

echo "[full_eval] All ${#EVAL_PIDS[@]} eval processes launched: ${EVAL_PIDS[*]}"
echo "[full_eval] Waiting for completion..."

FAIL=0
for i in "${!EVAL_PIDS[@]}"; do
  if ! wait "${EVAL_PIDS[$i]}"; then
    echo "[full_eval] Process $i (PID ${EVAL_PIDS[$i]}) FAILED"
    FAIL=$((FAIL+1))
  fi
done

T_END=$(date +%s)
ELAPSED=$((T_END - T_START))
echo "[full_eval] All done in ${ELAPSED}s ($(echo "scale=2; $ELAPSED/3600" | bc) hours). Failures: $FAIL"

# ── 合并结果 ──
echo "[full_eval] Merging results..."
/nas_train/app.e0031982/miniforge3/envs/py310/bin/python "$SCRIPT_DIR/merge_parallel_results.py" "$OUT"

# ── 清理服务器 ──
echo "[full_eval] Stopping servers..."
for pid in "${SERVER_PIDS[@]}"; do
  kill "$pid" 2>/dev/null || true
done

echo "[full_eval] DONE. Results at $OUT/results.json"
