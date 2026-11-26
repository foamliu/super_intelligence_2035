# trace_deepread: 1793253175918_yeyve / xinqiaoz / DRC Dummy QA target-layer check (item 9)

- **session**: `1793253175918_yeyve.messages.json` (xinqiaoz @ hfeg0plg56, mc=386, 274 msgs)
- **scan keywords**: `pdk:1011;drc:212;calibre:63;.gds:6;pyaether:5` (physical_verify, C-ratio 0.994)
- **size**: 990 KB messages.json (under 2 MB, manageable)
- **domain**: physical_verify (Calibre DRC QA on TVF dummy rule deck)

## Task narrative (user turns, verbatim intent)

- USER#1 (idx=0): "恢复中断的 T1 Dummy QA 会话" — resume a handoff-journal for G7 T1 (hyperbonding) Dummy QA on `calibreDummy.rule` (TVF config, 222 行), 21 项检查, chip 侧 only. Handoff context: P0 env ✅, P1 (检查项 1+2+7+8 头部开关) ✅, P3 (3+10) ✅, P4 (5 chip 数值) ✅.
- USER#5 (idx=49): **"任务：Dummy QA 检查项 9（target layer 确认）"** — the clean produce-task chosen as the case seed. Check that each mask's `_lay`/`_Info` target layer in `calibreDummy.rule` covers the guideline target layer set. Direction "只能多不能少": MISSING (guideline − rule) = FAIL; EXTRA (rule − guideline) = OK.
  - **guideline merged notation**: `"28/485/650;7"` (shared datatype), `"500/502/504;0"`, `"SE1(872;0/19/41)"` (prefix+paren group), `"93/95;0"`.
  - **rule expanded notation**: `set M1Z_lay [list 88_0 88_16 88_24 88_27]` (LAYER_DT), `set AT4_Info [concat $AT4_lay $PGZ_lay]` (concat with $var refs).

## Agent tool-use sequence (after idx=49, 115 tool_uses)

read_files guideline_parsed.json + calibreDummy.rule → editor `scripts/qa_09_target_layer.py` (the gold) → iterate (py_compile, run, fix) across multiple edits at idx 72/117/121/123/228/257. Final gold = `qa_09_target_layer.py` with:
- `expand_guideline_targets()` — regex-based expansion of merged forms (handles `/...;dt`, `PREFIX(...)` strip, single `lay;dt`)
- `parse_rule_vars()` — TCL `set` parser splitting `_lay` (list) vs `_Info` (expr/list)
- `_resolve_expr()` / `_resolve_var()` — recursive resolution of `$var` and `[concat $a $b]`
- `get_mask_targets()` — union of `{mask}_Info` ∪ `{mask}_Info_Extent` ∪ `{mask}_lay`
- `run_qa()` — per-mask MISSING/EXTRA + overall verdict; `main()` with argparse `--rule/--guideline/--out`

## Why this seed → case

- Clean produce-task: one well-defined comparator (rule target set vs guideline target set, with two distinct notations to bridge). Testable end-to-end via subprocess on hidden inputs.
- Real EDA notation complexity (TCL `set`/`[list]`/`[concat $var]` + guideline merged forms) — not a toy.
- xinqiaoz DRC QA family is well-covered but **no existing case targets check item 9 (target layer)**: existing DummyDeck/DummyMeas/DummyQA/DummyQaCliNoConfig/DummyGeoVerify/DummyQaDataPrep/PdkRunsetExplorer cover deck-diag/measure/harness/CLI-no-config/geo-check/data-prep/runset — none is the target-layer set comparison with merged/concat expansion. Novel sub-task.

## B档 synthesized reason

Real `calibreDummy.rule` (222 lines) + `guideline_parsed.json` contain real product mask names / layer numbers / internal PDK structure that should not be shipped into the SUT sandbox. Synthesized small A (5 masks, all PASS, 1 EXTRA) + B (6 masks, 2 MISSING→FAIL, 4 EXTRA→PASS incl. one concat) preserve the real notation patterns (merged `/dt`, `SE1(...)`, `[list L_DT]`, `[concat $var]`) and give full ground-truth control. Cross-input guard (A overall=PASS vs B overall=FAIL) prevents hardcoding.

## Ground truth (computed by gold, verified)

- **visible A** (calibreDummy_A.rule + guideline_A.json): M1Z extra=[90;0], AT4/RDL/SCC/HSP ==, overall PASS, n_fail=0.
- **hidden B** (calibreDummy_B.rule + guideline_B.json): M2Z missing=[90;0] FAIL, HLP missing=[96;0] FAIL, PGZ extra=[15;0] PASS, MT2 extra=[702;0] PASS (concat $MT2_base_lay), BPA extra=[872;41] PASS, RDL extra=[601;0] PASS, overall FAIL, n_fail=2.

## Self-verify

- gold on A → PASS (n_fail=0); gold on B → FAIL (n_fail=2, exact GT).
- check.py on reference gold → 14/14 conditions PASS.
- negative_selftest: fake_empty (cond c), fake_print_expected (cond d), fake_hardcode_b (cond d), core_deleted (cond h) all FAIL; gold PASS. §4.9 (a)(b)(c) covered.
