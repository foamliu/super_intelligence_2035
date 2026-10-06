#!/bin/bash
# AIMv2 提速 — ② Data pipeline optimization: num_workers sweep at bs=64
#   Attribution showed data/IO limited at bs=64 (GPU util ~70%, not saturated).
#   Test num_workers 6/12/16 at bs=64 (production recipe, global 512 unchanged).
#   Usage: setsid bash r12_throughput_bench_nw.sh &
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${GPIC},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
BENCH_OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out/bench_throughput

run_nw_bench() {
    NW=$1
    OUT="$BENCH_OUTROOT/nw${NW}"
    mkdir -p "$OUT"
    LOG="/tmp/bench_nw${NW}.log"

    echo "===== NW=$NW START $(date '+%F %T') =====" | tee -a /tmp/r12_bench_nw.log

    # Start training in background
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29700 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps 250 --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 9999 --probe-n 128 --num-workers "$NW" \
        --save-every 0 \
        --eval-data "$EVAL" \
        > "$LOG" 2>&1 &
    TRAIN_PID=$!

    # Wait for training to start
    for i in $(seq 1 60); do
        if grep -q '\[step ' "$LOG" 2>/dev/null; then
            echo "Training started!" | tee -a /tmp/r12_bench_nw.log
            break
        fi
        sleep 2
    done

    # Wait for training to finish
    wait $TRAIN_PID
    rc=$?

    echo "NW=$NW training exit=$rc" | tee -a /tmp/r12_bench_nw.log
    grep '\[done\]' "$LOG" | tee -a /tmp/r12_bench_nw.log
    echo "Steady-state (steps 60-250):" | tee -a /tmp/r12_bench_nw.log
    grep '\[step ' "$LOG" | awk 'NR>=6' | tee -a /tmp/r12_bench_nw.log
    echo "===== NW=$NW END $(date '+%F %T') =====" | tee -a /tmp/r12_bench_nw.log
    echo "" | tee -a /tmp/r12_bench_nw.log
}

# NW=6 is the baseline (already measured: steady_image_s=4993.1)
# Test 12 and 16
run_nw_bench 12
run_nw_bench 16

echo "===== ALL NW BENCH DONE $(date '+%F %T') =====" | tee -a /tmp/r12_bench_nw.log