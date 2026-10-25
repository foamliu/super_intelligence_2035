#!/bin/bash
# ==============================================================================
# run_armE_r2_protb_eval_ckpt60000.sh — A3: ProtB on ArmE-R2 checkpoint_60000
#
# WHY (2026-10-25, wake #266): The "next-steps" report
#   (reports/report_vision_next_steps_protb_mllm_zh.html) recommended as a
#   side-experiment "A3 (ckpt_60000 跑 ProtB, ~0.3 GPU·h)" to test the
#   "末段抖动 / best-segment" hypothesis: MEMORY noted ArmE-R2's ProtB used
#   s63400 (end-of-training, jittery regime), so final lp may be BELOW the
#   best segment. If ckpt_60000 lp > final(63400) lp 68.236±0.0182, that
#   confirms picking the best-segment ckpt could directly gain ~1-2pp.
#
# This is eval-only (~0.3 GPU·h): no new training, no API key, no shared-infra
# change. Identical Protocol B to run_armE_r2_protb_eval.sh; ONLY difference =
# ckpt = checkpoint_60000.pt (full training ckpt) instead of open_clip_state_dict.pt.
# load_armB_visual (armB_protb_eval.py:85-93) handles full ckpts: strips 'clip.'
# prefix, drops predictor keys, strict=False with a visual.* missing-key WARNING
# as the safety net (would surface in log if load failed -> random encoder).
#
# Output: armE_r2_20261022_protb_vitl14_224_ckpt60000_results.json
# PRIMARY comparison: ArmE-R2 final(63400) lp 68.236±0.0182 / 5-NN 58.904
#   (from armE_r2_20261022_protb_vitl14_224_results.json, open_clip_state_dict.pt).
#
# Launch: setsid bash run_armE_r2_protb_eval_ckpt60000.sh \
#           > /tmp/armE_protb_eval_ckpt60000_outer.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

# Thread caps (lesson from ArmA ProtB 2026-10-17): 8 procs x default OMP threads
# thrash on 224 cores -> extraction crawls.  Cap to 8.
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/armE_r2_20261022_aimv2_openclip_vitl14_224
CKPT="$OUT_DIR/checkpoint_60000.pt"
FEAT_DIR=/tmp/armE_protb_feats_ckpt60000
OUT_JSON=armE_r2_20261022_protb_vitl14_224_ckpt60000_results.json
LOG=/tmp/armE_protb_eval_ckpt60000.log

echo "===== ArmE-R2 A3 ProtB Eval (ckpt_60000) START $(date '+%F %T') =====" | tee "$LOG"
echo "[A3] ckpt=$CKPT" >> "$LOG"
echo "[A3] feat_dir=$FEAT_DIR" >> "$LOG"
echo "[A3] out_json=$OUT_JSON" >> "$LOG"
echo "[A3] protocol=Protocol B (full IN-1k 1.28M train + 50k val, SGD 90ep, seeds 0/1/2, projected, 5-NN)" >> "$LOG"
echo "[A3] compare: ArmE-R2 final(63400) lp 68.236±0.0182 / 5-NN 58.904 (PRIMARY)" >> "$LOG"
if [ ! -f "$CKPT" ]; then
    echo "[A3] ERROR: ckpt not found: $CKPT" >> "$LOG"
    exit 2
fi
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
    echo "[A3] Started shard $s (pid ${pids[-1]})" >> "$LOG"
done

echo "[A3] Waiting for ${#pids[@]} extraction processes..." >> "$LOG"
wait "${pids[@]}"
rc=$?
if [ $rc -ne 0 ]; then
    echo "[A3] ERROR: Feature extraction failed (exit $rc)" >> "$LOG"
    exit $rc
fi
echo "[A3] All extractions completed successfully" >> "$LOG"

# Step 2: Gather features and run linear probe (3 seeds)
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
echo -e "\n===== ArmE-R2 A3 ProtB Eval (ckpt_60000) DONE (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# Print final results
if [ -f "$OUT_JSON" ]; then
    echo -e "\n===== FINAL RESULTS =====" >> "$LOG"
    cat "$OUT_JSON" >> "$LOG"
    echo -e "\n===== RESULTS ====="
    cat "$OUT_JSON"
fi

exit $rc
