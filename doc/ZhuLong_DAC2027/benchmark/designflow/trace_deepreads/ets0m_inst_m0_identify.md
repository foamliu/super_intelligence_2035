# 深读笔记 · ets0m · 识别 instance 的 M0 + MXL/XL 区别

## trace 元数据
- session: `1793605922073_ets0m.messages.json`
- user / host: e0047695 @ hfeg0pkn005（NEW user）
- mc: 150；98 msgs；agent=lead；updated_at 2026-11-02T17:59Z
- 工具命中：aether:504 cellview:464 pdk:242 virtuoso:185 mixed-signal:102 schematic:86 techfile:54 pyaether:50（注：aether/cellview/pdk 多为搜索文档时的关键词，非工具运行；真实工具运行是 RAG_MCP__search_apis/get_api_details + SandBox_MCP__run_code(skill) 尝试）
- domain: **layout_virtuoso**（交付物是 Virtuoso SKILL 脚本 cxmt_getInstM0.il）

## 用户原话（单轮，2 条 user_input）
- U#0 (msg#0): `写个skill脚本，识别instance的m0`
- U#1 (msg#1): `MXL 和XL 的区别是什么`

两条都是「提出需求 / 表达目标」类，**未指出根因、未给修复方案** → A 档可用；但 cellview 未在 trace 中打开（SKILL 沙盒 10.129.8.124:25275 连接被拒），无用户附件 → 本案做 **B 档 synthesized**（合成 manifest：techfile layers + instances + terminology 探针）。

## assistant 工具链（98 msgs 的真实路径）
1. **路由 eda_agent skill**（msg#2）→ 读取 SKILL.md + 04_case_studies/case_007_highlight_nets_by_pattern_skill.md（msg#4-10）
2. **搜 CAD 源码 MXL/XL**（msg#4-14）：`/apps/imctf/cad/init/settings_cdns/skill` → XL=Virtuoso XL 模式（`hiGetAppType == "Virtuoso XL"`、`"Layout XL"`、`"Layout-GXL"`），MXL=0 hits
3. **RAG MCP 检索 SKILL API**（msg#13-81）：ddInst/ddShapes/ddPins/leGetCellView/leGetPinsInWindow/dbGetOpenCellViews/dbOpenCellViewByType/lxGetLXInfo/cphGetLayoutXLConfig
4. **搜 Aether 手册**（msg#29-74）：part_V_Layout_Editor.md / aether_tool_qa.md → Aether-LE 三档 Level 1/2/3（base / +SDL / +AMS PD），Layout XL = SDL binding 模式
5. **扫 PDK/techlib/user home 找 MXL**（msg#41-74）：0 hits（仅字体二进制伪命中）→ MXL 不是标准 Aether/Virtuoso 模式名
6. **写 cxmt_getInstM0.il**（msg#91，4214B 全 ASCII，cxmt_ 前缀）：
   - `CXMTLayerMatch(lpp name)` — tolower(car(lpp))==tolower(name) 大小写不敏感
   - `CXMTFindM0Layers()` — `geGetEditCellView()` → `cv->techFileID->layers` → `rexMatchp("^[mM]0" l->name)`
   - `CXMTGetInstM0(?layerName "m0" ?maxShapeReport 5 ?maxPinReport 20)` — `geGetSelSet()` + `typeOf(fig)=='instRef'` 过滤（无选中 fallback `cv->instances`）→ `inst->ddInst->ddShapes`（按 `shape->layer` 匹配）/ `inst->ddInst->ddPins` → 报告 master + M0 shape 数 + bbox + pin 名 + 汇总
7. **SandBox_MCP__run_code `load(".../cxmt_getInstM0.il")`**（msg#93）→ SKILL 沙盒未连接（`Connection refused by sandbox [skill] at 10.129.8.124:25275`），无法在线验证
8. **最终交付**（msg#97）：cxmt_getInstM0.il + MXL/XL 消歧（XL=Virtuoso XL 实锤 4 条证据；MXL=0 hits 如实说明，请用户补充出处）

## 6 个真实 Virtuoso SKILL 坑（本案 ground 的 pitfall）
| ID | 坑 | 正确做法（生成的 SKILL 代码须体现） |
|----|----|----|
| P1 | 取当前 cv 用 `geGetWindowCellView`/window 属性拿不到 layout cv | 用 `geGetEditCellView()` |
| P2 | 选中的 instance 要过滤；直接当 shape 处理会错 | `geGetSelSet()` + `typeOf(fig)=='instRef'` 过滤；无选中 fallback `cv->instances` |
| P3 | instance 内部的 shape/pin 不在 `cv->shapes`（那是顶层 shape） | 走 dd 对象模型：`inst->ddInst->ddShapes` / `->ddPins` |
| P4 | layer 名大小写不一致（PDK 写 `M0`，用户传 `m0`） | `tolower` 大小写不敏感匹配 |
| P5 | techfile 层名扫描要拿对入口 | `cv->techFileID->layers` + `rexMatchp("^[mM]0" l->name)` |
| P6 | 脚本须只读，不能改图 | 不得出现 `dbDeleteObject` / `dbCreateRect`/`dbCreatePath`/`dbCreateInst` / `dbReopen` |

## DISTINCT（与历史 case 对账）
- r232 SkillM1ShapeDeleteAudit：**删除** cellview 顶层 M1 shape（`cv->shapes` 过滤 + `dbDeleteObject`）。本案：**识别** instance 内部 M0 shape/pin（`inst->ddInst->ddShapes/ddPins`，只读）。对象域不同（cellview-shapes vs instance-internal-shapes）、动词不同（delete vs identify/report）、API 族不同（dbDeleteObject vs ddInst/ddShapes/ddPins + techFileID scan）。互补不重叠。
- ListInstCV-001：pyAether 脚本列出 view 全部 instance 名+master（`dbOpenCVByType`+`block.getInsts()`）。本案：Virtuoso SKILL 识别 instance 的 M0 shape/pin（dd 对象模型 + techfile 层扫描）+ MXL/XL 消歧。平台/对象/API/副任务全不同。
- r207 QaWidthPatternGen / r218b DrcQaWidthTypeGeom：DRC QA width pattern 生成。本案是 instance metal-layer 识别，不同。
- r230 VirtuosoStartupDiag / r223 VirtuosoLaunchRecipeGen：Virtuoso 启动诊断。本案不涉及启动。

## case 设计（B-synthesized, L1, k=18 a-r）
- **SUT 写** `inst_m0_identify_gen.py`（CLI `<manifest.json> -o <out.json>`，stdlib only）：读 manifest{meta, techfile{layers[]}, instances[{id,master_*,shapes[{layer,purpose,bbox}],pins[{name,layer}]}], target{layer}, terminology{mxl_hits_per_source[], xl_evidence[], xl_meaning}}，生成 SKILL 代码（CXMTLayerMatch/CXMTFindM0Layers/CXMTGetInstM0，规避 6 坑）+ 仿真 M0 识别（每 instance 的 M0 shape/pin 计数、master、汇总）+ MXL/XL 消歧报告。
- **A_run**（trace grounded）：RX_LIB/RX_Top/layout，techfile 6 层含 M0，3 instance（I1 RX_Inv M0=2/2，I2 RX_Nand M0=3/3，I3 RX_Buf M0=0/0），target=m0，mxl_total_hits=0 → verdict "not standard"。
- **隐藏 B**（反硬编码 A）：PLL_LIB/P_Top，techfile 4 层含 met0（target=met0 非 m0），4 instance（A1 4/2, A2 1/1, A3 0/0, A4 2/2），total_shapes=7 total_pins=5。
- **B2**（杀 always-found）：IO_LIB/PadTop，techfile 无 M0/met0，1 instance M1-only → m0_layers_found=[] total=0。
- **B3**（杀 always-zero-mxl）：mxl_total_hits=3（PDK 层表命中）→ verdict 不含 "not a standard"。
- **18 条①–⑱ a–r**：zip+1py / py_compile+stdlib / A JSON+8 keys / A exit0 / P1 geGetEditCellView / P2 geGetSelSet+instRef / P3 ddInst+ddShapes+ddPins / P4 tolower / P5 techFileID+rexMatchp / P6 readonly(no dbDeleteObject/dbCreateRect/dbCreatePath/dbCreateInst/dbReopen) / A m0_layers_found+instances_report / A total_shapes+total_pins / A mxl_xl(xl_meaning 含 Virtuoso XL + mxl_total_hits=0 + verdict 含 not) / A pitfalls_avoided=6 IDs / B met0+7+5 / B2 []+0+0 / B3 mxl_hits=3 + verdict not-contains "not a standard" / 3-seed 确定性。
