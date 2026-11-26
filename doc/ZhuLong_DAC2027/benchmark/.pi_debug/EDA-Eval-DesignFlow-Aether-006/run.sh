#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-006
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_metalfill_target_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 10 keys in order:
  total_layers total_fill underfill_layers met_layers missing_target_layers
  zero_fill_met_layers min_density_layer max_density_layer mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER6\", eval_id=\"20261030-aether6\", user=\"bench_aether6\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_metalfill_target_audit proc,
     - then paste and run this checker EXACTLY (it builds the metal-fill density
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_metalfill_target_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'target=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare float SUMMARY fields NUMERICALLY (expr ==), NOT with
  string equal (so '72.30' equals '72.3'). Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) DUPLICATE layer NAMES: LAST occurrence WINS (replace target/actual/fill_count,
      not sum, not first-wins). total_layers counts name only ONCE.
  (2) total_fill sums LAST-WINS distinct fill_count (missing fill_count= -> 0),
      NOT all input LAYER lines.
  (3) missing actual= -> actual defaults to 0.0 (layer still counts; 0.0 used for
      underfill compare and min/max density).
  (4) missing target= -> layer goes to missing_target_layers, NOT underfill, NOT met.
  (5) underfill is STRICT less-than (actual < target); actual == target is MET.
  (6) met = actual >= target (inclusive).
  (7) min/max density tie -> lexicographically SMALLEST name wins (lsort -dictionary).
  (8) mismatched_summary: min_density/max_density compared NUMERICALLY (expr ==),
      so '72.30' matches computed '72.3'; total_layers/total_fill compared as int.
      Absent SUMMARY fields NOT reported. Empty if no SUMMARY. If no layers, any
      provided min_density/max_density is mismatched; total_layers=total_fill=0 must
      match or be reported too.
  (9) verdict priority: underfill non-empty -> FAIL (TOP) > missing_target non-empty
      OR no-SUMMARY -> INCOMPLETE > PASS.
  (10) zero_fill_met_layers: layers with actual >= target AND fill_count == 0
       (missing fill_count= defaults 0 -> flagged). All output lists lex-sorted."
echo "=== pi-SUT Aether-006 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
