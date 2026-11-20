# 深读笔记 — sid 1787625078133_9ryp9（haoyut @ hfeg0plg49/hfeg0pkn003, mc=286）

- trace: `1787625078133_9ryp9.messages.json`（kanban/sessions JSONL 流式格式，3.5MB/31909 行/23 chat_done 轮/162 工具调用）
- 工具分布: run_commands 94 · SandBox_MCP_Server__run_code 37 · RAG_MCP_Server__search_apis 20 · ask_question 6 · read_files 3 · RAG_MCP_Server__get_api_details 2
- keywords: netlist:648 cellview:528 schematic:219 pyaether:211 aether:137 virtuoso:109 synopsys:58 dbopencellviewbytype:50

## 会话双主题

### Part 1（A#0–A#5）：Virtuoso/Aether 原理图层级下钻与连通性 — layout_aether（本 case 取材）
- U#0 原文逐字（纯意图，未给根因/修复 → A-faithful 合格 seed）：`你能通过这个view进入下一层层级吗`
- agent（cline lead，先 RAG search_apis 查 pyAether get current design/view → 因 pyAether 端口 58476 拒绝，切到 SKILL 运行时 10.129.35.74:32292）：
  - A#1 取当前视图 `iejoal_top/LOGICTOP/schematic`（window:2），用 `deGetEditCellView()`/`geGetWindowCellView(hiGetCurrentWindow())`；`mdeGetCurrentLibCellView`/`dbGetViewTypeName` 在该 SKILL 环境未定义。
  - A#2 连通性演示：取 `vss!` 网（14 terminals，接 14 个 `I_ANTENNAA54F_M2_{61..82}<239:0>` 天线实例的 vss 引脚）；实例属性 `I_BTHBEDGE_2`→`iejoal_top/LP6PIMCORE_BTHBEDGEL_22ull`，bBox `((932.60 1114.287)(934.75 1374.838))`。
  - **A#3（gold）层级下钻表**：L0 `iejoal_top/LOGICTOP/schematic` 2504 inst/1557 nets → L1 `I_ChannelLogic`→`iejoal_top/ChannelLogic_22ull/schematic` 1362 inst/2012 nets → L2 `I_SetIDDAmpOIP_22ull_2482`→`analogIP/SetIDDAmpOIP_22ull/schematic` 6 inst/4 nets。技术要点：**`dbOpenCellViewByType(lib cell view)` 三参数**打开 master cellview（加第四个 `"r"` 返回 nil）；**`inst~>cellView` 返回所在父层而非 master**；计数 `length(cv~>instances/nets/pins)`。
  - A#4 GUI 下钻：`deOpenCellView("iejoal_top" "ChannelLogic_22ull" "schematic" "schematic" <windowBox> "read")` 在 window:3 打开子单元成为活动窗口，原 LOGICTOP 保留。
  - A#5 启动目录 `/proj/iejoal/V0/workdir/haoyut`，HOME `/home/haoyut`，临时脚本 `/home/haoyut/.zl/virtuoso/`。
- 用户无追问 = 接受。

### Part 2（A#6–A#22）：PIM Verilog 回归仿真环境排障 — 非 shard C（spice_sim/digital，不取材）
- U#2 `你看看你能加载这个路径下的波形吗/proj/iejoad/V0/simdir/verilog/haoyut/verilog.pim.iejoad.post_TTTT/.../ncsim.shm/`（路径不存在）。
- agent 解释 `vsim`（Perl，基于 xrun/irun，LSF bsub）回归环境，提交 basiccheck（Job 206552 → verilog 队列），卡在 pre-exec `mkdir /tmp/...` 失败 7h+；最终根因：用户 PATH 的 `vsim`=/proj/shdc/sim/bin/vsim 是 SOS 旧副本（5/3，无 pim 分支 → 默认 x16、不铺源 → `ncverilog FILEMIS top.sv`），项目 `bin/vsim` 才支持 pim（→x24+完整 @lnfile）；最后差网表提取 `vsim -n`。

## 合成决策（B-档 faithful-seed-B-synthesized, L1-boundary, layout_aether）
- A-faithful 需 SUT 连真实 Virtuoso+Aether 读 iejoal_top 设计，SUT 沙盒只配 eda_flow MCP（无 RAG_MCP_Server、无该设计）→ 不可复现，故 B-档把层级结构放进 bundle，SUT 只做结构化渲染（与 r144 SpiceSimSkillGen 同口径）。
- gold = A#3 真实下钻表（L0/L1/L2 + 真实 inst/net/pin 计数 + 真实技术要点 dbOpenCellViewByType 三参数 / inst~>cellView 陷阱）。
- 泛化：bundle-driven `sch_hier_descent_report_gen.py`（CLI `<bundle> [--out]`/`--help`/`-h`/无参 exit1/坏 bundle 缺键 exit1+stderr），渲染 markdown = 标题 + 起始视图 + 层级下钻结果表 + 分层详情 + 技术要点 + 结论；stdout 报告 Report/Out/Levels/TopCell/TotalInstances/TotalNets/Depth。

## 失败模式（判分要拦）
① 硬编码 A 专属 design/lib/cell（iejoal_top/LOGICTOP/ChannelLogic/SetIDDAmpOIP）跨 bundle 穿 ② 漏层级表数据行 ③ 表行数/depth/cellview/inst/net/pin/via 不匹配 ④ stdout 聚合（TotalInstances=sum/Depth=max）算错 ⑤ 分层详情漏样例实例 ⑥ 技术要点漏条目 ⑦ 结论不含 design_name ⑧ 坏 bundle 仍写文件 ⑨ 非确定性（Out 路径混入 stdout 导致两跑不一致——判分对 Out 行归一化）。
