#!/bin/bash
# BaiZe L1 Experiment — 20B decay: FIX double-shift + LR 5e-4 + warmup 100
# Based on baize_xmodel25_decay_v2.sh but with:
#   1. Fixed double-shift bug (baize_xmodel25_decay_L1.py)
#   2. LR reduced from 1.67e-3 to 5e-4
#   3. ITERS reduced from 19980 to 5611 (20B tokens instead of 71.2B)
# Usage: setsid bash baize_xmodel25_decay_L1.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

MODEL_DIR="$BASE/nemo_experiments/xmodel25_history/step_532000"
TOKENIZER_DIR="$MODEL_DIR"
DATA_DIR="$BASE/data"
OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_L1_20b"
NP=8
PORT=29820

# L1: 20B token decay = 20B / (960*3712) = 5611 steps
SEQ=3712
GBS=960
MBS=4
ITERS=5611
WARMUP=100
LR=5e-4
MIN_LR=1e-5
SAVE_INTERVAL=500

SMOKE=""
if [ "${1:-}" = "--smoke" ]; then
    SMOKE="--smoke_test"
    OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_L1_smoke"
    echo "SMOKE TEST MODE"
fi

RESUME_DIR="${RESUME_DIR:-}"
RESUME_ARG=""
[ -n "$RESUME_DIR" ] && RESUME_ARG="--resume $RESUME_DIR"

echo "===== L1 Pre-flight @ $(date '+%F %T') ====="
echo "  Experiment: L1 (fix double-shift + LR 5e-4 + 20B tokens)"
echo "  Model: $MODEL_DIR"
echo "  Output: $OUTPUT_DIR"
echo "  seq=$SEQ GBS=$GBS MBS=$MBS DP=$NP"
echo "  Steps: $ITERS (warmup=$WARMUP decay=$((ITERS-WARMUP)))"
echo "  LR: $LR -> $MIN_LR (WSD exponential)"
echo "  Token budget: $((ITERS * GBS * SEQ / 1000000000))B tokens"
echo "  Fix: double-shift removed (chunked CE: no extra shift; non-chunked: pass input_ids as labels)"
echo "  Data blend: SFT 64% : L3 24% : code 10% : math 4% (same as v2)"
echo "  Save interval: $SAVE_INTERVAL"

cd "$RUN_DIR" || exit 1

export HF_HOME=/nas_train/app.e0031982/.cache
export HF_ENDPOINT=https://hf-mirror.com
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
export HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache
export TORCH_NCCL_DUMP_ON_TIMEOUT=1
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
export NCCL_ASYNC_ERROR_HANDLING=1

"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    baize_xmodel25_decay_L1.py \
    --model_path "$MODEL_DIR" \
    --tokenizer_dir "$TOKENIZER_DIR" \
    --data_dir "$DATA_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --seq_length "$SEQ" \
    --global_batch_size "$GBS" \
    --micro_batch_size "$MBS" \
    --total_steps "$ITERS" \
    --warmup_steps "$WARMUP" \
    --lr "$LR" \
    --min_lr "$MIN_LR" \
    --save_interval "$SAVE_INTERVAL" \
    --fast_data \
    --adamw_fused \
    --compile_model \
    --compile_mode default \
    --chunked_ce \
    --ce_chunk_size 256 \
    --verify_save_step 20 \
    $RESUME_ARG \
    $SMOKE > /tmp/baize_xmodel25_decay_L1_train.log 2>&1
RC=$?

echo "  rc=${RC}"
echo "===== L1 Decay END @ $(date '+%F %T') rc=${RC} ====="
exit $RC
