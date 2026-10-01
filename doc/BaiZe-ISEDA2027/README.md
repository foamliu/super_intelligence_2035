# BaiZe (ISEDA 2027) — 项目总纲 / Project README

> 本文件是 BaiZe 的**工作总纲**：定位、已完成实验、关键数字、评测协议、各阶段规划与风险清单。
> 论文本体在 `BaiZe-ISEDA2027/`；实验记录在 `run/`；对外报告是根目录的 `*.html`。
>
> ⚠️ 带 **[TBD]** 或 **⚠️** 的条目是**尚未确认/尚无数据**的，不要当成结论引用。

---

## 0. 一句话定位

> **ZhuLong 证明"harness 是主要矛盾"；BaiZe 证明"主要矛盾解决之后，参数规模不再是主要矛盾"。**

两篇论文是**互补而非竞争**关系，互为引用。

| | ZhuLong | BaiZe |
|---|---|---|
| 会议 | DAC 2027（arXiv 2608.07925） | ISEDA 2027 |
| 是什么 | Execution-grounded EDA coding agent（PyAether / SKILL / Tcl） | 从零训练的 ≈2.2B Mamba-2/attention 混合语言模型 |
| 核心论点 | EDA 正确性是**情境化**（situated）属性；grounding gap 受**观测保真度**约束，**不受模型规模**约束 | 在 harness 冻结、观测保真度相同的条件下，小模型也能逼近大 backbone 的效果，且推理成本低一个量级 |
| 手段 | MCP 三工具（`search_apis` / `get_api_details` / `run_code`）+ generate–execute–refine 闭环 + 离线 API 自探索 | 领域语料 → 混合架构 → 预算受限搜索 → SFT/RL → 多模态对齐 |
| 关系 | 提供 **harness 与评测基准** | 提供 **被评测的 backbone 与"降本"结论** |

**叙事链**：ZhuLong 找到瓶颈（观测，+几十 pp）→ BaiZe 回答"瓶颈解决后模型能压到多小"。

**BaiZe 的机会（核心命题）**：
MiniCPM5-2B 的 **36% 是在"零领域自适应、零 EDA RL"的通用模型上取得的**——它没训过 pyAether API、
没训过 generate–execute–refine 闭环、没为 EDA scripting 做过任何 RL。因此
> **36% 是"未适配下限"，不是"2B 的能力上限"。**

BaiZe 的贡献因此可以定义为：**这 58 pp 里，有多少是靠"领域自适应 + RL"可以回收的、代价是多少。**
这是一个**无论结果落在哪都有价值**的研究问题（回收得多 → 强结果；回收得少 → 支持"规模非瓶颈"论，与 ZhuLong 互证）。

---

## 1. 关键数字（当前已实测）

### 1.1 预训练 Stage (i) — 已完成

| 项 | 值 | 出处 |
|---|---|---|
| 架构 | Mamba-2 hybrid，56 层（其中 **4 层 attention**） | `3_architecture.tex` tab:config |
| 参数量 | **2.22B**（实测 `sum(numel())` = 2,220,268,032） | `EXPERIMENTS_2B.md` |
| tokenizer | DeepSeek-V4.1-Flash，vocab **129,281** | `4_llm_pretrain.tex` |
| 数据 | Ultra-FineWeb-L3(EN) 1.8T + code 1.2T + math 515G，seq 4096，packing | 同上 |
| 胜出配置 | LR **1e-3** / WSD / warmup **250** / decay **500** / min_lr **1e-5** / 退火 **86:10:4** | `BAIZE_PRETRAIN_RESULT.html` |
| val loss @5000 步 | **2.7647** | 同上 |
| final loss @20000 步 | **2.2054**（退火增益 ~0.14） | 同上 |
| 3-seed 复现（5000 步） | **2.6739 ± 0.0469**（n=3；2.6402 / 2.6539 / 2.7275） | 同上 |
| 预算 | 计划 ~92 GPU·h，实际消耗 **~85 GPU·h**（8×H100） | `4_llm_pretrain.tex` §Search Budget |
| 步数口径 | S1–S4 = 5000 步（≈164M tok，≈4.0 GPU·h/次）；S5 = 20000 步（≈655M tok，≈13.9 GPU·h） | 同上 |

> ⚠️ **训练量极小**：20000 步 × 32.7K tok/步 ≈ **655M tokens**，只占数据池 1.8T 的 **0.036%**；
> 架构对比更是只跑 1000 步 / 24.6M tokens。所有 loss 数字都是"早期收敛快照"，不是收敛值。

### 1.2 架构选型对比（Stage i 决策依据）

| 指标 | Dense (MiniCPM5-2B) | Hybrid (BaiZe) | 优势方 |
|---|---|---|---|
| 参数量 | 2.512B | **2.220B** | hybrid（−11.6%） |
| final loss @1000 步 | 4.8065 | **4.6846** | hybrid（−0.12） |
| 训练 tok/s | **~89K** | ~72K | dense（+24%） |
| prefill tok/s | 21,436 | **23,692** | hybrid（+10.5%） |
| decode tok/s | 2.21 | **22.77** | hybrid（+10.3×）⚠️ |

> ⚠️ **decode 的 10.3× 是测量口径产物**：Megatron-Core 直驱（无 CUDA-graph/flashinfer）下，
> dense 侧是 **CPU-launch-bound**（`Self CPU≈620ms` vs `Self CUDA≈4.05ms`，纯 GPU 上界 ≈250 tok/s）。
> 生产级推理栈下该差距会大幅收窄。**论文表格标题已加入此限定。**

### 1.3 视觉编码器 Stage (iii) — 已完成（但未验证，见 §6）

四候选同参（500–600M）、全部随机初始化、统一 open_clip 3.2.0 + SigLIP + 冻结文本塔：

| 架构 | 参数 | 类型 | Loss@5k | 训练 img/s | 推理 ms/img |
|---|---|---|---|---|---|
| **OpenVision2** | 505.0M | Attention | **4.456** | **2139** | **6.51** |
| DeepEncoderV2 | 516.9M | Attn+SSM | 4.466 | 1459 | 17.76 |
| MambaEye | 534.9M | SSM | 4.470 | 790 | hang@bs1 |
| MoE-ViE | 505.2M（222M active） | MoE | 4.466 | 852 | 141.7 |

**消融**：分辨率/patch 六档 loss **全为 4.9962**（cosine 在 step~700 坍缩到 1e-5 所致）；
lr 扫描 1e-3→4.9962、**3e-3→4.4562**、5e-3→4.4542。

> 🚨 **该阶段实际上未被验证**：编码器从未训到收敛（所选 lr 使 loss 钉在地板），
> 下游只有通用检索代理，无真正 EDA 下游指标。**做 Stage (iv) 前必须先修**（见 §6）。

### 1.4 EDA 下游评测 — **这是当前最关键的一张表**

基准：**EDA-Eval-PyAether（158 任务）**，Pass@1。

| Backbone | Pass@1 | 配置 | 状态 |
|---|---|---|---|
| DeepSeek-V4-Pro + **full harness** | **94.0%**（5-run mean；范围 93.0–95.4%，±~1.2 pp） | `-p 8 -n`，Sep 14–15 | ✅ 已测 |
| **MiniCPM5-2B** | **36%** | ✅ **full harness**（与 94.0% **同口径**） | ✅ 已测 |
| **BaiZe**（20000 步 ckpt） | **[TBD]** | 待测 | ⬜ **最高优先级** |

> 🎯 **同口径差距 = 94.0% − 36% = 58 pp —— 这 58 pp 就是 BaiZe 的研究对象，不是"坏消息"。**
> - **36%（MiniCPM5-2B）**：通用模型，**未做 EDA 领域训练、未做 EDA RL、未适配工具闭环** → **"未适配下限"**
> - **94.0%（DeepSeek-V4-Pro）**：**已接近饱和**，几乎没有上升空间
> - ⇒ 二者之差，**有多少是"领域自适应 + RL"可回收的**，就是本论文要回答的问题（见 §4 Stage ii 的成功阶梯）
>
> ⚠️ **有效性前提**：36% 与 94% 必须**同分母**（Pass@1 是在全部 158 上算，还是在"生成成功子集"上算？）——
> 两模型分母不同则 58 pp 不可比。见 §6 风险 #0b 与 §7.0 假差距 C。

> 🚨 **论文旧值已失效**：`78.5% / 84.8%`（全系统）与 `23.6% / 11.4%`（裸 LLM）是旧协议下的数字，
> ZhuLong 自己的 `run/eval/README.md` 已明确标注"**已失效**，将在 EDA-Scripting-Bench 上全量重测"。
> **引用前必须确认口径**，目前可信锚点是 **94.0%**。

---

## 2. 评测协议（沿用 ZhuLong，**冻结项不得改动**）

| 项 | 规定 |
|---|---|
| 基准 | EDA-Eval-PyAether，**158** 任务（jsonl，每行一 task） |
| 任务三要素 | 自然语言 prompt + 函数签名（`entry_point`）+ **断言式测试代码** `test`（内含 `check(candidate)`） |
| 任务粒度 | **函数级**：agent 实现 `entry_point`；**不是**"建库建图改设计"的 `run()` 风格 |
| 通过判据 | 代码在 PyAether sandbox 中**无错误执行**且**全部断言通过** |
| 指标 | `Pass@1 = 通过任务数 / 158 × 100%` |
| 单次超时 | **2500 秒** |
| 单 trace 原则 | 一任务只跑一条 trace，trace 内可反复迭代，**绝不跨 trace 重启** |
| 重复次数 | 每配置 **5 次独立运行**，每次重排任务顺序 + 全新 agent context；报 **mean ± std**（另报 `Pass^5`：task 级 5/5 全过） |
| 并发 | `-p 8`（8 并发）；**`-n`**（禁用 Memory Bank 注入） |
| 反作弊 | **`PreToolUse` hook 全程启用，且所有实验臂完全一致**——它是**冻结变量，不是消融对象** |
| 跑法 | `cd $BASE_DIR && bash scripts/run_cline_script.sh -p 8 -n`（约 **3 小时/轮**） |
| 打分 | `python scripts/run_eval.py -g <generated>.jsonl`；或直接取 log 内 `pass (xx.x%)` |

**工具集**（`_TOOL_DEFAULTS` + `.env` 的 `EDA_MCP_TOOLS_ENABLED`）：

- **核心 4 工具恒开**：`get_api_details` / `search_apis` / `search_apis_by_keyword` / `run_code`
- **扩展 3 工具（消融对象）**：`cimi_search` / `cimi_fetch` / `vqa`（当前默认**关闭**）

**任务场景分布**：Layout 64（40.5%）/ Schematic 47（29.7%）/ Design Management 24（15.2%）/ Others 23（14.6%）
**任务来源**：API 参考 61.4% / 文档示例 27.2% / 内部培训材料 7.6% / 脱敏 CAD 案例 3.8%

---

## 3. 集成方式（换 backbone 的成本 ≈ 0）

harness 通过 **OpenAI 兼容接口**接模型，因此 BaiZe 只要暴露一个 OpenAI-compatible endpoint 即可直接评测，**无需改 harness**：

```bash
# 切 backbone（ZhuLong 既有命令形态）
cline auth -p openai -k <API_KEY> -b <BASE_URL> -m <MODEL_ID>
```

现有 backbone 锚点与待测模型：

| 角色 | 模型 | 说明 |
|---|---|---|
| **主基座（锚点）** | `deepseek-v4-pro-fp4` | 已有 5-run 锚点（full×5），**不重跑** |
| 对照（大模型） | `glm-5.2` / `deepseek-v4-flash` / `kimi-k2.6-cloud` / `doubao-seed-2.0-pro-cloud` | ZhuLong 的 S3 模型消融 |
| 对照（同量级） | `MiniCPM5-2B`（36%）/ `MiniCPM5-1B` | BaiZe 必须超过这个数才有意义 |
| **待测（本论文）** | **BaiZe-base / -SFT / -RL** | 通过本地推理栈（vLLM/SGLang）暴露 OpenAI API 接入 |

**关键路径（关键资产清单）**：

| 组件 | 位置 |
|---|---|
| 代码生成 driver | `/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh` |
| 评分 | `/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py` |
| 评测框架 | `/nasdata/app.e0031982/code/EDA-Eval-Framework` |
| 158-case 数据集 | `eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl` |
| `BASE_DIR` | `/nasdata/app.e0031982/code/eda_fastmcp` |

---

## 4. 各 Stage 规划

### Stage (i) LLM Pretraining — ✅ 已完成
见 §1.1 / §1.2。

### Stage (ii) LLM Post-Training — ⬜ 待做（**当前主攻方向**）

**主张**：harness 冻结、观测保真度相同的前提下，2.2B 领域自适应模型逼近大 backbone 的效果。

**四段式**（★ = 相对早期方案的调整）：

0. **继续预训练 / 领域退火（EDA 语料）** ★
   - 🚨 **为什么这一步是必须的**：BaiZe 当前预训练语料是 `Ultra-FineWeb-L3` + code + math，
     **完全不含 EDA / HDL / PyAether 数据**。也就是说——
     > **BaiZe 在预训练层面同样不是领域模型。** 「领域模型」这个 claim 目前**完全压在 Stage (ii) 上**。
   - 做法：**直接复用 Stage (i) 已成熟的 WSD + 领域退火机制**，在 PyAether API 文档 / EDA 脚本语料上做继续预训练。
   - 收益预期：**这是最便宜的大杠杆之一**——预训练层的领域注入比 SFT 更根本（改的是先验，不只是行为）。
     且**顺带修掉论文"标题/引言声称 EDA、但训练数据里没有 EDA"的题材漂移问题**（此前后续 review 已指出）。
   - 消融：退火语料配比（通用 / code / **PyAether**）、退火步数、**只做 SFT 不做继续预训练（对照组）**
1. **SFT（前置，便宜）**
   - 数据：`UltraData-SFT-Agent`(51G) 打底 + **PyAether 领域语料**（来源：ZhuLong 已整理的 API 参考文档，占任务来源 61.4%）
   - **消融**：数据混合（agentic / +code / +math / **+PyAether API 语料**）；含 CoT+工具轨迹 vs 纯代码；LoRA vs 全参；**上下文长度 4096 vs 8192**
   - 🚨 **前置硬约束**：当前 `seq_length = 4096`，而 agentic 轨迹（代码+工具返回+多轮 refine）**极易超长**。
     预计**需先做长上下文适配**，否则 RL rollout 被截断、信号失真。
2. **RL（核心）**
   - 算法：**RLVR + GRPO**（奖励天然可验证，无需 reward model；GRPO 无 value model，显存友好；Nemotron-H reasoning 亦用 GRPO，血统一致）
   - **奖励设计 = 最重要的消融（≥4 臂）**：
     | 臂 | 奖励 |
     |---|---|
     | R1 | 二值 pass/fail |
     | R2 | 部分分：可执行 + 断言通过率 |
     | R3 | R2 + 工具调用次数惩罚（对齐 ZhuLong 的 −22.1% 工具削减） |
     | R4 | R3 + API 合法性奖励（抑制幻觉 API） |
   - 🚨 **Reward hacking 是最大风险**：必须挂 anti-cheat 并**单独报告 cheat rate**（模型试图绕过断言的比例）
   - ⚠️ **预算口径要换**：带沙盒执行时是**沙盒时延 bound，不是 GPU bound**（单次执行超时 2500s）。
     规划按"沙盒并发数 × 墙钟"算，**不能沿用 GPU-hour 口径**
3. **评测（⚠️ 口径必须改）**
   - **不要只报"BaiZe-RL 的 pass@1"**，要做 **backbone × harness 网格**，harness 侧用冻结配置：

     | Backbone | pure LLM | +RAG | +Sandbox | full |
     |---|---|---|---|---|
     | DeepSeek-V4-Pro | [TBD] | [TBD] | [TBD] | **94.0%** |
     | MiniCPM5-2B | [TBD] | [TBD] | [TBD] | **36%**？|
     | **BaiZe-base / -SFT / -RL** | [TBD] | [TBD] | [TBD] | [TBD] |

   - 三个卖点：**纵向**（RL 增益几个 pp，诚实报告）/ **横向**（同 harness 下 vs DeepSeek 的 pass@1 与成本）/ **补洞**（BaiZe 全篇缺下游指标）
4. **预注册的成功阶梯**（**先定后测**，避免事后合理化）

   | 里程碑 | Pass@1 | 含义 | 先验判断 |
   |---|---|---|---|
   | 起点 | **36%** | MiniCPM5-2B，通用模型，**零适配** | ✅ 已实测 |
   | M1 | **50%** | 工具协议修好（D1/D2/D6 改善） | 几近必然 |
   | M2 | **65%** | + 领域继续预训练 + SFT | 大概率 |
   | M3 | **75%** | + RL | 有望，已是强结果 |
   | M4 | **85%+** | 逼近 DeepSeek-V4-Pro | 惊喜级别 |

   > **阶梯的意义**：无论落在哪一档，结论都能成立且都值得发表——
   > 落在 M3/M4 是"小模型 + 领域自适应逼近大模型"；
   > 落在 M1/M2 则是"**领域自适应的可回收空间有限**"，**直接支持 ZhuLong「规模非瓶颈」的论点**，两篇互证。
   > **先写下这张表，再开始训练。**

### Stage (iii) Vision Encoder — ✅ 已完成但**未验证**（见 §6）

### Stage (iv) MLLM Alignment — ⬜ 待做
- **前置**：先修视觉编码器（lr=3e-3 重训到收敛 + 加 EDA 下游指标），否则效果差时无法归因
- 数据/任务（都能接回 EDA-Eval 口径）：
  | 任务 | 输入 → 输出 | 备注 |
  |---|---|---|
  | **图→脚本** | layout 截图 → PyAether 脚本 | **最强**：可直接用 ZhuLong 断言 harness 打分 |
  | 脚本→图 | 代码 → 预测渲染布局 | 执行即得配对数据，可自动构造 |
  | 版图 VQA | 图 → "这层是什么/哪里违反 DRC" | 需专家标注 |
- 消融：projector（MLP vs Q-Former）/ 视觉塔冻结 vs 解冻 / **每图视觉 token 数** / 三阶段课程配比
- ⚠️ 224/16 下每图仅 **196 token**；版图/原理图细节密集，**分辨率在 (iv) 很可能重新变成关键变量**（与 (iii) 结论不矛盾，任务不同）

### Stage (v) Semiconductor Domain Adaptation — ⬜ 待做
**必须先与 (ii) 划清边界**，建议按**奖励来源**切分：

| | Stage (ii) | Stage (v) |
|---|---|---|
| 模态 | 纯文本 | **多模态**（版图/原理图 + 脚本） |
| 奖励来源 | **可验证**（沙盒断言） | **人类偏好 / 内部评审**（learned RM 或工程师打分） |
| 性质 | RLVR | RLHF 式 |
| 场景 | 通用 PyAether/SKILL 脚本 | **专有设计流程**、team-specific 规范 |

> 这样 (v) = "从公开可验证任务走向**内部私有偏好**"，是递进而非重复，
> 且正好呼应 BaiZe 的原始动机（per-team / per-engineer 的常驻小模型）。

---

## 5. 红线（违反则整节作废）

### 5.1 污染隔离（contamination）

🚨 **`EDA-Eval-PyAether` 的 158 个任务（prompt + 函数签名 + 断言代码）绝对不能进任何训练集。**

- 允许：用 **API 参考文档**（占任务来源 61.4%）合成 (instruction, PyAether code) 训练对
- 必须：按 **API 名 / 函数签名** 做隔离，确保评测任务的答案与断言不泄漏
- 必须在论文中**写明隔离规则**；事后补做会被认定为 contamination

### 5.2 反作弊

- `PreToolUse` hook **全程启用，所有实验臂逐字一致**——它是**冻结变量**
- BaiZe 的 RL 也必须挂同一套 anti-cheat
- 必须报告 **cheat rate**

### 5.3 口径一致性

- ZhuLong 数字（94.0% / 36% / 旧 78.5%·84.8%·23.6%·11.4%）**引用前必须确认口径与版本**
- 5-run mean ± std，不得报单次值
- 158 任务固定集上做两系统比较时，**优先用配对检验（McNemar / paired bootstrap）**——
  仅比较均值不敏感（binomial SE @ p=0.8, n=158 ≈ 3.2 pp，95% CI ≈ ±6.2 pp）

---

## 6. 风险清单

| # | 风险 | 严重度 | 应对 |
|---|---|---|---|
| **0b** | 🚩 **分母漂移（有效性威胁）**：Pass@1 若在"**生成成功子集**"上计算，两模型分母不同 → **58 pp 不可比** | 🔴 **最高** | **核对 36% 与 94% 的分母口径并统一重算**——这是所有结论的前提（见 §7.0 假差距 C） |
| **0** | **58 pp 的可回收性未知**——这是**研究问题**，不是缺陷；但存在"回收有限"的可能 | 🟠 中 | 走 §4 Stage (ii) 的**成功阶梯**分档预注册；准备成本-质量前沿表述兜底 |
| 1 | **视觉编码器未验证**（未收敛 + 无 EDA 下游指标） | 🔴 高 | (iv) 前先用 lr=3e-3 重训到收敛，并加 EDA 图下游指标 |
| 2 | **Reward hacking** | 🔴 高 | anti-cheat + 报告 cheat rate |
| 3 | **上下文 4096 对 agentic 轨迹过短** | 🔴 高 | (ii) 前做长上下文适配；作为一等消融 |
| 4 | **污染**（训练集含评测任务） | 🔴 高 | §5.1 隔离规则，论文写明 |
| 5 | **"差不太多"是模糊主张**，易被质疑事后合理化 | 🟠 中 | **预注册判定阈值**（点估计 + 配对检验显著性 + 成本比），先定后测 |
| 6 | **harness 为 70B 模型调优**，可能低估小模型 | 🟠 中 | 报**两级**：冻结 harness（公平）+ 适配 harness（Φ 预算/检索 k 重调） |
| 7 | **同基准两篇论文**（ZhuLong@DAC + BaiZe@ISEDA）贡献边界 | 🟠 中 | BaiZe 只报 backbone 维度，不重报 harness 消融；互相引用 |
| 8 | **训练量极小**（655M tok / 2.2B 模型） | 🟠 中 | 补"训练 token 量 vs 下游 pass@1"曲线，用下游指标回应 |
| 9 | **预算口径错配**（GPU-hour vs 沙盒时延） | 🟡 低 | RL 阶段按沙盒并发 × 墙钟规划 |

---

## 7. 跨阶段消融清单（按性价比排序）

### 7.0 🔬 诊断清单（**零成本，必须先做**）— 排除"假差距"

36% 有可能是**协议不匹配**的产物，而不是能力上限。在做任何训练之前，先从**已有那次 36% 运行**里挖出下列统计：

| # | 诊断项 | 判读 |
|---|---|---|
| D1 | **工具调用合法率**（格式合法的 tool_call / 总数） | <90% → **协议问题**，SFT 可大幅回收 |
| D2 | **工具调用频次**（每任务平均调用次数，vs DeepSeek 的） | 显著偏低 → 模型不"用工具"、纯靠回忆 → SFT 可修 |
| D3 | **超上下文/截断比例** | 高 → 长上下文适配是 (ii) 的前置项 |
| D4 | **失败类型分解**（执行报错 vs 断言失败） | 报错多 → API/领域知识问题（SFT 领域语料）；断言失败多 → 语义推理问题（RL 价值更大） |
| D5 | **per-scenario 通过率**（Layout / Schematic / Design Mgmt / Others） | 决定 SFT 数据的配比 |
| D6 | **平均迭代轮数（Φ）分布** | 显著低于 DeepSeek → 模型不会用执行反馈闭环 |

**数据来源**：`~/eda_code_eval/*/final_report.json` 的 `details_per_task`（**数据已在手，无需重跑**）。

> 这六项**不花任何 GPU**，但直接决定 (ii) 该往哪使劲：若 D1/D2/D6 差得离谱，则 58 pp 里很大一部分是
> **可回收的协议差距**，"差不太多"才有戏；若 D1/D2/D6 都正常而 D4 全是断言失败，则差距是**真实能力差距**，
> 必须立刻转向成本-质量前沿的表述。

### 7.1 消融清单

| # | 消融 | 成本 | 价值 |
|---|---|---|---|
| **1** | **BaiZe-base 在 EDA-Eval-PyAether 的 pass@1**（先 pure LLM，再 full harness） | **极低（纯推理）** | **补上论文最大的洞；几天内可出数** |
| 2 | **harness 冻结下 backbone 横向对比**（BaiZe vs MiniCPM5-2B vs DeepSeek-V4-Pro） | 中 | 论文核心主张（成本效率） |
| 3 | **训练 token 量 vs 下游 pass@1**（200M / 655M / 2B 三点） | 中 | 用下游指标回应"训练量太小" |
| **4** | **hybrid vs dense 在同等 harness 下的 pass@1** | 中 | 现在只有 loss 层面的 hybrid 优势；换成下游指标才立得住。**可能是最有价值的一张图** |
| 5 | RL 奖励设计 4 臂（R1–R4） | 高（沙盒时延） | (ii) 核心 |
| 6 | 2.2B vs MiniCPM5-1B（S1-01 已跑过）同 harness | 中 | 回答"2.2B 值不值" |

### 建议的推进顺序

```
① BaiZe-base → EDA-Eval-PyAether（pure LLM）        ← 立刻做，低成本
② BaiZe-base → full harness（冻结）                 ← 决定性早期信号
③ 若差距大 → 诊断：工具协议遵循率 / 迭代次数分布 / 错误分类
④ SFT（含污染隔离）→ 重测
⑤ RL（奖励 4 臂 + anti-cheat）→ 重测
⑥ 补 hybrid vs dense 下游对比
⑦ 回头修视觉编码器 → Stage (iv)
```

---

## 8. 目录结构

```
doc/BaiZe-ISEDA2027/
├── README.md                      # 本文件（项目总纲）
├── BaiZe-ISEDA2027/               # 论文 LaTeX 树（IEEEtran，自包含）
│   ├── main.tex                   #   注意：作者信息已注释（ISEDA 需匿名）
│   ├── main.pdf                   #   5 页（随正文更新）
│   ├── reference.bib              #   13 条，全部被引用
│   ├── figures/                   #   s5_01_loss_curve.png / config_ablation.pdf / train_loss.pdf
│   └── ISEDA2027/                 #   0_abstract … 9_conclusion
├── run/                           # 实验执行编排 + 记录
│   ├── EXPERIMENTS*.md            #   实验台账（2B / pretrain / vision）
│   ├── MEMORY*.md                 #   agent 运行时状态
│   ├── daily-memories/            #   每日流水
│   └── train_s*.sh, baize_*.sh    #   可复现命令
├── data/                          # s5_01_loss_curve.csv
├── *.html                         # 对外报告（ARCH / PRETRAIN / VISION）
└── Xmodel-2, Xmodel-2.5, Xmodel-LM  # 参考项目（μP 内容属其自身，非遗留）
```

**相关但独立的项目**：`doc/ZhuLong_DAC2027/`（DAC 2027，harness 与基准的所有者）。

---

## 9. 待办 / 已知问题

### 论文层面
- [x] 清除 μP 遗留（commit `c1fd532`）
- [x] 修复致命表格 bug（`6_vision_encoder.tex` 6 行 `\` → `\\`），论文从"编译不出"到 0 错误
- [x] Nemotron-H 商品名分层淡化 + 来源交代 + 差异声明（`e1dab26`）
- [x] decode 10.3× 加限定；图片归位 `figures/`（`dc2e59b`）
- [x] 投稿匿名化 + 重建 main.pdf（`f7746df`）
- [ ] **补下游评测**（见 §7 第 1 项）— **最高优先级**
- [ ] **五阶段里 (ii)(iv)(v) 三节仍是骨架**，全文 11 处 `[TBD]`；摘要/引言/结论仍在卖五阶段
- [ ] **结构收缩 or 补满**：当前"结构规模 > 内容规模"（详见对话记录）
- [ ] 去重 §3.1 与 §4.1(iii) 的 pattern 出处句
- [ ] 补 Limitations 节
- [ ] 修 Abstract / Conclusion 中"reported as [TBD]"的陈旧表述（§4 已有实测数字）
- [ ] §2 相关工作缺视觉编码器一线（2.3 只覆盖 VLM 对齐）

### 工程层面
- [ ] BaiZe checkpoint → OpenAI-compatible 推理服务（vLLM/SGLang），接入 Cline harness
- [ ] 长上下文适配（4096 → 8192+）评估
- [ ] 视觉编码器以 lr=3e-3 重训至收敛 + 加 EDA 下游指标

### 待确认
- [x] ~~MiniCPM5-2B 的 36% 是在哪个 harness 配置下测的？~~ → **已确认：full harness（与 94.0% 同口径）**，差距 **58 pp**
- [ ] MiniCPM5-2B 的 36% 是**单次还是 5-run**？若单次需补足 5-run mean ± std
- [ ] **§7.0 诊断清单 D1–D6**（零成本，最高优先）
- [ ] ZhuLong 最终口径（94.0% 是否会在 EDA-Scripting-Bench 上重测后变化）
- [ ] **预注册** (ii) 的判定阈值（点估计 + 配对检验显著性 + 成本比）——**必须先定后测**


