#!/bin/bash
# BaiZe Stage(i) R2 P-9.6②：FP8 端到端复评 @ 唯一可达的 M≥32768 配置。
# 背景：P-9.6① bf16 最优搜索已收官 —— seq4096/TP2/SP/MBS4(M=16384)=210K、TP1·MBS2(M=8192)=249K 才是速度最优；
#       而抬 M 到 ≥32768 要么 TP2 OOM、要么 TP4 才能训（点8 TP4·SP·MBS8·seq8192, M=65536, 22.16s/iter=~189K）。
#       唯一能在 M≥32768 训练的配置 = TP4·SP·MBS8·seq8192（M=65536），此处微基准 s=1.31（FP8 饱和区）。
# 判据（预注册）：FP8 端到端 s = t_bf16 / t_fp8 > 1.05 才转正；≤1.05 → 不转正 → 定稿 bf16。
# ⚠️ 必带 CUDA_DEVICE_MAX_CONNECTIONS=1 A/B 对照（运维要求）：P-9.4 发现 SP-on 下 FP8 反慢 ~15%，
#    疑 FP8 amax/delayed-scaling allreduce 与 SP allreduce 叠加 → 测 A(=1) vs B(默认) 隔离该因子。
# bf16 基线 = 点8（22.16s/iter，默认连接，同机同口径）。
# 铁律：不改 P-5b recipe、不改训练代码。启动：setsid bash baize_p96b_fp8_e2e.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
SEQ=8192
GBS=512
TP=4
SP=1
MBS=8
PREC=bf16_with_fp8_delayed_scaling_mixed
SUM="/tmp/baize_p96b_fp8_e2e.log"
: > "$SUM"
echo "===== P-9.6② FP8 e2e @ M=65536 START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} TP=${TP} SP=${SP} MBS=${MBS} iters=${ITERS} precision=${PREC} ===== " > "$SUM"
echo "bf16 基线 = 点8 22.16s/iter（默认连接，~189K tok/s，522 TFLOP/s/GPU，峰值 reserved ~71GB）" >> "$SUM"

run_one() {
    local NAME="$1" CMDC="$2" PORT="$3"
    local LOG="/tmp/baize_${NAME}.log"
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') TP=${TP} SP=${SP} MBS=${MBS} M=$(( MBS * SEQ )) CUDA_DEVICE_MAX_CONNECTIONS=${CMDC} port=${PORT} ===== " >> "$SUM"

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
    if [ "$CMDC" = "1" ]; then
      CUDA_DEVICE_MAX_CONNECTIONS=1 "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --tensor-parallel "$TP" --sequence-parallel \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --eval-interval 250 --eval-iters 0 \
        --save-interval 99999 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
        --seed 1234 \
        --precision "$PREC" > "$LOG" 2>&1
    else
      "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --tensor-parallel "$TP" --sequence-parallel \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --eval-interval 250 --eval-iters 0 \
        --save-interval 99999 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
        --seed 1234 \
        --precision "$PREC" > "$LOG" 2>&1
    fi
    local RC=$?

    kill "$SAMPLER_PID" 2>/dev/null
    wait "$SAMPLER_PID" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

    if [ "$RC" -ne 0 ]; then
        echo "  ⚠️ rc!=0（可能尾部存 ckpt OOM，但 s/iter 已在 iteration 行测到）。最后 6 行：" >> "$SUM"
        tail -6 "$LOG" >> "$SUM"
    fi
    echo "  s/iter (last 5) + tok/s:" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} ===== " >> "$SUM"
}

# B. FP8 默认连接（vs bf16 点8 22.16s）—— 复现/确认 P-9.4 的 SP 叠加是否仍在 M=65536 发生
run_one p96b_fp8_tp4sp_mbs8_B  0 29921
# A. FP8 + CUDA_DEVICE_MAX_CONNECTIONS=1 —— 运维要求 A/B，隔离 amax+SP allreduce 叠加
run_one p96b_fp8_tp4sp_mbs8_A  1 29923

echo "" >> "$SUM"
echo "===== P-9.6② FP8 e2e @ M=65536 END @ $(date '+%F %T') ===== " >> "$SUM"