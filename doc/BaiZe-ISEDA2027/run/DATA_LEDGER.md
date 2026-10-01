# DATA_LEDGER.md — BaiZe 数据清单（核心产出，随 phase 推进持续更新）

> 版本 v0 · 2026-10-01 · 生成自 **phase0_inventory**（首次实测盘点）。
> ⚠️ 本清单**一律以实测为准**；与方案 `BAIZE_DATA_PREP_PLAN.html` §1 的差异在 §2 逐条列出。
> 产物绝对路径 + 规模 + 校验和在此登记，训练侧据此取用；`.bin/.idx`/tar/原始集**不入 git**。

---

## 0. 五条数据线总览（实测状态）

| 线 | 数据集 | 实测规模 | 状态 | 用途 |
|:---|:---|:---|:---|:---|
| 通用文本·主体 | Ultra-FineWeb-L3 (EN) qa | **616 个 parquet / 617.6 GiB** | ✅ 已下载 | Stage(i) 预训练主体 |
| 通用文本·退火 | UltraData-Code | **1121 个 parquet**（L2/L3 × 多语言） | ✅ 已下载 | 退火 code |
| 通用文本·退火 | UltraData-Math | **1823 个 parquet**（L1 CC-MAIN shard） | ✅ 已下载 | 退火 math |
| 通用文本·SFT | UltraData-SFT-2605 / -Agent-2609 | parquet=0（**疑似 jsonl 格式**，待 phase1 补查） | ✅ 已下载 | Stage(ii) SFT |
| 通用多模态 | LLaVA-OneVision-1.5 Mid-85M | EN **5545** + CN **1512** parquet（下载中） | 🟠 下载中 | 视觉编码器 + MLLM 对齐 |
| 通用多模态·已派生 | baize-vision/en500k | 25 tar / **68.59 GiB** | ✅ 已就绪 | Stage(iii) 四架构对比（完成） |
| 通用多模态·已派生 | baize-vision/eval5k | 1 tar / **1.27 GiB**（laioncn/EN） | ✅ 已就绪 | 检索代理评估（held-out） |
| **领域（EDA）** | PyAether/SKILL API 文档、EDA 工具文档、开源 HDL | **未实测（来源未落实）** | ❌ 待获取 | Stage(ii) 领域退火 + SFT（最关键） |
| **红线** | EDA-Eval-PyAether 评测集 | **158 任务**（v20260311.jsonl, 486 KB） | 🔒 只读隔离 | 建黑名单（见 CONTAMINATION_CHECK.md） |

---

## 1. 数据线明细（实测路径）

### 1.1 通用文本（只读源 `/nas_inference`）

| 数据集 | 绝对路径 | 实测 | 备注 |
|:---|:---|:---|:---|
| Ultra-FineWeb-L3 (EN) | `/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | 616 × `part-*.snappy.parquet`（各 ~1.07 GB），共 617.6 GiB | 内容列 `content`；snappy 压缩 |
| UltraData-Code | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/` | 1121 parquet；`L2/`(cpp,cs,go,java,js,php,py,r,rb,rust,sh) + `L3/`(+rs) | 退火源用 L3（Round 1 用 `--mode turns` 读 `texts` 列） |
| UltraData-Math | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/` | 1823 parquet；`L1/<CC-MAIN-*>` shard 结构 | 退火源 |
| UltraData-SFT-2605 | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605/data/` | parquet=0；子目录 `no_think/Chinese-general`、`no_think/Code`… | 疑似 jsonl，phase1 补查 |
| UltraData-SFT-Agent-2609 | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609/data/` | parquet=0；`Code_Agent/General_Agent/Search_Agent/Tool_Use` | 疑似 jsonl，phase1 补查 |

### 1.2 通用多模态（产出来源 `/nas_train`）

| 数据集 | 绝对路径 | 实测 | 备注 |
|:---|:---|:---|:---|
| LLaVA-OneVision-1.5 Mid-85M | `/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/` | 见下表 | 下载中 >50% |
| baize-vision/en500k | `/nas_train/app.e0031982/datasets/baize-vision/en500k/` | 25 tar（`shard-00000..00024`）/ 68.59 GiB | imagenet/EN，Round1 已派生 |
| baize-vision/eval5k | `/nas_train/app.e0031982/datasets/baize-vision/eval5k/` | 1 tar / 1.27 GiB | laioncn/EN held-out |

**LLaVA 85M 子集 parquet 计数（实测，下载进行中）：**

| 子集 | EN | CN |
|:---|---:|---:|
| imagenet | 50 | 32 |
| laioncn | 430 | 132 |
| datacomp1b | 439 | 136 |
| coyo | 1504 | **0（无 CN）** |
| mint | 553 | 152 |
| obelics | 2569 | 1060 |
| **合计** | **5545** | **1512** |

### 1.3 评测集（只读，红线，绝不写入训练集）

- **权威集（158 任务）**：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 行 / 486 KB）
  - 每任务字段：`task_id` / `prompt` / `entry_point` / `test` / `metadata`（task_name, source, scenario, category, num_unique_apis, techlib_dependency, lines_of_code）。
  - ⚠️ **差异**：任务书提到 `canonical_solution` 字段，但本版本 jsonl **无该字段**（只有 prompt/entry_point/test）。
- **同目录其他快照（也属评测内容，一并视为禁入）**：`EDA-Eval-PyAether-148.jsonl`(148)、`-46.jsonl`(46)、`-Updated102.jsonl`(102)、`-TEST.jsonl`(1)、`cuhk_benchmark_cxmt_format.jsonl`(80)。
  - 处置：黑名单主集用 v20260311(158)，其余快照 phase1 时核对去重关系后纳入同一黑名单体系。

---

## 2. 与方案 §1 的差异（逐条）

| # | 方案 §1 记录 | 实测 | 结论 |
|:---|:---|:---|:---|
| D1 | Ultra-FineWeb-L3 qa "1.8T tok" | **616 文件 / 617.6 GiB**（token 需分词后统计；Round 1 记忆写"31+ part 文件"与实测不符） | 文件数 >19×，以 616 为准；token 数 phase2 后补报 |
| D2 | "UltraData-SFT-Agent" | 实际目录 `UltraData-SFT-Agent-2609`，且另有 `UltraData-SFT-2605`（方案未列） | 方案漏列 2605，名称带版本后缀 |
| D3 | UltraData-Code / Math 路径仅写 `.../openbmb/` | Code 分 L2/L3、Math 分 L1 等多个子层 | 路径需下钻到具体 level |
| D4 | LLaVA-OneVision "…× EN/CN" | **coyo 只有 EN（无 CN）**；各子集 EN/CN 数量不等 | "× EN/CN" 不适用于 coyo |
| D5 | 多模态 "下载中 >50%" | 实测 EN 5545 / CN 1512 parquet | 与"过半"大致一致，phase4 前重测确认完成 |
| D6 | 领域（EDA）"来源未落实" | 未变；`eda_fastmcp` 代码库存在（`/nas_train/app.e0031982/code/eda_fastmcp`），API 知识库能否导出纯文本待 phase3 查证 | 待 phase3 |
| D7 | 已有派生数据 `BASE_DIR/data/ultrafineweb_l3_qa` | 确认在 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/`（**非** super_intelligence_2035 仓库） | `BASE_DIR` = `code/BaiZe-ISEDA2027`（训练仓库），与文档 git 仓库分离 |

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
| 黑名单指纹 + 校验脚本 | `run/data_pipeline/`（已建 ✅） | ✅ v0 |
| 通用文本 stable 主体 `.bin/.idx` | `/nas_train/app.e0031982/datasets/baize-data/text/`（规划） | ⬜ phase2 |
| 退火源 `.bin/.idx`（code/math/EDA） | 同上 | ⬜ phase2/3 |
| 多模态训练 webdataset | `/nas_train/app.e0031982/datasets/baize-data/mm/`（规划） | ⬜ phase4 |
| 多模态 held-out 评估集 | 同上 | ⬜ phase4 |
| 结果 HTML | `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html` | ⬜ phase6 |