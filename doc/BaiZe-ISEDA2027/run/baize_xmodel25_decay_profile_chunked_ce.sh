#!/bin/bash
# Profile chunked CE: MBS=4 and MBS=8 (GC OFF, fast_data, adamw_fused)
# Chunked CE avoids materializing full [B,S,V] logits → enables larger MBS
# Run on .29: setsid bash baize_xmodel25_decay_profile_chunked_ce.sh &
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

cleanup_gpus() {
    echo "  [cleanup] killing leftover processes..."
    # Use a pattern that won't match this pkill command itself
    for pid in $(ps -eo pid,args | grep 'decay_v2.py' | grep 'model_path' | grep -v grep | awk '{print $1}'); do
        kill -9 "$pid" 2>/dev/null || true
    done
    sleep 10
    local max_mem
    max_mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ' | sort -nr | head -1)
    echo "  [cleanup] max GPU memory: ${max_mem} MiB"
    if [ "${max_mem:-0}" -gt 1000 ]; then
        echo "  [cleanup] WARNING: GPUs still have ${max_mem} MiB! Waiting 15s..."
        sleep 15
    fi
}

run_profile() {
    local TAG="$1"; shift
    local PORT="$1"; shift
    local MBS="$1"; shift
    local CHUNK="$1"; shift
    local GA=$(( GBS / (MBS * NP) ))
    local OUT="$BASE/nemo_experiments/xmodel25_baize_80b_decay_profile_$TAG"
    local LOG="/tmp/baize_xmodel25_decay_profile_$TAG.log"
    echo "===== Profile $TAG START @ $(date '+%F %T') (port=$PORT, MBS=$MBS, GA=$GA, chunk=$CHUNK) ====="
    echo "  Output: $OUT"
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
        --profile_steps 35 --log_interval 5 \
        --fast_data --adamw_fused \
        --chunked_ce --ce_chunk_size "$CHUNK" \
        "$@" > "$LOG" 2>&1
    local rc=$?
    echo "===== Profile $TAG END @ $(date '+%F %T') rc=$rc ====="
    echo "--- train_log ---"
    tail -10 "$OUT/train_log.txt" 2>/dev/null
    echo "--- timing_log ---"
    tail -5 "$OUT/timing_log.txt" 2>/dev/null
    echo "--- GPU mem during run (from log) ---"
    grep -i 'memory\|oom\|cuda' "$LOG" 2>/dev/null | tail -5
    cleanup_gpus
    return $rc
}

echo "===== CHUNKED CE PROFILING SESSION @ $(date '+%F %T') ====="

cleanup_gpus

# A3: MBS=4, chunked CE (chunk=256), GC OFF, compile base model
run_profile chunked_mbs4 29830 4 256 --compile_model --compile_mode default
echo ""

# A4: MBS=8, chunked CE (chunk=256), GC OFF, compile base model
run_profile chunked_mbs8 29831 8 256 --compile_model --compile_mode default
echo ""

# A4b: MBS=8, chunked CE (chunk=128, smaller chunk if MBS=8 chunk=256 OOMs)
# run_profile chunked_mbs8_c128 29832 8 128

echo "===== CHUNKED CE PROFILING COMPLETE @ $(date '+%F %T') ====="
