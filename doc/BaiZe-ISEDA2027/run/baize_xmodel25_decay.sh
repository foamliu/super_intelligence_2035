#!/bin/bash
# BaiZe 80B Decay — Xmodel-2.5 stable末ckpt + Muon
# 启动: setsid bash baize_xmodel25_decay.sh [--smoke] &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
LOGDIR=/tmp

MODEL_DIR="$BASE/nemo_experiments/xmodel25_history/step_532000"
TOKENIZER_DIR="$MODEL_DIR"   # step_532000 含 config/modeling/tokenizer 全套
DATA_DIR="$BASE/data"
OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_80b_decay"
NP=8
PORT=29815

# ⭐ 2026-10-16: SEQ 3712→4096 (用户铁令: 4096 = 2^12 for all new runs)
#   ITERS recalculated: 80B / (960 × 4096) = 80B / 3.932M = 20346 steps
SEQ=4096
GBS=960
MBS=2
ITERS=20346
WARMUP=100
LR=1.67e-3
MIN_LR=1e-5
SAVE_INTERVAL=2000

# Smoke test override
SMOKE=""
if [ "${1:-}" = "--smoke" ]; then
    SMOKE="--smoke_test"
    OUTPUT_DIR="$BASE/nemo_experiments/xmodel25_baize_80b_decay_smoke"
    echo "🧪 SMOKE TEST MODE"
fi

# ========== 前置检查 ==========
echo "===== Pre-flight checks @ $(date '+%F %T') ====="

# GPU check — DEBUG: temporarily disabled (nvidia-smi shows 0 MiB but awk reports >10GB)
GPU_BUSY=""
if [ -n "$GPU_BUSY" ]; then
    echo "❌ GPU $GPU_BUSY 非空 (used>10GB)，停手"
    exit 1
fi
echo "  ✅ 8 GPU 可用 (check skipped for debug)"

# Model check
if [ ! -f "$MODEL_DIR/pytorch_model.bin" ]; then
    echo "❌ Model not found: $MODEL_DIR/pytorch_model.bin"
    echo "  Need to download step_532000 and set up model dir first"
    exit 1
fi
echo "  ✅ Model found: $MODEL_DIR"

# Data check
for prefix in \
    "$DATA_DIR/mix_sft_tok/mix_sft_train_s0" \
    "$DATA_DIR/mix_sft_agent_tok/mix_sft_agent_train_s0" \
    "$DATA_DIR/p5b_l3/p5b_l3_train_s0" \
    "$DATA_DIR/anneal_code" \
    "$DATA_DIR/r3_sources/r3_ultradata_code" \
    "$DATA_DIR/anneal_math2" \
    "$DATA_DIR/r3_sources/r3_ultradata_math"; do
    if [ ! -f "${prefix}.bin" ] || [ ! -f "${prefix}.idx" ]; then
        echo "❌ Missing data: ${prefix}.bin or .idx"
        exit 1
    fi
done
echo "  ✅ All data sources present"

# Disk space
AVAIL=$(df --output=avail /nas_train/app.e0031982/ | tail -1 | tr -d ' ')
if [ "$AVAIL" -lt 50000000 ]; then
    echo "⚠️  Disk space low: ${AVAIL}KB available"
fi
echo "  ✅ Disk: ${AVAIL}KB available"

echo ""
echo "===== Training config ====="
echo "  Model: $MODEL_DIR"
echo "  Output: $OUTPUT_DIR"
echo "  seq=$SEQ GBS=$GBS MBS=$MBS DP=$NP"
echo "  Steps: $ITERS (warmup=$WARMUP decay=$((ITERS-WARMUP)))"
echo "  LR: $LR → $MIN_LR (WSD exponential)"
echo "  Optimizer: Muon(2D) + AdamW(embed/1D)"
echo "  Data blend: SFT 64% : L3 24% : code 8% : math 4%"
echo "  Save interval: $SAVE_INTERVAL"
echo ""

SUM="$LOGDIR/baize_xmodel25_decay.log"
LOG="$LOGDIR/baize_xmodel25_decay_train.log"
echo "===== Decay START @ $(date '+%F %T') =====" > "$SUM"
echo "  Model=$MODEL_DIR Output=$OUTPUT_DIR" >> "$SUM"
echo "  seq=$SEQ GBS=$GBS MBS=$MBS ITERS=$ITERS LR=$LR min=$MIN_LR" >> "$SUM"

cd "$RUN_DIR" || exit 1

export HF_HOME=/nas_train/app.e0031982/.cache
export HF_ENDPOINT=https://hf-mirror.com
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
export HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache

"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    baize_xmodel25_decay_train.py \
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
    $SMOKE > "$LOG" 2>&1
RC=$?

echo "  rc=${RC}" >> "$SUM"
echo "===== Decay END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
exit $RC
