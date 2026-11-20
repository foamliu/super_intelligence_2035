#!/usr/bin/env bash
# chain_hermes_after_pi.sh — wait for Pi chain to finish, then run Hermes×30.
# Per 2026-10-07⑥ operator directive: expand to 7-way (Pi + Hermes).
# Hermes Agent: Python 3.14.6 venv at /nas_train/app.e0031982/harness_work/hermes-venv,
#   CLI at ~/.hermes/bin/hermes, config at ~/.hermes/config.yaml (kimi-proxy → gw_proxy:9090).
#   Smoke test done: django__django-10924 (patch-but-failed, rc=0, 567.5s).
#
# Usage: setsid bash chain_hermes_after_pi.sh > /tmp/chain_hermes.log 2>&1 < /dev/null &
set -euo pipefail

export PATH="$HOME/.bun/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export no_proxy=127.0.0.1,localhost,agi-gateway.cxmt.com
export HARNESS_MODEL=kimi-k2.6-cloud

HARNESS_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness"
cd "$HARNESS_DIR"

INSTANCES="django__django-10924 django__django-11001 django__django-11019 django__django-11039 django__django-11049 django__django-11099 django__django-11133 django__django-11179 django__django-11283 django__django-11422 django__django-11564 django__django-11583 django__django-11620 django__django-11630 django__django-11742 sympy__sympy-11870 sympy__sympy-11897 sympy__sympy-12171 sympy__sympy-12236 sympy__sympy-12419 sympy__sympy-12454 sympy__sympy-12481 sympy__sympy-13031 sympy__sympy-13043 sympy__sympy-13146 sympy__sympy-13177 sympy__sympy-13437 sympy__sympy-13471 sympy__sympy-13480 sympy__sympy-13647"

# The Pi chain script PID (chain_pi_after_deepseek.sh)
PI_CHAIN_PID=3288315

echo "=== [$(date '+%H:%M:%S')] Hermes chain script started ==="
echo "  Waiting for Pi chain PID $PI_CHAIN_PID to finish..."

# Wait for the Pi chain to finish
while kill -0 "$PI_CHAIN_PID" 2>/dev/null; do
    sleep 30
done
echo "=== [$(date '+%H:%M:%S')] Pi chain PID $PI_CHAIN_PID finished ==="

# Also wait a bit for any final HTML regen by the Pi chain script
sleep 10

# Step 1: Hermes×30 with --resume (django__django-10924 already done as smoke test)
echo ""
echo "=== [$(date '+%H:%M:%S')] Starting Hermes×30 (--resume, skip django-10924) ==="
python3 run_serial_kimi.py --harness hermes --instances $INSTANCES --resume 2>&1
echo "=== [$(date '+%H:%M:%S')] Hermes×30 finished ==="

# Final: Regenerate HTML with all 7 harnesses
echo ""
echo "=== [$(date '+%H:%M:%S')] Final SWEBENCH_COMPARE.html regeneration (7-way) ==="
python3 gen_kimi_compare.py || echo "WARNING: gen_kimi_compare.py failed"

echo ""
echo "=== [$(date '+%H:%M:%S')] Hermes chain script COMPLETE ==="

# Print final summary
python3 -c "
import json
from collections import Counter
d = json.load(open('kimi_pilot_results.json'))
for h in ['cline-patched', 'codex', 'opencode', 'claude-code', 'deepseek-harness', 'pi', 'hermes']:
    entries = [e for e in d if e.get('harness') == h]
    if entries:
        c = Counter(e.get('classification', '?') for e in entries)
        print(f'{h}: {len(entries)} scored, resolved={c.get(\"resolved\",0)}, pbf={c.get(\"patch-but-failed\",0)}, blk={c.get(\"quota-blocked\",0)}')
    else:
        print(f'{h}: 0 scored (not run)')
"
