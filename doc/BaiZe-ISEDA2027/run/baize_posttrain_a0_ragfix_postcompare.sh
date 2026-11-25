#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# baize_posttrain_a0_ragfix_postcompare.sh
#
# Watcher: waits for the A0_base_ragfix resume process to EXIT, then runs the
# paired statistical comparison (A0_base_ragfix [restored retrieval] vs
# A0_base [degraded retrieval, 43.29%]) required by ops order
# §A0_base_ragfix 判据④ (McNemar / paired bootstrap, 158 tasks).
#
# Does NOT touch the running resume script (AGENTS.md §3: never edit a running
# bash script). Pure stats: no GPU / sandbox / network / protocol change.
# Idempotent: overwrites output. Safe to re-run.
#
# Usage:
#   bash baize_posttrain_a0_ragfix_postcompare.sh [RESUME_PID]
#   (default RESUME_PID=3953894, the setsid ragfix resume driver)
#
# Output:
#   baseline_A0_base_vs_A0_ragfix_paired_compare.json   (paired compare result)
#   /tmp/posttrain_a0_ragfix_postcompare.log            (watcher log)
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
cd "$RUN_DIR" || exit 2

RESUME_PID="${1:-3953894}"
LOG="/tmp/posttrain_a0_ragfix_postcompare.log"
OLD_SUMMARY="baseline_A0_base_5run_summary.json"          # degraded retrieval, 43.29%
NEW_SUMMARY="baseline_A0_base_ragfix_5run_summary.json"   # restored retrieval
OUT="baseline_A0_base_vs_A0_ragfix_paired_compare.json"
COMPARE="baize_posttrain_arm_paired_compare.py"

log(){ echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== A0_base_ragfix post-compare watcher START ==="
log "RUN_DIR=$RUN_DIR RESUME_PID=$RESUME_PID"

# --- 1. wait for resume driver to exit (max ~8h) ---
MAX_WAIT=480   # iterations
ITER=0
while [ "$ITER" -lt "$MAX_WAIT" ]; do
  if ! kill -0 "$RESUME_PID" 2>/dev/null; then
    log "resume PID $RESUME_PID has exited (after ${ITER} poll cycles) -> proceed to compare"
    break
  fi
  ITER=$((ITER+1))
  [ $((ITER % 10)) -eq 0 ] && log "still waiting for resume PID $RESUME_PID (poll ${ITER}/${MAX_WAIT})..."
  sleep 60
done
if kill -0 "$RESUME_PID" 2>/dev/null; then
  log "TIMEOUT: resume PID $RESUME_PID still alive after ${MAX_WAIT} cycles (~8h) -> abort (a future wake will retry)"
  exit 3
fi

# --- 2. confirm new 5-run summary exists with enough runs ---
if [ ! -f "$NEW_SUMMARY" ]; then
  log "ABORT: $NEW_SUMMARY not found after resume exit -> finalize may have failed; a future wake will investigate"
  exit 4
fi
N_RUNS=$(python3 -c "import json;print(json.load(open('$NEW_SUMMARY')).get('n_runs_completed',0))" 2>/dev/null || echo 0)
NEW_MEAN=$(python3 -c "import json;print(json.load(open('$NEW_SUMMARY')).get('five_run_mean'))" 2>/dev/null || echo "?")
NEW_STD=$(python3 -c "import json;print(json.load(open('$NEW_SUMMARY')).get('five_run_std'))" 2>/dev/null || echo "?")
log "$NEW_SUMMARY present: n_runs_completed=$N_RUNS mean=$NEW_MEAN std=$NEW_STD"

if [ "$N_RUNS" -lt 4 ]; then
  log "ABORT: n_runs_completed=$N_RUNS < 4 (insufficient for 5-run mean); a future wake will investigate"
  exit 5
fi

# --- 3. run paired compare (old A0_base degraded vs new A0_base_ragfix restored) ---
if [ ! -f "$OLD_SUMMARY" ]; then
  log "ABORT: $OLD_SUMMARY (old degraded-retrieval baseline) not found"
  exit 6
fi
if [ ! -f "$COMPARE" ]; then
  log "ABORT: $COMPARE not found"
  exit 7
fi

log "running paired compare: --a0 $OLD_SUMMARY --a1 $NEW_SUMMARY --out $OUT"
python3 "$COMPARE" --a0 "$OLD_SUMMARY" --a1 "$NEW_SUMMARY" --out "$OUT" 2>&1 | tee -a "$LOG"
RC=${PIPESTATUS[0]}
log "paired compare rc=$RC"

if [ -f "$OUT" ]; then
  log "=== paired compare result readout ==="
  python3 -c "
import json
d=json.load(open('$OUT'))
print('arms=',list(d.get('arms',{}).keys()))
print('delta_mean_pass_rate=',d.get('delta_mean_pass_rate'))
print('n_tasks_paired=',d.get('n_tasks_paired'))
maj=d.get('mcnemar',{}).get('majority',{})
print('mcnemar_majority_chi2=',maj.get('chi2'),'p=',maj.get('p_two_sided'))
boot=d.get('paired_bootstrap',{})
print('bootstrap_delta=',boot.get('delta_mean'),'ci95=',boot.get('ci95'),'p=',boot.get('p_two_sided'))
" 2>&1 | tee -a "$LOG"
  log "OUTPUT: $RUN_DIR/$OUT"
fi
log "=== A0_base_ragfix post-compare watcher DONE (rc=$RC) ==="
exit "$RC"
