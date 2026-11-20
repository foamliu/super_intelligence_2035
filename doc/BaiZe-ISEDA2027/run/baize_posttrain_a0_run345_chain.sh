#!/usr/bin/env bash
# baize_posttrain_a0_run345_chain.sh -- Autonomous A0 (MiniCPM5-2B base) 5-run
# completion chain: waits for run2 (launched as `--run 2` single-run) to exit,
# then serially runs run3 -> run4 -> run5 via baize_posttrain_5run_eval.sh, and
# finally prints the 5-run mean±std.
#
# WHY THIS EXISTS: run2 was launched with `--run 2` (single run, run_single),
# NOT `--run-all`, so nothing auto-chains run3-5 after run2 finishes. This chain
# fulfills the authorized Stage3 plan (A0 补满 5-run, baseline-nailed 令 §C/§D).
#
# 冻结协议（总纲 §2，不得改动）：158 任务 / Pass@1 / 2500s/任务 / 单 trace /
#   5-run / -p 8 -n。本链只调度 run3/4/5，不改协议、不改题面/check.py/超时/-p。
#
# 串行纪律（baseline-nailed 令 §C）：providers.json 是共享单例；起跑前自检
#   `pgrep -f run_cline_script` + `ss -tlnp | grep -E ':(30|80)'`，发现他线
#   cline eval 在跑就等待（不并发）。本链 run3/4/5 严格串行，互不并发。
#
# Usage (background, fire-and-forget while run2 still RUNNING):
#   nohup bash baize_posttrain_a0_run345_chain.sh \
#     --run2-pid 4122533 --endpoint http://127.0.0.1:8098/v1 \
#     --model minicpm5-2b --label A0_base \
#     > /tmp/posttrain_a0_run345_chain.log 2>&1 &
#
#   bash baize_posttrain_a0_run345_chain.sh --dry-run     # print recipe only
#   bash baize_posttrain_a0_run345_chain.sh --status      # show wait/progress
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVAL_SH="$SCRIPT_DIR/baize_posttrain_5run_eval.sh"
RESULTS_DIR="/tmp/posttrain_5run_eval"

RUN2_PID=""
ENDPOINT="http://127.0.0.1:8098/v1"
MODEL="minicpm5-2b"
LABEL="A0_base"
DRY_RUN=0; STATUS_ONLY=0
MAX_WAIT_S=$((8 * 3600))   # 8h safety cap waiting for run2 to finish
POLL_INTERVAL=120          # 2 min poll while waiting for run2 / serial lane

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)        DRY_RUN=1 ;;
    --status)         STATUS_ONLY=1 ;;
    --run2-pid)       RUN2_PID="$2"; shift ;;
    --endpoint)       ENDPOINT="$2"; shift ;;
    --model)          MODEL="$2"; shift ;;
    --label)          LABEL="$2"; shift ;;
    *) echo "unknown: $1"; exit 1 ;;
  esac
  shift
done

if [ -z "$RUN2_PID" ]; then echo "FATAL: --run2-pid required"; exit 1; fi

log() { echo "[$(date '+%F %T')] $*"; }

# Serial-discipline self-check (baseline-nailed 令 §C). Returns 0 if lane clear.
lane_clear() {
  local others
  others=$(pgrep -af 'run_cline_script|run_design_flow|cline_eval' 2>/dev/null \
           | grep -v grep | grep -v "baize_posttrain_a0_run345_chain")
  if [ -n "$others" ]; then
    log "serial-lane BUSY (other cline eval active):"; echo "$others" | head -3
    return 1
  fi
  return 0
}

run_is_done() { local n="$1"; [ -f "$RESULTS_DIR/$LABEL/run$n/final_report.json" ]; }

run_pass_rate() {
  local n="$1"
  python3 -c "
import json
d=json.load(open('$RESULTS_DIR/$LABEL/run$n/final_report.json'))
m=d.get('metrics',{})
print(m.get('pass_rate', d.get('pass_rate', d.get('pass@1','N/A'))))
" 2>/dev/null
}

if [ $STATUS_ONLY = 1 ]; then
  log "=== A0 run345 chain STATUS ==="
  for n in 1 2 3 4 5; do
    if run_is_done "$n"; then log "run$n: DONE  pass_rate=$(run_pass_rate "$n")"
    else log "run$n: pending"; fi
  done
  if kill -0 "$RUN2_PID" 2>/dev/null; then log "run2 PID $RUN2_PID: ALIVE (codegen RUNNING)"
  else log "run2 PID $RUN2_PID: exited"; fi
  exit 0
fi

log "=== A0 run345 chain START ==="
log "run2-pid=$RUN2_PID endpoint=$ENDPOINT model=$MODEL label=$LABEL"
log "eval_sh=$EVAL_SH"

if [ $DRY_RUN = 1 ]; then
  log "[dry-run] would: wait for PID $RUN2_PID exit -> verify run2 final_report ->"
  log "[dry-run]   for n in 3 4 5: lane_clear? -> $EVAL_SH --run n -> verify final_report"
  log "[dry-run] then print 5-run mean±std"
  exit 0
fi

[ -x "$EVAL_SH" ] || chmod +x "$EVAL_SH" 2>/dev/null || true
if [ ! -f "$EVAL_SH" ]; then echo "FATAL: $EVAL_SH not found"; exit 1; fi

# ---- 1. Wait for run2 to finish -------------------------------------------
log "waiting for run2 (PID $RUN2_PID) to exit (max ${MAX_WAIT_S}s)..."
waited=0
while kill -0 "$RUN2_PID" 2>/dev/null; do
  sleep "$POLL_INTERVAL"; waited=$((waited + POLL_INTERVAL))
  if [ $waited -ge $MAX_WAIT_S ]; then
    log "FATAL: run2 still alive after ${waited}s — aborting chain (do not auto-kill)."
    exit 2
  fi
  if [ $((waited % 600)) -eq 0 ] && [ $waited -gt 0 ]; then
    log "still waiting for run2... (${waited}s elapsed)"
  fi
done
log "run2 (PID $RUN2_PID) has exited (waited ${waited}s)."

# ---- 2. Verify run2 produced a final_report --------------------------------
if ! run_is_done 2; then
  log "ERROR: run2 exited but no final_report.json — run2 may have failed."
  log "run2 dir contents:"; ls -la "$RESULTS_DIR/$LABEL/run2/" 2>/dev/null
  log "Aborting chain (will not start run3 on a failed run2). Inspect run2."
  exit 3
fi
log "run2 DONE pass_rate=$(run_pass_rate 2)"

# ---- 3. Serially run run3 -> run4 -> run5 ----------------------------------
for n in 3 4 5; do
  if run_is_done "$n"; then log "run$n already DONE — skip"; continue; fi

  log "=== preparing run$n ==="
  while ! lane_clear; do
    log "serial-lane busy before run$n — waiting ${POLL_INTERVAL}s..."
    sleep "$POLL_INTERVAL"
  done
  log "serial-lane clear for run$n."

  log "launching run$n: $EVAL_SH --endpoint $ENDPOINT --model $MODEL --label $LABEL --run $n"
  bash "$EVAL_SH" --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run "$n"
  rc=$?
  log "run$n eval-sh rc=$rc"

  if ! run_is_done "$n"; then
    log "WARNING: run$n produced no final_report.json (rc=$rc). Continuing; gap reported."
  else
    log "run$n DONE pass_rate=$(run_pass_rate "$n")"
  fi
done

# ---- 4. Compute 5-run mean±std --------------------------------------------
log "=== Computing A0 5-run mean±std ==="
python3 -c "
import json,os,statistics
r=[]
for i in range(1,6):
  f='$RESULTS_DIR/$LABEL/run'+str(i)+'/final_report.json'
  if os.path.exists(f):
    d=json.load(open(f)); m=d.get('metrics',{})
    p=m.get('pass_rate', d.get('pass_rate', d.get('pass@1')))
    if p is not None:
      r.append(float(p)); print(f'Run {i}: {p:.6f}')
  else:
    print(f'Run {i}: MISSING')
if len(r)>=2:
  print(f'A0 5-run mean±std: {statistics.mean(r):.6f}±{statistics.stdev(r):.6f} (n={len(r)}/5)')
elif len(r)==1:
  print(f'A0 1 run: {r[0]:.6f}')
else:
  print('No results')
" 2>&1
log "=== A0 run345 chain END ==="

