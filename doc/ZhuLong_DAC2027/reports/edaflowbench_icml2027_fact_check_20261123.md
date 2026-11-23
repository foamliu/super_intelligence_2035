# EDA-Flow-Bench_ICML2027 论文事实核查报告

**审阅范围**：`main.tex` + `sections/0-11_*.tex` + `appendix/A-D_*.tex` + `references.bib`
**审阅日期**：2026-11-23
**对照数据源**：EDA-Flow-Bench 评测仓库（`/nasdata/app.e0031982/code/EDA-Flow-Bench`）实测 + `doc/AGENTS.md` 冻结口径 + 11 月评测进展报告

---

## 严重问题（事实错误 / 数据自相矛盾）

### P1. 表 1 与表 2 的 UNKNOWN 数字差 2.4×，论文未解释

- **表 1（M0 baseline，section 6 L41）**：`UNKNOWN 49/696 7.0%`
- **表 2（failure-by-domain，appendix B L134）**：`UNK total = 119`
- **section 7 L5**：`residual UNKNOWN 7.0% (49/696)`
- 119/696 = 17.1%，**不是 7.0%**；119 - 49 = 70 = ERROR 数。
- 论文 L90-96 隐约解释"UNKNOWN column is dominated by the ERROR-status runs (aborted pre-judging)"，但**未明说**表 2 UNK(119) = 表 1 UNKNOWN(49) + ERROR(70)。读者会误以为同一指标两个数字打架。
- **建议**：表 2 caption 或脚注显式标注"UNK 列含 70 个 ERROR 终态 run（判分前中止，无 timeout/infra 签名）+ 49 个 FAIL-with-submit UNKNOWN"，并把表 1 的 UNKNOWN(49) 与表 2 UNK(119) 的关系画清楚。

### P2. 表 1 失败分类（4 类）与表 2 失败分类（8 类）口径无法对账

- 表 1：`no-output/aborted 146 + semantic/partial 437 + contract/format 2 + UNKNOWN 49 = 634`（非 PASS）
- 表 2：`NOSUB 70 + FMT 2 + RT 132 + SEM 305 + UNK 119 = 628`（FAIL+ERROR，不含 ABSENT 6）
- 表 1 `no-output/aborted 146` vs 表 2 `NOSUB 70`：差 76（= ERROR 70 + ABSENT 6）——但论文未明示这个映射。
- 表 1 `semantic/partial 437` vs 表 2 `RT 132 + SEM 305 = 437`：**完全相等**，但论文未点明 RT+SEM = semantic/partial。
- **建议**：在 section 7 或 appendix B 加一段"表 1（run 级终态分诊，4 类，含 ABSENT）与表 2（triage 后逐 run 类别，8 类，不含 ABSENT）的口径映射"，否则两表数字无法对账，审稿人会质疑。

### P3. `\ScriptPass{76.5%}` 归因错误

- **intro L5**：`VerilogEval, RTLLM, and similar benchmarks report $\geq$\ScriptPass{} on isolated scripting tasks`
- **abstract L3**：`versus \textbf{\ScriptPass{}} on single-script EDA benchmarks`
- 但 `\ScriptPass=76.5%` 实际来自 `references.bib` 的 `zhu2026edascript`（"EDA-Scripting-Bench: 449 tasks, PyAether/SKILL/Tcl, 76.5% Pass@1"）——**这是作者自己的 preprint 数字**，不是 VerilogEval/RTLLM 的报告值。
- VerilogEval（liu2023verilogeval）原论文报告 GPT-4 Pass@1 约 60-70%，RTLLM（lu2024rtllm）也是类似量级，**没有公开报告 76.5%**。
- **建议**：把 76.5% 明确归因为"our prior EDA-Scripting-Bench `\cite{zhu2026edascript}`"或"internal scripting baseline"，不能写成"VerilogEval/RTLLM report ≥76.5%"。否则是错误归因 + 误导审稿人。

### P4. 附录 A 各 shard case 数加和算术错

- **appendix A L54-55**：`2043 cases (A: 443, B: 483, C: 564, D: 554; 36 retired, all in shard A, 2007 active)`
- 443 + 483 + 564 + 554 = **2044**，不是 2043。差 1。
- 2044 - 36 retired = 2008 active，不是 2007。也差 1。
- **建议**：核对实际数字后修正总数或某 shard 计数。

### P5. 附录 A task id 格式描述与实际不符

- **appendix A L83**：`id: unique task identifier (area-group-prefixed, e.g., A-001)`
- 实际所有 case_id 格式是 `EDA-Eval-DesignFlow-XXX-001`（如 `EDA-Eval-DesignFlow-InstCdlConsist-001`），**没有任何 `A-001`/`B-001` 这类 area-group-prefixed 格式**。
- **建议**：改示例为 `EDA-Eval-DesignFlow-InstCdlConsist-001` 或描述真实命名规则。

### P6. `PLACEHOLDER_DATE27_ZHULONG` 是占位符引用，违反"不编造文献"铁律

- **references.bib L168-173**：`@unpublished{PLACEHOLDER_DATE27_ZHULONG, title={[DATE27 ZhuLong Preprint Title -- to appear 2026-12]}, author={Anonymous}, note={PLACEHOLDER: ...}}`
- 在 `section 2 L14` 和 `section 8 L5` 被 `\cite{PLACEHOLDER_DATE27_ZHULONG}` 引用。
- AGENTS.md §1.5 铁律 5「不编造文献」+ §10 双盲匿名要求；占位符引用编译会出 `[?]` 或显示成可疑条目。
- **建议**：DATE27 论文 12 月才出，投稿前要么删除该引用（改为"prior work, in preparation"脚注），要么等 DATE27 出来再填真实 bib。**ICML 投稿不能带 PLACEHOLDER 引用**。

### P7. 附录 A Task Example 是 [TODO] 占位

- **appendix A L8-13**：`[TODO: show one complete task: prompt + assets + check.py + test\_rationale. Suggested: a medium-difficulty schematic\_netlist case ...]`
- ICML 投稿不能有 TODO 占位。
- **建议**：选一个中等难度 schematic_netlist case（如 InstCdlConsist-001，case-study 报告里已分析过）填入完整 prompt + check.py 摘要 + test_rationale。

---

## 中等问题（口径不一致 / 措辞误导）

### M1. abstract 把 M0 同时描述为 DeepSeek-V4-Pro 和 doubao-seed-2.0-pro-cloud

- **abstract L3**：`a single frontier backbone reaches only \MzeroPass{} Pass@1` —— 上下文指 696-run Full-set snapshot（DeepSeek-V4-Pro）
- **abstract 末尾**：`M0 is evaluated on Lite (\MzeroAnchor{}, doubao-seed-2.0-pro-cloud)`
- 同一 abstract 里 M0 的"骨干"在两句话间从 DeepSeek-V4-Pro 切到 doubao-seed-2.0-pro-cloud，读者会困惑 M0 到底是哪个模型。
- 论文用 `\MzeroPass`（Full-set，DeepSeek）vs `\MzeroAnchor`（Lite top-120，doubao）区分，但 abstract 没点明这是两个不同模型 + 两个不同子集。
- **建议**：abstract 第一次提 M0 时加一句"two complementary M0 anchors: a Full-set descriptive snapshot (DeepSeek-V4-Pro, \MzeroPass) and a Lite top-120 arm anchor (doubao-seed-2.0-pro-cloud, \MzeroAnchor)"。

### M2. top-120-of-Lite Pass@1 (10.1%) 反而高于全 Lite (9.3%)，论文未讨论

- **section 6 L80**：`M0 arm anchor ... top-120-of-Lite: \MzeroAnchor{} (12/119 decided)` = 10.1%
- **同段**：`full Lite \LiteSet{} M0 under the same backbone is 9.3% (45/483 decided)`
- top-120 是按 chain length **最长**的 120 题（应该更难），但 Pass@1 反而**高** 0.8pp。
- 这反直觉，论文未解释。可能原因：top-120 的 decided 率高（119/120=99.2% vs 全 Lite 483/500=96.6%），或长链题反而更结构化，但论文没说。
- **建议**：加一句"the top-120 anchor's slightly higher rate reflects higher decided-rate on longer-chain tasks, not easier difficulty"或类似解释。

### M3. "DeepSeek-V4-Pro has since been deprecated as the arm backbone" 与 11-22 后实际使用矛盾

- **appendix B L60** + **section 5 L112**：`DeepSeek-V4-Pro, which has since been deprecated`
- 但用户 11-22 令追加 deepseek-v4-pro 强模型 3-run（r1 已完成 21.78%，r2 跑中，r3 待起），用于与 doubao-pro 做 McNemar 配对检验。
- 论文 v1.7 写于 11-21 前后，那时 deepseek 确实"下线"；但 11-22 后又启用了。"deprecated" 措辞与现实矛盾。
- **建议**：改为"DeepSeek-V4-Pro was initially retired from the arm backbone due to API availability; a 3-run re-evaluation was launched 2026-11-22 after canary validation, results pending"或直接更新为最新状态。

### M4. doubao-pro 全 Lite 9.3% (single run) vs 月报 3-run mean 10.18% ± 1.45% 口径不同

- **section 6 L80**：`full Lite \LiteSet{} M0 ... 9.3% (45/483 decided)` —— 这是 doubao-pro r1 单 run
- 月报与进展报告：doubao-pro 3-run mean = 10.18% ± 1.45%（45/57/45 PASS）
- 论文 v1.7 写于 11-21，那时只有 r1，OK。但论文继续投出去时，3-run 数据已就位，应更新为 3-run mean。
- **建议**：camera-ready 前把 9.3% (single run) 更新为 10.18% ± 1.45% (3-run)，并补 McNemar 配对检验。

### M5. "8 workers" vs README 默认 16 workers

- **appendix B L21** + **section 3 L26**：`696-run snapshot ... 8 workers`
- README 默认 `--workers 16`，用户基准 `51/484 = 10.5%（500 cases · 16 workers · ~2:57）`。
- 696-run 用 8 workers 是历史配置，OK 不算错，但与后续 Lite 500 评测（16 workers）配置不同，论文未说明。
- **建议**：在 appendix B caption 加一句"the 696-run snapshot used 8 workers (later Lite evaluations use 16)"。

---

## 轻微问题（引用规范 / 写作完整度）

### L1. `dong2026flowfixer` 引用不规范

- **references.bib L17-22**：`journal={IEEE Xplore}, year={2026}`
- "IEEE Xplore" 是数据库平台，不是期刊/会议名。应填具体期刊或会议（如 IEEE TCAD / DAC / ICCAD）。
- **建议**：补全 venue 或改为 `note={manuscript, available on IEEE Xplore}`。

### L2. `zhu2026edascript` 缺 arXiv 编号

- **references.bib L31-37**：`journal={arXiv preprint}, year={2026}` —— 没有具体 arXiv 编号
- 同作者的 `liu2026runreadbackrefine` 有 `arXiv:2611.19056`，但 `zhu2026edascript` 没有。
- **建议**：补 arXiv 编号或改为 `note={manuscript in preparation}`。

### L3. `liu2026runreadbackrefine` arXiv 编号 2611.19056 未独立核验

- **references.bib L160-166**：`arXiv:2611.19056`
- references.bib L108 注明"arXiv 编号来自 cimi_search 返回，未独立复核"。
- AGENTS.md §1.5 铁律 5 要求"引用必须可核验（标题 + 年份 + 会议/arXiv），不确定的标「二手·未核」"。
- **建议**：投稿前到 arXiv.org 核验该编号是否真实存在 + 内容匹配。

### L4. section 6 表 2 整表 \TBD + section 7 affective-mechanism 段 \TBD

- **section 6 L46-71**：criteria check 表所有 Est. 和 Verdict 都是 `\TBD`
- **section 7 L22**：`Affective-mechanism analysis (placeholder, pending evaluation). \TBD{} pending evaluation.`
- 这是 AGENTS.md 已知阻塞（令纪律：3-run 出来先报数，等用户裁定才回填），但 ICML 投稿前必须填掉。
- **建议**：等 deepseek 3-run + 配对检验完成后批量回填（18 处 \TBD）。

### L5. `rao2026sap` 和 `sulthanpete2026nyris` 与论文主题关联弱

- **references.bib L91-105**：这两个引用似乎是为了论证"proprietary data withheld is acceptable practice"而引入的工业案例。
- 在正文中未见明显 `\cite{rao2026sap}` 或 `\cite{sulthanpete2026nyris}`（需 grep 确认）。
- **建议**：grep 确认是否被引用；若未引用则从 bib 删除（避免 unused reference 警告）。

---

## 核查通过项（已验证正确）

- ✅ `\Neval=696`、`\MzeroPass=10.0%`（62/620 decided）、`\LiteSet=500`、`\ScriptPass=76.5%` 与 AGENTS.md 冻结口径一致
- ✅ 696-run batch `run_batch_20261109_171201` 实际存在
- ✅ 表 B per-domain 各行 PASS+FAIL+ERROR+ABSENT=Total 加和对（13 域全对）
- ✅ 表 B per-domain Pass% 计算对（13 域全对，如 pnr_signoff 5/24=20.8%、physical_verify 2/68=2.9%）
- ✅ 7.1× domain gap = 20.8/2.9 = 7.17 ≈ 7.1× ✓
- ✅ 7.6× gap = 76.5/10.0 = 7.65 ≈ 7.6× ✓
- ✅ doubao-pro r1 = 45 PASS + 438 FAIL = 483 decided, 17 ERROR/ABSENT → 论文 L80 "45/483 = 9.3%" ✓
- ✅ `\MzeroAnchor=10.1%` = 12/119 = 10.08% ✓
- ✅ 47 pilot runs 中位 26.5 calls / IQR 13.8-38.0 / 20.5 iterations / 1047s / 41.2% MCP —— 与 section 7 L14 + section 2 L5 + appendix B L143-148 多处一致引用
- ✅ ABBA compaction ablation 6 轮数字内部一致（basic 67.5/70.0/70.0 mean 69.2%；agentic 57.5/60.0/60.0 mean 59.2%）
- ✅ 双盲匿名：作者块 `Anonymous Submission` / `Anonymous Institution`，无真实作者名

---

## 优先级建议

| 优先级 | 问题 | 投稿前必须修 |
|:--|:--|:--:|
| P1 | 表 1 vs 表 2 UNKNOWN 数字差 2.4× | ✅ |
| P2 | 表 1 vs 表 2 失败分类口径无法对账 | ✅ |
| P3 | `\ScriptPass` 归因 VerilogEval/RTLLM 错误 | ✅ |
| P4 | 附录 A shard 数加和算术错（2044≠2043） | ✅ |
| P5 | task id 格式描述与实际不符 | ✅ |
| P6 | PLACEHOLDER 占位符引用 | ✅ |
| P7 | 附录 A Task Example [TODO] | ✅ |
| M1-M5 | 口径不一致 / 措辞误导 | camera-ready 前 |
| L1-L5 | 引用规范 / 写作完整度 | camera-ready 前 |

**核心结论**：论文有 **7 个严重问题**（P1-P7）必须在 ICML 投稿前修复，其中 P1/P2（UNKNOWN 数字打架 + 失败分类无法对账）和 P3（76.5% 归因错误）是审稿人最容易抓的硬伤；P6/P7（PLACEHOLDER 引用 + TODO 占位）是投稿纪律问题，不能带进投稿版。
