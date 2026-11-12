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

**本轮快照**：累计 **51** 条（首轮 11:5x 收 4 条；第二轮 11:4x 补 4 条 EDA / agent / PEFT；第三轮 12:1x 补 4 条 RoPE / SWE-bench / Reflexion / CoT；第四轮 12:4x 补 3 条 GPT-3 / InstructGPT / LLaMA；第五轮 15:0x 补 4 条 ResNet / seq2seq / Dyna / LLaVA；第六轮 18:0x 补 4 条 GPT-1 / GPT-2 / Kaplan scaling laws / DQN；第七轮 21:0x 补 4 条 AlphaGo / AlphaGo Zero / Gemini / OpenVLA；第八轮 2026-11-12 00:0x 补 4 条 AlphaFold / AlphaStar / Kimi k1.5 / π0；第九轮 2026-11-12 03:0x 补 4 条 GLM-4 / MiniMax-01 / RT-2 / Octo；**第十轮 2026-11-12 06:0x 补 4 条** SWE-agent / Tree of Thoughts / Llama 2 / LLaVA-1.5；**第十一轮 2026-11-12 09:0x 补 4 条** Llama 3 / RT-1 / Christiano 2017 / Stiennon 2020；**第十二轮 2026-11-12 12:0x 补 4 条** τ-bench / TD-Gammon / Sora 技术报告 / Kimi K2；**第十三轮 2026-11-12 15:0x 补 4 条** DPO / Mamba-2(SSD) / FlashAttention-2 / Ramulator 2.0）｜ 覆盖（一篇可服务多线，按文内「与我们工作的关系」逐条计数）：pretrain **28** · vision **17** · harness **32** · data **29** · zhulong **36** · designflow **16**

> 🆕 **第四轮（2026-11-11 12:4x）新增 3 条 = 「规模 → 指令 → 开放权重」三段主线**：GPT-3（few-shot 能力从哪来）→ InstructGPT（对齐/指令跟随的范式起点）→ LLaMA（用「多 token」把开放权重做到可用）。三篇合起来回答 data 线当前最实际的问题：**token 预算、指令数据、公开配比**。
>
> 🆕 **第五轮（2026-11-11 15:0x）新增 4 条 = 「视觉塔 + 序列到序列 + 模型式规划」**：ResNet（视觉塔的对照基线）→ LLaVA（图文对齐的最小可行配方）补上第四轮显式留空的 **vision 空档**；seq2seq（定长瓶颈的历史证据）与 Dyna（model-based 规划的范式起点）分别给 pretrain 的长上下文 ROI 与 harness 的 plan/act 预算提供参照。**必读清单覆盖度：本轮后 7/10 组已有一条以上落点**（缺：AlphaGo 系 / DeepMind 家族其余 / Kimi·GLM·MiniMax / VLA·SORA / GPT-1·GPT-2）。

> 🆕 **第六轮（2026-11-11 18:0x）新增 4 条 = 「预训练配方的起点 + 规模律 + 深度 RL 地基」**：GPT-1（两阶段配方 117M）→ GPT-2（1.5B 零样本 + WebText）→ Kaplan scaling laws（N/D/C 幂律，与 Chinchilla 对照）→ DQN（经验回放 + 目标网络）。**必读清单覆盖度：本轮后 8/10 组已有一条以上落点**（缺：AlphaGo 系 / AlphaGo Zero / AlphaFold / AlphaStar / Gemini / Kimi·GLM·MiniMax / VLA·SORA；其中 **DQN 已补上「DeepMind 家族」的入口**）。
> ⚠️ 第六轮如实记：**GPT-1 / GPT-2 无 arXiv、无 DOI**，OpenAlex 精确标题检索 `count=0`、Crossref 无对应条目 ⇒ **被引数「未查」**，本表不写估算值（Google Scholar 本机不可达）。这两条的「经典」依据是**奠基性**，不是被引数。

> 🆕 **第七轮（2026-11-11 21:0x）新增 4 条 = 「搜索 / 自我对弈 / 多模态家族 / 视觉-语言-动作」**：AlphaGo（策略/价值网络 + MCTS，首次击败人类职业棋手）→ AlphaGo Zero（去掉人类数据，纯自我对弈）→ Gemini（Ultra/Pro/Nano 多模态家族，报告口径）→ OpenVLA（7B 开源 VLA，DINOv2+SigLIP 融合 + 离散动作）。**必读清单覆盖：本轮后 10/10 组均至少一条落点**（第 3 组 AlphaGo、第 8 组 DeepMind 家族、第 10 组 VLA 均补齐）。⚠️ 组内仍有未收子项，见文末候选池（AlphaFold / AlphaStar / Kimi / GLM-4 / MiniMax-01 / RT-1·RT-2·π0·Octo / SORA）。

> **第七轮核验证据（可复核）**：arXiv API `id_list=2312.11805` 与 `2406.09246` **2/2** `HTTP 200` + `application/atom+xml`（83,259 B / 4,376 B；首条 2023-12-19、第二条 2024-06-13，均取 **v5 / v3** 最新版本标题）；Nature 两条经 **Crossref 2/2 `200`**（`nature16961` → 529(7587):484–489, 2016-01-27；`nature24270` → 550(7676):354–359, 2017-10）；被引数为 **OpenAlex 4/4 `200`**、查询日 **2026-11-11**。Nature 摘要文本取自 `nature.com/articles/<id>` 页面 `dc.description`（2/2 `200`），**只引摘要内出现的数字**。

> 🆕 **第八轮（2026-11-12 00:0x）新增 4 条 = 「领域先验 / 自我对弈 / RL scaling / VLA 主干复用」**：AlphaFold（把领域约束编码进网络 + CASP 盲测）→ AlphaStar（联盟式多智能体 RL）→ Kimi k1.5（RL 作为新 scaling 轴 + long2short）→ π0（VLM 主干 + flow matching 动作专家）。**必读清单组内剩余**：GLM-4 / MiniMax-01、VLA 其余（RT-1 / RT-2 / Octo）、SORA、Llama 2/3、LLaVA-1.5、Tree of Thoughts / SWE-agent、TD-Gammon、Christiano 2017 / Stiennon 2020。

> **第八轮核验证据（可复核）**：`nature.com/articles/s41586-021-03819-2` 与 `s41586-019-1724-z` 均 `HTTP 200`，摘要取自 `dc.description`（只引摘要内数字）；arXiv API `id_list=2501.12599,2410.24164` `HTTP 200` + `application/atom+xml`（11,826 B，首次提交 2025-01-22 / 2024-10-31）；OpenAlex `4/4 200`（45,663 / 3,799 / 1,436 / 3,214，查询日 2026-11-12）。

> 🆕 **第九轮（2026-11-12 03:0x）新增 4 条 = 「中文系开源 + VLA 两条地基」**：GLM-4（中文为主 10T token + All Tools 工具选择）→ MiniMax-01（线性注意力 + MoE，百万级上下文）→ RT-2（动作＝文本 token、6k 次真机评测）→ Octo（80 万轨迹、9 平台、数小时适配新动作空间）。**必读清单：10/10 组均有落点，具体条目 26/37**；组内剩余：TD-Gammon、Christiano 2017 / Stiennon 2020、Llama 2 / 3、LLaVA-1.5、Tree of Thoughts / SWE-agent、RT-1、SORA。
>
> **第九轮核验证据（可复核）**：arXiv API `id_list=2611.14459,2611.14493,2611.13560,2406.12793,2501.08313,2307.15818,2405.12213,2307.09288,2310.03744` **`200` + `application/atom+xml; charset=utf-8`**（38,801 B，9 条 entry；首次提交 2026-11-10 ×3 / 2024-06-18 / 2025-01-14 / 2023-07-28 / 2024-05-20 / 2023-07-18 / 2023-10-05）；OpenAlex `6/6 200`（1,879 / 213 / 2,322 / 1,192 / 19,635 / 3,281，查询日 2026-11-12）；Crossref 精确标题 **Octo 命中**（`10.15607/rss.2024.xx.090`，2024-07-15），**RT-2 未命中 ⇒ 会议记「未核验」**。

> 🆕 **第十轮（2026-11-12 06:0x）新增 4 条 = 「接口即方法 + 推理期算力 + 开源三档配方 + 视觉最小基线」**：SWE-agent（ACI 设计本身决定分数）→ Tree of Thoughts（搜索换成功率）→ Llama 2（SFT→拒绝采样→PPO 三段式，68 人报告）→ LLaVA-1.5（三处小改动 + 120 万公开数据 + 8×A100 一天）。**必读清单：10/10 组均有落点，具体条目 30/37**；组内剩余：TD-Gammon、Christiano 2017 / Stiennon 2020、Llama 3、RT-1、SORA。
>
> **第十轮核验证据（可复核）**：arXiv API `id_list=2307.09288,2310.03744,2405.15793,2305.10601` **`200` + `application/atom+xml; charset=utf-8`**（13,172 B，4 条 entry；首次提交 2023-07-18 / 2023-10-05 / 2024-05-06 / 2023-05-17，最新版本 v2 / v2 / v3 / v2）；会议取自 **arXiv `arxiv:comment` 原文**（ToT 明写 `NeurIPS 2023 camera ready`、LLaVA-1.5 明写 `Camera ready, CVPR 2024 (highlight)`；Llama 2 / SWE-agent 的 comment 未提会议 ⇒ 由 OpenAlex 定）；被引数 **OpenAlex 4/4 `200`**（19,635 / 3,281 / 1,502 / 3,112，查询日 2026-11-12）；会场 DOI 与页码来自 OpenAlex `primary_location`（LLaVA-1.5 `10.1109/cvpr52733.2024.02484` pp.26286–26296；SWE-agent `10.52202/079017-1601` pp.50528–50652；ToT `10.52202/075280-0517` pp.11809–11822；Llama 2 无会场记录）。

> 🆕 **第十一轮（2026-11-12 09:0x）新增 4 条 = 「偏好即奖励的三段前史 + 机器人策略的规模律 + 405B 的配方公开度」**：Christiano 2017（用成对偏好定义目标，反馈量 <1%）→ Stiennon 2020（reward model 能泛化到新数据集，评测从 ROUGE 转向人类偏好）→ RT-1（任务无关数据 + 高容量 → 真机泛化随数据/模型/多样性变化）→ Llama 3（405B dense、128K 上下文、组合式接入图像/视频/语音）。**必读清单：10/10 组均有落点，具体条目 34/37**；组内剩余：**TD-Gammon**、**τ-bench `2406.12045`**、**SORA 技术报告（无 arXiv，只能引官方报告）**。
>
> **第十一轮核验证据（可复核）**：arXiv API `id_list=2407.21783,2212.06817,1706.03741,2009.01325` **`200` + `application/atom+xml; charset=utf-8`**（73,338 B，4 条 entry；首次提交 2024-07-31 / 2022-12-13 / 2017-06-12 / 2020-09-02；最新版本 v3 / v2 / v4 / v3）；被引数 **OpenAlex 4/4 `200`**（23,796 / 2,747 / 1,643 / 945，查询日 2026-11-12）；会议证据：RT-1 = **RSS 2023**（OpenAlex 会场 DOI `10.15607/rss.2023.xix.025`）、Christiano = **NeurIPS 2017**（OpenAlex `locations` 含 `neural information processing systems` → `papers.nips.cc/paper/7017`）、Stiennon = **NeurIPS 2020**（arXiv `comments` 原文 `NeurIPS 2020`）、Llama 3 = **预印本技术报告**（OpenAlex `primary_location.source` = arXiv，无会场 DOI）。
> ⚠️ 第十一轮如实记：本轮 A 轨扫描第 5 个查询（`cs.SE`）遇 **arXiv `429`**（本线并发请求所致，非「无新增」）⇒ 已在 `ARXIV_API.md §9.155` 记录并改为「4/5 查询成功 + 06:00 的 `cs.SE` 值可参照」；🚫 不把 429 写成「本领域无新增」。

> 🆕 **第十二轮（2026-11-12 12:0x）新增 4 条 = 「补齐必读清单最后 3 项 + 中文系最新 agentic 报告」**：τ-bench（用 LM 模拟用户 + 域内 API + 政策约束，按**终态数据库**判分 + `pass^k` 测一致性）→ **第 7 组（姚顺雨）的最后一项**；TD-Gammon（1994/1995，TD(λ) + 自对弈，只靠胜负信号学到强中级水平）→ **第 1 组（萨顿）的「相关」项**；Sora 官方技术报告（「视频生成模型是世界模拟器」，无 arXiv/DOI）→ **第 10 组（SORA）的最后一项**；Kimi K2（32B 激活 MoE、MuonClip、15.5T token 零 loss spike、agentic 数据合成 + 联合 RL）→ 第 9 组（月之暗面）的**最新一条**。**必读清单：10/10 组、37/37 条目 —— 清单内条目本轮全部覆盖完毕**（此后转「补充 / 更正」为主）。
>
> **第十二轮核验证据（可复核）**：arXiv API `id_list=2406.12045,2401.14185` **`200` + `application/atom+xml; charset=utf-8`**（5,114 B）；`id_list=2507.20534` **`200` + atom**（14,399 B，v2，首发 2025-07-28 / 更新 2026-02-03）；OpenAlex `2406.12045` = **1,198**、`2507.20534` = **1,410**（查询日 2026-11-12）；TD-Gammon：Crossref `10.1145/203330.203343` **`200`**（CACM **38(3):58–68**，1995-03）、OpenAlex 同 DOI **1,680**，1994 姊妹篇 `10.1162/neco.1994.6.2.215` OpenAlex **823** 且取到**完整摘要**（本线只引摘要原文）；Sora：`openai.com/index/...` 与 `openai.com/research/...` 经代理与直连**均为 `403`**、Wayback `403`、`r.jina.ai` `401` ⇒ **正文未取到**，本条**不引任何数字**。
> ⚠️ **第十二轮如实记（更正）**：任务书 §6.5 表格把「Kimi（月之暗面报告，如 … 2401.14185 Moonshot）」作为示例 —— 本线实测 **`2401.14185` = `TDFNet: An Efficient Audio-Visual Speech Separation Model with Top-down Fusion`（cs.SD，Samuel Pegg / Kai Li / Xiaolin Hu，2024-01-25，OpenAlex 被引 3）**，**与 Kimi / Moonshot 无关** ⇒ 🚫 不据此伪造条目，改用实测存在的 **Kimi K2 `2507.20534`**；建议 supervisor 更正任务书示例。
>
> 🆕 **第十三轮（2026-11-12 15:0x）新增 4 条 = 「偏好优化 / SSM 统一 / 注意力实现 / 存储模拟基座」**：DPO（把 KL 约束 RLHF 化成分类损失，RM-free 路线对照）→ **zhulong 奖励设计的第三条路**；Mamba-2 / SSD（注意力与 SSM 通过半可分矩阵统一，核心层快 2–8×）→ **pretrain 架构对照 + 吞吐口径**；FlashAttention-2（25–40% → 50–73% 理论峰值，225 TFLOPs/s / 72% MFU）→ **pretrain 的 MFU 标尺**；Ramulator 2.0（模块化 DRAM 模拟器，MIT 许可）→ **zhulong 批量评测基座 + designflow 保真度三分**。**必读清单：10/10 组、37/37 条目仍全覆盖**（本轮属「补充」，故为 B 轨第十三轮）。
>
> **第十三轮核验证据（可复核）**：arXiv API `id_list=2310.16944,2405.21060,2307.08691,2308.11030` 与 `id_list=2305.18290,2310.16944` 均 **`200` + `application/atom+xml; charset=utf-8`**（9,704 B / 5,938 B / 9,862 B 三次调用）；被引数 **OpenAlex 4/4 `200`**（DPO **3,123** · Mamba-2 **1,003** · FlashAttention-2 **1,844** · Ramulator 2.0 **185**，查询日 2026-11-12）；会议证据：DPO = OpenAlex `conference-paper` + NeurIPS 会场 DOI `10.52202/075280-2338`（pp. 53728–53741）、Mamba-2 = arXiv `comment` 原文 `ICML 2024`、FlashAttention-2 = **未核到会场**（如实记预印本）、Ramulator 2.0 = IEEE CAL DOI `10.1109/LCA.2023.3333759`（23(1):112–116）。
> ⚠️ **第十三轮如实记（更正）**：候选池此前把 **DPO 记为 `2310.16944`** —— 本线实测该 ID = **`Zephyr: Direct Distillation of LM Alignment`（Tunstall et al., 2023-10-25, cs.LG）**，**不是 DPO**；DPO 的真实 ID 为 **`2305.18290`**（`v3`，2024-07-29）。⇒ 已按实测 ID 收录 #48，并**在此显式更正**，🚫 不沿用错误 ID。Zephyr 本身可作「dDPO 蒸馏」候选，但本轮**不凑数**、不收录。


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

## 20. Improving Language Understanding by Generative Pre-Training（GPT-1）

| 字段 | 内容 |
|:--|:--|
| 标题 | Improving Language Understanding by Generative Pre-Training |
| 作者（前 3） | Alec Radford · Karthik Narasimhan · Tim Salimans（et al.，共 4 位；Ilya Sutskever 末位；OpenAI） |
| 年份 | 2018（OpenAI 技术报告，**无 arXiv / 无 DOI**） |
| 会议 / 期刊 | 未发表（技术报告）；官方 PDF 实测 `HTTP 200` / `application/pdf` / 541,036 B（2026-11-11） |
| 被引数 | **未查**（OpenAlex 精确标题检索 `count=0`、Crossref `total-results` 无对应条目 ⇒ **无 DOI 可核**，按纪律不写估算值；Google Scholar 本机不可达） |
| arXiv / DOI | 无 ｜ 官方 PDF <https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf> |
| 一句话贡献 | 把「**生成式预训练 + 判别式微调**」写成两阶段配方：先在 BooksCorpus（7,000 本书）上用 12 层 decoder-only Transformer（768 hidden / 12 heads / **117M** 参数）做语言模型预训练，再把下游任务改写成「带任务前缀的连续文本」微调 ⇒ 12 个任务里 **9 个**刷新当时的 SOTA（含常识推理、蕴含、分类、指代）。 |
| 与我们工作的关系 | **pretrain（配方的历史起点）**：BaiZe 的「预训练 → SFT」两段式，方法学祖先就是这篇；它给出的关键判断「**无标注语料 >> 有标注任务量** 时预训练才划算」，正是我们 2B 规模要自己复核的前提。<br>**data（任务格式化）**：把分类 / 蕴含 / 相似度任务统一改写成文本序列的「task-aware input transformation」，可直接借到 EDA 任务（如「这段 RTL 是否有竞态？」）的 SFT 数据构造。<br>**harness（口径）**：9/12 任务 SOTA 是 **2018 年**的对照面，🚫 不可当今日基线。<br>**风险**：BooksCorpus 已不再公开分发，复现数据不可得；被引数未查 ⇒ 本表**不能**用它做「高引」论证。 |

首次收录: 2026-11-11（第六轮）｜ 状态: 元数据已核验（PDF 200 实测；被引数**未查**，已如实标注）

---

## 21. Language Models are Unsupervised Multitask Learners（GPT-2）

| 字段 | 内容 |
|:--|:--|
| 标题 | Language Models are Unsupervised Multitask Learners |
| 作者（前 3） | Alec Radford · Jeffrey Wu · Rewon Child（et al.，共 6 位；Dario Amodei、Ilya Sutskever 在列；OpenAI） |
| 年份 | 2019（OpenAI 技术报告，**无 arXiv / 无 DOI**） |
| 会议 / 期刊 | 未发表（技术报告）；官方 PDF 实测 `HTTP 200` / `application/pdf` / 582,775 B（2026-11-11）；`openai.com/index/better-language-models/` 对本机返回 **403**（页面不可判定，故只挂 CDN PDF） |
| 被引数 | **未查**（同 GPT-1：OpenAlex 精确标题 `count=0`、Crossref 无对应条目 ⇒ 无 DOI 可核） |
| arXiv / DOI | 无 ｜ 官方 PDF <https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf> |
| 一句话贡献 | 提出「**语言模型即无监督多任务学习器**」：在 WebText（**40GB / 800 万文档**，从 Reddit 外链抓取）上训练 **1.5B** 参数的 LM，**零样本**（zero-shot）即在 CoQA、LAMBADA、翻译、摘要等任务上达到「不需任务特定训练」的可用水平，并明确记录 `PPL` 与下游准确率的**对数线性**关系。 |
| 与我们工作的关系 | **pretrain（数据来源假设）**：WebText 的「**由人筛过的外链**」= 质量过滤的原始形态，对应 data 线现在的去污染 / 质量筛流程；它的教训是「数据来源的**筛选规则**本身就是方法」，而不是附带步骤。<br>**pretrain（评测）**：zero-shot PPL → 下游任务的对数线性关系，是「小模型能不能靠 PPL 预测下游」这一假设的最早系统性陈述 ⇒ **2B 上必须重测**，不可外推。<br>**zhulong（消融口径）**：1.5B 与 117M（GPT-1）的对比是「纯规模放大 + 数据放大」的最小对照实验，可作为我们等 token / 等算力对照的历史模板。<br>**风险**：WebText 未公开，复现只能近似；报告里「零样本」与「少样本」口径常被二手解读混用，引用时须点明。 |

首次收录: 2026-11-11（第六轮）｜ 状态: 元数据已核验（PDF 200 实测；被引数**未查**，已如实标注）

---

## 22. Scaling Laws for Neural Language Models（Kaplan et al.）

| 字段 | 内容 |
|:--|:--|
| 标题 | Scaling Laws for Neural Language Models |
| 作者（前 3） | Jared Kaplan · Sam McCandlish · Tom Henighan（et al.，共 7 位；Johns Hopkins + OpenAI） |
| 年份 | 2020（arXiv 首次提交 **2020-01-23**，本线实测） |
| 会议 / 期刊 | 预印本（**未被会议正式收录**；OpenAlex `type=preprint`） |
| 被引数 | **9,945**（OpenAlex，DOI `10.48550/arxiv.2001.08361`，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2001.08361> ｜ DOI `10.48550/arxiv.2001.08361` |
| 一句话贡献 | 用幂律同时拟合**参数量 N / 数据量 D / 训练算力 C**：`L(N,D)`、`L(C)` 在跨 7 个数量级内近似为直线（对数坐标），且**性能强烈依赖规模、极弱依赖网络形状（深宽比 / 头数）**；大模型样本效率更高 ⇒ 在固定算力下应「**大模型 + 适量数据**」（与后来 Chinchilla 的结论相反，两者口径不同，须分别引用）。 |
| 与我们工作的关系 | **pretrain（选点方法论，直接）**：2B 的训练 token 预算要用**自己的**拟合曲线定，而不是引 Chinchilla 的 20 token/参数 —— 这两条经验线在尺度外推上会打架，本文的「形状不敏感」也提示我们**别把调深宽比当主攻方向**。<br>**zhulong（成本口径）**：`L(C)` 曲线给出「多花 10× 算力换多少 loss」的一阶估计 ⇒ 消融表里报收益时应换算成算力倍数，而不是只报绝对值。<br>**data（配比）**：文中「大模型样本效率更高」意味着**数据配比实验必须在小与中等尺度各做一遍**，否则外推会错。<br>**风险**：① 结论建立在 2019 年的 Transformer + WebText 口径上；② 与 Chinchilla 的差异源于**固定算力下怎么分配 N 与 D**，🚫 不得把两者当成互相否证；③ 被引数口径 = OpenAlex。 |

首次收录: 2026-11-11（第六轮）｜ 状态: 已核验元数据（arXiv + OpenAlex + PDF 均实测）

---

## 23. Human-level control through deep reinforcement learning（DQN）

| 字段 | 内容 |
|:--|:--|
| 标题 | Human-level control through deep reinforcement learning |
| 作者（前 3） | Volodymyr Mnih · Koray Kavukcuoglu · David Silver（et al.，共 9 位；Demis Hassabis 末位；DeepMind） |
| 年份 | 2015（Nature 2015-02-25，Crossref 实测） |
| 会议 / 期刊 | **Nature** 518(7540): **529–533**（Crossref `page=529-533`，实测） |
| 被引数 | **32,259**（OpenAlex，DOI `10.1038/nature14236`，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | 无 arXiv 正刊版（**前置**：Playing Atari with Deep RL，arXiv `1312.5602`，NIPS 2013 DRL Workshop）｜ DOI `10.1038/nature14236` |
| 一句话贡献 | 用**同一个**卷积网络 + Q-learning，直接从 **210×160 像素 + 得分**学 49 个 Atari 游戏，靠两个工程手段稳住「深度网络 + RL」：**经验回放**（打散样本相关性）与**目标网络**（固定 bootstrap 目标）；29 个游戏达到人类水平以上。 |
| 与我们工作的关系 | **harness（agent 训练/评测的地基）**：我们的 code agent 若做 RL 或 on-policy 蒸馏，**经验回放 + 目标网络**仍是「样本贵、奖励稀疏」场景下最省的第一选择；报告里必须写清 replay 容量与目标网络同步频率，否则不可比。<br>**vision（特征学习的早期证据）**：像素 → 卷积特征 → 控制，是「视觉塔端到端可训」的最早大规模证据；对应我们「冻结视觉塔 vs 端到端」的 2×2 预注册。<br>**zhulong（评测口径）**：「人类水平」= **单游戏人类测试员得分**，且用 30 次随机种子的均值 —— 这条「多 seed + 人类参照」的记账方式应直接沿用。<br>**designflow（造题）**：49 个游戏同一接口（同分辨率 / 同动作空间）是「同构题库」的早期范例，可借鉴其**统一输入输出契约**降低判分成本。<br>**风险**：① 32,259 是 OpenAlex 口径；② Atari 的奖励稠密、状态可完全观测，与我们 EDA 任务（奖励稀疏、部分可观测）差异极大，🚫 不可直接套超参。 |

首次收录: 2026-11-11（第六轮）｜ 状态: 已核验元数据（OpenAlex + Crossref 双 200；页码 / 卷期实测）

---

## 24. Mastering the game of Go with deep neural networks and tree search（AlphaGo）

| 字段 | 内容 |
|:--|:--|
| 标题 | Mastering the game of Go with deep neural networks and tree search |
| 作者（前 3） | David Silver · Aja Huang · Chris J. Maddison（et al.，共 **20** 位；含 Ilya Sutskever / Koray Kavukcuoglu / Demis Hassabis；DeepMind） |
| 年份 | 2016（Nature 出版 **2016-01-27**，Crossref 实测） |
| 会议 / 期刊 | **Nature** 529(7587): **484–489**（Crossref `page=484-489`、OpenAlex biblio 一致） |
| 被引数 | **16,697**（OpenAlex，DOI `10.1038/nature16961`，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | 无 arXiv 版 ｜ DOI `10.1038/nature16961` ｜ <https://www.nature.com/articles/nature16961> |
| 一句话贡献 | 用「**策略网络**选点 + **价值网络**评估局面」两个深度网络（人类棋谱监督学习 + 自我对弈强化学习）配合 **MCTS** 搜索；据摘要，**无前瞻搜索**时网络已可达当时最强 MCTS 程序水平，完整系统对其他围棋程序胜率 **99.8%**，并以 **5–0** 击败欧洲围棋冠军 —— 首次在**全尺寸**围棋中战胜人类职业棋手。 |
| 与我们工作的关系 | **zhulong（思考预算轴，直接）**：这篇把「**模型先验**（policy/value）」与「**搜索预算**（MCTS 模拟次数）」拆成两个可独立加大的旋钮。我们的 thinking 轴应照此把「模型能力」与「每问搜索/采样预算」分开记账；<b>动作</b>：B 轴对照表加一列 `search_budget`（同一模型跑 {1×, 4×, 16×} 预算），否则「thinking 更强」无法判断是模型还是预算。<br>**harness（评测协议）**：AlphaGo 的核心证据是**固定对手、固定局数**的胜率（99.8% / 5–0），而不是单局示例；<b>动作</b>：EDA 任务的 A/B 对比也须写清对手版本、局数/题数与胜负判据，单题 showcase 不进结论。<br>**data（监督信号的来源）**：人类棋谱只用于**冷启动**，之后靠自我对弈提升；对应我们 code / EDA 语料的「人类数据冷启动 + 自生成数据」两段式，<b>判据</b>：自生成数据占比提高后，若 held-out 真实任务不升，则只保留冷启动数据。<br>**风险**：① 围棋是**完全观测、规则固定、可无限自我对弈**的封闭域，EDA 任务部分可观测且验证代价高，🚫 不可把「自我对弈能超越人类」直接外推到 EDA；② 99.8% / 5–0 均为**作者自报**，本线未复现；③ 论文的工程细节（分布式、特征平面）在 Methods，引用数字前须回原文对应段落。 |

首次收录: 2026-11-11（第七轮）｜ 状态: 元数据已核验（Crossref + OpenAlex 双 200；摘要文本取自 nature.com `dc.description`）

---

## 25. Mastering the game of Go without human knowledge（AlphaGo Zero）

| 字段 | 内容 |
|:--|:--|
| 标题 | Mastering the game of Go without human knowledge |
| 作者（前 3） | David Silver · Julian Schrittwieser · Karen Simonyan（et al.，共 **17** 位；含 Demis Hassabis；DeepMind） |
| 年份 | 2017（Nature 出版 **2017-10**，Crossref 实测） |
| 会议 / 期刊 | **Nature** 550(7676): **354–359**（Crossref `page=354-359`、OpenAlex biblio 一致） |
| 被引数 | **9,661**（OpenAlex，DOI `10.1038/nature24270`，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | 无 arXiv 版 ｜ DOI `10.1038/nature24270` ｜ <https://www.nature.com/articles/nature24270> |
| 一句话贡献 | **去掉人类棋谱、手工特征与领域知识**（除规则本身），只靠强化学习 + 自我对弈：网络同时预测自己的落子与胜负，搜索变强 → 自我对弈数据变好 → 网络再变强；据摘要，从 **tabula rasa** 起步最终以 **100–0** 战胜此前击败冠军的 AlphaGo，并自行发现新策略。 |
| 与我们工作的关系 | **zhulong（自我提升闭环）**：这是「**不用人类示范，靠可验证结果自举**」的最清晰范式；对应我们 thinking / RL 轴的核心问题 —— 判分器是否可靠到能当「胜负」。<b>动作</b>：在 zhulong 预注册「自生成数据闭环」小实验（生成 → 用 checker 判 → 只保留可判分样本 → 再训），<b>判据</b>：held-out 真实题提升且 checker 误判率 < 5%，否则停。<br>**data（合成数据）**：自我对弈数据**无人工标注成本**，但依赖环境可无限重置；我们的 EDA 环境重置/验证成本高 ⇒ <b>动作</b>：先统计「一次自生成样本的端到端成本（生成 + 验证）」，成本高于人工样本时不做。<br>**harness（对手/基线选择）**：100–0 是对**上一代自己**的胜负，不是对人类；<b>动作</b>：内部迭代报告须同时给「对上一版」与「对固定外部基线」两组数，避免只报自比自。<br>**designflow（造题）**：自我对弈可视为「题目难度自适应」的极端形式（对手即难度）；<b>动作</b>：可试点「出题 agent vs 解题 agent」双角色，用解题方胜率调难度，先做 30–50 题小样，不直接替换现有题库。<br>**风险**：① 围棋胜负判据**零成本且绝对可靠**，EDA 的 checker 是近似判据 —— 这是两者最大的不可迁移点；② 100–0 为作者自报；③ 「无人类知识」仅指不输入棋谱/特征，规则仍由人给出，引用时 🚫 不可写成「完全无人类参与」。 |

首次收录: 2026-11-11（第七轮）｜ 状态: 元数据已核验（Crossref + OpenAlex 双 200；摘要文本取自 nature.com `dc.description`）

---

## 26. Gemini: A Family of Highly Capable Multimodal Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Gemini: A Family of Highly Capable Multimodal Models |
| 作者（前 3） | Gemini Team（集体署名）· Rohan Anil · Sebastian Borgeaud（et al.；Google / Google DeepMind） |
| 年份 | 2023（arXiv 首次提交 **2023-12-19**，本线实测；所引为 **v5** 最新版本） |
| 会议 / 期刊 | 预印本技术报告（OpenAlex `type=preprint`；**未查**正式会议收录） |
| 被引数 | **10,518**（OpenAlex，DOI `10.48550/arxiv.2312.11805`，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2312.11805> ｜ DOI `10.48550/arxiv.2312.11805` |
| 一句话贡献 | 一个覆盖 **图像 / 音频 / 视频 / 文本**理解的多模态模型家族（**Ultra / Pro / Nano** 三档，从复杂推理到端侧）；据摘要，最强 Ultra 在 **32 个基准中的 30 个**刷新 SOTA、**20 个多模态基准全部提升**，并称是**首个在 MMLU 达到人类专家水平**的模型。 |
| 与我们工作的关系 | **vision（多模态家族形态）**：同一份报告里按「Ultra / Pro / Nano」分档 = 一套代码/数据配方服务多个算力档；对应 BaiZe 视觉塔的「同配方、不同规模」评估方式，<b>动作</b>：视觉线报告固定配方，至少报一个小档 + 一个大档，避免单档结论。<br>**pretrain（只作定位，不作配方依据）**：报告**未公开**数据配比、token 量与训练细节 ⇒ 🚫 不可据本文反推我们的 token 预算或配比；<b>动作</b>：pretrain 线引用时只写「多模态家族的产品化形态」，不引用任何训练配方。<br>**harness（评测口径）**：30/32、20/20 是**厂商自报**且基准集随时间过期（2023-12 口径）；<b>动作</b>：我们的评测表引用此类数字必须标「报告方自报 + 报告日期」，不得写成「当前 SOTA」。<br>**data（多模态混料）**：家族同时覆盖四种模态，说明混料必须覆盖下游要用的每一种模态；<b>动作</b>：data 线在 manifest 里为每个模态记 `share` 与 `eval_coverage`，缺模态覆盖的实验不进入对外结论。<br>**风险**：① 技术报告**信息不对称**（无配方、无数据细节），只能当「能力声明」不能当「方法论文」；② MMLU 人类专家水平的说法是 **2023 年**口径，今天已不构成 SOTA；③ 被引数含大量预印本引用，🚫 不与其他来源跨源比较。 |

首次收录: 2026-11-11（第七轮）｜ 状态: 元数据已核验（arXiv API 200 + atom+xml；OpenAlex 200）

---

## 27. OpenVLA: An Open-Source Vision-Language-Action Model

| 字段 | 内容 |
|:--|:--|
| 标题 | OpenVLA: An Open-Source Vision-Language-Action Model |
| 作者（前 3） | Moo Jin Kim · Karl Pertsch · Siddharth Karamcheti（et al.；Stanford / UC Berkeley / Google DeepMind 等；所引为 **v3**） |
| 年份 | 2024（arXiv 首次提交 **2024-06-13**，本线实测） |
| 会议 / 期刊 | 预印本（OpenAlex `type=preprint`；**未查**正式会议收录） |
| 被引数 | **2,913**（OpenAlex，DOI `10.48550/arxiv.2406.09246`，查询日 2026-11-11；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2406.09246> ｜ DOI `10.48550/arxiv.2406.09246` ｜ 代码 <https://github.com/openvla/openvla> |
| 一句话贡献 | 开源 **7B** VLA：**Llama 2** 语言主干 + 融合 **DINOv2 与 SigLIP** 预训练特征的视觉编码器，在 **970k** 真实机器人示范上训练、动作**离散分桶**；据摘要，在 **29 个任务 / 多机器人本体**上比闭源 **RT-2-X（55B）** 绝对成功率**高 16.5%**，参数少 **7×**，并给出高效微调（LoRA）做法。 |
| 与我们工作的关系 | **vision（双塔融合，直接）**：`DINOv2 + SigLIP` 融合是「语义 + 局部几何」两种预训练特征的组合；对应我们工业图像（版图 / 波形 / SEM）的视觉塔选型。<b>动作</b>：预注册 2×2 消融（单 SigLIP vs 双塔融合 × 冻结 vs 解冻），<b>判据</b>：融合臂在 held-out 域内任务上 > 单塔 +2 个绝对点才保留（否则省一半视觉算力）。<br>**data（多样性优先）**：970k 示范的价值在**任务/本体多样性**而非单任务量；<b>动作</b>：data 线做「固定 token 预算，仓库/文件数 × 每仓库重复次数」三臂实验，检验多样性是否同样压倒重复量（我们的语料侧对应命题）。<br>**harness（评测协议）**：29 任务 + 多本体 + 成功率 = 固定任务集、固定初始条件的对照；<b>动作</b>：EDA agent 评测表补 `fixed_initial_state`、`n_trials`、成功率置信区间三列，禁止用单次运行比较。<br>**zhulong（接口与微调成本）**：动作离散到 256 桶是「接口 token 化」的一种；对应我们 tool-call 动作空间的序列化方式。<b>动作</b>：对比「逐维分桶」与「动作文本序列化」两臂，同时记 LoRA vs 全参的训练成本。<br>**风险**：① 机器人动作空间连续、低维、固定本体，EDA 工具调用是**异构、变长、带类型**的，🚫 不可直接照搬分桶；② 16.5% / 7× 均为**作者自报**、任务集自选；③ 970k 示范不可得，复现只能换数据。 |

首次收录: 2026-11-11（第七轮）｜ 状态: 元数据已核验（arXiv API 200 + atom+xml；OpenAlex 200）

---

## 28. Highly accurate protein structure prediction with AlphaFold

| 字段 | 内容 |
|:--|:--|
| 标题 | Highly accurate protein structure prediction with AlphaFold |
| 作者（前 3） | John Jumper · Richard Evans · Alexander Pritzel（et al.；DeepMind；通讯含 Demis Hassabis / John Jumper） |
| 年份 | 2021 |
| 会议 / 期刊 | **Nature 596(7873): 583–589**（DOI `10.1038/s41586-021-03819-2`，OpenAlex 卷期页码已核） |
| 被引数 | **45,663**（OpenAlex，查询日 2026-11-12；S2 未查，🚫 不跨源比较） |
| arXiv / DOI | **无 arXiv** ｜ DOI <https://doi.org/10.1038/s41586-021-03819-2> ｜ 官方介绍 <https://deepmind.google/technologies/alphafold/> |
| 一句话贡献 | 用「多序列比对（MSA）+ 深度学习」把蛋白质三维结构预测做到**原子级精度**：据摘要，在 **CASP14** 上「多数目标达到与实验结构可竞争」的精度并大幅超过其他方法，且**在没有同源结构时**仍可用。 |
| 与我们工作的关系 | **vision（几何先验，间接）**：AlphaFold 的核心不是「更大的 ViT」，而是**把领域约束（物理/生物先验、MSA 进化信息）编码进网络结构**；对应我们工业图像（版图 / SEM / 波形）里「已知几何/工艺约束该以什么形式进模型」。<b>动作</b>：视觉线在下一版视觉塔预注册里加一组「显式几何通道 vs 纯像素」对照（同数据、同预算），<b>判据</b>：显式几何臂在 held-out 新节点/新图层上 > 纯像素 +2 个绝对点才保留。<br>**data（先验数据 vs 原始数据）**：MSA 相当于「同族历史样本」而非更多标注；对应 data 线「同族仓库/同族版图」的检索增强。<b>动作</b>：data 线为每条样本记 `family_id`，做「是否检索同族上下文」A/B。<br>**harness（盲测协议）**：CASP = 题目冻结 + 统一提交 + 统一判分，是防泄漏典范；<b>动作</b>：harness 设计 EDA 评测时固定「冻结题目 → 提交 → 统一判分」，报告写清冻结日期。<br>**风险**：① 生物「进化同源」在版图/波形无严格对应物，🚫 不可把 MSA 类比当可直接落地的模块；② 45,663 被引主要来自生命科学，不代表与我们的相关度；③ 「原子级」是 CASP14（2020）口径。 |

首次收录: 2026-11-12（第八轮）｜ 状态: 元数据已核验（Nature 页面 `dc.description` `200`；OpenAlex `200`）

---

## 29. Grandmaster level in StarCraft II using multi-agent reinforcement learning

| 字段 | 内容 |
|:--|:--|
| 标题 | Grandmaster level in StarCraft II using multi-agent reinforcement learning |
| 作者（前 3） | Oriol Vinyals · Igor Babuschkin · Wojciech M. Czarnecki（et al.；DeepMind；含 David Silver） |
| 年份 | 2019 |
| 会议 / 期刊 | **Nature 575(7782): 350–354**（DOI `10.1038/s41586-019-1724-z`） |
| 被引数 | **3,799**（OpenAlex，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | **无 arXiv** ｜ DOI <https://doi.org/10.1038/s41586-019-1724-z> |
| 一句话贡献 | 用**多智能体 RL + 持续进化的「联盟（league）」**（人类对局与智能体对局混用、主策略与克制策略共存）在完整《星际争霸 II》达到**宗师**水平：据摘要，三个种族均达宗师、**高于 99.8% 的官方排名玩家**（前 0.2%）。 |
| 与我们工作的关系 | **zhulong（自对弈与陪练课程，直接）**：联盟 = 一组**互相克制、持续更新**的对手，而非单一固定 baseline；对应我们「陪练模型生成难例」的课程设计。<b>动作</b>：zhulong 线把「单基线 RL」改为「3–5 个历史快照 + 1 个主策略」小联盟，主策略只与联盟对打，<b>判据</b>：固定评测集胜率提升且对最强历史快照不退步（防只赢当前陪练）。<br>**harness（防过拟合评测）**：联盟天然构造「训练时未见但同分布」的对手；<b>动作</b>：harness 的 agent 评测引入动态题库/对手池，每轮用不同快照，报告「对池均值 + 最差对手」两列。<br>**designflow（多轮任务）**：SC2 是长时程、部分可观测、动作空间巨大的决策问题，与 EDA 多步工具调用同构；<b>动作</b>：designflow 造题显式标注「部分可观测」与「环境会变化」两类，作为 L4/L5 保真度新维度。<br>**风险**：① SC2 动作空间与奖励由游戏给定，EDA 的「胜负」需自定义且多指标，🚫 不可照搬算法；② 宗师/99.8% 是 2019 天梯口径；③ 联盟训练成本极高，只能借思路不能借规模。 |

首次收录: 2026-11-12（第八轮）｜ 状态: 元数据已核验（Nature 页面 `dc.description` `200`；OpenAlex `200`）

---

## 30. Kimi k1.5: Scaling Reinforcement Learning with LLMs

| 字段 | 内容 |
|:--|:--|
| 标题 | Kimi k1.5: Scaling Reinforcement Learning with LLMs |
| 作者（前 3） | Kimi Team（Moonshot AI；署名列表含 Angang Du · Bofei Gao · Bowei Xing …，作者列表中另见 Jianlin Su） |
| 年份 | 2025（arXiv 首次提交 **2025-01-22**，本线实测；最新 **v4** 2025-06-03） |
| 会议 / 期刊 | 预印本技术报告（OpenAlex `type=preprint`；**未查**正式会议收录） |
| 被引数 | **1,436**（OpenAlex，DOI `10.48550/arxiv.2501.12599`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2501.12599> ｜ DOI `10.48550/arxiv.2501.12599` |
| 一句话贡献 | 用**长上下文 RL 扩展 + 改进的策略优化**训练多模态 LLM，**不依赖 MCTS / 价值函数 / 过程奖励模型**：据摘要，AIME **77.5**、MATH-500 **96.2**、Codeforces **94 百分位**、MathVista **74.9**，与 OpenAI o1 相当；并给出 **long2short**（用长 CoT 提升短 CoT），短 CoT 侧 AIME **60.8**、MATH-500 **94.6**、LiveCodeBench **47.3**。 |
| 与我们工作的关系 | **zhulong（thinking 预算 / long2short，直接）**：长 CoT 训练出的能力可**蒸馏进短 CoT**，对应我们「训练时想得长、部署时想得短」的成本结构。<b>动作</b>：zhulong 线加 `long2short` 消融（同一 base：长 CoT RL → 短 CoT 蒸馏 vs 直接短 CoT RL），<b>判据</b>：固定 token 预算下，蒸馏臂准确率不低于直接臂且平均生成长度 ≤ 其 60%。<br>**posttrain / pretrain（RL 数据墙）**：核心论点是「RL 提供新的 scaling 轴（用奖励换数据）」；<b>动作</b>：pretrain 线在算力分配表里把「RL token 预算」单列，不混算；对外统一用「总生成 token + GPU 小时」双口径。<br>**harness（自报口径）**：77.5 / 96.2 / 94 百分位均为**作者自报**、基准版本敏感；<b>动作</b>：引用时标「Moonshot 自报，2025-01」并同时记录我们自己的复测值，禁止把自报值写进对外结论。<br>**data（多模态 RL 数据）**：报告提到配方但未给完整配比；<b>动作</b>：data 线只当「多模态 RL 数据可 scale」的 existence proof，不据此推我们的配比。<br>**风险**：① 技术报告不公开训练细节（数据量、奖励设计）；② 基准分数随时间过期；③ 「不依赖 MCTS/PRM」是作者口径，复现需自行验证。 |

首次收录: 2026-11-12（第八轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 31. π0: A Vision-Language-Action Flow Model for General Robot Control

| 字段 | 内容 |
|:--|:--|
| 标题 | π₀: A Vision-Language-Action Flow Model for General Robot Control（arXiv 标题写作 `$π_0$`） |
| 作者（前 3） | Kevin Black · Noah Brown · Danny Driess（et al.；Physical Intelligence；含 Chelsea Finn / Sergey Levine / Karl Pertsch） |
| 年份 | 2024（arXiv 首次提交 **2024-10-31**，本线实测；最新 **v4** 2026-01-08） |
| 会议 / 期刊 | **Robotics: Science and Systems (RSS) 2025**（OpenAlex `type=conference-paper`，DOI `10.15607/rss.2025.xxi.010`） |
| 被引数 | **3,214**（OpenAlex，RSS DOI，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2410.24164> ｜ DOI `10.15607/rss.2025.xxi.010` ｜ 项目页 <https://physicalintelligence.company/blog/pi0> |
| 一句话贡献 | 在**预训练 VLM** 之上加一个 **flow matching** 动作专家，用**多机器人平台的大规模多样数据**训练通用策略：据摘要，支持**零样本**执行、跟随人类语言指令与高层 VLM 策略、并可通过微调获得新技能（叠衣、清桌、装箱等）。 |
| 与我们工作的关系 | **vision（VLM 主干复用，直接）**：π0 不重训视觉塔，而**继承 Internet 规模语义知识**再加动作头；对应 BaiZe 视觉塔「先接通用 VLM，再小成本适配域内」。<b>动作</b>：vision 线预注册「冻结 VLM 主干 + 只训适配层」与「全参微调」两臂，<b>判据</b>：冻结臂在域内任务上达到全参臂 −3 个绝对点以内即采用（省下的算力转投数据）。<br>**zhulong（动作生成方式）**：flow matching 生成连续动作块（action chunk），与「逐 token 自回归出 tool call」是两种接口；<b>动作</b>：zhulong 线对比「动作块（一次出多步）」与「逐步出」在长流程 EDA 任务上的成功率与调用成本，<b>判据</b>：动作块臂成功率不降且工具调用轮数下降 ≥20% 才保留。<br>**data（跨平台多样性）**：多机器人平台数据混合是泛化关键；<b>动作</b>：data 线为 EDA 语料建「工具/器件/工艺节点」三维多样性标签，做固定 token 预算下的多样性消融。<br>**harness（任务族评测）**：叠衣/清桌/装箱是可复现任务族而非单题；<b>动作</b>：harness 按任务族组织 EDA 用例，报告「族内平均 + 族间最差」。<br>**风险**：① 机器人高频连续控制与 EDA 离散、分钟级工具调用**时间尺度差几个数量级**，🚫 不可直接搬 flow matching 到 tool call；② 零样本/新技能均为作者自报自选任务；③ 训练数据不可得。 |

首次收录: 2026-11-12（第八轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex RSS DOI `200`）

---

## 32. ChatGLM: A Family of Large Language Models from GLM-130B to GLM-4 All Tools（GLM-4）

| 字段 | 内容 |
|:--|:--|
| 标题 | ChatGLM: A Family of Large Language Models from GLM-130B to GLM-4 All Tools |
| 作者（前 3） | Team GLM（智谱 AI / Zhipu AI；Aohan Zeng · Bin Xu · Bowen Wang …，共 **59** 位，含 Jie Tang / Juanzi Li / Minlie Huang / Yuxiao Dong） |
| 年份 | 2024（arXiv 首次提交 **2024-06-18**；最新 **v2** 2024-07-30，本线实测） |
| 会议 / 期刊 | 预印本技术报告（arXiv only；OpenAlex `type=preprint`，**会议收录未查**，🚫 不写「NeurIPS/ACL」之类未经核实的出处） |
| 被引数 | **1,879**（OpenAlex，DOI `10.48550/arxiv.2406.12793`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2406.12793> ｜ DOI `10.48550/arxiv.2406.12793` |
| 一句话贡献 | GLM-4 系列（GLM-4 / GLM-4-Air / GLM-4-9B）在 **约 10 万亿 token（以中英为主，另有 24 语种小比例语料）**上预训练，用**多阶段后训练（SFT + 人类反馈）**做中英对齐；据摘要，GLM-4 在 MMLU / GSM8K / MATH / BBH / GPQA / HumanEval 上「接近或超过 GPT-4」、IFEval 指令遵循「接近 GPT-4-Turbo」、长上下文与 GPT-4 Turbo（128K）/ Claude 3 相当、AlignBench 中文对齐「超过 GPT-4」；**GLM-4 All Tools** 学会判断「何时、调用哪个工具」（浏览器 / Python / 文生图 / 自定义函数）。 |
| 与我们工作的关系 | **pretrain（中文语料配比，直接）**：这是公开报告里少见的「中文为主 + 10T token」完整配方叙述，可作为 BaiZe 中文 token 预算与中英配比的对照基线（作者自报，非复现）。<b>动作</b>：pretrain 线在配比实验里加一行「中文占比」维度，固定总 token 做 3 档（30% / 50% / 70% 中文）并在同一 held-out 中文评测上报告。<br>**data（多语种长尾）**：正文提到 24 语种的小比例语料；<b>动作</b>：data 线把「长尾语种/长尾工具文档」单列一类，标出其 token 占比，便于判断是否被中英淹没。<br>**zhulong（All Tools 的工具选择）**：与我们「model 决定调哪个 EDA 工具」同构；<b>动作</b>：zhulong 线在评测里把「选错工具」「参数错」「该调不调」分开计分，而不是只算最终成功率。<br>**harness（对齐口径）**：IFEval / AlignBench 是「指令遵循」的公开口径；<b>动作</b>：harness 引用前先确认版本与语言子集，禁止把中文 AlignBench 分数与英文 IFEval 混排。<br>**风险**：① 全部为厂商自报、基准自选；② 训练数据不可得、配比只给方向不给精确比例；③ 「超过 GPT-4」是 2024 年的对照，🚫 不得当作当前 SOTA。 |

首次收录: 2026-11-12（第九轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 33. MiniMax-01: Scaling Foundation Models with Lightning Attention

| 字段 | 内容 |
|:--|:--|
| 标题 | MiniMax-01: Scaling Foundation Models with Lightning Attention |
| 作者（前 3） | MiniMax（团队署名，**按字母序**：Aonian Li · Bangwei Gong · Bo Yang …，共 **90** 位） |
| 年份 | 2025（arXiv 首次提交 **2025-01-14**，本线实测；仅 v1） |
| 会议 / 期刊 | 预印本技术报告（arXiv only；OpenAlex `type=preprint`） |
| 被引数 | **213**（OpenAlex，DOI `10.48550/arxiv.2501.08313`，查询日 2026-11-12；S2 未查）。⚠️ **低于 §1 的「≥500」门槛**，按用户令「必读清单优先于抽象判据」收录，🚫 不据此说它「影响力不足」或「已是经典」 |
| arXiv / DOI | <https://arxiv.org/abs/2501.08313> ｜ DOI `10.48550/arxiv.2501.08313` ｜ 代码 <https://github.com/MiniMax-AI> |
| 一句话贡献 | 用 **lightning attention（线性注意力）+ MoE** 做超长上下文：**32 个专家、总参 4,560 亿、每 token 激活 459 亿**，配合并行策略与计算-通信重叠；据摘要，训练上下文可达 **100 万 token**、推理外推到 **400 万 token**，MiniMax-VL-01 以 **5,120 亿**视觉-语言 token 继续训练，标准与自建基准上「与 GPT-4o / Claude-3.5-Sonnet 相当」，上下文长 **20–32 倍**。 |
| 与我们工作的关系 | **pretrain（线性注意力 / 混合架构，直接）**：这是「把 attention 换成线性注意力 + MoE」的完整工业级配方，与 Zhulong 的架构消融（线性注意力 / SSM / 循环深度）互为对照。<b>动作</b>：zhulong/pretrain 的架构消融表加一列「长上下文吞吐（tokens/s @ 256K）」，与「短上下文质量」并列，避免只报后者。<br>**zhulong（长上下文成本）**：100 万→400 万 token 的外推口径说明「训练长度」与「推理长度」要分开报；<b>动作</b>：成本表拆 `train_ctx` / `infer_ctx`，并注明是否含外推。<br>**vision（VL 继续训练）**：VL 版是「文本模型 + 512B VL token 继续训练」，不是从头多模态；<b>动作</b>：vision 线评估「继续训练」路线时，固定 VL token 预算，对比「继续训练 vs 从头对齐」两臂。<br>**harness（长上下文评测）**：摘要只给「与 GPT-4o 相当」的定性结论，未给逐项分数；<b>动作</b>：harness 引用时标「厂商自报、无逐项数字」，并自建 4 档长度（32K/128K/512K/1M）的 retrieval 测试。<br>**风险**：① 2025 年的对照结论已过期；② 线性注意力的质量-长度权衡在第三方复现中未必一致；③ 4,560 亿参数规模的并行细节不可复现到 2B 量级，只能借「方法选择」不能借「结论」。 |

首次收录: 2026-11-12（第九轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 34. RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control

| 字段 | 内容 |
|:--|:--|
| 标题 | RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control |
| 作者（前 3） | Anthony Brohan · Noah Brown · Justice Carbajal（et al.，共 **54** 位；含 Pete Florence（第 13）、Chelsea Finn、Sergey Levine、Karl Pertsch、Danny Driess） |
| 年份 | 2023（arXiv 首次提交 **2023-07-28**，本线实测；仅 v1） |
| 会议 / 期刊 | **会议收录未核验**（Crossref 精确标题检索未命中；arXiv 为预印本 ⇒ 🚫 不写「CoRL 2023」等未证实出处） |
| 被引数 | **2,322**（OpenAlex，DOI `10.48550/arxiv.2307.15818`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2307.15818> ｜ DOI `10.48550/arxiv.2307.15818` ｜ 项目页 <https://robotics-transformer.github.io/> |
| 一句话贡献 | 把**动作表示成文本 token**（与自然语言答案同一格式），在**机器人轨迹 + 互联网视觉-语言任务（如 VQA）上共同微调** VLM，得到端到端 VLA；据摘要，**6,000 次评测**显示其对未见物体的泛化显著提升，能执行机器人数据里没有的命令（如「放到数字 3 上」）、做基础推理（拿最小/最大/离某物最近的），并可用 **chain-of-thought** 完成多阶段语义推理（如「拿石头当锤子」）。 |
| 与我们工作的关系 | **zhulong（动作接口 = 文本 token，直接）**：这正是我们「agent 用文本 tool call 调 EDA 工具」的机器人版先例——动作不另造头，直接复用词表；<b>动作</b>：zhulong 线做「动作＝自由文本 vs 动作＝受限语法/枚举」两臂，<b>判据</b>：受限臂在参数精确率（如 W/L、约束值）上更高且解析失败率 &lt;1% 才采用。<br>**vision（VLM 主干 + 共微调）**：网页 VQA 数据与域内轨迹**混训**，说明「语义能力来自预训练、控制能力来自域内数据」；<b>动作</b>：vision 线在建域内数据时保留 10–20% 通用 VQA 混比，做「混 vs 不混」A/B，<b>判据</b>：混比臂在留出语义任务上更好且域内指标不降才保留。<br>**data（配方可借用）**：动作被序列化进训练集，意味着**数据格式统一**比数据量更关键；<b>动作</b>：data 线定义统一的 `(obs, action_text, result)` 三元组 schema，先统一格式再谈配比。<br>**harness（评测规模）**：6,000 次真机试验是「小模型 + 大评测预算」的样本；<b>动作</b>：harness 在报 EDA 结果时同时给「试验次数 / 每次成本」，避免用 20 次试验下结论。<br>**风险**：① 真机高频控制与分钟级工具调用时间尺度差异极大；② 「涌现能力」为作者自报、任务自选；③ 动作离散分桶会损失精度（对连续参数尤其明显），🚫 不可直接照搬。 |

首次收录: 2026-11-12（第九轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`；会议未核验）

---

## 35. Octo: An Open-Source Generalist Robot Policy

| 字段 | 内容 |
|:--|:--|
| 标题 | Octo: An Open-Source Generalist Robot Policy |
| 作者（前 3） | Octo Model Team（Dibya Ghosh · Homer Walke · Karl Pertsch …，共 **19** 位；含 Sergey Levine / Chelsea Finn / Dorsa Sadigh） |
| 年份 | 2024（arXiv 首次提交 **2024-05-20**，本线实测；最新 **v2** 2024-05-26） |
| 会议 / 期刊 | **Robotics: Science and Systems (RSS) 2024**（Crossref 实测 DOI `10.15607/rss.2024.xx.090`，`issued 2024-07-15`） |
| 被引数 | **1,192**（OpenAlex，DOI `10.48550/arxiv.2405.12213`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2405.12213> ｜ DOI `10.15607/rss.2024.xx.090` ｜ 项目页 <https://octo-models.github.io> |
| 一句话贡献 | 开源通用机器人策略：transformer 策略在 **Open X-Embodiment 的 80 万条轨迹**上训练，可用**语言指令或目标图像**指定任务，并能在**消费级 GPU 上数小时内**微调到**新的传感器与动作空间**；据摘要，在 **9 个机器人平台**上验证其可作为通用初始化，并系统消融了架构与训练数据的设计选择。 |
| 与我们工作的关系 | **data（跨平台数据 + 微调成本，直接）**：80 万轨迹混合训练 + 「几小时即可适配新动作空间」是「数据规模换适配成本」的量化样本；<b>动作</b>：data 线统计我们的「新工具/新 PDK 接入成本（人天）」，设目标 ≤1 天，并把所需域内样本量记进接入清单。<br>**zhulong（新动作空间适配）**：换动作空间只需微调而非重训，对应我们「新增一个 EDA 工具/命令」的场景；<b>动作</b>：zhulong 做「新增工具只用 1k / 5k / 20k 条示例」三档，报告成功率随样本量的曲线，<b>判据</b>：5k 档达到 20k 档 −5 点以内即认为「低成本可接入」。<br>**vision（多模态条件）**：语言或目标图像两种任务指定方式并存；<b>动作</b>：vision 线在版图任务上对比「文本描述 vs 参考图」，<b>判据</b>：参考图臂在布局类任务上高 ≥3 点才引入图像条件。<br>**harness（9 平台矩阵）**：跨平台矩阵而非单平台单任务；<b>动作</b>：harness 的 EDA 评测按「工具 × PDK × 任务族」出矩阵，报告每格 n 与最差格。<br>**风险**：① 机器人动作空间是同构低维连续量，EDA 工具调用是异构离散结构，🚫 不能假设「几小时适配」可平移；② 消融结论绑定其数据规模；③ 作者自报。 |

首次收录: 2026-11-12（第九轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`；Crossref RSS DOI `200`）

---

## 36. SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

| 字段 | 内容 |
|:--|:--|
| 标题 | SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering |
| 作者（前 3） | John Yang · Carlos E. Jimenez · Alexander Wettig（et al.，共 **7** 位；含 Shunyu Yao / Karthik Narasimhan） |
| 年份 | 2024（arXiv 首次提交 **2024-05-06**，最新 **v3** 2024-11-11，本线实测） |
| 会议 / 期刊 | **NeurIPS 2024**（OpenAlex `primary_location.source` = `neural information processing systems`，DOI `10.52202/079017-1601`，pp. 50528–50652） |
| 被引数 | **1,502**（OpenAlex，DOI `10.48550/arxiv.2405.15793`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2405.15793> ｜ 会场 DOI `10.52202/079017-1601` ｜ 代码 <https://swe-agent.com> |
| 一句话贡献 | 提出「**agent-计算机接口（ACI）必须为人之外的另一种用户单独设计**」：给 LM agent 定制打开文件/编辑/检索/执行测试的接口，抑制低层无效动作；据摘要，在 SWE-bench 上 pass@1 **12.5%**、HumanEvalFix **87.7%**，均称当时最好，并分析 ACI 设计如何改变 agent 行为。 |
| 与我们工作的关系 | **harness（直接，接口即能力）**：本文的核心主张是「**接口设计本身就是方法**」——同一模型换 ACI，SWE-bench 分数差一大截。这正是我们 harness 线在做的事（工具封装、输出截断、报错回显格式）。<b>动作</b>：harness 线做「同一个 2B/7B 模型 × 两套工具封装（原样 vs ACI 式：统一 edit 命令 + 限长输出 + 明确错误摘要）」的配对实验，<b>判据</b>：ACI 臂在一族 EDA 任务上成功率高 ≥3 点且平均轮次不升；否则不引入。<br>**designflow（工具接口保真度）**：ACI 是对真实工具（git / 测试 / 编辑器）的**窄接口**，而不是自由 shell；<b>动作</b>：designflow 的 L1–L5 保真度里加一条「接口粒度」维度（自由 shell / 受限命令集），造题时两档都出。<br>**data（轨迹数据格式）**：agent 的每一步被记录成「命令 + 观察 + 结果」，可直接转成训练轨迹；<b>动作</b>：data 线统一 `<cmd, obs, reward>` schema，并保留失败轨迹（负样本占比单独统计）。<br>**风险**：① SWE 任务（仓库级代码修复）与 EDA 工具（分钟级综合/仿真）时间尺度与错误面不同；② 12.5% 是 2024 年的基线，🚫 不可当作现在的能力参照；③ 作者自报。 |

首次收录: 2026-11-12（第十轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 37. Tree of Thoughts: Deliberate Problem Solving with Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Tree of Thoughts: Deliberate Problem Solving with Large Language Models |
| 作者（前 3） | Shunyu Yao · Dian Yu · Jeffrey Zhao（et al.，共 **7** 位；含 Izhak Shafran / Thomas L. Griffiths / Yuan Cao / Karthik Narasimhan） |
| 年份 | 2023（arXiv 首次提交 **2023-05-17**，最新 **v2** 2023-12-03，本线实测） |
| 会议 / 期刊 | **NeurIPS 2023**（arXiv `comments` 明写 camera-ready；OpenAlex DOI `10.52202/075280-0517`，pp. 11809–11822） |
| 被引数 | **3,112**（OpenAlex，DOI `10.48550/arxiv.2305.10601`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.10601> ｜ 会场 DOI `10.52202/075280-0517` ｜ 代码 <https://github.com/princeton-nlp/tree-of-thought-llm> |
| 一句话贡献 | 把 CoT 从「一条链」推广成「**思维树**」：在「思维」这一语义单元上做多分支探索 + 自评 + 前瞻/回溯，使推理可搜索；据摘要，在 24 点游戏上 GPT-4 + CoT 只有 **4%** 成功率，ToT 达 **74%**（另两个任务为创意写作与迷你填字）。 |
| 与我们工作的关系 | **zhulong（推理期算力分配，直接）**：ToT 证明「**多花推理算力换成功率**」是独立可调的一根轴，和我们「thinking / 语言轴」的消融是同一族问题。<b>动作</b>：zhulong 在固定总预算下比较三臂（单链 / 自洽投票 k 条 / ToT 式显式分支 + 剪枝），<b>判据</b>：ToT 臂只有在「每题工具调用次数不增 30%」时才算赢，否则记「贵而不值」。<br>**harness（评测口径）**：ToT 的收益高度依赖「有可自动判定的中间状态」（24 点游戏可验算）；<b>动作</b>：harness 给每类 EDA 任务标注「中间步骤可否自动验证」，只在该类上允许搜索式推理，避免把不可验证任务上的失败当作方法失败。<br>**pretrain（间接）**：说明「推理能力有一部分来自推理期搜索而非权重」，<b>动作</b>：pretrain 报 base 能力时固定「无搜索」解码，别把 ToT 收益混进 base。<br>**风险**：① 任务刻意选了可搜索、可判分的玩具题，外推到长链路 EDA 流程未验证；② 成本（token × 分支数）在摘要里未给；③ 作者自报。 |

首次收录: 2026-11-12（第十轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 38. Llama 2: Open Foundation and Fine-Tuned Chat Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Llama 2: Open Foundation and Fine-Tuned Chat Models |
| 作者（前 3） | Hugo Touvron · Louis Martin · Kevin Stone（et al.，共 **68** 位，Meta AI） |
| 年份 | 2023（arXiv 首次提交 **2023-07-18**，最新 **v2** 2023-07-19，本线实测） |
| 会议 / 期刊 | **预印本技术报告**（arXiv only；OpenAlex `primary_location.source` = `arXiv (Cornell University)`，无会议 DOI ⇒ 🚫 不写「某会议」） |
| 被引数 | **19,635**（OpenAlex，DOI `10.48550/arxiv.2307.09288`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2307.09288> ｜ DOI `10.48550/arxiv.2307.09288` |
| 一句话贡献 | 7B / 13B / 70B 三档**预训练 + 对话微调**模型全家桶（Llama 2-Chat），并首次把「**SFT → RLHF（拒绝采样 + PPO）→ 多轮安全迭代**」的完整配方与安全评估公开写清；据摘要，在多数测试基准上优于开源对话模型，人工评测的 helpfulness / safety 结果「可作为闭源模型的替代」。 |
| 与我们工作的关系 | **pretrain（配方 + 规模档位，直接）**：3 档同族模型 = 天然的「规模-能力」对照表；<b>动作</b>：pretrain 线报结果时固定「同族至少两档规模」，别只报单点，便于与我们 2B 定位比较。<br>**zhulong（post-train 三段式）**：SFT → 拒绝采样 → PPO 的顺序与「安全数据反复回流」是工业界标准做法；<b>动作</b>：zhulong 的 post-train 消融按这三级拆开报（SFT-only / +拒绝采样 / +RL），每级都记数据量与算力，<b>判据</b>：后一级必须在留出集上带来 ≥2 点且不损前一级能力才保留。<br>**data（数据量与配比披露口径）**：报告给了 token 规模与微调数据量级但**未给完整配比**——这正是我们可追问的缺口；<b>动作</b>：data 线对外汇报时也采用「总量公开、配比分级」的口径，内部留完整配比表。<br>**风险**：① 68 位作者、报告式写作，很多关键数字在附录表里，🚫 不要引二手博客的转述数字；② 2023 年的安全/对齐结论已明显过时；③ 开源许可有商用限制条款（需另核）。 |

首次收录: 2026-11-12（第十轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`；会议=无）

---

## 39. Improved Baselines with Visual Instruction Tuning（LLaVA-1.5）

| 字段 | 内容 |
|:--|:--|
| 标题 | Improved Baselines with Visual Instruction Tuning |
| 作者（前 3） | Haotian Liu · Chunyuan Li · Yuheng Li（et al.，共 **4** 位；含 Yong Jae Lee） |
| 年份 | 2023（arXiv 首次提交 **2023-10-05**，最新 **v2** 2024-05-15，本线实测） |
| 会议 / 期刊 | **CVPR 2024（highlight）**（arXiv `comments` 明写 camera ready；OpenAlex DOI `10.1109/cvpr52733.2024.02484`，pp. 26286–26296） |
| 被引数 | **3,281**（OpenAlex，DOI `10.48550/arxiv.2310.03744`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2310.03744> ｜ 会场 DOI `10.1109/cvpr52733.2024.02484` ｜ 项目页 <https://llava-vl.github.io> |
| 一句话贡献 | 一篇「**把基线做扎实**」的短文：只改三处——视觉塔换 **CLIP-ViT-L-336px**、投影从 Linear 换 **MLP**、加入**学术任务型 VQA 数据 + 简单回答格式提示**——就在 **11 个基准**上取得当时最好；据摘要，**13B 权重仅用 120 万公开数据**，单台 **8×A100 约 1 天**训完。 |
| 与我们工作的关系 | **vision（最小可行配方，直接）**：这是「**小改动 + 公开数据 + 1 天 8 卡**」的性价比样本，正好对应我们 vision 线「有限算力下先把基线打牢」的处境。<b>动作</b>：vision 线把三处改动做成三个开关（视觉塔分辨率 / 投影层类型 / 是否混学术 VQA），做 2³ 全因子或至少三组单变量对照，<b>判据</b>：某开关若在我们域内（版图/波形）指标上 <1 点收益，则不引入，避免无谓复杂度。<br>**data（数据效率口径）**：120 万条公开数据 + 简单格式提示就能对齐，说明「**格式一致性**」比数据量更便宜有效；<b>动作</b>：data 线把「回答格式模板」当作独立变量做 A/B（同数据、不同模板）。<br>**pretrain（算力口径）**：8×A100 × 1 天是罕见的「可复现训练预算」披露；<b>动作</b>：pretrain/vision 报训练成本统一用「卡数 × 小时 × 卡型」，并注明是否含数据加载。<br>**风险**：① 只报「11 个基准最好」而未逐项列数，🚫 不要转述具体分数；② 视觉塔分辨率提升带来的收益与其算力开销不可分；③ 作者自报。 |

首次收录: 2026-11-12（第十轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 40. The Llama 3 Herd of Models

| 字段 | 内容 |
|:--|:--|
| 标题 | The Llama 3 Herd of Models |
| 作者（前 3） | Aaron Grattafiori · Abhimanyu Dubey · Abhinav Jauhri（et al.，**Meta AI 团队署名，作者列表 561 人**） |
| 年份 | 2024（arXiv 首次提交 **2024-07-31**，最新 **v3** 2024-11-23，本线实测） |
| 会议 / 期刊 | **预印本技术报告**（arXiv only；OpenAlex `primary_location.source` = `arXiv (Cornell University)`，无会场 DOI ⇒ 🚫 不写「某会议」） |
| 被引数 | **23,796**（OpenAlex，DOI `10.48550/arxiv.2407.21783`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2407.21783> ｜ DOI `10.48550/arxiv.2407.21783` |
| 一句话贡献 | **405B 稠密 Transformer、上下文最高 128K** 的模型家族，原生支持多语言 / 代码 / 推理 / 工具；据摘要，在大量任务上与 GPT-4 质量相当，公开 405B 的预训练与后训练权重及 Llama Guard 3，并用「组合式」方式把图像 / 视频 / 语音接入（多模态版本自述仍在开发、未广泛发布）。 |
| 与我们工作的关系 | **pretrain（规模档位 + 长上下文口径）**：同族多尺寸 + 128K 上下文 = 报「长上下文 ROI」时的外部参照；<b>动作</b>：pretrain 报长上下文消融时固定「同族两档规模」并显式注明上下文长度与位置编码方案，<b>判据</b>：上下文翻倍带来的域内增益 &gt;1 绝对点且平均序列成本增幅可接受才保留。<br>**vision（主干复用 / 组合式接入，直接）**：官方路线是「语言主干 + 视觉/语音适配器」的组合式，与我们 vision 线「冻结主干 + 适配层」同构；<b>动作</b>：把「适配器容量」当独立变量（线性 / MLP / 小 Transformer），<b>判据</b>：域内 held-out +2 绝对点才升档。<br>**data（披露口径）**：报告按能力维度（多语言 / 代码 / 推理 / 工具）组织，但摘要未给配比 —— 这正是我们对外汇报可采用的口径（**总量公开、配比分级**）。<br>**zhulong（工具使用）**：把 tool usage 列为原生能力，可作为「工具调用是否要单独 SFT 一阶段」的对照假设。<br>**风险**：① 405B 与我们 2B 差两个数量级，规模结论**不可直接迁移**；② 团队报告、数字自报；③ 多模态部分自述未发布，🚫 不得当作可用能力。 |

首次收录: 2026-11-12（第十一轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`；会议=无）

---

## 41. RT-1: Robotics Transformer for Real-World Control at Scale

| 字段 | 内容 |
|:--|:--|
| 标题 | RT-1: Robotics Transformer for Real-World Control at Scale |
| 作者（前 3） | Anthony Brohan · Noah Brown · Justice Carbajal（et al.，**共 51 位**；含 Chelsea Finn / Brian Ichter / Sergey Levine / Karol Hausman） |
| 年份 | 2022（arXiv 首次提交 **2022-12-13**，最新 **v2** 2023-08-11，本线实测） |
| 会议 / 期刊 | **RSS 2023**（Robotics: Science and Systems；OpenAlex 会场 DOI `10.15607/rss.2023.xix.025`） |
| 被引数 | **2,747**（OpenAlex，DOI `10.48550/arxiv.2212.06817`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2212.06817> ｜ 会场 DOI `10.15607/rss.2023.xix.025` ｜ 项目页 <https://robotics-transformer1.github.io> |
| 一句话贡献 | 提出 **Robotics Transformer（RT-1）**：以「任务无关的大规模真机数据 + 高容量架构」替代任务专用模型；据摘要，在真实机器人上按 **数据规模 / 模型规模 / 数据多样性** 三轴验证了泛化随规模提升的可扩展性质（即机器人版的 scaling 观察）。 |
| 与我们工作的关系 | **vision（视觉-动作同构）**：图像帧 → 离散动作 token 的端到端路径，与我们「截图/版图 → 工具调用」的结构同型；<b>动作</b>：vision 线把「观测编码是否冻结」作为消融臂。<br>**harness（真机/真工具评测规模）**：其结论建立在**大规模真实评测**上，而不是仿真小样本；<b>动作</b>：harness 线给每个任务族记录「评测样本数 / 随机种子数 / 是否换环境」，<b>判据</b>：样本 &lt;50 的差异不得写成结论。<br>**data（多样性 &gt; 重复量）**：三轴里「数据多样性」是独立变量，正对应我们 EDA 语料的「工具 / 器件 / 节点」多样性；<b>动作</b>：固定 token 预算做「单节点重复 vs 多节点均衡」两臂。<br>**zhulong（动作接口）**：离散化动作 token 的粒度选择与我们「工具调用参数分桶 vs 自由文本」是同一取舍。<br>**designflow（任务族覆盖）**：任务族广度是能力上限的主因，<b>动作</b>：designflow 造题先补「任务族数量」，再谈单题难度。<br>**风险**：① 真机数据规模远超我们可得数据；② 摘要未给具体成功率数字（本线不转述二手数字）；③ 作者自报。 |

首次收录: 2026-11-12（第十一轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 42. Deep reinforcement learning from human preferences（Christiano et al. 2017）

| 字段 | 内容 |
|:--|:--|
| 标题 | Deep reinforcement learning from human preferences |
| 作者（前 3） | Paul Christiano · Jan Leike · Tom B. Brown（et al.，**共 6 位**；含 Shane Legg / Dario Amodei） |
| 年份 | 2017（arXiv 首次提交 **2017-06-12**，最新 **v4** 2023-02-17，本线实测） |
| 会议 / 期刊 | **NeurIPS 2017**（OpenAlex `locations` 含 `neural information processing systems`，落地页 `papers.nips.cc/paper/7017-deep-reinforcement-learning-from-human-preferences.pdf`） |
| 被引数 | **1,643**（OpenAlex，DOI `10.48550/arxiv.1706.03741`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1706.03741> ｜ DOI `10.48550/arxiv.1706.03741` |
| 一句话贡献 | 用**人对「两条轨迹片段」的成对偏好**定义目标：先学 reward model，再用 RL 优化策略；据摘要，在 Atari 与仿真机器人上可在**不到 1% 的交互量**获得反馈的情况下解决复杂任务，并展示约 **1 小时人类时间**即可训出全新行为。 |
| 与我们工作的关系 | **zhulong（RLHF 的起点，直接）**：这是「reward 不是写出来的，是学出来的」的原始论证，对应我们「可验证奖励 vs 学到的奖励」这条决策线；<b>动作</b>：zhulong 做三臂（纯规则奖励 / 纯偏好奖励 / 规则+偏好混合），<b>判据</b>：混合臂在留出集上不低于纯规则臂且对规则覆盖不到的失败模式有 &gt;2 点改善才保留。<br>**data（标注预算口径）**：「&lt;1% 交互量」是可写进标注预算表的参照量级；<b>动作</b>：data 线记录「每条轨迹的标注条数 / 成对比较数 / 标注者数」。<br>**harness（偏好标注的评测化）**：成对比较天然可转成评测协议；<b>动作</b>：harness 对主观项（可读性、修复建议质量）用成对盲评，而不是绝对打分。<br>**风险**：① 2017 年任务（Atari / 仿真机器人）与 LLM 工具调用差异极大，🚫 不可直接外推比例；② 「1 小时人类时间」是特定任务下的口径；③ 作者自报。 |

首次收录: 2026-11-12（第十一轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 43. Learning to summarize from human feedback（Stiennon et al. 2020）

| 字段 | 内容 |
|:--|:--|
| 标题 | Learning to summarize from human feedback |
| 作者（前 3） | Nisan Stiennon · Long Ouyang · Jeff Wu（et al.，**共 9 位**；含 Daniel M. Ziegler / Alec Radford / Dario Amodei / Paul Christiano） |
| 年份 | 2020（arXiv 首次提交 **2020-09-02**，最新 **v3** 2022-02-15，本线实测） |
| 会议 / 期刊 | **NeurIPS 2020**（arXiv `comments` 原文 `NeurIPS 2020`） |
| 被引数 | **945**（OpenAlex，DOI `10.48550/arxiv.2009.01325`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2009.01325> ｜ DOI `10.48550/arxiv.2009.01325` |
| 一句话贡献 | 在摘要任务上把「人类成对比较 → reward model → RL 微调」跑通：据摘要，模型在 TL;DR 上**显著优于人类参考摘要**与更大的纯监督微调模型，且**无需新闻域微调**就迁移到 CNN/DM、接近人类参考水平；并证明**按人类偏好优化优于按 ROUGE 优化**。 |
| 与我们工作的关系 | **zhulong（RL 微调流程，直接）**：SFT → reward model → RL 的三段式在此定型，是 InstructGPT 的直接前身；<b>动作</b>：zhulong 的 post-train 消融按「SFT-only / +RM 重排 / +RL」三级拆开报，每级记偏好数据量。<br>**data（偏好数据质量）**：报告对偏好数据集做了专门分析（摘要明写）⇒ <b>动作</b>：data 线对偏好数据单独建表（来源、标注者、成对一致率），与预训练语料分开统计。<br>**harness（评测口径迁移）**：「ROUGE 优化 ≠ 人想要的」是可复用的判据：<b>动作</b>：harness 对生成类任务必须同时报「自动指标」与「成对盲评胜率」，<b>判据</b>：两者方向相反时以盲评为准并在报告中注明。<br>**风险**：① 单一任务（摘要），外推到工具调用/EDA 流程未验证；② 人类参考摘要本身有噪声；③ 作者自报。 |

首次收录: 2026-11-12（第十一轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`）

---

## 44. τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

| 字段 | 内容 |
|:--|:--|
| 标题 | τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains |
| 作者（前 3） | Shunyu Yao · Noah Shinn · Pedram Razavi（et al.，共 **4** 位；含 Karthik Narasimhan） |
| 年份 | 2024（arXiv 首次提交 **2024-06-17**，v1，本线实测） |
| 会议 / 期刊 | **预印本**（arXiv only；arXiv `comment` 字段为空、OpenAlex `primary_location.source` = `arXiv (Cornell University)` ⇒ 🚫 不写「某会议」） |
| 被引数 | **1,198**（OpenAlex，DOI `10.48550/arxiv.2406.12045`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2406.12045> ｜ DOI `10.48550/arxiv.2406.12045` |
| 一句话贡献 | 用**语言模型模拟用户** + 域内 API 工具 + 政策约束，构造动态多轮对话任务；判分不靠文本匹配，而是**比对对话结束时的数据库状态与标注目标状态**，并提出 `pass^k` 衡量同一任务多次试验的**一致性**；据摘要，gpt-4o 类 SOTA 函数调用 agent 成功率 **<50%**，retail 域 `pass^8` **<25%**。 |
| 与我们工作的关系 | **harness（直接，最高优先）**：这是「**终态判分**」的范式样本 —— 我们的 EDA 任务同样有客观终态（工具跑通 / DRC 通过 / 网表一致），比「让裁判 LLM 打分」更可验证。<b>动作</b>：harness 把每条任务写成三元组 `(初始状态, 允许的 API 集, 目标终态谓词)`，判分只读终态；并新增 `pass^k`（同任务 k 次独立试验全过率）作为稳定性指标。<b>判据</b>：报告主表必须同时给「单次成功率」与 `pass^4`；两者差距 >20 点即判定该任务对随机性过敏，须先降方差再谈提升。<br>**zhulong（规则遵循）**：论文的核心失败模式是「不按域内政策办事」而非「不会调工具」——<b>动作</b>：zhulong 的 post-train 消融加入「政策违规率」这一独立指标（违规次数 / 总轮数），不要只看任务成功率。<br>**data（用户模拟器）**：用 LM 扮演用户 = 可无限扩样的交互数据源；<b>动作</b>：data 线先固定 2–3 个用户模拟 prompt 模板做 A/B，避免模拟器本身成为混淆变量。<br>**designflow（造题结构）**：`(状态, 工具, 目标谓词)` 正好可作为 designflow L1–L5 保真度的**判分骨架**。<br>**风险**：① 摘要只给 `gpt-4o` 与 retail 两个数字，🚫 不要外推成「所有 agent 都 <50%」；② 任务域是 retail / airline，与 EDA 差异大；③ 用户模拟器与真实用户分布不一致；④ 被引数高含「被当作 baseline 引用」的成分。 |

首次收录: 2026-11-12（第十二轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`；会议=无）

---

## 45. Temporal Difference Learning and TD-Gammon

| 字段 | 内容 |
|:--|:--|
| 标题 | Temporal Difference Learning and TD-Gammon |
| 作者（前 3） | Gerald Tesauro（**独著**；论文发表时为 IBM Thomas J. Watson Research Center） |
| 年份 | 1995（CACM **38(3):58–68**，1995-03；前身：1994 Neural Computation **6(2):215–219**） |
| 会议 / 期刊 | **Communications of the ACM 38(3), pp. 58–68**（Crossref `10.1145/203330.203343` 实测 `200`，卷 38 / 期 3 / 页 58–68）｜ 1994 姊妹篇 **Neural Computation 6(2):215–219**（DOI `10.1162/neco.1994.6.2.215`） |
| 被引数 | **1,680**（1995 CACM 版，OpenAlex，查询日 2026-11-12）｜ **823**（1994 Neural Computation 版，同源同查；S2 未查） |
| arXiv / DOI | 🚫 **无 arXiv**（1995 年 ACM 期刊）｜ CACM DOI <https://doi.org/10.1145/203330.203343> ｜ Neural Computation DOI <https://doi.org/10.1162/neco.1994.6.2.215> |
| 一句话贡献 | **1994 摘要原文（OpenAlex 全文摘要，2026-11-12 取）**：TD-Gammon 是「一个神经网络，**只靠与自己下棋并从结果中学习**就能学会下西洋双陆棋，基于 TD(λ) 强化学习算法（Sutton 1988）」；「从随机初始权重起步（因而初始策略随机）仍达到**惊人的强**水平」；「只给棋盘状态的『原始』描述时学到**强中级水平**；加入一组手工特征后达到**真正惊人**的性能」。🚫 本线**未取到 1995 CACM 正文**（付费墙），**不引任何胜率/ELO 数字**。 |
| 与我们工作的关系 | **zhulong（自对弈 RL 的最早成功案例，直接）**：证明「**只有最终胜负信号 + 自我对弈**」也能学出强策略 —— 与我们「用可验证结果（工具跑通 / DRC 通过）当奖励、用历史快照当陪练」的路线同构。<b>动作</b>：zhulong 的自对弈实验里把「**是否给手工特征/先验**」作为一个消融轴（原始输入 vs 加领域先验），<b>判据</b>：加先验臂要在固定预算下比原始输入臂高 ≥5 绝对点才值得维护特征管线。<br>**pretrain（数据效率的极端案例）**：零外部数据、纯自生成 —— 是「合成数据能否替代真人数据」这条讨论的历史锚点；<b>动作</b>：data/pretrain 报合成数据占比时，引用它作为「纯自生成可达强中级、但需先验才到顶级」的旁证（注明是棋盘游戏）。<br>**harness（评测设计）**：棋盘游戏「规则明确、结果客观」正是 `pass^k` 与终态判分的理想前提；<b>动作</b>：harness 对自对弈类实验固定「对手池 + 固定种子 + 局数」，禁止只报对单一对手的胜率。<br>**风险**：① **单一游戏 + 1990 年代算力**，外推到 LLM 工具调用无直接证据；② 1995 CACM 正文未读，**只用 1994 摘要内的表述**；③ 被引含大量「TD 教学引用」；④ 摘要里「惊人 / staggering」是作者修辞，🚫 不可当量化结论。 |

首次收录: 2026-11-12（第十二轮）｜ 状态: 元数据已核验（Crossref `200` + OpenAlex `200`；1994 摘要取 OpenAlex 全文摘要；1995 正文未取）

---

## 46. Video generation models as world simulators（Sora 技术报告）

| 字段 | 内容 |
|:--|:--|
| 标题 | Video generation models as world simulators |
| 作者（前 3） | Bill Peebles · Tim Brooks · Connor Holmes（et al., OpenAI；⚠️ **作者顺序未能在官方页二次核对** —— 本机 403，见下） |
| 年份 | 2024（OpenAI 官方技术报告，2024-02 发布） |
| 会议 / 期刊 | **OpenAI 技术报告**（🚫 **无 arXiv、无 DOI**；本线**不造 arXiv 号 / DOI**） |
| 被引数 | **未查**（无 DOI ⇒ OpenAlex 无精确匹配；Semantic Scholar 本轮未查。🚫 不写估算值） |
| arXiv / DOI | 🚫 无 ｜ 官方页 <https://openai.com/index/video-generation-models-as-world-simulators/>（本机实测 **`403`**：直连、Mihomo 代理、Wayback、`r.jina.ai` 全部被拒 ⇒ **正文未取到**） |
| 一句话贡献 | 官方报告的标题即其主张：把**视频生成模型当作「世界模拟器」**，即在大规模视频上训练的生成模型可作为通往通用物理世界模拟的一条路径。（⚠️ **本行只据官方标题与公开摘要表述**；正文 403 未取到，**不引任何数字、不转述实验细节**。） |
| 与我们工作的关系 | **vision（方法路线参照）**：视频生成所需的「时空一致性」与我们版图/波形这类二维结构数据的建模有共通点（长程依赖 + 局部保真）；<b>动作</b>：vision 线若做生成式数据增广，预注册「局部保真度」与「长程一致性」两个指标分开报，🚫 不合并成一个总分。<br>**designflow（仿真的替代品？）**：若模型能稳定预测「动作后的画面」，理论上可做**廉价 rollout**（类似 Dyna 的 model-based 规划）；<b>动作</b>：designflow 先做一个**极小规模验证**：用生成模型预测工具调用后的中间产物，与真实工具输出比对，<b>判据</b>：结构一致率 <80% 就不投这条线。<br>**pretrain（数据形态）**：报告的存在本身说明「视频数据可作为预训练主模态」——对我们只是一条旁证；<b>动作</b>：无（我们无视频数据）。<br>**风险**：① **正文未取到（403）** ⇒ 本条**只有标题级信息**，任何细节（时长、分辨率、patch 方案、分数）本线**一律不写**；② 「世界模拟器」是作者主张，不是被独立验证的结论，🚫 不可写成「Sora 已实现世界模型」；③ 官方博客式报告无同行评议。 |

首次收录: 2026-11-12（第十二轮）｜ 状态: ⚠️ **部分核验**（官方页标题可确认；正文 403 未取到；无 DOI ⇒ 被引未查）

---

## 47. Kimi K2: Open Agentic Intelligence

| 字段 | 内容 |
|:--|:--|
| 标题 | Kimi K2: Open Agentic Intelligence |
| 作者（前 3） | Kimi Team（团队署名）· Yifan Bai · Yiping Bao（et al.，作者列表数百人，本线只列前 3） |
| 年份 | 2025（arXiv 首次提交 **2025-07-28**，最新 **v2** 2026-02-03，本线实测） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `comment` 原文 = `tech report of Kimi K2, with minor updates`；OpenAlex `primary_location.source` = arXiv ⇒ 🚫 不写会议） |
| 被引数 | **1,410**（OpenAlex，DOI `10.48550/arxiv.2507.20534`，查询日 2026-11-12；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2507.20534> ｜ DOI `10.48550/arxiv.2507.20534` |
| 一句话贡献 | **32B 激活 / 1T 总参**的 MoE；提出 **MuonClip**（Muon + 新的 QK-clip）解决训练不稳定，**15.5T token 预训练零 loss spike**；后训练含**大规模 agentic 数据合成 + 联合 RL**；作者自报 Tau2-Bench **66.1** / ACEBench(En) **76.5** / SWE-Bench Verified **65.8** / SWE-Bench Multilingual **47.3**（称开源非思考模型 SOTA）。 |
| 与我们工作的关系 | **pretrain（训练稳定性，直接可用）**：`MuonClip` 的「QK-clip 防 attention logit 爆炸」是**可直接抄的工程手段**，且给了「15.5T token 零 spike」这一强证据。<b>动作</b>：pretrain 线在 WSD 长跑前先做 **1B 级小规模对照**（Muon vs MuonClip vs AdamW），监控 `max attention logit` 与 loss spike 次数；<b>判据</b>：MuonClip 若在等 token 下把 spike 次数降到 0 且 loss 不低于 AdamW，就在 2B 主跑采用。<br>**data（agentic 数据合成）**：大规模合成 agentic 轨迹是能力来源之一；<b>动作</b>：data 线把「合成轨迹 / 真实轨迹」比例单列一栏，做 3 档消融。<br>**harness（评测口径）**：Tau2-Bench / SWE-Bench 是**自选基准**，<b>动作</b>：引用其分数时必须标「作者自报 + 日期 + 自选基准」，🚫 不写成「当前 SOTA」。<br>**zhulong（联合 RL）**：真实 + 合成环境联合 RL 与我们的「可验证奖励 + 自举环境」同构；<b>动作</b>：zhulong 记录「环境真实性占比」（真实工具 vs 模拟器）作为一列。<br>**风险**：① 1T 总参远超我们 2B 量级，**规模不可迁移**，只能抄方法与判据；② 全部分数为**作者自报、基准自选**；③ 「零 loss spike」是特定配置下的结果，不等于 MuonClip 普适；④ 数百人署名，无法逐条核对。 |

首次收录: 2026-11-12（第十二轮）｜ 状态: 元数据已核验（arXiv API `200` + `application/atom+xml`；OpenAlex `200`；会议=无）

---

## 48. Direct Preference Optimization: Your Language Model is Secretly a Reward Model（DPO）

| 字段 | 内容 |
|:--|:--|
| 标题 | Direct Preference Optimization: Your Language Model is Secretly a Reward Model |
| 作者（前 3） | Rafael Rafailov · Archit Sharma · Eric Mitchell（et al.，共 6 位：+ Stefano Ermon · Christopher D. Manning · Chelsea Finn） |
| 年份 | 2023（arXiv 首次提交 **2023-05-29**；本线取到 **v3 / 2024-07-29**） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `type=conference-paper`、venue `neural information processing systems`，biblio pp. **53728–53741**，会场 DOI `10.52202/075280-2338`） |
| 被引数 | **3,123**（OpenAlex，DOI `10.48550/arxiv.2305.18290`，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.18290> ｜ DOI `10.48550/arxiv.2305.18290` |
| 一句话贡献 | 摘要原文：给 RLHF 的奖励模型换一种参数化，使**最优策略可闭式解出**，于是「KL 约束下的 RLHF 目标」退化为**一个简单分类损失** —— DPO 训练稳定、无需在微调中从 LM 采样、也不必拟合独立奖励模型；摘要称在情感控制上超过 PPO 版 RLHF，在摘要与单轮对话上与 PPO 持平或更好，且实现与训练显著更简单。 |
| 与我们工作的关系 | **zhulong（奖励设计：RM-free 路线对照）**：我们现在的路线是「可验证 checker 当奖励」，DPO 给的是第三条路 —— **不建 RM、不采样，直接用成对偏好做分类损失**。<b>动作</b>：zhulong 的奖励消融表加一档「DPO（仅离线成对偏好）」与「checker 奖励」「RM+PPO」并排，<b>判据</b>：在等标注预算下，若 DPO 档在留出任务上低于 checker 档 ≥5 绝对点，则离线偏好只当冷启动、不单独使用。<br>**data（偏好数据格式）**：DPO 只需要 `(prompt, chosen, rejected)` 三元组，比 RLHF 的「打分 + 在线采样」便宜 ⇒ data 线的偏好评测协议可直接按此格式预注册。<br>**harness（已知偏置）**：论文本身未系统处理**长度偏置**（DPO 被后续工作广泛报告会利用长度）⇒ harness 报分时必须单列长度统计，🚫 不看长度只看胜率。<br>**风险**：① 实验以 1B–7B 级与对话/摘要为主，**工具调用轨迹不在其评测范围**；② 「超过 PPO」是作者自报、基准自选；③ 离线数据分布偏移问题论文未解决（已在作者信中追问）。 |

首次收录: 2026-11-12（第十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`；Crossref/OpenAlex 会场 DOI 已记）

---

## 49. Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality（Mamba-2 / SSD）

| 字段 | 内容 |
|:--|:--|
| 标题 | Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality |
| 作者（前 3） | Tri Dao · Albert Gu（**共 2 位**） |
| 年份 | 2024（arXiv 首次提交 **2024-05-31**，v1） |
| 会议 / 期刊 | **ICML 2024**（据 arXiv `comment` 字段原文 `ICML 2024`；OpenAlex 仍只记 arXiv 预印本、无会场 DOI ⇒ **不写页码**） |
| 被引数 | **1,003**（OpenAlex，DOI `10.48550/arxiv.2405.21060`，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2405.21060> ｜ DOI `10.48550/arxiv.2405.21060` |
| 一句话贡献 | 摘要原文：证明 SSM（如 Mamba）与注意力变体**通过半可分矩阵的多种分解紧密相关**，据此提出 **SSD** 框架，并设计 **Mamba-2** —— 其核心层是 Mamba 选择性 SSM 的改进，**快 2–8×**，同时在语言建模上**仍与 Transformer 有竞争力**。 |
| 与我们工作的关系 | **pretrain（吞吐 + 架构对照）**：Mamba-2 的卖点是「同精度下更快」而不是「更强」⇒ 若要评估 SSM 替换 attention，必须按**等质量（loss/困惑度）比吞吐**，🚫 只比 tokens/s。<b>动作</b>：pretrain 的架构对照表新增 `Mamba-2` 一档，只跑 1B 级短跑（≤20B token），<b>判据</b>：等 loss 下吞吐提升 ≥30% 且长上下文（≥32k）不退化才进入 2B 候选。<br>**zhulong（消融基线）**：SSD 给出「注意力 ↔ SSM」的统一视角 ⇒ 消融里可把「线性注意力 / SSM / 混合」放进**同一个矩阵分解族**解释差异，而不是当成三个黑盒。<br>**harness（成本口径）**：2–8× 是**层内**加速，端到端收益取决于 attention 占比 ⇒ harness 报「每步耗时」必须同时给 `attention 时间占比`。<br>**风险**：① 2–8× 为作者自报、特定形状（chunk 大小 / 序列长）下成立；② 与 Mamba-1 共享作者，独立复现少；③ 「与 Transformer 有竞争力」限于摘要所述中小规模。 |

首次收录: 2026-11-12（第十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`；会议据 arXiv `comment` 原文）

---

## 50. FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning

| 字段 | 内容 |
|:--|:--|
| 标题 | FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning |
| 作者（前 3） | Tri Dao（**独著，共 1 位**） |
| 年份 | 2023（arXiv 首次提交 **2023-07-17**，v1） |
| 会议 / 期刊 | ⚠️ **预印本**（arXiv `comment` 字段为空；OpenAlex `type=preprint`、location 只有 arXiv ⇒ 本线**未核到会场记录**，🚫 不写 ICLR/页码） |
| 被引数 | **1,844**（OpenAlex，DOI `10.48550/arxiv.2307.08691`，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2307.08691> ｜ DOI `10.48550/arxiv.2307.08691` |
| 一句话贡献 | 摘要原文：FlashAttention-1 只达到理论最大 FLOPs/s 的 **25–40%**，原因是 thread block / warp 间**工作划分不佳**；FlashAttention-2 通过减少非 matmul FLOPs、**跨 block 并行单个 head**、warp 间再分工，得到**约 2× 加速**（相对 FlashAttention-1），在 A100 上达理论峰值的 **50–73%**；端到端训练 GPT 式模型可达 **225 TFLOPs/s per A100（72% MFU）**。 |
| 与我们工作的关系 | **pretrain（吞吐口径，直接可用）**：`25–40%` 与 `50–73%` 这两个区间是**判断「我们的 attention 实现是否还有空间」的历史标尺**；`225 TFLOPs/s / 72% MFU` 是 A100 上的参照，我们在等模型规模上应报同一口径（MFU）而不是 tokens/s。<b>动作</b>：pretrain 训练脚本固定记录 `MFU` 与 `attention 占比`，把 FlashAttention-2 的 50–73% 当作「实现效率下限参照」，低于区间下沿先查 work partitioning 与 block 形状。<br>**harness（计费口径）**：报「训练成本」须写清 `是否用 FA-2 / head_dim / 序列长`，否则跨实验不可比。<br>**zhulong**：无直接消融价值（属实现层，不改模型），列为**基线实现要求**：消融实验统一用 FA-2，避免把工程差异算成方法差异。<br>**风险**：① 全部是 A100 上的数字，未给其它卡；② 2× 是相对 FA-1、不同形状下浮动；③ 作者自报、代码开源但本线未复现。 |

首次收录: 2026-11-12（第十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`；会议=未核到）

---

## 51. Ramulator 2.0: A Modern, Modular, and Extensible DRAM Simulator

| 字段 | 内容 |
|:--|:--|
| 标题 | Ramulator 2.0: A Modern, Modular, and Extensible DRAM Simulator |
| 作者（前 3） | Haocong Luo · Yahya Can Tuğrul · F. Nisa Bostancı（et al.，共 6 位：+ Ataberk Olgun · A. Giray Yağlıkçı · **Onur Mutlu**） |
| 年份 | 2023（arXiv 首次提交 **2023-08-21**；本线取到 **v2 / 2023-11-29**） |
| 会议 / 期刊 | **IEEE Computer Architecture Letters（CAL）** 23(1):**112–116**，DOI `10.1109/LCA.2023.3333759`（OpenAlex `type=article`，2026-11-12 实测） |
| 被引数 | **185**（OpenAlex，DOI `10.48550/arxiv.2308.11030`，查询日 **2026-11-12**；S2 未查）<br>⚠️ **低于 §1「被引 ≥500」门槛**，按判据 ④「本领域（存储）标志性 / 方法论常青」收录 —— 它是 CMU SAFARI 组维护的**公开 DRAM 模拟器**（MIT 许可），持续被新一代存储 / RowHammer 论文当评测基座。 |
| arXiv / DOI | <https://arxiv.org/abs/2308.11030> ｜ 期刊 DOI `10.1109/LCA.2023.3333759` ｜ 代码 <https://github.com/CMU-SAFARI/ramulator2> |
| 一句话贡献 | 摘要原文：把 DRAM 系统的关键部件与交互**抽象成共享接口 + 独立实现**，用简洁可读的 DRAM 规格语法与**可复用的模板化 lambda**（建模 DRAM 命令功能）来快速支持新标准（**DDR5 / LPDDR5 / HBM3 / GDDR6**）；作者以**多种 RowHammer 缓解方案**为例展示「不改基线控制器代码即可模块化加实现」，并称经严格验证、保持相对现有周期级模拟器**较快的模拟速度**。 |
| 与我们工作的关系 | **zhulong（实验基座 / 成本口径）**：如果要把「LLM 出配置 → 模拟器跑 → 回填指标」做成闭环，**模拟器本身必须是可脚本化、可批量、单次成本可控的**；Ramulator 2.0 的「规格语法 + 模块化控制器」正是把配置空间暴露成可搜参数的形态。<b>动作</b>：zhulong 在设计「批量短评测」pipeline 前，先用 Ramulator 2.0 做一次**吞吐标定**（单配置固定 trace 的墙钟时间），<b>判据</b>：若单次评测 &gt;30s，则闭环必须先做代理模型 / 缩短 trace，🚫 直接上 LLM 搜参。<br>**designflow（L1–L5 保真度分层）**：本文明确区分「timing / 功耗 / 可靠性」三类模型成熟度 ⇒ designflow 的保真度分层可参照此三分，而不是笼统一个「高/中/低」。<br>**data（存储领域语料）**：DRAM 规格语法（DDR5/LPDDR5/HBM3/GDDR6）是**结构化领域文本**的样本来源 ⇒ data 线可评估「规格文档 → 可执行配置」这类任务的语料形态。<b>风险</b>：① 被引 185 未达门槛，收录属「领域标志性」判断（我们的观察）；② 摘要未给具体加速倍数与验证误差，🚫 不写「快 N 倍」；③ 与我们 CXMT 内部模型/工具链无任何对接验证。 |

首次收录: 2026-11-12（第十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 期刊 DOI）

---

## 候选池（下轮起逐轮补，**被引数本轮未查**，勿引用）



> 只登记「已实测 arXiv 元数据」的条目；被引数待下轮 OpenAlex 批量核过再写，**本表数字一律留空 = 未查**。
> ⚠️ 第十轮把 **Llama 2 `2307.09288` / LLaVA-1.5 `2310.03744` / SWE-agent `2405.15793` / Tree of Thoughts `2305.10601`** 四条转正为 #36–#39；**第十一轮把 Llama 3 `2407.21783` / RT-1 `2212.06817` / Christiano 2017 `1706.03741` / Stiennon 2020 `2009.01325`** 四条转正为 #40–#43；**第十二轮把 τ-bench `2406.12045` / TD-Gammon（CACM `10.1145/203330.203343`）/ Sora 技术报告 / Kimi K2 `2507.20534`** 四条转正为 #44–#47（元数据 + 被引当场实测）。✅ **必读清单 37/37 条目已全部覆盖**，此后以「补充 / 更正」为主。
> ⚠️ **更正**：候选池此前记的「Kimi 月之暗面早期报告 `2401.14185`」**实测为 `TDFNet`（音视频语音分离，cs.SD），与 Kimi 无关** ⇒ 已删除该候选，改收 **Kimi K2 `2507.20534`**（已转正 #47）。
> **下轮候选（🚫 未实测前不进本表、不写 DOI / 被引）**：① ~~DPO / Mamba-2 / FlashAttention-2 / 存储方向~~ ⇒ **第十三轮已转正 #48–#51**；② **`2310.16944` Zephyr（dDPO 蒸馏）** —— 实测存在（cs.LG，2023-10-25），可作「蒸馏 + 偏好」候选，待核被引；③ **版图 / EDA 预训练**（CircuitNet 类，须先实测是否 arXiv 一手）；④ Sutton《The Bitter Lesson》（**博客，无 arXiv / 无 DOI** ⇒ 只能引原文链接，单独标注）；⑤ **SimPO / IPO 类 DPO 改进**（须实测 arXiv 一手 + 被引）。


| arXiv ID | 标题（arXiv 实测） | 首次提交 | 拟服务线 | 为什么算经典（待核被引） |
|:--|:--|:--|:--|:--|
| — | （本轮无新增候选，待下轮实测后填） | — | — | — |

> ✅ 已晋级（第三轮转正，勿再留在候选池）：`2104.09864` RoFormer（#9）· `2310.06770` SWE-bench（#10）· `2303.11366` Reflexion（#11）· `2201.11903` CoT（#12）。

<!-- 维护纪律：新条目按「首次收录日」追加到末尾（不插入到旧条目之间、不改历史数字）；被引数变动只在新条目里写，旧条目保留原查询日。 -->
