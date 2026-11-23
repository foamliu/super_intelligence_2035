# trace_deepread: 1794829326520_ynfsl (xxchen@hfeg0plg18, mc=352, physical_verify)

- host: hfeg0plg18 (10.129.8.163 via ssh as e0031982), user xxchen
- session: `/home/xxchen/.cline/data/sessions/1794829326520_ynfsl/1794829326520_ynfsl.messages.json` (1.26 MB, 213 msgs, 95 assistant)
- keywords: drc:920; .gds:141; rtl:15; analog:9; pex:5; pdk:2; dbcreatelabel:2; pyaether:1
- tool profile counts: editor x41, read_files x36, run_approved_command x22, list_allowed_files x10
- workspace root: `/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/`

## User intent (verbatim, MSG 1 & MSG 111)

**MSG 1 (space):**
> 优化function:  space
> 1） 当前的space 额外增加一个参数 CheckCorner False，过滤掉corner对 line/corner的情况，只查有opposite run length的情况。
> QACELL CoreM0C_S_003_00    space             M0Ca->M0C;markcore      0.27     {CheckCorner False}

**MSG 111 (enclose):**
> 优化function:  enclose
> QACELL CoreM0C_ENC_004_00_c  enclose  M0C_FINAL_CORE->PC  0  {layer1width 1.0} {layer1length 3.0} {layer2width 0.08} {layer2length 0.104} {auxRegion CORE}
> 当前rule value为0 时 有些pattern不合适了，需要进行过滤。当value <= 0 时只保留和value相关的pattern。

## Assistant tool chain (space task)

1. Listed space cells in QA.gds via gdspy (`_list_space_cells.py`).
2. Wrote design spec `docs/superpowers/specs/2026-11-16-space-checkCorner-design.md`.
3. Edited `QA_Pattern_tool/function/space/simple/space.py` — added `CheckCorner` option parsing (default False), stored `self.check_corner`.
4. Per-pattern gate edits (the core change): in `good_pattern/3/negative_prl.py`, `bad_pattern/3/negative_prl_fail.py`, `bad_pattern/4/singular_fail.py` etc. — added `if not ctx.check_corner: return` at the top of `draw()`. Corner-class patterns (corner-to-corner, singular, corner-to-line 45°) are filtered when CheckCorner=False.
5. Updated `update_history.md` (#39, #40), `manual/space.md`, `PROJECT.md`, `tasks/todo.md`, `tasks/lessons.md`.
6. Verification: `verify_checkcorner.py` (gdspy geometry dump) confirmed 003_01 good=[1,2] (drop 3), bad=[1,2] (drop 3,4); created `{CheckCorner True}` temp config to confirm corner patterns restored; ran main + skill_convert regression (EXIT_OK, 0 ERROR / 0 WARNING).
7. Cleanup: removed stray `QA_checkcorner_true.gds`.

## Assistant tool chain (enclose task)

1. Wrote design spec `2026-11-16-enclose-value0-filter-design.md`.
2. Per-pattern gate in `bad_pattern/1/pattern1.py`, `bad_pattern/3/pattern3.py`, `bad_pattern/9/pattern9.py`: `if ctx.value <= 0: return` (edge-touching = pass at value=0).
3. Added value-related variants to bad_pattern/2 and bad_pattern/4.
4. Verified `verify_enclose_value0.py`: ENC_004_00_c (value=0) bad=[2,4,5] (1,3,9 filtered); ENC_004_01_c (value=0.08) unchanged.

## Key artifacts

- `function/space/simple/space.py` — SpaceContext/SpaceGenerator with mode + check_corner
- `function/space/simple/{good,bad}_pattern/N/*.py` — per-pattern draw() with gates
- `qa_config_device.txt` (READ-ONLY) — QACELL configs
- `temp_script_run/verify_checkcorner.py` — gdspy-based geometry verification

## Reframe decision

The real task touches a large GDS/gdspy codebase and the agent-policy writableRoots constraints (editor was sometimes rejected). To make a self-contained, offline-judgable case (no EDA sandbox / GDS needed), I reframed the **CheckCorner filtering logic** as a pure-stdlib pattern-survival classifier: given a manifest of patterns (name, kind, geom_class, row, mode affinity, is_45deg) and a config (mode, check_corner, check45), compute the sorted surviving set. The four gating rules (mode / check45 / check_corner / row) faithfully encode the trace semantics:

- check_corner=False drops corner_to_corner / corner_to_line / singular (no opposite run length) — the exact MSG 1 request.
- mode gate (min/max/exact) + row gate (wide bad only in max/exact) encode the checkValue iteration from the prior space three-mode refactor.
- check45 gate encodes the Check45dgree option.

Case: `EDA-Eval-DesignFlow-SpaceCheckCornerFilter-001` (physical_verify, k=14).
A=16 patterns (good 1-8, bad 1-8); B=22 patterns (gB_a1..10, bB_b1..12), disjoint names + different geom distribution (B has singular good, wide corner_to_corner, wide singular — anti-hardcode).
