#!/bin/bash
# SWE-bench Verified gate launcher: 10 problems x 6 available harnesses
# Runs predict phases concurrently, eval phases sequentially (docker limit).
#
# Usage:  bash launch_gate.sh
# Monitor: tail -f logs/gate_*.log
# Check:   cat reports/progress_*.json | python3 -m json.tool | head -20

set -euo pipefail
cd "$(dirname "$0")"

mkdir -p logs reports predictions instances

# Available harnesses (deepseek-harness excluded — not available)
HARNESSES=("cline-patched" "codex" "opencode" "pi" "claude-code" "hermes")
GATE_SIZE=10

echo "=== GATE LAUNCH: ${#HARNESSES[@]} harnesses x ${GATE_SIZE} problems ==="
echo "Started: $(date)"
echo ""

# --- Phase 1: PREDICT (all harnesses concurrently) ---
PIDS=()
for h in "${HARNESSES[@]}"; do
    echo "Starting PREDICT for $h ..."
    setsid bash -c "
        export PATH=\"\$HOME/.local/bin:\$HOME/.bun/bin:\$PATH\"
        python3 run_verified_full.py predict --harness $h --max ${GATE_SIZE}
    " > "logs/gate_predict_${h}.log" 2>&1 &
    PIDS+=($!)
    echo "  PID=$! -> logs/gate_predict_${h}.log"
    sleep 15  # Stagger launches to avoid proxy congestion during git fetch
done

echo ""
echo "Waiting for all predict phases to finish..."
echo "  (Monitor: tail -f logs/gate_predict_*.log)"
echo ""

# Wait for all predict phases
FAILED=0
for i in "${!HARNESSES[@]}"; do
    h="${HARNESSES[$i]}"
    pid="${PIDS[$i]}"
    if wait "$pid"; then
        echo "  PREDICT $h: DONE (exit 0)"
    else
        echo "  PREDICT $h: FAILED (exit $?)"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "Predict phase complete. ${FAILED} harnesses failed."
echo ""

# --- Phase 2: EVAL (sequential, to avoid docker container explosion) ---
echo "Starting EVAL phases (sequential)..."
echo ""

for h in "${HARNESSES[@]}"; do
    echo "EVAL $h ..."
    setsid bash -c "
        export PATH=\"\$HOME/.local/bin:\$HOME/.bun/bin:\$PATH\"
        python3 run_verified_full.py eval --harness $h --max ${GATE_SIZE}
    " > "logs/gate_eval_${h}.log" 2>&1
    echo "  EVAL $h: done (rc=$?) -> logs/gate_eval_${h}.log"
done

echo ""
echo "=== GATE RESULTS ==="
echo ""

# --- Phase 3: REPORT ---
for h in "${HARNESSES[@]}"; do
    python3 run_verified_full.py report --harness $h --max ${GATE_SIZE} 2>&1 || true
done

echo ""
echo "Gate complete: $(date)"
echo "Reports: reports/predict_*.json, reports/eval_*.json, reports/progress_*.json"
