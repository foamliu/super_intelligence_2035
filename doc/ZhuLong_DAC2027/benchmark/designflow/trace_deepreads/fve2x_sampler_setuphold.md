# Deepread: 1794970973210_fve2x — IO_DataLat D-latch setup/hold margin (spice_sim)

## Trace provenance
- session: `1794970973210_fve2x.messages.json`
- user: `irene1li`  host: `hfeg0plg58`  mc=113  domain: spice_sim
- snapshot 2026-11-20 (`summary_1120_reconstructed.tsv`). Live file on .75 host:
  `/home/irene1li/.cline/data/sessions/1794970973210_fve2x/1794970973210_fve2x.messages.json`
  (619 KB, 131 messages). agent: `lead` (zhulong).
- keywords: hspice:302 / netlist:509 / schematic:337 / waveview:90 / synopsys:75 / analog:73.
- claimed shard-B 2026-11-21 02:30; marked case 02:38 (EDA-Eval-DesignFlow-SamplerSetupHold-001).

## What the user actually did (faithful user turns)
- **msg[0]** "你会看采样margin吗" — can you analyze sampling margin?
- **msg[2]** THE key request: analyzing sim_CkDcaMux24to1 (CLK gen + 24to1 + PRBS),
  netlist `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/irene1li/simulation/sim_CkDcaMux24to1/hspiceD/schematic/netlist/netlist`,
  FSDB `.../stimulus_file/sim_1118pvt7PRBS7/test_1118pvt7PRBS7.fsdb`. Two items:
  - **第一项 IO_DataLat (D 锁存器, 下降沿采样)**: DNNER/DNNE_F = 1 D-latch (1 tap),
    DNNOR/DNNO_F = 2 D-latches (2 taps). User's literal definitions:
    > "setup time就是数据到CLK低电平的时间，hold up time就是CLK高电平到数据改变的时间"
    i.e. setup = t(clk↓) − t(data); hold = t(data) − t(clk↑).
  - **第二项 P2S_MAIN / P2S_FFE (三输入与非门采样)**: two CLK + one data; sample when both CLK high.
    setup = data → both-clk-high-start; hold = both-clk-high-end → data.
- **msg[3..130]** agent tries to read the 18 GB FSDB. fscript finds only `fiforst` (top-level),
  internal nodes (`dat0Lat`/`DNNER`/`CLK_Sample`) not found. log says `probe 'v(*)' matches 54282
  nodes, #probed=112084` ⇒ all internal signals ARE saved, but FineSim flattened/hashed node names
  (`_<hex>_void_pp`). Switches fscript → Verdi `fsdbreport` (can't open tuna segments) → WaveView
  `wv -ace_no_gui` via LSF bsub. wv opens FSDB but signal search returns hashed names; internal
  named signals unresolvable. **Session ends at msg[130] with NO measurement delivered.**

## Netlist reality (foundry-bound, NOT portable)
- Top: `sim_CkDcaMux24to1` (flat top, no .subckt wrapper). Hierarchy:
  `XI_io_Mux24to1_8` → `XI_IO_P2sTop` → `XI_IO_DataLat` (D-latches `IO_DataLatrsq`/`IO_DataLatsq`)
  and `XI_IO_P2s4to1Unit_4` → `IO_P2s`/`IO_DataSample` (nand3 samplers).
- Foundry model `/proj/m2701/V0_DDR4/model/current/model.sp` — NOT reproducible on .75.
- FSDB 18 GB with hashed node names — NOT parseable by name.

## Synthesis decision — `EDA-Eval-DesignFlow-SamplerSetupHold-001` (spice_sim, L1, A-faithful)
**Sub-skill**: extract D-latch (falling-edge) setup/hold margins from a sampled waveform,
implementing the user's **msg[2] literal definitions**. This is the user's real analytical
intent (item 1); the agent never delivered it because FSDB node naming blocked signal access.
- The real FSDB is unparseable + foundry-bound ⇒ reproducible offline by exporting CLK & DATA
  sampled waveforms to a CSV (t_ns, clk, data; 0..VDD; dt=10ps) and a sampler-spec JSON.
- Deliverable: pure-Python `sampler_setup_hold.py <wave.csv> <spec.json> [--out report.json]`
  that threshold-crossing-detects edges (linear interp), segments by clk period, finds the data
  edge in each high phase, computes `setup_ps=(t_fall−t_data)*1000`, `hold_ps=(t_data−t_rise)*1000`,
  and emits report.json (per-cycle + min/avg/max aggregates).
- **Visible A**: period=2.0 ns, offsets=[0.20,0.35,0.15,0.45,0.25,0.40] ns.
- **Hidden B** (anti-hardcode-A): period=1.6 ns, offsets=[0.18,0.30,0.42,0.22,0.38,0.12] ns
  (period AND all offsets differ ⇒ B setup/hold values differ from A).
- check.py independently recomputes GT_B from B's CSV (same threshold/interp rule) and asserts
  17 conditions (a..o): zip/py_compile/subprocess/schema/sampler/n_cycles/lengths/per-cycle
  setup/hold within ±20 ps/aggregates/anti-hardcode (close to GT_B, far from GT_A)/4 negatives
  FAIL/3-seed sha256 determinism. k_rationale = k_check = 17.
- negatives: naive_empty / print_only (canned A values) / core_removed (zeros) / hardcode_a —
  all FAIL (verified by negative_selftest.py: ref PASS, 4/4 neg FAIL).

## Verdict
- Faithful to a real, hard, reproducible characterization sub-skill (setup/hold margin extraction
  per the user's exact definitions). The trace's blocker (FSDB hashed naming) is sidestepped by
  exporting the two needed signals to CSV — same spirit as the agent's own fscript/wv attempts,
  minus the foundry FSDB obstacle.
- **Status: case DELIVERED 2026-11-21 02:38 → EDA-Eval-DesignFlow-SamplerSetupHold-001**
  (17 assertions; ref PASS 17/17; NEG 4/4 FAIL; 3-seed sha256 identical; B anti-hardcode-A holds:
  A setup=[800,650,850,550,750,600] vs B setup=[620,500,380,580,420,680]).
