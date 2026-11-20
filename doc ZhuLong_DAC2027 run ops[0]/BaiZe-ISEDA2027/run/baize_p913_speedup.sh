#!/bin/bash
# BaiZe Stage(i) R2 P-9.13：Step 2 训练提速候选清单（运维 2026-10-06 提速令第 2 步）。
# P-9.12 已证 NCCL 非瓶颈 → 转向运行时/并行提速。只用 GPU0-1，TP1/DP2，不改 recipe。
# 候选：1)baseline MBS2 default  2)MAX_CONN=1  3)MAX_CONN=4  4)MBS4
# 口径：seq=4096 / GBS=256 / TP1·DP2 / bf16 / seed1234 / 60 步短测不存 ckpt。
#   GBS=256/DP2/MBS2 = 64 micro-batches/GPU（= P-9.7 的 GBS=1024/DP8/MBS2 per-GPU load → 可比）。
# 铁律：不改 P-5b recipe、不回训、不存 ckpt；只用 GPU0-1；🚫绝不 kill watchdog loop。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export CUDA_VISIBLE_DEVICES=0,1

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60; SEQ=4096; GBS=256; TP=1
SUM="/tmp/baize_p913_speedup.sum"; : > "$SUM"
echo "===== P-9.13 Step2 speedup sweep START @ $(date '+%F %T') =====" > "$SUM"
echo "  GPU0-1 only, TP=${TP} DP=2, seq=${SEQ}, GBS=${GBS}, iters=${ITERS}, bf16" >> "$SUM"
echo "  token/step=$((GBS*SEQ))=1.05M  micro-batches/GPU(MBS2)=$((GBS/2/2))=64" >> "$SUM"
echo "  --- pre-flight contention check ---" >> "$SUM"
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory,process_name --format=csv 2>&1 >> "$SUM"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv 2>&1 >> "$SUM"
pgrep -af 'torchrun|pretrain_launcher' 2>&1 | grep -v "baize_p913\|$$\|grep" | cut -c1-120 >> "$SUM"

run_config() {
    local LABEL="$1" MBS="$2" MAXCONN="$3" PORT="$4"
    local NAME; NAME="p913_${LABEL}"
    local LOG; LOG="/tmp/baize_${NAME}.log"
    local PEAK_FILE; PEAK_FILE="/tmp/baize_${NAME}.peakmem"
    : > "$PEAK_FILE"
    echo "" >> "$SUM"
    echo "===== ${LABEL}: MBS=${MBS} MAX_CONN=${MAXCONN} START @ $(date '+%F %T') port=${PORT} =====" >> "$SUM"
    ( MAX=0; while :; do
        USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0,1 2>/dev/null | sort -n | tail -1)
        [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED; echo "$MAX" > "$PEAK_FILE"; sleep 2
      done ) &
    local SP=$!
    cd "$BASE" || exit 1
    local ENV_PREFIX=""; [ "$MAXCONN" != "default" ] && ENV_PREFIX="CUDA_DEVICE_MAX_CONNECTIONS=${MAXCONN}"
    env $ENV_PREFIX "$PY/torchrun" --nnodes=1 --nproc_per_node=2 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND --tensor-parallel "$TP" \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --eval-interval 250 --eval-iters 0 --save-interval 99999 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?
    kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK}" >> "$SUM"
    if [ "$RC" -ne 0 ]; then
        echo "  ❌ OOM/ERROR 最后 5 行：" >> "$SUM"; tail -5 "$LOG" >> "$SUM"
        echo "===== ${LABEL} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"; return
    fi
    echo "  --- steady-state (last 5 iteration lines) ---" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    local MS_LIST; MS_LIST=$(grep -E 'iteration +' "$LOG" | tail -5 | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    local MS_COUNT=$(echo "$MS_LIST" | grep -c .)
    if [ "$MS_COUNT" -gt 0 ]; then
        local AVG_MS; AVG_MS=$(echo "$MS_LIST" | awk '{s+=$1;n++} END {printf "%.1f",s/n}')
        local AVG_TPS; AVG_TPS=$(awk -v t="$((GBS*SEQ))" -v m="$AVG_MS" 'BEGIN {printf "%.0f",t/(m/1000)}')
        echo "  ★ avg ms/iter: ${AVG_MS} → tok/s: ${AVG_TPS}" >> "$SUM"
    fi
    local TFLOP_LIST; TFLOP_LIST=$(grep -E 'iteration +' "$LOG" | tail -5 | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
    if [ -n "$TFLOP_LIST" ]; then
        echo "  avg TFLOP/s/GPU: $(echo "$TFLOP_LIST" | awk '{s+=$1;n++} END {printf "%.1f",s/n}')" >> "$SUM"
    fi
    echo "  first iter line:" >> "$SUM"; grep -E 'iteration +' "$LOG" | head -1 >> "$SUM"
    echo "===== ${LABEL} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
}

run_config "baseline_mbs2_default"  2 "default" 29950
run_config "mbs2_maxconn1"          2 "1"       29951
run_config "mbs2_maxconn4"          2 "4"       29952
run_config "mbs4_default"           4 "default" 29953

echo "" >> "$SUM"
echo "===== P-9.13 Step2 speedup sweep END @ $(date '+%F %T') =====" >> "$SUM"
echo "SUM=$SUM"