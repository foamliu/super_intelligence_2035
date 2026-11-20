# trace_deepread: 1794461397387_7ehdd (chengwen@hfeg0pkn003, mc=37, schematic_netlist)

## trace_source
- session_file: 1794461397387_7ehdd.messages.json
- user: chengwen, host: hfeg0pkn003 (10.129.2.12), match_count: 37
- keywords: analog:1041;netlist:97;drc:96;cmos:51;lvs:33;schematic:9;hspice:6;aether:3
- 46 msgs, 411KB, act mode, single substantive task (2 user turns, same intent restated)

## user intent (verbatim)
- U#0: `/proj/drcpa/V0/workdir/chengwen/simulation/drcpa_top_DDR5TOP_config_pwrup_trans_ALPS/netlist.presim 这是netlist，帮我整理一下vdleq的cell name和hierarchy`
- U#4 (restated): `...帮我整理一下用到vdleq的cell name和hierarchy` (clarified: cells that USE vdleq)

## assistant workflow (produce-task, python-runner)
1. msg[7] write analyze_vdleq.py (v1): parse .SUBCKT, search vdleq, build hierarchy. Run → 37.6万行/6929 subckt/173 vdleq cells, but top-level wrong (defined-but-uninstantiated subckts counted as top).
2. msg[11]→v2: find real top from file-scope instances, write full report to vdleq_report.txt (3044 lines). Found top=PERI0.
3. msg[19]→v3: **TWO BUG FIXES (the teeth)**:
   - **Bug 1 port-continuation**: `.SUBCKT` port list spans multiple `+` lines; vdleq port on continuation line misjudged as body net → must handle `+` continuation in port parsing.
   - **Bug 2 master-with-params**: instance line `XI_... m=4` → master misjudged as `m=4` (last token) → must skip `=param` tokens when extracting master (walk reversed, first token without `=`).
4. msg[27] v3 result: 173 cells (143 port+body, 29 body-only, 1 port-only=R_RasBnkLogic), 265 hierarchy paths, roots=PERI0 + Array6G_T.
5. msg[41-43] verify top-level vdleq port names.
6. msg[45] **final accepted report** (act mode, no reject, implicit accept):
   - Overview: 376361 lines, 6929 subckts, 173 vdleq cells, classification 143/29/1, 265 hierarchy paths
   - top_net=`vdleq!` (global `!` suffix), 2 roots: XI_PERI0 (port inh_vdleq ← vdleq!), XI_Array6G_T_0 m=4 (port inh_vdleq ← vdleq!)
   - case-insensitive: vdleq/Vdleq/VdlEq/VDLEQ variants
   - common port names: inh_vdleq, VdlEq2Vcc(In/Out/Top), VdlEqActDis(In/Out/Top), Viso2Vdleq(In/Out/Top), VdleqRefTop, VdleqActEn(i/o), VdleqActPrime(i/o)
   - hierarchy tree: 2 branches (PERI0 ~200 paths, Array6G_T ~60 paths)

## gold standard (for B-grade reframe)
- deliverable = structured report: overview stats (total_lines, total_subckts, signal_cell_count, classification counts, hierarchy_path_count) + top_net + roots + signal_cells + hierarchy_paths
- parsing requirements (the teeth):
  1. port-continuation `+` lines in `.SUBCKT` header → ports on continuation must be counted as ports not body
  2. instance master extraction → skip `=param` tokens (m=4, w=2...), master = last non-param token
  3. case-insensitive signal matching (vdleq/Vdleq/VdlEq/VDLEQ)
  4. file-scope top instances = real roots (not defined-but-uninstantiated subckts)
  5. classification: port_and_body / body_only / port_only

## B-grade synthesized reframe plan
- original netlist 376K lines private (chengwen /proj path unreachable) → synthesize small SPICE netlist A/B with same structural features
- signal: A=vdleq, B=vcore (different, anti-hardcode); subckt names/net names/structure all differ
- A visible (assets), B hidden (reference, check runs on B)
- candidate writes analyze_signal.py: read netlist + target signal → JSON report
- check.py: embedded independent oracle + subprocess run candidate on B + ~18 conditions
- teeth embedded in B: port-continuation cell, m=N param instance, mixed-case signal variant, port-only/body-only/both/decoy cells
