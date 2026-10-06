#!/usr/bin/env bash
# P-6 全量评测启动器：8 个评测集 × 8 GPU 并行（每集独占一块 H100）。
#
# 依赖：baize_p6_lmeval.sh 已验证整条链路（HFLM 加载 nemotron_h / hf-mirror 下载
#       8 集 / loglikelihood 前向），本脚本只做"全量 + 8 路并行"。
# 结果写到 $OUT/<model>/results_*.json（带时间戳，天然无碰撞）。
set -euo pipefail

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
# 缓解 CUDA 显存碎片化（sciq 曾因 fragmentation OOM）。
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

MODEL="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/hf_nemotron_h"
OUT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/lm_eval_results"
BATCH=8

mkdir -p "$OUT"

# GPU -> task。hellaswag 最重（~40k 请求）独占 GPU0。
TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)

for gpu in 0 1 2 3 4 5 6 7; do
  task="${TASKS[$gpu]}"
  log="/tmp/p6_lmlog_${task}.log"
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

echo "ALL_LAUNCHED"