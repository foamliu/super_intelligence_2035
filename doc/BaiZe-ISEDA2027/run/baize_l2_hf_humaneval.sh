#!/usr/bin/env bash
# HF transformers HumanEval eval (limit=20) on 160k ckpt
# Uses lm_eval --model hf (direct HF transformers, no llama.cpp)
# CPU only, OMP_NUM_THREADS=4, nice 19 — must not affect training
set -uo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=4
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ALLOW_CODE_EVAL=1
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"

MODEL_PATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_humaneval"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
LOG="/tmp/baize_l2_hf_humaneval.log"

mkdir -p "$OUTDIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting HF transformers HumanEval (limit=20)..." | tee "$LOG"

nice -n 19 "$PY" -m lm_eval \
  --model hf \
  --model_args "pretrained=$MODEL_PATH,trust_remote_code=True,dtype=bfloat16,max_length=2048" \
  --tasks humaneval \
  --limit 20 \
  --output_path "$OUTDIR" \
  --write_out \
  2>&1 | tee -a "$LOG"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done. Results in $OUTDIR" | tee -a "$LOG"
