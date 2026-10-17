#!/bin/bash
# BaiZe 80B Decay v2 — seq=3712 + torch.compile(mode=default) + no_sync + GC OFF
# Winning config from profiling: 299.7K tok/s (+62.8% vs baseline 184K)
# Launch on .29: setsid bash baize_xmodel25_decay_v2.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
LOGDIR=/tmp

MODEL_DIR="$BASE/nemo_experiments/xmodel25_history/step_532000"
TOKENIZER_DIR="$MODEL_DIR"
DATA_DIR="$BASE/data"
OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_80b_decay"
NP=8
PORT=29815

# v2: seq=3712 (Xmodel native), ITERS=19980 (71.2B / (960*3712) = 19980)
SEQ=3712
GBS=960
MBS=4
ITERS=19980
WARMUP=100
LR=1.67e-3
MIN_LR=1e-5
SAVE_INTERVAL=500        # crash2 fix: was 2000 (first ckpt too far → crash@410 lost everything); 500 = lose ≤500 steps on crash

SMOKE=""
if [ "${1:-}" = "--smoke" ]; then
    SMOKE="--smoke_test"
    OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_80b_decay_smoke_v2"
    echo "SMOKE TEST MODE"
fi

echo "===== Pre-flight @ $(date '+%F %T') ====="
echo "  Model: $MODEL_DIR"
echo "  Output: $OUTPUT_DIR"
echo "  seq=$SEQ GBS=$GBS MBS=$MBS DP=$NP"
echo "  Steps: $ITERS (warmup=$WARMUP decay=$((ITERS-WARMUP)))"
echo "  LR: $LR -> $MIN_LR (WSD exponential)"
echo "  v2 improvements: fast_data=YES, grad_checkpoint=NO, adamw_fused=YES"
echo "  torch.compile: mode=default (kernel fusion, +62.8% throughput)"
echo "  DDP no_sync: YES (defer all-reduce to last micro-step)"
echo "  Data blend: SFT 64% : L3 24% : code 8% : math 4%"
echo "  Save interval: $SAVE_INTERVAL"
echo "  Projected: ~300K tok/s, ~11.9s/step, ~66h total"

cd "$RUN_DIR" || exit 1

export HF_HOME=/nas_train/app.e0031982/.cache
export HF_ENDPOINT=https://hf-mirror.com
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
export HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache

"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    baize_xmodel25_decay_v2.py \
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
    $SMOKE > "$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log" 2>&1
# crash2 fix: log to OUTPUT_DIR (persistent NFS) not /tmp (gets cleaned → traceback lost)
RC=$?

echo "  rc=${RC}" 
echo "===== Decay v2 END @ $(date '+%F %T') rc=${RC} ====="
exit $RC
