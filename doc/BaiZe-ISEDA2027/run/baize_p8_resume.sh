#!/bin/bash
# BaiZe P-8: RESUME from iter_0003147 after crash at step3740 (2026-10-11 13:07)
# Crash cause: /tmp was 100% full → NCCL temp file creation failed → rank7 exitcode=1
# Fix: cleaned /tmp (93G→38G). Resume with --lr-warmup-iters 0 (past warmup, no re-warmup).
# WSD schedule with warmup=0: stable=9441 (0→9441), decay=1049 (9441→10490).
# At step3147: stable phase, LR=1e-3 ✅. Decay starts at step9441 ✅.
#
# 启动：setsid bash baize_p8_resume.sh &（PPID=1 真后台）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

NAME="p8"
PORT=29810
ITERS=10490           # 44B token (GBS1024 × seq4094 = 4.192M token/步)
WARMUP=0              # ⭐ CHANGED: 0 (skip re-warmup, we're at step3147 past original warmup524)
DECAY=1049            # 10% ≈ 1049 (decay 尾段步数) — decay starts at step 9441 = 10490-1049
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=1049    # 每 ~10% 一个 ckpt
SEQ=4094              # 固定口径
GBS=1024
MBS=2
TP=1
NP=8                  # 8 卡独占

DATA="$BASE/data"

# ========== Stable data blend: web 88 : code 8 : math 4 ==========
BLEND=""
for s in $(seq 0 43); do
    BLEND="$BLEND 2 ${DATA}/mix_base/mix_base_train_s${s}"
done
BLEND="$BLEND 3 ${DATA}/anneal_code 5 ${DATA}/r3_sources/r3_ultradata_code"
BLEND="$BLEND 3 ${DATA}/anneal_math2 1 ${DATA}/r3_sources/r3_ultradata_math"
BLEND="${BLEND# }"

# ========== 前置检查 ==========
# 1) GPU 0-7 全空
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU_BUSY" ]; then
    echo "❌ GPU $GPU_BUSY 非空 (used>1GB)，停手" | tee "$LOGDIR/baize_${NAME}.log"
    exit 1
fi

# 2) /tmp 空间检查（crash 根因防护）
TMP_AVAIL=$(df --output=avail /tmp | tail -1 | tr -d ' ')
if [ "$TMP_AVAIL" -lt 5000000 ]; then
    echo "❌ /tmp 可用空间不足 (${TMP_AVAIL}KB < 5GB)，停手" | tee "$LOGDIR/baize_${NAME}.log"
    exit 1
fi

# 3) blend 中每个 .bin/.idx 齐备
for s in $(seq 0 43); do
    for ext in bin idx; do
        [ -f "${DATA}/mix_base/mix_base_train_s${s}.${ext}" ] || { echo "❌ 缺 mix_base_train_s${s}.${ext}" | tee "$LOGDIR/baize_${NAME}.log"; exit 1; }
    done
done
for prefix in "${DATA}/anneal_code" "${DATA}/r3_sources/r3_ultradata_code" "${DATA}/anneal_math2" "${DATA}/r3_sources/r3_ultradata_math"; do
    for ext in bin idx; do
        [ -f "${prefix}.${ext}" ] || { echo "❌ 缺 ${prefix}.${ext}" | tee "$LOGDIR/baize_${NAME}.log"; exit 1; }
    done
done

# 4) tokenizer
[ -f "${DATA}/tokenizer_eod/tokenizer.json" ] || { echo "❌ 缺 tokenizer_eod" | tee "$LOGDIR/baize_${NAME}.log"; exit 1; }

# 5) checkpoint exists
CKPT_DIR="$BASE/nemo_experiments/${NAME}/checkpoints"
if [ ! -f "$CKPT_DIR/latest_checkpointed_iteration.txt" ]; then
    echo "❌ No checkpoint found at $CKPT_DIR" | tee "$LOGDIR/baize_${NAME}.log"
    exit 1
fi
CKPT_ITER=$(cat "$CKPT_DIR/latest_checkpointed_iteration.txt")
echo "  Resuming from checkpoint iteration: $CKPT_ITER"

# ========== 启动训练 ==========
SUM="$LOGDIR/baize_${NAME}.log"
LOG="$LOGDIR/baize_${NAME}_train.log"
echo "===== P-8 RESUME START @ $(date '+%F %T') from iter=${CKPT_ITER} ITERS=${ITERS} GBS=${GBS} MBS=${MBS} seq=${SEQ} LR=${LR} min=${MIN_LR} warmup=${WARMUP} decay=${DECAY} save=${SAVE_INTERVAL} optimizer=dist_muon =====" > "$SUM"
echo "  NP=${NP} TP=${TP} DP=$((NP/TP))" >> "$SUM"
echo "  ⭐ warmup=0 (skip re-warmup, past original warmup524)" >> "$SUM"
echo "  WSD: stable 0→9441, decay 9441→10490" >> "$SUM"

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
    --precision bf16_mixed \
    --optimizer dist_muon > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== P-8 RESUME END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC
