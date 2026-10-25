#!/bin/bash
# BaiZe-2B Context-Parallel smoke (2026-10-26, 运维令 23:0x §3 "CP=2/4可行性")
# 目的: seq32768 在 CP=1 下 OOM (cfg5/cfg6), 测 CP=2 能否启用 32K 并保持满速.
# 配方: DP16/TP1/PP1 + FP8 tensorwise + 真数据 + graph OFF (rev3 真因=CUDA Graph 顶格停滞).
# 单变量: --context-parallel (1=对照OOM / 2=CP启用).
# rev3 基线: cfg0ang seq4096/mbs4/CP1/graph-off tok/mb=16384 = 561,126 tok/s, 75,517 MiB.
# 预期: CP=2 @ seq32768 -> per-GPU tok/mb = mbs*seq/CP = 1*32768/2 = 16384 (=悬崖边界, graph-off 应满速).
set -o pipefail

MASTER_IP=10.239.2.12
WORKER_IP=10.239.2.29
MASTER_PORT=29562
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

ITERS=20
ROOT=/tmp/baize_rc_cp_smoke
mkdir -p "$ROOT"
ALL="$ROOT/ALL_RESULTS.txt"
echo "# BaiZe-2B Context-Parallel smoke @ $(date '+%F %T')" > "$ALL"
echo "# Recipe: DP16/TP1/PP1 + FP8 tensorwise + graph OFF + real data" >> "$ALL"
echo "# rev3 baseline: cfg0ang seq4096/mbs4/CP1/graph-off tok/mb=16384 = 561,126 tok/s, 75,517 MiB" >> "$ALL"
echo "# cols: label seq mbs gbs cp accum tok_per_mb_per_gpu tok_per_step status tok_per_s step_per_s med_ms per_gpu_tok_s peak_mem_MiB loss gnorm nan" >> "$ALL"

BLEND=""
for i in $(seq 0 15); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"

CONFIGS=(
  "cp1_seq32k 32768 1 16 1"
  "cp2_seq32k 32768 1 16 2"
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
  pkill -f 'torchrun.*cp_smoke_rc' 2>/dev/null; true
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'pkill -f "torchrun.*cp_smoke_rc" 2>/dev/null; true' 2>/dev/null
  for k in 1 2 3 4 5 6 7 8 9 10; do
    if gpus_free local && gpus_free "$MASTER_IP"; then return 0; fi
    sleep 5
  done
  return 1
}

run_cfg() {
  local label="$1" seq="$2" mbs="$3" gbs="$4" cp="$5"
  local dp=$(( 16 / cp ))
  local accum=$(( gbs / (mbs * dp) ))
  local tmb_pg=$(( mbs * seq / cp ))
  local tps=$(( gbs * seq ))
  local D="$ROOT/$label"; mkdir -p "$D"
  local LOG_M="$D/master.log" LOG_W="$D/worker.log"
  local SUM="$D/summary.txt" PF_M="$D/master.peakmem" PF_W="$D/worker.peakmem"
  local NAME="cp_smoke_rc_${label}"

  echo "===== $label (seq=$seq mbs=$mbs gbs=$gbs CP=$cp DP=$dp accum=$accum tok/mb/gpu=$tmb_pg tps=$tps) @ $(date '+%F %T') =====" > "$SUM"
  echo "tok/mb_per_gpu=$tmb_pg tok/step=$tps CP=$cp DP=$dp" >> "$SUM"
  echo "--- preflight .12 ---" >> "$SUM"
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
  echo "--- preflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  if ! gpus_free local || ! gpus_free "$MASTER_IP"; then
    echo "PREFLIGHT_FAIL: GPUs not free" >> "$SUM"
    echo "$label $seq $mbs $gbs $cp $accum $tmb_pg $tps PREFLIGHT_FAIL - - - - - - - -" >> "$ALL"
    return 1
  fi

  : > "$PF_W"
  ( MAX=0; while :; do
      U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
      [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX="$U" && echo "$MAX" > "$PF_W"
      sleep 2
  done ) &  MON_W=$!
  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" "
    PF='$PF_M'; : > \"\$PF\"
    ( MAX=0; while :; do
        U=\$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n \"\$U\" ] && [ \"\$U\" -gt \"\$MAX\" ] && MAX=\"\$U\" && echo \"\$MAX\" > \"\$PF\"
        sleep 2
    done ) &
  " 2>/dev/null

  ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$MASTER_IP" "
    cd '$BASE'; ulimit -n 65536
    export $NCCL_ENV; export $PYTORCH_ENV
    timeout 1800 $PY/torchrun --nnodes=2 --node_rank=0 --nproc_per_node=8 \
        --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
        pretrain_launcher.py --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
        --tokenizer-path $BASE/data/tokenizer_eod --train-data-path '$BLEND' \
        --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
        --tensor-parallel 1 --context-parallel $cp --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise > '$LOG_M' 2>&1
  " > /dev/null 2>&1 &
  MASTER_SSH_PID=$!

  echo "--- launch worker @ $(date '+%T') ---" >> "$SUM"
  cd "$BASE"; ulimit -n 65536
  export $NCCL_ENV; export $PYTORCH_ENV
  timeout 1800 $PY/torchrun --nnodes=2 --node_rank=1 --nproc_per_node=8 \
      --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
      pretrain_launcher.py --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
      --tokenizer-path $BASE/data/tokenizer_eod --train-data-path "$BLEND" \
      --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
      --tensor-parallel 1 --context-parallel $cp --eval-interval 99999 --eval-iters 0 --save-interval 0 \
      --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
      --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise > "$LOG_W" 2>&1
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
    grep -iE 'OutOfMemory|CUDA out of memory|RuntimeError|Traceback|Error|Timeout|context.parallel|NotImplemented|assert|cp_size|ring|not support' "$LOG_W" "$LOG_M" 2>/dev/null | head -15 >> "$SUM"
    echo "--- worker tail ---" >> "$SUM"; tail -25 "$LOG_W" >> "$SUM" 2>&1
    local status=$([ "$oom" -gt 0 ] && echo "OOM" || echo "FAIL")
    echo "$label $seq $mbs $gbs $cp $accum $tmb_pg $tps $status - - - - $PEAK - - -" >> "$ALL"
  else
    local IL=$(grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {s=$(i+1); gsub(/\//,"",s); if(s+0>=5) print}}')
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
      echo "$label $seq $mbs $gbs $cp $accum $tmb_pg $tps OK $MT $SPS $MM $PER $PEAK $AL $AG $NC" >> "$ALL"
    else
      echo "PARSE_FAIL: no iteration logs (peak=${PEAK}MiB)" >> "$SUM"
      grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | head -5 >> "$SUM"
      echo "$label $seq $mbs $gbs $cp $accum $tmb_pg $tps PARSE_FAIL - - - - $PEAK - - -" >> "$ALL"
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
echo "# CP SMOKE COMPLETE @ $(date '+%F %T')" >> "$ALL"
echo "CP SMOKE COMPLETE"
