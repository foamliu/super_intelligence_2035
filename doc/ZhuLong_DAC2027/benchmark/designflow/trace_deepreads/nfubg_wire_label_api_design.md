# Deep-read: 1789970881163_nfubg (junxu @ hfeg0pkn005, mc=350)

**Claimed**: 2026-11-23 (shard D, schematic_netlist)
**Trace host/IP**: 10.129.2.14
**Session file**: `/home/junxu/.cline/data/sessions/1789970881163_nfubg/1789970881163_nfubg.messages.json` (902 KB, 204 msgs)
**Keywords**: virtuoso:1075;schematic:471;cellview:176;dbopencellviewbytype:39;rtl:36;pyaether:27;cadence:21;dbget:17

## 用户真实意图（提炼）
用户（junxu，virtuoso-cli skill 的开发者）与 assistant 协作设计 virtuoso-cli skill 的 schematic API 缺失能力，聚焦 **wire/net 名称修改的两种语义**：
1. **rename_net(net)** — 全局重命名网络（改名字，不改物理连接；网络上所有 label + pin 归属跟着变）。
2. **move pin to net（pin 级改线）** — 把器件某 pin 从 net A 改连到 net B（`I0.A` 原连 net `data`，改连 net `ctrl`），物理 wire 不必删重建。

用户明确约束：「layout 和 ocean 先不管」「尽量保持精简，不要 api 膨胀，能复用的尽量复用」。

## 关键发现 / 工具链
- 现有 `delete_wire_by_net(net)` 是**网络级**粒度——会删整条 net 的所有 wire shape，无法做 pin 级改线；用户指出组合方案（删 + 重建）会破坏中间状态、累及同 net 上其他 pin（I2.C/I3.D）。
- Assistant 通过 `RAG_MCP_Server__search_apis` 找到关键原语 **`pyAether.dbMovePinToNet(pin, net)`** —— pin 级改连的正确原语（不用删/重建 wire）。
- 相关候选 API：`seGuiReattachWireName`（reattach wire name to another wire）、`seGuiCreateWireName`、`dbCrtSchWireName`、`aeCreateWireName`、`leGuiDelLabelByInstance`。
- 后半程转入 Virtuoso 启动调试（`project.table` 缺 `iejoad_test` 条目、assistant 误擅自追加被用户叫停、`vir` 命令来源排查、daemon port 51766 在 hfeg0plg17 启动、跨机连接测试）——属于环境调试，非核心交付。

## 可造题方向（待合成）
- **L1/L2 case**：给定 `schematic.py` 源码（attachment，A 档自包含）+ 一个真实 schematic dump（A），要求候选脚本：
  - ① 实现 `rename_net(old, new)`：调用正确 pyAether 原语，语义=全局改名不改物理连接；
  - ② 实现 `move_pin_to_net(inst_pin, net)`：用 `dbMovePinToNet`（而非 delete_wire_by_net + 重建），语义=pin 级改连；
  - ③ 输出结构化 dump（net→pins 映射 / label 列表），供 check 解析比对。
- **隐藏 B**：另一 schematic dump，net/pin 拓扑与 A 不同（命名/规模/连接均不同），防 hardcode A。
- **check() 牙齿**：subprocess 跑候选脚本在 B 上，断言：rename 后旧 net 名消失、新 net 名出现且 pin 集合不变；move_pin 后目标 pin 归属新 net、同 net 其他 pin 不动、物理 wire shape 数不减少（区别于 delete+rebuild）；anti-hardcode 三假 FAIL。
- **难度**：L1（离线 Python 复刻 pyAether 调用序列 + dump 解析）或 L2（真跑 pyAether）。L1 更可控，B 档用真实 dump 文本即可。

## 本轮处置
- **DEBT: 1 deepread 未合成**。原因：trace 主体是 API 设计讨论 + Virtuoso 启动调试（后半程跑题），合成牙健 case 需要构造 schematic.py 源码附件 + A/B 两份 dump + 拓扑解析 check，本轮预算（40min，已用于 MCP 68th 复测 + 候选筛选，top 120 全 claimed 需下沉到 mc 50-350 才找到 fresh）不足以负责任地完成自验。
- 下轮直接基于本笔记合成，无需重复深读。
- 台账 status 维持 `claimed`，不 park（trace 可造题，只是本轮未合成完）。
