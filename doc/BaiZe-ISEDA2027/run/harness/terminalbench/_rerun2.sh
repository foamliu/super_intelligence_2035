#!/usr/bin/env bash
# R470: Re-run codex + claude-code pilot (5 tasks each) with setsid detachment.
# Fixes: codex chmod removal (R468), NFS perms 755 (R469).
set -uo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
SCRIPT_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[rerun2] HOST=$(hostname) key_len=${#TB_API_KEY} harbor=$(command -v harbor)"
[[ -n "${TB_API_KEY:-}" ]] || { echo "FATAL: key empty"; exit 1; }
cd "$SCRIPT_DIR" || exit 2
export PYTHONPATH="${SCRIPT_DIR}/..:${PYTHONPATH:-}"

# Pilot dataset
PILOT_DS="/tmp/tb_rerun_ds_TJk8k3"
TB_OVERLAY="$SCRIPT_DIR/overlay-network-host.yml"

# --- gw_proxy check ---
if ! curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null; then
    echo "[rerun2] starting gw_proxy on 9090..."
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1" GW_PROXY_PORT=9090 \
        python3 /nas_train/app.e0031982/harness_work/gw_proxy.py >>/tmp/tb_gw_proxy.log 2>&1 &
    sleep 3
fi
curl -s -o /dev/null -w "gw_proxy_9090=%{http_code}\n" http://127.0.0.1:9090/ 2>/dev/null

# --- Re-run codex ---
echo "=== Re-running codex (5 tasks) at $(date '+%F %T') ==="
sg docker -c "export TB_API_KEY='$TB_API_KEY' PATH='/home/app.e0031982/.local/bin:$PATH'; nice -n 19 harbor run -p $PILOT_DS --agent terminalbench.agents.codex:CodexTB -k 1 --n-concurrent 1 --extra-docker-compose $TB_OVERLAY --jobs-dir $SCRIPT_DIR/jobs_codex_rerun" 2>&1 | tee "$SCRIPT_DIR/traces/codex_rerun2.log"
echo "--- codex done at $(date '+%F %T') ---"

# --- Re-run claude-code ---
echo "=== Re-running claude-code (5 tasks) at $(date '+%F %T') ==="
sg docker -c "export TB_API_KEY='$TB_API_KEY' PATH='/home/app.e0031982/.local/bin:$PATH'; nice -n 19 harbor run -p $PILOT_DS --agent terminalbench.agents.claude_code:ClaudeCodeTB -k 1 --n-concurrent 1 --extra-docker-compose $TB_OVERLAY --jobs-dir $SCRIPT_DIR/jobs_claude-code_rerun" 2>&1 | tee "$SCRIPT_DIR/traces/claude-code_rerun2.log"
echo "--- claude-code done at $(date '+%F %T') ---"

echo ""
echo "=== Re-run2 complete at $(date '+%F %T') ==="
echo "Results: jobs_codex_rerun/ and jobs_claude-code_rerun/"
