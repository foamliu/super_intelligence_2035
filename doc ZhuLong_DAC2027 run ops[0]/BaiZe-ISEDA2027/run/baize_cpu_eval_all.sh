#!/usr/bin/env bash
# baize_cpu_eval_all.sh — 5 ckpt × 8 集 CPU 评测编排（limit=100，纯 CPU，降载）
#
# 用法: bash baize_cpu_eval_all.sh <ckpt_iter> [--limit N]
#   单个 ckpt 跑 8 集，结果落 lm_eval_results/hf_iter_<iter>/
#
# 硬约束（运维令 19:51）：
#   - CUDA_VISIBLE_DEVICES="" 纯 CPU
#   - OMP_NUM_THREADS≤8
#   - nice -n 19
#   - 不碰 GPU / 不影响 S1 训练
#
# 环境：py310 + PYTHONPATH=p6_tf5 (transformers 5.17 NemotronHForCausalLM)
set -euo pipefail

CKPT_ITER="${1:?用法: bash baize_cpu_eval_all.sh <ckpt_iter> [--limit N]}"
shift

LIMIT_ARG=""
if [[ "${1:-}" == "--limit" ]]; then LIMIT_ARG="--limit $2"; shift 2; fi

BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
MODEL="${BASE}/hf_iter_${CKPT_ITER}"
OUT="${BASE}/lm_eval_results/hf_iter_${CKPT_ITER}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -d "$MODEL" ]]; then
  echo "FAIL: HF model dir not found: $MODEL"
  exit 1
fi

mkdir -p "$OUT"

echo "============================================================"
echo "  baize_cpu_eval_all.sh · ckpt=${CKPT_ITER}"
echo "  model: $MODEL"
echo "  out:   $OUT"
echo "  limit: ${LIMIT_ARG:-full}"
echo "  start: $(date '+%F %T')"
echo "============================================================"

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8

bash "$SCRIPT_DIR/baize_cpu_lmeval.sh" "$MODEL" "$OUT" $LIMIT_ARG

echo "============================================================"
echo "  DONE · ckpt=${CKPT_ITER} · $(date '+%F %T')"
echo "============================================================"
