# BAIZE_DATA_TASK.md

### 🚨 2026-10-30 22:2x 运维直令：恢复 85M 下载 + `/nas_train` 大目录清理盘点 · 最高优先

> **用户令**：「data: 恢复下载 85M，看看 /nas_train 有哪些大目录可以删掉」

**A. 恢复 85M 下载（先交活，再记账）**
1. 探针 4 条（proxy `.23` / hf-mirror、目标 repo、剩余 shard、磁盘余量）→ 按 A/B/C 分支起下载。
2. **判活按字节增长**（不看进程存活）：连续 3 次 `du -sb` 递增、无 `.incomplete` 堆积。
3. 回报：已下/总量、实测 MB/s、ETA、失败 shard 名单（原文）。

**B. `/nas_train` 大目录盘点 + 可删候选表**
1. `du -x --max-depth=2 -h /nas_train 2>/dev/null | sort -h | tail -40` + `df -h /nas_train`。
2. 对 top-20 目录逐项给：表观（`du -sh`）/ 实占（`du -sb`）/ 文件数 + 抽样 `ls -li` 看 inode 硬链接数 / 是否已被镜像收录（对照 `INDEX.tsv`）/ 归属（`full_*` / `tokenized` / 下载 parquet / staging / 旧日志 / 孤儿）。
3. 产出 `run/data/cleanup_candidates_YYYYMMDD.tsv`：path、表观、实占、inode、判定（可删/保留/待定）、证据命令。
4. **红线不变**：`full_*`、`tokenized/`、`INDEX.tsv`、`DATA_LEDGER.md`、下载 parquet **一律不可删**；本轮**只出候选清单，不执行删除**（等运维批准）。
5. `DATA_MAPPING.md` 增设「可删候选」节（只列清单与合计；🚫 把表观当实占）。

**判据**：85M 有字节增长 + 候选表每行都有判定与证据命令；本轮不删任何数据。



> 🧷 **行动优先纪律（2026-10-25 13:4x 用户令 · 覆盖一切归档/收尾/铁律类条文）**
> 用户原话：「放开这些什么禁制、铁律什么的。」
> 1. **先把活干出来，再谈记录**：本轮有未完成指令时，**先交付**（文件落盘/进程起来），心跳、日报、归档都排在交付之后。
> 2. **未完成指令不许归档**；归档是清理，不是交付物。有未完成指令 ⇒ `WAITING: 0`（loop 60s 后再唤醒），不许睡 30 分钟。
> 3. **体积不作挡箭牌**：任务书 ≤40KB 即可干活；>40KB 才需归档已闭合块。**不许因为体积/归档/心跳而推迟交付。**
> 4. 心跳必须写 `未完成指令：<有/无>`。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

> ⚠️ 本文件由运维维护；agent 可【归档已闭合块】与【追加执行记录】（原文不改、不新增运维令），除此之外不改写正文。

> 🆕 §运维令·2026-10-28 10:1x（**暂停下载**）· 用户直令 · 最高优先

> 用户原话：「让 data 把下载暂停一下。」
> **任务**：
> 1. **立即暂停当前所有下载进程**：含 `download_85m_parallel16.sh`（`hf download mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M`）及其子进程等，全部停掉。
> 2. **恢复前不再发起任何新的下载 / 迁移等重 I/O 操作**，直到收到「恢复下载」新令。
> 3. 给 pretrain 的 pre-blend（.12/.29 并发、将写 ~6TB）让出 IO/磁盘/带宽。
> **判据**：`pgrep -af "hf download|download_.*\.sh|rsync|wget|aria2"` 无活跃下载/迁移进程。

> 🆕 §运维令·2026-10-27 13:3x（**分词 SFT-2605 + Agent-2609 到 /nas_env，纳入映射镜像同等对待**）· 用户直令 · 最高优先

> 用户原话：「data：分词 UltraData-SFT-2605 和 UltraData-SFT-Agent-2609，分词产物放置在 /nas_env。更新 run/data/DATA_MAPPING.md 和 reports/report_data_mapping_zh.html，把它们俩跟其它 10 个 MiniCPM5 数据同等对待。」

**任务**（当前 DATA_MAPPING.md 行 11-12 状态=「未分词」；这俩是 Decay 段 SFT 配比数据，pretrain 已阻塞等它）：
1. **分词两个 SFT 源**（复用现有 SFT 分词管线）：
   - `UltraData-SFT-2605/data/`（1504 jsonl：no_think 855 + think 649；下载 318.99 GB）→ 用 `convert_sft_to_parquet.py`（JSONL chat→parquet content 列）+ `preprocess_data.py --mode content` 产出 .bin/.idx。
   - `UltraData-SFT-Agent-2609/data/`（50 jsonl：Code_Agent 7 / General_Agent 32 / Search_Agent 2 / Tool_Use 9；下载 54.22 GB）→ 同理转 parquet→分词；⚠️ Agent 类含 tool_call/assistant 结构，转换逻辑须适配并留证据（tool call 如何序列化进 content、是否丢字段）。
2. **分词产物放 `/nas_env`**：与其余 9 源 `full_*` 同盘同口径；`tokenized/` 镜像建 symlink 指向 /nas_env（storage=symlink，与行 2-10 一致）。
3. **纳入镜像 + 刷新两文件（同等对待）**：`build_tokenized_mirror.py` 刷新 `INDEX.tsv`（triplet=OK/inode_ok）→ 重跑 `gen_data_mapping_md.py`（行 11-12 状态→「镜像完整」，补 .bin/.idx/.json 数 + tokens + 字节）→ 重跑 `gen_report_data_mapping_html.py` 刷新 `report_data_mapping_zh.html`（A 节由 10 镜像源变 12 镜像源，合计 shard/字节/tokens 随之更新）。
4. **判据**：两源 triplet/inode 全 OK、0 悬空链接、合计行自动求和无误差；两文件一起 commit + push（前缀 `data tokenize:` 或 `data report:`），心跳报两源新 tokens/字节 + 两文件新大小。

> 🆕 §运维令·2026-10-27 08:3x（**刷新 DATA_MAPPING.md + report_data_mapping_zh.html**）· 用户直令 · 最高优先

> 用户原话：「data：刷新 run/data/DATA_MAPPING.md 和 reports/report_data_mapping_zh.html」
> **任务**（迁移 4 源已完成，把两个文件刷到最新 symlink 状态）：
> 1. 重跑 `gen_data_mapping_md.py` → 刷新 `run/data/DATA_MAPPING.md`（9 源 storage=symlink 指向 /nas_env、字节/tokens 最新、SFT-2605/Agent-2609「未分词」行保留）。
> 2. 重跑报告生成脚本（`gen_report_data_mapping_html.py` 或等价）→ 刷新 `reports/report_data_mapping_zh.html`（列表数字同步迁移后状态，df /nas_env 83%/nas_train 84%）。
> 3. 两文件一起 commit + push（前缀 `data report:`），心跳报两文件新字节数。

> 📦 §运维令·2026-10-26 14:4x（SFT-2605/Agent-2609 加入映射表+报告；删报告第 4 节）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：两份均未分词(0 .bin/.idx/.json)→DATA_MAPPING.md 行11-12如实登记「未分词」(SFT-2605=1504jsonl/297GB,Agent-2609=50jsonl/50GB)+报告加行11-12+删第4节(节号顺延5→4)+untokenized_sft_sources.tsv侧车+gen_data_mapping_md.py改load_untokenized，commit 86431cfb4 data report:。需要时再读。

> 🆕 §运维令·2026-10-26 13:1x（**迁移 4 份新分词数据到 /nas_env**）· 用户直令 · 最高优先

> 用户原话：「data: 把 ufw_en（ultrafineweb_en）、ufw_l1_en_hq（ultrafineweb_l1_en_hq）、ufw_zh（ultrafineweb_zh）、UltraX-AICC 这四份数据也迁移到 /nas_env 去。」
> **任务**：把这 4 份已分词数据迁到 `/nas_env`，方式与之前迁移 5 源完全一致（复用 `migrate_to_nas_env_fast.sh`，bwlimit 300000 KiB/s、`--partial` + `flock` 单实例锁）。
> **迁移对象**（tokenized 镜像内的 4 个目录，131 shard ≈ 4.05TB）：
> - `tokenized/Ultra-FineWeb/ultrafineweb_en`（32）
> - `tokenized/Ultra-FineWeb/ultrafineweb_l1_en_hq`（94）
> - `tokenized/Ultra-FineWeb/ultrafineweb_zh`（4）
> - `tokenized/UltraX-Preview/UltraX-AICC`（1）
> **做法**：迁移底层数据 → `/nas_env`，tokenized/ 原路径改为 **symlink** 指向 /nas_env（镜像路径与 `INDEX.tsv` 逻辑不动）；迁移完成后 `gen_data_mapping_md.py` 重跑，`DATA_MAPPING.md` 的 storage 列同步为 symlink。
> **判据**：`df` 确认 `/nas_train` 释放 ~4TB、`/nas_env` 相应增长；`INDEX.tsv` triplet=OK、inode_ok 不变。🚫 迁移只在有锁单实例内跑、不重复迁、不得就地改在跑脚本。commit `data migrate:`。
> **⑤ 迁移完成后必须刷新并提交推送（用户补令）**：
> 1. 重跑 `gen_data_mapping_md.py` → 刷新 `run/data/DATA_MAPPING.md`（storage 列 = symlink、triplet/inode 更新）；
> 2. 基于新 `DATA_MAPPING.md` **重新生成** `reports/report_data_mapping_zh.html`（列表数字同步迁移后的状态）；
> 3. 两个文件一起 `git add` + commit + push（前缀 `data migrate:` 或 `data report:`）。

> 🆕 §运维令·2026-10-26 10:4x（**围绕 DATA_MAPPING.md 写数据情况列表报告**）· 用户直令 · 最高优先

> 用户原话：「那就让data写个报告，围绕DATA_MAPPING.md，列表讲清楚数据情况。」
> **任务**：写报告 `reports/report_data_mapping_zh.html`（自包含中文 HTML，内联样式）。
> **唯一数据源**：`run/data/DATA_MAPPING.md`（+ `tokenized/INDEX.tsv`，两者 mtime 均 09:52:38）。数字以它们为准，不另做 `du`/`find` 全树扫。
> **结构（列表讲清楚）**：
> 1. **总览行**：数据源总数、总 shard 数（=815）、总 tokens、总字节、磁盘占用（/nas_train + /nas_env 的 df）。
> 2. **逐源列表**（每个下载目录一行）：数据源 → 下载目录 → 分词镜像路径 → `.bin/.idx/.json` 数 → tokens → 字节 → **状态**（镜像完整/分词中/未分词/未映射/已删除）。
> 3. **重点列全 10 个已镜像源**（当前 DATA_MAPPING.md A 节 1–10 行，全部「镜像完整」）：en_v1_4(110)、ufw_en_l3(154)、Code-L2(141)、Code-L3(63)、Math-L1(149)、Math-L3(67)、**ufw_en(32)、ufw_l1_en_hq(94)、ufw_zh(4)、UltraX-AICC(1)**。
> 4. **其余状态源**（未分词/未映射/已删除/已废弃）单独一节列清。
> 5. **结论**：数据管线是否全部收尾就绪（当前应=全部镜像完整），还差什么收尾动作。
> 纪律：溯源到 DATA_MAPPING.md 行号；commit `data report:`。

> 🆕 §运维令·2026-10-26 09:5x（**提高未分词源的分词并发**）· 用户直令 · 最高优先

> 用户原话：「给 data 下发提高分词并发的指令」。
> **问题**：当前 `run_tokenize_untokenized.sh` 的 knee 校准把 `MAX_CONCURRENT` 收敛到 ~6（224 核只用了 ~6 核，CPU ~3%），分词巨慢（~18min/shard，ETA 深夜）。
> **动作（立即，先交付再写心跳）**：
> 1. kill 当前 `run_tokenize_untokenized.sh` 及其 `preprocess_data_cm.py` 子进程（脚本带 `flock` 锁 `/tmp/tokenize_untokenized.lock`，kill 后锁随进程释放）。
> 2. 用 `KNEE` 环境变量预设并发、跳过校准，重启：
>    ```bash
>    cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
>    KNEE=96 MAX_CONCURRENT=96 PARQUET_PER_SHARD=64 setsid -f nohup bash run_tokenize_untokenized.sh > /tmp/tokenize_untokenized_96.log 2>&1 &
>    ```
>    （脚本 Phase B 有 resume：`is_done` 跳过已完成 shard + `manifest/failed_shards` 续跑，安全，不会重复分词。）
> 3. 重启后观察：`done` 推进速率应明显快于 ~18min/shard；每轮报 `tokens/s`、`cpu%`、新 ETA。若 96 已撞 NFS 读 IO 瓶颈（tokens/s 不增反降）→ 回落到 **64** 并在心跳说明；若余量充足再升 128。
> 4. 判据：目标把「未分词 4 源」（done 97→131）的 ETA 从深夜提前到 **数小时内完成**。

> 🆕 §运维令·2026-10-26 08:2x（**写最近工作报告 · 中文 HTML**）· 用户直令 · 最高优先
> 用户原话：「关于最近的工作，安排 BaiZe 4个agent各自写一份报告。」
> **任务**：写本线（data）最近工作（10-20 起）总结报告 `reports/report_data_recent_work_zh.html`（自包含中文 HTML）。
> - 结构：① 本线定位 → ② 近期任务逐个 → ③ 关键数据速查表 → ④ 阻塞/待拍板 → ⑤ 下一步建议。
> - **必覆盖**：① en_v1_4 下载（暂停→恢复→**110/110 全源 2238.14B/8.88TB** 完成）；② 5 源全量分词（Code L3/Math L3/Code L2/UFW-L3/Math L1 = **574 shards / 1056.36B**）③ 迁移 5/5 源 → /nas_env + 软链接；④ prune/磁盘清理 + 85M 降优先级；⑤ 当前收尾的未分词 4 源（95/131）。
> - 数字溯源（log/json/manifest 文件:行）；commit `data report:`。

> 📦 §运维令·2026-10-24 18:1x（85M 降优先级 → 迁移提速）**已闭合**（迁移 5/5 源全 DONE，`migrate_to_nas_env_fast.sh` 已跑完）→ 原文归档 `run/ARCHIVE_OPERATOR_DATA.md`；**结论**：`--bwlimit` 50000→300000 KiB/s、新脚本带 `--partial`+`flock` 单实例锁、不得就地编辑在跑的脚本、不得起第二实例；85M 不再是任何前置条件。需要时再读。

> 📦 §运维指令·2026-10-24 16:1x（写"正在做的迁移"报告）**已闭合**（`reports/report_data_migration_nas_env_zh.html` 已交付，唤醒 637@17:39）→ 原文已归档 → `run/ARCHIVE_OPERATOR_DATA.md`。需要时再读。


> 📦 §运维指令·2026-10-24 08:4x（用户质询：分词5worker+85M线路）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：Q1=5worker因串行+剩余shard少(非硬编码),升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT);85M用parallel16+92.25续传。需要时再读。


> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区
> 📦 §运维令·2026-10-26 22:0x（修复坏shard env14_CC-MAIN-2023-23）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：已修复DONE(commit 1cfb5e7dd)。.bin截断49GB→从源parquet(512)重分词→新.bin 118.23GB/max_ptr<bin复验PASS→原子替换→mirror rebuild 815shard→DATA_MAPPING+report+LEDGER §7.2全量更新。env14 110/110全齐blender不SKIP。证据run/data/bad_shard_..._20261026.txt §8-9。需要时再读。

> 📦 §运维令·2026-10-25 22:3x（分词停顿2.6h诊断）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：done=95/131 FLAT系supervisor只计finalize的计数artifact非真停；/proc/io铁证36进程健康在写@1.65MB/s=412K tok/s/proc；处置=不杀；分词09:43:35全DONE 131/131。需要时再读。

> 📦 §运维令 2026-10-25 18:5x（DATA_MAPPING 脚本化 + 分批清理 + batch1 DONE）**已完成**（唤醒 657/674 交付：幂等生成器 + 候选清单 + batch1 实占 1.13MB + 清理记录侧车）→ 原文归档 ARCHIVE_OPERATOR_DATA.md。
### ⚖️ 口径仲裁（2026-10-25 13:3x · **与下文任何旧条冲突时，一律以本表为准**）
| 冲突点 | 旧说法 | **现在按这个做** |
|---|---|---|
| `env14_*` / `/nas_env/full_*`「不碰」 | 12:5x 块末写「不碰原件」 | 「不碰」= **不删 / 不改 / 不移动 / 不复制**；**允许**建 hardlink（同盘 env14）与 symlink（跨盘 `/nas_env`）用于新布局 |
| 报告能不能改 | 13:2x「停止一切报告工作」 | **结构冻结**（1 个 `<table>`、6 列、无解读段）；**内容允许**随实测更新——即按新 `tok_dir` 重跑生成器 |
| 新增分词落哪 | 11:0x「落 `baize-data/text/`」 | **一律落 `baize-data/tokenized/<镜像下载路径>/`**；`text/` 不再新增任何文件 |
| 前缀命名 | 11:0x `ufw_en_*` / `ultrax_*` | 12:5x 表为准：`ufw_en_s*` / `ufw_l1hq_s*` / `ufw_zh_s*` / `ultrax_aicc_s*` |
| 并发 | 2026-10-18「32 或 64 核」 | 12:5x 为准：**96/144/192/224 四档各 60s 标定**，取拐点，`workers=min(拐点,200)`，`nice -n 5` |
| 提交方式 | 收尾铁律「🚫 不用 `git add -A`」 | **已放开**：白名单 = `run/**` + `reports/**`；必要时允许 `-A`（仅本线路径） |
| 收尾铁律/体积 | 旧：≤32KB 必归档、`git add` 只许 8 个路径 | **已放开**：≤40KB 直接干活；体积**永不**优先于交付；归档只在 >40KB 时做 |
| 下载白名单 | 旧表：只许下 2 个源 | 只约束**新增下载**；**不约束**本轮分词与目录整理 |
| 目录命名 | 12:5x「路径镜像 HF 下载目录」写死 | **目录名不重要**：分词后允许自由改名；硬要求 = 映射表能一一对上且校验通过 |
| 盘点交付物 | 报告 HTML 为必交付 | **`run/data/DATA_MAPPING.md`（Markdown）为单一事实源**；HTML 报告 = 按需由 md 生成，不是必交付 |
| 32 uncovered shard | 待人工裁决（长期挂账、阻塞感） | **不阻塞**：映射表单列「未映射」节，逐条写证据与建议；未批准不许删 |

### [已归档] §运维令·2026-10-25 13:2x（停止一切报告工作，只做布局+分词两件事）**已完成**（布局 7896810a3、分词 94/131 在跑、报告已验收）-> 原文归档到 `run/ARCHIVE_OPERATOR_DATA.md`。需要时再读。

> 📦 §运维令·2026-10-25 12:5x（本轮执行顺序：①已分词布局镜像hardlink/symlink ②未分词4源开跑224核）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：①布局DONE(tokenized/镜像10目录/815shard/INDEX.tsv)+②分词DONE 131/131(09:43:35,1.18T/4.05TB)；口径仲裁表(本文件下方)仍为活口径不归档。需要时再读。


### 🧵 运维令 · 2026-10-25 11:0x（重盘盘点 + 对未分词开跑）· **已并入 12:0x 令，本条仅存档要点**
> 224 核是上限不是指标（4 档标定 64/96/128/192 取拐点，留余量给 85M）；分词器 `tokenizer_eod`（vocab 129,281 / pad 129,408）；落 `baize-data/tokenized/<镜像下载路径>/`（见仲裁表）；每前缀必须有 manifest（shard→源 parquet）；`setsid` 后台 + `/tmp/tokenize_untokenized_*.log` + `failed_shards.txt`；🚫 `/tmp`/`staging`/`*.orig` 不算源。

### 🗑 运维令 · 2026-10-25 10:3x（删不可对应产物）· **已执行完毕**
> 判定 110 shard → 删 78（被 `full_*` 覆盖，3.69 TiB）+ 删 32（不可与下载目录建立产物级对应，1.91 TiB，运维 RUN_ID 199）；`baize-data/text/` 现为 **110 shard / 2238.14 B / 8.93 TB（全 `env14_*`）**。清单 `run/data/prune_unmapped_*.txt|tsv|json`。

### 🚨 运维令 · 2026-10-25 08:0x（重写报告 v2）· **已闭合，被 12:0x 令取代**
> 原要点：以下载目录为准、一个下载目录一行、禁手填小计、未分词写「未实测」。v2 仍含漏源与小计错，且不是单表 ⇒ 12:0x 令要求整篇重写为「一张对应表」。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。


> 📦 §运维指令·2026-10-23 22:1x（复测 92.25 代理 / 恢复 85M / 分词产物体积 / 搬 /nas_env）**已闭合**（85M 已恢复并在降优先级后台跑，迁移 5/5 全 DONE）→ 原文归档 `run/ARCHIVE_OPERATOR_DATA.md`；**结论**：代理走 92.25+hf.co 直连；迁移铁律 = rsync -a 不用 mv、校验 shard+字节一致才删源、先建软链接、/nas_env 余量 ≥ 数据×1.1。需要时再读。

> 📦 §运维指令·2026-10-21 04:0x（MiniCPM5 全量数据完整分词·224核全开）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：5源全部分词完成（574 shards/1056.36B tokens/4.24TB），env14也完成（110/110/2238.14B/8.88TB）。迁移到/nas_env进行中。需要时再读。
> 📦 §运维指令·2026-10-20 15:5x（✅恢复en_v1_4下载）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：下载已恢复并运行中（PID1875054 alive,99/110dirs），kill+重启口径恢复，分词不受影响。需要时再读。

### 🗄 运维指令 · 2026-10-18 21:0x（en_v1_4 全量分词，不按 500B 截断）· **已闭合**
> 结论：env14 已 **110/110** 完成（2238.14 B tokens / 8.93 TB）；「32 或 64 核」是当时的限速口径，**已被 2026-10-25 12:5x 令的 96–224 四档标定取代**。原文归档 `run/ARCHIVE_OPERATOR_DATA.md`。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


> 📦 §运维指令·2026-10-18 10:2x（P0恢复git push）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：git push已修复（剥离HF代理执行：`env -u http_proxy -u https_proxy git push`），commit+push正常。需要时再读。

> 📦 §运维指令·2026-10-18②（.23+hf-mirror续en_v1_4最后25shard）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：25-shard续传已执行(下载现99/110dirs,.23+hf-mirror),en_v1_4分词由fullsource脚本接管(PID749330)。需要时再读。

### 🆕 运维指令 · 2026-10-17（🧹 清理本线 .12 /tmp 残留）· 用户直令
> 📦 已闭合（/tmp 清理已完成，残留=0）→ 原文 `daily-memories-data/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-15（⬇️ **补下 `UltraData-RL-2609`** + 复核 SFT-2605）· 用户直令 · 最高优先

> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§运维指令·2026-10-15（补下 RL-2609 + 复核 SFT-2605）」。
> **结论**：RL-2609 已下满并逐文件字节自校通过（20 jsonl / 174.75 GiB）；SFT-2605 复核通过（1504 jsonl / 0 incomplete），🚫 不需重下。需要时再读。


> **用户令（2026-10-15）**：「data：验证一下 `UltraData-SFT-2605`、`UltraData-RL-2609` 是否真的没有，没有就重新下载。」

### 🆕 运维指令 · 2026-10-14（▶️ 恢复全部 4 路下载 · 断点续传）· 用户直令 · 最高优先> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§运维指令·2026-10-14（恢复全部 4 路下载·断点续传）」。
> **结论**：WebMix-38M / InternVL-SA1B / wit_base 已下满；en_v1_4 由 2026-10-18（.23 + hf-mirror 续传）接管。需要时再读。

### 🆕 运维指令 · 2026-10-14（💾 新增下载落盘位置 `/nas_env`）· 用户直令 · 常驻> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§2026-10-14（新增落盘位置 `/nas_env`）」。常驻口径不变：`/nas_env` 仍为合法落盘地（仅用于新增下载）。需要时再读。

### 🆕 运维指令 · 2026-10-13（⏸ 暂停 85M + 📥 下载 HF 图文对 TOP-5 中「未下载」的 4 个 · 落 `/nas_inference` 或 `/nas_user` 的 datasets（🚫 不放 `/nas_train`））· 用户直令 · 最高优先
> 📦 已闭合（TOP-5 4 路均下完；85M 仍暂停）→ 原文 `daily-memories-data/2026-10-13.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 📦 §运维规程·agent归档（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：agent自滚MEMORY+任务书,判据≤32KB/红线40KB,做法=只搬迁留指针（与「体积维护规程」同口径）。需要时再读。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 📦 §收尾铁律·事故背景（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：心跳2h未更新致误判卡死→立「每轮必commit+push」硬约束。需要时再读。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（**不阻塞交付**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   wc -c doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md
   ```
   **≤40KB 一律不用管**（直接继续干活/收尾）；>40KB 才把已闭合块搬进 `run/ARCHIVE_OPERATOR_DATA.md`（留 1 行指针）。
   🚫 不许用「先归档/先写心跳」当理由推迟分词或布局。

1. 写心跳：更新 `run/MEMORY_DATA.md` 顶部进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-data/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建，不许攒着最后补）。
3. 自己提交 + 推送（**不许等 loop 兜底**；提交范围已放开）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run doc/BaiZe-ISEDA2027/reports
   # 若上面不够（例如脚本也被你改了）：git add -A   ← 允许，但提交信息必须带 data: 前缀便于溯源
   git commit -m "data <轮次>: <一句话>"
   git push origin main        # 失败时显式带代理：https_proxy=$P http_proxy=$P git push origin main
   ```
   ✅ `doc/BaiZe-ISEDA2027/run/**`（含 `run/data/`、`run/data_pipeline/`、MEMORY/日报）与 `doc/BaiZe-ISEDA2027/reports/**` **都在白名单内**。
   🚫 只此一条仍保留：**不要把别的线（pretrain/vision/harness）正在改的文件卷进你的提交** —— 用 `git status` 看一眼，只提交本线路径即可。

4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理（派人上机 kill / 重排卡），不再等你。你干得再多，心跳不动 = 仍会被判死。

> 📦 §第5轮·代理规模定案 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：d=128/L=14/N≈18.5M定案+5项必验全PASS+评测硬规则+第0步分工,详见各子指针。需要时再读。

> 📦 §用户复核② 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：5条判据(BO 200/200已满足)+先验88:8:4对照(进行中,见三步令①)+心跳纪律(已由收尾铁律覆盖)。需要时再读。

---

> 📦 §运维指令·2026-10-06配比实验改道（小代理+BO搜索空间/目标函数/交付§④⑤⑥）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：改道执行✅,BO R1+R2全完成,搜索空间/objective/交付已落地。需要时再读。

---

> 📦 §运维指令 · 2026-10-05（HTML报告 + D-CLEAN-4 定案 + 环境隔离）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：report_data_mix_s0a.html 已产出（已废弃）、D-CLEAN-4 保留不动、环境隔离纪律见 proxy 口径块。需要时再读。


### 🆕 运维口径 · 2026-10-05（你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测）

> 📦 §proxy口径·定位与反证段（2026-10-05）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：loop剥代理致外网不可达是预期→外网命令显式带proxy(见下方用法)。需要时再读。
> 🔧 正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）：凡访问外网的那一条命令，自己显式带上代理（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都不要带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> 🚫 装包别动共享 py310 env（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令 · 2026-10-05（分卡协调 GPU2-7）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：GPU2-7 归 data、配比实验已开工。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 📦 §体积维护规程·理由段（2026-10-03~06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：TASK/MEMORY每次唤醒全文读入→越大约烧token→≤32KB硬约束。需要时再读。
- 上限：**≤40KB 可正常干活**（>40KB 才当轮归档；不再要求 ≤32KB）。
- 自检：见「收尾铁律」第 0 条；**体积永远不优先于交付**。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_DATA.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_DATA_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成的调研轮次原文 → 沿用 `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md` 等；
  ④ 较早的唤醒流水（保留最近 ~20 条） → `daily-memories-data/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有「见 §③.9」「上方块」这类交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 「进度快照」③ 「运维问答」（这一区不清，运维靠它读答复）④ 最近 ~20 条流水。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---


| 项 | 当前值 |
|:---|:---|
| 🆕 下载白名单（2026-10-03 立 · 2026-10-09 用户裁定修订） | 只下 ① `ultrafineweb_l1_en_hq` + `ultrafineweb_zh`（base 族）② GPIC；🟡 `ultrafineweb_en_v1_4`：停用中 → 待 GPIC 下完后放行（用户 2026-10-09 裁定：放行时点 = GPIC 完成后、预计 10-10 上午、用户本人操作）；🚫 白名单外一律不下载、不调研、不推荐 |
| 历史指令 | 📦 D-CLEAN-4/当前指令/优先级覆盖/状态索取/暂停标志（2026-10-01~04）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：全部已闭合/被运维指令区新块取代（配比实验改道为BO搜索，见上方活跃块）。需要时再读。 |

---

## 📊 进度快照（每次唤醒必须更新，供远程巡检）

> 固定格式写在 `MEMORY_DATA.md` 最顶部，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_DATA.md` 的顶部单独一行（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行——否则会误触发 30 分钟长睡。
（pretrain loop 就是因为正文里出现了一句 `WAITING: **1**` 的散文而被误匹配，一直在长睡。）

运维巡检方式：外部运维通过 `git pull` 读取 `MEMORY_DATA.md` 顶部 + `DATA_LEDGER.md` + `CONTAMINATION_CHECK.md` 即可掌握进度；不需要登录服务器。

---

> 📦 §0「当前主攻」+ §0.6「R4阶段 P-8 数据配方」（2026-10-02）已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：R/R2 调研完成、配比实验已改道为小代理+BO（见运维指令区改道方案块）。需要时再读。
---
## 1. 任务目标

把已在盘上的原始语料，变成训练可直接消费、配比正确、且不污染评测集的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ ← 🚫 已取消（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. 污染隔离白/黑名单 + 校验脚本（红线，P0）

上游方案文档（先读它）：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
时间线约束：ISEDA 2027 投稿截止 ≈ 2027-02-01；本任务必须在 2026-11 底前可交接（见方案 §6）。

> 注意本任务的定位：瓶颈是算力窗口不是数据量（方案 §2.1）。
> 所以不要把精力花在"下载/切分更多数据"上，而要花在质量、配比、格式可用性、隔离上。

> 📦 §1.1「数据落盘地图」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：实测数据位置详见 DATA_LEDGER.md。需要时再读。

> 📦 §2「阶段与推荐执行顺序」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：R/phase0/phase5 完成，当前主攻=配比实验（见运维指令区）。需要时再读。

## 3. 红线：污染隔离（违反则全部下游结论作废）

🚨 `EDA-Eval-PyAether` 的 158 个任务内容（`prompt` / `entry_point` / `test` 断言；注：v20260311 版无 `canonical_solution` 字段，见 DATA_LEDGER §1.3）
绝对不能进入任何训练集。 改写/paraphrase 也不洗白。

- ✅ 允许入训练集：PyAether / SKILL 的 API 参考文档（它是任务的"来源材料"）
- ❌ 禁止入训练集：评测任务的 prompt、函数名、参考解、断言代码，及其改写版
- 机制必须包含：① 黑名单指纹 ② 训练集侧扫描 ③ 阈值写明可复现 ④ SFT 语料同闸 ⑤ 独立报告
- 同一条规则适用于多模态 held-out 评估集（如 `eval5k`）：与训练集不同源 + 跨集去重比对

评测集本体路径（用于建黑名单，只读，绝不写入任何训练集）：
`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`

---

> 📦 §4「git 与共享工作区规则」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：git 规程见「收尾铁律」§3 + AGENTS.md §4。需要时再读。

## 5. 资源与约束
> 📦 §5「资源与约束」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：常驻 .12、GPU2-7 归 data（见运维指令区）、重 I/O 避让。需要时再读。


## 6. 记忆管理

| 文件 | 作用 |
|:---|:---|
| `run/MEMORY_DATA.md` | 运行时状态：顶部"进度快照"（固定格式，供远程巡检）+ PHASE/WAITING/看板/流水 |
| `run/DATA_RESEARCH.md` | 🎯 调研报告（当前主攻）：只回答两个问题（LLM / Vision 的数据够不够 + 配比），每条含 URL / 规模 / 许可 / 可得性 / 建议 |
| `run/DATA_LEDGER.md` | 数据清单（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | 污染隔离报告（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 `DATA_RESEARCH.md`（调研报告，当前主攻） —— 两个问题各四小项全部有结论，每条关键结论可顺 URL 复核
2. `DATA_LEDGER.md`（数据清单，含实测规模与与方案文档的差异）
3. `CONTAMINATION_CHECK.md`（污染隔离规则 + 阈值 + 扫描量 + 命中 + 处置）
4. `run/data_pipeline/`（可复现脚本，至少含盘点、校验、分词打包、指纹比对）
5. 训练可消费的产物（`.bin/.idx` + webdataset），路径与校验和写入清单
6. `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html`（自包含，与既有 HTML 报告同风格）
7. git commit + push（只提交 doc/ 文本与 run/ 脚本）

---

## 8. 推进原则

- 无阻塞时连续推进：把能立即做完的步骤一口气做完（可跨多个阶段），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟）。
- 有异步阻塞时：回写记忆并把 `WAITING` 置 `1`，记录"等待什么、如何判断结束"，然后退出。
- 不确定就如实记录并上报，不要编造数据、不要产出"看起来对"的合成语料。
