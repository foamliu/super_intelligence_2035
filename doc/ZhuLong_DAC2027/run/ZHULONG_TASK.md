# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不改题/图/check、不编造数字、不删他人数据）。判断标准只有一条：**这条约束是为了「防止说谎/防止破坏」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主设计消融臂、判据与实验路线；A3/A4/… 的 idea 由你提，不要等我给。**

> 📦 已归档 · 2026-11-15 15:0x（用户令：出「A3–A6 是什么」中文 HTML 报告 · 纯文档不跑实验）· ✅ done_all commit `afc4c83a9`·报告 `reports/report_zhulong_a3a6_arms_zh.html`（8 节齐全 + 互链✅·wake#972 核验）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 15:0x」。


> 🔴 **运维令 · 2026-11-15 12:5x（清盘 · 最高优先 · 本轮第一件事）· 未完成**
>
> **用户原话**：「安排 zhulong 清理硬盘啊」
>
> **现状（你 wake#966 自报）**：`/home` 仅 **267M（100% 满）**、`/nasdata` **9.8G**。已卡住 loop/git 余量，也让 A3–A6 的（a）项磁盘前置无法满足。11-14 23:4x 已清过一次（done_all），本次属**复发**。
>
> **目标**：`/home` 可用 **≥5G**、`/nasdata` 可用 **≥25G**（回到 11-14 清盘后的口径）。达不到就把能清的全清掉，并在报告首屏写清还差多少。
>
> **硬护栏（违反则本轮作废，宁可少清）**：
> 1. **禁删在跑评测的产物**：posttrain 的 baseline batch `2026_1115_110506`（`run_cline_script -p 8`，PID3506378/3506387）的 jobs/工作目录、`/tmp` 下其 code/log/data-dir、任何 cline session 目录。
> 2. **禁 kill 任何进程**（含他线 loop）；禁改他人文件；遇到 `Permission denied` 记下来，不 sudo 硬来。
> 3. **禁删**：git 仓库、`eda_fastmcp` / `EDA-Eval-PyAether` / `EDA-Flow-Bench` 源码与题面、模型权重/serve、`~/.ssh`、token、正在用的 conda/venv、`/nasdata` 上 designflow 的 ledger/trace。
> 4. **先列后删**：每次删除前 `du -sh <path>` + `ls -lt` 留证；只对**明确路径**执行 `rm -rf`，**禁止** `rm -rf /home/*`、`rm -rf ~/*` 这类通配；删除清单落 `run/zhulong_disk_cleanup_<YYYYMMDD_HHMM>.tsv`（路径 / 字节 / 理由），随 commit 入库。
>
> **执行顺序（先安全后激进）**：
> - **a) 缓存**：`~/.cache/pip`、`~/.npm/_cacache`、`~/.cache/uv`、`~/.cache/huggingface`（**仅当无下载在跑**）、`__pycache__`、`*.pyc`
> - **b) 日志/临时**：自己产生的 `*.log`（>3 天）、旧 screen/nohup 日志、core dump、`/tmp` 下自己建的临时目录（**避开** posttrain 正在写的）
> - **c) 备份/中间物**：`*.bak*`、`*.old`、`*.tmp`、`*~`、失败的 run 目录（**无 `result.json` 且 mtime>3 天**）
> - **d) 旧产物**：只删**本线**已被取代/已归档的；**最新一版与正在用的绝不删**；不确定的先列清单不删
> - **e) `/nasdata`**：旧 scan 快照（`_hist` 留最新一版）、旧 jobs-dir、有 `.txt` 可复原的重复 `.b64`（先删重复编码件，保留文本）
>
> **验收（缺一不可）**：
> - `df -h /home /nasdata` **before/after 对比**；达标或写清差额
> - `ps -ef | grep run_cline_script` 仍能看到 baseline eval 存活（或已正常结束）
> - `git status -sb` 正常、loop 进程未挂
> - 报告 `reports/report_zhulong_disk_cleanup_zh.html`（中文、单文件、0 外链 / 0 script）：首屏两行给 before/after，随后「删除清单 top20（路径/大小/理由）」「未删项及原因」「若仍不足，下一步需要谁做什么」
> - `MEMORY_ZHULONG.md` 顶部一行结论（before/after + 是否达标）+ `daily-memories/2026-11-15.md` 流水 + commit 前缀 `zhulong disk:`
>
> **自主性**：清哪些由你判断，只要不碰上面四类禁区。若判断某目录可能是他线正在写的（mtime 很新），**先列不删**，在报告里点名让运维确认。


### ✅ 用户裁令 · 2026-11-15 07:2x（**⛔ 停止 H2 · 写 A0/A1/A2 中文 HTML 报告 · 提出 A3/A4… 消融 idea（目标：多 agent ≥ 单 agent）· 采纳「独立上下文 + 固定小 token 预算」思路**）· ✅ 已完成（wake#957·commit a6f78b8bc + 报告 Q1 补充 commit 见下）· **等用户裁决 A3-A6 起跑顺序**

> **用户原话**：「zhulong：停止H2。如果A2弱于A0，那么在A2基础上做的H2就没有意义，是浪费时间。现在请zhulong分析A0/A1/A2的日志trace，撰写中文HTML报告，提出A3/A4/... 的消融idea，以争取多agent得分>=单agent。另外，我有一个思路请zhulong考虑：多agent的主要优势在于独立上下文 -> 如果解决一个任务所需上下文 > 底模LLM上下文窗口，且单agent压缩机制不足以保留足够细节，那么多agent就可能优于单agent。因此是否可以考虑给每个agent(包括主agent）以确定且较小的token（in & out）预算，当然这就需要弱化（重测）基线。」

**零、立即动作（本轮第一件事，做完再谈别的）**
1. **停 H2**：`kill` `run_h2_ablation.sh` PID2017148 及其 cline 子进程（`pkill -f run_h2_ablation` + 逐 PID 核）；**已在跑的 B 臂 trace 一律保留不删**（它们是 H2 复现证据，也是 H2「子模型恒=父模型」的实证）；`§7 PHASE` 改 `h2_stopped_by_user`；`WAITING` 按实际（无 eval 在跑 ⇒ 0）。
2. 在 `MEMORY_ZHULONG.md` 记一行：**H2 停止理由 = A2(53.3%) 显著弱于 A0(69.2%)、A1(66.7%)（per-round McNemar A0vsA2 p=0.0008 / A1vsA2 p=0.006），在 A2 基础上做子模型梯度无科学意义**。若你有相反证据或更好的判断，直接写进 MEMORY 并说明——**决策可以被更好的论证推翻**。

**一、任务：A0/A1/A2 日志 trace 分析 → 中文 HTML 报告**

- **报告文件（新建，用户点名）**：`reports/report_zhulong_subagent_a0a1a2_trace_zh.html`（中文、单文件自包含、**0 外链 / 0 script**、图表用内联 SVG）。
- **必须回答的问题（逐条给证据：`路径:行号` 或命令输出）**：
  1. **A2 为什么掉 15.9pp？** 已知线索：`mcnemar_subagent_results.json.key_finding` 说主因是**生成吞吐下降**（cline_ok 60% vs A1 72–90%），而 gen-rate 都 ~87%（⇒ 不是代码质量，而是**没跑完/被截断**）。请用 trace **量化验证或推翻**这条：A2 的 per-task `wall_sec`、`max turns 命中率`、`finishReason` 分布、超时数、`spawn_agent` 调用次数分布（0 次 / 1 次 / >1 次）、子 agent 的 token 与耗时占比。
  2. **spawn 的「采纳率」**：主 agent 是否真把子 agent 的结论写进代码？（A2 的 verifier 建议是否被采纳 → 采纳 vs 未采纳题目的 Pass 差）。这是 `mcnemar_subagent_results.json.deferred` 里挂着的欠账，本轮必须还。
  3. **A1 为什么没增益（−2.5pp，p=0.68）？** 子 agent **无 MCP 工具**（只能 read_files/search_codebase/run_commands）⇒ 「研究委托」是否只是把主 agent 的 token 花了两遍？（对比 A0/A1 的 main tokens、tool histogram、重复探索 rate）。
  4. **上下文维度**：三臂的 main-agent 峰值上下文占用、compaction 触发次数与压缩后丢失率（能测就测，测不了写「未采集 + 补法」）。
  5. **三臂并列成绩表**（ITT mean±std、majority vote、3 轮逐轮数字、McNemar 三对，b/c/p/n 全列），**负结果照写**。
- **报告纪律**：更新版报告顶部要有**一句话结论**；旧报告 `reports/report_zhulong_subagent_ablation_zh.html` 保留为历史档，加 SUPERSEDED 指针（不删）。

**二、任务：提出 A3 / A4 / … 消融 idea（判据：多 agent ≥ 单 agent）**

- 每个 idea 必须写成**可执行臂**：`臂号 | 唯一变量 | 机制（谁 spawn、何时 spawn、子 agent 看到什么、结果怎么回传） | 预注册判据 | 预期机制 | 风险与失效模式 | 预估成本`。
- **硬约束**（这些是前面已经踩过的坑，别再踩）：
  - 子 agent **继承父模型**、**无 MCP 工具**、`maxIterations` 继承父值 ⇒ 任何依赖「给子 agent 换模型/换工具/换 iter」的设计**当前技术不可行**（除非重做 wrapper 并 smoke 证明）。
  - `-p 8` 下共享 data-dir 会出「messages must not be empty」竞态 ⇒ 需要并发的臂必须 per-task data-dir 隔离，并在臂描述里写清。
  - 每个臂都要先说清**「为什么这条能超过 A0=69.2%」**，否则不做。
- **候选起点（供参考，可采纳可推翻，须自己论证）**：
  - **A3 上下文预算臂（用户思路，优先评估）**：给**主 agent 与子 agent 都设确定且较小的 token 预算（in 与 out 分别设上限）**，超限即强制交付/交接；同时**弱化并重测基线**（预算打平时主 agent 会怎么退化的「预算基线」必须先测出来，否则没有可比性）。
  - **A4 接力臂（接力而非并行）**：把序列拆成「多段」，每段一个**全新上下文**的子 agent，段间只传**结构化交接物**（文件 + 摘要），主 agent 只做编排与合并（典型适用：长 trace 深读 → 逐段结论）。
  - **A5 严格「写后只挑刺」臂**：verifier **只允许输出 issue list 到文件**，不得改代码；主 agent **必须逐条 triage（accept/reject + 理由）后才能提交** ⇒ 把 A2 的「无脑采纳/吞吐下降」隔离开。
  - **A6 门槛臂（gate on trigger）**：只在「主 agent 判为高风险 / 上下文占用 > X% / 已有失败重试」时才 spawn，其余一律不 spawn（前提：先做 A3 的上下文测量）。
- **必须先做的「可行性预检」**（写进报告，不要直接开跑）：每条 idea 在 cline v3.0.74 wrapper 的**注入强度**（提示注入 vs hook vs wrapper 级），能否**不弱化判据**地实施。

**三、用户思路（必须正面回应，写进报告 §「为什么多 agent 可能赢」）**

> 多 agent 的主要优势在**独立上下文**：当**解决一个任务所需上下文 > 底模上下文窗口**、且**单 agent 压缩不足以保留足够细节**时，多 agent 才可能优于单 agent。⇒ 设想：给**每个 agent（含主 agent）确定且较小的 token（in & out）预算**。

- 你需要在报告中：
  1. 把这条思路**形式化**成可检验假设（例：`H_ctx`：在「总上下文超窗」的分层子集上，多 agent 的 Δ 显著为正，且在「不超窗」子集上 Δ ≤ 0；即 **Δ 与 (所需上下文 / 窗口) 正相关**）；
  2. 给出**分层口径**：用 A0 的 per-task 峰值上下文 / 压缩次数 / trace 长度做分层变量，把 40 题分成「超窗风险高 / 低」两层再比；
  3. **诚实说明**：若当前 40 题子集**根本不够长**（大多数题不触发窗口），那就**明确写「本数据集无法检验该假设」**并给出**能检验它的任务构造方案**（例如取 158 全集中 trace 最长的 top-k）。注意：40 题上的「无差异」**不能**用来否定该假设——那是检验力问题，不是结论。

**四、交付清单**
1. `reports/report_zhulong_subagent_a0a1a2_trace_zh.html`（含 §三 的假设形式化）
2. `A3/A4/… idea 表`（可直接接成下一轮 RUN_ARMS）
3. `MEMORY_ZHULONG.md` 一节 + `daily-memories/2026-11-15.md` 流水 + commit/push
4. **自主发起实验**：你可以自行决定何时起新臂。唯一要求是**资源不与他线冲突**（GPU/沙盒空闲）、**起跑前在 MEMORY 写一句「臂号 + 唯一变量 + 判据」**，这样结果可追溯。（本轮重点是报告+idea，但如果你判断某个小实验能立刻验证关键假设，直接做。）


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

### 📦 已归档 batch 13 · 2026-10-27（原文见 `ZHULONG_TASK_ARCHIVE.md` §归档 batch 13）

> 以下均已闭合/已被取代，仅留 1 行指针，需要时读 archive：10-26 ops 中继修复（relay PID118463 活，.last_run_id=128）· 10-26 cimi_search/cimi_fetch 挂载（research MCP 可用）· 10-24 23:0x DAC 审稿+改稿方案（41.6KB 报告已交付）· 10-24 19:0x 论文排版（commit 3651b322）· 10-24 22:23 配置对齐（maxTokens 16384→8192，已被 10-26 令覆盖）· 10-24 22:15 已核实事实（RUN_ID 115/117）· 10-24 22:1x 停 cline-full+重跑 5-run（已被 10-26 令覆盖）· 10-24 20:2x cline vs zhulong-CLI 差异归因（25.9KB）· 10-24 15:4x 引用修正（Lemma→Claim）· 10-24 16:1x refs 单独起页 · 10-24 13:0x 执行令（commit d2d9bb7a）· 10-23 22:1x cline×deepseek-v4-pro×full 5-run（**部分活跃·r1 已硬切留证，r2-r5 待裁决**）· 10-23 09:4x 作废 r1-r3+重跑（已被 10-26 覆盖）· batch 10/11/12 更早指针见 archive。
### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑）。**注**：`wo_sandbox`(=rag 已测) / `wo_selfexpl`(已测·运维令二十六排队干净重测) 不再「暂缓」。 |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 📦 已归档（2026-10-20，batch 6）：运维令 十四 ~ 二十四（10-13 ~ 10-15 批次）

> 均已闭合（echo 数据/消融建议书/paper 编译/SKILL-Tcl 并入/沙盒暂停-恢复撤销等）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（06:4x，batch 7）：十三（75% 下限规则）+ 预留追加块

> 均已闭合/长期未使用，原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（2026-10-20，batch 4）：运维令 十二 / 十一 / 十 / 九 / (一)~(八)10-10 / (二)~(五)10-09

> 均已闭合（full_v3 5/5=82.1±3.0% 已交付、r2–r5 已完成、RAG/沙盒排查已收口）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。需要时再读。


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**（详细 bash 脚本已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·该修复已于 10-08 执行完毕，loop 持续带代理运行）：核心 = `pkill -f zhulong_loop.sh` → `export https_proxy=http://172.19.92.23:13128 http_proxy=...` → `setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &` → 复核 `/proc/$PID/environ` 含 `https_proxy`。

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**纪律**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 📦 已归档（2026-10-20，batch 5）：运维令 10-08(一) / 10-05(四~八) / 10-04(全)

> 均已闭合（HTML 报告已交、ops 中继稳定、config dir 隔离已落地、试验次序 B→C1→C2→S1 已生效、环境迁移已落地）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。


   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
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
