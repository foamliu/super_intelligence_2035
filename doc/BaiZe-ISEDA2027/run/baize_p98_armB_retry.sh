#!/bin/bash
# BaiZe P-9.8 arm B (FP8) RE-LAUNCH — 2026-10-05 04:47
# 原因：arm B 首次启动因 harness agent 污染共享 py310 env（sympy 1.1.2.dev0
#   `from collections import Mapping` 在 Python 3.10 ImportError）而 rc=1。
#   已修复：从 vtp env 复制 sympy 1.14.0 + mpmath 到 py310 site-packages，
#   并从 easy-install.pth 移除 harness workdir 路径。
# arm A (bf16) 已完成 1000 步（22:39:58→04:39:14 rc=0，loss 6.40→2.54，nan=0/skip=0）。
# 本脚本只跑 arm B（FP8），与 arm A 同载体：TP4·SP-on·MBS8·seq8192·GBS512·M=65536。
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
TOKENS_PER_STEP=$(( GBS * SEQ ))
NAME="p98_armB_fp8_tp4sp_mbs8_RETRY"
LOG="/tmp/baize_p98_armB_fp8_retry.log"
PEAK_FILE="/tmp/baize_p98_armB_fp8_retry.peakmem"
SUM="/tmp/baize_p98_consistency.log"
: > "$PEAK_FILE"

echo "" >> "$SUM"
echo "===== ${NAME} RE-LAUNCH START @ $(date '+%F %T') precision=bf16_with_fp8_delayed_scaling_mixed MAX_CONN=1 M=65536 port=29935 =====" >> "$SUM"
echo "  (arm B 首次失败原因：harness agent sympy 1.1.2.dev0 污染 py310 env → ImportError collections.Mapping；已修复：vtp sympy 1.14.0 复制到 py310 site-packages)" >> "$SUM"

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
  --master_addr=127.0.0.1 --master_port=29935 \
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
  --precision bf16_with_fp8_delayed_scaling_mixed > "$LOG" 2>&1
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

# 每 100 步打点
echo "  --- per-100-step metrics (loss / grad-norm / skipped) ---" >> "$SUM"
for i in 100 200 300 400 500 600 700 800 900 1000; do
    LINE=$(grep -E "iteration +${i}/" "$LOG" | tail -1)
    if [ -n "$LINE" ]; then
        LOSS=$(echo "$LINE" | grep -oE 'lm loss: [0-9.eE+-]+' | head -1 | sed 's/lm loss: //')
        GN=$(echo "$LINE"   | grep -oE 'grad norm: [0-9.eE+-]+' | head -1 | sed 's/grad norm: //')
        SKIP=$(echo "$LINE" | grep -oE 'number of ski[a-z]*: [0-9]+' | head -1)
        ELAPSED=$(echo "$LINE" | grep -oE 'elapsed time per iteration \(ms\): [0-9.]+' | grep -oE '[0-9.]+$')
        printf "    iter=%4s  loss=%-12s grad_norm=%-8s %-22s elapsed_ms=%s\n" "$i" "$LOSS" "$GN" "$SKIP" "$ELAPSED" >> "$SUM"
    else
        echo "    iter=${i}  (NO LOG LINE — 未跑到此步)" >> "$SUM"
    fi
done

# NaN 检测
NANCNT=$(grep -iE 'nan|inf |overflow|loss scale: 0' "$LOG" | grep -viE 'loss scale: 1.0|contain|install|channel' | wc -l)
echo "  nan/overflow 疑似行数(粗扫) = ${NANCNT}" >> "$SUM"

# last-100 步稳态
echo "  --- last-100-step steady-state (iters $(( ITERS-100 ))-${ITERS}) ---" >> "$SUM"
grep -E 'iteration +' "$LOG" | awk -v lo=$(( ITERS-100 )) -v hi="$ITERS" '
    { for(i=1;i<=NF;i++){ if($i ~ /iteration/){ split($(i+1),a,"/"); it=a[1]+0 } }
      if(it>=lo && it<=hi){
        ms=0; for(i=1;i<=NF;i++){ if($i ~ /elapsed/){ split($(i+4),b,"("); ms=b[1]+0 } }
        if(ms>0){ n++; sum+=ms }
      } }
    END{ if(n>0) printf "    last-100 n=%d mean_s_per_iter=%.3f  tok/s=%.0f\n", n, sum/n/1000, ('"$TOKENS_PER_STEP"'*n)/(sum/1000) }' >> "$SUM"
echo "  TFLOP/s/GPU (末段):" >> "$SUM"
grep -oE 'GPU utilization: [0-9.]+TFLOP/s/GPU' "$LOG" | tail -10 >> "$SUM"

echo "" >> "$SUM"
echo "===== P-9.8 A/B FINAL END @ $(date '+%F %T') =====" >> "$SUM"
echo "  arm A (bf16): 1000 steps complete (22:39:58→04:39:14 rc=0)" >> "$SUM"
echo "  arm B (FP8):  see above (re-launch due to env contamination)" >> "$SUM"
