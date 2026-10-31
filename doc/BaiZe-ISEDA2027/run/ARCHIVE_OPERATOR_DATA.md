## 归档 2026-10-31（由 BAIZE_DATA_TASK.md 搬入，原文未改）

### 🚨 2026-10-30 22:2x 运维直令：恢复 85M 下载 + `/nas_train` 大目录清理盘点 · [主体已交付，下载持续进行]

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

# ARCHIVE — 历史运维指令（源自 BAIZE_DATA_TASK.md）

> 运维 2026-10-05「任务书瘦身」时移出（**原文未改**，不改任何结论）。仅当需要查历史指令细节时再读。
## 归档 2026-10-25（由 BAIZE_DATA_TASK.md 搬入，原文未改）

### 🔥🔥 最高优先 · 2026-10-25 13:2x · 运维直令 · **停止一切报告工作，现在只做两件事**

> 现状（运维 13:19 实测）：loop 活着（.12 PID 1647008）、cline 活着；你 12:41 重生成报告（10,520 B，1 table，每行加了 `du -sb …` 命令）—— **报告这部分做得对，验收通过**；`untokenized_v1_20261025.tsv`（12:47，500 B）已落。
> **但 `…/baize-data/tokenized/` 不存在、`preprocess_data` 进程 = 0、load 6.8 → ① 布局没建、② 分词没跑。用户要的就是这两件。**

1. **先提交你在工作区里的成果**（报告 HTML、`gen_tokenized_inventory_report.py`、`map_dl_vs_tok / untokenized_v1 / report_verify`、`DATA_LEDGER.md`、`MEMORY_DATA.md`）——
   **用显式路径 add**（收尾铁律禁 `-A`，本令把 `reports/report_data_tokenized_inventory_zh.html` 与 `run/data/` 加入你的提交白名单）：
   `git add -- doc/BaiZe-ISEDA2027/reports/report_data_tokenized_inventory_zh.html doc/BaiZe-ISEDA2027/run/data doc/BaiZe-ISEDA2027/run/DATA_LEDGER.md doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md doc/BaiZe-ISEDA2027/run/daily-memories-data && git commit -m "data <轮次>: <一句话>" && git push origin main`；**不许留在工作区不提交**。
2. **立刻建 `tokenized/` 镜像布局**（见下方 ①，hardlink/symlink，零拷贝）→ 建完 `tokenized/INDEX.tsv` 必须存在，并在 MEMORY 里贴 `find tokenized -maxdepth 3 -type d` 的实际输出。
3. **立刻开分词**（见下方 ②）→ **30 分钟内** `/tmp/tokenize_untokenized_*.log` 必须有 `done/total` 行、`ps -eo args= | grep -c '[p]reprocess_data'` 必须 > 0；标定四档（96/144/192/224）的数字要贴回来。
> 🚫 从现在起**不要再改报告结构、不要再重写报告、不要再补勘误/摘要**（报告已验收）。
> 🚫 不要把"核对了/准备跑"当成"跑起来了"；**判据只有：日志有进度 + 进程数 > 0**。


### 📊 运维指令 · 2026-10-24 13:2x（**MiniCPM5 全量已分词数据：硬盘实测清单**）· 用户直令 · 最高优先

> 用户原话：「我现在要的是 MiniCPM5 全量数据，分词后的数据，列表，占多少硬盘，分词后多少 tok，在硬盘的文件全名是什么。让 data 在硬盘上查。」
> **只许写硬盘实测值**：每个数字必须能追到 `du -sb` / `find` / `wc -l` / manifest 的原文行。🚫 不许估算、不许拼凑、🚫 不许把未分词/未下载的数据混进来。

**① 对象定义（严格）**
- 范围 = **已经分词落盘的 MiniCPM5 全量数据**（即 `/nas_train/app.e0031982/datasets/baize-data/text/` 下的全部分词产物 + 历史 `full_*` 目录）。
- **不含**：未分词的原始 parquet（base-en / l1_en_hq / zh / Math L2p）、SFT/RL jsonl、85M 多模态。
- 上述"不含"的部分只在报告末尾单列一节做**对照**，🚫 不得计入总量。

**② 必须回答的四个数（正文里直接给）**
1. **占多少硬盘**：总字节（`du -sb`，给 bytes + TB 两位小数）
2. **多少 token**：总 token（**取 manifest / summary 的实测累计值**；若某目录没有 manifest ⇒ 该目录标 `N/A`，并单列"无 token 记录"）
3. **多少 shard**：`.bin` 总数（并给 `.idx` 总数）
4. **文件全名**：见 ③

**③ 文件清单（这是本轮重点）**
- 先给**命名规则 + 目录结构**（例：`l3_s00.bin` / `l3_s00.idx` / `env14_000.bin` …），说明每个前缀对应哪个数据源。
- 再**逐文件列出完整路径与文件名**（每行：`绝对路径 | 字节`）。
- 文件数多时：正文只放**前 20 行样例 + 汇总**，完整清单落盘到
  `doc/BaiZe-ISEDA2027/run/data/tokenized_files_20261024.tsv`（列：`abs_path<TAB>bytes`），**commit 进仓库**并在正文给出该文件的路径与行数。

**④ 逐源汇总表（一行一个分词产物目录）**

`数据源 | 目录绝对路径 | .bin 数 | .idx 数 | 字节数(du -sb) | TB | token 数(实测) | 完成时间`

必须覆盖：en_v1_4 全源分词、UFW-L3、UltraData-Code L3、UltraData-Code L2、UltraData-Math L3、UltraData-Math L1，以及 `text/` 下其它任何 `*.bin` 所在目录（有就列，没有就说明）。
表末给**合计行**（∑字节 / ∑shards）。

**⑤ 空间判定**：`df -B1 /nas_env` 可用字节 vs 上表合计（×1.1 双份窗口）⇒ **够 / 不够 + 差多少 TB**。

**⑥ 口径（硬）**
- 只用 `timeout 120 du -sb <单个目录>`；🚫 禁止整树 du。
- 🚫 不要把内部轮次代号（如 "R3"）当数据源列出。
- token 数一律取 manifest/summary 实测值；取不到写 `N/A`。
- 纯只读：不移动、不删除、不起下载。

**⑦ 交付**：中文 HTML `reports/report_data_tokenized_inventory_zh.html`（自包含）+ 本轮回复给同样的表 + `tokenized_files_20261024.tsv`；commit 前缀 `data report:`；push 后无 ahead/behind。

### 🆕 运维指令 · 2026-10-23 22:1x（**① 复测 `92.25` 代理+hf.co 直连 ② 恢复 85M 下载 ③ MiniCPM5 分词产物体积 ④ 搬 `/nas_env` 腾 `/nas_train`**）· 用户直令 · 最高优先

> 用户原话：「data: 1.尝试 92.25 代理+hf.co直连是否恢复；2.恢复 85M下载；3.看看MiniCPM5分词后的数据有多大；4.如果够放，在en_v1_4 分词完成后把MiniCPM5分词的数据搬到/nas_env去给/nas_train省空间。」

**① 代理复测（先做，≤10 分钟出结论，别等分词）**
- 口径（2026-10-15 用户令不变）：**下数据 = `http://172.19.92.25:13128` 直连 `huggingface.co`；🚫 不用 hf-mirror**。
- 探针 4 条，逐条贴原文输出（`timeout 20` 包住）：
  1. 端口：`nc -zv 172.19.92.25 13128`（或 `curl -m 5 -x http://172.19.92.25:13128 -o /dev/null -s -w '%{http_code}' https://huggingface.co`）；
  2. `curl -x ... https://huggingface.co/api/models/openbmb/MiniCPM5-2B` → 期望 **200**；
  3. 实测下载 1 个 ≤20MB 文件取速（MB/s）；
  4. 与 `hf.co` 直连（不挂代理）对照，各 1 次。
- **判据**：② 200 且 ③ ≥1 MB/s ⇒ 「已恢复」→ **立刻做 ②**；若仍 5xx/超时 ⇒ 记「未恢复」+ 附 4 条原文，**不要反复重试烧时间**，转去做 ③④。

**② 恢复 85M 下载（用户直令，解除 10-13 的暂停）**
- 目标：`LLaVA-OneVision-1.5-Mid-Training-85M`（历史路径 `/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M`，**先 `ls` 核实真实路径**），暂停时进度 **8,436 / 12,124 parquet（69.6%）**。
- **必须断点续传**（不重下已完成的 parquet）：复用既有 `hf download` 封装/wrapper，`--resume`（或 `.incomplete` 保留）；**建议落 `/nas_env`**（用户令要腾 `/nas_train`）——若改落点，先 `df` 报余量再动，且写进 `DATA_LEDGER.md`。
- **前置**：`df -h /nas_train /nas_env` + 剩余 parquet 体积估算 + ETA，**先报数字再起下载**；放不下 ⇒ 报 blocker（说明差多少 TB）而不是硬下。
- **错峰**：分词的 10 个 worker 正在写盘，下载并发 ≤8，`nice -n 10`；🚫 不停 en_v1_4 分词、不删任何已有 parquet。

**③ MiniCPM5 分词产物体积（要机器可核的数字）**
- 输出：`du -sh`（**只对已知目录做有界 du，带 `timeout`，🚫 不对 `/nas_train` 整树 du**）+ `find … -name '*.bin' | wc -l` + `find … -name '*.idx' | wc -l` + 字节总和。
- 至少给：**总大小 / shard 数 / 各源拆分大小**（Code L3、Code L2、Math L3、Math L1、UFW-L3 五项）。
- 同时给 `/nas_train`、`/nas_env` 的 `df -h` 现状与余量。

**④ 迁移到 `/nas_env`（前置硬条件：en_v1_4 分词 done=110/110 之后才做）**
- 安全铁律（沿用 10-22 RUN_ID 149 口径）：① `df` 确认 `/nas_env` 余量 ≥ 数据量 ×1.1；② **`rsync -a` 不用 `mv`**（跨挂载 mv = 复制+删除）；③ **校验 shard 数 + 总字节一致后**才删源；④ 先建**软链接**保证旧路径可访问；⑤ 不停 en_v1_4 分词以外的任何工作。
- 删除前**必须在本轮回复里报「将删哪些目录 + 校验结果」**，未校验同号不得 `rm`。
- 完成写 `DATA_LEDGER.md`（源/新路径/字节/shard/校验和）+ `MEMORY_DATA.md`；commit 前缀 `data migrate:`。

**回报格式（本轮必须给）**：① 代理 4 探针原文+结论 ② 85M 磁盘余量/ETA/已起或 blocker ③ 五个源的 du 明细 ④ 迁移是否具备条件（余量对比）+ 若已迁则校验结果。

### ⚡ 运维令 · 2026-10-24 18:1x（**85M 降优先级 → 迁移提速**）· 用户直令 · 最高优先

> 用户原话：「**85M 下载优先级不高。**」

**① 唯一动作：把迁移限速提上去**
- `--bwlimit` **50000 → 300000 KiB/s**（≈51 MB/s → **≈307 MB/s**，可调）。
- 用新脚本 **`run/data_pipeline/migrate_to_nas_env_fast.sh`**：`BWLIMIT` 环境变量可覆盖（`0`=不限速）；
  校验口径（shard 数 + 总字节数）、先软链接后删源、顺序 `math_l3→code_l3→math_l1→ufw_l3→code_l2` **与 v1 完全一致**，
  新增 `--partial`（断点更省）与 `flock` **单实例锁**。
- 🚫 **不得就地编辑正在跑的 `migrate_to_nas_env.sh`**（bash 按字节偏移读脚本，会读串行）⇒ 必须先停旧进程。
- 🚫 **不得起第二个迁移实例**（串行总量才可控；双实例=双倍带宽=预算失效）。
- 切换由运维经 ops **RUN_ID 158** 执行（SIGINT 停旧 → 起新脚本 → 实测 60s 速率 + ETA）。
  - **兜底**：若中继无回执（`run/ops/.last_run_id` 仍为 `157`），则**本轮唤醒由你亲自执行同一套动作**（先 `kill -STOP` 旧脚本再 `kill -INT` rsync → `BWLIMIT=300000 setsid -f nohup bash migrate_to_nas_env_fast.sh > /tmp/migrate_to_nas_env_fast.log 2>&1 &` → `du -sb` 60s 实测），并在回报里写清"中继未执行、由 agent 代执行"。

**② 85M 降级**：**不再是任何前置条件**，不再为它预留 NFS 带宽；继续后台跑即可（8752/12124≈72.2%）。

**③ 判据**：新速率用 `du -sb` 60s 差值实测并写进 `MEMORY_DATA.md`；若 <80 MB/s ⇒ 瓶颈在 NFS 而非限速，如实记录（不要编"已提速"）。

---



### 🆕 运维指令 · 2026-10-10（🔄 重启 `en_v1_4` 下载）· 用户直令 · 最高优先

> **用户令（2026-10-10）**：「给 data 下指令，重启 en_v1_4 下载。」

**① 背景**：GPIC 已全部完成（train 8000/8000 + val 32/32 + test 128/128，唤醒 #294）→ `en_v1_4` 放行条件已满足。`en_v1_4` = Ultra-FineWeb base 的 4 config 之一（`data/ultrafineweb_en_v1_4/`，CC-MAIN-110 快照），**56,461 文件 / 6.75TB** = base 主体，是 P-8 主预训练语料（86% 档）的核心组成。之前被 10-03 白名单停用，现已放行。

**② 执行（立即启动，config 级 `--include` 续传）**：
```bash
setsid -f nohup hf download --repo-type dataset openbmb/Ultra-FineWeb \
  --local-dir /nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb \
  --include 'data/ultrafineweb_en_v1_4/*' \
  > /tmp/en_v1_4_dl.log 2>&1
```
- 落盘 `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/`（沿用 base-en 复用路径，勿改回 `/nas_inference`）。
- 公开数据集（apache-2.0），无需 token。
- 有 `.incomplete` 则从断点续传，**不删 `.incomplete`**。

**③ 纪律**：判活按 `.incomplete` 字节增长 / `/proc/io write` / log 尾部；僵死即 `kill` + **同命令**重启续传，报告标「已重启」+ 新 PID。磁盘 37T free ✅。下满 56,461/56,461 后**必经 `check_contamination.py`**（EDA-Eval 不同源 + 跨集去重）再报「`en_v1_4` 下载完成」。🚫 本轮**只下 en_v1_4**（zh / l1_en_hq 早已下完分词，无需再动）。

**④ 体积**：若 TASK 超 32KB，按「体积维护规程」把已闭合旧块原文搬入 `ARCHIVE_OPERATOR_DATA.md`（只搬迁留指针），不新增/改写历史指令。

### 🆕 运维口径 · 2026-10-10（`en_v1_4` 放行 · **用户再确认**）· 最高优先

> **用户令（2026-10-10）**：「GPIC 若结束，即可放行 en_v1_4。」—— 放行时点从「预计 10-10 上午」收敛为「**GPIC 完成即满足放行条件**」（GPIC 当前 7982/8001，ETA ~13:34）。放行操作仍由运维/用户改下载白名单后下指令；**data 仍不自行启动** `en_v1_4`。

### 🆕 运维口径 · 2026-10-09④（`en_v1_4` 放行时点 · **用户裁定**）· 最高优先

> **用户裁定（2026-10-09）**：`en_v1_4` **在 GPIC 下载完成之后再放行**；时点预计 **2026-10-10 上午**（GPIC 当前 7418/8001，ETA ~10:48 Oct10），**由用户本人操作**。

- ⇒ data **不要再把 `en_v1_4` 列进「阻塞」** —— 它**不是**「P-8 数据层就绪」的前置条件；`阻塞` 栏只留真实阻塞项（R3 分词 / GPIC）。
- ⇒ **不要自行启动 `en_v1_4` 下载**（白名单未改前仍属停用项）。放行由运维/用户改白名单后**单独**下指令。
- 其余一切不变 —— **③ 块继续有效**（R3 全量分词 → 污染扫描 → 报「P-8 数据层就绪」；GPIC 续下）。

---

### 🆕 运维问询 · 2026-10-07（**三个现状问题 —— 只回答，不加负担**）· 用户提问
### 🆕 运维问询 · 2026-10-07（**三个现状问题 —— 只回答，不加负担**）· 用户提问

> 用户 2026-10-07 中午问的三件事，请**本轮心跳直接回答**（写进 `MEMORY_DATA.md` 顶部「运维问答」+ 心跳一行），**要给原始命令/输出，不要只给结论**：

**① base 下完后，GPIC 下载是否加快了？**
- 给 **base 完成（08:16）前/后** 的 **GPIC tar 速率对比**（单位 **tar/h**，≥2–3 个采样点 × 各自 Δt，标明采样时刻）；若有 `nohup.out`/`hf` 的**实时速率行**更好。
- 给 **剩余 tar 数 → ETA**。⚠️ 如实：**没加速就说没加速**（别为好看编趋势）。

**② base 是否还有其它数据待下载？**
- 按**白名单**逐项列：`ultrafineweb_en` / `l1_en_hq` / `zh`（各自 **n/目标** + 是否已满 + 尺寸）；GPIC 单列。
- 明确白名单外（`en_v1_4` / `UltraX-Preview`）**是否仍按纪律不下载**（含那个 stale 0-byte `en_v1_4` `.incomplete` 如何处理）。
- **要一句话结论**：**base 的「下载」是否已全部结束、只剩「分词扩展（tokenize）22.05B→~100B tok」**。

**③ Round2 BO 为什么变慢了？**
- 把「**每 trial = 训练 X min ＋ lm_eval 8 集 Y min**」**拆开报**（给最近 ~10 个 trial 的 **train/eval 时长中位数**，从 DB `end_times`/日志取）。
- 逐条判：① 是否「**8 卡按波派发**」造成的锯齿（波次量化：8 个 trial 几乎同时完成 → 急/缓交替）；② 是否有 **I/O 争用** —— ⚠️ `.29` 上 **harness 的 SWE-bench（opencode×30，11:19 起）** 反复 `git clone/fetch` + 大量小文件 I/O，可能与 BO 的 **NFS 数据加载**抢带宽 ⇒ 给 `iowait` / `GPU util` / NFS 带宽佐证；③ 是否有 trial 失败/重试被计入分母。
- **要求**：给「**train vs eval 拆分 + 争用证据**」，据此再重估 ETA。

> 🚫 **约束**：**只答不动** —— 不占额外 GPU、**不改白名单**、不影响 BO 与下载；本轮 ≤30 min 内答完。

> **结论**：三问已答（唤醒185）：①base完成后GPIC无加速（仍~45.5/h→后因UltraX启动降至~3.4/h）；②base下载全部结束（en✅2048/l1_en_hq✅6000/zh✅256），只剩分词扩展22.05B→~100B；③BO变慢=波次量化锯齿(8trial/波gap~37min)非I/O争用(vmstat wa=0)。

### 🆕 运维指令 · 2026-10-05（**🔁 用 web search 重做一遍文献调研 —— 现有 `LIT_IDEAS_2026-10-04.html` 仅作参考**）

> **用户判断（2026-10-05）**：那份调研是**在没有 web search 的前提下**用「模型知识 + 本地 `.bib`」做的 —— **如果一开始就能联网，它找到的很可能是另外一批文献**。⇒ **请重新做一遍**；**现有结果只作参考（对照物），不是答案**。
> **现在前提已经不同**：`cimi_search`（搜索）+ `cimi_fetch`（抓正文）**四线均已实测可用**（见本文件下方「MCP 已修复」块）—— 这一版要**从一开始就联网**。

**与上一版的区别（请严格执行）**

| | 上一版（10-04） | **这一版（10-05 重做）** |
|:--|:--|:--|
| 起点 | 模型训练知识 + 仓库 `.bib` | **`cimi_search` 检索 → `cimi_fetch` 读原文/摘要**（**发现驱动**） |
| 前沿 | 「2026 最新工作」**完全空白**（检索不可用） | **必须补上 2024–2026 前沿** ← 本轮最大增量 |
| 证据 | 15 条事后核验 | **每条从一开始就带 `URL + 年份 + 会议`**；**正文级数字必须 `cimi_fetch` 核过** |
| 产出 | `LIT_IDEAS_2026-10-04.html` | **新文件 `LIT_IDEAS_2026-10-05.html`**（**旧文件保留不动**，便于对照） |

**怎么做（建议流程；可按实际调整，但要在报告里写清）**
1. **每个方向先做 5–10 次检索**（换关键词/同义词），把命中的论文/仓库列成**候选池**（先不求全）。
2. **筛一轮**：只留「**能改变我们某个决策**」或「**能提升论文质量**」的 → 进主表。
3. 对入选条目 **`cimi_fetch` 读原文/摘要**，抓**具体做法 / 超参 / 公式 / 数字**（🚫 不要只抄标题）。
4. **顺引用/相关工作再扩一层**（尤其 2024–2026）。
5. **方向 0（成本 / 服务经济性）最优先** —— 它是「≈2027 H2 救场」命题的支柱；**关键缺失数字 = DeepSeek-Flash 的 `$/1M tok` 定价**（及可比 SLM 的运行成本口径），要把「**~1/100 成本**」算实。
6. **每个方向都要有「经典锚点（≤2023）」+「前沿（2024–2026）」**。

**🔒 判据（什么算「重做成功」，先定后测）**
- **≥ 60% 的条目与上一版不同**（新增 / 替换 / 更正）—— 若几乎一样，说明还是在**凭记忆**，**要如实说明并继续检索**；
- **0 条「未在线核验」**（每条都有 URL + 年份；核不到就**剔除**，或明确标「未核实」并写原因）；
- **2024–2026 的条目 ≥ 15 条**（补上上一版的天窗）。

**📌 产出（新文件 + 对照节）**
- `doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-05.html`（自包含、无 CDN），结构沿用：TL;DR · 主表（**必须含 `URL` 列**）· 三档 · **「成本救场」专章** · TOP-10 · 7 方向详述 · 缺口清单；
- **新增一节 `§0 与 10-04 版的差异`**：**新增 / 被替换 / 被更正 / 被剔除** 各列几条 + 一句话原因（**这节对运维最有用**）。

**约束**：仍 🚫 不占 GPU · 不下大文件 · **不改下载白名单**（巡检 4 项照做）；可分**多个唤醒**推进，每次在 `MEMORY_DATA.md` 记一行进度；**做不完就交「已完成方向 + 缺口」**，🚫 不许凑数。

### 🆕 运维指令 · 2026-10-05（**🟢 MCP 已修复并实测可用 → 请用 `cimi_search`/`cimi_fetch` 把 LIT_IDEAS 升级为「全部一手核验」**）

> **运维已完成（2026-10-05 07:2x–07:35，RUN_ID 64→69，全部留痕在 `run/ops/outbox.md`）**：
> - `.29:8090` 的 **`eda_fastmcp` SSE MCP 一直在运行**（监听 **`0.0.0.0:8090`**，`pid=111692`），工具 = **`cimi_search` / `cimi_fetch`**；
> - 🔧 **修好了一个真 bug**：**`.12` 的共享 `~/.cline/data/settings/cline_mcp_settings.json` 是空的（22 B）** → **已备份并写入 `pyAether_MCP_server [sse]`**（`url=http://10.239.2.29:8090/sse`）。`.29` 侧本来就正常。
> - ✅ **已在 `.29` 与 `.12` 各真跑一次 `cimi_search` → 均 `rc=0`、返回真实搜索结果** ⇒ **MCP 服务本身能出网**。
> - 📌 另查明：**`--data-dir` 不改变 MCP 配置的读取路径** —— cline 固定读共享的 `~/.cline/data/settings/cline_mcp_settings.json`。
> ⇒ **你之前「MCP 未注册 / 网络不可达」的前提已经不成立。**（对应你在 `LIT_IDEAS` 顶部红框里那条声明 —— 现在可以撤掉。）

**要做的事：把 `doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-04.html` 从「37 条本地核验 + 15 条未核验」升级为「全部一手核验」**

1. **核验那 15 条「⚠️ 未在线核验」**（报告 §7 列表）：`DeepSeek-V3 2412.19437` · `GRPO/DeepSeekMath 2402.03300` · `推测解码 2211.17192` · `FrugalGPT 2305.05176` · `RouteLLM 2406.08502` · `SigLIP 2303.15343` · `MAE 2111.06377` · `CLIP 2103.00020` …（逐条确认 **ID / 标题 / 作者 / 年份** 是否对得上）。
2. **补「成本救场」专章的关键缺失数字**：**DeepSeek-Flash 的 $/1M token 定价**（及可比的 SLM 推理成本口径），用来把「**~1/100 成本**」算实（这是本命题最关键的基线数字）。
3. **查 ISEDA 2027 的页数上限 / 投稿要求**（论文当前 **7 页**）。
4. **补 2026 年最新工作**（此前 `cimi-search` 不可用 → 完全空白；现在是你的增量价值最大处）。
5. **用 `cimi_fetch` 抓正文核实关键数字**（不要只信摘要；凡引用成本/参数量/token 数都要能回溯到原文）。
6. **就地更新同名 HTML**：把已核验项标 **✅ 一手核验**、撤掉/改写顶部「工具不可用」红框、**每条都补可点 URL**；若某条最终核不实 → **如实标「未核实」并说明**（🚫 不许为凑数编条目）。

**报告**：`MEMORY_DATA.md` 记一行；HTML 就地更新（同名文件覆盖）。
> 🚫 仍然：**不占 GPU、不下大文件、不改下载白名单**（`en`/`l1_en_hq`/`zh`/`gpic` 巡检照做）。

### 🆕 运维指令 · 2026-10-04（**附加任务 · 最高优先：BaiZe 论文「idea 文献调研」→ HTML 报告，明早 08:30 前**）

> **用户定位（2026-10-04，决定本任务的取舍）**：
> 1. **论文的第 1 读者不是会议评审，而是「公司领导 + 约 1400 位设计工程师（DE）」** —— 目的是**技术影响力**：让人看出我们**真懂细节**、能把一个 2.2B 多模态 agent 从零搭出来。**投中 ISEDA 是加分项，不是目的**；「提升录用率」有帮助但**次要**。
> 2. **核心商业命题（论文要能自圆其说）**：ZhuLong 正在让越来越多 DE 用上 EDA agent → **随着使用人数增长，token 成本会急剧上涨**；**≈2027 H2** 时 **BaiZe 可「救场」分档承接流量 —— 指标达到 DeepSeek-Flash 的 70–80%，成本仅其 ~1/100**。
> ⇒ **调研的取舍规则**：优先找**「能写进论文、让人看出我们懂行」的深度细节**（具体做法/超参/公式/代码位置）与**「支撑上述成本命题」的一手证据**；**不要**堆砌「某某方向很有前景」的空话。
> 🚫 **本块不改变下载白名单** —— 巡检 4 项（`en`/`l1_en_hq`/`zh`/`gpic`）照旧做；本块是**附加**任务。

**① 工具（你独有）**
- 用 **`cimi-search` 搜索** + **`cimi-fetch` 取正文**（MCP）。**工具失败/不可达 → 如实报告**（贴原始报错），🚫 **不许凭记忆编造**。
- ⚠️ 本线既有纪律：**任何口令/密钥严禁打印**；长输出 `cut -c1-140`。

**② 证据规则（硬性）**
- **优先一手来源**：论文原文 / arXiv / 官方仓库 / 官方权重卡 / 官方榜单。**二手博客只能作线索**，且必须标「**二手·未核**」。
- 每条 idea **必须给可核验标识**：`标题 + 年份 + 会议/arXiv 号 + URL（或仓库路径）`。**核不到就标「未核实」**。
- **数字必须能回溯到来源**（不要转述二手数字）。

**③ 调研方向（7 条；**方向 0 为最高优先**）**

| # | 方向 | 具体要找什么 |
|:--|:--|:--|
| **0 ⭐** | **成本 / 服务经济性（支撑「70–80% @ 1/100 成本」命题）** | ① token 成本趋势 & **agentic 负载经济学**（为什么随用户数急剧上涨）；② **大模型→小模型的成本转移**：蒸馏 · **级联 cascade** · **路由 routing** · 推测解码；③ **「小模型达到大模型 X% 能力、成本 1/Y」的公开证据/基准**；④ **推理成本口径**（$/1M tok · KV/状态内存 · 并发 · 长会话）；⑤ **SLM 在 tool-use/agentic 上的实测**（有没有「小模型足够承接某档流量」的证据） |
| 1 | SLM 预训练 | 从零配方与教训（token 预算 vs 参数 · 数据配比 · WSD vs cosine）· **μP / 小规模超参排名的迁移性**（直接支撑我们的 proxy-search 支柱）· **hybrid-SSM vs Transformer 的最新效率-质量证据** · 线性解码对**长会话服务成本**的量化 |
| 2 | LLM 后训练 | SFT 数据质量/去重/难例挖掘 · **RLVR 在 agentic/tool-use 的做法**（GRPO/DAPO/…）· **领域退火**公开配方 |
| 3 | Vision encoder 预训练 | **密集监督在数据受限下的收益**（MAE / AIMv2 / SigLIP2 —— 正好对上我们刚出的「**AIMv2 翻盘 12.08%**」）· 小塔/数据效率 · **IN-1k 之外的评测**（线性探测 vs 下游） |
| 4 | MLLM 训练 | 对齐配方（单/两阶段 · 冻结 vs 解冻 · AnyRes · **token 压缩**）· 小 MLLM 高效对齐 · **EDA/图表/版图类**多模态评测 |
| 5 | MLLM 后训练 | 多模态 RLVR/DPO · 细粒度视觉推理的**数据合成** |
| 6 | 横切：论文质量 | related work 该补哪些线（**§2 现缺「视觉编码器」一线**）· Limitations 怎么写 · 图表与口径 · **「技术报告型」论文如何避免被判「无新意」**。**录用率作次要维度**（保留一列即可） |

- **⏳ 前沿 + 经典要平衡**：**每个方向都要给「经典锚点（≤2023）」与「前沿（2024–2026）」各若干**（经典示例：Chinchilla · μP · MAE · SigLIP · Hinton 蒸馏 · 早期 cascade/routing）。

**④ 先读我们的现状（允许且鼓励，**不必逐条对照**）**
- 读 `README.md` · `PAPER_STALENESS_AUDIT.md` · `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` · `run/EXPERIMENTS_VISION_ROUND{8,9,10,11}.md` · `run/BAIZE_*_TASK.md`。
- **目的只有一个：别推荐我们早已证否的东西**（例：**`caption-only`/GenLIP 类监督已被证否**；**加宽视觉塔是负收益**；**FP8 在 M<32K 不转正**）。**不需要**为每条 idea 做正式对照。

**⑤ 交付物（**明早 08:30 前**）**
- 产出 **自包含 HTML**：`doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-04.html`（单文件、可离线打开、**无外部 CDN 依赖**）。
- **结构（必须有）**：
  1. **TL;DR**：≤10 条「最值得做的」，每条一句话 + 为什么。
  2. **主表**（列）：`idea` · `出处（标题/年份/会议或 arXiv/URL）` · `对应 BaiZe 阶段或章节` · `提升什么（效果·速度·成本·叙事·录用）` · `可行性（数据/算力/工程量，三档）` · `潜力` · `证据强度（一手/二手）` · `落地动作（一句话）`。
  3. **分三档**：**① 立即可做（写进论文/改口径，零成本）② 需补小实验（≤1–2 臂或 ≤半天）③ 需长期**。
  4. **专章「成本救场」**：把支撑 **「70–80% 能力 @ ~1/100 成本、≈2027 H2」** 的**一手证据**单列（含蒸馏/级联/路由/推理成本口径）。
  5. **参考清单**：可点的 URL。
- **排序**：按 **可行性 × 潜力**；另单列「**最高性价比 TOP-10**」。
- **⚠️ 若到 08:30 做不完** → 交「**已完成部分 + 明确缺口清单**」，**🚫 不许为凑数编条目**。

**⑥ 约束**
- **纯网络调研**：🚫 不占 GPU、🚫 不下大文件（`cimi-fetch` 只取网页正文）、🚫 不改下载白名单、🚫 不删数据；重 I/O 照旧避让训练。
- 时间：**今晚起、随唤醒推进，明早 08:30 前交付**。

> ✅ **本区块生效即视为已批准** —— data agent **无需再等拍板**，按上述执行；巡检任务并行照做。



> **运维拍板（2026-10-03 用户，最新优先，覆盖此前一切下载相关指令）**：
> 「数据下载**现在就 MiniCPM5 的数据 + GPIC**，**不要再节外生枝**。」

**① 🎯 下载白名单 = 只有这两类（白名单外一律不下载）**

| # | 类别 | 具体项 | 状态 |
|:--|:--|:--|:--|
| **A** | **MiniCPM5 配方数据**（P-8 / Stage (i) 的 base 族） | `ultrafineweb_en` | ✅ **已下满（2048/2048）→ 不用管** |
| | | ⭐ **`ultrafineweb_l1_en_hq`（478 G）** | 🔜 **优先下完** |
| | | ⭐ **`ultrafineweb_zh`（324 G）** | 🔜 次之 |
| **B** | **GPIC**（Stage (iii) 视觉编码器用） | `gpic` train + test | 🔄 **继续巡检、保持推进** |

🚫 **白名单外一律不下载、不调研、不推荐**（含 `UltraX-Preview`、任何 HF 图文对/文本集、任何「要不要再找数据」的提案）—— **除运维点名，本轮起不再展开**。

**② 🔴 立即停 `ultrafineweb_en_v1_4`（本轮唯一动作项）**

- **依据（运维拍板）**：**6.7 TB / @1.8 MB/s ≈ 43 天**；**`base-en` 1 T tok 已够 P-8**；且它**阻塞**其后的 `l1_en_hq` + `zh`。
- **做法（二选一，按实际可行性，贴命令 + 原始输出）**：
  1. 若现有 `hf download` 任务**可单独摘除**该 config → 停掉它；**保留已下的 442/512 分片，🚫 不删**。
  2. 若是一次性拉全 config（无法摘）→ **kill 该下载进程，重启一个只含 `[ultrafineweb_l1_en_hq, ultrafineweb_zh]` 的任务**；⚠️ 重启前**先记录已下分片数**，**不要删已下内容**。
- **报告**：停了什么、释放带宽去向、新任务 `pid` + 目标清单 + 起步速率。

**③ ⭐ 优先把 `l1_en_hq` + `zh` 下完**（合计 ≈ **802 GB**，按 base 族实测速率估 **≈1–2 天**）→ 下完即视为「**MiniCPM5 base 族就绪**」，报运维。

**④ 带宽优先级（若三者互相抢）**：**GPIC > `ultrafineweb_l1_en_hq` > `ultrafineweb_zh`**
（理由：GPIC 是 **Stage (iii) 正在用**的；base 剩余两项是 P-8 备料，而 `base-en` 已够、P-8 本就暂缓。）

**⑤ 📌 报告口径（本轮起）**：每次巡检**只报白名单内 4 项**（`en` / `l1_en_hq` / `zh` / `gpic`）的**速率 + 进度 + ETA + 僵死判据**；**不再报、不再讨论白名单外的任何源**。
- 某项**速率趋零 / 僵死** → **kill + 重启**（沿用既有规程），报告里标「已重启」。

**⑥ 🚫 红线重申**：不得下载白名单外任何数据；不得新增数据集调研（除非运维点名）；**D-CLEAN 系列已全部完成，本轮不再做任何清理动作**。

> ⚠️ **如实记录的后果（需运维知悉）**：配方 §0.6 的 Stable 段原列 **`UltraX-Preview`** 为候选 web 源（`DATA_MIX_RECIPE.md §7` 标「❌ 未下」）。按本白名单它**不进下载** → 配比实验的 **S1 轴（base vs UltraX 占比）暂无从搜索**，**S1 轴先按「仅 base」处理**。若将来需要 UltraX，**由运维点名后再议**——**agent 不要自行下载或提议**。


### 🆕 运维指令 · 2026-10-04（**D-CLEAN-4：`/nas_train` 大盘复扫（sudo）—— 重点本用户目录**）

> **背景（用户 2026-10-04 指令）**：`/nas_train` **需要清理**。要求 **用 sudo** 看盘下各目录大小，**找到可删除的大目录**，**着重看 `/nas_train/app.e0031982`**。
> 🚫 **本轮 = 「只盘点、不删除」** —— 产出清单交运维拍板；**未经批准不得 `rm`/`mv` 任何东西**。
> ⚠️ **两条纪律（前几批的教训，必须遵守）**：
> ① **绝不整树 `du`** —— `/nas_train` 有 175 TB，全量 `du` 会跑几小时。**只用 `df` + 有界定向 `du`，且每条都带 `timeout`**；
> ② **长输出一律 `cut -c1-140`**；**任何口令/密钥严禁打印**（只以长度/前缀形式出现）。

**步骤（全部贴命令 + 原始输出，不许猜）**

1. **大盘**：`df -hT /nas_train /nas_inference /nas_user /data`，并附 `df -BG /nas_train | tail -1`。
2. **sudo 可用性**：先试 `sudo -n true`（免密？）；若需密码 → **按本线既有 sudo 流程**执行，**口令不要出现在任何输出里**。
3. **顶层**：`ls -1 /nas_train`（只列名）+ 每个顶层项的 **mtime**（`stat -c %y`）与 **owner**。
4. **⭐ 重点 —— 本用户目录**：
   - `timeout 300 du -sh --max-depth=1 /nas_train/app.e0031982 2>/dev/null | sort -hr | head -25`
   - 再对**前 10 大**各做 `timeout 120 du -sh --max-depth=1 <子目录>` **二级下钻**（分轮做，避免单块超时）。
5. **他人目录（sudo，只读排查）**：对 `/nas_train/*/` 的**顶层**做**有界** `du -sh --max-depth=1`（**每条带 `timeout`，每轮最多 3~4 个**）；
   标出 **mtime > 60 天** 且 **无活跃进程占用**（`pgrep` / `fuser` 二次确认）的大目录，给出 `owner / 大小 / mtime / 疑似用途`。
   ⚠️ 跨用户删除**必须**由运维或 owner 确认；本线**只产出清单**。
6. **产出**：更新 `run/DISK_CLEANUP_INVENTORY.md` —— 新增 **§8「2026-10-04 大盘复扫」**：
   表 = `路径 | owner | 大小 | mtime | 安全等级(🟢可清/🟡需确认/🔴不可动) | 判据/证据 | 建议`，并给 **可回收合计（分档）**。
   → 同时回写 `MEMORY_DATA.md`「运维问答」区一句结论。

**🔴 红线（绝不可动）**：`base/gpic` 下载目标 · `L3/code/math` · `SFT-2605` · `GPIC` · `en500k/eval5k` · `p5b_l3` · `EDA-Eval` 隔离区。
**优先级**：轻 I/O（`df` + 有界 `du`），**与下载巡检并行**；重 I/O 仍避让训练。

**⭐ 用户点名的重点目标（2026-10-04 追加）**：
> 用户在 **`LLaVA-OneVision-1.5`** 目录下做过大量实验，**沉淀了大量 4B 模型的检查点 —— 这些检查点绝大部分可以删除**。
- 因此本轮盘点**必须单列一节**：定位 `LLaVA-OneVision-1.5` → 列出 **所有 ckpt/checkpoint/output/save/4B 目录**的**大小 + mtime + 数量** → 估算 **可回收合计**。
- 参照已有先例：`servers/`（974 G，同类 LLaVA 旧训练 ckpt）已于 **D-CLEAN-3** 安全删除（前置 P1/P2/P3 全过、外部 symlink 未被跟随）→ **本次同类目标可沿用同一套前置检查**。
- ⚠️ 仍**只盘点不删除**；但请**标明哪些属于"用户已确认可删"**这一类，便于运维一次性拍板。


> 背景：几个盘空闲空间**在持续变小**（`/nas_train` 已用 ~85%、仅剩 ~31T）。运维要求**盘点可回收空间**，**包括但不限于本用户目录**（也可查**他人久已不用**的目录）。
> 🚫 **本任务 = 「只盘点、不删除」** —— 产出候选清单交运维拍板；**未经批准不得 `rm`/`mv` 任何东西**。
> 🔒 **红线**：`EDA-Eval-PyAether` 158 任务只读隔离区、以及**任何正在下载/训练的目标**，**绝不可动**。

**步骤（全部贴命令 + 原始输出，不许猜）**：
1. **大盘**：`df -hT /nas_train /nas_inference /nas_user /data`（**禁止全树 `du`**；每条 `du` 都带 `timeout` 且限定深度/单目录）。
2. **本用户（`app.e0031982`）可回收候选**，按安全等级分级：
   - 🟢 **明确可清**：HF cache 中**已下满且已确认**的重复 blob、pip/conda 缓存、`/tmp` 大文件、core dump、旧 `*.log`。
   - 🟡 **需确认**：**旧 checkpoint**（Nemo `nemo_experiments/*`、vision `R*/…`）、**下载中断残留**（`.incomplete`）、**重复数据副本**（❗已知 base-en 旧副本 **1.67TB 已被复用** → **不要删**）。
   - 🔴 **不可动**：**正在用**的（`p5b_l3/*`、base/gpic 下载目标、SFT-2605、L3/code/math、GPIC、en500k/eval5k）、EDA-Eval 隔离区。
3. **他人目录（只读排查，只报告不碰）**：扫 `/nas_train/*/` 的**顶层**，标出 **mtime > 60 天** 且**无活跃进程占用**的大目录；给出 `owner / 大小 / mtime / 疑似用途`。
   - ⚠️ 跨用户删除**必须**由运维或 owner 确认；本线**只产出清单**；扫描用 `df` + 有界 `du` + `pgrep`/`fuser` 二次确认，**不做全树扫描**。
4. **产出**：`run/DISK_CLEANUP_INVENTORY.md`（表：`路径 | owner | 大小 | mtime | 安全等级 | 判据/证据 | 建议` + **可回收合计（分档）**）+ 回写 `MEMORY_DATA.md`「运维问答」区一句结论。

**优先级**：与现有下载巡检**并行**（D-CLEAN 属轻 I/O：`df` + 有界 `du`）；**重 I/O 仍避让下载与训练**。

### 🆕 运维指令 · 2026-10-03（**D-CLEAN-2：已批准删除项 + `servers` 探查**）

> 运维已对 `DISK_CLEANUP_INVENTORY.md` 的候选拍板。**执行前先记录（路径 + `du` 实测 + `df` 前），执行后回写 `DISK_CLEANUP_INVENTORY.md` + `MEMORY_DATA.md`。**

**✅ 已批准删除（可执行 `rm -rf`）**：

| # | 路径 | 大小 | 备注 |
|:--|:--|--:|:--|
| 1 | `.../datasets/laion2B-en-aesthetic/` | **≈8.1 T** | URL-only 已淘汰（DATA_LEDGER §6）→ **最大回收项** |
| 2 | `/nas_train/app.e0031982/zhulong.tar.gz` | 493 M | ZhuLong 旧打包（2026-03-06），运维确认可删 |
| 3 | `.../code/BaiZe-ISEDA2027/nemo_experiments` | **524 G** | **只删「早期、已不再需要的 ckpt」**（＝ data agent 原建议「保留最晚/最优，其余可清」）；**保留最晚/最优 + P-6② 所需里程碑**（见下） |
| 4 | `/home/app.e0031982/.cache/pip` | 3.3 G | 🟢 缓存，可从 PyPI 重建（顺带清） |

**🔴 `nemo_experiments` 保留 / 清理规则（**先列清单、再删**；**不删整个目录**）**：
- **P-5b 正在往这里写**（`--save-interval 156 --dir nemo_experiments`）→ **🚫 绝不动任何近期 mtime 的目录**。
- **保留（最晚/最优 + P-6② 所需）**：**最新一个** + **P-6② 的 6 个里程碑 ckpt**（`--save-interval 156` → 约 `iter_0000156 / 0000312 / 0000624 / 0001248 / 0002496` + **final `iter_0004771`**；**以实际落盘名为准**）。
- **可清（早期、已不再需要）**：Round 1 / S 系列等**被更晚 ckpt 取代、且无后续用途**的旧 ckpt。
- **流程**：先 `ls -la --time-style=long-iso` 列清单 → 贴「保留 / 可清」两列到报告 **再删**。
- ⚠️ 若无法可靠区分「早期不再需要」与「仍需」→ 本轮**只列清单、不删**，等运维二次确认。

**🔍 待探查（**先不删**）：`/nas_train/app.e0031982/servers`（974 G）**
- `ls -la --time-style=long-iso servers/` + `du -sh --max-depth=1 servers/*`（**每条带 `timeout`**，避免全树超时；已知子目录 `du` 会超时）。
- 产出：**内部结构 + 用途判断 + 建议**，写进 `DISK_CLEANUP_INVENTORY.md` 新节。

**❌ 本轮不动（保持「待确认」）**：`models`(452G) · `hf_cache`(20G) · `outputs` · `download` · `Downloads` · 旧 filelist/checksums · **LLaVA 85M（26T，运维令保留）**。
**🚫 红线不变**：base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k、`EDA-Eval` 隔离区。

**产出**：更新 `DISK_CLEANUP_INVENTORY.md` —— **实际回收合计（`df` 前后对比）+ `servers` 探查结论**；口径仍**贴命令 + 原始输出**。

### 🆕 运维指令 · 2026-10-03（**D-CLEAN-3：删除 `servers/`（974 G）**；`nemo_experiments` R2 ckpt **不删**）

> 运维拍板（2026-10-03）：① ✅ **`servers` 可以清理**；② 🚫 **`nemo_experiments` 的 R2 近期 ckpt 先不清**（**保留**）。
> ⚠️ 这是 **974 G 的 `rm -rf`** → **必须先过下面 3 道前置检查**；**任一不过 → 停手 + 报告，不要删**。

**前置检查（三项全过才删；每条贴命令 + 原始输出）**：

| # | 查什么 | 怎么查 | 不过怎么办 |
|:--|:--|:--|:--|
| **P1** | **无进程占用** | `fuser -vm /nas_train/app.e0031982/servers 2>&1 \| head -20`；并核 `pgrep -af` 是否有训练/推理在读该目录 | **停手报告** |
| **P2** | **无近期活动** | `find /nas_train/app.e0031982/servers -newermt '-7 days' -print 2>/dev/null \| head -20`（应为空或仅无害项） | 有近期写入 → **停手报告** |
| **P3** | **无脚本引用** | 在共享工作副本内 grep：`grep -rn 'app.e0031982/servers' /nas_train/app.e0031982/code --include='*.sh' --include='*.py' --exclude-dir=.git 2>/dev/null \| head -10` | 被引用 → **停手报告** |

**执行（只有 P1/P2/P3 全过才做）**：
1. 删前记录：`df -BG /nas_train | tail -1` + `timeout 300 du -sh /nas_train/app.e0031982/servers`（**带 timeout**）。
2. **列 symlink**（供留证）：`find /nas_train/app.e0031982/servers -maxdepth 3 -type l -printf '%p -> %l\n' 2>/dev/null | head -40`
   - 说明：`rm -rf` **不跟随**符号链接（只删链接本身）→ 指向 `servers` **外部**的目标**不受影响**；但仍要列出发现的 symlink。
3. `rm -rf /nas_train/app.e0031982/servers`
4. 删后记录：`df -BG /nas_train | tail -1`，并核 `[ -d .../servers ] && echo STILL || echo GONE`。

**🚫 明确不动**：`nemo_experiments` 的 **R2 近期 ckpt**（`p1_*`/`p2_*`/`p3_*`/`p5a_*`/`p7_*` ~135 G，**保留**）与 **`p5b`**（live）。

**产出**：更新 `run/DISK_CLEANUP_INVENTORY.md` **§7**（P1/P2/P3 结果 + 删前后 `df` + 实际回收 + symlink 清单）；**贴命令 + 原始输出，不许猜**。

## 0.5 🔴 R3 阶段 —— **为 P-8 定数据 + 处置 base 旧副本**（运维 2026-10-02 指令）

> **运维明确**：**(ii)/(iv) 不急**；**Stage (i) 的 P-8 是当前主线**，其**启动配置（尤其"用什么数据"）需要慎重**。
> **🚫 另外：10 月份不要再提任何"领域化"相关的事**（EDA / 领域语料 / Stage (ii) 领域模型 —— 全部留白）。

### A. ✅ 确认并**持续推进 Ultra-FineWeb（base）下载**（**运维点名**）

- 该下载**已在跑**（`hf download openbmb/Ultra-FineWeb --local-dir /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb`，pid 2040865，进程存活）。
  → **保持推进，不要中断**；每轮唤醒报进度。
- 规模：**2.99 TB / 64624 文件**（en `ultrafineweb_en` 2048 + `ultrafineweb_en_v1_4` ~62k + `ultrafineweb_l1_en_hq` + `ultrafineweb_zh` 256）。
- ⚠️ **这是 P-8 的候选主料之一** —— 下完后要**过 `check_contamination.py`**、并给出**实测 token 数**。

### B. ⭐⭐ **base-en 旧副本（1.67TB）的正确处置 —— 先别删，先看能不能"复用"**

> **运维问：`/nas_train` 残留的 `base-en 1286/2048` 到底是啥、是不是没用的数据？**
>
> **已查明（见 `DATA_RESEARCH.md` R2-A 校正）**：
> - 它是 **`Ultra-FineWeb` base 的英文 config（`ultrafineweb_en`）的一份 2026-02 旧下载**，
>   位于 `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en/`，
>   **1286/2048 parquet（1.67 TB）**，**含 13 个 `.incomplete`**。
> - 它与**正在下的 `/nas_inference` 那份同名同构** → **新下载会把这 1286 个重下一遍**。

**所以任务不是"删不删"，而是按下面顺序处理：**

1. **先判断能否复用（省时间的正解）**
   实测带宽 **≈9.4 MB/s / 1.3GB 每片** → 重下 1.67 TB ≈ **49 小时 ≈ 2 天**。
   - 检查**新下载的 `--local-dir` 结构**与旧的 `/nas_train/.../data/ultrafineweb_en/` 是否可以直接对接
     （`hf download` 会按**文件大小/etag** 判断是否已存在而跳过）。
   - **若可复用** → **改把 base 的下到 `/nas_train` 旧目录**（或把旧目录 mv/rsync 过去），**让下载从 1286 续推**。
     ⚠️ 跨 NFS 硬链不可行 → **优先"改下载目标"而不是"搬文件"**。
   - **给出量化结论**：复用能省多少小时 / 多少 TB。
2. **若不可复用 → 再决定删留**
   - ⚠️ **删之前必须抽样校验**：旧的 1286 个 vs 新下的对应文件，**大小/etag 是否一致**
     （旧的是 **2026-02** 的版本，**上游可能已更新** → 若不一致，旧的属于**过期版本**，删掉是对的）。
   - 先把 **13 个 `.incomplete`** 清掉（无价值）。
3. **报账**：`/nas_train` 只剩 **32T**，这 1.67TB 占 **5%** → 给出"删能回多少 / 复用能省多少"的对比。

### C. 🎯 为 P-8 给出**数据方案定稿**（**这是本轮的最终产出**）

P-8 是 Stage (i) 本体，**启动配置要慎重**。基于已交付的 §0.3 + 本轮 A/B，给出：

1. **P-8 用什么数据、什么配比**（含 base 是否入选、入选后配比怎么调）
2. **实测 token 数**（不要把字节当 token —— 这是我们踩过的坑）
3. **`.bin/.idx` 切分方案**（复用 Round 1 脚本）+ 落盘路径 + 体积
4. **磁盘可行性**（`/nas_train` 32T；P-8 ckpt 每个 ≈30GB）
5. **可复制命令**

### 完成判据
- [ ] base 下载**连续推进**（无中断）
- [ ] **base-en 复用可行性**给出**量化结论**（省多少小时/TB），并据此给出**删 / 留 / 复用**的决定
- [ ] **P-8 数据方案定稿**（含实测 token、配比、切分、磁盘、命令）
- [ ] 🚫 **全轮不得出现领域化相关内容**

## 0.7 🔴 R5 阶段 —— **下载优先级调整 + 估时 + P-8 暂缓**（运维 2026-10-02 指令）

> **运维明确**：**P-8 暂缓启动** —— 因为它**依赖 base 下载**与**配比实验**，而这两件都要时间。
> 因此当前优先级：**① 下载 base（stage (i) 要用）② 配比实验 ③ gpic（stage (iii) 要用）**。

### A. 🚫 **停掉 85M（LLaVA-OneVision-1.5）下载** —— 优先级最低

**运维原话**：`.12` 上有三份数据在下载：**① base ② 85M ③ gpic**；
**stage (i) 需要 base，stage (iii) 需要 gpic，只有 85M 优先级较低，可以先停下。**

**执行**：
1. **找出并停掉 LLaVA 85M 的 `hf download` 进程**（此前实测 pid **3464918**，会变，**按命令行匹配**）：
   ```bash
   pgrep -af 'hf download' | grep -i 'LLaVA-OneVision-1.5-Mid-Training-85M'
   ```
   → 确认无误后 `kill <pid>`（**保留已下内容，不要删**）。
2. **释放的带宽给 base 与 gpic**。
3. ⚠️ **记录**：已下到哪（此前 **7629 parquet**）、停在哪，写进 `MEMORY_DATA.md`。
   - **注意**：`en500k`（已在盘上、R5/R8 用过）与 `eval5k` **不受影响**，vision 侧继续可用。
   - 85M 是**将来扩充 vision 数据**用的，**不是当前实验的阻塞项**。

### B. ⭐ **估计 base 下载需要多久**（**运维点名要**）

给出**量化估计**，必须含这三点：

1. **实测当前速率**（停掉 85M **之后**再测一次，与停之前对比 → 说明"停 85M 到底提速多少"）。
2. **剩余量与 ETA**：
   - 总量 **2.99 TB / 64624 文件**；当前 **~115/64624（≈140 GB，≈4.7% 字节）**。
   - ⚠️ **注意文件大小极不均**：**`ultrafineweb_en` 那 2048 个 ≈1.3 GB/个 ≈ 2.66 TB（占全部 ≈89%）**，
     其余 6.2 万个小文件（`en_v1_4`）合计仅 ≈0.33 TB。**别用"文件数比例"估时间**。
3. **给两个 ETA**：**不复用旧副本** vs **复用旧副本**（见 C）。

### C. ⭐⭐ **复用 `/nas_train` 的 1286 个 `ultrafineweb_en` —— 能省 ≈56% 的下载量**

> **为什么这条现在价值极高**：旧副本那 **1286 个文件，正是 `ultrafineweb_en`（1.3 GB/个）里的** →
> **1286 × 1.3 GB ≈ 1.67 TB ≈ base 全量的 56%**。按 9.4 MB/s，**省 ≈49 小时 ≈ 2 天**。

**要做**：
1. **判断能否让新下载直接复用**（`hf download` 按文件大小/etag 跳过已存在文件）：
   - 检查**把 base 的 `--local-dir` 指向 `/nas_train/.../Ultra-FineWeb/`（旧目录）** 是否可行
     —— 即让下载**从 1286 续推**，而不是重下。
   - **跨 NFS 硬链不可行** → **优先"改下载目标"，不要"搬 1.67TB 文件"**。
2. **若不可行** → 抽样校验旧 1286 与新 2048 中对应文件的大小/etag：
   - **一致** → 走 rsync/cp（但 1.67TB 的拷贝也要时间，要算进去）
   - **不一致**（旧的是 2026-02 版本，上游可能更新）→ **旧的属过期版本 → 删掉，老实重下**
3. **报账**：`/nas_train` 只剩 **32T** → 给出"复用能省 X 小时 / 删能回 1.67TB"的对比。

### D. **配比实验**（见 §0.6）—— 与下载并行推进
- **先把方案与数据就绪清单出了**（不需要卡）。
- 🎯 **用哪台机器（运维规则）**：**配比实验用「它所服务的那个正式训练」所用的机器**
  —— **LLM 侧（§0.6）用 `.29`**；**若将来 vision 也要做配比 → 用 `.12`**。
- ⚠️ **`.29` 上的排期**：**P-4R（1 卡 ≤2h）→ 配比实验 → 恢复 P-5b**（三者都在 `.29`，需串行）；
  **`.12` 上 R9 在用 8 卡，不要占**。

### 完成判据
- [ ] **LLaVA 85M 下载已停**（并记录停在哪）
- [ ] **base 下载 ETA 已给出**（含停 85M 前后的速率对比 + 复用/不复用两个 ETA）
- [ ] **复用 1286 个的可行性有明确结论**（省多少小时/TB）+ 据此定"复用/rsync/删"
- [ ] §0.6 的配比方案与数据就绪清单已出
- [ ] 🚫 **全轮不得出现领域化相关内容**

---




- `LLaVA-OneVision-1.5-Mid-Training-85M`（本地实测：EN 5545 + CN 1512 parquet，**下载中**）
- **`Stanford GPIC`**（`/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/`，
  含 `train` / `test` / `reference_stats`；tar 内 `{key}.json` + `{key}.jpg|png`，
  **caption 分 `tag` / `short` / `medium` / `long` 四档**）
- 各给：**图像数 / 对数 / tar 数 / 总字节 / 许可证**。

**(2) ⭐ caption 长度分布 —— 这是关键**
- 对**每份数据、每一档 caption**，统计**词数**与 **CLIP token 长度**的分布。
- 判据：`open_clip.tokenizer.SimpleTokenizer` 的**上下文长度是 77，超出即截断**。
- **必须给出"会被截断的比例"**；并**特别标出 GPIC 的 `tag` / `short` 是否正好落在 77 以内**。
- 🔑 **这是本问题最想要的结论**：若 LLaVA 长 recaption 被大面积截断、而 GPIC 的 `tag`/`short` 不被截断，
  则**换数据（或换 caption 档）本身可能就解决大半坍缩问题**。

**(3) 配比怎么定？**
- 85M（含 EN/CN）与 GPIC **怎么混**？caption 用哪一档？
- 给**具体建议 + 理由**，必须结合 (2) 的截断分析。

**(4) 是否需要在 HF 继续寻找？**
- 公开的**版图 / 原理图 / 电路图**视觉数据集有哪些（规模、许可、可得性）？
- ⚠️ **只给"是否值得引入"的判断**，不要展开长篇综述。

### R 阶段执行要求（逐条遵守）

1. 🚫 **只做上面两个问题**，**不要扩展**到 agentic SFT/RL 数据、长上下文、去污染方法、偏好数据等
   —— **那些本阶段一律不做、不写**。
   ⚠️ **EDA 语料已是"正式取消"，不再是"本阶段不做"** —— **永久不做**（见运维指令区 ②）
2. 每问产出一张表：`候选源 | URL | 规模 | 许可 | 可得性 | 建议 | 优先级`
3. **必须给 URL**；头部候选要用 `cimi-fetch` **抓正文核实**，**不要只凭搜索结果标题下结论**
4. **区分三类可得性**：`公开可直接下载` / `需申请或注册` / `仅论文描述（无公开数据）`
5. **许可写清**（Apache / MIT / CC-BY / 仅研究 / 不明），**"不明"显式标红** ——
   论文写了 "we release the recipe"，数据许可直接影响可发布性
6. **先与本地对照**（`DATA_LEDGER.md` §0 / §3 与任务书 §1.1），避免调研已就位的东西
7. 🚫 **只调研，不下载**
8. **不滥用搜索**：每问聚焦 3–8 条高线索，**宁可少而核实，不要多而未核实**

### R 阶段的完成判据

`run/DATA_RESEARCH.md` 中：

- **问题 1（LLM pretrain）**：四小项全部有结论；给出**"数据够不够"**与**"配比走 A 还是 B"**的**明确建议**；
  并完成两个**必答判定**：① **MiniCPM5 是否下全**；② **论文 §4 的 "≈1.8T tokens" 是否写错**。
- **问题 2（Vision encoder）**：四小项全部有结论；给出**"85M + GPIC 行不行"**与**"配比怎么定"**的**明确建议**；
  **必须包含 caption 截断比例的量化分析**（对 77-token 口径）。
- 每条关键结论都能顺着 URL 复核。

---


---

### 🔴 运维指令 · 2026-10-06（配比实验改道）① 立即动作 —— 已执行（2026-10-06 从 BAIZE_DATA_TASK.md 移出）

#### ① 立即动作（**第 0 步，先做这个**）

- 🔴 **kill 当前 `mix_stable_s0a`**（**data 线自己的进程**，重启后 PID `2528081`–`2528090`，端口 `29950`）→ **释放 `.29` GPU2–7**。
- 已跑的 **~1350 步作废**；**如实**记进 `MEMORY_DATA.md` 流水（**不许粉饰**、不许写成「阶段性成果」）。
- `report_data_mix_s0a.html` **保留为历史**：标题加后缀「（**已废弃方法 · 目标尺寸单臂**）」，**不再更新**。
- `run/baize_mix_stable_s0a.sh` **停止调用**（保留文件，标注 `# DEPRECATED 2026-10-06：2.2B 单臂方案作废`）。


### 🆕 运维指令 · 2026-10-05（深夜2 · HTML报告）—— 已完成（report_data_mix_s0a.html 已产出）

### 🆕 运维指令 · 2026-10-05（深夜2 · ⑤ **写一份 HTML 报告讲清「Stable S0a 配比实验是什么 + 现在到哪了」**）· 高优先

> **用户 2026-10-05 深夜**：「**数据配比实验（Stable S0a）是做什么，写个 html 报告**」。

- **报告必须讲清**（面向「领导 / 1400 DE」读者，不是只给本线看）：
  1. **它是什么**：**§0.6-B「P-8 数据配方」实验** —— 用 **MiniCPM5 / Xmodel-2 的 WSD 双阶段配比**思路，在**小规模代理预算**下搜索 **Stable 段（base 主体）** 与 **Decay 段（L3+Math+Code+SFT = 带 SFT 的退火）** 的最佳配比。
  2. **Stable S0a 臂具体是什么**：**`base:code:math = 88:8:4`** · **6 卡 DP6** · `seq=4094` · `mb=1` · **`GBS=1020`**（因 DP6 整除，较基线 1024 **−0.4%**，**须标注可比性**）· **5000 步** · bf16 · seed1234 · 脚本 `run/baize_mix_stable_s0a.sh`。
  3. **为什么这么设计**：搜索空间 = §0.6-B 的 **Stable / Decay 两张表**；每臂跑完用**两套代理指标**：**Table 2 的 8 个**（`ARC-C`/`ARC-E`/`BoolQ`/`HellaSwag`/`OpenBookQA`/`PiQA`/`SciQ`/`Winogrande`）+ **Table 3 的 6 个**（`GSM8K`/`MATH`/`BBH`/`MMLU`/`HumanEval`/`MBPP`）。
  4. **当前状态（用代码里的实时数，别照抄旧数）**：`step 330/5000`、`~37.6 s/iter`、`ETA ~2026-10-07 21:00`、`loss 4.36↓`、health OK（0 NaN/0 skip）；⚠️ **`SAVE_INTERVAL=5000` → 无中间 ckpt**（如实写风险）。
  5. **下一步**：5000 步完 → ckpt → HF → `lm_eval` Table 2（8 集）→ 填 `DATA_MIX_RECIPE.md` 实测值；**Decay 臂**待 `SFT-Agent-2609` s0/s1 分词完成。
  6. **它最终服务于什么**：**P-8（正式预训练）的投料配比** —— 即论文 Stage (i) 的配方依据。
- **数据来源**：`BAIZE_DATA_TASK.md §0.6-B` · `MEMORY_DATA.md` · `EXPERIMENTS*` · `run/baize_mix_stable_s0a.sh`（**贴命令 + 原始输出 + 路径**，铁律）。
- **产出**：`report_data_mix_s0a.html`（**自包含、无 CDN**，放 `doc/BaiZe-ISEDA2027/`）。

> ✅ 本块生效即视为已批准；**纯 CPU/写作，不占 GPU、不干扰 S0a 训练**。



### 🆕 运维指令 · 2026-10-05（D-CLEAN-4 定案 + 环境隔离）—— 已执行

### 🆕 运维指令 · 2026-10-05（晚 · ✅ **D-CLEAN-4 定案：保留不动**；+ 环境隔离纪律）

> **用户裁定（2026-10-05 晚）**：「**D-CLEAN-4 …… 不是昨天已经说了，剩下的保留不动嘛**。」

- ⇒ **D-CLEAN-4 终止**：**不再删除、也不再盘点**（此前「待拍板」**作废**）。请把 `MEMORY_DATA.md` / `run/DISK_CLEANUP_INVENTORY.md` 里 D-CLEAN-4 的状态改为「**已裁定 · 保留不动**」，并**停止**在报告/流水里把它列为「待拍板」。
- **红线重申（不变）**：`EDA-Eval-PyAether` 只读隔离区、base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k **均不可动**。

**环境隔离纪律（治「同机争用」—— 用户裁定）**
- **训练/长跑 = 共享 `py310`**（不动）；分词/转换等 CPU 重活照旧；**需要大量装包时另起独立 conda env**（🚫 别动共享 `py310`，避免重蹈 P-9.8 armB 被污染崩溃）。
- 你与 pretrain 共用 `.29` GPU（**GPU2–7 归你 / GPU0–1 归 pretrain**）—— **不许 kill 对方进程**，重 I/O 继续避让。

> ✅ 本块生效即视为已裁定。


### 🆕 运维指令 · 2026-10-05（分卡协调 GPU2-7）—— 已执行（配比实验已开工）

### 🆕 运维指令 · 2026-10-05（**🟢 分卡协调：`.29` GPU2–7（6 卡）归你 → 开始做「配比实验」，与 pretrain 的对比评测并行**）⭐ 高优先 · **已批准**

> **用户拍板（2026-10-05）**：「**给 pretrain 补一个对比评测任务**（要 GPU）——**它不需要 8 张卡**；**让它和 data 协调一下：pretrain 做对比评测时，data 可以同时做数据配比试验**。」
> ⇒ **§0.6-B 的配比实验，卡终于有了**（此前一直卡在「等 `.29` 让卡」）。

#### ① 卡的分配（**铁律** —— 完整账本见 **`run/GPU29_ALLOC.md`**）

| 机器 | 卡 | 归谁 | 用途 |
|:--|:--|:--|:--|
| `.29` | **GPU 0–1** | pretrain | P-9.10 推理对比评测（≤2 卡） |
| `.29` | **GPU 2–7（6 卡）** | **data（你）** | **数据配比实验** |

- ⏳ **起跑前置**：**先等 P-9.8 arm B(FP8) 跑完**（它现在占满 8 卡，ETA ~09:49）——
  判断依据：`run/MEMORY_PRETRAIN_2B.md` 状态头 + `ssh 10.239.2.29 nvidia-smi`。
  **等待期间你继续做「文献调研重做」（上方块）—— 那是当前最高优先。**
- 📢 **动态让卡（双向）**：你**只碰 GPU2–7**；要更多卡（或 pretrain 要更多卡）→ **在 `run/GPU29_ALLOC.md` 的「申请区」写一行**（几张/多久/为什么），
  **等对方在「臂边界 / step 边界 / 任务边界」让出**；🚫 **不许抢跑、不许 kill 对方进程**。
  **你自己的「臂与臂之间」就是天然让卡点**（每臂约 25–50 min）。
- 🚫 **`/nas_train` 是 `.12` 与 `.29` 共享的同一块 NFS**：你与 pretrain、vision 同盘 ⇒ **重 I/O（全量扫描 / 解包 / `du`）照旧避让**。

#### ② 怎么在 `.29` 上跑（你常驻 `.12`）
- **代码/数据不用搬**：工作副本是**共享 NFS**（`/nas_train/app.e0031982/code/super_intelligence_2035`，两台看到的是同一份）。
- 用 **`ssh 10.239.2.29 '<cmd>'`（免密已通）** 起训练；🚫 **不要在 `.12` 上再跑同一任务**。
- **第一件要做的事 = 只读可行性核查**（把**原文**贴进 `MEMORY_DATA.md`）：
  1. `ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'` → 确认 **GPU2–7 空**（若有**他人进程 → 停手报告**）；
  2. 找 pretrain 的现成脚本 / recipe：`run/baize_p5b_train.sh`、`run/baize_p9*.sh`、`code/BaiZe-ISEDA2027/scripts/train.sh`、`code/BaiZe-ISEDA2027/pretrain_launcher.py`
     （参考 `run/BAIZE_PRETRAIN_2B_TASK.md` §R2.2 的固定口径）；
  3. 训练数据 `.bin/.idx` 是否就位；`PYTHONPATH` / python 环境能否起（见 `MEMORY_PRETRAIN_2B.md`「关键笔记」）。
- 🔑 **不要从零发明**：**复制** pretrain 的脚本成**你自己的** `run/baize_mix_*.sh` 再改配比；🚫 **不要改 pretrain 正在用的脚本文件**。
- ⚠️ **若环境/权限确实起不来**（ssh 不通、环境装不上…）→ **立即如实报告**（贴原文）并在 `run/GPU29_ALLOC.md` 写一行
  → **降级方案：你出「配比矩阵 + 数据切分 + 评测口径」，由 pretrain 代跑**（它已在 `.29` 上）。

#### ③ 实验设计（**沿用 §0.6-B，不要重造**）
- 搜索空间照 §0.6-B 的 **Stable / Decay 两张表**。
- **口径**：**6 卡 · TP1/DP6 · `seq=4094` · `mb=1`** · **GBS 与既有基线对齐**（若必须改 GBS → **在报告里显式写出并说明可比性**）· **5000 步短地平线**（或更短，但**所有臂必须一致**）。
- 每臂跑完 → 跑 **§0.6-B 的两套代理指标**：
  **Table 2 的 8 个**（`ARC-C` / `ARC-E` / `BoolQ` / `HellaSwag` / `OpenBookQA` / `PiQA` / `SciQ` / `Winogrande`）+
  **Table 3 的 6 个**（`GSM8K` / `MATH` / `BBH` / `MMLU` / `HumanEval` / `MBPP`）。
- **评测基建请复用 pretrain 已打通的 `ckpt → HF → lm_eval`**（见 `MEMORY_PRETRAIN_2B.md`）；Table 3 那 6 个若缺 → **先评估工作量并报告**，不要闷头造。
- **每臂必记**：配比百分比 · loss · 代理指标分项 · 命令 · 路径 · **GPU 核验原文**。

#### ④ 交付与优先级
- 交付：`run/DATA_MIX_RECIPE.md`（§0.6-C 原定：**具体百分比 + 试验次数 + 实测值 + 可复现命令**）；
  每臂一行进 `MEMORY_DATA.md` / `DATA_LEDGER.md`；**做不完就交「已完成臂 + 缺口」**，🚫 **不许凑数**。
- **优先级**：**文献调研重做（上方块）≥ 本块** —— 等 armB（~09:49）这段时间**先干文献**；armB 一完就**两件事并行**（你 6 卡 / pretrain 2 卡）。
- 🚫 **全轮不得出现领域化相关内容**（既有硬规矩，不变）。

> ✅ **本区块生效即视为已批准** —— 无需再等拍板。

---

## 📦 归档批次 · 2026-10-06 唤醒150（任务书体积压缩 40.4KB→~32KB）

> 以下为从 `BAIZE_DATA_TASK.md` 原文搬迁的已闭合内容，**不改一字**。

### 1. §B 开工前 5 项必验（第5轮块内，2026-10-06）— 全部 PASS

#### B. 开工前 5 项必验（**不验 = 两天的结果作废**；顺序 = 优先级）

1. ⭐⭐ **可分辨性证伪（最该先做、最可能一票否决）**：18.5M 里 **90% 是 embedding、真容量只有 `body ≈ 1.91M`** ⇒ 先跑**强对比**：**`code=0%` vs `code=30%`**（其余给 base），**各 3 seed**，同一 held-out bin、同步数 ⇒ 报 **`Δloss` 与 `σ`（3 seed 标准差）**：
   - `Δloss > 2σ` ⇒ 规模**可用**，继续；
   - **`Δloss` 落在 `σ` 内 ⇒ 该规模作废**：按 §③.6 阶梯**回调**（`d=160/L=14` 23.7M → `d=192/L=14` → `d=256/L=14` 40.8M），**并重报 `T` 与可达 trial 数**。⇒ **宁可 300 组「能分辨」，也不要 512 组全是噪声**；🚫 **不许**「照跑 512 组、事后挑好看的」。
2. **`d=128` 结构合法性冒烟**：`heads = d/128 = 1`、`n_groups ≤ heads`、`d_inner = 2d = 256`、`ssm_state=128` 与 `head_dim` 整除关系 ⇒ **先 `numel()` 分模块（embed / body）打印 + 20 步冒烟**（GBS16 · seq2048 · **1 卡**），**贴原始输出**。非法 ⇒ 依次 `d=160/L=14`（23.7M，body 3.0M）→ `d=192/L=14` → `d=256/L=14`（40.8M），**每次重报 `T`**；仍非法再回 `h=512/L=14`（96.8M，备用档）。

3. **2B 是否 tie（决定 body 系数 `8.32` 还是 `7.19`）**：用 `pretrain_launcher.py --arch mamba2` 的 **2B config** 起模型（**1 卡、不训练**），**分模块 `numel()`** 打印 embed / body ⇒ 若实测 ≈ `8.32·d²·L` 则 **tie**（`share_embeddings_and_output_weights=True`）、≈ `7.19·d²·L` 则 **untie**。**把实测数字写进 `MEMORY_DATA.md`**（这是本仓库 8.32 / 7.19 两个系数的**唯一准据**）。
4. **`s_step` 实测**：口径 = `d=128/L=14` · **1 卡** · GBS16 · seq2048 · **≥50 步取中位数**（贴原始日志）；有条件**同时报 GBS128 的 `s/step`**。⇒ 用 **`T = 6×86400 ÷ [ 步数 × s_step × (1+ε) ]`**（`ε` 查 §③.9）**重算 `T` 并写死到 `MEMORY_DATA.md`**。
5. **LR 三点重扫**：`LR ∈ {3e-4, 1e-3, 3e-3}`（**proxy 的 LR ≠ 2.2B 的 `1e-3`**），按**固定 held-out val loss** 选一个并**全程固定** ⇒ 不扫 = **把「LR 不对」误判成「配比不好」**。

### 2. §A 事故复盘（用户复核②块内，2026-10-06）— 已闭合

#### A. 事故复盘（可核验，**不许辩解、只许修**）

| # | 事实（附核验点） | 责任 |
|:--|:--|:--|
| **A1** | `report_data_mix_s0a.html:111` 章节标题写着「**为什么要「做实验定配比」而不是拍脑袋？**」，而 §3 给出的却是一张「**工作假设配比表**」（88:8:4 直接来自先验）⇒ **以「实验」之名交付了一个先验** | data agent：**名实不符** |
| **A2** | 全程**只有 1 条臂（S0a）**；报告 `:133/:341/:362/:373` 却写「**选出最优配比**」⇒ **单臂下不存在「最优」**（无对照、无排序、无不确定性），结论**不能由数据推出** | data agent：**结论越界** |
| **A3** | 我把任务写成「§0.6-B 配比实验」，**从未定义「实验」的可检验形态**（多少组 / 怎么搜 / 判据 / 交付物）⇒ 等于给「用直觉填空」留了口子 | **运维：根因在我** |
| **A4** | 已烧算力：10-05 15:25 起 → 10-06 07:43 = **16.3h × 6 卡 ≈ 98 GPU·h**（step 1410/5000，loss 2.93，全程 0 NaN/0 skip）⇒ **≈ 一个完整搜索日预算（144 GPU·h）的 68%**；若不 kill，全程 ≈ **312 GPU·h ≈ P-8 本体的 13%** | 运维 + agent：**不可再续** |

> 📌 **A4 的正确对照**：这 98 GPU·h 若按新方案使用，**足够跑完 Stable 段搜索的 2/3**（≈200 个 trial）。**这就是「浪费了多长时间」的量化答案。**

### 3. §D 文档订正（用户复核②块内，2026-10-06）— 运维已加

#### D. 文档订正（**把「结论口吻」全部降级 —— 运维已在仓库侧先行订正**）

- `report_data_mix_s0a.html`：标题后缀「**（已废弃方法 · 目标尺寸单臂 · 非实验）**」+ **顶部红框声明**（**运维已加，见该文件顶部**）；正文 §6/§7 的「选出最优配比」口吻**不得再出现在任何新文档**。
- `run/DATA_MIX_RECIPE.md`：§3 表头已改「**未验证先验占比（待 BO 检验）**」+ §6 顶部已加改道订正框（**运维已加**）；**你要做的是**在 §6 重写完成后，**用实测 trial 表替换这些占位表述**。
- **纪律**：以上是**订正事实**，**不是「补写文档」**；**不许**把这些订正再「解释」成已完成的实验。

### 4. 运维指令区表格行（D-CLEAN-4/当前指令/优先级覆盖/状态索取/暂停标志，2026-10-01~04）— 已闭合/被取代

| **🆕 D-CLEAN-4（2026-10-04 · 最新）** | 🔴 **`/nas_train` 需要清理 → 用 sudo 盘点各目录大小，找可删除的大目录，重点 `/nas_train/app.e0031982`**；**只盘点不删除**；🚫 绝不整树 `du`（只用 `df` + 有界定向 `du`，每条带 `timeout`）→ 详见顶部「运维指令 · 2026-10-04（D-CLEAN-4）」 |
| **当前指令** | 🎯 **（2026-10-01 夜 · 三次修订）按序做这几件**：① ⭐ 重下 UltraData-SFT-2605（✅ 已完成）② 🔴 §0.3+§0.4 R2 阶段（✅ 已完成）③ §0.5+§0.6+§0.7（✅ 已完成/已改道为BO搜索） |
| **优先级覆盖** | §0.5/§0.6/§0.7 > 其他一切（全部已闭合/被运维指令区新块取代） |
| **状态索取** | `<无>` |
| **暂停标志** | `<无>` |



---

## 📦 2026-10-06 第二轮归档（唤醒156，从 BAIZE_DATA_TASK.md 移出，原文未改）

### §A 规模定案表（第5轮块内，2026-10-06）

#### A. 规模定案（🚫 **不许自行改**；若确因结构/性能改，必须在 `MEMORY_DATA.md` 写明「按 §③.6 哪一档、因何故」）

| 项 | 定案值 | 依据 / 口径 |
|:--|:--|:--|
| **型号名** | **`regmix_d128_L14`** | **与 RegMix 的 1–2M 非-embed body 同档**；同时是「1B token × 512 组 × 24h」的代数解 |
| **结构** | `d=128` · `L=14` · `ffn=512 (=4d)` · `mamba d_inner=256 (=2d)` · `ssm_state=128` · **`heads = d/128 = 1`** · `n_groups ≤ heads` · **tie embed** · pattern **严格保持 `24M:4*:28-` 比例**（`L=14` = 56 层的最小完整周期 `6M/1*/7-`） | 同上（比例一致 ⇒ 迁移性论证才成立） |
| **参数（预期值，以 `numel()` 实测为准）** | **`N ≈ 18.5M`** · **`E = 129,408 × 128 = 16.56M`（90%）** · **`body ≈ 1.91M`** | 总参 = **2.220B 的 1/120**；**非-embed = 1.955B 的 1/1027**（≈ RegMix 的 1/1000） |
| **`D`** | **1B token / trial** | GBS16×seq2048 ⇒ **30,518 步/trial**；GBS128 ⇒ **3,815 步/trial** |
| **`T`（含评测，`ε≈3%`）** | `η=1e14` → **394 / 448** · `η=1.5e14` → **548 / 660** · `η=2e14` → **681 / 863**（GBS16 / GBS128） | ⇒ **512 组要求 `η ≥ ~1.4e14`（GBS16）或 `≥ ~1.15e14`（GBS128）**；配 `MedianPruner` 后 **≈ 500–1200** |
| ⚠️ **`T` 的真实天花板** | **`N < 40M` 后瓶颈从算力转为「每步固定开销」（`t_fixed ≈ 3–8 ms`：launch + Adam + sync）** ⇒ `T` 实际**封顶 ~800–1200/天**；此时**唯一杠杆是提 GBS（§③.8-a）**，**不是继续缩模型** | §③.6 注 |

### §D 第0步分工（第5轮块内，2026-10-06）

#### D. 第 0 步的分工（**重要：防重复 kill**）

- ✅ **kill `mix_stable_s0a`：中继已核验（`RUN_ID 72`，2026-10-06 08:12:52）** —— `run/ops/inbox.md` RUN_ID 72 / 结果见 `run/ops/outbox.md` 末尾（含 `/tmp/restart_mix_stable_s0a.sh` 防重拉 + `crontab` 检查 + SIGTERM→SIGKILL + `nvidia-smi` 取证）。
  **实测结果：中继到场时已无 S0a 进程 ⇒ kill 是 no-op（它没杀任何东西）** —— GPU0–7 全空、重拉器已不存在、crontab 干净。**若这是你 08:0x 唤醒执行「第 0 步」的结果，判为正确**：只须把**你 kill 的原始输出**（`ps` / 日志尾巴）+ 时刻写进 `MEMORY_DATA.md`（**不许粉饰**：~1450 步作废）。
- ⇒ **你**：**不要再 kill 一次**（现在没有任何 S0a 进程可杀；重复 kill 只会误伤你新起的 trial）。
- ✅ **卡账本已由实测澄清（中继 `RUN_ID 72` 原始输出）**：`.29` **GPU0–7 全部 `0 MiB / 0 %`**（无任何计算进程）、**S0a 无进程**、`/tmp/restart_mix_stable_s0a.sh` **已不存在**、`crontab` **无重拉条目** ⇒ **原定的「GPU2–7 归 data」分配恢复生效，不必再等运维裁决**：现在就可以在 **GPU2–7** 上做标定 + 必验 ①–④（**先 1 卡标定，再铺 6 卡并行**）。
- ⚠️ **但必须登记**：开工/收工各写一行进 `run/GPU29_ALLOC.md`；若 **pretrain 同时要起 P-8** ⇒ 以**登记先后**为准，两边**不得同时占满 8 卡**（P-8 若起，你让到 2–4 卡并按 §③.8-a 提 GBS 把 `T` 保住），**并把该冲突立刻报运维**（心跳纪律同 §E）。
- 📌 **一句话**：**先把「这个规模能不能分辨配比差异」验掉；分辨不出就先放大，别急着上 Optuna。**

### 第5轮块头（用户两问+裁定，2026-10-06）

> **用户 2026-10-06 追加两问**：①「代理模型到底多小？」②「**若每 trial 1B token、24h + 6×H100 要跑 512 组，要多小？**（**要把评测时间算进去**）」
> **裁定**：把 `D=1B × 512 组 × 24h` 这条硬约束**代数求解**（`T = 6×86400 ÷ [ 步数 × s_step × (1+ε) ]`），得到**单一定档**：**`d=128 / L=14` ⇒ `N ≈ 18.5M`**（`E = 16.56M = 90%`、**`body ≈ 1.91M`**）。
> ⇒ **本块取代下块 §③.6 候选表里「`h=512`（定案）」的主选地位** —— `h=512/L=14`（96.8M）**降为备用**（仅在「必验 ② 结构不合法」时启用，见下）。

### 用户复核②块头（用户原话+裁定，2026-10-06）

> **用户 2026-10-06 复核原话**：「**配比实验是要【实验】，扫描大量可能配比，找到最优的。data agent 怎么做的，自己拍脑袋拍了【一个】出来（base:code:math = 88:8:4）。你是觉得你比人类直觉更强大还是怎么着？看到 `report_data_mix_s0a.html` 这份报告我吓坏了，浪费了多长时间！**」
> **裁定**：这不是「跑得慢」，而是 **跑的根本不是实验** —— 属**方法学级**错误，必须按本节订正。

### 改道方案裁定原文（配比实验改道块内，2026-10-06）

> **用户 2026-10-06 复核裁定**：现方案**方法学错 + 成本失控**，**即刻改道**。
> - ❌ **错在哪**：S0a 用的是 `pretrain_launcher.py --arch mamba2` = **与目标 P-8 同尺寸的 2.2B（`NVIDIAMambaHybridModelProvider2B`，2.220B）** ——
>   `DATA_MIX_RECIPE.md §6` 标题写着「无需全量 2.2B」，**执行却照跑全量**；且**只有 1 条臂 / 1 个 seed / 无中间 ckpt / 手挑网格**（全仓库 **0 命中** `optuna` / 贝叶斯 / grid / random search）。
> - ❌ **成本**：实测 **≈312 GPU·h / 臂**（配方里原估 0.5–1 GPU·h，**差 ~50×**）；按 40 臂算 ≈ **12,480 GPU·h ≈ 5.2× P-8 本体（~2,400 GPU·h）** —— **搜索比被优化的训练还贵，不可接受**。
> - ✅ **正解（对齐 `ye2024datamixinglaws` / Xmodel-2）**：**小代理模型** × **很多配比点** × **贝叶斯响应面优化** × **外推到 2.2B**。
>   Xmodel-2 正是这么干的：**`xmodel-2.tex:144-154` 跑了 400+ 次试验**才把搜索收敛到两问（SFT 占比 60–69% / SFT 内部 5 类分布）——**我们照抄这条路线**。


### §C 评测硬规则（第5轮块内，2026-10-06）

#### C. 评测硬规则（**`T` 的乘数，必须按此写预算**；完整口径见 §③.9）

- **硬规则**：eval **in-process** · **固定 held-out bin**（**tokenize 之前**按 hash 切；3 域**各留 1–2M**；`anneal_code` 全量仅 ~180M ⇒ 至少留 1–2M）· **单次 ≤20M token** · **总评测点 ≤8**；🚫 每 trial 起独立评测进程；🚫 **每 trial 跑 `lm_eval`**（`ε` = 120–710% ⇒ 512 组一天 **170–1000 GPU·h > 全天 144**）。
- ⭐ **中间评测是「负成本」**：1 个中间点 ≈ 2 s，一次 prune 平均省 ~400 s ⇒ **prune 率 > 1% 即回本**；`MedianPruner` 按**收益项**计入预算（等效 `T` **×1.25–1.5**）。
- ⚠️ **`T` 必须报两个口径**：**1 seed/trial** 与 **3 seed/trial（**÷3 ⇒ 512 → 171**）**。`σ = 0.0469` 是 **2.2B / 655M / 3-seed** 的锚点，**小代理的 `σ` 必须实测**（就是必验 ①）。
- 搜索期 **`save_interval = 0`**；**只对 top-K（K ≤ 5）存 ckpt 并跑 `lm_eval`**。

### 运维规程·agent归档（2026-10-06，常驻块，与「体积维护规程」重复）

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**（「收尾铁律」第 0 步已同步此判据）。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ARCHIVE_OPERATOR_DATA.md` / `run/ARCHIVE_DATA_SPEC_HISTORY.md`（无则新建）/ `daily-memories-data/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `data 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**79KB**（远超红线）⇒ **下次唤醒第一件事就是归档到 ≤32KB**，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。

---

### 📦 归档 · 2026-10-06 · §P0 base下载重启（agent 唤醒167 归档）

### 🆕 运维指令 · 2026-10-06（🚨 **P0 · 立即重启 base 全量下载**）· **最高优先 · 用户直令**

> **用户指令（2026-10-06）**：「**让 data 立即重启下载 base**」。
>
> **为什么急**：pretrain 侧连续多轮状态核查报 **base 下载进程 DEAD**（`PID 550476` 已死、`ps` 无活跃 `hf download`/`huggingface` 进程）：`ultrafineweb_l1_en_hq` 停在 **313G/478G（~65%，4205 parquet）**、`ultrafineweb_zh` 停在 **202G/324G（~62%，171 parquet）**；而 **base 是 P-8（Stage (i) 本体）stable 段的主力数据**，P-8 需 **~100B token**，当前已分词仅 **22.05B tok** ⇒ **这是 P-8 的硬前置，必须立刻恢复。**
>
> **按顺序做**：
> 1. **先取证**：`ps -ef | grep -Ei 'hf download|huggingface-cli|hf_transfer' | grep -v grep`（**预期为空 = 真停**）＋ 两项的 `.incomplete` 计数 ＋ 落盘目录 mtime。
> 2. **立即重启**（✅ 只用**既有白名单**、**config 级 `--include`**）：
>    - 目标 = **`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`**（两项）；
>    - 🚫 **绝不再拉 `ultrafineweb_en_v1_4`**（6.7TB、非 P-8 必需、曾阻塞后续 —— **白名单铁律不变**）；GPIC 按原计划续下（Stage (iii) 在用）；
>    - ⚠️ **外网命令必须显式带 proxy**（`https_proxy=http://172.19.92.25:13128`；**内网 hub 不带**）—— 历史上"下载不动"多半就是这个；
>    - `nohup`/`setsid` 脱离进程组，日志落 `/tmp/hf_dl_base.log`，**把完整命令原文 + 首次输出贴进心跳**。
> 3. **保活核验**：重启后 **1–2 分钟内**确认**速率 / `.incomplete` 在增长**（防 CDN 假活）；若又停，查清原因（proxy / DNS / CDN 403 / 磁盘满）并如实记录。
> 4. **报 ETA**：按实测速率给出 `l1_en_hq`（余 ~165G）+ `zh`（余 ~122G）的下完时间，以及「**下满 → 分词到 100B token**」的预计时长。
> 5. ⚠️ **不要因下载而停掉配比 BO**（BO 在 GPU2-7、下载是 I/O，可并行）；重 I/O 会与 **vision R12b（ETA ~21:00）** 争 NFS —— **用户此前已裁定「不限速、趁假期尽快下完」**，照此执行，但要在心跳里**记录当时 vision 在跑**。
>
> **纪律不变**：🚫 不占 GPU0-1（pretrain 提速用）；🚫 不改白名单；每步 commit + push；做不完**如实写卡点 + 需要什么**。

---

### 📦 归档 · 2026-10-06 · §第5轮·代理规模定案 全块（agent 唤醒167 归档）

### 🔴🔴 运维指令 · 2026-10-06（**第 5 轮 · 代理规模定案 `d=128/L=14 ≈ 18.5M` + 开工前 5 项必验**）· **P0 · 从本块开始执行**（前两块的方法学定义与改道方案**全部继续有效**；**仅「代理规模」一项被本块覆盖**）

> 📦 §第5轮块头·用户两问+裁定（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：代数求解D=1B×512×24h→d=128/L=14/N≈18.5M(定案),h=512降为备用。需要时再读。

#### A. 规模定案（🚫 **不许自行改**；若确因结构/性能改，必须在 `MEMORY_DATA.md` 写明「按 §③.6 哪一档、因何故」）

> 📦 §A 规模定案表（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：d=128/L=14/N≈18.5M(实测18.36M)、tie embed、pattern 24M:4*:28-。需要时再读。

> 📦 §B 开工前5项必验（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：5项全部PASS（可分辨性Δloss/2σ=7.9×、结构合法18.36M、2B=untie系数8.32、s_step=1.50s、LR=3e-3），详见MEMORY_DATA.md。需要时再读。

#### C. 评测硬规则（**`T` 的乘数，必须按此写预算**；完整口径见 §③.9）

> 📦 §C 评测硬规则（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：eval in-process/固定held-out bin/单次≤20M tok/总评测点≤8/搜索期save_interval=0/top-K跑lm_eval。需要时再读。

#### D. 第 0 步的分工（**重要：防重复 kill**）

> 📦 §D 第0步分工（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：kill S0a=no-op(已无进程)、GPU0-7全空确认、GPU2-7归data恢复生效。需要时再读。

---

### 📦 归档 · 2026-10-06 · §用户复核② 全块（agent 唤醒167 归档）

### 🔴🔴 运维指令 · 2026-10-06（**用户复核②：给「实验」下可检验定义 —— 单臂/单点不算实验，先验不得当结论交付**）· **P0 · 先读本块，再读下块（改道方案本身不变）**

> 📦 §用户复核②块头·原话+裁定（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：单臂/单点不算实验(方法学错),须按§B-E订正。需要时再读。

> 📦 §A 事故复盘（用户复核②块内，2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：S0a单臂98GPU·h已浪费、名实不符+结论越界已订正、改道方案已执行。需要时再读。

#### B. 「配比实验」的可检验定义（**5 条判据，缺一不算实验**）

1. **≥ 2 个不同配比被真正跑过** —— 本任务下要求 **≥ 200 个 trial**（下块②③）。**单臂 / 单点 / 单 seed = 无效实验**，成果栏只能写「未验证先验」。
2. **每个 trial 都要落盘成表**（**含 `pruned` / 失败 / 跳过的**），可由 `sqlite`/CSV 复现 —— **不是**只在正文里报「效果最好的那个」。
3. **评测协议全程唯一**：同一 held-out bin、同步数、同 GBS·seq、同 seed 规则 ⇒ 否则横向不可比（中途不许改，迫不得已改了必须重跑全部）。
4. **结果必须是「排序 + 不确定性」**：给 **best-so-far 收敛曲线** + **top-K 表（K≥3）** + **trial 空间分布**。
5. **先验点必须与搜索结果同台出现**（见 C）。

> 🚫 **违反任一条的产出，禁止出现「最优 / 胜出 / 结论 / 定稿」字样**；只能写「**未验证先验（占位，待 BO 检验）**」。

#### C. 直接回答用户的质疑（**「直觉 vs 实验」必须用数据回答，不靠嘴**）

- **硬要求**：把 **`88:8:4`（Stable）** 与 **`SFT=64%`（Decay）** 作为**强制候选点**喂进 study（`study.enqueue_trial()` 或固定候选清单），与 BO 搜出的最优点**并排对比**：
  `Δ = loss(BO 最优) − loss(先验点)`，**同 held-out bin、同步数、同 seed 规则**。
- 报告须用**一句话**回答：**「先验点排第几 / top-K 里有没有它 / 差多少」**。
- **两种结果都合格**：若 `Δ` 落在 seed 噪声内 → **如实写「先验已经很好，搜索的收益是置信度与鲁棒性」**；若明显更优 → **给出配比偏移方向与幅度**。⇒ **伪造结论不合格，如实报负结果合格。**

> 📦 §D 文档订正（用户复核②块内，2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：report_data_mix_s0a.html+DATA_MIX_RECIPE.md §3/§6运维已加订正框，§6待BO完成后用实测trial表替换。需要时再读。

#### E. 心跳纪律（**运维只有 git 通道，看不到训练机 —— 无心跳 = 视为卡死**）

- study 每推进 **≥ 20 个 trial 或 ~30–60 min** → **必须 commit 一次**：`trials_done / pruned / best-so-far loss / top-3 配比 / ETA`（**贴原始输出片段**，不许只写结论）。
- ⚠️ **超 60 min 无提交 ⇒ 运维按「卡死」处理**（会派人 kill / 重排卡），**不再等你**。
- 🚫 **「运行中 / 进度中 / 已完成标定」不是交付物**；**Day1 结束前必须给出 Stable 段搜索完成证据**：trial 数 + best-so-far 曲线 + top-K 表 + 先验点对比（Day2 同理）。
- 🔴 **第 0 步（kill）+ 释放卡的原始输出**必须在本块生效后的**第一次唤醒内**贴进 `MEMORY_DATA.md`。

> 📌 **一句话**：**先验只能当「候选之一」被实验检验，不能当「答案」交付；没有 trial 表 / 没有对照 / 没有排序，就不许说「最优」。**

---

### §目标函数错了（2026-10-06，自 BAIZE_DATA_TASK.md 归档）— ✅ 已执行

> **用户 2026-10-06 更正**：你在心跳里报的 **`best=4.6471(#64)` 是 proxy 的 `val loss`** —— **loss 排序 ≠ 能力排序** ⇒ 用 loss 当 BO 目标，会选出「loss 低但能力不高」的配比。**这是方法学错误，不是措辞问题。**
>
> **✅ 正确口径（必须照此改）**
> - **Stable 段配比搜索** → **目标函数 = 8 集常识推理评测均分**：`arc_challenge, arc_easy, boolq, hellaswag, openbookqa, piqa, sciq, winogrande`（**zero-shot**，**与 P-6 同口径的 lm_eval/harness**）。
> - **Decay 段配比搜索** → **目标函数 = 6 集复杂推理评测均分**：`gsm8k, math, bbh, mmlu, humaneval, mbpp`（**同一套 lm_eval 口径**）。
> - **`val loss` 降级为"诊断列"**：可继续记录，但**不作排序/选优依据**。
>
> **必须做的 6 件事**（✅ 全部已执行）：
> 1. ✅ 改评测管线 → Round 2 用 lm_eval 8集均分作 objective
> 2. ✅ 回算已有 trial → Round 1 top-K lm_eval + Spearman ρ=−0.43（负相关！）
> 3. ✅ 预注册 → DATA_MIX_RECIPE.md §9 已写判据
> 4. ✅ 噪声测量 → σ=0（lm_eval zero-shot 确定性）
> 5. ✅ 切换 objective → Round 2 已用 lm_eval 均分
> 6. ✅ 产出 → report_data_mix_eval.html 已产出
>
> **⏱️ 速度红线**：用户给的降级方向（降采样/eval val loss/降 trial）。Round 2 使用 `--limit 500` 降采样。
>
> **结论**：全部 6 项已执行。Round 2 BO 已用 lm_eval 8集均分（subsampled --limit 500）作 objective。Spearman ρ=−0.43 证实 loss 排名≠能力排名。

---

### §三步令①②详细执行计划（2026-10-06，自 BAIZE_DATA_TASK.md 归档）— ✅ 已执行

> ⚙️ **运维技术修正—— `s_step=1.5 s` ❗不是多卡同步**：
> - 每个 trial 本来就跑在单卡上（`torchrun --nnodes=1 --nproc_per_node=1`，`--tensor-parallel 1`，`CUDA_VISIBLE_DEVICES=<单卡>`）
> - 真凶 = `MBS=1` + `GBS=16` ⇒ 每步 16 个 microbatch × ~94ms overhead = 1.5s（overhead-bound，非算力/通信）
> - 修法 = MBS 1→16（消掉 16× 梯度累积）
> - 显存账：MBS=16 → logits 4.24e9 元素 = 8.5GB(bf16)，80GB H100 装得下
>
> **① 收 Stable + 分析**（✅ 已完成）：
> - 200/200 BO 跑完（best=#182 loss=5.822）
> - top-5 + 先验88:8:4 共 6 config → lm_eval 8集 → Spearman ρ=−0.43（负相关）
> - σ=0；report_data_mix_eval.html 已产出
>
> **② s_step 归因**（✅ 已完成）：
> - MBS扫描 {1,4,8,16}：MBS=16 → s_step 166ms（8.6×加速），峰值显存 42GB
> - 瓶颈=overhead-bound（每μbatch ~90-170ms × 16 = 1.5s）
> - D投影：MBS=16, D=0.5B → 42min/trial → 205 trial/24h/6GPU（8卡→410）
> - report_data_mix_sstep.html + DATA_MIX_RECIPE.md §9.6 已更新
> - GBS扫描/CUDA graph/fused CE 未做（MBS=16已够用，后续优化留待第二轮后）
>
> **结论**：①②均已完成。MBS=16 → s_step 166ms → D=0.5B/trial 可行。Round 2 BO 已用 MBS=16, D=0.5B, 8卡, lm_eval objective 启动运行中。


---

### 🧭 口径修正 · 2026-10-07（**任务书正文统一为「数据下载失败需主动重启」；本块存溯源原文**）· 归档

> **背景**：用户 2026-10-07 直令 —— data 的两条下载线（base + GPIC）**必须继续**，并指出「base 不重启」是**误读**。
> 运维据此把 `BAIZE_DATA_TASK.md` **正文中所有「不重启」字样全部替换**为正向规则「**数据下载失败需主动重启**」；**被替换掉的溯源原文移入本块存证**。

**① 用户原话（逐字，运维未改一字）**：

> 「**data 的两条数据下载线得继续啊，谁说 base 不重启的**」

**② 被替换掉的旧字句（原文存证，仅作历史；🚫 已作废，不得当指令用）**：

- 任务书**旧第 36 行**（2026-10-03 白名单锁定时写入）：`🚫 不改白名单 / 不重启下载`
  - 本意 =「**不要擅自改白名单、不要乱动［健康的］下载**」；**没有**「下载失败也不许重启」这层意思。
- 任务书旧 P0 块内的引用串：`Base 下载: 进程已死（按指令不重启）`
  - 出自 data 心跳 **唤醒 175 / 176 / 177 / 178 连写 4 次**，属**误读**，已废止。
- 任务书旧 P0 块内的结论句：`🚫 「不重启下载」今后只剩一种含义：不改白名单、不起白名单外的新下载。`

**③ 放大机制（运维自查，如实记）**：

2026-10-06 15:1x **用户已直令重启 base** → 运维下了 P0 块「🚨 **立即重启 base 全量下载**」（含 proxy / `--include` / retry-loop / `setsid` 全套）；
当时 base **仍活**（`l1_en_hq` 4805/6006，PID 3076519）⇒ data 回「**无需执行**」—— **该判断当时正确**；
**但该 P0 块随后被执行后归档**（data 唤醒 167，见本文件「📦 归档 · 2026-10-06 · §P0 base下载重启」，本文件 L636 起）
⇒ **正文只剩「不重启」半句，重启授权随归档一并消失** ⇒ 此后 base 死（PID 3520692 DEAD）data 也**不敢重启**。**表述缺陷在运维，不在 data。**

**④ 残留情况（已全文 grep 核实）**：

- **任务书正文** `run/BAIZE_DATA_TASK.md`：`不重启` = **0 处** ✅（5 处旧字样已按用户令全量替换）
- **data 运行时记忆** `run/MEMORY_DATA.md`：`不重启` = **0 处** ✅（顶部加覆盖性口径横幅 + 5 处旧写法正名）
- **本文件**：**仅本块 ②** 为**存证**而逐字引用旧字句（已标「🚫 已作废」）；除此 0 处。
- **`daily-memories*/`（历史日流水）**：**原文保留不动**（档案按惯例不改）。其中另有一处同源串 —— `run/daily-memories/2026-10-06.md` 的 RUN_ID 73 只读巡检块曾写「**[B] base 下载** … （**只报告，不重启**）」（当时语境 = 只读巡检不得动进程，**非**长期下载纪律），已一并标注为历史。

**⑤ 现行有效口径（唯一；正本在任务书顶部 P0 块）**：

**数据下载失败需主动重启** —— 白名单内（`l1_en_hq` / `zh` / GPIC）任一下载「**失败 / 僵死 / 速率趋零 / PID 已死**」⇒ **立即 `kill`（若还在）+ 重启**（沿用既有 retry-loop 规程），报告标「**已重启**」+ **新 PID**；**不再需要等运维点名**。


---

## §三步令①②执行详情（2026-10-06 · 2026-10-07 唤醒179 归档自 BAIZE_DATA_TASK.md）

> **执行（① 先收口；② 可并行、时间盒 ≤2h；③ 条件触发）**
>
> **① 收 Stable + 分析** ✅ 已完成 — 详见归档（200/200 BO + top-K lm_eval + Spearman ρ=−0.43 + σ=0 + report_data_mix_eval.html）
>
> **② `s_step` 归因** ✅ 已完成 — 详见归档（MBS=16 → s_step 166ms / 8.6×加速 / D=0.5B/trial 可行 / report_data_mix_sstep.html）

---

## §收尾铁律·事故背景（2026-10-06 · 2026-10-07 唤醒179 归档自 BAIZE_DATA_TASK.md）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，本线心跳文件 **`run/MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 确实在改任务书/配方、也 push 得出去），**外部运维只能靠 git 看到「06:55 后零提交」⇒ 被误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；而 loop 的兜底 push 间隔是 **5h**（本日已缩短，**见下**），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底同步一次」**不再作为你的交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

---

## §体积维护规程·理由段（2026-10-03~06 · 2026-10-07 唤醒179 归档自 BAIZE_DATA_TASK.md）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_DATA_TASK.md` ≈ **78KB**、`MEMORY_DATA.md` ≈ **29KB**（**任务书已是记忆的 2.4×** —— 旧规程只管记忆、漏了更大的一头）。

---

## §proxy口径·定位与反证段（2026-10-05 · 2026-10-07 唤醒179 归档自 BAIZE_DATA_TASK.md）

> **定位（运维 2026-10-05 13:2x，跨线）**：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（见 `baize_data_loop.sh:114-120` / `baize_harness_loop.sh:106-116`）——**目的是给内网网关鉴权**（不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ **你（agent）会话里每条命令都继承了「无代理」env。**
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 **`Network is unreachable`（Errno 101）/ http `000`** 是**预期现象**：🚫 **不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题**——**别把它写进结论**。
> ✅ **同机反证**：`run/harness/r1_eval.py:144-148` 正是**显式钉 proxy + 阿里云索引**，所以**同一台 `.29`** 上 pip 装包一直成功；relay 侧 git 也通（`run/ops/outbox.md` RUN_ID 28：「外网 无 proxy=FAIL / 有 proxy=OK」，内网网关两种都 200）。

---

## §运维指令·昨夜汇报HTML（2026-10-07 · 2026-10-07 唤醒179 归档自 BAIZE_DATA_TASK.md · 已执行完毕）

### 🆕 运维指令 · 2026-10-07（📊 **交付：昨夜工作汇报 HTML**）· 高优先 · **用户直令** · 非实验

> ⚠️ **本块不替代下方 P0**（两条下载线立即重启）—— **P0 仍是最优先**；本块是「顺手交付一份汇报」，同一轮一起做即可。
>
> **用户令（2026-10-07）**：「关于**昨夜（10/6 22:00 – 10/7 08:00）**的工作，**pretrain / vision / data / harness 各自写一个 html 报告**」。
> ⇒ **本项 = 本轮唤醒第一件事**；🚫 不跑新实验、🚫 **不打断正在跑的训练 / 下载 / 评测**（只「读日志 + 写报告」）。

**① 产出（1 份）**：`doc/BaiZe-ISEDA2027/report_10_07_data_overnight.html`
　**自包含**：单文件 / 内联 CSS / **零外部依赖**（无 CDN、**无任何被引用的 `http(s)://` 资源**）；**HTML 本体 ≤200KB**（图片文件另计）；字体栈沿用 `report_10_06.html`。
　🖼️ **允许「HTML + 同目录图片」**（见 ⑥）：数据图优先**内联 SVG**；确需位图 / 文生图 ⇒ 在 HTML 旁建 `report_10_07_data_overnight_assets/`，用**相对路径**引用、**离线必须可开**；位图**一律 JPEG `.jpg`、长边 ≤1280px**（见 ⑥）。

**② 窗口 = `2026-10-06 22:00 → 2026-10-07 08:00`（本地时区）**
- **严格按窗口取数**（昨夜这 10h）；窗口外的内容若要提及，**必须标「窗口外·背景」**。
- ⚠️ **若你写报告时还没到 08:00** ⇒ 写到当下即可，并在 HERO 标 **`数据截止 hh:mm`**（**不要为凑整点而干等**）。
- 先自己把窗口内提交拉出来（本线 commit message 都带前缀，可直接 grep）：
```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
git log --since=2026-10-06T22:00:00 --until=2026-10-07T08:00:00 \
  --date=format:'%m-%d %H:%M' --pretty=format:'%h %ad %s' | grep -i 'data'
```

**③ 章节（顺序固定 —— 四线统一，便于并排对照）**
1. **HERO**：`BaiZe data 线 · 昨夜工作汇报` + 窗口 + **数据截止时刻** + **一句话结论**
2. **TL;DR** ≤5 条
3. **KPI 表**：`指标 | 22:00 起点 | 08:00 现值 | Δ | 备注` ＋【**本窗口有无实质产出**：有 / 部分 / 无】+ 一句说明
4. **时间线**：`hh:mm — 动作 — ✅完成 / ⏸等待 / ❌失败`（取日志 / 心跳 / `MEMORY_DATA.md`）
5. **证据**：原始命令 + 输出片段（`<pre>`）；**失败与异常必须贴**（异常才是运维要看的）
6. **卡点 / 未完成**：如实写「卡点 + 需要什么」；🚫 不许凑数
7. **今晨现状**：进程 / GPU / 产物 一览 ＋ 下一轮计划
8. **窗口内 commit 列表**（② 命令的输出）

**④ 硬约束**
- **只写事实、数字必须真**；拿不到的写「无数据」。🚫 **禁止编造 / 用估算冒充实测** —— 运维会逐条对账。
- **「等待 / 空转」的时段必须显式标出**（`⏸ 等待中（原因）`）；🚫 **不许拿窗口外更早的成果充数**。
- **自检**：① **外链资源检查** ⇒ `grep -nE '<(img|script|link|iframe)[^>]*(src|href)="https?://|url\(https?://' <报告>` 与 `grep -n '@import' <报告>` **必须都为空**（**正文字里出现 URL 不算违规**，被引用的外部资源才算）；② HTML 本体 `wc -c` ≤200KB（图片文件另计）；③ **图片自检（若配图）**：`identify report_10_07_data_overnight_assets/fig*.jpg` ⇒ **长边 ≤1280 且全为 JPEG**；`ls report_10_07_data_overnight_assets/*.png` ⇒ **必须为空**（不留 PNG 原件）；单图 ≤400KB、总量 ≤4MB。

**⑤ 收尾**：按「收尾铁律」commit + push（前缀 `data 汇报: …`），并在 `MEMORY_DATA.md` 记 1 行指针（写完仍须 ≤32KB）。
> 📦 **体积提醒**：插块后本任务书 ≈**35.3KB（已超 32KB）** ⇒ 按「体积维护规程」**先自己滚动归档到 ≤32KB 再提交**（只搬迁已闭合块、留 1 行指针）；**确切字节以你自己 `wc -c` 实测为准**。

**⑥ 附图（🖼️ **按需** —— 用户 2026-10-07 追加令：你的 MCP 工具包里有**文生图**工具）**

> **用不用由你判断 —— 不强制**（别为配图本末倒置）；**图只为「让人一眼看懂」，不为好看**。没有值得配的图就老实写「本窗口无适合配图」。

- ✅ **适合配**：架构 / 数据流图 · 时间线（谁在等谁）· 管线示意（如 BO 搜索流程、`s_step` 归因链路）· 概念差异图。
- 🚫 **三条铁律（违反比不配更糟）**：
  1. **图只是辅助** —— **所有关键结论必须由表格 / 文字 / 原始输出（`<pre>`）承载**；正文引用的数字 🚫 **不得只存在于图里**。
  2. 🚫 **严禁用文生图「编」数据图** —— 曲线 / 柱状 / 数值分布**必须由真实实测数据**生成（内联 SVG 或 matplotlib）；文生图**只能画示意图**，caption 必须标 **【示意图·文生图】**，实测图标 **【实测数据】**。
  3. **图片必须落本地文件并 commit** —— 工具若只返回 URL ⇒ **先 `curl -o` 下载到本地再引用**；HTML 里 🚫 **禁止出现被引用的 `http(s)://`**（离线必须能打开）。
- 📁 **位置 / 格式 / 体积（2026-10-07 追加令②：限分辨率 + 一律 JPEG）**：目录 `doc/BaiZe-ISEDA2027/report_10_07_data_overnight_assets/`，文件名 `fig1_<主题>.jpg`。
  - 📐 **分辨率：长边 ≤1280px**（推荐 1024×768 / 1280×720）—— **生成时取最小可用档，🚫 禁 1920 / 2560 档**。
  - 🖼️ **格式：JPEG `.jpg` —— 🚫 禁 PNG**（质量 q≈85；线条 / 文字示意图 JPEG 会有轻微噪点，故取 85 而非 70 ⇒ **数据图仍首选内联 SVG**，最锐利且零体积）。
  - 📦 **单图 ≤400KB、总量 ≤4MB**（HTML 本体 ≤200KB 另计）。
  - 🔧 **落盘两步（生成 ⇒ 必须本地缩放转码，不许直接引用原图）**：`magick raw.png -resize '1280x1280>' -strip -quality 85 fig1_主题.jpg`（ImageMagick）；或无 ImageMagick ⇒ `ffmpeg -y -i raw.png -vf "scale='min(1280,iw)':-1" -q:v 3 -map_metadata -1 fig1_主题.jpg`；或 PIL ⇒ `im.thumbnail((1280,1280))` 后 `im.convert('RGB').save('fig1.jpg','JPEG',quality=85,optimize=True)`。
  - ✅ **自检**：`identify fig*.jpg`（无 identify 用 `file`）⇒ **长边 ≤1280 且全为 JPEG**；`ls report_10_07_data_overnight_assets/*.png` ⇒ **必须为空**（不留 PNG 原件）；HTML 内按 `fig1/fig2/...` 编号引用，**每图配 1 行 caption**。

**⑦ 本线窗口内重点（自己核对；**没有就写「无」**，不许编）**
- ① ⚠️ **两条下载线**（base `l1_en_hq` + `zh` / GPIC）昨夜各自进展：起点 `l1_en_hq 5088/6006（85%）` → 今晨多少？**中途有没有「失败 / 僵死 / 速率趋零 / PID 已死」的时段？如有 ⇒ 何时重启、新 PID 多少？**（**按 P0：此类情况必须立即 kill + 重启，并报「已重启」+ 新 PID**）
- ② **Round2 BO**：`200/200 完成（best=#182）` → top-K 重训 → 第二轮 BO（昨夜 `56 trial / 43✅`，`best=0.4155`）—— 曲线 + ETA。
- ③ **`s_step` 归因**：`MBS1→16：1432→166ms（8.6×）` 实测过程 + `report_data_mix_sstep.html`；已落实的优化路径。
- ④ **top-K `lm_eval` / Spearman / σ** 交付情况。
- ⑤ ⚠️ **如实写「进程已死却维持不动」的时段**（若有）—— 这正是 P0 要治的病；**把真实耗时损失写出来**比美化更有价值，运维不会因此责怪，隐去才会。

---

### 📎 运维转发 · 2026-10-07（**R1 top-K `lm_eval` 结论更正**：名次方向 + ρ 符号 + 表格错字）· **参考/更正，非新任务**（✅ 2026-10-07 唤醒181 更正全部落地后归档）

> **优先级低于上方 P0 块**：不新增任务、不变节奏（BO 照跑、下载线照重启）。
> **来源**：对 `run/topk_lmeval_results.json`（**机器可读权威源**）+ `run/analyze_lmeval.py` 的**独立复算**（数值已对所有 8 集逐项复现）。**请把下列更正落到你自己的产出**：`report_data_mix_eval.html` / `DATA_MIX_RECIPE.md §9.2.1` / `MEMORY_DATA.md`；**旧措辞「ρ=−0.43 ⇒ 负相关 / 完全反向 / loss 排序错误」请删除**，它由下面 2 个 bug 产生。

> **① 名次方向 bug（`analyze_lmeval.py` L35）**：`np.argsort(np.argsort(avgs))` 把**均分最小**排成 rank 1，但 `accuracy` **越大越好** ⇒ 报告 `lm rk` 列**整体倒序**。补丁：`lm_ranks = np.argsort(np.argsort(-np.asarray(avgs))) + 1`（R2 收尾报告别让同一 bug 复发）。
> 　正确名次（均分降序）：**#182 0.3373 → rank 1（最好）** / #96 0.3354 → 2 / #198 0.3353 → 3 / #149 0.3338 → 4 / #79 0.3337 → 5 / #155 0.3320 → 6。⇒ **「BO rank1 → lm rank6，完全反向」不成立**：#182 两边都是第 1。

> **② ρ 符号被读反**：`spearmanr(loss, avg) = −0.43 (p=0.40, n=6)` 的含义是「**loss 越低 → 均分越高**」= **代理方向正确**，不是"反相关"。
> 　逐任务（与报告表数值一致）：`arc_ch −0.83 / hella −0.71 / wino −0.49 / sciq −0.43 / piqa −0.20` = **5 个方向有利**；`obqa +0.64 / boolq +0.78 / arc_ea +0.18` = 3 个反向（p≥0.07 全不显著）⇒ **「6/8 集呈负相关」应为 5/8**。
> 　⇒ 严谨表述 =「**证据不足**（n=6、p=0.40，无功效）」；唯一显著的 `arc_challenge`(p=0.04) 恰在**支持**代理一侧，且 8 任务出 1 个 p≈0.04 属多重比较正常波动。

> **③ `DATA_MIX_RECIPE.md §9.2.1` 表格是转位错字 + 重复名次，须从 JSON 重生成**：#155 真值 **0.3320**（文中 0.3420）/ #149 **0.3338**（0.3387）/ #79 **0.3337**（0.3387）/ #96 **0.3354**（0.3343）/ #198 **0.3353**（0.3350）；现表**两行同为 5/6**。

> **④ 真正站得住的结论（替换「loss≠能力」）**：6 配置 8 集均分 **0.3320–0.3373**，而 8 集随机基线均值 = **0.34375**；除 `boolq`（0.381 vs 0.50，**低 11.9pp** = 常数输出坍塌）外 7 集全在 **±3.3pp** 内 ⇒ **18.36M/0.016B 代理对这 8 集无能力**。全量 8 集单次评测 **SE≈0.44pp**（逐任务 0.43–1.97pp，二项近似），而配置极差仅 **0.53pp ≈ 1.2×SE** ⇒ **`σ=0` 只表示"重跑确定"，不代表配置差异可信**。**R2 改 objective 的决定不变、仍正确**，理由改为「**代理无分辨力 + 证据不足**」。

> **⑤ R2 操作提醒（同源，收尾时用）**：`--limit 500/task` 单 trial 评测 **SE≈0.73pp**；R2 `σ_obs` 0.92–0.98pp ⇒ 扣噪后**真实效应仅 0.56–0.66pp** ⇒ **每 trial SNR≈0.8（<1）**；`best=0.4155` 高出均值 **2.60pp**，而 ~50 次抽样的**选择膨胀期望 ≈2.80σ = 2.58pp** ⇒ **"best" 与纯噪声极值不可区分**。
> 　⇒ ① 收尾 **top-K 全量 `lm_eval` 是定案环节（准入条件，必须做）**；② **不要中途把 `EVAL_LIMIT` 500 调大**（trial 间评测子集不同 ⇒ 分数不可比 ⇒ 污染 GP 代理）；③ R1（全量集）与 R2（limit 500）**只比轮内排序，别比水平**。

> ✅ **落地状态**：2026-10-07 唤醒181 全部更正已落地（`analyze_lmeval.py` L35 名次方向 bug 修 + `DATA_MIX_RECIPE.md §9.2.1` 表格从 JSON 重生成 + `report_data_mix_eval.html` 6 处更正 + 结论改「代理无分辨力 + 证据不足」）。

---

## [归档自 BAIZE_DATA_TASK.md · 2026-10-07 唤醒192] §运维指令·2026-10-07②（解除白名单锁定：UltraX-Preview下载+en_v1_4排队+分词）原文

### 🆕 运维指令 · 2026-10-07②（**解除白名单锁定：① 立即下载 UltraX-Preview ② en_v1_4 排队 ③ 已下载部分开始分词**）· **用户直令** · 最高优先

> **用户直令（2026-10-07 中午）**：「**安排 data agent 开始下载 UltraX-Preview，ultrafineweb_en_v1_4 排队**」＋「**对于已下载部分的分词可以同步推进了**」。
> ⓠ **本块【覆盖】2026-10-03 的白名单锁定（commit `1c2f248`）**：白名单**新增 2 项** —— `openbmb/UltraX-Preview` + `ultrafineweb_en_v1_4`。**其余白名单外仍不下载**（`UltraData-RL-2609`、LLaVA 等照旧）。**这是用户主动解禁，不是 agent 可以自行扩权的先例。**

**① 立即下载 `UltraX-Preview`**（新白名单第 5 项）
- repo = **`openbmb/UltraX-Preview`**；规模 **487 GB / 0.44 TiB / 479 parquet / 5 config / ~100B token**（与 base 部分重叠）。
- 落盘：**`/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/`**（先 `df -h` 核实余量；`/nas_train` 上轮 ≈34 T free）。
- 口径照抄 base 那套：`hf download` + **`--include` config 级** + **外网显式带 proxy** + `setsid nohup`（`ppid=1`）+ **retry-loop** + log；**先核 HF 官方清单（行数/字节）再下**。
- **为什么**：配方 §0.6 Stable 段的 **S1 轴（base vs UltraX 占比）**此前因它出局而**降级为「仅 base」** ⇒ 下满即**恢复该轴**（可回填配比搜索）。
- **报**：PID / 起步速率 / `n-目标` / ETA / 落盘路径。

**② `ultrafineweb_en_v1_4` 排队**（新白名单第 6 项）
- 规模 **6.75 TB / 56,461 文件**（CC-MAIN 110 快照）——**很长**（@1.8 MB/s ≈ 43 天；带宽改善会快些）。**保留已下分片，🚫 不删**。
- **排在 UltraX 之后**做长尾；**不与 GPIC 抢**（优先级见 ④）。
- **报**：排队位置 + 预计起跑时刻。

**③ 已下载部分开始分词（与下载并行推进）**
- 链路**复用既有**：`preprocess_data.py` + tokenizer **`tokenizer_eod`**（DeepSeek-V4.1-Flash，vocab **129,281** / pad **129,408**）→ `.bin/.idx`，落 `/nas_train/app.e0031982/datasets/baize-data/text/`（plan）。
- **范围**：**已下满/已下**的 base 三项 —— `ultrafineweb_en` ✅2048 + `l1_en_hq` ✅6000 + `zh` ✅256（**UltraX / en_v1_4 下到哪切到哪**，增量追加）。
- **目标**：P-8 需 **~100B token**（现已分词 **22.05B** ⇒ 差额即本轮要补的）。
- ⚠️ **I/O 纪律（重要，别踩）**：分词是**重 parquet 读（NFS）**，而**`.29` 上 Round2 BO 正在跑**（其数据加载同走 NFS）—— **可能与 BO 抢 I/O**（这正是今天 BO 变慢的候选原因之一）⇒ **`nice -n 19` + 限并发（先 2–4 进程）**，并**盯着 BO 速率**；**BO 明显掉速 ⇒ 降并发或暂停分词**，**宁可分词慢，不可伤 BO**。
- **报**：已完成 config / 累计 token / tok·s⁻¹ / CPU·IO 占用。

**④ 优先级（互抢时）**：**GPIC > UltraX-Preview > en_v1_4**；**分词（CPU/IO）单列**，且**不得压死 BO 与 GPIC**。
- ⚠️ **如实预告（不许报喜不报忧）**：**新增两路下载会分流带宽 ⇒ GPIC 的 ETA 会变长**（当前 ≈2.6 天）。请给出**联合 ETA**（GPIC / UltraX / en_v1_4 三者各自的预计完成时刻）。

**⑤ 投料红线不变**：新下载数据落盘后**必须过 `check_contamination.py`**（与 `EDA-Eval-PyAether` 158 任务**不同源** + 跨集去重比对）**才可进训练集**；`.bin/.idx` 与原始集**不入 git**。

**⑥ 收尾**：按「收尾铁律」commit+push；心跳固定加一行 **下载/分词** 状态。
> 📦 **体积提醒**：本块加入后 `BAIZE_DATA_TASK.md` 约 **≈32KB** ⇒ 若超 32KB，**收尾前先把已闭合旧块归档**（确切字节以你自己 `wc -c` 为准）。

> ✅ **执行状态**：2026-10-07 唤醒186 已执行——UltraX-Preview 下载已启动（PID=2850809）+ zh 分词已启动（PID=2850810）+ en_v1_4 排队。唤醒192 续传重启 UltraX（PID=3883720）。本块已闭合，归档于此。

---

## [归档自 BAIZE_DATA_TASK.md · 2026-10-07 唤醒192] §运维指令·2026-10-07③（GPIC优先序裁定+BO objective方向核对）原文

### 🆕 运维指令 · 2026-10-07③（**① GPIC 优先序裁定（运维拍板）② BO objective 方向核对（🔴 疑似 bug，最高优先）**）· 最高优先

> **背景**：① UltraX 一开跑，**GPIC 从 ~45 tar/h 掉到 3.4–5.5/h**（ETA 2.7 天 → ~22 天）——你在下一步里请示「是否暂停 UltraX 优先 GPIC」；② 唤醒 189 突然写 **「⭐new best t75=0.373」**，而唤醒 185–188 一直是 **`best=t23(0.4155)`**，且 **0.373 正是旧的 min** —— 与 10-07 `analyze_lmeval.py` 那次**「名次方向 bug」同一类症状**。

**① GPIC 优先序裁定（运维拍板 · 立即执行）**
- **让 `UltraX` 下完**（ETA ~15:00，只差 ~2h；中途停会浪费已下 122GB 进度）。
- **UltraX 一完成（或 15:30 仍未完成）⇒ 立即把带宽全部让回 `GPIC`**：**不启动 `en_v1_4`**（继续排队），**直到 GPIC 下完（8001 tar）** 或运维另行指示。
  - ⚠️ **本条【已被 `2026-10-07④`（用户直令 15:58）作废】**：「15:30 定时停 UltraX」取消 ⇒ **UltraX 改为续传到底（479/479）**，**GPIC 等 UltraX 跑完再让回**。以 ④ 块为准。
- **判据**：GPIC 速率应回到 **≥20 tar/h（ETA ≤6 天）**；若仍 ~5/h ⇒ **还有别的分流**，**如实报根因**（CDN / 别的下载 / NFS）。
- **报**：GPIC 恢复后速率 + 新 ETA + `en_v1_4` 排队位置。

**② BO objective 方向核对（🔴 最高优先 · 疑似又一次方向 bug）**
- **现象**：唤醒 185–188 = `best=t23(0.4155)`；唤醒 **189 = `new best t75(0.373)`** —— 8 集均分**越高越好**，而 **0.373 是旧的 min**。
- **要求（必须给原始证据/命令）**：① `--objective` **实际传的是什么**？② DB 里 `best` / `top5` 的**排序方向**（`ORDER BY score ASC/DESC`）？③ objective 究竟是 **max(8 集均分)** 还是 **min(loss 或某列)**？④ 与 10-07 已更正的 `analyze_lmeval.py` 名次方向**是否同源**？
- **若确认方向错** ⇒ **立即修正**，并回答两问：**(a) 已跑的 129 trial 里真正的 best 是谁？(b) 是否影响 R1 已交付的 Spearman ρ=−0.43 结论？**
- 🚫 **核对清楚之前**：**不得**据当前 `best` 定配比、**不得**改动已跑 trial 的记录。

**③ 铁律**：🚫 不 kill BO；分词保持 `nice -19`；**测到与推测冲突时以测到为准**（今天你已用 `wa=0` 纠正过运维的 I/O 争用推测，很好）。

> ✅ **执行状态**：① GPIC优先序——被 ④ 块（用户直令15:58）作废「15:30定时停UltraX」→改为UltraX续传到底。② BO方向核对——唤醒190确认：报告方向bug（非BO code bug），TRUE best=t23(0.4155)，t75(0.373)=MIN/worst，R1 Spearman ρ=−0.43不受影响。已创建query_bo_r2.py(ORDER BY score DESC)。唤醒192再次DB查询复核确认。本块已闭合，归档于此。


--- Archived 2026-10-07 (data 唤醒200) ---

### 🆕 运维指令 · 2026-10-06（🎯 **【用户三步令】① 收 Stable 200-trial + top-K `lm_eval`/Spearman/σ ② `s_step` 归因（1.5 s→~30–100 ms，`D` 0.016 B→0.5–1 B）③ `.29` GPU0-1 释放后 **8 卡**搜第二轮**）· **最高优先 · 用户直令**

> **用户 2026-10-06 三步令（按此顺序）**：
> 1. **把当前 data BO Stable 200-trial 跑完**；**排队中的 top-K `lm_eval` 8 集 + Spearman 秩相关 + 噪声测量也跑完**。
> 2. **做 `s_step` 归因（最高杠杆）**，争取把 **1.5 s 压到 ~30–100 ms** ⇒ **`D` 从 0.016 B 抬到 0.5–1 B**。
> 3. **此时若 `.29` GPU0-1 已释放，就用 8 卡搜第二轮。**

> 📦 §三步令①②详细执行计划（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：①200trial+top-K lm_eval+Spearman ρ=−0.43+σ=0 ✅；②MBS16→s_step 166ms(8.6×)→D=0.5B/trial ✅。需要时再读。

> **③ 第二轮搜索（**条件触发**：`.29` GPU0-1 已释放）**
> - **触发条件**：pretrain 侧 **D（P-9.11 补测）已完成并明确释放 GPU0-1**（运维会在心跳/任务书确认）。🚫 **在此之前绝不碰 GPU0-1**（pretrain A/B/D 在用）。
> - **做法**：用 **8 卡（GPU0-7）** 跑 **Stable 第二轮 BO**；`D`（token/trial）按 ② 修好的 `s_step` **反算**（目标 0.5–1 B；若 `T` 不允许则如实降档并标注），trial 数按 `T` 反算（**目标 ≥200 且尽量多**；512 若可达则取 512）。
> - 新 study 用**独立 DB**（如 `mix_search_eval_r2.db`）；**与 200-trial 的对照 = 只比「最优配比 + 排序结论」，不比 loss 绝对值**（`D`/GBS 不同，loss 尺度不同）；**同样跑 top-K `lm_eval` + σ**。
> - 产出 `report_data_mix_eval_r2.html`。
>
> **纪律（不变）**：🚫 **不 kill 正在跑的 BO**；🚫 **不在 pretrain 释放前碰 GPU0-1**；🚫 **不改白名单 / 不起白名单外的下载**（⚠️ **数据下载失败需主动重启**：白名单内任一进程「失败 / 僵死 / 速率趋零 / PID 已死」⇒ 立即 kill+重启，见顶部「运维指令 · 2026-10-07」P0 块）；**心跳 ≤60 min** 且每步 commit + push；做不完**如实写卡点 + 需要什么 + 阻塞**；`TASK/MEMORY` 体积均 ≤32KB。



### 🔴 运维指令 · 2026-10-06（**配比实验改道**：废弃「目标尺寸模型 + 手挑单臂」→ 改「**小代理模型 + Optuna 贝叶斯优化 + 每卡独立 trial**」；**1 天搜 Stable / 1 天搜 Decay**）· **最高优先 · 立即执行**

> 📦 §改道方案·裁定原文（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：S0a方法学错(单臂2.2B)+成本失控(312GPU·h/臂)→改道小代理+BO(§①②③已归档,§④⑤⑥见下)。需要时再读。

> 📦 §改道方案 ①②③（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md（①立即动作）+ run/ARCHIVE_DATA_SPEC_HISTORY.md（②硬约束+③标定）；**结论**：kill S0a 完成、d=128/L=14 由第5轮块定案、标定5项必验全部通过（见 MEMORY_DATA.md）。需要时再读。

#### ④ 搜索空间（Optuna `suggest_*`）

- **Day1 · Stable 段（WSD 的 stable 主体）**：`web`（base / UltraX；**UltraX 🚫 未下 → 本轴降级为「仅 base」**，沿用 §0.6-B 既有口径）· `code` · `math` **三点、`sum=1`**。
  初值域：`web ∈ [0.80, 0.95]`、`code ∈ [0.03, 0.12]`、`math = 1 − web − code`（**让 BO 自己找，别把先验钉死**）。
- **Day2 · Decay 段（带 SFT 的退火）**：**`SFT 总占比 ∈ [0.40, 0.80]`**（⚠️ Xmodel-2 最优落在 **60–69%（取 64%）**，**是文献锚点不是答案**——**让 BO 自己搜**）+ **SFT 内部 5 类**（`Mathematics` / `Code` / `Logic` / `Knowledge` / `Commonsense`，**CoT 归 Logic**）**单纯形采样**。
- 搜索空间若有物理约束（`sum=1`、非负）→ 用 **`suggest_float` + 归一化**，**不要**用会越界的独立 `suggest_float`。

#### ⑤ 目标函数（objective）与收尾

- **主 objective = 固定 held-out 验证集 loss**（⭐ **整轮固定同一个 held-out bin，防泄**；用 `suggest=` 采样出的配比去训，在**同一验证 bin** 上测）。
  → 便宜、信号密、**可早停**；**别对 300+ 个模型都跑 `lm_eval`**。
- **早停**：`MedianPruner`（如 **1/3 步处 loss 显著差于中位 → prune**）→ 同 24h 内能跑**更多** trial。
- **收尾**：取 **top-K（如 5）** 配比跑 **`lm_eval` Table 2（8 集）/ Table 3（6 集）** 复核（复用 pretrain 已打通的 `ckpt → HF → lm_eval` 管线）。
- **可复现**：每 trial 落盘 **Optuna `sqlite` storage** + **trial 配置 CSV**（`number / params / steps / loss / status / created`）。
- **依赖安装**：`optuna` **装进独立 env**（🚫 **不许污染共享 `py310`**，见上方「环境隔离纪律」）；**外网命令显式带 proxy**（见上方 proxy 口径块）。

#### ⑥ 交付 & 纪律

- **交付**：**重写 `DATA_MIX_RECIPE.md §6`** = **① Optuna study 定义（搜索空间/采样器/pruner/objective）② trial 数（实测）③ 两段各自的最优配比百分比 ④ 外推到 2.2B 的迁移性说明**（引用 `ye2024datamixinglaws`；**如实标注「代理规模 ≠ 2.2B」这一限制**）；每 trial 一行进实验记录（`MEMORY_DATA.md` / `DATA_LEDGER.md`）。
- **口径统一**：`DATA_MIX_RECIPE.md` 里 §6 的模型尺寸数字**有 2.2B / 2.47B / 3B 三种写法** → **一并订正**（以 `pretrain_launcher.py` 的 `NVIDIAMambaHybridModelProvider2B` = **2.220B** 为唯一准据）。
- **纪律（不变）**：🚫 不改 pretrain 的脚本 / 🚫 不碰 `.29` GPU0–1 / 🚫 **不 kill 对方进程** / 🚫 **全轮不出现领域化** / 重 I/O 避让（`.29` 与 `.12` 共享 `/nas_train`）。
- **回写**：`MEMORY_DATA.md` 的「进度快照」+「运维问答」须写清 **标定结果** 与 **最终两段配比**。

> ✅ **本块生效即视为已批准**，**无需再等拍板**。**这是当前 data 线唯一主攻**（白名单下载巡检照常后台低强度进行）。
> 📌 **一句话**：**用小模型跑几百次试验去拟合配比，而不是用 2.2B 跑一次；两天（Stable / Decay 各一天）出配方。**


---

## 📦 已归档运维指令块（2026-10-08 · 唤醒218归档）

### 🆕 运维指令 · 2026-10-08（📝 **更新论文 LaTeX：把数据配比实验结论写入 `4_llm_pretrain.tex`**）· **用户直令：各线自己更新论文** · 高优先

> **用户令**：「让 pretrain，vision 和 data 更新一下论文。」
> ⚠️ **不要代笔写 LaTeX** —— 你只负责把你自己的实验数据填入对应的 `.tex` 文件，然后编译 `main.pdf`。
> ⚠️ **论文在 `BaiZe-ISEDA2027/` 目录下，与任务书同在一个 repo** —— 你直接可见可改。

**① 当前 `4_llm_pretrain.tex` 已有基础数据配比描述（Ultra-FineWeb-L3 EN 1.8T + code 1.2T + math 515G），但你的配比实验结论——特别是「其他配比在代理规模下不可分辨」这一发现——完全没反映。**
**`5_llm_posttrain.tex` §5.1 也提到了 domain annealing 数据，你可更新数据描述的具体数值。**

**② 建议更新的内容（自行判断，不一定要全写）：**
1. **数据配比实验结论**：配比实验在 18.36M 代理上的发现——最优区域稳定在 web 0.87–0.94 / code 0.06–0.12 / math≈0.01（`88:8:4`），但全量 lm_eval 排名与 BO 排名几乎反转（ρ=−0.80），全量分差仅 0.6pp ⇒ 该规模下「不可分辨」。
   - 可在 §4 数据段加一句诚实的说明：「At the proxy scale of 18.36M parameters, data mixture rankings were indistinguishable within 0.6pp, leading to the adoption of the 88:8:4 prior from the literature.」
2. **数据准备状态**：base（Ultra-FineWeb-L3 EN 6000 parquet / ZH 256 / EN 2048）✅ 全量下载完成并分词中；GPIC 下载进度；UltraX ✅ 完成。
3. **污染隔离**：黑名单机制已实施，EDA-Eval-PyAether 的 158 个任务已隔离，可更新论文中的 contamination control 描述。
4. **更新 `5_llm_posttrain.tex` 的数据描述**：SFT 数据（UltraData-SFT-Agent 51G）的实际规模和校验状态，若有新数据可更新数字。

**③ 格式纪律**
- 🚫 **不改 § 编号、不改 label、不改 cross-ref** —— 只更新数字、表格行、段落描述。
- ✅ **可以加子节 / 加段落 / 加表 / 加图** —— 但 label 和 cross-ref 不能冲突。
- **编译前先 `cd doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027 && rm -f main.aux main.bbl main.blg main.log`，然后 `pdflatex main && bibtex main && pdflatex main && pdflatex main`，确认 0 error。
- 编译后的 `main.pdf` **一起 commit**。
- **git 前缀**：`data 论文更新: ...`

**④ 本块不撤销之前的报告任务** —— 推荐顺序：**先更新论文（简短任务），再写全链路状态报告**。
> ⚠️ **注意**：更新论文时你仍然要维护分词/下载后台任务。论文修改在 CPU 上做，不冲突。

> 📦 本块加入后 TASK 约 32KB，仍 ≤32KB ✅。
> ✅ **执行完毕**（唤醒217, 2026-10-08）：更新 `4_llm_pretrain.tex` §4.5+§4.6 + `5_llm_posttrain.tex` §5.2+§5.4，main.pdf=9pp 0err，commit cbe0b641→debb3260。

### 🆕 运维指令 · 2026-10-08（📄 **数据准备全链路状态报告 HTML**）· **用户直令：各线自己写报告** · 高优先

> **用户令**：「把任务下发给各 agent，由 agent 自己写报告，不要替代他们写。」
> ⚠️ 你的配比收官报告 `report_data_mix_summary.html` ✅ 已交付。但**完整的数据全链路状态**尚未形成一份统一报告。**用户点名要 agent 自己写报告**。

**① 交付**：`report_data_pipeline_status.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 格式（沿用 house style）**
- **自包含**：内联 CSS + **数据图优先内联 SVG**；**零外链**；**HTML 本体 ≤200KB**。
- 位图一律 **JPEG、长边 ≤1280、q85**、单图 ≤400KB/总量 ≤4MB、**落本地并 commit**；🚫 严禁外链、🚫 严禁用文生图「编」数据图。
- **开头 1 行指向** `report_data_mix_summary.html`（配比专项已有，不再重复）。

**③ 建议 8 节**
1. **TL;DR**（3–5 条：base 下载 ✅ / 分词完成量 / GPIC 进度 / 配比实验结论 88:8:4 / 剩余瓶颈）；
2. **数据全景**（参考 `DATA_LEDGER.md`）：各源（Ultra-FineWeb L3 EN/ZH / GPIC / UltraX / en_v1_4）的 **规模、格式、下载状态、分词状态** 总表；
3. **下载状态**：base（✅ 全满：l1_en_hq 6000 parquet + zh 256 + en 2048）/ GPIC（5768/8001，ETA~2.1d）/ UltraX（✅ 479/479）/ en_v1_4（排队）；
4. **分词进度**：zh（7/8 shard ✅ 98.80B tok，s9 ~88% ETA~09:45）/ l1_en_hq（12 进程 s12-s23，ETA~16:00）/ 总 token 量与 ETA；
5. **配比实验**（指向 `report_data_mix_summary.html`）：一句话结论 + 对 P-8 的建议（88:8:4）；
6. **污染隔离**：黑名单机制 / 扫描进度 / 命中率（引用 `CONTAMINATION_CHECK.md`）；
7. **磁盘与资源**：`/nas_train` 用量 / 预计 P-8 所需空间 / 清理建议；
8. **下一步与风险**：待完成项 + 关键路径（分词完成 → P-8 启动 → GPIC 下完 → en_v1_4 放行）。

**④ 纪律**
- **数字必须真**：每个数字可由 `DATA_LEDGER.md` / `MEMORY_DATA.md` 巡检记录复算；
- **报告写作与后台任务不冲突**：分词/下载照常进行，写报告在 CPU 上并行做；
- **收尾按「收尾铁律」commit+push**（前缀 `data 管道报告: …`）。

> 📦 本块加入后 TASK 约 31KB，仍 ≤32KB ✅。如需归档，只归档下方已闭合旧块。
> ✅ **执行完毕**（唤醒217, 2026-10-08）：`report_data_pipeline_status.html`（31KB）已交付并 commit。

### 🆕 运维指令 · 2026-10-07⑥（📄 **配比实验「收官总报告」HTML**）· **用户直令** · 高优先

> **用户令（2026-10-07 夜）**：「**既然 ✅ 配比实验全部交付，让 data 写个 html 报告。**」
> ⚠️ **注意：不是再写一份 R2 专项** —— 你已交付 `report_data_mix_eval_r2.html`（18KB，R2 专项）。**本次要的是整条 §0.6-B 配比实验的「收官总报告」**，把 R1 → s_step → R2 → top-K 的弧线一次讲清。**请在报告开头用 1 行指向那份 R2 专项**（避免重复劳动，也避免出现两份同主题报告）。

**① 交付**：`report_data_mix_summary.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 格式（沿用 house style —— 参照 `report_10_06.html` / `report_10_07_data_overnight.html`）**
- **自包含**：内联 CSS + **数据图优先内联 SVG**；**零外链**；**HTML 本体 ≤200KB**。
- ⚠️ 你现有那份 R2 报告用的是**深色主题** ⇒ **收官报告请统一到 house style**（浅色，与其它报告一致）。
- 若用位图：**一律 JPEG、长边 ≤1280、q85**、单图 ≤400KB / 总量 ≤4MB、**落本地并 commit**；🚫 严禁外链、🚫 严禁用文生图「编」数据图。

**③ 建议 8 节**
1. **TL;DR**（3–5 条）；
2. **实验设计**：小代理 `d=128/L=14 ≈ 18.36M`（**显式标注「代理 ≠ 2.2B」**）· Optuna `TPESampler + MedianPruner` · 每卡独立 trial（TP1/DP1）· GBS/seq=2048 · `D`(token/trial) · Stable/Decay 两段；
3. **时间线**：R1（`loss` objective，`D=0.016B`，**ρ=−0.43**）→ ⭐ **`s_step` 归因（MBS 1→16：1432ms→166ms = 8.6×，`D` 抬到 0.5B）** → R2（`lm_eval` objective，**200/200**）→ **top-K 收尾**（retrain top-5 + HF 转换 + 全量 lm_eval）；
4. **R2 结果**：Top-10 配比表（web/code/math + score）+ **score 分布/收敛曲线（内联 SVG）**；
5. ⭐ **核心结论（必须诚实）**：**top-K 全量 lm_eval 排名与 BO 排名几乎反转**；**ρ=−0.80（n=5, p≈0.10）**；**全量分差仅 0.3835–0.3899 ≈ 0.6pp ⇒ 该规模下「不可分辨」**；math 占比贴下界；
6. **口径与局限**：代理规模 ≠ 2.2B · `--limit 500` 抽样 · n=5 · 单 seed？（**如实写**）；
7. **对 P-8 的建议**：**沿用先验 88:8:4**（最优区域稳定在 web 0.87–0.94 / code 0.06–0.12 / math≈0.01）；
8. **下一步**：Decay 段配比 · 提分辨率的手段（更大代理 / 多 seed / 全量评测替代抽样）。

**④ 纪律**：**数字必须真** —— 每个数字可由 `topk_lmeval_results_r2.json` / `mix_search_eval_r2.db` 复算；**结论跑完即固化**；收尾按「收尾铁律」commit+push（前缀 `data 配比收官: …`）。
> 📦 体积提醒：本块加入后 `BAIZE_DATA_TASK.md` ≈36KB ⇒ 收尾前先归档已闭合旧块。
> ✅ **执行完毕**（唤醒203, 2026-10-08）：`report_data_mix_summary.html`（29KB）已交付并 commit。


---

### 🆕 运维指令 · 2026-10-07④（**撤销「15:30 定时停 UltraX」：UltraX 续传下完（479/479）；GPIC 等它跑完再让回**）· **用户直令** · 最高优先

> **用户直令（2026-10-07 15:58）**：「**UltraX 停了吗？让它下完吧。**」
> ⓠ **本块【覆盖 / 作废】2026-10-07③① 中「UltraX 一完成（或 15:30 仍未完成）⇒ 立即把带宽全部让回 GPIC」这一条** —— **不再为 GPIC 提前掐 UltraX**。③① 的**其余部分仍然有效**：**不启动 `en_v1_4`**（继续排队）· GPIC 恢复后**报速率 + 新 ETA + `en_v1_4` 排队位置**。

**① 立即恢复 UltraX-Preview 下载，一直跑到 479/479 全部完成**
- **现状（唤醒191，15:27 已执行停）**：PID `2850809`（retry-loop）+ `1448940`（`hf download`）已 kill，停止点 = **210/479 parquet / 215GB / 487GB（≈44%）**；**已下部分必须保留、不删、不重下**。
- **动作**：用**同一脚本 `run/baize_download_ultrax.sh`** 重启 —— 同 repo **`openbmb/UltraX-Preview`**、**同一落盘 `/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/`**、同样「`--include` config 级 + 外网**显式 proxy** + `setsid nohup`（**`ppid=1` 必须核验**）+ retry-loop + log」。
- **续传口径（重启后先取证、再续跑）**：`hf download` **对已完整文件自动跳过、对 `*.incomplete` 断点续传** ⇒ **不得重下已完成的那 210 个 parquet**。取证原文：`ps -ef | grep -E 'hf download|download'` + 目录 `.incomplete` 计数 + 最新 mtime；**报告中要写清「跳过 N 个已完成 / 继续 M 个未完成」**。
- **报**：新 PID（含 `ppid=1` 核验）/ 当前 `n/479` / 已下字节 / rate（s per file）/ **新 ETA**。
- ⚠️ **若发现 `hf download` 无法只补增量（要重整目录 / 报 hash 冲突）** ⇒ **先停下、如实报根因**，不要为了「续传」删掉已下的 215GB。

**② 禁止再设「预设定时终止」**：
- 唤醒190 设的 `sleep 2580 && kill -- -2850809`（15:2x 已触发，唤醒191 已清理 timer）**作废并且不得再设**。
- **要停只能由运维/用户明确下令**，或走既有「下载失败 / 僵死 / 速率趋零 / PID 已死 ⇒ 立即 kill + 重启」口径。

**③ 新收尾顺序**：**UltraX 下完（479/479）⇒ 带宽全部让回 GPIC（追 8001 tar）⇒ GPIC 下完后再由运维决定是否放 `en_v1_4`**。
- **GPIC 本体**：**不 kill、不重启**（除非命中上面「失败/僵死」口径）；UltraX 续传期间 GPIC 掉速属**已知带宽分流**，**如实记录、如实报**，**不必为 GPIC 掐 UltraX**。
- `en_v1_4` **继续排队、不启动**；🚫 不让 UltraX 与 `en_v1_4` 同时全速。

**⑤ 铁律（不变）**：🚫 **不 kill BO**（`.29` Round2 继续跑到 200 trial）· 分词保持 **`nice -19`** · **不启动白名单外下载** · `.bin/.idx` 与原始集**不入 git** · 每唤醒心跳**固定一行**下载状态（**UltraX 计数 + rate + ETA 必报**）· 「与推测冲突时**以测到为准**」。

> 📦 **体积**：本块加入后 `BAIZE_DATA_TASK.md` ≈**36KB**（**< 40KB 红线** ✅）。若需回落 32KB，**只把【已闭合】的旧块**（如 ② 白名单解禁块，已执行完）**原文搬进** `ARCHIVE_OPERATOR_DATA.md`（**留 1 行指针**），**不得删改 / 精简 ④ 块**。

---

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

---

### 🆕🆕🆕 运维指令 · 2026-10-09③（**停②：停掉Code/Math重头来 + 加Ultra-FineWeb-L3 + 放开并发**）· **用户直令** · 最高优先 · 覆盖②

> **用户直令（2026-10-09③）**：
> 1. Code/Math 刚开始才切了一部分，**停掉，重新来**——每个目录所有文件全切，不挑不漏
> 2. Ultra-FineWeb-L3 也加入分词
> 3. 一共 224 个核，**为什么一个数据源只能 8 并发？放开**
> 4. Ultra-FineWeb 目录只剩 197GB，分词 .bin 却有 2.0TB——**data agent 核实是否合理，回报**
> 5. 不要创造新名字（如 "Code L2"），**就按原始 6 个目录来**

**① 立即停止当前 Code/Math 分词进程**
- `kill` 所有 `preprocess_data.py` / `preprocess_data_cm.py` 进程
- 删除 ② 启动的部分产物（`baize-data/text/code_s*.bin/.idx/.json`、`math_s*.bin/.idx/.json`），从头来
- 报告：已 kill 几个 PID，已删哪些文件

**② 三个目录全量分词（每个目录下所有文件，不挑不漏，不设上限/下限）**

| 目录 | 文件数 | 磁盘 | 原始路径 | 落盘命名 |
|:---|---:|---:|:---|:---|
| `Ultra-FineWeb-L3` | 1,764 parquet | 1.8 TB | `/nas_inference/.../Ultra-FineWeb-L3/data/` | `l3_s{i}` |
| `UltraData-Code` | 1,121 parquet | 1.2 TB | `/nas_inference/.../UltraData-Code/data/` | `code_s{i}` |
| `UltraData-Math` | 1,823 parquet | 515 GB | `/nas_inference/.../UltraData-Math/data/` | `math_s{i}` |

- **口径**：每个目录下**所有** parquet 文件全切，不按子目录挑拣，不设上限/下限
- **tokenizer** = `tokenizer_eod`（DeepSeek-V4.1-Flash + EOD）
- **格式** = Megatron-LM `.bin/.idx/.json`（int32，4 字节/token），**不入 git**
- **落盘** = `/nas_train/app.e0031982/datasets/baize-data/text/`
- 每个目录先 smoke test 1 个 parquet 确认 text column 名（`content` / `text` / `full_content` 等），再批量切

**③ 并发：放开用满 224 核**
- 224 核可用，**每个数据源可以开 20–50 并发**（按文件数分配进程，每个进程处理一个子目录或一组 parquet）
- 三个目录合计可以跑 **60–100+ 进程**
- `nice -n 10`（GPIC 下载优先级更高），但**不必保守到 8**
- GPIC 下载是网络 I/O bound，分词是 CPU bound，**不争资源**
- 监控 load / NFS 吞吐 / GPIC 速率（若 GPIC 掉到 <30 tar/h 才减并发）

**④ Ultra-FineWeb 197GB → 2.0TB .bin 核实（data agent 必须回报）**
- 目录 `Ultra-FineWeb` 当前只剩 162 parquet / 197GB
- 分词产物 `mix_base/` 有 44 shards / 2.0TB / 524.43B token
- **data agent 回报**：
  1. Ultra-FineWeb 原始下载到底多少 GB？（查历史记录 / HF 缓存）
  2. 是否分词后删除了大部分原始 parquet？197GB 是残留还是全部？
  3. 524.43B token 对应的原始数据量是多少？
  4. 197GB → 2.0TB .bin 是否合理？（int32 = 4 字节/token，524.43B × 4 ≈ 2.1TB）

**⑤ 全量盘点（每唤醒心跳必报，按原始 6 个目录）**
- 每个目录报：原始多少 GB / 多少文件 / 分词多少 token / .bin 多少 GB / 是否对应
- 三个正在切的：报进度、token 数、活 PID、ETA
- GPIC 下载：照常报

| 目录 | 原始 | 文件 | 分词状态 | 已切 token | .bin |
|:---|---:|---:|:---|---:|---:|
| `Ultra-FineWeb` | 197 GB（?） | 162 parquet | ✅ 完成 | 524.43 B | 2.0 TB |
| `Ultra-FineWeb-L3` | 1.8 TB | 1,764 parquet | ❌ 未开始 | 0 | 0 |
| `UltraData-Code` | 1.2 TB | 1,121 parquet | 🔄 重来 | 0 | 0 |
| `UltraData-Math` | 515 GB | 1,823 parquet | 🔄 重来 | 0 | 0 |
| `UltraData-SFT-2605` | 298 GB | 1,504 jsonl | ✅ 完成 | 20.96 B | 79 GB |
| `UltraData-SFT-Agent-2609` | 51 GB | 50 jsonl | ✅ 完成 | 8.04 B | 30 GB |

**⑥ 投料前污染扫描（所有分词完成后做）**
- 对所有新分词产物跑 `check_contamination.py`（blacklist = 6 快照并集 536 任务 / 193,295 13-gram + 10 8-gram）
- 采样 ≥ 10K docs / 源 → 0 命中则可投料
- 结果写入 `CONTAMINATION_CHECK.md`

**⑦ 铁律（不变）**
- 🚫 不 kill GPIC 下载（PID 144981 保持运行）
- 🚫 不改 tokenizer / 不改 .bin/.idx 格式
- 🚫 不入 git（.bin/.idx/.json 产物不入库）
- 🚫 不挑不漏：每个目录所有文件都切
- 分词用 `nice -n 10`，心跳 ≤ 60 min 且每步 commit + push
- TASK/MEMORY ≤ 32KB

> 📦 ② 已归档至 git 历史（commit 0dd41843），本块覆盖②。
> **执行结论**：①kill 34旧进程+删46产物✅ ②R3全量分词110/110DONE(1483.91B tok/5.94TB)✅ ③并发110进程(nice -n 10)✅ ④Ultra-FineWeb核实(197GB→2.0TB合理:524.43B×4≈2.1TB)✅ ⑤6目录盘点(全✅)✅ ⑥污染扫描30/30 DONE(60K docs,0命中,累计220K docs全0命中)✅ ⑦铁律已遵守✅。归档自BAIZE_DATA_TASK.md 2026-10-10(唤醒303)。

---

### 🆕 运维指令 · 2026-10-11（📚 **文献借鉴报告**：从 research 线近期论文里找可借鉴 idea · 中文 HTML）· 用户直令 · 高优先

> **用户原话（2026-10-11）**：「**data** 看看**这几天 research 积累的论文**，看看有没有什么可以借鉴的 idea，**写个 html 报告（中文版）**。」
> **性质**：**纯阅读 + 写作**（🚫 不占 GPU、🚫 不打断两路下载巡检、🚫 不做重 I/O）。

**① 交付物**：`doc/BaiZe-ISEDA2027/report_data_lit_ideas.html`（**中文 · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB**）。

**② 输入（先 `git pull`，再读）**
- research 线近期日报（每天 5 篇）：**仓根相对** `doc/personal-watch/run/research/daily/2026-10-07.html` … `2026-10-11.html`（**共 25 篇**）。
- 精选与台账：`doc/personal-watch/run/research/TOP_K.md` + `TOP_K.jsonl` · `papers.jsonl` · `TAKEAWAYS.md`。
- 可对照本仓：`doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-04.html` / `LIT_IDEAS_2026-10-05.html` + 本线 `run/DATA_RESEARCH.md`。

**③ 本线关注面**：数据配比与课程（annealing）· 质量过滤 / 去重 / 污染检测 · 合成数据与改写 · tokenizer · 长上下文数据构造 · 多模态图文对与配对 · 数据规模 vs 质量。

**④ 每条 idea 必带（缺一不可）**：① 出处（**原题 + arXiv ID + URL + 日期**）② 一句话做了什么 ③ **与本线的关系**（**能用在 P-8 投料配比 / R3 分词 / 污染扫描 / 后续档位 的哪一步，具体到源/脚本**）④ **借鉴成本**（GPU·h / 墙钟 / 数据依赖）⑤ **风险/不确定性** ⑥ **价签**（可行性 × 潜力 打分）。
- **按「对本线的可执行价值」排序 · 给 TOP-5**；其余列附表。
- **显著区分**「**已验证可借鉴**」vs「**仅灵感/未验证**」；🚫 不得拿二手/摘要页当一手；**每条须可溯源**。

**⑤ 纪律**：🚫 不改下载白名单 / 不 kill 下载进程；🚫 不跑重 I/O；commit 前缀 `data lit-rpt:`；任务书 >32KB 自滚归档。

> **执行结论**：report_data_lit_ideas.html（36KB 自包含中文 HTML）已生成并推送（commit c80c7a74）。覆盖 research 线 2026-10-07~10-11 共 25 篇 arXiv 日报 → TOP-5 可借鉴（Conditional Transfer 2610.11548 配比三信号 / CoTrace 2610.10426 数据配方 / MiMo-V2.6 2610.11959 多模态退火 / Beyond Owls 2610.10657 污染检测盲区 / OPD Fails 2610.11247 teacher选择）+ 3 附录 + 25 篇全量覆盖表 + 价签汇总 + 方法论口径。全 25 篇 arXiv ID 经 papers.jsonl 逐一核实✅。17/25 篇判定无关。唤醒338(2026-10-11 20:30)产出，唤醒339(2026-10-12 00:42)验证ID正确性后归档。归档自BAIZE_DATA_TASK.md 2026-10-12(唤醒339)。


---

### 🆕 运维指令 · 2026-10-10（更正：85M 总量 = 46.7TB，否 7701/27T）· 用户直令 · 最高优先

> 用户核实（2026-10-10 晚）：HF 官方页明写 `Total file size: 46.7 TB` ——
> https://huggingface.co/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M

① 事实（运维已用 HF API 复核）
- 仓库顶层 = 8 个子集目录：`coyo` · `datacomp1b` · `imagenet` · `laioncn` · `mint` · `obelics` · `sa1b` · `zero250m`（+ `.gitattributes`/`README.md`）。
- 官方总量 ≈ 46.7 TB（约 12,124 parquet）。

② 唤醒 302 的「更正 7701/27T」❌ 作废 —— 两处口径错误
1. 漏子集：302 的 per-subdir 只列了 6 个（coyo+datacomp1b+imagenet+laioncn+mint+obelics = 7701），把 `sa1b`(≈5.09TB) 与 `zero250m`(≈4.76TB) 整个漏掉（≈9.85TB）。
2. 混淆「已下」与「总量」：`du=27T` 是本地已下载字节，不是仓库总量。以「本地 `.metadata`/已下 parquet 计数」当分母 ⇒ 必然把「未开始」误判成「已完成」。

③ 正确口径（请据此重算并落表）
- 总量 ≈ 46.66 TB / ~12,124 files（分母用 HF 仓库总量，❌ 不用本地 `.metadata` 计数）。
- 本地已下 ≈ 27 TB ≈ 57%；剩余 ≈ 20 TB。
- ETA（@12–16.6MB/s）≈ 14–25 天（保守 8MB/s → ≈29 天）⇒ 不是「10–30 分钟」。

④ 执行
1. 用 HF API 逐子集核实 —— `HfApi().list_repo_tree(repo, recursive=True)` 或 `/tree/main?recursive=true`，统计 8 个子集各自的【文件数 / 字节】，落一张表：`子集 | 总量 | 已下 | 剩余 | 是否已开始`。
2. 明确纠正 `MEMORY_DATA.md` 心跳 + `daily-memories-data/2026-10-10.md` 里的「85M 100% / 27T / ETA 10–30min」写法；`sa1b`/`zero250m` 若未开始须标「未开始」，不得计入已完成。
3. 重报 85M 真实进度% + ETA（分母 = 仓库总量）。

⑤ 纪律不变：只读巡检，不 kill / 不重启 / 不改并发（85M 由用户自管，data 线仅巡检；除僵死按既定纪律处理）。

> 📌 教训（记进本轮流水）：`huggingface_hub` 的本地 `.metadata` / 已下文件计数 = 已下载进度，≠ 仓库总量；总量必须取自 HF 仓库 tree/API。

> **执行结论**：唤醒302-310已用HfApi核实85M 8子集精确总量(12,124files/46.663TB)，纠正了MEMORY+daily-memories中的错误口径。85M总量=46.66TB已写入心跳。归档自BAIZE_DATA_TASK.md 2026-10-13(唤醒404)。

### 🆕 运维指令 · 2026-10-10（巡检并发下载 `85M` + `en_v1_4` · 回报各自速度/ETA）· 用户直令 · 最高优先

> 用户令（2026-10-10 傍晚）：「我在同时下载 85M 和 en_v1_4，请看下各自下载速度和 ETA。」

① 背景
- `en_v1_4` = `openbmb/Ultra-FineWeb` · `data/ultrafineweb_en_v1_4/`（56,461 文件 / 6.75TB）——本轮由 data 线 parallel 脚本 `run/data_pipeline/download_en_v1_4.py` 下载（PID 2535486，24 workers + hf_transfer，落盘 `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/`）。
- `85M` = `mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M`（此前 §0.7.A 曾停；用户当前另行在同时下载）。

② 执行（纯巡检，不改动任何下载）
1. 判活：`pgrep -af 'hf download|download_en_v1_4|LLaVA|Ultra-FineWeb'`（各留原文；确认两路进程是否都在）。
2. 两路各自取证（每路都要）：
   - 已落盘：`find <dir> -name '*.parquet' | wc -l` + `du -sh <dir>`（间隔 60–120s 取两次求增量，⚠️ 不用总比例估）；
   - 在途：`*.incomplete` 字节增长（`ls -l --time-style=+%H:%M` 两次）或 `/proc/<pid>/io` 的 `write_bytes` 6s 增量；
   - log 尾部：`tail -n 5` 对应日志（`en_v1_4` → `/tmp/en_v1_4_dl.log`；`85M` → 其自身 `nohup`/`hf` 日志）。
3. 算速度 + ETA（分路，给 ± 区间）：
   - `en_v1_4`：速度（files/min 与 MB/s 双口径）→ ETA = 剩余文件/字节 ÷ 速度。
   - `85M`：同上 —— ⚠️ 85M 是图像+文本 parquet，单件体积与 en_v1_4 量级差异大，ETA 必须按字节算，不能按文件数比例。
   - 注明争用：两条同时跑 = 共享出口带宽，故实测速度 = 争用后速度；若能推断「单跑」速度，一并给出对比。

③ 纪律
- 只读巡检：不 kill / 不重启 / 不改并发。唯一例外 = 某路僵死（`write_bytes` 长时间 0 且 PID 已死）→ 才按既定纪律 kill + 同命令续传，并标「已重启」+ 新 PID。
- 外网命令显式带 proxy；每条可能慢的命令带 `timeout`；不对大目录做全树遍历（`find` 限深度 / 限定子目录）。
- 判活不许用文件数比例估，用字节增量 / `/proc/io`。

④ 回写：本指令块下贴「两路各自：PID / 已落盘 / 实测速度 / ETA」表；同步更新 `MEMORY_DATA.md` 心跳与 `daily-memories-data/2026-10-10.md`。

⑤ 体积：若 TASK 超 32KB，按「体积维护规程」把已闭合旧块原文搬入 `ARCHIVE_OPERATOR_DATA.md`（只搬迁留指针）。

> **执行结论**：唤醒302-310已执行两路并发巡检,85M(en_v1_4)各自速度/ETA已报。后续唤醒持续看护。归档自BAIZE_DATA_TASK.md 2026-10-13(唤醒404)。
---

### 🆕 运维指令 · 2026-10-13（🔍 为 vision encoder 训练在 HuggingFace 找「图文对」数据集 · 要求 image 带 bytes（非 url）· 中文 HTML 报告）· 用户直令 · 高优先（归档自 BAIZE_DATA_TASK.md 2026-10-14 唤醒427）

> 用户令（2026-10-13）：「data：使用 web search 给 vision encoder 训练在 huggingface 上找图文对数据集（要求 image 带 bytes 而非 url），输出 html 报告（中文）。」
> 性质：纯 web 调研 + 写报告，CPU/网络，不占 GPU；web 请求不占 NFS 带宽，不打断 en_v1_4 / 85M 下载。

① 目标：为 Stage (iii) 视觉编码器对比预训练（现有 = GPIC + CC12M + Amshaker ≈59M 对）寻找可直接下载即用的图文对数据集，重点是 image 列存的是真实像素 bytes（HF `Image` feature / parquet 内嵌二进制），而非仅 URL。

② 逐条筛选口径（每项给证据）：
1. image 载体：确认 image 列 feature 类型 —— ✅ `Image`(bytes) / `{bytes,path}` vs ❌ `string`(url) / `{url}`。最硬证据 = HF `datasets-server` `/info` 或 `/first-rows` 返回 `features['image'] == {'_type':'Image'}`（仅看文字描述不算）。
2. 规模：图片对数 + 总字节（可估）。
3. 许可：license（cc-by(-sa) / mit / apache / 未标注）。
4. caption：短/长 caption、alt-text；语言 en / zh / multi。
5. 是否已用（GPIC / CC12M / Amshaker / LAION 系须标注，避免重复）。
6. 可达性：HF 直连/镜像、是否 gated。

③ 方法：HF Hub + `datasets-server` API 检索（`image-text pairs` · `caption` · `interleaved` · `alt-text` · `DataComp` · `pixelprose` · `redcaps` · `mmc4` · `OBELICS` · `MINT` · `wit` · `datacomp`…）；可用 `huggingface_hub` 列 features 佐证。

④ 交付：`doc/BaiZe-ISEDA2027/report_data_hf_imagetext_datasets_zh.html`（中文 · 自包含 · 内联 CSS · 零外链 · ≤200KB）。必需节：① HERO+TL;DR（TOP 3–5 推荐）② 口径与 bytes/url 判定法 ③ 主表（HF id · 对数 · 总大小 · image 载体证据 · caption · 语言 · 许可 · gated · 是否已用 · 推荐度）④ 三分类（✅bytes 可直接训 / ⚠️url 需抓 / ❌不可用）⑤ 下载命令模板 + 落盘路径建议 + 预估磁盘 ⑥ 与 GPIC/CC12M/Amshaker 互补性 ⑦ 风险/诚实条款。

⑤ 纪律：🚫 不占 GPU · 🚫 不 kill / 不打断 en_v1_4、85M 下载 · 🚫 本令只调研+出报告，不下数据（真下载须运维二次确认）· 每条带 HF url + 访问日 · commit 前缀 `data rpt:` · 任务书 >32KB 自滚归档。

> **执行结论**：唤醒404已交付 report_data_hf_imagetext_datasets_zh.html,含TOP-5推荐(WebMix-38M/wit_base/GPIC已用/the_cauldron/InternVL-SA1B)+bytes/url判定法+主表+三分类+下载模板+互补性+风险条款。归档自BAIZE_DATA_TASK.md 2026-10-14(唤醒427)。

---

### 🆕 运维指令 · 2026-10-13（📥 把 85M 下载从「用户自管」移交给 data 线启动 + 看护）· 用户直令 · 最高优先（归档自 BAIZE_DATA_TASK.md 2026-10-14 唤醒427）

> 用户令（2026-10-13）：「把运维（用户）起的 85M 下载停掉，由 data 启动和看护这个数据下载。」
> 背景：`mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M` 目前由用户自管进程在跑（此前 PID 1015571→555408，ppid 非 data 线），不在 data 线 kill+restart 看护纪律内，CDN 抖动崩了会静默卡住。现正式移交 data 线。

① 停掉用户进程（先定位再杀）：
1. `pgrep -af 'LLaVA-OneVision-1.5-Mid-Training-85M'`（或 `ps aux | grep 'hf download.*mvp-lab'`）定位当前 85M 进程（`hf download` 的 child，ppid 非 data 线）。
2. `kill <pid>`（SIGTERM）→ 等 10–20s → `pgrep` 复核已退；僵死则 `kill -9`。
3. ⚠️ 安全：`hf download` 可断点续传，杀进程不丢已下 parquet；`.incomplete` 残留见下清理。

② 由 data 线重启并接管（复用你现有 en_v1_4/GPIC 的「setsid 重启续传」套路，即唤醒 33/35 处置 base/SFT-2605 的同一套）：
1. 先核实落盘路径（`ls -d` / `du -sh`）：`/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M`（以实测为准，若实际在别处如实记「实际路径=X」）。
2. 清残留：`find <dir> -name '*.incomplete' -delete`（只删 `.incomplete`，勿动已下 parquet）。
3. 重启（断点续传，绝不重下）：`setsid -f nohup hf download --repo-type dataset mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M --local-dir <dir> > /tmp/85M_dl.log 2>&1`（如需 token 照旧加 `--token <HF_TOKEN>`；并发/workers 你按「不与 en_v1_4 互相饿死」自行定，如 `HF_HUB_ENABLE_HF_TRANSFER=1` 或有限并发）。
4. 记新 PID，写进 `MEMORY_DATA.md` 心跳，把「85M 用户自管」改为「85M data 线看护 PID=xxx」。

③ 纳入看护纪律（与 en_v1_4 / GPIC 相同）：
- 每唤醒 `pgrep` 判活；死/僵/速率趋零 → 立即 kill+重启续传（前置清 `.incomplete`），不必等运维点名。
- 心跳逐子集报（8 子集 coyo/datacomp1b/imagenet/laioncn/mint/obelics/sa1b/zero250m 各自 file 数），重点盯 `sa1b`+`zero250m` 两个一直未开始的子集（≈9.85TB，是剩余大头）。
- 速度/ETA 用「字节增量 + 仓库总量 46.66TB 分母」口径（延续 2026-10-10 更正；✅ 不用本地 `.metadata` 当分母）。
- 与 en_v1_4 并行，两条各自报速度 + 注明共享带宽争用。

④ 磁盘注意：`/nas_train` 现 ~85%（剩 ~32T），85M 剩余 ~17TB → 够放但告警；逼近 90% 或 85M 会越界就心跳标红 + 停 85M 等运维，🚫 不自作主张删任何数据。

⑤ 完成后：85M 下满 → `du -sh` 全量核实 ≈46.66TB / 12,124 files → 心跳报「85M 完成」→ 等运维指示再决定后续打包/对齐（85M 是多模态 mid-training 数据，非 P-8 LLM 投料，⚠️ 不并入 86:10:4 混料）。

> **执行结论**：唤醒405已将85M从用户自管移交data线启动+看护(PID2420118/2420132),后因用户令10-13暂停(8436/12124=69.6%),再因用户令10-14保持暂停。归档自BAIZE_DATA_TASK.md 2026-10-14(唤醒427)。
---

### 🚨 运维指令 · 2026-10-07（P0 · 两条下载线（base + GPIC）继续 / 立即重启 —— 正文口径统一为「数据下载失败需主动重启」）· 最高优先 · 用户直令（归档自 BAIZE_DATA_TASK.md 2026-10-14 唤醒427）

> 用户 2026-10-07 直令：data 的两条数据下载线必须继续跑 —— base 死了 / 僵死就重启，从来没有过「拖着不动」的指令（用户原话逐字见 `run/ARCHIVE_OPERATOR_DATA.md`「2026-10-07 口径修正」块）。
> ⇒ ① 两条下载线必须持续在跑：base（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）+ GPIC；② 从来没有过「base 死了就拖着不动」的指令 —— 你心跳里连写的 `Base 下载: 进程已死（按指令保持不动）` 属误读，立即废止该口径。

> 🔍 误读溯源（运维自查，如实说）：旧第 36 行那句 `🚫 不改白名单 / 不动下载`，本是 2026-10-03 白名单锁定时的巡检纪律，原意 =「不要擅自改白名单、不要乱动［健康的］下载」，不是「下载失败也不许重启」。2026-10-06 15:1x 用户已直令重启 base，那个 P0 块处置完后被归档进 `ARCHIVE_OPERATOR_DATA.md`（唤醒 167）⇒ 正文只剩「不动」半句，重启授权随归档一并消失。表述缺陷在运维，不在你。 完整溯源（含用户原话 + 被替换掉的旧字句原文）见归档「口径修正 · 2026-10-07」块。
> ✅ 永久口径（即刻生效，覆盖旧表述）：数据下载失败需主动重启 —— 白名单内任一下载「失败 / 僵死 / 速率趋零 / PID 已死」⇒ 立即 `kill`（若还在）+ 重启（沿用既有 retry-loop 规程），报告里标「已重启」+ 新 PID；不再需要等运维点名。
> 🚫 该条纪律今后只剩一种含义：不改白名单、不起白名单外的新下载；白名单内下载失败 ⇒ 按「数据下载失败需主动重启」处理，不许再写「保持不动」。

> 本轮唤醒内做完（不许拖到下轮）：
> 1. 取证：`ps -ef | grep -Ei 'hf download|huggingface-cli|hf_transfer|download_it_pairs'`（留原文）+ 两目录 `.incomplete` 计数 + 最新 mtime。
> 2. 重启 base（`l1_en_hq` 停在 5476/6006 ≈91%、`zh` ✅ 256/256 已满）：
>    - `--include 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*'`（config 级）；🚫 绝不拉 `en_v1_4`；
>    - retry-loop 包裹（失败 `sleep 30` 自愈 —— 你 2026-10-04 唤醒 85 用过、有效）+ `setsid nohup`（`ppid=1`）+ log `Ultra-FineWeb/download_l1_zh.log`；
>    - ⚠️ 外网命令显式带 proxy（`.12` 用你 `~/.bashrc` 里的那个值）；
>    - 命令原文 + 首次输出（起步 part 号）贴心跳。
> 3. GPIC 判活（PID / `gpic_train_XXXX.tar` mtime / 24h 新增 tar 数）→ 死即重启（父 `download_it_pairs.sh` 一并核）；目标 8001 tar + test 128 ✓。
> 4. 心跳格式（本轮起固定写一行）：`下载线：base l1_en_hq <n>/6006（+Δ, 活/已重启 PID, ETA）· zh ✅256/256 | GPIC <n>/8001（+Δ, 活/已重启 PID, ETA）`。
> 5. P-8 关联（为什么急）：base = P-8（Stage (i) 本体）硬前置（已分词仅 22.05B tok，P-8 需 ~100B）⇒ base 下满即解锁 P-8 备料；`l1_en_hq` + `zh` 双满 ⇒ 报运维「MiniCPM5 base 族就绪」。

> 纪律（不变）：🚫 不 kill 正在跑的 BO；🚫 不在 pretrain 释放前碰 GPU0-1；🚫 重 I/O 与 `.29` 抢 `/nas_train`；心跳 ≤60 min 且每步 commit + push；`TASK/MEMORY` ≤32KB。

> **执行结论**：该P0块已被2026-10-14用户令暂停全部4路下载取代。base下载已完成(l1_en_hq✅+zh✅256/256),GPIC✅8160tar。永久口径「数据下载失败需主动重启」仍有效但当前为暂停态。归档自BAIZE_DATA_TASK.md 2026-10-14(唤醒427)。

---

### 🆕 运维指令 · 2026-10-14（⏸ 暂停全部 4 路下载）· 用户直令 · 最高优先

> **用户令（2026-10-14）**：「让 data 把数据下载暂停一下。」（运维已确认范围：**全部 4 路**）

**① 暂停对象（4 路，全部 kill）**：
1. `en_v1_4`（hf download，PID 2535486，及任何 en_v1_4 相关进程）
2. `WebMix-38M`（retry-loop wrapper + hf download 子进程）
3. `wit_base`（同上）
4. `InternVL-SA1B`（同上）

**② 暂停方式**：
- **先 kill retry-loop wrapper 再 kill hf download**（否则 wrapper 会自动重启 hf）。
- `pkill -f` / `kill` 后用 `pgrep -af` 复核 4 路全部已退。
- 🚫 **保留已下内容**（不删任何 parquet / tar）；`.incomplete` 默认保留（便于将来断点续传）。

**③ 心跳更新**：4 路全标 `⏸ 暂停（用户令 2026-10-14）`，并记各自已下进度（en_v1_4 ~58%、3 路图文对已下 GB 数）。

**④ 纪律**：🚫 不删任何已有数据；85M 本就是暂停态（不动）；GPIC ✅ / the_cauldron ✅ 已完成的也不动；`setsid` 守护进程清理干净；commit 前缀 `data dl:` · 任务书 >32KB 自滚归档。

> **执行结论**：该块已被同日「▶️ 恢复全部 4 路下载」块取代；4 路均已恢复断点续传，WebMix/wit_base/InternVL-SA1B 陆续下满，en_v1_4 仍在下载中。归档自 BAIZE_DATA_TASK.md 2026-10-17(唤醒511)。

## 运维指令 · 2026-10-15（⬇️ 补下 UltraData-RL-2609 + 复核 SFT-2605）· 用户直令 · 最高优先

(2026-10-18 运维自 BAIZE_DATA_TASK.md 原文搬入，未改一字)

**① 运维已预核（RUN_ID 99 · 2026-10-15 21:17 实测，供你复核起点 · 机读事实）**

| 数据集 | 盘上实测 | 判定 |
|:--|:--|:--|
| `UltraData-SFT-2605` | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605` → **1504 jsonl / `.incomplete`=0 / ≈297.08 GB**（`data/{no_think,think}`，顶层 README/LICENSE/.gitattributes 齐） | ✅ **不缺**（10-02 已重下并逐字节核验）⇒ 🚫 **不要重下** |
| `UltraData-RL-2609` | `/nas_inference` `/nas_user` `/nas_env` `/nas_train` **四个盘皆无**；HF 缓存仅 `datasets--openbmb--Ultra-FineWeb` | ❌ **确实没下** ⇒ **需补下** |

**② 授权：用户直令「解除白名单」——仅限本项**：`openbmb/UltraData-RL-2609` 此前属「白名单外一律不下载」；**本令起放行该一项**。🚫 **不得**借此扩权到其他白名单外数据集。
- HF API 事实（10-15 实测）：**`gated=False`（公开，无需接条款）** · `siblings=26` · `lastModified=2026-09-07`；⚠️ **该 API 未回 size** ⇒ **下载前必须先用 `hf download --dry-run`（或 HfApi 列文件）取实际文件数 + 总字节，并如实回报**。

**③ 下载要求**
- **落盘（白名单内，按余量二选一）**：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-RL-2609`（**9.4T free**）或 `/nas_env/app.e0031982/datasets/openbmb/UltraData-RL-2609`（**9.9T free**）。
- **proxy 直连 hf.co**：`https_proxy=http://172.19.92.25:13128`（与既有下载同口径；🚫 不用 hf-mirror）。
- `setsid` 守护 + **正确 PATH**（`bash -lc` 或显式 PATH，防 `env: 'hf': No such file`）；沿用既有 **retry-loop 模式**（先起 wrapper 再起 hf 子进程）。
- ⚠️ **带宽纪律**：当前 **3 路在跑**（`en_v1_4` / `WebMix-38M` / `InternVL-SA1B`）——先记录各路 last-file 时间戳与速率作基线，**若新下载把它们挤到「速率趋零」，就错峰或调小 `--max-workers`**；老线一旦僵死/死掉，仍按常驻口径 **kill + restart**。

**④ 收尾 / 回报**
1. **进度表**：PID（wrapper + hf）· 已下文件数 / 总文件数 · 已下字节 · 速率 · ETA · **落盘路径** + `df -h` 余量。
2. **下完自校**：文件数 == HF 清单数、`.incomplete == 0`，并与 HfApi 清单**逐文件字节比对**（沿用 10-02 对 SFT-2605 的核验口径），结果写进 `DATA_LEDGER.md`。
3. `MEMORY_DATA.md` 进度快照 + `daily-memories-data/2026-10-15.md`；commit 前缀 `data dl:`。
4. **如实**：不可达 / 被限流 / 失败 ⇒ 写「失败 + 原文报错」，🚫 不编造进度；查不到就写「未找到」。

**⑤ 纪律**：🚫 不删任何已有数据；`GPIC` / `the_cauldron` / `wit_base` / **`UltraData-SFT-2605`（已下满，勿动）** 均不动；**85M 维持暂停**；错峰 IO；任务书 >32KB 自滚归档。

## 运维指令 · 2026-10-14（▶️ 恢复全部 4 路下载 · 断点续传）· 用户直令 · 最高优先

(2026-10-18 运维自 BAIZE_DATA_TASK.md 原文搬入，未改一字)



> **用户令（2026-10-14）**：「data 数据下载 resume。」（= 解除同日「⏸ 暂停全部 4 路下载」）
> **范围**：**恢复 `en_v1_4` + `WebMix-38M` + `wit_base` + `InternVL-SA1B` 共 4 路**（断点续传、`.incomplete` 处继续）。
> ⚠️ **85M 本令不含**：维持暂停（2026-10-13 令）——**除非用户另指，不恢复 85M**。

**① 恢复前先核（只读）**：`df -h` 确认目标盘已挂载且余量足；`ls -la` 确认各路 `.incomplete` 仍在。
- ⚠️ 余量提示：`/nas_train 85%（32T free）` · `/nas_user 75%（28T free）` · `/nas_env 1%（9.9T）`。

**② 恢复方式（逐路 · 断点续传）**：
- **用停前的同一下载方式续传**（`hf download --resume` / 现有 retry-loop 脚本），**🚫 勿从头下**（`.incomplete` 已在）。
- **`setsid` 守护** + **正确 PATH**（登录 shell `bash -lc` 或显式 PATH；防 `env: 'hf'/'cline': No such file`）；**先起 wrapper（retry-loop）再起 hf 子进程**（与暂停时相反顺序）。
- **落盘白名单（不变）**：`/nas_inference/app.e0031982/datasets/` · `/nas_user/<user>/datasets/` · `/nas_env/app.e0031982/datasets/`（新增）；🚫 仍不放 `/nas_train`（**`en_v1_4` 是文本语料，按停前原路径 `/nas_train/openbmb/Ultra-FineWeb/...` 续传 —— 属既有例外，如实记**）。
- **看护（沿用常驻口径）**：**失败 / 僵死 / 速率趋零 / PID 已死 ⇒ 立即 kill + restart**，心跳标「已重启」+ 新 PID（不必等运维点名）。

**③ 恢复基线（停前值 · 供续传核对）**：
| 路 | 停前进度 | 落盘路径 |
|:--|:--|:--|
| `en_v1_4` | 32,995 / 56,461 parquet ≈ **58.4%**（3.0T） | `/nas_train/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4/` |
| `WebMix-38M` | 78 parquet / 59G（+1 `.incomplete`） | `/nas_user`（datasets） |
| `wit_base` | 79 parquet / 70G（+1 `.incomplete`） | `/nas_user`（datasets） |
| `InternVL-SA1B` | 303 tar / 227G（+1 `.incomplete`） | `/nas_user`（datasets） |

**④ 心跳 / 回写**：4 路状态改 `▶️ 下载中（2026-10-14 恢复）` + 各自**新 PID / 速率 / 进度 / ETA**；`MEMORY_DATA.md`（进度快照 + 流水）+ `daily-memories-data/2026-10-14.md`；commit 前缀 `data dl:`。

**⑤ 纪律**：🚫 不删任何已有数据；**GPIC ✅ / the_cauldron ✅ 不动**；**85M 不动（维持暂停）**；**错峰 IO**（避开 `.29` pretrain / `.12` vision 训练）；任务书 >32KB 自滚归档。


> 📦 §运维指令·2026-10-14（⏸ 暂停全部 4 路下载）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：已被同日「▶️ 恢复」块取代；4 路均已恢复并陆续下满（WebMix/wit_base/InternVL-SA1B✅），en_v1_4 仍在下载。需要时再读。

## 运维指令 · 2026-10-14（💾 新增下载落盘位置 `/nas_env`）· 用户直令 · 常驻

(2026-10-18 运维自 BAIZE_DATA_TASK.md 原文搬入，未改一字)



> **用户令（2026-10-14）**：「告知 data，以后数据也可以下载到 `/nas_env`，目录仍然是 `app.e0031982/datasets`。」

**① 新增可落盘位置（常驻，与现有并列）**：`/nas_env/app.e0031982/datasets/`。落盘路径形式仍是 `<盘>/app.e0031982/datasets/<publisher>/<name>/`。

**② 现有落盘位置白名单（更新后）**：
- ✅ `/nas_inference/app.e0031982/datasets/`
- ✅ `/nas_user/<用户>/datasets/`（或 `/nas_user/app.e0031982/datasets/`）
- ✅ **`/nas_env/app.e0031982/datasets/`（新增）**
- 🚫 `/nas_train` 仍不放（已 ~85%）。

**③ 纪律（不变）**：下载前 `df -h` 确认目标盘已挂载 + 剩余空间 ≥ 预计总量；`setsid` 守护 + 断点续传；纳入「死/僵/速率趋零即 kill+restart」看护；实际落盘路径写进心跳；commit 前缀 `data dl:`；任务书 >32KB 自滚归档。

---

## ⏸️ 运维指令 · 2026-10-20（🔴 暂停 en_v1_4 数据下载）· 用户直令 · 最高优先 · 覆盖旧「下载口径」

(2026-10-21 data agent 自 BAIZE_DATA_TASK.md 原文搬入，未改一字；已被同日 15:5x「✅ 恢复下载」块覆盖/取代)

> **用户原话**：「让 data 暂停数据下载」。
>
> **动作（本轮唤醒立即执行）**：
> 1. **kill 下载进程**：停掉 en_v1_4 下载 —— `download_en_v1_4.py` / `download_en_v1_4_resolve.py`（当前 PID 2732959，resolve.py）及其子进程。**只杀下载，不动分词**。
> 2. **保留分词进程**：`run_tokenize_env14_fullsource.sh`（PID 749330）及其 `preprocess_data_cm` 子进程**继续跑**，把已下载的 shard 分完（**不暂停分词**）。
> 3. **保持暂停**：🚫 **覆盖**旧「下载口径（失败/僵死/速率趋零就 kill+重启）」—— 本轮起**下载保持暂停**，agent **不得重启下载**，直到收到新的「恢复 en_v1_4 下载」指令。
> 4. **记录暂停位置**：在 `MEMORY_DATA.md` 进度快照 + `DATA_LEDGER.md` 记下暂停点（当前 sh94 / 总 parquet 数 / 已下载 dir 数），便于将来续传。
>
> **报告**：本轮唤醒回报「下载已暂停」+ 暂停位置 + 分词仍进行的 done/110 快照。

---

### ▶️ 运维指令 · 2026-10-20 15:5x（✅ 恢复 en_v1_4 数据下载）· 用户直令 · 已执行

> 用户原话：「data: 可以恢复下载了」。
>
> **动作（本轮唤醒立即执行）**：
> 1. **重启下载**（从暂停点续传，脚本幂等、自动 SKIP 已完成文件）：
>    ```bash
>    cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
>    export HF_PROXY=http://172.19.92.23:13128 HF_ENDPOINT=https://hf-mirror.com
>    export https_proxy=$HF_PROXY http_proxy=$HF_PROXY
>    setsid -f nohup python3 download_en_v1_4_resolve.py > /tmp/en_v1_4_dl_dot23.log 2>&1 &
>    ```
>    （暂停点：**sh95(CC-MAIN-2024-10)@139/512**，95/110 dirs，48267 parquet）；续传从 sh95 起，sh96–110 尚未创建。
> 2. **恢复旧「下载口径」**（2026-10-07 起生效版）：下载**失败 / 僵死 / 速率趋零 / PID 已死就 kill+重启**，报告标「已重启」+ 新 PID，不必等运维点名。
> 3. **分词不受影响**：`run_tokenize_env14_fullsource.sh`（PID 749330）继续跑，下载续上的 shard 落盘后自动排队分词。
> 4. **报告**：报重启后 PID + 续传起点 + 实测 MB/s + 剩余 shard ETA；`DATA_LEDGER.md` 的 en_v1_4 行改回「🟢 下载中」。

> 📦 §⏸️运维指令·2026-10-20（暂停 en_v1_4 下载）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：已被同日 15:5x「✅恢复下载」块覆盖/取代；下载已恢复（PID1875054 alive,2.80MB/s）。需要时再读。

---

### 🆕 运维指令 · 2026-10-18 10:2x（🔧 **P0：恢复 git push（换代理疑似污染全局 proxy 环境）**）· 用户直令 · 与续传令并行

> **判断**：换 `.23` 代理过程中可能在 shell/服务里全局 export 了 `http_proxy/https_proxy/ALL_PROXY`，导致 `git push` 走不通（尤其远端是 HTTPS 时）。**下载用 HF 代理 ≠ git 走代理**。
> **要求**：
> 1. 先只读诊断：`git remote -v`、`git status -sb`、`env | grep -iE 'proxy|HF_'`、`git config --get-regexp '.*proxy'`、`ls .git/index.lock`。
> 2. `git` 一律**剥离 HF 代理**执行：`env -u http_proxy -u https_proxy -u ALL_PROXY -u all_proxy git fetch/pull/push origin main`；🚫 不要为 git 永久写 `git config --global http.proxy`。
> 3. 若远端是 SSH（`git@github.com:`），代理环境本不影响；若仍失败，贴 `GIT_SSH_COMMAND="ssh -v" git ls-remote origin HEAD` 原文。
> 4. 修好后**立刻执行同日②的续传令**（`.23+hf-mirror`，25 shard）+ 启分词；ops 中继会在恢复后执行 RUN_ID 123 的 `.12` git 只读诊断，可与中继结论互相印证。

---

### 🆕 运维指令 · 2026-10-18②（🔴 **P0：立即改用 `172.19.92.23:13128` + hf-mirror 续 `en_v1_4` 最后 25 个 shard**）· 用户直令 · 覆盖同日①的"先探针"

> **背景**：你已经连续多轮报 `.25` → `huggingface.co HTTP=000 timeout`，但 **`.23 + hf-mirror` 已由中继在 `.12`/`.29` 双机实测为 200**：
> `.23→hf-mirror` **200 / 0.33s**、`.23→hf-mirror API tree` **200 / 0.35–0.57s**（RUN_ID 122，2026-10-18 07:31）。⇒ **不要再等 `.25`**。
> 现状：**43,520 parquet / 0 incomplete / 4.1T / 85 of 110 shard 完成，只差 25 个**。

**① 立即执行（不再探针、不再等待）**
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
export HF_PROXY=http://172.19.92.23:13128
export HF_ENDPOINT=https://hf-mirror.com
export https_proxy=$HF_PROXY; export http_proxy=$HF_PROXY
export HF_HUB_ENABLE_HF_TRANSFER=1; export HF_HUB_DOWNLOAD_TIMEOUT=120
setsid -f nohup bash download_en_v1_4.sh > /tmp/en_v1_4_dl_dot23.log 2>&1
```
- ⚠️ **脚本已由运维改成读 `HF_PROXY`/`HF_ENDPOINT`**（原 L26-27 硬编码 `.25` 已移除）⇒ **必须先 `git pull`**，否则仍会走 `.25`。
- 若 `.sh` 的 API 列目录失败 ⇒ 改 `setsid -f nohup python3 download_en_v1_4.py > /tmp/en_v1_4_dl_dot23.log 2>&1`（24 workers 并行版）。
- **已完成的 85 个 shard 自动 SKIP，不要删、不要重下。**

**② 判活（10–15 min 内给结论，🚫 不看进程存活，只看字节增长）**
- `du -s` 目标目录两次（间隔 120s）必须增长；或 `/proc/<pid>/io` 的 `write_bytes` 增长；或日志出现新的 `downloading/DONE`。
- **零增长 ⇒ 判假活**：kill wrapper → 换 ① 的 Python 并行版 → 仍零增长则报 blocker（贴报错原文）。

**③ 回报（本轮就要）**
1. `.23 + hf-mirror` 下的实测：**MB/s**、已完成 shard 数（从 85 起算）、**25 个剩余 shard 的 ETA**（按实测速率算，禁止沿用旧 7–8 天口径）。
2. 日志路径 `/tmp/en_v1_4_dl_dot23.log` + `pgrep -af download_en_v1_4` 原文。
3. 完成后自校：`parquet` 数 vs HF 清单、`.incomplete==0`，写入 `DATA_LEDGER.md`。

**④ 紧接着（本令的第二优先，不阻塞 ①）**
- **en_v1_4 开始分词**（P-8/v5 的 S1 要 500B token）：复用 `preprocess_data.py` + `tokenizer_eod`，`nice -19`，并发 4–8；**先报预计 B tok/天 与到 500B 的天数**。
- 🚫 85M 维持暂停；🚫 不动 GPIC/WebMix/InternVL/wit_base/cauldron/SFT-2605/RL-2609；🚫 不改 `.12` 上 vision 正在用的 GPU 任务（vision P0 已占用 8 卡，分词只用 CPU）。


> **用户令（2026-10-18）**：「data: 既然 172.19.92.25:13128 返回503，那就尝试用 172.19.92.23:13128+hf-mirror 来续传」

**① 范围（只动 `en_v1_4` 一路）**
- 目标：`openbmb/Ultra-FineWeb · data/ultrafineweb_en_v1_4/`（56,461 文件 / 6.75TB），落盘 `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/` 不变。
- 现状（唤醒 522）：**43,520 parquet / 0 `.incomplete` / 4.1T / 85 of 110 snapshot 目录完成**；wrapper 已退出（03:59，`completed=14 skipped=71 failed=25`）⇒ **只需续 25 个失败 shard**，已有的 85 个目录自动 SKIP（🚫 不要删、不要重下）。
- 🚫 **不动**：85M（维持用户令 10-13 暂停）、GPIC、WebMix-38M、InternVL-SA1B、wit_base、the_cauldron、SFT-2605、RL-2609；不动 `.25` 上任何已完数据。

**② proxy 口径（本令覆盖 10-15「.12 下数据一律 .25 直连 hf.co」——仅限 `en_v1_4` 这一路）**
```bash
export HF_PROXY=http://172.19.92.23:13128     # ⚠️ 不是 .25
export HF_ENDPOINT=https://hf-mirror.com      # 92.23 恒配 hf-mirror（用户 10-15 口径）
export https_proxy="$HF_PROXY"; export http_proxy="$HF_PROXY"
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=1
```
- 若 `.23` 恢复后改用 `.25`：`HF_PROXY=http://172.19.92.25:13128` 且 **unset HF_ENDPOINT**（直连 hf.co）。
- ⚠️ **脚本已改（运维 2026-10-18 直接提交）**：`run/data_pipeline/download_en_v1_4.py` 原先在 **L26-27 硬编码 `.25`**、`.sh` 在 L11-12 硬编码 `.25` ⇒ **只 export 环境变量无效**。现两脚本均改为读 `HF_PROXY` / `HF_ENDPOINT`（未设时默认 `.23` + hf-mirror）。**先 `git pull` 拿到新版再起**；若你本地有未提交改动，以本令为准合并，别把硬编码 `.25` 带回来。

**③ 第一步：连通性探针（必须先做；单行命令，可直接复制到 `.12` 的 bash）**
```bash
curl -sS -m 20 -o /dev/null -w '.25 baseline -> hf.co: %{http_code} %{time_total}s\n' -x http://172.19.92.25:13128 https://huggingface.co
curl -sS -m 20 -o /dev/null -w '.23 -> hf-mirror: %{http_code} %{time_total}s\n' -x http://172.19.92.23:13128 https://hf-mirror.com
curl -sS -m 25 -o /dev/null -w '.23 -> hf-mirror API: %{http_code}\n' -x http://172.19.92.23:13128 https://hf-mirror.com/api/datasets/openbmb/Ultra-FineWeb/tree/main/data/ultrafineweb_en_v1_4
curl -sS -m 20 -o /dev/null -w '.23 -> 无 mirror: %{http_code}\n' -x http://172.19.92.23:13128 https://huggingface.co
```
- **过闸判据**：`.23→hf-mirror` 与 `.23→hf-mirror API` **都返回 200/3xx**。任一非 200/3xx ⇒ **不要把 wrapper 起满**，按 ④ 的 B/C 处理并回报原文。

**④ 起训（按探针结果选一条；同样单行，避免续行符被 Markdown 吞掉）**
```bash
# A 默认（探针全通）——脚本已改读 HF_PROXY/HF_ENDPOINT，默认即 .23 + hf-mirror
export HF_PROXY=http://172.19.92.23:13128; export HF_ENDPOINT=https://hf-mirror.com; setsid -f nohup bash download_en_v1_4.sh > /tmp/en_v1_4_dl_dot23.log 2>&1
# B `.23` 通但 hf download 列目录失败——改 Python 并行版（24 workers，per-snapshot 非递归 listing）
export HF_PROXY=http://172.19.92.23:13128; export HF_ENDPOINT=https://hf-mirror.com; setsid -f nohup python3 download_en_v1_4.py > /tmp/en_v1_4_dl_dot23.log 2>&1
```
- 日志用**新文件名** `en_v1_4_dl_dot23.log`，保留旧 `en_v1_4_dl.log` 作证据；起 wrapper 前确认 `pgrep -af download_en_v1_4` 无残留旧进程。
- **C（`.23` 也不通）**：**不许空转重试**——停手，把探针四条原文 + `.25` 恢复时的重启用命令写进心跳，报 blocker 等运维。

**⑤ 保活 / 判活（10–15 min 内必须给一次结论）**
- 进程：`pgrep -af 'download_en_v1_4'`（应见 wrapper PID + hf/python 子进程）。

---

## §运维指令 · 2026-10-24 16:1x（**写一份"正在做的迁移"报告**）· 用户直令 · 最高优先

> 📦 **归档于 2026-10-24 18:1x（运维滚动，原文未改）**。闭合依据：`reports/report_data_migration_nas_env_zh.html` 已交付（唤醒 637@17:39，200 行/18KB/9 节），并经 wake 636 复核。

### 📄 运维指令 · 2026-10-24 16:1x（**写一份"正在做的迁移"报告**）· 用户直令 · 最高优先

> 用户原话：「data：**正在做的是什么样的迁移，写个报告。**」

**① 交付物**：`reports/report_data_migration_nas_env_zh.html`（自包含单文件中文 HTML）

**② 报告必须回答的问题（逐条，缺一不可）**

1. **迁移的是什么、从哪到哪**：
   - 源：5 源全量分词产物（`data/full_*`）—— 列出**每个源的 shard 数 / token 数 / 字节数**
   - 目标：`/nas_env/...` 的**确切绝对路径**
   - 总量：5 源合计（已知约 **4.24 TB**）

2. **为什么要迁**（背景与约束）：
   - `/nas_train` 使用率现状 vs `/nas_env` 余量（贴 `df -h` 实测）
   - **关键约束**：硬盘实测清单 19.14TB / 4778.41B tokens / 794 shards / 2383 文件 —— 而 `/nas_env` 只有 **10.51TB**，**放不下全量 21.05TB，只够 5 源 4.67TB**
   - **所以"迁移"做的是"5 源分词产物"，不是全部数据** —— 报告要把这个口径写清楚，避免误解

3. **迁移怎么做**（方法学，要可复现）：
   - 用 `rsync`（**为什么不用 mv**：跨挂载 mv = 复制+删除，中断两边都不完整）
   - **顺序**：`math_l3 → code_l3 → math_l1 → ufw_l3 → code_l2`（为什么是这个顺序？说明依据，如大小/重要性）
   - 是否保留目录结构、是否可断点续传

4. **校验方案**（**最关键，审稿/运维都看这个**）：
   - 每源迁完如何校验：**shard 数一致 + 总字节数一致 + `.idx` 可读性抽检**
   - 校验通过后如何切换：`mv 原目录 原目录.orig` + `ln -s 新路径 原目录`（**软链接保证 pretrain 的旧路径仍可用**）
   - **原目录先不删**（保留回滚能力），何时删

5. **当前进度与 ETA**：
   - 当前：`math_l3 55/67 .bin`（82%，237G/292G），rsync PID 112559
   - 每源耗时实测 + 剩余 4 源的 ETA
   - 总 ETA

6. **风险与应对**：
   - NFS 带宽争用（同时有 85M 下载在跑）→ 是否影响迁移速度
   - 磁盘写满风险（`/nas_env` 10.51TB vs 5 源 4.67TB，余 5.84TB 缓冲，够）
   - 中断恢复（rsync 重跑幂等）

7. **迁移完成后谁用、怎么用**：
   - pretrain 全量预训练（**等 data 就绪**）
   - 软链接路径不变 → **pretrain 脚本无需改动**

**③ 顺带说明**：报告里要有一小节 **"与 85M 下载的关系"** —— 85M 现在 8703/12124（71.8%），走 **92.25 + hf.co 直连**，落在 `/nas_train`（不是 `/nas_env`，因为 9.6T < 15.2T 剩余）。**这两件事是并行的，不冲突。**

**④ 纪律**：只写报告，**不打断正在跑的 rsync**；数据可溯源（贴 `df`、`du -sb`、`ls | wc -l` 的真实输出）。

- **真推进（硬判据，🚫 不看进程存活）**：日志里出现 `[n/110] CC-MAIN-XXXX: downloading/DONE` **且** 目标目录 `du` 或 `/proc/<hf-pid>/io write_bytes` **在 120s 内增长**；或 `.incomplete` 字节增长。
- 若 10 min 内 0 字节增长 ⇒ 视为假活：kill 该 wrapper → 换 ④-B 或 ④-C。

**⑥ 回报（这一轮就要）**
1. 探针 4 行原文（`.25` / `.23→mirror` / `.23→mirror API` / `.23→无 mirror`）。
2. 用的哪条路径（A/B/C）+ wrapper PID + 日志路径 + 实际 `HF_PROXY` / `HF_ENDPOINT` 值。
3. 25 个待续 shard 名单（从旧日志 `failed` 行取），完成后逐 shard 的 parquet 计数。
4. **速率 + ETA**：先报 **MB/s（或 files/min）实测**，再给「25 shard 剩余 GB ÷ 速率」的 ETA；不许沿用旧的 7–8 天口径。
5. 完成后自校：`parquet` 计数 vs HF 清单、`.incomplete == 0`，写入 `DATA_LEDGER.md`。
6. 写 `MEMORY_DATA.md` 进度快照（PHASE/当前动作/下一步/阻塞 四行必须提到「`.23`+hf-mirror」）+ `daily-memories-data/2026-10-18.md`；commit 前缀 `data dl:`。

**⑦ 纪律**
- 只在这条线上换 proxy；**别线（vision 的 HF 评测、harness 安装包、git push）仍按 `run/ops/README.md §7` 口径**，🚫 不要顺手改全局 `~/.bashrc` / `git config`。
- `git pull --rebase --autostash` 后如遇 `.25` 与 `.23` 记录冲突：**保留双方**（两条探针结果都要留档）。
- 任务书 >32KB 自滚归档（只搬已闭合块原文 + 1 行指针）。


---

## §运维指令·2026-10-21 04:0x（MiniCPM5 全量数据完整分词 · 224 核全开）· 已归档 2026-10-24
> 结论：5 个源（Code L3/L2, Math L3/L1, UFW-L3）全部分词完成，共 574 shards / 1056.36B tokens / 4.24TB。env14 全源分词也已完成（110/110, 2238.14B）。迁移到 /nas_env 进行中。

### 🔥 运维指令 · 2026-10-21 04:0x（**MiniCPM5 全量数据完整分词 · 224 核全开**）· 用户直令 · 最高优先

> 用户原话：「那就完整分词啊，交代给 data，CPU核有224个，把已经下载的 MiniCPM5 的数据，完整分词！！」
> **背景（decay v2 差 20pp 的核心数据侧根因）**：UltraData-Code **411B token 全量仍未分词**，decay 只用了 `anneal_code` 90M + r3 小样本 140M = **0.23B**，导致 **code 被重复 26 个 epoch**；UltraData-Math（303B）同样只有 ~1B 小样本。**这不是配比问题，是"有数据没用"的问题。**

**① 任务：把下列「已下载但未分词」的数据源做完整分词（不做小样本、不切 mix）**

| 数据源 | 路径 | 规模 | 现状 | 目标产物 |
|:--|:--|--:|:--|:--|
| **UltraData-Code L3** | `/nas_inference/.../openbmb/UltraData-Code/data/UltraData-Code-L3/` | **56B tok** | ❌ 未分词 | `data/full_ultradata_code_l3/…` |
| **UltraData-Code L2** | 同上 `L2/` | **355B tok** | ❌ 未分词 | `data/full_ultradata_code_l2/…` |
| **UltraData-Math L3** | `/nas_inference/.../openbmb/UltraData-Math/data/UltraData-Math-L3/` | **87B tok** | ❌ 未分词 | `data/full_ultradata_math_l3/…` |
| **UltraData-Math L1** | 同上 `L1/` | **184B tok** | ❌ 未分词 | `data/full_ultradata_math_l1/…` |
| **Ultra-FineWeb-L3** | `/nas_inference/.../openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | **690B tok** | 部分（仅 p5b_l3 20.56B） | `data/full_ufw_l3/…` |

> ⚠️ **优先级**：**Code L3 → Math L3 → Code L2 → UFW-L3 → Math L1**。理由：decay 20B 实验只需 code 1.6B / math 0.8B，**L3 层 56B+87B 足以支撑，且 L3 是最高质量层，decay 本就该用 L3**。先把 L3 两批分完，**20B decay 实验即可解除数据阻塞**。

**② 并发：用满 224 核**

- 现 en_v1_4 全源分词只用了 **32 workers（throttle@32）**，`nproc`=224 ⇒ **绝大部分 CPU 闲置**。
- 新任务要求：
  - **按 CPU 核数自动定并发**：`NPROC=$(nproc)`；分词进程 **≤ NPROC × 0.85**（留余量给 I/O 与 en_v1_4 现有 worker），即 **~190 并发**。
  - 建议先用 **64 并发做 5 分钟测速**（tok/s、MB/s、CPU 利用率、内存），再按线性外推拉到 **160~190**。
  - `nice -n 10`（不抢 en_v1_4 已有 worker 的交互）。
  - **内存/IO 是真实瓶颈**：每进程读 parquet 解压需内存，先确认 `free -g` 剩余足够（每并发约 1~2GB），不够就按 `可用内存/2GB` 定并发，**不要盲目拉满导致 OOM**。

**③ 产出规范（必须与现有 decay 脚本兼容）**
- 输出 **Megatron `.bin` + `.idx`**（int32）到 `data/full_*` 目录，命名 `<src>_train_s{0..N}` 分片（与 `baize_xmodel25_decay_v2.py:472` 的 `sources.append` 格式一致，便于直接改数据源）。
- tokenizer：**Xmodel-2.5 原生 tokenizer**（vocab 129280，`/nas_train/app.e0031982/models/...`），避免 vocab 不兼容。
- **入库登记**：每完成一个源，把「源 / 路径 / 实际 token 数 / shard 数 / 耗时」写入 `DATA_LEDGER.md` + `MEMORY_DATA.md`。

**④ 与 en_v1_4 的关系**
- en_v1_4 下载（PID1875054）+ 全源分词（PID749330）**继续跑，不要 kill**。
- 新增分词进程**共用机器**，但要 `nice` 降权；若出现 IO 打满导致 en_v1_4 速率跌破 1MB/s，**降低新任务并发**，不要停下载。

**⑤ 回报**
- 每轮写：`源 / 已完成 shard / 累计 token / 并发数 / tok/s / CPU 与内存占用 / ETA`。
- **全部 L3 完成后立刻报**（这是 pretrain 20B decay 实验的解锁条件）。


### 🔴 运维指令 · 2026-10-24 08:4x（**用户质询：分词为何只用 5 worker（224 核闲置）+ 85M 是否走 92.25/hf.co 直连**）· 用户直令 · 最高优先

> 用户原话：「data：分词为什么使用这么少的work，这台服务器不是有224个CPU核吗？85M 下载是否使用了 92.25+hf.co 直连？」
> **运维实测**：① en_v1_4 分词仅 **5 workers**、1.19MB/s、系统 **load 26/224**（CPU 几乎闲置）；② 85M 下载已 8.7 小时仅 +20 parquet（8588/12124=70.8%），**推算 ~10MB/s、剩余 16TB 需 ~18 天**。

**① 立即回答两个问题（必须先取证，不许猜）**
1. **分词为何只有 5 worker**：读 `fullsource`（PID 2557971）的启动命令与其脚本里的并发参数（`MAX_CONCURRENT` / `-j` / `nproc`），说明是「脚本硬编码小值」还是「剩余 shard 少导致自然降并发」。**贴出命令行原文**。
2. **85M 下载走的哪条线**：从 `PID 171042` 的 `/proc/<pid>/environ` 读 `https_proxy / http_proxy / HF_ENDPOINT`，**贴原文**，明确回答「是不是 92.25 + hf.co 直连」。若不是，说明现在走的是什么。

**② 提速（先测后放，防 OOM/IO 打满）**
1. **en_v1_4 分词提到高并发**：剩余 5 个 shard 若各自单进程，则**对每个 shard 内部并行**（或按 shard 内 parquet 分片并发）。目标 **≥64 并发**（可先 32 测 5 分钟再拉到 64-128），`nice -n 10`，**先查 `free -g` 按 每并发 1-2GB 兜底**。目标：把 ETA 从 22:30 压到 **3-4 小时内**。
2. **85M 下载按 2026-10-15 用户令切换线路**：
   - **`http://172.19.92.25:13128` → 直连 hf.co（🚫 不设 HF_ENDPOINT）**
   - 若当前用的是 92.23+hf-mirror，**改配置后重启下载进程**（幂等续传）
   - 若已是 92.25 但速度仍 ~10MB/s → **多线程/多进程并发下载**（HF 单连接常被限速，用 `hf_transfer` 或 4-8 并发 range）
3. **切换前必须做 60 秒测速对比**（92.23+hf-mirror vs 92.25+hf.co 直连 vs 多并发），**贴实测 MB/s**，择优。

**③ 纪律**
- 🚫 不 kill 正在写盘的分词进程（先确认可续传再重启）
- ✅ 提速后必须贴：并发数 / 实测 MB/s / CPU 占用 / 内存
- ✅ 两个问题的答案 + 提速结果写进 `MEMORY_DATA.md`

## 归档 2026-10-26（由 BAIZE_DATA_TASK.md 搬入，原文未改 · 唤醒673轻归档）

### [运维令] 2026-10-25 22:3x（分词停顿 2.6h：37 进程活着但 0 产出，先诊断再动）· 用户直令 · 最高优先
> 事实（RUN_ID 210 实测 22:00）：`done=94/131` 自 19:21 起未变；`tokens=150,155,374,778` 与 `bin_bytes=600,621,499,112` 与 19:21 **完全相同**；`preprocess=37`；ETA 由 7,688s 涨到 11,369s ⇒ 不是慢，是**停**。
> 1) **先诊断（15 分钟内）**：`ps -eo pid,etimes,pcpu,stat,args | grep '[p]reprocess_data'`（看 CPU 与 D 状态）；对 2-3 个 PID `py-spy dump --pid` 或 `cat /proc/<pid>/stack`；`nfsstat -c` / `dmesg | tail` / `df -h`；确认 37 个进程是否卡在同一 parquet 或同一 NFS 句柄。
> 2) **按类处置**（不许直接全杀）：① NFS/IO 阻塞 ⇒ 留证据，重启这些 shard（保留已完成 `.bin/.idx/.json`）；② BPE/进程死锁 ⇒ 照 2026-10-22 的 BPE 死循环处理：杀卡住的 PID、清半成品 `.bin`、supervisor 重排；③ 计数器坏了但仍在写 ⇒ 用 `du -sb` + 文件 mtime 证明，修 supervisor 计数。
> 3) 恢复后每 30 分钟记一次 `done` 与 `bin_bytes`，**连续两次相同才算真停**。
> 4) 完成后仍按 18:5x 令刷 `DATA_MAPPING.md` 第 7-10 行为 `镜像完整`、重跑 `build_tokenized_mirror.py` 与 triplet/inode 校验。
> 5) 报回：卡在哪个 shard、哪类原因、处置动作、恢复后 done 速率与 ETA。

### [运维令] 2026-10-25 18:2x（32 个「不可映射」分词 shard：**全部删除**，删前留档）· 用户直令 · 最高优先 · 覆盖 18:1x 块
> 用户原话：「我难道说的还不清楚吗？不明来历的，无法被DATA_MAPPING.md收录的数据，也就无法使用，那放在那里占用磁盘空间干什么？你出这个硬盘吗？」
> 前提（用户 18:3x 明确）：**这是 MiniCPM5 的训练数据管线** —— **下载的数据（parquet / 下载目录 / env14 / full_*）一律保留**；要删的只有 data 线**自己分词、且来历理不清**的那批产物（即下面这 32 个「不可映射」shard）。
> 结论：**这 32 个（l3_s 28 个 + math_s 4 个）全部删除**，不再讨论「是否唯一」。用户口径 = **不能被 DATA_MAPPING.md 收录的数据即不可用，留着只占磁盘**。
> 规模（已实测）：472.85B tokens，约 1.89 TB（按 4 B/token），涉及 1286 个 parquet 引用，全部是 l3_s / math_s 的 `staging_r3` 早期中间产物。

**1) 删前留档（唯一强制动作，10 分钟做完，先 commit 再删）**
- 对 32 个目录逐个记录：目录路径、`du -sb` 字节、`find -type f | wc -l` 文件数、`.bin/.idx/.json` 三件套清单、`.json` 里的 parquet 引用（若有）。
- 落 `run/data/deleted_unmapped32_20261025.tsv`（32 行明细）+ `run/data/deleted_unmapped32_summary.md`（总计字节 / TB / 文件数 / 一句结论）。
- 留档只为追溯「删了什么、多大、从哪来」，**不是保留理由**。

**2) 执行删除（直接删，不搬家、不挂账）**
- 对象 = judgment TSV 里 action 以「保留」开头的 32 行：`l3_s0`-`l3_s12`、`l3_s25`-`l3_s39`、`math_s32`-`math_s35`，位于 `/nas_train/app.e0031982/datasets/baize-data/text/`。
- 删前抽查 3 个是否被 `tokenized/` 镜像 hardlink 引用（`find tokenized -samefile <path>`）；有引用就先解除再删，避免镜像里留悬空链接。
- 删完立刻 `du -sb` 复核释放量，并记录 `df -h /nas_train` 前后对比。

**3) 收尾（必须同步，缺一不可）**
- `DATA_MAPPING.md`：新增「已删除 / 不可用」节，32 行状态置 `已删除`（附删前字节、删除时间、指向 `deleted_unmapped32_20261025.tsv`），**正文映射表里不再出现**。
- `tokenized/INDEX.tsv` + `DATA_LEDGER.md` 同步；重跑 `build_tokenized_mirror.py` 与 triplet/inode 校验，确认无悬空链接（在跑的 131 分词可先不打断，收尾校验等它结束后一并做）。
- 报回：`删除 32 个 / 释放 X TB / 文件数 Y / 磁盘前后`，一句话结论 + 表。

**铁律**
- 前提：**MiniCPM5 训练数据，下载的一律保留**；只删 data 线自己分词、来历理不清的 32 个产物。
- 只删**分词产物**；下载 parquet / 下载目录 / env14 / full_* 原样保留，不许碰（它们是训练数据本体）。
- 不许把这 32 个再挪进「待裁决」或再挂账：**本令为终裁，删完即结案**。
- 个别目录删不掉（权限/占用）⇒ 如实报出路径与原因，不许静默跳过。

### ⏱ 本轮执行顺序（2026-10-25 12:5x 用户直令 · **覆盖此前所有令**）
> 用户原话：「1. 已下载已分词的，把分词目录整理一下，跟下载目录有更好的对应。2. 已下载未分词的，去分词，充分利用多核并发。」
> 已删 32 个不可对应 shard（1.91 TiB，RUN 199）；报告已由运维改为**单表**（8.5 KB / 1 table / 14 行），**结构不许改**。

#### ⓪ 报告复核 · **已完成并验收**
> data 于 12:41 重生成（10,520 B / 1 table / 每行附 `du -sb` 命令 / 结构未变），运维 13:19 验收通过。若 `run/data/report_verify_20261025.md` 还没落，随下次提交补上（只补实测值与命令，不补论断）；🚫 不得再改报告结构。

#### ① 已分词产物：整理成「镜像下载目录」的布局（**零拷贝**）

新根：`/nas_train/app.e0031982/datasets/baize-data/tokenized/`，**路径镜像 HF 下载目录**：

| 新目录（= 镜像下载路径） | 现有产物来源 | 建法 |
|---|---|---|
| `tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4/` | `baize-data/text/env14_*.{bin,idx,json}`（110 组） | 同盘 ⇒ **hardlink**（同 inode、0 额外空间、旧路径继续可用） |
| `tokenized/Ultra-FineWeb-L3/ultrafineweb_en_l3/qa/` | `/nas_env/…/full_ufw_l3`（154 组） | 跨盘 ⇒ **symlink**（**禁止 cp**，4.24 TB） |
| `tokenized/UltraData-Code/UltraData-Code-L2/` | `/nas_env/…/full_ultradata_code_l2`（141） | symlink |
| `tokenized/UltraData-Code/UltraData-Code-L3/` | `/nas_env/…/full_ultradata_code_l3`（63） | symlink |
| `tokenized/UltraData-Math/UltraData-Math-L1/` | `/nas_env/…/full_ultradata_math_l1`（149） | symlink |
| `tokenized/UltraData-Math/UltraData-Math-L3/` | `/nas_env/…/full_ultradata_math_l3`（67） | symlink |

硬性规则：
1. **只许 hardlink（同盘）/ symlink（跨盘）**；🚫 `cp`、🚫 `mv`、🚫 `rm` 任何已有 `.bin/.idx/.json`。目的是"整理视图"，不是搬数据。
2. 每个新目录写 `MANIFEST.json`：`{download_dir(绝对), hf_repo, subdir, shards:[...], tokens_total, bytes_total, tokenizer, storage:"hardlink|symlink", created}`。
3. 顶层 `tokenized/INDEX.tsv`：`tokenized_dir | download_dir | shards | tokens | bytes | tokenizer | storage`；数字用脚本统计（`ls *.bin` / `du -sb` / `.json num_tokens` 求和），禁手填。
4. 之后**校验**：每目录 `bin == idx == json 三件套齐全`、hardlink 用 `stat -c %i` 比 inode 相同、`num_tokens` 可解析。
5. 完成后把 `run/data/map_dl_vs_tok_20261025.tsv` 的 `tok_dir` 列改成新路径，重跑 `python run/data/gen_tokenized_inventory_report.py`（已是单表模式），报告表里的「分词产物目录」必须是新布局。

#### ② 已下载未分词：**现在就分词，把 224 核用起来**

未分词 4 源（实测：**12,002 parquet / 3,532.21 GB**）：

| 下载目录 | parquet | GB | 目标前缀 | 输出目录（新布局） |
|---|---:|---:|---|---|
| `…/openbmb/Ultra-FineWeb/data/ultrafineweb_en` | 2,048 | 2661.36 | `ufw_en_s*` | `tokenized/Ultra-FineWeb/ultrafineweb_en/` |
| `…/openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq` | 6,000 | 477.98 | `ufw_l1hq_s*` | `tokenized/Ultra-FineWeb/ultrafineweb_l1_en_hq/` |
| `…/openbmb/Ultra-FineWeb/data/ultrafineweb_zh` | 256 | 324.32 | `ufw_zh_s*` | `tokenized/Ultra-FineWeb/ultrafineweb_zh/` |
| `…/openbmb/UltraX-Preview/data/UltraX-AICC` | 61 | 68.55 | `ultrax_aicc_s*` | `tokenized/UltraX-Preview/UltraX-AICC/` |

- **并发标定（必须做，别拍脑袋）**：`96 / 144 / 192 / 224` 四档各 60s，记 tokens/s、CPU%、load、NFS 写速；取 **tokens/s 拐点**，`workers = min(拐点, 200)`（留 4–8 核给系统与 85M 下载）；`nice -n 5`。标定表必须贴进回报。
- 分词器沿用 `tokenizer_eod`（vocab 129,281 / pad 129,408），链路 `preprocess_data.py` 不变；shard 目标 ~64–80 GB/片；每片写 manifest（shard → 源 parquet 列表）。
- `setsid` 后台跑，日志 `/tmp/tokenize_untokenized_*.log`；断点续传（已有三件套跳过）；失败重试 2 次后落 `failed_shards.txt`。
- **边分边报**：每 30 分钟 `done/total`、tokens/s、CPU%/load、写速、ETA、失败数；全部完成后校验 `.bin=.idx`、字节、`num_tokens`，再更新 `DATA_LEDGER.md §9` + 重生成报告 + `INDEX.tsv`。

> 🚫 不许 `cp` 已有 4.24 TB 产物；🚫 不许 `mv`/`rm` 已有分词文件；🚫 `env14_*` 原件与 `/nas_env/full_*`：不删/不改/不移/不复制（**建 hardlink/symlink 允许**，见顶部仲裁表）。
> 🚫 报告结构不许改（已经是单表）；只需按新路径重生成。
> 🚫 不许用「未实测/N/A/—」；未跑完不许称「已就绪」。
> 顺序：**① 先做（分钟级：链接 + INDEX），② 立刻开跑**；② 未启动前不得睡。


---

## 归档 · 2026-10-25 17:5x 运维令（已完成）

### [运维令] 2026-10-25 17:5x（**目录名不再重要：核心交付 = 「下载与分词」映射表；Markdown 为单一事实源，HTML 按需**）· 用户直令 · 最高优先
> 用户原话：「data：目录不重要，分词后可以改目录名字。关键是维护好映射表，这个映射表可以是markdown，需要时转HTML给运维报告。」
> 本条 + 下方「口径仲裁」新增的三行，优先于 13:2x 块里关于报告结构 / 目录命名 / uncovered shard 的旧口径。

**1) 在跑的不要停**
分词继续跑（131 目标，17:23 为 done=92/131）直到 `done=131/131`，然后：新 shard re-link 进 `tokenized/`（同盘 hardlink / 跨盘 symlink），再校验 `.bin == .idx == .json` 三元组 + 字节 + `num_tokens` 可解析，最后更新映射表。

**2) 唯一硬交付：`run/data/DATA_MAPPING.md`（Markdown 单一事实源）**
- 一行 = 一个下载目录（粒度以盘上 `ls` 实测为准；不自造源、不合并目录凑行）。
- 列固定：`# | 下载目录 | 分词目录 | .bin | .idx | .json | 字节(B) | GB | tokens(B) | 状态 | 校验时间 | 证据`
- `状态` 只取：`镜像完整` / `分词中` / `未分词` / `未映射` / `已废弃`。
- **合计行由脚本求和**，不许手填；表尾附核对式（各列求和 = 合计，误差 0）。
- 每行「证据」写实测命令（`du -sb` / `find | wc -l` / `wc -l`），或在附录统一给命令清单 + 输出摘要。
- **允许改目录名**：改名必须与映射表**同一批提交**同步更新；改完跑一次 triplet + inode 校验，结果写回「校验时间」。禁出现「表里路径不存在 / 盘上目录没登记」。
- 生成器：`run/data/gen_data_mapping_md.py`（读实测 TSV + `du`，输出 md + 合计 + 核对式；重跑幂等）。

**3) 32 个未映射 shard 不再阻塞**
- 在映射表单列「未映射 / 来源不明」一节，逐条写：路径、字节、能否追到下载目录、建议（保留 / 待删 / 补下载）。
- **未经用户批准不许删除任何数据**；只标注与建议。

**4) HTML 报告按需**
- 需要给运维 / 用户看时，再用 `run/data/gen_tokenized_inventory_report.py` 从映射表生成 `reports/report_data_tokenized_inventory_zh.html`（单表结构不变）。
- 不要为报告反复重写结构；**md 更新才是主线**，HTML 只是渲染。

**5) 收尾**
`MEMORY_DATA.md` 首部新块 + `run/daily-memories-data/2026-10-25.md`；commit 前缀 `data mapping:`；`git status -sb` 无 ahead / behind。


---

## 归档 · 2026-10-25 18:5x 运维令（已完成）

### [运维令] 2026-10-25 18:5x（把 DATA_MAPPING.md 做成脚本生成的真·单一事实源 + 授权按测得分批清理磁盘）· 用户直令 · 最高优先
> 用户原话：「对于 data 来说，维护好 run/data/DATA_MAPPING.md 至关重要。可以适当清理一下硬盘，减少占用。」

**1) 映射表补齐（第一优先）**
- 补 `run/data/gen_data_mapping_md.py`（C 节现在写着「待补、首版手工建立」）：输入 = `tokenized/INDEX.tsv` + 盘上 `du -sb` / `find | wc -l` 实测 + 下载目录实测；输出 = A/B 两节 + 合计 + 核对式 + 「生成时间 / 驱动数据 / git 短 hash」。判据：**连跑两次 md 逐字节相同**（幂等）。
- A 节增两列：`下载目录字节(B)`、`下载/分词字节比`（同一行能核对「下载了多少，分出来多少」），其余 12 列保留；合计行仍由脚本求和。
- 分词跑完（判据 `done=131/131`）立即刷新：第 7-10 行 `分词中` 改 `镜像完整` 并补 bin/idx/json/字节/tokens；`INDEX.tsv`、`DATA_LEDGER` 对应节同批更新。
- 「证据」列要可复现：写具体命令（`du -sb <path>`、`ls <dir>/*.bin | wc -l`）或 INDEX 行号，禁只写「OK」。

**2) 磁盘清理（授权，但必须按实测分批）**
- 先出候选清单 `run/data/disk_cleanup_candidates_20261025.tsv`：路径 / 类型 / `du -sb` 表观字节 / 实占字节（硬链接只算一次）/ inode 链接数 / 是否被 `tokenized/` 引用 / 判定（可删 / 保留 / 待定）/ 理由；按**实占**降序。
- **可删（不必再请示）**：① `text/staging_r3/` 剩余 78 个纯输入符号链接暂存目录；② 分词崩溃残留（无 `.idx` 的孤儿 `.bin`、`.partial`、`.bak`）；③ 空目录；④ `/tmp` 下本线分词中间日志（保留最后 3 份）；⑤ 已被 `tokenized/` 收录且 inode 链接数 > 1 的重复副本（删前必须证明 `tokenized/` 侧仍可访问）。
- **不可删**：`/nas_env/full_*`（训练数据本体）、`tokenized/` 镜像与 `INDEX.tsv`、`DATA_LEDGER.md`、`/nas_inference` 下载 parquet、任何 `.json` manifest。下载数据一律保留（18:3x 已定）。
- **分批**：每批实占不超过 500 GB；每批前后各记 `df -h /nas_train` 与 `du -sb`；删后立即跑 triplet + inode 校验（镜像 `.bin` 数应恒为 716，悬空 = 0）。第一批做完报数，再决定是否继续。
- 报回：`候选 N 项 / 第一批删 M 项 / 实占释放 X GB / 表观体积 Y GB（差值 = 硬链接）/ 校验 OK` + 清单路径。**不许把表观体积当实际释放。**

**3) 收尾**
- `DATA_MAPPING.md` C 节加「清理记录」指针（批次 / 时间 / 释放 / manifest 路径）。
- `MEMORY_DATA.md` 首部新块 + `daily-memories-data/2026-10-25.md`；commit 前缀 `data mapping:` 或 `data cleanup:`；`git status -sb` 无 ahead / behind。
- HTML 报告按需（用户或运维要才生成），不为此表反复改报告结构。

> 📦 §运维令·2026-10-25 18:2x（删32不可映射shard）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：32个(l3_s28+math_s4)已全部删除(1.91TiB表观/实占~471.6KB)，删前留档deleted_unmapped32_20261025.tsv+summary.md，DATA_MAPPING.md B节标已删除，终裁结案。需要时再读。

> 📦 §运维令 2026-10-25 17:5x（DATA_MAPPING 为单一事实源 + 下载↔分词映射）**已完成**（18:5x 令交付脚本化生成器 `gen_data_mapping_md.py` 幂等 PASS，A 节 716 shard + B 节 32 已删）→ 原文归档 ARCHIVE_OPERATOR_DATA.md。

## 归档 2026-10-27（由 BAIZE_DATA_TASK.md 搬入，原文未改）

### [运维令] 2026-10-26 22:0x（**修复坏 shard：en_v1_4 / env14_CC-MAIN-2023-23 的 .idx 指针越界**）· 用户直令「安排 data 去处理」

> 用户原话：「坏 shard（env14_CC-MAIN-2023-23 idx 越界）安排 data 去处理吧」。
> **事实（来自 pretrain S1 实测，可复核）**：blender 报
> `SKIP env14_CC-MAIN-2023-23: ptr overflow: max_ptr=122,496,093,768 >= bin_size=49,025,167,172`
> ⇒ 该 shard 的 `.idx` 指针约为 `.bin` 的 **2.5 倍**，判定损坏；blender 已安全跳过（`validate_shards: 109 ok, 1 skipped, 110 total`，0.65 权重摊到 109 片），
> 但 `Ultra-FineWeb/ultrafineweb_en_v1_4` 实际少了 **1/110 片**（占比最大的一路）。

**要做（按序，先留证再动手）**
1. **定性**：`ls -l` 该 shard 的 `.bin/.idx` 实测字节；用 python 读 `.idx` 头与偏移，确认 `num_tokens` 与 `max_ptr`；判断是 **.bin 被截断** / **.idx 来自别的分片** / **分词中途写坏**。
   证据落 `run/data/bad_shard_env14_CC-MAIN-2023-23_20261026.txt`（含命令与原始输出）。
2. **修复优先级**：
   - (a) 若 `staging_r3` / `full_*` / 源 parquet 仍在 ⇒ **只重分词这一片**（估 ~49GB / ~12B token，先报 ETA 再跑）；
   - (b) 若 `.bin` 完整、仅 `.idx` 坏且 `preprocess_data.py` 支持重建索引 ⇒ 只重建 `.idx`；
   - (c) 都不行 ⇒ **正式标记剔除**，并在 `DATA_MAPPING.md` 写「状态=已废弃(损坏)」+ 影响（en_v1_4 少 1/110）。
3. **复验**：`max_ptr < bin_size` 且偏移单调；重跑 `blender` 校验不再出现 SKIP；结论写 `DATA_MAPPING.md` + `DATA_LEDGER §7`；commit `data fix:`。

**红线**
- 🚫 不许直接删 `.idx` 或截断 `.bin`（会破坏下载↔分词映射与训练）；改动前先 `cp` 留档或用 tsv 记录原始字节数。
- 🚫 不许为了让校验通过而改 blast 权重规则（权重必须仍 = 1.0）。

**体积**：本文件 ~33KB，请本轮顺手把已闭合块归档到 **≤32KB**（指针留 1 行）。

> **执行结论（唤醒677-679, 2026-10-27 02:0x）**：已修复 DONE。定性=.bin 被截断至 49GB（=期望122.5GB的40%），.idx 正确(max_ptr=122.5GB)但指向截断外。修复=从源 parquet(512文件)重分词→新.bin 118.23GB/29.56B token(max_ptr=118.23GB<bin=118.23GB 复验PASS)→原子替换→build_tokenized_mirror.py重建hardlink+INDEX.tsv 815shard→DATA_MAPPING.md+report+DATA_LEDGER §7.2全量更新→commit 1cfb5e7dd data fix:。env14 110/110全齐，blender 不再 SKIP。证据 run/data/bad_shard_env14_CC-MAIN-2023-23_20261026.txt §8-9。

---

### [运维令] 2026-10-26 14:4x（**SFT-2605/Agent-2609 加入映射表+报告；删报告第 4 节**）· 用户直令 · 最高优先

> 用户原话：① 把 `/nas_inference/app.e0031982/datasets/openbmb` 下 `UltraData-SFT-2605`、`UltraData-SFT-Agent-2609` 两份数据加入 `run/data/DATA_MAPPING.md` 和 `report_data_mapping_zh.html`；② 报告「4. 其余状态源（未分词/未映射/已删除/已废弃）」这节数据已删、没必要保留，删除该节。

**① 加入两份数据（先核查分词状态，再如实登记）**
- 源路径：`/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605/data/`（no_think + think）与 `/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609/data/`（Code_Agent/General_Agent/Search_Agent/Tool_Use）。
- 先查这两份是否已有分词产物（`.bin/.idx/.json`）：
  - **已分词未镜像** → 镜像进 `tokenized/` + 更新 `INDEX.tsv` + 重跑 `gen_data_mapping_md.py`，使 DATA_MAPPING.md 自动含这两份（状态=镜像完整，storage 如实）。
  - **未分词** → 在 DATA_MAPPING.md 以「未分词」状态如实登记（并标注，不伪造「已分词/镜像完整」）。
- 每份列出：下载目录 → 镜像路径（或「—」）→ shard 数 → tokens → 字节 → 状态，数字溯源。

**② 更新报告 `report_data_mapping_zh.html`**：加入这两份数据的行；**删除「4. 其余状态源（未分词/未映射/已删除/已废弃）」整节**（数据已删，节号顺延）。

**③ 提交**：`DATA_MAPPING.md` + 报告一起 commit + push（前缀 `data report:`），心跳报字节数变化。

> **执行结论（唤醒672, 2026-10-26 16:3x）**：已交付 DONE。①核查分词状态=两份均无 .bin/.idx/.json（仅 jsonl）→判定「未分词」（不伪造镜像完整）。②实测：SFT-2605=1504 jsonl/318,990,486,183 B（297 GB，no_think 855:Chinese-general50/Code300/IF20/Knowledge80/Math300/Multi-lang-Knowledge50/Multi-lang-Math55 + think 649:Chinese-general50/Code279/IF20/Knowledge50/Math250）；Agent-2609=50 jsonl/54,220,373,384 B（50 GB，Code_Agent7/General_Agent32/Search_Agent2/Tool_Use9）。③新建 `untokenized_sft_sources.tsv` + 改 `gen_data_mapping_md.py`（load_untokenized + --untokenized-tsv，A 节追加 2 行未分词，分词目录=—，下载字节计入合计）→ DATA_MAPPING.md 重生成 103 行/11,001 B（字节数变化 10,093→11,001 B，+908 B；合计 815 shards/4474.83 B/17.26 TB 分词产物/下载 13,021,192,793,759 B=12127 GB；未分词小计 2 源 1554 jsonl/373,210,859,567 B=347.6 GB；幂等 run1==run2=True）。④报告 report_data_mapping_zh.html 更新（字节数变化 25,112→20,434 B，−4,678 B；总览数据源 10→12 + 下载 12647.98→13021.19 GB；逐源列表加行 11(SFT-2605 未分词)+12(Agent-2609 未分词)+合计；删第 4 节「其余状态源」（32 已删除表+状态汇总），5→4 结论节号顺延，加 SFT 未分词说明；footer 更新）。⑤HTML 校验 tag 平衡。commit 86431cfb4 `data report:`。后续 1cfb5e7dd（坏 shard 修复）再次全量刷新报告，当前报告 20,882 B / 4 节。

