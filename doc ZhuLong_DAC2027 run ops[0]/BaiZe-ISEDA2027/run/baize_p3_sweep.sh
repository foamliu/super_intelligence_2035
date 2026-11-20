#!/bin/bash
# BaiZe Stage(i) R2 P-3：架构对比延长到 5000 步（dense vs hybrid，6 卡 TP1/DP6/GBS=6/seed=1234）。
#   与 Round 1 架构搜索对比（EXPERIMENTS_2B.md A1-01/A2-01，1000 步）同源同口径，仅 train-iters 1000→5000：
#     lr=3e-4 / cosine / min_lr=3e-5 / warmup=100 / seq=4096 / GBS=6 / mb=1 / bf16 / seed=1234。
#   ⚠️ 两架构统一 cosine：minicpm5 recipe 仅支持 cosine（distributed_fused_adam_with_cosine_annealing），
#      mamba2 也传 --lr-decay-style cosine 保证公平对比。
#   在 500/1000/2000/3000/5000 步各记一次 lm loss（两条曲线）。
#   ⚠️ dense 若 >30min 无法启动 → 记原因并跳过（P-3 降级为 hybrid 单侧延长）。
# 启动：setsid bash baize_p3_sweep.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

L3="$BASE/data/ultrafineweb_l3_qa"

SUM="$LOGDIR/baize_p3_sweep.log"
echo "===== P-3 arch-comp 5000-step START @ $(date '+%F %T') (dense=minicpm5 / hybrid=mamba2, 6卡/GBS=6/cosine/lr3e-4/warmup100/seq4096/seed1234) =====" > "$SUM"

run() {  # $1=ARCH $2=NAME $3=PORT
    local ARCH="$1" NAME="$2" PORT="$3"
    local LOG="$LOGDIR/baize_${NAME}.log"
    echo "===== ${NAME} (arch=${ARCH}) START @ $(date '+%F %T') =====" >> "$SUM"
    cd "$BASE" || exit 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node=6 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch "$ARCH" --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path "$L3" \
        --tensor-parallel 1 \
        --train-iters 5000 --global-batch-size 6 --micro-batch-size 1 --seq-length 4096 \
        --eval-interval 250 --eval-iters 0 \
        --lr 3e-4 --min-lr 3e-5 --lr-warmup-iters 100 --lr-decay-iters 1000 --lr-decay-style cosine \
        --seed 1234 --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?
    echo "  rc=${RC}" >> "$SUM"
    # 记录 500/1000/2000/3000/5000 步 loss（eval 关闭，取训练 lm loss）
    for S in 500 1000 2000 3000 5000; do
        local L
        L=$(grep -oE "iteration +${S}/ +5000 .*lm loss: [0-9.Ee+-]+" "$LOG" | tail -n1 | grep -oE "lm loss: [0-9.Ee+-]+")
        echo "  iter ${S}: ${L:-NA}" >> "$SUM"
    done
    local NAN; NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    if [ "${NAN:-0}" -gt 0 ]; then echo "  ⚠️ NaN iterations detected!" >> "$SUM"; fi
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
}

run minicpm5 p3_dense 29731
run mamba2 p3_hybrid 29732

echo "===== P-3 arch-comp ALL DONE @ $(date '+%F %T') =====" >> "$SUM"