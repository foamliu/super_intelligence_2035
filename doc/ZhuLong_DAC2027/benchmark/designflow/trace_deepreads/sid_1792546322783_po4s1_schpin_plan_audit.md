# Deepread: 1792546322783_po4s1 (colinxu / hfeg0plg81)

- **user/host**: colinxu / hfeg0plg81
- **mc**: 248 (cellview 628, schematic 438, dbGet 198, virtuoso 22, skill 77, dbShape 1)
- **session**: 188 msgs / 3 user_input turns / 426KB
- **domain**: layout_virtuoso (Virtuoso SKILL schematic cellView ops)

## User inputs (verbatim, A-档 seed evaluation)
- UI#1 (i=0): `当前打开的cell是？` — pure query, no design goal → not A-档 seed
- UI#2 (i=10): `帮我高亮有pin的连线` — operation on current cell, no explicit design deliverable → weak
- UI#3 (i=151): `帮我在这个cell里创建一个TESTPIN，并且完成保存` — **提出需求 + 明确目标 + 未给根因/修复 → A-档 seed ✓**

## Agent tool chain (key)
UI#2 (highlight wires-with-pins):
- RAG search_apis × 6: `geAddHilightFig`, `schSchemToPinList`, `dbGet`, nets/shapes iteration
- SandBox run_code (SKILL) × 14: probe schematic cellView structure — `deGetEditCellView`→`db:0x1db4581a`, `cv~>figures` empty, `isOpen=nil` (schematic 几何层未装配), `schSchemToPinList("drjpa_analog" "AG_AnalogBankBuf" "schematic")` 返回 `(nil ports (portList...) prop (nil))` 结构
- 沙箱连接断 × 6 (`Connection refused`)，`sleep 25-45` 等待恢复
- 最终未完成高亮 (figure 层不可达)

UI#3 (create TESTPIN + save):
- RAG search_apis: `schCreatePin`, `schCreateSymbolPin`, `leCreatePin`, `dbSave`, `dbIsCellViewCounter`, `dbFindTermByName`
- get_api_details: **`schCreateSymbolPin(d_cvId d_master t_termName t_direction l_origin t_orientation [g_flatten] [g_powerSens] [g_groundSens] [g_sigType]) => t_pinFigId / nil`** — d_cvId 必须 editable symbol cellview；d_master = `dbOpenCellViewByType("basic" "ipin" "symbol")` 类，figures 拷贝进目标 cv；terminal 用 t_termName 创建；orientation R0/R90/R180/R270/MX/MY/R90MX/R90MY
- `schCreatePin(cvId masterCV termName direction offSheetP origin orientation)` — schematic pin 变体
- `dbSave(cv)` — 必须 write/append 模式；read 模式只能另存为新 cellview
- `dbFindTermByName(d_cellView t_name) => d_term / nil` — term 重名校验
- `dbIsCellViewModified(cv)` — 修改后保存前置
- SandBox run_code (SKILL): `dbOpenCellViewByType("drjpa_analog" "AG_AnalogBankBuf" "schematic" "schematic" "a")` → `db:0x1dc2581a` 但 nets=0/terms=0/bBox 全零 (空壳) ; `basic/iopin/symbol` master 正常 (bBox `((-0.1125 -0.0625) (0.1125 0.25625))`)
- **严重发现**: `schSchemToPinList("drjpa_analog" "AG_AnalogBankBuf" "schematic")` 返回 `(nil ports (nil) prop (nil))` — pinList 从 39 个端口变成 0 (i=165, "之前的 39 个端口全没了")，怀疑之前 "w" 模式打开清空数据
- agent 进入数据完整性调查：`list_allowed_files` → `find /home/colinxu /proj -maxdepth 5 -name drjpa_analog`，`CDS.log` 显示 Virtuoso 在跑但 `deGetEditCellView` "Not a valid windowid"
- **trace 在 i=187 截断**：agent 正在 `/proj` 下找库物理位置，TESTPIN 创建/保存 **未完成**

## A-档 disqualified 原因
1. 真实 cellView `drjpa_analog/AG_AnalogBankBuf/schematic` 是 colinxu 私有 OA 库（`/proj` 下，沙盒无权访问，CDS.log 显示 live Virtuoso 实例占用）
2. trace 末尾无用户接受结果（session 在调查中途截断，TESTPIN 从未创建/保存成功）
3. 无法在 .75 sandbox 复现完整 schCreateSymbolPin + dbSave 流程

## B-档 synthesized L1-boundary 主题
**Schematic Pin Plan Audit** — 捕获确定性上游子任务：
1. 解析 `schSchemToPinList(lib cell view)` 返回的 SKILL disembodied proplist 原文 `(nil ports (portList) prop (nil))` → 提取 ports (name, direction)
2. 数据完整性审计：ports_count == 0 且 prior_count > 0 → `DATA_WIPE` 告警
3. `schCreateSymbolPin` 计划验证 (API 契约)：
   - master_lib ∈ {basic, analogLib}, master_view == "symbol"
   - master_cell ∈ {ipin, opin, iopin, opinOut, bidirectional} 且与 t_direction 一致 (ipin→input, opin→output, iopin/opinOut/bidirectional→inputOutput)
   - t_termName 不与现有 terms 重名
   - l_origin = 2 元数值 list
   - t_orientation ∈ {R0 R90 R180 R270 MX MY R90MX R90MY}
4. `dbSave` 前置验证：cv_open_mode ∈ {a, w}
5. 预测 post-create term inventory (current_terms + [new_termName] if plan valid)
6. 输出结构化 manifest JSON (纯 Python3 stdlib, 离线)

**与既有区别**：
- AddCellPin-001 (hxh3n, colinxu) = layout `dbCreatePin` + API call 序列提取
- PinFloatAether-001 = pyAether float-pin 检测
- PortPropagate-001 = port 跨层级传播
- 本案 = **schematic `schSchemToPinList` SKILL list 结构解析 + 数据完整性 (39→0 wipe) 审计 + `schCreateSymbolPin` API 契约验证 + dbSave 前置 + post-create term 预测**，主题/断言独立

## Gold (B-档 synthesized)
- **A 输入**: AG_AnalogBankBuf/schematic, 39 ports (prior=39), valid plan (TESTPIN, input, basic/ipin/symbol, (10 20), R0), mode "a" → integrity OK, plan VALID, post-create terms=40, dbSave OK
- **hidden B**: AG_AnalogDCCore/schematic, 24 ports (prior=24), valid plan (CLKIN, input, basic/ipin/symbol, (5 5), R90), mode "a" → integrity OK, plan VALID, post-create terms=25
- **hidden B2** (cross-input guard, data-wipe): `(nil ports (nil) prop (nil))` 空, prior=30, plan valid, mode "a" → DATA_WIPE alert, integrity FAIL
- **hidden B3** (cross-input guard, invalid plan): 24 ports, plan master=analogLib/opin/symbol but direction=input mismatch → plan INVALID
