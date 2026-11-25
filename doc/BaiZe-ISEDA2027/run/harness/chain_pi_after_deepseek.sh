#!/usr/bin/env bash
# chain_pi_after_deepseek.sh — wait for deepseek-harness chain to finish, then run Pi×30.
# Per 2026-10-07⑥ operator directive: expand 5-way to 7-way (Pi + Hermes).
# Hermes Agent marked "toolchain not available" (Python 3.14+Node 26 not on system, Docker perm denied).
# Pi smoke-test PASSED (resolved django__django-10924).
#
# Usage: setsid bash chain_pi_after_deepseek.sh > /tmp/chain_pi.log 2>&1 < /dev/null &
set -euo pipefail

export PATH="$HOME/.bun/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export no_proxy=127.0.0.1,localhost,agi-gateway.cxmt.com
export HARNESS_MODEL=kimi-k2.6-cloud

HARNESS_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness"
cd "$HARNESS_DIR"

INSTANCES="django__django-10924 django__django-11001 django__django-11019 django__django-11039 django__django-11049 django__django-11099 django__django-11133 django__django-11179 django__django-11283 django__django-11422 django__django-11564 django__django-11583 django__django-11620 django__django-11630 django__django-11742 sympy__sympy-11870 sympy__sympy-11897 sympy__sympy-12171 sympy__sympy-12236 sympy__sympy-12419 sympy__sympy-12454 sympy__sympy-12481 sympy__sympy-13031 sympy__sympy-13043 sympy__sympy-13146 sympy__sympy-13177 sympy__sympy-13437 sympy__sympy-13471 sympy__sympy-13480 sympy__sympy-13647"

# The deepseek chain script PID
DEEPSEEK_CHAIN_PID=1292346

echo "=== [$(date '+%H:%M:%S')] Pi chain script started ==="
echo "  Waiting for deepseek chain PID $DEEPSEEK_CHAIN_PID to finish..."

# Wait for the deepseek chain to finish
while kill -0 "$DEEPSEEK_CHAIN_PID" 2>/dev/null; do
    sleep 30
done
echo "=== [$(date '+%H:%M:%S')] deepseek chain PID $DEEPSEEK_CHAIN_PID finished ==="

# Also wait a bit for any final HTML regen by the chain script
sleep 10

# Step 1: Pi×30 with --resume (Pi smoke-test already resolved django__django-10924, --resume will skip it)
echo ""
echo "=== [$(date '+%H:%M:%S')] Starting Pi×30 (--resume) ==="
python3 run_serial_kimi.py --harness pi --instances $INSTANCES --resume 2>&1
echo "=== [$(date '+%H:%M:%S')] Pi×30 finished ==="

# Final: Regenerate HTML with all 6 harnesses (5+Pi, Hermes marked unavailable)
echo ""
echo "=== [$(date '+%H:%M:%S')] Final SWEBENCH_COMPARE.html regeneration (6-way: 5+Pi) ==="
python3 gen_kimi_compare.py || echo "WARNING: gen_kimi_compare.py failed"

echo ""
echo "=== [$(date '+%H:%M:%S')] Pi chain script COMPLETE ==="

# Print final summary
python3 -c "
import json
from collections import Counter
d = json.load(open('kimi_pilot_results.json'))
for h in ['cline-patched', 'codex', 'opencode', 'claude-code', 'deepseek-harness', 'pi']:
    entries = [e for e in d if e.get('harness') == h]
    if entries:
        c = Counter(e.get('classification', '?') for e in entries)
        print(f'{h}: {len(entries)} scored, resolved={c.get(\"resolved\",0)}, pbf={c.get(\"patch-but-failed\",0)}, blk={c.get(\"quota-blocked\",0)}')
    else:
        print(f'{h}: 0 scored (not run)')
print('Hermes Agent: toolchain not available (Python 3.14+Node 26, Docker permission denied)')
"
