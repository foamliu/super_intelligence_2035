# Deepread: 1793847690294_guobm — SAR ADC HSPICE Netlist Generation

## Trace Source
- **Session**: 1793847690294_guobm.messages.json (348KB, 108 msgs, 3 user turns)
- **User**: leo7c @ hfeg0plg95
- **match_count**: 159 (hspice:99, netlist:868... wait no: keywords = netlist:2323;schematic:776;cmos:619;analog:616;waveview:443;verilog:123;hspice:68;aether:39 — spice_count=99 from hspice+other spice-kw... actually hspice:68+aether:39? No. Let me recount: the summary.tsv keywords field shows spice-family = hspice:99? Actually from the raw data: hspice:99 in the candidate list... hmm. The mc=159 from match_count column.)
- **mtime**: 2026-11-05 (ts=1793847690294)
- **Domain**: spice_sim

## User Turns
- U#0 (m0): "你能做什么" — capability question (noise)
- U#1 (m2): "我能在本地调用你妈" — junk
- U#2 (m4): "帮我写一个8bit SAR ADC的hspice代码" — **CLEAN produce-task** ✓

## Gold Standard
Assistant msg#5 announces plan (charge redistribution architecture), then msg#9-65 writes the netlist via editor + write_sar_adc.py:

### Generated Netlist (sar_adc_8b.sp) Structure:
1. **Simulation Control**: `.options post=2 probe csdf=2 runlvl=5`, `.op`, `.tran 0.5n 10u`
2. **Power Supplies**: VDD=1.8V, VREF=1.8V, VCM=0.9V, VGND=0V
3. **Input Signal**: VIN DC 0.9 SIN(0.9 0.9 100k) — 100kHz sinusoidal
4. **Clock**: VCLK PULSE(0 1.8 0 0.1n 0.1n 0.49u 1u) — 1MHz 50% duty
5. **bootstrap_switch subcircuit**: Cboot 1.0p, MP1/MP4/MP6 (pch), MN2/MN3/MN5/MNSAMP (nch), XINV1/XINV2 — 7 MOSFETs + 2 inverter instances
6. **inv subcircuit**: MP (pch W=2u), MN (nch W=1u)
7. **comparator subcircuit** (StrongARM): MN1-MN7 (nch, diff pair + regenerative latch + reset), MP1-MP4 (pch, cross-coupled + reset) — 11 MOSFETs
8. **unit_cap subcircuit**: C1 50f
9. **dac_array subcircuit**: Cb0-Cb7 (50f, 100f, 200f, 400f, 800f, 1.60p, 3.20p, 6.40p) + Cdum 50f — binary weighted 8-bit + dummy
10. **sar_adc_8b main subcircuit**: XBS (bootstrap), XDAC (dac_array), MTP (top-plate switch), Cpar (parasitic), XCOMP (comparator), VCSW_S0-S7 (sampling switches), VCSW_R0-R7 (VREF conversion switches), EINV0-7 (signal inverters), VCSW_C0-C7 (VCM conversion switches), A0 sar_ctrl_va (SAR controller Verilog-A), Rdout0-7 (output drivers), Rph1/Cph1 (sample clock)
11. **Testbench**: XADC instantiation, Cload0-7 (20f output loads)
12. **Probe**: .probe tran for v(vin)/v(clk)/v(samp_out)/v(samp_top), v(comp_outp)/v(comp_outn), v(d<7:0>), v(s<7:0>)
13. **BSIM3v3 Models**: .MODEL nch NMOS (LEVEL=49, VTH0=0.40, full BSIM3v3 params), .MODEL pch PMOS (LEVEL=49, VTH0=-0.40)
14. **Switch Models**: SW_VREF/SW_VCM/SW_VIN VSWITCH (RON=50 ROFF=10G VON=1.2 VOFF=0.6)
15. **.END**

## Case Design
- **Case ID**: EDA-Eval-DesignFlow-SarAdc8bNetlistGen-001
- **Domain**: spice_sim / B-synthesized / L1
- **Deliverable**: gen_sar_adc.py (reads spec.json → writes out.sp)
- **Assets A**: spec.json (8-bit, Cu=50fF, 1.8V, 1MS/s)
- **Hidden B1**: 10-bit, Cu=20fF, 1.8V, 2MS/s
- **Hidden B2**: 12-bit, Cu=10fF, 3.3V, 500kS/s (anti-hardcoding: different bit width, cap values, supply)
- **Reference**: gen_sar_adc_ref.py (parameterized by spec)
- **check.py**: 14 assertions (a-n), subprocess runs candidate on B1/B2, independently computes expected cap values
- **Negatives**: 6 (naive_empty, hardcoded_a, only_print, empty_shell, no_expand, ref_core_deleted) all FAIL
- **§4.9**: empty_shell/only_print/ref_core_deleted all FAIL

## Self-Verify Results
- ref PASS 14/14 ✓
- 6neg all FAIL NEG_OK ✓
- §4.9 三假 FAIL-OK ✓
- Assertion gate: k_rationale == k_check = 14 ≥ 8 ✓
- Byte sync: test field == disk check.py ✓
