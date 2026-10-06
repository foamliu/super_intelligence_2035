#!/bin/bash
# R12b eval watcher — backup: if the parent r12b_fulldata_fresh.sh dies
# (orphan pattern seen in R12/R12-continue), this watcher detects training
# completion and runs 4-GPU parallel IN-1k eval + scaling analysis.
#
# If the parent script's built-in auto-eval (lines 73-89 of r12b_fulldata_fresh.sh)
# already fired, this watcher detects it and exits WITHOUT double-evaluating.
#
# Created 2026-10-06 18:00 (R12b step~107k/272k, ETA~02:00).
#
# Usage: nohup setsid bash r12b_eval_watcher.sh > /tmp/r12b_eval_watcher.log 2>&1 &
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUT=/nas_train/app.e0031982/datasets/baize-vision/out/R12b_fulldata_aimv2_w512
TRAIN_LOG=/tmp/r12b_fulldata_aimv2.log
WATCHER_LOG=/tmp/r12b_eval_watcher.log
PARALLEL_DIR=/tmp/r12b_single_eval
NGPU=4
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

log() { echo "$(date '+%F %T') $*" >> "$WATCHER_LOG"; }

log "===== R12b eval watcher START ====="
log "Monitoring for r9_train.py (R12b) processes to exit..."

# Phase 1: Wait for training ranks to exit
while true; do
    N=$(ps -eo pid=,args= 2>/dev/null | grep 'r9_train.py' | grep 'R12b_fulldata' | grep -v grep | grep -c python)
    N=${N:-0}
    if [ "$N" -eq 0 ]; then
        log "All R12b training ranks exited (N=$N). Proceeding to check eval status."
        break
    fi
    # Check if training is done but ranks hung at cleanup
    if grep -q '\[done\]' "$TRAIN_LOG" 2>/dev/null; then
        log "[done] found in train log but $N ranks still alive — waiting 120s for cleanup..."
        sleep 120
        N2=$(ps -eo pid=,args= 2>/dev/null | grep 'r9_train.py' | grep 'R12b_fulldata' | grep -v grep | grep -c python)
        N2=${N2:-0}
        if [ "$N2" -gt 0 ]; then
            log "$N2 ranks still alive after [done]+120s — killing hung ranks."
            pkill -f 'r9_train.py.*R12b_fulldata' 2>/dev/null || true
            sleep 5
        fi
        break
    fi
    STEP=$(grep -E '^\[step' "$TRAIN_LOG" 2>/dev/null | tail -1 | awk '{print $2}')
    log "Training in progress: $N ranks alive, latest $STEP"
    sleep 300
done

# Phase 2: Check if built-in auto-eval already fired
log "Checking if built-in auto-eval already started..."
sleep 15  # give parent script time to write its eval header

if grep -q 'R12b IN-1k eval' "$TRAIN_LOG" 2>/dev/null; then
    log "Built-in auto-eval already fired in parent script. Waiting for it to complete..."
    # Wait for built-in eval to finish (look for "ALL DONE" or "R12b ALL DONE")
    while ! grep -q 'R12b ALL DONE\|R12b throughput test' "$TRAIN_LOG" 2>/dev/null; do
        sleep 60
        log "Waiting for built-in eval to complete..."
    done
    log "Built-in auto-eval completed. Extracting results for scaling analysis."
    # Built-in eval already ran r8_eval_in1k.py — results are in TRAIN_LOG
    # Run scaling analysis using the train log as input
    log "Running scaling analysis (r12b_scaling.py)..."
    "$PY" "$VISION_DIR/r12b_scaling.py" --r12b-log "$TRAIN_LOG" >> "$WATCHER_LOG" 2>&1
    log "===== R12b eval watcher ALL DONE (built-in eval path) ====="
    exit 0
fi

log "Built-in auto-eval did NOT fire (parent script likely died). Running eval now."

# Phase 3: Collect ALL R12b checkpoints
log "Collecting ALL checkpoints from $OUT"
sleep 10  # give NFS a moment to flush

mapfile -t CKPTS < <(ls "$OUT"/vision_step*.pt 2>/dev/null | sort -t'p' -k3 -n)
if [ -f "$OUT/vision.pt" ]; then
    CKPTS+=("$OUT/vision.pt")
fi

TOTAL=${#CKPTS[@]}
log "Found $TOTAL checkpoints"

if [ "$TOTAL" -eq 0 ]; then
    log "ERROR: zero checkpoints found. NOT evaluating."
    exit 1
fi

# Phase 4: Run 4-GPU parallel eval (proven pattern from r12_single_eval.sh)
mkdir -p "$PARALLEL_DIR"
rm -f "$PARALLEL_DIR"/*.log 2>/dev/null || true

log "Starting 4-GPU parallel IN-1k eval on $TOTAL ckpts..."

# Round-robin split across NGPU
for g in $(seq 0 $((NGPU-1))); do
    groups[$g]=""
done
for i in "${!CKPTS[@]}"; do
    g=$((i % NGPU))
    groups[$g]+="${CKPTS[$i]} "
done

PIDS=()
for g in $(seq 0 $((NGPU-1))); do
    ckpt_list="${groups[$g]}"
    n=$(echo $ckpt_list | wc -w)
    log "Launching GPU $g: $n ckpts"
    CUDA_VISIBLE_DEVICES=$g \
    OMP_NUM_THREADS=16 \
    MKL_NUM_THREADS=16 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    PYTHONUNBUFFERED=1 \
    nohup $PY "$VISION_DIR/r8_eval_in1k.py" --ckpts $ckpt_list \
        > "$PARALLEL_DIR/gpu${g}.log" 2>&1 &
    PIDS+=($!)
    sleep 3  # stagger to reduce NFS thundering herd
done

log "Eval PIDs: ${PIDS[*]}"

# Wait for all
DONE=0
while [ $DONE -lt $NGPU ]; do
    sleep 30
    DONE=0
    PROGRESS=""
    for g in $(seq 0 $((NGPU-1))); do
        if ! kill -0 ${PIDS[$g]} 2>/dev/null; then
            DONE=$((DONE+1))
        fi
        n_done=$(grep -c "linear-probe top1=" "$PARALLEL_DIR/gpu${g}.log" 2>/dev/null || echo 0)
        PROGRESS+="GPU${g}:${n_done} "
    done
    log "Eval progress: $PROGRESS (done: $DONE/$NGPU)"
done

log "All eval processes complete"

# Phase 5: Merge results and run scaling analysis
log "Merging results..."
{
    echo "Starting IN-1k eval on $TOTAL ckpts (R12b full-data scaling curve)..."
    for g in $(seq 0 $((NGPU-1))); do
        grep -E "\[R8-IN1K\] (ckpt=|zero-shot)" "$PARALLEL_DIR/gpu${g}.log" 2>/dev/null || true
    done
    echo "[R8-IN1K] DONE"
} > "$WATCHER_LOG.results"

N_RESULTS=$(grep -c "linear-probe top1=" "$WATCHER_LOG.results" || echo 0)
log "Merged $N_RESULTS/$TOTAL results"

log "Running scaling analysis (r12b_scaling.py)..."
"$PY" "$VISION_DIR/r12b_scaling.py" --r12b-log "$WATCHER_LOG.results" >> "$WATCHER_LOG" 2>&1

log "===== R12b eval watcher ALL DONE ====="
