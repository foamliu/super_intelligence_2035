#!/usr/bin/env bash
# launch_tb4_glm53_rerun_cline_codex.sh — TB4 RE-RUN: cline-patched + codex × glm-5.3-flash
# First run (06:02/06:27) ALL 66 tasks ERRORED due to gateway ECONNRESET.
# Gateway is now stable (probe OK). Re-running with TB_AGENT_TIMEOUT=3600s.
# Usage: sg docker -c "setsid bash launch_tb4_glm53_rerun_cline_codex.sh > /tmp/tb4_glm53_rerun_cline_codex.log 2>&1 < /dev/null &"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TB4_DATASET="${HOME}/terminal-bench-4.0"
TB_OVERLAY="${SCRIPT_DIR}/overlay-network-host.yml"
TRACES_DIR="${SCRIPT_DIR}/traces"
JOBS_DIR="${SCRIPT_DIR}/jobs_tb4_glm53_full"

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

mkdir -p "${TRACES_DIR}"

echo "=== TB4 RE-RUN (cline-patched + codex) × glm-5.3-flash ==="
echo "Date: $(date '+%F %T')"
echo "Dataset: ${TB4_DATASET} ($(ls "${TB4_DATASET}" | wc -l) tasks)"
echo "Timeout: ${TB_AGENT_TIMEOUT}s"
echo "Reason: First run all-66-errored due to gateway ECONNRESET"

# Gateway probe (real chat completions check)
if ! curl -s -o /dev/null http://127.0.0.1:9092/v1/models 2>/dev/null; then
  echo "FATAL: gw_proxy 9092 down" >&2; exit 1
fi
echo "gw_proxy 9092: OK"

run_harness() {
    local harness="$1" agent_path="$2"
    echo "[$(date '+%H:%M:%S')] Starting ${harness} RE-RUN (66 tasks)"
    nice -n 19 harbor run \
      -p "${TB4_DATASET}" \
      --agent "${agent_path}" \
      -k 1 --n-concurrent 1 \
      --extra-docker-compose "${TB_OVERLAY}" \
      --jobs-dir "${JOBS_DIR}/${harness}" \
      2>&1 | tee "${TRACES_DIR}/tb4_glm53_full_${harness}_rerun.log" || {
        echo "WARNING: ${harness} had errors."
      }
    echo "[$(date '+%H:%M:%S')] Finished ${harness} RE-RUN"
}

run_harness "cline-patched" "terminalbench.agents.cline_patched:ClinePatched" &
PID1=$!
run_harness "codex" "terminalbench.agents.codex:CodexTB" &
PID2=$!

wait "${PID1}"
wait "${PID2}"
echo "=== TB4 RE-RUN (cline-patched + codex) complete ==="
