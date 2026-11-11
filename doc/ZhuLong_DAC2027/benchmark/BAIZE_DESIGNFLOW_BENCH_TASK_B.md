# BAIZE_DESIGNFLOW_BENCH_TASK.md — 设计流 Benchmark 任务书（2026-10-30 重构版）

> 💬 **2026-11-11 用户令：0-case 时进讨论区**（`benchmark/designflow/discuss/`）
>
> 用户原话：「各线designflow在没有case可做时，阅读论文，在这个文件中阅读他人的看法，发表自己的意见。」
>
> **触发**：① 本轮 0 case（已贴 `mc-matrix` 且 `mc10.fresh==0`）② `board.md` 有 OPEN 议题点 @B。有 case 则造题优先。
>
> **4 步**：① **读** `board.md` + 其他 3 个 shard 的 `.md`（尤其 `回应 @B`）+ `rounds/` 最新 + 论文 section
> ② **想**：用 **spice_sim / characterization** 域视角给独有判断
> ③ **写**：**append 到 `discuss/B.md`**（格式照 `discuss/README.md §3`）
> ④ **提交**：`git add benchmark/designflow/discuss/B.md`
>
> 🚫 禁改 `README.md` / `board.md` / 其他 shard 的 `.md`；🚫 `git add -A`
> - 召集人 = **shard A**（`board.md` 只由 A 写，你只读）。
> 🚫 「我同意」「+1」不算发言；必须表态明确 + 给本域依据（case id / 实测数字 / 论文 section+行号）。
> 讨论产出是**建议**不是结论。论文 `EDA-LiveFlow-Bench_ICML2027/` 全目录只读。



> 🟢 **2026-11-11 用户令（最高优先 · 本轮唯一任务）：B 线 0-case 时改做「论文改进建议」**
>
> **用户原话**：「既然 designflow-B 没有 case 了，那让它看下论文 EDA-LiveFlow-Bench_ICML2027，提出改进建议（中文HTML，设想自己是研究组的一员，思考下一步做什么，怎么做）。」
>
> ### 触发条件（满足即执行本条，替代当轮造题）
> 当本轮**已经**做完 `mc-matrix` 取证且 `mc10.fresh == 0`（或 fresh 全部 peek 后无 CLEAN）⇒ **不要空转收尾，直接做本条**。
> 若本轮仍有可用 case ⇒ 先造 case，本条留到 0-case 轮再做。
>
> ### 论文位置（只读，🚫 不许修改论文任何文件）
> `doc/ZhuLong_DAC2027/EDA-LiveFlow-Bench_ICML2027/`
> - 正文：`main.tex` + `sections/0_abstract.tex` … `sections/9_reproducibility.tex`（10 个 section 文件）
> - 附录：`appendix/`
> - 当前事实源：`\Ntasks` = **1032**（A203+B242+C289+D298）；冻结评测 **696 runs**（2026-11-09）；**Pass@1 = 10.0%（62/620 已判定，ERROR 70 不计分母）**
>
> ### 你的视角（关键 · 决定这份报告有没有价值）
> **设想你是这个研究组的一员**，不是审稿人、不是打分员。要回答的是：
> - **下一步做什么**（该补哪个实验、该改哪个口径、该扩哪个域）
> - **怎么做**（具体到数据集/脚本/配置/预算，能直接派活）
>
> ### 必须回答的 6 个问题
> 1. **我们最薄弱的论证环节是哪个？** 论文现在最容易被 ICML 审稿人打穿的地方（举出具体 section + 原句）。
> 2. **10.0% 这个数字站得住吗？** 620 的分母、70 个 ERROR 的处置、单 backbone、单 thinking level —— 哪些需要补对照组？
> 3. **B 线视角的独特输入**：你是 spice_sim / characterization 域，这两域在论文里的表现如何？域内案例质量、断言强度、判分口径有没有问题（结合你自己造的 case 经验）。
> 4. **下一步该补什么实验**（按性价比排序，至少 3 条）：每条写清 *目的 / 方法 / 数据 / 预计工作量 / 预期能回答什么质疑*。
> 5. **benchmark 本身该怎么演进**：1032 个 case 的分布是否合理？13 个域有没有偏科？要不要加新域（如 AI 辅助 layout、PDK QA）？
> 6. **如果只有两周，你先做哪三件事？**（必须排序并说明为什么是这个顺序）
>
> ### 报告要求
> **产出**：`reports/report_designflow_paper_next_steps_zh.html`
> - **中文 · 单文件自包含**（内联 CSS · 零外链/CDN · 离线双击可开）
> - 结构建议：① 一句话结论 ② 论文现状速览（关键数字表）③ 六个问题的回答 ④ **行动清单**（表格：优先级 / 事项 / 负责人角色 / 工时 / 依赖）⑤ 风险与反对意见（预判审稿人会怎么反驳，我们怎么答）
> - **引用论文原句时必须给 section + 行号或原句**，不许转述成自己的话
> - 🚫 **不许改论文**（`EDA-LiveFlow-Bench_ICML2027/` 下任何文件都只读）；🚫 不许提「已验证」的结论，未做的写「建议验证」
>
> ### 与既有令的关系
> - 本条**不解除**顶部 mc≥10 令与「禁止无证据说池枯竭」令——做本条前仍须贴 `mc-matrix` 证据。
> - 本条**不涉及** `eval_triage/`（那是 shard A 独占），若你要引用归因结果，直接读 A 已产出的即可，🚫 不要自己重跑。

> 🔴 **2026-11-11 用户令（最高优先 · 覆盖所有旧 mc / 候选池口径令）：**
> ### ① 候选池快照 11/05 → **11/09**；② mc 阈值 **全线 30 → 10**（mc≥10，坚决执行）
>
> **用户原话**：「1.候选池替换: 11/5 -> 11/9；2.mc阈值降低到10(mc>=10)」「把mc>=10 这条规则坚决执行下去」。
>
> **换池由 shard A 独家执行**（A1–A6 见 A 任务书顶部；会改 `summary_stats.json` 与 `candidates_mc10.tsv`）。
> **你线不要自己换池**（4 个 agent 抢同一个 `summary_stats.json` 会互相覆盖）。判据：`summary_stats.json.mc_matrix.src` 变成 `designflow/summary_1109.tsv` 即视为已换池。
>
> **本 shard 每轮必须遵守（mc≥10 强制执行条款）：**
> 1. **选料阈值固定 mc≥10**：`awk '$5+0>=10'`。**禁止**出现 `>=30` / `>=15` / `min-mc 30` 作为选料阈值。
> 2. **候选清单只用 `candidates_mc10.tsv`**，`candidates_mc30.tsv` **冻结停用**（仅作历史）；按本 shard 过滤重出：`python3 designflow/trace_ledger.py --shard B mc-matrix --src <mc_matrix.src> --emit-candidates --emit-candidates-mc 10`。
> 3. **`refresh` 时 `target_mc` 必须写 10、`shard_mc` 必须 `{"A":10,"B":10,"C":10,"D":10}`**，禁止写回 15/30。
> 4. **禁止在无证据时写「池枯竭 / 池耗尽 / 0-case 证据链」收尾**：必须先贴 `python3 designflow/trace_ledger.py --shard B mc-matrix --src <mc_matrix.src>` 输出，且仅当 `mc10.fresh == 0` 才可下此结论。你线此前多轮 0-case 都是在 mc≥30 口径下判定的，mc≥10 下**尚未验证**。
> 5. **覆盖率一律按 `target_mc=10` 报数**，并注明快照来源（`mc_matrix.src`）；不得再用 `mc30=2247` 当分母。
> 6. 本条令**优先于**本任务书内一切旧的 mc 阈值描述（含历史用户令、背景说明、示例命令）。
>
> **B 线实测（11/05 快照，shard B keywords 过滤后 565 session；11/09 换池后由 A 重算）**：
>
> | 阈值 | 池总量 | 已动过 | 未动过（可做） |
> |:--|--:|--:|--:|
> | mc≥30（旧） | 376 | 371 | **5** |
> | mc≥15 | 448 | 421 | 27 |
> | **mc≥10（新）** | **486** | **447** | **39** |
>
> ⇒ B 线从 5 个可做涨到 **39 个（约 8 倍）**，"spice 池 98%+ ledgered" 的结论只在 mc≥30 成立。

> 🚫 **2026-11-10 用户令：696-run 评测归因（`eval_triage/`）由 shard A 独占执行。**
> B/C/D **不要**跑 `designflow/eval_triage/05_batch_triage.py`、**不要**改论文
> `sections/5_analysis.tex` 或 `appendix/B_additional_results.tex`（4 个 agent 抢同一批文件会互相覆盖）。
> 继续按本任务书正常造题；若 shard A 在 MEMORY 里报了归因结果，直接采信、不重复跑。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow（含本 benchmark 的造题/保真度/判分）。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「designflow 建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 🚨 2026-11-05 19:2x 运维令：**「池枯竭」结论作废 · 自行经 `.75` 的 `run_commands` 重扫 698 机刷新 trace 源** · 用户直令 · 最高优先

> 用户原话（2026-11-05 19:1x）：「让 designflow B 自己通过 .75 的 run_commands 去刷新 trace 来源，这几天肯定又有新的trace写入 698 台机器了。」

**① 裁定**：18:4x–18:54 的「shard B spice_char real trace 池枯竭」结论**作废**——它只基于 **10-28 的旧快照**（`.75:/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv`），不代表现状。🚫 不许再以「pool exhausted」结案、也不许靠它维持 `WAITING: 1`。

**② 本轮必做（同一轮内做完，不许只交计划）**
1. 经 `eda_flow` MCP（`http://127.0.0.1:18891/mcp`）调 **`.75`（`hfhds201` / `10.129.32.75`）的 `run_commands`**，**重扫 698 台机的 cline trace 目录**，产出**新快照**（如 `/home/t0002965/log/ssh_eda_search_20261105_HHMMSS/` + `summary.tsv`，列同旧表 `ip host user session_file match_count keywords tools`）。沿用旧口径：分批 5–10 台/次防超时；只读 `find`/`ls`/`cat`/`head -c`/`grep`/`awk`/`python3`。
2. **优先时间窗 ≥ 2026-10-28** 的 session 文件（新写入优先）；旧 84 条保留作历史，**新增命中单列**。
3. 用 spice 主导过滤重建候选（spice 工具计数 / 总工具计数 ≥35% 且 spice≥10），产出：扫描台数 / 命中 session 数 / 新增 proper 条数 / 候选清单（`user·host·session_file·match_count`），落 `designflow/` 并 commit。
4. **立刻用新候选交付 1 条 case**（A 档 trace-faithful，`metadata.trace_source` 必填，k≥8 断言，判分器不入 workdir），走既有 casemaking 流程。
5. 只有**确实 0 新增**（须给证据链：扫描命令 + 时间窗 + 遍历台数 + 命中数 + 与旧 `summary.tsv` 的 diff）才允许报「本轮无可做 case」并置 `WAITING: 1`；否则 **`WAITING: 0`** 继续往下做。

**③ 判据**：本轮结束必须给出 ① 新 `summary.tsv` 路径 + 行数 ② 旧 vs 新 diff（新增 session / 新增 proper）③ 至少 1 条新候选的 case 交付（或 0 新增的完整证据链）。

**④ 纪律**：对 698 机**只读**（🚫 写/删/`tee`/`>`）；分批扫描防超时；不碰 A/C/D shard；commit `designflow shard B #…`；心跳写 `未完成指令：有` ⇒ `WAITING: 0`。

**⑤ 体积（先做，别拖）**：`MEMORY_DESIGNFLOW_B.md` 现 **40,413B，已越 40KB 红线**（规则 §1.6：≤32KB / 红线 40KB）⇒ 本轮**先把已闭合流水原文滚进 `ARCHIVE_OPERATOR_DESIGNFLOW.md`**（保留状态头 + 最近 ≥20 条流水 + 1 行指针），压到 **≤32KB** 后再开工；TASK 28.6KB 尚在软限内。

### 📦 归档指针 · 2026-11-02「被测换 cline + PreToolUse 防泄题 hook」· 现行口径：被测 = cline（`--auto-approve true --json`）；cline + PreToolUse hook ⇒ agent 只能看 workspace 内文件，判分器在 workspace 外独立跑，消除泄题。原文见 `ARCHIVE_OPERATOR_DESIGNFLOW_B.md`「归档块 · 2026-11-11」

### 🚨 2026-10-31 21:5x 运维令：`test 思路` 必须是「k 条断言」（**硬闸门 + 打回重写**）· 用户直令 · 最高优先

> **背景**：§4.6 昨天已要求 `k 条断言：①…`，但 10_31 日报 **30 条 case 里 0 条达标**（全文“断言”出现 0 次，全部仍是散文式，如「解 zip 校验 5 文件…」）。原因不是理解偏差，是**没有闸门**。本轮起改成硬闸门。

**规则（每条 case、每一轮都必须过）**
1. **写**：`metadata.test_rationale` 必须**以 `k 条断言：` 开头**，后接 ①②③…，**与 `check()` 中可独立失败的条件一一对应**，每条写「对象 + 判定」。🚫 散文 / 🚫 实现细节（`raise`、`zipfile`）/ 🚫 「校验交付件完整性」式废话。
2. **对账（落 jsonl 之前）**：agent 必须**先把 `check.py` 的条件标签列出来**（a–n，或 `CONDITIONS = [("a","…"), …]` 表），数出 `k_check`；判据 **`k_rationale == k_check` 且 `k_check ≥ 8`**。
3. **不过就滚回去改**：`k_rationale ≠ k_check` 或 `k_check < 8` ⇒ 该 case 标 **`incomplete`**：🚫 不许 `mark --status case`、🚫 不许追加进 jsonl、🚫 不计入通过率；写入 `designflow/rewrite_queue.tsv`，**下一轮第一件事就是修它**，修完才准开新 case。
4. **日报必须自证**：`gen_daily_report.py` 的 case 表**新增三列** `k(断言)` / `k(check)` / `一致`；任一 case 显示 `✗` 或 `—` ⇒ 当日日报判「未交付」，心跳写 `DEBT:<n>`。
5. **存量 30 条**：按 §4.6 全部视为未完成；每轮从 `rewrite_queue.tsv` **修 1 条**，直到清零，心跳写 `断言清单 x/30`。
6. **心跳新增一行**：`🧾 断言: k_rationale=k_check=n ✓/✗（今日 x/30 达标）`。

> 📦 体积：本令约 1.5KB；TASK 现 17KB，远低于 40KB 红线。


### 🚨 2026-10-31 21:3x 运维令：A/B 双档 casemaking（trace-faithful 试点 10 条）· 用户直令 · 最高优先

> **用户原话**：「如果只把真实 trace 中用户的意图作为任务说明，不妄做修改，是否难度就可以提升、通过率下降？」→「好的试试看」
> **判断（运维）**：当前通过率偏高，主因不是模型强，而是**合成的 `task_brief.md` 替模型把题读懂了**——交付形态、资产用途、验收点全写明，难度被稀释。本轮起引入 **A 档（trace-faithful）**。

#### ① A 档（本轮试点 10 条，唯一硬交付）
1. **任务说明 = 该轮用户原话逐字原文**：按红线 #2 **不脱敏、不改写、不补全**（仅 key/token/密码掩码）。🚫 不许把口语改写成规整需求。
2. **选轮规则（关键）**：只取「**提出需求 / 表达目标**」的用户轮；🚫 **凡用户已指出根因或给出修复方案的轮，一律不得用作 A 档任务说明**（可另存为 hint，不进 prompt）。
3. **接口固定 ≠ 改意图**：契约照旧 —— `mode:design_flow` + `entry_point=outputs/submit.zip` + `test=check(deliverable, workdir)` 双参；`task_brief.md` **只写「交付接口与文件位置」≤3 行，不写「要做什么」**。
4. **金标准** = trace 末尾**用户实际接受的结果**（工具真实产物），人工复核一次；断言只对事实（数值容差 / 拓扑等价 / 产物确由工具生成），🚫 不对措辞、不许拿合成 brief 反推答案。
5. **隐藏 B 照旧**（换输入 / 反转结构 / 多 seed），防硬编码与猜答案。
6. **资产用该轮真实 attachments**（原文），不加说明性注解。

#### ② B 档（synthesized）= 现有做法
保留作 L1 补牙 / 教学 / 消融。**A、B 两档通过率分开报，🚫 混算**（这同时修掉「最近 20 条混算 L1+L2」的口径缺陷）。

#### ③ 试点与判据
- 先做 **10 条 A 档**，优先覆盖 **L2 真跑商业工具**的域（spice_sim / physical_verify / schematic_netlist / layout_*）。
- 每条用同一口径跑 pi（`pi 1.4.0` / `deepseek-v4-pro-cloud` / `--thinking medium`），记录 pass/fail + **失败归因四类**：①交付形态/位置错 ②前提缺失（需澄清/需上一轮状态）③能力不足 ④判分歧义。
- **判据**：A 档通过率 **≤10%**，且「①+④」类失败占比 **≤30%**（否则先修接口与判分，不许把格式失败当难度）。
- 交付：10 条追加进同一 jsonl（加 `metadata.track: "faithful"`；🚫 不新建 jsonl）；日报加「A/B 分档通过率」两行；中文 HTML 报告落 `doc/ZhuLong_DAC2027/reports/`。

#### ④ 口径调整（覆盖 §0 的单一目标）
- B 档：通过率目标 **20–30% 不变**；
- A 档：**本轮不设目标、只报数**，试点后用实测定档；
- 任何对外数字必须标档位（A / B），🚫 用 B 档数字代表真实难度。

> 📦 体积：本令约 1.7KB，TASK 已超 40KB 红线（agent 只读）；运维下轮归档已闭合块。



> **本文件由运维维护（agent 只读）**。运行时状态写 `MEMORY_DESIGNFLOW.md`、`EXPERIMENTS_DESIGNFLOW.md`、`daily-memories-designflow/`。
> 旧版全文（即时令 VII/VIII/IX/X/XI/XII、运维增补 I–IV、收尾铁律、体积规程）已**原文归档** → `ARCHIVE_OPERATOR_DESIGNFLOW.md`「归档批次 48」。本版把上述指令**按主题融合**，不再按时间堆叠。

## 0. 目标（一句话）

用 `.75` 内网 **698 台机 / 2,850 用户 / 52,698 会话（24,085 条 IC-EDA 命中）** 的真实 cline 轨迹，构建「设计流编排」评测集；**难度必须校准到 pi-SUT 通过率 20–30%**——不是"能跑通就算过"。

## 1. 红线（不可协商）

1. **真实 trace 才有资格**：每条 case 必带 `metadata.trace_source{user, host, session_file, match_count, real_task_summary}`。没有真实 trace 的 case 一律删除，🚫 不许改个名字保留。
2. **不脱敏（全产物）**：`user` / `host` / `session_file` / `/home/<user>` 路径 / `prompt` / `attachments` / 深读笔记 / 日报 / MEMORY **一律保留原值**；只有 **key / token / 密码** 需掩码。🚫 prompt 里出现"脱敏""不要出现真实用户名"字样视为违规。
3. **单一 jsonl**：只往 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl` 追加；🚫 新建 jsonl（>500 条才按 `metadata.domain` 拆 4 个）。
4. **只读纪律**：对 698 机只 `find`/`ls`/`cat`/`head -c`/`awk`/`python3` 只读；🚫 写目标机、🚫 `rm`/`tee`/`>`；🚫 本机自扫；🚫 lineage 自审计 / §X 递归。
5. **git 双仓**：workspace + 日报 → `super_intelligence_2035` **main**；用例产物 → `EDA-Flow-Bench` **master**；🚫 `git add -A`。
6. **体积**：本 TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限按 §8 归档（原文搬 ARCHIVE，留 1 行指针）。

## 2. 环境速查

| 项 | 值 |
|:--|:--|
| workspace | `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/` |
| 用例仓库 | `/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`（jsonl / assets / reference） |
| 历史快照 | `EDA-Flow-Bench/agent_workspace/designflow/`（bench_v0.1~v0.50，只读，不迁） |
| 运行时 cwd | `/nasdata/app.e0031982/code/EDA-Flow-Bench/` |
| 沙盒入口 | `eda_flow` MCP `http://127.0.0.1:18891/mcp` → `.75`（`hfhds201` / `10.129.32.75`）`run_commands`·`run_code`·`read_file`·`write_file` |
| 扫描结果 | `.75:/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv`（列：`ip host user session_file match_count keywords tools`） |
| 评测框架 | `./RUN_EVAL.sh --design-flow` / `--design-flow-agent`；`scripts/run_design_flow_batch.py`；`config.yaml`；`docs/design_flow_session_backend.md`（§3 接口 / §9 判分两步）；`docs/设计流Benchmark-{测试用例编写指南,框架改进设计文档}.html` |
| pi（被测） | `pi` 1.4.0，provider `cxmt` / `deepseek-v4-pro-cloud`，已配 `eda_flow` MCP。调用：`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "<prompt>"`（Node 22 需在 PATH：`export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH`） |
| 日报 | `cd <benchmark>/designflow && python3 gen_daily_report.py` → `doc/ZhuLong_DAC2027/reports/report_benchmark_MM_DD.html`（运维已加独立「用户」列，**别再重复改**） |

**命令模板（只读抓 trace）**
```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "head -c 4000 /home/<user>/.cline/data/sessions/<session_file>"
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "ls /home/*/.cline/data/sessions/*.messages.json | head -20"
```
> `.75` 已对 **697/698** 台免密（`e0031982` 身份）。**分批 5–10 台/次**，别一次扫 698 台（会超时）。

**三个已知坑（别再踩）**
1. **GitHub 假阴性**：`curl https://github.com` 在剥掉 proxy 的环境里返回 `000`，但 `git push` 走 `git config --global http.proxy` 仍可通。**判据用 `git ls-remote origin HEAD`，不要用 curl**。（确需代理：`git config --global http.proxy http://172.19.92.23:13128`）
2. **`write_file(content_base64=...)` 会腐蚀内容**（`$dA` → `$d\x01`）：一律用 plain `content` 字符串，或 `run_commands` 里 `base64 -d` 在本机解码。
3. **`ssh` 在 eda_flow 里会 hang**：命令前加 `</dev/null`（`-n` 反而会断 stdin pipe）。

## 3. 用例契约（proper `design_flow`）

```text
mode:        "design_flow"
entry_point: "outputs/submit.zip"
test:        "def check(deliverable, workdir): ..."   # 双参，返回通过 / 抛异常失败
prompt:      自然语言，写真实场景（真实用户名/路径/工具/指标），不是函数签名题
attachments: [assets/<task_id>/...]                    # 真实输入文件
metadata:    { trace_source{...}, domain, test_rationale }
```
🚫 不带 `lang` / `host` / `runtime`；🚫 不写"实现 `xxx(args)->dict`"这类抽象题。

**单轮闭环 + 交付定义（DoD）**

一轮 = 一条 case 从选料到落库，**不要拆成两轮**：
`选料 → 深读 → 合成 → 自验(ref PASS + §4.9 三假提交 FAIL) → 追加 jsonl → 日报一行`

- **深读是硬闸门，但不是独立的一轮**：必须先解析完整对话流（`scp` `messages.json` → user 意图 / assistant 工具链 / 关键产物 → `designflow/trace_deepreads/<sid>_<主题>.md`）才允许合成；已有笔记可直接复用，不重复深读。
- **DoD（交付定义）**：1 条 case 通过自验并写进 `EDA-Eval-DesignFlow.jsonl` 才算交付；**深读笔记是中间产物，不算交付**。
- **每轮只做 1 条 case**：做完即收尾，**不在同一轮开第二条**（控制上下文不膨胀）；交付后首行 `WAITING: 0`，loop 60s 后唤醒做下一条。
- **唯一例外**：单条 trace 过大（>2MB 或 >600 msgs）允许本轮只深读，但**下一轮必须先交付 case**，心跳记 `DEBT: 1 deepread 未合成`；🚫 禁止连续两轮只深读。
- **选 trace 一律走台账（唯一去重口径）**：`python3 designflow/trace_ledger.py next --n 5` → 按它给出的 awk 在 `.75` 上取候选（**已自动排除台账里的 session**）→ 选第一条 → `claim` 落台账。
  - 出完 case：`mark --session <s> --status case --case-id <EDA-Eval-DesignFlow-XXX>`（覆盖率的唯一分子）；
  - 暂缓：`mark --session <s> --status parked --note "<原因>"`（如 aether 超时），**不重复捡**。
  - 🚫 禁止凭记忆/凭 jsonl 目测选 trace；🚫 禁止跳过 claim 直接开工（去重与进度都会失真）。
- 选料偏好：`match_count` 高 + **该 domain 尚无 case**（domain 覆盖优先于纯命中数）。

## 4. 判分质量（"有牙"，缺一不可）

1. **隐藏输入 B**：A 给 SUT 看，B 放 `assets/<id>/hidden/` + `hidden_manifest.json`，**不进 SUT 沙箱**；`check()` **只跑 B**，B 与 A 在规模/取值/结构上必须不同（不是换文件名）。
2. **真跑候选**：≥1 个条件用 `subprocess` 在 B 上执行候选脚本，断言**输出结构**（解析成字段/拓扑/计数再比较），不是文本相似。
3. **≥8 个独立条件**，每个单独可 FAIL；🚫 "仅成员名 / 仅子串出现"式断言。
4. **负样本入库**：`reference/<id>/negative/` ≥2 个错解（naive / always-XXX stub）+ `negative_selftest.py`，一次跑完必须**全 FAIL**；每轮抽查 1 条重跑。
5. **随机化**：在 B 上随机抽子集（net / signal / 行），3 个随机种子跑 3 次结论一致；🚫 把期望值硬编码成固定串。
6. **`metadata.test_rationale` = 逐条断言清单（不是摘要）**：格式固定 `k 条断言：①<验什么> ②<验什么> …`，**一条对应 `check()` 里一个可独立失败的条件**，写清"对象 + 判定"。
   - ✅ `7 条断言：① zip 内 5 个文件齐全 ② mac4.v 有 module mac4 且端口 clk/rst_n/acc0 齐全 ③ 累加为 32-bit 有符号饱和（边界 0x7fffffff/0x80000000） ④ sim_mac4.log 含 MAC4_SIM_PASS 且无 MAC4_SIM_FAIL ⑤ …`
   - 🚫 废话：`解 zip 校验 3 文件`、`校验交付件完整性`、`断言内容达标`
   - 🚫 实现细节：`raise AssertionError(...)`、`zipfile.ZipFile(...)`、`z.read(...).decode(...)`
   - 自检：`k` 必须等于 §4.3 要求的独立条件数（≥8）；两者对不上 = 未完成。⇒ 按顶部令 21:5x 执行：标 `incomplete`、进 `designflow/rewrite_queue.tsv`、🚫 不许落 jsonl、🚫 不许计入通过率。
7. `check()` 在**独立临时目录**解 zip；🚫 在 SUT workdir 留 `__chk`。
8. **泄漏隔离**：SUT 沙箱不得包含 `benchmarks/EDA-Eval-DesignFlow/`（`reference/`、jsonl、`test` 字段）；结论写 MEMORY 一行。
9. **退化提交回归**：每条 case 必须让 (a) 空壳 (b) 只 print 期望串 (c) 参考解删核心 三种假提交**全部 FAIL**；任一 PASS ⇒ 该 case 判分不合格，限期整改或下线。

## 5. 难度校准（立即生效）

| 层 | 定义 | 配额 |
|:--|:--|--:|
| L1 | 离线 Python 复刻（读附件写脚本） | **≤30%** |
| L2 | 真跑沙盒工具（calibre LVS/DRC、Virtuoso、PrimeTime、VCS，经 eda_flow / .75） | **≥50%** |
| L3 | 多工具链路 + 修复 + 回归（DRC 179→0、LVS 干净 CORRECT、ERC 全清） | **≥20%** |

- 新建 case **只做 L2 / L3**；L1 仅用于补牙维护。
- 总样本 **<30 条前不报通过率**，只写"已跑 n 条中 x PASS"（6 条算百分比没有统计意义）。
- 滚动窗口（最近 20 条已跑）目标 **20–30%**：
  - **>50% ⇒ 自动判"太简单"**：上隐藏输入 B / 加条件 / 换更难 trace，下轮重跑；
  - **<10% ⇒ 先查 `check()` 误判**（ref 是否真能 PASS），再考虑降难；
  - 20–30% ⇒ 保持。
- 心跳每轮写一行：`🎯 通过率: 最近20条 x/20 = y%（目标20–30%）`。

## 6. 每轮流程

1. `trace_ledger.py next --n 5` 取候选 → `claim` → 深读（有笔记就复用）→ 合成（`assets/` `reference/` `hidden/` `negative/`）。
2. 自验：`reference/` 参考解跑 `check()` 必 PASS；§4.9 (a)(b)(c) 三假提交必 FAIL；`negative_selftest.py` 全 FAIL。
3. pi 实跑：`designflow/pi_debug_status.jsonl` 追加一行，记 `pi_model / pi_thinking / pi_dur_sec / pi_verdict / ref_check`。
4. **先过断言闸门**（`k_rationale == k_check ≥ 8`；不过 ⇒ 标 `incomplete` 进 `rewrite_queue.tsv`，本轮只改它、不开新 case）→ 追加 jsonl → **`mark --status case --case-id <id>`** → 日报：`python3 designflow/gen_daily_report.py`（含「用户」列、`k 条断言` 清单、trace 覆盖率进度条）。
5. 难度回路：按 §5 判定"加难 / 保持 / 查判分"，结论写进当日日报的"阻塞/下一步"。
6. 收尾：`WAITING: 0`（下一轮 60s 后立即开下一条 case）；仅真外部阻塞（pi 异步未回 / 推送失败 / 等人工）才写 `WAITING: 1`。

## 7. 当前基线（每轮只更新这一行，不堆历史）

`11 条 proper（10 域）· 已跑 6 条 = 6 PASS · 6 trace_deepreads · test_rationale 断言清单 0/30（硬闸门见顶部令 21:5x）· 目标通过率（B 档）20–30%`
`📊 trace 覆盖率：见 designflow/trace_ledger.py stats（covered / mc≥10 候选池，target_mc=10）`
明细看日报 `reports/report_benchmark_MM_DD.html`；历史结论看 `EXPERIMENTS_DESIGNFLOW.md`。
> 现存 11 条的 `test_rationale` 本轮内全部改写成 `k 条断言：①…`（k = 该 case `check()` 的独立条件数）。

## 8. 收尾（轻量结账，不是每轮做全套）

> 收尾是"结账"：**一轮 = 1 条 case = 1 次结账**。别把结账做成产出，也别攒着不提交。

0. **体积自检**：TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限先把已闭合块**原文**搬 `ARCHIVE_OPERATOR_DESIGNFLOW.md`（留 1 行指针），搬前 `git pull --rebase --autostash`，🚫 不改小节编号/标题。数字抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB`。
1. **心跳（轻）**：`MEMORY_DESIGNFLOW.md` 顶部快照**只改变化的几行** + **追加 1 行流水**（三口径 + `🎯 通过率` + `📊 trace 覆盖率 x/y=z%` + `DEBT`）；🚫 每轮重写整份快照。
   - 顺带刷新候选池（**2026-11-11 令：mc≥10 口径**）：统计 `sessions / mc10 / mc20 / mc30 / mc100`，然后
     `python3 designflow/trace_ledger.py refresh --json '{"sessions":N,"mc10":N10,"mc30":N30,"mc100":N100,"target_mc":10,"shard_mc":{"A":10,"B":10,"C":10,"D":10}}'`
     ⚠️ **禁止**写 `"target_mc":30` 或 `shard_mc` 出现 15/30。本 shard 非共享配置 owner（只读）；A 已换池则跳过本步。
2. **日记忆**：`daily-memories-designflow/<YYYY-MM-DD>.md` **当天首轮创建，之后只追加**。
3. **提交**：**每轮（1 条 case）结束即提交**（loop 另有每 30 分钟兜底）；🚫 把工作留在工作树过夜。双仓命令：
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/EXPERIMENTS_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/designflow \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow \
           doc/ZhuLong_DAC2027/reports
git commit -m "designflow #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow
git commit -m "designflow #<轮次>: <一句话>" && git push origin master
```
4. **闭环自检**：`git status -sb` 无 ahead/behind；push 失败重试 1 次并记报错原文。

> ⏱ 心跳 **>60 min 无新提交 ⇒ 按卡死处理**。

## 9. 待确认（未确认前按默认走）

- Benchmark 是否对外（默认：先内部）
- 是否允许主动扫描 698 机（默认：否，只被动只读发现）

---

> ⚠️ 本文件为**只读指令文件**，agent 禁止修改；有异议写进 MEMORY 并存疑执行。



## 🔀 SHARD 配置（本 shard 专用 · 覆盖主 TASK 中的通用描述）

**你是 shard B（spice_char）**。只负责以下 domain：characterization, spice_sim

### 你的文件（不要碰别的 shard 的文件）
- **jsonl**：`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl`（只往这个文件追加 case）
- **台账**：`designflow/trace_ledger_B.tsv`（通过 `trace_ledger.py --shard B` 自动使用）
- **心跳**：`MEMORY_DESIGNFLOW_B.md`（只写这个文件）
- **日记忆**：`daily-memories-designflow/daily_B_*.md`

### 选 trace 命令（带 shard 过滤）
```bash
python3 designflow/trace_ledger.py --shard B next --n 5
python3 designflow/trace_ledger.py --shard B claim --session <s> --user <u> --host <h> --match <m> --domain <d>
python3 designflow/trace_ledger.py --shard B mark --session <s> --status case --case-id <id>
```

### 合并
- **不要碰主 jsonl**（`EDA-Eval-DesignFlow.jsonl`），它由 merge 脚本自动合并 4 个 shard 生成
- 你的 case 只追加到 `EDA-Eval-DesignFlow_B.jsonl`
- merge 脚本每 30 分钟自动合并 4 片 → 主 jsonl + regen 日报

### 收尾提交（只提交自己 shard 的文件）
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_B.md \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_B.tsv \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_deepreads \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow/daily_B_*
git commit -m "designflow shard B #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl \
           benchmarks/EDA-Eval-DesignFlow/assets benchmarks/EDA-Eval-DesignFlow/reference
git commit -m "designflow shard B #<轮次>: <一句话>" && git push origin master
```
