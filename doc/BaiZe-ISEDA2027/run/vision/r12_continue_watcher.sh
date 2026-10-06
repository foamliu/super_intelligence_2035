#!/bin/bash
# R12 续跑 watcher — waits for (1) R12 training ranks to exit, (2) R12 eval watcher
# (PID 3282690) to exit, THEN launches r12_continue_3epoch.sh automatically.
#
# Created 2026-10-05 19:00.  R12 training is at step ~49k/120k and will finish ~21:00.
# The eval watcher (r12_eval_watcher.sh PID 3282690) will then eval ~13 ckpts (~1.3h).
# This watcher polls every 5 min; once both are done, it starts the 3-epoch continuation.
#
# Usage:  nohup setsid bash r12_continue_watcher.sh > /tmp/r12_continue_watcher.log 2>&1 &
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"

LOG=/tmp/r12_continue_watcher.log
TRAIN_LOG=/tmp/r12_fulldata_aimv2.log
CONT_LOG=/tmp/r12_continue_3epoch.log

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

log "===== R12 continue watcher START ====="

# Phase 1: Wait for R12 training ranks to exit
log "Phase 1: waiting for R12 training ranks (r9_train.py) to exit..."
while true; do
    N=$(ps -eo pid=,args= 2>/dev/null | grep 'r9_train.py' | grep -v 'cline' | grep -v grep | grep -c python)
    N=${N:-0}
    if [ "$N" -eq 0 ]; then
        log "Phase 1 done: all R12 training ranks exited."
        break
    fi
    STEP=$(grep -E '^\[step' "$TRAIN_LOG" 2>/dev/null | tail -1 | awk '{print $2}')
    log "Phase 1: $N ranks alive, latest $STEP"
    sleep 300
done

# Phase 2: Wait for R12 eval watcher to exit
log "Phase 2: waiting for R12 eval watcher (r12_eval_watcher.sh) to exit..."
while true; do
    EW=$(ps -eo pid=,args= 2>/dev/null | grep 'r12_eval_watcher' | grep -v grep | grep -c bash)
    EW=${EW:-0}
    if [ "$EW" -eq 0 ]; then
        log "Phase 2 done: R12 eval watcher exited."
        break
    fi
    log "Phase 2: eval watcher still running ($EW process)"
    sleep 300
done

# Phase 3: Verify resume checkpoint exists
log "Phase 3: verifying resume checkpoint..."
OUT=/nas_train/app.e0031982/datasets/baize-vision/out/R12_fulldata_aimv2_w512
sleep 15  # give NFS a moment to flush
RESUME=""
for cand in "$OUT/vision.pt" "$OUT/vision_fused.pt"; do
    if [ -f "$cand" ]; then
        RESUME="$cand"
        break
    fi
done
if [ -z "$RESUME" ]; then
    RESUME=$(ls -t "$OUT"/vision_step*.pt 2>/dev/null | head -1)
fi
if [ -z "$RESUME" ] || [ ! -f "$RESUME" ]; then
    log "Phase 3 FAILED: no checkpoint found in $OUT — cannot continue. Aborting."
    exit 1
fi
RESUME_STEP=$(basename "$RESUME")
log "Phase 3 done: resume ckpt = $RESUME ($RESUME_STEP)"

# Phase 4: GPU free check (make sure no lingering processes)
log "Phase 4: GPU free check..."
sleep 10
GPU_PROCS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
log "Phase 4: $GPU_PROCS GPU compute processes detected."
if [ "$GPU_PROCS" -gt 0 ]; then
    log "Phase 4: WARNING — GPU still has processes. Waiting 120s for cleanup..."
    sleep 120
    GPU_PROCS2=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
    log "Phase 4: after wait, $GPU_PROCS2 GPU processes. Proceeding anyway."
fi

# Phase 5: Launch the 3-epoch continuation
log "Phase 5: launching r12_continue_3epoch.sh ..."
bash r12_continue_3epoch.sh "$RESUME" 6 >> "$LOG" 2>&1
RC=$?
log "Phase 5: r12_continue_3epoch.sh exited (rc=$RC)"
log "===== R12 continue watcher ALL DONE ====="
