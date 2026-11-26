# trace_deepread: 1787564069550_sstk3 — Decoder38 Structural Netlist Generator

- **session**: 1787564069550_sstk3.messages.json
- **user**: junxu @ hfeg0pkn005 (10.129.2.x)
- **mc**: 1605 · **domain**: layout_virtuoso
- **keywords**: virtuoso:2202; schematic:1969; cellview:975; dbGet:12; dbCreateRect:9; netlist:6

## 用户原始意图
1. (msg 0) `/virtuoso-cli 做一个三八译码器` — 使用 virtuoso-cli skill 和 stdcells_am 标准单元库实现一个 3-to-8 译码器电路。
2. 后续 msg 中用户反复指导 agent 调整器件摆放、net 命名、bus 合并等版图细节。

## Agent 实际行为
- 使用 virtuoso-cli skill 调用 SKILL API (dbOpenCellViewByType, dbCreateInst, dbCreateRect, dbCreatePath 等) 在 Virtuoso 中创建 schematic 和 layout。
- 3-to-8 译码器用 3 个反相器 (INV) 生成输入补码 + 8 个 3 输入与非门 (NAND3) 实现一个 active-low one-hot 译码。
- session 极长 (948 msgs, 493 user msgs)，主要时间花在版图摆放调整和 SKILL 语句修正上。

## Case 抽象 (reframe B 档 produce-tool)
- 真实意图：用标准单元库搭建 3-to-8 译码器电路。
- reframe：写 Python CLI 工具 `decoder38_gen.py`，读标准单元库 JSON 描述（含 cell 名/引脚/function），自动识别反相器和 3 输入与非门，生成结构化 Verilog 网表（3 INV + 8 NAND3，active-low one-hot）。
- **A (visible)**: stdcell_lib_A.json — stdcells_am 工艺库, cell INV (A/Y) + NAND3 (A/B/C/Y)
- **B (hidden)**: stdcell_lib_B.json — SC7P 工艺库, cell INVX2 (I/ZN) + NAND3X2 (A1/A2/A3/ZN)，不同 cell 名和引脚名
- 判分：运行 candidate on B → 验证输出 .v 的结构（module/3 input/8 output/3 inv/8 nand/dec7=a,b,c/dec0=a_b,b_b,c_b/用 B cell 名/确定性/无 A 硬编码）
- 纯 Python 无 EDA 工具 → judge_layers=[L0,L1]

## 断言清单 (16 条: a-p)
① 候选文件存在于 zip ② Python 编译通过 ③ 使用 argparse CLI ④ hidden B 可读 ⑤ 候选在 B 上运行 exit 0 ⑥ 输出 .v 文件产生 ⑦ module 声明 ⑧ 3 输入端口 ⑨ 8 输出端口 ⑩ 内部补码线 ⑪ 3 反相器实例 ⑫ 8 译码实例 ⑬ dec7 用 a,b,c ⑭ dec0 用 a_b,b_b,c_b ⑮ 用 B 库 cell 名非 A 硬编码 ⑯ 3 跑确定性 md5 一致
