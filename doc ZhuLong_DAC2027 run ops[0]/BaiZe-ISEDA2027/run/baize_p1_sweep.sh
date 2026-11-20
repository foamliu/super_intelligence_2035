#!/bin/bash
# BaiZe Stage(i) R2 P-1：LR 网格向上扩展（WSD 固定），3 点 × 5000 步，8 卡 TP1/DP8 串行。
#   LR ∈ {1.5e-3, 2e-3, 3e-3}。其余超参与 Round 1 S2 完全一致（纯 L3 主体、min_lr=3e-5、
#   WSD warmup=250/decay=500、GBS=8、seq=4094、bf16、seed=1234）。
#   目的：判定 Round 1 的 LR 最优 1e-3 是否落在网格边界（S2 七点 loss 单调改善到 1e-3）。
#   ⚠️ 若某点 loss 发散 / 出现 NaN，不重试超过 1 次——发散本身就是结论（= LR 上界），标 DIVERGED。
# 每点日志独立 /tmp/baize_<name>.log，汇总写 /tmp/baize_p1_sweep.log。
# 启动：setsid bash baize_p1_sweep.sh & （PPID=1 真后台，勿用裸 nohup &）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
LOGDIR=/tmp

declare -a LRS=(1.5e-3 2e-3 3e-3)
declare -a NAMES=(p1_1p5e3 p1_2e3 p1_3e3)
declare -a PORTS=(29711 29712 29713)

SUM="${LOGDIR}/baize_p1_sweep.log"
echo "===== P-1 LR grid-extend sweep START @ $(date '+%F %T') =====" > "$SUM"
echo "  (pure L3 ultrafineweb_l3_qa, min_lr=3e-5, WSD warmup250/decay500, GBS=8, seq=4094, bf16, seed=1234, 5000 steps)" >> "$SUM"

for i in "${!LRS[@]}"; do
    LR="${LRS[$i]}"
    NAME="${NAMES[$i]}"
    PORT="${PORTS[$i]}"
    LOG="${LOGDIR}/baize_${NAME}.log"
    echo "===== ${NAME} LR=${LR} START @ $(date '+%F %T') =====" >> "$SUM"
    TRAIN_ITERS=5000 LR="${LR}" bash "${BASE}/scripts/train.sh" mamba2 "${NAME}" "${PORT}" 8 > "$LOG" 2>&1
    RC=$?
    FINAL=$(grep -oE "iteration +5000/ +5000.*" "$LOG" | tail -n1)
    NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    echo "  rc=${RC} | ${FINAL}" >> "$SUM"
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected → DIVERGED（LR 上界证据）" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
done
echo "===== P-1 LR grid-extend sweep ALL DONE @ $(date '+%F %T') =====" >> "$SUM"