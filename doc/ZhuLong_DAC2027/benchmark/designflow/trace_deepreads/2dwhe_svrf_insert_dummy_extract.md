# trace_deepread: 2dwhe (ellawu@hfeg0plg79) — SVRF dummy-fill rule deck Q&A

- **trace**: 1794993350192_2dwhe, ellawu @ hfeg0plg79 (10.129.8.122), mc=30, kw drc:2064/calibre:87/.gds:17/skipper:10 — clean physical_verify.
- **size**: 67 msgs / 1.19 MB / 1 attached file `G4C_AA_PG_dummy_fill_for_Logic.rule` (399318 B / 3170 lines).
- **user turns** (16 real user_input, single-session Q&A about a Calibre TVF/SVRF dummy-fill rule deck):
  - U#1「insert vert不同数量dummy的异同点」(+attached .rule)
  - U#3「${GL}_${GL}_DIF_OUTER_insert_1_PGDummy_t总共有几种」
  - U#4「${GL}_${GL}_DIF_OUTER_insert_1_PGDummy_t把三种命令完整写出来」
  - U#6-7 variable-naming questions (`insert_2_1st_PGDummy_Space_Region_2` vs `2_2nd_PGDummy_Space_Region`)
  - U#8「这个GL语法是什么」(GL = Tcl foreach loop var, deck is TVF)
  - U#9-16 SETLAYER / DFM PROPERTY SELECT SECONDARY / OVERLAP ABUT / LENGTH / MAX / `-=(...)` / `expr` vs `$` semantics Q&A
- **assistant gold chain**: read_files full deck (700-line truncated upload + 3169-line full deck on Desktop) → editor `find_insert1_search.py` (search `1st_1st_/2nd_2nd_/1st_2nd_` definitions across Desktop rule files) → run_approved_command → located full deck `/home/ellawu/Desktop/G4C_AA_PG_dummy_fill_for_Logic.rule` (3169 lines) → final answer (idx=44):
  - **three commands** verbatim:
    - ① `1st_1st_DIF_OUTER_insert_1_PGDummy_t` (from `foreach GL {1st 2nd}` template L596, GL=1st) `= EXT 1st_DIF_OUTER_Extend_EDGE (DFM COPY 1st_DIF_OUTER_Extend_EDGE) >= $insert_1_1st_PGDummy_Space_Region < $insert_2_1st_PGDummy_Space_Region ABUT < 90 EXCLUDE SHIELDED OPPOSITE REGION`
    - ② `2nd_2nd_DIF_OUTER_insert_1_PGDummy_t` (template L596, GL=2nd) `= EXT 2nd_DIF_OUTER_Extend_EDGE (DFM COPY 2nd_DIF_OUTER_Extend_EDGE) >= $insert_1_2nd_PGDummy_Space_Region < $insert_2_2nd_PGDummy_Space_Region ABUT < 90 EXCLUDE SHIELDED OPPOSITE REGION`
    - ③ `1st_2nd_DIF_OUTER_insert_1_PGDummy_t` (concrete handwritten block L1119) `= EXT 1st_DIF_OUTER_Extend_EDGE 2nd_DIF_OUTER_Extend_EDGE >= $insert_1_1st_PGDummy_Space_Region_2 < $insert_2_1st_PGDummy_Space_Region_2 ABUT < 90 EXCLUDE SHIELDED OPPOSITE REGION`
  - threshold values: 1st_1st 0.326/0.448, 2nd_2nd 0.386/0.528, 1st_2nd 0.346/0.468.
  - "三种" = 1st_1st + 2nd_2nd (foreach template expansion) + 1st_2nd (separate handwritten cross-gate block).
- **reframe decision**: trace-faithful produce-task reframe — `svrf_insert_dummy_extract.py <rule_file> <pattern> [-o out.json]`. Grounding: the real deck is TVF with `foreach GL` Tcl expansion (the "three" requires loop expansion). Reframe ships a **pre-expanded** SVRF deck (foreach already expanded to concrete `1st_1st_/2nd_2nd_` names + handwritten `1st_2nd_` block) so the analyzer does pure pattern-match SETLAYER extraction (no Tcl parsing). Captures U#3 (count) + U#4 (write commands) + structural dependency graph (U#1 "异同点" → derived layers referencing the trigger). Single-line SETLAYER (confirmed: each SETLAYER on its own line in real deck). Judge = exact-field-match (count/names/lines/command-text/derived) + anti-hardcode A guard + 3-seed + anti-cheat B literals.
- **intent audit**: keep — ellawu真实意图(理解 SVRF dummy-fill deck 中 `*_DIF_OUTER_insert_1_PGDummy_t` 的种类数 + 写出三种命令 + 理解衍生层/变量语义)完整保留; reframe 是 grounding (TVF foreach 不可沙盒 + 3169 行真实 deck → 小合成 pre-expanded fixture + JSON 结构化提取, 离线化) 非加难; 用户原话逐字入 prompt; 11-15 reaudit 后 analysis-Q&A 类合法.
