#!/bin/bash
# ==============================================================================
# e2fair_watcher.sh — 2026-10-09⑨ fair rerun chain watcher
# Waits for E1fair (run_scaling_experiment.sh e1fair) to finish, then launches
# E2fair (run_scaling_experiment.sh e2fair 187101) automatically.
#
# The e1fair mode runs: E1fair training → E1fair eval (Prot B + Prot A) → exit.
# It does NOT chain to E2fair. This watcher bridges that gap.
#
# Launch: setsid bash e2fair_watcher.sh > /tmp/e2fair_watcher.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

LOG=/tmp/e2fair_watcher.log
STEPS=187101
E1FAIR_LOG=/tmp/scaling_e1fair.log
E2FAIR_LOG=/tmp/scaling_e2fair.log

echo "[$(date '+%F %T')] e2fair_watcher STARTED — waiting for E1fair to finish..." | tee -a "$LOG"

# ---- Phase 1: Wait for E1fair process to exit ----
# The e1fair parent process runs run_scaling_experiment.sh with mode=e1fair.
# We detect it by looking for the r9_train.py process with "E1fair" in output-dir.
while true; do
    # Check if any r9_train.py process with E1fair output-dir is still running
    E1_RUNNING=$(ps -eo args= | grep 'r9_train.py' | grep 'scaling_E1fair' | grep -v grep | head -1)
    # Also check if the run_scaling_experiment.sh e1fair parent is still alive
    E1_SCRIPT=$(ps -eo args= | grep 'run_scaling_experiment.sh' | grep 'e1fair' | grep -v grep | head -1)

    if [ -z "$E1_RUNNING" ] && [ -z "$E1_SCRIPT" ]; then
        echo "[$(date '+%F %T')] E1fair process gone. Checking if E1fair completed successfully..." | tee -a "$LOG"
        break
    fi
    sleep 60
done

# ---- Phase 2: Verify E1fair completed successfully ----
# Look for "E1fair done (exit 0)" in the E1fair log
if grep -q 'E1fair done (exit 0)' "$E1FAIR_LOG" 2>/dev/null; then
    echo "[$(date '+%F %T')] ✅ E1fair training succeeded (exit 0)." | tee -a "$LOG"
else
    echo "[$(date '+%F %T')] 🚫 E1fair training may have FAILED — 'E1fair done (exit 0)' not found in log." | tee -a "$LOG"
    echo "[$(date '+%F %T')] Last 20 lines of E1fair log:" | tee -a "$LOG"
    tail -20 "$E1FAIR_LOG" 2>/dev/null | tee -a "$LOG"
    echo "[$(date '+%F %T')] ABORTING E2fair launch — E1fair did not complete successfully." | tee -a "$LOG"
    exit 1
fi

# Check if E1fair eval also completed
if grep -q 'e1fair eval DONE' /tmp/scaling_e1fair_eval.log 2>/dev/null; then
    echo "[$(date '+%F %T')] ✅ E1fair eval also completed." | tee -a "$LOG"
else
    echo "[$(date '+%F %T')] ⚠️ E1fair eval may still be running or failed — proceeding to E2fair anyway." | tee -a "$LOG"
fi

# ---- Phase 3: Verify GPU is free before launching E2fair ----
echo "[$(date '+%F %T')] Checking GPU status before E2fair launch..." | tee -a "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv | tee -a "$LOG"

# ---- Phase 4: Launch E2fair ----
echo "[$(date '+%F %T')] 🚀 Launching E2fair (steps=$STEPS)..." | tee -a "$LOG"
bash run_scaling_experiment.sh e2fair "$STEPS" 6 2>&1 | tee -a "$LOG"
E2_RC=${PIPESTATUS[0]}
echo "[$(date '+%F %T')] E2fair pipeline finished (rc=$E2_RC)." | tee -a "$LOG"

# ---- Phase 5: Summary ----
echo "" | tee -a "$LOG"
echo "[$(date '+%F %T')] ===== CHAIN WATCHER COMPLETE =====" | tee -a "$LOG"
echo "E1fair training: $(grep 'E1fair done' "$E1FAIR_LOG" 2>/dev/null | tail -1)" | tee -a "$LOG"
echo "E2fair training: $(grep 'E2fair done' "$E2FAIR_LOG" 2>/dev/null | tail -1)" | tee -a "$LOG"
echo "E1fair eval:     $(grep 'e1fair eval DONE' /tmp/scaling_e1fair_eval.log 2>/dev/null | tail -1)" | tee -a "$LOG"
echo "E2fair eval:     $(grep 'e2fair eval DONE' /tmp/scaling_e2fair_eval.log 2>/dev/null | tail -1)" | tee -a "$LOG"
echo "[$(date '+%F %T')] All fair rerun experiments complete. Next agent wake should collect results + write report." | tee -a "$LOG"
