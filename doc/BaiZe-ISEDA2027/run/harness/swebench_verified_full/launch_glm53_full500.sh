#!/bin/bash
# launch_glm53_full500.sh — SWE-bench Verified full-500 x glm-5.3-flash x 7 harnesses
# (2026-11-06 directive: glm-5.3-flash retest SWE-bench Verified x7)
# Config setup copied from launch_glm53_7x300.sh Step1-Step2.
#   cline: direct gateway; codex/opencode/claude-code/pi/hermes: gw_proxy 9092; dsh: gw_proxy_dsh 9093
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_glm53"
mkdir -p "$LOGDIR"
GLM53_MODEL="glm-5.3-flash"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
GLM53_BASE="http://agi-gateway.cxmt.com/v1"
GW_PROXY_PORT_GLM53="9092"
GW_DSH_PORT_GLM53="9093"
PYTHON="${PYTHON:-python3}"
ORCHESTRATOR="$HERE/run_verified_full.py"
GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")
PI_CFG="$HOME/.pi/agent/models.json"
HERMES_CFG="$HOME/.hermes/config.yaml"
OPENCODE_CFG="$HOME/.config/opencode/opencode.json"
CLINE_GS="$HOME/.cline/data/globalState.json"
CLINE_HARNESS_GS="/nas_train/app.e0031982/harness_work/cline_harness_data/globalState.json"
PHASE="${1:-predict}"

# Step 0: curl probe
HTTP_CODE=$(curl -sS -m 60 -o /tmp/glm53_full500_probe.txt -w '%{http_code}' \
  -X POST "${GLM53_BASE}/chat/completions" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${GLM53_KEY}" \
  -d "{\"model\":\"${GLM53_MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"max_tokens\":10}" 2>&1 || echo "000")
echo "API probe: HTTP $HTTP_CODE"
if [ "$HTTP_CODE" != "200" ]; then
  echo "FATAL: API probe HTTP $HTTP_CODE != 200. ABORTING."; exit 1
fi
echo "API probe passed (HTTP 200)"

# Step 1: Start gw_proxy instances
if ! pgrep -f "gw_proxy.py.*GW_PROXY_PORT=$GW_PROXY_PORT_GLM53" >/dev/null 2>&1; then
  cd /nas_train/app.e0031982/harness_work
  GW_UPSTREAM=http://agi-gateway.cxmt.com/v1 \
  GW_API_KEY="$GLM53_KEY" GW_PROXY_PORT="$GW_PROXY_PORT_GLM53" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_PY" > /tmp/gw_proxy_glm53_full500.log 2>&1 &
  echo "Started gw_proxy (port $GW_PROXY_PORT_GLM53) PID=$!"; sleep 2
else
  echo "gw_proxy (port $GW_PROXY_PORT_GLM53) already running"
fi
if ! pgrep -f "gw_proxy_dsh.py.*GW_PROXY_PORT=$GW_DSH_PORT_GLM53" >/dev/null 2>&1; then
  cd /nas_train/app.e0031982/harness_work
  GW_UPSTREAM=http://agi-gateway.cxmt.com/v1 \
  GW_API_KEY="$GLM53_KEY" GW_PROXY_PORT="$GW_DSH_PORT_GLM53" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_DSH_PY" > /tmp/gw_proxy_dsh_glm53_full500.log 2>&1 &
  echo "Started gw_proxy_dsh (port $GW_DSH_PORT_GLM53) PID=$!"; sleep 2
else
  echo "gw_proxy_dsh (port $GW_DSH_PORT_GLM53) already running"
fi

# Step 2: Backup & update config files
for cfg in "$PI_CFG" "$HERMES_CFG" "$OPENCODE_CFG" "$CLINE_GS" "$CLINE_HARNESS_GS"; do
  [ -f "$cfg" ] && [ ! -f "${cfg}.glm53_backup" ] && cp "$cfg" "${cfg}.glm53_backup" && echo "Backed up $cfg"
done

# cline GS -> direct gateway /v1
[ -f "$CLINE_GS" ] && python3 -c "
import json,pathlib
p=pathlib.Path('$CLINE_GS');d=json.loads(p.read_text());old=d.get('openAiBaseUrl','')
if '/cloud/v1' in old or '9090' in old:
    d['openAiBaseUrl']='${GLM53_BASE}';d['actModeOpenAiModelId']='${GLM53_MODEL}';d['planModeOpenAiModelId']='${GLM53_MODEL}';p.write_text(json.dumps(d,indent=2));print(f'cline GS: {old}->{d[\"openAiBaseUrl\"]}')
else: print(f'cline GS OK: {old}')
"

# cline-patched harness GS
[ -f "$CLINE_HARNESS_GS" ] && python3 -c "
import json,pathlib
p=pathlib.Path('$CLINE_HARNESS_GS');d=json.loads(p.read_text());old=d.get('openAiBaseUrl','')
if '9090' in old:
    d['openAiBaseUrl']=old.replace('9090','${GW_PROXY_PORT_GLM53}').replace('/cloud/v1','/v1')
elif '/cloud/v1' in old:
    d['openAiBaseUrl']='${GLM53_BASE}'
else:
    print(f'cline-patch GS OK: {old}');exit()
d['actModeOpenAiModelId']='${GLM53_MODEL}';d['planModeOpenAiModelId']='${GLM53_MODEL}';p.write_text(json.dumps(d,indent=2));print(f'cline-patch GS: {old}->{d[\"openAiBaseUrl\"]}')
"

# cline-patched harness providers.json (cline v3.0.51 reads this, NOT globalState.json)
CLINE_HARNESS_PROVIDERS="/nas_train/app.e0031982/harness_work/cline_harness_data/settings/providers.json"
if [ -f "$CLINE_HARNESS_PROVIDERS" ]; then
  python3 -c "
import json,pathlib
p=pathlib.Path('$CLINE_HARNESS_PROVIDERS');d=json.loads(p.read_text())
s=d.get('providers',{}).get('openai-compatible',{}).get('settings',{})
old=s.get('baseUrl','')
s['baseUrl']='http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1'
s['apiKey']='dummy-key-for-proxy'
s['model']='${GLM53_MODEL}'
d['providers']['openai-compatible']['settings']=s
p.write_text(json.dumps(d,indent=2));print(f'cline-patch providers.json: {old}->http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1')
"
fi

# cline-patched harness secrets.json (cline also reads this for API key)
CLINE_HARNESS_SECRETS="/nas_train/app.e0031982/harness_work/cline_harness_data/secrets.json"
if [ -f "$CLINE_HARNESS_SECRETS" ]; then
  python3 -c "
import json,pathlib
p=pathlib.Path('$CLINE_HARNESS_SECRETS');d=json.loads(p.read_text())
d['openAiApiKey']='dummy-key-for-proxy'
p.write_text(json.dumps(d,indent=2));print('cline-patch secrets.json: set to dummy-key-for-proxy')
"
fi

# Clear stale deepseek-harness sessions
rm -rf /tmp/dsh_home/* 2>/dev/null
echo "Cleared /tmp/dsh_home for deepseek-harness"

# pi config
python3 -c "
import json,pathlib
p=pathlib.Path('$PI_CFG');d=json.loads(p.read_text())
d.setdefault('providers',{}).setdefault('gw',{}).setdefault('options',{})
d['providers']['gw']['baseUrl']='http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1'
models=d['providers']['gw'].setdefault('models',[])
if not any(m.get('id')=='$GLM53_MODEL' for m in models):
    models.append({'id':'$GLM53_MODEL','name':'GLM 5.3 Flash','reasoning':False,'input':['text'],'contextWindow':131072,'maxTokens':8192})
p.write_text(json.dumps(d,indent=2));print('pi config updated')
"

# hermes config
python3 -c "
import pathlib
p=pathlib.Path('$HERMES_CFG');t=p.read_text()
t=t.replace('http://127.0.0.1:9090/v1','http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1')
t=t.replace('http://127.0.0.1:9091/v1','http://127.0.0.1:${GW_DSH_PORT_GLM53}/v1')
p.write_text(t);print('hermes config updated')
"

# opencode config
python3 -c "
import json,pathlib
p=pathlib.Path('$OPENCODE_CFG');d=json.loads(p.read_text())
d.setdefault('provider',{}).setdefault('gw',{}).setdefault('options',{})
d['provider']['gw']['options']['baseURL']='http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1'
d['model']='gw/$GLM53_MODEL'
models=d['provider']['gw'].setdefault('models',{})
models['$GLM53_MODEL']={'name':'$GLM53_MODEL','tool_call':True,'reasoning':True}
p.write_text(json.dumps(d,indent=2));print('opencode config updated')
"

# codex config.toml (codex reads ~/.codex/config.toml, NOT env vars, for base_url)
CODEX_TOML="$HOME/.codex/config.toml"
if [ -f "$CODEX_TOML" ]; then
  [ ! -f "${CODEX_TOML}.glm53_backup" ] && cp "$CODEX_TOML" "${CODEX_TOML}.glm53_backup"
  python3 -c "
p='$CODEX_TOML';text=open(p).read()
text=text.replace('http://127.0.0.1:9090/v1','http://127.0.0.1:${GW_PROXY_PORT_GLM53}/v1')
text=text.replace('http://127.0.0.1:9091/v1','http://127.0.0.1:${GW_DSH_PORT_GLM53}/v1')
text=text.replace('model = \"kimi-k2.6-cloud\"','model = \"${GLM53_MODEL}\"')
text=text.replace('model = \"deepseek-v4-flash\"','model = \"${GLM53_MODEL}\"')
open(p,'w').write(text);print('codex config.toml updated (base_url -> ${GW_PROXY_PORT_GLM53}, model -> ${GLM53_MODEL})')
"
fi

# Step 3: Set env vars and launch
export HARNESS_MODEL="$GLM53_MODEL"
export OPENAI_API_KEY="$GLM53_KEY"
export MODEL_SUFFIX="$GLM53_MODEL"
export RUN_ID_PREFIX="verified_full_glm53"
export EVAL_TAG="glm53_"
export PRED_SUBDIR="predictions_glm53"
export WORKDIR_TAG="_glm53"
export GW_PROXY_PORT="$GW_PROXY_PORT_GLM53"
export GW_DSH_PORT="$GW_DSH_PORT_GLM53"
export PATH="$HOME/.bun/bin:$PATH"
export PYTHONUNBUFFERED=1
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

if [ "$PHASE" = "predict" ]; then
  echo "=== glm53 full500 PREDICT | $(date) | 7 parallel ==="
  PIDS=()
  for h in "${HARNESSES[@]}"; do
    LOG="$LOGDIR/predict_${h}_glm53.log"
    echo "Starting predict $h -> $LOG"
    nice -n 10 nohup $PYTHON "$ORCHESTRATOR" predict --harness "$h" > "$LOG" 2>&1 &
    PIDS+=($!); echo "  PID=$!"; sleep 2
  done
  echo "All 7 predict launched. PIDs: ${PIDS[*]}"
  echo "Logs: $LOGDIR/predict_*_glm53.log"
elif [ "$PHASE" = "eval" ]; then
  H="${HARNESS:-}"
  [ -z "$H" ] && { echo "ERROR: HARNESS=... bash $0 eval"; exit 1; }
  echo "=== glm53 full500 EVAL | $H | $(date) ==="
  EVAL_MAX_WORKERS="${EVAL_MAX_WORKERS:-8}" $PYTHON "$ORCHESTRATOR" eval --harness "$H"
elif [ "$PHASE" = "all" ]; then
  H="${HARNESS:-}"
  [ -z "$H" ] && { echo "ERROR: HARNESS=... bash $0 all"; exit 1; }
  echo "=== glm53 full500 ALL | $H | $(date) ==="
  EVAL_MAX_WORKERS="${EVAL_MAX_WORKERS:-8}" $PYTHON "$ORCHESTRATOR" all --harness "$H"
else
  echo "Unknown phase: $PHASE. Use: predict|eval|all"; exit 1
fi
echo "Restore kimi configs: for cfg in ~/.pi/agent/models.json ~/.hermes/config.yaml ~/.config/opencode/opencode.json ~/.cline/data/globalState.json /nas_train/app.e0031982/harness_work/cline_harness_data/globalState.json; do [ -f \"\${cfg}.glm53_backup\" ] && cp \"\${cfg}.glm53_backup\" \"\$cfg\"; done"
