# Deepread: 8l9el — ULVT gm characterization (joeyl)

**Trace**: `1794817546755_8l9el` @ `joeyl/hfeg0pkn004` (mc=68, hspice:36/opamp:44/netlist:164)
**Session**: 156 msgs / 668KB. Date: 2026-11-16.

## User intent (3 user turns)
- **U0** (idx 0): References real netlist `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/4_WCKTOP/2_TRAN.sp` as 范例文档. Asks to **test ULVT pmos+nmos gm across Vgs (saturation→subthreshold) and Vds (saturation→linear)**.
- **U4** (idx 4): Asks about **delvto=-0.2V impact on gm** (manually added `_delvto=-0.2` to netlist to simulate -vth process, which arrives later; unsure if -vth affects gm).
- **U154** (idx 154): Asks **how increasing current indirectly affects gm** (common design lever).

## Assistant work (real finesim characterization)
1. **Model exploration**: read `/proj/m2701/V0_DDR4/model/current/...lib` — found `nulvt_ckt`/`pulvt_ckt` subcircuits, `_delvto` maps to BSIM `delvto` (Vt shift) on underlying device.
2. **Testbench generation** (`_ulvt_mk.py`): single-device DC sweep TBs for NMOS (`tst_nmos.sp`) and PMOS (`tst_pmos.sp`) with finesim options + `.lib top_tt` + `.temp 45`.
3. **Sweep grid** (`_ulvt_gen_sweep.py`): 24 runs = 2 polarities × 2 delvto {0, -0.2} × 6 Vds {0.025, 0.05, 0.1, 0.2, 0.4, 0.875}. Vgs sweep 0→0.9V. Manifest CSV.
4. **finesim execution** (`run_batch.py`): ran all 24 + 1 extra (pmos delvto=+0.2 sign-flip check). Each produced `.pd0` (Vgs Id columns).
5. **Analysis** (`_analyze.py`): parsed .pd0 → per-run CSV (x=vgs, id, gm=dId/dVgs via finite diff). 24 runs analyzed.
6. **Report** (`_report.py`, `_report2.py`): delvto=0 vs -0.2 gm ratio tables at SAT(Vds=0.875)/MOD(0.2)/LIN(0.05) across |Vgs|={0.1..0.8}. Plots (`_plot.py`): gm_vgs_{n,p}_{0,-0.2}.png + gm_vds_{n,p}.png.
7. **REPORT_ULVT_gm.md** written.

## Key physical findings (real, from trace msg 114/142)
- **NMOS delvto=-0.2**: Vth↓ → gm↑ (ratio 1.03–153x across Vgs; huge in subthreshold, ~1.17 in strong sat).
- **PMOS delvto=-0.2**: |Vth|↑ → |gm|↓ (ratio ~0.85, ~constant across Vgs) — **SIGN FLIP vs NMOS**.
- **PMOS delvto=+0.2** (verification run): |Vth|↓ → |gm|↑ (ratio ~1.15) — confirms sign convention.
- **Vds region**: at high Vds (sat) gm peaks then rolls; at low Vds (linear) gm lower and shifts.

## Reframe → case
Produce `ulvt_gm_analyzer.py <spec.json> <data_dir> <out.json>`:
- parse .pd0 (vgs id per line) per spec manifest
- compute gm=dId/dVgs (central finite difference)
- classify vgs-region (subthreshold/transition/saturation) + vds-region (linear/saturation)
- delvto_ratio = |gm(delvto_x)| / |gm(delvto_0)| at matched (vgs, vds)
- PMOS sign-flip verdict (delvto<0 → PMOS |gm|↓ while NMOS gm↑)
- summary verdict + per-run gm curves → JSON

**A** (faithful to trace): NMOS/PMOS × delvto={0,-0.2} × Vds={0.025,0.05,0.1,0.2,0.4,0.875} = 24 .pd0; Vth0=0.30, Vgs 0→0.9 step 0.05. NMOS delvto=-0.2 ↑gm, PMOS delvto=-0.2 ↓|gm| (sign flip).
**hidden B** (anti-hardcode): NMOS/PMOS × delvto={0,+0.15} × Vds={0.02,0.08,0.15,0.3,0.7} = 20 .pd0; Vth0=0.35, Vgs 0→0.85 step 0.05. **Sign pattern FLIPPED**: NMOS delvto=+0.15 ↓gm (ratio<1), PMOS delvto=+0.15 ↑|gm| (ratio>1) — naive "NMOS>1/PMOS<1" hardcode FAILS.

## check.py ≥8 conditions (plan)
① zip+py_compile+size ② B exit0+非空JSON ③ 顶层键集合 ④ n_runs==oracle ⑤ per-run gm finite-diff==oracle(tol) ⑥ vgs-region分类==oracle ⑦ vds-region分类==oracle ⑧ delvto_ratio==oracle(per Vgs at sat Vds) ⑨ PMOS sign-flip verdict==oracle(B: NMOS ratio<1, PMOS ratio>1) ⑩ anti-hardcode(A delvto -0.2 absent in B, B delvto +0.15 present) ⑪ 3-seed sha256 consistent
