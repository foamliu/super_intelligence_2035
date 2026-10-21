#!/bin/bash
# ==============================================================================
# run_armE_protb_eval.sh — ArmE (2026-10-21) open_clip ViT-L/14 Protocol-B eval
#
# Operator instruction 2026-10-19 (step ②, after ArmD training completes):
#   - Same Protocol B as ArmB/ArmC: full IN-1k 1.28M train + 50k val, SGD 90ep,
#     3 seeds (0/1/2), feature=projected, 5-NN.
#   - ONLY change vs ArmC ProtB: ckpt points to ArmD output dir.
#   - Reuses armB_protb_eval.py --model ViT-L-14 (generic entrypoint).
#   - Output: armE_20261021_protb_vitl14_224_results.json (lp mean ± sigma + 5-NN)
#   - PRIMARY comparison: ArmD-R2 lp 64.3373 / 5-NN 55.956 (single-variable baseline).
#
# Launch (ONLY after ArmD training done, .12 GPUs free):
#   setsid bash run_armD_protb_eval.sh > /tmp/armE_protb_eval.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

# Thread limits (lesson from ArmA ProtB 2026-10-17): 8 procs x default OMP
# threads thrash on 224 cores → extraction crawls at ~1.2 img/s.  Cap to 8.
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/armE_20261021_aimv2_openclip_vitl14_224
# Prefer open_clip_state_dict.pt (clean CLIP weights, no predictor);
# fall back to latest.pt if open_clip_state_dict.pt is missing.
if [ -f "$OUT_DIR/open_clip_state_dict.pt" ]; then
    CKPT="$OUT_DIR/open_clip_state_dict.pt"
else
    CKPT="$OUT_DIR/latest.pt"
fi
FEAT_DIR=/tmp/armE_protb_feats
OUT_JSON=armE_20261021_protb_vitl14_224_results.json
LOG=/tmp/armE_protb_eval.log

echo "===== ArmE ProtB Eval START $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmE-eval] ckpt=$CKPT" >> "$LOG"
echo "[ArmE-eval] feat_dir=$FEAT_DIR" >> "$LOG"
echo "[ArmE-eval] out_json=$OUT_JSON" >> "$LOG"
echo "[ArmE-eval] protocol=Protocol B (full IN-1k 1.28M train + 50k val, SGD 90ep, seeds 0/1/2, projected, 5-NN)" >> "$LOG"
echo "[ArmE-eval] compare: ArmD-R2 lp 64.3373 / 5-NN 55.956 (PRIMARY, single-var baseline); ArmB 62.093/58.102; ArmC 62.332/54.718" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

# Step 1: 8x GPU parallel feature extraction
echo -e "\n===== Step 1/2: 8x GPU feature extraction =====" >> "$LOG"
rm -rf "$FEAT_DIR"
mkdir -p "$FEAT_DIR"

pids=()
for s in 0 1 2 3 4 5 6 7; do
    CUDA_VISIBLE_DEVICES=$s "$PY" armB_protb_eval.py --model ViT-L-14 \
        --ckpt "$CKPT" \
        --device cuda:0 \
        --probe-full-train \
        --shard $s \
        --num-shards 8 \
        --feat-dir "$FEAT_DIR" \
        --extract-bs 512 >> "$LOG" 2>&1 &
    pids+=($!)
    echo "[ArmE-eval] Started shard $s (pid ${pids[-1]})" >> "$LOG"
done

# Wait for all extractions to finish
echo "[ArmE-eval] Waiting for ${#pids[@]} extraction processes..." >> "$LOG"
wait "${pids[@]}"
rc=$?
if [ $rc -ne 0 ]; then
    echo "[ArmE-eval] ERROR: Feature extraction failed (exit $rc)" >> "$LOG"
    exit $rc
fi
echo "[ArmE-eval] All extractions completed successfully" >> "$LOG"

# Step 2: Gather features and run linear probe
echo -e "\n===== Step 2/2: Gather + Linear probe (3 seeds) =====" >> "$LOG"
"$PY" armB_protb_eval.py --model ViT-L-14 \
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
echo -e "\n===== ArmE ProtB Eval DONE (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# Print final results
if [ -f "$OUT_JSON" ]; then
    echo -e "\n===== FINAL RESULTS =====" >> "$LOG"
    cat "$OUT_JSON" >> "$LOG"
    echo -e "\n===== RESULTS ====="
    cat "$OUT_JSON"
fi

exit $rc
