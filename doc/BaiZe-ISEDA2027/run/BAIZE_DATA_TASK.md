# BAIZE_DATA_TASK.md

> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_DATA.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。
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

> 📦 §运维指令·2026-10-24 16:1x（写"正在做的迁移"报告）**已闭合**（`reports/report_data_migration_nas_env_zh.html` 已交付，唤醒 637@17:39）→ 原文已归档 → `run/ARCHIVE_OPERATOR_DATA.md`。需要时再读。


> 📦 §运维指令·2026-10-24 08:4x（用户质询：分词5worker+85M线路）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：Q1=5worker因串行+剩余shard少(非硬编码),升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT);85M用parallel16+92.25续传。需要时再读。


> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

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

> 📦 §运维指令·2026-10-21 04:0x（MiniCPM5 全量数据完整分词·224核全开）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：5源全部分词完成（574 shards/1056.36B tokens/4.24TB），env14也完成（110/110/2238.14B/8.88TB）。迁移到/nas_env进行中。需要时再读。
> 📦 §运维指令·2026-10-20 15:5x（✅恢复en_v1_4下载）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：下载已恢复并运行中（PID1875054 alive,99/110dirs），kill+重启口径恢复，分词不受影响。需要时再读。

### 🆕 运维指令 · 2026-10-18 21:0x（🔴 分词口径纠正：不按 1.5T/500B 预算截断；要分就某个数据源全部分词）· 用户直令 · 最高优先 · 覆盖旧「到 500B」表述

> **用户原话**：「Data 分词我没有说按 1.5T 分，要分就某个数据源全部分词。」
> **纠正**：**1.5T / 500B 是 v5 训练取用量估算，不是分词目标、不是停止条件**；分词必须按**某个数据源全量**执行。
>
> **当前源 = `en_v1_4`**：对 `CC-MAIN-*` 全部 **110 个 snapshot 目录**逐 shard 分词，直到 **110/110** 都有 `.bin/.idx/.json`；**不要在第 8 个 shard、92.6B tok 或 500B tok 处停止/宣告完成**。
>
> **执行口径**：
> 1. 当前 `run_tokenize_env14_resume.sh`（PID 2446254）继续跑完已下载 shards；
> 2. 下载完成的 shard（512 parquet 且无 `.incomplete`）立即排队分词；
> 3. 下载未完成的 shard **不提前分词**，标 `PENDING_DOWNLOAD`；
> 4. 全部 110 shard 完成后产出 `env14_fullsource_manifest.tsv` + `env14_fullsource_summary.json`（每 shard tokens/bytes/status + 全源总 tokens），并写入 `DATA_LEDGER.md`；
> 5. 全源完成前，任何报告**不得**写「en_v1_4 分词完成」；
> 6. 当前 `run_tokenize_env14_resume.sh` 退出后，用 **`data_pipeline/run_tokenize_env14_fullsource.sh`** 接管（本次已新增）：自动扫描 110 个 shard、跳过 DONE/RUNNING、下载完成后自动补分，直到 **110/110**；启动：
>    `setsid -f nohup bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/run_tokenize_env14_fullsource.sh > /tmp/run_tokenize_env14_fullsource.log 2>&1 &`
>    （脚本内置等待 resume 退出，避免双 launcher；不要手工再起第二份）。
>
> **报告**：每次唤醒报 `done/110`、`tokens 累计`、`PENDING_DOWNLOAD`、`全源 ETA`。
>
> **并发（2026-10-18 21:0x 用户批准）**：分词可用 **32 或 64 核**。默认 **32**；按当前 8 workers ≈230B tok/day 线性外推：32 ≈ **2.5 天**、64 ≈ **1.3–1.5 天**（全源 2.31T；实际受 NFS/内存影响）。先以 32 起跑，10–15 分钟后看 `pgrep -c preprocess_data_cm`、`/proc/io`、NFS 延迟与 tok/s；若近似线性且内存充足，再升 64。
>
> **接管方式**：当前 `run_tokenize_env14_resume.sh`（PID 2446254）只是发射器；先 `kill 2446254`（**不要杀 8 个 `preprocess_data_cm.py` 子进程**），确认子进程仍 alive 后，立即：
> `MAX_CONCURRENT=32 setsid -f nohup bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/run_tokenize_env14_fullsource.sh > /tmp/run_tokenize_env14_fullsource.log 2>&1 &`
> 若 kill 把子进程也带走，等子进程退出后再启动；DONE shard 自动跳过，不会重复分词。
>
> 🚫 不为凑 500B/1.5T 跳 shard、不混源部分分词、不把训练取用量当分词上限。


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

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_DATA.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_DATA.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_DATA.md` 顶部进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-data/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建，不许攒着最后补）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md doc/BaiZe-ISEDA2027/run/DATA_LEDGER.md \
              doc/BaiZe-ISEDA2027/run/CONTAMINATION_CHECK.md doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md \
              doc/BaiZe-ISEDA2027/run/DATA_MIX_RECIPE.md doc/BaiZe-ISEDA2027/run/DISK_CLEANUP_INVENTORY.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-data doc/BaiZe-ISEDA2027/run/data_pipeline
   git commit -m "data <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已因此出过事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
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
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
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
