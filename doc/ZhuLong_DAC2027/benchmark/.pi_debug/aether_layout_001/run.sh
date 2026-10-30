#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/aether_layout_001
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT=$(python3 -c "import json;print(json.load(open('/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl'))['prompt'])")
echo "=== pi debug start $(date) ==="
timeout 1500 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ==="
echo "=== outputs dir ==="
ls -laR outputs 2>&1
