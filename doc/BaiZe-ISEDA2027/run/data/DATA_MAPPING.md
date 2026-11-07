# DATA_MAPPING.md — BaiZe 训练数据「下载 ↔ 分词」映射表（单一事实源）

> 维护规程（运维令 2026-10-25 17:5x / 18:5x）：本文件为 Markdown 单一事实源，由 `run/data/gen_data_mapping_md.py` 生成；HTML 报告按需由 `gen_tokenized_inventory_report.py` 渲染。
> 一行 = 一个下载目录（粒度以盘上 `ls` 实测为准）；`状态` 取值：`镜像完整` / `分词中` / `未分词` / `未映射` / `已废弃` / `已删除`。
> 合计行由脚本求和，禁手填。数字均来自实测（`du -sb` / `find | wc -l` / `INDEX.tsv`）。
> 生成器：`run/data/gen_data_mapping_md.py`（幂等：连跑两次逐字节相同）。驱动数据指纹：`INDEX.tsv` size=3513 blob-hash=33fb0d4ebc9b mtime=2026-10-27 15:06。

---

## A. 当前可用映射（下载目录 ↔ 分词镜像）

> 来源：`/nas_train/app.e0031982/datasets/baize-data/tokenized/INDEX.tsv`（镜像 build_tokenized_mirror.py 产出）。下载目录字节来自 `du -sb` 实测（缓存 `.du_download_cache.tsv`）。

| # | 下载目录 | 分词目录 | .bin | .idx | .json | 字节(B) | GB | tokens(B) | 下载目录字节(B) | 下载/分词字节比 | 状态 | 校验时间 | 证据 |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 1 | `…/Ultra-FineWeb/data/ultrafineweb_en_v1_4` | `…/Ultra-FineWeb/ultrafineweb_en_v1_4` | 110 | 110 | 110 | 8,999,055,538,432 | 8381 | 2,237,073,612,082 | 6,747,434,955,525 | 0.750 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L2: triplet=OK inode_ok=110 (hardlink) |
| 2 | `…/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | `…/Ultra-FineWeb-L3/ultrafineweb_en_l3/qa` | 154 | 154 | 154 | 1,062,000,123,988 | 989 | 263,899,449,229 | 663,183,709,378 | 0.624 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L3: triplet=OK inode_ok=154 (symlink) |
| 3 | `…/UltraData-Code/data/UltraData-Code-L2` | `…/UltraData-Code/UltraData-Code-L2` | 141 | 141 | 141 | 1,691,139,314,855 | 1575 | 421,450,419,455 | 611,281,878,122 | 0.361 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L4: triplet=OK inode_ok=141 (symlink) |
| 4 | `…/UltraData-Code/data/UltraData-Code-L3` | `…/UltraData-Code/UltraData-Code-L3` | 63 | 63 | 63 | 516,117,199,509 | 481 | 128,623,266,591 | 604,712,501,031 | 1.172 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L5: triplet=OK inode_ok=63 (symlink) |
| 5 | `…/UltraData-Math/data/UltraData-Math-L1` | `…/UltraData-Math/UltraData-Math-L1` | 149 | 149 | 149 | 659,469,460,275 | 614 | 164,437,183,984 | 366,622,940,699 | 0.556 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L6: triplet=OK inode_ok=149 (symlink) |
| 6 | `…/UltraData-Math/data/UltraData-Math-L3` | `…/UltraData-Math/UltraData-Math-L3` | 67 | 67 | 67 | 313,425,604,823 | 292 | 77,949,162,709 | 122,536,811,815 | 0.391 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L7: triplet=OK inode_ok=67 (symlink) |
| 7 | `…/Ultra-FineWeb/data/ultrafineweb_en` | `…/Ultra-FineWeb/ultrafineweb_en` | 32 | 32 | 32 | 3,222,004,397,626 | 3001 | 905,921,334,220 | 2,661,358,397,268 | 0.826 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L8: triplet=OK inode_ok=32 (symlink) |
| 8 | `…/Ultra-FineWeb/data/ultrafineweb_l1_en_hq` | `…/Ultra-FineWeb/ultrafineweb_l1_en_hq` | 94 | 94 | 94 | 603,519,735,520 | 562 | 150,155,374,778 | 477,975,290,461 | 0.792 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L9: triplet=OK inode_ok=94 (symlink) |
| 9 | `…/Ultra-FineWeb/data/ultrafineweb_zh` | `…/Ultra-FineWeb/ultrafineweb_zh` | 4 | 4 | 4 | 453,644,894,252 | 422 | 112,756,190,641 | 324,321,522,155 | 0.715 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L10: triplet=OK inode_ok=4 (symlink) |
| 10 | `…/UltraX-Preview/data/UltraX-AICC` | `…/UltraX-Preview/UltraX-AICC` | 1 | 1 | 1 | 46,394,689,578 | 43 | 11,492,264,080 | 68,553,927,738 | 1.478 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L11: triplet=OK inode_ok=1 (symlink) |
| 11 | `…/UltraData-SFT-2605/data` | `…/UltraData-SFT-2605/UltraData-SFT-2605` | 94 | 94 | 94 | 75,867,441,833 | 71 | 18,891,665,320 | 318,990,486,183 | 4.205 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L12: triplet=OK inode_ok=94 (symlink) |
| 12 | `…/UltraData-SFT-Agent-2609/data` | `…/UltraData-SFT-Agent-2609/UltraData-SFT-Agent-2609` | 13 | 13 | 13 | 23,886,244,139 | 22 | 5,969,140,740 | 54,220,373,384 | 2.270 | 镜像完整 | 2026-10-27 15:06 | INDEX.tsv L13: triplet=OK inode_ok=13 (symlink) |
| **合计** | | | **922** | **922** | **922** | **17,666,524,644,830** | **16453** | **4,498,619,063,829** | **13,021,192,793,759** | **12127 GB** | | | 误差 0 |

核对式：`sum(.bin)=922 = sum(.idx)=922 = sum(.json)=922`；`sum(分词字节)=17,666,524,644,830`；`sum(tokens)=4,498,619,063,829`；`sum(下载字节)=13,021,192,793,759`。

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

### 清理记录（运维令 2026-10-25 18:5x ②）

> 磁盘清理按实测分批执行；每批实占 ≤500 GB，删后校验镜像 .bin 恒定 + 悬空链接 = 0。manifest = `run/data/disk_cleanup_candidates_20261025.tsv`。

| 批次 | 日期 | 删除项 | 释放字节(实占) | manifest | 状态 |
|:---|:---|:---|---:|:---|:---|
| batch1 | 2026-10-25 | 78 staging_r3 symlink dirs + 1 .bak + 1 empty dir (staging_full) + 1 oldest /tmp log (kept latest 3) | 1,132,338 | `disk_cleanup_candidates_20261025.tsv` | DONE |
| batch2 | 2026-10-25 | 110 env14_*.bin hardlink copies in text/ (actual 0 bytes; tokenized/ holds same inode; tidy only) | 0 | `disk_cleanup_candidates_20261025.tsv` | PENDING operator decision |

> 注：`释放字节(实占)` = 硬链接只算一次后的实际释放量（非表观体积）。batch1 释放 ~1.13 MB（78 个 staging_r3 符号链接目录 + .bak + 空目录 + 旧日志）；表观体积远大于实占因 110 env14 hardlink 实占 0。

---

## D. 可删候选（2026-10-30 /nas_train 盘点）

> 运维令 2026-10-30 22:2x：`/nas_train` 大目录盘点 + 可删候选表。本轮**只出候选清单，不执行删除**（等运维批准）。
> 完整明细：`run/data/cleanup_candidates_20261030.tsv`（49 行，含 path / 表观(du -sh) / 实占(du -sb) / inode / 判定 / 证据命令）。
> ⚠️ **表观 ≠ 实占**：硬链接目录（如 baize-data/ env14）表观 8.4T 但实占因 hardlink 部分已被 tokenized/ 镜像共享；本节只列合计与判定，不把表观当实占。

### 红线（一律保留，不可删）

| 路径 | 表观 | 实占(B) | 理由 |
|:---|---:|---:|:---|
| `datasets/mvp-lab/` | 42T | 45,985,312,034,386 | 85M 下载进行中（10462/12126 files，86.3%） |
| `datasets/openbmb/` | 9.8T | 10,698,031,684,940 | INDEX.tsv 下载源 parquet（Ultra-FineWeb / UltraX-Preview） |
| `datasets/baize-data/` | 8.4T | 9,186,503,937,898 | RED LINE：tokenized/ INDEX.tsv full_* |
| `datasets/baize-vision/` | 1.1T | 1,116,034,189,821 | vision agent 活跃数据 |
| `code/` | 3.5T | — | BaiZe-ISEDA2027 项目代码 |
| `.cline_*/` | ~4.4G | — | 活跃 agent 会话数据（4 个） |

### 可删（低风险）

| 路径 | 表观 | 实占(B) | 理由 |
|:---|---:|---:|:---|
| `datasets/stanford-corenlp-full-2016-10-31.zip` | 389M | 388,633,790 | 解压目录已存在，zip 冗余 |
| `tmp/.nfs0000000b14c0fe4000fd2352` | — | — | NFS silly-rename 垃圾 |
| `nccl_dbg/` | 68K | 37,673 | NCCL 调试日志 |

### 待定（需运维/各线确认后决定）

| 路径 | 表观 | 实占(B) | 说明 |
|:---|---:|---:|:---|
| `datasets/FineVision/` | 4.3T | 4,645,236,803,666 | 186 视觉数据子目录，不在 INDEX.tsv，待 vision 确认 |
| `datasets/HuggingFaceFW/` | 1.3T | 1,365,756,121,231 | fineweb-edu，不在 INDEX.tsv，旧文本下载 |
| `datasets/conceptual-captions-12m-webdataset/` | 1.2T | 1,244,033,908,448 | webdataset 格式，不在 INDEX.tsv |
| `datasets/imagenet-1k/` | 156G | 166,753,472,862 | ImageNet-1K，不在 INDEX.tsv |
| `datasets/lmms-lab/` | 137G | 146,251,614,972 | LMM 评测数据，不在 INDEX.tsv |
| `datasets/LLaVA-Instruct-150K/` | 91G | 97,680,038,930 | LLaVA 指令数据，不在 INDEX.tsv |
| `datasets/LLaVA-Pretrain/` | 85G | 85,723,169,187 | LLaVA 预训练（664 entries），不在 INDEX.tsv |
| `datasets/coco/` | 63G | 65,303,204,197 | COCO 数据集，不在 INDEX.tsv |
| `datasets/gqa/` | 42G | 43,816,985,024 | GQA 视觉推理，不在 INDEX.tsv |
| `datasets/vg/` | 30G | 30,545,172,713 | Visual Genome，不在 INDEX.tsv |
| `datasets/textvqa/` | 14G | 14,168,782,169 | TextVQA，不在 INDEX.tsv |
| `datasets/ocr_vqa/` | 9.1G | 7,988,057,464 | OCR-VQA，不在 INDEX.tsv |
| `datasets/LLaVA-CC3M-Pretrain-595K/` | 6.4G | 6,866,613,212 | LLaVA CC3M，不在 INDEX.tsv |
| `models/` | 460G | 493,837,583,591 | 模型权重，pretrain/vision 可能依赖 |
| `hf_cache/` | 49G | 51,781,238,854 | HF 缓存，清理可能影响续传 |
| `outputs/` | 6.7G | 7,125,118,579 | 旧训练输出 |
| `download/` | 3.4G | 2,674,418,927 | 旧下载目录 |
| `.hf_cache/` | 2.0G | 2,074,331,978 | 隐藏 HF 缓存 |
| `tmp/` | 1.3G | 1,180,858,456 | 临时文件（含 .nfs 垃圾） |
| `datasets/armanakbari4/` | 1.6G | 387,389,164 | 用途不明 |
| `datasets/red_caps/` | 1013M | 1,061,997,941 | RedCaps，不在 INDEX.tsv |
| `datasets/AMSbench/` | 495M | 517,861,956 | AMS benchmark |
| `datasets/stanford-corenlp-full-2016-10-31/` | 373M | 390,330,174 | Stanford CoreNLP（如不使用） |
| `datasets/MMMU/` | 232M | 240,736,341 | MMMU 评测数据 |
| `Downloads/` | 209M | 216,932,527 | 旧下载 |
| `datasets/allenai/` | 1.7M | 1,415,941 | 用途不明 |
| `code/BaiZe-ISEDA2027/nemo_experiments/` | 645G | 692,340,206,072 | 旧 NeMo 训练实验（128 子目录，架构搜索期已收敛），不在 INDEX.tsv |
| `datasets/mvp-lab/LLaVA-OneVision-1.5-Instruct-Data/` | 5.5T | 5,989,056,868,520 | LLaVA 指令调优数据（182 子目录），不在 INDEX.tsv |
| `datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-Webdataset-Quick-Start-3M/` | 149G | 159,121,745,303 | LLaVA 快速启动 webdataset，不在 INDEX.tsv |
| `datasets/mvp-lab/LLaVA-NeXT-780k-webdataset/` | 101G | 108,079,183,973 | LLaVA-NeXT webdataset，不在 INDEX.tsv |
| `code/LLaVA-OneVision-1.5-RL/` | 30G | 30,125,997,787 | LLaVA RL 代码+数据，不在 INDEX.tsv |
| `code/BaiZe-ISEDA2027/output/` | 22G | 22,792,217,964 | 旧训练输出，不在 INDEX.tsv |
| `code/BaiZe-ISEDA2027/hf_checkpoints/` | 8.9G | 9,485,369,788 | 旧 HF 检查点 |
| `code/flash-attention/` | 8.9G | 9,359,124,562 | flash-attention 源码（编译依赖） |
| `datasets/mvp-lab/LLaVA-OneVision-1.5-RL-Data/` | 19G | 20,022,879,590 | LLaVA RL 数据，不在 INDEX.tsv |
| `datasets/mvp-lab/llava_conversion_work/` | 7.1G | 7,220,256,280 | LLaVA 转换工作目录 |

> ⚠️ 上述 `nemo_experiments/`、`code/BaiZe-ISEDA2027/output/`、`code/LLaVA-OneVision-1.5-RL/` 等是 `code/`（红线保留）下的子目录；`mvp-lab/LLaVA-OneVision-1.5-Instruct-Data/` 等是 `mvp-lab/`（红线保留，含 85M 下载）下的子目录。它们作为独立条目列出以供运维逐项决策，但表观合计与父目录有重叠。

### 可删（低风险）· 补充

| 路径 | 表观 | 实占(B) | 理由 |
|:---|---:|---:|:---|
| `code/BaiZe-ISEDA2027/p6_tf5/` | 302M | 214,841,930 | 旧实验数据（63 子目录，架构搜索期），不在 INDEX.tsv |

### 合计估算

| 分类 | 表观合计 | 实占合计(B) | 说明 |
|:---|---:|---:|:---|
| 红线（保留） | ~61.7T | ~66,906,379,766,145 | 不可删（含 85M 下载 37T + 源 parquet + 分词产物） |
| 可删（低风险） | ~691M | ~603,513,393 | 等批准即可删（stanford-corenlp zip + .nfs + nccl_dbg + p6_tf5） |
| 待定（待确认） | ~14.3T | ~14,649,436,452,716 | 需各线 agent 确认是否使用（含子目录独立条目，与父目录有重叠） |
| **总计** | ~69.7T | | /nas_train 已用 173T / 207T (84%) |

> ⚠️ **待定项中 Top-5 最大可释放空间**：FineVision(4.3T) + LLaVA-Instruct-Data(5.5T) + HuggingFaceFW(1.3T) + conceptual-captions(1.2T) + nemo_experiments(645G) = **~12.9T**，但需 vision agent 确认 FineVision/conceptual-captions/Instruct-Data 是否使用，需确认 HuggingFaceFW/fineweb-edu 是否为旧下载，需确认 nemo_experiments 是否仍有参考价值。

---

## E. 长上下文下载（运维令 2026-11-04 09:2x · 未分词 · 落盘 `/nas_inference`）

> 运维令 2026-11-04 09:2x（用户直令 · 最高优先）：批准下载「长上下文」A 类数据集，落盘 `/nas_inference/app.e0031982/datasets/<repo原名>/`。
> **本节为下载登记（未分词）**：10 源全部 `status=OK`、`incomplete=0`，下载于 2026-11-04 12:46 全部落地（launch 日志 `==== longctx download FINISH 12:46:07 ====`）。
> 数据源（durable）：`run/data/longctx_download_status_20261104.tsv`（10 行，幂等可复现）。字节来自 `du -sb` 实测（.12 公开 9 源 + .29 gated 1 源）。
> ⚠️ `deepmind/pg19` 仅含加载脚本 + 文件清单（494,680 B / 18 files），**无 parquet 数据体**——HF 上 pg19 为 script-based 数据集，实际文本需经 `load_dataset` 脚本按 `train_files.txt` 拉取；当前登记如实记录「已下载文件 = 脚本+清单」，数据体待后续 `load_dataset` 或找 parquet 镜像补齐。
> ⚠️ `birgermoell/oellm-...pilot-v1` 已为分词后 `.bin/.idx` 格式（非原始文本），可直接用于长上下文训练，无需再分词。

| # | repo_id | 落盘路径 | 主机 | 文件数 | 字节(B) | GiB | gated | incomplete | 备注 |
|:---|:---|:---|:---|---:|---:|---:|:---|---:|:---|
| 1 | `ysngkil/whole-books` | `/nas_inference/app.e0031982/datasets/ysngkil/whole-books` | .12 | 147 | 27,173,873,250 | 25.31 | no | 0 | 书籍长文 |
| 2 | `princeton-nlp/prolong-data-512K` | `/nas_inference/app.e0031982/datasets/princeton-nlp/prolong-data-512K` | .12 | 10,062 | 122,387,428,650 | 113.98 | no | 0 | prolong 512K 训练数据 |
| 3 | `openbmb/InfLLM-V2-data-5B` | `/nas_inference/app.e0031982/datasets/openbmb/InfLLM-V2-data-5B` | .12 | 66 | 16,143,986,199 | 15.04 | no | 0 | InfLLM-V2 5B 训练数据 |
| 4 | `self-long/RULER-llama3-1M` | `/nas_inference/app.e0031982/datasets/self-long/RULER-llama3-1M` | .12 | 360 | 5,506,516,210 | 5.13 | no | 0 | RULER 1M 评测/合成 haystack |
| 5 | `caskcsg/NExtLong-128K-dataset` | `/nas_inference/app.e0031982/datasets/caskcsg/NExtLong-128K-dataset` | .12 | 627 | 22,010,223,770 | 20.50 | no | 0 | NExtLong 128K（原 401 私有，改公开变体） |
| 6 | `THUDM/LongAlign-10k` | `/nas_inference/app.e0031982/datasets/THUDM/LongAlign-10k` | .12 | 9 | 655,080,842 | 0.61 | no | 0 | LongAlign 10k 长对齐 |
| 7 | `birgermoell/oellm-longctx-tokenized-natural-128k-256k-pilot-v1` | `/nas_inference/app.e0031982/datasets/birgermoell/oellm-longctx-tokenized-natural-128k-256k-pilot-v1` | .12 | 69 | 3,059,986,934 | 2.85 | no | 0 | oellm pilot-v1（已分词 .bin/.idx） |
| 8 | `deepmind/pg19` | `/nas_inference/app.e0031982/datasets/deepmind/pg19` | .12 | 18 | 494,680 | 0.00 | no | 0 | ⚠️ 仅脚本+清单，无 parquet 数据体 |
| 9 | `ghostcc3/mix-context-post-training-128k` | `/nas_inference/app.e0031982/datasets/ghostcc3/mix-context-post-training-128k` | .12 | 690 | 34,848,792,554 | 32.46 | no | 0 | mix-context 128k 后训练 |
| 10 | `yuyijiong/LongData-Corpus` | `/nas_inference/app.e0031982/datasets/yuyijiong/LongData-Corpus` | .29 | 235 | 36,070,795,362 | 33.60 | yes | 0 | gated（用户 token 授权，.29） |
| **合计** | **10 源** | | | **12,283** | **267,857,178,451** | **249.48** | | **0** | .12 公开 9 源 = 215.88 GiB / 12,048 files；.29 gated 1 源 = 33.60 GiB / 235 files |

核对式：`sum(文件)=12,283`；`sum(字节)=267,857,178,451`（≈ 249.48 GiB / 232.36 GB）；`.12 公开 = 231,786,383,089`；`.29 gated = 36,070,795,362`；`sum(incomplete)=0`。

> 落盘校验：每源 `du -sb` + `find -name '*.incomplete' | wc -l = 0` + `find -type f | wc -l` 三项核对（2026-11-04 12:46）。launch 日志 `/tmp/data_download_lc_20261104_101957.log` 记录全部 `status=OK`。
> 后续动作（待运维批准）：① pg19 数据体补齐（找 parquet 镜像或 `load_dataset` 脚本拉取）；② 长上下文源分词入 `tokenized/` 镜像（oellm pilot-v1 已分词可直接用）；③ 分词后回写 A 节、本节状态翻「已分词」。
> 🚫 token 不得写入本表/日报/任何 commit（运维令 09:2x ③）。

---

## F. B 类 agentic 数据下载（运维令 2026-11-04 13:2x · 未分词 · 落盘 `/nas_inference`）

> 运维令 2026-11-04 13:2x（用户直令 · 最高优先）：放行 B 类 agentic 数据下载，落盘 `/nas_inference/app.e0031982/datasets/<repo原名>/`。
> **本节为下载登记（未分词）**：12 源全部 `status=OK`、`incomplete=0`，下载于 2026-11-04 14:16 全部落地（master 日志 `==== bclass download start 20261104_133804 ====`，末源 `ia03/terminal-bench` 完成于 14:16）。
> 数据源（durable）：`/tmp/data_download_bclass_status.tsv`（12 行，幂等可复现）+ master 日志 `/tmp/data_download_bclass_master.log`。字节/文件数来自 `du -sb` + `find -type f | wc -l` 实测（.12 全部公开 non-gated，无 gated 源）。
> ⚠️ `ia03/terminal-bench` 为**评测集本体**（运维令标注「评测集仅去污染」）——**不得入训练集**，仅用于建黑名单/去污染校验，与 EDA-Eval 红线同口径。
> ⚠️ 巨大项 `AlienKevin/SWE-ZERO-12M-trajectories`(111G) 按运维令②**不默认下**，选择性下或后置（盘上 `AlienKevin/` 目录为旧残留，非本轮产物）。

| # | repo_id | 落盘路径 | 主机 | 文件数 | 字节(B) | GiB | gated | incomplete | 备注 |
|:---|:---|:---|:---|---:|---:|---:|:---|---:|:---|
| 1 | `SWE-bench/SWE-smith` | `/nas_inference/app.e0031982/datasets/SWE-bench/SWE-smith` | .12 | 40 | 277,797,639 | 0.25 | no | 0 | SWE-smith 修复轨迹（MIT） |
| 2 | `nvidia/Nemotron-Terminal-Corpus` | `/nas_inference/app.e0031982/datasets/nvidia/Nemotron-Terminal-Corpus` | .12 | 94 | 8,198,886,139 | 7.63 | no | 0 | 终端命令语料（CC BY 4.0） |
| 3 | `nebius/SWE-rebench` | `/nas_inference/app.e0031982/datasets/nebius/SWE-rebench` | .12 | 16 | 245,202,838 | 0.22 | no | 0 | SWE-rebench |
| 4 | `zhangdw/to-tool-call-datasets` | `/nas_inference/app.e0031982/datasets/zhangdw/to-tool-call-datasets` | .12 | 37 | 2,354,026,701 | 2.19 | no | 0 | 工具调用 SFT |
| 5 | `tuandunghcmut/toolbench-v1` | `/nas_inference/app.e0031982/datasets/tuandunghcmut/toolbench-v1` | .12 | 40 | 540,918,767 | 0.50 | no | 0 | ToolBench-v1（Apache-2.0） |
| 6 | `open-thoughts/AgentTrove` | `/nas_inference/app.e0031982/datasets/open-thoughts/AgentTrove` | .12 | 121 | 19,552,408,650 | 18.20 | no | 0 | Agent 多轮轨迹 |
| 7 | `microsoft/Orchard` | `/nas_inference/app.e0031982/datasets/microsoft/Orchard` | .12 | 73 | 10,962,177,581 | 10.20 | no | 0 | Orchard（MIT） |
| 8 | `nvidia/Nemotron-Cascade-RL-SWE` | `/nas_inference/app.e0031982/datasets/nvidia/Nemotron-Cascade-RL-SWE` | .12 | 16 | 31,322,695,342 | 29.17 | no | 0 | SWE RL cascade（可验证奖励） |
| 9 | `nvidia/Nemotron-Cascade-SFT-SWE` | `/nas_inference/app.e0031982/datasets/nvidia/Nemotron-Cascade-SFT-SWE` | .12 | 16 | 6,768,363,884 | 6.30 | no | 0 | SWE SFT cascade（CC BY 4.0） |
| 10 | `SWE-bench/SWE-smith-trajectories` | `/nas_inference/app.e0031982/datasets/SWE-bench/SWE-smith-trajectories` | .12 | 103 | 4,223,886,972 | 3.93 | no | 0 | SWE-smith 轨迹（parquet） |
| 11 | `mshojaei77/terminal-command-execution-sft` | `/nas_inference/app.e0031982/datasets/mshojaei77/terminal-command-execution-sft` | .12 | 13 | 51,198,163 | 0.04 | no | 0 | 终端命令执行 SFT |
| 12 | `ia03/terminal-bench` | `/nas_inference/app.e0031982/datasets/ia03/terminal-bench` | .12 | 13 | 41,302,907 | 0.03 | no | 0 | ⚠️ 评测集本体，仅去污染，禁入训练 |
| **合计** | **12 源** | | | **582** | **84,538,865,583** | **78.73** | | **0** | 全部公开 non-gated；含 1 评测集（terminal-bench） |

核对式：`sum(文件)=582`；`sum(字节)=84,538,865,583`（≈ 78.73 GiB / 78.73 GB）；`sum(incomplete)=0`；最大源 = Nemotron-Cascade-RL-SWE(29.17 GiB)。

> 落盘校验：每源 `du -sb` + `find -type f | wc -l` + `find -name '*.incomplete' | wc -l = 0` 三项核对（2026-11-04 14:16，.12）。master 日志 `/tmp/data_download_bclass_master.log` 记录全部 12 源 `status=OK`、`attempts=1`、`incomplete=0`。
> 下载纪律（运维令④）：`setsid` 后台 + `/tmp/data_download_*.log`；`nice`、`--max-workers 4` 限并发；走代理 `HTTPS_PROXY=http://172.19.92.25:13128`；断点续传（hf download 原生支持）。
> 后续动作（待运维批准）：① agentic 源分词入 `tokenized/` 镜像（需先定分词口径，部分为 jsonl/parquet 非 mcore 格式）；② `ia03/terminal-bench` 纳入去污染黑名单（与 SWE-bench Verified / Terminal Bench 同闸）；③ 分词后回写 A 节、本节状态翻「已分词」。
> 🚫 token 不得写入本表/日报/任何 commit（运维令 13:2x ③）。

---

## G. 代码语料放行 + ROI 自排优先级下载（运维令 2026-11-07 08:5x · 未分词 · 落盘 `/nas_inference`）

> 运维令 2026-11-07 08:5x（用户直令 · 最高优先）：放行代码语料下载——`bigcode/the-stack-v2` 禁下（67.5TB gated）、`HuggingFaceCode/stack-v3-train` 可考虑（15.9TB train，⚠️≥1TB 需报运维批准）、其余单集 <1TB 放行；agent 自排 ROI 优先级从高到低下载。
> **三条硬口径**：① stack-v2 🚫 禁下；② stack-v3-train ⚠️ ≥1TB 需报运维（本轮不下，见 §G.3）；③ 单集 ≥1TB 一律不自行下载。
> **本轮新增总量**：8 源 ≈ 25.15 GB，远低于 1.5TB 上限。跳过 3 源（见 §G.2）。体量来自 HF API `list_repo_tree` 实测（2026-11-07 08:5x）。

### G.1 ROI 评估表（5 维度 × 排序）

> 评估维度：① 相关性（PyAether/EDA 代码生成/agentic 工具调用直接帮助）② 单位成本收益（GB vs token量 vs 独特性）③ 可用性（gated/license/格式）④ 质量风险（NC license/评测污染/清洗需求）⑤ 落地成本（下载时长+转换）。

| ROI | repo_id | HF体量 | 文件 | 相关性 | 单位成本 | 可用性 | 质量风险 | 落地成本 | 决策 | 理由 |
|---:|:---|---:|---:|:---|:---|:---|:---|:---|:---|:---|
| 1 | `utter-project/LongBlocks` | 9.57GB | 39 | 🟢高 | 🟢高 | 🟢CC BY-SA 4.0/非gated | 🟢低 | 🟢~16min | ✅下载 | 194K多语言长上下文QA(含中文)+3教师响应可蒸馏；SFT用途 |
| 2 | `nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` | 5.10GB | 3 | 🟢高 | 🟢高 | 🟢CC-BY-4.0/非gated | 🔴高(SWE同源) | 🟢~9min | ✅下载 | 33.8K步级RL(pass-rate)；agentic SWE直接相关；须去污染 |
| 3 | `caskcsg/NExtLong-Instruct-Magpie-Llama-3.3-Pro-1M-v0.1` | 2.89GB | 69 | 🟢高 | 🟢高 | 🟡license未核到/非gated | 🟢低(合成) | 🟢~5min | ✅下载 | 1M合成长上下文；64K/128K/256K/512K子集100%≥64K；直击decay-B闸门 |
| 4 | `common-pile/arxiv_papers_filtered` | 6.04GB | 10 | 🟡中 | 🟡中 | 🟢CC BY/SA/CC0/非gated | 🟢低 | 🟢~10min | ✅下载 | 论文全文8K-50K；≥128K有限但版权干净且与web数据有独特性 |
| 5 | `THUDM/LongWriter-6k` | 0.15GB | 3 | 🟡中 | 🟢高(极小) | 🟢非gated | 🟢低 | 🟢<1min | ✅下载 | 6K长输出生成SFT(2K-20K words)；体积小ROI高 |
| 6 | `NovaSky-AI/SkyRL-v0-293-data` | 0.002GB | 3 | 🟡中 | 🟢高(极小) | 🟡license未核到 | 🟡中(SWE-Gym同源) | 🟢<1min | ✅下载 | 293 tasks验证RL pipeline；7B:11→14.6%有据 |
| 7 | `Nethraaaaa81/swev-trm-trajectories-25models` | 0.93GB | 4 | 🟡中 | 🟡中 | 🟢MIT/非gated | 🔴高(直接用Verified) | 🟢~2min | ✅下载 | 25模型12K轨迹；仅TRM训练/分析；🚫禁SFT |
| 8 | `zai-org/LongBench-v2` | 0.47GB | 3 | N/A(评测) | N/A | 🟢Apache-2.0 | ⚠️评测集 | 🟢<1min | ✅下载(仅去污染) | 503 MCQ；🚫禁入训练；仅去污染黑名单 |
| — | `common-pile/project_gutenberg_filtered` | 7.63GB | 17 | 🔴低 | 🔴低(冗余) | 🟢Public Domain | 🟢低 | — | 🚫跳过 | whole-books上游；已下whole-books无需重复 |
| — | `alea-institute/kl3m-data`(系列) | ~16.9GB | 多子集 | 🔴低 | 🟡中 | 🟡已分词(非本线tokenizer) | 🟢低 | 🟡tokenizer兼容存疑 | 🚫跳过 | 法律/金融域不匹配；已用kl3m tokenizer分词 |
| — | `harborframework/terminal-bench-2` | N/A | — | N/A(评测) | — | — | — | — | 🚫跳过 | HF API 401 Not Found；待核正确repo名 |
| ⚠️ | `HuggingFaceCode/stack-v3-train` | 15.9TB | — | 🟢高 | 🟢高 | 🟢ODC-By/非gated/内联 | 🟡中 | 🔴≥1TB | ⚠️报运维 | 173M仓库内联；比v2实用；≥1TB需批；本轮不下 |

### G.2 跳过清单（3 源）

| repo_id | 跳过原因 | 建议 |
|:---|:---|:---|
| `common-pile/project_gutenberg_filtered` | whole-books 上游，已下 whole-books(25.3G) 无需重复 | 如需 raw gutenberg 可后置 |
| `alea-institute/kl3m-data`(系列) | 域不匹配(法律/金融)+已分词(kl3m tokenizer≠本线 tokenizer_eod) | 如需超长法律文书可单独评估原始文本版 |
| `harborframework/terminal-bench-2` | HF API 401 Not Found，repo 可能不存在或需特殊访问 | 待运维核实正确 repo 名 |

### G.3 ≥1TB 待批清单

| repo_id | 体量 | license | 理由 | 状态 |
|:---|---:|:---|:---|:---|
| `HuggingFaceCode/stack-v3-train` | 15.9 TB(train) | ODC-By | 173M仓库文件内联,天然仓库级长上下文;比v2(SWHID引用)更实用;非gated | ⚠️ 报运维批准(≥1TB不自行下) |
| `bigcode/the-stack-v2` | 67.5 TB(full)/32.1 TB(dedup) | gated+需SWH协议 | 🚫 运维令明确禁下 | 禁下(终态) |

### G.4 下载登记（进行中 → 完成后回填实测）

> 下载脚本：`run/data/roi_download_20261107.sh`（setsid 后台 PID=1920377，日志 `/tmp/data_download_roi_20261107.log`，状态 TSV `/tmp/data_download_roi_status.tsv`）。
> 纪律：`nice -n 10`、`--max-workers 4`、走代理 `HTTPS_PROXY=http://172.19.92.25:13128`、断点续传、不挤 S1。
> ⚠️ `zai-org/LongBench-v2` 为评测集——🚫 禁入训练，仅纳入去污染黑名单（与 EDA-Eval / SWE-bench Verified / ia03/terminal-bench 同闸）。
> ⚠️ `Nethraaaaa81/swev-trm-trajectories-25models` 高污染（直接用 SWE-bench Verified）——🚫 禁入 SFT，仅 TRM 训练/分析。
> ⚠️ `nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` 高污染（含 numpy/Pillow 等 SWE-bench 同源仓库）——下载后须去污染方可用于 RL。

| # | repo_id | 落盘路径 | 主机 | 文件数 | 字节(B) | GiB | gated | incomplete | 备注 |
|:---|:---|:---|:---|---:|---:|---:|:---|---:|:---|
| 1 | `utter-project/LongBlocks` | `/nas_inference/app.e0031982/datasets/utter-project/LongBlocks` | .12 | — | — | 9.57 | no | — | 多语言长上下文QA(CC BY-SA 4.0) |
| 2 | `nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` | `/nas_inference/app.e0031982/datasets/nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` | .12 | — | — | 5.10 | no | — | agentic SWE RL(CC-BY-4.0,🔴高污染) |
| 3 | `caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1` | `/nas_inference/app.e0031982/datasets/caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1` | .12 | — | — | 2.89 | no | — | 合成长上下文训练(1M样本) |
| 4 | `common-pile/arxiv_papers_filtered` | `/nas_inference/app.e0031982/datasets/common-pile/arxiv_papers_filtered` | .12 | — | — | 6.04 | no | — | arxiv论文全文(CC BY/SA/CC0) |
| 5 | `THUDM/LongWriter-6k` | `/nas_inference/app.e0031982/datasets/THUDM/LongWriter-6k` | .12 | — | — | 0.15 | no | — | 长输出生成SFT(6K) |
| 6 | `NovaSky-AI/SkyRL-v0-293-data` | `/nas_inference/app.e0031982/datasets/NovaSky-AI/SkyRL-v0-293-data` | .12 | — | — | 0.00 | no | — | RL验证(293 tasks) |
| 7 | `Nethraaaaa81/swev-trm-trajectories-25models` | `/nas_inference/app.e0031982/datasets/Nethraaaaa81/swev-trm-trajectories-25models` | .12 | — | — | 0.93 | no | — | SWE轨迹TRM(MIT,🔴高污染禁SFT) |
| 8 | `zai-org/LongBench-v2` | `/nas_inference/app.e0031982/datasets/zai-org/LongBench-v2` | .12 | — | — | 0.47 | no | — | ⚠️评测集仅去污染禁入训练 |
| **合计** | **8 源** | | | **—** | **—** | **~25.15** | | **—** | 全部公开 non-gated；含2个需去污染(1评测+1高污染轨迹) |

> 📌 本节文件数/字节为 HF API 预估值，下载完成后以 `du -sb` + `find -type f | wc -l` + `find -name '*.incomplete' | wc -l` 三项实测回填。
> 🚫 token 不得写入本表/日报/任何 commit（运维令 08:5x ④）。

