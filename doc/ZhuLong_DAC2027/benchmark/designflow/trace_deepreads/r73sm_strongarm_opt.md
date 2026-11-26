# Deepread: 1794383471111_r73sm (jiangbaol @ hfeg0pkn001 / 10.129.2.10)

**Source**: 11/12 fresh-window rescan (mtime ≥ 11/10) of top-5 spice hosts — 11-05 rescan command
**Slug**: 1794383471111_r73sm | **spice grep count**: 586 | **msgs**: 394 | **tools**: 196
**Domain**: spice_sim | **Tier**: L2-L3 (multi-script sweep + finesim real-sim + FOM analysis)

## User intent (trace-faithful)
- U0: "我现在需要优化strongarm电路，应该从哪里开始"
- U1: Library=dejoa_slicer_liang, Cell=DqIb_strongarm_pmos, View=schematic; model incFile=/proj/shdc/models/G4B/model_local/G4B_CIP_Model_L6_v0d5_t07/incFile_lp; goal=提高速度/比较时间 + 降低功耗
- U2: Provides switch_close/switch_open subckts (ideal switch model for bench)
- U3: bench=/proj/dscqa/V0_LP6/simdir/finesim/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa.sp; tool=finesim; clk(DqSanp)=3200MHz
- U4/U5: FineSimPro $DATA1 measurement results (cur_slicer_avg, cur_slicer_latch_avg, ck2q_dfe_t_f, ck2q_dfe_b_f, slicer1st_dly_f0, slicer1st_dly...)

## Assistant work (196 tool calls)
- 71 editor (script creation), 63 run_approved_command (finesim runs + sweeps), 24 read_files, 18 RAG_MCP search_apis (pyAether API search), 2 run_commands
- Key scripts created:
  - `strongarm_sweep.sp` — parameterized sweep netlist
  - `run_sweep.py`, `run_rst_sweep.py`, `run_final_combo.py` — sweep runners
  - `make_nmos_sweep.py`, `make_mn18_sweep.py` — sweep netlist generators (NMOS sizing)
  - `analyze_strongarm.py`, `analyze_nmos_fom.py`, `analyze_mp23.py`, `final_fom_analysis3u.py` — FOM analysis (speed vs power)
  - `try_finesim.py` — finesim invocation probe
  - `strongarm_plan.py`, `strongarm_netlist_insights.txt` — optimization plan/notes
  - `add_final_meas.py` — .MEASURE statement injection
  - `sr_latch_debug.py` — SR latch debug
  - `find_sweep_files.py`, `inspect_ldlib.py`, `prepare_rst_sweep.py`

## Case design (next round synthesis)
- **A-faithful task**: Given strongarm comparator netlist (DqIb_strongarm_pmos) + testbench (finesim, clk=3200MHz) + model incFile, run NMOS sizing + RST timing sweeps to optimize FOM (minimize comparison delay × power). Deliver: sweep report (JSON) with best FOM point, sweep grid, and per-point measurements.
- **Hidden B**: Different sizing grid / different corner / different FOM weighting (e.g., add latch current to FOM)
- **check.py (L2, k≥8)**: zip+py_compile / B runs finesim on hidden netlist / report.json schema / sweep grid completeness / FOM values sane / best-point identified / .MEASURE keys match SPEC / cross-validation A≠B / fallback parse
- **Negative**: naive_stub (print fixed report), constant_FOM (all points same FOM), partial_sweep (only 1 point)
- **Note**: finesim is the simulator (not hspice); /proj paths need sanitization for sandbox (copy netlist into assets)

## Status
- **Claimed** r409 (ledger_B). DEBT: 1 deepread → next round MUST synthesize + deliver case.
