# CONTAMINATION_CHECK.md — 污染隔离报告（红线留证）

> 版本 v0.3 · 2026-10-01 · phase5_isolation（**全评测快照并集立闸**，6 快照；**修复中文 prompt 指纹丢失 + 短文本 8-gram 兜底 + SFT 嵌套 jsonl 目录同闸扫描**）。
> 目标：确保 `EDA-Eval-PyAether` 的 158 任务内容（prompt / entry_point / test 断言，及改写版）
> **绝不进入任何训练集**（含 SFT 语料同闸 + 多模态 held-out 不同源）。违反则下游结论全部作废。

---

## 1. 规则（允许 vs 禁止）

| 内容 | 可否入训练集 |
|:---|:---|
| PyAether / SKILL 的 **API 参考文档**（函数签名、参数说明、示例） | ✅ 允许（任务的"来源材料"） |
| 评测任务的 **prompt**、**entry_point（函数名）**、**canonical_solution**、**test 断言** | ❌ 禁止 |
| 上述任务内容的 **改写 / paraphrasing 版** | ❌ 禁止（改写不洗白） |

- 字段判定：评测集 v20260311 每任务字段为 `prompt` / `entry_point` / `test` / `metadata`。
  - **纳入黑名单**：`prompt`、`entry_point`、`test`（`canonical_solution` 若存在同样纳入；本版本无该字段）。
  - **不纳入**：`metadata.source`（如 `pyAether.xxx`）——它是 API 来源名，属 API 参考文档侧（允许入训练集）。

## 2. 指纹方法（可复现）

- **归一化**（v0.2 修正）：`NFKC 兼容归一化` → 小写 → 把非 Unicode `\w`（非文字/数字/下划线）字符折叠为单个空格 → 去掉空格。
  - ⚠️ **v0.1 的 bug**：旧实现 `[^a-z0-9_]` 会把**所有非 ASCII 字符**（含 CJK 汉字）当空格丢弃，
    导致中文评测 prompt（cuhk 基准）完全丧失指纹——80 任务里 59 条被误判为"过短跳过"。
  - NFKC 先把 Kangxi 部首兼容字符（如 ⼀ U+2F00 → 一 U+4E00）映射回标准 CJK，再用 Unicode `\w` 保留全部文字。
  - 对纯 ASCII 英文文本（EDA-Eval-PyAether 158 任务）行为与旧版**一致，无回归**。
- **切分**：归一化文本的**字符级 13-gram**（shingle），每任务 = 一个 shingle 集合。
- **短文本兜底**（v0.2 新增）：主 13-gram 无法切分（文本 <13 字符）的任务，改切 **8-gram**；
  若仍不足 8 字符，则以整串为单 token（整串精确匹配）。
  用于覆盖中文短 prompt 及**嵌在长文档中的短串**（扫描侧总有 8-gram 覆盖）。
- **黑名单**：
  - `ngram_hashes.txt`：全量去重 13-gram 的 **FNV-1a 64-bit** 哈希集（精确命中集合）。
  - `short_ngram_hashes.txt`：短文本兜底 8-gram 的 FNV-1a 64-bit 哈希集。
  - `meta.json`：每任务 **MinHash(k=128, 双哈希 64-bit)** 签名（Jaccard 估计）；短任务另存 `minhash_short`。
  - `entry_points.sha256`：每任务 entry_point 的 sha256（函数名二次校验）。
- **可复现性**：哈希用确定性 FNV-1a（不依赖 `PYTHONHASHSEED`）；脚本 `run/data_pipeline/build_blacklist.py`。

## 3. 阈值（写明，论文可复现）

- **主命中判定**：某训练文档的 13-gram 集合与全局黑名单的**重合率 ≥ 0.80** → 标记为污染。
  - `重合率 = |doc_13grams ∩ 黑名单| / |doc_13grams|`
- **短文本命中判定**：文档的 8-gram 集合与 `short_ngram_hashes.txt` 的**重合数 ≥ 1** → 标记为污染
  （覆盖中文短 prompt 及嵌在长文档中的短串；这些短串经 NFKC 后高度唯一，≥1 命中即近重复）。
- **溯源**：被标记文档再与全部任务逐一算 **MinHash Jaccard**（主签名 + 短签名取较大者），取最高者为最可能撞源任务。
- 默认参数：`--ngram 13 --short-ngram 8 --threshold 0.8 --minhash-k 128`。

## 4. 黑名单产物（已生成，内容安全，无原始评测内容）

| 文件 | 大小 | 内容 |
|:---|:---|:---|
| `run/data_pipeline/blacklist/meta.json` | 2.1 MB | 536 任务 MinHash 签名 + 来源溯源（task_id 带快照文件名前缀） |
| `run/data_pipeline/blacklist/ngram_hashes.txt` | 3.3 MB | 193,295 个去重 13-gram 的 64-bit hex |
| `run/data_pipeline/blacklist/short_ngram_hashes.txt` | 170 B | 10 个去重 8-gram 的 64-bit hex（短文本兜底） |
| `run/data_pipeline/blacklist/entry_points.sha256` | 58.7 KB | entry_point 函数名 sha256（536 行） |

- 覆盖 **6 个评测快照**：`v20260311`(158) + `148`(148) + `46`(46) + `Updated102`(102) + `TEST`(2) + `cuhk`(80) = **536 任务**。
- 生成：`python run/data_pipeline/build_blacklist.py --eval-jsonl <jsonl1> <jsonl2> ... --out-dir run/data_pipeline/blacklist`（脚本多文件求**并集**）。
- 结果（v0.2）：536 任务 / 193,295 去重后 13-gram（较 v0.1 的 191,718 多了 1,577，全来自被修复的中文 cuhk 内容）；
  短文本兜底 4 任务 / 10 个 8-gram（`CUHK-PyAether-012/-037/-042/-052`，NFKC 后仍不足 13 字符）。

#### 快照去重关系（实测）

- `148 = 46 ∪ Updated102`（46 与 102 不相交，均为 148 子集；三者 task_id 互斥）。
- `148` 与 `v20260311(158)` 的 **task_id 0 重叠**，但 **entry_point 重叠 144/148** → 判定为**同一批任务的旧格式/早期快照**（扁平字段 vs 嵌套 metadata）。已全部纳入并集，安全冗余、无漏。
- `TEST`(2) 是 `v20260311` 的子集（2/2 重叠）；`cuhk`(80) 是独立学术基准（CUHK/CXMT，仅 `prompt` 无 `entry_point`/`test`）。

## 5. 实测扫描（phase5 冒烟）

| 测试 | 输入 | 扫描量 | 命中 | 结论 |
|:---|:---|:---|:---|:---|
| 负控 | L3 qa `part-00000`（通用 web 文本） | 1500 文档 | **0** | ✅ 通用文本不含评测内容 |
| 正控 | v20260311.jsonl 自身 | 158 任务 | **158**（重合率全 1.0） | ✅ 闸门 100% 抓住主评测集 |
| 正控 | `-46.jsonl` 自身（旧格式快照） | 46 任务 | **46**（全 1.0） | ✅ 并集黑名单覆盖旧格式快照 |
| 正控 | `148.jsonl` 自身 | 148 任务 | **148** | ✅ |
| 正控 | `Updated102.jsonl` 自身 | 102 任务 | **102** | ✅ |
| 正控 | `TEST.jsonl` 自身 | 2 任务 | **2** | ✅ |
| 正控 | `cuhk_benchmark`（仅 prompt，中文） | 80 任务 | **80**（v0.1 仅 21；76 经 13-gram + 4 经短 8-gram 兜底） | ✅ v0.2 修复中文指纹丢失 |
| 来源对照 | API 参考文档（pyAether_API_Docstring / emyDesign / sklangref） | 3 文件 | **0** | ✅ 来源材料不含评测内容（粗粒度） |
| SFT 同闸 | UltraData-SFT-Agent-2609 `Code_Agent_part-1-of-7.jsonl`（单文件，`messages` 字段） | 30 文档 | **0** | ✅ SFT jsonl + `messages` 多轮对话字段可扫（实测单文档 ≈40KB，短兜底 0） |
| SFT 同闸 | UltraData-SFT-Agent-2609 `data/Code_Agent/`（嵌套 jsonl **目录**） | 10 文档 | **0** | ✅ 目录输入递归收集 jsonl（旧版漏扫目录内 jsonl → 静默 0 文档，已修复） |
| **en_base 投料前扫描** | ultrafineweb_en part-0001-of-2048（通用 web 英文） | 2000 文档 | **0** | ✅ en_base 源无评测污染（唤醒244, 2026-10-09） |
| **en_base 投料前扫描** | ultrafineweb_en part-1000-of-2048（中段采样） | 2000 文档 | **0** | ✅ |
| **en_base 投料前扫描** | ultrafineweb_en part-2048-of-2048（末段采样） | 2000 文档 | **0** | ✅ |
| **l1_en_hq 投料前扫描** | ultrafineweb_l1_en_hq CC-MAIN-2025-30 part-0001-of-1000 | 2000 文档 | **0** | ✅ l1_en_hq 源无评测污染 |
| **zh 投料前扫描** | ultrafineweb_zh part-001-of-256（中文通用 web） | 2000 文档 | **0** | ✅ zh 源无评测污染（中文黑名单覆盖验证） |

> **投料前扫描小结（2026-10-09 唤醒244）**：5 个代表性源 parquet × 2000 docs = **10,000 docs**，覆盖 en_base（首/中/末）、l1_en_hq、zh 三个 config，**全部 0 命中**。与 phase5 负控（L3 qa 1500 docs 0 命中）一致 → Ultra-FineWeb 全系通用 web 文本与 EDA-Eval 评测集不同源。⚠️ 正式投料前需对**全量** 2048 en_base + 6000 l1_en_hq + 256 zh parquet 跑完整扫描（当前为代表性采样）。

- 命令：
  ```
  python run/data_pipeline/check_contamination.py --blacklist-dir run/data_pipeline/blacklist \
    --input <训练语料 glob> --ngram 13 --threshold 0.8 --out report.md
  ```

## 6. 处置流程（命中即执行）

1. 命中文档**剔除**（不进 `.bin/.idx` / webdataset / SFT），并记录 doc_idx + 撞源 task_id。
2. 改写版同样命中 → 同样剔除（改写不洗白）。
3. SFT 语料（Stage ii）走**同一套** `check_contamination.py`，不单独放行。
4. 多模态 held-out 评估集（如 eval5k）与训练集**不同源** + 跨集去重比对。

## 7. 状态与待办

- [x] 黑名单指纹生成脚本 + 扫描脚本 + 报告（phase5 v0 → v0.1 → v0.2）
- [x] 负控 / 正控冒烟验证（全 6 快照正控 100%、负控 0）
- [x] 全部 6 个评测快照（148/46/Updated102/TEST/cuhk）纳入同一并集黑名单
- [x] **中文 prompt 指纹丢失修复**（v0.2）：归一化改 `NFKC + Unicode \w`，cuhk 由 21→80 全覆盖
- [x] **短 prompt 覆盖**：NFKC 后仍 <13 字符的 4 条 cuhk prompt 走 **8-gram 兜底**（`short_ngram_hashes.txt`，10 哈希）
- [~] **en_base / l1_en_hq / zh 投料前采样扫描**（唤醒244, 2026-10-09）：5 parquet × 2000 docs = 10,000 docs, **0 命中** ✅；正式投料前需补全量扫描（2048+6000+256 parquet）
- [x] SFT 语料同闸机制修复 + 冒烟（唤醒 5）：check_contamination.py 目录分支现可递归扫描**嵌套 jsonl**（旧版只 glob parquet → 目录输入会静默扫 0 文档），并支持 Agent-2609 的 `messages`（list<{role,content}>）多轮对话字段；单文件 30 / 目录 10 文档均 **0 命中**、正控 158/158 无回归
- [ ] SFT 语料（UltraData-SFT-*）同闸**全量正式扫描**（phase2/3）：Agent-2609 已就绪可扫；2605 落盘为空需重下后再扫。⚠️ **性能**：Agent-2609 单文档 ≈40KB，纯 Python 逐 13-gram 哈希全量扫 51GiB 会很慢（2000 文档 >30s），正式扫需按 shard 并行 / 加速
- [ ] EDA API 参考文档正式入库前，逐片段（非整文件）跑同闸扫描，确保无评测内容泄漏