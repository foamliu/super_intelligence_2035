#!/usr/bin/env bash
# _rerun_hermes_tb4_R1715.sh — TB4 smoke rerun for HERMES only (fixed _ensure_pip)
# R1714 fix: _base.py _ensure_pip now passes --break-system-packages to get-pip.py.
# The earlier hermes-rerun (03:39:56) ran BEFORE the fix and failed with PEP668.
# This rerun uses the now-fixed _base.py (mtime 03:54:54) + fresh pyc.
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

echo "=== TB4 smoke rerun · HERMES only · R1715 ==="
echo "Task: ${SMOKE_TASK}  Model: ${GLM53_MODEL}  Date: $(date '+%F %T')"

# pre-flight
curl -s -o /dev/null http://127.0.0.1:9092/v1/models || { echo "FATAL gw_proxy 9092 down"; exit 1; }
echo "gw_proxy 9092: OK"

# clear stale pyc to guarantee fixed _base.py is used
rm -f "${SCRIPT_DIR}/agents/__pycache__/"*.pyc 2>/dev/null || true

nice -n 19 harbor run \
    -p "${TB4_DATASET}/${SMOKE_TASK}" \
    --agent "terminalbench.agents.hermes:HermesTB" \
    -k 1 \
    --n-concurrent 1 \
    --agent-timeout-multiplier 0.02 \
    --extra-docker-compose "${TB_OVERLAY}" \
    --jobs-dir "${JOBS_DIR}/hermes-rerun2" \
    2>&1 | tee "${TRACES_DIR}/tb4_glm53_smoke_hermes_rerun2.log"

echo "=== hermes rerun2 done $(date '+%F %T') ==="
