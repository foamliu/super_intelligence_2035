#!/usr/bin/env bash
# _full_7x15_launcher.sh — Terminal-Bench 2.0 full evaluation (R472, 2026-10-24).
#
# Only 15 of 89 TB task images are locally cached (MITM proxy blocks Docker Hub).
# Creates a filtered dataset of the 15 available tasks, then runs all 7 harnesses
# sequentially via launch_tb_7way.sh (which handles gw_proxy, oracle check, etc.).
#
# Total: 7 harnesses × 15 tasks = 105 trials (pass@1, k=1, concurrency=1).
# ETA: ~17 hours (sequential, ~10min/task).
#
# Usage:  setsid bash _full_7x15_launcher.sh > /tmp/tb_full_7x15.log 2>&1 < /dev/null &
set -euo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"

# --- Get API key ---
# keys.txt uses FULL-WIDTH colon (：); awk -F'：' splits on it.
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[full7x15] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
[[ -n "${TB_API_KEY:-}" ]] || { echo "[full7x15] FATAL: TB_API_KEY empty"; exit 1; }
cd "$TB_DIR" || { echo "[full7x15] FATAL: cd failed"; exit 2; }

# --- Kill any stale gw_proxy on 9090/9091 (from previous runs) ---
echo "[full7x15] cleaning stale gw_proxy ..."
for port in 9090 9091; do
    pids=$( (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep ":${port} " | grep -oP 'pid=\K\d+' | sort -u || true )
    for pid in $pids; do
        echo "[full7x15] killing gw_proxy on port ${port} (PID ${pid})"
        kill "$pid" 2>/dev/null || true
    done
done
sleep 2

# --- Create filtered dataset with only tasks that have local Docker images ---
FULL_DATASET="$(mktemp -d -t tb_full_dataset_XXXXXX)"
echo "[full7x15] creating filtered dataset at ${FULL_DATASET}"
sg docker -c 'for d in ~/terminal-bench/*/; do t=$(basename "$d"); docker image inspect alexgshaw/$t:20251031 >/dev/null 2>&1 && echo "$t"; done' 2>/dev/null | while read -r t; do
    ln -sf "${HOME}/terminal-bench/${t}" "${FULL_DATASET}/${t}"
done
N_TASKS=$(ls -d "${FULL_DATASET}"/*/ 2>/dev/null | wc -l)
echo "[full7x15] ${N_TASKS} tasks with local images"
echo "[full7x15] task list:"
ls "${FULL_DATASET}" 2>/dev/null | sort | sed 's/^/  /'

echo "[full7x15] starting full 7×${N_TASKS} at $(date '+%F %T') ..."
echo "[full7x15] logging to /tmp/tb_full_7x15.log"

# --- Run via launch_tb_7way.sh in full mode with filtered dataset ---
# launch_tb_7way.sh handles: gw_proxy startup, oracle check, sequential 7-harness run.
# We override TB_TASKS_DIR to point at our filtered 15-task dataset.
exec sg docker -c "
    export TB_API_KEY='${TB_API_KEY}'
    export PATH='/home/app.e0031982/.local/bin:\${PATH}'
    export TB_TASKS_DIR='${FULL_DATASET}'
    bash launch_tb_7way.sh
"
