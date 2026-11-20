#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-PV-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'drc_waiver_apply_audit' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id="BENCH-PV4", eval_id="20261030-pv4", user="bench_pv4", sample="0") to get a workdir.
  2. run_code with lang="tcl" host="waveview" and workdir=<the workdir>. In ONE Tcl code block:
     - define your drc_waiver_apply_audit proc,
     - then paste and run this checker EXACTLY (it builds the DRC violations + waiver fixtures
       inline as multi-line tab-separated strings and asserts on the returned dict; no external
       files needed -- pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call: set r [check drc_waiver_apply_audit]; puts "RESULT:$r"; if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: you do NOT need regexp here -- use Tcl split (on tab), string tolower, and string
  compare / eq. The wildcard star char is a LITERAL single-char string equality (do NOT treat
  it as a glob). Rule comparison is case-INSENSITIVE (string tolower both sides); cell/x/y/layer
  are exact string match OR the star char. First-match wins: each violation waived at most once;
  a waiver that only matches already-waived violations is a DUPLICATE; a waiver that matches
  nothing is an ORPHAN. remaining_by_rule uses the violation ORIGINAL-CASE rule name as key and
  is the literal string none when empty. Keep your solution minimal. Do not modify the task prompt."
echo "=== pi-SUT PV-004 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12
