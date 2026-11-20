#!/bin/bash
# ==============================================================================
# post_merge3ds_chain.sh — Auto-eval chain for merge3ds ArmC (LR ×4 linear)
#
# Waits for merge3ds ArmC training to finish, then auto-runs the full eval suite:
#   1. Protocol B (3 seeds, full train) — linear probe, mainstream protocol
#   2. Protocol A — BaiZe internal protocol (for cross-protocol comparison)
#   3. Zero-shot IN-1k — direct text-similarity classification
#   4. k-NN probe — non-parametric baseline
#
# After eval, prints summary for next agent wake to collect.
#
# Launch (after launching run_merge3ds_armC_resume.sh):
#   setsid bash post_merge3ds_chain.sh > /tmp/post_merge3ds_chain.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/post_merge3ds_chain.log
TRAIN_LOG=/tmp/merge3ds_armC_resume.log
EVAL_LOG=/tmp/merge3ds_armC_eval.log

OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
MERGE_OUT="$OUTROOT/merge3ds_bs4_lrC_w512_d30_p16_224"

echo "[$(date '+%F %T')] post_merge3ds_chain STARTED — waiting for merge3ds ArmC training to finish..." | tee -a "$LOG"

# ---- Phase 1: Wait for merge3ds ArmC training to complete ----
while true; do
    if grep -q 'merge3ds ArmC RESUME done' "$TRAIN_LOG" 2>/dev/null; then
        echo "[$(date '+%F %T')] ✅ merge3ds ArmC training completed." | tee -a "$LOG"
        break
    fi
    # Check if training process died
    TRAINING_ALIVE=$(ps -eo args= | grep 'r9_train.py' | grep 'merge3ds_bs4_lrC' | grep -v grep | head -1)
    if [ -z "$TRAINING_ALIVE" ]; then
        if grep -q 'merge3ds ArmC RESUME done' "$TRAIN_LOG" 2>/dev/null; then
            echo "[$(date '+%F %T')] ✅ merge3ds ArmC training done (process exited normally)." | tee -a "$LOG"
            break
        fi
        echo "[$(date '+%F %T')] ⚠️ merge3ds ArmC training process gone — checking log..." | tee -a "$LOG"
        tail -20 "$TRAIN_LOG" 2>/dev/null | tee -a "$LOG"
        if grep -q 'merge3ds ArmC RESUME done' "$TRAIN_LOG" 2>/dev/null; then
            break
        fi
        echo "[$(date '+%F %T')] 🚫 merge3ds ArmC training FAILED — aborting eval chain." | tee -a "$LOG"
        exit 1
    fi
    echo "[$(date '+%F %T')] merge3ds ArmC training still in progress..." | tee -a "$LOG"
    sleep 300
done

# ---- Phase 2: Verify GPU is free ----
echo "[$(date '+%F %T')] GPU status before merge3ds eval:" | tee -a "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv | tee -a "$LOG"

# ---- Phase 3: Locate merge3ds checkpoint ----
MERGE_CKPT="$MERGE_OUT/vision.pt"
if [ ! -f "$MERGE_CKPT" ]; then
    MERGE_CKPT=$(ls "$MERGE_OUT"/vision_step*.pt 2>/dev/null | sort -V | tail -1)
fi
if [ ! -f "$MERGE_CKPT" ]; then
    MERGE_CKPT="$MERGE_OUT/vision_fused.pt"
fi
echo "[$(date '+%F %T')] merge3ds checkpoint: $MERGE_CKPT" | tee -a "$LOG" | tee "$EVAL_LOG"

if [ ! -f "$MERGE_CKPT" ]; then
    echo "[$(date '+%F %T')] 🚫 No merge3ds checkpoint found in $MERGE_OUT — aborting." | tee -a "$LOG"
    exit 1
fi

# ---- Phase 4: Full eval suite ----
echo "[$(date '+%F %T')] ===== merge3ds ArmC EVAL START =====" | tee -a "$EVAL_LOG"

# 4a. Protocol B (3 seeds) — the primary metric
echo "[$(date '+%F %T')] --- Protocol B (3 seeds, full train) ---" | tee -a "$EVAL_LOG"
"$PY" lp_protocol_bridge.py --ckpts "$MERGE_CKPT" --protocol B --probe-full-train >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Protocol B done (rc=$?)" | tee -a "$EVAL_LOG"

# 4b. Protocol A
echo "[$(date '+%F %T')] --- Protocol A ---" | tee -a "$EVAL_LOG"
"$PY" lp_protocol_bridge.py --ckpts "$MERGE_CKPT" --protocol A >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Protocol A done (rc=$?)" | tee -a "$EVAL_LOG"

# 4c. Zero-shot
echo "[$(date '+%F %T')] --- Zero-shot ---" | tee -a "$EVAL_LOG"
"$PY" zeroshot_in1k_eval.py --ckpt "$MERGE_CKPT" >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Zero-shot done (rc=$?)" | tee -a "$EVAL_LOG"

# 4d. k-NN probe
echo "[$(date '+%F %T')] --- k-NN ---" | tee -a "$EVAL_LOG"
"$PY" probe_comparison_eval.py --ckpt "$MERGE_CKPT" --knn-only >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] k-NN done (rc=$?)" | tee -a "$EVAL_LOG"

echo "[$(date '+%F %T')] ===== merge3ds ArmC EVAL DONE =====" | tee -a "$EVAL_LOG"
echo "[$(date '+%F %T')] ===== POST_MERGE3DS_CHAIN COMPLETE =====" | tee -a "$LOG"
echo "Results: merge3ds eval=$EVAL_LOG" | tee -a "$LOG"
echo "[$(date '+%F %T')] Next agent wake: collect results → update EXPERIMENTS_VISION.md + report_vision_merge3ds_result_zh.html." | tee -a "$LOG"
