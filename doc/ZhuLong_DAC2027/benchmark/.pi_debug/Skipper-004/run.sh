#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/Skipper-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat pi_prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'uvs_regr_compile_summary_audit' per the prompt. It takes TWO
  string arguments (compile_log_text, test_list_text) and returns a flat Tcl dict with
  EXACTLY these 13 keys in this order:
  tags_compiled total_rows compiled_ok compile_fail skipped
  error_total warn_total duplicate_compiles missing_compiles
  recovered_compiles elapsed_total_sec max_elapsed_tb overall_verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean Skipper Tcl sandbox:
  1. open_session(task_id=\"BENCH-SK4\", eval_id=\"20261030-sk4\", user=\"bench_sk4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"skipper\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your uvs_regr_compile_summary_audit proc,
     - then paste and run this checker EXACTLY (it builds the compile-log fixtures inline
       and asserts on the returned dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         check uvs_regr_compile_summary_audit; puts \"RESULT:ALL_ASSERTS_PASS\"; puts \"DESIGN_FLOW_VERDICT=PASS\"
       (the checker already returns ALL_ASSERTS_PASS on success and errors out on failure)
  3. close_session(workdir) to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean Skipper Tcl regexp supports POSIX classes like [[:space:]],
  [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes. Use Tcl
  'split' on newline, 'string trim', 'regexp --' with POSIX classes, 'dict' for
  sets/maps, 'lsort' to sort lists, 'dict create' to build the returned dict in the
  exact key order. Keep your solution minimal.
- Key real traps in this task (a naive impl fails these -- the checker asserts the
  correct behavior):
  (1) elapsed normalization: '1:30' means 90 seconds (m*60+ss), NOT int('1:30'). Plain
      ints stay ints.
  (2) last-wins dedup by (testbench, tag): a re-compile in the SAME tag REPLACES the
      earlier row's errors/warns/elapsed (does NOT accumulate). duplicate_compiles counts
      only same-(tb,tag) overrides.
  (3) same testbench in DIFFERENT tags is NOT a duplicate (different tag -> different key).
  (4) missing_compiles: declared testbench never compiled in any tag -> reported (sorted).
  (5) recovered_compiles: a testbench whose last-wins status is FAIL in some tag AND OK in
      another (cross-tag recovery). A tb that only ever fails is NOT recovered.
  (6) max_elapsed_tb: the testbench with the largest normalized elapsed across all
      last-wins pairs; on a TIE the lexicographically SMALLEST name wins; empty string if
      no rows. (Per-tb max across tags, then global max.)
  (7) overall_verdict priority FAIL > INCOMPLETE > PASS: FAIL when compile_fail>0;
      INCOMPLETE when no FAIL but missing_compiles non-empty; PASS otherwise."
echo "=== pi-SUT Skipper-004 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ==="
