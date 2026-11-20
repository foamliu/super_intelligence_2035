# Deepread: 1791782242441_8rxb1 · steveny@hfeg0pnd001 · mc=47

**Domain**: schematic_netlist (D)
**User original (U#0, single user turn, verbatim)**:
> 通过mcp 工具，获取api和桥接服务，实现：高亮当前打开的virtuoso design的schemetic view 中所有以net 打头的net。注意是virtuoso skill，不是pyaether。用户名是steveny

**意图**：在当前打开的 Virtuoso schematic cellview 里，把所有名字以 `net` 打头的 net 高亮出来；交付物 = Virtuoso SKILL 脚本（不是 pyAether）。

**对话流（32 msgs, 102KB, 单 user turn；其余均为 tool_result）**：
- U#0 提需求 → 助手走 RAG_MCP search_apis 三连（get current design open cellview / highlight net in schematic view / get nets of schematic cellview）
- 检索到的关键 API：`geGetWindowCellView`（取当前窗口 cellview）、`dbStartGenNet`（生成 net 迭代器）、`dbFindNetByName(d_cellView t_name)`（按名取 net）、`schHiHiliteLabel`（高亮 wire/inst label）、`leMarkNet`/`leUnmarkNet`（layout 标注 net）、`leHiMarkNet`（开 Mark Net form）、`geAddHilightSet`/`gePushHilightStack`/`geAddHilightRow`（highlight set 机制）
- 助手在 SandBox_MCP run_code 里探测函数存在性：
  - `functionp` undefined → 该 SKILL 风味不支持 functionp
  - `dbMarkNet(nil)` → **undefined function**（此环境无 dbMarkNet）
  - `dbStartGenNet(nil)` → **argument #1 should be a database object (type template "d")** → dbStartGenNet **存在**
  - `if` unbound → 用 `when`/`unless`（受限解释器）
- msg#31 最后一次 run_code（foreach errset 探测 leUnmarkNet/leMarkNet/leHiMarkNet/dbGetAllNet/geAddToHighlightSet/geAddHilightLine/geMarkNet）→ `code_sidecar_sigterm`（沙盒被杀，session 在此中断）

**关键正确点（从 trace 提炼）**：
1. 取当前 cellview：`geGetWindowCellView()`（或 `geGetEditCellView()`）
2. 取所有 net：`dbStartGenNet(cv)` 生成迭代器（已验证存在）；或 `cv~>nets`
3. 按名前缀过滤：net 名 `net_xxx` 才算，`xnet`/`mynet`（含但不起头）不算 → **前缀匹配，非子串**
4. 高亮：dbMarkNet 在该环境不可用 → 需走 highlight-set 机制（`geAddHilightSet`/`geAddToHighlightSet`）或 `schHiHiliteLabel`；trace 未得出最终结论即中断

**金标准状态**：trace 在 msg#31 中断（sidecar sigterm），**无用户接受的最终产物**。故采 B-grade synthesized：把「cellview net 列表 + 前缀 → 高亮计划（匹配 net 清单 + SKILL 指令片段）」抽成单文件 Python CLI，自包含、纯 stdlib、可离线判分。

**真实环境不可复刻点**：私有 Virtuoso session / steveny 真实 cellview / .zl/virtuoso 沙盒 / RAG_MCP API 检索 → 全部抽离；SUT 只看自包含 cellview.json + 前缀，产出 highlight_plan.json + highlight.il。

**维度正交检查**：既有 D schematic_netlist case 多为拓扑重构/网表清洗/verdict JOIN/SA 搭建/门库过滤/族配对/glob 解析/层级路径/cross-probe CSV/布尔对拍/svwf 展开等；本 case =「cellview net 按名前缀过滤 + 生成 SKILL 高亮指令片段」（前缀匹配非子串 + SKILL geGetWindowCellView/dbStartGenNet/geAddHilightSet 结构），机制/产物全不同。
