# 经典论文清单（B 轨 · 滚动维护）

> 依据：`WATCH_RESEARCH_TASK.md` 用户令 2026-11-11（research 50% 时间看经典论文 + 建作者关系网 + 跟踪顶级研究者言论）。
> 本清单**不占**每日 5 篇新论文额度（那是 A 轨）；**不删旧条目**，新增条目标 `首次收录: YYYY-MM-DD`；累计 50+ 后转「补充 / 更正」为主。
>
> **「经典」判据（满足任一 + 与本线在研方向相关）**：① 被引 ≥500；② 开创某一范式；③ 方法论常青（至今被新论文反复对比）；④ 本领域（EDA / LLM-for-EDA / 存储）标志性工作。
>
> **被引数来源（硬口径）**：`OpenAlex API`（`api.openalex.org/works/https://doi.org/10.48550/arxiv.<ID>`），**逐条注明查询日期**。
> ⚠️ 本轮 `api.semanticscholar.org` 连续返回 `HTTP 429 Too Many Requests`（两次实测）⇒ **S2 未查**，不写估算值；Google Scholar 本机不可达。**不同来源被引数口径不同，禁止跨源比较**。
>
> **元数据核验**：标题 / 首次提交日 均取自 arXiv 官方 API（`export.arxiv.org/api/query?id_list=...`，2026-11-11 实测 `HTTP 200` + `application/atom+xml; charset=utf-8`，4/4）。

**本轮快照**：累计 **4** 条（首轮 2026-11-11 11:5x CST）｜ 覆盖：pretrain 2 · zhulong 3 · data 1 · harness 1 · designflow 0（下轮补 EDA 经典）

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

## 候选池（下轮起逐轮补，**被引数本轮未查**，勿引用）

> 只登记「已实测 arXiv 元数据」的条目；被引数待下轮 OpenAlex 批量核过再写，**本表数字一律留空 = 未查**。

| arXiv ID | 标题（arXiv 实测） | 首次提交 | 拟服务线 | 为什么算经典（待核被引） |
|:--|:--|:--|:--|:--|
| `2311.00176` | ChipNeMo: Domain-Adapted LLMs for Chip Design | 2023-10-31 | designflow · zhulong | LLM-for-EDA 的标志性工业工作（**被引 357**，OpenAlex 2026-11-11 已查） |
| `2210.03629` | ReAct: Synergizing Reasoning and Acting in Language Models | 2022-10-06 | harness | agent「思考-行动」循环的范式来源（**被引 5,814**，OpenAlex 2026-11-11 已查） |
| `2309.07544` | VerilogEval: Evaluating Large Language Models for Verilog Code Generation | 2023-09-14 | designflow | RTL 代码生成评测的基准起点（被引未查） |
| `2106.09685` | LoRA: Low-Rank Adaptation of Large Language Models | 2021-06-17 | vision · pretrain | 参数高效微调常青方法（被引未查） |
| `2104.09864` | RoFormer: Enhanced Transformer with Rotary Position Embedding | 2021-04-20 | pretrain | RoPE 原始论文，BaiZe 位置编码的直接来源（被引未查） |
| `2310.06770` | SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | 2023-10-10 | harness | 代码 agent 评测的事实标准（被引未查） |

<!-- 维护纪律：新条目按「首次收录日」追加到末尾（不插入到旧条目之间、不改历史数字）；被引数变动只在新条目里写，旧条目保留原查询日。 -->
