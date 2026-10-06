#!/bin/bash
# BaiZe Stage(i) S3 关键轴微调（S2 胜出 LR 基础上，每次只动一个变量），5 组，逐组 5000 步，8 卡 TP1/DP8 串行。
#   S3-01  WSD 参考（胜出 LR，warmup250/decay500/min_lr3e-5）—— S3 组内基线
#   S3-02  cosine（调度族对比）
#   S3-03  decay ratio 5%（DECAY_ITERS=250，默认 10%=500）
#   S3-04  warmup 固定 2000 步（占比 5%=250 vs 固定 2000）
#   S3-05  min_lr 1e-5（默认 3e-5）
# 每点日志独立 /tmp/baize_<name>.log，汇总写 /tmp/baize_s3_sweep.log。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
LOGDIR=/tmp

# ✅ S2 胜出 stable LR = 1e-3（final loss 2.7627 为 7 点最低，单调递减：2e-4 2.9037 → 3e-4 2.8462 → 4e-4 2.8167 → 5e-4 2.7981 → 6e-4 2.7783 → 8e-4 2.7700 → 1e-3 2.7627；1e-3 退火尾段 2.92@4440 → 2.76@5000 骤降反超 8e-4）。
WINNER_LR="1e-3"

declare -a NAMES=(s3_01 s3_02 s3_03 s3_04 s3_05)
declare -a PORTS=(29671 29672 29673 29674 29675)

SUM="${LOGDIR}/baize_s3_sweep.log"
echo "===== S3 key-axis sweep START @ $(date '+%F %T') (WINNER_LR=${WINNER_LR}) =====" > "$SUM"

run() {  # $1=NAME $2=PORT  (其余超参用环境变量覆盖，见 train.sh)
    local NAME="$1" PORT="$2"
    LOG="${LOGDIR}/baize_${NAME}.log"
    echo "===== ${NAME} START @ $(date '+%F %T') DECAY_STYLE=${DECAY_STYLE:-WSD} WARMUP=${WARMUP_ITERS:-250} DECAY=${DECAY_ITERS:-500} MIN_LR=${MIN_LR:-3e-5} =====" >> "$SUM"
    TRAIN_ITERS=5000 LR="${WINNER_LR}" \
        DECAY_STYLE="${DECAY_STYLE:-WSD}" \
        WARMUP_ITERS="${WARMUP_ITERS:-250}" \
        DECAY_ITERS="${DECAY_ITERS:-500}" \
        MIN_LR="${MIN_LR:-3e-5}" \
        bash "${BASE}/scripts/train.sh" mamba2 "${NAME}" "${PORT}" 8 > "$LOG" 2>&1
    RC=$?
    FINAL=$(grep -oE 'iteration +5000/ +5000.*' "$LOG" | tail -n1)
    NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    echo "  rc=${RC} | ${FINAL}" >> "$SUM"
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected!" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
}

# S3-01：WSD 参考（默认 warmup250/decay500/min_lr3e-5）
DECAY_STYLE=WSD; WARMUP_ITERS=250; DECAY_ITERS=500; MIN_LR=3e-5
run s3_01 29671

# S3-02：cosine（decay 忽略，全称 cosine 到 train_iters）
DECAY_STYLE=cosine; WARMUP_ITERS=250; DECAY_ITERS=500; MIN_LR=3e-5
run s3_02 29672

# S3-03：decay ratio 5%（DECAY_ITERS=250）
DECAY_STYLE=WSD; WARMUP_ITERS=250; DECAY_ITERS=250; MIN_LR=3e-5
run s3_03 29673

# S3-04：warmup 固定 2000 步
DECAY_STYLE=WSD; WARMUP_ITERS=2000; DECAY_ITERS=500; MIN_LR=3e-5
run s3_04 29674

# S3-05：min_lr 1e-5
DECAY_STYLE=WSD; WARMUP_ITERS=250; DECAY_ITERS=500; MIN_LR=1e-5
run s3_05 29675

echo "===== S3 key-axis sweep ALL DONE @ $(date '+%F %T') =====" >> "$SUM"