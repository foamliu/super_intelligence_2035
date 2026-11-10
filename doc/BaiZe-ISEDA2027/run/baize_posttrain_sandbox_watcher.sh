#!/usr/bin/env bash
# baize_posttrain_sandbox_watcher.sh
# =============================================================================
# BaiZe Stage(ii) post-train : remote EDA sandbox recovery watcher + auto-trigger
# -----------------------------------------------------------------------------
# Problem : the remote EDA sandbox (10.129.32.75:8667) has been firewalled CLOSED
#   for 30+ consecutive wakes, blocking Phase1 eval and Phase3 RL (R1-R4) which
#   depend on code-execution rewards. GPU4 (MiniCPM5-2B serve :8098) and root
#   GPU0-3 (Qwen3.8-27B :8099) are already up, so the ONLY missing piece for
#   Phase1 baseline eval is the sandbox tunnel.
# Solution: poll the sandbox TCP port every N seconds; the instant it opens,
#   (a) stamp a sentinel flag + log entry, (b) optionally auto-launch
#   baize_posttrain_surrogate_pipeline.sh --phase1 in a detached nohup so the
#   baseline eval begins without waiting for the next agent wake.
#
# Discipline:
#   * Never kills any vLLM serve (honours 17:10 GPU-occupation order).
#   * Phase1 only needs sandbox + GPU4 serve + root GPU0-3 -> no GPU contention.
#   * --auto-eval is OFF by default; pass it to enable auto-launch.
#   * Phase1 pipeline itself re-checks the sandbox gate + contam gate + endpoints,
#     so a spurious recovery detection cannot launch an unsafe eval.
#
# Usage:
#   bash baize_posttrain_sandbox_watcher.sh --check-once        # single probe, exit 0=open / 1=closed
#   bash baize_posttrain_sandbox_watcher.sh --status            # show sentinel/log/last-state
#   bash baize_posttrain_sandbox_watcher.sh --dry-run           # print config, probe once, do NOT launch
#   bash baize_posttrain_sandbox_watcher.sh --watch             # poll forever (foreground)
#   bash baize_posttrain_sandbox_watcher.sh --watch --auto-eval # poll forever + auto-launch Phase1 on recovery
#   INTERVAL=120 MAX_POLLS=2880 bash baize_posttrain_sandbox_watcher.sh --watch --auto-eval  # ~48h @120s
#   nohup bash baize_posttrain_sandbox_watcher.sh --watch --auto-eval > /tmp/posttrain_sandbox_watcher.nohup 2>&1 &
#
# Env overrides: SANDBOX_HOST SANDBOX_PORT INTERVAL MAX_POLLS SENTINEL LOG
#                 PIPELINE_PHASE1 AUTO_EVAL_OUT
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- config (env-overridable) ----------
SANDBOX_HOST="${SANDBOX_HOST:-10.129.32.75}"
SANDBOX_PORT="${SANDBOX_PORT:-8667}"
INTERVAL="${INTERVAL:-60}"              # seconds between polls (watch mode)
MAX_POLLS="${MAX_POLLS:-0}"             # 0 = infinite
SENTINEL="${SENTINEL:-/tmp/posttrain_sandbox_recovered.flag}"
LOG="${LOG:-/tmp/posttrain_sandbox_watcher.log}"
PIPELINE_PHASE1="${PIPELINE_PHASE1:-$SCRIPT_DIR/baize_posttrain_surrogate_pipeline.sh}"
AUTO_EVAL_OUT="${AUTO_EVAL_OUT:-/tmp/posttrain_phase1_eval.auto.log}"
PROBE_TIMEOUT="${PROBE_TIMEOUT:-6}"     # seconds per TCP probe

# ---------- mode flags ----------
MODE=""
AUTO_EVAL=0

# ---------- helpers ----------
ok(){ printf '\033[32m[OK]\033[0m %s\n' "$*"; }
no(){ printf '\033[31m[NO]\033[0m %s\n' "$*" >&2; }
wa(){ printf '\033[33m[WA]\033[0m %s\n' "$*"; }
info(){ printf '\033[36m[--]\033[0m %s\n' "$*"; }

usage(){
  cat <<'EOF'
baize_posttrain_sandbox_watcher.sh — sandbox recovery watcher + auto Phase1 trigger
  --check-once        single TCP probe; exit 0 if OPEN, 1 if CLOSED
  --status            print sentinel/log/last probe state, exit 0
  --dry-run           print config + single probe, never launch
  --watch             poll every INTERVAL s (foreground); exit on recovery
  --watch --auto-eval poll + auto-launch pipeline --phase1 on recovery (nohup bg)
  --help              this message
Env: SANDBOX_HOST SANDBOX_PORT INTERVAL MAX_POLLS SENTINEL LOG PIPELINE_PHASE1
     AUTO_EVAL_OUT PROBE_TIMEOUT
EOF
}

parse_args(){
  while [ $# -gt 0 ]; do
    case "$1" in
      --check-once) MODE="check-once" ;;
      --status)     MODE="status" ;;
      --dry-run)    MODE="dry-run" ;;
      --watch)      MODE="watch" ;;
      --auto-eval)  AUTO_EVAL=1 ;;
      --help|-h)    usage; exit 0 ;;
      *) no "unknown arg: $1"; usage; exit 2 ;;
    esac
    shift
  done
  if [ -z "$MODE" ]; then no "no mode given"; usage; exit 2; fi
}

# single TCP probe; returns 0 if OPEN, 1 if CLOSED/timeout
probe_sandbox(){
  if timeout "$PROBE_TIMEOUT" bash -c "exec 3<>/dev/tcp/$SANDBOX_HOST/$SANDBOX_PORT" 2>/dev/null; then
    exec 3>&- 3<&- 2>/dev/null || true
    return 0
  else
    return 1
  fi
}

log_line(){ printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

stamp_recovery(){
  local ts; ts="$(date '+%Y-%m-%dT%H:%M:%S%z')"
  printf '%s sandbox=%s:%s\n' "$ts" "$SANDBOX_HOST" "$SANDBOX_PORT" > "$SENTINEL"
  log_line "RECOVERY DETECTED: $SANDBOX_HOST:$SANDBOX_PORT TCP OPEN (sentinel=$SENTINEL)"
}

launch_phase1(){
  if [ ! -x "$PIPELINE_PHASE1" ] && [ ! -f "$PIPELINE_PHASE1" ]; then
    no "pipeline script not found: $PIPELINE_PHASE1 — skipping auto-launch"
    log_line "AUTO-EVAL SKIP: pipeline missing ($PIPELINE_PHASE1)"
    return 1
  fi
  local out; out="${AUTO_EVAL_OUT%.log}_$(date '+%Y%m%d_%H%M%S').log"
  log_line "AUTO-EVAL: launching $PIPELINE_PHASE1 --phase1 (nohup bg, log=$out)"
  # detached, survives this shell; pipeline itself gates on sandbox/contam/endpoints
  setsid bash "$PIPELINE_PHASE1" --phase1 > "$out" 2>&1 < /dev/null &
  local pid=$!
  disown "$pid" 2>/dev/null || true
  ok "Phase1 auto-launched (pid=$pid, log=$out)"
}

do_check_once(){
  if probe_sandbox; then
    ok "sandbox $SANDBOX_HOST:$SANDBOX_PORT OPEN"
    log_line "PROBE: OPEN"
    return 0
  else
    no "sandbox $SANDBOX_HOST:$SANDBOX_PORT CLOSED (timeout ${PROBE_TIMEOUT}s)"
    log_line "PROBE: CLOSED"
    return 1
  fi
}

do_status(){
  info "config: host=$SANDBOX_HOST port=$SANDBOX_PORT interval=${INTERVAL}s max_polls=${MAX_POLLS}"
  info "sentinel: $SENTINEL -> $([ -f "$SENTINEL" ] && cat "$SENTINEL" || echo '(none — never recovered)')"
  info "log: $LOG -> $([ -f "$LOG" ] && echo "$(wc -l < "$LOG") lines, last: $(tail -1 "$LOG" 2>/dev/null)" || echo '(none)')"
  info "pipeline: $PIPELINE_PHASE1 -> $([ -f "$PIPELINE_PHASE1" ] && echo 'present' || echo 'MISSING')"
  info "auto-eval: $([ "$AUTO_EVAL" = 1 ] && echo ON || echo OFF)"
  if probe_sandbox; then ok "current probe: OPEN"; else no "current probe: CLOSED"; fi
  return 0
}

do_dry_run(){
  info "DRY-RUN: will NOT launch anything"
  info "config: host=$SANDBOX_HOST port=$SANDBOX_PORT interval=${INTERVAL}s max_polls=${MAX_POLLS} auto_eval=$AUTO_EVAL"
  info "sentinel=$SENTINEL log=$LOG pipeline=$PIPELINE_PHASE1"
  if [ ! -f "$PIPELINE_PHASE1" ]; then no "pipeline MISSING (auto-eval would skip)"; else ok "pipeline present"; fi
  if probe_sandbox; then ok "probe: OPEN (recovery would stamp sentinel$( [ "$AUTO_EVAL" = 1 ] && echo ' + launch Phase1'))"; else no "probe: CLOSED (would keep polling)"; fi
  log_line "DRY-RUN ok"
  return 0
}

do_watch(){
  info "WATCH start: host=$SANDBOX_HOST:$SANDBOX_PORT interval=${INTERVAL}s max_polls=${MAX_POLLS} auto_eval=$AUTO_EVAL"
  log_line "WATCH start interval=${INTERVAL}s max_polls=${MAX_POLLS} auto_eval=$AUTO_EVAL"
  local n=0
  while true; do
    n=$((n+1))
    if probe_sandbox; then
      ok "poll #$n: OPEN — recovery!"
      stamp_recovery
      if [ "$AUTO_EVAL" = 1 ]; then launch_phase1 || true; else wa "auto-eval OFF — sentinel stamped, no launch"; fi
      return 0
    else
      no "poll #$n: CLOSED — sleeping ${INTERVAL}s"
      [ $((n % 10)) -eq 0 ] && log_line "still CLOSED (poll #$n)"
    fi
    if [ "$MAX_POLLS" -gt 0 ] && [ "$n" -ge "$MAX_POLLS" ]; then
      wa "reached MAX_POLLS=$MAX_POLLS without recovery — exiting"
      log_line "WATCH end: MAX_POLLS reached (still CLOSED)"
      return 1
    fi
    sleep "$INTERVAL"
  done
}

# ---------- main ----------
parse_args "$@"
case "$MODE" in
  check-once) do_check_once ;;
  status)     do_status ;;
  dry-run)    do_dry_run ;;
  watch)      do_watch ;;
esac
