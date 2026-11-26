# Deepread — sid 1790130179096_bmhid (lizwen, hfeg0plg16, mc=357)

- **Host**: 172.16.8.192 (hfeg0plg16), user lizwen
- **Session**: `/home/lizwen/.cline/data/sessions/1790130179096_bmhid/1790130179096_bmhid.messages.json` (1.71MB, 435 msgs, 2026-09-23)
- **Domain**: layout_aether (DRC testpattern generation in OA via pyAether)
- **Real tool profile**: 256 cellview + 182 pyAether + 45 calibre + 16 schematic + 12 dbGet + 11 `"lang":"pyAether"`

## Real task & artifact

User (lizwen, PDK QA / DRC pattern engineer) built a reusable Aether skill **`drc_pattern_gen.py`** that, given a DRC rule query (rule id or wildcard, case-insensitive), reads `sample_drc_deck/specs/test_deck_new` + `config/drc_rules_spec.json` (49 rules, each with `pattern_constraints.pass_case`/`fail_case` + `coordinates_hint`) and draws PASS/FAIL testpattern `.oa` data into an OA library `DRCPatLib`, with layer resolution against `derived_layer_map.json` + techfile.tf + display.drf.

Key real script (544 lines) at `/home/lizwen/.cline/scripts/data/drc_pattern_gen.py`. Core layout-composition math (single-cell mode, the user's main use case):

1. Matched rules split into **large** (`_max_h >= 50.0` um) and **small** groups.
2. Two columns: large left at `x=0`; small right at `x = max_large_pair_width + 30` (pair_width = pass_w + 10 + fail_w). If no large, small column at `x=0`.
3. Each rule = one row: PASS drawn left, FAIL right (COL_GAP=10).
4. Shapes drawn **downward** from per-rule `y_top` (y decreases): bbox = `(x_offset + (x1-min_x), y_top-(y2-min_y)) .. (x_offset+(x2-min_x), y_top-(y1-min_y))`.
5. Auto font: `sub_label_h = max(2.0, min(12.0, row_h*0.08))`; `rule_label_h = sub_label_h*1.5`.
6. Proportional gaps: `sub_label_gap = max(5.0, row_h*0.10)`; `rule_label_gap = max(5.0, row_h*0.10)`.
7. `label_space = sub_label_gap + sub_label_h + rule_label_gap + rule_label_h`; `row_gap = max(15.0, label_space*1.5)`.
8. `y_cursor` advances by `-(row_h + row_gap)` after each rule (uses the CURRENT rule's row_gap — so a small rule followed by a large rule can let the large rule's labels overlap the small rule's shapes; this is the real bug-prone behavior the user complained about in UI#5/UI#7).
9. Labels: PASS/FAIL sub-labels centered above each pattern (`x_offset + width/2`, `y_top + sub_label_gap + sub_label_h/2`); rule name centered above the PASS/FAIL pair.
10. Layer resolution (`resolve_layer`): `NON_LAYER_NAMES` (Rect1/Rect2/...) → rule's primary layer; `LAYER_SUB` overrides (ESD_ALL/NMOSCAP/CLAMP → None = skip; NTR→AT4; NGATE→PG; M1NET→M1); else physical layer (`_drawing` suffix stripped).

## User intent evolution (UI#0..7, all `<user_input mode="act">`)

- UI#0: skill spec for "DRC Testpattern Generator" (meta-skill creation; `pythone drc_pattern_gen.py "QUERY" [out]`).
- UI#1: "每次搜索 .oa 数据都存放在一个 .oa 里，pass 和 fail 放在一起一行作对比，名字按搜索 rule 命名…搜索第二次不覆盖第一个，同样名字要更新覆盖" → single-cell PASS/FAIL side-by-side, update-on-same-name semantics.
- UI#2/UI#3: "techfile.tf / TECHLIB.layermap 这两没起作用，aether 里层显示不对，另外其他人使用我的 skill 要提供哪些文件" → layer display dependency + skill portability.
- UI#4: "rule 名字和 pass/fail 标题错开点不要重叠…别人使用 skill 时这些输入文件要 copy 过去吗" → spacing/label overlap + dependency packaging.
- UI#5: "不同 rule 的 pattern 位于同一个 .oa 里，距离拉开不要重叠" → inter-rule spacing.
- UI#6: "根据 pattern 大小自动变化间距，保证一条 rule 对应一对 pass/fail，rule name 在这对 pattern 中间上面…字体大小 pattern 配合度合理…skill 如何维护" → auto-spacing + auto-font + maintainability.
- UI#7: "排版方面 rule name 和 pass/fail 依旧太近…space 再大一些，DNW_W_000_00 DNW_W_007_00 这些依旧在大图形里边" → continued spacing tuning.

## A-档 vs B-档 decision

UI#0 is a meta-skill spec (not a pure need — it pre-specifies the script interface); UI#1-7 are iterative refinement of a stateful skill across a long session, with no single byte-faithful accepted final artifact (the user never says "done"; UI#7 is still complaining). The real deliverable (the 544-line script) evolved through many turns and depends on a 4.5MB OA techfile + private PDK files (`techfile.tf`, `display.drf`) that are not sandbox-reproducible and not accessible to e0031982 on 172.16.8.192. → **A-档 disqualified → B-档 synthesized, L1-boundary**: take the real `drc_pattern_gen.py` layout-composition math as the gold, make the deliverable an offline placement planner (`drc_pat_planner.py`) that, given a rule spec JSON, emits the placement plan JSON (columns, per-rule rows, shapes, labels, gaps, font sizes) — fully offline Python3, judgment needs no live Aether/OA.

## Inputs

- **A** (`assets/.../rules_A.json`): 6 real rules extracted from `drc_rules_spec.json` (2 large: DNW_S_001_00 h=209.30, PG_Wmax_066_00 h=50.0; 4 small: DNW_W_000_00 h=20, DNW_W_007_00 h=10, NCH_W_000_00_c h=3, NCH_W_000_00_p h=3). Real `coordinates_hint` verbatim. small_col_x = 345+30 = 375.
- **hidden B** (`reference/.../hidden/rules_B.json`): 6 synthesized rules, structure differs (3 large: BIG_W_300 h=300 [font clamp max=12], BOUND_050 h=50 [boundary ≥50], NW_S_BIG h=370 [Rect1/Rect2 + ESD_ALL skip]; 3 small: M2_W_100 h=4, MT_SP_005 h=0.4 [font clamp min=2], PC_ENC_020 h=12). small_col_x = 430+30 = 460. Tests font clamps, boundary, layer resolution, skip.
- **hidden B2** (`hidden/rules_B2.json`): 2 small rules, no large → small_col_x must be 0 (branch coverage).

## Distinctness vs prior shard-C cases

Prior layout_aether cases: WheelZoom (bindkey), M2PathLayout (path draw), WireWatermark (watermark), AddCellPin/CellPin (pin), StrongARMComp (comparator), HierJump (hier jump), FindCircuitByPath (schematic path), PortPropagate (port), ListInstCV (list inst), FreezeMaker (freeze), DRCPatGen/DRCPatPlan/DRCPatGen002 (earlier DRC pattern gen variants in other shards?). This case = **DRC testpattern PASS/FAIL pair placement planner with auto-font/auto-spacing/large-small column split + SVRF layer resolution** — placement-composition math + layer resolution, distinct topic/assertions.

## Self-verification

- ref `drc_pat_planner.py` → check.py PASS (all 15 assertions).
- 4 negatives (empty_stub / print_only / no_split_logic / hardcoded_A) → all FAIL (negative_selftest NEG_RC=0).
- §4.9 (a) empty shell (b) print-only (c) core-deleted → all FAIL.
- Local pure Python3, no live Aether needed.
