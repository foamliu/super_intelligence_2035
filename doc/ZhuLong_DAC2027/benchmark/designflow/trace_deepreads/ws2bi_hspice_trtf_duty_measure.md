# Deepread: 1791523486486_ws2bi (irene1li @ hfeg0pkn004) — spice_sim domain

- match_count=248, 474 msgs (242 user / 232 assistant), 119 tool_use (read_files 101 / editor 110 / search_codebase 5 / run_commands 3 / list_allowed_files 8). Trace file: `1791523486486_ws2bi/1791523486486_ws2bi.messages.json` (3.0 MB), path structure = `<sid>/<sid>.messages.json` subdir (same as 4ybw1/cgqd1).
- keywords: hspice:591, netlist:580, schematic:549, pdk:201, spectre:39, cmos:33, transistor:12.

## Real task (13 substantive user msgs, 5 stages)
1. **S0** — user gives 3 files: `MEAS_tr.sp` (measure tr), `MEAS_skew.sp` (generate skew), `netlist` (new circuit). Wants an ACE/HSPICE measurement file to measure **tr/tf + duty + skew** of the new netlist's important nodes.
2. **S1** — regenerate; **grouping requirement**: measure TR all first, then TF all, then DUTY — do NOT mix per-node. Corrects the important-node list (P2S mux_eve/mux_odd, DRV DINB/DINB_PU, predriver stage1 DqPuDin_STG1/DqPdDin_STG1, stage2 DqPu/DqPd, stage3 pddrv_stg3<2>, stage4 pd/pu_main, zq + ffe paths). Drop skew.
3. **S2/S3/S4** — convert a `.mt0`/measure-result file into a summary table; needs a **Python script** runnable in terminal; **no Chinese** (garbles).
4. **S5** — the desired summary format: `net  TR  TF  SPEC` rows (e.g. DqPd 1.823E-11 2.266E-11 2.000E-11; clk0n 1.200E-11 …; spec 2.000E-11 = 20ps).
5. **S6/S8/S9/S10/S11/S12** — netlist at `/proj/m2701/V0_DDR4/workdir/irene1li/simulation/sim_p2sPredrv_TEST/hspiceD/schematic/netlist/netlist`; spec = trtf<20ps all corners, duty 50%±3%, skew<5ps between pdmain<1-3> & zqpd3/4/5<2>; stimulus `test_dout.sp` (7 corners); **iterate transistor sizes** by editing netlist + rerun sim (fqueue3/fqueue2h queues) until spec met; don't touch originals, write to `/home/irene1li/AI_test/m2701_tx/`. Convert files to all-English.

## Measurable teeth recognized (7+ classes)
- `.measure tran` trig/targ idiom for tr (10%→90% rising) / tf (90%→10% falling); **rise=/fall= qualifiers** needed (inverting nodes give negative times without them).
- duty = high-pulse-width / period at 50% level (pw rise1→fall1, per rise1→rise2).
- **grouping order** TR block → TF block → DUTY block (user's explicit S1 requirement).
- absolute crossing levels from vdd (not referencing netlist param names → portable).
- node list must come from the netlist topology / a nodes file → generalize, no hard-coding.
- ASCII-only Python (user forbade Chinese).
- spec compliance: tr/tf < spec_trtf, duty in [lo,hi].

## Case synthesized: EDA-Eval-DesignFlow-SpiceSim-001 (spice_sim domain, L2)
- **Deliverable**: `gen_meas_deck.py` (Python stdlib, ASCII) — CLI `--nodes <f> --spec <f> [--out]` → emits HSPICE `.measure` deck (TR block, TF block, DUTY block, `.end`), levels = 0.1/0.9/0.5*vdd absolute.
- **Attachments A**: `netlist.sp` (4-stage non-inverting buffer chain, self-contained level-1 .model + pulse + .tran, NO .end), `nodes.txt` (dq_stg1..dq_main), `spec.txt` (vdd=1.8/spec_trtf=100p/duty 0.45-0.55), `MEAS_tr.sp.example`, `task_brief.md`.
- **Hidden B** (`assets/.../hidden/` + embedded in check()): 3-stage chain, vdd=1.2, nodes q1/q2/q3, period 1.5n, spec_trtf=140p — different stage count / vdd / node names / sizes / period so a hard-coded-A tool fails.
- **check.py (10 conditions a-j)**: (a) zip+gen_meas_deck.py+ASCII (b) py_compile (c) gen runs + .measure (d) grouped TR→TF→DUTY + covers B nodes (e) per-node tr/tf/pw/per/duty + no extra nodes (f) levels 10/90/50% vdd (g) **real hspice run** on B+deck exit 0 + .lis measures present no-fail (h) all TR/TF<spec (i) all DUTY in range (j) **3-seed shuffle** consistency + spec. hspice available on .75 sandbox (`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`, license 14696/15000).
- **Self-verify (.75)**: reference `verify_ref.py` → **13/13 PASS** (hspice measured TR q1=130.5p/q2=125.5p/q3=42.3p all<140p; TF 42-103p; duty 0.51; 3-seed consistent). `negative_selftest.py` → 7 negatives (naive_empty/naive_tr_only/naive_hardcode_a/naive_wrong_levels + §4.9 empty_shell/print_expected/ref_core_deleted) **all FAIL** at distinct conditions (c/d/e/f). Local `check.py` reaches (g) hspice gate cleanly (a-f pass).
- pi-SUT real-run: **pending** (budget; pi ~6-12min exceeds remaining round budget). pi_debug_status to note pending.
