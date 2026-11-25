#!/bin/bash
# R11-F -> R11-G -> R11-H automatic chain.
#   Waits for R11-F (r11f_continue.sh, arms B/C/E/D) to finish, then runs R11-G
#   (AIMv2 108k long run + scaling-curve eval), then R11-H (pure-AR 30k + eval).
#   Per task book 2026-10-04 (七): chain all three to use the overnight window
#   without waiting for the next loop wake-up.
#   Launch:  setsid bash r11fgh_chain.sh &
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

LOG=/tmp/r11fgh_chain.log
DSLOG=/tmp/r11f_datasource.log
echo "===== R11-F-G-H CHAIN START $(date '+%F %T') =====" > "$LOG"

# ---- 1. Wait for R11-F (r11f_continue.sh) to finish ---- #
#    R11-F continuation runs arms B,C,E,D. Detect completion by:
#    (a) the r11f_continue.sh process is gone, AND
#    (b) the "ALL DONE" marker is present in the datasource log (robustness).
echo "[$(date '+%T')] Waiting for R11-F (r11f_continue.sh) to finish..." >> "$LOG"
while pgrep -f 'r11f_continue.sh' > /dev/null 2>&1; do
    echo "[$(date '+%T')] R11-F still running (r11f_continue.sh alive), waiting 120s..." >> "$LOG"
    sleep 120
done
echo "[$(date '+%T')] r11f_continue.sh process gone." >> "$LOG"
if grep -q 'R11-F CONTINUATION ALL DONE' "$DSLOG" 2>/dev/null; then
    echo "[$(date '+%T')] R11-F CONTINUATION ALL DONE marker found." >> "$LOG"
else
    echo "[$(date '+%T')] WARNING: R11-F marker NOT found (process died?). Proceeding to GPU-free check." >> "$LOG"
fi

# ---- 2. Wait for GPU to be fully free ---- #
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date '+%T')] GPU still has compute processes, waiting 30s..." >> "$LOG"
    sleep 30
done
echo "[$(date '+%T')] GPU free." >> "$LOG"

# ---- 3. Run R11-G (AIMv2 108k long run + scaling-curve eval) ---- #
echo "[$(date '+%T')] Launching R11-G (AIMv2 108k long run)..." >> "$LOG"
bash r11g_run_aimv2_long.sh 108000 6 >> "$LOG" 2>&1
echo "[$(date '+%T')] R11-G done (exit $?). Log: /tmp/r11g_aimv2_long.log" >> "$LOG"

# ---- 4. Wait for GPU to be free again ---- #
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date '+%T')] GPU still has compute processes (post R11-G), waiting 30s..." >> "$LOG"
    sleep 30
done
echo "[$(date '+%T')] GPU free after R11-G." >> "$LOG"

# ---- 5. Run R11-H (pure AR, no contrast, 30k + eval) ---- #
echo "[$(date '+%T')] Launching R11-H (pure AR, no contrast)..." >> "$LOG"
bash r11h_run_pure_ar.sh 30000 6 >> "$LOG" 2>&1
echo "[$(date '+%T')] R11-H done (exit $?). Log: /tmp/r11h_pure_ar.log" >> "$LOG"

echo "===== R11-F-G-H CHAIN ALL DONE $(date '+%F %T') =====" >> "$LOG"
