#!/bin/bash
# Standalone eval+report runner for R548 gate v2 (launch_gate.sh died from tool
# timeout; predict processes survived in setsid).  Run AFTER all predict phases
# complete (check: pgrep -af 'run_verified_full.py predict' == empty).
#
# Usage:  bash run_eval.sh
set -uo pipefail
cd "$(dirname "$0")"

GATE_IDS="gate_10_ids.txt"
HARNESSES=("cline-patched" "codex" "opencode" "pi" "claude-code" "hermes" "deepseek-harness")
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"
export EVAL_MAX_WORKERS="${EVAL_MAX_WORKERS:-8}"

echo "=== GATE EVAL: ${#HARNESSES[@]} harnesses (sequential, workers=${EVAL_MAX_WORKERS}) ==="
echo "Started: $(date)"
echo ""

for h in "${HARNESSES[@]}"; do
    echo "EVAL $h ..."
    python3 run_verified_full.py eval --harness "$h" --ids-file "$GATE_IDS" \
        > "logs/gate_eval_${h}.log" 2>&1
    echo "  EVAL $h: done (rc=$?) -> logs/gate_eval_${h}.log"
done

echo ""
echo "=== GATE RESULTS ==="
echo ""
for h in "${HARNESSES[@]}"; do
    python3 run_verified_full.py report --harness "$h" --ids-file "$GATE_IDS" 2>&1 || true
done

echo ""
echo "Gate eval+report complete: $(date)"