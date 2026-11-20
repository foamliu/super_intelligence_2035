#!/bin/bash
# S0/S1 vision encoder pretraining helper — shared env for torchrun training.
# Usage:  bash run_train.sh <tower> <steps> <output_dir> [extra args...]
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export MASTER_PORT=$((29400 + RANDOM % 1000))
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

TOWER="$1"; STEPS="$2"; OUT="$3"; shift 3
echo "[run_train] tower=$TOWER steps=$STEPS out=$OUT extra=$*"

mkdir -p "$OUT"
exec "$PY" -m torch.distributed.run --nproc_per_node=6 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$MASTER_PORT \
    train.py --tower "$TOWER" --steps "$STEPS" --output-dir "$OUT" "$@"