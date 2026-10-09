# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_DATA.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_DATA.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。

> 📦 §运维指令·昨夜汇报HTML（2026-10-07）已执行完毕 → report_10_07_data_overnight.html 已交付；详细指令已归档 → run/ARCHIVE_OPERATOR_DATA.md。需要时再读。

> 📦 §运维指令·2026-10-08论文更新（§4 Data Mixture Search+§5 SFT/污染, main.pdf 9pp 0err, commit cbe0b641）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：4_llm_pretrain.tex+5_llm_posttrain.tex已更新,main.pdf编译0err,commit cbe0b641→debb3260。需要时再读。

> 📦 §运维指令·2026-10-08数据准备全链路状态报告HTML（report_data_pipeline_status.html 31KB）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：8节全链路报告已交付,含TL;DR/数据全景/下载/分词/配比/污染/磁盘/下一步。需要时再读。

> 📦 §运维指令·2026-10-07⑥配比实验收官总报告HTML（report_data_mix_summary.html 29KB）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：R1→s_step→R2→top-K全弧线报告已交付,ρ=−0.80排名反转+0.6pp不可分辨+88:8:4先验。需要时再读。


### 🆕🆕 运维指令 · 2026-10-09②（**修正①：全量口径扩大至所有已下载数据 —— 用户直令「绝不偷工减料」**）· **用户直令** · 最高优先 · 覆盖①

> **用户直令（2026-10-09②）**：「没人说P-8需要多少数据，要我看MiniCPM5用多少，P-8就训多少。请绝对不要偷工减料，下载多少，分词多少！！」
>
> **①指令的三个严重错误（已作废）**：
> 1. **6.76B/4.36B 是运维自己编的**，不是用户要求，不是 MiniCPM5 规格——**全部删除，永不引用**。
> 2. **Code 只给了 L3 路径（560 parquet / 564GB），遗漏了 L2（561 parquet / 570GB）**——一半 Code 数据没切。
> 3. **Math 只给了 L1 路径（1485 parquet / 342GB），遗漏了 L2-preview（138 parquet / 59GB）+ L3（200 parquet / 115GB）**。
>
> **MiniCPM5 训练数据（P-8 参考基准，来源：HF 模型卡 + arXiv 2602.09003）**：
> MiniCPM5-2B 的 base/mid 训练数据 = **Ultra-FineWeb + Ultra-FineWeb-L3 + UltraX-Preview + UltraData-Code（L2+L3）+ UltraData-Math（L1+L2+L3）**。
> - UltraData-Code：L2 ≈400B tok + L3 ≈150B tok
> - Ultra-FineWeb-L3：≈690B tok（en 467B + zh 223B）
> - 后训练 SFT：400B tok（UltraData-SFT-2605，Stage(ii) 不在本轮）
> - **P-8 与 MiniCPM5 同源同量，用多少切多少。**
>
> **已落盘数据全量清单（下载了多少，就分词多少）**：

| 数据源 | 层级 | parquet 数 | 磁盘 | 已分词? | 落盘命名 |
|:---|:---|---:|---:|:---:|:---|
| Ultra-FineWeb base en | — | 2048 | 2.66TB | ✅ s24-s33 | `*_s{24..33}` |
| Ultra-FineWeb base zh | — | 256 | 301GB | ✅ s4-s11 | `*_s{4..11}` |
| Ultra-FineWeb-L1 en_hq | — | 6000 | 478GB | ✅ s12-s23 | `*_s{12..23}` |
| Ultra-FineWeb base subset | — | 48 | — | ✅ s0-s3 | `*_s{0..3}` |
| UltraX-Preview | — | 479 | — | ✅ s34-s43 | `*_s{34..43}` |
| **Ultra-FineWeb-L3 en_qa** | — | 616 | — | ❌ **NEW** | `l3_en_qa_s{i}` |
| **Ultra-FineWeb-L3 en_multi** | — | 552 | — | ❌ **NEW** | `l3_en_multi_s{i}` |
| **Ultra-FineWeb-L3 zh_qa** | — | 310 | — | ❌ **NEW** | `l3_zh_qa_s{i}` |
| **Ultra-FineWeb-L3 zh_multi** | — | 286 | — | ❌ **NEW** | `l3_zh_multi_s{i}` |
| **UltraData-Code L2** | L2 | 561 | 570GB | ❌ **NEW** | `code_l2_s{i}` |
| UltraData-Code L3 | L3 | 560 | 564GB | 🔄 s0-s10 跑中 | `code_s{i}` |
| UltraData-Math L1 | L1 | 1485 | 342GB | 🔄 s0-s3 跑中 | `math_s{i}` |
| **UltraData-Math L2-preview** | L2 | 138 | 59GB | ❌ **NEW** | `math_l2_s{i}` |
| **UltraData-Math L3** | L3 | 200 | 115GB | ❌ **NEW** | `math_l3_s{i}` |
| **合计待新增** | | **2749** | **~3.1TB** | | |

> **口径（覆盖①一切旧写法）**：**下载了多少 parquet 就分词多少 parquet——全量 = 切完所有已落盘的原始文件，绝不偷工减料，不跳过、不采样、不截断、不设 token 上限/下限。** ①已启动的 Code-L3（7进程）和 Math-L1（4进程）继续跑，**本指令新增所有 ❌ NEW 部分。**

**① UltraData-Code 全量分词 = L2 + L3（合计 1121 parquet / ~1.13TB）**

- **L3（已在跑，保持不动）**：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3/`（560 parquet / 564GB / 11 语言：py/cpp/js/cs/go/java/php/rb/rs/r/sh）→ 当前 code_s0–s10 继续
- **L2（本指令新增，立即启动）**：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L2/`（561 parquet / 570GB / 11 语言：py/cpp/js/cs/go/java/php/rb/rust/r/sh）
  - **落盘** = `/nas_train/app.e0031982/datasets/baize-data/text/`，命名 `code_l2_s{i}.bin/.idx/.json`
  - **分词口径**：同 L3 — tokenizer=`tokenizer_eod` / `--mode content --text-column full_content` / Megatron-LM `.bin/.idx/.json` / **不入 git**
  - **并行化**：按语言子目录分片（11 语言 → 7–11 进程），`setsid nohup` + `nice -n 10`；起步 N=min(8, nproc/4)，盯 GPIC 速率不掉

**② UltraData-Math 全量分词 = L1 + L2-preview + L3（合计 1823 parquet / ~516GB）**

- **L1（已在跑，保持不动）**：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L1/CC-MAIN-*/`（1485 parquet / 342GB / 99 CC-MAIN shards）→ 当前 math_s0–s3 继续
- **L2-preview（本指令新增）**：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L2-preview/`（138 parquet / 59GB）
  - **落盘** = `math_l2_s{i}.bin/.idx/.json` / `--mode content --text-column content` / `nice -n 10`
- **L3（本指令新增）**：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L3/`（200 parquet / 115GB / 4 子目录：Conversation-Synthetic / Multi-Style-Synthetic / QA-Synthetic / Textbook-Exercise-Synthetic）
  - **落盘** = `math_l3_s{i}.bin/.idx/.json`
  - **分词口径**：先 smoke test 1 parquet 确认 text column（可能 `content` 或 `text`），再批量切
  - **并行化**：4 子目录 → 4 进程起步

**③ Ultra-FineWeb-L3 全量分词（1764 parquet / 1.8TB / ~690B token —— ①完全遗漏，MiniCPM5 base 训练核心数据）**

> ⚠️ **这是最大遗漏**：Ultra-FineWeb-L3 是 MiniCPM5 base/mid 训练核心数据源之一（≈690B token），已在盘上 1764 parquet / 1.8TB，①完全没提。

- **原始数据路径**：`/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/`
  - `ultrafineweb_en_l3/qa/`（616 parquet）→ `l3_en_qa_s{i}`
  - `ultrafineweb_en_l3/multi_style/`（552 parquet）→ `l3_en_multi_s{i}`
  - `ultrafineweb_zh_l3/qa/`（310 parquet）→ `l3_zh_qa_s{i}`
  - `ultrafineweb_zh_l3/multi_style/`（286 parquet）→ `l3_zh_multi_s{i}`
  - 合计 1764 parquet / 1.8TB / ≈690B token
- **分词口径**：与既有 web shards（en_base / zh / l1_en_hq / ultrax）完全一致 — tokenizer=`tokenizer_eod` / `--mode content` / 先 smoke test 确认 text column
  - **落盘** = `/nas_train/app.e0031982/datasets/baize-data/text/`，命名如上
- **并行化**：4 config 各开 2–4 进程起步（en_qa 616→4进程；en_multi 552→4；zh_qa 310→2；zh_multi 286→2），同 ① 并发策略

**④ 投料前污染扫描（所有分词完成后做）**
- 对所有新分词产物（Code L2+L3 / Math L1+L2+L3 / L3 web）跑 `check_contamination.py`（blacklist = 6 快照并集 536 任务 / 193,295 13-gram + 10 8-gram）
- 采样 ≥ 10K docs / 源 → 0 命中则可投料
- 结果写入 `CONTAMINATION_CHECK.md`

**⑤ 报告要求（每唤醒心跳必报）**
- Code L3：`code_s{i} 进度，X 亿 tok，活 PID，ETA`（已有）
- Code L2：`code_l2_s{i} 进度，X 亿 tok，活 PID，ETA`（新增）
- Math L1：`math_s{i} 进度，X 亿 tok，活 PID，ETA`（已有）
- Math L2-preview：`math_l2_s{i} 进度，X 亿 tok，ETA`（新增）
- Math L3：`math_l3_s{i} 进度，X 亿 tok，ETA`（新增）
- L3 web：`l3_{en|zh}_{qa|multi}_s{i} 进度，X 亿 tok，ETA`（新增）
- GPIC 下载：照常报
- **分词全部完成后**：报「Code L2+L3 X.B tok / Math L1+L2+L3 Y.B tok / L3 web Z.B tok / web 已有 524.42B / **合计 W.B tok** / P-8 数据层全就绪」→ 运维将评估 P-8 启动

**⑥ 铁律（不变）**
- 🚫 不 kill GPIC 下载（PID 144981 保持运行）
- 🚫 不改 tokenizer / 不改 .bin/.idx 格式
- 🚫 不入 git（.bin/.idx/.json 产物不入库）
- 分词用 `nice -n 10`，GPIC 下载优先级更高
- 心跳 ≤ 60 min 且每步 commit + push
- 🚫 **绝不偷工减料**：每个 parquet 文件都要切完，不跳过、不采样、不截断、不设上限/下限
- TASK/MEMORY ≤ 32KB

**⑥ 优先级排序**：本块 **最高优先** → GPIC 续下（照常）→ en_v1_4 排队（不启动）
- Code/Math 分词 **可与 GPIC 下载并行**（分词 = CPU + NFS read，GPIC = NFS write + 网络，I/O 模式不同）

> 📦 体积提醒：本块加入后 `BAIZE_DATA_TASK.md` ≈ 33KB → 若超 32KB，**先把已闭合的旧块（如 2026-10-07④ UltraX 续传块，已执行完毕）归档**到 `run/ARCHIVE_OPERATOR_DATA.md`（留 1 行指针），**不得删改/精简本块**。


### 🆕 运维指令 · 2026-10-07⑤（**① 分词加大并发（太慢）② `.29` 8 卡已空的口径 ③ 配比实验后的推进顺序**）· **用户直令** · 最高优先

> **用户直令（2026-10-07 21:2x）**：①「**base 分词太慢，需要加大并发**」；②「**配比实验结束，`.29` 的卡空出来了吧？**」

**① 分词加大并发（本轮立刻做）**
- **现状确认太慢**：`zh` 分词 **单进程 @99% CPU**（PID 2851334），**file 33/256，ETA ~2.5 天**。
- **做法**：**并行化 = N 个 `preprocess_data.py`，每个吃 parquet 的一个子集，各自产出 `s{i}.bin/.idx`**（沿用既有 shard 命名/格式，**最后合并或直接进 blend 列表**）；🚫 **不改 `.bin/.idx` 格式、不改 tokenizer**（仍是 `tokenizer_eod`）。
- **先测再定 N**：`nproc` + `cat /proc/loadavg` + `uptime` + 观察 NFS 吞吐 → **起步 `N = min(8, nproc/2)`**，跑 ~10 min 看 load/吞吐，**再逐级加**；**目标：zh 分词 ETA 从 ~2.5 天压到 ≤12 h**。
- ⚠️ **护栏**：① **BO 已结束**（`.29` 空）⇒ **不必再为 BO 让路**；② 但 **GPIC 下载仍在 I/O** ⇒ **别把 NFS 打满**（盯 GPIC 速率是否掉）；③ `nice` 可放宽到 **-n 10**（不必再 19）；④ `setsid nohup` + log + 心跳报「已跑 file 数 / tok·s⁻¹ / 每进程吞吐」。
- **报**：nproc / 采用的 N / 每进程实测吞吐 / 合并后 **zh 总 token 数** / 新 ETA。

**② `.29` 8 卡已空（口径）**
- **已核验**：**`.29` 8×0 MiB / 0%**（pretrain #176 ssh 实测）⇒ **`.29` 现在对 data 也空闲**。
- 若 data 日后要用 `.29` 的 GPU（如更大规模复算）⇒ **先登记**（`run/GPU29_ALLOC.md`，无则新建），**避免与 pretrain 新任务（今晚 T1/T2 要跑 `.29`）相撞**。

**③ 配比实验交付后的推进顺序**
1. **分词并发化**（本块①）→ **先切完 `zh`**，再 **`l1_en_hq` 分词**（6000 parquet）→ 目标 **P-8 所需 ~100B tok**（现 22.05B）；
2. **GPIC** 续下至 **8001**（ETA ~2.7 天）；
3. **`en_v1_4`** 继续排队（**不启动**，直到 GPIC 下完或运维放行）；
4. 新分词产物**正式投料前必须过 `check_contamination.py`**（与 EDA-Eval 158 任务不同源 + 跨集去重）。
> 📦 体积提醒：本块加入后 `BAIZE_DATA_TASK.md` ≈33KB ⇒ 若超 32KB，**收尾前先把已闭合旧块归档**（确切字节以你自己 `wc -c` 为准）。


> 📦 §运维指令·2026-10-07④（撤销定时停UltraX+续传下完479/479+GPIC让回）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：UltraX✅479/479全下完,GPIC恢复全速,en_v1_4继续排队。需要时再读。

> 📦 §运维指令·2026-10-07③（GPIC优先序裁定+BO方向核对）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：①GPIC优先序被④块作废(改为UltraX续传到底) ②BO方向bug=报告bug非code bug,TRUE best=t23(0.4155),t75(0.373)=MIN,R1 ρ=−0.43不受影响,已创建query_bo_r2.py。需要时再读。


> 📦 §运维指令·2026-10-07②（解除白名单锁定：UltraX-Preview下载+en_v1_4排队+分词）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：UltraX下载已启动(唤醒186)+zh分词已启动+en_v1_4排队；唤醒192续传重启UltraX。白名单新增UltraX-Preview+en_v1_4（用户主动解禁）。需要时再读。


### 🚨 运维指令 · 2026-10-07（**P0 · 两条下载线（base + GPIC）继续 / 立即重启 —— 正文口径统一为「数据下载失败需主动重启」**）· **最高优先 · 用户直令**

> **用户 2026-10-07 直令**：**data 的两条数据下载线必须继续跑** —— **base 死了 / 僵死就重启**，**从来没有过「拖着不动」的指令**（用户原话逐字见 `run/ARCHIVE_OPERATOR_DATA.md`「2026-10-07 口径修正」块）。
> ⇒ ① **两条下载线必须持续在跑**：**base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）+ **GPIC**；② **从来没有过「base 死了就拖着不动」的指令** —— 你心跳里连写的 `Base 下载: 进程已死（按指令保持不动）` 属**误读**，**立即废止该口径**。

> 🔍 **误读溯源（运维自查，如实说）**：旧第 36 行那句 `🚫 不改白名单 / 不动下载`，本是 **2026-10-03 白名单锁定时的巡检纪律**，原意 =「**不要擅自改白名单、不要乱动［健康的］下载**」，**不是**「下载失败也不许重启」。2026-10-06 15:1x **用户已直令重启 base**，那个 **P0 块**处置完后被归档进 `ARCHIVE_OPERATOR_DATA.md`（唤醒 167）⇒ **正文只剩「不动」半句，重启授权随归档一并消失**。**表述缺陷在运维，不在你。** 完整溯源（含用户原话 + 被替换掉的旧字句原文）见归档「口径修正 · 2026-10-07」块。
> ✅ **永久口径（即刻生效，覆盖旧表述）**：**数据下载失败需主动重启** —— **白名单内任一下载「失败 / 僵死 / 速率趋零 / PID 已死」⇒ 立即 `kill`（若还在）+ 重启**（沿用既有 retry-loop 规程），报告里标「**已重启**」+ 新 PID；**不再需要等运维点名**。
> 🚫 该条纪律**今后只剩一种含义**：**不改白名单、不起白名单外的新下载**；**白名单内下载失败 ⇒ 按「数据下载失败需主动重启」处理，不许再写「保持不动」**。

> **本轮唤醒内做完（不许拖到下轮）**：
> 1. **取证**：`ps -ef | grep -Ei 'hf download|huggingface-cli|hf_transfer|download_it_pairs'`（留原文）+ 两目录 `.incomplete` 计数 + 最新 mtime。
> 2. **重启 base**（`l1_en_hq` 停在 **5476/6006 ≈91%**、`zh` **✅ 256/256 已满**）：
>    - `--include 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*'`（**config 级**）；🚫 **绝不拉 `en_v1_4`**；
>    - **retry-loop 包裹**（失败 `sleep 30` 自愈 —— 你 2026-10-04 唤醒 85 用过、有效）+ `setsid nohup`（`ppid=1`）+ log `Ultra-FineWeb/download_l1_zh.log`；
>    - ⚠️ 外网命令**显式带 proxy**（`.12` 用你 `~/.bashrc` 里的那个值）；
>    - **命令原文 + 首次输出（起步 part 号）贴心跳**。
> 3. **GPIC 判活**（PID / `gpic_train_XXXX.tar` mtime / 24h 新增 tar 数）→ **死即重启**（父 `download_it_pairs.sh` 一并核）；目标 **8001 tar** + test 128 ✓。
> 4. **心跳格式（本轮起固定写一行）**：`下载线：base l1_en_hq <n>/6006（+Δ, 活/已重启 PID, ETA）· zh ✅256/256 | GPIC <n>/8001（+Δ, 活/已重启 PID, ETA）`。
> 5. **P-8 关联（为什么急）**：base = **P-8（Stage (i) 本体）硬前置**（已分词仅 **22.05B tok**，P-8 需 ~100B）⇒ **base 下满即解锁 P-8 备料**；`l1_en_hq` + `zh` 双满 ⇒ **报运维「MiniCPM5 base 族就绪」**。

> **纪律（不变）**：🚫 不 kill 正在跑的 BO；🚫 不在 pretrain 释放前碰 GPU0-1；🚫 重 I/O 与 `.29` 抢 `/nas_train`；心跳 ≤60 min 且每步 commit + push；`TASK/MEMORY` ≤32KB。

---
> 📦 §运维问询·2026-10-07（三个现状问题）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：三问已答(唤醒185)①GPIC无加速②base下载全满只剩分词③BO变慢=波次锯齿非I/O。需要时再读。


> 📦 §📎 运维转发·R1 lm_eval结论更正（2026-10-07）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：名次方向bug+ρ符号+表格错字+结论改"代理无分辨力+证据不足"全部落地✅(唤醒181)。R2收尾操作提醒(§⑤)仍在归档中,收尾时需读。需要时再读。


> 📦 §运维指令·2026-10-06三步令（①200trial+top-K ②s_step归因 ③Round2 BO）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：三步全完成✅(①200trial+Spearman ρ=−0.43 ②MBS16→s_step 166ms=8.6×,D=0.5B ③Round2 200/200+top-K lm_eval ρ=−0.80)。需要时再读。

> 📦 §P0 base下载重启（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：base下载已重启(PID 3520692,l1_en_hq 89%+zh✅256/256),proxy=172.19.92.25:13128,白名单不变。需要时再读。


> 📦 §目标函数错了（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：6项全执行✅(Round2用lm_eval 8集均分作objective, Spearman ρ=−0.43证实loss≠能力)。需要时再读。


### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> 📦 §运维规程·agent归档（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：agent自滚MEMORY+任务书,判据≤32KB/红线40KB,做法=只搬迁留指针（与「体积维护规程」同口径）。需要时再读。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> 📦 §收尾铁律·事故背景（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：心跳2h未更新致误判卡死→立「每轮必commit+push」硬约束。需要时再读。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_DATA.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_DATA.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_DATA.md` 顶部进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories-data/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**，不许攒着最后补）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md doc/BaiZe-ISEDA2027/run/DATA_LEDGER.md \
              doc/BaiZe-ISEDA2027/run/CONTAMINATION_CHECK.md doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md \
              doc/BaiZe-ISEDA2027/run/DATA_MIX_RECIPE.md doc/BaiZe-ISEDA2027/run/DISK_CLEANUP_INVENTORY.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-data doc/BaiZe-ISEDA2027/run/data_pipeline
   git commit -m "data <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已因此出过事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**（派人上机 kill / 重排卡），**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**

> 📦 §第5轮·代理规模定案 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：d=128/L=14/N≈18.5M定案+5项必验全PASS+评测硬规则+第0步分工,详见各子指针。需要时再读。

> 📦 §用户复核② 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：5条判据(BO 200/200已满足)+先验88:8:4对照(进行中,见三步令①)+心跳纪律(已由收尾铁律覆盖)。需要时再读。

---

> 📦 §运维指令·2026-10-06配比实验改道（小代理+BO搜索空间/目标函数/交付§④⑤⑥）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：改道执行✅,BO R1+R2全完成,搜索空间/objective/交付已落地。需要时再读。

---

> 📦 §运维指令 · 2026-10-05（HTML报告 + D-CLEAN-4 定案 + 环境隔离）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：report_data_mix_s0a.html 已产出（已废弃）、D-CLEAN-4 保留不动、环境隔离纪律见 proxy 口径块。需要时再读。


### 🆕 运维口径 · 2026-10-05（**你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测**）

> 📦 §proxy口径·定位与反证段（2026-10-05）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：loop剥代理致外网不可达是预期→外网命令显式带proxy(见下方用法)。需要时再读。
> 🔧 **正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）**：**凡访问外网的那一条命令，自己显式带上代理**（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都**不要**带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> 🚫 **装包别动共享 py310 env**（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令 · 2026-10-05（分卡协调 GPU2-7）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：GPU2-7 归 data、配比实验已开工。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 📦 §体积维护规程·理由段（2026-10-03~06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：TASK/MEMORY每次唤醒全文读入→越大约烧token→≤32KB硬约束。需要时再读。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_DATA.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_DATA_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成的**调研轮次原文** → 沿用 `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md` 等；
  ④ 较早的**唤醒流水**（保留最近 ~20 条） → `daily-memories-data/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有「见 §③.9」「上方块」这类交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 「进度快照」③ 「运维问答」（**这一区不清**，运维靠它读答复）④ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---


| 项 | 当前值 |
|:---|:---|
| **🆕 下载白名单（2026-10-03 最新 · 覆盖一切下载类指令）** | **只下 ① `ultrafineweb_l1_en_hq` + `ultrafineweb_zh`（base 族剩余）② GPIC**；🔴 **立即停 `ultrafineweb_en_v1_4`**（43 天 / 非必需 / 阻塞后两项）；🚫 **白名单外一律不下载、不调研、不推荐**（含 `UltraX-Preview`）→ 详见顶部「运维指令 · 2026-10-03（下载白名单锁定）」 |
| **历史指令** | 📦 D-CLEAN-4/当前指令/优先级覆盖/状态索取/暂停标志（2026-10-01~04）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：全部已闭合/被运维指令区新块取代（配比实验改道为BO搜索，见上方活跃块）。需要时再读。 |

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

> 📦 §0「当前主攻」+ §0.6「R4阶段 P-8 数据配方」（2026-10-02）已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：R/R2 调研完成、配比实验已改道为小代理+BO（见运维指令区改道方案块）。需要时再读。
---
## 1. 任务目标

把已在盘上的原始语料，变成**训练可直接消费、配比正确、且不污染评测集**的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ **← 🚫 已取消**（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. **污染隔离白/黑名单 + 校验脚本（红线，P0）**

**上游方案文档（先读它）**：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
**时间线约束**：ISEDA 2027 投稿截止 ≈ **2027-02-01**；本任务必须在 **2026-11 底**前可交接（见方案 §6）。

> **注意本任务的定位**：瓶颈是**算力窗口**不是数据量（方案 §2.1）。
> 所以**不要**把精力花在"下载/切分更多数据"上，而要花在**质量、配比、格式可用性、隔离**上。

> 📦 §1.1「数据落盘地图」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：实测数据位置详见 DATA_LEDGER.md。需要时再读。

> 📦 §2「阶段与推荐执行顺序」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：R/phase0/phase5 完成，当前主攻=配比实验（见运维指令区）。需要时再读。

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

> 📦 §4「git 与共享工作区规则」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：git 规程见「收尾铁律」§3 + AGENTS.md §4。需要时再读。

## 5. 资源与约束
> 📦 §5「资源与约束」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：常驻 .12、GPU2-7 归 data（见运维指令区）、重 I/O 避让。需要时再读。


## 6. 记忆管理

| 文件 | 作用 |
|:---|:---|
| `run/MEMORY_DATA.md` | 运行时状态：**顶部"进度快照"**（固定格式，供远程巡检）+ PHASE/WAITING/看板/流水 |
| **`run/DATA_RESEARCH.md`** | 🎯 **调研报告（当前主攻）**：只回答两个问题（LLM / Vision 的数据够不够 + 配比），每条含 URL / 规模 / 许可 / 可得性 / 建议 |
| `run/DATA_LEDGER.md` | **数据清单**（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | **污染隔离报告**（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 **`DATA_RESEARCH.md`（调研报告，当前主攻）** —— **两个问题各四小项全部有结论**，每条关键结论可顺 URL 复核
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
