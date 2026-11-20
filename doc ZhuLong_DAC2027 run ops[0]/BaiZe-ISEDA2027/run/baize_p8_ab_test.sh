#!/bin/bash
# BaiZe P-8 MBS 2→3 A/B test — 300 steps each arm
# 运维指令 2026-10-10: MBS 2→3 A/B 验证 · 候选 GBS=1032
#
# Arm A: MBS=2, GBS=1024 (baseline, same as P-8 current config)
# Arm B: MBS=3, GBS=1032 (candidate, 43×24)
#
# 预注册判据（三全过才切 MBS=3）:
#   ① 吞吐 B ≥ A×1.12 (A≈249K → B≥279K, last-100 步均值)
#   ② 峰值显存 B ≤ 76GB (OOM 直接判负, nvidia-smi 全程记 max)
#   ③ loss@300 与 A 一致 (无 NaN/发散/抬升)
#
# 前提: P-8 已在 step 1049 保存 ckpt 并暂停（GPU 全空）
# 启动: setsid bash baize_p8_ab_test.sh > /tmp/baize_p8_ab.log 2>&1 < /dev/null &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

SEQ=4094
TP=1
NP=8
LR="1e-3"
MIN_LR="1e-5"
WARMUP_AB=10
DECAY_AB=290
ITERS_AB=300
DATA="$BASE/data"

# ========== Stable data blend: web 88:code 8:math 4 ==========
BLEND=""
for s in $(seq 0 43); do
    BLEND="$BLEND 2 ${DATA}/mix_base/mix_base_train_s${s}"
done
BLEND="$BLEND 3 ${DATA}/anneal_code 5 ${DATA}/r3_sources/r3_ultradata_code"
BLEND="$BLEND 3 ${DATA}/anneal_math2 1 ${DATA}/r3_sources/r3_ultradata_math"
BLEND="${BLEND# }"

# ========== VRAM monitor (background) ==========
VRAM_PID=""
start_vram_monitor() {
    local logfile=$1
    : > "$logfile"
    while true; do
        nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits 2>/dev/null | \
            awk -F',' '{gsub(/ /,"",$1); gsub(/ /,"",$2); m=$2+0; total+=m; if(m>max) max=m} END {print strftime("%H:%M:%S"), "max_per_gpu="max"MiB total="total"MiB"}' >> "$logfile"
        sleep 5
    done
}

stop_vram_monitor() {
    [ -n "$VRAM_PID" ] && kill "$VRAM_PID" 2>/dev/null
    VRAM_PID=""
}

# ========== Run one arm ==========
run_arm() {
    local arm=$1 mbs=$2 gbs=$3 port=$4
    local name="p8_ab_${arm}"
    local train_log="$LOGDIR/baize_${name}_train.log"
    local vram_log="$LOGDIR/baize_${name}_vram.log"
    local summary="$LOGDIR/baize_${name}_summary.log"
    echo "===== Arm ${arm} START @ $(date '+%F %T') MBS=${mbs} GBS=${gbs} =====" | tee "$summary"

    GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
    if [ -n "$GPU_BUSY" ]; then
        echo "GPU $GPU_BUSY busy - previous arm may not have exited" | tee -a "$summary"
        return 1
    fi
    start_vram_monitor "$vram_log" &
    VRAM_PID=$!
    cd "$BASE" || return 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
        --master_addr=127.0.0.1 --master_port="$port" \
        pretrain_launcher.py \
        --arch mamba2 --name "$name" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --tensor-parallel "$TP" \
        --train-iters "$ITERS_AB" --global-batch-size "$gbs" --micro-batch-size "$mbs" --seq-length "$SEQ" \
        --eval-interval 9999 --eval-iters 0 --save-interval 0 \
        --lr "$LR" --min-lr "$MIN_LR" \
        --lr-warmup-iters "$WARMUP_AB" --lr-decay-iters "$DECAY_AB" --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed --optimizer dist_muon > "$train_log" 2>&1
    local rc=$?
    stop_vram_monitor
    echo "  rc=${rc}" >> "$summary"
    echo "===== Arm ${arm} END @ $(date '+%F %T') rc=${rc} =====" | tee -a "$summary"
    if [ $rc -eq 0 ]; then
        echo "  --- last-10 steps ---" | tee -a "$summary"
        grep 'iteration' "$train_log" | tail -10 | tee -a "$summary"
        awk '{for(i=1;i<=NF;i++){if($i~/max_per_gpu=/){gsub(/max_per_gpu=/,"",$i);gsub(/MiB/,"",$i);v=$i+0;if(v>max)max=v}}} END{print "  peak_VRAM="max"MiB ("max/1024"GB)"}' "$vram_log" | tee -a "$summary"
    fi
    return $rc
}

# ========== Pre-flight: GPU must be free (P-8 paused) ==========
echo "===== P-8 MBS A/B test @ $(date '+%F %T') =====" | tee "$LOGDIR/baize_p8_ab.log"
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
if [ -n "$GPU_BUSY" ]; then
    echo "GPU $GPU_BUSY busy - P-8 may not be paused, exit" | tee -a "$LOGDIR/baize_p8_ab.log"
    exit 1
fi
echo "GPU all free, starting A/B test" | tee -a "$LOGDIR/baize_p8_ab.log"

# Arm A (baseline: MBS=2, GBS=1024)
run_arm "A" 2 1024 29811
ARM_A_RC=$?
echo "Arm A rc=${ARM_A_RC}" | tee -a "$LOGDIR/baize_p8_ab.log"
echo "Sleeping 60s for GPU cleanup..." | tee -a "$LOGDIR/baize_p8_ab.log"
sleep 60

# Arm B (candidate: MBS=3, GBS=1032)
run_arm "B" 3 1032 29812
ARM_B_RC=$?
echo "Arm B rc=${ARM_B_RC}" | tee -a "$LOGDIR/baize_p8_ab.log"

echo "===== A/B COMPLETE @ $(date '+%F %T') =====" | tee -a "$LOGDIR/baize_p8_ab.log"
echo "Arm A(MBS=2/GBS=1024) rc=${ARM_A_RC}" | tee -a "$LOGDIR/baize_p8_ab.log"
echo "Arm B(MBS=3/GBS=1032) rc=${ARM_B_RC}" | tee -a "$LOGDIR/baize_p8_ab.log"
echo "Criteria: 1)tok/s B>=A*1.12  2)peakVRAM B<=76GB  3)loss@300 consistent" | tee -a "$LOGDIR/baize_p8_ab.log"
echo "If pass: P-8 switch MBS=3/GBS=1032, 10409 steps/warmup520/decay1041/save1041" | tee -a "$LOGDIR/baize_p8_ab.log"
echo "If fail: restore MBS=2/GBS=1024 original (10490/524/1049/1049)" | tee -a "$LOGDIR/baize_p8_ab.log"

