#!/usr/bin/env bash
# baize_posttrain_a0a1_compare_watcher.sh -- fire-and-forget watcher that runs the
# A0-vs-A1 paired statistical comparison once BOTH 5-run summaries exist.
#
# WHY (baseline-nailed 令 §D Stage3 / §E): the A0 finalize-watcher produces
# baseline_A0_base_5run_summary.json; the A1 chain (step 8) produces
# baseline_A1_sft_5run_summary.json. Neither auto-runs the paired comparison
# (McNemar / paired bootstrap / Wilcoxon) that quantifies the SFT delta. This
# watcher polls for BOTH files, then invokes
# baize_posttrain_arm_paired_compare.py and exits.
#
# Safe: new process, does NOT modify the running A1 chain (bash incremental-read
# risk, see AGENTS.md §3). Pure CPU stats, no GPU/sandbox/network.
#
# Usage: bash baize_posttrain_a0a1_compare_watcher.sh [--status]
#   launch fire-and-forget:
#     setsid bash -c 'exec bash baize_posttrain_a0a1_compare_watcher.sh > /tmp/posttrain_a0a1_compare_watcher.log 2>&1' < /dev/null &
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPARE_PY="$SCRIPT_DIR/baize_posttrain_arm_paired_compare.py"
A0_SUM="$SCRIPT_DIR/baseline_A0_base_5run_summary.json"
A1_SUM="$SCRIPT_DIR/baseline_A1_sft_5run_summary.json"
OUT="$SCRIPT_DIR/baseline_A0_vs_A1_paired_compare.json"
LOG=/tmp/posttrain_a0a1_compare_watcher.log
MAX_WAIT_S=$((48 * 3600))   # A0~5h + A1~18h => generous
POLL_INTERVAL=180
STATUS_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --status) STATUS_ONLY=1 ;;
    *) echo "unknown: $1" ;;
  esac
  shift
done

log() { echo "[$(date '+%F %T')] $*"; }

if [ $STATUS_ONLY = 1 ]; then
  echo "A0 summary: $([ -f "$A0_SUM" ] && echo PRESENT || echo pending)"
  echo "A1 summary: $([ -f "$A1_SUM" ] && echo PRESENT || echo pending)"
  echo "out:        $([ -f "$OUT" ] && echo PRESENT || echo pending)"
  exit 0
fi

[ -f "$COMPARE_PY" ] || { log "FATAL: $COMPARE_PY not found"; exit 1; }

log "=== A0-vs-A1 compare-watcher START ==="
log "polling for A0=$A0_SUM and A1=$A1_SUM (max ${MAX_WAIT_S}s)"

waited=0
while true; do
  if [ -f "$A0_SUM" ] && [ -f "$A1_SUM" ]; then
    log "BOTH summaries PRESENT -> running paired comparison."
    break
  fi
  sleep "$POLL_INTERVAL"; waited=$((waited + POLL_INTERVAL))
  if [ $waited -ge $MAX_WAIT_S ]; then
    log "FATAL: timed out after ${waited}s waiting for both summaries. A0=$([ -f "$A0_SUM" ] && echo Y || echo N) A1=$([ -f "$A1_SUM" ] && echo Y || echo N)"
    exit 2
  fi
  if [ $((waited % 1800)) -eq 0 ] && [ $waited -gt 0 ]; then
    log "still waiting... (${waited}s) A0=$([ -f "$A0_SUM" ] && echo Y || echo N) A1=$([ -f "$A1_SUM" ] && echo Y || echo N)"
  fi
done

cd "$SCRIPT_DIR"
log "invoking: python3 $COMPARE_PY --a0 $A0_SUM --a1 $A1_SUM --out $OUT"
python3 "$COMPARE_PY" --a0 "$A0_SUM" --a1 "$A1_SUM" --out "$OUT" 2>&1
rc=$?
log "compare rc=$rc"
if [ $rc -eq 0 ] && [ -f "$OUT" ]; then
  log "DELIVERABLE written: $OUT"
  python3 -c "
import json
d=json.load(open('$OUT'))
a0=d['arms'].get('A0_base',{}); a1=d['arms'].get('A1_sft',{})
print('A0 mean=%.4f+/-%.4f (n=%s)' % (a0.get('mean_pass_rate',0), a0.get('std_pass_rate',0), a0.get('n_runs')))
print('A1 mean=%.4f+/-%.4f (n=%s)' % (a1.get('mean_pass_rate',0), a1.get('std_pass_rate',0), a1.get('n_runs')))
print('delta(A1-A0)=%.4f' % d.get('delta_mean_pass_rate',0))
b=d.get('paired_bootstrap') or {}
print('bootstrap CI95=[%.4f,%.4f] p=%.4g' % (b.get('ci95_low',0),b.get('ci95_high',0),b.get('p_two_sided',1)))
m=(d.get('mcnemar') or {}).get('majority',{})
print('McNemar(majority): both=%s A0only=%s A1only=%s exact_p=%s' % (m.get('both_pass'),m.get('A0_only'),m.get('A1_only'),m.get('exact_binom_p_two_sided')))
" 2>&1
else
  log "ERROR: compare did not produce $OUT (rc=$rc)"
  exit 3
fi
log "=== compare-watcher DONE ==="
