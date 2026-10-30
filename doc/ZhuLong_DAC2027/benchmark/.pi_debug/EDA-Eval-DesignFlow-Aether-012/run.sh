#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-012
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_pgmesh_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 14 keys in order:
  total_straps power_straps ground_straps unknown_straps
  short_count open_count skip_count
  min_width max_space worst_min_width_strap worst_max_space_strap
  coverage_pct mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER12\", eval_id=\"20261030-aether12\", user=\"bench_aether12\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_pgmesh_audit proc,
     - then paste and run this checker EXACTLY (it builds the PG-MESH fixtures
       inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_pgmesh_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'min_width=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare SUMMARY integer count fields with integer == and
  min_width/max_space with NUMERIC == (expr {double($a)==double($b)}).
  Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) direction & status CASE-INSENSITIVE (HORIZONTAL/horizontal, OK/Ok, SHORT/Short).
  (2) Duplicate (name, layer) key: LAST occurrence WINS (replace
      direction/width/space/vias/status, not sum, not first-wins). Counts ONCE.
  (3) (name, layer) is an ORDERED key: 'vdd1 M5' and 'vdd1 M6' are DIFFERENT
      keys, both counted. layer is part of the key.
  (4) status ABSENT or EMPTY -> default 'ok' (NEVER inferred from width/space).
  (5) missing width -> 0.0; missing space -> 0.0; missing vias -> 1. A missing
      width of 0.0 CAN become the min_width (default-ok non-skip strap).
  (6) min_width / max_space / worst_*_strap over NON-SKIP keys ONLY. short/open/
      ok are all NON-SKIP and INCLUDED. SKIP keys EXCLUDED even if they hold the
      extreme. If no non-SKIP: min_width=-1.0, max_space=-1.0, worst_*_strap=''.
  (7) worst_*_strap tie-break: LEX-SMALLEST name via lsort -dictionary (so
      strap2 < strap10, numeric-aware), NOT plain lsort -increasing.
  (8) coverage_pct = round((power+ground)*100/total); total==0 -> 0. Computed
      from NAME-classification counts regardless of status (a SKIP vdd1 still
      counts in power_straps and total).
  (9) mismatched_summary: ABSENT fields NOT reported. min_width/max_space with
      NUMERIC equality (0.080 == 0.08 -> match, NOT a mismatch). total/power/
      ground/coverage with integer equality. Empty list if no SUMMARY line.
  (10) verdict priority: FAIL (short>0) > REVIEW (open>0) > INCOMPLETE
       (no summary or mismatched) > PASS. FAIL beats PASS even with matching
       summary; REVIEW beats INCOMPLETE.
  All output lists lex-sorted with lsort -dictionary where applicable."
echo "=== pi-SUT Aether-012 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
