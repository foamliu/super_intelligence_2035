#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_drc_audit' per the prompt. It takes ONE
  string argument (drc_text) and returns a flat Tcl dict with EXACTLY
  these 10 keys in order:
  total_rules total_violations error_count warning_count checked_rules
  duplicate_rule_names per_layer_errors mismatched_summary layers_used verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER3\", eval_id=\"20261030-aether3\", user=\"bench_aether3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_drc_audit proc,
     - then paste and run this checker EXACTLY (it builds the DRC-report
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_drc_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'layer=*'), 'string tolower' for case-insensitive severity, 'lsort -dictionary'
  for lexicographic sorting + tie-breaks, 'array'/'info exists' for sets,
  'dict create' for the returned dict in exact key order. Use 'format %c 10'
  for newline if you need to split lines. Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) severity CASE-INSENSITIVE (ERR/Err/err all errors).
  (2) DUPLICATE rule names: LAST occurrence WINS (replace, not sum, not first-wins).
  (3) duplicate_rule_names still REPORTS names seen >1 time (sorted, dedup).
  (4) ZERO-count rules still count toward checked_rules (do not skip them).
  (5) missing SUMMARY -> verdict INCOMPLETE (NOT PASS), and mismatched_summary empty.
  (6) per_layer_errors ONLY err layers, sorted, warn excluded.
  (7) mismatched_summary compares computed vs SUMMARY per-field; absent fields not reported.
  (8) verdict priority: error>0 FAIL > warning>0 WARN > no-summary INCOMPLETE > PASS.
  (9) layers_used sorted, includes err AND warn layers, dedup.
  (10) All output lists lexicographically sorted (lsort -dictionary)."
echo "=== pi-SUT Aether-003 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
