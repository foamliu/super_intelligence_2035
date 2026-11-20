#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-InnovusNetlist-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'def_net_connectivity_audit' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-INN4\", eval_id=\"20261030-inn4\", user=\"bench_inn4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your def_net_connectivity_audit proc,
     - then paste and run this checker EXACTLY (it builds the NETS/SPECIALNETS fixtures
       inline as multi-line strings and asserts on the returned dict; no external
       files needed -- pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call: set r [check def_net_connectivity_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: power classification has STRICT precedence (first match wins): SPECIALNETS membership
  > USE attr (POWER/GROUND) > name pattern (VDD/VSS/GND/VCC/VEE exact). A net with explicit
  USE SIGNAL is SIGNAL even if its name is VDD-like (USE wins over pattern when USE is explicit);
  a net with NO USE attr falls back to the name pattern. Duplicate (inst,pin) pairs within one
  net collapse to one unique connection; track discarded duplicates in duplicate_connections.
  single_pin_signal = signal nets with UNIQUE pin count == 1; unconnected_signal = 0 pins.
  All lists sorted (lsort). Use pure Tcl string ops; POSIX classes if regexp (no backslash-s/d/b).
  Keep your solution minimal. Do not modify the task prompt."
echo "=== pi-SUT InnovusNetlist-004 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12
