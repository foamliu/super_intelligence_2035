#!/usr/bin/env bash
# baize_posttrain_a0_finalize_watcher.sh -- wait for the run345 chain to finish
# all 5 A0 runs, then run finalize to emit the two deliverables (pertask JSONs +
# 5-run summary). Safe/idempotent: finalize re-runs cleanly; pertask files that
# already exist are reused. Satisfies baseline-nailed 令 §D Stage3 / §E 交付物 2+3.
#
# WHY: baize_posttrain_a0_run345_chain.sh only prints mean±std to /tmp log; it
# does NOT call baize_posttrain_a0_finalize_5run.py. This watcher closes the gap
# so the deliverables land automatically without an extra wake.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="${1:-A0_base}"
CHAIN_PID="${2:-}"   # optional: chain PID to also wait on
RESULTS_DIR="/tmp/posttrain_5run_eval"
LOG=/tmp/posttrain_a0_finalize_watcher.log
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

all_done(){
  for n in 1 2 3 4 5; do
    [ -f "$RESULTS_DIR/$LABEL/run$n/final_report.json" ] || return 1
  done
  return 0
}

log "=== watcher START label=$LABEL chain_pid=$CHAIN_PID ==="
# Poll up to ~30h for all 5 runs (run3/4/5 each ~5h codegen).
for i in $(seq 1 1800); do
  if all_done; then log "all 5 final_report.json present."; break; fi
  sleep 60
done
if ! all_done; then
  log "FATAL: not all 5 runs done after ~30h; aborting finalize."
  exit 2
fi
# Extra grace in case the chain is still mid-write.
sleep 30
log "all 5 runs done — running finalize --require-all"
cd "$SCRIPT_DIR"
python3 baize_posttrain_a0_finalize_5run.py --label "$LABEL" --runs 1,2,3,4,5 --require-all 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
log "finalize rc=$rc"
log "=== watcher END ==="
exit $rc
