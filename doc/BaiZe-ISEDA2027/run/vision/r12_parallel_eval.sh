#!/bin/bash
# R12 3-epoch parallel eval: split 35 ckpts across 8 GPUs for ~10x speedup.
# Each GPU runs r8_eval_in1k.py on a subset of ckpts, writing to its own log.
# After all complete, merge logs into /tmp/r12_continue_eval_watcher.log
# (the path r12_3epoch_scaling.py reads from).
#
# Created 2026-10-06.  Replaces the sequential eval watcher (killed at 10:36).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUT=/nas_train/app.e0031982/datasets/baize-vision/out/R12_fulldata_aimv2_w512
MERGED_LOG=/tmp/r12_continue_eval_watcher.log
PARALLEL_DIR=/tmp/r12_parallel_eval

mkdir -p "$PARALLEL_DIR"
rm -f "$PARALLEL_DIR"/gpu*.log

# All 34 step ckpts sorted by step + vision.pt (344k)
ALL_CKPTS=$(ls "$OUT"/vision_step*.pt | sort -V)
FINAL_CKPT="$OUT/vision.pt"

# Split into 8 groups (round-robin by sorted order for even step distribution)
# GPU 0: 10k,90k,170k,250k,330k
# GPU 1: 20k,100k,180k,260k,340k
# GPU 2: 30k,110k,190k,270k,vision.pt
# GPU 3: 40k,120k,200k,280k
# GPU 4: 50k,130k,210k,290k
# GPU 5: 60k,140k,220k,300k
# GPU 6: 70k,150k,230k,310k
# GPU 7: 80k,160k,240k,320k
i=0
declare -A GPU_CKPTS
for gpu in 0 1 2 3 4 5 6 7; do GPU_CKPTS[$gpu]=""; done
for ckpt in $ALL_CKPTS "$FINAL_CKPT"; do
    gpu=$((i % 8))
    GPU_CKPTS[$gpu]="${GPU_CKPTS[$gpu]} $ckpt"
    i=$((i + 1))
done

echo "===== R12 parallel eval START $(date '+%F %T') =====" > "$MERGED_LOG"

# Launch 8 parallel eval processes
PIDS=()
for gpu in 0 1 2 3 4 5 6 7; do
    ckpts="${GPU_CKPTS[$gpu]}"
    log="$PARALLEL_DIR/gpu${gpu}.log"
    echo "GPU $gpu: $ckpts"
    CUDA_VISIBLE_DEVICES=$gpu \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    "$PY" r8_eval_in1k.py --ckpts $ckpts > "$log" 2>&1 &
    PIDS+=($!)
done

echo "Launched ${#PIDS[@]} parallel eval processes: ${PIDS[@]}"
echo "Waiting for all to complete..."

# Wait for all
FAIL=0
for pid in "${PIDS[@]}"; do
    if ! wait "$pid"; then
        echo "WARNING: PID $pid exited with non-zero status"
        FAIL=1
    fi
done

echo "All eval processes complete (fail=$FAIL) at $(date '+%F %T')"

# Merge: extract ckpt+result pairs from each GPU log, sort by step, output.
# Use awk to pair lines, extract step for sorting, then re-format.
echo "Merging results..."
{
    echo "Starting IN-1k eval on 35 ckpts (full 3-epoch scaling curve)..."
    for gpu in 0 1 2 3 4 5 6 7; do
        grep -E '\[R8-IN1K\] (ckpt=|zero-shot)' "$PARALLEL_DIR/gpu${gpu}.log" 2>/dev/null
    done
    echo "[R8-IN1K] DONE"
    echo "===== R12-continue eval watcher ALL DONE ====="
} > "$MERGED_LOG"

echo "Merged log written to $MERGED_LOG"
echo "===== R12 parallel eval ALL DONE $(date '+%F %T') =====" >> "$MERGED_LOG"
echo "Done at $(date '+%F %T')"
exit $FAIL
