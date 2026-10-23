#!/bin/bash
# CX6 fix eval for decay-5000: re-run 5 crashed CX6 tasks with sdpa attention
# gsm8k/math500/bbh crashed on flash_attn varlen_fwd; humaneval/mbpp need HF_ALLOW_CODE_EVAL=1
set -uo pipefail

MODEL=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/Xmodel-2.5-code/out/hf_decay_5000_final
OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/eval_decay_5000_final
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

# Environment — must match baize_decay5000_eval_14.sh
unset PYTHONPATH
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_ALLOW_CODE_EVAL=1

MARGS="pretrained=${MODEL},dtype=bfloat16,trust_remote_code=True"

echo "===== CX6 sdpa fix START @ $(date '+%Y-%m-%d %H:%M:%S') ====="

# GPU0: gsm8k (5-shot, generate)
CUDA_VISIBLE_DEVICES=0 ${PY} -m lm_eval --model hf \
  --model_args "${MARGS}" \
  --tasks gsm8k --num_fewshot 5 --batch_size 8 \
  --output_path ${OUT}/cx_sdpa_gsm8k > ${OUT}/cx_sdpa_gsm8k.log 2>&1 &
PID_GSM=$!

# GPU1: hendrycks_math500 (4-shot, generate)
CUDA_VISIBLE_DEVICES=1 ${PY} -m lm_eval --model hf \
  --model_args "${MARGS}" \
  --tasks hendrycks_math500 --num_fewshot 4 --batch_size 4 \
  --output_path ${OUT}/cx_sdpa_math500 > ${OUT}/cx_sdpa_math500.log 2>&1 &
PID_MATH=$!

# GPU3: bbh_zeroshot (0-shot, generate)
CUDA_VISIBLE_DEVICES=3 ${PY} -m lm_eval --model hf \
  --model_args "${MARGS}" \
  --tasks bbh_zeroshot --num_fewshot 0 --batch_size 4 \
  --output_path ${OUT}/cx_sdpa_bbh > ${OUT}/cx_sdpa_bbh.log 2>&1 &
PID_BBH=$!

# GPU4: humaneval (0-shot, generate + code eval via env)
CUDA_VISIBLE_DEVICES=4 ${PY} -m lm_eval --model hf \
  --model_args "${MARGS}" \
  --tasks humaneval --num_fewshot 0 --batch_size 4 \
  --output_path ${OUT}/cx_sdpa_humaneval > ${OUT}/cx_sdpa_humaneval.log 2>&1 &
PID_HUM=$!

# GPU5: mbpp (3-shot, generate + code eval via env)
CUDA_VISIBLE_DEVICES=5 ${PY} -m lm_eval --model hf \
  --model_args "${MARGS}" \
  --tasks mbpp --num_fewshot 3 --batch_size 4 \
  --output_path ${OUT}/cx_sdpa_mbpp > ${OUT}/cx_sdpa_mbpp.log 2>&1 &
PID_MBP=$!

echo "  launched GPU0 -> gsm8k (pid ${PID_GSM})"
echo "  launched GPU1 -> hendrycks_math500 (pid ${PID_MATH})"
echo "  launched GPU3 -> bbh_zeroshot (pid ${PID_BBH})"
echo "  launched GPU4 -> humaneval (pid ${PID_HUM})"
echo "  launched GPU5 -> mbpp (pid ${PID_MBP})"
echo "  Waiting for CX6 sdpa fix..."

wait ${PID_GSM} && echo "  gsm8k DONE" || echo "  gsm8k FAILED"
wait ${PID_MATH} && echo "  hendrycks_math500 DONE" || echo "  hendrycks_math500 FAILED"
wait ${PID_BBH} && echo "  bbh_zeroshot DONE" || echo "  bbh_zeroshot FAILED"
wait ${PID_HUM} && echo "  humaneval DONE" || echo "  humaneval FAILED"
wait ${PID_MBP} && echo "  mbpp DONE" || echo "  mbpp FAILED"

echo "===== CX6 sdpa fix DONE @ $(date '+%Y-%m-%d %H:%M:%S') ====="
