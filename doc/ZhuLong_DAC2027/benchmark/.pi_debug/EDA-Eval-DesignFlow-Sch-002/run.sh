#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Sch-002
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'netlist_lib_cell_map' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-SCH2\", eval_id=\"20261030-sch2\", user=\"bench_sch2\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block:
     - define your netlist_lib_cell_map proc (and any helper),
     - then paste and run this checker EXACTLY (it builds the cell_list + netlist fixtures
       inline as multi-line strings with backslash-n newlines and asserts on the returned dict;
       no external files needed -- pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call: set r [check netlist_lib_cell_map]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: you do NOT need regexp -- use Tcl string range / string trim / string trimleft /
  string index / string length / split / dict create. HEADER RECOGNITION is strict: after
  stripping the leading '*' and trimming, the body must start with EXACTLY 'Library' / 'Cell' /
  'View' (case-SENSITIVE) and the very next non-space char after the keyword must be ':'. A line
  like '* Library catalog : fake' is NOT a Library header. Maintain a current-library / current-cell
  state machine; EMIT only on a '* View : schematic' header (skip symbol/other views). Dedup pairs
  by \"\$lib|\$cell\" (NOT by cell name -- a cell in two libraries yields TWO pairs). Only emit for
  cells present in the cell_list (dedup the cell_list to unique names; total_cell_list counts
  unique). Report unmapped (requested but no schematic pair) and multi_lib_cells (>1 distinct
  library). verdict = 'complete' if unmapped_count==0 else 'incomplete'. Keep your solution minimal.
  Do not modify the task prompt."
echo "=== pi-SUT Sch-002 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|ALL_ASSERTS_PASS|RESULT:" pi_run.log | head -12
