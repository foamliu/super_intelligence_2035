#!/bin/bash
# BaiZe Stage(i) P-8: Formal pretraining — 44B token (Chinchilla lower bound)
# From scratch, Mamba2-hybrid 2.220B, dist_muon, WSD 5%/85%/10%
#
# Stable blend: web 88% (mix_base 44 shards, 524B) : code 8% (anneal_code + r3_code, 270M) : math 4% (anneal_math2 + r3_math, 609M)
#   ⚠️ code/math tokenized data is undersized (~270M/609M vs ~3B/1.5B needed) → ~12x/2.6x repetition.
#   Web (524B) has zero repetition. This is a known limitation; full UltraData-Code/Math tokenization pending.
#
# Two-phase plan:
#   Phase 1 (this script) = 10490 steps with stable data + WSD schedule (warmup 524 → stable 8917 → decay 1049)
#   Phase 2 (separate script baize_p8_decay.sh, after step 9441) = 1049 steps with SFT decay blend
#     → SFT 退火混合 in decay phase: SFT 64% + L3 24% + code 8% + math 4%
#     → Resume from step-9441 checkpoint, LR decays 1e-3→1e-5
#
# 启动：setsid bash baize_p8_train.sh &（PPID=1 真后台；勿裸 nohup &）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

NAME="p8"
PORT=29810
ITERS=10490           # 44B token (GBS1024 × seq4094 = 4.192M token/步)
WARMUP=524            # 5% ≈ 524
DECAY=1049            # 10% ≈ 1049 (decay 尾段步数)
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=1049    # 每 ~10% 一个 ckpt（11 个点：1049, 2098, ..., 10490）
SEQ=4094              # 固定口径（memory: "seq_length=4094, 非 4096"）
GBS=1024
MBS=2                 # P-8 关键改：MBS=2（P-5b 是 MBS=1）→ 249K tok/s
TP=1
NP=8                  # 8 卡独占

DATA="$BASE/data"

# ========== Stable data blend: web 88 : code 8 : math 4 ==========
# 44 mix_base shards × weight 2 = 88 (web 88%)
# anneal_code (90M, w=3) + r3_ultradata_code (180M, w=5) = 8 (code 8%)
# anneal_math2 (431M, w=3) + r3_ultradata_math (178M, w=1) = 4 (math 4%)
# Total weight = 88 + 8 + 4 = 100

BLEND=""
# Web: 44 mix_base shards, each weight 2
for s in $(seq 0 43); do
    BLEND="$BLEND 2 ${DATA}/mix_base/mix_base_train_s${s}"
done
# Code: anneal_code (w=3) + r3_ultradata_code (w=5)
BLEND="$BLEND 3 ${DATA}/anneal_code 5 ${DATA}/r3_sources/r3_ultradata_code"
# Math: anneal_math2 (w=3) + r3_ultradata_math (w=1)
BLEND="$BLEND 3 ${DATA}/anneal_math2 1 ${DATA}/r3_sources/r3_ultradata_math"

# Trim leading space
BLEND="${BLEND# }"

# ========== 前置检查 ==========
# 1) GPU 0-7 全空（8 卡独占）
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU_BUSY" ]; then
    echo "❌ GPU $GPU_BUSY 非空 (used>1GB)，停手（不 kill 他人）" | tee "$LOGDIR/baize_${NAME}.log"
    exit 1
fi

# 2) blend 中每个 .bin/.idx 齐备
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

# 3) tokenizer
[ -f "${DATA}/tokenizer_eod/tokenizer.json" ] || { echo "❌ 缺 tokenizer_eod" | tee "$LOGDIR/baize_${NAME}.log"; exit 1; }

# ========== 启动训练 ==========
SUM="$LOGDIR/baize_${NAME}.log"
LOG="$LOGDIR/baize_${NAME}_train.log"
echo "===== P-8 train START @ $(date '+%F %T') ITERS=${ITERS} GBS=${GBS} MBS=${MBS} seq=${SEQ} LR=${LR} min=${MIN_LR} warmup=${WARMUP} decay=${DECAY} save=${SAVE_INTERVAL} optimizer=dist_muon =====" > "$SUM"
echo "  NP=${NP} TP=${TP} DP=$((NP/TP))" >> "$SUM"
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
    --optimizer dist_muon > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== P-8 train END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC
