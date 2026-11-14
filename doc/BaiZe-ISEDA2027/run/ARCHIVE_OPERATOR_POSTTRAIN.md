# ARCHIVE_OPERATOR_POSTTRAIN.md — 已闭合运维指令归档

> 从 BAIZE_POSTTRAIN_TASK.md 搬迁的已闭合运维块原文。agent 只读。

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

## 📦 归档：2026-11-14 16:3x / 16:1x 两条用户令原文（运维 2026-11-14 20:0x 搬入，因任务书超 40KB 硬限；两条均已闭合，结论见任务书指针）

### 🔴 用户令 · 2026-11-14 16:3x（**基于 trace 重写 RCA 报告**：工具调用 1.9 万次为何仍只有 3.04%）· 未完成 · 最高优先

> **用户原话**：「post-train：MiniCPM5-2B 调用了工具这么多次为啥通过率还这么低呢？让 post-train 基于这个 trace 重写 RCA 文档（中文 HTML）。最后 RCA 文档末尾提出提分意见。」

**一、用户提的问题就是报告的主线**

你自己实测的 trace 统计：`search_apis` 4,418 + `search_apis_by_keyword` 2,060 + `get_api_details` 5,436 + `run_code` 1,460 + `run_commands` 6,401 ≈ **19,775 次工具调用**，而 Pass@1 仅 **3.04%**。

> **两者之间的巨大落差，就是这份 RCA 必须解释清楚的核心问题。**
> 「有工具」已经不是问题；要回答的是：**工具用了这么多，为什么还是不通过？**

**二、重写要求（不是修补旧报告，是重写）**

产出**新的**中文 HTML 报告（旧报告保留作历史，顶部加指针说明已被本报告取代）：

`reports/report_posttrain_pyaether_rca_v2_zh.html`

**必含章节**：

1. **口径与数据（可复算）**
   - 基线 ckpt、serve 配置、数据集 md5、trace 根路径、扫描命令；
   - 5-run 通过数、Pass@1 mean±std。

2. **工具调用画像（这是新增的核心章节）**
   - 各工具调用次数、**成功率/失败率**（tool_result 里有无 error）；
   - **每题平均调用次数**、调用次数的分布（是不是少数题疯狂调用、多数题不调）；
   - **调用后是否有"有效结果"**：例如 `search_apis` 返回 sim=0.9375 的高分文档，模型**后续有没有真的用上那个 API**；
   - 有无**重复调用同一 API / 死循环重试**的迹象（占多少题）。

3. **失败归因（自行从 trace 提炼，不预设分类）**

   重点回答这几个**具体**问题（能答就给数字，答不了标 TODO）：
   - **检索到 ≠ 用对**：`get_api_details` 拿到了正确文档，后续生成的代码里有没有出现该 API？还是用了别的（错的）API？
   - **写得出 ≠ 跑得通**：`run_code` 报 `SyntaxError` / `Code contains non-ASCII` 各占多少题？这些题最后有没有修好？
   - **跑得通 ≠ 判得过**：代码执行成功但 check 判 fail 的，占多少？失败在哪个断言？
   - **迭代次数**：`run_commands` 6401 次里，多少是有效迭代、多少是原地打转？
   - **prompt 矛盾的影响**：`.17` 用的 `eval_sys_prompt_template_no_sandbox.md` 明写「本场景无沙箱可实际执行，内部推演唯一校验」，但 agent 仍调用 `run_code` 1,460 次 —— 这种**指令与环境自相矛盾**对模型行为的影响，请在 trace 里找证据（例如模型是否表现出"不敢信执行结果"、是否反复推演）。

4. **图表**：工具调用分布 / 失败漏斗（检索→用对→跑通→判过）/ 各类占比，**内联 SVG，单文件自包含，0 外链 0 script**。

5. **【报告末尾】提分意见（用户明确要求）**

   按 **ROI 排序**给具体可执行的建议，每条写清：
   - **改什么**（数据 / prompt / 工具 schema / 训练 / 评测环境）
   - **依据**（对应上面哪类失败、多少题、trace 证据）
   - **预期收益**（保守估计 + 理由）
   - **成本**（人时 / 机时）
   - **优先级 P0/P1/P2**

   最后给一句 **「如果只做一件事，做哪件」**。

**三、纪律**

- 所有数字**可复算**（路径 + 命令），取不到标 `TODO`；
- 🚫 不许编造 trace 原文；
- 🚫 不要用「模型能力不行」这类空话收尾 —— 必须落到「哪一步断掉了」；
- 报告落 `reports/`，中文、单文件、0 外链、0 script。

---

### 🔴 用户令 · 2026-11-14 16:1x（**看 3.04% 那次 run 的 trace，判定是否有正确的工具调用**）· 未完成 · 最高优先

> **用户原话**：「现在有两种意见：
> 意见A：3.04% 使用了正确的 API 文档检索工具和沙盒
> 意见B：3.04% **没有** 使用正确的 API 文档检索工具和沙盒
> 让 post-train 看看 3.04% 这次 run 的 trace，看看有没有正确的工具调用，有没有正确的结果不就知道了吗？」

**一、要你做什么（用 trace 实证，不要推理）**

去 3.04% 那 5 个 run 的**原始 trace** 里，**逐条统计工具调用**，用事实回答 A/B 之争。

**必须统计的三类事实**（每条都要给出计数 + trace 路径 + 原文摘引）：

1. **API 文档检索工具**是否被调用、调用是否成功：
   - 工具名（你评测配置里 pyAether MCP 的 `search_apis` / `get_api_details` 等，按实际名）
   - **调用次数** / **成功次数** / **失败次数**
   - 失败时的错误原文（如 `NoSuchToolError` / 403 / 超时 / 工具不存在）
   - 若**从未调用**：说明是模型没想到调、还是工具没挂在工具列表里（这两种含义完全不同）

2. **沙盒执行工具**（`run_code` 等）是否被调用、结果如何：
   - 调用次数 / 成功次数 / 失败次数
   - 典型成功返回（例如 `2+2=4` 之类的真实回显）
   - 典型失败返回（连接失败 / 端口不通 / 403 / 超时）
   - 沙盒端口/隧道相关错误原文

3. **是否存在"工具根本没注册"的证据**：
   - trace 里的工具列表快照（system prompt / tools schema 里到底有几个工具、名字是什么）
   - 与 **zhulong 在 36.15 上跑时的工具列表**做对比（可直接问 zhulong 要它的口径）

**二、判定输出（必须二选一，给硬证据）**

在 MEMORY 心跳里用一行给出结论：

```
3.04% trace 判定: [A 有正确工具调用 | B 没有] · 依据: search_apis 调用 n 次/成功 m 次 · run_code 调用 x 次/成功 y 次 · 工具表 z 个
```

- 若 **A**：说明 3.04% 是有效基线，A5 可省；但仍需给出"隧道 vs 直连"的差异说明。
- 若 **B**：说明 3.04% **无效**，须立即在 RCA 报告顶部标「作废 + 原因」，并按方案文档的阶段 A 重做。
- 若**证据不足**（trace 缺失/损坏/只有 stdout 无 tool_calls）：写 `证据不足 + 缺什么`，🚫 不许硬猜。

**三、范围与纪律**

- 只读 trace，**不重跑评测**（本轮只做判定）。
- 统计要能复算：给出你的扫描命令 + trace 根路径。
- 🚫 不许用"应该/大概/可能"下结论；A/B 之争只认 trace 里的原始记录。

---


## 📦 归档：2026-11-12 11:2x 隧道令 / 2026-11-10 17:10 占位令 / 2026-11-06 P0-P3 令 原文（运维 2026-11-14 wake501 搬入，因任务书超 32KB 软限；三块均已闭合/前提消失，结论见任务书指针）

> 搬迁说明：① 11:2x 隧道令——dual-nix-tunnel 已通（TUNNEL_OK 实测、run_code e2e PASS），连通配置已落 `.env`+MEMORY 关键事实段；② 17:10 占位令——前提「沙盒未通」已消失，GPU5 现为 vision R9、GPU6/7 为 eval serve；③ 11-06 P0-P3 令——P0/P1/P2/P3预备 全部 ✅ 交付，P3 正式训练 ⏻ 等 pretrain ckpt（ETA≈2026-12-25），已在任务书「阻塞项」单列。原文如下，未改写。

---

### 🔴 用户令 · 2026-11-12 11:2x（**沙盒隧道已启动——只用它 SSH 到 36.15 以访问 EDA 环境**）· 用户直令 · 最高优先 · 未完成

> **用户原话（第二轮，覆盖上一号令的细节）**：「沙盒隧道已启动，只要求它使用隧道 SSH 到 36.15，以进一步访问 EDA 环境即可。」

**立即执行**（本轮首要任务；上一号令「自行建立隧道」之细节作废，隧道**已由外部启动好**）：

1. **先读**本机 `.17` 上的 `cat /nas_data/app.e0031982/code/dual-nix-tunnel/README.md`，理解如何使用这条**已就绪的隧道**（ssh 命令、端口/跳板参数、认证方式）。
2. **通过隧道 SSH 到 36.15**（即 `10.251.36.15`，ZhuLong 那台），验证 `ssh` 可达并能登录。
3. 在 36.15 上**进一步访问 EDA 环境**（pyAether Python+SWIG / Virtuoso SKILL 沙盒），用最小用例实测 `run_code` 端到端可达。
4. 把实际可用的连通方式（走哪条 ssh 隧道、目标主机/端口）**更新进** `eda_fastmcp .env`、`MEMORY_POSTTRAIN.md` 关键事实段、以及本任务书隧道说明；替换旧的 `SANDBOX_HOST=10.129.32.75:8664/8665/8653/8669` 失效通路。
5. 隧道打通后，回到 2026-11-10 计划主线：**拆 GPU5/6/7 占位 serve → 用 v11v38 语料重训 SFT → 评测验证 data gap coverage 改善 → baseline eval 5-run → RL R1-R4 起跑**。
6. 凭证/密钥路径一律存仓库外、不入库不入日志（沿用「secret 不入库」纪律）。
7. 完成后在 MEMORY_POSTTRAIN.md 报告：SSH 36.15 是否真正可达（附探测输出证据）、EDA 访问是否通、连通配置落盘位置、下一步动作，保持 `WAITING=0` 继续主线。

---

---

### 🔴 用户令 · 2026-11-10 17:10（**sandbox 未通前用 serve 占住 GPU5-7，防止被挪用**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「既然阻塞（隧道未通），让post-train先随便起一些长任务把后三卡占用起来（比如也serve MiniCPM5，否则被挪用）。」

**立即执行**：
1. 在 GPU 5/6/7 上各启动一个 vLLM serve MiniCPM5-2B（复用已有 venv 和配置），端口分别 8097/8096/8095。
2. 命令模板（直接跑）：
```bash
CUDA_VISIBLE_DEVICES=<N> HF_HOME=/tmp/hf_home TRANSFORMERS_CACHE=/tmp/hf_home HF_MODULES_CACHE=/tmp/hf_home/modules \
  nohup /tmp/vllm_venv/bin/python -m vllm.entrypoints.openai.api_server \
  --model /nas_data/app.e0031982/models/MiniCPM5-2B \
  --served-model-name minicpm5-2b-gpu<N> --host 0.0.0.0 --port <PORT> \
  --trust-remote-code --gpu-memory-utilization 0.85 --max-model-len 32768 \
  > /tmp/vllm_gpu<N>.log 2>&1 &
```
3. 启动后验证：`curl -s http://localhost:<PORT>/v1/models` 有响应 + `nvidia-smi -i <N>` 显存占用 ~37GB。
4. **注意**：transformers 必须是 4.49（不是 5.x），否则 tokenizer 报错。如果 `import transformers; print(transformers.__version__)` 不是 4.49，先 `uv pip install --python /tmp/vllm_venv/bin/python "transformers>=4.45,<4.50"` 降级再启动。
5. **注意**：启动前先 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv -i <N>` 确认 GPU 无残留进程，有则 `kill -9` 清理。
6. 占住后在 MEMORY_POSTTRAIN.md 记录端口映射表，并保持 WAITING=0 继续做其它可做的事（归档 EXPERIMENTS、准备 SFT 脚本等）。

---

---

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

---

