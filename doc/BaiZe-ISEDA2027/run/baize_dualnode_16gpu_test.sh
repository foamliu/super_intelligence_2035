#!/bin/bash
# BaiZe-2B dual-node 16-GPU throughput test (2026-10-24, NCCL-fixed v2)
# Config: e18 identical (MBS3 + FP8 tensorwise + CUDA Graphs), DP16
# Baseline: single-node 8-GPU = 305,098 tok/s (e18, MBS3/GBS1008/FP8 TW/CG)
# NCCL fix: 4 vars from 2-rank test (GID_INDEX=3, MTU=4096, TC=106, TIMEOUT=22)
#   MASTER_ADDR=10.239.2.12 (bond0, verified), rank0=.12, rank1=.29
# Run from .29: master via SSH->.12, worker local on .29
set -uo pipefail

MASTER_IP=10.239.2.12   # TCP store on .12 (bond0, verified by 2-rank NCCL test)
WORKER_IP=10.239.2.29   # worker = local (.29, where this script runs)
MASTER_PORT=29555
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

ITERS=80; SEQ=4096; MBS=3; GBS=1008
NAME="dualnode_16gpu_e18"

# Build BLEND (16 shards, 1:1) -- same as single-node e18
BLEND=""
for i in $(seq 0 15); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"

R="/tmp/baize_dualnode_16gpu"; mkdir -p "$R"
LOG_M="$R/master.log"; LOG_W="$R/worker.log"
SUM="$R/summary.txt"; PF_M="$R/master.peakmem"; PF_W="$R/worker.peakmem"

echo "===== Dual-node 16-GPU throughput test @ $(date '+%F %T') =====" > "$SUM"
echo "Config: e18 identical (MBS3 + FP8 TW + CG), DP=16 (2 nodes x 8 GPU)" >> "$SUM"
echo "Baseline: single-node 8-GPU = 305098 tok/s (e18)" >> "$SUM"
echo "MBS=$MBS GBS=$GBS SEQ=$SEQ ITERS=$ITERS" >> "$SUM"
echo "GBS/(MBS*DP16) = $GBS/48 = $(( GBS / (MBS * 16) )) accum steps" >> "$SUM"
echo "Ideal linear = $(( 305098 * 2 )); 85% = $(( 305098 * 2 * 85 / 100 )); 70% = $(( 305098 * 2 * 70 / 100 ))" >> "$SUM"
echo "NCCL: GID_INDEX=3 MTU=4096 TC=106 TIMEOUT=22" >> "$SUM"
echo "MASTER_ADDR=$MASTER_IP (rank0 on .12), WORKER on .29 (rank1)" >> "$SUM"
echo "" >> "$SUM"

# === PRE-FLIGHT ===
echo "=== PRE-FLIGHT GPU CHECK ===" >> "$SUM"
echo "--- .12 (master, remote) ---" >> "$SUM"
ssh -o StrictHostKeyChecking=no $MASTER_IP 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
echo "--- .29 (worker, local) ---" >> "$SUM"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
echo "--- .12 stale procs ---" >> "$SUM"
ssh -o StrictHostKeyChecking=no $MASTER_IP 'pgrep -af "torchrun|pretrain_launcher" 2>/dev/null || echo none' >> "$SUM" 2>&1
echo "--- .29 stale procs ---" >> "$SUM"
pgrep -af "torchrun|pretrain_launcher" 2>/dev/null || echo none >> "$SUM" 2>&1
echo "" >> "$SUM"

# Cleanup any stale processes
pkill -f 'torchrun.*dualnode' 2>/dev/null; sleep 2
ssh -o StrictHostKeyChecking=no $MASTER_IP 'pkill -f "torchrun.*dualnode" 2>/dev/null; true'
sleep 2

# === Peak memory monitor on worker (.29, local) ===
: > "$PF_W"
( MAX=0; while :; do
    U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
    [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX=$U; echo "$MAX" > "$PF_W"; sleep 2
done ) &
MON_W=$!

# === Peak memory monitor on master (.12, remote) ===
ssh -f -o StrictHostKeyChecking=no $MASTER_IP "mkdir -p /tmp/baize_dualnode_16gpu && : > $PF_M && setsid bash -c 'MAX=0; while :; do U=\$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n \"\$U\" ] && [ \"\$U\" -gt \"\$MAX\" ] && MAX=\$U; echo \"\$MAX\" > $PF_M; sleep 2; done' </dev/null >/dev/null 2>&1 &"
sleep 3

# === Start master on .12 (node_rank=0, TCP store on .12) ===
echo "=== STARTING MASTER on $MASTER_IP @ $(date '+%T') ===" >> "$SUM"
ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 $MASTER_IP "
    ulimit -n 65536 && \
    cd $BASE && \
    export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 && \
    export NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22 && \
    export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1 && \
    $PY/torchrun --nnodes=2 --node_rank=0 --nproc_per_node=8 \
        --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
        pretrain_launcher.py \
        --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
        --tokenizer-path $BASE/data/tokenizer_eod \
        --train-data-path $BLEND \
        --train-iters $ITERS --global-batch-size $GBS --micro-batch-size $MBS --seq-length $SEQ \
        --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed \
        --fp8-recipe tensorwise --enable-cuda-graph
" > $LOG_M 2>&1 &
MASTER_SSH_PID=$!
echo "  master SSH PID=$MASTER_SSH_PID" >> "$SUM"
sleep 10

# === Start worker on .29 locally (node_rank=1) ===
echo "=== STARTING WORKER on $WORKER_IP @ $(date '+%T') ===" >> "$SUM"
cd "$BASE"
ulimit -n 65536
export NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1
timeout 1800 $PY/torchrun --nnodes=2 --node_rank=1 --nproc_per_node=8 \
    --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
    pretrain_launcher.py \
    --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
    --tokenizer-path $BASE/data/tokenizer_eod \
    --train-data-path $BLEND \
    --train-iters $ITERS --global-batch-size $GBS --micro-batch-size $MBS --seq-length $SEQ \
    --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \
    --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
    --seed 1234 --precision bf16_mixed \
    --fp8-recipe tensorwise --enable-cuda-graph > $LOG_W 2>&1
WORKER_RC=$?
echo "  worker rc=$WORKER_RC @ $(date '+%T')" >> "$SUM"

# Wait for master SSH to finish
wait $MASTER_SSH_PID 2>/dev/null
MASTER_RC=$?
echo "  master rc=$MASTER_RC @ $(date '+%T')" >> "$SUM"

# Stop memory monitors
kill $MON_W 2>/dev/null; wait $MON_W 2>/dev/null
ssh -o StrictHostKeyChecking=no $MASTER_IP 'pkill -f "nvidia-smi.*memory.used" 2>/dev/null; true'

# === RESULT PARSING ===
echo "" >> "$SUM"; echo "=== RESULT PARSING ===" >> "$SUM"
if [ "$WORKER_RC" -ne 0 ] || [ "$MASTER_RC" -ne 0 ]; then
    echo "FAIL: worker rc=$WORKER_RC master rc=$MASTER_RC" >> "$SUM"
    grep -iE "OutOfMemory|CUDA out of memory|AssertionError|RuntimeError|ValueError|Traceback|Error|Timeout|timeout" "$LOG_W" "$LOG_M" 2>/dev/null | head -15 >> "$SUM"
    echo "--- master log tail ---" >> "$SUM"; tail -30 "$LOG_M" >> "$SUM" 2>&1
    echo "--- worker log tail ---" >> "$SUM"; tail -30 "$LOG_W" >> "$SUM" 2>&1
else
    IL=$(grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {s=$(i+1); gsub(/\//,"",s); if(s+0>=30) print}}')
    MS=$(echo "$IL" | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    MC=$(echo "$MS" | grep -c .)
    TF=$(echo "$IL" | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
    LG=$(echo "$IL" | grep -oP 'lm loss: \K[0-9.]+')
    GN=$(echo "$IL" | grep -oP 'grad norm: \K[0-9.]+')
    TPS=$(( GBS * SEQ ))
    if [ "$MC" -gt 0 ]; then
        MM=$(echo "$MS" | sort -n | awk '{a[NR]=$1} END{if(NR%2) print a[(NR+1)/2]; else printf "%.1f",(a[NR/2]+a[NR/2+1])/2}')
        MT=$(awk -v t="$TPS" -v m="$MM" 'BEGIN{printf "%.0f",t/(m/1000)}')
        AT=$(echo "$TF" | awk '{s+=$1;n++} END{printf "%.1f",s/n}')
        AL=$(echo "$LG" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
        AG=$(echo "$GN" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
        NC=$(echo "$IL" | grep -oP 'number of nan iterations:\s+\K[0-9]+' | awk '{s+=$1} END{print s+0}')
        PEAK_M=$(ssh -o StrictHostKeyChecking=no $MASTER_IP "cat $PF_M 2>/dev/null")
        PEAK_W=$(cat "$PF_W" 2>/dev/null)
        PER_GPU=$(( MT / 16 ))
        EFF=$(awk -v t="$MT" -v b="305098" 'BEGIN{printf "%.1f",t/(b*2)*100}')
        echo "  pts=$MC med_ms=$MM med_toks=$MT tflop=$AT loss=$AL gnorm=$AG nan=$NC" >> "$SUM"
        echo "  peak_mem_master(.12)=${PEAK_M}MiB peak_mem_worker(.29)=${PEAK_W}MiB" >> "$SUM"
        echo "  per_gpu_tok/s=$PER_GPU scaling_eff=${EFF}%" >> "$SUM"
        echo "" >> "$SUM"; echo "===== SUMMARY TABLE =====" >> "$SUM"
        echo "| Metric | Value |" >> "$SUM"
        echo "|--------|-------|" >> "$SUM"
        echo "| Config | MBS3+GBS1008+FP8 TW+CG, DP16 (2x8 H100) |" >> "$SUM"
        echo "| Baseline (8 GPU) | 305098 tok/s |" >> "$SUM"
        echo "| 16 GPU throughput | $MT tok/s |" >> "$SUM"
        echo "| Scaling efficiency | ${EFF}% |" >> "$SUM"
        echo "| Per-GPU throughput | $PER_GPU tok/s |" >> "$SUM"
        echo "| Median step time | $MM ms |" >> "$SUM"
        echo "| GPU utilization | $AT TFLOP/s/GPU |" >> "$SUM"
        echo "| Peak VRAM master (.12) | ${PEAK_M} MiB |" >> "$SUM"
        echo "| Peak VRAM worker (.29) | ${PEAK_W} MiB |" >> "$SUM"
        echo "| Loss (step 30-80) | $AL |" >> "$SUM"
        echo "| Grad norm | $AG |" >> "$SUM"
        echo "| NaN count | $NC |" >> "$SUM"
    else
        echo "PARSE_FAIL: no iteration logs found" >> "$SUM"
        grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | head -5 >> "$SUM"
    fi
fi
echo "" >> "$SUM"; echo "=== NCCL TRANSPORT CHECK ===" >> "$SUM"
echo "--- NCCL NET/IB/Init COMPLETE/Connected ---" >> "$SUM"
grep -iE 'NCCL INFO.*NET|NCCL INFO.*IB|NCCL INFO.*SOCK|NCCL INFO.*Using|busbw|Algo|Proto|Init COMPLETE|Connected all' "$LOG_W" "$LOG_M" 2>/dev/null | head -30 >> "$SUM"
echo "--- busbw (last 10) ---" >> "$SUM"
grep -i 'busbw' "$LOG_W" "$LOG_M" 2>/dev/null | tail -10 >> "$SUM"
echo "--- worker NCCL ---" >> "$SUM"
grep -iE 'NCCL INFO.*NET|NCCL INFO.*IB|NCCL INFO.*SOCK|NCCL INFO.*Using|Init COMPLETE' "$LOG_W" | head -10 >> "$SUM"
echo "" >> "$SUM"; echo "=== POST-FLIGHT GPU CHECK ===" >> "$SUM"
echo "--- .12 (master, remote) ---" >> "$SUM"
ssh -o StrictHostKeyChecking=no $MASTER_IP 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
echo "--- .29 (worker, local) ---" >> "$SUM"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
echo "" >> "$SUM"
echo "===== TEST COMPLETE @ $(date '+%F %T') =====" >> "$SUM"
echo "SUM=$SUM LOG_M=$LOG_M LOG_W=$LOG_W R=$R"
