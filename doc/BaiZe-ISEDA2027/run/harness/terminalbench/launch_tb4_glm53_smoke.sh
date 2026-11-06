#!/usr/bin/env bash
# launch_tb4_glm53_smoke.sh — Terminal-Bench 4.0 · 7-harness smoke test × glm-5.3-flash
#
# Runs 7 harnesses × 1 task (bun-sourcemap-leak) to verify adapters work on TB4.
# Uses the existing gw_proxy 9092 (chat) + 9093 (dsh) started by launch_glm53_full500.sh.
#
# Usage:
#   sg docker -c "bash launch_tb4_glm53_smoke.sh" > /tmp/tb4_glm53_smoke.log 2>&1 &
#
# Per BAIZE_HARNESS_TASK.md §2026-11-06:
#   - backbone = glm-5.3-flash
#   - cline: direct gateway; codex/opencode/claude-code/pi/hermes: gw_proxy 9092; dsh: gw_proxy_dsh 9093
#   - 7×1 smoke to verify adapters on TB4 before full 7×66
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TB4_DATASET="${HOME}/terminal-bench-4.0"
SMOKE_TASK="bun-sourcemap-leak"
TB_OVERLAY="${SCRIPT_DIR}/overlay-network-host.yml"
TRACES_DIR="${SCRIPT_DIR}/traces"
JOBS_DIR="${SCRIPT_DIR}/jobs_tb4_glm53_smoke"

# --- glm-5.3-flash configuration ---
GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
GLM53_BASE="http://agi-gateway.cxmt.com/v1"

# --- Export env vars for TB adapters (_base.py reads these) ---
export TB_MODEL="${GLM53_MODEL}"
export TB_API_KEY="${GLM53_KEY}"
export TB_BASE_URL="${GLM53_BASE}"
export TB_GW_PROXY_URL="http://127.0.0.1:9092/v1"
export TB_GW_PROXY_BASE="http://127.0.0.1:9092"
export TB_GW_DSH_URL="http://127.0.0.1:9093/v1"
export TB_AGENT_TIMEOUT=600   # 10min per agent (smoke — don't need full 8h)
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
export PATH="${HOME}/.bun/bin:${HOME}/.local/bin:${PATH}"
# Strip proxies for internal gateway access (mirrors launch_glm53_full500.sh)
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

# --- Pre-flight checks ---
echo "=== Terminal-Bench 4.0 · 7-harness smoke × glm-5.3-flash ==="
echo "Task: ${SMOKE_TASK}"
echo "Dataset: ${TB4_DATASET} ($(ls "${TB4_DATASET}" | wc -l) tasks)"
echo "Model: ${GLM53_MODEL}"
echo "Date: $(date '+%F %T')"
echo ""

# Check task exists
if [[ ! -d "${TB4_DATASET}/${SMOKE_TASK}" ]]; then
    echo "FATAL: smoke task ${SMOKE_TASK} not found in ${TB4_DATASET}" >&2
    exit 1
fi

# Check gw_proxy is up
if ! curl -s -o /dev/null http://127.0.0.1:9092/v1/models 2>/dev/null; then
    echo "FATAL: gw_proxy 9092 not responding" >&2
    exit 1
fi
if ! curl -s -o /dev/null http://127.0.0.1:9093/v1/models 2>/dev/null; then
    echo "FATAL: gw_proxy_dsh 9093 not responding" >&2
    exit 1
fi
echo "gw_proxy 9092 + 9093: OK"

# Check docker access
if ! docker info >/dev/null 2>&1; then
    echo "FATAL: docker daemon not accessible" >&2
    exit 1
fi
echo "docker: OK ($(docker version --format '{{.Client.Version}}'))"
echo "harbor: $(harbor --version)"
echo ""

# --- Run each harness × 1 task ---
TASK_PATH="${TB4_DATASET}/${SMOKE_TASK}"
mkdir -p "${JOBS_DIR}" "${TRACES_DIR}"

PASS=0
FAIL=0
RESULTS=()

for harness in "${HARNESSES[@]}"; do
    echo "--- Harness: ${harness} ---"

    case "${harness}" in
        cline-patched)     AGENT_PATH="terminalbench.agents.cline_patched:ClinePatched" ;;
        codex)             AGENT_PATH="terminalbench.agents.codex:CodexTB" ;;
        hermes)            AGENT_PATH="terminalbench.agents.hermes:HermesTB" ;;
        opencode)          AGENT_PATH="terminalbench.agents.opencode:OpenCodeTB" ;;
        claude-code)       AGENT_PATH="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
        deepseek-harness)  AGENT_PATH="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
        pi)                AGENT_PATH="terminalbench.agents.pi:PiTB" ;;
    esac

    # Run with short timeout multiplier for smoke (agent_timeout=28800s × 0.02 ≈ 576s)
    nice -n 19 harbor run \
        -p "${TASK_PATH}" \
        --agent "${AGENT_PATH}" \
        -k 1 \
        --n-concurrent 1 \
        --agent-timeout-multiplier 0.02 \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${JOBS_DIR}/${harness}" \
        2>&1 | tee "${TRACES_DIR}/tb4_glm53_smoke_${harness}.log" || {
            echo "WARNING: ${harness} smoke failed. Continuing."
            RESULTS+=("${harness}: FAIL")
            FAIL=$((FAIL + 1))
            continue
        }

    # Check result
    RESULT_FILE=$(find "${JOBS_DIR}/${harness}" -name "result.json" -newer "${JOBS_DIR}" 2>/dev/null | head -1)
    if [[ -n "${RESULT_FILE}" ]]; then
        REWARD=$(python3 -c "import json; d=json.load(open('${RESULT_FILE}')); print(d.get('reward','?'))" 2>/dev/null || echo "?")
        echo "  ${harness} reward=${REWARD}"
        RESULTS+=("${harness}: reward=${REWARD}")
        PASS=$((PASS + 1))
    else
        echo "  ${harness} no result.json found"
        RESULTS+=("${harness}: no result")
        FAIL=$((FAIL + 1))
    fi
    echo "--- ${harness} done ---"
    echo ""
done

echo ""
echo "=== TB4 glm53 smoke complete ==="
echo "Pass: ${PASS} / Fail: ${FAIL} / Total: ${#HARNESSES[@]}"
echo ""
echo "Results:"
for r in "${RESULTS[@]}"; do
    echo "  ${r}"
done
echo ""
echo "Jobs: ${JOBS_DIR}"
echo "Traces: ${TRACES_DIR}/tb4_glm53_smoke_*.log"
