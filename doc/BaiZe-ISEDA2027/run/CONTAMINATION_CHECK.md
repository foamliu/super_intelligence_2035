# CONTAMINATION_CHECK.md — 污染隔离报告（红线留证）

> 版本 v0.1 · 2026-10-01 · phase5_isolation（**全评测快照并集立闸**，6 快照）。
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

- **归一化**：小写 → 把连续非 `[a-z0-9_]` 字符映射为单个空格 → 去掉空格。
- **切分**：归一化文本的**字符级 13-gram**（shingle），每任务 = 一个 shingle 集合。
- **黑名单**：
  - `ngram_hashes.txt`：全量去重 13-gram 的 **FNV-1a 64-bit** 哈希集（精确命中集合）。
  - `meta.json`：每任务 **MinHash(k=128, 双哈希 64-bit)** 签名（Jaccard 估计）。
  - `entry_points.sha256`：每任务 entry_point 的 sha256（函数名二次校验）。
- **可复现性**：哈希用确定性 FNV-1a（不依赖 `PYTHONHASHSEED`）；脚本 `run/data_pipeline/build_blacklist.py`。

## 3. 阈值（写明，论文可复现）

- **命中判定**：某训练文档的 13-gram 集合与全局黑名单的**重合率 ≥ 0.80** → 标记为污染。
  - `重合率 = |doc_13grams ∩ 黑名单| / |doc_13grams|`
- **溯源**：被标记文档再与 158 任务逐一算 **MinHash Jaccard**，取最高者为最可能撞源任务。
- 默认参数：`--ngram 13 --threshold 0.8 --minhash-k 128`。

## 4. 黑名单产物（已生成，内容安全，无原始评测内容）

| 文件 | 大小 | 内容 |
|:---|:---|:---|
| `run/data_pipeline/blacklist/meta.json` | 2.0 MB | 536 任务 MinHash 签名 + 来源溯源（task_id 带快照文件名前缀） |
| `run/data_pipeline/blacklist/ngram_hashes.txt` | 3.3 MB | 191,718 个去重 13-gram 的 64-bit hex |
| `run/data_pipeline/blacklist/entry_points.sha256` | 58.7 KB | entry_point 函数名 sha256（536 行） |

- 覆盖 **6 个评测快照**：`v20260311`(158) + `148`(148) + `46`(46) + `Updated102`(102) + `TEST`(2) + `cuhk`(80) = **536 任务**。
- 生成：`python run/data_pipeline/build_blacklist.py --eval-jsonl <jsonl1> <jsonl2> ... --out-dir run/data_pipeline/blacklist`（脚本已改为多文件求**并集**）。
- 结果：536 任务 / 191,718 去重后 13-gram（**去重前 = 去重后**，13-gram 级跨任务几乎无重叠）。

#### 快照去重关系（实测）

- `148 = 46 ∪ Updated102`（46 与 102 不相交，均为 148 子集；三者 task_id 互斥）。
- `148` 与 `v20260311(158)` 的 **task_id 0 重叠**，但 **entry_point 重叠 144/148** → 判定为**同一批任务的旧格式/早期快照**（扁平字段 vs 嵌套 metadata）。已全部纳入并集，安全冗余、无漏。
- `TEST`(2) 是 `v20260311` 的子集（2/2 重叠）；`cuhk`(80) 是独立学术基准（CUHK/CXMT，仅 `prompt` 无 `entry_point`/`test`）。

## 5. 实测扫描（phase5 冒烟）

| 测试 | 输入 | 扫描量 | 命中 | 结论 |
|:---|:---|:---|:---|:---|
| 负控 | L3 qa `part-00000`（通用 web 文本） | 1500 文档 | **0** | ✅ 通用文本不含评测内容 |
| 正控 | v20260311.jsonl 自身 | 158 任务 | **158**（重合率全 1.0） | ✅ 闸门 100% 抓住主评测集 |
| 正控 | `-46.jsonl` 自身（**新增快照**） | 46 任务 | **46**（全 1.0） | ✅ 并集黑名单覆盖旧格式快照 |
| 正控 | `cuhk_benchmark`（仅 prompt） | 80 任务 | **21**（59 过短跳过） | ⚠️ 短 prompt 限制见 §7 |
| 来源对照 | API 参考文档（pyAether_API_Docstring / emyDesign / sklangref） | 3 文件 | **0** | ✅ 来源材料不含评测内容（粗粒度） |

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

- [x] 黑名单指纹生成脚本 + 扫描脚本 + 报告（phase5 v0 → v0.1）
- [x] 负控 / 正控冒烟验证（含新增快照正控：-46 46/46、cuhk 21 命中 + 59 过短跳过）
- [x] 全部 6 个评测快照（148/46/Updated102/TEST/cuhk）纳入同一并集黑名单
- [ ] **短 prompt 覆盖**：cuhk 80 任务中 59 条 prompt 归一化后 <13 字符，13-gram 无法指纹（被跳过）；phase1 补 8-gram 或整串精确匹配兜底
- [ ] phase2 产出 `.bin/.idx` 前，对**全量训练文档**跑正式扫描并记录扫描量/命中
- [ ] SFT 语料（UltraData-SFT-*）同闸正式扫描（phase2/3，需先确认其 jsonl 结构）
- [ ] EDA API 参考文档正式入库前，逐片段（非整文件）跑同闸扫描，确保无评测内容泄漏