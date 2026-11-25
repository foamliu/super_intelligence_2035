#!/bin/bash
# SWE-bench Verified gate launcher (R548 v2, 2026-10-28):
#   10 DIVERSE problems (1 per repo, 10 distinct repos) x 7 harnesses.
# R548 v1 failed: 10 astropy-only instances x 6 concurrent -> 6 simultaneous
# astropy fetches through one proxy -> first timed out -> broken workdir reused
# by all 9 subsequent same-repo instances -> 0 agents ran.  v2 fixes: diverse
# repos (concurrent fetches hit different repos) + proven shallow-fetch git
# logic (no full-fetch fallback) + deepseek-harness added.
#
# Runs predict phases concurrently (7 harnesses), eval phases sequentially
# (docker container limit).  Phase selection via $PHASE (all|predict|eval|report).
#
# Usage:  PHASE=all bash launch_gate.sh
# Monitor: tail -f logs/gate_predict_*.log ; tail -f logs/gate_launcher.log

set -euo pipefail
cd "$(dirname "$0")"

PHASE="${PHASE:-all}"
GATE_IDS="gate_10_ids.txt"
GATE_SIZE=$(wc -l < "$GATE_IDS" | tr -d ' ')
mkdir -p logs reports predictions instances

# All 7 harnesses per operator directive (deepseek-harness needs PYTHONPATH)
HARNESSES=("cline-patched" "codex" "opencode" "pi" "claude-code" "hermes" "deepseek-harness")
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"
export EVAL_MAX_WORKERS="${EVAL_MAX_WORKERS:-8}"

echo "=== GATE LAUNCH v2: ${#HARNESSES[@]} harnesses x ${GATE_SIZE} diverse problems ==="
echo "Phase: $PHASE  |  ids: $GATE_IDS"
echo "Started: $(date)"
echo ""

# --- Clean stale state from failed v1 gate ---
echo "Cleaning stale workdirs + progress from failed v1 gate..."
rm -rf /dev/shm/harness_verified_full/workdirs/*
for h in "${HARNESSES[@]}"; do
  rm -f "reports/progress_${h}.json" "reports/predict_${h}.json" "reports/eval_${h}.json"
  rm -f "predictions/predictions_${h}.json" "predictions/${h}__"*.json
  : > "logs/gate_predict_${h}.log"
  : > "logs/gate_eval_${h}.log"
done
echo "  done."
echo ""

if [ "$PHASE" = "predict" ] || [ "$PHASE" = "all" ]; then
  # --- Phase 1: PREDICT (all harnesses concurrently) ---
  PIDS=()
  for h in "${HARNESSES[@]}"; do
    echo "Starting PREDICT for $h ..."
    setsid bash -c "
        export PATH=\"\$HOME/.local/bin:\$HOME/.bun/bin:\$PATH\"
        export PYTHONPATH=\"/tmp/dsh_sdk:\${PYTHONPATH:-}\"
        python3 run_verified_full.py predict --harness $h --ids-file $GATE_IDS
    " > "logs/gate_predict_${h}.log" 2>&1 &
    PIDS+=($!)
    echo "  PID=$! -> logs/gate_predict_${h}.log"
    sleep 20  # Stagger launches to avoid proxy congestion during git fetch
  done

  echo ""
  echo "Waiting for all predict phases to finish..."
  echo "  (Monitor: tail -f logs/gate_predict_*.log)"
  echo ""

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
fi

if [ "$PHASE" = "eval" ] || [ "$PHASE" = "all" ]; then
  # --- Phase 2: EVAL (sequential, to avoid docker container explosion) ---
  echo "Starting EVAL phases (sequential, workers=${EVAL_MAX_WORKERS})..."
  echo ""

  for h in "${HARNESSES[@]}"; do
    echo "EVAL $h ..."
    setsid bash -c "
        export PATH=\"\$HOME/.local/bin:\$HOME/.bun/bin:\$PATH\"
        export PYTHONPATH=\"/tmp/dsh_sdk:\${PYTHONPATH:-}\"
        export EVAL_MAX_WORKERS=${EVAL_MAX_WORKERS}
        python3 run_verified_full.py eval --harness $h --ids-file $GATE_IDS
    " > "logs/gate_eval_${h}.log" 2>&1
    echo "  EVAL $h: done (rc=$?) -> logs/gate_eval_${h}.log"
  done
  echo ""
fi

# --- Phase 3: REPORT ---
echo "=== GATE RESULTS ==="
echo ""
for h in "${HARNESSES[@]}"; do
    python3 run_verified_full.py report --harness $h --ids-file $GATE_IDS 2>&1 || true
done

echo ""
echo "Gate complete: $(date)"
echo "Reports: reports/predict_*.json, reports/eval_*.json, reports/progress_*.json"
