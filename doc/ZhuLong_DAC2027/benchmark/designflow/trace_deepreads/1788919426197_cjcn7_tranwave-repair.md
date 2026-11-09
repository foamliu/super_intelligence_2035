# Deep-read: 1788919426197_cjcn7 — SaNP transient-noise testbench repair

- sid: `1788919426197_cjcn7`
- user/host: `ming1w@hfeg0pkn005`
- match_count: 164 (hspice=266 / schematic=197 / netlist=100)
- domain: waveform (transient-noise / .tr0 waveform) + schematic_netlist
- size: 801 KB, 99 msgs (52 user / 47 assistant), 5 real user turns
- ledger: claimed, shard D, domain=waveform

## Real user intent (verbatim turns)

1. `document sanp_result.log has a error,help me fix it.`
2. `read this document again. give me the solution about the error`
3. `how can we set "noisefmax"`
4. `in reslut,I can't find waveform of simulation`
5. `it have not transient simulation waveform`

## Real working dir

`/rundata/drjpa/V0/simdir/finesim/workdir/ming1w/simulation/Check_SaNP_1/hspiceD/schematic/vddvssdrop/TT1.166v25c/`

- `Check_SaNP_tb.sp` — SPICE testbench (FineSim → PrimeSim HSPICE)
- `sanp_result.log` / `sanp_result.elog` — FineSim run log
- `result/Check_SaNP_tb.lis` — HSPICE listing (80 000+ lines)
- `result/Check_SaNP_tb.st0` — status (dcop only, no tran)
- `result/Check_SaNP_tb.tr0` — **MISSING** (transient waveform never produced)
- model file: `/apps/imctf/models/G4B/model_local/G4B_CIP_Model_L6_v0d5_t06/incFile_G4B_CIP` (line 12138 subckt ntnlv_hlsa)
- corner: `TT1.166v25c` (TT, 1.166 V, 25 °C)
- circuit scale: 15 078 nodes, 2 239 devices

## Defect chain diagnosed by the agent (5 classes)

| # | Defect | Evidence (log/tb line) | Fix |
|---|--------|------------------------|-----|
| 1 | MOSFET W below model binning min | `ERROR! failed to find correct binning model for mosfet 'xi_pcs_loading_0.xmmn13.mn1' (mname=ntnlv_hlsa l=0.049608u w=0.620736u)`; model range `wmin=0.900u wmax=1.600u` | raise instance W to ≥ 0.900u |
| 2 | `.trannoise` not supported in PRO mode | log L97 `Main Mode: promd`; log L135 `ERROR! only spice mode supports transient noise analysis. Restart ... with spicehd/spicemd/spicead mode.` | `.option mode=spicemd` (or switch to HSPICE) |
| 3 | `.option list` → 80 000+ line listing → LSF job killed before transient | `.st0` ends after `dcop`, never reaches `tran:`; `.tr0` missing | comment out `.option list` |
| 4 | empty `.trannoise` + params on `.option noisefmin/noisefmax/noiseseed` | `.lis` L5366 `Warning: missing .trannoise command data`; L5368 `Error: Please check for format error`; L5370 `hspice job aborted`; L29 `**warning** Unknown option noiseseed` | put `fmin=.. fmax=.. noiseseed=..` directly on the `.trannoise` line; delete orphan `.option` |
| 5 | `.option ARTIST` conflicts with `post=2` | agent summary step 4 | comment out `.option ARTIST` |

Also FineSim→HSPICE syntax shift: FineSim used inline `fmin=/fmax=/seed=` on `.trannoise`; HSPICE accepts `fmin/fmax/noiseseed` on the `.trannoise` line but `noiseseed` is **not** a valid `.option` (only `noisefmin/noisefmax` are .option params). Final correct form: `.trannoise fmin=10 fmax=10G noiseseed=1`.

## Agent toolchain

run_commands (find), list_allowed_files (×7, policy-scoped dir walks), read_files (×31, log/tb/lis/st0), editor (×1, blocked by policy), run_approved_command (×1, denied), fetch_web_content (×1, blocked), search_codebase (×2), ask_question (×1, mode choice). Agent could READ but not WRITE (policy) — gave manual fix instructions.

## Synthesis plan (B-grade, L2)

- **task_id**: `EDA-Eval-DesignFlow-SaNPTrannoiseFix-001`
- **deliverable**: `submit.zip` containing `fix_spice.py` — a SPICE-testbench repair tool that takes a broken `Check_SaNP_tb.sp` + a `model_ranges.json` sidecar and emits a corrected testbench + `fix_report.json`, fixing all 5 defect classes generally (not hard-coded to A).
- **visible A**: broken `Check_SaNP_tb.sp` (TT1.166v25c, W=0.620736u vs wmin=0.900u, promd, .option list, empty .trannoise + orphan .option noisefmax, .option ARTIST+post=2) + `model_ranges_A.json`.
- **hidden B**: different-scale broken testbench (corner SS0p95v-40c, W=0.45u vs wmin=0.600u, .trannoise params fmin=100 fmax=5G noiseseed=7, .option list, empty .trannoise + orphan .option, ARTIST+post=2) + `model_ranges_B.json`. NOT in SUT sandbox.
- **judge**: `check.py` runs fix_spice.py on B (real subprocess) + `spice_lint.py` subprocess (real-run) → 11 labeled conditions (a–k): compile, run-B-exit0, lint-overall-PASS, defect1-5 each PASS, fix_report lists 5, anti-hardcode A≠B (different clamp values), 3-seed md5 determinism. ≥8 ✓ (k=11).
- **negatives**: 2 broken submissions (only-defect-1 fix; no-op cp) + negative_selftest all-FAIL; §4.9 three fakes (empty / print-only / core-deleted) all FAIL.
