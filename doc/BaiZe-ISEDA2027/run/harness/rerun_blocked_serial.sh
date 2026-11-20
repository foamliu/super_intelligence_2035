#!/bin/bash
# Serial re-run of 88 workdir-blocked instances after hermes completes.
#
# Context (R207 discovery): 88 instances were "blocked" because 7 harnesses
# sharing the same repo workdirs caused git checkout conflicts in parallel mode.
# This script:
#   1. Waits for the hermes process to finish (no parallel workdir access)
#   2. Cleans all shared workdirs (git reset --hard + git clean -fd)
#   3. Re-runs blocked instances serially, one harness at a time
#   4. --resume skips resolved/pbf entries, re-runs only blocked ones
#
# Launched via setsid+nohup so it survives the cline session.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128 http_proxy=http://172.19.92.25:13128
export HARNESS_MODEL=kimi-k2.6-cloud
export PYTHONUNBUFFERED=1

WORKDIRS=/dev/shm/harness_work/workdirs
RESULTS="$HERE/kimi_pilot_results.json"

echo "[$(date)] === Serial re-run of blocked instances ==="

# --- Step 1: Wait for hermes to finish ---
echo "[$(date)] Step 1: Waiting for hermes process to finish..."
while true; do
    HERMES_PID=$(pgrep -f 'run_serial_kimi.py --harness hermes' || true)
    if [ -z "$HERMES_PID" ]; then
        echo "[$(date)] Hermes process not found — proceeding."
        break
    fi
    echo "[$(date)] Hermes still running (PID=$HERMES_PID). Sleeping 300s..."
    sleep 300
done

# --- Step 2: Clean all shared workdirs ---
echo "[$(date)] Step 2: Cleaning all shared workdirs..."
for wd in "$WORKDIRS"/*/; do
    [ -d "$wd/.git" ] || continue
    repo_name=$(basename "$wd")
    echo "  Cleaning $repo_name..."
    git -C "$wd" reset --hard HEAD 2>&1 | tail -1
    git -C "$wd" clean -fd 2>&1 | tail -3
done
echo "[$(date)] Workdir cleanup complete."

# --- Step 3: Get blocked instances per harness ---
echo "[$(date)] Step 3: Identifying blocked instances..."
BLOCKED_JSON=$(python3 -c "
import json
with open('$RESULTS') as f:
    data = json.load(f)
with open('$HERE/instance_selection_100.json') as f:
    sel = json.load(f)
all_set = set(sel['instances'])

from collections import defaultdict
blocked_by_harness = defaultdict(list)
for e in data:
    if e.get('instance_id') in all_set and e.get('classification') == 'blocked':
        blocked_by_harness[e['harness']].append(e['instance_id'])

import json as j
print(j.dumps({h: sorted(v) for h, v in blocked_by_harness.items()}))
")

echo "[$(date)] Blocked instances per harness:"
echo "$BLOCKED_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for h, insts in sorted(d.items()):
    print(f'  {h}: {len(insts)} instances')
print(f'  TOTAL: {sum(len(v) for v in d.values())}')
"

# --- Step 4: Re-run each harness's blocked instances serially ---
HARNESSES_ORDER="cline-patched codex claude-code deepseek-harness pi codex"
# Note: codex appears twice intentionally? No — remove dup
HARNESSES_ORDER="cline-patched codex claude-code deepseek-harness pi"

for H in $HARNESSES_ORDER; do
    INSTANCES=$(echo "$BLOCKED_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
insts = d.get('$H', [])
print(' '.join(insts))
" 2>/dev/null || true)

    if [ -z "$INSTANCES" ]; then
        echo "[$(date)] $H: no blocked instances, skipping."
        continue
    fi

    COUNT=$(echo "$INSTANCES" | wc -w)
    echo "[$(date)] Re-running $H: $COUNT blocked instances (serial)..."
    LOG="$HERE/rerun_blocked_${H}.log"

    python3 "$HERE/run_serial_kimi.py" \
        --harness "$H" \
        --instances $INSTANCES \
        --resume \
        > "$LOG" 2>&1
    echo "[$(date)] $H done. See $LOG"
done

echo "[$(date)] === All blocked instances re-run complete ==="

# --- Step 5: Print final summary ---
echo "[$(date)] Final summary:"
python3 -c "
import json
from collections import Counter
with open('$RESULTS') as f:
    data = json.load(f)
with open('$HERE/instance_selection_100.json') as f:
    sel = json.load(f)
all_set = set(sel['instances'])
harnesses = ['cline-patched','codex','opencode','claude-code','deepseek-harness','pi','hermes']
for h in harnesses:
    entries = [e for e in data if e.get('harness') == h and e.get('instance_id') in all_set]
    cls = Counter(e.get('classification','unknown') for e in entries)
    resolved = cls.get('resolved', 0)
    pbf = cls.get('patch-but-failed', 0)
    blocked = cls.get('blocked', 0)
    scored = resolved + pbf
    rate = f'{100*resolved/scored:.1f}%' if scored > 0 else 'N/A'
    print(f'  {h:20s}: done={len(entries):3d}/100  resolved={resolved:2d}  pbf={pbf:2d}  blocked={blocked:2d}  rate={rate}')
"

echo "[$(date)] DONE."
