# Deepread: 1792497033564_goryy (ellawu @ hfeg0plg76, mc=136)

## Session overview
- User: ellawu, host: hfeg0plg76, session: 1792497033564_goryy
- mc=136, domain: pg_layout (Calibre TVF PG dummy fill)
- ~30+ user turns, all asking to explain specific SETLAYER lines from a Calibre TVF DRC deck
- Deck file: G4C_AA_PG_dummy_fill_for_Logic.rule (3169 lines, attached as upload)

## Key user turns (verbatim)
1. "SETLAYER 1st_PG_DUMMY_s1 = PG_DUMMY WITH WIDTH == $1st_PG_Dummy_Vert_Width 解释这句"
2. "这个脚本生成的垂直的dummy宽度为0.062的长度不一样原因出在哪里"
3. "STRIPE 2nd_PG_Dummy_Vert_Width PGDummy_PGDummy_Space VERTICAL 是什么意思"
4. "这个脚本的flow"
5. "梳理一下G4脚本" (summarize the G4 script)
6. Various "SETLAYER ... 这句话的意思" questions about specific constructs

## Deck content highlights
- Calibre TVF deck for auto-adding AA/PG dummy for G4C block cells
- LAYOUT PRIMARY "MatBlock_9X5_2", LAYOUT SYSTEM GDSII
- Tcl variables: 1st_PG_Dummy_Vert_Width=0.042, 2nd_PG_Dummy_Vert_Width=0.062, PG_Dummy_Hori_Width=0.056
- SETLAYER constructs using WITH WIDTH == $<var> to filter PG_DUMMY by width
- 1st_PG_DUMMY_s1/s2/s3 sub-step chain (WITH WIDTH may cut polygons → s2/s3 fix)
- 2nd_PG_DUMMY = PG_DUMMY WITH WIDTH == $2nd_PG_Dummy_Vert_Width (no substeps)

## Case synthesis (TvfSetlayerExpl-001)
- A档 faithful: verbatim first user turn as task statement
- Generalized: build tvf_setlayer_analyzer.py that parses any SETLAYER construct from a TVF deck
- Output: JSON with command/output_layer/source_layer/filter_type/filter_variable/filter_value/has_substeps/deck_type/layout_primary
- Hidden B: same structure, different values (0.038, Block_7X3_1)
- 12 check conditions (a-l): zip/compile/run/JSON + 9 field validations (2 dynamic: filter_value + layout_primary)
- 3 negatives: hardcode_a (hardcodes A values), print_expected (no deck reading), empty_shell
- §4.9 fakes: empty shell / print-expected / deleted-core all FAIL
- Reference PASS, all negatives FAIL

## Coverage impact
- pg_layout: 37 → 38 (+1)
- Total: 285 → 286 cases
