# Deepread: j56lm — Auto P&R Orchestration (analog_context)

- **session**: 1789119944175_j56lm (davidwu @ hfeg0plg95, mc168, 143 msgs, 438KB)
- **domain**: analog_context (pyAether autodesign P&R)
- **U#0** (A-faithful 提需求轮, 未指出根因 ✓): 「帮我将打开的电路test3/AF_PPRCntEnd floorplan view 完成布局和布线.请使用placementConfig_v13.json 文件执行step 3 aeAutoPlacementFromDesign.」

## Agent workflow
1. Load skill `ae-auto-placement-from-design` → aeAutoPlacementFromDesign API (从原理图自动生成布局)
2. RAG get_api_details: aeAutoPlacementFromDesign, dbOpenCV, openDesign, emyCdbaNS
3. Read placementConfig_v13.json (1782 bytes), apr_v13.py, apr_v14.py (prior scripts), launch_v13/v14.sh
4. Examine test3/ directory structure, v14 route scripts/logs (route5 layer rule m_widthSpace type error)
5. Load skill `do-logic-router` → doLogicRouter API
6. Build **apr_v15.py** (based on v14 pattern, PROJECT=test3):
   - Step 0: `emyInitAether("adv")`
   - Step 1: `aeOpenDesign("test3","AF_PPRCntEnd","floorplan")` → se (design handle)
   - Step 2: read `placementConfig_v13.json` via `json.load`, count instances (262) + shapes (4606)
   - Step 3: **`aeAutoPlacementFromDesign(se, cfg)`** (user-specified) → returned True (placement OK)
   - Step 4: `aeSaveDesign(se)` → saved layout.oa (36300→41108 bytes, backup created)
   - Step 5: `doLogicRouter(se, ...)` → returned **False** (routing FAILED)
   - v15 result: **placement SUCCESS, routing FAIL**
7. U#5 (msg 95) repeats same request → agent builds **apr_v16.py**:
   - Key fix: add `RouteBaseOptions()` with `setRouteMode(OPT_ROUTE_MODE_NORMAL)` + `setTrunkMode(OPT_TRUNK_MODE_SINGLETRUNK)` (v15 never called setRouteMode → routing engine had no mode → immediate False)
   - Added via rules: `aeViaGetViaOptions` + `setViaRules`
   - v16 result: `aeOpenDesign` returned False ("Library ddgoa not found" — lib.defs issue, design modified in GUI)
   - Trace ends mid-debug (msg 142, no final user acceptance)

## Gold standard (人工复核)
- User's actual accepted result: **v15 placement succeeded** (aeAutoPlacementFromDesign=True, layout.oa saved). Routing failed; v16 attempted fix but broke open.
- Gold = P&R orchestration script structure (v15 Steps 0-4 + v16 RouteBaseOptions fix for Step 5).
- Real pyAether P&R is non-deterministic + sandbox-dependent → **degrade to config-driven generator** (produce apr.py + plan.json), L1-boundary.

## Synthesis plan: EDA-Eval-DesignFlow-AutoPR-001 (A-faithful, analog_context, L1-boundary)
- **Generator** `gen_apr_ref.py`: config-driven → apr.py (orchestration script with emyInitAether→aeOpenDesign→readConfig→aeAutoPlacementFromDesign→aeSaveDesign→RouteBaseOptions+doLogicRouter) + plan.json
- **config_A** (visible): test3/AF_PPRCntEnd/floorplan, placementConfig_v13.json, 262 inst, 4606 shapes, route_mode OPT_ROUTE_MODE_NORMAL, trunk_mode OPT_TRUNK_MODE_SINGLETRUNK
- **config_B** (hidden): AmpLib_B/AmpTop_B/floorplan, placeCfg_B.json, 418 inst, 7291 shapes, structurally different
- **check.py ≥15 conditions**: a(zip含gen) b(py_compile) c(跑B出.py+plan) d(emyInitAether) e(aeOpenDesign) f(aeAutoPlacementFromDesign) g(json.load读config) h(aeSaveDesign) i(doLogicRouter) j(RouteBaseOptions+setRouteMode) k(step顺序:place在route前) l(plan inst/shapes==B) m(plan lib/cell/view==B) n(跨输入护栏:A-only不泄) o(非退化+3sha一致+§4.9三假FAIL)
- **5 negatives**: fake_empty(→c) / fake_print_fixed_A(硬编A→n,l,m) / fake_core_deleted(无aeAutoPlacementFromDesign→f) / naive_no_route_options(无setRouteMode→j) / naive_no_save(无aeSaveDesign→h)
