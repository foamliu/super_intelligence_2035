#!/bin/bash
# baize_posttrain_baseline_report_watcher.sh
# Auto-regenerates reports/report_posttrain_baseline_nailed_zh.html whenever any
# baseline-nailed JSON deliverable lands/changes (A0 5-run summary, A1 5-run
# summary, paired compare, B4, audit, run1 pertask).
#
# Mirrors finalize-watcher / compare-watcher: fire-and-forget, zero GPU, zero
# sandbox. Fingerprint = mtime+size of inputs; regen only when changed.
# Usage: bash baize_posttrain_baseline_report_watcher.sh [max_wait_seconds]
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
GEN="baize_posttrain_baseline_report_gen.py"
LOG="/tmp/posttrain_baseline_report_watcher.log"
STATE="/tmp/posttrain_baseline_report_watcher.state"
MAX_WAIT="${1:-172800}"   # 48h default
POLL=600
INPUTS=(
  "baseline_measurement_audit.json"
  "baseline_B4_execution_determinism.json"
  "baseline_A0_base_5run_summary.json"
  "baseline_A1_sft_5run_summary.json"
  "baseline_A0_vs_A1_paired_compare.json"
  "baseline_A0_base_run1_pertask.json"
)
# also pick up interim A0 summaries (fallback inputs)
INTERIM_GLOB="baseline_A0_base_*run_interim_summary.json"

echo "[$(date '+%F %T')] === baseline report-watcher START (max_wait=${MAX_WAIT}s poll=${POLL}s) ===" | tee -a "$LOG"

fingerprint() {
  local fp=""
  for f in "${INPUTS[@]}"; do
    if [ -f "$f" ]; then
      fp+="${f}:$(stat -c '%s %Y' "$f" 2>/dev/null)|"
    else
      fp+="${f}:MISSING|"
    fi
  done
  # include interim summaries
  for f in $INTERIM_GLOB; do
    [ -f "$f" ] && fp+="${f}:$(stat -c '%s %Y' "$f" 2>/dev/null)|"
  done
  echo -n "$fp"
}

PREV_FP="$(cat "$STATE" 2>/dev/null || echo '')"
ELAPSED=0
while [ "$ELAPSED" -lt "$MAX_WAIT" ]; do
  FP="$(fingerprint)"
  if [ "$FP" != "$PREV_FP" ]; then
    echo "[$(date '+%F %T')] input fingerprint changed -> regenerating report" | tee -a "$LOG"
    if python3 "$GEN" >>"$LOG" 2>&1; then
      echo "[$(date '+%F %T')] report regen OK" | tee -a "$LOG"
      echo -n "$FP" > "$STATE"
      PREV_FP="$FP"
    else
      echo "[$(date '+%F %T')] report regen FAILED (rc=$?) -- will retry next poll" | tee -a "$LOG"
    fi
  else
    echo "[$(date '+%F %T')] no change (${ELAPSED}s) -- A0sum=$([ -f baseline_A0_base_5run_summary.json ] && echo Y || echo N) A1sum=$([ -f baseline_A1_sft_5run_summary.json ] && echo Y || echo N) cmp=$([ -f baseline_A0_vs_A1_paired_compare.json ] && echo Y || echo N)" | tee -a "$LOG"
  fi
  sleep "$POLL"
  ELAPSED=$((ELAPSED + POLL))
done
echo "[$(date '+%F %T')] max_wait reached, exiting" | tee -a "$LOG"
