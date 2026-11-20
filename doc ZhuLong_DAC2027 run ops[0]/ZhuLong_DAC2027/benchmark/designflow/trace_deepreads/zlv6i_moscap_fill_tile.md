# zlv6i — sasachen auto moscap fill tool deepread

**session**: 1794986146633_zlv6i · sasachen @ hfeg0pkn005 (10.129.35.74) · mc=207
**keywords**: calibre:778;drc:521;.gds:342;gdsii:142;cellview:21;cmos:16;binary:9;dbget:8;rtl:4;cadence:2;pyaether:1;analog:1
**trace**: 310 msgs / 6 real user text turns / 965KB messages.json (Nov 20 09:42-10:48)
**domain**: physical_verify (GDS fill-region rectangle tiling, calibre rule deck integration)

## User intent (verbatim, U#4 = real task turn)
```
sure so i want to develop a auto moscap fill tool, the moscap cells are mosaics
we only have to input the parameters such as rows and columns, i've created a
certain base of it which you can refter to:
  /home/sasachen/mine/mySnakie/request/ddgoa/autoMoscapFill.py
  /home/sasachen/mine/mySnakie/request/ddgoa/atExtract.rule
as i said it's not finished, what i wanted you to help me complete is processing
these gds file and cut it to rectangles of which i could fill moscaps in, the
rectangles shoule be min:horizontal:11.28 vertical:9.8 max: h:29.58 v:25.56,
i want you to withe atExtract.rule and output a gds file with rectangles fo me
to fill moscaps in, then we will figure out the rest together, also here's the
gds i've working on:
  /proj/ddgoa/V0/ver/drc/sasachen/z_sasha/ChanMid/moscap/capnotat4_extracted_1
also this is the cell i've been testing on:
  /proj/ddgoa/V0/workdir/sasachen/z_sasha/ChanMid/layout/layout.oa
dazzle me ~
```

Follow-up turns:
- U#246: "so you did all the process with python instead of calibre rule deck, impressive, but canyou integrate with the rule deck a bit more?, i want the rectangle created with the calibre rule deck, just try, and keep the old stuff you've worked on i want to see both methods"
- U#308: "instead of generating have you thought about work with the existing gds shapes, tile them and size them and stuff?"

U#0/U#2 are user chitchat (agent thinking too long) — not task intent.

## User-provided base files (attachments in trace)
- `autoMoscapFill.py` (72 lines): pyAether GUI tool — gets curDesign cellview, streams out to GDS via asOut, runs calibre -drc with atExtract.rule (bsub -I -q pv), then (unfinished) streams result back via asIn. Defines runDir = /proj/$PROJ_NAME/$Ver/ver/drc/$USER/$lib/$cell/moscap.
- `atExtract.rule` (146 lines): Calibre SVRF DRC rule deck — maps AT4 layers (layer 4 datatypes: 8/19/41/43/45/3/2/24/306/102/103/104/14/20/13 → 8051-8066) and CAP layers (3110-3130 → 8242-8262). Derived: AT4 = OR(PCH,NCH,CMP,DUMMY2,SL); CAP = OR(all CAP_*_drawing). Commented-out rule AT4_CAP_OUT: `tmp = NOT CAP AT4; tmp_1 = SIZE tmp BY -1; tmp_1 210 0` → outputs cap-not-at4 regions to **layer 210 datatype 0** (the fill regions rect_gen.py reads).

## Assistant gold chain
read_files(autoMoscapFill.py + atExtract.rule) → list_allowed_files(/proj/.../moscap) → read drc.log → run_approved_command (ls/wc/grep) → **editor writes** (iterative refinement, ~30 editor calls):
- check_tools.py, inspect_gds.py, inspect_gds2.py (GDS inspection probes)
- **autoMoscapFill_rect.py** (first rect generator)
- **rect_gen.py** (main gold, ~15 editor edits at msg 82/86/116/122/173/175/191) — the final deliverable
- temp_create.py, write_rect_gen.py, write_clean.py, gen_create.py, trunc_rect.py, prep_rect.py, make_rect.py, fix_rect.py, write_final.py (helpers/variants)

## Core gold = rect_gen.py (153 lines, on disk at /home/sasachen/mine/mySnakie/request/ddgoa/rect_gen.py)
- **deps**: gdspy + numpy (reads GDS, boolean ops)
- **constants** (user's exact min/max): MIN_W=11.28, MIN_H=9.80, MAX_W=29.58, MAX_H=25.56; output layer 211; reads layer 210 datatype 0
- **algorithm**:
  - `sizes()`: 7×7 grid of (w,h) from {MAX_W, MAX_W-2, MAX_W-4, MAX_W-6, MIN_W+4, MIN_W+2, MIN_W} × {MAX_H, ..., MIN_H}, filtered w>=MIN_W & h>=MIN_H, sorted by (-w,-h) [largest first] → 49 variants
  - per source polygon (sorted by area desc): for each (w,h) largest-first:
    - `tile_poly(verts, w, h, placed)`: grid `np.arange(bbox_origin, bbox_max - w + 0.001, w)` × same for h; for each grid (x,y) if `tile_inside` (5-9 sample points via `points_in_poly` ray-casting) AND not `any_ovl` with placed → add rect
    - `sub_poly(verts, rects)`: gdspy.boolean(sc, dc, "not") subtract placed rects from polygon, keep largest remaining piece → re-loop with next smaller size
  - output: write all rects to GDS layer 211 + summary .txt (`# x1 y1 x2 y2 w h area` rows + totals)
- **key primitives**: `bbox`, `area` (shoelace via numpy), `points_in_poly` (ray-casting vectorized), `tile_inside` (5-9 sample pts), `ovl`/`any_ovl` (rect overlap), `sub_poly` (gdspy boolean NOT)

## Pipeline (full user workflow)
1. autoMoscapFill.py (pyAether) streams out current cell → GDS, runs atExtract.rule (calibre -drc) → produces capnotat4_extracted_1.gds with layer 210/0 = cap-not-at4 fill regions (NOT CAP AT4, sized -1)
2. rect_gen.py (gdspy) reads capnotat4_extracted_1.gds layer 210/0, tiles with moscap-sized rects (11.28×9.8 … 29.58×25.56), writes moscap_rectangles.gds layer 211 + summary .txt
3. (U#246) calibre-rule-deck variant: generate rects via SVRF DRC operations (vs python gdspy) — "both methods"

## Reframe rationale (档 B)
- Real gold runs gdspy on a real project GDS (capnotat4_extracted_1.gds, project-specific, large, not reproducible in judge env). Judge env has no gdspy/gdstk (per r862).
- Reframe to **fixture-driven pure-stdlib geometry tiling**: input = text polygon file (the layer-210/0 fill regions as vertex lists), candidate delivers `moscap_tile.py <poly_file> [-o out.txt]` that tiles each polygon with moscap-sized rectangles (user's exact min/max) and outputs a rect list + summary. No GDS library, no numpy — pure stdlib geometry (shoelace area, ray-casting point-in-polygon, rect overlap).
- Judge = **structural correctness + coverage threshold** (not exact-algorithm match, since valid moscap fill is not unique): all rects in size bounds, all inside source poly, no overlap, coverage >= 70% of independent greedy reference, count >= 50% of ref, anti-hardcode A guard, 3-seed determinism, anti-cheat B-vertex literals.
- User intent preserved verbatim (U#4). Min/max sizes = user's exact numbers. Reframe is grounding (real GDS → small text polygons + pure-stdlib geometry) not added difficulty.

## 意图审计判定
**keep** — sasachen 真实意图 (auto moscap fill tool: GDS fill regions → moscap-sized rectangles for fill) 完整保留; reframe 是 grounding (gdspy+真实项目GDS → 纯stdlib几何 + 小合成多边形fixture) 非加难; min/max 尺寸直出 U#4 用户原话 (11.28/9.8/29.58/25.56); 11-15 reaudit 后 produce-task 合法.
