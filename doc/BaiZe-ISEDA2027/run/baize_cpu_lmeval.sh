#!/usr/bin/env bash
# CPU 评测脚本 — lm_eval 8 集 zero-shot（纯 CPU，不碰 GPU）
#
# 用法:  bash baize_cpu_lmeval.sh <hf_model_dir> <output_dir> [--limit N] [--tasks T1,T2]
#   <hf_model_dir>  HF 格式模型目录（如 hf_iter_10000）
#   <output_dir>    结果输出目录
#   --limit N       可选，只跑 N 个样本（冒烟用）
#   --tasks T1,T2   可选，覆盖默认 8 集
#
# 环境：PYTHONPATH 前置 p6_tf5（transformers 5.17 含 NemotronHForCausalLM）
#       py310 env python（lm_eval）
#       CUDA_VISIBLE_DEVICES="" 强制纯 CPU
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "用法: bash baize_cpu_lmeval.sh <hf_model_dir> <output_dir> [--limit N] [--tasks T1,T2]"
  exit 1
fi

MODEL="$1"
OUT="$2"
shift 2

TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
LIMIT=""
DTYPE="float32"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)  LIMIT="--limit $2"; shift 2 ;;
    --tasks)  TASKS="$2"; shift 2 ;;
    --dtype)  DTYPE="$2"; shift 2 ;;
    *)        echo "Unknown arg: $1"; exit 1 ;;
  esac
done

mkdir -p "$OUT"

# 强制纯 CPU + 离线模式
export CUDA_VISIBLE_DEVICES=""
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-4}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================================"
echo "  CPU lm_eval . model=$MODEL"
echo "  output=$OUT  tasks=$TASKS  limit=${LIMIT:-full}  dtype=$DTYPE"
echo "  OMP=$OMP_NUM_THREADS  CUDA_VISIBLE_DEVICES=(empty)"
echo "============================================================"

exec /nas_train/app.e0031982/miniforge3/envs/py310/bin/python "$SCRIPT_DIR/cpu_lmeval_run.py" \
  "$MODEL" \
  "$OUT" \
  --tasks "$TASKS" \
  --dtype "$DTYPE" \
  --num_fewshot 0 \
  --batch_size 1 \
  $LIMIT