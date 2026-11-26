# Deepread · 1794983239607_0sfqm (wnyu @ hfeg0pkn005, mc=33, spice_sim)

**Case**: EDA-Eval-DesignFlow-VcoBiasAcStbGen-001 (r936)
**Trace source**: wnyu, host hfeg0pkn005 (10.129.33.24), session 1794983239607_0sfqm, 150 msgs / 11 user-text / 75 tool_use (21 read_files + 22 editor + 19 run_approved_command + 10 list_allowed_files + 2 get_agent_policy_status + 1 ask_question), model deepseek-v4-flash.

## User intent (verbatim user-text msgs)

- msg[0]: `hi`
- msg[2]/[3]: `/proj/m2701/V0_DDR4/workdir/wnyu/simulation/sim_VCO_BIAS_1p085/hspiceD/schematic/netlist/ 再分析下这个电路`
- msg[16]: `/proj/m2701/V0_DDR4/workdir/wnyu/simulation/sim_VCO_BIAS_1p085_rvt/hspiceD/schematic/netlist/netlist 看下这个网表，VDDAI和VCTRLF连在一起，算下VCTRL和VRING及VCTRLH和VRING的传函和稳定性`  ← **core produce intent**
- msg[21]: `2，把这个tb起名字叫VCO_BIAS_ac.sp 放在/proj/m2701/V0_DDR4/workdir/wnyu/simulation/PLL/VCO_BIAS/ 这个路径下`
- msg[35]: `可以的`
- msg[82]: `你来替代下吧`
- msg[94]: `为什么是1Hz–1GHz？不是8GHz`  ← user corrects AC sweep upper bound (VCO runs at ~8 GHz, sweep must extend beyond)
- msg[107]: `波形在哪儿，我自己看下，还有小信号推导有没有图，可以画下`
- msg[135]/[136]: `result/vco_bias_ac_A.fsdb_wdf/ac0.ac 这个图只有四个信号波形`

## Agent produce (75 tool_use)

1. `get_agent_policy_status` + `list_allowed_files` → discover sandbox `/ai_sandbox/m2701/V0_DDR4/agentdir/wnyu` (writable) vs `/proj/...` (read-only) vs `/rundata/...` (read-only raw netlist).
2. `read_files` the DUT netlist at `sim_VCO_BIAS_1p085(_rvt)/hspiceD/schematic/netlist/` + the raw netlist at `/rundata/.../netlist/raw`.
3. `editor` creates `VCO_BIAS_ac.sp` (first at /rundata/.../PLL/VCO_BIAS/, then copies to /ai_sandbox/.../) — the AC+STB deck (full content in assets/A/VCO_BIAS_ac.sp, verbatim):
   - `.option scale=0.855 finesim_mode=spicead finesim_output=wdf post=1 probe=1 measfile=1 measform=3 measdgt=6 accurate=1 runlvl=5 gmin=1e-14 gmindc=1e-14`
   - `.inc './pvt_0p94_tt.sp'` + `.inc './netlist_rvt_base'`
   - `.param VVDD=1.025 ac_vc=1 ac_vch=0` + `.temp 25`
   - supplies: VSUPVDD VDD 0 dc VVDD / VSUPVSS VSS 0 dc 0 / VPD PD 0 dc 0 / VPDBH PDBH 0 dc VVDD
   - AC injection: `VCP VCTRL 0 dc 0.6 ac {ac_vc}` + `VCTRLHS VCTRLH 0 dc 0.6 ac {ac_vch}`
   - bias: `IIBPVCO IBPVCO 0 dc 40u` + `IRING VRING 0 dc 300u`
   - load caps: CVRING VRING 0 10f / CCTRL VCTRL 0 100p / CCTRLH VCTRLH 0 100p / CTOO TOO_HIGH 0 10f
   - **loop-break STB probe**: `VSTB VDDAI VCTRLF dc 0 ac 1` (VDDAI & VCTRLF shorted through 0V ac=1 probe for .stb loop-gain measurement)
   - DUT: `XBIAS IBPVCO PD PDBH TOO_HIGH VCTRL VCTRLF VCTRLH VDD VDDAI VRING VSS VCO_BIAS_1p085_rvt` (11 ports)
   - `.op` + `.probe dc v(VDD) v(VDDAI) v(VCTRL) v(VCTRLH) v(VRING) v(TOO_HIGH)`
   - `.ac dec 50 1 1e10` (extended to 1e10 per msg[94] "not 8GHz") + `.probe ac v(VCTRL) v(VCTRLH) v(VRING) v(VDDAI)` + `.print ac vdb/vp` for each
   - `.stb v=VSTB` + `.probe stb gain() phase()`
4. `editor` creates `run_vco_bias_ac.sh` (finesim V-2023.12-1, `finesim VCO_BIAS_ac.sp -o result/vco_bias_ac.fsdb`, 3 sweeps A=VCTRL inj / B=VCTRLH inj / C=STB).
5. `run_approved_command` × 19 runs finesim (real AC sim, drive_eda_tool).
6. `editor` creates `plot_analysis.py` (parse finesim `.pa0` AC output; compute **loop gain T = -V(VDDAI)/V(VCTRLF)**; find 0 dB crossover by linear interpolation; phase margin PM = 180 + phase(T)@crossover; Bode plot 2×2 panels). `plot_diagram.py` (small-signal derivation diagram per msg[107]).

## Reframe (harness-for-teeth, no FineSim license in SUT sandbox)

Deliverable = `vco_bias_ac_gen.py` — parameterized AC+STB testbench generator. Reads `config_*.json` + the DUT netlist `.subckt` header (port order parsed, NOT hardcoded) + pvt file → emits `VCO_BIAS_ac.sp`. Variant-agnostic: same generator builds the deck for A (VCO_BIAS_1p085_rvt) and hidden B (VCO_BIAS_1p1_lvtf, different subckt name/port order/node names/biases/caps/sweep/loop nodes). Check parses the emitted deck (no sim run) — 13 assertions (a-m) on structure + semantics + anti-hardcode-A.

## Near-dup defense (r927 three-gate + r909 per-toolchain intent-diff)

wnyu already has `EDA-Eval-DesignFlow-VcoBiasTbGen-001` (session 7pswx, mc353) — a VCO_BIAS testbench case. This case is **defensibly distinct** per both gates:

- **r909 action-verb gate**: VcoBiasTbGen verbs = build DC/load/PSRR-tran TB suite + 1.8V→0.94V migration (large-signal DC/transient regulation); VcoBiasAcStbGen verbs = AC small-signal transfer function + loop stability / phase margin (.ac + .stb). Action verbs orthogonal (DC/tran vs AC/stability).
- **r927 gate (c) check-assertion-overlap <50%**: VcoBiasTbGen check asserts DC TB structure + load regulation + PSRR tran + PVT corners + voltage levels; VcoBiasAcStbGen check asserts AC sweep + STB loop-break probe + AC injection sources + transfer-function probe nodes + stability. The two check.py assertion sets share ONLY the trivial ".option/.inc present" overlap — well under 50%. Unlike c08s4 (which was parked because the DSPF PARSE PIPELINE was shared → check assertions overlapped >50%), here the ANALYSIS PIPELINE is disjoint (AC small-signal vs DC/transient).
- Asset: VcoBiasTbGen netlist = sim_VCO_BIAS_1p085 (1.085V, LDO regulation); VcoBiasAcStbGen netlist = sim_VCO_BIAS_1p085_rvt (rvt variant, AC small-signal). Different netlist variant + different deliverable script (build_vcobias_tb.py vs vco_bias_ac_gen.py).

Conclusion: orthogonal analysis domain (AC/stability vs DC/tran/load/PSRR), disjoint check-assertion pipeline, different deliverable script. Defensible per r927 gate (c) letter (check overlap <50%) AND spirit (no shared parse/analysis pipeline). Documented here for dedup audit.

## Selection context

Picked from fresh pool: mc-matrix `summary_1120_reconstructed.tsv` mc≥10 pool=2072 touched=1735 fresh=337. 0sfqm is one of only 3 truly spice-dominant fresh candidates (spice-ratio≥0.30): 8igoq (mingyu1l, mc11, consultation "explain scripts" — rejected no produce), 0sfqm (wnyu, mc33, ratio 0.30, clean netlist+hspice+schematic, no PDK), u33un (e0030760, mc19, ratio 0.54, but e0030760 already 18 B-cases — high near-dup risk). 0sfqm chosen: cleanest spice-dominant fresh, no PDK (asset-reachable), moderate user case count (wnyu 8 B-cases, near-dup defendable per above). Alternatives rejected: y58ez (willz, near-dup of PvtDeckGen-001 same CaPad PVT project), h5giy (e0044131, near-dup of SramSpecVecCoverage-001 same SRAM project), dgo3h (zhenglu, already used for HspiceLibMetaencrypt-001).

## Self-verify

REF: 13/13 PASS (CLI + selftest). NEG 4/4 FAIL: naive_empty (b-m fail, empty deck), naive_print (b-m fail, no file), naive_hardcode_a (c-m fail, A deck on B → wrong subckt + A-leak tokens), fake_core_deleted (c-m fail, hardcoded A port order + A nodes). 3-seed byte-identical (md5 0b63f0d6...). cases/B 463→464, ledger_B case 625→626.
