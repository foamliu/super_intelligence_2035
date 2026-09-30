#!/bin/bash
# S9 inference deep-dive (P3): batch sweep + multi-resolution on the winner (OpenVision2).
# Uses bench.py (torch.cuda.Event unified forward path, single GPU, bf16) — same stack as S2.
# NOTE: SGLang is not installed; this is the degraded unified-forward benchmark (see Decision 4).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export CUDA_VISIBLE_DEVICES=0

# batch sweep at anchor 224/16
for b in 1 8 32; do
    echo "===== S9 openvision2 batch=$b res=224 patch=16 ====="
    "$PY" bench.py --tower openvision2 --resolution 224 --patch 16 --batch "$b" --iters 50 --warmup 10
done

# multi-resolution at batch=1
for rp in "336 16" "448 16" "224 14"; do
    set -- $rp
    echo "===== S9 openvision2 batch=1 res=$1 patch=$2 ====="
    "$PY" bench.py --tower openvision2 --resolution "$1" --patch "$2" --batch 1 --iters 50 --warmup 10
done
echo "===== S9 ALL DONE ====="