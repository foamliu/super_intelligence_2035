#!/usr/bin/env bash
# Relaunch 5 Xmodel-2.5 Complex6 tasks with sdpa (config.json fixed)
# GPU 0-4 only; Xmodel-2 tasks on GPU 5-7 are still running from previous launch
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_ALLOW_CODE_EVAL=1

XM25_MODEL=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_final
XM25_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_history/eval_final

mkdir -p "$XM25_OUT"

echo "===== Xmodel-2.5 Complex6 relaunch START @ $(date '+%F %T') ====="

PIDS=()

# GPU 0: gsm8k (5-shot, bs=8)
CUDA_VISIBLE_DEVICES=0 "$PY" -m lm_eval \
  --model hf \
  --model_args "pretrained=${XM25_MODEL},dtype=bfloat16,trust_remote_code=True,attn_implementation=sdpa" \
  --tasks gsm8k --num_fewshot 5 --batch_size 8 \
  --output_path "${XM25_OUT}/cx_gsm8k" \
  > "${XM25_OUT}/cx_gsm8k.log" 2>&1 &
PIDS+=($!)

# GPU 1: hendrycks_math500 (4-shot, bs=4)
CUDA_VISIBLE_DEVICES=1 "$PY" -m lm_eval \
  --model hf \
  --model_args "pretrained=${XM25_MODEL},dtype=bfloat16,trust_remote_code=True,attn_implementation=sdpa" \
  --tasks hendrycks_math500 --num_fewshot 4 --batch_size 4 \
  --output_path "${XM25_OUT}/cx_hendrycks_math500" \
  > "${XM25_OUT}/cx_hendrycks_math500.log" 2>&1 &
PIDS+=($!)

# GPU 2: bbh_zeroshot (0-shot, bs=4)
CUDA_VISIBLE_DEVICES=2 "$PY" -m lm_eval \
  --model hf \
  --model_args "pretrained=${XM25_MODEL},dtype=bfloat16,trust_remote_code=True,attn_implementation=sdpa" \
  --tasks bbh_zeroshot --num_fewshot 0 --batch_size 4 \
  --output_path "${XM25_OUT}/cx_bbh_zeroshot" \
  > "${XM25_OUT}/cx_bbh_zeroshot.log" 2>&1 &
PIDS+=($!)

# GPU 3: humaneval (0-shot, bs=4)
CUDA_VISIBLE_DEVICES=3 "$PY" -m lm_eval \
  --model hf \
  --model_args "pretrained=${XM25_MODEL},dtype=bfloat16,trust_remote_code=True,attn_implementation=sdpa" \
  --tasks humaneval --num_fewshot 0 --batch_size 4 \
  --output_path "${XM25_OUT}/cx_humaneval" \
  > "${XM25_OUT}/cx_humaneval.log" 2>&1 &
PIDS+=($!)

# GPU 4: mbpp (3-shot, bs=4)
CUDA_VISIBLE_DEVICES=4 "$PY" -m lm_eval \
  --model hf \
  --model_args "pretrained=${XM25_MODEL},dtype=bfloat16,trust_remote_code=True,attn_implementation=sdpa" \
  --tasks mbpp --num_fewshot 3 --batch_size 4 \
  --output_path "${XM25_OUT}/cx_mbpp" \
  > "${XM25_OUT}/cx_mbpp.log" 2>&1 &
PIDS+=($!)

echo "  Launched 5 Xmodel-2.5 tasks on GPU 0-4. PIDs: ${PIDS[*]}"
echo "  Waiting for completion..."

for pid in "${PIDS[@]}"; do wait "$pid"; done
echo "  All Xmodel-2.5 tasks DONE @ $(date '+%T')"
echo "===== Xmodel-2.5 Complex6 relaunch COMPLETE @ $(date '+%F %T') ====="
