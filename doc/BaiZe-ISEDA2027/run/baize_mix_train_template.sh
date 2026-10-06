#!/bin/bash
# BaiZe 数据配比实验（§0.6-B）：Stable / Decay 段配比搜索短跑模板。
#
# 口径（运维 2026-10-05 批准）：6 卡 · TP1/DP6 · seq=4094 · mb=1 · GBS=1024（与既有基线对齐）· 5000 步短地平线。
# GPU：CUDA_VISIBLE_DEVICES=2,3,4,5,6,7（GPU2-7，data 名下）。
#
# 用法：复制本模板 → 改 BLEND / NAME / WARMUP / DECAY → setsid bash baize_mix_<arm>.sh &
#   - Stable 段臂：用 base + code + math blend，WSD warmup=250/decay=0（纯 stable，不退火）
#   - Decay 段臂：用 L3 + SFT + code + math blend，WSD warmup=250/decay=500（带退火）
#
# 代理指标：每臂跑完 → ckpt → HF → lm_eval（Table 2 的 8 个 + Table 3 的 6 个）。
# 评测基建复用 pretrain 已打通的 pipeline（见 MEMORY_PRETRAIN_2B.md P-6②）。
#
# ⚠️ 前置检查：GPU2-7 空（nvidia-smi --query-compute-apps）+ .bin/.idx 齐备。
# ⚠️ 铁律：不 kill pretrain 进程；不碰 GPU0-1。
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export CUDA_VISIBLE_DEVICES=2,3,4,5,6,7

# ========== 实验参数（每臂修改这里）==========
NAME="mix_stable_s0a"          # 臂名（改！）
PORT=29950                     # master_port（每臂不同，避免冲突）
ITERS=5000                     # 短地平线
WARMUP=250                     # 5% warmup
DECAY=0                        # Stable 段=0（不退火）；Decay 段=500
LR="1e-3"
MIN_LR="1e-5"
SAVE_INTERVAL=5000             # 只存 final ckpt（5000 步），供 lm_eval
SEQ=4094
GBS=1024
MBS=1
TP=1
NP=6                           # nproc_per_node=6（DP6）

# ========== 数据 blend（每臂修改这里）==========
# Megatron 扁平 weight/prefix 平铺：[w0, prefix0, w1, prefix1, ...]
# 权重是相对值，megatron 内部归一化。
# 示例：Stable S0a = web(base):code:math = 88:8:4
DATA="$BASE/data"
BLEND="88 ${DATA}/mix_base/mix_base_train_s0 88 ${DATA}/mix_base/mix_base_train_s1 88 ${DATA}/mix_base/mix_base_train_s2 88 ${DATA}/mix_base/mix_base_train_s3 8 ${DATA}/anneal_code 4 ${DATA}/anneal_math2"

# ========== 前置检查 ==========
# 1) GPU2-7 空
GPU_PROCS=$(ssh -o StrictHostKeyChecking=no localhost 'nvidia-smi --query-compute-apps=pid --format=csv,noheader' 2>/dev/null | wc -l)
# 注：本脚本在 .29 上跑，直接查本机
GPU_PROCS=$("$(dirname "$PY")"/nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
if [ "$GPU_PROCS" -gt 0 ]; then
    echo "⚠️ GPU 上有 $GPU_PROCS 个进程，检查是否在 GPU2-7（可能 pretrain 在 GPU0-1）" | tee -a "$SUM"
    # 进一步检查 GPU2-7 是否空
    GPU2_7=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '$1>=2 && $1<=7 {print $2}' | grep -v '^0' | wc -l)
    if [ "$GPU2_7" -gt 0 ]; then
        echo "❌ GPU2-7 非空，停手（不 kill 对方）" | tee -a "$SUM"; exit 1
    fi
fi

# 2) blend 中每个 .bin/.idx 齐备
for prefix in $(echo "$BLEND" | awk 'NR%2==0'); do
    for ext in bin idx; do
        [ -f "${prefix}.${ext}" ] || { echo "❌ 缺 ${prefix}.${ext}" | tee -a "$SUM"; exit 1; }
    done
done

# ========== 启动训练 ==========
SUM="$LOGDIR/baize_${NAME}.log"
LOG="$LOGDIR/baize_${NAME}_train.log"
echo "===== mix ${NAME} START @ $(date '+%F %T') ITERS=${ITERS} GBS=${GBS} TP=${TP} DP=${NP} seq=${SEQ} LR=${LR} warmup=${WARMUP} decay=${DECAY} =====" > "$SUM"
echo "  BLEND=[$BLEND]" >> "$SUM"
echo "  CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}" >> "$SUM"

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
    --precision bf16_mixed > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" >> "$SUM"
echo "===== mix ${NAME} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC
