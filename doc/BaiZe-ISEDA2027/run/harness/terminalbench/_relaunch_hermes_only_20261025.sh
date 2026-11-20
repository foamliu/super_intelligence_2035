#!/usr/bin/env bash
# _relaunch_hermes_only_20261025.sh — relaunch ONLY hermes after python3-fallback
# adapter fix (claude-code keeps running untouched). Same config as the 7x89 run.
set -uo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
HARNESS_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness"
LOCAL_ROOT="/tmp/tb_7x89"
STAMP="20261025"
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
cd "$TB_DIR" || exit 2
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
FULL_DATASET="/tmp/tb_rerun_ds_20261025_KzHXLm"
TB_OVERLAY="${TB_DIR}/overlay-network-host.yml"
echo "[hermes-relaunch-$STAMP] start $(date '+%F %T') HOST=$(hostname) apikey_len=${#TB_API_KEY}"
nice -n 19 harbor run \
    -p "${FULL_DATASET}" --agent "terminalbench.agents.hermes:HermesTB" \
    -k 1 --n-concurrent 1 \
    --extra-docker-compose "${TB_OVERLAY}" \
    --jobs-dir "${LOCAL_ROOT}/jobs_hermes_rerun_${STAMP}" \
    > "${LOCAL_ROOT}/traces/hermes_rerun_${STAMP}.log" 2>&1
echo "[hermes-relaunch-$STAMP] exited status $? at $(date '+%F %T')"
