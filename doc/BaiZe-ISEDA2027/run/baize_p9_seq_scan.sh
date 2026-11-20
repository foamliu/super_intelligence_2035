#!/bin/bash
# BaiZe Stage(i) R2 P-9.3：seq 多点扫描（hybrid 关 O(n²) 定量）。
# 目的：hybrid 几乎关掉了「注意力随上下文爆炸」→ 扫 seq ∈ {2048,4096,8192,16384}，
#       测 r = t_step(seq)/t_step(4096)，量化「hybrid 把 O(n²) 关掉多少」（论文加分点）。
# 口径不变量（P-9.0）：每步 ≈4.19M token（GBS×seq 同步）：2048→2048 / 4096→1024 / 8192→512 / 16384→256。
#   其余固定：TP1·DP8（与 P-9.1 基线一致）/ MBS=2 / bf16 / seed1234 / 8×H100（.29）。
# 记录：t_step、tok/s、峰值显存、是否 OOM（如实记 OOM，不硬凑）。
#      5-way 归因（attention/SSM/GEMM/comm/elementwise）→ P-9.5 profiling 承担，不在此脚本内做。
# 数据：复用 p5b_l3 16 分片（每次 fresh 进程只读 60 步，无跨进程消耗问题）。
# 铁律：不改 P-5b recipe、不改训练代码。启动：setsid bash baize_p9_seq_scan.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
MBS=2
SUM="/tmp/baize_p9_seq_scan.log"
: > "$SUM"
echo "===== P-9.3 seq scan START @ $(date '+%F %T') TP1 DP8 MBS=2 iters=${ITERS} precision=bf16_mixed ===== " > "$SUM"

run_one() {
    local NAME="$1" SEQ="$2" GBS="$3" PORT="$4"
    local LOG="/tmp/baize_${NAME}.log"
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} port=${PORT} ======" >> "$SUM"

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
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --tensor-parallel 1 \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --eval-interval 250 --eval-iters 0 \
        --save-interval 99999 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
        --seed 1234 \
        --precision bf16_mixed > "$LOG" 2>&1
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
    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} ======" >> "$SUM"
}

# seq | GBS（每步≈4.19M token）
run_one p9_seq2048  2048  2048 29841
run_one p9_seq4096  4096  1024 29843   # 同-run 基线（vs P-9.1 TP1·MBS2 = 19.3s/218K）
run_one p9_seq8192  8192  512  29845
run_one p9_seq16384 16384 256  29847   # 边界点，可能 OOM（如实记）

echo "" >> "$SUM"
echo "===== P-9.3 seq scan END @ $(date '+%F %T') ===== " >> "$SUM"