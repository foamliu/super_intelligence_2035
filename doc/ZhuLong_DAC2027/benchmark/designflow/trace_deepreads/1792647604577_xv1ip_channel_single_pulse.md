# Trace deepread: 1792647604577_xv1ip — channel single-pulse response

- **user/host**: alenxu @ 10.129.2.12 (mc=186, keywords: schematic:318 netlist:283 hspice:139 cmos:113 pyaether:94)
- **session**: `/home/alenxu/.cline/data/sessions/1792647604577_xv1ip/1792647604577_xv1ip.messages.json` (489 msgs, 254 user / 235 asst)
- **domain**: analog_context (channel signal-integrity / single-pulse response sim)
- **A-faithful task turn**: U#0 (msg 0) = `仿真channel的单脉冲响应` (verbatim). Pure request, no root-cause/fix given by user → A-faithful.

## Task evolution (msg 0 → 60, the channel-pulse task; msg 61+ = unrelated TX-Ron task)

1. agent loads `eda_agent` + `SpiceAgent` skills, `list_allowed_files` `/home/alenxu/Desktop/SpiceAgent_V2` → finds CTLE/channel design env, `runs/tb_channel_ac/`, `runs/dq_near_pwl/ch_dq0.s2p`.
2. reads `_wchpulse.py`, `gen_dfe_hk.py`, existing `tb_channel_pulse.sp/.pt0`, `tb_full_step_new.sp/.pt0` — finds existing channel+CTLE pulse TBs already exist.
3. runs `gen_dfe_hk.py` → DFE taps from channel+CTLE single-pulse: `H = [184.2, −84.4, +11.1, +17.3, +15.5, −2.0] mV`.
4. existing `tb_channel_pulse.pt0` is sparse (60 adaptive points, no `v(rx)`) → builds a NEW fine-sampled channel-only single-pulse TB in `runs/tb_channel_pulse_v2/`:
   - **stimulus**: single 1-UI pulse, 100 mVpp, CM 0.825 V, UI=96.15 ps (10.4 Gbps), 15 ps edges, 50 Ω source resistor
   - **channel**: `ch_dq0.s2p` (2-port S-parameter, DDR5 DQ0 near-end), instantiated as subckt
   - **RX load**: `Cc dq0 rx 1 µF` (AC-coupling) + `Rbi rx vcm 50 kΩ` (bias to 0.825 V) + `CL rx 20 fF` (mirror `tb_ch_ctle_prbs_100n` topology, CTLE removed)
   - `.TRAN 0.5 ps 8 ns`, `.PROBE V(vsrc) V(ch_in) V(dq0) V(rx)`
5. runner `_run_channel_pulse2.py` (subprocess → FineSim): first attempt fails with GLIBCXX error because agent's `LD_PRELOAD` leaked into subprocess env → fix `env.pop("LD_PRELOAD")` (mirror reference `run_channel_pulse.sh` which unsets it) → FineSim `Successfully Completed` rc=0.
6. analysis `_analyze_channel_pulse.py`: parses `.pt0`, computes baseline / main cursor h0 / post-cursor ISI taps h1..h5 at UI grid (96.15 ps), undershoot. **Bug**: first version sampled absolute `dq0` not deviation (`dq0 − baseline`) → fix to sample `yd`/`yr` deviations.
7. **results** (channel-only, `v(dq0)`):
   - baseline: dq0 = 0.3249 V, rx = 0.8250 V
   - **main cursor h0 = +36.86 mV** @ ~2.975 ns
   - undershoot = −4.15 mV
   - post-cursor ISI: h1=−3.07, h2=+2.12, h3=+3.89, h4=+1.69, h5=+0.65 mV (channel memory short, tails <4 mV after 1 UI)
   - plot `channel_pulse.png` (dq0 + rx)
8. U#59 `给出完整路径` → agent lists all absolute paths (still part of task 1).
9. U#61 (msg 61) starts a NEW unrelated task (`tx_out.sp` inverter Ron) → task 1 ends at msg 60.

## Gold (B-grade synthesized, L1)

Real `/proj /rundata /home/alenxu/Desktop/SpiceAgent_V2` paths + real `ch_dq0.s2p` not attachable → B-grade synthesized. Gold = `gen_chpulse_ref.py`, a data-driven FineSim single-pulse channel TB generator (CLI `<config.json> [--out <sp>]`):
- emits `.OPTION`, `.lib <model_lib> <corner>`, `.param` block (amp/vcm/ui/tr/tf/rs/cc_val/rbi_val/cl_val/tstep/tstop/vhi/vlo/data_rate)
- `VCM vcm 0 DC=vcm`, `VPULSE <vin> 0 PWL(single 1-UI pulse)`, `RS <vin> <ch_in> rs_val`
- inline channel subckt `.subckt <channel_subckt> p1 p2 / S1 p1 0 p2 0 <s2p_file> / .ends` + `XCH <ch_in> <dout> <channel_subckt>`
- RX load `CC <dout> <rx> cc_val`, `RBI <rx> vcm rbi_val`, `CL <rx> 0 cl_val`
- `.TRAN tstep tstop START=0`
- `.MEAS` block driven by `cfg['metrics']`: baseline (`base_v AVG V(dout)`), peak (`peak_v MAX V(dout)` + `tpeak` + `h0`), undershoot (`valley_v MIN V(dout)` + `unsh`) — metrics subset selection is the anti-hardcode axis
- `.PROBE TRAN V(vin) V(ch_in) V(dout) V(rx)`, `.END`

## A vs hidden B (anti-hardcode, double-axis)

| axis | A (visible) | B (hidden) |
|---|---|---|
| circuit | ch_dq0_pulse | ch_dq1_pulse |
| channel_subckt | CH_MODEL | CH_DFE |
| s2p_file | ch_dq0.s2p | ch_dq1.s2p |
| model_lib / corner | model.env / tt_25 | rx_corner.env / ss_m40 |
| pulse amp/vcm/ui/edge | 0.1 / 0.825 / 96.15ps / 15ps | 0.08 / 0.6 / 80ps / 10ps |
| source_r | 50 | 45 |
| load cc/rbi/cl | 1µF / 50k / 20fF | 0.5µF / 100k / 15fF |
| tran tstep/tstop | 0.5ps / 8ns | 0.4ps / 6ns |
| signals vin/ch_in/dout/rx | vsrc / ch_in / dq0 / rx | vs / cin / d1 / r1 |
| data_rate | 10.4 Gbps | 12.5 Gbps |
| metrics | baseline+peak+undershoot | baseline+peak (NO undershoot) |

metrics-subset difference (B omits undershoot) defeats a generator that hardcodes the full A measurement set (caught by condition n); full signal/value/subckt difference defeats hardcoded-A (caught by g/h/k) and hardcoded-B (caught by o).

## check.py — 16 conditions a-p

a zip+imports, b py_compile, c B exit0+nonempty, d .TRAN, e PWL+pulse B ui/edge, f RS B source_r, g inline subckt CH_DFE+ch_dq1.s2p, h XCH cin/d1/CH_DFE, i RX load B values, j .lib rx_corner.env ss_m40, k .PROBE B signals no A, l baseline .MEAS, m peak .MEAS, n NO undershoot .MEAS, o anti-hardcode (A differs + A-only tokens + no B-only literals), p no forbidden paths + determinism.

Self-verify: ref PASS 16/16; 8 negatives ALL-FAIL (distinct first-fail {a,b,c,g,m,n,o}=7); §4.9 three fakes {empty→a, print_expected_B→o, ref_core_deleted→g} distinct=3; test==disk sha 777cafb2c138; k_rationale=k_check=16≥8 GATE PASS; D.jsonl 127→128.

## Lessons

1. **channel single-pulse response is a clean analog_context L1 paradigm**: PWL 1-UI pulse → S2p channel subckt → RX AC-coupling load (Cc+Rbi+CL) → .TRAN; 16 conditions come naturally from stimulus/load/channel/corner/probe/metrics axes.
2. **A-faithful prompt = U#0 verbatim** (`仿真channel的单脉冲响应`); SUT must infer the TB structure (FineSim + S-parameter channel + RX load) from prompt + task_brief alone — task_brief only states the CLI delivery interface, not "what to do".
3. **anti-hardcode double-axis**: (i) full signal/subckt/value/s2p/corner rotation (A vs B) + (ii) metrics-subset difference (B omits undershoot). hardcode_metric_set (always emits all 3 metrics) caught by (n); always_baseline_only (only baseline) caught by (m); hardcode_a (A deck) caught by (g); print_expected_B (hardcoded full B) caught by (o) via B-only literals in source.
4. **FineSim subprocess env hygiene** (LD_PRELOAD leak → GLIBCXX error) is a real trace pain point but not encoded in the L1 static check (candidate only generates .sp, doesn't run FineSim) — kept the gold generator pure-static to stay checkable without a FineSim license.
5. **`.param rs_val = <n>` + `RS ... rs_val` form** matters for the check regex (`rs_val\s*=\s*45\b`); negatives using bare `RS vs cin 45` fail at (f) prematurely — fixed negatives to use the .param form so they fail at their intended later condition.
