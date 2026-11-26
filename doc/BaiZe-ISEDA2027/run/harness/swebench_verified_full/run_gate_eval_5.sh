#!/bin/bash
# Gate eval for 5 completed harnesses (excludes hermes=still running, deepseek=0patch)
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"
export EVAL_MAX_WORKERS=4
GATE_IDS="gate_10_ids.txt"
HARNESSES=("cline-patched" "codex" "claude-code" "opencode" "pi")
echo "=== GATE EVAL 5h: workers=${EVAL_MAX_WORKERS} started=$(date) ==="
for h in "${HARNESSES[@]}"; do
    echo "$(date '+%H:%M:%S') EVAL $h ..."
    python3 run_verified_full.py eval --harness "$h" --ids-file "$GATE_IDS" \
        > "logs/gate_eval_${h}.log" 2>&1
    echo "  $(date '+%H:%M:%S') EVAL $h rc=$?"
done
echo "=== GATE EVAL complete: $(date) ==="
# Generate gate reports
for h in "${HARNESSES[@]}"; do
    python3 run_verified_full.py report --harness "$h" --ids-file "$GATE_IDS" 2>&1 || true
done
