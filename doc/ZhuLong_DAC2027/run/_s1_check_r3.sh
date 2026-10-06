#!/bin/bash
echo "=== DATE ==="
date
echo "=== PGREP run_cline_script ==="
pgrep -af run_cline_script
echo "=== PGREP exit code ==="
pgrep -f '^bash scripts/run_cline_script'
echo "rc=$?"
echo "=== DF /home ==="
df -h /home
echo "=== LOG TAIL ==="
tail -25 /tmp/ABL_omega_low_r3.log
echo "=== LOG SCORE (pass) ==="
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_omega_low_r3.log | tail -5
echo "=== PS python/bash ==="
ps -eo pid,etime,time,cmd | grep -E 'run_cline|python' | grep -v grep
echo "=== DONE ==="