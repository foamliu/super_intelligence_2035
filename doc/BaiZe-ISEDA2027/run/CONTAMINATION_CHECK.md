# CONTAMINATION_CHECK.md — 污染隔离报告（红线留证）

> 版本 v0 · 2026-10-01 · phase5_isolation 初版。
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
| `run/data_pipeline/blacklist/meta.json` | 579 KB | 158 任务 MinHash 签名 + 元信息 |
| `run/data_pipeline/blacklist/ngram_hashes.txt` | 3.3 MB | 191,372 个去重 13-gram 的 64-bit hex |
| `run/data_pipeline/blacklist/entry_points.sha256` | 13.8 KB | entry_point 函数名 sha256 |

- 生成：`python run/data_pipeline/build_blacklist.py --eval-jsonl <v20260311.jsonl> --out-dir run/data_pipeline/blacklist`
- 结果：158 任务 / 191,372 去重前 shingle（去重后相同，说明 13-gram 级几乎无跨任务重叠）。

## 5. 实测扫描（phase5 冒烟）

| 测试 | 输入 | 扫描量 | 命中 | 结论 |
|:---|:---|:---|:---|:---|
| 负控 | L3 qa `part-00000`（通用 web 文本） | 1500 文档 | **0** | ✅ 通用文本不含评测内容 |
| 正控 | v20260311.jsonl 自身（当作训练输入） | 158 任务 | **158**（重合率全 1.0） | ✅ 闸门能 100% 抓住评测内容 |

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

- [x] 黑名单指纹生成脚本 + 扫描脚本 + 初版本报告（phase5 v0）
- [x] 负控 / 正控冒烟验证
- [ ] 其余评测快照（148/46/Updated102/TEST）纳入同一黑名单（phase1 核对去重关系后）
- [ ] phase2 产出 `.bin/.idx` 前，对**全量训练文档**跑正式扫描并记录扫描量/命中
- [ ] SFT 语料（UltraData-SFT-*）同闸正式扫描（phase2/3，需先确认其 jsonl 结构）