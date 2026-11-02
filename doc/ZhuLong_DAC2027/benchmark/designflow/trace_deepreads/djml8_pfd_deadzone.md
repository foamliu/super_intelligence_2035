# Deepread: 1792742447012_djml8 — PLL PFD dead-zone characterization (spice_sim)

## Trace provenance
- session: `1792742447012_djml8.messages.json`
- user: `wnyu`  host: `hfeg0plg06`  mc=401  domain: spice_sim
- snapshot 2026-11-02 12:33 (mc300=1001). Live file on .75:
  `/home/wnyu/.cline/data/sessions/1792742447012_djml8/1792742447012_djml8.messages.json`
  (2.7 MB, 17951 lines, 810 messages: 439 user / 371 assistant).
- agent: `lead` (zhulong). tool histogram: editor 159, run_approved_command 140,
  read_files 34, list_allowed_files 20. simulator: **FineSim**
  (`.option finesim_mode=spicead`, `.option finesim_output=fsdb`).
- claimed shard-B 2026-11-02 16:15.

## What the user actually did (task evolution, faithful user turns)
1. **msg[0]** Build PLL PFD module; which `delay` symbol to use? look in
   `/proj/m2701/V0_DDR4/libs/Reference_LP6/stdcells_am` + `intDEV`.
2. **msg[2]** "am 是别的项目，用的不一样的工艺" — wrong lib.
3. **msg[3–10]** Find `tiel` (tie-low, 置0信号) symbol; check colleagues' usage;
   decide PFD delay symbol — buffer vs inv (等效吗); pick inv; choose VT flavor
   (svt/rvt/ulvt) — user's prior company used svt; decides rvt inv; "11 级 inv".
4. **msg[10] (=180)** Write PFD testbench `TB_tt.sp`:
   - netlist: `/rundata/.../sim_PFD_rvt/hspiceD/schematic/netlist`
   - testbench: `/rundata/.../PLL/PFD/TB/TB_tt.sp`
   - input freq **19.2 MHz**, save output-pin waveforms. Read netlist first.
5. **msg[11] (=208)** "我要看 PFD 的死区，你给我写下 meas" → add dead-zone .measure.
6. **msg[12] (=216)** Also measure `dly` symbol propagation delay (in→out).
7. **msg[13] (=230)** Netlist changed; recheck — dly = in→out delay, /10 for one inv;
   is the dead-zone meas correct?
8. **msg[14] (=244)** Sync `TB_ff.sp` / `TB_ss.sp` to same (tiel high + dly meas).
9. **msg[15] (=266)** Run it, put results in `result/`.
10. **msg[16] (=325)** Aggregate the 3 corners' fsdb/mt0 into one summary in `result/`.
11. **msg[17–18] (=334,348]** up/dn no signal → save all waveforms, debug; set tiel=0 rerun.
    → root cause: PFD DFF D-input must be tied HIGH (tiel=VVDD, not 置0). msg[233] fix.
12. **msg[19–22] (=370–380]** dly reversed? → 11 inv stages, in/out direction; user
    re-edits circuit+netlist, re-run.
13. **msg[34–36] (=401–417]** **THE dead-zone spec (key)**:
    > 死区 ADE 仿真 tran, t=20(ps step), -400:20:400 (ps phase sweep);
    > avg vt(up) - vt(dn). 不是折算相位角度, 不清楚怎么定 spec.
    i.e. sweep phase offset Δφ ∈ [-400ps, +400ps] step 20ps; at each, tran sim,
    measure avg(v(up) - v(dn)); dead zone = Δφ range where avg(up-dn) ≈ 0.
14. **msg[37–40] (=442–445]** Run TT/SS/FF tbs across **3 voltages 0.82/0.85/0.88**
    × **5 corners TT/SS/FF/FS/SF**.

## The agent's actual deck (TB_tt.sp, msg[192/209/233])
- FineSim options: `scale=0.855`, `finesim_mode=spicead`, `finesim_output=fsdb`,
  `post=1 probe=1 measfile=1 measform=3 measdgt=6 accurate=1 runlvl=5 method=gear
  converge=1 gmin=1e-14 gmindc=1e-14`.
- params: `VVDD=0.85`, `tr=tf=20p`. `.inc './pvt_tt.sp'` (corner model).
- Stimulus: `V_CLKREF CLKREF 0 pulse(0 VVDD clk_half tr tf ... clk_period)`,
  `V_CLKFB` similar but with phase offset param `t`.
- `.tran 1p 30n` (later extended for the dead-zone sweep window).
- **dead-zone measures (msg[209])**:
  ```
  .meas tran up_pw1 trig v(UP) val='vth' td=td rise=1 targ v(UP) val='vth' fall=1
  .meas tran dn_pw1 trig v(DN) val='vth' td=td rise=1 targ v(DN) val='vth' fall=1
  .meas tran dz_time    param='min(up_pw1,dn_pw1)'      * dead-zone time ≈ reset delay
  .meas tran dz_deg     param='dz_time/clkref_per*360'
  .meas tran dz_mismatch param='up_pw1 - dn_pw1'
  ```
  plus dly in→out `.meas tran dly trig v(dly_in) ... targ v(dly_out) ...`.
- **tiel fix (msg[233])**: PFD_rvt port `GND`→`tiel`; DFF D must be logic-1 ⇒
  `TIEL_VAL=VVDD` (tie HIGH), else PFD produces no UP/DN.
- Aggregation: collect fsdb/mt0 from 3 corners → `result/summary`.

## Netlist reality (foundry-bound, NOT portable)
- PFD_rvt netlist from `sim_PFD_rvt/hspiceD/schematic/netlist` — CXMT foundry
  model (`/proj/m2701/V0_DDR4/model/current/model.sp`, `pvt_tt.sp`). NOT
  reproducible on .75 (no foundry model). ⇒ synthesis MUST use a self-contained
  level-1 MOS PFD, same pattern as SramSNM-001.

## Synthesis plan — `EDA-Eval-DesignFlow-PFDdeadZone-001` (spice_sim L2, B档)
**Sub-skill**: PFD dead-zone characterization — phase-offset sweep + avg(up−dn)
measurement + dead-zone width extraction. The hardest reproducible sub-skill in
the trace; faithful to the user's msg[401–417] dead-zone spec.

**Self-contained PFD (portable to .75 HSPICE, no foundry)**:
- Tri-state PFD = two DFFs (D tied high) + reset AND gate, CMOS gate-level.
  Build DFF from transmission-gate + inverters (or NAND2 latch DFF), AND from
  NAND2+inv. Output buffers (inv chain) on UP/DN. All MOSFET level-1
  (`NMOS vto=0.4 kp=300e-6`; `PMOS vto=-0.4 kp=100e-6`), W/L scalable.
- **Dead-zone origin**: the reset path delay (AND→DFF reset propagation) ≈ the
  min(UP,DN) pulse width at lock; for |Δφ| < this window the charge-pump never
  sees a pulse ⇒ avg(up−dn) ≈ 0. Width scales with gate delay ⇒ scales with W/L
  and VDD ⇒ good cross-input handle.
- **Testbench**: `V_CLKREF` pulse @ f_ref; `V_CLKFB` = same with phase offset
  `t_dly` param. Sweep `t_dly` over [-400ps:+400ps:20ps] (faithful to user spec).
  At each, `.tran` + `.meas tran avg_updn AVG v(up),v(dn) FROM ... TO ...` (or
  param='avg(v(up))-avg(v(dn))'). Extract dead zone = contiguous Δφ window where
  |avg_updn| < thr; gain slope = avg_updn/Δφ outside dead zone.
- **Risk note**: MOS-gate DFFs in HSPICE tran can have init/convergence issues;
  may need `ic`/`.ic v()=` to force DFF reset state, or fall back to a simpler
  edge-triggered DFF. Budget a fallback to behavioral `E/G` sources if level-1
  DFF misbehaves (keep dead-zone physics from the AND+reset delay).

**Visible A**: W=1u/L=1u, vto_n=0.4/vto_p=-0.4, kp_n=250e-6/kp_p=90e-6,
  VDD=0.85, f_ref=19.2MHz, sweep [-400:20:400]ps.
**Hidden B**: W=2u/L=1u (faster gates ⇒ WIDER dead zone), vto_n=0.35,
  kp_n=350e-6/kp_p=120e-6, VDD=0.90, f_ref=19.2MHz, same sweep. Cross-input
  guard: B dead_zone_ps must DIFFER from A (scales with gate delay), defeating
  hardcoded constants.

**Check conditions (≥8, target ~12)**:
  a. submit.zip contains non-empty ASCII `pfd_deadzone.py` + `report.json`
  b. `pfd_deadzone.py` py_compile passes
  c. on hidden B, script runs HSPICE (subprocess exit 0) and report.sim_ok=True
     (proves real sim, not print-only)
  d. report schema valid (n_sweeps, dead_zone_ps, dead_zone_deg, gain_slope,
     monotonic, avg_curve[])
  e. B n_sweeps == 41 (-400:20:400 ⇒ 41 points)
  f. B dead_zone_ps ≈ GT_B (tol ±15ps) — proves real dead-zone extraction
  g. B avg_curve monotonic increasing with Δφ outside dead zone (monotonic=True)
  h. B dead_zone_ps > 0 (dead zone exists, ≥ reset delay) AND < sweep range
  i. B gain_slope ≈ GT_B (tol ±15%) — linear gain region
  j. B dead_zone_deg = dead_zone_ps * f_ref * 360 ≈ GT_B (consistency)
  k. **cross-input guard**: A dead_zone_ps ≠ B dead_zone_ps AND ratio tracks the
     gate-delay ratio (defeats hardcode-expected fake — §4.9 critical guard)
  l. B avg_curve[center] (Δφ=0) ≈ 0 within thr (symmetry at lock)
  m. negatives: 3错解(naive_copy/always_pass/ref_no_core) all FAIL
  n. §4.9 three-fake-submission (empty/print-expected/ref-no-core) all FAIL

**Deliverable contract**: `outputs/submit.zip` containing `pfd_deadzone.py` +
`report.json` (+ any helper .sp the generator writes). entry_point outputs/submit.zip.

**Assets**: `assets/EDA-Eval-DesignFlow-PFDdeadZone-001/` — `pfd_netlist.sp.inc`
  (self-contained PFD subckt), `tb_template.sp` (skeleton with placeholders),
  `task_brief.md`, `hidden/{pfd_netlist_b.sp.inc, hidden_manifest.json}`.

**Open risk**: self-contained MOS-gate tri-state PFD dead zone must be verified
  to actually appear in HSPICE level-1 on .75 before writing check.py GT. If the
  dead zone is ill-defined at level-1, simplify to a 2-DFF PFD where reset delay
  is dominated by an explicit buffer chain (deterministic dead-zone width).
  → Next round: build netlist on .75 FIRST, run dead-zone sweep, confirm GT,
  THEN write check.py + negatives. Same flow as SramSNM-001 (GT from real .75 run).

## Verdict
- Strong spice_sim L2 candidate; faithful to a real, hard, reproducible sub-skill
  (PFD dead-zone sweep). Self-contained level-1 approach proven viable by
  SramSNM-001. Main risk is DFF tran convergence — mitigated by explicit reset
  init + deterministic buffer-chain reset delay.
- **Status: deepread DONE, synthesis NOT started (deferred to next round).**
  Ledger marked `deepread`. Claim preserved. Next round: build .75 netlist →
  confirm dead-zone GT → write check.py + negatives → selftest → append jsonl.
