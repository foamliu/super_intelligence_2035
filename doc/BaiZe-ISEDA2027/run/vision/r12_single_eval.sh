#!/bin/bash
# R12 3-epoch eval: 4-GPU parallel (not 8), data in page cache, then auto-run scaling.
# Replaces the stuck r12_parallel_eval.py (8 procs × redundant NFS reads).
set -euo pipefail

OUT="/nas_train/app.e0031982/datasets/baize-vision/out/R12_fulldata_aimv2_w512"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
VISION_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision"
MERGED_LOG="/tmp/r12_continue_eval_watcher.log"
PARALLEL_DIR="/tmp/r12_single_eval"
NGPU=4
LOG="/tmp/r12_single_eval_main.log"

mkdir -p "$PARALLEL_DIR"
rm -f "$PARALLEL_DIR"/*.log 2>/dev/null || true

# Collect all step ckpts sorted by step number
mapfile -t CKPTS < <(ls "$OUT"/vision_step*.pt | sort -t'p' -k3 -n)
# Add vision.pt (final, step 344k) if it exists and isn't already a step ckpt
if [ -f "$OUT/vision.pt" ]; then
    CKPTS+=("$OUT/vision.pt")
fi

TOTAL=${#CKPTS[@]}
echo "[$(date '+%H:%M:%S')] Total ckpts: $TOTAL" | tee "$LOG"

# Round-robin split across NGPU
for g in $(seq 0 $((NGPU-1))); do
    groups[$g]=""
done
for i in "${!CKPTS[@]}"; do
    g=$((i % NGPU))
    groups[$g]+="${CKPTS[$i]} "
done

# Launch parallel processes
PIDS=()
for g in $(seq 0 $((NGPU-1))); do
    ckpt_list="${groups[$g]}"
    n=$(echo $ckpt_list | wc -w)
    echo "[$(date '+%H:%M:%S')] Launching GPU $g: $n ckpts" | tee -a "$LOG"
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

echo "[$(date '+%H:%M:%S')] PIDs: ${PIDS[*]}" | tee -a "$LOG"

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
    echo "[$(date '+%H:%M:%S')] Progress: $PROGRESS (done: $DONE/$NGPU)" | tee -a "$LOG"
done

echo "[$(date '+%H:%M:%S')] All eval processes complete" | tee -a "$LOG"

# Merge results into the log the scaling script reads
echo "[$(date '+%H:%M:%S')] Merging results..." | tee -a "$LOG"
{
    echo "Starting IN-1k eval on $TOTAL ckpts (full 3-epoch scaling curve)..."
    for g in $(seq 0 $((NGPU-1))); do
        grep -E "\[R8-IN1K\] (ckpt=|zero-shot)" "$PARALLEL_DIR/gpu${g}.log" 2>/dev/null || true
    done
    echo "[R8-IN1K] DONE"
    echo "===== R12-continue eval watcher ALL DONE ====="
} > "$MERGED_LOG"

N_RESULTS=$(grep -c "linear-probe top1=" "$MERGED_LOG" || echo 0)
echo "[$(date '+%H:%M:%S')] Merged $N_RESULTS/$TOTAL results into $MERGED_LOG" | tee -a "$LOG"

# Auto-run scaling analysis
echo "[$(date '+%H:%M:%S')] Running r12_3epoch_scaling.py..." | tee -a "$LOG"
$PY "$VISION_DIR/r12_3epoch_scaling.py" --r12-log "$MERGED_LOG" 2>&1 | tee -a "$LOG"

echo "[$(date '+%H:%M:%S')] ALL DONE" | tee -a "$LOG"
