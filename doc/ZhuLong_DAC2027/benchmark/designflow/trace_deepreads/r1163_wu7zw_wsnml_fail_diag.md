# r1163 deepread: wu7zw — WSNML MC sim all-failure diagnosis

**session**: `1795415009363_wu7zw.messages.json`
**user/host**: e0030760 @ hfeg0pkn001
**mc**: 51 (hspice:306; netlist:22; synopsys:17; transistor:13; schematic:3; waveview:1)
**domain**: spice_sim
**nmsgs**: 46
**claimed**: 2026-11-24 20:15 (ledger B)
**status**: DEBT — deepread done, synthesis pending (artifact access blocker, see §blocker)

## Real user intent (U0 原文)
> `/proj/lacaa/V0/workdir/e0039809/MC_hspice/HD_FS_CH252_6T_dspf/ttg_25C_0.75V_dspf_WSNML` 这是根据后仿真网表仿真的WSNML，检查一下为什么全部仿真失败？

User ran a post-sim (DSPF) HSPICE Monte-Carlo WSNML (Write Static Noise Margin Low) sweep on a CH252 HD FS 6T SRAM bitcell at 25°C / 0.75V. All 5000 MC samples failed. User wants the root cause.

## Deck (ttg_25C_0.75V_dspf_WSNML.sp, from U8)
- `* CH252_HD_FS_6T_SRAM_WSNML for Hspice pre-simulation* hspice MC sweep 5000`
- `$ Test item: WSNML - single cell XWSNML, DC write trip measurement`
- `.include '/proj/lacaa/V0/workdir/e0039809/model_file/option_hspice.sp'`
- 6T cell: xmpu1/xmpu2 (PU), xmpd1/xmpd2 (PD), xmpg1/xmpg2 (PG/access) — from pa0
- DC sweep on `vin`, probe `q_wnml`, `.measure WNML` (write trip = where v(Q)-v(QB) crosses 0)

## Assistant tool chain
1. read .sp deck → WSNML DC write-trip, MC sweep 5000
2. .lis = 189169202 bytes (189MB) → too large for direct read
3. **created analyze_wsnml.py** (python-runner) → parse .lis
4. Pattern counts (U14): `error:0, warning:5, converge:6734, failed/measure:5002, trouble:0, crash:0`
   → 5002 "failed/measure" = all 5000 MC samples failed `.measure WNML` (5002 vs 5000 = 2 extra index lines)
5. Located MC index boundaries: `*** monte carlo  index = 1 ***` @ line 11403, index=2 @ 12918 → sample1 = 1515 data rows
6. Read AVA log (U36, Synopsys Advanced Variation Analysis V-2023.12-SP1):
   - `WARNING! Measure wnml be skipped due to all sample data is failure`
   - `ERROR! all measures be dropped since small variations (ERROR)`
   - `Abnormal program termination ... exit code=101`
7. Inspected warning region (U40): `**warning** No connections on node q_wnml; Node ignored.` + `singular supplies` @ line 11352-11353
8. Extracted q_wnml DC sweep data for MC index 1 (U44): vin 0→0.75V, **q_wnml = 0.000e+00 across the ENTIRE sweep** including trip region 0.40-0.52V
9. Read option_hspice.sp (U32): RUNLVL=6, HIER_DELIM=0, REDEFSUB=1, MEASDGT=7, PSF=2

## Root cause (M45 thinking, definitive)
The probed node `q_wnml` stays **flat 0.000** across the whole DC sweep (vin 0→0.75V). The bitcell Q node never performs the intended 1→0 write transition → `v(Q)-v(QB)` never crosses zero → `.measure WNML` = `failed` for every MC sample → AVA drops all measures → abnormal termination exit 101.

Secondary: "No connections on node q_wnml" warning suggests the node is probe-only / not driven after flattening (possible netlist hookup bug in the DSPF extract — q_wnml not actually connected to the bitcell Q).

**The user's deliverable = a diagnostic analyzer** that parses the giant .lis, categorizes failure patterns, locates MC samples, detects the flat-node root cause, and reports the AVA abnormal-termination.

## Reframe for case (synthesis target, next round)
**case id (proposed)**: `EDA-Eval-DesignFlow-WsnmlMcFailDiagProduce-001`
**deliverable**: `outputs/submit.zip` containing `wsnml_fail_diag.py` (independent Python, no EDA deps)
**input (A)**: a sub-100KB `.lis` subset (real excerpt from the trace) + `deck.sp` (real) + `ava.log` (real)
**task**: parse the HSPICE MC .lis log, produce a structured failure diagnosis:
1. Pattern category counts (error/warning/converge/failed-measure/trouble/crash) — must match real counts
2. MC index boundary detection (line numbers of `*** monte carlo  index = N ***`)
3. Per-sample q_wnml DC sweep extraction (vin, q_wnml columns)
4. Flat-node detector: assert q_wnml is constant (all-zero) across a sample's sweep → root-cause flag
5. AVA abnormal-termination detector (exit 101, "all sample data is failure")
6. Root-cause verdict output (structured JSON): `{root_cause: "flat_probed_node", flat_node: "q_wnml", mc_failed: 5000, ava_exit: 101, ...}`

**check() ≥8 conditions** (draft):
① zip valid + py_compile + size>0
② B exit 0 + non-empty stdout
③ pattern counts exact (error:0,warning:5,converge:6734,failed/measure:5002,trouble:0,crash:0)
④ MC index boundaries detected (≥1 sample, line numbers reported)
⑤ q_wnml DC sweep extracted (vin column monotonic, ≥100 rows)
⑥ flat-node detector fires on q_wnml (all values == 0 within tol)
⑦ AVA abnormal-termination detected (exit 101 + "all sample data is failure")
⑧ root_cause verdict JSON has root_cause=="flat_probed_node" + flat_node=="q_wnml"
⑨ (anti-hardcode) B uses different MC sample / different flat node name → detector still fires
⑩ §4.9 three-fake (empty / print-only / core-deleted) all FAIL

**hidden B** (anti-hardcode): different .lis subset — different MC sample index, q_wnml renamed to a different probe node (e.g. `q_wsnm`), different vin range, AVA exit code 101 retained, pattern counts scaled. 3-seed random subset.

## Blocker (why DEBT this round)
- `/proj/lacaa/V0/workdir/e0039809/...` is e0039809-owned; e0031982 (my ssh identity on .75) gets **Permission denied** → cannot `cat` the 189MB .lis / .sp / ava.log directly.
- **Workaround for next round**: the real .lis/.sp/ava.log excerpts are captured verbatim in the cline `.messages.json` tool_results (U8/U14/U36/U40/U44), which ARE readable (`/home/e0030760/.cline/data/sessions/1795415009363_wu7zw/...`). Synthesis will build the sub-100KB `.lis` asset from these real recorded excerpts (not fabricated) + reconstruct the .sp deck from U8. This preserves 真实性 (red line #1) — assets are real trace content, just sub-setted.
- Alternative: ask e0039809 to chmod, or run synthesis on a host where e0031982 has /proj/lacaa access. Defer to next round.

## Pool finding (overturns "fresh 池耗尽")
r1162 MEMORY said "fresh 池仍耗尽". That was based on the 1123 scan's 218-file cross-shard pool. The **new 1124 scan** (`ssh_eda_search_20261124_023802/summary.tsv`, +6956 traces) has **134 hspice-leaning fresh candidates** (mc 5-80, hspice bh≥10, bf≥0.3, not in B ledger). Peeked 4:
- v8ou8 (rongjiez, mc12) — reject: Q&A "这脚本干嘛的" + skill-mgmt
- 6kfqu (aryaoy, mc8) — reject: grill-me skill exploration
- zc8r5 (vincentz, mc61, hspice:694) — Q&A "vtarget 怎么得到的，二分法终点" (bisection understanding, reframable but Q&A-leaning; park candidate)
- **wu7zw (e0030760, mc51, hspice:306) — ACCEPT**: real sim-failure debug, checkable deliverable, claimed

Next round: synthesize wu7zw. Other fresh hspice candidates available in the new scan if wu7zw synthesis hits a wall.
