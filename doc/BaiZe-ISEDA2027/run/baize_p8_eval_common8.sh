#!/usr/bin/env bash
# BaiZe P-8 final ckpt lm-eval: 常识推理 8 集 (zero-shot, raw accuracy + Avg)
# 运维指令 2026-10-15: 用 P-8 final ckpt 跑 lm-eval 评测
# 8 GPU 并行, 每集独占一块 H100, ~5min
set -uo pipefail

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
# proxy for dataset downloads (if needed)
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0

MODEL="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8_adamw_decay/hf_iter_1149"
OUT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8_adamw_decay/lm_eval_common8"
BATCH=8

mkdir -p "$OUT"

# GPU -> task. hellaswag 最重（~40k 请求）独占 GPU0.
TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)

for gpu in 0 1 2 3 4 5 6 7; do
  task="${TASKS[$gpu]}"
  log="/tmp/p8_common8_${task}.log"
  CUDA_VISIBLE_DEVICES=$gpu setsid nohup python -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
    --tasks "$task" \
    --num_fewshot 0 \
    --batch_size "$BATCH" \
    --output_path "$OUT" \
    > "$log" 2>&1 &
  echo "launched GPU$gpu -> $task (pid $!, log $log)"
done

echo "ALL_LAUNCHED @ $(date '+%F %T')"
echo "Monitor: tail -f /tmp/p8_common8_*.log"
echo "Results will be in: $OUT"
