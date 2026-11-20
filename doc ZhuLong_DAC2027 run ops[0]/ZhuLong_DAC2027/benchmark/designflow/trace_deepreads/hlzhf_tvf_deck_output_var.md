# Deepread: hlzhf — TVF Deck Output Variable Trace

**session**: `1792477592591_hlzhf` · **user**: ellawu · **host**: 10.129.2.14 (hfeg0pkn005) · **mc**: 24
**keywords**: drc:1289;calibre:21;.gds:9;gdsii:4;cmos:4;lvs:2
**date**: 2026-10-20 · **agent**: lead · **msgs**: 38 (2 user turns)

## Trace summary

User uploads a 3169-line / 399KB Calibre TVF/SVRF rule deck `G4C_AA_PG_dummy_fill_for_Logic.rule` (G4C process, auto AA/PG dummy fill for Logic blocks) and asks two things:

- **U#0** (msg[0]): "整理一下这个脚本的flow" — organize the flow of the script.
- **U#22** (msg[22]): "最终结果是哪个变量" — which variable is the final result?

### Assistant flow (msg[1]–msg[37])

- msg[1-20]: reads the deck in ~10 chunks (lines 1-120, 121-250, 251-400, 401-550, 550-700, 701-850, 590-690, 690-780, 850-920, 920-1000, 1000-1100, 1100-1200, 1200-1300, 1320-1400, 1400-1500, 1500-1600, 1600-1720). Maps out: LAYOUT SETUP → LAYER DEFINITIONS (PSUB/NSUB/GATE/DIF_TR) → GATE CLASSIFICATION (1st/2nd gate by gate_len) → BLOCK LAYERS (BLK_poly/BLK_dummy/BLK_diff) → EDGE DETECTION (DIF_OUTER_OP_EDGE_T/B/L/R) → PHASE 1 HORI PG DUMMY (MOS_AA_Insert_Hori_PG, width=0.056) → PHASE 2 VERT PG DUMMY (3 cases: 1st-1st width=0.042 / 2nd-2nd width=0.062 / 1st-2nd mixed width=0.062, each with 6 insert levels insert_1/2/3/4/more/outside) → final merge.
- msg[21]: delivers a full flow document (markdown) with phase diagram + composition description.
- msg[23-36]: after U#22 "最终结果是哪个变量", searches for `PGDummy_FILL_REGION`, `OUTPUT {`, reads tail of file (lines 1200-1720).
- msg[37]: **answers** — final output variable = `PGDummy_FILL_REGION`, OUTPUT block = `DFM RDB GDS "AA_PG_DUM_Logic.gds" PGDummy_FILL_REGION 30 4 PROPERTIES APPEND _auto_pgdm`, composition = `MOS_AA_Insert_Hori_PG ∪ 1st_1st_DIF_OUTER_FILL_PGDummy ∪ 2nd_2nd_DIF_OUTER_FILL_PGDummy ∪ 1st_2nd_DIF_OUTER_FILL_PGDummy`, error checks = ERROR_DUM_space / ERROR_DUM_width.

### Key deck facts (verified by ref parser on full 3169-line deck)

- **OUTPUT block** (line 3161): `OUTPUT { DFM RDB GDS "AA_PG_DUM_Logic.gds" PGDummy_FILL_REGION 30 4 PROPERTIES APPEND _auto_pgdm }`
- **final_output_var**: `PGDummy_FILL_REGION` (line 1890: `SETLAYER PGDummy_FILL_REGION = PGDummy_FILL_REGION_drc3 NOT (AREA PGDummy_FILL_REGION_drc3 < $PG_Dummy_MinArea)`)
- **composition** (line 1877): `SETLAYER PGDummy_FILL_REGION_drc0 = FLATTEN (OR MOS_AA_Insert_Hori_PG 1st_1st_DIF_OUTER_FILL_PGDummy 2nd_2nd_DIF_OUTER_FILL_PGDummy 1st_2nd_DIF_OUTER_FILL_PGDummy)` → 4 vars
- **derivation_chain**: PGDummy_FILL_REGION_drc0 → _drc1 → _drc1_shrink → _drc1_singular → _drc1_singular_shrink → _drc2 → _drc3 → PGDummy_FILL_REGION (ref parser collapses to 5 by _drcN suffix: drc0/drc1/drc2/drc3/final)
- **foreach loops**: 5 (lines 381, 578, 590, 974, 1043), all `foreach GL $gateList`
- **error_checks**: ERROR_DUM_space, ERROR_DUM_width (ERROR_DUM_overBLK commented out)
- **verbatim_blocks**: 13 · **setlayer_count**: 1029

## Case decision (r812)

- **domain**: physical_verify (Calibre DRC deck analysis; consistent with r810 9m82z TvfDeckAnalyzeReport-001)
- **layer**: L1 (offline stdlib parser, no real Calibre run)
- **档**: B (reframe — A档 gold = free-text markdown flow doc + single-string answer, no ≥8 硬断言牙)
- **子型**: calibre-tvf-deck-output-var-tracer
- **distinct from r810**: r810 = 9-section structure extractor (header/versions/drc_env/layer_deriv/tcl_params/drc_select/output_block/layer_map/statistics); r812 = **final-output-variable dataflow tracer** (output_block + final_output_var + OR-composition chain + derivation_chain). Different algorithmic task: r810 extracts static sections; r812 traces the dataflow to the OUTPUT block.
- **distinct from r811**: r811 = pgdummy-flow-static-analyzer for a Python script (5 stages + 4 bugs); r812 = deck-output-var-tracer for a TVF deck (different input language, different output structure).

## Reframe (档 B)

A档 gold = assistant's free-text markdown flow document + the answer string "PGDummy_FILL_REGION". No ≥8 independent hard-assertion teeth (free-text markdown can't be structurally asserted). Reframe = extract the algorithmic core of what the assistant actually did — **parse a TVF deck, locate the OUTPUT block, identify the final output SETLAYER variable, walk back the OR-composition chain, enumerate foreach/error/derivation/verbatim** — into a pure-stdlib dataflow tracer `tvf_deck_output_tracer.py` (CLI `<deck> <out.json>`, 8 top-level keys, sort_keys deterministic output).

## Anti-hardcode (hidden B)

Hidden B = synthesized ST22 process deck (81 lines), all identifiers distinct from A:
- final_output_var: `ST22_PG_DUM_FILL` (vs A `PGDummy_FILL_REGION`)
- gds_filename: `ST22_PG_DUM_Peri.gds` (vs A `AA_PG_DUM_Logic.gds`)
- layer/datatype: 28/7 (vs A 30/4)
- properties_append: `_auto_st22pgdm` (vs A `_auto_pgdm`)
- composition: `[ST22_Hori_PG_Insert, 1st_1st_FILL, 2nd_2nd_FILL, 1st_2nd_FILL]` (vs A `[MOS_AA_Insert_Hori_PG, 1st_1st_DIF_OUTER_FILL_PGDummy, ...]`) — keeps digit-start names to test parser robustness
- foreach_loops: 3 (vs A 5)
- error_checks: `[ERR_DUM_space, ERR_DUM_width]` (ERR_ prefix vs A ERROR_)
- verbatim_blocks: 4 (vs A 13)
- derivation_chain: 4 stages (vs A 5)
- setlayer_count: 13 (vs A 1029)

## Self-verify (all pass)

- ref PASS 16/16 (a-p)
- 4 negatives all FAIL at distinct points: empty→[a], print_only→[c], hardcode_a→[d], core_deleted→[i]
- §4.9 (a)(b)(c) three fake submits all FAIL
- determinism: 2x byte-identical
- ref parser on real A (full 3169-line deck on .75): final=PGDummy_FILL_REGION, composition=4 vars, gds=AA_PG_DUM_Logic.gds L30 DT4 — matches assistant's trace answer
- jsonl roundtrip: test == disk check.py, 17159 bytes, k_rationale=k_check=16
