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

export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"

# --- Get API key (keys.txt uses FULL-WIDTH colon ：) ---
TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[full7x15] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
if [[ -z "${TB_API_KEY}" ]]; then echo "[full7x15] FATAL: TB_API_KEY empty"; exit 1; fi

cd "$TB_DIR" || { echo "[full7x15] FATAL: cd failed"; exit 2; }

# --- Kill any stale gw_proxy on 9090/9091 (from previous runs) ---
echo "[full7x15] cleaning stale gw_proxy ..."
pkill -f 'gw_proxy.py' 2>/dev/null || true
sleep 2

# --- Create filtered dataset with only tasks that have local Docker images ---
FULL_DATASET="$(mktemp -d -t tb_full_dataset_XXXXXX)"
echo "[full7x15] creating filtered dataset at ${FULL_DATASET}"
sg docker -c 'for d in ~/terminal-bench/*/; do t=$(basename "$d"); docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1 && echo "$t"; done' 2>/dev/null > /tmp/tb_local_images.txt
while IFS= read -r t; do
    ln -sf "${HOME}/terminal-bench/${t}" "${FULL_DATASET}/${t}"
done < /tmp/tb_local_images.txt
N_TASKS=$(ls -d "${FULL_DATASET}"/*/ 2>/dev/null | wc -l)
echo "[full7x15] ${N_TASKS} tasks with local images"
echo "[full7x15] task list:"
ls "${FULL_DATASET}" 2>/dev/null | sort | sed 's/^/  /'

echo "[full7x15] starting full 7×${N_TASKS} at $(date '+%F %T') ..."

# --- Run via launch_tb_7way.sh in full mode with filtered dataset ---
# Quoting pattern matches the working _pilot_gen7_launcher.sh.
exec sg docker -c 'export TB_API_KEY="'"$TB_API_KEY"'" PATH="/home/app.e0031982/.local/bin:$PATH" TB_TASKS_DIR="'"$FULL_DATASET"'"; cd '"$TB_DIR"'; bash launch_tb_7way.sh'

