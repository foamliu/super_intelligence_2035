#!/bin/bash
# S2 inference benchmark: single-GPU forward, batch=1 (inference), bf16, res=224/patch=16.
# Robust: mambaeye (SSM) last since its kernel can stall at batch=1; per-tower timeout.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/s2_bench.log

# cleanup any orphaned benchmark from earlier attempts
pkill -f 'bench.py' 2>/dev/null || true
pkill -f 's2_bench.py' 2>/dev/null || true

echo "##### S2 inference benchmark (batch=1, bf16, 224/16) #####" > "$LOG"
for TOWER in openvision2 deepencoder_v2 moevie mambaeye; do
    echo "== tower=$TOWER ==" >> "$LOG"
    timeout 150 "$PY" bench.py --tower "$TOWER" --resolution 224 --patch 16 --batch 1 --iters 200 --warmup 30 >> "$LOG" 2>&1
    echo "== $TOWER rc=$? ==" >> "$LOG"
done
echo "##### S2 DONE #####" >> "$LOG"