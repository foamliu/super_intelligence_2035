#!/usr/bin/env bash
# rerun_opencode_tb21.sh — restart stuck opencode TB-2.1 (29/89 → 89/89)
# R2090: opencode TB-2.1 died at 29/89 ("Docker daemon not running" error)
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
export TB_AGENT_TIMEOUT=3600
export PYTHONPATH="$HARNESS_DIR:${PYTHONPATH:-}"
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"
HJ="$JOBS_BASE/opencode"; mkdir -p "$HJ" "$TRACES_DIR"
echo "=== [$(date '+%F %T')] opencode TB-2.1 rerun (resume from 29/89) ==="
echo "Benchmark: TB-2.1 / 89 tasks / 7-way concurrent (NOT comparable with TB4)"
echo "Model: glm-5.3-flash | gw_proxy: 9092"
nice -n 19 harbor run -p "$TB_DATASET" \
    --agent terminalbench.agents.opencode:OpenCodeTB \
    -k 1 --n-concurrent 1 \
    --extra-docker-compose "$TB_OVERLAY" \
    --jobs-dir "$HJ" \
    2>&1 | tee "$TRACES_DIR/tb21_opencode_rerun.log" || echo "WARNING: opencode rerun errors"
echo "=== [$(date '+%F %T')] opencode TB-2.1 rerun done ==="
