#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-008
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_via_enclosure_audit' per the prompt. It takes ONE
  string argument (report_text) and returns a flat Tcl dict with EXACTLY
  these 10 keys in order:
  total_via_types total_lines pass_count warn_count fail_count
  skip_count worst_via min_enclosure mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER8\", eval_id=\"20261030-aether8\", user=\"bench_aether8\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_via_enclosure_audit proc,
     - then paste and run this checker EXACTLY (it builds the via-enclosure
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_via_enclosure_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'enc_bot=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare float SUMMARY fields NUMERICALLY (expr ==), NOT with
  string equal (so '0.080' equals '0.08'). Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) status CASE-INSENSITIVE: 'fail'/'FAIL'/'Fail' all match FAIL.
  (2) DUPLICATE (name,cut) pair: LAST occurrence WINS (replace enc_bot/enc_top/req/status,
      not sum, not first-wins). Counts ONCE in total_lines.
  (3) status ABSENT -> infer FAIL if (enc_bot<req OR enc_top<req) else PASS (NEVER WARN/SKIP).
  (4) enc == req -> PASS (inclusive). FAIL only strict <.
  (5) missing req= -> default 0.0 (always PASS).
  (6) missing enc_bot/enc_top= -> default 0.0 (can FAIL if req>0; included in min_enclosure as 0.0).
  (7) min_enclosure/worst_via over NON-SKIP lines ONLY, line enclosure = min(enc_bot,enc_top).
      SKIP excluded even if its enclosure is the file min. No non-SKIP -> min_enclosure=-1.0, worst_via=\"\".
  (8) worst_via tie at min_enclosure -> lexicographically SMALLEST via name
      (lsort -dictionary, numeric-aware: 'via2' < 'via10').
  (9) mismatched_summary: vias_checked/violations/warns/skipped INTEGER equality;
      min_enclosure NUMERIC equality (expr ==, so '0.080' == 0.08); worst_via STRING
      equality. ABSENT SUMMARY fields NOT reported. Empty list if no SUMMARY.
      Computed: vias_checked=total_lines, violations=fail_count, warns=warn_count,
      skipped=skip_count.
  (10) verdict priority: fail_count>0 -> FAIL (TOP) > (mismatched_summary non-empty
       OR no SUMMARY) -> INCOMPLETE > PASS.
  bottom / top / count are red herrings; ignore them in all computed values.
  All output lists lex-sorted with lsort -dictionary."
echo "=== pi-SUT Aether-008 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
