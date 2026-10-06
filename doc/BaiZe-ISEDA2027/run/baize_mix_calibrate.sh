#!/bin/bash
# BaiZe 配比实验 §③ 标定：在 .29 GPU2-4 上并行跑 3 个 LR 点的 50 步冒烟，
# 实测 s/step → 反推 24h trial 数，锁定代理模型尺寸。
#
# 模型：mamba2_hybrid_proxy（h=512, L=14, ~96.8M, tie embed）
# 口径：1 卡/trial · TP1/DP1 · seq=2048 · GBS=16 · mb=1 · 50 步 · bf16_mixed
# LR：3e-4 / 1e-3 / 3e-3（§③.7.③ LR 扫描）
#
# 用法：ssh 10.239.2.29 'bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_calibrate.sh'
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
DATA="$BASE/data"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export TOKENIZER="$DATA/tokenizer_eod"

# 用 base 数据做标定（只测速度，不需要配比）
BLEND="100 ${DATA}/mix_base/mix_base_train_s0"

ITERS=50
GBS=16
SEQ=2048
WARMUP=10

echo "===== CALIBRATION START @ $(date '+%F %T') ====="
echo "  Model: mamba2_hybrid_proxy (h=512, L=14, ~96.8M, tie embed)"
echo "  Config: 1 GPU/trial, TP1/DP1, seq=$SEQ, GBS=$GBS, $ITERS steps, bf16_mixed"
echo "  LR sweep: 3e-4 (GPU2) / 1e-3 (GPU3) / 3e-3 (GPU4)"
echo ""

# 3 个 LR 点并行
for i in 0 1 2; do
    GPU=$((i + 2))  # GPU2, GPU3, GPU4
    case $i in
        0) LR="3e-4"; PORT=29960;;
        1) LR="1e-3"; PORT=29961;;
        2) LR="3e-3"; PORT=29962;;
    esac
    NAME="calib_lr${i}"
    LOG="/tmp/baize_${NAME}.log"

    echo "  [GPU$GPU] LR=$LR PORT=$PORT → $LOG"

    CUDA_VISIBLE_DEVICES=$GPU \
    $PY/torchrun --nnodes=1 --nproc_per_node=1 \
        --master_addr=127.0.0.1 --master_port=$PORT \
        $BASE/pretrain_proxy_launcher.py \
        --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$TOKENIZER" \
        --train-data-path $BLEND \
        --tensor-parallel 1 \
        --train-iters $ITERS --global-batch-size $GBS --micro-batch-size 1 \
        --seq-length $SEQ \
        --eval-interval 9999 --eval-iters 0 \
        --save-interval 99999 \
        --lr "$LR" --min-lr "1e-5" \
        --lr-warmup-iters $WARMUP --lr-decay-iters 0 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed \
        > "$LOG" 2>&1 &
done

echo ""
echo "  All 3 calibration trials launched. Waiting..."
wait
echo ""
echo "===== CALIBRATION END @ $(date '+%F %T') ====="
echo ""
echo "=== Results ==="
for i in 0 1 2; do
    NAME="calib_lr${i}"
    LOG="/tmp/baize_${NAME}.log"
    echo "--- $NAME ---"
    grep -E "iteration|Step Time|lm loss" "$LOG" | tail -10
    echo ""
done
