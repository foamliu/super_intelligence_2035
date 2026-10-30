#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Analog-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'hspice_meas_script_parse' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-ANA3\", eval_id=\"20261029-a3\", user=\"bench_ana3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your hspice_meas_script_parse proc,
     - then paste and run this checker EXACTLY (it builds the measure-script fixtures inline
       and asserts the parsed dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the CHECK_RESULT/DETAIL line from the sandbox run, and state PASS if
  DESIGN_FLOW_VERDICT==PASS.
- NOTE: the waveview Tcl regexp does NOT support \\b / \\s / \\d / \\w Perl classes; use POSIX
  classes like [[:space:]], [^[:space:]], [[:graph:]] instead. Tokenize on runs of whitespace
  (spaces OR tabs) with regexp -all -inline -- {[^[:space:]]+}. Keep your solution minimal.
  Do not modify the task prompt."
echo "=== pi-SUT Analog-003 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- DESIGN_FLOW_VERDICT result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|PASS .* FAIL" pi_run.log | head -12
