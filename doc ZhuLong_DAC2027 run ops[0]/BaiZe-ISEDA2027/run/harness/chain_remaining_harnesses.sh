#!/usr/bin/env bash
# chain_remaining_harnesses.sh — chain claude-code×30 + deepseek-harness×30 after opencode finishes.
# Per 2026-10-07 operator directive: 30×5 harness cross-eval (kimi-k2.6-cloud, serial=1).
#
# Usage: setsid bash chain_remaining_harnesses.sh > /tmp/chain_harnesses.log 2>&1 < /dev/null &
set -euo pipefail

export PATH="$HOME/.bun/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export no_proxy=127.0.0.1,localhost,agi-gateway.cxmt.com
export HARNESS_MODEL=kimi-k2.6-cloud

HARNESS_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness"
cd "$HARNESS_DIR"

INSTANCES="django__django-10924 django__django-11001 django__django-11019 django__django-11039 django__django-11049 django__django-11099 django__django-11133 django__django-11179 django__django-11283 django__django-11422 django__django-11564 django__django-11583 django__django-11620 django__django-11630 django__django-11742 sympy__sympy-11870 sympy__sympy-11897 sympy__sympy-12171 sympy__sympy-12236 sympy__sympy-12419 sympy__sympy-12454 sympy__sympy-12481 sympy__sympy-13031 sympy__sympy-13043 sympy__sympy-13146 sympy__sympy-13177 sympy__sympy-13437 sympy__sympy-13471 sympy__sympy-13480 sympy__sympy-13647"

OPENCODE_PID=87730

echo "=== [$(date '+%H:%M:%S')] Chain script started ==="
echo "  Waiting for opencode PID $OPENCODE_PID to finish..."

# Step 0: Wait for opencode to finish
while kill -0 "$OPENCODE_PID" 2>/dev/null; do
    sleep 30
done
echo "=== [$(date '+%H:%M:%S')] opencode PID $OPENCODE_PID finished ==="

# Regenerate HTML with opencode results
echo "=== [$(date '+%H:%M:%S')] Regenerating SWEBENCH_COMPARE.html (post-opencode) ==="
python3 gen_kimi_compare.py || echo "WARNING: gen_kimi_compare.py failed"

# Step 1: claude-code×30 with --resume
echo ""
echo "=== [$(date '+%H:%M:%S')] Starting claude-code×30 (--resume) ==="
python3 run_serial_kimi.py --harness claude-code --instances $INSTANCES --resume 2>&1
echo "=== [$(date '+%H:%M:%S')] claude-code×30 finished ==="

# Regenerate HTML with claude-code results
echo "=== [$(date '+%H:%M:%S')] Regenerating SWEBENCH_COMPARE.html (post-claude-code) ==="
python3 gen_kimi_compare.py || echo "WARNING: gen_kimi_compare.py failed"

# Step 2: deepseek-harness×30 with --resume
echo ""
echo "=== [$(date '+%H:%M:%S')] Starting deepseek-harness×30 (--resume) ==="
python3 run_serial_kimi.py --harness deepseek-harness --instances $INSTANCES --resume 2>&1
echo "=== [$(date '+%H:%M:%S')] deepseek-harness×30 finished ==="

# Final: Regenerate HTML with all 5 harnesses
echo ""
echo "=== [$(date '+%H:%M:%S')] Final SWEBENCH_COMPARE.html regeneration ==="
python3 gen_kimi_compare.py || echo "WARNING: gen_kimi_compare.py failed"

echo ""
echo "=== [$(date '+%H:%M:%S')] Chain script COMPLETE ==="

# Print final summary
python3 -c "
import json
from collections import Counter
data = json.load(open('kimi_pilot_results.json'))
for h in ['cline-patched','codex','opencode','claude-code','deepseek-harness']:
    entries = [e for e in data if e.get('harness')==h]
    cls = Counter(e.get('classification','?') for e in entries)
    resolved = cls.get('resolved',0)
    pbf = cls.get('patch-but-failed',0)
    scored = resolved + pbf
    rate = f'{100*resolved/scored:.1f}%' if scored > 0 else 'N/A'
    print(f'  {h}: total={len(entries)} resolved={resolved} pbf={pbf} rate={rate}')
"
