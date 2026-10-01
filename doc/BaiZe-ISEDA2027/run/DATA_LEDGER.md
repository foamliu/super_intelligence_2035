# DATA_LEDGER.md — BaiZe 数据清单（核心产出，随 phase 推进持续更新）

> 版本 v0 · 2026-10-01 · 生成自 **phase0_inventory**（首次实测盘点）。
> ⚠️ 本清单**一律以实测为准**；与方案 `BAIZE_DATA_PREP_PLAN.html` §1 的差异在 §2 逐条列出。
> 产物绝对路径 + 规模 + 校验和在此登记，训练侧据此取用；`.bin/.idx`/tar/原始集**不入 git**。

---

## 0. 五条数据线总览（实测状态）

| 线 | 数据集 | 实测规模 | 状态 | 用途 |
|:---|:---|:---|:---|:---|
| 通用文本·主体 | Ultra-FineWeb（base） | **2.99 TB / 2.72 TiB = 1,290,261,453 行**（en 1,159,254,991 + zh 131,006,462），≈**1.12T token** | 🟠 **下载中**（R2 本轮启动） | **Stage(i) 预训练主体（R2 改判：base 替 L3 做主体）** |
| 通用文本·退火/decay | Ultra-FineWeb-L3 | **1764 parquet / 1.9 TB**，≈**690B token** | ✅ 已下全 | 退火/decay 档（合成 Q&A，README 明为 base 派生） |
| 通用文本·退火 | UltraData-Code | **1121 parquet / 1.22 TB**，≈**411B token**（L2 355B + L3 56B） | ✅ 已下载 | 退火 code |
| 通用文本·退火 | UltraData-Math | **1823 parquet / 552 GB**，≈**303B token**（L1 184B + L2p 32B + L3 87B） | ✅ 已下载 | 退火 math |
| 通用文本·SFT | UltraData-SFT-2605 / -Agent-2609 | **2605 空/需重下**；Agent-2609=jsonl 50shard/51GiB | 🟠 部分就绪 | Stage(ii) SFT |
| 通用多模态 | LLaVA-OneVision-1.5 Mid-85M | EN **5601** + CN **1948** parquet（7549，下载中，sa1b/zero250m 未下） | 🟠 下载中 | 视觉编码器 + MLLM 对齐 |
| 通用多模态·已派生 | baize-vision/en500k | 25 tar / **68.59 GiB** | ✅ 已就绪 | Stage(iii) 四架构对比（完成） |
| 通用多模态·已派生 | baize-vision/eval5k | 1 tar / **1.27 GiB**（laioncn/EN） | ✅ 已就绪 | 检索代理评估（held-out） |
| **领域（EDA）** | PyAether/SKILL API 参考文档（`eda_fastmcp/docs/`）、EDA 工具文档、开源 HDL | **已确认来源 ≈45MB 纯文本**（API 参考文档） | 🟡 待授权确认 + 待入库 | Stage(ii) 领域退火 + SFT（最关键） |
| **红线** | EDA-Eval-PyAether 评测集 | **158 任务**（v20260311.jsonl, 486 KB） | 🔒 只读隔离 | 建黑名单（见 CONTAMINATION_CHECK.md） |

---

## 1. 数据线明细（实测路径）

### 1.1 通用文本（只读源 `/nas_inference`）

| 数据集 | 绝对路径 | 实测 | 备注 |
|:---|:---|:---|:---|
| Ultra-FineWeb-L3 (EN) | `/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | 616 × `part-*.snappy.parquet`（各 ~1.07 GB），共 617.6 GiB | 内容列 `content`；snappy 压缩 |
| UltraData-Code | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/` | 1121 parquet；`L2/`(cpp,cs,go,java,js,php,py,r,rb,rust,sh) + `L3/`(+rs) | 退火源用 L3（Round 1 用 `--mode turns` 读 `texts` 列） |
| UltraData-Math | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/` | 1823 parquet；`L1/<CC-MAIN-*>` shard 结构 | 退火源 |
| Ultra-FineWeb（base） | `/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb/` | **R2 下载中**（≤2.99 TB / 64,624 parquet，en 2048 + zh ~62,576；列 `content/score/source`） | **P-8 主预训练主体（R2 改判）** |
| UltraX-Preview | `/nas_inference/app.e0031982/datasets/openbmb/UltraX-Preview/`（未下） | HF 113,789,578 行 / 487 GB / 479 parquet，5 config，~100B token | 备选（与 base 重叠，≤200B 不下载） |
| UltraData-RL-2609 | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-RL-2609/`（未下） | HF 20 jsonl / 187.63 GB，4 config（Math default/Knowledge/Long-Context/Code） | Stage(v) RL 用，P-8 不需要 |
| UltraData-SFT-2605 | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605/data/` | **落盘为空**：总 152K，仅 README+LICENSE；`no_think/Chinese-general`、`no_think/Code` 目录空；179 个 `.lock` 缓存 | ❌ 未下载完整，需重下（新数据缺口） |
| UltraData-SFT-Agent-2609 | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609/data/` | **jsonl，50 shard / 51 GiB**；`Code_Agent`(7)/`General_Agent`/`Search_Agent`/`Tool_Use`，2GB/shard | ✅ 已就绪（jsonl，check_contamination.py 直接可扫） |

### 1.2 通用多模态（产出来源 `/nas_train`）

| 数据集 | 绝对路径 | 实测 | 备注 |
|:---|:---|:---|:---|
| LLaVA-OneVision-1.5 Mid-85M | `/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/` | 见下表 | 下载中 >50% |
| baize-vision/en500k | `/nas_train/app.e0031982/datasets/baize-vision/en500k/` | 25 tar（`shard-00000..00024`）/ 68.59 GiB | imagenet/EN，Round1 已派生 |
| baize-vision/eval5k | `/nas_train/app.e0031982/datasets/baize-vision/eval5k/` | 1 tar / 1.27 GiB | laioncn/EN held-out |

**LLaVA 85M 子集 parquet 计数（实测，2026-10-01 下载进行中，数字仍增长）：**

| 子集 | EN | CN | 备注 |
|:---|---:|---:|:---|
| imagenet | 50 | 32 | |
| laioncn | 430 | 132 | |
| datacomp1b | 439 | 136 | |
| coyo | 1504 | **436** | ⚠️ 中文在 **`Language-CN`**（非 `CN`）子目录 |
| mint | 553 | 152 | |
| obelics | 2625 | 1060 | EN 较 phase0(2569) +56（仍在增） |
| **合计** | **5601** | **1948** | 总数 ≈7549（下载中） |

> **目录命名注意**（=D8）：六子集除 coyo 外，中文目录统一叫 `CN`；**coyo 的中文目录叫 `Language-CN`**。
> phase4 打包与 inventory 计数必须**同时覆盖 `CN` 与 `Language-CN`**。

### 1.3 评测集（只读，红线，绝不写入训练集）

- **权威集（158 任务）**：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 行 / 486 KB）
  - 每任务字段：`task_id` / `prompt` / `entry_point` / `test` / `metadata`（task_name, source, scenario, category, num_unique_apis, techlib_dependency, lines_of_code）。
  - ⚠️ **差异**：任务书提到 `canonical_solution` 字段，但本版本 jsonl **无该字段**（只有 prompt/entry_point/test）。
- **同目录其他快照（也属评测内容，一并视为禁入）**：`EDA-Eval-PyAether-148.jsonl`(148)、`-46.jsonl`(46)、`-Updated102.jsonl`(102)、`-TEST.jsonl`(2)、`cuhk_benchmark_cxmt_format.jsonl`(80)。
  - 关系（实测）：`148 = 46 ∪ Updated102`；`148` 与 `v20260311` task_id 0 重叠、但 entry_point 重叠 144/148（早期快照/旧格式）；`TEST`(2) 是 v20260311 子集；`cuhk`(80) 是独立 CUHK/CXMT 学术基准（仅 prompt，无 entry_point/test）。
  - 处置：**已全部纳入同一并集黑名单**（536 任务 / 191,718 去重 13-gram，见 CONTAMINATION_CHECK.md v0.1）。

---

## 2. 与方案 §1 的差异（逐条）

| # | 方案 §1 记录 | 实测 | 结论 |
|:---|:---|:---|:---|
| D1 | Ultra-FineWeb-L3 qa "1.8T tok" | **616 文件 / 617.6 GiB**（token 需分词后统计；Round 1 记忆写"31+ part 文件"与实测不符） | 文件数 >19×，以 616 为准；token 数 phase2 后补报 |
| D2 | "UltraData-SFT-Agent" | 实际目录 `UltraData-SFT-Agent-2609`，且另有 `UltraData-SFT-2605`（方案未列） | 方案漏列 2605，名称带版本后缀 |
| D3 | UltraData-Code / Math 路径仅写 `.../openbmb/` | Code 分 L2/L3、Math 分 L1 等多个子层 | 路径需下钻到具体 level |
| D4 | LLaVA-OneVision "…× EN/CN" | 各子集 EN/CN 数量不等；coyo 的**中文目录叫 `Language-CN`**（非 `CN`），其余用 `CN`（见 D8） | "× EN/CN" 不严格适用于 coyo 的目录命名 |
| D5 | 多模态 "下载中 >50%" | 实测 EN 5571 / CN 1512 + coyo `Language-CN` 436 ≈ CN 1948（总数 ≈7519，仍增长） | 与"过半"大致一致，phase4 前重测确认完成 |
| D6 | 领域（EDA）"来源未落实" | **已突破**：`eda_fastmcp/docs/` 已含 API 参考文档纯文本（pyAether_API_Docstring.md 144K、skill_data/*.md ≈8MB、API_INFO_MERGED_V3.json 18M/8464 条、innovus 6.8M 等，合计 ≈45MB）；导出纯文本**可行**，待授权确认后入库 | phase3 已确认来源 ✅ |
| D7 | 已有派生数据 `BASE_DIR/data/ultrafineweb_l3_qa` | 确认在 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/`（**非** super_intelligence_2035 仓库） | `BASE_DIR` = `code/BaiZe-ISEDA2027`（训练仓库），与文档 git 仓库分离 |
| D8 | （新增发现）LLaVA 子集目录命名 | coyo 中文 = `coyo/Language-CN`（436 parquet），其余子集中文 = `<s>/CN` | phase0 计数把 coyo CN 误记为 0；已修正，inventory.sh 同步覆盖 Language-CN |
| D9 | （R2 改判）Stage(i) 主体用 L3 | **R2 判定改用 `Ultra-FineWeb` base 做主体**（L3 是 base 的 Q&A/多风格合成改写，重叠≈0；base = +1.12T 原始 web）；退火仍 Code+Math 86:10:4 | P-8 三档 44B/100B/200B = base-en(86):code(10):math(4)，见 DATA_RESEARCH.md R2-C |
| D10 | （R2 实测补）token 估算 | Code ≈411B、Math ≈303B、L3 ≈690B、base ≈1.12T（均抽样外推，正式值以 phase2 `.bin` 分词为准） | 之前 LEDGER 只记字节不记 token，本轮补齐 |

---

## 3. Round 1 复用资产（phase2 照抄，不另起炉灶）

| 资产 | 绝对路径 | 说明 |
|:---|:---|:---|
| 分词脚本 | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py` | 读 `content` / `texts`(`--mode turns`) 列 → DeepSeek tokenize → `.bin/.idx/.json` |
| tokenizer | 源 `/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash`；EOD 副本 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod` | vocab 129281 / pad 129408 / eod 129280 |
| 已切产物 | `.../code/BaiZe-ISEDA2027/data/ultrafineweb_l3_qa`(.bin 659MB) | 200k docs / 165M token |
| 已切产物 | `.../data/ultrafineweb_l3_qa_700m`(.bin 2.97GB) | 900k docs / 742M token |
| 退火产物 | `.../data/anneal_code`(90M tok)、`anneal_math`(8.5M)、`anneal_math2` | code/math `.bin/.idx` |
| launcher | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/pretrain_launcher.py` | 直接喂 `.bin/.idx` 前缀 |
| webdataset 打包 | `/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/prep_data.py` | LLaVA parquet → tar |

---

## 4. 本任务产物规划（落盘 NFS，不入 git）

| 产物 | 目标路径 | 状态 |
|:---|:---|:---|
| 黑名单指纹 + 校验/打包脚本 | `run/data_pipeline/`（build_blacklist + check_contamination + inventory + **validate_data.py** 校验 + **preprocess_text.sh** 分词打包） | ✅ v0.2 + 校验/打包脚本新补齐 |
| 通用文本 stable 主体 `.bin/.idx` | `/nas_train/app.e0031982/datasets/baize-data/text/`（规划） | ⬜ phase2 |
| 退火源 `.bin/.idx`（code/math/EDA） | 同上 | ⬜ phase2/3 |
| 多模态训练 webdataset | `/nas_train/app.e0031982/datasets/baize-data/mm/`（规划） | ⬜ phase4 |
| 多模态 held-out 评估集 | 同上 | ⬜ phase4 |
| 结果 HTML | `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html` | ⬜ phase6 |

---

## 5. EDA 领域语料（phase3 排查结果，2026-10-01）

> ⚠️ **🚫 本线（phase3_domain）已被运维正式取消**（2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义，故不再调研/入库。下表保留仅为**留证**（说明当时排查过、且这批 API 参考文档**已确认不入库**）。**红线不变**：`EDA-Eval-PyAether` 158 任务的 prompt/函数名/参考解/断言及其改写版仍禁止进入任何训练集。

**结论：EDA 领域"来源材料"已在盘上，且本就是纯文本**——`eda_fastmcp` 项目自带的 API 参考文档，导出为纯文本文档**可行**（本就是 md/json）。

| 来源 | 绝对路径 | 规模 | 性质 | 可否入训练集 |
|:---|:---|:---|:---|:---|
| PyAether API docstring | `/nas_train/app.e0031982/code/eda_fastmcp/docs/pyAether_API_Docstring.md` | 144 KB | 函数签名 + 说明 | ✅ API 参考（来源材料） |
| PyAether 设计文档 | `.../docs/emyDesign.md` | 16 KB | emyDesign 说明 | ✅ |
| SKILL 参考（9 篇） | `.../docs/skill_data/*.md` | ≈8 MB | SKILL 语言/布局/DF 等参考 | ✅ API 参考 |
| API 结构化索引 | `.../docs/api_functions.jsonl` / `api_classes.jsonl` / `api_methods.jsonl` | 3.5M / 2.2M / 2.3M | 结构化 API 清单 | ✅ |
| API 全文合并 | `.../docs/API_INFO_MERGED_V3.json` | 18 MB（8464 条 api_descriptions） | 在线向量库主源 | ✅ |
| 其他 EDA 工具 API | `.../docs/innovus_API_INFO.json`(6.8M) / `wv_ace_API_INFO.json`(224K) | — | Innovus / WV-ACE API | ✅（授权待确认） |
| 向量库 `kb/` | `.../kb/chroma_db_v3_full` 等 | — | ChromaDB 检索索引 | 可追溯回 docs 的 JSON 源 |

**关键区分（红线）**：
- ✅ **允许**：上表 API 参考文档（函数签名、参数说明、示例）——它是评测任务的"来源材料"。
- ❌ **禁止**：评测任务的 `prompt` / `entry_point` / `test` 断言及其改写版——这些在 `pyAether-eval/original_dataset/*.jsonl`，已全部纳入黑名单。

**phase3 待办**：
- [ ] 授权确认：`eda_fastmcp` 是 ZhuLong 内部项目，其 API 参考文档**能否作为训练数据入库需负责人确认**（任务书 §4.3"待确认授权"）。
- [ ] 入库前逐片段过闸：API 文档与评测内容天然同源（评测 prompt 由 docstring 生成），正式入库前须用 `check_contamination.py` 逐片段（非整文件）扫描，剔除命中片段。
- [ ] 量级评估：≈45MB 纯文本对"退火"偏少（对 SFT 足够）；是否补开源 HDL 待定。
- 粗粒度预检：pyAether_API_Docstring / emyDesign / sklangref 整文件过闸 → **0 命中**（来源材料不含评测内容）。