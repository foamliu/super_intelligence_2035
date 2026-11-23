# r1124 (shard B) 0-case 选料无果轮 · 2026-11-24

## 背景
r1123 收口 6mbnf 后，MEMORY 下一步提示「1124 scan 023802 fresh B-spice 高 mc 段已紧(仅 6mbnf 真 fresh)，下轮探低 mc(<200) hspice-dominant 段 或 spectre/siliconsmart 子域 或等新 scan」。

本轮从 `b_fresh_1123_Bonly_538.tsv`（1123 scan 的 B 域 fresh 池，538 行）筛选 B-spice dominant（spice_sum≥10 且 spice 占比≥15%）得 20 候选，扣除 cross-shard 已 claimed/cased/parked 后真 fresh（全 4 shard ledger 无记录）剩 7 条，本轮 peek 6 条（hglhw / 7xh6n / dny8u / i7p2y / 7c6ni / k5jur）+ 复核 1 条（b99hz r1114 已拒）。

## Peek 逐条（全 reject）

| sid | user@host | mc | spice kw | peek 结论 | 判 |
|---|---|---|---|---|---|
| 1795074707573_7xh6n | e0018590@hfeg0plg92 | 31 | spectre:35 | U#0="linux 执行文本文件 permission denied"→chmod/shebang/bash 续行 Q&A；U#2="命令行分行写"Q&A。**实际意图=通用 Linux Q&A**，spice kw 来自 assistant 举例，非用户意图。498KB 但全是 Linux/bash 问答。 | REJECT (Q&A 无 produce) |
| 1793006064236_hglhw | hanchen@hfeg0plg56 | 7 | spice:10 | U#0="how to use parameter m in a netlist? apply m to customized cell other than MOS"=SPICE 语法 Q&A；assistant 调 ask_question 选 simulator。11.7KB 短会话。 | REJECT (doc-search Q&A) |
| 1794893721615_dny8u | yixiaow@hfeg0plg107 | 4 | spice:24 | 5msgs；U#0 注入 `<command-name>demeter-agent</command-name>` 整份 Demeter Expert Agent+Skills 定义（基于 User Guide 56页）；U#1="[demeter-agent] IBIS flow 如何搭建"=对注入 agent 的 doc-search Q&A。57.5KB 但大头是 skill 定义文本。 | REJECT (skill-inject + doc Q&A) |
| 1794191817353_i7p2y | e0041392@hfeg0plg77 | 4 | spice:15 | U#0=`<skill_instructions name="ask-eda">` 调 Dify RAG AskEDA 知识库；同 user e0041392 即 r1114 已拒的 b99hz（"askeda 查 NanoSpice 精度" doc-search）。24.7KB。 | REJECT (doc-search Q&A，dup user pattern) |
| 1795006285185_7c6ni | alan17z@hfhds201 | 3 | spice:12 | U#0="Context summary" continuation，合并 3 个 IBIS skill (ibis-t2b-gen/ibis-zq-calib/ibis-zq-sim-gen)→ibis-extract 端到端 skill；同 user 同 off-domain skill-mgmt pattern as gug8y(r958 parked)。 | REJECT (skill-mgmt env-config) |
| 1795006180806_k5jur | alan17z@hfhds201 | 3 | spice:12 | 7c6ni 的兄弟会话（同 ts 同 Context summary 同 IBIS skill 合并任务）。 | REJECT (skill-mgmt, sibling dup) |
| 1791770402098_b99hz | e0041392@hfeg0plg77 | 4 | spice:28 | r1114 已 peek 拒："askeda 查 NanoSpice 精度"=doc-search Q&A 无 check 齿。 | 已 parked（不复检） |

## 池状态结论
- **1123 scan B-only fresh 池（538 行）经本轮 6 peek 后，spice-dominant 真 fresh 段已实质耗尽**：剩余 fresh 多为低 mc(<5) 或非 spice-dominant（drc/pex/virtuoso 主导，属 C/D 域）。
- **失败模式高度集中**：6 peek 全部命中「Q&A / doc-search / skill-mgmt / continuation-context」四类无 produce 齿意图——与 r1114（10 peek 全 reject）、r1087/r1088（7 peek 全 reject）同型。高 mc fresh B-spice 池在多轮消耗后，残存 fresh 的 produce 密度已趋近 0。
- r1123 的 6mbnf 是该段最后一条真 produce trace（mc274 hspice:667 88% dominant），与本轮 6 条残存 fresh（最高 mc31 且 spice 占比仅 18%）形成断崖——印证「池已紧」判断。

## 止损决策
- 本轮 **0-case 产出**，6 条 peek 全 parked 入台账（防复检）。
- 连续有效 peek 本域 fresh ≥12 条（r1123 1 产 + 本轮 6 + r1114 10 中的本域部分）无 produce，触达 §6 止损线。
- **下一步**：等新 scan（1124 scan 023802 已落，但顶层 fresh B-spice 仅 6mbnf 入选 r1123；下一 scan 前）；或转 §4.9 自查 / ledger 治理；或探 spectre/siliconsmart 子域需更宽 keyword（当前 dominant 过滤后几乎无 fresh）。

## 指标
- 📊 trace 覆盖率：covered=588 / target=4529 = 13.0%（mc≥10，不变；本轮 0 case）
- 🎯 通过率：最近20条 20/20=100%（观察值，不变；总样本<30 前不报总通过率）
- 🧾 本轮 0 k（无新 case）
- 📦 MEMORY_B <32KB ✓
- DEBT: 0
