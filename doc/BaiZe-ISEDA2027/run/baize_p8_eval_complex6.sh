#!/usr/bin/env bash
# BaiZe P-8 final ckpt lm-eval: 复杂推理 6 集 (lm-eval default n-shot + Avg)
# 运维指令 2026-10-15: 用 P-8 final ckpt 跑 lm-eval 评测
# Tasks: gsm8k / hendrycks_math500 / mmlu / bbh_zeroshot / humaneval / mbpp
# HumanEval/MBPP: code execution enabled (HF_ALLOW_CODE_EVAL=1)
# Online mode with proxy (NOT offline — v1 offline caused failures)
set -uo pipefail

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_HUB_ENABLE_HF_TRANSFER=0
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_ALLOW_CODE_EVAL=1

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
MODEL="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8_adamw_decay/hf_iter_1149"
OUT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8_adamw_decay/lm_eval_complex6"
SUM="/tmp/baize_p8_complex6.sum"; : > "$SUM"
BATCH=4

mkdir -p "$OUT"

echo "===== P-8 Complex 6 eval START @ $(date '+%F %T') =====" >> "$SUM"
echo "  Model: $MODEL" >> "$SUM"
echo "  GPU0, online proxy=172.19.92.25:13128, HF_ALLOW_CODE_EVAL=1" >> "$SUM"

# 6 tasks with appropriate limits (matching v2 approach)
# gsm8k: full (default 5-shot), hendrycks_math500: 100, mmlu: 200,
# bbh_zeroshot: 100, humaneval: 164 (full), mbpp: 100
TASKS=(
  "gsm8k:0"
  "hendrycks_math500:100"
  "mmlu:200"
  "bbh_zeroshot:100"
  "humaneval:0"
  "mbpp:100"
)

for task_spec in "${TASKS[@]}"; do
  task="${task_spec%%:*}"
  limit="${task_spec##*:}"
  LOG="/tmp/baize_p8_c6_${task}.log"

  echo "  $task (limit=$limit) @ $(date '+%T')" >> "$SUM"

  CUDA_VISIBLE_DEVICES=0 $PY -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
    --tasks "$task" \
    --num_fewshot 0 \
    --batch_size "$BATCH" \
    --output_path "$OUT" \
    ${limit:+--limit "$limit"} \
    > "$LOG" 2>&1
  rc=$?

  if [ $rc -ne 0 ]; then
    echo "    rc=$rc  ❌ FAILED — last 5 lines:" >> "$SUM"
    tail -5 "$LOG" | sed 's/^/    /' >> "$SUM"
  else
    echo "    rc=0  ✅ done" >> "$SUM"
  fi
done

echo "===== P-8 Complex 6 eval END @ $(date '+%F %T') =====" >> "$SUM"
echo "Results in: $OUT"
