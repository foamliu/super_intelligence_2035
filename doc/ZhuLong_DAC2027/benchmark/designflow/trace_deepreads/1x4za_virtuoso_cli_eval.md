# Deepread: 1787809753708_1x4za — virtuoso-cli Skill 评估 + 反馈报告

- **trace_source**: user=junxu, host=hfeg0pkn005 (10.129.2.14), session=1787809753708_1x4za.messages.json, mc=379, 329 msgs, 960KB
- **domain**: schematic_netlist (virtuoso schematic 搭建 + API 评估)
- **scan**: ssh_eda_search_20261122_172249/summary.tsv
- **台账**: claimed r1176 (schematic_netlist, fresh D-pure top-1200 第 1 名)
- **真实任务摘要**: 用户作为测试用户，通过 `/virtuoso-cli` skill 在 `iejoad_work` lib 下用 `stdcells_am` 门级单元搭建 `cli_test_fifo` 原理图（4 深×4 位 FIFO，83 门级实例+14 I/O pin，schCheck 0 error/0 warning），借此评估 virtuoso-cli 接口能否满足工作需要；多轮追问 API 短板后，最终交付一份结构化反馈报告给 developer。

## 任务弧（user_input 时序）
1. **MSG 0**（初始）: 建 cli_test_fifo schematic，用 stdcells_am 门级电路搭功能齐全的 FIFO
2. **MSG 147**: "你好像手写了很多 skill，python api 哪里不能满足你的需求吗" — 探 API 缺口
3. **MSG 167**: "注意到你几乎没有实际进行连线，都是用 net name 桥接的，这是为什么" — 缺画线 API
4. **MSG 197**: "为什么 netname 的 font 用 fix，观感很奇怪" — 字体硬编码
5. **MSG 208**: "为什么你从来不用 bus 线，很多重复的器件其实也能合并成 IXX<3:0>" — 缺 bus 封装
6. **MSG 224**: "bus 线要用尖括号" — `<>` vs `[]` 行为差异
7. **MSG 236**: "器件摆放很分散，中间大量空白区域" — 无布局辅助
8. **MSG 240**: "你觉得 api 设计上能否规避这一点" — API 设计建议
9. **MSG 258**（交付指令）: "结合以上所有信息，写一份反馈报告，我去交给 developer"
10. **MSG 325+**（尾声）: 调试 virtuoso-cli daemon 连接 bug（ipcIsAliveProcess 崩溃后误判 alive，RBStart 拒重启）

## 交付物（反馈报告原文，feedback.md）
路径：/home/junxu/.cline/skills/block-design/virtuoso-cli-feedback.md（host 上已清，原文从 trace MSG 263-277 editor new_text 提取）

### 报告结构
- 测试场景：iejoad_work/cli_test_fifo，4 深×4 位 FIFO，83 门级实例+14 I/O pin，schCheck 0/0
- 测试环境：IC617ISR23, stdcells_am 1573 cell, Python 3.6
- 三层 API 架构：Business API / raw `_exec` / CLI shell

### P0 — 功能缺失（需绕过 Business API 用 _exec）
1. **缺 symbol view 创建方法**：schPinListToSymbol 未封装，被迫 _exec 手写 SKILL。建议 `eda.schematic.create_symbol_from_pins(lib, cell)`
2. **缺 bus/vector 封装**：dbCreateBusNetDef/BusTermDef/VectorInstDef 未暴露。但 `<>` 透传可用（`add_pin('DIN<3:0>')`/`add_instance(name='Ibuf<3:0>')`/`name_net('DIN<3:0>')` 均 OK，vector inst 创建后 power net 显示 `<*4>vcc!` 确认展开）；`[]` 被 CXMT 检查拒绝（"Net name cannot start with special characters"），文档未提及。建议 add_bus_pin/add_vector_instance/add_bus_wire + 文档说明 `<>`vs`[]`

### P1 — 设计缺陷（影响输出质量）
3. **name_net 字体硬编码 "fixed"**：schematic.py L743 `schCreateWireLabel` 的 t_fontStyle 硬编码 "fixed"，签名无 font_style 参数。schCreateWireLabel 支持 9 字体（euroStyle/fixed/gothic/math/roman/script/stick/swedish/milSpec），Virtuoso 默认 "stick"。建议加 font_style 可选参数默认 "stick"
4. **add_instance 仅接受绝对坐标，无布局辅助**：bBox 返回 SKILL 字符串 `"((-0.125 -0.25625) (0.8 0.725))"` 需自行解析；get_symbol_pins 返回结构化 {name,x,y} 但相对 symbol 原点。实测坐标随意导致 81% 空白（50×50 面积仅 19% 有器件，行间距 9 vs FF 高 0.981，合理应 ~1.5）。建议 bBox 返回结构化 {x1,y1,x2,y2,width,height} + `get_cell_size(lib,cell)` 便捷方法

### 尾声 bug（补充反馈项）
- skill_bridge.il 的 `ipcIsAliveProcess(RBIpc)` 在 daemon 崩溃后仍返回 t，导致 RBStart 误判 "already running" 拒重启。需 RBStop()+RBStart() 或 `RBIpc='unbound` + RBStart() 强制清空

## 造题方向（待合成 · DEBT）
**Case 概念（L1，analysis/flow-driving 合法意图）**：用户给 SUT 一份 virtuoso-cli API 参考（attachment）+ 一段实测 transcript 摘录（展示了搭建 FIFO 时遇到的 4 类 API 短板），要求 SUT 产出一份**结构化反馈报告 JSON**（不是自由 markdown），字段固定：`{p0_gaps:[{id,title,evidence,suggested_api}], p1_defects:[...], behavior_notes:[...], overall}`。check.py 解析 JSON 断言：
- ≥2 条 P0（symbol view 缺失 / bus 封装缺失）
- bus 行为笔记含 `<>` 可用 + `[]` 被拒
- name_net 字体问题 + 默认应为 stick
- 布局问题 + bBox 应结构化
- 隐藏 B：换一份不同 transcript 摘录（不同 FIFO 配置/不同短板组合），报告字段需对应 B 的实测短板
- §4.2 subprocess：check 用 subprocess 跑候选脚本（feed B transcript → 产出 JSON）再解析
- 反硬编码：A 的短板清单跑 B 必须不匹配（B 短板不同）
- k≥8 断言

**为何未本轮合成**：预算（~40min）用于 MCP 第72次复测 + 候选筛选（top-1200 D-pure fresh 定位，10 条 fresh）+ 1x4za 深读（329 msgs/960KB + 反馈报告原文提取），合成来不及过 §4 全闸门（hidden B + ≥8 断言 + 3 负样本 + 自验 + pi 跑）。下轮基于本笔记直接合成。

## 候选筛选成果（r1176 解决 r1175 DEBT）
- top-1200 D-pure（mc≥5，domain 过滤）去重后 424 unique sid，与 4-shard ledger（4453 known sid）diff 得 **10 条 fresh**：
  - 1x4za(junxu,mc379,schematic)✅claimed · 04qh0(junxu,222) · hx63r · wlzg5(jiashengz,238,lvs+waveview) · xotrf(cliu,275,netlist) · 0yu3c(harrywu,265,analog) · 2kujt(steveny,243,pyaether) · 0wsvo(yingyu,204,cdl/netlist) · jcop7(dechaoc,221,drc+netlist) · 3byhk(dechaoc,243,drc+netlist)
- 方法：awk on .75 summary.tsv → 本地 diff 4-shard known_sids（awk-on-.75 法验证可行，r1175 DEBT 兑现）
