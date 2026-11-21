# r934 deepread — ntqdg (jzeng@hfeg0plg85, mc=67, layout_aether)

**session**: 1794796541325_ntqdg.messages.json (752KB, 93 msgs, 2026-11-16)
**user**: jzeng (CXMT DRGQX layout engineer)
**keywords**: pyaether:432;drc:279;cellview:66;dbopencv:62;dbget:57;.gds:35;aether:34;calibre:21

## Real intent

jzeng wants to optimize the M4/M5/V4 auto-via generation flow. The legacy
`IMCleAutoVia.py` (2102 lines, full GUI auto-via tool) writes vias directly
into the target layout and creates V4 with `dbCrtVia`. jzeng's requirements
(msg 0):

> 优化该脚本，使其在0.55um宽的M4及0.55um宽的M5交点处生成2um x 2um的M4 M5，
> 再生成V4，M4 M5及V4都需要生成在auto via库的一个cell里面，不要直接生成在目标layout

## Conversation flow

- msg 0: user request (above)
- msg 1-27: agent reads IMCleAutoVia.py (2102 lines), V4_gen_M4M5.py (126 lines
  — scans 0.55um M4/M5, draws 2um squares in BOTH source AND auto_via,
  undesired), V4_gen_V4.py (empty). Searches pyAether APIs: dbCrtVia,
  dbNewCellView, techCrtCustomViaDefByName, dbCreateLib, dbCrtRect, etc.
- msg 22-89: agent writes V4_gen_V4.py (~320 lines) — optimized generator:
  read-only scan of source layout for M4/M5 wires width≈0.55um, finds
  intersections, draws 2um squares in auto_via cell only, creates V4 via
  dbCrtVa/custom via def. Multiple editor calls + syntax checks.
- msg 90: **user correction** — "无法生成V4，需要先生成足够的M4 M5，然后才能
  通过DRC check生成V4" (Cannot generate V4 directly — need enough M4/M5 first,
  then V4 auto-generated through DRC check)
- msg 91-92: agent re-reads IMCleAutoVia.py lines 799-1000 to understand the
  DRC flow (trace ends mid-correction)

## Trace gold

The intellectual core = the auto-via placement *plan*:
1. Filter M4/M5 wires by width ≈ 0.55um ± tol
2. Compute M4∩M5 bbox intersections
3. Place 2um×2um M4/M5 rects at intersection centers (auto_via cell, not target)
4. V4 via positions subject to DRC min-spacing (NOT dbCrtVia — DRC auto-gen)

User's key correction (msg 90) is the crux: V4 is DRC-generated, not manually
created. This becomes the via-spacing-skip logic in the reframe.

## Reframe (档B fixture-driven)

Decouple the geometry/planning logic from real Aether API calls (aeGetCurDesign,
dbCrtRect, dbCrtVia). Agent writes `auto_via_plan.py` that reads a JSON wire
fixture + DRC rules and emits a structured placement plan. check() validates
the plan on hidden B (different wires, via_size, spacing → forces a DRC skip).

## Case

- id: EDA-Eval-DesignFlow-AutoViaPlanGen-001
- domain: layout_aether
- k=14 teeth, ref PASS 14/14, 3 neg FAIL distinct (c/d/g)
- roundtrip sha256 85e83438740939122b6161f839d460e810a0e991a39cd26e7116981b600bd949 ✓
- C.jsonl 572→573
