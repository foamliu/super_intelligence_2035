#!/bin/bash
# run_B_zh_r2_regrade_gap.sh — B_zh_r2 regrade "gap-grabber" (method A, 2026-11-10 21:3x user order).
#
# REPLACES run_B_zh_r2_regrade_wait.sh (wait-for-orchestrator-exit). The orchestrator
# (run_think_lang_ablation.sh) runs rounds in the FOREGROUND serially; between rounds
# there is only: score grep + trace copy (~430MB) + probe_quota → usually tens of seconds
# (up to 5 min when quota exhausted). This script GRABS that inter-round gap to run the
# regrade, and YIELDS the instant a new round appears.
#
# SAFETY: during a gap no run_cline_script is active → the 4 shared sandbox workdirs are
# free → regrade (eval-only, uses 2 of 4 workdirs) cannot pollute a round. The risk is only
# that a new round starts mid-regrade; the yield-guard kills the regrade within ~60s of that.
# A new round's generation phase (cline LLM calls) does not touch the sandbox workdirs
# immediately, so a ≤60s overlap endangers only the (discarded) regrade results, not the new
# round. This is the user-accepted tradeoff vs waiting ~2 days for the orchestrator to exit.
#
# Logic (ZHULONG_TASK.md §一):
#   1. loop
#   2. GAP detect: !pgrep '^bash scripts/run_cline_script' AND !pgrep 'run_eval.py'
#      → sleep 20 re-verify (no new round for 20s = real gap)
#   3. exclusive launch: bash run_B_zh_r2_regrade.sh -p 2 (background, own process group, record PID)
#   4. yield-guard: every 60s check pgrep '^bash scripts/run_cline_script'; if appears
#      → kill -TERM <regrade_pgid>, log "ABORT: new round appeared at <ts>, gap too short"
#      → back to step 1 (this attempt counts as one used chance)
#      → if regrade finished before any new round → DONE (success)
#   5. 3 chances all aborted → DOWNGRADE to B: wait for orchestrator PID to exit, then run
#      regrade once (full, no yield). Log "upgraded-to-B: 3 gaps too short".
#
# 🚫 Red lines: no `pkill -f run_cline_script`, no kill orchestrator/worker, no `exec -a`
#    name spoofing (orchestrator's own `pkill '^bash scripts/run_cline_script'` cleanup
#    would catch a spoofed name — keep the regrade cmdline honest).
#
# Launch (detached, survives ssh detach):
#   setsid bash run_B_zh_r2_regrade_gap.sh > /tmp/regrade_B_zh_r2_gap.log 2>&1 < /dev/null &
set -uo pipefail

RUN_DIR=/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
REGRADE_SCRIPT="$RUN_DIR/run_B_zh_r2_regrade.sh"
REGRADE_LOG=/tmp/regrade_B_zh_r2.log
GAP_LOG=/tmp/regrade_B_zh_r2_gap.log
STATUS_FILE=/tmp/regrade_B_zh_r2_STATUS   # written on terminal state for next agent wake
ORCH_PATTERN='run_think_lang_ablation\.sh'
ROUND_PATTERN='^bash scripts/run_cline_script'
EVAL_PATTERN='run_eval\.py'
MAX_CHANCES=3

ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" | tee -a "$GAP_LOG"; }

# Real-process detectors. Patterns are anchored / specific so they do NOT match this gap
# script nor the opencode agent (whose cmdline embeds the task book mentioning these strings).
# pgrep never matches itself.
round_active()  { pgrep -f "$ROUND_PATTERN"  >/dev/null 2>&1; }
eval_active()   { pgrep -f "$EVAL_PATTERN"   >/dev/null 2>&1; }
orch_active()   { pgrep -f "$ORCH_PATTERN"   >/dev/null 2>&1; }

write_status() { # args: state [extra]
  echo "state=$1 ts=$(ts) $2" > "$STATUS_FILE"
}

# Launch regrade in its own session (process group) so we can kill the whole tree.
# Returns 0 if regrade completed, 1 if aborted (new round appeared).
run_regrade_with_yield_guard() {
  log "  launching regrade (-p 2) in own pgroup -> $REGRADE_LOG"
  setsid bash "$REGRADE_SCRIPT" -p 2 > "$REGRADE_LOG" 2>&1 &
  local rpid=$!
  local pgid=$rpid   # setsid makes the child a new group leader → pgid == child pid
  log "  regrade PID=$rpid PGID=$pgid"

  local aborted=0
  while kill -0 "$rpid" 2>/dev/null; do
    sleep 60
    if kill -0 "$rpid" 2>/dev/null && round_active; then
      log "  ABORT: new round appeared at $(ts), gap too short -> kill -TERM -$pgid"
      kill -TERM -- "-$pgid" 2>/dev/null || kill -TERM "$rpid" 2>/dev/null
      sleep 5
      kill -KILL -- "-$pgid" 2>/dev/null || kill -KILL "$rpid" 2>/dev/null
      aborted=1
      break
    fi
  done
  wait "$rpid" 2>/dev/null
  local rc=$?
  if [[ $aborted -eq 1 ]]; then
    log "  regrade ABORTED (yielded to new round; rc after kill=$rc)"
    return 1
  fi
  log "  regrade FINISHED rc=$rc"
  return 0
}

# Extract gate info (n_tasks denominator + pass%) from regrade log.
gate_snippets() {
  grep -oE 'pass \([0-9.]+%\)|[0-9]+/158 pass' "$REGRADE_LOG" 2>/dev/null | tail -5
}
n_tasks_from_log() {
  # pull the "/NN" denominator from the "X/NN pass" summary line
  grep -oE '[0-9]+/[0-9]+ pass' "$REGRADE_LOG" 2>/dev/null | tail -1 | grep -oE '/[0-9]+' | tr -d '/'
}

log "=== B_zh_r2 regrade GAP-GRABBER START $(ts) ==="
log "strategy: grab inter-round gap + yield on new round; max $MAX_CHANCES chances; then downgrade to wait-orchestrator-exit"
log "regrade script: $REGRADE_SCRIPT  regrade log: $REGRADE_LOG"
write_status "running" "phase=gap-grab"

# Kill the voided standalone waiter (run_B_zh_r2_regrade_wait.sh) — superseded by this script.
OLD_WAITER=$(pgrep -f 'run_B_zh_r2_regrade_wait\.sh' | head -1)
if [[ -n "$OLD_WAITER" ]]; then
  log "killing voided old waiter PID=$OLD_WAITER (superseded by gap-grabber)"
  kill -TERM "$OLD_WAITER" 2>/dev/null || true
fi

chances_used=0
while [[ $chances_used -lt $MAX_CHANCES ]]; do
  log "--- looking for a gap (chances_used=$chances_used/$MAX_CHANCES) ---"
  # Wait until no round and no eval is active.
  while round_active || eval_active; do
    sleep 20
  done
  # Re-verify after 20s: if a new round started, this is not a real gap — keep waiting.
  sleep 20
  if round_active || eval_active; then
    log "  gap vanished during 20s re-verify; keep waiting (no chance consumed yet)"
    continue
  fi
  log "  gap confirmed (no round, no eval for 20s) — committing chance $((chances_used+1))/$MAX_CHANCES"
  chances_used=$((chances_used+1))
  run_regrade_with_yield_guard
  if [[ $? -eq 0 ]]; then
    log "=== B_zh_r2 regrade COMPLETED via gap (chance $chances_used) ==="
    nt=$(n_tasks_from_log)
    snaps=$(gate_snippets)
    log "  gate: n_tasks_denominator=${nt:-<none>}  snippets: $snaps"
    if [[ "$nt" == "158" ]]; then
      log "  GATE PASS: n_tasks==158"
      write_status "done" "chances=$chances_used n_tasks=$nt method=gap snippets=\"$snaps\""
    else
      log "  GATE FAIL: n_tasks=${nt:-<missing>} != 158 → BLOCKED, do not backfill"
      write_status "blocked" "chances=$chances_used n_tasks=${nt:-<missing>} method=gap reason=n_tasks!=158"
    fi
    exit 0
  fi
  log "  chance $chances_used aborted (gap too short); will look for next gap"
done

# ---- Downgrade to B: wait for orchestrator to exit, then run regrade once (full, no yield) ----
log "=== $MAX_CHANCES chances exhausted; DOWNGRADE to wait-orchestrator-exit (method B) ==="
log "upgraded-to-B: 3 gaps too short"
write_status "running" "phase=downgraded-B reason=3-gaps-too-short"

log "  waiting for orchestrator ($ORCH_PATTERN) to exit..."
while orch_active; do
  sleep 300
done
log "  orchestrator gone; final cleanup wait for any tail round/eval"
while round_active || eval_active; do
  sleep 60
done
log "  launching FINAL regrade (full, -p 2, no yield) -> $REGRADE_LOG"
bash "$REGRADE_SCRIPT" -p 2 > "$REGRADE_LOG" 2>&1
rc=$?
log "  final regrade rc=$rc"
nt=$(n_tasks_from_log)
snaps=$(gate_snippets)
log "  gate: n_tasks_denominator=${nt:-<none>}  snippets: $snaps"
if [[ "$nt" == "158" ]]; then
  log "  GATE PASS: n_tasks==158"
  write_status "done" "chances=$chances_used n_tasks=$nt method=downgraded-B snippets=\"$snaps\""
else
  log "  GATE FAIL: n_tasks=${nt:-<missing>} != 158 → BLOCKED, do not backfill"
  write_status "blocked" "chances=$chances_used n_tasks=${nt:-<missing>} method=downgraded-B reason=n_tasks!=158"
fi
log "=== B_zh_r2 regrade GAP-GRABBER END $(ts) ==="
