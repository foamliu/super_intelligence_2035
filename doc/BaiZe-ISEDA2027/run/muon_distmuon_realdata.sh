#!/bin/bash
# dist_muon (layer-wise distributed) 重测 — 1000 步, P-5b 真实数据
# 与上一轮 muon vs adamw A/B 逐字一致，唯一差异 = optimizer dist_muon
# 参数: --gbs 16 --mbs 1 --seq 4094 --iters 1000 --seed 1234 --data p5b_l3_blend
# 8 GPU · TP=1 · DP=8 · bf16
# 启动: setsid bash muon_distmuon_realdata.sh > /tmp/muon_distmuon_realdata.log 2>&1 < /dev/null &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export LD_LIBRARY_PATH="${PY}/../lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}"
export MASTER_ADDR=127.0.0.1

# P-5b data blend (16 shards, equal weight 1 each) — 与上一轮逐字一致
BLEND=""
for i in $(seq 0 15); do
    BLEND="$BLEND 1 ${BASE}/data/p5b_l3/p5b_l3_train_s${i}"
done
TOKENIZER="${BASE}/data/tokenizer_eod"

# 超参（与上一轮 muon/adamw A/B 逐字一致，唯一差异 = optimizer=dist_muon）
ITERS=1000
GBS=16
MBS=1
SEQ=4094
TP=1
NPROC=8
SEED=1234
LR=3e-4
MIN_LR=3e-5
WARMUP=50
DECAY=200      # WSD 退火尾段
SAVE_INT=99999  # 不存 ckpt

SUM="$LOGDIR/muon_distmuon_realdata.sum"
: > "$SUM"
echo "===== dist_muon realdata 1000-step START @ $(date '+%F %T') =====" >> "$SUM"
echo "  8 GPU, TP=${TP} DP=${NPROC}, seq=${SEQ}, GBS=${GBS}, MBS=${MBS}, iters=${ITERS}, bf16, seed=${SEED}" >> "$SUM"
echo "  optimizer: dist_muon (layer-wise distributed)" >> "$SUM"
echo "  data: P-5b 16-shard blend (~20.6B tokens), tokenizer=DeepSeek_eod" >> "$SUM"
echo "  token/step=$((GBS*SEQ))=6.55M" >> "$SUM"
echo "  --- pre-flight GPU check ---" >> "$SUM"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv 2>&1 >> "$SUM"
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv 2>&1 >> "$SUM"

OPT="dist_muon"
NAME="distmuon"
LOG="$LOGDIR/muon_ab_realdata_${NAME}.log"
PEAK_FILE="$LOGDIR/muon_ab_realdata_${NAME}.peakmem"
: > "$PEAK_FILE"
echo "" >> "$SUM"
echo "===== ARM: ${NAME} (optimizer=${OPT}) START @ $(date '+%F %T') =====" >> "$SUM"

# 峰值显存监控
( MAX=0; while :; do
    USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
    [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED; echo "$MAX" > "$PEAK_FILE"; sleep 2
  done ) &
SP=$!

# 随机端口避免 EADDRINUSE
PORT=$("${PY}/python" -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")

cd "$BASE" || exit 1
"${PY}/torchrun" --nnodes=1 --nproc_per_node="$NPROC" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    pretrain_launcher.py \
    --arch mamba2 --name "muon_ab_realdata_${NAME}" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$TOKENIZER" \
    --train-data-path $BLEND \
    --tensor-parallel "$TP" \
    --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
    --eval-interval 9999 --eval-iters 0 --save-interval "$SAVE_INT" \
    --lr "$LR" --min-lr "$MIN_LR" --lr-warmup-iters "$WARMUP" \
    --lr-decay-iters "$DECAY" --lr-decay-style WSD \
    --seed "$SEED" --precision bf16_mixed \
    --optimizer "$OPT" > "$LOG" 2>&1
RC=$?
kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
PEAK=$(cat "$PEAK_FILE" 2>/dev/null)

echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK}" >> "$SUM"

if [ "$RC" -ne 0 ]; then
    echo "  ❌ FAILED — last 15 lines:" >> "$SUM"
    tail -15 "$LOG" >> "$SUM"
    echo "===== ARM: ${NAME} END (FAILED) @ $(date '+%F %T') =====" >> "$SUM"
    exit 1
fi

# 提取关键指标
echo "  --- loss curve (every 50/100 steps) ---" >> "$SUM"
for S in 10 50 100 150 200 300 400 500 600 700 800 900 1000; do
    LINE=$(grep -E "iteration +${S}/" "$LOG" | tail -n1)
    LOSS=$(echo "$LINE" | grep -oP 'lm loss: \K[0-9.Ee+-]+')
    GRAD=$(echo "$LINE" | grep -oP 'grad norm: \K[0-9.]+')
    echo "  iter ${S}: loss=${LOSS:-NA} grad_norm=${GRAD:-NA}" >> "$SUM"
done

# 稳态吞吐（最后 10 步）
echo "  --- steady-state throughput (last 10 iters) ---" >> "$SUM"
MS_LIST=$(grep -E 'iteration +' "$LOG" | tail -10 | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
TFLOP_LIST=$(grep -E 'iteration +' "$LOG" | tail -10 | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
MS_COUNT=$(echo "$MS_LIST" | grep -c .)
if [ "$MS_COUNT" -gt 0 ]; then
    AVG_MS=$(echo "$MS_LIST" | awk '{s+=$1;n++} END {printf "%.1f",s/n}')
    AVG_TPS=$(awk -v t="$((GBS*SEQ))" -v m="$AVG_MS" 'BEGIN {printf "%.0f",t/(m/1000)}')
    echo "  ★ avg ms/iter: ${AVG_MS} → tok/s: ${AVG_TPS}" >> "$SUM"
fi
if [ -n "$TFLOP_LIST" ]; then
    echo "  avg TFLOP/s/GPU: $(echo "$TFLOP_LIST" | awk '{s+=$1;n++} END {printf "%.1f",s/n}')" >> "$SUM"
fi

# VRAM from training log
VRAM_LINE=$(grep 'memory (MB)' "$LOG" | tail -n1)
echo "  VRAM: ${VRAM_LINE:-NA}" >> "$SUM"

# NaN check
NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
if [ "${NAN:-0}" -gt 0 ]; then
    echo "  ⚠️ NaN iterations detected!" >> "$SUM"
fi

# bridge_compat routing confirmation
echo "  --- bridge_compat routing ---" >> "$SUM"
grep 'bridge_compat.*muon' "$LOG" | head -1 >> "$SUM"

echo "===== ARM: ${NAME} END (OK) @ $(date '+%F %T') =====" >> "$SUM"
echo "" >> "$SUM"
echo "===== dist_muon realdata 1000-step ALL DONE @ $(date '+%F %T') =====" >> "$SUM"
echo "  Summary file: $SUM" >> "$SUM"
echo "  Log:          $LOG" >> "$SUM"
