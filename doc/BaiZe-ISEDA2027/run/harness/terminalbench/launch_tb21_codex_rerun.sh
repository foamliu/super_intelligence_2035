#!/usr/bin/env bash
# launch_tb21_codex_rerun.sh — TB-2.1 codex ONLY rerun (fresh).
# Reason: first codex run failed at 22:53 11-07 because Docker daemon was down
# (trace: "Docker daemon is not running"). Docker is now up; gateway quota
# recovered ~05:26 11-08. Rerun codex fresh (89 tasks) so no 429/docker-down
# artifacts pollute the result. Failed jobs dir moved aside to .failed-dockerdown.
# Benchmark: TB-2.1 / 89 tasks / 7-way concurrent (NOT comparable with TB4).
# Discipline: 7 routes not replaced/merged; codex is its own route, run separately.
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
echo "=== TB-2.1 codex rerun (fresh) · glm-5.3-flash · $(date '+%F %T') ==="
echo "Benchmark: TB-2.1 / 89 tasks / 7-way concurrent (NOT comparable with TB4)"
if [[ ! -d "$TB_DATASET" ]]; then echo "FATAL: dataset not found" >&2; exit 1; fi
curl -s -o /dev/null http://127.0.0.1:9092/v1/models 2>/dev/null || { echo "FATAL: gw_proxy 9092 down" >&2; exit 1; }
echo "gw_proxy 9092: OK"
HJ="$JOBS_BASE/codex"; mkdir -p "$HJ" "$TRACES_DIR"
echo "--- [$(date '+%H:%M:%S')] codex (89 tasks, fresh rerun) ---"
nice -n 19 harbor run -p "$TB_DATASET" --agent "terminalbench.agents.codex:CodexTB" -k 1 --n-concurrent 1 \
    --extra-docker-compose "$TB_OVERLAY" --jobs-dir "$HJ" \
    2>&1 | tee "$TRACES_DIR/tb21_codex_run2.log" || echo "WARNING: codex errors"
echo "--- [$(date '+%H:%M:%S')] codex rerun done ---"
