#!/bin/bash
# BaiZe-2B recompute retest (2026-10-26, 运维令 23:0x 配方变更组)
# 目的: tok/mb=16384 (cfg0a: seq4096/mbs4) 慢+顶格81GB, 测 --recompute-num-layers 能否降显存回满速.
# 配方冻结: DP16/TP1/PP1 + FP8 tensorwise + CUDA Graphs + 真数据 (与 ladder 同口径).
# 单变量: recompute_num_layers (0=基线 cfg0a / 28=半 / 56=全 56层).
# 基线对照: cfg0a (无recompute) = 121,032 tok/s, 81,087 MiB, 14.7% MFU (TSV).
set -o pipefail

MASTER_IP=10.239.2.12
WORKER_IP=10.239.2.29
MASTER_PORT=29561
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

ITERS=80
ROOT=/tmp/baize_rc_recompute
mkdir -p "$ROOT"
ALL="$ROOT/ALL_RESULTS.txt"
echo "# BaiZe-2B recompute retest @ $(date '+%F %T')" > "$ALL"
echo "# Recipe: DP16/TP1/PP1 + FP8 tensorwise + CUDA Graphs + real data (ladder cfg0a identical)" >> "$ALL"
echo "# Baseline ref: cfg0a (no recompute) seq4096/mbs4/gbs512/accum8 tok/mb=16384 = 121,032 tok/s, 81,087 MiB" >> "$ALL"
echo "# cols: label seq mbs gbs accum rc tok_per_mb tok_per_step status tok_per_s step_per_s med_ms per_gpu_tok_s peak_mem_MiB loss gnorm nan" >> "$ALL"

BLEND=""
for i in $(seq 0 15); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"

# NOTE: full-uniform recompute asserts "only supported with full iteration CUDA graph",
# but Mamba2 recipe uses local cuda-graph mode (no CLI to switch). => drop --enable-cuda-graph
# entirely for this retest. Two no-graph configs isolate the recompute effect on memory:
#   cfg0ang = rc=0  (no graph, no recompute)  -> control (isolates cuda-graph removal)
#   rc56ng  = rc=56 (no graph, full recompute) -> test    (recompute effect vs control)
CONFIGS=(
  "cfg0ang 4096 4 512 0"
  "rc56ng 4096 4 512 56"
)

NCCL_ENV="NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22"
PYTORCH_ENV="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1"

gpus_free() {
  local host="$1" u
  if [ "$host" = "local" ]; then
    u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
  else
    u=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$host" 'nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1')
  fi
  [ -n "$u" ] && [ "$u" -lt 2000 ]
}

release_gpus() {
  pkill -f 'torchrun.*recompute_rc' 2>/dev/null; true
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'pkill -f "torchrun.*recompute_rc" 2>/dev/null; true' 2>/dev/null
  for k in 1 2 3 4 5 6 7 8 9 10; do
    if gpus_free local && gpus_free "$MASTER_IP"; then return 0; fi
    sleep 5
  done
  return 1
}

run_cfg() {
  local label="$1" seq="$2" mbs="$3" gbs="$4" rc="$5"
  local accum=$(( gbs / (mbs * 16) ))
  local tmb=$(( mbs * seq ))
  local tps=$(( gbs * seq ))
  local D="$ROOT/$label"; mkdir -p "$D"
  local LOG_M="$D/master.log" LOG_W="$D/worker.log"
  local SUM="$D/summary.txt" PF_M="$D/master.peakmem" PF_W="$D/worker.peakmem"
  local NAME="recompute_rc_${label}"
  local RCARG=""
  [ "$rc" -gt 0 ] && RCARG="--recompute-num-layers $rc"

  echo "===== $label (seq=$seq mbs=$mbs gbs=$gbs accum=$accum rc=$rc tok/mb=$tmb tps=$tps) @ $(date '+%F %T') =====" > "$SUM"
  echo "tok/mb=$tmb tok/step=$tps recompute_num_layers=$rc" >> "$SUM"
  echo "--- preflight .12 ---" >> "$SUM"
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
  echo "--- preflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  if ! gpus_free local || ! gpus_free "$MASTER_IP"; then
    echo "PREFLIGHT_FAIL: GPUs not free" >> "$SUM"
    echo "$label $seq $mbs $gbs $accum $rc $tmb $tps PREFLIGHT_FAIL - - - - - - - -" >> "$ALL"
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
        --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise $RCARG
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
      --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise $RCARG > "$LOG_W" 2>&1
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
    grep -iE 'OutOfMemory|CUDA out of memory|RuntimeError|Traceback|Error|Timeout|recompute|not support|assert|NotImplemented' "$LOG_W" "$LOG_M" 2>/dev/null | head -15 >> "$SUM"
    echo "--- worker tail ---" >> "$SUM"; tail -20 "$LOG_W" >> "$SUM" 2>&1
    local status=$([ "$oom" -gt 0 ] && echo "OOM" || echo "FAIL")
    echo "$label $seq $mbs $gbs $accum $rc $tmb $tps $status - - - - $PEAK - - -" >> "$ALL"
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
      echo "$label $seq $mbs $gbs $accum $rc $tmb $tps OK $MT $SPS $MM $PER $PEAK $AL $AG $NC" >> "$ALL"
    else
      echo "PARSE_FAIL: no iteration logs (peak=${PEAK}MiB)" >> "$SUM"
      grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | head -5 >> "$SUM"
      echo "$label $seq $mbs $gbs $accum $rc $tmb $tps PARSE_FAIL - - - - $PEAK - - -" >> "$ALL"
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
echo "# RECOMPUTE RETEST COMPLETE @ $(date '+%F %T')" >> "$ALL"
echo "RECOMPUTE RETEST COMPLETE"
