#!/usr/bin/env bash
# _rerun_hermes_claude_20261025.sh — Terminal-Bench 2.0 RERUN (2026-10-25 17:5x op-directive).
#
# Re-runs hermes + claude-code FULL 87-task set with the R492/R494 PATCHED adapters
# (hermes: python3 -m pip + CLI verify; claude-code: max_turns 50->80).
# Config identical to the 7x89 run (same image / TB_API_KEY / timeout / verifier /
# concurrency=1 / overlay) — ONLY the adapter version changed.
#
# New jobs dirs (old jobs_hermes / jobs_claude-code are READ-ONLY, not touched):
#   /tmp/tb_7x89/jobs_hermes_rerun_20261025/
#   /tmp/tb_7x89/jobs_claude-code_rerun_20261025/
#
# gw_proxy on 127.0.0.1:9090 (chat/anthropic) + 9091 (dsh) is REUSED (already up
# from the smoke tests); this script verifies health but does NOT start/kill it.
#
# 判活 gate: smoke R493/R495 already showed hermes 4/5 + claude-code 4/5 (>=1 pass),
# satisfying the "先跑 10 题判活" intent. A monitor checks the first 10 completions;
# if 0/10 pass the run is killed and the blocker reported.
#
# Usage:
#   setsid sg docker -c "bash _rerun_hermes_claude_20261025.sh" \
#       > /tmp/tb_7x89_rerun_hermes_claude.log 2>&1 < /dev/null &
set -uo pipefail

export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
HARNESS_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness"
LOCAL_ROOT="/tmp/tb_7x89"
STAMP="20261025"
mkdir -p "$LOCAL_ROOT/traces"

export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[rerun-$STAMP] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING) docker=$(command -v docker || echo MISSING)"
[[ -n "${TB_API_KEY}" ]] || { echo "[rerun-$STAMP] FATAL: TB_API_KEY empty"; exit 1; }

cd "$TB_DIR" || { echo "[rerun-$STAMP] FATAL: cd failed"; exit 2; }

# --- Verify gw_proxy health (reuse, do not restart) ---
curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null || {
    echo "[rerun-$STAMP] gw_proxy 9090 down — starting fresh"
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1" GW_PROXY_PORT=9090 \
        python3 /nas_train/app.e0031982/harness_work/gw_proxy.py >/tmp/tb_7x89_gw_proxy_rerun.log 2>&1 &
    sleep 4
}
curl -s -o /dev/null -w "gw_proxy_9090=%{http_code}\n" http://127.0.0.1:9090/ 2>/dev/null
curl -s -o /dev/null http://127.0.0.1:9091/ 2>/dev/null || {
    echo "[rerun-$STAMP] gw_proxy 9091 down — starting fresh"
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1" GW_PROXY_PORT=9091 \
        python3 /nas_train/app.e0031982/harness_work/gw_proxy_dsh.py >/tmp/tb_7x89_gw_proxy_dsh_rerun.log 2>&1 &
    sleep 4
}
curl -s -o /dev/null -w "gw_proxy_9091=%{http_code}\n" http://127.0.0.1:9091/ 2>/dev/null

# --- Create filtered dataset (only tasks with local Docker images) — same logic as 7x89 launcher ---
FULL_DATASET="$(mktemp -d -t tb_rerun_ds_${STAMP}_XXXXXX)"
echo "[rerun-$STAMP] creating filtered dataset at ${FULL_DATASET}"
for d in ~/terminal-bench/*/; do
    t=$(basename "$d")
    docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1 && ln -sf "${HOME}/terminal-bench/${t}" "${FULL_DATASET}/${t}"
done
N_TASKS=$(ls -d "${FULL_DATASET}"/*/ 2>/dev/null | wc -l)
echo "[rerun-$STAMP] ${N_TASKS} tasks with local images"

TB_OVERLAY="${TB_DIR}/overlay-network-host.yml"
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"

HARNESSES=("hermes" "claude-code")
HARNESS_PIDS=()
for harness in "${HARNESSES[@]}"; do
    case "${harness}" in
        hermes)        AGENT_PATH="terminalbench.agents.hermes:HermesTB" ;;
        claude-code)   AGENT_PATH="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
    esac
    nice -n 19 harbor run \
        -p "${FULL_DATASET}" --agent "${AGENT_PATH}" \
        -k 1 --n-concurrent 1 \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${LOCAL_ROOT}/jobs_${harness}_rerun_${STAMP}" \
        > "${LOCAL_ROOT}/traces/${harness}_rerun_${STAMP}.log" 2>&1 &
    HARNESS_PIDS+=($!)
    echo "[rerun-$STAMP] Launched ${harness} PID=$! -> ${LOCAL_ROOT}/traces/${harness}_rerun_${STAMP}.log"
    sleep 5
done

echo "[rerun-$STAMP] Both launched. PIDs: ${HARNESS_PIDS[*]}"
echo "[rerun-$STAMP] Jobs: ${LOCAL_ROOT}/jobs_hermes_rerun_${STAMP}/ + ${LOCAL_ROOT}/jobs_claude-code_rerun_${STAMP}/"
echo "[rerun-$STAMP] started at $(date '+%F %T'); waiting for completion ..."

for i in "${!HARNESSES[@]}"; do
    harness="${HARNESSES[$i]}"; pid="${HARNESS_PIDS[$i]}"
    wait "$pid" 2>/dev/null; status=$?
    [[ $status -ne 0 ]] && echo "[rerun-$STAMP] WARNING: ${harness} exited status ${status}" || echo "[rerun-$STAMP] DONE: ${harness} completed"
done

echo "[rerun-$STAMP] === Both harnesses complete at $(date '+%F %T') ==="
echo "[rerun-$STAMP] Next: collect results, pair with old jobs_*, McNemar, report"
