#!/usr/bin/env bash
# baize_posttrain_serve_teardown.sh — R165: stop placeholder vLLM serve to free GPU
#
# Purpose: Per 2026-11-10 17:10 user order, GPU 5/6/7 each run a placeholder
#   vLLM serve MiniCPM5-2B (ports 8097/8096/8095) to prevent GPU reallocation
#   while the EDA sandbox tunnel (10.129.32.75:8667) is firewalled CLOSED.
#   When the sandbox recovers and Phase 1 baseline eval completes, Phase 2 SFT
#   needs GPU 6-7 free — but no existing script tears down the placeholder serve
#   (the SFT/RL sub-scripts only have a GPU-busy GUARD that refuses to launch;
#   they never kill any serve, by discipline). This helper fills that gap.
#
# Safety rules (red lines):
#   * NEVER touches GPU 0-3 / port 8099 (root SGLang Qwen3.8-27B) — hard guard.
#   * Default scope = placeholder serve on GPU 5/6/7 (ports 8097/8096/8095) only.
#   * --gpu4  also stops the Phase-1 eval serve on GPU 4 (port 8098) — use only
#     after Phase 1 eval is done and Phase 3 RL needs GPU 4.
#   * --all   = GPU 5/6/7 + GPU 4 (all four posttrain serves). Still never 0-3.
#   * Identifies processes by PORT (robust: survives PID reuse / model-name drift).
#   * SIGTERM first, then SIGKILL after grace period; verifies VRAM freed.
#
# Usage:
#   bash baize_posttrain_serve_teardown.sh --dry-run       # show what would be killed
#   bash baize_posttrain_serve_teardown.sh                 # stop GPU 5/6/7 placeholders
#   bash baize_posttrain_serve_teardown.sh --gpu4          # also stop GPU 4 (post Phase1)
#   bash baize_posttrain_serve_teardown.sh --all           # stop all 4 posttrain serves
#   bash baize_posttrain_serve_teardown.sh --status        # show serve occupancy map
#
# Env: GRACE=15 (SIGTERM->SIGKILL seconds)
# Exit: 0 if all targeted serves stopped (or already gone); 1 if any failed.
set -uo pipefail

GRACE="${GRACE:-15}"

# ---- targets: port -> gpu index (posttrain serves only; 8099 is ROOT, excluded) ----
PORTS_PLACE=(8097 8096 8095)   # GPU 5,6,7 placeholders
GPUS_PLACE=(5   6   7)
PORT_GPU4=8098                 # GPU 4 Phase-1 eval serve
GPU4_IDX=4
ROOT_PORT=8099                 # GPU 0-3 root SGLang — NEVER touch (guard only)

DRY_RUN=0; DO_GPU4=0; DO_ALL=0; STATUS_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --gpu4)    DO_GPU4=1 ;;
    --all)     DO_ALL=1; DO_GPU4=1 ;;
    --status)  STATUS_ONLY=1 ;;
    -h|--help) sed -n '2,28p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

ok(){ printf '  \033[32mPASS\033[0m %s\n' "$1"; }
no(){ printf '  \033[31mFAIL\033[0m %s\n' "$1" >&2; }
wa(){ printf '  \033[33mWARN\033[0m %s\n' "$1"; }
info(){ printf '  \033[36m[--]\033[0m %s\n' "$1"; }
hr(){ printf '  %s\n' "$(printf -- '-%.0s' $(seq 1 60))"; }

# find_pids_by_port <port> -> echo space-separated PIDs of vllm api_server on that port
# Self-match protection: pgrep -f can match its OWN command line (the pattern
# string appears in the pgrep invocation). We filter out any matched PID whose
# cmdline contains pgrep/grep or this script's name, keeping only real vllm
# api_server processes.
find_pids_by_port(){
  local port="$1"
  pgrep -f "vllm.entrypoints.openai.api_server.*--port ${port}" 2>/dev/null |
  while read -r pid; do
    ps -o args= -p "$pid" 2>/dev/null | grep -qvE 'pgrep|grep|baize_posttrain_serve_teardown' && printf '%s ' "$pid"
  done | sed 's/ $//; s/  */ /g; s/^ //'
}

# vram_used <gpu_idx> -> MiB (integer) or empty on failure
vram_used(){
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$1" 2>/dev/null | tr -d ' '
}

# stop_port <port> <gpu_idx> <label>
stop_port(){
  local port="$1" gi="$2" label="$3"
  local pids; pids=$(find_pids_by_port "$port")
  local before; before=$(vram_used "$gi")
  if [ -z "$pids" ]; then
    local after; after=$(vram_used "$gi")
    if [ -n "$after" ] && [ "$after" -lt 1024 ]; then
      ok "$label (port $port / GPU $gi): no serve process, VRAM already free (${after} MiB)"
    else
      wa "$label (port $port / GPU $gi): no serve process on port, but GPU $gi still shows ${after:-?} MiB — residual? check nvidia-smi -i $gi"
    fi
    return 0
  fi
  info "$label (port $port / GPU $gi): found PID(s) {$pids}, VRAM=${before:-?} MiB"
  if [ "$DRY_RUN" = 1 ]; then
    wa "DRY-RUN: would SIGTERM+SIGKILL PID(s) {$pids} to free GPU $gi"; return 0; fi
  # SIGTERM each PID and its process group (negative kill)
  local p
  for p in $pids; do
    kill -TERM "$p" 2>/dev/null || true
    kill -TERM "-$p" 2>/dev/null || true
  done
  info "SIGTERM sent; waiting up to ${GRACE}s for graceful exit..."
  local waited=0
  while [ "$waited" -lt "$GRACE" ]; do
    local still=""; still=$(find_pids_by_port "$port")
    [ -z "$still" ] && break
    sleep 1; waited=$((waited+1))
  done
  # SIGKILL stragglers
  local still=""; still=$(find_pids_by_port "$port")
  if [ -n "$still" ]; then
    wa "still alive after ${GRACE}s: {$still} — sending SIGKILL"
    for p in $still; do kill -KILL "$p" 2>/dev/null || true; kill -KILL "-$p" 2>/dev/null || true; done
    sleep 2
  fi
  # verify
  local after; after=$(vram_used "$gi")
  local remaining=""; remaining=$(find_pids_by_port "$port")
  if [ -z "$remaining" ] && [ -n "$after" ] && [ "$after" -lt 1024 ]; then
    ok "$label stopped: GPU $gi VRAM ${before:-?} -> ${after} MiB (freed)"
    return 0
  else
    no "$label: teardown incomplete — port $port proc={$remaining} GPU $gi VRAM=${after:-?} MiB"
    return 1
  fi
}

show_status(){
  echo "===== Posttrain serve occupancy map @ $(date '+%F %T') ====="
  hr
  printf '  %-6s %-6s %-28s %-10s %s\n' "GPU" "PORT" "SERVED-MODEL" "VRAM(MiB)" "PID(s)"
  hr
  local rpids; rpids=$(find_pids_by_port "$ROOT_PORT")
  local rvram; rvram=$(vram_used 0)
  printf '  %-6s %-6s %-28s %-10s %s\n' "0-3" "$ROOT_PORT" "qwen3.8-27b (ROOT)" "${rvram:-?}" "${rpids:-—} [GUARD]"
  local g4pids; g4pids=$(find_pids_by_port "$PORT_GPU4")
  local g4vram; g4vram=$(vram_used "$GPU4_IDX")
  printf '  %-6s %-6s %-28s %-10s %s\n' "$GPU4_IDX" "$PORT_GPU4" "minicpm5-2b" "${g4vram:-?}" "${g4pids:-—}"
  local i
  for i in 0 1 2; do
    local port="${PORTS_PLACE[$i]}" gi="${GPUS_PLACE[$i]}"
    local pids; pids=$(find_pids_by_port "$port")
    local vram; vram=$(vram_used "$gi")
    printf '  %-6s %-6s %-28s %-10s %s\n' "$gi" "$port" "minicpm5-2b-gpu${gi}" "${vram:-?}" "${pids:-—}"
  done
  hr
  echo "  ROOT guard: GPU 0-3 / port $ROOT_PORT — this script NEVER touches them."
  echo
}

# ---- main dispatch ----
if [ "$STATUS_ONLY" = 1 ]; then show_status; exit 0; fi

echo "===== Posttrain serve teardown @ $(date '+%F %T') ====="
[ "$DRY_RUN" = 1 ] && wa "DRY-RUN mode — no processes will be killed"
hr
# hard guard: assert root port never in target list
if echo " ${PORTS_PLACE[*]} $PORT_GPU4 " | grep -qw " $ROOT_PORT "; then
  no "FATAL: root port $ROOT_PORT in target list — aborting (guard)"; exit 1; fi

rc=0
local_i=0
for local_i in 0 1 2; do
  stop_port "${PORTS_PLACE[$local_i]}" "${GPUS_PLACE[$local_i]}" "placeholder-gpu${GPUS_PLACE[$local_i]}" || rc=1
done
if [ "$DO_GPU4" = 1 ]; then
  stop_port "$PORT_GPU4" "$GPU4_IDX" "phase1-eval-gpu4" || rc=1
fi
hr
if [ "$DRY_RUN" = 1 ]; then
  echo "  DRY-RUN complete. Re-run without --dry-run to actually stop the serves."
elif [ "$rc" = 0 ]; then
  ok "all targeted serves stopped / already free. GPUs ready for SFT/RL."
else
  no "one or more serves failed to tear down cleanly — inspect nvidia-smi + logs."
fi
echo
exit "$rc"