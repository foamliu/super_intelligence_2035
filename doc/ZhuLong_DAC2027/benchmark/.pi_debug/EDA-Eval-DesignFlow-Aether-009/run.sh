#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-009
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
CHECKER="$(cat checker.tcl)"
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'layout_routing_audit' per the prompt. It takes ONE
  string argument (routing_text) and returns a flat Tcl dict with EXACTLY
  these 12 keys in order:
  total_nets routed_count partial_count unrouted_count skipped_count
  single_segment_nets missing_via_nets max_segments max_segment_net
  layers_used mismatched_summary verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-AETHER9\", eval_id=\"20261030-aether9\", user=\"bench_aether9\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your layout_routing_audit proc,
     - then paste and run this checker EXACTLY (it builds the routing
       fixtures inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
${CHECKER}
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check layout_routing_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [^[:space:]]; do NOT rely on \\b / \\s / \\d / \\w Perl classes.
  Use Tcl 'split' on newline, 'string trim', 'string match' globs (e.g.
  'segments=*'), 'lsort -dictionary' for lexicographic sorting + tie-breaks,
  'array'/'info exists' for sets, 'dict create' for the returned dict in exact
  key order. Compare SUMMARY fields NUMERICALLY (expr ==) where ints/floats,
  NOT with string equal. Avoid lassign if unsure; use lindex.
- Key real traps (a naive impl fails these -- the checker asserts correct behavior):
  (1) status CASE-INSENSITIVE: 'routed'/'ROUTED'/'Routed' all match ROUTED.
  (2) DUPLICATE net name: LAST occurrence WINS (replace segments/vias/layers/status,
      not sum, not first-wins). Counts ONCE in total_nets.
  (3) status ABSENT -> infer from segments: 0->UNROUTED, 1->PARTIAL, >=2->ROUTED
      (NEVER SKIPPED).
  (4) missing_via_nets = layer_count>=2 AND vias==0 (single-layer 0-via is FINE,
      not listed; naive flags all 0-via nets or ignores layer count).
  (5) layers list dedup + empty handling: 'M1,M2,M1' -> {M1,M2} (2 layers);
      'layers=' empty -> 0 layers. layers_used is the UNION over ALL nets.
  (6) single_segment_nets = segments==1 REGARDLESS of status (a watchlist; a net
      with status=routed but segments==1 is STILL listed; it is NOT a FAIL trigger).
  (7) max_segments / max_segment_net over NON-SKIP nets ONLY. SKIP excluded even
      if its segment count is the file max. No non-SKIP -> max_segments=-1, max_segment_net=\"\".
  (8) max_segment_net tie at max_segments -> lexicographically SMALLEST net name
      (lsort -dictionary, numeric-aware: 'via2' < 'via10').
  (9) mismatched_summary: nets_checked/routed/unrouted/missing_vias INTEGER equality;
      max_segments NUMERIC equality (expr ==); max_segment_net STRING equality.
      ABSENT SUMMARY fields NOT reported. Empty list if no SUMMARY.
      Computed: nets_checked=total_nets, routed=routed_count, unrouted=unrouted_count,
      missing_vias=[llength missing_via_nets].
  (10) verdict priority: unrouted_count>0 OR missing_via_nets non-empty -> FAIL (TOP)
       > (mismatched_summary non-empty OR no SUMMARY) -> INCOMPLETE > PASS.
       partial_count and single_segment_nets do NOT trigger FAIL (watchlists only).
  All output lists lex-sorted with lsort -dictionary."
echo "=== pi-SUT Aether-009 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
