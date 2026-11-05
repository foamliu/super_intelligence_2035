# Deepread: sid_1792720528359_2tuxj — CTLE Transient Deck Generation

**Trace**: kaixuanx @ hfeg0pkn002 (10.129.2.11), session `1792720528359_2tuxj.messages.json`
**Stats**: mc=183, spice=498/1312 (ratio 0.38), 186 msgs, 753KB
**Domain**: spice_sim (A-faithful L2)

## USER#0 (verbatim, msg[0]) — the A-grade task turn
> 我设计了一个CTLE电路，仿真激励和网表都在这个文件夹里/proj/m2701/V0_DDR4/workdir/kaixuanx/simulation/CTLE_active_ind  ，我已经仿真了CLTE的AC性能ctle_act_ind.sp，现在我想仿真相关的瞬态性能ctle_act_ind_tran.sp，我需要你帮我总结一下需要仿真的各项性能指标，并帮我重新写一个仿真脚本

Clean A-grade "提出需求" turn: gives existing sim folder + already-ran AC deck + wants transient sim + asks to (1) summarize tran performance metrics, (2) write a new sim script. No root cause, no fix given.

## USER#1 (msg[109]): "仿真已经跑完" — acceptance (sim ran successfully)

## USER#2-3 (msg[119,139]): layout generation requests — different task (not used)

## Assistant workflow (msg[1]-~108])
1. `list_allowed_files` on sim dir → found AC deck, tran deck, mc deck, netlist, run scripts
2. `read_files` ctle_act_ind.sp + ctle_act_ind_tran.sp + ctle_act_ind_mc.sp + netlist + run scripts
3. Understood CTLE circuit: differential input INP/INN, output OUTP/OUTN, cross-coupled cap XC1 + feedback resistor XR3 (active inductor HF peaking), PMOS loads XPM0/XPM1, bias XNM0/XNM3/XNM4, resistor ladders XR5-XR8, load caps C0/C4=CL
4. Checked hspice availability: hspice at /apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice (no bsub needed for local run)
5. Read option_hspice.sp (probe=1, PSF=2, RUNLVL=5), corners_0p8.env (tt_25_pre corner)
6. Wrote `ctle_act_ind_tran_v2.sp` (7001+3144+3856 bytes, 3 editor calls) with:
   - .inc option_hspice.sp + switch.sp
   - .lib corners_0p8.env tt_25_pre
   - .inc netlist
   - VDD=0.8V, VSS=0, IBIAS=0.2mA, CL=20f, vcm=0.4
   - EDM OUT_DM = POLY(2) OUTP OUTN = OUTP-OUTN (differential), EIN IN_DM = INP-INN
   - Input: data_rate=7.2e9, ui=1/data_rate, swing=0.2, amp_high/low = vcm±swing/2
   - **Initially used PRBS() source → HSPICE error "Undefined parameter or function definition prbs"**
   - Searched HSPICE docs → found **LFSR** is the correct pseudo-random source: `LFSR(Vl Vh Td Tr Tf rate seed [taps])`
   - Fixed to: `VINP INP 0 LFSR(amp_low amp_high 0 trin trin data_rate prbs_seed prbs_taps)`, prbs_taps=[15,14] (PRBS-15)
   - VINN complementary (amp_high amp_low)
   - .TRAN tstep sim_time START=0ns (tstep=ui/40, sim_time=num_bits*ui, num_bits=1024, twarm=64*ui)
   - .MEAS for 5 metric categories:
     - (A) Eye: eye_vmax MAX V(OUT_DM), eye_vmin MIN, eye_amp=eye_vmax-eye_vmin, eye_mid
     - (D) Output SE: outp_hi MAX, outp_lo MIN, outcm_avg AVG, outcm_wnd PP
     - (B) Timing: td_plh (TRIG IN_DM RISE→TARG OUT_DM RISE), td_phl (FALL), out_trise (20%→80%), out_tfall (80%→20%)
     - (C) Overshoot: out_ovsh MAX (2*ui to 8*ui), out_uns MIN
     - (E) Power: i_vdd_avg AVG I(VDD), i_vdd_max MAX, pwr_avg=i_vdd_avg*vdd_sup
   - .PROBE TRAN V(INP) V(INN) V(OUTP) V(OUTN) V(OUT_DM)
   - .END
7. Validation run (48 bits, short) → sim ran (rc=0) but eye_vmax≈eye_vmin≈0 (PRBS not working) → discovered PRBS() unsupported → fixed to LFSR() → re-ran successfully

## Gold standard
The final `ctle_act_ind_tran_v2.sp` deck with LFSR source + 5-category .MEAS. User accepted ("仿真已经跑完").

## Real assets (extracted from trace read_files, permission-denied on direct scp)
- ctle_act_ind.sp (3978B): AC deck, .AC DEC 1000 1kHz-50GHz, .MEAS ugbw/pm/gain_dc/gain_peak/boost, VDD=0.8V, vcm=0.4, CL=20f
- netlist (6029B): CTLE_active_ind circuit (6T diff pair, PMOS loads, cross-coupled cap XC1, resistor ladders, load caps)
- option_hspice.sp (7166B): HSPICE options (probe=1, PSF=2, RUNLVL=5, etc.)
- ctle_act_ind_tran.sp (4096B): existing (incomplete) tran deck with PULSE source, no .MEAS

## Case design
- **Deliverable**: `gen_ctle_tran_deck.py <ac_deck> <netlist> <out_sp>` — parses AC deck + netlist, generates tran deck
- **Hidden B**: different CTLE (vdd=0.85V, vcm=0.5, CL=10f, ss_125_pre corner, different transistor sizes, no corners_voltage_pre.sp .inc) — forces parsing vs hardcoding
- **k=15 conditions** (a-o): zip+compile, B exit0+nonempty, .TRAN, LFSR/PRBS (non-comment), diff input INP/INN, eye MAX+MIN, delay TRIG/TARG, rise/fall 20%-80%, overshoot, power, CM, vdd matches B (0.85V), netlist .inc, .PROBE output, cross-input guard A(0.8V)≠B(0.85V)
- **Negatives**: naive_empty, hardcode_A, copy_input, print_stub, always_pulse
