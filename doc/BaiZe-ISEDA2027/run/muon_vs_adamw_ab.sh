#!/bin/bash
# Muon vs AdamW A/B 实验（用户 2026-10-09 指令）
# 两臂各 1000 步 · GBS=16 · seq=4094 · bf16 · 同 seed=1234 · mock 数据
# 对比 loss 曲线（附 grad-norm / 吞吐 / 显存）
# 8 GPU · TP=1 · DP=8 · MBS=1（每 GPU 2 个 micro-batch）
# 注：真实数据因 MegatronPretrainingSampler "single" 模式
#     consumed_samples >= total_samples 断言失败（16000==16000），
#     改用 --mock 数据（smoke test 已验证 Muon 可跑通）。
# 启动: setsid bash muon_vs_adamw_ab.sh > /tmp/muon_vs_adamw_ab.log 2>&1 < /dev/null &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export LD_LIBRARY_PATH="${PY}/../lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}"
export MASTER_ADDR=127.0.0.1

# 超参（两臂共用，唯一差异 = optimizer）
# 注：seq=4094 为本线固定口径（非 4096；改 seq 需同步改 recipe provider）
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

SUM="$LOGDIR/muon_vs_adamw_ab.sum"
: > "$SUM"
echo "===== Muon vs AdamW A/B START @ $(date '+%F %T') =====" >> "$SUM"
echo "  8 GPU, TP=${TP} DP=${NPROC}, seq=${SEQ}, GBS=${GBS}, MBS=${MBS}, iters=${ITERS}, bf16, seed=${SEED}, mock_data" >> "$SUM"
echo "  token/step=$((GBS*SEQ))=6.55M" >> "$SUM"
echo "  --- pre-flight GPU check ---" >> "$SUM"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv 2>&1 >> "$SUM"
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv 2>&1 >> "$SUM"

run_arm() {
    local OPT="$1" NAME="$2"
    local LOG="$LOGDIR/muon_ab_${NAME}.log"
    local PEAK_FILE="$LOGDIR/muon_ab_${NAME}.peakmem"
    : > "$PEAK_FILE"
    echo "" >> "$SUM"
    echo "===== ARM: ${NAME} (optimizer=${OPT}) START @ $(date '+%F %T') =====" >> "$SUM"

    # 峰值显存监控
    ( MAX=0; while :; do
        USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED; echo "$MAX" > "$PEAK_FILE"; sleep 2
      done ) &
    local SP=$!

    # 随机端口避免 EADDRINUSE
    local PORT
    PORT=$("${PY}/python" -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")

    cd "$BASE" || exit 1
    "${PY}/torchrun" --nnodes=1 --nproc_per_node="$NPROC" \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "muon_ab_${NAME}" --dir "$BASE/nemo_experiments" \
        --mock \
        --tensor-parallel "$TP" \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --eval-interval 9999 --eval-iters 0 --save-interval "$SAVE_INT" \
        --lr "$LR" --min-lr "$MIN_LR" --lr-warmup-iters "$WARMUP" \
        --lr-decay-iters "$DECAY" --lr-decay-style WSD \
        --seed "$SEED" --precision bf16_mixed \
        --optimizer "$OPT" > "$LOG" 2>&1
    local RC=$?
    kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)

    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK}" >> "$SUM"

    if [ "$RC" -ne 0 ]; then
        echo "  ❌ FAILED — last 10 lines:" >> "$SUM"
        tail -10 "$LOG" >> "$SUM"
        echo "===== ARM: ${NAME} END (FAILED) @ $(date '+%F %T') =====" >> "$SUM"
        return 1
    fi

    # 提取关键指标
    echo "  --- loss curve (every 100 steps) ---" >> "$SUM"
    for S in 10 50 100 200 300 400 500 600 700 800 900 1000; do
        local LINE
        LINE=$(grep -E "iteration +${S}/" "$LOG" | tail -n1)
        local LOSS GRAD
        LOSS=$(echo "$LINE" | grep -oP 'lm loss: \K[0-9.Ee+-]+')
        GRAD=$(echo "$LINE" | grep -oP 'grad norm: \K[0-9.]+')
        echo "  iter ${S}: loss=${LOSS:-NA} grad_norm=${GRAD:-NA}" >> "$SUM"
    done

    # 稳态吞吐（最后 10 步）
    echo "  --- steady-state throughput (last 10 iters) ---" >> "$SUM"
    local MS_LIST TFLOP_LIST
    MS_LIST=$(grep -E 'iteration +' "$LOG" | tail -10 | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    TFLOP_LIST=$(grep -E 'iteration +' "$LOG" | tail -10 | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
    local MS_COUNT=$(echo "$MS_LIST" | grep -c .)
    if [ "$MS_COUNT" -gt 0 ]; then
        local AVG_MS AVG_TPS
        AVG_MS=$(echo "$MS_LIST" | awk '{s+=$1;n++} END {printf "%.1f",s/n}')
        AVG_TPS=$(awk -v t="$((GBS*SEQ))" -v m="$AVG_MS" 'BEGIN {printf "%.0f",t/(m/1000)}')
        echo "  ★ avg ms/iter: ${AVG_MS} → tok/s: ${AVG_TPS}" >> "$SUM"
    fi
    if [ -n "$TFLOP_LIST" ]; then
        echo "  avg TFLOP/s/GPU: $(echo "$TFLOP_LIST" | awk '{s+=$1;n++} END {printf "%.1f",s/n}')" >> "$SUM"
    fi

    # VRAM from training log
    local VRAM_LINE
    VRAM_LINE=$(grep 'memory (MB)' "$LOG" | tail -n1)
    echo "  VRAM: ${VRAM_LINE:-NA}" >> "$SUM"

    # NaN check
    local NAN; NAN=$(grep -c 'number of nan iterations: *[1-9]' "$LOG" || true)
    if [ "${NAN:-0}" -gt 0 ]; then
        echo "  ⚠️ NaN iterations detected!" >> "$SUM"
    fi

    echo "===== ARM: ${NAME} END (OK) @ $(date '+%F %T') =====" >> "$SUM"
    return 0
}

# 先跑 Muon 臂（刚验证通过）
run_arm muon muon
# 再跑 AdamW 臂
run_arm adam adamw

echo "" >> "$SUM"
echo "===== Muon vs AdamW A/B ALL DONE @ $(date '+%F %T') =====" >> "$SUM"
echo "  Summary file: $SUM" >> "$SUM"
echo "  Muon log:     $LOGDIR/muon_ab_muon.log" >> "$SUM"
echo "  AdamW log:    $LOGDIR/muon_ab_adamw.log" >> "$SUM"
