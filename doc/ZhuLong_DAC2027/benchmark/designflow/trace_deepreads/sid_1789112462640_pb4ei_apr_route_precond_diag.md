# 深读笔记 — sid 1789112462640_pb4ei (davidwu / hfeg0pjn200)

- **session**: 1789112462640_pb4ei.messages.json, 612KB / 229 msgs / 1 user_input
- **user/host**: davidwu / hfeg0pjn200 (10.129.40.209)
- **match_count**: 259 · tools: 164 schematic / 133 pyAether / 44 dbShape / 34 cellview / 29 netlist
- **shard C domain**: layout_aether (pyAether APR)

## 用户意图（逐字原文 UI#0）
> 帮我将打开的电路test2/AF_PPRCntEnd floorplan view 完成布局和布线.请使用placementConfig_v13.json 文件执行step 3 aeAutoPlacementFromDesign.

A-档 seed 合规：提出需求 + 明确目标（floorplan view 布局+布线，用 placementConfig_v13.json 跑 step 3），未给根因/修复方案 ✓。

## assistant 工具链（90+ tool_use）
1. 读 placementConfig_v13.json / launch_v13.sh / apr_v12.py / apr_v13.py / apr_v13.log（v13 在 Step 3 被中断）
2. RAG get_api_details: aeAutoPlacementFromDesign / aeOpenDesign / emyInitAether / aeGetCurDesign / aeGenAutoPlacementConfigFile / aeFindSDLSchematicForLayout / dbOpenCVByType / aeSaveDesign / doLogicRouter / RouteBaseOptions / RouteOptions / techFindLayer / emyLayer
3. skills: ae-auto-placement-from-design / do-logic-router / route-base-options / route-options / pyaether-automatic-place-route
4. editor 创建 apr_v14.py（Step0 emyInitAether → Step1 aeOpenDesign(floorplan,edit) → Step2 verify config → Step3 aeAutoPlacementFromDesign → Step4 aeSaveDesign → Step5 RouteBaseOptions → Step6 RouteOptions → Step7 doLogicRouter → Step8 save+summary）
5. run_commands 跑 launch_v14.sh → PID 798473 → 监控 CPU/内存
6. 5 个 route 迭代脚本（route2/route3/route4/route5 + debug），每个修复一个 doLogicRouter 错误

## 关键产物（gold 事实，逐字从 result log 提取）

### Placement (apr_v14_result.log)
- emyInitAether('adv') → OK (20.6s)
- aeOpenDesign(floorplan, edit) → True (23.0s)
- floorplan_initial: inst=262, shapes=4606
- placementConfig_v13.json 1760 bytes OK
- **aeAutoPlacementFromDesign → True (168.3s) — PLACEMENT OK** ✓
- RouteBaseOptions (pre-correct-init stub): setRouteMode NOT present / setAutoPin OK / setAutoPinOrient OK / setExistPin OK / setTrunkMode NOT present / setUsePinWidth NOT present / setAnalogConnect NOT present / setRouteByGroup NOT present
- doLogicRouter → False (0.0s) — ROUTING FAILED
- Total 214.3s, inst 262→262, shapes 4606→4606

### doLogicRouter 错误推进（3 个独立 precondition 依次修复）
| attempt | error_code | missing setter | resolution | next error |
|---|---|---|---|---|
| route2 (apr_v14_route2) | "Constraint name is invalid. (doLogicRouter)" | setConstraintGroupName | cstGetDefaultConstraintGroupName(le,"Wire")→"virtuosoDefaultSetup" | "No net available for routing" |
| route3 (apr_v14_route3) | "No net available for routing. (doLogicRouter)" | setRouteNets | 从 4606 shapes 提取 19 net names (emyShapeGetNetName) | "Layer rules cannot be empty" |
| route4 (apr_v14_route4) | "Layer rules cannot be empty. (doLogicRouter)" | setLayerRules | vector1D_oarLayerRule via techFindLayer (35 routing layers) | route5 in-progress |
| route5 (apr_v14_route5) | null (in-progress) | — | — | session 截断 |

- 19 nets: A, B, C, Ck, CkN, D, I4|net6, Q, R, RN, S, SN, Y, net11, net12, net13, pulsic_no_net, vcc!, vss!
- debug (apr_v14_debug, msg 205) post-init RouteBaseOptions 7 methods present: setAutoPin, setAutoPinOrient, setBoundaryLine, setConstraintGroupName, setExistPin, setLayerRules, setViaRules（setRouteMode/setTrunkMode/setUsePinWidth/setAnalogConnect/setRouteByGroup 仍 NOT present）
- aeGetRoutingLayers = 35 layers: NBP,TCP,CTA,M1A,V1A,M2A,V2A,M3A,V3A,M4A,TMA,HSV,PG,PC,MT2,CT,M1,V1,M2,V2,M3,V3,M4,V4,M5,V5,M6,V6,M7,FAM,FPA,HLV,BPA,RDV,RDL
- oarLayerRule / vector1D_oarLayerRule / oarViaOption class 存在
- techGetPrRoutingLayers = () empty

## A-档 评估
disqualified：依赖私有 /proj/train/V0_fillimplant_drgqa/workdir/davidwu/ 工作区（davidwu 私有，沙盒无写权）+ live Aether + pyAether + 私有 test2/AF_PPRCntEnd cell（davidwu 私有 OA 库）+ route5 doLogicRouter 最终结果未确定（session 在 route5 in-progress 时截断，无用户接受结果）。→ **B-档 synthesized L1-boundary**。

## B-档 合成（捕获确定性上游子任务）
捕获 **APR routing precondition diagnosis**（路由前置条件诊断）：给定 pyAether APR 执行 manifest（placement result log + RouteBaseOptions method catalog + 有序 doLogicRouter route attempts + tech routing layers），诊断 ①placement 是否成功 ②有序 routing error 推进 + 每个 error 映射到缺失的 RouteBaseOptions/RouteOptions setter + resolution API ③routing stage reached + final verdict。

签名 gold = 3-error 推进（Constraint name → No net → Layer rules），每个映射到缺失 setter + resolution API（davidwu 会话独有）。

**与既有区别**：DRCPatPlan-001 / DRQAPlan2Skill-001 = calibre/DRC plan；AutoCellFlowValidate-001 = cell flow validation；本案 = **pyAether APR doLogicRouter 路由前置条件诊断（error-progression + missing-setter 映射 + stage/verdict 分类）**，主题/断言独立。

## check.py 14 条断言 (k=14=k_check≥8, GATE PASS)
①[a] zip+py_compile+manifest 齐 + 4 candidate runs rc==0
②[b] A placement: aeAutoPlacementFromDesign=True / placement_ok=True / inst==262 / shapes==4606 / config_bytes==1760
③[c] A RouteBaseOptions: 7 present 含 setConstraintGroupName/setLayerRules/setViaRules；setRouteMode+setTrunkMode absent
④[d] A route_error_stages 含 3 个 grounded error 且有序（constraint→nets→layers）
⑤[e] A 每个 error 映射到正确 missing_setter（setConstraintGroupName/setRouteNets/setLayerRules）+ resolution_api（cstGetDefaultConstraintGroupName/emyShapeGetNetName/techFindLayer）
⑥[f] A constraint_resolution: method=cstGetDefaultConstraintGroupName / name=virtuosoDefaultSetup / resolved=True
⑦[g] A net_extraction count==19 + 独立从 A input 重计数 19
⑧[h] A layer_rule_resolution count==35 + via_techFindLayer=True + tech_routing_layer_count==35
⑨[i] A routing_stage_reached==3 + verdict==PLACEMENT_OK_ROUTING_STAGE3_LAYER_RULES
⑩[j] 跨输入守卫 B: placement_ok + inst==148(≠A 262) + net_count==24(≠A 19) + verdict stage3 + constraint=mynoiseSetup + layer count 28(≠A 35) + 独立重计数 24（击穿硬编码 A）
⑪[k] placement-failed 守卫 B2: aeAutoPlacementFromDesign=False → verdict==PLACEMENT_FAILED（杀 always-routing / naive_skip_placement）
⑫[l] early-stage 守卫 B3: constraint unresolved → verdict==STAGE1_CONSTRAINT_UNRESOLVED + stage==0（杀 always-stage3 / naive_always_stage3）
⑬[m] 确定性 B 3 次 md5 一致
⑭[n] 结构: 每个 route_error_stage 的 missing_setter 是真实 RouteBaseOptions/RouteOptions 方法名 + resolution_api 是真实 pyAether API 名

## 自验
- ref PASS 14/14 ✓
- 5 neg（fake_empty→a / fake_print_expected→d / fake_core_deleted→d / naive_always_stage3→j / naive_skip_placement→k）全 FAIL NEG_RC=0 ✓
- §4.9 (a) empty shell→a (b) only-print-expected→d (c) core-deleted→d 全 FAIL ✓
