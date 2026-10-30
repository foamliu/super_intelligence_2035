#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Analog-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'hspice_corner_worst_case_audit' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AN004\", eval_id=\"20261030-an004\", user=\"bench_an004\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your hspice_corner_worst_case_audit proc,
     - then paste and run this checker EXACTLY (it builds the corner_results/spec fixtures
       inline and asserts on the returned dict; no external files needed -- pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call: set r [check hspice_corner_worst_case_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: signed margin is min-spec: value - bound (pass if >=0); max-spec: bound - value (pass if >=0).
  A metric ABSENT from a corner line is SKIPPED for that metric (counted in missing_count) but
  is NOT a failure (do not treat missing as 0). Worst corner per metric = smallest margin; ties
  broken by lexicographically smallest corner NAME (lsort ascending). Overall worst = the single
  (metric, corner) with the smallest margin across all metrics measured at least once (or
  worst_metric=\"\", worst_corner=\"\", worst_margin=0 if nothing measured). Overall verdict is
  'pass' iff NO measured pair failed (vacuously pass when empty). All lists sorted (lsort).
  Use pure Tcl string ops; POSIX classes if regexp (no backslash-s/d/b). Keep your solution minimal.
  Do not modify the task prompt."
echo "=== pi-SUT Analog-004 start $(date) ===" > run.out
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec" >> run.out
echo "--- result lines ---" >> run.out
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12 >> run.out
