#!/usr/bin/env bash
# baize_l3_autoqueue.sh — Auto-start L3 Terminal-Bench smoke after MBPP finishes
#
# Waits for port 8083 to be free (MBPP v6 eval complete), checks training health,
# then launches baize_l3_tb_smoke.sh automatically.  This avoids waiting for the
# next agent wakeup cycle (could be hours) before L3 can start.
#
# Usage (on .29):
#   setsid bash baize_l3_autoqueue.sh > /tmp/baize_l3_autoqueue.log 2>&1 < /dev/null &
#
# Safety:
#   - Checks training step time < 7400ms before starting L3
#   - Only one llama-server at a time (waits for port 8083 to be free)
#   - L3 smoke script itself has its own pre-flight checks
#   - Auto-exits if training becomes unhealthy

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMOKE_SCRIPT="${SCRIPT_DIR}/baize_l3_tb_smoke.sh"
PORT=8083
POLL_INTERVAL=30        # seconds between port checks
MAX_WAIT=7200           # max 2 hours waiting
LOG="/tmp/baize_l3_autoqueue.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [autoqueue] $*" | tee -a "$LOG"; }

log "=== L3 Auto-Queue started ==="
log "Waiting for port ${PORT} to become free (MBPP v6 eval to finish)..."

WAITED=0
while (( WAITED < MAX_WAIT )); do
    if ! curl -s -o /dev/null "http://127.0.0.1:${PORT}/health" 2>/dev/null; then
        log "Port ${PORT} is free! (waited ${WAITED}s)"
        break
    fi
    # Also check if the MBPP lm_eval process is still alive
    if ! pgrep -f "lm_eval.*mbpp" >/dev/null 2>&1; then
        log "MBPP lm_eval process gone. Checking port..."
        sleep 5
        if ! curl -s -o /dev/null "http://127.0.0.1:${PORT}/health" 2>/dev/null; then
            log "Port ${PORT} confirmed free after MBPP exit."
            break
        fi
        log "Port still in use despite MBPP exit. Killing stale llama-server on ${PORT}..."
        local_server_pid=$(pgrep -f "llama-server.*--port ${PORT}" 2>/dev/null | head -1)
        if [[ -n "${local_server_pid:-}" ]]; then
            log "Killing stale llama-server PID ${local_server_pid}"
            kill "${local_server_pid}" 2>/dev/null || true
            sleep 3
        fi
        break
    fi
    sleep "$POLL_INTERVAL"
    WAITED=$((WAITED + POLL_INTERVAL))
    if (( WAITED % 300 == 0 )); then
        log "Still waiting... (${WAITED}s elapsed)"
    fi
done

if (( WAITED >= MAX_WAIT )); then
    log "ERROR: Timed out after ${MAX_WAIT}s waiting for port ${PORT}. Exiting."
    exit 1
fi

# --- Training health check ---
log "Checking training health before starting L3..."
TRAIN_PID=$(pgrep -f "baize_xmodel25_decay_v2" 2>/dev/null | head -1)
if [[ -z "$TRAIN_PID" ]]; then
    log "WARNING: Training process not found. Proceeding with caution."
else
    # Read last few lines from training log
    TRAIN_LOG_LINE=$(tail -3 /proc/${TRAIN_PID}/fd/1 2>/dev/null | grep "elapsed time per iteration" | tail -1)
    if [[ -n "$TRAIN_LOG_LINE" ]]; then
        STEP_TIME=$(echo "$TRAIN_LOG_LINE" | grep -oP 'elapsed time per iteration \(ms\): \K\d+')
        log "Training step time: ${STEP_TIME}ms (PID ${TRAIN_PID})"
        if [[ -n "$STEP_TIME" ]] && (( STEP_TIME > 7400 )); then
            log "ERROR: Training step time ${STEP_TIME}ms > 7400ms. Aborting L3 start."
            exit 1
        fi
        log "Training healthy. Proceeding with L3 smoke test."
    else
        log "WARNING: Could not parse training step time. Proceeding with caution."
    fi
fi

# --- Check MBPP results ---
MBPP_RESULTS="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_v6/mbpp"
if [[ -d "$MBPP_RESULTS" ]]; then
    MBPP_JSON=$(find "$MBPP_RESULTS" -name "results.json" -o -name "*.json" 2>/dev/null | head -1)
    if [[ -n "$MBPP_JSON" ]]; then
        log "MBPP results found: ${MBPP_JSON}"
        # Extract pass@1 if available
        MBPP_SCORE=$(python3 -c "
import json, sys
try:
    d = json.load(open('$MBPP_JSON'))
    r = d.get('results', {})
    for k, v in r.items():
        if 'pass' in str(v).lower() or 'mbpp' in k.lower():
            for mk, mv in v.items():
                if isinstance(mv, (int, float)):
                    print(f'{k}.{mk}={mv}')
except: pass
" 2>/dev/null)
        log "MBPP scores: ${MBPP_SCORE:-N/A}"
    fi
fi

# --- Launch L3 smoke test ---
log "=== Starting L3 Terminal-Bench smoke test ==="
log "Command: bash ${SMOKE_SCRIPT}"
bash "$SMOKE_SCRIPT" 2>&1 | tee -a "$LOG"
RC=$?
log "=== L3 smoke test finished (exit code: ${RC}) ==="

# --- Results ---
RESULTS_FILE="${SCRIPT_DIR}/baize_l3_tb_smoke_results/results_summary.txt"
if [[ -f "$RESULTS_FILE" ]]; then
    log "=== L3 Results Summary ==="
    cat "$RESULTS_FILE" | tee -a "$LOG"
fi

log "=== L3 Auto-Queue complete ==="
exit $RC
