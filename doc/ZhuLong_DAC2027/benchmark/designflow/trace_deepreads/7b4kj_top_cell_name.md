# Trace Deepread — 7b4kj (e0014566@10.129.2.10, mc=23, schematic_netlist/cellview)

**session**: `1792214069125_7b4kj` (26 msgs, 72KB messages.json)
**user**: e0014566 @ 10.129.2.10 (hfeg0pkn002 系列)
**scan keywords**: cellview:173 / virtuoso:27 / dbget:4 / cadence:4 / schematic:2 / dbopencellviewbytype:1
**mc**: 23 (mc≥10 池 fresh, D-pure)

## 用户意图（逐字 U#0）
`<user_input mode="act">请返回当前top cell的名称，使用virtuoso skill的API接口，使用run code工具执行</user_input>`

→ 用户要当前 Virtuoso 窗口的 **顶层 cell（top cell）** 名称，要求用 SKILL API + run_code 工具执行。

## assistant 工具链（关键步骤）
- **U#1 RAG search_apis×2**：query="get current top cell name of design" + "get current design cellview"
  - 命中：hdbGetTopCellName / geGetTopLevelCellView / schHiReturnToTop / leEditDesignProperties / deOpenCellView / geGetWindowCellView / geGetEditCellView / hiGetCurrentWindow
- **U#4 get_api_details**：api_list=[geGetTopLevelCellView, hiGetCurrentWindow, geGetWindowCellView, deGetCellView]
  - 确认 `geGetTopLevelCellView([w_windowId]) => d_cellview / nil` —— 取顶层 cellview（区别于 geGetWindowCellView 取当前显示 cellview、geGetEditCellView 取 in-place 编辑子 cell）
- **U#9 SandBox run_code(lang=skill)**：写出 `procedure(getTopCellName())` —— `hiGetCurrentWindow()` → `geGetTopLevelCellView(win)` → `topCV~>libName / ~>cellName / ~>viewName` → printf + return list
- **U#10-18 执行失败**：所有 SKILL run_code（含最简 `plus(1 2)` / `printf("hello")`）均报 `Unknown SKILL error` —— **headless 沙盒无打开的 Virtuoso 交互会话**，环境层故障，与代码逻辑无关
- **U#19+**：转 run_approved_command(probe_sandbox.sh) 探查环境，session 截止于 U#25

## 金标准判定
- trace 末尾**无用户接受的真实工具产物**（SKILL 沙盒全失败，session 未闭环）→ 不符合 A 档「金标准=trace末尾用户实际接受的结果」
- **代码逻辑正确**（API 链 hiGetCurrentWindow→geGetTopLevelCellView→~>libName/~>cellName/~>viewName + nil 守卫），可作为 B 档 synthesized 的金标准参考
- 关键判别点：`geGetTopLevelCellView`（顶层）vs `geGetWindowCellView`/`geGetEditCellView`（当前显示/编辑子 cell）—— 用户问的是 top cell，错用 API 会返回子 cell 名称

## 跨 shard / 重复核查
- e0014566 已有 68 个 cased session（高频用户），但本 session `7b4kj` 未被 cased（fresh-not-cased）
- 与 r865 SkillIfaceExplainer-001（steveny gx19a，geGetWindowCellView+dbGetCellViewPorts 取 ports）**意图不同**：本 case 取 top cell **名称**，r865 取 design **接口**；API 链不同（geGetTopLevelCellView vs geGetWindowCellView+dbGetCellViewPorts）；deliverable 不同（top_cell name vs ports/terms 列表）
- 与 PyAetherCurDesignApi-001（pyAether 取当前 design，Python 而非 SKILL）工具栈不同

## case 落库
- case_id: `EDA-Eval-DesignFlow-TopCellNameResolver-001`
- 档位: B synthesized (trace-faithful prompt = 逐字原话)
- domain: schematic_netlist
- 16 断言 (a-p): 见 reference/TopCellNameResolver-001/check.py
- hidden B: window_spec_B (topCellView=primitivesLib/TopAmp, edit cell=analogLib/amp3 distractor)
- hidden B2: window_spec_B2 (topCellView=null 边界, edit cell=ioLib/bufx4)
- A-leak tokens: topInvChain / myLib
- 自验: ref SELF-TEST PASS + 3 negative (empty_stub/print_only/hardcode_a) 全 FAIL + §4.9 (a)(b)(c) 全 FAIL ✓
- k_rationale == k_check == 16 ≥ 8 ✓
- normal-apply D.jsonl 468→469
