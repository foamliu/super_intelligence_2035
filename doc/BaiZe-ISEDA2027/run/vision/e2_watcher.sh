#!/bin/bash
# e2_watcher.sh — waits for E1 to finish, then runs E2 smoke + full training (⑥ revised: w768/d30)
# Created 2026-10-08 per operator instruction ⑥
set -uo pipefail
cd "$(dirname "$0")"

E1_SCRIPT_PID=1429345  # bash run_scaling_experiment.sh e1
LOG=/tmp/e2_watcher.log
echo "[$(date '+%F %T')] E2 watcher started — waiting for E1 (PID $E1_SCRIPT_PID) to finish..." | tee "$LOG"

# Wait for E1 script process to exit
while kill -0 "$E1_SCRIPT_PID" 2>/dev/null; do
    sleep 60
done
echo "[$(date '+%F %T')] E1 script (PID $E1_SCRIPT_PID) has exited." | tee -a "$LOG"

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

echo "[$(date '+%F %T')] E2 watcher complete. Both arms should now be done." | tee -a "$LOG"
