#!/usr/bin/env bash
# baize_cpu_lmeval_parallel.sh — 任务级多进程并行 + hellaswag 分片
#
# 用法: bash baize_cpu_lmeval_parallel.sh <hf_model_dir> <output_dir> [--limit N]
#
# 策略:
#   - hellaswag (10042 docs, 55% 请求) 拆成 4 片, 各 ~2511 docs
#   - 其余 7 任务各 1 进程
#   - 共 11 进程 × 16 线程 = 176 核 (224 核机器安全)
#   - 每进程 nice -n 19, 不抢 S1 GPU 训练
set -euo pipefail

MODEL="${1:?用法: bash baize_cpu_lmeval_parallel.sh <hf_model_dir> <output_dir> [--limit N]}"
OUT="${2:?缺 output_dir}"
shift 2

LIMIT_ARG=""
if [[ "$1" == "--limit" ]]; then
  LIMIT_ARG="--limit $2"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
THREADS=16

# hellaswag 分片 (10042 docs → 4 chunks: 2511+2511+2511+2509)
declare -A HS_RANGES=(
  [0]="0-2510"
  [1]="2511-5021"
  [2]="5022-7532"
  [3]="7533-10041"
)

OTHER_TASKS="arc_challenge arc_easy boolq openbookqa piqa sciq winogrande"

echo "============================================================"
echo "  Parallel CPU lm_eval: model=$MODEL"
echo "  output=$OUT  threads_per_proc=$THREADS  procs=11"
echo "  hellaswag: 4 chunks  +  7 single-task procs"
echo "============================================================"

mkdir -p "$OUT"

# 生成 hellaswag 分片的 samples JSON
gen_samples() {
  local start=$1 end=$2
  python3 -c "
import json
idxs=list(range($start,$end+1))
print(json.dumps({'hellaswag':idxs}))
"
}

PIDS=()
T_START=$(date +%s)

# 启动 hellaswag 分片进程
for chunk in 0 1 2 3; do
  IFS='-' read -r start end <<< "${HS_RANGES[$chunk]}"
  samples_json=$(gen_samples "$start" "$end")
  chunk_out="$OUT/hellaswag_chunk${chunk}"
  echo "[parallel]Launching hellaswag chunk $chunk: docs[$start-$end] -> $chunk_out"
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS \
    nice -n 19 bash "$SCRIPT_DIR/baize_cpu_lmeval.sh" \
    "$MODEL" "$chunk_out" --tasks hellaswag --samples "$samples_json" $LIMIT_ARG \
    > "$chunk_out.log" 2>&1 &
  PIDS+=($!)
done

# 启动其余 7 任务的独立进程
for task in $OTHER_TASKS; do
  task_out="$OUT/${task}"
  echo "[parallel] Launching $task -> $task_out"
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS \
    nice -n 19 bash "$SCRIPT_DIR/baize_cpu_lmeval.sh" \
    "$MODEL" "$task_out" --tasks "$task" $LIMIT_ARG \
    > "$task_out.log" 2>&1 &
  PIDS+=($!)
done

echo "[parallel] All ${#PIDS[@]} processes launched: ${PIDS[*]}"
echo "[parallel] Waiting for completion..."

# 等待所有进程
FAIL=0
for i in "${!PIDS[@]}"; do
  if ! wait "${PIDS[$i]}"; then
    echo "[parallel] Process $i (PID ${PIDS[$i]}) FAILED"
    FAIL=$((FAIL+1))
  fi
done

T_END=$(date +%s)
ELAPSED=$((T_END - T_START))
echo "[parallel] All done in ${ELAPSED}s (${ELAPSED}/3600 = $(echo "scale=2; $ELAPSED/3600" | bc) hours). Failures: $FAIL"

# 合并结果
echo "[parallel] Merging results..."
/nas_train/app.e0031982/miniforge3/envs/py310/bin/python "$SCRIPT_DIR/merge_parallel_results.py" "$OUT"

echo "[parallel] DONE. Merged results at $OUT/results.json"
