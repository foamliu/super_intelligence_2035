#!/bin/bash
# BaiZe 配比实验 · 开工前 5 项必验 · 2026-10-06 第5轮定案 (d=128/L=14)
#
# 并行执行：
#   GPU2: d=128 proxy 50步 smoke + s_step 实测 (必验 #2 + #4)
#   GPU3: 2B model numel check (必验 #3, tie/untie)
#   GPU4: LR=3e-4, 50步 (必验 #5)
#   GPU5: LR=1e-3, 50步 (必验 #5)
#   GPU6: LR=3e-3, 50步 (必验 #5)
#
# 用法：ssh 10.239.2.29 'bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_validate_d128.sh'
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
DATA="$BASE/data"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export TOKENIZER="$DATA/tokenizer_eod"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

GBS=16
SEQ=2048
ITERS=50
WARMUP=10
LOGDIR=/tmp/validate_d128

mkdir -p "$LOGDIR"

echo "===== D128 VALIDATION START @ $(date '+%F %T') ====="
echo "  Model: d=128/L=14 (18.5M expected, 第5轮定案)"
echo "  GPU2: d=128 smoke+s_step (50 steps)"
echo "  GPU3: 2B numel check (1 step mock)"
echo "  GPU4: LR=3e-4 (50 steps)"
echo "  GPU5: LR=1e-3 (50 steps)"
echo "  GPU6: LR=3e-3 (50 steps)"
echo ""

# === GPU2: d=128 proxy smoke + s_step (必验 #2 + #4) ===
# Use real tokenizer + real base data for 50 steps
BLEND_BASE="100 ${DATA}/mix_base/mix_base_train_s0"
VAL_BASE="1 ${DATA}/heldout/held_out_base"

CUDA_VISIBLE_DEVICES=2 \
$PY/torchrun --nnodes=1 --nproc_per_node=1 \
    --master_addr=127.0.0.1 --master_port=29980 \
    $BASE/pretrain_proxy_launcher.py \
    --name val_d128_sstep --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$TOKENIZER" \
    --train-data-path $BLEND_BASE \
    --valid-data-path $VAL_BASE \
    --proxy-size d128 \
    --train-iters $ITERS --global-batch-size $GBS --micro-batch-size 1 \
    --seq-length $SEQ \
    --eval-interval 25 --eval-iters 10 \
    --save-interval 99999 \
    --lr 1e-3 --min-lr 1e-5 \
    --lr-warmup-iters $WARMUP --lr-decay-iters 0 --lr-decay-style WSD \
    --seed 1234 --precision bf16_mixed \
    > "$LOGDIR/gpu2_d128_sstep.log" 2>&1 &
PID_GPU2=$!

# === GPU3: 2B model numel check (必验 #3, tie/untie) ===
# Mock data, real tokenizer, 1 step only — just need parameter count
CUDA_VISIBLE_DEVICES=3 \
$PY/torchrun --nnodes=1 --nproc_per_node=1 \
    --master_addr=127.0.0.1 --master_port=29981 \
    $BASE/pretrain_launcher.py \
    --arch mamba2 \
    --name val_2b_numel --dir /tmp/numel_2b \
    --tokenizer-path "$TOKENIZER" \
    --mock --train-iters 1 \
    --global-batch-size 1 --micro-batch-size 1 \
    --seq-length 2048 \
    --eval-interval 9999 --eval-iters 0 \
    --save-interval 99999 \
    --lr 1e-4 --seed 1234 --precision bf16_mixed \
    > "$LOGDIR/gpu3_2b_numel.log" 2>&1 &
PID_GPU3=$!

# === GPU4-6: LR rescan (必验 #5) ===
for i in 0 1 2; do
    GPU=$((i + 4))  # GPU4, GPU5, GPU6
    case $i in
        0) LR="3e-4"; PORT=29984;;
        1) LR="1e-3"; PORT=29985;;
        2) LR="3e-3"; PORT=29986;;
    esac
    NAME="val_d128_lr${i}"
    LOG="$LOGDIR/${NAME}.log"

    CUDA_VISIBLE_DEVICES=$GPU \
    $PY/torchrun --nnodes=1 --nproc_per_node=1 \
        --master_addr=127.0.0.1 --master_port=$PORT \
        $BASE/pretrain_proxy_launcher.py \
        --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$TOKENIZER" \
        --train-data-path $BLEND_BASE \
        --valid-data-path $VAL_BASE \
        --proxy-size d128 \
        --train-iters $ITERS --global-batch-size $GBS --micro-batch-size 1 \
        --seq-length $SEQ \
        --eval-interval 25 --eval-iters 10 \
        --save-interval 99999 \
        --lr "$LR" --min-lr 1e-5 \
        --lr-warmup-iters $WARMUP --lr-decay-iters 0 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed \
        > "$LOG" 2>&1 &
    echo "  [GPU$GPU] LR=$LR PORT=$PORT PID=$! → $LOG"
done

echo ""
echo "  PIDs: GPU2=$PID_GPU2 GPU3=$PID_GPU3"
echo "  Waiting for all to complete..."

# Wait for 2B check (should be fastest, ~1 min)
wait $PID_GPU3 2>/dev/null
echo "  [GPU3] 2B numel check done @ $(date '+%T')"

# Wait for remaining
wait $PID_GPU2 2>/dev/null
echo "  [GPU2] d=128 s_step done @ $(date '+%T')"

# Wait for LR rescan
wait
echo "  [GPU4-6] LR rescan done @ $(date '+%T')"

echo ""
echo "===== ALL VALIDATIONS COMPLETE @ $(date '+%F %T') ====="
echo "  Logs in $LOGDIR/"
echo ""
echo "=== GPU2: d=128 numel + s_step ==="
grep -E 'number of parameters|padded vocab|iteration.*10.*lm loss|iteration.*20.*lm loss|iteration.*30.*lm loss|iteration.*40.*lm loss|iteration.*50.*lm loss|validation loss' "$LOGDIR/gpu2_d128_sstep.log" 2>/dev/null | head -20
echo ""
echo "=== GPU3: 2B numel ==="
grep -E 'number of parameters|padded vocab|share_embeddings' "$LOGDIR/gpu3_2b_numel.log" 2>/dev/null | head -10
echo ""
echo "=== GPU4: LR=3e-4 ==="
grep -E 'number of parameters|iteration.*50.*lm loss|validation loss' "$LOGDIR/val_d128_lr0.log" 2>/dev/null | head -10
echo ""
echo "=== GPU5: LR=1e-3 ==="
grep -E 'number of parameters|iteration.*50.*lm loss|validation loss' "$LOGDIR/val_d128_lr1.log" 2>/dev/null | head -10
echo ""
echo "=== GPU6: LR=3e-3 ==="
grep -E 'number of parameters|iteration.*50.*lm loss|validation loss' "$LOGDIR/val_d128_lr2.log" 2>/dev/null | head -10
