# BAIZE_VISION_TASK.md

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 📦 §用户令·2026-11-07 10:10（阶段2 放行·CPU 放开试各种 idea）✅ 已交付（wake#893：6 项授权变更 v2–v5 全试，v5 获统计显著正结果 A16%→B37%→C53% p=0.0009）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-14 wake#1212 归档）。需要时再读。

### 📦 §用户令·2026-11-07 09:2x（走出「干等 GPU」·用 .12/.29 CPU 设计有效 RL 证明 Qwen3.5-2B 波形理解显著提升）✅ 已交付（wake#893：数据集调研+技术栈冒烟+RL 方案+CPU 实验(含对照与显著性)+中文 HTML 报告 全部交付）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-14 wake#1212 归档）。需要时再读。


> 📦 已归档（2026-10-30~31，ViT-L 68.236% / MLLM 26.10% 写进论文 ch6/ch7、6_vision_encoder.tex 重写、第6章审校修订、波形图强化 RL 计划书、2B MLLM 看懂波形图能力报告）→ run/ARCHIVE_OPERATOR_VISION.md（wake#424/#435/#436/#437/#439）。需要时再读。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔴 用户令 · 2026-11-14 10:3x（**与 designflow 的协作通道已建好 —— 你的「跨线无法驱动」已不再是阻塞**）· 未完成

> **用户原话**：「请你帮助 vision 完成跟 designflow 的工作协调（#3 / #4）」

**一、我已替你打通的三件事**

1. **发现并修掉了一个真问题**：designflow 的 4 个 shard loop 读的是**各自专属任务书**
   `BAIZE_DESIGNFLOW_BENCH_TASK_{A,B,C,D}.md`，而此前「不降级」令写进了 4 shard **共用**的那份
   ⇒ **四个 shard 实际都读不到，指令等于没下发**。现已把协作令写入**四份专属任务书顶部**。
2. **建立了交接区**：`doc/ZhuLong_DAC2027/benchmark/designflow/WAVEVIEW_COLLAB.md`
   —— 含「认领记录 / 交付记录」两张表，designflow 任一空闲 shard 认领后会在表里留痕。
3. **你的交底清单已在位**：`run/reports/waveview_need_image_handoff.md`（α4+β7=11 题），
   协作令里已直接引用它作为 designflow 的输入。

**二、你现在做什么（不要再等）**

你的 #3 / #4 拆成「可并行」与「需等待」两部分，**先做可并行的那半**：

- **✅ 立即可做（不依赖 designflow）**：
  1. **把 Qwen3.5-2B 封装成 VQA tool**（#3 的前半）——定义调用接口（输入：波形图 + 问题；输出：答案），
     跑通单题样例，写清调用方式（供 cline 调用）。这是纯本线工作，**没有理由再等**。
  2. **准备 #4 的训练/合成数据管线**（合成波形图-问答对、SFT 数据格式、RL 奖励设计），
     先用合成数据自测能力基线，**不等 designflow 的用例**。
- **⏳ 需等待**：用 designflow 恢复原形态后的用例做「无 VQA vs 有 VQA」对照。

- **解除阻塞**：🚫 不要再写「单 agent 无法跨线驱动 designflow」——通道已建好，
  designflow 会自己认领；你只需**定期查 `WAVEVIEW_COLLAB.md` 的「交付记录」**，有结果就接上 #3 后半。

---

### 🔴 用户令 · 2026-11-14 09:5x（**口径变更：designflow 不再降级多模态题 → 你的 waveview 结论前提已变**）· 未完成

> **用户原话**：「这样不对，告诉 designflow 复查。对这些需要多模态的题不要降级，暂时没有多模态能力，就让它们 fail。这样才好度量多模态带来的增益。」

**要你知道的三件事**

1. **我已向 designflow 下发复查令**：要求它把「被降级成文本/Tcl」的 waveview 题**恢复原本需要看图的形态**；当前无多模态能力的系统**就该在这些题上 fail**，这是正确行为，不是缺陷。
2. **你上一份报告的结论前提已改变**：报告里「已评测 7 题全 PASS 且全 γ、所以无因看不见波形而失败」——那是因为**题被降级了**。降级取消后，这些题会**重新变成会 fail 的题**，你的 α/β/γ 统计基础需要据此更新。
3. **你要做的事**（不要重复造轮子，等 designflow 复查结果）：
   - 待 designflow 恢复原形态后，**重新统计** waveview 用例的 α/β/γ 分布与新基线通过率；
   - 把这批题作为 **「多模态增益」的度量基准**：`基线 fail → 上 VQA 后 pass` 的差值才是核心指标；
   - 这正是你手上四件事（NeurIPS §6 / 协调 designflow 评 waveview / Qwen3.5-2B 封 VQA tool / 强化识图能力）的**共同前提**。

- **现在可做**：主动与 designflow 对接，把你筛出的 37 题清单里**哪些是"原意图需看图"的**交底给它（它需要据此判断恢复哪些题）。
- **纪律**：🚫 不要再基于"降级后"的数据下结论；更新后的统计要写明数据时点与 designflow 恢复进度。

---

### 🔴 用户令 · 2026-11-14 09:1x（**四件事：NeurIPS §6 刷新 / 协调 designflow 评 waveview / Qwen3.5-2B 封装 VQA tool 对比 / 强化波形识图能力**）· 未完成 · 最高优先

> **用户原话（逐字，共 4 条）**：
> 1.「刷新 `doc/BaiZe-ISEDA2027/BaiZe-NeurIPS2027`，特别是第六节。期望：有想象力&创造力（提醒：它有 cimi-search 这个网搜工具，善用）。」
> 2.「协调空闲的 designflow shard agent(A/B/C/D) 帮忙评测这些 waveview 相关用例」
> 3.「协调空闲的 designflow shard agent(A/B/C/D)，把 Qwen3.5-2B 封装成 vqa tool 给 cline 后，再次评测，写报告对比二者。」
> 4.「在 #3 基础上强化 VQA 工具读懂波形图的能力，使用合成数据/SFT/RL 各种手段，提升基模（Qwen3.5-2B），争取通过率得到显著提升。」

> ⚠️ **本令优先于 idle-spin 处置**：先做这四件，停不停 loop 另议。
> ⚠️ **#2/#3 需要跨线协调**：designflow 是独立线（`doc/ZhuLong_DAC2027/benchmark/`，4 个 shard 共用同一 git 工作区，有严格同步纪律）。**协调方式由你与 designflow 线对接确定**（写协作请求到其任务书/ops 通道，或自行按 `designflow_bench_loop_shard.sh` 口径起评测），**不要违反其「不 clean/reset/stash 别人改动」铁律**。

---

#### ① NeurIPS2027 论文刷新（尤其第六节）

- **文件**：`doc/BaiZe-ISEDA2027/BaiZe-NeurIPS2027/NeurIPS2027/6_domain_rl.tex`（当前 `\section{Semiconductor Domain Adaptation}`，结果仍是 `\textbf{[TBD]}`）；其余 0–7 各节亦在刷新范围。
- **用户要的是「想象力 + 创造力」**，不是把现有文字润色一遍。
- **善用 cimi-search 网搜工具**（用户点名提醒）：检索 2026 年 NeurIPS/ICML/ICLR 相关工作、最新 benchmark、领域适配/偏好学习/波形多模态的前沿方法与可引用数据，把**外部证据**带进正文（每条引用必须真实可查，🚫 不许编造文献）。
- **第六节必须脱掉 [TBD]**：用你已有的真实结果填（waveview 37 题/30 failed/α 13.3%、v5 typecls C=53%>B=37%>A=16% p=0.0009、v6–v11 负结果、Qwen3.5-2B 现状），**负结果也照实写**。
- 判据：编译 0 error；引用可查；无 `[TBD]` 残留（或明确列出仍缺哪些数据、需要什么补）。

#### ② 协调 designflow 评 waveview 用例

- 你已有 waveview 筛选结果（37 题 / 30 failed），**把这份清单作为评测输入**交接给 designflow shard。
- 目标：由 designflow（有 pi_debug 与真实 EDA 环境）**跑一遍这些用例**，拿到**基准口径下的当前通过率**，作为 #3 的对照底数。
- 交付：评测清单 + 环境/口径说明 + 结果表；交接过程与结果写进 MEMORY。

#### ③ Qwen3.5-2B 封装为 VQA tool 给 cline，二次评测并对比

- 把 **Qwen3.5-2B** 封装成「看图答波形问题」的 **VQA tool**（供 cline 调用；模型已在用，见 `run/launch_qwen35_server.sh` 与 `run/longctx_eval_results/`）。
- 由 designflow shard 用**同一批 waveview 用例**再评一遍（**唯一变量 = 有没有 VQA tool**）。
- 交付：**对比报告（中文 HTML）**——两次评测同表并列，明确「哪些题靠 VQA tool 翻转了」，以及**未翻转的为什么**。
- 纪律：两次评测的题目、环境、判据必须一致，否则不可比。

#### ④ 强化 VQA tool 读波形图的能力（合成数据 / SFT / RL）

- 在 #3 的 VQA tool 基础上提升基模（Qwen3.5-2B）的波形识图能力。
- **手段自选**：合成数据、SFT、RL 皆可（你任务书已指定 LLaMA-Factory + KTransformers + LoRA 栈，CPU 可跑，不必等 GPU）。
- **判据（用户明确要）**：**通过率得到显著提升** —— 必须有**对照**（pre / post 同口径、≥3 run，给 mean±std）与**显著性**；负结果照实记录，🚫 不许挑好看的 run 上报。
- 交付：中文 HTML 报告（做了什么 / 数据怎么造 / 训练配置 / 对照结果 / 哪些题翻转过来了 / 下一步）。

---

**统一纪律**
- 所有数字可复算（路径 + 命令）；取不到的标 `TODO/BLOCKED`，🚫 不许估、不许编。
- 报告一律中文 HTML、单文件自包含、0 外链、0 script。
- #1 完成即可先出；#2→#3→#4 是依赖链，按序推进，每步完成即写 MEMORY 心跳。

---

### 🔴 用户令 · 2026-11-14 08:4x（**分析 designflow 评测中的 waveview 用例：哪些 failed 在「有波形图识图能力」下大概率能过**）· 未完成 · 优先于 idle-spin 告警

> **用户原话**：「vision：看下 designflow 做的评测，先筛出 waveview 相关的用例，然后出一份数据分析报告（中文 HTML）。哪些 waveview 相关的 failed case，在有波形图多模态识图能力的情况下，大概率能过。这个比例有多大，请做出有想象力创造力的分析报告。」

- **📌 本条优先于「idle-spin 第 35 轮」告警**：这是一条**新的实质研究方向**，先做完这份报告再谈是否停 loop。
- **数据源（都在本仓，只读）**：designflow 线（`doc/ZhuLong_DAC2027/benchmark/designflow/`）的评测记录 —— 已确认存在下列 wave 线索，请**自己再全量筛一遍**（别只抄这几个）：
  - 深度阅读记录：`trace_deepreads/` 下 `*wave*` / `*fsdb*` / `*openwave*` / `*tranwave*` 等（如 `3qe6x_wavecmp_wrap.md`、`7fcir_openwave_fmt.md`、`as67p_waveview_ace_fsdb_signal_extractor.md`、`1790241096712_s0t3i_waveview_panel_height.md`、`1788919426197_cjcn7_tranwave-repair.md`）
  - 用例台账：`designflow/A.jsonl` / `B.jsonl` / `C.jsonl` / `D.jsonl`（或对应 ledger `*.tsv`）中 task 名/skill 标签含 wave / fsdb / vcd / waveform / waveview / 波形 的条目
  - 调试现场：`.pi_debug/EDA-Eval-DesignFlow-Wave-00x/`、`EDA-Eval-DesignFlow-Analog-004/_waveview_ref.tcl` 等
- **筛选口径（请明确定义并写进报告）**：什么算「waveview 相关」？建议三维判定并给每题的判定依据：
  ① **任务要求**涉及波形文件操作（VCD/FSDB/WLF 解析、信号提取、测量、对比、修复、绘图面板）；
  ② **判据/checker** 需要看波形数值或形状；
  ③ **失败原因**是否与"看不见波形/只能读文本"相关。
  注意：**Aether/纯脚本类**（只改 tcl/python、不涉及波形可视化）不算。

**必做内容（报告五部分）**

1. **筛选结果表**：waveview 相关用例总数 / 其中 passed / failed（给出题名列表与判定依据）；
2. **失败逐个分类**（关键）：把每个 waveview failed case 归到
   - **α 强相关 · 识图可解**：失败直接因为"模型看不到波形形状"（例如判断毛刺/时序错位/眼图/上升沿、从截图里读数值），**给了图像大概率能过**
   - **β 弱相关 · 识图有帮助**：需要波形信息但也可用脚本读数值替代，识图能降低难度但非决定性
   - **γ 不相关 · 识图无用**：失败原因是脚本语法/环境/API/约束理解，与"看不看得见"无关
   **每类给题数、占比、2–3 个具体例证（含 trace 原文摘引 + 路径）**
3. **核心结论数字**：`waveview failed 共 N 题，其中 α(大概率能过) = n 题，α/N = x%；α+β = y%`。**同时给保守/乐观区间**，并说明区间来源（哪几题判不准、为什么）；
4. **"想象力"部分（用户明确要）**：
   - 反事实推演：如果给模型**波形截图 + 数值双通道**，这几题的解题路径会变成什么样？举 2–3 个 case 画出**前后对比的推演流程**；
   - 反向思考：**哪些看起来能过的其实过不了**（例如识图能看出问题但改不对代码）；
   - 延伸机会：这份分析能否反向指导设计 **"waveform-VQA 专项评测集"**？给出题源与构造思路（这是本报告对后续 vision 实验的价值输出）。
5. **可视化**：桑基/堆叠条 or 饼图（α/β/γ 占比）+ 结论卡片。**必须内联 SVG，单文件自包含，0 外链 0 script。**

**纪律**
- 数字全部可复算（路径 + 命令）；拿不到就标 `TODO/BLOCKED`，🚫 **不许编造 case 或 trace 原文**；
- 报告落 `reports/report_vision_waveview_failed_analysis_zh.html`（中文 / 单文件 / 0 外链 / 0 script / 内联 SVG）；
- MEMORY 心跳一行：`waveview分析: 相关=N题 failed=M · α=a(x%) β=b γ=c · 结论=<识图可解比例> · 报告已出`；
- **本报告只做分析，不起训练/实验**（与 idle-spin 处置解耦，处置另议）。

---

> 📦 §用户令·2026-11-06 21:3x（advantage 方差诊断）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#838 判定 PARTIAL（std=0=78.7%/全0=0%/全同档=无信号根因），建议 group_size→8+按目标差异化+奖励连续化(需批)。需要时再读。

> 📦 §用户令·2026-11-06 18:5x（vision 先上 CPU）**✅ 已交付**（wake#827-#835：P0 冒烟 5 步 365s（73s/步）、P1 50 步 ~2min/步、4 个 eval JSON、报告 15058B、EXPERIMENTS §21；结论 post-GRPO 6.2% < post-SFT 9.2% 未提升）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### 📦 §运维令·2026-11-05 17:5x（执行波形 RL 计划：Stage-1W SFT → Stage-2W GRPO · 分阶段）· ✅ 阶段0+阶段1 已交付 → 原文见 `ARCHIVE_OPERATOR_VISION.md`

> **用户令**：「vision：执行 2026-10-31 波形 RL 计划书（`reports/report_vision_wave_rl_plan_zh.html`），让 2B MLLM 通过与 WaveView 交互学会看懂波形图。分阶段，先解锁待核项再训练。」
> **交付进展**：阶段0（WaveView/FSDB 解锁 + Gym 冒烟）✅ · 阶段1 SFT 验收 PASS（format 100%/submit 100%）✅ · Phase2 **CPU pilot 全链路 PASS**（诚实负结果 post-GRPO 6.2% < post-SFT 9.2%）✅ · advantage 诊断 gs4/gs8 双轮 ✅（PARTIAL，离散分档是全同档根因）。**阶段2 正式 GRPO 需 GPU —— 已被 2026-11-07 用户令改为「改用 CPU 重新设计」路线，见顶部新令。** 需要细节读 archive / 各阶段报告。
> 📦 已归档（2026-10-17 ~ 10-26）：ArmA/B/C/D 系列指令 + OCR 三条调研/路线令 + Milestone 报告令 + 08:2x ArmD-R2 整块→ `run/ARCHIVE_OPERATOR_VISION.md`（wake#133/#247/#250/#271/#272/#275/#279 交付）。需要时再读。
### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-17（ArmA 中文报告 + open_clip×AIMv2-style 兼容性评估）**已完成**（wake#133：数字全溯源 EXPERIMENTS §10，不得写「AIMv2好 9pp」）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> 不得回退：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---

> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。

> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）

- 🚫 不许闭门造车：涉及"别人怎么做"（架构/loss/评测/数据）必须去读官方仓库或论文原文（能 clone 就 clone）—— 不得凭二手描述下结论（本线已因此出错一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂必须报「参数量 + 训练 token + 每步耗时」，不许只比 acc。
- 预注册：判据先定后测，不许事后改。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
