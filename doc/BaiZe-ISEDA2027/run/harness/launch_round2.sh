#!/bin/bash
# Round 2: 7-way x 100-instance cross-eval (kimi-k2.6-cloud)
# Selection: 30 round-1 + 70 stratified new = 100 total
# --resume skips already-completed instances (the 30 round-1)
# Concurrent-safe: save_results uses fcntl locking
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128 http_proxy=http://172.19.92.25:13128
export HARNESS_MODEL=kimi-k2.6-cloud

# Load 100 instance IDs from selection file
INSTANCES=$(python3 -c "
import json
sel = json.load(open('$HERE/instance_selection_100.json'))
print(' '.join(sel['instances']))
")

echo "[$(date)] Round-2 launch: 7 harnesses x 100 instances (70 new each with --resume)"
echo "[$(date)] Instance count: $(echo $INSTANCES | wc -w)"
echo "[$(date)] Harnesses: cline-patched pi hermes opencode codex claude-code deepseek-harness"
echo "[$(date)] Model: $HARNESS_MODEL"
echo "[$(date)] Starting all 7 in parallel (save_results is fcntl-safe)..."

HARNESSES="cline-patched pi hermes opencode codex claude-code deepseek-harness"

for H in $HARNESSES; do
    LOG="$HERE/round2_${H}.log"
    echo "[$(date)] Launching $H -> $LOG"
    nohup python3 "$HERE/run_serial_kimi.py" \
        --harness "$H" \
        --instances $INSTANCES \
        --resume \
        > "$LOG" 2>&1 &
    echo "  PID=$!"
    sleep 2  # stagger launch to avoid thundering herd on proxy
done

echo "[$(date)] All 7 launched. Monitoring..."
echo "[$(date)] ETA: ~9-12 hours (70 new instances per harness, ~450s avg)"
wait
echo "[$(date)] All 7 harnesses completed!"
