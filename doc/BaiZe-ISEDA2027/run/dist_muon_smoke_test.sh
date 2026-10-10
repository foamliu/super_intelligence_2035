#!/bin/bash
# dist_muon 优化器冒烟测试：8 GPU (DP=8, TP=1), mock 数据, 10 步
# 验证 layer-wise distributed Muon 能跑通 (dist_muon 需 DP>1)
# 用法: bash dist_muon_smoke_test.sh
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
cd "$BASE"

export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/dist_muon_smoke.log

MASTER_PORT=$($PY -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")
echo "===== dist_muon smoke test @ $(date '+%F %T') ====="
echo "8 GPU, DP=8, TP=1, mock data, 10 steps"
echo "MASTER_PORT=$MASTER_PORT"

$PY -m torch.distributed.run \
    --nnodes=1 --nproc_per_node=8 \
    --master_port=$MASTER_PORT \
    pretrain_launcher.py \
    --arch mamba2 \
    --name dist_muon_smoke \
    --dir "$BASE/nemo_experiments" \
    --mock \
    --train-iters 10 \
    --optimizer dist_muon \
    --tensor-parallel 1 \
    --global-batch-size 16 \
    --micro-batch-size 1 \
    --seq-length 4094 \
    --seed 1234 \
    --precision bf16_mixed \
    --lr 3e-4 \
    --lr-warmup-iters 2 \
    --lr-decay-iters 5 \
    --lr-decay-style WSD \
    --eval-interval 9999 --eval-iters 0 \
    --save-interval 99999 \
    2>&1 | tee "$LOG"

rc=${PIPESTATUS[0]}
if [ $rc -eq 0 ]; then
    echo "===== dist_muon smoke test PASSED @ $(date '+%F %T') ====="
    grep -E '^\s*[0-9]+/' "$LOG" | head -20
    echo "--- bridge_compat routing log ---"
    grep -i 'bridge_compat.*muon\|layer_wise' "$LOG" | head -5
else
    echo "===== dist_muon smoke test FAILED (rc=$rc) @ $(date '+%F %T') ====="
    tail -80 "$LOG"
fi
