#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Virtuoso-Flow-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'vflow_runlog_audit' per the prompt. It takes ONE string
  argument (runlog_text) and returns a flat Tcl dict with EXACTLY these 10 keys in order:
  steps_seen step_status step_attempts step_duration_sec skip_reasons
  total_wall_sec retried_steps skipped_steps failed_steps overall_verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-VF3\", eval_id=\"20261030-vf3\", user=\"bench_vf3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your vflow_runlog_audit proc,
     - then paste and run this checker EXACTLY (it builds the runlog fixtures inline
       and asserts on the returned dict; no external files needed -- pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check vflow_runlog_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like [[:space:]],
  [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes. Use Tcl
  'split' on newline, 'string map' to drop \\r, 'string trim', 'regexp --' with POSIX
  classes, 'dict' for sets/maps, 'lsort' to sort the pair-list keys, 'dict create' to
  build the returned dict in the exact key order. Keep your solution minimal.
- Key real traps in this task (a naive impl fails these -- the checker asserts the
  correct behavior):
  (1) RETRY attempts = number of '[step:X] start' lines (block count), NOT number of
      'retry' lines. A step that fails with no retry still has attempts = 1.
  (2) LAST-WINS: a block with PASS then later ERROR -> final ERROR, not PASS.
  (3) skipped_steps must include ALL skip reasons (upstream-failed AND user and any
      other), not only upstream-failed.
  (4) total_wall_sec = (flow_end - flow_start) wall clock, NOT the sum of per-step
      final-block durations (setup gap + discarded retry time are excluded from the sum
      but included in the wall).
  (5) MIDNIGHT rollover: end_ts < start_ts means +86400 (23:59:55 -> 00:00:05 = 10s,
      not negative).
  (6) overall_verdict priority ERROR > SKIPPED > PASS (a flow with both a final FAIL
      and a SKIP is ERROR, not SKIPPED).
  (7) steps_seen de-duplicated in FIRST-APPEARANCE order (a retried step appears once,
      not once per start)."
echo "=== pi-SUT Virtuoso-Flow-003 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ==="
