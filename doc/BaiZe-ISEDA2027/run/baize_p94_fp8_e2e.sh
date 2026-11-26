#!/bin/bash
# BaiZe Stage(i) R2 P-9.4：FP8 端到端复评（bf16 vs FP8，同 MBS、同步数）。
# 载体 = TP2·DP4·MBS4（M=MBS×seq=4×4096=16384，P-9.2 定位的 FP8 交叉载体；bf16 基线见 P-9.2）。
#   A. TP2·SP-off·MBS4 · FP8  （vs ② bf16 = 21.2s / ~198K tok/s）
#   B. TP2·SP-on ·MBS4 · FP8  （vs ④ bf16 = 20.0s / ~210K tok/s）
# 精度：--precision bf16_with_fp8_delayed_scaling_mixed（= TE delayed-scaling FP8，Xmodel-2.5 同款）。
# 口径不变量：seq=4096 / GBS=1024（4.19M tok/步）/ seed1234 / 60 步短测 / 不存 ckpt。
# 记录：s/iter、tok/s、峰值显存、loss/NaN。铁律：不改 P-5b recipe、不改训练代码。
# 启动：setsid bash baize_p94_fp8_e2e.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
SEQ=4096
GBS=1024
PREC=bf16_with_fp8_delayed_scaling_mixed
SUM="/tmp/baize_p94_fp8_e2e.log"
: > "$SUM"
echo "===== P-9.4 FP8 end-to-end START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} iters=${ITERS} precision=${PREC} ===== " > "$SUM"

run_one() {
    local NAME="$1" SP="$2" PORT="$3"
    local LOG="/tmp/baize_${NAME}.log"
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') TP=2 SP=${SP} MBS=4 precision=${PREC} port=${PORT} =====" >> "$SUM"

    local PEAK_FILE="/tmp/baize_${NAME}.peakmem"
    : > "$PEAK_FILE"
    (
      MAX=0
      while :; do
        USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED
        echo "$MAX" > "$PEAK_FILE"
        sleep 2
      done
    ) &
    local SAMPLER_PID=$!

    cd "$BASE" || exit 1
    local SPARG=""
    [ "$SP" = "1" ] && SPARG="--sequence-parallel"
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --tensor-parallel 2 $SPARG \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size 4 --seq-length "$SEQ" \
        --eval-interval 250 --eval-iters 0 \
        --save-interval 99999 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
        --seed 1234 \
        --precision "$PREC" > "$LOG" 2>&1
    local RC=$?

    kill "$SAMPLER_PID" 2>/dev/null
    wait "$SAMPLER_PID" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

    if [ "$RC" -ne 0 ]; then
        echo "  ❌ OOM/ERROR 最后 6 行：" >> "$SUM"
        tail -6 "$LOG" >> "$SUM"
        return
    fi
    echo "  s/iter (last 5) + tok/s:" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
}

# A. TP2·SP-off·MBS4 FP8（vs ② bf16 21.2s）
run_one p94_fp8_tp2_mbs4      0 29831
# B. TP2·SP-on·MBS4 FP8（vs ④ bf16 20.0s）
run_one p94_fp8_tp2sp_mbs4    1 29833

echo "" >> "$SUM"
echo "===== P-9.4 FP8 end-to-end END @ $(date '+%F %T') ===== " >> "$SUM"