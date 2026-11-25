# TOP-K 精选论文（研究相关性 x 质量）

> research 线 · 运维指令 2026-10-03 第 2 批（第 3 批强化）。窗口 **<=30d**（`published` 首次提交）。
> 候选池：1118 篇（生成于 2026-10-03T11:51:07.979605+00:00）｜ TOP-20 ｜ 权重 **w1(rel)=0.6 / w2(q)=0.4**。
> 第 3 批新增：① 相关面放宽到「**存储/芯片 AI 研究院**」视角（新增 `BaiZe·存储/内存技术`、
> `BaiZe·芯片/加速器` 两组，半导体/EDA/存储相关 AI 论文 `rel` 上调）；② 每条附 **`takeaway`（可借鉴点）+ `action`（建议动作）**，
> 源 `TOP_K_takeaways.json`；③ 行动清单见 `TAKEAWAYS.md`。

## 排序方法

- **rel（0-5）**：关键词命中 BaiZe / ZhuLong 主题词表后按权重（1.0/1.5）求和、封顶 5（0.5 粒度）。
- **q（0-5）**：`min(5, code + method + org + comment + hn)`，五项代理各 +1；
  · **code** = 摘要/comment 提及代码或仓库（github/gitlab/huggingface）
  · **method** = 提出新方法/框架/基准（非综述/小增量）
  · **org** = 命中已知实验室白名单
  · **comment** = arXiv `comment` 或 `journal_ref` 非空
  · **hn** = **HN Algolia**（`https://hn.algolia.com/api/v1/search`）标题命中且 points>=5（+1）/ 弱命中（+0.5）
- **total = 0.6·rel + 0.4·q**（偏向与本线研工作的相关性）。
- **takeaway / action（人工，不参与打分）**：每条给「对我们工作的**可借鉴点**」与**建议动作**
  （`试跑` / `读原文` / `仅备忘`），源 `TOP_K_takeaways.json`。

## 局限（诚实声明）

- 代理指标 **!=** 真实影响力：词表命中会**高估**同名但不同义的工作；`q` 的 org 白名单只看文本、拿不到 arXiv affiliations，**可能漏判/误判**。
- **HF Daily Papers 本机不可达（已实测 `Network is unreachable`）** → 社区热度**改用 HN Algolia 替代**；HN 以英文技术圈为主，**中文/冷门方向会低估**。
- `q` 的 code 代理只看摘要/comment 文本，**未逐个打开项目页核验**（避免犯 `200 != 有料` 的错）。
- 排序对 `w1/w2` 敏感；本文给出明确权重，便于复核与调整。

## TOP-5 导读（人工撰写 · 3-5 句/条）

> 说明：以下是**人工**对 TOP-5 的「为什么与我们在研工作相关」，3–5 句/条；
> 全部基于**标题 + 摘要 + arXiv comment**（未整篇精读），判断类语句标「**我们判断**」。
> 生成器每次重跑都会**自动嵌入本文件**（`--notes-md`），因此可与 `TOP_K.md` 保持一致。
>
> ⚠️ 第 3 批把相关面放宽到「**存储/芯片 AI 研究院**」视角后，**DeepSeek-V4.1-Flash 升为 #1**
> （`HBM/SSD/KV cache` 命中新增的 `BaiZe·存储/内存技术`，`rel` 由 4.0 → 5.0）。次序为脚本自动排序结果。

- **#1 DeepSeek-V4.1-Flash（2609.19969）**：它把长上下文的瓶颈明确指向**HBM / SSD 容量与带宽**，并用**跨层 KV 复用（CSA2）+ FP4 KV 缓存 + SWA Bounded Replay** 把全局 KV 压到 **890 bytes/token（约 V4-Flash 的 1/4）**、持久 KV 压到约 **1/8**；
  这对**「显存/存储带宽受限」的高效推理**与 BaiZe 的**长上下文推理**是最直接的一手借鉴。**我们判断**：其**非对称激活（8B prefill / 16B decode）** 与「KV 常驻 HBM + 冷 KV 落 SSD」的分层，正是**存储研究院视角**下最值得复刻的工程范式；
  这也是本轮把 `rel` 相关面放宽到半导体/存储后**新上榜首**的条目。

- **#2 ExecCritic（2609.09133）**：它把**测试构造**与**代码修复**拆成两个角色，用 `test→verify→revise` 脚手架 + 角色化 RL 训练，正对口 ZhuLong 的 **generate–execute–refine 执行闭环** 与 **code agent** 方向；
  摘要明确 point out「patch 与 test 由同一轨迹生成会**同错而同信**（false confidence）」，这恰是我们在 EDA 代码任务里做**执行反馈可信度**时最该防的失效模式。**我们判断**：其「fail-closed harness 冻结测试」的设计可直接借鉴为 ZhuLong 的评测/判分护栏；
  有官方代码（`github.com/msr-orchard/execcritic`）与 35 页 tech report，属**可复现**的高价值条目。

- **#3 Rethinking Multi-Image Re-Representation（2609.39363）**：它把**多图理解**统一为「重表征」，并把 **prompted CoT** 与 **agentic 视觉工具调用**当作同一枚硬币的两面——这与 BaiZe 的 **多模态对齐** 与 ZhuLong 的 **工具/MCP** 两条线同时相交；
  其 **Mosaic** 用 10 个**可组合图像算子**主动构造视觉中间产物，本质上是「视觉侧的 harness」。**我们判断**：其新基准 **MosaicBench** 的「细粒度 grounding」评测口径，对 BaiZe 多模态对齐的验收有参考价值；代码在 `github.com/gengyuanmax/mosaic`。

- **#4 PainterBench（2609.34195）**：把人类**未完成图形发散思维**任务搬到 agent 场景：agent 经**工具调用**作画、每轮观察结果、自行决定何时收笔——是**工具使用 + 增量视觉规划**的干净基准；
  对 ZhuLong 的 **评测基准（SWE-bench 类）** 与 **工具/MCP** 很有启发：它展示了「开放式、无 golden answer、过程可观测」的任务如何被**可评测化**。**我们判断**：其「agent 自我终止」机制对长程 EDA 任务的**停止准则**设计有借鉴意义（25 页 / 7 图 / 11 表，规格扎实）。

- **#5 One to More, More to One（2609.23377）**：针对仓库级 SWE 的**类别跷跷板**（RL 后部分类别涨、部分类别退）提出**类别感知的专家训练 + 策略融合**，直击 ZhuLong **SWE 类 agent** 与 BaiZe **后训练（SFT/RL）** 的共同痛点；
  其「Executable task construction + SWE Labeler 多轴标注」把训练池**证据化组织**，方法与我们的**数据配比/可执行任务构造**诉求高度一致。**我们判断**：这是本轮**最贴近 ZhuLong 主线**的候选之一，且放出了 `Logics-SWE-Qwen3.6-27B` 权重与 44 页附录，**可复现性最强**。

> **复核提示（人工，防代理过配）**：**#6 Faynt（2610.02144）⚠️** 用 10M/75M Transformer 策略 + RL 在《任天堂明星大乱斗 Melee》上做到 **98.4% 胜率**，
> **代码/方法/54 页**三项代理命中故 `q=4.0`；但这是**游戏 RL 的策略缩放**，与 LLM/SLM 主线的相关性**仅停留在「规模律 / RL 后训练 / 高效推理」这类泛词命中**——**我们判断**它很可能是**词表过配（over-match）**，建议人工降权。
> （**`q` 的 org 代理在本文是假阳性**：白名单命中的 `nvidia` 来自摘要中「on an NVIDIA T4」这一**硬件型号**，**并非作者所属机构**——已如实标注，提示 org 代理的局限。）
> 另：**#18 Sharpening Tax in Post-Training（2610.01509）** 的真实优先级应更高：它发现**预训练 LLM + 轻量 inference harness 即可是能干 agent，且 pass@K（解空间覆盖）常胜过 post-trained 版本**——
> 对 ZhuLong 的 **agent harness** 与 BaiZe 的 **后训练** 都是**反直觉且高信息量**的结论，只因缺 `code/org/comment` 代理而 `q` 偏低（见 `TAKEAWAYS.md` 第 1 条）。

## TOP-20

| # | rel | q | total | 标题 | arXiv | 主分类 | 提交 |
|--:|--:|--:|--:|:--|:--|:--|:--|
| 1 | 5.0 | 4.0 | 4.6 | DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression | [2609.19969](https://arxiv.org/abs/2609.19969v1) | cs.CL | 2026-09-17 |
| 2 | 4.5 | 4.0 | 4.3 | ExecCritic: Learn to Test, Test to Improve for Coding Agents | [2609.09133](https://arxiv.org/abs/2609.09133v1) | cs.AI | 2026-09-08 |
| 3 | 5.0 | 3.0 | 4.2 | Rethinking Multi-Image Re-Representation in Multi-Image Understanding | [2609.39363](https://arxiv.org/abs/2609.39363v1) | cs.CV | 2026-09-30 |
| 4 | 5.0 | 3.0 | 4.2 | PainterBench: A Figural Divergent-Thinking Benchmark for Tool-Using Language Models | [2609.34195](https://arxiv.org/abs/2609.34195v1) | cs.AI | 2026-09-28 |
| 5 | 5.0 | 3.0 | 4.2 | One to More, More to One: Category-Aware Iterative Expert Training for Software Engineering Agents | [2609.23377](https://arxiv.org/abs/2609.23377v1) | cs.SE | 2026-09-20 |
| 6 | 4.0 | 4.0 | 4.0 | Faynt: Scaling and Optimizing Policies for Competitive Melee | [2610.02144](https://arxiv.org/abs/2610.02144v1) | cs.LG | 2026-10-01 |
| 7 | 5.0 | 2.0 | 3.8 | From Given to Gathered Evidence: Agentic Learning for Longitudinal Medical Reasoning | [2609.39566](https://arxiv.org/abs/2609.39566v1) | cs.CV | 2026-09-30 |
| 8 | 5.0 | 2.0 | 3.8 | Codoku: Renewable Program-Reasoning Challenges for Frontier Coding Agents | [2609.34661](https://arxiv.org/abs/2609.34661v1) | cs.SE | 2026-09-28 |
| 9 | 5.0 | 2.0 | 3.8 | Qwen-Audio-3.1-Realtime: Towards Reliable Agentic Voice Interaction | [2609.25176](https://arxiv.org/abs/2609.25176v2) | eess.AS | 2026-09-21 |
| 10 | 4.0 | 3.0 | 3.6 | GroundingPI: A Grounding Foundation Model towards Physical Intelligence with Visual Primitives | [2609.39601](https://arxiv.org/abs/2609.39601v1) | cs.CV | 2026-09-30 |
| 11 | 4.0 | 3.0 | 3.6 | SRJudge: Empowering Large Language Models with Selective Reasoning for Fine-Grained Knowledge Concept Tagging | [2609.36982](https://arxiv.org/abs/2609.36982v1) | cs.CL | 2026-09-29 |
| 12 | 4.0 | 3.0 | 3.6 | Qwen-Planner-Agent: A Closed-Loop AI-for-AI Framework for Real-World Mobile Planner Agents | [2609.29892](https://arxiv.org/abs/2609.29892v1) | cs.AI | 2026-09-24 |
| 13 | 4.0 | 3.0 | 3.6 | IndicBankBench: Evaluating Safety and Reliability of Language Model Assistants in Indian Retail Banking | [2609.29167](https://arxiv.org/abs/2609.29167v1) | cs.AI | 2026-09-24 |
| 14 | 4.0 | 3.0 | 3.6 | Qwen3.8-Omni: Towards Native Omni-Modal Agents | [2609.25611](https://arxiv.org/abs/2609.25611v1) | cs.CL | 2026-09-22 |
| 15 | 4.0 | 3.0 | 3.6 | On the Recall Scaling Laws in Mamba: A Theoretical and Mechanistic Study via Hashing | [2609.07681](https://arxiv.org/abs/2609.07681v1) | cs.LG | 2026-09-07 |
| 16 | 4.5 | 2.0 | 3.5 | CineMR: Tool-Integrated Vision-Language Reasoning for Quantitative Cardiac MRI Assessment | [2610.01166](https://arxiv.org/abs/2610.01166v1) | cs.CV | 2026-10-01 |
| 17 | 4.5 | 2.0 | 3.5 | EgoTools: Towards Tool-Centric Reasoning in Real-World Egocentric Videos | [2609.39378](https://arxiv.org/abs/2609.39378v1) | cs.CV | 2026-09-30 |
| 18 | 5.0 | 1.0 | 3.4 | Sharpening Tax in Post-Training | [2610.01509](https://arxiv.org/abs/2610.01509v1) | cs.AI | 2026-10-01 |
| 19 | 5.0 | 1.0 | 3.4 | QuantCode Model: Specializing Language Models for Executable Algorithmic Trading Code | [2609.39420](https://arxiv.org/abs/2609.39420v1) | cs.CL | 2026-09-30 |
| 20 | 5.0 | 1.0 | 3.4 | Visual Parallel Search: Learning to Search High-Resolution Images with Parallel Tile Inspection and Adaptive Zoom | [2609.37002](https://arxiv.org/abs/2609.37002v2) | cs.CV | 2026-09-29 |

## 逐条：相关性理由 + 质量证据

- **#1 DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression**（arXiv:2609.19969）
  · 🔗 rel=5.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理；BaiZe·存储/内存技术）
  · 🏅 q=4.0（代码: 摘要/comment 提及代码或仓库（https://huggingface.co/deepseek-ai/deepseek-v4.1-flash.）；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（deepseek）；HN 热度: 命中《DeepSeek-v4.1 Flash: Pushing the Limits of KV Cache Compression》(131 points, 标题重合 100%)）
  · 🎯 takeaway: 跨层 KV 复用(CSA2) + FP4 KV 缓存 + SWA Bounded Replay，把全局 KV 压到 890 bytes/token（约 DeepSeek-V4-Flash 的 1/4）、持久 KV 压到约 1/8，并显式点名『HBM/SSD 容量与带宽是部署成本主瓶颈』——对『显存/存储带宽受限』的高效推理与 BaiZe 长上下文推理是最直接借鉴（含 8B prefill / 16B decode 的非对称激活）。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.19969v1 ｜ pdf: https://arxiv.org/pdf/2609.19969v1 ｜ 💻 https://huggingface.co/deepseek-ai/deepseek-v4.1-flash.
- **#2 ExecCritic: Learn to Test, Test to Improve for Coding Agents**（arXiv:2609.09133）
  · 🔗 rel=4.5（BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·执行闭环(generate-execute-refine)；ZhuLong·评测基准）
  · 🏅 q=4.0（代码: 摘要/comment 提及代码或仓库（https://github.com/msr-orchard/execcritic.）；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（qwen）；arXiv comment/journal_ref: 35 pages；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 把『生成测试』与『生成补丁』拆成两个角色，并用 fail-closed harness 冻结测试后只让 Repair agent 改源码——直击 ZhuLong 的 generate–execute–refine 闭环；摘要点名的『patch 与 test 同轨迹生成会同错而同信(false confidence)』正是 EDA 代码任务里做执行反馈可信度最该防的失效模式。我们判断其 fail-closed 冻结测试可直接借鉴为 ZhuLong 的评测/判分护栏。
  · ✅ action: 试跑
  · abs: https://arxiv.org/abs/2609.09133v1 ｜ pdf: https://arxiv.org/pdf/2609.09133v1 ｜ 💻 https://github.com/msr-orchard/execcritic.
- **#3 Rethinking Multi-Image Re-Representation in Multi-Image Understanding**（arXiv:2609.39363）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/gengyuanmax/mosaic.）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 27 pages, 7 figures, 9 tables；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 多图理解里『文本 CoT』与『视觉工具调用』被统一为『重表征』的两种方式，收益强依赖任务；其 Mosaic（10 个可组合图像算子）=『视觉侧的 harness』，新基准 MosaicBench 的细粒度 grounding 口径可作 BaiZe 多模态对齐的验收基准。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.39363v1 ｜ pdf: https://arxiv.org/pdf/2609.39363v1 ｜ 💻 https://github.com/gengyuanmax/mosaic.
- **#4 PainterBench: A Figural Divergent-Thinking Benchmark for Tool-Using Language Models**（arXiv:2609.34195）
  · 🔗 rel=5.0（BaiZe·预训练/数据配比；BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 25 pages, 7 figures, 11 tables；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 把人类『未完成图形发散思维』搬到 agent：多轮工具作画、每轮观察、agent 自决何时收笔——示范了『开放式、无标准答案、过程可观测』的任务如何被可评测化。我们判断其『agent 自我终止』机制对 ZhuLong 长程 EDA 任务的停止准则设计有借鉴意义。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.34195v1 ｜ pdf: https://arxiv.org/pdf/2609.34195v1
- **#5 One to More, More to One: Category-Aware Iterative Expert Training for Software Engineering Agents**（arXiv:2609.23377）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理；ZhuLong·agent harness/code agent；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://huggingface.co/logics-mllm/logics-swe-qwen3.6-27b）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 44 pages, including appendices. Model available at https://huggingface.co/Logics；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 仓库级 SWE 的『类别跷跷板』（部分类别涨、部分退）用『类别专家 + 同源自我蒸馏 + 标签路由多教师 on-policy 蒸馏』缓解；其可执行任务构造 + SWE Labeler 多轴标注把训练池证据化组织，方法与 BaiZe 的数据配比 / ZhuLong 的可执行任务构造高度一致。我们判断这是本轮最贴近 ZhuLong 主线、可复现性最强的候选之一。
  · ✅ action: 试跑
  · abs: https://arxiv.org/abs/2609.23377v1 ｜ pdf: https://arxiv.org/pdf/2609.23377v1 ｜ 💻 https://huggingface.co/logics-mllm/logics-swe-qwen3.6-27b
- **#6 Faynt: Scaling and Optimizing Policies for Competitive Melee**（arXiv:2610.02144）
  · 🔗 rel=4.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；BaiZe·高效推理；ZhuLong·评测基准）
  · 🏅 q=4.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（nvidia）；arXiv comment/journal_ref: 54 pages. Preprint, in review；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 10M/75M Transformer 策略 + RL 在《大乱斗 Melee》上 98.4% 胜率；本质是游戏 RL 的策略缩放，与 LLM/SLM 主线相关性仅停留在『规模律/RL 后训练/高效推理』这类泛词命中——我们判断为词表过配(over-match)，仅供类比，不必迁移。
  · ✅ action: 仅备忘
  · abs: https://arxiv.org/abs/2610.02144v1 ｜ pdf: https://arxiv.org/pdf/2610.02144v1
- **#7 From Given to Gathered Evidence: Agentic Learning for Longitudinal Medical Reasoning**（arXiv:2609.39566）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（代码: 摘要/comment 提及代码或仓库（https://github.com/vinyehshaw/case.）；方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 『从给定证据 → 主动收集证据』的 agentic 后训练范式（SFT 迁移前沿模型轨迹 + RL 自环境交互 + 特权 on-policy 自蒸馏 + rubric 反馈，且不规定工具序列），可迁移到任何需要跨记录检索的任务；其纵向多模态基准（UK Biobank）思路对 BaiZe 多模态对齐的『长程取证』评测有参考。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.39566v1 ｜ pdf: https://arxiv.org/pdf/2609.39566v1 ｜ 💻 https://github.com/vinyehshaw/case.
- **#8 Codoku: Renewable Program-Reasoning Challenges for Frontier Coding Agents**（arXiv:2609.34661）
  · 🔗 rel=5.0（BaiZe·小模型/端侧；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（代码: 摘要/comment 提及代码或仓库（https://github.com/connglli/codoku.）；方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 『可再生、防污染、答案稀疏到无法枚举/工具绕过』的基准构造思路（语义具体化 + witness 保证可解）——可借鉴到 EDA 代码基准的可再生化：用约束稀疏性迫使 agent 必须真正做程序推理而非执行试错。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.34661v1 ｜ pdf: https://arxiv.org/pdf/2609.34661v1 ｜ 💻 https://github.com/connglli/codoku.
- **#9 Qwen-Audio-3.1-Realtime: Towards Reliable Agentic Voice Interaction**（arXiv:2609.25176）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·高效推理；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP）
  · 🏅 q=2.0（机构/作者: 命中已知实验室白名单（qwen）；arXiv comment/journal_ref: 25 pages, technical report；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 实时语音 agent 的 Think/Act/Speak 三段式 + M²-OPD 多教师 on-policy 蒸馏 + 自演化可执行环境做 GRPO；其中『多教师 on-policy 蒸馏把不同能力收敛进一个可部署学生』与 ZhuLong 的多工具 agent 训练可互通。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.25176v2 ｜ pdf: https://arxiv.org/pdf/2609.25176v2
- **#10 GroundingPI: A Grounding Foundation Model towards Physical Intelligence with Visual Primitives**（arXiv:2609.39601）
  · 🔗 rel=4.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/groundingpi/groundingpi）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 64 pages, including supplementary material. Project page: https://groundingpi.gi；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 4B grounding 基座把点/框当量化坐标统一进词表（多模态+空间预训练 → SFT → GRPO），34 个 grounding 基准平均 73.68% 超过更大模型——对『小模型 + 空间 grounding + 端侧/机器人闭环』路线有参考（BaiZe 多模态/端侧）。
  · ✅ action: 仅备忘
  · abs: https://arxiv.org/abs/2609.39601v1 ｜ pdf: https://arxiv.org/pdf/2609.39601v1 ｜ 💻 https://github.com/groundingpi/groundingpi
- **#11 SRJudge: Empowering Large Language Models with Selective Reasoning for Fine-Grained Knowledge Concept Tagging**（arXiv:2609.36982）
  · 🔗 rel=4.0（BaiZe·后训练(SFT/RL)；BaiZe·小模型/端侧；BaiZe·高效推理；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/nicozwy/srjudge.）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: Accepted by IJCAI 2026；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 三段式 Select-Reason-Judge：先用小模型(SLM/BERT)把候选概念缩到 top-K 降低决策空间、再让 LLM 推理判分——这种『SLM 降维 + LLM 精判』的分工可复用到任何大规模候选决策空间任务（省 token、提准确）。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.36982v1 ｜ pdf: https://arxiv.org/pdf/2609.36982v1 ｜ 💻 https://github.com/nicozwy/srjudge.
- **#12 Qwen-Planner-Agent: A Closed-Loop AI-for-AI Framework for Real-World Mobile Planner Agents**（arXiv:2609.29892）
  · 🔗 rel=4.0（BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP）
  · 🏅 q=3.0（方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（qwen）；arXiv comment/journal_ref: https://tongyi-mai.github.io/Qwen-Planner-Agent/；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 闭环 AI-for-AI：用真实环境反馈驱动 planner agent 迭代（含环境/评测闭环与项目页）——与 ZhuLong 的 generate–execute–refine 同构，可对照其『真实反馈如何进训练回路』的实现。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.29892v1 ｜ pdf: https://arxiv.org/pdf/2609.29892v1
- **#13 IndicBankBench: Evaluating Safety and Reliability of Language Model Assistants in Indian Retail Banking**（arXiv:2609.29167）
  · 🔗 rel=4.0（ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 16 pages, 4 figures；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 领域化的 assistant 安全/可靠性评测基准（印度零售银行，16 页）：其『领域合规 + 安全 + 可靠性』多维评测口径，可借鉴为 EDA/存储域 agent 的合规评测模板。
  · ✅ action: 仅备忘
  · abs: https://arxiv.org/abs/2609.29167v1 ｜ pdf: https://arxiv.org/pdf/2609.29167v1
- **#14 Qwen3.8-Omni: Towards Native Omni-Modal Agents**（arXiv:2609.25611）
  · 🔗 rel=4.0（BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（qwen）；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 原生全模态 agent 的技术报告，可作『多模态 + agent 合流』路线的现状对照；关注其模态融合与工具调用的接口设计（BaiZe 多模态对齐）。
  · ✅ action: 仅备忘
  · abs: https://arxiv.org/abs/2609.25611v1 ｜ pdf: https://arxiv.org/pdf/2609.25611v1
- **#15 On the Recall Scaling Laws in Mamba: A Theoretical and Mechanistic Study via Hashing**（arXiv:2609.07681）
  · 🔗 rel=4.0（BaiZe·Mamba/混合架构；BaiZe·规模律；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/yuvalko1/mamba-recall-scaling-laws）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 53 pages, 20 figures. Code and experiments available at: https://github.com/yuva；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 从理论 + 机制层面刻画 Mamba 的『回忆(recall)规模律』（用 hashing 视角给出解释与实验）——直接对口 BaiZe 的 Mamba-2×attention 混合架构选型与规模律分析，可支撑『哪些能力该交给 attention、哪些可交给 SSM』的架构决策。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.07681v1 ｜ pdf: https://arxiv.org/pdf/2609.07681v1 ｜ 💻 https://github.com/yuvalko1/mamba-recall-scaling-laws
- **#16 CineMR: Tool-Integrated Vision-Language Reasoning for Quantitative Cardiac MRI Assessment**（arXiv:2610.01166）
  · 🔗 rel=4.5（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（代码: 摘要/comment 提及代码或仓库（https://github.com/ai-mind-lab/cinemr.）；arXiv comment/journal_ref: Code, benchmark resources, and model weights are available at https://github.com；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 工具集成 VLM 做定量心脏 MRI 评估（含代码/基准/权重，端到端）——是『工具调用 + 领域定量评测』的完整范本，可对照其工具接口与评测协议。
  · ✅ action: 仅备忘
  · abs: https://arxiv.org/abs/2610.01166v1 ｜ pdf: https://arxiv.org/pdf/2610.01166v1 ｜ 💻 https://github.com/ai-mind-lab/cinemr.
- **#17 EgoTools: Towards Tool-Centric Reasoning in Real-World Egocentric Videos**（arXiv:2609.39378）
  · 🔗 rel=4.5（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 32 pages, 7 figures. Project page: https://ropedia.github.io/egotools；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 第一视角(egocentric)视频里『以工具为中心』的推理基准，把工具使用评测的模态边界扩展到真实第一人称视频；可作 ZhuLong 工具/MCP 评测的场景启发。
  · ✅ action: 仅备忘
  · abs: https://arxiv.org/abs/2609.39378v1 ｜ pdf: https://arxiv.org/pdf/2609.39378v1
- **#18 Sharpening Tax in Post-Training**（arXiv:2610.01509）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=1.0（方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 反直觉高价值结论：预训练 LLM + 轻量 inference harness 即可作能干 agent，且 pass@K（解空间覆盖）常胜过 post-trained 版本；后训练把任务推向『总解/永不解』两端、提升采样效率却牺牲覆盖。给出诊断指标 Sharpening Tax 与即插即用采样法 PTGS。我们判断这对『是否需要重度后训练』是重要警戒，直接关系 BaiZe 后训练策略与 ZhuLong harness 设计。
  · ✅ action: 试跑
  · abs: https://arxiv.org/abs/2610.01509v1 ｜ pdf: https://arxiv.org/pdf/2610.01509v1
- **#19 QuantCode Model: Specializing Language Models for Executable Algorithmic Trading Code**（arXiv:2609.39420）
  · 🔗 rel=5.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=1.0（arXiv comment/journal_ref: 16 pages, 2 figures, 6 tables；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 两段式领域专业化配方『继续预训练框架代码 → 在 agent 验证过的 request→code 对上 SFT』，并给出反直觉证据：继续预训练会损伤指令跟随（修复后终胜率反降 47.5%→32.5%），而 SFT 使首轮与终局双升（22.3%→58.3%、47.5%→79.5%）。对 ZhuLong 的领域代码专业化与 SFT 配方可直接迁移（含 400 任务基准 + SWE-bench 类仓库级 track）。
  · ✅ action: 试跑
  · abs: https://arxiv.org/abs/2609.39420v1 ｜ pdf: https://arxiv.org/pdf/2609.39420v1
- **#20 Visual Parallel Search: Learning to Search High-Resolution Images with Parallel Tile Inspection and Adaptive Zoom**（arXiv:2609.37002）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=1.0（方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · 🎯 takeaway: 视觉搜索框架 VPS：主 agent 先用 grid_search 并行巡检 tile 获得全局、再自适应 zoom_in 精读，配『无提示验证 + 角色化 GRPO』；我们判断『先粗扫再精读 + 主子 agent 分工』可直接迁移为 ZhuLong 的『先扫 API/仓库全局、再精读定位』检索策略，其角色特定 RL 还能压缩工具调用次数。
  · ✅ action: 读原文
  · abs: https://arxiv.org/abs/2609.37002v2 ｜ pdf: https://arxiv.org/pdf/2609.37002v2

