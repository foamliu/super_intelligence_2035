#!/usr/bin/env bash
# _full_7x89_concurrent_launcher.sh — Terminal-Bench 2.0 FULL evaluation.
#
# 7 harnesses run IN PARALLEL (7-way concurrent), each doing all 89 tasks
# serially (--n-concurrent 1).  Total: 7 × 89 = 623 trials, pass@1, k=1.
#
# Designed per 2026-10-24 operator directive:
#   - Each harness = 1 concurrency slot (7 parallel harbor processes)
#   - Independent --jobs-dir on /tmp (NOT NFS — avoids Stale file handle)
#   - Independent trace dirs
#   - Shared gw_proxy (9090 chat/anthropic + 9091 dsh)
#   - nice -n 19 to avoid IO contention with training on .12/.29
#
# PREREQUISITE: All 89 alexgshaw/*:20251031 images must be present.
#
# Usage:
#   setsid sg docker -c "bash _full_7x89_concurrent_launcher.sh" \
#       > /tmp/tb_7x89_concurrent.log 2>&1 < /dev/null &

set -uo pipefail

export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
HARNESS_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness"
LOCAL_ROOT="/tmp/tb_7x89"
mkdir -p "$LOCAL_ROOT/traces"

export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[7x89] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
if [[ -z "${TB_API_KEY}" ]]; then echo "[7x89] FATAL: TB_API_KEY empty"; exit 1; fi

cd "$TB_DIR" || { echo "[7x89] FATAL: cd failed"; exit 2; }

# --- Check all 89 images present ---
echo "[7x89] Checking all 89 task images ..."
MISSING=0; MISSING_LIST=""
for d in ~/terminal-bench/*/; do
    t=$(basename "$d")
    docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1 || {
        MISSING=$((MISSING + 1)); MISSING_LIST="${MISSING_LIST} ${t}"; }
done
if [[ $MISSING -gt 0 ]]; then
    echo "[7x89] FATAL: $MISSING images still missing:$MISSING_LIST"
    exit 3
fi
echo "[7x89] All 89 images present. Proceeding."

# --- 30-second resource assessment ---
echo "[7x89] === Resource Assessment ==="
echo "[7x89] CPUs: $(nproc)"
echo "[7x89] RAM:  $(free -h | awk '/^Mem:/ {print $2 " total, " $7 " available"}')"
echo "[7x89] Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "[7x89] Disk: $(df -h /data | awk 'NR==2 {print $2 " total, " $4 " free (" $5 " used)"}')"
echo "[7x89] Docker containers running: $(docker ps -q 2>/dev/null | wc -l)"
echo ""


GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"
GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1"
GW_PIDS=(); HARNESS_PIDS=()
cleanup_gw() {
    for _pid in "${GW_PIDS[@]:-}"; do kill "$_pid" 2>/dev/null || true; done
    for _pid in "${HARNESS_PIDS[@]:-}"; do kill "$_pid" 2>/dev/null || true; done
}
trap cleanup_gw EXIT

GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="$GW_UPSTREAM" GW_PROXY_PORT=9090 \
    python3 "$GW_PROXY_PY" >/tmp/tb_7x89_gw_proxy.log 2>&1 &
GW_PIDS+=($!)
GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="$GW_UPSTREAM" GW_PROXY_PORT=9091 \
    python3 "$GW_PROXY_DSH_PY" >/tmp/tb_7x89_gw_proxy_dsh.log 2>&1 &
GW_PIDS+=($!)
for _ in $(seq 1 20); do
    curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null && break; sleep 0.5
done
curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null || {
    echo "[7x89] ERROR: gw_proxy did not start"; cat /tmp/tb_7x89_gw_proxy.log >&2; exit 1; }
echo "[7x89] gw_proxy up on 127.0.0.1:9090 + 9091"
echo ""

TB_OVERLAY="${TB_DIR}/overlay-network-host.yml"
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

echo "[7x89] === Running ${#HARNESSES[@]} harnesses x ${N_TASKS} tasks = $(( ${#HARNESSES[@]} * N_TASKS )) trials ==="
echo "[7x89] Mode: 7-WAY CONCURRENT (each harness --n-concurrent 1)"
echo "[7x89] starting at $(date '+%F %T') ..."
echo ""

for harness in "${HARNESSES[@]}"; do
    case "${harness}" in
        cline-patched)    AGENT_PATH="terminalbench.agents.cline_patched:ClinePatched" ;;
        codex)            AGENT_PATH="terminalbench.agents.codex:CodexTB" ;;
        hermes)           AGENT_PATH="terminalbench.agents.hermes:HermesTB" ;;
        opencode)         AGENT_PATH="terminalbench.agents.opencode:OpenCodeTB" ;;
        claude-code)      AGENT_PATH="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
        deepseek-harness) AGENT_PATH="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
        pi)               AGENT_PATH="terminalbench.agents.pi:PiTB" ;;
    esac
    nice -n 19 harbor run \
        -p "${FULL_DATASET}" --agent "${AGENT_PATH}" \
        -k 1 --n-concurrent 1 \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${LOCAL_ROOT}/jobs_${harness}" \
        > "${LOCAL_ROOT}/traces/${harness}_run.log" 2>&1 &
    HARNESS_PIDS+=($!)
    echo "[7x89] Launched ${harness} PID=$! -> ${LOCAL_ROOT}/traces/${harness}_run.log"
    sleep 5  # stagger to avoid thundering herd
done

echo ""
echo "[7x89] All 7 launched. PIDs: ${HARNESS_PIDS[*]}"
echo "[7x89] Waiting for completion ..."
echo ""

FAILED_HARNESSES=()
for i in "${!HARNESSES[@]}"; do
    harness="${HARNESSES[$i]}"; pid="${HARNESS_PIDS[$i]}"
    wait "$pid" 2>/dev/null; status=$?
    if [[ $status -ne 0 ]]; then
        echo "[7x89] WARNING: ${harness} exited status ${status}"
        FAILED_HARNESSES+=("$harness")
    else
        echo "[7x89] DONE: ${harness} completed"
    fi
done

echo ""
echo "[7x89] === All 7 harnesses complete at $(date '+%F %T') ==="
[[ ${#FAILED_HARNESSES[@]} -gt 0 ]] && echo "[7x89] Failed: ${FAILED_HARNESSES[*]}"
echo "[7x89] Jobs:   ${LOCAL_ROOT}/jobs_*/"
echo "[7x89] Traces: ${LOCAL_ROOT}/traces/"
echo "[7x89] Next: collect results, McNemar, 89/89 full coverage report"

pkill -f 'gw_proxy.*9090' 2>/dev/null || true
pkill -f 'gw_proxy.*9091' 2>/dev/null || true
sleep 2

FULL_DATASET="$(mktemp -d -t tb_7x89_dataset_XXXXXX)"
echo "[7x89] creating full 89-task dataset at ${FULL_DATASET}"
for d in ~/terminal-bench/*/; do
    t=$(basename "$d"); ln -sf "${HOME}/terminal-bench/${t}" "${FULL_DATASET}/${t}"
done
N_TASKS=$(ls -d "${FULL_DATASET}"/*/ 2>/dev/null | wc -l)
echo "[7x89] ${N_TASKS} tasks in dataset"
