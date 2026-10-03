# TOP-K 精选论文（研究相关性 x 质量）

> research 线 · 运维指令 2026-10-03 第 2 批。窗口 **<=30d**（`published` 首次提交）。
> 候选池：1118 篇（生成于 2026-10-03T11:51:07.979605+00:00）｜ TOP-20 ｜ 权重 **w1(rel)=0.6 / w2(q)=0.4**。

## 排序方法

- **rel（0-5）**：关键词命中 BaiZe / ZhuLong 主题词表后按权重（1.0/1.5）求和、封顶 5（0.5 粒度）。
- **q（0-5）**：`min(5, code + method + org + comment + hn)`，五项代理各 +1；
  · **code** = 摘要/comment 提及代码或仓库（github/gitlab/huggingface）
  · **method** = 提出新方法/框架/基准（非综述/小增量）
  · **org** = 命中已知实验室白名单
  · **comment** = arXiv `comment` 或 `journal_ref` 非空
  · **hn** = **HN Algolia**（`https://hn.algolia.com/api/v1/search`）标题命中且 points>=5（+1）/ 弱命中（+0.5）
- **total = 0.6·rel + 0.4·q**（偏向与本线研工作的相关性）。

## 局限（诚实声明）

- 代理指标 **!=** 真实影响力：词表命中会**高估**同名但不同义的工作；`q` 的 org 白名单只看文本、拿不到 arXiv affiliations，**可能漏判/误判**。
- **HF Daily Papers 本机不可达（已实测 `Network is unreachable`）** → 社区热度**改用 HN Algolia 替代**；HN 以英文技术圈为主，**中文/冷门方向会低估**。
- `q` 的 code 代理只看摘要/comment 文本，**未逐个打开项目页核验**（避免犯 `200 != 有料` 的错）。
- 排序对 `w1/w2` 敏感；本文给出明确权重，便于复核与调整。

## TOP-5 导读（人工撰写 · 3-5 句/条）

> 说明：以下是**人工**对 TOP-5 的「为什么与我们在研工作相关」，3–5 句/条；
> 全部基于**标题 + 摘要 + arXiv comment**（未整篇精读），判断类语句标「**我们判断**」。
> 生成器每次重跑都会**自动嵌入本文件**（`--notes-md`），因此可与 `TOP_K.md` 保持一致。

- **#1 ExecCritic（2609.09133）**：它把**测试构造**与**代码修复**拆成两个角色，用 `test→verify→revise` 脚手架 + 角色化 RL 训练，正对口 ZhuLong 的 **generate–execute–refine 执行闭环** 与 **code agent** 方向；
  摘要明确 point out「patch 与 test 由同一轨迹生成会**同错而同信**（false confidence）」，这恰是我们在 EDA 代码任务里做**执行反馈可信度**时最该防的失效模式。**我们判断**：其「fail-closed harness 冻结测试」的设计可直接借鉴为 ZhuLong 的评测/判分护栏；
  有官方代码（`github.com/msr-orchard/execcritic`）与 35 页 tech report，属**可复现**的高价值条目。

- **#2 Rethinking Multi-Image Re-Representation（2609.39363）**：它把**多图理解**统一为「重表征」，并把 **prompted CoT** 与 **agentic 视觉工具调用**当作同一枚硬币的两面——这与 BaiZe 的 **多模态对齐** 与 ZhuLong 的 **工具/MCP** 两条线同时相交；
  其 **Mosaic** 用 10 个**可组合图像算子**主动构造视觉中间产物，本质上是「视觉侧的 harness」。**我们判断**：其新基准 **MosaicBench** 的「细粒度 grounding」评测口径，对 BaiZe 多模态对齐的验收有参考价值；代码在 `github.com/gengyuanmax/mosaic`。

- **#3 PainterBench（2609.34195）**：把人类**未完成图形发散思维**任务搬到 agent 场景：agent 经**工具调用**作画、每轮观察结果、自行决定何时收笔——是**工具使用 + 增量视觉规划**的干净基准；
  对 ZhuLong 的 **评测基准（SWE-bench 类）** 与 **工具/MCP** 很有启发：它展示了「开放式、无 golden answer、过程可观测」的任务如何被**可评测化**。**我们判断**：其「agent 自我终止」机制对长程 EDA 任务的**停止准则**设计有借鉴意义（25 页 / 7 图 / 11 表，规格扎实）。

- **#4 One to More, More to One（2609.23377）**：针对仓库级 SWE 的**类别跷跷板**（RL 后部分类别涨、部分类别退）提出**类别感知的专家训练 + 策略融合**，直击 ZhuLong **SWE 类 agent** 与 BaiZe **后训练（SFT/RL）** 的共同痛点；
  其「Executable task construction + SWE Labeler 多轴标注」把训练池**证据化组织**，方法与我们的**数据配比/可执行任务构造**诉求高度一致。**我们判断**：这是本轮**最贴近 ZhuLong 主线**的候选之一，且放出了 `Logics-SWE-Qwen3.6-27B` 权重与 44 页附录，**可复现性最强**。

- **#5 Faynt（2610.02144）⚠️**：它用 **10M/75M 参数的 Transformer 策略**+RL 在《任天堂明星大乱斗 Melee》上做到 98.4% 胜率，**代码/方法/机构(NVIDIA)/54 页**四项代理全中，故 `q=4.0`。
  **但须诚实标注**：这是**游戏 RL 的策略缩放**，与 LLM/SLM 主线的相关性**仅停留在「规模律 / RL 后训练 / 高效推理」这类泛词命中**——**我们判断**它很可能是**词表过配（over-match）**，建议人工降权。
  → **复核提示**：若按「与两条线的真实相关度」手排，**#18 Sharpening Tax in Post-Training（2610.01509）** 的优先级应更高：它发现**预训练 LLM + 轻量 inference harness 即可是能干 agent，且 pass@K（解空间覆盖）常胜过 post-trained 版本**——对 ZhuLong 的 **agent harness** 与 BaiZe 的 **后训练** 都是**反直觉且高信息量**的结论，只因缺 `code/org/comment` 代理而 `q` 偏低。

## TOP-20

| # | rel | q | total | 标题 | arXiv | 主分类 | 提交 |
|--:|--:|--:|--:|:--|:--|:--|:--|
| 1 | 4.5 | 4.0 | 4.3 | ExecCritic: Learn to Test, Test to Improve for Coding Agents | [2609.09133](https://arxiv.org/abs/2609.09133v1) | cs.AI | 2026-09-08 |
| 2 | 5.0 | 3.0 | 4.2 | Rethinking Multi-Image Re-Representation in Multi-Image Understanding | [2609.39363](https://arxiv.org/abs/2609.39363v1) | cs.CV | 2026-09-30 |
| 3 | 5.0 | 3.0 | 4.2 | PainterBench: A Figural Divergent-Thinking Benchmark for Tool-Using Language Models | [2609.34195](https://arxiv.org/abs/2609.34195v1) | cs.AI | 2026-09-28 |
| 4 | 5.0 | 3.0 | 4.2 | One to More, More to One: Category-Aware Iterative Expert Training for Software Engineering Agents | [2609.23377](https://arxiv.org/abs/2609.23377v1) | cs.SE | 2026-09-20 |
| 5 | 4.0 | 4.0 | 4.0 | Faynt: Scaling and Optimizing Policies for Competitive Melee | [2610.02144](https://arxiv.org/abs/2610.02144v1) | cs.LG | 2026-10-01 |
| 6 | 4.0 | 4.0 | 4.0 | DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression | [2609.19969](https://arxiv.org/abs/2609.19969v1) | cs.CL | 2026-09-17 |
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

- **#1 ExecCritic: Learn to Test, Test to Improve for Coding Agents**（arXiv:2609.09133）
  · 🔗 rel=4.5（BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·执行闭环(generate-execute-refine)；ZhuLong·评测基准）
  · 🏅 q=4.0（代码: 摘要/comment 提及代码或仓库（https://github.com/msr-orchard/execcritic.）；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（qwen）；arXiv comment/journal_ref: 35 pages；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.09133v1 ｜ pdf: https://arxiv.org/pdf/2609.09133v1 ｜ 💻 https://github.com/msr-orchard/execcritic.
- **#2 Rethinking Multi-Image Re-Representation in Multi-Image Understanding**（arXiv:2609.39363）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/gengyuanmax/mosaic.）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 27 pages, 7 figures, 9 tables；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.39363v1 ｜ pdf: https://arxiv.org/pdf/2609.39363v1 ｜ 💻 https://github.com/gengyuanmax/mosaic.
- **#3 PainterBench: A Figural Divergent-Thinking Benchmark for Tool-Using Language Models**（arXiv:2609.34195）
  · 🔗 rel=5.0（BaiZe·预训练/数据配比；BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 25 pages, 7 figures, 11 tables；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.34195v1 ｜ pdf: https://arxiv.org/pdf/2609.34195v1
- **#4 One to More, More to One: Category-Aware Iterative Expert Training for Software Engineering Agents**（arXiv:2609.23377）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理；ZhuLong·agent harness/code agent；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://huggingface.co/logics-mllm/logics-swe-qwen3.6-27b）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 44 pages, including appendices. Model available at https://huggingface.co/Logics；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.23377v1 ｜ pdf: https://arxiv.org/pdf/2609.23377v1 ｜ 💻 https://huggingface.co/logics-mllm/logics-swe-qwen3.6-27b
- **#5 Faynt: Scaling and Optimizing Policies for Competitive Melee**（arXiv:2610.02144）
  · 🔗 rel=4.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；BaiZe·高效推理；ZhuLong·评测基准）
  · 🏅 q=4.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（nvidia）；arXiv comment/journal_ref: 54 pages. Preprint, in review；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2610.02144v1 ｜ pdf: https://arxiv.org/pdf/2610.02144v1
- **#6 DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression**（arXiv:2609.19969）
  · 🔗 rel=4.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理）
  · 🏅 q=4.0（代码: 摘要/comment 提及代码或仓库（https://huggingface.co/deepseek-ai/deepseek-v4.1-flash.）；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（deepseek）；HN 热度: 命中《DeepSeek-v4.1 Flash: Pushing the Limits of KV Cache Compression》(131 points, 标题重合 100%)）
  · abs: https://arxiv.org/abs/2609.19969v1 ｜ pdf: https://arxiv.org/pdf/2609.19969v1 ｜ 💻 https://huggingface.co/deepseek-ai/deepseek-v4.1-flash.
- **#7 From Given to Gathered Evidence: Agentic Learning for Longitudinal Medical Reasoning**（arXiv:2609.39566）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（代码: 摘要/comment 提及代码或仓库（https://github.com/vinyehshaw/case.）；方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.39566v1 ｜ pdf: https://arxiv.org/pdf/2609.39566v1 ｜ 💻 https://github.com/vinyehshaw/case.
- **#8 Codoku: Renewable Program-Reasoning Challenges for Frontier Coding Agents**（arXiv:2609.34661）
  · 🔗 rel=5.0（BaiZe·小模型/端侧；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（代码: 摘要/comment 提及代码或仓库（https://github.com/connglli/codoku.）；方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.34661v1 ｜ pdf: https://arxiv.org/pdf/2609.34661v1 ｜ 💻 https://github.com/connglli/codoku.
- **#9 Qwen-Audio-3.1-Realtime: Towards Reliable Agentic Voice Interaction**（arXiv:2609.25176）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·高效推理；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP）
  · 🏅 q=2.0（机构/作者: 命中已知实验室白名单（qwen）；arXiv comment/journal_ref: 25 pages, technical report；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.25176v2 ｜ pdf: https://arxiv.org/pdf/2609.25176v2
- **#10 GroundingPI: A Grounding Foundation Model towards Physical Intelligence with Visual Primitives**（arXiv:2609.39601）
  · 🔗 rel=4.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；BaiZe·高效推理）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/groundingpi/groundingpi）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 64 pages, including supplementary material. Project page: https://groundingpi.gi；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.39601v1 ｜ pdf: https://arxiv.org/pdf/2609.39601v1 ｜ 💻 https://github.com/groundingpi/groundingpi
- **#11 SRJudge: Empowering Large Language Models with Selective Reasoning for Fine-Grained Knowledge Concept Tagging**（arXiv:2609.36982）
  · 🔗 rel=4.0（BaiZe·后训练(SFT/RL)；BaiZe·小模型/端侧；BaiZe·高效推理；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/nicozwy/srjudge.）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: Accepted by IJCAI 2026；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.36982v1 ｜ pdf: https://arxiv.org/pdf/2609.36982v1 ｜ 💻 https://github.com/nicozwy/srjudge.
- **#12 Qwen-Planner-Agent: A Closed-Loop AI-for-AI Framework for Real-World Mobile Planner Agents**（arXiv:2609.29892）
  · 🔗 rel=4.0（BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP）
  · 🏅 q=3.0（方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（qwen）；arXiv comment/journal_ref: https://tongyi-mai.github.io/Qwen-Planner-Agent/；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.29892v1 ｜ pdf: https://arxiv.org/pdf/2609.29892v1
- **#13 IndicBankBench: Evaluating Safety and Reliability of Language Model Assistants in Indian Retail Banking**（arXiv:2609.29167）
  · 🔗 rel=4.0（ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 16 pages, 4 figures；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.29167v1 ｜ pdf: https://arxiv.org/pdf/2609.29167v1
- **#14 Qwen3.8-Omni: Towards Native Omni-Modal Agents**（arXiv:2609.25611）
  · 🔗 rel=4.0（BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库；方法/基准: 提出新方法/框架/基准（非小增量）；机构/作者: 命中已知实验室白名单（qwen）；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.25611v1 ｜ pdf: https://arxiv.org/pdf/2609.25611v1
- **#15 On the Recall Scaling Laws in Mamba: A Theoretical and Mechanistic Study via Hashing**（arXiv:2609.07681）
  · 🔗 rel=4.0（BaiZe·Mamba/混合架构；BaiZe·规模律；ZhuLong·评测基准）
  · 🏅 q=3.0（代码: 摘要/comment 提及代码或仓库（https://github.com/yuvalko1/mamba-recall-scaling-laws）；方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 53 pages, 20 figures. Code and experiments available at: https://github.com/yuva；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.07681v1 ｜ pdf: https://arxiv.org/pdf/2609.07681v1 ｜ 💻 https://github.com/yuvalko1/mamba-recall-scaling-laws
- **#16 CineMR: Tool-Integrated Vision-Language Reasoning for Quantitative Cardiac MRI Assessment**（arXiv:2610.01166）
  · 🔗 rel=4.5（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（代码: 摘要/comment 提及代码或仓库（https://github.com/ai-mind-lab/cinemr.）；arXiv comment/journal_ref: Code, benchmark resources, and model weights are available at https://github.com；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2610.01166v1 ｜ pdf: https://arxiv.org/pdf/2610.01166v1 ｜ 💻 https://github.com/ai-mind-lab/cinemr.
- **#17 EgoTools: Towards Tool-Centric Reasoning in Real-World Egocentric Videos**（arXiv:2609.39378）
  · 🔗 rel=4.5（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=2.0（方法/基准: 提出新方法/框架/基准（非小增量）；arXiv comment/journal_ref: 32 pages, 7 figures. Project page: https://ropedia.github.io/egotools；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.39378v1 ｜ pdf: https://arxiv.org/pdf/2609.39378v1
- **#18 Sharpening Tax in Post-Training**（arXiv:2610.01509）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=1.0（方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2610.01509v1 ｜ pdf: https://arxiv.org/pdf/2610.01509v1
- **#19 QuantCode Model: Specializing Language Models for Executable Algorithmic Trading Code**（arXiv:2609.39420）
  · 🔗 rel=5.0（BaiZe·预训练/数据配比；BaiZe·后训练(SFT/RL)；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=1.0（arXiv comment/journal_ref: 16 pages, 2 figures, 6 tables；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.39420v1 ｜ pdf: https://arxiv.org/pdf/2609.39420v1
- **#20 Visual Parallel Search: Learning to Search High-Resolution Images with Parallel Tile Inspection and Adaptive Zoom**（arXiv:2609.37002）
  · 🔗 rel=5.0（BaiZe·后训练(SFT/RL)；BaiZe·多模态对齐；ZhuLong·agent harness/code agent；ZhuLong·工具/MCP；ZhuLong·评测基准）
  · 🏅 q=1.0（方法/基准: 提出新方法/框架/基准（非小增量）；HN 热度: 无显著命中（nbHits=0））
  · abs: https://arxiv.org/abs/2609.37002v2 ｜ pdf: https://arxiv.org/pdf/2609.37002v2

