#!/bin/bash
# Restart Round-2: 5 incomplete harnesses x 100 instances (--resume skips done)
# Uses setsid+nohup so processes survive the cline session that launched them.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128 http_proxy=http://172.19.92.25:13128
export HARNESS_MODEL=kimi-k2.6-cloud
export PYTHONUNBUFFERED=1

# Load 100 instance IDs from selection file
INSTANCES=$(python3 -c "
import json
sel = json.load(open('$HERE/instance_selection_100.json'))
print(' '.join(sel['instances']))
")

echo "[$(date)] Round-2 RESTART: 5 incomplete harnesses x 100 instances (--resume)"
echo "[$(date)] Instance count: $(echo $INSTANCES | wc -w)"

# Only restart harnesses that are NOT at 100/100
HARNESSES="cline-patched opencode claude-code deepseek-harness hermes"

for H in $HARNESSES; do
    LOG="$HERE/round2_${H}.log"
    echo "[$(date)] Launching $H -> $LOG (setsid+nohup for survival)"
    setsid nohup python3 "$HERE/run_serial_kimi.py" \
        --harness "$H" \
        --instances $INSTANCES \
        --resume \
        > "$LOG" 2>&1 &
    echo "  PID=$!"
    sleep 2  # stagger launch to avoid thundering herd on proxy
done

echo "[$(date)] All 5 relaunched. Processes detached via setsid (will survive parent exit)."
echo "[$(date)] ETA: hermes 36 remaining ~6.5h, others 7-13 remaining ~1-3h"
