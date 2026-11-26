#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-PnRSignoff-002
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)"
echo "=== pi-SUT PnRSignoff-002 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- tail of pi_run.log ---"
tail -25 pi_run.log
echo "--- REF_CHECK result lines ---"
grep -E "REF_CHECK_RC|REF_CHECK_MSG|CHECK_PASS|ASSERT FAIL" pi_run.log | head -10
