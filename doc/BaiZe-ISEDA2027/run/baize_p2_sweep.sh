#!/bin/bash
# BaiZe Stage(i) R2 P-2：补 2 个新 seed（→ n=5），胜出配置 5000 步 × 2，8 卡 TP1/DP8 串行。
#   目的：把 min_lr 1e-5 vs 3e-5 的 Δ≈0.003 结论的 σ 压小 / 证实其落在 run-to-run 噪声内。
#   胜出配置（与 Round 1 S5 3-seed 完全同口径）：LR=1e-3 / WSD / warmup=250 / decay=500 / min_lr=1e-5
#   / 退火混合 L3(86%)+code(10%)+math(4%)，GBS=8 / seq=4094 / bf16。新 seed = 7 与 2025。
# 启动：setsid bash baize_p2_sweep.sh & （PPID=1 真后台，勿用裸 nohup &）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

L3_165="$BASE/data/ultrafineweb_l3_qa"
CODE="$BASE/data/anneal_code"
MATH="$BASE/data/anneal_math"

WINNER_LR="1e-3"
WINNER_MIN_LR="1e-5"
WINNER_WARMUP="250"
WINNER_DECAY="500"
WINNER_DECAY_STYLE="WSD"

SEEDS=(7 2025)
NAMES=(p2_seed7 p2_seed2025)
PORTS=(29721 29722)

SUM="$LOGDIR/baize_p2_sweep.log"
echo "===== P-2 multi-seed (n=5, +2 new seeds) START @ $(date '+%F %T') (WINNER LR1e-3/WSD/warmup250/decay500/min1e-5, blend L3+code+math 86:10:4) =====" > "$SUM"

run() {  # $1=NAME $2=PORT $3=SEED
    local NAME="$1" PORT="$2" SEED="$3"
    local LOG="$LOGDIR/baize_${NAME}.log"
    echo "===== ${NAME} START @ $(date '+%F %T') SEED=${SEED} =====" >> "$SUM"
    cd "$BASE" || exit 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path 86 "${L3_165}" 10 "${CODE}" 4 "${MATH}" \
        --tensor-parallel 1 \
        --train-iters 5000 --global-batch-size 8 --micro-batch-size 1 --seq-length 4094 \
        --eval-interval 250 --eval-iters 0 \
        --lr "$WINNER_LR" --min-lr "$WINNER_MIN_LR" \
        --lr-warmup-iters "$WINNER_WARMUP" --lr-decay-iters "$WINNER_DECAY" --lr-decay-style "$WINNER_DECAY_STYLE" \
        --seed "$SEED" --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?
    local FINAL; FINAL=$(grep -oE "iteration +5000/ +5000.*" "$LOG" | tail -n1)
    local NAN; NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    echo "  rc=${RC} | ${FINAL}" >> "$SUM"
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected!" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
}

run "${NAMES[0]}" "${PORTS[0]}" "${SEEDS[0]}"
run "${NAMES[1]}" "${PORTS[1]}" "${SEEDS[1]}"

echo "===== P-2 multi-seed ALL DONE @ $(date '+%F %T') =====" >> "$SUM"