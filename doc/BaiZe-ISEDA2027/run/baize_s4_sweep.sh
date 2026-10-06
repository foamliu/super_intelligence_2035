#!/bin/bash
# BaiZe Stage(i) S4 退火数据混合消融（S3 胜出配置上，只动「退火数据混合」一个变量），3 组，逐组 5000 步，8 卡 TP1/DP8 串行。
#   S4-01  纯 L3 高质量子集（基线，退火数据不加码）
#   S4-02  L3 + 代码（UltraData-Code，退火数据混 10% code）
#   S4-03  L3 + 代码 + 数学（UltraData-Math，退火数据混 10% code + 4% math）
#
# 实现口径（短地平线代理，详见 MEMORY）：本 recipe 的 GPTDatasetConfig 仅支持单次静态 blend
#   （`--train-data-path [w1 p1 w2 p2 ...]`，megatron 扁平 weight/prefix 格式，已由 launcher nargs="*"
#   + recipe get_blend_fields_from_data_paths 支持）。「decay 尾段混入」在 5000 步短地平线消融中用
#   **全段静态 blend** 近似（S4-02/03 全程混 code/math），量化「退火数据加码是否压低 final loss」；
#   真正的两步退火切数据（stable 纯 L3 → decay 段切 blend，需 ckpt 交接）留待 S5 长跑（预算允许时）。
#
# 数据（已切，无需再下载）：
#   L3   data/ultrafineweb_l3_qa     200000 docs / 164.75M token
#   code data/anneal_code             66383 docs /  90.34M token
#   math data/anneal_math            101380 docs /   8.51M token
# 5000 步 × GBS8 × seq4094 = 163.76M token/组；blend 内各源 token 余量足够（code 16.4M≤90M、math 6.55M≤8.5M）。
#
# 本脚本 torchrun 直驱（不经 scripts/train.sh，因其 data-path 硬编码单前缀），8 卡 TP1/DP8。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

L3="$BASE/data/ultrafineweb_l3_qa"
CODE="$BASE/data/anneal_code"
MATH="$BASE/data/anneal_math"

# ⚠️ TODO：S3 五组 final@5000 全部回收后，据 `/tmp/baize_s3_sweep.log` 回填下方「胜出关键轴」占位。
#   （S2 已定 stable LR=1e-3；S3 在 1e-3 上单变量：调度族 WSD/cosine、decay 5%、warmup 2000、min_lr 1e-5。）
WINNER_LR="1e-3"          # TODO: S3 后若增量扫 1.2e-3/1.5e-3 反超则更新
WINNER_DECAY_STYLE="WSD"  # TODO: S3-01(WSD) vs S3-02(cosine) 胜出
WINNER_WARMUP="250"       # TODO: S3-04（250 vs 2000）胜出
WINNER_DECAY="500"        # TODO: S3-03（10%=500 vs 5%=250）胜出
WINNER_MIN_LR="1e-5"      # ✅ S3-05（3e-5 vs 1e-5）：1e-5 胜出（2.764702 vs 2.767915，Δ~0.003 略优于 3e-5，点估计更低）

declare -a NAMES=(s4_01 s4_02 s4_03)
declare -a PORTS=(29681 29682 29683)

SUM="$LOGDIR/baize_s4_sweep.log"
echo "===== S4 anneal-data-ablation sweep START @ $(date '+%F %T') (WINNER=${WINNER_LR}/${WINNER_DECAY_STYLE}/warmup${WINNER_WARMUP}/decay${WINNER_DECAY}/min${WINNER_MIN_LR}) =====" > "$SUM"

run() {  # $1=NAME $2=PORT  其余为 blend 平铺参数（[w p w p ...]，单前缀时只传 p）
    local NAME="$1" PORT="$2"; shift 2
    local LOG="$LOGDIR/baize_${NAME}.log"
    echo "===== ${NAME} START @ $(date '+%F %T') BLEND=[$*] =====" >> "$SUM"
    cd "$BASE" || exit 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path "$@" \
        --tensor-parallel 1 \
        --train-iters 5000 --global-batch-size 8 --micro-batch-size 1 --seq-length 4094 \
        --eval-interval 250 --eval-iters 0 \
        --lr "$WINNER_LR" --min-lr "$WINNER_MIN_LR" \
        --lr-warmup-iters "$WINNER_WARMUP" --lr-decay-iters "$WINNER_DECAY" --lr-decay-style "$WINNER_DECAY_STYLE" \
        --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?
    local FINAL; FINAL=$(grep -oE 'iteration +5000/ +5000.*' "$LOG" | tail -n1)
    local NAN; NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    echo "  rc=${RC} | ${FINAL}" >> "$SUM"
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected!" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
}

# S4-01：纯 L3 高质量子集（单前缀，退火数据基线）
run s4_01 29681 "$L3"

# S4-02：L3 + 代码（90:10）
run s4_02 29682 90 "$L3" 10 "$CODE"

# S4-03：L3 + 代码 + 数学（86:10:4）
run s4_03 29683 86 "$L3" 10 "$CODE" 4 "$MATH"

echo "===== S4 anneal-data-ablation ALL DONE @ $(date '+%F %T') =====" >> "$SUM"