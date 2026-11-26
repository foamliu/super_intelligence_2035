# Trace deepread: cdvwc — cksys clock-mux xlsx→CSV→JSON codegen pipeline

- **session**: `1793779591197_cdvwc` (e0046472 @ hfeg0plg76 = 10.129.8.124, mc=255, 509 msgs / 1.6MB)
- **keywords**: rtl:1014;verilog:583;synopsys:31;systemverilog:10 (ana=1 → clean digital, true shard A)
- **ledger**: claimed shard A (r296, domain=digital), status → deepread (DEBT:1, build pending infra)
- **trace_source**: real cline session, user e0046472, project `/home/e0046472/Design/Foudamental/cksys_dev/`

## Conversation (15 user turns)
1. U1: "read this folder ...cksys_dev, and summary the script usage" → analysis (folder overview)
2. **U2: "change the parse_ckmux_v2.py, please use the CKMUX.xlsx to generate all the csv files, and then use the csv to geneate json model."** → **A-faithful produce-task** (user states goal, no root cause given ✓)
3. U3: "how can i check wether openpyxl is installed" → trivial Q
4. U4: "rewrite the USAGE.MD" → produce-task (doc)
5. U5: fix ~T~@ symbols in USAGE.MD → fix
6. U6: generate_v2.ps1 PowerShell-on-Linux errors → debug
7. U7: gen_clock_init_v2.py FileNotFoundError (Windows temp CSV path) → debug
8. U8: check_rtl.py FileNotFoundError generated/cksys.v → debug
9. U9: ~@~T in *.sdc files, rewrite script → fix
10. U10: iverilog not found → debug
11. U11: "i have vcs, please use vcs to do this check" → fix
12. U12: SyntaxError Non-UTF-8 in gen_cksys_rtl_v2.py → debug
13-14. "go on" → continue
15. "are you there" → idle

## Selected turn for A-faithful case = U2
U2 is a clean "提出需求" turn (build xlsx→CSV→JSON pipeline), no root-cause/fix given by user. The assistant's deliverable (msg 33) = modified `parse_ckmux_v2.py` adding `export_xlsx_to_csvs()` (reads CKMUX.xlsx 8 sheets → 8 CSVs in `script/decrypted_csvs/`) + changed CSV dir from a Windows temp path to local + called it in `main()`; the existing CSV parsers then build the JSON clock-tree model → `generated/cksys_v2.json`.

## Gold (reference solution) = on-disk `script/parse_ckmux_v2.py` (post-U2, 555 lines, 18710 B)
Fetched to .75 workdir as `parse_ckmux_v2_gold.py`. Structure:
- `export_xlsx_to_csvs()`: openpyxl.load_workbook(data_only=True); sheet→CSV map:
  `PLL→0.CKMUX_PLL.CSV`, `PLL Divider→1.CKMUX_PLLDivider.CSV`, `Clock Source→2.CKMUX_ClockSource.CSV`,
  `Clock List→3.CKMUX_ClockList.CSV`, `CKBUF→4.CKMUX_CKBUF.CSV`, `CKCG→5.CKMUX_CKCG.CSV`,
  `CK_SEL→6.CKMUX_CKSEL.CSV`, `CK_Mon→7.CKMUX_CK_Mon.CSV`; writes utf-8-sig CSV; float fmt `f"{x:.10f}".rstrip("0").rstrip(".")`.
- parsers: parse_pll, parse_pll_divider, parse_clock_source (grouping by Input clock), parse_clock_list (OCC/Voltage cols), parse_ckbuf, parse_ckcg, parse_cksel.
- model: OrderedDict with 12 top-level keys: simulation_only{plls,pll_dividers}, sources, groups, divider_groups, input_ports, mux_outputs, buffers, gates, output_ports, internal_wires, cksel{sources,n_outputs,outputs}, monitor.
- paths: XLSX_PATH=ROOT/1.excel/CKMUX.xlsx, DECRYPTED_DIR=SCRIPT/decrypted_csvs, OUT_DIR=ROOT/generated/cksys_v2.json (SCRIPT_DIR=Path(__file__).parent, ROOT_DIR=SCRIPT_DIR.parent).

## Input asset = CKMUX.xlsx (real, 8 sheets)
- PLL: 3 PLLs (MAINPLL 2048, UNIVPLL 2156, USBPLL 480) [A values]
- PLL Divider: 18 dividers; Clock Source: 50 rows / 12 groups; Clock List: 5 mux outputs;
  CKBUF: 2; CKCG: 2; CK_SEL: 11; CK_Mon: 32.
- Gold run on A → 8 CSVs + cksys_v2.json (40KB): plls=3, pll0_freq=2048.0, pll0_step=13,
  mux_outputs=5, buffers=2, gates=2, cksel=11, input_ports=10.

## Hidden B (built on .75 via build_B.py, openpyxl) = CKMUX_B.xlsx
Modified A: PLL freqs MAINPLL 2048→3200 (step 13→15), UNIVPLL 2156→2800 (step 13→17), USBPLL 480→1500 (step 24→11); Clock List row2 freq 26→52. Counts unchanged (3/5/2/2/11) → cross-input guard via freq value, not count.
Gold run on B → plls=3, **pll0_freq=3200.0**, pll0_step=15, mux=5, buf=2, gate=2, cksel=11.
B PLL CSV: `MAINPLL,3200,26,15` / `UNIVPLL,2800,26,17` / `USBPLL,1500,48,11` (vs A: 2048/2156/480).

## Pre-U2 asset (file to "change") = parse_ckmux_v2_preU2.py (built on .75 from gold)
= gold minus `export_xlsx_to_csvs()` def, minus Step-0 export block in main(), DECRYPTED_DIR reverted to
`Path(r"C:\Users\E0046472\AppData\Local\Temp\cimicode\cksys_csvs")`. py_compile OK. Keeps all CSV parsers + JSON builder (so SUT's job = add xlsx→CSV export + fix CSV dir + call it). 481 lines.

## Case design (ready to build — EDA-Eval-DesignFlow-CkmuxXlsxExport-001)
- domain=digital, track=A-faithful, L1-static + subprocess (offline Python w/ openpyxl; no EDA tool).
- **A assets (SUT-visible)**: CKMUX.xlsx (=A xlsx) + parse_ckmux_v2.py (=preU2, the file to change) + prompt.txt (U2 verbatim) + task_brief.md (≤3 lines: deliver parse_ckmux_v2.py in outputs/submit.zip; script reads ../1.excel/CKMUX.xlsx, writes CSVs to ./decrypted_csvs/, writes JSON to ../generated/cksys_v2.json).
- **hidden B**: CKMUX_B.xlsx + hidden_manifest.json (NOT in SUT sandbox).
- **reference**: parse_ckmux_v2_ref.py (=gold) + reference_submit.zip (contains it as parse_ckmux_v2.py) + expected_b/{8 CSVs, cksys_v2.json} (gold output on B, already on .75 projB/).
- **check.py (16 conds a-p)**, runs SUT script on B in replicated layout (1.excel/CKMUX.xlsx=B, script/parse_ckmux_v2.py=SUT), then:
  a. submit.zip contains parse_ckmux_v2.py
  b. SUT script py_compile OK
  c. `python3 script/parse_ckmux_v2.py` (cwd=grading) exit 0
  d. script/decrypted_csvs/ has 8 CSV files
  e. CSV filenames == {0.CKMUX_PLL…7.CKMUX_CK_Mon}
  f. SUT 0.CKMUX_PLL.CSV == expected_b (normalized: csv-reader, float-tolerant cell cmp)
  g. SUT 2.CKMUX_ClockSource.CSV == expected_b (normalized)
  h. SUT 3.CKMUX_ClockList.CSV == expected_b (normalized) — differs A(26) vs B(52)
  i. generated/cksys_v2.json exists
  j. JSON parses; top-level keys ⊇ {simulation_only,sources,groups,divider_groups,input_ports,mux_outputs,buffers,gates,output_ports,cksel,monitor} (≥11)
  k. JSON simulation_only.plls list len == 3
  l. JSON mux_outputs len == 5
  m. JSON buffers len == 2 AND gates len == 2
  n. cross-input guard: JSON plls[0].freq_mhz == 3200 (B) AND != 2048 (A) — anti-hardcode-A
  o. 3-seed: run 3× → cksys_v2.json byte-identical
  p. anti-trivial: empty script fails b; print-only fails c/d (covered by b/c/d)
- **negatives** (≥2 + 3 §4.9 fakes): noop (empty) → b; hardcode_a (embeds A's CSVs/JSON, no xlsx read) → f/n; stub (writes 8 empty CSVs + empty JSON) → f/j; keep_windows_path (doesn't add export, keeps Windows DECRYPTED_DIR) → c (FileNotFoundError) / d.
- test_rationale = `16 条断言：①zip含parse_ckmux_v2.py ②脚本py_compile通过 ③在B布局下运行exit0 ④生成8个CSV ⑤CSV文件名匹配8约定名 ⑥PLL CSV内容匹配B ⑦ClockSource CSV匹配B ⑧ClockList CSV匹配B(freq52) ⑨生成cksys_v2.json ⑩JSON含≥11个顶层key ⑪JSON plls数=3 ⑫JSON mux_outputs数=5 ⑬JSON buffers=2且gates=2 ⑭交叉输入plls[0]freq=3200(B)且≠2048(A) ⑮3种子JSON字节一致 ⑯空壳/纯print假提交失败` (k_rationale=k_check=16≥8 GATE PASS)

## BLOCKERS (why not built this round r296) — infra, not design
1. **Binary xlsx transfer**: no shared FS between .75 and local; local can't ssh .75 (timeout); openpyxl not installed locally (pip install --break-system-packages timed out). xlsx is 29KB binary; read_file returns ~40KB base64 — cannot be faithfully inlined through the agent into a local write call. **Resolve next round**: stdlib xlsx builder (zipfile+XML, inline strings) from the small TEXT CSVs (A_all_csvs.txt / B_all_csvs.txt, 155 lines each, already on .75 workdir) → rebuild CKMUX_A.xlsx + CKMUX_B.xlsx locally; verify on .75 (openpyxl reads stdlib-built xlsx → gold reproduces A output).
2. **openpyxl in grading env**: SUT's script + check.py's subprocess need openpyxl. Not confirmed available in the eval harness's check() env. **Resolve next round**: confirm via r293 DftTestmaxLaunchFlow check.py pattern (does it run subprocess locally or via eda_flow on .75?); if local lacks openpyxl, either (a) make check.py run the SUT script on .75 via eda_flow run_code, or (b) vendor a minimal openpyxl, or (c) reframe check.py to compare SUT's CSVs/JSON to pre-computed expected_b files (no openpyxl needed in check.py itself; only the SUT's subprocess needs it — still requires openpyxl at grade time).
3. **Self-verify**: requires running gold on B's xlsx (openpyxl). Do on .75 (workdir has all pieces: CKMUX_A/B.xlsx, gold, preU2, expected_b).

## Files already prepared ON .75 workdir (default_20261110-r296_shardA-r296_0)
- `CKMUX_A.xlsx`, `CKMUX_B.xlsx` (binary, ready)
- `parse_ckmux_v2_gold.py` (reference), `parse_ckmux_v2_preU2.py` (asset, file-to-change)
- `projA/` (gold run on A: script/decrypted_csvs/*.CSV, generated/cksys_v2.json)
- `projB/` (gold run on B: expected outputs)
- `A_all_csvs.txt`, `B_all_csvs.txt` (155-line text CSV dumps for stdlib xlsx rebuild)
- `dig_filter.py`, `peeker.py`, `deepread.py`, `extract_tooluse.py`, `build_B.py`, `transform_preU2.py`, `fix_preU2.py`

## Pool finding (r296, corrects r295's "pool-quality bottleneck")
r295 peeked only the top-10-by-raw-mc (mostly wrong-shard: calibre/virtuoso/SPICE netlist noise) and parked them, concluding "clean produce=0". r296 applied a **digital-dominant filter** (dig>ana, dig>50) on the r292 full-rescan summary.tsv → 317 digital-dominant sessions. Cross-referenced against the **correct normalized** ledger (strip `.messages.json` suffix; earlier rounds' `next`/checks used 5-char suffixes against full-id ledger → false "un-ledgered"). Result: most strong-digital candidates (lond8→SynLintFlow-001, r3gb7→CovFMFlow-001, uiqz1→DesignListGen-001, mmmtz→DcSynthAnalyze-001, 7j9b9→SimFailParse-001, qiqs7→AprStampFix-001, 8ylkn→XyzSvEnumPort-001, xt9ag→VconnConsistCheck-001, pfubi→TimingECO-001) are **already delivered as cases by parallel shard-A sessions** — the pool was being consumed, not exhausted. Truly un-ledgered clean-digital: cdvwc (this trace, xlsx pipeline), + a few e0039602 netlist/LVS (shard-C-ish) and fernandoy UVM (too big, r295 parked). **cdvwc is the best (only) clean un-ledgered shard-A digital produce-task.** Lesson: always normalize ledger session ids (strip `.messages.json`) before exclusion; the 5-char-suffix check is wrong.
