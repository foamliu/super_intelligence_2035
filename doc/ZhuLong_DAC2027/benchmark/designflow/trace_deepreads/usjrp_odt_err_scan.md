# Deepread: usjrp (ruisongs @ hfeg0pfn090, mc176, digital)

**Session**: `1793619124342_usjrp` · user `ruisongs` · host `hfeg0pfn090` · mc=176
**Domain**: digital (DDR5 sim verilog / VCS, log-parse + cross-check) — A-domain clean
  (kw `verilog:1536;netlist:46;rtl:27;.def:7;systemverilog:6;drc:4;analog:3;cmos:1`,
   a_tot=1569 vs c_tot=50 vs b_tot=4; top tool=verilog)
**Size**: messages.json 1.6MB / 262 msgs (140 user / 122 assistant) / 37 user-typed prompts
**Trace source**: 11/09 scan `ssh_eda_search_20261109_224902/summary.tsv`
**Ledger**: claimed r404 → marked case `EDA-Eval-DesignFlow-OdtErrStatScan-001`
**Accessibility**: ✅ ssh hfeg0pfn090 reachable, session dir + messages.json readable (1.6MB)
**Selection**: strict-A-dominant filter (top_tool∈{verilog,rtl,...} excluding ambiguous
  `synopsys`/`synthesis`; a_tot>2·c_tot; a_tot>2·b_tot; exclude blocked users
  tongfanl/e02141; exclude analog-marker-heavy). 80 fresh candidates; usjrp is the
  cleanest high-mc (verilog:1536 nearly pure A). Picked over: us0hd/s4my6 (e0039102
  verilog-heavy, plg74, kept as backup), bwdql/x88fx (eric1ch, lower mc), wzkye (gracew
  rtl+verilog, mc129).

## Context (the project)

ruisongs runs DDR5 ODT (On-Die Termination) verification on a `run_odt` directory tree,
one subdirectory per sim case (e.g. `odt_eye_1102.x4_9200/`, `odt_1028.x8_9200/`).
Each case has:
- `A_Summary.rpt` — per-pattern summary lines: `CASE: <name> (Total=N, Failed=N, Passed=N)`
  then `Failed: >>> <pattern>   DQ_Err:34, DQS_t_Err:2, ..., DQODT_Err:6, DQSODT_Err:0,
  ..., Monitor_Err:1` (16 `<field>_Err:<int>` counters per line).
- `A_Compare.rpt` — per-pattern ODT detail lines with pin labels:
  `<pattern> at <t> ps` header, then `Exp_ODT DQS_t[7] at <t> ps: exp=0x1 got=0x0`,
  `Exp_ODT DQ[3] at <t> ps: ...`, `Exp_PkgOut_ODT at <t> ps: ...`.

Root cause the user chases across 37 prompts: **DQS ODT errors are mis-recorded into the
DQODT_Err column** — `A_Compare.rpt` has `DQS_t` ODT detail lines but `A_Summary.rpt`
shows `DQSODT_Err:0` and `DQODT_Err:6`. The user repeatedly asks to "找出根本原因",
"定位到哪一行代码", "按文件列出来", "忽略 Monitor_Err", "0 的不需要列出来".

## Agent's produce actions (20+ scan_*.py scripts)

The agent writes a series of increasingly refined Python scanners (all pure-stdmp, run
via python-runner on the .75 sandbox against `/proj/drvqa/...` paths):

- `scan_odt.py` / `scan_odt2.py` — first-pass ODT summary scan
- `scan_compare.py` / `scan_compare2.py` / `scan_compare3.py` — parse A_Compare.rpt
  ODT detail lines, classify by pin label, count per pattern
- `scan_dqodt.py`..`scan_dqodt3.py` — DQ-vs-DQS ODT disambiguation
- `scan_corr.py` — correlate compare ODT line kinds with summary ODT columns
- **`scan_all_odt_cmp.py` (msg81)** — the cross-check: for each run, count
  `Exp_ODT`/`Exp_PkgOut_ODT` lines by pin-kind (`PkgOut_ODT, DQS_t[, DQS_c[, DQ[, DM[,
  TDQS, LBDQ, LBDQS, CA[, CK[, CS_n`), map pin-kind→expected summary ODT column
  (`DQS_t→DQSODT_Err, DQ[→DQODT_Err, DM[→DMODT_Err, TDQS→TDQSODT_Err, LBDQ/LBDQS→LBODT_Err,
  CA[/CK[/CS_n→CACSCKODT_Err, PkgOut_ODT→DMODT_Err`), and flag where compare has lines but
  summary column == 0 (the mis-record). This is the bug detector.
- **`scan_err_stats.py` (msg177)** — the aggregator: glob `*/A_Summary.rpt`, parse each
  line with `\b(\w+_Err):(\d+)\b` and `\b(DCA_ERR):(\d+)\b`, **exclude Monitor_Err**,
  sum per field, count non-zero lines, emit in stable order, **only non-zero fields**,
  with `(除 Monitor_Err 外无其它 err)` fallback for clean cases.
- `scan_pat_err.py` / `scan_pat_err2.py` — per-pattern non-zero error listing
  (`Failed: >>> <pat>` lines, collect non-zero err fields, skip Monitor_Err).

The recurring produce-task = a log-parser/aggregator + cross-checker over the run_odt
report tree. This is the A-domain log-parser archetype (cf. SpefLogAnalyze-001,
SimIncludeMissDiag-001) but with a structured cross-check (compare pin-kind vs summary
ODT column mapping) that makes the mis-record auto-detectable.

## B档 synthesis (r404 — this case)

**Case id**: `EDA-Eval-DesignFlow-OdtErrStatScan-001` (digital, L1 log-parser+cross-check, B档 synthesized)
- **Deliverable**: `odt_err_scan.py` (pure stdlib, `--base <run_odt> --out <json>`):
  (1) scan `<base>/*/A_Summary.rpt`, per-case aggregate field totals + non-zero-line
  counts, exclude Monitor_Err, only-non-zero fields, canonical field order, clean=true
  for all-zero cases; (2) cross-check `A_Compare.rpt` ODT detail lines (pin-kind→column
  map) flagging `zero_summary_nonzero_compare` mismatches; (3) JSON output
  `{runs:{case:{total,failed,passed,fields:[{name,total,nonzero_lines}],clean}},
  mismatches:[{run,pin_kind,compare_lines,expected_col,summary_col_value,kind}]}`.
- **A (visible, 3 cases)**: odt_eye_1102.x4_9200 (DQS_t mis-record), odt_1028.x8_9200
  (clean, NO A_Compare.rpt), odt_ca_1102.x4_9200 (CA correctly recorded).
- **B (hidden, 4 cases, DIFFERENT)**: odt_eye_1109.x8_9200 (DQS_t+DQS_c mis-record),
  odt_pwr_1109.x4_9200 (LBODT correct), odt_clean.x8_9200 (all-zero ODT, clean),
  odt_mixed_1109.x4_9200 (DM correct + CA[ mis-record). Names/values/pin-kinds/scale all
  differ from A; B has 4 cases vs A's 3, and a fully-clean case A lacks.
- **check.py**: 16 independent conditions (a-p): zip valid+py / py_compile / exit 0 /
  JSON top-level keys / 4 runs / Monitor_Err excluded / only-non-zero / clean case /
  field totals match independent re-parse (random subset) / nonzero_lines match /
  mismatches non-empty / DQS_t→DQSODT_Err mis-record present / CA[→CACSCKODT_Err present /
  compare_lines match independent re-count / canonical field order / no-mismatch-for-
  no-ODT-compare-case. 3-seed randomization (shuffle order, verdict stable).
- **Negatives (4)**: naive_empty (empty report), print_only (hardcoded A values), 
  core_removed (no cross-check + lists zero fields + includes Monitor_Err),
  excluded_compared (correct structure but leaks Monitor_Err). All FAIL.
- **§4.9 fakes (3)**: empty shell / print-only-no-output / no-cross-check-all-clean — all FAIL.

## Self-verify (r404)
- ref `odt_err_scan.py` on B: 16/16 conditions PASS, VERDICT PASS (3 seeds consistent).
- 4 negatives: all FAIL. 3 §4.9 fakes: all FAIL.
- assertion gate: k_rationale == k_check == 16 >= 8 ✓.

## Selection aftermath / PIVOT status
- hzyu6 (fernandoy mc326, claimed-then-parked this round): dup of ii9ew (r401
  VerdiCfgVipGen-001) — same fernandoy PIM2 UVM work, same gen_verdi_cfg.py produce-task.
  Parked as dup. Confirms dedup vigilance needed for fernandoy's multi-session threads.
- PIVOT (自 r381, now 24 轮): clean A-domain fresh exists (80 strict-A candidates this
  round) — NOT a quantity exhaustion. Quality is adequate (usjrp is a clean produce-task).
  The prior "质量枯竭" framing (r374-r400) was partly a filter artifact (the `rc` regex
  matching `drc`, `synopsys` counting path mentions); the refined filter
  (top_tool∈hard-A-tools, exclude synopsys/synthesis, exclude blocked/analog) yields
  usable candidates. PIVOT still technically open but evidence increasingly supports
  "no pivot needed, just better filtering".
