# BAIZE_DATA_TASK.md

### 🔴 用户令 · 2026-11-13 18:5x（**先确认 StepB 下载 ETA 的基数与算法：15.9TB vs 2.1TB/5297 文件对不上**）· 用户直令 · 最高优先 · ✅ 已确认

> **回执（唤醒1489, 2026-11-13 20:25）**：**已确认**。HfApi().dataset_info(files_metadata=True) 实测 repo 总计 8207 文件 / 3,545,765,800,565 B = **3.546 TB**（非 15.9TB！）；data/part-*.parquet = 8192 文件 / 3,545,762,968,481 B = 3.546 TB。15.9TB 出处 = stats/train/totals.json 的 total_bytes = 11.5TB（未压缩 content size）。已下 2.358 TB / 5455 parquet / 2 inc(.cache)。逐文件比对剩余 2737 文件 / 1,195,119,410,512 B = **1.195 TB**。实测速率（444s 窗口）：21.6 MB/s = 19.1 s/file（近期，下降 3.7 倍）；全程均速 79.3 MB/s = 5.46 s/file。**ETA 保守 ~14.7h（近期速率）/ ETA 乐观 ~4.2h（全程均速），取较大 → ~14.7h**。磁盘 /nas_user 可用 59.3TB >> 1.2TB → ✅。StepC 护栏已修复（旧脚本 incomplete 检查在 data/ 始终返回 0 + EXPECTED_FILES=8207 从未用于 break 条件 → 已修复：REPO_ROOT 含 .cache/ + EXPECTED_PARQUET=8192 + 三条件 + 崩溃 exit1）。落盘 /tmp/stackv3_size_audit.json。**结论：本次下载是 3.546TB 不是 15.9TB，剩余 1.195TB，ETA 保守 ~14.7h**。

> **用户原话**：「data：下载ETA有问题。15-2=13TB，不可能在几小时下载完的吧。让它确认一下。」

**自洽性检查（先看这段）**：11-13a 的标的是 stack-v3-train **全量 15.9TB**、已下的 2TB 不重下 ⇒ 剩余应 ≈ **13.8TB**；但 MEMORY 写的是「**5297/8207=65%、2.1TB、~4.1s/file、ETA~3.3h**」⇒ 反推 8207 个文件 ≈ **3.3TB**（397MB/文件），**与 15.9TB 差约 5 倍**。现 ETA 只按「文件数 × 单文件秒数」推，**既没按字节算，也没确认这 8207 个文件是不是全集**。

**必须实测并回报（证据优先，禁止估算）**：
1. **权威字节**：data 机器上 `HfApi().dataset_info("HuggingFaceCode/stack-v3-train", files_metadata=True)` 分别求和 —— (i) 本次 pattern `data/part-*.parquet` 的**文件数/字节**（这才是分母）；(ii) 全 repo 所有 sibling 的字节（解释 15.9TB 出处）。落 `/tmp/stackv3_size_audit.json`。
2. **已下实测**：`du -sb <目标目录>/data`、`find … -name 'part-*.parquet' | wc -l`、`find … -name '*.incomplete' | wc -l`，与 MEMORY 的 2.1TB / 5297 / 0inc 对齐。
3. **剩余字节**：按 1(i) 清单**逐文件**比对本地是否有同尺寸文件后求和（🚫 不用「剩余文件数 × 平均大小」）。
4. **实测速率**：取 **≥10 分钟**窗口的前后 `du -sb` 差值 ÷ 秒数，同时报 **MB/s 与 file/s**。
5. **两个 ETA 并列**：`ETA_bytes = 剩余字节 / 速率` 与 `ETA_files = 剩余文件数 × 实测 s/file`，对外取**较大者**；两者差 >2 倍必须写明原因（文件大小分布 / 重试 / 代理限速）。
6. **磁盘**：`df -B1` 可用字节 ≥ 剩余字节 × 1.1，否则**先停下载并报告**（不许写满盘）。
7. **StepC 护栏**：auto-wait 触发条件必须含「下载进程 exit=0 **且** `.incomplete`=0 **且** 文件数 == 1(i) 文件数」，否则会在**部分数据**上启动分词 → 立即补护栏或先暂停 StepC。
8. **一处纠正多处同步**：把纠正后的口径/ETA 覆盖 `MEMORY_DATA.md` 快照里的 "ETA~3.3h/~21:50CST" + 心跳一行 + 本令下方回执（写「已确认 / 仍待确认」）。

**判据（缺一即未完成）**：① 1(i)/1(ii) 两个字节数都在；② 剩余字节与 ETA_bytes 有算式；③ 明确回答「本次到底 3.3TB 还是 15.9TB」并给证据；④ StepC 护栏结论；⑤ MEMORY 旧 ETA 已被覆盖。
**红线**：🚫 不得只用「文件数 × 秒数」当 ETA；🚫 不得拿 repo 卡数字当本次口径；🚫 不得为赶 ETA 调高并发抢 S1/pretrain 带宽。
**落盘**：`/tmp/stackv3_size_audit.json` + `MEMORY_DATA.md` 快照/心跳 + `daily-memories-data` 一行。

> ⚠️ 本任务书当前已 47.9KB（>32KB 红线、>40KB 硬上限）：本轮**同时**把已闭合的旧令原文搬进 `run/ARCHIVE_OPERATOR_DATA.md` 留 1 行指针，归档后正文必须 ≤32KB。

---

### 🔄 用户令 · 2026-11-13b（**分词数据搬到 /nas_user + 下载完成后立即分词新数据**）· 用户直令 · 最高优先 · 进行中

> **用户原话**：「让 data 把第一批 2TB 的分词数据也搬运到 /nas_user，等下载完立即分词（已分词的部分跳过）。」

#### 0. 现状（先读，别重复劳动）

| 项 | 值 | 来源 |
|:--|:--|:--|
| 已分词数据 | 4600 shard / 926GB / 249.2B tokens | MEMORY_DATA 唤醒1478 |
| 分词产物位置 | `/nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train/`（.12 上，13288 文件 = 4600×3 `.bin/.idx/.json` + MANIFEST.json） | 实测 ssh .12 |
| 源 parquet（已搬走） | 原 `/nas_inference/.../stack-v3-train/` 2TB 已 rsync 到 `/nas_user/.../stack-v3-train/`，源删除中 | MEMORY_DATA 唤醒1480 |
| 全量下载 | 🔄 `hf download` 后台跑中（8207 files / 56% / 4615 parquet / 1.995TB / nice19 / max-workers2） | MEMORY_DATA 唤醒1480 |
| 分词脚本 | `run/data/stackv3_tokenize.py`（`PARQUET_DIR` 硬编码 `/nas_inference/...`，`OUTPUT_DIR` 硬编码 `/nas_train/.../tokenized/...`，支持 `--output-dir` + `--shard-list` 参数） | 实测 |
| `/nas_user` 余量 | 113T / 57T 可用 | 实测 df |

#### 1. 执行顺序

**Step A · 搬迁已分词数据 926GB → /nas_user（立即执行，与下载并行）**
- `rsync -a --info=progress2 /nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train/ /nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train/`
- 后台 `setsid` + 日志 `/tmp/stackv3_tokenized_rsync.log` + `nice -n 19` + `ionice -c3`
- 搬完校验：`find <dst> -name '*.json' | wc -l` = 4600（每 shard 一个 .json）且 `du -sb <dst>` 与源一致
- **校验通过后删源**：`rm -rf /nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train/`（释放 `/nas_train` 926GB）
- 🚫 删源前必须确认 rsync 字节级一致
- ⚠️ `/nas_train` 是 pretrain 训练盘，删 926GB 后确认不影响训练（pretrain 用的 baize-llm 模型/ckpt 不在此路径）

**Step B · 等全量下载完成（当前 hf download 后台跑中）**
- 监控 `/tmp/stackv3_post_rsync.log`（或 hf download 日志）
- 完成标志：`find /nas_user/.../stack-v3-train/data/ -name '*.parquet' | wc -l` 达到全量 shard 数（预计 ~8200），无 `.incomplete` 文件

**Step C · 立即分词新下载的 shard（跳过已分词的 4600）**
- 分词脚本 `stackv3_tokenize.py` 需改 `PARQUET_DIR` 指向新位置：`/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data`
- `OUTPUT_DIR` 指向 `/nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train/`（与搬迁目标一致）
- **跳过已分词**：脚本已支持 `--shard-list` 参数 → 传入新 shard ID 列表（part-04600 起）；或脚本检测 `.json` 已存在则 SKIP
- 先用 3 shard 试分词（验证 tokenizer 加载、EOD 语义、新路径读写 OK）→ PASS 后全量并行
- `setsid` 后台 + `nice -n 19` + `ionice -c3` + 日志 `/tmp/tokenize_stackv3_new.log`
- 并行度：16 workers（同第一批，nice 19 不挤 S1）
- 每轮报进度（已完成 shard 数 / 失败数 / ETA / 吞吐 tokens/s / 磁盘余量）

**Step D · 完成后**
- `du -sb` 实测分词总字节 + `find -name '*.json' | wc -l` shard 总数
- 更新 `DATA_MAPPING.md`（分词产物新位置 / 总 token / 总字节）
- 更新 `MEMORY_DATA.md` 进度快照 + 一行结论
- commit `data stackv3-full-tok:` + push

#### 2. 纪律

- 🚫 不挤 S1（pretrain 训练在 `.29` 跑，分词 `nice 19` + `ionice -c3`）
- 🚫 不碰 `/nas_train` 上非 stack-v3 的文件
- ✅ rsync 搬迁用 `-a`，校验字节一致才删源
- ✅ 分词跳过已有 `.json` 的 shard（不重复分词）
- ✅ 每轮报进度
- 🚫 `/nas_user` 余量红线 ≥ 5T；分词产物 926GB + 新增预计 ~2-3TB → 总需 ~3.5TB，57T 可用充裕

#### 3. 验收

- `/nas_user/.../tokenized/HuggingFaceCode/stack-v3-train/` 包含全量 shard 的 `.bin/.idx/.json` + MANIFEST.json
- `/nas_train` 原分词位置已清理（0 残留）
- `DATA_MAPPING.md` 更新（新位置 / 总 token / 总字节）
- 已分词的 4600 shard 未被重跑
- 新 shard 全部分词完成（`failed_shards.txt` 为空或已逐一说明）

---

### 🔄 用户令 · 2026-11-13a（**把 stack-v3-train 全量下载到 /nas_user，已下的 2TB 挪过去不重下**）· 用户直令 · 最高优先 · 进行中

#### 0. 现状（先读，别重复劳动）

| 项 | 值 | 来源 |
|:--|:--|:--|
| 已下载 | 4600 parquet / 1,987,930,402,327 B（1.85TiB）/ 0 incomplete | §H + MEMORY_DATA |
| 当前位置 | `/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/`（`data/` 4600 parquet + `stats/train/` 5 json） | 实测 |
| 全量 train split | **~15.9TB**（`HuggingFaceCode/stack-v3-train` 仅 train，🚫 full 113.7TB） | §H |
| 目标位置 | `/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/` | 用户指定 |
| `/nas_user` 余量 | 113T 总 / 56T 已用 / **57T 可用**（50%）→ 放 15.9TB 充裕 | 实测 df |
| `/nas_inference` 余量 | 45T / 19T 已用 / 27T 可用（42%）→ 挪走 2TB 后释放空间 | 实测 df |

#### 1. 执行顺序

**Step 1 · 搬迁已下载的 2TB（优先，不阻塞分词）**
- 用 `rsync -a --info=progress2` 把 `/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/` 整目录搬到 `/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/`
- **搬完校验**：`find <dst>/data -name '*.parquet' | wc -l` = 4600 且 `du -sb <dst>` 与源字节一致后才删源
- `rsync` 而非 `mv`：NFS 跨盘 `mv` = copy+delete，不可靠；`rsync -a` 保权限/时间戳，校验通过后再 `rm -rf <src>`
- 🚫 删源前必须确认 rsync 字节级一致；🚫 不要碰正在分词的 `baize-data/tokenized/` 产物（分词读的是 `/nas_inference` 源 parquet → 搬迁期间分词可能还在跑，**等分词主跑完成后再搬**，或先 `cp -a`（保留源直到分词结束再删）)
- **重要**：如果分词仍在运行并读取 `/nas_inference` 的 parquet 源文件，**先等分词主跑+rerun 全部完成**再执行搬迁删源；可以先把目标目录建好、开始 rsync（rsync 不影响源读取），但 `rm -rf <src>` 必须等分词完全结束

**Step 2 · 下载剩余 ~13.9TB**
- 用 `huggingface-cli download HuggingFaceCode/stack-v3-train --repo-type dataset --local-dir /nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/` 下载全量 train split
- `hf download` 会自动跳过已存在的文件（断点续传），所以 Step 1 搬过去的 4600 parquet **不会被重下**
- 走代理：`HTTPS_PROXY=http://172.19.92.25:13128 HTTP_PROXY=http://172.19.92.25:13128`
- `setsid` 后台 + 日志 `/tmp/stackv3_full_download.log`
- `nice -n 19` + `--max-workers 2`（🚫 不挤 S1 带宽；分词如果还在跑，下载让位分词）
- 批次粒度：每 ~500GB 报一次进度（已下 parquet 数 / 总估计数 / 当前字节 / ETA / 磁盘余量）
- 🚫 `/nas_user` 余量红线 ≥ 5T，不足则暂停报运维

**Step 3 · 完成后**
- `du -sb` 实测总字节 + `find | wc -l` parquet 总数
- 更新 `DATA_MAPPING.md`（源/字节/文件数/新位置/证据命令）
- 更新 `MEMORY_DATA.md` 进度快照 + 一行结论
- commit `data stackv3-full:` + push

#### 2. 纪律

- 🚫 不挤 S1（pretrain 训练在 `.29` 跑，下载 `nice 19` + `--max-workers 2`）
- 🚫 不碰 `/nas_inference` 上其他数据集
- 🚫 不动 `baize-data/tokenized/` 分词产物
- ✅ 搬迁用 `rsync -a`，校验字节一致才删源
- ✅ 下载用 `hf download`（自动跳已存在文件）
- ✅ 分词完成前不删 `/nas_inference` 源 parquet
- ✅ 每轮报进度（parquet 数 / 字节 / ETA / 磁盘余量）

#### 3. 验收

- `/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data/` 包含全量 train split parquet
- `du -sh` ≈ 15.9TB（与 HF 标注一致或接近，偏差有解释）
- `/nas_inference` 原位置已清理（0 残留）
- `DATA_MAPPING.md` 更新
- 分词产物不受影响

---

### ✅ 用户令 · 2026-11-12（**分析 stack-v3-train 里哪些数据最能提升 EDA 脚本能力**）· ✅ 已交付 → 原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-12 EDA脚本价值分析」；结论：V1~828文件/~0.01B tok, V2~6854文件/~0.04B tok, V3~139518文件；Tcl唯一显著EDA命中39.2%/SKILL未检出/PyAether 0命中；报告 `reports/report_data_stackv3_eda_script_value_zh.html`；commit a6370ce60。

### ✅ 用户令 · 2026-11-12（**把 stack-v3-train 2TB 分词**）· ✅ 已完成 → 4600/4600shard DONE(245.8B tok/926GB)；rerun 40shard DONE(0ERR)；分词产物已搬至 /nas_user。详见 MEMORY_DATA 唤醒1478。

### ✅ 用户令 · 2026-11-11（**为 vision encoder 找图文对**）· ✅ 已交付 → 原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-11 vision图文对调研」；结论：归因+盘点25源+推荐Top5；报告 `reports/report_vision_textpair_sourcing_zh.html` 28KB 6节 0外链。


### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

> 📦 §运维令 2026-11-10 08:1x（更新论文数据节：淡化源名+双饼图）**已撤回**（用户 11-10 改令：改由 opencode 直接执行，data 不再承接）。需要时再读。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### ✅ 运维令 · 2026-11-07 10:10（**`stack-v3-train` 正式放行：ROI 高，先下 2TB 优质子集**）· 用户直令 · 最高优先 · ✅ 已交付（2TB/7批/4600parquet/0inc/ROI复盘✅有价值/97.6%独特）

> **用户原话**：「data：stack-v3-train 从 ROI 来讲，I 比较高，因此 ROI 有限。可以选择下载部分优质的（比如先下 2TB）。」
>
> 解读（按上下文最合理口径）：**stack-v3-train 的 ROI 高，但整库太大（15.9TB train / 113.7TB full）导致实际可拿的收益有限，因此只挑优质子集，首批 2TB。**

#### 1. 授权范围（本令即批文）

| 项 | 口径 |
|:--|:--|
| 数据集 | `HuggingFaceCode/stack-v3-train`（**仅 train 分片**，🚫 full 113.7TB） |
| 首批体量 | **2TB 上限**（含 `.incomplete` 已下部分；不再走"单集 >=1TB 需报批"流程） |
| 批次粒度 | 每批 <=300GB，逐批实测/校验/回填后 commit，再起下一批 |
| 总量红线 | 本批次总占用 <=2TB；批间须复核 `/nas_inference` 余量 >=5T，不足则暂停报运维 |
| 并发/带宽 | `nice -n 10`（或 19）、`--max-workers <=2`、断点续传；🚫 不得与 S1 抢带宽 |

#### 2. "优质"的判定（自定但必须写清并留证据）

1. **语言优先序（EDA/PyAether 相关性）**：Python（含 PyAether/EDA 工具链脚本）> C/C++ > Verilog/SystemVerilog > Tcl > Makefile/CMake/Shell/Bazel。
2. **质量过滤**：剔除 minified / generated / vendored 第三方 / test fixture / 纯配置大文件 / 单文件 >1MB 的生成物；剔除低质量仓库（无 license、星数极低、空仓库、纯文档仓库）。
3. 用 HF `--include` 按子集/语言/分片挑选，**禁止整库拉取**；挑选规则与命中量写进 `DATA_MAPPING.md`。
4. 若发现 stack-v3-train 的分片结构不支持按语言筛，则按分片号 + 抽样质检的方式挑选，并说明抽样方法与置信度（不许凭感觉）。

#### 3. 每批必交付（否则视为未完成）

1. `du -sb` 实测字节 + `find | wc -l` 文件数 + `.incomplete` 数量；
2. 语言分布与 token 估算（给出估算方法）；
3. 质量过滤规则命中数（剔除量/保留量）；
4. `DATA_MAPPING.md` 增行（源/字节/文件数/存储形态/证据命令），并更新 ROI 表；
5. commit 前缀 `data stackv3:`。

#### 4. 2TB 完成后的复盘（后一批须运维再批）

- 给一份**实测 ROI 复盘**：每 TB 带来的 token / 独特性 / 与现有 UltraData-Code L2/L3 的重叠度（可抽样 1 万文件估 n-gram 重叠）。
- 明显低效则停；确有价值再报下一批。**2TB 不是要"下满"，够用即停。**

> 与原 08:5x 令的关系：08:5x 令的">=1TB 先报批"由本令对该 2TB 批次**豁免**；`the-stack-v2` 仍**禁下**，其余单集 <1TB 口径不变。

---


### 📦 归档指针 · 2026-11-07 08:5x「代码语料放行 stack-v3-train」· ✅ 已交付（ROI表+8源25.14GB+stack-v3调研+2TB全下+ROI复盘）。现行要点：`the-stack-v2` 🚫禁下；`stack-v3-train` 仅 train 15.9TB（🚫 full 113.7TB）；其它单集 <1TB 按 ROI 自排；code 补料属**低压力背景任务**（用户：有也行无也行、不急、不挤 S1 带宽）。原文见 ARCHIVE「归档块 · 2026-11-11」

### 🚀 运维令 · 2026-11-04 13:2x（**放行 B 类 agentic 数据下载 · 落盘 /nas_inference**）· 用户直令 · 最高优先 · ✅ 已交付（12/12 落地 78.73 GiB）

> 用户批准（2026-11-04 13:2x）：放行数据下载（A+B 类）。A 类已落地 10/10；本条放行 **B 类 agentic**。

**① B 类下载清单（~90–180 GiB，不含巨大项）**：
- P0：`SWE-bench/SWE-smith`(5-10G,MIT) · `nvidia/Nemotron-Terminal-Corpus`(10-15G,CC BY 4.0) · `nebius/SWE-rebench`(3-5G)
- P1：`zhangdw/to-tool-call-datasets`(2.4G) · `tuandunghcmut/toolbench-v1`(10-50G,Apache-2.0)
- P2：`open-thoughts/AgentTrove`(18.6G) · `microsoft/Orchard`(15-25G,MIT) · `nvidia/Nemotron-Cascade-RL-SWE`(10-20G) · `nvidia/Nemotron-Cascade-SFT-SWE`(10-20G,CC BY 4.0) · `SWE-bench/SWE-smith-trajectories`(2-5G)
- P3：`mshojaei77/terminal-command-execution-sft`(<5G) · `ia03/terminal-bench`(<5G,评测集仅去污染)

**② 巨大项不默认下**：`AlienKevin/SWE-ZERO-12M-trajectories`(111G) 体量大，选择性下或后置。

**③ 落盘**：`/nas_inference/app.e0031982/datasets/<repo原名>/`；gated 源用已配 token（`.29` `~/.cache/huggingface/token`）；走代理 `HTTPS_PROXY=http://172.19.92.25:13128`。

**④ 纪律**：`setsid` 后台 + `/tmp/data_download_*.log`；🚫 不挤 S1（nice、限并发、留带宽）；断点续传；93 完成后写 mapping；commit `data 下载:`；心跳 `未完成指令：有` ⇒ `WAITING: 0`。

### 📦 运维令 · 2026-11-04 13:2x（RL+数学+agentic 调研）+ 09:4x（复杂推理+代码 SFT 调研）· ✅ 均已交付 → 原文见 `ARCHIVE_OPERATOR_DATA.md`

> **用户原话**：①「请 data 调研能够强化 LLM 复杂推理和代码能力的 SFT 和 Code-SFT 数据集，写成中文 HTML 报告。」②「调研提升复杂推理/代码/数学/agentic 能力的 SFT+RL 数据集」。
> **交付**：`report_data_reasoning_code_sft_survey_zh.html`(79KB) + `report_data_rl_math_survey_zh.html`(38KB)，均 0 script 0 外链。**口径**：只调研不下载；真去 hf.co 核实 repo/体量/license/gated/字段；奖励信号类型单列；与盘上 12 源去重。需要明细读报告原文。
### 🚀 运维令 · 2026-11-04 09:2x（**批准下载长上下文(A类)数据 · 落盘 /nas_inference**）· 用户直令 · 最高优先

> 用户批准（2026-11-04 09:2x）：批准下载「长上下文」数据集，落盘 `/nas_inference/app.e0031982/datasets/`（覆盖报告 §6 里的 `/nas_env` 老路径）。

**① 范围（只下 A 类长上下文，~286 GiB）**：`ysngkil/whole-books`(25G) · `princeton-nlp/prolong-data-512K`(120G) · `openbmb/InfLLM-V2-data-5B`(25G) · `self-long/RULER-llama3-1M`(<5G) · `caskcsg/NExtLong`(<50G) · `THUDM/LongAlign-10k`(<5G) · `birgermoell/oellm-longctx-...pilot-v1`(<5G) · `deepmind/pg19`(12G) · `ghostcc3/mix-context-post-training-128k`(<5G) · `yuyijiong/LongData-Corpus`(36G, gated, 用户 token 授权)。合计约 **286 GiB**。

**② 本轮不下（⚠️）**：`HuggingFaceCode/stack-v3-train`(15.9TB) / `bigcode/the-stack-v2`(67.5TB,gated, 无 SWH 协议) 体量巨大**不默认下**；「未核到」体量的（LongBlocks 等）先核体积再下。agentic(B 类)不在本令范围。

**③ gated 认证（`yuyijiong/LongData-Corpus` 专用）**：HF token 已由运维配到 `.29` 的 `~/.cache/huggingface/token`（chmod 600，经代理校验 `whoami`=foamliu ✅）。下载时走代理 `HTTPS_PROXY=http://172.19.92.25:13128` 直连 hf.co，`hf download` 自动读该 token 认证。🚫 token 不得写入报告/日报/任何 commit。

**④ 落盘**：`/nas_inference/app.e0031982/datasets/<repo原名>/`（该盘 45T 已有 17T、余 29T，足够）；下载后按「镜像下载路径」写 mapping。

**⑤ 纪律**：`setsid` 后台 + `/tmp/data_download_*.log`；🚫 不占 GPU、不挤 S1（`nice`、限并发 ≤4、限带宽留余量给训练）；失败续传/断点；commit `data 下载:`；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到落地。

### 🚀 运维令 · 2026-11-04 09:1x（**确认 85M 下载完成 · P0 待命**）· 用户直令 · 最高优先

> 运维确认（2026-11-04 09:1x）：「85M 已经下完了。」

**① 85M 状态翻转**：把 85M 下载从「疑似完成 / 待运维确认」正式翻成 **✅ 已完成**（进程已停 + 无 `.incomplete` + 磁盘正常，运维已核）。心跳/状态头同步更新。

**② 归档**：85M 下载相关已闭合的运维块按体积规程归档（移 `ARCHIVE_OPERATOR_DATA.md` + 留 1 行指针），腾体积。

**③ 下一步 P0/P2/P3 暂不执行**：whole-books / SWE-smith / Nemotron-Terminal-Corpus / SWE-rebench / mix-ctx-128k / terminal-bench-2.1 **仍 WAITING=1，待运维另行批准后再下**（本轮只确认 85M 完成，不启动新下载）。

### 📦 运维令 · 2026-10-31 17:3x（HF 两类数据集调研：长上下文 + agentic）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_DATA.md`

> **用户原话**：「让 data 用 web search 去 hf.co 找找下边两类数据集：1. 长上下文（用于白泽的长上下文训练）2. agentic（用于白泽的 SFT 和 RL…）。上述调研写个中文 HTML 报告」
> **交付**：`reports/report_data_lc_agentic_survey_zh.html`（117KB，单文件 0 script 0 外链）+ 生成器（幂等）。**关键口径**：decay-B 闸门 = `en_v1_4` 里 ≥32K 文档仅 2.52% token、≥128K 仅 0.03%，目标 ≥20%/≥1%；报告须给每个候选的「≥32K/≥128K 占比」证据或标「未标注需实测」。需要明细再读 archive / 报告原文。
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

评测集本体路径（用于建黑名单，只读，绝不写入任何训�
