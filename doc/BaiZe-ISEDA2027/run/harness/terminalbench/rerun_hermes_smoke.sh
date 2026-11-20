#!/usr/bin/env bash
# rerun_pipless_smoke.sh — re-run hermes + deepseek-harness TB4 smoke after the
# pip-bootstrap fix (R1714).  Both failed with "No module named pip" because TB4
# images ship bare python3 without pip.  _base.py:_ensure_pip() now bootstraps
# pip via ensurepip → get-pip.py before the harness install.
#
# Usage: sg docker -c "bash rerun_pipless_smoke.sh"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TB4_DATASET="${HOME}/terminal-bench-4.0"
SMOKE_TASK="bun-sourcemap-leak"
TB_OVERLAY="${SCRIPT_DIR}/overlay-network-host.yml"
TRACES_DIR="${SCRIPT_DIR}/traces"
JOBS_DIR="${SCRIPT_DIR}/jobs_tb4_glm53_smoke"

GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
GLM53_BASE="http://agi-gateway.cxmt.com/v1"

export TB_MODEL="${GLM53_MODEL}"
export TB_API_KEY="${GLM53_KEY}"
export TB_BASE_URL="${GLM53_BASE}"
export TB_GW_PROXY_URL="http://127.0.0.1:9092/v1"
export TB_GW_PROXY_BASE="http://127.0.0.1:9092"
export TB_GW_DSH_URL="http://127.0.0.1:9093/v1"
export TB_AGENT_TIMEOUT=600
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
export PATH="${HOME}/.bun/bin:${HOME}/.local/bin:${PATH}"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

echo "=== TB4 smoke re-run: hermes + deepseek-harness (R1714 pip-bootstrap) ==="
echo "Task: ${SMOKE_TASK} | Date: $(date '+%F %T')"

for harness in hermes deepseek-harness; do
    echo ""
    echo "--- Harness: ${harness} ---"
    case "${harness}" in
        hermes)           AGENT_PATH="terminalbench.agents.hermes:HermesTB" ;;
        deepseek-harness) AGENT_PATH="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
    esac
    nice -n 19 harbor run \
        -p "${TB4_DATASET}/${SMOKE_TASK}" \
        --agent "${AGENT_PATH}" \
        -k 1 \
        --n-concurrent 1 \
        --agent-timeout-multiplier 0.02 \
        --agent-setup-timeout-multiplier 3.0 \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${JOBS_DIR}/${harness}-rerun" \
        2>&1 | tee "${TRACES_DIR}/tb4_glm53_smoke_${harness}_rerun.log" || {
            echo "WARNING: ${harness} re-run failed."
            continue
        }
    echo "--- ${harness} done ---"
done

echo ""
echo "=== re-run complete ==="
echo "Results in: ${JOBS_DIR}/{hermes,deepseek-harness}-rerun/"

