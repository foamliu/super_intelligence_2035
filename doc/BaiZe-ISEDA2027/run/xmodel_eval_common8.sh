#!/usr/bin/env bash
# Xmodel-2 / Xmodel-2.5 checkpoint lm-eval: 常识推理 8 集 (zero-shot, raw accuracy + Avg)
# Usage: bash xmodel_eval_common8.sh <model_dir> <output_dir> [trust_remote_code]
# 8 GPU 并行, 每集独占一块 H100, ~5min per checkpoint
set -uo pipefail

MODEL="${1:?Usage: $0 <model_dir> <output_dir> [trust_remote_code]}"
OUT="${2:?Usage: $0 <model_dir> <output_dir> [trust_remote_code]}"
TRUST="${3:-true}"

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

# GPU -> task. hellaswag 最重独占 GPU0.
TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)

for gpu in 0 1 2 3 4 5 6 7; do
  task="${TASKS[$gpu]}"
  log="/tmp/xmodel_common8_${TAG}_${task}.log"
  CUDA_VISIBLE_DEVICES=$gpu setsid nohup /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=${TRUST}" \
    --tasks "$task" \
    --num_fewshot 0 \
    --batch_size "$BATCH" \
    --output_path "$OUT" \
    > "$log" 2>&1 &
  echo "launched GPU$gpu -> $task (pid $!, log $log)"
done

echo "ALL_LAUNCHED @ $(date '+%F %T') for $TAG"
echo "Monitor: tail -f /tmp/xmodel_common8_${TAG}_*.log"
echo "Results will be in: $OUT"
