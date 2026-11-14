# Deep-read: 0qbbv (yzwang@hfeg0plg55) — PatternPortOpcMark-001

**Session**: 1794296395393_0qbbv
**User**: yzwang @ hfeg0plg55 (10.129.8.x)
**mc**: 68 (dbcreaterect:254; dbcreatepath:114; pdk:68; aether:124; drc:23; cellview:10; virtuoso:9)
**Domain**: layout_virtuoso
**Track**: B (synthesized mock-behavioral)
**Size**: 395KB, 59 msgs, 4 user turns, 12 read_files + 6 editor + 6 run_approved_command

## User intent evolution

- **USER#0** (debug): "spaceUponWidthPass.il 脚本，这个pcell会生成两排pattern，其中第一排和第二排的倒数第二个pattern有问题，生成的两个矩形的space并不是参数space的值，好像差了几个格点，请帮忙分析原因。" → debug-Q&A (user gives symptom, not A档 eligible)
- **USER#1** (modify with direction): "在不改变上下图形width的情况下，将上下图形的space改成所填space的大小" → modify-existing with user giving fix direction
- **USER#2** (warning report): dbCreatePath width must be multiple of 0.0005 warning → debug info
- **USER#3** (produce-task): "把Pass脚本中第266-269行和507-510行的pattern移植到fail脚本中，且266行-269行的pattern出现在fail pattern第一行的最后一个，507-510行的pattern出现在fail pattern第二行的最后一个，并且新生成的两个pattern中，每个pattern的两个矩形的space区域框上合适大小的OPC01_mark1" → **produce-task modify-existing port** (user gives exact line numbers = fix solution → B档-only)

## Agent workflow

1. read_files spaceUponWidthPass.il (multi-segment read)
2. editor msg#13: analysis script (Python geometry analysis for space/width/grid)
3. editor msg#19: fix dbCreateRect coordinates (SKILL code patch)
4. editor msg#26/30: snap-to-grid analysis scripts (precisionFix=2000, snap_trunc/snap_round)
5. read_files spaceUponWidthFail.il
6. **editor msg#46**: port_opc_mark.py (3283B) — the main porting script:
   - Reads Pass.il, extracts shield blocks (lines 266-269 / 507-510)
   - Reads Fail.il, finds insertion points (end of each pattern row)
   - Inserts ported patterns as LAST pattern of target row
   - Adds lppOPC = parseString("OPC01_mark1", "_") layer definition
   - Adds dbCreateRect(cv lppOPC list(sx0 sy0 sx1 sy1)) covering space region
   - Writes patched file to /home/yzwang/spaceUponWidthFail_OPC01_patched.il
7. **editor msg#54**: verification script (1451B) — structural sanity checks:
   - lppOPC defined exactly once
   - lppOPC used in dbCreateRect exactly 2 times
   - lppOPC declared in let local list
   - Parenthesis balance check

## Core algorithm (abstracted for mock-behavioral case)

1. **Parse** pass_deck → extract specified patterns (by index)
2. **Insert** ported patterns at end of target rows in fail_deck
3. **Compute space region** between each ported pattern's two rectangles:
   - x-overlap: [max(rect0.x0, rect1.x0), min(rect0.x2, rect1.x2)]
   - y-gap: [rect0.y_top, rect1.y_bottom]
4. **Add OPC marker** (rectangle) on OPC01_mark1 layer covering the space region
5. **Output** patched_deck.json (deterministic, sort_keys)

## Key trap (anti-hardcode)

- B pattern 0 (shB1): rects [15,0,25,4] and [18,6,28,10] → **partial x-overlap** [18,25], space=[18,4,25,6]
  - naive_full_width: [15,4,28,6] → wrong
  - naive_rect0_only: [15,4,25,6] → wrong
- B2: 3 rows, port to rows 0 and 2 (row 1 NOT targeted, must stay unchanged)

## Case structure

- **Visible A**: pass_deck_A.json (2 patterns, full x-overlap) + fail_deck_A.json (2 rows, 2 pat each) + port_spec_A.json + original_port_script.py.txt + task_brief.md
- **Hidden B**: pass_deck_B (3 patterns, partial x-overlap trap in #0, decoy #2) + fail_deck_B (2 rows, 3 pat each) + port_spec_B (port [0,1]→rows [0,1])
- **Hidden B2**: pass_deck_B2 (2 patterns, different coords/layers M3) + fail_deck_B2 (3 rows, row 1 not targeted) + port_spec_B2 (port [0,1]→rows [0,2])
- **12 conditions a-l**: structure(2) + B run(1) + B n_ported(1) + B opc_layer_defined(1) + B rows(1) + B row0 ported_0(2) + B row1 ported_1(1) + B opc_markers count(1) + B opc_marker[0] bbox partial-overlap(1) + B opc_marker[1] bbox(1) + B2 anti-hardcode(1) = 12 (determinism is a non-labeled gate)
