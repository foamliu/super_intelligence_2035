# Deepread: 1793947227109_1236h — DDR5 LPDDR5 testmode RAST stop selection verification

**Session**: 1793947227109_1236h  
**User**: daiweilu @ hfeg0pjn100 (mc=91)  
**Domain**: verification (digital)  
**Keywords**: netlist:242;verilog:122;cmos:57;analog:17;rtl:7  
**Date**: 2026-11-13  

## User Intent
U#0: "我要验证testmode cm1_ro_IsmRASTstopSel，我的pattern为/proj/ddgoa/.../TM_processmonitor.v，网表为/proj/ddgoa/.../netlist, 要求是在Ism 47/48测量（refresh测量）时，选择用哪一个RAST信号沿作为ISM stop信号送出。如果是2pump，有4个可选，cm1_ro_IsmRASTstopSel<2:0>取值范围为000/001/010/011；如果是3pump，有6个可选，cm1_ro_IsmRASTstopSel<2:0>取值范围为000/001/010/011/100/101。"

U#1 (msg43): "我该看哪几个信号来判断功能是否正确？"
U#2 (msg55): "把这几个信号的路径给我"

## Agent Actions (95 msgs)
1. Explored pattern file TM_processmonitor.v + netlist directory
2. Searched for RAST stop selection signals (grep IsmRASTstopSel, RASTstop, IsmRAST)
3. Found i==47 (all-bank refresh) and i==48 (per-bank refresh) are 3-pump (TM_RHR3PUMP) with j=0..5
4. Read ISMRASTtiming module in netlist (line 543880+): mux selecting stop0..stop5 → RefStop
5. Traced signal chain: cm1_ro_IsmRASTstopSel → I_ISMRASTtiming_0 mux → RefStop → RowControl → ISM measurement
6. Wrote trace_hier.py to parse netlist module hierarchy and find instantiation path
7. Found full hierarchy: WOWTOP.I_C_Top.I_Channel.I_ChanMid.I_Controller.I_RowControl_PN1p76_646.I_ISMRASTtiming_0
8. Identified observable signals: cm1_ro_IsmRASTstopSel, RefStop, RefStart, IsmOutEn, TDQ probe readout

## Key Technical Details
- DDR5 LPDDR5 fuse_1103 netlist (V0_WOWTOP_2026Oct29.172927)
- RAST stop selection: 6-input mux (stop0..stop5) controlled by cm1_ro_IsmRASTstopSel<2:0>
- 2pump: 4 valid values (000-011), 3pump: 6 valid values (000-101)
- Hierarchy depth: 6 levels from WOWTOP to ISMRASTtiming
- Parent module: RowControl (netlist 553477), RefStart/RefStop are its outputs
- Latch: I_CmFsLatchX5L_8 for stopSel

## A-faithful Assessment
QUALIFIED: User gave task (verify testmode) + file paths (pattern + netlist) + configuration spec (2pump/3pump ranges) but did NOT give the netlist parsing algorithm, hierarchy tracing logic, or the specific module instantiation path. Agent had to discover these by reading the netlist.

## Deliverable Assessment
DELIVERABLE = analysis/verification results for private /proj/ddgoa/ files → INFEASIBLE (private project files, not accessible in sandbox) → B档合成

## Synthesized Case
**EDA-Eval-DesignFlow-NetlistHierTracer-001** (verification L1-B, k=16)
- Archetype: verilog-netlist-hierarchy-tracer
- Core task: parse Verilog netlist, extract module definitions + instantiations, trace hierarchy path from root to target
- Key traps: comment stripping (FakeMod in comments), multi-instance same-type paths (per-path cycle prevention), cross-input guard (A names ≠ B names), port connection counting
