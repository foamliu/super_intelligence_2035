#!/bin/bash
# ==============================================================================
# v3_eval_watcher.sh — V3 full-data training watcher + auto-eval
#
# Waits for the V3 training process (r9_train.py with scaling_V3_fulldata
# output-dir) to finish, then runs the full evaluation suite:
#   1. Protocol B (3 seeds, SGD+cosine, 90ep, full IN-1k train)
#   2. Protocol A (AdamW full-batch, 100ep)
#   3. Zero-shot (same-model IN-1k zs)
#   4. k-NN probe (k=5,10,20)
#
# Launch: setsid bash v3_eval_watcher.sh > /tmp/v3_eval_watcher.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_V3_fulldata_ov2_w512_d30_p16_224
TRAIN_LOG="$OUT_DIR/train.log"
LOG=/tmp/v3_eval_watcher.log

echo "[$(date '+%F %T')] v3_eval_watcher STARTED — waiting for V3 training to finish..." | tee -a "$LOG"

# ---- Phase 1: Wait for V3 training process to exit ----
while true; do
    V3_RUNNING=$(ps -eo args= | grep 'r9_train.py' | grep 'scaling_V3_fulldata' | grep -v grep | head -1)
    if [ -z "$V3_RUNNING" ]; then
        echo "[$(date '+%F %T')] V3 training process gone." | tee -a "$LOG"
        break
    fi
    # Log current progress
    LAST_STEP=$(grep -oP '\[step \K[0-9]+' "$TRAIN_LOG" 2>/dev/null | tail -1)
    echo "[$(date '+%F %T')] V3 still training: step ${LAST_STEP:-?}/230598" | tee -a "$LOG"
    sleep 300  # Check every 5 minutes
done

# ---- Phase 2: Verify V3 completed successfully ----
echo "[$(date '+%F %T')] Checking V3 completion..." | tee -a "$LOG"

# Check if final checkpoint exists (vision.pt is saved at the end of training)
FINAL_CKPT="$OUT_DIR/vision.pt"
if [ ! -f "$FINAL_CKPT" ]; then
    echo "[$(date '+%F %T')] vision.pt not found, checking for last step checkpoint..." | tee -a "$LOG"
    FINAL_CKPT=$(ls "$OUT_DIR"/vision_step*.pt 2>/dev/null | sort -V | tail -1)
    if [ -z "$FINAL_CKPT" ]; then
        echo "[$(date '+%F %T')] 🚫 NO checkpoint found! V3 training may have failed." | tee -a "$LOG"
        echo "[$(date '+%F %T')] Last 30 lines of train.log:" | tee -a "$LOG"
        tail -30 "$TRAIN_LOG" 2>/dev/null | tee -a "$LOG"
        exit 1
    fi
fi
echo "[$(date '+%F %T')] ✅ Final checkpoint: $FINAL_CKPT" | tee -a "$LOG"
echo "[$(date '+%F %T')] Last 10 lines of train.log:" | tee -a "$LOG"
tail -10 "$TRAIN_LOG" 2>/dev/null | tee -a "$LOG"

# ---- Phase 3: Verify GPU is free ----
echo "[$(date '+%F %T')] GPU status before eval:" | tee -a "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv | tee -a "$LOG"

# ---- Phase 4: Run evaluation suite ----
EVAL_LOG=/tmp/scaling_v3_eval.log
echo "[$(date '+%F %T')] ===== V3 EVAL START =====" | tee -a "$LOG" | tee "$EVAL_LOG"

# 4a. Protocol B (3 seeds, SGD+cosine, 90ep, full IN-1k train)
echo "[$(date '+%F %T')] --- Protocol B (3 seeds) ---" | tee -a "$EVAL_LOG"
"$PY" lp_protocol_bridge.py --ckpts "$FINAL_CKPT" --protocol B --probe-full-train >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Protocol B done (rc=$?)" | tee -a "$EVAL_LOG"

# 4b. Protocol A (AdamW full-batch, 100ep, seed 0)
echo "[$(date '+%F %T')] --- Protocol A ---" | tee -a "$EVAL_LOG"
"$PY" lp_protocol_bridge.py --ckpts "$FINAL_CKPT" --protocol A >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Protocol A done (rc=$?)" | tee -a "$EVAL_LOG"

# 4c. Zero-shot (same-model IN-1k zs)
echo "[$(date '+%F %T')] --- Zero-shot ---" | tee -a "$EVAL_LOG"
"$PY" zeroshot_in1k_eval.py --ckpt "$FINAL_CKPT" >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Zero-shot done (rc=$?)" | tee -a "$EVAL_LOG"

# 4d. k-NN probe + longer probe comparison
echo "[$(date '+%F %T')] --- k-NN + probe comparison ---" | tee -a "$EVAL_LOG"
"$PY" probe_comparison_eval.py --ckpt "$FINAL_CKPT" >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] k-NN/probe comparison done (rc=$?)" | tee -a "$EVAL_LOG"

echo "[$(date '+%F %T')] ===== V3 EVAL DONE =====" | tee -a "$EVAL_LOG"

# ---- Phase 5: Summary ----
echo "" | tee -a "$LOG"
echo "[$(date '+%F %T')] ===== V3 WATCHER + EVAL COMPLETE =====" | tee -a "$LOG"
echo "Eval log: $EVAL_LOG" | tee -a "$LOG"
echo "--- Key results ---" | tee -a "$LOG"
grep -E 'ProtB|ProtA|ZS|k-NN|lp_top1|zs_top1|knn' "$EVAL_LOG" 2>/dev/null | tail -30 | tee -a "$LOG"
echo "[$(date '+%F %T')] Next agent wake should collect V3 eval results → update EXPERIMENTS_VISION.md §9.5 + report." | tee -a "$LOG"
