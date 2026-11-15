# 深读笔记 · am99r · 串联堆叠 MOS 静态工作点分析 Q&A

**session**: `1793089704959_am99r` · **user**: e0029308 · **host**: hfeg0pkn002 · **mc**: 339
**trace 源**: `.75` ssh scp `/home/e0029308/.cline/data/sessions/1793089704959_am99r/1793089704959_am99r.messages.json` (721634 B, 98 msgs: 54 user / 44 assistant)
**审计来源**: `designflow/pool_reaudit_B.tsv` 旧判 `reject consulting (OP analysis + job-status diagnostic, non-produce)` → 新判 **可造**（11-15 用户令：analysis/explain/debug-Q&A 一律恢复可造）

## 真实用户意图（trace 原文）

**msg#0**（首条 user）：
> 现在在跑运放的静态工作点路径如下：`/proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/STD_PLDX_LVL_SIM/OP_DC_SIM` 其中有很多串联管子当成一个 L 较长的管子，那我静态工作该如何分析了，看这一串管子中的某一根可以吗

**msg#19**（user 追问）：
> 我看起来是接近 D 端的 Vds 会更大，难道不是分析靠近 D 端部分的管子工作状态吗

**msg#21**（user 再追问，并纠正助手）：
> 那我这种五管 OTA，的输入对管，我应该看那一侧呢，你最好再看下电路图再回答我，别再错了蓝色大肥鱼

助手 msg#18/20 给出正确分析（核心知识点，作判分 ground truth）：
- 串联堆叠 MOS（栅共接、漏源串接）≡ 一根 N×L 长沟道管；目的是拉长 L 抬输出阻抗/分摊压降。
- **只有靠近漏端（D 端）那根进入饱和（pinch-off），其余靠源端（S 端）管落在三极管区是正常预期，不是设计错**。助手首答把方向说反（说底管/源端饱和），被用户追问后在 msg#20 订正为 **D 端饱和**。
- 判整串是否饱和：看 D 端管 `region==sat` 且 `Vds_D ≥ Vov_D`；整串饱和条件 `Vds_total ≥ Vg−Vth` 落在 D 端管上。
- 电流：KCL → 串内每根 |id| 相等，读任意一根 id 即整串电流。
- D 端管 Vov 会小于 S 端管 Vov（其源被中间节点抬高），故需更大 Vds 维持同电流——这是 D 端 Vds 大的根源。
- 五管 OTA 输入对管：需看电路图定位哪侧是 D（助手 msg#22 调 skill inspect schematic）。

msg#61（trivial，不入题）：切换中文输入法。msg#63（次意图，暂不入题）：仿真跑完任务挂服务器（job-status diagnostic）。

## 合成决策

- **任务形态**：analysis/explain Q&A → 按重审令「脚本分析报告」形态操作化（reaudit 自定的拟造形态）。deliverable = `op_analyze.py`（读 dcOpInfo JSON → 产出 `op_analysis.json`），把用户「该看哪根、整串怎么判」的概念困惑固化成可复用分析工具。这既保真用户意图（分析知识），又满足 §4 hidden-B/有牙 check（脚本在隐藏 B 上重跑）。
- **A 输入**（可见）：5T OTA 堆叠 NMOS 输入对管，2 个 stack（NM_INPUT_P/NM_INPUT_N），D 端管 sat、S 端管 triode、电流一致 → properly_saturated。数值按真实物理（Vg=0.75, Vth=0.45, Vov=0.30, 中间节点 0.082, Vout=0.60）合成。
- **hidden B**（不进 SUT）：cascoded PMOS load，SS/-40C，D 端管 PM2 落在 triode（Vds_total 不足）→ not_saturated + anomaly，d_side_margin 负。与 A 在 verdict / d_side 管 / region / margin / circuit 全异 → cross-input 守卫。
- **核心判分知识**：D 端管 = 拓扑推断（drain 节点不是栈内任何管的 source），而非取 data[0]；S 端 triode 是预期非异常；D 端非 sat ⇒ not_saturated + 异常。
- **判分有牙**：11 条独立断言 a-k；naive_hardcode_a / always_properly_saturated / empty / print_only 四负例 + 三 §4.9 假提交（空壳/print-only/删拓扑推断核心）全 FAIL；ref 11/11 PASS。

## case
`EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001` (spice_sim L1, track=synthesized, A档 trace-faithful prompt) → `EDA-Eval-DesignFlow_B.jsonl` line 320.
