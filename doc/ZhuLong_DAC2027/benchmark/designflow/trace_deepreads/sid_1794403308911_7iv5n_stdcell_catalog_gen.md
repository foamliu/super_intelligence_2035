# Deepread: sid 1794403308911_7iv5n — Stdcell Catalog Gen + Library Cross-Validation

**User**: xdwang @ hfeg0pkn005 (10.129.2.14), mc=130
**Domain**: schematic_netlist
**Session**: 232 msgs, 975KB, 4 user turns
**Scan src**: summary_1113.tsv

## User turns (verbatim, key produce turns)
- U0: "this circuit include all standard cell, check and sort all cell list(cell name, function, lib, device type(ntn, ntk ...) etc.) and output result to /proj/dscqa/V0/workdir/xdwang/simulation/00_StandardCell"
- U1: "result is ok, output each cell library name and library path to result, now update it"
- U2: "not find library name and library path in cell list, check result and update it again" (txt didn't show lib per row)
- U3: "some cell not exist in library, check and remove these cells from the circuit"

## Assistant flow (editor×102, run_approved_command×68)
1. list ALL_STDCELL_CIRUIT → read data.dm (Aether binary) → extract strings → parse ILList `(lib "stdcells_ac" cellname "symbol")` → 1328 unique cells
2. Find library at /proj/dscqa/V0/libs/stdcells_ac → examine cell structure (schematic/sch.oa + data.dm per cell)
3. Find TECHLIB → understand device types: ntn, ptn, ntn_lv, ptn_lv, ntn_lvio, ptn_lvio
4. Analyze cell naming convention: `<func><inputs><flavor><drive>[_feature]`
   - func: inv, buf, nand2/3/4, nor2/3, and2/3, or2/3, xor2, xnor2, aoi21/22/211, oai21/22, mux2, mxi2/4, ffr, ffrq, ffsr, latch, passgt, tie0/1, cap4x, delay4
   - flavor: L, CS, DS, GS, LV, LVS
   - drive: x1/x2/x4/x8/x16/x0p5, ofN, sN
   - feature: _fbs, _fbr, _gut, _fb, _pc60, _slv
5. Build generate_catalog.py → gen_cat2.py (parse_name + decode_function + flavor_of + device_for_flavor)
6. Output: StandardCell_List.csv (1328 rows), .txt, Summary.csv, README.md
7. U1: add LibName + LibPath columns → update
8. U2: fix txt to show lib per row (not just header)
9. U3: cross-validate — check_missing.py: 566 of 1328 don't exist as dirs in library → remove → 762 remain → Removed_Cells_MissingInLibrary.csv

## Key gotchas (portable)
1. **CS flavor → ntn_lv/ptn_lv** (NOT ntn/ptn!) — non-obvious device mapping: L/DS/GS→ntn/ptn, CS/LV/LVS→ntn_lv/ptn_lv
2. **Longest-flavor-first matching**: LVS before LV before L (else "nand2LVSx1" would split as nand2L+VS or nand2LV+S)
3. **Drive extraction**: xNN or xNNpNN (fractional x0p5) at end, before flavor
4. **Feature suffix stripping**: _fbs/_fbr/_gut at very end, before drive
5. **Cross-validation**: cell exists iff `<libdir>/<cellname>/` is a directory; remove non-existent from catalog, output removed report
6. **Lib name+path per row** in txt (U2 gotcha: not just header)
7. **Sorted output** by CellName
8. **catalog + removed == all source cells** (no cell lost/duplicated)

## Synthesis plan (portable)
- SUT produces `stdcell_catalog.py` (pure stdlib CLI: `<cell_list.txt> <lib_dir> <lib_name> <lib_path> <out_dir>`)
- visible A: 40 cells (28 exist, 12 missing)
- hidden B: 52 cells (36 exist, 16 missing) — different names, anti-hardcode
- hidden C: 44 cells (30 exist, 14 missing) — cross-input anti-hardcode
- check.py 16 cond a-p (k_check=16), independent oracle re-parses B/C
- 4 negatives (empty/print/hardcode-A/core-removed) ALL FAIL
- k_rationale = k_check = 16 ≥ 8 ✓

## Near-dup audit
- xdwang: NEW user (0 prior cases in D.jsonl)
- StdcellListXtract-001 (o8ivt): extracts cell NAMES from a single netlist (flat list + SPF path filter). This case: directory-level inventory with rich metadata decode (function/flavor/drive/device-type) + library cross-validation + removal. Different metric/SUT/check/gotcha/domain-scope → defensible distinct.
