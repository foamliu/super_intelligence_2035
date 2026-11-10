# deepread: 1793762204059_2v098 (daiweilu@hfeg0pjn100, mc=110, schematic_netlist)

## trace source
- session: 1793762204059_2v098.messages.json (762KB / 157 msgs)
- user: daiweilu @ hfeg0pjn100
- scan: ssh_eda_search_20261109_224902/summary.tsv
- keywords: netlist:417;verilog:177;analog:87;transistor:42;cmos:36;schematic:5

## user intent (single thread, debug-driven)
DRAM LPDDR5 DDGOA fuse_1103 验证 Dummy-Edge-WL testmode (TM_DumEdgeWl.v)：
1. 解释 testmode 说明（near 端 4 根 dummy WL 中控制 WL<1>/<2>，default=vwln，force=vwlp）
2. 验证 pattern TM_DumEdgeWl.v 能否实现该功能
3. Far 端是否只改 MA
4. compwrite 写什么 / 9F9F vs exp 99FF
5. 应该看哪个信号验证
6. WL=X 调试（cm 拉 high 但 WL=X，net023=Z，MP10 竞争）

## 助手产出（debug/analysis, 无单一 deliverable 文件）
- 多个临时 grep 脚本（editor writes 20 个，均为 throwaway grep/parse helpers）
- netlist 驱动追踪：定位 `cm0_ts_DumEdgeWL_nearDrv` 模块、`I_cm0_ts_DumEdgeWL_nearDrv_95/96` 实例、MP10(PMOS 上拉 vwlp)、MN24(NMOS 下拉 vwln)、`LvlShftVcc2VwlpRstLYdecIP` 电平转换器
- 控制信号链：`cm0_ts_DumEdgeWL`(CM bit3) → `ForceDummy` → level shifter → `fnHv` → `fnPupN`/`fnPdn` → MP10/MN24 栅
- 关键正确点：
  - near 端 CM = `cmOut3` (bit3)，OP_DUMEDGEWL=6'b001000
  - far 端 CM = `cmOut0` (bit0)，OP 不同 → 不能只改 MA
  - `HForceDumWL_U/V` 从 `m1G_YS_Near_sub` inout 传到阵列，拆 `_T/_B`
  - near 驱动模块内 DumWL 只有 MP10 一个真驱动（net023=Z 正常，MN24 关断）
  - WL=X 原因：模拟节点在数字仿真悬空（非 testmode 逻辑错）

## B-grade synthesized 抽象
核心机制 = **verilog 网表中对目标 net 做驱动溯源**：
- 解析 verilog 实例连接，找所有 .D/.output 端接到目标 net 的 instance
- 分类驱动类型（PMOS 上拉 / NMOS 下拉 / gate driver / inout pass-through）
- 解析每个驱动的栅/控制信号，递归溯源控制信号到 CM bit / 电源
- 对给定 testmode 配置，判定每条驱动通路 active/inactive
- 输出结构化驱动报告

与既有 D schematic_netlist case 正交：
- #500 prefix highlight（字符串过滤）≠ 驱动溯源
- #499 svwf expand（层级展开）≠ 驱动溯源
- #498 boolean expr check（逻辑求值）≠ 驱动溯源
- #497 cross-probe CSV（hierarchy BFS）≠ 驱动溯源

真实 /proj/ddgoa + pyAether 沙箱 + 698 主机不可复刻 → B-grade 自包含：
把「verilog 网表 + 目标 net + testmode 配置 → 驱动溯源报告」抽成单文件 CLI。

## 选料决策
- fresh: 4 shard ledger 均无 (A/B/C/D = 0/0/0/0)
- D-domain: netlist:417 + verilog:177 + transistor:42 + analog:87 → schematic_netlist
- 干净度: Q&A/debug-heavy，无单一 produce file → B-grade synthesized (机制清晰可抽)
- 已 claim: trace_ledger_D 1793762204059_2v098 schematic_netlist
