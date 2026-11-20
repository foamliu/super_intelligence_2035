# Deepread — hpy3y (ruisongs @ 10.129.33.207, mc=82, schematic_netlist)

**Session**: 1792378803577_hpy3y.messages.json (775 KB, 142 msgs, 8 user turns)
**Source host**: 10.129.33.207 (ruisongs)
**Domain**: schematic_netlist (netlist:262; analog:28; schematic:17)

## User turns (verbatim, A-faithful eligibility noted)

- **U#0 @msg0**: "分析一下/proj/drvsa/V0/simdir/verilog/weki/1010_tt/ruisong/dca_m1_reset_sre_1019.x8_9200 和 /proj/drvsa/V0/simdir/verilog/weki/1010_tt/jedec_auto/dca_m1_reset_sre_cai=x_mir=x.x8_9200，为什么SHORT_CONFIG会影响pattern是否pass" — 提需求(分析为什么) 但属"找根因"型分析，且依赖 live /proj simdir 路径。
- **U#1 @msg34**: "真实配置流程为什么没有把 DQ/DQS 的驱动/org/RDLatency 维持到期望状态？" — 追问根因。
- **U#2 @msg55**: "SHORT_CONFIG,现在看波形查明了，带了这个define，有个cm会在reset后被复位，不带就不会，帮忙在代码里面找到对应的逻辑" — **用户已给出根因**(cm reset after reset with define) → 按 A 档规则 ② 不得作 A-faithful 任务说明。
- **U#3 @msg92**: "reset后，这些fuse是会重新broadcast，还是直接复位了？"
- **U#4 @msg114**: "需要分析判断出是现在的pattern: Reset(); Deselectn(.n(400)); 时间给的不够，没完成广播还是其他的什么原因"
- **U#5 @msg125**: "SHORT_CONFIG，应该就是这个define，SHORTSIM带不带没影响"
- **U#6 @msg127**: "你的意思是，不带SHORT_CONFIG，reset后，cm1_fc_RDLatencyTo64，就直接复位，不管等多久也不会拉高？"
- **U#7 @msg129**: "怎么看reset后会不会再广播？"

## Assistant produces (25 editor writes, all grep/find/trace Python over verilog netlists)

grep_short.py, grep_short2.py, grep_plus.py, dump_configdut.py, locate_configdut.py, dump_tasks.py,
find_reset.py, find_cm.py, find_cm2.py, find_cm3.py, dump_cm_driver.py, find_orgx.py, dump_cmcell.py,
dump_cmunit.py, dump_af.py, find_af.py, dump_leaf.py, trace_fs.py, dump_deselect_fuse.py,
trace_fsspread.py, trace_fsspread2.py, find_bcast_src.py, find_bcast_main.py, find_spread_drv.py

All scripts grep/find/trace verilog netlist text under live /proj/drvsa paths to locate `ifdef SHORT_CONFIG
guarded modules, trace reset/broadcast connectivity, and find which CM cell is reset differently.

## A-faithful decision

U#2 gives the root cause (cm reset after reset with define) → A-faithful NOT allowed per rule ②.
Live /proj/drvsa simdir paths not attachable. → **B-grade synthesized**.

## Synthesis (ShortCfgTrace-001, schematic_netlist, L1)

Distill the user's real goal (trace a verilog compile `define's effect through netlist modules to find
reset/broadcast-affected cells) into an offline-verifiable Python tool `shortcfg_trace.py`:

- CLI: `--netlist <v> --define <name> --out <report.md>`
- Find every `ifdef <define> directive (exact name match); `ifndef/`elsif and other-name `ifdef are distractors
- Stack over `if* / `endif to find each guard's matching `endif (block range)
- Within union of matched guard blocks count: guard_count, module_count (+ names), instance_count (u_*),
  wire_count, assign_count, reset_refs (rst_n), broadcast_refs (bcast|broadcast)
- Output markdown top summary key:value + per-guard detail

**Assets**: A=chip_shortcfg_A.v (3 `ifdef SHORT_CONFIG + 2 OTHER_CFG distractors; guard=3 mod=2 inst=3
wire=5 asg=7 rst=11 bcast=6); hidden B=chip_shortcfg_B.v (define=SHORT_CONFIG, 4 guards + 2 OTHER_SIM;
guard=4 mod=3 inst=4 wire=5 asg=8 rst=15 bcast=6, names cm0_x_B/cm1_y_B/cm2_z_B); hidden B2=chip_shortcfg_B2.v
(cross-input, define=FAST_SIM, 3 FAST_SIM guards + 1 SHORT_CONFIG DECOY + 1 OTHER_MODE; guard=3 mod=2 inst=5
wire=4 asg=5 rst=12 bcast=5, names fa0_p_B2/fa1_q_B2). A/B/B2 counts all disjoint → anti-hardcode.

**Reference**: shortcfg_trace_ref.py (stack-based `endif matching, anchored structural regexes).
**check.py**: 16 conditions a-p (zip/py_compile/B-run/B-counts×7/B-module-names/B2-run/B2-guard/B2-module/determinism).
**Self-test**: ref PASS 16/16; 4 negatives (empty/hardcode-A/no-define-filter/no-endif-stack) all FAIL;
§4.9 three-fake (empty/hardcode-A/ref-core-deleted) all FAIL; determinism sha256 identical.
**Gate**: k_rationale == k_check == 16 ✓.
