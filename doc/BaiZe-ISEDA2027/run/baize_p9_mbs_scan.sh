#!/bin/bash
# BaiZe Stage(i) R2 P-9.1：MBS 吞吐/显存扫描（问题①）。
# 目的：当前 --micro-batch-size 1（GBS=1024/DP8 → 每步 128 段 grad-accum），显存余量过半，
#       运维问「MBS 1→2(或更高)能否提速」。同时 M = MBS × seq，抬 MBS 才能把 FP8 的 M 抬进收益区。
# 口径（P-9.0 不变量）：seq=4096 / GBS=1024（每步 ≈4.19M token）/ TP1·DP8 / bf16 / seed1234。
# 扫描：MBS ∈ {1,2,4,8} × 短测 60 步（不存 ckpt）。数组每个值独立 torchrun 启动（fresh 进程从数据头读）。
# 记录：s/iter、tok/s、峰值显存（后台采样）、是否 OOM。
# 数据：复用 p5b_l3 16 分片（20.5B token，每次 fresh 进程只读 60 步 ≈251M token，无跨进程消耗问题）。
# 铁律：不改 P-5b recipe；只给结论供 P-8 参考。
#
# 启动：setsid bash baize_p9_mbs_scan.sh &（PPID=1 真后台）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
SEQ=4096
GBS=1024
SUM="/tmp/baize_p9_mbs_scan.log"
: > "$SUM"
echo "===== P-9.1 MBS scan START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} iters=${ITERS} precision=bf16_mixed ===== " > "$SUM"

for MBS in 1 2 4 8; do
    PORT=$(( 29811 + MBS ))
    NAME="p9_mbs${MBS}"
    LOG="/tmp/baize_${NAME}.log"
    echo "" >> "$SUM"
    echo "===== MBS=${MBS} START @ $(date '+%F %T') name=${NAME} port=${PORT} =====" >> "$SUM"

    # 后台采样峰值显存（每 2s 记一次 max，直到 torchrun 退出）
    PEAK_FILE="/tmp/baize_${NAME}.peakmem"
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
    SAMPLER_PID=$!

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
    RC=$?

    kill "$SAMPLER_PID" 2>/dev/null
    wait "$SAMPLER_PID" 2>/dev/null
    PEAK=$(cat "$PEAK_FILE" 2>/dev/null)

    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

    if [ "$RC" -ne 0 ]; then
        echo "  ❌ OOM/ERROR 最后 5 行：" >> "$SUM"
        tail -5 "$LOG" >> "$SUM"
        continue
    fi

    # 摘稳态 s/iter（取最后 5 条 iteration 行，剔除首步编译/预热）
    echo "  s/iter (last 5) + tok/s:" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    # 首条 iteration 行（看首步是否含编译开销）
    echo "  first iter line (compile overhead check):" >> "$SUM"
    grep -E 'iteration +' "$LOG" | head -1 >> "$SUM"

    echo "===== MBS=${MBS} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
done

echo "" >> "$SUM"
echo "===== P-9.1 MBS scan END @ $(date '+%F %T') =====" >> "$SUM"