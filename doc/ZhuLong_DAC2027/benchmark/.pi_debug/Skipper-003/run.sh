#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/Skipper-003
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'uvs_regr_scoreboard_aggregate' per the prompt. It takes two
  string arguments (scoreboard_text, test_list_text) and returns a flat Tcl dict with
  EXACTLY these 12 keys in order:
  tags_scanned total_tests_run passed failed skipped timeout pending
  flaky_tests missing_tests duplicate_runs pass_rate overall_verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean Skipper Tcl sandbox:
  1. open_session(task_id=\"BENCH-SK3\", eval_id=\"20261030-sk3\", user=\"bench_sk3\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"skipper\" and workdir=<the workdir>. IMPORTANT: the
     skipper interpreter does NOT chdir into the workdir, so when sourcing files use the
     ABSOLUTE workdir path. In ONE Tcl code block:
     - define your uvs_regr_scoreboard_aggregate proc,
     - then paste and run this checker EXACTLY (it builds the scoreboard + test_list
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check uvs_regr_scoreboard_aggregate]; puts \"RESULT:\$r\"; if {\$r eq \"CHECK_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean Skipper Tcl regexp supports POSIX classes like [[:space:]],
  [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes. Use Tcl
  'split' on newline, 'string map' to drop \\r, 'string trim', 'regexp --' with POSIX
  classes, 'dict' for the per-(test,tag) last-wins map and the rawP/rawFail/declared
  sets, 'lsort' to sort flaky_tests/missing_tests, 'switch -- \$code' for outcome
  counting. Keep your solution minimal.
- Key real traps in this task (a naive impl fails these -- the checker asserts the
  correct behavior):
  (1) FLAKY uses RAW rows (before dedup): a testname with at least one 'P' row AND at
      least one 'F' or 'T' row ANYWHERE in the scoreboard is flaky. A re-run that flips
      P->F inside ONE tag IS flaky. Do NOT compute flaky per-tag-only (misses cross-tag)
      and do NOT compute it after last-wins dedup (misses the rerun flip).
  (2) DUPLICATE RERUN: per (testname, tag) keep the LAST outcome row; an earlier row for
      the same (testname, tag) is a duplicate -> increment duplicate_runs. The
      passed/failed/skipped/timeout/pending counts are over these LAST-WINS unique pairs,
      NOT over raw rows. total_tests_run IS the raw row count (includes duplicates).
  (3) pass_rate = passed*100/(passed+failed+timeout), INTEGER division; the denominator
      EXCLUDES skipped and pending. pass/total (including skip+pending) is WRONG.
  (4) missing_tests: a declared test (from test_list_text, skipping '#' lines and blanks,
      name = first whitespace token) that has NO row in ANY tag. Sorted. Not silently
      dropped.
  (5) overall_verdict priority FAIL > INCOMPLETE > PASS: FAIL if failed>0 or timeout>0
      (pass>0 does NOT rescue it); else INCOMPLETE if missing non-empty or pending>0;
      else PASS. A 100% pass_rate with a missing test is INCOMPLETE, NOT PASS.
  (6) outcome codes are single letters: P pass, F fail, S skipped, T timeout, . pending.
      'S' is NOT a failure; '.' is NOT a failure (and NOT in the pass_rate denominator);
      'T' (timeout) IS a scoring failure.
  (7) scoreboard header line is exactly '=== <tag> ===' (three equals, spaces, tag, spaces,
      three equals); a row is exactly '<testname> <one outcome letter>'. Any other
      non-empty line is ignored."
echo "=== pi-SUT Skipper-003 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ===" >> pi_run.log
echo "pi exit=$ec"
echo "--- result lines ---"
grep -E "DESIGN_FLOW_VERDICT|CHECK_RESULT|CHECK_ERROR|ASSERT FAIL|CHECK_PASS|RESULT:" pi_run.log | head -12
