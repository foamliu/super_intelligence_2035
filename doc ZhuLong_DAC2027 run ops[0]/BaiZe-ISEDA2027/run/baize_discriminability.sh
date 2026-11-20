#!/bin/bash
# BaiZe 配比实验 · 必验 #1 判别力测试 · 2026-10-06
#
# code=0% vs code=30%，各 3 seed，6 GPU 同跑
# 验证 Δloss > 2σ（配比实验可开工的必要条件）
#
# 用法：ssh 10.239.2.29 'bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_discriminability.sh'
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
DATA="$BASE/data"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export TOKENIZER="$DATA/tokenizer_eod"

GBS=16
SEQ=2048
ITERS=50
WARMUP=10
LR=3e-3   # 最佳 LR (from 必验 #5)
LOGDIR=/tmp/validate_d128

mkdir -p "$LOGDIR"

# Data blends
BASE_DATA="$DATA/mix_base/mix_base_train_s0"
CODE_DATA="$DATA/anneal_code"
VAL_CODE="1 ${DATA}/heldout/held_out_code"

echo "===== DISCRIMINABILITY TEST START @ $(date '+%F %T') ====="
echo "  code=0% (3 seeds): GPU2,3,4"
echo "  code=30% (3 seeds): GPU5,6,7"
echo "  LR=$LR, ITERS=$ITERS, eval on held_out_code"
echo ""

# === code=0% (seeds 1234, 2345, 3456) ===
for i in 0 1 2; do
    GPU=$((i + 2))  # GPU2, 3, 4
    SEED=$((1234 + i * 1111))
    PORT=$((29990 + i))
    NAME="disc_code0_s${SEED}"
    LOG="$LOGDIR/${NAME}.log"

    CUDA_VISIBLE_DEVICES=$GPU \
    $PY/torchrun --nnodes=1 --nproc_per_node=1 \
        --master_addr=127.0.0.1 --master_port=$PORT \
        $BASE/pretrain_proxy_launcher.py \
        --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$TOKENIZER" \
        --train-data-path 100 ${BASE_DATA} \
        --valid-data-path $VAL_CODE \
        --proxy-size d128 \
        --train-iters $ITERS --global-batch-size $GBS --micro-batch-size 1 \
        --seq-length $SEQ \
        --eval-interval 25 --eval-iters 10 \
        --save-interval 99999 \
        --lr "$LR" --min-lr 1e-5 \
        --lr-warmup-iters $WARMUP --lr-decay-iters 0 --lr-decay-style WSD \
        --seed "$SEED" --precision bf16_mixed \
        > "$LOG" 2>&1 &
    echo "  [GPU$GPU] code=0% seed=$SEED PID=$! → $LOG"
done

# === code=30% (seeds 1234, 2345, 3456) ===
for i in 0 1 2; do
    GPU=$((i + 5))  # GPU5, 6, 7
    SEED=$((1234 + i * 1111))
    PORT=$((29993 + i))
    NAME="disc_code30_s${SEED}"
    LOG="$LOGDIR/${NAME}.log"

    CUDA_VISIBLE_DEVICES=$GPU \
    $PY/torchrun --nnodes=1 --nproc_per_node=1 \
        --master_addr=127.0.0.1 --master_port=$PORT \
        $BASE/pretrain_proxy_launcher.py \
        --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$TOKENIZER" \
        --train-data-path 70 ${BASE_DATA} 30 ${CODE_DATA} \
        --valid-data-path $VAL_CODE \
        --proxy-size d128 \
        --train-iters $ITERS --global-batch-size $GBS --micro-batch-size 1 \
        --seq-length $SEQ \
        --eval-interval 25 --eval-iters 10 \
        --save-interval 99999 \
        --lr "$LR" --min-lr 1e-5 \
        --lr-warmup-iters $WARMUP --lr-decay-iters 0 --lr-decay-style WSD \
        --seed "$SEED" --precision bf16_mixed \
        > "$LOG" 2>&1 &
    echo "  [GPU$GPU] code=30% seed=$SEED PID=$! → $LOG"
done

echo ""
echo "  Waiting for all 6 runs..."
wait
echo "===== DISCRIMINABILITY TEST COMPLETE @ $(date '+%F %T') ====="
echo ""

echo "=== code=0% results ==="
for s in 1234 2345 3456; do
    LOG="$LOGDIR/disc_code0_s${s}.log"
    echo "  seed=$s:"
    grep "validation loss at iteration 50 |" "$LOG" 2>/dev/null | sed 's/^/    /'
done

echo ""
echo "=== code=30% results ==="
for s in 1234 2345 3456; do
    LOG="$LOGDIR/disc_code30_s${s}.log"
    echo "  seed=$s:"
    grep "validation loss at iteration 50 |" "$LOG" 2>/dev/null | sed 's/^/    /'
done
