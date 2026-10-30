#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/Virtuoso-Flow-002
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'vflow_config_validate' per the prompt. It takes ONE string
  argument (config_text) and returns a flat Tcl dict with EXACTLY these 8 keys in order:
  missing_global_keys undeclared_steps missing_step_blocks steps_no_cmd
  undefined_deps cycle_members exec_order verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-VF2\", eval_id=\"20261030-vf2\", user=\"bench_vf2\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your vflow_config_validate proc,
     - then paste and run this checker EXACTLY (it builds the flow.config fixtures inline
       and asserts on the returned dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check vflow_config_validate]; puts \"RESULT:\$r\"; if {\$r eq \"CHECK_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like [[:space:]],
  [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes. Use Tcl
  'split' on newline, 'string map' to drop \\r, 'string trim', 'regexp --' with POSIX
  classes, 'dict' for sets/maps, 'lsort' to sort all the list keys, 'dict create' to
  build the returned dict in the exact key order. Keep your solution minimal.
- Key real traps in this task (a naive impl fails these -- the checker asserts the
  correct behavior):
  (1) [steps] registry line is BARE (e.g. 'rscalc pe autovia') -- it has NO 'key = value'
      form; parse the whole trimmed line (or the part after '=' if present) splitting on
      commas AND whitespace, de-duplicating into a registry set.
  (2) LAST-WINS duplicate [step:X] block: a second [step:X] block FULLY OVERWRITES the
      earlier one's cmd/deps (reset cmd='' and deps={} on block open, then apply the new
      block's keys). Do NOT merge blocks; do NOT let first-block cmd survive.
  (3) self-dependency 'depends = X' inside step X where X IS in the registry is a CYCLE of
      1 (cycle_members includes X), NOT an undefined dep.
  (4) undefined dep (depends on a name NOT in the registry) is reported in undefined_deps
      as 'step:dep', but it does NOT drop the step from exec_order: only REGISTRY deps gate
      readiness; non-registry deps create no graph edge.
  (5) cycle_members: a node v is on a cycle iff v can reach itself (path length>=1) along
      registry-dep edges. If any cycle exists, exec_order is the EMPTY list.
  (6) exec_order: Kahn's algorithm with LEXICOGRAPHIC tie-break -- among ready steps
      (all registry deps already emitted) always emit the lsort-smallest name. A registry
      step with no block, or a block with no depends, has no deps and is ready immediately.
  (7) unknown sections (not [global]/[steps]/[step:...]) are IGNORED, not errors. A
      required global key present with an EMPTY value still counts as present (only ABSENT
      keys go in missing_global_keys). steps_no_cmd considers blocks whose cmd is empty
      (key absent OR 'cmd = ' empty).
  (8) verdict = 'valid' iff ALL six error lists (missing_global_keys, undeclared_steps,
      missing_step_blocks, steps_no_cmd, undefined_deps, cycle_members) are empty; else
      'invalid'. exec_order non-empty does NOT make it valid by itself."
echo "=== pi-SUT Virtuoso-Flow-002 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|CHECK_PASS|RESULT:" pi_run.log | head -12
