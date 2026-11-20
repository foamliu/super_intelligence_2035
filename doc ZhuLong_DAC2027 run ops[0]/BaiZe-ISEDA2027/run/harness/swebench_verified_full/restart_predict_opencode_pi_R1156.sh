#!/bin/bash
# R1156: restart opencode (499/500) and pi (441/500) predict runners.
#   Both died 2026-10-28 13:50 and were NOT restarted in R1103 (only codex/claude-code were).
#   Checkpoint resume: skips instances with existing valid predictions.
#   opencode: 499/500 (1 missing), pi: 441/500 (59 missing).
# Memory self-check PASSED (195th): avail ~1.4TiB, no this-line proc >50GB.
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"

HARNESSES=("opencode" "pi")
mkdir -p logs reports predictions instances

echo "=== RESTART PREDICT: ${#HARNESSES[@]} harnesses started=$(date) ==="

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
    " > "logs/full_predict_${h}_R1156.log" 2>&1 &
    PID=$!
    echo "  PID=$PID -> logs/full_predict_${h}_R1156.log"
    sleep 30  # Stagger launches to reduce proxy congestion
done

echo ""
echo "=== All ${#HARNESSES[@]} predict processes launched at $(date) ==="
echo "Monitor: tail -f logs/full_predict_*_R1156.log"
