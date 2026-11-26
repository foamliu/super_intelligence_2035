#!/usr/bin/env bash
# _auto_transition_7x89.sh — Wait for 89/89 images, stop v2 serial run,
# then launch 7x89 concurrent evaluation.
#
# Created R478 (2026-10-24) to automate the transition from v2 serial to
# 7-way concurrent per user directive.
#
# Usage:
#   setsid sg docker -c "bash _auto_transition_7x89.sh" \
#       > /tmp/tb_auto_transition.log 2>&1 < /dev/null &

set -uo pipefail

REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
LOG="/tmp/tb_auto_transition.log"

echo "[transition] START $(date '+%F %T')"

# --- Phase 1: Wait for all 89 images ---
echo "[transition] Phase 1: Waiting for 89/89 images ..."
WAIT_COUNT=0
while true; do
    PRESENT=$(docker images --format '{{.Repository}}' | grep -c alexgshaw)
    if [[ "$PRESENT" -ge 89 ]]; then
        echo "[transition] All 89 images present! ($PRESENT)"
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [[ $WAIT_COUNT -ge 120 ]]; then  # 120 × 30s = 60 min max
        echo "[transition] TIMEOUT after 60 min. Only $PRESENT/89 images."
        echo "[transition] Missing:"
        for d in ~/terminal-bench/*/; do
            t=$(basename "$d")
            docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1 || echo "  $t"
        done
        exit 1
    fi
    echo "[transition] $PRESENT/89 images (wait ${WAIT_COUNT}/120) ..."
    sleep 30
done

# --- Phase 2: Stop v2 serial run + its gw_proxy ---
echo "[transition] Phase 2: Stopping v2 serial run ..."

# Kill v2 launcher process tree
V2_PID=$(pgrep -f '_full_7x15_v2_launcher.sh' | head -1)
if [[ -n "$V2_PID" ]]; then
    echo "[transition] Killing v2 launcher (PID=$V2_PID) ..."
    kill "$V2_PID" 2>/dev/null
    sleep 3
    kill -9 "$V2_PID" 2>/dev/null || true
    # Kill any child harbor processes from v2
    pkill -f 'harbor.*tb_full_v2' 2>/dev/null || true
    pkill -f 'harbor.*jobs_opencode' 2>/dev/null || true
    pkill -f 'harbor.*jobs_claude' 2>/dev/null || true
    pkill -f 'harbor.*jobs_deepseek' 2>/dev/null || true
    pkill -f 'harbor.*jobs_pi' 2>/dev/null || true
    sleep 2
    echo "[transition] v2 stopped."
else
    echo "[transition] v2 launcher not found (may have already finished)."
fi

# Kill v2's gw_proxy (ports 9090/9091) — they conflict with 7x89 launcher
pkill -f 'gw_proxy.*9090' 2>/dev/null || true
pkill -f 'gw_proxy.*9091' 2>/dev/null || true
pkill -f 'gw_proxy_dsh' 2>/dev/null || true
sleep 3
echo "[transition] gw_proxy (9090/9091) stopped."

# Clean up any lingering docker containers from v2
echo "[transition] Cleaning up v2 docker containers ..."
docker ps -q --filter "name=tb_full_v2" 2>/dev/null | xargs -r docker rm -f 2>/dev/null || true
# Also stop any env containers from v2's opencode run
for c in $(docker ps --format '{{.Names}}' 2>/dev/null | grep -E '__env-main-1$'); do
    # Only kill containers that are NOT from 7x89 (which hasn't started yet)
    docker rm -f "$c" 2>/dev/null || true
done
sleep 5
echo "[transition] Cleanup done. Remaining containers: $(docker ps -q 2>/dev/null | wc -l)"

# --- Phase 3: Launch 7x89 concurrent ---
echo "[transition] Phase 3: Launching 7x89 concurrent ..."
echo "[transition] Resource check: CPUs=$(nproc), RAM=$(free -h | awk '/^Mem:/ {print $7}') available, Load=$(uptime | awk -F'load average:' '{print $2}')"

cd "$TB_DIR" || { echo "[transition] FATAL: cd failed"; exit 2; }

setsid bash "$TB_DIR/_full_7x89_concurrent_launcher.sh" \
    > /tmp/tb_7x89_concurrent.log 2>&1 < /dev/null &
LAUNCH_PID=$!
echo "[transition] 7x89 launcher started PID=$LAUNCH_PID"
echo "[transition] Log: /tmp/tb_7x89_concurrent.log"
sleep 10
echo "[transition] === Launcher output (first 20 lines) ==="
head -20 /tmp/tb_7x89_concurrent.log 2>/dev/null
echo "[transition] DONE at $(date '+%F %T')"
