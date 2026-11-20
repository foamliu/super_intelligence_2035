# kkzh8 — pg_layout merge-relationship audit + file-size anomaly

## trace source
- session: `1793585721814_kkzh8`
- user: `e0014566` @ `10.129.35.82` (hfeg0plg49 cluster)
- match_count: 322 (keywords: virtuoso:475;dbopencellviewbytype:132;cellview:118;dbcreateinst:56;drc:41;aether:22;dbcreaterect...)
- domain: **pg_layout**
- cline messages: 363 (NUUSER 10 substantive turns)

## real user intent (verbatim, A档 trace-faithful)
- **U#0** (flow-driving opener): "read the prompt_powerfill.md and do the job in it." — delegates to a prompt file (the powerfill flow spec). This opener is flow-driving (same e0014566 cluster flagged r696 as prompt_flow/prompt_powerfill flow-driving).
- **U#38** (the real task — selected as A档 prompt): 「请你检查下原始的输入layout: austin_new/test_20260528/layout. 输出的power fill cell: austin_new/test_20260528_auto_pgfill/layout. 以及 将原来的输入layout 和 power fill cell merge 过后的结果：austin_new/test_20260528_powerfill/layout。能帮忙审查下他们之间的关系嘛，我看了下文件的大小，感觉比较奇怪，不太符合预期。」
- **U#144/U#145**: "你的这个修复具有普适性嘛？会不会对于别的layout, 还是会出现各种问题。" (generalization concern)
- **U#147**: "所以你得到的结论是什么？"
- **U#233** (the core anomaly question): 「为啥merge过后新的layout的文件大小比原本的layout还要小。」
- **U#322/U#323**: "continue"

Real intent = **audit the relationship between 3 layouts (input / auto_pgfill / merged powerfill) AND explain a file-size anomaly (merged file_size < input, which is unexpected because merging powerfill cells should grow the layout)**. Real deliverable = verbal review/explanation (analysis/Q&A). Per 2026-11-15 task初心, analysis/Q&A on layouts IS a real user intent and is造-able.

## fixture accessibility
- The real layout paths (`/home/e0014566/austin_new/test_20260528*/`) are NOT accessible from e0031982 identity (the layouts live under a project tree e0031982 cannot read; the trace's pyAether/dbGet tool_results on .75 contain the real cell/layer/bbox/size numbers but the .messages.json rotated during this round).
- The session dir on 10.129.35.82 is `1783585721814_kkzh8` (Jul 9 original); the `1793585721814_kkzh8` (Nov resume) dir was archived mid-round. The candidates_mc10.tsv lists `1793585721814_kkzh8`.
- **Reframe = mock-behavioral** (承 r645-r700 family): fixture is a synthesized textual layout manifest capturing the real task structure (3 layouts with cells/layers/bbox/file_size + the size anomaly), inspired by the real trace intent. This matches the family pattern (r697 PgDummyFillFlowOrganize, r698 ErcRulecheckStatsScan, r699 PgPlacementPlan, r700 PexCharConfigReview).

## reframe — new sub-family `pg-layout-merge-relationship-audit`
- candidate = pure-stdlib `pg_layout_merge_audit.py` that reads a manifest JSON (3 layouts: input/powerfill/merged, each with cells[]/layers[]/bbox/file_size) and emits an audit JSON:
  - `per_layout`: per-layout cell_count / layer_count / bbox_area / file_size
  - `merge_relationship`: added_cells (merged - input) / missing_cells (input - merged) / unexpected_cells (merged - input - powerfill) / shared_input_powerfill / cell lists
  - `size_analysis`: merged_size / input_size / ratio / delta / **anomaly_flag** (merged_size < input_size)
  - `cross_check`: layers_consistent (input∪powerfill layers ⊆ merged layers) / bbox_containment (merged bbox ⊇ input ∧ ⊇ powerfill) / merged_has_all_input_cells
  - `conclusion`: human-readable summary
- **teeth**: set relationships (added/missing/unexpected cells), size comparison + anomaly_flag, layer/bbox cross-check, determinism (sort_keys, 2x byte-identical). All B/B2-disjoint from A.
- distinct vs existing C cases:
  - r699 PgPlacementPlan-001 = PG device list + placement plan (generate placement spec)
  - r697 PgDummyFillFlowOrganize-001 = TVF deck 14-section structural extract
  - r698 ErcRulecheckStatsScan-001 = batch erc.rep tree scan + per-rule aggregate
  - **本例 = 3-layout merge-relationship audit + size-anomaly flag** (set-relationship + size-parity, distinct from placement / deck-extract / batch-scan)

## scenarios (A visible; B/B2 hidden, fully disjoint)
| | A (visible) | B (hidden) | B2 (hidden) |
|---|---|---|---|
| input cells | 7 (INV,NAND2,NOR2,DFF,BUF,LATCH6,MUX2) | 5 (AN2,OR2,XOR2,INVX,DFFR) | 3 (HS1,HS2,HS3) |
| powerfill cells | 2 (PFILL_VDD,PFILL_VSS) | 3 (PG_FILL_A/B/C) | 1 (PF1) |
| merged cells | 7 (input minus LATCH6,MUX2 + 2 PFILL) | 8 (all input + 3 PG_FILL) | 5 (all input + PF1 + UNKNOWN_X) |
| merged file_size | 38000 | 56000 | 19000 |
| input file_size | 52000 | 41000 | 24000 |
| anomaly_flag | True (38000<52000, missing 2 cells) | False (56000>41000, normal) | True (19000<24000, unexpected UNKNOWN_X) |
| added_cells | {PFILL_VDD,PFILL_VSS} | {PG_FILL_A,B,C} | {PF1,UNKNOWN_X} |
| missing_cells | {LATCH6,MUX2} | {} | {} |
| unexpected_cells | {} | {} | {UNKNOWN_X} |

A/B/B2 mutually disjoint in cell names, layer sets, bbox, file sizes, anomaly_flag ⇒ anti-hardcode.

## check() — 18 conditions (a-r), k_rationale == k_check == 18 ≥ 8 GATE PASS
a zip contains script · b py_compile · c B valid JSON · d B 5 top-level keys · e B merged.cell_count==8 · f B merged.file_size==56000 · g B added_cells=={PG_FILL_*} · h B missing=={} · i B anomaly_flag==False · j B ratio==56000/41000 · k B layers_consistent · l B bbox_containment · m B2 valid JSON+5 keys · n B2 merged.cell_count==5 · o B2 unexpected_cells=={UNKNOWN_X} · p B2 anomaly_flag==True · q B2 merged.file_size==19000 · r determinism 2x byte-identical

## self-verify (2026-11-17 09:10)
- gold reference_submit.zip: check() PASS ✓ (B + B2)
- reference on A: anomaly True + missing {LATCH6,MUX2} + added {PFILL_VDD,PFILL_VSS} ✓
- 4 negatives all FAIL, 4 distinct first-fail tags (empty_shell→c, only_print_A→e, always_normal→g, always_anomaly→i) ✓
- §4.9 three fakes: (a) empty shell → c FAIL · (b) only print A → e FAIL · (c) delete core logic (always_normal) → g FAIL ✓
- determinism: 2x md5 e1e03d9066c2851add88025dde490806 identical ✓
- anti-hardcode: A∩B∩B2 cell/layer/bbox/size/anomaly all disjoint ✓
- jsonl test field round-trip: extract → run reference_submit.zip → CHECK PASS ✓
- k_rationale == k_check == 18 ≥ 8 GATE PASS ✓

## ledger
- claimed r701 (e0014566/10.129.35.82 mc322 pg_layout) → marked case EDA-Eval-DesignFlow-PgLayoutMergeAudit-001
- covered 434 → 435; pg_layout 43 → 44
- jsonl_C 435 → 436
