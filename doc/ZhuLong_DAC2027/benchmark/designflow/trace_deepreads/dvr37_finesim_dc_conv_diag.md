# trace_deepread: 1794795007762_dvr37 (thomasz@hfeg0pfn058, mc145, spice_sim)

**Session**: `/home/thomasz/.cline/data/sessions/1794795007762_dvr37/1794795007762_dvr37.messages.json` (1.5MB, 187 msgs)
**Scan kw**: analog:885 netlist:546 waveview:162 hspice:115 synopsys:64 verilog:15 mosfet:15 pyaether:6
**Domain**: spice_sim (FineSim/PrimeSim DDROA IDD current sim convergence diagnosis)

## User real intent (verbatim first turn, msg[0])
> /proj/ddgoa/V0/simdir/finesim/ddgoaF/MatrixRun_Netlist_IDD_20261019_aiden_1113_PDhammer/.../
> /proj/ddgoa/V0/simdir/finesim/ddgoaF/MatrixRun_Netlist_IDD_20261019_aiden_1111_pdhammer/.../
> 对比下这两个仿真，为啥一个能跑出来，另一个DC都不收敛

## What the agent actually did (across 187 msgs)
1. **Compare 1111 vs 1113** (msgs 1-43): read control/simrun.log/finesim.elog of both dirs. Found 1111 = "PrimeSim Successfully Completed", 459116 time points, 100%; 1113 = "WARNING! DC not converged", "ERROR! time step too small (diverged)", 21 time points, "all measurement are failed". Built `compare_runs2/3/4/5.py`. **Key finding: the ONLY control diff is one added line in 1113**:
   `vpdhammer5 XI_C_Top.XI_Channel.XI_ChanMid.XI_CMCenterL.XI_CmFsLatchX5L_65.cmN<5> 0 pwlz 0 z '4n-0.1n' z 4n 0`
2. **User followup** (msg[44]): "但是之前加了vpdhammer1-4，没有不收敛啊，怎么多加一个就不收敛了" → agent traced cmN<2>/<3>/<5> node connections in netlist (trace_cmn2.py).
3. **packsim batch round 1** (msgs 54-99): user pointed to `packsim_1116141728/` with 6 variants (option1/2/3/nodeset/2025/prohd). Agent found: option1 (remove vpdhammer5), rawnp1 (single-core), raw2025 (primesim2025) converge; the -np 4 + 2023.12 version with vpdhammer5 doesn't. Built `packx.py`. Read rawnp1/si.elog (CPU 100% = single core) and raw2025/2025.elog.
4. **User constraint** (msg[100]): "我不希望切换版本或者改变核数，有什么办法或者测试方向吗" → agent suggested gmin tuning (gmin=1e-16 too small → try 1e-12), nodeset, spicehd mode.
5. **gmin/gmindc finding** (msgs 129-134): log shows `gmin = 1e-16`, `gmindc = 1e-16`, `INFO: .option gmin=1e-16 is scaled to gmin=1e-19 for BSIM-CMG` — gmindc inherits gmin (not default 1e-12).
6. **nodeset syntax** (msgs 135-136): user found diverging node `cpselb<2>` initial value 16.81mV, asked how to write nodeset → agent gave `.nodeset v(...cpselb<2>) = 0.01681`.
7. **packsim batch round 2** (msgs 137-186): user submitted `runsimdebug1` batch (raw2/noprobe/option4/option5/gmindc/gmindc1, all -np 4 + 2023.12-SP2-3). Agent reviewed each input diff (diffr2b.py), caught `nodeset1.inp` was a duplicate of si.inp (no actual nodeset) → user updated; caught option4/option5 split confusion. **Final finding: `noprobe` (removing 5 `.probe isub(...)` lines) is the ONLY DC-converged variant** — the real culprit was the isub probes, not vpdhammer5 directly. noprobe still running transient (~7.9%, ~40h left).

## Reframe (harness-for-teeth, spice_sim)
Diagnosis Q&A → produce a parameterized `finesim_converge_compare.py` with two subcommands:
- `compare --good <d> --bad <d> --outdir <d>`: diff control files (added/removed force lines) + classify each run's convergence (dc_converged/completed/time_points/measurement_failed/has_dc_not_converged/has_time_step_too_small/diverged_node) → compare_report.json
- `batch --batchdir <d> --outdir <d>`: scan each variant, classify, find converging ones → batch_report.json

## Asset fidelity
A = format-faithful: control/simrun.log/finesim.elog excerpts rebuilt verbatim from trace (vpdhammer5/cmN<5>/CmFsLatchX5L_65/459116/21/DC not converged/time step too small/all measurement are failed/Successfully Completed/6 variant names/noprobe converges/.probe isub commented/gmin=1e-16 scaled to 1e-19 for BSIM-CMG).
Hidden B = different values: force name `vpwrhammer2` on `XI_ChanTop.XI_Array.XI_Row8.XI_SenseAmp_3.blN<7>`, time_points 512038/17, variants base/clean_probe/railmode/nset/gm2/gm3, converging winner `clean_probe` (not noprobe), 3 commented probes (not 5).

## Case outcome
- case_id: EDA-Eval-DesignFlow-FinesimConvCompare-001
- B.jsonl: 422 → 423
- k_check = k_rationale = 10 (a-j), §4.9 5 negatives all FAIL (NEG_RC=5/5), ref 10/10 PASS
- layer: L1 (pure Python text parsing, no EDA binary)
- ledger_B marked: dvr37 → case
