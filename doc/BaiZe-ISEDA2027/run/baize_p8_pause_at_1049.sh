#!/bin/bash
# BaiZe P-8: monitor step 1049 → save ckpt → gracefully pause → launch A/B test
# 运维指令 2026-10-10: MBS 2→3 A/B 验证
#
# This script runs in background:
#   1. Poll /tmp/baize_p8_train.log every 30s for "iteration 1050" (step 1049 done + ckpt saved)
#   2. Send SIGTERM to the P-8 process group (bash script PID)
#   3. Wait for all 8 GPUs to be free (< 1000 MiB)
#   4. Launch baize_p8_ab_test.sh
#
# Launch: setsid bash baize_p8_pause_at_1049.sh > /tmp/baize_p8_pause.log 2>&1 < /dev/null &
set -uo pipefail
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
TRAIN_LOG=/tmp/baize_p8_train.log
AB_SCRIPT="$RUN_DIR/baize_p8_ab_test.sh"
TARGET_STEP=1050   # wait for step 1049 to complete + ckpt saved

echo "===== P-8 pause monitor START @ $(date '+%F %T') ====="
echo "  Watching for step ${TARGET_STEP} in $TRAIN_LOG"

# ========== Phase 1: Wait for target step ==========
while true; do
    # Check if training log shows step >= TARGET_STEP
    if grep -q "iteration.*${TARGET_STEP}/" "$TRAIN_LOG" 2>/dev/null; then
        echo "  [$(date '+%T')] Step ${TARGET_STEP} reached! Checkpoint at step 1049 should be saved."
        break
    fi

    # Check if training process already died
    if ! pgrep -f 'baize_p8_train.sh' > /dev/null 2>&1; then
        echo "  [$(date '+%T')] WARNING: P-8 training process not found (may have crashed or been killed)."
        echo "  Checking GPU status..."
        GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits 2>/dev/null | awk -F',' '{gsub(/ /,"",$2); if($2+0>1000) print $1}')
        if [ -z "$GPU_BUSY" ]; then
            echo "  GPU all free. Proceeding to A/B test."
            break
        else
            echo "  GPU $GPU_BUSY still busy. Waiting..."
        fi
    fi

    # Print current step
    CUR_STEP=$(grep 'iteration' "$TRAIN_LOG" 2>/dev/null | tail -1 | sed -n 's/.*iteration *\([0-9]*\).*/\1/p')
    echo "  [$(date '+%T')] Current step: ${CUR_STEP:-?}, waiting for ${TARGET_STEP}..."
    sleep 30
done

# ========== Phase 2: Gracefully pause P-8 ==========
echo ""
echo "===== Phase 2: Pausing P-8 @ $(date '+%F %T') ====="

# Find the P-8 bash script PID (parent of torchrun)
P8_BASH_PID=$(pgrep -f 'baize_p8_train.sh' | head -1)
if [ -n "$P8_BASH_PID" ]; then
    echo "  P-8 bash script PID: $P8_BASH_PID"
    echo "  Sending SIGTERM to process group..."
    # Kill the process group (negative PID = PGID)
    kill -- -"$P8_BASH_PID" 2>/dev/null || kill "$P8_BASH_PID" 2>/dev/null
    sleep 5
    # Force kill if still alive
    if kill -0 "$P8_BASH_PID" 2>/dev/null; then
        echo "  Still alive, sending SIGKILL..."
        kill -9 -- -"$P8_BASH_PID" 2>/dev/null || kill -9 "$P8_BASH_PID" 2>/dev/null
    fi
else
    echo "  P-8 bash script not found (may have already exited)."
fi

# ========== Phase 3: Wait for GPU to be free ==========
echo ""
echo "===== Phase 3: Waiting for GPU to be free @ $(date '+%F %T') ====="
MAX_WAIT=300  # 5 minutes
WAITED=0
while [ "$WAITED" -lt "$MAX_WAIT" ]; do
    GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits 2>/dev/null | awk -F',' '{gsub(/ /,"",$2); if($2+0>1000) print $1}')
    if [ -z "$GPU_BUSY" ]; then
        echo "  All GPUs free! (waited ${WAITED}s)"
        break
    fi
    echo "  [$(date '+%T')] GPU $GPU_BUSY still busy (waited ${WAITED}s/${MAX_WAIT}s)"
    sleep 10
    WAITED=$((WAITED + 10))
done

if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    echo "  TIMEOUT: GPU still busy after ${MAX_WAIT}s. A/B test will NOT start."
    echo "  Manual intervention required."
    exit 1
fi

# ========== Phase 4: Verify checkpoint ==========
echo ""
echo "===== Phase 4: Verify checkpoint @ $(date '+%F %T') ====="
CKPT_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8
if [ -d "$CKPT_DIR" ]; then
    echo "  Checkpoint directory contents:"
    ls -la "$CKPT_DIR/" 2>/dev/null | head -20
    # Look for iter_0001049 checkpoint
    if find "$CKPT_DIR" -name '*1049*' -type d 2>/dev/null | head -1 | grep -q .; then
        echo "  ✅ Checkpoint at step 1049 found!"
    else
        echo "  ⚠️ No explicit iter_1049 checkpoint dir found, but training may save differently."
    fi
else
    echo "  ⚠️ Checkpoint directory $CKPT_DIR not found!"
fi

# ========== Phase 5: Launch A/B test ==========
echo ""
echo "===== Phase 5: Launching A/B test @ $(date '+%F %T') ====="
echo "  Script: $AB_SCRIPT"
cd "$RUN_DIR" || { echo "  ERROR: cannot cd to $RUN_DIR"; exit 1; }
bash "$AB_SCRIPT"
AB_RC=$?
echo ""
echo "===== A/B test finished @ $(date '+%F %T') rc=${AB_RC} ====="
echo "  Results in /tmp/baize_p8_ab_A_summary.log and /tmp/baize_p8_ab_B_summary.log"
echo "  Full A/B log: /tmp/baize_p8_ab.log"
echo ""
echo "===== P-8 pause monitor + A/B test COMPLETE @ $(date '+%F %T') ====="
