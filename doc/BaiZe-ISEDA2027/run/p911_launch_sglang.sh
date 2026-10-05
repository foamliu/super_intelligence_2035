#!/bin/bash
# P-9.11: Launch sglang server for BaiZe benchmark
# Usage: bash p911_launch_sglang.sh <hybrid|dense> [port]
set -euo pipefail

MODEL_TYPE="${1:?Usage: $0 <hybrid|dense> [port]}"
PORT="${2:-30000}"

SGLANG_PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
HYBRID_HF=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_hybrid/hf_iter_5000
DENSE_HF=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_dense/hf_iter_5000

if [ "$MODEL_TYPE" = "hybrid" ]; then
    MODEL_PATH="$HYBRID_HF"
    EXTRA_FLAGS="--mamba-ssm-dtype float32"
elif [ "$MODEL_TYPE" = "dense" ]; then
    MODEL_PATH="$DENSE_HF"
    EXTRA_FLAGS=""
else
    echo "ERROR: model type must be 'hybrid' or 'dense'"
    exit 1
fi

echo "[$(date)] Launching sglang server: $MODEL_TYPE on port $PORT"
echo "  model_path=$MODEL_PATH"
echo "  extra_flags=$EXTRA_FLAGS"

# SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1: allow ctx > max_position_embeddings (4096)
# --attention-backend flashinfer: avoid cutlass/flash_attn_origin RoundingModeKind bug
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1

CUDA_VISIBLE_DEVICES=0 $SGLANG_PY -m sglang.launch_server \
    --model-path "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port "$PORT" \
    --context-length 131072 \
    --trust-remote-code \
    --mem-fraction-static 0.85 \
    --attention-backend flashinfer \
    --log-level info \
    $EXTRA_FLAGS \
    2>&1
