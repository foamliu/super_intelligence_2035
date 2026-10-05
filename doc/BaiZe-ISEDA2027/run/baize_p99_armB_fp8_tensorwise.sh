#!/bin/bash
# BaiZe P-9.9 step 3-alt — FP8 tensorwise (current scaling) recipe — 2026-10-05
# blockwise (subchannel) 需要 CUDA >= 12.9，我们 CUDA 12.8 不满足 → AssertionError。
# 改用 bf16_with_fp8_current_scaling_mixed (fp8_recipe="tensorwise")：
#   - 与 delayed 的区别：用当前 step 的 amax（非上一步的 delayed amax）
#   - 仍是 per-tensor（非 fine-grained），但消除了 delayed amax lag
#   - spike 根因假设：delayed scaling 在 loss landscape 变化时 amax 追不上 → current scaling 可能避免
# 同载体 TP4·SP-on·MBS8·seq8192·GBS512·M=65536，seed 1234，1000 步。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
OUT="$BASE/data/p5b_l3"

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=1000
SEQ=8192
GBS=512
TP=4
MBS=8
NAME="p99_armB_fp8_tensorwise_tp4sp_mbs8"
LOG="/tmp/baize_p99_armB_fp8_tensorwise.log"
PEAK_FILE="/tmp/baize_p99_armB_fp8_tensorwise.peakmem"
SUM="/tmp/baize_p99_consistency.log"
: > "$PEAK_FILE"

echo "" >> "$SUM"
echo "===== ${NAME} START @ $(date '+%F %T') precision=bf16_with_fp8_current_scaling_mixed (tensorwise, current per-tensor) MAX_CONN=1 M=65536 port=29939 =====" >> "$SUM"
echo "  (P-9.9 step 3-alt: blockwise requires CUDA>=12.9 (we have 12.8) -> try tensorwise current scaling instead)" >> "$SUM"

# 峰值显存采样器
(
  MAX=0
  while :; do
    USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
    [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED
    echo "$MAX" > "$PEAK_FILE"
    sleep 3
  done
) &
SAMPLER_PID=$!

cd "$BASE" || exit 1
CUDA_DEVICE_MAX_CONNECTIONS=1 "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
  --master_addr=127.0.0.1 --master_port=29939 \
  pretrain_launcher.py \
  --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
  --tokenizer-path "$BASE/data/tokenizer_eod" \
  --train-data-path $BLEND \
  --tensor-parallel "$TP" --sequence-parallel \
  --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
  --eval-interval 250 --eval-iters 0 \
  --save-interval 0 \
  --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
  --seed 1234 \
  --precision bf16_with_fp8_current_scaling_mixed > "$LOG" 2>&1
RC=$?

kill "$SAMPLER_PID" 2>/dev/null
wait "$SAMPLER_PID" 2>/dev/null
PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
echo "" >> "$SUM"
echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} peak_gpu_mem_MiB=${PEAK} =====" >> "$SUM"

if [ "$RC" -ne 0 ]; then
    echo "  ⚠️ rc!=0. Last 10 lines:" >> "$SUM"
    tail -10 "$LOG" >> "$SUM"
fi
