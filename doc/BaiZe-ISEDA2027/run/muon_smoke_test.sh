#!/bin/bash
# Muon 优化器冒烟测试：1 GPU, mock 数据, 10 步 — 验证 Muon 能跑通
# 用法: bash muon_smoke_test.sh
set -euo pipefail
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027

export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export CUDA_VISIBLE_DEVICES=0
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/muon_smoke.log

# Pick a random free port to avoid EADDRINUSE on default 29500
MASTER_PORT=$($PY -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")
echo "===== Muon smoke test @ $(date '+%F %T') ====="
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader -i 0)"
echo "MASTER_PORT=$MASTER_PORT"

$PY -m torch.distributed.run \
    --nnodes=1 --nproc_per_node=1 \
    --master_port=$MASTER_PORT \
    pretrain_launcher.py \
    --arch mamba2 \
    --name muon_smoke \
    --mock \
    --train-iters 10 \
    --optimizer muon \
    --tensor-parallel 1 \
    --global-batch-size 4 \
    --micro-batch-size 1 \
    --seq-length 4096 \
    --seed 1234 \
    --precision bf16_mixed \
    --lr 3e-4 \
    --lr-warmup-iters 2 \
    --lr-decay-iters 5 \
    --lr-decay-style WSD \
    --eval-interval 100 \
    --eval-iters 0 \
    --save-interval 100 \
    2>&1 | tee "$LOG"

rc=${PIPESTATUS[0]}
if [ $rc -eq 0 ]; then
    echo "===== Muon smoke test PASSED @ $(date '+%F %T') ====="
    # 提取关键 loss 行
    grep -E '^\s*[0-9]+/' "$LOG" | head -20
else
    echo "===== Muon smoke test FAILED (rc=$rc) @ $(date '+%F %T') ====="
    tail -50 "$LOG"
fi
