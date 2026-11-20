#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-PnRSignoff-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'pnr_signoff_audit_pt_launcher' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-PNR3\", eval_id=\"20261029-p3\", user=\"bench_pnr3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your pnr_signoff_audit_pt_launcher proc,
     - then paste and run this checker EXACTLY (it builds the launcher fixtures inline
       and asserts the audit dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the CHECK_RESULT/DETAIL line from the sandbox run, and state PASS if
  DESIGN_FLOW_VERDICT==PASS.
- NOTE: the waveview Tcl regexp does NOT support \b word boundaries; use [[:space:]]
  or explicit boundaries. Keep your solution minimal. Do not modify the task prompt."
echo "=== pi-SUT PnRSignoff-003 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- DESIGN_FLOW_VERDICT result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|PASS .* FAIL" pi_run.log | head -12
