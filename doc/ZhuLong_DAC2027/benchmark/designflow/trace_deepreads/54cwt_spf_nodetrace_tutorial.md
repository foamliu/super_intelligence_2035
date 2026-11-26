# Deepread: 1795568047471_54cwt (xxchen @ hfeg0pkn003, mc383, physical_verify)

## Trace
- user: xxchen, host: hfeg0pkn003, session 1795568047471_54cwt.messages.json, 383 msgs
- first user msg: `整理下traceSPFresNode.py这个脚本的运行原理，使用html格式编写成一个教程，类似ppt的格式。`
- real intent: document the working principles of an EXISTING real EDA tool `traceSPFresNode.py`
  (a StarRC DSPF resistor-network node tracer) into an HTML tutorial (PPT-style).
- assistant: read the script (1306 lines), ran `--selftest`, read sample report
  `temp_starcmp/traceNet_ideal_IO.rep`, produced HTML tutorial.

## The real tool (fetched from .75:/home/xxchen/workspace/small_tool/spf_Analysis/traceSPFresNode.py, 50608 B / 1306 lines)
- purpose: trace the resistor network of ONE target node in a StarRC DSPF netlist
  (*|NET sections). Designed for huge files (50GB+): streaming parse to locate the
  target's net, then seek+parse only that net.
- core algorithm:
  - phase1: streaming scan for the *|NET section containing the target node
  - phase2: parse that net (*|P ports, *|I pins, R resistors with $lvl=), build graph
  - path mode (default): Dijkstra min-resistance path target -> net head; ties -> fewer
    hops; dangling degree-1 wire ends (non-pin/non-port) on path excluded
  - full mode: whole connected network reachable from target
  - ideal-short mode (--ideal-short): contract resistors <= OHM (default 0.001) into
    [merged:I n=K] nodes, trace only real series resistors
  - *LAYER_MAP: $lvl= number -> layer name annotation
  - report format: text .rep with summary + path resistors + path nodes + nearest
    real resistors through ideal shorts + dangling ends
- CLI: `traceSPFresNode.py <spf> <target> [-o rep] [--mode path|full] [--ideal-short [OHM]] [--selftest]`
- --selftest: 19 checks (path small net, stub on path, ideal-short merged/contracted/
  kept/path/nearest, lmap entry/plain/header/not-entry, lvl present/absent/non-num,
  lname mapped/unmapped/no-lvl) -> OK

## Case adaptation (EDA-Eval-DesignFlow-SpfNodeTrace-001)
- The real user intent (document the existing tool) is a one-off analysis task that
  does NOT fit the §4 hidden-B + subprocess-on-candidate model (candidate would
  document the visible A script; no general script runs on hidden B).
- This case adapts the real tool's CORE FUNCTIONALITY (DSPF *|NET parse + resistor
  graph + Dijkstra min-resistance path + *LAYER_MAP annotation) into a
  "write trace_spf_node.py" implementation task -- a genuine EDA-automation task with
  authentic reference (the real tool, fetched from xxchen's workspace). Scoped to
  small in-memory files (path/full modes + layer map); ideal-short streaming mode
  out of scope. trace_source.real_task_summary records the real intent transparently.
- A (visible): fixture_A.dspf -- simple 3-resistor series net (vdd_a!) + side pin,
  + a 2nd net (gnd_a!). target XI_A.M1:SRC -> path 50.0 ohm / 4 nodes / R1,R2,R3.
- B (hidden): fixture_B.dspf -- DIFFERENT design (QA_DESIGN_B), two nets with
  PARALLEL BRANCHES (forces real Dijkstra, not full-list):
  - vcc_core! (7 resistors, 2 branches): target XI_TOP.U1:SRC -> min path R1+R2+R3=35.0
    (alt branch R1+R4+R5+R6=311.0); full reachable = 7 nodes/7 resistors
  - sense_ln! (4 resistors, 2 branches): target XI_BOT.S1:SRC -> min path R20+R21+R22=31.0
    (alt R20+R23=104.0)
- check.py: 12 conditions (py_compile / runs / status OK / matched_net / resistor count /
  total resistance / node topology / resistor names / layer annotation / full node count /
  target2 generality / not-found exit). Ground-truth values verified against reference
  solution (run on B), embedded as numeric/structural assertions (not text similarity).
- negatives (§4.9 trio): empty->c3, print-expected(hardcode target1)->c10, core-deleted
  (no Dijkstra, full-list)->c5. 3-distinct first-fails verified.
- judge_layers=[L0,L1] (mock; pure Python, no EDA tool needed).

## Why this trace (selection note)
- xxchen is the established r1215/r1216 lead; 1x17n was used by r1216 (TopPinLabelExtract).
- 54cwt is the only remaining xxchen session whose core subject (traceSPFresNode.py) is a
  GENERAL-purpose EDA tool whose functionality adapts cleanly to a §4-compliant
  write-a-general-script case. The other 3 (u03z0/qikhb/4bz6d) are QA-pattern-GUI
  schematic code-modifications (specific per-function edits, not general scripts) which
  do not fit the §4 hidden-B input model; parked for future consideration.
