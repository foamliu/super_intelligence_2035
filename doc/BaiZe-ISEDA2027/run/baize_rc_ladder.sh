#!/bin/bash
# BaiZe-2B tok/microbatch cliff root-cause LADDER (operator order 2026-10-25 23:0x)
# Purpose: disambiguate "tok/mb cliff @ 16384 + mem顶格81GB" (order framing) vs
#          "small-batch geometry GPU starvation" (#782 framing).
# Recipe FROZEN: DP16/TP1/PP1 + FP8 tensorwise + CUDA Graphs + real data (e18 identical, 2-node .12+.29).
# Single variable = tok_per_mb (= mbs*seq); seq/mbs/gbs/accum vary per cell per the ladder.
# Baseline ref: seq4096/mbs3/gbs1008/accum21 tok/mb=12288 = 606,449 tok/s.
# Prior context rows (baseline/cfg0a/cfg0b=E1/cfg1-4) already seeded in the TSV.
# Output: run/pretrain_rc_ladder_20261026.tsv (append); logs /tmp/baize_rc_ladder/<label>/
set -o pipefail

MASTER_IP=10.239.2.12
WORKER_IP=10.239.2.29
MASTER_PORT=29561
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

REPO=/nas_train/app.e0031982/code/super_intelligence_2035
TSV="$REPO/doc/BaiZe-ISEDA2027/run/pretrain_rc_ladder_20261026.tsv"
ITERS=80
ROOT=/tmp/baize_rc_ladder
mkdir -p "$ROOT"

BLEND=""
for i in $(seq 0 15); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"

# Ladder cells: label step seq mbs gbs   (accum=gbs/(mbs*16); tok/mb=mbs*seq; tok/step=gbs*seq)
# E2: tok/mb=8192 (below cliff), tok/step=2.1M (=cfg0a) -> if FAST => tok/mb is driver (8K满速)
# E3: tok/mb=12288 (=baseline), seq=12288 -> confirms 12288 fast regardless of seq
# E4: tok/mb=12288, seq=6144, mbs=2 -> third 12288 cross-validation
# E5a: tok/mb=16384 (above cliff), seq=2048, mbs=8 -> if SLOW => tok/mb pure effect; if FAST => seq/mem matters
# E5b: tok/mb=16384, seq=1024, mbs=16 -> extreme small seq, big mbs
CONFIGS=(
  "E2 E2 8192 1 256"
  "E3 E3 12288 1 256"
  "E4 E4 6144 2 512"
  "E5a E5a 2048 8 1024"
  "E5b E5b 1024 16 2048"
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
  pkill -f 'torchrun.*rc_ladder' 2>/dev/null; true
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'pkill -f "torchrun.*rc_ladder" 2>/dev/null; true' 2>/dev/null
  for k in 1 2 3 4 5 6 7 8 9 10; do
    if gpus_free local && gpus_free "$MASTER_IP"; then return 0; fi
    sleep 5
  done
  return 1
}
run_cfg() {
  local label="$1" step="$2" seq="$3" mbs="$4" gbs="$5"
  local accum=$(( gbs / (mbs * 16) ))
  local tokmb=$(( mbs * seq ))
  local tps=$(( gbs * seq ))
  local D="$ROOT/$label"; mkdir -p "$D"
  local LOG_M="$D/master.log" LOG_W="$D/worker.log"
  local SUM="$D/summary.txt" PF_M="$D/master.peakmem" PF_W="$D/worker.peakmem"
  local NAME="rc_ladder_${label}"

  echo "===== $label ($step seq=$seq mbs=$mbs gbs=$gbs accum=$accum tokmb=$tokmb tps=$tps) @ $(date '+%F %T') =====" > "$SUM"
  echo "tok/mb=$tokmb tok/step=$tps" >> "$SUM"
  echo "--- preflight .12 ---" >> "$SUM"
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
  echo "--- preflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  if ! gpus_free local || ! gpus_free "$MASTER_IP"; then
    echo "PREFLIGHT_FAIL: GPUs not free, skipping $label" >> "$SUM"
    echo "$step $label $seq $mbs $gbs $accum $tokmb $tps PREFLIGHT_FAIL - - - - - - - -" >> "$TSV"
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
    echo "$step $label $seq $mbs $gbs $accum $tokmb $tps $status - - - - $PEAK - - -" >> "$TSV"
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
      echo "$step $label $seq $mbs $gbs $accum $tokmb $tps OK $MT $SPS $MM $PER $PEAK $AL $AG $NC" >> "$TSV"
    else
      echo "PARSE_FAIL: no iteration logs (peak=${PEAK}MiB)" >> "$SUM"
      grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | head -5 >> "$SUM"
      echo "$step $label $seq $mbs $gbs $accum $tokmb $tps PARSE_FAIL - - - - $PEAK - - -" >> "$TSV"
    fi
  fi
  echo "--- postflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  # NOTE: TSV committed by the agent at wake-up (avoid git-lock contention with concurrent commits)
  release_gpus
  echo "===== $label DONE @ $(date '+%F %T') =====" >> "$SUM"
  return 0
}

for cfg in "${CONFIGS[@]}"; do
  set -- $cfg
  run_cfg "$1" "$2" "$3" "$4" "$5"
done

echo "" >> "$TSV"
echo "# LADDER COMPLETE @ $(date '+%F %T')" >> "$TSV"
echo "LADDER COMPLETE"


