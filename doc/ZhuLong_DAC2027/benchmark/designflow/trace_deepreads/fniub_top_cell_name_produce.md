# trace deepread: fniub — top cell name retrieval via Virtuoso SKILL API

**session**: 1792223787830_fniub · user e0014566 · host hfeg0plg58 (10.129.35.82) · mc=14
**keywords**: cellview:114; dbget:14; netlist:12; virtuoso:6; schematic:4; ddgetobj:1
**size**: 24753 B / 9 msgs (1 user text input + 4 assistant tool_uses + 4 tool_results)
**model**: GLM-5.2
**domain**: schematic_netlist (Virtuoso cellview/schematic, SKILL API)

## 对话流

### U#0 (msg 0) — 用户需求（A-faithful seed）
> 请返回当前top cell的名称，使用virtuoso skill的API接口，使用run code工具执行

### assistant 工具链 (msgs 1-7)

1. **RAG_MCP_Server__search_apis** query="get current top cell name" lang=skill top_k=10
   → 返回 hdbGetTopCellName (sim 0.6593) / geGetTopLevelCellView (sim 0.643)

2. **RAG_MCP_Server__get_api_details** api_list=[hdbGetTopCellName, geGetTopLevelCellView] lang=skill
   + **RAG_MCP_Server__search_apis** query="get current design cell view name" lang=skill
   → hdbGetTopCellName(h_configId) 需要 config id（来自 hdbOpen）；geGetTopLevelCellView(da) 返回顶层 cellView ID
   → 第二次搜索返回 geGetWindowCellView / leEditDesignProperties / geGetTopLevelCellView / dbAllCellViews / hdbSetTopCellViewName / geGetEditCellView

3. **SandBox_MCP_Server__run_code** lang=skill username=e0014566 encoding=ascii
   ```skill
   cellView = geGetTopLevelCellView(hiGetCurrentWindow())
   if( cellView then
       printf("Top cell name: %s\n" cellView~>cellName)
       printf("Library: %s\n" cellView~>libName)
       printf("View: %s\n" cellView~>viewName)
   else
       printf("No top-level cellview found.\n")
   )
   ```

4. **tool_result** (msg 7):
   ```json
   {"response": "The code execution was successful",
    "print_log": "Top cell name: and2CSx1\nLibrary: stdcells_ac\nView: schematic",
    "error_log": ""}
   ```

### A#8 (msg 8) — 最终交付
表格输出：Top Cell = `and2CSx1` / Library = `stdcells_ac` / View = `schematic`，附 SKILL API 说明（hiGetCurrentWindow → geGetTopLevelCellView → ~>cellName/libName/viewName），并说明无窗口时返回 nil。

## 判读

- **用户意图**：获取当前 Virtuoso 设计环境中顶层 cell 的名称。单一、清晰、可 falsify。
- **真实 gold**：and2CSx1 / stdcells_ac / schematic（agent 真实执行 SKILL 获得的结果，用户接受）。
- **API 链**：geGetTopLevelCellView(hiGetCurrentWindow()) → cellView~>cellName/libName/viewName；nil 处理。
- **reframe**：B档 synthesized-reframe produce —— SUT 提交 Python 脚本 get_top_cell.py（pyAether 版），用 aeGetCurDesign() → emyDesign.cellName/libName/viewName（或 aeGetTopLevelCellView(aeGetActiveDa())），输出 JSON，处理 None。check 用 mock pyAether 在 3 个隐藏 B seed + nil case 上 subprocess 验证。
- **asset_fidelity**：synthesized-reframe（trace 用 SKILL，交付 reframe 为 pyAether Python；用户意图保持：获取顶层 cell 名称 via 设计 API）。
- **falsifiability**：3 seed (adcLib/SARComp3/layout + pllLib/PLLTop/schematic + rfLib/LNACore/layout) 与 A 完全不相交；nil case 测 None 处理；anti-hardcode 词边界正则查 A token (and2CSx1/stdcells_ac) 与 B cell 名 (SARComp3/PLLTop/LNACore)。

## case

- **case_id**: EDA-Eval-DesignFlow-TopCellNameProduce-001
- **D.jsonl**: 520→521
- **check.py**: 14 断言 a-n，k_check=k_rationale=14 ≥ 8 ✓
- **自验**: reference 14/14 PASS + 3 negatives (empty_shell/print_expected/delcore) 全 FAIL ✓
- **ledger**: fniub mark case

## 复用范式

- mock_pyAether.py + subprocess 真跑（承 r971 SchPinAddProduce / r975 OpenDmViewsProduce 范式）
- D 域 schematic_netlist produce-from-scratch 首例（top-cell-name retrieval via design API）
- NOFILE revival 第 7 例 case（r970-r975 连续 7 case streak，承 fz05e/5fjwc/tgumy/demod/3rdqj/xpue4）
- path-bug revival: fniub 原为 NOFILE-parked（flat path 不可读），子目录路径 24753B 可读
