#!/usr/bin/env bash
# Smoke test: verify lm_eval pipeline works with P-5b HF checkpoint
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
MODEL=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/hf_iter_0156

echo "=== Smoke test: arc_challenge --limit 10 ==="
CUDA_VISIBLE_DEVICES=0 $PY -m lm_eval \
  --model hf \
  --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
  --tasks arc_challenge \
  --num_fewshot 0 \
  --batch_size 8 \
  --limit 10 \
  --output_path /tmp/p5b_smoke_test \
  2>&1
echo "=== Smoke test done (exit $?) ==="
