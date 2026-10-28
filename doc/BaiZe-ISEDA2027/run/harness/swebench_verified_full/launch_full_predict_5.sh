#!/bin/bash
# SWE-bench Verified FULL 500 predict launcher (R551, 2026-10-28).
#   5 gate-PASSING harnesses x 500 problems, concurrent (setsid background).
#   Gate results: cline/codex/claude-code/opencode/pi ALL PASS.
#   hermes/deepseek-harness FAILED gate → excluded (reported separately).
#
# Improvements per operator directive:
#   - git fetch timeout 300→1800s (run_verified_full.py patched)
#   - Rotated ids per harness (full_500_ids_{h}.txt) to avoid concurrent
#     same-repo fetch congestion (cline@astropy, codex@django, etc.)
#   - Checkpoint resume: skips instances with existing valid predictions
#     (gate_10 instances already done → auto-skipped)
#   - Progress: reports/progress_{h}.json updated after each instance
#
# Usage:  setsid bash launch_full_predict_5.sh > logs/full_predict_launcher.log 2>&1 &
# Monitor: tail -f logs/full_predict_*.log ; python3 -c "import json; ..."
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"

HARNESSES=("cline-patched" "codex" "claude-code" "opencode" "pi")

mkdir -p logs reports predictions instances

echo "=== FULL 500 PREDICT: ${#HARNESSES[@]} harnesses started=$(date) ==="
echo "Git fetch timeout: 1800s (patched in run_verified_full.py)"
echo ""

for h in "${HARNESSES[@]}"; do
    ids_file="full_500_ids_${h}.txt"
    if [ ! -f "$ids_file" ]; then
        echo "ERROR: $ids_file not found, skipping $h"
        continue
    fi
    echo "Starting PREDICT for $h (ids=$ids_file) ..."
    setsid bash -c "
        export PATH=\"\$HOME/.local/bin:\$HOME/.bun/bin:\$PATH\"
        export PYTHONPATH=\"/tmp/dsh_sdk:\${PYTHONPATH:-}\"
        python3 run_verified_full.py predict --harness $h --ids-file $ids_file
    " > "logs/full_predict_${h}.log" 2>&1 &
    PID=$!
    echo "  PID=$PID -> logs/full_predict_${h}.log"
    sleep 30  # Stagger launches to reduce proxy congestion during initial git fetch
done

echo ""
echo "=== All ${#HARNESSES[@]} predict processes launched at $(date) ==="
echo "Monitor: tail -f logs/full_predict_*.log"
echo "Progress: cat reports/progress_{harness}.json | python3 -m json.tool | head -12"
echo "ETA: ~500 instances x ~400-600s each (serial per harness, 5 concurrent) ≈ 2-3 days"
