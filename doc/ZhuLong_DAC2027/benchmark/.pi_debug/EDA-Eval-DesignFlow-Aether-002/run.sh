#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-002
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_placement_audit' per the prompt. It takes ONE
  string argument (placement_text) and returns a flat Tcl dict with EXACTLY
  these 10 keys in order:
  total_instances total_rects pin_count duplicate_inst_names
  malformed_entries overlapping_pairs missing_layers unconnected_pins
  layers_used verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER2\", eval_id=\"20261030-aether2\", user=\"bench_aether2\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_placement_audit proc,
     - then paste and run this checker EXACTLY (it builds the placement-report
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_placement_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'origin=*'), 'string range' to strip prefixes/parens, 'lsort -dictionary'
  for lexicographic sorting + tie-breaks, 'array'/'info exists' for sets,
  'dict create' for the returned dict in exact key order. Use 'format %c 10'
  for newline if you need to split lines. Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) STRICT INTERIOR overlap: touching edges (urx==other.llx) are NOT overlap.
  (2) MALFORMED includes ZERO-AREA (urx==llx), not just inverted (urx<llx).
  (3) layers_used / missing_layers / unconnected_pins key off RECT layers ONLY.
  (4) OVERLAP is INST vs INST only; RECTs/PINs excluded.
  (5) MALFORMED instances are EXCLUDED from overlap detection.
  (6) VERDICT = single highest-priority category (malformed>overlap>missing_layer>unconnected_pin).
  (7) overlapping_pairs: each unordered pair ONCE, smaller name first, lex sorted, dedup.
  (8) All output lists lexicographically sorted (lsort -dictionary)."
echo "=== pi-SUT Aether-002 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -25 pi_run.log
