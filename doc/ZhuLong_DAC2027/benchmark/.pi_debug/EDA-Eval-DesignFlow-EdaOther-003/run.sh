#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-EdaOther-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'regr_log_classify' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-EDA3\", eval_id=\"20261029-eda3\", user=\"bench_eda3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your regr_log_classify proc,
     - then paste and run this checker EXACTLY (it builds the regression log fixtures
       inline via a helper L and asserts on the returned flat string; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call: set r [check regr_log_classify]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the CHECK_RESULT/RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the waveview Tcl regexp does NOT support \\b / \\s / \\d / \\w Perl classes; use POSIX
  classes like [[:space:]], [[:alnum:]_], [[:alpha:]] instead. A regression event line has the
  form '[ STATUS ] <test> seed=<n> ...' where STATUS is one of RUN/PASS/FAIL/TIMEOUT/SKIP/XPASS/XFAIL
  and the spaces inside the brackets may vary (e.g. '[ TIMEOUT]' has no trailing space before ']').
  Use a regex like '^\\[ +([A-Z]+) *\\] (.*)\$'. Lines not matching (banner comments '# ...',
  tool warnings 'xrun: ...', blank lines) are NOISE and must be skipped. The rerun marker is the
  literal substring '(rerun #N)'. Keep your solution minimal. Sort rerun_tests/flaky_tests ascending.
  Do not modify the task prompt."
echo "=== pi-SUT EdaOther-003 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12
