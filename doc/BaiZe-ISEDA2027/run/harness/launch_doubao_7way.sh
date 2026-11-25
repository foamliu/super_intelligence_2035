#!/bin/bash
# launch_doubao_7way.sh — SWE-bench Verified 500 × 7 harnesses with doubao-seed-2.0-pro-cloud
#
# User order 2026-11-25: switch from glm-5.3-flash to doubao-pro for SWE-bench Verified.
# Doubao has low daytime usage → run 7-way concurrent during the day (no night window needed).
# Token usage recorded via gw_proxy sidecar (/tmp/gw_proxy_usage.jsonl) — code already deployed.
#
# MM 2×3 (ports 9095+) is independent and must NOT be disturbed.
#
# Usage:
#   bash launch_doubao_7way.sh                # launch all 7 harnesses
#   bash launch_doubao_7way.sh status         # show progress
#   bash launch_doubao_7way.sh stop           # kill all 7 + proxies (not MM)
#
# Architecture:
#   - gw_proxy  (9090): doubao → /cloud/v1  (codex/opencode/cc/pi/hermes + cline env)
#   - gw_proxy  (9092): doubao → /cloud/v1  (cline globalState.json fallback)
#   - gw_proxy_dsh (9091): doubao → /cloud   (deepseek-harness)
#   - MM proxies (9095+): untouched

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VF_DIR="$HERE/swebench_verified_full"
LOGDIR="$HERE/logs_doubao_pro"
mkdir -p "$LOGDIR"

# ── Model & API config ──
DOUBAO_MODEL="doubao-seed-2.0-pro-cloud"
DOUBAO_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f"
# gw_proxy needs upstream WITHOUT /v1 suffix (it prepends _UP_PATH_PREFIX)
DOUBAO_UPSTREAM="http://agi-gateway.cxmt.com/cloud"

GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"

# gw_proxy ports (same as existing infra, will be killed & restarted)
GW_PORT_MAIN="9090"   # codex/opencode/cc/pi/hermes + cline OPENAI_BASE_URL env
GW_PORT_CLINE="9092"  # cline globalState.json fallback
GW_PORT_DSH="9091"     # deepseek-harness

HARNESSES=("cline-patched" "codex" "opencode" "pi" "claude-code" "hermes" "deepseek-harness")

# ── Env vars for run_verified_full.py ──
export HARNESS_MODEL="$DOUBAO_MODEL"
export MODEL_SUFFIX="$DOUBAO_MODEL"
export PRED_SUBDIR="predictions_doubao_pro"
export WORKDIR_TAG="_doubao_pro"
export EVAL_TAG="doubao_pro_"
export PREDICT_WORKERS="${PREDICT_WORKERS:-1}"
export PATH="$HOME/.bun/bin:$PATH"
export PYTHONUNBUFFERED=1
export GW_USAGE_LOG="/tmp/gw_proxy_usage.jsonl"
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true

# ────────────────────────────────────────────────────────────────────────────
# status subcommand
# ────────────────────────────────────────────────────────────────────────────
if [ "${1:-}" = "status" ]; then
  echo "=== SWE-bench Verified · doubao-pro 7-way status ==="
  echo ""
  for h in "${HARNESSES[@]}"; do
    pf="$VF_DIR/reports/progress_${EVAL_TAG}${h}.json"
    done_n=0; patch_n=0; infra_n=0
    if [ -f "$pf" ]; then
      read -r done_n patch_n infra_n < <(python3 -c "
import json,sys
d=json.load(open('$pf'))
r=d.get('results',[])
print(len(r), sum(1 for x in r if x.get('model_patch_len',0)>0), sum(1 for x in r if x.get('classification') in ('infra','blocked')))
" 2>/dev/null || echo "0 0 0")
    fi
    running=$(pgrep -f "run_verified_full.py predict --harness $h" >/dev/null 2>&1 && echo "RUN" || echo "idle")
    # token sum
    tok_in=0; tok_out=0
    if [ -f "$pf" ]; then
      read -r tok_in tok_out < <(python3 -c "
import json
d=json.load(open('$pf'))
ti=to=0
for x in d.get('results',[]):
    it=x.get('input_tokens'); ot=x.get('output_tokens')
    if it: ti+=it
    if ot: to+=ot
print(ti,to)
" 2>/dev/null || echo "0 0")
    fi
    printf '  %-20s %3s/500 done | patch=%3s infra=%3s | tok_in=%s tok_out=%s | %s\n' \
      "$h" "$done_n" "$patch_n" "$infra_n" "$tok_in" "$tok_out" "$running"
  done
  echo ""
  echo "Proxies:"
  for port in $GW_PORT_MAIN $GW_PORT_CLINE $GW_PORT_DSH; do
    running=$(pgrep -f "gw_proxy.*GW_PROXY_PORT=$port" >/dev/null 2>&1 && echo "UP" || echo "DOWN")
    echo "  port $port: $running"
  done
  exit 0
fi

# ────────────────────────────────────────────────────────────────────────────
# stop subcommand
# ────────────────────────────────────────────────────────────────────────────
if [ "${1:-}" = "stop" ]; then
  echo "Stopping doubao-pro 7-way predict + proxies (NOT touching MM)..."
  for h in "${HARNESSES[@]}"; do
    pkill -f "run_verified_full.py predict --harness $h" 2>/dev/null || true
  done
  for port in $GW_PORT_MAIN $GW_PORT_CLINE $GW_PORT_DSH; do
    pkill -f "gw_proxy.*GW_PROXY_PORT=$port" 2>/dev/null || true
    pkill -f "gw_proxy_dsh.*GW_PROXY_PORT=$port" 2>/dev/null || true
  done
  echo "Done. MM processes untouched."
  exit 0
fi

# ────────────────────────────────────────────────────────────────────────────
# Step 0: API probe
# ────────────────────────────────────────────────────────────────────────────
echo "========================================"
echo "Step 0: doubao-pro API connectivity probe"
echo "========================================"
HTTP_CODE=$(curl -sS -m 60 -o /tmp/doubao_probe_resp.txt -w '%{http_code}' \
  -X POST "${DOUBAO_UPSTREAM}/v1/chat/completions" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${DOUBAO_KEY}" \
  -d "{\"model\":\"${DOUBAO_MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"max_tokens\":10}" 2>&1 || echo "000")
echo "  HTTP response code: $HTTP_CODE"
if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: doubao-pro API probe failed (HTTP $HTTP_CODE)"
  echo "  Response: $(cat /tmp/doubao_probe_resp.txt 2>/dev/null | head -5)"
  echo "  Aborting."
  exit 1
fi
echo "API probe passed (HTTP 200)"

# ────────────────────────────────────────────────────────────────────────────
# Step 1: Kill old glm53 proxies (9090/9091/9092) and start doubao proxies
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Step 1: Restart gw_proxy with doubao-pro config"
echo "========================================"

for port in $GW_PORT_MAIN $GW_PORT_CLINE; do
  pkill -f "gw_proxy.py.*GW_PROXY_PORT=$port" 2>/dev/null || true
done
pkill -f "gw_proxy_dsh.py.*GW_PROXY_PORT=$GW_PORT_DSH" 2>/dev/null || true
sleep 1

cd /nas_train/app.e0031982/harness_work

# 9090: main proxy (codex/opencode/cc/pi/hermes + cline env)
GW_API_KEY="$DOUBAO_KEY" GW_UPSTREAM="$DOUBAO_UPSTREAM" \
  GW_PROXY_PORT="$GW_PORT_MAIN" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_PY" > /tmp/gw_proxy_doubao_9090.log 2>&1 &
echo "  Started gw_proxy (port $GW_PORT_MAIN) PID=$!"
sleep 1

# 9092: cline globalState.json fallback
GW_API_KEY="$DOUBAO_KEY" GW_UPSTREAM="$DOUBAO_UPSTREAM" \
  GW_PROXY_PORT="$GW_PORT_CLINE" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_PY" > /tmp/gw_proxy_doubao_9092.log 2>&1 &
echo "  Started gw_proxy (port $GW_PORT_CLINE) PID=$!"
sleep 1

# 9091: deepseek-harness (dsh variant)
GW_API_KEY="$DOUBAO_KEY" GW_UPSTREAM="$DOUBAO_UPSTREAM" \
  GW_PROXY_PORT="$GW_PORT_DSH" GW_PROXY_HOST=127.0.0.1 \
  setsid python3 "$GW_PROXY_DSH_PY" > /tmp/gw_proxy_doubao_9091.log 2>&1 &
echo "  Started gw_proxy_dsh (port $GW_PORT_DSH) PID=$!"
sleep 2

cd "$HERE"

# Truncate usage sidecar (fresh start)
: > "$GW_USAGE_LOG"
echo "  Truncated usage sidecar: $GW_USAGE_LOG"

# ────────────────────────────────────────────────────────────────────────────
# Step 2: Update harness configs for doubao-pro
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Step 2: Update harness configs for doubao-pro"
echo "========================================"

# cline globalState.json (shared harness data dir)
CLINE_HARNESS_GS="/nas_train/app.e0031982/harness_work/cline_harness_data/globalState.json"
if [ -f "$CLINE_HARNESS_GS" ]; then
  python3 -c "
import json, pathlib
p = pathlib.Path('$CLINE_HARNESS_GS')
d = json.loads(p.read_text())
d['openAiBaseUrl'] = 'http://127.0.0.1:${GW_PORT_CLINE}/v1'
d['actModeOpenAiModelId'] = '${DOUBAO_MODEL}'
d['planModeOpenAiModelId'] = '${DOUBAO_MODEL}'
p.write_text(json.dumps(d, indent=2))
print(f'  cline harness GS → port ${GW_PORT_CLINE}, model ${DOUBAO_MODEL}')
"
fi

# cline ~/.cline/data/globalState.json (for non-patched cline, if used)
CLINE_USER_GS="$HOME/.cline/data/globalState.json"
if [ -f "$CLINE_USER_GS" ]; then
  python3 -c "
import json, pathlib
p = pathlib.Path('$CLINE_USER_GS')
d = json.loads(p.read_text())
d['openAiBaseUrl'] = 'http://127.0.0.1:${GW_PORT_CLINE}/v1'
d['actModeOpenAiModelId'] = '${DOUBAO_MODEL}'
d['planModeOpenAiModelId'] = '${DOUBAO_MODEL}'
p.write_text(json.dumps(d, indent=2))
print(f'  cline user GS → port ${GW_PORT_CLINE}, model ${DOUBAO_MODEL}')
"
fi

# pi config
PI_CFG="$HOME/.pi/agent/models.json"
if [ -f "$PI_CFG" ]; then
  python3 -c "
import json, pathlib
p = pathlib.Path('$PI_CFG')
d = json.loads(p.read_text())
d['providers']['gw']['baseUrl'] = 'http://127.0.0.1:${GW_PORT_MAIN}/v1'
models = d['providers']['gw'].setdefault('models', [])
if not any(m.get('id') == '${DOUBAO_MODEL}' for m in models):
    models.append({'id': '${DOUBAO_MODEL}', 'name': 'Doubao Pro (via gw_proxy)', 'reasoning': False, 'input': ['text'], 'contextWindow': 131072, 'maxTokens': 8192})
p.write_text(json.dumps(d, indent=2))
print('  pi config → port ${GW_PORT_MAIN}, model ${DOUBAO_MODEL}')
"
fi

# hermes config
HERMES_CFG="$HOME/.hermes/config.yaml"
if [ -f "$HERMES_CFG" ]; then
  python3 -c "
import pathlib, re
p = pathlib.Path('$HERMES_CFG')
text = p.read_text()
text = re.sub(r'http://127\.0\.0\.1:\d+/v1', 'http://127.0.0.1:${GW_PORT_MAIN}/v1', text)
p.write_text(text)
print('  hermes config → port ${GW_PORT_MAIN}')
"
fi

# opencode config
OPENCODE_CFG="$HOME/.config/opencode/opencode.json"
if [ -f "$OPENCODE_CFG" ]; then
  python3 -c "
import json, pathlib
p = pathlib.Path('$OPENCODE_CFG')
d = json.loads(p.read_text())
d['provider']['gw']['options']['baseURL'] = 'http://127.0.0.1:${GW_PORT_MAIN}/v1'
d['model'] = 'gw/${DOUBAO_MODEL}'
models = d['provider']['gw'].setdefault('models', {})
models['${DOUBAO_MODEL}'] = {'name': '${DOUBAO_MODEL}', 'tool_call': True, 'reasoning': False}
p.write_text(json.dumps(d, indent=2))
print('  opencode config → port ${GW_PORT_MAIN}, model ${DOUBAO_MODEL}')
"
fi

# ────────────────────────────────────────────────────────────────────────────
# Step 3: Launch 7 harnesses in parallel
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "SWE-bench Verified 500 × 7 | doubao-pro | Start: $(date)"
echo "  Model: $DOUBAO_MODEL"
echo "  Predictions: $VF_DIR/$PRED_SUBDIR/"
echo "  Progress: $VF_DIR/reports/progress_${EVAL_TAG}<harness>.json"
echo "  Token sidecar: $GW_USAGE_LOG"
echo "  7 parallel × ${PREDICT_WORKERS} workers each"
echo "========================================"

export GW_PROXY_PORT="$GW_PORT_MAIN"
export GW_DSH_PORT="$GW_PORT_DSH"
export OPENAI_API_KEY="dummy-key-for-proxy"

PIDS=()
for h in "${HARNESSES[@]}"; do
  LOG="$LOGDIR/${h}_doubao_pro.log"
  echo "Starting $h -> $LOG"
  nice -n 10 nohup python3 "$VF_DIR/run_verified_full.py" predict \
    --harness "$h" --workers "$PREDICT_WORKERS" \
    > "$LOG" 2>&1 &
  PID=$!
  PIDS+=($PID)
  echo "  PID=$PID"
  sleep 2
done

echo ""
echo "All 7 launched. PIDs: ${PIDS[*]}"
echo "Logs: $LOGDIR/<harness>_doubao_pro.log"
echo "Monitor: bash $0 status"
echo "Stop:    bash $0 stop"
echo ""
echo "⚠️  MM 2×3 (ports 9095+) is independent and NOT affected."
echo "Token usage will be recorded per-instance in predictions JSON."
