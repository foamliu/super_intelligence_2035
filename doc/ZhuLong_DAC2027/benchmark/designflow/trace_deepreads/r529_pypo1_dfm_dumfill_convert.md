# r529 deepread: pypo1 — DFM DUMMYFILL SVRF RECTANGLES→DFM SPEC FILL conversion

**trace**: 1791944782637_pypo1 (jon@172.16.8.191, mc=134, physical_verify)
**file**: 386 msgs, 1.24MB; session dir `/home/jon/.cline/data/sessions/1791944782637_pypo1/`

## USER#0 (resume/context-summary, B档 synthesized)
"好的，我来给你产出**文件2 → DFM SPEC FILL 风格**的完整改后版本。" — resume of prior session converting Calibre DFM DUMMYFILL rule deck.

## Real task (distilled from full trace)
Convert a Calibre SVRF DFM DUMMYFILL rule deck from **RECTANGLES-based** TVF output to **DFM SPEC FILL SHAPE** format, using `dummy_sample.svrf` as the reference format.

### Files involved (on 172.16.8.191:/home/jon/01_virtual3/proj3/)
- `01_test_CXMT_N22DBS_Calibre_DUMMYFILL.svrf` — TVF-generated original (RECTANGLES)
- `02_dummy_DFM.svrf` — partial DFM SPEC FILL (user: "02并不是完全正确的DFM格式版本")
- `03_dummy_DFM.svrf` — partially converted (with syntax issues)
- `04_dummy_DFM_fixed.svrf` — **output** the assistant produces/fixes
- `dummy_sample.svrf` — **correct** DFM SPEC FILL reference format (user: "dummy_sample.svrf才是")

### Key transformations (from 04 revision history + edits)
1. `#endif` → `#ENDIF` (case-sensitive SVRF fix)
2. `RECTANGLES w h dx dy OFFSET ox oy INSIDE OF LAYER region` → `DFM SPEC FILL SHAPE <name>` + `POLYFILL` polygon coords (RECTANGLES→POLYFILL for nested slot shapes)
3. `FILLSHAPE OUTPUT "tag" "shape"` (one line) → `FILLSHAPE` + `    OUTPUT "tag" "shape"` (split to separate lines — SVRF syntax)
4. STEP/OFFSET removed from SHAPE definitions (was SVRF error); STEP added to DFM FILL rules
5. `M1_T1_fill_inner` eliminated (RECTANGLES artifact)
6. DFM FILL calls validated against OUTPUT tags

### DFM SPEC FILL reference format (dummy_sample.svrf:3558+)
```
DFM SPEC FILL SHAPE F_T1_10000_1
    POLYFILL    0.0000 0.0000   0.2660 0.0000   0.2660 0.2400   0.0000 0.2400   0.0000 0.2400

DFM SPEC FILL F_T1_dum INSIDE OF LAYER AMF_EX_1
    INITIAL INSIDE OF LAYER  LL
    FILLSHAPE
    OUTPUT "T1_1104_4" "F_T1_1104_4"
    OUTPUT "T1_1116_4" "F_T1_1116_4"
    STEP 0.079  0.09
    SPACEXY INTERIOR  0.079 0.04    BORD
    SPACE EDGE 0.1    AMF_EX_h_1
```

### Assistant tool chain
editor (create/fix 04_dummy_DFM_fixed.svrf) + run_approved_command (python-runner profile: show_orig.py, check_dfm_syntax.py, validate.py, find_fillshape.py, fix_fillshape.py — inspect/transform SVRF) + read_files (verify sections). 386 msgs of iterative editing.

## Synthesis decision
**B档 synthesized** (USER#0 is resume/context-summary, not clean produce-task opening).
**Domain**: physical_verify (Calibre DRC/DFM deck transformation).
**L2-boundary**: offline Python SVRF text transformation (no Calibre binary needed; parse/convert SVRF syntax).
**Case**: DfmDumFillConvert-001 — candidate `dfm_fill_convert.py <input.svrf> <output.svrf>` converts RECTANGLES fills + `FILLSHAPE OUTPUT` one-liners + lowercase `#endif` → DFM SPEC FILL SHAPE format with POLYFILL polygons, split FILLSHAPE/OUTPUT, uppercase #ENDIF.
**A**: 3 fill blocks (FEOL pair, M1 T1, M2 T1) with RECTANGLES + 2 `FILLSHAPE OUTPUT` one-liners + `#endif`.
**B**: 4 fill blocks (different layers M3/M4, different geometry params) — cross-input guard defeats hardcoding.
