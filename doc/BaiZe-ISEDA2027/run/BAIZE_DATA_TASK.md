# BAIZE_DATA_TASK.md

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。


> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_DATA.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。
> 📦 §运维令·2026-10-24 18:1x（85M 降优先级 → 迁移提速）**已闭合**（迁移 5/5 源全 DONE，`migrate_to_nas_env_fast.sh` 已跑完）→ 原文归档 `run/ARCHIVE_OPERATOR_DATA.md`；**结论**：`--bwlimit` 50000→300000 KiB/s、新脚本带 `--partial`+`flock` 单实例锁、不得就地编辑在跑的脚本、不得起第二实例；85M 不再是任何前置条件。需要时再读。

> 📦 §运维指令·2026-10-24 16:1x（写"正在做的迁移"报告）**已闭合**（`reports/report_data_migration_nas_env_zh.html` 已交付，唤醒 637@17:39）→ 原文已归档 → `run/ARCHIVE_OPERATOR_DATA.md`。需要时再读。


> 📦 §运维指令·2026-10-24 08:4x（用户质询：分词5worker+85M线路）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：Q1=5worker因串行+剩余shard少(非硬编码),升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT);85M用parallel16+92.25续传。需要时再读。


> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### ⏱ 本轮执行顺序（2026-10-25 11:4x 用户直令 · 覆盖下文步骤顺序）
> 用户原话：「data 唤醒后，**先盘点**现有的 MiniCPM5 训练数据中**已下载且已分词**的数据，**删掉无法跟下载目录对应的分词数据**。」
1. **先盘点**：现有 MiniCPM5 训练数据里「**已下载** + **已分词**」清单（= 下条 11:0x 令的 表 A / 表 B），逐条贴实测证据。
2. **再删除**：把**无法与 HF 下载目录对应**的分词产物删掉（= 10:3x 令：逐 shard 判定 → 先落 `prune_unmapped_20261025.txt` → 再 `rm` → 报释放量）。
3. **最后分词**：对「已下载未分词」（表 C）按标定并发开跑（64/96/128/192 取拐点，**多开但不打满**，留余量给 85M 下载）。
> 🚫 顺序不得颠倒：**没做完 ①②，不许开 ③**。


### 🧵 运维令 · 2026-10-25 11:0x（**重新盘点三张表 → 对「已下载未分词」启动分词（多开并发，按标定取拐点）**）· 用户直令 · 最高优先
> 用户原话：「重新盘点，列出下载目录，以及对应的分词语料，已下载未分词的。让 data 去分词，服务器 CPU 224 核，可以设置适当并发。」
> ⚠️ 澄清：**224 核是机器的上限，不是要全部用满** —— 目标是「比上一轮（65 并发）**多开一些**」，并按标定取性价比拐点。

**① 盘点（三张表，全实测，禁估算）**
- **表 A · HF 下载目录白名单**：`ls -d` + `find -name '*.parquet' | wc -l` + `du -sb` + mtime，逐条给出「绝对路径 / 对应 HF repo / 子目录名 / parquet 数 / 字节」。判断"是 HF 下载目录"的依据 = 目录内是 HF repo 的 parquet 布局（贴 `ls` 输出）。
- **表 B · 分词产物 ↔ 下载目录 映射**：每个下载目录对应哪些 `.bin`（前缀 / shard 数 / tokens / 字节 / 产物路径 / 完成时间）。**只认能对上 A 表目录的产物**。
- **表 C · 已下载未分词**：A 中有 parquet 但 B 无产物的部分 —— 逐目录给 repo/子目录/parquet 数/字节 + 「未分词」判定依据（无 `.bin`，或 shard 数与 parquet 分组数不符）。

**② 分词启动（只处理表 C，不重跑已完成的）**
- 分词器沿用 `tokenizer_eod`（vocab 129,281 / pad 129,408），`preprocess_data.py` 链路不变；
- **并发（不用满）**：机器 **224 核** ⇒ 4 档 60s 标定（`64/96/128/192`），记 tokens/s、CPU%、NFS 写速、load；取"增益不抵代价"那档（预期 96–160），**留余量给 85M**；`nice -n 10`；回报写明选它的理由；
- 落盘：`/nas_train/.../baize-data/text/`（先 `df -h`，按"未分词×1.5"估余量；不足再议 `/nas_env`）；
- 命名（与 `env14_*` 同规范）：按「repo+子目录」定前缀（如 `ufw_en_*`/`ultrax_*`/`ud_code_*`），**每前缀必须有 manifest**（shard→源 parquet）；
- **断点续传**：已有 `.bin/.idx/.json` 的 shard 直接跳过；失败重试 2 次后落 `failed_shards.txt`；
- `setsid` 后台启动，日志 `/tmp/tokenize_untokenized_*.log`。

**③ 监控**：每轮回报 `done/total`、累计 tokens、tokens/s、CPU%/load、NFS 写速、ETA、失败数；完成后校验 `.bin=.idx`、总字节、`num_tokens` 求和、tokens/byte 合理性。

**④ 交付**：①三张表（A/B/C）+ 并发标定表（4 档）+ 启动命令 + 日志路径；②完成后每前缀 shard/tokens/字节 + 校验 + 空间变化；③更新 `DATA_LEDGER.md`/`MEMORY_DATA.md`；盘点报告升 **v3**（加「已下载未分词→已分词」+ 训练可用 token 总量）。
> 🚫 不许把 `/tmp`、`staging`、`*.orig` 当源；🚫 不碰 `env14_*`（en_v1_4）与 `/nas_env/full_*`；🚫 未分词前不得声称"已就绪"。


### 🗑 运维令 · 2026-10-25 10:3x（**删除「无法对应下载目录」的早期分词产物**）· 用户直令 · 最高优先
> 背景：`baize-data/text/` 现有 220 个 `.bin`（env14 110 / code_s 30 / l3_s 40 / math_s 40）。`env14_*` = **en_v1_4 全量分词（必须保留）**；其余三组来源须逐 shard 回溯到 HF 下载目录。用户令：**只认 HF 下载目录，对不上一律删**。

**① HF 白名单**：**直接用上方「11:0x 令 · 表 A」的同一次盘点结果**（同轮完成，不重复扫盘）。

**② 逐 shard 映射**：对 `code_s*`(30) / `l3_s*`(40) / `math_s*`(40) 的**每一个** `.bin`（含 `.idx/.json`），用 manifest / `.json` 的 source / 分词日志回溯输入目录 → **对得上表 A ⇒ 保留；对不上（目录不存在/不在白名单/无证据）⇒ 删除**。
**③ 闸门**：`env14_*` 与 `/nas_env/full_*` **绝对不动**；某组"部分对得上"⇒ 只删对不上的那几个并逐个写明对应目录。
**④ 留痕**：先落 `run/data/prune_unmapped_20261025.txt`（shard / keep|delete / **依据** / 字节），**再** `rm` 对应 `.bin/.idx/.json`；删前后 `du -sb baize-data/text/` + `df -h /nas_train`，**报释放量**。
**⑤ 交付**：判定表 + 删除清单 + 释放空间；更新 `DATA_LEDGER.md`/`MEMORY_DATA.md`（v3 与 11:0x 令合并出一次）。
> 🚫 删前必先落 `prune_unmapped_*.txt`；🚫 不得凭"看起来重复"删除；🚫 不碰 en_v1_4 与 /nas_env；🚫 判定依据只准用"能否对上 HF 下载目录"，不许引入其它推测。

### 🚨🚨 最高优先 · 2026-10-25 08:0x · 用户直令 · **本轮唤醒必须先做这件事**

**任务**：重新盘点 MiniCPM5 数据，**重写** `reports/report_data_tokenized_inventory_zh.html`（v2）。
**原因**：上一版漏了 4 个**已在盘**的源，且小计对不上 —— 用户要求「**以下载目录为准，不要自己加戏，不要自己创造数据源**」。

> **① 必须逐个目录列出（一个下载目录 = 一行，不许合并）**
> - `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/` 下 **4 个子目录全列**：`en`（base-en）/ `en_v1_4` / `l1_en_hq` / `zh`
> - `/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview`（**单列**）
> - 另加：Ultra-FineWeb-L3、UltraData-Code L3/L2、UltraData-Math L3/L1、`baize-data/text/` 下各历史子集
> - 每行给：绝对路径 | parquet 数 | incomplete 数 | `.bin`/`.idx` 数 | `du -sb` 字节 | TB | token(实测) | 是否已分词 | 最近写入
>
> **② 禁手填小计**：所有小计/总计用脚本求和，附录写求和式；**总字节 = 各行之和（误差 0）**。
> 上一版 `text/ 小计 = 3722.05B` 实际只有 4 个源（2238.14+550.07+658.91+274.92），表头却写 5 源 —— 这类错**不许再犯**。
>
> **③ 未分词源**（en / l1_en_hq / zh / UltraX）：token 列写「**未分词（未实测）**」，🚫 禁填估算/论文数；禁 N/A。
>
> **④ 报告必含两节**：
> - **「目录清单」放正文最前**（`ls` + `du` 第一性证据）
> - **「⑥ 与上一版勘误表」**：逐条点名 base-en / l1_en_hq / zh / UltraX-Preview 四处遗漏 + text/ 小计错误
>
> **⑤ 交付**：`reports/report_data_tokenized_inventory_zh.html`（中文 HTML 自包含 v2）+ 生成器 `run/data/gen_tokenized_inventory_report.py` + 原始测量 `run/data/inventory_v2_20261025.tsv`；commit 前缀 `data inventory:`。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

> 📦 §运维指令·2026-10-24 13:2x（MiniCPM5 全量已分词数据：硬盘实测清单）**已闭合**（首版报告已交付 `reports/report_data_tokenized_inventory_zh.html`，但**因 04 表漏源/小计错误被 10-25 令要求返工**）→ 原文归档 `run/ARCHIVE_OPERATOR_DATA.md`；**结论**：口径=只写硬盘实测（`du -sb`/`find`/`.idx` manifest），未分词原始 parquet 与 SFT/RL/85M 不计入总量、只做对照；产物 `run/data/tokenized_files_20261024.tsv`（2383 行）可复用。需要时再读。

> 📦 §运维指令·2026-10-23 22:1x（复测 92.25 代理 / 恢复 85M / 分词产物体积 / 搬 /nas_env）**已闭合**（85M 已恢复并在降优先级后台跑，迁移 5/5 全 DONE）→ 原文归档 `run/ARCHIVE_OPERATOR_DATA.md`；**结论**：代理走 92.25+hf.co 直连；迁移铁律 = rsync -a 不用 mv、校验 shard+字节一致才删源、先建软链接、/nas_env 余量 ≥ 数据×1.1。需要时再读。

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
