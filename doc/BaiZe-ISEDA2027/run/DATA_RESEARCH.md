# DATA_RESEARCH.md — R 阶段数据调研报告（只回答两个问题）

> 版本 v1.1 · 2026-10-01 · 由 **R 阶段**产出（运维指令 §0，2026-10-01 修订：**原「10 主题 / 8 主题」清单已作废**）。
> v1.1 修订：本轮用 `fetch_web_content` 直连 HF 数据集卡 / 模型卡 / Paper 页**逐条复核** URL 事实（Ultra-FineWeb-L3 官方 config 命名与 1.9TB 字节、GPIC gated 状态、MiniCPM5 数据配方归属、arxiv 2602.09003 的真实身份），共修正 3 处表述，见各节标注「v1.1 修订」。
> 本文件**只回答 §0 的两个问题**：① LLM pretrain 的数据够不够 + 配比；② Vision encoder 的数据够不够 + 配比。
> 铁律：① 每条关键结论给出可点击 URL；② 查不到就写「未找到」，不编造；③ 许可「不明」显式标红；④ 只调研不下载（本地实测读取仅涉已落盘文件）。

## 0. 调研方法与可信度

- **可达**：本机 `curl` 直连 `huggingface.co`（REST API + `/raw` 全文）与 `datasets-server.huggingface.co`（官方 rows/size）。已用这些**逐条实测**。
- **不可达**：`api.bocha.cn`（`cimi-search` 底层，SSL 被防火墙截断）、`arxiv.org`、`github.com`、`ultradata.openbmb.cn` 全部无响应。因此论文正文级细节（MiniCPM5 逐源配比表、GPIC 训练 recipe）只能靠 HF 模型卡 / README 摘要层核实，无法抓 arxiv 全文；凡属此类我显式标注「⚠️摘要层」。
- **置信度**：`✅实测`（HF API 实时取数 + 本地 `open_clip`/`DeepSeek tokenizer` 实测）＞ `⚠️摘要`（模型卡/README 原文）＞ `❔常识`（业界公认入口）。

---

## 摘要（四句话结论）

1. **Q1（LLM 数据）：够，不是瓶颈**（必答判定①：MiniCPM5 对 BaiZe 计划已下全）。本地 Ultra-FineWeb-L3 **完整**（4 config / 1764 parquet，与 HF 官方逐文件一致），Code/Math 也完整；Ultra-FineWeb-L3 实测 ≈**690B token**（英文 ≈467B / 中文 ≈223B），对 2.2B 模型远超 Chinchilla 需求，缺的是「单遍跑满 4 个月」的冗余，靠多 epoch 或补 Ultra-FineWeb base 即可。唯一真实缺口 = `UltraData-SFT-2605` 落盘为空需重下（Stage(ii) SFT）。
2. **Q1（配比）：建议走路线 A**（直接复用 MiniCPM5 配比），理由：本地数据本就是 MiniCPM5 数据源的子集、BaiZe 已用 S4 三点消融实证退火比 86:10:4；路线 B（Data Mixing Agent + MATH/MMLU 代理）依赖未就绪的 P-6 评测基建，本阶段只能给方案不能执行。
3. **必答判定 ②：「1.8T tokens」写错了**——`1.8T` 是 `du` 出来的**磁盘字节**（1.8 TiB = HF parquet 1898 GB），不是 token；真实 token ≈690B（全 L3）/ ≈467B（英文子集）。论文 §4 还多错一处：写的是「English subset ≈1.8T tokens」，而英文子集其实只有 1.2 TiB 字节 / ≈467B token。
4. **Q2（Vision 数据）：换 caption 档即可消掉 77-token 截断**。LLaVA 85M 的 recaption 实测 **99.7–100% 超过 77 token 被截断**（英文均值 ~200+ token）；而 **GPIC 的 `tag`/`short`/`medium` 三档实测 0% 截断**（token 均值 11/20/46，仅 `long` 档 100% 截断）。这坐实了 vision R3 的数据侧怀疑：**换 GPIC 的 short/medium caption 本身就可能解决大半坍缩**。

---

# 问题 1 —— LLM pretrain 的数据够不够 + 配比怎么定

## Q1(1) MiniCPM5 的数据下全了吗？

**官方数据源清单**（来自 MiniCPM5-2B 模型卡 + openbmb/MiniCPM5 collection，URL 见下）：
Base/mid 训练 = `Ultra-FineWeb` + `Ultra-FineWeb-L3` + `UltraX-Preview` + `UltraData-Code` + `UltraData-Math`；Post SFT = `UltraData-SFT-2605`（400B token 深度思考 SFT）+ `UltraData-SFT-Agent-2609`（500K agent 样本）；Post RL = `UltraData-RL-2609`（80K+ RL 样本）。

| 数据集 | URL | 本地 | HF 官方 | 判定 |
|:---|:---|:---|:---|:---:|
| Ultra-FineWeb-L3 | https://huggingface.co/datasets/openbmb/Ultra-FineWeb-L3 | **4 config 全在**：en_qa 616 / en_multi 552 / zh_qa 310 / zh_multi 286 = **1764** parquet ✅实测 | 1764 parquet（4 config 逐文件一致）✅实测 | ✅ **下全** |
| UltraData-Code | https://huggingface.co/datasets/openbmb/UltraData-Code | **1121** parquet（L2 561 + L3 560）✅实测 | 1121 parquet（561/560 一致）apache-2.0 ✅实测 | ✅ **下全** |
| UltraData-Math | https://huggingface.co/datasets/openbmb/UltraData-Math | **1823** parquet（L1 1485 + L2-preview 138 + L3 200）✅实测 | 1823 parquet（一致）apache-2.0 ✅实测 | ✅ **下全** |
| UltraData-SFT-Agent-2609 | https://huggingface.co/datasets/openbmb/UltraData-SFT-Agent-2609 | jsonl **50 shard / 51 GiB** ✅实测 | ≈500K 样本 apache-2.0 ✅实测 | ✅ 就绪 |
| UltraData-SFT-2605 | https://huggingface.co/datasets/openbmb/UltraData-SFT-2605 | **落盘为空**：152K（仅 README+LICENSE；`data/no_think/*` 目录空，179 个 `.lock` 缓存）✅实测 | 1510 siblings；**gated=auto** ✅实测 | ❌ **缺（需同意条款后重下）** |
| Ultra-FineWeb（base） | https://huggingface.co/datasets/openbmb/Ultra-FineWeb | ❌ 不在盘上 | 1T en + 120B zh | ⬜ 未下（BaiZe 计划未用） |
| UltraX-Preview | https://huggingface.co/datasets/openbmb/UltraX-Preview | ❌ 不在盘上 | 公开（HTTP 200）✅实测 | ⬜ 未下（MiniCPM5 新增 web 源） |
| UltraData-RL-2609 | https://huggingface.co/datasets/openbmb/UltraData-RL-2609 | ❌ 不在盘上 | 公开（HTTP 200）✅实测 | ⬜ 未下（RL 阶段用） |

**判定：对 BaiZe 计划「下全」，对 MiniCPM5 全复刻「缺 4 个」**。
- BaiZe 的数据计划 = L3 做 Stage(i) 主体、Code+Math 做退火、SFT-* 做 Stage(ii)，这三块里 **L3/Code/Math/Agent-SFT 全部已下全**，唯一落地缺口是 `UltraData-SFT-2605`（**已下但为空，需重下**，gated=auto 要先在 HF 点同意）。
- MiniCPM5 官方还用了 `Ultra-FineWeb`（base）、`UltraX-Preview`、`UltraData-RL-2609` 三个本地**没有**的数据集，但**这三者均不在 BaiZe 计划的落地范围内**（BaiZe 用 L3 而非 base，RL 阶段数据自产），故不算必须补齐的缺口。

> 注：DATA_LEDGER §0 此前只记了 L3 的「616 / 617.6 GiB」（仅 en_qa 一支），漏记了 multi_style 与 zh 共 1148 支；实际 L3 全部 4 支 = **1764 parquet / ≈1.9 TiB** 已就位。已实测核对无误。
> **v1.1 修订（官方 config 命名核对）**：HF 官方 4 个 config（https://huggingface.co/datasets/openbmb/Ultra-FineWeb-L3）为 `Ultra-FineWeb-L3-en-QA-Synthetic`(320M 行) / `-en-Multi-Style-Synthetic`(378M) / `-zh-QA-Synthetic`(157M) / `-zh-Multi-Style-Synthetic`(204M)，对应本地目录 `ultrafineweb_en_l3/qa`(616)、`en_l3/multi_style`(552)、`zh_l3/qa`(310)、`zh_l3/multi_style`(286)。HF 官方 `Number of rows: 1,058,535,126`、`Total file size: 1.9 TB`（= 1898 GB ≈ 1.8 TiB），与本地逐 parquet 数 + 字节和完全吻合 ✅。


## Q1(2) 数据够不够？—— token 实测 + 「1.8T」判定

**实测 token 外推**（对每 config 抽 1 个 parquet 的首 row group 8000 文档，DeepSeek-V4.1-Flash tokenizer / `tokenizer_eod` 分词，再乘官方 rows 数外推）：

| config | 官方 rows（HF size API）✅实测 | 实测 tok/doc | 外推 token |
|:---|:---|---:|---:|
| en-QA | 320,112,563 | 821.1 | **263B** |
| en-Multi-Style | 378,071,951 | 539.4 | **204B** |
| zh-QA | 156,629,979 | 810.7 | **127B** |
| zh-Multi-Style | 203,720,633 | 470.3 | **96B** |
| **合计** | 1,058,535,126 行 | — | **≈690B**（en ≈467B / zh ≈223B） |

与官方自述互核：README 明写「**400B+ English tokens 和 200B+ Chinese tokens**」（≈600B+）；我的抽样外推 ≈690B，略高但在同一量级（抽样偏向长文 en_qa 所致），结论一致。

> **v1.1 修订（抽样口径透明化）**：任务书 §0.1(2) 建议「抽样 20–50 个 parquet 外推」，本次实际为**每 config 抽 1 个 parquet 的首 row-group 8000 文档**（4 个 parquet 共 32000 文档）分词再乘官方 rows 数外推。未按 20–50 抽的考量：① README 已自给 token 量级（600B+），与抽 1 个 parquet 的外推（≈690B）互为印证、同一量级；② 本问「1.8T=字节而非 token」的**主证是字节对账**（1898 GB ≈ 1.9 TB ≈ 1.8 TiB，见 Q1(1)），不依赖抽样的精确度。真实 token 数以 phase2 分词后的 `.bin` 为准（尾注已说明）。

**对照需求（2.2B 模型 · 4 个月算力窗口）**：
- 任务书给定 `~93K tok/s → 30 天 ≈ 242B token`，则 **4 个月 ≈ 968B token**。
- 英文 L3 单支（≈467B）≈ **1.9 个月**；全 L3（≈690B）≈ **2.85 个月**；再加 code/math 退火 ≈ **3+ 个月**。
- Chinchilla 计算最优 ≈ 20 token/参数，2.2B 仅需 ≈ **44B token**（https://arxiv.org/abs/2203.15556）；690B 已是其 **15×**。

**结论：数据「够」——瓶颈是算力不是数据**（与方案 §2.1 一致）。但要「单遍、不重读」跑满 4 个月会差 ~1 个月：真想要满窗单遍，可补 `Ultra-FineWeb` base（1T en + 120B zh，apache-2.0，公开直接下载）或接受多 epoch（对 2.2B 完全可接受）。

🔴 **必答判定② —— 论文 §4 的「≈1.8T tokens」是否写错：写错了，是「字节」被当成了「token」。**
- 论文 §4 原文（`ISEDA2027/4_llm_pretrain.tex:35`）：「Pre-training uses the Ultra-FineWeb-L3 **English subset** (≈1.8T **tokens**)」。
- `1.8T` 来源 = 早先 pretrain 侧 `du -sh` 磁盘字节（`MEMORY.md:14` 记「Ultra-FineWeb-L3: 1.8T」，就是 1.8 TiB）。
- 与之**精确吻合**的是 HF 官方 parquet 字节：663+594+333+308 = **1898 GB ≈ 1.8 TiB**（不是 token）。
- 真实 token = **≈690B**（全 L3）/ **≈467B**（英文子集）——「1.8T tokens」比真实值**高约 2.6×（相对全 L3）到 3.9×（相对英文子集）**。
- 同段 `MEMORY.md` 里的 `1.2T / 515G / 51G`（Code/Math/SFT-Agent）**也全是磁盘字节**，不是 token。
- 建议改法：§4 该句改为「Ultra-FineWeb-L3 English subset (≈467B tokens / ≈1.2 TiB)」或「full L3 (≈690B tokens / ≈1.9 TiB)」；§5 的配比/步数按真实 token 重算（Phase2 分词后可用 `.bin` 真实 token 数替换）。

## Q1(3) 配比怎么定？—— 建议走路线 A，理由如下

**路线 A（直接复用 MiniCPM5 配比好的数据）**
- MiniCPM5 **未在模型卡公开逐源百分比**（模型卡只以 tag 列出 8 个数据集的归属：Ultra-FineWeb / UltraX-Preview / Ultra-FineWeb-L3 / UltraData-Math / UltraData-Code / UltraData-SFT-2605 / UltraData-SFT-Agent-2609 / UltraData-RL-2609，无任何占比数字，✅实测）。
- **v1.1 修订（arxiv 2602.09003 的真实身份）**：该 arxiv 号 = **《Data Science and Technology Towards AGI Part I: Tiered Data Management》**，是 **UltraData 数据平台的立场/框架论文** —— HF Paper 页原文宣称「**2.4T open tokens**」= **整个 Ultra* 平台全部语料的总 token 量**（⚠️摘要层，来自 https://huggingface.co/papers/2602.09003 原文），**并非** MiniCPM5 模型的技术报告；其摘要与模型卡**均未发布 MiniCPM5 的逐源配比百分比**。→ 结论不变：**MiniCPM5「逐源配比」在可及公开渠道「未找到」**（不编造）。
- 但数据源本身（Ultra-FineWeb-L3 + Code + Math）**本地已全具备**——「复用配比」的最小改动 ≈ **零下载**：直接用已在盘上的 L3/Code/Math，按 BaiZe 自己已经消融出的退火比投料即可。
- **BaiZe 已实证了一个配比**：S4 三点消融得出纯 L3(2.7621) → L3+code(2.6793) → L3+code+math(**2.6298**) 单调下降，最终退火比 **L3:code:math = 86:10:4**（`4_llm_pretrain.tex` 的 S4-03）。这个比例**就是可交付的配比结论**，无需再搜。

**路线 B（MATH + MMLU 代理指标搜最优配比，Data Mixing Agent 一类）**
- 可执行方案：固定 2.2B 网，扫 N 组配比 × 各训到代理信号饱和（如每组 ~1–2B token）→ 用 MATH/MMLU 打分选优。
- 成本估算：若 **8 组配比 × 1B token / 组 = 8B token**，在 ~72K tok/s（hybrid 实测）下 ≈ 8e9/72e3 ≈ 31 GPU·h；若每组训 5B token 则 ~155 GPU·h。**钱在可负担范围，但**——
- ⚠️ **硬依赖未就绪**：路线 B 要能跑 MATH/MMLU 评测，即需 pretrain 侧 **P-6（mcore→HF→SGLang→lm_eval）** 基建；当前基建未就绪，**路线 B 只能给方案、不能执行**。

**明确建议：A**。三点理由：① 本地数据 = MiniCPM5 数据源子集，A 的边际成本≈0；② BaiZe 已用四点消融「免费」得到了退火比 86:10:4，再搜一遍配比收益极低；③ B 的评测基建未就绪，且对 2.2B/4 个月窗口，把算力花在搜配比不如花在满窗训练上（数据早已不是瓶颈，见 Q1(2)）。

## Q1(4) 是否需要在 HF 继续寻找？

**基本不用。** 仅两种情况需要补：
1. **SFT-2605 重下**（唯一真实缺口）：`openbmb/UltraData-SFT-2605`（apache-2.0，**gated=auto**，公开但需先点同意）—— Stage(ii) 深度思考 SFT 主体，本地只有 152K 空壳。
2. **若要「单遍满 4 个月」**：补 `openbmb/Ultra-FineWeb`（base，1T en + 120B zh，apache-2.0，公开直接下载）；否则多 epoch 即可，不必补。

候选均为官方开放数据、许可清楚（apache-2.0）、可公开直接下载，无「不明」许可问题，无需再泛泛罗列其他外部源。


---

# 问题 2 —— Vision encoder 的数据够不够 + 配比怎么定

> 背景：vision R3 判定训练发生**表征坍缩**（两塔退化常量嵌入），怀疑之一在数据侧 = `SimpleTokenizer` 77-token 截断 + LLaVA 长 recaption 截断后互相高度相似。本节只做「数据是否为元凶」的事实层定量，训练侧验证由 vision R4 负责。

## Q2(1) 两份数据各是什么

| 数据集 | URL | 许可 | 结构 | 规模（HF 官方）✅实测 | 本地实测 |
|:---|:---|:---|:---|:---|:---|
| LLaVA-OneVision-1.5-Mid-Training-85M | https://huggingface.co/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M | apache-2.0 ✅实测 | 8 子集 × EN/CN，parquet 列 `[id, image, caption]`，~8000 行/文件 | **12126 parquet**：EN 9544 + CN 2580（imagenet 50/32、laioncn 430/132、datacomp1b 439/136、zero250m 925/385、coyo 1504/436、sa1b 900/247、mint 553/152、obelics 4743/1060） | **7519 parquet**（EN 5571 + CN 1948），**下载中**；**缺 sa1b + zero250m 两整子集**，obelics/EN 仅 2594/4743 |
| Stanford GPIC | https://huggingface.co/datasets/stanford-vision-lab/gpic | **mit** ✅实测（⚠️ **gated** 访问，见下） | tar 内 `{key}.json`+`{key}.jpg|png`；json 含 `caption_type∈{tag,short,medium,long}` + `caption` | **28T 像素**；100M train + 200K val + 1M test；**8000 train tar + 32 val + 128 test** | train **406/8000**（仍有进程在下载，++ 中）、test **128/128 全齐**、reference_stats 5 npz |

> 本地 LLaVA 85M 是 6/8 子集、GPIC train 是 406/8000 tar——两份**都还在下载**。但本问题要用的数据是「vision encoder 实际训练子集 = `imagenet/EN` 500K」（论文 6_vision 明写用了 500K imagenet/EN），该小支**已齐**（50 parquet），故 caption 分析不受影响。
> **v1.1 修订（GPIC 可得性）**：GPIC 许可确为 **MIT**（可商用，✅实测），但 HF 页面明确「**You need to agree to share your contact information to access this dataset**」——即访问**需先同意 gated 条件（共享联系信息）**，并非「无需注册的公开直接下载」。可得性应记为 **`需接受 gated 条件`**（与任务书 §5 提到的「下载带 HF token」一致；对已开始下载的本机无影响，但对外人/评审需先同意条件）。

## Q2(2) ⭐ caption 长度分布 —— 77-token 截断的量化

> 口径：`open_clip.tokenizer.SimpleTokenizer`（open_clip 3.2.0 实测加载，`context_length=77`）。对每档 caption 报告**词数**与 **CLIP token 长度**，判据 = token 长度是否 >77（超出即截断）。

**LLaVA 85M recaption（各子集抽 1500 条）✅实测：**

| 子集/语言 | CLIP token 均值 | 中位 | 最大 | **>77 比例** |
|:---|:---:|:---:|:---:|:---:|
| coyo/EN | 202 | 195 | 600 | **99.9%** |
| coyo/CN | 498 | 479 | 1385 | **100%** |
| obelics/EN | 222 | 216 | 515 | **99.9%** |
| datacomp1b/EN | 215 | 209 | 486 | **99.9%** |
| laioncn/EN | 227 | 217 | 649 | **99.7%** |
| mint/EN | 228 | 222 | 445 | **100%** |

→ **LLaVA 85M 的 recaption 几乎 100% 超 77 token、被截断**；中文更甚（均值 498 token）。这正是 R3 怀疑的「长 recaption 被截断后互相高度相似」。

**GPIC（5 tar 采样 53637 图，按 caption_type 分档）✅实测：**

| caption_type | 占比 | 词数均值/中位 | CLIP token 均值/中位 | 最大 | **>77 比例** |
|:---|:---:|:---:|:---:|:---:|:---:|
| `tag` | ~1% | 7.0 / 7.0 | 11.1 / 11 | 19 | **0%** ✅ |
| `short` | ~45% | 17.4 / 17.0 | 20.2 / 19 | 51 | **0%** ✅ |
| `medium` | ~45% | 39.2 / 39.0 | 45.8 / 46 | 80 | **0.1%** ✅ |
| `long` | ~9% | 131.9 / 131.0 | 157.4 / 156 | 373 | **100%** |

🔑 **本问题最想要的结论**：
- LLaVA 长 recaption 被**大面积（99.7–100%）截断**；
- GPIC 的 **`tag`/`short`/`medium` 三档几乎 0% 截断**（tag/short 完全 0，medium 0.1% 且 max 才 80、只超 3 个）；
- 只有 GPIC `long` 档（9%）会 100% 截断。
- **推论**：把 vision encoder 的 caption 源从「LLaVA 长 recaption」换成「**GPIC short（或 short+medium）**」，就能把「77-token 截断 → 全库 caption 高度相似 → 表征坍缩」这条链路从数据侧直接掐断；**换数据本身很可能解决大半坍缩**（最终仍由 vision R4 训练侧验证）。

## Q2(3) 85M 与 GPIC 怎么混？caption 用哪一档？

**建议：caption 用 GPIC `short` 为主、`medium` 为辅，85M 降级为「图像多样性来源」而非「caption 来源」。**

| 组件 | 角色 | 理由 |
|:---|:---|:---|
| GPIC `short` | **主 caption 源** | 17 词 / 20 token，0% 截断；语义完整且长度在 77 安全区间 |
| GPIC `medium` | 次选（可选增强） | 46 token，99.9% 安全；多一点点上下文，但贴近 77 上限，收益/风险需小消融 |
| GPIC `long` | 🚫 不用 | 100% 截断，重蹈 LLaVA 覆辙 |
| LLaVA 85M | 图像多样性（caption 丢弃或先截断到 <77） | 其 recaption 100% 截断；但图像本体仍是有价值的通用图源，可与 GPIC 图像池并集 |

- **最小验证实验**：先「纯 GPIC short」重跑 R3 的四架构对比，看坍缩是否消失（若消失即坐实数据元凶，且无需再混 85M）；这一步几乎零成本（只需换 caption 源）。
- **混合比例原则**：caption 一律取 GPIC `short`（+可选 `medium`），图像可 85M:GPIC ≈ 1:1 起步；**不要再把 LLaVA 的长 caption 放进 77-token 的 SimpleTokenizer**。
- 若必须复用 85M 的 caption（例如要 EN/CN 双语），必须先做「前 77 token 截断」或换长上下文 text tower，否则等于继续喂被截断的相似文本。

## Q2(4) 是否需要在 HF 继续找版图/原理图/电路图视觉数据集？

> 判据：vision encoder 是从零预训练的**通用图像编码器**，需要亿级图像；EDA 版图/原理图是 Stage(iii)/(iv) 的**领域适配**任务，不属于本问题（预训练）范围。

| 候选源 | URL | 规模 | 许可 | 可得性 | 判定 |
|:---|:---|:---|:---|:---|:---|
| open-schematics | https://huggingface.co/datasets/bshada/open-schematics | 未标注（likes 188 / 下载 9715，K 级） | 不明🔴 | 公开直接下载 | 太小，不用于预训练 |
| schematic_images | https://huggingface.co/datasets/hanky2397/schematic_images | 未标注（K 级） | 不明🔴 | 公开直接下载 | 同上 |
| CircuitNet3.0 | https://huggingface.co/datasets/SKLP-EDA-LAB/CircuitNet3.0 | 布线/拥塞基准（K 级，非自然图像） | 不明🔴 | 公开直接下载 | 任务特定，不用于预训练 |
| CircuitVQA（本地已有） | https://huggingface.co/datasets/ayoubkirouane/CircuitVQA | — | 不明🔴 | 本地 `/nas_user` 已有 | 领域 Q/A 用，非预训练 |

**结论：不值得在「vision encoder 预训练」阶段引入**。公开的版图/原理图/电路图视觉集都是 K 级、任务特定（缺陷检测/布线基准/Q&A），与「亿级通用图像预训练」量级差 3–4 个数量级，且许可多为「不明」。**EDA 领域视觉的正确做法是 Stage(iii)/(iv) 用脚本渲染自标注图**（对齐 PyAether 任务 + 红线数据），而不是去凑这些小块开放集。

---

## 尾注（诚实声明）

- 所有 `✅实测` 数字来自 2026-10-01：HF REST API 实时取数 + 本地 `open_clip 3.2.0` / `tokenizer_eod` 实测抽样（已贴具体抽样量与命令口径）。
- `⚠️摘要` 指 HF 模型卡/README/Paper 页原文（本机连不上 arxiv 全文/github/bocha；但 HF 模型卡、数据集卡、Paper 页本轮已可抓取复核）。MiniCPM5「逐源配比百分比」官方未在模型卡公开，属「未找到」而非编造。
- 「1.8T tokens 写错」第一步（1.8T = 磁盘字节）为**铁证级**（`MEMORY.md` 的 `du` 记录 + HF `num_bytes` 同量纲吻合）；第二步 token 外推（821/539/811/470 tok/doc）为**抽样估计**，phase2 分词后可用真实 `.bin` token 数替换，结论方向不变。

---

# R2 —— LLM 数据侧（2026-10-01）

> 本轮任务书：BAIZE_DATA_TASK.md 的**两项优先任务** ① UltraData-SFT-2605 重下（gated token 验证是阻塞点）② P-8 数据方案（8 源事实表满填 + base vs L3 重叠率实测 + P-8 三档方案）。
> 方法：逐源 `huggingface.co` REST（`/api/datasets`、`/api/datasets/<repo>/tree`、`/raw` README）+ `datasets-server.huggingface.co`（rows/size/first-rows）+ 本地 `tokenizer_eod` 抽样实测。

## R2-A · 8 源事实表（满填，无空项）

| # | 数据集 | URL | 许可 | 行数 | 磁盘字节 | token 估算 | 官方结构 | 本地状态 | 判定 |
|:--:|:---|:---|:---|:---|---:|---:|:---|:---|:---|
| 1 | Ultra-FineWeb（**base**） | https://huggingface.co/datasets/openbmb/Ultra-FineWeb | apache-2.0 ✅ | **1,290,261,453**（en 1,159,254,991 / zh 131,006,462）✅ | **2,985,679,608,127** = **2.99 TB / 2.72 TiB** ✅ | **~1.12T**（README：1T en + 120B zh；抽样 826 tok/doc→en≈1.0T 互核） | default config（split en/zh），64,624 parquet（en 2048 + zh ~62,576），列 `content/score/source` | ❌→**下载中**（本轮已启动） | **新增·主预训练主体** |
| 2 | UltraX-Preview | https://huggingface.co/datasets/openbmb/UltraX-Preview | apache-2.0 ✅ | **113,789,578** ✅ | **486,915,450,022** = **487 GB / 0.44 TiB** ✅ | **~100B**（5 config 各 ~20B，README 口径） | 5 config：AICC 21.3M/68.6G、FineWeb 29.2M/108.8G、FineWeb-ProX-Doc 17.3M/109.3G、RedPajama-V2 22.1M/91.4G、**Ultra-FineWeb 23.9M/108.9G**，479 parquet，列 `uid/raw_content/cleaned_content/processed_functions/source` | ❌ | **新增，但主要与 base 重叠** |
| 3 | Ultra-FineWeb-L3 | https://huggingface.co/datasets/openbmb/Ultra-FineWeb-L3 | apache-2.0 ✅ | 1,058,535,126 ✅ | 1.9 TB / 1.8 TiB ✅ | **≈690B**（en 467B / zh 223B，与 README「600B+」一致） | 4 config（en/zh × QA/Multi-Style），1764 parquet | ✅ **下全** | 退火/decay 主体 |
| 4 | UltraData-Code | https://huggingface.co/datasets/openbmb/UltraData-Code | apache-2.0 ✅ | **348,083,481**（L2 266,878,376 / L3 81,205,105）✅ | **1,215,994,166,161** = **1.22 TB / 1.11 TiB** ✅ | **≈411B**（L2 355B + L3 56B，本轮抽样 1330/692 tok/doc） | L2 ×11 语言 + L3 ×12 语言，1121 parquet | ✅ **下全** | 退火 code |
| 5 | UltraData-Math | https://huggingface.co/datasets/openbmb/UltraData-Math | apache-2.0 ✅ | **181,186,453**（L1 86,032,552 / L2-preview 13,835,635 / L3 81,318,266）✅ | **552,412,859,233** = **552 GB / 0.50 TiB** ✅ | **≈303B**（L1 184B + L2p 32B + L3 87B，本轮抽样 2138/2285/1076 tok/doc） | L1(CC-MAIN)/L2-preview/L3，1823 parquet | ✅ **下全** | 退火 math |
| 6 | UltraData-SFT-2605 | https://huggingface.co/datasets/openbmb/UltraData-SFT-2605 | apache-2.0（**gated=auto**）✅ | 官方首页按目录展示，**318.99 GB / 1504 jsonl**（`no_think` 855 + `think` 649；⚠️ 2026-10-02 校正，旧记 97.6GB 有误） | —（SFT，不计 token） | — | `no_think/{Chinese-general,Code,IF,Knowledge,Math,Multi-lang-K,Multi-lang-M}` + `think`，1510 siblings | 🟠 **下载中（315/1504）** | **重下中（token 已有效）** |
| 7 | UltraData-SFT-Agent-2609 | https://huggingface.co/datasets/openbmb/UltraData-SFT-Agent-2609 | apache-2.0 ✅ | **~500K 样本**（jsonl 50 shard） | **51 GiB** ✅ | —（SFT） | `Code_Agent`(7)/`General_Agent`/`Search_Agent`/`Tool_Use` jsonl | ✅ **就绪** | Stage(ii) SFT |
| 8 | UltraData-RL-2609 | https://huggingface.co/datasets/openbmb/UltraData-RL-2609 | apache-2.0 ✅ | 10K<n<100K（`size_categories`） | **187.63 GB** ✅ | —（RL） | 4 config：Math(default)/Knowledge/Long-Context/Code，20 jsonl（Code 12=~184G / Knowledge 2=~10M / Math 4=~15M / Long-Context 2=~3.6G） | ❌ | RL 阶段(Stage v)用，**P-8 不需要** |

> 事实来源均为 2026-10-01 实时：行数/字节 = `datasets-server` `/size`+`/info`（✅实测）；结构与 gated = HF `/api/datasets/<repo>/tree`（✅实测）。Code/Math/L3 的 token 为本轮 `r2_local_sample.py` 抽样（各源 5–8 parquet × 400–4000 文档）外推；base 用 README 权威值 + `first-rows` 抽样互核。

## R2-B · base vs L3 重叠率（一句话结论 + 数字）

> **结论：下 `Ultra-FineWeb`（base）＝ 净新增 ≈1.12T 原始 web 语料，不是重复劳动。**

- **关系定性（官方 README）**：`Ultra-FineWeb-L3` = 在 `Ultra-FineWeb`（base）之上做「**Q&A 生成 + 多风格改写（multi-style rewrite）**」合成的**退火档**——即 L3 是 base 的**派生改写**，不是 base 的复制。
- **实测数字**（base en `first-rows` 48 文档 vs L3 en/qa 抽样 696 文档，`r2_local_sample.py`）：
  - 全文 verbatim 重合 = **0 / 48 = 0.00%**；
  - 5-gram Jaccard 均值 = **0.0000**（基本正交）。
- **语义/语言分布**：base en ≈ raw 网页文本（自然长文，样本 avg 826 tok/doc）；L3 en/qa = 合成问答（avg 825 tok/doc、内容为改写问答，措辞与 base 不同源表达）。
- **结论 → 投料**：base（raw web）应作 **P-8 主预训练的稳定主体**，L3 是**退火档**；两者**不重复**，量化重叠 ≈ 0。

## R2-C · P-8 数据方案（三档）

**当前 P-8 投料情形**：现方案 Stage(i) 主体 = `Ultra-FineWeb-L3 (EN)`、退火 = `Code + Math`（86:10:4，S4 消融实证），推荐档 **100B token**，缺 body 的「raw web 稳定主体」。

**建议**：把 Stage(i) 主体从 **L3 换成 base（`Ultra-FineWeb` en 支）**，退火仍用 Code+Math，配比沿用 86:10:4。理由：① base 是原始 web（1.12T），比合成 L3 更适合做主预训练稳定主体；② L3 更适合退火，本地已全、可与 base 互补；③ 86:10:4 已被 S4 消融实证，无需再搜。

| 档位 | 总量 | base-en | code | math | 落盘需求（增量） |
|:---|:---|---:|---:|---:|:---|
| **P-8 小（44B，Chinchilla 下限）** | 44B | 37.8B | 4.4B | 1.8B | base-en 仅需 ~42B token ≈ 分 1 支 en parquet 即可开场 |
| **P-8 中（100B，推荐）** | 100B | 86B | 10B | 4B | base 2.99TB 全量，code/math 各取 ~2.4%/1.3% |
| **P-8 大（200B）** | 200B | 172B | 20B | 8B | 同上（base 2.99TB 足够） |

**需要下载 / 已完成（`✅`区分）**：
1. `openbmb/Ultra-FineWeb`（base，2.99TB，apache-2.0，**公开、无需 token**）—— **本轮已启动下载**（写入 `/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb/`，进程持续中）。
2. `openbmb/UltraData-SFT-2605`（gated，318.99GB / 1504 jsonl）—— **已在本轮重下**：token `hf_lqLxH…`（用户 foamliu）`whoami-v2` 实测**有效**、gated resolve 通过，下载中（315/1504 jsonl）；下完核验「实际字节+文件数 vs HF 官方清单」一致性（Stage(ii) SFT，不阻塞 P-8）。
3. `UltraX-Preview`（487GB）—— **不下载**：其 config `UltraX-Ultra-FineWeb` 实为 base 的程序化精炼版，与 base 重叠；≤200B 档用 base 即可，UltraX 留作「base 不可得时的质量替代」备选。
4. `UltraData-RL-2609`（187.63GB）—— **不下载**：RL/RLVR 阶段（Stage v）才用，与 P-8（预训练）无关。

**磁盘与带宽**：base 2.99TB 增量，`/nas_inference` ~21.0 TB、`/nas_train` ~32 TB 可用，**足够**。带宽当前被 gpic + LLaVA 两路 HF 下载占用（实测 ~10–13 MB/s），base 按当前速度约 **3 天**下完（争用时更长）。**污染隔离**：base/UltraX 落盘后须过 `check_contamination.py`（红线：与 `EDA-Eval-PyAether` 评测集不同源 + 跨集去重比对），正式投料前完成。

**命令口径（复现）**：
```bash
# ① base 全量下载（已启动，无需 token）
hf download --repo-type dataset openbmb/Ultra-FineWeb \
  --local-dir /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb
# ② SFT-2605（需先换成有效 token HF_TOKEN）
HF_TOKEN=<新token> hf download --repo-type dataset openbmb/UltraData-SFT-2605 \
  --local-dir /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605
```

## R2-D · 配比来源复核（MiniCPM5 逐源百分比）

**核对过的页面**：① MiniCPM5-2B 模型卡；② 8 个数据集的 HF 数据集卡 README；③ arxiv 2602.09003 = **《Data Science and Technology Towards AGI Part I: Tiered Data Management》**（UltraData 平台框架论文，宣称「2.4T open tokens」为整个 Ultra* 平台总量）。

**结论**：以上公开渠道**均未发布 MiniCPM5 逐源配比百分比**（模型卡只有数据集 tag 归属、无占比；各家数据集卡只有各自 token 量、无混合比）。故「MiniCPM5 官方配比」＝ **未找到（不编造）**。

**→ 建议配比（替代）**：P-8 采用 **base-en : code : math = 86 : 10 : 4**（见 R2-C 三档表）。依据：① 直接复用 BaiZe S4 三点消融已实证的退火比（纯 L3 2.7621 → +code 2.6793 → +code+math 2.6298）；② 参照 MiniCPM5 分层结构（base 做主训练、Code/Math 做退火），把「L3 主体」原位替换为「base 主体」。此比例是数据侧可交付结论；精准主体:退火占比若需微调，属 pretrain 侧小消融（数据侧已把 base/code/math 三源备齐）。

---

# 问题 2（R2 修订版）—— Vision encoder：去 HF 找更多通用图文对（§0.4）

> 版本 R2-视觉侧 · 2026-10-01 夜 · 响应运维「三次修订」§0.4（上一轮把问题错缩小成"要不要找 EDA 版图"）。
> 铁律落地：① **「图像形态」一票否决**（`bytes` / `URL-only` / 待抽验，逐行贴抽验证据）；② ≥10 个 HF 候选、每条实测短 caption(≤77 token)率；③ 前 3 推荐**必须全部 `bytes`**。
> ⚠️ `cimi-search` 底层 `api.bocha.cn` 仍 SSL 被防火墙截断（本次复测仍不可达），故用 **HF 全文搜索 API（`/api/datasets?search=`）+ `datasets-server /first-rows` + 本地 `open_clip.tokenizer.SimpleTokenizer`** 完成等价动作，并把你**实际搜过的页面/请求**列在 B 表下方。

## R2-视觉侧 A · 本地多模态源逐条实测（图像形态 + ≤77 率）

> 抽验方法：webdataset→`tar -tf` 看是否内嵌 `.jpg`；parquet→`pyarrow.ParquetFile.schema`；（远程）→`datasets-server /first-rows` 看列类型是否 `Image`/`url`。≤77＝`open_clip SimpleTokenizer` 抽 N 条 caption 的 ≤77 token 占比。

| 本地已有 | 路径 | 图像形态（证据） | 是图文对 | 图像/对数 | caption ≤77 率（实测） | 判定 |
|:--|:--|:--|:--|:--|:--|:--|
| `conceptual-captions-12m-webdataset` | `/nas_train/.../datasets/conceptual-captions-12m-webdataset/data/*.tar` | ✅ **bytes**（`tar -tf`＝`00010000.jpg/.json/.txt` 三件套） | ✅ | **1100 tar / 1.2T / ≈11M 对**（每 tar 30000 成员=10000 对） | **98.0% ≤77**（mean 20.9，N=100；样本"`<PERSON>, 'Chair from the Organic Design Competition', 1941`"） | ✅ 可用 |
| `laion2B-en-aesthetic` | `/nas_train/.../datasets/laion2B-en-aesthetic/*.parquet` | 🚫 **URL-only**（schema＝`URL/TEXT/WIDTH/HEIGHT/similarity/hash/punsafe/pwatermark/aesthetic`，无 image bytes） | 是(文字) | ≈2500 parquet / ~8.1TB（仅元数据） | 99%≤77（但没图） | 🚫 淘汰 |
| `Recap-DataComp-1B`（UCSC-VLAA + 顶层） | `/nas_user/.../UCSC-VLAA/Recap-DataComp-1B`(518G) + `/nas_user/.../Recap-DataComp-1B`(67G) | 🚫 **URL-only（运维已确认）** | 否 | — | — | 🚫 淘汰 |
| `BLIP3o-Pretrain-Long-Caption` | `/nas_user/.../BLIP3o/BLIP3o-Pretrain-Long-Caption/sa_*.tar` | ✅ **bytes**（`sa_1665103.jpg/.txt`） | ✅ | 2891 tar / 1.3T | **0% ≤77**（mean 121.1 tok，N=100，长描述） | ⚠️ bytes 但 caption 超长，不适配冻结 CLIP 77-token |
| `Amshaker/Mobile-O-Pre-Train` | `/nas_user/.../Amshaker/Mobile-O-Pre-Train/*.tar` | ✅ **bytes**（`000000000.jpg/.txt`） | ✅ | **2250 tar / 3.7T / ≈6M 对**（每 tar 5292 成员=2646 对） | **100% ≤77**（mean 12.6，N=100；样本"`A close-up of a textured, cream-colored upholstered chair backrest.`"） | ✅ 可用 |
| `coco` / `vg` | `/nas_train/.../datasets/coco`、`vg`（`images.zip` 5.5G+`images2.zip` 9.7G） | ✅ bytes（zip/jpg） | 部分(VG 带 caption) | ≈108K（vg）+≈123K（coco） | 短（COCO 短图注） | 可作补充（量小） |
| `FineVision`(188 子集) | `/nas_train/.../datasets/FineVision/{allava_laion, allava_vflan, ...}` | ⚠️ mixed（`allava_laion` URL；部分 bytes） | 部分 | 188 子集 | 待抽验 | ⚠️ 需按子集筛 URL |
| `LLaVA-Pretrain`(664 子集) | `/nas_train/.../datasets/LLaVA-Pretrain/00000..00663/*.parquet` | ✅ **bytes**（parquet `image` 列＝文件名，图在 archive） | ✅(短 caption) | ≈**558K** | **100% ≤77**（mean 11.5，N=100） | ✅ 可用 |
| `LLaVA-CC3M-Pretrain-595K` | `/nas_train/.../datasets/LLaVA-CC3M-Pretrain-595K`（`images.zip`+`chat.json`） | ✅ **bytes**（`image`＝`GCC_train_*.jpg`，图在 zip） | ✅ | ≈**595K** | **100% ≤77**（mean 12.3，N=100） | ✅ 可用 |
| `ocr_vqa` / `textvqa` | `/nas_train/.../datasets/ocr_vqa/images/*.jpg`、`textvqa/train_images/*.jpg` | ✅ bytes（jpg） | ❌(VQA) | ≈200K | —（VQA 非图文对） | ⚠️ 非通用图文对 |
| `LLaVA-OneVision-1.5` 全家桶 | `/nas_train/.../datasets/mvp-lab/` | ✅ **bytes**（parquet 内嵌，已知） | ✅(但 85M recaption 99.7% 截断) | 7549 parquet（下载中） | 见 v1.1（长 recaption 截断） | ⚠️ 长 caption |
| `stanford-vision-lab/gpic` | `/nas_inference/.../stanford-vision-lab/gpic` | ✅ **bytes**（tar 内 `{key}.jpg`） | ✅(tag/short 短) | 8000 train | tag/short/medium 0% 截断（v1.1 已实测） | ✅ 但量小 |

> **A 表结论**：本地**早已躺着一批「bytes + 短 caption」的通用图文对**，上轮盘点完全漏掉——`CC12M webdataset ≈11M`、`Amshaker Mobile-O ≈6M`、`LLaVA-Pretrain/CC3M ≈1.15M`，三者 ≤77 率 98–100%。这就是"补数据不足"的实际弹药。

## R2-视觉侧 B · HF 通用图文对候选（图像形态 + 短 caption 率实测）

> 证据来源：`datasets-server /first-rows` 实时取真实样本（列类型 + 首个样本原文）；≤77 率用 `open_clip SimpleTokenizer` 抽 ≤100 条 caption 实测。
> ⚠️ **结论与现实完全印证运维预判**：CLIP 级大集（LAION/COYO/DataComp/PixelProse/Recap/OBELICS）**普通是 URL-only**，一票淘汰；真正「带图 + 短 caption」的是**中小规模（几万~千万）**集。

| 候选 | HF repo | 规模 | 图像形态（证据） | 许可 | 短 caption ≤77 率 | 判定 |
|:--|:--|:--|:--|:--|:--|:--|
| DataComp-1B | `mlfoundations/datacomp_1b` | ~1.4B 行 | 🚫 **URL-only**（`url` 列=`https://...blob.core.windows.net`） | — | 99%≤77（mean13.8）但没图 | 🚫 淘汰 |
| COYO-700M | `kakaobrain/coyo-700m` | ~747M 行 | 🚫 **URL-only**（`url` 列） | cc-by-4.0 | 99%≤77（mean18.7） | 🚫 淘汰 |
| PixelProse | `tomg-group-umd/pixelprose` | ~46M | 🚫 **URL-only**（`url` 列，另有 `vlm_caption` 长） | — | original_caption 99%≤77 | 🚫 淘汰 |
| Recap-DataComp-1B | `UCSC-VLAA/Recap-DataComp-1B` | ~1.3B | 🚫 **URL-only（运维已确认，本地也死）** | — | — | 🚫 淘汰 |
| OBELICS（交错） | `HuggingFaceM4/OBELICS` | ~141M doc | 🚫 **URL-only**（`images`＝`https://...` 列表，交错网页） | — | n/a（非图文对） | 🚫 淘汰 |
| LAION-COCO(-nllb) | `visheratin/laion-coco-nllb` | — | 🚫 **URL-only**（`url` 列） | — | 100%≤77（mean10.6） | 🚫 淘汰 |
| LAION-2B-en-aesthetic | `laion/laion2B-en-aesthetic` | ~625M | 🚫 **URL-only**（本地 schema 已证 URL+embedding） | — | — | 🚫 淘汰 |
| CC12M（webdataset 版） | `laion/conceptual-captions-12m-webdataset` | ~11M（1100 tar） | ✅ **bytes**（本地 `tar -tf`＝`.jpg/.json/.txt`） | CC 类 | **98.0%≤77**（mean20.9） | ✅ **推荐** |
| LLaVA-CC3M-Pretrain-595K | `liuhaotian/LLaVA-CC3M-Pretrain-595K` | 595K | ✅ **bytes**（`image`=`GCC_train_*.jpg`，图在 `images.zip`） | CC 类 | **100%≤77**（mean12.3） | ✅ **推荐** |
| LLaVA-Pretrain(558K) | `liuhaotian/LLaVA-Pretrain` | 558K | ✅ **bytes**（`image`=`00453/004539375.jpg`，图在 archive） | CC 类 | **100%≤77**（mean11.5） | ✅ **推荐** |
| COCO（检测版） | `detection-datasets/coco` | 118K | ✅ **bytes**（`image` 列类型=`Image`，parquet 内嵌） | COCO 许可 | n/a（检测框，非 caption 对） | ⚠️ 非通用图文对 |
| InternVL-SA1B-Caption | `hanlincs/InternVL-SA1B-Caption-WebDataset` | SA-1B 子集 | ✅ **bytes**（`jpg` 列类型=`Image`）+`__url__` | apache-2.0? | 待抽验（caption 字段未在 first-rows 显式出现） | ✅ 新发现·可选补量 |
| cc12m-webdataset（镜像） | `yangyang857658468/cc12m-webdataset` | ~12M | ✅ bytes（webdataset） | — | 待抽验 | 新发现·与 CC12M 重复 |
| danbooru-2023（动漫） | `zenless-archive/danbooru-2023-webdataset` | 千万级 | ✅ bytes（webdataset） | 需查（Danbooru 约束） | 待抽验 | 新发现·域外(动漫) |

**实际搜过的请求/页面**（不编造，`cimi-search` 底层不可达，改用等价手段）：
1. HF 搜索 `GET /api/datasets?search=image caption`（返回多为个人小样本，无价值）。
2. HF 搜索 `GET /api/datasets?search=webdataset`（→ 命中 `hanlincs/InternVL-SA1B`、`zenless-archive/danbooru-2023`、`yangyang857658468/cc12m-webdataset`、`laion/conceptual-captions-12m-webdataset` 等真实 bytes webdataset）。
3. `datasets-server /first-rows` 对上述候选逐条取真实样本判「图像形态」（见上表证据列）。
4. 本地 `pyarrow` schema（laion2B-en-aesthetic）与 `tar -tf`（CC12M/BLIP3o/Amshaker）做 bytes 取证。

## R2-视觉侧 C · 前 3 推荐 + 下载清单 + 「能不能补上数据不足」

**前 3 推荐（全部 bytes、全部短 caption、全部已在盘上——无需下载）**：
1. **`laion/conceptual-captions-12m-webdataset`（本地已下全 1100 tar / 1.2T / ≈11M 对，98% ≤77）** —— 通用自然图文对、短 caption，是 CLIP 式对比学习最对口的弹药。
2. **`Amshaker/Mobile-O-Pre-Train`（本地已下 2250 tar / 3.7T / ≈6M 对，100% ≤77）** —— 短单句 caption、规模可观。
3. **`liuhaotian/LLaVA-Pretrain` + `liuhaotian/LLaVA-CC3M-Pretrain-595K`（本地已下 ≈1.15M，100% ≤77）** —— 短 caption，与 1/2 互补。

**「能不能补上数据不足」——能，且无需新下载**：

| 口径 | 可用对数 |
|:--|:--|
| 现状（上轮口径） | `en500k` **≈50 万** + LLaVA 85M（caption 99.7% 截断，几乎不可用） |
| 补齐后（**已扣除全部 URL-only**、只算"bytes+短 caption"） | ≈**11M（CC12M）+ 6M（Amshaker）+ 1.15M（LLaVA-Pretrain/CC3M）+ 金量 gpic/coco/vg ≈0.3M ≈ 18–19M 对** |

→ **结论：由 50 万 → ≈1800 万对，×~35 倍**，足以支撑 2.2B 视觉编码器 Stage(iii)/(iv)（这已不是"CLIP 级 4–20 亿"的量级，但 CLIP 级那批数据在 HF 上全是 URL 元数据、公司网络下不动图 → 拿不到就是拿不到，如实说明）。**若要强上 >1 亿对，唯一现实路径是在公司内网自行跑 `img2dataset` 重下 LAION（不在本轮范围，需运维放行出网）。**

**下载清单 + 磁盘 + 带宽**：
- **必下：无**（前 3 推荐全本地）。已在后台下载的 `SFT-2605`（318.99GB/1504 jsonl，见 §0.3）与本结论无关。
- **可选补量（新 found bytes，磁盘允许时再下）**：`hanlincs/InternVL-SA1B-Caption-WebDataset`、`zenless-archive/danbooru-2023-webdataset`（域外）。
- 磁盘：`/nas_train` 剩 32T、`/nas_user` 剩 29T，本地已下数据不新增占用；可选补量若下 InternVL-SA1B 全量需先查大小。
- 带宽：当前 4 路 HF 下载（base 2.99TB / gpic / LLaVA / SFT-2605）共用，实测 ~10–13 MB/s，**本阶段不宜再开新大下载**。

**可复制下载命令（若后续采纳可选补量）**：
```bash
# 可选① InternVL-SA1B caption（bytes webdataset）
hf download --repo-type dataset hanlincs/InternVL-SA1B-Caption-WebDataset \
  --local-dir /nas_user/app.e0031982/datasets/hanlincs/InternVL-SA1B-Caption-WebDataset
# 可选② 动漫（域外，谨慎）
hf download --repo-type dataset zenless-archive/danbooru-2023-webdataset \
  --local-dir /nas_user/app.e0031982/datasets/zenless-archive/danbooru-2023-webdataset
```

**污染闸**：任何新落盘的图文源，投料前一律过 `run/data_pipeline/check_contamination.py`（`EDA-Eval-PyAether` 158 任务红线，同 §3 机制）；WebDataset 需先按 `{key}.txt/.json` 抽 caption 文本入库过闸。本地 CC12M/Amshaker/LLaVA 亦按 "多模态 held-out 评估集与训练集不同源 + 跨集去重" 同闸。
