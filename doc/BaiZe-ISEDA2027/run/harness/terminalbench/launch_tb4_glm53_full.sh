#!/usr/bin/env bash
# launch_tb4_glm53_full.sh — Terminal-Bench 4.0 · 7-harness full run × glm-5.3-flash
# Runs 7 harnesses × 66 TB4 tasks = 462 trials total.
# Uses gw_proxy 9092 (chat) + 9093 (dsh) from launch_glm53_full500.sh.
# Smoke confirmed all 7 adapters work on TB4 (pip bootstrap fixed for hermes/deepseek).
# Concurrency: 2 harnesses in parallel, each --n-concurrent 1 (2 Docker containers max).
# Agent timeout: 3600s (1h) per task via TB_AGENT_TIMEOUT env (was 1800s=30min, too short — all tasks errored).
# --agent-timeout-multiplier removed: let adapter use TB_AGENT_TIMEOUT directly (opts.timeout=None → fallback).
# Usage: sg docker -c "bash launch_tb4_glm53_full.sh" > /tmp/tb4_glm53_full.log 2>&1 &
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

HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

echo "=== Terminal-Bench 4.0 · 7-harness full run × glm-5.3-flash ==="
echo "Dataset: ${TB4_DATASET} ($(ls "${TB4_DATASET}" | wc -l) tasks)"
echo "Model: ${GLM53_MODEL}"
echo "Date: $(date '+%F %T')"
echo ""

if [[ ! -d "${TB4_DATASET}" ]]; then echo "FATAL: TB4 dataset not found" >&2; exit 1; fi
if ! curl -s -o /dev/null http://127.0.0.1:9092/v1/models 2>/dev/null; then echo "FATAL: gw_proxy 9092 down" >&2; exit 1; fi
if ! curl -s -o /dev/null http://127.0.0.1:9093/v1/models 2>/dev/null; then echo "FATAL: gw_proxy_dsh 9093 down" >&2; exit 1; fi
echo "gw_proxy 9092 + 9093: OK"
run_harness() {
    local harness="$1" agent_path=""
    case "${harness}" in
        cline-patched)     agent_path="terminalbench.agents.cline_patched:ClinePatched" ;;
        codex)             agent_path="terminalbench.agents.codex:CodexTB" ;;
        hermes)            agent_path="terminalbench.agents.hermes:HermesTB" ;;
        opencode)          agent_path="terminalbench.agents.opencode:OpenCodeTB" ;;
        claude-code)       agent_path="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
        deepseek-harness)  agent_path="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
        pi)                agent_path="terminalbench.agents.pi:PiTB" ;;
    esac
    echo "[$(date '+%H:%M:%S')] Starting ${harness} (66 tasks)"
    nice -n 19 harbor run \
        -p "${TB4_DATASET}" \
        --agent "${agent_path}" \
        -k 1 --n-concurrent 1 \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${JOBS_DIR}/${harness}" \
        2>&1 | tee "${TRACES_DIR}/tb4_glm53_full_${harness}.log" || {
            echo "WARNING: ${harness} had errors."
        }
    echo "[$(date '+%H:%M:%S')] Finished ${harness}"
}

i=0
while [[ $i -lt ${#HARNESSES[@]} ]]; do
    h1="${HARNESSES[$i]}"; h2=""
    if [[ $((i + 1)) -lt ${#HARNESSES[@]} ]]; then h2="${HARNESSES[$((i + 1))]}"; fi
    echo "=== Batch $((i / 2 + 1)): ${h1} ${h2:+& ${h2}} ==="
    run_harness "${h1}" & pid1=$!
    if [[ -n "${h2}" ]]; then run_harness "${h2}" & pid2=$!; wait "${pid2}"; fi
    wait "${pid1}"
    i=$((i + 2))
done

echo ""; echo "=== TB4 glm53 full run complete ==="
echo "Jobs: ${JOBS_DIR}"; echo "Traces: ${TRACES_DIR}/tb4_glm53_full_*.log"; echo ""
echo "=== Results Summary ==="
for harness in "${HARNESSES[@]}"; do
    latest=$(ls -td "${JOBS_DIR}/${harness}"/*/ 2>/dev/null | head -1)
    if [[ -n "${latest}" && -f "${latest}result.json" ]]; then
        python3 -c "
import json; d=json.load(open('${latest}result.json')); s=d.get('stats',{}); ev=s.get('evals',{})
for k,v in ev.items():
    rs=v.get('reward_stats',{}).get('reward',{}); n_pass=sum(1 for r,ids in rs.items() if float(r)>0)
    print(f'  ${harness}: {n_pass} passed / {len(rs.get(\"0.0\",[]))} zero / {v.get(\"n_errors\",0)} errored / {v.get(\"n_trials\",0)} total')
" 2>/dev/null || echo "  ${harness}: (parse error)"
    else echo "  ${harness}: (no result.json)"; fi
done

if ! docker info >/dev/null 2>&1; then echo "FATAL: docker not accessible" >&2; exit 1; fi
echo "docker: OK | harbor: $(harbor --version)"
echo ""

mkdir -p "${JOBS_DIR}" "${TRACES_DIR}"
