# DATA_MAPPING.md — BaiZe 训练数据「下载 ↔ 分词」映射表（单一事实源）

> 维护规程（运维令 2026-10-25 17:5x）：本文件为 Markdown 单一事实源；HTML 报告按需由 `gen_tokenized_inventory_report.py` 渲染。
> 一行 = 一个下载目录（粒度以盘上 `ls` 实测为准）；`状态` 取值：`镜像完整` / `分词中` / `未分词` / `未映射` / `已废弃` / `已删除`。
> 合计行由脚本求和，禁手填。数字均来自实测（`du -sb` / `find | wc -l` / `.json num_tokens`）。
> 生成时间：2026-10-25 18:2x（首次建立；映射主体来自 `tokenized/INDEX.tsv`，已删除节来自运维令 18:2x）。

---

## A. 当前可用映射（下载目录 ↔ 分词镜像）

> 来源：`/nas_train/app.e0031982/datasets/baize-data/tokenized/INDEX.tsv`（2026-10-25 14:54 build_tokenized_mirror.py 产出，triplet+inode ALL OK）。

| # | 下载目录 | 分词目录 | .bin | .idx | .json | 字节(B) | GB | tokens(B) | 状态 | 校验时间 | 证据 |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 1 | `…/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4` | `tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4` | 110 | 110 | 110 | 8,929,852,999,497 | 8930 | 2,238,140,710,284 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv triplet=OK inode_ok=110 |
| 2 | `…/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | `tokenized/Ultra-FineWeb-L3/ultrafineweb_en_l3/qa` | 154 | 154 | 154 | 1,062,000,123,988 | 1062 | 263,899,449,229 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv triplet=OK inode_ok=154 |
| 3 | `…/openbmb/UltraData-Code/data/UltraData-Code-L2` | `tokenized/UltraData-Code/UltraData-Code-L2` | 141 | 141 | 141 | 1,691,139,314,855 | 1691 | 421,450,419,455 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv triplet=OK inode_ok=141 |
| 4 | `…/openbmb/UltraData-Code/data/UltraData-Code-L3` | `tokenized/UltraData-Code/UltraData-Code-L3` | 63 | 63 | 63 | 516,117,199,509 | 516 | 128,623,266,591 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv triplet=OK inode_ok=63 |
| 5 | `…/openbmb/UltraData-Math/data/UltraData-Math-L1` | `tokenized/UltraData-Math/UltraData-Math-L1` | 149 | 149 | 149 | 659,469,460,275 | 659 | 164,437,183,984 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv triplet=OK inode_ok=149 |
| 6 | `…/openbmb/UltraData-Math/data/UltraData-Math-L3` | `tokenized/UltraData-Math/UltraData-Math-L3` | 67 | 67 | 67 | 313,425,604,823 | 313 | 77,949,162,709 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv triplet=OK inode_ok=67 |
| 7 | `…/openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq` | `tokenized/Ultra-FineWeb/ultrafineweb_l1_en_hq` | 32 | 32 | 32 | 192,910,037,902 | 193 | 47,988,834,942 | 分词中 | 2026-10-25 14:54 | 131 目标分词进行中 |
| 8 | `…/openbmb/Ultra-FineWeb/data/ultrafineweb_en` | `tokenized/Ultra-FineWeb/ultrafineweb_en` | 0 | 0 | 0 | 0 | 0 | 0 | 分词中 | 2026-10-25 14:54 | 131 目标分词进行中(done=92/131@17:23) |
| 9 | `…/openbmb/Ultra-FineWeb/data/ultrafineweb_zh` | `tokenized/Ultra-FineWeb/ultrafineweb_zh` | 0 | 0 | 0 | 0 | 0 | 0 | 分词中 | 2026-10-25 14:54 | 131 目标分词进行中 |
| 10 | `…/openbmb/UltraX-Preview/data/UltraX-AICC` | `tokenized/UltraX-Preview/UltraX-AICC` | 0 | 0 | 0 | 0 | 0 | 0 | 分词中 | 2026-10-25 14:54 | 131 目标分词进行中 |
| **合计** | | | **716** | **716** | **716** | **13,364,914,740,849** | **13365** | **3,342,489,027,194** | | | 误差 0 |

核对式：`sum(.bin)=716 = sum(.idx)=716 = sum(.json)=716`；`sum(bytes)=13,364,914,740,849`；`sum(tokens)=3,342,489,027,194`。

> 注：`env14_*` 真身在 `/nas_train/.../baize-data/text/`（与 `tokenized/` 同盘 ⇒ hardlink）；`full_*` 真身在 `/nas_env/app.e0031982/baize-data/`（跨盘 ⇒ symlink）。两者均属「下载的一律保留」，未删未改未移。

---

## B. 已删除 / 不可用（运维令 2026-10-25 18:2x · 用户直令 · 终裁）

> 用户口径：不能被本表 A 节收录的数据即不可用，留着只占盘。本节为终裁，删完即结案，不再挂账。
> 明细：`run/data/deleted_unmapped32_20261025.tsv`（32 行）；汇总：`run/data/deleted_unmapped32_summary.md`。
> ⚠️ **实测更正**：此 32 目录实为 `staging_r3/` 下的**输入符号链接暂存**（仅 ~471.6 KB 元数据，非 `.bin/.idx/.json` 产物）；真正的分词产物此前迁移 `/nas_env/full_*` 时已处置。删除释放 ≈ 471.6 KB（非任务书所述 1.89 TB；1.89 TB 为按 token×4B 的理论 .bin 体积）。`/nas_inference` 源 parquet 原样保留。

| # | shard | 原路径(staging_r3/) | 删前字节 | 符号链接数 | 理论tokens(参考) | 状态 |
|:---|:---|:---|---:|---:|---:|:---|
| 1 | l3_s0 | l3_s0 | 15617 | 45 | 14,364,981,864 | 已删除 |
| 2 | l3_s1 | l3_s1 | 15617 | 45 | 14,367,599,448 | 已删除 |
| 3 | l3_s2 | l3_s2 | 15617 | 45 | 14,366,256,102 | 已删除 |
| 4 | l3_s3 | l3_s3 | 15617 | 45 | 14,366,613,648 | 已删除 |
| 5 | l3_s4 | l3_s4 | 15617 | 45 | 14,368,882,547 | 已删除 |
| 6 | l3_s5 | l3_s5 | 15617 | 45 | 14,365,361,981 | 已删除 |
| 7 | l3_s6 | l3_s6 | 15617 | 45 | 14,364,257,374 | 已删除 |
| 8 | l3_s7 | l3_s7 | 15617 | 45 | 14,366,499,270 | 已删除 |
| 9 | l3_s8 | l3_s8 | 15617 | 45 | 14,365,102,915 | 已删除 |
| 10 | l3_s9 | l3_s9 | 15617 | 45 | 14,366,083,546 | 已删除 |
| 11 | l3_s10 | l3_s10 | 15617 | 45 | 14,366,888,523 | 已删除 |
| 12 | l3_s11 | l3_s11 | 15617 | 45 | 14,365,010,123 | 已删除 |
| 13 | l3_s12 | l3_s12 | 15320 | 45 | 17,970,036,302 | 已删除 |
| 14 | l3_s25 | l3_s25 | 15230 | 45 | 19,048,242,972 | 已删除 |
| 15 | l3_s26 | l3_s26 | 15617 | 45 | 14,114,958,375 | 已删除 |
| 16 | l3_s27 | l3_s27 | 15617 | 45 | 14,115,321,614 | 已删除 |
| 17 | l3_s28 | l3_s28 | 15617 | 45 | 14,116,508,289 | 已删除 |
| 18 | l3_s29 | l3_s29 | 15617 | 45 | 14,116,608,027 | 已删除 |
| 19 | l3_s30 | l3_s30 | 15617 | 45 | 14,115,801,296 | 已删除 |
| 20 | l3_s31 | l3_s31 | 15617 | 45 | 14,114,861,130 | 已删除 |
| 21 | l3_s32 | l3_s32 | 15338 | 45 | 17,298,553,950 | 已删除 |
| 22 | l3_s33 | l3_s33 | 15212 | 45 | 18,737,130,528 | 已删除 |
| 23 | l3_s34 | l3_s34 | 15212 | 45 | 18,737,633,687 | 已删除 |
| 24 | l3_s35 | l3_s35 | 15212 | 45 | 18,738,003,380 | 已删除 |
| 25 | l3_s36 | l3_s36 | 15212 | 45 | 18,735,200,626 | 已删除 |
| 26 | l3_s37 | l3_s37 | 15212 | 45 | 18,737,362,596 | 已删除 |
| 27 | l3_s38 | l3_s38 | 15212 | 45 | 18,736,865,948 | 已删除 |
| 28 | l3_s39 | l3_s39 | 5500 | 9 | 3,747,724,045 | 已删除 |
| 29 | math_s32 | math_s32 | 14708 | 46 | 7,566,398,806 | 已删除 |
| 30 | math_s33 | math_s33 | 14448 | 46 | 10,432,537,812 | 已删除 |
| 31 | math_s34 | math_s34 | 14448 | 46 | 12,565,307,743 | 已删除 |
| 32 | math_s35 | math_s35 | 15570 | 46 | 14,711,233,910 | 已删除 |
| **合计** | | | **482,940** | **1,408** | **472,849,828,377** | |

核对式：`sum(删前字节)=482,940`；`sum(符号链接)=1,408`；`sum(理论tokens)=472,849,828,377`（理论 .bin 体积 ≈ 1.89 TB，**非实际释放量**）。

---

## C. 维护说明

- 生成器：`run/data/gen_data_mapping_md.py`（待补；当前为首版手工建立，数字均来自 `INDEX.tsv` 实测与 `deleted_unmapped32_20261025.tsv`）。
- 重跑幂等：A 节由 `build_tokenized_mirror.py` 产出的 `INDEX.tsv` 驱动；B 节由 `deleted_unmapped32_20261025.tsv` 驱动。
- 改名同步：分词后允许改目录名，但必须与本表同一批提交同步，改完跑 triplet+inode 校验写回「校验时间」。
- HTML 报告：需要时用 `gen_tokenized_inventory_report.py` 从本表渲染 `reports/report_data_tokenized_inventory_zh.html`。
