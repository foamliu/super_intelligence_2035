#!/bin/bash
# launch_7x300.sh — 7×300 SWE-bench Lite cross-eval (2026-10-09⑧ directive)
#
# Runs 7 harnesses in parallel, each internally serial (N=1).
# Uses --resume to reuse existing 100-set results (700 done).
# codex already has all 300 (0 new); other 6 harnesses × 200 new = 1200 new runs.
#
# Code fixes applied (run_serial_kimi.py):
#   1. Per-harness workdir isolation: WORKDIRS/<harness>/<repo>
#   2. Rootfs global flock on setup_rootfs() and eval_instance()
#   3. --per-instance-workdir flag for future N>1
#
# Usage: bash launch_7x300.sh [N]
#   N=1 (default): 7 parallel, each serial
#   N>1: use --per-instance-workdir (each harness runs N concurrent instances)
#        (requires separate process management per harness — not yet implemented here)
#
# ETA: ~42h wall (hermes bottleneck) at N=1; ~42/N h at N>1.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_7x300"
mkdir -p "$LOGDIR"

N="${1:-1}"
EXTRA_ARGS=""
if [ "$N" -gt 1 ]; then
  EXTRA_ARGS="--per-instance-workdir"
  echo "⚠️  N=$N: per-instance workdir enabled (NOT YET SUPPORTED for concurrent within-harness)"
  echo "    This script runs each harness as a single serial process."
  echo "    For N>1, you need to split instances and run multiple processes per harness."
  exit 1
fi

PYTHON="${PYTHON:-python3}"
RUN_SCRIPT="$HERE/run_serial_kimi.py"

HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")

echo "========================================"
echo "7x300 SWE-bench Lite Cross-Eval"
echo "  Start: $(date)"
echo "  N=$N (7 parallel, each serial)"
echo "  --resume: reuse 100-set results"
echo "  --all-prepared: 300 instances"
echo "  Extra args: $EXTRA_ARGS"
echo "========================================"

PIDS=()
for h in "${HARNESSES[@]}"; do
  LOG="$LOGDIR/${h}_7x300.log"
  echo "Starting $h → $LOG"
  nohup $PYTHON "$RUN_SCRIPT" \
    --harness "$h" \
    --all-prepared \
    --resume \
    $EXTRA_ARGS \
    > "$LOG" 2>&1 &
  PID=$!
  PIDS+=($PID)
  echo "  PID=$PID"
  sleep 2  # stagger start to avoid simultaneous rootfs access
done

echo ""
echo "All 7 harnesses launched. PIDs: ${PIDS[*]}"
echo "Logs: $LOGDIR/<harness>_7x300.log"
echo ""
echo "Monitor: tail -f $LOGDIR/*_7x300.log"
echo "Status:  ps -eo pid=,etimes=,args= | grep run_serial_kimi | grep -v grep"
echo ""
echo "ETA: ~42h wall (N=1). Check back periodically."
