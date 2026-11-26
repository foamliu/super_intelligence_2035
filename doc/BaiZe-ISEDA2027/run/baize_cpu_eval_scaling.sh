#!/usr/bin/env bash
# baize_cpu_eval_scaling.sh — 11w 检查点 CPU 评测线程/batch 扫描编排
#
# 用法: bash baize_cpu_eval_scaling.sh <ckpt_iter> <threads> <batch_size> [--limit N] [--tasks T1,T2]
#
#   <ckpt_iter>    检查点迭代号（如 112000）
#   <threads>      OMP_NUM_THREADS（≤80）
#   <batch_size>   lm_eval batch_size
#   --limit N      可选，只跑 N 个样本（吞吐探测用）
#   --tasks T1,T2  可选，覆盖默认 8 集
#
# 硬约束（运维令 2026-11-07）：
#   - CUDA_VISIBLE_DEVICES="" 纯 CPU
#   - OMP_NUM_THREADS ≤ 80（不许跑满 224 核）
#   - nice -n 19
#   - 不碰 GPU / 不影响 S1 训练
#   - 单进程 %cpu > 8000%（=80 核）立杀
#
# 结果落 lm_eval_results/hf_iter_<iter>_t<threads>_b<batch>/
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "用法: bash baize_cpu_eval_scaling.sh <ckpt_iter> <threads> <batch_size> [--limit N] [--tasks T1,T2]"
  exit 1
fi

CKPT_ITER="$1"
THREADS="$2"
BATCH_SIZE="$3"
shift 3

LIMIT_ARG=""
TASKS_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT_ARG="--limit $2"; shift 2 ;;
    --tasks) TASKS_ARG="--tasks $2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
MODEL="${BASE}/hf_iter_${CKPT_ITER}"

# 结果目录标签：t<threads>_b<batch>，如有 limit 加 _lim<N>
TAG="t${THREADS}_b${BATCH_SIZE}"
if [[ -n "$LIMIT_ARG" ]]; then
  LIM_NUM="${LIMIT_ARG##* }"
  TAG="${TAG}_lim${LIM_NUM}"
fi
OUT="${BASE}/lm_eval_results/hf_iter_${CKPT_ITER}_${TAG}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -d "$MODEL" ]]; then
  echo "FAIL: HF model dir not found: $MODEL"
  exit 1
fi

mkdir -p "$OUT"

# 记录开始时间
START_EPOCH=$(date +%s)
START_TS=$(date '+%F %T')

echo "============================================================"
echo "  baize_cpu_eval_scaling.sh"
echo "  ckpt=${CKPT_ITER}  threads=${THREADS}  batch=${BATCH_SIZE}"
echo "  model: $MODEL"
echo "  out:   $OUT"
echo "  limit: ${LIMIT_ARG:-full}"
echo "  start: ${START_TS}"
echo "============================================================"

# 设置线程数（由 wrapper 控制，不依赖 baize_cpu_lmeval.sh 的默认值）
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS="$THREADS"
export MKL_NUM_THREADS="$THREADS"

# 运行评测，同时捕获 stderr 到日志文件
LOG_FILE="${OUT}/eval.log"
bash "$SCRIPT_DIR/baize_cpu_lmeval.sh" "$MODEL" "$OUT" \
  --batch_size "$BATCH_SIZE" \
  $LIMIT_ARG $TASKS_ARG 2>&1 | tee "$LOG_FILE"

# 记录结束时间和 wall-clock
END_EPOCH=$(date +%s)
END_TS=$(date '+%F %T')
WALL_SEC=$((END_EPOCH - START_EPOCH))
WALL_MIN=$((WALL_SEC / 60))

echo "============================================================"
echo "  DONE · ckpt=${CKPT_ITER} t=${THREADS} b=${BATCH_SIZE}"
echo "  wall-clock: ${WALL_SEC}s (${WALL_MIN}min)"
echo "  end: ${END_TS}"
echo "============================================================"

# 将 timing 元数据写入单独文件
cat > "${OUT}/timing.json" <<EOF
{
  "ckpt_iter": "${CKPT_ITER}",
  "threads": ${THREADS},
  "batch_size": ${BATCH_SIZE},
  "limit": "${LIMIT_ARG:-full}",
  "start_ts": "${START_TS}",
  "end_ts": "${END_TS}",
  "wall_sec": ${WALL_SEC},
  "wall_min": ${WALL_MIN}
}
EOF

echo "timing.json written to ${OUT}/timing.json"
