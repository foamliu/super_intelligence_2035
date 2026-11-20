# 深读笔记 · session 1790127814437_ngrdz · ziyuny @ 10.129.32.190

- mc=12, keywords: lvs:106; drc:86; analog:31; aether:13; calibre:6; transistor:5; pyaether:4; netlist:3
- messages.json: 14 条（6 user / 8 assistant），62KB
- 档案时间：2026-09-23，会话 14:09 起

## 用户意图（逐轮）

整段会话是**模拟电路匹配对管概念 Q&A**，4 个 user 实质轮全部是「提问/求知」类（无工具调用、无附件、无产物文件）：

1. **U#0**：「模拟电路中 DP CP CM分别是指什么电路」——问三种缩写的含义。
2. **U#8**：「CP —— Cross-coupled Pair（交叉耦合对）的管子左右两边必须一样吗」——追问 CP 匹配要求。
3. **U#10**：「DP的管子，左右两边必须一样吗」——追问 DP 匹配要求。
4. **U#12**：「你知道这类电路画版图的时候，按照AB管去画有什么画法吗」——问 AB 匹配对管的版图画法（叉指/共质心图案）。

## 助手回答要点

- **msg 7**（DP/CP/CM 定义）：DP=Differential Pair 差分对，CP=Cross-coupled Pair 交叉耦合对（PLL 语境下也可指 Charge Pump），CM=Current Mirror 电流镜。三者是模拟版图匹配约束自动识别的最基本三类「匹配对管」。
- **msg 9**（CP 匹配）：原则上左右管必须电学对称（同尺寸、对称版图、共质心+叉指+dummy），否则产生失调/误锁存；少数场景（SRAM 比例逻辑、偏斜锁存）刻意不对称。
- **msg 11**（DP 匹配）：比 CP 更严格，DP 失配同时损害失调/CMRR/PSRR/线性度四大指标；版图手段：共质心、叉指拆分、同方向摆放、dummy 保护、对称走线。
- **msg 13**（AB 画法，最丰富）：按匹配强度从弱到强——
  - 简单并排/镜像 `A B`：质心不重合，不推荐。
  - 一维叉指 `ABAB`（A1 B1 A2 B2）：局部失配平均化，但**质心不重合**，一阶梯度未消除。
  - 一维共质心 `ABBA`（A1 B1 B2 A2）：**质心重合**，一阶线性梯度抵消。
  - 二维共质心 2×2 `A B / B A`：x、y 双向一阶梯度抵消，最高精度。
  - 推广 4×4 阵列；原则：质心重合、分布离散、图案紧凑、双向对称。
  - 配表对比各画法的质心重合/抵消梯度能力/适用场景。

## 任务形态判定

- 真实用户意图 = **理解模拟匹配对管的版图画法与匹配要求**（explain / Q&A 类）。
- 2026-11-15 用户令 §二：explain / Q&A 类全部恢复为可造 → **合法用户意图**。
- 无真实附件、无工具产物 → A 档 gold（free-text markdown 答案）无 ≥8 硬断言牙（print-only stub 打印同形 markdown 即 PASS，违反 §4.9）。
- **档 B reframe**：抽离助手在 msg 13 中真实编码的「AB 匹配对管布局画法 + 质心重合 + 对称性 + 梯度抵消阶数」知识成**参数化布局生成器** `analog_match_layout_gen.py`（CLI `<spec.json> <out.json>`，支持 ABAB/ABBA/AABB/2D_cross 四类 pattern，计算 A/B 质心、判定质心重合/对称性/梯度抵消阶数，确定性输出）。判分用隐藏 B（CM，P1/P2，4+4 fingers，2D_cross）——与可见 A（DP，M1/M2，2+2，ABBA，1D）在 pair/管名/finger 数/dimension/pattern 全不同，反硬编码。

## 域归属

- 主题是模拟版图匹配对管布局 → **layout_aether**（模拟版图域）。ledger claim 时粗标 physical_verify（keywords lvs/drc 主导），但会话实质是模拟版图概念；case metadata.domain 用 layout_aether 以反映真实主题，并在 MEMORY 说明。
- 溯源：user=ziyuny, host=10.129.32.190, session_file=1790127814437_ngrdz, match_count=12。
