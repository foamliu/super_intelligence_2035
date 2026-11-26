# Deepread — 1792463051213_e2nuq (ellawu / hfeg0pkn005)

- **slug**: 1792463051213_e2nuq
- **user/host**: ellawu / hfeg0pkn005
- **mc**: 36 (drc:2419; calibre:145; aether:116; .gds:30; gdsii:7)
- **session_msgs**: 26 (small, clean)
- **messages.json size**: 1,188,030 bytes (1.18 MB)
- **attached file**: G5_AA_PG_dummy_fill_for_Logic.rule (2106 lines, Calibre TVF DFM deck, CXMT G5 AA/PG dummy for Logic cells)
- **domain**: physical_verify (Calibre TVF dummy-fill rule deck analysis)
- **status**: completed (3 user turns, all answered)

## User turns (verbatim, A-faithful seed candidates)

- **USER#1 (idx 0)**: 「总结这个flow」 + 附件 G5_AA_PG_dummy_fill_for_Logic.rule
  - *Produce-task?* YES — asks for a flow summary of the attached rule deck.
- **USER#2 (idx 10)**: 「这个脚本是怎么处理BLK和dummy之间关系的」
  - *Produce-task?* YES — asks how the script handles BLK vs dummy relationship.
- **USER#3 (idx 22)**: 「被BLK截短的dummy怎么处理」
  - *Produce-task?* YES — asks how BLK-truncated dummy is handled.
  - *Per A-faithful rule*: USER#3 starts to point at root-cause ("被BLK截短") but does NOT give a fix — still a valid A-faithful task statement (asks "怎么处理" = how is it handled, not "fix it").

All 3 turns are "提出需求/表达目标" type (not "已指出根因或给出修复方案"). All eligible as A-faithful seeds.

## Agent tool chain (6 tool calls, all read_files / search_codebase)

1. read_files rule deck lines 1-500 (4 chunks)
2. read_files rule deck lines 500-1100
3. read_files rule deck lines 1400-2150
4. read_files rule deck lines 2000-2150
5. → text response: "G5 AA/PG Dummy Fill for Logic — Flow 总结" (TVF format, AA/PG dummy 自动插入, vert FILL + hori FILL_H)
6. USER#2 → search_codebase (BLK_diff, BLK = OR, NOT BLK, ...)
7. read_files BLK definition sections (lines 285-420, 570-650, 880-960)
8. search_codebase (BLK_for_hori, NOT BLK_for_hori, PGDummy_FILL_REGION, ...)
9. read_files lines 435-445, 495-505
10. → text response: "BLK 与 Dummy 之间的关系处理详解" (两套 BLK 体系)
11. USER#3 → read_files lines 937-948, 680-720
12. → text response: "被 BLK 截短的 Dummy 会经历什么" (6-layer filter pipeline)

## Key technical findings (ground truth for case synthesis)

### Two BLK systems (lines 301-324)

```tvf
SETLAYER BLK_poly = SIZE PG_POLY BY $PG_Dummy_MinSpace           // line 301
SETLAYER BLK_dummy = SIZE PG_DUMMY BY $PG_Dummy_MinSpace         // line 303
SETLAYER BLK_diff = OR (SIZE SUB2 ...) (SIZE SUB1_1 ...) ...      // line 319
SETLAYER BLK_diff_for_hori = SIZE DIF_ALL BY $AT4_PG_Dummy_Space // line 320
SETLAYER BLK = OR BLK_diff BLK_dummy BLK_poly                    // line 323 (for vert)
SETLAYER BLK_for_hori = OR BLK_diff_for_hori BLK_dummy BLK_poly  // line 324 (for hori)
```

- **BLK** (vert): 3 components BLK_diff + BLK_dummy + BLK_poly
- **BLK_for_hori** (hori): 3 components BLK_diff_for_hori + BLK_dummy + BLK_poly
- Differs by ONE component: BLK_diff (vert) vs BLK_diff_for_hori (hori); BLK_dummy + BLK_poly shared.

### 5 vertical PG dummy fills (FILL_1..4 + FILL_more, lines 917-1181)

Each fill follows the same 6-stage post-clip filter pipeline (truncated-dummy fate):

```
drc0 = candidate region (OR ..._edge_RL ..._edge_TB)
drc1 = drc0 NOT (OR BLK (SIZE (OR FILL_prev... LAYER_B) BY $MinSpace))   # NOT-CLIP against BLK + accumulated dummies
drc2 = SIZE drc1 UNDEROVER BY $VertWidth/2 - $GRID                       # SIZE (geometry resize)
drc3 = DFM JOGCLEAN drc2 JOGX $GridStep JOGY $GridStep                   # JOGCLEAN (jog cleaning)
drc4 = drc3 NOT INTERACT (OR RLESD_mark0 DEVTR_mark19 ...)               # NOT-INTERACT (remove bad marks)
drc5 = drc4 NOT (AREA drc4 < $MinArea)                                   # NOT-AREA (remove tiny fragments)
final = drc5 WITH EDGE (LENGTH (LENGTH drc5 > $VertWidth) >= $MinLength) # WITH-EDGE-LENGTH (length filter)
```

- FILL_1 drc1 clips against BLK + LAYER_B
- FILL_2 drc1 clips against BLK + (OR FILL_1 LAYER_B) — accumulates FILL_1
- FILL_3 drc1 clips against BLK + (OR FILL_1 FILL_2 LAYER_B) — accumulates FILL_1, FILL_2
- FILL_4 drc1 clips against BLK + (OR FILL_1 FILL_2 FILL_3 LAYER_B) — accumulates FILL_1..3

### 1 horizontal PG dummy (FILL_H, uses BLK_for_hori)

```
FILL_H_drc1 = FILL_H_drc0 NOT (OR BLK_for_hori (SIZE LAYER_B BY $MinSpace))  # uses BLK_for_hori, NOT BLK
... same 6-stage pipeline but with HoriWidth instead of VertWidth ...
```

### Summary (real deck)
- n_blk_systems = 2 (BLK, BLK_for_hori)
- n_fills = 5 (FILL_1, FILL_2, FILL_3, FILL_4, FILL_H) [FILL_more commented out per line 1087]
- n_vert_fills = 4, n_hori_fills = 1
- fills_per_blk_system: BLK=4, BLK_for_hori=1
- n_filter_stages_per_fill = 6 (drc1..final)
- filter stage op_type sequence: [NOT-CLIP, SIZE, JOGCLEAN, NOT-INTERACT, NOT-AREA, WITH-EDGE-LENGTH]

## Case synthesis decision

- **Track**: B-synthesized (not A-faithful). Reason: real 2106-line rule deck contains real CXMT G5 PDK layer names (PG_POLY, AA, SUB, AT4, PG_DUMMY, PG_NCH, PG_PCH, etc.) + real process parameters — cannot be attached to SUT sandbox as-is. Synthesized small A (3 vert + 1 hori) and B (4 vert + 1 hori) decks preserve the real TVF topology (SETLAYER / OR composite / NOT(OR BLK ...) clip / SIZE UNDEROVER / DFM JOGCLEAN / NOT INTERACT / NOT (AREA) / WITH EDGE LENGTH) with fully-controlled ground truth and synthetic layer names.
- **Gold**: blk_dummy_clip_extract.py — regex-based TVF parser extracting BLK systems, fills, clip expressions, 6-stage filter pipeline op_types, and summary stats → JSON.
- **Cross-input guard**: A n_fills=4 (3 vert + 1 hori) vs B n_fills=5 (4 vert + 1 hori); A has FILL_3 but no FILL_4 → prevents hardcoding B.
- **Distinct from r394 DummyFillCoverageAnalyzer**: r394 computes coverage % from rule deck geometry (build-tool, different angle). This case extracts BLK-dummy CLIP STRUCTURE (which BLK system gates each fill + the 6-stage post-clip filter pipeline) — different sub-topic, different gold logic, different JSON schema.

## Case ID
EDA-Eval-DesignFlow-BlkDummyClipPipelineExtract-001 (physical_verify, L1, B-synthesized, k=14 a-n)
