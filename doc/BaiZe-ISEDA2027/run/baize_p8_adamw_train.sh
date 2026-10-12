#!/bin/bash
# BaiZe Stage(i) P-8: Formal pretraining — 44B token (Chinchilla lower bound)
# From scratch, Mamba2-hybrid 2.220B, **AdamW** (standard Megatron adam), WSD 5%/85%/10%
#
# ⭐ 2026-10-12 用户令：dist_muon 发散 → 换回 AdamW 从零重启
#   - optimizer=adam (= 标准 Megatron AdamW, 非 dist_muon, 无 layer_wise_distributed_optimizer)
#   - NAME=p8_adamw (独立 ckpt 目录，🚫 不覆盖 dist_muon 的 p8/)
#   - warmup=524 (从头训，非崩溃恢复的 0)
#   - LR=1e-3 (AdamW 早先试验定值，🛫 不准改)
#
# Stable blend: web 88% (mix_base 44 shards, 524B) : code 8% (anneal_code + r3_code, 270M) : math 4% (anneal_math2 + r3_math, 609M)
#
# Two-phase plan:
#   Phase 1 (this script) = 10490 steps with stable data + WSD schedule (warmup 524 → stable 8917 → decay 1049)
#   Phase 2 (baize_p8_decay.sh, after step 9441) = 1049 steps with SFT decay blend
#     → Resume from step-9441 checkpoint, LR decays 1e-3→1e-5
#
# 启动：setsid bash baize_p8_adamw_train.sh &（PPID=1 真后台；勿裸 nohup &）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

NAME="p8_adamw"         # ⭐ 独立目录，不覆盖 dist_muon 的 p8/
PORT=29812              # different port
ITERS=10490             # 44B token (GBS1024 × seq4094 = 4.192M token/步)
WARMUP=524              # ⭐ 5% warmup (从头训，非崩溃恢复的 0)
DECAY=1049              # 10% ≈ 1049 (decay 尾段步数)
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=1049      # 每 ~10% 一个 ckpt
SEQ=4094                # 固定口径（memory: "seq_length=4094, 非 4096"）
GBS=1024
MBS=2                   # P-8 关键：MBS=2 → 249K tok/s
TP=1
NP=8                    # 8 卡独占

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
# 1) GPU 0-7 全空（8 卡独占）
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU_BUSY" ]; then
    echo "❌ GPU $GPU_BUSY 非空 (used>1GB)，停手（不 kill 他人）" | tee "$LOGDIR/baize_${NAME}.log"
    exit 1
fi

# 2) /tmp 空间检查（crash 根因防护，learned from step3740 crash）
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

# ========== 启动训练 ==========
SUM="$LOGDIR/baize_${NAME}.log"
LOG="$LOGDIR/baize_${NAME}_train.log"
echo "===== P-8 AdamW train START @ $(date '+%F %T') ITERS=${ITERS} GBS=${GBS} MBS=${MBS} seq=${SEQ} LR=${LR} min=${MIN_LR} warmup=${WARMUP} decay=${DECAY} save=${SAVE_INTERVAL} optimizer=adam(AdamW) =====" > "$SUM"
echo "  NP=${NP} TP=${TP} DP=$((NP/TP))" >> "$SUM"
echo "  ⭐ From scratch (no checkpoint loading), optimizer=adam (standard Megatron AdamW)" >> "$SUM"
echo "  blend shards: 44 mix_base (web 88%) + anneal_code+r3_code (code 8%) + anneal_math2+r3_math (math 4%)" >> "$SUM"

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
    --optimizer adam > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== P-8 AdamW train END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC