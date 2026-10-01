# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。

| 项 | 当前值 |
|:---|:---|
| **当前指令** | 🎯 **主攻 §0「R 阶段：数据调研」**（2026-10-01 运维下发）——用 `cimi-search` / `cimi-fetch` 为 **5 个阶段**做数据调研，产出 `run/DATA_RESEARCH.md` |
| **优先级覆盖** | **R 阶段（调研）> phase1/2/4（重 I/O，等下载完成）> phase3（等授权）** |
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

## 0. 🎯 当前主攻：**R 阶段 —— 数据调研（为全部 5 个阶段做数据准备）**

> **运维指令（2026-10-01）**：本阶段主攻 **调研**。
> 你具备 **`cimi-search`（web 搜索）与 `cimi-fetch`（网页抓取）** 两个工具，**本阶段应主动使用它们**。
>
> **为什么现在做调研**：本地重 I/O 阶段（`phase1/2/4`）正被 **多模态下载未完成** 卡住，
> `phase3` 又卡在 **EDA 语料授权**。**调研不依赖这两件事**，而且它是后续所有 phase 的**前置输入**。
>
> **唯一交付物**：`run/DATA_RESEARCH.md`（调研报告）。
> **两条铁律**：① **每条结论必须给出可点击的来源 URL**；
> ② **查不到就如实写"未找到"——绝不允许编造数据集名、规模或许可**。

### R 调研清单（按优先级）

| ID | 主题 | 服务于 | 要回答的问题 |
|:---|:---|:---|:---|
| **R-A1** | **EDA / HDL 开源语料** | Stage (ii) 领域退火 + SFT | 有哪些**公开可得**的 Verilog / SystemVerilog / Tcl / SKILL 语料？各自规模、许可、获取方式？ |
| **R-A2** | **Agentic SFT / RL 数据与奖励设计** | Stage (ii) SFT + RLVR | 公开的 **agent 轨迹数据**有哪些？**RLVR / GRPO 在代码与 agent 任务上的奖励设计**最佳实践？（对照论文 §5.3 的 R1–R4 奖励臂） |
| **R-A3** | **长上下文语料与适配做法** | Stage (ii) 前置 | agentic trace 常规超 `4096` token；公开的**长上下文继续训练语料**与主流做法（RoPE 外推 / 数据混合 / 步数）？ |
| **R-A4** | ⭐ **HF 文本语料调研 + 本地完整性核对** | Stage (i) / (ii) | ① **openbmb 在 HF 上的官方清单**：Ultra-FineWeb-L3 / UltraData 各子集的**官方文件数与规模**是多少？**本地是否下载全**（本地实测 616 parquet / 617.6 GiB，需与官方对照）？② 还有哪些**高质量纯文本语料**可用（如 FineWeb / FineWeb-Edu / DCLM / SlimPajama / Dolma / RedPajama / CulturaX 等）——规模、许可、可得性？<br>🔴 **附带的必答硬问题**：论文 §4 写的 **"≈1.8T tokens" 是否写错**？本地 617.6 GiB 的 snappy parquet 按已切产物的 `4 B/token` 口径反推**只对应 ~400B token**（差 4–6 倍）。用 HF 官方标注 + 抽样分词外推，**给出判定** |
| **R-B1** | **EDA 视觉数据集** | Stage (iii) / (iv) | 公开的**版图 / 原理图 / DRC / 电路图**图像数据集有哪些？规模、标注形式、许可？ |
| **R-B2** | **「图像 ↔ 代码」自标注数据构造的先例** | Stage (iv) | 是否有公开先例：**执行脚本即得配对数据**（image→script / script→image）？同类做法与坑？ |
| **R-B3** | ⭐ **OpenVision2 论文 + 开源库调研** | Stage (iii) / (iv) | 既然**胜出架构是 OpenVision2**，必须把它研究透：① **开源库与论文链接**（repo / arXiv）；② **原作者的训练超参数**是什么——optimizer、lr、warmup、schedule、分辨率/patch、batch、数据增强、预训练语料与规模？**与我们 Round 1/R2 用的（lr=3e-3 / AdamW 0.9,0.95 / warmup 100 + cosine / 224-16 / bs 32×6 / en500k）差多少**？③ 🔴 **原作者是怎么评测 vision encoder 的**（zero-shot 分类 / linear probe / 检索 / 下游任务）？——这条**直接关系到 vision R3-1 正在查的"检索指标退化到随机水平"问题：如果原作者用的是别的评测口径，我们可能一直在用错的代理指标** |
| **R-C1** | **偏好数据与领域 RLHF（数据稀缺场景）** | Stage (v) | 偏好数据稀缺时如何做领域适配？DPO / SimPO / KTO / GRPO 变体、弱标注、合成偏好数据的实践与风险？ |
| **R-D1** | **去污染（decontamination）方法** | 全程**红线** | 当前公认做法？（13-gram / MinHash / 嵌入去重）业界对"评测集泄漏"的标准检测与报告方式？ |
| **R-D2** | **数据配比与 token 预算** | Stage (i) / (ii) | 2B 级模型、给定算力窗口下的**数据配比**经验（Chinchilla 之后的过度训练实践、领域配比）？ |

### R 阶段执行要求（逐条遵守）

1. **每个主题产出一张表**：`候选源 | URL | 规模 | 许可 | 可得性 | 建议用途 | 优先级`
2. **必须给 URL**；对每个主题的**头部候选**用 `cimi-fetch` **抓正文核实**——
   **不要只凭搜索结果的标题就下结论**（标题常与内容不符）
3. **必须区分三类可得性**：`公开可直接下载` / `需申请或注册` / `仅论文描述（无公开数据）`。
   这三类对我们的价值完全不同，**混在一起写等于没写**
4. **许可必须写清**（Apache / MIT / CC-BY / 仅研究用途 / 不明），**"不明"要显式标红**——
   论文里写了 "we release the recipe"，数据许可会直接影响可发布性
5. **先与本地资产对照再调研**：同类东西本地已经有了什么（见 `DATA_LEDGER.md` §0 / §3 与任务书 §1.1），
   **避免调研已就位的资源**；调研报告里要写"本地是否已有等价物"
6. 🚫 **本阶段只调研，不要真的下载**（下载属于 `phase2/4`，且要避开下载争用）
7. **不要滥用搜索**：每个主题聚焦 3–8 条高价值线索即可，**宁可少而核实，不要多而未核实**
8. 报告末尾给**综合建议**：每个 Stage 应优先采用哪 1–2 个数据源、为什么、还缺什么

### R 阶段的完成判据

`run/DATA_RESEARCH.md` 中，**8 个主题全部有结论**（含"未找到"这类结论），
且每条关键结论都能顺着 URL 复核；**综合建议**段落给出可执行的下一步。

---


## 1. 任务目标

把已在盘上的原始语料，变成**训练可直接消费、配比正确、且不污染评测集**的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math / **EDA**）
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
- `cxmt/`（EDA / 电路相关标注与 benchmark —— phase3 领域排查时可查）

> 对数据 agent 的影响：phase0 已盘点的主路径（`/nas_inference/openbmb`、`/nas_train/datasets/mvp-lab`）正确；
> 但 phase0 尚未覆盖 `②` 里的 Ultra-FineWeb 基础版（`/nas_train/.../openbmb`）、`③ stanford-vision-lab/gpic`、`④ /nas_user` 整块 —— 后续 phase 复核时把这些补齐进 DATA_LEDGER。

---

## 2. 阶段与推荐执行顺序

```
推荐顺序： 【🎯 当前】R（调研，见 §0） → phase0 inventory ✅ → phase5 isolation ✅ → phase1 validate → phase2 text → phase3 domain → phase4 mm → phase6 handoff
```

> **为什么 phase5（污染隔离）排在最前**：它必须在**任何"训练可消费产物"产出之前**就位。
> 如果先切了数据再立闸，已经切好的数据要全部重扫、甚至重切——**白做一遍**。

| 阶段 | 做什么 | 完成判据 |
|:---|:---|:---|
| **R** `research` 🎯 **当前主攻** | 用 `cimi-search` / `cimi-fetch` 为 **5 个阶段**做数据调研（详见 **§0**） | `DATA_RESEARCH.md`：8 个主题全部有结论 |
| **phase0** `inventory` ✅ | 对 `/nas_inference` 与 `/nas_train` 上每条数据线**实测**：文件数、总字节、目录结构、抽样看格式；确认哪些路径真实存在 | `DATA_LEDGER.md` 初版；**与方案 §1 的差异逐条列出** |
| **phase5** `isolation` | 建 EDA-Eval-PyAether 的黑名单指纹 + 训练集侧扫描脚本 + SFT 同闸 | `CONTAMINATION_CHECK.md` 初版 + 可复用脚本 |
| **phase1** `validate` | 下载完整性（parquet 全量可开 / tar 可解 / shard 无缺号）；损坏清单 | 损坏/缺失清单 + 校验命令 |
| **phase2** `text` | 通用文本分词打包成 `.bin/.idx`（stable 主体 + 退火源），**复用 Round 1 脚本** | 训练实测能加载并跑 10 步冒烟 |
| **phase3** `domain` | EDA 领域语料**排查**（有哪些、在哪、能否导出/授权）→ 确认后入库并过闸 | 来源清单 + 实际入库量（**查不到就是结论，不要造数据**） |
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
| **`run/DATA_RESEARCH.md`** | 🎯 **调研报告（当前主攻）**：8 个主题的数据源调研，每条含 URL / 规模 / 许可 / 可得性 / 优先级 |
| `run/DATA_LEDGER.md` | **数据清单**（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | **污染隔离报告**（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 **`DATA_RESEARCH.md`（调研报告，当前主攻）** —— 8 个主题全部有结论，每条关键结论可顺 URL 复核
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

