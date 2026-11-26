#!/usr/bin/env bash
# R469: Re-run ONLY codex + claude-code pilot (5 tasks each).
# Fixes applied:
#   - codex.py: removed `chmod +x` that caused EROFS on ro NFS mount (R468)
#   - claude_code.py: same chmod removal (R468)
#   - NFS perms: chmod 755 on @anthropic-ai/ + claude-code/ + @openai/ + codex/ dirs
#     (were 750, agent user couldn't traverse → exit 127)
set -euo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[rerun] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor)"
[[ -n "${TB_API_KEY:-}" ]] || { echo "FATAL: TB_API_KEY empty"; exit 1; }

SCRIPT_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
cd "$SCRIPT_DIR" || { echo "FATAL: cd failed"; exit 2; }
export PYTHONPATH="${SCRIPT_DIR}/..:${PYTHONPATH:-}"

# --- Start gw_proxy ---
GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"
GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1"

if curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null; then
    echo "[rerun] gw_proxy already running on 9090"
else
    echo "[rerun] starting gw_proxy..."
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="$GW_UPSTREAM" GW_PROXY_PORT=9090 \
        python3 "$GW_PROXY_PY" >/tmp/tb_gw_proxy.log 2>&1 &
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="$GW_UPSTREAM" GW_PROXY_PORT=9091 \
        python3 "$GW_PROXY_DSH_PY" >/tmp/tb_gw_proxy_dsh.log 2>&1 &
    sleep 3
    for i in $(seq 1 10); do
        if curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null; then break; fi
        sleep 0.5
    done
    if ! curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null; then
        echo "ERROR: gw_proxy did not start"; cat /tmp/tb_gw_proxy.log; exit 1
    fi
    echo "[rerun] gw_proxy up on 9090+9091"
fi

# --- Build pilot dataset ---
TB_TASKS_DIR="${HOME}/terminal-bench"
PILOT_DATASET="$(mktemp -d -t tb_rerun_dataset_XXXXXX)"
for task in break-filter-js-from-html bn-fit-modify log-summary-date-ranges chess-best-move fix-git; do
    ln -sf "${TB_TASKS_DIR}/${task}" "${PILOT_DATASET}/${task}"
done
echo "[rerun] pilot dataset: $PILOT_DATASET"

TB_OVERLAY="${SCRIPT_DIR}/overlay-network-host.yml"
TRACES_DIR="${SCRIPT_DIR}/traces"

# --- Re-run codex ---
echo "=== Re-running codex (5 tasks) ==="
nice -n 19 harbor run \
    -p "$PILOT_DATASET" \
    --agent "terminalbench.agents.codex:CodexTB" \
    -k 1 --n-concurrent 1 \
    --extra-docker-compose "$TB_OVERLAY" \
    --jobs-dir "${SCRIPT_DIR}/jobs_codex_rerun" \
    2>&1 | tee "${TRACES_DIR}/codex_rerun.log" || {
        echo "WARNING: codex rerun failed"
    }
echo "--- codex rerun done ---"

# --- Re-run claude-code ---
echo "=== Re-running claude-code (5 tasks) ==="
nice -n 19 harbor run \
    -p "$PILOT_DATASET" \
    --agent "terminalbench.agents.claude_code:ClaudeCodeTB" \
    -k 1 --n-concurrent 1 \
    --extra-docker-compose "$TB_OVERLAY" \
    --jobs-dir "${SCRIPT_DIR}/jobs_claude-code_rerun" \
    2>&1 | tee "${TRACES_DIR}/claude-code_rerun.log" || {
        echo "WARNING: claude-code rerun failed"
    }
echo "--- claude-code rerun done ---"

echo ""
echo "=== Re-run complete ==="
echo "Check results in jobs_codex_rerun/ and jobs_claude-code_rerun/"
