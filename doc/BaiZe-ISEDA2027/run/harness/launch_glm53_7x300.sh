#!/bin/bash
# launch_glm53_7x300.sh — 7×300 SWE-bench Lite cross-eval with glm-5.3-flash (2026-10-14 directive)
#
# Reuses the 7×300 framework but switches backbone to glm-5.3-flash.
# Results saved to glm53_pilot_results.json (NOT kimi_pilot_results.json).
#
# Architecture:
#   - cline: direct to gateway (OPENAI_API_KEY = glm53 key, HARNESS_MODEL = glm-5.3-flash)
#   - codex/opencode/claude-code/pi/hermes: through NEW gw_proxy on port 9092 (glm53 key)
#   - deepseek-harness: through NEW gw_proxy_dsh on port 9093 (glm53 key)
#   - kimi rerun (port 9090/9091) continues undisturbed
#
# Usage: bash launch_glm53_7x300.sh
# ETA: ~42h wall (7 parallel, each serial, N=1)

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_glm53"
mkdir -p "$LOGDIR"

GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
# 2026-10-14 FIX: glm53 key returns 403 on /cloud/v1 (MSE Gateway Basic auth),
# but works on /v1 (HTTP 200 verified). Task instruction said /cloud/v1 but
# the key is only provisioned for the /v1 endpoint.
GLM53_BASE="http://agi-gateway.cxmt.com/v1"
GW_PROXY_PORT_GLM53="9092"
GW_DSH_PORT_GLM53="9093"
RESULTS_FILE="$HERE/glm53_pilot_results.json"

PYTHON="${PYTHON:-python3}"
RUN_SCRIPT="$HERE/run_serial_kimi.py"
GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

# ── Step 0: curl probe ──
echo "========================================"
echo "Step 0: API connectivity probe"
echo "========================================"
HTTP_CODE=$(curl -sS -m 15 -o /tmp/glm53_probe_resp.txt -w '%{http_code}' \
  -X POST "${GLM53_BASE}/chat/completions" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${GLM53_KEY}" \
  -d "{\"model\":\"${GLM53_MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"max_tokens\":10}" 2>&1 || echo "000")

echo "  HTTP response code: $HTTP_CODE"
if [ "$HTTP_CODE" != "200" ]; then
  echo "BLOCKER: glm-5.3-flash API key returned HTTP $HTTP_CODE (expected 200)"
  echo "  Response: $(cat /tmp/glm53_probe_resp.txt 2>/dev/null | head -5)"
  echo "  Cannot start the run. Verify the API key is provisioned on the gateway."
  exit 1
fi
echo "API probe passed (HTTP 200)"

# ── Step 1: Start gw_proxy instances for glm53 ──
echo "Starting gw_proxy instances (port $GW_PROXY_PORT_GLM53 + $GW_DSH_PORT_GLM53)"
if ! pgrep -f "gw_proxy.py.*GW_PROXY_PORT=$GW_PROXY_PORT_GLM53" > /dev/null 2>&1; then
  cd /nas_train/app.e0031982/harness_work
  GW_UPSTREAM=http://agi-gateway.cxmt.com/v1 \
  GW_API_KEY="$GLM53_KEY" GW_PROXY_PORT="$GW_PROXY_PORT_GLM53" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_PY" > /tmp/gw_proxy_glm53.log 2>&1 &
  echo "  Started gw_proxy (port $GW_PROXY_PORT_GLM53) PID=$!"
  sleep 2
else
  echo "  gw_proxy (port $GW_PROXY_PORT_GLM53) already running"
fi

if ! pgrep -f "gw_proxy_dsh.py.*GW_PROXY_PORT=$GW_DSH_PORT_GLM53" > /dev/null 2>&1; then
  cd /nas_train/app.e0031982/harness_work
  GW_UPSTREAM=http://agi-gateway.cxmt.com/v1 \
  GW_API_KEY="$GLM53_KEY" GW_PROXY_PORT="$GW_DSH_PORT_GLM53" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_DSH_PY" > /tmp/gw_proxy_dsh_glm53.log 2>&1 &
  echo "  Started gw_proxy_dsh (port $GW_DSH_PORT_GLM53) PID=$!"
  sleep 2
else
  echo "  gw_proxy_dsh (port $GW_DSH_PORT_GLM53) already running"
fi
cd "$HERE"

# ── Step 2: Backup & update config files (cline, pi, hermes, opencode) ──
echo "Updating config files for glm-5.3-flash"
PI_CFG="$HOME/.pi/agent/models.json"
HERMES_CFG="$HOME/.hermes/config.yaml"
OPENCODE_CFG="$HOME/.config/opencode/opencode.json"
CLINE_GS="$HOME/.cline/data/globalState.json"

for cfg in "$PI_CFG" "$HERMES_CFG" "$OPENCODE_CFG" "$CLINE_GS"; do
  if [ -f "$cfg" ] && [ ! -f "${cfg}.kimi_backup" ]; then
    cp "$cfg" "${cfg}.kimi_backup"
    echo "  Backed up: $cfg -> ${cfg}.kimi_backup"
  fi
done

# Update cline globalState.json: change openAiBaseUrl from /cloud/v1 to /v1
# (glm53 key only works on /v1, not /cloud/v1 — 2026-10-14 verified)
if [ -f "$CLINE_GS" ]; then
  python3 -c "
import json, pathlib
p = pathlib.Path('$CLINE_GS')
d = json.loads(p.read_text())
old = d.get('openAiBaseUrl', '')
if '/cloud/v1' in old:
    d['openAiBaseUrl'] = old.replace('/cloud/v1', '/v1')
    p.write_text(json.dumps(d, indent=2))
    print(f'  Updated cline openAiBaseUrl: {old} -> {d[\"openAiBaseUrl\"]}')
else:
    print(f'  cline openAiBaseUrl already OK: {old}')
"
fi

# ALSO update cline-patched harness data dir globalState.json (2026-10-14 fix)
# cline-patched uses --data-dir /nas_train/app.e0031982/harness_work/cline_harness_data
# (run_single.py:28), NOT ~/.cline/data/. Its globalState.json has openAiBaseUrl
# pointing at the kimi proxy (port 9090) — must switch to glm53 proxy (port 9092).
CLINE_HARNESS_GS="/nas_train/app.e0031982/harness_work/cline_harness_data/globalState.json"
if [ -f "$CLINE_HARNESS_GS" ]; then
  python3 -c "
import json, pathlib
p = pathlib.Path('$CLINE_HARNESS_GS')
d = json.loads(p.read_text())
old = d.get('openAiBaseUrl', '')
if '9090' in old:
    d['openAiBaseUrl'] = old.replace('9090', '${GW_PROXY_PORT_GLM53}')
    d['actModeOpenAiModelId'] = '${GLM53_MODEL}'
    d['planModeOpenAiModelId'] = '${GLM53_MODEL}'
    p.write_text(json.dumps(d, indent=2))
    print(f'  Updated cline-patched harness GS: {old} -> {d[\"openAiBaseUrl\"]}')
else:
    print(f'  cline-patched harness GS already OK: {old}')
"
fi

# Update pi config: change baseUrl to 9092, add glm-5.3-flash model
python3 -c "
import json, pathlib
p = pathlib.Path('$PI_CFG')
d = json.loads(p.read_text())
d['providers']['gw']['baseUrl'] = 'http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1'
models = d['providers']['gw'].setdefault('models', [])
if not any(m.get('id') == '$GLM53_MODEL' for m in models):
    models.append({'id': '$GLM53_MODEL', 'name': 'GLM 5.3 Flash (via gw_proxy)', 'reasoning': False, 'input': ['text'], 'contextWindow': 131072, 'maxTokens': 8192})
p.write_text(json.dumps(d, indent=2))
print('  Updated pi config')
"

# Update hermes config: change base_url to 9092
python3 -c "
import pathlib
p = pathlib.Path('$HERMES_CFG')
text = p.read_text()
text = text.replace('http://127.0.0.1:9090/v1', 'http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1')
p.write_text(text)
print('  Updated hermes config')
"

# Update opencode config: change baseURL to 9092, add glm-5.3-flash model
python3 -c "
import json, pathlib
p = pathlib.Path('$OPENCODE_CFG')
d = json.loads(p.read_text())
d['provider']['gw']['options']['baseURL'] = 'http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1'
d['model'] = 'gw/$GLM53_MODEL'
models = d['provider']['gw'].setdefault('models', {})
models['$GLM53_MODEL'] = {'name': '$GLM53_MODEL', 'tool_call': True, 'reasoning': True}
p.write_text(json.dumps(d, indent=2))
print('  Updated opencode config')
"

# ── Step 3: Launch 7 harnesses in parallel ──
echo "========================================"
echo "7x300 with glm-5.3-flash | Start: $(date)"
echo "  Model: $GLM53_MODEL | Results: $RESULTS_FILE"
echo "  7 parallel, each serial (N=1) | --resume"
echo "========================================"

export HARNESS_MODEL="$GLM53_MODEL"
export OPENAI_API_KEY="$GLM53_KEY"
export RESULTS_PATH="$RESULTS_FILE"
export GW_PROXY_PORT="$GW_PROXY_PORT_GLM53"
export GW_DSH_PORT="$GW_DSH_PORT_GLM53"
export PATH="$HOME/.bun/bin:$PATH"
export PYTHONUNBUFFERED=1
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

PIDS=()
for h in "${HARNESSES[@]}"; do
  LOG="$LOGDIR/${h}_glm53.log"
  echo "Starting $h -> $LOG"
  nice -n 10 nohup $PYTHON "$RUN_SCRIPT" \
    --harness "$h" --all-prepared --resume \
    > "$LOG" 2>&1 &
  PID=$!
  PIDS+=($PID)
  echo "  PID=$PID"
  sleep 2
done

echo ""
echo "All 7 launched. PIDs: ${PIDS[*]}"
echo "Logs: $LOGDIR/<harness>_glm53.log"
echo "Monitor: tail -f $LOGDIR/*_glm53.log"
echo "Status:  ps -eo pid=,etimes=,args= | grep run_serial_kimi | grep -v grep"
echo "Results: $RESULTS_FILE"
echo "ETA: ~42h wall (N=1)"
echo ""
echo "Restore kimi configs after run:"
echo "  for cfg in ~/.pi/agent/models.json ~/.hermes/config.yaml ~/.config/opencode/opencode.json ~/.cline/data/globalState.json; do"
echo "    [ -f \"\${cfg}.kimi_backup\" ] && cp \"\${cfg}.kimi_backup\" \"\$cfg\" && echo \"Restored \$cfg\""
echo "  done"
