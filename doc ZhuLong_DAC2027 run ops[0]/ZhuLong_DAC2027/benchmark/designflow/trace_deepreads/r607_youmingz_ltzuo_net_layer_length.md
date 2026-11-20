# r607 deepread — youmingz / 1794469565658_ltzuo / net highlight + per-metal-layer routing length

**session**: 1794469565658_ltzuo.messages.json (167 msgs, 793KB)
**user**: youmingz @ hfeg0plg93 (10.129.8.225)
**mc**: 273 (pyaether:540; aether:261; drc:121; cellview:119; schematic:79; dbget:48)
**domain**: layout_aether (pyAether-dominant)
**pool status**: r538 peek REJECT "analysis: highlight+measure routing length" → r607 revive (B类误杀，2026-11-15 令 analysis 合法)

## 用户意图（核心 produce-task）

- UI#0 / UI#1（逐字）：「请帮我在NewDout的版图中高亮CLm12E这根线并统计其在各金属层到走线长度」
- UI#140（重申 + 中文要求）：「请帮我在NewDout的版图中高亮CLm12E这根线并统计其在各金属层的走线长度，并且在思考的时候用中文显示，我看不懂英文」
- UI#151（纠错）：「怎么可能没有，我直接点版图都可以点出来，一定是你没有认真去找，现在给我重新找，是CLm12E这根线，你不要去找不存在的东西，DqPreSfBegin这个根本就不存在」

**意图**：在 `drcpa_digital/NewDout/layout` 中定位名为 `CLm12E` 的网络，(a) 高亮它，(b) 统计它在各金属层（M1/M2/M3…）上的走线长度。这是 layout_aether 的 net-probe + per-layer-wire-length 统计任务，author-new-flow（提需求未给根因/方案）。

## agent 行为与关键产物

agent 用 eda_agent skill → search_apis 找高亮/长度 API → SandBox run_code 真 pyAether：
- aeOpenDesign('drcpa_digital','NewDout','layout') → 178 nets，顶层无精确 "CLm12E"（只有 LatCLm12E）
- net.getShapes()=0 → 走线在子块（hierarchical routing）：3 个 instTerm（D_CdqGen / D_CdqsGen / nor2IOLVx1_pc60）
- 尝试 dbTraverseHierPathTriggerFunc 子类化做层次遍历（2 callbacks fired，但只下钻到 net 名对齐的子块）
- 尝试 emyNetGetPinFigs + emyFigGetPinName 做边界 pin→内部 net 映射
- 递归扫描全层次找 text "CLm12E" → **超时**：Sandbox [pyAether] at 10.129.8.229:42591 did not respond within 30s（递归打开太多子块窗口把 Aether 进程拖垮）

## 结局（trace 未交付）

会话以 **sandbox 卡死** 收尾（#157-#165 连续 6 次 30s 超时，连最简调用都不响应）。agent 在 #166 中文说明情况、道歉，请用户恢复沙箱。**用户未接受任何结果**——这是一条 failed session（操作性失败：递归打开过多 cell 把 Aether 拖死），**不是任务非法**。

按 2026-11-15 令：failed-session / analysis 均非真实排除标准；用户意图（高亮 net + 各金属层走线长度）是真实 produce-task。可造。

## B档 mock-behavioral reframe（承 r602-r606 模式）

源 layout 在私有 Aether cellview（沙盒不可达，且 trace 已卡死）→ asset_fidelity=synth。把「高亮 net + 各金属层走线长度」参数化为纯 Python3 `net_layer_length.py <layout.json> <net_name> <out_report.json>`（stdlib only）：

- 输入 JSON layout dump：cell{name,view} + nets[{name,shapes}] + instances[{name,master,pinConnections[{pin,topNet}]}] + masterCells{cell:{nets[{name,pins,shapes}]}}
- shape: {layer, purpose, figType("path"/"rect"/"polygon"), points/xy}
- 算法：定位 net（精确名，case-insensitive fallback）→ 收集该 net 全层次 shapes：顶层 net 直接 shapes + 各 instance pinConnection 解析（pin→master 内含该 pin 的 net→其 shapes，递归）→ 按 metal layer(正则 ^M\d+$) 分组求走线长度
- 长度模型：path(wire/drawing)=manhattan 折线长(sum|dx|+|dy|)；rect(purpose==wire)=max(dx,dy)；pin rect / polygon / 非金属层 不计长度但计 highlight
- 输出确定性 JSON：{cell, net_name, found, total_length, per_layer{Mx:len}, shape_count, per_layer_shape_count{Mx:n}, highlight[{cell,net,shape_count}]}（sort_keys）

输入A(NewDout/CLm12E, 顶层0 shape, 2 instance 贡献, M1=12/M2=30/M3=50 total=92)；隐藏B(TopDqs/DqClkN, 0 top shape, 2 instance, M2=35/M3=40/M4=25 total=100, 含 PO 非金属 distractor)；隐藏B2(PreDrv/LatCLm12E, 顶层有直接 shape, 1 instance, M1=10/M2=18 total=28, 含 VIA1 distractor)反硬编。

16 条 a-p（结构2 + B 8 + 反硬编A 1 + B2 2 + 确定性1 + 鲁棒性1 + 详情见 check.py）。
