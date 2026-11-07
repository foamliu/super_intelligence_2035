# BAIZE_VISION_TASK.md

### 🔴 用户令 · 2026-11-07 10:10（**阶段2 放行：不再等 GPU，在 CPU 上放开试各种 idea**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「vision 阶段 2：放行，可以基于 CPU 大胆尝试各种 idea。」

#### 0. 本条令解决了什么（先读）

此前两轮诊断（gs4 `std=0` 占 78.7%，gs8 占 73.0%）得出：瓶颈是**离散分档奖励 + 部分目标能力缺口**，不是算力。运维已把这 2 项上报用户，**用户现已批准**，即：阶段 2 的技术路线**不再需要逐项等审批**。

#### 1. 已授权的变更（可直接执行，无需再问）

| 序号 | 变更 | 说明 |
|:--|:--|:--|
| 1 | **奖励连续化** | `R_main -> exp(-rel_err/tau)`（或等价连续形式）替代 5 档离散；tau 需给标定理由 |
| 2 | **按目标差异化** | period（信号足）先上 RL；rise_time / duty_cycle（能力缺口）走 SFT 补数据或改任务定义 |
| 3 | **换基座** | 用户指定 Qwen3.5-2B；允许与旧基座做对照 |
| 4 | **改任务定义** | 允许改为可判定的中间任务（波形类型判别 / 两波形频率比较 / 异常点定位等），只要对下游有意义 |
| 5 | **推翻旧 plan** | 允许推翻 `report_vision_wave_rl_plan_zh.html` 的假设与路径 |
| 6 | **放开 idea** | 允许基于 CPU（.12/.29）大胆试各种 idea（数据合成 / 课程学习 / 过程奖励 / 相对排序奖励 / 蒸馏等），不做"等 GPU"的空转 |

#### 2. 仍然必须守的纪律（不可放宽）

1. **改奖励/改任务 = 改目标函数 -> 必须先写新判据再跑**。禁止"看到结果再调判据"。
2. 每轮必须有**对照**：pre-SFT / post-SFT / post-RL 三档同口径，多次重复（>=3 run）给 mean + std。
3. **负结果如实记录**（沿用 post-GRPO 6.2% < post-SFT 9.2% 的诚实口径），禁止挑好看的 run 上报。
4. **CPU pilot 结论不得外推成 GPU 结论**；报告里标注算力与规模。
5. 每轮交付：JSONL/指标 + EXPERIMENTS 段落 + （阶段性）HTML 报告，commit 前缀 `vision rl:`。
6. 体积：任务书 >32KB 时先归档**已闭合**块，本令未完成期间不得归档。

#### 3. 建议的推进节奏（可自调，但要写进心跳）

- 第 1 轮：连续化奖励 + period 单目标，Qwen3.5-2B + LoRA，CPU，小规模 pilot（先证明 std>0 的比例显著上升）。
- 第 2 轮：多目标（period + amplitude）与课程学习；同时起 rise_time/duty_cycle 的 SFT 数据补齐。
- 第 3 轮：与 SFT-only 基线做配对检验（>=3 run），给显著性结论。
- **连续 3 轮无提升**：必须换方向，并在心跳里写明换的理由与证据。

---


### 🔴 用户令 · 2026-11-07 09:2x（**走出「干等 GPU」——用现有 CPU 资源（.12/.29）设计有效 RL，证明显著提升 Qwen3.5-2B 的波形理解**）· 用户直令 · 最高优先 · ⚠️ 未完成

> **用户原话**：「鼓励 Vision 用 CPU 做后续的探索，走出高 ROI 的新路来；**不要干等 GPU**。千方百计证明经过精心设计的 RL 后，MLLM 在波形识别方面有显著提升。请它自行调研 hf.co 等网站，看有没有波形评测的现成数据集。就是争取在现有资源（.12/.29 的 CPU），设计有效的 RL 方案，应用在 Qwen3.5-2B 上，证明显著提升它看懂波形图的能力。」

#### 0. 这条令的核心意图（先读懂）

> 🆕 **技术路线（用户 2026-11-07 追加·指定的新路）**：**LLaMA-Factory + KTransformers 后端 + LoRA + 2B 模型（Qwen3.5-2B）**。
> 用户原话：「vision 的训练实验，建议 LLaMA-Factory + KTransformers 后端 + LoRA + 2B模型（Qwen3.5-2B），走出一条新路来。**不要'等靠要'**。」
>
> ⚠️ **这套栈在本仓库里是全新的**（`grep KTransformers|LLaMA-Factory` 全仓 0 命中，此前从未用过）。运维侧无法代为验证其在本环境（conda `py310` / PyTorch 2.8 / transformers 5.x）的兼容性 —— **需要你先做可行性冒烟，再决定是否采用**。若发现不兼容，**如实说明并给替代方案**，🚫 不要为了"用上这个栈"而硬凑，也🚫 不要因为不熟就放弃不用。
>
> 📌 **已知可复用的既有资产**：Vision 线**已经跑通过 LoRA**（wake#741：`_cpu_train_validate.py` 7/7 PASS，**LoRA 69.7M**，loss 单调下降，CPU 端到端训练循环验证通过）。⇒ LoRA 这条路本身是通的，**新栈的价值在于工程化 + KTransformers 的 CPU 推理加速**，不是从零开始。

| | 内容 |
|:--|:--|
| **🚫 不要做的** | 「等 GPU 释放（ETA 12/25）→ 跑原计划 Stage-2 → 写报告」。**这条老路已经走不通**，见 §1。 |
| **✅ 要做的** | 用 **.12/.29 的 CPU** 这个现有资源，**重新设计**一条能出结果、能证明显著提升的 RL 路径。 |
| **成功判据** | 让 **Qwen3.5-2B** 在波形理解上**显著提升**（要有对照、有统计、能证伪）。 |

> 💡 **「鼓励」不是空话**：允许你**推翻**之前 plan（`report_vision_wave_rl_plan_zh.html`）里的假设与路径，允许更换基座（Qwen3.5-2B 是用户指定）、允许重新定义任务与奖励。**只要能证明提升，方法你自己定。**

#### 1. 必须先正视的既有事实（别重复踩）

- **CPU 上已经跑过一轮 GRPO**（wake#827-835，`--smoke`→pilot 50 step）：结果 **post-GRPO 6.2% < post-SFT 9.2%**（诚实负结果，已记录在案）。⇒ **不是「没 CPU 所以跑不了」，而是「按原方案跑 CPU 也没效果」。**
- **advantage 方差诊断已做两轮**（gs4：std=0 占 78.7%；gs8：73%，仅降 5.7pp）：根因 = **离散分档奖励导致「全同档 = 无信号」**，而非「全 0」。
- 按目标拆：**rise_time 100% 全错**（能力缺口，G 加大无效）、**duty_cycle 91.7% 全错**、**period 仅 21.7%**（信号足，可上 GRPO）。
- 结论：**原奖励设计是主要瓶颈**，不是算力。所以「等 GPU」并不能解决问题 —— 这也正是用户说「不要干等 GPU」的原因。

#### 2. 要你做的事（四块，可并行）

**① 调研现成数据集（用户明确要求）**
- 自行到 **hf.co / GitHub / arXiv** 检索**波形/信号图/时序图 VQA 评测集**，例如方向：plot/chart 理解（ChartQA、PlotQA、FigureQA）、示波器/波形图、时序图 QA、EDA 波形截图。**有现成的就别自己造。**
- 每个候选给：`repo id / 体量 / license / gated / 字段结构 / 是否含波形类 / 可用性`。拿不到写「未核到」，🚫 不许编造。
- 明确回答：**能否直接用于我们「波形识别」任务？** 若不能，能否**迁移**（改造成波形语境）？

**② 重新设计奖励与任务（核心，这是高 ROI 的地方）**
- 针对 §1 的根因，**重新设计奖励**，方向自选，例如：**连续化**（`exp(-rel_err/τ)` 替代离散分档）、**分目标差异化**（period 先上、rise_time 补 SFT/不做 RL）、**过程奖励**、**相对排序奖励**。
- **任务定义也可改**：如果「读数」太难，可以改成**可判定的中间任务**（如「判断波形类型」「比较两波形哪个频率高」「指出异常点」），只要能证明能力提升且对下游有意义。
- ⚠️ **必须重新预注册判据**（改奖励=改目标函数，判据要跟着变；🚫 不许看到结果再调判据）。

**③ 用 Qwen3.5-2B 落地（用户指定基座 + 指定技术栈）**
- 基座换成 **Qwen3.5-2B**（用户明确），说明与之前基座的差异与理由。
- **技术栈（用户指定）**：`LLaMA-Factory` 做训练编排 + `KTransformers` 做后端 + `LoRA` + Qwen3.5-2B。落地前**先做三步冒烟**（每步不过就停，别硬推）：
  - **S1 环境**：装 LLaMA-Factory 与 KTransformers，确认与现有 conda `py310`（PyTorch 2.8 / transformers 5.x）**不冲突**（建议独立 venv/conda env，🚫 别污染现有环境）。
  - **S2 单步训练**：LLaMA-Factory 能否在 **CPU** 上跑起 Qwen3.5-2B 的 LoRA 单步（`--use_cpu` 或等价开关），loss 正常下降。
  - **S3 后端联动**：KTransformers 在此栈中的角色要**说清楚** —— 它是**推理加速后端**（用于 rollout/评测）还是**训练后端**？若只做推理加速，那"训练用 LLaMA-Factory + rollout 用 KTransformers"就是合理的两段式；若无法在 CPU 上做训练，**如实说明并退回 LoRA(peft) 直训**（已有 69.7M adapter 的成功先例）。
- **CPU 上能跑多大规模就做多大**：LoRA/小参数量微调、小 step 数、小 batch，**先证明方向有效，再谈规模**。
- 若判断「CPU 上 Qwen3.5-2B 训练不可行」，**如实说明并给替代方案**（如：只用 CPU 做数据/评测/推理，训练等 GPU；或改用更小可训模块），🚫 不要硬扛也不要不做。
- 🚫 **不许「等靠要」**：不要写「等 GPU 到了再试」作为结论。CPU 上能验证到哪一步就做到哪一步，把边界说清楚。

**④ 严格的证伪设计（用户要的是「证明显著提升」）**
- 必须有 **before/after 对照** + **统计检验**（McNemar / bootstrap CI）+ **控制组**（如空转 RL、随机奖励）。
- **必须报 cheat rate / 数据泄漏检查**（波形图若来自同一 FSDB，极易泄漏）。
- 🚫 **不许**只说「提升了」而不给基线与显著性；🚫 **不许**把 infra 问题算成能力提升。

#### 3. 护栏

- 🚫 **不碰 GPU**（.12/.29 的 H100 全给 S1 训练）；CPU 使用降载 `nice -n 19`、控线程数，**别把机器打爆**（同 pretrain 令：224 核跑满会崩，设上限）。
- 🚫 不打断 S1 训练与他线进程。
- WaveView/FSDB 合规沿用既有约束（沙盒隔离、只读、license 并发不超）。
- 🚫 不编造数据集/论文/数字；拿不到标「未核到」。
- commit 前缀 `vision cpu-rl:`；TASK/MEMORY ≤32KB。

#### 4. 交付

- **调研**：现成波形/图 VQA 数据集清单（含可用性判断 + 迁移方案）。
- **技术栈可行性**：LLaMA-Factory + KTransformers + LoRA + Qwen3.5-2B 在 CPU 上的三步冒烟结论（S1 环境 / S2 单步训练 / S3 后端角色），**若不兼容给出原因与替代路径**。
- **方案**：新 RL 设计文档（奖励 + 任务 + 预注册判据 + 为什么这次能work 而上次不行）。
- **实验**：CPU 上的 before/after 结果表 + 显著性 + cheat rate。
- **中文 HTML 报告**（`reports/report_vision_cpu_rl_waveform_zh.html`，单文件 0 script 0 外链）：必须诚实报告结果 —— **若仍无显著提升，也要写清「为什么」和「下一步该怎么做」**，负结果同样有价值。

> **完成标记**：数据集调研 + 新 RL 方案 + CPU 实验（含对照与显著性）交付 ⇒ 本行改 `✅ 已交付`；未完成 ⇒ `WAITING: 0`。
> ⚠️ **不要为了「已交付」而挑软指标**：宁可交付一个诚实的「这方向 CPU 上做不到，需要 X」，也不要粉饰成「显著提升」。

---

> 📦 §运维令·2026-10-31 16:0x（ViT-L 68.236% + MLLM 26.10% 写进论文 ch6/ch7/摘要/intro）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#441+#442 交付 4 .tex 改稿 commit 1a2e19b2f，6页/ERR=0/UNDEF=0，数字全溯源 armE_r2 JSON + EXPERIMENTS §15.5，MME 用 ArmE-R2 实测值。需要时再读。

> 📦 §运维令·2026-10-31 11:2x（直接重写第6章 6_vision_encoder.tex）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#437+#439 交付 18行/6页/ERR=0/UNDEF=0 + report_vision_paper_edit_zh.html，commit f2ca45de5/e5145dc85。需要时再读。



> 📦 §运维令·2026-10-31 11:0x（审校第6章出修订计划）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#436 交付 report_vision_paper_revise_plan_zh.html，已被 11:2x 令升级为直接改稿并执行完毕。需要时再读。



> 📦 §运维令·2026-10-31 08:4x（波形图强化RL计划书）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#435 交付 report_vision_wave_rl_plan_zh.html 59241B/12节，覆盖9个必答问题+WaveView API实测事实引用。需要时再读。



> 📦 §运维令·2026-10-30 22:2x（写「2B MLLM 看懂波形图」能力与评测报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#424 交付 report_vision_waveform_zh.html 45236B/6节/14表，覆盖任务定义/能力拆解/数据/训练/评测/成本ETA。需要时再读。

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 📦 §用户令·2026-11-06 21:3x（advantage 方差诊断）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#838 判定 PARTIAL（std=0=78.7%/全0=0%/全同档=无信号根因），建议 group_size→8+按目标差异化+奖励连续化(需批)。需要时再读。


> 📦 §用户令·2026-11-06 18:5x（vision 先上 CPU）**✅ 已交付**（wake#827-#835：P0 冒烟 5 步 365s（73s/步）、P1 50 步 ~2min/步、4 个 eval JSON、报告 15058B、EXPERIMENTS §21；结论 post-GRPO 6.2% < post-SFT 9.2% 未提升）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### 📦 §运维令·2026-11-05 17:5x（执行波形 RL 计划：Stage-1W SFT → Stage-2W GRPO · 分阶段）· ✅ 阶段0+阶段1 已交付 → 原文见 `ARCHIVE_OPERATOR_VISION.md`

> **用户令**：「vision：执行 2026-10-31 波形 RL 计划书（`reports/report_vision_wave_rl_plan_zh.html`），让 2B MLLM 通过与 WaveView 交互学会看懂波形图。分阶段，先解锁待核项再训练。」
> **交付进展**：阶段0（WaveView/FSDB 解锁 + Gym 冒烟）✅ · 阶段1 SFT 验收 PASS（format 100%/submit 100%）✅ · Phase2 **CPU pilot 全链路 PASS**（诚实负结果 post-GRPO 6.2% < post-SFT 9.2%）✅ · advantage 诊断 gs4/gs8 双轮 ✅（PARTIAL，离散分档是全同档根因）。**阶段2 正式 GRPO 需 GPU —— 已被 2026-11-07 用户令改为「改用 CPU 重新设计」路线，见顶部新令。** 需要细节读 archive / 各阶段报告。
### [已归档] §运维令·2026-10-26 08:2x（写最近工作报告 · 中文 HTML）**已完成**（wake#279 交付 `reports/report_vision_recent_work_zh.html` 40423B/5节/0 script/0 外链）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维令·2026-10-25 22:4x（生成 1000 万 OCR 图文对）**已完成**（wake#275：9,999,999 对/2000 shard/470GB；去重 2.4486%、泄漏 113 已如实披露；用户已裁定 accept-as-is）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维令·2026-10-25 19:5x（路线①细化为执行方案报告）**已完成**（wake#272 交付 report_vision_ocr_sft_plan_zh.html 22,706B/9节）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维令·2026-10-25 17:5x（OCR 类评测偏低：OCR 合成数据调研）**已完成**（wake#271 交付 report_vision_ocr_synthdata_zh.html 29177B/8节）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维指令·2026-10-24 16:1x（写「下一步如何提升 ProtB 与 MLLM 成绩」报告）**已完成**（wake#250 交付 `reports/report_vision_next_steps_protb_mllm_zh.html` 21.1KB / 8 节 / 0 script / 0 外链，后续 A3 + B4 已执行）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

### [已归档] §运维指令·2026-10-24 10:3x（ArmE-R2 完整实验报告）**已完成**（wake#247 交付 `reports/report_vision_armE_r2_20261024_zh.html` 26,522B / 7 节；wake#267 复核仍在位）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

> **已归档**（2026-10-24 11:43）：ArmE 停止降 LR 重跑 / 启动 ArmE（ViT-L14）/ Stage-2 改原版 780k 三块 —— 原文均在 `run/ARCHIVE_OPERATOR_VISION.md`。


### 📦 运维指令 · 2026-10-20 08:2x（**ArmD-R2：LR 1e-3 / min_LR 1e-5 / 数据不变**）· 用户直令 · 最高优先 — 已归档

> **已闭合**（ArmD-R2 全链路 DONE 2026-10-21：①训练✅63400步 / ②ProtB✅lp64.3373·5-NN55.956 / ③MLLM三阶段✅Stage-2原版数据 / ④12集✅avg26.12% / ⑤报告✅）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-21 归档）。**结论**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp/Δ5-NN+1.238pp 双双正向；MLLM下游几乎持平→ProtB→MLLM传递性再次证伪。ArmD-R2 是 ArmE 的对照基线（口径值见上方 ArmE 块口径表）。需要时再读。
> **已归档**（2026-10-24 11:43）：🔥 运维令 · 2026-10-19 22:5x（**立即启动 ArmD，不要再 idle**）· 用户直令「vision：尽快启动」 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 📦 已归档（08:2x）：ArmD 原始块（2026-10-19 21:2x）

> 已被 **08:2x「ArmD-R2」块**取代（LR 2e-3→1e-3，数据不变）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

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


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

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

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ 21KB、`MEMORY_VISION.md` ≈ 32KB（已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_VISION.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的巡检/流水条目（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
