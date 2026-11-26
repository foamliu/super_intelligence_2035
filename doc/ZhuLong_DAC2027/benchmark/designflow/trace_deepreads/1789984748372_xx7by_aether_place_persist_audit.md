# 深读笔记 — 1789984748372_xx7by (davidwu @ hfeg0pjn200, mc=228)

- **会话**：215 msgs / 1.06MB，agent cline(lead) glm-5.3-flash，cwd=/home/davidwu，status=failed(terminal_marker=failed_external_process_exit，stale_session_reconciler，10-09 桌面进程死，非任务失败)。provider cxmt-glm。
- **tools 命中**：pyAether:195 / schematic:234 / dbGet:116 / virtuoso:48 / dbShape:29 / netlist:37 / cellview:27 / calibre:16。
- **domain**：layout_aether（pyAether autodesign 自动布局 aeAutoPlacementFromDesign + emyDesignSave 落盘审计）。

## 真实任务（USER#0 逐字，末行是真正需求）
USER#0 贴入一整份《PyAether 自动化布局布线（Place & Route）编排 Skill》文档（emyInitAether→dbOpenCV/openDesign→aeGenAutoPlacementConfigFile→aeAutoPlacementFromDesign→RouteBaseOptions/RouteNetOptions/RouteOptions→doLogicRouter 七步），末尾真正的需求逐字：

> 帮我将打开的电路test3/AF_PPRCntEnd floorplan view 完成布局.请使用script/data/placementConfig_v13.json 文件执行step 3 aeAutoPlacementFromDesign.

即：对已打开的 `test3/AF_PPRCntEnd` floorplan view，用 `script/data/placementConfig_v13.json` 执行 Step 3 `aeAutoPlacementFromDesign`。

## 关键产物（真实路径/数值，不脱敏）
- 配置：`/home/davidwu/.cline/scripts/data/placementConfig_v13.json`（1782 bytes，35 条 JSON 对象数组：preserveBoundaryEnabled=false / firstRatioType=0 / firstRatioValue=50 / secondRatioType=1 / secondRatioValue=1 / xSpace=1 / ySpace=1 / hornorPinPlacement=false / pinAutoPlacement=true / minPinXSpace=0 / minPinYSpace=0 / digitalModeEnabled=true / sharedCell=true / cellbBoundaryLayerEnabled=true / boundaryPurposeName=drawing / specifiedRowEnabled=false / specifyRowsNumber=1 / powerTermEnabled=true / powerTermName=`[AaDd]?[Vv][Dd][Dd].* [AaDd]?[Vv][Cc][Cc].* vcc*` / groundTermEnabled=true / groundTermName=`[AaDd]?[Vv][Ss][Ss].* ... vss* vbn*` / tapCellEnabled=false / crossCellEnabled=false / fillerCellEnabled=true / fillerCellNames=["TECHLIB/spacer/layout"] / capCellEnabled=false / hierarchyEnabled=false / similarStructureEnabled=false / templateString=""）。
- 入口脚本：`/home/davidwu/.cline/scripts/data/step3_place_final.py`（headless：不调 emyInitAether，用 dbOpenCV(schematic,"r") + aeGetCurDesign/openDesign(floorplan,"a")，建 SDL 映射 aeFindSDLSchematicForLayout，调 `pa.aeAutoPlacementFromDesign(le, se, CONFIG_PATH)`，**保存用 `pa.aeSaveDesign()`**）。
- 上次成功基线日志 `step3_placement_result.log`（20260921_153811，result=True，15.4s，aeSaveDesign:OK）。
- 工程 workdir：`/proj/train/V0_fillimplant_drgqa/workdir/davidwu`；cds.lib → SOFTINCLUDE ./setup/cds.lib.assign；`dbGetFullPath` → **`/home/davidwu/test3/AF_PPRCntEnd/floorplan/layout.oa`**。
- **两份 test3 库**：`/home/davidwu/test3/` 与 `/proj/train/V0_fillimplant_drgqa/workdir/davidwu/test3/`；批处理写到前者，后者 09-18 19:49 未动。

## 完整对话流 + 失败模式
1. **A#1-A#35**：agent 跑 `step3_place_final.py` → `[aeAutoPlacementFromDesign] -> OK, result=True (15.0s)`，`aeSaveDesign: OK`，Total 15.4s，Placement OK。写 `verify_placement_now.py` 统计 floorplan：**262 个顶层实例 / 4606 shapes**，declare 成功（修了 viewType `maskLayout`→`layout` 的 bug）。
2. **USER#37**：`你确定已经成功placer了吗？` — 用户质疑。
3. **A#38-A#79**：深度验证。`dbGetFullPath`→/home/davidwu/test3/.../layout.oa；`dbInstanceQuery` 返回 `emyArray_sp_SleHierData`（非普通 figure）；内省出 `obj.name/obj.cellName/obj.dbuOrigin/obj.orient`+`getPlacementStatus()`；262 顶层实例（stopLevel=1，objType=ScalarInst），27 distinct positions，x∈[0,286000] DBU，y∈[-645650,0]，22 distinct y 成行结构，`PlacementStatus: placed`。再次 declare 成功。
4. **USER#80**：`看来你还是没有执行place功能。目前floorplan view里面的版图还是通过SDL直接掉进来的。` — 用户指出 floorplan 内容是 SDL 掉入的原始位置，auto-place 并未真生效。
5. **A#81-A#106**：A/B 实验。v13 原配置重跑(12.9s)→262→262，**13 个实例 orient R0→MX**；改配置(xSpace 1→6,ySpace 1→6,ratio 50→20,rows 1→3,38.4s)→**16 个 R0→MX，无 origin 变化**（但测量盲区：append 模式 getName/getOrigin 抛异常退回 `inst_N`/`?`，origin 对比假相等）。修属性读取后重跑 AB 配置：**全部 26 个功能单元被移到全新坐标**（I25 `(83200,-584250)MX`→`(293500,194500)`，新区域 y 全正、3 行、混合 MX）→证伪"placer 没执行"。
6. **A#108-A#115（决定性根因）**：发现**最后矛盾**——Exp4(v13) 的 BEFORE 坐标与 Exp3 BEFORE 完全相同 → Exp3 的"保存成功"并未落盘。查 `aeSaveDesign` 文档：**"saves the activated design"**——保存的是当前激活（GUI 窗口）的设计！headless 批处理无激活窗口 → `aeSaveDesign()` **全程静默无效**。磁盘取证：`layout.oa` mtime **仍是 15:38:11**（今天 5 次运行 aeSaveDesign 都"OK"却从未落盘），磁盘内容=SDL 原始位置（26 个顶层单元全在负 y，如 I25 `(83200,-584250)`）。
7. **A#118-A#122（修复）**：改用 `emyDesignSave(le, msg)` → `True`，msg=""（无错）；**layout.oa mtime 15:38:11→20:14:15（更新）**；独立进程只读复核磁盘：I11 `(2000,30650)R0`、I18 `(19200,77850)MX`、I25 `(26200,20650)MX`、I10 `(58100,30650)R0`、I34 `(71600,77850)MX`、I37 `(78600,20650)MX`、I26 `(106900,77850)MX`、I27 ffrqLx1 `(33500,77850)MX`、I13 ffsqLx... —— 全在新正 y 行。agent 向用户复盘认错：**"您说得对——之前磁盘上确实只是 SDL 掉入的内容"**。
8. **USER#123/124**：用户重贴原任务 + `继续`。agent 进 Step 4-7 路由。**A#132 新警报**：磁盘取证 `layout.oa` mtime 变 **20:15:18** 且内容**回到 SDL 原始位置**（I25=(83200,-584250) 旧坐标）——20:14:15 保存后有另一进程（GUI/SDL update）20:15:18 又写回旧布局。会话在此 stale 结束。

## 教学点（判分锚）
1. **`aeSaveDesign()` 在 headless 下是静默 no-op**（只保存 activated/GUI 设计）→ 必须 `emyDesignSave(le, msg)` 才落盘。这是本案核心。
2. **"API 返回 True" ≠ "磁盘已更新"**：判 placement 是否真生效必须看 `layout.oa` mtime 变化 + 磁盘实例 origin 分布（SDL 负 y → auto-place 正 y 行），不能信 aeSaveDesign 的 "OK"。
3. A/B 配置实验 + 属性读取（`obj.dbuOrigin/obj.orient` 而非 getName/getOrigin getter）才能区分"内存布局成功"与"磁盘落盘"。
4. cds.lib SOFTINCLUDE 解析 + `dbGetFullPath` 确认物理库；两份同名库需文件级 mtime 取证。

## A/B 档判定
- A-档不可行：gold = 已落盘的 placed floorplan，依赖 live Aether OA + test3/AF_PPRCntEnd 设计 + 用户在 trace 末尾并未干净接受（20:15:18 又被 GUI/SDL 写回旧布局，会话 stale 失败）。沙盒 .75 无该设计。
- → **B-档 synthesized L1-boundary**（离线 stdlib Python，无 live Aether）：交付 `place_persist_audit.py`，输入 `<run_log> <forensics.json> <out.json>`，解析批处理日志（aeAutoPlacementFromDesign True/False + 时长 + aeSaveDesign OK + emyDesignSave True/msg）+ 磁盘取证 JSON（layout.oa 路径、mtime before/after、实例 name/cell/origin/orient、before_count、two_libraries、cds_lib_resolve），emit 审计 JSON：判定 `disk_save_verdict`(SAVED/SAVE_NOOP_HEADLESS/NOT_SAVED) + `verdict`(PLACEMENT_PERSISTED/PLACEMENT_IN_MEMORY_ONLY/PLACEMENT_NOT_EXECUTED) + mtime_changed + sdl_baseline + auto_placed + instance_count + non_origin_count + distinct_positions。
- 资产 A = xx7by 真实 no-op 场景（v13 + aeSaveDesign OK + mtime 不变 + SDL 负 y）；hidden B1 = 不同设计的 no-op 场景（杀硬编码 A）；hidden B2 = 修复后的 SAVED 场景（emyDesignSave True + mtime 变 + 正 y 行）→ 双场景杀"恒判 no-op"与"恒判 SAVED"两类作弊。
