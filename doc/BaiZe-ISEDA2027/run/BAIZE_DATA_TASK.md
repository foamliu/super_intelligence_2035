# BAIZE_DATA_TASK.md

> 🧷 **行动优先纪律（2026-10-25 13:4x 用户令 · 覆盖一切归档/收尾/铁律类条文）**
> 用户原话：「放开这些什么禁制、铁律什么的。」
> 1. **先把活干出来，再谈记录**：本轮有未完成指令时，**先交付**（文件落盘/进程起来），心跳、日报、归档都排在交付之后。
> 2. **未完成指令不许归档**；归档是清理，不是交付物。有未完成指令 ⇒ `WAITING: 0`（loop 60s 后再唤醒），不许睡 30 分钟。
> 3. **体积不作挡箭牌**：任务书 ≤40KB 即可干活；>40KB 才需归档已闭合块。**不许因为体积/归档/心跳而推迟交付。**
> 4. 心跳必须写 `未完成指令：<有/无>`。

> ⚠️ 本文件由运维维护；agent 可【归档已闭合块】与【追加执行记录】（原文不改、不新增运维令），除此之外不改写正文。
> 📦 §运维令·2026-10-24 18:1x（85M 降优先级 → 迁移提速）**已闭合**（迁移 5/5 源全 DONE，`migrate_to_nas_env_fast.sh` 已跑完）→ 原文归档 `run/ARCHIVE_OPERATOR_DATA.md`；**结论**：`--bwlimit` 50000→300000 KiB/s、新脚本带 `--partial`+`flock` 单实例锁、不得就地编辑在跑的脚本、不得起第二实例；85M 不再是任何前置条件。需要时再读。

> 📦 §运维指令·2026-10-24 16:1x（写"正在做的迁移"报告）**已闭合**（`reports/report_data_migration_nas_env_zh.html` 已交付，唤醒 637@17:39）→ 原文已归档 → `run/ARCHIVE_OPERATOR_DATA.md`。需要时再读。


> 📦 §运维指令·2026-10-24 08:4x（用户质询：分词5worker+85M线路）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：Q1=5worker因串行+剩余shard少(非硬编码),升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT);85M用parallel16+92.25续传。需要时再读。


> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

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
