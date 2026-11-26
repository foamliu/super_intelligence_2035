#!/usr/bin/env bash
# rerun_codex_tb4_R1731.sh — re-run codex TB4 after fixing stale config.toml
# (was: model=kimi-k2.6-cloud + wire_api=responses → exit=1 on every task)
# Fix: agents/codex.py now writes model=TB_MODEL(glm-5.3-flash) + wire_api=chat
# Runs in parallel with the ongoing cline-patched TB4 (1 container each, 2 max).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TB4_DATASET="${HOME}/terminal-bench-4.0"
TB_OVERLAY="${SCRIPT_DIR}/overlay-network-host.yml"
TRACES_DIR="${SCRIPT_DIR}/traces"
JOBS_DIR="${SCRIPT_DIR}/jobs_tb4_glm53_full/codex"

GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
GLM53_BASE="http://agi-gateway.cxmt.com/v1"

export TB_MODEL="${GLM53_MODEL}"
export TB_API_KEY="${GLM53_KEY}"
export TB_BASE_URL="${GLM53_BASE}"
export TB_GW_PROXY_URL="http://127.0.0.1:9092/v1"
export TB_GW_PROXY_BASE="http://127.0.0.1:9092"
export TB_GW_DSH_URL="http://127.0.0.1:9093/v1"
export TB_AGENT_TIMEOUT=3600
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
export PATH="${HOME}/.bun/bin:${HOME}/.local/bin:${PATH}"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

mkdir -p "${JOBS_DIR}" "${TRACES_DIR}"

echo "=== TB4 codex re-run (R1731 fix: stale config → TB_MODEL+wire_api=chat) ==="
echo "Date: $(date '+%F %T')"
echo "Dataset: ${TB4_DATASET} ($(ls "${TB4_DATASET}" | wc -l) tasks)"

if ! curl -s -o /dev/null http://127.0.0.1:9092/v1/models 2>/dev/null; then
    echo "FATAL: gw_proxy 9092 down" >&2; exit 1
fi
echo "gw_proxy 9092: OK"

nice -n 19 harbor run \
    -p "${TB4_DATASET}" \
    --agent "terminalbench.agents.codex:CodexTB" \
    -k 1 --n-concurrent 1 \
    --extra-docker-compose "${TB_OVERLAY}" \
    --jobs-dir "${JOBS_DIR}" \
    2>&1 | tee "${TRACES_DIR}/tb4_glm53_full_codex_rerun_R1731.log"

echo "[$(date '+%H:%M:%S')] Finished codex TB4 re-run"
