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

**本轮快照**：累计 **299** 条（**第七十八轮 2026-11-21 00:0x 补 3 条 → 299**：Horovod `1802.05799`（**1,619**，预印本）/ Deformable DETR `2010.04159`（**8,952**，arXiv `comment` = ICLR 2021 Oral）/ SigLIP 2 `2502.14786`（**1,832**，预印本）；元数据 arXiv `id_list` 单篇 **3/3 `200` + `application/atom+xml`**（`published` 齐备）+ OpenAlex **3/3 `200`**（查询日 2026-11-21）；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**（本轮 PDF 下载 30 s 内未完成）；覆盖轴 = 数据并行 ring-allreduce 的通信成本基线 / 参考点稀疏采样把收敛压 10× / 视觉塔的统一图文配方与原生宽高比）

**本轮快照**：累计 **292** 条（**第七十六轮 2026-11-20 18:0x 补 4 条 → 292**：ELECTRA `2003.10555`（**5,109**，arXiv `comment` = ICLR 2020）/ Faster R-CNN `1506.01497`（**80,700**，IEEE TPAMI 39(6):1137–1149, 2017）/ Mask R-CNN `1703.06870`（**7,047**，IEEE TPAMI 42(2):386–397, 2020）/ Soft Actor-Critic `1801.01290`（**13,567**，arXiv `comment` = ICML 2018，OpenAlex biblio pp. 1861–1870）；元数据 `id_list=2003.10555,1703.06870,1506.01497,1801.01290` **`200` + `application/atom+xml`**（9,733 B / 4 entry）+ OpenAlex **4/4 `200`**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**；覆盖轴 = 判别式预训练的样本效率 / 共享卷积特征做近零成本候选框 / 解耦掩码分支与 RoIAlign / 最大熵离策略 RL 的种子稳定性）

**本轮快照**：累计 **288** 条（**第七十五轮 2026-11-20 15:0x 补 4 条 → 288**：SimCLR `2002.05709`（**18,118**，ICML 2020）/ NeRF `2003.08934`（**1,186**，ECCV 2020 oral）/ ChatEDA `2308.10204`（**319**，IEEE TCAD 43(10):3184–3197, 2024；**&lt;500 按「本领域权威」收**）/ Routing Transformers `2003.05997`（**925**，TACL 9:53–68, 2021）；arXiv `id_list` 两批均 **`200` + atom**（10,472 B / 4 entry、9,755 B / 4 entry），OpenAlex **4/4 `200`**；ChatEDA 另用 arXiv 原生 HTML（196,479 B）读作者与 affiliation；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**；⚠️ 原计划 ELECTRA 的旧记 ID `2003.05997` 实测为 Routing Transformers ⇒ 改收后者，ELECTRA 真 ID `2003.10555` 留作下轮）

**本轮快照**：累计 **284** 条（**第七十四轮 2026-11-20 12:0x 补 4 条 → 284**：PaLM-E `2303.03378`（**4,143**，预印本）/ 3D Gaussian Splatting `2308.04079`（**12,239**，ACM TOG 2023）/ Magicoder `2312.02120`（**416**，**&lt;500 按「方法论常青」收**）/ SGDR `1608.03983`（**11,502**，arXiv `comment` = ICLR 2017）；元数据分两批实测 arXiv `id_list`：`2303.03378,2308.04079,2010.00718,2301.12597` ⇒ **`200` + atom**（9,914 B / 4 entry，其中 `2010.00718` 实测为 *When to Impute?* ⇒ **SpeechT5 的 ID 记错，本轮未收**）与 `2303.03378,2312.02120` ⇒ **`200` + atom**（6,252 B / 2 entry），`1608.03983` ⇒ **`200` + atom**（2,359 B / 1 entry），逐条按 `published` 核 + OpenAlex **4/4 `200`**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**；覆盖轴 = 多模态句子与连续状态编码进语言塔 / 各向异性高斯 + 密度控制做实时新视角合成 / 开源片段当种子自造指令数据 / 余弦退火与热重启日程）

**本轮快照**：累计 **280** 条（**第七十三轮 2026-11-20 09:0x 补 4 条 → 280**：SmoothQuant `2211.10438`（**839**）/ Chatbot Arena `2403.04132`（**2,131**）/ ALOHA+ACT `2304.13705`（**3,065**，RSS 2023）/ Dolma `2402.00159`（**674**，ACL 2024）；元数据 arXiv `id_list` **`200` + atom**（11,794 B / 4 entry）+ OpenAlex **4/4 `200`**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**；两条 OpenAlex 记 `preprint` 的如实标注、不写记忆中的会场）

**本轮快照**：累计 **276** 条（**第七十二轮 2026-11-20 06:0x 补 4 条 → 276**：MMLU `2009.03300`（**6,448**，ICLR 2021）/ Qwen2-VL `2409.12191`（**6,170**）/ The Pile `2101.00027`（**3,645**）/ DeepSeek-V2 `2405.04434`（**1,986**）；元数据 arXiv `id_list` **`200` + atom**（19,377 B / 4 entry）+ OpenAlex **4/4 `200`** + ar5iv HTML **4/4 `200`**（208,166 / 655,463 / 677,121 / 694,593 B）核数字，**未做 PDF 逐页复核**；覆盖轴 = 57 学科知识基准的聚合与污染 / 原生动态分辨率与三维位置编码 / 语料配比的「比例 × epoch」两旋钮 / MLA 的 KV cache 压缩）

**本轮快照**：累计 **272** 条（**第七十一轮 2026-11-20 03:0x 补 4 条 → 272**：C4 文档化 `2104.08758`（**990**，EMNLP 2021 pp. 1286–1305）/ ConvNeXt `2201.03545`（**13,910**，CVPR 2022 pp. 11966–11976）/ Grokking `2201.02177`（**967**）/ Mirage `2304.15004`（**1,116**，NeurIPS 2023 pp. 55565–55581）；元数据 arXiv abs 页 **4/4 `200`** + OpenAlex **4/4 `200`**；数字用 ar5iv HTML **4/4 `200`**（207,799 / 476,499 / 106,203 / 151,070 B）核对，**未做 PDF 逐页复核**；覆盖轴 = 网页语料来源审计 / 纯 ConvNet 现代化配方 / 过拟合之后的泛化 / 指标选择制造的假涌现）

**本轮快照**：累计 **268** 条（**第七十轮 2026-11-20 00:0x 补 4 条 → 268**：Transformer-XL `1901.02860`（**1,881**）/ Emu3 `2409.18869`（**1,022**）/ Medusa `2401.10774`（**1,028**）/ Janus `2410.13848`（**633**，CVPR 2025 pp. 12966–12977）；元数据经 **arXiv abs 页 `citation_*` 4/4 `200`**（arXiv `id_list` 本轮 `429`，如实记）+ OpenAlex 4/4 `200`；PDF 4/4 `200` 但**全部截断**（`pdftotext` 失败）⇒ 数字一律改用 **ar5iv HTML 4/4 `200`**（312,920 / 267,946 / 319,495 / 317,703 B）核对并逐条标注；覆盖轴 = 段级递归与相对位置编码 / 全离散 token 的统一理解生成 / 多解码头投机解码的无损档 / 理解与生成双编码器解耦）。回溯：**第六十九轮 2026-11-19 21:0x 补 4 条 → 264**：Transfusion `2408.11039`（**588**）/ Agentless `2407.01489`（**1,053**，PACM SE Vol. 2 Issue FSE pp. 801–824, 2025）/ Massive Activations `2402.17762`（**444**，**&lt;500 按「方法论常青」收**）/ EDA Corpus `2405.06676`（**38**，**&lt;500 按「本领域权威」收**，IEEE LAD 2024 pp. 1–5）；arXiv `id_list` 4/4 `200` + OpenAlex 4/4 `200`；PDF 2/4 完整（1,384,716 / 453,822 B）、2/4 `content-length` 14,087,563 / 7,636,655 B **>5 MB 未落盘** ⇒ 数字用 **ar5iv HTML 2/2 `200`**（300,229 / 271,351 B）核对。


**本轮快照**：累计 **264** 条（**第六十九轮 2026-11-19 21:0x 补 4 条 → 264**：Transfusion `2408.11039`（**588**）/ Agentless `2407.01489`（**1,053**，PACM SE Vol. 2 Issue FSE pp. 801–824, 2025）/ Massive Activations `2402.17762`（**444**，**&lt;500 按「方法论常青」收**）/ EDA Corpus `2405.06676`（**38**，**&lt;500 按「本领域权威」收**，IEEE LAD 2024 pp. 1–5，DOI `10.1109/lad62341.2024.10691774`）；arXiv `id_list` 4/4 `200` + OpenAlex 4/4 `200`；PDF 2/4 <5 MB **完整可解析**（Agentless 1,384,716 B / EDA Corpus 453,822 B），另 2 篇 `content-length` 14,087,563 / 7,636,655 B **>5 MB 未落盘** ⇒ 数字改用 **ar5iv HTML 2/2 `200`**（300,229 / 271,351 B）+ arXiv 官方摘要核对；覆盖轴 = 图文共用主干的双损失与模态掩码 / 「无 agent 三段流水线」作为 harness 基线 / 巨值激活即隐式 bias（量化与 spike 排查）/ EDA 语料的**可执行判分**）；回溯：**第六十八轮 2026-11-19 18:1x 补 4 条 → 260**：DiT `2212.09748`（**9,393**，ICCV 2023 pp. 4172–4182）/ DeepSeek-Coder `2401.14196`（**2,479**）/ Math-Shepherd `2312.08935`（**1,535**，ACL 2024 pp. 9426–9439）/ MetaGPT `2308.00352`（**2,831**）；arXiv `id_list` 4/4 `200` + OpenAlex 4/4 `200`；PDF 2/4 可下载（1,911,399 / 827,225 B）但**均因截断 `pdftotext` 失败**，另 2 篇 `content-length` 43,824,062 / 16,753,634 B **>5 MB 未落盘** ⇒ 数字全部改用 **ar5iv HTML 4/4 `200`**（288,428 / 324,866 / 156,622 / 502,095 B）+ arXiv 官方摘要核对并逐条标注；覆盖轴 = 前向 Gflops 作为规模尺 / 87-10-3 代码配比与 repository-level 预训练 / 自动过程奖励与逐步 PPO / SOP 驱动的多角色流水线）；**第六十七轮 2026-11-19 15:3x 补 4 条 → 256**：s1 `2501.19393`（**1,939**，EMNLP 2025 pp. 20286–20332）/ Gemma 2 `2408.00118`（**3,891**）/ BLT `2412.09871`（**144**，**&lt;500 按「开创范式」收**）/ TheAgentCompany `2412.14161`（**465**，**&lt;500 按「本领域权威 / 方法论常青」收**）；arXiv `id_list` `200` + OpenAlex 4/4 `200`，PDF **仅 1/4 可解析**（Gemma 2 610,320 B、`%%EOF` 完整），另 3 篇下载截断（1,368,920 / 839,117 / 1,183,809 B，无 `%%EOF`、`pdftotext` 失败）⇒ 数字改用 arXiv 官方摘要与 ar5iv HTML `200`（s1）核对并逐条标注；覆盖轴 = 思考 token 预算与「Wait」续想 / 蒸馏替代 NTP 与局部-全局交错注意力 / 熵切分字节级建模 / 长程数字员工型 agent 评测）；**第六十五轮 2026-11-19 12:0x 补 4 条 → 249**：BART `1910.13461`（**15,049**，ACL 2020 pp. 7871–7880）/ Chameleon `2405.09818`（**1,262**）/ Qwen-VL `2308.12966`（**5,222**）/ RWKV `2305.13048`（**830**）；arXiv abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 完整下载 2/4（296,072 / 1,590,242 B，均 <5 MB）且本地字节 = 远程 `Content-Length`，另 2 篇（25,245,551 / 6,329,953 B）**>5 MB 未落盘** ⇒ 数字改用 **ar5iv HTML 2/2 `200`** 核对并如实标注；覆盖轴 = 去噪目标的五种加噪与 λ=3 / 早期融合的统一 token 词表 / 视觉分辨率与框接口 / 线性注意力的 `O(Td)` 成本）；**第六十四轮 2026-11-19 09:0x 补 4 条 → 245**：ALiBi `2108.12409`（**969**）/ Efficiently Scaling Transformer Inference `2211.05102`（**506**）/ DistServe `2401.09670`（**711**）/ Mooncake `2407.00079`（**345**，<500 按「方法论常青 / 生产系统权威」收）；arXiv abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200` 且本地字节与远程 `Content-Length` 对齐（759,030 / 1,036,959 / 647,352 / 581,962 B）+ `pdftotext` 逐篇核数字；覆盖轴 = 位置外推的加性偏置 / 推理成本的分区解析模型 / prefill–decode 拆分的 goodput 口径 / KVCache 变为调度对象）；**第六十三轮 2026-11-19 06:0x 补 4 条 → 241**：BBH `2210.09261`（**1,433**）/ Speculative Sampling `2302.01318`（**1,424**）/ RULER `2404.06654`（**1,799**）/ Sarathi-Serve `2403.02310`（**539**）；arXiv `id_list` 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`（349,916 / 5,375,941 / 682,955 / 1,945,812 B；BBH >5 MB 仅 `/tmp`）+ `pdftotext` 逐篇核数字；覆盖轴 = 评测形态改变模型排名 / 投机解码保持目标分布 / 长上下文「有效长度」口径 / 服务调度的 chunk 粒度与 TBT）；**第六十二轮 2026-11-19 03:0x 补 3 条 → 237**：OPT `2205.01068`（**5,818**）/ MiniCPM `2404.06395`（**994**）/ DAPO `2503.14476`（**3,544**）；arXiv `id_list` 3/3 `200` + OpenAlex 3/3 `200` + PDF 3/3 `200`（1,765,159 / 15,188,294 / 826,801 B；MiniCPM >5 MB 仅 `/tmp`）+ `pdftotext` 核数字；覆盖轴 = 开放权重 LLM 的失败日志口径 / 小模型 WSD 与过训 token 比 / 可验证奖励 RL 的四个开关）；**第六十一轮 2026-11-19 00:1x 补 3 条 → 234**：AIMv2 `2411.14402`（**147**，**&lt;500 按「方法论常青 / 开源基线」收**）/ Position Interpolation `2306.15595`（**983**）/ DFN `2309.17425`（**273**，**&lt;500 按「方法论常青」收**）；arXiv `id_list` `200` + OpenAlex 3/3 `200` + PDF 3/3 `200`（751,217 / 1,431,519 / 4,788,339 B，均 <5 MB）+ `pdftotext` 核数字；覆盖轴 = 长上下文扩窗的最低成本基线 / 数据过滤器的下游代理口径 / 判别式 vs 生成式视觉塔的路线对照）；**第六十轮 2026-11-18 21:0x 补 4 条 → 231**：Zero Bubble `2401.10241`（**100**，**&lt;500 按「奠基 / 开创范式」收**：同步语义下首个零空泡 PP 调度）/ FP8 Formats `2209.05433`（**593**，NVIDIA 技术报告，E4M3/E5M2 分工）/ SigLIP 2 `2502.14786`（**1,822**，四档尺寸 86M–1B + 109 语言 + NaFlex）/ Pythia `2304.01373`（**761**，ICML 2023，16 模型 × 154 checkpoint、Pile 300B vs 去重 207B）；arXiv `id_list` `200` + atom 4 entry + OpenAlex 4/4 `200` + PDF 4/4 `200`（649,126 / 281,195 / 623,539 / 1,091,147 B，全部 ≤5 MB）+ `pdftotext` 逐篇核数字；覆盖轴 = PP 调度空泡与内存换吞吐 / FP8 格式与 scaling 口径 / 视觉塔四档尺寸与稠密任务配方 / 可复现训练轨迹的评测对照尺）；**第五十九轮 2026-11-18 18:0x 补 3 条 → 227**：DeepSeekMoE `2401.06066`（**1,590**）/ Small-scale proxies `2309.14322`（**139**，**&lt;500 按「方法论常青」收**）/ Mixed Precision Training `1710.03740`（**2,697**，ICLR 2018，会议取自 PDF 页眉）；OpenAlex 3/3 `200` + PDF 3/3 `200`（733,666 / 10,685,777 / 1,404,641 B；10.7 MB 那篇 >5 MB 仅 `/tmp`）+ `pdftotext` 逐篇核数字；覆盖轴 = MoE 专家粒度与两级均衡系数 / 小模型复现大模型 loss spike 的预检协议 / FP16 三件套与 loss-scale 口径）；**第五十八轮 2026-11-18 15:0x 补 2 条 → 224**：OLMoE `2409.02060`（**374**，**&lt;500 按「方法论常青」收**）/ Ring Attention `2310.01889`（**508**，NeurIPS 2023）；OpenAlex 2/2 `200` + PDF 2/2 `200` + `pdftotext` 核数字；覆盖轴 = 全开放 MoE 的「激活参数对齐」消融 / 长上下文的硬件常数 `c` 与 MFU 口径）；**第五十六轮 2026-11-18 09:0x 补 3 条 → 219**：StarCoder 2 `2402.19173`（**1,095**，预印本 TMLR under review）/ Magpie `2406.08464`（**353**，**&lt;500 按「方法论常青」收**）/ Jamba `2403.19887`（**789**，预印本）；OpenAlex 4/4 `200` + PDF 3/3 `200` + `pdftotext` 核数字；⚠️ Magpie/Jamba 的 arXiv `id_list` 本轮 `429`/`000` ⇒ **首次提交日留白**；覆盖轴 = 代码语料可审计构建 + 小模型过训 / 零人工指令自举与过滤 / Transformer-Mamba-MoE 比例与激活参数口径）；**第五十五轮 2026-11-18 06:0x 补 4 条 → 216**：Tülu 3 `2411.15124`（**1,670**，预印本技术报告）/ DSPy `2310.03714`（**1,261**，预印本，仅 v1）/ OpenHands `2407.16741`（**1,050**，ICLR 2025）/ SAM 2 `2408.00714`（**5,632**，预印本技术报告）；arXiv `id_list` `200` + atom 6 entry + OpenAlex 4/4 `200` + PDF 4/4 `200`（8,313,277 / 460,814 / 3,293,124 / 12,709,657 B，两篇 >5 MB 仅 `/tmp`）；覆盖轴 = 后训练三段配方与 RLVR / 指标驱动的 prompt 编译 / 外壳即平台（runtime+事件流）/ 视觉 streaming memory）；**第五十四轮 2026-11-18 03:0x 补 3 条 → 212**：VeriGen `2308.00708`（**533**，ACM TODAES；前身 DATE 2023）/ WebShop `2207.01206`（**1,765**，NeurIPS 2023）/ ChipNeMo `2311.00176`（**472**，预印本技术报告，**&lt;500 按「本领域权威」收**）；arXiv `id_list` `200` + atom 4 entry + OpenAlex 3/3 `200` + PDF 3/3 `200`（2,636,063 / 8,878,628 / 1,135,269 B；WebShop >5 MB 仅 `/tmp`）；覆盖轴 = Verilog 生成的**功能正确性判分** / 长程网页交互的**成功率与人类差距口径** / 工业 EDA 的**领域适配四件套**）；**第五十三轮 2026-11-18 00:0x 补 3 条 → 209**：DCLM `2406.11794`（**627**，NeurIPS 2024 D&B）/ AdamW `1711.05101`（**34,224**，ICLR 2019）/ Prismatic VLMs `2402.07865`（**325**，ICML 2024，**&lt;500 按「方法论常青」收**）；arXiv `id_list` `200` + atom 4 entry + OpenAlex 3/3 `200` + PDF 3/3 `200`（1.66 / 6.06 / 9.72 MB，后两篇 >5MB 仅 `/tmp`）；覆盖轴 = 网页语料过滤与配比基线 / 解耦 weight decay 的源头 / 视觉塔与训练阶段因子化消融；**⚠️ 更正**：VeriGen 真 ID 是 `2308.00708`（非 `2308.00113`，后者为水印论文），但其 PDF 三端点 `000`/`404` ⇒ 不进表）；**第五十二轮 2026-11-17 18:0x 补 4 条 → 206**：GPQA `2311.12022`（**2,204**，预印本）/ MMMU `2311.16502`（**2,994**，CVPR 2024 Oral）/ LAION-5B `2210.08402`（**1,963**，NeurIPS 2022 D&B）/ MATH `2103.03874`（**7,734**，NeurIPS 2021）；arXiv `id_list` `200` + atom 4 entry + OpenAlex 4/4 `200` + PDF 4/4 `200`（0.62 / 16.87 / 17.69 / 2.03 MB，后两篇 >5MB 仅 `/tmp`）；覆盖轴 = 抗检索难题口径 / 多模态判分与图表读图 / 图文对 CLIP 过滤阈值 / 数学判分与难度分层；**第五十一轮 2026-11-17 12:0x 补 4 条 → 202**：InternVL `2312.14238`（**3,950**，CVPR 2024）/ Phi-3 `2404.14219`（**3,285**，预印本）/ FineWeb `2406.17557`（**1,799**，NeurIPS 2024 D&B）/ OLMo `2402.00838`（**908**，ACL 2024）；arXiv abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`（1.32 / 3.91 / 3.14 / 0.56 MB，均 <5MB，不入 git）；覆盖轴 = 视觉塔放大与像素重排 / 小模型数据配方 / 网页语料消融 / 全开放训练栈；**第五十轮 2026-11-17 09:0x 补 4 条 → 198**：Qwen2.5 `2412.15115`（**11,888**，预印本技术报告）/ Gemma `2403.08295`（**3,803**，预印本技术报告）/ Diffusion Policy `2303.04137`（**2,313**，RSS 2023，DOI `10.15607/RSS.2023.XIX.026`）/ Open X-Embodiment `2310.08864`（**1,045**，预印本技术报告）；arXiv abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`（Diffusion Policy 6,192,199 B >5MB 仅 `/tmp`）；覆盖轴 = 小模型数据过滤与上下文课程 / 按规模分叉的架构与词表 / 动作 chunk 与 receding horizon / 跨本体混配与技能标签；**第四十九轮 2026-11-17 06:0x 补 4 条 → 194**：The Stack `2211.15533`（**553**，预印本）/ Code Llama `2308.12950`（**4,881**，预印本）/ Qwen2-VL `2409.12191`（**6,157**，预印本）/ LiveCodeBench `2403.07974`（**1,802**，预印本）；arXiv `id_list` `200` + atom（12,622 B / 4 entry）+ OpenAlex 4/4 `200` + PDF 4/4 `200`（Qwen2-VL 35,936,325 B >5MB 仅 `/tmp`，其余 3 篇 <5MB）；覆盖轴 = 代码语料许可 / 代码专化与 FIM / 动态分辨率视觉塔 / 免污染时间切窗评测；**第四十八轮 2026-11-17 03:0x 补 4 条 → 190**：Judging LLM-as-a-Judge（MT-Bench / Chatbot Arena）`2306.05685`（**5,326**，NeurIPS 2023 D&B）/ Self-Rewarding LMs `2401.10020`（**664**，ICML 2024）/ TinyStories `2305.07759`（**589**，预印本 MSR）/ Mind2Web `2306.06070`（**503**，NeurIPS 2023 Spotlight）；arXiv `id_list` `200` + atom（11,227 B / 4 entry）+ OpenAlex 4/4 `200` + PDF 4/4 `200`（3 篇 <5MB；Mind2Web 7,635,816 B >5MB 仅 /tmp）；**第四十七轮 2026-11-17 00:0x 补 4 条 → 186**：AlphaCode `2203.07814`（**1,787**，Science 2022，OpenAlex DOI `10.1126/science.abq1158`）/ BLOOM `2211.05100`（**2,860**，预印本技术报告）/ StarCoder `2305.06161`（**1,518**，预印本技术报告）/ HH-RLHF `2204.05862`（**5,138**，预印本技术报告）；四篇 PDF 均 `200` + `%PDF-` 且 <5MB（3,797,220 / 3,029,243 / 1,174,499 / 9,503,688 B），`pdftotext` 逐篇核到关键数字）；**第四十六轮 2026-11-16 21:0x 补 4 条 → 182**：LIMA `2305.11206`（**904**，NeurIPS 2023）/ The False Promise of Imitating Proprietary LLMs `2305.15717`（**304**，ICLR 2024 spotlight，**&lt;500 按「方法论常青」收**）/ Muon is Scalable for LLM Training `2502.16982`（**622**，预印本）/ FlashAttention-3 `2407.08608`（**418**，NeurIPS 2024，**&lt;500 按「开创范式 + 方法论常青」收**）；**第四十五轮 2026-11-16 18:0x 补 4 条 → 178**：LAMB `1904.00962`（**932**，ICLR 2020）/ Layer Normalization `1607.06450`（**12,853**，预印本）/ StreamingLLM `2309.17453`（**1,248**，ICLR 2024）/ Nucleus Sampling `1904.09751`（**2,832**，ICLR 2020）；**第四十四轮 2026-11-16 15:0x 补 4 条**：Swin `2103.14030`（**38,712**，ICCV 2021）/ SpeechT5 `2110.07205`（**141**，ACL 2022，**&lt;500 按「开创统一模态范式」收**）/ GPipe `1811.06965`（**1,280**，NeurIPS 2019）/ Scaling Data-Constrained `2305.16264`（**254**，NeurIPS 2023，**&lt;500 按「方法论常青」收**）；**第四十三轮 2026-11-16 12:0x 补 4 条**：Gemini 1.5 `2403.05530`（**4,633**，预印本）/ RTLLM `2308.05345`（**301**，ASP-DAC 2024，<500 按「本领域权威」）/ VerilogEval `2309.07544`（**359**，ICCAD 2023 Invited，<500 按「本领域权威」）/ PIM Benchmarking `2105.03814`（**285**，IEEE Access 2022，<500 按「本领域权威」）；**第四十二轮 2026-11-16 09:0x 补 5 条 → 166**：GShard `2006.16668`（1,633）/ Mixtral `2401.04088`（4,372）/ Self-RAG `2310.11511`（1,091）/ LongBench `2308.14508`（1,169，ACL 2024）/ Cambrian-1 `2406.16860`（514，NeurIPS 2024 Oral）；**第三十八轮 2026-11-15 21:0x 补 4 条**：HuBERT `2106.07447`（**3,561**，TASLP，会场取自 OpenAlex）/ Tensor Programs V（μP）`2203.03466`（**302**，NeurIPS 2021，⚠️ <500 按「开创范式」收）/ Training Verifiers（GSM8K）`2110.14168`（**11,462**，预印本）/ Emergent Abilities `2206.07682`（**4,208**，TMLR 2022）；**第三十七轮 2026-11-15 18:0x 补 4 条**：wav2vec 2.0 `2006.11477`（**3,140**）/ Multi-Query Attention `1911.02150`（**872**）/ BitNet b1.58 `2402.17764`（**496**，`Work in progress` 预印本）/ Reward Model Overoptimization `2210.10760`（**291**）；**第三十六轮 2026-11-15 15:0x 补 4 条**：Whisper `2212.04356`（**3,720**）/ Gato `2205.06175`（**876**，TMLR 2022）/ SGLang `2312.07104`（**812**，NeurIPS 2024）/ Self-Consistency `2203.11171`（**5,587**，ICLR 2023）；**第三十五轮 2026-11-15 12:0x 补 4 条**：Qwen Technical Report `2309.16609`（**6,006**）/ PaLM `2204.02311`（**5,425**）/ RETRO `2112.04426`（**697**）/ AWQ `2306.00978`（**831**，MLSys 2024 Best Paper）；**第三十四轮 2026-11-15 09:0x 补 4 条**：MemGPT `2310.08560`（1,909）/ Generative Agents `2304.03442`（4,325，UIST 2023）/ Self-Refine `2303.17651`（2,464，NeurIPS 2023）/ Mamba `2312.00752`（7,633）；**第三十三轮 2026-11-15 06:0x 补 3 条**：ToolLLM `2307.16789`（**1,490**，2023 预印本）/ Voyager `2305.16291`（**2,787**，2023 预印本）/ HuggingGPT `2303.17580`（**1,219**，NeurIPS 2023）；**第三十二轮 2026-11-15 03:0x 补 3 条**：AgentBench `2308.03688`（**1,427**，ICLR 2024，会议取自 arXiv `comment`）/ Constitutional AI `2212.08073`（**5,135**）/ BLIP-2 `2301.12597`（**3,197**）；**第三十一轮 2026-11-15 00:0x 补 4 条**：Codex / HumanEval `2107.03374`（**12,170**，2021 预印本）/ HELM `2211.09110`（**2,295**，TMLR 2023）/ The Pile `2101.00027`（**3,021**，2020 预印本）/ FLAN `2109.01652`（**3,471**，2021 预印本）；**第三十轮 2026-11-14 22:3x 补 4 条**：GPT-4 `2303.08774`（38,329）/ Roofline（CACM 52(4):65–76，2,165）/ SigLIP `2303.15343`（1,884，ICCV'23）/ 训练集去重 `2107.06499`（ACL 2022，226）；**第二十九轮 2026-11-14 15:0x 补 4 条**：phi-1 `2306.11644`（**1,104**，2023，预印本）/ OSWorld `2404.07972`（**686**，NeurIPS 2024，pp. 52040–52094）/ ML for EDA Survey `2102.03357`（**388**，TODAES 26(5):1–46）/ A Modern Primer on PIM `2012.03112`（**92**，2020，综述）；**第二十八轮 2026-11-14 12:0x 补 4 条**：Genie `2402.15391` / Hitting the Memory Wall（1995） / Deep Learning（Nature 2015） / AlexNet（CACM 2017）；首轮 11:5x 收 4 条；第二轮 11:4x 补 4 条 EDA / agent / PEFT；第三轮 12:1x 补 4 条 RoPE / SWE-bench / Reflexion / CoT；第四轮 12:4x 补 3 条 GPT-3 / InstructGPT / LLaMA；第五轮 15:0x 补 4 条 ResNet / seq2seq / Dyna / LLaVA；第六轮 18:0x 补 4 条 GPT-1 / GPT-2 / Kaplan scaling laws / DQN；第七轮 21:0x 补 4 条 AlphaGo / AlphaGo Zero / Gemini / OpenVLA；第八轮 2026-11-12 00:0x 补 4 条 AlphaFold / AlphaStar / Kimi k1.5 / π0；第九轮 2026-11-12 03:0x 补 4 条 GLM-4 / MiniMax-01 / RT-2 / Octo；**第十轮 2026-11-12 06:0x 补 4 条** SWE-agent / Tree of Thoughts / Llama 2 / LLaVA-1.5；**第十一轮 2026-11-12 09:0x 补 4 条** Llama 3 / RT-1 / Christiano 2017 / Stiennon 2020；**第十二轮 2026-11-12 12:0x 补 4 条** τ-bench / TD-Gammon / Sora 技术报告 / Kimi K2；**第十三轮 2026-11-12 15:0x 补 4 条** DPO / Mamba-2(SSD) / FlashAttention-2 / Ramulator 2.0；**第十四轮 2026-11-12 18:0x 补 4 条** SimPO / Zephyr / CircuitNet / Sutton《The Bitter Lesson》（博客，单列非论文条目）；**第十六轮 2026-11-13 00:0x 补 4 条** KTO `2402.01306` / H₂O `2306.14048` / Self-Instruct `2212.10560` / Switch Transformer `2101.03961`；**第十七轮 2026-11-13 03:0x 补 4 条** Chip Placement（AlphaChip 预印本 `2004.10746`）/ YaRN `2309.00071` / Speculative Decoding `2211.17192` / GPTQ `2210.17323`；**第十八轮 2026-11-13 06:0x 补 4 条** Toward an Open-Source Digital Flow（OpenROAD, DAC 2019）/ LongRoPE `2402.13753` / Ramulator（IEEE CAL 2015）/ RowHammer（ISCA 2014）；**第十九轮 2026-11-13 09:0x 补 4 条** Megatron-LM `1909.08053` / DeepSeek-V3 `2412.19437` / GAIA `2311.12983` / A Case for Intelligent RAM（IEEE Micro 1997，无 arXiv）；**第二十轮 2026-11-13 12:0x 补 4 条** BERT `1810.04805` / CLIP `2103.00020` / DeepSeek-R1 `2501.12948` / DRAMsim3（IEEE CAL 2020，无 arXiv）；**第二十一轮 2026-11-13 15:0x 补 4 条** QLoRA `2305.14314` / T5 `1910.10683` / RAG `2005.11401` / Toolformer `2302.04761`；**第二十二轮 2026-11-13 18:0x 补 4 条** Distilling the Knowledge `1503.02531` / GQA `2305.13245` / Orca `2306.02707` / Mistral 7B `2310.06825`；**第二十三轮 2026-11-13 21:0x 补 4 条** ViT `2010.11929` / DINOv2 `2304.07193` / WebArena `2307.13854` / TPU ISCA 2017 `1704.04760`；**第二十四轮 2026-11-14 00:0x 补 4 条** PPO `1707.06347`（31,326）/ DDPM `2006.11239`（11,034）/ ZeRO `1910.02054`（1,432，SC 2020）/ SAM `2304.02643`（16,904，ICCV 2023）；**第二十五轮 2026-11-14 03:0x 补 4 条** DeepSeekMath / GRPO `2402.03300`（11,153）/ MAE `2111.06377`（10,217，CVPR 2022）/ S4 `2111.00396`（2,741，ICLR 2022 Outstanding HM）/ DreamerV3 `2301.04104`（1,962，Nature 2025）；**第二十六轮 2026-11-14 06:0x 补 4 条** Adam `1412.6980`（101,807，ICLR 2015）/ Batch Normalization `1502.03167`（34,937，ICML 2015 PMLR 37:448–456）/ GAN `1406.2661`（9,668 预印本记录，NeurIPS 2014）/ DREAMPlace（DAC 2019，177；TCAD 版 205，**无 arXiv**）；**第二十七轮 2026-11-14 09:0x 补 4 条** Latent Diffusion `2112.10752`（**20,670**，CVPR 2022；⚠️ 候选池旧 ID `2207.11240` 实为 Discrete Key-Value Bottleneck ⇒ 已更正）/ MuZero `1911.08265`（Nature 2020 588:604–609，**2,075**）/ AutoDMP（ISPD 2023，**67**，无 arXiv）/ DREAM-GAN（ISPD 2023，**16**，无 arXiv））｜ 覆盖（一篇可服务多线，按文内「与我们工作的关系」逐条计数）：pretrain **104** · vision **47** · harness **117** · data **110** · zhulong **119** · designflow **49**

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


> 🆕 **第十七轮（2026-11-13 03:0x）新增 4 条 = 「布局 RL 原点 + 长上下文扩展 + 解码加速 + 后训练量化」**：Chip Placement / AlphaChip（把布局写成 RL + 学一个奖励预测器当编码器 → designflow 的布局基线题、zhulong 的「代理模型只排序、真值归工具」）→ YaRN（少 10× token、2.5× 步数扩展上下文 → pretrain 长上下文的第一条低成本基线）→ Speculative Decoding（草稿 + 并行验证，输出分布不变，T5-XXL 2×–3×）→ GPTQ（175B 4 GPU 小时量化到 3–4 bit，单卡推理；2B 化后直接服务端侧/部署成本）。**必读清单：仍 10/10 组、37/37 条目全覆盖**（本轮属「补充」，且首次系统补上 **serving 侧（解码 / 量化）** 这条此前没有落点的线）。
>
> **第十七轮核验证据（可复核）**：arXiv API `id_list=2611.13925,2611.13543,2004.10746,2309.00071,2211.17192,2210.17323` → **`200` + `application/atom+xml; charset=utf-8`**（15,717 B / 6 条 entry）；被引数 **OpenAlex 4/4 `200`**（Chip Placement arXiv 版 **274** · YaRN **591** · Spec-Dec **354**⚠️ · GPTQ **2,195**，查询日 2026-11-13），另经 OpenAlex 精确标题检索核到 **Nature 版** `A graph placement methodology for fast chip design`（DOI `10.1038/s41586-021-03544-w`，**704**，2021）。⚠️ Spec-Dec **354 &lt; 500**、Chip Placement 预印本 **274 &lt; 500** ⇒ 均按「奠基」收录并显式标注；🚫 不把两个口径混算。

> 🆕 **第二十一轮（2026-11-13 15:0x）新增 4 条 = 「小团队可落地的四条底座」**：QLoRA（4-bit 基座 + LoRA，65B 单卡 48GB 微调、Guanaco 24h 单卡）→ pretrain 的单卡 SFT 配方 / zhulong 的显存-时间记账；T5（一切任务写成 text-to-text，系统对比目标 × 架构 × 数据）→ harness 的统一评分接口 / data 的 C4 清洗对照 / pretrain 的 encoder-decoder 对照轴；RAG（参数化 + 非参数化记忆）→ harness 的「不改模型即可换知识」通道 / zhulong 的索引-延迟成本；Toolformer（自监督学会调 API）→ harness 的工具能力后训练注入 / data 的调用数据过滤准则。**必读清单：仍 10/10 组、37/37 条目全覆盖**（本轮属「补充」，且首次把「**检索**」与「**工具调用数据自举**」两条独立线补上）。
>
> **第二十一轮核验证据（可复核）**：arXiv API `id_list=2305.14314,1910.10683,2005.11401,2302.04761` → **`200` + `application/atom+xml; charset=utf-8`**（10,900 B / 4 条 entry；作者数与首发时间已核）；被引数 **OpenAlex 4/4 `200`**（QLoRA **4,052** · T5 **13,437** · RAG **6,188** · Toolformer **3,245**，查询日 2026-11-13）。会场：QLoRA / Toolformer = NeurIPS 2023（OpenAlex `conference-paper` + pp. 已核）；T5 = OpenAlex `biblio` 记 JMLR **21(140):1–67** 但 `type=preprint` ⇒ **如实并列、不混算**；RAG = 仅 arXiv `comment` 写 `Accepted at NeurIPS 2020`、OpenAlex 无会场 DOI ⇒ **不写 DOI**。

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

## 52. SimPO: Simple Preference Optimization with a Reference-Free Reward

| 字段 | 内容 |
|:--|:--|
| 标题 | SimPO: Simple Preference Optimization with a Reference-Free Reward |
| 作者（前 3） | Yu Meng · Mengzhou Xia · **Danqi Chen**（共 3 位） |
| 年份 | 2024（arXiv 首次提交 **2024-05-23**；本线取到 **v3 / 2024-11-01**） |
| 会议 / 期刊 | **NeurIPS 2024**（arXiv `comment` 原文含 `NeurIPS 2024`；OpenAlex `type=conference-paper`，会议 DOI `10.52202/079017-3946`，页码 **124198–124235**） |
| 被引数 | **560**（OpenAlex，DOI `10.48550/arxiv.2405.14734`，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2405.14734> ｜ 会议 DOI `10.52202/079017-3946` ｜ 代码 <https://github.com/princeton-nlp/SimPO> |
| 一句话贡献 | 摘要原文：把**序列的平均对数概率**当作隐式奖励（与生成时的打分口径一致），从而**不需要参考模型**、更省显存与算力；同时在 Bradley–Terry 目标中加入**目标奖励边际（target reward margin）**以拉开正负样本间距，作者自报在多种设置下优于 DPO 及其变体。 |
| 与我们工作的关系 | **zhulong（奖励设计，直接影响）**：我们当前在 ~2B 规模上纠结「要不要保留参考模型」；SimPO 给出了一条**去参考模型**的路径，代价是奖励变成「平均对数概率」⇒ 长度效应被显式引入。<b>动作</b>：zhulong 的奖励消融固定三臂 —— `DPO（带参考）` / `SimPO（无参考 + γ）` / `SimPO 去 γ`，<b>预注册判据</b>：若 SimPO 三臂中「平均回答长度」与「判定正确率」的相关系数 **&gt;0.5**，则必须加长度归一或长度惩罚后重跑，否则不采信其胜出。<br>**data（偏好数据）**：γ 与 β 一起决定「多接近才算赢」，直接影响标注粒度需求 ⇒ data 线的偏好对采集表要同时记录 `长度差` 与 `胜负有无可验证依据`。<br>**harness**：评测必须报**平均输出长度**，否则「胜出」可能只是更长。<b>风险</b>：① 作者自报、本线未复现；② 摘要未给具体胜率数字 ⇒ 本文不引用任何「提升 X%」；③ 我们面对的是工具调用轨迹（长尾、含报错文本），与摘要任务分布差异大，结论不能直接搬。 |

首次收录: 2026-11-12（第十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 会议 DOI / 页码）

---

## 53. Zephyr: Direct Distillation of LM Alignment

| 字段 | 内容 |
|:--|:--|
| 标题 | Zephyr: Direct Distillation of LM Alignment |
| 作者（前 3） | Lewis Tunstall · Edward Beeching · **Nathan Lambert**（et al.，共 14 位） |
| 年份 | 2023（arXiv 首次提交 **2023-10-25**，仅 v1） |
| 会议 / 期刊 | **预印本**（arXiv；OpenAlex `type=preprint`，本轮**未核到会议 DOI**） |
| 被引数 | **867**（OpenAlex，DOI `10.48550/arxiv.2310.16944`，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2310.16944> |
| 一句话贡献 | 摘要原文：先做**蒸馏式 SFT（dSFT）**，再用**AI 反馈排序出的偏好数据**做**蒸馏式 DPO（dDPO）**，得到 Zephyr-7B；作者自报其在 7B 级 chat 基准上为当时最好，**无需人工标注**，且微调**只需数小时、无需额外采样**。 |
| 与我们工作的关系 | **pretrain / posttrain（后训练配方）**：这是「**AI 反馈替代人工标注**」这条线的代表作 ⇒ 对我们最实际的问题是「域内偏好对只有几万条时，教师排序 + DPO 是否仍优于纯 SFT」。<b>动作</b>：posttrain 在 ~2B 上做**四臂对照**：`dSFT only` / `dSFT+dDPO(AI 反馈)` / `dSFT+DPO(checker 偏好)` / `dSFT+dDPO 但教师换成我们自己的 7B`，<b>判据</b>：以 harness 的「工具调用一次成功率」为主指标，若 checker 偏好臂不劣于 AI 反馈臂，则**优先 checker**（可自动化、无标注成本）。<br>**data（偏好数据来源）**：AI 反馈 = 可放大但会继承教师偏好；checker = 精确但覆盖窄 ⇒ data 线需要一张「哪些任务可 checker 化」的清单。<br>**zhulong（消融归因）**：Zephyr 的增益同时来自教师数据与 DPO 步，任何引用它的消融都必须把两者拆开。<b>风险</b>：① 7B 结果不外推到 2B；② 全文数字本线未复现，不引用具体分数；③ 「无需人工标注」不等于「无需人工设计教师与筛选」。 |

首次收录: 2026-11-12（第十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`；会议=未核到）

---

## 54. CircuitNet: An Open-Source Dataset for Machine Learning Applications in Electronic Design Automation (EDA)

| 字段 | 内容 |
|:--|:--|
| 标题 | CircuitNet: An Open-Source Dataset for Machine Learning Applications in Electronic Design Automation (EDA) |
| 作者（前 3） | Zhuomin Chai · Yuxiang Zhao · **Yibo Lin**（共 6 位：+ Wei Liu · Runsheng Wang · Ru Huang） |
| 年份 | 2022（arXiv 首次提交 **2022-08-01**；本线取到 **v4 / 2022-09-01**） |
| 会议 / 期刊 | **Science China Information Sciences** 65(**12**)，DOI `10.1007/s11432-022-3571-8`（OpenAlex `type=other`，2026-11-12 实测） |
| 被引数 | **44**（OpenAlex，上述期刊 DOI，查询日 **2026-11-12**；S2 未查）<br>⚠️ **远低于 §1「被引 ≥500」门槛**，按判据 ④「本领域（EDA / LLM-for-EDA）标志性工作」收录 —— 摘要自称 **the first open-source dataset** for ML in VLSI CAD，是本领域少数公开可下载的设计-指标数据集。 |
| arXiv / DOI | <https://arxiv.org/abs/2208.01040> ｜ 期刊 DOI `10.1007/s11432-022-3571-8` |
| 一句话贡献 | 摘要原文：指出 EDA 社区做跨阶段预测时**普遍缺大规模公开数据**、多数研究只能用自建小数据集验证，因此给出**首个开源数据集**（CircuitNet），用于 VLSI CAD 中的机器学习任务。 |
| 与我们工作的关系 | **data（EDA 语料 / 切分纪律，直接可用）**：公开数据集的价值不只在于「有数据」，而在于**给了可比较的切分口径**。<b>动作</b>：data 线在建 BaiZe 的 EDA 语料时，把「**按设计切分而非按样本切分**」写成硬规则（同一设计的不同采样点不得跨 train/test），并用 CircuitNet 做一次泄漏对照实验，<b>判据</b>：按设计切分后指标若下降 &gt;20%，说明此前的随机切分确实在泄漏。<br>**designflow（造题 / 保真度）**：它把「设计 → 预测指标」做成标准任务 ⇒ designflow 的 L1–L2 题面可直接对齐这类任务形态（读设计特征、预测某项指标），L3+ 才引入工具闭环。<br>**zhulong（代理模型）**：若要把「LLM 出配置 → 工具跑 → 回填」闭环压到可承受成本，代理模型必须先在公开数据上标定误差。<b>风险</b>：① 被引 44 未达门槛，收录属「领域标志性」判断（我们的观察）；② 摘要未给数据规模 / 工艺节点 / 指标清单 ⇒ 本文只写摘要出现的内容，具体类别（IR-drop / DRC / 拥塞）属**领域常识**，未在本文摘要中出现，引用时须另行核验；③ 与我们 CXMT 内部设计数据无任何对接验证。 |

首次收录: 2026-11-12（第十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 期刊 DOI）

---

## 55. The Bitter Lesson（**非论文条目 · 博客随笔**，单列）

> ⚠️ 本条**不是论文**：无 arXiv、无 DOI、无被引口径。按用户令里「必读基线」的候选清单收录（Sutton 一系），**单独标注类型**，不混入论文计数口径的引用场景。

| 字段 | 内容 |
|:--|:--|
| 标题 | The Bitter Lesson |
| 作者 | **Richard S. Sutton**（单作者） |
| 年份 | **2019-03-13**（页面原文日期；`HTTP 200` / 7,297 B，2026-11-12 18:0x 实测） |
| 会议 / 期刊 | 无（个人主页随笔；`incompleteideas.net`） |
| 被引数 | **未查**（博客无被引口径；🚫 不写任何估算值） |
| 链接 | <http://www.incompleteideas.net/IncIdeas/BitterLesson.html> |
| 一句话贡献 | 原文首句逐字：`The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin.`；随后论证：多数 AI 研究假设算力恒定、转而注入人类领域知识，但长期只有「利用算力」有效，且**两者在实践中往往相互挤占**。 |
| 与我们工作的关系 | **pretrain（战略口径，不是技术细节）**：这篇是「**通用方法 + 算力** 长期胜出」最常被引的表述，直接对上我们「2B 领域模型 + 领域先验」的取舍 —— 它提醒：领域知识的注入是**短期收益**，长期会被通用方法吃掉。<b>动作</b>：pretrain 在写「为什么要做领域继续预训练」的立项依据时，必须同时给出**通用基线**（同 token 预算的通用语料）作为对照，<b>判据</b>：若领域语料带来的增益在 &lt;2× token 预算内被通用基线追平，则该领域配比按「战术性」而非「战略性」投入。<br>**designflow（造题倾向）**：提示我们少造「靠人肉先验可解」的题，多造「必须调用工具、可规模化验证」的题。<b>风险</b>：① 是**观点文**不是实验证据，🚫 不能当作「已验证结论」引用；② 常被断章取义成「数据无用 / 领域知识无用」，原文明确说两者「need not run counter」，引用须带上下文；③ 无被引数、无同行评审。 |

首次收录: 2026-11-12（第十四轮）｜ 状态: 原文已实测（`HTTP 200` / 7,297 B；首句逐字核对）｜ 类型: **blog（非论文）**

---

## 56. ORPO: Monolithic Preference Optimization without Reference Model

| 字段 | 内容 |
|:--|:--|
| 标题 | ORPO: Monolithic Preference Optimization without Reference Model |
| 作者（前 3） | **Jiwoo Hong** · **Noah Lee** · **James Thorne**（共 3 位） |
| 年份 | 2024（arXiv 首次提交 **2024-03-12**；本线取到 **v2 / 2024-03-14**） |
| 会议 / 期刊 | **EMNLP 2024**（OpenAlex `type=conference-paper`，DOI `10.18653/v1/2024.emnlp-main.626`） |
| 被引数 | **586**（OpenAlex，查询日 **2026-11-12**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2403.07691> ｜ 会议 DOI `10.18653/v1/2024.emnlp-main.626` |
| 一句话贡献 | 摘要原文要点：论文先论证 **SFT 在偏好对齐中不可省**，且「对不受欢迎的生成风格施加**轻微惩罚**」就足以得到偏好对齐的 SFT；据此提出**无参考模型**的**单体 odds ratio 偏好优化（ORPO）**，把指令微调与偏好对齐合并成**一个阶段**，从而**省掉额外的偏好对齐阶段**。 |
| 与我们工作的关系 | **posttrain（后训练配方，直接影响）**：我们 ~2B 的后训练现在是「SFT → DPO」两段式，显存与流程成本都压在参考模型上。ORPO 提供「**一个阶段、不要参考模型**」的替代。<b>动作</b>：posttrain 跑三臂对照 —— `SFT→DPO(带参考)` / `ORPO 单阶段` / `SFT→SimPO`，同一份域内偏好对、同一 token 预算，<b>判据</b>：以 harness「工具调用一次成功率」为主指标，ORPO 臂若不劣于 DPO 臂且节省 ≥1 次全参前向，则纳入候选配方。<br>**zhulong（奖励设计）**：ORPO 的奖励本质是「**SFT 对数似然 + λ·odds ratio**」两项之和 ⇒ 消融必须把 λ 单列，否则无法区分「去参考模型」与「多了一个 SFT 项」各自的贡献。<br>**data（偏好数据）**：单体目标意味着**偏好对与 SFT 语料同时进入一个 loss** ⇒ data 线要记录「每条偏好对是否也有对应的 chosen-only SFT 样本」，否则无法复现。<b>风险</b>：① 作者自报，本线未复现；② 摘要未给具体胜率数字 ⇒ 本文不引用任何「提升 X%」；③ 我们的偏好对来自**工具轨迹**（含报错文本、长度长尾），与论文的对话/摘要分布差异大，λ 的最优值不可直接搬。 |

首次收录: 2026-11-12（第十五轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 会议 DOI）

---

## 57. A General Theoretical Paradigm to Understand Learning from Human Preferences（IPO）

| 字段 | 内容 |
|:--|:--|
| 标题 | A General Theoretical Paradigm to Understand Learning from Human Preferences |
| 作者（前 3） | **Mohammad Gheshlaghi Azar** · **Mark Rowland** · **Bilal Piot**（et al.，共 7 位：+ Daniel Guo · Daniele Calandriello · Michal Valko · Rémi Munos；全部 Google DeepMind） |
| 年份 | 2023（arXiv 首次提交 **2023-10-18**；本线取到 **v2 / 2023-11-22**） |
| 会议 / 期刊 | **预印本**（arXiv；OpenAlex `type=preprint`，本轮**未核到会议 DOI**） |
| 被引数 | **285**（OpenAlex，DOI `10.48550/arxiv.2310.12036`，查询日 **2026-11-12**；S2 未查）<br>⚠️ **低于 §1「被引 ≥500」门槛**，按判据 ②「**奠基**（偏好优化的理论范式）」收录 —— 它把 DPO 的隐含假设摆到台面上并给出带正则的替代目标（IPO），是后续大量偏好优化工作的理论参照。 |
| arXiv / DOI | <https://arxiv.org/abs/2310.12036> ｜ arXiv DOI `10.48550/arxiv.2310.12036` |
| 一句话贡献 | 摘要原文要点：RLHF 依赖**两个近似** —— ① 把**成对偏好**换成**逐点奖励**，② 假设奖励模型能从收集数据泛化到策略采样的分布外数据；DPO 绕过了 ②，但**仍重度依赖 ①**。本文给出更一般的理论范式来理解「从人类偏好学习」，并据此提出对 ① 的替代（IPO）。 |
| 与我们工作的关系 | **zhulong（奖励设计 / 消融归因，强相关）**：我们做偏好优化时最容易被忽略的正是 ① —— 把「A 比 B 好」硬当成两个独立分数。<b>动作</b>：zhulong 在写消融结论时必须显式声明「本实验是否假设了逐点奖励可替代成对偏好」，并把 IPO 作为**对照目标**加入（DPO / IPO / SimPO 三目标同数据同预算），<b>判据</b>：若在**高度 off-policy** 的离线偏好数据上 IPO 与 DPO 的胜率差 &lt;1 个标准差，则结论只能写「在该数据量下目标选择不敏感」，🚫 不许写「DPO 更好」。<br>**data（偏好数据）**：理论指出「偏好数据覆盖不足 ⇒ ① 不成立」 ⇒ data 线的偏好对采集必须报**覆盖度**（同一任务上出现过的对比对数），而非只报总条数。<br>**harness（评测口径）**：需要能区分「策略偏离偏好数据分布」的指标（如 chosen 似然与策略似然的偏移）。<b>风险</b>：① 是**理论 + 小规模实验**的论文，工程收益不保证；② 被引 285 未达门槛，收录属「奠基」判断（我们的观察）；③ 引用的摘要为 arXiv 摘要全文要点，公式与定理细节本线未逐条核对，引用具体定理前须回原文。 |

首次收录: 2026-11-12（第十五轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`；会议=未核到）

---

## 58. Lost in the Middle: How Language Models Use Long Contexts

| 字段 | 内容 |
|:--|:--|
| 标题 | Lost in the Middle: How Language Models Use Long Contexts |
| 作者（前 3） | **Nelson F. Liu** · **Kevin Lin** · **John Hewitt**（et al.，共 7 位：+ Ashwin Paranjape · Michele Bevilacqua · Fabio Petroni · Percy Liang） |
| 年份 | 2023（arXiv 首次提交 **2023-07-06**；本线取到 **v3 / 2023-11-20**） |
| 会议 / 期刊 | **TACL 2024**（arXiv `comment` 原文：`Accepted for publication in Transactions of the Association for Computational Linguistics (TACL), 2023`；OpenAlex DOI `10.1162/tacl_a_00638`） |
| 被引数 | **3,578**（OpenAlex，上述期刊 DOI，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2307.03172> ｜ 期刊 DOI `10.1162/tacl_a_00638` |
| 一句话贡献 | 摘要原文要点：用**多文档问答**与**键值检索**两个「必须在输入里找到相关信息」的任务评测长上下文能力，发现**只改变相关信息的位置就能让性能显著下降** ⇒ 现有模型并未稳健地利用长输入；性能**通常在相关信息位于开头或结尾时最高**，在**中部显著下降**。 |
| 与我们工作的关系 | **pretrain（长上下文配比 / 位置鲁棒性，直接影响）**：我们的 EDA 场景天然是「长日志 + 关键一行在中间」，这篇是**必须先跑满的基线**。<b>动作</b>：pretrain 在做长上下文扩展前，先做一个**位置扫描**实验（把关键证据分别放在 0% / 25% / 50% / 75% / 100% 位置），<b>判据</b>：若 50% 位置的指标比两端低 &gt;15%，则长上下文扩展的优先级高于继续加训练 token。<br>**harness（判分与上下文编排，直接影响）**：评测题要把「证据位置」作为**自变量**记录进元数据，否则「长上下文变强」可能只是「证据恰好在前部」。<br>**designflow（造题）**：L3+ 题面应显式设计「**证据埋在长日志中部**」的变体，用来区分「会调工具」与「会找证据」。<br>**vision（间接）**：多图 / 长文档视觉输入同样存在位置效应，可作为图像序列顺序消融的参照。<b>风险</b>：① 实验对象是**自然语言**多文档 QA / 键值检索，我们是**结构化日志与报错文本**，U 形是否同样成立需自测（已在请教信里向一作提问）；② 结论针对 2023 年模型，新模型的绝对差距可能缩小，🚫 不能写成「所有模型都只擅长首尾」。 |

首次收录: 2026-11-12（第十五轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 期刊 DOI）

---

## 59. Efficient Memory Management for Large Language Model Serving with PagedAttention（vLLM）

| 字段 | 内容 |
|:--|:--|
| 标题 | Efficient Memory Management for Large Language Model Serving with PagedAttention |
| 作者（前 3） | **Woosuk Kwon** · **Zhuohan Li** · **Siyuan Zhuang**（et al.，共 9 位：+ Ying Sheng · Lianmin Zheng · Cody Hao Yu · Joseph E. Gonzalez · Hao Zhang · Ion Stoica） |
| 年份 | 2023（arXiv 首次提交 **2023-09-12**，仅 v1） |
| 会议 / 期刊 | **SOSP 2023**（arXiv `comment` 原文 `SOSP 2023`；OpenAlex `type=conference-paper`，DOI `10.1145/3600006.3613165`） |
| 被引数 | **3,869**（OpenAlex，上述 DOI，查询日 **2026-11-12**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2309.06180> ｜ 会议 DOI `10.1145/3600006.3613165` |
| 一句话贡献 | 摘要原文要点：高吞吐服务需要足够大的 batch，但每个请求的 **KV cache 巨大且动态伸缩**，管理不当会被**碎片与重复**严重浪费；作者提出受操作系统**虚拟内存 / 分页**启发的 **PagedAttention**，并在其上构建 **vLLM**，实现（1）KV cache **近零浪费**、（2）**请求内 / 请求间的 KV cache 灵活共享**。 |
| 与我们工作的关系 | **harness（评测吞吐 / 批量跑题，直接影响）**：我们要在成千上万个配置变体上跑 LLM 闭环，**单卡并发与显存碎片**就是成本口径的第一瓶颈。<b>动作</b>：harness 的批量评测基座把「**KV cache 利用率**」作为与「正确率」并列的报表指标，<b>判据</b>：同一批题目下若把 serving 换成 PagedAttention 类实现后吞吐提升 &lt;1.3×，说明瓶颈不在 KV cache，应转查 prompt 长度分布或工具等待。<br>**zhulong（成本口径）**：ZhuLong 的「单位任务成本」必须区分**生成 token 成本**与**KV 显存成本**，否则长上下文实验的结论会被显存 OOM 掩盖。<br>**pretrain（间接）**：长上下文训练 / 推理的可行 batch 直接受此约束。<b>风险</b>：① 这是**系统论文**（吞吐 / 显存），与模型能力无关，🚫 不能当作「模型更好」的证据；② 具体加速倍数依赖硬件与负载，本文不引用任何倍数；③ 我们的 2B 模型与论文实验规模不同，收益需实测。 |

首次收录: 2026-11-12（第十五轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 会议 DOI）

---

## 60. KTO: Model Alignment as Prospect Theoretic Optimization

| 字段 | 内容 |
|:--|:--|
| 标题 | KTO: Model Alignment as Prospect Theoretic Optimization |
| 作者（前 3） | **Kawin Ethayarajh** · **Winnie Xu** · **Niklas Muennighoff**（et al.，共 5 位：+ Dan Jurafsky · Douwe Kiela） |
| 年份 | 2024（arXiv 首次提交 **2024-02-02**；最新 v5 2026-09-08） |
| 会议 / 期刊 | **ICML 2024**（arXiv `comment` 原文 `ICML 2024`；⚠️ OpenAlex 记为 `type=preprint`、无会场 DOI ⇒ 会议信息只引 arXiv comment） |
| 被引数 | **951**（OpenAlex，DOI `10.48550/arxiv.2402.01306`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2402.01306> ｜ DOI `10.48550/arxiv.2402.01306` |
| 一句话贡献 | 摘要原文要点：把 Kahneman–Tversky **前景理论**的人类效用函数搬进对齐目标，指出 DPO 等方法隐式属于「human-aware losses（HALOs）」；KTO **只学「输出是否可取」的二元信号**（不需要成对偏好），在 **1B–30B** 尺度上匹配或超过基于偏好的方法，并强调**没有普适最优的 HALO**，最优损失取决于场景的归纳偏置。 |
| 与我们工作的关系 | **posttrain（直接对口）**：我们的 checker 天然只给「跑通 / 失败」「DRC 过 / 不过」这类**二元信号**，而成对偏好数据稀缺且昂贵 ⇒ KTO 是「用 checker 信号直接做对齐」的最短路径。<b>动作</b>：在同一批工具轨迹上做 DPO / ORPO / KTO 三臂对照，KTO 臂只用二元标签；<b>预注册判据</b>：若 KTO 在留出任务上的通过率不低于 DPO 且标注成本 &lt;1/5，则把二元 checker 信号列为主训练信号。<br>**zhulong（奖励设计）**：把「好/坏」的**定义**（工具跑通 vs 指标改善）作为独立消融，因为 KTO 的上限由该二元标签的语义决定。<br>**data（数据表）**：偏好数据表要新增「二元可取性」列，并记录标注来源（checker / 人工）。<b>风险</b>：① 二元信号丢失「好多少」的边际信息，长尾任务可能被压平；② 论文在 1B–30B 通用对话上验证，**工具轨迹上的长度偏置未验证**；③ 951 为 OpenAlex 口径，跨源不可比。 |

首次收录: 2026-11-13（第十六轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 61. H₂O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | H$_2$O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models |
| 作者（前 3） | **Zhenyu Zhang** · **Ying Sheng** · **Tianyi Zhou**（et al.，共 12 位，含 Lianmin Zheng · Christopher Ré · Zhangyang Wang · **Beidi Chen**） |
| 年份 | 2023（arXiv 首次提交 **2023-06-24**；v3 2023-12-18） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `type=conference-paper`，会议 DOI `10.52202/075280-1506`） |
| 被引数 | **423**⚠️（OpenAlex，上述 DOI，查询日 **2026-11-13**；**低于 500**，按「奠基 / 方法论常青」收录并显式标注；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2306.14048> ｜ 会议 DOI `10.52202/075280-1506` |
| 一句话贡献 | 摘要原文要点：KV cache 随序列长度与 batch **线性增长**，是长文本生成的成本主因；作者发现**少数 token（Heavy Hitters）贡献大部分 attention 值**，且删掉它们会显著掉点；据此提出 **H₂O** 驱逐策略，动态保留「近期 + heavy hitter」的平衡，把驱逐写成动态子模问题并给出（温和假设下的）理论保证；**20% heavy hitters** 下，相对 DeepSpeed Zero-Inference / HF Accelerate / FlexGen 吞吐最高提升 **29× / 29× / 3×**，同 batch 延迟最高降 **1.9×**（OPT-6.7B / OPT-30B，另测 LLaMA、GPT-NeoX）。 |
| 与我们工作的关系 | **zhulong（成本口径，直接对口）**：ZhuLong 的闭环会累积很长的**工具日志 / 波形摘要 / 报错堆栈**，KV cache 往往比权重更早撞墙。<b>动作</b>：在长轨迹评测里加一档「KV 预算 = 20%」的消融，记录「保留哪些 token」与通过率的关系；<b>预注册判据</b>：若 20% 预算下通过率下降 &lt;2 个百分点，则把 KV 预算作为独立成本旋钮纳入报表。<br>**harness（评测吞吐）**：批量跑题时把 KV 命中率与显存占用列入与正确率并列的指标。<br>**pretrain（间接）**：长上下文训练/推理的可行 batch 受同一约束。<b>风险</b>：① 29× / 1.9× 为**特定 serving 实现与负载**下的作者自报，不可外推；② heavy hitter 的判定依赖 attention 统计，**结构化日志是否同样稀疏未验证**；③ 本文不涉及模型能力提升。 |

首次收录: 2026-11-13（第十六轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + 会议 DOI）

---

## 62. Self-Instruct: Aligning Language Models with Self-Generated Instructions

| 字段 | 内容 |
|:--|:--|
| 标题 | Self-Instruct: Aligning Language Models with Self-Generated Instructions |
| 作者（前 3） | **Yizhong Wang** · **Yeganeh Kordi** · **Swaroop Mishra**（et al.，共 7 位：+ Alisa Liu · Noah A. Smith · Daniel Khashabi · Hannaneh Hajishirzi） |
| 年份 | 2022（arXiv 首次提交 **2022-12-20**；v2 2023-05-25） |
| 会议 / 期刊 | **ACL 2023**（DOI `10.18653/v1/2023.acl-long.754`；arXiv `comment` 原文 `ACL 2023 camera ready`） |
| 被引数 | **2,477**（OpenAlex，上述 DOI，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2212.10560> ｜ DOI `10.18653/v1/2023.acl-long.754` |
| 一句话贡献 | 摘要原文要点：指令微调高度依赖**人工撰写的指令数据**（数量、多样性、创造性都受限）；Self-Instruct 让模型**自举生成** instruction / input / output，过滤无效与相似样本后再微调原模型；在 GPT-3 上对 Super-NaturalInstructions **绝对提升 33%**，与用私有用户数据 + 人工标注训练的 InstructGPT-001 持平；在专家新任务上仅落后 InstructGPT-001 **5 个百分点**，并公开合成数据与代码。 |
| 与我们工作的关系 | **data（直接对口）**：EDA / 存储域的人工指令数据极少，Self-Instruct 的「种子 → 自举 → 过滤」流水线是我们扩充域内指令集的现成骨架。<b>动作</b>：用 100–200 条人工种子（版图问答、时序报告解读、工具调用）跑一轮自举，比较「只用种子」vs「种子 + 自举」在留出题上的通过率；<b>预注册判据</b>：自举数据带来的提升若 &lt;3 个百分点，则把预算转回人工种子而非继续放大合成量。<br>**harness / designflow（造题）**：把过滤规则（无效 / 相似 / 与评测重叠）固化成造题流水线的必经检查。<b>风险</b>：① 33% / 5% 为 GPT-3 时代作者自报，**模型与任务都不同**，不可直接外推；② 合成数据存在**评测污染**风险，必须先做去重与 held-out 隔离；③ 域内种子质量决定上限，自举会放大种子的偏差。 |

首次收录: 2026-11-13（第十六轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200` + ACL DOI）

---

## 63. Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

| 字段 | 内容 |
|:--|:--|
| 标题 | Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity |
| 作者（前 3） | **William Fedus** · **Barret Zoph** · **Noam Shazeer** |
| 年份 | 2021（arXiv 首次提交 **2021-01-11**；v3 2022-06-16） |
| 会议 / 期刊 | **JMLR**（arXiv `comment` 原文 `JMLR`；⚠️ OpenAlex 记为 `type=preprint`、无会场 DOI ⇒ 只引 arXiv comment） |
| 被引数 | **1,665**（OpenAlex，DOI `10.48550/arxiv.2101.03961`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2101.03961> ｜ DOI `10.48550/arxiv.2101.03961` |
| 一句话贡献 | 摘要原文要点：MoE 用「每个样本选不同参数」换**稀疏激活**（参数量大、算力恒定），但复杂度、通信成本与训练不稳定阻碍落地；Switch Transformer 把路由简化为 **top-1**，给出降通信/降计算的设计与稳定训练技巧，并**首次用 bfloat16 训练大型稀疏模型**；基于 T5-Base/Large 在同算力下取得最高 **7×** 预训练加速，多语言上对 mT5-Base 的 **101 种语言**均有增益，最终在 C4 上预训练到**万亿参数**，相对 T5-XXL **4×** 加速。 |
| 与我们工作的关系 | **pretrain（架构对照）**：BaiZe 2B 目前是稠密路线，Switch 提供「总参 ↑、激活算力不变」的对照轴。<b>动作</b>：在 2B 量级做小规模 MoE 试片（如 8 专家 top-1），预注册比较「同激活算力下的验证损失」与「同显存下的吞吐」；<b>判据</b>：若同激活算力下损失改善 &lt;2%，则不进入主训练配方。<br>**zhulong（成本口径）**：报表必须同时给**总参 / 激活参 / 每 token FLOPs**，否则 MoE 与稠密模型无法公平比较。<br>**data（配比）**：多语言增益提示数据配比要按语言分层报告。<b>风险</b>：① 7× / 4× 是**预训练速度**，不是能力倍数；② 万亿参数实验的稳定性技巧未必迁移到 2B；③ 路由负载均衡与通信开销在单机小集群上可能反而更贵。 |

首次收录: 2026-11-13（第十六轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 64. Chip Placement with Deep Reinforcement Learning（AlphaChip 的预印本）

| 字段 | 内容 |
|:--|:--|
| 标题 | Chip Placement with Deep Reinforcement Learning |
| 作者（前 3） | **Azalia Mirhoseini** · **Anna Goldie** · **Mustafa Yazgan**（et al.，共 22 位，含 Ebrahim Songhori · Quoc V. Le · Jeff Dean） |
| 年份 | 2020（arXiv 首次提交 **2020-04-22**；同行评审版 **2021**） |
| 会议 / 期刊 | arXiv **预印本**（无 comment）；同行评审版 = **A graph placement methodology for fast chip design**, *Nature* **594**:207–212 (2021)，DOI `10.1038/s41586-021-03544-w` |
| 被引数 | **704**（Nature 版，OpenAlex DOI `10.1038/s41586-021-03544-w`）· **274**（arXiv 预印本，DOI `10.48550/arxiv.2004.10746`）；均为 OpenAlex、查询日 **2026-11-13**；S2 未查，**两口径不可混用** |
| arXiv / DOI | <https://arxiv.org/abs/2004.10746> ｜ Nature DOI `10.1038/s41586-021-03544-w` |
| 一句话贡献 | 摘要原文要点：把宏单元布局写成 **RL 问题**（把网表节点放到画布上），并用「预测布局质量」的监督任务做表示学习，再把该网络当作策略/价值网络的编码器以支持迁移；目标是最小化 **PPA**，作者称在**不到 6 小时**内即可在现代加速器网表上生成「超人或有竞争力」的布局，而既有基线需要人类专家在环、耗时数周。 |
| 与我们工作的关系 | **designflow（直接对口）**：这是「用学习/agent 做布局」的**方法论原点**，也是造题时最容易被问「和 AlphaChip 比怎样」的基线。<b>动作</b>：布局类题面固定三项口径 —— 网表输入、PPA 评估脚本、可迁移性 split（训练块 / 未见块），「未见块」单列榜单，不许混进同一条平均分。<br>**zhulong（奖励设计）**：核心技巧是**先学一个能预测奖励的代理模型**再拿它当编码器 ⇒ 与我们「LLM 出方案、工具给真值」互补：代理模型只用于**排序候选**，最终分必须由真实 PPA 工具给；加一档「代理排序 vs 随机排序」同预算对照。<br>**harness（评测）**：6 小时 vs 数周提示评测必须同时报**墙钟时间**与**工具调用次数**，否则「快」不可核验。<b>风险</b>：① 704 是 Nature 版、274 是预印本，跨源不可比；② 「superhuman」为作者自报、依赖其内部网表与工具流；③ 2020 年的 RL 配方 ≠ 今天 LLM agent 的能力证据。 |

首次收录: 2026-11-13（第十七轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex 2/2 `200`；Nature 版经 OpenAlex 精确标题检索命中）

---

## 65. YaRN: Efficient Context Window Extension of Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | YaRN: Efficient Context Window Extension of Large Language Models |
| 作者（前 3） | **Bowen Peng** · **Jeffrey Quesnelle** · **Honglu Fan**（et al.，共 4 位：+ Enrico Shippole） |
| 年份 | 2023（arXiv 首次提交 **2023-08-31**；v3 **2026-02-06**） |
| 会议 / 期刊 | arXiv **预印本**（无 comment；OpenAlex `type=preprint`）⇒ **本轮未核到会场，不写会议名** |
| 被引数 | **591**（OpenAlex，DOI `10.48550/arxiv.2309.00071`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2309.00071> ｜ DOI `10.48550/arxiv.2309.00071` |
| 一句话贡献 | 摘要原文要点：RoPE 能编码位置信息，但模型**无法泛化到超过训练长度**；YaRN 是计算高效的上下文扩展方法，相对此前方法**少用 10× token、少用 2.5× 训练步**，让 LLaMA 类模型能有效利用并外推到远超原预训练长度的上下文，且**超过此前上下文扩展 SOTA**；还展示了**外推到微调数据长度之外**的能力（代码开源）。 |
| 与我们工作的关系 | **pretrain（长上下文，直接对口）**：若要从 8K/32K 扩到更长，YaRN 是**成本最低的第一条基线**（只改位置编码缩放 + 少量继续训练），比从头长上下文预训练便宜一个量级。<b>动作</b>：在 2B 上做「YaRN 继续训练 1B token」vs「从零长上下文」同算力对照，评测用**同一套长文档检索 + 长轨迹任务**；<b>预注册判据</b>：若 YaRN 臂在 ≥64K 检索上掉点 &gt;3pp，则不作主路径，只作推理期临时扩展。<br>**data（语料）**：扩展训练必须配长文档语料，数据表单列「长度分布」，否则只是「位置编码能外推、内容没见过」。<br>**harness（长轨迹）**：外推能力可把长工具日志塞进同一上下文，但须与 H₂O/驱逐策略**分开消融**。<b>风险</b>：① 591 为 OpenAlex 口径；② 「超过 SOTA」是 2023 年的对比结论，**不代表对今天的长上下文模型仍成立**；③ 外推到微调长度之外为作者自报，需自测。 |

首次收录: 2026-11-13（第十七轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 66. Fast Inference from Transformers via Speculative Decoding

| 字段 | 内容 |
|:--|:--|
| 标题 | Fast Inference from Transformers via Speculative Decoding |
| 作者（前 3） | **Yaniv Leviathan** · **Matan Kalman** · **Yossi Matias**（共 3 位，均 Google Research） |
| 年份 | 2022（arXiv 首次提交 **2022-11-30**；v2 2023-05-18） |
| 会议 / 期刊 | **ICML 2023 Oral**（arXiv `comment` 原文 `ICML 2023 Oral`；OpenAlex 记为 `type=preprint` ⇒ 会议信息只引 arXiv comment） |
| 被引数 | **354**⚠️（OpenAlex，DOI `10.48550/arxiv.2211.17192`，查询日 **2026-11-13**；**低于 500**，按「奠基 / 方法论常青」收录并显式标注；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2211.17192> ｜ DOI `10.48550/arxiv.2211.17192` |
| 一句话贡献 | 摘要原文要点：自回归解码 K 个 token 要跑 K 次串行前向，是推理慢的根因；作者提出 **speculative decoding** —— 用更高效的近似模型先「草拟」若干 token，再用**新的采样方法**在大模型上并行验证，从而在**不改变输出分布**的前提下加速；**无需重训、无需改架构**，在 T5-XXL 上相对标准 T5X 实现 **2×–3× 加速且输出完全一致**。 |
| 与我们工作的关系 | **zhulong（serving 成本，直接对口）**：长轨迹 agent 的瓶颈常在**逐 token 解码**，speculative decoding 是「不动模型、只动解码」的即插即用加速，适合不能频繁重训的场景。<b>动作</b>：在 2B 评测服务上接一版草稿模型（同 tokenizer 的小模型），预注册比较「同 batch、同输出一致性」下的 tokens/s 与 p95 延迟；<b>判据</b>：若在 EDA/存储域文本上接受率 &lt;60%，该草稿模型不用于生产，只用于离线批量评测。<br>**harness（评测吞吐）**：批量跑题时把「解码加速比」与「判分正确率」并列报告，避免用加速换来判分漂移却看不见。<br>**pretrain（间接）**：训练不受影响，但**评测/自采样**（如 RL 采样）可直接受益。<b>风险</b>：① 354 &lt; 500，属「奠基」而非高引；② 2×–3× 是 T5-XXL + 特定实现的作者自报，**域外文本接受率可能显著更低**；③ 「输出完全一致」依赖采样方法的正确实现，自研实现需做分布一致性测试。 |

首次收录: 2026-11-13（第十七轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 67. GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers

| 字段 | 内容 |
|:--|:--|
| 标题 | GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers |
| 作者（前 3） | **Elias Frantar** · **Saleh Ashkboos** · **Torsten Hoefler**（et al.，共 4 位：+ Dan Alistarh） |
| 年份 | 2022（arXiv 首次提交 **2022-10-31**；v2 2023-03-22） |
| 会议 / 期刊 | **ICLR 2023**（arXiv `comment` 原文 `ICLR 2023`；OpenAlex 记为 `type=preprint` ⇒ 会议信息只引 arXiv comment） |
| 被引数 | **2,195**（OpenAlex，DOI `10.48550/arxiv.2210.17323`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2210.17323> ｜ DOI `10.48550/arxiv.2210.17323` |
| 一句话贡献 | 摘要原文要点：GPT/OPT 类模型推理即使只做前向也要多张高性能 GPU，限制可用性；GPTQ 是**基于近似二阶信息的一次性权重量化**方法，可在**约 4 GPU 小时**内量化 **175B** 模型到 **3–4 bit**，相对未压缩基线精度损失可忽略；压缩收益比此前 one-shot 量化方法**翻倍以上**，**首次让 175B 模型在单卡内做生成式推理**；端到端相对 FP16 约 **3.25×**（A100）/ **4.5×**（A6000）加速（作者自报）。 |
| 与我们工作的关系 | **zhulong / vision（部署成本，直接对口）**：BaiZe 2B 若要上单卡或端侧，4-bit 权重量化是最现实的降本手段；GPTQ 是**后训练、无需重训**的路线，与 QAT 形成对照。<b>动作</b>：在 2B checkpoint 上做「FP16 / 8-bit / 4-bit GPTQ」三档，评测集固定为**同一套 EDA 与工具调用题**（不是通用困惑度）；<b>预注册判据</b>：若 4-bit 在留出题上通过率下降 &gt;2pp，则只在离线批量场景启用，不进在线服务。<br>**harness（评测口径）**：量化后模型必须用**同一判分器**重跑，不许引用 FP16 历史分数。<br>**SLM / 端侧**：4-bit 让 2B 的显存占用进入消费级显卡区间，是「端侧可跑」的前提之一。<b>风险</b>：① 3.25×/4.5× 为特定 GPU 与实现的作者自报；② 175B 的结论**不保证**在 2B 上同样无损（小模型通常更脆弱）；③ 校准集分布偏移（芯片设计文本/工具日志 vs 通用网页）可能显著影响精度，须自测。 |

首次收录: 2026-11-13（第十七轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 68. Toward an Open-Source Digital Flow: First Learnings from the OpenROAD Project

| 字段 | 内容 |
|:--|:--|
| 标题 | Toward an Open-Source Digital Flow: First Learnings from the OpenROAD Project |
| 作者（前 3） | **Tutu Ajayi** · **Vidya A. Chhabria** · **Mateus Paiva Fogaça**（et al.，共 **21** 位；含 **Andrew B. Kahng**、Sherief Reda、Sachin S. Sapatnekar、Carl Sechen） |
| 年份 | **2019**（OpenAlex `publication_year=2019`） |
| 会议 / 期刊 | **DAC 2019**（ACM/IEEE Design Automation Conference；DOI `10.1145/3316781.3326334`；OpenAlex `biblio` 记 pp. 1–4） |
| 被引数 | **216**（OpenAlex，查询日 **2026-11-13**；S2 / Google Scholar 未查） |
| arXiv / DOI | **无 arXiv 版本** ⇒ 按 DOI 收录：<https://doi.org/10.1145/3316781.3326334> |
| 一句话贡献 | 摘要原文要点：介绍 OpenROAD 的 Alpha 版计划 —— 一个**开源端到端 silicon compiler**，目标是「硬件设计民主化」（降低系统设计者的成本 / 专业门槛 / 周期 / 风险）；流程覆盖**逻辑综合、floorplan、placement、CTS、global routing、detailed routing**，并配套 **STA、寄生提取、电源完整性分析、云部署**；摘要同时给出若干「lessons learned」，但**没有给任何 PPA 数字**（🚫 不得替它编性能结论）。 |
| 与我们工作的关系 | **designflow（造题与保真度基座，直接对口）**：一个**开源、可脚本化、可固定版本**的完整 flow，是 L1–L5 保真度里「流程级」最现实的参照 —— 题目可以定义为「在固定 flow 上把某个指标做上去」。<b>动作</b>：固定 **工具 commit + PDK 版本**，选 5 个小设计跑通「综合→布局→布线→STA」，把 WNS / TNS / area / power 四项落表；<b>预注册判据</b>：同一输入连跑两次，若任一指标漂移 **&gt;2%**，则该 flow 判为「不可复现」，🚫 不进判分基线。<br>**harness（判分可验证性）**：把「flow 跑通」拆成可判定的门（DRC clean、timing 报告可解析、版图可 diff），而不是让模型自述成功。<br>**zhulong（动作空间）**：EDA 工具 + Tcl / 约束脚本天然是 agent 的动作空间；文中「lessons learned」强调的**工具间版本耦合**提示：动作必须绑定版本，否则同一策略在换版本后失效。<br>**data（领域语料）**：flow 的脚本 / 日志 / 报告是「结构化领域文本」的天然样本来源。<b>风险</b>：① 2019 年论文，且 **216 &lt; 500**，按「领域奠基」而非高引收录（我们的观察）；② 摘要无量化结果，任何「快 N 倍 / 面积降 N%」都不得挂到本文；③ OpenROAD 本身已迭代多年，本文只代表 Alpha 期设计意图。 |

首次收录: 2026-11-13（第十八轮）｜ 状态: 元数据已核验（OpenAlex `200`，DOI / venue / 作者 / 被引；**无 arXiv ⇒ 未做 arXiv 校验，如实标注**）

---

## 69. LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens

| 字段 | 内容 |
|:--|:--|
| 标题 | LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens |
| 作者（前 3） | **Yiran Ding** · **Li Lyna Zhang** · **Chengruidong Zhang**（et al.，共 **8** 位：+ Yuanyuan Xu、Ning Shang、Jiahang Xu、Fan Yang、Mao Yang） |
| 年份 | **2024**（arXiv 首次提交 **2024-02-21T12:30:33Z**） |
| 会议 / 期刊 | **arXiv 预印本**（`cs.CL`；OpenAlex `type=preprint`；**会议未核到**，🚫 不写 ICML / NeurIPS） |
| 被引数 | **302**（OpenAlex，DOI `10.48550/arxiv.2402.13753`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2402.13753> ｜ DOI `10.48550/arxiv.2402.13753` |
| 一句话贡献 | 摘要原文要点：把预训练 LLM 的上下文窗口**首次扩到 2048k token**，训练长度 ≤256k 时只需**至多 1k 步微调**，同时保持原短上下文性能；三项设计 = ① 通过高效搜索识别并利用**位置插值的两种非均匀性**（免微调即可 **8×** 扩展）；② **渐进式扩展**（先把 256k 模型微调好，再做第二次位置插值到 2048k）；③ 在 **8k** 长度上重新校准以恢复短上下文性能；实验覆盖 LLaMA2 与 Mistral。 |
| 与我们工作的关系 | **pretrain（长上下文配方，直接对照 B 轨 #65 YaRN）**：两条路线都是「改位置编码 + 少量继续训练」，但 LongRoPE 多了**渐进式两段扩展 + 短上下文回校**。<b>动作</b>：在 2B 模型上做「YaRN 一步扩到 64k」vs「LongRoPE 式 32k→64k 两段 + 8k 回校」同算力对照；<b>预注册判据</b>：64k 检索任务掉点 &gt;3pp，或短上下文（≤8k）回升 &lt;1pp，则该臂只作推理期扩展，不进训练配方。<br>**data（长文语料）**：摘要点明「long texts 稀缺」是扩展的成本来源 ⇒ data 线须单列长文档语料的**长度分布**，不足 1B token 不做长上下文对照。<br>**harness（长上下文评测）**：必须**同时**报长上下文与短上下文两组分数（本文第 ③ 步就是为此），否则「扩窗」可能只是把短任务能力换掉。<b>风险</b>：① **302 &lt; 500**，按「奠基 / 常青」收录；② 2048k 与 1k 步均为作者自报，微调算力与数据未在摘要给出；③ 实验模型是 LLaMA2 / Mistral，**2B 小模型上是否同样成立未知**；④ 与 RoPE / YaRN 的差异属实现细节，引用时须回原文。 |

首次收录: 2026-11-13（第十八轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 70. Ramulator: A Fast and Extensible DRAM Simulator

| 字段 | 内容 |
|:--|:--|
| 标题 | Ramulator: A Fast and Extensible DRAM Simulator |
| 作者（前 3） | **Yoongu Kim** · **Weikun Yang** · **Onur Mutlu**（共 3 位） |
| 年份 | **2015**（OpenAlex `publication_year=2015`；IEEE CAL **15(1):45–49**） |
| 会议 / 期刊 | **IEEE Computer Architecture Letters**（DOI `10.1109/LCA.2015.2414456`） |
| 被引数 | **799**（OpenAlex，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | **无 arXiv 版本** ⇒ <https://doi.org/10.1109/LCA.2015.2414456> ｜ 代码 <https://github.com/CMU-SAFARI/ramulator> |
| 一句话贡献 | 摘要原文要点：面向「DRAM 标准快速演化」的需求，提出**基于通用模板**的**周期精确、可扩展** DRAM 模拟器 —— 先建模通用 DRAM 系统、再注入具体标准细节，因此开箱支持 **DDR3/4、LPDDR3/4、GDDR5、WIO1/2、HBM** 及若干学术提案（SALP、AL-DRAM、TL-DRAM、RowClone、SARP）；作者自报**比次快模拟器快 2.5×**，**BSD** 许可发布。 |
| 与我们工作的关系 | **zhulong（评测基座 / 成本口径）**：把「LLM 出配置 → 模拟器跑 → 回填指标」做成闭环前，先要有一个**可脚本化、可换标准**的模拟器；模板化设计意味着**新增一个 DRAM 标准只需加规格文件**，适合作为参数搜索的执行端。<b>动作</b>：用固定 trace 标定单配置墙钟时间，再决定闭环预算；<b>判据</b>：单次评测 &gt;30s ⇒ 先做代理模型 / 缩短 trace，🚫 直接上大搜索。<br>**designflow（L1–L5 保真度）**：本文「通用模板 + 标准细节」的分层，可直接作为保真度分层的写法（时序 / 功耗 / 可靠性分开建模，而不是笼统一个「高 / 中 / 低」）。<br>**data（存储领域语料）**：DRAM 标准规格是**结构化领域文本**的一手样本，可用来造「规格 → 可执行配置」类任务。<b>风险</b>：① 2.5× 为作者自报、且是 2015 年的对比基线；② 支持的标准列表停留在 2015 年（DDR5 / HBM3 等不在内）；③ 新工作应优先用 **Ramulator 2.0（B 轨 #51）**，本条价值在**方法论源头**（模板化 / 可扩展）而非当前版本。 |

首次收录: 2026-11-13（第十八轮）｜ 状态: 元数据已核验（OpenAlex `200`；**无 arXiv ⇒ 如实标注**）

---

## 71. Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors（RowHammer）

| 字段 | 内容 |
|:--|:--|
| 标题 | Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors |
| 作者（前 3） | **Yoongu Kim** · **Ross Daly** · **Jeremie S. Kim**（et al.，共 **9** 位：+ Chris Fallin、Ji Hye Lee、Donghyuk Lee、Chris B. Wilkerson、Konrad K. Lai、**Onur Mutlu**） |
| 年份 | **2014**（ISCA 2014） |
| 会议 / 期刊 | **ISCA 2014**（ACM SIGARCH Computer Architecture News **42(3):361–372**；DOI `10.1145/2678373.2665726`） |
| 被引数 | OpenAlex 对同一篇有**两个记录**：ACM DOI 记录 **967**、IEEE DOI 记录（`10.1109/ISCA.2014.6853210`）**528**（查询日 **2026-11-13**）。本表取**较高记录 967** 并注明拆分，🚫 不把两个数字相加。 |
| arXiv / DOI | <https://doi.org/10.1145/2678373.2665726> ｜ IEEE 版 <https://doi.org/10.1109/ISCA.2014.6853210>（**无 arXiv**） |
| 一句话贡献 | 摘要原文要点：DRAM 工艺缩小后单元间电学干扰加剧，**反复激活同一行会破坏邻近行数据**（内存隔离假设被打破）；在 Intel / AMD 系统上用恶意程序复现，**129 个 DRAM 模块中 110 个**（来自 3 家主要厂商）被诱发错误；根因是**字线反复翻转**加剧单元间耦合、加速邻近行漏电；FPGA 测试平台给出特征化结论 —— **最少 139K 次访问即可诱发错误**、**每 1.7K 个单元中最多 1 个易受影响**；并提出一种低开销防护方案。 |
| 与我们工作的关系 | **data（存储领域一手语料 / 题源，间接但真实）**：RowHammer 是「规格之外的真实失效模式」的经典样本，适合做**可靠性问答 / 失效分析题**的语料锚点（题目必须引用原文结论，🚫 不外推阈值）。<br>**designflow（L1–L5 保真度）**：它说明「性能跑分」之外**可靠性是独立一层**保真度；造存储类题时须把「功能正确」与「压力下正确」分开判。<br>**zhulong（若做内存系统评测）**：评测指标不能只有吞吐 / 延迟，还要有**错误率 / 防护开销**两列。<br>**harness（判分口径）**：压力测试的「通过」必须由**独立 checker** 判（数据比对），不许用被测系统自报。<b>风险</b>：① 2014 年、硬件相关阈值（139K / 1.7K）**只对当时测试平台成立**，🚫 当普适常数引用；② 与 LLM 研发无直接关系，价值在**存储域语料与可靠性口径**；③ OpenAlex 双记录（967 / 528）系同一篇，引用时须说明取哪一个。 |

首次收录: 2026-11-13（第十八轮）｜ 状态: 元数据已核验（OpenAlex `200` ×2 记录；**无 arXiv ⇒ 如实标注**）

---

## 72. Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism

| 字段 | 内容 |
|:--|:--|
| 标题 | Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism |
| 作者（前 3） | **Mohammad Shoeybi** · **Mostofa Patwary** · **Raul Puri**（et al.，共 **6** 位：+ Patrick LeGresley、Jared Casper、**Bryan Catanzaro**） |
| 年份 | **2019**（arXiv 首次提交 **2019-09-17T19:42:54Z**；v2 更新 2020-03-13） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`，venue 记 arXiv；🚫 不写 NeurIPS/ICML —— 未核到正式会场） |
| 被引数 | **3,281**（OpenAlex，DOI `10.48550/arxiv.1909.08053`，查询日 **2026-11-13**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1909.08053> ｜ DOI `10.48550/arxiv.1909.08053` ｜ 代码 <https://github.com/NVIDIA/Megatron-LM> |
| 一句话贡献 | 摘要原文要点：提出**层内（intra-layer）模型并行** —— 把 Transformer 的 attention / MLP 按列、按行切到多卡，**不需要新编译器或改库**，在原生 PyTorch 里插几个通信算子即可，且与流水并行正交；用 512 张 GPU 训到 **8.3B** 参数，整机持续 **15.1 PetaFLOPs**、相对单卡强基线（39 TFLOPs，峰值 30%）的**扩展效率 76%**；并指出 **BERT 类模型在放大时 layer-norm 的放置位置至关重要**（这一条比 PPL 数字更可迁移）。 |
| 与我们工作的关系 | **pretrain（2B 训练的并行底座，直接对口）**：我们做 2B 级训练时最先撞到的是**显存而非算力** —— 本文给出的「层内切分 + 与流水并行正交」是最小改动路径。<b>动作</b>：在 2B 上做「纯数据并行（梯度累积）」vs「数据并行 + 层内张量并行 TP=2/4」两组对照，固定全局 batch 与 token 数，只比**有效吞吐（tokens/s/卡）与显存峰值**；<b>预注册判据</b>：若 TP 组相对 DP 组的有效吞吐提升 **&lt;15%**，或通信开销使 MFU 下降，则该并行度不进默认配方（我们的观察：2B 规模下 TP 的收益随互联带宽剧烈变化）。<br>**harness（成本口径）**：本文的「15.1 PFLOPs + 76% 扩展效率」是**整机口径**，提醒我们评测/成本表必须同时报**峰值占比与扩展效率**，否则不同并行配置的训练成本不可比。<br>**zhulong（动作-代价模型）**：并行度是可配置动作，其代价（通信 / 重算 / 显存）应进 zhulong 的「动作 → 成本」映射，而不是当常量。<b>风险</b>：① 2019 年、V100 时代数字，**不可外推到 H800 / 2B 规模**；② 8.3B 与 76% 均为作者自报，未给完整超参表；③ LN 位置结论只在 BERT 类（post-LN）上验证过，GPT 类（pre-LN）需另测。 |

首次收录: 2026-11-13（第十九轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 73. DeepSeek-V3 Technical Report

| 字段 | 内容 |
|:--|:--|
| 标题 | DeepSeek-V3 Technical Report |
| 作者（前 3） | **DeepSeek-AI**（机构作者）· **Aixin Liu** · **Bei Feng**（et al.；arXiv 作者表极长，含 Wenfeng Liang 等，本表不逐一列举） |
| 年份 | **2024**（arXiv 首次提交 **2024-12-27T04:03:16Z**；v2 更新 2025-02-18） |
| 会议 / 期刊 | **arXiv 预印本**（技术报告；OpenAlex `type=preprint`；🚫 不写正式会场） |
| 被引数 | **7,939**（OpenAlex，DOI `10.48550/arxiv.2412.19437`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2412.19437> ｜ DOI `10.48550/arxiv.2412.19437` ｜ 权重 <https://github.com/deepseek-ai/DeepSeek-V3> |
| 一句话贡献 | 摘要原文要点：**MoE 架构，总参 671B / 每 token 激活 37B**；沿用 **MLA + DeepSeekMoE**（V2 已验证），并首次采用 **auxiliary-loss-free 负载均衡**与**多 token 预测（MTP）**训练目标；预训练 **14.8T tokens** 后再做 SFT + RL；全程训练仅 **2.788M H800 GPU 小时**，且**训练全程未出现不可恢复的 loss spike、未做任何回滚**。 |
| 与我们工作的关系 | **pretrain（MoE 路由稳定性，最有价值的一条）**：2B 级做 MoE 时，auxiliary loss 会与主损失抢梯度、系数难调；本文的 **aux-loss-free 负载均衡**是可直接试的替代。<b>动作</b>：在 2B 稠密基线之上加一组「同激活参数量的小 MoE」，分别用 aux-loss 与 aux-loss-free 路由，对比**专家负载熵 / 路由抖动 / 验证损失**；<b>预注册判据</b>：若 aux-loss-free 组在固定 token 预算下验证损失劣于稠密基线 **&gt;2%**，或专家负载熵在训练后 20% 区间持续下降（塌缩），则该路由方案不进主配方。<br>**data（token 预算锚点）**：14.8T tokens 作为「大厂 MoE 的预算量级」，提醒我们 2B 的 token 预算讨论要**先对齐 token 数再谈配方**，不能拿不同 token 数的曲线互相比较。<br>**zhulong（成本口径）**：2.788M H800 小时 = **可直接换算的「一次完整训练」成本单位**，可作 zhulong 动作成本表的参照量级（注意那是 671B 模型，🚫 不得线性缩放到 2B 当结论）。<br>**harness（评测口径）**：报告以「对比闭源前沿模型」为结论口径，我们在引用时只能写「作者自报」，🚫 不当作独立复现结论。<b>风险</b>：① 671B / 37B 与 2B 规模差 2 个数量级，**任何超参都不能照搬**；② 摘要**未给** FP8 / 通信重叠等正文细节，引用须回原文；③ 7,939 次引用含大量二手转述，被引数只反映关注度、不反映正确性。 |

首次收录: 2026-11-13（第十九轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---


## 74. GAIA: a benchmark for General AI Assistants

| 字段 | 内容 |
|:--|:--|
| 标题 | GAIA: a benchmark for General AI Assistants |
| 作者（前 3） | **Grégoire Mialon** · **Clémentine Fourrier** · **Craig Swift**（et al.，共 **6** 位：+ **Thomas Wolf**、Yann LeCun、Thomas Scialom） |
| 年份 | **2023**（arXiv 首次提交 **2023-11-21T20:34:47Z**，仅 v1） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`；🚫 不写正式会场） |
| 被引数 | **526**（OpenAlex，DOI `10.48550/arxiv.2311.12983`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2311.12983> ｜ DOI `10.48550/arxiv.2311.12983` ｜ 榜单 <https://huggingface.co/gaia-benchmark> |
| 一句话贡献 | 摘要原文要点：提出面向通用助手的 GAIA 基准，题目要求**推理 + 多模态 + 网页浏览 + 工具使用**组合能力，**对人类概念上简单、对当前 AI 很难** —— 人类作答 **92%** vs 带插件的 GPT-4 **15%**；与「越难越好」的基准潮流相反，其立场是 **AGI 的标志是在日常问题上表现出接近普通人的稳健性**；共设计 **466 题**，公开题目但**保留 300 题答案**用于榜单。 |
| 与我们工作的关系 | **harness（判分可验证性 + 反「刷榜」设计，直接对口）**：GAIA 的两个设计值得照抄 —— ① **答案唯一且可自动判**（不靠 LLM 当裁判），② **留出 300 题答案不公开**以抑制过拟合。<b>动作</b>：把 designflow / EDA agent 题的答案库按「公开题面 + 私有判据」拆分，私有部分只进评测机；<b>预注册判据</b>：若某题型的判据无法写成**确定性检查器**（只能人工看），则该题降级为「探索题」，🚫 不进主榜。<br>**harness（人机差作为难度标尺）**：92% vs 15% 的差距说明「对人类简单」不等于「对模型简单」；我们造 EDA 题时可先测**领域工程师的正确率**，把「工程师能做对、模型做不对」作为选题优先级，而不是一味加难。<br>**zhulong（工具使用能力轴）**：题目要求多步工具调用 ⇒ 与 zhulong 的「工具轨迹」评测同构，可借用其**多能力组合**的题型分层。<b>风险</b>：① 作者自报数字（92% / 15%），且 GPT-4 是 2023 年配置，**今日不可直接对比**；② 526 次引用里大量是二手引用，被引数只代表关注度；③ 题目内容涉网页浏览，**2026 年已有大量题目因网页变化而失效**（我们的观察）⇒ 引用其方法论而非题目本身。 |

首次收录: 2026-11-13（第十九轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex `200`）

---

## 75. A Case for Intelligent RAM（IRAM）

| 字段 | 内容 |
|:--|:--|
| 标题 | A Case for Intelligent RAM |
| 作者（前 3） | **David A. Patterson** · **Thomas E. Anderson** · **Neal Cardwell**（et al.，共 **8** 位：+ Richard Fromm、Kimberly Keeton、Christos Kozyrakis、R. Thomas、Katherine Yelick） |
| 年份 | **1997**（IEEE Micro **17(2):34–44**，3–4 月号） |
| 会议 / 期刊 | **IEEE Micro**（DOI `10.1109/40.592312`） |
| 被引数 | **729**（OpenAlex，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | **无 arXiv 版本**（1997 年）⇒ <https://doi.org/10.1109/40.592312> |
| 一句话贡献 | 摘要原文要点：指出把 CPU 与 DRAM 分在不同晶圆线上制造的做法正被两个趋势动摇 —— **处理器与 DRAM 的速度差每年扩大 50%**，而**单颗 DRAM 的容量与组织方式越来越难用、容量却每年增长 60%**；主张 **IRAM（Intelligent RAM）= 把处理与存储合到一颗芯片**，以**降低访存延迟、提高带宽、改善能效**，并让容量/组织选择更灵活、节省板级面积；文末给出**三种 IRAM 设计**的性能与能效估算。 |
| 与我们工作的关系 | **zhulong（架构-成本论证的模板，间接但真实）**：「把两个层级合成一个」的论证结构（差距在扩大 → 合并能省什么 → 三种设计估算）可以直接搬到我们的「推理栈哪里该合并」讨论（如 KV cache 与计算、预取与调度）。<b>动作</b>：用同一结构写一页「2B 推理的合并候选」：列出 3 个候选合并点、各自能省的延迟/带宽/能耗、以及**必须付出的代价**（容量灵活性、良率、编程模型）；<b>预注册判据</b>：任一候选若省下的带宽 &lt; 20% 而引入新失效模式（如容量不可配），则不立项。<br>**data（存储域一手语料）**：这类「趋势数字 + 设计权衡」文本是**架构判断题**的优质语料锚点（题目须引用原文数字，🚫 不外推）。<br>**方法论迁移（我们的观察）**：1997 年的「速度差每年 50%」这类趋势论证，今天换成了「HBM 带宽 vs 计算」的同类论证 —— 读经典的价值在于**论证结构**而非当时的数字。<b>风险</b>：① 1997 年数字（50% / 60%）**只对当时成立**，🚫 当今日常数；② IRAM 商业上未成为主流（HBM + chiplet 走了另一条路），引用时须说明「论证成立 ≠ 路线胜出」；③ 本文是**杂志文章（IEEE Micro）**而非完整会议论文，实验细节有限。 |

首次收录: 2026-11-13（第十九轮）｜ 状态: 元数据已核验（OpenAlex `200`；**无 arXiv ⇒ 如实标注**）

---


## 76. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

| 字段 | 内容 |
|:--|:--|
| 标题 | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding |
| 作者（前 3） | **Jacob Devlin** · **Ming-Wei Chang** · **Kenton Lee**（et al.，共 **4** 位：+ Kristina Toutanova） |
| 年份 | **2018**（arXiv 首次提交 **2018-10-11T00:50:01Z**，`v2`） |
| 会议 / 期刊 | **NAACL-HLT 2019**（OpenAlex 独立记录：DOI `10.18653/v1/N19-1423`，2019，pp. 4171–4186） |
| 被引数 | **76,688**（OpenAlex，arXiv DOI `10.48550/arxiv.1810.04805`，查询日 **2026-11-13**）／ **57,751**（同一工作的 NAACL 记录，DOI `10.18653/v1/N19-1423`，同日查询；**两条记录口径不同，🚫 不相加**）；S2 未查 |
| arXiv / DOI | <https://arxiv.org/abs/1810.04805> ｜ DOI `10.48550/arxiv.1810.04805` |
| 一句话贡献 | 摘要原文要点：用「**双向**上下文联合建模」的掩码语言模型（MLM）+ 下一句预测做无标注预训练，微调时只加一层输出即可在 **11 项 NLP 任务**上刷新当时最好成绩 —— GLUE **80.5%**（+7.7 点）、MultiNLI **86.7%**（+4.6 点）、SQuAD v1.1 Test F1 **93.2**（+1.5）、SQuAD v2.0 Test F1 **83.1**（+5.1）。 |
| 与我们工作的关系 | **pretrain（编码器路线的对照基线）**：BaiZe 若做「编码器式」任务（判分、检索、结构化抽取），BERT 的 **MLM 目标 + 微调范式**仍是成本最低的对照；<b>动作</b>：在 2B 规模上对比「decoder-only 零样本」与「BERT 式编码器 + 小头微调」在 EDA 文本任务上的样本效率；<b>预注册判据</b>：若在 ≤1k 标注样本下编码器路线领先 &lt; 3 点，则不额外维护双塔训练栈。<br>**data（语料配比的历史教训）**：其「大规模无标注语料 + 小任务微调」说明**预训练规模效应可压过任务特定结构**；<b>动作</b>：数据线做「同 token 预算、不同配比」对照时，把「下游微调样本量」固定成一条轴，别只比预训练 loss。<br>**与 GPT 系的分歧点（方法论）**：MLM 的双向性与 decoder-only 的单向性之争最终由「生成式统一」胜出 —— 读它的价值在于**知道我们放弃的是什么**。<b>风险</b>：① 数字是 2018 年基线（自报，未复现）；② 76,688 与 57,751 是同一工作的两条记录，引用时**只可择一**并注明 DOI；③ 当年语料（BooksCorpus + Wikipedia）今日不可直接复用。 |

首次收录: 2026-11-13（第二十轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`；OpenAlex 两条记录均 `200`）

---

## 77. Learning Transferable Visual Models From Natural Language Supervision（CLIP）

| 字段 | 内容 |
|:--|:--|
| 标题 | Learning Transferable Visual Models From Natural Language Supervision |
| 作者（前 3） | **Alec Radford** · **Jong Wook Kim** · **Chris Hallacy**（et al.，共 **12** 位：+ Aditya Ramesh、Gabriel Goh、Sandhini Agarwal、Girish Sastry、Amanda Askell、Pamela Mishkin、Jack Clark、Gretchen Krueger、**Ilya Sutskever**） |
| 年份 | **2021**（arXiv 首次提交 **2021-02-26T19:04:58Z**，`v1`） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`、`primary_location` = arXiv；ICML 2021 正式版**本轮未核到** ⇒ 不写会场） |
| 被引数 | **19,245**（OpenAlex，DOI `10.48550/arxiv.2103.00020`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2103.00020> ｜ DOI `10.48550/arxiv.2103.00020` ｜ 代码/权重 <https://github.com/OpenAI/CLIP> |
| 一句话贡献 | 摘要原文要点：用「**判断哪段文本配哪张图**」这个简单对比目标，在 **4 亿**互联网图文对上从零预训练，学到的表征可用自然语言直接指代视觉概念 ⇒ **零样本迁移**；在 **30+** 视觉数据集（OCR / 视频动作识别 / 地理定位 / 细粒度分类）上多数任务**无需数据集特定训练**即可接近全监督基线，在 ImageNet 上**零样本**匹配原版 ResNet-50 且未用其 128 万训练样本。 |
| 与我们工作的关系 | **vision（视觉塔的第一对照基线）**：BaiZe 视觉编码器做「冻结 / 微调」取舍时，CLIP 的**零样本-全监督差距**就是最直接的标尺；<b>动作</b>：视觉线先跑「CLIP 冻结特征 + 线性头」作为下界，再决定是否值得训自研塔；<b>预注册判据</b>：自研塔在同一评测上若不领先冻结 CLIP ≥5 点，先查数据与对齐目标而不是加参数。<br>**data（图文对质量 &gt; 数量）**：4 亿对来自互联网 ⇒ 其**过滤/去重策略**比数字本身更可迁移；<b>动作</b>：图-文/图-代码对（波形图、版图、时序报告截图）要做「文本侧可判别性」抽检，避免图相似而文本近乎重复。<br>**harness（零样本评测口径）**：prompt 模板与类别名会显著影响零样本分数 ⇒ 评测必须**冻结 prompt 集**并报告方差；<b>动作</b>：把 prompt 模板纳入「固定不变量」清单，进版本号。<br>**与 EDA 场景的差异（我们的观察）**：自然图像语义在互联网语料里密集，**版图/波形语义稀疏**，直接套 CLIP 目标大概率欠拟合 ⇒ 需先验证「文本能否区分相邻样本」。<b>风险</b>：① 19,245 次引用横跨多版本，数字只表关注度；② 30+ 数据集结论为作者自报，且评测集与训练语料的重叠争议**本文未解决**；③ 未核到正式会场 ⇒ 🚫 不写 ICML。 |

首次收录: 2026-11-13（第二十轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom；OpenAlex `200`）

---

## 78. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning

| 字段 | 内容 |
|:--|:--|
| 标题 | DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning |
| 作者（前 3） | **DeepSeek-AI**（机构署名）· **Daya Guo** · **Dejian Yang**（et al.，arXiv `v2` 列 **200** 位作者；OpenAlex 记 **194** 位，差异为机构署名条目计法不同） |
| 年份 | **2025**（arXiv 首次提交 **2025-01-22T15:19:35Z**，`v2`） |
| 会议 / 期刊 | **Nature 2025**（正式版 *DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning*，**645(8081):633–638**，DOI `10.1038/s41586-025-09422-z`，OpenAlex `type=article`） |
| 被引数 | **16,824**（OpenAlex，Nature 记录 DOI `10.1038/s41586-025-09422-z`，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2501.12948> ｜ 期刊版 DOI `10.1038/s41586-025-09422-z` |
| 一句话贡献 | 摘要原文要点：证明**纯强化学习**即可「激励」出 LLM 的推理能力，**无需人工标注的推理轨迹**；训练中出现**自我反思、验证、动态策略调整**等高级推理模式；在数学、编程竞赛、STEM 等**可验证任务**上优于用人类示范做常规监督训练的对照模型；这些涌现模式还可**系统性地迁移去增强小模型**。 |
| 与我们工作的关系 | **zhulong（后训练路线的第二条腿）**：R1 把「推理来自 RL」与「推理来自 SFT 蒸馏」摆成两条可比较的路；<b>动作</b>：消融表里设「同基座、同 token 预算」的 RL-only vs SFT 对照，并把**可验证性**（答案能否自动判）作为选题前提；<b>预注册判据</b>：若某任务无法给出确定性验证器（只能 LLM 当裁判），该任务不进入 RL 训练集，只作评测。<br>**harness（可验证任务是前提）**：其结论成立的前提是「奖励可自动判对错」——这正是 harness 线的核心资产；<b>动作</b>：把判分器覆盖率当作 RL 可做性的**门禁指标**，先扩验证器再谈 RL。<br>**data（拒绝采样与冷启动）**：摘要只讲机制不讲配方 ⇒ 我们只能引「机制成立」，**不能引具体超参**（未在摘要给出）。<br>**pretrain（规模对照）**：其基座规模与我们 2B 差两个量级 ⇒ 迁移时须重做「RL 在 2B 上是否仍有增益」的最小实验，🚫 不默认成立。<b>风险</b>：① 摘要**无具体数字**，本表不写任何准确率；② 16,824 引用中大量为二手讨论；③ 「涌现」属作者表述，复现争议需自行验证。 |

首次收录: 2026-11-13（第二十轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：200 作者、首发时间已核；OpenAlex Nature 记录 `200`）

---

## 79. DRAMsim3: A Cycle-Accurate, Thermal-Capable DRAM Simulator

| 字段 | 内容 |
|:--|:--|
| 标题 | DRAMsim3: A Cycle-Accurate, Thermal-Capable DRAM Simulator |
| 作者（前 3） | **Shang Li** · **Zhiyuan Yang** · **Dhiraj Reddy**（et al.，共 **5** 位：+ **Ankur Srivastava**、**Bruce Jacob**；University of Maryland） |
| 年份 | **2020**（IEEE Computer Architecture Letters **19(2):106–109**） |
| 会议 / 期刊 | **IEEE Computer Architecture Letters**（DOI `10.1109/LCA.2020.2973991`；OpenAlex `type=article`） |
| 被引数 | **372**（OpenAlex，查询日 **2026-11-13**；⚠️ **&lt; 500** ⇒ 按「方法论常青 / 工具基座」收录，🚫 不以高引为由） |
| arXiv / DOI | **无 arXiv 版本** ⇒ <https://doi.org/10.1109/LCA.2020.2973991> |
| 一句话贡献 | 摘要原文要点：DRAM 技术在快速演进（3D 堆叠、CPU-DRAM 同片集成），而**精确仿真工具没跟上**，尤其缺 3D DRAM 建模；本文给出**周期精确、经校验**的 DRAM 模拟器 DRAMsim3，作者称其在现有周期精确模拟器中**仿真性能与功能集最好**，且是**首个同时提供运行时热建模**的 DRAM 模拟器。 |
| 与我们工作的关系 | **zhulong（内存成本口径的固定尺）**：做「带宽受限 vs 计算受限」判断时，需要一个**版本冻结**的周期精确模拟器当尺子；<b>动作</b>：把 DRAMsim3 的配置（器件型号 / 通道数 / 时序参数）写成配置文件入仓并钉 commit，所有内存成本数字标注该配置版本；<b>预注册判据</b>：任何「内存侧优化」主张须给出同配置下 **带宽 / 能耗 / 尾延迟**三项，缺一项不算通过。<br>**harness（复现性 / 反「静默漂移」）**：模拟器配置是典型的**隐性变量** —— 换一个时序参数就能让结论翻转；<b>动作</b>：把「模拟器配置哈希」纳入实验元数据，评测报告缺哈希即视为不可复现（照抄 GAIA 的「固定不变量」思路）。<br>**designflow（保真度分层）**：周期精确模拟属「高保真但慢」，与我们 L1–L5 保真度分级里的高层对应；<b>动作</b>：把 DRAMsim3 定为**L4 级**参照（真值工具），agent 生成的快速代理模型只在 L2–L3 使用并须对 L4 抽样校准。<br>**方法论迁移（我们的观察）**：「工具没跟上硬件」是存储域的长期结构性问题 —— 对我们的启示是**评测工具本身要有版本与校准记录**，否则「快」会掩盖「错」。<b>风险</b>：① 作者自报「最好 / 首个」，本线未复现；② 2020 年的器件覆盖（HBM2/3 等）需按当前工艺重核；③ 被引 372，属工具类引用，**不代表方法论地位等同千引论文**。 |

首次收录: 2026-11-13（第二十轮）｜ 状态: 元数据已核验（OpenAlex DOI 直查 `200`，作者 5 位、卷期页码已核；**无 arXiv ⇒ 如实标注**）；同轮已向作者 Ankur Srivastava 发请教信

---


## 80. QLoRA: Efficient Finetuning of Quantized LLMs

| 字段 | 内容 |
|:--|:--|
| 标题 | QLoRA: Efficient Finetuning of Quantized LLMs |
| 作者（前 3） | **Tim Dettmers** · **Artidoro Pagnoni** · **Ari Holtzman**（et al.，共 **4** 位：+ **Luke Zettlemoyer**） |
| 年份 | **2023**（arXiv 首次提交 **2023-05-23T17:50:33Z**，`v1`） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `type=conference-paper`，DOI `10.52202/075280-0441`，pp. 10088–10115） |
| 被引数 | **4,052**（OpenAlex，DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.14314> ｜ 会场 DOI `10.52202/075280-0441` |
| 一句话贡献 | 摘要原文要点：**冻结 4-bit 量化基座、只对 LoRA 适配器反传梯度**，使 **65B 模型能在单张 48GB GPU 上微调且保持 16-bit 全量微调的任务性能**；三个省显存件为 **(a) 4-bit NormalFloat（NF4，对正态权重信息论最优）**、**(b) double quantization（量化量化常数，进一步降平均占用）**、**(c) paged optimizers（应对显存尖峰）**；最佳模型族 **Guanaco 在 Vicuna 基准上达到 ChatGPT 的 99.3%**，单卡微调仅 **24 小时**；共微调 **1,000+** 模型，覆盖 **8** 个指令集与 LLaMA / T5 多尺度；并称 **GPT-4 评测是廉价合理的人评替代**、**当前 chatbot 基准不可信**。 |
| 与我们工作的关系 | **pretrain（单卡 SFT 配方的直接对照）**：BaiZe 2B 的域内微调要回答「4-bit 基座 + 适配器」是否够用；<b>动作</b>：同数据、同步数跑 `16-bit LoRA` / `NF4 + LoRA` / `NF4 + double-quant + paged` 三臂，固定随机种子与 rank；<b>预注册判据</b>：三臂在下游 EDA 任务上的差距 &lt; 1 个绝对点才允许把 4-bit 路线用于常规实验，否则只在显存不足时启用。<br>**zhulong（成本口径）**：省显存 ≠ 省时间 —— 摘要只给「24 小时单卡」这一条，<b>动作</b>：把「峰值显存 / 每步耗时 / 可跑的最大 batch」三项并列记账，禁止只报显存；<b>判据</b>：若 4-bit 路径吞吐下降 &gt; 30%，则不作为成本优化项，只作为「能跑起来」的兜底。<br>**harness（评测口径）**：文中明确「**benchmark 不可信**」与「GPT-4 可替代人评」两条主张都属**作者观察**；<b>动作</b>：我们的判分仍以确定性验证器为主，LLM 裁判只作辅助并须报人评抽样一致率；评测对象须写明是**合并/反量化权重**还是**4-bit + adapter 路径**（两者不可混报）。<br>**data（小数据高质量）**：Guanaco 的核心经验是「**小的高质量数据集**」而非堆量；<b>动作</b>：域内 SFT 先做 5k / 20k / 50k 三档规模曲线，再决定是否扩数据。<b>风险</b>：① 99.3% 是 **Vicuna 基准 + 作者自评口径**，本线未复现；② 「信息论最优」是作者对 NF4 的论证，🚫 不引申为「4-bit 无损」；③ 2023 年的基座与今天不同，2B 上的结论须重测。 |

首次收录: 2026-11-13（第二十一轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：4 作者、首发时间已核；OpenAlex DOI 直查 `200`：4,052、NeurIPS 2023 页码已核）；同轮已向一作 Tim Dettmers 发请教信

---

## 81. Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer（T5）

| 字段 | 内容 |
|:--|:--|
| 标题 | Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer |
| 作者（前 3） | **Colin Raffel** · **Noam Shazeer** · **Adam Roberts**（et al.，共 **9** 位） |
| 年份 | **2020**（arXiv 首次提交 **2019-10-23T17:37:36Z**，`v4` 更新 **2023-09-19**） |
| 会议 / 期刊 | **JMLR 21(140):1–67（2020）**（OpenAlex `biblio` 字段；其 `type` 仍记 `preprint`、来源记 arXiv ⇒ 本线如实并列，不把两者混算） |
| 被引数 | **13,437**（OpenAlex arXiv DOI 记录，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1910.10683> ｜ DOI `10.48550/arXiv.1910.10683` |
| 一句话贡献 | 摘要原文要点：提出**统一框架把所有文本任务改写成 text-to-text 格式**，并在数十个语言理解任务上**系统对比预训练目标、架构、无标注数据集、迁移方式**等因素；结合规模与自建的 **C4（Colossal Clean Crawled Corpus）**，在摘要、问答、文本分类等大量基准上取得当时最好结果；**公开数据、预训练模型与代码**。 |
| 与我们工作的关系 | **pretrain（架构与目标的对照轴）**：我们的 2B 是 decoder-only；T5 给出「encoder-decoder + span corruption」这一整条对照线；<b>动作</b>：在等参数预算下只做一次小规模对照（≤500M 代理实验），把「下游样本效率」而非「loss」当判据；<b>预注册判据</b>：若 encoder-decoder 在低资源（≤1k 标注）上领先 &lt; 3 点，则 2B 主线不切换架构。<br>**data（清洗配方的历史基线）**：C4 的启发式清洗（去重、去模板、按行过滤）仍是今天网页语料管线的**最小对照**；<b>动作</b>：data 线的清洗消融必须包含「C4 式规则」这一臂，否则无法说明自研清洗的增量。<br>**harness（统一接口降低适配成本）**：把所有任务写成 text-to-text，本质是把「任务适配」从代码层挪到**数据层**；<b>动作</b>：EDA 任务（RTL 生成 / 报告抽取 / 日志归类）统一成 `输入文本 → 目标文本` 的评分接口，判分器只依赖目标串，不依赖任务专用脚本。<br>**zhulong（多任务消融的记账）**：其系统对比表的组织方式（目标 × 架构 × 数据 × 迁移）可直接借为我们的消融模板。<b>风险</b>：① 2020 年的「SOTA」已过期，🚫 不得写成当前最好；② 最大模型 11B、语料为英文网页，**跨语言与领域外推须重测**；③ JMLR 卷期取自 OpenAlex `biblio`，正式排版页码未逐页核对。 |

首次收录: 2026-11-13（第二十一轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：9 作者、首发/更新时间已核；OpenAlex `200`：13,437、`biblio` 21(140):1–67）；作者 Noam Shazeer 已在作者网（#4），本轮新增一作 Colin Raffel（未找到 X）

---

## 82. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks（RAG）

| 字段 | 内容 |
|:--|:--|
| 标题 | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks |
| 作者（前 3） | **Patrick Lewis** · **Ethan Perez** · **Aleksandra Piktus**（et al.，共 **12** 位） |
| 年份 | **2020**（arXiv 首次提交 **2020-05-22T21:34:34Z**，`v4` 更新 **2021-04-12**） |
| 会议 / 期刊 | **NeurIPS 2020**（arXiv `comment` 原文 `Accepted at NeurIPS 2020`；OpenAlex 记录为 `preprint`、**无会场 DOI** ⇒ 不写 DOI） |
| 被引数 | **6,188**（OpenAlex arXiv DOI 记录，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2005.11401> ｜ DOI `10.48550/arXiv.2005.11401` |
| 一句话贡献 | 摘要原文要点：把**参数化记忆（预训练 seq2seq）**与**非参数化记忆（Wikipedia 稠密向量索引 + 预训练神经检索器）**结合，给出通用 RAG 微调配方；比较两种形式 —— **整段生成共用同一批检索段落** vs **逐 token 可用不同段落**；在多个知识密集型任务上微调评测，在 **3 个开放域 QA** 上取得当时最好结果，超过纯参数化 seq2seq 与任务专用 retrieve-and-extract 架构；生成侧比纯参数基线**更具体、更多样、更符合事实**。 |
| 与我们工作的关系 | **harness（工具与检索的接口范式）**：RAG 把「知识」外置成可替换索引，等于给 harness 一个**不改模型即可更新知识**的通道；<b>动作</b>：在 EDA agent 里把「规格 / 工艺文档 / 既往 issue」建成独立索引，检索器与生成器分开评测（命中率 / 引用正确率 / 端到端通过率三层）；<b>预注册判据</b>：若检索层 Recall@k 提升但端到端通过率不升，判定瓶颈在生成而非检索，不再扩索引。<br>**data（非参数化 vs 参数化）**：把「世界知识」放进参数还是索引，是数据线的**成本选择题**；<b>动作</b>：对更新频繁的文档（工具版本说明、PDK 规则）默认走索引，不进入预训练语料，避免「训完就过期」。<br>**zhulong（成本口径）**：索引规模、检索延迟、上下文长度三者互相牵制；<b>动作</b>：报 RAG 收益时必须同时报 **每查询 token 增量与 p95 延迟**，否则视为不完整。<br>**pretrain（间接）**：摘要未给数据配比与训练细节 ⇒ 只可引「范式成立」，🚫 不引超参。<b>风险</b>：① 2020 年的 Wikipedia 索引与今天的网页环境差异大；② 三种 QA 基准的「SOTA」已过期；③ 「更符合事实」为作者评测结论，非普遍保证，需自带判分复核。 |

首次收录: 2026-11-13（第二十一轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：12 作者、首发/更新时间已核；OpenAlex `200`：6,188；会场仅据 arXiv `comment`，未核到会场 DOI ⇒ 如实标注）；本轮新增作者 Patrick Lewis（X `@PSH_Lewis` 已核验；主页邮箱为模板占位 ⇒ 不发信）

---

## 83. Toolformer: Language Models Can Teach Themselves to Use Tools

| 字段 | 内容 |
|:--|:--|
| 标题 | Toolformer: Language Models Can Teach Themselves to Use Tools |
| 作者（前 3） | **Timo Schick** · **Jane Dwivedi-Yu** · **Roberto Dessì**（et al.，共 **8** 位） |
| 年份 | **2023**（arXiv 首次提交 **2023-02-09T16:49:57Z**，`v1`） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `type=conference-paper`，DOI `10.52202/075280-2997`，pp. 68539–68551） |
| 被引数 | **3,245**（OpenAlex，DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2302.04761> ｜ 会场 DOI `10.52202/075280-2997` |
| 一句话贡献 | 摘要原文要点：让语言模型**以自监督方式自学调用外部工具** —— 自己决定**调用哪个 API、何时调用、传什么参数、如何把结果并入后续 token 预测**，每个 API 只需**少量示例**；接入计算器、问答系统、**两个搜索引擎**、翻译系统、日历等工具后，在多种下游任务上**零样本性能显著提升，常可与更大模型竞争，且不牺牲核心语言建模能力**。 |
| 与我们工作的关系 | **harness（工具调用的训练范式）**：agent 的工具能力可以**后训练注入**，不必全靠预训练；<b>动作</b>：为 EDA 工具集（综合 / 仿真 / 时序报告解析）各写 5–10 条示例，跑一版「自监督生成调用数据 → 过滤 → 微调」的小实验，与「纯 prompt 提示工具」对照；<b>预注册判据</b>：若自动生成的调用数据经过滤后，端到端任务通过率提升 &lt; 2 点，则回到人工示例路线。<br>**data（自举数据的质量控制）**：Toolformer 的关键不是「会不会调」，而是**过滤准则**（调用是否降低 loss）；<b>动作</b>：data 线把「工具调用样本的保留判据」写成可复算脚本并入 manifest，禁止手工挑样本后宣称自动。<br>**zhulong（小模型 + 工具）**：与我们的 2B 定位高度一致 —— 用工具补能力缺口而不是盲目放大参数；<b>动作</b>：消融里固定基座，只比较「工具集大小 / 调用轮数」，把参数规模当控制变量。<br>**pretrain（边界）**：本文属**后训练/推理期**方案，🚫 不可据此改动预训练目标。<b>风险</b>：① 2023 年的 API 集合固定（无代码执行、无现代检索 API），迁移需重选工具；② 「常可竞争更大模型」为作者在特定任务上的观察，非普遍结论；③ 自监督过滤阈值未在摘要给出 ⇒ 不引具体数值。 |

首次收录: 2026-11-13（第二十一轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：8 作者、首发时间已核；OpenAlex DOI 直查 `200`：3,245、NeurIPS 2023 页码已核）；本轮新增作者 Timo Schick（X `@timo_schick` 经本人主页链接 + X 页双源；主页无邮箱 ⇒ 不发信）

---

## 84. Distilling the Knowledge in a Neural Network（知识蒸馏的源头）

| 字段 | 内容 |
|:--|:--|
| 标题 | Distilling the Knowledge in a Neural Network |
| 作者（前 3） | **Geoffrey Hinton** · **Oriol Vinyals** · **Jeff Dean**（共 **3** 位） |
| 年份 | **2015**（arXiv 首次提交 **2015-03-09T15:44:49Z**，`v1`，无后续版本） |
| 会议 / 期刊 | **NIPS 2014 Deep Learning Workshop**（arXiv `comment` 原文 `NIPS 2014 Deep Learning Workshop`）；OpenAlex `type=preprint`、无会场 DOI ⇒ **不写会场 DOI** |
| 被引数 | **26,232**（OpenAlex arXiv DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1503.02531> ｜ DOI `10.48550/arXiv.1503.02531` |
| 一句话贡献 | 摘要原文要点：把**集成模型的知识压进单个模型**（部署便宜），核心技巧是用**带温度的软目标**训练学生模型，并在 MNIST 上给出「意外」结果；另提出由**若干全量模型 + 多个 specialist 模型**组成的集成 —— specialist 只负责区分全量模型易混淆的细粒度类别，且**可并行快速训练**（明确不同于 mixture of experts）。 |
| 与我们工作的关系 | **pretrain（教师规模 vs 蒸馏时长的预算分配）**：我们若用大模型产出软标签训练 2B 学生，关键变量是「教师更大」还是「蒸馏更久」；<b>动作</b>：固定学生与 token 预算，做「教师 2B / 8B」×「蒸馏 1× / 3× 步数」2×2 小实验；<b>预注册判据</b>：若 8B 教师在域内留出集上领先 2B 教师 &lt; 1.5 点，则不再为蒸馏扩大教师。<br>**data（软标签作为数据资产）**：软目标是**可复用的数据层产物**（一次教师前向，多次学生训练）；<b>动作</b>：把软标签与原始文本分开存、单独记 manifest（教师版本 / 温度 / 生成日期），禁止把「用软标签训过的学生」和「纯硬标签学生」混在同一张表比较。<br>**zhulong（成本口径）**：蒸馏的收益必须换算成**每 token 成本**，否则等于用更大教师换指标；<b>动作</b>：报告里并列「学生推理成本」与「教师离线生成成本」。<br>**harness（复现口径）**：本文的评测是分类/声学模型，🚫 不能直接套到生成式判分；若要移植，先在 harness 里固定解码参数再比。<b>风险</b>：① 2015 年的实验规模（MNIST / 商用声学模型）与今天的 LLM 差异极大，🚫 不得当作「2B 蒸馏有效」的证据；② 温度 T 的最优值随教师/学生容量比变化，摘要未给通用规则；③ 「surprising results on MNIST」为作者措辞，本线未复现。 |

首次收录: 2026-11-13（第二十二轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + `application/atom+xml`：3 作者、首发时间已核；OpenAlex arXiv DOI 直查 `200`：26,232、`type=preprint`）；作者 Geoffrey Hinton **已发信**（18:05:17，英文 186 词，邮箱取自本人当前主页）、Jeff Dean X 已核验

---

## 85. GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

| 字段 | 内容 |
|:--|:--|
| 标题 | GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints |
| 作者（前 3） | **Joshua Ainslie** · **James Lee-Thorp** · **Michiel de Jong**（et al.，共 **6** 位） |
| 年份 | **2023**（arXiv 首次提交 **2023-05-22T17:16:38Z**，`v3` 更新 **2023-12-23**） |
| 会议 / 期刊 | **EMNLP 2023**（arXiv `comment` 原文 `Accepted at EMNLP 2023`；OpenAlex `type=conference-paper`，DOI `10.18653/v1/2023.emnlp-main.298`，pp. 4895–4901） |
| 被引数 | **1,522**（OpenAlex，DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.13245> ｜ 会场 DOI `10.18653/v1/2023.emnlp-main.298` |
| 一句话贡献 | 摘要原文要点：① 给出把已有 **multi-head 检查点「uptrain」成 MQA** 的配方，只需**原预训练算力的 5%**；② 提出 **GQA（grouped-query attention）** —— KV 头数取「多于 1、少于 query 头数」的中间值；实测 uptrain 后的 GQA **质量接近 MHA、速度接近 MQA**。 |
| 与我们工作的关系 | **zhulong（KV cache 与解码成本的最小改动路径）**：GQA 是**不改架构、只改 KV 头数**的降本杠杆，比换 attention 变体风险低；<b>动作</b>：在 2B 上做「MHA / GQA-8 / GQA-4 / MQA」四臂，固定 token 预算，记录**质量（域内留出集）/ KV 显存 / 解码 tokens·s⁻¹** 三列；<b>预注册判据</b>：若 GQA-8 相对 MHA 质量差 &lt; 1 点且 KV 显存下降 ≥ 40%，则把 GQA-8 设为默认，MQA 只在极限吞吐场景启用。<br>**pretrain（uptrain 的算力口径）**：本文的 5% 是**相对原预训练算力**，不是绝对步数；<b>动作</b>：若我们的 2B 已训到中途要改 KV 头数，先按「5% 预算」预注册再跑，避免把 uptrain 成本算成从零重训。<br>**harness（吞吐口径统一）**：评测服务同时报「质量」与「tokens/s」，禁止只报其中一列。<b>风险</b>：① 5% 结论基于其自有模型与语料，跨模型/跨域不保证；② 摘要未给「质量下降多少」的具体数字 ⇒ 本线不引数值；③ 2023 年的推理栈（无 paged attention 等）与现栈不同，实测须在本机重跑。 |

首次收录: 2026-11-13（第二十二轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：6 作者、首发/更新时间已核；OpenAlex DOI 直查 `200`：1,522、EMNLP 2023 页码已核）；作者 Joshua Ainslie 本轮登记（邮箱 / X 未找到，见 `AUTHORS.md`）

---


## 86. Orca: Progressive Learning from Complex Explanation Traces of GPT-4

| 字段 | 内容 |
|:--|:--|
| 标题 | Orca: Progressive Learning from Complex Explanation Traces of GPT-4 |
| 作者（前 3） | **Subhabrata Mukherjee** · **Arindam Mitra** · **Ganesh Jawahar**（et al.，共 **6** 位） |
| 年份 | **2023**（arXiv 首次提交 **2023-06-05T08:58:39Z**，`v1`） |
| 会议 / 期刊 | **arXiv 预印本（无会场）**（OpenAlex `type=preprint`、无会场 DOI ⇒ 不写 DOI） |
| 被引数 | **622**（OpenAlex arXiv DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2306.02707> ｜ DOI `10.48550/arXiv.2306.02707` |
| 一句话贡献 | 摘要原文要点：指出小模型模仿大模型时的三类问题 —— **模仿信号浅**（只学风格不学推理）、**训练数据规模小且同质**、**缺严格评测导致高估**；据此做 **Orca（13B）**：用 GPT-4 的**解释轨迹 / 逐步思考过程 / 复杂指令**为监督信号、ChatGPT 作教师辅助，配合**大规模多样模仿数据 + 采样与筛选**；摘要称在 BBH 上**超过 Vicuna-13B 100% 以上**、AGIEval **+42%**，BBH 上与 ChatGPT 持平，SAT/LSAT/GRE/GMAT 上 **4 点差距**（带优化 system message），仍落后 GPT-4。 |
| 与我们工作的关系 | **data（推理轨迹是一种数据形态，不是提示技巧）**：Orca 的核心动作是「**采什么数据、怎么筛**」；<b>动作</b>：在 EDA 域先人工写 100 条「分析 → 结论」轨迹（如时序报告读法），再用强模型扩写到 5k，按「是否含可验证中间步骤」筛一遍；<b>预注册判据</b>：若「轨迹数据」相对「答案 Only 数据」在域内留出题上提升 &lt; 3 点，则不扩写，转去补人工种子。<br>**harness（防止「学风格」的评测设计）**：本文点名的失败模式正是我们的风险 —— 模型学会了报告格式却没学会推理；<b>动作</b>：判分器必须包含**中间产物检查**（如关键路径是否点对），不能只看最终字符串。<br>**zhulong（渐进式训练的顺序）**：先大量通用模仿、再域内精调的顺序可作消融轴。<b>风险</b>：① 用 GPT-4 输出作训练信号涉及**服务条款与数据来源合规**，本线不据此建议任何具体商用路径；② 摘要数字（100% / 42% / 4 点）均为**作者自报**，未复现；③ 13B 与我们的 2B 规模差 6.5 倍，结论不可直接外推。 |

首次收录: 2026-11-13（第二十二轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：6 作者、首发时间已核；OpenAlex `200`：622、`type=preprint`）；作者 Subhabrata Mukherjee 本轮**未找到**可核邮箱 / X（MSR 个人页 `404`）⇒ 不发信

---

## 87. Mistral 7B

| 字段 | 内容 |
|:--|:--|
| 标题 | Mistral 7B |
| 作者（前 3） | **Albert Q. Jiang** · **Alexandre Sablayrolles** · **Arthur Mensch**（et al.，共 **18** 位） |
| 年份 | **2023**（arXiv 首次提交 **2023-10-10T17:54:58Z**，`v1`） |
| 会议 / 期刊 | **arXiv 预印本（技术报告）**（arXiv `comment` 原文 `Models and code are available at https://mistral.ai/news/announcing-mistral-7b/`；OpenAlex `type=preprint`） |
| 被引数 | **10,625**（OpenAlex arXiv DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2310.06825> ｜ DOI `10.48550/arXiv.2310.06825` |
| 一句话贡献 | 摘要原文要点：发布 **Mistral 7B v0.1**（7B，Apache 2.0），摘要称**在所有评测基准上超过 Llama 2 13B**、在推理/数学/代码上超过 **Llama 1 34B**；架构上用 **GQA** 加速推理、用 **sliding window attention（SWA）**以更低成本处理任意长序列；另提供指令微调版 **Mistral 7B – Instruct**，摘要称在人工与自动评测上均超过 **Llama 2 13B – Chat**。 |
| 与我们工作的关系 | **pretrain（「小模型靠配方胜过更大模型」的当代证据）**：7B 超 13B 靠的是**数据 + GQA + SWA** 的组合，而不是参数；<b>动作</b>：把 SWA 窗口长度作为 2B 的一个预注册消融轴（如 4K / 8K / 16K），固定总 token 预算，比较「同等显存下的有效上下文长度」与域内任务通过率；<b>预注册判据</b>：若 SWA 在需要我们最长文档（如整份时序报告）的任务上掉点 &gt; 2 点，则只作推理期选项、不进预训练默认配置。<br>**zhulong（开源许可与成本基线）**：Apache 2.0 + 7B 是「可自托管对照基线」的常见选择；<b>动作</b>：成本表里加一行「同机部署 7B 开源模型」的 tokens/s 与显存占用，作为 2B 自研模型的参照。<br>**data（未公开的部分要标出来）**：本文**未披露训练数据配比**；<b>动作</b>：引用其效果时🚫 不得倒推出「数据配方」，只能记「配方未公开」。<b>风险</b>：① 全部对比数字为**作者自报**，且对比对象是**当时**的 Llama 版本；② 无数据/训练细节 ⇒ 不可复现；③ GQA 与 SWA 的贡献在文中未做单项拆分消融（摘要层面）。 |

首次收录: 2026-11-13（第二十二轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：18 作者、首发时间已核；OpenAlex `200`：10,625）；三作 Arthur Mensch 已在作者网（#8），本轮**补上 X `@arthurmensch`**（bio `Co-founder and CEO @MistralAI`）⇒ 状态由「未找到 X」更正为「已核验」

---


## 88. An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale（ViT）

| 字段 | 内容 |
|:--|:--|
| 标题 | An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale |
| 作者（前 3） | **Alexey Dosovitskiy** · **Lucas Beyer** · **Alexander Kolesnikov**（et al.，共 **12** 位） |
| 年份 | **2020**（arXiv 首次提交 **2020-10-22T17:55:59Z**，`v1`；`v2` 2021-06-03） |
| 会议 / 期刊 | **ICLR 2021**（arXiv `comment` 原文写明 `ICLR camera-ready version…`；OpenAlex 记 arXiv 版 `type=preprint`，未另记会场 DOI） |
| 被引数 | **51,264**（OpenAlex arXiv DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2010.11929> ｜ DOI `10.48550/arXiv.2010.11929` |
| 一句话贡献 | 摘要原文要点：不必依赖 CNN —— 把图像切成 **16×16 patch 序列**、直接喂标准 Transformer（ViT），在**大规模预训练**后迁移到 ImageNet / CIFAR-100 / VTAB 等中小基准，取得与当时最好 CNN 相当或更好的结果，且训练所需算力显著更少。 |
| 与我们工作的关系 | **vision（视觉塔的「token 化」基线，直接）**：ViT 把「分辨率 × patch 大小」变成「视觉 token 数」，这正是我们工业图像（版图 / SEM / 波形）进 2B 主干时的成本开关。<b>动作</b>：预注册 `patch ∈ {8, 14, 16}` × `输入边长 ∈ {224, 448}` 的 3×2 对照，**固定视觉 token 总预算**（超出则降 batch），只比较域内 held-out 的缺陷分类 / 线宽回归。<b>预注册判据</b>：只有「更小 patch + 更高分辨率」在 held-out 新图层上绝对提升 ≥ 2 点，才接受其翻倍的视觉算力；否则按 16×16 基线。<br>**pretrain（预训练规模 > 归纳偏置）**：摘要的核心结论是「数据够大时，纯 Transformer 不需要卷积先验」；<b>动作</b>：视觉塔选型表里把「预训练数据规模」单列一列，🚫 不得把「架构更好」与「预训练数据更多」混成一个结论。<br>**data（域内数据少时的迁移口径）**：ViT 的强项建立在**大规模（自然图像）预训练**上，而我们的域内标注远小于此；<b>动作</b>：data 线记录每个视觉实验的 `pretrain_corpus` 与 `in-domain labels` 两个数，作为可复现的最小元数据。<br>**风险**：① 论文的基准是自然图像分类，🚫 不能把 ImageNet 的提升直接外推到版图 / SEM 缺陷；② 「算力更少」是与 2019–2020 年的 CNN 训练口径比，不是与今天的配方比；③ 16×16 在 224 输入下只有 196 个 token，高分辨率工业图直接套用会丢细节。 |

首次收录: 2026-11-13（第二十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**12** 作者、首发时间已核；OpenAlex `200`：**51,264**）；二作 Lucas Beyer 本轮进作者网（#94，`@giffmana`）

---

## 89. DINOv2: Learning Robust Visual Features without Supervision

| 字段 | 内容 |
|:--|:--|
| 标题 | DINOv2: Learning Robust Visual Features without Supervision |
| 作者（前 3） | **Maxime Oquab** · **Timothée Darcet** · **Théo Moutakanni**（et al.，共 **26** 位） |
| 年份 | **2023**（arXiv 首次提交 **2023-04-14T15:12:19Z**，`v1`；`v2` 2024-02-02） |
| 会议 / 期刊 | **arXiv 预印本**（无 `journal_ref` / `comment`；OpenAlex 记 `type=preprint`，本轮**未核到会场 DOI** ⇒ 不写会议） |
| 被引数 | **7,783**（OpenAlex arXiv DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2304.07193> ｜ DOI `10.48550/arXiv.2304.07193` |
| 一句话贡献 | 摘要原文要点：**自监督**预训练也能产出「通用视觉特征」—— 前提是**用自动流水线构建多样、经过筛选（curated）的图像数据**，并把训练在数据与模型规模上放大（训练细节多为加速 / 稳定化）；作者训练 **1B 参数 ViT** 再**蒸馏**成一系列小模型，摘要称在图像级与像素级多数基准上超过当时最好的通用特征 **OpenCLIP**。 |
| 与我们工作的关系 | **vision（无标注工业图，直接）**：我们的缺陷 / 版图样本标注贵、类别长尾，DINOv2 的「无监督通用特征」正好是**先冻结当基线**的路线。<b>动作</b>：视觉线先跑「冻结 DINOv2 特征 + 线性探针」作为 held-out 基线，再决定是否自训编码器。<b>预注册判据</b>：若冻结特征在域内 held-out 上距全量微调 ≤ 2 个绝对点，则本期**不投入**自监督预训练算力，把预算让给数据清洗。<br>**data（curated > uncurated）**：论文把「自动筛选流水线」当作与模型同等重要的贡献；<b>动作</b>：data 线做一组小规模对照 —— 同一图像池「按规则筛选 vs 全量」，固定下游探针与预算，检验筛选是否同样带来增益。<br>**harness（固定冻结基线）**：冻结特征 + 线性探针是**低成本、可复现**的评测行，适合放进 harness 作为「视觉能力地板」。<b>动作</b>：评测表新增一行 `frozen_dinov2_linear_probe`，固定权重版本与预处理，禁止随任务调参。<br>**designflow（L1–L2 保真度）**：图像级缺陷 / 版图截图分类可先复用该特征；<b>动作</b>：L1–L2 任务先以冻结特征跑通判分链路，再换成自研编码器对照。<br>**风险**：① 训练语料是自然图像，SEM / 版图属**分布外**，零样本结论不可直接引用；② 摘要只给「多数基准超过 OpenCLIP」的定性结论，**无逐项数字**；③ 1B 教师 → 小模型的蒸馏配方未在摘要给出，复现需读全文与代码。 |

首次收录: 2026-11-13（第二十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**26** 作者、首发时间已核；OpenAlex `200`：**7,783**）；一作 Maxime Oquab 本轮**未找到可核验 X / 邮箱** ⇒ 未进作者网

---

## 90. WebArena: A Realistic Web Environment for Building Autonomous Agents

| 字段 | 内容 |
|:--|:--|
| 标题 | WebArena: A Realistic Web Environment for Building Autonomous Agents |
| 作者（前 3） | **Shuyan Zhou** · **Frank F. Xu** · **Hao Zhu**（et al.，共 **12** 位；末位 **Graham Neubig**） |
| 年份 | **2023**（arXiv 首次提交 **2023-07-25T22:59:32Z**，`v1`；`v4` 2024-04-16） |
| 会议 / 期刊 | **arXiv 预印本**（`comment` 只给 `webarena.dev` 复现资源，未写会场；本轮**未核到会场 DOI** ⇒ 不写会议） |
| 被引数 | **1,438**（OpenAlex arXiv DOI `10.48550/arxiv.2307.13854` 直查，查询日 **2026-11-13**；⚠️ **该记录标题仍是旧标题 `Autonomous Tester Agent Benchmark`**，计数按 DOI 归并 ⇒ 引用时须连同此注记；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2307.13854> ｜ DOI `10.48550/arXiv.2307.13854` |
| 一句话贡献 | 摘要原文要点：搭一个**高保真、可复现**的 web 环境 —— 四个常见域（电商 / 社交论坛 / 协作软件开发 / 内容管理）的**功能完整站点**，外加地图类工具与用户手册等外部知识；基准题**按任务完成的功能正确性判分**，题目多样、长程；摘要报告最好的 GPT-4 agent **端到端成功率 14.41%**，远低于人类 **78.24%**。 |
| 与我们工作的关系 | **harness（判分范式，直接）**：WebArena 用「**功能正确性 / 终态判定**」而不是文本相似度，这正是 EDA agent 需要的口径（网表、时序报告、DRC 日志是否真的对）。<b>动作</b>：harness 的判分表把每个任务写成「终态检查函数 + 允许的执行副作用」，文本输出只作日志不作分数；<b>预注册判据</b>：若某任务的终态检查无法写成确定性函数，则该题降级为人工评审，🚫 不进自动榜。<br>**zhulong（长程任务的现实基线）**：14.41% vs 78.24% 说明「多步、带工具、状态会变」的任务远未解决；<b>动作</b>：zhulong 的闭环评测拆「单步正确率 / 10 步内完成率 / 全任务成功率」三档，🚫 只报最后一档会掩盖失败模式。<br>**designflow（造题）**：四域自托管 + 统一重置 =「题目冻结、环境冻结」；<b>动作</b>：designflow 的 L3–L5 题面附 `env_image_digest`、`reset_protocol`、`n_trials` 三列，缺一列不算可复现。<br>**data（不做数据泄漏）**：环境自托管使「题目答案」可被 agent 读到；<b>动作</b>：我们造题时把 ground-truth 终态放在 agent 不可读的判分容器内，并记录一次泄漏自检。<br>**风险**：① 动作空间是浏览器 DOM / a11y 树，与我们 CLI / 工具调用差异大，🚫 不可照搬动作设计；② 14.41% 是 2023 年 GPT-4 口径、单次运行成功率，未给 `pass^k`；③ OpenAlex 记录标题异常，引用被引数时必须注明。 |

首次收录: 2026-11-13（第二十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**12** 作者、首发时间已核；OpenAlex `200`：**1,438**，标题旧名已如实标注）；末位作者 Graham Neubig 本轮进作者网（#95，`@gneubig`，已发信）

---

## 91. In-Datacenter Performance Analysis of a Tensor Processing Unit（TPU, ISCA 2017）

| 字段 | 内容 |
|:--|:--|
| 标题 | In-Datacenter Performance Analysis of a Tensor Processing Unit |
| 作者（前 3） | **Norman P. Jouppi** · **Cliff Young** · **Nishant Patil**（et al.，共 **75** 位；第 4 作者 **David Patterson**） |
| 年份 | **2017**（arXiv 首次提交 **2017-04-16T12:07:54Z**） |
| 会议 / 期刊 | **ISCA 2017**（arXiv `comment` 原文 `To appear at the 44th International Symposium on Computer Architecture (ISCA)…`；OpenAlex 记 `ACM SIGARCH Computer Architecture News`、`type=article`） |
| 被引数 | **1,572**（OpenAlex arXiv DOI 直查，查询日 **2026-11-13**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1704.04760> ｜ DOI `10.48550/arXiv.1704.04760` |
| 一句话贡献 | 摘要原文要点：评估 2015 年起部署在数据中心的 **TPU（推理 ASIC）**—— 核心是 **65,536 个 8-bit MAC** 的矩阵乘单元（峰值 **92 TOPS**）+ **28 MiB** 软件管理片上存储；作者强调其**确定性执行模型**更匹配应用的 **99 分位响应时间**，而 CPU/GPU 的缓存、乱序、多线程等动态优化更利于平均吞吐；与同期 Haswell CPU / K80 GPU 比，平均快 **15–30×**、**TOPS/W 高 30–80×**（摘要自报）。 |
| 与我们工作的关系 | **zhulong（延迟分布 vs 平均吞吐，直接）**：TPU 的论证是「**p99 才是线上指标**」，与 LLM / agent 推理的成本讨论同构；<b>动作</b>：zhulong 的推理成本表增加 `p50 / p99 latency` 与「每任务端到端秒数」，🚫 只报 tokens/s 平均值。<b>预注册判据</b>：若某配置 p99 > 2× p50，先做调度 / 批处理优化，暂不换模型或加卡。<br>**designflow（专用硬件 vs 通用工具）**：论文的价值在「**按负载特征定制**」；对应我们的 agent 负载里最慢的一环往往是 EDA 工具（综合 / 仿真 / DRC）而非模型本身；<b>动作</b>：先测一条完整设计流程中各工具调用的耗时分布，再决定优化预算落在模型还是工具封装。<br>**harness（负载代表性）**：论文用 MLP / CNN / LSTM 代表 **95%** 的推理需求来选基准；<b>动作</b>：harness 定义我们自己的「覆盖 95% 调用量」的最小任务集，并写清选取依据与统计窗口。<br>**风险**：① 2017 年**推理-only、8-bit** 口径，🚫 不能把 15–30× 外推到今天的训练或新时代加速器；② 对比对象是同机房 Haswell / K80，属**同期同环境**对照；③ 92 TOPS / 28 MiB 是硬件规格，不代表实际利用率（摘要亦承认部分应用利用率低）。 |

首次收录: 2026-11-13（第二十三轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**75** 作者、首发时间已核；OpenAlex `200`：**1,572**）；第 4 作者 David A. Patterson 已在作者网（#74，此前 IRAM 轮已发信）

---

## 92. Proximal Policy Optimization Algorithms

| 字段 | 内容 |
|:--|:--|
| 标题 | Proximal Policy Optimization Algorithms |
| 作者（前 3） | **John Schulman** · **Filip Wolski** · **Prafulla Dhariwal**（et al.，共 **5** 位，含 Alec Radford、Diederik Kingma） |
| 年份 | **2017**（arXiv 首次提交 **2017-07-20T02:32:33Z**，`v1`；`v2` 2017-08-28） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`；arXiv `comment` 为空，**未核到会场 DOI** ⇒ 不写会议） |
| 被引数 | **31,326**（OpenAlex arXiv DOI `10.48550/arxiv.1707.06347` 直查，查询日 **2026-11-14**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1707.06347> ｜ DOI `10.48550/arXiv.1707.06347` |
| 一句话贡献 | 摘要原文要点：给出一族策略梯度方法，交替「与环境交互采样」与「随机梯度上升优化代理目标」；与标准策略梯度**每个样本只做一次梯度更新**不同，新目标允许**多次小批量 epoch 更新**；作者称 PPO 具备 TRPO 的部分好处，但**更易实现、更通用、样本复杂度更好**，并在仿真机器人运动与 Atari 上优于其他在线策略梯度方法，在样本复杂度 / 实现简单 / 墙钟时间之间取得较好平衡。 |
| 与我们工作的关系 | **zhulong（RL 训练器基线，直接）**：zhulong 的消融臂要跑 RL 迭代，PPO 的**三个旋钮**（clip 比例 / 每批数据 epoch 数 / minibatch 大小）就是最先要固定下来的口径。<b>动作</b>：在启动 P2 前先做一组小网格（clip ∈ {0.1,0.2,0.3} × epoch ∈ {3,10}），只作为内部配方、**不进论文**。<b>预注册判据</b>：若三组配置的 Pass@1 差异 &lt; 2 个绝对点，则固定默认值、不再搜；差异主要来自 epoch 数 ⇒ 说明瓶颈在数据复用而非目标函数。<br>**vision（波形 RL，直接）**：vision 线用 RL 做波形参数回归，奖励已连续化；PPO 的 clip 机制决定了「奖励尺度变化时更新幅度是否失控」——<b>动作</b>：把奖励归一化方式（除以滑动标准差 vs 固定尺度）作为一臂对照，观察 rise_time / duty_cycle 的误差曲线是否出现塌陷。<br>**harness（训练与判分解耦）**：PPO 的「多 epoch 复用同批采样」意味着<b>同一条轨迹会被多次计分</b>；评测时必须用独立 rollout，不能复用训练采样。<b>动作</b>：harness 的成功率统计明确写「评测 rollout 与训练采样不共享」；缺此说明的结果不进对外对比。<br>**风险**：① 摘要只给「优于其他在线策略梯度」的定性结论，**无逐任务数字**；② 2017 年的实验环境（MuJoCo / Atari）与 LLM 的 RL 场景差异大，🚫 不能把「样本效率更好」直接外推到 token 级 RL；③ 论文未讨论 KL 约束的具体实现细节（那在 TRPO / 后续工作里）。 |

首次收录: 2026-11-14（第二十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**5** 作者、首发时间已核；OpenAlex `200`：**31,326**）；一作 John Schulman 已进作者网（`@johnschulman2`，无邮箱 ⇒ 未发信）

---

## 93. Denoising Diffusion Probabilistic Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Denoising Diffusion Probabilistic Models |
| 作者（前 3） | **Jonathan Ho** · **Ajay Jain** · **Pieter Abbeel**（共 **3** 位） |
| 年份 | **2020**（arXiv 首次提交 **2020-06-19T17:24:44Z**，`v1`；`v2` 2020-12-16） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`；arXiv `comment` 为空，**未核到会场 DOI** ⇒ 不写会议） |
| 被引数 | **11,034**（OpenAlex arXiv DOI `10.48550/arxiv.2006.11239` 直查，查询日 **2026-11-14**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2006.11239> ｜ DOI `10.48550/arXiv.2006.11239` |
| 一句话贡献 | 摘要原文要点：用扩散概率模型（受非平衡热力学启发的隐变量模型）做高质量图像合成；最佳结果来自一个**加权变分下界**，其权重由「扩散模型 ↔ 去噪分数匹配 + Langevin 动力学」的新联系导出；模型天然支持**渐进式有损解压**（可看作自回归解码的推广）；CIFAR-10 无条件生成 **IS 9.46 / FID 3.17**，256×256 LSUN 上与 ProgressiveGAN 相当。 |
| 与我们工作的关系 | **vision（合成数据，间接但明确）**：vision 线当前是「波形 → 参数」的回归任务，标注贵、长尾重；DDPM 提供的是**从分布采样**的能力，适合生成「罕见的异常波形 / 缺陷形态」。<b>动作</b>：先做三臂小对照 —— ① 纯直接回归（现状）② 扩散生成后取统计量 ③ 回归 + 扩散增广；固定数据与训练预算。<b>预注册判据</b>：若生成臂在 held-out 上**没有降低** period / rise_time / duty_cycle 的绝对误差，则本期不投入生成式路线（不因「方法新」而上）。<br>**designflow（造题 / 稀有场景）**：L4–L5 的题面需要「真实但稀缺」的设计场景；用扩散模型在**版图截图 / 波形轨迹**上做受控增广，比人工造题便宜。<b>动作</b>：增广样本必须与真实样本**分开标注来源**，且每条题面注明 `synthetic=true`。<br>**data（保真度检查）**：论文的核心是**训练目标**（加权 VLB），不是「生成得像」；我们的合成数据验收不能只看视觉相似。<b>动作</b>：沿用「关键统计量 vs 真实参照集」的对照（见同日 A 轨 CADET），把 FID 类指标降为辅助。<br>**风险**：① FID / IS 是图像指标，**不能**直接衡量 1-D 波形或版图的功能正确性；② 论文的加权重构是为自然图像调的，换到信噪比分布不同的信号需重新推导（本线已就此向三作 Abbeel 发信请教）；③ 摘要未给采样步数与推理成本，落地前须实测。 |

首次收录: 2026-11-14（第二十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**3** 作者、首发时间已核；OpenAlex `200`：**11,034**）；三作 Pieter Abbeel 已进作者网（`@pabbeel` + `pabbeel@cs.berkeley.edu`，**已发信** 2026-11-14）

---

## 94. ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

| 字段 | 内容 |
|:--|:--|
| 标题 | ZeRO: Memory Optimizations Toward Training Trillion Parameter Models |
| 作者（前 3） | **Samyam Rajbhandari** · **Jeff Rasley** · **Olatunji Ruwase**（et al.，共 **4** 位，含 Yuxiong He） |
| 年份 | **2019**（arXiv 首次提交 **2019-10-04T17:29:39Z**，`v1`；`v3` 2020-05-13） |
| 会议 / 期刊 | **SC 2020**（OpenAlex `type=conference-paper`，DOI `10.1109/sc41405.2020.00024`） |
| 被引数 | **1,432**（OpenAlex arXiv DOI `10.48550/arxiv.1910.02054` 直查，查询日 **2026-11-14**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1910.02054> ｜ DOI `10.48550/arXiv.1910.02054`；会场 DOI `10.1109/sc41405.2020.00024` |
| 一句话贡献 | 摘要原文要点：提出 **ZeRO（Zero Redundancy Optimizer）**，消除数据并行与模型并行中的**显存冗余**（优化器状态 / 梯度 / 参数分片），同时保持低通信量与高计算粒度，使模型规模可随设备数线性扩展；分析称今天硬件上可扩到 **1 万亿参数**；实测在 **400 GPU** 上训练 **&gt;100B** 参数模型，吞吐 **15 Petaflops**、超线性加速，模型规模 **8×**、可达性能 **10×**；且无需模型并行即可训练 **13B** 级模型（大于 Megatron GPT 8.3B / T5 11B）。 |
| 与我们工作的关系 | **pretrain（2B 训练的显存与并行口径，直接）**：BaiZe 是 ~2B 主干，显存瓶颈可能来自**优化器状态**（Adam 的 fp32 master weights + 动量）而非参数本身；ZeRO 的分层（stage-1 优化器状态 / stage-2 梯度 / stage-3 参数）正好给出「先分片哪一块」的优先序。<b>动作</b>：在训练配置表里新增三列 <code>zero_stage</code> / <code>opt_state_sharded</code> / <code>param_sharded</code>，任何吞吐对比必须三列齐全。<b>预注册判据</b>：若 stage-2 已能把单卡显存压到 &lt;70%，则不上 stage-3（通信开销换显存的收益递减）；若 stage-3 后 step time 上升 &gt;20%，则优先调 micro-batch 而非继续加 stage。<br>**data（吞吐预算）**：数据加载与 tokenize 吞吐必须与训练 step time 同框记录，否则「训练变快但数据供不上」会被误读成并行收益。<b>动作</b>：data 线的 shard 产出速率（tokens/s）写进同一张表。<br>**风险**：① 论文的 15 Petaflops / 8× 是 **2020 年 V100 集群**口径，🚫 不能外推到今天的卡型与互联；② 13B 与 2B 的通信/计算比不同，stage 选择的最优点会移动；③ 摘要未给「Zero-3 在长序列上的额外通信成本」。 |

首次收录: 2026-11-14（第二十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**4** 作者、首发时间已核；OpenAlex `200`：**1,432**，`conference-paper`）；4 位作者均为 Microsoft Research ⇒ 未找到可核验个人主页邮箱，本轮**未进作者网**

---

## 95. Segment Anything

| 字段 | 内容 |
|:--|:--|
| 标题 | Segment Anything |
| 作者（前 3） | **Alexander Kirillov** · **Eric Mintun** · **Nikhila Ravi**（et al.，共 **12** 位，含 Hanzi Mao） |
| 年份 | **2023**（arXiv 首次提交 **2023-04-05T17:59:46Z**，`v1`） |
| 会议 / 期刊 | **ICCV 2023**（OpenAlex `type=conference-paper`，DOI `10.1109/iccv51070.2023.00371`） |
| 被引数 | **16,904**（OpenAlex arXiv DOI `10.48550/arxiv.2304.02643` 直查，查询日 **2026-11-14**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2304.02643> ｜ DOI `10.48550/arXiv.2304.02643`；会场 DOI `10.1109/iccv51070.2023.00371` |
| 一句话贡献 | 摘要原文要点：提出 **SA 项目**（新任务 + 模型 + 数据集）；用高效模型构成**数据收集闭环**，建成当时最大的分割数据集 —— **1B+ mask、11M 张**有授权且隐私合规的图像；模型被设计成**可提示（promptable）**，从而能零样本迁移到新的图像分布与任务；作者称零样本表现常与既有全监督结果相当甚至更好，并开源 SAM 与 SA-1B。 |
| 与我们工作的关系 | **vision（缺陷 / 版图分割基线，直接）**：我们的视觉任务里「区域级」标注（缺陷区域、版图图层）比整图分类更贵；SAM 提供**先出 mask、再人工接受/拒绝**的半自动路径。<b>动作</b>：先在 held-out 缺陷图上跑「冻结 SAM + 轻量头」作为下界，固定权重版本与 prompt 策略（点 / 框）。<b>预注册判据</b>：若冻结 SAM 距全量微调 ≤ 2 个绝对点（IoU 或任务指标），则本期不自训分割编码器，把预算让给标注。<br>**data（数据引擎）**：论文真正的工程贡献是「模型辅助标注闭环」——先标一部分、训模型、用模型预标、人工只做接受/拒绝。<b>动作</b>：data 线选一个小任务试点，记录「初标接受率」与「每 100 个样本的人时」；<b>预注册判据</b>：人时节省 &lt;30% 或接受率 &lt;70% ⇒ 停试点，回到纯人工。<br>**harness（分割指标口径）**：promptable 模型的评测依赖**提示策略**，不同提示会给出不同分。<b>动作</b>：评测表固定写死 prompt 生成规则与随机种子，禁止「挑一个能过的点」。<br>**风险**：① 训练语料是自然图像，SEM / 版图属**分布外**，零样本结论不可直接引用；② 摘要只给「常与全监督相当或更好」的定性说法，**无逐项数字**；③ 1B mask 的规模对我们不现实，只能借「闭环」方法而非其规模。 |

首次收录: 2026-11-14（第二十四轮）｜ 状态: 元数据已核验（arXiv `id_list` `200` + atom：**12** 作者、首发时间已核；OpenAlex `200`：**16,904**，`conference-paper`）；一作 Alexander Kirillov 主页 `404`、候选 `@akirillov` 判非本人 ⇒ 邮箱与 X **均未找到，不登记**

---

## 96. DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models（**GRPO 出处**）

| 标题 | DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models（**GRPO 出处**） |
| 作者（前 3） | **Zhihong Shao** · **Peiyi Wang** · **Qihao Zhu**（et al.，共 **11** 位；DeepSeek-AI） |
| 年份 | **2024**（arXiv 首次提交 **2024-02-05T18:55:32Z**，现 `v3`） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`，无会场 DOI ⇒ **不写会议**） |
| 被引数 | **11,153**（OpenAlex arXiv DOI `10.48550/arxiv.2402.03300` 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2402.03300> ｜ DOI `10.48550/arXiv.2402.03300` |
| 一句话贡献 | 摘要原文要点：DeepSeekMath 7B 在 DeepSeek-Coder-Base-v1.5 7B 上**继续预训练 120B 数学相关 token**（来自 Common Crawl，混自然语言与代码数据），在**不使用外部工具与投票**的情况下于竞赛级 **MATH 得 51.7%**，64 样本自洽达 **60.9%**；作者把能力归因于两点——**精心设计的数据选择 pipeline**，以及 **GRPO（Group Relative Policy Optimization）**：PPO 的变体，在提升数学推理的同时**优化 PPO 的显存占用**（用组内相对基线替代 value model）。 |
| 与我们工作的关系 | **zhulong（RL 训练器：算法选型，直接）**：GRPO 用**同一 prompt 的一组采样**的均值/标准差作基线，**去掉 critic**，显存与超参面都更小。<b>动作</b>：在现有 PPO 基线上加一条 GRPO 对照臂，固定采样数 G ∈ {4, 8}、固定总 rollout 预算，比较「显存峰值 / 每步墙钟 / 最终成功率」。<b>预注册判据</b>：若 GRPO 在同等 rollout 预算下成功率不低于 PPO 且显存峰值下降 ≥30%，则 RL 主实验改用 GRPO、PPO 仅作消融。<br>**data（领域继续预训练）**：120B 数学 token 的「数据选择 pipeline」比模型结构更像可复用资产。<b>动作</b>：把我们的 RTL / 时序报告语料按同样三段式（召回 → 质量筛 → 配比）建档，先做 1B token 的小规模对照。<br>**pretrain（继续预训练配方）**：在 code base 上继续预训练、再 RL 的两段式，与我们 2B 的「通用 → 领域」路线同构；但摘要未给学习率 / 步数 / 配比细节 ⇒ **不可直接照搬超参**。<br>**风险**：① 51.7% 是**数学**基准，与 EDA 任务无可比性；② 论文未披露 120B token 的完整配比；③「接近 Gemini-Ultra / GPT-4」是作者 2024 年的自述，🚫 不得当作当前结论。 |

首次收录: 2026-11-14（第二十五轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；OpenAlex `200`）

---

## 97. Masked Autoencoders Are Scalable Vision Learners

| 标题 | Masked Autoencoders Are Scalable Vision Learners |
| 作者（前 3） | **Kaiming He** · **Xinlei Chen** · **Saining Xie**（et al.，共 **6** 位，另含 Yanghao Li / Piotr Dollár / Ross Girshick） |
| 年份 | **2021**（arXiv 首次提交 **2021-11-11T18:46:40Z**，现 `v3`；CVPR 2022） |
| 会议 / 期刊 | **CVPR 2022**（OpenAlex `type=conference-paper`，DOI `10.1109/cvpr52688.2022.01553`，pp. **15979–15988**） |
| 被引数 | **10,217**（OpenAlex 会场 DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2111.06377> ｜ DOI `10.48550/arXiv.2111.06377`；会场 DOI `10.1109/cvpr52688.2022.01553` |
| 一句话贡献 | 摘要原文要点：**随机遮住输入图像的 patch 并重建缺失像素**；两项核心设计——**非对称编解码器**（编码器只看可见 patch、不带 mask token，轻量解码器从 latent + mask token 重建）与**高掩码比例（如 75%）**使自监督任务「非平凡且有意义」；两者结合带来 **≥3× 训练加速**与精度提升，ViT-Huge 在**仅用 ImageNet-1K** 的方法中取得 **87.8%** 最佳精度，下游迁移优于监督预训练。 |
| 与我们工作的关系 | **vision（视觉塔预训练：直接）**：这是我们「版图 / 波形图像没有足够标签」时最省数据的一条自监督路线。<b>动作</b>：先在小规模未标注版图图像上跑 MAE 预训练（固定 ViT 尺寸与 patch 大小），再线性探测 + 轻量分割头，与「ImageNet 监督初始化」和「从零训练」三臂对照。<b>预注册判据</b>：若 MAE 初始化在 held-out 缺陷分割上的 IoU 不低于 ImageNet 监督初始化，则视觉塔默认走 MAE、把标注预算留给下游。<br>**data（无标注数据可用性）**：掩码重建不需要标签，可把历史版图 / 波形直接纳入预训练。<b>动作</b>：先统计可用无标注图像量级与分辨率分布，按 75% 掩码估算每 epoch 的 token 成本。<br>**designflow（辅助任务）**：掩码重建可作为版图 / 波形表征的辅助目标，但**须与下游判分分离**。<br>**风险**：① 75% 是**自然图像**上的经验值，窄域高冗余图像未必最优；② 87.8% 是 ImageNet-1K 分类，与 EDA 稠密任务不可直接比；③ 论文未给「小数据域」的迁移结论。 |

首次收录: 2026-11-14（第二十五轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；OpenAlex `200`）；三作 Saining Xie 的联系方式与 X 见 `AUTHORS.md`，**本轮已发信**

---

## 98. Efficiently Modeling Long Sequences with Structured State Spaces（**S4**）

| 标题 | Efficiently Modeling Long Sequences with Structured State Spaces（**S4**） |
| 作者（前 3） | **Albert Gu** · **Karan Goel** · **Christopher Ré**（共 **3** 位） |
| 年份 | **2021**（arXiv 首次提交 **2021-10-31T03:32:18Z**，现 `v3`；ICLR 2022） |
| 会议 / 期刊 | **ICLR 2022**（arXiv `comment` 原文 `ICLR 2022 (Outstanding Paper HM)`；OpenAlex 记 `preprint` ⇒ **不写会场 DOI**） |
| 被引数 | **2,741**（OpenAlex arXiv DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2111.00396> ｜ DOI `10.48550/arXiv.2111.00396` |
| 一句话贡献 | 摘要原文要点：给出 SSM 的**新参数化**——对状态矩阵 `A` 做**低秩修正**使其可稳定对角化，把 SSM 归约为 **Cauchy kernel** 的计算，从而在**保留长程建模理论优势**的同时大幅降低计算与显存；实证：**sequential CIFAR-10 91%**（无数据增广 / 辅助损失）、图像与语言建模上显著缩小与 Transformer 的差距且**生成快 60×**、**Long Range Arena 全部任务 SoTA**（含此前所有方法都失败的 **Path-X，长度 16k**）。 |
| 与我们工作的关系 | **pretrain（长序列架构对照轴：直接）**：S4 是 Mamba 的直接前身，也是「**线性时间 / 线性显存**换长上下文」这条路最早的强证据。<b>动作</b>：在 2B 规模的架构选型表里加入 SSM 轴（Transformer / 混合 / 纯 SSM），**固定 token 预算与评测集**，只比较「每 token 墙钟 / 峰值显存 / 长上下文检索精度」。<b>预注册判据</b>：若纯 SSM 在 ≥32k 上下文检索上不劣于 Transformer 且吞吐 ≥1.5×，则长上下文实验优先用混合架构；否则维持 Transformer + 位置扩展。<br>**zhulong（长轨迹建模）**：EDA 的调试 / 布线轨迹可达上万步，S4 的线性复杂度是「整条轨迹进模型」的前提。<br>**风险**：① 91% / 60× 分别来自 **sequential CIFAR-10** 与**生成**场景，🚫 不可外推到训练吞吐；② 论文未给 2B 参数规模的结论；③ 与 Mamba 的差异（选择性 / 硬件感知）须区分，不可混为一条。 |

首次收录: 2026-11-14（第二十五轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；OpenAlex `200`）；⚠️ **更正**：任务书候选写的 `2110.13985` 实为 **LSSL**（NeurIPS 2021），**S4 真 ID = `2111.00396`**

---

## 99. Mastering Diverse Domains through World Models（**DreamerV3**）

| 标题 | Mastering Diverse Domains through World Models（**DreamerV3**） |
| 作者（前 3） | **Danijar Hafner** · **Jurgis Pasukonis** · **Jimmy Ba**（et al.，共 **4** 位，另含 Timothy Lillicrap） |
| 年份 | **2023**（arXiv 首次提交 **2023-01-10T18:12:16Z**，现 `v2`；Nature 版 **2025**） |
| 会议 / 期刊 | **Nature 2025**（OpenAlex `type=article`，DOI `10.1038/s41586-025-08744-2`，**640**(8059):**647–653**） |
| 被引数 | **1,962**（OpenAlex Nature DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2301.04104> ｜ DOI `10.48550/arXiv.2301.04104`；期刊 DOI `10.1038/s41586-025-08744-2` |
| 一句话贡献 | 摘要原文要点：DreamerV3 是**单一配置**就能在 **150+ 个任务**上超过专用方法的通用算法——**学环境模型**并**在想象中改进策略**；靠**归一化、平衡与变换**等鲁棒性技术实现跨域稳定学习；开箱即用时是**首个在 Minecraft 中从零收集钻石、无需人类数据或课程**的算法。 |
| 与我们工作的关系 | **zhulong（model-based RL / 世界模型：直接）**：我们已有可调用但昂贵的 EDA 工具链，Dreamer 的「先学动力学、再在潜空间里规划」正是「少调真工具」的路线。<b>动作</b>：选一个确定性仿真器（如布线 / 时序修复），先训一个 latent dynamics 模型，比较「模型内规划 + 少量真实验证」与「纯真工具 trial-and-error」在**同样真工具调用次数**下的成功率。<b>预注册判据</b>：若同等工具调用预算下模型内规划的成功率提升 &lt;5 个百分点，则不投入世界模型，改回纯 harness 优化。<br>**vision（latent dynamics）**：其「从像素学动力学」与我们波形 / 版图观测同构，可复用 symlog / two-hot 的**跨尺度归一化**思路。<br>**designflow（仿真器规划）**：预算控制与「想象 rollout」可直接写进 L4–L5 的 agent 策略。<br>**风险**：① 150+ 任务与 Minecraft 均**非 EDA**，跨域结论不可直接引用；② Nature 版与 arXiv 版为**同一工作两版**，被引数只取 Nature 记录、🚫 不相加；③ 摘要未给「工具调用成本」口径。 |

首次收录: 2026-11-14（第二十五轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；OpenAlex `200`）；一作 Danijar Hafner 的 X 见 `AUTHORS.md`（邮箱未找到 ⇒ 不发信）

---

## 100. Adam: A Method for Stochastic Optimization

| 字段 | 内容 |
|:--|:--|
| 标题 | Adam: A Method for Stochastic Optimization |
| 作者（前 3） | **Diederik P. Kingma** · **Jimmy Ba**（共 **2** 位；arXiv 署名为 `Jimmy Ba`，OpenAlex 记 `Jimmy Lei Ba`） |
| 年份 | **2014**（arXiv 首次提交 **2014-12-22T13:54:29Z**，现 `v9`；ICLR 2015） |
| 会议 / 期刊 | **ICLR 2015**（arXiv `comment` 原文 `Published as a conference paper at the 3rd International Conference for Learning Representations, San Diego, 2015`；OpenAlex 记 `preprint`、无会场 DOI ⇒ **不写会场 DOI**） |
| 被引数 | **101,807**（OpenAlex arXiv DOI `10.48550/arxiv.1412.6980` 直查，查询日 **2026-11-14**；⚠️ OpenAlex 另有 **UvA-DARE** 仓储记录 132,527 —— **同 DOI 同工作重复记录，🚫 不相加**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1412.6980> ｜ DOI `10.48550/arXiv.1412.6980` |
| 一句话贡献 | 摘要原文要点：提出 **Adam** —— 基于**一阶梯度低阶矩的自适应估计**的随机目标优化算法；实现简单、计算高效、**显存需求小**、**对梯度对角缩放不变**，适合参数/数据规模大的问题，也适合**非平稳目标与噪声大 / 稀疏梯度**；超参有直观解释、通常几乎不需调；给出 online convex optimization 框架下与已知最优可比的 **regret bound**；并讨论基于 ∞-范数的变体 **AdaMax**。 |
| 与我们工作的关系 | **pretrain（优化器默认基线：直接）**：2B 主跑之前的对照表里，Adam(W) 是不可省的一档。<b>动作</b>：在 1B 级做 **Adam vs AdamW vs MuonClip** 三方小跑（固定 token 与 global batch），监控 `max attention logit`、loss spike 次数、最终 loss 与显存峰值。<b>预注册判据</b>：若 Adam 在等 token 下 loss 不劣于 AdamW 且 spike 次数为 0，则**只维护一套优化器配置**，不再加第二套调参面。<br>**zhulong（显存 / 超参预算）**：优化器状态是显存大头之一 ⇒ 与 ZeRO（#94）、QLoRA（#80）一起算「每卡可训参数」；RL 阶段若频繁重启训练，超参少调省时间。<br>**风险**：① 摘要给的收敛保证是 **online convex** 设定，非凸深度网络不适用（后续有非收敛反例工作，引用时须一并说明）；② 现代实践普遍改为**解耦权重衰减（AdamW）**，🚫 不可把本文配方当 2026 最佳实践；③ 101,807 与 132,527 是同一工作的双记录，只能择一。 |

首次收录: 2026-11-14（第二十六轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：2 作者、首发时间已核；OpenAlex `200`，含 authorships 机构）

---

## 101. Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift

| 字段 | 内容 |
|:--|:--|
| 标题 | Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift |
| 作者（前 3） | **Sergey Ioffe** · **Christian Szegedy**（共 **2** 位） |
| 年份 | **2015**（arXiv 首次提交 **2015-02-11T01:44:18Z**，现 `v3`；ICML 2015） |
| 会议 / 期刊 | **ICML 2015，PMLR 37:448–456**（来源：PMLR 官方页 `proceedings.mlr.press/v37/ioffe15.html` 实测 `HTTP 200` / 17,799 B，页内逐字 `PMLR 37:448-456` 与 `Proceedings of the 32nd International Conference on Machine Learning`；OpenAlex 只记 `preprint`） |
| 被引数 | **34,937**（OpenAlex arXiv DOI `10.48550/arxiv.1502.03167` 直查，查询日 **2026-11-14**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1502.03167> ｜ DOI `10.48550/arXiv.1502.03167`；会场页 <https://proceedings.mlr.press/v37/ioffe15.html> |
| 一句话贡献 | 摘要原文要点：训练时每层输入分布随前层参数变化而漂移（作者称 **internal covariate shift**），逼迫用小学习率 + 谨慎初始化，且对饱和非线性极难训练；把**归一化做进模型架构、按 mini-batch 做**后，可用**更大学习率**、**对初始化不敏感**，并有**正则效果**（某些情况下可去掉 Dropout）；在当时的 SOTA 图像分类模型上，**同样精度只需 1/14 的训练步数**，集成后 ImageNet **top-5 验证错误 4.9%**（作者自报）。 |
| 与我们工作的关系 | **pretrain（训练稳定性 / lr 预算：直接）**：我们的 2B 预训练用的是 RMSNorm/LayerNorm —— 二者**不依赖 batch 统计量**，与 BN 的假设不同，必须当作**不同机制**分别评估。<b>动作</b>：只在归一化层这一轴做对照（RMSNorm vs LayerNorm vs 前若干层 BN），其余配置全固定，记录「可用的最大学习率」与 loss 方差。<b>预注册判据</b>：若 BN 在 ≥1B 参数 / 长序列下需要 SyncBN 才能稳定（通信开销吃掉吞吐），立即排除，不再投入调参。<br>**data（batch 组成）**：BN 让结果依赖 batch 内样本组成 ⇒ 数据配比实验一旦改动 batch 采样，必须**重测**，不能沿用旧结论。<br>**风险**：① 4.9% / 14× 是 2015 年 ImageNet 口径、作者自报、未复现；② 分布式训练需跨卡同步统计量（SyncBN），成本高；③ 「有效原因是 internal covariate shift」这一解释后续有争议（有工作指出起作用的是优化景观平滑），🚫 不得把解释当机制定论。 |

首次收录: 2026-11-14（第二十六轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；OpenAlex `200`；PMLR 会场页 `200` 逐字核页码）

---

## 102. Generative Adversarial Networks

| 字段 | 内容 |
|:--|:--|
| 标题 | Generative Adversarial Networks |
| 作者（前 3） | **Ian J. Goodfellow** · **Jean Pouget-Abadie** · **Mehdi Mirza**（et al.，共 **8** 位，另含 Bing Xu / David Warde-Farley / Sherjil Ozair / Aaron Courville / Yoshua Bengio） |
| 年份 | **2014**（arXiv 首次提交 **2014-06-10T18:58:17Z**，`v1`） |
| 会议 / 期刊 | **NeurIPS 2014（NIPS 2014）**；⚠️ OpenAlex **未收录会场版**（只收 arXiv 记录）⇒ **不写会场 DOI、不写页码**，仅按学界通行会场署名记录 |
| 被引数 | **9,668**（OpenAlex arXiv DOI `10.48550/arxiv.1406.2661` 直查，查询日 **2026-11-14**；⚠️ 这是**预印本记录**，会场版被引显著更高但 OpenAlex 无该记录；S2 本轮实测 **`429 Too Many Requests`** ⇒ 不写估算值） |
| arXiv / DOI | <https://arxiv.org/abs/1406.2661> ｜ DOI `10.48550/arXiv.1406.2661` |
| 一句话贡献 | 摘要原文要点：提出用**对抗过程**估计生成模型的框架 —— 同时训练**生成器 G**（拟合数据分布）与**判别器 D**（估计样本来自真实数据而非 G 的概率），G 的训练目标是**最大化 D 犯错的概率**；在任意函数空间中存在唯一解（G 恢复训练分布、D 处处为 1/2）；G / D 用 MLP 表示时整个系统可用**反向传播**训练，**不需要马尔可夫链或展开的近似推断**；并用定性与定量实验展示生成样本的潜力。 |
| 与我们工作的关系 | **vision（生成式基线 / 合成数据：直接）**：若要用生成模型补稀有版图 / 波形样本，GAN 是「**无显式似然**」路线的起点，应与扩散模型（#93 DDPM）对照而不是二选一。<b>动作</b>：vision 线在**小规模版图 patch** 上做 GAN vs DDPM 对照，指标固定为「**下游检测精度** + 与真实分布的差异」，FID 只作参考、🚫 不作唯一判据。<b>预注册判据</b>：若 GAN 在同训练预算下下游精度落后 ≥3 点且出现模式崩塌，则合成数据只走扩散 / 回归模型。<br>**data（合成数据红线）**：合成样本必须与真实样本**分栏记账**，🚫 混入训练集不加标注。<br>**designflow（布局生成）**：EDA 里 GAN 已被用于布局 / 布线生成（如 DREAM-GAN，ISPD 2023），本文是这条线的源头。<br>**风险**：① 训练不稳定 / 模式崩塌是公认缺陷，摘要未给稳定化方案；② 9,668 只是**预印本记录**口径，引用时必须注明来源与日期；③ 摘要的「唯一解」是**理论最优性**，实际 MLP 参数化不保证达到。 |

首次收录: 2026-11-14（第二十六轮）｜ 状态: 元数据已核（arXiv `id_list` `200` + atom：8 作者、首发时间已核；OpenAlex 仅预印本记录 `200`；S2 `429` 未取）

---

## 103. DREAMPlace: Deep Learning Toolkit-Enabled GPU Acceleration for Modern VLSI Placement（DAC 2019）

| 字段 | 内容 |
|:--|:--|
| 标题 | DREAMPlace: Deep Learning Toolkit-Enabled GPU Acceleration for Modern VLSI Placement |
| 作者（前 3） | **Yibo Lin** · **Shounak Dhar** · **Wuxi Li**（et al.，共 **6** 位，含 Haoxing Mark Ren / Brucek Khailany / David Z. Pan；OpenAlex authorships 机构：前 3 + Pan 为 UT Austin，Ren / Khailany 为 NVIDIA） |
| 年份 | **2019**（DAC 2019；OpenAlex `publication_year=2019`） |
| 会议 / 期刊 | **ACM/IEEE DAC 2019**（OpenAlex `conference-paper`，DOI `10.1145/3316781.3317803`，pp. **1–6**）；扩展期刊版 **IEEE TCAD 2020**（DOI `10.1109/tcad.2020.3003843`，pp. **748–761**，OpenAlex 未给卷号 ⇒ **不写卷号**） |
| 被引数 | **177**（DAC 会场记录）；扩展版 TCAD **205** —— **同一工作两版，🚫 不相加**（OpenAlex 直查，查询日 **2026-11-14**；S2 未查） |
| arXiv / DOI | **无 arXiv**（`ti:"DREAMPlace"` 与 `all:"DREAMPlace"` 两次检索均 0 entry ⇒ 一手源 = 会议 / 期刊 DOI）｜ DAC <https://doi.org/10.1145/3316781.3317803> ｜ TCAD <https://doi.org/10.1109/tcad.2020.3003843> |
| 一句话贡献 | 摘要原文：VLSI 布局是设计收敛最重要的步骤之一；本文把**解析式布局问题等价改写为「训练一个神经网络」**，在 PyTorch 上实现并为**线长 / 密度计算**写定制 kernel ⇒ 相对当时 SOTA 的多线程 placer **RePlAce**，**全局布局加速 >30× 且质量不降**；作者认为这为「用 AI 软硬件的进步重访经典 EDA 问题」打开了方向。 |
| 与我们工作的关系 | **designflow（L4/L5 工具链与保真度：直接）**：把布局变成可微程序，正是「造题 + 可验证判分」最需要的底座 —— 目标函数显式（HPWL + 密度）、可复现、可批量跑。<b>动作</b>：把 DREAMPlace 固定版本与参数作为 **L4 的参考 placer**，对同一网表产出「参考布局」作为判分基线。<b>预注册判据</b>：若 agent 产出的布局不能在 HPWL / 合法化后指标上达到或接近 DREAMPlace 默认结果，则判分阈值定在**相对 DREAMPlace 的比值**上，而不是绝对 HPWL。<br>**zhulong（工具即环境）**：GPU placer 单次运行到秒级 ⇒ 适合放进 agent 的 rollout 循环；但必须记录两个成本旋钮（**迭代数 / 目标密度**），否则「工具调用预算」不可比。<br>**harness（成本口径）**：>30× 是**全局布局 vs RePlAce** 的口径，🚫 不可当端到端 flow 的加速比。<br>**风险**：① 加速比为作者自报，依赖硬件与版本；② 2019 年工作，后续商用 placer 与 OpenROAD 集成已变化（本项目另有 #68 OpenROAD）；③ 177 / 205 为同工作双记录，只能择一。 |

首次收录: 2026-11-14（第二十六轮）｜ 状态: 元数据 + 被引已核（OpenAlex `200` 两次：DOI 直查 + authorships；**无 arXiv 已两次检索确认**；一级作者主页 `users.ece.utexas.edu/~dpan/` `200`，已发请教信）

---

## 104. High-Resolution Image Synthesis with Latent Diffusion Models（**LDM / Stable Diffusion 的论文原型**）

| 字段 | 内容 |
|:--|:--|
| 标题 | High-Resolution Image Synthesis with Latent Diffusion Models |
| 作者（前 3） | **Robin Rombach** · **Andreas Blattmann** · **Dominik Lorenz**（et al.，共 **5** 位，另含 Patrick Esser / Björn Ommer） |
| 年份 | **2021**（arXiv 首次提交 **2021-12-20T18:55:25Z**，现 `v2` 更新于 2022-04-13；CVPR 2022） |
| 会议 / 期刊 | **CVPR 2022**（arXiv `comment` 原文即 `CVPR 2022`；OpenAlex `type=conference-paper` 记为 CVPR 系列；⚠️ **未核到会场 DOI / 页码** ⇒ 不写） |
| 被引数 | **20,670**（OpenAlex arXiv DOI `10.48550/arxiv.2112.10752` 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2112.10752> ｜ DOI `10.48550/arXiv.2112.10752` |
| 一句话贡献 | 摘要原文要点：像素空间扩散训练 / 推理代价高（常需数百 GPU 日）；本文改在**预训练自编码器的隐空间**做扩散，先由自编码器提供「感知压缩」表示，再在其上训练扩散模型 ⇒ 首次在**复杂度下降与细节保留间取得近最优点**；引入 **cross-attention** 层，使同一模型可被文本 / 边界框等一般条件控制；在**图像修复、类条件合成**上取得当时新 SOTA，文生图 / 超分等具竞争力，且**计算需求显著低于像素级扩散**。 |
| 与我们工作的关系 | **vision（生成式数据增广：直接）**：与 #93 DDPM、#102 GAN 组成生成三档（GAN → DDPM → LDM）。<b>动作</b>：版图 patch / 波形片段上做「像素扩散 vs 隐空间扩散」两臂，固定下游检测 / 回归任务与训练预算，指标用**下游精度 + 分布距离**，FID 仅参考。<b>预注册判据</b>：隐空间臂若在同等 GPU 时下下游精度 ≥ 像素臂 +1 个绝对点，则合成默认走 LDM；否则退回像素扩散（少一个自编码器误差源）。<br>**data（合成账本）**：LDM 有**两层误差**（重建 + 生成），必须分开记账。<b>动作</b>：manifest 增列 `autoencoder_id` 与重建 PSNR，合成与真实样本分栏。<br>**designflow（条件生成接口）**：cross-attention 条件通路 = 把「规格 / 约束」塞进生成器的现成接口。<b>动作</b>：L4 生成类题目先只做**无条件 / 弱条件**（尺寸、层数），不要一上来条件到网表。<br>**zhulong（推理成本）**：扩散推理是**多步串行**，与工具长尾延迟叠加会放大预算。<b>动作</b>：生成式 rollout 必须记「步数 × 每步时延」，与直接回归基线同表比较。<br>**风险**：① 20,670 为 OpenAlex 单一来源，🚫 不跨源比较；② FID / IS 在工业图像上**不等于**可用性，🚫 不得替代下游判分；③ 本条「经典」依据是被引 + 范式（隐空间扩散），不是 EDA 结论。 |

首次收录: 2026-11-14（第二十七轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；OpenAlex `200`）；⚠️ **更正**：候选池此前写的 `2207.11240` 经 OpenAlex 直查实为 **Discrete Key-Value Bottleneck**（2022，被引 15）⇒ **LDM 真 ID = `2112.10752`**

---

## 105. Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model（**MuZero**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model（arXiv 原题；Nature 版标题为小写 `Mastering Atari, Go, chess and shogi by planning with a learned model`） |
| 作者（前 3） | **Julian Schrittwieser** · **Ioannis Antonoglou** · **Thomas Hubert**（et al.，共 **12** 位，另含 Karen Simonyan / Laurent Sifre / Demis Hassabis / David Silver 等） |
| 年份 | **2019**（arXiv 首次提交 **2019-11-19T13:58:52Z**，现 `v2` 2020-02-21；Nature 版 **2020-12-23**） |
| 会议 / 期刊 | **Nature 588(7839):604–609, 2020**（Crossref DOI 直查 `200`，DOI `10.1038/s41586-020-03051-4`） |
| 被引数 | **2,075**（OpenAlex Nature DOI 直查，查询日 **2026-11-14**；⚠️ arXiv 预印本与 Nature 版为**同一工作两记录**，🚫 不相加；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1911.08265> ｜ DOI `10.48550/arXiv.1911.08265`；期刊 DOI `10.1038/s41586-020-03051-4` |
| 一句话贡献 | 摘要原文要点：树搜索在**有完美模拟器**的棋类上极成功，但真实问题里**环境动力学未知**；MuZero 把**树搜索与学习到的模型**结合，在**不知道底层动力学**时于多个视觉复杂域达到超人水平；它学的模型**只预测规划所需**——**动作选择策略、价值函数、奖励**；在 **57 个 Atari 游戏**上取得 SOTA，在围棋 / 国际象棋 / 将棋上**不给规则**也与「给规则的 AlphaZero」打平。 |
| 与我们工作的关系 | **zhulong（model-based 规划：直接）**：三个预测头（policy / value / reward）对应「工具调用策略 / 结果好坏 / 每步收益」，且证明**不必重建完整状态**。<b>动作</b>：EDA 闭环里试点「只预测 PPA 增量与是否违规的轻模型」做候选动作前瞻，真实工具只验证 top-k。<b>预注册判据</b>：同等真工具调用预算下，前瞻臂成功率若不高于启发式 top-k +3 个绝对点则停。<br>**harness（评测协议）**：57 个 Atari + 三种棋 = 固定任务集、可复现；<b>动作</b>：评测表固定「任务集版本 + 环境镜像 + 种子数」，并**同时报多个域**，禁止只报最好一域。<br>**designflow（代理模型）**：把「预测奖励 / 价值」当 signoff 廉价代理，先在仿真器上验证代理与真值的秩相关。<br>**风险**：① 游戏胜负判据**零成本且绝对**，EDA checker 是近似判据 —— 最大不可迁移点；② 57 / 三棋均为游戏域，🚫 外推；③ MuZero 仍需**已知动作空间**，🚫 写成「完全无先验」。 |

首次收录: 2026-11-14（第二十七轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom；Nature 摘要取自 nature.com 页面 meta `description`；Crossref `200`；OpenAlex `200`）

---

## 106. AutoDMP: Automated DREAMPlace-based Macro Placement（**ISPD 2023 · 非 AI 强基线**）

| 字段 | 内容 |
|:--|:--|
| 标题 | AutoDMP: Automated DREAMPlace-based Macro Placement |
| 作者（前 3） | **Anthony Agnesina** · **Puranjay Rajvanshi** · **Tian Yang**（et al.，共 **8** 位，另含 Geraldo Pradipta / Austin Jiao / Ben Keller / Brucek Khailany / Haoxing Ren；机构 = NVIDIA） |
| 年份 | **2023**（ISPD 2023；Crossref `published` = 2023-03-26） |
| 会议 / 期刊 | **ISPD 2023**（ACM `conference-paper`，DOI `10.1145/3569052.3578923`，pp. **149–157**，Crossref + OpenAlex 双 `200` 逐字核） |
| 被引数 | **67**（OpenAlex DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | **无 arXiv**（`ti:"AutoDMP"` 检索 `200` + atom、`totalResults = 0`）｜ DOI <https://doi.org/10.1145/3569052.3578923> |
| 一句话贡献 | 摘要原文要点：macro placement 直接决定 PPA；AutoDMP 用 **GPU 加速的 DREAMPlace** 把 **macro 与标准单元同时摆放**，并用**多目标超参优化**自动调参，产出**高质量且可预测**的解，在学术基准上优于学术与商用工具基线；效率上**单台 NVIDIA DGX Station A100 上 3 小时**优化一个 **270 万单元 / 320 个 macro** 的设计。 |
| 与我们工作的关系 | **designflow（参考 flow / 造题基线：直接）**：这是「**工具 + 自动调参**」而非「生成模型」的强基线，正是 judge agent 时必须打的靶子。<b>动作</b>：把 AutoDMP（固定 DREAMPlace 版本 + 固定搜索预算）作为 L4 的**非 AI 强基线**，agent 必须在**同一 PPA 指标 + 同一墙钟预算**下与它比。<b>预注册判据</b>：若 agent 在 3 小时等价预算内 PPA 不优于 AutoDMP，结论只能写「未超过自动化调参基线」，🚫 不得写「AI 优于传统 flow」。<br>**zhulong（把搜索当工具）**：多目标 HPO = 一种**可被 agent 调用的搜索原语**；<b>动作</b>：把「调参搜索」注册成单独 tool，计入工具调用预算，避免靠无限重试刷分。<br>**harness（可预测性）**：摘要强调 `predictable solutions` ⇒ 评测必须报**方差 / 种子数**，不只看最好一次。<br>**data（设计多样性）**：学术基准与商用设计的分布差异是主要风险，manifest 须标明基准来源。<br>**风险**：① 67 被引**低于**「经典 ≥500」阈值，本条按「**本领域权威 / 方法论常青**（DREAMPlace 生态的自动化延伸）」收录；② 3 小时 / 270 万单元是**特定硬件 + 特定设计**口径，🚫 当通用成本；③ 商用工具基线未公开版本，复现只能比学术基线。 |

首次收录: 2026-11-14（第二十七轮）｜ 状态: 元数据 + 被引已核（OpenAlex `200` + Crossref `200`；**无 arXiv 已用标题检索确认 `totalResults=0`**）；同组作者 Haoxing Ren / Brucek Khailany 已在 `AUTHORS.md`

---

## 107. DREAM-GAN: Advancing DREAMPlace towards Commercial-Quality using Generative Adversarial Learning（**ISPD 2023**）

| 字段 | 内容 |
|:--|:--|
| 标题 | DREAM-GAN: Advancing DREAMPlace towards Commercial-Quality using Generative Adversarial Learning |
| 作者（前 3） | **Yi-Chen Lu** · **Haoxing Ren** · **Hao-Hsiang Hsiao**（et al.，共 **4** 位，另含 Sung Kyu Lim；机构 = Georgia Tech / NVIDIA） |
| 年份 | **2023**（ISPD 2023；Crossref `published` = 2023-03-26） |
| 会议 / 期刊 | **ISPD 2023**（ACM `conference-paper`，DOI `10.1145/3569052.3572993`，pp. **141–148**，Crossref + OpenAlex 双 `200` 逐字核） |
| 被引数 | **16**（OpenAlex DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | **无 arXiv**（`ti:"DREAM-GAN"` 检索 `200` + atom、`totalResults = 0`）｜ DOI <https://doi.org/10.1145/3569052.3572993> |
| 一句话贡献 | 摘要原文要点：DREAMPlace 只优化**线长与密度**，其布局在工业 flow 中不可直接用；DREAM-GAN **在不知道商用工具黑盒算法的前提下**，每次布局迭代除原有两项目标外，**额外优化一个可微的「与商用数据库布局的相似度」损失**；在 **5 个商用设计 + OpenCore** 上、用 **Synopsys ICC2** 实现的工业 flow 验证：布局阶段全面优于原生 DREAMPlace，且收益**保持到布线后**——最多 **8.3% 线长**与 **7.4% 总功耗**改善。 |
| 与我们工作的关系 | **designflow（参考解 / 判分对齐：直接）**：这是「**把商业工具输出当软标签**」的最小可行做法，对应我们「本地开源 flow 与 signoff 之间有 gap」的问题。<b>动作</b>：若能拿到少量**商用 flow 参考布局**，先在 L4 上做「原生 DREAMPlace vs +相似度损失」两臂，指标固定为布线后线长 / 功耗。<b>预注册判据</b>：若参考布局 <20 个设计时收益 <2%，则不建这条管线（数据量我们拿不到）。<br>**harness（跨阶段口径）**：8.3% / 7.4% 是**布线后**指标，说明布局阶段好看的数字可能不迁移；<b>动作</b>：布局类实验必须报到**下一阶段**再下结论。<br>**zhulong（成本可比）**：把 DREAMPlace 当固定基线时必须冻结参数（迭代数 / 目标密度 / 种子）。<br>**data（商用数据不可得）**：商用数据库不可公开 ⇒ 只能用自己的 signoff 结果构造软标签，报告须注明标签来源与数量。<br>**风险**：① 16 被引**远低于** ≥500 阈值，本条按「**本领域权威**（DREAMPlace 生态标志性后续）」收录，**不作范式结论**；② 5 个商用设计样本极小，8.3% / 7.4% 为作者自报；③ 依赖 ICC2 环境，我们复现不了同等条件。 |

首次收录: 2026-11-14（第二十七轮）｜ 状态: 元数据 + 被引已核（OpenAlex `200` + Crossref `200`；**无 arXiv 已用标题检索确认 `totalResults=0`**）；末位作者 Sung Kyu Lim 见 `AUTHORS.md`，**本轮已发信**

---

## 108. Genie: Generative Interactive Environments（**视频世界模型 · 无标注视频学可交互环境**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Genie: Generative Interactive Environments |
| 作者（前 3） | **Jake Bruce** · **Michael Dennis** · **Ashley Edwards**（et al.，共 **25** 位，末位 **Tim Rocktäschel**；机构 = Google DeepMind） |
| 年份 | **2024**（arXiv 首发 `2024-02-23T15:47:26Z`，v1；abs 页 `citation_date` = `2024/02/23`） |
| 会议 / 期刊 | **预印本**（⚠️ arXiv `comment` 仅给一个项目页链接、无会议名 ⇒ **会议未核验**，🚫 不写 ICML） |
| 被引数 | **258**（OpenAlex arXiv DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2402.15391> ｜ DOI `10.48550/arxiv.2402.15391` |
| 一句话贡献 | 摘要原文要点：**首个从无标注互联网视频无监督训练的可交互生成环境**；模型可用**文本 / 合成图像 / 照片 / 草图**提示，生成**动作可控**的虚拟世界；规模 **11B 参数**，可视为一个 foundation world model，由**时空视频 tokenizer + 自回归动力学模型 + 简单可扩展的 latent action model** 组成；在**没有任何真值动作标签**的情况下也能逐帧操作；学到的 latent action 空间还能让 agent **从没见过的视频里模仿行为**。 |
| 与我们工作的关系 | **zhulong（低价演练：直接）**：如果 agent 能先在「学出来的环境」里试错、再用真工具验证少数候选，就等价于把 MuZero（#105）的「模型内规划」搬到工具链上。<b>动作</b>：先做最小可行版——用**工具日志 + 中间产物截图**训一个单步动力学模型（预测「下一次调用后 PPA / DRC 变化」），不做整环境生成；<b>预注册判据</b>：同等真工具调用预算下，模型内预演若不能把真工具调用次数降 ≥30% 而不掉成功率，则不投入。<br>**harness（如何验证「真的可控」）**：Genie 的最大争议正是「latent action 是真空作还是拟合了相机/场景变化」；我们评测 agent 的「模拟环境」时必须同样自证——<b>动作</b>：加**反事实一致性**测试（同一状态给不同动作，产物必须系统性不同），并报**随机动作基线**。<br>**vision（视频表征）**：时空 tokenizer 与「长程一致性 + 局部保真」的权衡，与我们版图 / 波形这类二维结构数据同构；<b>动作</b>：vision 线做生成式增广时，把这两个指标**分开报**，不合并成一个总分。<br>**data（无标注数据的价值）**：作者证明价值可以来自**没有动作标签**的原始视频；<b>动作</b>：data 线在 manifest 里区分「有标注 / 仅原始观测」两类，并记录后者占比。<br>**风险**：① 258 被引**低于「经典 ≥500」阈值** ⇒ 按「**开创性 / 领域里程碑**」收录（我们的观察），**不作范式结论**；② 11B / 互联网视频规模，我们无对应数据；③ Genie 2 只有 DeepMind 官方博客、**无一手论文** ⇒ 本表**不单独收**，也不引其数字。 |

首次收录: 2026-11-14（第二十八轮）｜ 状态: 元数据 + 被引已核（arXiv **abs 页** `HTTP 200` / 45,346 B，`citation_title` / `citation_date` / `citation_author` × 25 已核；⚠️ 同轮 API `429` 限速，**abs 页为一手替代源**并已注明）；OpenAlex `200` + 摘要原文；Crossref 精确标题检索**未命中** ⇒ 会议留空

---

## 109. Hitting the Memory Wall: Implications of the Obvious（**"内存墙"提法出处**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Hitting the Memory Wall: Implications of the Obvious |
| 作者（前 3） | **Wm. A. Wulf** · **Sally A. McKee**（共 **2** 位；机构 = University of Virginia, Department of Computer Science） |
| 年份 | **1995**（Crossref `issued` = `1995-03`） |
| 会议 / 期刊 | **ACM SIGARCH Computer Architecture News**，**23(1):20–24**（Crossref `200` 逐字核，`journal-article`） |
| 被引数 | **1,783**（OpenAlex DOI 直查，查询日 **2026-11-14**；ACM 页面自报 1,091，**两源口径不同 ⇒ 不相加、不混用**；S2 / Google Scholar 未查） |
| arXiv / DOI | **无 arXiv** ｜ DOI <https://doi.org/10.1145/216585.216588> |
| 一句话贡献 | 把「**处理器性能提升速度远快于 DRAM 访问速度**」这个当时被视为理所当然的趋势写成一则可引用的论证：两者差距逐年拉大 ⇒ 处理器将有越来越大比例的时间耗在**等内存**上，并讨论该趋势对系统设计（缓存、并行、编程模型）的含义。⚠️ **原文具体的年增百分比本线未取到**（ACM 全文页 `HTTP 403`、Crossref 无 abstract）⇒ 本条**不写任何百分比数字**，只记论点。 |
| 与我们工作的关系 | **zhulong（成本口径：直接）**：这是我们「带宽 / 延迟受限 vs 计算受限」判断的**提法源头**；BaiZe 2B 推理、agent 长上下文、DRAM 仿真实验都该先标清「受限项」。<b>动作</b>：任何性能主张必须同时报**计算量 / 访存量 / 墙钟**三列，缺一列不算通过。<br>**designflow（L4 保真度）**：内存墙说明「周期精确仿真」与「纯 FLOP 估算」会给出**系统性偏差**的结论；<b>动作</b>：L4 布局 / 布线题的成本估计必须走 Ramulator 2.0（#51）或 DRAMsim3（#79）这类周期级模型，🚫 用 FLOPs 反推。<br>**harness（评测可比）**：同一算法在不同**内存配置**下的排名可以翻转；<b>动作</b>：评测 manifest 必须记内存配置（通道数 / 频率 / 时序档），并把它当**不可比标记**。<br>**pretrain（HBM 流量视角）**：与 FlashAttention（#1）的 IO-awareness 同源——**先看 HBM 流量，再看 FLOPs**。<br>**风险**：① 1995 年的机器与今日 GPU/HBM 层级差异巨大，**趋势成立 ≠ 数字可用**（我们的观察）；② 论文是 5 页的「观点 + 粗略估算」，不是测量研究；③ 具体百分比未核 ⇒ 引用时只能引「内存墙」这一概念，🚫 引数字。 |

首次收录: 2026-11-14（第二十八轮）｜ 状态: 元数据 + 被引已核（OpenAlex `200` + Crossref `200`，卷期页码 `23(1):20–24` 逐字一致；ACM 全文页 `403` ⇒ 摘要未取，**未写任何未核实数字**）；同主题已有 Ramulator（#70）/ RowHammer（#71）/ IRAM（#75）/ DRAMsim3（#79）/ Ramulator 2.0（#51）

---

## 110. Deep Learning（**Nature 综述 · 表示学习的纲领文本**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Deep Learning |
| 作者（前 3） | **Yann LeCun** · **Yoshua Bengio** · **Geoffrey Hinton**（共 **3** 位；发表时机构 = NYU / UdeM-MILA / Google-Toronto） |
| 年份 | **2015**（Crossref `issued` = `2015-05-27`） |
| 会议 / 期刊 | **Nature**，**521(7553):436–444**（Crossref `200`，`journal-article`） |
| 被引数 | **90,176**（OpenAlex DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | **无 arXiv** ｜ DOI <https://doi.org/10.1038/nature14539> |
| 一句话贡献 | 摘要原文要点：深度学习让**多层计算模型**学习**多级抽象**的数据表示；这些方法在**语音识别、视觉物体识别、物体检测**以及药物发现 / 基因组学等领域显著提升 SOTA；它靠**反向传播**指示「每层表示该怎样由上一层表示算出、内部参数该怎样改」；**深卷积网络**在图像、视频、语音、音频上带来突破，**循环网络**则在文本、语音等序列数据上发挥作用。 |
| 与我们工作的关系 | **pretrain（论证模板：直接）**：这是我们向内部解释「为什么值得做领域预训练」的最短论证链——**表示学习替代手工特征 → 数据规模 + 深度 → 跨任务迁移**；<b>动作</b>：pretrain 线的立项文档直接引这三段，并明确「我们的『多级抽象』对应什么」（字符/词 → 语句 → 设计意图）。<br>**vision（CNN 谱系）**：与 ResNet（#6）/ AlexNet（#111）构成「 convolutional 路线为什么成了默认」的三点一线；<b>动作</b>：视觉塔选型表把 CNN / ViT（#88）并列，注明各自的历史依据。<br>**data（数据与表示的因果）**：文中把「大数据 + 深模型」作为能力来源 ⇒ 数据线的配比实验必须与大模型一起扫，不能单独定。<br>**zhulong（端到端 vs 分阶段）**：综述强调端到端学习表示的收益，这正是我们「agent 端到端 vs 工具链分阶段」争论的历史参照；<b>动作</b>：消融表明确每段是否可微、若不可微用什么代理信号。<br>**风险**：① 2015 年综述，**未涉及 Transformer / 自监督大模型**，不能当今日路线图；② 综述性质，不含新实验，🚫 引用其结论当作实验证据；③ 90,176 为 OpenAlex 口径，与其他源不可比。 |

首次收录: 2026-11-14（第二十八轮）｜ 状态: 元数据 + 被引已核（OpenAlex `200` + Crossref `200`；摘要取自 `nature.com/articles/nature14539` 页面 `dc.description`（`HTTP 200` / 381,847 B），**只写摘要内出现的说法、不写正文数字**）；三位作者中 Hinton 已在 `AUTHORS.md`（第二十二轮），LeCun / Bengio 本轮新增

---

## 111. ImageNet Classification with Deep Convolutional Neural Networks（**AlexNet**）

| 字段 | 内容 |
|:--|:--|
| 标题 | ImageNet Classification with Deep Convolutional Neural Networks |
| 作者（前 3） | **Alex Krizhevsky** · **Ilya Sutskever** · **Geoffrey Hinton**（共 **3** 位；发表时机构 = University of Toronto） |
| 年份 | **2012**（NeurIPS 2012 原始版）· 期刊版 **2017**（CACM `issued` = `2017-05-24`，DOI `10.1145/3065386`） |
| 会议 / 期刊 | **NeurIPS (NIPS) 2012** 原始版 ｜ 本表被引与卷期取 **Communications of the ACM 60(6):84–90** 记录（Crossref `200`，`journal-article`） |
| 被引数 | **114,712**（OpenAlex CACM DOI 直查，查询日 **2026-11-14**；该数字为**期刊版记录**，与 NeurIPS 版记录**不可相加**；S2 / Google Scholar 未查） |
| arXiv / DOI | **无 arXiv** ｜ DOI <https://doi.org/10.1145/3065386>（NeurIPS 原始版：`papers.nips.cc` 存档，本线未单独核被引） |
| 一句话贡献 | 摘要原文要点：训练一个**大型深卷积网络**把 ImageNet LSVRC-2010 的 **120 万张高分辨率图像**分到 **1000 类**，测试 **top-1 37.5% / top-5 17.0%**，显著优于当时 SOTA；网络 **6000 万参数 / 65 万神经元**，**5 个卷积层**（部分接 max-pooling）+ **3 个全连接层** + 1000 路 softmax；为加速训练用了 **non-saturating 神经元（ReLU 系）** 与**高效 GPU 卷积实现**；为抑制全连接层过拟合用了 **dropout**；该模型的 ILSVRC-2012 变体取得 **top-5 15.3%**，第二名 **26.2%**。 |
| 与我们工作的关系 | **vision（工程配方：直接）**：ReLU + dropout + GPU 卷积这三件事至今是视觉塔的默认项；<b>动作</b>：视觉塔的**消融基线**就用「AlexNet 级配方」起手（小分辨率、固定 patch 数），先确认管线正确再加复杂度。<br>**pretrain（算力换精度）**：6000 万参数在 2012 年已是「大模型」，说明**规模 + 数据 + 算力**的组合早于 Transformer；<b>动作</b>：BaiZe 的 scaling 讨论里把「模型容量 / 数据 / 算力」三轴的历史拐点各标一条，避免把 2020 后的结论当成唯一路线。<br>**harness（固定基准）**：「同一 1000 类、同一 top-1/top-5 口径」是它被高引的重要原因；<b>动作</b>：我们的 EDA 评测必须冻结**任务集版本 + 指标定义**，否则分数不可比。<br>**data（数据规模的作用）**：120 万张标注是当时的关键投入；<b>动作</b>：data 线报「标注成本 / 有效样本数」两列，避免只看总量。<br>**风险**：① 2012 年基准与今日视觉任务差异巨大，🚫 把 15.3% / 26.2% 当现状；② 114,712 是 CACM 汇总记录，含大量教材/综述引用，**不代表同等方法论地位**；③ 两版（NeurIPS 2012 / CACM 2017）**同一工作**，🚫 相加。 |

首次收录: 2026-11-14（第二十八轮）｜ 状态: 元数据 + 被引已核（OpenAlex `200` + 摘要原文；Crossref `200`，CACM `60(6):84–90`、`issued=2017-05-24`；NeurIPS 原始版未单独核被引 ⇒ **只报一个数字**）；作者 Ilya Sutskever / Geoffrey Hinton 已在 `AUTHORS.md`，Alex Krizhevsky 本轮新增（**未找到 X**）

---

## 112. Textbooks Are All You Need（**phi-1 · 「数据质量 > 数据量」的可执行配方**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Textbooks Are All You Need |
| 作者（前 3） | **Suriya Gunasekar** · **Yi Zhang** · **Jyoti Aneja**（共 **19** 位；Microsoft Research） |
| 年份 | **2023**（arXiv v1 `2023-06-20`，v2 `2023-10-02`） |
| 会议 / 期刊 | **预印本**（arXiv `2306.11644`，`cs.CL`；本线**未核到**正式会议/期刊记录 ⇒ 🚫 不写「某会录用」） |
| 被引数 | **1,104**（OpenAlex DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2306.11644> ｜ DOI `10.48550/arXiv.2306.11644` |
| 一句话贡献 | 摘要原文要点：**1.3B** 参数的 phi-1 用 **8×A100 训 4 天**，语料 = **6B token「教科书质量」网页筛选数据 + 1B token 由 GPT-3.5 合成的教科书与练习**；HumanEval **pass@1 50.6%**、MBPP **55.5%**；同配方 **350M** 的 phi-1-small 仍达 HumanEval **45%**，且相对 phi-1-base 出现「**emergent properties**」。 |
| 与我们工作的关系 | **data（直接 · 主目标）**：它把「数据质量 > 数据量」落成可复现的两步配方 —— ① 用分类器从网页里筛「教科书质量」；② 用强模型**合成教材 + 练习**。<b>动作</b>：data 线在 BaiZe 的 2B 语料上做 3 档对照（**全量网页 / 分类器筛后 / 筛后 + 合成**），等 token 预算、等步数；<b>判据</b>：代码类 pass@1 相对全量档 ≥ +5pp，且通用中文能力不降 >2pp，才把「筛 + 合成」写进正式配方。<br>**pretrain（成本）**：4 天 × 8×A100 说明**小模型 + 好数据**的消融循环可以做得很便宜；<b>动作</b>：把 data-mix 消融的单次预算压到 ≤2 天，先跑 350M 级再上 2B。<br>**vision（配方迁移）**：合成「教材 + 练习」的思路可搬到版图 / 波形的**教学样例合成**（每张图配「该看什么、错在哪」的说明），<b>动作</b>：vision 增广清单加一档「合成 + 解说」并单列消融。<br>**designflow（造题）**：教材式合成 = 带解法的题目生成，与 designflow 的 L1–L5 出题同构；<b>动作</b>：每题必须自带「参考解法 + 判分脚本」，无解法者不入库。<br>**风险**：① **50.6% / 55.5% 为作者自报、未复现**，且 HumanEval 存在训练集污染争议（**我们的观察**，须自查）；② 合成数据依赖 GPT-3.5，不可直接复现；③ 预印本无正式评审记录；④ 6B/1B token 的筛选比例未在本表核实，🚫 不外推「多少比例合成最好」。 |

首次收录: 2026-11-14（第二十九轮）｜ 状态: 元数据 + 被引已核（arXiv API `200` + `atom`，19 作者逐字一致；OpenAlex `200`，DOI 直查；摘要取自 OpenAlex `abstract_inverted_index` 原文拼接）

---

## 113. OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments（**执行式评测 · 每条任务自带判定脚本**）

| 字段 | 内容 |
|:--|:--|
| 标题 | OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments |
| 作者（前 3） | **Tianbao Xie** · **Danyang Zhang** · **Jixuan Chen**（共 **17** 位；论文时香港大学 / Salesforce Research 等） |
| 年份 | **2024**（arXiv v1 `2024-04-11`，v2 `2024-05-30`） |
| 会议 / 期刊 | **NeurIPS 2024**（OpenAlex `type=conference-paper`，pp. **52040–52094**，DOI `10.52202/079017-1650`；Crossref 未逐项核） |
| 被引数 | **686**（OpenAlex DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2404.07972> ｜ DOI `10.48550/arXiv.2404.07972` |
| 一句话贡献 | 摘要原文要点：给出**可扩展的真实电脑环境**（支持任务搭建、**执行式评测**、交互学习，跨 **Ubuntu / Windows / macOS**），并构造 **369** 条真实任务（网页 + 桌面应用、OS 文件 I/O、跨应用工作流）；每条任务都带**详细初始状态配置**与**自定义判定脚本**；人类可完成 **>72.36%**，最好模型仅 **12.24%**，主要卡在 **GUI grounding 与操作知识**。 |
| 与我们工作的关系 | **harness（直接 · 主目标）**：把「成功」定义成**可执行的检查脚本**，而不是让模型自己说做完；<b>动作</b>：EDA 评测 manifest 每条任务强制两段 —— `setup`（固定初始设计 / 工具版本 / 随机种子）与 `check()`（只读产物：GDS、报告 JSON、日志断言），缺一段判 `invalid` 不计分。<br>**zhulong（成本与判别力）**：长链条任务用**二值成功率**方差大、区分度低；<b>动作</b>：报表同时给「二值成功率」与「子目标通过率」两列，**只允许二值那列用于对外比较**（避免用子目标分数报成绩）。<br>**designflow（造题模板）**：任务 = 真实用例 + 初始状态快照 + 判定脚本；<b>动作</b>：L1–L5 每道题必须登记 `initial_state_hash`，改题即换 hash、旧成绩作废。<br>**vision（失败分布）**：GUI grounding 是主要失败源 ⇒ 截图分辨率 / OCR 是瓶颈假设；<b>动作</b>：视觉塔评测加「低分辨率 / 缩放」两档，看成功率掉多少。<br>**风险**：① **12.24% 是 2024 年的基线，🚫 不许当现状引用**；② 我们面对的是**无 GUI 的 CLI 工具链**，VM 级隔离是否必要**未经验证**（已在作者信里直接提问）；③ 369 题的题面公开 ⇒ 存在「背题」风险，**我们的观察**：必须自建留出集。 |

首次收录: 2026-11-14（第二十九轮）｜ 状态: 元数据 + 被引已核（arXiv API `200` + `atom`，17 作者逐字一致；OpenAlex `200`，会议 / 页码 / DOI 已核；摘要取自 OpenAlex 原文拼接）；⚠️ 本轮据此给一作 **Tianbao Xie** 发中文请教信（草稿 `research/mail/drafts/2404.07972.md`）

---

## 114. Machine Learning for Electronic Design Automation: A Survey（**ML-for-EDA 的分层地图**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Machine Learning for Electronic Design Automation: A Survey |
| 作者（前 3） | **Guyue Huang** · **Jingbo Hu** · **Yifan He**（共 **16** 位；清华大学 / 香港中文大学等，末位含 **Bei Yu** / **Yu Wang**） |
| 年份 | **2021**（arXiv v1 `2021-01-10`，v2 `2021-03-08`；TODAES `issued` 2021） |
| 会议 / 期刊 | **ACM Transactions on Design Automation of Electronic Systems (TODAES) 26(5):1–46**（DOI `10.1145/3451179`；arXiv 主分类 `eess.SP`） |
| 被引数 | **388**（OpenAlex 期刊记录直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2102.03357> ｜ DOI `10.1145/3451179` |
| 一句话贡献 | 摘要原文要点：CMOS 微缩使 VLSI 设计复杂度持续上升；文章给出 ML-for-EDA 的**综述**，按 **EDA 层级（EDA hierarchy）** 组织既有研究 —— 即把「ML 能插进设计流的哪一层」画成一张有序地图，而不是按模型种类罗列。 |
| 与我们工作的关系 | **designflow（L1–L5 分层的对照表 · 主目标）**：本文的分类轴是「**EDA 层级**」而不是模型类别 ⇒ 我们的 L1–L5 保真度分层可以拿它做外部校验（每一层对应的任务类型、可用输入、可验证输出）。<b>动作</b>：designflow 造题表加一列「所属 EDA 层级（本文口径）」，两套分层对不上的题先重新归层再入库。<br>**pretrain（领域语料分层）**：按层级归类的任务本身就是**领域语料的分类体系**；<b>动作</b>：data 语料清单按同一层级打标签，报表给出「每层 token 占比」，避免学科目失衡。<br>**harness（每层指标不同）**：不同 EDA 层级的目标函数（时序 / 面积 / 功耗 / 良率）不可混算 ⇒ <b>动作</b>：评测 manifest 增列 `eda_layer` 与 `objective`，跨层聚合一律标 `不可比`。<br>**zhulong（代理模型边界）**：综述覆盖的都是「某一层用 ML 替代/加速」的既有做法 ⇒ 我们的代理模型只在**单一层级内**声明有效性；<b>动作</b>：报告代理模型时写明层级与训练分布外推范围。<br>**data（任务形态）**：各层输入形态差异大（网表 / 版图 / 波形 / 报告）⇒ 不能用一套 tokenizer 打天下；<b>动作</b>：data 线按形态分组做去重与配比。<br>**风险**：① **388 < 500**，未达「高引」门槛 ⇒ 按「**本领域权威综述 + 方法论常青**」收录（**我们的观察**），不作范式结论；② 2021 年综述，**不含 2023 后的 LLM-for-EDA 进展**（ChipNeMo 等另见 #5）；③ 综述性质，不含新实验，🚫 引用其结论当实验证据；④ 16 位作者的具体机构分工本表未逐条核。 |

首次收录: 2026-11-14（第二十九轮）｜ 状态: 元数据 + 被引已核（arXiv API `200` + `atom`，16 作者逐字一致、主分类 `eess.SP`；OpenAlex `200`，`type=article`，TODAES `26(5):1–46` 与 DOI 一致；摘要取自 OpenAlex 原文拼接）

---

## 115. A Modern Primer on Processing in Memory（**存储内计算（PIM）综述 · 数据搬移视角**）

| 字段 | 内容 |
|:--|:--|
| 标题 | A Modern Primer on Processing in Memory |
| 作者（前 3） | **Onur Mutlu** · **Saugata Ghose** · **Juan Gómez-Luna**（共 **6** 位；ETH Zurich / UIUC / 等） |
| 年份 | **2020**（arXiv v1 `2020-12-05`，最新 v5 `2025-02-06`） |
| 会议 / 期刊 | **预印本 / 综述**（arXiv `2012.03112`，`cs.AR`；本线未核到正式期刊卷期 ⇒ 不写「某刊录用」） |
| 被引数 | **92**（OpenAlex DOI 直查，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2012.03112> ｜ DOI `10.48550/arXiv.2012.03112` |
| 一句话贡献 | 摘要原文要点：把「**在数据附近/内部计算**」统称 **PIM** —— 计算单元放进存储芯片或模块内部、3D 堆叠存储的逻辑层、存储控制器、存储设备中，从而**减少或消除数据在计算与存储之间的搬移**；文章梳理应用与存储电路/工艺两条动因，并区分两类路线：**processing-using-memory**（利用存储阵列的模拟工作特性直接完成运算）与近存 / 用存路线。 |
| 与我们工作的关系 | **zhulong（成本口径 · 主目标）**：与 #109「内存墙」同一论证链的**现代版**——把「搬移 vs 计算」写成可分类的判断，正好给我们的成本报表一个三分法（<b>动作</b>：性能主张必须标明「计算受限 / 搬移受限 / 容量受限」，并把 PIM 类方案单列一档，🚫 与 GPU 基线混算）。<br>**designflow（L4 保真度）**：PIM 方案的正确性高度依赖**存储阵列的模拟行为**，纯功能级仿真会给出错误结论；<b>动作</b>：涉及近存/用存的题一律标 `L4+`，并要求给模拟器配置哈希。<br>**data（结构化领域文本）**：存储工艺与阵列操作是高度结构化的领域知识，可作为「规格 → 可执行模型」语料的样本形态；<b>动作</b>：data 线登记该类语料的可得性与授权状态。<br>**pretrain（无关但需标注）**：本文与预训练配方无关，🚫 不借其结论支撑模型侧主张（写清以免被误引）。<br>**风险**：① **92 < 500**，按「**方向权威综述**（Mutlu 组）+ 方法论常青」收录（**我们的观察**），🚫 当高引经典引用；② 综述性质，不含新实验；③ 与我们 CXMT 内部工艺/模型无任何对接验证；④ v5 更新到 2025，版本间数字可能变动，引用须标版本。 |

首次收录: 2026-11-14（第二十九轮）｜ 状态: 元数据 + 被引已核（arXiv API `200` + `atom`，6 作者逐字一致、`cs.AR`；OpenAlex `200`，DOI 直查；摘要取自 OpenAlex 原文拼接）；同主题已有 #109 内存墙 / #51 Ramulator 2.0 / #70 Ramulator / #75 IRAM / #79 DRAMsim3

---

## 116. GPT-4 Technical Report（**「能力 + 可预测性 + 局限」报告体例的模板**）

| 字段 | 内容 |
|:--|:--|
| 标题 | GPT-4 Technical Report |
| 作者（前 3） | **OpenAI**（机构署名）· **Josh Achiam** · **Steven Adler**（arXiv API 计 **281** 条作者/机构署名，逐字取自 atom） |
| 年份 | **2023**（arXiv v1 `2023-03-15`，v6 `2024-03-04`） |
| 会议 / 期刊 | **预印本**（arXiv `2303.08774`，`cs.CL`）；本线**未核到正式会场版本** ⇒ 不写「某会录用」 |
| 被引数 | **38,329**（OpenAlex DOI 直查 `10.48550/arXiv.2303.08774`，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2303.08774> ｜ DOI `10.48550/arXiv.2303.08774` |
| 一句话贡献 | 摘要原文要点：报告 GPT-4 —— 可接受**图像与文本**输入、输出文本的大规模多模态模型；在多项专业与学术基准上达「人类水平」，包括模拟律师资格考试约**前 10%**；明确自述「在真实世界许多场景仍不如人类」；核心工程点是**跨规模可预测**的基础设施与优化方法，可用不超过 GPT-4 **1/1,000** 计算量训练的模型预测其部分能力。 |
| 与我们工作的关系 | **pretrain（主目标 · 规模外推纪律）**：报告把「小规模代理实验 → 大模型能力」写成可预测关系 ⇒ <b>动作</b>：2B 配方每次改动先在 350M/600M 上跑「代理点」，只把方向一致的改动推到大模型，并在 MEMORY 记录代理点与大点的同向性。<br>**harness（报告体例）**：能力表 + 明确局限，而不是单一 SOTA 句 ⇒ <b>动作</b>：我们的评测报表固定三块「能力 / 失败模式 / 不可比说明」，缺一块不对外。<br>**zhulong（成本口径）**：算力—性能曲线的外推必须标「代理点算力占比」⇒ <b>动作</b>：成本表加 `proxy_scale_ratio` 列。<br>**data（弱相关）**：报告不披露数据配比 ⇒ 不据此写任何数据结论。<br>**风险**：① **未公开架构、参数量、数据与训练细节** ⇒ 任何「GPT-4 用了 X」都是**推测**，🚫 写成事实；② 38,329 为 OpenAlex **预印本**口径；③ 「前 10%」是模拟考试成绩，🚫 泛化成「达到人类专家」。 |

首次收录: 2026-11-14（第三十轮）｜ 状态: 元数据 + 被引已核（arXiv API `200` + `atom`，281 条署名逐字；OpenAlex `200`，`type=preprint`，无卷期；摘要取自 arXiv `summary`）

---

## 117. Roofline: An Insightful Visual Performance Model for Multicore Architectures（**成本三分法的源头**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Roofline: An Insightful Visual Performance Model for Multicore Architectures |
| 作者（前 3） | **Samuel Williams** · **Andrew Waterman** · **David Patterson**（共 **3** 位；UC Berkeley Parallel Computing Laboratory，Crossref 机构字段已核） |
| 年份 | **2009**（CACM `issued` 2009-04） |
| 会议 / 期刊 | **Communications of the ACM 52(4):65–76**（DOI `10.1145/1498765.1498785`；Crossref `200`） |
| 被引数 | **2,165**（Crossref 该 DOI 的 `is-referenced-by-count`，查询日 **2026-11-14**；另有一条 LBNL 技术报告 DOI `10.2172/1407078` 记 **85**，**两条不相加**；OpenAlex 未查 —— 本轮该 IP 的免费额度已用尽） |
| arXiv / DOI | **无 arXiv** ｜ DOI `10.1145/1498765.1498785`（⚠️ 曾误记为 `10.1145/1340771.1340803`，Crossref 返回 `404` ⇒ 已按实测更正） |
| 一句话贡献 | 摘要原文（Crossref JATS，仅一句）：**Roofline 模型提供关于如何改进软硬件性能的洞见**。模型以「**可达性能 vs 运算强度**」为坐标，把**计算峰值**与**内存带宽**画成两条「屋顶线」，从而一眼看出某内核是**受计算限制**还是**受带宽限制**。 |
| 与我们工作的关系 | **zhulong（主目标 · 成本口径）**：这正是我们「计算受限 / 搬移受限」二分法的**一手出处** ⇒ <b>动作</b>：成本报表每个 kernel 必须给 `ops/byte`（运算强度）与命中的屋顶线，缺一项判 `不可比`；PIM / 近存类方案单列一档（见 #115）。<br>**pretrain（吞吐排障）**：attention / FFN 的算术强度决定优化方向（换 kernel 还是减搬移）⇒ <b>动作</b>：吞吐回退时先算 `ops/byte`，再决定查 kernel 还是查内存。<br>**harness（可比性）**：性能对比必须落在同一 roofline 点 ⇒ <b>动作</b>：benchmark 记录硬件峰值与带宽，跨机型只比「相对屋顶线的百分比」。<br>**风险**：① 原文面向**多核 CPU 浮点**，GPU 与低精度（BF16/FP8）需换算峰值，🚫 直接套用；② 2165 为 Crossref 单条记录，不等于全口径被引；③ 摘要只有一句 ⇒ 本表「一句话贡献」的第二句是**我们的观察**，非原文。 |

首次收录: 2026-11-14（第三十轮）｜ 状态: 元数据 + 被引已核（Crossref DOI 直查 `200`，标题 / 刊名 / 卷期页码 / 3 位作者 / 机构逐项一致）；⚠️ OpenAlex 本轮额度耗尽 ⇒ 只用 Crossref

---

## 118. Sigmoid Loss for Language Image Pre-Training（**SigLIP · 视觉塔损失与 batch 的解耦**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Sigmoid Loss for Language Image Pre-Training |
| 作者（前 3） | **Xiaohua Zhai** · **Basil Mustafa** · **Alexander Kolesnikov**（共 **4** 位，末位 **Lucas Beyer**；arXiv atom 逐字核） |
| 年份 | **2023**（arXiv v1 `2023-03-27`，v4 `2023-09-27`） |
| 会议 / 期刊 | **ICCV 2023（Oral）**，pp. **11941–11952**（OpenAlex `type=conference-paper` 记录）；arXiv 主分类 `cs.CV` |
| 被引数 | **1,884**（OpenAlex DOI 直查 `10.48550/arXiv.2303.15343`，查询日 **2026-11-14**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2303.15343> ｜ DOI `10.48550/arXiv.2303.15343` |
| 一句话贡献 | 摘要原文要点：提出 **pairwise sigmoid loss**，只作用于图像—文本对，**不需要全局相似度归一化**（去掉 softmax 的 all-pairs 视野）；因此**既可把 batch 继续放大，又在小 batch 下更好**；配合 Locked-image Tuning 仅 **4 块 TPUv4、2 天** 得到 **84.5%** ImageNet zero-shot；把 batch 推到 **1M** 后发现收益很快饱和，**32k 已足够**。 |
| 与我们工作的关系 | **vision（主目标 · 损失与 batch）**：视觉塔对比学习是否必须 all-gather 全局负例，直接影响通信与可扩展性 ⇒ <b>动作</b>：视觉塔预训练加一组 `sigmoid vs softmax` 对照（固定图文对与 token 预算），预注册判据 = 检索 R@1 不低于 softmax 基线且单卡显存峰值下降。<br>**data（配比与去重）**：sigmoid 把「负例」变成显式的对级判定 ⇒ batch 内**互译/近重复图文对会被当负例**；<b>动作</b>：图文对入库前做跨语种近似去重，报表给「重复对占比」。<br>**pretrain（并行开销）**：去掉全局归一化可减少跨卡 all-gather ⇒ <b>动作</b>：在多模态阶段记录通信占比前后对比。<br>**风险**：① 84.5% 与 32k 均为**作者自报**，未复现；② v1→v4 数字与模型档位有变（v4 才补 Base / Large / Shape-Optimized 400M）⇒ 引用必须标版本；③ 1,884 为 OpenAlex **ICCV** 记录口径。 |

首次收录: 2026-11-14（第三十轮）｜ 状态: 元数据 + 被引已核（arXiv API `id_list` `200` + `atom`，4 作者逐字、`cs.CV`；OpenAlex `200`，ICCV 页码一致；摘要取自 arXiv `summary`）；⚠️ 本轮据此给一作 **Xiaohua Zhai** 发中文请教信（草稿 `research/mail/drafts/2303.15343.md`）

---

## 119. Deduplicating Training Data Makes Language Models Better（**训练集去重：记忆化与评测污染的一手证据**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Deduplicating Training Data Makes Language Models Better |
| 作者（前 3） | **Katherine Lee** · **Daphne Ippolito** · **Andrew Nystrom**（共 **7** 位，末位 **Nicholas Carlini**；ACL Anthology `citation_author` 逐条核） |
| 年份 | **2021**（arXiv v1 `2021-07-14`，v2 `2022-03-24`）；**ACL 2022** |
| 会议 / 期刊 | **ACL 2022（Long Papers）**，pp. **8424–8445**，DOI `10.18653/v1/2022.acl-long.577`（Crossref `200`） |
| 被引数 | **226**（Crossref 该 DOI 的 `is-referenced-by-count`，查询日 **2026-11-14**；OpenAlex 上另有**预印本**记录 **357**，**两条不相加**） |
| arXiv / DOI | <https://arxiv.org/abs/2107.06499> ｜ DOI `10.18653/v1/2022.acl-long.577` |
| 一句话贡献 | 摘要原文要点：现有语言建模数据集含大量**近重复样本与长重复子串**，导致**超过 1%** 的无提示输出**逐字复制**训练数据；作者给出两种去重工具（例：从 C4 中删掉一句重复 **60,000+** 次的 61 词英文句子），去重后**记忆化输出减少十倍**、达到同等或更好精度所需**步数更少**；并指出标准数据集的验证集中**超过 4%** 与训练集重叠，去重可降低 train-test 泄漏、让评测更准。 |
| 与我们工作的关系 | **data（主目标 · 去重）**：把「去重」从卫生习惯变成有数字的评测问题 ⇒ <b>动作</b>：语料入库流水线固定两级去重（精确子串 + 近似），报表给「重复 token 占比 / 跨 split 重叠率」。<br>**harness（污染）**：>4% 验证集重叠说明**公开基准分数可能虚高** ⇒ <b>动作</b>：我们自建留出集必须与训练语料做跨源近重复检索（n-gram + 向量），命中率进报表。<br>**pretrain（效率）**：去重后更少步数达同等精度 ⇒ <b>动作</b>：把「去重率」列为配方变体的一等超参，记录与 token 效率的关系。<br>**风险**：① 结论基于 **C4 等英文语料**，中文 / 代码需重测，🚫 直接外推；② 「十倍」只指**记忆化文本频率**，不是通用能力十倍；③ 226（ACL）与 357（预印本）是两条记录，**不相加**。 |

首次收录: 2026-11-14（第三十轮）｜ 状态: 元数据 + 被引已核（arXiv API `200` + `atom`，7 作者；ACL Anthology 页 `200` / 42,877 B，`citation_*` 逐条一致；Crossref DOI `200`，页码 8424–8445 一致）

---

## 120. Evaluating Large Language Models Trained on Code（Codex / HumanEval）

| 字段 | 内容 |
|:--|:--|
| 标题 | Evaluating Large Language Models Trained on Code |
| 作者（前 3） | Mark Chen · Jerry Tworek · Heewoo Jun（共 **54** 位；arXiv 作者字段逐字核，OpenAlex 把一作误并成 `Mark I-Cheng Chen` ⇒ **以 arXiv 为准**） |
| 年份 | **2021**（arXiv v1 `2021-07-07`，v2 `2021-07-14`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，无会场记录；本轮未核到一手会场页 ⇒ 不写会议） |
| 被引数 | **12,170**（OpenAlex `10.48550/arxiv.2107.03374`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2107.03374> ｜ DOI `10.48550/arxiv.2107.03374` |
| 一句话贡献 | 在**公开 GitHub 代码**上微调 GPT 系列模型，把「函数级代码生成」变成可测任务：提出 **HumanEval**（164 道手写 Python 题，含单元测试）与 **pass@k** 的无偏估计，并报告「单次采样 → 重复采样」的收益随采样数上升。 |
| 与我们工作的关系 | **harness（直接）**：`pass@k` 与「题 + 可执行单测」的判分口径，是今天所有代码 agent 评测的祖本 ⇒ <b>动作</b>：我们的代码题集必须自带可执行测试，且同时报 pass@1 与 pass@k，避免只报一次采样。<br>**data（直接）**：训练语料 = 公开 GitHub 代码，说明「代码能力主要来自公开代码预训练」这一路线在 2021 年已可复现 ⇒ <b>动作</b>：代码语料入库时记录「许可证 / 去重 / 与评测集重叠」三列，作为 pass@k 可信度的前置条件。<br>**zhulong（间接）**：单测通过 ≠ 需求满足（本文只测函数级正确性）⇒ <b>动作</b>：agent 任务的判分不得把「测试通过」当成需求验收，须另有规格项。<br>**风险**：① HumanEval 仅 164 题、Python 单语言，**已被后续工作大量用作训练数据** ⇒ 分数不再可比；② 本文非同行评审；③ 12,170 是 OpenAlex 预印本口径。 |

首次收录: 2026-11-15（第三十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，54 作者；OpenAlex `200`）

---

## 121. Holistic Evaluation of Language Models（HELM）

| 字段 | 内容 |
|:--|:--|
| 标题 | Holistic Evaluation of Language Models |
| 作者（前 3） | Percy Liang · Rishi Bommasani · Tony Lee（共 **50** 位，CRFM/Stanford；arXiv 作者字段逐字核） |
| 年份 | **2022**（v1 `2022-11-16`，v2 `2023-10-01`） |
| 会议 / 期刊 | **TMLR 2023**（arXiv `journal_ref` 原文：`Published in Transactions on Machine Learning Research (TMLR), 2023`） |
| 被引数 | **2,295**（OpenAlex `10.48550/arxiv.2211.09110`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2211.09110> ｜ DOI `10.48550/arxiv.2211.09110` ｜ 项目页 <https://crfm.stanford.edu/helm/v1.0> |
| 一句话贡献 | 提出**整体评测**框架：在统一条件下把「场景 × 模型 × 指标」排成矩阵，指标固定为 **accuracy / calibration / robustness / fairness / bias / toxicity / efficiency** 七类，并要求**同时报多指标**而不是单一分数；配套开源可复现的评测栈。 |
| 与我们工作的关系 | **harness（主目标）**：七类指标清单可直接当我们评测报表的**列模板** ⇒ <b>动作</b>：任何「某模型更强」的结论必须附 efficiency 与 robustness 两列，缺列即降级为「未评测」。<br>**zhulong（成本口径）**：把 efficiency 当一等信息 ⇒ <b>动作</b>：消融表固定加「每任务成本 / 每正确回答成本」两列，与准确率同表。<br>**data（次要）**：多场景矩阵暴露出「某场景高分来自数据泄漏」的风险 ⇒ <b>动作</b>：自建留出集按场景分层做污染检查。<br>**风险**：① 评测对象是**基座/API 模型**，不是 agent 轨迹，不能直接套到 harness 的 agent 评测；② 矩阵式评测成本高，2B 级自测需缩表，缩表后**不可与原文分数横比**；③ 2,295 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，50 作者；`journal_ref` = TMLR 2023）

---

## 122. The Pile: An 800GB Dataset of Diverse Text for Language Modeling

| 字段 | 内容 |
|:--|:--|
| 标题 | The Pile: An 800GB Dataset of Diverse Text for Language Modeling |
| 作者（前 3） | Leo Gao · Stella Biderman · Sid Black（共 **12** 位，EleutherAI；arXiv 作者字段逐字核） |
| 年份 | **2020**（`published=2020-12-31`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`；无会场记录 ⇒ 不写会议） |
| 被引数 | **3,021**（OpenAlex `10.48550/arxiv.2101.00027`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2101.00027> ｜ DOI `10.48550/arxiv.2101.00027` |
| 一句话贡献 | 把 **800GB、22 个子数据集**的英文语料合成一个**公开可比**的预训练集合，逐个子集给出来源、许可证与去重处理，并证明「多样性」本身是配方的一部分（在同等困惑度下下游任务更好）。 |
| 与我们工作的关系 | **data（主目标）**：子数据集清单本身就是一份**配比模板**（网页 / 论文 / 代码 / 对话 / 百科 / 法律…）⇒ <b>动作</b>：我们的配比表按「子集 × 许可证 × 是否去重 × token 占比」四列建账，先对齐再谈调优。<br>**pretrain（可复现性）**：公开数据集 + 固定版本 = 可复现的基线 ⇒ <b>动作</b>：BaiZe 预训练报告里必须写明语料快照日期与哈希，否则跨版本 loss 不可比。<br>**zhulong（消融）**：多样性收益需要**按子集 ablation**，不能只报「加/不加 Pile」⇒ <b>动作</b>：至少做「去掉代码」「去掉论文」两条单因素消融。<br>**风险**：① 语料以**英文**为主，中文与代码配比不可直接外推；② 2020 年的许可证与今天不同，**必须重新核许可**；③ 「同等困惑度下更好」不能推广成「多样性永远更好」。 |

首次收录: 2026-11-15（第三十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，12 作者；OpenAlex `200`）

---

## 123. Finetuned Language Models Are Zero-Shot Learners（FLAN）

| 字段 | 内容 |
|:--|:--|
| 标题 | Finetuned Language Models Are Zero-Shot Learners |
| 作者（前 3） | Jason Wei · Maarten Bosma · Vincent Y. Zhao（共 **9** 位；arXiv 作者字段逐字核） |
| 年份 | **2021**（v1 `2021-09-03`，v5 `2022-02-08`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `journal_ref` / `doi`；OpenAlex `type=preprint`；**本轮未核到一手会场页 ⇒ 不写 ICLR 等会议名**） |
| 被引数 | **3,471**（OpenAlex `10.48550/arxiv.2109.01652`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2109.01652> ｜ DOI `10.48550/arxiv.2109.01652` |
| 一句话贡献 | 提出**指令微调**范式：把大量已有 NLP 数据集改写成「指令 + 输入 → 输出」的统一格式，按**任务簇**组织并在留出的任务簇上评测，证明指令微调后的模型在**未见任务**上零样本可用（即「指令」本身可迁移）。 |
| 与我们工作的关系 | **data（主目标）**：核心变量不是数据量而是**任务簇的划分**（留出簇 = 泛化检验）⇒ <b>动作</b>：指令数据表必须带 `task_cluster` 列，训练/评测按簇切分，禁止同簇跨 split。<br>**pretrain（次要）**：137B 级模型上指令微调才显现强零样本能力 ⇒ <b>动作</b>：2B 级做同类实验时把「基座规模」当显式变量，不假设结论可下推。<br>**zhulong（能力保留）**：指令微调会改变输出风格与长度 ⇒ <b>动作</b>：能力消融须同时报「目标任务分」与「通用基准分」，防「指令跟随变好、能力退化」被单表掩盖。<br>**风险**：① 任务簇划分与模板由作者设定，**模板措辞本身影响结果**（后续工作反复验证）；② 模型为 LaMDA-PT 系列，未必可外推到 decoder-only 中文模型；③ 3,471 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，9 作者；OpenAlex `200`）

---

## 124. AgentBench: Evaluating LLMs as Agents（**「把 LLM 当 agent 评」的八环境共同口径**）

| 字段 | 内容 |
|:--|:--|
| 标题 | AgentBench: Evaluating LLMs as Agents |
| 作者（前 3） | Xiao Liu · Hao Yu · Hanchen Zhang（共 **22** 位；arXiv 作者字段逐字核，末位 Jie Tang） |
| 年份 | **2023**（v1 `2023-08-07`，v3 `2025-10-04`） |
| 会议 / 期刊 | **ICLR 2024**（arXiv `arxiv:comment` 原文「Published in ICLR 2024」） |
| 被引数 | **1,427**（OpenAlex `10.48550/arxiv.2308.03688`，查询日 **2026-11-15**；`type=preprint`，`primary_location` 为 arXiv） |
| arXiv / DOI | <https://arxiv.org/abs/2308.03688> ｜ DOI `10.48550/arxiv.2308.03688` |
| 一句话贡献 | 把「LLM 是否能在多轮交互中完成任务」拆成 **8 个可执行环境**（操作系统 / 数据库 / 知识图谱 / 数字卡牌 / 解谜 / 家居 / 网页浏览 / 网页购物），用**统一的任务给法、统一的交互轮次与判分**横向比较不同模型，并显式区分「单轮能力」与「多轮持续交互能力」。 |
| 与我们工作的关系 | **harness（主目标）**：评测 agent 的关键不是题有多难，而是**交互口径是否一致**（同一环境、同一轮次上限、同一终止条件）⇒ <b>动作</b>：harness 报表头必须写「环境版本 + 最大轮次 + 终止条件」三项，缺一项即标「非同口径」。<br>**designflow（次要）**：八环境里每个都要求「可执行验证」，而不是让评审看输出像不像 ⇒ <b>动作</b>：出题时先定验证器（可跑的命令 / 可查的状态），再写题面。<br>**风险**：① 2023 年的环境与模型已旧，绝对分数不可与本代模型横比；② 八环境的选择本身带偏好（偏「操作类」），对纯推理或长文本任务覆盖弱；③ 1,427 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十二轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，22 作者；OpenAlex `200`；会议取自 arXiv `comment` 原文）

---

## 125. Constitutional AI: Harmlessness from AI Feedback（**成文原则 + AI 反馈替代人工标注**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Constitutional AI: Harmlessness from AI Feedback |
| 作者（前 3） | Yuntao Bai · Saurav Kadavath · Sandipan Kundu（共 **51** 位；arXiv 作者字段逐字核，末位 Jared Kaplan） |
| 年份 | **2022**（v1 `2022-12-15`，仅一版） |
| 会议 / 期刊 | **预印本**（arXiv 无 `journal_ref` / `doi`；OpenAlex `type=preprint`） |
| 被引数 | **5,135**（OpenAlex `10.48550/arxiv.2212.08073`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2212.08073> ｜ DOI `10.48550/arxiv.2212.08073` |
| 一句话贡献 | 用一份**写下来的原则清单（constitution）**驱动两个阶段：① 监督阶段让模型**自我批评并按原则修订**回答；② RL 阶段用模型自己按原则给出的偏好（**RLAIF**）替代人工偏好标注。目标是减少「人类标注有害输出」这一环的成本与心理负担。 |
| 与我们工作的关系 | **data（主目标）**：这是「偏好数据太贵」的另一条路线——不必先雇人标，而是先写原则、再让模型判 ⇒ <b>动作</b>：data 线把「原则文件」当成一等产物（版本化、可 diff），并把 RLAIF 生成偏好与人工偏好做**同预算**对照。<br>**pretrain（次要）**：原则 + 自我批评本质是「用推理换标注」⇒ <b>动作</b>：若 2B 级模型的自我批评能力不足，此路线在小模型上可能失效，须先测自我批评的一致率。<br>**zhulong（能力保留）**：AI 反馈同样会带来「对齐税」⇒ <b>动作</b>：报告必须同时给「无害性」与「通用能力」两项，不能只报前者。<br>**风险**：① 原则由作者撰写，**原则文本本身就是未消融的变量**；② 51 人作者、Anthropic 内部模型，外部复现门槛高；③ 「AI 反馈更好」在原文中是**特定任务上的比较**，不可外推为通用结论；④ 5,135 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十二轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，51 作者；OpenAlex `200`）

---

## 126. BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models（**冻结两塔 + 轻量桥接**）

| 字段 | 内容 |
|:--|:--|
| 标题 | BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models |
| 作者（前 3） | Junnan Li · Dongxu Li · Silvio Savarese（共 **4** 位，含 Steven Hoi；arXiv 作者字段逐字核） |
| 年份 | **2023**（v1 `2023-01-30`，v3 `2023-06-15`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `journal_ref` / `doi`；OpenAlex `type=preprint`，`primary_location` 为 arXiv） |
| 被引数 | **3,197**（OpenAlex `10.48550/arxiv.2301.12597`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2301.12597> ｜ DOI `10.48550/arxiv.2301.12597` |
| 一句话贡献 | 图像编码器与 LLM **都冻结**，只训一个轻量 **Q-Former** 桥接：第一阶段做视觉—文本表征对齐（对比 / 匹配 / 生成），第二阶段把桥接输出接到冻结 LLM 上做生成式训练。用远小于联合训练的成本获得可用的图文理解与生成能力。 |
| 与我们工作的关系 | **vision（主目标）**：这是「视觉能力接入」的最小改动路线 ⇒ <b>动作</b>：视觉接入方案拆成「塔 / 桥 / LLM」三段，先只调桥接容量（宽度、query 数、阶段数）做对照，再决定是否解冻塔。<br>**pretrain（次要）**：两阶段训练顺序（表征学习 → 生成学习）本身是配方 ⇒ <b>动作</b>：若走冻结路线，两阶段各自的数据配比与步数要单独记录，不能合成一个「总步数」。<br>**风险**：① 冻结塔的表示上限固定，桥接再大也补不回塔丢掉的细节；② 「小成本接近联合训练」是**特定基准**上的结论，中文与 2B 级未测；③ 3,197 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十二轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，4 作者；OpenAlex `200`）

---

## 127. ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs（**工具调用从「造数据」到「判分」的一条龙底座**）

| 字段 | 内容 |
|:--|:--|
| 标题 | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs |
| 作者（前 3） | Yujia Qin · Shihao Liang · Yining Ye（共 **19** 位，含 Yankai Lin / Zhiyuan Liu / Maosong Sun；arXiv 作者字段逐字核） |
| 年份 | **2023**（v1 `2023-07-31`，v2 `2023-10-03`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `comment` / `journal_ref`；OpenAlex `primary_location` 为 arXiv） |
| 被引数 | **1,490**（OpenAlex `10.48550/arxiv.2307.16789`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2307.16789> ｜ DOI `10.48550/arxiv.2307.16789` |
| 一句话贡献 | 从 RapidAPI 收 **16,464** 个 REST API，用 ChatGPT 自动造单工具/多工具指令，再用 **DFSDT**（深度优先搜索决策树，可回溯）替代 ReACT 标注解路径，得到 **126,486** 条（指令，解路径）对；以 LLaMA-2 7B 微调出 ToolLLaMA（用 positional interpolation 把上下文 4096→8192），并给出自动判分器 **ToolEval**（pass rate / win rate）。 |
| 与我们工作的关系 | **harness（主目标）**：pass rate「在预算内是否完成」与 win rate「两条路径谁更好」是两种不同判分口径 ⇒ <b>动作</b>：我们的 agent 评测表至少要分开记「预算内完成率」与「路径偏好胜率」，不能合成一个分数。<br>**data（次要）**：解路径由搜索产生而非单次采样 ⇒ <b>动作</b>：造 agent 训练数据时，把「回溯次数 / 分支数」记成轨迹元数据，否则无法区分「模型强」与「搜索预算大」。<br>**风险**：① 判分器本身由 ChatGPT 担任，存在同源偏置；② RapidAPI 接口会变（论文自己也按 404/维护状态筛 API）⇒ 复现需冻结 API 快照；③ 1,490 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十三轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，19 作者；OpenAlex `200`；PDF `200` 2,048,075 B 并 `pdftotext` 抽取正文核对 126,486 / 16,464 / 4096→8192）

---

## 128. Voyager: An Open-Ended Embodied Agent with Large Language Models（**自动课程 + 可执行技能库 + 自校验迭代**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Voyager: An Open-Ended Embodied Agent with Large Language Models |
| 作者（前 3） | Guanzhi Wang · Yuqi Xie · Yunfan Jiang（共 **8** 位，含 Linxi Fan / Anima Anandkumar；arXiv 作者字段逐字核） |
| 年份 | **2023**（v1 `2023-05-25`，v2 `2023-10-19`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `journal_ref`；`comment` 仅给项目页 `https://voyager.minedojo.org/`） |
| 被引数 | **2,787**（OpenAlex `10.48550/arxiv.2305.16291`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2305.16291> ｜ DOI `10.48550/arxiv.2305.16291` |
| 一句话贡献 | 三个部件拼成终身学习 agent：① 自动课程用 GPT-4 按探索进度提任务；② 技能库存**可执行代码**，按技能描述的 embedding 检索复用；③ 迭代提示把环境反馈 / 执行报错 / **自校验**喂回 GPT-4 改代码，确认完成才入库。Minecraft 中 160 次提示迭代内取得 **3.3×** 更多独特物品、**2.3×** 更远移动距离，木级科技树解锁快 **15.3×**，且是唯一到达钻石级的基线。 |
| 与我们工作的关系 | **harness（主目标）**：把「成功经验」固化成可检索复用的程序，而不是只存对话历史 ⇒ <b>动作</b>：我们的 agent 记忆先做「技能卡（代码 + 描述 embedding）」的最小实现，再谈长上下文。<br>**zhulong（次要）**：技能库让后续任务少走弯路，等于把成本从推理时移到复用 ⇒ <b>动作</b>：成本口径要分「首解成本」与「复用后成本」两列。<br>**风险**：① 自校验与课程都由 GPT-4 兼任，存在自评偏置，论文未给人工核验的一致率；② 指标是 Minecraft 单一环境，不外推到代码 / EDA 任务；③ 2,787 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十三轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，8 作者；OpenAlex `200`；PDF `200` 18,830,859 B 并 `pdftotext` 抽取正文核对 3.3× / 2.3× / 15.3× / 160 iterations）

---

## 129. HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face（**LLM 当调度器：规划 → 选模型 → 执行 → 汇总**）

| 字段 | 内容 |
|:--|:--|
| 标题 | HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face |
| 作者（前 3） | Yongliang Shen · Kaitao Song · Xu Tan（共 **6** 位，含 Dongsheng Li / Weiming Lu / Yueting Zhuang；arXiv 作者字段逐字核） |
| 年份 | **2023**（v1 `2023-03-30`，v4 `2023-12-03`） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `primary_location` = Neural Information Processing Systems；arXiv 本身无 `comment` / `journal_ref`） |
| 被引数 | **1,219**（OpenAlex `10.48550/arxiv.2303.17580`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2303.17580> ｜ DOI `10.48550/arxiv.2303.17580` |
| 一句话贡献 | 把 LLM 当控制器：**任务规划**（把用户请求拆成带 `dep` 依赖的 JSON 任务表）→ **模型选择**（用 Hugging Face 的 model card 描述挑专家模型，另设 **hybrid endpoint** 承接指令跟随类模型）→ **任务执行**（用 `<resource>-task_id` 符号在运行时替换前置任务的输出，解决资源依赖）→ **响应生成**。 |
| 与我们工作的关系 | **harness（主目标）**：多模型编排的失败点集中在两处——模型选择的描述匹配、任务间的数据依赖 ⇒ <b>动作</b>：我们的 harness 日志必须逐任务记「选了哪个模型 / 依赖哪个前置 task_id」，否则编排出错无法归因。<br>**vision（次要）**：视觉任务（检测 / 分割 / 图像生成）是它最主要的外部模型类别 ⇒ <b>动作</b>：视觉能力若走「外挂专家模型」，接口约定（输入输出 schema）就是 harness 的一部分。<br>**风险**：① model card 描述质量直接决定选择正确率，写法一变结果就漂；② 论文实测规模有限（示例任务为主），不能当作大规模编排的可靠性证据；③ 1,219 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十三轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + `atom`，6 作者；OpenAlex `200`；PDF `200` 3,417,598 B 并 `pdftotext` 抽取正文核对 `<resource>-task_id` / hybrid endpoint / 四阶段）

---

## 130. MemGPT: Towards LLMs as Operating Systems（**虚拟上下文管理 = 分层 + 由模型自己换页**）

| 字段 | 内容 |
|:--|:--|
| 标题 | MemGPT: Towards LLMs as Operating Systems |
| 作者（前 3） | Charles Packer · Sarah Wooders · Kevin Lin（共 **7** 位，含 Vivian Fang / Shishir G. Patil / Ion Stoica / Joseph E. Gonzalez；arXiv abs 页作者字段逐字核） |
| 年份 | **2023**（v1 `2023-10-12`，v2 `2024-02-12`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `journal_ref`；`comment` 仅给代码与数据链接；OpenAlex `primary_location` = arXiv） |
| 被引数 | **1,909**（OpenAlex `10.48550/arxiv.2310.08560`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2310.08560> ｜ DOI `10.48550/arxiv.2310.08560` |
| 一句话贡献 | 借操作系统「分页」的思路做**虚拟上下文**：把上下文分成主上下文（直接进窗口）与外部存储（可检索的归档），由模型自己发函数调用在两层之间换入换出，并配读写队列与事件通知；作者在两个「窗口不够用」的场景（长文档分析 / 多轮会话）上验证。 |
| 与我们工作的关系 | **harness（主目标）**：上下文管理不该只有「拉长窗口」一条路 ⇒ <b>动作</b>：我们的 agent 循环里把「取用外部信息」做成显式工具调用，并<b>记录每次换页</b>（谁触发、取了什么、为什么），否则长任务出错无法归因。<br>**zhulong（次要）**：换页次数是可计量的成本项 ⇒ <b>动作</b>：成本表加 `page_in / page_out` 两列，与 token 成本并列。<br>**风险**：① 换页由模型自主决定，论文未给人工核验的「是否该换」准确率；② 无训练、纯提示工程的系统，换模型即需重调提示；③ 1,909 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十四轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 43,126 B 逐字解析，7 作者；OpenAlex `200`；PDF `200` 663,708 B 并 `pdftotext` 核对「虚拟上下文管理 / 分层换页」表述）

---

## 131. Generative Agents: Interactive Simulacra of Human Behavior（**记忆流 + 三轴检索 + 反思**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Generative Agents: Interactive Simulacra of Human Behavior |
| 作者（前 3） | Joon Sung Park · Joseph C. O'Brien · Carrie J. Cai（共 **6** 位，含 Meredith Ringel Morris / Percy Liang / Michael S. Bernstein；abs 页逐字核） |
| 年份 | **2023**（v1 `2023-04-07`，v2 `2023-08-06`） |
| 会议 / 期刊 | **UIST 2023**（OpenAlex `primary_location` = ACM Symposium on User Interface Software and Technology；arXiv 无 `journal_ref`） |
| 被引数 | **4,325**（OpenAlex `10.48550/arxiv.2304.03442`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2304.03442> ｜ DOI `10.48550/arxiv.2304.03442` |
| 一句话贡献 | 给 agent 一套可长期运行的记忆：所有观察进**记忆流**，检索时按**时近性 / 重要性 / 相关性**三轴加权；再让模型**反思**，把零散观察抽象成高层结论写回记忆流；25 个 agent 在小镇里跑出可观察的社会行为（如自发组织活动）。 |
| 与我们工作的关系 | **harness（主目标）**：记忆模块的检索口径决定长任务表现 ⇒ <b>动作</b>：我们的 agent 记忆至少存 `recency` / `importance` / `relevance` 三个字段，并做一次「去掉反思层」的消融再决定是否上反思（每次反思是一次额外 LLM 调用）。<br>**data（次要）**：观察与反思是两类不同数据 ⇒ <b>动作</b>：训练/评测数据里分开标注 `observation` 与 `reflection`，不要混成一种。<br>**风险**：① 行为评估以人类打分与访谈为主，指标不可直接搬到工程任务；② 4,325 为 OpenAlex 口径（UIST 引用量口径偏大，含 HCI 社区）；③ 25 agent × 2 天的模拟规模有限。 |

首次收录: 2026-11-15（第三十四轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 44,651 B，6 作者；OpenAlex `200` 且 `primary_location` = UIST；PDF `200` 11,947,867 B 并 `pdftotext` 核对记忆/反思表述）

---

## 132. Self-Refine: Iterative Refinement with Self-Feedback（**同一模型自评自改，不训练也涨分**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Self-Refine: Iterative Refinement with Self-Feedback |
| 作者（前 3） | Aman Madaan · Niket Tandon · Prakhar Gupta（共 **16** 位，含 Yiming Yang / Sean Welleck / Amir Yazdanbakhsh / Peter Clark；abs 页逐字核） |
| 年份 | **2023**（v1 `2023-03-30`，v2 `2023-05-25`） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `primary_location` = Neural Information Processing Systems；arXiv 无 `journal_ref`） |
| 被引数 | **2,464**（OpenAlex `10.48550/arxiv.2303.17651`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2303.17651> ｜ DOI `10.48550/arxiv.2303.17651` |
| 一句话贡献 | 生成 → 同一模型写反馈 → 按反馈改写，循环到停止条件：7 个任务（对话、代码可读性、数学推理等）平均绝对提升约 **20%**，不需要监督数据、额外训练或 RL；停止条件 `stop(fb_t, t)` 只能是「固定 timestep」或「反馈提示里生成一个 scalar stop score」；失败分析（70 条样本）：**25%** 忽略反馈、**20%** 引入新问题，另有 **60%** 对错误或泛泛反馈保持鲁棒；Vicuna-13B 连 feedback 的格式都产不出。 |
| 与我们工作的关系 | **posttrain（主目标）**：test-time 迭代是「不训练也能涨」的第三条路，但必须与「多采样 k 条再投票」算力对齐才能比 ⇒ <b>动作</b>：任何自评自改的收益都要报「等 token 预算」对照。<br>**harness（次要）**：失败要分类记，不能只看最终分 ⇒ <b>动作</b>：日志加 `feedback_ignored` / `new_issue_introduced` / `robust_to_wrong_feedback` 三列。<br>**风险**：① 20% 是 7 个任务平均、模型为 GPT-3.5/GPT-4，不能外推到 2B；② 停止判据由模型自己给，论文未给「何时该停」的可靠性数字；③ 生成器/评审同一模型 ⇒ 同源偏置。 |

首次收录: 2026-11-15（第三十四轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 43,537 B，16 作者；OpenAlex `200` 且 = NeurIPS；PDF `200` 2,014,949 B 并 `pdftotext` 核对 ~20% / 7 tasks / `stop(fb_t,t)` / 25% / 20% / 60% / Vicuna-13B）

---

## 133. Mamba: Linear-Time Sequence Modeling with Selective State Spaces（**选择性 SSM 骨干**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Mamba: Linear-Time Sequence Modeling with Selective State Spaces |
| 作者（前 3） | Albert Gu · Tri Dao（共 **2** 位；abs 页逐字核） |
| 年份 | **2023**（v1 `2023-12-01`，v2 `2024-05-31`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `journal_ref`；OpenAlex `primary_location` = arXiv） |
| 被引数 | **7,633**（OpenAlex `10.48550/arxiv.2312.00752`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2312.00752> ｜ DOI `10.48550/arxiv.2312.00752` |
| 一句话贡献 | 让 SSM 的参数随输入变化（selective，解决离散模态上的内容推理弱项），但这样就不能再用卷积 ⇒ 设计 **recurrent 模式的硬件感知 parallel scan** 把并行度补回来；整网无 attention、无 MLP 块；生成吞吐约为同规模 Transformer 的 **5×**、序列长度线性扩展，Mamba-3B 在语言建模上超过同规模 Transformer、追平 2× 规模；块内 **expansion = 2**、MLP 扩张因子取 **2**（而非 4）、层数相应 ×**1.5** 保参数量；训练配方为 linear warmup + cosine 衰减到 `1e-5`、峰值取 GPT-3 的 **5 倍**。 |
| 与我们工作的关系 | **pretrain（主目标）**：换骨干是最大的单点决策 ⇒ <b>动作</b>：先做**等参对照**（按上面的配比把参数量对齐现有 2B Transformer，同 token 数、同评测集），同时记 `tokens/s` 与显存峰值；等参下短任务平均分低 >2 个百分点就不换。<br>**zhulong（次要）**：5× 是短序列生成口径 ⇒ <b>动作</b>：成本模型按 `(batch, seq_len)` 分档实测，不许用一个常数。<br>**风险**：① 5× 与「追平 2× 规模」都是作者自报、单实验室；② 长上下文（≥32k）的显存/吞吐拐点论文未给工程结论；③ 7,633 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十四轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 43,088 B，2 作者；OpenAlex `200`；PDF `200` 1,168,615 B 并 `pdftotext` 核对 5× / E=2 / MLP 2 / ×1.5 / 1e-5 / 5× GPT-3 peak lr；作者块自带 `agu@cs.cmu.edu`）

---

## 134. Qwen Technical Report（**中英双语词表 + 3T token 的开源底座**）

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen Technical Report |
| 作者（前 3） | Jinze Bai · Shuai Bai · Yunfei Chu（共 **48** 位，含 Junyang Lin / Jingren Zhou / Tianhang Zhu；abs 页逐字核） |
| 年份 | **2023**（v1 `2023-09-28`，单版本） |
| 会议 / 期刊 | **预印本（技术报告）**（arXiv `comment` = `59 pages, 5 figures`；无 `journal_ref`；OpenAlex `primary_location` = arXiv） |
| 被引数 | **6,006**（OpenAlex `10.48550/arxiv.2309.16609`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2309.16609> ｜ DOI `10.48550/arxiv.2309.16609` |
| 一句话贡献 | 用 **3 万亿 token**（网页 / 百科 / 书籍 / 代码，英文与中文占大头）训练 1.8B / 7B / 14B 的 decoder-only 模型，再用 SFT + RLHF 得 chat 版；关键工程决策是**词表**：从 tiktoken `cl100k_base` 起，补入常用汉字与词、把**数字拆成单个数字**，词表扩到约 **152K**，并以压缩率图给出中 / 英 / 代码与其他十余种语言的相对编码效率；训练上下文 **2048**，评测时验证到 **8192** 以上；另派生 Code-Qwen / Math-Qwen。 |
| 与我们工作的关系 | **pretrain（主目标）**：中文模型的词表与压缩率是**成本的一阶项** ⇒ <b>动作</b>：在 2B 预训练前先做词表对照实验（现有词表 vs 加中文词 vs 数字拆单字符），以「同一批中文/代码样本的 token 数」与「下游 C-Eval/MMLU 的每 token 收益」双指标定稿，不以「词表更大更好」拍板。<br>**data（次要）**：技术报告给了 3T 语料的组成与 13-gram 重叠过滤口径 ⇒ <b>动作</b>：我们的配比表按「网页 / 百科 / 书籍 / 代码」四类分别记来源与许可，去污染沿用 13-gram 但要单列中文阈值（中文更容易偶然重合）。<br>**zhulong（次要）**：tokenizer 压缩率直接改变成本模型 ⇒ <b>动作</b>：成本表加一列「每千汉字 token 数」，词表一换就重算，不许沿用旧系数。<br>**风险**：① 作者自报、未给完整消融，152K 词表的增益与代价未分离；② 语料未公开 ⇒ 无法复现配比；③ 6,006 为 OpenAlex 口径（技术报告被引普遍偏高）。 |

首次收录: 2026-11-15（第三十五轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 47,465 B，48 作者；OpenAlex `200`；PDF `200` 1,994,623 B 并 `pdftotext` 核对 3T / 152K / `cl100k_base` / 数字拆单字符 / 上下文 2048 与 8192）

---

## 135. PaLM: Scaling Language Modeling with Pathways（**540B dense + 6144 TPU v4 的规模实证**）

| 字段 | 内容 |
|:--|:--|
| 标题 | PaLM: Scaling Language Modeling with Pathways |
| 作者（前 3） | Aakanksha Chowdhery · Sharan Narang · Jacob Devlin（共 **67** 位，含 Noam Shazeer / Jeff Dean / Slav Petrov / Noah Fiedel；abs 页逐字核） |
| 年份 | **2022**（v1 `2022-04-05`） |
| 会议 / 期刊 | **预印本**（无 `journal_ref`；OpenAlex `primary_location` = arXiv） |
| 被引数 | **5,425**（OpenAlex `10.48550/arxiv.2204.02311`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2204.02311> ｜ DOI `10.48550/arxiv.2204.02311` |
| 一句话贡献 | 单模型 **540B** 参数、dense decoder-only，用 **Pathways** 在 **6144 块 TPU v4** 上做无 pipeline 并行的训练（论文强调这是该规模下首次高效使用 Pathways），语料 **780B token**、其中非英语约 **22%**、去重后 **196GB** 源代码；2-shot 提示下在数百个语言 / 代码 / 数学任务上取 few-shot SOTA，并报告 **62B → 540B 的非连续跃升**（多步算术等任务上出现断点式提升）。 |
| 与我们工作的关系 | **pretrain（主目标）**：规模跃升不是线性的 ⇒ <b>动作</b>：2B 的规模律外推必须留「断点」余量，任何从 0.5B/1B 曲线直接外推 2B 的结论都标为高风险，并用至少一个中间点（如 1.3B）校准。<br>**data（次要）**：22% 非英语 + 196GB 代码（Levenshtein 去重）是「多语 + 代码」配比的可引用坐标 ⇒ <b>动作</b>：中文占比与代码占比各做一档 ±50% 的消融，看下游是否出现同向收益。<br>**harness（次要）**：few-shot 的 shot 数与提示格式对结论影响极大 ⇒ <b>动作</b>：评测表固定写 `n-shot`，不同 shot 数的分数不得同表横比。<br>**风险**：① 540B 的结论不能外推到 2B（论文只给 8B/62B/540B 三点）；② 训练数据未公开；③ 5,425 为 OpenAlex 口径（arXiv 版被引低于正式引用总量）。 |

首次收录: 2026-11-15（第三十五轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 53,032 B，67 作者；OpenAlex `200`；PDF `200` 2,711,295 B 并 `pdftotext` 核对 540B / 6144 TPU v4 / 780B tokens / 22% 非英语 / 196GB 代码 / 2-shot / 62B→540B 跃升）

---

## 136. Improving language models by retrieving from trillions of tokens（RETRO）

| 字段 | 内容 |
|:--|:--|
| 标题 | Improving language models by retrieving from trillions of tokens（RETRO） |
| 作者（前 3） | Sebastian Borgeaud · Arthur Mensch · Jordan Hoffmann（共 **28** 位，含 Oriol Vinyals / Karen Simonyan / Jack W. Rae / Laurent Sifre；abs 页逐字核） |
| 年份 | **2021**（v1 `2021-12-08`，v3 `2022-02-07`） |
| 会议 / 期刊 | **预印本**（v3 `comment` = `Fix incorrect reported numbers in Table 14`；OpenAlex `primary_location` = arXiv） |
| 被引数 | **697**（OpenAlex `10.48550/arxiv.2112.04426`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2112.04426> ｜ DOI `10.48550/arxiv.2112.04426` |
| 一句话贡献 | 把「检索」做进**预训练目标**而不是外挂：2048 token 的序列切成 **64 token 的 chunk**，每个 chunk 用 **BERT 句向量（宽 r=128）** 在库里取 **k 个近邻**，再以 **chunked cross-attention** 让后续 token 只能看前面 chunk 的检索结果（保持自回归与因果性）；训练用 5T token 语料、128K SentencePiece，训练检索库 **600B**、评测检索库 **1.75T**，2T 库的 SCaNN 查询约 **10 ms**（按 chunk 摊销）；结果是在 Pile 上以 **25× 更少参数** 达到与当时最大模型相当的困惑度；去污染用 **13-gram Jaccard + MinHash，阈值 0.8**。 |
| 与我们工作的关系 | **pretrain（主目标）**：这是「用检索替代一部分参数/上下文」的最完整对照 ⇒ <b>动作</b>：在 2B 上做一条**小比例**检索臂（例如 10% 训练步启用），判据是「同 token 预算下 Pile/中文验证集困惑度」，若等 token 下不优于直接加数据即停。<br>**zhulong（次要）**：检索是**服务端成本项** ⇒ <b>动作</b>：成本表单列「索引内存 + 每 chunk 检索延迟」，与 KV cache 分档并列；交互场景（TTFT 目标）先算这条，别等上线才发现。<br>**data（次要）**：13-gram 去污染阈值对中文偏松 ⇒ <b>动作</b>：中文去污染另跑一档更严阈值（如 8-gram / 更长 n），并在数据卡里记两套阈值的结果差。<br>**风险**：① 25× 是「同困惑度」口径，不是同下游任务分；② 索引规模与内存论文未给端到端工程预算；③ 697 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十五轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 45,961 B，28 作者；OpenAlex `200`；PDF `200` 1,566,448 B 并 `pdftotext` 核对 n=2048 / m=64 / r=128 / 600B vs 1.75T / 2T 库 10 ms / 13-gram 0.8 / 25× / 128K 词表）

---

## 137. AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration（**MLSys 2024 最佳论文**）

| 字段 | 内容 |
|:--|:--|
| 标题 | AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration |
| 作者（前 3） | Ji Lin · Jiaming Tang · Haotian Tang（共 **10** 位，末位 **Song Han**；abs 页逐字核） |
| 年份 | **2023**（v1 `2023-06-01`，v4 2024） |
| 会议 / 期刊 | **MLSys 2024（Best Paper Award）**（arXiv `comment` 原文；OpenAlex `primary_location` 仍记 arXiv） |
| 被引数 | **831**（OpenAlex `10.48550/arxiv.2306.00978`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2306.00978> ｜ DOI `10.48550/arxiv.2306.00978` |
| 一句话贡献 | 只量化权重（**W4A16**），并按**激活幅度**挑出约 **0.1%–1%** 的显著通道保留 FP16、其余用 **per-group（g=128）** 缩放补偿：OPT-6.7B 在 **INT3-g128** 下困惑度从 **43.2（RTN）→ 13.0**（保留 1% 与等价缩放到同一水平），说明「保护极少数通道」比混合精度整层保留更划算；配套 **TinyChat** 推理框架（SIMD-aware 权重打包，ARM 上 128-bit 掩码解包另有约 1.2×）在 on-device 单流下相对 FP16 有 **3–4×** 加速，并支持 4-bit 的 LLM/VLM。 |
| 与我们工作的关系 | **zhulong（主目标）**：这是部署侧「能不能单卡跑 2B」的直接方案 ⇒ <b>动作</b>：把 W4A16 作为一条成本臂，与 INT8 同表对比，指标必须含 **batch ≥16 的 tokens/s**（不是单流延迟）与任务分掉落。<br>**pretrain（次要）**：量化后的评测口径会变 ⇒ <b>动作</b>：量化前后用同一套 harness 与同一 prompt，且记录 PPL 与任务分两条线，避免只报 PPL 好看。<br>**vision（次要）**：论文覆盖 VLM ⇒ <b>动作</b>：视觉塔是否也量化要单列一臂（视觉塔对激活离群更敏感，不能默认同参数）。<br>**风险**：① 3–4× 是 on-device 单流口径，服务端 batch 下会被反量化开销吃掉；② 1% 显著通道比例在中文语料与小模型上未验证；③ MLSys 最佳论文不等于跨语言可复现。 |

首次收录: 2026-11-15（第三十五轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 44,966 B，10 作者，`comment` = MLSys 2024 Best Paper；OpenAlex `200`；PDF `200` 19,804,976 B 并 `pdftotext` 核对 1% / 43.2→13.0 / INT3-g128 / W4A16 / TinyChat 3–4× / 128-bit 掩码 1.2×）

---

## 138. Robust Speech Recognition via Large-Scale Weak Supervision（Whisper）

| 字段 | 内容 |
|:--|:--|
| 标题 | Robust Speech Recognition via Large-Scale Weak Supervision（Whisper） |
| 作者（前 3） | Alec Radford · Jong Wook Kim · Tao Xu（共 **6** 位，含 Greg Brockman / Christine McLeavey / Ilya Sutskever；abs 页逐字核） |
| 年份 | **2022**（v1 `2022-12-06`） |
| 会议 / 期刊 | **预印本**（arXiv 无 `comment` / `journal_ref`；OpenAlex `type` = `preprint`、`primary_location` = arXiv） |
| 被引数 | **3,720**（OpenAlex `10.48550/arxiv.2212.04356`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2212.04356> ｜ DOI `10.48550/arxiv.2212.04356` |
| 一句话贡献 | 不做「先自监督再微调」，而是直接用**互联网弱监督转写**做多任务监督：**680,000 小时**音频里，**117,000 小时覆盖 96 种其他语言**、**125,000 小时为 X→en 翻译数据**，同一个 decoder 用任务 token（语言识别 / 转写 / 翻译 / 时间戳）切换目标；推理按 **30 秒窗口**滑窗 + 时间戳规则拼接长音频，零样本迁移即可接近人类在噪声与口音上的鲁棒性（论文强调「充分大的模型上，多语 + 多任务联合训练无损失甚至有收益」）。 |
| 与我们工作的关系 | **data（主目标）**：这是「弱监督 + 多语配比」最完整的一份公开配方 ⇒ <b>动作</b>：中文语料做配比表时，把「多语联合训练是否有损」单列一列结论（按语言对），并对小语种做一档 2× 上采样与一档「靠总规模硬吃」对照，判据看中文 CER 与代码/数学任务分是否同向变化。<br>**harness（次要）**：幻觉在无音段最严重、且被归因于解码器语言建模先验 ⇒ <b>动作</b>：评测表把「静音/噪声段的插入错误」单列一行，不与整体 WER 混算。<br>**zhulong（次要）**：30 秒窗口 + 滑窗拼接是**流式成本**的直接约束 ⇒ <b>动作</b>：语音类请求的成本按「每 30 秒窗口 + 重叠比例」建模，别按整段音频线性外推。<br>**风险**：① 3,720 为 OpenAlex 口径；② 680k 小时数据未公开，配比只能定性参考；③ WER 跨数据集不可横比（各数据集归一化口径不同）。 |

首次收录: 2026-11-15（第三十六轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 40,046 B，6 作者；OpenAlex `200`；PDF `200` 1,008,644 B / 28 页，`pdftotext` 核对 680,000 / 117,000 小时 / 96 languages / 125,000 小时 X→en）


---

## 139. A Generalist Agent（Gato）

| 字段 | 内容 |
|:--|:--|
| 标题 | A Generalist Agent（Gato） |
| 作者（前 3） | Scott Reed · Konrad Żołna · Emilio Parisotto（共 **20** 位，含 Sergio Gomez Colmenarejo 等；abs 页逐字核） |
| 年份 | **2022**（v1 `2022-05-12`） |
| 会议 / 期刊 | **TMLR 2022**（arXiv `comment` 原文 = `Published at TMLR, 42 pages`） |
| 被引数 | **876**（OpenAlex `10.48550/arxiv.2205.06175`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2205.06175> ｜ DOI `10.48550/arxiv.2205.06175` |
| 一句话贡献 | 把**所有**输入输出压成同一个 token 序列：文本用 **32,000 子词** SentencePiece，图像按 **16×16 patch 光栅序**展开（patch 内像素归一化后间隔量化到 **128 个均匀 bin**），机器人关节力矩 / 按键 / 离散动作也各自离散化成 token；一个 **1.18B** 参数的自回归 transformer 在 **604 个任务**上、**1,024 token** 上下文内同权重运行，部署时**不做任何梯度更新**（论文另给 364M / 79M 变体）。 |
| 与我们工作的关系 | **harness（主目标）**：这是「统一 token 接口 + 单模型多任务」的源头文档 ⇒ <b>动作</b>：工具调用轨迹也按同一纪律序列化（每次调用 = 一个结构化 token 段），并在评测表里显式写「上下文长度上限」，超过就必须分片。<br>**pretrain（次要）**：多模态混合训练不炸的关键在**量化/归一化口径统一** ⇒ <b>动作</b>：视觉与文本共训时，把归一化常数与量化 bin 数写进数据卡，换数据重训时必须重算。<br>**vision（次要）**：图像走 patch 序列而非独立编码器 ⇒ <b>动作</b>：做「早期融合 vs 外挂视觉塔」对照时，用同一 patch 划分做控制变量。<br>**风险**：① 604 任务是作者口径，部分任务在 50% 专家分阈值附近（论文自述）；② 1,024 token 上下文对长程任务明显不够（论文自己列为主限制）；③ 大部分任务数据与权重未开放。 |

首次收录: 2026-11-15（第三十六轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 43,244 B，20 作者、`comment` = TMLR 2022；OpenAlex `200`；PDF `200` 7,662,379 B / 42 页，`pdftotext` 核对 1.18B / 604 tasks / 1024 tokens / 32,000 subwords / 16×16 patches / 128 bins）


---


## 140. SGLang: Efficient Execution of Structured Language Model Programs

| 字段 | 内容 |
|:--|:--|
| 标题 | SGLang: Efficient Execution of Structured Language Model Programs |
| 作者（前 3） | Lianmin Zheng · Liangsheng Yin · Zhiqiang Xie（共 **12** 位，含 Chuyue Sun / Ying Sheng / Ion Stoica / Joseph E. Gonzalez；机构 = Stanford / UC Berkeley / SJTU / Texas A&M） |
| 年份 | **2023**（v1 `2023-12-12`；v2 `2024-06-06`） |
| 会议 / 期刊 | **NeurIPS 2024**（arXiv 无 `comment`；会场取自 OpenAlex `primary_location.source` = `neural information processing systems`、`type` = `conference-paper`） |
| 被引数 | **812**（OpenAlex `10.48550/arxiv.2312.07104`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2312.07104> ｜ DOI `10.48550/arxiv.2312.07104` |
| 一句话贡献 | 前端语言 + 运行时两层：运行时用 **RadixAttention** 把 KV cache 组织成**基数树**做跨请求前缀复用（按 **LRU** 淘汰），再用**压缩有限状态机**加速结构化输出解码；在 agent 控制流 / 逻辑推理 / few-shot / JSON 解码 / RAG / 多轮对话等多类负载上，相对当时最优推理系统给出**端到端最高 6.4× 吞吐**。 |
| 与我们工作的关系 | **zhulong（主目标）**：这是「多轮 / 结构化输出场景下 KV 前缀复用」的工程基线 ⇒ <b>动作</b>：成本表加一行「前缀命中率」，并按负载类型分档（JSON 解码 / 多轮工具调用 / RAG）各报一次 tokens/s，禁止只用单一平均值。<br>**harness（次要）**：agent 循环里每一轮都在复用同一 system prompt 与工具定义 ⇒ <b>动作</b>：harness 记录每轮「新增 token / 复用 token」比例，作为前缀缓存预算的输入。<br>**pretrain（次要）**：批量服务下小模型的显存预算更紧 ⇒ <b>动作</b>：≤2B 场景先把「缓存 token 数上限」做成配置项并扫 2–3 档，再谈吞吐优化。<br>**风险**：① 6.4× 是端到端 throughput、对特定基线版本，不可当作通用倍数引用；② 收益强依赖负载的前缀重复度，长独立生成几乎无收益；③ NeurIPS 会场来自 OpenAlex（arXiv 本身无 `comment`）。 |

首次收录: 2026-11-15（第三十六轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 41,853 B，12 作者；OpenAlex `200`；PDF `200` 1,383,463 B / 20 页，`pdftotext` 核对 `RadixAttention` 33 次 / `radix tree` 20 次 / 6.4× / compressed FSM）


---

## 141. Self-Consistency Improves Chain of Thought Reasoning in Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Self-Consistency Improves Chain of Thought Reasoning in Language Models |
| 作者（前 3） | Xuezhi Wang · Jason Wei · Dale Schuurmans（共 **8** 位，含 Quoc Le / Ed Chi / Sharan Narang / Aakanksha Chowdhery / Denny Zhou） |
| 年份 | **2022**（v1 `2022-03-21`；v4 = camera ready） |
| 会议 / 期刊 | **ICLR 2023**（arXiv `comment` 原文：`Published at ICLR 2023. V2: added PaLM results; V3: added UL2 results; V4: camera ready version at ICLR 2023`） |
| 被引数 | **5,587**（OpenAlex `10.48550/arxiv.2203.11171`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2203.11171> ｜ DOI `10.48550/arxiv.2203.11171` |
| 一句话贡献 | 把 CoT 的**贪心解码**换成**多路径采样 + 边缘化**：对同一题采样 k 条不同推理路径（主实验 **k = 40**），对最终答案做一致性投票（unweighted / weighted 两种），不含任何额外训练；GSM8K **+17.9%**（PaLM-540B 贪心 **56.5** → 自洽 **74.4**）、SVAMP **+11.0%**、AQuA **+12.2%**，并给出 SVAMP / ASDiv 上 **+7%–11%** 的区间。 |
| 与我们工作的关系 | **harness（主目标）**：这是「测试时算力换正确率」的最便宜基线 ⇒ <b>动作</b>：判分表把「单次贪心」与「k 采样投票」两列并列，同时记 k 与总 token 成本，禁止只报更漂亮的一列。<br>**zhulong（次要）**：k=40 意味着 40× 生成成本 ⇒ <b>动作</b>：把 k 做成可配置预算项，并给出「k 从 5→10→20→40」的边际收益曲线，按业务延迟容忍度选点。<br>**pretrain（次要）**：论文明确**小容量模型收益递减**（自洽要在推理能力已具备时才有效）⇒ <b>动作</b>：2B 上先验证贪心准确率是否已过「会做题」阈值，再决定要不要上自洽评测，避免把采样方差当能力。<br>**风险**：① 成本是 k 倍，晚到 40 倍的 token 预算；② 一致性投票在开放生成任务上无定义，只适用可枚举答案；③ 5,587 为 OpenAlex 口径。 |

首次收录: 2026-11-15（第三十六轮）｜ 状态: 元数据 + 被引已核（abs 页 `200` / 42,282 B，8 作者、`comment` = ICLR 2023；OpenAlex `200`；PDF `200` 10,505,941 B / 24 页，`pdftotext` 核对 17.9% / 56.5→74.4 / k = 40 / SVAMP +11.0% / AQuA +12.2%）


---


## 142. wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations

| 字段 | 内容 |
|:--|:--|
| 标题 | wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations |
| 作者（前 3） | Alexei Baevski · Henry Zhou · Abdelrahman Mohamed（共 **4** 位，含 Michael Auli；arXiv 作者字段逐字核） |
| 年份 | **2020**（v1 `2020-06-20`；v3 `2020-10-22`） |
| 会议 / 期刊 | **未核验**（arXiv `comment` 为空；OpenAlex `primary_location.source` = arXiv，`type` = `preprint`）⇒ 🚫 不写 NeurIPS 2020 等会场断言 |
| 被引数 | **3,140**（OpenAlex `10.48550/arxiv.2006.11477`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2006.11477> ｜ DOI `10.48550/arxiv.2006.11477` |
| 一句话贡献 | 用**对比学习 + 量化码本**在**无标注语音**上预训练（论文口径 **53.2k 小时** LibriVox 音频；码本 **G = 320**、特征步长 **25 ms**、掩码概率 **0.065**），再在少量有标注数据上微调：用 LibriSpeech 全部标注数据得 **1.8 / 3.3 WER**（clean / other），仅 **10 分钟**标注数据得 **5.2 / 8.6**，无标注数据扩到 53k 小时则 **4.8 / 8.2**。 |
| 与我们工作的关系 | **data（无标注数据的价值量化，主目标）**：这是「标注少、无标注多」场景的范式证据 ⇒ <b>动作</b>：在数据线报表里把「无标注小时数 / 有标注小时数」做成两列，并记录「10 分钟 / 1 小时 / 10 小时 / 100 小时 / 全量」五档学习曲线，禁止只报全量结果。<br>**pretrain（掩码式自监督的可迁移性）**：掩码 + 对比的组合与我们图文/代码侧的掩码目标同构 ⇒ <b>动作</b>：在 2B 主干的预训练目标消融里加一档「纯掩码 vs 掩码+对比」，固定 token 预算比较下游。<br>**harness（评测口径）**：WER 的 clean / other 分列是「同一模型两个难度域」的样板 ⇒ <b>动作</b>：agent 评测表也按难度域分列（easy / hard），避免单值平均掩盖长尾。<br>**风险**：① 53.2k 小时数据集（LibriVox 预处理版）**未随论文发布**，配比不可复现；② 1.8/3.3 是语音识别专用指标，🚫 不可外推到文本任务；③ 会场未核验，引用时只写 arXiv。 |

首次收录: 2026-11-15（第三十七轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：4 作者、v1/v3 日期已核；OpenAlex `200` 3,140；PDF `200` 740,863 B / 19 页，`pdftotext` 核对 53.2k 小时 / G = 320 / 25ms / 0.065 / 1.8 / 3.3 / 10 minutes）

---

## 143. Fast Transformer Decoding: One Write-Head is All You Need（Multi-Query Attention）

| 字段 | 内容 |
|:--|:--|
| 标题 | Fast Transformer Decoding: One Write-Head is All You Need |
| 作者（前 3） | Noam Shazeer（**单一作者**，共 1 位） |
| 年份 | **2019**（`2019-11-06`，v1 = 最新） |
| 会议 / 期刊 | **未核验**（arXiv `comment` / `journal_ref` 均为空；OpenAlex `primary_location.source` = arXiv） |
| 被引数 | **872**（OpenAlex `10.48550/arxiv.1911.02150`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/1911.02150> ｜ DOI `10.48550/arxiv.1911.02150` |
| 一句话贡献 | 指出自回归增量解码的瓶颈是**重新加载 K/V 张量的显存带宽**（正文给的访存/计算比 = Θ(n/d + 1/b)），提出 **multi-query attention**：所有 head **共享一组 K/V**（query / output 仍多头），把 K/V 张量缩小到 1/h；实测 base 模型训练 step `433ms`（基线）vs `425ms`（MQA），解码**明显更快**而质量仅轻微下降，并用 beam-4 解码做了端到端对照。 |
| 与我们工作的关系 | **zhulong（推理成本的第一性分解，主目标）**：把「解码慢」归因到**带宽**而非算力，是我们成本表的正确框架 ⇒ <b>动作</b>：成本表拆成 `compute` / `memory-bandwidth` 两列，并记录 `batch` 与 `context length` 两个条件，否则倍数不可比。<br>**pretrain（架构选型的对照项）**：MQA 与 GQA（#85）是同一族谱 ⇒ <b>动作</b>：2B 主干的注意力头配置至少跑 MHA / GQA / MQA 三档，固定 token 与下游评测，报「质量损失 vs 解码加速」。<br>**harness（吞吐评测纪律）**：论文只报 step 时间与解码速度、未报完整质量表 ⇒ <b>动作</b>：我们的评测必须同时给「准确率」与「tokens/s」，单向指标不算通过。<br>**风险**：① 2019 年 TPUv2 口径，🚫 不能当今天 GPU 上的倍数；② 论文自述 MQA 质量「略差于基线」，小模型上差距可能放大；③ 本条目被引 872 属「奠基范式」入选，非高引入选。 |

首次收录: 2026-11-15（第三十七轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：1 作者、cs.NE 主分类；OpenAlex `200` 872；PDF `200` 142,627 B / 9 页，`pdftotext` 核对 `multi-query` / Θ(n/d + 1/b) / 433ms vs 425ms / beam-4）

---

## 144. The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits（BitNet b1.58）

| 字段 | 内容 |
|:--|:--|
| 标题 | The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits |
| 作者（前 3） | Shuming Ma · Hongyu Wang · Lingxiao Ma（共 **10** 位，含 Furu Wei（⋄ 通讯）；arXiv 作者字段逐字核） |
| 年份 | **2024**（`2024-02-27`，v1 = 最新） |
| 会议 / 期刊 | **预印本**（arXiv `comment` 原文：`Work in progress`） |
| 被引数 | **496**（OpenAlex `10.48550/arxiv.2402.17764`，查询日 **2026-11-15**；⚠️ 低于 500 ⇒ 按「开创范式」入选，不按高引） |
| arXiv / DOI | <https://arxiv.org/abs/2402.17764> ｜ DOI `10.48550/arxiv.2402.17764` |
| 一句话贡献 | 把每个权重压成**三值 `{-1, 0, 1}`**（即 **1.58 bit**）：`BitLinear` 替换 `nn.Linear`，权重 **absmean 量化**、激活保持 **8-bit**，从零训练；摘要称同规模同 token 下 PPL 与下游追平 FP16/BF16 基线，且 **3.55× 显存 / 2.71× 加速**（正文另报 3.9B = **2.4× 快 / 3.32× 省**，70B 快 **4.1×**、batch **11×**、吞吐 **8.9×**，7nm 上矩阵乘算术能耗降至 **1/71.4**）。 |
| 与我们工作的关系 | **pretrain（低成本主干的候选路线，主目标）**：三值权重把「显存 / 能耗」压到另一条曲线 ⇒ <b>动作</b>：在 2B 主干的可行性表里新增一行 `weight_precision ∈ {FP16, INT8, 1.58-bit}`，同时记录 `tokens_to_target_ppl`，用「达到同一 PPL 所需 token」比较，而不是只比同 token 的 PPL。<br>**zhulong（推理侧预算）**：论文的省显存主要发生在**权重**，KV cache 不受益 ⇒ <b>动作</b>：长上下文场景必须把「权重显存 / KV 显存」分列，避免把权重的 3.55× 误当端到端。<br>**harness（能力回归）**：三值模型的失败模式常在**格式遵循 / 长链推理**而非 PPL ⇒ <b>动作</b>：量化档位变更必须跑同一套 agent 任务回归，PPL 不作为唯一门槛。<br>**风险**：① 论文自述 `Work in progress`，未同行评审；② 3.55×/2.71× 的测量条件（序列长度、batch、是否含 KV）摘要未给全；③ 496 次引用低于 500 阈值，🚫 不得当「高引经典」引用。 |

首次收录: 2026-11-15（第三十七轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：10 作者、`comment` = `Work in progress`；OpenAlex `200` 496；PDF `200` 463,748 B / 8 页，`pdftotext` 核对 1.58 / {-1,0,1} / absmean / 3.55x / 2.71x / 4.1 times / 71.4 times）

---

## 145. Scaling Laws for Reward Model Overoptimization

| 字段 | 内容 |
|:--|:--|
| 标题 | Scaling Laws for Reward Model Overoptimization |
| 作者（前 3） | Leo Gao · John Schulman · Jacob Hilton（共 **3** 位） |
| 年份 | **2022**（`2022-10-19`，v1 = 最新） |
| 会议 / 期刊 | **未核验**（arXiv `comment` / `journal_ref` 均为空；OpenAlex `primary_location.source` = arXiv） |
| 被引数 | **291**（OpenAlex `10.48550/arxiv.2210.10760`，查询日 **2026-11-15**；⚠️ 低于 500 ⇒ 按「方法论常青」入选，不按高引） |
| arXiv / DOI | <https://arxiv.org/abs/2210.10760> ｜ DOI `10.48550/arxiv.2210.10760` |
| 一句话贡献 | 用一个**固定的 gold RM 冒充人类**、训练 proxy RM 的**合成实验**，量化「对 proxy 优化过度会把 gold 分数拉下来」的 overoptimization：**RL 与 best-of-n 两种优化方式服从不同的函数形式**，gold 分数随 KL 距离 `d = D_KL(π‖π_init)` 先升后降；proxy RM 参数量 / 数据量对曲线的**偏移是对数线性的**；并给出「RL 的 KL 惩罚能抬高 proxy 分数，但**不改善** gold–KL 前沿」这一反直觉结论。 |
| 与我们工作的关系 | **harness（奖励/判分不可无限优化，主目标）**：这是「评测得给上限」的定量依据 ⇒ <b>动作</b>：任何用学习型判分器（RM-as-judge）的评测，必须同时报 best-of-n 的 n 与 KL 预算，并画 gold 代理对照曲线，禁止只报 n 越大越好。<br>**zhulong（posttrain 的早停判据）**：KL 惩罚不改善真实前沿 ⇒ <b>动作</b>：RL 阶段把「proxy 分数 / 独立留出集分数 / KL」三线同图，用留出集拐点做早停，而不是用 KL 系数调参。<br>**data（合成偏好数据的边界）**：proxy RM 的数据量只带来对数级偏移 ⇒ <b>动作</b>：偏好数据扩量前先估「当前 proxy 与 gold 的差距来自数据量还是模型容量」，再决定投哪一边。<br>**风险**：① gold RM **不是人类**，合成实验的绝对值不可直接外推到真人偏好；② 291 次引用低于 500 阈值，🚫 不当高引引用；③ 会场未核验，只写 arXiv。 |

首次收录: 2026-11-15（第三十七轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：3 作者、cs.LG 主分类；OpenAlex `200` 291；PDF `200` 3,186,215 B / 28 页，`pdftotext` 核对 gold-standard / proxy / best-of-n / D_KL(π ‖ π_init) / KL penalty ineffectiveness）

---

## 146. HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units

| 字段 | 内容 |
|:--|:--|
| 标题 | HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units |
| 作者（前 3） | Wei-Ning Hsu · Benjamin Bolte · Yao-Hung Hubert Tsai（共 **6** 位，含 Kushal Lakhotia / Ruslan Salakhutdinov / Abdelrahman Mohamed；arXiv 作者字段逐字核） |
| 年份 | **2021**（`2021-06-14`，v1 = 最新） |
| 会议 / 期刊 | **IEEE/ACM Transactions on Audio, Speech, and Language Processing**（**取自 OpenAlex `primary_location.source`**，2021；arXiv `comment` / `journal_ref` 均为空 ⇒ 未按 arXiv 元数据写会场） |
| 被引数 | **3,561**（OpenAlex `10.48550/arxiv.2106.07447`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2106.07447> ｜ DOI `10.48550/arxiv.2106.07447` |
| 一句话贡献 | 不在连续波形上做重建，而是**掩码后预测「离线聚类得到的离散单元」**：先用 MFCC 做 **100 个簇**的 k-means 出伪标签，训练第一轮（**250k 步**），再用第一轮**第 6 层**输出重新聚类（**第二轮 400k 步**）；无标注数据用 **960 小时 LibriSpeech** 或 **60,000 小时 Libri-light**；三档规模 **BASE 90M / LARGE 300M / X-LARGE 1B**，X-LARGE 在 test-clean / test-other 到 **4.6% / 6.8% WER**，10 分钟标注时 LARGE 即 **4.7% / 7.6%**。 |
| 与我们工作的关系 | **vision（视觉自监督目标选型，主目标）**：这是「离散目标 + 掩码预测」最干净的工程证据 ⇒ <b>动作</b>：视觉塔对照实验加一臂 `target ∈ {pixel/feature regression, offline cluster ID}`，并记录聚类数、迭代轮数、每轮步数，用同一微调预算比较。<br>**pretrain（两阶段自举的配方）**：伪标签来自模型自己的中间层而非外部标注 ⇒ <b>动作</b>：把「第一轮步数 / 重聚类层号 / 第二轮步数」写成三个可调超参，做 1B 以下的 3 点消融，而不是一次定死。<br>**data（无标注 vs 有标注的配比）**：10 分钟 / 1 小时 / 10 小时 / 100 小时 / 960 小时五档标注预算下都报数 ⇒ <b>动作</b>：data 线按同一五档预算报告自监督预训练的收益曲线，避免只报全量标注的单一数字。<br>**风险**：① 语音与视觉的「聚类是否稳定」不可直接类比（语音有强时序平滑，视觉 token 更碎）；② 4.6%/6.8% 是 LibriSpeech 特定测试集、作者自报；③ 会场取自 OpenAlex，未在 arXiv 侧交叉验证。 |

首次收录: 2026-11-15（第三十八轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：6 作者；OpenAlex `200` 3,561；PDF `200` `application/pdf` 374,525 B / 10 页，`pdftotext` 核对 100 clusters / 250k / 400k steps / 6th layer / 960 hours / 60,000 hours Libri-light / 90M / 300M / 1B / 4.6% / 6.8% / 4.7% / 7.6%）

---

## 147. Tensor Programs V: Tuning Large Neural Networks via Zero-Shot Hyperparameter Transfer

| 字段 | 内容 |
|:--|:--|
| 标题 | Tensor Programs V: Tuning Large Neural Networks via Zero-Shot Hyperparameter Transfer |
| 作者（前 3） | Greg Yang · Edward J. Hu · Igor Babuschkin（共 **10** 位，含 Xiaodong Liu / Weizhu Chen / Jianfeng Gao；arXiv 作者字段逐字核） |
| 年份 | **2022**（`2022-03-07`，v2 `2022-03-28`） |
| 会议 / 期刊 | **NeurIPS 2021**（arXiv `comment` 原文：`NeurIPS 2021`） |
| 被引数 | **302**（OpenAlex `10.48550/arxiv.2203.03466`，查询日 **2026-11-15**；⚠️ 低于 500 ⇒ 按「开创范式（超参迁移 / μP）」入选，不按高引） |
| arXiv / DOI | <https://arxiv.org/abs/2203.03466> ｜ DOI `10.48550/arxiv.2203.03466` |
| 一句话贡献 | 提出 **μP（maximal update parametrization，最大更新参数化）**：在 `abc`-参数化族里选出让「每层更新幅度不随宽度变化」的那一支，于是**最优学习率等超参在宽度方向可零样本迁移**；Transformer 上还要把注意力从 `1/√d` 改成 **`1/d`**（`qᵀk/d`）；实验在宽度 **128 → 8192** 上验证，并从 **40M 参数调到 6.7B**（作者称超过已发表的 6.7B GPT-3 数字，调参开销仅占预训练算力 **7%**）。 |
| 与我们工作的关系 | **pretrain（省掉大模型 LR 扫参，主目标）**：2B 主跑的调参预算本来就紧 ⇒ <b>动作</b>：先在 20–50M 代理模型上按 μP 规则调 `lr`、`init std`、`attention multiplier`，再**零样本迁移**到 2B，主跑只验证不扫参。<b>预注册判据</b>：若迁移后 2B 前 100B token 的 loss 曲线不劣于「手工按宽度经验缩放」的对照，则把 μP 写进默认配方。<br>**harness（评测口径）**：超参口径不同会让「模型对比」变成「调参对比」⇒ <b>动作</b>：所有消融在评测卡里写明是 `SP（standard parametrization）还是 μP`、代理模型宽度、迁移了哪些超参。<br>**zhulong（RL 重启成本）**：RL 阶段频繁改模型宽度 / 恢复训练时，μP 让旧超参仍可用 ⇒ <b>动作</b>：把「宽度变更后是否需要重扫 `lr`」列为 RL 实验清单的一项。<br>**风险**：① 302 次引用低于 500 阈值，🚫 不当高引经典引用；② 理论保证是**宽度极限**下的一阶结论，深度 / 数据分布变化不保证；③ 6.7B 数字是作者自报、依赖具体基线实现。 |

首次收录: 2026-11-15（第三十八轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：10 作者、`comment` = `NeurIPS 2021`；OpenAlex `200` 302；PDF `200` `application/pdf` 3,195,677 B / 48 页，`pdftotext` 核对 `abc-parameterization` / `1/d attention` / 宽度 128–8192 / 40M → 6.7B / 7% of total pretraining cost）

---

## 148. Training Verifiers to Solve Math Word Problems

| 字段 | 内容 |
|:--|:--|
| 标题 | Training Verifiers to Solve Math Word Problems |
| 作者（前 3） | Karl Cobbe · Vineet Kosaraju · Mohammad Bavarian（共 **12** 位，含 Lukasz Kaiser / Jacob Hilton / John Schulman；arXiv 作者字段逐字核） |
| 年份 | **2021**（`2021-10-27`，v2 `2021-11-18`） |
| 会议 / 期刊 | **预印本**（arXiv `comment` / `journal_ref` 均为空；OpenAlex `type` = `preprint`） |
| 被引数 | **11,462**（OpenAlex `10.48550/arxiv.2110.14168`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2110.14168> ｜ DOI `10.48550/arxiv.2110.14168` |
| 一句话贡献 | 发布 **GSM8K**（**8.5K** 道语言多样的小学数学应用题，人工编写、带分步解答），并提出**验证器路线**：生成器采样多条候选解，用单独训练的 verifier 打分重排；结论是「**验证比生成更容易随模型规模扩展**」（同规模下 verifier 重排优于纯微调），且**验证器必须与生成器分开训练**以免生成器过拟合；6B 模型若直接输出答案不写中间步骤，test@1 从 **20.6% 掉到 5.2%**；随训练轮数增加 test@1 近似单调上升，但 **test@100 下降更快**（过拟合先伤多样性）。 |
| 与我们工作的关系 | **harness（「判分器可被刷到什么程度」的定量源头，主目标）**：这是 best-of-n + 学习型判分的原始证据 ⇒ <b>动作</b>：agent 评测里凡使用 verifier 重排，必须同时报 `n`（采样数）与 `test@1 / test@n` 两条曲线，禁止只报最优 n。<br>**zhulong（推理预算的边界）**：验证器把算力换成准确率，但收益随模型变大而变 ⇒ <b>动作</b>：在 2B 级上先做「n ∈ {1, 4, 16, 64} × 是否独立 verifier」的小网格，找到收益拐点再决定 RL 阶段的采样预算。<br>**data（合成数据的自洽性）**：verifier 需要正负样本，且与生成器隔离 ⇒ <b>动作</b>：data 线把「生成器轨迹 / 验证器训练集」的来源与重叠率单列，作为合成数据质量表的一列。<br>**风险**：① 11,462 引用里含大量「引用 GSM8K 数据集」而非方法本身，🚫 不可当方法被验证了上万次；② 论文明确 verifier 会因**题意歧义**误判（正文有正确解被判错的例子）；③ 预印本，无同行评审版本可核。 |

首次收录: 2026-11-15（第三十八轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：12 作者；OpenAlex `200` 11,462；PDF `200` `application/pdf` 2,935,719 B / 22 页，`pdftotext` 核对 8.5K / 20.6% → 5.2% / test@1 / test@100 / separate generator and verifier）

---

## 149. Emergent Abilities of Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Emergent Abilities of Large Language Models |
| 作者（前 3） | Jason Wei · Yi Tay · Rishi Bommasani（共 **16** 位，含 Colin Raffel / Percy Liang / Jeff Dean / William Fedus；arXiv 作者字段逐字核） |
| 年份 | **2022**（`2022-06-15`，v2 `2022-10-26`） |
| 会议 / 期刊 | **TMLR 08/2022**（arXiv `comment` 原文：`Transactions on Machine Learning Research (TMLR), 2022`；PDF 页眉亦印 `Published in Transactions on Machine Learning Research (08/2022)`） |
| 被引数 | **4,208**（OpenAlex `10.48550/arxiv.2206.07682`，查询日 **2026-11-15**） |
| arXiv / DOI | <https://arxiv.org/abs/2206.07682> ｜ DOI `10.48550/arxiv.2206.07682` |
| 一句话贡献 | 把「**在小模型上不存在、在大模型上突然出现**」的能力定义为 **emergent ability**，用 8 个 few-shot 任务（BIG-Bench 的 200+ 任务子集、算术、指令跟随等）展示曲线是**台阶式**而非平滑上升：如 3 位数加减在 GPT-3 **13B（2×10²² FLOPs）**、LaMDA **68B（10²³）** 之前接近零；WiC 要到 PaLM **540B（2.5×10²⁴ FLOPs）** 才过随机；并指出**评测指标的粒度会改变「是否涌现」的判断**（不给部分分的指标会把渐变看成突变）。 |
| 与我们工作的关系 | **pretrain（规模预期管理）**：2B 级不能假定「大模型能力按比例缩小」⇒ <b>动作</b>：预训练里程碑评审把预期能力分「可外推（PPL 类）」与「不可外推（多步推理 / 指令跟随）」两栏，后者只按实测、不按曲线外推。<br>**harness（指标粒度，主目标）**：给部分分 vs 全对全错会直接决定「有没有涌现」⇒ <b>动作</b>：同一套 agent 任务同时报 `exact-match / 部分分 / pass@k` 三种口径，任何「能力跃迁」结论必须三口径一致才写进日报。<br>**data（任务覆盖）**：8 个任务取自 BIG-Bench 等公开集 ⇒ <b>动作</b>：data 线在配比表里标注「任务族覆盖」，避免只按领域名配比而漏掉能力族。<br>**风险**：① 论文自述**不提出新方法**、只做文献归纳，且「涌现不可预测」本身在 2023–2024 受到「指标选择造成假象」的质疑 ⇒ 引用时必须一并给出该争议；② FLOPs 与参数量的对应取自各原始论文，口径不完全统一；③ 台阶形状依赖具体 few-shot 设置。 |

首次收录: 2026-11-15（第三十八轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：16 作者、`comment` = `Transactions on Machine Learning Research (TMLR), 2022`；OpenAlex `200` 4,208；PDF `200` `application/pdf` 842,905 B / 30 页，`pdftotext` 核对 13B / 2 · 10²² / 68B / 10²³ / 540B / 2.5 · 10²⁴ / BIG-Bench over 200 benchmarks / partial credit）

---

## 150. Longformer: The Long-Document Transformer

| 字段 | 内容 |
|:--|:--|
| 标题 | Longformer: The Long-Document Transformer |
| 作者（前 3） | Iz Beltagy · Matthew E. Peters · Arman Cohan（共 **3** 位；arXiv 作者字段逐字核） |
| 年份 | **2020**（`2020-04-10`，v2 `2020-12-02`，v2 增加 LED） |
| 会议 / 期刊 | **预印本**（arXiv `journal_ref` 为空；OpenAlex 出版源显示 `arXiv (Cornell University)`） |
| 被引数 | **6,470**（OpenAlex `10.48550/arxiv.2004.05150`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2004.05150> ｜ DOI `10.48550/arxiv.2004.05150` |
| 一句话贡献 | 把 self-attention 换成「**滑动窗口（w = 512，与 RoBERTa 等算力）+ 按 head 配置的 dilation + 少量任务相关的 global attention**」组合，复杂度从 O(n²) 降到 **O(n)**；位置编码用「把 RoBERTa 的 512 个学习式位置编码**复制**扩到 4,096」的办法续上，避免从头学长程位置；v2 给出 encoder-decoder 版 **LED**（23 处提及）用于长文档生成。 |
| 与我们工作的关系 | **pretrain（长上下文续训，主目标）**：2B 模型要喂进整份时序报告 / 网表摘要，全注意力在 30k token 上不可行 ⇒ <b>动作</b>：把「窗口 + dilation + 少量 global token」作为长上下文 baseline 之一，与 RoPE 插值对照，判据用「训练长度之外的 PPL 是否先崩」。<br>**harness / zhulong（长文档输入的成本口径）**：global attention 钉在哪些 token，等价于「让模型看哪里」，直接影响长文档任务的成本与可解释性 ⇒ <b>动作</b>：评测 agent 读长设计文档时，把 global token 的选择规则（结构标记 vs 学习型 slot）记为一列元数据，禁止只报总分。<br>**风险**：① 6,470 引用中含大量「长文档 baseline」式引用，不等于方法在长上下文上最优（2023 后 RoPE 插值 / FlashAttention 路线已改写默认选项）；② 预印本无正式评审版本；③ 复制位置编码的做法只在 ≤4,096 被验证过。 |

首次收录: 2026-11-16（第三十九轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：3 作者、`comment` = `Version 2 introduces the Longformer-Encoder-Decoder (LED) model`；OpenAlex `200` 6,470；PDF `200` `application/pdf` 539,211 B / 17 页，`pdftotext` 核对 `window size of 512` / `dilation` 14 处 / `O(n)` / `2,048` / `copy position embeddings` / `position 4,096`）

---

## 151. Flamingo: a Visual Language Model for Few-Shot Learning

| 字段 | 内容 |
|:--|:--|
| 标题 | Flamingo: a Visual Language Model for Few-Shot Learning |
| 作者（前 3） | Jean-Baptiste Alayrac · Jeff Donahue · Pauline Luc（共 **27** 位，含 Antoine Miech；arXiv 作者字段逐字核） |
| 年份 | **2022**（`2022-04-29`，v2 `2022-11-15`） |
| 会议 / 期刊 | **NeurIPS 2022**（arXiv `comment` 原文：`54 pages. In Proceedings of Neural Information Processing Systems (NeurIPS) 2022`） |
| 被引数 | **2,333**（OpenAlex `10.48550/arxiv.2204.14198`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2204.14198> ｜ DOI `10.48550/arxiv.2204.14198` |
| 一句话贡献 | 用「**冻结的语言模型 + Perceiver Resampler（把变长视觉特征压成固定数量 latent）+ 层间插入的 GATED XATTN-DENSE 交叉注意力**」把图像/视频接进 80B LM（`80B` 11 处），只在 **43 million** 网页图文交错数据上训练，就能在 16 个多模态任务上做 few-shot；消融显示 **0 初始化的 tanh gating 是必需项**（去掉后总分掉 **4.2%** 并出现训练不稳），**每层插一块**优于隔层插但更贵。 |
| 与我们工作的关系 | **vision（域内图文对稀少时的架构选择，主目标）**：数万张版图 / SEM / 波形图 + 冻结 LM 的设定与 Flamingo 最接近 ⇒ <b>动作</b>：vision 线做「Resampler latent 数 ∈ {32, 64, 128} × gating 是否 0 初始化」的小网格，先确认瓶颈是 latent 数还是数据量。<br>**pretrain（跨模态注入的冷启动）**：0 初始化门控是可复现的稳定化手段 ⇒ <b>动作</b>：pretrain 线在「冻结主干 + 新增适配层」的任何实验里默认把新增门控参数零初始化，并写进配置模板。<br>**风险**：① 80B / 43M 网页数据的规模在 2B 上不可直接外推；② 论文自述 interleaved 数据不可公开，配比无法复现；③ 2,333 引用里含大量「多模态 baseline」引用。 |

首次收录: 2026-11-16（第三十九轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：27 作者；OpenAlex `200` 2,333；PDF `200` `application/pdf` 31,579,390 B / 54 页，`pdftotext` 核对 `80B` / `43 million` / `Perceiver Resampler` 23 处 / `tanh gating` 9 处 / `alpha_xattn … init at 0` / 去掉 0 初始化掉 `4.2%` 且训练不稳）

---

## 152. RoBERTa: A Robustly Optimized BERT Pretraining Approach

| 字段 | 内容 |
|:--|:--|
| 标题 | RoBERTa: A Robustly Optimized BERT Pretraining Approach |
| 作者（前 3） | Yinhan Liu · Myle Ott · Naman Goyal（共 **10** 位，含 Jingfei Du；arXiv 作者字段逐字核） |
| 年份 | **2019**（`2019-07-26`，仅有 v1） |
| 会议 / 期刊 | **预印本**（arXiv `comment` 与 `journal_ref` 均为空；OpenAlex 出版源为 `arXiv (Cornell University)`） |
| 被引数 | **33,672**（OpenAlex `10.48550/arxiv.1907.11692`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/1907.11692> ｜ DOI `10.48550/arxiv.1907.11692` |
| 一句话贡献 | 证明「**BERT 是被显著训练不足的**」（`significantly undertrained` 2 处），给出更稳的预训练配方：**动态掩码**（每步重新生成掩码）、**去掉 NSP** 改用整段句子、**160GB** 语料（原文 16GB 的 10 倍）、**batch 8K × 500K steps**、byte-level BPE；不改模型结构即可超过同期 BERT 变体。 |
| 与我们工作的关系 | **pretrain（配方等价性清单，主目标）**：这是「同样的算力，改配方比改结构更划算」的原始证据 ⇒ <b>动作</b>：2B 主跑把「动态掩码 / 去 NSP / 数据量 ×10 / 大 batch + 长步数」逐项做成单变量消融表，任一项不做必须写明理由。<br>**data（语料规模的阈值感）**：160GB 是当时可复现的最大公开混合语料 ⇒ <b>动作</b>：data 线在配比表里同时记「原始语料 GB」与「去重后 GB」，避免用去重前体积对外比较。<br>**风险**：① 33,672 引用中含大量「base 模型就是 RoBERTa」的顺手引用；② 结论绑定在 2019 年的算力与数据可得性上，不能直接搬到 2B / 中文 / 代码语料；③ 预印本，无正式评审版本。 |

首次收录: 2026-11-16（第三十九轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：10 作者；OpenAlex `200` 33,672；PDF `200` `application/pdf` 209,675 B / 13 页，`pdftotext` 核对 `160GB` 6 处 / `dynamic masking` 4 处 / `batch size of 8K` / `500K steps` 2 处 / `significantly undertrained`）

---

## 153. Emerging Properties in Self-Supervised Vision Transformers

| 字段 | 内容 |
|:--|:--|
| 标题 | Emerging Properties in Self-Supervised Vision Transformers |
| 作者（前 3） | Mathilde Caron · Hugo Touvron · Ishan Misra（共 **7** 位，含 Hervé Jégou；arXiv 作者字段逐字核） |
| 年份 | **2021**（`2021-04-29`，v2 `2021-05-24`） |
| 会议 / 期刊 | **ICCV 2021**（arXiv `comment` 仅 `21 pages`；出版源取自 OpenAlex = `IEEE/CVF International Conference on Computer Vision (ICCV)`） |
| 被引数 | **7,104**（OpenAlex `10.48550/arxiv.2104.14294`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2104.14294> ｜ DOI `10.48550/arxiv.2104.14294` |
| 一句话贡献 | **DINO**：把「**无标签自蒸馏**（student 走梯度分支、teacher 用 momentum encoder）+ **multi-crop** + **centering / sharpening 防塌缩**」用到 ViT 上，得到的特征既是强 k-NN 分类器（小 ViT 上 ImageNet **78.3%** top-1），又自带语义分割式的显式结构；并指出 momentum encoder、multi-crop、小 patch 是三个关键项。 |
| 与我们工作的关系 | **vision（自监督视觉塔的原始配方，主目标）**：域内标注图稀少时，「先自监督预训练编码器再接线」比纯监督更抗过拟合 ⇒ <b>动作</b>：vision 线把 DINO 式 self-distillation 作为编码器初始化候选，与「冻结 CLIP/SigLIP」并列对照，判据用下游 agent 任务而非线性探测。<br>**pretrain（防塌缩的两个旋钮）**：centering（teacher 输出中心化）与 sharpening（低温 softmax）可直接搬运 ⇒ <b>动作</b>：pretrain 线在任何 teacher-student 结构里把这两个超参显式写进配置（默认值取本文），不靠框架默认。<br>**data（无标注数据的用法）**：只用 ImageNet 无标签数据即得可用特征 ⇒ <b>动作</b>：data 线单列「可无标注使用」的图像池规模，作为 vision 自监督的数据口径。<br>**风险**：① 78.3% 是**小 ViT + k-NN** 口径，不等于线性探测或下游任务 SOTA；② momentum teacher 需额外显存与两次前向，2B 级训练的吞吐代价文中未给；③ ICCV 会场取自 OpenAlex（arXiv `journal_ref` 为空）。 |

首次收录: 2026-11-16（第三十九轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：7 作者；OpenAlex `200` 7,104 且源为 ICCV；PDF `200` `application/pdf` 30,930,829 B / 21 页，`pdftotext` 核对 `78.3%` 3 处 / `momentum encoder` 14 处 / `multi-crop` 32 处 / `centering` 22 处 / `sharpening` 13 处 / `self-distillation`）

---

## 154. Small-scale proxies for large-scale Transformer training instabilities

| 字段 | 内容 |
|:--|:--|
| 标题 | Small-scale proxies for large-scale Transformer training instabilities |
| 作者（前 3） | Mitchell Wortsman · Peter J. Liu · Lechao Xiao（共 **16** 位；arXiv 作者字段逐字核） |
| 年份 | **2023**（`2023-09-25`，v2 `2023-10-16`） |
| 会议 / 期刊 | **ICLR**（arXiv `comment` 与 `journal_ref` 均为空；`venue` 取自 Semantic Scholar，但 S2 未给届次年份 ⇒ **不代填年份**） |
| 被引数 | **218**（Semantic Scholar Graph `arXiv:2309.14322`，查询日 **2026-11-16**；⚠️ 本轮 OpenAlex 返回 `429`（免费额度用尽）⇒ 改用 S2，口径与往轮 OpenAlex 不同） |
| arXiv / DOI | <https://arxiv.org/abs/2309.14322> ｜ DOI `10.48550/arxiv.2309.14322` |
| 一句话贡献 | 提出用「**LR sensitivity**」（学习率 vs 损失的敏感度）作为跨规模诊断量：两类在大模型上出现的训练不稳（**attention logit growth** 与 **output logit divergence**）在小模型以高学习率训练时同样出现；**qk-layernorm** 与 **z-loss（系数 1e-4）** 能降低 LR sensitivity 并使训练稳定，且不稳可在其显性出现前被预测。 |
| 与我们工作的关系 | **pretrain（稳定性判据，主目标）**：2B 主跑最大的隐性成本是「跑完 3 天才发现不稳」⇒ <b>动作</b>：把「小模型 × 三档学习率」的 LR sensitivity 扫描做成 2B 主跑前的**预注册探针**，判据 = 目标 LR 处 sensitivity 是否落在小模型稳定区；不稳时先试 qk-layernorm，再试 z-loss 1e-4。<br>**data / zhulong（不稳的成本口径）**：不稳浪费的算力要单列 ⇒ <b>动作</b>：实验记录新增「不稳导致的重复训练 GPU 小时」一列，与最终 loss 并列。<br>**风险**：① 218 引用（S2 口径）远低于同期方法论文，属「工程报告」性质；② 结论绑定 decoder-only Transformer + AdamW 的默认配置，换优化器 / 换归一化位置需重测；③ 预印本 + ICLR 会场为二手字段，未见正式 proceedings 页码。 |

首次收录: 2026-11-16（第四十轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：16 作者、`published=2023-09-25T17:48:51Z`、`updated=2023-10-16T18:43:25Z`；S2 `200` 218；PDF `200` `application/pdf` 10,685,777 B，`pdftotext` 核对 `LR sensitivity` / `qk-layernorm` / `z-loss` / `coefficient 1e-4` / `attention logit growth` / `divergence of the output logits`）

---

## 155. DataComp: In search of the next generation of multimodal datasets

| 字段 | 内容 |
|:--|:--|
| 标题 | DataComp: In search of the next generation of multimodal datasets |
| 作者（前 3） | Samir Yitzhak Gadre · Gabriel Ilharco · Alex Fang（共 **34** 位，含 Ludwig Schmidt；arXiv 作者字段逐字核） |
| 年份 | **2023**（`2023-04-27`，v2 `2023-10-20`） |
| 会议 / 期刊 | **NeurIPS 2023 Datasets and Benchmarks Track**（arXiv `comment` 原文逐字） |
| 被引数 | **821**（Semantic Scholar Graph `arXiv:2304.14108`，查询日 **2026-11-16**；OpenAlex 本轮 `429`） |
| arXiv / DOI | <https://arxiv.org/abs/2304.14108> ｜ DOI `10.48550/arxiv.2304.14108` |
| 一句话贡献 | 把「图文数据筛选」变成可比基准：公开 **CommonPool 12.8B** 图文对 + **四档算力规模（12.8M → 12.8B 候选池）**，固定 CLIP ViT-B/32 训练预算下比 filter；结论是**过滤方法的排序跨规模大体一致**（可小规模选型）、12.8B 档最优过滤比不过滤 **+6.9pp** ImageNet 零样本、组合两个最优过滤得到 **DataComp-1B** 训练 CLIP ViT-L/14 达 **79.2%**；BYOD 轨道追加 **109M**（<1% 池）数据可再 **+1.2pp**。 |
| 与我们工作的关系 | **data（过滤基线与规模一致性，主目标）**：域内数据少时最贵的问题是「该不该重过滤」⇒ <b>动作</b>：data 线先用同比例缩小规模比较 2–3 种过滤策略，再上 2B 主跑；判据 = 小规模排序与主跑排序是否一致（本文证据支持一致，但需在本域复核）。<br>**vision（图文对质量口径）**：CLIP 分数过滤不是万灵药，需报「过滤后保留率」⇒ <b>动作</b>：图文对登记表新增「过滤前 / 后条数 + CLIP 阈值」，禁止只报最终条数。<br>**风险**：① 79.2% 是 CLIP ViT-L/14 + 1.4B 训练样本的特定组合，不能直接搬到 2B 语言模型；② 结论以英文网页图文为主，半导体 / 工程图文分布差异大；③ 34 人作者名单意味着后续维护与版本可能分叉。 |

首次收录: 2026-11-16（第四十轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：34 作者、`comment=NeurIPS 2023 Datasets and Benchmarks Track`；S2 `200` 821；PDF `200` `application/pdf` 2,783,491 B，`pdftotext` 核对 `12.8B` / `12.8M` / `+6.9 percentage points` / `79.2%` / `109M` / `rankings … consistent across scale`）

---

## 156. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

| 字段 | 内容 |
|:--|:--|
| 标题 | AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation |
| 作者（前 3） | Qingyun Wu · Gagan Bansal · Jieyu Zhang（共 **14** 位，含 Chi Wang；arXiv 作者字段逐字核） |
| 年份 | **2023**（`2023-08-16`，v2 `2023-10-03`） |
| 会议 / 期刊 | **预印本**（arXiv `comment` 仅 `43 pages (10 pages for the main text, …)`；Semantic Scholar `venue` 为空） |
| 被引数 | **3,218**（Semantic Scholar Graph `arXiv:2308.08155`，查询日 **2026-11-16**；OpenAlex 本轮 `429`） |
| arXiv / DOI | <https://arxiv.org/abs/2308.08155> ｜ DOI `10.48550/arxiv.2308.08155` |
| 一句话贡献 | 提出 **conversable agent**（每个 agent 可自主多轮对话、也可按需请求人类输入）+ **conversation programming**（用自然语言与代码两种方式编排对话流程）+ 内置代码执行器；把多 agent 协作统一成「对话」这一原语，示例在 MATH 上以交互式检索 + 代码执行达 **69.48%**（同文对比 GPT-4 单模型 **55.18%**）。 |
| 与我们工作的关系 | **harness（多 agent 编排原语，主目标）**：我们的 harness 需要「写→跑→改」的闭环 ⇒ <b>动作</b>：把「发言权轮转 + 工具执行 + 人工介入点」三项抽成可配置对象，先把单 agent 的失败模式分类（工具返回空 / 解析失败 / 循环），再加第二个 agent。<br>**zhulong（成本口径）**：对话式多 agent 的代价是 token 倍增 ⇒ <b>动作</b>：任何多 agent 实验必须同时报「每任务 token / 工具调用次数 / 成功率的分子分母」，禁止只报成功率。<br>**风险**：① 3,218 引用含大量框架式引用，不等于方法优越；② MATH 69.48% 依赖 GPT-4 + 交互式检索的特定组合，与开源小模型不可比；③ 框架本身后来有重大 API 变更，复现需锁版本。 |

首次收录: 2026-11-16（第四十轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：14 作者、`comment` 43 页；S2 `200` 3,218；PDF `200` `application/pdf` 3,571,809 B，`pdftotext` 核对 `conversable` / `69.48%` / `55.18%` / `conversation programming`）

---

## 157. Ring Attention with Blockwise Transformers for Near-Infinite Context

| 字段 | 内容 |
|:--|:--|
| 标题 | Ring Attention with Blockwise Transformers for Near-Infinite Context |
| 作者（前 3） | Hao Liu · Matei Zaharia · Pieter Abbeel（共 **3** 位；arXiv 作者字段逐字核） |
| 年份 | **2023**（`2023-10-03`，v2 `2023-11-27`） |
| 会议 / 期刊 | **ICLR**（arXiv `comment` 仅给代码链接；`venue` 取自 Semantic Scholar，但 S2 未给届次年份 ⇒ **不代填年份**） |
| 被引数 | **656**（Semantic Scholar Graph `arXiv:2310.01889`，查询日 **2026-11-16**；OpenAlex 本轮 `429`） |
| arXiv / DOI | <https://arxiv.org/abs/2310.01889> ｜ DOI `10.48550/arxiv.2310.01889` |
| 一句话贡献 | 把 self-attention 与 FFN 都**分块**算，并在设备间组成**环**传递 KV 块（传输与计算重叠，配对块计算量 ≥ 传输量时零额外开销），从而把「序列维」也从单卡显存里拿出来；在**不做近似**的前提下比此前 memory-efficient 方案支持**长 500 倍以上**的序列，可训练 **>100M token**（示例：batch=1 处理 100M token 原本要 **>1000GB**，环式后可放进 **100GB HBM**）。 |
| 与我们工作的关系 | **pretrain（长上下文的主选项对照，主目标）**：RoPE 插值 / 窗口注意力都是「改模型」，Ring Attention 是「改并行」⇒ <b>动作</b>：长上下文实验表新增一行「并行策略（DP/TP/环式）」；判据 = 目标长度下有效吞吐（token/s/卡）与 PPL，不能只报可支持长度。<br>**zhulong（成本口径）**：文章把瓶颈从算力换成**卡间带宽** ⇒ <b>动作</b>：成本表把「KV 块传输字节 / 每 token」单列，与 DRAM 字节数并列。<br>**harness（长文档输入）**：真·百万 token 输入可行后，评测要改成「必须跨块引用」的题，否则长上下文只是摆设。<br>**风险**：① 656 引用（S2 口径）低于同期 FlashAttention 系；② 零开销的前提是「块计算 ≥ 块传输」，低带宽互联（如以太网）下不成立；③ 需要多卡，单卡小规模实验无法验证。 |

首次收录: 2026-11-16（第四十轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：3 作者、`comment` 给代码 `github.com/lhao499/llm_large_context`；S2 `200` 656 + venue ICLR；PDF `200` `application/pdf` 1,766,025 B，`pdftotext` 核对 `blockwise` / `500 times longer` / `100 million` / `1000GB` / `100GB of high-bandwidth memory`）

---

## 158. Gorilla: Large Language Model Connected with Massive APIs

| 字段 | 内容 |
|:--|:--|
| 标题 | Gorilla: Large Language Model Connected with Massive APIs |
| 作者（前 3） | Shishir G. Patil · Tianjun Zhang · Xin Wang（共 **4** 位，末位 Joseph E. Gonzalez；arXiv `id_list` 作者字段逐字核） |
| 年份 | **2023**（`2023-05-24`） |
| 会议 / 期刊 | **NeurIPS**（arXiv `comment` 为空；`venue` 取自 OpenAlex `primary_location.source`，`type=conference`，未给届次年份 ⇒ **不代填年份**） |
| 被引数 | **1,151**（OpenAlex `10.48550/arxiv.2305.15334`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2305.15334> ｜ DOI `10.48550/arxiv.2305.15334` |
| 一句话贡献 | 用 LLaMA-7B 微调出「调用百万级真实 API」的模型，并给出可自动判分的 **APIBench**（TorchHub / TensorHub / HuggingFace 三个来源）；判分靠 **AST 子树立匹配**（只匹配 `repo_or_dir` / `model` 等登记键，`pretrained=True` 这类可选参数不参与），同时把「调用了数据库里不存在的 API」单列为 **hallucination**、与「调用错参数」的 error 区分；再把检索文档拼进训练指令（**Retrieval-Aware Training**），使模型能跟上文档版本变化。 |
| 与我们工作的关系 | **harness（工具调用判分口径，主目标）**：把「幻觉」与「错误」拆成两类再分别报，是评测表该有的粒度 ⇒ <b>动作</b>：工具调用评测加两列 `unknown-tool rate` / `wrong-arg rate`，并要求判分器说明「哪些参数参与匹配、哪些忽略」。<br>**data（中文 API 文档可行性）**：RAT 依赖文档可检索且可截断 ⇒ <b>动作</b>：先做「中文文档 BM25 命中率」小实验（50 个常用库），命中率 &lt;60% 就不要急着训 RAT。<br>**pretrain（规模）**：论文是 7B；2B 是否仍能吃下 RAT 的增益未知 ⇒ <b>动作</b>：2B / 7B 各训一版，判据 = unknown-tool rate 的相对降幅，而不是总准确率。<br>**风险**：① APIBench 是自建 **16,450 条 {instruction, API} 对**（HuggingFace 过滤后 **925** 个模型 + TF Hub v2 **626** 个 + TorchHub），规模远小于真实工具生态；② AST 匹配的「登记键」是人工选择，换一组键数会变；③ 论文未给 2B 级结果。 |

首次收录: 2026-11-16（第四十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` 查询得 `published=2023-05-24T17:41:29Z`、4 作者、`comment` 空；OpenAlex `200` 1,151 / venue NeurIPS；PDF `200` `application/pdf` 1,247,664 B / 18 页，`pdftotext` 核对 `AST sub-tree` / `retrieval-aware` / `pretrained=True` / `APIBench`）

---

## 159. Let's Verify Step by Step

| 字段 | 内容 |
|:--|:--|
| 标题 | Let's Verify Step by Step |
| 作者（前 3） | Hunter Lightman · Vineet Kosaraju · Yura Burda（共 **10** 位；含 Jan Leike / John Schulman / Ilya Sutskever / Karl Cobbe；arXiv `id_list` 逐字核） |
| 年份 | **2023**（`2023-05-31`；仅 v1） |
| 会议 / 期刊 | **arXiv 预印本**（`comment` 为空；OpenAlex `type=preprint`）⇒ 其他渠道所称会议版本本轮**未取得一手出处**，不写 |
| 被引数 | **2,226**（OpenAlex `10.48550/arxiv.2305.20050`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2305.20050> ｜ DOI `10.48550/arxiv.2305.20050` |
| 一句话贡献 | 把「奖励每一步推理」与「只看最终答案」直接对比：在同一生成器上，**过程监督 PRM 78.2% / 结果监督 ORM 72.4% / 多数投票 69.6%**（best-of-1860，500 道 MATH 测试题），并用**主动学习**把标注效率提高 **2.6×**，同时公开 **PRM800K**（80 万条 step-level 人工标签）。作者自陈该数据集被主动学习偏置到「答案错误」一侧。 |
| 与我们工作的关系 | **posttrain（推理后训练的主对照，主目标）**：给了「过程奖励值不值标注成本」的第一个可量化答案 ⇒ <b>动作</b>：后训练实验表加一行「奖励粒度（outcome / step）」，判据 = 同等标注预算下的 pass@1 与标注人时。<br>**zhulong（thinking 轴）**：PRM 只做 reranker 也能涨 5.8 个点（72.4 → 78.2），这条「不加训练、只加挑选」的路线成本更低 ⇒ <b>动作</b>：先在推理评测上跑 PRM reranker 基线，再决定是否进 RL。<br>**harness（评测口径）**：「first mistake」判据在 MATH 上良定义，换到 Verilog / EDA 流程未必 ⇒ <b>动作</b>：造题时标注「错误可定位步数」，只对 ≤2 步可定位的题采 step label。<br>**风险**：① 只覆盖 MATH，且 best-of-N 的收益随 N 饱和；② PRM800K 有主动学习偏置，直接照抄配比会带来分布偏差；③ 作者群已有多人离开 OpenAI，维护状态未知。 |

首次收录: 2026-11-16（第四十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：10 作者、`published=2023-05-31T17:24:00Z`、`comment` 空；OpenAlex `200` 2,226；PDF `200` 4,384,742 B / 29 页，`pdftotext` 核对 `78.2` / `72.4` / `69.6` / `PRM800K` / `2.6×`）

---

## 160. Qwen2.5-VL Technical Report

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen2.5-VL Technical Report |
| 作者（前 3） | Shuai Bai · Keqin Chen · Xuejing Liu（共 **27** 位，署名 **Qwen Team, Alibaba Group**；arXiv `id_list` 逐字核） |
| 年份 | **2025**（`2025-02-19`；仅 v1） |
| 会议 / 期刊 | **技术报告 / arXiv 预印本**（`comment` 为空；OpenAlex `type=preprint`） |
| 被引数 | **8,551**（OpenAlex `10.48550/arxiv.2502.13923`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2502.13923> ｜ DOI `10.48550/arxiv.2502.13923` |
| 一句话贡献 | 一套可直接照抄的**原生动态分辨率**视觉语言配方：视觉端从零训 ViT（patch `stride 14`、窗口 **112×112 = 8×8 patch** 的 window attention，小于窗口的区域不补齐），时间端把 **MRoPE 对齐到绝对时间**并配 **dynamic FPS** 采样以支持小时级视频；预训练语料从 **1.2T 扩到 4.1T token**。 |
| 与我们工作的关系 | **vision（视觉编码器配方，主目标）**：native dynamic resolution + window attention 是我们正在比较的两条路线 ⇒ <b>动作</b>：视觉消融表把「初始化（CLIP / 从零）」与「注意力（全图 / 窗口）」拆成 2×2，判据 = 固定视觉 token 预算下的 OCR 与文档理解分数。<br>**pretrain（多模态 token 配比）**：4.1T 里视觉占多少论文未直接给 ⇒ <b>动作</b>：我们自己按「图像 token / 文本 token」分开记账，别只报总 token。<br>**data（中英图文配比）**：中文 OCR 与文档理解是强项，说明中文图文数据质量关键 ⇒ <b>动作</b>：数据线建「中文文档截图 → OCR 标注」子集并做污染检查。<br>**风险**：① 技术报告，未给消融的绝对训练成本；② 从零训 ViT 需要大量图文对，2B 级复现未必划算；③ 8,551 引用含大量「用它当基座」的引用，不等于方法被独立验证。 |

首次收录: 2026-11-16（第四十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：27 作者、`published=2025-02-19T18:00:14Z`、`comment` 空；OpenAlex `200` 8,551；PDF `200` 2,219,929 B / 23 页，`pdftotext` 核对 `window attention` / `112×112` / `stride of 14` / `absolute time` / `4.1 trillion`）

---

## 161. DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

| 字段 | 内容 |
|:--|:--|
| 标题 | DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model |
| 作者（前 3） | DeepSeek-AI · Aixin Liu · Bei Feng（共 **157** 位；arXiv `id_list` 逐字核） |
| 年份 | **2024**（`2024-05-07`，v5 `2024-06-19`） |
| 会议 / 期刊 | **技术报告 / arXiv 预印本**（`comment` 为空；OpenAlex `type=preprint`） |
| 被引数 | **1,552**（OpenAlex `10.48550/arxiv.2405.04434`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2405.04434> ｜ DOI `10.48550/arxiv.2405.04434` |
| 一句话贡献 | 给出「**236B 总参 / 21B 激活**」的 MoE 配方，核心是 **MLA（Multi-head Latent Attention）**：对 KV 做低秩联合压缩，使 **KV cache 减少 93.3%**、最大生成吞吐提升 **5.76×**，并在 **8.1T token** 上预训练的同时**节省 42.5% 训练成本**（相对同规模稠密模型）。 |
| 与我们工作的关系 | **pretrain（架构与成本口径，主目标）**：MLA 是「省 KV cache」而非「省参数」⇒ <b>动作</b>：2B 级实验里把 `KV cache 字节/token` 作为一等指标记录，与 PPL 同表；判据 = 同等显存下可服务的并发数。<br>**zhulong（成本口径）**：论文把「训练成本 −42.5%」与「吞吐 ×5.76」分开报，这种拆法可直接搬到我们的成本表 ⇒ <b>动作</b>：成本表分「训练侧」与「推理侧」两栏，不合并成「效率提升」。<br>**data**：8.1T 语料以中英为主，且作者明确提到用数据质量治理幻觉 ⇒ <b>动作</b>：数据线把「幻觉相关清洗」列为单独实验组。<br>**风险**：① 157 人署名，细节问题难以定位到具体作者；② 42.5% 是与「同规模稠密模型」比，不是与上一代 DeepSeek 比；③ 2B 规模下 MoE 稀疏度收益远小于 236B，结论不能直接下移。 |

首次收录: 2026-11-16（第四十一轮）｜ 状态: 元数据 + 被引已核（arXiv `id_list` `200` + atom：157 作者、`published=2024-05-07T15:56:43Z`、`comment` 空；OpenAlex `200` 1,552；PDF `200` 1,586,880 B / 52 页，`pdftotext` 核对 `236B` / `21B` / `93.3%` / `42.5%` / `5.76` / `8.1T`）

---

## 162. GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding

| 字段 | 内容 |
|:--|:--|
| 标题 | GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding |
| 作者（前 3） | Dmitry Lepikhin · HyoukJoong Lee · Yuanzhong Xu（共 **9** 位；arXiv abs 页逐字核） |
| 年份 | **2020**（`2020-06-30`；仅 v1） |
| 会议 / 期刊 | **技术报告 / arXiv 预印本**（arXiv `comment` 空；OpenAlex `type=preprint`） |
| 被引数 | **1,633**（OpenAlex `10.48550/arxiv.2006.16668`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2006.16668> ｜ DOI `10.48550/arxiv.2006.16668` |
| 一句话贡献 | 把 Transformer 的**每隔一层 FFN 换成 top-2 门控的稀疏 MoE 层**，配一套「用户只标注关键张量、编译器自动切分」的分片标注（SPMD）系统，使多语言翻译模型在 **2,048 块 TPU v3 上 4 天**训到 **600B 参数**（37.5B → 600B 共 16×，算力 6 → 22 TPU v3 core-year 仅 3.6×）。 |
| 与我们工作的关系 | **pretrain（MoE 扩展的成本曲线，主目标）**：这是「容量涨 16 倍、算力只涨 3.6 倍」最干净的公开证据 ⇒ <b>动作</b>：2B 级 MoE 试点把「总参 / 激活参 / core-year」三列并排记账，判据 = 同算力下 loss 是否低于 dense 基线。<br>**data（多语言配比）**：100 语种 → 英语的收益随专家数增长 ⇒ <b>动作</b>：数据线按语种簇分桶统计，专家路由熵作为配比失衡的探针。<br>**风险**：① 2020 年的 TPU v3 与今天的硬件不可比；② 翻译任务收益不能直接外推到代码 / EDA；③ 论文未给显存与通信开销的绝对值；④ 1,633 引用多为 MoE 背景引用，不等于方法被独立复现。 |

首次收录: 2026-11-16（第四十二轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 43,816 B：9 作者、`Submitted on 30 Jun 2020`、`comment` 空；OpenAlex `200` 1,633；PDF `200` 1,747,868 B / 35 页，`pdftotext` 核对 `600 billion` / `2048 TPU v3` / `37.5B to 600B` / `6 to 22 years` / `top-2 gating`）

---

## 163. Mixtral of Experts

| 字段 | 内容 |
|:--|:--|
| 标题 | Mixtral of Experts |
| 作者（前 3） | Albert Q. Jiang · Alexandre Sablayrolles · Antoine Roux（共 **26** 位；arXiv abs 页逐字核） |
| 年份 | **2024**（`2024-01-08`；仅 v1） |
| 会议 / 期刊 | **技术报告 / arXiv 预印本**（`comment` = "See more details at this https URL"；OpenAlex `type=preprint`） |
| 被引数 | **4,372**（OpenAlex `10.48550/arxiv.2401.04088`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2401.04088> ｜ DOI `10.48550/arxiv.2401.04088` |
| 一句话贡献 | 每层 **8 个专家、每个 token 由 router 选 top-2**，总参 **47B** 但推理只用 **13B 激活参数**，并以 **32k 上下文**预训练；它把「总参 ≠ 单 token 计算量」这层成本结构写成可直接抄的对照表（Mixtral 8x7B vs Llama 2 7B/13B/70B）。 |
| 与我们工作的关系 | **pretrain（MoE 的最小可用配方，主目标）**：8 专家 / top-2 / 32k 是 2B 级复现最省算力的起点 ⇒ <b>动作</b>：预训练配置表增加「总参 / 激活参 / 每 token FLOPs」三行，禁止只报总参。<br>**zhulong（成本口径）**：论文反复强调「13B 激活」与「47B 显存占用」是两回事 ⇒ <b>动作</b>：成本表把「显存」与「单 token 算力」分栏，避免把 MoE 说成「13B 的成本」。<br>**data（多语言）**：Mixtral 明确用多语言语料 ⇒ <b>动作</b>：数据线给出语种配比表，并标注 router 负载均衡的辅助损失系数。<br>**harness**：32k 上下文的长文召回是自评，无第三方复现 ⇒ <b>动作</b>：评测时自带长文检索子集，不引用其自报数字当基线。<br>**风险**：① 未公布训练 token 数与训练成本；② 47B 总参的显存占用对小团队仍是硬门槛；③ 13B 激活是「每 token 平均」，负载不均时实际算力高于此值。 |

首次收录: 2026-11-16（第四十二轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 46,189 B：26 作者、`Submitted on 8 Jan 2024`；OpenAlex `200` 4,372；PDF `200` 2,475,990 B / 13 页，`pdftotext` 核对 `47B` / `13B active` / `8 distinct groups` / `two experts` / `32k tokens`）

---

## 164. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

| 字段 | 内容 |
|:--|:--|
| 标题 | Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection |
| 作者（前 3） | Akari Asai · Zeqiu Wu · Yizhong Wang（共 **5** 位；arXiv abs 页逐字核） |
| 年份 | **2023**（`2023-10-17`；仅 v1） |
| 会议 / 期刊 | **预印本**（arXiv `comment` = `30 pages, 2 figures, 12 tables`，**未标会场**；OpenAlex `type=preprint`）⚠️ 常被引作 ICLR 2024，本轮**未取得一手会场页** ⇒ 不写会场 |
| 被引数 | **1,091**（OpenAlex `10.48550/arxiv.2310.11511`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2310.11511> ｜ DOI `10.48550/arxiv.2310.11511` |
| 一句话贡献 | 让模型在生成时分段插入**反思 token**（检索类 `Retrieve`/`Continue` + 评判类 `ISREL`/`ISSUP`/`ISUSE`），把「何时检索、检索到的是否相关、生成是否被支持、是否有用」变成可训练、可在推理期调节的显式信号；推理端用**段级 beam search**，以反思 token 概率的**加权线性和**作段打分，7B/13B 即可超过 ChatGPT 与 retrieval-augmented Llama2-chat。 |
| 与我们工作的关系 | **harness（可插拔的自评判分，主目标）**：反思 token 是一种「模型自带裁判」的接口 ⇒ <b>动作</b>：agent 评测框架把「是否检索 / 是否被证据支持」做成两列独立指标，而不是塞进一个总分。<br>**data（用强模型造标签）**：训练反思 token 的监督来自 GPT-4 生成的反思数据 ⇒ <b>动作</b>：数据线评估「用教师模型造过程标签」的许可与成本，先做小规模可行性，不默认可商用。<br>**zhulong（推理期可调成本旋钮）**：`Retrieve=Yes` 概率阈值直接控制检索次数 ⇒ <b>动作</b>：把「检索率」列为与准确率并列的实验轴，画准确率-检索次数曲线。<br>**风险**：① 监督依赖专有模型（GPT-4），复现受许可限制；② 段级 beam search 使推理成本随 beam 宽度上升；③ 1,091 引用中相当部分是「RAG 综述式引用」，不等于被独立复现。 |

首次收录: 2026-11-16（第四十二轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 42,906 B：5 作者、`Submitted on 17 Oct 2023`、`comment` = 30 pages；OpenAlex `200` 1,091；PDF `200` 1,405,127 B / 30 页，`pdftotext` 核对 `reflection tokens` / `ISREL` / `ISSUP` / `ISUSE` / `segment-level beam search` / `weighted linear sum` / `threshold`）

---

## 165. LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding

| 字段 | 内容 |
|:--|:--|
| 标题 | LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding |
| 作者（前 3） | Yushi Bai · Xin Lv · Jiajie Zhang（共 **13** 位；arXiv abs 页逐字核；机构含清华大学 / 智谱 AI / 中科院自动化所） |
| 年份 | **2023**（v1 `2023-08-28`；v2 `2024-06-19`） |
| 会议 / 期刊 | **ACL 2024**（arXiv `comment` = `ACL 2024`；OpenAlex `type=conference-paper`，venue = ACL） |
| 被引数 | **1,169**（OpenAlex `10.48550/arxiv.2308.14508`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2308.14508> ｜ DOI `10.48550/arxiv.2308.14508` |
| 一句话贡献 | 把长上下文理解拆成 **21 个数据集 / 6 类任务**（单文档 QA、多文档 QA、摘要、少样本学习、合成任务、代码补全）的中英双语基准，共 **4,750 条测试样本**，英文平均 **6,711 词**、中文平均 **13,386 字**；并明确写出「超长输入从中间截断」的评测口径，使不同上下文窗口的模型可在同一张表上比较。 |
| 与我们工作的关系 | **harness（长上下文评测口径，主目标）**：中间截断会改变同一样本在不同模型上实际看到的内容 ⇒ <b>动作</b>：我们的长上下文评测表必须写明「截断策略」，并加一列「有效输入长度」。<br>**zhulong（长度-成本权衡）**：论文发现商业模型仍随长度下降，且缩放位置编码 / 长序列微调能显著改善 ⇒ <b>动作</b>：把「上下文长度」当作消融轴，固定任务集、只改长度，报分数-延迟双曲线。<br>**data（中文长文来源）**：中文子集来自百度搜索等来源，平均长度高于英文 ⇒ <b>动作</b>：数据线建立中文长文（规格书 / 手册）子集时，先做长度分布统计再定配额。<br>**风险**：① 自动指标（F1 / ROUGE-L / Edit Sim）与人工判断有偏差，长文摘要尤甚；② 4,750 条样本量小，单任务 150–200 条，置信区间宽；③ 论文评测的模型已过时，分数不可当今天的基线。 |

首次收录: 2026-11-16（第四十二轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 45,172 B：13 作者、`Submitted on 28 Aug 2023 (v1), last revised 19 Jun 2024`、`comment` = ACL 2024；OpenAlex `200` 1,169、`conference-paper`；PDF `200` 11,630,690 B / 19 页，`pdftotext` 核对 `4,750 test instances` / `21 datasets` / `6,711 words` / `13,386 characters` / `truncate the input sequence`）

---

## 166. Cambrian-1: A Fully Open, Vision-Centric Exploration of Multimodal LLMs

| 字段 | 内容 |
|:--|:--|
| 标题 | Cambrian-1: A Fully Open, Vision-Centric Exploration of Multimodal LLMs |
| 作者（前 3） | Shengbang Tong · Ellis Brown · Penghao Wu（共 **14** 位，末位 Saining Xie；arXiv abs 页逐字核；机构 New York University） |
| 年份 | **2024**（v1 `2024-06-24`；v2 `2024-12-04`） |
| 会议 / 期刊 | **NeurIPS 2024（Oral）**（arXiv `comment` = `NeurIPS 2024 (Oral). Website at this https URL`；OpenAlex `conference-paper`，venue = NeurIPS） |
| 被引数 | **514**（OpenAlex `10.48550/arxiv.2406.16860`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2406.16860> ｜ DOI `10.48550/arxiv.2406.16860` |
| 一句话贡献 | 用 **20 多个视觉编码器**做「只改视觉塔、其余尽量固定」的横向对照（CLIP / SigLIP / DINOv2 / MAE / I-JEPA / SAM / MoCo v3 等），提出 **SVA（Spatial Vision Aggregator）**：以可学习 latent token 做多层、空间感知的跨注意力聚合，把单个编码器的 **576 个视觉 token 压到 36 个**仍保留定位能力；并开源 **Cambrian-7M** 指令数据配比（OCR 占 27.6%）与视觉中心基准 **CV-Bench**。 |
| 与我们工作的关系 | **vision（视觉塔选型与 token 预算，主目标）**：这是目前唯一把「换编码器」与「冻结 / 解冻」拆开做完整对照的公开实验 ⇒ <b>动作</b>：视觉消融表按「编码器族 × 冻结策略」二维排布，判据 = 固定视觉 token 预算下的 OCR 与定位分数。<br>**vision（连接器）**：SVA 的「576 → 36」给出 token 压缩的可测区间 ⇒ <b>动作</b>：把连接器实验做成 576/144/36 三档，记录压缩率与定位指标的折点。<br>**data（指令数据配比）**：Cambrian-7M 的 OCR 27.6%、Filtered DVQA 1550K 等是可照抄的量级 ⇒ <b>动作</b>：数据线做同构配比表，先小规模验证再放大。<br>**harness**：CV-Bench 是自建的视觉中心基准 ⇒ <b>动作</b>：评测时同时报通用基准与视觉中心基准，避免只报综合分掩盖定位退化。<br>**风险**：① 514 引用（2026-11-16）刚过 500 线，方法尚未经过多年独立复现；② 7M 数据与训练成本对我们偏大；③ SVA 的 576 → 36 结论在更高分辨率 / 更小模型上未必成立。 |

首次收录: 2026-11-16（第四十二轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 45,385 B：14 作者、`Submitted on 24 Jun 2024 (v1), last revised 4 Dec 2024`、`comment` = NeurIPS 2024 Oral；OpenAlex `200` 514、`conference-paper`；PDF `200` 6,427,380 B / 51 页，`pdftotext` 核对 `Spatial Vision Aggregator` / `576` / `36 tokens` / `CV-Bench` / `OCR (27.6%)`）

---

## 167. Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context

| 字段 | 内容 |
|:--|:--|
| 标题 | Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context |
| 作者（前 3） | Gemini Team · Petko Georgiev · Ving Ian Lei（团队报告；arXiv abs 页 `citation_author` 共 **1,137** 条；通讯地址 `gemini-1_5-report@google.com` 写在正文脚注 1） |
| 年份 | **2024**（v1 `2024-03-08`；v5 `2024-12-16`） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `primary_location.source` = arXiv，无会场 DOI） |
| 被引数 | **4,633**（OpenAlex `10.48550/arxiv.2403.05530`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/2403.05530> ｜ DOI `10.48550/arxiv.2403.05530` |
| 一句话贡献 | 用 **MoE + 长上下文**把窗口推到 **至少 10M tokens**（文本约 7M 词、音频 9.7M tokens），并给出可复核的长上下文证据：needle recall 在 **530K tokens 内 100%**、**1M 内 >99.7%**；文本 NLL 在 **1M（文档）/ 约 2M（代码）** 内仍近似幂律，到 **10M** 出现偏离；同时报告长文档 QA / 长视频 / 长代码库三类下游任务的随长度变化。 |
| 与我们工作的关系 | **pretrain（长上下文配方，主目标）**：幂律在 1M/2M 后偏离 = 位置外推、注意力容量、语料构成三者纠缠 ⇒ <b>动作</b>：我们的 32K→128K 扩展实验必须同时记「固定位置 NLL」与「语料长度分布」，否则无法判断偏离来自模型还是数据。<br>**harness（长上下文评测口径）**：needle 在 1M 已接近饱和（>99.7%）⇒ <b>动作</b>：不能只用 needle 作为长上下文判据，需加「多针 + 位置分层 + 证据落地」三项，并报告深度/长度网格。<br>**zhulong（长度-成本）**：论文把「有效长度」与「名义窗口」分开讨论 ⇒ <b>动作</b>：成本表加「有效输入长度」列，按 128K/512K/1M 分档报准确率与延迟。<br>**data**：10M token 级样本需要跨文档拼接与去重 ⇒ <b>动作</b>：数据线先做「拼接后跨文档污染」检查。<br>**风险**：① 团队报告，训练细节（数据配比、位置编码方案）披露有限；② 4,633 引用中含大量二手引用；③ 10M 级评测成本对我们不可直接复制。 |

首次收录: 2026-11-16（第四十三轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 233,352 B：`citation_author` 1,137 条、`Submitted on 8 Mar 2024 (v1), last revised 16 Dec 2024 (v5)`；OpenAlex `200` 4,633、venue = arXiv；PDF `200` 7,184,542 B，`pdftotext` 核对 `at least 10M tokens` / `>99.7%` / `1M tokens` / `10M tokens` / `7M words` / `9.7M tokens` / `power-law`）

---

## 168. RTLLM: An Open-Source Benchmark for Design RTL Generation with Large Language Model

| 字段 | 内容 |
|:--|:--|
| 标题 | RTLLM: An Open-Source Benchmark for Design RTL Generation with Large Language Model |
| 作者（前 3） | Yao Lu · Shang Liu · Qijun Zhang（共 **4** 位，末位 / 通讯 Zhiyao Xie；arXiv abs 页逐字核；机构 HKUST） |
| 年份 | **2023**（v1 `2023-08-10`；v3 `2023-11-11`） |
| 会议 / 期刊 | **ASP-DAC 2024**（OpenAlex `primary_location.source` = ASP-DAC，DOI `10.1109/asp-dac58780.2024.10473904`） |
| 被引数 | **301**（OpenAlex `10.48550/arxiv.2308.05345`，查询日 **2026-11-16**；⚠️ <500，按「本领域权威」收） |
| arXiv / DOI | <https://arxiv.org/abs/2308.05345> ｜ DOI `10.48550/arxiv.2308.05345` |
| 一句话贡献 | 提出 **30 个设计**（11 个算术 + 19 个逻辑，HDL 行数中位 86 / 最大 2.5K，综合后 cell 数中位 408 / 最大 11.8K）的 RTL 生成基准，并把评测拆成**三层递进目标**：syntax（能综合）→ functionality（过 testbench）→ design quality（与人工参考设计比 PPA）；同时给出 **self-planning**（先让模型写实现计划再写 RTL）提示法，把 GPT-3.5 的功能通过从 **10/30 提到 14/30**、语法通过从 55% 提到 73%。 |
| 与我们工作的关系 | **designflow（造题与判分，主目标）**：三层目标可直接映射到 L1–L5 保真度 ⇒ <b>动作</b>：造题卡片固定写「syntax / function / quality」三列判据，并附参考设计。<br>**designflow（PPA 判据）**：论文用后综合 netlist 的 area / power / timing 与人工参考比，且出现「生成设计面积小于参考」的情况 ⇒ <b>动作</b>：我们的质量判据不能只比数值，必须同时报 testbench 覆盖（边界向量）与工艺库，否则「更小」可能是漏功能。<br>**harness（分层报告）**：三层目标允许部分得分 ⇒ <b>动作</b>：agent 评测表按三层分别给分，不合并成单一总分。<br>**data**：30 个设计规格 + 参考 RTL 可作种子 ⇒ <b>动作</b>：先做小规模 SFT 试验并核许可。<br>**风险**：① 301 引用，属「领域内公认基准」而非高引经典；② 30 题规模小、PPA 数字绑定特定工艺库（Design Compiler）；③ self-planning 的增益在乘法器上并不稳定。 |

首次收录: 2026-11-16（第四十三轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 41,896 B：4 作者、`Submitted on 10 Aug 2023 (v1), last revised 11 Nov 2023 (v3)`；OpenAlex `200` 301、`conference-paper` ASP-DAC；PDF `200` 374,181 B，`pdftotext` 核对 `30 designs` / `syntax goal` / `functionality goal` / `design quality goal` / `55% correct syntax` / `10/30` / `14/30` / `239` / `19K` / `640` / `52` / `Design Compiler`）

---

## 169. VerilogEval: Evaluating Large Language Models for Verilog Code Generation

| 字段 | 内容 |
|:--|:--|
| 标题 | VerilogEval: Evaluating Large Language Models for Verilog Code Generation（ICCAD 版标题带 `Invited Paper:` 前缀） |
| 作者（前 3） | Mingjie Liu · Nathaniel Pinckney · Brucek Khailany（共 **4** 位，末位 Haoxing Ren；arXiv abs 页逐字核；机构 NVIDIA） |
| 年份 | **2023**（v1 `2023-09-14`；v2 `2023-12-10`） |
| 会议 / 期刊 | **ICCAD 2023（Invited Paper）**（arXiv `comment` 原文；DOI `10.1109/iccad57390.2023.10323812`；⚠️ OpenAlex 该条 `primary_location.source` 为空，会场取自 arXiv `comment` 与 DOI） |
| 被引数 | **359**（OpenAlex `10.48550/arxiv.2309.07544`，查询日 **2026-11-16**；⚠️ <500，按「本领域权威」收） |
| arXiv / DOI | <https://arxiv.org/abs/2309.07544> ｜ DOI `10.48550/arxiv.2309.07544` |
| 一句话贡献 | 从 HDLBits 整理 **156 道** Verilog 题（含人工改写的自然语言描述，解决原题描述歧义），用**仿真器自动判功能正确**，以 `pass@k`（k=1/5/10，nucleus sampling `top_p=0.95`）报告；并证明「用 LLM 生成题目描述 + 解答」做监督微调，可让较小模型在 pass@1 上持续提升，而 pass@5/10 在训练后期反而退化。 |
| 与我们工作的关系 | **designflow（判分可验证性，主目标）**：156 题 + 仿真判分 = 可复现的「过仿真」层 ⇒ <b>动作</b>：designflow 的 RTL 题统一采用「题目描述 + testbench + 参考解」三件套，判分先跑仿真再谈质量。<br>**harness（pass@k 口径）**：k=1/5/10 与采样温度必须一起报 ⇒ <b>动作</b>：agent 评测表加「采样预算 n / 温度 / top_p」三列，否则跨模型不可比。<br>**data（合成题面）**：用 LLM 改写题面解决歧义 ⇒ <b>动作</b>：数据线做「题面改写 + 人工抽检」流程，抽检不过关不进正式集。<br>**风险**：① 359 引用，且 156 题规模有限；② 判分只到「功能正确」，不覆盖时序/面积（与 RTLLM 互补）；③ 论文自述早期版本 gpt-4 数字有误（v2 已更正）⇒ 引用必须用 v2 及以后。 |

首次收录: 2026-11-16（第四十三轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 41,893 B：4 作者、`Submitted on 14 Sep 2023 (v1), last revised 10 Dec 2023 (v2)`、`comment` 原文含 ICCAD 2023 Invited；OpenAlex `200` 359；PDF `200` 671,101 B，`pdftotext` 核对 `156 problems` / `HDLBits` / `pass@k` / `top p = 0.95` / `functional correctness`）

---

## 170. Benchmarking a New Paradigm: An Experimental Analysis of a Real Processing-in-Memory Architecture

| 字段 | 内容 |
|:--|:--|
| 标题 | Benchmarking a New Paradigm: An Experimental Analysis of a Real Processing-in-Memory Architecture（IEEE Access 版标题为 `Benchmarking a New Paradigm: Experimental Analysis and Characterization of a Real Processing-in-Memory System`） |
| 作者（前 3） | Juan Gómez-Luna · Izzat El Hajj · Ivan Fernandez（共 **6** 位，末位 Onur Mutlu；arXiv abs 页逐字核；机构 ETH Zurich / American University of Beirut 等） |
| 年份 | **2021**（v1 `2021-05-09`；v7 `2022-05-04`） |
| 会议 / 期刊 | **IEEE Access 2022**（OpenAlex DOI `10.1109/access.2022.3174101`；arXiv 侧为预印本） |
| 被引数 | **285**（OpenAlex `10.48550/arxiv.2105.03814`，查询日 **2026-11-16**；⚠️ <500，按「本领域权威」收：首个真实商用 PIM 系统的系统级实测） |
| arXiv / DOI | <https://arxiv.org/abs/2105.03814> ｜ DOI `10.48550/arxiv.2105.03814` |
| 一句话贡献 | 对**首个公开可用的真实 PIM 架构 UPMEM**（DRAM bank 内嵌可编程处理单元）做系统级实测：用微基准刻画 **bank 内/跨 bank、CPU↔PIM 数据传输、归约原语** 的带宽-延迟特性，再用 **PrIM 基准套件（16 个记忆密集型 workload）**给出「哪些负载适合 PIM」的可操作判据，并总结编程建议与对未来 PIM 架构设计的启示。 |
| 与我们工作的关系 | **zhulong（近存 / 存储侧成本模型）**：真实 PIM 的瓶颈是 CPU↔PIM 传输与 bank 级并行，不是理论带宽 ⇒ <b>动作</b>：成本模型必须把「数据搬运次数」单列，禁止只用峰值带宽估算收益。<br>**designflow（硬件约束的可测性）**：微基准给出可复现实验模板 ⇒ <b>动作</b>：涉及存储侧的设计题，判据里写明「搬运量 / bank 冲突 / 归约次数」三项可测字段。<br>**data**：PrIM 的 16 个 workload 分类可作为「记忆密集型」样本定义 ⇒ <b>动作</b>：数据线建 workload 画像时按访存模式分层。<br>**风险**：① 285 引用，且 UPMEM 为特定商用架构，结论不可无条件外推到 HBM-PIM；② 2021–2022 的硬件与编译器已迭代；③ 论文主体是实测报告，不含新算法。 |

首次收录: 2026-11-16（第四十三轮）｜ 状态: 元数据 + 被引已核（arXiv abs 页 `200` / 45,640 B：6 作者、`Submitted on 9 May 2021 (v1), last revised 4 May 2022 (v7)`；OpenAlex `200` 285、`article` IEEE Access、标题为期刊版措辞；PDF `200` 6,091,843 B，`pdftotext` 核对 `UPMEM` / `processing-in-memory` / `PrIM` / `16 work-` / `640`）

---

## 171. Swin Transformer: Hierarchical Vision Transformer using Shifted Windows

| 字段 | 内容 |
|:--|:--|
| 标题 | Swin Transformer: Hierarchical Vision Transformer using Shifted Windows |
| 作者（前 3） | Ze Liu · Yutong Lin · Yue Cao（共 **8** 位，末位 Baining Guo；arXiv abs 页逐字核；机构 USTC / MSRA） |
| 年份 | **2021**（v1 `2021-03-25`；v2 `2021-08-17`） |
| 会议 / 期刊 | **ICCV 2021**（OpenAlex `conference-paper`，`primary_location.source` = IEEE/CVF International Conference on Computer Vision；arXiv abs 页未写 `comment`） |
| 被引数 | **38,712**（OpenAlex `10.48550/arxiv.2103.14030`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2103.14030> ｜ DOI `10.48550/arxiv.2103.14030` |
| 一句话贡献 | 把 ViT 改成**层级式** backbone：从 4×4 patch 起步、逐级 patch merging 得到多尺度特征图，并用 **shifted window**（窗口内注意力 + 相邻层窗口错位）把注意力复杂度从全图的二次降为**对图像尺寸线性**；给出 Tiny/Small/Base/Large 四档，ImageNet-1K **87.3 top-1**（Swin-L @384²）、COCO test-dev **58.7 box AP / 51.1 mask AP**、ADE20K **+3.2 mIoU**（论文自报，未复现）。 |
| 与我们工作的关系 | **vision（视觉编码器结构选型，主目标）**：Swin 的「窗口大小 × merging 次数」直接决定**同一分辨率下的视觉 token 数**，而这正是 2B 模型里图文预算的关键变量 ⇒ <b>动作</b>：视觉塔对照表新增 `window_size` / `patch_merging_stages` / `tokens@224/448` 三列，任何分辨率对比必须三列齐全。<br>**vision（分辨率-吞吐折中）**：线性复杂度是相对全图 attention 的论断，不等于在低算力卡上一定更快（window 重排有实现开销）⇒ <b>动作</b>：预注册判据 = 若 448² 下 tokens 翻 4 倍而吞吐下降 &gt;30%，则退回「全局 attention + 早期下采样」，不先调窗口。<br>**harness（检测/分割口径）**：58.7 box AP / 51.1 mask AP 绑定 HTC++ 与特定训练 schedule ⇒ <b>动作</b>：引用时把 backbone 与 head / schedule 一起写，禁止只写 AP 数字。<br>**designflow（层级特征的可复用性）**：多尺度特征图与版图/图像类视觉任务同构 ⇒ <b>动作</b>：视觉前端若接图形类输入，先按「单尺度 vs 层级」做小对照。<br>**风险**：① 38,712 是 OpenAlex 口径，🚫 与 Google Scholar / S2 混算；② 监督 ImageNet 配方 ≠ CLIP 式图文预训练，不能把分类结论直接搬到多模态；③ shifted window 的内存/重排开销随实现而变。 |
| 首次收录 | **2026-11-16**（第四十四轮） |
| 核验状态 | arXiv abs 页 `200` / 44,906 B（8 作者、`Submitted on 25 Mar 2021 (v1), last revised 17 Aug 2021 (v2)`）；OpenAlex `200` 38,712、`conference-paper` ICCV；PDF `200` / 1,360,315 B，`pdftotext` 核对 `87.3 top-1` / `58.7 box AP and 51.1 mask AP` / `shifted windows` / `linear computational complexity` / `Swin-B 83.5` / `86.4` |

---

## 172. SpeechT5: Unified-Modal Encoder-Decoder Pre-Training for Spoken Language Processing

| 字段 | 内容 |
|:--|:--|
| 标题 | SpeechT5: Unified-Modal Encoder-Decoder Pre-Training for Spoken Language Processing |
| 作者（前 3） | Junyi Ao · Rui Wang · Long Zhou（共 **14** 位，末位 Furu Wei；arXiv abs 页逐字核；机构 Microsoft Research Asia 等） |
| 年份 | **2021**（v1 `2021-10-14`；v3 `2022-05-24`） |
| 会议 / 期刊 | **ACL 2022 main conference**（arXiv `comment` 原文 `Accepted by ACL 2022 main conference`；⚠️ OpenAlex 该条 `type=preprint`、无会场 DOI ⇒ 只按 arXiv `comment` 记会议） |
| 被引数 | **141**（OpenAlex `10.48550/arxiv.2110.07205`，查询日 **2026-11-16**；⚠️ **&lt;500**，按「开创统一模态范式」收：首个把 speech / text 共用一套 encoder-decoder 的预训练框架） |
| arXiv / DOI | <https://arxiv.org/abs/2110.07205> ｜ DOI `10.48550/arxiv.2110.07205` |
| 一句话贡献 | 用一个**共享 encoder-decoder** + **6 个模态特定 pre/post-net**（speech/text 各 3 个）做统一模态预训练：输入先经 pre-net 映射到共享隐空间，decoder 输出再经 post-net 还原成语音或文本；在 **960 小时 LibriSpeech + 400M 句文本**上预训练后，同一套权重覆盖 ASR / TTS / speech translation / voice conversion / speech enhancement，论文自报 ASR 在 960h 微调下优于 wav2vec 2.0 / HuBERT base。 |
| 与我们工作的关系 | **vision（模态接口层的结构范式，主目标）**：SpeechT5 把「共享主干 + 模态专用前后处理」写成了可配置结构 ⇒ <b>动作</b>：我们的多模态编码器配置表显式区分 `shared_backbone` 与 `modality_pre_post_net`，禁止把模态差异硬编码进主干。<br>**pretrain（统一目标与配比）**：语音侧用「重建 + CTC」等多目标联合 ⇒ <b>动作</b>：预训练目标表按「模态 × 目标」二维排，记录每个目标的权重与对应数据量。<br>**data（有标注/无标注混合）**：960h 标注语音 + 400M 句无标注文本的比例是可照抄的量级 ⇒ <b>动作</b>：数据线建「标注:无标注」比例列，先小规模验证再放大。<br>**harness（跨任务同一权重）**：一个模型多任务 ⇒ <b>动作</b>：评测表按任务分列，禁止只报平均分掩盖某一任务退化。<br>**风险**：① 141 引用，远低于 500，属「范式开创 + 领域常用」而非高引经典；② 语音与图文在 token 率、序列长度上差异大，结论不可直接搬到 vision；③ 「outperforms」是作者自报，未复现。 |
| 首次收录 | **2026-11-16**（第四十四轮） |
| 核验状态 | arXiv abs 页 `200` / 43,773 B（14 作者、`Submitted on 14 Oct 2021 (v1), last revised 24 May 2022 (v3)`、`comment` = ACL 2022 main）；OpenAlex `200` 141、`preprint`；PDF `200` / 1,710,946 B，`pdftotext` 核对 `960` / `100/960 hours` / `outperforms wav2vec 2.0` / `HuBERT` / `shared encoder-decoder`；⚠️ **先验 ID 更正**：候选池旧记 `2010.00718`，本轮实测该 ID = `When to Impute? Imputation before and during cross-validation`（Jaeger et al.），**不是 SpeechT5**；真 ID = `2110.07205`（按标题检索 + abs 页逐字核后才收录） |

---

## 173. GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism

| 字段 | 内容 |
|:--|:--|
| 标题 | GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism |
| 作者（前 3） | Yanping Huang · Youlong Cheng · Ankur Bapna（共 **11** 位，末位 Zhifeng Chen；arXiv abs 页逐字核；机构 Google Brain） |
| 年份 | **2018**（v1 `2018-11-16`；v5 `2019-07-25`） |
| 会议 / 期刊 | **NeurIPS 2019**（ACM DL `10.5555/3454287.3454297`、NeurIPS proceedings 2019 有正式论文页；⚠️ OpenAlex 该 arXiv DOI 记录为 `preprint`、arXiv `comment` 仍写 `Work in progress` ⇒ 会议与预印本两口径如实并列） |
| 被引数 | **1,280**（OpenAlex `10.48550/arxiv.1811.06965`，查询日 **2026-11-16**） |
| arXiv / DOI | <https://arxiv.org/abs/1811.06965> ｜ DOI `10.48550/arxiv.1811.06965`；会议记录 `10.5555/3454287.3454297` |
| 一句话贡献 | 把网络按层切成连续 **stage** 放到不同加速器，并把 mini-batch 切成 **micro-batch** 流水执行以填满流水线气泡；配合**重算（recomputation）**把激活显存压到可训规模：AmoebaNet 从单卡 82M 扩到 8 卡 **1.8B（25×）**、ImageNet-2012 **84.4% top-1**；同参数量 Transformer 上报告 **3.5× 加速**，并给出「气泡可忽略」的经验条件 **M ≥ 4×K**（micro-batch 数 ≥ 4 倍 stage 数）。 |
| 与我们工作的关系 | **pretrain（并行策略选择，主目标）**：BaiZe ~2B 的瓶颈可能是**激活显存**而非参数/优化器状态 ⇒ <b>动作</b>：训练配置表新增 `pp_stages` / `micro_batches` / `recompute` 三列，与 ZeRO（#94）的 `zero_stage` 同表记录，任何吞吐对比必须同时给出并行组合。<br>**pretrain（判据）**：论文给的经验条件是 `M ≥ 4K` ⇒ <b>动作</b>：预注册判据 = 若实测 bubble 占比 &gt;15%，先加 micro-batch（受显存限制时再减 stage），不先加 stage；若开启 recompute 后 step time 上升 &gt;20%，则把 recompute 只用于最深的若干 stage。<br>**zhulong（长序列 RL 的显存-吞吐折中）**：长轨迹训练显存压力大 ⇒ <b>动作</b>：长序列实验先报「不开 recompute 能否放下」，再决定是否用时间换显存。<br>**data（吞吐预算）**：流水线会改变每步可消费的样本数 ⇒ <b>动作</b>：dataloader 的 tokens/s 与 step time 同表记录。<br>**风险**：① 1,280 是 arXiv DOI 口径，会议版可能另计；② 84.4% / 3.5× 是 2018–2019 的 TPUv2 + AmoebaNet/Transformer 口径，🚫 不可外推到今天的卡型与互联；③ bubble 与 stage 数的关系依赖 micro-batch 上限，2B 规模的最优点会移动。 |
| 首次收录 | **2026-11-16**（第四十四轮） |
| 核验状态 | arXiv abs 页 `200` / 45,691 B（11 作者、`Submitted on 16 Nov 2018 (v1), last revised 25 Jul 2019 (v5)`、`comment` = `11 pages. Work in progress.`）；OpenAlex `200` 1,280、`preprint`；PDF `200` / 539,195 B，`pdftotext` 核对 `1.8 billion` / `25x` / `84.4%` / `3.5× speedup` / `2.7× speedup` / `M ≥ 4 × K` / `recomputation` |

---

## 174. Scaling Data-Constrained Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Scaling Data-Constrained Language Models |
| 作者（前 3） | Niklas Muennighoff · Alexander M. Rush · Boaz Barak（共 **9** 位，末位 Colin Raffel；arXiv abs 页逐字核；机构 Hugging Face / Cornell / Harvard 等） |
| 年份 | **2023**（v1 `2023-05-25`；v5 `2025-06-28`） |
| 会议 / 期刊 | **NeurIPS 2023**（OpenAlex `conference-paper`，`primary_location.source` = NeurIPS；PDF 正文写 `37th Conference on Neural Information Processing Systems (NeurIPS 2023)`） |
| 被引数 | **254**（OpenAlex `10.48550/arxiv.2305.16264`，查询日 **2026-11-16**；⚠️ **&lt;500**，按「方法论常青」收：数据受限/重复训练的 scaling law 原始工作） |
| arXiv / DOI | <https://arxiv.org/abs/2305.16264> ｜ DOI `10.48550/arxiv.2305.16264` |
| 一句话贡献 | 训练 **&gt;400 个模型**（10M–9B 参数，最多 **1500 epochs**）系统测「重复数据」对 scaling 的影响：**最多 4 个 epoch 的重复几乎与等量新数据等效**，之后收益迅速递减（40 epochs 时重复已近乎无用）；给出把重复折算成**等效唯一 token（effective data）**的修正公式，并建议数据受限时在固定算力下**训更小的模型、更多 epoch**。 |
| 与我们工作的关系 | **data（配比与重复上限，主目标）**：中文/代码/EDA 语料都可能被迫重复 ⇒ <b>动作</b>：语料账本新增 `unique_tokens` / `epochs` / `effective_data` 三列，任何「我们用了 N tokens」的表述必须换算成 effective data 后再比较。<br>**data（预注册判据）**：论文的 4-epoch 拐点是全局平均口径 ⇒ <b>动作</b>：若某子集重复 &gt;4 epoch，先单独拟合该子集的折旧率（至少 3 个重复档位），折旧率显著差于全局值时才追加新数据。<br>**pretrain（Chinchilla 公式修正）**：固定算力下「小模型 + 多 epoch」可能优于「大模型 + 一遍数据」⇒ <b>动作</b>：2B 规模的算力分配实验把 epoch 数作为第四轴（与参数量/数据量/学习率并列）。<br>**zhulong（成本对照）**：重复数据的边际收益递减 ⇒ <b>动作</b>：成本表把「重复 epoch 的训练成本」与「新增数据采集成本」并列，禁止默认加数据更贵。<br>**风险**：① 254 引用，未到 500；② 实验上界 9B 参数，外推到 2B 需重新拟合并验证；③ 论文以英文语料为主，中文/代码/EDA 的折旧率未分域测量 ⇒ 🚫 不得直接套用 4-epoch。 |
| 首次收录 | **2026-11-16**（第四十四轮） |
| 核验状态 | arXiv abs 页 `200` / 42,834 B（9 作者、`Submitted on 25 May 2023 (v1), last revised 28 Jun 2025 (v5)`）；OpenAlex `200` 254、`conference-paper` NeurIPS；PDF `200` / 2,160,774 B，`pdftotext` 核对 `Up to 4 epochs` / `At 40 epochs` / `400 models` / `1500 epochs` / `10 million to 9 billion` / `effective data` / `NeurIPS 2023` |

---

## 175. Large Batch Optimization for Deep Learning: Training BERT in 76 minutes

| 字段 | 内容 |
|:--|:--|
| 标题 | Large Batch Optimization for Deep Learning: Training BERT in 76 minutes |
| 作者（前 3） | Yang You · Jing Li · Sashank Reddi（共 **10** 位，末位 Cho-Jui Hsieh；arXiv abs 页逐字核；机构 Google Brain / UC Berkeley / NUS） |
| 年份 | **2019**（v1 `2019-04-01`；v5 `2020-01-03`） |
| 会议 / 期刊 | **ICLR 2020**（arXiv `comment` 原文 `Published as a conference paper at ICLR 2020`；⚠️ OpenAlex 该 arXiv DOI 记录为 `preprint` ⇒ 会议只按 arXiv `comment` 记） |
| 被引数 | **932**（OpenAlex `10.48550/arxiv.1904.00962`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1904.00962> ｜ DOI `10.48550/arxiv.1904.00962` |
| 一句话贡献 | 把 LARS 的「逐层信任比」思想移植到 Adam，得到 **LAMB**：每层用 `‖w‖ / ‖更新量‖` 做自适应缩放，使**极大 batch 也能用同一套学习率**；在 **batch size 32768** 的 TPUv3 Pod 上把 BERT 预训练压到 **76 分钟（100.2% 效率）**，并报告该 batch 下微调 F1 达 **91.460**（论文自报，未复现）。 |
| 与我们工作的关系 | **pretrain（大 batch 与学习率缩放，主目标）**：数据并行扩到多机时，Adam 的逐元素二阶矩对 batch 变化敏感 ⇒ <b>动作</b>：优化器对照表把 `batch_size` / `lr` / `warmup` / `layerwise_scaling(yes/no)` 四列绑定记录，禁止「只改 batch 不改 lr」的对照。<br>**pretrain（判据）**：论文的核心是「逐层范数比」而非全局 clip ⇒ <b>动作</b>：预注册判据 = 若 batch 扩大 2× 后前 2k step 的 loss 抖动 &gt;0.02，则先上 LAMB 式逐层缩放，再考虑降 lr；若逐层缩放后仍抖，才判定为数据/精度问题。<br>**zhulong（成本口径）**：76 分钟是 TPUv3 Pod 的特定规模，不等于同 step 数在别的卡上更快 ⇒ <b>动作</b>：成本表把「墙钟时间」与「加速器小时数」并列，🚫 只用其中一列做结论。<br>**风险**：① 932 是 OpenAlex 口径，会议版可能另计；② 32k batch 的结论绑定 BERT-base/Large 与英文语料；③ 论文自报 F1 未复现，🚫 当作我们的基线。 |
| 首次收录 | **2026-11-16**（第四十五轮） |
| 核验状态 | arXiv abs 页 `200` / 47,227 B（10 作者、`Submitted on 1 Apr 2019 (v1), last revised 3 Jan 2020 (this version, v5)`、`comment` = ICLR 2020）；OpenAlex `200` 932、`preprint`；PDF `200` / 977,812 B，`pdftotext` 核对 `76 minutes` / `batch size of 32768` / `TPUv3 Pod` / `91.460` / `100.2% efficiency` |

---

## 176. Layer Normalization

| 字段 | 内容 |
|:--|:--|
| 标题 | Layer Normalization |
| 作者（前 3） | Jimmy Lei Ba · Jamie Ryan Kiros · Geoffrey E. Hinton（共 **3** 位；arXiv abs 页逐字核；机构 University of Toronto） |
| 年份 | **2016**（v1 `2016-07-21`，无 v2） |
| 会议 / 期刊 | **预印本（无 `comment`、OpenAlex 记 `preprint`）** ⇒ 会议未核验，🚫 不写「NeurIPS/ICML」 |
| 被引数 | **12,853**（OpenAlex `10.48550/arxiv.1607.06450`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1607.06450> ｜ DOI `10.48550/arxiv.1607.06450` |
| 一句话贡献 | 把 BatchNorm 的统计量换成**单个样本、单层内全部隐单元**上的均值与方差（`μ, σ` 不再依赖 mini-batch 组成），并给每个神经元独立的**自适应 bias 与 gain**；因此对 batch 大小不敏感、可直接用于 RNN/变长序列，且推理期**不需要保存 running statistics**。 |
| 与我们工作的关系 | **pretrain（数值稳定性与归一化位置，主目标）**：LN 的统计量与 batch 组成无关 ⇒ 小 batch、长序列、变长打包（packing）下行为稳定，这正是长上下文/多模态混合训练常踩的坑 ⇒ <b>动作</b>：模型配置表新增 `norm_type` / `norm_position(pre|post)` / `eps` 三列，任何「训练不稳」的结论必须先排除归一化实现差异。<br>**pretrain（判据）**：LN 不给「什么时候换 RMSNorm / 调 eps」的结论 ⇒ <b>动作</b>：预注册判据 = 同一数据配比下，若前 500 step 的 grad-norm 分位数跨度 &gt;3×，先固定 `eps` 与 `norm_position` 做对照，再谈优化器。<br>**vision（小 batch 与序列打包）**：多模态图文混合时视觉分支常被文本填充 ⇒ <b>动作</b>：视觉塔在 &lt;8/卡的小 batch 配置下必测一遍，禁止默认沿用大 batch 的 BN 结论。<br>**风险**：① 12,853 是 OpenAlex 口径；② 2016 年的 RNN 实验不等于今天的 Transformer 结论（现多用 RMSNorm + pre-norm）；③ 论文未做 1B+ 规模验证 ⇒ 🚫 不能据此断言「LN 比 RMSNorm 更适合 2B」。 |
| 首次收录 | **2026-11-16**（第四十五轮） |
| 核验状态 | arXiv abs 页 `200` / 41,854 B（3 作者、`Submitted on 21 Jul 2016`、**无 `comment`**、主分类 `stat.ML`）；OpenAlex `200` 12,853、`preprint`；PDF `200` / 612,446 B，`pdftotext` 核对 `mean and variance` / `all of the summed inputs to the neurons in a layer on a single training case` / `adaptive bias and gain` / `only one set of gain and` |

---


## 177. Efficient Streaming Language Models with Attention Sinks

| 字段 | 内容 |
|:--|:--|
| 标题 | Efficient Streaming Language Models with Attention Sinks |
| 作者（前 3） | Guangxuan Xiao · Yuandong Tian · Beidi Chen（共 **5** 位，末位 Mike Lewis；arXiv abs 页逐字核；机构 MIT / Meta AI） |
| 年份 | **2023**（v1 `2023-09-29`；v2 `2024-04-07`） |
| 会议 / 期刊 | **ICLR 2024**（arXiv `comment` 原文 `ICLR 2024`；OpenAlex 该 arXiv DOI 记 `preprint` ⇒ 只按 `comment` 记会议） |
| 被引数 | **1,248**（OpenAlex `10.48550/arxiv.2309.17453`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2309.17453> ｜ DOI `10.48550/arxiv.2309.17453` |
| 一句话贡献 | 发现 **attention sink** 现象：少数**最前面的 token**（语义无关）吸走大量注意力分数，因此只要**保留最初若干 token 的 KV + 最近窗口**（StreamingLLM），窗口有限的模型就能在**最多 4M token** 的流式输入上不微调地稳定工作，比滑动窗口重算基线快 **up to 22.2×**；并指出预训练时**加一个占位 token 当专用 sink** 可进一步改善流式性能。 |
| 与我们工作的关系 | **pretrain（长上下文与位置编码，主目标）**：sink 是**预训练窗口**塑造出的注意力结构，而非推理期修补 ⇒ <b>动作</b>：长上下文实验表新增 `window_len` / `sink_tokens_kept` / `extrapolation_method` 三列，与 RoPE/YaRN 类外推方案分列记录。<br>**pretrain（判据）**：若 4M 长度下 PPL 崩塌而保留前若干 token 后恢复 ⇒ <b>动作</b>：预注册判据 = 先做「保留 k 个初始 token」的 k∈{1,2,4} 扫描，崩塌仍在则判定为位置编码失效而非 KV 淘汰策略问题。<br>**harness（长上下文评测口径）**：流式与「整段喂入」是两种口径 ⇒ <b>动作</b>：长上下文基准必须写明 `streaming(yes/no)` 与 KV 预算，🚫 不与全注意力结果混排。<br>**zhulong（KV 预算与成本）**：KV cache 是长轨迹推理的主要显存项 ⇒ <b>动作</b>：成本表新增 `kv_cache_bytes@length` 一列，按 sink+窗口方案给出与全注意力对照。<br>**风险**：① 1,248 是 OpenAlex 口径；② 22.2× 是对「滑动窗口重算」基线的加速，不等于对全注意力的 22×；③ PDF 16.95MB（≥5MB）⇒ 只本地核验、不入 git。 |
| 首次收录 | **2026-11-16**（第四十五轮） |
| 核验状态 | arXiv abs 页 `200` / 43,362 B（5 作者、`Submitted on 29 Sep 2023 (v1), last revised 7 Apr 2024 (v2)`、`comment` = `ICLR 2024`）；OpenAlex `200` 1,248、`preprint`；PDF `200` / **16,952,848 B**（≥5MB，只在 `/tmp` 核验），`pdftotext` 核对 `attention sink` / `up to 4 million tokens` / `22.2× speedup` / `placeholder token as a dedicated attention sink during pre-training` |

---

## 178. The Curious Case of Neural Text Degeneration

| 字段 | 内容 |
|:--|:--|
| 标题 | The Curious Case of Neural Text Degeneration |
| 作者（前 3） | Ari Holtzman · Jan Buys · Li Du（共 **5** 位，末位 Yejin Choi；arXiv abs 页逐字核；机构 University of Washington / Allen Institute for AI 等） |
| 年份 | **2019**（v1 `2019-04-22`；v2 `2020-02-14`） |
| 会议 / 期刊 | **ICLR 2020**（arXiv `comment` 原文 `Published in ICLR 2020`；OpenAlex 该 arXiv DOI 记 `preprint` ⇒ 只按 `comment` 记会议） |
| 被引数 | **2,832**（OpenAlex `10.48550/arxiv.1904.09751`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1904.09751> ｜ DOI `10.48550/arxiv.1904.09751` |
| 一句话贡献 | 指出「最大化似然」的解码（beam search，size 32）会让 GPT-2 级模型产出**退化重复**文本，而纯采样又跑偏；提出 **Nucleus Sampling（top-p）**：按累积概率截断「不可靠的长尾」，只在**动态核**内采样，人类评测下长文本质量优于当时既有策略。 |
| 与我们工作的关系 | **harness（解码与判分口径，主目标）**：评测分数强依赖解码配置 ⇒ <b>动作</b>：评测报告模板新增 `decoding(beam/top-k/top-p + 参数)` / `temperature` / `max_len` 三列，任何跨模型比较必须同列。<br>**harness（判据）**：论文说明「高概率解码 ≠ 好文本」⇒ <b>动作</b>：预注册判据 = 若某模型在 greedy/beam 下重复 n-gram 比例 &gt;5%，先切 nucleus 解码复核，再判定为模型能力问题。<br>**zhulong（质量-成本权衡）**：纯采样便宜但质量不稳 ⇒ <b>动作</b>：成本表把「解码策略」与「每千 token 成本」并列，长轨迹 rollout 必须写明采样策略。<br>**风险**：① 2,832 是 OpenAlex 口径；② 人类评测基于 2019 年的 GPT-2 级模型，🚫 不能外推为今天对话模型的最优 p 值；③ 论文未给单一推荐 p 值，本线也**不写默认 p**。 |
| 首次收录 | **2026-11-16**（第四十五轮） |
| 核验状态 | arXiv abs 页 `200` / 42,332 B（5 作者、`Submitted on 22 Apr 2019 (v1), last revised 14 Feb 2020 (v2)`、`comment` = `Published in ICLR 2020`）；OpenAlex `200` 2,832、`preprint`；PDF `200` / 4,691,115 B，`pdftotext` 核对 `Beam Search (size 32) leads to degenerate repetition` / `truncating the unreliable tail of the probability distribution` / `dynamic nucleus` |

---
## 179. LIMA: Less Is More for Alignment

| 字段 | 内容 |
|:--|:--|
| 标题 | LIMA: Less Is More for Alignment |
| 作者（前 3） | Chunting Zhou · Pengfei Liu · Puxin Xu（共 **15** 位，末位 Omer Levy；arXiv abs 页逐字核；署名机构含 Meta AI / CMU / NYU 等） |
| 年份 | **2023**（abs 页 `Submitted on 18 May 2023`，单版本） |
| 会议 / 期刊 | **NeurIPS 2023**（arXiv `comment` 为空、PDF 首页仍写 `Preprint. Under review` ⇒ 会议**只取 OpenAlex**：`primary_location.source` = `neural information processing systems`、DOI `10.52202/075280-2400`、pp. 55006–55021） |
| 被引数 | **904**（OpenAlex `10.48550/arxiv.2305.11206`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.11206> ｜ DOI `10.48550/arxiv.2305.11206` |
| 一句话贡献 | 在 **65B LLaMA** 上只用 **1,000 条**人工精选 prompt–response（约 **750,000 token**）做**无 RLHF** 的监督微调，对照人类评测中「等价或更优」的比例对 GPT-4 为 **43%**、对 Bard 为 **58%**、对 DaVinci003 为 **65%**，88% 回答满足要求 ⇒ 主张对齐主要在教**风格 / 格式**，知识几乎全在预训练里；消融显示只加数据量不加 prompt 多样性收益急剧递减，优化**质量**收益明显。 |
| 与我们工作的关系 | **data（SFT 数据账本，主目标）**：给「指令数据量 vs 多样性 vs 质量」一个可引用的对照点 ⇒ <b>动作</b>：`data` 线账本新增 `n_examples` / `prompt_diversity`（按任务簇计）/ `tokens` 三列，任何「加数据」决策必须先固定多样性档位。<br>**data（判据）**：论文的递减收益结论是在**英文、通用助手**任务上得到的 ⇒ <b>动作</b>：预注册判据 = 中文 / 代码 / EDA 三域各取 1k 与 10k 两档，若 10k 档相对 1k 档的胜率提升 &lt;3pt，则判定该域进入「加数据无用」区，改投多样性或难度分层。<br>**harness（评测口径）**：43%/58%/46% 这类数字强依赖**标注者、对照组与提示集** ⇒ <b>动作</b>：偏好评测报告必须写 `annotator`（人群 / 模型）、`baseline`（哪个版本）、`prompt_set` 三项，🚫 不写单个数就当 SOTA。<br>**zhulong（成本口径）**：无需多轮对话数据也能产生多轮行为 ⇒ <b>动作</b>：成本表把「对齐阶段 token 预算」与「多轮数据采集成本」分列，先证明 1k 档不足再加。<br>**风险**：① 904 是 OpenAlex 口径；② 会议信息来自 OpenAlex，arXiv 自身无 `comment`；③ 65B + 1k 的结论**不能**直接外推到 2B 规模（容量与知识量都不同）。 |
| 首次收录 | **2026-11-16**（第四十六轮） |
| 核验状态 | arXiv abs 页 `200` / 43,595 B（15 作者、`Submitted on 18 May 2023`、`comment` = NONE）；arXiv API `id_list` `200` + `application/atom+xml; charset=utf-8`；OpenAlex `200`（904、`conference-paper`、NeurIPS 2023、pp. 55006–55021）；PDF `200` / 499,719 B，`pdftotext` 核对 `1,000 carefully curated` / `750,000 tokens` / `43%` / `58%` / `65%` / `88% meet the prompt requirements` / `diminishing returns when scaling up data quantity` |

---

## 180. The False Promise of Imitating Proprietary LLMs

| 字段 | 内容 |
|:--|:--|
| 标题 | The False Promise of Imitating Proprietary LLMs（OpenReview / ICLR 版标题写作 `…Proprietary Language Models`，同一工作） |
| 作者（前 3） | Arnav Gudibande · Eric Wallace · Charlie Snell（共 **8** 位，末位 Dawn Song；arXiv abs 页逐字核；UC Berkeley 等） |
| 年份 | **2023**（abs 页 `Submitted on 25 May 2023`，单版本） |
| 会议 / 期刊 | **ICLR 2024 spotlight**（OpenReview `venue` 字段原文 `ICLR 2024 spotlight`，forum `Kz3yckpCN5`；OpenAlex 该 arXiv DOI 记 `preprint` ⇒ 会议只按 OpenReview 记） |
| 被引数 | **304**（OpenAlex `10.48550/arxiv.2305.15717`，查询日 **2026-11-16**；S2 未查）｜⚠️ **&lt;500，按「方法论常青」收录**（合成 / 模仿数据路线的反例基准，至今被反复对比） |
| arXiv / DOI | <https://arxiv.org/abs/2305.15717> ｜ DOI `10.48550/arxiv.2305.15717` |
| 一句话贡献 | 用 ChatGPT 输出蒸馏出 **0.3M–150M token** 的模仿模型：众包评分里约 **70%** 判为与 ChatGPT 相当，但换成**定向自动评测**后，模仿模型在「模仿数据未覆盖」的任务上**几乎没有缩小**与 ChatGPT 的差距 —— 它们擅长模仿**风格**而非**事实性**；继续加模仿数据收益趋平，而**扩大基座模型**才稳步提升 ⇒「模型模仿是虚假承诺」。 |
| 与我们工作的关系 | **data（合成数据天花板，主目标）**：给「用强模型蒸馏 / 自举」划出一条实测边界 ⇒ <b>动作</b>：`data` 线新增 `imitation_tokens` / `covered_task_clusters` 两列，任何合成数据批次必须标注它覆盖了哪些任务簇。<br>**data（判据）**：论文的对照是「加模仿数据 vs 加基座规模」⇒ <b>动作</b>：预注册判据 = 在固定算力下，若「+1 档模仿数据」的定向自动评测提升 &lt;「+1 档基座」的一半，则判定进入模仿收益枯竭区，转投真实数据或难度上采样。<br>**harness（评测口径）**：众包高分与真实能力脱钩是本文的核心发现 ⇒ <b>动作</b>：评测报告必须同时给「众包 / 人类偏好」与「定向自动评测」两列，二者冲突时以定向自动评测为准。<br>**zhulong（奖励设计）**：把另一个模型的输出当奖励/目标，会奖励风格而非正确性 ⇒ <b>动作</b>：RL 奖励表里禁止单用「模仿似然」项，必须挂可验证判据。<br>**风险**：① 304 是 OpenAlex 口径且 &lt;500；② 实验基于 2023 年的 ChatGPT 与较小基座，🚫 不能直接断言今天的强模型蒸馏同样无效；③ 会议信息来自 OpenReview（非 arXiv `comment`）。 |
| 首次收录 | **2026-11-16**（第四十六轮） |
| 核验状态 | arXiv abs 页 `200` / 42,562 B（8 作者、`Submitted on 25 May 2023`、`comment` = NONE）；arXiv API `id_list` `200` + atom；OpenAlex `200`（304、`preprint`）；OpenReview `notes/search` `200`（`venue` = `ICLR 2024 spotlight`，forum `Kz3yckpCN5`）；PDF `200` / 1,051,380 B，`pdftotext` 核对 `∼70%` / `mimicking ChatGPT’s style but not its factuality` / `model imitation is a false promise` / `0.3M–150M tokens` |

---

## 181. Muon is Scalable for LLM Training

| 字段 | 内容 |
|:--|:--|
| 标题 | Muon is Scalable for LLM Training |
| 作者（前 3） | Jingyuan Liu · Jianlin Su · Xingcheng Yao（共 **28** 位，末位 Zhilin Yang；arXiv abs 页逐字核；Moonshot AI 等） |
| 年份 | **2025**（abs 页 `Submitted on 24 Feb 2025`，单版本 v1） |
| 会议 / 期刊 | **预印本**（arXiv `comment` = NONE；OpenAlex 该 arXiv DOI `type` = `preprint`、source = arXiv ⇒ 本轮**没有**任何一手会议证据，🚫 不写会场） |
| 被引数 | **622**（OpenAlex `10.48550/arxiv.2502.16982`，查询日 **2026-11-16**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2502.16982> ｜ DOI `10.48550/arxiv.2502.16982` |
| 一句话贡献 | 把 Muon（用 **Newton–Schulz 迭代做近似正交化**的二阶动量优化器）推到十亿参数 / 万亿 token：给出两个关键技巧 —— **(1) 加 weight decay、(2) 逐参数重标 update scale**，使其开箱即用不需逐层调参；scaling law 实验称相对 AdamW 约 **2× compute efficiency**；据此训练 **Moonlight 3B/16B MoE、5.7T token**，并开源**分布式实现**（ZeRO-1 式切分 + 兼容 TP/PP/EP/DP，内存最优、通信更省）。 |
| 与我们工作的关系 | **pretrain（优化器与训练稳定性，主目标）**：给「换优化器」提供一个**带两个必要补丁**的对照点 ⇒ <b>动作</b>：优化器对照表新增 `weight_decay` / `update_scale_rule` / `ns_steps`（Newton–Schulz 迭代步数）三列，🚫 不允许只写「用 Muon」而不写这三项。<br>**pretrain（判据）**：2× 来自 **compute-optimal scaling law 外推**而非端到端全量对跑 ⇒ <b>动作</b>：预注册判据 = 在 2B 规模、固定 token 预算下做 AdamW vs Muon 双跑，若 Muon 的 loss 未在相同步数内低 0.02 以上，则判定 2× 不可迁移，回到 AdamW + 调 warmup。<br>**pretrain（稳定性）**：正交化改的是更新方向与谱范数 ⇒ <b>动作</b>：训练监控表把 `update_norm / param_norm`（逐层）与 loss spike 时间戳对齐，spike 出现时先看该项是否跳变再怀疑数据。<br>**zhulong（成本口径）**：可省的是**算力**不是显存 ⇒ <b>动作</b>：成本表把「优化器 state 字节数」单列（Muon 只对矩阵参数维护动量，非矩阵参数仍用 AdamW），估算 2B 模型的显存预算时不得一律按 AdamW 的 2× 参数量计。<br>**风险**：① 622 是 OpenAlex 口径；② 2× 是 scaling law 外推值，**不是**端到端实测加速；③ 论文为预印本，无会场与同行评审证据。 |
| 首次收录 | **2026-11-16**（第四十六轮） |
| 核验状态 | arXiv abs 页 `200` / 45,291 B（28 作者、`Submitted on 24 Feb 2025`、`comment` = NONE）；arXiv API `id_list` `200` + atom；OpenAlex `200`（622、`preprint`）；PDF `200` / 2,077,505 B（`pdftotext` 有一条 `Invalid blend mode in ExtGState` 警告但正文可解析，57,172 字符），核对 `adding weight decay` / `per-parameter update scale` / `∼ 2× computational efficiency` / `5.7T tokens` / `3B/16B` / `Newton-Schulz` / `ZeRO-1` |

---

## 182. FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision

| 字段 | 内容 |
|:--|:--|
| 标题 | FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision |
| 作者（前 3） | Jay Shah · Ganesh Bikshandi · Ying Zhang（共 **6** 位，末位 Tri Dao；arXiv abs 页逐字核） |
| 年份 | **2024**（abs 页 `Submitted on 11 Jul 2024 (v1), last revised 12 Jul 2024 (v2)`） |
| 会议 / 期刊 | **NeurIPS 2024**（arXiv `comment` = NONE ⇒ 会议**只取 OpenAlex**：`primary_location.source` = `neural information processing systems`、`publication_year` 2024、DOI `10.52202/079017-2193`、pp. 68658–68685） |
| 被引数 | **418**（OpenAlex `10.48550/arxiv.2407.08608`，查询日 **2026-11-16**；S2 未查）｜⚠️ **&lt;500，按「开创范式 + 方法论常青」收录**（Hopper 上 attention kernel 的当前标尺） |
| arXiv / DOI | <https://arxiv.org/abs/2407.08608> ｜ DOI `10.48550/arxiv.2407.08608` |
| 一句话贡献 | 针对 Hopper（H100）架构用**异步执行（TMA + warp-specialization）+ 低精度（FP8）**重写 attention：相对 FlashAttention-2 前向 **1.5–2.0×**、反向 **1.5–1.75×**，FP16 达 **740 TFLOPs/s（75% 利用率）**、FP8 接近 **1.2 PFLOPs/s**；并用 incoherent processing 把 FP8 的数值误差压到比基线 FP8 attention **低 2.6×** —— 起点是 FlashAttention-2 在 H100 上只有 **35%** 利用率。 |
| 与我们工作的关系 | **pretrain（MFU 标尺，主目标）**：给「attention 还能快多少」一个可引用上限 ⇒ <b>动作</b>：训练报告把 `attn_kernel`（实现名 + 版本）/ `dtype`（FP16/BF16/FP8）/ `utilization` 三列并入，与 `tokens/s` 一起报。<br>**pretrain（判据）**：740 TFLOPs/s 是**单项 kernel 前向**数字 ⇒ <b>动作</b>：预注册判据 = 端到端 MFU 提升 &lt; kernel 提升的 1/3 时，判定瓶颈已转移到非 attention 部分（MLP / 通信 / 数据加载），改查数据管线而不是继续升级 kernel。<br>**harness（长上下文评测成本）**：attention 成本随长度超线性 ⇒ <b>动作</b>：长上下文基准表新增 `attn_impl` / `seq_len` / `prefill_time` 三列，🚫 不同 kernel 的结果不混排。<br>**zhulong（rollout 成本）**：长轨迹推理里 attention 占比高 ⇒ <b>动作</b>：成本表把 `prefill` 与 `decode` 的 attention 时间分开记，decode 侧不套用 prefill 的加速比。<br>**风险**：① 418 是 OpenAlex 口径且 &lt;500；② 数据全部来自 H100 SXM5，🚫 不能外推到其他卡型；③ 会议信息来自 OpenAlex（arXiv 无 `comment`）；④ FP8 的正确性只在该文设定的误差度量下比较过。 |
| 首次收录 | **2026-11-16**（第四十六轮） |
| 核验状态 | arXiv abs 页 `200` / 43,000 B（6 作者、`Submitted on 11 Jul 2024 (v1), last revised 12 Jul 2024 (v2)`、`comment` = NONE）；arXiv API `id_list` `200` + atom；OpenAlex `200`（418、`conference-paper`、NeurIPS 2024、pp. 68658–68685）；PDF `200` / 1,096,663 B，`pdftotext` 核对 `740 TFLOPs/s (75% utilization)` / `1.2 PFLOPs/s` / `1.5-2.0×` / `2.6× lower numerical error` / `35% utilization on the H100` |

---

## 183. Competition-Level Code Generation with AlphaCode

| 字段 | 内容 |
|:--|:--|
| 标题 | Competition-Level Code Generation with AlphaCode |
| 作者（前 3） | Yujia Li · David Choi · Junyoung Chung（共 **26** 位，末位 Oriol Vinyals；arXiv API `id_list` 逐字核） |
| 年份 | **2022**（v1 `2022-02-08`） |
| 会议 / 期刊 | **Science 2022**（OpenAlex：`type` = `article`、DOI `10.1126/science.abq1158`、`publication_year` 2022；arXiv abs 页 `comment` 仅 `74 pages`） |
| 被引数 | **1,787**（OpenAlex `10.48550/arxiv.2203.07814`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2203.07814> ｜ 期刊 DOI `10.1126/science.abq1158` |
| 一句话贡献 | 把「竞赛级编程」做成**大规模采样 + 执行过滤**的工程闭环：每题生成海量候选程序，先用题目自带示例测试筛掉行为不符的，再按输出行为聚类，只提交最多 **10** 个候选 —— 在 Codeforces 上 >**5,000** 人参赛的比赛中模拟评测，平均排名进入前 **54.3%**。 |
| 与我们工作的关系 | **harness（执行式判分与过滤，主目标）**：它证明「判分器 = 执行结果」时，模型能力之外的最大杠杆是**过滤 + 去重策略** ⇒ <b>动作</b>：agent 评测报告分开记 `采样数 n` / `过滤后保留数` / `提交数 k`，🚫 只报最终的 pass@1。<br>**zhulong（成本口径）**：1,787 被引的工作把「算力换正确率」写成了显式配方 ⇒ <b>动作</b>：成本表新增 `生成 token / 有效提交` 一列，用于和「单次采样 + 自一致性」对照。<br>**data（可验证语料）**：题目自带示例测试是天然的去污染信号 ⇒ <b>动作</b>：造题管线为每题至少配 2 条公开示例 + 1 条隐藏用例，公开示例用于训练期自检、隐藏用例只用于判分。<br>**风险**：① 被引 1,787 为 OpenAlex 口径（含 Science 版与预印本合并计数）；② 平均排名 54.3% 是**模拟**评测结果，🚫 不等于真实比赛成绩；③ 十选一的聚类依赖可执行样例，抽样成本高。 |
| 首次收录 | **2026-11-17**（第四十七轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（26 作者、`published 2022-02-08T23:16:31Z`）；OpenAlex `200`（1,787、`article`、Science、DOI `10.1126/science.abq1158`）；PDF `200` / 3,797,220 B，`pdftotext` 核对 `top 54.3%` / `more than 5,000 participants` / `10 simulated Codeforces contests` / `three key components` |

---

## 184. BLOOM: A 176B-Parameter Open-Access Multilingual Language Model

| 字段 | 内容 |
|:--|:--|
| 标题 | BLOOM: A 176B-Parameter Open-Access Multilingual Language Model |
| 作者（前 3） | BigScience Workshop · Teven Le Scao ·（workgroup 署名，共 **394** 位，末位 Thomas Wolf；arXiv API 逐字核） |
| 年份 | **2022**（v1 `2022-11-09`；v4 `2023-06-27`） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `type` = `preprint`、`primary_location.source` = arXiv；arXiv `comment` = NONE） |
| 被引数 | **2,860**（OpenAlex `10.48550/arxiv.2211.05100`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2211.05100> ｜ DOI `10.48550/arxiv.2211.05100` |
| 一句话贡献 | 176B 参数 decoder-only 开源多语模型，训练语料 **ROOTS** 覆盖 **46 种自然语言 + 13 种编程语言（共 59 种）**，并把数据许可 / 来源审计与多语评测一并公开。 |
| 与我们工作的关系 | **data（多语配额与许可审计，主目标）**：59 种语言的语料配比与来源审计是「中文为主 + 代码」配比决策的直接参照 ⇒ <b>动作</b>：数据台账为每种语言记 `来源数` / `许可类型` / `去重前后 token`，🚫 只记总量。<br>**pretrain（多语 tokenizer 压缩率）**：176B 规模的多语训练成本基线 ⇒ <b>动作</b>：训练报告把 `tokens/char` 按语种拆开报（英文 vs 中文 vs 代码），用于校准同一 token 预算下的有效信息量。<br>**vision（多语图文对的来源）**：ROOTS 的许可分级做法可迁移到图文对采集 ⇒ <b>动作</b>：图文数据采集表加 `许可` / `是否可商用` 两列。<br>**风险**：① 394 位作者的署名方式使「谁负责数据治理」不可追；② 2,860 为 OpenAlex 口径；③ 预印本无同行评审，语料比例的统计口径需以附录原文为准。 |
| 首次收录 | **2026-11-17**（第四十七轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（394 作者、`published 2022-11-09T18:48:09Z`、`updated 2023-06-27T09:57:58Z`）；OpenAlex `200`（2,860、`preprint`、arXiv）；PDF `200` / 3,029,243 B，`pdftotext` 核对 `176B-parameter open-access` / `ROOTS corpus` / `46 natural and 13 programming languages (59 in total)` |

---

## 185. StarCoder: may the source be with you!

| 字段 | 内容 |
|:--|:--|
| 标题 | StarCoder: may the source be with you! |
| 作者（前 3） | Raymond Li · Loubna Ben Allal · Yangtian Zi（共 **67** 位，末位 Harm de Vries；arXiv API 逐字核） |
| 年份 | **2023**（v1 `2023-05-09`；v2 `2023-12-13`） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `type` = `preprint`、arXiv；arXiv `comment` = NONE） |
| 被引数 | **1,518**（OpenAlex `10.48550/arxiv.2305.06161`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.06161> ｜ DOI `10.48550/arxiv.2305.06161` |
| 一句话贡献 | **StarCoderBase 在 The Stack 的 1 万亿 token 上训练**（仅用许可明确的 GitHub 仓库，并提供 **opt-out** 下架流程）；配套多查询注意力（MQA）支撑大 batch 推理，使 15B 级代码模型可实际服务。 |
| 与我们工作的关系 | **data（代码语料质量筛 + opt-out 治理，主目标）**：把「许可过滤 + opt-out + 检查工具」写成可复制的数据治理流程 ⇒ <b>动作</b>：代码语料台账新增 `许可判定方式` / `opt-out 命中数` / `检查工具版本` 三列。<br>**zhulong（代码 agent 底座）**：1T token 的代码配方是「代码能力下限」的参照 ⇒ <b>动作</b>：中文 / 代码配比实验把 StarCoder 式过滤（去重 + 许可 + 质量分类器）作为对照组之一，预注册「同 token 预算下 pass@1 差值」。<br>**pretrain（MQA 吞吐）**：MQA 与大 batch 推理的绑定关系 ⇒ <b>动作</b>：推理服务配置表把 `kv_heads` 与 `max_batch` 一起记，避免只调 batch 不看 kernel。<br>**风险**：① 1,518 为 OpenAlex 口径；② The Stack 的 opt-out 是一手治理数据但本线未复现比例；③ 预印本，无同行评审。 |
| 首次收录 | **2026-11-17**（第四十七轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（67 作者、`published 2023-05-09T08:16:42Z`、`updated 2023-12-13T14:44:10Z`）；OpenAlex `200`（1,518、`preprint`、arXiv）；PDF `200` / 1,174,499 B，`pdftotext` 核对 `1 trillion tokens` / `The Stack` / `permissively licensed GitHub repositories` / `opt-out process` / `multi-query attention` |

---

## 186. Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback

| 字段 | 内容 |
|:--|:--|
| 标题 | Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback |
| 作者（前 3） | Yuntao Bai · Andy Jones · Kamal Ndousse（共 **31** 位，末位 Jared Kaplan；arXiv API 逐字核） |
| 年份 | **2022**（v1 `2022-04-12`） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `type` = `preprint`、arXiv；arXiv `comment` = `Data available at https://github.com/anthropics/hh-rlhf`） |
| 被引数 | **5,138**（OpenAlex `10.48550/arxiv.2204.05862`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2204.05862> ｜ DOI `10.48550/arxiv.2204.05862`；数据 <https://github.com/anthropics/hh-rlhf> |
| 一句话贡献 | 用偏好建模 + RLHF 同时优化「有用」与「无害」，并系统比较**离线偏好训练**与**在线迭代 RLHF**（偏好模型与策略交替更新，最大规模 **52B**），公开 HH-RLHF 数据集。 |
| 与我们工作的关系 | **posttrain（对齐数据与在线迭代，主目标）**：离线偏好 vs 在线迭代 RLHF 的对照是后训练配方的直接基线 ⇒ <b>动作</b>：后训练实验表把 `preference_data_version` / `是否在线迭代` / `策略更新轮数` 列为必填。<br>**harness（有用 vs 无害的联合判分）**：两个目标同时评测、分开报 ⇒ <b>动作</b>：评测报告把 `helpfulness` 与 `harmlessness` 分成两列，🚫 不给单一总分掩盖冲突。<br>**zhulong（thinking 轴的取舍）**：无害性往往与「拒绝回答」相关，长思考轨迹下更易触发 ⇒ <b>动作</b>：消融里单列「过度拒答率」指标。<br>**风险**：① 5,138 为 OpenAlex 口径；② 52B 的在线迭代成本未在该文中给出可复用的单位成本；③ 预印本，数据集的标注口径以仓库为准。 |
| 首次收录 | **2026-11-17**（第四十七轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（31 作者、`published 2022-04-12T15:02:38Z`）；OpenAlex `200`（5,138、`preprint`、arXiv）；PDF `200` / 9,503,688 B（<5MB 门槛内，未入 git），`pdftotext` 核对 `preference modeling and reinforcement learning from human feedback` / `iterated online mode` / `Online HH RLHF (52B)` |

---

## 187. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena

| 字段 | 内容 |
|:--|:--|
| 标题 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena |
| 作者（前 3） | Lianmin Zheng · Wei-Lin Chiang · Ying Sheng（等；UC Berkeley / UC San Diego / CMU 等） |
| 年份 | **2023**（v1 `2023-06-09`；最新 v4 `2023-12-24`） |
| 会议 / 期刊 | **NeurIPS 2023 Datasets and Benchmarks Track**（arXiv `comment` 与会场口径；OpenAlex `type` = `conference-paper`） |
| 被引数 | **5,326**（OpenAlex `10.48550/arxiv.2306.05685`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2306.05685> ｜ DOI `10.48550/arxiv.2306.05685`；数据/代码 <https://github.com/lm-sys/FastChat> |
| 一句话贡献 | 提出 MT-Bench（80 道多轮题、8 类能力）与 Chatbot Arena，系统检验「用强 LLM 当裁判」的可靠性：GPT-4 判分与人类偏好一致率 **超 80%**，与人类-人类一致率同量级；同时给出位置偏差、冗长偏好、自我增强偏差三类失效模式。 |
| 与我们工作的关系 | **harness（判分口径，主目标）**：把「LLM-as-a-Judge 可不可信」变成可测的三类偏差 ⇒ <b>动作</b>：我们的评测报告必须单列 `judge_model` / `position_swapped`（A/B 换位重判）/ `length_controlled`（长度受控胜率），🚫 只报单一胜率。<br>**zhulong（奖励设计）**：若用 judge 当奖励，冗长偏好会直接推高生成长度 ⇒ <b>动作</b>：奖励表加 `len_corr`（奖励与回答长度的相关系数）作为告警指标。<br>**data（偏好数据）**：位置/冗长偏差会污染偏好对 ⇒ <b>动作</b>：构造偏好对时强制随机化位置并记录长度差分布。<br>**风险**：① 5,326 为 OpenAlex 口径；② 结论基于 2023 年的 GPT-4 裁判，换到今天的主干需重测；③ 80 题规模小，不适合当能力评测全集。 |
| 首次收录 | **2026-11-17**（第四十八轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（`published 2023-06-09T17:44:31Z`、`updated 2023-12-24`）；OpenAlex `200`（5,326、`conference-paper`）；PDF `200` / 1,580,141 B（<5MB，未入 git），`pdftotext` 核对 `over 80% agreement` / `80 MT-bench questions` / `3K expert votes` / `6 models: GPT-4, GPT-3.5, Claude-V1` |

---

## 188. Self-Rewarding Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Self-Rewarding Language Models |
| 作者（前 3） | Weizhe Yuan · Richard Yuanzhe Pang · Kyunghyun Cho（共 7 位，末位 Jason Weston；Meta / NYU） |
| 年份 | **2024**（v1 `2024-01-18`；v3 `2025-03-28`） |
| 会议 / 期刊 | **ICML 2024**（arXiv `comment`；OpenAlex `preprint` 记录） |
| 被引数 | **664**（OpenAlex `10.48550/arxiv.2401.10020`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2401.10020> ｜ DOI `10.48550/arxiv.2401.10020` |
| 一句话贡献 | 让模型同时当「答题者」与「裁判」：用 LLM-as-a-Judge 给自己的回答打偏好、做**迭代 DPO**（Llama-2-70B，3 轮），既提升指令跟随、也提升自评能力；对 GPT-4-Turbo 的 AlpacaEval 2.0 胜率 **9.94% → 15.38% → 20.44%**。 |
| 与我们工作的关系 | **posttrain（自奖励/自标注，主目标）**：给出「无人工偏好也能迭代」的最小闭环 ⇒ <b>动作</b>：后训练表把 `reward_source=human|judge|checker` 与 `self_reward_rounds` 列为必填，并记录每轮自评与外部评的一致率。<br>**data（合成偏好对）**：自造偏好对会放大自身偏差 ⇒ <b>动作</b>：合成偏好集必须留 10% 人工抽检，报告「自评-人评一致率」。<br>**zhulong（可验证奖励）**：与我们的 checker 奖励互补 —— 自奖励适合无 checker 的开放式任务，二者需分列。<br>**风险**：① 664 为 OpenAlex 口径；② 70B 规模 + 英文 AlpacaEval，2B 中文场景不可直接外推；③ 「自评能力提升」是作者自报的胜率，非独立复现。 |
| 首次收录 | **2026-11-17**（第四十八轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（7 作者、`published 2024-01-18T14:43:47Z`）；OpenAlex `200`（664、`preprint`）；PDF `200` / 1,136,245 B，`pdftotext` 核对 `Iterative DPO training` / `9.94% in Iteration 1, to 15.38% in Iteration 2, to 20.44% in Iteration 3` / `AlpacaEval 2.0` |

---

## 189. TinyStories: How Small Can Language Models Be and Still Speak Coherent English?

| 字段 | 内容 |
|:--|:--|
| 标题 | TinyStories: How Small Can Language Models Be and Still Speak Coherent English? |
| 作者（前 3） | Ronen Eldan · Yuanzhi Li（2 位；Microsoft Research） |
| 年份 | **2023**（v1 `2023-05-12`；v2 `2023-05-24`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type` = `preprint`） |
| 被引数 | **589**（OpenAlex `10.48550/arxiv.2305.07759`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.07759> ｜ DOI `10.48550/arxiv.2305.07759`；数据 <https://huggingface.co/datasets/roneneldan/TinyStories> |
| 一句话贡献 | 用 GPT-3.5/GPT-4 生成「3–4 岁儿童能懂」的合成短故事（受控词表约 **1,500** 词），证明 **1M–33M 参数**的小模型也能产出语法连贯、有基本事实与推理的英文，并提出用 GPT-4 打分替代人工评测的范式。 |
| 与我们工作的关系 | **data（合成数据与词表控制，主目标）**：把「数据复杂度」当作可控变量 ⇒ <b>动作</b>：合成语料登记表新增 `vocab_domain_size`（受控词表规模）/ `generator_version`（GPT-3.5/GPT-4 及版本）/ `grader_model`；<b>判据</b>：任何「合成数据提升小模型」结论须同时报这三列，否则不可比。<br>**SLM（规模-能力曲线）**：1M–33M 的参数-能力对照可直接当 SLM 的能力下限基线 ⇒ <b>动作</b>：SLM 评测加一档「玩具语料上的连贯性」作为冒烟测试。<br>**risk / 风险**：① 589 为 OpenAlex 口径；② 任务是「儿童故事」，与代码/EDA 域差距大，只能借方法论不能借数据；③ GPT-4 打分本身有偏差（见 #187）。 |
| 首次收录 | **2026-11-17**（第四十八轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（`published 2023-05-12`、2 作者）；OpenAlex `200`（589、`preprint`）；PDF `200` / 4,069,571 B（<5MB），`pdftotext` 核对 `vocabulary consisting of about 1500 basic words` / `TinyStories-1M/3M/9M/28M/33M` / `single V100 GPU within at most 30 hours` |

---

## 190. Mind2Web: Towards a Generalist Agent for the Web

| 字段 | 内容 |
|:--|:--|
| 标题 | Mind2Web: Towards a Generalist Agent for the Web |
| 作者（前 3） | Xiang Deng · Yu Gu · Boyuan Zheng（共 8 位，末位 Yu Su；The Ohio State University） |
| 年份 | **2023**（v1 `2023-06-09`；v3 `2023-12-09`） |
| 会议 / 期刊 | **NeurIPS 2023 Spotlight**（arXiv `comment`；OpenAlex `conference-paper`） |
| 被引数 | **503**（OpenAlex `10.48550/arxiv.2306.06070`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2306.06070> ｜ DOI `10.48550/arxiv.2306.06070`；数据/代码 <https://osu-nlp-group.github.io/Mind2Web> |
| 一句话贡献 | 首个「通用 Web agent」数据集：**137 个真实网站 / 31 个域 / 逾 2,000 条**任务，按 **cross-task / cross-website / cross-domain** 三切分评测泛化；候选生成用 DeBERTa-86M 达 `Recall@50` **88.9% / 85.3% / 85.7%**，再交给 LLM 做动作预测。 |
| 与我们工作的关系 | **harness（Web/工具 agent 评测，主目标）**：三切分是「同分布 vs 跨域」的最小对照 ⇒ <b>动作</b>：harness 报告任何 Web/工具任务分数时必须标切分，🚫 只报同分布；并把 `candidate_recall@k` 与 `end_to_end_success` 分成两列（该文显示候选召回很高、端到端仍低）。<br>**designflow（题面保真）**：真实网站快照 + 三切分是造题的现成骨架 ⇒ <b>动作</b>：L3+ 题面记录 `site_snapshot_date` 与 `domain`，防止快照漂移导致不可复现。<br>**zhulong（终态判分）**：元素匹配判分与任务终态判分不等价 ⇒ <b>动作</b>：奖励定义需注明是「元素命中」还是「终态达成」。<br>**风险**：① 503 为 OpenAlex 口径；② 网页会漂移，原始快照未长期托管；③ Spotlight 结论基于 2023 年的模型，现市值需重测。 |
| 首次收录 | **2026-11-17**（第四十八轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（8 作者、`published 2023-06-09T17:44:31Z`、`comment` = `NeurIPS'23 Spotlight`）；OpenAlex `200`（503、`conference-paper`）；PDF `200` / 7,635,816 B（**>5MB ⇒ 仅存 `/tmp`，不入 git**），`pdftotext` 核对 `over 2,000 open-ended tasks collected from 137 websites` / `31 different domains` / `88.9% / 85.3% / 85.7% Recall@50` |

---

## 191. The Stack: 3 TB of permissively licensed source code

| 字段 | 内容 |
|:--|:--|
| 标题 | The Stack: 3 TB of permissively licensed source code |
| 作者（前 3） | Denis Kocetkov · Raymond Li · Loubna Ben Allal（共 **13** 位，末位 Leandro von Werra；ServiceNow Research / Hugging Face；arXiv API 逐字核） |
| 年份 | **2022**（`published 2022-11-20T18:15:30Z`，单版本 v1） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `primary_location.source` = `arXiv (Cornell University)`，无会场 DOI ⇒ 不记会议） |
| 被引数 | **553**（OpenAlex `10.48550/arxiv.2211.15533`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2211.15533> ｜ DOI `10.48550/arxiv.2211.15533`；数据 <https://huggingface.co/datasets/bigcode/the-stack> |
| 一句话贡献 | 只用**宽松许可（permissive license）**的 GitHub 代码构建 **3.1 TB / 30 种编程语言**语料：从 GHArchive 拿到许可信息的 **2,640 万**仓库、其余 **1.109 亿**仓库因许可不明被排除，再做近似去重与 opt-out 治理；仅用该许可子集训练的模型在 HumanEval / MBPP 上已能超过同规模「许可不明」数据基线（作者自报）。 |
| 与我们工作的关系 | **data（代码语料合规与许可过滤，主目标）**：把「许可」当作可执行过滤器而非事后声明 ⇒ <b>动作</b>：代码语料流水线新增 `license` / `license_source`（仓库 LICENSE / GHArchive）/ `opt_out_checked` 三列，未填不许进训练集；<b>判据</b>：任何「代码占比提升」结论必须同时报这三列。<br>**data（去重口径）**：语料规模以「去重后 token」而非「下载字节」记账 ⇒ <b>动作</b>：账本同时记 `raw_bytes` / `near_dedup_bytes` / `tokens`，禁止拿 GB 数对比不同流水线。<br>**pretrain（代码比例实验）**：本文的许可子集是可复现的下限基线 ⇒ <b>动作</b>：配比消融里把「许可子集」固定为对照臂，代码比例每次只动一个变量。<br>**风险**：① 553 为 OpenAlex 口径；② 30 种语言中中文 / EDA 相关语料极少，🚫 不能据此外推 Verilog / TCL 覆盖度；③ 2022 年 GitHub 快照，许可分布与今天不同；④ HumanEval / MBPP 为作者自报，本线未复现。 |
| 首次收录 | **2026-11-17**（第四十九轮） |
| 核验状态 | arXiv API `id_list` `200` + `atom`（12,622 B / 4 entry 复合查询；13 作者、`published 2022-11-20T18:15:30Z`、`primary_category=cs.CL`）；OpenAlex `200`（553、arXiv 源）；PDF `200` / 736,600 B（27 页，<5MB），`pdftotext` 核对 `3.1 TB` / `30 programming languages` / `26.4M repositories` / `110.9M` |

---

## 192. Code Llama: Open Foundation Models for Code

| 字段 | 内容 |
|:--|:--|
| 标题 | Code Llama: Open Foundation Models for Code |
| 作者（前 3） | Baptiste Rozière · Jonas Gehring · Fabian Gloeckle（共 **26** 位，末位 Gabriel Synnaeve；Meta AI；arXiv API 逐字核） |
| 年份 | **2023**（v1 `2023-08-24`；v3 `2024-01-31`） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `comment` 为空、OpenAlex `preprint` ⇒ 不记会议） |
| 被引数 | **4,881**（OpenAlex `10.48550/arxiv.2308.12950`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2308.12950> ｜ DOI `10.48550/arxiv.2308.12950`；代码/权重 <https://github.com/facebookresearch/codellama> |
| 一句话贡献 | 在 Llama 2 上继续训练出 **7B / 13B / 34B / 70B** 四档代码模型（Code Llama / Python 专化 / Instruct）：**16k** 训练序列、对 **100k** 输入仍有改进；7B/13B/70B 支持按上下文填空（fill-in-the-middle）的 infilling 目标，而 **34B 未用 infilling** 训练；除 70B 用 **1T** token 外其余为 **500B** token；作者自报 HumanEval **67%** / MBPP **65%**。 |
| 与我们工作的关系 | **data（代码语料配比与专化，主目标）**：同一基座用「通用代码 / Python 专化 / 指令版」三条分支对比，说明专化数据不必另起模型 ⇒ <b>动作</b>：数据线账本新增 `code_specialization`（general / python / instruct）维度，配比实验按此分层报告。<br>**pretrain（长上下文与训练长度）**：16k 训练、100k 推理的「训练长度 &lt; 使用长度」组合是可复现的廉价方案 ⇒ <b>动作</b>：长上下文消融增加 `train_len` / `eval_len` 两列，先试 16k→100k 外推再决定是否全量长训。<br>**pretrain（infilling 目标）**：7B/13B/70B 支持、34B 不支持 ⇒ <b>动作</b>：目标函数表把 `FIM` 单列并注明「按模型规模开关」，避免把 34B 的缺项误当全局结论。<br>**harness（代码评测口径）**：67% / 65% 是 pass@1 自报 ⇒ <b>动作</b>：代码评测报告必须写 `pass@k` 的 k、温度与去重口径，🚫 不与其他 benchmark 混排。<br>**风险**：① 4,881 为 OpenAlex 口径；② 训练数据未公开，配比不可复现；③ 中文 / EDA 域未评测，🚫 不能外推 Verilog 生成能力；④ 分数为作者自报。 |
| 首次收录 | **2026-11-17**（第四十九轮） |
| 核验状态 | arXiv API `id_list` `200` + `atom`（26 作者、`published 2023-08-24T17:39:13Z`、`updated 2024-01-31`、`cs.CL`）；OpenAlex `200`（4,881、arXiv 源）；PDF `200` / 1,623,794 B（48 页，<5MB），`pdftotext` 核对 `500B tokens` / `1T tokens` / `16k tokens` / `100k tokens` / `67%` / `65%` / `34B model was trained without the infilling objective` |

---

## 193. Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution |
| 作者（前 3） | Peng Wang · Shuai Bai · Sinan Tan（共 **19** 位，末位 Junyang Lin；Qwen Team, Alibaba Group；arXiv API 逐字核） |
| 年份 | **2024**（v1 `2024-09-18`；v2 `2024-10-03`） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `comment` 只给代码链接 + 与 `2408.15262` 文本重叠的 admin note；OpenAlex `preprint` ⇒ 不记会议） |
| 被引数 | **6,157**（OpenAlex `10.48550/arxiv.2409.12191`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2409.12191> ｜ DOI `10.48550/arxiv.2409.12191`；代码 <https://github.com/QwenLM/Qwen2-VL> |
| 一句话贡献 | 用 **Naive Dynamic Resolution** 把任意分辨率图像映射成**可变数量**视觉 token（ViT 后用一层 MLP 把相邻 **2×2** token 压成 1 个），配 **M-RoPE**（把旋转位置编码拆成时间/高/宽三分量）统一图文视频位置编码；视觉侧 **675M** ViT + LLM，规模覆盖 **2B / 8B（正文 §3 亦写 7B）/ 72B**，作者自报 72B 在多模态基准上与 GPT-4o / Claude 3.5 Sonnet 可比。 |
| 与我们工作的关系 | **vision（视觉编码器的分辨率与 token 预算，主目标）**：动态分辨率 + 2×2 压缩是「不重训 ViT 也能改 token 数」的最小改动 ⇒ <b>动作</b>：视觉塔配置表新增 `dynamic_resolution(on/off)` / `token_merge_factor` / `tokens_per_image` 三列，任何图像任务先报 token 预算。<br>**vision（位置编码）**：M-RoPE 的三分量拆分对图文视频混合序列是结构性改动 ⇒ <b>动作</b>：位置编码消融增加 `rope_variant=1D|M-RoPE` 单变量对照，先小规模验证再上量。<br>**pretrain（多模态配比与缩放）**：论文把「模型规模 × 数据量」都当自变量 ⇒ <b>动作</b>：多模态预训练表按 `params` / `vision_tokens` / `text_tokens` 三轴记账，禁止只报参数量。<br>**harness（跨模态评测）**：72B 与 GPT-4o「可比」是作者自报、口径为各基准原始设置 ⇒ <b>动作</b>：跨模型对比必须同 prompt 模板、同解码参数、同判分脚本。<br>**风险**：① 6,157 为 OpenAlex 口径（含技术报告高引，🚫 不等于方法被独立复现次数）；② PDF **35,936,325 B &gt;5MB** ⇒ 仅存 `/tmp`，不入 git；③ 摘要写 8B、正文 §3 写 7B，**两处并存如实记录**，不擅自统一；④ 中文 / EDA 图（原理图、版图）未评测。 |
| 首次收录 | **2026-11-17**（第四十九轮） |
| 核验状态 | arXiv API `id_list` `200` + `atom`（19 作者、`published 2024-09-18T17:59:32Z`、`updated 2024-10-03`、`cs.CV`）；OpenAlex `200`（6,157、arXiv 源）；PDF `200` / **35,936,325 B**（52 页，>5MB 仅 `/tmp/r49pdf/`），`pdftotext` 核对 `Naive Dynamic Resolution` / `2 × 2 tokens` / `675M` / `M-RoPE` / `2B, 8B, and 72B` / 正文 `Qwen2-VL-7B` |

---

## 194. LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code

| 字段 | 内容 |
|:--|:--|
| 标题 | LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code |
| 作者（前 3） | Naman Jain · King Han · Fanjia Yan（共 **10** 位，末位 Ion Stoica；UC Berkeley / MIT / Cornell；arXiv API 逐字核） |
| 年份 | **2024**（v1 `2024-03-12`；v2 `2024-06-06`） |
| 会议 / 期刊 | **预印本**（arXiv `comment` 只有网站链接；OpenAlex `preprint` ⇒ 不记会议） |
| 被引数 | **1,802**（OpenAlex `10.48550/arxiv.2403.07974`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2403.07974> ｜ DOI `10.48550/arxiv.2403.07974`；网站 <https://livecodebench.github.io/> |
| 一句话贡献 | 从 LeetCode / AtCoder / CodeForces 的**周赛**持续收题并打**发布日期**标签，用「只评训练截止之后发布的题」构造免污染评测：初版 **500+ 题（2023-05 ~ 2024-05）**，覆盖**代码生成 / 自修复 / 代码执行 / 测试输出预测**四种场景，评了 **18 个基座 + 34 个指令微调**模型；论文给出可复核证据：DeepSeek-Instruct 与 GPT-4-O 在各自截止日之后的题上分数明显下降（作者据此判为潜在污染）。 |
| 与我们工作的关系 | **harness（去污染与时间切窗，主目标）**：把「发布日期」当评测一等字段 ⇒ <b>动作</b>：harness 题库 schema 增加 `release_date` / `model_cutoff` 两列，报告默认只算 `release_date > model_cutoff` 子集，并同时给全量与切窗两行。<br>**harness（多场景判分）**：自修复 / 执行 / 输出预测三类场景的排序与生成不一致 ⇒ <b>动作</b>：agent 评测报告按场景分列，🚫 只报生成总分。<br>**designflow（造题可验证性）**：用「周赛题 + 官方测试」保证可判分 ⇒ <b>动作</b>：designflow L3–L5 题面必须挂官方或自建可执行测试，抽 20 题做「题面→测试」人工对齐检查。<br>**zhulong（污染对成本口径的影响）**：污染会让旧题显得便宜好用 ⇒ <b>动作</b>：成本-效果曲线标注每点所用题集的发布时间窗。<br>**风险**：① 1,802 为 OpenAlex 口径；② 题库随时间增长 ⇒ 论文分数**不可与今日榜单直接比**；③ 「潜在污染」是作者基于分数下降的推断，🚫 不是逐样本证据；④ 仅代码竞赛题，未覆盖 EDA 脚本类任务。 |
| 首次收录 | **2026-11-17**（第四十九轮） |
| 核验状态 | arXiv API `id_list` `200` + `atom`（10 作者、`published 2024-03-12T17:58:04Z`、`updated 2024-06-06`、`cs.SE`）；OpenAlex `200`（1,802、arXiv 源）；PDF `200` / 4,960,954 B（46 页，<5MB），`pdftotext` 核对 `over five hundred coding problems` / `between May 2023 and May 2024` / `18 base LLMs and 34 instruction-tuned` / `potential contamination`；PDF 首页作者块给 `naman_jain@berkeley.edu` 等明文邮箱 |

---

## 195. Qwen2.5 Technical Report

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen2.5 Technical Report |
| 作者（前 3） | An Yang · Baosong Yang · Beichen Zhang（Qwen Team 集体署名，abs 页 `citation_author` 共 **44** 条含团队名；arXiv abs 页逐条核） |
| 年份 | **2024**（v1 `2024-12-19`；v2 `2025-01-03`） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `cs.CL`；OpenAlex `preprint` ⇒ 不记会议） |
| 被引数 | **11,888**（OpenAlex `10.48550/arxiv.2412.15115`，查询日 **2026-11-17**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2412.15115> ｜ DOI `10.48550/arxiv.2412.15115` |
| 一句话贡献 | 把预训练语料从 Qwen2 的 **7T 扩到 18T tokens**，用 **Qwen2-Instruct 模型做多维数据质量打分与过滤**；后训练数据 **100 万+ 样本**，上下文从 4,096 起经四阶段 **32,768 → 65,536 → 131,072 → 262,144** 扩展，旗舰 **Qwen2.5-72B-Instruct** 在论文自报表中对标同级开源与闭源模型。 |
| 与我们工作的关系 | **data（数据过滤，主目标）**：把「用小模型当质量过滤器」写成可执行管线 ⇒ <b>动作</b>：data 线在 2B 预训练前先跑一版「小模型打分 + 多维阈值」的离线过滤，与现有关键词/去重规则做 A/B，记录保留率与下游 loss。<br>**pretrain（上下文扩展课程）**：四阶段 32K→64K→128K→256K ⇒ <b>动作</b>：把长上下文训练拆成阶段式，每阶段固定 token 预算并单独记 validation loss，🚫 一次跳到目标长度。<br>**pretrain（后训练数据量）**：100 万+ SFT 样本 ⇒ <b>动作</b>：SFT 配比实验把「样本数」与「去重后唯一任务数」分列上报，避免只报条数。<br>**zhulong（长上下文成本）**：128K/8K 的输入输出上限直接影响单题成本 ⇒ <b>动作</b>：benchmark 成本表增加「输入长度桶」维度。<br>**风险**：① 11,888 为 OpenAlex 口径；② 数据管线细节（过滤器模型、阈值）论文未给全 ⇒ 不可复现为「同款过滤」；③ 对标分数为作者自报，未复现。 |
| 首次收录 | **2026-11-17**（第五十轮） |
| 核验状态 | arXiv abs 页 `200`（49,650 B；`cs.CL`；`citation_date 2024/12/19`）；PDF `200` / 1,938,604 B（`%PDF-`），`pdftotext` 核对 `from 7 trillion tokens to 18 trillion tokens` / `over 1 million samples` / `32,768 tokens, 65,536 tokens, 131,072 tokens, and ultimately 262,144` |

---

## 196. Gemma: Open Models Based on Gemini Research and Technology

| 字段 | 内容 |
|:--|:--|
| 标题 | Gemma: Open Models Based on Gemini Research and Technology |
| 作者（前 3） | Gemma Team · Thomas Mesnard · Cassidy Hardin（abs 页 `citation_author` **108** 条；团队署名） |
| 年份 | **2024**（v1 `2024-03-13`；多版更新至 2024-04） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `cs.CL`；OpenAlex `preprint`） |
| 被引数 | **3,803**（OpenAlex `10.48550/arxiv.2403.08295`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2403.08295> ｜ DOI `10.48550/arxiv.2403.08295` |
| 一句话贡献 | 2B / 7B 开源模型：**2B 用 3T tokens、7B 用 6T tokens** 预训练，上下文 **8,192**，词表沿用 Gemini 的 **256k** SentencePiece，7B 用多头注意力、2B 用 **MQA（`num_kv_heads=1`）**，激活改为近似 **GeGLU**；工程侧 7B 跨 **16 pods / 4,096 TPUv5e**，2B 用 **256-way 数据复制**；论文自报 7B IT 对 Mistral 7B v0.2 Instruct 的胜率 **61.2%**（安全集 **63.5%**）。 |
| 与我们工作的关系 | **pretrain（小模型配方，主目标）**：2B 用 MQA、7B 用 MHA 的**按规模分叉**是有数据支撑的选择 ⇒ <b>动作</b>：BaiZe 2B 消融把 `num_kv_heads` 与 `head_dim` 分开扫，报告显存/吞吐/下游三项，不只报 loss。<br>**pretrain（数据复制策略）**：2B 用 256-way replication ⇒ <b>动作</b>：小模型训练脚本显式记录 replication factor，并在 WSD 的 decay 阶段复测是否仍需要同样复制度。<br>**data（词表）**：256k 词表来自 Gemini ⇒ <b>动作</b>：比较 128k vs 256k 词表在中文/代码/EDA 文本上的 tokens/字符比，作为是否扩词表的判据。<br>**harness（胜率评测）**：61.2% / 63.5% 是成对胜率而非绝对分 ⇒ <b>动作</b>：内部对比报告同时给绝对分与成对胜率，并注明裁判模型。<br>**风险**：① 3,803 为 OpenAlex 口径；② 训练数据未公开 ⇒ 配比不可复现；③ 胜率为作者自报、裁判口径未完全公开。 |
| 首次收录 | **2026-11-17**（第五十轮） |
| 核验状态 | arXiv abs 页 `200`（59,441 B；`cs.CL`）；PDF `200` / 578,815 B（`%PDF-`），`pdftotext` 核对 `3T and 6T` / `8192` / `256k entries` / `4096 TPUv5e` / `256-way` / `61.2%` / `63.5%` |

---

## 197. Diffusion Policy: Visuomotor Policy Learning via Action Diffusion

| 字段 | 内容 |
|:--|:--|
| 标题 | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion |
| 作者（前 3） | Cheng Chi · Zhenjia Xu · Siyuan Feng（共 **8** 位，末位 Shuran Song；Columbia / Stanford / MIT / TRI；abs 页逐条核） |
| 年份 | **2023**（v1 `2023-03-07`；v2 `2024-03-14`，为 RSS 2023 论文的扩展期刊版） |
| 会议 / 期刊 | **RSS 2023**（DOI `10.15607/RSS.2023.XIX.026`；arXiv `comments` = "An extended journal version of the original RSS2023 paper"） |
| 被引数 | **2,313**（OpenAlex `10.15607/rss.2023.xix.026`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2303.04137> ｜ DOI `10.15607/RSS.2023.XIX.026` |
| 一句话贡献 | 把机器人策略学习写成**动作序列的条件去噪（DDPM）**：以观测为条件预测 `Tp` 步动作、只执行前 `Ta` 步（receding horizon），并给出 CNN（1D temporal conv + FiLM）与 Transformer 两种主干；在 **15 个任务 / 4 个基准**上平均成功率提升 **46.9%**，消融指出观测视野 **To=2**、执行视野 **Ta=8** 是多数任务的好默认值。 |
| 与我们工作的关系 | **zhulong（动作/输出 chunk，主目标）**：一次预测多步、按步回放 ⇒ <b>动作</b>：多轮 agent 的动作接口改为「预测 k 步、执行 m 步（m<k）」并在成本表记录 m/k，对比单步贪心。<br>**vision（主干选型）**：CNN 1D temporal + FiLM 在多数任务够用、Transformer 更适合高频/多模态 ⇒ <b>动作</b>：视觉塔下游接策略头时先跑 CNN 版基线，再决定是否上 Transformer。<br>**harness（多基准一致性）**：15 任务 4 基准的排序一致性 ⇒ <b>动作</b>：内部评测不用单基准定优劣，至少两基准交叉。<br>**data（低资源门槛）**：示教量对 receding horizon 收益的影响 ⇒ <b>动作</b>：数据线做 20/50/100 条示教的缩放曲线，找退化点。<br>**风险**：① 2,313 为 OpenAlex 口径（DOI 指向 RSS 版）；② 46.9% 为作者自报、跨 4 个基准的平均，🚫 不可当单任务增益；③ 机器人控制结论迁移到 LLM agent 需重新验证。 |
| 首次收录 | **2026-11-17**（第五十轮） |
| 核验状态 | arXiv abs 页 `200`（43,764 B；`cs.RO`；`citation_date 2023/03/07`）；PDF `200` / 6,192,199 B（`%PDF-`，>5 MB ⇒ 仅 `/tmp`，不入 git），`pdftotext` 核对 `15 different tasks from 4` / `average improvement of 46.9%` / `horizon of 8 steps` / `observation horizon of 2` / `1D temporal` / `FiLM` |

---

## 198. Open X-Embodiment: Robotic Learning Datasets and RT-X Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Open X-Embodiment: Robotic Learning Datasets and RT-X Models |
| 作者（前 3） | Embodiment Collaboration · Abby O'Neill · Abdul Rehman（abs 页 `citation_author` **294** 条，跨 21 家机构） |
| 年份 | **2023**（v1 `2023-10-13`；后续多版更新） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `cs.RO`；OpenAlex `preprint` ⇒ 不记会议） |
| 被引数 | **1,045**（OpenAlex `10.48550/arxiv.2310.08864`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2310.08864> ｜ DOI `10.48550/arxiv.2310.08864`（项目页见 arXiv `comments`） |
| 一句话贡献 | 汇总 **60 个数据集 / 22 种机器人本体 / 21 家机构**的 **1M+ 真实轨迹**，用 **527 个技能（160,266 个任务）**描述覆盖；训练 **RT-1-X**（机器人专用架构）与 **RT-2-X（55B）**（VLM 策略），论文自报 RT-1-X 平均成功率比各域原方法 **高 50%**、RT-2-X 在新技能上约有 **3× 泛化**；同时报告**高数据域上的负迁移**（RT-1-X 反而不如域内原方法）。 |
| 与我们工作的关系 | **data（跨源混配，主目标）**：22 本体 60 数据集并表的加权与负迁移 ⇒ <b>动作</b>：data 线配比表增加「按来源轨迹数加权 vs 等权」两列，并对最大来源做下采样消融，显式报告负迁移域。<br>**zhulong（跨工具迁移）**：把「换本体」类比「换 EDA 工具」 ⇒ <b>动作</b>：zhulong 设计跨工具（DC/PT/仿真）迁移实验，先测共享动作空间、再测共享观测格式。<br>**designflow（技能分类法）**：527 skills / 160,266 tasks 的标签体系 ⇒ <b>动作</b>：designflow 题面元数据加 `skill` / `task` 两级标签，抽 30 题做跨标注一致性检查。<br>**vision（VLM 策略）**：RT-2-X 55B 说明 VLM 主干 + 动作 token 化可用 ⇒ <b>动作</b>：vision 线评估把动作离散成 token 的接口成本。<br>**风险**：① 1,045 为 OpenAlex 口径；② 数据许可与本体差异大 ⇒ 不可直接照搬配比；③ 「3× 泛化」「50%」均为作者自报、定义见原文表格。 |
| 首次收录 | **2026-11-17**（第五十轮） |
| 核验状态 | arXiv abs 页 `200`（91,646 B；`cs.RO`；`citation_date 2023/10/13`）；PDF `200` / 4,011,306 B（`%PDF-`），`pdftotext` 核对 `60 individual datasets across 22 embodiments` / `22 robot embodiments` / `1M+ robot trajectories` / `527 skills` / `160266 tasks` / `RT-2-X (55B)` / `50% higher` / `3× generalization` |

---

## 199. InternVL: Scaling up Vision Foundation Models and Aligning for Generic Visual-Linguistic Tasks

| 字段 | 内容 |
|:--|:--|
| 标题 | InternVL: Scaling up Vision Foundation Models and Aligning for Generic Visual-Linguistic Tasks |
| 作者（前 3） | Zhe Chen（陈喆）· Jiannan Wu · Wenhai Wang（王文海）等 **15** 位（末位 **Jifeng Dai 代季峰**；abs 页 `citation_author` 15 条逐条核） |
| 年份 | **2024**（v1 `2023-12-18`；CVPR 2024 版） |
| 会议 / 期刊 | **CVPR 2024**（OpenAlex `conference-paper`，会场 DOI `10.1109/cvpr52733.2024.02283`） |
| 被引数 | **3,950**（OpenAlex `10.48550/arxiv.2312.14238`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2312.14238> ｜ arXiv DOI `10.48550/arxiv.2312.14238` |
| 一句话贡献 | 把**视觉塔单独放大到 6B（InternViT-6B）**，再以「对比 + 生成」两阶段目标与 LLM（QLLaMA，8B 级）**渐进对齐**，并用 **pixel shuffle（像素重排）** 换动态分辨率与 token 预算；论文自报在 **32 个**通用视觉-语言基准上取得 SOTA（摘要原话）。 |
| 与我们工作的关系 | **vision（视觉塔容量/分辨率，主目标）**：给出「小塔 → 6B 塔」的完整对照与像素重排实现 ⇒ <b>动作</b>：视觉塔配置表增设 `vision_params` / `pixels_per_token` / `dynamic_resolution` 三列，先做 300M 与 6B 两档的单变量对照。<br>**pretrain（视觉侧目标）**：对比 + 生成两阶段 ⇒ <b>动作</b>：视觉侧预训练消融把「纯对比」与「对比 + 生成」分开记账，各记下游线性探针分。<br>**data（图文对）**：web-scale 多源图文对 ⇒ <b>动作</b>：图文对配比表按来源分列并记去重前后条数。<br>**zhulong（读图入口）**：版图截图 / 波形 / 器件表格属小字密集输入 ⇒ <b>动作</b>：把「小字密集图」单独建 200 题子集，作为视觉塔选型的判据集。<br>**风险**：① 3,950 为 OpenAlex 口径；② 「32 基准 SOTA」为作者自报、定义见原文表格；③ 6B 视觉塔的显存/吞吐代价未在本条量化 ⇒ 选型前须自测。 |
| 首次收录 | **2026-11-17**（第五十一轮） |
| 核验状态 | arXiv abs 页 `200`（43,416 B；`citation_date 2023/12/18`；`citation_author` 15 条）；PDF `200` / 1,315,333 B（`%PDF-`），`pdftotext` 核对 `6 billion parameters` / `6B` / `QLLaMA`（54 处）/ `4096`；`32` 基准表述取自 abs 页摘要原文 |

---

## 200. Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone

| 字段 | 内容 |
|:--|:--|
| 标题 | Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone |
| 作者（前 3） | Marah Abdin · Jyoti Aneja · Hany Awadalla 等（Microsoft 团队署名，作者数众多；abs 页 `citation_author` 逐条可核） |
| 年份 | **2024**（v1 `2024-04-22`） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `preprint` ⇒ 不记会议） |
| 被引数 | **3,285**（OpenAlex `10.48550/arxiv.2404.14219`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2404.14219> ｜ arXiv DOI `10.48550/arxiv.2404.14219` |
| 一句话贡献 | `phi-3-mini`：**3.8B 参数、3.3T token** 训练，摘要自报 **MMLU 69% / MT-bench 8.38**，可与 Mixtral 8x7B、GPT-3.5 相比且能跑在手机上；数据为「重过滤公开网页 + 合成数据」的 phi-2 配方放大版；同族 7B / 14B（`phi-3-small` / `phi-3-medium`）训 **4.8T token**，MMLU **75% / 78%**、MT-bench **8.7 / 8.9**；并给出 **128K 上下文**变体。 |
| 与我们工作的关系 | **pretrain（小模型数据配方，主目标）**：同架构下「token 数 × 数据质量」的对照最完整 ⇒ <b>动作</b>：2B 配方把「重过滤网页」与「合成数据」拆两列，各记 token 与 val loss 曲线。<br>**data（合成数据占比）**：3.8B 用 3.3T token（约 **868 token/参数**）⇒ <b>动作</b>：配比表加 `tokens_per_param` 列，并对合成占比做 10% / 30% 两档消融。<br>**harness（小模型口径）**：MMLU / MT-bench 双口径 ⇒ <b>动作</b>：内部报告对 <5B 模型同时给知识型与对话型分数，不只报聚合。<br>**zhulong（端侧/低成本基线）**：手机可部署 ⇒ <b>动作</b>：成本表增设「端侧可跑」标记列。<br>**风险**：① 3,285 为 OpenAlex 口径；② 数据配方只给类别、不给比例；③ 分数为作者自报且 MT-bench 用 GPT-4 判分，跨报告不可直接比。 |
| 首次收录 | **2026-11-17**（第五十一轮） |
| 核验状态 | arXiv abs 页 `200`（65,710 B；`citation_date 2024/04/22`）；PDF `200` / 3,908,493 B（`%PDF-`），`pdftotext` 核对 `3.8 billion parameter` / `3.3 trillion tokens` / `69% on MMLU` / `8.38 on MT-bench` / `4.8T tokens` / `75%, 78%` / `128K` |

---

## 201. The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale

| 字段 | 内容 |
|:--|:--|
| 标题 | The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale |
| 作者（前 3） | Guilherme Penedo · Hynek Kydlíček · Loubna Ben Allal 等（末位 Leandro von Werra；abs 页 `citation_author` 逐条可核） |
| 年份 | **2024**（v1 `2024-06-26`） |
| 会议 / 期刊 | **NeurIPS 2024 Datasets & Benchmarks**（OpenAlex `conference-paper`，会场 DOI `10.52202/079017-0970`，`source` = `neural information processing systems`） |
| 被引数 | **1,799**（OpenAlex `10.48550/arxiv.2406.17557`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2406.17557> ｜ arXiv DOI `10.48550/arxiv.2406.17557` |
| 一句话贡献 | 从 **96 个 Common Crawl 快照**抽出 **15 万亿 token** 的开放预训练语料，并把**去重（MinHash）与过滤**的每个设计选择逐项消融、公开记录；另给 **FineWeb-Edu（1.3T token）**——用分类器筛出的「教育性」子集，摘要自报下游显著更好。 |
| 与我们工作的关系 | **data（网页语料清洗，主目标）**：少见的「把消融做全」的开放语料报告 ⇒ <b>动作</b>：清洗流水线按 `extraction` / `language_id` / `minhash_dedup` / `filter_model` 四段分别开关，逐段记 `kept_tokens` 与 1B 小模型 val loss。<br>**pretrain（数据量 vs 质量）**：15T 全量 vs 1.3T 教育子集 ⇒ <b>动作</b>：预训练配方做「同算力下 质量×数量」二选一预注册实验。<br>**harness（数据侧评测）**：以固定小模型 + 固定评测集作数据质量判据 ⇒ <b>动作</b>：data 线建立「1B / 8k step 探针」作为配比变更的快速判据。<br>**zhulong（语料成本）**：96 快照的处理成本可折算 ⇒ <b>动作</b>：成本表加「每 T token 清洗 GPU 时」列。<br>**风险**：① 1,799 为 OpenAlex 口径；② 「显著更好」为作者自报，具体增益见原文表格；③ FineWeb 只覆盖英文网页，不可直接外推到中文/代码语料。 |
| 首次收录 | **2026-11-17**（第五十一轮） |
| 核验状态 | arXiv abs 页 `200`（42,466 B；`citation_date 2024/06/26`）；PDF `200` / 3,137,041 B（`%PDF-`），`pdftotext` 核对 `15-trillion token` / `96 Common Crawl snapshots` / `1.3-trillion token` / `MinHash`（18 处） |

---

## 202. OLMo: Accelerating the Science of Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | OLMo: Accelerating the Science of Language Models |
| 作者（前 3） | Dirk Groeneveld · Iz Beltagy · Pete Walsh 等（Ai2 团队署名；abs 页 `citation_author` 逐条可核） |
| 年份 | **2024**（v1 `2024-02-01`） |
| 会议 / 期刊 | **ACL 2024**（OpenAlex `conference-paper`，会场 DOI `10.18653/v1/2024.acl-long.841`） |
| 被引数 | **908**（OpenAlex `10.48550/arxiv.2402.00838`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2402.00838> ｜ arXiv DOI `10.48550/arxiv.2402.00838` |
| 一句话贡献 | 把「真正开放」定义为**权重 + 训练数据（Dolma）+ 训练/评测代码 + 日志**四件套齐发；给出 **OLMo-1B / OLMo-7B** 的完整训练配方，7B 在 Dolma 上训到 **2.46T token** 并公开中间 checkpoint，使「训练过程」本身可被研究。 |
| 与我们工作的关系 | **pretrain（可复现配方，主目标）**：2.46T token 的训练日志与 checkpoint 序列 ⇒ <b>动作</b>：2B 预训练对照 OLMo 的 `global batch` / `seq len 4096` 级配置逐项记账，并把中间 checkpoint 留存策略写进任务书。<br>**data（Dolma 治理）**：数据与代码同源发布 ⇒ <b>动作</b>：配比表每条注明「可公开复现 / 仅内部」，防止结论依赖不可公开数据。<br>**harness（可复现评测）**：评测框架一并开源 ⇒ <b>动作</b>：内部评测脚本对齐其任务清单，差集单列。<br>**zhulong（实验可审计）**：日志全开 ⇒ <b>动作</b>：消融实验预注册表增加「日志与 checkpoint 保留」栏。<br>**风险**：① 908 为 OpenAlex 口径；② 7B 规模结论不能直接外推到 2B / 更大规模；③ 「开放」不等于「许可宽松」，商用前须逐项核数据许可。 |
| 首次收录 | **2026-11-17**（第五十一轮） |
| 核验状态 | arXiv abs 页 `200`（47,839 B；`citation_date 2024/02/01`）；PDF `200` / 562,224 B（`%PDF-`），`pdftotext` 核对 `OLMo-7B` / `OLMo-1B` / `2.46T tokens on the Dolma` / `11,008`（7B 词表对齐值）/ `Dolma` |

---

## 203. GPQA: A Graduate-Level Google-Proof Q&A Benchmark

| 字段 | 内容 |
|:--|:--|
| 标题 | GPQA: A Graduate-Level Google-Proof Q&A Benchmark |
| 作者（前 3） | David Rein · Betty Li Hou · Asa Cooper Stickland 等 **8** 位（abs 页 `citation_author` 8 条逐条核） |
| 年份 | **2023**（v1 `2023-11-20`；无 v2） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint` ⇒ 不记会议） |
| 被引数 | **2,204**（OpenAlex `10.48550/arxiv.2311.12022`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2311.12022> ｜ arXiv DOI `10.48550/arxiv.2311.12022` |
| 一句话贡献 | 造 **448** 道研究生级问答（物理 / 化学 / 生物），其中 **198** 道为 diamond 子集；出题后用「专家验证 + 非专家对照」筛掉可被检索解决的题：领域专家正确率 **65%**（剔除明显错误后 **74%**），非专家在可查资料、平均 **>30 分钟**下仅 **34%**，专家间一致率 **74%**。 |
| 与我们工作的关系 | **harness（抗检索 / 抗污染的难题口径，主目标）**：题目按「能不能被检索解决」反向筛选 ⇒ <b>动作</b>：内部评测集增设 `retrieval_solvable` 标注列，先报「开卷可解」比例，再报分。<br>**data（题目生产流水线）**：「写题 → 专家验证 → 非专家对照」三道筛 ⇒ <b>动作</b>：造题流程照抄三筛并记每筛淘汰率。<br>**zhulong（thinking 轴上限探针）**：单题人类中位耗时 30 分钟 ⇒ <b>动作</b>：只用 198 道 diamond 做上限探针，不进高吞吐回归集。<br>**风险**：① 2,204 为 OpenAlex 口径；② 448 题量小 ⇒ 单次评测方差大，跨模型比较须给置信区间；③ 65% / 34% 为论文自报的人类被试研究，不可外推到任意人群。 |
| 首次收录 | **2026-11-17**（第五十二轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；PDF `200` / 617,128 B（`%PDF-`），`pdftotext` 核到 `448`（7 处）/ `198`（4 处）/ `65%`（2 处）/ `34%`（3 处）/ `74%`（4 处）/ `median 30 minutes` |

---

## 204. MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI

| 字段 | 内容 |
|:--|:--|
| 标题 | MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI |
| 作者（前 3） | Xiang Yue · Yuansheng Ni · Kai Zhang 等 **22** 位（**通讯 Wenhu Chen**；abs 页 `citation_author` 逐条核） |
| 年份 | **2024**（v1 `2023-11-27`；CVPR 2024 版） |
| 会议 / 期刊 | **CVPR 2024 Oral**（arXiv `comment` 原文 `CVPR 2024 Oral`；OpenAlex `type=conference-paper`，**未核到会场 DOI ⇒ 不写 DOI**） |
| 被引数 | **2,994**（OpenAlex `10.48550/arxiv.2311.16502`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2311.16502> ｜ arXiv DOI `10.48550/arxiv.2311.16502` |
| 一句话贡献 | 建 **11.5K** 道大学水平多模态题，覆盖 **6** 大学科 / **30** 科目 / **183** 子领域、**30** 种异质图像（图表、示意图、地图、表格…），来源含 **30** 所大学；划分 **dev:val:test = 150:900:10500**；评测 28 个开源 LMM 与 GPT-4V / Gemini，最佳人类专家 val **88.6%**、GPT-4V **56.8%**。 |
| 与我们工作的关系 | **harness（多模态判分口径，主目标）**：长回答用正则 + response-processing 抽答案，抽不到时**选择题随机选、开放题判错** ⇒ <b>动作</b>：内部判分器把「无效应答」单列计数并报比例，再决定 strict / lenient 两套口径是否并存。<br>**vision（图表 / 示意图读图，主目标）**：30 种图像类型里 charts / diagrams / tables 最难 ⇒ <b>动作</b>：视觉塔选型用「图表类子集」单列报分并记输入分辨率。<br>**zhulong（读图入口）**：EDA 波形 / 版图 / 器件表格与图表类同源 ⇒ <b>动作</b>：新增中文 + EDA 子集时按图像类型分层抽样，避免只抽文本型题。<br>**风险**：① 2,994 为 OpenAlex 口径；② 30 科目题量不均，单科 1–2 pt 差异不宜下结论；③ val 仅 ≈900 题而 prompt 选型在 val 上做 ⇒ 存在选型过拟合风险（本线已去信通讯作者求证 val / test 排名一致性）。 |
| 首次收录 | **2026-11-17**（第五十二轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；PDF `200` / 16,874,947 B（`%PDF-`，>5 MB ⇒ 仅存 `/tmp`、不入 git），`pdftotext` 核到 `11.5K`（7 处）/ `30 subjects`（5 处）/ `183`（6 处）/ `150:900:10500` / `88.6`（3 处）/ `56.8`（5 处）/ `response-processing` |

---

## 205. LAION-5B: An open large-scale dataset for training next generation image-text models

| 字段 | 内容 |
|:--|:--|
| 标题 | LAION-5B: An open large-scale dataset for training next generation image-text models |
| 作者（前 3） | Christoph Schuhmann · Romain Beaumont · Richard Vencu 等 **16** 位（abs 页 `citation_author` 逐条核） |
| 年份 | **2022**（v1 `2022-10-16`） |
| 会议 / 期刊 | **NeurIPS 2022 Datasets & Benchmarks Track**（arXiv `comment` + OpenReview `M3Y74vmsMcY`；OpenAlex `type=preprint` ⇒ **不写会场 DOI**，两口径并列不混算） |
| 被引数 | **1,963**（OpenAlex `10.48550/arxiv.2210.08402`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2210.08402> ｜ arXiv DOI `10.48550/arxiv.2210.08402` |
| 一句话贡献 | 发布 **5.85B** 条 **CLIP 过滤后**的图文对（其中 **2.32B** 英文、**2.26B** 多语种、**1.27B** 不特定语种），给出「网页抓取 → CLIP 相似度阈值过滤 → 近似去重」的可复现流水线与 **400M** 子集对照；论文自报仅用该数据训练的 open CLIP 复现已接近 OpenAI CLIP 水平。 |
| 与我们工作的关系 | **data（图文对规模与过滤阈值，主目标）**：阈值越高 precision 越高、recall 越低，且总量按语种切分记账 ⇒ <b>动作</b>：图文对配比表加 `clip_score_threshold` / `lang_bucket` / `kept_after_dedup` 三列，阈值做单变量消融。<br>**vision（数据与视觉塔耦合）**：过滤本身由视觉模型完成 ⇒ <b>动作</b>：换视觉塔时同步重算同阈值下的留存率，避免「换塔即换数据」被忽略。<br>**pretrain（多语种配比）**：英文 2.32B vs 多语 2.26B ⇒ <b>动作</b>：多语种占比做 10% / 30% 两档，单列中文评测。<br>**风险**：① 1,963 为 OpenAlex 口径；② 5.85B 是「过滤后」计数，不等于高质量对数量；③ 数据源含版权与 NSFW 争议，论文自报做过过滤但不构成合规保证。 |
| 首次收录 | **2026-11-17**（第五十二轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；PDF `200` / 17,686,858 B（`%PDF-`，>5 MB ⇒ 仅存 `/tmp`、不入 git），`pdftotext` 核到 `5.85 billion` / `2.32 billion` / `2.26 billion` / `1.27 billion` / `400M`（72 处）/ `CLIP-filtered` |

---

## 206. Measuring Mathematical Problem Solving With the MATH Dataset

| 字段 | 内容 |
|:--|:--|
| 标题 | Measuring Mathematical Problem Solving With the MATH Dataset |
| 作者（前 3） | Dan Hendrycks · Collin Burns · Saurav Kadavath 等 **8** 位（末位 Jacob Steinhardt；abs 页 `citation_author` 逐条核） |
| 年份 | **2021**（v1 `2021-03-05`；v2 `2021-11-08`） |
| 会议 / 期刊 | **NeurIPS 2021**（arXiv `comment` 原文 `NeurIPS 2021`；OpenAlex `type=preprint` ⇒ 不写会场 DOI） |
| 被引数 | **7,734**（OpenAlex `10.48550/arxiv.2103.03874`，查询日 **2026-11-17**） |
| arXiv / DOI | <https://arxiv.org/abs/2103.03874> ｜ arXiv DOI `10.48550/arxiv.2103.03874` |
| 一句话贡献 | 建 **12,500** 道竞赛级数学题（**7,500** 训练 / **5,000** 测试），每题带逐步解答，按 **7** 个科目与难度 **1–5** 双层标注；另发布辅助预训练语料 **AMPS**（Khan Academy + Mathematica，>100,000 题 / 23 GB）；基线极低：GPT-2 0.1B 仅 **5.4%**，参数放大 15× 后 **6.9%**。 |
| 与我们工作的关系 | **harness（答案抽取与等价判定，主目标）**：分数高度依赖「抽答案 + 判等」实现 ⇒ <b>动作</b>：判分器把 `extract` 与 `compare` 分开单测并报「抽取失败率」，换判分器必须重跑历史结果。<br>**data（辅助语料）**：AMPS 说明「辅助预训练语料」能抬主任务分 ⇒ <b>动作</b>：EDA 题库 / 文档按同思路做一份辅助预训练集，与主数据分开记账。<br>**zhulong（thinking 轴难度分层）**：难度 1–5 与科目双维标注 ⇒ <b>动作</b>：thinking 预算实验按 level 分层报分，避免平均分掩盖 level 4–5 的退化。<br>**风险**：① 7,734 为 OpenAlex 口径；② 题目 / 答案的标注质量本线**未复核**，不据此判断噪声比例；③ 基线来自 GPT-2 时代，不代表当代模型水平。 |
| 首次收录 | **2026-11-17**（第五十二轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；PDF `200` / 2,030,715 B（`%PDF-`），`pdftotext` 核到 `12,500`（2 处）/ `7,500` / `5,000` / `5.4%`（2 处）/ 难度 `1 to 5` / `AMPS` / `23GB` |

---

## 207. DataComp-LM: In search of the next generation of training sets for language models

| 字段 | 内容 |
|:--|:--|
| 标题 | DataComp-LM: In search of the next generation of training sets for language models |
| 作者（前 3） | Jeffrey Li · Alex Fang · Georgios Smyrnis 等（作家长名单，末位 Ludwig Schmidt；abs 页 `citation_author` 逐条核） |
| 年份 | **2024**（v1 `2024-06-17`；最新 v4 `2025-04-21`） |
| 会议 / 期刊 | **NeurIPS 2024（Datasets & Benchmarks）**（OpenAlex `primary_location.source` = `neural information processing systems`；arXiv `comment` 仅给项目页） |
| 被引数 | **627**（OpenAlex `10.48550/arxiv.2406.11794`，查询日 **2026-11-18**） |
| arXiv / DOI | <https://arxiv.org/abs/2406.11794> ｜ arXiv DOI `10.48550/arxiv.2406.11794` |
| 一句话贡献 | 建 **240T token** 的标准化网页语料（来自 Common Crawl）与 **53** 项下游评测的 DCLM 基准：参与者在 412M–7B 模型规模上做数据配比与清洗方法对比；基线 `DCLM-BASELINE` 从零训练 7B 模型达到 64% 的 5-shot MMLU，比 Llama 2 7B 少 **40%** 计算，并在 53 项任务上与 Mistral-7B-v0.3 相当、训练计算少 **6.6×**。 |
| 与我们工作的关系 | **data（主目标：网页语料质量过滤与混合比例的基线）**：把「分类器质量过滤 + 领域重采样比例」做成可复算的对照实验 ⇒ <b>动作</b>：在自有中英数据上复现「fastText 质量分类器 + 比例搜索」两段，报告固定 token 预算下的等价评测子集分数，作为后续任何数据配方的分母。<br>**pretrain（辅助）**：412M–7B 的多规模扫描说明数据结论要按模型规模复核 ⇒ <b>动作</b>：数据消融至少在 2 个规模上各跑一遍，禁止只在最大模型上做单点结论。<br>**风险**：① 627 为 OpenAlex 口径；② 240T token 语料本身含许可与合规问题，本线不下载原始语料；③ 64% MMLU 为作者自报，未复现。 |
| 首次收录 | **2026-11-18**（第五十三轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`；PDF `200` / 1,656,647 B（`%PDF-`），`pdftotext` 核到 `240T tokens` / `53 downstream evaluations` / `412M to 7B` / `64%` / `40% less compute` / `6.6×` |

---

## 208. Decoupled Weight Decay Regularization

| 字段 | 内容 |
|:--|:--|
| 标题 | Decoupled Weight Decay Regularization |
| 作者（前 3） | Ilya Loshchilov · Frank Hutter（2 位，无 et al） |
| 年份 | **2017**（v1 `2017-11-14`；最新 v3 `2019-01-04`） |
| 会议 / 期刊 | **ICLR 2019**（arXiv `comment` 原文 `Published as a conference paper at ICLR 2019`） |
| 被引数 | **34,224**（OpenAlex `10.48550/arxiv.1711.05101`，查询日 **2026-11-18**） |
| arXiv / DOI | <https://arxiv.org/abs/1711.05101> ｜ arXiv DOI `10.48550/arxiv.1711.05101` |
| 一句话贡献 | 证明 L2 正则与 weight decay 仅在 SGD + 固定学习率重参数化下等价；在 Adam 里二者**不等价**，L2 会经由自适应分母产生「历史梯度大的权重反而衰减不足」的偏差；提出把 decay 从梯度更新里解耦出来的 **AdamW**，并给出解耦后最优 λ 与学习率的联动规律。 |
| 与我们工作的关系 | **pretrain（主目标：weight decay 与优化器耦合）**：本线已收的 Muon 临时 weight decay（`2611.17876`）讨论的正是「λ 何时撤除」，其理论起点即本文的解耦项 ⇒ <b>动作</b>：所有优化器对照实验必须显式声明「decay 是加在梯度里还是加在参数上」，并把 λ 与学习率的联动写成预注册的超参网格，禁止只报单点 λ。<br>**zhulong（辅助）**：thinking/语言轴的消融若换优化器，需固定「是否解耦」这一因子，否则不同臂之间不可比。<br>**风险**：① 34,224 为 OpenAlex 口径（含引用本文的工程博客/代码库可能不计入）；② 本文结论针对 Adam 家族，Muon 等新优化器需重新推导，不可直接照搬。 |
| 首次收录 | **2026-11-18**（第五十三轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`；PDF `200` / 6,063,896 B（`%PDF-`，>5 MB ⇒ 仅存 `/tmp`、不入 git），`pdftotext` 核到 `L2 regularization and weight decay regularization are equivalent for standard` / `ICLR 2019` |

---

## 209. Prismatic VLMs: Investigating the Design Space of Visually-Conditioned Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Prismatic VLMs: Investigating the Design Space of Visually-Conditioned Language Models |
| 作者（前 3） | Siddharth Karamcheti · Suraj Nair · Ashwin Balakrishna 等 **6** 位（含 Percy Liang / Thomas Kollar / Dorsa Sadigh；abs 页逐条核） |
| 年份 | **2024**（v1 `2024-02-12`；最新 v2 `2024-05-30`） |
| 会议 / 期刊 | **ICML 2024**（arXiv `comment` 原文 `Published at ICML 2024`） |
| 被引数 | **325**（OpenAlex `10.48550/arxiv.2402.07865`，查询日 **2026-11-18**）⚠️ **<500，按「方法论常青」收**（视觉条件语言模型设计空间消融的标准对照） |
| arXiv / DOI | <https://arxiv.org/abs/2402.07865> ｜ arXiv DOI `10.48550/arxiv.2402.07865` |
| 一句话贡献 | 在**固定数据与评测**的前提下系统扫视觉条件语言模型的设计空间：视觉主干（CLIP vs SigLIP）、是否微调视觉塔、单阶段 vs 多阶段训练、以及训练任务配比；结论是「视觉主干与分辨率」的影响大于多数架构改动，且**只调视觉塔的学习率/微调策略**即可显著改变下游分数；同时开源训练与评测代码（TRI-ML）。 |
| 与我们工作的关系 | **vision（主目标：视觉塔与训练阶段的因子化对照）**：给出一套「固定其余变量、只改一个设计维度」的消融模板 ⇒ <b>动作</b>：在自有 2B 级 VLM 上先复制「视觉主干 × 是否解冻 × 单/多阶段」三维对照，评测集固定，报告每维的边际增益；若某维增益 <1 个点即从后续实验中剔除，避免维度爆炸。<br>**harness（辅助）**：其开源评测管线强调「同一 prompt 模板 + 统一答案抽取」⇒ <b>动作</b>：VLM 评测脚本把 prompt 模板与抽取器版本号写入结果文件。<br>**风险**：① 325 被引未达 500，收录依据是「方法论常青」而非高引，引用时须注明；② 结论基于 7B 级模型与 2024 年数据，2B 级是否同样成立**未经本文验证**。 |
| 首次收录 | **2026-11-18**（第五十三轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`；PDF `200` / 9,717,222 B（`%PDF-`，>5 MB ⇒ 仅存 `/tmp`、不入 git），`pdftotext` 核到 `Published at ICML 2024` / `skaramcheti@cs.stanford.edu` |

---

## 210. VeriGen: A Large Language Model for Verilog Code Generation

| 字段 | 内容 |
|:--|:--|
| 标题 | VeriGen: A Large Language Model for Verilog Code Generation |
| 作者（前 3） | Shailja Thakur · Baleegh Ahmad · Hammond Pearce 等 **7** 位（含 Benjamin Tan / Brendan Dolan-Gavitt / Ramesh Karri / Siddharth Garg） |
| 年份 | **2023**（v1 `2023-07-28`） |
| 会议 / 期刊 | **ACM TODAES**（PDF 首页 ACM Reference Format 原文 `ACM Trans. Des. Autom. Electron. Syst. 37, 4, Article 111`；DOI 在 PDF 里是占位 `XXXXXXX` ⇒ 🚫 不写 DOI）；前身发表于 **DATE 2023**（PDF 脚注原文） |
| 被引数 | **533**（OpenAlex `10.48550/arxiv.2308.00708`，查询日 **2026-11-18**）⚠️ 00:00 轮实测 531，本轮复测 533（同一来源、不同时点，正常漂移） |
| arXiv / DOI | <https://arxiv.org/abs/2308.00708> ｜ arXiv DOI `10.48550/arxiv.2308.00708` |
| 一句话贡献 | 用 **GitHub 抓取的 Verilog 语料 + 教科书习题**微调开源 CodeGen（2B/6B/16B），并自建 **problem set + 测试台（test bench）** 以**功能正确性**（而非文本相似度）判分；据摘要，微调后的 CodeGen-16B 在自建题集上**整体超过 GPT-3.5-turbo 1.1%**，相对其预训练版本**语法正确率提升 41%**，并开源训练/评测脚本与 checkpoint。 |
| 与我们工作的关系 | **zhulong（主目标：Verilog 生成的判分口径）**：本文最可复用的是「**仿真验证式判分**」而不是模型本身 —— 每条题必须带 test bench，通过 = 仿真输出与期望一致 ⇒ <b>动作</b>：zhulong 的 Verilog 评测统一改为「编译通过 → 仿真通过 → 波形/断言一致」三级闸门，并单独统计各级失败率；🚫 不用「与参考代码的编辑距离」当主指标。<br>**designflow（造题结构）**：`(自然语言描述, 参考 RTL, test bench)` 三件套 + 难度分层（教科书题 / 真实 IP 片段）可直接对齐 designflow 的 L1–L5 保真度骨架 ⇒ <b>动作</b>：造题时强制要求 test bench 由出题人独立编写，避免「参考实现与测试同源」导致题目过易。<br>**data（辅助）**：GitHub Verilog 语料的许可过滤问题本文未系统处理 ⇒ 与 The Stack `2211.15533` 的许可清单合并使用。<br>**风险**：① 2023 年模型（CodeGen-16B）与 GPT-3.5-turbo 的对比已过时，🚫 不可外推为「当前 SOTA」；② 41% 是「语法正确率」而非功能正确率；③ 题集规模与难度分布需读正文核对后再引用具体题数。 |
| 首次收录 | **2026-11-18**（第五十四轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（533）；PDF `200` / 2,636,063 B（`%PDF-`，<5 MB），`pdftotext` 核到 `1.1% overall increase` / `41% improvement` / `st4920@nyu.edu` |

---

## 211. WebShop: Towards Scalable Real-World Web Interaction with Grounded Language Agents

| 字段 | 内容 |
|:--|:--|
| 标题 | WebShop: Towards Scalable Real-World Web Interaction with Grounded Language Agents |
| 作者（前 3） | Shunyu Yao · Howard Chen · John Yang（et al.，共 **4** 位，含 Karthik Narasimhan；Princeton NLP） |
| 年份 | **2022**（v1 `2022-07-04`；最新 v4 `2023-02-08`） |
| 会议 / 期刊 | **NeurIPS 2023**（arXiv `comment` 原文 `v3 is NeurIPS camera ready version`） |
| 被引数 | **1,765**（OpenAlex `10.48550/arxiv.2207.01206`，查询日 **2026-11-18**；⚠️ 早前候选池写的 358 为误记，本轮实测以 1,765 为准） |
| arXiv / DOI | <https://arxiv.org/abs/2207.01206> ｜ arXiv DOI `10.48550/arxiv.2207.01206` |
| 一句话贡献 | 构造可扩展的**模拟电商环境**：118 万真实商品 + **12,087 条众包文本指令** + 1,600+ 人类演示；判分要求 agent 在多页面上检索、定制并下单，**结果必须同时匹配属性、选项与价格区间**；据摘要，最好的模型任务成功率 **29%**，规则启发式 **9.6%**，人类专家 **59%**，并报告在 amazon.com / ebay.com 上的 **sim-to-real 迁移**。 |
| 与我们工作的关系 | **harness（主目标：长程交互的「终态式」判分与人类差距）**：WebShop 的成功判据不是「说了什么」而是「买了什么」—— 与 τ-bench 的终态判分同源，但它是**单轮任务 + 多步动作** ⇒ <b>动作</b>：harness 的 agent 评测表把「成功率」与「人类基线」并列报告，并给出 **动作步数分布**（步数暴涨往往意味着在页面上来回打转，而不是在推理）。<br>**data（辅助：指令多样性）**：12,087 条众包指令可作为「属性组合覆盖度」的检查清单 ⇒ <b>动作</b>：造题时按「属性数 × 选项数 × 价格约束」分层抽样，避免只出单属性题。<br>**zhulong（弱相关）**：其「先检索再决策」的循环与 EDA 工具调用同构（查库 → 选单元 → 校验），可借其失败分类。<br>**风险**：① 环境是 2022 年的静态商品快照，网页分布已过时；② 29% vs 59% 的差距是**特定环境 + 特定模型**，🚫 不可当作「所有 agent 都差一半」；③ 众包指令含标注噪声。 |
| 首次收录 | **2026-11-18**（第五十四轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（1,765）；PDF `200` / 8,878,628 B（`%PDF-`，**>5 MB ⇒ 仅存 `/tmp`、不入 git**），`pdftotext` 核到 `1.18 million real-world products` / `12,087 crowd-sourced text instructions` / `29%` / `9.6%` / `59%` |

---

## 212. ChipNeMo: Domain-Adapted LLMs for Chip Design

| 字段 | 内容 |
|:--|:--|
| 标题 | ChipNeMo: Domain-Adapted LLMs for Chip Design |
| 作者（前 3） | Mingjie Liu · Teodor-Dumitru Ene · Robert Kirby（et al.，**40+** 位，NVIDIA；含 Bill Dally / Bryan Catanzaro / Haoxing Ren） |
| 年份 | **2023**（v1 `2023-10-31`；最新 v5 `2024-04-04`） |
| 会议 / 期刊 | **预印本技术报告**（arXiv only；`comment` = `Updated results for ChipNeMo-70B model`，未提会议 ⇒ 🚫 不写会议） |
| 被引数 | **472**（OpenAlex `10.48550/arxiv.2311.00176`，查询日 **2026-11-18**）⚠️ **<500，按「本领域权威」收**（LLM-for-EDA 的工业标志性报告） |
| arXiv / DOI | <https://arxiv.org/abs/2311.00176> ｜ arXiv DOI `10.48550/arxiv.2311.00176` |
| 一句话贡献 | 不是直接部署通用模型，而是对 LLaMA2 做**四件套领域适配**：领域自适应分词器、领域自适应继续预训练、领域指令对齐、领域检索模型；在**三个芯片设计场景**（工程助手 chatbot、EDA 脚本生成、bug 总结与分析）上评测，据摘要 **ChipNeMo-70B 在两个场景上超过 GPT-4**，在 bug 总结上具竞争力，且通用能力无退化。 |
| 与我们工作的关系 | **zhulong（主目标：领域适配的顺序与成本）**：四件套里「分词器 → 继续预训练 → 指令对齐 → 检索」的顺序可作为 zhulong 的 A/B 骨架 ⇒ <b>动作</b>：先做「分词器 + 继续预训练」两件套的小规模对照（同一 base、同一 token 预算），再决定是否加指令对齐；若继续预训练掉通用能力 >2 点，则缩短步数或混入通用语料。<br>**designflow（造题）**：三个场景正好对应三类题型：问答（chatbot）、脚本生成（EDA 脚本）、摘要（bug triage）⇒ <b>动作</b>：designflow 的 L2/L3 题型直接按此三类分层，并各自给出可验证判据（脚本能跑 / 摘要含关键信号 / 问答命中内部术语）。<br>**data（辅助）**：领域检索模型说明「私有语料 + 检索」比「把知识压进权重」更划算 ⇒ <b>动作</b>：data 线先建内部检索索引，再评估是否值得继续预训练。<br>**风险**：① 472 被引未达 500，收录依据是「本领域权威」；② 内部语料与内部评测不可复现，数字只能作方向性参考；③ 70B 与 GPT-4 的对比是 2023–2024 年时点。 |
| 首次收录 | **2026-11-18**（第五十四轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（472）；PDF `200` / 1,135,269 B（`%PDF-`，<5 MB），`pdftotext` 核到 `domain-adaptive tokenization` / `ChipNeMo-70B` / `outperforms the highly capable GPT-4 on two of our use cases` |

---

## 213. Tülu 3: Pushing Frontiers in Open Language Model Post-Training

| 字段 | 内容 |
|:--|:--|
| 标题 | Tülu 3: Pushing Frontiers in Open Language Model Post-Training |
| 作者（前 3） | Nathan Lambert · Jacob Morrison · Valentina Pyatkin 等 **23** 位（Allen Institute for AI / University of Washington；含 Hannaneh Hajishirzi / Noah A. Smith / Pradeep Dasigi） |
| 年份 | **2024**（v1 `2024-11-22`；最新 v5 `2025-04-14`） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `comment` = `Added Tulu 3 405B results and additional analyses`，未提会议 ⇒ 🚫 不写会议） |
| 被引数 | **1,670**（OpenAlex `10.48550/arxiv.2411.15124`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2411.15124> ｜ arXiv DOI `10.48550/arxiv.2411.15124` |
| 一句话贡献 | 把后训练从「调 prompt」变成**可复算的配方**：在 Llama 3.1（8B / 70B / 405B）上依次做 SFT → DPO → 作者自创的 **RLVR**（Reinforcement Learning with Verifiable Rewards），并把数据、代码、评测（Tülu 3 Eval）、训练基础设施全部开放；据摘要，成绩超过 Llama 3.1 / Qwen 2.5 / Mistral 的 instruct 版本，甚至超过 GPT-4o-mini 与 Claude 3.5-Haiku；正文还专门分析了「**没能稳定涨点的训练方法**」。 |
| 与我们工作的关系 | **pretrain / posttrain（主目标：后训练阶段的顺序与止损判据）**：三段式 SFT→DPO→RLVR 的顺序可作为自有 2B 级模型的后训练默认骨架 ⇒ <b>动作</b>：先只跑 SFT + RLVR（跳过 DPO）与三段全跑做对照，预注册判据 = 三段全跑在可验证任务上领先 ≥2 点且通用集不损伤 >1 点，否则砍掉 DPO 省一轮算力。<br>**harness（辅助）**：其「开发集 / 未见集」双轨 + 对开放数据集做**去污染**的做法可直接借用 ⇒ <b>动作</b>：把评测集切 dev / unseen 两份，训练侧按 n-gram 重叠剔除，报告两口径分数差。<br>**data（辅助）**：RLVR 只依赖「可验证奖励」，等于把数据成本转移到**判分器**上 ⇒ <b>动作</b>：先盘清自有可验证任务（数学 / 代码 / 结构化抽取）占后训练数据的比例，再决定 RLVR 投入。<br>**风险**：① 全部结论建立在 8B 以上模型，2B 级是否同样成立**未经本文验证**；② 「超过 GPT-4o-mini」是 2024 年时点对比，🚫 不可外推为当前 SOTA；③ 405B 结果在 v5 才补，引用须注明版本。 |
| 首次收录 | **2026-11-18**（第五十五轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（1,670）；PDF `200` / 8,313,277 B（`%PDF-`，>5 MB ⇒ 仅存 `/tmp`、不入 git），`pdftotext` 核到 `Reinforcement Learning with Verifiable Rewards (RLVR)` / `surpassing the instruct versions of Llama 3.1, Qwen 2.5, Mistral` / `tulu@allenai.org` |

---

## 214. DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines

| 字段 | 内容 |
|:--|:--|
| 标题 | DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines |
| 作者（前 3） | Omar Khattab · Arnav Singhvi · Paridhi Maheshwari 等 **13** 位（Stanford / UC Berkeley / CMU 等；含 Christopher Potts / Matei Zaharia） |
| 年份 | **2023**（v1 `2023-10-05`，仅 v1） |
| 会议 / 期刊 | **预印本**（arXiv `comment` / `journal_ref` 均为空，PDF 首页标 `Preprint` ⇒ 🚫 不写会议） |
| 被引数 | **1,261**（OpenAlex `10.48550/arxiv.2310.03714`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2310.03714> ｜ arXiv DOI `10.48550/arxiv.2310.03714` |
| 一句话贡献 | 把 LM 流水线写成**声明式模块图**（signature + module），再用 **compiler** 依据指标自动优化（生成/筛选示范、拼装提示、必要时微调），取代手写 prompt 模板；据摘要，几分钟编译即可让 GPT-3.5 与 llama2-13b-chat 自举出超过标准 few-shot 的流水线（一般分别 **>25% / >65%**），并超过专家手写示范（最高 **5–46% / 16–40%**），编译到 770M 的 T5 也能与依赖 GPT-3.5 的专家提示链竞争。 |
| 与我们工作的关系 | **harness（主目标：把 prompt 从「手写资产」变成「可编译产物」）**：核心可迁移点是「**指标 → 编译器 → 提示/示范**」的闭环，而不是某个具体提示 ⇒ <b>动作</b>：harness 侧给每个任务定义 (signature, metric)，把 prompt 与 few-shot 选择交给离线编译脚本，产物带版本号入库；预注册判据 = 编译产物在同一评测集上 ≥ 手写基线，否则保留手写。<br>**data（辅助）**：编译器会**自动挑示范样本**，等于把「数据选择」变成可复算步骤 ⇒ <b>动作</b>：把选中的示范集连同随机种子一起存档，便于复现与审计。<br>**zhulong（辅助）**：EDA 脚本生成这类「输入结构化、输出可验证」的任务最适合用 metric 驱动编译。<br>**风险**：① 论文只 v1、无同行评审版本，指标提升是在 2023 年的模型与任务上测得；② 「>65%」是相对标准 few-shot 的相对提升，🚫 不可当成绝对准确率；③ 编译器需要每条任务一个可靠 metric，没有 metric 的任务不适用。 |
| 首次收录 | **2026-11-18**（第五十五轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（1,261）；PDF `200` / 460,814 B（`%PDF-`，<5 MB），`pdftotext` 核到 `by over 25% and 65%, respectively` / `up to 5–46% and 16–40%` / `okhattab@cs.stanford.edu` |

---

## 215. OpenHands: An Open Platform for AI Software Developers as Generalist Agents

| 字段 | 内容 |
|:--|:--|
| 标题 | OpenHands: An Open Platform for AI Software Developers as Generalist Agents |
| 作者（前 3） | Xingyao Wang · Boxuan Li · Yufan Song 等 **24** 位（UIUC / CMU / Yale / UC Berkeley / Alibaba / All Hands AI 等；含 Graham Neubig / Heng Ji / Hao Peng） |
| 年份 | **2024**（v1 `2024-07-23`；最新 v3 `2025-04-18`） |
| 会议 / 期刊 | **ICLR 2025**（arXiv `comment` 原文 `Accepted by ICLR 2025`） |
| 被引数 | **1,050**（OpenAlex `10.48550/arxiv.2407.16741`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2407.16741> ｜ arXiv DOI `10.48550/arxiv.2407.16741` |
| 一句话贡献 | 把「代码 agent」做成**可复现的平台层**而不是单篇方法：统一 sandbox 运行时（bash / Python / 浏览器）、事件流状态、多 agent 委托与评测接口，默认通用 agent 为 **CodeActAgent**；据正文，其在 **SWE-bench Lite 上达到 26% 的 resolve rate**，与当时的开源 SWE 专化方案可比，并把整套平台与评测代码开源。 |
| 与我们工作的关系 | **harness（主目标：把「外壳」当第一等公民）**：本文价值在于把 **runtime / 状态 / 动作空间** 显式定义，任何分数都绑定到具体外壳版本 ⇒ <b>动作</b>：自有 harness 的结果文件必须记录 (runtime 镜像哈希, 动作空间版本, 最大轮数, 超时)；同一模型换外壳后必须重跑基线，🚫 跨外壳版本直接比较分数。<br>**designflow（辅助）**：「事件流 + 可回放」让失败可归因 ⇒ <b>动作</b>：把 designflow 的判分输入从「最终产物」扩展到「事件流」，用于区分「没做对」与「没跑起来」。<br>**data（辅助）**：SWE-bench Lite 的题面 + 测试可作为造题模板。<br>**风险**：① 26% 是 SWE-bench Lite 上的历史数字（2024 年），🚫 不可与当前榜单直接比；② 平台本身不提升模型能力，收益来自工程一致性，引用时勿写成「方法创新带来涨点」。 |
| 首次收录 | **2026-11-18**（第五十五轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（1,050）；PDF `200` / 3,293,124 B（`%PDF-`，<5 MB），`pdftotext` 核到 `Published as a conference paper at ICLR 2025` / `competitive resolve rate of 26%` / `CodeActAgent` / `gneubig@cs.cmu.edu` |

---

## 216. SAM 2: Segment Anything in Images and Videos

| 字段 | 内容 |
|:--|:--|
| 标题 | SAM 2: Segment Anything in Images and Videos |
| 作者（前 3） | Nikhila Ravi · Valentin Gabeur · Yuan-Ting Hu 等 **20** 位（Meta FAIR；含 Ross Girshick / Piotr Dollár / Christoph Feichtenhofer） |
| 年份 | **2024**（v1 `2024-08-01`；最新 v2 `2024-10-28`） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `comment` = `Website: https://ai.meta.com/sam2`，未提会议 ⇒ 🚫 不写会议） |
| 被引数 | **5,632**（OpenAlex `10.48550/arxiv.2408.00714`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2408.00714> ｜ arXiv DOI `10.48550/arxiv.2408.00714` |
| 一句话贡献 | 把「可提示分割」从图像推到**视频**：模型是带 **streaming memory** 的 transformer（记忆编码历史帧的 mask 与特征），数据侧用 data engine 收集 **SA-V 数据集（50.9K 视频 / 35.5M masks，比此前视频分割数据集多 53×）**；据摘要，视频分割用 **3× 更少交互**取得更好精度，图像分割比 SAM **更准且快 6×**。 |
| 与我们工作的关系 | **vision（主目标：视觉 token 的「记忆」设计）**：streaming memory 把「历史帧压缩成少量 token + 后续帧条件于它」做成可训练模块，与我们关心的「有限视觉 token 预算下保留长期证据」是同一问题 ⇒ <b>动作</b>：在自有 VLM 上做最小对照 —— 无记忆 / 只存 mask token / mask + 特征 token，测同图多轮追问与长视频问答的掉点曲线。<br>**data（辅助）**：data engine 的「模型—人工—再训练」闭环是造数据流水线的范本 ⇒ <b>动作</b>：designflow 造题时记录「题从哪一轮模型失败中产出」，便于追踪题目难度漂移。<br>**风险**：① 5,632 被引里含大量「用 SAM 2 当工具」的引用，不等于方法被验证；② 6× / 3× 是与其自家 SAM 及同期基线比，🚫 不可外推到任意分割器；③ 数据集与权重虽开放，训练成本未在摘要中给出，引用成本结论须读正文。 |
| 首次收录 | **2026-11-18**（第五十五轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`；OpenAlex `200`（5,632）；PDF `200` / 12,709,657 B（`%PDF-`，>5 MB ⇒ 仅存 `/tmp`、不入 git），`pdftotext` 核到 `35.5M masks across 50.9K videos` / `53× more masks` / `3× fewer interactions` / `6× faster` |

---

## 217. StarCoder 2 and The Stack v2: The Next Generation

| 字段 | 内容 |
|:--|:--|
| 标题 | StarCoder 2 and The Stack v2: The Next Generation |
| 作者（前 3） | Anton Lozhkov · Raymond Li · Loubna Ben Allal（et al.，作者 50+ 位；Hugging Face · ServiceNow Research · NVIDIA 等，BigCode 协作项目） |
| 年份 | **2024**（arXiv 首次提交 **2024-02-29**，`cs.SE`，v1 实测） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 首页 `Under review as submission to TMLR`；正式发表版本本轮**未核验** ⇒ 不写会议名） |
| 被引数 | **1,095**（OpenAlex `10.48550/arxiv.2402.19173`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2402.19173> ｜ arXiv DOI `10.48550/arxiv.2402.19173` |
| 一句话贡献 | 在 Software Heritage 档案上重建代码语料 **The Stack v2**（覆盖 **619** 种编程语言，含 issue / notebook / 文档，训练集 **900B+ 去重 token、比 StarCoder v1 大 4×**），并用 **3B/7B/15B** 三档模型各训 **3.3–4.3T token**；作者自报 StarCoder2-3B 在多数基准上超过 StarCoderBase-15B，15B 匹敌/超过两倍大的 CodeLlama-34B。 |
| 与我们工作的关系 | **data（主目标：代码语料的可审计构建）**：这篇把「语料从哪来、许可证怎么筛、按语言怎么去重」写成了可复核流程 ⇒ <b>动作</b>：自有代码语料入库前，按本文口径记录 `来源快照 / 语言清单 / 去重前后 token / 许可证白名单` 四列，缺一列不许进训练集。<br>**pretrain（辅助：故意过训小模型）**：3B 模型训 3.3T+ token（远超 Chinchilla 比例）仍继续涨 ⇒ <b>动作</b>：BaiZe 2B 的 token 预算应按「推理成本优先」重算，不要用 Chinchilla 最优比例直接卡死；对照实验固定 `tokens/param ≈ 1000×` 档。<br>**harness（辅助）**：代码评测只报「高资源语言平均分」会掩盖长尾语言退化 ⇒ <b>动作</b>：评测表按语言分桶，单列长尾桶。<br>**风险**：① 900B+ 是**去重后**统计，和 v1 的「3T 原始」不是同一口径，🚫 不可直接比大小；② 3B 超 15B 的说法绑定其自有评测集与语言分布；③ 许可证过滤会系统性删掉部分代码，引用「数据更多 ⇒ 更好」时须同时报删除了多少。 |
| 首次收录 | **2026-11-18**（第五十六轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`（6,760 B）；OpenAlex `200`（1,095）；PDF `200` / 1,114,300 B（`%PDF-`，<5 MB），`pdftotext` 核到 `619 programming languages` / `900B+ unique tokens` / `3B, 7B, and 15B parameters` / `3.3 to 4.3 trillion tokens` / `contact@bigcode-project.org`（全文**无个人邮箱**） |

---

## 218. Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing

| 字段 | 内容 |
|:--|:--|
| 标题 | Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing |
| 作者（前 3） | Zhangchen Xu · Fengqing Jiang · Radha Poovendran（et al.，共 7 位；University of Washington · Allen Institute for AI） |
| 年份 | **2024**（PDF 实测 v2 = `2024-10-07`，`cs.CL`；**首次提交日未核到**：arXiv API 本轮 `429` / `SSL_ERROR_SYSCALL 000`，不臆写） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 页眉 `Preprint`；会议信息本轮未核验） |
| 被引数 | **353**（OpenAlex `10.48550/arxiv.2406.08464`，查询日 **2026-11-18**；**&lt;500 ⇒ 按「方法论常青」收录**：只用对齐模型的前置模板自举指令，已被后续大量数据合成工作当作基线） |
| arXiv / DOI | <https://arxiv.org/abs/2406.08464> ｜ arXiv DOI `10.48550/arxiv.2406.08464` |
| 一句话贡献 | 利用对齐后 LLM 的自回归性质：只喂「用户消息之前的模板」，模型就会自己生成一条用户指令；用 Llama-3-Instruct 合成 **400 万条**指令，再走「生成回复 → 过滤」两步得到 **Magpie-Pro（1M）/ 300K 过滤子集**，作者自报其质量可接近人工对齐数据。 |
| 与我们工作的关系 | **data（主目标：零人工指令池的合法起点）**：这是「没有标注预算时如何起步」的最省事做法 ⇒ <b>动作</b>：在自有 SFT 数据冷启动时先跑 5 万条 Magpie 式自举，与人写种子集做同 token 对照，判据 = 下游任务分 + 指令多样性（去重后簇数），不看loss。<br>**harness（辅助：过滤器的可复算性）**：本文的过滤（质量 / 去重 / 难度）决定最终 300K 子集，正是我们判分器要复现的部分 ⇒ <b>动作</b>：把过滤规则写成可单测函数，固定随机种子后必须能重建同一子集。<br>**风险**：① 自举出的指令继承教师模型的**风格与盲区**（PDF 明确只对 Llama-3-Instruct 验证），换成自家模型会漂移；② 被引 353 中多数是「拿来当数据」而非「验证方法」，🚫 不可当效果已被独立复现；③ 该做法可能触碰教师模型的使用条款，入库前须法务确认。 |
| 首次收录 | **2026-11-18**（第五十六轮） |
| 核验状态 | OpenAlex `200`（353）；PDF `200` / 3,951,723 B（`%PDF-`，<5 MB），`pdftotext` 核到 `generate 4 million instructions` / `1M MAGPIE-Pro` / `300K` / `two filtered datasets` / `Llama-3-Instruct`；⚠️ arXiv API 元数据本轮未取到（`429` / `000`），故**首次提交日留白**，仅记 PDF 版本日期 |

---

## 219. Jamba: A Hybrid Transformer-Mamba Language Model

| 字段 | 内容 |
|:--|:--|
| 标题 | Jamba: A Hybrid Transformer-Mamba Language Model |
| 作者（前 3） | Opher Lieber · Barak Lenz · Hofit Bata（et al.，共 22 位；AI21 Labs） |
| 年份 | **2024**（PDF 实测 v2 = `2024-07-03`，`cs.CL`；**首次提交日未核到**：arXiv API 本轮 `429` / `000`，不臆写） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 未标会议；本轮未核验正式发表） |
| 被引数 | **789**（OpenAlex `10.48550/arxiv.2403.19887`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2403.19887> ｜ arXiv DOI `10.48550/arxiv.2403.19887` |
| 一句话贡献 | 把 Transformer 层与 Mamba 层按 **1:7** 交错（每 8 层一块），并在部分 MLP 上插入 MoE（**每 2 层一次，16 专家、top-2**），得到 **52B 总参 / 12B 激活**的模型；作者自报在 **256K** 上下文仍保持强结果，且 8bit 权重下可装进**单张 80GB GPU**（>128K 上下文时）。 |
| 与我们工作的关系 | **zhulong（主目标：架构消融的第三条轴）**：Transformer vs 纯 Mamba vs **混合比例**是当前最能解释「长上下文吞吐 / 显存」差异的对照 ⇒ <b>动作</b>：在 zhulong 的消融表新增一行「attention:Mamba = 1:7 / 1:3 / 1:1」，固定激活参数量与训练 token，只测 32K→256K 的吞吐与掉点。<br>**pretrain（辅助：激活参数口径）**：52B 总参 / 12B 激活说明「参数量」与「每 token 算力」必须分开报 ⇒ <b>动作</b>：所有训练成本表同时列 `total params / active params / tokens`，🚫 只报总参。<br>**风险**：① 单卡 80GB 的前提是 **8bit 权重**且上下文 >128K，不等于训练可单卡；② 1:7 比例是作者在其硬件与目标下的选择，PDF 只说「支持其他配置」，没给完整比例扫描表；③ 摘要级结论未覆盖中文任务，🚫 直接外推到中文长文。 |
| 首次收录 | **2026-11-18**（第五十六轮） |
| 核验状态 | OpenAlex `200`（789）；PDF `200` / 1,287,281 B（`%PDF-`，<5 MB），`pdftotext` 核到 `12B active parameters, 52B total available parameters` / `single 80GB GPU` / `l = 8, a : m = 1 : 7` / `MoE applied every e = 2 layers` / `16 experts` / `256K tokens`；⚠️ arXiv API 元数据本轮未取到（`429` / `000`），**首次提交日留白** |

---

## 220. Qwen3 Technical Report

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen3 Technical Report |
| 作者（前 3） | An Yang · Anfeng Li · Baosong Yang（et al.，共 **60** 位；阿里巴巴通义千问团队） |
| 年份 | **2025**（arXiv 首次提交 **2025-05-14**，`cs.CL`，v1 实测；`updated` 同 v1） |
| 会议 / 期刊 | **arXiv 技术报告**（PDF 未见会议名；本轮不写会议） |
| 被引数 | **19,693**（OpenAlex `10.48550/arxiv.2505.09388`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2505.09388> ｜ arXiv DOI `10.48550/arxiv.2505.09388` |
| 一句话贡献 | 一个系列同时给**稠密 6 档（0.6B / 1.7B / 4B / 8B / 14B / 32B）与 MoE 两档（30B-A3B / 235B-A22B）**，预训练 **36T token、覆盖 119 种语言**；核心是把 **thinking / non-thinking 两种模式放进同一个模型**（后训练四段：Long-CoT cold start → Reasoning RL → **Thinking Mode Fusion** → General RL），小模型则用 **strong-to-weak distillation**（off-policy + on-policy）继承大模型推理能力。作者自报 Qwen3-235B-A22B 在 **AIME'24 85.7 / AIME'25 81.5 / LiveCodeBench v5 70.7 / CodeForces 2,056**。 |
| 与我们工作的关系 | **zhulong（主目标：thinking 轴与「两模式合一」）**：它把「思考长度」做成**可分配的 budget** 而不是换模型，正是 zhulong 想测的「thinking 开关 × 语言」二维表的现成对照 ⇒ <b>动作</b>：zhulong 消融表固定模型与解码，只把 thinking budget 分档（例如 0 / 1K / 4K / 16K），同表记录准确率与 token 成本，并**预注册**「budget 翻倍后准确率增益 < X% 即判无收益」。<br>**pretrain（辅助：语言覆盖口径）**：119 语言说明「多语言能力」可以靠 36T token 覆盖而非后训练补 ⇒ <b>动作</b>：自有语料的语言清单按 ISO 码逐项登记，报「覆盖语言数 + 每语言 token 占比」，🚫 只报总 token。<br>**data（辅助：蒸馏数据）**：strong-to-weak distillation 的 off-policy / on-policy 混合，是我们做小模型冷启动的直接参照。<br>**风险**：① 19,693 次被引里含大量「引用报告做基线」的引用，不代表方法被复现；② 85.7 / 81.5 / 2,056 均为**作者自报**，本线未复现；③ 报告未给 thinking budget 与准确率的完整曲线。 |
| 首次收录 | **2026-11-18**（第五十七轮） |
| 核验状态 | arXiv API `id_list` `200` + `application/atom+xml`（6,413 B）；OpenAlex `200`（19,693）；PDF `200` / 779,424 B（`%PDF-`，<5 MB），`pdftotext` 核到 `36 trillion tokens` / `119 languages` / `0.6 to 235 billion` / `85.7 on AIME'24` / `81.5 on AIME'25` / `70.7 on LiveCodeBench v5` / `2,056 on CodeForces` / `Thinking Mode Fusion` / `Strong-to-Weak Distillation`；全文 `pdftotext` 后 **`@` 0 命中** ⇒ 无个人邮箱 |

---

## 221. 2 OLMo 2 Furious（OLMo 2）

| 字段 | 内容 |
|:--|:--|
| 标题 | 2 OLMo 2 Furious |
| 作者（前 3） | Team OLMo · Pete Walsh · Luca Soldaini（et al.，共 **43** 位；Allen Institute for AI（Ai2），含 Noah A. Smith / Luke Zettlemoyer / Ali Farhadi / Hannaneh Hajishirzi） |
| 年份 | **2024**（arXiv 首次提交 **2024-12-31**，`cs.CL`；最新 `updated` **2025-10-08**，v3 已补 32B 结果） |
| 会议 / 期刊 | **COLM 2025**（arXiv `comment` 原文 `Shorter version accepted to COLM 2025. Updated to include 32B results.`） |
| 被引数 | **870**（OpenAlex `10.48550/arxiv.2501.00656`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2501.00656> ｜ arXiv DOI `10.48550/arxiv.2501.00656` |
| 一句话贡献 | 把「全开放」做成**可复算的训练配方**：7B / 13B / 32B 稠密模型分别训 **4.05T / 5.6T / 6.6T token**（其中预训练段 3.90T / 5T / 6.06T），预训练语料 OLMo 2 Mix 1124 约 **3.9T token、95% 以上来自网页**；训练切成 **两段**（第二段 mid-training 占 **5–10% 的 FLOPs**），mid-training 阶段换用 **Dolmino Mix 1124** 做退火；稳定性上换成 **RMSNorm + QK-Norm + Z-Loss**，并用**多随机序重跑 50B/100B token 的 checkpoint soup（模型平均）**降低方差；后训练沿用 Tülu 3 的做法并加 **RLVR**。作者自报 OLMES 子集上 OLMo 2 32B 平均 **73.3**。 |
| 与我们工作的关系 | **pretrain（主目标：两段式训练与退火预算）**：把「预训练 / mid-training」显式切开并给出 FLOPs 占比，是我们做 2B 级模型「何时切退火」的直接对照 ⇒ <b>动作</b>：预训练日志固定记录 `stage1 tokens / stage2 tokens / stage2 FLOPs 占比`，并把退火数据清单按来源（DCLM / Dolma / ProofPile II / StarCoder）分列。<br>**data（主目标：mix 的可复算性）**：Mix 1124 + Dolmino 1124 两套配比都给了来源与比例 ⇒ <b>动作</b>：自有配比表按同一粒度（来源 × 子集 × 占比 × 去重前后 token）落盘，版本号写成 `mix-<YYMM>` 便于与论文对齐。<br>**harness（辅助：方差口径）**：checkpoint soup 说明「单次跑分」噪声大 ⇒ <b>动作</b>：评测报分至少 3 次不同数据序，或明确写「单次，未做 seed 平均」。<br>**风险**：① 73.3 为 OLMES 子集平均、作者自报；② mid-training 的 **Dolmino** 具体 token 预算正文给的是 FLOPs 区间（5–10%）而非固定 token 数 ⇒ 🚫 不换算成 token 反推。 |
| 首次收录 | **2026-11-18**（第五十七轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（7,762 B，含 `comment`）；OpenAlex `200`（870）；PDF `200` / 4,213,966 B（`%PDF-`，<5 MB），`pdftotext` 核到 `4.05 trillion tokens` / `3.90 trillion for pretraining stage` / `5.6 trillion` / `6.6 trillion` / `approximately 3.9 trillion tokens, with over 95% derived from web data` / `mid-training (5–10% of training FLOPs)` / `QK-Norm` / `Z-Loss` / `OLMo 2 32B 73.3` / `for 50B tokens each` |

---


## 222. AutoChip: Automating HDL Generation Using LLM Feedback

| 字段 | 内容 |
|:--|:--|
| 标题 | AutoChip: Automating HDL Generation Using LLM Feedback |
| 作者（前 3） | Shailja Thakur · Jason Blocklove · Hammond Pearce（et al.，共 **6** 位，含 Benjamin Tan / Ramesh Karri / Siddharth Garg；IBM Research · NYU · UNSW · University of Calgary） |
| 年份 | **2023**（arXiv 首次提交 **2023-11-08**，`cs.PL`；最新 `updated` **2024-06-04**） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 用 `acmart` 模板 + ACM 版权块，但本轮**未核到**具体会议/DOI ⇒ 🚫 不写会议名） |
| 被引数 | **247**（OpenAlex `10.48550/arxiv.2311.04887`，查询日 **2026-11-18**；S2 未查）。**&lt;500，按「本领域权威」收**（LLM-for-EDA 的「生成-编译-仿真」闭环里最早被反复引用的开源实现之一） |
| arXiv / DOI | <https://arxiv.org/abs/2311.04887> ｜ arXiv DOI `10.48550/arxiv.2311.04887` |
| 一句话贡献 | 把「生成 Verilog」做成**闭环**而非一次性补全：先用设计 prompt 生成初版 module，再把 **Icarus Verilog 的编译错误与仿真输出差异**回灌给对话模型迭代修正；在 **HDLBits** 的设计 prompt + testbench 上评测 **GPT-4 / GPT-3.5-turbo / Claude 2 / Code Llama**，作者自报通过 **89.19% 的全部测试用例、比 zero-shot 多 24.2%**，脚本与数据集开源（`github.com/shailja-thakur/AutoChip`）。 |
| 与我们工作的关系 | **designflow（主目标：反馈信号的定义）**：它说明「编译通过」与「仿真一致」是两个不同信号，且**回灌哪个信号决定模型学什么** ⇒ <b>动作</b>：designflow 判分器把 `compile_pass / sim_match / 功能等价` 拆三级分别记录，🚫 不用单一 pass 率代替；造题时每个 testbench 额外留一份**不参与反馈**的隐藏用例，用于检测「只对齐 testbench」。<br>**harness（辅助：迭代预算口径）**：报分必须同时写 `轮数上限 / 每轮 token 成本 / 模型版本`，否则 24.2% 无法与其他外壳比较。<br>**风险**：① 原文表述是「24.2% more than zero-shot settings」，基数与口径需按表核（本线未复现）；② 模型为 2023 年的 GPT-4 / Claude 2 / Code Llama，🚫 不可外推到现在；③ 隐藏用例若与反馈用例同源，分数会虚高。 |
| 首次收录 | **2026-11-18**（第五十七轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（7,762 B）；OpenAlex `200`（247）；PDF `200` / 1,637,705 B（`%PDF-`，&lt;5 MB），`pdftotext` 核到 `89.19% of all test cases` / `24.2% more than zero-shot settings` / `Icarus Verilog` / `HDLBits` / `GPT-4, GPT-3.5-turbo, Claude 2, and Code` / `the first feedback-driven` |

---

## 223. OLMoE: Open Mixture-of-Experts Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | OLMoE: Open Mixture-of-Experts Language Models |
| 作者（前 3） | Niklas Muennighoff · Luca Soldaini · Dirk Groeneveld（et al.，共 **23** 位；Allen Institute for AI / University of Washington / CMU / Stanford 等，含 Ali Farhadi / Noah A. Smith / Hannaneh Hajishirzi） |
| 年份 | **2024**（arXiv 首次提交 **2024-09-03**，`cs.CL`；`comment` = `63 pages (24 main), 36 figures, 17 tables`） |
| 会议 / 期刊 | **arXiv 预印本**（`comment` 未提会议；本轮**未核到**正式会场 ⇒ 🚫 不写会议名） |
| 被引数 | **374**（OpenAlex `10.48550/arxiv.2409.02060`，查询日 **2026-11-18**；S2 未查）。**&lt;500，按「方法论常青」收**（全开放 MoE 的消融基线，被后续 MoE 工作反复当对照） |
| arXiv / DOI | <https://arxiv.org/abs/2409.02060> ｜ arXiv DOI `10.48550/arxiv.2409.02060` |
| 一句话贡献 | 训练并**全量开源**一个稀疏 MoE：**OLMoE-1B-7B** 在 **5.1T token** 上预训练，**总参数 6.9B、每 token 激活 1.3B**（推理成本≈1B 稠密模型）；架构为每层 **64 个专家、激活 8 个**（FFN 维度 1,024，对照稠密模型 FFN 8,192 ⇒ 激活参数对齐）；据正文消融，**dropless token-based routing 优于 expert-based**、**shared experts 无收益**、路由在**预训练约 1%（5,000 步 / 20B token）时已基本饱和**；摘要称同激活规模下超过所有可用模型，并超过 Llama2-13B-Chat 与 DeepSeekMoE-16B。 |
| 与我们工作的关系 | **pretrain（主目标：MoE vs 稠密的对照怎么设）**：它给了一个「**激活参数对齐**」的受控实验（1.3B dense vs 1.3B active / 6.9B total，同 130B token、各 128×H100）⇒ <b>动作</b>：BaiZe 若做 MoE 分支，对照实验必须同时报 `total / active / tokens / 卡数`，并把 dense 基线压到**同 active**，🚫 用同 total 比。<br>**data（辅助）**：5.1T token + 全开源日志 ⇒ <b>动作</b>：把「路由饱和点」写进训练监控（每 5k 步记 top-8 命中集合的重合率），早饱和就早停路由相关调参。<br>**harness（辅助）**：报分必须标 active 参数，否则与稠密模型不可比。<br>**zhulong（辅助）**：路由饱和曲线可作为「专家分化是否发生」的廉价探针。<br>**风险**：① 374 被引里含大量「拿 OLMoE 当基线」的引用，不等于其结论被独立复现；② 「shared experts 无效」「expert-based 更差」是**在其 1.3B active 规模、其数据配比下**的结论，🚫 不可直接外推到 30B+；③ 摘要的「超过 Llama2-13B-Chat」绑定其自有评测集与 prompt。 |
| 首次收录 | **2026-11-18**（第五十八轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（23 位作者逐字核对）；OpenAlex `200`（374）；PDF `200` / **6,501,620 B**（`%PDF-`，<5 MB 但接近上限；`pdftotext` 可解析），核到 `5.1 trillion tokens with 6.9B total parameters, of which only 1.3B are activated` / `64 experts out of which 8 are activated` / `FFN dimension of 1,024` / `each on 128 H100 GPUs` / `130B tokens` / `dropless token-based routing outperforms expert-based routing` / `ineffectiveness of shared experts` / `after 1% of pretraining (5000 steps or 20B tokens)` / `Llama2-13B-Chat and DeepSeekMoE-16B` |

---

## 224. Ring Attention with Blockwise Transformers for Near-Infinite Context

| 字段 | 内容 |
|:--|:--|
| 标题 | Ring Attention with Blockwise Transformers for Near-Infinite Context |
| 作者（前 3） | Hao Liu · Matei Zaharia · Pieter Abbeel（共 **3** 位；UC Berkeley；`comment` = `Code: https://github.com/lhao499/llm_large_context`） |
| 年份 | **2023**（arXiv 首次提交 **2023-10-03**，`cs.LG`） |
| 会议 / 期刊 | **NeurIPS 2023**（ACM DL 记录 `NIPS '23: Proceedings of the 37th International Conference on Neural Information Processing Systems`；arXiv `comment` 未写会议 ⇒ 会议信息取自 ACM 记录，非 arXiv 元数据） |
| 被引数 | **508**（OpenAlex `10.48550/arxiv.2310.01889`，查询日 **2026-11-18**；S2 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2310.01889> ｜ arXiv DOI `10.48550/arxiv.2310.01889` |
| 一句话贡献 | 把长上下文训练拆成**块内计算 + 环状传递 KV 块**：激活显存只与**块大小 c 线性相关、与序列长度 s 无关**（Table 1），且 KV 通信与块计算**完全重叠**（论文要求 c ≥ FLOPS/Bandwidth，最小序列 s = 6c，Table 2）；据正文，**8×A100 可训 256K 上下文**，外推 **512 张 A100 → 1,600 万 token**，并在 7B–65B 上实测 Table 4 的 MFU（含 `over 4M` 上下文配置）。 |
| 与我们工作的关系 | **pretrain（主目标：长上下文训练的显存口径）**：它把「上下文能多长」从模型常数变成**硬件常数**（c = FLOPS / 带宽）⇒ <b>动作</b>：BaiZe 的长上下文实验先按自家互联算 `c` 与 `s = 6c`，若目标序列 < 6c 就**不要**上 ring（通信盖不住计算），直接用小 block + 重算更划算；把 `c / s / 实测 MFU` 写入实验预注册表。<br>**harness（辅助）**：长上下文评测必须同时报「训练序列长度 / 注意力实现 / 卡数」，否则 RULER 类分数不可比。<br>**zhulong（辅助）**：EDA 长文档（规格书 + 波形报告）属长序列场景，可复用其「块内局部 + 环状全局」的划分思路。<br>**风险**：① 16M 是**外推**（论文原话为 `it suggests`），🚫 不是实测；② Table 2 的 `c` 是**最保守下界**，实际实现可用更小 block 配重算；③ 508 被引里含大量「长上下文综述引用」，不等于方法在异构集群上被验证。 |
| 首次收录 | **2026-11-18**（第五十八轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（3 位作者逐字核对）；OpenAlex `200`（508）；PDF `200` / **1,766,025** B（`%PDF-`），`pdftotext` 核到 `the minimal block size required c = FLOPS/Bandwidth, and minimal sequence length s = 6c` / Table 2 的 `1.0`、`6.2`（A100 NVLink）与 `24.5`、`149.5`（A100 InfiniBand） / `256K context size when using 8x A100 GPUs` / `512 A100 GPUs ... 16 million` / `Table 4: Model flops utilization (MFU)` / `7B-65B`；Table 2 / Table 4 数值先用 ar5iv 全文页交叉核对（`https://ar5iv.labs.arxiv.org/html/2310.01889` `200` / 221,572 B） |

---

## 225. DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models |
| 作者（前 3） | Damai Dai · Chengqi Deng · Chenggang Zhao（共 **17** 位；DeepSeek-AI（含北京大学合作者，见作者名单末两位 `Zhifang Sui` / `Wenfeng Liang`）；`cs.CL`） |
| 年份 | **2024**（arXiv 首次提交 **2024-01-11**，v1 即终版，无更新） |
| 会议 / 期刊 | **预印本技术报告**（arXiv `comment` 未标会议；会议/期刊**本轮未核** ⇒ 不写） |
| 被引数 | **1,590**（OpenAlex `10.48550/arXiv.2401.06066`，查询日 **2026-11-18**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2401.06066> ｜ arXiv DOI `10.48550/arXiv.2401.06066` |
| 一句话贡献 | 提出两条正交改动把「专家」切细：**fine-grained expert segmentation**（把 FFN 切成 `mN` 个专家、激活其中 `mK` 个，总参数与激活参数不变）＋ **shared expert isolation**（固定 `Ks` 个专家对所有 token 常开，吸收公共知识、压缩其余专家的冗余）；由此把一份算力**集中到更少的激活参数**上。作者自报三档：**2B** 档 = 2.0B 总参、`1 shared + 7/63 routed`、每个专家为**标准 FFN 的 0.25 倍**；**16B** 档在 **2T token** 上训练，用**约 40% 计算量**达到 **DeepSeek 7B**（同 2T 语料稠密模型）的可比水平，并与激活参数约 2.5 倍的 **LLaMA2 7B** 相当；**145B** 档（初步）为 **62 层 / hidden 4096 / 32 头×128**、`4 shared + 12/128 routed`、专家为 **0.125×FFN**，**144.6B 总参 / 约 22.2B 激活**，仅训 **245B token（13,000 步）**。 |
| 与我们工作的关系 | **pretrain（主目标：MoE 的结构超参与负载均衡系数口径）**：可直接抄走三组**成对可复现的超参**——① 专家粒度（`0.25×` / `0.125×` 标准 FFN）② `shared : activated-routed = 1:3`（作者实测 1/2/4 个 shared expert 的 Pile loss 为 **1.808 / 1.806 / 1.811**，差异很小，故取 1:3）③ 均衡损失两级分开——**expert-level balance factor 0.01（2B/16B）/ 0.001（145B）**、device-level 用更大的值；作者原话是「expert-level 取小以防路由塌缩，device-level 取大以均衡设备计算」。⇒ <b>动作</b>：BaiZe 的 MoE 消融表把这两级系数**分开记**（现在若只记一个总的 aux loss 系数，跨规模不可比），并在 145B 档前先跑「0.01 vs 0.001」小规模对照。<br>**zhulong（辅助：成本口径）**：报分必须同时给 `total / activated / tokens`（16B 档「40% 计算量」这一句只有在给了 2T token 与稠密对照时才立得住）。<br>**risk**：① 145B 档自述为 **ongoing / preliminary**（仅 245B token，约为 16B 档的 1/8），🚫 不能当「145B 已验证」引用；② 被引 1,590 含大量「MoE 综述引用」，不等于方法在异构集群复现；③ 2B 档的对照是**同参数量**的 GShard / Hash Layer，不是同激活参数量，读表时容易错位。 |
| 首次收录 | **2026-11-18**（第五十九轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（17 位作者逐字核对）；OpenAlex `200`（1,590）；PDF `200` / **733,666** B（`%PDF-`，`pdftotext` 可解析），核到 `64 total experts` / `1 shared expert and 7 out of 63 routed experts` / `0.25 times the size of a standard FFN` / `2.0B total parameters` / `trained on a large-scale corpus with 2T tokens` / `with only about 40% of computations` / `comparable performance with DeepSeek 7B` / `1.808, 1.806, and 1.811` / `expert-level balance factor of 0.01` / `0.001` / `4 shared experts and 128 routed experts` / `144.6B total parameters` / `around 22.2B` / `245B training tokens` / `13,000 steps` / `3.0 × 10−4` |

---

## 226. Small-scale proxies for large-scale Transformer training instabilities

| 字段 | 内容 |
|:--|:--|
| 标题 | Small-scale proxies for large-scale Transformer training instabilities |
| 作者（前 3） | Mitchell Wortsman · Peter J. Liu · Lechao Xiao（共 **16** 位；Google DeepMind / Google Research；`cs.LG`） |
| 年份 | **2023**（arXiv 首次提交 **2023-09-25**，v2 **2023-10-16**） |
| 会议 / 期刊 | **未核**（arXiv `comment` 未标会议；OpenAlex 记录的 source = `arXiv (Cornell University)`、type = `preprint` ⇒ 🚫 不写 ICLR，待另核会议页） |
| 被引数 | **139**（OpenAlex `10.48550/arXiv.2309.14322`，查询日 **2026-11-18**；S2 / Google Scholar 未查）——**<500，按「方法论常青」收录**：它是「用小模型复现大模型 loss spike」这一做法的**标准参照**，后续训练稳定性工作报告几乎都要与它对照 |
| arXiv / DOI | <https://arxiv.org/abs/2309.14322> ｜ arXiv DOI `10.48550/arXiv.2309.14322` |
| 一句话贡献 | 证明**大模型的两类训练不稳定可以在小模型上复现**：① 注意力 logit 增长、② 输出 logit 与 log-prob 的偏离；办法是**把学习率扫大**（AdamW，LR 扫 `{3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1}`，cosine + 5e3 步 warmup、总 1e5 步、batch 256×512 token、词表 32,101）。关键结论：**qk-layernorm + z-loss（系数 1e-4）能把稳定训练区间拉开约三个数量级的学习率**；并在 **4.8B** 上做了「先预测、后验证」——用各规模下 attention logit 最大值拟合曲线，预测「无 qk-layernorm 时 4.8B 在 LR 1e-2 会发散」，实测**确实发散**；另报「注意力 logit 超过 `1e4` 的点全部发散」。 |
| 与我们工作的关系 | **pretrain（主目标：把「稳定性」变成可预算的小规模实验）**：这篇给出一个**可执行的预检协议**——① 先在 ≤1B 档把 LR 扫到发散边界，记录 **max attention logit**；② 拟合 logit 随规模的曲线，**在花大卡之前预测目标规模会不会炸**；③ 判据写死：注意力 logit > `1e4` 即视为进入发散区。⇒ <b>动作</b>：BaiZe 2B 的 WSD 训练在每次改结构 / 改 LR 时跑一档「LR 上扫」小实验，把 `max attention logit` 与 `qk-layernorm 开/关` 两列写进实验表；若不用 qk-layernorm，则必须配 z-loss 1e-4。<br>**zhulong（辅助：失败归因）**：训练日志须留 `attention logit max` 与 `output logit vs log-prob` 两个指标，否则「spike 归因」只能靠猜。<br>**risk**：① 小模型复现的是**同一类**不稳定，不等于大模型**同一处**不稳定；② 论文用的是自家内部训练栈（T5 词表 + SentencePiece），迁移到别的 tokenizer / 并行策略需重扫 LR；③ 139 被引对 ICLR 论文偏低，说明它在「工程实践」里被用得多、在「学术引用」里被记得少——🚫 不要拿被引数判断它没用。 |
| 首次收录 | **2026-11-18**（第五十九轮） |
| 核验状态 | arXiv API `title` 检索 `200` + atom（16 位作者逐字核对，首作者 `Mitchell Wortsman`）；OpenAlex `200`（139）；PDF `200` / **10,685,777** B（`%PDF-`，**>5 MB ⇒ 只存 `/tmp`，不入 git**），`pdftotext` 核到 `three orders of magnitude of learning rate` / `qk-layernorm allows training a model with 1.2B parameters at learning rate 0.3` / `z-loss coefficient 1e-4` / `we predict that a 4.8B parameter model will be unstable at LR 1e-2 without qk-layernorm` / `we trained a new 4.8B parameter model at LR 1e-2. This model diverged as predicted` / `all points with attention logits above 1e4 diverged` / `The default batch size is 256` / `has size 32101`；数字另用 ar5iv 全文页交叉核对（<https://ar5iv.labs.arxiv.org/html/2309.14322> `200` / 213,785 B） |

---

## 227. Mixed Precision Training

| 字段 | 内容 |
|:--|:--|
| 标题 | Mixed Precision Training |
| 作者（前 3） | Paulius Micikevicius · Sharan Narang · Jonah Alben（共 **11** 位；NVIDIA + Baidu Research；`cs.AI`） |
| 年份 | **2017**（arXiv 首次提交 **2017-10-10**，v3 **2018-02-15**） |
| 会议 / 期刊 | **ICLR 2018**（PDF 页眉原文 `Published as a conference paper at ICLR 2018`，本轮以 PDF 为准） |
| 被引数 | **2,697**（OpenAlex `10.48550/arXiv.1710.03740`，查询日 **2026-11-18**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1710.03740> ｜ arXiv DOI `10.48550/arXiv.1710.03740` |
| 一句话贡献 | 给出「用 FP16 训练而不掉精度」的**三件套**：① **FP32 master weights**（更新在 FP32 上做，再舍入成 FP16 给下一步）② **loss scaling**（把 loss 乘常数把梯度挪进 FP16 可表示区间，反传后、裁剪前再除回来）③ **FP16 乘法 + FP32 累加**。作者报告三处可复核的数字：**约 5% 的权重梯度指数小于 `−24`**（FP16 下直接变 0）；Multibox SSD 的激活梯度里 **67% 为 0**，而 `[2^-27, 2^-24)` 区间的值对训练**仍然重要**；**loss scaling 因子实测取 8 – 32K**（判据是「最大绝对梯度 × 因子 < 65,504」，即 FP16 最大值），并给出「检测到溢出就跳过该步更新」的做法。 |
| 与我们工作的关系 | **pretrain（主目标：数值口径，不是「要不要用 FP16」而是「怎么记超参」）**：这篇是今天所有 BF16/FP16 训练配置的**出处**。⇒ <b>动作</b>：BaiZe 的训练配置表固定记四列——`master weight dtype / 累加 dtype / loss scale 取值与方式(常数或动态) / 溢出处理策略(跳过或回滚)`；现在若只写「bf16 训练」，等于把**是否开 loss scaling、溢出怎么办**这两处最容易炸的细节藏起来了。BF16 动态范围与 FP16 不同（指数位更多），⇒ 迁移时**不能照搬 8–32K 的常数因子**，须按「最大绝对梯度 × 因子 < 目标格式最大值」重算。<br>**zhulong（辅助：成本口径）**：FP16 算术吞吐为 FP32 的 **2×–8×**（论文原话），是「换精度省多少」这一账的原始依据；报「训练成本」时须同时给精度格式。<br>**risk**：① 2017 年的 GPU（V100 以前）与今天的 BF16/FP8 生态不同，因子与结论需重验；② 「FP32 master weights 并非所有网络都必需」是作者原话 ⇒ 🚫 不要写成「必须」；③ `65,504` 是 **FP16** 的上界，BF16 不适用。 |
| 首次收录 | **2026-11-18**（第五十九轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（11 位作者逐字核对）；OpenAlex `200`（2,697）；PDF `200` / **1,404,641** B（`%PDF-`），`pdftotext` 核到 `Published as a conference paper at ICLR 2018` / `half-precision math throughput in recent GPUs is 2× to 8× higher` / `single-precision master weights and updates, loss-scaling, and accumulating FP16 products into FP32` / `approximately 5% of weight gradient values have exponents smaller than −24` / `67% of the values are zero` / `gradient values below 2−27 in magnitude were irrelevant ... but values in the [2−27, 2−24) range were important` / `scaling factors ranging from 8 to 32K` / `below 65,504` / `skip the weight update when an overflow is detected`；作者单位与 PDF 首页明文邮箱亦已核（`{pauliusm, alben, ...}@nvidia.com` / `{sharan, gdiamos}@baidu.com`，2017 年地址，**发信前须先核现行主页**） |

---

## 228. Zero Bubble Pipeline Parallelism

| 字段 | 内容 |
|:--|:--|
| 标题 | Zero Bubble Pipeline Parallelism |
| 作者（前 3） | Penghui Qi · Xinyi Wan · Guangxing Huang（第 4 位 Min Lin；共 **4** 位；Sea AI Lab；`cs.DC`） |
| 年份 | **2023**（arXiv 首次提交 / 唯一版本 **2023-11-30**） |
| 会议 / 期刊 | **未核**（arXiv `comment` 无会议；OpenAlex source = `arXiv (Cornell University)`、type = `preprint` ⇒ 🚫 不写 ICLR/MLSys，待另核） |
| 被引数 | **100**（OpenAlex `10.48550/arXiv.2401.10241`，查询日 **2026-11-18**；S2 / Google Scholar 未查）——**<500，按「奠基 / 开创范式」收录**：自述 **first to successfully achieve zero pipeline bubbles under synchronous training semantics**，此前「bubble 不可避免」是 PP 的共识前提 |
| arXiv / DOI | <https://arxiv.org/abs/2401.10241> ｜ arXiv DOI `10.48550/arXiv.2401.10241` |
| 一句话贡献 | 把 1F1B 的调度**按「前向 F / 反向输入梯度 B / 反向权重梯度 W」拆成三类 pass**，用 W 去填尾端空泡：手写调度 **ZB-H1** 把空泡压到 1F1B 的 **1/3**、峰值激活与 1F1B 相同（`pMB`）；**ZB-H2** 做到 **零空泡**、代价是峰值激活升到 `(2p−1)MB`；再给**虚拟流水（ZB-V）**在「接近零空泡」和最小内存之间取点。真正实现零空泡还需**绕开 optimizer step 的跨 stage 同步**：改为「先各自更新、之后做 post-validation，发现偏离再回滚」，从而在不破坏同步语义的前提下省掉 all-reduce 屏障。实测相对 1F1B：**同等内存上限下吞吐 +23%**，**放宽内存后可到 +31%**。 |
| 与我们工作的关系 | **pretrain（主目标：2B 多机训练的吞吐账）**：如果 BaiZe 2B 用 PP 而不是纯 DP/FSDP，这篇给出**可直接试的两种配置**：低内存档用 ZB-H1（空泡 1/3、内存不变），内存有余档用 ZB-H2（零空泡、激活 ~2×）。⇒ <b>动作</b>：在 8×GPU 上做一次「1F1B vs ZB-H1 vs ZB-H2」三组对照，固定 micro-batch 数与模型切分，记录 `tokens/s`、`峰值激活`、`optimizer 同步耗时` 三列；<b>预注册判据</b>：若 ZB-H1 的 tokens/s 提升 <10%（即 23% 的收益在 2B 规模上不成立），则不上 PP 调度改造，把工程预算转去数据管线。<br>**zhulong（成本口径）**：+23% / +31% 是**训练吞吐**数字，不是推理；成本表里 PP 相关项必须标「调度器版本」，否则两次跑分不可比。<br>**风险**：① 100 被引、2023 年预印本，**未核到正式会议**；② 实验规模与拓扑（未在本轮核）与我们的集群不同，收益需自测；③ 「post-validation 回滚」会改变**优化器语义**（严格同步 vs 事后校验），对可复现性有影响 ⇒ 跑对照时必须两组同 seed 且记录回滚次数。 |
| 首次收录 | **2026-11-18**（第六十轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（4 位作者逐字核对，单位 `Sea AI Lab`）；OpenAlex `200`（100）；PDF `200` / **649,126** B（`%PDF-`，`pdftotext` 可解析），核到 `first to successfully achieve zero pipeline bubbles under synchronous training` / `improve upon the widely used 1F1B schedule up to 23% in throughput under a similar memory limit` / `further pushed to 31% when the memory constraint is relaxed` / `bypass synchronizations during the optimizer step` / `bubble size is reduced to a third of 1F1B’s size` / `ZB-H1 (p − 1)(TF + TB − TW) ... pMB` / `ZB-H2 (p − 1)(TF + TB − 2TW) ... (2p − 1)MB` |

---

## 229. FP8 Formats for Deep Learning

| 字段 | 内容 |
|:--|:--|
| 标题 | FP8 Formats for Deep Learning |
| 作者（前 3） | Paulius Micikevicius · Dusan Stosic · Patrick Judd（共 **8** 位；NVIDIA；`cs.LG`） |
| 年份 | **2022**（arXiv 首次提交 **2022-09-12**，v2 **2022-09-29**） |
| 会议 / 期刊 | **无**（技术报告，arXiv `comment` 未标会议；OpenAlex type = `preprint` ⇒ 🚫 不写会议） |
| 被引数 | **593**（OpenAlex `10.48550/arXiv.2209.05433`，查询日 **2026-11-18**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2209.05433> ｜ arXiv DOI `10.48550/arXiv.2209.05433` |
| 一句话贡献 | 定义深度学习的两种 8 位浮点编码并给出**用途分工**：**E4M3**（4 位指数 / 3 位尾数，指数偏置 **7**，最大正规数 **448**，**不表示无穷**、只有**一种 NaN 位型** `S.1111.111`）用于**权重与激活**；**E5M2**（5 位指数 / 2 位尾数，偏置 **15**，最大正规数 **57,344**，遵循 IEEE 754 特殊值约定）用于**梯度**。关键工程结论：**缩放因子（scaling factor）放在软件里做，而不是改指数偏置**；并且 **FP16 AMP 那套「按溢出历史调 loss scale」的做法对 FP8 不是好选择**——FP8 的动态范围问题更多来自张量间的分布差异，需按张量/通道选缩放因子；同时给出 E4M3↔FP16 转换时「无穷与 NaN 都映射为 NaN」的特殊值规则，供混合精度运行时依赖 NaN 检测做 loss-scale 调整。 |
| 与我们工作的关系 | **pretrain（主目标：低精度训练的三列口径）**：我们现在只写「bf16」，一旦要试 FP8 就缺口径。这篇给的是**格式层**的硬约束，直接决定配置表怎么写。⇒ <b>动作</b>：BaiZe 的训练配置表在原有四列之外增加 `FP8 格式（E4M3/E5M2）`、`缩放粒度（per-tensor / per-channel）`、`缩放因子来源（静态标定 / 动态更新）` 三列；<b>预注册判据</b>：任何「FP8 不掉点」的主张，必须同时给出 `缩放粒度 + 是否保留 FP32 master weights + 溢出处理`，缺一项判不可比。<br>**zhulong（口径）**：推理侧若上 FP8，成本表要区分「权重/激活 FP8」与「KV cache 精度」——本文只覆盖训练侧格式，🚫 不外推。<br>**风险**：① 593 被引但只是 2 页技术报告，**无实验细节、无训练曲线**；② 结论基于 NVIDIA 自家硬件路径（H100 之前的格式提案），与本机 GPU 的转换指令实现可能不同；③ 「E5M2 用于梯度」是建议而非定理，实际有效性与模型/损失尺度相关。 |
| 首次收录 | **2026-11-18**（第六十轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（8 位作者逐字核对，单位 `NVIDIA`）；OpenAlex `200`（593）；PDF `200` / **281,195** B（`%PDF-`），`pdftotext` 核到 `E4M3 (4-bit exponent and 3-bit mantissa) and E5M2 (5-bit exponent and 2-bit mantissa)` / `E4M3’s dynamic range is extended by not representing infinities and having only one mantissa bit-pattern for NaNs` / `Exponent bias 7 ... 15` / `Max normal ... 448 ... 57, 344` / `E4M3 for weight and activation tensors, and E5M2 for gradient tensors` / `preference for scaling factor handling in software rather than via exponent bias` / `is not a good choice for FP8` |

---

## 230. SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features

| 字段 | 内容 |
|:--|:--|
| 标题 | SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features |
| 作者（前 3） | Michael Tschannen · Alexey Gritsenko · Xiao Wang（共 **14** 位；Google DeepMind；`cs.CV`） |
| 年份 | **2025**（arXiv 首次提交 / 唯一版本 **2025-02-20**） |
| 会议 / 期刊 | **未核**（arXiv `comment` 未标会议；OpenAlex type = `preprint` ⇒ 🚫 不写 CVPR/ICLR） |
| 被引数 | **1,822**（OpenAlex `10.48550/arXiv.2502.14786`，查询日 **2026-11-18**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2502.14786> ｜ arXiv DOI `10.48550/arXiv.2502.14786` |
| 一句话贡献 | 在 SigLIP 的 **sigmoid 图文损失**之上合并四条独立技术成一条配方：① **captioning 预训练**（LocCa 式解码器，含 dense captioning 与 referring expression）② **自蒸馏 + 掩码预测**（教师取学生参数的 **EMA**，提升分割/深度等稠密任务）③ **在线数据筛选** ④ 多语数据去偏，得到 **109 种语言**可用的编码器族。发布 **四个尺寸：ViT-B（86M）/ L（303M）/ So400m（400M）/ g（1B）**，文本塔用 **256k 词表的 Gemma 分词器**、文本长度 64；另有 **NaFlex** 变体——单模型原生支持不同分辨率与长宽比。作者报告该配方在定位与稠密预测上显著改善，并额外用纯 sigmoid 图文损失多训了 **4B 样本**。 |
| 与我们工作的关系 | **vision（主目标：小模型视觉塔的配方与尺寸选择）**：我们 2B 级模型的视觉塔大概率在 86M–400M 区间，这篇正好给出**四档尺寸 + 同一配方的对照**。⇒ <b>动作</b>：vision 线把「ViT-B/86M」与「So400m/400M」两档按本文配方各训一版（sigmoid + captioning + EMA 自蒸馏），在**我们的 agent 任务**上比，而不是只看 ImageNet 线性探测；<b>预注册判据</b>：若 400M 档相对 86M 在目标任务上提升 <3% 而训练成本 >2×，则 2B 主模型锁 86M 档，把参数预算给语言侧。<br>**vision（多语与 NaFlex）**：中文工单/截图场景长宽比极端 ⇒ <b>动作</b>：评测集固定加入「竖屏截图 / 宽幅波形图」两类，比较 NaFlex 与固定分辨率版本的定位指标。<br>**风险**：① 1,822 被引中含大量「引用一个 checkpoint」式引用，**不等于方法被验证**；② 多语增益主要来自数据配比，我们的域内图文对可能不足以复现；③ 4B 额外样本的收益未给消融，🚫 不能当「多训一定更好」的依据。 |
| 首次收录 | **2026-11-18**（第六十轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（14 位作者逐字核对，单位 `Google DeepMind`）；OpenAlex `200`（1,822）；PDF `200` / **623,539** B（`%PDF-`），`pdftotext` 核到 `captioning-based pretraining, self-supervised losses (self-distillation, masked prediction) and online data curation` / `ViT-B (86M), L (303M), So400m (400M), and g (1B)` / `multilingual Gemma tokenizer ... vocabulary size 256k` / `109 languages` / `NaFlex combines ideas from FlexiViT ... NaViT` / `additional 4B examples using just the sigmoid image-text` |

---

## 231. Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling

| 字段 | 内容 |
|:--|:--|
| 标题 | Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling |
| 作者（前 3） | Stella Biderman · Hailey Schoelkopf · Quentin Anthony（共 **13** 位；EleutherAI / 多机构；`cs.CL`） |
| 年份 | **2023**（arXiv 首次提交 **2023-04-03**，v2 **2023-05-31**） |
| 会议 / 期刊 | **ICML 2023**（PDF 页眉原文 `Proceedings of the 40th International Conference on Machine Learning`，PMLR 202，本轮以 PDF 为准） |
| 被引数 | **761**（OpenAlex `10.48550/arXiv.2304.01373`，查询日 **2026-11-18**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2304.01373> ｜ arXiv DOI `10.48550/arXiv.2304.01373` |
| 一句话贡献 | 发布**可完全复现的训练套件**：**8 个尺寸（70M – 12B）× 两套数据（原始 Pile 300B token / MinHashLSH 近去重后约 207B token，阈值 0.87）= 16 个模型**，每个模型公开 **154 个中间 checkpoint**，且**训练顺序已知**（可精确知道某 checkpoint 见过哪些数据）。训练细节：batch **1024** 条序列（作者明确说这比 GPT-3 套件的 batch 大 4–8×，小模型也照用）、学习率按尺寸 6.0e-4 → 1.2e-4。基于该套件给出可复核的发现：去重对**记忆化**影响明显、偏见随训练动态变化，且 **65,000 步（训练进度 45%）后出现相变**——2.8B 及以上模型才开始出现「任务准确率与任务相关词频相关」，更小模型没有。 |
| 与我们工作的关系 | **harness（主目标：可复现的 checkpoint 序列是评测的对照尺）**：要回答「某能力是何时出现的」，必须能拿到同一训练轨迹上的多个 checkpoint；Pythia 是少数**训练顺序可复现**的公开套件。⇒ <b>动作</b>：harness 线把「中间 checkpoint 扫描」列为常规实验类型，评测报告固定记 `checkpoint 步数 / 已见 token 数 / 数据顺序版本` 三列；<b>预注册判据</b>：任何「能力涌现」结论必须给出至少 5 个 checkpoint 的曲线，单点结论判无效。<br>**data（去重口径）**：原始 300B → 近去重 207B（MinHashLSH 0.87）这一对可直接当我们去重实验的**参照档位**；<b>动作</b>：data 线的去重实验至少跑「不去重 / 0.87 阈值」两档，比记忆化与下游两项。<br>**pretrain（batch 口径）**：1,024 序列的 batch 在小模型上也用，是「小模型不必缩 batch」的一个现成反例；与我们 WSD 配方对照时要说明 batch 差异。<br>**风险**：① 12B 以下，**不能外推到 2B 之外的量级趋势**；② 相变点是**该套件 + Pile** 的观测，换数据/分词器需重测；③ 154 checkpoint 是 2023 年版本口径，后续版本数量可能变化（本轮未核）。 |
| 首次收录 | **2026-11-18**（第六十轮） |
| 核验状态 | arXiv API `id_list` `200` + atom（13 位作者逐字核对）；OpenAlex `200`（761）；PDF `200` / **1,091,147** B（`%PDF-`），`pdftotext` 核到 `154 checkpoints for each one of the 16` / `70M to 12B parameters` / `the deduplicated Pile is approximately 207B tokens in size, compared to the original Pile which contains 300B tokens` / `MinHashLSH and a threshold of 0.87` / `we use a batch size of 1024 samples` / `4× to 8×` / `a significant phase change occurs after 65,000 training steps (45% through training)` / `2.8 billion parameters or more`；会议取自 PDF 页眉（PMLR 202） |

---

## 232. Multimodal Autoregressive Pre-training of Large Vision Encoders (AIMv2)

| 字段 | 内容 |
|:--|:--|
| 标题 | Multimodal Autoregressive Pre-training of Large Vision Encoders（AIMv2） |
| 作者（前 3） | Enrico Fini · Mustafa Shukor · Xiujun Li（et al.，共 **16** 位，含 Alaaeldin El-Nouby；**Apple**；`cs.CV`） |
| 年份 | **2024**（arXiv 首次提交 **2024-11-21**，`cs.CV`） |
| 会议 / 期刊 | **CVPR 2025**（来源：OpenAlex `primary_location.source` = CVPR Proceedings；PDF 本轮**未核到**页眉 ⇒ 会议名只按 OpenAlex，不当作 PDF 实测） |
| 被引数 | **147**（OpenAlex `10.48550/arxiv.2411.14402`，查询日 **2026-11-19**；S2 / Google Scholar 未查）。**&lt;500，按「方法论常青 / 开源基线」收**：Apple 开源的强视觉塔，作为 SigLIP 2 / CLIP 之外的**自回归预训练**对照，被后续多模态工作反复当 baseline |
| arXiv / DOI | <https://arxiv.org/abs/2411.14402> ｜ arXiv DOI `10.48550/arxiv.2411.14402` |
| 一句话贡献 | 把「自回归预训练」从纯视觉扩展到**图文多模态**：视觉编码器配一个多模态解码器，自回归生成**原始 image patch 与文本 token**；**AIMv2-3B** 在**冻结主干**下取得 **89.5%** ImageNet-1k 准确率，并在定位 / grounding / 分类等视觉基准上超过同级判别式模型；代码与权重开源（`github.com/apple/ml-aim`）。 |
| 与我们工作的关系 | **vision（主目标：视觉塔的两条技术路线对照）**：判别式（CLIP / SigLIP）vs 生成式（AIMv2）在**参数效率**与**可扩展性**上各有取舍 —— 判别式参数效率高但难训，生成式简单可扩但需更大容量 ⇒ <b>动作</b>：视觉塔选型时把这两条各放一个基线，固定下游任务集比较，🚫 只看 ImageNet。<br>**pretrain（辅助）**：多模态解码器与主干的**容量分配**是 2B 级模型的关键预算项，可借它的消融设计。<br>**data（辅助）**：图文对与纯文本比例会影响生成式预训练的收敛。<br>**风险**：① 147 被引、2024 年工作，结论需按后续复现校正；② 89.5% 是 **AIMv2-3B + 冻结主干**的特定设定，🚫 不可外推到我们的小视觉塔。 |
| 首次收录 | **2026-11-19**（第六十一轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（147）；PDF `200` / **4,788,339 B**（`%PDF-`，`Content-Length` 对账一致；<5 MB 但接近上限 ⇒ 仅 `/tmp`，不入 git），`pdftotext` 核到 `AIM V 2-3B encoder achieves 89.5% accuracy on ImageNet-1k with a frozen trunk` / `autoregressively generates raw image patches and text tokens` / `Apple` / `github.com/apple/ml-aim` |

---


## 233. Extending Context Window of Large Language Models via Positional Interpolation

| 字段 | 内容 |
|:--|:--|
| 标题 | Extending Context Window of Large Language Models via Positional Interpolation |
| 作者（前 3） | Shouyuan Chen · Sherman Wong · Liangjian Chen（et al.，共 **4** 位，含 Yuandong Tian；Meta） |
| 年份 | **2023**（arXiv 首次提交 **2023-06-26**，`cs.CL`） |
| 会议 / 期刊 | **arXiv 预印本**（本轮以 PDF 为准，**未核到**正式会场页眉 ⇒ 🚫 不写会议名） |
| 被引数 | **983**（OpenAlex `10.48550/arxiv.2306.15595`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2306.15595> ｜ arXiv DOI `10.48550/arxiv.2306.15595` |
| 一句话贡献 | 直接**线性插值 RoPE 的位置索引**（不改结构、不加参数），把 LLaMA 7B–65B 的 2048 上下文扩到 **32768**，只需 **≤1000 步**微调；并从理论上给出「插值上界比外推上界小约 **600×**」（LLaMA 7B 设定）。 |
| 与我们工作的关系 | **pretrain（主目标：长上下文扩窗的最低成本基线）**：任何扩窗方案（YaRN / NTK-aware / 继续预训练）都应先与它同 token 预算对比 ⇒ <b>动作</b>：把 `PI + 1000 步微调` 固定为对照表第一行，报分同时给 `ppl@32K` 与 `4K→32K 保持率`。<br>**zhulong（辅助：长度轴的可归因性）**：thinking 长度实验必须记录「窗口是怎么扩的、续训多少步」，否则「长思考更好」与「窗口更大」不可区分。<br>**风险**：① 983 被引含大量「拿 PI 当 baseline」的引用，不等于其所有结论被独立复现；② 600× 是特定设定下的上界比值，🚫 不可外推为通用常数。 |
| 首次收录 | **2026-11-19**（第六十一轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（983）；PDF `200` / **751,217** B（`%PDF-`，`Content-Length` 对账一致，&lt;5 MB，不入 git），`pdftotext` 核到 `up to 32768` / `within 1000 steps` / `∼ 600× smaller` / `LLaMA 7B to 65B` |

---

## 234. Data Filtering Networks

| 字段 | 内容 |
|:--|:--|
| 标题 | Data Filtering Networks |
| 作者（前 3） | Alex Fang · Albin Madappally Jose · Amit Jain（et al.，含 Ludwig Schmidt；University of Washington 等） |
| 年份 | **2023**（arXiv 首次提交 **2023-09-27**，`cs.CV`） |
| 会议 / 期刊 | **arXiv 预印本**（本轮 PDF 未核到会场页眉；OpenAlex source = arXiv ⇒ 🚫 不写会议名） |
| 被引数 | **273**（OpenAlex `10.48550/arxiv.2309.17425`，查询日 **2026-11-19**；S2 / Google Scholar 未查）。**&lt;500，按「方法论常青」收**：图文过滤的对照基线，被后续数据筛选工作反复对比 |
| arXiv / DOI | <https://arxiv.org/abs/2309.17425> ｜ arXiv DOI `10.48550/arxiv.2309.17425` |
| 一句话贡献 | 把「第二步过滤」本身学成一个**数据过滤网络（DFN）**：在少量高质量数据上训练小分类器去筛大语料；核心发现是**ImageNet 准确率是坏代理**——高 ImageNet 精度的过滤器可能产出更差的训练集；**DFN-5B** 上训练的 ViT-H 达 **84.4%** ImageNet 零样本，并释放 **DFN-2B** 作为可复现的起点。 |
| 与我们工作的关系 | **data（主目标：过滤器准入口径）**：筛子自身的分类指标 ≠ 数据质量 ⇒ <b>动作</b>：新过滤器上线前必须给「固定小模型 × 固定 token → 下游缩放曲线」，并保留一条「低分类精度、高下游」的对照组。<br>**vision（辅助）**：图文对过滤阈值需与下游任务绑定，🚫 不按单一 benchmark 调阈值。<br>**harness（辅助）**：数据消融必须固定 token 预算，否则曲线不可比。<br>**风险**：① 结论主要在图文（CLIP 式）预训练设定，🚫 不可直接外推到纯文本；② 84.4% 为作者自报，且 ViT-H/14 训练成本高，复现门槛高。 |
| 首次收录 | **2026-11-19**（第六十一轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（273）；PDF `200` / **1,431,519** B（`%PDF-`，`Content-Length` 对账一致，&lt;5 MB，不入 git），`pdftotext` 核到 `DFN-5B` / `84.4%` / `ViT-H` / `DFN-2B` / `data filtering network` |

---


## 235. OPT: Open Pre-trained Transformer Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | OPT: Open Pre-trained Transformer Language Models |
| 作者（前 3） | Susan Zhang · Stephen Roller · Naman Goyal（et al.，含 Mikel Artetxe / Luke Zettlemoyer；Meta AI） |
| 年份 | **2022**（arXiv 首次提交 **2022-05-02**，v2 2022-06-21，`cs.CL`） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 未核到会场页眉；OpenAlex source = arXiv ⇒ 🚫 不写会议名） |
| 被引数 | **5,818**（OpenAlex `10.48550/arxiv.2205.01068`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2205.01068> ｜ arXiv DOI `10.48550/arxiv.2205.01068` |
| 一句话贡献 | 发布 **125M–175B** 的 decoder-only 开放权重模型族，并公开**训练 logbook + metaseq 代码**；OPT-175B 在 **992 张 80GB A100** 上训练，**147 TFLOP/s/GPU**，语料约 **180B token（≈800GB）**；文中如实记录 **≥35 次人工重启 + 70+ 次硬件导致的自动重启**、动态 loss scaling 与 mid-flight 调参。 |
| 与我们工作的关系 | **pretrain（主目标：失败日志口径）**：这是「把训练不稳定写进论文」的早期范例 ⇒ <b>动作</b>：2B 主跑的 runbook 增加三列 `重启原因 / loss-scale 状态 / 重启点选择依据`，每次重启必须留证；判据 = 一次长跑若重启 >5 次，先做硬件与数据两端归因再继续。<br>**data（辅）**：180B token / 175B 参数 ≈1.03 token/param，远低于 Chinchilla 20× ⇒ <b>动作</b>：引用「OPT 训练不足」时必须同时给 token/param 比，🚫 只引参数量。<br>**风险**：① 2022 年配方（Adam + 动态 loss scaling）与现在 WSD/bf16 不同，🚫 不可直接当 2026 最佳实践；② 5,818 为 OpenAlex 口径。 |
| 首次收录 | **2026-11-19**（第六十二轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（5,818）；PDF `200` / **1,765,159** B（`%PDF-`，<5 MB，不入 git），`pdftotext` 核到 `992 80GB A100` / `147 TFLOP/s` / `180B tokens` / `35 manual restarts` / `70+ automatic restarts` / `metaseq` |

---

## 236. MiniCPM: Unveiling the Potential of Small Language Models with Scalable Training Strategies

| 字段 | 内容 |
|:--|:--|
| 标题 | MiniCPM: Unveiling the Potential of Small Language Models with Scalable Training Strategies |
| 作者（前 3） | Shengding Hu 胡声鼎 · Yuge Tu · Xu Han（et al.，含 Zhiyuan Liu / Maosong Sun；清华大学等） |
| 年份 | **2024**（arXiv 首次提交 **2024-04-09**，v2 2024-06-03，`cs.CL`） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 未核到会场页眉；OpenAlex source = arXiv ⇒ 🚫 不写会议名） |
| 被引数 | **994**（OpenAlex `10.48550/arxiv.2404.06395`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2404.06395> ｜ arXiv DOI `10.48550/arxiv.2404.06395` |
| 一句话贡献 | 以 **1.2B / 2.4B（非 embedding 参数）** 两个小模型为对象，提出 **WSD（Warmup-Stable-Decay）学习率** + **Model Wind Tunnel Experiments** 的可复用训练配方；两模型均训练 **1.1T token**（≈ 2.4B × 458 token/param，远高于 Chinchilla 20×），并报告 **decay 用约 10% token 足够、2.5% 不够**；2.4B-128K 与 MiniCPM-MoE（4B 激活）同族扩展。 |
| 与我们工作的关系 | **pretrain（主目标：WSD 与 token 预算）**：我们的 2B 主跑正需要「预算未定时可复用 checkpoint」⇒ <b>动作</b>：在 1B 探针上复现 `WSD(320N, 32N)` 的 loss 轨迹，记录 stable 段可续点与 decay 段掉点幅度；判据 = decay 10% 相对 2.5% 的最终 loss 差 >0.01 才保留 WSD，否则回到 cosine。<br>**data（辅）**：1.1T token / 2.4B 参数说明「小模型过训」是可行路线 ⇒ <b>动作</b>：数据配比实验把 token/param 比作为显式列（20× / 100× / 400× 三档），🚫 只报绝对 token 数。<br>**风险**：① 1.1T token 与「超过 Mistral-7B / Llama2-13B」均为作者自报，评测集与 prompt 未第三方复现；② 15.2 MB PDF 未入 git。 |
| 首次收录 | **2026-11-19**（第六十二轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（994）；PDF `200` / **15,188,294** B（`%PDF-`，**>5 MB 仅 `/tmp`，不入 git**），`pdftotext` 核到 `1.2B` / `2.4B` / `1.1T` / `WSD` / `10%` / `2.5%` / `4M tokens` |

---

## 237. DAPO: An Open-Source LLM Reinforcement Learning System at Scale

| 字段 | 内容 |
|:--|:--|
| 标题 | DAPO: An Open-Source LLM Reinforcement Learning System at Scale |
| 作者（前 3） | Qiying Yu · Zheng Zhang · Ruofei Zhu（et al.，含 Mingxuan Wang / Yonghui Wu；ByteDance Seed · 清华 AIR） |
| 年份 | **2025**（arXiv 首次提交 **2025-03-18**，v2 2025-05-20，`cs.LG`） |
| 会议 / 期刊 | **arXiv 预印本**（PDF 未核到会场页眉；OpenAlex source = arXiv ⇒ 🚫 不写会议名） |
| 被引数 | **3,544**（OpenAlex `10.48550/arxiv.2503.14476`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2503.14476> ｜ arXiv DOI `10.48550/arxiv.2503.14476` |
| 一句话贡献 | 开源一套大规模 RL 系统：Qwen2.5-32B 上 **AIME 2024 = 50 分**（对比 DeepSeek-R1-Zero-Qwen-32B 的 **47 分**），且只用 **50% 训练步数**；算法含四个显式开关 —— **Clip-Higher**（`εlow=0.2` / `εhigh=0.28`）、**Dynamic Sampling**（过滤全对/全错组）、**Token-Level Policy Gradient Loss**、**Overlong Reward Shaping**（期望最大长度 `16,384` + `4,096` soft cache = 生成上限 `20,480` token）；并明确**移除 KL 项**。 |
| 与我们工作的关系 | **zhulong（主目标：RL 配方）**：thinking 轴要用可验证奖励做 RL ⇒ <b>动作</b>：把 DAPO 四开关逐项做成 2B 级消融（固定 prompt 集与 rollout 数），先只开 Clip-Higher，再加 Dynamic Sampling；判据 = 每个开关带来的 `pass@1` 增量 >2 个绝对点且熵不塌才保留。<br>**pretrain（辅）**：去掉 KL 后策略可漂移更远 ⇒ <b>动作</b>：在 RL 前记录 base 模型的 held-out 困惑度，RL 后复测，作为「能力漂移」监控项。<br>**harness（辅）**：`20,480` token 的生成上限与 `16,384` 的软惩罚边界必须写进评测配置，否则 pass 率不可比。<br>**风险**：① 50 vs 47 为作者自报、单一 benchmark（AIME 2024）；② 32B 规模结论不可直接外推到 2B；③ 移除 KL 的适用边界论文只给了可验证奖励设定。 |
| 首次收录 | **2026-11-19**（第六十二轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（3,544）；PDF `200` / **826,801** B（`%PDF-`，<5 MB，不入 git），`pdftotext` 核到 `50 points` / `47 points` / `50% training steps` / `εlow=0.2` / `εhigh=0.28` / `16,384` / `4,096` / `20,480` / `KL term` |

## 238. Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them（BIG-Bench Hard）

| 字段 | 内容 |
|:--|:--|
| 标题 | Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them |
| 作者（前 3） | Mirac Suzgun · Nathan Scales · Nathanael Schärli（et al.，共 11 位，含 Denny Zhou / Jason Wei；Google Research · Stanford） |
| 年份 | **2022**（arXiv 首次提交 **2022-10-17**，仅 v1，`cs.CL`） |
| 会议 / 期刊 | **arXiv 预印本**（arXiv `comment` 只给 GitHub；OpenAlex `primary_location.source` = arXiv、`type=preprint` ⇒ 🚫 不写会议名） |
| 被引数 | **1,433**（OpenAlex `10.48550/arxiv.2210.09261`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2210.09261> ｜ arXiv DOI `10.48550/arxiv.2210.09261` |
| 一句话贡献 | 从 BIG-Bench 里挑出**「此前所有模型都低于人类平均评分」的 23 个任务**组成 BBH；同一批任务上，**answer-only → CoT** 的均分变化为：PaLM 540B **52.3 → 65.2（+12.9）**、InstructGPT **51.8 → 68.4（+16.6）**、Codex **56.6 → 73.9（+16.7）**，人类平均 67.7；CoT 让若干「缩放曲线原本是平的」任务出现**涌现式提升**（Table 2）。 |
| 与我们工作的关系 | **harness（主目标：评测集与判分形态）**：BBH 的价值不是分数而是**「同一任务上换 prompting 形态，模型排名会变」**⇒ <b>动作</b>：我们的 agent 评测必须固定「是否给 CoT / 是否给工具」这一维，否则跨版本分数不可比；至少报 `answer-only` 与 `CoT` 两个口径。<br>**zhulong（辅：thinking 轴）**：<b>动作</b>：thinking 开关的判据要按任务族分层（NLP 12 / 算法 11），因为本文实测算法类收益（+17.7~+28.5）远大于 NLP 类（+7.1~+10.4）。<br>**pretrain（辅）**：`CoT enables emergent task performance` 提示「平曲线」不等于「没能力」，评测分辨率不足会误判小模型的可用性。<br>**风险**：① 2022 年的模型与 prompting 口径，分数不可与今日模型横比；② 人类基线是「平均评分者」而非专家上限（最高评分者均分 94.4）。 |
| 首次收录 | **2026-11-19**（第六十三轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（1,433）；PDF `200` / **5,375,941** B（`%PDF-`，**>5 MB ⇒ 只留 `/tmp`，不入 git**），`pdftotext` 核到 `23 challenging BIG-Bench tasks` / `52.3` / `65.2 (+12.9)` / `56.6` / `73.9 (+16.7)` / `67.7` / `10 of the 23` / `17 of the 23` |

---

## 239. Accelerating Large Language Model Decoding with Speculative Sampling

| 字段 | 内容 |
|:--|:--|
| 标题 | Accelerating Large Language Model Decoding with Speculative Sampling |
| 作者（前 3） | Charlie Chen · Sebastian Borgeaud · Geoffrey Irving（et al.，共 6 位，含 Laurent Sifre / John Jumper；DeepMind） |
| 年份 | **2023**（arXiv 首次提交 **2023-02-02**，仅 v1，`cs.CL`） |
| 会议 / 期刊 | **arXiv 预印本**（arXiv `comment` 为空；OpenAlex `type=preprint`） |
| 被引数 | **1,424**（OpenAlex `10.48550/arxiv.2302.01318`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2302.01318> ｜ arXiv DOI `10.48550/arxiv.2302.01318` |
| 一句话贡献 | 用「**小 draft 模型先猜 K 个 token + 目标模型一次并行验证 + 修正版拒绝采样**」把自回归解码变成并行验证，**数学上保持目标模型分布**（硬件数值范围内）；在 **Chinchilla 70B** 上取得 **2–2.5×** 解码加速（Table 1，batch=1、`K=4`、16×TPU v4）：XSum greedy **14.1 → 7.00 ms/token（2.01×）**、HumanEval 100-shot **14.1 → 5.73 ms/token（2.46×）**。 |
| 与我们工作的关系 | **harness（主目标：评测吞吐）**：跑成千上万次 agent rollout 时，**解码延迟直接决定单位时间能评多少 case** ⇒ <b>动作</b>：先测「draft 模型的接受率」再决定是否启用，判据 = 端到端 `ms/token` 实测下降 >30% 且输出分布校验通过才保留。<br>**pretrain（辅：服务侧成本口径）**：关键工程点是 **draft 模型要做「宽而浅」** 以减少跨设备通信（7B draft 在 16 卡上反而更慢）⇒ <b>动作</b>：若做投机解码，draft 的拓扑必须与 target 同机部署，不能按「越小越快」选。<br>**zhulong（辅）**：成本表要区分「训练成本」与「解码成本」，投机解码只改后者。<br>**风险**：① 加速比强依赖任务的可预测性（代码/摘要比开放对话更吃香）；② 70B + 16×TPU v4 的绝对值不可搬到我们的硬件；③ 分布等价性只在数值范围内成立。 |
| 首次收录 | **2026-11-19**（第六十三轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（1,424）；PDF `200` / **349,916** B（`%PDF-`，<5 MB），`pdftotext` 核到 `2–2.5× decoding speedup` / `70 billion parameter` / `14.1ms/Token` / `7.00ms/Token` / `2.01×` / `5.73ms/Token` / `2.46×` / `𝐾 = 4` |

## 240. RULER: What's the Real Context Size of Your Long-Context Language Models?

| 字段 | 内容 |
|:--|:--|
| 标题 | RULER: What's the Real Context Size of Your Long-Context Language Models? |
| 作者（前 3） | Cheng-Ping Hsieh · Simeng Sun · Samuel Kriman（et al.，共 8 位，含 Boris Ginsburg；NVIDIA） |
| 年份 | **2024**（arXiv 首次提交 **2024-04-09**，v3 2024-08-06，`cs.CL`） |
| 会议 / 期刊 | **COLM 2024**（取自 arXiv `comment` 原文：`COLM 2024; Code is available at ...`；OpenAlex 仍记 `type=preprint`、source=arXiv） |
| 被引数 | **1,799**（OpenAlex `10.48550/arxiv.2404.06654`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2404.06654> ｜ arXiv DOI `10.48550/arxiv.2404.06654` |
| 一句话贡献 | 指出 needle-in-a-haystack 只是「表层检索」，据此把长上下文评测扩成**四类任务（retrieval / multi-hop tracing / aggregation / QA）共 13 个任务**，测 **17 个长上下文模型**；用 **Llama2-7B 在 4K 的成绩（85.6）作为固定阈值**定义「有效长度」，结论是**声称 ≥32K 的模型里只有一半在 32K 仍达标**（Table 3：Llama3.1-70B 声称 128K、有效 64K，128K 处均分掉到 66.6；Gemini-1.5-Pro 有效长度 >128K、均分 95.8）。 |
| 与我们工作的关系 | **pretrain（主目标：长上下文「声称 vs 实测」）**：<b>动作</b>：BaiZe 若做 32K 扩窗，验收必须同时报「4K 基线 / 目标长度均分 / 有效长度」三列，🚫 不许只报「支持 32K」。<br>**harness（主目标：判分口径）**：本文阈值是**固定值 85.6**，不是按模型归一 ⇒ <b>动作</b>：复现时先记录「同尺寸基线在 4K 的成绩」，否则短上下文本身弱的模型会被误判成「长上下文退化」。<br>**data（辅）**：aggregation 类任务（CWE / FWE）的输入长度与答案个数绑定 ⇒ 造数据时要写清 `num_ucw ∝ context length` 的构造公式，否则难度不可比。<br>**风险**：① 评测是**合成任务**，与真实长文档理解有差距（作者自称 pressure test）；② 17 个模型的版本口径为 2024 年中；③ 有效长度的阈值选择会直接改变排名。 |
| 首次收录 | **2026-11-19**（第六十三轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（1,799）；PDF `200` / **682,955** B（`%PDF-`，<5 MB），`pdftotext` 核到 `four categories` / `13 representative tasks` / `17 long-context LMs` / `Llama2-7b model at the 4K context length as the threshold` / `85.6` / `only half of them can maintain satisfactory performance at the length of 32K` / `95.8` / `66.6` |

---

## 241. Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

| 字段 | 内容 |
|:--|:--|
| 标题 | Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve |
| 作者（前 3） | Amey Agrawal · Nitin Kedia · Ashish Panwar（et al.，共 8 位，含 Ramachandran Ramjee；Microsoft Research India · Georgia Tech） |
| 年份 | **2024**（arXiv 首次提交 **2024-03-04**，v3 2024-06-17，`cs.LG`） |
| 会议 / 期刊 | **arXiv 预印本**（arXiv `comment` 为空；OpenAlex `type=preprint`、source=arXiv ⇒ 🚫 不写会议名） |
| 被引数 | **539**（OpenAlex `10.48550/arxiv.2403.02310`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2403.02310> ｜ arXiv DOI `10.48550/arxiv.2403.02310` |
| 一句话贡献 | 把 LLM 服务的「吞吐 vs TBT 尾延迟」矛盾归因到**请求级调度**：用 **chunked-prefills**（把 prefill 切成近等大 chunk）＋ **stall-free batching**（不暂停在跑的 decode 就往 batch 里加新请求）让两者解耦；Mistral-7B 单卡 A100 服务容量 **2.6×**、Yi-34B 双卡 **3.7×**、Falcon-180B 加流水并行 **5.6×**（相对 vLLM）；并指出 chunk 取 257 比 256 慢 **32%**（tile quantization，§4.3）。 |
| 与我们工作的关系 | **harness（主目标：批量跑题的机时成本）**：<b>动作</b>：评测机的调度参数（chunk / token budget）必须写进实验记录 —— 本文实测 chunk 256→257 就有 32% 的 prefill 时间差，等于同一批题的成本差三成。<br>**pretrain（辅：推理侧成本口径）**：<b>动作</b>：报「每千次 rollout 的成本」时用 TBT SLO 约束下的**容量**（请求/秒）而不是裸吞吐，否则数字不可比。<br>**zhulong（辅）**：thinking 轴的长生成会放大 TBT 压力 ⇒ 消融表要标「生成上限」与「并发数」。<br>**风险**：① 5.6× 需要流水并行 + 多卡，单卡场景只有 2.6×；② 收益强依赖 trace 的 prompt/output 长度分布；③ token budget 由 Vidur 模拟器离线搜索，换硬件要重搜。 |
| 首次收录 | **2026-11-19**（第六十三轮） |
| 核验状态 | arXiv `id_list` `200`；OpenAlex `200`（539）；PDF `200` / **1,945,812** B（`%PDF-`，<5 MB），`pdftotext` 核到 `chunked-prefills` / `stall-free` / `2.6× higher serving capacity` / `3.7× higher serving ca-` / `5.6× gain` / `chunk size of 257 can increase prefill time by 32%` / `256` |

---

## 242. Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation

| 字段 | 内容 |
|:--|:--|
| 标题 | Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation |
| 作者（前 3） | Ofir Press · Noah A. Smith · Mike Lewis（University of Washington · Meta AI） |
| 年份 | **2021**（arXiv 首次提交 **2021-08-27**，v2 2022-04-22，`cs.CL`） |
| 会议 / 期刊 | **ICLR 2022**（PDF 页眉原文 `Published as a conference paper at ICLR 2022`；OpenAlex 记录为 arXiv 预印本，会议名以 PDF 为准） |
| 被引数 | **969**（OpenAlex `10.48550/arxiv.2108.12409`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2108.12409> ｜ arXiv DOI `10.48550/arxiv.2108.12409` |
| 一句话贡献 | 不在 embedding 里加位置向量，而在每个注意力头上加<b>静态线性偏置</b> `m · [-(i-j)]`（斜率按头几何递增），使**训练长度 1024 的 1.3B 模型外推到 2048** 时达到「在 2048 上训练的 sinusoidal 模型」同等困惑度，且训练**快 11%**、**省 11% 内存**；代价是在训练长度内略逊于学习式位置编码。 |
| 与我们工作的关系 | **pretrain（主目标：长上下文扩窗的最低成本对照）**：<b>动作</b>：扩窗对照表除 RoPE+PI / YaRN 外，必须留一行「ALiBi 从头训」作零参数基线，判据 = 目标长度上的 perplexity 与同 token 预算的 RoPE 方案差 &lt;1% 才可省掉位置编码改动。<br>**harness（辅）**：长度外推的好坏必须报「训练长度内 / 外」两组分数，否则看不出「以短换长」的代价。<br>**风险**：① 1.3B / 1024→2048 的结论，不能直接外推到 32K；② 在训练长度内仍略差于学习式位置编码（作者自报）；③ 偏置斜率按头数几何设定，换头数要重算。 |
| 首次收录 | **2026-11-19**（第六十四轮） |
| 核验状态 | arXiv abs `200`（`citation_*` 元数据：标题 / 3 作者 / 2021-08-27 / `2108.12409`）；OpenAlex `200`（969，`type=preprint`）；PDF `200` / **759,030** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `Published as a conference paper at ICLR 2022` / `length 1024 that extrapolates to input sequences of length 2048` / `training 11% faster and using 11% less memory` / `100MB of extra memory` |

---

## 243. Efficiently Scaling Transformer Inference

| 字段 | 内容 |
|:--|:--|
| 标题 | Efficiently Scaling Transformer Inference |
| 作者（前 3） | Reiner Pope · Sholto Douglas · Aakanksha Chowdhery（et al.，共 10 位，含 Jacob Devlin / James Bradbury / Jeff Dean；Google） |
| 年份 | **2022**（arXiv 首次提交 **2022-11-09**，`cs.LG`） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`；会议信息未在 PDF 核到 ⇒ 🚫 不写会议名） |
| 被引数 | **506**（OpenAlex `10.48550/arxiv.2211.05102`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2211.05102> ｜ arXiv DOI `10.48550/arxiv.2211.05102` |
| 一句话贡献 | 用**解析模型**把推理成本拆成「权重读取 / KV cache 读取 / 计算」三项，据此选 TPU v4 切片上的多维分区；在 **PaLM 540B**、2048 token 上下文下达到 **29 ms/token**（低 batch、int8 权重）与 **76% MFU**（大 batch prefill），并说明多查询注意力省下的 KV 内存可把上下文放大 **32×**。 |
| 与我们工作的关系 | **pretrain（主目标：推理侧成本预算）**：<b>动作</b>：2B 模型的 serving 预算表按「权重字节 / KV 字节 / 计算」三列拆开，先算 decode 每 token 的带宽下界，再决定是否上量化与 MQA/GQA。<br>**zhulong（辅）**：thinking 长输出的成本应按「每 token 的 KV 读取」估，而不是按 FLOPs 估。<br>**风险**：① 全部结论在 TPU v4 + PaLM 上取得，换 GPU / 换模型需重算常数；② 29 ms/token 依赖 int8 权重量化；③ 76% MFU 是大 batch prefill 口径，不等于 decode 吞吐。 |
| 首次收录 | **2026-11-19**（第六十四轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：10 位作者 / 2022-11-09 / `2211.05102`）；OpenAlex `200`（506，`type=preprint`）；PDF `200` / **1,036,959** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `29ms per token` / `76% MFU` / `PaLM 540B` / `2048-token context` / `32× larger context lengths` / `int8 weight quantization` |

---

## 244. DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving

| 字段 | 内容 |
|:--|:--|
| 标题 | DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving |
| 作者（前 3） | Yinmin Zhong · Shengyu Liu · Junda Chen（et al.，共 8 位，含 Xin Jin / Hao Zhang；Peking University · StepFun · UC San Diego） |
| 年份 | **2024**（arXiv 首次提交 **2024-01-18**，v3 2024-06-06，`cs.DC`） |
| 会议 / 期刊 | **arXiv 预印本**（OpenAlex `type=preprint`；OSDI 2024 录用信息未在 PDF 核到 ⇒ 🚫 不写会议名） |
| 被引数 | **711**（OpenAlex `10.48550/arxiv.2401.09670`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2401.09670> ｜ arXiv DOI `10.48550/arxiv.2401.09670` |
| 一句话贡献 | 把 **prefill 与 decode 拆到不同 GPU**，按应用给定的 **TTFT / TPOT** 两个 SLO 分别做资源分配与并行策略，并以 **per-GPU goodput** 为目标；在 >90% 请求满足延迟约束下，相对同卡共置系统可服务 **7.4×** 更多请求或承受 **12.6×** 更紧 SLO（13B、单卡 A100、input 512 / output 64 的对照图）。 |
| 与我们工作的关系 | **harness（主目标：跑题的机时与延迟口径）**：<b>动作</b>：批量评测报告必须分开写 `P90 TTFT` / `P90 TPOT` 与「达成率」，🚫 只报平均吞吐；不同阶段（prefill 重 / decode 重）分别选并行方案。<br>**zhulong（辅）**：thinking 长输出把负载推向 decode，应单独核算 decode 阶段的 GPU 数与 SLO；KV 传输开销要进成本表。<br>**风险**：① 7.4× / 12.6× 依赖 workload 的 prompt/output 长度分布；② 拆分本身引入 KV 传输，跨节点时可能吃掉收益；③ 论文未给出 2B 级模型结果，小模型结论需自测。 |
| 首次收录 | **2026-11-19**（第六十四轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：8 位作者 / 2024-01-18 / `2401.09670`）；OpenAlex `200`（711，`type=preprint`）；PDF `200` / **647,352** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `7.4× more requests` / `12.6× tighter SLO` / `over 90% requests` / `13B parameters` / `input length = 512 and output length = 64` / `P90 TTFT` / `P90 TPOT` |

---

## 245. Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving

| 字段 | 内容 |
|:--|:--|
| 标题 | Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving |
| 作者（前 3） | Ruoyu Qin · Zheming Li · Weiran He（et al.，共 7 位，含 Mingxing Zhang / Yongwei Wu；Moonshot AI · Tsinghua University） |
| 年份 | **2024**（arXiv 首次提交 **2024-06-24**，v5 2026-10-08，`cs.DC`） |
| 会议 / 期刊 | **ACM Transactions on Storage**（OpenAlex `type=article`、source = ACM Transactions on Storage，查询日 2026-11-19；卷期 / 页码未核 ⇒ 不写） |
| 被引数 | **345**（OpenAlex `10.48550/arxiv.2407.00079`，查询日 **2026-11-19**；**&lt;500 按「方法论常青 / 生产系统权威」收**：Kimi 的生产 serving 平台，KVCache 调度的原始系统工作） |
| arXiv / DOI | <https://arxiv.org/abs/2407.00079> ｜ arXiv DOI `10.48550/arxiv.2407.00079` |
| 一句话贡献 | 把 **KVCache 本身当调度对象**：prefill / decode 集群分离，用 GPU 集群里闲置的 CPU / DRAM / SSD 做**分层 KVCache 池**，调度器按 cache 块（而非按请求）排队，并对过载场景做**基于预测的提前拒绝**；在相同 TTFT / TBT SLO 下，模拟负载吞吐最高 **+525%**，真实负载下 Kimi 可多承接 **75%** 请求。 |
| 与我们工作的关系 | **harness（主目标：高并发跑批的成本）**：<b>动作</b>：并发压测必须同时记 `TTFT SLO` / `TBT SLO` / 前缀命中率，否则「吞吐提升」不可比；过载时用「提前拒绝」而不是排队雪崩。<br>**zhulong（辅）**：RL rollout 的并发远高于在线服务，需判断收益来自前缀复用还是调度 —— 前缀差异大时先做 P/D 拆分。<br>**风险**：① 525% 是模拟场景、与 baseline 比；② 收益依赖长上下文与前缀复用，短序列高并发场景可能不成立（作者称「excels in long-context scenarios」）；③ 论文未给 2B 级模型数据。 |
| 首次收录 | **2026-11-19**（第六十四轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：7 位作者 / 2024-06-24 / `2407.00079`）；OpenAlex `200`（345，`type=article`，ACM Transactions on Storage）；PDF `200` / **581,962** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `525% increase in throughput` / `75% more requests` / `KVCache-centric scheduler` / `prediction-based early rejection` / `excels in long-context scenarios` / `separates the prefill and decoding clusters` |

---

## 246. BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension

| 字段 | 内容 |
|:--|:--|
| 标题 | BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension |
| 作者（前 3） | Mike Lewis · Yinhan Liu · Naman Goyal（et al.，共 8 位，含 Luke Zettlemoyer；Facebook AI） |
| 年份 | **2019**（arXiv 首次提交 **2019-10-29**，`cs.CL`） |
| 会议 / 期刊 | **ACL 2020**，pp. **7871–7880**（OpenAlex `type=conference-paper`，DOI `10.18653/v1/2020.acl-main.703`） |
| 被引数 | **15,049**（OpenAlex `10.48550/arxiv.1910.13461`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1910.13461> ｜ ACL DOI `10.18653/v1/2020.acl-main.703` ｜ arXiv DOI `10.48550/arxiv.1910.13461` |
| 一句话贡献 | 把「去噪自编码器 + seq2seq」合成一个预训练配方：先对文档施加五种噪声（token masking、token deletion、sentence permutation、document rotation、text infilling，其中 span 长度取自 `Poisson(λ = 3)`），再由编码器读损坏文本、解码器**自回归重建原文**；摘要自报在生成类任务上最多 **+6 ROUGE**、在 XSum 上比回译基线 **+1.1 BLEU**，在 GLUE / SQuAD 上与 RoBERTa 可比。 |
| 与我们工作的关系 | **pretrain（主目标：去噪目标是否值得开一路）**：<b>动作</b>：2B 主线仍是 next-token；若要加一路去噪，先只开**一个**噪声函数做消融，判据写「同 token 预算下下游 NLL / 任务分」，🚫 不同时上五种。<br>**data（噪声即数据增广）**：五种噪声等于五种「破坏—重建」样本构造法 ⇒ <b>动作</b>：data 线把「注入噪声」单列为可开关的增广步骤，报表记 `noise_type` 与 `span_lambda`，便于与干净数据对照。<br>**harness（评测口径）**：BART 的生成增益集中在摘要/翻译类，不是所有任务 ⇒ <b>动作</b>：评测报表按任务族分组，🚫 用单一均分宣称「预训练更好」。<br>**风险**：① 15,049 是 OpenAlex ACL 记录口径；② 论文以 encoder–decoder 为主，**decoder-only 的迁移性未验证** ⇒ 我们的观察：不能直接把「+6 ROUGE」外推到 2B decoder-only；③ 噪声比例（如 15% 掩码）与 Poisson 参数是本文设置，不构成最优结论；④ 2019 年基线，与当今长上下文 / 代码语料不可直接比。 |
| 首次收录 | **2026-11-19**（第六十五轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：8 位作者 / 2019-10-29）；OpenAlex `200`（15,049，ACL 2020 pp. 7871–7880）；PDF `200` / **296,072** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `five noising functions` / `Poisson distribution (λ = 3)` / `15% of tokens` / `gains of up to 6 ROUGE` / `1.1 BLEU increase over` |

---

## 247. Chameleon: Mixed-Modal Early-Fusion Foundation Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Chameleon: Mixed-Modal Early-Fusion Foundation Models |
| 作者（前 3） | **Chameleon Team**（arXiv atom 仅 1 条机构署名；Meta FAIR） |
| 年份 | **2024**（arXiv 首次提交 **2024-05-16**，`cs.CV`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，source = arXiv；本线未核到正式会场版本 ⇒ 不写「某会录用」） |
| 被引数 | **1,262**（OpenAlex `10.48550/arxiv.2405.09818`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2405.09818> ｜ arXiv DOI `10.48550/arxiv.2405.09818` |
| 一句话贡献 | **早期融合（early-fusion）的 token 化混合模态模型**：图像与文本都被离散成 token，用同一个 Transformer 从零端到端训练在约 **10T** 交错的图文 token 上，因而能在任意序列里**理解并生成**图文；图像 tokenizer 把 **512×512** 编码为 **1024** 个 token（码本 **8192**）；摘要自报在图像描述上 SOTA、纯文本任务强于 Llama-2 并与 Mixtral 8x7B / Gemini-Pro 竞争，同时具备非平凡图像生成能力；正文报告 **Chameleon-34B** 与 QK-Norm / dropout 的稳定性消融。 |
| 与我们工作的关系 | **vision（主目标：视觉塔是否必须单独存在）**：<b>动作</b>：视觉线保留「独立编码器 + 适配器」与「统一 token 词表」两条对照，判据写「同参数、同 token 预算下的稠密任务分 + 训练是否发散」，🚫 只按生成样例好看选型。<br>**pretrain（训练稳定性）**：本文把 QK-Norm 与 dropout 作为防发散手段并给出 7B 消融 ⇒ <b>动作</b>：长跑前先在 7B 级开/关 QK-Norm 各跑一个短程点，记录输出范数曲线；范数失控即判红。<br>**data（token 预算）**：约 10T 混合模态 token、其中文本约 2.9T ⇒ <b>动作</b>：data 配比报表区分「文本 token / 图像 token」，🚫 把图像 token 计入文本预算。<br>**harness（多模态评测）**：本文同时报 VQA、captioning、纯文本与混合生成 ⇒ <b>动作</b>：多模态报表分四组，缺组不与其他模型排名。<br>**风险**：① 25,245,551 B PDF **>5 MB**，本轮未落盘，数字取自 **ar5iv HTML `200` / 476,680 B** 与 arXiv abs 摘要，⚠️ 未做 PDF 逐页复核；② 模型未开放权重 ⇒ 无法复现；③ 「SOTA / 强于 Llama-2」为作者自报；④ 早期融合对图像 tokenizer 质量高度敏感（本文自训 tokenizer），我们的观察：换 tokenizer 结论可能反转。 |
| 首次收录 | **2026-11-19**（第六十五轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：`Chameleon Team` / 2024-05-16）；OpenAlex `200`（1,262，`type=preprint`）；正文数字经 ar5iv HTML `200`（`Chameleon-34B` / `∼10T tokens` / `1024 discrete tokens` / `codebook of size 8192` / `2.9 trillion text-only tokens` / `QK-Norm` / `dropout`）；⚠️ PDF `Content-Length` 25,245,551 B >5 MB，本轮**未完整下载**（不写「PDF 已核」） |

---

## 248. Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond |
| 作者（前 3） | Jinze Bai · Shuai Bai · Shusheng Yang（et al.，共 9 位；Alibaba Group） |
| 年份 | **2023**（arXiv 首次提交 **2023-08-24**，`cs.CV`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，source = arXiv；本线未核到正式会场版本 ⇒ 不写「某会录用」） |
| 被引数 | **5,222**（OpenAlex `10.48550/arxiv.2308.12966`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2308.12966> ｜ arXiv DOI `10.48550/arxiv.2308.12966` |
| 一句话贡献 | 在 Qwen-LM 上加**视觉受体（visual receptor）**：语言对齐的视觉编码器 + **位置感知适配器（position-aware adapter）**，把图像分辨率从 **224×224** 提到 **448×448** 以减少下采样信息损失，并用「图像—描述—框」三元组对齐出**定位与读字**能力；总参数 **9.6B**（视觉 **1.9B** + 适配器 **0.08B** + LLM **7.7B**），三阶段训练；框坐标归一化到 **[0, 1000)** 后以字符串形式生成。 |
| 与我们工作的关系 | **vision（主目标：分辨率与定位的接口设计）**：<b>动作</b>：视觉线做「固定 224 / 448 / 原生动态分辨率」三臂时，必须同时报「读字类（OCR / 文档）」与「定位类（框 IoU）」两组指标，🚫 只看 VQA 均分；框输出统一用归一化整数串，便于与工具链对接。<br>**harness（判分口径）**：框是**字符串生成**，格式错与定位错要分开记 ⇒ <b>动作</b>：judge 先校验格式合法率，再算 IoU；两列都进报表。<br>**designflow（读图入口）**：版图 / 波形 / 报告截图属于高分辨率读字任务 ⇒ <b>动作</b>：designflow 的 L1–L2 题允许「视觉输入」时，必须给原始分辨率与切图策略，否则不可比。<br>**data（图文框三元组）**：本文用 image-caption-box 对齐构造监督 ⇒ <b>动作</b>：data 线的域内图文对若含版图/器件标注，优先保留**框级**标注而不是只留整图描述。<br>**风险**：① PDF `Content-Length` **6,329,953 B >5 MB**，本轮未完整下载，数字取自 **ar5iv HTML `200` / 335,271 B** 与 abs 摘要；② 9.6B 为 2023 版设置；③ 预印本，未经同行评审版本核对；④ 「new records」为作者自报，🚫 写成第三方 SOTA。 |
| 首次收录 | **2026-11-19**（第六十五轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：9 位作者 / 2023-08-24）；OpenAlex `200`（5,222，`type=preprint`）；正文数字经 ar5iv HTML `200`（`1.9B 0.08B 7.7B 9.6B` / `448 × 448` / `[0, 1000)` / `position-aware adapter` / `three-stage training`）；⚠️ PDF 6,329,953 B >5 MB，本轮**未完整下载** |

---

## 249. RWKV: Reinventing RNNs for the Transformer Era

| 字段 | 内容 |
|:--|:--|
| 标题 | RWKV: Reinventing RNNs for the Transformer Era |
| 作者（前 3） | Bo Peng · Eric Alcaide · Quentin Anthony（et al.，共 **34** 位；EleutherAI / 多机构） |
| 年份 | **2023**（arXiv 首次提交 **2023-05-22**，`cs.CL`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，source = arXiv；本线未核到正式会场版本 ⇒ 不写「某会录用」） |
| 被引数 | **830**（OpenAlex `10.48550/arxiv.2305.13048`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2305.13048> ｜ arXiv DOI `10.48550/arxiv.2305.13048` |
| 一句话贡献 | 用 **time mixing + channel mixing** 两种块把注意力换成**线性注意力**，使序列建模可写成 RNN 递推（推理复杂度 `O(Td)`，对照 Transformer 的 `O(T²d)`），训练时仍能**时间并行**；给出 169M–14B 的参数表，在 Pile 上训练 **330B token**（1 epoch）、上下文 1024，并做 1024→2048→4096→8192 的**上下文扩展续训**（10B / 100B token 级）与 LRA 评测。 |
| 与我们工作的关系 | **pretrain（主目标：线性注意力的成本—质量对照）**：<b>动作</b>：2B 若考虑线性/混合注意力，必须在同 token 预算下同时报「Pile 式验证 loss + 长上下文外推曲线 + 推理每 token 时间」，🚫 只报 speedup；上下文扩展用「逐级续训」而不是一步到位，并记录每级 token 数。<br>**zhulong（成本口径）**：`O(Td)` vs `O(T²d)` 的差异在 8K+ 才显著 ⇒ <b>动作</b>：成本报表按序列长度分档（≤2K / 8K / 32K）给「每 token 时间」，避免平均掩盖交叉点。<br>**harness（长上下文评测）**：本文用 LRA 与 Pile loss，不等于长文档任务能力 ⇒ <b>动作</b>：长上下文验收必须另加真实长文档任务，LRA 只作参考。<br>**data（训练配比）**：330B token、单 epoch、1024 上下文 ⇒ <b>动作</b>：与 2B 的 token 预算对照时注明「epoch 数与上下文长度」，🚫 直接比 loss。<br>**风险**：① 与 Transformer 的对照以 2023 年基线与 Pile 为背景；② 摘要强调效率，质量差距需看具体任务；③ 34 位作者、多机构，贡献分工未逐条核；④ 预印本。 |
| 首次收录 | **2026-11-19**（第六十五轮） |
| 核验状态 | arXiv abs `200`（`citation_*`：34 位作者 / 2023-05-22）；OpenAlex `200`（830，`type=preprint`）；PDF `200` / **1,590,242** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `linear attention` / `Channel Mixing` / `169 M` / `3B` / `7B` / `14B` / `330 billion tokens` / `context length of 1024` / `O(Td)` |

---

## 250. Universal Language Model Fine-tuning for Text Classification

| 字段 | 内容 |
|:--|:--|
| 标题 | Universal Language Model Fine-tuning for Text Classification |
| 作者（前 3） | Jeremy Howard · Sebastian Ruder（共 2 位；fast.ai / University of Washington） |
| 年份 | **2018**（arXiv 首次提交 **2018-01-18**，`cs.CL`） |
| 会议 / 期刊 | **ACL 2018**，pp. **328–339**（OpenAlex `type=conference-paper`，source = Proceedings of the ACL Meeting，DOI `10.18653/v1/P18-1031`） |
| 被引数 | **6,245**（OpenAlex `10.48550/arxiv.1801.06146`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1801.06146> ｜ ACL DOI `10.18653/v1/P18-1031` ｜ arXiv DOI `10.48550/arxiv.1801.06146` |
| 一句话贡献 | 提出**三阶段迁移学习**（通用域 LM 预训练 → 目标任务 LM 微调 → 分类器微调），并把「怎么微调」拆成三个可复用的手段：**discriminative fine-tuning**（每层不同学习率，下层取 `η_{l-1} = η_l / 2.6`）、**slanted triangular learning rates**（`cut_frac = 0.1`、`ratio = 32`）、**gradual unfreezing**（从最后一层起逐层解冻，每解冻一层训 1 epoch）；预训练语料 Wikitext-103（**28,595** 篇 / **103M** 词），分类器微调 **50 epochs**，摘要自报在 6 个文本分类数据集上相对错误率下降 **18–24%**。 |
| 与我们工作的关系 | **pretrain（主目标：小数据域内微调的配方）**：<b>动作</b>：2B 主线做域内 SFT 时，把「分层学习率倍数」与「是否逐层解冻」做成两个独立开关，各跑一个短程点；判据 = 同 token 预算下域内任务分与通用能力回退，🚫 只报域内涨点。<br>**data（小样本 epoch 预算）**：本文在 30k 级样本上分类器训 50 epochs 不过拟合、更大数据集可以更久 ⇒ <b>动作</b>：data 线报表新增「样本量 × epoch 上限」对照，避免把大语料 epoch 数直接搬到小语料。<br>**harness（复现口径）**：三阶段配方的效果依赖预训练 LM 的域与规模 ⇒ <b>动作</b>：任何「分层学习率有效」的结论必须同时给预训练语料规模，否则不可比。<br>**风险**：① 预训练规模仅 103M 词，与当今万亿 token 预训练不可直接比；② 模型是 LSTM（AWD-LSTM），**decoder-only Transformer 的迁移性未验证** ⇒ 我们的观察：不能直接外推 `η/2.6` 与 `cut_frac=0.1`；③ 18–24% 为作者自报，未第三方复现；④ 2018 年基线。 |
| 首次收录 | **2026-11-19**（第六十六轮） |
| 核验状态 | arXiv `id_list` `200`（2 位作者 / 2018-01-18）；OpenAlex `200`（**6,245**，ACL 2018 pp. 328–339）；PDF `200` / **979,417** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `28,595 preprocessed Wikipedia articles and 103 million words` / `cut f rac = 0.1, ratio = 32` / `η l /2.6` / `one epoch` / `50 epochs` / `error reduction of 18-24%` |

---

## 251. Dense Passage Retrieval for Open-Domain Question Answering

| 字段 | 内容 |
|:--|:--|
| 标题 | Dense Passage Retrieval for Open-Domain Question Answering |
| 作者（前 3） | Vladimir Karpukhin · Barlas Oğuz · Sewon Min（et al.，共 8 位，含 Danqi Chen、Wen-tau Yih；Facebook AI / University of Washington / Princeton） |
| 年份 | **2020**（arXiv 首次提交 **2020-04-10**，`cs.CL`） |
| 会议 / 期刊 | **EMNLP 2020**，pp. **6769–6781**（OpenAlex `type=conference-paper`；DOI `10.18653/v1/2020.emnlp-main.550`；⚠️ 本线 15:0x 草稿备注曾误写「ACL 2020」⇒ 以 OpenAlex 的 EMNLP 记录为准） |
| 被引数 | **8,667**（OpenAlex `10.48550/arxiv.2004.04906`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2004.04906> ｜ EMNLP DOI `10.18653/v1/2020.emnlp-main.550` ｜ arXiv DOI `10.48550/arxiv.2004.04906` |
| 一句话贡献 | 用**双塔（dual-encoder）**做段落检索：问题与段落各过一个 BERT 编码器，训练目标是对比学习，**负例构造**是核心贡献——**in-batch negatives**（batch 内其它问题的正段落当负例）+ 每条问题**额外 1 个 BM25 检索到的难负例**，batch size **128**；摘要自报在 top-20 段落检索准确率上比 Lucene-BM25 **绝对提升 9%–19%**，Top-5 准确率 **65.2% vs 42.9%**，下游 QA 端到端也优于 ORQA；重排时对 BM25 与 DPR 的分数用 **λ = 1.1** 融合。 |
| 与我们工作的关系 | **data（主目标：检索语料的负例构造）**：<b>动作</b>：domain 检索语料（工具手册 / 时序报告）建索引时，负例策略写成显式配置 `in_batch` / `bm25_per_query` / `batch_size`，先做「只 in-batch」与「in-batch + 1 BM25」两档对照，判据 = top-k 命中率与下游任务分。<br>**harness（检索指标口径）**：top-20 / top-100 与 Top-5 是不同量纲 ⇒ <b>动作</b>：报表固定写「k 值 + 数据集 + 是否含 BM25 重排」，🚫 只写「检索更好」。<br>**designflow（读手册找参数）**：芯片设计问题常是「某参数在哪个文档哪一节」⇒ <b>动作</b>：designflow 的 L1 题可先用本方法做检索臂，记录「命中段落是否含答案 span」而不是只看答案对错。<br>**风险**：① 8,667 为 OpenAlex 口径；② 预训练编码器是 BERT-base，与当今 2B 级 LLM 的 embedding 不能直接比；③ 双塔对**领域漂移**（索引由旧编码器建、查询用新编码器）的鲁棒性本文未系统评估；④ 9%–19% 为作者自报。 |
| 首次收录 | **2026-11-19**（第六十六轮） |
| 核验状态 | arXiv `id_list` `200`（8 位作者 / 2020-04-10）；OpenAlex `200`（**8,667**，EMNLP 2020 pp. 6769–6781）；PDF `200` / **383,508** B（`%PDF-`，本地字节 = 远程 `Content-Length`），`pdftotext` 核到 `9%-19% absolute in terms of top-20 passage retrieval accuracy` / `65.2% vs. 42.9% in Top-5 accuracy` / `one additional BM25 negative passage per question` / `batch size of 128` / `In-batch negatives` / `λ = 1.1` |

---

## 252. SpecAugment: A Simple Data Augmentation Method for Automatic Speech Recognition

| 字段 | 内容 |
|:--|:--|
| 标题 | SpecAugment: A Simple Data Augmentation Method for Automatic Speech Recognition |
| 作者（前 3） | Daniel S. Park · William Chan · Yu Zhang（et al.，共 7 位，含 Quoc V. Le；Google Brain） |
| 年份 | **2019**（arXiv 首次提交 **2019-04-18**，`eess.AS`） |
| 会议 / 期刊 | **Interspeech 2019**，pp. **2613–2617**（OpenAlex `type=conference-paper`；arXiv DOI `10.48550/arxiv.1904.08779`） |
| 被引数 | **4,968**（OpenAlex `10.48550/arxiv.1904.08779`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/1904.08779> ｜ arXiv DOI `10.48550/arxiv.1904.08779` |
| 一句话贡献 | 把语音识别的数据增广做成**直接在 log-mel 频谱上施加的三种形变**：time warping（时间轴弯折）、frequency masking（掩掉连续 mel 通道）、time masking（掩掉连续时间步），可在线施加；给出四条手工策略的参数表（**LB** = `W 80 / F 27 / m_F 1 / T 100 / p 1.0 / m_T 1`，**LD** 同参但双掩码，**SM/SS** = `W 40` 配 `F 15/27`、`T 70`、`p 0.2`），在 LAS 网络上使 LibriSpeech test-other **6.8% WER**（无 LM）/ **5.8%**（shallow fusion），对照此前混合系统 **7.5%**；Switchboard 达 **7.2% / 14.6%**。 |
| 与我们工作的关系 | **data（主目标：域内数据的「破坏—重建」增广）**：<b>动作</b>：把增广写成可开关步骤并带参数四元组 `(W, F, m, T)`，先在窄域小样本上做「无增广 / 单掩码 / 双掩码」三档，判据 = 域内任务分 + 过拟合间隔（train-val gap），🚫 不看训练 loss。<br>**pretrain（正则化视角）**：本文的增益来自「输入空间遮挡」而非新数据 ⇒ <b>动作</b>：若 2B 训练后期出现记忆化，可试结构化遮挡（如屏蔽固定宽度的时间/频率带），并记录与 dropout 的叠加效应。<br>**vision（类比迁移）**：掩块 = Cutout 的谱域版本 ⇒ <b>动作</b>：视觉线做 patch 遮挡增广时，直接借用其「策略表 + 参数」形式，先固定一档再调。<br>**harness（指标口径）**：语音任务报 WER 且区分「有无 LM」⇒ <b>动作</b>：任何「增广有效」的结论必须标注是否用了外部 LM / 重排，否则不可比。<br>**风险**：① 结果是语音识别任务，**与文本 / 多模态 LLM 的迁移性未验证** ⇒ 我们的观察：只能借「策略表化」的做法，不能借具体参数；② 4,968 为 OpenAlex 口径；③ 2019 年基线，LAS 架构已被取代；④ 6.8% / 5.8% 为作者自报。 |
| 首次收录 | **2026-11-19**（第六十六轮） |
| 核验状态 | arXiv `id_list` `200`（7 位作者 / 2019-04-18）；OpenAlex `200`（**4,968**，Interspeech 2019 pp. 2613–2617）；⚠️ PDF `Content-Length` **3,733,556** B，本轮下载中途被截断（本地 1,683,456 B，`pdftotext` 报 `Couldn't read xref table`）⇒ **未做 PDF 逐页复核**，Table 1 参数与 WER 数字改由 **ar5iv HTML `200` / 172,404 B** 核对（`LB 80 27 1 100 1.0 1` / `LD 80 27 2 100 1.0 2` / `SM 40 15 2 70 0.2 2` / `SS 40 27 2 70 0.2 2` / `6.8% WER on test-other` / `5.8% WER with shallow fusion` / `7.5% WER`） |

---

## 253. s1: Simple test-time scaling

| 字段 | 内容 |
|:--|:--|
| 标题 | s1: Simple test-time scaling |
| 作者（前 3） | Niklas Muennighoff · Zitong Yang · Weijia Shi（et al.，共 10 位，含 Li Fei-Fei、Luke Zettlemoyer、Percy Liang、Tatsunori Hashimoto；机构未逐人核） |
| 年份 | **2025**（arXiv 首次提交 **2025-01-31**，最新版 v3 2025-03-01，`cs.CL`） |
| 会议 / 期刊 | **EMNLP 2025** main，pp. **20286–20332**（OpenAlex `type=conference-paper`，DOI `10.18653/v1/2025.emnlp-main.1025`） |
| 被引数 | **1,939**（OpenAlex `10.48550/arxiv.2501.19393`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2501.19393> ｜ EMNLP DOI `10.18653/v1/2025.emnlp-main.1025` ｜ arXiv DOI `10.48550/arxiv.2501.19393` |
| 一句话贡献 | 用**最小配方**复现 o1 式测试时扩展：① 只造 **1,000** 道题（`s1K`，按 difficulty / diversity / quality 三条准则筛，并逐条做消融验证）；② 提出 **budget forcing** —— 在解码期强制设定思考 token 的**上界 `a_max` 与下界 `a_min`**（超限就追加 end-of-thinking token 强制收束，不足则在模型想结束时反复追加 `"Wait"` 让它继续想）；③ 在 `Qwen2.5-32B-Instruct` 上做 SFT 得 `s1-32B`，摘要自报在 MATH / AIME24 竞赛题上比 o1-preview **最高 +27%**，且仅靠 budget forcing 就把 AIME24 从 **50% 提到 57%**。 |
| 与我们工作的关系 | **zhulong（主目标：thinking 轴的显式预算）**：<b>动作</b>：thinking/语言消融里把「思考 token 上界」设为独立变量（如 1k / 4k / 16k 三档），判据 = 同题集准确率 vs 平均思考 token 数（画曲线，不报单点），并记录**强制截断导致的空答案率**。<br>**harness（评测口径）**：本文所有增益都在「给多少思考预算」下成立 ⇒ <b>动作</b>：agent 评测报表固定写 `预算档位 + 是否触发截断`，🚫 把不同预算的分数放同一列比。<br>**designflow（推理长度与题难度的匹配）**：`"Wait"` 续想能纠正中间步骤 ⇒ <b>动作</b>：L3–L5 难题可试「低预算先出答案、再按需续想」的两段式，判据 = 最终可验证通过率与 token 成本。<br>**风险**：① 只在 Qwen2.5 一个模型族 + 1,000 题上验证；② `+27%`、`50%→57%` 均**作者自报**，未第三方复现；③ budget forcing 依赖模型自身的 end-of-thinking token，换 base 模型未必有该 token；④ 强制截断会产生「想一半就答」的失败模式，本文未给该失败率。 |
| 首次收录 | **2026-11-19**（第六十七轮） |
| 核验状态 | arXiv `id_list` `200`（10 位作者 / 2025-01-31，最新 v3）；OpenAlex `200`（**1,939**，EMNLP 2025 pp. 20286–20332）；PDF `200` / **1,368,920** B 但文件**无 `%%EOF`（下载中途截断）⇒ `pdftotext` 失败**，故数字改由 **ar5iv HTML `200` / 731,343 B** 的摘要与正文核对（`1,000` / `budget forcing` / `"Wait"` / `27%` / `50% to 57%`），并如实标注「未做 PDF 逐页复核」。 |

---

## 254. Gemma 2: Improving Open Language Models at a Practical Size

| 字段 | 内容 |
|:--|:--|
| 标题 | Gemma 2: Improving Open Language Models at a Practical Size |
| 作者（前 3） | Gemma Team · Morgane Riviere · Shreya Pathak（et al.；Google DeepMind） |
| 年份 | **2024**（arXiv 首次提交 **2024-07-31**，最新版 v3 2024-10-02，`cs.CL`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，source = arXiv；本线未核到正式会场版本 ⇒ 不写「某会录用」） |
| 被引数 | **3,891**（OpenAlex `10.48550/arxiv.2408.00118`，查询日 **2026-11-19**；S2 / Google Scholar 未查） |
| arXiv / DOI | <https://arxiv.org/abs/2408.00118> ｜ arXiv DOI `10.48550/arxiv.2408.00118` |
| 一句话贡献 | 2B / 9B / 27B 三档开放权重模型，给出**三处工程化改动**：① 每两层**交替**插一层局部滑窗注意力与一层全局注意力（局部窗口 **4096** token，全局跨度 **8192** token，上下文总长 **8192**）；② 用 **GQA** + RoPE；③ **2B 与 9B 不用 next-token prediction，改用知识蒸馏**训练（用大模型当教师，「simulate training beyond the number of available tokens」），另加 **logit soft-capping**（`logits ← soft_cap · tanh(logits/soft_cap)`，注意力层 `soft_cap=50.0`、最终层 `30.0`）；27B 为从零训练。 |
| 与我们工作的关系 | **pretrain（主目标：蒸馏替代 NTP 的可行性）**：<b>动作</b>：2B 主线先做「NTP vs 蒸馏自 27B/更大教师」二选一的小规模对照，判据 = 同算力下验证集 NLL + 下游分 + 训练是否发散；🚫 只看 loss 曲线。<br>**pretrain（注意力成本）**：局部滑窗 4096 + 全局 8192 的 1:1 交错是「省 KV 又不丢全局」的现成配方 ⇒ <b>动作</b>：长上下文实验组把「交错比」做成 1:1 与 3:1 两档，判据 = 同显存下的有效上下文长度与 RULER 类分数。<br>**harness（数值稳定口径）**：`soft_cap` 属「改数值范围」而非「改目标函数」⇒ <b>动作</b>：训练报表新增「logit 分位数 + 是否 soft-cap」，便于跨配方对比发散。<br>**风险**：① 蒸馏配方依赖**未公开的教师**，外部无法完全复现；② 8192 上下文相对当今 128K 偏短；③ 3,891 为 OpenAlex 口径，不同源不可比；④ 全部数字为作者自报。 |
| 首次收录 | **2026-11-19**（第六十七轮） |
| 核验状态 | arXiv `id_list` `200`（`Gemma Team` + 个人作者，2024-07-31，最新 v3）；OpenAlex `200`（**3,891**，`type=preprint`）；PDF `200` / **610,320** B（`%PDF-`，文件以 `%%EOF` 收尾），`pdftotext` 逐项核到 `8192` / `4096` / `alternate between a local sliding window attention … and global attention in every other` / `soft_cap parameter to 50.0 for the selfattention layers and to 30.0 for the final layer` / `2B and 9B models with knowledge distillation`。 |

---


## 255. Byte Latent Transformer: Patches Scale Better Than Tokens

| 字段 | 内容 |
|:--|:--|
| 标题 | Byte Latent Transformer: Patches Scale Better Than Tokens |
| 作者（前 3） | Artidoro Pagnoni · Ram Pasunuru · Pedro Rodriguez（et al.，共 14 位，含 Jason Weston、Luke Zettlemoyer、Srinivasan Iyer；机构未逐人核） |
| 年份 | **2024**（arXiv 首次提交 **2024-12-13**，v1，`cs.CL`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，source = arXiv；本线未核到正式会场版本） |
| 被引数 | **144**（OpenAlex `10.48550/arxiv.2412.09871`，查询日 **2026-11-19**；**&lt;500 ⇒ 按「开创范式」收录**：号称首个在规模上追平 tokenization 的**字节级** LLM，且给出首个 FLOP 受控的字节级 scaling study） |
| arXiv / DOI | <https://arxiv.org/abs/2412.09871> ｜ arXiv DOI `10.48550/arxiv.2412.09871` |
| 一句话贡献 | 取消固定词表：先把字节流切成**动态大小的 patch**，切分依据是**下一个字节的熵**（熵高处切短、可预测处切长），patch 成为真正的计算单元；摘要自报做**首个 FLOP 受控的字节级 scaling 研究，最大到 8B 参数 / 4T 训练字节**，在固定推理成本下同时增大 patch 与模型规模，扩展性优于 tokenization 模型，并在推理效率与长尾鲁棒性上更好。 |
| 与我们工作的关系 | **pretrain（主目标：词表是否必需）**：<b>动作</b>：2B 主线**不**立即换架构，先在评测侧加一条「同文本、不同分词器（原生 BPE vs 自训 BPE）」的敏感性对照，判据 = 同题分数的方差；若分词器敏感度过高，再把 BLT 式熵切分列为下一阶段候选。<br>**data（分词器不再是数据前置）**：字节级意味着**拼写错误 / 稀有标识符 / 代码符号**不再被 `<unk>` 吞掉 ⇒ <b>动作</b>：data 线在清洗报表里新增「被 tokenizer 切碎比例」这一列（EDA 网表名、Verilog 宏名尤甚）。<br>**harness（判分口径）**：字节级模型的输出可能不落在合法 token 边界 ⇒ <b>动作</b>：判分器不得假设「输出可被同一 tokenizer 无损还原」，需加一层字节级校验。<br>**风险**：① 144 引用、2024-12 预印本，社区复现少；② 熵切分需先有一个 next-byte 预测器，工程复杂度高于 BPE；③ `8B / 4T bytes` 仍小于主流 token 级训练规模，规模外推未证；④ 全部数字作者自报。 |
| 首次收录 | **2026-11-19**（第六十七轮） |
| 核验状态 | arXiv `id_list` `200`（14 位作者 / 2024-12-13）；OpenAlex `200`（**144**，`type=preprint`）；PDF `200` / **839,117** B 但文件**无 `%%EOF`（下载中途截断）⇒ `pdftotext` 失败**，故只用 arXiv 官方摘要（`entropy of the next byte` / `8B parameters and 4T training bytes` / `dynamically sized patches`）核对，并如实标注「未做 PDF 逐页复核」。 |

---

## 256. TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks

| 字段 | 内容 |
|:--|:--|
| 标题 | TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks |
| 作者（前 3） | Frank F. Xu · Yufan Song · Boxuan Li（et al.，共 21 位，末位 Graham Neubig；一作现为 Microsoft AI） |
| 年份 | **2024**（arXiv 首次提交 **2024-12-18**，最新版 v3 2025-09-10，`cs.CL`） |
| 会议 / 期刊 | **NeurIPS 2025**，pp. **10291–10321**（OpenAlex `type=conference-paper`，DOI `10.52202/085713-0315`；本线未核具体 track） |
| 被引数 | **465**（OpenAlex `10.48550/arxiv.2412.14161`，查询日 **2026-11-19**；**&lt;500 ⇒ 按「本领域权威 / 方法论常青」收录**：长程「数字员工」型 agent 评测的代表性基座） |
| arXiv / DOI | <https://arxiv.org/abs/2412.14161> ｜ NeurIPS DOI `10.52202/085713-0315` ｜ arXiv DOI `10.48550/arxiv.2412.14161` |
| 一句话贡献 | 建一个**自包含的模拟小软件公司**（内部网站 + 内部数据，可离线跑），任务要求 agent 像数字员工一样**浏览网页、写代码、跑程序、与同事沟通**；用闭源 API 与开放权重两类模型做基线，摘要自报**最强 agent 只能自主完成 30% 的任务**，并指出「简单任务可自动、长程难任务仍不可及」。 |
| 与我们工作的关系 | **harness（主目标：长程任务的评测形态）**：<b>动作</b>：agent 评测除单轮 QA 外，补一组「多步 + 跨工具 + 需检查产物」的任务，判据 = 端到端完成率 + 每步可核验证据（文件 / 命令输出），🚫 只用最终答案字符串判分。<br>**designflow（流程同构）**：本文任务形态（读文档 → 改代码 → 跑工具 → 看结果 → 汇报）与 EDA 流程几乎一一对应 ⇒ <b>动作</b>：designflow 的 L4/L5 题直接照此拆「环境 + 可核验产物 + 沟通件」，判分只看环境内产物。<br>**harness（口径）**：`30%` 是「自主完成率」而非「部分得分」⇒ <b>动作</b>：我们报表必须同时给「全自动完成率」与「人机协作后完成率」，🚫 混称「通过率」。<br>**风险**：① 30% 随模型版本变化，且为作者自报；② 模拟公司与真实企业流程有差距（内部系统是简化版）；③ 任务总数 / 难度分层本轮未从 PDF 核实（PDF 截断）。 |
| 首次收录 | **2026-11-19**（第六十七轮） |
| 核验状态 | arXiv `id_list` `200`（21 位作者 / 2024-12-18，最新 v3 2025-09-10）；OpenAlex `200`（**465**，NeurIPS 2025 pp. 10291–10321）；PDF `200` / **1,183,809** B 但文件**无 `%%EOF`（下载中途截断）⇒ `pdftotext` 失败**，故只用 arXiv 官方摘要（`30% of tasks autonomously` / `browsing the Web, writing code, running programs, and communicating`）核对，并如实标注「未做 PDF 逐页复核」。 |

---


## 257. Scalable Diffusion Models with Transformers (DiT)

| 字段 | 内容 |
|:--|:--|
| 标题 | Scalable Diffusion Models with Transformers |
| 作者（前 3） | William Peebles · Saining Xie（共 2 位；两位均已在 `AUTHORS.md` 建档：#52 Bill Peebles / X 表 V-48 Saining Xie） |
| 年份 | **2022**（arXiv 首次提交 **2022-12-19**，最新版 v2 2026-11-19，`cs.CV`） |
| 会议 / 期刊 | **ICCV 2023**，pp. **4172–4182**（OpenAlex `type=conference-paper`，DOI `10.1109/iccv51070.2023.00387`） |
| 被引数 | **9,393**（OpenAlex `10.48550/arxiv.2212.09748`，查询日 **2026-11-19**） |
| arXiv / DOI | <https://arxiv.org/abs/2212.09748> ｜ ICCV DOI `10.1109/iccv51070.2023.00387` ｜ arXiv DOI `10.48550/arxiv.2212.09748` |
| 一句话贡献 | 把扩散模型的 **U-Net 主干换成 Transformer**（在 VAE 潜空间的 patch 序列上跑），并用 **前向 Gflops** 作为可比的规模尺：同 Gflops 的不同宽/深/patch 配置 FID 接近；DiT-XL/2（**118.6 Gflops**）在类别条件 ImageNet **256×256 上 FID 2.27**（摘要自报 SOTA），512×512 上 DiT-XL/2-G（cfg=1.50）FID **3.04**（表 3）。 |
| 与我们工作的关系 | **vision（主目标：视觉/生成主干选型）**：<b>动作</b>：视觉塔与生成头的对照实验统一以「同 Gflops」而非「同参数量」对齐预算，报表同时给参数量与 Gflops（#257 图 8 的核心口径）。<br>**pretrain（规模尺）**：<b>动作</b>：2B 主线的消融表加一列「前向 Gflops / token」，避免「加宽 vs 加 token」两类改动被误读为同一类 scaling。<br>**data（patch 即分词）**：<b>动作</b>：若做图像/版图生成原型，先固定 `p=2/4/8` 三档 patch 做小规模对照，判据 = 同 Gflops 下 FID/重构误差，而不是先调深度。<br>**风险**：① FID 为作者自报、本线未复现；② DiT 的结论建立在类别条件 ImageNet 与 VAE 潜空间上，迁移到版图/波形需重做基线；③ 43,824,062 B 的 PDF（含附录）**>5 MB 未落盘**，数字取自 arXiv 摘要与 ar5iv 正文。 |
| 首次收录 | **2026-11-19**（第六十八轮） |
| 核验状态 | arXiv `id_list` `200`（2 位作者 / 2022-12-19 / v2 2026-11-19）；OpenAlex `200`（**9,393**，ICCV 2023 pp. 4172–4182）；ar5iv HTML `200` / **288,428 B** 核 `118.6 Gflops` / `2.27` / 表 3 `3.04`；PDF HEAD `content-length: 43,824,062` **>5 MB 未下载**（如实标注）。 |

---

## 258. DeepSeek-Coder: When the Large Language Model Meets Programming — The Rise of Code Intelligence

| 字段 | 内容 |
|:--|:--|
| 标题 | DeepSeek-Coder: When the Large Language Model Meets Programming -- The Rise of Code Intelligence |
| 作者（前 3） | Daya Guo（郭达雅）· Qihao Zhu · Dejian Yang（et al.，共 **13** 位，末位 Wenfeng Liang） |
| 年份 | **2024**（arXiv 首次提交 **2024-01-25**，最新版 v1 同日期，`cs.SE`） |
| 会议 / 期刊 | **预印本技术报告**（OpenAlex `primary_location` = arXiv，无会场 DOI） |
| 被引数 | **2,479**（OpenAlex `10.48550/arxiv.2401.14196`，查询日 **2026-11-19**） |
| arXiv / DOI | <https://arxiv.org/abs/2401.14196> ｜ arXiv DOI `10.48550/arxiv.2401.14196` |
| 一句话贡献 | 从零训练 **1.3B–33B** 开源代码模型系列，**2 万亿 token**，配比实测为 **87% 源码 / 10% 英文代码相关自然语言 / 3% 与代码无关的中文**；**首次把 repository-level 数据构造放进预训练**（作者称显著提升跨文件代码生成），并用 **16K 窗口的 fill-in-the-blank** 任务增强补全；摘要自报在多个基准上超过 Codex / GPT-3.5。 |
| 与我们工作的关系 | **data（主目标：代码语料配比与仓库级切分）**：<b>动作</b>：数据线报表把「仓库级样本占比」和「FIM 样本占比」单列，先做 0% / 10% / 30% 三档对照，判据 = 跨文件补全与单文件补全分开报（#258 的核心论点是两者不同向）。<br>**pretrain（训练目标）**：<b>动作</b>：2B 主线加一组 FIM 开关（16K 窗口按本文设置），看通用 NLL 掉多少、补全能力涨多少，做成二维表再决定是否常开。<br>**harness（代码评测口径）**：<b>动作</b>：代码题必须区分「函数级补全」与「仓库级改动」两类，🚫 用同一个 pass@1 混称。<br>**风险**：① 超越 Codex / GPT-3.5 为作者自报（2024 年时点）；② 87/10/3 是本文配比，不能直接外推到我们的中英混合 EDA 语料；③ PDF 本地 1,911,399 B 但仅 4 页、无完整 xref（下载截断）⇒ 数字取自 arXiv 摘要 + ar5iv 正文，未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-19**（第六十八轮） |
| 核验状态 | arXiv `id_list` `200`（13 位作者 / 2024-01-25）；OpenAlex `200`（**2,479**，preprint）；ar5iv HTML `200` / **324,866 B** 核 `87% source code / 10% English / 3% Chinese`、`87 programming languages`、`repository-level data construction`；PDF `200` / 1,911,399 B 但 `pdftotext` 报 xref 错误（截断）⇒ 如实标注。 |

---


## 259. Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations

| 字段 | 内容 |
|:--|:--|
| 标题 | Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations |
| 作者（前 3） | Peiyi Wang（王培懿）· Lei Li · Zhihong Shao（et al.，共 **9** 位，末位 Zhifang Sui 穗志方） |
| 年份 | **2023**（arXiv 首次提交 **2023-12-14**，最新版 v3 2024-06-07，`cs.AI`） |
| 会议 / 期刊 | **ACL 2024（Long Papers）**，pp. **9426–9439**（OpenAlex `type=conference-paper`，DOI `10.18653/v1/2024.acl-long.510`） |
| 被引数 | **1,535**（OpenAlex `10.48550/arxiv.2312.08935`，查询日 **2026-11-19**） |
| arXiv / DOI | <https://arxiv.org/abs/2312.08935> ｜ ACL DOI `10.18653/v1/2024.acl-long.510` ｜ arXiv DOI `10.48550/arxiv.2312.08935` |
| 一句话贡献 | 用「**从该步继续采样、能否推出正确答案**」的 completion/estimation 自动给每一步打标签，训练**过程奖励模型（PRM）**，从而绕开人工逐步标注；两种用法：① 对多份候选解重排（verification）；② 用逐步 PPO 直接强化。实测 Mistral-7B：逐步 PPO 使 GSM8K **77.9%→84.1%**、MATH **28.6%→33.0%**；再加验证重排到 **89.1% / 43.5%**（摘要自报）。 |
| 与我们工作的关系 | **zhulong（主目标：thinking 轴的奖励粒度）**：<b>动作</b>：把「结果奖励」与「过程奖励」做成两档对照，过程奖励先用本文的自动标注法生成（无需人工），判据 = 同采样预算下的准确率与「错误步骤被提前截断的比例」。<br>**harness（判分器）**：<b>动作</b>：agent 评测的判分器若引入 PRM，必须先测「PRM 重排是否只是长度/格式偏好」——本文用「所有步骤分数取最小值」聚合，我们应同时报 min / last / mean 三种聚合的差异。<br>**pretrain（离线数据）**：<b>动作</b>：把自动过程标签当作 posttrain 数据资产盘点（每题的标签数与采样数），避免与 pretrain token 预算混算。<br>**风险**：① 只在数学（GSM8K / MATH）验证，迁移到 EDA / 代码题未验证；② 自动标签依赖「采样可推出正确答案」这一假设，弱模型上会系统性偏悲观；③ PDF 本地 827,225 B 但仅 5 页、xref 不完整 ⇒ 数字取自 arXiv 摘要 + ar5iv 正文。 |
| 首次收录 | **2026-11-19**（第六十八轮） |
| 核验状态 | arXiv `id_list` `200`（9 位作者 / 2023-12-14 / v3 2024-06-07）；OpenAlex `200`（**1,535**，ACL 2024 pp. 9426–9439）；ar5iv HTML `200` / **156,622 B** 核四个准确率与「minimum score across all steps」；PDF `200` / 827,225 B 但 `pdftotext` 报 xref 错误（截断）⇒ 如实标注。 |

---

## 260. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

| 字段 | 内容 |
|:--|:--|
| 标题 | MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework |
| 作者（前 3） | Sirui Hong（洪思睿）· Mingchen Zhuge · Jiaqi Chen（et al.，共 **15** 位，末位 Jürgen Schmidhuber） |
| 年份 | **2023**（arXiv 首次提交 **2023-08-01**，最新版 v2 2024-01-03，`cs.AI`） |
| 会议 / 期刊 | **预印本**（OpenAlex `primary_location` = arXiv，无会场 DOI） |
| 被引数 | **2,831**（OpenAlex `10.48550/arxiv.2308.00352`，查询日 **2026-11-19**） |
| arXiv / DOI | <https://arxiv.org/abs/2308.00352> ｜ arXiv DOI `10.48550/arxiv.2308.00352` |
| 一句话贡献 | 把**人类工作的标准作业程序（SOP）编码进 prompt 序列**，用流水线给多个 agent 分配角色（产品经理 / 架构师 / 项目经理 / 工程师 / QA），让中间产物（需求文档、设计、接口）成为可校验的结构化物；作者称在协作式软件工程基准上比聊天式多 agent 更连贯，HumanEval / MBPP **Pass@1 85.9% / 87.7%**（作者自报 SoTA），完整跑一例 **503 秒**、每行代码 **126.5 / 124.3** token（对照 ChatDev 248.9）。 |
| 与我们工作的关系 | **harness（主目标：把流程当 harness 设计）**：<b>动作</b>：agent harness 的评测脚本显式记录「阶段产物」（需求/设计/补丁/测试），并把「阶段间返工次数」作为一等指标；🚫 只记最终通过率。<br>**designflow（流程同构）**：<b>动作</b>：L4/L5 造题直接借用「角色 + SOP + 结构化交付物」三件套，把 EDA 流程拆成可独立判分的阶段产物（约束文件 → 网表 → 版图 → signoff 报告）。<br>**data（中间产物即数据）**：<b>动作</b>：把多 agent 的中间产物按阶段入库并标「被下游采纳/被丢弃」，作为后续 SFT 的候选数据，而不是只留最终答案。<br>**风险**：① 85.9% / 87.7% 为作者自报，且 HumanEval/MBPP 与仓库级任务差距大；② token/时间数字随模型版本变化；③ PDF 16,753,634 B **>5 MB 未落盘**，数字取自 ar5iv 正文与摘要。 |
| 首次收录 | **2026-11-19**（第六十八轮） |
| 核验状态 | arXiv `id_list` `200`（15 位作者 / 2023-08-01 / v2 2024-01-03）；OpenAlex `200`（**2,831**，preprint）；ar5iv HTML `200` / **502,095 B** 核 `85.9% and 87.7% in Pass@1` / `503 seconds` / `126.5/124.3 tokens`；PDF HEAD `content-length: 16,753,634` **>5 MB 未下载**（如实标注）。 |

---


## 261. Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model

| 字段 | 内容 |
|:--|:--|
| 标题 | Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model |
| 作者（前 3） | Chunting Zhou · Lili Yu · Arun Babu（et al.，共 **10** 位，末位 Omer Levy；Meta FAIR） |
| 年份 | **2024**（arXiv 首次提交 **2024-08-20**，`cs.AI`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，`primary_location` = arXiv，无会场 DOI） |
| 被引数 | **588**（OpenAlex `10.48550/arxiv.2408.11039`，查询日 **2026-11-19**） |
| arXiv / DOI | <https://arxiv.org/abs/2408.11039> ｜ arXiv DOI `10.48550/arxiv.2408.11039` |
| 一句话贡献 | **同一个 Transformer 里同时跑两种损失**：文本 token 用 next-token 交叉熵、图像 patch 用扩散（连续值加噪去噪），**文本走因果注意力、图像 patch 走双向注意力**，解码时把「语言模型的文本采样」与「扩散的图像迭代去噪」拼在一个循环里；最大做到 **7B / 2T 多模态 token**（**1T 文本 + 约 5 个 epoch 的 6.92 亿图**）。与 Chameleon 的「图像离散化成 token」路线对照：**同 FLOPs 下 FID 约低 2×**，图文生文任务以 **21.8% FLOPs** 追平 Chameleon；加模态专属编解码层后每图可压到 **16 个 patch**。 |
| 与我们工作的关系 | **vision（主目标：图文是否共用一套 token 词表）**：<b>动作</b>：视觉塔与语言主干是否共享词表，先做「共享 vs 独立 + 连续 vs 离散」2×2 小规模对照，判据 = 同 FLOPs 下图文双向任务（生文 / 生图）分别报，🚫 只报单向。<br>**pretrain（注意力掩码按模态切）**：<b>动作</b>：多模态预训练 runbook 显式写清「哪些 token 因果、哪些双向」；若做混合 batch，必须记录图文 token 比与实际 FLOPs，而不是只记样本数。<br>**data（图像当连续信号）**：<b>动作</b>：图文数据管线保留连续潜变量通路（VAE 潜空间 + patchify），不强行先离散化；离散化只在「必须复用 LLM 词表」时才作为约束。<br>**风险**：① 2× FID / 21.8% FLOPs 为作者自报、本线未复现；② 对照对象是 Chameleon（同门模型），外部可比性有限；③ PDF `content-length = 14,087,563 B` **>5 MB 未落盘**，数字取自 arXiv 摘要与 ar5iv 正文。 |
| 首次收录 | **2026-11-19**（第六十九轮） |
| 核验状态 | arXiv `id_list` `200`（10 位作者 / 2024-08-20 / `cs.AI`）；OpenAlex `200`（**588**，preprint）；ar5iv HTML `200` / **300,229 B** 核 `causal attention for text tokens and bidirectional attention for image patches`、`2 ×` lower FID、`21.8% of the FLOPs`、`16 patches`、`1T text tokens` + `5 epochs of 692M images`；PDF HEAD `content-length: 14,087,563` **>5 MB 未下载**（如实标注）。 |

---

## 262. Agentless: Demystifying LLM-based Software Engineering Agents

| 字段 | 内容 |
|:--|:--|
| 标题 | Agentless: Demystifying LLM-based Software Engineering Agents |
| 作者（前 3） | Chunqiu Steven Xia · Yinlin Deng · Soren Dunn（et al.，共 **4** 位，末位 Lingming Zhang；UIUC） |
| 年份 | **2024**（arXiv 首次提交 **2024-07-01**，最新版 v2 2024-10-29，`cs.SE`） |
| 会议 / 期刊 | **PACM SE（Proc. ACM Softw. Eng.）Vol. 2, Issue FSE, pp. 801–824, 2025**（OpenAlex `type=article`） |
| 被引数 | **1,053**（OpenAlex `10.48550/arxiv.2407.01489`，查询日 **2026-11-19**） |
| arXiv / DOI | <https://arxiv.org/abs/2407.01489> ｜ arXiv DOI `10.48550/arxiv.2407.01489` |
| 一句话贡献 | 直接质疑「必须上自主 agent」：**固定三段流水线 = 定位 → 修 → 补丁验证**，不让模型自己决定下一步、也不给它复杂工具；定位是**层级式**（先文件、再类/函数、最后编辑行），检索用 LLM 提示式 + embedding 式两路合并；修补阶段采样多条 diff，并**自己生成复现测试**，与回归测试一起给候选补丁排序。SWE-bench Lite 上 **32.00%（96 个正确修复）/ 每题 $0.70**，作者称同时优于当时所有开源 agent。 |
| 与我们工作的关系 | **harness（主目标：先证「无 agent 也能行」再谈 agent 增益）**：<b>动作</b>：harness 评测必须先跑「固定流水线 + 无自主决策」基线（定位/编辑/验证三段），再跑 agent；只有 agent 相对该基线有稳定增量时才保留 agent 复杂度。<br>**designflow（流程可判分）**：<b>动作</b>：把设计任务拆成「定位到具体文件/单元 → 修改 → 用生成脚本自证修复」三段，每段单独给中间产物与判据；🚫 只判最终产物。<br>**zhulong（成本口径）**：<b>动作</b>：评测报表增加「每题美元成本 + token 数」，与通过率并列；成本随模型/接口变动，须标抓取日期。<br>**风险**：① 32.00% / $0.70 为作者自报（v2 版本；v1 曾报 27.33% / $0.34 ⇒ 引用必须写版本）；② 仅 SWE-bench Lite（300 题，Python），不可外推到 EDA / 多语言；③ 采样数、重排序模型随实现变化，复现需固定配置。 |
| 首次收录 | **2026-11-19**（第六十九轮） |
| 核验状态 | arXiv `id_list` `200`（4 位作者 / 2024-07-01 / v2 2024-10-29 / `cs.SE`）；OpenAlex `200`（**1,053**，PACM SE Vol. 2 FSE pp. 801–824, 2025）；PDF `200` / **1,384,716 B**（`%PDF-` 头已验）首页明文 `{chunqiu2, yinlind2, sorend2, lingming}@illinois.edu`；ar5iv HTML `200` / **401,375 B** 核 Table 1 的 `96 (32.00%)` / `$0.70` / `78,166` 与三段流水线描述。 |

---

## 263. Massive Activations in Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | Massive Activations in Large Language Models |
| 作者（前 3） | Mingjie Sun · Xinlei Chen · J. Zico Kolter（et al.，共 **4** 位，末位 Zhuang Liu；CMU / Meta AI / Bosch Center for AI） |
| 年份 | **2024**（arXiv 首次提交 **2024-02-27**，最新版 v2 2024-08-14，`cs.CL`） |
| 会议 / 期刊 | **预印本**（OpenAlex `primary_location` = arXiv，无会场 DOI） |
| 被引数 | **444**（OpenAlex `10.48550/arxiv.2402.17762`，查询日 **2026-11-19**；**&lt;500 按「方法论常青」收**，理由：把训练中的「激活爆值 / loss spike」落到具体层与具体通道，是排查异常激活的标准参照） |
| arXiv / DOI | <https://arxiv.org/abs/2402.17762> ｜ arXiv DOI `10.48550/arxiv.2402.17762` |
| 一句话贡献 | 记录一个跨模型族普遍存在的现象：**极少数激活值比同层其它值大 10^5 量级**（「massive activations」），位置固定在少数通道/层（如 LLaMA2-7B 的第 2 层、第 15 层一带）；**取值几乎与输入无关 ⇒ 实质是隐式 bias 项**，并把注意力概率吸到对应 token 上；人为去掉会破坏模型（CLIP ViT-L 第 13 层直接置零，ImageNet 准确率 **75.5% → 59.8%**；置为该层均值仍保持 **75.5%**）；反过来，**显式加 bias 项训练后模型就不再学出这些巨值**。 |
| 与我们工作的关系 | **pretrain（主目标：异常激活的排查口径）**：<b>动作</b>：训练监控报表新增「逐层最大激活 / 同层中位数」比值曲线，阈值先按 10^4 量级报警；出现尖峰时先看是否只落在固定通道（本现象）还是随输入漂移（更可能是真故障）。<br>**harness / zhulong（量化与压缩前置检查）**：<b>动作</b>：做激活量化 / FP8 / 剪枝前先扫一遍每层最大激活，巨值通道必须单独处理（per-channel scale），否则精度崩点难归因。<br>**vision（ViT 侧对照）**：<b>动作</b>：视觉塔异常激活出现在**较后的层**，且固定特征维、patch 位置不固定（本文 Fig. 12 / Table 4）⇒ 视觉侧监控按「特征维」聚合，不按「patch 位置」聚合。<br>**风险**：① 结论是经验观察 + 干预实验，非因果证明；② 模型族以 LLaMA2 / GPT-2 / ViT 为主，我们自研结构需自行复测；③ PDF `content-length = 7,636,655 B` **>5 MB 未落盘**，数字取自 arXiv 摘要与 ar5iv 正文。 |
| 首次收录 | **2026-11-19**（第六十九轮） |
| 核验状态 | arXiv `id_list` `200`（4 位作者 / 2024-02-27 / v2 2024-08-14 / `cs.CL`）；OpenAlex `200`（**444**，preprint）；ar5iv HTML `200` / **271,351 B** 核 `100,000 times larger`、`bias terms`、Table 4 的 `75.5 / 59.8 / 75.5`、`CLIP ViT-L, layer 13`；PDF HEAD `content-length: 7,636,655` **>5 MB 未下载**（如实标注）。 |

---

## 264. EDA Corpus: A Large Language Model Dataset for Enhanced Interaction with OpenROAD

| 字段 | 内容 |
|:--|:--|
| 标题 | EDA Corpus: A Large Language Model Dataset for Enhanced Interaction with OpenROAD |
| 作者（前 3） | Bing-Yue Wu · Utsav Sharma · Sai Rahul Dhanvi Kankipati（et al.，共 **8** 位，末位 Vidya A. Chhabria；Arizona State University · NYU） |
| 年份 | **2024**（arXiv 首次提交 **2024-05-04**，`cs.CL`） |
| 会议 / 期刊 | **IEEE LLM Aided Design Workshop (LAD) 2024**，pp. **1–5**（OpenAlex `type=conference-paper`，DOI `10.1109/lad62341.2024.10691774`） |
| 被引数 | **38**（OpenAlex `10.48550/arxiv.2405.06676`，查询日 **2026-11-19**；**&lt;500 按「本领域权威」收**，理由：EDA 侧少见的「可再分发 + OpenROAD 原生 + 判分可执行」公开语料，是设计流程 agent 造题的现成底座） |
| arXiv / DOI | <https://arxiv.org/abs/2405.06676> ｜ 会议 DOI `10.1109/lad62341.2024.10691774` ｜ arXiv DOI `10.48550/arxiv.2405.06676` |
| 一句话贡献 | 针对 OpenROAD 开源流程做**可再分发的 EDA 语料**：两种成对格式 ——（i）**问题 + 散文答案**（**198** 个唯一 QA，改写增强后近 **600** 条）、（ii）**指令 + OpenROAD Python 脚本**（含改写 prompt 与改参数/功能两类增强）；总计 **>1000** 条。判分口径值得抄：脚本类样本**必须在 OpenROAD 里真跑、按输出判对错**（单元测试式），不是比对文本；实测原始 ChatGPT-3.5/4 在脚本任务上几乎全错，微调后准确率接近一半（作者自报）。 |
| 与我们工作的关系 | **designflow（主目标：造题的「可执行判据」模板）**：<b>动作</b>：L1–L5 造题统一要求「产物可执行 + 有自动判分脚本」，脚本类题先跑通 OpenROAD/工具再入库；🚫 用文本相似度当判据。<br>**data（EDA 语料的可得性边界）**：<b>动作</b>：语料盘点表新增一列「许可是否允许再分发 / 是否可用于训练」，商业工具文档与论坛问答单列（本文正因许可问题才自建 OpenROAD 语料）。<br>**harness（增强数据的配比实验）**：<b>动作</b>：小数据域适配先做「唯一 vs 增强」两档对照，判据 = 执行通过率（不看 loss）；增强方式按「改写 prompt」与「改参数/功能」两类分别报。<br>**风险**：① 规模小（千级）且聚焦 OpenROAD 单一工具链，不可外推为「EDA 全面覆盖」；② 「接近一半」是作者自报的单次实验，无多种子；③ 会议为 workshop（LAD 2024，5 页），不是期刊长文。 |
| 首次收录 | **2026-11-19**（第六十九轮） |
| 核验状态 | arXiv `id_list` `200`（8 位作者 / 2024-05-04 / `cs.CL`）；OpenAlex `200`（**38**，IEEE LAD 2024 pp. 1–5，DOI `10.1109/lad62341.2024.10691774`）；PDF `200` / **453,822 B**（`%PDF-` 头已验；`pdftotext` 可解析 25,991 字符）核 `198 unique data points` / `nearly 600 data points` / `over 1000 data points` / `true only if the model generates a script that returns the correct result when executed in OpenROAD`。⚠️ **纠一处 ID 误记**：候选阶段曾按 `2405.07288` 取数，实测该 ID 为 *Erasing Concepts from Text-to-Image Diffusion Models with Few-shot Unlearning*（无关）⇒ 按标题检索得真 ID **`2405.06676`** 后才收录。 |

---

## 265. Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context

| 字段 | 内容 |
|:--|:--|
| 标题 | Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context |
| 作者（前 3） | Zihang Dai · Zhilin Yang · Yiming Yang（et al.，共 **6** 位，另有 Jaime Carbonell / Quoc V. Le / Ruslan Salakhutdinov；CMU · Google Brain） |
| 年份 | **2019**（arXiv 首次提交 **2019-01-09**，`cs.LG`） |
| 会议 / 期刊 | **预印本**（OpenAlex `primary_location` = arXiv，`locations` 仅 arXiv 两条、无会场 DOI ⇒ 本轮**未核**会议收录，不写会议名） |
| 被引数 | **1,881**（OpenAlex `10.48550/arxiv.1901.02860`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/1901.02860> ｜ arXiv DOI `10.48550/arxiv.1901.02860` |
| 一句话贡献 | 用**段级递归（segment-level recurrence）+ 相对位置编码**解决「固定长度上下文」与「上下文碎片化」：把前一段的隐状态缓存下来参与当前段计算，使模型学到的依赖比 RNN **长 80%**、比原版 Transformer **长 450%**，评测期比原版快最多 **1,874×**；bpc / perplexity 达 **0.99**（enwiki8）/ **1.08**（text8）/ **18.3**（WikiText-103）/ **21.8**（One Billion Word）/ **54.5**（PTB，无微调）。 |
| 与我们工作的关系 | **pretrain（主目标：长上下文的「记忆」与位置编码口径）**：<b>动作</b>：长上下文对照实验固定三档 —— ① 纯滑窗注意力；② 段级递归（缓存前段隐状态）；③ 相对位置编码 + 扩窗。判据 = 同显存下「有效依赖长度」与下游分，而非只看训练 loss。<br>**harness（评测口径）**：<b>动作</b>：长上下文题必须写明「训练注意力长度 / 评测注意力长度」（本文 **384 / 1600**），否则跨论文分数不可比。<br>**data（长文档切分）**：<b>动作</b>：切段时保留「段间重叠 + 段序信息」，与本文的 segment 递归配套；WikiText-103 的规模（28K 篇 / 103M token / 平均 3.6K token）可当切段实验的参照。<br>**风险**：① 2019 年的结果，词级 BPE 与现在的 tokenizer 不同，绝对 bpc 不可直接对比；② 1,874× 是「评测期 vs 原版逐段重算」的比值，不是端到端吞吐；③ PDF 下载被截断（无 `%%EOF`，`pdftotext` 失败）⇒ 数字取自 **ar5iv HTML**（312,920 B）与 arXiv 摘要，未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十轮） |
| 核验状态 | arXiv abs 页 `200` / 45,339 B（`citation_title` / `citation_author` ×6 / `citation_date=2019/01/09`）；OpenAlex `200`（**1,881**，仅 arXiv location）；ar5iv HTML `200` / **312,920 B** 核 `80% longer than RNNs and 450% longer than vanilla Transformers`、`1,874 times speedup`、`0.99 / 1.08 / 18.3 / 21.8 / 54.5`、`attention length to 384 during training and 1600 during evaluation`、`103M training tokens from 28K articles`、`average length of 3.6K tokens`；PDF `200` / 347,570 B 但**截断**（无 `%%EOF`、`pdftotext` 报 xref 错误）⇒ 数字以 ar5iv 为准。 |

---

## 266. Emu3: Next-Token Prediction is All You Need

| 字段 | 内容 |
|:--|:--|
| 标题 | Emu3: Next-Token Prediction is All You Need |
| 作者（前 3） | Xinlong Wang · Xiaosong Zhang · Zhengxiong Luo（et al.，BAAI 团队） |
| 年份 | **2024**（arXiv 首次提交 **2024-09-27**，`cs.CV`） |
| 会议 / 期刊 | **预印本**（OpenAlex `primary_location` = arXiv，无会场 DOI） |
| 被引数 | **1,022**（OpenAlex `10.48550/arxiv.2409.18869`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2409.18869> ｜ arXiv DOI `10.48550/arxiv.2409.18869` |
| 一句话贡献 | 把图像 / 文本 / 视频全部离散成**同一种 token**，只用一个 **8B** 自回归 Transformer 做下一 token 预测，**不用扩散、也不做视觉编码器与语言模型的拼接**：同一套权重同时做图像生成、图像理解与视频生成。配置公开：**32 层 / hidden 4,096 / FFN 14,336 / 32 heads（8 个 KV heads）/ 词表 184,622 / RoPE base 1,000,000 / 上下文 131,072**；图像生成 **512×512**（DPO 版 **720×720**，Top-k **16,384**、Top-p **1.0**），视觉 tokenizer 基于 **SBER-MoVQGAN**；视频字幕按「<20 秒取 **12** 帧均采、更长视频切 **10–20 秒**子片段分别标注」。 |
| 与我们工作的关系 | **vision（主目标：理解与生成共用一个主干的极端形态）**：<b>动作</b>：视觉塔选型增加「统一 token 空间」对照档，但不作替代项 —— 先量「同一主干同时做理解 / 生成」时理解侧的掉点，再决定是否值得。<br>**data（视频语料的切分与标注）**：<b>动作</b>：视频标注流水线沿用「<20s 均采 12 帧 / 更长切 10–20s 子片段」的确定性规则，避免标注粒度随视频长度漂移。<br>**pretrain（tokenizer 即架构决策）**：<b>动作</b>：把「视觉 tokenizer（MoVQGAN 类）」列为与文本 tokenizer 同级的预训练前置项，先定词表与压缩率再谈配比。<br>**风险**：① 512×512 生成分辨率与现在的 1K+ 不可直接比较；② 「SOTA」为作者自报（2024-09 时点），引用须带原文表格位置；③ PDF 截断 ⇒ 数字取自 ar5iv 正文，未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十轮） |
| 核验状态 | arXiv abs 页 `200` / 44,721 B（`citation_title` / `citation_author` / `citation_date=2024/09/27`）；OpenAlex `200`（**1,022**）；ar5iv HTML `200` / **267,946 B** 核 Table 3 的 `8B / 32 / 4096 / 14336 / 32 / 8 / 184622 / 1000000 / 131072`、`512 x 512`、`720 x 720`、`Top-k to 16,384 and Top-p to 1.0`、`SBER-MoVQGAN`、`shorter than 20 seconds are captioned using 12 evenly sampled frames`、`10-20 second sub-clips`；PDF `200` / 656,992 B 但**截断**（`pdftotext` 失败）⇒ 数字以 ar5iv 为准。 |

---

## 267. Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

| 字段 | 内容 |
|:--|:--|
| 标题 | Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads |
| 作者（前 3） | Tianle Cai · Yuhong Li · Zhengyang Geng（et al.，共 **7** 位，另有 Hongwu Peng / Jason D. Lee / Deming Chen / Tri Dao；Princeton · UIUC · Together AI） |
| 年份 | **2024**（arXiv 首次提交 **2024-01-19**，`cs.LG`） |
| 会议 / 期刊 | **预印本**（OpenAlex `primary_location` = arXiv，`locations` 仅 arXiv、无会场 DOI ⇒ 未独立核会议收录，不写会议名） |
| 被引数 | **1,028**（OpenAlex `10.48550/arxiv.2401.10774`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2401.10774> ｜ arXiv DOI `10.48550/arxiv.2401.10774` |
| 一句话贡献 | 在冻结主干之上加**多个解码头**并行预测后续多个位置，配合 **tree attention** 一次验证多条候选，把「投机解码」做成**不需要草稿模型**的插件：**Medusa-1**（主干冻结）> **2.2×** 加速且不损生成质量，**Medusa-2**（与主干联合微调、需保能力的训练配方）进一步到 **2.3–2.8×**；分任务上「信息抽取」类加速最高 **3.62×**；稀疏树可在加速率基本不变的前提下减少 tokens/s 的下降。 |
| 与我们工作的关系 | **zhulong（主目标：成本口径的「无损加速」档位）**：<b>动作</b>：成本表把「无损加速比」单列一栏（Medusa-1 型），与「有损 / 需联合训练」（Medusa-2 型）分开报，禁止合成一个「平均加速」；判据 = 同任务同质量门槛下的 tokens/s 与每题成本（含草稿头显存）。<br>**harness（延迟口径）**：<b>动作</b>：评测报表记录「是否启用投机解码 / 树宽 / 验证批次」，不同档位的时延不得并列比较。<br>**pretrain（辅）**：<b>动作</b>：若要联合训练解码头，预训练末期预留「保能力」配方（本文 Medusa-2 的前提），不要等到上线前才补。<br>**风险**：① 加速比强依赖 batch / 序列长度 / 任务类型（抽取类 3.62× 不可外推为通用值）；② 数字为作者自报，未见第三方在同硬件复现；③ PDF 截断 ⇒ 数字取自 ar5iv 正文与 arXiv 摘要。 |
| 首次收录 | **2026-11-20**（第七十轮） |
| 核验状态 | arXiv abs 页 `200` / 45,392 B（`citation_title` / `citation_author` ×7 / `citation_date=2024/01/19`）；OpenAlex `200`（**1,028**）；ar5iv HTML `200` / **319,495 B** 核 `Medusa-1 can achieve over 2.2× speedup without compromising generation quality`、`Medusa-2 further improves the speedup to 2.3-2.8×`、`highest speedup at 3.62×`、`tree attention`；PDF `200` / 513,446 B 但**截断**（`pdftotext` 失败）⇒ 数字以 ar5iv 为准。 |

---

## 268. Janus: Decoupling Visual Encoding for Unified Multimodal Understanding and Generation

| 字段 | 内容 |
|:--|:--|
| 标题 | Janus: Decoupling Visual Encoding for Unified Multimodal Understanding and Generation |
| 作者（前 3） | Chengyue Wu · Xiaokang Chen · Zhiyu Wu（et al.，DeepSeek-AI · 北京大学） |
| 年份 | **2024**（arXiv 首次提交 **2024-10-17**，`cs.CV`） |
| 会议 / 期刊 | **IEEE/CVF CVPR 2025**，pp. **12966–12977**（OpenAlex `type=conference-paper`，`primary_location` = IEEE CVPR） |
| 被引数 | **633**（OpenAlex `10.48550/arxiv.2410.13848`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2410.13848> ｜ arXiv DOI `10.48550/arxiv.2410.13848` |
| 一句话贡献 | 指出「理解」与「生成」对视觉表征的粒度要求存在冲突，**把视觉编码拆成两条通路**（理解用 **SigLIP** 语义特征 + understanding adaptor；生成用离散 tokenizer + generation adaptor），但仍**共用一个 Transformer 主干**：**1.3B** 模型在 GenEval 达 **61%**、MSCOCO-30K FID **8.53**，超过 DALL-E 2 与 SDXL 一类纯生成模型；理解侧三项基准 **69.4 / 63.7 / 87.0**，优于 LLaVA-v1.5-7B 与 Qwen-VL-Chat-7B（作者自报）。 |
| 与我们工作的关系 | **vision（主目标：理解与生成的编码器可以解耦）**：<b>动作</b>：视觉塔方案表新增「单编码器共享 vs 双编码器解耦」两档，判据 = 理解基准掉点幅度与生成 FID / GenEval 的同表对比；不要默认「统一编码器更省」就等于更好。<br>**designflow（辅：图 / 版图理解的判分）**：<b>动作</b>：若流程图 / 版图任务既要「读懂」又要「画出」，按本文结论先把两条通路的 adaptor 分开评测，避免用一个总分掩盖一侧退化。<br>**pretrain（辅）**：<b>动作</b>：共享主干 + 双 adaptor 的结构可直接作为 2B 规模的多模态消融项（参数量增量远小于双塔）。<br>**风险**：① 1.3B 规模，不能外推到更大模型；② GenEval / FID 均为作者自报，生成分辨率为 384/512 级；③ PDF 截断 ⇒ 数字取自 ar5iv 正文，未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十轮） |
| 核验状态 | arXiv abs 页 `200` / 42,726 B（`citation_title` / `citation_author` / `citation_date=2024/10/17`）；OpenAlex `200`（**633**，CVPR 2025 pp. 12966–12977）；ar5iv HTML `200` / **317,703 B** 核 `Janus (Ours) 1.3B`、`FID score of 8.53`、`accuracy of 61%`、`69.4 / 63.7 / 87.0`、`SigLIP`、`decouple visual encoding into separate pathways`；PDF `200` / 284,070 B 但**截断**（`pdftotext` 失败）⇒ 数字以 ar5iv 为准。 |

---

## 269. Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus

| 字段 | 内容 |
|:--|:--|
| 标题 | Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus |
| 作者（前 3） | Jesse Dodge · Maarten Sap · Ana Marasović（et al.，共 8 位；Allen Institute for AI / UW / CMU / Stanford） |
| 年份 | **2021**（arXiv 首次提交 **2021-04-18**，`cs.CL`） |
| 会议 / 期刊 | **EMNLP 2021**，pp. **1286–1305**（OpenAlex `type=conference-paper`） |
| 被引数 | **990**（OpenAlex `10.48550/arxiv.2104.08758`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2104.08758> ｜ arXiv DOI `10.48550/arxiv.2104.08758` |
| 一句话贡献 | 首次系统**文档化 C4** 的来源、内容与过滤后果：`C4.en` 为 **365M 文档 / 156B token / 305 GB**（无 blocklist 版 395M / 198B / 380 GB，无清洗版 1.1B / 1.4T / 2.3 TB）；来源含专利与美国军方网站，正文含机器翻译文本与其他基准的评测样例；blocklist 过滤**不成比例地删除少数群体相关文本**。 |
| 与我们工作的关系 | **data（主目标：网页语料的来源审计与去污染基线）**：<b>动作</b>：语料清洗报表固定三列——来源域抽样、机器生成文本抽检、与评测集的重合检查；把「无 blocklist / 无清洗」两档规模写进同一张表，避免只报最终规模。<br>**harness（辅）**：<b>动作</b>：评测集污染检查不只查精确串，还要查「同分布机器翻译文本」与「基准样例原文」两类（本文实测两类都在 C4 中）。<br>**pretrain（辅）**：<b>动作</b>：报预训练语料规模时同时给「文档数 / token 数 / 字节数」三个口径，🚫 只报 token。<br>**风险**：① 2021 年的 Common Crawl 快照，不能代表当前网页分布；② 过滤影响是描述性统计，不是因果实验；③ 只覆盖英文 C4。 |
| 首次收录 | **2026-11-20**（第七十一轮） |
| 核验状态 | arXiv abs 页 `200` / 43,569 B（`citation_title` / `citation_author` / `citation_date=2021/04/18`）；OpenAlex `200`（**990**，EMNLP 2021 pp. 1286–1305）；ar5iv HTML `200` / **207,799 B** 核 `365 million` / `156 billion` / `305 GB` / `395 million` / `198 billion` / `380 GB` / `1.1 billion` / `1.4 trillion` / `2.3 TB` 与 blocklist 段落；**未做 PDF 逐页复核**。 |
| 首次收录补注 | 本条目同时补上必读清单外的「数据文档化」源头：C4 是 T5 `1910.10683`（#81）的训练语料，但语料本身的审计结论只在这篇里。 |

---

## 270. A ConvNet for the 2020s（ConvNeXt）

| 字段 | 内容 |
|:--|:--|
| 标题 | A ConvNet for the 2020s |
| 作者（前 3） | Zhuang Liu · Hanzi Mao · Chao-Yuan Wu（et al.，共 6 位；Meta AI / UC Berkeley；末位 Saining Xie） |
| 年份 | **2022**（arXiv 首次提交 **2022-01-10**，`cs.CV`） |
| 会议 / 期刊 | **IEEE/CVF CVPR 2022**，pp. **11966–11976**（OpenAlex `type=conference-paper`） |
| 被引数 | **13,910**（OpenAlex `10.48550/arxiv.2201.03545`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2201.03545> ｜ arXiv DOI `10.48550/arxiv.2201.03545` |
| 一句话贡献 | 把标准 ResNet **逐步「现代化」**（macro design / ResNeXt / inverted bottleneck / 大卷积核 / 逐层微设计）为纯 ConvNet：**300 epoch**、AdamW **4e-3**、batch **4096**、weight decay **0.05**、20 epoch warmup、LayerScale 初值 **1e-6**、EMA；ConvNeXt-T 在 **4.5 GFLOPs** 下 **82.1%**（Swin-T **81.3%**），ConvNeXt-XL 384² 达 **87.8%**（350M 参数 / 179.0 GFLOPs），并在 COCO / ADE20K 上优于 Swin（作者自报）。 |
| 与我们工作的关系 | **vision（主目标：视觉编码器选型与配方）**：<b>动作</b>：视觉塔方案表把「纯 ConvNet / 层级 Transformer / 混合」并排，判据 = 同 GFLOPs 下的精度 + 下游 VLM 任务掉点，🚫 只看 ImageNet 单点。<br>**pretrain（辅）**：<b>动作</b>：把 300 epoch / 4e-3 / wd 0.05 / LayerScale 1e-6 / EMA 作为「强基线配方」写进预训练配置表，先固定配方再比架构，避免架构与配方混在一起。<br>**风险**：① 主结果是 ImageNet-1K 监督预训练，不等于图文对齐最优；② 13,910 次被引里大量是后续工作引用，非独立复现；③ ar5iv 数字未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十一轮） |
| 核验状态 | arXiv abs 页 `200` / 44,344 B（`citation_title` / `citation_author` / `citation_date=2022/01/10`）；OpenAlex `200`（**13,910**，CVPR 2022 pp. 11966–11976）；ar5iv HTML `200` / **476,499 B** 核 `87.8%` / `82.1` / `81.3` / `4.5G` / `300 epochs` / `4e-3` / `batch size of 4096` / `weight decay of 0.05` / `1e-6` / `EMA`；**未做 PDF 逐页复核**。 |

---

## 271. Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets

| 字段 | 内容 |
|:--|:--|
| 标题 | Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets |
| 作者（前 3） | Alethea Power · Yuri Burda · Harri Edwards（et al.，共 5 位；OpenAI） |
| 年份 | **2022**（arXiv 首次提交 **2022-01-06**，`cs.LG`） |
| 会议 / 期刊 | arXiv 预印本（OpenAlex `type=preprint`，无会场记录） |
| 被引数 | **967**（OpenAlex `10.48550/arxiv.2201.02177`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2201.02177> ｜ arXiv DOI `10.48550/arxiv.2201.02177` |
| 一句话贡献 | 在小算法数据集上发现 **grokking**：泛化可以发生在**严重过拟合之后**——除法 mod 97、训练集占 **50%** 时，训练精度约 **10^3** 步接近完美，而验证精度要到约 **10^6** 步才达到同水平；数据比例在 **25–30%** 附近时，少 **1%** 数据会让泛化**中位时间增加 40–50%**；**weight decay** 对改善泛化最有效（作者自报）。 |
| 与我们工作的关系 | **pretrain（主目标：训练时长 / 早停 / 正则化口径）**：<b>动作</b>：小规模预训练消融必须固定「训练步数上限」，并把「验证集还在上升」与「已经平台」分开记录；🚫 用早期验证曲线判定某组件无效。<br>**harness（辅）**：<b>动作</b>：小验证集上的「明显掉点」先排除指标噪声与样本量不足，再判定能力缺失（与 #272 同一教训）。<br>**data（辅）**：<b>动作</b>：数据量缩小实验必须记录「达到目标精度所需步数」，不只记最终精度。<br>**风险**：① 任务全是合成算法数据集（模运算 / 群运算），不能直接外推到自然语言；② 结果对小数据集与强正则化敏感；③ 未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十一轮） |
| 核验状态 | arXiv abs 页 `200` / 43,160 B（`citation_title` / `citation_author` / `citation_date=2022/01/06`）；OpenAlex `200`（**967**，preprint）；ar5iv HTML `200` / **106,203 B** 核 `division mod 97` / `50%` / `10^3` / `10^6` / `25-30%` / `1%` / `40-50%` / `weight decay is particularly effective`；**未做 PDF 逐页复核**。 |

---

## 272. Are Emergent Abilities of Large Language Models a Mirage?

| 字段 | 内容 |
|:--|:--|
| 标题 | Are Emergent Abilities of Large Language Models a Mirage? |
| 作者（前 3） | Rylan Schaeffer · Brando Miranda · Sanmi Koyejo（共 3 位；Stanford University） |
| 年份 | **2023**（arXiv 首次提交 **2023-04-28**，`cs.CL`） |
| 会议 / 期刊 | **NeurIPS 2023**，pp. **55565–55581**（OpenAlex `type=conference-paper`） |
| 被引数 | **1,116**（OpenAlex `10.48550/arxiv.2304.15004`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2304.15004> ｜ arXiv DOI `10.48550/arxiv.2304.15004` |
| 一句话贡献 | 提出「涌现是**指标造成的幻象**」：BIG-Bench 上约 **92%** 的「涌现能力」只在 **multiple-choice grade / exact match** 这类非线性或不连续指标下出现；换成线性 / 连续指标或增加统计量后消失，而 per-token 交叉熵随模型规模按**幂律平滑下降**；样本太少也会让弱小模型看起来「突然不行」，从而制造假涌现。 |
| 与我们工作的关系 | **harness（主目标：判分口径与报表模板）**：<b>动作</b>：报表同时给「连续指标（per-token loss / per-step 部分分）」与「离散指标（pass@k / 全对率）」，并写明题量与置信区间；🚫 只报一个离散总分。<br>**designflow（辅）**：<b>动作</b>：L1–L5 判分不要全用「全对 / 全错」，至少保留一档可累加的部分分，否则阶段能力会被「门槛效应」掩盖。<br>**pretrain（辅）**：<b>动作</b>：scaling 曲线读数先用连续 loss，再看离散基准，避免把指标拐点当成能力拐点。<br>**风险**：① 论文针对的是「同一模型家族的固定输出」分析，不否认某些能力确实在规模上出现；② 92% 是 BIG-Bench 子集统计，不是所有基准；③ 未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十一轮） |
| 核验状态 | arXiv abs 页 `200` / 42,800 B（`citation_title` / `citation_author` / `citation_date=2023/04/28`）；OpenAlex `200`（**1,116**，NeurIPS 2023 pp. 55565–55581）；ar5iv HTML `200` / **151,070 B** 核 `92%` / `Multiple Choice Grade` / `exact match` / `power law` / `per-token cross entropy`；**未做 PDF 逐页复核**。 |

---
## 273. Measuring Massive Multitask Language Understanding（MMLU）

| 字段 | 内容 |
|:--|:--|
| 标题 | Measuring Massive Multitask Language Understanding |
| 作者（前 3） | Dan Hendrycks · Collin Burns · Steven Basart（et al.，共 7 位；UC Berkeley / Columbia / UChicago / MIT；末位 Jacob Steinhardt） |
| 年份 | **2021**（ICLR 2021；arXiv 首次提交 **2020-09-07**，`cs.CY`） |
| 会议 / 期刊 | **ICLR 2021**（arXiv `comment` 原文 `ICLR 2021`；OpenAlex 对该 arXiv DOI 记录为 `preprint`，两条口径不同） |
| 被引数 | **6,448**（OpenAlex `10.48550/arxiv.2009.03300`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2009.03300> ｜ arXiv DOI `10.48550/arxiv.2009.03300` |
| 一句话贡献 | 用 **57 个学科**的多选题测预训练知识：**14,079** 道测试题、**1,540** 道开发题、每科至少 **100** 道测试题，覆盖 STEM / 人文 / 社科 / 其他，难度从小学到专业；估计专家准确率约 **89.8%**，而 GPT-3 为 **43.9%**、随机猜为 **25%**，且没有任何单科达到专家水平（作者自报）。 |
| 与我们工作的关系 | **harness（主目标：基准聚合与污染口径）**：<b>动作</b>：新 harness 的第一道 sanity check 固定跑 MMLU，但报表必须同时给「总分 + 逐科分数 + 每科题量」，并按题量给区间；🚫 只报一个总分（#272 已证明总分会被指标形状掩盖）。<br>**pretrain（辅）**：<b>动作</b>：预训练数据决策里把 MMLU 当「知识覆盖探针」，🚫 当能力上限；对单科突增先做污染排查再归因到数据配比。<br>**data（辅）**：<b>动作</b>：去污染流水线把 MMLU 测试题（含选项顺序变体）列入固定 blocklist，并在数据配比实验前后各跑一次。<br>**风险**：① 测试集公开且早于多数现行语料，分数易受污染；② 89.8% 是估计值而非实测专家分数；③ 题目以英语 / 美国语境为主；④ 未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十二轮） |
| 核验状态 | arXiv API `id_list=2009.03300,2409.12191,2101.00027,2405.04434` **`200` + `application/atom+xml`**（19,377 B / 4 entry；`published=2020-09-07T17:59:25Z`）；OpenAlex **`200`（6,448）**；ar5iv HTML **`200` / 208,166 B** 核 `57 subjects` / `14,079` / `1,540` / `100 test examples` / `89.8` / `43.9` / `25%`；**未做 PDF 逐页复核**。 |

---

## 274. Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution

| 字段 | 内容 |
|:--|:--|
| 标题 | Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution |
| 作者（前 3） | Peng Wang · Shuai Bai · Sinan Tan（et al.，共 19 位；Alibaba Group / Qwen Team；末位 Junyang Lin） |
| 年份 | **2024**（arXiv 首次提交 **2024-09-18**，`cs.CV`） |
| 会议 / 期刊 | arXiv 预印本（OpenAlex `type=preprint`；无会场记录） |
| 被引数 | **6,170**（OpenAlex `10.48550/arxiv.2409.12191`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2409.12191> ｜ arXiv DOI `10.48550/arxiv.2409.12191` |
| 一句话贡献 | 两条接口改动而非换主干：① **naive dynamic resolution** 把任意分辨率图像映射成可变数量视觉 token；② **M-RoPE** 把旋转位置编码拆成 **temporal / height / width** 三分量（文本时三分量取相同 ID，退化为 1D-RoPE）；ViT 后用 MLP 把相邻 **2×2** token 压成一个，统一处理图像与视频；2B / 8B / 72B 三档，声称可理解 **20 分钟以上**视频；DocVQA **96.5 / 94.5 / 90.1**、MMMU **64.5 / 54.1 / 41.1**（72B / 7B / 2B，作者自报）。 |
| 与我们工作的关系 | **vision（主目标：视觉塔分辨率与位置编码）**：<b>动作</b>：视觉塔方案表新增「固定分辨率 + 插值」vs「原生动态分辨率 + 2×2 压缩」两行，判据 = 同视觉 token 预算下的 OCR / 文档任务分数，并单独记录 token 数随分辨率的增长。<br>**pretrain（辅）**：<b>动作</b>：长上下文位置编码试验把 M-RoPE 的三分量拆解作为对照（文本退化一致性必须先验证），🚫 直接把 1D-RoPE 结论套到多模态。<br>**data（辅）**：<b>动作</b>：图文对采集不强制统一分辨率，保留原始宽高比与像素数，供动态分辨率训练直接使用。<br>**风险**：① 全部数字为作者自报且未复现；② 动态分辨率会抬高视觉 token 成本，收益需与显存 / 时延一起算；③ 论文注明与 `2408.15262` 有文本重叠（arXiv admin note）；④ 未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十二轮） |
| 核验状态 | arXiv API `id_list` **`200` + atom**（`published=2024-09-18T17:59:32Z`；`comment` = 代码链接 + 文本重叠提示）；OpenAlex **`200`（6,170）**；ar5iv HTML **`200` / 655,463 B** 核 `naive dynamic resolution` / `M-RoPE` / `temporal, height, and width` / `2 × 2` / `DocVQA` 96.5·94.5·90.1 / `MMMU val` 64.5·54.1·41.1 / `20 minutes`；**未做 PDF 逐页复核**。 |

---



## 275. The Pile: An 800GB Dataset of Diverse Text for Language Modeling

| 字段 | 内容 |
|:--|:--|
| 标题 | The Pile: An 800GB Dataset of Diverse Text for Language Modeling |
| 作者（前 3） | Leo Gao · Stella Biderman · Sid Black（et al.，共 12 位；EleutherAI） |
| 年份 | **2020**（arXiv 首次提交 **2020-12-31**，`cs.CL`；数据集论文常引作 2021） |
| 会议 / 期刊 | arXiv 预印本（OpenAlex `type=preprint`；无会场记录） |
| 被引数 | **3,645**（OpenAlex `10.48550/arxiv.2101.00027`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2101.00027> ｜ arXiv DOI `10.48550/arxiv.2101.00027` |
| 一句话贡献 | 公开 **825.18 GiB**、**22 个子集**的英文预训练语料，并把「原始大小 / 采样权重 / 重复 epoch 数 / 有效大小」四列同时公开：Pile-CC **227.12 GiB（18.11%，1.0 epoch）**、PubMed Central **90.27 GiB（14.40%，2.0）**、Books3 **100.96 GiB（12.07%，1.5）**、OpenWebText2 **62.77 GiB（10.01%，2.0）**、ArXiv **56.21 GiB（8.96%，2.0）**；评测用 **bits per UTF-8 encoded byte（bpb）** 而非仅 perplexity，并承认训练 / 验证 / 测试划分之间仍可能有重复文档（作者自报）。 |
| 与我们工作的关系 | **data（主目标：配比的两个旋钮）**：<b>动作</b>：数据配比表把「采样比例」与「重复 epoch 数」拆成两列分别记录，按有效 token 而非原始字节核算；小规模消融固定有效 token 预算再比比例。<br>**pretrain（辅）**：<b>动作</b>：跨语料比较统一用 **bpb**（与 tokenizer 无关），🚫 用不同 tokenizer 下的 perplexity 直接横比。<br>**harness（辅）**：<b>动作</b>：验证 / 测试集去重口径写进数据卡，承认跨 split 重复并按文档级指纹复检。<br>**风险**：① 语料含已下架 / 版权争议子集（如 Books3），不可直接照搬；② 2020 年的网页语料与现行清洗口径差距大；③ 22 子集的权重是经验选择，非最优化结果；④ 未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十二轮） |
| 核验状态 | arXiv API `id_list` **`200` + atom**（`published=2020-12-31T19:00:10Z`）；OpenAlex **`200`（3,645）**；ar5iv HTML **`200` / 677,121 B** 核 `825.18 GiB` / `22 diverse` / `Pile-CC 227.12 GiB 18.11%` / `PubMed Central 90.27 GiB 14.40%` / `Books3 100.96 GiB 12.07%` / `ArXiv 56.21 GiB 8.96%` / `bits per UTF-8` / 跨 split 重复说明；**未做 PDF 逐页复核**。 |

---

## 276. DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model

| 字段 | 内容 |
|:--|:--|
| 标题 | DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model |
| 作者（前 3） | DeepSeek-AI（团队署名；Aixin Liu · Bei Feng · Bin Wang …） |
| 年份 | **2024**（arXiv 首次提交 **2024-05-07**，`cs.CL`） |
| 会议 / 期刊 | arXiv 预印本技术报告（OpenAlex `type=preprint`；无会场记录） |
| 被引数 | **1,986**（OpenAlex `10.48550/arxiv.2405.04434`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2405.04434> ｜ arXiv DOI `10.48550/arxiv.2405.04434` |
| 一句话贡献 | **236B 总参 / 21B 激活**、**128K** 上下文的 MoE 模型，核心是 **MLA（Multi-head Latent Attention）**：把 K/V 联合压到低秩潜向量以缩 KV cache，并与 **DeepSeekMoE**（细粒度专家 + 共享专家）组合；在 **8.1T token** 上预训练，相对 DeepSeek 67B 声称节省 **42.5%** 训练成本、KV cache 减少 **93.3%**、最大生成吞吐提升 **5.76×**（作者自报）。 |
| 与我们工作的关系 | **pretrain（主目标：注意力与 MoE 的联合设计）**：<b>动作</b>：长上下文配置表新增「MLA vs GQA vs MHA」三行，判据 = 同显存下的最大 batch / 序列长度与训练吞吐，并单列低秩维度作为超参；🚫 只比参数量。<br>**zhulong（辅）**：<b>动作</b>：成本口径把「KV cache 字节数」与「每 token 激活参数」分开记，MLA 的收益主要落在前者，不能折算成同等训练算力节省。<br>**harness（辅）**：<b>动作</b>：长上下文评测固定报告「有效上下文」而非标称 128K（与 #240 的 RULER 口径一致）。<br>**风险**：① 团队署名、个人贡献难拆分；② 42.5% / 93.3% / 5.76× 均为对自家 67B 基线的相对值，不可跨模型横比；③ MLA 的低秩压缩对某些检索型任务可能掉点；④ 未做 PDF 逐页复核。 |
| 首次收录 | **2026-11-20**（第七十二轮） |
| 核验状态 | arXiv API `id_list` **`200` + atom**（`published=2024-05-07T15:56:43Z`）；OpenAlex **`200`（1,986）**；ar5iv HTML **`200` / 694,593 B** 核 `236B` / `21B` / `128K` / `8.1T` / `42.5%` / `93.3%` / `5.76` / `Multi-head Latent Attention`；**未做 PDF 逐页复核**。 |

---

## 277. SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models |
| 作者（前 3） | Guangxuan Xiao · Ji Lin · Mickael Seznec（共 **6** 位；末位 Song Han；arXiv 作者字段逐字核） |
| 年份 | **2022**（arXiv v1 `2022-11-18`；v2 `2024-03-29`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，来源标 arXiv；本轮未核到一手会场页 ⇒ 不写会议） |
| 被引数 | **839**（OpenAlex `10.48550/arxiv.2211.10438`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2211.10438> ｜ DOI `10.48550/arxiv.2211.10438` |
| 一句话贡献 | 训练后量化（PTQ）：用逐通道缩放 `s_j = max|X_j|^α / max|W_j|^(1−α)` 把激活的离群难度**等价迁移**到权重，从而做 **W8A8**；摘要自报 **1.56×** 加速、**2×** 显存下降，并可在单节点服务 **530B** 模型。 |
| 与我们工作的关系 | **zhulong（主 · 成本口径）**：凡引用量化收益，必须注明「按权重还是按激活折算」，否则成本对比不可比。**pretrain（推理侧）**：W8A8 后的精度差摘要只写 "negligible loss"、无逐任务数字 ⇒ 我方须自测后再入账。**harness**：模型卡需固定精度版本（FP16 / W8A8），否则同一基准的分数不可跨轮比较。 |
| 首次收录 | **2026-11-20**（第七十三轮） |
| 核验状态 | arXiv `id_list=2403.04132,2211.10438,2304.13705,2402.00159` **`200` + `application/atom+xml`**（11,794 B / 4 entry）；OpenAlex **`200`（839）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 278. Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference

| 字段 | 内容 |
|:--|:--|
| 标题 | Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference |
| 作者（前 3） | Wei-Lin Chiang · Lianmin Zheng · Ying Sheng（共 **11** 位；末位 Ion Stoica；arXiv 作者字段逐字核） |
| 年份 | **2024**（arXiv v1 `2024-03-07`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，来源标 arXiv；本轮未核到一手会场页 ⇒ 不写会议） |
| 被引数 | **2,131**（OpenAlex `10.48550/arxiv.2403.04132`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2403.04132> ｜ DOI `10.48550/arxiv.2403.04132` |
| 一句话贡献 | 把**匿名成对比较 + 众包投票**做成常驻评测平台：累计 **240K+** 票；验证众包问题足够多样且有区分度、人类投票与专家评分一致性良好；公开排行榜。 |
| 与我们工作的关系 | **harness（主 · 人评与自动判分的偏差）**：<b>动作</b>：agent 任务的人评比聊天更贵，先做「成对比较 + 小样本一致性抽样」校准自动 judge，再决定是否扩大人评；报表须同时给票数与置信区间。**zhulong**：人评成本单独列一项，不混进模型推理成本。 |
| 首次收录 | **2026-11-20**（第七十三轮） |
| 核验状态 | 同批 arXiv `id_list` **`200` + atom**；OpenAlex **`200`（2,131）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 279. Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware（ALOHA + ACT）

| 字段 | 内容 |
|:--|:--|
| 标题 | Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware |
| 作者（前 3） | Tony Z. Zhao · Vikash Kumar · Sergey Levine（共 **4** 位；末位 Chelsea Finn；arXiv 作者字段逐字核） |
| 年份 | **2023**（arXiv v1 `2023-04-23`） |
| 会议 / 期刊 | **Robotics: Science and Systems（RSS）**（OpenAlex `type=conference-paper`，`primary_location.source.display_name` 原文） |
| 被引数 | **3,065**（OpenAlex `10.48550/arxiv.2304.13705`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2304.13705> ｜ DOI `10.48550/arxiv.2304.13705` |
| 一句话贡献 | 低成本双臂遥操作硬件 + **ACT**：对**动作序列**建生成模型、一次预测一段（action chunking），用 **10 分钟**演示在 **6** 个真机精细任务上达到 **80–90%** 成功率。 |
| 与我们工作的关系 | **vision（视觉塔接动作头）**：视觉编码器之外，「一次预测一段动作」是降低复合误差的关键设计。**data**：演示量以「分钟」计 ⇒ 数据线可用「每任务演示时长」作预算单位。**harness**：真机成功率须写清每任务演示数 / 尝试次数，否则不可比。 |
| 首次收录 | **2026-11-20**（第七十三轮） |
| 核验状态 | 同批 arXiv `id_list` **`200` + atom**；OpenAlex **`200`（3,065）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 280. Dolma: an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research

| 字段 | 内容 |
|:--|:--|
| 标题 | Dolma: an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research |
| 作者（前 3） | Luca Soldaini · Rodney Kinney · Akshita Bhagia（共 **36** 位；Ai2；arXiv 作者字段逐字核） |
| 年份 | **2024**（arXiv v1 `2024-01-31`；v2 `2024-06-06`） |
| 会议 / 期刊 | **ACL**（OpenAlex `type=conference-paper`，`primary_location.source.display_name` = `Proceedings of the conference - Association for Computational Linguistics. Meeting`） |
| 被引数 | **674**（OpenAlex `10.48550/arxiv.2402.00159`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2402.00159> ｜ DOI `10.48550/arxiv.2402.00159` |
| 一句话贡献 | 发布 **3 万亿 token** 英文预训练语料（网页 / 论文 / 代码 / 公版书 / 社交 / 百科六类来源），并把**构造过程 + 中间态分析 + 开源 curation toolkit** 一并公开。 |
| 与我们工作的关系 | **data（主 · 配比与顺序）**：<b>动作</b>：把「中间态 checkpoint 上的 loss」作为每个清洗步骤的验收指标，而不是只看最终语料统计。**pretrain**：语料版本号进训练配置，保证可复现。**harness**：评测报表须记录模型所用的数据版本，跨版本分数不直接比较。 |
| 首次收录 | **2026-11-20**（第七十三轮） |
| 核验状态 | 同批 arXiv `id_list` **`200` + atom**；OpenAlex **`200`（674）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---



## 281. PaLM-E: An Embodied Multimodal Language Model

| 字段 | 内容 |
|:--|:--|
| 标题 | PaLM-E: An Embodied Multimodal Language Model |
| 作者（前 3） | Danny Driess · Fei Xia · Mehdi S. M. Sajjadi（共 **22** 位；末位 Pete Florence；arXiv 作者字段逐字核） |
| 年份 | **2023**（arXiv v1 `2023-03-06`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，来源标 arXiv；记忆中的 ICML 2023 本轮**未核到一手会场页 ⇒ 不写**） |
| 被引数 | **4,143**（OpenAlex `10.48550/arxiv.2303.03378`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2303.03378> ｜ DOI `10.48550/arxiv.2303.03378` |
| 一句话贡献 | 把**图像 + 连续状态估测的编码**当作 token 拼进「多模态句子」，与文本交错后**端到端**喂给预训练 LLM；单个 **PaLM-E-562B（562B）**模型跨多种机器人本体做顺序操作规划 / VQA / 描述，并在互联网规模语言-视觉联合训练上出现**正迁移**。 |
| 与我们工作的关系 | **vision（主 · 视觉塔怎么接语言塔）**：<b>动作</b>：把连续观测编码成与文本同序列的 token 时，**保留观测的时序位置**（哪一帧对应哪一步）比编码器选型更影响长程任务成功率 —— 做视觉接口消融时把这一项单列。**data**：多域联合训练**正迁移**意味着配比不必按「域内最好」单独优化，先做 2–3 个域的对半配比作为基线。**harness**：具身任务须报「本体 + 任务数 + 每任务试次」，否则成功率不可比。 |
| 首次收录 | **2026-11-20**（第七十四轮） |
| 核验状态 | arXiv `id_list=2303.03378,2312.02120` **`200` + `application/atom+xml`**（6,252 B / 2 entry，`published` 逐条核）；OpenAlex **`200`（4,143）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 282. 3D Gaussian Splatting for Real-Time Radiance Field Rendering

| 字段 | 内容 |
|:--|:--|
| 标题 | 3D Gaussian Splatting for Real-Time Radiance Field Rendering |
| 作者（前 3） | Bernhard Kerbl · Georgios Kopanas · Thomas Leimkühler（共 **4** 位；末位 George Drettakis；arXiv 作者字段逐字核） |
| 年份 | **2023**（arXiv v1 `2023-08-08`） |
| 会议 / 期刊 | **ACM Transactions on Graphics**（OpenAlex `type=article`，`source.display_name` = `ACM Transactions on Graphics`；本轮未核卷期页 ⇒ 不写） |
| 被引数 | **12,239**（OpenAlex `10.48550/arxiv.2308.04079`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2308.04079> ｜ DOI `10.48550/arxiv.2308.04079` |
| 一句话贡献 | 用**各向异性 3D 高斯**做显式场景表示（从相机标定的稀疏点初始化），配合**交错优化 / 密度控制**与**可见性感知光栅化**，在 **1080p** 下达到 **≥30 fps** 实时新视角合成，训练时间与当时 SOTA 相当。 |
| 与我们工作的关系 | **vision（主 · 合成多视角数据）**：<b>动作</b>：把 3DGS 当「有预算上限的数据生成器」时，先记录三个旋钮（梯度阈值 / 不透明度重置间隔 / 每场景点数）与画质的对应，再谈扩量。**data**：以「场景数 × 每场景视角数」而非「图片张数」做数据预算单位。**designflow**：场景级重建的可行性边界（稀疏 SfM 点上是否退化）决定它能否用于版图/机台类三维示意。 |
| 首次收录 | **2026-11-20**（第七十四轮） |
| 核验状态 | arXiv `id_list=2303.03378,2308.04079,2010.00718,2301.12597` **`200` + `application/atom+xml`**（9,914 B / 4 entry）；OpenAlex **`200`（12,239）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---



## 283. Magicoder: Empowering Code Generation with OSS-Instruct

| 字段 | 内容 |
|:--|:--|
| 标题 | Magicoder: Empowering Code Generation with OSS-Instruct |
| 作者（前 3） | Yuxiang Wei · Zhe Wang · Jiawei Liu（共 **5** 位；末位 Lingming Zhang；arXiv 作者字段逐字核） |
| 年份 | **2023**（arXiv v1 `2023-12-04`；v2 `2024-06-07`） |
| 会议 / 期刊 | **预印本**（OpenAlex `type=preprint`，来源标 arXiv；记忆中的 ICML 2024 本轮**未核到一手会场页 ⇒ 不写**） |
| 被引数 | **416**（OpenAlex `10.48550/arxiv.2312.02120`，查询日 **2026-11-20**；**&lt;500，按「方法论常青」收**：只用开源片段做种子自造指令，已被后续数据合成工作反复当基线） |
| arXiv / DOI | <https://arxiv.org/abs/2312.02120> ｜ DOI `10.48550/arxiv.2312.02120` |
| 一句话贡献 | **OSS-Instruct**：拿开源代码片段当种子、让 LLM 围绕它自造 **75K** 条合成指令数据；7B 规模的 **MagicoderS-CL-7B** 在 **HumanEval+** 上以 **66.5** 对 **65.9**（pass@1）超过 ChatGPT，且与 Evol-Instruct **正交**可叠加。 |
| 与我们工作的关系 | **data（主 · 合成代码数据怎么可控）**：<b>动作</b>：合成指令数据必须记录「种子来源 + 每种子条数 + 许可证」，否则同一批数据无法二次审计。**pretrain（代码配比）**：把「片段种子」与「凭空生成」当两类数据分别计量占比，而不是笼统记「合成数据」。**harness**：HumanEval+ 的 0.6 分差属小样本量级，报表须同时给 pass@1 与样本数，不得单点比较。 |
| 首次收录 | **2026-11-20**（第七十四轮） |
| 核验状态 | arXiv `id_list=2303.03378,2312.02120` **`200` + `application/atom+xml`**（6,252 B / 2 entry）；OpenAlex **`200`（416）**；ar5iv HTML **`200`**（652,918 B，读到作者块 `ywei40@illinois.edu`）；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 284. SGDR: Stochastic Gradient Descent with Warm Restarts

| 字段 | 内容 |
|:--|:--|
| 标题 | SGDR: Stochastic Gradient Descent with Warm Restarts |
| 作者（前 3） | Ilya Loshchilov · Frank Hutter（共 **2** 位；arXiv 作者字段逐字核） |
| 年份 | **2016**（arXiv v1 `2016-08-13`；v5 `2017-05-03`） |
| 会议 / 期刊 | **ICLR 2017**（arXiv `comment` 字段原文 = `ICLR 2017 conference paper`；OpenAlex 记 `type=preprint` ⇒ 会议信息按 arXiv 字段写，不按记忆） |
| 被引数 | **11,502**（OpenAlex `10.48550/arxiv.1608.03983`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/1608.03983> ｜ DOI `10.48550/arxiv.1608.03983` |
| 一句话贡献 | 把**余弦退火 + 周期性热重启**（`T_0` 首周期、`T_mult` 周期倍增）做成一行改动即可用的日程：CIFAR-10 **3.14%**、CIFAR-100 **16.21%** 错误率（作者自报当时 SOTA），并给出 EEG 与降采样 ImageNet 上的对照。 |
| 与我们工作的关系 | **pretrain（主 · 学习率日程）**：<b>动作</b>：WSD 之外再留**余弦 / 热重启**一条基线，判据固定为「同 token 预算下的最终 loss + 末段 loss 抖动幅度」，否则日程之争无法收敛。**zhulong（消融）**：LR 日程是消融里的强混杂因子，跨日程的 thinking/语言轴对比必须同日程。**harness**：模型卡必须写 LR 日程与 `T_mult`，否则同基准分数不可跨轮比较。 |
| 首次收录 | **2026-11-20**（第七十四轮） |
| 核验状态 | arXiv `id_list=1608.03983` **`200` + `application/atom+xml`**（2,359 B / 1 entry）；OpenAlex **`200`（11,502）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 285. A Simple Framework for Contrastive Learning of Visual Representations

| 字段 | 内容 |
|:--|:--|
| 标题 | A Simple Framework for Contrastive Learning of Visual Representations |
| 作者（前 3） | Ting Chen · Simon Kornblith · Mohammad Norouzi（共 **4** 位；末位 Geoffrey Hinton；arXiv 作者字段逐字核） |
| 年份 | **2020**（arXiv v1 `2020-02-13`；v3 `2020-07-01`） |
| 会议 / 期刊 | **ICML 2020**（arXiv `comment` 原文 `ICML'2020`；OpenAlex `type=preprint` 记 arXiv 版 ⇒ 会议信息按 arXiv 字段写） |
| 被引数 | **18,118**（OpenAlex `10.48550/arxiv.2002.05709`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2002.05709> ｜ DOI `10.48550/arxiv.2002.05709` |
| 一句话贡献 | 去掉 memory bank 与专用结构，只用「**数据增强组合 + 可学习非线性投影头 + 大 batch 长训练**」三项就做出强对比学习：ImageNet 线性探针 **76.5%** top-1（较前 SOTA 相对 +**7%**，与有监督 ResNet-50 持平）；仅用 **1%** 标签微调即得 **85.8%** top-5（标签少 **100×** 仍超 AlexNet）。 |
| 与我们工作的关系 | **vision（主 · 自监督预训练的第一杠杆）**：<b>动作</b>：视觉塔消融把「增强策略组合」与「编码器容量」拆成两个独立因子预注册，别把收益全记到编码器上。**harness**：加一条「冻结 backbone + 线性探针」的廉价评测口径（不微调），与全量微调分数并列报。**pretrain**：投影头在预训练后丢弃 ⇒ 下游用的是 backbone 表示，报表不得把投影维度当成模型规格。 |
| 首次收录 | **2026-11-20**（第七十五轮） |
| 核验状态 | arXiv `id_list=2002.05709,2003.08934,1907.11692,2012.03112` **`200` + `application/atom+xml; charset=utf-8`**（10,472 B / 4 entry，其中 RoBERTa / PIM 综述**已在表内** ⇒ 本轮不收）；OpenAlex **`200`（18,118）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 286. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis

| 字段 | 内容 |
|:--|:--|
| 标题 | NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis |
| 作者（前 3） | Ben Mildenhall · Pratul P. Srinivasan · Matthew Tancik（共 **6** 位；末位 Ren Ng；arXiv 作者字段逐字核） |
| 年份 | **2020**（arXiv v1 `2020-03-19`；v2 `2020-08-03`） |
| 会议 / 期刊 | **ECCV 2020（oral）**（arXiv `comment` 原文 `ECCV 2020 (oral)`；OpenAlex `type=preprint` 记 arXiv 版） |
| 被引数 | **1,186**（OpenAlex `10.48550/arxiv.2003.08934`，查询日 **2026-11-20**；该记录指向 arXiv 预印本，**其他版本不在同一记录内** ⇒ 口径只作本表内部比较） |
| arXiv / DOI | <https://arxiv.org/abs/2003.08934> ｜ DOI `10.48550/arxiv.2003.08934` |
| 一句话贡献 | 用一个全连接网络把**单条 5D 坐标**（空间 `(x,y,z)` + 视角 `(θ,φ)`）映射成**体密度 + 视角相关辐射亮度**，沿相机光线查询并用可微体渲染投回图像；只需「已知位姿的稀疏视角图像」即可优化出连续场景表示并做新视角合成。 |
| 与我们工作的关系 | **vision（主 · 合成多视角数据）**：<b>动作</b>：若把 NeRF 类方法当数据生成器，预算单位写「**场景数 × 每场景视角数**」，并先测位姿噪声对重建的影响，再谈扩量。**designflow**：体渲染表示的是**外观/辐射**而非几何真值 ⇒ 可做「版图三维示意」，🚫 不能当尺寸/层高可验证的 CAD 真值。**data**：生成的每张图必须带来源三元组（场景 / 位姿 / 渲染器版本）。 |
| 首次收录 | **2026-11-20**（第七十五轮） |
| 核验状态 | 同 #285 的 arXiv 批量（10,472 B / 4 entry）；OpenAlex **`200`（1,186）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 287. ChatEDA: A Large Language Model Powered Autonomous Agent for EDA

| 字段 | 内容 |
|:--|:--|
| 标题 | ChatEDA: A Large Language Model Powered Autonomous Agent for EDA |
| 作者（前 3） | Zhuolun He · Haoyuan Wu · Xinyun Zhang（共 **7** 位；末位 Bei Yu；arXiv 作者字段逐字核，affiliation 取自 arXiv 原生 HTML：一作 **Chinese University of Hong Kong**，Haisheng Zheng 为 Shanghai Artificial Intelligent Laboratory） |
| 年份 | **2023**（arXiv v1 `2023-08-20`；v4 `2024-09-21`） |
| 会议 / 期刊 | **IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems**（OpenAlex：vol **43**、issue **10**、pp. **3184–3197**、2024；DOI `10.1109/tcad.2024.3383347`） |
| 被引数 | **319**（OpenAlex `10.48550/arxiv.2308.10204`，查询日 **2026-11-20**；**&lt;500，按「本领域权威」收**：EDA 流程自动化 agent 的代表性一手工作） |
| arXiv / DOI | <https://arxiv.org/abs/2308.10204> ｜ 期刊 DOI `10.1109/tcad.2024.3383347` ｜ arXiv DOI `10.48550/arxiv.2308.10204` |
| 一句话贡献 | **ChatEDA** = LLM（自训 **AutoMage**）+ EDA 工具当执行器，把 **RTL → GDSII** 的流程拆成「**任务分解 / 脚本生成 / 任务执行**」三段；作者自报在多类需求上优于 GPT-4 等通用 LLM。 |
| 与我们工作的关系 | **designflow（主 · 造题与可验证性）**：<b>动作</b>：造题按「分解 / 脚本 / 执行」三段分别记分，执行段必须在**真 OpenROAD** 跑通才算过（呼应 EDA Corpus #264 的「脚本判对错要真跑」）。**harness**：判分对象是**脚本产物 + 运行日志**，不是自然语言解释。**data**：微调样本必须带「流程阶段」标签，否则无法判断模型是学会了流程还是背了模板。 |
| 首次收录 | **2026-11-20**（第七十五轮） |
| 核验状态 | arXiv `id_list=2003.05997,1812.04948,2305.13243,2308.10204` **`200` + `application/atom+xml`**（9,755 B / 4 entry）；OpenAlex **`200`（319，TCAD 43(10):3184–3197）**；arXiv 原生 HTML `https://arxiv.org/html/2308.10204v2` **`200` / 196,479 B**（读作者块与 affiliation）；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 288. Efficient Content-Based Sparse Attention with Routing Transformers

| 字段 | 内容 |
|:--|:--|
| 标题 | Efficient Content-Based Sparse Attention with Routing Transformers |
| 作者（前 3） | Aurko Roy · Mohammad Saffar · Ashish Vaswani（共 **4** 位；末位 David Grangier；arXiv 作者字段逐字核） |
| 年份 | **2020**（arXiv v1 `2020-03-12`；v5 `2020-10-24`） |
| 会议 / 期刊 | **Transactions of the Association for Computational Linguistics**（OpenAlex：vol **9**、pp. **53–68**、2021；DOI `10.1162/tacl_a_00353`） |
| 被引数 | **925**（OpenAlex `10.48550/arxiv.2003.05997`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2003.05997> ｜ 期刊 DOI `10.1162/tacl_a_00353` ｜ arXiv DOI `10.48550/arxiv.2003.05997` |
| 一句话贡献 | 用**在线 k-means 路由模块**学出内容相关的稀疏注意力模式，把复杂度从 `O(n²d)` 降到 **`O(n^1.5 d)`**；Wikitext-103 困惑度 **15.8 vs 18.3**、ImageNet-64 **3.43 vs 3.44** bits/dim，并在 PG-19 上以 22 层 / **8192** 序列长度取得测试困惑度 **33.2**。 |
| 与我们工作的关系 | **pretrain（主 · 长上下文稀疏注意力基线）**：<b>动作</b>：长上下文实验里把「固定窗口 / 学出来的稀疏模式」当两类基线分别跑，报告同一 token 预算下的困惑度与显存。**zhulong（成本口径）**：稀疏注意力的实际加速取决于 kernel 与聚类开销 ⇒ 成本必须实测，🚫 不许按复杂度公式外推。**harness**：长上下文评测须同时给「序列长度 + 是否外推」两个标签。 |
| 首次收录 | **2026-11-20**（第七十五轮） |
| 核验状态 | 同 #287 的 arXiv 批量（9,755 B / 4 entry）；OpenAlex **`200`（925，TACL 9:53–68）**；数字取自 arXiv 官方摘要；**未做 PDF 逐页复核**。 |

---

## 289. ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators

| 字段 | 内容 |
|:--|:--|
| 标题 | ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators |
| 作者（前 3） | Kevin Clark · Minh-Thang Luong · Quoc V. Le（共 **4** 位；末位 Christopher D. Manning；arXiv 作者字段逐字核） |
| 年份 | **2020**（arXiv v1 `2020-03-23`；仅 v1） |
| 会议 / 期刊 | **ICLR 2020**（arXiv `comment` 逐字为 `ICLR 2020`）；OpenAlex 该 DOI 记为预印本（`arXiv (Cornell University)`，无卷期页）⇒ **不写记忆中的页码** |
| 被引数 | **5,109**（OpenAlex `10.48550/arxiv.2003.10555`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2003.10555> ｜ arXiv DOI `10.48550/arxiv.2003.10555` |
| 一句话贡献 | 把 MLM 的「填空」换成 **replaced token detection**：先用小生成器把若干 token 换成合理替代词，再训练判别器逐 token 判「是否被换」；摘要口径称该目标比 MLM **更省算力（sample-efficient）**，且判别器不必与生成器等大。 |
| 与我们工作的关系 | **pretrain（主 · 预训练目标对照）**：小模型阶段若要「同算力下更高样本效率」，把 RTD 与 MLM 作为**并列目标基线**跑，预注册判据 = **同 FLOPs 下的下游微调分数 + 收敛步数**，🚫 不许只报最后分数。<br>**zhulong（因果边界）**：判别式目标只喂编码器，**不直接产出生成能力** ⇒ 「thinking 轴」的收益必须单独测，不能与预训练效率混谈。<br>**data（配比陷阱）**：生成器与判别器所见语料必须**同分布**，否则判别器学成「体裁/领域判别器」而非「替换检测器」——这是复现时最常见的一种假成功。 |
| 首次收录 | **2026-11-20**（第七十六轮） |
| 核验状态 | arXiv `id_list=2003.10555,1703.06870,1506.01497,1801.01290` ⇒ **`200` + `application/atom+xml`**（9,733 B / 4 entry）；OpenAlex **`200`（5,109）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 290. Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks

| 字段 | 内容 |
|:--|:--|
| 标题 | Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks |
| 作者（前 3） | Shaoqing Ren · Kaiming He · Ross Girshick（共 **4** 位；末位 Jian Sun；arXiv 作者字段逐字核） |
| 年份 | **2015**（arXiv v1 `2015-06-04`；v3 `2016-01-06`） |
| 会议 / 期刊 | **IEEE TPAMI**（OpenAlex：vol **39**、issue **6**、pp. **1137–1149**、2017；DOI `10.1109/tpami.2016.2577031`）；arXiv `comment` 仅写 `Extended tech report`，**会议版本轮未从一手源核对 ⇒ 不写** |
| 被引数 | **80,700**（OpenAlex `10.48550/arxiv.1506.01497`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/1506.01497> ｜ 期刊 DOI `10.1109/tpami.2016.2577031` ｜ arXiv DOI `10.48550/arxiv.1506.01497` |
| 一句话贡献 | 用 **RPN**（全卷积，逐位置同时出 objectness 与框回归）替代外部候选框算法，并**与检测网络共享全图卷积特征** ⇒ 候选框「近乎零成本」；VGG-16 上**全流程 5 fps**，每图仅 **300** 个候选即达 VOC 2007/2012 与 COCO 的当时最优（摘要口径）。 |
| 与我们工作的关系 | **vision（主 · 区域级检测头）**：视觉塔若要输出「区域级」结果（版图图形 / 封装元件 / 缺陷块），RPN 的「共享特征 + 轻量头」是成本基线；先量「共享」省下多少算力，再谈换更重的头。<br>**designflow（造题分层）**：「定位」与「分类」拆两段记分（框 IoU 与类别分开判），避免一个总分掩盖定位退化。<br>**harness（可比性）**：检测类数字必须同时报 **候选数（300）+ NMS 阈值 + 输入分辨率**，否则跨论文不可比。 |
| 首次收录 | **2026-11-20**（第七十六轮） |
| 核验状态 | 同 #289 的 arXiv 批量（9,733 B / 4 entry）；OpenAlex **`200`（80,700，TPAMI 39(6):1137–1149）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 291. Mask R-CNN

| 字段 | 内容 |
|:--|:--|
| 标题 | Mask R-CNN |
| 作者（前 3） | Kaiming He · Georgia Gkioxari · Piotr Dollár（共 **4** 位；末位 Ross Girshick；arXiv 作者字段逐字核） |
| 年份 | **2017**（arXiv v1 `2017-03-20`；v3 `2018-01-24`） |
| 会议 / 期刊 | **IEEE TPAMI**（OpenAlex：vol **42**、issue **2**、pp. **386–397**、2020；DOI `10.1109/tpami.2018.2844175`）；arXiv `comment` = `open source; appendix on more results`（**不写会议页码**） |
| 被引数 | **7,047**（OpenAlex `10.48550/arxiv.1703.06870`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/1703.06870> ｜ 期刊 DOI `10.1109/tpami.2018.2844175` ｜ arXiv DOI `10.48550/arxiv.1703.06870` |
| 一句话贡献 | 在 Faster R-CNN 上**并行加一路掩码分支**（分类 / 框 / 掩码解耦），代价小、**5 fps**；在 COCO 的实例分割、检测、人体关键点三条赛道均取得当时单模型最优（摘要口径），代码开放为 Detectron。 |
| 与我们工作的关系 | **vision（主 · 像素级区域标注）**：版图 / 封装图像若需要「轮廓」而非框，掩码分支是更贴近下游的接口；但标注成本高 ⇒ 建议 **框标注 + 少量掩码金标** 的课程式数据方案。<br>**designflow（判分）**：造题可要求输出掩码并按 IoU 判分，比框 IoU 更难被「瞎猜大框」蒙过。<br>**harness**：分割指标须与检测指标**分开报**，🚫 不用一个总分代替两者。 |
| 首次收录 | **2026-11-20**（第七十六轮） |
| 核验状态 | 同 #289 的 arXiv 批量（9,733 B / 4 entry）；OpenAlex **`200`（7,047，TPAMI 42(2):386–397）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 292. Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor

| 字段 | 内容 |
|:--|:--|
| 标题 | Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor |
| 作者（前 3） | Tuomas Haarnoja · Aurick Zhou · Pieter Abbeel（共 **4** 位；末位 Sergey Levine；arXiv 作者字段逐字核） |
| 年份 | **2018**（arXiv v1 `2018-01-04`；v2 `2018-08-08`） |
| 会议 / 期刊 | **ICML 2018**（arXiv `comment` 逐字含 `ICML 2018`）；OpenAlex 该 DOI 记 `arXiv (Cornell University)` 但 biblio 给 pp. **1861–1870** ⇒ 两处均如实记录 |
| 被引数 | **13,567**（OpenAlex `10.48550/arxiv.1801.01290`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/1801.01290> ｜ arXiv DOI `10.48550/arxiv.1801.01290` ｜ 代码 <https://github.com/haarnoja/sac> |
| 一句话贡献 | 在**最大熵**框架下把离策略更新与**随机 actor**结合：目标同时最大化期望回报与熵（「尽量成功，同时尽量随机」），在连续控制基准上优于同期 on-policy / off-policy 方法，且**不同随机种子下性能接近**（摘要口径，作者以此论证稳定性）。 |
| 与我们工作的关系 | **zhulong（主 · 稳定性判据）**：把「**同配置多种子方差**」写进预注册判据（报均值 + 标准差 + 最差种子），比只报单次最好成绩更能暴露训练不稳。<br>**harness**：任何「稳定性」结论必须附种子数与随机源（初始化 / 数据序），否则不可复核。<br>**designflow**：若把工具调用序列当连续控制，熵正则可作为探索基线；但**本线不做在线 RL 训练**，只借其评测口径。<br>**pretrain**：关系弱，只借「种子稳定性」这一报告规范。 |
| 首次收录 | **2026-11-20**（第七十六轮） |
| 核验状态 | 同 #289 的 arXiv 批量（9,733 B / 4 entry）；OpenAlex **`200`（13,567）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 293. End-to-End Object Detection with Transformers（DETR）

| 字段 | 内容 |
|:--|:--|
| 标题 | End-to-End Object Detection with Transformers |
| 作者（前 3） | Nicolas Carion · Francisco Massa · Gabriel Synnaeve（共 **6** 位；末位 Sergey Zagoruyko；arXiv 作者字段逐字核） |
| 年份 | **2020**（arXiv v1 `2020-05-26`；v3 为当前版本） |
| 会议 / 期刊 | **ECCV 2020**（OpenAlex：`Lecture Notes in Computer Science`，pp. **213–229**，DOI `10.1007/978-3-030-58452-8_13`；arXiv `comment` 为空 ⇒ 会议名按 DOI/页码记，未从会议官网逐字核） |
| 被引数 | **25,731**（OpenAlex `10.48550/arxiv.2005.12872`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2005.12872> ｜ arXiv DOI `10.48550/arxiv.2005.12872` ｜ 会议 DOI `10.1007/978-3-030-58452-8_13` ｜ 代码 <https://github.com/facebookresearch/detr> |
| 一句话贡献 | 把检测当**集合预测**：用**二分匹配**的集合损失强制「一个目标一个预测」，配 transformer 编码器-解码器与一小组**可学习 object queries**，**去掉 NMS 与 anchor 生成**；COCO 上精度/耗时与高度优化的 Faster R-CNN 基线相当，并可统一扩展到全景分割（摘要口径）。 |
| 与我们工作的关系 | **vision（主 · 无 NMS 的检测头）**：版图图形 / 封装元件若要做端到端区域输出，先试「固定 query 槽 + 集合损失」这条路线，把 NMS 阈值与 anchor 超参从调参空间里去掉。<br>**designflow（判分）**：集合式输出天然支持「一对象一答案」的对齐判分，适合造「漏检 / 重复检」两类错误分开计分的题。<br>**harness**：必须同时报 **query 数 + 训练 epoch（原文为 500）+ AP/AP50**，否则与单阶段检测器不可比。<br>**data（标注粒度）**：集合损失对「同一实物多次标注」敏感 ⇒ 数据侧要先定去重规则。 |
| 首次收录 | **2026-11-20**（第七十七轮） |
| 核验状态 | arXiv `id_list=2005.12872,1506.02640,2403.09629,2309.12284` ⇒ **`200` + `application/atom+xml`**（10,477 B / 4 entry）；OpenAlex **`200`（25,731，LNCS pp. 213–229）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**（PDF 下载 30 s 内未完成，已放弃）。 |

---

## 294. You Only Look Once: Unified, Real-Time Object Detection（YOLO）

| 字段 | 内容 |
|:--|:--|
| 标题 | You Only Look Once: Unified, Real-Time Object Detection |
| 作者（前 3） | Joseph Redmon · Santosh Divvala · Ross Girshick（共 **4** 位；末位 Ali Farhadi；arXiv 作者字段逐字核） |
| 年份 | **2015**（arXiv v1 `2015-06-08`；v5 为当前版本） |
| 会议 / 期刊 | **CVPR 2016**（OpenAlex：IEEE CVPR，pp. **779–788**，DOI `10.1109/cvpr.2016.91`；arXiv `comment` 为空 ⇒ 按 OpenAlex 记） |
| 被引数 | **66,671**（OpenAlex `10.48550/arxiv.1506.02640`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/1506.02640> ｜ arXiv DOI `10.48550/arxiv.1506.02640` ｜ 会议 DOI `10.1109/cvpr.2016.91` |
| 一句话贡献 | 把检测写成**单网络的回归问题**（一次前向直接出框 + 类别概率），整条流水线端到端优化；基础模型 **45 fps**、Fast YOLO **155 fps** 且 mAP 仍是其它实时检测器的两倍（摘要口径）；定位误差更多、但「无物体处乱报」显著更少，且从自然图像迁移到艺术画时优于 DPM / R-CNN。 |
| 与我们工作的关系 | **vision（主 · 单阶段成本基线）**：任何「实时筛查」需求（缺陷初筛 / 版面快筛）都应先量 YOLO 式单阶段成本，再决定是否上两阶段或 transformer。<br>**data（全局上下文）**：整图一次回归 ⇒ 标注要覆盖「背景即负样本」，否则误检率不可控；数据侧须给出**每图目标数分布**。<br>**designflow**：造题可把「漏检 vs 误检」设成两条独立评分轴（YOLO 的取舍正是这两轴不同权重）。<br>**harness**：检测数字必须成组报 **mAP + fps + 输入分辨率 + GPU 型号**。 |
| 首次收录 | **2026-11-20**（第七十七轮） |
| 核验状态 | 同 #293 的 arXiv 批量（10,477 B / 4 entry）；OpenAlex **`200`（66,671，CVPR 2016 pp. 779–788）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 295. Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking

| 字段 | 内容 |
|:--|:--|
| 标题 | Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking |
| 作者（前 3） | Eric Zelikman · Georges Harik · Yijia Shao（共 **6** 位；末位 Noah D. Goodman；arXiv 作者字段逐字核） |
| 年份 | **2024**（arXiv v1 `2024-03-14`；v2 为当前版本） |
| 会议 / 期刊 | **arXiv 预印本**（arXiv `comment` 为空；OpenAlex 该 DOI 记 `arXiv (Cornell University)`、`type=preprint` ⇒ **不写未核实的会议**） |
| 被引数 | **436**（OpenAlex `10.48550/arxiv.2403.09629`，查询日 **2026-11-20**；**&lt;500，按「方法论常青」收**：把「先想再说」做成可在任意文本上自监督的预训练目标） |
| arXiv / DOI | <https://arxiv.org/abs/2403.09629> ｜ arXiv DOI `10.48550/arxiv.2403.09629` |
| 一句话贡献 | STaR 的泛化：让 LM 在**每个 token 处**先生成一段「内部想法」再预测后文，用**逐 token 并行采样**、可学习的**想法起止 token** 与**扩展 teacher forcing** 控制成本；在互联网文本上继续预训练后，**零样本**（不做任务微调）把 GSM8K 从 **5.9% → 10.9%**、CommonsenseQA 从 **36.3% → 47.2%**，并降低难预测 token 的困惑度（摘要口径）。 |
| 与我们工作的关系 | **zhulong（主 · thinking 轴的前置证据）**：证明「思考」不必只在 SFT/RL 阶段引入，可在**继续预训练**里用「解释后文」的自监督信号学出来 ⇒ 小模型 thinking 预算实验应加「预训练期 vs 后训练期」两组。<br>**pretrain（目标设计）**：可把「想法 token + 原目标」看成一项**辅助损失**，需预注册主/辅损失权重与想法长度上限。<br>**harness（口径）**：其卖点是 **zero-shot、无任务微调** ⇒ 复现时必须同报「基线是否做过同量继续预训练」，否则收益会被误记到方法上。<br>**data**：想法从「任意文本」学，不依赖人工 rationale ⇒ 语料规模比标注质量更关键，需记录继续预训练 token 数。 |
| 首次收录 | **2026-11-20**（第七十七轮） |
| 核验状态 | 同 #293 的 arXiv 批量（10,477 B / 4 entry）；OpenAlex **`200`（436，preprint）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 296. MetaMath: Bootstrap Your Own Mathematical Questions for Large Language Models

| 字段 | 内容 |
|:--|:--|
| 标题 | MetaMath: Bootstrap Your Own Mathematical Questions for Large Language Models |
| 作者（前 3） | Longhui Yu · Weisen Jiang · Han Shi（共 **10** 位；末位 Weiyang Liu；arXiv 作者字段逐字核） |
| 年份 | **2023**（arXiv v1 `2023-09-21`；v4 为当前版本） |
| 会议 / 期刊 | **ICLR 2024（Spotlight）**（arXiv `comment` 逐字：`To appear at ICLR 2024 (Spotlight). Project Page: https://meta-math.github.io/`；OpenAlex 记 `International Conference on Learning Representations`，无页码） |
| 被引数 | **1,029**（OpenAlex `10.48550/arxiv.2309.12284`，查询日 **2026-11-20**） |
| arXiv / DOI | <https://arxiv.org/abs/2309.12284> ｜ arXiv DOI `10.48550/arxiv.2309.12284` ｜ 项目页 <https://meta-math.github.io/> |
| 一句话贡献 | **不加外部知识**，把同一道数学题从多个视角**改写**（自我引导）造出 **MetaMathQA**，再微调 LLaMA-2；**MetaMath-7B** 达 GSM8K **66.4%** / MATH **19.4%**（比同尺寸当时最好高 **11.5% / 8.7%**），**MetaMath-70B** GSM8K **82.3%**，略高于 GPT-3.5-Turbo（摘要口径），数据 / 模型 / 代码全开放。 |
| 与我们工作的关系 | **data（主 · 题目自举与改写）**：给「小语料扩题」一条低成本路线 —— 只改题面不改答案，先做**答案一致性过滤 + 近重复去重**，再进 SFT；预注册判据 = 原始题集不掉点、改写题集涨点。<br>**zhulong（数学推理基线）**：把 MetaMath-7B 的 GSM8K/MATH 当 SFT 档基线，与 thinking 档对比时必须同 token 预算、同评测脚本。<br>**harness（污染）**：GSM8K/MATH 的测试题可能被改写模型见过 ⇒ 必须报去污染方式（n-gram 重叠阈值），否则涨幅不可信。<br>**designflow**：可借「一题多视角改写」造 EDA 规格题，但答案须可执行验证。 |
| 首次收录 | **2026-11-20**（第七十七轮） |
| 核验状态 | 同 #293 的 arXiv 批量（10,477 B / 4 entry）；OpenAlex **`200`（1,029，ICLR）**；authors/affiliation 另用 arXiv 原生 HTML **`200` / 304,026 B** 核；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。⚠️ **ID 记录更正**：本轮原计划用 `2309.12284` 收 RTLLM，实测该 ID 标题为 **MetaMath**（RTLLM 真 ID = `2308.05345`，早已收录且已发信 #66）⇒ 当场改收 MetaMath，未产生错误条目。 |

---

## 297. Horovod: fast and easy distributed deep learning in TensorFlow

| 字段 | 内容 |
|:--|:--|
| 标题 | Horovod: fast and easy distributed deep learning in TensorFlow |
| 作者（前 3） | Alexander Sergeev · Mike Del Balso（共 **2** 位；arXiv 作者字段逐字核） |
| 年份 | **2018**（arXiv v1 `2018-02-15`；v3 为当前版本） |
| 会议 / 期刊 | **预印本**（arXiv `comment` 为空；OpenAlex `type=preprint`，无会场记录） |
| 被引数 | **1,619**（OpenAlex `10.48550/arxiv.1802.05799`，查询日 **2026-11-21**） |
| arXiv / DOI | <https://arxiv.org/abs/1802.05799> ｜ arXiv DOI `10.48550/arxiv.1802.05799` |
| 一句话贡献 | 把 **ring-allreduce** 做成 TensorFlow 的通用 allreduce 路径（`hvd.allreduce` 等），并用尽量少的代码改动让模型从单卡扩到多卡；论文的核心论点是通信库的**开销**与**改写成本**这两道门槛会让人放弃多卡。 |
| 与我们工作的关系 | **pretrain（主 · 通信成本）**：训练日志应固定记录 allreduce 时间 / step 时间，把「扩卡效率」写成预注册判据；ring 模型的带宽-延迟分解可用于判断瓶颈在链路还是同步频率。<br>**data（数据并行口径）**：全局 batch = 单卡 batch × 卡数 × 梯度累积步数，分片方式会影响有效样本顺序 ⇒ 数据配比实验必须固定这些量。<br>**harness（复现）**：任何「多卡加速」声明都应同时给单卡基线与本机的通信占比。 |
| 首次收录 | **2026-11-21**（第七十八轮） |
| 核验状态 | arXiv `id_list=1802.05799` **`200` + `application/atom+xml`**（`published` `2018-02-15T23:36:51Z`，`primary_category=cs.LG`）；OpenAlex **`200`（1,619，2018，type=preprint）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**（PDF 下载 30 s 内未完成）。 |

---

## 298. Deformable DETR: Deformable Transformers for End-to-End Object Detection

| 字段 | 内容 |
|:--|:--|
| 标题 | Deformable DETR: Deformable Transformers for End-to-End Object Detection |
| 作者（前 3） | Xizhou Zhu · Weijie Su · Lewei Lu（共 **6** 位；末位 Jifeng Dai；arXiv 作者字段逐字核） |
| 年份 | **2020**（arXiv v1 `2020-10-08`；v4 为当前版本） |
| 会议 / 期刊 | **ICLR 2021 Oral**（arXiv `comment` 逐字：`ICLR 2021 Oral`；OpenAlex 仍记 `type=preprint` ⇒ 以 arXiv comment 为准） |
| 被引数 | **8,952**（OpenAlex `10.48550/arxiv.2010.04159`，查询日 **2026-11-21**） |
| arXiv / DOI | <https://arxiv.org/abs/2010.04159> ｜ arXiv DOI `10.48550/arxiv.2010.04159` ｜ 代码 <https://github.com/fundamentalvision/Deformable-DETR> |
| 一句话贡献 | 针对 DETR「收敛慢 + 特征分辨率受限」，把注意力改成**只在参考点周围少量采样点上做**（deformable attention），在 COCO 上以**少 10× 的训练 epoch** 超过 DETR，尤其改善**小目标**。 |
| 与我们工作的关系 | **vision（主 · 检测头）**：给「采样预算 vs 小目标召回」一条可测轴；我们的版图/封装图目标尺度跨两个数量级，可先固定采样点数再扫特征层。<br>**designflow（评分轴）**：稀疏采样 + 集合预测（无 NMS/anchor）适合把「漏检 / 误检」拆成两条独立评分，不与 mAP 混算。<br>**harness（收敛成本）**：把「达到同等精度所需 epoch」作为单独指标记录，避免只看最终分数。 |
| 首次收录 | **2026-11-21**（第七十八轮） |
| 核验状态 | arXiv `id_list=2010.04159` **`200` + atom**（`published` `2020-10-08T17:59:21Z`，`comment=ICLR 2021 Oral`）；OpenAlex **`200`（8,952，2020）**；作者邮箱另用 **ar5iv HTML `200` / 267,916 B** 核对（脚注 `{zhuwalter,luotto,daijifeng}@sensetime.com` / `jackroos@mail.ustc.edu.cn` / `binli@ustc.edu.cn` / `xgwang@ee.cuhk.edu.hk`）；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 299. SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features

| 字段 | 内容 |
|:--|:--|
| 标题 | SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features |
| 作者（前 3） | Michael Tschannen · Alexey Gritsenko · Xiao Wang（共 **14** 位；末位 Xiaohua Zhai；arXiv 作者字段逐字核） |
| 年份 | **2025**（arXiv v1 `2025-02-20`） |
| 会议 / 期刊 | **预印本**（arXiv `comment` 只给 checkpoint 链接，未提会议；OpenAlex `type=preprint`） |
| 被引数 | **1,832**（OpenAlex `10.48550/arxiv.2502.14786`，查询日 **2026-11-21**） |
| arXiv / DOI | <https://arxiv.org/abs/2502.14786> ｜ arXiv DOI `10.48550/arxiv.2502.14786` ｜ 权重 <https://github.com/google-research/big_vision> |
| 一句话贡献 | 在 SigLIP 的图文目标上并入 **caption 预训练 + 自监督损失（自蒸馏 / 掩码预测）+ 在线数据治理**，形成统一配方；各规模在零样本分类、图文检索、VLM 迁移上均优于 SigLIP，并显著改善**定位与稠密预测**；另有支持**多分辨率 / 原生宽高比**的变体与去偏后的数据混合。 |
| 与我们工作的关系 | **vision（主 · 视觉塔选型）**：原生宽高比 + 多分辨率对**长宽比极端的版图截图**是直接相关变量；应作为视觉塔候选与我们现用塔同数据对照。<br>**data（图文对配方）**：caption 预训练与在线治理说明「图文对质量」不只靠离线过滤；去偏前后的配比要留档。<br>**pretrain（分辨率策略）**：多分辨率训练对 token 数与位置编码的影响，可作为 2B 预训练的数据形状预注册项。<br>**designflow**：规格书截图 / 版图注释属稠密特征任务，正好对应本文声称改进的 dense features。 |
| 首次收录 | **2026-11-21**（第七十八轮） |
| 核验状态 | arXiv `id_list=2502.14786` **`200` + atom**（`published` `2025-02-20T18:08:29Z`，`comment` 为 checkpoint 链接）；OpenAlex **`200`（1,832，2025，type=preprint）**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。 |

---

## 候选池（下轮起逐轮补，**被引数本轮未查**，勿引用）

| arXiv ID | 标题（arXiv 实测） | 首次提交 | 拟服务线 | 为什么算经典（待核被引） |
|:--|:--|:--|:--|:--|
| `2303.03378` | ~~PaLM-E~~ ⇒ 已转正 **#281**（⚠️ 旧候选池误记 `2403.03378`，实测为无关物理论文 ⇒ 已更正） | — | — | — |
| `2402.00159` | ~~Dolma~~ ⇒ 已转正 #280 | — | — | — |
| `2308.04079` | ~~3D Gaussian Splatting~~ ⇒ 已转正 **#282** | — | — | — |
| `2310.08560` | MemGPT: Towards LLMs as Operating Systems | 2023-10-12 | harness / zhulong | 已收 #130 ⇒ 勿重复 |
| `1904.00962` | ~~LAMB~~ ⇒ 已收 #175 | — | — | — |

> 维护纪律：候选池只放**未收录**且**被引未实测**的 ID；转正后从本表删去并在条目里写明「首次收录」。🚫 未实测前不写被引数、不写会议。

> ✅ **第七十七轮（2026-11-20 21:0x）转正 4 条**：DETR `2005.12872`（#293，**25,731**，ECCV 2020，LNCS pp. 213–229）· YOLO `1506.02640`（#294，**66,671**，CVPR 2016 pp. 779–788）· Quiet-STaR `2403.09629`（#295，**436**，**&lt;500 按「方法论常青」收**，arXiv 预印本 · `comment` 空）· MetaMath `2309.12284`（#296，**1,029**，ICLR 2024 Spotlight）⇒ B 轨累计 **296**（覆盖轴：集合预测 + 二分匹配去掉 NMS/anchor / 单网络回归的实时检测成本 / 每个 token 都想一下的自监督 thinking / 多视角改写题目自举）。核验：arXiv `id_list` **`200` + `application/atom+xml`**（10,477 B / 4 entry）+ OpenAlex **4/4 `200`**（25,731 / 66,671 / 436 / 1,029，查询日 2026-11-20，含 DETR 与 YOLO 的会议 DOI/页码）；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**（DETR PDF 30 s 内未下完 ⇒ 放弃，如实记）。**先查重**：DETR / YOLO 两 ID 在 `PAPERS.md` 全量正则 **0 命中**；ZeRO `1910.02054` / Ring Attention `2310.01889` 已在表内 ⇒ 不收。⚠️ **ID 误记在写入前拦截**：原计划用 `2309.12284` 收 RTLLM，实测该 ID 为 **MetaMath** ⇒ 改收 MetaMath；RTLLM 真 ID `2308.05345` 早已收录（并已发信 #66），未产生错误条目。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 通信重叠侧（Ring-AllReduce / overlap，ZeRO 已收 ⇒ 只补通信侧）；④ 视觉塔对照补 SigLIP 2（待核一手版本）；⑤ 检测后续（Deformable DETR `2010.04159` / DINO 系列，待核被引）。

> ✅ **第七十五轮（2026-11-20 15:0x）转正 4 条**：SimCLR `2002.05709`（#285，**18,118**，ICML 2020）· NeRF `2003.08934`（#286，**1,186**，ECCV 2020 oral）· ChatEDA `2308.10204`（#287，**319**，IEEE TCAD 43(10):3184–3197, 2024，**&lt;500 按「本领域权威」收**）· Routing Transformers `2003.05997`（#288，**925**，TACL 9:53–68, 2021）⇒ B 轨累计 **288**（覆盖轴：增强组合 + 投影头 + 大 batch 的对比学习配方 / 5D 坐标 + 可微体渲染 / RTL→GDSII 的分解-脚本-执行三段 agent / 在线 k-means 内容稀疏注意力）。核验：arXiv `id_list` 两批均 **`200` + atom**（10,472 B / 4 entry、9,755 B / 4 entry）+ OpenAlex **4/4 `200`**（18,118 / 1,186 / 319 / 925，查询日 2026-11-20）；ChatEDA 另用 arXiv 原生 HTML **`200` / 196,479 B** 读作者与 affiliation；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。**先查重**：四 ID 在 `PAPERS.md` 全量正则 **0 命中**（`1907.11692` RoBERTa / `2012.03112` PIM 综述 / `2308.00113` VeriGen / `2104.14294` DINO / `2304.07193` DINOv2 / `2311.04887` AutoChip / `1406.2661` GAN 均已在表内或仅作候选 ⇒ 本轮不收）。⚠️ **避免一处 ID 误记**：原计划收 **ELECTRA**，按记忆写成 `2003.05997`，实测该 ID 为 **Routing Transformers** ⇒ 当场改收后者（#288）；**ELECTRA 真 ID = `2003.10555`**（arXiv `200` + title 逐字核），留作下轮候选。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① ELECTRA `2003.10555`（真 ID 已核，待核被引）；② Mask R-CNN `1703.06870` / Faster R-CNN `1506.01497`（检测侧空缺）；③ SAC `1801.01290` / DDPG `1509.02971`（连续控制）；④ HBM / JEDEC 一手（连续多轮未命中）；⑤ 通信重叠侧（ZeRO 已收 ⇒ 只补 Ring-AllReduce / overlap）。

> ✅ **第七十四轮（2026-11-20 12:0x）转正 4 条**：PaLM-E `2303.03378`（#281，**4,143**，预印本）· 3D Gaussian Splatting `2308.04079`（#282，**12,239**，ACM TOG）· Magicoder `2312.02120`（#283，**416**，**&lt;500 按「方法论常青」收**）· SGDR `1608.03983`（#284，**11,502**，arXiv `comment` = ICLR 2017）⇒ B 轨累计 **284**（覆盖轴：多模态句子 + 连续状态编码进语言塔 / 各向异性高斯 + 密度控制做实时新视角合成 / 开源片段当种子自造指令数据 / 余弦退火与热重启日程）。核验：arXiv `id_list` 三批全 **`200` + atom**（9,914 B / 4 entry、6,252 B / 2 entry、2,359 B / 1 entry）+ OpenAlex **4/4 `200`**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。**先查重**：四 ID 在 `PAPERS.md` 全量正则 0 命中（`2301.12597` BLIP-2 / `2310.01889` Ring Attention / `2308.03688` AgentBench / `2312.14238` InternVL / `2306.06070` Mind2Web / `1711.05101` AdamW / `1710.03740` Mixed Precision 均已在表内 ⇒ 全部作废）。⚠️ **两处更正**：① 旧候选池把 PaLM-E 记成 `2403.03378`，OpenAlex 实测该 DOI 是 *European Physical Journal C* 的物理论文 ⇒ 真 ID = `2303.03378`；② 旧记录把 SpeechT5 记成 `2010.00718`，实测该 ID 为 *When to Impute? Imputation before and during cross-validation*（stat.ME）⇒ **SpeechT5 的 arXiv ID 仍未核实**（OpenAlex 标题检索到 `2110.07205` 预印本 159 + ACL 2022 版 318），下一轮须先核 ID 再收。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① SpeechT5（先核真 ID，再核 ACL 2022 版被引）；② HBM / JEDEC 一手（连续多轮未命中）；③ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；④ Ring-AllReduce / 通信重叠一侧（ZeRO 已收 ⇒ 只补通信侧）；⑤ 数据质量线「合成数据自举」后续一手（Magicoder 已收 ⇒ 补 Self-Instruct 之后的演进）。
> ✅ **第七十三轮（2026-11-20 09:0x）转正 4 条**：SmoothQuant `2211.10438`（#277，**839**）· Chatbot Arena `2403.04132`（#278，**2,131**）· ALOHA+ACT `2304.13705`（#279，**3,065**，RSS）· Dolma `2402.00159`（#280，**674**，ACL）⇒ B 轨累计 **280**（覆盖轴：W8A8 的逐通道缩放与成本口径 / 人评排行榜的一致性与置信区间 / 动作分块降低复合误差 / 语料构造的中间态验收）。核验：arXiv `id_list` **`200` + atom**（11,794 B / 4 entry）+ OpenAlex **4/4 `200`**；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。**先查重**：四个 ID 在 `PAPERS.md` 全量正则 0 命中。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① PaLM-E `2403.03378`（具身多模态）；② 3D Gaussian Splatting `2308.04079`；③ HBM / JEDEC 一手（连续多轮未命中）；④ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；⑤ 数据质量线「合成数据自举」后续一手。

> ✅ **第七十二轮（2026-11-20 06:0x）转正 4 条**：MMLU `2009.03300`（#273，**6,448**，ICLR 2021）· Qwen2-VL `2409.12191`（#274，**6,170**）· The Pile `2101.00027`（#275，**3,645**）· DeepSeek-V2 `2405.04434`（#276，**1,986**）⇒ B 轨累计 **276**（覆盖轴：57 学科知识基准的聚合与污染 / 原生动态分辨率与三维位置编码 / 语料配比的「比例 × epoch」两旋钮 / MLA 的 KV cache 压缩）。核验：arXiv `id_list` **`200` + atom**（19,377 B / 4 entry）+ OpenAlex **4/4 `200`** + ar5iv HTML **4/4 `200`**（208,166 / 655,463 / 677,121 / 694,593 B），**未做 PDF 逐页复核**。**先查重**：四个 ID 在 `PAPERS.md` 全量正则 0 命中（另核 `2211.09110` HELM / `2107.03374` Codex / `2306.00978` AWQ / `2308.03688` AgentBench / `2306.05685` MT-Bench 均未收录，留作候选）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ HELM `2211.09110`（多场景评测框架）或 Codex `2107.03374`（HumanEval 的原始出处）；④ AWQ `2306.00978`（激活感知权重量化，SLM 部署）；⑤ 合成数据自举后续一手。
> ✅ **第七十一轮（2026-11-20 03:0x）转正 4 条**：C4 文档化 `2104.08758`（#269，**990**，EMNLP 2021 pp. 1286–1305）· ConvNeXt `2201.03545`（#270，**13,910**，CVPR 2022 pp. 11966–11976）· Grokking `2201.02177`（#271，**967**）· Are Emergent Abilities a Mirage? `2304.15004`（#272，**1,116**，NeurIPS 2023 pp. 55565–55581）⇒ B 轨累计 **272**（覆盖轴：网页语料的来源审计 / 纯 ConvNet 的现代化配方 / 过拟合之后的泛化 / 指标选择制造的假涌现）。核验：abs 页 4/4 `200`；OpenAlex 4/4 `200`（990 / 13,910 / 967 / 1,116）；ar5iv HTML 4/4 `200`（207,799 / 476,499 / 106,203 / 151,070 B）核数字，**未做 PDF 逐页复核**。**先查重**：四个 ID 在 `PAPERS.md` 全量正则 0 命中。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 合成数据自举后续一手；④ EDA 第二篇可执行判分（换 OpenROAD 指令集方向）；⑤ 视觉侧补 AIMv2 / DFN 与 #270 对照。
> ✅ **第七十轮（2026-11-20 00:0x）转正 4 条**：Transformer-XL `1901.02860`（#265，**1,881**）· Emu3 `2409.18869`（#266，**1,022**）· Medusa `2401.10774`（#267，**1,028**）· Janus `2410.13848`（#268，**633**，CVPR 2025 pp. 12966–12977）⇒ B 轨累计 **268**（覆盖轴：段级递归 + 相对位置编码 / 全离散 token 统一理解与生成 / 多解码头投机解码的无损档 / 理解与生成双编码器解耦）。核验：arXiv `id_list` 本轮 **`429`** ⇒ 改用 **abs 页 `citation_*` 4/4 `200`**（标题 / 作者 / 首次提交日齐全，如实记）；OpenAlex 4/4 `200`；PDF 4/4 `200` 但**全部截断**（无 `%%EOF`、`pdftotext` 失败）⇒ 数字改用 **ar5iv HTML 4/4 `200`**（312,920 / 267,946 / 319,495 / 317,703 B）核对。**先查重**：四个 ID 在 `PAPERS.md` 全量正则 0 命中（另核 `2307.08691` FlashAttention-2 / `1811.06965` GPipe / `1910.02054` ZeRO / `1909.08053` Megatron-LM 均已在表内 ⇒ 不收）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 合成数据自举后续一手；④ EDA 第二篇可执行判分（VerilogEval 已在表内 ⇒ 换 OpenROAD 指令集方向）；⑤ 长上下文位置编码续（NTK-aware 一手）。
> ✅ **第六十九轮（2026-11-19 21:0x）转正 4 条**：Transfusion `2408.11039`（#261，**588**）· Agentless `2407.01489`（#262，**1,053**，PACM SE Vol. 2 Issue FSE pp. 801–824, 2025）· Massive Activations `2402.17762`（#263，**444**，**&lt;500 按「方法论常青」收**）· EDA Corpus `2405.06676`（#264，**38**，**&lt;500 按「本领域权威」收**，IEEE LAD 2024 pp. 1–5）⇒ B 轨累计 **264**（覆盖轴：文本因果 / 图像双向的混合注意力与双损失 / 固定三段流水线作为 agent 基线 / 巨值激活＝隐式 bias 项 / 脚本必须在 OpenROAD 里真跑才算对）。核验：arXiv `id_list` 4/4 `200` + OpenAlex 4/4 `200`；PDF 2/4 完整（1,384,716 / 453,822 B，`%PDF-` + `pdftotext` 均通过），2/4 `content-length` 14,087,563 / 7,636,655 B **>5 MB 未落盘** ⇒ 数字用 ar5iv 2/2 `200`（300,229 / 271,351 B）核对。⚠️ **本轮拦下一处 ID 误记**：候选池/检索时记的「EDA Corpus `2405.07288`」实测是 *Erasing Concepts from Text-to-Image Diffusion Models with Few-shot Unlearning*（OpenAlex 被引 34，与 EDA 无关）⇒ 按标题检索得真 ID **`2405.06676`**（被引 **38**，IEEE LAD 2024）后才收录；**旧记作废**。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中，改试 `ti:` + 会议论文集）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手，本轮 #263 已补「异常激活」侧）；③ 数据质量线「合成数据自举」后续一手；④ EDA 侧第二篇可执行判分语料（VerilogEval `2309.07544` 已在表内 ⇒ 换 ChipNeMo 后续或 OpenROAD 指令集工作）；⑤ 长上下文位置编码续（NTK-aware 一手）。

> ✅ **第六十六轮（2026-11-19 15:0x）转正 3 条**：ULMFiT `1801.06146`（#250，**6,245**，ACL 2018 pp. 328–339）· DPR `2004.04906`（#251，**8,667**，EMNLP 2020 pp. 6769–6781）· SpecAugment `1904.08779`（#252，**4,968**，Interspeech 2019 pp. 2613–2617）⇒ B 轨累计 **252**（覆盖轴：小数据域内微调的三个旋钮 `η_{l-1}=η_l/2.6` / `cut_frac=0.1` / `ratio=32` / 逐层解冻 1 epoch / 50 epochs · 检索负例构造 in-batch + 每条 1 个 BM25 难负例 / batch 128 / `λ=1.1` · 谱域结构化遮挡的策略表 `(W, F, m_F, T, p, m_T)`）。两篇 PDF 与 `Content-Length` 对齐（979,417 / 383,508 B），SpecAugment PDF 3,733,556 B **下载中途被截断**（本地 1,683,456 B、`pdftotext` 报 xref 错误）⇒ 该篇数字改由 **ar5iv HTML `200`** 核对并如实标注「未做 PDF 逐页复核」。<br>⚠️ **本轮纠一处会议误记**：15:0x 草稿备注把 DPR 写成「ACL 2020」⇒ OpenAlex 实测为 **EMNLP 2020**（pp. 6769–6781，DOI `10.18653/v1/2020.emnlp-main.550`），已在 #251 内留痕。<br>⚠️ **候选池陈旧项结清**：旧候选「SpeechT5 `2010.00718`（元数据已核未收）」**早已作废**——该 ID 实为 *When to Impute?*，SpeechT5 真 ID `2110.07205` 已于第四十四轮转正为 **#172**；后续轮次反复抄写此行属笔误，本轮一并删除。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 数据质量线「合成数据自举」一手；④ 视觉侧「统一 token 词表」对照（Transfusion `2408.11039` 待核）；⑤ 长上下文位置编码续（NTK-aware 一手）。

> ✅ **第六十五轮（2026-11-19 12:0x）转正 4 条**：BART `1910.13461`（#246，**15,049**，ACL 2020 pp. 7871–7880）· Chameleon `2405.09818`（#247，**1,262**）· Qwen-VL `2308.12966`（#248，**5,222**）· RWKV `2305.13048`（#249，**830**）⇒ B 轨累计 **249**（覆盖轴：去噪目标的五种加噪与 `Poisson(λ = 3)` / 早期融合的统一 token 词表 / 视觉分辨率与框接口 / 线性注意力的 `O(Td)` 成本）。两篇 PDF >5 MB（25,245,551 / 6,329,953 B）**未落盘**，改用 ar5iv HTML 2/2 `200` 核数字并如实标注；另两篇 PDF 与 `Content-Length` 对齐（296,072 / 1,590,242 B）。<br>⚠️ **本轮纠一处 ID 误记**：候选池/记忆里「Muon 原论文 `2410.21276`」**实测是 *GPT-4o System Card***（OpenAlex `200`，11,351）⇒ 该 ID **不收**；Muon 的可引论文是 **`2502.16982`（Muon is Scalable for LLM Training，已收 #181）**，Muon 本身的原始描述是博客而非 arXiv 论文。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手，本轮 Chameleon 已补 QK-Norm 消融）；③ 视觉侧「统一 token 词表」对照（Transfusion `2408.11039` 待核）；④ 存储侧近存 / HBM 一手；⑤ EDA 侧 LLM-for-EDA 新一手（ASAP7 / OpenROAD 流程耦合）。

> ✅ **第六十轮（2026-11-18 21:0x）转正 4 条**：Zero Bubble `2401.10241`（#228，**100**，**&lt;500 按「奠基 / 开创范式」收**，理由：同步训练语义下首个「零空泡」PP 调度，此前共识是 bubble 不可避免）· FP8 Formats `2209.05433`（#229，**593**，NVIDIA 技术报告，E4M3/E5M2 分工 + 缩放因子放软件）· SigLIP 2 `2502.14786`（#230，**1,822**，四档 86M–1B + 109 语言 + NaFlex）· Pythia `2304.01373`（#231，**761**，ICML 2023，16 模型 × 154 checkpoint、Pile 300B vs 去重 207B）⇒ B 轨累计 **231**（覆盖轴：PP 空泡与内存换吞吐 / FP8 格式与 scaling 口径 / 视觉塔尺寸与稠密任务配方 / 可复现训练轨迹作评测对照尺）。四篇均 arXiv `id_list` + OpenAlex + PDF 三源实测；PDF 尺寸 649,126 / 281,195 / 623,539 / 1,091,147 B（**全部 ≤5 MB，不入 git**）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中，改试 `ti:` 与会议论文集）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 数据质量线「合成数据自举」后续一手；④ 视觉侧可补 AIMv2 / DFN（与 #230 的对照）；⑤ 长上下文位置编码续（YaRN 已收 ⇒ 可补 NTK-aware 一手）。<br>⚠️ 本轮**候选池结清**：旧记「Zero Bubble 实测 90 ⇒ 暂留」→ 本轮实测 **100**，按「奠基」收（不再以被引阈值卡）；旧记「SigLIP 2 待核一手」→ 已核 `2502.14786` 并收。<br>
> ✅ **第五十九轮（2026-11-18 18:0x）转正 3 条**：DeepSeekMoE `2401.06066`（#225，**1,590**）· Small-scale proxies `2309.14322`（#226，**139**，**&lt;500 按「方法论常青」收**，理由：小模型复现大模型 loss spike 的标准参照）· Mixed Precision Training `1710.03740`（#227，**2,697**，ICLR 2018）⇒ B 轨累计 **227**（覆盖轴：MoE 专家粒度 `0.25×/0.125×` 与两级均衡系数 0.01/0.001 / 注意力 logit > `1e4` 即发散 + 4.8B 先预测后验证 / FP32 master weights + loss scaling 8–32K + 溢出跳过）。三篇均 arXiv + OpenAlex + PDF 三源实测；PDF 尺寸 733,666 / **10,685,777** / 1,404,641 B（>5 MB 那篇只留 `/tmp`）。⚠️ 本轮**先纠一处 ID 误记**：候选池旧记「spike 侧 2209.14389」**实测是 *Downstream Datasets Make Surprisingly Good Pretraining Corpora***，真 ID = **`2309.14322`**（按标题检索确认，首作者 Wortsman）⇒ 旧记作废。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 长上下文调度侧（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）；③ 视觉侧 SigLIP 2（待核一手 arXiv 版本）；④ 数据质量线「合成数据自举」一手工作；⑤ FP8 / 低精度训练一手（Mixed Precision 已收 ⇒ 可补 FP8 格式与 scaling 侧）。
> ✅ **第五十八轮（2026-11-18 15:0x）转正 2 条**：OLMoE `2409.02060`（#223，**374**，**&lt;500 按「方法论常青」收**）· Ring Attention `2310.01889`（#224，**508**，NeurIPS 2023）⇒ B 轨累计 **224**（覆盖轴：全开放 MoE 的「激活参数对齐」消融与路由饱和 / 长上下文的硬件常数 `c = FLOPS/Bandwidth` 与 MFU 口径）。本轮只加 2 条的原因：两篇 PDF 下载被上游限速（6,501,620 B 用了约 9 分钟，Ring Attention 同样慢），时间预算优先保证「三源实测 + `pdftotext` 逐条核数字」，🚫 不凭记忆补条目。另**更正**历史候选：`2404.12358` 实测是 **From r to Q\*（280 被引）**，**不是 DBRX** ⇒ 从候选池移除（DBRX 只有官方博客，无 arXiv 一手论文）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 长上下文调度侧（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）；④ MoE 侧可补 DeepSeekMoE `2401.06066`（待核被引 / PDF）；⑤ 视觉侧可补 SigLIP 2（待核一手版本）。
> ✅ **第五十七轮（2026-11-18 12:0x）转正 3 条**：Qwen3 `2505.09388`（#220，**19,693**，技术报告）· OLMo 2 `2501.00656`（#221，**870**，COLM 2025）· AutoChip `2311.04887`（#222，**247**，**&lt;500 按「本领域权威」收**）⇒ B 轨累计 **222**（覆盖轴：thinking/non-thinking 合一的 budget 机制 + 两段式训练与退火配比 + HDL 生成-仿真反馈闭环）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① OLMoE `2409.02060`（OpenAlex 实测 **374**，全开放 MoE，PDF 未取）；② DBRX `2404.12358`（早前 OpenAlex 已实测，未收）；③ Tulu 3 已收 #213 ⇒ 不重复；④ HBM / JEDEC 一手（连续多轮未命中）；⑤ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）。
> ✅ **第五十六轮（2026-11-18 09:0x）转正 3 条**：StarCoder 2 `2402.19173`（#217，**1,095**，预印本 TMLR under review）· Magpie `2406.08464`（#218，**353**，**&lt;500 按「方法论常青」收**，理由：只用前置模板自举指令，已被后续数据合成工作当基线）· Jamba `2403.19887`（#219，**789**，预印本）⇒ B 轨累计 **219**。⚠️ 该轮如实记三处未核：① Magpie / Jamba 的 arXiv `id_list` 当时 `429`/`000` ⇒ 首次提交日留白；② 两篇会议信息未核；③ StarCoder 2 全文无个人邮箱。


> ✅ **第五十五轮（2026-11-18 06:0x）转正 4 条**：Tülu 3 `2411.15124`（#213，**1,670**，预印本技术报告）· DSPy `2310.03714`（#214，**1,261**，预印本，仅 v1）· OpenHands `2407.16741`（#215，**1,050**，ICLR 2025）· SAM 2 `2408.00714`（#216，**5,632**，预印本技术报告）⇒ B 轨累计 **216**（覆盖轴：后训练 SFT→DPO→RLVR 三段配方 / 指标驱动的 prompt 编译 / 外壳即平台（runtime + 事件流）/ 视觉 streaming memory）。四篇均 arXiv `id_list` + OpenAlex + PDF 三源实测；`pdftotext` 逐篇核到关键数字（`>25% and 65%` / `resolve rate of 26%` / `35.5M masks across 50.9K videos` / `Reinforcement Learning with Verifiable Rewards`）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① Magpie `2406.08464`（实测 353，<500 ⇒ 需先写明「方法论常青」理由）；② HBM / JEDEC 一手（连续多轮未命中）；③ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；④ 长上下文调度（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）；⑤ StarCoder 2 `2402.19173`（本轮实测 **1,095**，可作 The Stack v2 数据侧补充，下轮优先）。
> ✅ **第五十四轮（2026-11-18 03:0x）转正 3 条**：VeriGen `2308.00708`（#210，**533**，ACM TODAES / 前身 DATE 2023）· WebShop `2207.01206`（#211，**1,765**，NeurIPS 2023）· ChipNeMo `2311.00176`（#212，**472**，预印本技术报告，**&lt;500 按「本领域权威」收**）⇒ B 轨累计 **212**。⚠️ **本轮先纠了两处历史误记**：① VeriGen 的 PDF 本轮三端点可取（2,636,063 B，`%PDF-`）⇒ 00:00 轮「PDF 不可达 ⇒ 不进表」的暂缓正式解除；② 候选池早前写 WebShop「358」被引，本轮 OpenAlex 实测 **1,765**（`2207.01206`）⇒ 以本轮实测为准，旧数字作废。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① Magpie `2406.08464`（本轮实测 **353**，&lt;500 ⇒ 需先写明「方法论常青」理由才收）；② HBM / JEDEC 一手（连续多轮未命中）；③ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；④ 长上下文调度（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）。
> ✅ **第五十三轮（2026-11-18 00:0x）转正 3 条**：DCLM `2406.11794`（#207，**627**，NeurIPS 2024 D&B）· AdamW `1711.05101`（#208，**34,224**，ICLR 2019）· Prismatic VLMs `2402.07865`（#209，**325**，ICML 2024，**&lt;500 按「方法论常青」收**）⇒ B 轨累计 **209**。⚠️ 本轮**更正一个错误 ID**：VeriGen 不是 `2308.00113`（实测为水印论文 *Three Bricks*），真 ID = `2308.00708`（OpenAlex **531**）；但该文 PDF 三端点均 `000`/`404`（多次重试 + 后台下载未拿到完整文件）⇒ 按三源纪律**不进表**，留 06:00 首选项。
> ✅ **第五十二轮（2026-11-17 18:0x）转正 4 条**：GPQA `2311.12022`（#203，**2,204**，预印本）· MMMU `2311.16502`（#204，**2,994**，CVPR 2024 Oral）· LAION-5B `2210.08402`（#205，**1,963**，NeurIPS 2022 D&B）· MATH `2103.03874`（#206，**7,734**，NeurIPS 2021）⇒ B 轨累计 **206**（覆盖轴：抗检索难题口径 / 多模态判分与图表读图 / 图文对过滤阈值 / 数学判分与难度分层）；四篇均为 15:00 时窗因外网阻断而 `BLOCKED` 的候选，本轮网络恢复后**逐条重跑**（arXiv API + OpenAlex + PDF 三源实测），🚫 无一条凭记忆补数字。
> ✅ **第五十一轮（2026-11-17 12:0x）转正 4 条**：InternVL `2312.14238`（#199，**3,950**，CVPR 2024）· Phi-3 `2404.14219`（#200，**3,285**，预印本）· FineWeb `2406.17557`（#201，**1,799**，NeurIPS 2024 D&B）· OLMo `2402.00838`（#202，**908**，ACL 2024）⇒ B 轨累计 **202**（覆盖轴：视觉塔 6B 与像素重排 / 小模型 3.3T token 数据配方 / 96 快照去重与过滤消融 / 全开放权重+数据+代码+日志）。
> ⚠️ 本轮**先查重后才收**：原拟的 ViT `2010.11929`（#88）/ DINOv2 `2304.07193`（#89）/ MAE `2111.06377`（#97）/ Dolma `2402.00159` 均**已在表内** ⇒ 全部作废、改收上述 4 条（教训：`PAPERS.md` 的 ID 提取要用正则全量扫，别只 grep 标题）。
> **下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① DCLM `2406.11794`（实测 **627**，可作 FineWeb 对照）；② Qwen2 `2407.10671`（实测 **5,379**，但 Qwen2.5 / Qwen2-VL 已收 ⇒ 只在需要「同族版本对照」时收）；③ HBM / JEDEC 一手（连续多轮未命中）；④ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；⑤ Magpie `2406.08464`（**300**）/ WebShop `2207.01206`（**358**）仍 <500，暂留。
> ✅ **第五十轮（2026-11-17 09:0x）转正 4 条**：Qwen2.5 `2412.15115`（#195，**11,888**，预印本）· Gemma `2403.08295`（#196，**3,803**，预印本）· Diffusion Policy `2303.04137`（#197，**2,313**，RSS 2023）· Open X-Embodiment `2310.08864`（#198，**1,045**，预印本）⇒ B 轨累计 **198**（覆盖轴：小模型数据过滤与上下文课程 / 小模型架构分叉与词表 / 动作 chunk 与 receding horizon / 跨本体数据混配与技能分类）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① Magpie `2406.08464`（**300**，实测 &lt;500 ⇒ 暂留）/ WebShop `2207.01206`（**358** ⇒ 暂留）；② HBM / JEDEC 一手（连续多轮未命中）；③ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；④ 长上下文调度（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）；⑤ 数据线可补 Dolma `2402.00159`（本轮未查被引）。
> ✅ **第四十九轮（2026-11-17 06:0x）转正 4 条**：The Stack `2211.15533`（#191，553，预印本）· Code Llama `2308.12950`（#192，4,881，预印本）· Qwen2-VL `2409.12191`（#193，6,157，预印本）· LiveCodeBench `2403.07974`（#194，1,802，预印本）⇒ B 轨累计 **194**（覆盖轴：代码语料许可过滤 / 代码专化与 FIM 目标 / 动态分辨率视觉塔 / 免污染时间切窗评测）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① Magpie `2406.08464`（**300**，实测 &lt;500 ⇒ 暂留）/ WebShop `2207.01206`（**358** ⇒ 暂留）；② HBM / JEDEC 一手（连续多轮未命中）；③ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；④ 长上下文调度（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）；⑤ 数据线可补 Dolma `2402.00159`（本轮未查被引）。
> ✅ **第四十八轮（2026-11-17 03:0x）转正 4 条**：MT-Bench / LLM-as-a-Judge `2306.05685`（#187，5,326，NeurIPS 2023 D&B）· Self-Rewarding LMs `2401.10020`（#188，664，ICML 2024）· TinyStories `2305.07759`（#189，589，预印本）· Mind2Web `2306.06070`（#190，503，NeurIPS 2023 Spotlight）⇒ B 轨累计 **190**（覆盖轴：judge 可靠性 / 自奖励对齐 / 受控词表合成数据 / 通用 Web agent 三切分）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① **Magpie `2406.08464`**（实测 **300** 被引，<500 ⇒ 暂不收，若按「方法论常青」需先在条目里写明理由）；② **WebShop `2207.01206`**（实测 **358**，NeurIPS 2023 D&B ⇒ 同理暂留）；③ HBM / JEDEC 一手（连续多轮未命中）；④ 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；⑤ 长上下文调度（Zero Bubble `2401.10241` 实测 90 ⇒ 暂留）。<br>> ✅ **第四十七轮（2026-11-17 00:0x）转正 4 条**：AlphaCode `2203.07814`（#183，1,787，Science 2022）· BLOOM `2211.05100`（#184，2,860，预印本）· StarCoder `2305.06161`（#185，1,518，预印本）· HH-RLHF `2204.05862`（#186，5,138，预印本）⇒ B 轨累计 **186**（覆盖轴：执行式过滤 / 多语数据治理 / 代码语料许可 / 对齐偏好数据）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike）；③ 长上下文调度（Zero Bubble `2401.10241` 实测 90 被引 ⇒ 暂留候选）；④ 数据质量线「合成数据自举」后续一手工作。<br>> ✅ **第四十六轮（2026-11-16 21:0x）转正 4 条**：LIMA `2305.11206`（#179，904，NeurIPS 2023）· The False Promise `2305.15717`（#180，304，ICLR 2024 spotlight，**&lt;500 按「方法论常青」收**）· Muon is Scalable `2502.16982`（#181，622，预印本）· FlashAttention-3 `2407.08608`（#182，418，NeurIPS 2024，**&lt;500 按「开创范式 + 方法论常青」收**）⇒ B 轨累计 **182**。
> **下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手资料（连续多轮未命中，下轮先试 `ti:` + 会议论文集）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手工作，μP 与 Muon 已收）；③ 长上下文系统的调度侧（Zero Bubble `2401.10241` 本轮实测仅 **90** 被引 ⇒ 暂不收，留候选）；④ 数据质量线「合成数据自举」的后续一手工作。
> ✅ **第四十五轮（2026-11-16 18:0x）转正 4 条**：LAMB `1904.00962`（#175，932，ICLR 2020）· Layer Normalization `1607.06450`（#176，12,853，预印本）· StreamingLLM `2309.17453`（#177，1,248，ICLR 2024）· Nucleus Sampling `1904.09751`（#178，2,832，ICLR 2020）⇒ B 轨累计 **178**。
> **下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手资料（须先核可获得性，已连续多轮未命中）；② 数据质量线「合成数据自举」的后续一手工作；③ 长上下文续（位置外推的一手实验对照，已收 YaRN / LongRoPE / StreamingLLM）；④ 训练稳定性 spike 侧（μP 已收，可补 QK-clip / loss-spike 一手工作）。
> ✅ **第四十四轮（2026-11-16 15:0x）转正 4 条**：Swin `2103.14030`（#171，38,712，ICCV 2021）· SpeechT5 `2110.07205`（#172，141，ACL 2022，**&lt;500 按「开创统一模态范式」收**；⚠️ 旧候选 ID `2010.00718` 实为 `When to Impute?`，已更正为 `2110.07205`）· GPipe `1811.06965`（#173，1,280，NeurIPS 2019）· Scaling Data-Constrained `2305.16264`（#174，254，NeurIPS 2023，**&lt;500 按「方法论常青」收**）⇒ B 轨累计 **174**。




> ✅ **第四十三轮（2026-11-16 12:0x）转正 4 条**：Gemini 1.5 `2403.05530`（#167，4,633，预印本技术报告）· RTLLM `2308.05345`（#168，301，ASP-DAC 2024，按「本领域权威」）· VerilogEval `2309.07544`（#169，359，ICCAD 2023 Invited，按「本领域权威」）· PIM Benchmarking `2105.03814`（#170，285，IEEE Access 2022，按「本领域权威」）⇒ B 轨累计 **170**。
> **下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① SpeechT5 `2010.00718`（元数据已核未收）；② 数据质量线「合成数据自举」一手工作；③ HBM / JEDEC 一手资料（须先核可获得性）；④ 长上下文续（位置外推类一手实验）。


> ✅ **第三十六轮（2026-11-15 15:0x）转正 4 条**：Whisper `2212.04356`（#138，3,720）· Gato `2205.06175`（#139，876，TMLR 2022）· SGLang `2312.07104`（#140，812，NeurIPS 2024）· Self-Consistency `2203.11171`（#141，5,587，ICLR 2023）⇒ B 轨累计 **141**。
> **下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① 语音 / 多模态接口线（Whisper 已收；可核 wav2vec 2.0 与 SpeechT5 的一手版本）；② 服务端调度线（continuous batching 的原始工作，Orca `2306.02707` 已收）；③ 测试时算力线（verifier / Best-of-N 的原始论文，CoT 与 Self-Consistency 已收）；④ 存储方向（HBM / GDDR 一手综述或 JEDEC 标准文档，须先核可获得性，未核不得登记）。




> 只登记「已实测 arXiv 元数据」的条目；被引数待下轮 OpenAlex 批量核过再写，**本表数字一律留空 = 未查**。
>
> ✅ **第三十七轮（2026-11-15 18:0x）转正 4 条**：wav2vec 2.0 `2006.11477`（#142，3,140）· Multi-Query Attention `1911.02150`（#143，872）· BitNet b1.58 `2402.17764`（#144，496，按「开创范式」入选）· Reward Model Overoptimization `2210.10760`（#145，291，按「方法论常青」入选）⇒ B 轨累计 **145**。
> ✅ **第三十八轮（2026-11-15 21:0x）转正 4 条**：HuBERT `2106.07447`（#146，3,561）· Tensor Programs V（μP）`2203.03466`（#147，302，按「开创范式」入选）· Training Verifiers（GSM8K）`2110.14168`（#148，11,462）· Emergent Abilities `2206.07682`（#149，4,208）⇒ B 轨累计 **149**。
> **下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① 语音侧（SpeechT5 `2010.00718` 上轮已核元数据但未收录；可核其 abs 页与 OpenAlex 被引后决定）；② 训练稳定性（QK-clip / loss spike 的一手工作，μP 已收 ⇒ 只补 spike 侧）；③ 存储方向（HBM / GDDR 一手综述或 JEDEC 标准文档，须先核可获得性）；④ 数据质量线（去重 `2107.06499` 已收 ⇒ 可补「合成数据自举」的一手工作）。
>
> ✅ **第二十七轮候选去向（2026-11-14 12:0x 结清）**：㉔ 视频世界模型线 ⇒ 已转正 **#108 Genie `2402.15391`**（⚠️ **更正**：先用 `10.48550/arxiv.2402.08015` 查 OpenAlex 返回 **Walia-LLM**（阿姆哈拉语 LLaMA 微调）⇒ 该 ID **不是 Genie**；按标题检索得真 ID **`2402.15391`**，25 人作者名单逐字一致后才收录）（Genie 2 只有官方博客、无一手论文 ⇒ 不单独收，只在 #108 备注）；㉕ 存储 / 内存墙补充 ⇒ 已转正 **#109 Hitting the Memory Wall**（1995，1,783；HBM 一手论文 / JEDEC 标准本轮 `ti:` 未命中可用一手条目 ⇒ 留待下轮）；㉖ EDA 大模型位置 ⇒ **ChipNeMo 早于第二轮已收（#5）**，本轮不重复收；另补 **#110 Deep Learning（Nature 2015）/ #111 AlexNet** 两条视觉—预训练源头。
> ⚠️ 第十轮把 **Llama 2 `2307.09288` / LLaVA-1.5 `2310.03744` / SWE-agent `2405.15793` / Tree of Thoughts `2305.10601`** 四条转正为 #36–#39；**第十一轮把 Llama 3 `2407.21783` / RT-1 `2212.06817` / Christiano 2017 `1706.03741` / Stiennon 2020 `2009.01325`** 四条转正为 #40–#43；**第十二轮把 τ-bench `2406.12045` / TD-Gammon（CACM `10.1145/203330.203343`）/ Sora 技术报告 / Kimi K2 `2507.20534`** 四条转正为 #44–#47（元数据 + 被引当场实测）。✅ **必读清单 37/37 条目已全部覆盖**，此后以「补充 / 更正」为主。
> ⚠️ **更正**：候选池此前记的「Kimi 月之暗面早期报告 `2401.14185`」**实测为 `TDFNet`（音视频语音分离，cs.SD），与 Kimi 无关** ⇒ 已删除该候选，改收 **Kimi K2 `2507.20534`**（已转正 #47）。
> **下轮候选（🚫 未实测前不进本表、不写 DOI / 被引）**：① ~~DPO / Mamba-2 / FlashAttention-2 / 存储方向~~ ⇒ **第十三轮已转正 #48–#51**；② ~~Zephyr / CircuitNet / Bitter Lesson / SimPO~~ ⇒ **第十四轮已转正 #52–#55**；③ ~~ORPO / IPO / Lost in the Middle / vLLM~~ ⇒ **第十五轮已转正 #56–#59**；④ ~~KTO `2402.01306` / KV cache 压缩（H₂O）/ 指令数据自举（Self-Instruct）/ MoE（Switch）~~ ⇒ **第十六轮已转正 #60–#63**；⑤ ~~版图布局（AlphaChip）/ 长上下文位置编码（YaRN）/ speculative decoding / 量化（GPTQ）~~ ⇒ **第十七轮已转正 #64–#67**；⑥ ~~**EDA 评测基座**（OpenROAD / ORFS 相关一手工作）~~ ⇒ **第十八轮已转正 #68**（OpenROAD DAC 2019，216）；⑦ ~~**长上下文续**（LongRoPE / 位置插值对照）~~ ⇒ **第十八轮已转正 #69**（LongRoPE `2402.13753`，302）；⑧ ~~**存储方向补充**（DRAM 模拟 / 近存计算）~~ ⇒ **第十八轮已转正 #70 Ramulator（799）/ #71 RowHammer（967 / 528 双记录）**；⑨ ~~**近存计算源头**（A Case for Intelligent RAM, Patterson et al. 1997，729）~~ ⇒ **第十九轮已转正 #75**（OpenAlex 摘要/作者/卷期已核）；⑨b **并行训练底座**（Megatron-LM `1909.08053`，3,281）⇒ **第十九轮已转正 #72**；⑨c **MoE 训练配方**（DeepSeek-V3 `2412.19437`，7,939）⇒ **第十九轮已转正 #73**；⑨d **通用 agent 基准**（GAIA `2311.12983`，526）⇒ **第十九轮已转正 #74**；⑩ **ORFS / OpenROAD 后续**（Leveling Up: A Trajectory of OpenROAD…, 2022，**13** ⇒ 只作补充）；⑪ ~~**DRAM 模拟对照**（DRAMsim3，2020，**372**，DOI `10.1109/LCA.2020.2973991`）~~ ⇒ **第二十轮已转正 #79**（OpenAlex 直查 372、卷期页码已核）；⑫ ~~**量化微调**（QLoRA `2305.14314`）~~ / ⑬ ~~**统一文本到文本框架**（T5 `1910.10683`）~~ / ⑭ ~~**检索增强生成**（RAG `2005.11401`）~~ ⇒ **第二十一轮已转正 #80–#82**；⑮ **ORFS / OpenROAD 后续**（Leveling Up: A Trajectory of OpenROAD…, 2022，**13** ⇒ 只作补充，不作主线）；⑯ ~~**蒸馏源头**（Distilling the Knowledge in a Neural Network `1503.02531`）~~ / ⑰ ~~**分组查询注意力**（GQA `2305.13245`）~~ / ⑱ ~~**解释轨迹蒸馏**（Orca `2306.02707`）~~ / ⑲ ~~**滑窗注意力开源模型**（Mistral 7B `2310.06825`）~~ ⇒ **第二十二轮已转正 #84–#87**；⑳ ~~**工具自举**（Toolformer `2302.04761`）~~ ⇒ **第二十一轮已转正 #83**。**第二十六轮后下轮候选（🚫 未实测前不进本表、不写 DOI / 被引）**：~~㉑ 图像/视频生成线（Latent Diffusion `2207.11240`）~~ ⇒ **第二十七轮已转正 #104**（⚠️ 真 ID **`2112.10752`**，`2207.11240` 实为 Discrete Key-Value Bottleneck）；~~㉒ EDA 布局生成线（AutoDMP / DREAM-GAN, ISPD 2023）~~ ⇒ **第二十七轮已转正 #106 / #107**（均**无 arXiv**，按「本领域权威」收）；~~㉓ RL 探索/规划线（MuZero）~~ ⇒ **第二十七轮已转正 #105**（Nature 2020 版；与 AlphaZero #7 配对）。**第二十七轮后下轮候选（🚫 未实测前不进本表、不写 DOI / 被引）**：㉔ **视频世界模型线**（Sora #46 已有；可补 **Genie / Genie 2** 系列，须核一手）；㉕ **存储 / 内存墙补充**（HBM 相关一手论文或 JEDEC 标准文档，须核可获得性）；㉖ **EDA 大模型位置**（ChipNeMo, NVIDIA 2023，若 OpenAlex 被引足够或按「本领域权威」收）。


| arXiv ID | 标题（arXiv 实测） | 首次提交 | 拟服务线 | 为什么算经典（待核被引） |
|:--|:--|:--|:--|:--|
| — | （本轮无新增候选，待下轮实测后填） | — | — | — |

> ✅ **第七十八轮（2026-11-21 00:0x）转正 3 条**：Horovod `1802.05799`（#297，**1,619**，预印本）· Deformable DETR `2010.04159`（#298，**8,952**，ICLR 2021 Oral）· SigLIP 2 `2502.14786`（#299，**1,832**，预印本）⇒ B 轨累计 **299**（覆盖轴：数据并行 ring-allreduce 的通信成本基线 / 参考点稀疏采样把收敛压 10× / 视觉塔的统一图文配方与原生宽高比）。核验：arXiv `id_list` 单篇 **3/3 `200` + atom** + OpenAlex **3/3 `200`**（查询日 2026-11-21）；数字取自 arXiv 官方摘要，**未做 PDF 逐页复核**。**先查重**：三 ID 在 `PAPERS.md` / `SEEN.md` / `papers.jsonl` 全量正则均 **0 命中**（`1802.05799` 与此前「Ring-AllReduce 通信侧」候选一致，未与 ZeRO `1910.02054` 重复）。<br>**下轮候选（🚫 未实测前不进表、不写 DOI / 被引）**：① HBM / JEDEC 一手（连续多轮未命中）；② 训练稳定性 spike 侧（QK-clip / loss-spike 一手）；③ 检测后续（DINO 系列 / Mask DINO）；④ 视觉塔对照补 SigLIP 原文 `2103.00020` 已在表内 ⇒ 改补 EVA / InternViT 一手；⑤ 存储墙侧（PIM 综述已收 ⇒ 补近三年 HBM 实测论文）。

> ✅ 已晋级（第三轮转正，勿再留在候选池）：`2104.09864` RoFormer（#9）· `2310.06770` SWE-bench（#10）· `2303.11366` Reflexion（#11）· `2201.11903` CoT（#12）。

<!-- 维护纪律：新条目按「首次收录日」追加到末尾（不插入到旧条目之间、不改历史数字）；被引数变动只在新条目里写，旧条目保留原查询日。 -->
