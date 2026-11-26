# 6ro9q deepread — current-window schematic name query

**session**: 1794383219607_6ro9q
**user/host**: e0047722 @ hfeg0plg75 (10.129.8.125)
**mc**: 15 (cellview:73 / schematic:16 / virtuoso:10)
**domain**: schematic_netlist (clean D — cellview+schematic 双 D-keyword)
**messages**: 12 (6 user + 6 assistant)
**ts**: 2026-11-11 15:46 ~ 15:46 (一轮 ~14 分钟)

## 用户意图（逐字）

- **U#0** (act 模式): 「请获取当前virtuoso打开的原理图名称。」
- **U#8** (act 模式): 「继续」——前一轮 assistant 末行 `sformat()` 报错（SKILL 无此函数），用户让继续 → assistant 改用干净版本重跑

只取「提出需求」轮 → **U#0** 为 A 档任务说明（U#8 是修复后续，不另作 prompt）。

## Assistant 工具链

1. `search_apis("get current window cellView libName cellName viewName", lang=skill, top_k=5, sim=0.6)` → top 5:
   - `geGetWindowCellView` (sim 0.7648) — "Returns the ID of the cellview displayed in a window." ← 正解
   - `geGetWindowRep` (sim 0.7461) — alias for geGetWindowCellView
   - `geGetTopLevelCellView` (sim 0.7173) — "Returns the ID of the top-level cellview displayed in a window." ← 干扰项（用户要"当前打开"=displayed，不是 top-level）
   - `geGetCellViewWindow` (sim 0.7162) — reverse lookup (cellview → window)
   - `ddsGetLibManLCV` (sim 0.7148) — library manager selection
2. `get_agent_policy_status()` → policy active
3. `get_api_details([geGetWindowCellView, hiGetCurrentWindow, hiGetWindowList], lang=skill)`:
   - `geGetWindowCellView([w_windowId]) => d_cellview / nil` — Returns the ID of the **cellview displayed in a window**; "The cellview being displayed in the window can be different from the cellview being edited, as returned by `geGetEditCellView`, if you are currently editing a cell in place." Example: `geGetWindowCellView( hiGetCurrentWindow( ) )` → db:123456
   - `hiGetCurrentWindow() => w_windowId / nil`
   - `hiGetWindowList()` → list of all open windows (非当前窗口)
4. `SandBox run_code (lang=skill)`:
   ```skill
   let( (win cv lib cell view)
     win = hiGetCurrentWindow()
     cv = geGetWindowCellView( if(win win printf("null window") ) )
     if( cv
       then
         lib  = cv~>libName
         cell = cv~>cellName
         view = cv~>viewName
         printf("Current window id: %L\n" win)
         printf("Library : %s\n" lib)
         printf("Cell    : %s\n" cell)
         printf("View    : %s\n" view)
         printf("FULL    : %s\n" sformat(nil "%s/%s/%s" lib cell view))   ; ← ERROR: sformat undefined
       else
         when(win printf("Window is empty or cellview is nil\n"))
         unless(win printf("There is NO current window.\n"))
     )
   )
   ```
   - **Result**: `*Error* eval: undefined function - sformat` (line 17). 但 `print_log` 成功打印：
     - Current window id: window:2
     - Library : TECHLIB
     - Cell    : ALL_gates
     - View    : schematic
5. User: "继续" → assistant 解释 sformat 应为 sprintf，rerun 干净版本（去掉 sformat 行）→ success:
   - Library : TECHLIB
   - Cell    : ALL_gates
   - View    : schematic

## 金标准（用户实际接受的结果）

- **displayedCellView (geGetWindowCellView)**: TECHLIB / ALL_gates / schematic
- **windowId**: window:2 (数值化为 2)
- 用户停在顶层，displayed == top（无 in-place editing）
- 末轮 assistant 给出表格式结果 + 解释 sformat 错误，用户未再追问 → 接受

## Trace 教训（判分需考）

1. **API 选择**: 用户要"当前打开的原理图名称" = **displayed cellview** → `geGetWindowCellView` 正解；`geGetTopLevelCellView` 是干扰项（top-level 是顶层，descend into sub-cell 后与 displayed 不同）
2. **SKILL `sformat` 不存在**: 必须用 `sprintf` 或分行 printf。本 trace 教训对应 TopCellNameQuery-001 的 `if(cv then ...)` empty-clause 教训——SKILL 多行 if/then 解析失败要用 `when()`
3. **nil 守卫**: `geGetWindowCellView` 可能返回 nil（window 空或无当前窗口）→ 必须 `when(cv ...)` 守卫

## 与已有 case 区分（避免重复）

| 维度 | TopCellNameQuery-001 (r869/9vjrk) | **CurWindowSchematicName-001 (r872/6ro9q)** |
|---|---|---|
| 用户意图 | "请返回当前top cell的名称" | "请获取当前virtuoso打开的原理图名称" |
| 正确 API | `geGetTopLevelCellView` | `geGetWindowCellView` |
| 干扰 API | `geGetWindowCellView` (displayed ≠ top) | `geGetTopLevelCellView` (top ≠ displayed) |
| 用户 | e0014566 | e0047722 |
| 金标准 | TrimDelay / drjqa_stdcells / schematic | TECHLIB / ALL_gates / schematic |
| SKILL 教训 | `if(cv then)` 解析失败 → `when()` | `sformat` 未定义 → `sprintf`/分行 printf |
| RAG query | "get current top cell name" | "get current window cellView libName cellName viewName" |
| RAG top1 | hdbGetTopCellName (sim 0.66) | geGetWindowCellView (sim 0.76) |

两 case 为**镜像**：相同 RAG 噪声族（geGetWindowCellView/geGetTopLevelCellView 都出现），但**正解相反**——TopCellNameQuery 排除 geGetWindowCellView，CurWindowSchematicName 排除 geGetTopLevelCellView。在隐藏 B 中可用 displayed≠top 的场景强制区分（若 candidate 混淆两 API，B 上必报错 cell）。

## 合成方案（A 档 trace-faithful）

- **prompt**: 逐字 U#0「请获取当前virtuoso打开的原理图名称。」
- **scenario**: 用户停在顶层（displayed==top，匹配 6ro9q trace 实情）
- **asset A**: window_spec_A (TECHLIB/ALL_gates/schematic, windowId=2, displayed==top) + rag_results_A (5 候选真实 RAG + 8 干扰)
- **hidden B** (反硬编码): window_spec_B 用不同 cell (analogLib/invx1/schematic, windowId=1) 且 **displayed≠top** (topCellView=TopAmp/primitivesLib, displayedCellView=invx1/analogLib) — 强制 candidate 报 displayed 而非 top
- **hidden B2** (边界): 空窗口 windowId=99, hasWindow=true, displayedCellView=null, topCellView=null — 验证 nil 守卫
- **reframe**: L1 Python-on-JSON `cur_window_schematic_name.py` 读 window_spec + rag 产 `cur_window_schematic_report.json`
- **判分**: 16 断言 a-p（mirror TopCellNameQuery-001 但正解 API 翻转 + sformat 教训）
- **A-leak tokens**: TECHLIB, ALL_gates
