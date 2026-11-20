#!/bin/bash
# BaiZe Stage(i) S2 stable-LR 扫描（WSD 固定）：7 点，逐点 5000 步，8 卡 TP1/DP8 串行。
#   2e-4 / 3e-4 / 4e-4 / 5e-4 / 6e-4 / 8e-4 / 1e-3
# 每点日志独立 /tmp/baize_<name>.log，汇总写 /tmp/baize_s2_sweep.log。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
LOGDIR=/tmp

declare -a LRS=(2e-4 3e-4 4e-4 5e-4 6e-4 8e-4 1e-3)
declare -a NAMES=(s2_01 s2_02 s2_03 s2_04 s2_05 s2_06 s2_07)
declare -a PORTS=(29661 29662 29663 29664 29665 29666 29667)

SUM="${LOGDIR}/baize_s2_sweep.log"
echo "===== S2 LR sweep START @ $(date '+%F %T') =====" > "$SUM"

for i in "${!LRS[@]}"; do
    LR="${LRS[$i]}"
    NAME="${NAMES[$i]}"
    PORT="${PORTS[$i]}"
    LOG="${LOGDIR}/baize_${NAME}.log"
    echo "===== ${NAME} LR=${LR} START @ $(date '+%F %T') =====" >> "$SUM"
    TRAIN_ITERS=5000 LR="${LR}" bash "${BASE}/scripts/train.sh" mamba2 "${NAME}" "${PORT}" 8 > "$LOG" 2>&1
    RC=$?
    FINAL=$(grep -oE 'iteration +5000/ +5000.*' "$LOG" | tail -n1)
    NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    echo "  rc=${RC} | ${FINAL}" >> "$SUM"
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected!" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
done
echo "===== S2 LR sweep ALL DONE @ $(date '+%F %T') =====" >> "$SUM"