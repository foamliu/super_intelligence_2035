# jzzsv 深读 — SKILL 删除当前版图 M1 图形（layout_virtuoso）

- **trace**: `1782880367712_jzzsv.messages.json`（e03179 @ hfeg0pkn002, mc=495; 49 msgs; 27 user turns but仅 1 真实需求轮）
- **tools**: RAG_MCP_Server__search_apis(9) + RAG_MCP_Server__get_api_details(3) + run_commands(3) + SandBox_MCP_Server__run_code(10) + submit_and_exit(1, 被拒——该工具不可用)
- **agent**: lead v1; cwd /home/e0025768/devops/bundle（执行用户 e0025768，非会话用户 e03179——sandbox 桥接账号）

## 用户唯一需求轮（U#0, msg#0）
> `<user_input mode="act">删除当前版图在所有M1的图形，使用skill语言生成代码并执行。</user_input>`

纯需求表达，未给根因/修复 → A-faithful 合格；但无真实用户 attachment（cellview 已在 Virtuoso session 打开），资产须从 trace 重建 → 本案做 **B-synthesized**（prompt 场景化，ground 在真实 cellview/层/pitfalls）。

## assistant 完整调试链（10 次 SandBox run_code）
1. **RAG 搜 API**：search_apis("delete shapes in layout" / "get current design cellview" / "find shapes by layer" / "dbDeleteObject delete shape" / "get current window cellview") + get_api_details(geGetWindowCellView, dbDeleteObject, leHiDelete, geGetTopLevelCellView, dbStartGenLPToShape, dbStartGenLPPHeaderToShape, dbReopen, dbOpenCellViewByType)。
2. **v1 SKILL**（msg#15）：`geGetWindowCellView(hiGetCurrentWindow())` + `dbStartGenLPToShape(cv '("M1" "drawing"))` + while gen~>next 收集 + dbDeleteObject。→ **失败**：`'( )` quote 语法 error（line 18 col 52）。
3. **v2**（msg#17）：改 `list("M1" "drawing")`。→ **失败**：`cv~>name` 在 printf `%s` 中为 nil → "format spec. incompatible with data, argument #1 is nil"（cellview 拿到了但 name nil）。
4. **v3**（msg#21）：改 `geGetEditCellView()` fallback + `cv~>name` → 仍 nil format error。
5. **探环境**（msg#27-30）：`hiGetCurrentWindow()` 返回 `window:4`（有窗！）；`win~>displayCellView` = `db:0x1dcf491a`（**关键发现**：geGetWindowCellView() 返回 nil 但 win~>displayCellView 属性能拿到 cellview）；`hiGetAllWindows`/`dbGetCellViews` undefined function。
6. **列 shapes**（msg#31-34）：cellview = `TECHLIB_test/CT_Mark_P/layout`，mode="a"，isEditable=nil，3 shapes：
   - `db:0x3175eb9a` M0C/markcore
   - `db:0x3175eb9b` CT/drawing
   - `db:0x3175eb9c` M1/drawing  ← 目标
7. **试 dbReopen**（msg#40-41）：`dbReopen(cv "a")` 试图改可编辑 → 仍 isEditable nil → error "Failed to reopen"。**结论**：dbReopen 无效，但（见下）dbDeleteObject 仍可工作。
8. **v4 成功**（msg#42-43）：不依赖 isEditable，直接 `foreach shape cv~>shapes when(layerName=="M1" && purpose=="drawing") dbDeleteObject(shape)` → `dbDeleteObject` 返回 `t`，删除 1 个 M1 shape。**关键**：isEditable=nil 不阻止 dbDeleteObject（append mode "a" 允许改）。
9. **验证**（msg#44-45）：再跑 SKILL 数剩余 M1 → 0；剩余 shapes = M0C/markcore + CT/drawing。**SUCCESS**。
10. **submit_and_exit**（msg#47）被拒（工具不存在）；agent 文本确认完成（msg#48）。

## 金标准（用户实际接受）
- cellview `TECHLIB_test/CT_Mark_P/layout`：删前 3 shapes（M0C/markcore, CT/drawing, M1/drawing），删后 2 shapes（M0C/markcore, CT/drawing），M1/drawing 剩余 0。
- 删除 1 个 M1 shape，dbDeleteObject 返回 t。

## 6 类 SKILL pitfalls（最终正确代码必须规避）
- **P1** `geGetWindowCellView()` 返回 nil → 用 `hiGetCurrentWindow()~>displayCellView`（属性访问）
- **P2** `cv~>name` 为 nil → 用 `cv~>libName`/`cv~>cellName`/`cv~>viewName`
- **P3** `isEditable` nil 但 `dbDeleteObject` 仍工作（append mode "a"）→ 不 gate 删除于 isEditable，不调用 dbReopen
- **P4** 用 `cv~>shapes` 迭代 + `~>layerName`/`~>purpose` 过滤（不用 dbStartGenLPToShape 生成器——其 quote 语法易错）
- **P5** 用 `dbDeleteObject(shape)` 删除
- **P6** 验证：删后数剩余目标层 shape == 0

## 选料结论
- jzzsv = 真 SKILL 删除 layout shape 完整调试闭环 + 用户单轮纯需求 + 可形式化 6 pitfalls → **layout_virtuoso seed (52→53)**。
- DISTINCT from r231 SkillPyaetherTransAudit（SKILL→pyAether 翻译 bug 静态诊断）/ r226 PcellPatternGeoDiag（pcell 几何）/ r218b DrcQaWidthTypeGeom（DRC width 几何）——本案首次 ground on **Virtuoso SKILL 删除指定层 shape 的 API pitfall 诊断 + 删除仿真**（geGetWindowCellView nil / cv~>name nil / isEditable nil-but-deletable / dbReopen-failed / dbStartGenLPToShape-syntax / verify-count）。

## 案件设计（B-synthesized, L1-boundary）
- **SUT 写 `skill_shape_delete_audit.py`**（CLI `<manifest.json> -o <output.json>`, stdlib only）：读 layout manifest{cellview, target{layer,purpose}, shapes[]}，输出 JSON{skill_code, remaining_shapes, deleted_shapes, deleted_count, pitfalls_avoided[6], summary{total_before,total_after,deleted,target_layer,target_purpose,cellview}}。
- **A_run** = trace grounded（TECHLIB_test/CT_Mark_P, 3 shapes, target M1/drawing → 删 1 剩 2）。
- **隐藏 B** = 合成不同 cellview（如 ANA_LIB/InvX4/layout, 7 shapes 4 层, target MT2/drawing → 删 2 剩 5）击穿硬编码 A。
- **B2 clean guard** = 0 个目标层 shape → 删 0 剩全部，杀 always-delete。
- **B3 heavy guard** = 多目标 shape（5 个 MT2 + 其他）→ 删 5，杀 always-small-count。
- **k 条 a-r（18 条）**：zip/compile/JSON 键/退出 0/skill_code 含 ~>displayCellView 且不含 geGetWindowCellView(/含 ~>libName+cellName+viewName/含 dbDeleteObject/含 ~>layerName+~>purpose/含验证 count/不含 dbReopen/A deleted_count==1/A remaining==金标 2/A summary 3-2-1/A pitfalls==6 类/A 总数对/B 删 2 剩 5/B2 删 0 剩全/B3 删 5/3-seed sha256 确定性。
- negatives: empty_shell / print_expected / core_deleted / naive_hardcode_a / stub_no_skill_code 全 FAIL。
