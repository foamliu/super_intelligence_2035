#!/bin/bash
# Profile MBS=3 + no_sync (v2.py now has no_sync by default)
# Combines MBS=3 (4% improvement) + no_sync (5% improvement)
# Run on .29: setsid bash baize_xmodel25_decay_profile_mbs3_nosync.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

MODEL_DIR="$BASE/nemo_experiments/xmodel25_history/step_532000"
TOKENIZER_DIR="$MODEL_DIR"
DATA_DIR="$BASE/data"
NP=8
PORT=29826
SEQ=3712
GBS=960
MBS=3
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

# ── Cleanup any leftover processes ──
echo "  [cleanup] killing leftover processes..."
pkill -9 -f baize_xmodel25_decay_v2 2>/dev/null
sleep 5
max_mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ' | sort -nr | head -1)
echo "  [cleanup] max GPU memory: ${max_mem} MiB"

TAG="mbs3_nosync"
OUT="$BASE/nemo_experiments/xmodel25_baize_80b_decay_profile_$TAG"
LOG="/tmp/baize_xmodel25_decay_profile_$TAG.log"

echo """
===== MBS=3 + no_sync PROFILE @ $(date '+%F %T') =====
  MBS=$MBS, GC=ON, no_sync=True (v2.py default), port=$PORT
  Combines MBS=3 (4% win) + no_sync (5% win) = ~9% expected
"""
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
    --grad_checkpoint > "$LOG" 2>&1

rc=$?
echo "===== MBS=3 + no_sync PROFILE END @ $(date '+%F %T') rc=$rc ====="
echo "--- train_log ---"
cat "$OUT/train_log.txt" 2>/dev/null
echo "--- timing_log ---"
cat "$OUT/timing_log.txt" 2>/dev/null
