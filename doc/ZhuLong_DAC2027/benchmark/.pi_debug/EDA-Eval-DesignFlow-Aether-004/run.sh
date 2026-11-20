#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_gds_layermap_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 11 keys in order:
  total_layers total_shapes drawing_layers pin_layers label_layers
  dup_gdsno missing_purpose_layers max_shape_layer mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER4\", eval_id=\"20261030-aether4\", user=\"bench_aether4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_gds_layermap_audit proc,
     - then paste and run this checker EXACTLY (it builds the GDS layer-map
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_gds_layermap_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'gdsno=*'), 'string tolower' for case-insensitive purpose, 'lsort -dictionary'
  for lexicographic sorting + tie-breaks, 'array'/'info exists' for sets,
  'dict create' for the returned dict in exact key order. Avoid lassign if
  unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) purpose CASE-INSENSITIVE (DRAWING/Drawing/drawing all drawing).
  (2) DUPLICATE layer NAMES: LAST occurrence WINS (replace, not sum, not first-wins).
  (3) dup_gdsno = shared (gdsno AND datatype) PAIR; same gdsno DIFFERENT datatype
      is NOT a dup. List ALL layers sharing a pair, each name once.
  (4) missing purpose: a layer with empty purpose goes to missing_purpose_layers,
      NOT defaulted to drawing, NOT in drawing/pin/label.
  (5) max_shape_layer tie -> lexicographically SMALLEST name wins.
  (6) total_shapes sums LAST-WINS distinct counts (not all input lines).
  (7) mismatched_summary: absent SUMMARY fields NOT reported; empty if no SUMMARY.
  (8) verdict priority: dup_gdsno non-empty FAIL > missing_purpose non-empty
      INCOMPLETE > no-summary INCOMPLETE > PASS.
  (9) All output lists lexicographically sorted (lsort -dictionary).
  (10) count default 0 when count= field is absent."
echo "=== pi-SUT Aether-004 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
