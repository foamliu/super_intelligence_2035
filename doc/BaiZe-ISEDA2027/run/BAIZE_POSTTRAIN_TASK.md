# BAIZE_POSTTRAIN_TASK.md

> BaiZe Stage(ii) LLM Post-Training 任务书 —— 领域退火 / SFT / RLVR-GRPO 三步走 + EDA-Eval-PyAether 评测。
> 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`。
> 本文件为**只读指令文件**，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_POSTTRAIN.md`、`EXPERIMENTS_POSTTRAIN.md` 和 `daily-memories-posttrain/`。

> 📁 **报告目录纪律（全局常驻）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 禁止产出到 `run/reports/` 或项目根 `reports/`。

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否已产出交付物并 commit 或运维已标「已闭合」。没有 `✅ 已完成/已交付` 标记的一律视为未完成，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，不是本轮交付物。归档完立即回到运维指令区，从最上面那条未完成指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡去等下次唤醒」。只要有未完成指令，`WAITING` 必须置 0（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 本区为运维下发指令；agent 只读、不写（除「归档搬迁」这一唯一例外，见下方体积规程）。
> 新指令置顶；已闭合块按体积规程原文搬入 `run/ARCHIVE_OPERATOR_POSTTRAIN.md`、留 1 行指针。

### 🔴 用户令 · 2026-11-07 10:10（**GPU 11/9 到位是既定安排，不要再问；等待期继续深入调研**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「posttrain：不是说了11/9吗，还问啥。继续调研啊。」

#### 0. 口径澄清（一次性钉死，之后不得再问）

- `.17` 的 4 张 A40 于 **2026-11-09** 到位，这是**既定安排**，不需要用户再确认、不需要运维协调。
- 后续任何唤醒：🚫 **不得**再把「什么时候给 GPU」「是否现在腾卡」「要不要等 11/9」写成阻塞项或待用户决策。
- 正确做法：按 11/9 倒排准备，**到位当天自动起跑**（不等到下次唤醒再问）。

#### 1. 11-07 -> 11-09 的主任务 = 深入调研（不是例行巡检）

每轮唤醒必须至少产出**一项实质内容**并落盘，从下列任选（鼓励都做）：

| 编号 | 调研方向 | 必须回答的问题 |
|:--|:--|:--|
| R1 | **EDA 环境交互式 RL 的可执行方案** | 环境接口（SSH/双向隧道/本地 clone）如何稳定调用？奖励如何自动可判定？单题 rollout 预算？超时与部分失败的恢复策略？ |
| R2 | **PyAether 造题与难度分层** | 把 500 题模板扩展到可自动判定正确性的规模（目标 2k-5k）；难度标定方法（pass@8 profiling 还是规则分层）；每档题的区分度证据 |
| R3 | **奖励设计与 GRPO 稳定性** | 连续化/分档混合、省 GPU 的 group 配置、长度与格式作弊的抑制、KL 与 clip 的取值依据；失败模式（对照 vision 线离散奖励教训） |
| R4 | **35% 侧失败模式分类** | 从 MiniCPM5-2B 36% 基线出发，按 API 类别/错误类型（语法错、API 误用、逻辑错、超时、缺依赖）建分类法；等 GPU 后用真实轨迹校正 |

#### 2. 反空转条款

- 🚫 禁止「只写心跳 + 置 `WAITING: 1`」式空转。
- **连续两轮无新增调研产出 = 未完成任务**，必须 `WAITING: 0` 继续做。
- 每轮心跳必须写清：`本轮新增调研产出：<文件/章节/结论>`；没有就说明为什么。

#### 3. 交付物

1. 调研结论写入 `EXPERIMENTS_POSTTRAIN.md` 新节（或扩写既有节），带检索词与来源链接；
2. 需要时产出中文 HTML 报告到 `doc/BaiZe-ISEDA2027/reports/`（单文件自包含）；
3. 可执行脚本/配置/数据落 `run/`，须 `bash -n` / `--help` 可跑通；
4. commit 前缀 `posttrain research:` 或 `posttrain prep:`。

#### 4. 11/9 GPU 到位后的第一件事（预先写死）

1. `vllm serve /tmp/models/MiniCPM5-2B`（venv 已就绪）-> 复测 36% 基线（同口径 5-run）；
2. 采集真实失败轨迹，**用实测替换 R4 调研中的假设**；
3. 按 R1/R2/R3 结论起第一轮 EDA 交互式 RL（替身预演），报告显著标注「收益不可迁移到白泽」。

---


### 🔴 §用户令·2026-11-07（**替身模型 × EDA 交互式 RL 预演**：用 MiniCPM5-2B 走通「读文档→自造题→EDA 环境求解→拿反馈→RL」闭环）· 用户直令 · 最高优先 · ✅ 已交付

> **用户原话（分三句，均 2026-11-07）**：
> ①「.17 GPU 比较弱只有 4 张 A40。因此只能做跟 EDA 环境有关的强化学习。现在白泽模型还在预训练，我想用 MiniCPM5-2B 或者 Qwen3.5-2B 做替身，先测基线，然后通过跟 EDA 环境的交互做 RL 训练，强化写 PyAether 脚本的能力。」
> ②「EDA-Eval-PyAether 158 不能用来训练，但是可以通过双向隧道，让 post-train 可以连通 EDA 环境，哪里有 python 等 PyAether 执行环境和 API 文档 API。post-train 可以通过阅读文档，自己生成问题，在 EDA 环境中尝试解决 & 获取反馈的方式提升自己对特定领域的熟悉程度。」
> ③「把这些信息给 post-train 沟通，让它沿着这个方向，继续深入调研，充分做好准备。」

#### 0. 目标定位（**先读这段，决定后面所有判据**）

| 定位 | 内容 | 是否本次目标 |
|:--|:--|:--|
| **A** | 验证「与 EDA 环境交互式 RL」**这条方法链路**能否走通 | ✅ **是** |
| **B** | 用替身预演白泽后训练的**流程**（数据配方/奖励设计/超参），等 pretrain ckpt 直接复用 | ✅ **是** |
| ❌ | 「用替身模型在 158 题上刷高分」 | 🚫 **不是**，且不允许 |

> ⚠️ **报告必须显著标注**：本次 RL 收益**不可迁移**到白泽（2B 通用模型 ≠ 白泽；A40 也训不动大模型）。本次仅验证方法链路 + 沉淀可复用流程。**🚫 不得把替身分数写成白泽的预期成绩。**

#### 1. 硬约束（违反即作废）

- 🚫 **不改任何代码/脚本**：`run/baize_posttrain_*.sh` 一律**只读**（用户 11-07 明确「这些代码都先不动」）。改动需求只写进方案的「待改清单」，不动手。
- 🚫 **158 题绝不上训练**（含改写版）：投料前必过 `run/baize_posttrain_contamination_gate.sh` 指纹闸门。这是 §P1-e 红线。
- 🚫 **不下载 A 类**（`/nas_env` 17.67TB 分词镜像）：post-train 用不到。
- 🚫 **也不下载 B 类 agentic**（用户 11-07 改口）：当前只做 **EDA 环境的 RL（验证 self-play 收益）**，而基模 MiniCPM5-2B / Qwen3.5-2B **本身已具备 agentic 能力**，无需额外语料。**本令周期内不下任何数据**（WSD 跑到 12 月底，SFT 阶段再议）。
- 🚫 **不得以「隧道未通 / 等 GPU」为本令的阻塞理由**：下面 L1/L2 两项**零 GPU、零隧道**，本轮必须推进。

#### 2. ⭐ 你已有的素材（**已实测，不用重新调研**）

| 素材 | 位置 | 规模 | 状态 |
|:--|:--|:--|:--|
| **PyAether API 文档** | `~/code/eda_fastmcp/docs` + `kb` | **8463 项 API**，≈21MB JSON，≈4–5M tok | ✅ wake4 实测可达（见 `EXPERIMENTS_POSTTRAIN.md` §PyAether-corpus） |
| **EDA 执行环境** | 36.15（经双向隧道可达） | `run_code` 四组合：pyAether/aether · skill/virtuoso · tcl/waveview · tcl/innovus | ✅ 现存 |
| **执行反馈字段** | `run_code` 返回 | `response` / `error_log` / `print_log` / `result` | ✅ **这就是天然 reward 信号源** |
| **污染隔离闸门** | `run/baize_posttrain_contamination_gate.sh` | — | ✅ 已定稿 |
| **存量报告** | `reports/report_posttrain_*.html` × 4 | 含 D1–D6、§PyAether-corpus、数据盘点 | ✅ 交付 |

> 💡 **关键认知**：本方案 = **Self-Instruct / Self-Play + 可执行反馈（executable verification）**。EDA 场景的独特优势是**有真实执行器判对错**，不像纯文本任务只能靠 LLM 自评 —— 奖励信号因此是**客观的**。

#### 3. 四层实施（L1/L2 本周做，L3/L4 等隧道+GPU）

**L1 · 素材测绘（🚫 零依赖 —— 本轮必须交付）**

**L1.0 · 先把 PyAether 文档拉到本地（用户 2026-11-07 直令 · 最优先）**

> 用户原话：「你可以让 post-train 在本地（code 目录）git clone eda_fastmcp 这个仓库。地址可以从 zhulong 那里获取，这样就可以看看 PyAether 的文档。」

1. **目标**：`git clone` 到本地 `~/code/eda_fastmcp`，从此**离线可读** PyAether API 文档，不必依赖 36.15 挂载或隧道。
2. **拿地址**（仓库文档里**没有**记录 remote，必须现场查，🚫 别猜）：
   - 在 **36.15** 上执行 `cd /nasdata/app.e0031982/code/eda_fastmcp && git remote -v`（这一步需隧道，若隧道未通则跳过）；
   - 或查 `doc/ZhuLong_DAC2027/` 下的任务书/归档（`ZHULONG_TASK.md:317` 仅写「仓库外的独立 git 仓库」，无 URL）；
   - 或问运维（本令的发起人）。
3. **clone**：`cd ~/code && git clone <URL> eda_fastmcp`。`.17` 外网需显式带 proxy：`https_proxy=http://<proxy> http_proxy=http://<proxy> git clone ...`（wake17 已验证 proxy 可通 github）。
4. ⚠️ **若 clone 失败（内网私有仓库 / .17 无路由 / 需凭证）⇒ 立刻上报 blocker 并写进报告**，改用备选路径：经隧道或 scp 从 36.15 拷 `docs/` + `kb/` 目录（只拷文档，不拷数据集）。
5. **验收**：`ls ~/code/eda_fastmcp/docs` + `kb` 能看到 API 文档；统计文件数与总字节，与已知口径（≈8463 项 API / ≈21MB）对得上。

> 💡 这一步价值很大：**把「必须等隧道才能看文档」变成「现在就能看」**，L1/L2 的数据侧因此完全解耦。

---

**L1.1 · API 结构化测绘**
1. 把 8463 项 API 导出为结构化清单：`api_name / 模块 / 签名 / 参数(type,default) / 返回 / 关联示例`。
2. **可出题性评估**（核心）：给每项打「可判分」标签 ——
   - ✅ **纯函数型**（输入→输出可断言，如查询/计算/格式化）
   - ⚠️ **副作用型**（改数据库/开窗/写文件，判分需快照对比）
   - ❌ **不适用**（GUI 交互、需要人工确认、强依赖 license 独占）
3. 产出 **`可出题 API 白名单`**（预期从 8463 筛出数百~上千条），按域分组（pyAether/skill/tcl×3 host）。

**L2 · 题目自动生成（🚫 零依赖 —— 本轮必须交付）**
1. 基于白名单**模板化造题**（🚫 **不要用 2B 模型自举造题** —— 见下方 §4 陷阱①）。
2. 三档难度：**单 API 调用**（低）→ **多 API 串联**（中）→ **带约束的查询/分析**（高）。
3. **每题必须自带可机器判定的验收条件**（例：「返回的 cell 数 == N」「输出 JSON 含键 X 且值 == Y」）——没有验收条件的题**一律丢弃**。
4. 产出 `rl_pyaether_synth_tasks.jsonl`（目标 **500 题**起步，格式对齐 `EXPERIMENTS_POSTTRAIN.md:159` 约定）。
5. 🚫 每批生成后必过 contamination gate（对 158 题做 n-gram/指纹比对）。

**L3 · 环境自验证（⏳ 等隧道，周一/二后）**
- 把 L2 的题丢进 36.15 的 EDA 沙盒，**验证题目本身是否可解**（用参考解或强模型跑一遍）。
- **解不出来的题必须剔除** —— 否则奖励信号是错的（模型再努力也拿不到 1）。
- 📌 记住：**造题容易，造「可解的题」难**。这一步的产出（通过率）本身就是质量指标。

**L4 · RL 训练（⏳ 等 GPU 11/10 + 隧道）**
- 替身基座：**MiniCPM5-2B 优先**（唯一理由是它有 36% 锚点可对照；Qwen3.5-2B 无基线，测出数来无法归因）。
- 算法 GRPO；**奖励起步用 R2（断言通过率部分分），不要用 R1（二值）** —— 2B 模型在 R1 下大概率大面积 0，无梯度。
- 冒烟用脚本内置 `--smoke`（`ITERS=10, GROUP_SIZE=4, SANDBOX_CONCURRENCY=2`），稳了再逐步加并发。

#### 4. 必须提前想清的两个陷阱（写进方案，别等踩了再说）

**① 造题的「自举悖论」**
让 2B 自己造题 ⇒ 要么全是它会做的（学不到东西），要么全是它不会的（全错无梯度）。
⇒ **对策**：造题阶段用**模板化确定性生成**（可控难度）；难的类别可借 gateway 强模型（glm-5.3-flash）辅助生成题干，但**验收条件必须由模板产生**（不能靠模型自己说「这题对」）。

**② 奖励稀疏性**
纯 pass/fail 在 2B 上很可能大面积 0。
⇒ **对策**：用 R2 分层给分（执行成功 0.2 / 部分断言 0.2–0.8 / 全通过 1.0），并在报告里**同时报 cheat rate**（§5.1 anti-cheat 全程生效）。

#### 5. 本周交付物（🚫 零依赖，必须完成）

0. **`~/code/eda_fastmcp` 本地克隆就绪**（L1.0）—— `docs/` + `kb/` 可离线读取；若 clone 不可行（内网私有/无路由），改为「已上报 blocker + 给出 scp 备选方案的执行结果」。**这一项决定 L1/L2 能否脱离隧道推进，优先做**。
1. **`reports/report_posttrain_synth_rl_plan_zh.html`**（中文单文件、0 script、0 外链）—— 深度调研报告，必含：
   ① 8463 API 的可出题性分级统计（纯函数/副作用/不适用，各多少条 + 按域分布）
   ② 白名单构造方法与结果
   ③ 三档难度模板设计（含 2–3 个完整样例：题面 + 验收条件 + 期望输出）
   ④ **可解性预判**（哪些类别预计好判分、哪些有坑）
   ⑤ 奖励设计对比（R1–R4 在 2B + 稀疏反馈下的取舍，给出推荐与理由）
   ⑥ 已知失败模式调研（附**来源 URL + 日期**，🚫 不许编造）
   ⑦ **与白泽的可迁移性分析**（哪些流程可直接复用、哪些依赖模型规模）
2. **`run/rl_pyaether_synth_tasks.jsonl`** —— ≥500 题，每题自带验收条件，已过 contamination gate（附闸门通过日志）。
3. **隧道 SOP**（`EXPERIMENTS_POSTTRAIN.md` 新增一节）：端口映射 / 长连接保活（`ServerAliveInterval`）/ 并发起步值 / 5 个逐段验证步骤及判据 / 常见失败模式与排查。
4. **SFT 数据可达性核实**（仅此项，**不下载**）：SFT 99.76G 到底在哪台机（`/nas_data` vs `/nas_env` 两处记载矛盾，需现场实测 `du -sb`）。⚠️ **B 类 agentic 下载清单与分词口径均已按用户 11-07 指示暂缓**（见 §1 硬约束）——**不要做，也不要写进本令交付物**。

#### 6. 护栏

- 🚫 不启训练、不占 GPU（本周全为零 GPU 工作）；CPU 降载 `OMP_NUM_THREADS≤8` + `nice -n 19`。
- 🚫 不动他人数据；web search 只登记可下载源，不发起下载（下载需另批）。
- 数字全可溯源；拿不到就标「未核实」。
- commit 前缀 `posttrain synthrl:`；TASK/MEMORY ≤32KB。
- **每轮唤醒必须实际推进 L1/L2**，🚫 不许「写心跳 + 置 WAITING:1 睡去」。本令未完成前 `WAITING: 0`。

> **完成标记**：上述 4 项交付物齐全 ⇒ 本行改 `✅ 已交付`；未完成 ⇒ `WAITING: 0`（60s 后继续）。

---

### 📦 §用户令·2026-11-06 22:5x（后训练各阶段数据调研 + 本机硬盘体检）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`

> 交付：`reports/report_posttrain_stage_data_survey_zh.html`（45.4KB / 10 节 / 0 script / 0 外链）+ `EXPERIMENTS_POSTTRAIN.md` §E + 硬盘体检附节。**关键结论**：`/` 386G 可用(84%)、`/nas_data` 20T 可用(85%)，后训练全流程预估 200–300GB ⇒ **存储非瓶颈**；可清理候选 ≈4.7G（Qwen3.5-2B 4.3G 用途待确认）；`/nas_inference` 与 `/nas_env` 在 .17 **未挂载**。需要细节再读 archive。

### 🆕 2026-11-06 运维直令：建立 post-train 线 · 先做 P0 诊断 + 数据/方案预研（不启训练）

> 这是本线**第一条**指令。post-train 线**新建**，从零起步。
> ⚠️ **当前阶段（架构实验期末尾 → 正式训练前）**：pretrain S1 仍在 `.29` 跑（iter~101320/700000，ETA≈2026-12-25），**post-train 的正式训练依赖 pretrain 收敛 ckpt**。
> ⇒ **本线现在不启任何训练**，先做**零成本/低成本的准备 + 预研**，等 pretrain ckpt 就绪后再起。
> ⏱️ ISEDA 2027 投稿截止 ≈ 2027-02-01，倒推 post-train 正式训练窗口 ≈ **2026-12 下 → 2027-01 中**（约 3 周）。

**P0（本轮起，零 GPU，必须先做）—— §7.0 诊断清单 D1–D6**

> 出处：项目总纲 `README.md` §7.0。这六项**不花任何 GPU**，但直接决定 post-train 该往哪使劲。
> 数据来源：`~/eda_code_eval/*/final_report.json` 的 `details_per_task`（**数据已在手，无需重跑**）。
> 36% 是 MiniCPM5-2B 在 full harness 下已测的 Pass@1（与 94.0% 同口径）；58 pp 差距里有多少是「协议问题（可回收）」vs「真实能力差距」，全靠这六项判。

| # | 诊断项 | 判读 |
|:--|:--|:--|
| D1 | 工具调用合法率（格式合法 tool_call / 总数） | <90% → 协议问题，SFT 可大幅回收 |
| D2 | 工具调用频次（每任务平均调用次数，vs DeepSeek 的） | 显著偏低 → 模型不「用工具」、纯靠回忆 → SFT 可修 |
| D3 | 超上下文/截断比例 | 高 → 长上下文适配是 post-train 的前置项 |
| D4 | 失败类型分解（执行报错 vs 断言失败） | 报错多 → API/领域知识问题（SFT 领域语料）；断言失败多 → 语义推理问题（RL 价值更大） |
| D5 | per-scenario 通过率（Layout 64 / Schematic 47 / Design Mgmt 24 / Others 23） | 决定 SFT 数据的配比 |
| D6 | 平均迭代轮数（Φ）分布 | 显著低于 DeepSeek → 模型不会用执行反馈闭环 |

**交付**：
1. 从 `~/eda_code_eval/*/final_report.json` 提取 D1–D6 六项统计（MiniCPM5-2B 的那次 36% 运行；若有 DeepSeek 94% 的对照运行则一并列出做 diff）。
2. 若 `final_report.json` 字段不足以算某项，**如实标注「字段缺失」**并写明需要补抓什么；🚫 禁止编造。
3. 产出中文 HTML 报告 `reports/report_posttrain_diagnose_d1d6_zh.html`（自包含、0 script、0 外链、≥8 节：摘要 + 六项各一节 + 结论「58 pp 里多少是协议可回收」初步判断 + 对 post-train 三步的侧重建议）。
4. 同步把六项数值写进 `EXPERIMENTS_POSTTRAIN.md` §D（新建）。
5. commit 前缀 `posttrain diag:`。

**P1（P0 完成后，零/低 GPU，并行可做）—— 数据盘点 + 方案预研**

> post-train 正式训练需要的数据**部分已就绪**，部分需补。先盘清。

| 项 | 内容 | 现状（已知） |
|:--|:--|:--|
| P1-a | **SFT 通用指令集** `UltraData-SFT-2605`（319G / 1504 JSONL / 20.97B tok） | ✅ 已分词镜像（`DATA_MAPPING.md` L11） |
| P1-b | **SFT agentic 指令集** `UltraData-SFT-Agent-2609`（51G / 50 shard） | ✅ 已分词（`DATA_MAPPING.md` L12） |
| P1-c | **B 类 agentic 数据**（`to-tool-call-datasets`/`AgentTrove`/`Nemotron-Cascade-SFT-SWE`/`terminal-command-execution-sft` 等，落 `/nas_inference`） | ⏳ 已下载未分词（`DATA_MAPPING.md` §F） |
| P1-d | **PyAether 领域语料**（API 参考 / EDA 工具文档 / HDL 源码，供领域退火 + SFT 合成） | ⚠️ **待确认来源** —— `eda_fastmcp` 的 API 知识库能否导出为纯文本？见总纲 §9 待确认项 |
| P1-e | **EDA-Eval-PyAether 158 任务污染隔离规则**（§5.1 红线） | ⚠️ 必须在合成任何 PyAether 训练对之前定稿 |

**P1 交付**：
1. 盘点 P1-a~P1-c 的**实际可用性**（路径存在 / 字节数 / 是否已分词为 mcore 格式 / token 数），写成 `EXPERIMENTS_POSTTRAIN.md` §Data 表。
2. **P1-d 调研**：`eda_fastmcp` 的 API 知识库（`/nasdata/app.e0031982/code/eda_fastmcp`）能否导出为纯文本文档？能导出多少？格式？→ 写成 `EXPERIMENTS_POSTTRAIN.md` §PyAether-corpus 节 + 在报告里给「领域退火语料组装方案」（来源/配比/预估 token 数）。
3. **P1-e 污染隔离规则草案**：按 API 名 / 函数签名做隔离，确保 158 任务的答案与断言不泄漏；写出可执行的隔离脚本骨架（即使现在不跑，也要先把规则定下来）。🚨 这是红线，违反则整节作废（总纲 §5.1）。
4. 产出中文 HTML 报告 `reports/report_posttrain_data_inventory_zh.html`（自包含、≥10KB）。
5. commit 前缀 `posttrain data:`。

**P2（P1 完成后，零 GPU，纯设计）—— 三步训练方案书**

> 依据 P0 诊断 + P1 数据盘点，写 post-train 三步的**完整方案书**（不启训练，只设计）。

1. **领域退火**：复用 Stage(i) 的 WSD 机制；退火语料配比（通用/code/PyAether）、退火步数、与「仅 SFT」对照组的隔离设计（总纲 §4 Stage(ii) 步骤 0）。
2. **SFT**：数据混合（agentic / +code / +math / +PyAether API 语料）；CoT+工具轨迹 vs 纯代码；LoRA vs 全参；**上下文长度 4096 vs 8192 vs 16384**（总纲 §4 步骤 1，⚠️ agentic 轨迹极易超长，长上下文适配是前置项）。
3. **RL（核心）**：RLVR + GRPO；**奖励设计 4 臂**（R1 二值 / R2 部分分 / R3 R2+工具调用惩罚 / R4 R3+API 合法性，见 `5_llm_posttrain.tex` Table\ref{tab:reward}）；🚨 **Reward hacking 是最大风险** —— anti-cheat + 单独报告 cheat rate；⚠️ **预算口径换算**：带沙盒执行时是沙盒时延 bound，按「沙盒并发数 × 墙钟」规划，不沿用 GPU-hour（总纲 §4 步骤 2）。
4. **评测**：backbone × harness 网格（总纲 §4 步骤 3）；**预注册成功阶梯 M1–M4**（36%→50%→65%→75%→85%，先定后测，避免事后合理化，总纲 §4 步骤 4）。
5. **预注册判定阈值**：点估计 + 配对检验（McNemar / paired bootstrap）显著性 + 成本比 —— **必须先定后测**（总纲 §9 待确认项）。

**P2 交付**：中文 HTML 报告 `reports/report_posttrain_plan_zh.html`（自包含、≥15KB、覆盖三步 + 评测 + 成功阶梯 + 预注册阈值 + 时间线 + 风险）。
commit 前缀 `posttrain plan:`。

**P3（pretrain ckpt 就绪后，需 GPU，正式训练）—— ⬜ 等 pretrain 收敛**

> ⚠️ **依赖**：pretrain S1 ETA≈2026-12-25（iter 700000）。P3 在此之前**不启动**。
> P3 的具体子任务（退火起跑 / SFT 起跑 / RL 起跑 / 评测起跑）将在 pretrain ckpt 就绪后由运维另行下发。
> 现在只做：把 P0/P1/P2 的方案落实到「可执行脚本骨架」（不跑，只写好 `run/baize_posttrain_*.sh` 系列 + 配方文件），等 ckpt 一到即可起。

**P3 预备（本轮可做，零 GPU）**：
1. 参照 `baize_xmodel25_decay_v2.sh` / `baize_p8_train.sh` 的结构，写 `run/baize_posttrain_anneal.sh`（领域退火配方骨架，从 pretrain ckpt resume，换数据 blend）。
2. 写 `run/baize_posttrain_sft.sh`（SFT 配方骨架，从 anneal ckpt 或 pretrain ckpt 起）。
3. 写 `run/baize_posttrain_rl_grpo.sh`（RLVR+GRPO 配方骨架；奖励 4 臂用配置开关切换；沙盒并发参数化）。
4. 写 `run/baize_posttrain_eval.sh`（EDA-Eval-PyAether 评测脚本骨架，5-run、reshuffle、fresh context、2500s timeout，接入 OpenAI-compatible endpoint）。
5. 每个脚本写好后做**语法检查**（`bash -n`）+ **dry-run 打印配方**（不真跑），把输出贴进 `EXPERIMENTS_POSTTRAIN.md` §Scripts。
6. commit 前缀 `posttrain scaffold:`。

---

### 🧹 运维总则 · 2026-10-18（禁令作用域清理，沿用）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的「等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X」只在该块任务内有效；与最新用户令或最新任务块冲突时，以最新块为准。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）

> ⚠️ **红线（违反则整节作废，见总纲 §5）**：
> 1. **污染隔离**：EDA-Eval-PyAether 的 158 个任务（prompt + 函数签名 + 断言代码）**绝对不能进任何训练集**。允许用 API 参考文档合成训练对，但必须按 API 名/函数签名隔离，论文写明隔离规则。
> 2. **反作弊**：`PreToolUse` hook 全程启用，所有实验臂逐字一致；BaiZe 的 RL 也挂同一套 anti-cheat；必须报告 cheat rate。
> 3. **口径一致**：5-run mean ± std，不得报单次值；158 任务固定集上两系统比较优先用配对检验（McNemar / paired bootstrap）。
> 4. **评测协议冻结项不得改动**（总纲 §2）：158 任务 / Pass@1 / 2500s 超时 / 单 trace 原则 / 5 次独立运行 / `-p 8 -n`。

> 📋 **评测关键资产**（总纲 §3）：
> - 代码生成 driver：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh`
> - 评分：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py`
> - 158-case 数据集：`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`
> - `BASE_DIR`：`/nasdata/app.e0031982/code/eda_fastmcp`
> - BaiZe 接入：通过 vLLM/SGLang 暴露 OpenAI-compatible endpoint，`cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，换 backbone 成本≈0。

> 🎯 **成功阶梯（预注册 · 先定后测 · 总纲 §4 步骤 4）**：
> | 里程碑 | Pass@1 | 含义 | 先验判断 |
> |:--|:--|:--|:--|
> | 起点 | 36% | MiniCPM5-2B，通用模型，零适配 | ✅ 已实测 |
> | M1 | 50% | 工具协议修好（D1/D2/D6 改善） | 几近必然 |
> | M2 | 65% | + 领域继续预训练 + SFT | 大概率 |
> | M3 | 75% | + RL | 有望，已是强结果 |
> | M4 | 85%+ | 逼近 DeepSeek-V4-Pro | 惊喜级别 |
> 阶梯意义：无论落在哪一档，结论都能成立且都值得发表（落在 M1/M2 则支持「规模非瓶颈」论，与 ZhuLong 互证）。

### 🧭 运维规程 · 2026-10-06（agent 归档 MEMORY + 任务书，常驻）

> 用户裁定：MEMORY + 任务书两样都由 agent 自己滚。
> 判据：两者均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交。
> 做法 = 只「搬迁」、不改内容：① 已闭合运维块原文搬入 `run/ARCHIVE_OPERATOR_POSTTRAIN.md`（无则新建）；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块；冲突保留双方；提交用 `posttrain 归档:` 前缀。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级，硬性）

> `MEMORY_POSTTRAIN.md` 与 `BAIZE_POSTTRAIN_TASK.md` 都每次唤醒被全文读进 prompt ⇒ 越大越烧 token。
> - 上限：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
> - 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
> - 归档去向：① 已执行完/作废的运维块 → `run/ARCHIVE_OPERATOR_POSTTRAIN.md`（留 1 行指针）；② 较早流水（保留最近 ~20 条）→ `daily-memories-posttrain/<日期>.md`（原文不改）。
> - 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头。
> - 指针：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_OPERATOR_POSTTRAIN.md；**结论**：<一句话>。需要时再读。`
> - 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条流水。
> - 纪律：归档不改变任何结论；`WAITING:` 纪律不变（正文/流水/快照里不得再出现以 `WAITING:` 开头的行）。

### 🧭 收尾铁律（每轮唤醒结束前必须执行，不许省）

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. **体积自检**（先跑，数字抄进心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_POSTTRAIN_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前你自己滚动归档，直到两者都 ≤ 32KB；> 40KB ⇒ 必须先归档再提交。
   收尾把两文件体积抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_POSTTRAIN.md）`。

1. **写心跳**：更新 `run/MEMORY_POSTTRAIN.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories-posttrain/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. **自己提交 + 推送**（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md \
              doc/BaiZe-ISEDA2027/run/EXPERIMENTS_POSTTRAIN.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_POSTTRAIN_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-posttrain
   git commit -m "posttrain #<轮次>: <一句话>"   # 🚫 提交信息必须带线名前缀
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交。
4. **闭环自检**：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。

---

## ⚠️ git 同步规则（必读，每次唤醒都要走）

### 前提：这是一个共享工作副本

vision / pretrain / data / harness 任务的 agent 与本任务共用同一份工作副本——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（多节点共享同一块盘）。

因此：
- 只需一个 agent pull，其余立刻看到。不要重复 pull，也不要因为「工作区里出现了别的任务的改动」而困惑。
- 工作区里陌生的未提交改动很可能是别线任务的在途文件。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 各 loop 会互相把对方在途文件一起提交，这是既有设计的已知副作用，不要试图「修正」它。

### 但 loop 本身只 push 不 pull（pull 必须由 agent 做）

每次唤醒按顺序执行：
1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. 提交时显式指定你自己的文件（见上方收尾铁律第 3 条）。🚫 不要用 `git add -A`。
3. 若显示 behind / diverged：`git pull --rebase --autostash origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是双方的在途改动：先把自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → 另一个 agent 正在做 git 操作：等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并跳过本次 git 操作，下次唤醒再试。
   - 🚫 绝不 `git push --force`；🚫 绝不 `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind 才算闭环。
5. 流水记一行 git 结果。

---

## ══════════════ Stage (ii) 任务定义 ══════════════

你是推进 BaiZe Stage(ii) LLM Post-Training（领域退火 → SFT → RLVR-GRPO → EDA-Eval-PyAether 评测）的自动化 agent（Cline），被唤醒时按 `MEMORY_POSTTRAIN.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

### 阶段总览（与论文 `5_llm_posttrain.tex` 对齐）

| 步骤 | 名称 | 论文节 | 依赖 | 状态 |
|:--|:--|:--|:--|:--|
| 0 | 领域退火（Domain Annealing） | §5.1 | pretrain ckpt | ⬜ 等 pretrain |
| 1 | SFT | §5.2 | 退火 ckpt 或 pretrain ckpt + SFT 数据 | ⬜ 等 P0/P1/P2 |
| 2 | RLVR + GRPO（4 臂奖励 R1–R4） | §5.3 | SFT ckpt + 沙盒 | ⬜ 等 SFT |
| 3 | EDA-Eval-PyAether 评测（backbone × harness 网格） | §5.5 | 各阶段 ckpt | ⬜ 等 ckpt |
| — | Anima 协议 + 本地自纠错（部署） | §5.4 | RL ckpt | ⬜ 部署阶段 |

### 当前可做（不依赖 pretrain ckpt，零/低 GPU）

- **P0**：§7.0 诊断清单 D1–D6（从已有 36% 运行的 `final_report.json` 提取，零 GPU）。
- **P1**：数据盘点 + PyAether 语料调研 + 污染隔离规则草案（零/低 GPU）。
- **P2**：三步训练方案书（纯设计，零 GPU）。
- **P3 预备**：训练/评测脚本骨架（零 GPU，只写不跑）。

### 阻塞项（等依赖就绪）

- **正式训练（退火/SFT/RL/评测）** 阻塞于 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。
- **GPU**：post-train 线在 `10.252.32.17`；正式训练的 GPU 待 pretrain 完成或运维协调分卡（见 `GPU29_ALLOC.md`）。P0/P1/P2/P3预备 纯 CPU/IO 在 `.17` 本机跑。

### 红线（违反则整节作废）

1. **污染隔离**（总纲 §5.1）：158 任务的 prompt + 函数签名 + 断言代码绝对不能进任何训练集。
2. **反作弊**（总纲 §5.2）：`PreToolUse` hook 全程启用；RL 挂同一套 anti-cheat；报告 cheat rate。
3. **口径一致**（总纲 §5.3）：5-run mean ± std；配对检验；引用 ZhuLong 数字前确认口径。
4. **评测协议冻结**（总纲 §2）：158 任务 / Pass@1 / 2500s / 单 trace / 5-run / `-p 8 -n` 不得改动。
5. **预注册**：成功阶梯 M1–M4 + 判定阈值先定后测，避免事后合理化。

### 与他线边界

- **pretrain 线**：提供 base ckpt；post-train 从其收敛 ckpt resume。不 kill pretrain 训练。
- **data 线**：提供 SFT/退火语料的分词镜像；PyAether 语料若需新分词，提需求给 data 线或自行分词（避免重 I/O 撞训练）。
- **harness 线**：提供评测 driver / 评分脚本 / 158-case 数据集的接入方式；post-train 评测复用同一套，只换 backbone。
- **vision 线**：独立，post-train（纯文本）不与 vision 交叉；Stage(iv) MLLM 对齐是另一阶段。

---

> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_POSTTRAIN.md`、`EXPERIMENTS_POSTTRAIN.md` 和 `daily-memories-posttrain/`。
