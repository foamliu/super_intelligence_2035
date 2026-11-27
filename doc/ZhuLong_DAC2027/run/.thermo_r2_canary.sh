#!/bin/bash
# thermo r2 canary: single case real run, verdict must be PASS (cert b)
export PATH=/home/app.e0031982/.local/node-20/bin:$HOME/.bun/bin:$PATH
export https_proxy=http://172.19.92.23:13128
cd /nasdata/app.e0031982/code/EDA-Flow-Bench
rm -f eval/canary_thermo_r2.jsonl
bash eval/run_one.sh DrcDensityParseJudge-001 --shard C \
  --model doubao-seed-2.0-pro-cloud --thinking low --timeout 2400 \
  --status /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/canary_thermo_r2.jsonl \
  > /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/canary_thermo_r2.log 2>&1
echo "canary_exit=$?" >> /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/canary_thermo_r2.log
