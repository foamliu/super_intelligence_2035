# r252 deepread: 1793792893744_ioiiw (liwan@hfeg0pkn002, mc=157)

## Trace
- user: liwan (NEW user, first case), host: hfeg0pkn002/10.129.2.11, mc=157
- agent: lead, 71 msgs, ~560KB messages.json
- kw: 179 pyAether + 67 schematic + 19 dbGet + 10 netlist + 10 cellview + 9 pyAether + 7 calibre

## User intent (U#0, organic, 提出需求)
"你好 烛龙 请帮忙生成layout (lib : drcpa_analog  cell name :AG_ThinFsAllTopCap)"
- User asks to GENERATE layout for specific cell. No root cause given. A档 rule2 qualifies.

## Agent work
1. Agent searches codebase for pyAether layout creation patterns
2. Initializes pyAether: ae.emyInitAether("-adv")
3. Checks cell existence: ae.dbCVExist("drcpa_analog", "AG_ThinFsAllTopCap", "layout") → True
4. Opens layout: cv = ae.dbOpenCV("drcpa_analog", "AG_ThinFsAllTopCap", "layout")
5. Extracts shapes: list(cv.shapes) → 116 shapes, each with lpp, objType, bbox
6. Extracts instHeaders: list(cv.instHeaders) → 15 instHeaders, each with libName, cellName
7. Opens schematic: ae.dbOpenCV("drcpa_analog", "AG_ThinFsAllTopCap", "schematic") → 73 insts, 195 shapes
8. Produces layout status report (prose): shape count per layer, instance list with orientations, bbox, net count, port count
9. U#65: "2" → user selects more details → agent produces detailed report with instance groups, layer distribution, port list

## Key pyAether APIs used
- ae.emyInitAether("-adv")
- ae.dbGetAllLibs()
- ae.dbCVExist(lib, cell, view)
- ae.dbOpenCV(lib, cell, view) → cv object
- cv.shapes → list of shape objects (lpp, objType, bbox)
- cv.instHeaders → list of instHeader objects (libName, cellName)
- cv.libName, cv.cellName, cv.viewName

## Layout structure (AG_ThinFsAllTopCap)
- 116 shapes: M1.drawing:8, M2.drawing:9, M2.pin:48, M3.drawing:3, text.drawing:48
- 15 instHeaders: TECHLIB/RM02t:6, drcpa_MAT/Nicap_2S:10, drcpa_analog/AG_CXcap1S103x479:1, etc.
- bbox: (196.27, -431.7) ~ (2695.14, 822.74)
- 15 nets, 11 top-level ports

## B档 redefinition
- Real assets (drcpa_analog/AG_ThinFsAllTopCap) NOT accessible to e0031982 on .75 (drcpa_analog not in 1172 libs)
- BUT: TECHLIB cells accessible on .75 (RM02t, cut, switch_open, switch_close, Nicap_2S)
- Probed .75 Aether DB: TECHLIB/RM02t (8 shapes, 2 insts, MT2.resistance/drawing/reference + M0U.drawing, Rect+Path, insts=TECHLIB/cut×2), TECHLIB/switch_open (7 shapes, 0 insts, M1.drawing/term/open + text.drawing), TECHLIB/cut (2 shapes, V2.drawing), TECHLIB/Nicap_2S (0 shapes empty)
- B档 task: "layout structure extractor" — SUT writes layout_summary.py that parses pyAether shape/inst dump (JSON format mimicking dbOpenCV+cv.shapes+cv.instHeaders output) and produces structured JSON summary (total_shapes, lpp_counts, type_counts, total_inst_headers, inst_groups, dominant_inst, bbox, area)
- A: RM02t-like dump (8 shapes, 2 insts) | B: switch_open-like (7 shapes, 0 insts) | B2: cut-like (2 shapes) | B3: Nicap_2S-like (0 shapes empty)

## DISTINCT from existing layout_aether cases
- r238 LayoutFloorplanGen: floorplan generation (different task)
- r226 PcellPatternGeoDiag: PCell pattern geometry diagnosis
- r233 InstM0ShapePinIdentify: identify M0 shapes/pins from layout (filter specific layer)
- r236 SkillBindkeyFlattenMakeCell: flatten makeCell via SKILL
- r246 LefFromPinList: LEF macro generation from pin list
- r250 YamlToGds (shard C, e0047488): YAML→GDS via pyAether (generation, not extraction)
- THIS case: first ground on pyAether layout DB structure EXTRACTION (dbOpenCV → shapes/instHeaders → structured JSON summary with lpp_counts, type_counts, inst_groups, bbox, area)

## Case: EDA-Eval-DesignFlow-LayStructExtract-001
- Domain: layout_aether, Level: L1, Track: B-synthesized, k=18 (a-r)
- check.py: 18 conditions (zip valid, py_compile+stdlib, B exit+JSON, B total_shapes/lpp_counts/type_counts/inst_headers/inst_groups/dominant_inst/bbox/area, B2 total_shapes/lpp_counts, B3 empty, anti-hardcode B!=A, missing args, A total_shapes+dominant_inst)
- Self-verify: golden 18/18 PASS, 5 negatives all FAIL, §4.9 three-degenerate all FAIL
- test field == disk check.py byte equality verified
