#!/bin/bash
# thermo r2 launch: setsid bash -lc with PATH+https_proxy injection
export PATH=/home/app.e0031982/.local/node-20/bin:$HOME/.bun/bin:$PATH
export https_proxy=http://172.19.92.23:13128
cd /nasdata/app.e0031982/code/EDA-Flow-Bench
# ensure fresh status file (do not reuse)
rm -f eval/status_thermo_r2.jsonl
TS=$(date +%Y%m%d_%H%M)
LOG="eval/run_thermo_r2_${TS}.log"
setsid bash -lc "export PATH=/home/app.e0031982/.local/node-20/bin:\$HOME/.bun/bin:\$PATH; export https_proxy=http://172.19.92.23:13128; cd /nasdata/app.e0031982/code/EDA-Flow-Bench; bash eval/run_batch.sh --workers 4 --status /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/status_thermo_r2.jsonl" > "$LOG" 2>&1 < /dev/null &
echo "r2 launched setsid parent PID=$!"
echo "log=$LOG"
sleep 8
echo "=== run_batch proc ==="; pgrep -fa "run_batch.sh --workers 4 --status.*status_thermo_r2" | head -2
echo "=== log head ==="; head -6 "$LOG" 2>/dev/null
echo "=== status file (should be 0 lines fresh) ==="; wc -l eval/status_thermo_r2.jsonl 2>/dev/null || echo "not created yet (normal early)"
