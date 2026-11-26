# Deepread: 0d17g — QA Pattern Tool max_area_ratio (antenna) SKILL→Python migration (xxchen)

- **session**: 1791851758041_0d17g @ hfeg0pkn002 (xxchen, mc=393)
- **tools profile**: editor=91, run_approved_command=29, read_files=27, search_codebase=12, list_allowed_files=2 (cline "approved command channel")
- **nmsgs**: 299 (165 user / 134 assistant)
- **project**: QA Pattern Tool v0.3, `/home/xxchen/workspace/DRC_pattern_tool/0.3/device_rule1` — SKILL pcell → Python (gdspy) migration, 28 rule functions, good/bad DRC test-pattern cells.

## User intent (verbatim U#2, idx16 — the act turn for THIS session)
> 继续下一个 max_area_ratio 的 pcell skill to python的转换。

## User intent (verbatim U#3, idx48 — ANT connectivity config spec)
> 这个脚本需要一个 Connectivity setting … 我希望能把ANT的设置也写到同一个 config文件中 …
> LDR: antenna_Raito_000_00 Max ratio - PG area to GATE channel area. GATE not connected to PD <= 200
> config: TOOL config output_ANT_gds QA_ANT.gds (ANT 的GDS 单独进行输出)
> LDR connect ANT_connect {GATE {AT4;NCH PG;NCH} {AT4;PCH PG;PCH}} {conn {PG PC MT2} {AT4 PC MT2} {M0C PCU M0U} {MT2 PCU M0U} {M0U CT M1} {TCP CT M1} {M1 V1 M2} {M2 V2 M3} {M3 V3 M4} {M4 V4 M5} {M5 RDV RDL}}
> QACELL_ANT antenna_Raito_000_00 max_area_ratio PG->NMOS,PMOS 200 {layer2_device GATE} …

## User intent (verbatim U#4, idx109)
> 上面的任务完成了吗？  →  assistant: 还没有完成 (analysis+framework done, body+patterns+config+verify+records pending)

## What the session actually did (assistant flow)
1. Read conversion_progress.md C1 blocker note: 3 ratio fns depend on getConn/geFindLayerPath_old/dbGroup dynamic copy. Plan A = hand-expand to static geometry over fixed layer stack; Plan B = skip. User picked Plan A (max_area_ratio).
2. Read SKILL source: gate T-shape + connection-path stairs + wrong/right dual regions + cumulative/SingleViolation/GateConnectedPD branches. Most complex of 28 fns.
3. Confirmed `getConn`/`findVia`/`geFindLayerPath_old` NOT defined in source dir (Cadence env fns, depend on tech conn DB) → C1 cannot be derived from source.
4. layer.map query (approval channel): **PG=30;0, MT2=65;0, DGX=20;0, KGX=122;0, NSD=39;0, CT=85;0** present; **AA/CA/V0/M0 missing**. GATE group is layer pair (AA, PG). PG;NCH=30;3, PG;PCH=30;2, AT4;NCH=4;3, AT4;PCH=4;2. conn chain: only **M0C** absent from layer.map (user's path doesn't traverse it).
5. Found `skill_pcell/ANT_config.il` = real `getConn` definition. GATE = two variants `(AT4;NCH, PG;NCH)`/`(AT4;PCH, PG;PCH)`; conn = triple connectivity graph; `geFindLayerPath_old` = BFS shortest path (incl. both endpoints).
6. Extended `config_parser.py`: continuation-line merge + LDR connect parser (nested brace) + QACELL_ANT branch + output_ANT_gds handling. LDR value top-level is two independent `{...}` blocks → parsed as `[[GATE...],[conn...]]`; had to flatten top-level blocks first.
7. Extended `qa_pattern_tool.py` main(): ANT force simple + `_ldr` injection + dual GDS library split (ANT cells → QA_ANT.gds).
8. Wrote `max_area_ratio` entry module (Context init: CDF params + LDR conn + variant select + layer resolve; draw methods: gate structure / stairs / mark / long rect; pattern entry + finish_bbox + generator outlet) + 5 pattern files.
9. Updated config: TOOL output_ANT_gds + DEVICE NMOS/PMOS + LDR connect + QACELL_ANT row.
10. Offline verify script: config parse + graph-solver unit + 5-variant generator counts + geometry assertions. Hit bugs:
    - `parse_config` body had 12-space indent death-code (old loop body landed inside `if not line` block) → fixed indent.
    - `find_via` function accidentally deleted by a 3rd-segment edit (Context `__init__` still called it) → restored.
    - framework calls `draw(ctx, andLayer, andLayer2)` 3-arg → fixed all 5 pattern files signatures.
    - geometry assertions used flatten'd top coords (shifted +2 by pattern placement) → fixed to collect temp cell raw coords.
    - one assertion typo (V3 stair rect orientX = 1+11×0.5 = 6.5, not 6).
    → offline **54/54 PASS**.
11. Full-tool run: **37/37 cells exit 0**, ANT split to QA_ANT.gds working, no ERROR/WARNING.
12. GDS check script: PMOS variant MISSING, names untagged → dump QA_ANT.gds.
    - **Root cause (real bug, KEY grounded element)**: framework `zip(l1_groups, layer2_groups)` is PAIR semantics — 1 layer1 group × 2 layer2 groups runs only the first (NMOS), PMOS dropped. Comment intent was "layer1 × layer2" → must be `itertools.product` (existing multi-layer1 cases had single layer2 group so behavior unchanged). Fixed framework to product.
13. product fix: NameError on `product` at runtime (import timing?) — debug in progress at trace end (idx235).

## Trace termination
Trace ends mid-debug of the `product` NameError (A#77 idx235). User's last turn was "上面的任务完成了吗？" → assistant answered "还没有完成" and continued. **No user-accepted final gold product** → NOT suitable for A-faithful; use **B-synthesized** grounded on the real config/layer.map/conn-graph/naming/cross-product-bug.

## Grounded elements reused for the synthesized case (AntPatternConfigAudit)
- config format: TOOL/DEVICE/LDR connect/QACELL_ANT rows (verbatim structure from U#3)
- LDR conn triples (PG PC MT2, AT4 PC MT2, M0C PCU M0U, … M5 RDV RDL) — 11 triples
- GATE variants [(AT4;NCH,PG;NCH),(AT4;PCH,PG;PCH)]
- layer.map entries (PG;NCH=30;3, PG;PCH=30;2, AT4;NCH=4;3, AT4;PCH=4;2, M0C absent)
- antenna rule: max_area_ratio PG→GATE, threshold 200, GATE not connected to PD
- BFS shortest path (geFindLayerPath_old): PG→PC→AT4
- cell naming {good|bad}_{QACELL}_{L1}_{L2}
- ANT cells → separate output_ANT_gds (QA_ANT.gds)
- GRID 0.0001 µm alignment
- 3-step validation (offline → full-tool → gdspy GDS)
- **the zip→itertools.product cross-product bug** (PMOS variant dropped) → becomes check condition (i) len(cells)==4
- A-broken = delete the {AT4 PC MT2} conn triple → BFS PG→AT4 no path → overall_pass False
- hidden B = re-parameterized (PO/GT2/NF/PF, threshold 150, QA_ANT_B.gds, different datatypes) → defeats hardcoding A

## Distinctness from prior shard-C cases
- r201 CentroidPlaceAudit (common-centroid placement) — different (placement audit, not config/conn-graph)
- r200 PgRscalcAgentInline (RsCalc agent) — different (resistance calc, not antenna pattern)
- r199 HierCellPatternFind (hierarchical cell DFS) — different (tree traversal, not conn-graph BFS)
- This case is the FIRST to ground on: LDR connectivity config parsing + layer.map resolution + conn-graph BFS + itertools.product cross-product expansion + antenna max_area_ratio rule.
