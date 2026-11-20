#!/bin/bash
# ==============================================================================
# watch_4ep_results.sh — Monitor ④-4ep training+eval completion, collect results
#
# Writes a summary file when everything is done:
#   /tmp/4ep_results_summary.txt
#
# Launch:
#   setsid bash watch_4ep_results.sh > /tmp/watch_4ep_results.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail

EVAL_LOG=/tmp/e4_4ep_eval.log
TRAIN_LOG=/tmp/e4_4ep_train.log
SUMMARY=/tmp/4ep_results_summary.txt
E4_4EP_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224

echo "[$(date '+%F %T')] watch_4ep_results STARTED — waiting for eval completion..."

# Wait for eval to complete
while true; do
    if grep -q '④-4ep EVAL DONE' "$EVAL_LOG" 2>/dev/null; then
        echo "[$(date '+%F %T')] ✅ ④-4ep EVAL COMPLETE — collecting results..."
        break
    fi
    
    # Check if training is still running
    TRAINING_ALIVE=$(ps -eo args= | grep 'r9_train.py' | grep 'scaling_E4_4ep' | grep -v grep | head -1)
    EVAL_RUNNING=$(ps -eo args= | grep -E 'lp_protocol_bridge|zeroshot_in1k|probe_comparison' | grep -v grep | head -1)
    POST_CHAIN=$(ps -eo args= | grep 'post_4ep_chain' | grep -v grep | head -1)
    
    if [ -z "$TRAINING_ALIVE" ] && [ -z "$EVAL_RUNNING" ] && [ -z "$POST_CHAIN" ]; then
        # Everything stopped — check if eval log has results
        if [ -f "$EVAL_LOG" ] && grep -q 'EVAL DONE' "$EVAL_LOG" 2>/dev/null; then
            echo "[$(date '+%F %T')] ✅ Eval done (all processes exited)."
            break
        fi
        # Maybe training crashed
        if ! grep -q '④-4ep done' "$TRAIN_LOG" 2>/dev/null; then
            echo "[$(date '+%F %T')] ⚠️ Training may have crashed — checking..."
            tail -5 "$TRAIN_LOG" 2>/dev/null
        fi
    fi
    
    # Print progress
    LAST_STEP=$(tail -1 "$TRAIN_LOG" 2>/dev/null | grep -oP 'step \K[0-9]+' | head -1)
    echo "[$(date '+%F %T')] Training at step ${LAST_STEP:-?}/748404, eval not yet done..."
    sleep 120
done

# ---- Collect results ----
echo "========================================" > "$SUMMARY"
echo "④-4ep RESULTS SUMMARY ($(date '+%F %T'))" >> "$SUMMARY"
echo "========================================" >> "$SUMMARY"
echo "" >> "$SUMMARY"

# Training final stats
echo "=== TRAINING STATS ===" >> "$SUMMARY"
tail -5 "$TRAIN_LOG" 2>/dev/null >> "$SUMMARY"
echo "" >> "$SUMMARY"

# Final checkpoint
echo "=== FINAL CHECKPOINT ===" >> "$SUMMARY"
ls -la "$E4_4EP_OUT/vision.pt" 2>/dev/null >> "$SUMMARY" || echo "vision.pt not found" >> "$SUMMARY"
echo "" >> "$SUMMARY"

# All checkpoints
echo "=== ALL CHECKPOINTS ===" >> "$SUMMARY"
ls -1 "$E4_4EP_OUT"/vision_step*.pt 2>/dev/null | wc -l >> "$SUMMARY"
echo "Latest: $(ls -t "$E4_4EP_OUT"/vision_step*.pt 2>/dev/null | head -1)" >> "$SUMMARY"
echo "" >> "$SUMMARY"

# Eval results — extract key numbers
echo "=== EVAL RESULTS (from $EVAL_LOG) ===" >> "$SUMMARY"
cat "$EVAL_LOG" 2>/dev/null >> "$SUMMARY"
echo "" >> "$SUMMARY"

# Extract specific metrics
echo "=== KEY METRICS EXTRACTION ===" >> "$SUMMARY"
echo "" >> "$SUMMARY"
echo "--- Protocol B results ---" >> "$SUMMARY"
grep -i 'protocol.*B\|lp.*=\|linear.*probe\|acc.*=' "$EVAL_LOG" 2>/dev/null | tail -20 >> "$SUMMARY"
echo "" >> "$SUMMARY"
echo "--- Protocol A results ---" >> "$SUMMARY"
grep -i 'protocol.*A\|lp.*=' "$EVAL_LOG" 2>/dev/null | head -10 >> "$SUMMARY"
echo "" >> "$SUMMARY"
echo "--- Zero-shot results ---" >> "$SUMMARY"
grep -i 'zero.*shot\|top1\|top5\|top-1\|top-5' "$EVAL_LOG" 2>/dev/null >> "$SUMMARY"
echo "" >> "$SUMMARY"
echo "--- k-NN results ---" >> "$SUMMARY"
grep -i 'k.*nn\|knn\|k=.*acc' "$EVAL_LOG" 2>/dev/null >> "$SUMMARY"
echo "" >> "$SUMMARY"

echo "========================================" >> "$SUMMARY"
echo "SUMMARY COMPLETE — read /tmp/4ep_results_summary.txt" >> "$SUMMARY"
echo "========================================" >> "$SUMMARY"

echo "[$(date '+%F %T')] ✅ Summary written to $SUMMARY"
