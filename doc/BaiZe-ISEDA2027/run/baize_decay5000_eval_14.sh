#!/usr/bin/env bash
# BaiZe decay-5000 14-benchmark evaluation (adapted from baize_p8_eval_14.sh)
# Changes: no p6_tf5 PYTHONPATH (broken sklearn from harness), trust_remote_code=True
# Usage: bash baize_decay5000_eval_14.sh <hf_model_path> <output_dir> [batch_size]
# Designed for 8×H100, 1.35B model fits on single GPU → data-parallel by task.
set -uo pipefail

MODEL="${1:?Usage: bash baize_decay5000_eval_14.sh <hf_model_path> <output_dir> [batch_size]}"
OUT="${2:?output_dir required}"
BATCH="${3:-8}"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

# DO NOT add p6_tf5 to PYTHONPATH — its transformers imports a broken sklearn
# from /dev/shm/harness_work (harness agent pollution). Use py310's transformers 4.56.1.
unset PYTHONPATH
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0

mkdir -p "$OUT"
SUM="$OUT/eval_summary.txt"
: > "$SUM"
echo "===== decay-5000 14-benchmark eval START @ $(date '+%F %T') =====" >> "$SUM"
echo "  MODEL=$MODEL" >> "$SUM"
echo "  OUT=$OUT" >> "$SUM"
echo "  BATCH=$BATCH" >> "$SUM"

# ── Phase 1: Common sense 8 (zero-shot) — 8 GPUs in parallel ──
echo "" >> "$SUM"
echo "===== Phase 1: Common sense 8 (zero-shot, 8 GPU parallel) @ $(date '+%T') =====" >> "$SUM"

CS_TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)

for gpu in 0 1 2 3 4 5 6 7; do
  task="${CS_TASKS[$gpu]}"
  log="$OUT/cs_${task}.log"
  CUDA_VISIBLE_DEVICES=$gpu setsid nohup $PY -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=True" \
    --tasks "$task" \
    --num_fewshot 0 \
    --batch_size "$BATCH" \
    --output_path "$OUT/cs_${task}" \
    > "$log" 2>&1 &
  echo "  launched GPU$gpu -> $task (pid $!)" >> "$SUM"
done

echo "  Waiting for Phase 1 (common sense 8)..." >> "$SUM"
wait
echo "  Phase 1 DONE @ $(date '+%T')" >> "$SUM"

# ── Phase 2: Complex 6 (lm-eval default n-shot) — 6 GPUs in parallel ──
echo "" >> "$SUM"
echo "===== Phase 2: Complex 6 (default n-shot, 6 GPU parallel) @ $(date '+%T') =====" >> "$SUM"

# Task names matching P-5b complex6 eval
# gsm8k: 5-shot (lm_eval default), hendrycks_math500: 4-shot, mmlu: 5-shot
# bbh_zeroshot: 0-shot, humaneval: 0-shot, mbpp: 3-shot
CX_TASKS=(gsm8k hendrycks_math500 mmlu bbh_zeroshot humaneval mbpp)
CX_SHOTS=(5     4                 5    0            0         3)
CX_BATCH=(8     4                 8    4            4         4)

for i in 0 1 2 3 4 5; do
  gpu=$i
  task="${CX_TASKS[$i]}"
  shot="${CX_SHOTS[$i]}"
  cbatch="${CX_BATCH[$i]}"
  log="$OUT/cx_${task}.log"
  CUDA_VISIBLE_DEVICES=$gpu setsid nohup $PY -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=True" \
    --tasks "$task" \
    --num_fewshot "$shot" \
    --batch_size "$cbatch" \
    --output_path "$OUT/cx_${task}" \
    > "$log" 2>&1 &
  echo "  launched GPU$gpu -> $task (shot=$shot, batch=$cbatch, pid $!)" >> "$SUM"
done

echo "  Waiting for Phase 2 (complex 6)..." >> "$SUM"
wait
echo "  Phase 2 DONE @ $(date '+%T')" >> "$SUM"

# ── Phase 3: Collect results ──
echo "" >> "$SUM"
echo "===== Phase 3: Collecting results @ $(date '+%T') =====" >> "$SUM"
$PY "$RUN_DIR/baize_p8_eval_collect.py" --out "$OUT" >> "$SUM" 2>&1

echo "" >> "$SUM"
echo "===== decay-5000 14-benchmark eval ALL DONE @ $(date '+%F %T') =====" >> "$SUM"
echo "Results in: $OUT" >> "$SUM"