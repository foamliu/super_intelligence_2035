# Deepread: 11voz — joeyl CML WCKTOP 5-corner tuning (r995 peek)

**Session**: 1794893672653_11voz.messages.json · joeyl @ hfeg0plg74 (10.129.8.112) · mc=116 · 794KB · 245 msgs / 2 user text
**Scan keywords**: netlist:272;hspice:243;pdk:223;synopsys:91;opamp:69;aether:45;binary:30;transistor:21;schematic:14
**Domain**: spice_sim (characterization-adjacent: circuit tuning via HSPICE/FineSim)

## User intent (U[0], trace-faithful)
> `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/4_WCKTOP/2_TRAN.sp` 这里是WCKTOP的testbench，我想请你帮忙调节前三级的cml电路以能够在5corner下都能尽可能实现在高频下的放大功能（底线是17.6G的datarate时，对应的8.8G vdb(outn,outp)＞1，最好能摸到25.2G）。 你可以自由调节电阻length，bias管，输入管的width和finger，考虑到高频，我们可能还需要调节第二级中间的有源电感尺寸。 我们在调节时，应该进行综合的权衡，首先应尽量让静态的bias与输入管均在饱和区，则此时若输入swing不够就有许多可能，比如bw不够，电流不够或电阻不够

**U[1]**: 请用中文总结

## Agent actions
- run_approved_command: 60 (FineSim simulations)
- editor: 45 (edited .sp testbench)
- read_files: 13

## Resource accessibility (SUT sandbox = .75)
- FineSim: ✓ available at /apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim
- Model file `/proj/m2701/V0_DDR4/model/current/model.sp`: ✗ NOT mounted on .75
- Testbench `/rundata/m2701/.../2_TRAN.sp`: ✗ permission denied via SSH (e0031982 identity)
- Option includes `/proj/drjpa/...`: ✗ NOT mounted on .75

## Reframe assessment
- **L2/L3 (真跑 FineSim)**: NOT feasible — model files + option includes not accessible on .75 SUT sandbox; .sp file permission-denied via SSH (must extract from session messages)
- **L1 produce reframe (viable)**: candidate produces `cml_tuner.py` that parses .sp, identifies 3 CML stages, applies parametric tuning (W/L/finger adjustments per stage + active inductor sizing), outputs tuned .sp + corner analysis report. check() verifies output structure (parsed stages, param deltas, .sp syntax preserved, report completeness) — no simulation needed.
  - **Concern**: user intent is "tune and VERIFY via sim", not just "analyze and output params". L1 reframe loses the verify essence. But per 11-15 order, analysis-only is NO LONGER weak.
  - **Feasibility**: .sp content extractable from session read_files tool_results (agent read the file). CML subckt definitions likely inline in .sp (netlist:272 keyword suggests inline netlist).
- **Deliverable for next round**: extract full .sp from session → build assets (testbench A + hidden B with different CML topology) + reference tuner + check.py ≥8 conds + negatives

## Status: DEBT for r996 (claimed in ledger, deepread done, case synthesis pending)
**Why not this round**: 40-min budget insufficient for complex L1 case (extract .sp from session + build assets + ref + check + negatives + self-validate). §4.9 self-check on PwlFormatConvert-001 delivered instead.
