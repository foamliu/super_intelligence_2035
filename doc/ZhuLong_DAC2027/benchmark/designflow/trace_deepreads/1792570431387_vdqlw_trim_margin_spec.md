# trace_deepread: 1792570431387_vdqlw — SCmos_col delay-trim chain netlist understanding + margin spec verification

- **trace**: `1792570431387_vdqlw.messages.json`
- **user / host**: ypzheng @ hfeg0pkn003
- **match_count**: 335 (hspice 65 / spectre 4 / netlist 566 / schematic 576 / pyAether 16)
- **shard / domain**: B / characterization
- **status**: case → `EDA-Eval-DesignFlow-TrimMarginSpec-001` (2026-11-03)
- **model**: deepseek-v4-flash (dsv4)

## Real task (U[101], the spec — trace-faithful, B档 synthesized)
> 定位到SCmos_col这个模块，理解这句话的意思：CkeColScmosEn在GResetN拉高之后关闭，Column的CkeColScmosRst与CkeColScmosEn信号follow act2信号打开，前者同样晚于后者，通过cm1_sc_BnkColEnRstGap<1:0>可以对于delay时间进行trim，之间的margin需要大于1.5ns。

ypzheng feeds a DRAM per-bank FineSim netlist (`/proj/ddgoa/V0/simdir/finesim/.../Netlist_Vcap.../netlist`, permission-denied / foundry, not portable to .75), asks the agent to locate the `SCmos_col` submodule and explain/verify the delay-trim chain:
- `CkeColScmosEn` (column SCmos enable) closes after `GResetN` deasserts.
- `CkeColScmosRst` (column SCmos reset) opens following `act2`, **later than** `CkeColScmosEn`.
- The En→Rst delay gap is trimmed by the 2-bit bus `cm1_sc_BnkColEnRstGap<1:0>`.
- **Spec: the En→Rst margin must be > 1.5 ns** for the trim setting to be compliant.

## Real flow (195 msgs)
ypzheng loads an Aether-EDA-QA skill, then drives the agent through:
1. U[39/41] "can I feed you the netlist to understand the circuit" → read `/proj/ddgoa/.../netlist` (35 editor / 31 run_approved_command / 13 read_files).
2. U[101] the spec above — locate SCmos_col, explain the delay-trim chain + 1.5 ns margin.
3. U[125/133] "I only found CkeRowScmosEn, not CkeColScmosEn — at which hierarchy level is it?" → descend into SCmos_col layer.
4. U[135] read a波形 file under the SCmos_col checklist lens.
5. U[166/180] explain redundancy signal generation + address-gating power-saving.
6. U[194] line-by-line analysis of `Ras_vint_temp.sp`.

The agent uses editor + run_approved_command (python/shell runner) to slice + grep the 100k-line DRAM netlist, locate the SCmos_col subckt, trace the CkeColScmosEn/CkeColScmosRst fanout, and explain the cm1_sc_BnkColEnRstGap trim mechanism. No HSPICE binary run by the user — pure netlist-understanding task.

## Reproducible sub-skill (the case target)
**Hierarchical SPICE netlist module location + delay-trim-bus extraction + per-trim-code margin spec compliance verification.** The real DRAM netlist / FineSim deck is foundry-permission-denied and non-portable, so the DUT is replaced by a self-contained hierarchical SPICE netlist fragment that preserves the measurable structure:

- `.SUBCKT SCmos_col` with ports `CkeColScmosEn`, `CkeColScmosRst`, `GResetN`, `act2`, and the trim bus `cm1_sc_BnkColEnRstGap_<w-1>...cm1_sc_BnkColEnRstGap_0`.
- A delay chain (En → series of buffer taps) + a width-selected mux driving CkeColScmosRst, the tap chosen by the trim bus.
- `.PARAM spec_margin = <val>n` encoding the spec.
- A `.measure`-style `.lis` fixture giving the measured En→Rst delay per trim code (gap string).

The candidate must produce a structured JSON report:
`{module, trim_bus, trim_width, en_signal, rst_signal, spec_margin_ns, delays_ns{code:val}, compliance{code:bool}, violators[code], worst_code, worst_margin_ns}`.

**NOT covered by existing shard B cases**: ProbeTrim-001 = FineSim `.probe` node-trim (sim perf), DelayChainEdgeMeas-001 = single-buffer-chain edge 10-90 measurement, SubcktExtract-001 = `.SUBCKT` stream extract + X-inst parse. This case's distinct axis = **parameterized trim-bus (gap) selection across a bus width + per-code spec-compliance matrix + worst-code identification from a measure report**.

## Core traps baked into the case
1. **Trim bus is a bus, not a scalar** — parser must group `cm1_sc_BnkColEnRstGap_<i>` ports, derive base name + width = count of distinct bit suffixes (A=2-bit, hidden B=3-bit). Hardcoding width=2 fails B (width=3).
2. **Gap code bit order** — `cm1_sc_BnkColEnRstGap_<w-1>` is MSB, `_0` is LSB; the gap string in the `.lis` is `<msb>...<lsb>`. Reversing bit order gives wrong code→delay map.
3. **Margin = En→Rst delay** (the gap), not Rst→En, not absolute time. Compliance = `delay > spec_margin` (strictly greater).
4. **worst_code = min-margin code** (closest to / below spec), not max-delay code, not first-violator.
5. **violators = codes with delay ≤ spec** (strictly ≤ fails the "> spec" requirement).
6. **spec_margin parsed from netlist `.PARAM`**, not hardcoded 1.5 (B uses a different spec).
7. **Cross-input guard** — re-run candidate on hidden B (different width, different spec, different delays, different violators); assert B's delays ≠ A's and B's violators ≠ A's, defeating hardcoded-A.

## Hidden B vs visible A
- **A** (visible): 2-bit trim bus (4 codes 00/01/10/11), spec_margin=1.5n, delays=[1.234,1.612,2.005,2.418]ns → violators=[00], worst=00 (1.234).
- **B** (hidden): 3-bit trim bus (8 codes 000..111), spec_margin=1.2n, delays=[0.95,1.05,1.25,1.40,1.60,1.85,2.10,2.45]ns → violators=[000,001], worst=000 (0.95).
- width (2 vs 3) + spec (1.5 vs 1.2) + delay set + violator set all differ → cross-input guard defeats hardcoding A.

## Self-verification plan (L1, offline Python — no .75 HSPICE needed)
- ref runs on A → report_A matches GT_A on all fields.
- ref runs on B → report_B matches GT_B on all fields.
- 5 negatives (empty_shell→a/b · print_expected→b · hardcode_A→m/n cross-input · no_parse→i · ref_no_core→h/i) all FAIL.
- §4.9 three fakes (empty / print-expected / ref-no-core) all FAIL.
- 14 independent conditions a-n (k=14=k_check≥8 ✓).
