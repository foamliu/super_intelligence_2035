#!/bin/bash
# DEPRECATED 2026-10-06：2.2B 单臂方案作废（运维指令 §🔴🔴 2026-10-06）。
# 原因：用目标尺寸 2.2B 模型跑单臂（base:code:math=88:8:4），无对照/无搜索/无不确定性，
#       不构成「实验」；成本 ≈312 GPU·h/臂 ≈ P-8 本体的 13%，搜索比训练还贵。
# 已跑 1470/5000 步作废（~100 GPU·h 浪费）。GPU2-7 已于 2026-10-06 08:06 释放。
# 新方案：小代理模型（96.8M h512/L14）+ Optuna BO + 每卡独立 trial → run/baize_mix_optuna.py
#
# === 以下为历史脚本，保留备查，不再调用 ===
# BaiZe 数据配比实验（§0.6-B）— Stable 段 S0a 臂：base:code:math = 88:8:4
# 口径：6 卡 · TP1/DP6 · seq=4094 · mb=1 · GBS=1024 · 5000 步 · bf16_mixed
# GPU：CUDA_VISIBLE_DEVICES=2,3,4,5,6,7（GPU2-7，data 名下）
# 代理指标：跑完 → ckpt → HF → lm_eval（Table 2 的 8 个）
exit 1  # DEPRECATED — do not run
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export CUDA_VISIBLE_DEVICES=2,3,4,5,6,7

NAME="mix_stable_s0a"
PORT=29950
ITERS=5000
WARMUP=250
DECAY=0
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=5000
SEQ=4094
GBS=1020  # 6×170=1020（DP6 要求 GBS 整除 6；基线 1024→1020，-0.4%，报告注明）
MBS=1
TP=1
NP=6

# ========== 数据 blend ==========
# Megatron 扁平 weight/prefix：[w0, prefix0, w1, prefix1, ...]
# 4 base shards × 22 = 88（base 88%）；code 8%；math 4% → 总 100
DATA="$BASE/data"
BLEND="22 ${DATA}/mix_base/mix_base_train_s0 22 ${DATA}/mix_base/mix_base_train_s1 22 ${DATA}/mix_base/mix_base_train_s2 22 ${DATA}/mix_base/mix_base_train_s3 8 ${DATA}/anneal_code 4 ${DATA}/anneal_math2"

# ========== 前置检查 ==========
# 1) GPU2-7 空（只查 GPU2-7，允许 GPU0-1 被 pretrain 用）
GPU2_7_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '$1>=2 && $1<=7 {gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU2_7_BUSY" ]; then
    echo "❌ GPU2-7 非空 (GPU $GPU2_7_BUSY used>1GB)，停手（不 kill 对方）" | tee "$LOGDIR/baize_${NAME}.log"; exit 1
fi

# 2) blend 中每个 .bin/.idx 齐备
for prefix in $(echo "$BLEND" | awk 'NR%2==0'); do
    for ext in bin idx; do
        [ -f "${prefix}.${ext}" ] || { echo "❌ 缺 ${prefix}.${ext}" | tee "$LOGDIR/baize_${NAME}.log"; exit 1; }
    done
done

# ========== 启动训练 ==========
SUM="$LOGDIR/baize_${NAME}.log"
LOG="$LOGDIR/baize_${NAME}_train.log"
echo "===== mix ${NAME} START @ $(date '+%F %T') ITERS=${ITERS} GBS=${GBS} TP=${TP} DP=${NP} seq=${SEQ} LR=${LR} warmup=${WARMUP} decay=${DECAY} =====" > "$SUM"
echo "  BLEND=[$BLEND]" >> "$SUM"
echo "  CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}" >> "$SUM"

cd "$BASE" || exit 1
"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    pretrain_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$BASE/data/tokenizer_eod" \
    --train-data-path $BLEND \
    --tensor-parallel "$TP" \
    --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
    --eval-interval 250 --eval-iters 0 \
    --save-interval "$SAVE_INTERVAL" \
    --lr "$LR" --min-lr "$MIN_LR" \
    --lr-warmup-iters "$WARMUP" --lr-decay-iters "$DECAY" --lr-decay-style WSD \
    --seed 1234 \
    --precision bf16_mixed > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== mix ${NAME} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC