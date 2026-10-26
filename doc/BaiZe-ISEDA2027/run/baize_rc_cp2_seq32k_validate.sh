#!/bin/bash
# BaiZe-2B Context-Parallel smoke - SINGLE NODE (2026-10-26, 运维令 23:0x §3 CP=2/4可行性)
# 单机 .29 8xH100, nnodes=1, 无 ssh -> 规避 2-node master-ssh redirect 挂起.
# 目的: seq32768 CP=1 OOM (cfg5/cfg6), 测 CP=2 能否启用 32K 满速.
# 配方: DP=8/cp, TP1/PP1, FP8 tensorwise, graph OFF (rev3 真因=CUDA Graph 顶格停滞).
# cp1: DP8 seq32768 mbs1 tok/mb/gpu=32768 -> 期望 OOM (印证 CP 必要)
# cp2: DP4 seq32768 mbs1 tok/mb/gpu=16384 (=悬崖边界, graph-off 应满速)
# rev3 基线(2-node DP16): cfg0ang tok/mb=16384 graph-off = 561,126 tok/s, per-gpu 35,070, 75,517 MiB.
set -o pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
ITERS=40
ROOT=/tmp/baize_rc_cp2_validate
mkdir -p "$ROOT"
ALL="$ROOT/ALL_RESULTS.txt"
echo "# BaiZe-2B CP smoke SINGLE-NODE @ $(date '+%F %T')" > "$ALL"
echo "# Recipe: .29 8xH100, nnodes=1, TP1/PP1, FP8 tensorwise, graph OFF, real data" >> "$ALL"
echo "# rev3 baseline (2-node DP16): cfg0ang tok/mb=16384 graph-off = 561,126 tok/s, per-gpu 35,070, 75,517 MiB" >> "$ALL"
echo "# cols: label seq mbs gbs cp dp accum tok_per_mb_per_gpu tok_per_step status tok_per_s step_per_s med_ms per_gpu_tok_s peak_mem_MiB loss gnorm nan" >> "$ALL"
BLEND=""
for i in $(seq 0 7); do BLEND="$BLEND 1 ${OUT}/p5b_l3_train_s${i}"; done
BLEND="${BLEND# }"
CONFIGS=(
  "cp2_seq32k 32768 1 8 2"
)
NCCL_ENV="NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22"
PYTORCH_ENV="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1"
gpus_free() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n "$u" ] && [ "$u" -lt 2000 ]; }
run_cfg() {
  local label="$1" seq="$2" mbs="$3" gbs="$4" cp="$5"
  local dp=$(( 8 / cp ))
  local accum=$(( gbs / (mbs * dp) ))
  local tmb_pg=$(( mbs * seq / cp ))
  local tps=$(( gbs * seq ))
  local D="$ROOT/$label"; mkdir -p "$D"
  local LOG="$D/train.log" PF="$D/peakmem" SUM="$D/summary.txt"
  local NAME="cp2val_rc_${label}"
  echo "===== $label (seq=$seq mbs=$mbs gbs=$gbs CP=$cp DP=$dp accum=$accum tok/mb/gpu=$tmb_pg tps=$tps) @ $(date '+%F %T') =====" > "$SUM"
  echo "tok/mb_per_gpu=$tmb_pg tok/step=$tps CP=$cp DP=$dp" >> "$SUM"
  echo "--- preflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  if ! gpus_free; then echo "PREFLIGHT_FAIL" >> "$SUM"; echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps PREFLIGHT_FAIL - - - - - - - -" >> "$ALL"; return 1; fi
  : > "$PF"
  ( MAX=0; while :; do U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1); [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX="$U" && echo "$MAX" > "$PF"; sleep 2; done ) & MON=$!
  echo "--- launch @ $(date '+%T') ---" >> "$SUM"
  cd "$BASE"; ulimit -n 65536
  export $NCCL_ENV; export $PYTORCH_ENV
  timeout 1200 $PY/torchrun --nnodes=1 --nproc_per_node=8 --standalone --master_port=29566 \
      pretrain_launcher.py --arch mamba2 --name $NAME --dir $BASE/nemo_experiments \
      --tokenizer-path $BASE/data/tokenizer_eod --train-data-path $BLEND \
      --train-iters $ITERS --global-batch-size $gbs --micro-batch-size $mbs --seq-length $seq \
      --tensor-parallel 1 --context-parallel $cp --eval-interval 99999 --eval-iters 0 --save-interval 0 \
      --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
      --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise > "$LOG" 2>&1
  RC=$?
  echo "  rc=$RC @ $(date '+%T')" >> "$SUM"
  kill $MON 2>/dev/null; wait $MON 2>/dev/null
  local PEAK=$(tail -1 "$PF" 2>/dev/null); PEAK=${PEAK:-0}
  if [ "$RC" -ne 0 ]; then
    local oom=$(grep -ciE 'OutOfMemory|CUDA out of memory|out of memory' "$LOG" 2>/dev/null | awk '{s+=$1}END{print s+0}')
    echo "FAIL: rc=$RC oom_lines=$oom peak=${PEAK}MiB" >> "$SUM"
    grep -iE 'OutOfMemory|CUDA out of memory|RuntimeError|Traceback|Error|Timeout|context.parallel|NotImplemented|assert|cp_size|ring|not support|value' "$LOG" 2>/dev/null | head -15 >> "$SUM"
    echo "--- train.log tail ---" >> "$SUM"; tail -25 "$LOG" >> "$SUM" 2>&1
    local status=$([ "$oom" -gt 0 ] && echo "OOM" || echo "FAIL")
    echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps $status - - - - $PEAK - - -" >> "$ALL"
  else
    local IL=$(grep -E '^\s*\[.*iteration\s+' "$LOG" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {s=$(i+1); gsub(/\//,"",s); if(s+0>=5) print}}')
    local MS=$(echo "$IL" | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    local MC=$(echo "$MS" | grep -c .)
    local LG=$(echo "$IL" | grep -oP 'lm loss: \K[0-9.]+')
    local GN=$(echo "$IL" | grep -oP 'grad norm: \K[0-9.]+')
    if [ "$MC" -gt 0 ]; then
      local MM=$(echo "$MS" | sort -n | awk '{a[NR]=$1} END{if(NR%2) print a[(NR+1)/2]; else printf "%.1f",(a[NR/2]+a[NR/2+1])/2}')
      local MT=$(awk -v t="$tps" -v m="$MM" 'BEGIN{printf "%.0f",t/(m/1000)}')
      local SPS=$(awk -v m="$MM" 'BEGIN{printf "%.3f",1000/m}')
      local PER=$(( MT / 8 ))
      local AL=$(echo "$LG" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
      local AG=$(echo "$GN" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
      local NC=$(echo "$IL" | grep -oP 'number of nan iterations:\s+\K[0-9]+' | awk '{s+=$1} END{print s+0}')
      echo "  pts=$MC med_ms=$MM tok/s=$MT step/s=$SPS per_gpu=$PER loss=$AL gnorm=$AG nan=$NC peak=${PEAK}MiB" >> "$SUM"
      echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps OK $MT $SPS $MM $PER $PEAK $AL $AG $NC" >> "$ALL"
    else
      echo "PARSE_FAIL: no iteration logs (peak=${PEAK}MiB)" >> "$SUM"
      grep -E '^\s*\[.*iteration\s+' "$LOG" 2>/dev/null | head -5 >> "$SUM"
      echo "$label $seq $mbs $gbs $cp $dp $accum $tmb_pg $tps PARSE_FAIL - - - - $PEAK - - -" >> "$ALL"
    fi
  fi
  echo "--- postflight .29 ---" >> "$SUM"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> "$SUM" 2>&1
  pkill -9 -f "cp2val_rc_${label}" 2>/dev/null; true
  for k in 1 2 3 4 5; do gpus_free && break; sleep 3; done
  echo "===== $label DONE @ $(date '+%F %T') =====" >> "$SUM"
  return 0
}
for cfg in "${CONFIGS[@]}"; do set -- $cfg; run_cfg "$1" "$2" "$3" "$4" "$5"; done
echo "" >> "$ALL"
echo "# CP2 SEQ32K VALIDATE (patch test) COMPLETE @ $(date '+%F %T')" >> "$ALL"
echo "CP2 SEQ32K VALIDATE (patch test) COMPLETE"
