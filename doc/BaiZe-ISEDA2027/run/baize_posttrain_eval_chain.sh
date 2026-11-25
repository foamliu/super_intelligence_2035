#!/usr/bin/env bash
# baize_posttrain_eval_chain.sh -- Chain remaining 5-run evals after step105 completes.
#
# Sequence:
#   1. Wait for step105 autocomplete daemon (PID from --step105-pid) to finish
#   2. Run step60 runs 2-5 (run 1 already done) via baize_posttrain_5run_eval.sh
#   3. Run base model runs 1-5 via baize_posttrain_5run_eval.sh
#   4. Run analysis script to compute mean+/-std + McNemar + bootstrap
#
# Usage (background):
#   nohup bash baize_posttrain_eval_chain.sh \
#     --step105-pid 1122770 \
#     > /tmp/posttrain_eval_chain.log 2>&1 &
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVAL_SCRIPT="$SCRIPT_DIR/baize_posttrain_5run_eval.sh"
ANALYSIS_SCRIPT="$SCRIPT_DIR/baize_posttrain_5run_analysis.py"
RESULTS_DIR="/tmp/posttrain_5run_eval"

STEP105_PID=""
while [ $# -gt 0 ]; do
  case "$1" in
    --step105-pid) STEP105_PID="$2"; shift ;;
    *) echo "unknown: $1" ;;
  esac
  shift
done

echo "===== Eval Chain Daemon @ $(date '+%F %T') ====="
echo "  step105 autocomplete daemon PID=$STEP105_PID"

# 1. Wait for step105 autocomplete daemon to finish
if [ -n "$STEP105_PID" ]; then
  echo "[chain] Waiting for step105 autocomplete daemon (PID $STEP105_PID)..."
  while kill -0 "$STEP105_PID" 2>/dev/null; do
    echo "[chain] step105 daemon still running ($(date '+%T'))... sleeping 120s"
    sleep 120
  done
  echo "[chain] step105 daemon finished at $(date '+%F %T')"
fi

# Verify step105 has 5 runs
step105_count=$(find "$RESULTS_DIR/step105" -name 'final_report.json' 2>/dev/null | wc -l)
echo "[chain] step105 final_report.json count: $step105_count"

# 2. Run step60 runs 2-5 (GPU5 port 8097)
echo "[chain] === Starting step60 runs 2-5 @ $(date '+%F %T') ==="
for run_n in 2 3 4 5; do
  run_dir="$RESULTS_DIR/step60/run${run_n}"
  if [ -f "$run_dir/final_report.json" ]; then
    echo "[chain] step60 run${run_n} SKIP (already done)"
    continue
  fi
  echo "[chain] step60 run${run_n} START @ $(date '+%F %T')"
  bash "$EVAL_SCRIPT" --endpoint http://127.0.0.1:8097/v1 --model minicpm5-2b-sft-v39 --label step60 --run "$run_n" 2>&1
  echo "[chain] step60 run${run_n} END @ $(date '+%F %T')"
done

# 3. Run base model runs 1-5 (GPU4 port 8098)
echo "[chain] === Starting base model runs 1-5 @ $(date '+%F %T') ==="
for run_n in 1 2 3 4 5; do
  run_dir="$RESULTS_DIR/base/run${run_n}"
  if [ -f "$run_dir/final_report.json" ]; then
    echo "[chain] base run${run_n} SKIP (already done)"
    continue
  fi
  echo "[chain] base run${run_n} START @ $(date '+%F %T')"
  bash "$EVAL_SCRIPT" --endpoint http://127.0.0.1:8098/v1 --model minicpm5-2b --label base --run "$run_n" 2>&1
  echo "[chain] base run${run_n} END @ $(date '+%F %T')"
done

# 4. Run analysis
echo "[chain] === Running 5-run analysis @ $(date '+%F %T') ==="
python3 "$ANALYSIS_SCRIPT" --output "$RESULTS_DIR/5run_final_analysis.json" 2>&1
echo "[chain] === Analysis complete @ $(date '+%F %T') ==="
echo "[chain] All eval chains done."
