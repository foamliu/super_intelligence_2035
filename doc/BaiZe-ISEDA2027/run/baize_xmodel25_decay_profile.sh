#!/bin/bash
# Profile v2: baseline (grad_ckpt on, slow data) vs improved (grad_ckpt off, fast_data)
# Run on .29: setsid bash baize_xmodel25_decay_profile.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

MODEL_DIR="$BASE/nemo_experiments/xmodel25_history/step_532000"
TOKENIZER_DIR="$MODEL_DIR"
DATA_DIR="$BASE/data"
NP=8
SEQ=3712
GBS=960
MBS=2
ITERS=19980
WARMUP=100
LR=1.67e-3
MIN_LR=1e-5

export HF_HOME=/nas_train/app.e0031982/.cache
export HF_ENDPOINT=https://hf-mirror.com
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
export HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache
cd "$RUN_DIR" || exit 1

# ── Cleanup any leftover processes before starting ──
cleanup_gpus() {
    echo "  [cleanup] killing leftover baize_xmodel25_decay_v2 processes..."
    pkill -9 -f baize_xmodel25_decay_v2 2>/dev/null
    # Wait for processes to actually die and release GPU memory
    local waited=0
    while [ $waited -lt 30 ]; do
        local remaining
        remaining=$(ps -eo args= | grep baize_xmodel25_decay_v2 | grep -v grep | wc -l)
        if [ "$remaining" -eq 0 ]; then
            break
        fi
        echo "  [cleanup] still $remaining processes alive, waiting... (${waited}s)"
        sleep 2
        waited=$((waited + 2))
    done
    sleep 3  # extra safety margin for CUDA cleanup
    # Verify GPUs are free
    local max_mem
    max_mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ' | sort -nr | head -1)
    echo "  [cleanup] max GPU memory used: ${max_mem} MiB"
    if [ "${max_mem:-0}" -gt 1000 ]; then
        echo "  [cleanup] WARNING: GPUs still have ${max_mem} MiB in use! Waiting 10s..."
        sleep 10
    fi
}

run_profile() {
    local TAG="$1"; shift
    local PORT="$1"; shift
    local OUT="$BASE/nemo_experiments/xmodel25_baize_80b_decay_profile_$TAG"
    local LOG="/tmp/baize_xmodel25_decay_profile_$TAG.log"
    echo "===== Profile $TAG START @ $(date '+%F %T') (port=$PORT) ====="
    echo "  Output: $OUT"
    echo "  Args: $@"
    rm -f "$OUT/train_log.txt" "$OUT/timing_log.txt"
    mkdir -p "$OUT"
    "$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        baize_xmodel25_decay_v2.py \
        --model_path "$MODEL_DIR" \
        --tokenizer_dir "$TOKENIZER_DIR" \
        --data_dir "$DATA_DIR" \
        --output_dir "$OUT" \
        --seq_length "$SEQ" --global_batch_size "$GBS" --micro_batch_size "$MBS" \
        --total_steps "$ITERS" --warmup_steps "$WARMUP" \
        --lr "$LR" --min_lr "$MIN_LR" \
        --profile_steps 15 --log_interval 5 \
        "$@" > "$LOG" 2>&1
    local rc=$?
    echo "===== Profile $TAG END @ $(date '+%F %T') rc=$rc ====="
    echo "--- train_log ---"
    cat "$OUT/train_log.txt" 2>/dev/null
    echo "--- timing_log ---"
    cat "$OUT/timing_log.txt" 2>/dev/null
    # Cleanup between phases to prevent GPU memory overlap
    echo "  [phase-end] cleaning up GPU state..."
    pkill -9 -f baize_xmodel25_decay_v2 2>/dev/null
    sleep 5
    return $rc
}

echo """
===== PROFILING SESSION @ $(date '+%F %T') =====
"""

# Pre-flight: kill any leftover processes from previous runs
cleanup_gpus

# Phase 1: BASELINE (original behavior: grad_checkpoint ON, slow data)
# Port 29820 for baseline
run_profile baseline 29820 --grad_checkpoint

# Phase 2: IMPROVED (grad_checkpoint OFF, fast_data ON, adamw_fused ON)
# Port 29821 for improved (different port to avoid any lingering rendezvous)
cleanup_gpus
run_profile improved 29821 --fast_data --adamw_fused

echo """
===== PROFILING COMPLETE @ $(date '+%F %T') =====
"""
