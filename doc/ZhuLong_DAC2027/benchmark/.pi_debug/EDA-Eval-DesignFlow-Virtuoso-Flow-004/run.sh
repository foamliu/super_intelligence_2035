#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Virtuoso-Flow-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'vflow_manifest_audit' per the prompt. It takes ONE string
  argument (manifest_text) and returns a flat Tcl dict with EXACTLY these 10 keys in
  this order:
  total_steps pass_steps fail_steps skip_steps missing_artifacts
  ghost_artifacts zero_byte_artifacts missing_checksum_signoff
  name_collisions verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-VF4\", eval_id=\"20261030-vf4\", user=\"bench_vf4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your vflow_manifest_audit proc,
     - then paste and run this checker EXACTLY (it builds the manifest fixtures inline
       and asserts on the returned dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         check vflow_manifest_audit; puts \"RESULT:ALL_ASSERTS_PASS\"; puts \"DESIGN_FLOW_VERDICT=PASS\"
       (the checker already prints RESULT:ALL_ASSERTS_PASS on success and errors out on failure)
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like [[:space:]],
  [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes. Use Tcl
  'split' on newline, 'string trim', 'regexp --' with POSIX classes, 'dict' for
  sets/maps, 'lsort' to sort lists, 'dict create' to build the returned dict in the
  exact key order. Keep your solution minimal.
- IMPORTANT Tcl quirk: do NOT use the nested-path form
  'dict lappend D step key \$val' to append a LIST-valued \$val -- it SPLITS \$val into
  its elements. Instead fetch the list, 'lappend' it (single arg = one element), and
  'dict set' it back.
- Key real traps in this task (a naive impl fails these -- the checker asserts the
  correct behavior):
  (1) missing_artifacts: a step whose LAST-WINS status is PASS but whose artifact list
      is EMPTY. Naive 'total artifacts > 0 -> ok' misses it (must gate per-step on PASS).
  (2) ghost_artifacts: artifact PATHS listed under a step whose status is FAIL or SKIP
      (stale leftovers). Naive ignores step status.
  (3) zero_byte_artifacts: artifact PATHS whose size == 0 AND owning step status is PASS
      (truncated write). Artifacts under FAIL/SKIP are ghosts, not zero-byte. Naive
      'size >= 0 ok' misses it.
  (4) missing_checksum_signoff: artifact PATHS whose signoff flag is 'true' but checksum
      is EMPTY, regardless of step status. Naive checks checksum generally, not gated on
      signoff.
  (5) name_collisions: artifact BASENAMES appearing under TWO OR MORE DISTINCT steps
      (cross-step). The same basename twice under the SAME step is a per-step duplicate,
      NOT a collision. Naive 'basename seen >1 -> collision' wrongly flags the per-step
      dup. Track basename -> set of distinct step names; collision iff >= 2 distinct
      steps.
  (6) LAST-WINS: a step with MORE THAN ONE [step:X] block -- the LAST block fully
      overwrites (status AND artifact list; the earlier block is entirely DISCARDED, NOT
      merged). Reset the step's status and artifact list to empty on EACH new [step:X]
      header. Naive merges artifact lists across blocks.
  (7) verdict 'clean' iff ALL FIVE violation lists (missing_artifacts, ghost_artifacts,
      zero_byte_artifacts, missing_checksum_signoff, name_collisions) are empty;
      otherwise 'dirty'. A FAIL or SKIP step with zero artifacts is CLEAN (consistent).
      Naive gates verdict on missing_artifacts alone, returning clean when only
      ghost/zero-byte/etc. are present."
echo "=== pi-SUT Virtuoso-Flow-004 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ==="
