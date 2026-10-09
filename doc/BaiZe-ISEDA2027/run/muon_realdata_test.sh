#!/bin/bash
# Muon real-data quick test: 20 steps with P-5b data, 1 GPU — verify data path works
# Usage: bash muon_realdata_test.sh
set -euo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
cd "$BASE"

export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export CUDA_VISIBLE_DEVICES=0
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/muon_realdata_test.log

# P-5b data blend (16 shards, equal weight 1 each)
BLEND=""
for i in $(seq 0 15); do
    BLEND="$BLEND 1 ${BASE}/data/p5b_l3/p5b_l3_train_s${i}"
done
TOKENIZER="${BASE}/data/tokenizer_eod"

MASTER_PORT=$($PY -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")
echo "===== Muon real-data test @ $(date '+%F %T') ====="
echo "BLEND: $BLEND"
echo "TOKENIZER: $TOKENIZER"

$PY -m torch.distributed.run \
    --nnodes=1 --nproc_per_node=1 \
    --master_port=$MASTER_PORT \
    pretrain_launcher.py \
    --arch mamba2 \
    --name muon_realdata_test \
    --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$TOKENIZER" \
    --train-data-path $BLEND \
    --train-iters 20 \
    --optimizer muon \
    --tensor-parallel 1 \
    --global-batch-size 4 \
    --micro-batch-size 1 \
    --seq-length 4094 \
    --seed 1234 \
    --precision bf16_mixed \
    --lr 3e-4 \
    --lr-warmup-iters 2 \
    --lr-decay-iters 10 \
    --lr-decay-style WSD \
    --eval-interval 9999 --eval-iters 0 \
    --save-interval 99999 \
    2>&1 | tee "$LOG"

rc=${PIPESTATUS[0]}
if [ $rc -eq 0 ]; then
    echo "===== PASSED @ $(date '+%F %T') ====="
    grep -E '^\s*[0-9]+/' "$LOG" | head -25
else
    echo "===== FAILED (rc=$rc) @ $(date '+%F %T') ====="
    tail -80 "$LOG"
fi
