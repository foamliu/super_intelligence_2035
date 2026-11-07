#!/usr/bin/env bash
# baize_llamacpp_full_eval.sh — 全量 llama.cpp 8 集评测 (多服务器并行)
#
# 用法: bash baize_llamacpp_full_eval.sh <hf_model_dir> <output_dir> [num_servers] [threads_per]
#
# 策略 (2026-11-07 修订):
#   - 启动 N 个 llama-server 实例 (默认 8 = 每任务独占 1 个), 各 16 线程 8 slot
#   - ⚠️ 线程数固定 16: 探测矩阵证明 16 线程饱和 (#1570),
#     56/80 线程因 Mamba2 SSM 顺序扫描反而更慢
#   - 8 任务各自独占 1 个 server, 不共享 → 无争用
#   - 各 gguf_lmeval_run.py 进程并行运行
#   - 合并结果 + 记录每任务耗时
set -euo pipefail

MODEL="${1:?用法: bash baize_llamacpp_full_eval.sh <hf_model_dir> <output_dir> [num_servers] [threads_per]}"
OUT="${2:?缺 output_dir}"
NUM_SERVERS="${3:-8}"
THREADS_PER="${4:-16}"

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
echo "  GGUF=$GGUF  servers=$NUM_SERVERS  threads=$THREADS_PER  output=$OUT"
echo "============================================================"

mkdir -p "$OUT"

# ── 启动 N 个 llama-server ──
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
# 8 任务 = 8 服务器, 各独占; 任务顺序按 request 数降序排列
# 以便最先启动最大任务 (hellaswag)
ALL_TASKS="hellaswag arc_easy boolq sciq piqa arc_challenge winogrande openbookqa"
declare -A TASK_SERVER
idx=0
for task in $ALL_TASKS; do
  TASK_SERVER[$task]=$idx
  idx=$((idx + 1))
done

echo "[full_eval] Task assignment (1 task per server, threads=$THREADS_PER):"
for task in $ALL_TASKS; do
  echo "  $task -> server ${TASK_SERVER[$task]} (port $((BASE_PORT + ${TASK_SERVER[$task]})))"
done

# ── 启动评测进程 ──
EVAL_PIDS=()
declare -A EVAL_TASK_NAMES
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
  EVAL_TASK_NAMES[$!]=$task
done

echo "[full_eval] All ${#EVAL_PIDS[@]} eval processes launched: ${EVAL_PIDS[*]}"
echo "[full_eval] Waiting for completion..."

FAIL=0
for i in "${!EVAL_PIDS[@]}"; do
  pid="${EVAL_PIDS[$i]}"
  task_name="${EVAL_TASK_NAMES[$pid]}"
  t_wait_start=$(date +%s)
  if ! wait "$pid"; then
    echo "[full_eval] Process $i ($task_name PID $pid) FAILED"
    FAIL=$((FAIL+1))
  else
    t_wait_end=$(date +%s)
    task_elapsed=$((t_wait_end - T_START))
    echo "[full_eval] $task_name DONE (wall=${task_elapsed}s from eval start)"
  fi
done

T_END=$(date +%s)
ELAPSED=$((T_END - T_START))
echo "[full_eval] All done in ${ELAPSED}s ($(echo "scale=2; $ELAPSED/3600" | bc) hours). Failures: $FAIL"

# ── 写入 END 标记 (供 gen_eval_speedup_report.py 读取耗时) ──
MARKER_FILE="${FULL_EVAL_MARKER:-/tmp/baize_full_eval_v4.marker}"
if [[ -f "$MARKER_FILE" ]]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') END epoch=${T_END} rc=${FAIL}" >> "$MARKER_FILE"
  echo "[full_eval] END marker written to $MARKER_FILE"
fi

# ── 合并结果 ──
echo "[full_eval] Merging results..."
/nas_train/app.e0031982/miniforge3/envs/py310/bin/python "$SCRIPT_DIR/merge_parallel_results.py" "$OUT"

# ── 清理服务器 ──
echo "[full_eval] Stopping servers..."
for pid in "${SERVER_PIDS[@]}"; do
  kill "$pid" 2>/dev/null || true
done

echo "[full_eval] DONE. Results at $OUT/results.json"
