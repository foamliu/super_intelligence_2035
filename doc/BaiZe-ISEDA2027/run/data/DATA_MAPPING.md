# DATA_MAPPING.md — BaiZe 训练数据「下载 ↔ 分词」映射表（单一事实源）

> 维护规程（运维令 2026-10-25 17:5x / 18:5x）：本文件为 Markdown 单一事实源，由 `run/data/gen_data_mapping_md.py` 生成；HTML 报告按需由 `gen_tokenized_inventory_report.py` 渲染。
> 一行 = 一个下载目录（粒度以盘上 `ls` 实测为准）；`状态` 取值：`镜像完整` / `分词中` / `未分词` / `未映射` / `已废弃` / `已删除`。
> 合计行由脚本求和，禁手填。数字均来自实测（`du -sb` / `find | wc -l` / `INDEX.tsv`）。
> 生成器：`run/data/gen_data_mapping_md.py`（幂等：连跑两次逐字节相同）。驱动数据指纹：`INDEX.tsv` size=2888 blob-hash=1df161bf87e0 mtime=2026-10-25 14:54。

---

## A. 当前可用映射（下载目录 ↔ 分词镜像）

> 来源：`/nas_train/app.e0031982/datasets/baize-data/tokenized/INDEX.tsv`（镜像 build_tokenized_mirror.py 产出）。下载目录字节来自 `du -sb` 实测（缓存 `.du_download_cache.tsv`）。

| # | 下载目录 | 分词目录 | .bin | .idx | .json | 字节(B) | GB | tokens(B) | 下载目录字节(B) | 下载/分词字节比 | 状态 | 校验时间 | 证据 |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 1 | `…/Ultra-FineWeb/data/ultrafineweb_en_v1_4` | `…/Ultra-FineWeb/ultrafineweb_en_v1_4` | 110 | 110 | 110 | 8,929,852,999,497 | 8317 | 2,238,140,710,284 | 6,747,434,955,525 | 0.756 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv L2: triplet=OK inode_ok=110 (hardlink) |
| 2 | `…/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | `…/Ultra-FineWeb-L3/ultrafineweb_en_l3/qa` | 154 | 154 | 154 | 1,062,000,123,988 | 989 | 263,899,449,229 | 663,183,709,378 | 0.624 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv L3: triplet=OK inode_ok=154 (symlink) |
| 3 | `…/UltraData-Code/data/UltraData-Code-L2` | `…/UltraData-Code/UltraData-Code-L2` | 141 | 141 | 141 | 1,691,139,314,855 | 1575 | 421,450,419,455 | 611,281,878,122 | 0.361 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv L4: triplet=OK inode_ok=141 (symlink) |
| 4 | `…/UltraData-Code/data/UltraData-Code-L3` | `…/UltraData-Code/UltraData-Code-L3` | 63 | 63 | 63 | 516,117,199,509 | 481 | 128,623,266,591 | 604,712,501,031 | 1.172 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv L5: triplet=OK inode_ok=63 (symlink) |
| 5 | `…/UltraData-Math/data/UltraData-Math-L1` | `…/UltraData-Math/UltraData-Math-L1` | 149 | 149 | 149 | 659,469,460,275 | 614 | 164,437,183,984 | 366,622,940,699 | 0.556 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv L6: triplet=OK inode_ok=149 (symlink) |
| 6 | `…/UltraData-Math/data/UltraData-Math-L3` | `…/UltraData-Math/UltraData-Math-L3` | 67 | 67 | 67 | 313,425,604,823 | 292 | 77,949,162,709 | 122,536,811,815 | 0.391 | 镜像完整 | 2026-10-25 14:54 | INDEX.tsv L7: triplet=OK inode_ok=67 (symlink) |
| 7 | `…/Ultra-FineWeb/data/ultrafineweb_en` | `…/Ultra-FineWeb/ultrafineweb_en` | 0 | 0 | 0 | 0 | 0 | 0 | 2,661,358,397,268 | — | 分词中 | 2026-10-25 14:54 | ls …/Ultra-FineWeb/ultrafineweb_en/*.bin | wc -l ; 日志 /tmp/tokenize_untokenized_*.log（done=131/131 后刷新） |
| 8 | `…/Ultra-FineWeb/data/ultrafineweb_l1_en_hq` | `…/Ultra-FineWeb/ultrafineweb_l1_en_hq` | 32 | 32 | 32 | 192,910,037,902 | 180 | 47,988,834,942 | 477,975,290,461 | 2.478 | 分词中 | 2026-10-25 14:54 | ls …/Ultra-FineWeb/ultrafineweb_l1_en_hq/*.bin | wc -l ; 日志 /tmp/tokenize_untokenized_*.log（done=131/131 后刷新） |
| 9 | `…/Ultra-FineWeb/data/ultrafineweb_zh` | `…/Ultra-FineWeb/ultrafineweb_zh` | 0 | 0 | 0 | 0 | 0 | 0 | 324,321,522,155 | — | 分词中 | 2026-10-25 14:54 | ls …/Ultra-FineWeb/ultrafineweb_zh/*.bin | wc -l ; 日志 /tmp/tokenize_untokenized_*.log（done=131/131 后刷新） |
| 10 | `…/UltraX-Preview/data/UltraX-AICC` | `…/UltraX-Preview/UltraX-AICC` | 0 | 0 | 0 | 0 | 0 | 0 | 68,553,927,738 | — | 分词中 | 2026-10-25 14:54 | ls …/UltraX-Preview/UltraX-AICC/*.bin | wc -l ; 日志 /tmp/tokenize_untokenized_*.log（done=131/131 后刷新） |
| **合计** | | | **716** | **716** | **716** | **13,364,914,740,849** | **12447** | **3,342,489,027,194** | **12,647,981,934,192** | **11779 GB** | | | 误差 0 |

核对式：`sum(.bin)=716 = sum(.idx)=716 = sum(.json)=716`；`sum(分词字节)=13,364,914,740,849`；`sum(tokens)=3,342,489,027,194`；`sum(下载字节)=12,647,981,934,192`。

> 注：`env14_*` 真身在 `/nas_train/.../baize-data/text/`（与 `tokenized/` 同盘 ⇒ hardlink）；`full_*` 真身在 `/nas_env/app.e0031982/baize-data/`（跨盘 ⇒ symlink）。两者均属「下载的一律保留」，未删未改未移。`下载/分词字节比` = 下载目录字节 ÷ 分词产物字节（int32 token×4B 常大于压缩 parquet，故比值多 < 1）。

---

## B. 已删除 / 不可用（运维令 2026-10-25 18:2x · 用户直令 · 终裁）

> 用户口径：不能被本表 A 节收录的数据即不可用，留着只占盘。本节为终裁，删完即结案，不再挂账。
> 明细：`run/data/deleted_unmapped32_20261025.tsv`（32 行）；理论 tokens 来自 `run/data/prune_unmapped_judgment_20261025.tsv`（action 以「保留」开头的 32 行）。
> ⚠️ **实测更正**：此 32 目录实为 `staging_r3/` 下的**输入符号链接暂存**（仅 ~471.6 KB 元数据，非 `.bin/.idx/.json` 产物）；真正的分词产物此前迁移 `/nas_env/full_*` 时已处置。删除释放 ≈ 471.6 KB（非任务书所述 1.89 TB；1.89 TB 为按 token×4B 的理论 .bin 体积）。`/nas_inference` 源 parquet 原样保留。

| # | shard | 原路径(staging_r3/) | 删前字节 | 符号链接数 | 理论tokens(参考) | 状态 |
|:---|:---|:---|---:|---:|---:|:---|
| 1 | l3_s0 | l3_s0 | 15,617 | 45 | 14,364,981,864 | 已删除 |
| 2 | l3_s1 | l3_s1 | 15,617 | 45 | 14,367,599,448 | 已删除 |
| 3 | l3_s10 | l3_s10 | 15,617 | 45 | 14,366,888,523 | 已删除 |
| 4 | l3_s11 | l3_s11 | 15,617 | 45 | 14,365,010,123 | 已删除 |
| 5 | l3_s12 | l3_s12 | 15,320 | 45 | 17,970,036,302 | 已删除 |
| 6 | l3_s2 | l3_s2 | 15,617 | 45 | 14,366,256,102 | 已删除 |
| 7 | l3_s25 | l3_s25 | 15,230 | 45 | 19,048,242,972 | 已删除 |
| 8 | l3_s26 | l3_s26 | 15,617 | 45 | 14,114,958,375 | 已删除 |
| 9 | l3_s27 | l3_s27 | 15,617 | 45 | 14,115,321,614 | 已删除 |
| 10 | l3_s28 | l3_s28 | 15,617 | 45 | 14,116,508,289 | 已删除 |
| 11 | l3_s29 | l3_s29 | 15,617 | 45 | 14,116,608,027 | 已删除 |
| 12 | l3_s3 | l3_s3 | 15,617 | 45 | 14,366,613,648 | 已删除 |
| 13 | l3_s30 | l3_s30 | 15,617 | 45 | 14,115,801,296 | 已删除 |
| 14 | l3_s31 | l3_s31 | 15,617 | 45 | 14,114,861,130 | 已删除 |
| 15 | l3_s32 | l3_s32 | 15,338 | 45 | 17,298,553,950 | 已删除 |
| 16 | l3_s33 | l3_s33 | 15,212 | 45 | 18,737,130,528 | 已删除 |
| 17 | l3_s34 | l3_s34 | 15,212 | 45 | 18,737,633,687 | 已删除 |
| 18 | l3_s35 | l3_s35 | 15,212 | 45 | 18,738,003,380 | 已删除 |
| 19 | l3_s36 | l3_s36 | 15,212 | 45 | 18,735,200,626 | 已删除 |
| 20 | l3_s37 | l3_s37 | 15,212 | 45 | 18,737,362,596 | 已删除 |
| 21 | l3_s38 | l3_s38 | 15,212 | 45 | 18,736,865,948 | 已删除 |
| 22 | l3_s39 | l3_s39 | 5,500 | 9 | 3,747,724,045 | 已删除 |
| 23 | l3_s4 | l3_s4 | 15,617 | 45 | 14,368,882,547 | 已删除 |
| 24 | l3_s5 | l3_s5 | 15,617 | 45 | 14,365,361,981 | 已删除 |
| 25 | l3_s6 | l3_s6 | 15,617 | 45 | 14,364,257,374 | 已删除 |
| 26 | l3_s7 | l3_s7 | 15,617 | 45 | 14,366,499,270 | 已删除 |
| 27 | l3_s8 | l3_s8 | 15,617 | 45 | 14,365,102,915 | 已删除 |
| 28 | l3_s9 | l3_s9 | 15,617 | 45 | 14,366,083,546 | 已删除 |
| 29 | math_s32 | math_s32 | 14,708 | 46 | 7,566,398,806 | 已删除 |
| 30 | math_s33 | math_s33 | 14,448 | 46 | 10,432,537,812 | 已删除 |
| 31 | math_s34 | math_s34 | 14,448 | 46 | 12,565,307,743 | 已删除 |
| 32 | math_s35 | math_s35 | 15,570 | 46 | 14,711,233,910 | 已删除 |
| **合计** | | | **482,940** | **1408** | **472,849,828,377** | |

核对式：`sum(删前字节)=482,940`；`sum(符号链接)=1408`；`sum(理论tokens)=472,849,828,377`（理论 .bin 体积 ≈ 1.72 TB，**非实际释放量**）。

---

## C. 维护说明

- 生成器：`run/data/gen_data_mapping_md.py`（本文件由它产出；驱动数据指纹见页首）。
- 幂等判据：`python gen_data_mapping_md.py --check-idempotent` ⇒ 连跑两次 `DATA_MAPPING.md` 逐字节相同。
- A 节由 `tokenized/INDEX.tsv`（build_tokenized_mirror.py 产出）+ `.du_download_cache.tsv`（`du -sb` 下载目录）驱动；`--measure` 重测下载字节并刷新缓存。
- B 节由 `deleted_unmapped32_20261025.tsv`（删前留档）+ `prune_unmapped_judgment_20261025.tsv`（理论 tokens）驱动。
- 分词中 → 镜像完整：`done=131/131` 后重跑 `build_tokenized_mirror.py`（把新 shard hardlink 进镜像、刷新 INDEX.tsv），再清空 `mapping_inprogress.txt`，最后重跑本脚本 ⇒ A 节第 7–10 行自动翻 `镜像完整` 并补字节/tokens。
- 改名同步：分词后允许改目录名，但必须与本表同一批提交同步；改完跑 triplet+inode 校验写回 INDEX.tsv，再重跑本脚本。
- HTML 报告：需要时用 `gen_tokenized_inventory_report.py` 从本表渲染 `reports/report_data_tokenized_inventory_zh.html`。

