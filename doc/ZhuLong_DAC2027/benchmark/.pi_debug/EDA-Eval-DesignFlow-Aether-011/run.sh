#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-011
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_eco_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 12 keys in order:
  total_ecos add_count delete_count modify_count swap_count
  applied_count pending_count rejected_count skipped_count
  cells_affected mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER11\", eval_id=\"20261030-aether11\", user=\"bench_aether11\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_eco_audit proc,
     - then paste and run this checker EXACTLY (it builds the ECO fixtures
       inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_eco_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'cell=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare SUMMARY integer count fields with integer ==.
  Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) action CASE-INSENSITIVE: 'add'/'ADD'/'Add' all match add.
  (2) status CASE-INSENSITIVE: 'applied'/'APPLIED'/'Applied' all match applied.
  (3) Duplicate (action, inst_name) key: LAST occurrence WINS (replace
      cell/status/delta, not sum, not first-wins). Counts ONCE in total_ecos.
  (4) (action, inst_name) is an ORDERED key: 'add u1' and 'modify u1' are
      DIFFERENT keys, both counted. action is part of the key.
  (5) status ABSENT or EMPTY -> infer from delta: >0 applied, ==0 skipped,
      <0 pending. NEVER treat absent as skipped by default.
  (6) delta==0.0 -> skipped (inclusive); delta>0 -> applied; delta<0 -> pending.
  (7) missing delta -> default 0.0 -> skipped (0.0 == 0.0).
  (8) cells_affected: UNION over ALL keys (regardless of status), deduplicated,
      lex-sorted. Empty/absent cell values NOT added.
  (9) mismatched_summary: ABSENT summary fields NOT reported. Empty list if no
      SUMMARY line. Integer equality for all count fields.
  (10) verdict priority: FAIL (rejected>0) > REVIEW (pending>0) > INCOMPLETE
       (no summary or mismatched) > PASS. A REVIEW case with mismatched summary
       is still REVIEW.
  All output lists lex-sorted with lsort -dictionary."
echo "=== pi-SUT Aether-011 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
