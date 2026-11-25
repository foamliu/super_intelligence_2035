#!/bin/bash
# ==============================================================================
# post_v3_chain.sh — Post-V3 automated experiment chain
#
# Waits for V3 eval watcher to finish, then:
#   1. Runs ② ×5 epochs probe + wd/LR sweep on E1fair checkpoint (~1 GPU·h)
#   2. Launches ④-2ep training (374,202 steps, ~10h)
#   3. Waits for ④-2ep training to finish
#   4. Auto-evals ④-2ep (ProtB 3-seed + ProtA + zero-shot + k-NN, ~3.5h)
#
# This ensures continuous GPU utilization without waiting for next agent wake.
#
# Launch (do NOT launch until V3 is running):
#   setsid bash post_v3_chain.sh > /tmp/post_v3_chain.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/post_v3_chain.log
V3_EVAL_LOG=/tmp/v3_eval_watcher.log
V3_EVAL_RESULTS=/tmp/scaling_v3_eval.log

E1FAIR_CKPT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E1fair_ov2_w512_d30_p16_224/vision.pt
E4_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_2ep_ov2_w512_d30_p16_224
EVAL=/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar

echo "[$(date '+%F %T')] post_v3_chain STARTED — waiting for V3 eval watcher to finish..." | tee -a "$LOG"

# ---- Phase 1: Wait for V3 eval watcher to complete ----
while true; do
    if grep -q 'V3 WATCHER + EVAL COMPLETE' "$V3_EVAL_LOG" 2>/dev/null; then
        echo "[$(date '+%F %T')] ✅ V3 eval watcher completed." | tee -a "$LOG"
        break
    fi
    # Also check if watcher process died without completing
    WATCHER_ALIVE=$(ps -eo args= | grep 'v3_eval_watcher.sh' | grep -v grep | head -1)
    V3_TRAINING=$(ps -eo args= | grep 'r9_train.py' | grep 'scaling_V3_fulldata' | grep -v grep | head -1)
    if [ -z "$WATCHER_ALIVE" ] && [ -z "$V3_TRAINING" ]; then
        # Watcher gone and no V3 training — check if eval completed
        if grep -q 'V3 EVAL DONE' "$V3_EVAL_RESULTS" 2>/dev/null; then
            echo "[$(date '+%F %T')] ✅ V3 eval done (watcher exited, eval log has DONE)." | tee -a "$LOG"
            break
        fi
        echo "[$(date '+%F %T')] ⚠️ V3 watcher gone but no EVAL DONE found — checking eval log..." | tee -a "$LOG"
        tail -20 "$V3_EVAL_RESULTS" 2>/dev/null | tee -a "$LOG"
        # Proceed anyway — V3 training is done, GPU should be free
        break
    fi
    echo "[$(date '+%F %T')] V3 still in progress (training or eval)..." | tee -a "$LOG"
    sleep 300
done

# ---- Phase 2: Verify GPU is free ----
echo "[$(date '+%F %T')] GPU status before ② probe:" | tee -a "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv | tee -a "$LOG"

# ---- Phase 3: Run ② ×5 epochs probe + wd/LR sweep on E1fair ----
echo "[$(date '+%F %T')] ===== ② ×5 PROBE START =====" | tee -a "$LOG"
bash run_probe_x5.sh >> "$LOG" 2>&1
PROBE_RC=$?
echo "[$(date '+%F %T')] ② ×5 probe done (rc=$PROBE_RC)" | tee -a "$LOG"
echo "[$(date '+%F %T')] Probe results in /tmp/probe_x5.log" | tee -a "$LOG"

# ---- Phase 4: Launch ④-2ep training ----
echo "[$(date '+%F %T')] ===== ④-2ep TRAINING START =====" | tee -a "$LOG"
bash run_e4_2ep.sh >> "$LOG" 2>&1
E4_RC=$?
echo "[$(date '+%F %T')] ④-2ep training done (rc=$E4_RC)" | tee -a "$LOG"

if [ $E4_RC -ne 0 ]; then
    echo "[$(date '+%F %T')] 🚫 ④-2ep training FAILED (rc=$E4_RC). Aborting eval." | tee -a "$LOG"
    tail -30 /tmp/e4_2ep_train.log 2>/dev/null | tee -a "$LOG"
    exit 1
fi

# ---- Phase 5: ④-2ep eval (same suite as E1fair) ----
E4_CKPT="$E4_OUT/vision.pt"
if [ ! -f "$E4_CKPT" ]; then
    E4_CKPT=$(ls "$E4_OUT"/vision_step*.pt 2>/dev/null | sort -V | tail -1)
fi
echo "[$(date '+%F %T')] ④-2ep checkpoint: $E4_CKPT" | tee -a "$LOG"

EVAL_LOG=/tmp/e4_2ep_eval.log
echo "[$(date '+%F %T')] ===== ④-2ep EVAL START =====" | tee -a "$LOG" | tee "$EVAL_LOG"

# 5a. Protocol B (3 seeds)
echo "[$(date '+%F %T')] --- Protocol B (3 seeds) ---" | tee -a "$EVAL_LOG"
"$PY" lp_protocol_bridge.py --ckpts "$E4_CKPT" --protocol B --probe-full-train >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Protocol B done (rc=$?)" | tee -a "$EVAL_LOG"

# 5b. Protocol A
echo "[$(date '+%F %T')] --- Protocol A ---" | tee -a "$EVAL_LOG"
"$PY" lp_protocol_bridge.py --ckpts "$E4_CKPT" --protocol A >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Protocol A done (rc=$?)" | tee -a "$EVAL_LOG"

# 5c. Zero-shot
echo "[$(date '+%F %T')] --- Zero-shot ---" | tee -a "$EVAL_LOG"
"$PY" zeroshot_in1k_eval.py --ckpt "$E4_CKPT" >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] Zero-shot done (rc=$?)" | tee -a "$EVAL_LOG"

# 5d. k-NN probe
echo "[$(date '+%F %T')] --- k-NN ---" | tee -a "$EVAL_LOG"
"$PY" probe_comparison_eval.py --ckpt "$E4_CKPT" --knn-only >> "$EVAL_LOG" 2>&1
echo "[$(date '+%F %T')] k-NN done (rc=$?)" | tee -a "$EVAL_LOG"

echo "[$(date '+%F %T')] ===== ④-2ep EVAL DONE =====" | tee -a "$EVAL_LOG"
echo "[$(date '+%F %T')] ===== POST_V3_CHAIN COMPLETE =====" | tee -a "$LOG"
echo "Results: V3 eval=$V3_EVAL_RESULTS, probe=/tmp/probe_x5.log, ④-2ep eval=$EVAL_LOG" | tee -a "$LOG"
echo "[$(date '+%F %T')] Next agent wake: collect all results → update EXPERIMENTS_VISION.md §9.5 + report." | tee -a "$LOG"
