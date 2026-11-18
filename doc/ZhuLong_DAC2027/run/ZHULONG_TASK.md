# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

> 🔴 **2026-11-18 22:3x 用户令 — 朋友评审意见：请「参考」并逐条研判（P0 三项须先定论）· ✅ 主体已交付**（wake#1350 commit `cfb185159`·P0 3/3 结论 + 11 项处置矩阵 采纳10/部分1/不采纳0·报告 `reports/report_edafb_friend_review_response_zh.html`·论文重编译 12p/0err/0undef/235123B·写作层 5 项 P2①③④⑤+R4 延至预注册后）
>
> **用户原话**：「朋友提出意见，下发给 zhulong agent，请他参考」。
> **输入材料（完整原文 163 行，不要改写、不要删）**：`run/ZHULONG_REVIEW_20261118_friend.md`
> 该文件含 **文档 A**（R1–R5 结构性风险 + 三、细节 5 条 + 四、结论）与 **文档 B**（sub-hypotheses 与 ablation 数量评估、2.1–2.4 逐臂分析、方案 A/B）。
> **性质**：外部评审输入，**不是指令**——请逐条研判（**采纳 / 部分采纳 / 不采纳** + 理由 + 影响面），**不要照单全收**，也不要因为"参考"就一条不改。
>
> **P0（实验设计地基，必须先给结论；不改也要写明理由与代价）**：
> 1. **R1 · H1c 定义漏洞**：S1 臂的 session 内 in-context learning 本身即短期记忆 ⇒ `S1 ≤ M0` 可能被"伪证伪"。要求：把 H1c 精确化为「**跨 session 长期记忆是跨 session RSI 的前提**」，并在 S1 臂**显式禁止任何 session 间持久化**（含 harness 层文件残留）；若判定原陈述无误，须给出"session 内自改进不可能等效于记忆"的反驳证据。
> 2. **R2 · 功效不足**：§5.3 自承 120 题下 McNemar 功效 ≈0.62（40% 真效应会漏检）；**M6 的失败子集仅 ~40 题，3pp 判据功效 <0.3，属假阴性高危臂**。要求二选一并落成文字：(a) 最小矩阵抬到 **≥200 题/臂**（M6 失败子集 ≥80），(b) 明确定位为 **pilot signal，不作结论**，且 **abstract 不报具体 pp 数字**。禁止"120 题跑出 2.1pp 就写 H1a 部分支持"。
> 3. **R5 · M0 锚点子集口径**：10.0% 是 696-run 全集（62/620）的值，而最小矩阵取 top-120 by chain length ⇒ 子集 M0 很可能只有 4–6%。要求：**M0 锚点必须用同子集实测值**（重跑或明确声明），同步改 §5.4「M0 引用快照」行。
>
> **P1（臂表收敛，需给明确结论）**：参照文档 B 的**方案 A**（13 → **10 臂主表 + 3 臂附录**：主表 `M0·M3·S1·M3+S1·N1·N2·M4·M5·M6·M7`；M1 移附录；M2 仅作 M5/M7 对照、**撤掉 M2≥M0+2pp 与 M3≥M2+1pp 两条判据**；M8 移附录）。若采纳，须同步：§5.1 臂表 / §5.2 假设映射 / §5.3 功效与题量 / §5.4 时间线 / §6 判据编号 / 论文 §5 与 §6 对应段落。若不采纳，逐臂说明保留理由与功效依据。
>
> **P2（写作与口径，逐条给结论）**：① abstract 里 "7.6× drop" 与 "7.1× domain gap" 并置需半句区分（跨任务难度 vs flow 内域间差异）；② H2b 联合判据的**中间地带**（记忆 0.6–0.8×、Pass@1 持平）需定义「弱支持」；③ 表 5 的 UNK **119** 与正文 **49** 口径不一致，须加脚注；④ **DATE27 的 PLACEHOLDER 引用**必须在截稿前落实（否则 Related Work「继承 DATE27 骨架」缺支撑）；⑤ B.2「five machine-days」与 §5.4「28 天」量级差异 ⇒ 拆成「多骨干扫描」与「全臂理想矩阵」两个里程碑。
> **R3/R4 也要给结论**：R3 = M4 泄露审计需**机器可判代理指标**（记忆条目与目标域 prompt/文件名/断言字面量的 n-gram 重叠率，人工只审 borderline）；R4 = 论文 **§4.5.1 公式旁补「与最近邻方法的计算差异」**（surprise 用 KL(posterior∥prior) 而非 embedding 距离；penalty 是 sunk-cost 而非固定权重），并说明 M5 的 α/β 扫描考的是「机制贡献」还是「超参」。
>
> **纪律**：
> - 逐条处置矩阵必须写明 **采纳/部分/不采纳 + 理由 + 影响面（改哪些文件/哪些臂/要不要重跑）**；不采纳项要给"不改的代价"判断。
> - **不改任何既有实测数字**（696-run / 10.0% / 62·558·70·6 / 2.9% physical_verify 等），不编造新数字；不改题、图、check、他线文件。
> - **⚠️ 预注册日 2026-11-22 只剩 3 天**：优先级 = 保证"预注册材料可冻结"。请明确划分：哪些进 **plan v1.8**（设计层）、哪些进**预注册文档**（判据层，冻结后不可改）、哪些只改**论文正文**（写作层）。若 3 天内做不完，先交 P0 + 处置矩阵，其余排到预注册后。
>
> **验收**：① P0 三项均有明确结论；② 处置矩阵覆盖 R1–R5 + P2 五项 + 臂表收敛；③ 若动臂表/假设 ⇒ 四处编号（§5.1/§5.2/§5.3/§6）与论文对应章节同步且自查一致；④ 论文若改，重新编译 `pdflatex→bibtex→pdflatex×2` 记页数/0 err/0 undef（页数变化须说明原因）；⑤ 交付中文 HTML 报告 `run/reports/report_edafb_friend_review_response_zh.html`（与本线 `report_edafb_zh_translation_zh.html` 同目录，单文件自包含无外链：逐条处置矩阵 + P0 改前/改后对照 + 臂表 diff + 待决项）；⑥ MEMORY/daily 一行 `[friend-review] P0 3/3 结论 · 采纳 n / 部分 m / 不采纳 k · plan vX · commit <sha>`。
> **提交**：前缀 `zhulong review:`，只 `git add -- doc/ZhuLong_DAC2027/**`（含本次评审输入文件与报告）。

> 📦 已归档 · 2026-11-18 20:5x zh-cn 令（论文全文加中文对照·注释态）· ✅ 已交付 round1 `abf24281f`+round2 `28e77662f`·编译 11p/0err/230611B 同字节·报告 `reports/report_edafb_zh_translation_zh.html`·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 20:5x zh-cn」。



> 📦 已归档 · 2026-11-18 v1.7 令（放行直接改论文正文：按 v1.6 计划书重写 `EDA-Flow-Bench_ICML2027/` 正文 main.tex + sections/*.tex + appendix/*.tex + main.bbl·正文 ≤ 6 页·10 判据全通过）· ✅ 已交付·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.7」。

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
