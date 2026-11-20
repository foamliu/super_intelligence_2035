# Deep-read: 1793692590888_zudnw (yuhzhu@hfeg0plg91, mc=53, analog_context)

## Session Info
- **sid**: 1793692590888_zudnw
- **user**: yuhzhu
- **host**: hfeg0plg91
- **match_count**: 53
- **domain**: analog_context (circuit placement/floorplan planning from CDL)
- **keywords**: aether:1757;pyaether:323;netlist:13;analog:10;drc:8;schematic:6;skipper:3
- **messages**: 96 msgs, ~50 user turns (many are tool results)
- **file size**: 765KB

## Real Task Summary
yuhzhu 在 hfeg0plg91 上做 DDR PHY DQ 数据通路宏 DPHalf 的版图摆放规划。用户提供了 CDL 网表文件（DPHalf, 11285 行），希望助手解析网表的连接关系，分析信号流向，识别功能簇和对称结构，指导合理的版图摆放。

### 关键用户轮次
- U#0-3: "我能给你电路的连接关系 你来指导我怎么摆放合理吗"（重复4次，可能 retry）
- U#6: 提供 CDL 文件（zl_test_1，路径 /home/yuhzhu/.cline/data/sessions/.../uploads/zl_test_1）
- U#23: "只关注LkEccStage*这部分电路 LkEccStage放在中心 画一张更细的摆放图"
- U#28: "要我再往下给其中某一个 Stage123D（或 Stage4D/Stage56D）内部的器件摆放"
- U#33: "整体可以生成一个plan的图片吗"
- U#50: "我要查看图片"

### 助手工作流
1. 读取 CDL 文件 → 识别 11285 行，顶层 ddgoa_cmos_digital/DPHalf/schematic
2. 写 Python 脚本解析层次结构 → 569 个标准单元子电路，132 个顶层实例
3. 分析功能簇：ECC 编码通路（LkEccStage123D×4 + Stage4D×2 + Stage56D）、输出驱动树干、ECC 纠错/译码、接收编码/错误计数、延迟/校准链、模拟/DFT 岛
4. 识别电源域：GF 单元（vcc!/vssz!）、PF 单元（vccz!/vss!）、环振/SCMOS 模拟岛（vdd1!/vdd2h!/vwlp!/vdleq!/vsszFtRODq!）
5. 分析信号流向 → 确定 floorplan 摆放方向
6. 聚焦 LkEccStage* 子集 → 分析树状汇聚结构（4×Stage123D → 2×Stage4D_L/H → 1×Stage56D）
7. 识别两套对称半区（奇/偶 *O/*Ev）→ mirror 对称摆放
8. 门级展开 Stage123D → XOR12_pc60（2-input XOR = 4 管 + 3 反相器）
9. 用 matplotlib 生成 PNG floorplan 规划图（修复颜色/字体问题后成功）

## B-grade Synthesized Case Design: CdlPlacePlanGen-001

### 核心机制（从 trace 提取）
CDL 网表 → 层次解析 → 信号流向分析 → 拓扑排序 → 对称对识别 → 结构化 placement plan JSON

### 设计选择
- **选取子任务**: CDL 解析 + 层次/连接关系分析 + 拓扑排序 placement plan 生成（放弃 PNG 绘图子任务，纯解释性难≥8断言）
- **A/B/C 三变体**:
  - A (SUT-visible): EccEnc_A, 8 data bits, 4 input stages + 2 merge + 1 output = 7 instances, 9 subckts
  - B (hidden): EccEnc_B, 12 data bits, 6 input stages + 3 merge + 1 output = 10 instances, 12 subckts
  - C (embedded in check.py): EccEnc_C, 6 data bits, 3 input stages + 1 merge + 1 output = 5 instances, 8 subckts
- A/B/C 不相交: data bits(8/12/6), instance counts(7/10/5), subckt counts(9/12/8), stage names(Stage8/Stage18/Stage3)

### SUT: cdl_placement_planner.py
- 纯 stdlib (json/re/sys/os)
- 解析 CDL .SUBCKT → 层次树 → 找顶层 → 端口方向分类 → 拓扑排序 → 对称对识别 → JSON 输出

### check.py: 13 条件 a-m 独立 oracle
- 独立 _oracle_parse + _oracle_plan（与 SUT 完全独立的解析器）
- a: zip+源码+无禁import+无B/C字面量泄漏
- b: py_compile
- c: 跑B退0+产JSON
- d: design名匹配oracle
- e: num_subckts匹配
- f: top_ports三类匹配
- g: 实例名集+计数匹配
- h: 每实例level匹配oracle拓扑序
- i: signal_flow=left_to_right
- j: symmetric_pairs规范化匹配
- k: placement_order匹配
- l: power_domains匹配
- m: 反硬编码C变体全匹配+C≠B

### 维度正交性
vs BufPFFlatGen (SPICE flattening + TCL flow) / CdlXistorAudit (CDL/GDS filename audit + transistor count) / NetlistCellReplace (netlist cell replacement) / GioLioAbTilingGen (GIO/LIO tiling placement) — 机制全不同：CDL hierarchy parsing + topological sort + symmetry detection → structured placement plan JSON，非重复。

## Self-verify
- ref SUT PASS 13/13 ✓
- 4 neg (empty/print_only/hardcode_a/core_deleted) 全 FAIL ✓
- 3-seed sha256 consistent ✓
- jsonl round-trip PASS ✓
- k_rationale = k_check = 13 ✓
