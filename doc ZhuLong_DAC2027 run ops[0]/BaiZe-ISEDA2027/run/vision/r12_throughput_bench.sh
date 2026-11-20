#!/bin/bash
# AIMv2 提速 — ① 归因实测 (attribution benchmark)
#   Operator instruction (archived): "运维前置 · 2026-10-05 AIMv2 提速"
#   Test bs 64/128/256 × ≥200 steps, record ms/iter, image/s, GPU util, memory peak.
#   Purpose: determine if bottleneck is data/IO (util<70% or ms/iter flat) or
#            compute (util≈100% and img/s scales with MBS).
#
# Usage: bash r12_throughput_bench.sh
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
SUMMARY=/tmp/r12_throughput_bench_summary.txt
echo "===== AIMv2 Throughput Attribution Benchmark $(date '+%F %T') =====" > "$SUMMARY"
echo "Data: GPIC+CC12M+Amshaker (mixed, caption_type=all)" >> "$SUMMARY"
echo "Tower: openvision2 w512 d30, loss=aimv2 mask=0.6, 8 GPUs, seed 1234, bf16" >> "$SUMMARY"
echo "" >> "$SUMMARY"

GPIC_N=$(ls $GPIC 2>/dev/null | wc -l)
CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
echo "Shard counts: GPIC=$GPIC_N CC12M=$CC12M_N Amshaker=$AMSH_N total=$((GPIC_N+CC12M_N+AMSH_N))" >> "$SUMMARY"
echo "" >> "$SUMMARY"

for BS in 64 128 256; do
    OUT="$BENCH_OUTROOT/bs${BS}"
    mkdir -p "$OUT"
    LOG="/tmp/bench_bs${BS}.log"
    DMON="/tmp/bench_bs${BS}_dmon.log"

    echo "===== BS=$BS START $(date '+%F %T') ====="
    echo "" >> "$SUMMARY"
    echo "--- BS=$BS (global=$((BS*8))) ---" >> "$SUMMARY"

    # Start nvidia-smi dmon in background (1s interval, 300 samples = 5 min max)
    nvidia-smi dmon -s u -c 300 > "$DMON" 2>&1 &
    DMON_PID=$!
    echo "dmon PID=$DMON_PID, logging to $DMON"

    # Also capture memory peak via query loop in background
    MEMLOG="/tmp/bench_bs${BS}_mem.log"
    (
        for i in $(seq 1 300); do
            nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader 2>/dev/null
            sleep 1
        done
    ) > "$MEMLOG" 2>&1 &
    MEM_PID=$!

    # Run training for 250 steps with log-every=10 (dense throughput data)
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
        > "$LOG" 2>&1
    rc=$?

    # Stop background monitors
    kill $DMON_PID 2>/dev/null
    kill $MEM_PID 2>/dev/null
    wait $DMON_PID 2>/dev/null
    wait $MEM_PID 2>/dev/null

    echo "BS=$BS training exit=$rc"

    # Parse training log for throughput
    echo "Training log (last 20 lines):" >> "$SUMMARY"
    tail -20 "$LOG" >> "$SUMMARY" 2>&1

    # Extract steady-state ms/iter and image/s from [step ...] lines (skip first 50 warmup steps)
    echo "" >> "$SUMMARY"
    echo "Steady-state throughput (steps 60-250, from [step] lines):" >> "$SUMMARY"
    grep '\[step ' "$LOG" | awk -F'ms/iter=' '{print $2}' | awk '{print $1}' | tail -20 >> "$SUMMARY" 2>&1
    grep '\[step ' "$LOG" | awk -F'image/s=' '{print $2}' | awk '{print $1}' | tail -20 >> "$SUMMARY" 2>&1

    # Extract [done] line
    echo "" >> "$SUMMARY"
    grep '\[done\]' "$LOG" >> "$SUMMARY" 2>&1

    # Parse dmon for GPU util stats (skip header lines, column 3 = sm util)
    echo "" >> "$SUMMARY"
    echo "GPU util from dmon (per-GPU avg of sm%):" >> "$SUMMARY"
    # dmon format: # gpu     sm    mem    enc    dec    jpg    ofa   pxld
    #              0     45%    0%     0%     0%     0%     0%     0%
    tail -n +2 "$DMON" | grep -v '^#' | awk '{sum+=$2; n++} END{if(n>0) printf "  avg_sm_util=%.1f%% (n=%d samples)\n", sum/n, n}' >> "$SUMMARY" 2>&1

    # Parse memory log for peak
    echo "" >> "$SUMMARY"
    echo "Memory peak (max across all GPUs):" >> "$SUMMARY"
    # Format: 0, 1234 MiB, 56 %
    cat "$MEMLOG" | awk -F',' '{gsub(/[^0-9]/,"",$2); if($2+0>max) max=$2} END{printf "  peak_mem=%d MiB\n", max}' >> "$SUMMARY" 2>&1

    echo "" >> "$SUMMARY"
    echo "===== BS=$BS END $(date '+%F %T') ====="
    echo ""
done

echo "" >> "$SUMMARY"
echo "===== BENCHMARK COMPLETE $(date '+%F %T') =====" >> "$SUMMARY"

echo ""
echo "===== SUMMARY ====="
cat "$SUMMARY"