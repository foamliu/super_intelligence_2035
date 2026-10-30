#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-LogicSynth-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'synthesis_qor_audit' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-LS4\", eval_id=\"20261030-ls4\", user=\"bench_ls4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your synthesis_qor_audit proc,
     - then paste and run this checker EXACTLY (it builds the Genus QoR report fixtures
       inline as multi-line strings and asserts on the returned dict; no external files
       needed -- pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call: set r [check synthesis_qor_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the CHECK_RESULT/RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the waveview Tcl regexp does NOT support \\b / \\s / \\d / \\w Perl classes; use POSIX
  classes like [[:space:]], [[:alnum:]_], [[:alpha:]] instead. Section headers are exact lines
  '=== TIMING (setup) ===', '=== TIMING (hold) ===', '=== AREA ===', '=== INSTANCE ===' (the
  parentheses are literal -- match them with [(] [)] or \\( \\)). Header comments set design/corner
  only when the colon comes IMMEDIATELY after the keyword ('# Design: ' / '# Corner: ').
  Slack values may be negative -- capture an optional leading minus (-?[0-9.]+). Area values carry
  a trailing unit token (um^2 or nm^2) -- extract it from the 'Total area' line. total_cells =
  leaf_cells + hierarchical_cells (registers are a SUBSET of leaf cells, do NOT subtract them).
  total_area is the EXPLICIT 'Total area' line value (do NOT compute it from parts -- macros are
  easily missed). area_check = 1 iff |combo+seq+macro - total| < 1e-6. timing_met = 1 iff both
  setup_wns>=0 AND hold_wns>=0. Keep your solution minimal. Do not modify the task prompt."
echo "=== pi-SUT LogicSynth-004 start $(date) ==="
echo "PROMPT_BYTES=${#PROMPT}"; printf "%s" "$PROMPT" | tr -cd "`" | wc -c; echo "DRY_OK"
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12
