#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Sch-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'spice_subckt_pin_arity_audit' per the prompt. It takes ONE string
  argument (netlist_text) and returns a flat Tcl dict with EXACTLY these 8 keys in order:
  total_subckts_defined subckts_defined instances_scanned arity_matches arity_mismatches
  unknown_subckt_instances malformed_instances verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-SCH3\", eval_id=\"20261030-sch3\", user=\"bench_sch3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your spice_subckt_pin_arity_audit proc,
     - then paste and run this checker EXACTLY (it builds the netlist fixtures inline
       and asserts on the returned dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check spice_subckt_pin_arity_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like [[:space:]],
  [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes. Use Tcl
  'split' on newline, 'string map' to drop \\r, 'string trim', 'regexp --' with POSIX
  classes, 'string match *=* \$tok' to detect params, 'dict' for sets/maps, 'lsort' to
  sort all the list keys, 'dict create' to build the returned dict in the exact key
  order. Keep your solution minimal.
- Key real traps in this task (a naive impl fails these -- the checker asserts the
  correct behavior):
  (1) PARAM EXCLUSION: tokens with '=' are NOT pins and NOT the subckt name.
      'X1 a b INV w=1u l=1u' -> pins=[a b] (count 2), sub=INV. Naive 'count all middle
      tokens' -> 4 pins -> false mismatch.
  (2) LAST-WINS .subckt REDEFINITION: a repeated '.subckt NAME' REPLACES port_count.
      Naive 'first def wins' -> false match.
  (3) '+' CONTINUATION JOIN: an instance/header split across '+' lines must be joined
      before tokenizing. Naive per-line -> wrong subckt name / pin count.
  (4) UNKNOWN != MISMATCH: an undefined-subckt instantiation goes to
      unknown_subckt_instances, NOT arity_mismatches. Naive 'compare to 0 ports' ->
      false mismatch.
  (5) COMMENT ('*' col1) / BLANK lines are skipped AND break a pending continuation.
  (6) MALFORMED: an 'X' instance with only params (no node token) -> malformed_instances,
      NOT unknown/mismatch. Naive 'last token = subckt regardless of =' -> false unknown.
  (7) LEXICOGRAPHIC SORT: every output list sorted ascending (lsort) for determinism.
  (8) verdict = 'pass' iff arity_mismatches empty AND unknown_subckt_instances empty AND
      malformed_instances == 0; else 'fail'. instances_scanned/total_subckts_defined do
      NOT affect verdict."
echo "=== pi-SUT Sch-003 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ==="
