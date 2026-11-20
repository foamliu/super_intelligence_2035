# Deep-read: mdgyo (1782886137735_mdgyo) — Delete all M1 shapes via SKILL

- **trace_source**: user=e03179, host=hfeg0plg90, session=1782886137735_mdgyo.messages.json, mc=29
- **domain**: schematic_netlist (layout shape manipulation via SKILL)
- **size**: 77617 bytes, 36 msgs
- **selected round**: U#0 (MSG0) — clean A-faithful single-shot 提需求 round.

## U#0 (verbatim)
> 删除当前版图在所有M1的图形，使用skill语言生成代码并执行。

No root-cause, no fix suggested — pure requirement. ✓ A-faithful.

## Agent flow
1. MSG1: run_commands pwd/ls → devops/bundle dir.
2. MSG3-10: RAG search_apis (3 queries): "get current design layout", "delete shapes by layer name", "geGetEditCellView or get current cellView"; then "get all shapes on layer in cellView", "dbDeleteObject delete shape", "dbGetShapeOverlaps". Returns: hiGetItemOfLayout/hiGetLayoutType (noise), pcHIDeleteLayer/techDeleteLayer (layer-def deletion, not what we want), geGetEditRep/geGetEditCellView/deGetEditCellView (✓ current cv), dbGetFluidShapes/dbStartGenLPToShape/dbShapeQuery/dbHasShape (✓ shape query), dbDeleteObject (✓ delete), pcDeleteParamShape/leHiDeleteShapeFromNet (noise).
3. MSG11: get_api_details on dbStartGenLPToShape, dbDeleteObject, geGetEditCellView, dbShapeQuery. dbStartGenLPToShape signature: `dbStartGenLPToShape(d_cellViewId l_layerPurpose) => I_genId`, example uses `gen1~>next` + `dbStopGen(gen1)`.
4. MSG13: **v1 SKILL** — geGetEditCellView → lpp=list("M1" "drawing") → dbStartGenLPToShape(cvId lpp) → while(shapeId=genId~>next) dbDeleteObject(shapeId) inline → dbStopGen. SandBox run_code(lang=skill): **FAIL** "dbgenGetq: object is a purged/freed object - dbgen@0x315ee750" but print_log "Successfully deleted 1 shapes". **Bug**: deleting during generator iteration invalidates the generator.
5. MSG15: **v2 SKILL** — collect shapeList via append1 first, then dbStopGen, then foreach dbDeleteObject. But used `return()` outside `prog` + dbStartGenLPToShape returned nil (no M1 in this cv). **FAIL** "*Error* return: return can only be used within a prog" + "Could not create generator for M1 shapes".
6. MSG17-20: debug — geGetEditCellView() = db:0x1dcf491a, cellViewType="maskLayout", 2 shapes: M0C/markcore + CT/drawing. **No M1 layer in this cv.**
7. MSG21-22: tried 6 M1 purposes (drawing/pin/net/label/markcore/boundary) → all "no generator (layer may not exist)". M1 absent entirely in this tech.
8. MSG23-24: **v3 final SKILL** — `prog(() ...)` wrapper, foreach purpose list("drawing" "pin" "net" "label" "markcore" "boundary" "text"), lpp=list("M1" purpose), `when(genId ...)` guard, shapeList collect via while(append1), dbStopGen, foreach dbDeleteObject. SandBox run: **SUCCESS** "Total 0 shapes deleted from M1 layer." (correct — no M1 present).
9. MSG25-26: editor saves delete_m1_shapes.il to /home/e0025768/devops/bundle/.
10. MSG29-31: summary; tried submit_and_exit (rejected — not a real tool); final report to user. User implicitly accepts (no correction).
11. MSG32-35: **UNRELATED second task** "print hello in skill" — NOT part of A-faithful requirement; ignored.

## Gold standard (MSG23/MSG25 SKILL script)
```skill
;;; delete_m1_shapes.il
prog(()
    cvId = geGetEditCellView()
    unless(cvId
        printf("Error: No cellview is being edited.\n")
        return()
    )
    totalCount = 0
    foreach(purpose list("drawing" "pin" "net" "label" "markcore" "boundary" "text")
        lpp = list("M1" purpose)
        genId = dbStartGenLPToShape(cvId lpp)
        when(genId
            shapeList = list()
            while(shapeId = genId~>next
                shapeList = append1(shapeList shapeId)
            )
            dbStopGen(genId)
            foreach(shapeId shapeList
                dbDeleteObject(shapeId)
                totalCount = totalCount + 1
            )
        )
    )
    printf("Total %d shapes deleted from M1 layer.\n" totalCount)
)
```

## Key technical lessons (→ check assertions)
1. **Collect-then-delete**: must `append1(shapeList shapeId)` collect ALL shape IDs first, `dbStopGen`, THEN `foreach dbDeleteObject`. Deleting during `genId~>next` iteration → "dbgenGetq: purged/freed object" (trace MSG14 bug).
2. **`prog(() ... )` wrapper**: SKILL `return()` only valid inside `prog` (trace MSG16 bug).
3. **Multi-purpose iteration**: M1 shapes may exist under non-drawing purposes (pin/net/label/markcore/boundary/text). Must iterate the 7 standard purposes, not just "drawing".
4. **`when(genId ...)` guard**: `dbStartGenLPToShape` returns nil if the LPP doesn't exist in the tech → guard with `when`, skip gracefully.
5. **`dbStopGen(genId)`**: close the generator after collecting to free virtual memory.
6. **Cellview-agnostic**: script uses `geGetEditCellView()` (runtime current cv), does NOT hardcode a cellview name. The cellview/lib are only metadata (header comment + plan).

## Degradation rationale
Real Aether/Virtuoso GUI execution is non-deterministic (depends on which cellview is open, what layers exist in the tech). The trace's cv had NO M1 (only M0C+CT), so the real run deleted 0 — not a useful gold. **Degrade to config-driven generator**: gen_del_m1.py reads config.json (cellview + layers with counts) → emits the gold-structured SKILL script + a deterministic deletion plan computed from the config. This is the L1-boundary pattern (same as #239 NetHighlightProbe).

## Synthesis (A-faithful, L1-boundary schematic_netlist)
- **case_id**: EDA-Eval-DesignFlow-DelM1Shapes-001
- **config_A** (visible): TopLayout_A/demo_a; M1 drawing5+pin2+net1=8; decoy M0C/markcore3 + CT/drawing4. Expected delete 8.
- **config_B** (hidden): PwrLayout_B/analog_b; M1 drawing10+label3+boundary2=15; decoy M2/drawing6 + V0/drawing4 + M0C/markcore1. M1 absent under pin/net/markcore/text → 0 each. Expected delete 15.
- **deliverable**: submit.zip containing gen_del_m1.py (config-driven generator).
- **check.py**: 15 conditions a-o; runs gen on hidden B in isolated temp; asserts 7 SKILL-structure conditions (d-j) + 3 plan-value conditions (k-m) + cross-input guard (n) + non-degenerate/deterministic/§4.9-three-fakes (o).
- **5 negatives**: fake_empty(→c), fake_print_fixed_A(→k/l/m/n), fake_core_deleted(→g/h/i), naive_no_purpose_loop(→j/k/l), naive_no_layer_filter(→k/l).
- **§4.9 three fakes distinct**: {c} ∪ {k,l,m,n} ∪ {g,h,i} = 8 distinct ≥3 ✓.

## Self-verification results
- ref (gen_del_m1_ref.py as gen_del_m1.py in reference_submit.zip): **PASS 15/15**.
- 5 negatives: **ALL FAIL** (NEG_RC=0).
- §4.9 three fakes: empty→[c], print_fixed_A→[k,l,m,n], core_deleted→[g,h,i] → 8 distinct conditions.
- test==disk roundtrip: sha256 match ✓.
- k_rationale=15 == k_check=15 (CONDITIONS a-o) ≥8 ✓.
- D.jsonl 85→86 行.
