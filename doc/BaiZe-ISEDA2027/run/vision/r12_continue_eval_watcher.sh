#!/bin/bash
# R12-continue eval watcher — waits for 3-epoch continuation training ranks to exit,
# then auto-runs IN-1k eval on ALL checkpoints (R12's 10k..120k + continuation's 130k..344k).
#
# Created 2026-10-05 23:40.  The parent r12_continue_3epoch.sh + torchrun died
# (same orphan pattern as R12), so the script's built-in auto-eval (lines 86-101)
# will NOT fire.  This watcher replaces it.
#
# Usage: nohup setsid bash r12_continue_eval_watcher.sh > /tmp/r12_continue_eval_watcher.log 2>&1 &
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUT=/nas_train/app.e0031982/datasets/baize-vision/out/R12_fulldata_aimv2_w512
TRAIN_LOG=/tmp/r12_continue_3epoch.log
WATCHER_LOG=/tmp/r12_continue_eval_watcher.log

log() { echo "$(date '+%F %T') $*" >> "$WATCHER_LOG"; }

log "===== R12-continue eval watcher START ====="
log "Monitoring for r9_train.py rank processes to exit..."

# Phase 1: Wait for training ranks to exit
while true; do
    N=$(ps -eo pid=,args= 2>/dev/null | grep 'r9_train.py' | grep -v 'cline' | grep -v grep | grep -c python)
    N=${N:-0}
    if [ "$N" -eq 0 ]; then
        log "All training ranks exited (N=$N). Proceeding to eval."
        break
    fi
    # Check if training is done but ranks hung at cleanup
    if grep -q '\[done\]' "$TRAIN_LOG" 2>/dev/null; then
        log "[done] found in train log but $N ranks still alive — waiting 120s for cleanup..."
        sleep 120
        N2=$(ps -eo pid=,args= 2>/dev/null | grep 'r9_train.py' | grep -v 'cline' | grep -v grep | grep -c python)
        N2=${N2:-0}
        if [ "$N2" -gt 0 ]; then
            log "$N2 ranks still alive after [done]+120s — killing hung ranks."
            pkill -f 'r9_train.py.*R12_fulldata_aimv2' 2>/dev/null || true
            sleep 5
        fi
        break
    fi
    STEP=$(grep -E '^\[step' "$TRAIN_LOG" 2>/dev/null | tail -1 | awk '{print $2}')
    log "Training in progress: $N ranks alive, latest $STEP"
    sleep 300
done

# Phase 2: Collect ALL checkpoints (R12 + continuation)
log "Collecting ALL checkpoints from $OUT"
sleep 10  # give NFS a moment to flush

CKPTS=()
while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$OUT"/vision_step*.pt 2>/dev/null | sort -V)
FINAL="$OUT/vision.pt"
[ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
[ -f "$FINAL" ] && CKPTS+=("$FINAL")

log "Found ${#CKPTS[@]} checkpoints:"
for c in "${CKPTS[@]}"; do log "  $c"; done

if [ "${#CKPTS[@]}" -eq 0 ]; then
    log "ERROR: zero checkpoints found. NOT evaluating."
    exit 1
fi

# Phase 3: Run IN-1k eval (full scaling curve: R12 + continuation)
log "Starting IN-1k eval on ${#CKPTS[@]} ckpts (full 3-epoch scaling curve)..."
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
"$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$WATCHER_LOG" 2>&1
rc=$?
log "R12-continue eval done (exit $rc)"
log "===== R12-continue eval watcher ALL DONE ====="
