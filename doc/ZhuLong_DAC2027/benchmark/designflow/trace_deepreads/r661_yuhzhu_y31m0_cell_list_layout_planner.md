# Deepread r661 — yuhzhu@y31m0 (layout_aether, cell-list→one-view)

**Session**: `1793063311378_y31m0` · user `yuhzhu` @ `hfeg0plg91` (10.129.8.221) · mc60 · keywords `aether:95;pyaether:67;cellview:41;schematic:14;lvs:5;drc:5;virtuoso:4`
**Status**: r578 parked ("meta(hello layout eng) + thin produce cell-list->one-view below family bar") → **r661 revival per 2026-11-15 用户令** (real user intent, no preset filter can veto). Re-marked `claimed` 2026-11-16.

## Trace shape

`/home/yuhzhu/.cline/data/sessions/1793063311378_y31m0/1793063311378_y31m0.messages.json` — 39 msgs / 2 user turns / single session end.

### User turns (verbatim)

- **U#0** (intro): `你好 我是一名layout工程师，请问你如何帮我提高工作效率` — greeting, no task.
- **U#2** (核心需求): `给你一个cell list 你能帮我把这些调到同一个view 里面吗` — **提出需求型**, A档合规.
- U#6 (clarify via ask_question): `把 cell list 调到同一个 Layout 版图视图里（平铺或按行列摆放）` — placement = flat or row/col grid.
- U#20 (clarify): `cells 可能来自不同 Library，我提供完整 lib/cell/view 信息` — cross-library cells, full lib/cell/view tuple.

### Assistant tool chain

RAG search_apis (`aeCreateInstance`/`aeOpenDesign`/`aeGetCellView`/`aeSaveDesign`/`aeZoomAll`/`aeCheckAndSaveDesign`/`emyInitAether`) → `get_api_details` (aeCreateInstance signature) → `list_allowed_files` (/home/yuhzhu) → `editor` creates 3 files → `read_files` verifies.

### Artifacts produced (3 files in /home/yuhzhu/)

1. **`place_cells_to_layout.py`** — main script. Hardcoded `CELL_LIST` of 8 tuples `(lib, cell, view)` from `lib_a/lib_b/lib_c` (INV/NAND2/NOR2/AND2/DFF/MUX2/BUFFER/XOR2). Target `my_lib/top_cell/layout`. Cols=4, row_space=50, col_space=50, start=(0,0), prefix="I_". Logic: `emyInitAether` → `aeOpenDesign(target)` (fallback create) → loop `aeCreateInstance(cell, (x,y), libName, viewName, instName, orient='R0', magni=1.0, justify='LowerCenter')` with `row=idx//COLS, col=idx%COLS, x=START_X+col*COL_SPACE, y=START_Y+row*ROW_SPACE, inst_name=prefix+cell` → `aeCheckAndSaveDesign` / `aeSaveDesign` → `aeZoomAll`.
2. **`place_cells_from_csv.py`** — CSV-driven version. `load_cell_list_from_csv()` parses `lib,cell,view` rows, skips `#` comments + header (`lib`/`library`/`libname`), defaults `view="layout"` if blank, defaults `lib=TARGET_LIB` if blank. Same placement math as main script.
3. **`cell_list.csv`** — example CSV: 8 rows `lib_a,INV,layout` / `lib_a,NAND2,layout` / `lib_a,NOR2,layout` / `lib_b,DFF,layout` / `lib_b,MUX2,layout` / `lib_c,BUFFER,layout` / `lib_a,XOR2,layout` / `lib_a,AND2,layout`.

### Gold (user acceptance)

Session ends after A#38 summary table; no further user prompts ⇒ **implicit acceptance**. Gold = the 3 files above with the documented placement logic.

## Reframe (B档 mock-behavioral, per r645–r660 pattern)

**Why reframe**: real scripts call `pyAether` GUI APIs (`aeCreateInstance`/`aeOpenDesign`/`aeSaveDesign`) which require Aether GUI + live library DB. Hardcode-able (CELL_LIST baked-in) and sandbox-unreachable. ⇒ reframe to a **pure-stdlib `cell_layout_planner.py`** that takes any cell-list CSV + placement config JSON, parses+validates entries, computes grid placement, and emits a structured JSON manifest. The pyAether API calls become a *planning* problem (no GUI side-effects), preserving the user's intent (place cells into one view in a row/col grid) while being verifiable on hidden inputs.

**New sub-type**: `cell-list-layout-planner` (layout_aether). Distinct vs r658=netlist-to-schematic-builder / r657=3d-lvs-gui-config / r656=via-enclosure-dist / r655=polygon-orientation / r652=pex-batch-path / r650=cut-layer-idx / r645=svrf-antenna.

**Asset A** (SUT-visible): `cell_list_A.csv` (trace 8 cells) + `place_cells_to_layout_A.py` (trace original as schema reference — agent sees it to learn the placement math, NOT to copy hardcodes) + `prompt.md` (user原话 + spec) + `task_brief.md` (≤3 行交付接口).

**Hidden B** (check-only, not in SUT sandbox):
- `cell_list_B.csv` — 12 data rows (10 valid placed + 1 blank-cell skipped + 1 blank-lib defaulted to TARGET_LIB) from libs `AnalogLib/StdCellLib/MEMCells/IOCells/TOP_LIB(defaulted)` (distinct from A's `lib_a/lib_b/lib_c`).
- `config_B.json` — `cols=3, row_space=80, col_space=60, start_x=100, start_y=200, prefix="I_", target=TOP_LIB/chip_top/layout`.
- `cell_list_B2.csv` — degenerate: 1 valid cell (StdCellLib,INV,layout).
- `config_B2.json` — `cols=1, row_space=10, col_space=10, start=0/0, prefix="X_", target=TOP_LIB/buf_top/layout`.

**Deliverable**: `cell_layout_planner.py` — `python cell_layout_planner.py <cell_list.csv> <config.json> <out.json>` — reads CSV (skip `#` comments + header `lib`/`library`/`libname` + blank lines; default `lib←target_lib` if blank, `view←"layout"` if blank; skip data rows with blank cell name counting them in `summary.skipped`), reads config, computes `row=idx//cols, col=idx%cols, x=start_x+col*col_space, y=start_y+row*row_space, inst_name=inst_prefix+cell, orient="R0"`, emits JSON:
```json
{
  "target": {"lib":..., "cell":..., "view":...},
  "placement": {"cols":N, "row_space":F, "col_space":F, "start_x":F, "start_y":F, "inst_prefix":...},
  "cells": [{"idx":0, "lib":..., "cell":..., "view":..., "inst_name":"I_OPAMP", "x":100.0, "y":200.0, "row":0, "col":0, "orient":"R0"}, ...],
  "summary": {"total":12, "placed":11, "skipped":1, "libs_used":[...sorted unique incl. defaulted...], "unique_cells":11, "unique_views":["layout"], "bbox":[xmin,ymin,xmax,ymax]}
}
```

**check() 16 条件 a–p**: (a) zip 含 py + py_compile ②(b) B 跑通+合法 JSON ③(c) 4 顶层键+类型 ④(d) cells.length==11(placed) ⑤(e) 每 cell 含 10 必需键 ⑥(f) cell[idx].lib/cell/view 逐项匹配 B CSV (含 BUF2 lib=TOP_LIB defaulted / view=layout defaulted) ⑦(g) x=start_x+col*col_space (idx 0/5/10 spot-check) ⑧(h) y=start_y+row*row_space (idx 0/5/10 spot-check) ⑨(i) row=idx//cols, col=idx%cols (idx 0/3/10 spot-check) ⑩(j) inst_name==prefix+cell ⑪(k) orient=="R0" ⑫(l) summary.total==12/placed==11/skipped==1 ⑬(m) libs_use==["AnalogLib","IOCells","MEMCells","StdCellLib","TOP_LIB"] sorted incl. defaulted ⑭(n) unique_cells==11, unique_views==["layout"] ⑮(o) bbox==[100,200,220,440] ⑯(p) B2 反硬编 (1 cell, total=1, bbox=[0,0,0,0], target.cell=="buf_top") + 确定性 3x byte-identical + AST 无 A 档专属字面量 (lib_a/lib_b/lib_c/my_lib/top_cell/NAND2/NOR2/MUX2/BUFFER/XOR2/AND2).

**4 negatives**: neg1 empty-shell (a) / neg2 print-expected (d) / neg3 core-deleted (f) / neg4 always-pass-stub (c) / neg5 wrong-bbox (o).

**Self-verify**: gold_ref.py PASS 16/16 ✓; 5 negs all FAIL with ≥3 distinct first_fail labels ✓; §4.9 三假 (empty-shell/print-expected/core-deleted = neg1/neg2/neg3) 全 FAIL ✓; k_rationale==k_check==16≥8 GATE PASS ✓.

## Asset reachability

- trace messages.json: `/home/yuhzhu/.cline/data/sessions/1793063311378_y31m0/1793063311378_y31m0.messages.json` (39KB) — accessible via `ssh 10.129.8.221` (e0031982 identity, passwordless).
- artifact files: `/home/yuhzhu/place_cells_to_layout.py` (4.3KB), `/home/yuhzhu/place_cells_from_csv.py` (3.9KB), `/home/yuhzhu/cell_list.csv` (0.3KB) — all readable via ssh.

## Ledger

- `claim`-ed 2026-11-16 (revival from r578 parked).
- Will `mark --status case --case-id EDA-Eval-DesignFlow-CellLayoutPlanner-001` after jsonl append.
