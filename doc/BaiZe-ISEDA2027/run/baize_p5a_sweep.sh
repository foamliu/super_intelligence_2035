#!/bin/bash
# BaiZe Stage(i) R2 P-5a：GBS × LR 扫描（判定 GBS=1024 生产口径下最优 LR 是否从 GBS=8 的 1e-3 右移）。
#   固定 token 预算 164M（按 token 匹配，非按 step）；WSD 按 5%/85%/10% 形状等比重标定。
#   口径与 P-1 的 GBS=8 基线一致（纯 L3 ultrafineweb_l3_qa、min_lr=3e-5、WSD、seed=1234、seq=4094、bf16、TP1/DP8）。
#   GBS=8 基线 4 点（1e-3/1.5e-3/2e-3/3e-3）已在 P-1 完成（谷底 1e-3，见 ROUND2 报告）。
#   本脚本跑 GBS∈{64,256,1024} × LR∈{1e-3,2e-3,4e-3}（4e-3 为向上新探点，P-1 最高只到 3e-3）。
#   WSD 等比重标定：GBS=64→625步(warmup31/decay63) | GBS=256→156步(warmup8/decay15) | GBS=1024→39步(warmup2/decay4)
#   ⚠️ 若某点 NaN/发散 → 不重试超 1 次，标 DIVERGED（= 该 GBS 下 LR 上界证据）。
# 每点日志 /tmp/baize_<name>.log，汇总 /tmp/baize_p5a_sweep.log。
# 启动：setsid bash baize_p5a_sweep.sh & （PPID=1 真后台，勿用裸 nohup &）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

declare -a GBSs=(64 256 1024)
declare -a STEPS=(625 156 39)
declare -a WARMS=(31 8 2)
declare -a DECAYS=(63 15 4)
declare -a LRS=(1e-3 2e-3 4e-3)

SUM="$LOGDIR/baize_p5a_sweep.log"
echo "===== P-5a GBS×LR sweep START @ $(date '+%F %T') =====" > "$SUM"
echo "  (164M token/run; pure L3; min_lr=3e-5; WSD 5%/85%/10% rescaled; seed=1234; seq=4094; TP1/DP8; bf16)" >> "$SUM"

PORT=29740
for i in "${!GBSs[@]}"; do
    GBS="${GBSs[$i]}"; STEPS="${STEPS[$i]}"; WARM="${WARMS[$i]}"; DECAY="${DECAYS[$i]}"
    for LR in "${LRS[@]}"; do
        NAME="p5a_g${GBS}_lr${LR//./p}"
        LOG="$LOGDIR/baize_${NAME}.log"
        PORT=$((PORT+1))
        echo "----- ${NAME} GBS=${GBS} steps=${STEPS} LR=${LR} warmup=${WARM} decay=${DECAY} START @ $(date '+%F %T') -----" >> "$SUM"
        TRAIN_ITERS="$STEPS" LR="$LR" MIN_LR=3e-5 WARMUP_ITERS="$WARM" DECAY_ITERS="$DECAY" \
          GBS="$GBS" bash "$BASE/scripts/train.sh" mamba2 "$NAME" "$PORT" 8 > "$LOG" 2>&1
        RC=$?
        FINAL=$(grep -oE "iteration +${STEPS}/ +${STEPS} \|.*" "$LOG" | tail -n1)
        NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
        echo "  rc=${RC} | ${FINAL}" >> "$SUM"
        if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN → DIVERGED（该 GBS 下 LR 上界证据）" >> "$SUM"; fi
        echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
    done
done
echo "===== P-5a GBS×LR sweep ALL DONE @ $(date '+%F %T') =====" >> "$SUM"