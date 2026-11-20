#!/bin/bash
# BaiZe Stage(i) R2 P-5b：训练量 scaling 曲线（loss-vs-tokens，log-x，决定 P-8 token 预算）。
# 从零训练，用 P-5a 定的 GBS=1024 / LR=1e-3 / min_lr=1e-5 / WSD，纯 L3 8 分片 1:1 等权 blend。
# 记录点（token → 步）：655M→156 / 1.3B→310 / 2.6B→620 / 5.2B→1240 / 10.5B→2505 / 20B→4771。
#
# 依赖：baize_p5b_tokenize.sh（s0..s7，10.2B）+ baize_p5b_tokenize_b2.sh（s8..s15，+10.2B）
#   已产出 data/p5b_l3/p5b_l3_train_s{0..15}.bin/.idx/.json（合计 ~20.6B token，覆盖 20B 目标）。
#
# ⚠️ 口径决策（详见 ROUND2 报告 P-5b 节）：
#   ① val loss = train/lm loss 代理（与既有 2.2054@655M 同口径；不接 held-out val，避免改 recipe + 加切验证片）。
#   ② loss-vs-tokens 曲线从训练日志（log-interval=10）读 6 个点的 lm loss + grad norm，无需 ckpt 即出曲线。
#   ③ checkpoint：--save-interval 156（每 ~655M token 一个），恰落在 6 个 2 倍等分点 156/312/624/1248/2496 + final 4771，
#      供 P-6 第 2 步「能力 vs token」（6 个 ckpt 跑 lm_eval）。模型-only torch_dist ckpt ≈4.4GB × ~30 ≈ 132GB。
#   ④ GBS=1024 绝对 loss 收敛是本次实验的第 2 个关键产出（首段 655M/1.3B 点直接量化），不预设结论。
#
# 启动：setsid bash baize_p5b_train.sh &（PPID=1 真后台；勿裸 nohup &）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

OUT="$BASE/data/p5b_l3"
NAME="p5b"
PORT=29801
ITERS=4771            # 20B token（GBS1024 × seq4094 = 4.192M token/步）
WARMUP=238            # 5% ≈ 238
DECAY=477             # 10% ≈ 477
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=156     # 每 ~655M token 一个 ckpt（对齐 6 个 2 倍等分点）

# 前置检查：16 分片 .bin/.idx/.json 齐备（batch1+batch2 分词未完成则拒绝启动）
for s in $(seq 0 15); do
    for ext in bin idx json; do
        [ -f "$OUT/p5b_l3_train_s${s}.${ext}" ] || { echo "❌ 缺 $OUT/p5b_l3_train_s${s}.${ext}（baize_p5b_tokenize[_b2].sh 未完成？）"; exit 1; }
    done
done

# 1:1 等权 blend（megatron 扁平 weight/prefix 平铺：[w p w p ...]）
BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

SUM="$LOGDIR/baize_p5b_train.log"
LOG="$LOGDIR/baize_${NAME}.log"
echo "===== P-5b train START @ $(date '+%F %T') ITERS=${ITERS} GBS=1024 LR=${LR} min=${MIN_LR} warmup=${WARMUP} decay=${DECAY} save-interval=${SAVE_INTERVAL} =====" > "$SUM"
echo "  BLEND=[$BLEND]" >> "$SUM"

cd "$BASE" || exit 1
"$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    pretrain_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$BASE/data/tokenizer_eod" \
    --train-data-path $BLEND \
    --tensor-parallel 1 \
    --train-iters "$ITERS" --global-batch-size 1024 --micro-batch-size 1 --seq-length 4094 \
    --eval-interval 250 --eval-iters 0 \
    --save-interval "$SAVE_INTERVAL" \
    --lr "$LR" --min-lr "$MIN_LR" \
    --lr-warmup-iters "$WARMUP" --lr-decay-iters "$DECAY" --lr-decay-style WSD \
    --seed 1234 \
    --precision bf16_mixed > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== P-5b train END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC