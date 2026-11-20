#!/bin/bash
# AIMv2 提速 — ① 归因实测 (bs=128 and bs=256, run after bs=64 completed)
#   Monitors GPU util AFTER training starts (waits for step 10 in log).
#   Usage: setsid bash r12_throughput_bench_128_256.sh &
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

run_bench() {
    BS=$1
    OUT="$BENCH_OUTROOT/bs${BS}"
    mkdir -p "$OUT"
    LOG="/tmp/bench_bs${BS}.log"
    MONLOG="/tmp/bench_bs${BS}_mon.log"

    echo "===== BS=$BS START $(date '+%F %T') =====" | tee -a /tmp/r12_bench_run.log

    # Start training in background
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29600 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps 250 --resolution 224 --patch 16 \
        --batch-size "$BS" --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 9999 --probe-n 128 --num-workers 6 \
        --save-every 0 \
        --eval-data "$EVAL" \
        > "$LOG" 2>&1 &
    TRAIN_PID=$!

    # Wait for training to start (step 10 appears in log)
    echo "Waiting for training to start (TRAIN_PID=$TRAIN_PID)..."
    for i in $(seq 1 60); do
        if grep -q '\[step ' "$LOG" 2>/dev/null; then
            echo "Training started! Beginning GPU monitoring."
            break
        fi
        sleep 2
    done

    # Start GPU monitoring (60 samples at 1s interval) — now training is active
    nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader -l 1 -c 60 > "$MONLOG" 2>&1 &
    MON_PID=$!

    # Wait for training to finish
    wait $TRAIN_PID
    rc=$?
    wait $MON_PID 2>/dev/null

    echo "BS=$BS training exit=$rc" | tee -a /tmp/r12_bench_run.log

    # Print results
    echo "" | tee -a /tmp/r12_bench_run.log
    echo "--- BS=$BS RESULTS ---" | tee -a /tmp/r12_bench_run.log
    grep '\[done\]' "$LOG" | tee -a /tmp/r12_bench_run.log
    echo "Steady-state [step] lines (last 10):" | tee -a /tmp/r12_bench_run.log
    grep '\[step ' "$LOG" | tail -10 | tee -a /tmp/r12_bench_run.log
    echo "GPU monitoring (util + mem):" | tee -a /tmp/r12_bench_run.log
    cat "$MONLOG" | tee -a /tmp/r12_bench_run.log
    echo "GPU util avg (sm%):" | tee -a /tmp/r12_bench_run.log
    cat "$MONLOG" | awk -F',' '{gsub(/[^0-9]/,"",$2); gsub(/[^0-9]/,"",$3); sum+=$2; if($3+0>maxmem) maxmem=$3; n++} END{if(n>0) printf "  avg_util=%.1f%%  peak_mem=%d MiB  (n=%d samples)\n", sum/n, maxmem, n}' | tee -a /tmp/r12_bench_run.log
    echo "===== BS=$BS END $(date '+%F %T') =====" | tee -a /tmp/r12_bench_run.log
    echo "" | tee -a /tmp/r12_bench_run.log
}

run_bench 128
run_bench 256

echo "===== ALL BENCH DONE $(date '+%F %T') =====" | tee -a /tmp/r12_bench_run.log