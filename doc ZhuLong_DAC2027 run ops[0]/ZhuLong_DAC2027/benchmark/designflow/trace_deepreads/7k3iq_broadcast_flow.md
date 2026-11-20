# Deepread: 7k3iq — broadcast flow in LPDDR5 DDGOA netlist

- session: `1793672902894_7k3iq.messages.json`
- host/user: `hfeg0pkn005` / `thomas1w` (10.129.2.14)
- match_count: 133 (verilog:388 cmos:300 netlist:223 analog:59 drc:42 schematic:24)
- domain: schematic_netlist (shard D)
- 96 turns, 4 real user turns, 43 assistant turns
- grade seed: **A** (U#1 user states goal, no root-cause/fix given) → B-grade synthesized (private 49MB /rundata netlist + writableRoot limits)

## U#1 (the seed)
> `/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.1029/netlist/V0_WOWTOP_2026Oct29.172927/netlist 这个是网表内容，看下broadcast的流程`

## Assistant tool-chain (U#1 → A#24 final)
1. `get_agent_policy_status` + `list_allowed_files` on the netlist path (path is a FILE not dir).
2. `run_commands`: `ls -la` + `wc -l` → netlist ~49MB, ~1M lines.
3. `search_codebase` "broadcast".
4. Creates `/home/thomas1w/inspect_netlist.py` (info + grep helper), `run_approved_command` python-runner → grep "broadcast" → hits in module `AF_PPRAddLatClk` (clock-related, minor).
5. Creates `grep_netlist.py` (case-insensitive multi-pattern) → finds `BroadcastFuseTestBit` die-level fuse test bit + `BroadcastFuseTestBitPre`/`O` variants.
6. Creates `module_map.py` (extract all `module NAME` + line ranges) → top module `WOWTOP` (line 1,035,329).
7. Filters module list for Fuse|Broadcast|CMCenter|Chan → finds `AF_FsAryTmBroadcast` (173657), `AF_FsBroadcastflagInChannel` (67407).
8. Reads `AF_FsBroadcastflagInChannel` (67407): `Out = (Enable & Flagbits) | BroadcastFuseTestBitPre` (aoi21 + inv).
9. Creates `trace_btb.py` (trace BroadcastFuseTestBit per containing module) → maps all occurrences.
10. Creates `trace_bp.py` (trace BroadcastFuseTestBitPre source) → CMCenterR generation.
11. `module_map.py` Chan/CMCenter/PrcUnit → Channel(610806), CMCenterL(409811)/CMCenterR(417375), ChanRight(140941)/ChanLeft(400621)/ChanMid(604428), ChanEdgeR(245041)/ChanEdgeL(382123), CMDqR(70765)/CMDqL, FuseRightTracks(206)/FuseLeftTracks, ControllerM5(557929)→TclkTdqCtrl(440311).
12. Reads CMCenterR region (440330-440475, 420190-420240): `aoi21 I691` `net30=~((CMCenterRBCFlagEn & CMCenterRBCFlagbit)|BroadcastFuseTestBitPreleft)`, `nor2 I693` `net28=~(BroadcastFuseTestBitPreRight|BroadcastFuseTestBit_cmcenterright)`.
13. Final synthesis (A#24): 5-section report — (1) top module & broadcast location; (2) generation/merge at CM center; (3) propagation in DQ slice + leaf injection (AF_FsBroadcastflagInChannel OR-merge → FuseRightTracks bufLx16 → PrcUnitChanrightm5fuse.SignalLeft); (4) cross-die edge buffers (ChanEdgeR/L bufLx24); (5) readback ControllerM5→TclkTdqCtrl (.BroadcastFuseTestBit(BCDataBankOutForCPtest)).

## Subsequent turns (not used for the case seed, but confirm domain depth)
- U#2 "CCR的电路在哪里" → CCR = column redundancy/column-copy repair; maps _CCR_fbcc spare columns, CCRtop_DDGOA_rev controller, CompRdCCRUnitV2 CP compare.
- U#3 "CCRtop_DDGOA_rev 这个模块是做什么的" → 5 sub-modules (LvlShftYSdecUnit_ccrgating, ColRed_DDGOA_rev, RCol987EnC_rev, RedCPYsDec_rev, ColAddDly_DDGOA).
- U#4 "结合电路详细介绍一下是怎么实现的" → gate-level: ColRedComp_rev XNOR compare (CA[8:6] vs Fn[7:5]), FzCPSelX16 encode → RedCP/RCA87/CCRgating.

## Synthesis decision
- Real netlist: 49MB / ~1M lines on private `/rundata` (not reproducible in SUT sandbox; writableRoot limits blocked direct edits in the trace).
- → **B-grade synthesized**: self-contained compact gate-level netlist (`netlist_A.v`, ~200 lines) reproducing the broadcast flow structure (WOWTOP→Channel→CMCenterR aoi21 gen → ChanRight→CMDqR→AF_FsBroadcastflagInChannel leaf OR → FuseRightTracks bufLx16 → PrcUnitChanrightm5fuse.SignalLeft; ChanEdgeR/L bufLx24; ControllerM5→TclkTdqCtrl readback).
- Deliverable = `broadcast_analyzer.py <netlist.v> <report.json>`: parses netlist, emits structured JSON {summary{top_module,broadcast_signal,total_modules,occ}, generation{module,gate_type,output_net}, leaf_injection{module,gate_type,inputs,output_signal}, consumer{module,port}, readback{controller_module,tdq_module,alias_signal}}.
- Hidden `netlist_B.v` structurally different: DDR5TOP / BroadcastScanTestBit / ScanCenterL oai21 / AF_ScanflagInject and2 (AND-merge vs OR) / ScanFuseColumn.ScanIn / DftController→TdqScanCtrl/CPtestDataOut. Anti-hardcode: A/B namespaces fully disjoint.
- check.py: 11 conditions (a-k); ref PASS 11/11; 3 negatives + §4.9 3 fakes all FAIL; NEG_RC=0.

## case_id
`EDA-Eval-DesignFlow-NetlistBroadcastFlow-001` (schematic_netlist, B-grade synthesized, L2, k=11)
