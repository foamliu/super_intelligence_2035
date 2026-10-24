#!/usr/bin/env bash
# _full_7x15_v2_launcher.sh — Terminal-Bench 2.0 full evaluation (R473, 2026-10-24).
#
# FIX vs v1: redirect ALL harbor --jobs-dir and trace logs to /tmp (local disk)
# to avoid NFS "Stale file handle" (Errno 116) crashes that killed v1.
# Oracle check already verified (15/15, mean 0.733) — skipped here.
#
# Only 15 of 89 TB task images are locally cached (MITM proxy blocks Docker Hub).
# Creates a filtered dataset of the 15 available tasks, then runs all 7 harnesses
# sequentially via harbor run.
#
# Total: 7 harnesses × 15 tasks = 105 trials (pass@1, k=1, concurrency=1).
# ETA: ~17 hours (sequential, ~10min/task).
#
# This script MUST be run under sg docker (user not in docker group):
#   setsid sg docker -c "bash _full_7x15_v2_launcher.sh" > /tmp/tb_full_7x15_v2.log 2>&1 < /dev/null &

set -uo pipefail   # no -e: a single harness failure should not abort the whole run

export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
HARNESS_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness"

# Local disk workspace (avoids NFS stale handle)
LOCAL_ROOT="/tmp/tb_full_v2"
mkdir -p "$LOCAL_ROOT/traces"

# --- Get API key (keys.txt uses FULL-WIDTH colon ：) ---
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[v2] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
if [[ -z "${TB_API_KEY}" ]]; then echo "[v2] FATAL: TB_API_KEY empty"; exit 1; fi

cd "$TB_DIR" || { echo "[v2] FATAL: cd failed"; exit 2; }

# --- Kill any stale gw_proxy on 9090/9091 (from previous runs) ---
echo "[v2] cleaning stale gw_proxy ..."
pkill -f 'gw_proxy.*9090' 2>/dev/null || true
pkill -f 'gw_proxy.*9091' 2>/dev/null || true
sleep 2

# --- Create filtered dataset with only tasks that have local Docker images ---
# (already running under sg docker, so docker is accessible)
FULL_DATASET="$(mktemp -d -t tb_full_dataset_XXXXXX)"
echo "[v2] creating filtered dataset at ${FULL_DATASET}"
for d in ~/terminal-bench/*/; do
    t=$(basename "$d")
    docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1 && ln -sf "${HOME}/terminal-bench/${t}" "${FULL_DATASET}/${t}"
done
N_TASKS=$(ls -d "${FULL_DATASET}"/*/ 2>/dev/null | wc -l)
echo "[v2] ${N_TASKS} tasks with local images"
echo "[v2] task list:"
ls "${FULL_DATASET}" 2>/dev/null | sort | sed 's/^/  /'

# --- Start gw_proxy (same as launch_tb_7way.sh) ---
GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"
GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1"
GW_PIDS=()
cleanup_gw() {
    for _pid in "${GW_PIDS[@]:-}"; do
        kill "$_pid" 2>/dev/null || true
    done
}
trap cleanup_gw EXIT

if [[ ! -f "$GW_PROXY_PY" ]]; then
    echo "[v2] ERROR: gw_proxy.py not found at $GW_PROXY_PY" >&2
    exit 1
fi
echo "[v2] Starting gw_proxy (9090 chat/anthropic) + gw_proxy_dsh (9091)..."
GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="$GW_UPSTREAM" GW_PROXY_PORT=9090 \
    python3 "$GW_PROXY_PY" >/tmp/tb_gw_proxy.log 2>&1 &
GW_PIDS+=($!)
GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="$GW_UPSTREAM" GW_PROXY_PORT=9091 \
    python3 "$GW_PROXY_DSH_PY" >/tmp/tb_gw_proxy_dsh.log 2>&1 &
GW_PIDS+=($!)
for _ in $(seq 1 20); do
    if curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null; then break; fi
    sleep 0.5
done
if ! curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null; then
    echo "[v2] ERROR: gw_proxy did not start. Log:" >&2
    cat /tmp/tb_gw_proxy.log >&2
    exit 1
fi
echo "[v2] gw_proxy up on 127.0.0.1:9090 + 9091 (upstream ${GW_UPSTREAM})"
echo ""

# --- Overlay file ---
TB_OVERLAY="${TB_DIR}/overlay-network-host.yml"

# --- Python path for custom agents ---
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"

# --- Harness list ---
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

echo "[v2] === Running ${#HARNESSES[@]} harnesses × ${N_TASKS} tasks = $(( ${#HARNESSES[@]} * N_TASKS )) trials ==="
echo "[v2] starting at $(date '+%F %T') ..."
echo ""

# --- Run each harness (jobs-dir on /tmp to avoid NFS stale handle) ---
for harness in "${HARNESSES[@]}"; do
    echo "--- Harness: ${harness} ($(date '+%T')) ---"

    case "${harness}" in
        cline-patched)     AGENT_PATH="terminalbench.agents.cline_patched:ClinePatched" ;;
        codex)             AGENT_PATH="terminalbench.agents.codex:CodexTB" ;;
        hermes)            AGENT_PATH="terminalbench.agents.hermes:HermesTB" ;;
        opencode)          AGENT_PATH="terminalbench.agents.opencode:OpenCodeTB" ;;
        claude-code)       AGENT_PATH="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
        deepseek-harness)  AGENT_PATH="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
        pi)                AGENT_PATH="terminalbench.agents.pi:PiTB" ;;
    esac

    # KEY FIX: --jobs-dir on /tmp (local disk), NOT NFS
    # We're already under sg docker, so harbor has docker access.
    nice -n 19 harbor run \
        -p "${FULL_DATASET}" \
        --agent "${AGENT_PATH}" \
        -k 1 \
        --n-concurrent 1 \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${LOCAL_ROOT}/jobs_${harness}" \
        2>&1 | tee "${LOCAL_ROOT}/traces/${harness}_run.log" || {
            echo "WARNING: ${harness} run failed (may be quota/infra). Continuing."
        }

    echo "--- ${harness} done ($(date '+%T')) ---"
    echo ""
done

echo "[v2] === All 7 harnesses complete at $(date '+%F %T') ==="
echo "[v2] Jobs:   ${LOCAL_ROOT}/jobs_*/"
echo "[v2] Traces: ${LOCAL_ROOT}/traces/"
echo ""
echo "[v2] Next: collect results and generate report"
