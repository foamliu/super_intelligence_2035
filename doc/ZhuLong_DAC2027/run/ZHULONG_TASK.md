# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

### 🔴 用户令 · 2026-11-14 18:3x（**A1 的强提示方向错了 → 改为 spawn「验证 agent」+ 对抗视角**）· 未完成 · 最高优先

> **用户原话**：「这个强提示理解，但感觉方向不对。任务开始，第一项工作就是调研背景，主 agent 上下文还空，自然没必要 spawn，真 spawn 后，这个 agent 做了调研，有了成果，又无法传给主 agent 的上下文，造成很多浪费。因此我建议通过提示让主 agent spawn 验证 agent，带有一些对抗视角，用于测试主 agent 写的代码。」

**一、为什么现在的提示是错的（用户的分析）**

现有 `SUBAGENT_HINT`（`run_subagent_ablation.sh` L47-52）要求：

> 「Before writing any code, you MUST use the `spawn_agent` tool to delegate to a **researcher** sub-agent…
> Do NOT answer directly or write code until the sub-agent returns its findings.」

**两个结构性错误**：

1. **调研阶段 spawn 是浪费**：任务刚开始时主 agent 上下文还空，没有"上下文压力"，**本就没必要外包**；
2. **子 agent 成果传不回来**：子 agent 做完调研，产出**无法注入主 agent 的上下文**（你自己 wake#926 也实测过：子 agent 只有 `systemPrompt` + `task` 两个输入、输出回传受限），
   ⇒ 主 agent 拿不到调研成果，**等于白跑一轮**，还平白多了一次往返开销。

**二、改成什么：验证 agent + 对抗视角**

**新的 spawn 触发点 = 主 agent 写完代码之后**，让它 spawn 一个**独立的验证/审查 agent**，带**对抗视角**去测主 agent 写的代码。

**为什么这样合理**：
- 主 agent 此时**已经有上下文**（自己刚写的代码、自己的推理），**正需要外部独立视角**；
- 验证 agent 的产出是**判定结论**（通过/不通过 + 问题清单），**短小、可直接被主 agent 采用**，不存在"成果传不回来"的浪费；
- **对抗性**（刻意找错）比"协助调研"更符合独立 agent 的价值。

**三、要改的具体内容**

1. **重写 `SUBAGENT_HINT`**（`run_subagent_ablation.sh` L47-52）：
   - 触发时机：**在写出第一版代码并执行之后**（不是"写代码之前"）；
   - 子 agent 角色：**adversarial reviewer / verifier**，任务是**挑错**——检查 API 用法是否正确、参数是否符合文档、边界条件、异常处理、单位/坐标/精度、是否满足题目全部约束；
   - 要求子 agent **给出明确的通过/不通过判定 + 具体问题清单（含代码位置）**；
   - **禁止**子 agent 写完整实现（只审不写），避免它变成第二个主 agent。

2. **提示措辞要点**（你自行定稿，务必体现）：
   - 「写完之后」而非「写之前」；
   - 「independent reviewer / red team」而非「researcher」；
   - 「find what is wrong」而非「look up APIs」；
   - 输出要求：**verdict + issue list**，简洁、可执行。

3. **⚠️ A1 在跑的 3 轮怎么办**：
   - 若 **r1/r2 已跑完、r3 未起** ⇒ 按**新提示**跑 r3，并在 MEMORY 标注 **r1/r2 用旧提示、r3 用新提示，不可混算**；
   - 若 3 轮都已跑完 ⇒ **新提示另起一轮完整 3 轮**（A1'），旧 3 轮保留为「旧提示口径」历史数据，**不删**；
   - 具体采用哪种，按实际进度自行判断并在 MEMORY 写明。

**四、与 H1 结论的关系（重要）**

- 这一改动使 A1 从「**spawn 调研 agent + 强提示**」变为「**spawn 验证 agent + 对抗提示**」，
  与 A0 的差异**仍然是"是否 spawn"**，但**提示内容变了** ⇒ **新旧 A1 结果不可混算**，必须分组统计。
- 最终报告需**分别报告**：
  - A1-旧提示（调研型 spawn）的 Pass@1；
  - A1-新提示（验证型 spawn）的 Pass@1；
  - 与 A0 的配对比较（McNemar）。
- **额外分析（很有价值）**：统计「**主 agent 采纳了验证 agent 意见的题** vs **未采纳的题**」的通过率差异，看对抗审查是否真的有用。

**五、纪律**

- 🚫 不要为了"提高 spawn 率"而把提示写得更强硬重；用户要的是**有意义**的 spawn，不是**多**的 spawn。
- ✅ 改动后先 **smoke 1 题**，确认：主 agent 先写代码 → 再 spawn → 子 agent 给出 verdict —— trace 里要有这三段。
- ✅ 记 MEMORY：新旧提示的差异、r1/r2/r3 各用什么提示。

---

### 🔴 用户令 · 2026-11-14 17:0x（**H3 不做；H2 恢复 —— 允许改 cline 源码重编译，让自主 spawn 的子 agent 用弱模型**）· 未完成 · 最高优先

> **用户原话**：
> 「H3 不做
> H2 可以做，需要改 cline 代码重新编译安装也没问题，只要向后兼容即可。
> H2 只做自主 spawnagent 这条线，不做 custom。要求修改代码，在 spawnagent 时，通过配置让 agent 用弱模型。」

**一、裁决变更（覆盖 wake#926 的 H1-only 决定）**

| 假设 | 原裁决 | **新裁决** |
|:--|:--|:--|
| **H3**（maxIterations 5/15/30） | ❌ 不可行 | **❌ 不做**（用户明确：H3 不做） |
| **H2**（子 agent 弱基座梯度） | ❌ 不可行 | **✅ 要做** —— 允许改 cline 源码、重新编译安装，**只要向后兼容** |
| **H1**（spawn on/off） | ✅ 可检验 | ✅ 继续（A1 的 P2 继续跑完） |

**二、H2 的实现路线（用户已指定，不要跑偏）**

- **只做「自主 spawn_agent」这条线**：主 agent 调用 `spawn_agent` 工具时，**通过配置**让被 spawn 的子 agent 使用**弱模型**。
- **🚫 不做 configured agent（custom）路线** —— 不要再走 `researcher.yaml` / `subagent_researcher` 那条路，那条已证实 3.0.51 不通。

**三、技术任务（改源码）**

你 wake#926 已经用 `strings` 反查出关键代码：

```js
eu({kind:"subagent", prompt: i.systemPrompt,
    configProvider: e.configProvider,     // ← 子模型 = 父的
    tools: e.subAgentTools,               // ← 子工具 = 父的
    maxIterations: e.defaultMaxIterations})
```

**要做的事**：
1. 在源码仓库 `/nasdata/app.e0031982/code/cline/sdk/packages/core/src/extensions/tools/team/` 里，
   给 **`spawn_agent`**（`spawn-agent-tool.ts`）**增加一个可选配置项**，让子 agent 的 `configProvider`（模型）可被覆盖；
2. **配置来源**：环境变量、cline settings、或 spawn_agent 的 input schema 新增可选字段——**方式你定**，但必须：
   - **向后兼容**：默认行为**完全不变**（不配置时子 agent 仍继承父模型），保证 A0/A1 现有结果与 compaction 等历史实验不受影响；
   - 不破坏 `tools` / `maxIterations` 的现有继承逻辑（H3 不做，别动）。
3. 🔴 **必须一并修复：子 agent 的工具限制（用户 2026-11-14 18:0x 明确要求）**

   > **用户原话**：「search_apis 报 NoSuchToolError 说明原来的实现有问题，限制了子 agent 使用的工具。这个问题这次要一起修复。」
   > **用户给定的目标行为**：「**子 agent 默认继承所有工具，唯二的差别在于 LLM + 上下文。**」

   - **正确设计 = 子 agent 继承主 agent 的完整工具集**，与主 agent 的差别**只有两个**：① 用哪个 LLM ② 上下文（systemPrompt / task）。
   - 你在 wake#926/#927 记录到「子 agent 调用 `search_apis` → `AI_NoSuchToolError`，回退 `search_codebase`」——
     **这说明当前实现在 `tools: e.subAgentTools` 处对子 agent 做了工具限制，是 bug，本次一并修掉。**
   - 修法：让 `spawn_agent` 派生子 agent 时传**父 agent 的完整工具集**（含 MCP 工具），而不是受限子集。
   - ⚠️ 顺带核实 `NoSuchToolError` 的**直接成因**：是工具名不匹配（子 agent 用了裸名 `search_apis`，而 MCP 工具在父侧的完整名是 `pyAether_MCP_server__search_apis`），还是工具确实没注入。**两种情况都要修到"子 agent 能正常调用 MCP 工具"为止**，并在 smoke 里给证据（子 agent 成功调用一次 MCP 工具的 trace 原文）。
   - **向后兼容**：此项修复同样不得改变主 agent 的工具集与默认行为。

**四、验证与执行顺序**

1. **编译安装**：在 36.15 完成 build，`cline --version` 可用。
2. **向后兼容自检**（必做）：
   - 不配置任何新选项时，跑 1 题，确认子 agent 仍继承父模型、行为与改动前一致；
   - 现有 A1 P2 若在跑，**不要打断**（另装一份或用独立 data-dir 做 smoke，避免影响在跑实验）。
3. **确认性 smoke**：配一个弱模型，跑 1 题，确认**子 session 的 messages.json 里模型名 = 弱模型**（用你 wake#926 那套 `n_msgs` + 模型核验方法，给证据）。
4. **H2 实验**：确认 smoke 通过后，按计划书恢复 **B2（dsv4-flash）/ B3（doubao-pro）/ B4（doubao-mini）/ B5（doubao-lite）** 四臂（B1 same 作为梯度最强端，若已有数据可复用）。
   - 更新 `providerId` 修正（你 wake#922 已查明应为 `openai-compatible` + doubao model/key）。

**五、纪律**

- 🚫 **向后兼容是硬要求**：默认行为不得改变；改完要给「改动前后默认路径行为一致」的证据。
- 🚫 不改评测题集/判据/超时。
- ✅ 源码改动要有 commit 记录与 diff 摘要，写进 MEMORY。
- 若某步确实做不成，写 `BLOCKED + 具体卡点 + 需要什么`，🚫 不许又一次直接裁掉。

---

### 🔴 用户令 · 2026-11-13 21:2x（**启动 subagent 消融**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「启动 subagent 消融」

**执行口径**：严格按已交付计划书 `reports/plan_zhulong_subagent_ablation_zh.html`（P0 已于 2026-11-13 17:20 PASS）。全臂恒定：`--compaction basic`、`CLINE_THINKING=medium`、`LANG_HINT` 空、`-p 8 -n`、主基座 `deepseek-v4-pro-cloud`；**A0 直接复用 compaction basic r1–r3**（不重跑），A0 的 158 题复用轴 A medium。

**① 起跑前复核（10 分钟，任一不过先修再跑）**
- `researcher.yaml`（**必须 .yaml，不是 .md**）在 `.cline/agents/`；tools 用完整 MCP 名 `pyAether_MCP_server__search_apis / __get_api_details`；工具列表里能看到 `subagent_researcher`（P0 时为第 19 号工具）
- doubao pro/mini/lite 三 key 连通（P0 已 curl OK，重测 1 次）
- 沙盒 8664/8665/8653/8669 全 FREE + `pgrep -f '^bash scripts/run_cline_script'` 无输出；harness TB-2.1 rerun 在跑（Docker/gateway），若争用则排队并写心跳
- **磁盘**：/home 99%（6.6G）先 `df`；`EVAL_ROOT_DIR=/tmp/zhulong_subagent_eval` 每轮清理；trace 落 `/nasdata/.../trace_ablation_subagent/`，`/nasdata` 若满改落 /tmp 并按轮归档；可用 <5G 先清再跑

**② P1 pilot（现在起跑：8 臂 × 8 题 × 1 轮，~1.5h）**

```bash
head -8 run/compaction_subset_40.txt > run/subagent_pilot8.txt
SUBSET_FILE=$PWD/run/subagent_pilot8.txt ROUNDS=1 nohup setsid bash run/run_subagent_ablation.sh > /tmp/subagent_pilot_master.log 2>&1 &
```

- 产出：每臂 subagent 调用率 / doubao 三臂连通 / 每臂 Pass@1 / 墙钟
- **go/no-go（预注册）**：调用率 `<20%` 且强提示后仍 `<30%` ⇒ **判无效**，停 P2，直接出负结果报告；否则进 P2。单轮不得解释为结论。

**③ P2 主实验（P1 go 后自动进：9 臂 × 40 题 × 3 轮 ≈16h）**
- 串行；每轮前 quota probe；429 等待不降并发；每轮落 `cost_S_<arm>_r<n>.json` + `ablation_subagent_results.json` 条目 + trace 归档
- **起跑前必须补的工程缺口**：现 `run_subagent_ablation.sh` 的 cost 收集是 TODO 空壳（只写 arm/round/batch）⇒ 必须先实现：从 trace/session 采 `SpawnAgentOutput.usage.{inputTokens,outputTokens}`、spawn 次数与完成率（`finishReason=completed`）、主/子消息数、wall_sec；否则 H2/H3 无法判

**④ P3 全量（P2 完成后：4 臂 A0/B1/B3/B5 × 158 题 × 1 轮 ≈10h）+ P4 报告（2h）**
- 报告：`reports/report_zhulong_subagent_ablation_zh.html`（新文件=里程碑，中文/自包含/**0 外链**）：摘要 / 机制与 P0 修正 / 主结果表+逐题配对 / 调用率 / 基座梯度曲线 / 成本-性能（主 vs 子 token 分拆）/ 亚组 / 失败分类 / 结论与默认策略

**判据（预注册，不许事后改）**：主终点 = 3 轮 Pass@1 均值（ITT）；**H1** A0 vs A1/B1 McNemar discordant ≥6:6 且方向一致；**H2** B1 vs B2–B5 Δ≥3pp 且 bootstrap CI 不跨 0、梯度回归 R²>0.7、B5 per-pass token 降 ≥20%；**H3** 完成率差 ≥10pp ⇒ maxIter=5 过紧。差异 <3pp 一律写「证据不足」。
**纪律**：🚫 不改 benchmark/评分器；🚫 不删旧结果与 trace；🚫 不 kill 编排器/loop；🚫 不把 proxy/reward 当能力（真实裁判=Pass@1）。zhulong 与 designflow 使用**互不相干的沙盒**（本线 = `run_code` 端口 8664/8665/8653/8669；designflow = `eda_flow` MCP → `.75` 远端 `run_commands`），**不存在资源争用**，无需互斥。
**心跳**：每轮写 臂/轮/PID/etime/log 大小/batch/已评题数/调用率；跑中 WAITING=1；P2+P3 完 + 报告 + commit（`zhulong subagent:`）后 done_all。
**体积**：本任务书 52.7KB（>40KB 硬上限）⇒ 本轮**同时**把已闭合旧令原文搬去 `run/ARCHIVE_ZHULONG_TASK.md` 留 1 行指针，归档后 ≤32KB。

---


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
