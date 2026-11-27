#!/usr/bin/env bash
# S1→S2 Blend Hot-Switch Executor (follows SWITCH_RUNBOOK.md)
# Waits for 350k ckpt, cold-switches to S2 blend, auto-rollback on failure.
# Usage: setsid bash s2_switch_executor.sh > /tmp/s2_switch.log 2>&1 < /dev/null &
set -uo pipefail
RUN_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
LLM_HOME="/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm"
TRAIN_SH="$LLM_HOME/scripts/train.sh"
CKPT_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints"
LATEST_CKPT="$CKPT_DIR/latest_checkpointed_iteration.txt"
CURSOR_JSON="$RUN_DIR/data/blendswitch/cursor_offsets_350k.json"
S2_TSV="$LLM_HOME/configs/blend_s2_preblend.tsv"
S1_TSV="$LLM_HOME/configs/blend_s1_preblend.tsv"
WLOG="/tmp/baize_s1_baize2b_worker.log"
DAEMON="$LLM_HOME/scripts/eval/baize_l1_autoqueue_continuous.sh"
RIP="10.239.2.12"
SLOG="/tmp/s2_switch_execution.log"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$SLOG"; }
rollback() {
  log "ROLLBACK: killing+restarting with S1"
  kill "$NEW_PID" 2>/dev/null; sleep 5; kill -9 "$NEW_PID" 2>/dev/null
  ssh -n -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=10 "$RIP" "pkill -f pretrain_launcher" 2>/dev/null
  sleep 10; unset BLEND_CURSOR_OFFSETS_JSON; export BLEND_TSV="$S1_TSV"
  setsid bash "$TRAIN_SH" s1 > /tmp/baize_s2_rollback.log 2>&1 < /dev/null &
  log "ROLLBACK done PID=$!"; log "===== FAILED — ROLLED BACK ====="; exit 1
}
log "===== S2 SWITCH EXECUTOR STARTED ====="
# Phase 0: Pre-switch state
PRE_I=$(tail -5 "$WLOG" 2>/dev/null|grep -oP 'iteration\s+\K\d+'|tail -1)
PRE_L=$(tail -5 "$WLOG" 2>/dev/null|grep -oP 'lm loss:\s+\K[\d.E+]+'|tail -1)
PRE_S=$(tail -5 "$WLOG" 2>/dev/null|grep -oP 'elapsed time per iteration \(ms\):\s+\K[\d.]+'|tail -1)
PRE_C=$(cat "$LATEST_CKPT" 2>/dev/null)
TPID=$(ps -eo pid=,args=|grep -v grep|grep -v cline|awk '$2=="bash" && $3=="scripts/train.sh" && $4=="s1" {print $1}'|head -1)
DPID=$(ps -eo pid=,args=|grep 'baize_l1_autoqueue_continuous'|grep -v grep|awk '{print $1}'|head -1)
log "P0: pre iter=$PRE_I loss=$PRE_L step=$PRE_S ckpt=$PRE_C train=$TPID daemon=$DPID"
[ ! -f "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py" ]&&{ log "FATAL shim missing";exit 1;}
[ ! -f "$CURSOR_JSON" ]&&{ log "FATAL cursor missing";exit 1;}
[ ! -f "$S2_TSV" ]&&{ log "FATAL s2tsv missing";exit 1;}
log "P0: shim+cursor+s2tsv exist ✓"
# Phase 1: Wait for 350k
log "P1: polling for 350k (30s intervals, max 2h)"
for i in $(seq 1 240); do
  CI=$(cat "$LATEST_CKPT" 2>/dev/null)
  [ "$CI" = "350000" ]&&[ -d "$CKPT_DIR/iter_0350000" ]&&{ log "  350k CONFIRMED poll#$i";break;}
  [ "$((i%10))" = "0" ]&&log "  poll#$i ckpt=$CI"
  sleep 30
done
[ "$CI" != "350000" ]&&{ log "FATAL timed out";exit 1;}
sleep 10; log "  ckpt stable"
# Phase 2: Save logs
log "P2: saving pre-switch logs"
cp "$WLOG" /tmp/baize_s1_baize2b_worker_pre_s2.log 2>/dev/null
cp /tmp/baize_s1_baize2b_master.log /tmp/baize_s1_baize2b_master_pre_s2.log 2>/dev/null
# Phase 3: Kill daemon
log "P3: kill daemon PID=$DPID"
[ -n "$DPID" ]&&kill "$DPID" 2>/dev/null&&sleep 3
[ -n "$DPID" ]&&kill -0 "$DPID" 2>/dev/null&&kill -9 "$DPID" 2>/dev/null&&sleep 2
pgrep -f 'llama-server' 2>/dev/null|xargs kill 2>/dev/null;sleep 2; log "  daemon killed"
# Phase 4: Kill training both nodes
log "P4: kill training PID=$TPID"
[ -n "$TPID" ]&&kill "$TPID" 2>/dev/null&&sleep 5
[ -n "$TPID" ]&&kill -0 "$TPID" 2>/dev/null&&kill -9 "$TPID" 2>/dev/null&&sleep 3
ps -eo pid=,args=|grep 'pretrain_launcher\.py'|grep -v grep|awk '{print $1}'|xargs kill -9 2>/dev/null;sleep 3
log "  .29 killed"
ssh -n -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=10 "$RIP" \
  "pkill -f pretrain_launcher 2>/dev/null;pkill -f 'torchrun.*node_rank=0' 2>/dev/null;sleep 2" 2>&1|while read -r l;do log "  .12:$l";done
# Phase 4b: Poll GPU memory on BOTH nodes until clear (fix for 05:18 failure)
# Root cause: old code only checked .29 GPU0 after fixed 20s sleep; .12 GPU
# was still occupied → launcher FATAL "10.239.2.12 GPU 非空闲" → rollback.
log "P4b: polling GPU memory on both nodes until clear (5s interval, max 180s)"
GPU_CLEAR=0
for i in $(seq 1 36); do
  G29_MAX=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
  G12_MAX=$(ssh -n -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=10 "$RIP" \
    "nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1" 2>/dev/null)
  G29_MAX=${G29_MAX:-99999}; G12_MAX=${G12_MAX:-99999}
  log "  poll#$i .29 max=${G29_MAX}MiB .12 max=${G12_MAX}MiB"
  if [ "$G29_MAX" -lt 1000 ] 2>/dev/null && [ "$G12_MAX" -lt 1000 ] 2>/dev/null; then
    log "  both nodes GPU clear ✓"; GPU_CLEAR=1; break
  fi
  sleep 5
done
if [ "$GPU_CLEAR" -ne 1 ]; then
  log "FATAL: GPU not clear after 180s (.29 max=${G29_MAX} .12 max=${G12_MAX})"
  rollback
fi
log "  GPU clear: .29 max=${G29_MAX}MiB .12 max=${G12_MAX}MiB ✓"
# Phase 5: Export S2 env + restart
log "P5: restart with S2 blend"
export BLEND_CURSOR_OFFSETS_JSON="$CURSOR_JSON"
export BLEND_TSV="$S2_TSV"
log "  CURSOR=$CURSOR_JSON"
log "  TSV=$S2_TSV"
setsid bash "$TRAIN_SH" s1 > /tmp/baize_s2_switch_train.log 2>&1 < /dev/null &
NEW_PID=$!
log "  new train PID=$NEW_PID"
# Phase 6: Wait 180s check alive
log "P6: wait 180s startup"
sleep 180
if ! kill -0 "$NEW_PID" 2>/dev/null; then
  log "FATAL: train exited<180s"
  tail -20 /tmp/baize_s2_switch_train.log 2>/dev/null|while read -r l;do log "  $l";done
  rollback
fi
log "  alive after 180s ✓"
# Phase 7: Monitor 300s
log "P7: monitor 300s"
sleep 300
PI=$(tail -20 "$WLOG" 2>/dev/null|grep -oP 'iteration\s+\K\d+'|tail -1)
PL=$(tail -20 "$WLOG" 2>/dev/null|grep -oP 'lm loss:\s+\K[\d.E+]+'|tail -1)
PN=$(tail -20 "$WLOG" 2>/dev/null|grep -oP 'nan iterations:\s+\K\d+'|tail -1)
log "  post iter=$PI loss=$PL nan=$PN"
tail -10 "$WLOG" 2>/dev/null|while read -r l;do log "  w:$l";done
[ "$PN" != "0" ]&&[ -n "$PN" ]&&{ log "FATAL NaN";rollback;}
! kill -0 "$NEW_PID" 2>/dev/null&&{ log "FATAL died";rollback;}
# Check shim both nodes
S29=$(grep -i 'blend.hot.switch' "$WLOG" 2>/dev/null|tail -3)
S12=$(ssh -n -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=10 "$RIP" \
  "grep -i 'blend.hot.switch' /tmp/baize_s1_baize2b_master.log 2>/dev/null|tail -3" 2>/dev/null)
log "  .29 shim: $([ -n "$S29" ]&&echo FOUND✓||echo MISSING⚠️)"
[ -n "$S29" ]&&echo "$S29"|while read -r l;do log "    $l";done
log "  .12 shim: $([ -n "$S12" ]&&echo FOUND✓||echo MISSING⚠️)"
[ -n "$S12" ]&&echo "$S12"|while read -r l;do log "    $l";done
# Phase 8: Restart daemon
log "P8: restart daemon"
setsid bash "$DAEMON" > /tmp/baize_l1_daemon_restart.log 2>&1 < /dev/null &
log "  daemon PID=$!"
# Phase 9: Final
log "P9: DONE"
log "  pre: iter=$PRE_I loss=$PRE_L ckpt=$PRE_C"
log "  post: iter=$PI loss=$PL nan=$PN"
log "  train=$NEW_PID .29shim=$([ -n "$S29" ]&&echo F||echo M) .12shim=$([ -n "$S12" ]&&echo F||echo M)"
log "===== S2 SWITCH COMPLETE ====="
log "Manual rollback if needed: kill $NEW_PID; ssh $RIP 'pkill -f pretrain_launcher'; unset BLEND_CURSOR_OFFSETS_JSON; export BLEND_TSV=$S1_TSV; setsid bash $TRAIN_SH s1"
