#!/bin/bash
# BaiZe-2B seq-length x tok/step throughput grid (2026-10-25, 用户直令)
# 目的: 每步 token 数固定 (2M=S1 / 4M=S2) 下, 测增大 seq 对 16 卡训练吞吐的影响.
# 配方冻结: DP16/TP1/PP1 + FP8 tensorwise + CUDA Graphs + 真数据 (与双机 e18 同口径).
# 单变量: seq (同组 3 个 seq 共用同一批 16 个 p5b_l3 shard, 仅运行时 --seq-length 切块不同).
# 基线参考: seq=4096 / 4,128,768 tok/step / DP16 e18 = 606,449 tok/s (/tmp/baize_dualnode_16gpu/).
# 注: launcher 无 --mamba-ssm-dtype flag; Mamba2 SSM dtype 由 mamba2_hybrid_2b.recipe 内部管理
#     (与 606K 基线一致), 故本网格配方与 e18 字节级一致, 仅 seq/MBS/GBS 变化.
# 运行: 从 .29 启动; master 经 SSH->.12, worker 本地 .29. 6 格串行, 每格跑完释放 16 卡.
set -o pipefail

MASTER_IP=10.239.2.12
WORKER_IP=10.239.2.29
MASTER_PORT=29555
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

ITERS=80
ROOT=/tmp/baize_seqlen_grid
mkdir -p "$ROOT"
ALL="$ROOT/ALL_RESULTS.txt"
echo "# BaiZe-2B seq x tok/step throughput grid @ $(date '+%F %T')" > "$ALL"
echo "# Recipe: DP16/TP1/PP1 + FP8 tensorwise + CUDA Graphs + real data (e18 identical)" >> "$ALL"
echo "# Baseline ref: seq=4096 / 4,128,768 tok/step / DP16 e18 = 606,449 tok/s" >> "$ALL"
echo "# Single variable = seq; same 16 p5b_l3 shards for all 6 configs" >> "$ALL"
echo "# cols: label group seq mbs gbs accum tok_per_step status tok/s step/s med_ms per_gpu_tok/s peak_mem_MiB loss gnorm nan" >> "$ALL"

BLEND=""
for i in $(seq 0 15); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"

# Configs: label group seq mbs gbs  (accum=gbs/(mbs*16); tok/step=gbs*seq)
CONFIGS=(
  "cfg1 S1 8192 2 256"
  "cfg2 S2 8192 2 512"
  "cfg3 S1 16384 1 128"
  "cfg4 S2 16384 1 256"
  "cfg5 S1 32768 1 64"
  "cfg6 S2 32768 1 128"
)

NCCL_ENV="NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22"
PYTORCH_ENV="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1"

gpus_free() {  # arg: local|ip ; 0 if all 8 GPUs < 2000 MiB used
  local host="$1" u
  if [ "$host" = "local" ]; then
    u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
  else
    u=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$host" 'nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1')
  fi
  [ -n "$u" ] && [ "$u" -lt 2000 ]
}

release_gpus() {
  pkill -f 'torchrun.*seqlen_grid' 2>/dev/null; true
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'pkill -f "torchrun.*seqlen_grid" 2>/dev/null; true' 2>/dev/null
  for k in 1 2 3 4 5 6 7 8 9 10; do
    if gpus_free local && gpus_free "$MASTER_IP"; then return 0; fi
    sleep 5
  done
  return 1
}

run_cfg() {
  local label="$1" group="$2" seq="$3" mbs="$4" gbs="$5"
  local accum=$(( gbs / (mbs * 16) ))
  local tps=$(( gbs * seq ))
  local D="$ROOT/$label"; mkdir -p "$D"
  local LOG_M="$D/master.log" LOG_W="$D/worker.log"
  local SUM="$D/summary.txt" PF_M="$D/master.peakmem" PF_W="$D/worker.peakmem"
  local NAME="seqlen_grid_${label}"

  echo "===== $label ($group seq=$seq mbs=$mbs gbs=$gbs accum=$accum tps=$tps) @ $(date '+%F %T') =====" > "$SUM"
  echo "tok/step=$tps (expected: $([ "$group" = S1 ] && echo 2097152 || echo 4194304))" >> "$SUM"
  echo "--- preflight .12 ---" >> "$SUM"
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
  echo "--- preflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  if ! gpus_free local || ! gpus_free "$MASTER_IP"; then
    echo "PREFLIGHT_FAIL: GPUs not free, skipping $label" >> "$SUM"
    echo "$label $group $seq $mbs $gbs $accum $tps PREFLIGHT_FAIL - - - - - - -" >> "$ALL"
    return 1
  fi

  : > "$PF_W"
  ( MAX=0; while :; do
      U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
      [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX=$U; echo "$MAX" > "$PF_W"; sleep 2
  done ) & MON_W=$!
  ssh -f -o StrictHostKeyChecking=no "$MASTER_IP" "mkdir -p $D && : > $PF_M && setsid bash -c 'MAX=0; while :; do U=\$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n \"\$U\" ] && [ \"\$U\" -gt \"\$MAX\" ] && MAX=\$U; echo \"\$MAX\" > $PF_M; sleep 2; done' </dev/null >/dev/null 2>&1 &" 2>/dev/null
  sleep 3

  echo "=== START MASTER .12 @ $(date '+%T') ===" >> "$SUM"
  ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 "$MASTER_IP" "
    ulimit -n 65536 && cd $BASE && \
    export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 && \
    export $NCCL_ENV && export $PYTORCH_ENV && \
    $PY/torchrun --nnodes=2 --node_rank=0 --nproc_per_node=8 \
        --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
        pretrain_launcher.py --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
        --tokenizer-path $BASE/data/tokenizer_eod --train-data-path $BLEND \
        --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
        --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise --enable-cuda-graph
  " > "$LOG_M" 2>&1 &
  MASTER_SSH_PID=$!
  echo "  master SSH PID=$MASTER_SSH_PID" >> "$SUM"
  sleep 10

  echo "=== START WORKER .29 @ $(date '+%T') ===" >> "$SUM"
  cd "$BASE"; ulimit -n 65536
  export $NCCL_ENV; export $PYTORCH_ENV
  timeout 3600 $PY/torchrun --nnodes=2 --node_rank=1 --nproc_per_node=8 \
      --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
      pretrain_launcher.py --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
      --tokenizer-path $BASE/data/tokenizer_eod --train-data-path $BLEND \
      --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
      --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \
      --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
      --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise --enable-cuda-graph > "$LOG_W" 2>&1
  WORKER_RC=$?
  wait $MASTER_SSH_PID 2>/dev/null; MASTER_RC=$?
  echo "  worker rc=$WORKER_RC master rc=$MASTER_RC @ $(date '+%T')" >> "$SUM"

  kill $MON_W 2>/dev/null; wait $MON_W 2>/dev/null
  ssh -o StrictHostKeyChecking=no "$MASTER_IP" 'pkill -f "nvidia-smi.*memory.used" 2>/dev/null; true' 2>/dev/null
  PEAK_M=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" "cat $PF_M 2>/dev/null" 2>/dev/null | tail -1)
  PEAK_W=$(tail -1 "$PF_W" 2>/dev/null)
  PEAK_M=${PEAK_M:-0}; PEAK_W=${PEAK_W:-0}
  local PEAK=$( [ "$PEAK_M" -gt "$PEAK_W" ] && echo "$PEAK_M" || echo "$PEAK_W" )

  if [ "$WORKER_RC" -ne 0 ] || [ "$MASTER_RC" -ne 0 ]; then
    local oom=$(grep -ciE 'OutOfMemory|CUDA out of memory|out of memory' "$LOG_W" "$LOG_M" 2>/dev/null | awk '{s+=$1}END{print s+0}')
    echo "FAIL: worker rc=$WORKER_RC master rc=$MASTER_RC oom_lines=$oom peak=${PEAK}MiB" >> "$SUM"
    grep -iE 'OutOfMemory|CUDA out of memory|RuntimeError|Traceback|Error|Timeout' "$LOG_W" "$LOG_M" 2>/dev/null | head -10 >> "$SUM"
    echo "--- worker tail ---" >> "$SUM"; tail -15 "$LOG_W" >> "$SUM" 2>&1
    local status=$([ "$oom" -gt 0 ] && echo "OOM" || echo "FAIL")
    echo "$label $group $seq $mbs $gbs $accum $tps $status - - - - $PEAK - - -" >> "$ALL"
  else
    local IL=$(grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {s=$(i+1); gsub(/\//,"",s); if(s+0>=30) print}}')
    local MS=$(echo "$IL" | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    local MC=$(echo "$MS" | grep -c .)
    local LG=$(echo "$IL" | grep -oP 'lm loss: \K[0-9.]+')
    local GN=$(echo "$IL" | grep -oP 'grad norm: \K[0-9.]+')
    if [ "$MC" -gt 0 ]; then
      local MM=$(echo "$MS" | sort -n | awk '{a[NR]=$1} END{if(NR%2) print a[(NR+1)/2]; else printf "%.1f",(a[NR/2]+a[NR/2+1])/2}')
      local MT=$(awk -v t="$tps" -v m="$MM" 'BEGIN{printf "%.0f",t/(m/1000)}')
      local SPS=$(awk -v m="$MM" 'BEGIN{printf "%.3f",1000/m}')
      local PER=$(( MT / 16 ))
      local AL=$(echo "$LG" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
      local AG=$(echo "$GN" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
      local NC=$(echo "$IL" | grep -oP 'number of nan iterations:\s+\K[0-9]+' | awk '{s+=$1} END{print s+0}')
      echo "  pts=$MC med_ms=$MM tok/s=$MT step/s=$SPS per_gpu=$PER loss=$AL gnorm=$AG nan=$NC peak=${PEAK}MiB" >> "$SUM"
      echo "$label $group $seq $mbs $gbs $accum $tps OK $MT $SPS $MM $PER $PEAK $AL $AG $NC" >> "$ALL"
    else
      echo "PARSE_FAIL: no iteration logs (peak=${PEAK}MiB)" >> "$SUM"
      grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | head -5 >> "$SUM"
      echo "$label $group $seq $mbs $gbs $accum $tps PARSE_FAIL - - - - $PEAK - - -" >> "$ALL"
    fi
  fi
  echo "--- postflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  release_gpus
  echo "===== $label DONE @ $(date '+%F %T') =====" >> "$SUM"
  return 0
}

for cfg in "${CONFIGS[@]}"; do
  set -- $cfg
  run_cfg "$1" "$2" "$3" "$4" "$5"
done

echo "" >> "$ALL"
echo "# GRID COMPLETE @ $(date '+%F %T')" >> "$ALL"
echo "GRID COMPLETE"
