# Deepread: uqv1k — POR cap-sweep power-on delay testbench (analog_context)

- **session**: `1792722208192_uqv1k.messages.json` (karlwang @ hfeg0plg58 / 10.129.8.109, mc=113, n_msgs=108, n_user=61)
- **source**: fresh_D286_pool.tsv rank 91; peeked in #290 batch (rank 84-103)
- **A-faithful produce turns** (verbatim, pure intent, no root-cause/fix):
  - U#2: `给我生成一个仿真nicap值对上电速度影响的parttern`
  - U#19 (clarification to agent's ask_question): `MIM/MOM 电容或其它类型的电容，想研究容值对 POR（Power-On Reset）电路延迟的影响`

## Trace evolution
- U#0 `你好` (greeting) → U#2 produce request.
- agent list_allowed_files (Desktop) → read lib.defs → search RAG knowledge base for "nicap" (no results) → ask_question to clarify cap type / target.
- U#19 clarifies: MIM/MOM cap, study cap value effect on **POR (Power-On Reset) delay**.
- agent generates `nicap_por_simulation/` deliverable set:
  - `por_testbench.sp` — POR testbench: VDD PWL power-on ramp → R_por + swept MIM/MOM load_cap (RC charging vcap) → Schmitt-trigger comparator → por_out; `.MEAS` t_por_dly / t_vcap_vh / t_rc_tau / t_por_rise; `.alter` cap sweep.
  - `run_simulation.sh` / `run_simulation.tcl` — sweep runner (hspice).
  - `analyze_results.py` — parse .lis .meas → delay vs cap report.
  - `expected_results.md` / `README.md`.
- tries hspice run → aborts (no model lib, B-source/TABLE incompat, convergence). agent iterates netlist compatibility (E-source IF, .alter inline, minimal test). session ends mid-debug (minimal_test exit 0). **No explicit user acceptance** — but task intent + deliverable form unambiguous.

## Why B-grade synthesized
- Real hspice model lib + `/home/karlwang/Desktop/nicap_por_simulation/` paths not attachable; trace never reached clean user-accepted result.
- Gold = data-driven SPICE POR cap-sweep testbench **generator** (`gen_porcap_ref.py <config.json> --out <sp>`), generalizing the agent's converged deck form (VDD PWL ramp / RC + swept cap / Schmitt subckt / .meas delay / .alter sweep).
- Judge is pure static structural check on emitted .sp (no hspice run) → L1, portable, no external dep.

## Case
- **EDA-Eval-DesignFlow-PorCapSweepGen-001** (analog_context, A-faithful, B-grade synthesized, L1, 16 conditions a-p)
- A config: por_cap_sweep_A, vdd=1.8, ramp_tr=10us, r_por=100k, caps=[100f,500f,1p,5p,10p], Schmitt VH=1.26/VL=0.54, nodes vdd/vcap/por_out, measures incl. t_por_rise.
- hidden B: por_cap_scan_B, vdd=1.2, ramp_tr=5us, r_por=220k, caps=[200f,800f,2p,8p], VH=0.84/VL=0.36, nodes avdd/vcapb/porb_out, measures EXCL t_por_rise (metric-subset anti-hardcode).
- 8 negatives ALL FAIL (6 distinct first-fail {b,c,d,g,n,o}); §4.9 three fake submits (empty→c, print_expected_B→o, ref_core_deleted→c) all FAIL; ref PASS 16/16; test==disk sha; D.jsonl 129→130.
