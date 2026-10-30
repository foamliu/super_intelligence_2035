#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-010
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_pgshort_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 12 keys in order:
  total_shorts short_count leak_count clean_count power_count
  ground_count mixed_pairs max_resistance worst_pair layers_affected
  mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER10\", eval_id=\"20261030-aether10\", user=\"bench_aether10\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_pgshort_audit proc,
     - then paste and run this checker EXACTLY (it builds the PG-short
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_pgshort_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'type=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare SUMMARY numeric fields with 'expr ==' (NOT string equal).
  Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) status CASE-INSENSITIVE: 'short'/'SHORT'/'Short' all match short.
  (2) DUPLICATE ordered pair (net_a, net_b): LAST occurrence WINS (replace
      type/resistance/layer/status, not sum, not first-wins). Counts ONCE.
  (3) status ABSENT or EMPTY -> infer from resistance: R<1.0->short,
      1.0<=R<100.0->leak, R>=100.0->clean (NEVER unknown).
  (4) R==1.0 -> leak (inclusive), R==100.0 -> clean (inclusive). strict.
  (5) missing resistance -> default 0.0 -> short (0.0 < 1.0).
  (6) max_resistance / worst_pair / layers_affected over NON-CLEAN pairs ONLY.
      clean excluded even if higher R. No non-clean -> max_resistance=-1.0,
      worst_pair=\"\", layers_affected={}.
  (7) worst_pair tie at max_resistance -> lexicographically SMALLEST
      'net_a-net_b' (lsort -dictionary, numeric-aware: 'via2-vss' < 'via10-vss').
  (8) type 'mixed' counts in BOTH power_count AND ground_count (not exclusive).
  (9) (net_a, net_b) is ORDERED: (a,b) and (b,a) are DIFFERENT pairs, both
      counted. Do NOT normalize/sort the pair.
  (10) mismatched_summary: shorts_checked/shorts/leaks/clean INTEGER equality;
       max_resistance NUMERIC equality (expr ==, so 5.0==5 is MATCH); worst_pair
       STRING equality. ABSENT fields NOT reported. Empty list if no SUMMARY.
       verdict priority: short>0->FAIL > leak>0->REVIEW > mismatched/no-summary
       ->INCOMPLETE > PASS (REVIEW beats INCOMPLETE even with mismatched).
  All output lists lex-sorted with lsort -dictionary."
echo "=== pi-SUT Aether-010 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
