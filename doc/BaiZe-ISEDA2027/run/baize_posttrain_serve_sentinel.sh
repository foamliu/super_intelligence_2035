#!/usr/bin/env bash
# baize_posttrain_serve_sentinel.sh
# =============================================================================
# BaiZe Stage(ii) post-train : vLLM serve-health sentinel + auto-restart guard
# -----------------------------------------------------------------------------
# Problem : the 2026-11-10 17:10 user order requires GPU 5/6/7 to be occupied
#   by vLLM serve MiniCPM5-2B (ports 8097/8096/8095) until the EDA sandbox
#   tunnel recovers.  If any serve process crashes, the GPU becomes free and
#   may be reallocated.  The agent only checks serve health during its ~15-min
#   wake cycle, leaving a gap where a crashed serve goes unnoticed.
# Solution: poll all 5 serve endpoints every N seconds.  For GPU 5/6/7
#   placeholder serves (8097/8096/8095), auto-restart on crash using the exact
#   command from the 17:10 operator note.  GPU 4 (:8098) and root GPU 0-3
#   (:8099) are check-only — never restarted by this sentinel.
#
# Hard guards:
#   * NEVER touches GPU 0-3 (root SGLang :8099).
#   * Only restarts GPU 5/6/7 serves (the 17:10 placeholder serves).
#   * Before restart, kills residual GPU processes.
#
# Usage:
#   bash baize_posttrain_serve_sentinel.sh --check-once
#   bash baize_posttrain_serve_sentinel.sh --status
#   bash baize_posttrain_serve_sentinel.sh --dry-run
#   bash baize_posttrain_serve_sentinel.sh --watch
#   bash baize_posttrain_serve_sentinel.sh --watch --auto-restart
#   nohup bash baize_posttrain_serve_sentinel.sh --watch --auto-restart \
#     > /tmp/posttrain_serve_sentinel.nohup 2>&1 &
#
# Env: INTERVAL CURL_TIMEOUT VLLM_VENV MODEL_PATH LOG SENTINEL_FLAG RESTART_GPU4
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- config (env-overridable) ----------
INTERVAL="${INTERVAL:-120}"
CURL_TIMEOUT="${CURL_TIMEOUT:-5}"
VLLM_VENV="${VLLM_VENV:-/tmp/vllm_venv/bin/python}"
MODEL_PATH="${MODEL_PATH:-/nas_data/app.e0031982/models/MiniCPM5-2B}"
LOG="${LOG:-/tmp/posttrain_serve_sentinel.log}"
SENTINEL_FLAG="${SENTINEL_FLAG:-/tmp/posttrain_serve_sentinel.flag}"
RESTART_GPU4="${RESTART_GPU4:-0}"

# ---------- endpoint table: GPU|PORT|SERVED_NAME|RESTARTABLE ----------
ENDPOINTS=(
  "5|8097|minicpm5-2b-gpu5|1"
  "6|8096|minicpm5-2b-gpu6|1"
  "7|8095|minicpm5-2b-gpu7|1"
  "4|8098|minicpm5-2b|0"
  "0|8099|qwen3.8-27b|0"
)

MODE=""
AUTO_RESTART=0

# ---------- helpers ----------
ok(){ printf '\033[32m[OK]\033[0m %s\n' "$*"; }
no(){ printf '\033[31m[NO]\033[0m %s\n' "$*" >&2; }
wa(){ printf '\033[33m[WA]\033[0m %s\n' "$*"; }
info(){ printf '\033[36m[--]\033[0m %s\n' "$*"; }
log(){ printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

usage(){
  cat <<'EOF'
baize_posttrain_serve_sentinel.sh — vLLM serve-health sentinel + auto-restart
  --check-once            single health probe of all 5 endpoints, exit 0
  --status                print config + sentinel flag state, exit 0
  --dry-run               print config + single probe, never restart, exit 0
  --watch                 poll every INTERVAL s (foreground), alert-only
  --watch --auto-restart  poll + auto-restart GPU5/6/7 serves on crash
  --help                  this message
Env: INTERVAL CURL_TIMEOUT VLLM_VENV MODEL_PATH LOG SENTINEL_FLAG RESTART_GPU4
EOF
}

parse_args(){
  while [ $# -gt 0 ]; do
    case "$1" in
      --check-once)   MODE="check-once" ;;
      --status)       MODE="status" ;;
      --dry-run)      MODE="dry-run" ;;
      --watch)        MODE="watch" ;;
      --auto-restart) AUTO_RESTART=1 ;;
      --help|-h)      usage; exit 0 ;;
      *) no "unknown arg: $1"; usage; exit 1 ;;
    esac
    shift
  done
  if [ -z "$MODE" ]; then usage; exit 1; fi
}

# ---------- core: probe one endpoint ----------
probe_endpoint(){
  local port="$1" resp
  resp=$(curl -s -m "$CURL_TIMEOUT" "http://localhost:${port}/v1/models" 2>/dev/null || true)
  [ -n "$resp" ] && echo "$resp" | grep -q '"object":"list"'
}

# ---------- core: restart a serve on a given GPU ----------
restart_serve(){
  local gpu="$1" port="$2" name="$3"

  # HARD GUARD: never restart GPU 0-3 (root)
  if [ "$gpu" -ge 0 ] && [ "$gpu" -le 3 ]; then
    no "HARD GUARD: refusing to restart GPU ${gpu} (root SGLang)"
    log "HARD-GUARD reject GPU${gpu} port${port}"
    return 1
  fi
  # GPU 4: only restart if RESTART_GPU4=1
  if [ "$gpu" -eq 4 ] && [ "$RESTART_GPU4" -eq 0 ]; then
    wa "GPU 4 (port ${port}) down but RESTART_GPU4=0 — alert only"
    log "GPU4 down, RESTART_GPU4=0, alert-only"
    return 1
  fi

  # Step 1: kill residual processes on this GPU
  local residual_pids
  residual_pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader -i "$gpu" 2>/dev/null | tr -d ' ' || true)
  if [ -n "$residual_pids" ]; then
    wa "GPU ${gpu} residual PIDs: ${residual_pids} — killing"
    log "GPU${gpu} residual: ${residual_pids}"
    for pid in $residual_pids; do kill -9 "$pid" 2>/dev/null || true; done
    sleep 3
  fi

  # Step 2: launch vLLM serve (exact 17:10 command template)
  info "Restarting vLLM serve GPU ${gpu} port ${port} name ${name}"
  log "RESTART GPU${gpu} port${port} name=${name}"
  CUDA_VISIBLE_DEVICES="$gpu" \
    HF_HOME=/tmp/hf_home TRANSFORMERS_CACHE=/tmp/hf_home HF_MODULES_CACHE=/tmp/hf_home/modules \
    nohup "$VLLM_VENV" -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_PATH" \
    --served-model-name "$name" --host 0.0.0.0 --port "$port" \
    --trust-remote-code --gpu-memory-utilization 0.85 --max-model-len 32768 \
    > "/tmp/vllm_gpu${gpu}.log" 2>&1 &
  log "RESTART launched GPU${gpu} PID=$!"

  # Step 3: wait up to 120s for serve to come up
  local waited=0
  while [ "$waited" -lt 120 ]; do
    sleep 10; waited=$((waited + 10))
    if probe_endpoint "$port"; then
      ok "GPU ${gpu} (port ${port}) back UP after ${waited}s"
      log "GPU${gpu} port${port} UP after ${waited}s"
      return 0
    fi
  done
  no "GPU ${gpu} (port ${port}) FAILED to come up in 120s — see /tmp/vllm_gpu${gpu}.log"
  log "GPU${gpu} port${port} FAILED 120s"
  return 1
}

# ---------- core: probe all endpoints ----------
probe_all(){
  local all_healthy=1 restartable_down=0
  printf '%-6s %-8s %-22s %-10s %-12s\n' "GPU" "PORT" "SERVED_NAME" "HEALTH" "ACTION"
  printf '%-6s %-8s %-22s %-10s %-12s\n' "---" "----" "------------" "------" "------"
  for ep in "${ENDPOINTS[@]}"; do
    IFS='|' read -r gpu port name restartable <<< "$ep"
    local health="DOWN" action="none"
    if probe_endpoint "$port"; then
      health="UP"
    else
      health="DOWN"; all_healthy=0
      if [ "$restartable" -eq 1 ]; then
        restartable_down=1
        [ "$AUTO_RESTART" -eq 1 ] && action="RESTART" || action="ALERT"
      else
        action="ALERT-ONLY"
      fi
    fi
    printf '%-6s %-8s %-22s %-10s %-12s\n' "$gpu" "$port" "$name" "$health" "$action"
  done
  if [ "$all_healthy" -eq 1 ]; then ok "All 5 serve endpoints UP"; fi

  # Perform restarts if auto-restart enabled
  if [ "$AUTO_RESTART" -eq 1 ] && [ "$restartable_down" -eq 1 ]; then
    for ep in "${ENDPOINTS[@]}"; do
      IFS='|' read -r gpu port name restartable <<< "$ep"
      if [ "$restartable" -eq 1 ] && ! probe_endpoint "$port"; then
        wa "GPU ${gpu} (port ${port}) DOWN — initiating restart"
        restart_serve "$gpu" "$port" "$name" || true
      fi
    done
  fi
  return 0
}

# ---------- modes ----------
do_check_once(){ probe_all; }

do_status(){
  info "Config:"
  printf '  INTERVAL=%s CURL_TIMEOUT=%s\n' "$INTERVAL" "$CURL_TIMEOUT"
  printf '  VLLM_VENV=%s\n' "$VLLM_VENV"
  printf '  MODEL_PATH=%s\n' "$MODEL_PATH"
  printf '  LOG=%s\n' "$LOG"
  printf '  RESTART_GPU4=%s AUTO_RESTART=%s\n' "$RESTART_GPU4" "$AUTO_RESTART"
  echo ""
  if [ -f "$SENTINEL_FLAG" ]; then
    info "Sentinel flag: $(cat "$SENTINEL_FLAG" 2>/dev/null || echo '(empty)')"
  else
    wa "No sentinel flag (not running in watch mode)"
  fi
  echo ""
  info "Running sentinel processes:"
  ps -eo pid=,ppid=,etimes=,args= | grep 'serve_sentinel' | grep -v grep || info "(none)"
  echo ""
  info "Endpoint health:"
  do_check_once
}

do_dry_run(){
  info "DRY-RUN — probe only, NEVER restart"
  do_status
}

do_watch(){
  info "Watch mode (INTERVAL=${INTERVAL}s AUTO_RESTART=${AUTO_RESTART})"
  echo "$$" > "$SENTINEL_FLAG"
  log "sentinel PID=$$ AUTO_RESTART=$AUTO_RESTART INTERVAL=$INTERVAL"
  local poll=0
  while true; do
    poll=$((poll + 1))
    log "poll #${poll}"
    probe_all || true
    echo "poll=${poll} $(date '+%H:%M:%S')" > "$SENTINEL_FLAG"
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

