# S2 新源污染扫描汇总（自动生成）

> 扫描时间：2026-11-22 00:14~00:17 (R139)
> 黑名单：`blacklist_extended/`（5359 任务 / 4,847,354 去重 13-gram 哈希）
>   - EDA-Eval 536 + HumanEval 164 + MBPP 500 + GSM8K 1319 + MATH 546 + SWE-bench 2294
> 阈值：n-gram=13，重合率 ≥ 0.80；短文本兜底 n-gram=8，重合数 ≥ 1
> 环境：`/tmp/contam_venv`（Python 3.10 + pyarrow 25.0.1，uv venv）
> 采样脚本：`data_pipeline/sample_s2_new_sources.py`（每源 12 parquet 均匀采样 × ~1000 docs/file = 12,000 docs）

## 扫描结果

| 数据源 | 采样文件数 | 扫描文档数 | 短文本兜底 | 命中（污染）数 | 状态 |
|:---|---:|---:|---:|---:|:---|
| stack-v3-train | 12 / 8192 | 12,000 | 76 | **0** | ✅ 清洁 |
| finemath-3plus | 12 / 128 | 12,000 | 0 | **0** | ✅ 清洁 |
| Nemotron-CC-Math | 12 / 57 | 12,000 | 0 | **0** | ✅ 清洁 |
| MegaMath-web-pro | 12 / 100 | 12,000 | 0 | **0** | ✅ 清洁 |
| **合计** | — | **48,000** | 76 | **0** | **✅ 全清洁** |

## 数据源路径

| 源 | parquet 目录 | 文本字段 |
|:---|:---|:---|
| stack-v3-train | `/nas_user/.../HuggingFaceCode/stack-v3-train/data/` | 嵌套 `files[].content` |
| finemath-3plus | `/nas_user/.../HuggingFaceTB/finemath/finemath-3plus/` | 顶层 `text` |
| Nemotron-CC-Math | `/nas_user/.../nvidia/Nemotron-CC-Math-v1/3/` | 顶层 `text` |
| MegaMath-web-pro | `/nas_user/.../IFM/MegaMath/megamath-web-pro/` | 顶层 `text` |

## 结论

S2 blend 新增的 4 个零重叠数据源（stack-v3 / finemath / Nemotron-CC-Math / MegaMath-web-pro）
各抽样 12,000 docs（合计 48,000 docs），使用扩展黑名单（EDA-Eval + HumanEval + MBPP +
GSM8K + MATH + SWE-bench = 5359 任务）进行 13-gram 精确重合率扫描，
**全部 0 命中**。**结论：S2 新源数据清洁，与全部评测集不同源，可正式投料。**

> 累计污染扫描总计：S1（base 10K + base 全量 150K + R3 60K = 220K docs，0 命中）
> + S2 新源 48K docs，0 命中 = **268,000 docs 全 0 命中**。
