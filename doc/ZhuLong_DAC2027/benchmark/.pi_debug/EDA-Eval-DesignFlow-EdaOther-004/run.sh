#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-EdaOther-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'vsim_pattern_coverage_audit' per the prompt. It takes two
  string arguments (reports_text, pattern_list_text) and returns a flat key/value string.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-EDA4\", eval_id=\"20261030-eda4\", user=\"bench_eda4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your vsim_pattern_coverage_audit proc,
     - then paste and run this checker EXACTLY (it builds the A_Summary.rpt fixtures and
       the reference pattern lists inline and asserts on the returned flat string; no
       external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call: set r [check vsim_pattern_coverage_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the waveview Tcl regexp does NOT support \\b / \\s / \\d / \\w Perl classes; use POSIX
  classes like [[:space:]], [[:alnum:]_], [[:digit:]] instead. Key real traps in this task:
  (1) colon-spacing ASYMMETRY: 'Total Pattern : N' has a space before the colon, but
  ' Failed Pattern: N' has a LEADING space and NO space before the colon -- a regex keyed
  on only one form misses the other; use [[:space:]]*:[[:space:]]* to handle both;
  (2) the reference pattern list may contain blank lines, '# comment' lines, trailing
  whitespace, carriage returns (\\r), and DUPLICATE entries -- skip blanks/comments, strip
  \\r/whitespace, and count UNIQUE names for expected_count;
  (3) bytemode is the .xN token (dot, literal x, digits) matched anywhere in the simdir;
  'basic.x4.rerun' -> bytemode 'x4' (NOT 'rerun'), regression 'basic'; a simdir with no
  .xN -> bytemode 'unknown';
  (4) pattern_list_entries counts ACTUAL post-separator pattern lines (raw, incl dups),
  NOT the 'Total Pattern' header sum -- a run may report 5 but list 4;
  (5) ran_unique collapses duplicates (a pattern listed twice in one run, or in two runs,
  counts ONCE in ran_unique);
  (6) missing = expected-but-not-ran; extra = ran-but-not-expected (DIRECTION matters);
  (7) the '---' separator and the Total/Failed/Global_Seed header lines BEFORE it are NOT
  pattern names. Use Tcl 'split' on newline, 'string map' to drop \\r, 'string trim',
  'regexp --' with POSIX classes, 'lsort' for sorting, 'join' with comma for bytemodes/
  regressions and with space for missing/extra name lists. Keep your solution minimal."
echo "=== pi-SUT EdaOther-004 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12
