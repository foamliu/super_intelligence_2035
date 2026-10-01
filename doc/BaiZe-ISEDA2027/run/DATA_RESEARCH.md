# DATA_RESEARCH.md — R 阶段数据调研报告（只回答两个问题）

> 版本 v1 · 2026-10-01 · 由 **R 阶段**产出（运维指令 §0，2026-10-01 修订：**原「10 主题 / 8 主题」清单已作废**）。
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
- MiniCPM5 **未在模型卡公开逐源百分比**（模型卡只给 8 个数据集的三阶段归属，⚠️摘要层；精确逐源占比在技术报告 arxiv:2602.09003，本机不可达、未核实到数字）。
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
| Stanford GPIC | https://huggingface.co/datasets/stanford-vision-lab/gpic | **mit** ✅实测 | tar 内 `{key}.json`+`{key}.jpg|png`；json 含 `caption_type∈{tag,short,medium,long}` + `caption` | **28T 像素**；100M train + 200K val + 1M test；**8000 train tar + 32 val + 128 test** | train **406/8000**（仍有进程在下载，++ 中）、test **128/128 全齐**、reference_stats 5 npz |

> 本地 LLaVA 85M 是 6/8 子集、GPIC train 是 406/8000 tar——两份**都还在下载**。但本问题要用的数据是「vision encoder 实际训练子集 = `imagenet/EN` 500K」（论文 6_vision 明写用了 500K imagenet/EN），该小支**已齐**（50 parquet），故 caption 分析不受影响。

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
- `⚠️摘要` 指 HF 模型卡/README 原文（本机连不上 arxiv/github/bocha，未抓论文全文）。MiniCPM5「逐源配比百分比」官方未在模型卡公开，属「未找到」而非编造。
- 「1.8T tokens 写错」第一步（1.8T = 磁盘字节）为**铁证级**（`MEMORY.md` 的 `du` 记录 + HF `num_bytes` 同量纲吻合）；第二步 token 外推（821/539/811/470 tok/doc）为**抽样估计**，phase2 分词后可用真实 `.bin` token 数替换，结论方向不变。

