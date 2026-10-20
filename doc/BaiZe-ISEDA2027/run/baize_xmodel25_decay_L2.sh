#!/bin/bash
# BaiZe L2 Experiment — 20B decay: FIX double-shift ONLY (keep v2's high LR 1.67e-3)
# 2×2 factorial: L1 (fix+lowLR) | L2 (fix+highLR) | L3 (bug+lowLR) | v2 (bug+highLR, done)
# L2 isolates: does double-shift fix alone prevent degradation, even with high LR?
# Usage: setsid bash baize_xmodel25_decay_L2.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

MODEL_DIR="$BASE/nemo_experiments/xmodel25_history/step_532000"
TOKENIZER_DIR="$MODEL_DIR"
DATA_DIR="$BASE/data"
OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_L2_20b"
NP=8
PORT=29822

SEQ=3712
GBS=960
MBS=4
ITERS=5611
WARMUP=100
LR=1.67e-3   # Same as v2 (high LR) — isolates double-shift fix
MIN_LR=1e-4  # Same as v2
SAVE_INTERVAL=500

SMOKE=""
if [ "${1:-}" = "--smoke" ]; then
    SMOKE="--smoke_test"
    OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_L2_smoke"
    echo "SMOKE TEST MODE"
fi

echo "===== L2 Pre-flight @ $(date '+%F %T') ====="
echo "  Experiment: L2 (fix double-shift ONLY, keep v2 high LR 1.67e-3, 20B tokens)"
echo "  Model: $MODEL_DIR"
echo "  Output: $OUTPUT_DIR"
echo "  seq=$SEQ GBS=$GBS MBS=$MBS DP=$NP"
echo "  Steps: $ITERS (warmup=$WARMUP decay=$((ITERS-WARMUP)))"
echo "  LR: $LR -> $MIN_LR (WSD exponential) — SAME as v2 (high LR)"
echo "  Token budget: $((ITERS * GBS * SEQ / 1000000000))B tokens"
echo "  Fix: double-shift removed (uses L1 Python script with fix)"
echo "  Data blend: SFT 64% : L3 24% : code 10% : math 4% (same as v2)"

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
    $SMOKE > /tmp/baize_xmodel25_decay_L2_train.log 2>&1
RC=$?

echo "  rc=${RC}"
echo "===== L2 Decay END @ $(date '+%F %T') rc=${RC} ====="
exit $RC
