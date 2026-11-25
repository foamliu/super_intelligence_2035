#!/usr/bin/env bash
# baize_posttrain_a1_sft_chain.sh -- Autonomous A1 (SFT v39 step105) same-scale
# 5-run chain for the baseline-nailed 令 §C/§D Stage3.
#
# WHY: A0 (MiniCPM5-2B base) 5-run is auto-chained by
# baize_posttrain_a0_run345_chain.sh + baize_posttrain_a0_finalize_watcher.sh.
# Once A0's 5 runs are clean, the A1 arm (SFT v39 global_step_105) must run the
# SAME scale (158 / Pass@1 / 2500s / 5-run / -p 8 -n / same extractor / same
# fail_mode classifier) to isolate the SFT delta (McNemar / paired bootstrap).
# This script waits for A0 completion, then serves the SFT ckpt on GPU5:8096 and
# serially runs A1 run1..5, then finalizes the deliverables.
#
# 冻结协议（总纲 §2，不得改动）：158 任务 / Pass@1 / 2500s/任务 / 单 trace /
#   5-run / -p 8 -n。本链只调度 A1 run1-5，不改协议/题面/check.py/超时/-p。
#
# 串行纪律（baseline-nailed 令 §C）：providers.json 是共享单例；起跑前自检
#   pgrep -f run_cline_script + ss -tlnp，发现他线 cline eval 在跑就等待。
#   本链 run1-5 严格串行；且必须等 A0 5-run 全部完成才起跑。
#
# GPU：仅用 GPU5（FREE，posttrain 备用，wake637 确认）。🚫 不碰 GPU0-3/GPU4/GPU6-7。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVAL_SH="$SCRIPT_DIR/baize_posttrain_5run_eval.sh"
SERVE_SH="$SCRIPT_DIR/baize_posttrain_sft_surrogate_serve.sh"
FINALIZE_PY="$SCRIPT_DIR/baize_posttrain_a0_finalize_5run.py"
RESULTS_DIR="/tmp/posttrain_5run_eval"

A0_LABEL="A0_base"
LABEL="A1_sft"
ENDPOINT="http://127.0.0.1:8096/v1"
MODEL="minicpm5-2b-sft-v39-final"
SERVE_GPU="5"
SERVE_PORT="8096"
SFT_RUN_NAME="minicpm5_agentic_v39_pretok"
SFT_STEP="global_step_105"
SERVE_MEM="0.85"
SERVE_MAX_LEN="65536"
DRY_RUN=0; STATUS_ONLY=0
MAX_WAIT_S=$((30 * 3600))
POLL_INTERVAL=120

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)        DRY_RUN=1 ;;
    --status)         STATUS_ONLY=1 ;;
    *) echo "unknown: $1"; exit 1 ;;
  esac
  shift
done

log() { echo "[$(date '+%F %T')] $*"; }

lane_clear() {
  local others
  others=$(pgrep -af 'run_cline_script|run_design_flow|cline_eval' 2>/dev/null \
           | grep -v grep | grep -v "baize_posttrain_a1_sft_chain")
  if [ -n "$others" ]; then
    log "serial-lane BUSY (other cline eval active):"; echo "$others" | head -3
    return 1
  fi
  return 0
}

a0_run_done() { local n="$1"; [ -f "$RESULTS_DIR/$A0_LABEL/run$n/final_report.json" ]; }

a0_run_pass_rate() {
  local n="$1"
  python3 -c "
import json
d=json.load(open('$RESULTS_DIR/$A0_LABEL/run$n/final_report.json'))
m=d.get('metrics',{})
print(m.get('pass_rate', d.get('pass_rate', d.get('pass@1','N/A'))))
" 2>/dev/null
}

a0_all_done() {
  for n in 1 2 3 4 5; do a0_run_done "$n" || return 1; done
  return 0
}

# Minimal plausibility gate (NOT a judgment on the value — only rejects
# missing/NaN/negative so we don't auto-run A1 on a broken A0).
a0_plausible() {
  for n in 1 2 3 4 5; do
    pr=$(a0_run_pass_rate "$n")
    python3 -c "
v='$pr'
try:
    f=float(v)
except Exception:
    raise SystemExit(1)
if f < 0.0 or f > 1.0:
    raise SystemExit(1)
" || { log "A0 run$n pass_rate='$pr' not in [0,1] — A0 looks broken, aborting A1."; return 1; }
  done
  return 0
}

a1_run_done() { local n="$1"; [ -f "$RESULTS_DIR/$LABEL/run$n/final_report.json" ]; }

a1_run_pass_rate() {
  local n="$1"
  python3 -c "
import json
d=json.load(open('$RESULTS_DIR/$LABEL/run$n/final_report.json'))
m=d.get('metrics',{})
print(m.get('pass_rate', d.get('pass_rate', d.get('pass@1','N/A'))))
" 2>/dev/null
}

if [ $STATUS_ONLY = 1 ]; then
  log "=== A1 SFT chain STATUS ==="
  log "A0 ($A0_LABEL) completion:"
  for n in 1 2 3 4 5; do
    if a0_run_done "$n"; then log "  A0 run$n: DONE  pass_rate=$(a0_run_pass_rate "$n")"
    else log "  A0 run$n: pending"; fi
  done
  log "A1 ($LABEL) progress:"
  for n in 1 2 3 4 5; do
    if a1_run_done "$n"; then log "  A1 run$n: DONE  pass_rate=$(a1_run_pass_rate "$n")"
    else log "  A1 run$n: pending"; fi
  done
  if curl -s --max-time 3 "http://localhost:${SERVE_PORT}/v1/models" | grep -q "$MODEL"; then
    log "  A1 serve :${SERVE_PORT}: HEALTHY ($MODEL)"
  else
    log "  A1 serve :${SERVE_PORT}: not running"
  fi
  exit 0
fi

log "=== A1 SFT chain START ==="
log "label=$LABEL endpoint=$ENDPOINT model=$MODEL"
log "serve: GPU${SERVE_GPU} port ${SERVE_PORT} run_name=$SFT_RUN_NAME step=$SFT_STEP"

if [ $DRY_RUN = 1 ]; then
  log "[dry-run] would: wait A0 5-run done+plausible -> lane_clear ->"
  log "[dry-run]   $SERVE_SH --run-name $SFT_RUN_NAME --gpu $SERVE_GPU --port $SERVE_PORT --name $MODEL --mem $SERVE_MEM --max-len $SERVE_MAX_LEN"
  log "[dry-run]   for n in 1 2 3 4 5: lane_clear? -> $EVAL_SH --endpoint $ENDPOINT --model $MODEL --label $LABEL --run n"
  log "[dry-run] then mean±std -> $FINALIZE_PY --label $LABEL --runs 1,2,3,4,5 --require-all"
  exit 0
fi

[ -x "$EVAL_SH" ] || chmod +x "$EVAL_SH" 2>/dev/null || true
[ -x "$SERVE_SH" ] || chmod +x "$SERVE_SH" 2>/dev/null || true
[ -f "$EVAL_SH" ]   || { echo "FATAL: $EVAL_SH not found"; exit 1; }
[ -f "$SERVE_SH" ]  || { echo "FATAL: $SERVE_SH not found"; exit 1; }
[ -f "$FINALIZE_PY" ] || { echo "FATAL: $FINALIZE_PY not found"; exit 1; }

# ---- 1. Wait for A0 5-run to finish (A0 holds the serial lane) -------------
log "waiting for A0 ($A0_LABEL) 5-run to finish (max ${MAX_WAIT_S}s)..."
waited=0
while ! a0_all_done; do
  sleep "$POLL_INTERVAL"; waited=$((waited + POLL_INTERVAL))
  if [ $waited -ge $MAX_WAIT_S ]; then
    log "FATAL: A0 still not done after ${waited}s — aborting A1 chain."
    exit 2
  fi
  if [ $((waited % 600)) -eq 0 ] && [ $waited -gt 0 ]; then
    log "still waiting for A0 5-run... (${waited}s elapsed)"
  fi
done
log "A0 5-run all DONE."
for n in 1 2 3 4 5; do log "  A0 run$n pass_rate=$(a0_run_pass_rate "$n")"; done

# ---- 2. Plausibility gate --------------------------------------------------
if ! a0_plausible; then
  log "ABORT: A0 5-run failed plausibility gate. A1 NOT started. Inspect A0."
  exit 3
fi
log "A0 5-run passed plausibility gate (all pass_rate in [0,1])."

# ---- 3. Serial-lane clear --------------------------------------------------
while ! lane_clear; do
  log "serial-lane busy before A1 serve — waiting ${POLL_INTERVAL}s..."
  sleep "$POLL_INTERVAL"
done
log "serial-lane clear for A1."

# ---- 4. Serve SFT v39 step105 on GPU5:8096 ---------------------------------
if curl -s --max-time 3 "http://localhost:${SERVE_PORT}/v1/models" | grep -q "$MODEL"; then
  log "A1 serve :${SERVE_PORT} already HEALTHY ($MODEL) — reuse."
else
  log "launching A1 serve: $SERVE_SH --run-name $SFT_RUN_NAME --gpu $SERVE_GPU --port $SERVE_PORT --name $MODEL --mem $SERVE_MEM --max-len $SERVE_MAX_LEN"
  bash "$SERVE_SH" --run-name "$SFT_RUN_NAME" --gpu "$SERVE_GPU" --port "$SERVE_PORT" \
       --name "$MODEL" --mem "$SERVE_MEM" --max-len "$SERVE_MAX_LEN"
  rc=$?
  if [ $rc -ne 0 ]; then
    log "FATAL: A1 serve launch failed (rc=$rc). Aborting A1 chain."
    exit 4
  fi
fi

# ---- 5. B1 identity proof (baseline-nailed 令 §B.1) ------------------------
log "=== B1 identity proof for A1 ==="
mid=$(curl -s --max-time 5 "$ENDPOINT/models" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['data'][0]['id'])" 2>/dev/null)
log "  served_model_id = ${mid:-<fetch failed>}"
log "  requested_model = $MODEL"
log "  ckpt_path       = $SCRIPT_DIR/sft_surrogate_runs/$SFT_RUN_NAME/$SFT_STEP"
log "  ckpt_mtime      = $(stat -c '%y' "$SCRIPT_DIR/sft_surrogate_runs/$SFT_RUN_NAME/$SFT_STEP" 2>/dev/null)"
if [ "$mid" != "$MODEL" ]; then
  log "FATAL: B1 identity mismatch (served='$mid' != requested='$MODEL'). Aborting A1 chain."
  exit 5
fi
log "B1 identity PASS (served==requested)."

# ---- 6. Serially run A1 run1 -> run5 ---------------------------------------
for n in 1 2 3 4 5; do
  if a1_run_done "$n"; then log "A1 run$n already DONE — skip"; continue; fi

  log "=== preparing A1 run$n ==="
  while ! lane_clear; do
    log "serial-lane busy before A1 run$n — waiting ${POLL_INTERVAL}s..."
    sleep "$POLL_INTERVAL"
  done
  log "serial-lane clear for A1 run$n."

  log "launching A1 run$n: $EVAL_SH --endpoint $ENDPOINT --model $MODEL --label $LABEL --run $n"
  bash "$EVAL_SH" --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run "$n"
  rc=$?
  log "A1 run$n eval-sh rc=$rc"

  if ! a1_run_done "$n"; then
    log "WARNING: A1 run$n produced no final_report.json (rc=$rc). Continuing; gap reported."
  else
    log "A1 run$n DONE pass_rate=$(a1_run_pass_rate "$n")"
  fi
done

# ---- 7. Compute A1 5-run mean±std ------------------------------------------
log "=== Computing A1 5-run mean±std ==="
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
  print(f'A1 5-run mean±std: {statistics.mean(r):.6f}±{statistics.stdev(r):.6f} (n={len(r)}/5)')
elif len(r)==1:
  print(f'A1 1 run: {r[0]:.6f}')
else:
  print('No results')
" 2>&1

# ---- 8. Finalize A1 deliverables (pertask JSONs + 5-run summary) -----------
log "=== Finalizing A1 deliverables ==="
cd "$SCRIPT_DIR"
python3 "$FINALIZE_PY" --label "$LABEL" --runs 1,2,3,4,5 --require-all 2>&1
rc=$?
log "finalize rc=$rc"
if [ $rc -eq 0 ]; then
  log "A1 deliverables: baseline_${LABEL}_run<N>_pertask.json + baseline_${LABEL}_5run_summary.json"
fi
log "=== A1 SFT chain END (serve left running on GPU${SERVE_GPU}:${SERVE_PORT}) ==="
