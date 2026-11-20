#!/bin/bash
# Optimized serial re-run of 88 workdir-blocked instances.
#
# Optimization (R210): Hermes's 12 remaining instances are ALL sympy, so
# non-sympy blocked instances (44) can be re-run NOW in parallel with hermes.
# Only sympy blocked instances (44) must wait for hermes to finish.
#
# Phase 1: Re-run 44 non-sympy blocked instances (django/matplotlib/sklearn/sphinx)
#           — runs immediately, in parallel with hermes (different workdirs)
# Phase 2: Wait for hermes to finish
# Phase 3: Re-run 44 sympy blocked instances — after hermes, sympy workdir is free
#
# git_clone_or_fetch already does git reset --hard + git clean -fd per instance,
# so no blanket workdir cleanup needed.
#
# Launched via setsid+nohup so it survives the cline session.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128 http_proxy=http://172.19.92.25:13128
export HARNESS_MODEL=kimi-k2.6-cloud
export PYTHONUNBUFFERED=1

RESULTS="$HERE/kimi_pilot_results.json"

echo "[$(date)] === Optimized blocked re-run: Phase 1 (non-sympy) + Phase 3 (sympy after hermes) ==="

# --- Get blocked instances, split by sympy vs non-sympy ---
BLOCKED_JSON=$(python3 -c "
import json
with open('$RESULTS') as f:
    data = json.load(f)
with open('$HERE/instance_selection_100.json') as f:
    sel = json.load(f)
all_set = set(sel['instances'])
from collections import defaultdict
nonsympy = defaultdict(list)
sympy = defaultdict(list)
for e in data:
    if e.get('instance_id') in all_set and e.get('classification') == 'blocked':
        h = e['harness']
        iid = e['instance_id']
        if iid.startswith('sympy__sympy'):
            sympy[h].append(iid)
        else:
            nonsympy[h].append(iid)
import json as j
print(j.dumps({
    'nonsympy': {h: sorted(v) for h, v in nonsympy.items()},
    'sympy': {h: sorted(v) for h, v in sympy.items()}
}))
")

echo "[$(date)] Blocked split:"
echo "$BLOCKED_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
ns = d['nonsympy']
sy = d['sympy']
print('  Non-sympy (Phase 1, starts now):')
for h in sorted(ns):
    print(f'    {h}: {len(ns[h])}')
print(f'    TOTAL: {sum(len(v) for v in ns.values())}')
print('  Sympy (Phase 3, after hermes):')
for h in sorted(sy):
    print(f'    {h}: {len(sy[h])}')
print(f'    TOTAL: {sum(len(v) for v in sy.values())}')
"

# --- Phase 1: Re-run non-sympy blocked instances serially ---
echo "[$(date)] === Phase 1: Non-sympy blocked re-run (parallel with hermes) ==="
HARNESSES_ORDER_NS="claude-code cline-patched deepseek-harness pi"

for H in $HARNESSES_ORDER_NS; do
    INSTANCES=$(echo "$BLOCKED_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
insts = d['nonsympy'].get('$H', [])
print(' '.join(insts))
" 2>/dev/null || true)

    if [ -z "$INSTANCES" ]; then
        echo "[$(date)] $H: no non-sympy blocked instances, skipping."
        continue
    fi

    COUNT=$(echo "$INSTANCES" | wc -w)
    echo "[$(date)] Phase 1: Re-running $H: $COUNT non-sympy blocked (serial)..."
    LOG="$HERE/rerun_nonsympy_${H}.log"

    python3 "$HERE/run_serial_kimi.py" \
        --harness "$H" \
        --instances $INSTANCES \
        --resume \
        > "$LOG" 2>&1
    echo "[$(date)] Phase 1: $H done. See $LOG"
done

echo "[$(date)] === Phase 1 complete ==="

# --- Phase 2: Wait for hermes to finish ---
echo "[$(date)] === Phase 2: Waiting for hermes to finish ==="
while true; do
    HERMES_PID=$(pgrep -f 'run_serial_kimi.py --harness hermes' || true)
    if [ -z "$HERMES_PID" ]; then
        echo "[$(date)] Hermes process not found — proceeding to Phase 3."
        break
    fi
    echo "[$(date)] Hermes still running (PID=$HERMES_PID). Sleeping 300s..."
    sleep 300
done

# --- Phase 3: Re-run sympy blocked instances serially ---
echo "[$(date)] === Phase 3: Sympy blocked re-run (after hermes) ==="
HARNESSES_ORDER_SY="claude-code cline-patched codex deepseek-harness pi"

for H in $HARNESSES_ORDER_SY; do
    INSTANCES=$(echo "$BLOCKED_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
insts = d['sympy'].get('$H', [])
print(' '.join(insts))
" 2>/dev/null || true)

    if [ -z "$INSTANCES" ]; then
        echo "[$(date)] $H: no sympy blocked instances, skipping."
        continue
    fi

    COUNT=$(echo "$INSTANCES" | wc -w)
    echo "[$(date)] Phase 3: Re-running $H: $COUNT sympy blocked (serial)..."
    LOG="$HERE/rerun_sympy_${H}.log"

    python3 "$HERE/run_serial_kimi.py" \
        --harness "$H" \
        --instances $INSTANCES \
        --resume \
        > "$LOG" 2>&1
    echo "[$(date)] Phase 3: $H done. See $LOG"
done

echo "[$(date)] === Phase 3 complete ==="

# --- Final summary ---
echo "[$(date)] === ALL blocked instances re-run complete ==="
python3 -c "
import json
from collections import Counter
with open('$RESULTS') as f:
    data = json.load(f)
with open('$HERE/instance_selection_100.json') as f:
    sel = json.load(f)
all_set = set(sel['instances'])
harnesses = ['cline-patched','codex','opencode','claude-code','deepseek-harness','pi','hermes']
print('  Final 7x100 summary:')
for h in harnesses:
    entries = [e for e in data if e.get('harness') == h and e.get('instance_id') in all_set]
    cls = Counter(e.get('classification','unknown') for e in entries)
    resolved = cls.get('resolved', 0)
    pbf = cls.get('patch-but-failed', 0)
    blocked = cls.get('blocked', 0)
    scored = resolved + pbf
    rate = f'{100*resolved/scored:.1f}%' if scored > 0 else 'N/A'
    print(f'    {h:20s}: done={len(entries):3d}/100  resolved={resolved:2d}  pbf={pbf:2d}  blocked={blocked:2d}  rate={rate}')
total_resolved = sum(1 for e in data if e.get('instance_id') in all_set and e.get('classification') == 'resolved')
print(f'  TOTAL resolved: {total_resolved}')
"

echo "[$(date)] DONE."
