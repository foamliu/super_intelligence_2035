# Deepread: 1794636165058_j8uux (xxchen @ 10.129.2.10 / hfeg0pkn001)

- **mc**: 468, keywords: drc:2627; .gds:297; pdk:6; dbcreatepath:4
- **domain**: physical_verify (DRC pattern tool development)
- **trace**: 2.2MB, 350 msgs, 2026-11-14
- **session_file**: 1794636165058_j8uux.messages.json

## User intent (real task)

xxchen is developing a "QA Pattern Tool" that generates DRC test patterns (good/bad cells)
for Calibre DRC rules. In this session, the user wants to implement a **NOT virtual-layer**
parsing mechanism: the VIRLAYER definition `PWr boundry-NW,AVT;ARRAY` should parse into
TWO NOT-group entries, where PW is computed as `boundry NOT (NW or AVT)`.

Key user directives:
- **USER#50**: VIRLAYER definition changed to `PWr boundry-NW,AVT;ARRAY`; boundry is
  special layer (bordLayer 4002;51); real PW = boundry - NW/AVT (complement region)
- **USER#57**: Concern about NOT shape (two rectangles → boundry with two holes)
- **USER#59**: Space semantics already defined in pattern files; NOT is separate final-stage
- **USER#61** (CORE): "VIRTUAL解析错了：- = NOT。boundry-NW,AVT;ARRAY → 两个 NOT 组
  {sub:NW}、{sub:AVT;ARRAY}。注意 这里也是符合 layer;purpose 这种描述规则的。
  finalize阶段，realPW 上面就是只有 boundry_rect 和（NW 或 AVT;ARRAY）层，
  不需要绘制PW;drawing层。"
- **USER#63**: NOT mode uses solid boundry_rect instead of thin border frame
- **USER#83**: "没有其他要修改的了，开始东西修改吧。" (start implementing)

## Assistant tool chain

1. Read AGENTS.md, PROJECT.md, existing virlayer_manager.py, cell_builder.py, space_var.py
2. Wrote design doc `2026-11-14-space_var-not-boundry-design.md`
3. Edited `virlayer_manager.py`: added `boundry_not` field to VirlayerEntry,
   `_build_boundry_not_entries()`, `_expand_recursive` checks `boundry-` prefix
4. Edited `cell_builder.py`: NOT entry effective layer = sub physical layer,
   l1_groups 4-tuple with l1_not
5. Edited `space_var.py`: NOT mode `draw_border` draws solid boundry_rect,
   `_copy_scratch` for 0;0 temp layer
6. Created test `test_not_parse.py`, ran compile checks, all pass
7. Updated `update_history.md`, `PROJECT.md`, `tasks/todo.md`

## Gold standard (test output USER#113)

```
virlayers keys have PWr: True
ENTRY main='' and=[] boundry_not={'base': 'boundry', 'sub': 'NW', 'sub_spec': None} display=boundry-NW
ENTRY main='' and=[] boundry_not={'base': 'boundry', 'sub': 'AVT;ARRAY', 'sub_spec': None} display=boundry-AVT;ARRAY
PACT main='AT4;PCH' and=['PSD'] boundry_not=None
PWx main='BORD;drawing' boundry_not=None display=BORD;drawing
```

## NOT dialect parsing rules (from design doc + code)

1. `boundry-` prefix triggers NOT parsing (bare `boundry` does NOT)
2. Strip `boundry-` → subtract-list, split on `,` → per-sub layer spec
3. Each sub obeys `layer;purpose` rule: `NW` = `NW;drawing`, `AVT;ARRAY` = layer AVT purpose ARRAY
4. `;` is layer;purpose separator, NOT a group-layout directive
5. Each sub → one NOT variant entry: `boundry_not = {"base": "boundry", "sub": "<str>", "sub_spec": None}`
6. main_layer is EMPTY for NOT entries; display_name = `boundry-<sub>`
7. Normal expressions (`AT4;PCH&PSD`) unaffected: main + and_layers, boundry_not=None
8. Must distinguish from existing `-` offset meaning (e.g. `NSD-0.1` = and-layer expansion)

## Case plan: VirlayerNotParse-001 (B档 synthesized, pure Python)

- **Task**: Write `virlayer_not_parser.py` that parses VIRLAYER config definitions
  including the NOT dialect into structured VirlayerEntry objects
- **Input A** (visible): config with VIRLAYER defs including `PWr boundry-NW,AVT;ARRAY`
- **Hidden B**: different config with different NOT expressions (3 subs, single sub, etc.)
- **check()**: 12 assertions on B output (NOT entry count, sub values, display names,
  normal expr unaffected, `;` not group separator, determinism, empty handling, bare boundry)
- **negatives**: empty stub, print-only, deleted-core
