# 经典论文清单（B 轨 · 滚动维护）

> 依据：`WATCH_RESEARCH_TASK.md` 用户令 2026-11-11（research 50% 时间看经典论文 + 建作者关系网 + 跟踪顶级研究者言论）。
> 本清单**不占**每日 5 篇新论文额度（那是 A 轨）；**不删旧条目**，新增条目标 `首次收录: YYYY-MM-DD`；累计 50+ 后转「补充 / 更正」为主。
>
> **「经典」判据（满足任一 + 与本线在研方向相关）**：① 被引 ≥500；② 开创某一范式；③ 方法论常青（至今被新论文反复对比）；④ 本领域（EDA / LLM-for-EDA / 存储）标志性工作。
>
> **被引数来源（硬口径）**：`OpenAlex API`（`api.openalex.org/works/https://doi.org/10.48550/arxiv.<ID>`），**逐条注明查询日期**。
> ⚠️ 首轮（11:3x）`api.semanticscholar.org` 连续返回 `HTTP 429 Too Many Requests`（两次实测）⇒ **S2 未查**，不写估算值；第二轮**未再请求 S2**（仍记为「未查」）。Google Scholar 本机不可达。**不同来源被引数口径不同，禁止跨源比较**。
>
> **元数据核验**：标题 / 首次提交日 均取自 arXiv 官方 API（`export.arxiv.org/api/query?id_list=...`，2026-11-11 两轮实测 `HTTP 200` + `application/atom+xml; charset=utf-8`，首轮 4/4、第二轮 4/4 = 累计 8/8）。

**本轮快照**：累计 **19** 条（首轮 11:5x 收 4 条；第二轮 11:4x 补 4 条 EDA / agent / PEFT；第三轮 12:1x 补 4 条 RoPE / SWE-bench / Reflexion / CoT；第四轮 12:4x 补 3 条 GPT-3 / InstructGPT / LLaMA；**第五轮 15:0x 补 4 条** ResNet / seq2seq / Dyna / LLaVA）｜ 覆盖（一篇可服务多线，故合计数 > 19）：pretrain **12** · vision **4** · harness **5** · data **5** · zhulong **10** · designflow **4**

> 🆕 **第四轮（2026-11-11 12:4x）新增 3 条 = 「规模 → 指令 → 开放权重」三段主线**：GPT-3（few-shot 能力从哪来）→ InstructGPT（对齐/指令跟随的范式起点）→ LLaMA（用「多 token」把开放权重做到可用）。三篇合起来回答 data 线当前最实际的问题：**token 预算、指令数据、公开配比**。
>
> 🆕 **第五轮（2026-11-11 15:0x）新增 4 条 = 「视觉塔 + 序列到序列 + 模型式规划」**：ResNet（视觉塔的对照基线）→ LLaVA（图文对齐的最小可行配方）补上第四轮显式留空的 **vision 空档**；seq2seq（定长瓶颈的历史证据）与 Dyna（model-based 规划的范式起点）分别给 pretrain 的长上下文 ROI 与 harness 的 plan/act 预算提供参照。**必读清单覆盖度：本轮后 7/10 组已有一条以上落点**（缺：AlphaGo 系 / DeepMind 家族其余 / Kimi·GLM·MiniMax / VLA·SORA / GPT-1·GPT-2）。

---

## 1. Attention Is All You Need

| 字段 | 内容 |
|:--|:--|
| 标题 | Attention Is All You Need |
| 作者（前 3） | Ashish Vaswani · Noam Shazeer · Niki Parmar（et al.，共 8 位） |
| 年份 | 2017（arXiv 首次提交 **2017-06-12**） |
| 会议 / 期刊 | **NeurIPS 2017**（Advances in NeurIPS 30, pp. 5998–6008；OpenAlex `primary_location` 记为 arXiv 版，biblio 卷 30 / 页 5998–6008） |
| 被引数 | **136,007**（OpenAlex，查询日 2026-11-11；S2 本轮 429 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1706.03762> ｜ DOI `10.48550/arxiv.1706.03762` |
| 一句话贡献 | 用「多头自注意力 + 残差 + LayerNorm + FFN」的纯注意力堆叠替掉 RNN/CNN，训练可完全并行，从此序列建模可以随算力一起放大。 |
| 与我们工作的关系 | **pretrain（基线）**：BaiZe 2B 的 block 结构、位置编码（绝对 → RoPE）、pre-LN、GQA/MQA 全是这条线的变体对照，本文是「对照组」本身。<br>**zhulong（消融基线）**：任何架构类消融（线性注意力 / SSM / 循环深度）都以此为等参数、等 token 的参照。<br>**读法建议**：不必重读全文，重点看 §3.2 的缩放（`d_model/head` 与 FLOPs 口径）——各线报「等价预算」时要能对齐这份口径。 |

首次收录: 2026-11-11 ｜ 状态: 已核验元数据

---

## 2. Training Compute-Optimal Large Language Models（Chinchilla）

| 字段 | 内容 |
|:--|:--|
| 标题 | Training Compute-Optimal Large Language Models |
| 作者（前 3） | Jordan Hoffmann · Sebastian Borgeaud · Arthur Mensch（et al.，DeepMind） |
| 年份 | 2022（arXiv 首次提交 **2022-03-29**） |
| 会议 / 期刊 | **NeurIPS 2022**（pp. 30016–30030） |
| 被引数 | **4,612**（OpenAlex，查询日 2026-11-11；S2 本轮 429 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2203.15556> ｜ DOI `10.48550/arxiv.2203.15556` |
| 一句话贡献 | 用 400+ 个模型的三种拟合方法得出：给定算力时**参数量与训练 token 数应同比例放大**（约 20 token/参数），当时主流大模型普遍「参数过大、训练不足」。 |
| 与我们工作的关系 | **data（直接）**：BaiZe 2B 的 token 预算与配比实验，选点要能对得上「20 token/参数」这条经验线（作者自报结论，未经本线复现）。<br>**pretrain**：学习率 schedule / 训练步数配比（700k step 的量级）应随 token 数同调，而不是只按参数量调。<br>**zhulong（方法论）**：「等**计算**预算对比」而非「等步数」——消融表里必须写清 token / FLOPs 口径。 |

首次收录: 2026-11-11 ｜ 状态: 已核验元数据

---

## 3. FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness

| 字段 | 内容 |
|:--|:--|
| 标题 | FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness |
| 作者（前 3） | Tri Dao · Daniel Y. Fu · Stefano Ermon（et al.，共 5 位；Stanford） |
| 年份 | 2022（arXiv 首次提交 **2022-05-27**） |
| 会议 / 期刊 | **NeurIPS 2022**（Advances in NeurIPS 35, pp. 16344–16359；OpenAlex `raw_source_name` 实测确认） |
| 被引数 | **2,057**（OpenAlex，查询日 2026-11-11；S2 本轮 429 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2205.14135> ｜ DOI `10.48550/arxiv.2205.14135` |
| 一句话贡献 | 把 attention 计算按 **SRAM / HBM 层级分块（tiling）+ 反向重算**，不做近似就把 HBM 读写降下来，得到精确注意力的 2–4× 加速与线性显存。 |
| 与我们工作的关系 | **pretrain（吞吐 / 长上下文）**：训练吞吐瓶颈常在 attention 的 **HBM 流量**而非 FLOPs，BaiZe 的长上下文实验排障应按这个视角看。<br>**harness（成本口径）**：单 token 成本拆解里 attention kernel 的占比，直接决定长上下文任务的 wall-clock 预算。<br>**本轮已据此给作者发请教信**（见 `research/mail/drafts/2205.14135.md`）。 |

首次收录: 2026-11-11 ｜ 状态: 已核验元数据 + 作者已发信

---

## 4. Mamba: Linear-Time Sequence Modeling with Selective State Spaces

| 字段 | 内容 |
|:--|:--|
| 标题 | Mamba: Linear-Time Sequence Modeling with Selective State Spaces |
| 作者（前 3） | Albert Gu · Tri Dao（共 2 位；CMU · Princeton） |
| 年份 | 2023（arXiv 首次提交 **2023-12-01**） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex 未标会议；其正式发表版本本轮**未核验**，故不写会议名） |
| 被引数 | **7,496**（OpenAlex，查询日 2026-11-11；S2 本轮 429 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2312.00752> ｜ DOI `10.48550/arxiv.2312.00752` |
| 一句话贡献 | 让 SSM 的离散化步长随输入变化（selective / S6），配合硬件感知的并行扫描，做到线性时间序列建模，语言建模上首次与同规模 Transformer 可比。 |
| 与我们工作的关系 | **zhulong（架构消融）**：Transformer vs 线性注意力 / SSM / 混合比例，是当前最主流的对照轴；本文给出「线性时间 + 内容选择」的标准基线。<br>**pretrain（长上下文吞吐）**：若做长上下文压缩，S6 的选择性机制是可对照的替代方案（注意：线性时间 ≠ GPU 上更快，实际吞吐依赖 kernel，见 FlashAttention 同作者）。 |

首次收录: 2026-11-11 ｜ 状态: 已核验元数据（会议信息未核验）

---

## 5. ChipNeMo: Domain-Adapted LLMs for Chip Design

| 字段 | 内容 |
|:--|:--|
| 标题 | ChipNeMo: Domain-Adapted LLMs for Chip Design |
| 作者（前 3） | Mingjie Liu · Teodor-Dumitru Ene · Robert Kirby（et al.，共 42 位；NVIDIA） |
| 年份 | 2023（arXiv 首次提交 **2023-10-31**，v5 更新 2024-04-04） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex 仅记 arXiv 版，未标会议；正式发表版本本轮**未核验** ⇒ 不写会议名） |
| 被引数 | **357**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2311.00176> ｜ DOI `10.48550/arxiv.2311.00176` |
| 一句话贡献 | 不做通用大模型的直接部署，而是走「领域 tokenizer + 领域继续预训练 + 领域指令对齐 + 领域检索」四件套，在工程助手、EDA 脚本生成、bug 归纳三个用例上验证；作者自报 ChipNeMo-70B 在其中两个用例上优于 GPT-4。 |
| 与我们工作的关系 | **designflow（造题口径）**：它把「芯片设计 LLM 用例」拆成三类可评测任务，我们造 agent 题时可对齐这个分类，避免所有题都退化成「写一段 Verilog」。<br>**zhulong（领域适配消融）**：「继续预训练 vs 检索 vs tokenizer」是可拆的消融轴，正好对应 zhulong 的消融表设计。<br>**pretrain（2B 路线）**：作者自报 70B 才在部分用例超 GPT-4 ⇒ 2B 级模型的领域适配收益上限必须实测，不能照搬结论。 |

首次收录: 2026-11-11（第二轮）｜ 状态: 已核验元数据 + 已发信（公司公开信箱）

---

## 6. ReAct: Synergizing Reasoning and Acting in Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | ReAct: Synergizing Reasoning and Acting in Language Models |
| 作者（前 3） | Shunyu Yao · Jeffrey Zhao · Dian Yu（et al.，共 7 位；Princeton · Google Research） |
| 年份 | 2022（arXiv 首次提交 **2022-10-06**；v3 = ICLR camera-ready） |
| 会议 / 期刊 | **ICLR 2023**（arXiv `comment` 实测「v3 is the ICLR camera ready version」；作者主页标注 Oral / top 5%） |
| 被引数 | **5,814**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2210.03629> ｜ DOI `10.48550/arxiv.2210.03629` |
| 一句话贡献 | 让模型把「推理轨迹」和「任务动作」交错生成：推理负责归纳/跟踪/修正计划与处理异常，动作负责从外部环境取新信息，从而在问答与交互决策任务上同时改善效果与可解释性。 |
| 与我们工作的关系 | **harness（骨架来源）**：现在所有 code agent harness 的「think → tool call → observation」循环都可追到这篇；我们的上下文压缩、重复 action 检测、失败归因都在这个循环上做。<br>**harness（成本口径）**：轨迹里 reasoning 与 tool 输出谁更占 token，直接决定压缩策略；本轮已就此给作者发信。<br>**data（轨迹数据）**：若自造 agent 轨迹数据，这篇的「交错格式」是最小可用模板。 |

首次收录: 2026-11-11（第二轮）｜ 状态: 已核验元数据 + 已发信（`shunyuy@princeton.edu`）

---

## 7. VerilogEval: Evaluating Large Language Models for Verilog Code Generation

| 字段 | 内容 |
|:--|:--|
| 标题 | VerilogEval: Evaluating Large Language Models for Verilog Code Generation |
| 作者（前 3） | Mingjie Liu · Nathaniel Pinckney · Brucek Khailany（et al.，共 4 位；NVIDIA） |
| 年份 | 2023（arXiv 首次提交 **2023-09-14**） |
| 会议 / 期刊 | **ICCAD 2023（Invited Paper）**（arXiv `comment` 实测；OpenAlex 另记 DOI `10.1109/iccad57390.2023.10323812`） |
| 被引数 | **346**（OpenAlex，查询日 2026-11-11；该源标题带 `Invited Paper:` 前缀；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2309.07544> ｜ DOI `10.48550/arxiv.2309.07544` |
| 一句话贡献 | 从 HDLBits 取 156 道题构成 Verilog 生成基准，用「生成设计 vs 标准答案的瞬态仿真输出比对」做**自动功能正确性判分**，并示范用 LLM 合成题解对做监督微调可提升生成能力。 |
| 与我们工作的关系 | **designflow（判分可验证性）**：这是我们 L1–L5 保真度里「可自动判分」一档的现成参照——判据是仿真输出等价，不是文本相似。<br>**designflow（造题）**：156 题的难度梯度（组合电路 → 复杂 FSM）可作为我们造题分布的下限基线。<br>**风险（已写进信里）**：仿真通过 ≠ 设计意图正确；若我们的题只测仿真，会把「碰巧过测试」判成对。 |

首次收录: 2026-11-11（第二轮）｜ 状态: 已核验元数据

---

## 8. LoRA: Low-Rank Adaptation of Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | LoRA: Low-Rank Adaptation of Large Language Models |
| 作者（前 3） | Edward J. Hu · Yelong Shen · Phillip Wallis（et al.，共 8 位；Microsoft） |
| 年份 | 2021（arXiv 首次提交 **2021-06-17**） |
| 会议 / 期刊 | **ICLR 2022**（本轮**未从可访问来源核验**；arXiv API 无 `journal_ref` / `comment` ⇒ 仅作参考，勿当已核验事实引用） |
| 被引数 | **14,411**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2106.09685> ｜ DOI `10.48550/arxiv.2106.09685` |
| 一句话贡献 | 冻结原权重，只训练注入到每层的低秩分解矩阵（`B·A`），把可训练参数降几个数量级，且推理时可将 `BA` 合并回原权重、不增加延迟。 |
| 与我们工作的关系 | **vision（波形 RL / 小样本）**：LoRA 是「小样本 + 低算力」微调的默认起点；vision 线做 CPU 训练时必须先确认 LoRA 是否足以承载波形任务。<br>**pretrain（PEFT 对照）**：若 BaiZe 2B 要做领域适配，LoRA / 全参继续预训练的对比是标准消融轴。<br>**评估风险**：作者自报「推理无额外延迟」的前提是合并权重；多适配器切换场景下该前提不成立。 |

首次收录: 2026-11-11（第二轮）｜ 状态: 已核验元数据（会议未核验）

---

## 9. RoFormer: Enhanced Transformer with Rotary Position Embedding

| 字段 | 内容 |
|:--|:--|
| 标题 | RoFormer: Enhanced Transformer with Rotary Position Embedding |
| 作者（前 3） | Jianlin Su · Yu Lu · Shengfeng Pan（et al.，共 6 位；Zhuiyi Technology, Shenzhen） |
| 年份 | 2021（arXiv 首次提交 **2021-04-20**；v5 = 2023-11-08） |
| 会议 / 期刊 | **Neurocomputing**（OpenAlex `primary_location.source` 实测：vol. 568, 127063；arXiv 元数据无 `journal_ref` / `comment` 会议信息） |
| 被引数 | **3,867**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2104.09864> ｜ DOI `10.48550/arxiv.2104.09864` |
| 一句话贡献 | 把位置信息写成「按绝对位置旋转 query/key 向量」的乘法形式，使注意力分数只依赖相对位移，且不增加参数；外推与长文性能优于绝对位置编码与当时的口径。 |
| 与我们工作的关系 | **pretrain（直接）**：RoPE 是 BaiZe 位置编码的默认选择，本文是 θ 基频 / 外推（NTK、YaRN 等后续工作）的源头 ⇒ 长上下文实验排障时必须能回到「旋转角随位置线性增长」这一条。<br>**zhulong（消融口径）**：任何位置编码消融（绝对 / 相对 / RoPE / NoPE）都以此为等参数对照。<br>**风险**：论文自报的长文外推收益依赖具体实现，训练长度外的退化曲线要用我们自己的长度扫描验，不能直接引用结论。 |

首次收录: 2026-11-11（第三轮）｜ 状态: 已核验元数据（机构 = OpenAlex `raw_affiliation_strings` 实测）

---

## 10. SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

| 字段 | 内容 |
|:--|:--|
| 标题 | SWE-bench: Can Language Models Resolve Real-World GitHub Issues? |
| 作者（前 3） | Carlos E. Jimenez · John Yang · Alexander Wettig（et al.，共 7 位；Princeton · UChicago） |
| 年份 | 2023（arXiv 首次提交 **2023-10-10**；v3 = 2024-11-11） |
| 会议 / 期刊 | **ICLR 2024**（arXiv `comment` 实测含「ICLR 2024」；OpenAlex 只记 arXiv 版） |
| 被引数 | **2,078**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2310.06770> ｜ DOI `10.48550/arxiv.2310.06770` |
| 一句话贡献 | 从 12 个真实 Python 仓库的 issue + 合并 PR 里抽出 2,294 个任务，用「仓库自带测试是否从 fail 变 pass」自动判分，把「修真实 bug」变成可规模化评测的基准。 |
| 与我们工作的关系 | **harness（协议来源）**：我们 7 路评测的「resolved / pass@k / 重试」口径都源自这里；本文的价值在**判分协议**（FAIL_TO_PASS + PASS_TO_PASS）而不是分数本身。<br>**designflow（判分可验证性）**：这正是「判据 = 可执行测试」的范本 —— 我们的 RTL/波形题若要做自动判分，应照此把「必须由错变对」与「必须保持正确」两类断言分开写。<br>**风险**：仓库测试覆盖不足 ⇒ 过测试 ≠ bug 真被修对（后续 SWE-bench+ / SWE-ABS 一类工作正是补这个洞）。 |

首次收录: 2026-11-11（第三轮）｜ 状态: 已核验元数据

---

## 11. Reflexion: Language Agents with Verbal Reinforcement Learning

| 字段 | 内容 |
|:--|:--|
| 标题 | Reflexion: Language Agents with Verbal Reinforcement Learning |
| 作者（前 3） | Noah Shinn · Federico Cassano · Edward Berman（et al.，共 6 位；发表时 Northeastern University · Princeton） |
| 年份 | 2023（arXiv 首次提交 **2023-03-20**；v4 = 2023-10-10） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `primary_location.source` = neural information processing systems，pp. 8634–8652；arXiv 无 `journal_ref`） |
| 被引数 | **3,297**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2303.11366> ｜ DOI `10.48550/arxiv.2303.11366` |
| 一句话贡献 | 不更新权重，把「失败原因」写成自然语言反思存进情节记忆，下一轮把它放进上下文再试，从而用「语言梯度」替代策略梯度来改进 agent 的重复尝试。 |
| 与我们工作的关系 | **harness（重试策略）**：我们现在的重试只是「再来一次」，本文给出另一种做法：把失败信号蒸馏成可复用的教训。关键待验问题是「反思 vs 直接带测试反馈重试」谁更划算。<br>**zhulong（agent 侧消融）**：可作为「记忆 / 反思」这一轴的基线条件（无记忆 → 原始轨迹 → 蒸馏反思）。<br>**风险**：反思会累积成上下文膨胀；对「测试即真值」的任务，反思可能只是变相增加尝试次数（本轮已就此给作者发信）。 |

首次收录: 2026-11-11（第三轮）｜ 状态: 已核验元数据 + 已发信（`noahrshinn@gmail.com`）

---

## 12. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Chain-of-Thought Prompting Elicits Reasoning in Large Language Models |
| 作者（前 3） | Jason Wei · Xuezhi Wang · Dale Schuurmans（et al.，共 9 位） |
| 年份 | 2022（arXiv 首次提交 **2022-01-28**；v6 = 2023-01-10） |
| 会议 / 期刊 | **NeurIPS 2022**（OpenAlex `primary_location.source` = neural information processing systems，pp. 24824–24837；arXiv 无 `journal_ref`） |
| 被引数 | **13,949**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2201.11903> ｜ DOI `10.48550/arxiv.2201.11903` |
| 一句话贡献 | 在 few-shot 提示里给出「中间推理步骤」的示例，让足够大的模型在数学/常识/符号推理上显著提升；并指出这是**随规模涌现**的能力，小模型写出流畅但不合逻辑的链反而更差。 |
| 与我们工作的关系 | **zhulong（thinking 轴的理论依据）**：「显式推理 token 是否值得」这件事的成本账要从这里起算 —— 收益随规模涌现，2B 级未必成立，必须自己做规模扫描。<br>**pretrain（数据侧）**：若 SFT 数据里混入推理链，要区分「示范格式」与「真实可验证推理」，否则学到的只是句式。<br>**风险**：CoT 的「可解释」是形式上的，不等于忠实反映模型内部计算（2026 年已有专门工作反驳）。 |

首次收录: 2026-11-11（第三轮）｜ 状态: 已核验元数据 + 已发信（`jason.weng.wei@gmail.com`）

---

## 13. Language Models are Few-Shot Learners（GPT-3）

| 字段 | 内容 |
|:--|:--|
| 标题 | Language Models are Few-Shot Learners |
| 作者（前 3） | Tom B. Brown · Benjamin Mann · Nick Ryder（et al.，**31 位**，OpenAlex `authorships` 实测） |
| 年份 | 2020（arXiv 首次提交 **2020-05-28**；v4 = 2020-07-22，`arXiv:2005.14165` abs 页实测） |
| 会议 / 期刊 | **NeurIPS 2020**（OpenAlex `biblio` = 卷 33 / 页 1877–1901） |
| 被引数 | **33,665**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2005.14165> ｜ DOI `10.48550/arxiv.2005.14165` |
| 一句话贡献 | 把模型放大到 175B、不做任何梯度更新，仅靠**上下文里的几个示例（in-context learning）**就能做新任务；并系统记录了「能力随规模提升、且部分任务呈**涌现**」的曲线。 |
| 与我们工作的关系 | **pretrain（规模假设的原始表述）**：BaiZe 2B 属于「小模型」区间 —— 本文的结论**不能直接外推**，但它定义了我们必须自己回答的问题：2B 上 in-context 学习是否还成立、示例数收益在第几个 shot 饱和。<br>**data（评测口径）**：本文的 few-shot / one-shot / zero-shot 三分法，是各线报「同任务不同 shot 数」时必须写清的口径来源。<br>**zhulong（消融对照）**：任何「小模型 + 更多数据 / 更长训练」的取舍，都是对本文「纯放大」路线的一次反问。<br>**风险**：作者自报数字均未复现；涌现结论在后续工作中有争议（阈值对度量方式敏感）。 |

首次收录: 2026-11-11（第四轮）｜ 状态: 已核验元数据（标题 / 日期取自 `arxiv.org/abs` 实测 `200`）

---

## 14. Training language models to follow instructions with human feedback（InstructGPT）

| 字段 | 内容 |
|:--|:--|
| 标题 | Training language models to follow instructions with human feedback |
| 作者（前 3） | Long Ouyang · Jeff Wu · Xu Jiang（et al.，OpenAI） |
| 年份 | 2022（arXiv 首次提交 **2022-03-04**，`arXiv:2203.02155` abs 页实测） |
| 会议 / 期刊 | **NeurIPS 2022**（OpenAlex `biblio` 未记页码 ⇒ **页码未核验**，不填补） |
| 被引数 | **8,059**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2203.02155> ｜ DOI `10.48550/arxiv.2203.02155` |
| 一句话贡献 | 用「人类偏好标注 → 训练奖励模型 → PPO 微调」三步（RLHF），让 1.3B 的 InstructGPT 在人类偏好上**胜过 175B 的 GPT-3**；并指出对齐训练的代价是通用基准上的轻微退化（alignment tax）。 |
| 与我们工作的关系 | **zhulong（对齐轴基线）**：ZhuLong 若做指令微调 / 偏好优化，1.3B > 175B 这一条是「小模型靠对齐翻盘」的最强历史证据，值得作为**预注册判据**的参照（不是结论）。<br>**pretrain（数据侧）**：SFT 数据量与多样性比模型规模更稀缺 —— 与我们 2B 规模的现实约束一致。<br>**data（成本口径）**：偏好标注成本必须进「解出任务成本」的账，否则 RLHF 的收益会被高估。<br>**风险**：奖励模型会放大标注者偏好（谄媚 / 长度偏置），评测若只看人类偏好会形成闭环。 |

首次收录: 2026-11-11（第四轮）｜ 状态: 已核验元数据（会议页码未核验，如实留空）

---

## 15. LLaMA: Open and Efficient Foundation Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | LLaMA: Open and Efficient Foundation Language Models |
| 作者（前 3） | Hugo Touvron · Thibaut Lavril · Gautier Izacard（et al.，Meta AI） |
| 年份 | 2023（arXiv 首次提交 **2023-02-27**，`arXiv:2302.13971` abs 页实测） |
| 会议 / 期刊 | 预印本（abs 页**无** `journal_ref` / `comments` ⇒ **会议未核验**） |
| 被引数 | **23,690**（OpenAlex，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2302.13971> ｜ DOI `10.48550/arxiv.2302.13971` |
| 一句话贡献 | 用**远超「Chinchilla 最优」的 token 数**（7B–65B 训 1.0–1.4T token）证明：给定**推理预算**而不是训练预算时，小模型多训更划算；并公开了配方（公开数据 + 不额外私有数据）。 |
| 与我们工作的关系 | **data（直接）**：BaiZe 2B 的 token 预算选点，本文与 Chinchilla 是**两条相反的经验线**（≤20 vs ≫20 token/参数）—— 我们必须自己扫一遍，不能引用任何一条当结论。<br>**pretrain（配方）**：全部来自公开数据这一点，对我们的数据合规与可复现性有参考价值。<br>**zhulong（成本口径）**：「训练成本」与「推理成本」谁主导，会直接改变「小模型多训」的取舍结论 —— 消融表要写明按哪个记账。<br>**风险**：本文被引数高但有大量二手解读混淆「LLaMA 1」与「LLaMA 2」的许可与数据口径。 |

首次收录: 2026-11-11（第四轮）｜ 状态: 已核验元数据（会议未核验）

---

## 16. Deep Residual Learning for Image Recognition（ResNet）

| 字段 | 内容 |
|:--|:--|
| 标题 | Deep Residual Learning for Image Recognition |
| 作者（前 3） | Kaiming He · Xiangyu Zhang · Shaoqing Ren（et al.，共 4 位；发表时 Microsoft Research） |
| 年份 | 2016（arXiv 首次提交 **2015-12-10**，`arxiv.org/abs/1512.03385` 实测；CVPR 2016 会议期 2016-06，Crossref 实测） |
| 会议 / 期刊 | **CVPR 2016**，pp. **770–778**（Crossref `10.1109/cvpr.2016.90` 实测） |
| 被引数 | **243,173**（OpenAlex，**CVPR 版** DOI `10.1109/cvpr.2016.90`，查询日 2026-11-11）<br>⚠️ 同一论文的 **arXiv 记录**为 **12,953**（`10.48550/arxiv.1512.03385`）—— **两条记录口径不同，不相加、不跨记录比较** |
| arXiv / DOI | <https://arxiv.org/abs/1512.03385> ｜ DOI `10.1109/CVPR.2016.90`（CVPR 版）/ `10.48550/arxiv.1512.03385`（arXiv 版） |
| 一句话贡献 | 把每层改成学**残差** `F(x)=H(x)−x` 并加**恒等 shortcut**，让 152 层网络（比 VGG 深 8×、复杂度更低）可训练并拿到 ILSVRC 2015 分类第一（集成 ImageNet test **3.57%** error）；CIFAR-10 上验证到 100 / 1000 层，COCO 检测因「表征更深」获 **28%** 相对提升。 |
| 与我们工作的关系 | **vision（视觉塔基线，直接）**：工业图像（版图 / 波形 / 显微图）数据量远小于 ImageNet，conv+残差仍是低数据下的强基线 ⇒ 我们的视觉塔选型必须把「ResNet 类 vs ViT 类」做成等参数量对照，而不是只比公开榜单。<br>**pretrain（结构直觉）**：恒等 shortcut 提供梯度直达通路，与 pre-LN 残差流是同一类「不退化」机制 —— 判断「加深是否白加」时用它做参照。<br>**zhulong（联训稳定性）**：视觉塔冻结 / 端到端两种接法，残差尺度与初始化会改变 2B 主干的早期 loss 抖动，消融表要单列这一项。<br>**designflow（现成基线）**：L1–L3 保真度里「图像分类 / 缺陷检测」档可直接复用该结构。<br>**风险**：① 3.57% 是 2015 年 ImageNet 口径，数据域与我们的差异极大，🚫 不可当预期收益；② BN 的 batch 统计在小 batch / 分布式切分下不稳，且与 LLM 的 LN 栈不统一 —— 复用前要先决定 BN / GN / LN 与是否冻结。 |

首次收录: 2026-11-11（第五轮）｜ 状态: 已核验元数据（会议与页码经 Crossref 实测；被引数按 DOI 分记录单列）

---

## 17. Sequence to Sequence Learning with Neural Networks（seq2seq）

| 字段 | 内容 |
|:--|:--|
| 标题 | Sequence to Sequence Learning with Neural Networks |
| 作者（前 3） | Ilya Sutskever · Oriol Vinyals · Quoc V. Le（共 3 位；发表时 Google） |
| 年份 | 2014（arXiv 首次提交 **2014-09-10** v1；v3 = 2014-12-14，`arxiv.org/abs/1409.3215` 实测） |
| 会议 / 期刊 | **NeurIPS (NIPS) 2014**（官方论文集索引 `papers.nips.cc/paper_files/paper/2014` **实测命中**该标题；⚠️ **页码本轮未核验**，不填补） |
| 被引数 | **18,379**（OpenAlex，arXiv 记录 `10.48550/arxiv.1409.3215`，查询日 2026-11-11；会议版无独立 OpenAlex 记录 ⇒ 只有单条记录，无跨记录问题） |
| arXiv / DOI | <https://arxiv.org/abs/1409.3215> ｜ DOI `10.48550/arxiv.1409.3215` |
| 一句话贡献 | 用「多层 LSTM 编码 → **固定维向量** → 另一多层 LSTM 解码」端到端做序列到序列，WMT'14 英法整测试集 **BLEU 34.8**（当时 phrase-based SMT 为 **33.3**）；发现**把输入句反序**能显著改善长句依赖；并首次系统证明「定长向量能承载句子语义」。 |
| 与我们工作的关系 | **pretrain（长上下文 ROI 的历史参照）**：定长瓶颈正是后来 attention 与长上下文的动因 —— 我们评估「窗口从 8K 加到 128K 值不值」时，要能回到这条最原始的瓶颈证据，而不是只看新论文的自报收益。<br>**data（混淆项）**：输入反序这一 trick 说明**样本顺序 / 排列本身**就能改变可学性 ⇒ 数据配比实验里「打乱方式、课程顺序」必须作为控制变量写进预注册。<br>**harness（任务形态）**：EDA 的「规格 → RTL / 波形」天然是 seq2seq 任务，但定长编码会先撞墙 —— 支持我们用「长上下文 + agent 迭代」而不是 encoder-decoder 单跳的路线选择。<br>**风险**：① BLEU 不可迁移到现代评测，🚫 不得与新基准分数并列；② LSTM 时代的结论对 Transformer 不必然成立；③ 论文的 34.8 含 OOV 惩罚口径，跨论文比较无意义。 |

首次收录: 2026-11-11（第五轮）｜ 状态: 已核验元数据（标题 / 日期取自 `arxiv.org/abs` 实测 `200`；会议经 NIPS 官方论文集索引命中，页码留空）

---

## 18. Dyna, an integrated architecture for learning, planning, and reacting（Dyna）

| 字段 | 内容 |
|:--|:--|
| 标题 | Dyna, an integrated architecture for learning, planning, and reacting（前身：Integrated Architectures for Learning, Planning, and Reacting Based on Approximating Dynamic Programming，1990） |
| 作者（前 3） | Richard S. Sutton（两版均为**单作者**） |
| 年份 | 1991（ACM SIGART Bulletin **2(4): 160–163**，1991-07，Crossref 实测）／ 前身 **1990**（Machine Learning Proceedings 1990，pp. 216–224，Crossref 实测） |
| 会议 / 期刊 | **ACM SIGART Bulletin**（期刊短文，1991）／ **Machine Learning Proceedings 1990**（会议论文集章节，1990） |
| 被引数 | **871**（1991 SIGART 版，DOI `10.1145/122344.122377`）／ **1,383**（1990 前身版，DOI `10.1016/b978-1-55860-141-3.50030-4`）—— **两条记录分别计，不相加**；均 OpenAlex，查询日 2026-11-11 |
| arXiv / DOI | 无 arXiv（1990/1991 年代）｜ DOI `10.1145/122344.122377`（1991）· `10.1016/b978-1-55860-141-3.50030-4`（1990） |
| 一句话贡献 | 把「**从真实经验学价值 + 从真实经验学环境模型 + 用模型生成的模拟经验做规划**」统一进一个架构（Dyna-Q）：每步真实交互既更新价值也更新模型，随后做 k 次「想象」更新 —— model-based RL 的范式起点，也是「学世界模型再规划」的最早清晰表述。 |
| 与我们工作的关系 | **harness（plan/act 预算，直接）**：Dyna 给出的最朴素判据是「规划只值有限的 k 步模拟，多了是浪费」—— 我们评测 agent 的 plan-then-act 时，k 应作为扫描维度而不是默认越大越好；预注册里要写「每多 1 步规划带来的成功率增量」这个成本口径。<br>**zhulong（thinking 轴的历史参照）**：把「思考步数」当预算（而不是当免费能力）这一记账方式，源头可追到 Dyna 的 k。<br>**pretrain（世界模型路线）**：模型与策略共享表示的思想，是后来 model-based 大规模工作的祖先；若我们做 EDA 环境的 world model，这是最早的可引用范式。<br>**designflow（造题）**：可照 Dyna 的「真实 vs 模拟经验」区分，把题分成「必须真跑仿真」和「可离线推演」两档，降低判分成本。<br>**风险**：① 表格型 / 小状态空间的结论，深网络与高维观测下 k 的最优值完全不同，🚫 不得直接套用；② 1990 年代文风，无现代实验口径可用。 |

首次收录: 2026-11-11（第五轮）｜ 状态: 已核验元数据（两版会议 / 卷期 / 页码均经 Crossref 实测；无 arXiv）

---

## 19. Visual Instruction Tuning（LLaVA）

| 字段 | 内容 |
|:--|:--|
| 标题 | Visual Instruction Tuning |
| 作者（前 3） | Haotian Liu · Chunyuan Li · Qingyang Wu（et al.，共 4 位；发表时 UC San Diego + Microsoft Research） |
| 年份 | 2023（arXiv 首次提交 **2023-04-17** v1；v2 = 2023-12-11，`arxiv.org/abs/2304.08485` 实测） |
| 会议 / 期刊 | **NeurIPS 2023（Oral）**（arXiv `comments` 字段实测原文 `NeurIPS 2023 Oral`）；Crossref：**Advances in NeurIPS 36**，pp. **34892–34916**（DOI `10.52202/075280-1516`） |
| 被引数 | **3,189**（OpenAlex，**NeurIPS 版** DOI `10.52202/075280-1516`）／ arXiv 记录 **2,820**（`10.48550/arxiv.2304.08485`）—— **两条记录分列，不相加**；查询日 2026-11-11 |
| arXiv / DOI | <https://arxiv.org/abs/2304.08485> ｜ DOI `10.52202/075280-1516`（NeurIPS 版）/ `10.48550/arxiv.2304.08485`（arXiv 版） |
| 一句话贡献 | 首个用**纯文本 GPT-4** 把图文对「翻译」成多模态指令数据（**158K** 语言-图像指令样本 + **595K** 过滤后的 CC3M 图文对做对齐），接一个投影层把视觉特征映射进 LLM，两阶段训练（先只训投影层、再解冻 LLM）；ScienceQA 上 LLaVA+GPT-4 集成达 **92.53%**，相对 GPT-4 的合成多模态指令评测得 **85.1%** 相对分。 |
| 与我们工作的关系 | **vision（最小可行配方，直接）**：只训 projection 就能把视觉接入 LLM 的性价比基线 ⇒ 我们的视觉塔接 2B 主干时，第一阶段应先复现这条最省的路，再谈端到端解冻。<br>**data（造数据模板）**：用强模型把「已有图文对」改写成指令/问答，是我们在 EDA 领域（版图截图、波形图、时序图）造多模态指令数据的可复用方法；**标注成本必须进账**。<br>**harness（评测口径）**：「相对 GPT-4 的 85.1%」是相对分，🚫 不能当绝对能力；多模态题必须自带可验证真值，否则会重复「用模型判模型」的闭环。<br>**designflow（造题）**：可把「看图回答设计意图」类题按 L1–L5 保真度分层，LLaVA 式数据只覆盖描述层。<br>**风险**：① 85.1% / 92.53% 均为作者自报、本线未复现；② GPT-4 生成数据的许可与污染风险未在文中量化；③ 幻觉在细节计数 / 文字识别上仍明显（原文自述能力边界模糊）。 |

首次收录: 2026-11-11（第五轮）｜ 状态: 已核验元数据（会议 `Oral` 取自 arXiv comments 原文；页码经 Crossref 实测）

---

## 候选池（下轮起逐轮补，**被引数本轮未查**，勿引用）

> 只登记「已实测 arXiv 元数据」的条目；被引数待下轮 OpenAlex 批量核过再写，**本表数字一律留空 = 未查**。
> ⚠️ 第五轮**未新增候选**（4 条直接转正为 #16–#19，元数据均当场实测）；下轮优先补必读清单仍缺的组：**AlphaGo / AlphaGo Zero / DQN / AlphaFold / AlphaStar / Gemini**（DeepMind 家族）、**GPT-1 / GPT-2 + Kaplan scaling laws**、**Kimi / GLM / MiniMax**、**VLA（RT-2 / OpenVLA / π0）· SORA**。**元数据未实测前不进本表**。


| arXiv ID | 标题（arXiv 实测） | 首次提交 | 拟服务线 | 为什么算经典（待核被引） |
|:--|:--|:--|:--|:--|
| — | （本轮无新增候选，待下轮实测后填） | — | — | — |

> ✅ 已晋级（第三轮转正，勿再留在候选池）：`2104.09864` RoFormer（#9）· `2310.06770` SWE-bench（#10）· `2303.11366` Reflexion（#11）· `2201.11903` CoT（#12）。

<!-- 维护纪律：新条目按「首次收录日」追加到末尾（不插入到旧条目之间、不改历史数字）；被引数变动只在新条目里写，旧条目保留原查询日。 -->
