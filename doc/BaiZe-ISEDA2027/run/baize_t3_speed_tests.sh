#!/bin/bash
# BaiZe T3 提速验证：TP1 上 recompute + FP8 能否解锁 MBS4 / 长上下文 / >249K tok/s。
# 用户直令（2026-10-09）：「T3 报告写了 2 天了还没跑，.29 全空，跑起来」
# 测试顺序（每点 60 步，--save-interval 0，不存 ckpt）：
#   Test 1 (C2):  TP1·MBS4·seq4096·recompute28·bf16
#   Test 2 (C2+): TP1·MBS4·seq8192·recompute28·bf16 (M=32768)
#   Test 3 (C2+FP8): TP1·MBS4·seq8192·recompute28·FP8 (梦幻配置)
#   Test 4 (C1):  TP1·MBS2·seq4096·FP8 (快速确认, 预期 s<1.0)
# 铁律：不改 P-5b recipe 超参，只加 recompute。不存 ckpt。
# 启动：setsid bash baize_t3_speed_tests.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
SUM="/tmp/baize_t3_all.log"
: > "$SUM"
echo "===== T3 Speed Tests START @ $(date '+%F %T') =====" >> "$SUM"
echo "Baseline: P-9.7 TP1·MBS2·seq4094 = 16841.9 ms/iter / 249K tok/s / 54.7GB" >> "$SUM"

run_one() {
    local NAME="$1" SEQ="$2" GBS="$3" MBS="$4" PREC="$5" RC_LAYERS="$6" CMDC="$7" PORT="$8"
    local LOG="/tmp/baize_t3_${NAME}.log"
    local M=$(( MBS * SEQ ))
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} MBS=${MBS} M=${M} precision=${PREC} recompute=${RC_LAYERS} CMDC=${CMDC} ===== " >> "$SUM"

    local PEAK_FILE="/tmp/baize_t3_${NAME}.peakmem"
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
    local -a TC=("$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
      --master_addr=127.0.0.1 --master_port="$PORT" \
      pretrain_launcher.py \
      --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
      --tokenizer-path "$BASE/data/tokenizer_eod" \
      --train-data-path $BLEND \
      --tensor-parallel 1 \
      --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
      --eval-interval 250 --eval-iters 0 \
      --save-interval 0 \
      --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
      --seed 1234 \
      --precision "$PREC")
    if [ -n "$RC_LAYERS" ] && [ "$RC_LAYERS" -gt 0 ] 2>/dev/null; then
        TC+=(--recompute-num-layers "$RC_LAYERS")
    fi
    if [ "$CMDC" = "1" ]; then
        CUDA_DEVICE_MAX_CONNECTIONS=1 "${TC[@]}" > "$LOG" 2>&1
    else
        "${TC[@]}" > "$LOG" 2>&1
    fi
    local RC=$?

    kill "$SAMPLER_PID" 2>/dev/null
    wait "$SAMPLER_PID" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

    local OOM=0
    if [ "$RC" -ne 0 ]; then
        if grep -qiE 'out of memory|CUDA error|OOM' "$LOG" 2>/dev/null; then
            OOM=1
            echo "  OOM detected" >> "$SUM"
        else
            echo "  rc!=0 (non-OOM). Last 6 lines:" >> "$SUM"
            tail -6 "$LOG" >> "$SUM"
        fi
    fi

    echo "  s/iter (last 5) + tok/s:" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} OOM=${OOM} ===== " >> "$SUM"

    eval "${NAME}_OOM=${OOM}"
    eval "${NAME}_RC=${RC}"
    eval "${NAME}_PEAK=${PEAK}"
}

# ─── Test 1 (C2): TP1·MBS4·seq4096·recompute28·bf16 ───
run_one test1_c2_rc_mbs4 4096 1024 4 bf16_mixed 28 0 29931

# ─── Test 4 (C1): TP1·MBS2·seq4096·FP8 — 快速确认 ───
run_one test4_c1_fp8_mbs2 4096 1024 2 bf16_with_fp8_delayed_scaling_mixed "" 1 29933

# ─── Test 2 (C2+): TP1·MBS4·seq8192·recompute28·bf16 — M=32768 ───
TEST1_OOM_VAL=$(eval echo "\${test1_c2_rc_mbs4_OOM:-1}")
TEST1_RC_VAL=$(eval echo "\${test1_c2_rc_mbs4_RC:-1}")
if [ "$TEST1_OOM_VAL" = "0" ] && [ "$TEST1_RC_VAL" = "0" ]; then
    echo "" >> "$SUM"
    echo ">>> Test 1 OK → proceeding to Test 2" >> "$SUM"
    run_one test2_c2plus_seq8192 8192 512 4 bf16_mixed 28 0 29935

    TEST2_OOM_VAL=$(eval echo "\${test2_c2plus_seq8192_OOM:-1}")
    TEST2_RC_VAL=$(eval echo "\${test2_c2plus_seq8192_RC:-1}")
    if [ "$TEST2_OOM_VAL" = "0" ] && [ "$TEST2_RC_VAL" = "0" ]; then
        echo "" >> "$SUM"
        echo ">>> Test 2 OK → proceeding to Test 3 (FP8)" >> "$SUM"
        run_one test3_c2plus_fp8 8192 512 4 bf16_with_fp8_delayed_scaling_mixed 28 1 29937
    else
        echo ">>> Test 2 failed → skip Test 3" >> "$SUM"
    fi
else
    echo ">>> Test 1 failed → skip Test 2 & 3" >> "$SUM"
fi

echo "" >> "$SUM"
echo "===== T3 Speed Tests END @ $(date '+%F %T') =====" >> "$SUM"
echo "" >> "$SUM"
echo "===== SUMMARY =====" >> "$SUM"
echo "Test 1: rc=${test1_c2_rc_mbs4_RC:-?} OOM=${test1_c2_rc_mbs4_OOM:-?} peak=${test1_c2_rc_mbs4_PEAK:-?}MiB" >> "$SUM"
echo "Test 4: rc=${test4_c1_fp8_mbs2_RC:-?} OOM=${test4_c1_fp8_mbs2_OOM:-?} peak=${test4_c1_fp8_mbs2_PEAK:-?}MiB" >> "$SUM"
echo "Test 2: rc=${test2_c2plus_seq8192_RC:-?} OOM=${test2_c2plus_seq8192_OOM:-?} peak=${test2_c2plus_seq8192_PEAK:-?}MiB" >> "$SUM"
echo "Test 3: rc=${test3_c2plus_fp8_RC:-?} OOM=${test3_c2plus_fp8_OOM:-?} peak=${test3_c2plus_fp8_PEAK:-?}MiB" >> "$SUM"
