#!/usr/bin/env bash
# launch_tb21_glm53_7way.sh — Terminal-Bench 2.1 · 7-harness full run × glm-5.3-flash
# Switched from TB4 per §15:2x (2026-11-07): TB4 661 results/0 passed (capability, R1743).
# TB-2.1: 89 tasks × 7 harnesses = 623 trials, 7-way concurrent.
# Discipline: 1) declare TB-2.1/89/7way (NOT comparable with TB4) 2) oracle 5/5 first
#   3) 7 routes not replaced/merged 4) jobs-dir in /tmp 5) export TB_API_KEY
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TB_DATASET="${HOME}/terminal-bench"
TB_OVERLAY="$SCRIPT_DIR/overlay-network-host.yml"
TRACES_DIR="$SCRIPT_DIR/traces"
JOBS_BASE="/tmp/tb21_glm53_jobs"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
export TB_MODEL="glm-5.3-flash"
export TB_API_KEY="$GLM53_KEY"
export TB_BASE_URL="http://agi-gateway.cxmt.com/v1"
export TB_GW_PROXY_URL="http://127.0.0.1:9092/v1"
export TB_GW_PROXY_BASE="http://127.0.0.1:9092"
export TB_GW_DSH_URL="http://127.0.0.1:9093/v1"
export TB_AGENT_TIMEOUT=3600
export PYTHONPATH="$HARNESS_DIR:${PYTHONPATH:-}"
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")
PILOT_TASKS=("break-filter-js-from-html" "bn-fit-modify" "log-summary-date-ranges" "cancel-async-tasks" "fix-git")
echo "=== Terminal-Bench 2.1 · 7-harness × glm-5.3-flash ==="
echo "Dataset: $TB_DATASET ($(ls "$TB_DATASET" | wc -l) tasks) | Model: glm-5.3-flash"
echo "Benchmark: TB-2.1 / 89 tasks / 7-way concurrent (NOT comparable with TB4)"
echo "Date: $(date '+%F %T')"
if [[ ! -d "$TB_DATASET" ]]; then echo "FATAL: dataset not found" >&2; exit 1; fi
curl -s -o /dev/null http://127.0.0.1:9092/v1/models 2>/dev/null || { echo "FATAL: gw_proxy 9092 down" >&2; exit 1; }
curl -s -o /dev/null http://127.0.0.1:9093/v1/models 2>/dev/null || echo "WARNING: gw_proxy_dsh 9093 down"
echo "gw_proxy 9092+9093: OK"
mkdir -p "$JOBS_BASE" "$TRACES_DIR"
echo "=== Oracle check (5 pilot tasks) ==="
PILOT_DATASET="$(mktemp -d -t tb21_pilot_XXXXXX)"
for task in "${PILOT_TASKS[@]}"; do ln -sf "$TB_DATASET/$task" "$PILOT_DATASET/$task"; done
ORACLE_JOBS="$JOBS_BASE/oracle"
mkdir -p "$ORACLE_JOBS"
nice -n 19 harbor run -p "$PILOT_DATASET" --agent oracle -k 1 --n-concurrent 4 \
    --extra-docker-compose "$TB_OVERLAY" --jobs-dir "$ORACLE_JOBS" \
    2>&1 | tee "$TRACES_DIR/tb21_oracle_check.log" || true
echo "Oracle check complete. Verifying 5/5..."
ORACLE_PASS=0; ORACLE_FAIL=0
for task in "${PILOT_TASKS[@]}"; do
    rf=$(find "$ORACLE_JOBS" -path "*/$task*/verifier/reward.txt" 2>/dev/null | head -1)
    if [[ -z "$rf" ]]; then echo "  $task: NO reward.txt — FAIL"; ORACLE_FAIL=$((ORACLE_FAIL+1)); continue; fi
    reward=$(cat "$rf" 2>/dev/null | tr -d '[:space:]')
    if [[ "$reward" == "1.0" ]] || [[ "$reward" == "1" ]]; then
        echo "  $task: reward=$reward — PASS"; ORACLE_PASS=$((ORACLE_PASS+1))
    else
        echo "  $task: reward=$reward — FAIL"; ORACLE_FAIL=$((ORACLE_FAIL+1))
    fi
done
echo "Oracle: $ORACLE_PASS/5 passed, $ORACLE_FAIL/5 failed"
if [[ "$ORACLE_PASS" -lt 5 ]]; then
    echo "FATAL: Oracle <5/5. Aborting (per §15:2x discipline #2)."; exit 1
fi
echo "Oracle 5/5 PASSED — proceeding to full 7-way run."
echo "=== 7 harnesses × 89 tasks = 623 trials ==="
for harness in "${HARNESSES[@]}"; do
    agent_path=""
    case "$harness" in
        cline-patched)    agent_path="terminalbench.agents.cline_patched:ClinePatched" ;;
        codex)            agent_path="terminalbench.agents.codex:CodexTB" ;;
        hermes)           agent_path="terminalbench.agents.hermes:HermesTB" ;;
        opencode)         agent_path="terminalbench.agents.opencode:OpenCodeTB" ;;
        claude-code)      agent_path="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
        deepseek-harness) agent_path="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
        pi)               agent_path="terminalbench.agents.pi:PiTB" ;;
    esac
    HJ="$JOBS_BASE/$harness"; mkdir -p "$HJ"
    echo "--- [$(date '+%H:%M:%S')] $harness (89 tasks) ---"
    nice -n 19 harbor run -p "$TB_DATASET" --agent "$agent_path" -k 1 --n-concurrent 1 \
        --extra-docker-compose "$TB_OVERLAY" --jobs-dir "$HJ" \
        2>&1 | tee "$TRACES_DIR/tb21_${harness}_run.log" || echo "WARNING: $harness errors"
    echo "--- [$(date '+%H:%M:%S')] $harness done ---"
done
echo "=== All 7 harnesses complete ==="
echo "Benchmark: TB-2.1 / 89 tasks / 7-way concurrent | Date: $(date '+%F %T')"
