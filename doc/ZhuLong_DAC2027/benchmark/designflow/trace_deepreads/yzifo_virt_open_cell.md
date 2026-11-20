# Deepread: 1793100700946_yzifo — Virtuoso 查询当前打开 cell SKILL 脚本生成

## trace_source
- session: 1793100700946_yzifo.messages.json
- user: colinxu
- host: hfeg0plg55 = 10.129.35.74 (ledger 旧记 NOFILE wrong-host, 实际在 10.129.35.74 /home/colinxu/.cline/data/sessions/1793100700946_yzifo/)
- mc: 46, keywords: cellview:151;virtuoso:138;analog:26;dbget:25;schematic:16;pyaether:14;aether:7;dbopencellviewbytype:5
- size: 65KB, 21 msgs, 1 real user turn
- domain: layout_virtuoso (C 线)

## 用户意图（逐字原文）
U#0: "帮我查看virtuoso当前打开的cell"
（唯一真实 user turn — 单一明确请求：查询 Virtuoso 当前打开的 cell）

## 助手 gold 链
1. A#1: skills(eda_agent) — 加载 eda_agent 技能
2. A#3: run_commands ls SKILL 案例目录 + list_allowed_files /home/colinxu/agentdir/train/V0_NCG_HF_Virtuoso (发现 _sandbox_status.py / add_testpin.il / delete_testpin.il 等)
3. A#6: read_files _sandbox_status.py + add_testpin.il + delete_testpin.il + get_agent_policy_status
4. A#9: run_approved_command _sandbox_status.py — /proc 扫描超时被终止
5. A#11: RAG search_apis "get current open cellview windows hiGetCurrentWindow dbGetOpenCellViews" lang=skill + run_approved_command _sandbox_status.py --no-proc-scan
6. A#14: RAG get_api_details [dbGetOpenCellViews, hiGetCurrentWindow, geGetWindowCellView, geGetWindowId] lang=skill — 确认 SKILL API 用法 + 确认环境: Virtuoso IC617ISR23, 当前无 GUI 会话运行
7. A#16: **editor 写 get_current_cell.il** — 核心交付物
8. A#18: read_files 验证 get_current_cell.il 写入正确
9. A#20: 文字说明环境现状 + 脚本用法 (Part A: hiGetCurrentWindow → geGetWindowCellView → lib/cell/view + editCellView + isModified/isSaved; Part B: dbGetOpenCellViews → 遍历列表 + 计数)

## gold 交付物: get_current_cell.il
路径: /home/colinxu/agentdir/train/V0_NCG_HF_Virtuoso/get_current_cell.il

结构:
- `procedure( CCSGetCurrentCell() let( (w cv cvs curLib curCell curView n ...) ... ) )`
- **Part A (focused window)**:
  - `w = hiGetCurrentWindow()` — 取当前聚焦窗口
  - `cv = geGetWindowCellView(w)` — 取窗口显示的 cellview
  - `cv->libName / cv->cellName / cv->viewName` — 取 lib/cell/view
  - `geGetEditCellView(cv)` — editCellView 标志
  - `cv->isModified / cv->isSaved` — 修改/保存状态
  - 处理 w==nil (无窗口) 与 cv==nil (窗口空) 两个 edge case → printf warning
- **Part B (all open cellviews)**:
  - `cvs = dbGetOpenCellViews()` — 取会话所有打开 cellview
  - `foreach(cv cvs) n=n+1; printf(" %2d. %s/%s/%s" ...)` — 逐个打印 + 计数
  - `printf(" total open cellviews = %d" n)` — 总数
  - 处理 cvs==nil (无打开) → "(no cellview is open)"
- 末尾 `CCSGetCurrentCell()` 自调用

## 档 B reframe 设计
- A 档 gold = live Virtuoso `load("get_current_cell.il")` 跑出真实报告 (依赖 live Virtuoso GUI 会话, 不可离线复现, 无 ≥8 硬断言牙)
- reframe 为 **fixture 驱动 Virtuoso open-cell 报告器 (Python 离线复刻)**:
  - 候选交付 `virtuoso_open_cell_report.py` (单文件 stdlib), 实现 SKILL 查询逻辑的等价 Python 复刻
  - 输入: mock Virtuoso session-state JSON (windows 列表 + current_window_id + open_cellviews 列表, 每个 cellview 含 libName/cellName/viewName/isModified/isSaved/editCellView)
  - 输出: 报告文本, 严格匹配 gold SKILL printf 格式
    - Part A: `== A. Current (focused) window ==` + window ID + `>> current cell = lib/cell/view` + editCellView + wasModified/saved
    - Part B: `== B. All open cellviews in this session ==` + 逐行 ` %2d. lib/cell/view` + ` total open cellviews = N`
  - 处理 4 个 edge case: 无窗口 / 窗口空 cellview / 无打开 cellview / 正常多窗口多 cellview
- visible A fixture: trace 语义示例 (1 窗口 1 cellview) + A 期望报告 (SUT 可见作数据形状示例)
- hidden B fixture: 不同 session 状态 (3 窗口 / 5 open cellviews / 含 nil cellview 边界) + B 期望报告 (不进 SUT 沙箱)
- A/B cellview 的 lib/cell/view 名全异 → 硬编 A fail B

## 意图审计判定: keep
- colinxu 真实意图 (查询 Virtuoso 当前打开 cell) 完整保留
- reframe 是 grounding: 把「live Virtuoso SKILL 查询」沉淀为「fixture 驱动 + 查询逻辑等价 Python 复刻校验」, 单文件化+离线化, 非加难
- SKILL API 语义 (hiGetCurrentWindow/geGetWindowCellView/dbGetOpenCellViews/cv->libName/cellName/viewName/geGetEditCellView/cv->isModified/isSaved) 全来自 trace gold, 未引入用户未要求的内容
- 2026-11-15 reaudit 后 flow-driving/script-completion 合法第 N 例

## C 域 layout_virtuoso SKILL open-cell-query reframe 子型
- 与 VirtCellNameFromIlProduce-001(.il 解析推断 cellview)/VirtBridgeStatusDiag-001(bridge TCP)/VirtuosoOpenCellQueryGen-001(生成 open 脚本)/TapPcellBot-001(pcDefinePCell pcell 生成) 正交
- 本案 = **SKILL open-cell 查询逻辑 fixture 驱动 Python 等价复刻** (hiGetCurrentWindow→geGetWindowCellView→lib/cell/view + dbGetOpenCellViews→遍历+计数 + 4 edge case)
