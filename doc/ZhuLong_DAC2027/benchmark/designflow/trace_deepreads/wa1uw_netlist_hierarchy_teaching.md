# trace_deepread — wa1uw (netlist-grounded DRAM column-select hierarchy teaching)

- **session**: `1789526951493_wa1uw` (rongtaoy @ hfeg0pkn001 / hfeg0pkn002 / hfeg0plg74 / hfeg0plg103 / hfeg0plg99 — shared home, multi-host login)
- **host ip**: 10.129.2.10 (also 10.129.8.112/235/231); user rongtaoy
- **mc**: 237 (netlist:533; schematic:51; hspice:36; synopsys:34; cmos:26; aether:6; mosfet:5; transistor:3)
- **agent**: `lead` (not cline) — 157 msgs, 1.93 MB messages.json
- **trace 源可达性**: **B-grade** — `/rundata/ddgoa/.../netlist_1184_5csl` permission-denied from .75 (e0031982 身份); trace 内 lead agent 以 rongtaoy 身份可读 reneez 目录，.75 不可读。netlist 按 trace 结构 B-grade 重建。

## verbatim 用户原话（substantive turns）

- **U#0**: `can you find the path:/proj/ddgoa/V0/workdir/rongtaoy/simulation/sim_4_SM/,and see every .sp file inside the floders, i want you tell me the target of the all simulation,please speak chinese`
- **U#20**: interaction-protocol 7 段结构定义 + 要求学习 sim_4_SM（目的/配置/过程/结果/sp/波形），抓取 preeqoff 侧代表 .sp 全文 + 4 感测类型 .sp 前 40~60 行 + replace_sp/runall 脚本 + Bisection 迭代 + 完整裕度 CSV
- **U#45**: `1.联系网表文件，dram架构等等，向我详细阐述什么是6-5ys，用具体的电路举例说明，其次有没有m-nys，m-nxs之类的  2.这个仿真具体目的，过程，结论是什么，结合.sp文件和result教会我`
- **U#62**（**本 case 选定子意图**）: 「你上次关于"6-5 YS"的讲解里，有几个层级数字互相打架，我作为学员学不动，需要你重做一份"自下而上、每一步都自洽、能教会人"的版本」+ **层级守恒表**：

  | 层级 | 实例数 | 每实例含几个下级 | 位线对数 | Csl 数 |
  |------|--------|----------------|--------|--------|
  | Memory Cell | ? | ? | ? | - |
  | CXSA1x4_die2_fbcc | ? | 4 | 4 | ? |
  | msax256_fbcc | ? | ? | ? | ? |
  | msax512_fbcc | ? | ? | ? | ? |
  | msaq_U_CCR_fBcc_int_spf (顶层) | 1 | ? | ? | 1120? 还是其它 ? |

  要求：从 1184 列出发把每层列数守恒追到顶层；明确顶层到底几根 Csl（1120/296/别个）；解释 1120 与 1184 差额来源；纠正"5 对 IO 数据线"若不符。
- **U#78**: 「数字归属」—— 把 "5"（及 "6-5"）钉死在真实信号/总线/模块上；Cslin<1119:0> 是什么；以 blasec28<556> 追一条端到端通路
- **U#99**: 针对 `array10Meg_EU_fbcc_spf_5csl` 模块做 5csl 溯源（.SUBCKT 定义 + 包含关系 + 恰好 5 的实物 + EU/10Meg 含义 + 与 blasec28<556> 关系）
- **U#122/U#135**: 提供文件路径 / `.SUBCKT array10Meg_EU_fbcc_spf_5csl` 在 L29349
- **U#151**: FineSim 二分法迭代完整记录教学（mixb.log 逐行 iter/Vtarget/MaxVout/success/fail）

## 助手关键产物（trace 内 agent 真实读到/算出的）

- 网表两份：`netlist_1184_5csl`（reneez 目录，9040 行，原始）+ `netlist_1376`（rongtaoy 目录，44204 行，SPF 提取版）
- 层级结构（A#150 最终自洽版）：
  ```
  array10Meg_EU_fbcc_spf_5csl  (L29349, 4488 列, ≈10Mb, BLa<4487:0>)
    └── array0P8Meg_R_fbcc_spf   (L29549, ≈0.8Mb)
         └── msaq_U_CCR_fBcc_int_spf  (L8993, Cslin<1119:0>=1120, 本仿真 1184 列子块)
              └── msax640_fbcc   (L854, 640 列, Csl<159:0>)
              └── msax512_fbcc   (L383, 512 列, Csl<127:0>)
              └── msax256_fbcc   (L166, 256 列, Csl<63:0>)
                   └── CXSA1x4_die2_fbcc  (L77, 4 列/CXSA, 1 Csl, 4 Io)
  ```
- 守恒：1184 列 ÷ 4 = 296 CXSA；msax256 含 64 CXSA（共享 Io0<3:0>）；msax512 含 128 CXSA
- 关键诊断：Cslin<1119:0> = 1120 是**译码前地址**，非直接 Csl；本仿真 1184 列是完整 4488 列阵列的约 1/4 子块；"5csl" = 版本标记（sim_7sec_fbcc_spf_5csl L1），网表内无宽度恰为 5 的总线；"6-5" 的 5 = 6 组 CSL 中 5 有效数据通道（4+2=6 组 CSL，5 有效输出）

## 意图判定与 case 设计

- **用户真实意图**：multi-turn teaching session，学员（rongtaoy）跟 zhulong 学 DRAM 6-5 YS 列选择架构。最可判分子意图 = **U#62 层级守恒表**（用户明确要"实例数/每实例含几个下级/位线对数/Csl 数"表，可结构化断言；其余 teaching 子意图如"6-5 释义/感测时序/FineSim 二分法"散文式难结构化判分）。
- **domain**: schematic_netlist（SPICE 网表层级，netlist-grounded）
- **reframe**：用户意图=netlist-grounded hierarchy-explain Q&A，design_flow 契约需在隐藏 B 上跑候选→reframing 成 netlist-grounded hierarchy-extraction tool（读 SPICE 网表 + 问题 → 结构化层级守恒表 JSON: layers[{name, instance_count, children_per_inst, bitline_pairs, csl_count, cited_subckt}] + netlist_summary + cited_identifiers + architecture_summary）。套 bgrlw r710 / otonl r739 netlist-grounded explain pattern。
- **B-grade gold**：源不可达（/rundata permission-denied），按 trace 结构重建 netlist_A.sp（自洽 1184 列 / 296 Cslin，模块名沿用真实 msaq_U/msax512/msax256/msax160/CXSA1x4）。
- **data-driven 3×B**：B1（640 列 4 级 SecAr_B1/TileA_B1/Mux4_B1/Cell_B1）/ B2（128 列 Bank_B2/Quad_B2/Sense1_B2/Bit_B2）/ B3（trivial InvLeaf_B3 优雅降级）。模块名/规模/结构与 A 全异，反硬编码有牙。

## 近重判（dedup）

- wa1uw 在 pool_reaudit r704 标 prototype-proven（netlist-grounded explain 套 #29/#33 v2），无已交付近重 case（bgrlw r710 = Verilog netlist module-explain，本例 = SPICE netlist hierarchy-extract，source-type 不同；otonl r739 = netlist circuit-find+mechanism，不同子型）。可造。
