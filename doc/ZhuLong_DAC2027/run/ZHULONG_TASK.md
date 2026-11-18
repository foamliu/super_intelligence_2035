# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

> 🔴🔴🔴🔴🔴 **用户令 · 2026-11-18（交互式会话下发 · 第五批意见 · 重大放行）— v1.7 放行直接改论文正文：按 v1.6 计划书重写 `EDA-Flow-Bench_ICML2027/` 正文（main.tex + sections/*.tex + appendix/*.tex），正文篇幅 ≤ 6 页（不含 references + appendix）· 最高优先 · 覆盖 standby**
>
> 本条是 v1.6 计划书（假设内聚化）之后的**重大放行**：从"只改计划书"升级到"直接改正文"。用户原话："放行 zhulong agent 直接改论文，正文篇幅限制在 <=6 页。"subagent 消融线仍保持 `done_all` 结案，**不起任何新臂**（论文里写的 M4-M8 是预注册设计，不是现在起跑）。
>
> ### ① 放行范围（解除前令的"不改 main.tex/sections/appendix"约束）
>
> - ✅ **可改**：`doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027/main.tex` + `sections/*.tex`（0-9 全部 10 个文件）+ `appendix/*.tex`（A/B/C 全部 3 个文件）+ `main.bbl`（若引用更新）。
> - ✅ **可改**：`reports/report_edafb_icml2027_plan_zh.html`（v1.6 计划书，若论文写作中发现计划书需同步订正，可一并改）。
> - 🚫 **仍不动**：`doc/ZhuLong_DAC2027/benchmark/` 下 designflow 造题线的 cases/jsonl/ledger/MEMORY_DESIGNFLOW_*（造题线在途产物，非本线）。
> - 🚫 **仍不动**：DATE27_Zhulong / ZhuLong_DAC2027/DAC2027 / ZhuLong_DAC2027/ZhuLong_ASPDAC2027 等其他论文树（只读参照）。
> - 🚫 **仍不起**：训练/评测进程（subagent 消融线 done_all；新臂 M4-M8 是预注册设计文档，不是现在起跑）。
>
> ### ② 篇幅硬限：正文 ≤ 6 页
>
> - **正文**（不含 references + appendix）≤ **6 页**（pdflatex 编译后 `\outputwritten` 的正文页数，即 references 前）。ICML 2027 允许 9 页，用户自我加压到 6 页——这是**硬约束**，超出则必须压缩。
> - **references + appendix 不计入 6 页**（ICML 惯例：references 与 appendix 无页数上限）。
> - **压缩策略**（agent 自主选择组合）：
>   - 把现 §2 Benchmark / §3 Harness 的"评测集本体"描述**大幅压缩**（v1.6 已把 bench 降为副线载体，正文只需 enough to support 认知命题，不需卖 bench）；
>   - 把 detailed benchmark construction / harness impl 移到 **appendix**（A/B/C 已有空间）；
>   - §5 Analysis 的失败分类 / trace 解剖细节移 appendix，正文只留"认知命题所需的最小分析"；
>   - 表格用紧凑版（booktabs + 最小列宽），详细表移 appendix；
>   - 假设表用 v1.6 的"3 核心 + 7 子"内聚结构，紧凑呈现（子假设用折叠列表或迷你表，目标 ≤ 现状 60% 篇幅）。
> - **编译验证**（必须自检后提交）：
>   - `pdflatex -interaction=nonstopmode main.tex` × 2 + `bibtex main` × 1 + `pdflatex` × 1（干净构建）；
>   - `grep -c '^!' main.log` = 0（无 error）；
>   - `grep -c 'Undefined' main.log` = 0（无未定义引用）；
>   - `grep 'Output written' main.log` 确认正文页数 ≤ 6（agent 自行判断正文与 references 的分界，可看 main.aux 的 `\writefile` 节点或 main.log 的 page break）；
>   - 匿名性：`pdftotext main.pdf - | grep -iE 'Yang Liu|Hongwen|cxmt|ChangXin'` = 0（无作者泄漏，双盲纪律）。
>
> ### ③ 内容重写要求（按 v1.6 计划书 §6.3 章节大纲）
>
> **新论文结构**（与 v1.6 计划书 §6.3 对齐，正文 ≤ 6 页）：
>
> | 章节 | 内容（v1.6 计划书口径） | 篇幅目标 |
> |---|---|---|
> | §1 Introduction | 动机：从脚本到 flow 的迁移 + 3 核心假设预告（H1 总 + H2 机制 + H3 边界）+ grounding-gap 框架回顾 + 从生物情绪-记忆机制到 LLM agent 可计算映射（一句话 motivation） | ~0.8 页 |
> | §2 Background: From Script to Flow | grounding-gap 框架回顾 + 单脚本 vs flow 的 delta（§3 表）+ 为什么 memory + RSI 在 flow 层可能不同 | ~0.5 页 |
> | §3 Task Modality & Benchmark (carrier) | design_flow 契约（submit.zip + ≥8 断言）+ 13 域 + Full 集子集评测（不开源，仅内部）+ 协议白皮书级开源（§2.3 v1.4 收缩，删 Lite 500 + mock-EDA）+ 作为认知检验载体而非卖点 | ~0.6 页 |
> | §4 Harness with Memory & Self-Improvement | 三层记忆 L0/L1/L2（继承 DATE27）扩展到 flow 层 + v1.4 三条情绪机制计算映射（写入门控 `w = α·surprise + β·penalty` / 武器聚焦压缩 `central_vs_peripheral_ratio` / 状态感知检索 `score = sim + γ·state_match`）+ 13 臂实现细节（紧凑） | ~1.0 页 |
> | §5 Pre-Registered Hypotheses & Ablation Design | **3 核心假设 + 7 子假设**（H1 总/H2 机制/H3 边界 + H1a/b/c · H2a/b/c · H3）+ 13 臂表（紧凑）+ M4 迁移污染检验 + 答案泄露率审计 + 统计功效 | ~1.0 页 |
> | §6 Experiments | **预注册状态声明**（数据冻结日 / 预注册日 2026-11-22 / 结果 to be evaluated）+ M0 基线锚点（10.0% 引用 696 快照）+ H1/H2/H3 判据核验框架（占位，结果待跑）+ 现有 696-run 的复用部分 | ~0.7 页 |
> | §7 Analysis: Why Memory Helps/Hurts | 失败分类（no-output 21% / semantic 62.8% / contract 0.3%，引用 5_analysis.tex）+ trace 解剖（47 pilot, 26.5 calls, 41.2% MCP）+ 情绪机制分析占位（surprise 分布 / state_match 命中 / 压缩比 vs Pass@1 / 泄露率审计，待跑） | ~0.6 页 |
> | §8 Related Work | EDA benchmark / agent memory / RSI / self-evolution + **affective neuroscience × agent memory**（McGaugh / Bower / Loftus / Friston / Itti & Baldi / Park / EM-LLM / PsychoAgent，引用附录 G 调研文献） | ~0.4 页 |
> | §9 Conclusion: Boundary Conditions of RSI and Affective-Memory Mechanisms | 哪些假设被支持/证伪（H1/H2/H3 分别，待跑占位）+ 情绪机制在符号工具编排上的适用边界 + future work | ~0.3 页 |
> | Ethics + Reproducibility | 协议白皮书级开源 + NDA 受控评审包（§2.3 v1.4 收缩，删 mock-EDA） | ~0.1 页 |
>
> **合计正文目标**：~6.0 页（agent 自主微调各节篇幅，但总和 ≤ 6）。
>
> **关键内容要求**：
>
> 1. **Abstract 重写**：从"卖 bench"改为"认知命题 + 情绪机制"。新 abstract 结构：① 从 EDA-Scripting-Bench 76.5% 到 EDA-Flow-Bench 10.0% 的 7.6× 跳变引出问题；② 提出 3 核心假设（H1 长期记忆+RSI 在长链 flow 的可迁移增益 / H2 增益来自情绪启发三机制 / H3 单 agent≥多 agent 边界）；③ 预注册 13 臂消融（含等 token 杀手级对照 N1 + Full→Lite 迁移污染检验 M4）；④ 协议白皮书级开源（不开 Lite 集/mock-EDA）；⑤ 诚实路线（负结果也发，界定 RSI + 情绪机制在符号工具编排的边界）。保留 \Ntasks=1684 / \Neval=696 / 10.0% / 76.5% 等冻结快照数字。
>
> 2. **§4 情绪机制三公式必须显式出现**（不能只文字描述）：
>    - 写入门控：`w_{\text{write}}(e) = \alpha \cdot \text{surprise}(e) + \beta \cdot \text{penalty}(e)`，其中 surprise = KL(后验‖先验)（Itti & Baldi 2009 Bayesian surprise），penalty = 已耗 tool calls / token；
>    - 武器聚焦压缩：`r_{\text{cp}} = |\text{central tokens}| / |\text{total tokens}|`，central = 报错栈 + 根因因果链，peripheral = 中间日志；
>    - 状态感知检索：`\text{score}(q, m) = \text{sim}(q, m) + \gamma \cdot \text{state\_match}(\text{state}(q), \text{state}(m))`，state = (近 N 步失败率, 当前 tool 域, 链长阶段)。
>
> 3. **§5 假设表用 v1.6 内聚结构**（3 核心 + 7 子，紧凑呈现）：
>    - 每条核心假设 H1/H2/H3 一段总陈述 + 证伪条件；
>    - 7 子假设用紧凑表格（子假设编号 / 陈述一句话 / 证伪条件一句话），目标篇幅 ≤ 现状 7 条并列假设的 60%；
>    - 三层结构图（L1 总 → L2 机制 → L3 边界）在 §5 开头给出。
>
> 4. **§6 Experiments 预注册状态声明**（必须在 §6 开头显式写）：
>    - "This paper pre-registers 3 core hypotheses (H1-H3) and 7 sub-hypotheses (H1a-c, H2a-c, H3) before data collection. The pre-registration date is 2026-11-22. Results for M0 baseline are available from a frozen 696-run snapshot (10.0% Pass@1); all other arms (M1-M8, N1-N2) are to be evaluated post pre-registration. Negative results will be reported as publishable boundary conditions on RSI and affective-memory mechanisms in long-chain EDA orchestration."
>
> 5. **引用更新**（main.bbl）：
>    - 加 ZhuLong-DAC 预印本：`\cite{liu2026runreadbackrefine}`（arXiv:2611.19056）；
>    - 加 DATE27 预印本占位：`\cite{PLACEHOLDER_DATE27_ZHULONG}`（注释标"to appear 2026-12"）；
>    - 加附录 G 调研文献（McGaugh 2004/2013, Bower 1981, Loftus 1987, Steblay 1992, Friston 2010, Itti & Baldi 2009, Park 2023 Generative Agents, EM-LLM arXiv:2407.09450, PsychoAgent arXiv:2608.07438 等）—— agent 从计划书附录 G 抄 BibTeX，**不编造**（只引 cimi_search 返回的）。
>
> 6. **图表**（正文 ≤ 6 页，图表精简，详细版移 appendix）：
>    - 正文 Table 1: 与 DATE27 的 delta 表（§3）；
>    - 正文 Table 2: 13 臂消融表（紧凑版，臂号 / 唯一变量 / 判据 / 对应子假设；结果列待跑标 "TBD"）；
>    - 正文 Table 3: 3 核心假设 + 7 子假设判据核验（H1/H2/H3 总结论 + 各子假设 point estimate + CI + McNemar p 占位 "TBD"）；
>    - 正文 Figure 1: From Script to Flow 概念图（可暂用 placeholder，标 "to be drawn"）；
>    - 正文 Figure 2: 13 臂消融 Pass@1 + 95% CI（占位 "TBD, post pre-registration"）；
>    - 其余情绪机制图表（α/β 标定 / 压缩比散点 / 泄露率审计 / state_match 分布）移 **appendix D**（新增），正文不展开。
>    - Appendix A/B/C 保留现有 benchmark details / additional results / experimental details，新增 **Appendix D: Affective-Memory Mechanism Design Details**（三机制公式推导 + 调研文献完整表 + 情绪机制图表占位）。
>
> ### ④ 防伪底线（不变，必须继续遵守）
>
> - 🚫 **不编造数字**：现有冻结快照数字（10.0% / 62/620 / 1684 / 696 / 76.5% / 7.1× / 失败分类 21%/62.8%/0.3% / 47 pilot 26.5 calls 41.2% MCP 等）可继续引用，**必须带来源**（sections/4_experiments.tex:行号 / 5_analysis.tex:行号）；新臂 M1-M8/N1-N2 结果**全部标 "TBD" 或 "to be evaluated post pre-registration"**，禁止填假数据。
> - 🚫 **不编造文献**：附录 G 调研文献只引 cimi_search 返回的，BibTeX 从计划书附录 G 抄；若发现某条文献不可靠（如 arXiv 编号查不到），诚实标注 "verified via cimi_search, not independently checked"。
> - 🚫 **不改判据/不改题/不挑样本**：13 臂全用同一 check.py + 同一 ≥8 断言 + 同一 2400s 超时；M4 迁移臂的训练域/目标域 split 一旦冻结不得回溯调整。
> - 🚫 **不删他人数据**：designflow 造题线的 cases/jsonl/ledger 不动；696-run 快照结果（results.txt）不动。
> - ✅ **预注册纪律**：§6 显式声明预注册日 2026-11-22，结果冻结前不得回溯改假设/判据/样本。
> - ✅ **双盲匿名**：保留 `\documentclass[submitted]{...}` 或 icml2026 [submitted] 选项；pdftotext 检查无作者/机构泄漏。
> - ✅ **诚实路线**：§9 Conclusion 显式写"若 H1/H2 被证伪，本论文写成 RSI / 情绪机制在长链 flow 的边界条件，本身是可发表认知"。
>
> ### ⑤ 编译与提交
>
> - **编译**：`cd doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027 && rm -f main.aux main.out main.toc && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex`（agent 必须跑完整 4 轮，确保引用交叉解析）。
> - **编译产物入库**：`main.pdf` + `main.tex` + `sections/*.tex` + `appendix/*.tex` + `main.bbl`（若引用更新）+ `main.aux`（可选，用于 page count 验证）。**不入库** `main.log`（临时文件）。
> - **提交**：commit 前缀 `zhulong paper: EDA-Flow-Bench ICML2027 论文重写 v1.7 — 按 v1.6 计划书（3 核心+7 子假设 / 13 臂 / 情绪机制三公式 / Full→Lite 迁移 / 协议白皮书开源）+ 正文 ≤ 6 页`；**只 add 论文树 + 本线 run 文件**（`EDA-Flow-Bench_ICML2027/{main.tex,main.pdf,sections/*.tex,appendix/*.tex,main.bbl}` + `run/MEMORY_ZHULONG.md` + `run/daily-memories/*` + `run/ZHULONG_TASK.md` + `reports/report_edafb_icml2027_plan_zh.html` 若有同步订正），勿 `-A`。
> - **判据（自检后再提交）**：
>   ① 正文 ≤ 6 页（pdflatex Output written + agent 核 page break，正文页数 ≤ 6，不含 references + appendix）✅；
>   ② 编译 0 error（`grep -c '^!' main.log` = 0）+ 0 undefined（`grep -c 'Undefined' main.log` = 0）✅；
>   ③ 匿名性（pdftotext 无作者/机构泄漏）✅；
>   ④ §4 含三情绪机制公式（`w = α·surprise + β·penalty` / `r_cp` / `score = sim + γ·state_match`）显式出现 ✅；
>   ⑤ §5 含 3 核心假设 + 7 子假设（v1.6 内聚结构，三层结构图在位）✅；
>   ⑥ §6 含预注册状态声明（预注册日 2026-11-22 + M0 锚点 10.0% + M1-M8/N1-N2 标 TBD）✅；
>   ⑦ §9 Conclusion 含诚实路线（H1/H2 证伪写成边界条件）✅；
>   ⑧ 引用含 ZhuLong-DAC + DATE27 PLACEHOLDER + 附录 G 调研文献（不编造）✅；
>   ⑨ 防伪底线全过（不编造数字/文献，不改判据/题/样本，不删他人数据）✅；
>   ⑩ Appendix D 新增（情绪机制设计细节 + 调研文献完整表 + 图表占位）✅。
> - 完成后 `WAITING=0` standby，记一行心跳（wake# 续编），等待用户下一步放行（§7.2 预注册日 2026-11-22 临近，论文重写应在预注册日前完成）。
>
> **agent 自主空间**：各节具体篇幅分配（在 6 页内）/ 压缩策略组合 / 公式排版细节 / 表格紧凑形式 / Figure 1 概念图是否用 placeholder / Appendix D 结构细节 由 agent 自主决定——用户给的是"按 v1.6 计划书重写 + 6 页硬限 + 防伪底线"，不是逐字模板。**鼓励 agent 发挥**：若重写中发现 v1.6 计划书某处需订正（如某假设陈述在 LaTeX 里更清晰、某公式符号更规范），可一并改计划书 + 论文，但必须 commit message 标注"plan + paper 同步订正"。

> 📦 已归档 · 2026-11-18 v1.6 令（假设内聚化重组：7 条并列假设 → 3 条核心假设 + 7 条子假设·总-机制-边界三层 + §5.1 臂表对应假设列 + §6 编号同步）· ✅ 已交付·报告 122386B·8 判据全通过·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.6」。

> 📦 已归档 · 2026-11-18 v1.5 增量令（§6 同步至 v1.4 口径：标题/贡献/章节/图表 4 处）· ✅ 已交付 commit `e810dc502`·报告 119150B·7 判据全通过·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.5」。

> 📦 已归档 · 2026-11-18 v1.4 令（核心认知升级情绪×长期记忆 + Full→Lite 迁移 + 开源边界收缩 + cimi_search 调研 + 合并 v1.3 预印本引用子任务④）· ✅ 已交付 commit `2c4ed787d`·v1.4·111269B·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.4」。

> 📦 已归档 · 2026-11-18 v1.3 令（补两篇 zhulong 预印本 BibTeX 引用）· ⚠️ 已被 v1.4 令合并为子任务 ④，不单独出 v1.3·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.3」。

> 📦 已归档 · 2026-11-17 22:5x 新任务令（EDA-Flow-Bench 论文重定位 + 消融设计 + 计划书 v1）· ✅ 已交付 commit `87cdb56f8`（v1 计划书）·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-17 22:5x v1」。



> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不改题/图/check、不编造数字、不删他人数据）。判断标准只有一条：**这条约束是为了「防止说谎/防止破坏」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主设计消融臂、判据与实验路线；A3/A4/… 的 idea 由你提，不要等我给。**

> 📦 已归档 · 2026-11-17 09:3x 结案令（停止 subagent 消融评测·覆盖一切前令）· ✅ 已执行（A0pp eval killed by ops）·两条认知结论（单 agent > 多 agent；自主 spawn > 用户定制）已入 MEMORY·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-17 09:3x 结案」。

> 📦 已归档 · 2026-11-16 09:0x（用户令：修正 A0′/A3 实验设计 · 限制 input 而非 output）· ⚠️ 被 2026-11-17 09:3x 结案令覆盖（subagent 消融线结案，不再追加新臂）

> 📦 已归档 · 2026-11-15 20:5x 用户令（放行 A3–A6）· ⚠️ 被 2026-11-17 09:3x 结案令覆盖（subagent 消融线结案，不再追加新臂）·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 20:5x 用户令」。

> 📦 已归档 · 2026-11-15 20:5x 运维令（放行 A3–A6·允许起实验）· ⚠️ A0′/A3 预算维度被 2026-11-16 令修正 + 整体被 2026-11-17 结案令覆盖·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 20:5x 运维令」。


> 📦 已归档 · 2026-11-15 15:0x（用户令：出「A3–A6 是什么」中文 HTML 报告 · 纯文档不跑实验）· ✅ done_all commit `afc4c83a9`·报告 `reports/report_zhulong_a3a6_arms_zh.html`（8 节齐全 + 互链✅·wake#972 核验）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 15:0x」。


> 📦 已归档 · 2026-11-15 12:5x（清盘令）· ✅ done_all（wake#975 第三轮双达标·`/home` 5.8G✅ / `/nasdata` 33G✅·三轮 wake#967/968/975·报告 `reports/report_zhulong_disk_cleanup_zh.html` + TSV `zhulong_disk_cleanup_20261115_*.tsv`）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 12:5x」。


### 📦 已归档 · 2026-11-15 07:2x 用户裁令（⛔ 停止 H2 · 写 A0/A1/A2 trace 报告 · 提出 A3/A4… idea · 采纳「独立上下文 + 固定小 token 预算」思路）· ✅ 已完成 wake#957 commit `a6f78b8bc`·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 07:2x」。


> 📦 已归档 · 2026-11-14 23:4x（清盘 + 隧道复盘）· ✅ done_all commit 03bc3224d · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。
> 📦 已归档 · 2026-11-14 18:3x（A1 提示改验证 agent → A2 新臂）· ✅ A2 三轮全完 53.3±3.8% · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。
> 📦 已归档 · 2026-11-14 17:0x（H2 恢复：改 cline 源码 + wrapper v3.0.74）· ✅ commit 39ccd44cc + 三 smoke 全过（H2 后被 11-15 07:2x 叫停）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。
> 📦 已归档 · 2026-11-13 21:2x（启动 subagent 消融）· ✅ A0/A1/A2 全完 + P4 报告 commit 9b0737fe4/a6f78b8bc · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。

> 📦 已归档 · 2026-11-12 21:2x 压缩机制消融（basic vs agentic）·✅ 已交付 commit e09c7e238 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。
> 📦 已归档 · 2026-11-12 15:4x B_en_r1 基座对齐重跑·✅ done_all commit a909fe482 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。
> 📦 已归档 · 2026-11-11 22:4x RU+regrade+r3重跑 + 11-11 lang-audit·✅ 已交付 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准（本线消融实验的基座/题量/协议口径不受其影响）。



> 📦 已归档 · 2026-11-07 08:3x 两轴消融 thinking×lang·✅ 30/30 已交付 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。
> 📦 已归档 · 2026-11-05 19:2x P0 双盲裁定·✅ CLOSED · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。

### 📦 已闭合（batch 15/16，原文见 `ZHULONG_TASK_ARCHIVE.md`）

> 🚨 11-03 21:0x llama.cpp + Qwen3.5-0.8B 安装（smoke 双过）✅ · 11-02 21:3x Tab-3 美观改进（`Tab3_改进建议.html` 已入库，`6_exp.tex` 已落地）✅ · 10-30 22:2x zhulong-full×kimi-k2.6 5-run（**85.0±2.5%**，vs cline 86.8±1.6% Δ−1.8pp）✅ · 10-29 21:5x 论文审阅（92.8KB 报告，P0=1/P1=3/P2=11）✅ · 10-26 08:1x 作废 224219+重跑 glm53-full（已被 10-27 令覆盖）。详情见 archive §batch 15/16。


### 📦 归档指针 · 2026-10-25「按外部评审意见改论文（含 57.4pp 归因硬伤）」· 已执行完毕（10-26 令并行）。要点：改稿须如实标注「待补」及补法，不得编造数字/文献。原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-11」。

### 📦 已归档 batch 13 · 2026-10-27（*pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（硬上限 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
