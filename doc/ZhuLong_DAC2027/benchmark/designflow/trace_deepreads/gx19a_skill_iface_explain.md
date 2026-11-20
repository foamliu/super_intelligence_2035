# Deepread: gx19a — SKILL 脚本获取当前 design 接口 (RAG retrieval Q&A)

- **session**: `1793846320456_gx19a` (subdir `1793846320456_gx19a/`)
- **user/host**: steveny @ 10.129.32.189, mc=22 (1116_072610 快照)
- **domain**: schematic_netlist (kw_D=265: cellview:244, dbget:37, schematic:21; 99%D-pure)
- **trace**: 46KB messages.json + 2.4KB json, 15 msgs, agent=lead, 1 substantive user turn
- **model**: deepseek-v4-flash, exit_code=0 (completed)
- **trace 路径**: `.75` SSH → `10.129.32.189:/home/steveny/.cline/data/sessions/1793846320456_gx19a/`

## 用户意图（U#0 原话）
```
<user_input mode="act">用你的rag mcp 查一下skill脚本获得当前design到接口</user_input>
```
**意图**：用 RAG MCP 检索 SKILL 脚本，了解如何获取当前打开 design 的接口（端口/终端）。典型 retrieval + explain Q&A（verb "查一下…获得"）。

## 助手工具链
1. `RAG_MCP_Server__search_apis(query="获取当前design的接口信息", top_k=10, lang="skill")` → NO_RESULTS
2. 多角度重搜 ×3 并发：
   - `query="current design interface pin"` → dbGetPinConnection, cphSbDisplayIOPinInfo
   - `query="get current cellview design"` → leEditDesignProperties, schHiOpenOtherView, lxLaunchLayoutXL
   - `query="当前打开的schematic/layout设计的接口"` → schHiOpenOtherView, lxLaunchLayoutXL
3. 精确搜索 ×3 并发：
   - `query="cellview 端口 ports 接口 database"` → techGetDeviceCellView
   - `query="dbGetCellViewPorts get ports of cellview interface terminals"` → lmPrintTerm, pcGetParameters
   - `query="获取当前cellview的输入输出端口列表"` → dbGetCellViewInheritedTerm, pcGetParameters
4. `RAG_MCP_Server__get_api_details(api_list=["lmPrintTerm","dbGetCellViewInheritedTerm","dbGetCellViewPorts","geGetWindowCellView"], lang="skill")` → 详细签名
5. `search_apis(query="get current window cellview hiGetCurrentWindow geGetWindowCellView")` → geGetWindowRep, geGetCellViewWindow
6. 最终输出两步走结论 + 完整示例 SKILL 脚本

## 金标准（assistant 最终回答要点）
- **两步走**：① 取当前 cellview ID → ② 读 ports/terms
- **cellview API**：`geGetWindowCellView(hiGetCurrentWindow())`（主），`geGetEditCellView()`（in-place 编辑），`geGetWindowRep(hiGetCurrentWindow())`（别名）
- **端口读取**：`cv->ports`（属性，最直接），`dbGetCellViewPorts(cv)`（专用 API，等价 cv->ports），`cv->terms`（顶层 terminal），`lmPrintTerm(t_cellName, t_viewName)`（打印终端名/类型/宽度），`dbGetCellViewInheritedTerm(cv)`（inherited net 表达式终端）
- **port 对象字段**：`port->name`, `port->direction` (input/output/inout), `port->term->name`
- **完整示例脚本**：
  ```skill
  cv = geGetWindowCellView( hiGetCurrentWindow() )
  lports = dbGetCellViewPorts( cv )
  printf("Design: %s/%s/%s  interface port count = %d\n"
         cv~>libName cv~>cellName cv~>viewName length(lports))
  foreach( port lports
      printf("  %-12s dir=%-5s term=%-12s\n"
             port~>name port~>direction port~>term~>name)
  )
  ```

## Reframe (retrieval-Q&A → produce, per 11-15 令 + r864 plan)
- 真实交付物 = 口头知识回答（哪些 SKILL API + 示例脚本）；reframe = 通用 `skill_iface_explainer.py` 产结构化 `interface_report.json`
- 工具读 cellview spec JSON + rag_results JSON → 输出：① 从 cellview 提取 design_info/ports/terminals/port_count/terminal_count（数据提取，可对 B 客观验证）② skill_api_guide（从 RAG 噪声中筛出 cellview_apis + port_access_apis + example_skill_script，知识部分验证 API 名正确性）③ 确定性输出
- **Distinct vs** fx2mf(MatrixRunDirExplain)=FineSim 目录结构讲解 / XProbeHierGen=schematic 层级遍历 / InstArcDiagFix=inst 诊断修正 = **本例 SKILL API 知识检索 + cellview 接口提取（两步走 API 模式 + 端口字段提取）**

## Asset A (visible, real-ish)
- A/cellview_A.json: invx1/analogLib/schematic, 4 端口 (in/out/vdd/vss), 4 terminals
- A/rag_results_sample.json: 17 条 RAG 结果（含噪声 NO_RESULTS/dbGetPinConnection/leEditDesignProperties + 真正相关 geGetWindowCellView/dbGetCellViewPorts/lmPrintTerm/dbGetCellViewInheritedTerm/hiGetCurrentWindow）
- A/prompt.txt (verbatim): "用你的rag mcp 查一下skill脚本获得当前design到接口"
- A/task_brief.md: 交付接口说明（≤3 行）
- A/scenario.txt: 角色背景（EDA 工程师 + Virtuoso）

## Hidden B (anti-hardcode, fully disjoint from A)
- B/cellview_B.json: nand2/primitivesLib/schematic, 5 端口 (a/b/zn/vdd/vss), 5 terminals
- B/cellview_B2.json: bufx4/ioLib/schematic, 7 端口 (din/dout/en/vcc/gnd/vpp/vbb), 7 terminals — 双 cellview 反硬编码
- B/rag_results_B.json: 12 条 RAG 结果（不同顺序/噪声，仍含关键 API）
- names ∩ A = ∅ (vdd/vss 是电源地通用名除外); cellName/libName ∩ A = ∅

## 断言规划 (k=16, a-p)
a zip+py 候选 · b py_compile · c B 跑通产 report · d B report 6 顶层键 · e B design_info 匹配(非 A) · f B ports 5 个名匹配 · g B port 字段 name/direction/term · h B terminals 5 匹配 · i B port_count/terminal_count · j cellview_apis 含 geGetWindowCellView · k port_access_apis 含 dbGetCellViewPorts/lmPrintTerm/dbGetCellViewInheritedTerm 之一 · l example_script 含 geGetWindowCellView+hiGetCurrentWindow+printf · m example_script 含 foreach/for/while · n B2 跑通且匹配 B2(非 B,反硬编码) · o 确定性 B 连跑两次一致 · p 无 A 泄漏(invx1/analogLib)

## §4.9 退化提交回归
- (a) 空壳 empty_stub.py → FAIL (无输出)
- (b) 只 print 期望串 print_only.py → FAIL (硬编码 B 但 B2 不匹配)
- (c) 参考解删核心 hardcode_a.py → FAIL (读但忽略 input，用 A 数据)
- ref SELF-TEST PASS + 3 negatives 全 FAIL ✓ (negative_selftest.py 验证通过)

## 自验结果
- `python3 negative_selftest.py` → ALL CHECKS OK: ref PASS, all 3 negatives FAIL
- `python3 check.py <ref_zip>` → CHECK: PASS
- D.jsonl 467→468 (normal-apply 落盘 ✓)
