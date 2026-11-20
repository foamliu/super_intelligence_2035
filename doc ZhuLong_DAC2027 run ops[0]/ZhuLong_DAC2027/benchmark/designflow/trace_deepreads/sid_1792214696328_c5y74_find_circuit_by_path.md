# Deep-read: tongni / 1792214696328_c5y74 (hfeg0pfn119, mc=379)

## meta
- user: tongni, host: hfeg0pfn119, session: 1792214696328_c5y74
- mc=379, tools: pyAether 530 + cellview 118 + schematic 88 + netlist 67 + dbGet 63 + calibre 6 + virtuoso 3
- cwd: /home/tongni/Desktop, model: deepseek-v4-flash
- status: **failed** (exit 1), started 2026-10-17 05:24, ended 2026-10-19 00:55
- agent: lead; system_prompt = "pyAether 代码工程师"; skill preamble auto-loaded: aether-tool-qa / argus-tool-helper / Spice_Agent (均与实际任务无关，仅作为 skill 上下文注入)

## 真实任务轮（A-档 seed 候选）
- msg[4] (after Spice_Agent skill preamble) 逐字原文：
  **「帮我写一个aether中可以使用的脚本，把XI_DDR6TOP_R.XI_Array32GTop_0.XI_Array16G_PSD0.XI_Array2G_PSD0_BGAB.XI3粘贴到弹窗里面可以找到对应的电路」**
  = 纯需求委托轮，用户提出需求，未给根因/未给修复 → 合规 A-档 seed。
- 后续 refine 轮：
  - msg[182]「这个脚本以什么形式运行 快捷键吗」
  - msg[189]「请帮我改成快捷键脚本load进去就可以使用」
  - msg[222]「F2有反应，但是搜索不到」(bug 报告)
  - msg[232]「没有反馈结果」(bug 报告)

## assistant 工具链
- 148 tool_use：RAG_MCP_Server__search_apis 59 / RAG_MCP_Server__get_api_details 21 / editor 28 / run_approved_command 19 / read_files 7 / list_allowed_files 4 / SandBox_MCP_Server__run_code 3 / run_commands 3 / search_codebase 3
- 主产物文件：`/home/tongni/Desktop/find_circuit_by_path.py` (6945B, 178 行, 多轮 editor 迭代 msg 162→252)
- 辅助：`/home/tongni/Desktop/design/ldo/probe_aether.sh`、`/home/t0002962/Desktop/design/ldo/selfcheck.py`（探针/自检，非核心）

## gold 评估
- 最终 `find_circuit_by_path.py`（Oct 17 14:09 末版，已 scp 回本机）：
  - `descend_hier_by_inst_path(top_design, path_str, verbose)`：逐级 `dbFindInst` → `emyRefGetMasterName` 取 master LCV → `dbOpenCV` 打开下一级，返回最深 "lib/cell/view"
  - `_FinderCallBack(aeBaseAppFormCallBack)` form 回调：取 pathField → descend → `aeOpenDesign` 打开最深 cell
  - `run_finder()`：`aeCreateStringField` + `geCreateAppForm` + `geDisplayForm`
  - `bind_hotkey(key, apptypes)`：`aeSetBindKey` 绑 F2 on layout/schematic/symbol
  - `_auto_install()`：load 时 `emyInitAether` + `bind_hotkey`
  - 加了 `_log()` 写 `finder_debug.log`（应对用户「没有反馈结果」）
- **A-档 disqualified**：trace 末尾 status=failed；用户最后两轮是 bug 报告（「搜索不到」「没有反馈结果」），assistant 末轮(msg 254)请用户重测并把日志发回，**用户未回复、未接受** → 无 user-accepted gold。
- 故本轮作 **B-档 synthesized**：以 trace 真实任务为 seed（trace_source 保留原值），参考 assistant 最终脚本重建干净金标准；隐藏 B 用不同 lib/cell/inst 名 + 同深度（libB/soc_top, U_PLL→U_VCO→U_CLKBUF）；判分桩驱动真跑 descend。

## 主题与既有 case 区别
- HierJump-001 (shuoran)：pulldown 菜单 + `sleGuiDescendRead` (read-only descend) + `geCreatePullDownMenuEx`
- HierDescend-001 (fxian)：schematic descend via mock OA db (CLI orchestrator, 无 Aether GUI form)
- 本案：**Aether GUI 输入表单(粘贴路径) + dbOpenCV 链 + aeOpenDesign 打开最深 + F2 hotkey**，API 面不同（aeCreateStringField/geCreateAppForm/aeSetBindKey/aeOpenDesign），交互不同 → 非 near-duplicate。

## 决策
- domain: layout_aether（11→12），track: synthesized，l_level: L1-boundary（离线 Python + 桩 pyAether 注入，subprocess 真跑候选 on hidden B）
- case_id: EDA-Eval-DesignFlow-FindCircuitByPath-001
- 已 claim → mark case；jsonl 追加 EDA-Eval-DesignFlow_C.jsonl
