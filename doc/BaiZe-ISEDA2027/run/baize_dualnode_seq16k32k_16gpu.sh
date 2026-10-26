#!/bin/bash
# BaiZe-2B dual-node 16-GPU seq16K/32K throughput (2026-10-26, 运维令 11:1x)
# 真实双机 16 卡 (2x8 H100) 实测 seq=16384 / 32768, graph OFF (rev3 真因=CUDA Graph 顶格停滞).
# 节点: master=.12 (rank0, TCP store on .12 bond0), worker=.29 (rank1, local). 从 .29 启动.
# 前提: .12+.29 是本集群唯一可 SSH 互达的 2 节点组合 (.10/.11/.13/.20 等均拒 key);
#       vision(.12) 当前 WAITING=1 空闲未训练(等用户裁定), 使用其空闲 GPU 不构成"抢".
#       每配置前后核验 .12 空闲; 若 .12 非空闲(vision 启动?) -> SKIP 该配置 (铁律: 不抢 vision).
# FA3 CP patch (te_cp_flash_attn3_patch.diff) 已应用于共享 NFS 的 TE site-packages,
#   .12/.29 经同一 /nas_train 挂载可见 (PATCH_HITS=14), 32K CP=2 两端均生效.
# 配方: DP=16/cp (TP1/PP1), FP8 tensorwise, graph OFF, 真数据 16 shard.
# #791 8 卡基线: 16K(CP1,goff)=300,133 tok/s per-GPU 37,516; 32K(CP2)=183,394 per-GPU 22,924.
# 8K 16 卡基线(#770): 606,300 tok/s = 99.4% 线性 -> 16K 目标 >=600K.
set -uo pipefail

MASTER_IP=10.239.2.12   # TCP store on .12 (bond0, verified by 2-rank NCCL test #770)
WORKER_IP=10.239.2.29   # worker = local (.29, where this script runs)
MASTER_PORT=29557
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

ITERS=40

# Build BLEND (16 shards, 1:1)
BLEND=""
for i in $(seq 0 15); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"

R="/tmp/baize_dualnode_seq16k32k"; mkdir -p "$R"
ALL="$R/ALL_RESULTS.txt"
echo "# BaiZe-2B dual-node 16-GPU seq16K/32K @ $(date '+%F %T')" > "$ALL"
echo "# nodes: master=.12 (rank0) worker=.29 (rank1), graph OFF, FP8 tensorwise, 16 shards" >> "$ALL"
echo "# #791 8卡基线: 16K(CP1,goff)=300,133 per-GPU 37,516 peak76,795MiB; 32K(CP2)=183,394 per-GPU 22,924 peak77,619MiB" >> "$ALL"
echo "# 8K 16卡基线(#770)=606,300 tok/s=99.4%线性; 16K目标>=600K" >> "$ALL"
echo "# cols: label seq mbs gbs cp dp accum tok_per_mb_per_gpu tok_per_step status tok_per_s step_per_s med_ms per_gpu_tok_s peakM_MiB peakW_MiB loss gnorm nan" >> "$ALL"

NCCL_ENV="NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22"
PYTORCH_ENV="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1"

gpus_free_local()  { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n "$u" ] && [ "$u" -lt 2000 ]; }
gpus_free_remote() { local u; u=$(timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP 'nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1' 2>/dev/null); [ -n "$u" ] && [ "$u" -lt 2000 ]; }

# configs: label seq mbs gbs cp
CONFIGS=(
  "e1_16k_cp1 16384 1 256 1"
  "e2_16k_cp2 16384 1 128 2"
  "e3_32k_cp2 32768 1 128 2"
)

run_cfg() {
  local label="$1" seq="$2" mbs="$3" gbs="$4" cp="$5"
  local dp=$(( 16 / cp ))
  local accum=$(( gbs / (mbs * dp) ))
  local tmb_pg=$(( mbs * seq / cp ))
  local tps=$(( gbs * seq ))
  local D="$R/$label"; mkdir -p "$D"
  local LOG_M="$D/master.log" LOG_W="$D/worker.log" SUM="$D/summary.txt"
  local PF_M="/tmp/baize_dn_peak_m_$label" PF_W="$D/worker.peakmem"
  local NAME="dn16g_${label}"
  echo "===== $label (seq=$seq mbs=$mbs gbs=$gbs CP=$cp DP=$dp accum=$accum tok/mb/gpu=$tmb_pg tps=$tps) @ $(date '+%F %T') =====" > "$SUM"
  echo "graph=OFF FP8=tensorwise nodes=.12(master)+.29(worker)" >> "$SUM"
  echo "--- preflight .12 (master, remote) ---" >> "$SUM"
  timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
  echo "--- preflight .29 (worker, local) ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1

  # SAFETY GATE: 不抢 vision(.12) -- 若 .12 非空闲则 SKIP
  if ! gpus_free_remote; then
    echo "SKIP: .12 not idle (vision active?) -> respect 不抢vision, skip $label" >> "$SUM"
    echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps SKIP_DOT12_BUSY - - - - - - - - - -" >> "$ALL"
    return 1
  fi
  if ! gpus_free_local; then
    echo "SKIP: .29 not idle" >> "$SUM"
    echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps SKIP_DOT29_BUSY - - - - - - - - - -" >> "$ALL"
    return 1
  fi

  pkill -f "torchrun.*$NAME" 2>/dev/null; true
  timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP "pkill -f 'torchrun.*$NAME' 2>/dev/null; true"
  sleep 2

  : > "$PF_W"
  ( MAX=0; while :; do U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX=$U && echo "$MAX" > "$PF_W"; sleep 2; done ) & MON_W=$!
  timeout 15 ssh -f -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP "rm -f $PF_M; : > $PF_M; setsid bash -c 'MAX=0; while :; do U=\$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n \"\$U\" ] && [ \"\$U\" -gt \"\$MAX\" ] && MAX=\$U && echo \"\$MAX\" > $PF_M; sleep 2; done' </dev/null >/dev/null 2>&1 &"
  sleep 3

  echo "--- launch master .12 @ $(date '+%T') ---" >> "$SUM"
  ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o BatchMode=yes $MASTER_IP "
    ulimit -n 65536 && \
    cd $BASE && \
    export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 && \
    export $NCCL_ENV && \
    export $PYTORCH_ENV && \
    $PY/torchrun --nnodes=2 --node_rank=0 --nproc_per_node=8 \
        --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
        pretrain_launcher.py \
        --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
        --tokenizer-path $BASE/data/tokenizer_eod \
        --train-data-path $BLEND \
        --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
        --tensor-parallel 1 --context-parallel $cp --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed \
        --fp8-recipe tensorwise
  " > "$LOG_M" 2>&1 &
  MASTER_SSH_PID=$!
  echo "  master SSH PID=$MASTER_SSH_PID" >> "$SUM"
  sleep 10

  echo "--- launch worker .29 @ $(date '+%T') ---" >> "$SUM"
  cd "$BASE"; ulimit -n 65536
  export $NCCL_ENV; export $PYTORCH_ENV
  timeout 1500 $PY/torchrun --nnodes=2 --node_rank=1 --nproc_per_node=8 \
      --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
      pretrain_launcher.py \
      --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
      --tokenizer-path $BASE/data/tokenizer_eod \
      --train-data-path $BLEND \
      --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
      --tensor-parallel 1 --context-parallel $cp --eval-interval 99999 --eval-iters 0 --save-interval 0 \
      --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
      --seed 1234 --precision bf16_mixed \
      --fp8-recipe tensorwise > "$LOG_W" 2>&1
  WORKER_RC=$?
  echo "  worker rc=$WORKER_RC @ $(date '+%T')" >> "$SUM"
  wait $MASTER_SSH_PID 2>/dev/null; MASTER_RC=$?
  echo "  master rc=$MASTER_RC @ $(date '+%T')" >> "$SUM"

  kill $MON_W 2>/dev/null; wait $MON_W 2>/dev/null
  timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP 'pkill -f "nvidia-smi.*memory.used" 2>/dev/null; true'

  local PEAK_M=$(timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP "cat $PF_M 2>/dev/null" 2>/dev/null); PEAK_M=${PEAK_M:-0}
  local PEAK_W=$(tail -1 "$PF_W" 2>/dev/null); PEAK_W=${PEAK_W:-0}

  if [ "$WORKER_RC" -ne 0 ] || [ "$MASTER_RC" -ne 0 ]; then
    local oom=$(grep -ciE 'OutOfMemory|CUDA out of memory|out of memory' "$LOG_W" "$LOG_M" 2>/dev/null | awk '{s+=$1}END{print s+0}')
    echo "FAIL: worker_rc=$WORKER_RC master_rc=$MASTER_RC oom=$oom peakM=${PEAK_M}MiB peakW=${PEAK_W}MiB" >> "$SUM"
    grep -iE 'OutOfMemory|CUDA out of memory|RuntimeError|Traceback|Error|Timeout|context.parallel|NotImplemented|assert|cp_size|ring|value' "$LOG_W" "$LOG_M" 2>/dev/null | head -15 >> "$SUM"
    echo "--- master log tail ---" >> "$SUM"; tail -20 "$LOG_M" >> "$SUM" 2>&1
    echo "--- worker log tail ---" >> "$SUM"; tail -20 "$LOG_W" >> "$SUM" 2>&1
    local status=$([ "$oom" -gt 0 ] && echo "OOM" || echo "FAIL")
    echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps $status - - - - $PEAK_M $PEAK_W - - -" >> "$ALL"
  else
    local IL=$(grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {s=$(i+1); gsub(/\//,"",s); if(s+0>=20) print}}')
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
      echo "  pts=$MC med_ms=$MM tok/s=$MT step/s=$SPS per_gpu=$PER loss=$AL gnorm=$AG nan=$NC peakM=${PEAK_M}MiB peakW=${PEAK_W}MiB" >> "$SUM"
      echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps OK $MT $SPS $MM $PER $PEAK_M $PEAK_W $AL $AG $NC" >> "$ALL"
    else
      echo "PARSE_FAIL: no iteration logs (peakM=${PEAK_M}MiB peakW=${PEAK_W}MiB)" >> "$SUM"
      grep -E '^\s*\[.*iteration\s+' "$LOG_W" "$LOG_M" 2>/dev/null | head -5 >> "$SUM"
      echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps PARSE_FAIL - - - - $PEAK_M $PEAK_W - - -" >> "$ALL"
    fi
  fi

  pkill -9 -f "torchrun.*$NAME" 2>/dev/null; true
  timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP "pkill -9 -f 'torchrun.*$NAME' 2>/dev/null; pkill -9 -f 'pretrain_launcher.*$NAME' 2>/dev/null; true"
  for k in 1 2 3 4 5 6 7 8 9 10; do gpus_free_local && break; sleep 3; done
  echo "--- postflight .29 ---" >> "$SUM"; nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  echo "--- postflight .12 ---" >> "$SUM"; timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes $MASTER_IP 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' >> "$SUM" 2>&1
  echo "===== $label DONE @ $(date '+%F %T') =====" >> "$SUM"
  return 0
}

for cfg in "${CONFIGS[@]}"; do set -- $cfg; run_cfg "$1" "$2" "$3" "$4" "$5"; sleep 5; done

echo "" >> "$ALL"
echo "# DUALNODE SEQ16K/32K 16-GPU COMPLETE @ $(date '+%F %T')" >> "$ALL"
echo "ALL=$ALL"
echo "SUMMARY:"
cat "$ALL"
