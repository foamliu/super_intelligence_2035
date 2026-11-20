#!/usr/bin/env bash
# Xmodel-2/2.5 single-GPU sequential eval: Common8 (zero-shot, raw acc + Avg)
# Usage: bash xmodel_eval_common8_single_gpu.sh <model_dir> <output_dir> <gpu_id> [trust_remote_code]
# Runs all 8 tasks sequentially on one GPU (~40 min per checkpoint)
set -uo pipefail

MODEL="${1:?Usage: $0 <model_dir> <output_dir> <gpu_id> [trust_remote_code]}"
OUT="${2:?Usage: $0 <model_dir> <output_dir> <gpu_id> [trust_remote_code]}"
GPU="${3:?Usage: $0 <model_dir> <output_dir> <gpu_id> [trust_remote_code]}"
TRUST="${4:-true}"

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0

BATCH=8
TAG=$(basename "$MODEL")
mkdir -p "$OUT"

# 8 commonsense tasks (same as xmodel_eval_common8.sh)
TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)

echo "START @ $(date '+%F %T') | GPU=$GPU | model=$TAG"

for task in "${TASKS[@]}"; do
  result_file="$OUT/results_${task}.json"
  if [ -f "$result_file" ]; then
    echo "[SKIP] $task already has results at $result_file"
    continue
  fi
  echo "[RUN] $task @ $(date '+%F %T')"
  CUDA_VISIBLE_DEVICES=$GPU /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=${TRUST}" \
    --tasks "$task" \
    --num_fewshot 0 \
    --batch_size "$BATCH" \
    --output_path "$OUT" \
    2>&1 | tail -5
  echo "[DONE] $task @ $(date '+%F %T')"
done

echo "ALL_DONE @ $(date '+%F %T') for $TAG on GPU$GPU"
