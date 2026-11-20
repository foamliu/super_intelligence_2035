#!/bin/bash
# ==============================================================================
# run_armA_protb_eval.sh — ArmA open_clip ViT-B/16 Protocol-B linear probe eval
#
# Operator instruction 2026-10-16:
#   "ArmA 训练完成 → 起 ProtB 评测（8卡 sharded）"
#   - Mainstream Protocol B: full IN-1k train + official val, 3 seeds, SGD 90ep
#   - 8x H100 parallel feature extraction → ~30min total
#
# Output:
#   - /tmp/armA_protb_feats/ : cached features (train + val)
#   - armA_protb_results.json : final lp results (mean ± sigma)
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

# Thread limits (2026-10-17 fix): this box has 224 cores; 8 extraction procs x
# default OMP threads (==nproc) = ~1500 threads thrashing on 224 cores, which
# made tiny per-image tensor ops (Normalize/stack) spend all CPU on thread
# scheduling -> extraction crawled at ~1.2 img/s.  Cap each proc to 8 threads.
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
CKPT=/nas_train/app.e0031982/datasets/baize-vision/out/armA_openclip_vitb16_224/latest.pt
FEAT_DIR=/tmp/armA_protb_feats
OUT_JSON=armA_protb_vitb16_224_results.json
LOG=/tmp/armA_protb_eval.log

echo "===== ArmA ProtB Eval START $(date '+%F %T') =====" | tee "$LOG"
echo "[eval] ckpt=$CKPT" >> "$LOG"
echo "[eval] feat_dir=$FEAT_DIR" >> "$LOG"
echo "[eval] out_json=$OUT_JSON" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

# Step 1: 8x GPU parallel feature extraction
echo -e "\n===== Step 1/2: 8x GPU feature extraction =====" >> "$LOG"
rm -rf "$FEAT_DIR"
mkdir -p "$FEAT_DIR"

pids=()
for s in 0 1 2 3 4 5 6 7; do
    CUDA_VISIBLE_DEVICES=$s "$PY" armA_protb_eval.py \
        --ckpt "$CKPT" \
        --device cuda:0 \
        --probe-full-train \
        --shard $s \
        --num-shards 8 \
        --feat-dir "$FEAT_DIR" \
        --extract-bs 512 >> "$LOG" 2>&1 &
    pids+=($!)
    echo "[eval] Started shard $s (pid ${pids[-1]})" >> "$LOG"
done

# Wait for all extractions to finish
echo "[eval] Waiting for ${#pids[@]} extraction processes..." >> "$LOG"
wait "${pids[@]}"
rc=$?
if [ $rc -ne 0 ]; then
    echo "[eval] ERROR: Feature extraction failed (exit $rc)" >> "$LOG"
    exit $rc
fi
echo "[eval] All extractions completed successfully" >> "$LOG"

# Step 2: Gather features and run linear probe
echo -e "\n===== Step 2/2: Gather + Linear probe (3 seeds) =====" >> "$LOG"
"$PY" armA_protb_eval.py \
    --ckpt "$CKPT" \
    --device cuda:0 \
    --probe-full-train \
    --gather \
    --num-shards 8 \
    --feat-dir "$FEAT_DIR" \
    --out-json "$OUT_JSON" \
    --epochs 90 \
    --probe-batch 1024 \
    --lr 0.1 \
    --warmup-epochs 5 \
    --seeds 0 1 2 \
    --knn >> "$LOG" 2>&1

rc=$?
echo -e "\n===== ArmA ProtB Eval DONE (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# Print final results
if [ -f "$OUT_JSON" ]; then
    echo -e "\n===== FINAL RESULTS =====" >> "$LOG"
    cat "$OUT_JSON" >> "$LOG"
    echo -e "\n===== RESULTS ====="
    cat "$OUT_JSON"
fi

exit $rc