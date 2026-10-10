#!/bin/bash
# BaiZe Stage(i) P-8: Decay phase — SFT annealing blend (steps 9441→10490)
# Resume from step-9441 checkpoint of the stable phase (baize_p8_train.sh).
#
# Decay blend: SFT 64% + L3 24% + code 8% + math 4%
#   SFT 64% = mix_sft_tok (4 shards × w=8 = 32) + mix_sft_agent_tok (4 shards × w=8 = 32)
#   L3 24%  = p5b_l3 (8 shards s0-s7 × w=3 = 24)
#   Code 8% = anneal_code (w=3) + r3_ultradata_code (w=5)
#   Math 4% = anneal_math2 (w=3) + r3_ultradata_math (w=1)
#   Total weight = 64 + 24 + 8 + 4 = 100
#
# WSD: warmup=0 (no warmup, resuming at peak LR), decay=1049 steps
#   → LR decays from 1e-3 to 1e-5 over steps 9441→10490
#
# ⚠️ PREREQUISITE: Stop stable phase after step 9441 checkpoint is saved:
#     grep 'iteration' /tmp/baize_p8_train.log | tail -1
#     pkill -f 'pretrain_launcher.*p8'
#   Then wait ~30s for GPU memory to free, and launch this script.
#
# 启动：setsid bash baize_p8_decay.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

NAME="p8"               # SAME name → auto-loads checkpoint from same dir
PORT=29811              # different port to avoid conflict
ITERS=10490             # total steps; decay goes 9441→10490
WARMUP=0                # no warmup — resuming at peak LR
DECAY=1049              # decay over 1049 steps
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=1049      # save at step 10490 (final)
SEQ=4094
GBS=1024
MBS=2
TP=1
NP=8

DATA="$BASE/data"
CKPT_DIR="$BASE/nemo_experiments/${NAME}/checkpoints"

# ========== Decay data blend: SFT 64 : L3 24 : code 8 : math 4 ==========
BLEND=""
# SFT-2605: 4 mix_sft shards, each weight 8 (= 32)
for s in 0 1 2 3; do
    BLEND="$BLEND 8 ${DATA}/mix_sft_tok/mix_sft_train_s${s}"
done
# SFT-Agent-2609: 4 mix_sft_agent shards, each weight 8 (= 32)
for s in 0 1 2 3; do
    BLEND="$BLEND 8 ${DATA}/mix_sft_agent_tok/mix_sft_agent_train_s${s}"
done
# L3: 8 p5b_l3 shards (s0-s7), each weight 3 (= 24)
for s in 0 1 2 3 4 5 6 7; do
    BLEND="$BLEND 3 ${DATA}/p5b_l3/p5b_l3_train_s${s}"
done
# Code: anneal_code (w=3) + r3_ultradata_code (w=5) (= 8)
BLEND="$BLEND 3 ${DATA}/anneal_code 5 ${DATA}/r3_sources/r3_ultradata_code"
# Math: anneal_math2 (w=3) + r3_ultradata_math (w=1) (= 4)
BLEND="$BLEND 3 ${DATA}/anneal_math2 1 ${DATA}/r3_sources/r3_ultradata_math"
BLEND="${BLEND# }"

# ========== 前置检查 ==========
# 1) GPU 0-7 全空（8 卡独占）
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU_BUSY" ]; then
    echo "❌ GPU $GPU_BUSY 非空 (used>1GB)，停手（stable phase 可能还没停？）" | tee "$LOGDIR/baize_p8_decay.log"
    exit 1
fi

# 2) Checkpoint at step 9441 must exist
STEP9441_CKPT="${CKPT_DIR}/iter_0009441"
if [ ! -d "$STEP9441_CKPT" ]; then
    echo "❌ Checkpoint not found: $STEP9441_CKPT" | tee "$LOGDIR/baize_p8_decay.log"
    echo "   Stable phase may not have reached step 9441 yet. Check:" | tee -a "$LOGDIR/baize_p8_decay.log"
    echo "   grep 'iteration' /tmp/baize_p8_train.log | tail -1" | tee -a "$LOGDIR/baize_p8_decay.log"
    echo "   Available checkpoints:" | tee -a "$LOGDIR/baize_p8_decay.log"
    ls -d "${CKPT_DIR}"/iter_* 2>/dev/null | tee -a "$LOGDIR/baize_p8_decay.log" || echo "   (none)" | tee -a "$LOGDIR/baize_p8_decay.log"
    exit 1
fi

# 3) Clean up any checkpoints AFTER 9441 (from stable phase running past 9441)
echo " Checking for stale checkpoints after step 9441..."
for ckpt in "${CKPT_DIR}"/iter_*; do
    [ -d "$ckpt" ] || continue
    iter=$(basename "$ckpt" | sed 's/iter_0*//')
    if [ "$iter" -gt 9441 ] 2>/dev/null; then
        echo " ⚠️ Removing stale checkpoint: $(basename "$ckpt") (stable phase ran past 9441)"
        rm -rf "$ckpt"
    fi
done
# 4) blend 中每个 .bin/.idx 齐备
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
# 5) tokenizer
[ -f "${DATA}/tokenizer_eod/tokenizer.json" ] || { echo "❌ 缺 tokenizer_eod"; exit 1; }

# ========== 启动 decay phase 训练 ==========
SUM="$LOGDIR/baize_p8_decay.log"
LOG="$LOGDIR/baize_p8_decay_train.log"
echo "===== P-8 decay START @ $(date '+%F %T') ITERS=${ITERS} WARMUP=${WARMUP} DECAY=${DECAY} LR=${LR} min=${MIN_LR} save=${SAVE_INTERVAL} optimizer=dist_muon =====" > "$SUM"
echo "  NP=${NP} TP=${TP} DP=$((NP/TP))" >> "$SUM"
echo "  resume from: ${STEP9441_CKPT}" >> "$SUM"
echo "  decay blend: SFT 64% + L3 24% + code 8% + math 4%" >> "$SUM"

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
echo "===== P-8 decay END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC


