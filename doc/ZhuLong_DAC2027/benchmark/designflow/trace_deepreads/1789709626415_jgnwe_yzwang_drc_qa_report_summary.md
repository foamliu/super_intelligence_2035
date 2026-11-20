# trace_deepread: 1789709626415_jgnwe / yzwang / DRC QA report summarization

- **session**: `1789709626415_jgnwe.messages.json` (yzwang @ hfeg0pkn001, mc=238, 162 msgs)
- **scan keywords**: `drc:1124;pdk:199;calibre:19;rtl:16` (physical_verify, C-ratio high)
- **domain**: physical_verify (DRC QA report post-run summarization)
- **selection round**: r394 (pg_layout priority pivot → all pg_layout candidates
  keyword false-positive or near-dup → fallback to physical_verify fresh)

## Task narrative

yzwang runs DRC QA on a chip block and obtains a `.report` file in a 3-part
format:

1. **metadata block** — `key: value` lines (process / product / run_id /
   calibre_version / deck / timestamp / overall_result ...).
2. **checkItem summary table** — one row per QA checkItem with id / name /
   total / pass / fail / result columns.
3. **reST grid rule table** — the detailed rule-level table: columns
   `Rule ID | Description | Category | Pass | Fail | Result`, with reST grid
   separators (`====`), and **2-row spans** where a `.. _c:: CATEGORY` header
   row precedes its member rule rows (the `_c::` row has empty Rule ID /
   Description and a Category cell; the `_p::` per-rule rows below carry the
   actual rule data). The `_c::` / `_p::` markers + the leading blank Rule ID
   cell are the span signals.

The user wants a programmatic summary: parse the 3-part report → emit a JSON
summary (metadata + checkItem summary + per-category pass/fail counts + overall
result) AND an HTML report rendering the same.

## Why this seed → case

- **Clean produce-task**: single well-defined transform (report text → JSON +
  HTML), fully text I/O, no EDA bridge / live Calibre / GUI dependency.
- **Self-contained**: input is a static `.report` file, output is static JSON +
  HTML — ideal for SUT sandbox (no `.gds` / live cellview / product PDK needed).
- **Real format complexity**: the reST grid `_c::` / `_p::` 2-row span pattern
  is non-trivial to parse (a naive row-splitter over-counts categories), so
  the task discriminates real parsers from naive ones.
- **Novel sub-task**: existing Qa-prefixed C cases cover QA plan / diag /
  diff / merge / width / pattern / cell-rule-label / PDK module / cli-config /
  data-prep / gate-netlist / tb-gen / lib-cell-build — **none is a
  single-report → (JSON summary + HTML) transform**. yzwang is a new C-domain
  user (first case).

## B档 synthesized reason

The real `.report` from yzwang's trace contains real product / process /
rule-id strings (TVF / DTV process names, real DRC rule ids) that should not
ship into the SUT sandbox. Synthesized small A + B reports preserve the 3-part
format topology (metadata `key: value`, checkItem table, reST grid with
`_c::`/`_p::` 2-row spans) and give full ground-truth control. Cross-input
guard (A: 18 rules / 11 pass / 7 fail / 6 categories / TVF1 vs B: 24 rules /
16 pass / 8 fail / 7 categories / DTV2) prevents hardcoding — a candidate that
dumps the B expected JSON verbatim fails the A cross-guard.

## Ground truth (computed by gold, verified)

- **visible A** (`drc_qa_report_A.report`): process=TVF1, product=CHIP_A,
  6 checkItems (5 pass / 1 fail), 18 rules / 11 pass / 7 fail across 6
  categories (PASS_S 3/1, PG_F 1/2, PG_L 2/1, PMR_ENC 0/2, PMR_F 3/0,
  PC1_F 2/1), overall=fail.
- **hidden B** (`drc_qa_report_B.report`): process=DTV2, product=CHIP_B,
  7 checkItems (5 pass / 2 fail), 24 rules / 16 pass / 8 fail across 7
  categories (PASS_S 5/0, PG_EXT 3/0, PG_L 2/2, PMR_S 1/2, PMR_W 0/2,
  PSD_S 3/1, PCH_F 2/1), overall=fail.

## Gold (drc_qa_report_summary.py)

- `parse_metadata(text)` — `key: value` block up to blank line.
- `parse_checkitems(text)` — table after `CheckItem Summary` header.
- `parse_rule_table(text)` — reST grid parser: skip `====` separators +
  `_c::` category-span rows (Rule ID cell empty) + collect `_p::` per-rule
  rows; categorize by the most-recent `_c::` category.
- `categorize(rules)` — group by category, count pass/fail.
- `summarize(report)` — assemble metadata + checkitems + categories + overall.
- `generate_html(summary)` — render HTML.
- `main()` — argparse `--report / --out-json / --out-html`.

## check.py (k=14 a-n, exceeds ≥8 gate)

- a zip single .py | b py_compile | c AST ≥5 core funcs | d argparse
  --report/--out-json/--out-html | e run B exit0 + valid JSON | f B meta
  process=DTV2 product=CHIP_B | g B checkitem 7/5/2 | h B rule 24/16/8 |
  i B categories PG_L 2/2 PMR_W 0/2 PSD_S 3/1 | j B overall=fail | k B HTML
  has DTV2/CHIP_B/PMR_W | l cross-guard A rule 18/11/7 | m A process=TVF1 |
  n A checkitem=6 + A has PMR_ENC.
- 2 subprocess real-run conditions (cond e hidden B + cond l/m/n visible A
  cross-guard).

## Self-verify

- gold on A → 18/11/7 PASS, process TVF1, checkitem 6/5/1 ✓
- gold on B → 24/16/8 PASS, process DTV2, checkitem 7/5/2 ✓
- check.py ref self-test 14/14 PASS ✓
- §4.9 three-fake-submit: fake_empty (fail b/c/e) / fake_print_expected (fail l)
  / core_deleted (fail h/i) — all 3 covered.
- 4th neg fake_hardcode_b (fail l cross-guard) — covered.
- negative_selftest 4/4 FAIL + gold PASS ✓
- k_rationale = k_check = 14 ≥ 8 ✓
