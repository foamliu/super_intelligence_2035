#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-007
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_antenna_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 10 keys in order:
  total_nets total_lines pass_count warn_count fail_count
  skip_count worst_net max_ratio mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER7\", eval_id=\"20261030-aether7\", user=\"bench_aether7\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_antenna_audit proc,
     - then paste and run this checker EXACTLY (it builds the antenna-check
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_antenna_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'ratio=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare float SUMMARY fields NUMERICALLY (expr ==), NOT with
  string equal (so '100.0' equals '100'). Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) status CASE-INSENSITIVE: 'fail'/'FAIL'/'Fail' all match FAIL.
  (2) DUPLICATE (net,layer) pair: LAST occurrence WINS (replace ratio/limit/status,
      not sum, not first-wins). Counts ONCE in total_lines.
  (3) status ABSENT -> infer FAIL if ratio > limit else PASS (NEVER WARN/SKIP).
  (4) ratio == limit -> PASS (inclusive). FAIL only strict >.
  (5) missing limit= -> default 400.0.
  (6) missing ratio= -> default 0.0 (always PASS; included in max_ratio as 0.0).
  (7) max_ratio / worst_net over NON-SKIP lines ONLY. SKIP excluded even if its
      ratio is the file max. No non-SKIP -> max_ratio=-1.0, worst_net=\"\".
  (8) worst_net tie at max_ratio -> lexicographically SMALLEST net name
      (lsort -dictionary).
  (9) mismatched_summary: nets_checked/violations/warns/skipped INTEGER equality;
      max_ratio NUMERIC equality (expr ==, so '100.0' == 100); worst_net STRING
      equality. ABSENT SUMMARY fields NOT reported. Empty list if no SUMMARY.
      Computed: nets_checked=total_lines, violations=fail_count, warns=warn_count,
      skipped=skip_count.
  (10) verdict priority: fail_count>0 -> FAIL (TOP) > (mismatched_summary non-empty
       OR no SUMMARY) -> INCOMPLETE > PASS.
  gate_area / diode_area are red herrings; ignore them in all computed values.
  All output lists lex-sorted with lsort -dictionary."
echo "=== pi-SUT Aether-007 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
