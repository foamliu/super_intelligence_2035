#!/bin/bash
# R1000 watcher: wait for claude-code incr_eval docker container to finish,
# then regen eval summaries + HTML report.  Auto-exits; logs to logs/watch_regen_R1000.log.
cd "$(dirname "$0")"
LOG=logs/watch_regen_R1000.log
exec >>"$LOG" 2>&1
echo "=== watch_regen START $(date) ==="
# Wait up to 25 min for the scikit-learn__scikit-learn-14710 container to exit.
for i in $(seq 1 150); do
  if ! sg docker -c 'docker ps --format {{.Names}}' 2>/dev/null | grep -q 'verified_full_claude-code'; then
    echo "[$(date)] container gone after ${i} polls"
    break
  fi
  sleep 10
done
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py
echo "[$(date)] === regenerate HTML report ==="
python3 ../gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== watch_regen DONE $(date) ==="
