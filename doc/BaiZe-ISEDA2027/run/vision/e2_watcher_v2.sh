#!/bin/bash
# e2_watcher_v2.sh — waits for E1 resume to finish, then runs E2 smoke + full training + eval
# Created 2026-10-09 after E1 crash recovery (step 131490/187101, DataLoader bus error)
# Pipeline: E1 resume (130k→187k) → E2 smoke (30 steps) → E2 full (1 epoch) → eval both final ckpts
set -uo pipefail
cd "$(dirname "$0")"

LOG=/tmp/e2_watcher_v2.log
E1_RESUME_PID="${1:-}"

if [ -z "$E1_RESUME_PID" ]; then
    echo "[$(date '+%F %T')] ERROR: must provide E1 resume PID as argument" | tee "$LOG"
    exit 1
fi

echo "[$(date '+%F %T')] E2 watcher v2 started — waiting for E1 resume (PID $E1_RESUME_PID) to finish..." | tee "$LOG"

# Wait for E1 resume process to exit
while kill -0 "$E1_RESUME_PID" 2>/dev/null; do
    sleep 60
done
echo "[$(date '+%F %T')] E1 resume (PID $E1_RESUME_PID) has exited." | tee -a "$LOG"

# Small buffer for GPU memory to release
sleep 30
echo "[$(date '+%F %T')] GPU buffer wait done. Checking GPU state..." | tee -a "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv | tee -a "$LOG"

# Step 1: E2 smoke test (30 steps) to measure throughput
echo "[$(date '+%F %T')] Starting E2 smoke test (w768/d30, 30 steps)..." | tee -a "$LOG"
bash run_scaling_experiment.sh smoke_e2 2>&1 | tee -a "$LOG"
SMOKE_RC=${PIPESTATUS[0]}
echo "[$(date '+%F %T')] E2 smoke exit code: $SMOKE_RC" | tee -a "$LOG"

# Report smoke throughput
grep -E 'image/s|params' /tmp/scaling_e2.log | tail -5 | tee -a "$LOG"

# Step 2: E2 full training (1 epoch)
echo "[$(date '+%F %T')] Starting E2 full training (w768/d30, 1 epoch)..." | tee -a "$LOG"
bash run_scaling_experiment.sh e2 2>&1 | tee -a "$LOG"
E2_RC=${PIPESTATUS[0]}
echo "[$(date '+%F %T')] E2 training exit code: $E2_RC" | tee -a "$LOG"

# Step 3: Evaluate E1 final checkpoint (in case it wasn't evaluated by the resume script)
echo "[$(date '+%F %T')] Evaluating E1 final checkpoint..." | tee -a "$LOG"
bash run_scaling_experiment.sh eval_final 2>&1 | tee -a "$LOG"

echo "[$(date '+%F %T')] E2 watcher v2 complete. Both arms should now be done + evaluated." | tee -a "$LOG"
