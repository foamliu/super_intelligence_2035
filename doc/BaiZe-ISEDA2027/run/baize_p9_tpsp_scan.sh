#!/bin/bash
# BaiZe Stage(i) R2 P-9.2：TP/SP 其它可变参数扫描（已暴露开关 B，仅动 TP/SP 两变量）。
# 目的：P-9.1 发现 MBS=2 是最大可行（MBS=4 在 TP1·DP8 下 81GB OOM），MBS 1→2 提速 ~59%。
#       现问：TP2·DP4 把每卡 weight+optimizer 减半，能否让 MBS=4 落地（从而 M=MBS×seq=16384 进 FP8 交叉点）？
#       同时测 SP on/off 对通信/显存的影响。
# 口径（P-9.0 不变量）：seq=4096 / GBS=1024（每步 ≈4.19M token）/ bf16 / seed1234。
# 扫描（每次只动一个变量，便于归因）：
#   ① TP2·DP4 SP off MBS=2  （vs P-9.1 TP1·DP8 MBS=2=218K tok/s 基线，隔离 TP 影响）
#   ② TP2·DP4 SP off MBS=4  （测 TP2 是否腾出显存放 MBS=4）
#   ③ TP2·DP4 SP on  MBS=2  （vs ①，隔离 SP 影响）
#   ④ TP2·DP4 SP on  MBS=4  （SP 进一步减激活显存，测 MBS=4 能否落地）
# 记录：s/iter、tok/s、峰值显存、是否 OOM。铁律：不改 P-5b recipe、不改训练代码。
# 启动：setsid bash baize_p9_tpsp_scan.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
SEQ=4096
GBS=1024
SUM="/tmp/baize_p9_tpsp_scan.log"
: > "$SUM"
echo "===== P-9.2 TP/SP scan START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} iters=${ITERS} precision=bf16_mixed ===== " > "$SUM"

# 配置列表：name|TP|SP(0/1)|MBS|port
run_one() {
    local NAME="$1" TP="$2" SP="$3" MBS="$4" PORT="$5"
    local LOG="/tmp/baize_${NAME}.log"
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') TP=${TP} SP=${SP} MBS=${MBS} port=${PORT} =====" >> "$SUM"

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
        --tensor-parallel "$TP" $SPARG \
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
        echo "  ❌ OOM/ERROR 最后 5 行：" >> "$SUM"
        tail -5 "$LOG" >> "$SUM"
        return
    fi
    echo "  s/iter (last 5) + tok/s:" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
}

run_one p9_tp2_mbs2      2 0 2 29821
run_one p9_tp2_mbs4      2 0 4 29823
run_one p9_tp2sp_mbs2    2 1 2 29825
run_one p9_tp2sp_mbs4    2 1 4 29827

echo "" >> "$SUM"
echo "===== P-9.2 TP/SP scan END @ $(date '+%F %T') =====" >> "$SUM"