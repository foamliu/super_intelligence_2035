# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。

| 项 | 当前值 |
|:---|:---|
| **当前指令** | 🎯 **（2026-10-01 夜 · 三次修订）按序做这几件**：<br>**① ⭐ 重下 `UltraData-SFT-2605`** —— 运维**已在 HF 网页点同意条款**（原先 `gated=auto` 卡住，落盘只有 README + LICENSE + 179 个 `.lock`）。下完报**实际字节数 + 文件数 + 与 HF 官方清单的一致性**。<br>**② 🔴 当前主攻 = §0.3 + §0.4「R2 阶段」** —— 上一轮 R 的**事实层合格、结论层不合格**（两处）：<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.3（LLM 侧 / P-8 数据方案）**：你拿 **"BaiZe 计划未用"** 当理由跳过了 `Ultra-FineWeb`(base) / `UltraX-Preview` / `UltraData-RL-2609`，**那是循环论证**（计划是在不知道这些源存在时定的）。<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.4（视觉侧 / 找更多图文对）**：你**自己**给了「视觉编码器训练数据**严重不足**」的结论（`en500k` 仅 50 万对、LLaVA 85M 的 caption 99.7–100% 被截断），**却从没去 HF 找过任何通用图文对** —— 反而把问题缩小成「要不要找 EDA 版图/原理图」然后答「不值得」。**那是答错了题。**<br>&nbsp;&nbsp;&nbsp;&nbsp;**本轮两份都要交**：**8 源事实表填满（无 `?`）· base vs L3 重叠率数字 · P-8 三档投料+下载清单** **＋** **本地多模态源逐条实测 · ≥10 个 HF 通用图文对候选（含实测短 caption 率）· 前 3 推荐 + 下载命令**。<br>&nbsp;&nbsp;&nbsp;&nbsp;🚫 **禁止"待定"/"视情况"/"不在计划内"/"不值得找"（除非先给出找过的清单与规模）**；**若判定为新增且磁盘允许 → 直接开始下载**。<br>&nbsp;&nbsp;&nbsp;&nbsp;💡 特别提示：**`Recap-DataComp-1B`（十亿级）与 `conceptual-captions-12m`（CC12M，短 alt-text）可能已经在盘上** —— 优先核实。<br>**③ 🚫 `phase3_domain`（EDA 领域语料）已正式取消** —— 不再找来源、不再调研、不再入库。理由：其评测 prompt 由 docstring 生成、**与语料天然同源**，"把测试集放进训练集"**没有意义**。<br>&nbsp;&nbsp;&nbsp;&nbsp;⚠️ **必须区分**：被取消的是「**EDA 语料线**」；`EDA-Eval-PyAether` 158 任务的**黑名单红线依然有效、必须继续执行**（那是"禁止"，不是"语料"）。 |
| **优先级覆盖** | **① SFT-2605 重下 + ② §0.3/§0.4 R2 调研 > 其他一切**（三者可并行：重下是 I/O，调研是读 + 少量下载）；<br>`phase1/2/4`（重 I/O，等下载）**本阶段不碰**；<br>🚫 **`phase3_domain` 已取消**，**不要再碰**（任务书 §2 相应行已划掉） |
| **状态索取** | `<无>`（若运维写入具体问题，本轮**先答该问题**再干活，答案写进 `MEMORY_DATA.md` 顶部的"运维问答"区） |
| **暂停标志** | `<无>`（若写入 `STOP`，本轮**只更新记忆、不做任何 I/O 与数据处理**，然后退出） |

---

## 📊 进度快照（**每次唤醒必须更新**，供远程巡检）

> 固定格式写在 **`MEMORY_DATA.md` 最顶部**，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ **`WAITING` 只写在 `MEMORY_DATA.md` 的顶部单独一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
**绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。
（pretrain loop 就是因为正文里出现了一句 `WAITING: **1**` 的散文而被误匹配，一直在长睡。）

**运维巡检方式**：外部运维通过 `git pull` 读取 `MEMORY_DATA.md` 顶部 + `DATA_LEDGER.md` + `CONTAMINATION_CHECK.md` 即可掌握进度；**不需要登录服务器**。

---

## 0. 🎯 当前主攻

> **R 阶段（只答两问）✅ 已收敛** → 产出 `run/DATA_RESEARCH.md` v1.1（事实层扎实）。
>
> | 节 | 状态 |
> |:--|:--|
> | §0.1 / §0.2 | ⏹ **历史**（R 阶段的两问，已完成；§0.2 已被 §0.4 取代） |
> | **§0.3** | 🔴 **当前主攻（LLM 侧）** —— P-8 数据方案 |
> | **§0.4** | 🔴 **当前主攻（视觉侧）** —— vision encoder 训练数据：去 HF 找更多通用图文对 |
>
> 原因：上一轮 R 的**事实层合格、结论层不合格**（两处，详见 §0.3 与 §0.4 开头）。
> **本轮两份都必须给出可执行的结论。**

---

## 0.3 🔴 R2 阶段 —— **P-8 数据方案**（**必须给结论，不许再"待定"**）

> ### 为什么又要做一轮：上一轮的结论层不合格
>
> 上轮 `DATA_RESEARCH.md` v1.1 把三个源一句话带过：
> - `Ultra-FineWeb`（base，**1T en + 120B zh**）→ ⬜「未下（**BaiZe 计划未用**）」
> - `UltraX-Preview`（MiniCPM5 的**新增 web 源**）→ ⬜「未下」+ **只有一句"HTTP 200"，连多大都没写**
> - `UltraData-RL-2609` → ⬜「未下」
>
> 然后下结论："这三者均**不在 BaiZe 计划的落地范围内**，故**不算必须补齐的缺口**"。
>
> 🚫 **这是循环论证**：**那个"计划"是在我们还不知道这些源存在的时候定的**。
> 拿"计划里没有"来证明"不需要"，等于用结论证明前提。**本轮不允许再出现这种写法。**
>
> ### 背景已经变了
> 现在确定要跑 **P-8 = Stage (i) 完整训练**（见 `BAIZE_PRETRAIN_2B_TASK.md`）：
> **推荐预算 100B token**（下限 44B / 上限 200B），**在真实全量语料上从零训**。
> **→ P-8 到底喂什么数据、要不要补下载，由你给出结论。**

---

### 🚫 本轮禁止出现的回答形式

| 禁止 | 为什么 |
|:---|:---|
| "BaiZe 计划未用" / "不在计划范围内" | **不能作为不下载的理由**（循环论证，见上） |
| "公开可下载" 却**不给规模** | 不给行数/字节/token = 没调研 |
| "待定" / "视情况" / "后续再看" | **每个问题必须落地成可执行的决定** |
| 只写"未找到"就结束 | 可以写"未找到"，但**必须同时给出你的建议方案** |

---

### A. 逐源事实表（**8 个源全部要，一个不许漏**）

MiniCPM5 官方列的 8 个训练数据源，逐个填满：

| 源 | HF URL | 许可 | 行数 | 字节 | **token 估算** | 本地 | 判定 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| **Ultra-FineWeb (base)** | | | | | **?** | ❌ | **?** |
| **UltraX-Preview** | | | | | **?** | ❌ | **?** |
| Ultra-FineWeb-L3 | ✅ | | | 1.9 TiB | ≈690B ✅ | ✅ | 已下全 |
| UltraData-Code | ✅ | | | | **?** | ✅ | 已下全 |
| UltraData-Math | ✅ | | | | **?** | ✅ | 已下全 |
| UltraData-SFT-2605 | ✅ | apache-2.0 | | | n/a | 空壳 | 重下中 |
| UltraData-SFT-Agent-2609 | ✅ | apache-2.0 | | | n/a | ✅ | 就绪 |
| UltraData-RL-2609 | | | | | n/a | ❌ | **?** |

> ⚠️ **表里所有 `?` 都必须填掉**。特别是 **`UltraX-Preview`** ——
> 它是 MiniCPM5 相对前代**新增的 web 源**，很可能有明确的设计意图。
> **必须查清：它是什么、多大、什么构成、和 FineWeb 系什么关系。**
>
> 工具：HF REST API `https://huggingface.co/api/datasets/<repo>`（siblings + size）、
> `https://datasets-server.huggingface.co/size?dataset=<repo>`（rows / bytes）。
> 上轮已实测这条路可用（`curl` 直连 + `datasets-server`）。token 用**抽样分词外推**（口径写清）。

---

### B. ⭐ 重叠分析 —— 决定"要不要下 base"

`Ultra-FineWeb`（base，1T en + 120B zh）与 `Ultra-FineWeb-L3`（≈690B token）**是什么关系？**

1. base 是**包含** L3，还是与 L3 **互不相交**？还是**部分重叠**？
2. **抽样实测**：两边各抽 N（建议 ≥500）条文档，按 **URL / hash / 文本前缀** 算**重叠率**。
3. **🔴 结论必须是一句话**：下 base 是「**+≈1.1T token 的新增语料**」还是「**重复劳动**」？

> 若官方文档查不到关系说明，**就用抽样实测给数字**。**不允许只写"关系不明"。**

---

### C. ⭐⭐ P-8 数据方案（**本轮的最终交付物**）

给定 P-8 预算 **100B token**（并**同时**给出 **44B** 与 **200B** 两档的建议），逐条回答：

1. **投料清单**：用哪些源、**什么配比**？
   给出可直接照做的形式，如 `L3(86%) + Code(10%) + Math(4%)`；
   并说明**是否因新增 base / UltraX-Preview 而调整**（若调整，给出理由与预期收益）。
2. **要不要新下载**？逐项：下什么、多大、**磁盘够不够**（`/nas_train` **只剩 32T**）、
   **按实测带宽估计要多久**（给出实测下载速度）。
3. **产出格式与路径**：`.bin/.idx` 怎么切、放哪、多大（按 100B token 估算）。
4. **污染闸**：新下载的源**必须**过 `check_contamination.py`（`EDA-Eval-PyAether` 158 任务红线）。
5. **下载命令**：若要补 base / UltraX-Preview，给出**可复制**的 `hf download` 命令。

> 🔴 **若 B 判定为"新增"且磁盘允许 → 本轮直接开始下载**（不要等、不要再问）。
> 同时把下载进度写进 `MEMORY_DATA.md`（沿用既有 `find`-count 口径）。

---

### D. MiniCPM5 逐源配比 —— **再查一轮**

上轮结论"未找到"。**本轮再查**，按此顺序，并**列出你实际查过哪些页面**：
1. MiniCPM5 技术报告（arxiv / HF model card / `openbmb` GitHub）
2. `openbmb/MiniCPM5` **collection 里每个数据集的 dataset card**（上轮似乎只看了模型卡）
3. **arxiv 2602.09003**《Tiered Data Management》全文（上轮只看了摘要层）

> 若仍找不到，**写"未找到"并列出查阅清单**（不编造）。
> ⚠️ **但不要用"未找到"就结束** —— 必须接着给出：**在没有官方配比时，你建议用什么配比**（= C.1 的答案）。

---

### R2 阶段的完成判据

**下面每一条都必须有明确答案，缺一不算完成：**

- [ ] A 表 **8 行填满，无 `?` 残留**
- [ ] B 给出一句话结论 + 重叠率**数字**
- [ ] C 给出 100B / 44B / 200B 三档的**投料清单 + 下载清单 + 磁盘/带宽估算 + 可复制命令**
- [ ] D 列出查阅清单；找不到就给出建议配比
- [ ] 新下载的源完成污染扫描
- [ ] 更新 `DATA_RESEARCH.md`（追加 R2 节）+ `DATA_LEDGER.md` + `MEMORY_DATA.md`

---



## 0.1 🅰 问题 1 —— LLM pretrain 的数据够不够？配比怎么定？

**(1) MiniCPM5 的数据下全了吗？**
- 本地实测：`Ultra-FineWeb-L3` 等 = **616 parquet / 617.6 GiB**（见 `DATA_LEDGER.md` §0）。
- **去 HF（openbmb / MiniCPM5 官方）核对官方清单**：文件数、总规模、是否有未下的分片或子集。
- 判定：**"下全了" / "缺哪些"**，缺的给出**具体清单**。

**(2) 够不够？**
- 实测**全量 token 数**：抽样 20–50 个 parquet，用 `tokenizer_eod` 分词外推 → 给**总量估计**。
- 对照需求：2.2B 模型、4 个月算力窗口（~93K tok/s → 30 天 ≈ **242B token**）。
- 判定：**够 / 不够**，并给出"**能支撑多少天训练**"。
- 🔴 **顺带必须判定**：论文 §4 写的 **"≈1.8T tokens" 是否写错**——本地 617.6 GiB 按已切产物的
  `4 B/token` 口径反推只对应 **~400B token**（差 4–6 倍）。**论文里白纸黑字写着，必须给结论。**

**(3) 配比怎么定？—— 两条路，请明确建议走哪条**
- **路线 A（简单，优先评估）**：**直接用 MiniCPM5 配比好的数据。**
  → 查清：**MiniCPM5 官方发布的训练配比是什么**（各源占比）？**这些源本地是否具备**？
  若能直接复用，**需要做的最小改动是什么**？
- **路线 B（搜索）**：**用 `MATH` + `MMLU` 做代理指标，搜最优配比**
  （即 *Data Mixing Agent* 一类论文的做法）。
  → 给出：**可执行方案 + 成本估算**（需多少组配比 × 每组多少 token = 总 GPU·h）。
  → ⚠️ **依赖**：该路线需要**能跑 MATH/MMLU 评测**，即依赖 pretrain 侧的
  **P-6（mcore→HF→SGLang→lm_eval）** 基建。**基建未就绪时，路线 B 只能给方案、不能执行。**
- **请明确建议 A 还是 B，并说明理由。**
  现状参考：当前退火配比是 `L3(86):code(10):math(4)`（Round 1 的 S4 三点消融得出）。

**(4) 是否需要在 HF 继续寻找？**
- **仅当** (2) 判定"不够"、或 (3) 路线 A 缺源时才需要；
- 给**具体候选 + 规模 + 许可 + 可得性**，不要泛泛罗列。

## 0.4 🔴 R2 阶段（视觉侧）—— **vision encoder 训练数据：去 HF 找更多合适的图文对**

> ### 为什么这是本轮必做
> 你自己在 `DATA_RESEARCH.md` v1.1 里给出了「**视觉编码器训练数据严重不足**」的结论：
> `en500k` 只有 **50 万对**；LLaVA 85M 虽有 8500 万张图，但 **caption 99.7–100% 被截断**、可用性差。
> **既然结论是"严重不足"，那就必须去找。** 你有 `cimi-search` / `cimi-fetch` + HF REST API，
> **完全具备这个能力**。**只给"不足"的结论、却不给"去哪找"，这份调研就没做完。**

> ### 🚫 上一轮**答错了题**（必须纠正）
> 上一轮 `Q2(4)` 把问题**缩小**成了：「是否需要在 HF 继续找 **EDA 版图/原理图/电路图** 数据集？」
> 然后答「不值得（K 级、任务特定、许可不明）」。
>
> **这不是本题。** 版图/原理图属于 Stage (iii)/(iv) 的**领域适配**，与**预训练数据量**是两码事。
> 本题问的是：**「有没有更多、更大、与 CLIP 式对比学习匹配的 _通用_ 图文对？」**
> 🚫 **本轮不许再把问题缩小到领域数据集。**
> （另注：运维已取消 **EDA 文本语料线**；视觉侧的领域数据同样**不在本轮范围**，聚焦通用图文对。）

### 🚫 禁止的回答形式（与 §0.3 同）
- 「不值得找」—— 除非**先列出你找过哪些、规模各多少**，再论证
- 「本地够用」—— 除非给出**当前可用对数**与**目标对数**的**数字对比**
- 「关系不明」/「待定」/「后续再看」

---

### A. ⭐ 先盘点**本地已有**的多模态源（**很可能是你漏了**）

`BAIZE_DATA_TASK.md` §1.1 列了 `/nas_user` 那一整块，**其中有多条可能直接可用**。
**逐条实测**（`du -sh` + 抽样看格式），把下表**填满**：

| 本地已有 | 路径 | 是图文对吗 | 图像数 | caption 长度分布 | **≤77 可用率** | 判定 |
|:--|:--|:--|:--|:--|:--|:--|
| `conceptual-captions-12m-webdataset` | | | | | | |
| `laion2B-en-aesthetic` | | | | | | |
| `Recap-DataComp-1B` / `UCSC-VLAA/Recap-DataComp-1B` | | | | | | |
| `BLIP3o-Pretrain-Long-Caption` | | | | | | |
| `Amshaker/Mobile-O-Pre-Train` | | | | | | |
| `coco` / `vg` | | | | | | |
| `FineVision`(188 子集) / `LLaVA-Pretrain`(664 子集) | | | | | | |
| `ocr_vqa` / `textvqa` | | | | | | |
| `LLaVA-OneVision-1.5` 全家桶（含 `-packed-webdataset`） | | | | | | |

> ⚠️ **每一行都必须填。** 特别留意两个：
> - **`Recap-DataComp-1B`** —— 重新打标的 DataComp-1B，**十亿级**；
> - **`conceptual-captions-12m`（CC12M）** —— **短 alt-text，天然适合 CLIP 式对比**。
>
> **这两个如果真在盘上，可能直接解决"数据不足"。请优先核实。**

---

### B. ⭐⭐ 再去 HF 找**新的通用图文对**（**本轮的最终交付物**）

**目标量级**：CLIP 级是 **4–20 亿对**；本项目即使打折，也应瞄准 **≥1 亿对可用**。

**"合适"的三条判据（三条都要满足）**：
1. **是图像-文本对**（不是纯图像分类集、不是 VQA、不是交错网页）
2. **caption 短且干净** —— **≤77 token 占比要高**
   （这一条**直接决定**能不能用当前那个**冻结的 CLIP 文本塔 + 77 token**）
3. **规模 ≥1000 万对** 且 **许可明确**（可入库、可随论文发布）

**必查清单（至少覆盖这些，且每行都要有实测数字）**：

| 候选 | HF repo | 规模（行/字节） | 许可 | **短 caption 率** | 判定 |
|:--|:--|:--|:--|:--|:--|
| DataComp-1B 系列 | | | | | |
| LAION-2B / LAION-400M（及 aesthetic 子集） | | | | | |
| COYO-700M | | | | | |
| Recap-DataComp-1B | | | | | |
| DFN / DFN-2B / DFN-5B | | | | | |
| PixelProse | | | | | |
| RedCaps / YFCC-15M | | | | | |
| CC12M / CC3M / SBU | | | | | |
| WIT（Wikipedia Image-Text） | | | | | |
| LAION-COCO | | | | | |
| OBELICS / MMC4（交错图文，需切对） | | | | | |
| **你自己搜到的其他源**（见下） | | | | | |

> ### 🔴 必须真的用 `cimi-search` 去搜
> 用 `cimi-search` / `cimi-fetch` 搜这些方向，**把你新找到的也加进上表**：
> 「CLIP pretraining dataset」「image-text pairs short captions」「open image text dataset billion scale」
> 「contrastive learning dataset huggingface」等。
> 🚫 **不许只把常见名字抄一遍就结束。**
>
> **短 caption 率必须实测**：用 `datasets-server /first-rows` 取**真实样本**，
> 抽样分词算 **≤77 token 占比**（每源抽 N 条，口径写清）。
> 工具：HF REST API `/api/datasets/<repo>`（siblings+size）、`datasets-server /size`（行数）、`/first-rows`（真样本）。

---

### C. 给出**数据方案**（**不要再只给方案不执行**）

1. **推荐用哪几个源？** 按「规模 × 短 caption 率 × 许可清晰度」排序，给出**前 3 个**。
2. **🔴 能不能补上"数据不足"这个洞？** 必须明确回答：
   **当前可用对数 → 补齐后可用对数 → 是否足以支撑 Stage (iii)/(iv)**。
3. **下载清单 + 磁盘 + 带宽**：下什么、多大、`/nas_train` 剩 **32T** 够不够、按**实测带宽**要多久。
4. **可复制的下载命令**（`hf download ...`）。
5. **污染闸**：新源必须过 `check_contamination.py`（`EDA-Eval-PyAether` 158 任务红线）。

### 完成判据
- [ ] **A 表全部填满**（本地已有源逐条实测，含 ≤77 可用率）
- [ ] **B 表 ≥ 10 行**，每行含 HF **实测规模 + 实测短 caption 率**
- [ ] 至少**新增 3 个**由 `cimi-search` 找到、不在上表清单里的候选源
- [ ] **C 给出前 3 推荐 + 下载清单 + 可复制命令**，并**明确回答"能不能补上数据不足"**
- [ ] 更新 `DATA_RESEARCH.md`（追加「R2 视觉侧」节）+ `DATA_LEDGER.md` + `MEMORY_DATA.md`

---


## 0.2 🅱 问题 2 —— Vision encoder 的数据够不够？配比怎么定？

> ⚠️ **本节是 R 阶段的早期版本，已被 §0.4 取代**（保留作历史记录）。
> **本轮请按 §0.4 执行** —— 特别是 §0.2 的 Q2(4) 把问题缩小成了"要不要找 EDA 版图/原理图"，
> **那是答错了题**（见 §0.4 开头）。

> ⚠️ **背景（必读）**：vision 侧 R3 已判定**训练发生表征坍缩**——两塔退化为常量嵌入，
> 四个架构都塌到同一均衡点。而 R3 列出的**怀疑之一就在数据侧**：
> **`SimpleTokenizer` 的 77-token 截断** + **LLaVA Mid-Training 的长 recaption 被截断后互相高度相似**。
> → **本问题是"数据是否为坍缩元凶"的事实层调查**；
> **训练侧的验证由 vision agent 的 R4 负责 —— 你不要重复做训练实验。**

**(1) 两份数据各自是什么？**
- `LLaVA-OneVision-1.5-Mid-Training-85M`（本地实测：EN 5545 + CN 1512 parquet，**下载中**）
- **`Stanford GPIC`**（`/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/`，
  含 `train` / `test` / `reference_stats`；tar 内 `{key}.json` + `{key}.jpg|png`，
  **caption 分 `tag` / `short` / `medium` / `long` 四档**）
- 各给：**图像数 / 对数 / tar 数 / 总字节 / 许可证**。

**(2) ⭐ caption 长度分布 —— 这是关键**
- 对**每份数据、每一档 caption**，统计**词数**与 **CLIP token 长度**的分布。
- 判据：`open_clip.tokenizer.SimpleTokenizer` 的**上下文长度是 77，超出即截断**。
- **必须给出"会被截断的比例"**；并**特别标出 GPIC 的 `tag` / `short` 是否正好落在 77 以内**。
- 🔑 **这是本问题最想要的结论**：若 LLaVA 长 recaption 被大面积截断、而 GPIC 的 `tag`/`short` 不被截断，
  则**换数据（或换 caption 档）本身可能就解决大半坍缩问题**。

**(3) 配比怎么定？**
- 85M（含 EN/CN）与 GPIC **怎么混**？caption 用哪一档？
- 给**具体建议 + 理由**，必须结合 (2) 的截断分析。

**(4) 是否需要在 HF 继续寻找？**
- 公开的**版图 / 原理图 / 电路图**视觉数据集有哪些（规模、许可、可得性）？
- ⚠️ **只给"是否值得引入"的判断**，不要展开长篇综述。

### R 阶段执行要求（逐条遵守）

1. 🚫 **只做上面两个问题**，**不要扩展**到 agentic SFT/RL 数据、长上下文、去污染方法、偏好数据等
   —— **那些本阶段一律不做、不写**。
   ⚠️ **EDA 语料已是"正式取消"，不再是"本阶段不做"** —— **永久不做**（见运维指令区 ②）
2. 每问产出一张表：`候选源 | URL | 规模 | 许可 | 可得性 | 建议 | 优先级`
3. **必须给 URL**；头部候选要用 `cimi-fetch` **抓正文核实**，**不要只凭搜索结果标题下结论**
4. **区分三类可得性**：`公开可直接下载` / `需申请或注册` / `仅论文描述（无公开数据）`
5. **许可写清**（Apache / MIT / CC-BY / 仅研究 / 不明），**"不明"显式标红** ——
   论文写了 "we release the recipe"，数据许可直接影响可发布性
6. **先与本地对照**（`DATA_LEDGER.md` §0 / §3 与任务书 §1.1），避免调研已就位的东西
7. 🚫 **只调研，不下载**
8. **不滥用搜索**：每问聚焦 3–8 条高线索，**宁可少而核实，不要多而未核实**

### R 阶段的完成判据

`run/DATA_RESEARCH.md` 中：

- **问题 1（LLM pretrain）**：四小项全部有结论；给出**"数据够不够"**与**"配比走 A 还是 B"**的**明确建议**；
  并完成两个**必答判定**：① **MiniCPM5 是否下全**；② **论文 §4 的 "≈1.8T tokens" 是否写错**。
- **问题 2（Vision encoder）**：四小项全部有结论；给出**"85M + GPIC 行不行"**与**"配比怎么定"**的**明确建议**；
  **必须包含 caption 截断比例的量化分析**（对 77-token 口径）。
- 每条关键结论都能顺着 URL 复核。

---


## 1. 任务目标

把已在盘上的原始语料，变成**训练可直接消费、配比正确、且不污染评测集**的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ **← 🚫 已取消**（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. **污染隔离白/黑名单 + 校验脚本（红线，P0）**

**上游方案文档（先读它）**：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
**时间线约束**：ISEDA 2027 投稿截止 ≈ **2027-02-01**；本任务必须在 **2026-11 底**前可交接（见方案 §6）。

> **注意本任务的定位**：瓶颈是**算力窗口**不是数据量（方案 §2.1）。
> 所以**不要**把精力花在"下载/切分更多数据"上，而要花在**质量、配比、格式可用性、隔离**上。

## 1.1 数据落盘地图（实测背景 · 2026-10-01 勘定）

> 本节由**实地探查**得出，用于纠正本任务书成稿时对数据位置的误记。
> 每轮唤醒 / phase 复核时以此节为索引，`DATA_LEDGER.md` 为实测明细，二者互相印证；**最终一律以实测为准**。

**三块挂载 + 三条 HF 组织名线索**（HuggingFace 数据集按 `org/repo` 落盘）：

| 挂载 | 定位 | 关键内容 |
|:---|:---|:---|
| `/nas_train/app.e0031982/datasets/` | **多模态主库**（生产 + 派生） | `mvp-lab/`（LLaVA-OneVision-1.5 全家桶）、`baize-vision/`、coco/gqa/imagenet/laion2B/FineVision/LLaVA-Pretrain/MMMU… |
| `/nas_inference/app.e0031982/datasets/` | **只读源 / 下载中转**（**纯文本主力在此**） | `openbmb/`（Ultra-FineWeb-L3、UltraData-Code/Math/SFT-2605/SFT-Agent-2609）、`stanford-vision-lab/gpic` |
| `/nas_user/app.e0031982/datasets/` | 少量多模态 / 领域语料 | `mvp-lab/`（OV1.5 webdataset、OV2）、`BLIP3o/`、`UCSC-VLAA/`、`Amshaker/`、`ayoubkirouane/`、`cxmt/` |

**① 多模态主库 —— `/nas_train/app.e0031982/datasets/`**
- `mvp-lab/`（⚠️ 是连字符 **`mvp-lab`**，不是 `mvp_lab`）— LLaVA-OneVision-1.5 系列：
  - `LLaVA-OneVision-1.5-Instruct-Data`（183 个任务子集，SFT / 对齐主体）
  - `LLaVA-OneVision-1.5-Mid-Training-85M`（子集 coyo/datacomp1b/imagenet/laioncn/mint/obelics —— 即 phase0 已盘点项）
  - webdataset 派生：`-packed-webdataset` / `-webdataset` / `-webdataset-16384` / `Quick-Start-3M` / `MultiMixQA-opt46|47`
  - `LLaVA-OneVision-1.5-RL-Data`、`LLaVA-558K-Webdataset`、`LLaVA-NeXT-780k*`
- `openbmb/Ultra-FineWeb`（纯文本，**仅** Ultra-FineWeb 基础版，非完整 Ultra-* 套件）
- `baize-vision/`（en500k / eval5k —— vision agent 派生产出）
- 其他多模态（可选补充源）：`coco`、`gqa`、`imagenet-1k`、`laion2B-en-aesthetic`、`FineVision`(188 子集)、`LLaVA-Pretrain`(664 子集)、`MMMU`、`ocr_vqa`、`textvqa`、`vg`、`conceptual-captions-12m-webdataset`、`LLaVA-CC3M-Pretrain-595K`、`LLaVA-Instruct-150K`
- 非数据（勿混）：`stanford-corenlp-full-2016-10-31`（NLP 工具，非斯坦福视觉数据）

**② 纯文本主力 —— `/nas_inference/app.e0031982/datasets/openbmb/`**
- `Ultra-FineWeb-L3`（Stage(i) 主体）、`UltraData-Code` / `UltraData-Math`（退火源）、`UltraData-SFT-2605` / `UltraData-SFT-Agent-2609`（Stage(ii) SFT）
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/openbmb`，实际在 **`/nas_inference`** 挂载。

**③ 斯坦福视觉数据 —— `/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic`**
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/stanford-vision-lab`，实际在 **`/nas_inference`**。`gpic`（含 train / test / reference_stats）。

**④ 少量多模态 / 领域 —— `/nas_user/app.e0031982/datasets/`**
- `mvp-lab/`：`LLaVA-OneVision-1.5-Mid-Training-85M-webdataset`、`LLaVA-OneVision-2-Data`、`ov2_quickstart`
- `BLIP3o/BLIP3o-Pretrain-Long-Caption`、`UCSC-VLAA/Recap-DataComp-1B`、`Recap-DataComp-1B`
- `Amshaker/Mobile-O-Pre-Train`、`ayoubkirouane/CircuitVQA`
- `cxmt/`（EDA / 电路相关标注与 benchmark —— ~~phase3 领域排查时可查~~ **🚫 该线已取消，不再排查**）

> 对数据 agent 的影响：phase0 已盘点的主路径（`/nas_inference/openbmb`、`/nas_train/datasets/mvp-lab`）正确；
> 但 phase0 尚未覆盖 `②` 里的 Ultra-FineWeb 基础版（`/nas_train/.../openbmb`）、`③ stanford-vision-lab/gpic`、`④ /nas_user` 整块 —— 后续 phase 复核时把这些补齐进 DATA_LEDGER。

---

## 2. 阶段与推荐执行顺序

```
推荐顺序： 【🎯 当前】phase1 validate（含 ① SFT-2605 重下） → phase0 inventory ✅ → phase5 isolation ✅ → phase2 text → phase4 mm → phase6 handoff
🚫 phase3 domain —— **已取消，从流水线移除**（见运维指令区 ②）
```

> **为什么 phase5（污染隔离）排在最前**：它必须在**任何"训练可消费产物"产出之前**就位。
> 如果先切了数据再立闸，已经切好的数据要全部重扫、甚至重切——**白做一遍**。

| 阶段 | 做什么 | 完成判据 |
|:---|:---|:---|
| **R** `research` 🎯 **当前主攻** | 用 `cimi-search` / `cimi-fetch` **只回答 §0 的两个问题**（LLM 数据够不够+配比 / Vision 数据够不够+配比） | `DATA_RESEARCH.md`：两问各四小项全有结论 |
| **phase0** `inventory` ✅ | 对 `/nas_inference` 与 `/nas_train` 上每条数据线**实测**：文件数、总字节、目录结构、抽样看格式；确认哪些路径真实存在 | `DATA_LEDGER.md` 初版；**与方案 §1 的差异逐条列出** |
| **phase5** `isolation` | 建 EDA-Eval-PyAether 的黑名单指纹 + 训练集侧扫描脚本 + SFT 同闸 | `CONTAMINATION_CHECK.md` 初版 + 可复用脚本 |
| **phase1** `validate` | 下载完整性（parquet 全量可开 / tar 可解 / shard 无缺号）；损坏清单 | 损坏/缺失清单 + 校验命令 |
| **phase2** `text` | 通用文本分词打包成 `.bin/.idx`（stable 主体 + 退火源），**复用 Round 1 脚本** | 训练实测能加载并跑 10 步冒烟 |
| **phase3** `domain` 🚫 **已取消** | ~~EDA 领域语料排查（有哪些、在哪、能否导出/授权）→ 确认后入库并过闸~~<br>**运维 2026-10-01 正式取消**：评测 prompt 由 docstring 生成、**与语料天然同源**，"把测试集放进训练集"没有意义 | —（不再产出） |
| **phase4** `mm` | 多模态下载完成后：校验 → 统计 → 切子集 → webdataset 打包 → held-out 评估集 | Stage (iii) 能直接开跑 |
| **phase6** `handoff` | 清单终版 + 污染报告终版 + 结果 HTML + 可复现命令 | 可交接给训练 |

---

## 3. 红线：污染隔离（**违反则全部下游结论作废**）

🚨 **`EDA-Eval-PyAether` 的 158 个任务内容（`prompt` / `entry_point` / `test` 断言；注：v20260311 版无 `canonical_solution` 字段，见 DATA_LEDGER §1.3）
绝对不能进入任何训练集。** 改写/paraphrase 也不洗白。

- ✅ **允许**入训练集：PyAether / SKILL 的 **API 参考文档**（它是任务的"来源材料"）
- ❌ **禁止**入训练集：评测任务的 prompt、函数名、参考解、断言代码，及其改写版
- 机制必须包含：① 黑名单指纹 ② 训练集侧扫描 ③ **阈值写明可复现** ④ **SFT 语料同闸** ⑤ 独立报告
- 同一条规则适用于**多模态 held-out 评估集**（如 `eval5k`）：与训练集不同源 + 跨集去重比对

**评测集本体路径**（用于建黑名单，**只读，绝不写入任何训练集**）：
`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`

---

## 4. git 与共享工作区规则

### 4.1 前提：这是一个**共享工作副本**

**本任务、vision 任务、pretrain 任务共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

- **只需一个人 pull，其余立刻看到**：别的 agent 拉取后，你读到的 `$TASK_MD` 与所有文件同步更新。**不要重复 pull。**
- 工作区里**陌生的未提交改动很可能是别的任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉别人的成果。
- 多个 loop 各自 `git add -A && commit && push`（每 5 小时），**会互相把对方在途文件一起提交**，这是既有设计的已知副作用，**不要去"修正"它**。

### 4.2 你的 git 操作规程

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_DATA.md DATA_LEDGER.md CONTAMINATION_CHECK.md run/data_pipeline/ daily-memories-data/`
   🚫 **不要用 `git add -A`**——会把别的任务的在途文件卷进你的提交。
3. 若 behind / diverged：`git pull --rebase origin main`。
   - `cannot rebase: You have unstaged changes` → 是**多方在途改动**：先 commit 自己要提交的文件再 rebase；🚫 不要 stash/丢弃别人的改动。
   - `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：等 30–60 秒重试（≤3 次）；仍失败就记一行流水并**跳过本次 git 操作**。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind。
5. 流水记一行 git 结果。

> 参照：vision agent 在 `daily-memories-vision/2026-10-01.md:198` 用 `git pull --rebase` 恢复过，沿用同一做法。

### 4.3 数据产物**不入库**

`.bin/.idx`、webdataset tar、原始数据集**一律不提交 git**。只提交：`doc/` 下的文本（md/html/json）与 `run/` 下的**脚本**。
在报告与流水中写清产物的**绝对路径 + 规模 + 校验和**，训练侧据此取用。

---

## 5. 资源与约束

- **节点**：本 agent 常驻 `10.239.2.12`（主机 `whag0pgpuap12`）；数据在 NFS（`/nas_inference` 只读源、`/nas_train` 产出）。
- ⚠️ **与 GPU 任务共享 NFS 与带宽**：
  - **本节点 `.12` 有 2 个 HF 下载任务在跑**（`hf download`，2026-10-01 实测，各已运行约 1 小时+）：
    1. `mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M` → 写入 `/nas_train/app.e0031982/datasets/`（多模态下载进行中）
    2. `stanford-vision-lab/gpic` → 写入 `/nas_inference/app.e0031982/datasets/`（带 HF token；⚠️ token 已暴露在进程参数里，建议轮换，勿写进文档/日志）
    **下载期间不要做重 I/O / 全量扫描**，会互相拖慢
  - vision 任务需要一次"**无争用的干净吞吐测量**（R2-4）" → 启动重 I/O 前先读 `run/MEMORY_VISION.md` 看它进度，**优先避让**
  - pretrain 任务在 `10.239.2.29` 跑训练（另有协调规则）
- **不占用 GPU**（本任务不是 GPU 任务）；也**绝不杀他人进程**。
- **每轮唤醒单次预算 ≈ 25 分钟**；有长时任务时把 `WAITING` 置 1 让 loop 拉长睡眠。

---

## 6. 记忆管理

| 文件 | 作用 |
|:---|:---|
| `run/MEMORY_DATA.md` | 运行时状态：**顶部"进度快照"**（固定格式，供远程巡检）+ PHASE/WAITING/看板/流水 |
| **`run/DATA_RESEARCH.md`** | 🎯 **调研报告（当前主攻）**：只回答两个问题（LLM / Vision 的数据够不够 + 配比），每条含 URL / 规模 / 许可 / 可得性 / 建议 |
| `run/DATA_LEDGER.md` | **数据清单**（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | **污染隔离报告**（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 **`DATA_RESEARCH.md`（调研报告，当前主攻）** —— **两个问题各四小项全部有结论**，每条关键结论可顺 URL 复核
2. `DATA_LEDGER.md`（数据清单，含**实测**规模与与方案文档的差异）
3. `CONTAMINATION_CHECK.md`（污染隔离规则 + 阈值 + 扫描量 + 命中 + 处置）
4. `run/data_pipeline/`（可复现脚本，至少含盘点、校验、分词打包、指纹比对）
5. 训练可消费的产物（`.bin/.idx` + webdataset），**路径与校验和写入清单**
6. `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html`（自包含，与既有 HTML 报告同风格）
7. git commit + push（只提交 doc/ 文本与 run/ 脚本）

---

## 8. 推进原则

- **无阻塞时连续推进**：把能立即做完的步骤一口气做完（可跨多个阶段），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟）。
- **有异步阻塞时**：回写记忆并把 `WAITING` 置 `1`，记录"等待什么、如何判断结束"，然后退出。
- **不确定就如实记录并上报**，不要编造数据、不要产出"看起来对"的合成语料。

