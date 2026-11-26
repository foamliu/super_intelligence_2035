# szdav — StrongARM Slicer Sizing Optimization (analog_context, B-grade synthesized, L2)

## trace_source
- user: jiangbaol · host: hfeg0pkn003 (10.129.2.12) · session: 1791954407908_szdav · mc=56
- keywords: netlist:211;hspice:128;schematic:104;synopsys:86;cmos:21;verilog:20;skipper:12;analog:12
- 192 msgs, model GLM-5.2

## user intent (2 natural produce-task turns)
- **U0** (repeated 5× — user resent): `004_onlySlicer_delay_dejoa.sp` (block TB_DqIb_strongarm_pmos, FineSim testbench). Tune 8 params — pmoswidth/pmosfinger/nmoswidth/nmosfinger/itailwidth/itailwidthfinger/inwidth/inwidthfinger — so `Cur_slicer_latch_avg` at **TT_1V_45 corner** ≤ 380 uA (max constraint), and `slicer2nd_dly_r0` / `slicer2nd_dly_r1` minimized (delay objective). Work files → SA_opt/.
- **U151**: second testbench `004_onlySlicer_delay_dejoa_test_cmdm.sp` (block DqIb_strongarm_pmos), optimize only pmoswidth/finger + nmoswidth/finger: minimize `cur_slicer_latch_avg`, ensure `LDFEdataErn` rises to 240 mV after 2.04 ns, maximize |`slicer_out`|, minimize overall delay `CK2Q_DFE_T_F`; give sim-iterated sizes.

## agent tool chain (real work)
1. read_files `.sp` + setup files; search_codebase for the 8 width params.
2. **param→device mapping** (in `netlist_without_1st_reset_130n`): `pmoswidth→XMMP0/XMM17` (stage-2 cross-coupled PMOS latch), `nmoswidth→XMMN5/XMMN23`, `itailwidth→tail`, `inwidth→input pair`.
3. read 5-corner file `DEJOA_SA_5corner.sp` → TT_1V_45 = alter #1/#2 (temp=45).
4. built LSF sweep harness: `sa_submit.sh` (bsub finesim, sed-patch 8 params into .sp), `sa_collect.sh`, `sa_wait.sh`, `sa_inspect.sh`.
5. validated metric parser vs known-good baseline `without_1st_reset_130n.mt0.csv` → **baseline @ TT_1V_45: cur_slicer_latch_avg=350.05 uA, dly_r0=46.11 ps, dly_r1=45.12 ps**.
6. submitted baseline + 5 candidate sweeps (001–006: pmos+, itail+, in+, nmos-den variants).
7. **BLOCKED**: FineSim FSPRO license daemon down site-wide — every new `.tran` job fails at license checkout (`no valid license(-1)`), `lmstat` returns no FSPRO tokens. Could not run new sims.
8. delivered ready-to-run SA_opt workspace (scripts + candidate configs + README + baseline measured data); did NOT fabricate sim-verified sizes.
9. U151: same blocker; provided device mapping + baseline param values (pmoswidth=24u/finger=4, nmoswidth=18u/finger=3) + setup, no sim-verified result.

## why B-grade synthesized
- real assets under `/proj/dscqa/V0_LP6/...` are **permission-denied** to e0031982 (private project tree). Only the conversation is captured.
- → synthesize A/B testbench + netlist + 5-corner file + baseline mt0.csv replicating the real structure (8-param StrongARM slicer, TT_1V_45 corner, cur≤380 uA, dly_r0/r1 objective, bsub/finesim sweep harness).

## case design (SaSlicerSizingPlan-001)
- candidate writes `sa_sizing_plan.py` (CLI): parse testbench `.sp` (8 `.param` defaults) + netlist (param→device-instance mapping) + corner file (corner→temp/vdd/model, identify TT corner by target vdd/temp/model) + baseline `mt0.csv` (extract cur_slicer_latch_avg / slicer2nd_dly_r0 / slicer2nd_dly_r1 at TT corner); emit `mapping.json` / `corner_map.json` / `baseline_metrics.json` / `sweep_plan.json` (≥3 candidate param sets) / `submit.sh` (bsub finesim, 8 sed patches, LSF source).
- A: 5 corners, TT_1V_45 @ idx 0, baseline cur=350.05 uA, cur_limit=380 uA, instances XMMP0/XMM17/XMMN5/XMMN23/XITAIL0/XIN0/XIN1.
- hidden B: 7 corners, TT_1V_27 @ idx 3, baseline cur=395.50 uA, cur_limit=420 uA, instances XPP0/XPP9/XNN3/XNN18/XTAIL2/XIP0/XIP5 (every dimension different → anti-hardcode).
- 14 conditions a–n: zip completeness / py_compile / subprocess B / 8-param mapping uses B instances / TT corner idx=3 / baseline cur parsed (B value) / dly_r0+r1 parsed / sweep ≥3 sets all 8 params / ≥1 width reduced / submit.sh bsub+finesim+8 sed+LSF / submit.sh output dir / anti-hardcode cross-input (B names+values, not A) / 3-seed determinism / corner identified by temp/vdd/model parse not hardcoded idx (swapped-corner robustness).
