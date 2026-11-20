#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Wave-005
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'wv_count_by_pattern' per the prompt.
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Synopsys Custom WaveView sandbox:
  1. open_session(task_id=\"BENCH-WAVE5\", eval_id=\"20261029-w5\", user=\"bench_wave5\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code block, define your proc, then run this checker exactly:
     ---CHECKER START---
     proc assert {cond msg} {
         set ok [uplevel 1 [list expr \$cond]]
         if {!\$ok} { error \"ASSERT FAIL: \$cond -- \$msg\" }
     }
     proc check {candidate} {
         set fsdb \"/apps/synopsys/verdi/Verdi_M-2017.03-SP2-9/demo/mixed/mixed.fsdb\"
         assert {[\$candidate \$fsdb \"*clock*\"] == 9} \"clock count mismatch\"
         assert {[\$candidate \$fsdb \"*rst*\"] == 13} \"rst count mismatch\"
         assert {[\$candidate \$fsdb \"*data*\"] == 7} \"data count mismatch\"
         assert {[\$candidate \$fsdb \"*En_*\"] == 24} \"En_ count mismatch\"
         assert {[\$candidate \$fsdb \"*\"] == 240} \"total count mismatch\"
         assert {[\$candidate \$fsdb \"*no_such_signal_zzz*\"] == 0} \"no-match must be 0\"
         set fo [sx_open_sim_file_read \$fsdb]
         set ic 0
         for {set w [sx_first_wave \$fo]} {\$w ne \"NULL\" && \$w ne \"\"} {set w [sx_next_wave \$w]} {
             if {[string match \"*clock*\" [sx_get_name \$w]]} { incr ic }
         }
         catch {sx_close_sim_file \$fo}
         assert {\$ic == 5} \"sanity naive baseline clock=5\"
         assert {[\$candidate \$fsdb \"*clock*\"] != \$ic} \"must use sx_signal not iterate+stringmatch\"
     }
     set err \"\"
     if {[catch {check wv_count_by_pattern} e]} { set err \$e }
     if {\$err eq \"\"} { puts \"REF_CHECK_RC=0\" ; puts \"REF_CHECK_MSG=CHECK_PASS\" } else { puts \"REF_CHECK_RC=1\" ; puts \"REF_CHECK_MSG=\$err\" }
     ---CHECKER END---
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'REF_CHECK_RC=<0 or 1>' and 'REF_CHECK_MSG=<message>' from the sandbox run, and state PASS if REF_CHECK_RC==0.
- Keep your solution minimal. Do not modify the task prompt."
echo "=== pi-SUT Wave-005 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- tail of pi_run.log ---"
tail -30 pi_run.log
echo "--- REF_CHECK result lines ---"
grep -E "REF_CHECK_RC|REF_CHECK_MSG|CHECK_PASS|ASSERT FAIL" pi_run.log | head -10
