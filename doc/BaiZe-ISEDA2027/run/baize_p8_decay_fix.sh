#!/bin/bash
# BaiZe Stage(i) P-8: Decay phase FIX — SFT annealing blend with proper LR decay
#
# 🔧 2026-10-14 FIX (用户直令): LR 未衰减根因 = resume 时 scheduler 内部 step 计数器
#   未恢复（load_optim=False 导致 scheduler state 不加载），但全局 step 被恢复到 9441
#   → scheduler 内部 counter 从 0 开始，WSD stable 区 0→9441，decay 区 9441→10490
#   → decay run 只有 1049 步，永远到不了 decay 区 → LR 卡 1e-3。
#
#   修复方案（用户给定）：finetune=True → 只加载权重，不加载 optimizer/scheduler/train_state
#   → step 重置为 0，scheduler 从新 config 开始 → warmup 100 步 → decay 1049 步 (1e-3→1e-5)
#
# Resume from step-9441 checkpoint of the stable phase (weights only, no optimizer state).
# New run name "p8_adamw_decay" → saves to separate directory, doesn't overwrite stable ckpts.
#
# Decay blend: SFT 64% + L3 24% + code 8% + math 4%
# WSD: warmup=100 (short warmup, per user instruction), decay=1049 steps
#   → LR warms 0→1e-3 over 100 steps, then decays 1e-3→1e-5 over 1049 steps
#   → Total ITERS = 1149
#
# 启动：setsid bash baize_p8_decay_fix.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

NAME="p8_adamw_decay"    # ⭐ NEW name → saves to separate dir
STABLE_NAME="p8_adamw"   # stable phase run name (source of weights)
PORT=29811
ITERS=1149               # total steps: 100 warmup + 1049 decay
WARMUP=100               # ⭐ short warmup (user: "稍稍 warmup, ~50-100 步")
DECAY=1049               # decay over 1049 steps (1e-3 → 1e-5)
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=500        # save at 500, 1000, 1149
SEQ=4094                 # ⚠️ keep 4094 (same as stable, P-8 整轮不变)
GBS=1024
MBS=2
TP=1
NP=8

DATA="$BASE/data"
SAVE_CKPT_DIR="$BASE/nemo_experiments/${NAME}/checkpoints"
LOAD_CKPT_DIR="$BASE/nemo_experiments/${STABLE_NAME}/checkpoints"

# ========== Decay data blend: SFT 64 : L3 24 : code 8 : math 4 ==========
BLEND=""
for s in 0 1 2 3; do
    BLEND="$BLEND 8 ${DATA}/mix_sft_tok/mix_sft_train_s${s}"
done
for s in 0 1 2 3; do
    BLEND="$BLEND 8 ${DATA}/mix_sft_agent_tok/mix_sft_agent_train_s${s}"
done
for s in 0 1 2 3 4 5 6 7; do
    BLEND="$BLEND 3 ${DATA}/p5b_l3/p5b_l3_train_s${s}"
done
BLEND="$BLEND 3 ${DATA}/anneal_code 5 ${DATA}/r3_sources/r3_ultradata_code"
BLEND="$BLEND 3 ${DATA}/anneal_math2 1 ${DATA}/r3_sources/r3_ultradata_math"
BLEND="${BLEND# }"

# ========== 前置检查 ==========
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU_BUSY" ]; then
    echo "❌ GPU $GPU_BUSY 非空 (used>1GB)，停手" | tee "$LOGDIR/baize_p8_decay_fix.log"
    exit 1
fi

STEP9441_CKPT="${LOAD_CKPT_DIR}/iter_0009441"
if [ ! -d "$STEP9441_CKPT" ]; then
    echo "❌ Stable checkpoint not found: $STEP9441_CKPT" | tee "$LOGDIR/baize_p8_decay_fix.log"
    ls -d "${LOAD_CKPT_DIR}"/iter_* 2>/dev/null | tee -a "$LOGDIR/baize_p8_decay_fix.log" || true
    exit 1
fi

TMP_AVAIL=$(df --output=avail /tmp | tail -1 | tr -d ' ')
if [ "$TMP_AVAIL" -lt 5000000 ]; then
    echo "❌ /tmp 可用空间不足 (${TMP_AVAIL}KB < 5GB)，停手" | tee "$LOGDIR/baize_p8_decay_fix.log"
    exit 1
fi

for s in 0 1 2 3; do
    for ext in bin idx; do
        [ -f "${DATA}/mix_sft_tok/mix_sft_train_s${s}.${ext}" ] || { echo "❌ 缺 mix_sft_train_s${s}.${ext}"; exit 1; }
        [ -f "${DATA}/mix_sft_agent_tok/mix_sft_agent_train_s${s}.${ext}" ] || { echo "❌ 缺 mix_sft_agent_train_s${s}.${ext}"; exit 1; }
    done
done
for s in 0 1 2 3 4 5 6 7; do
    for ext in bin idx; do
        [ -f "${DATA}/p5b_l3/p5b_l3_train_s${s}.${ext}" ] || { echo "❌ 缺 p5b_l3_train_s${s}.${ext}"; exit 1; }
    done
done
for prefix in "${DATA}/anneal_code" "${DATA}/r3_sources/r3_ultradata_code" "${DATA}/anneal_math2" "${DATA}/r3_sources/r3_ultradata_math"; do
    for ext in bin idx; do
        [ -f "${prefix}.${ext}" ] || { echo "❌ 缺 ${prefix}.${ext}"; exit 1; }
    done
done
[ -f "${DATA}/tokenizer_eod/tokenizer.json" ] || { echo "❌ 缺 tokenizer_eod"; exit 1; }

# ========== 启动 decay phase 训练 (FIX: finetune mode) ==========
SUM="$LOGDIR/baize_p8_decay_fix.log"
LOG="$LOGDIR/baize_p8_decay_fix_train.log"
echo "===== P-8 decay FIX START @ $(date '+%F %T') ITERS=${ITERS} WARMUP=${WARMUP} DECAY=${DECAY} LR=${LR} min=${MIN_LR} save=${SAVE_INTERVAL} optimizer=adam(AdamW) finetune=True =====" > "$SUM"
echo "  NP=${NP} TP=${TP} DP=$((NP/TP))" >> "$SUM"
echo "  finetune=True: load weights only from ${LOAD_CKPT_DIR}, fresh optimizer + scheduler, step=0" >> "$SUM"
echo "  save to: ${SAVE_CKPT_DIR}" >> "$SUM"
echo "  decay blend: SFT 64% + L3 24% + code 8% + math 4%" >> "$SUM"
echo "  WSD: warmup ${WARMUP} steps (0->${LR}) -> decay ${DECAY} steps (${LR}->${MIN_LR})" >> "$SUM"

cd "$BASE" || exit 1
"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    pretrain_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --load-dir "$LOAD_CKPT_DIR" \
    --finetune \
    --tokenizer-path "$BASE/data/tokenizer_eod" \
    --train-data-path $BLEND \
    --tensor-parallel "$TP" \
    --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
    --eval-interval 250 --eval-iters 0 \
    --save-interval "$SAVE_INTERVAL" \
    --lr "$LR" --min-lr "$MIN_LR" \
    --lr-warmup-iters "$WARMUP" --lr-decay-iters "$DECAY" --lr-decay-style WSD \
    --seed 1234 \
    --precision bf16_mixed \
    --optimizer adam > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== P-8 decay FIX END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC
