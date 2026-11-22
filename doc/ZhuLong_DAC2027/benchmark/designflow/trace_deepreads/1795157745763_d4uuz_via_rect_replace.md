# Deepread: 1795157745763_d4uuz — V1 Rectangle→Via Replacement

## Trace metadata
- **session**: `1795157745763_d4uuz.messages.json`
- **user**: robin1l
- **host**: hfeg0plg87 (10.129.8.87)
- **mc**: 175
- **domain**: layout_aether (pyaether:302, cellview:297, aether:193, dbopencv:68)
- **date**: 2026-11-19
- **msgs**: 121

## Real task summary

robin1l is working in the Aether Layout Editor on cell `drvqa_cmos_digital/D_YsaThirdTop_gut/layout`.
The session evolved through 4 sub-questions:

1. **"你能看到我现在打开的是哪个cell吗"** — Can you see which cell I have open?
   - Agent used pyAether: `emyInitAether`, `aeGetCurDesign`, `aeGetTopDesign`, `aeGetFitDesign`
   - Found: EditDesign = `drvqa_cmos_digital/D_YsaThirdTop_gut/layout`,
     TopDesign = `drvqa_cmos_top/DDR5TOP/layout`,
     FitDesign = `drvqa_cmos_digital/D_YsaBankx2/layout`

2. **"你能不能获得我这个cell的编辑权限"** — Can you get edit permission?
   - Cell was read-only; agent used `aeMakeEditable()` to grant edit access

3. **"是不是能看到很多rectangle类型的via"** — Are there many rectangle-type vias?
   - Agent queried shapes via `block.getShapes()`, classified by `type(s).__name__`
   - Found in `D_YsaThirdTop_gut/layout`:
     - **190** `emyCustomVia` objects (V1, V2_L via definitions)
     - **458** rectangles drawn directly on via cut layers:
       - **287** rects on V1 cut layer (layerNum=90), each 450×450 dbu
       - **171** rects on V2 cut layer
     - Also 283 M1 rects, 458 M2 rects (normal metal)

4. **"我需要将Rectangle类型的V1替换成Via V1，该如何操作"** — How to replace Rectangle-type V1 with Via V1?
   - Agent investigated:
     - V1 rect bbox: 450×450 dbu (e.g., (284775,259375)-(285225,259625))
     - Existing V1 customVia bbox: ~1850×1850 dbu
     - Tried `dbCrtVia` → returned None (couldn't find V1 viaDef by name in that tech)
     - Tried `techGetTechFile`, `techGetTechLib` — sandbox crashed
     - Researched `emyCustomVia.create(block, viaDef, xform, params)` and `techCrtCustomViaDefByName`
     - Planned approach: get V1 viaDef from existing vias (`block.getVias()` → `v.getViaDef()`),
       then for each V1 rect: compute center, create via at center, delete original rect
   - **Sandbox died (Connection refused at 10.129.8.138:51722) before completion**

## Key technical facts (from trace)

| Item | Value |
|------|-------|
| Target library | `drvqa_cmos_digital` |
| Target cell | `D_YsaThirdTop_gut` |
| View | `layout` |
| V1 cut layer number | 90 |
| V1 rect count | 287 |
| V1 rect size | 450×450 dbu |
| V1 rect example bbox | (284775,259375)-(285225,259625) |
| Existing V1 customVia count | 190 |
| V1 customVia bbox | ~1850×1850 dbu |
| Via def names | V1, V2_L |

## Key APIs mentioned/used in trace

- `emyInitAether("-adv")` — initialize
- `aeGetCurDesign()` / `aeGetTopDesign()` / `aeGetFitDesign()` — get current/top/fit design
- `aeMakeEditable()` — make cell editable (from read-only)
- `dbOpenCVByType(lib, cell, view, "layout", "a")` — open in append mode
- `design.getTopBlock()` — get top block
- `block.getShapes()` — get all shapes
- `block.getVias()` — get all vias
- `type(s).__name__ == "emyRect"` — check if rectangle
- `s.getLayerNum()` — get layer number
- `s.dbuBox` → `box.left()`, `box.right()`, `box.bottom()`, `box.top()` — get bbox
- `v.getViaDefName(vdn)` — get via def name
- `v.getViaDef()` — get via def object
- `dbCrtVia(cv, defName, point, ...)` — create via by def name (failed in trace)
- `emyCustomVia.create(block, viaDef, xform, params)` — create custom via
- `techFindViaDefByName(tech, name)` — find via def by name
- `techGetTechFile(lib, "r")` / `design.tech` — get tech database
- `aeDeleteObj()` — delete selected figures (GUI selection-based)

## Case design plan

**task_id**: `EDA-Eval-DesignFlow-ViaRectReplaceSpec-001`
**domain**: layout_aether
**tier**: 2
**deliverable**: `v1_rect_to_via_replace_spec.md` (markdown operations spec)
**check mode**: static text analysis (no pyAether execution)

### k=10 assertions plan
1. spec file exists at zip root, non-empty (>200 chars)
2. mentions opening layout in edit/append mode (`dbOpenCV` / `dbOpenCVByType` with mode "a" or "edit")
3. mentions identifying V1 rectangles by layer number (getLayerNum / layerNum == 90 / V1 cut layer)
4. mentions getting V1 viaDef from existing vias (`getVias` → `getViaDef` / `getViaDefName`)
5. mentions `techFindViaDefByName` as alternative to get viaDef from tech DB
6. mentions computing rect center position from bbox (left+right)/2, (bottom+top)/2
7. mentions via creation API (`dbCrtVia` or `dbCrtVia3X` or `emyCustomVia.create`)
8. mentions deleting original rect (`aeDeleteObj` / `dbDeleteObj` / delete shape)
9. mentions verification: count V1 rects before/after (should decrease), count vias before/after (should increase)
10. mentions `aeMakeEditable` as prerequisite for edit access
11. structure: ≥2 distinct methods with numbered steps

### 3 negative cases (all must FAIL)
- neg_a: empty zip → FAIL ①
- neg_b: wrong filename (spec.py not .md) → FAIL ①
- neg_c: plain text with no relevant keywords → FAIL ②③④⑦

### §4.9 three-fake (all must FAIL)
- fake_a: generic layout editing guide with no via-specific content → FAIL ③④⑦
- fake_b: via creation tutorial that doesn't mention rect replacement → FAIL ③⑧⑨
- fake_c: correct file but only 1 method, no verification → FAIL ⑨⑪
