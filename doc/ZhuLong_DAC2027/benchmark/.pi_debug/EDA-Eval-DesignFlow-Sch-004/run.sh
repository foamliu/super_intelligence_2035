#!/bin/bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Sch-004
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0
PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- Implement the Tcl proc 'netlist_fanout_floating_audit' per the prompt. It
  takes ONE string argument (netlist_text) and returns a flat Tcl dict with
  EXACTLY these 10 keys in order:
  total_nets total_connections floating_nets floating_count power_ground_nets
  power_ground_count multi_connect_count max_fanout_net max_fanout_count verdict
- You have the eda_flow MCP connected (open_session / run_code / close_session).
- Verify your implementation on the .75 Empyrean WaveView Tcl sandbox:
  1. open_session(task_id=\"BENCH-SCH4\", eval_id=\"20261030-sch4\", user=\"bench_sch4\", sample=\"0\") to get a workdir.
  2. run_code with lang=\"tcl\" host=\"waveview\" and workdir=<the workdir>. In ONE Tcl code
     block:
     - define your netlist_fanout_floating_audit proc,
     - then paste and run this checker EXACTLY (it builds the netlist fixtures
       inline and asserts on the returned dict; no external files needed --
       pure text analysis):
     ---CHECKER START---
$(cat checker.tcl)
     ---CHECKER END---
     - at the end of the code block, call:
         set r [check netlist_fanout_floating_audit]; puts \"RESULT:\$r\"; if {\$r eq \"ALL_ASSERTS_PASS\"} { puts \"DESIGN_FLOW_VERDICT=PASS\" } else { puts \"DESIGN_FLOW_VERDICT=FAIL\" }
  3. close_session(workdir) with keep=false to clean up.
- At the very end of your response, print the line 'DESIGN_FLOW_VERDICT=<PASS or FAIL>'
  and the RESULT line from the sandbox run, and state PASS if DESIGN_FLOW_VERDICT==PASS.
- NOTE: the Empyrean WaveView Tcl regexp supports POSIX classes like
  [[:space:]], [[:alnum:]_], [[:digit:]]; do NOT rely on \\b / \\s / \\d / \\w
  Perl classes. Use Tcl 'split' on newline, 'string map' to drop \\r,
  'string trim', 'string tolower', 'string match' for globs,
  'string match *=* \$tok' to detect params, 'lsort -dictionary' for lex
  sorting + lex-smallest-tie-break, 'array'/'info exists' for the connection
  map and .global set, 'dict create' for the returned dict in exact key order.
- Key real traps in this task (a naive impl fails these -- the checker
  asserts the correct behavior):
  (1) PARAM EXCLUSION: tokens with '=' are NOT nodes and NOT the subname.
      'X1 a b INV w=1u l=1u' -> nodes {a b} (count 2), sub=INV. Naive 'all
      tokens after name are nodes' -> counts w/l/INV -> wrong counts.
  (2) SUBNAME = LAST non-'=' token (excluded from nodes). Naive 'all non-'='
      tokens are nodes' -> counts the subname as a node -> inflated counts.
  (3) POWER/GROUND NAME RULE: case-insensitive, strip a single trailing '!',
      then glob match gnd*/vdd*/vss*/vcc*/avdd*/avss*/dvdd*/dvss*. 'gnd!',
      'AVDD', 'vss0' are ALL power/ground. A 1-connection power/ground net is
      NOT floating. Naive exact-case 'gnd'/'vdd' -> misses these.
  (4) NODE '0' is ALWAYS ground (SPICE global ground). A '0' with 1
      connection is power/ground, NOT floating.
  (5) '.global' DECLARED net is power/ground-class even if its name does NOT
      match the globs. A '.global vddx' with 1 connection is power/ground, NOT
      floating. Naive name-only -> false floating.
  (6) '+' CONTINUATION JOIN: an instance split across '+' lines must be
      joined before tokenizing. Naive per-line -> wrong subname / node set.
  (7) DUPLICATE NODE IN ONE INSTANCE counts as 2 connections: 'X1 a a INV'
      -> net 'a' has count 2 (NOT 1). Naive per-instance dedup -> undercounts.
  (8) COMMENT ('*' col1) / BLANK lines are skipped AND BREAK a pending '+'
      continuation. A '+' line after a comment is ignored, not joined.
  (9) MAX_FANOUT TIE-BREAK: on a tie for highest count, the LEXICOGRAPHICALLY
      SMALLEST net wins (use lsort -dictionary order and keep strictly-greater
      updates). Naive first-seen -> wrong name.
  (10) LEX SORT floating_nets and power_ground_nets (lsort -dictionary).
  (11) verdict: 'clean'/'floating'/'sparse_power'/'both' per the truth table
       in the prompt (sparse_power = some power/ground net with <2 conns).
       Naive 'only check floating' -> reports 'floating' instead of 'both'."
echo "=== pi-SUT Sch-004 start $(date) ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date) ==="
