#!/bin/bash
# BaiZe Stage(i) S5 长跑收敛曲线 + 多 seed 复现（S4 胜出配置），4 组，8 卡 TP1/DP8。
#   S5-01  胜出配置从零 **20000 步**（论文 loss 收敛曲线，数据 = 700M 补切集）
#   S5-02…04  胜出配置 3 seed × 5000 步（可复现，报 loss 均值±σ）
#
# ⚠️ TODO（回填前勿启动）：本脚本所有「胜出占位」须在 S3/S4 全部 final@5000 回收后，
#   据 `/tmp/baize_s3_sweep.log` + `/tmp/baize_s4_sweep.log` 回填（S3 定调度族/decay/warmup/min_lr，
#   S4 定退火数据混合）。当前为 S4 脚本同一套占位（stable LR=1e-3 已由 S2 定）。
#
# 数据口径（多 seed 与长跑）：
#   长跑 20000 步 × GBS8 × seq4094 = 655.36M token；每 seed 5000 步 = 163.84M token。
#   L3 主体 `data/ultrafineweb_l3_qa`(164.75M) 仅够 5000 步/seed，长跑须用
#   `data/ultrafineweb_l3_qa_700m`(742M) 以保证 20000 步纯 L3 不重复（655M<742M ✓）。
#   若 S4 胜出含 code/math 混合，长跑需在 700M 主体上按 blend 平铺；⚠️ code 90M 够 10%×655M=65.5M，
#   但 math 仅 8.5M < 4%×655M=26M —— 长跑混 math 会耗尽，需 S4→S5 交接时按实际胜出比例核算（见 TODO）。
#
# 启动请用 `setsid bash baize_s5_sweep.sh &`（PPID=1 真后台；run_commands 30s 超时会 kill 进程组，
#   nohup & 不足以保活，详见 MEMORY 落坑记录）。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

L3_700="$BASE/data/ultrafineweb_l3_qa_700m"   # 742M token，长跑主体
L3_165="$BASE/data/ultrafineweb_l3_qa"        # 164.75M，多 seed 短地平线主体
CODE="$BASE/data/anneal_code"                  # 90.34M
MATH="$BASE/data/anneal_math"                  # 8.51M

# ⚠️ TODO：S3/S4 全回收后回填（当前 = S4 脚本同一套占位，勿视为定论）。
WINNER_LR="1e-3"          # S2 已定；S3 后若增量扫 1.2e-3/1.5e-3 反超则更新
WINNER_DECAY_STYLE="WSD"  # S3-01(WSD) vs S3-02(cosine) 胜出
WINNER_WARMUP="250"       # S3-04（250 vs 2000）胜出
WINNER_DECAY="500"        # S3-03（10%=500 vs 5%=250）胜出
WINNER_MIN_LR="1e-5"      # ✅ S3-05（3e-5 vs 1e-5）：1e-5 胜出（2.764702 vs 2.767915）
# 退火数据混合（S4-01 纯L3 / S4-02 L3+code / S4-03 L3+code+math 胜出后回填；默认纯 L3）。
# BLEND_MAIN / BLEND_SEEDS：`--train-data-path` 平铺参数（[w p w p …]，单前缀只传 p）。
BLEND_MAIN="${L3_700}"
BLEND_SEEDS="${L3_165}"

# 多 seed 复现三个种子（可复现；S5-01 用默认 seed=1234 与全期对标）
SEEDS=(44 777 2024)

declare -a NAMES=(s5_01 s5_02 s5_03 s5_04)
declare -a PORTS=(29691 29692 29693 29694)

SUM="$LOGDIR/baize_s5_sweep.log"
echo "===== S5 long-run + multi-seed START @ $(date '+%F %T') (WINNER=${WINNER_LR}/${WINNER_DECAY_STYLE}/warmup${WINNER_WARMUP}/decay${WINNER_DECAY}/min${WINNER_MIN_LR}) =====" > "$SUM"

run() {  # $1=NAME $2=PORT $3=ITERS $4=SEED  其余为 blend 平铺参数
    local NAME="$1" PORT="$2" ITERS="$3" SEED="$4"; shift 4
    local LOG="$LOGDIR/baize_${NAME}.log"
    echo "===== ${NAME} START @ $(date '+%F %T') ITERS=${ITERS} SEED=${SEED} BLEND=[$*] =====" >> "$SUM"
    cd "$BASE" || exit 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path "$@" \
        --tensor-parallel 1 \
        --train-iters "$ITERS" --global-batch-size 8 --micro-batch-size 1 --seq-length 4094 \
        --eval-interval 250 --eval-iters 0 \
        --lr "$WINNER_LR" --min-lr "$WINNER_MIN_LR" \
        --lr-warmup-iters "$WINNER_WARMUP" --lr-decay-iters "$WINNER_DECAY" --lr-decay-style "$WINNER_DECAY_STYLE" \
        --seed "$SEED" \
        --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?
    local FINAL; FINAL=$(grep -oE "iteration +${ITERS}/ +${ITERS}.*" "$LOG" | tail -n1)
    local NAN; NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    echo "  rc=${RC} | ${FINAL}" >> "$SUM"
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected!" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
}

# S5-01：胜出配置 20000 步长跑（seed=1234 与 S1/S2/S3/S4 对标）
run s5_01 29691 20000 1234 $BLEND_MAIN

# S5-02…04：胜出配置 3 seed × 5000 步（可复现，报 loss 均值±σ）
run s5_02 29692 5000 "${SEEDS[0]}" $BLEND_SEEDS
run s5_03 29693 5000 "${SEEDS[1]}" $BLEND_SEEDS
run s5_04 29694 5000 "${SEEDS[2]}" $BLEND_SEEDS

echo "===== S5 long-run + multi-seed ALL DONE @ $(date '+%F %T') =====" >> "$SUM"