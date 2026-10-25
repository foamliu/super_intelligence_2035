# MEMORY.md — BaiZe-ISEDA2027 **运维（operator）** 长期记忆 · **醒来先读本文件**

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。适用于**所有线**（pretrain / vision / data / harness / zhulong / news / recruit / research / video）。

## 2026-10-25 17:5x — 四条用户令下发（harness / data / vision / pretrain）

用户 17:4x 一次性下四条，已写进各自任务书顶部（用户直令 · 最高优先），并同步把「已闭合」旧块原文搬进 ARCHIVE（emoji 原样保留）：

| 线 | 任务书 | 新令要点 | 体积 | 归档（原文搬入） |
|:--|:--|:--|--:|:--|
| harness | `run/BAIZE_HARNESS_TASK.md` | ① 授权 hermes / claude-code 全量复跑 89 题（canonical 87，先进 10 题判活）；② 排查 codex 高 err（20/87=23.0%，59 exception，先分类再归因：适配器 / 容量 / 上游） | 29,468B | 08:2x 适配器修复令（5,045B） |
| data | `run/BAIZE_DATA_TASK.md` | 目录名不重要（可改名）；唯一硬交付 = `run/data/DATA_MAPPING.md`（Markdown 单一事实源、合计脚本求和），HTML 按需生成；32 uncovered shard 降为「未映射」表内标注、不阻塞、未批准不许删 | 33,582B（红线 40KB） | 未归档（余量充足） |
| vision | `run/BAIZE_VISION_TASK.md` | OCR 类评测偏低：web search 调研「合成数据补强 OCR」并写 8 节中文 HTML 报告；只调研不训练；OCRBench / DocVQA / ChartQA / InfoVQA 均不需 judge | 30,448B | 10-24 16:1x 报告令（4,482B） |
| pretrain | `run/BAIZE_PRETRAIN_2B_TASK.md` | 6 格网格：seq 8192 / 16384 / 32768 x 2M / 4M tok/step（GBS 256 / 512 / 128 / 256 / 64 / 128），唯一变量 = seq；80 步取 step 30-80 median；OOM 回退单列不进主表 | 31,137B | 10-25 07:4x 双机报告令（5,200B） |

- 用户原话（摘）：harness「授权 hermes/claude-code 全量复跑 89 题、排查codex 高 err」；data「目录不重要，分词后可以改目录名字。关键是维护好映射表，这个映射表可以是markdown，需要时转HTML给运维报告。」；vision「现在OCR类评测很低，web search 调研一下合成数据补强这块能力的方法，写报告。」；pretrain「…在每步训练数据量不变（2M/4M,对应S1和S2）的情况下，看看增大seq对训练吞吐的影响。」
- 基线锚点：pretrain 双机 e18 = 606,300 tok/s、4,128,768 tok/step（seq=4096）；OCR 参考（ArmB，`run/vision/generate_armC_mllm_report.py` 的 ARMB）OCRBench 1.6% / DocVQA 7.36% / ChartQA 12.52% / InfoVQA 16.88%。
- 18:2x（data 32 shard · 终裁）：32 个 = l3_s 28 + math_s 4，合计 472.85B tokens ≈ 1.89 TB、涉 1286 个 parquet 引用；它们**有下载目录**，但 manifest 指向废弃的 `staging_r3`，**无法被 DATA_MAPPING.md 稳定收录**。用户口径：「不明来历、无法被映射表收录的数据 = 不可用 = 只占磁盘」⇒ **32 个全部删除**，不再讨论是否唯一。已改令：删前留档 `run/data/deleted_unmapped32_20261025.tsv`（路径/字节/文件数/parquet 引用，先 commit 再删），删后 `du -sb` 复核 + `df` 前后对比，`DATA_MAPPING.md` 增设「已删除/不可用」节，重跑镜像与 triplet/inode 校验；**下载 parquet / 下载目录 / env14 / full_* 一律保留**（MiniCPM5 训练数据本体，用户 18:3x 再次确认）。
- 18:0x 顺手清理：删除重复且陈旧的分身文件 `run/reports/report_pretrain_dualnode_throughput_zh.html`（项目级 `reports/` 有正式版）。
- 18:5x（data · 映射表是命门 + 授权清理）：用户令「维护好 `run/data/DATA_MAPPING.md` 至关重要；可以适当清理硬盘」。已下发（`BAIZE_DATA_TASK.md` 39,650B / 红线 40KB）：① 补 `run/data/gen_data_mapping_md.py`（幂等、重跑两次逐字节相同；合计脚本求和）；A 节加「下载目录字节 / 下载-分词字节比」两列；「证据」列写可复现命令；② 分词 `done=131/131` 后刷新第 7-10 行 `分词中`→`镜像完整`；③ 清理走「候选清单（表观 vs 实占 + inode 链接数）→ 分批实占 ≤500GB → 前后 `df`/`du` → triplet+inode 校验（镜像 .bin 恒 716、悬空 0）」。可删 = `staging_r3` 剩 78 个纯符号链接暂存 / 崩溃残留孤儿 / 空目录 / 旧日志 / 已被镜像收录的重复硬链接副本；**不可删 = `full_*`、`tokenized/` 镜像、`INDEX.tsv`、`DATA_LEDGER.md`、下载 parquet**。禁把表观体积当实际释放。
- 19:5x（vision · 路线①细化）：用户令把 OCR 合成数据方案细化成「可照着做」的执行报告，点名要答「中英文比例 / 数学公式怎么办 / 其他呢」。已下发（任务书 31,396B，归档 10-24 10:3x 块 3,981B）：
  - 报告必答四问：① 中英文基线配比表 + 至少 2 个候选配比（A 英6:中3:混排1；B 中英1:1）与可判定判据；② 数学公式三通道（im2latex 纯公式 / arXiv LaTeX+KaTeX 正文夹公式 / 公式+表格混排）+ token 预算与渲染失败率；③ 其他类别（文档版面、图表、表格、手写、场景文本、低质退化、代码截图、多语种）各类数量/优先级/判据；④ 可执行管线（trdg/SynthTIGER 参数、stage-2 780k 混合比、SFT 配方、成本与 ETA、P0 20 万 pilot -> 全量 -> SFT）。
  - 预注册判据：主 OCRBench >= +2pp（基线 1.60%）；副 DocVQA/ChartQA/InfoVQA >= +1pp；回归护栏 MMStar/MMBench/AI2D/RealWorldQA 掉幅 <= 1pp。必须给决策树。
  - 交付 `reports/report_vision_ocr_sft_plan_zh.html`（9 节、>=18KB、0 script/0 外链）+ `vision/generate_ocr_sft_plan_report.py` + 一页纸执行清单；本轮不启训练、不生成全量数据。
- 20:2x（pretrain · seq 掉速根因令，**补记：上一轮只在对话里分析、未落盘，现正式落盘**）：用户质疑「4096->8192 吞吐掉 5.6x 不符合常识，阿里等 8192 预训练很常见，我们又是 Mamba2-hybrid，理应对长上下文更友好」，允许 web search。已下发（任务书 32,585B；归档 10-24 23:5x 块 3,607B）：① 补单变量对照 cfg0a（seq4096/2M）与 cfg0b（seq4096/4M 重跑基线）；② 时间分解 + dmon util + CUDA graph 状态 + 数据侧重打包/worker；③ web search 对标（Qwen2.5 预训练最大 32,768 / Llama 3 8K / Megatron 长序列实践 / SSD chunk scan 融合可提 1.50-2.51x）；④ 假设-检验表 H1-H5 逐行实测；⑤ 修复只改一项并复测，判据修复后降幅 <=30%；交付 `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`（≥15KB）+ 生成器 + 更新 seqlen 报告与 EXPERIMENTS；commit 前缀 `pretrain rc:`；ETA 3-4h。
- 22:3x（网格收尾 + 分词停顿）：① **pretrain 6 格全部结束**（21:46）：seq 8K/16K 四格 tok/s = 108,291 / 111,897 / 112,094 / **121,495**，per-GPU 6.8-7.6K；**cfg5/cfg6（32K）FAIL**，峰值 81,031 MiB（卡 80GB 上限）。四格峰值显存几乎相同（81,079-81,087）且与 seq/tok-step 无关 ⇒ 疑似「与 seq 无关的固定巨额分配」，已要求列入 profile（memory_summary）；cfg5/6 按配方变更组用 recompute/dist-opt 重试。② **data 分词停顿**：`done=94/131` 自 19:21 起 2.6h 不变、tokens/bin_bytes 完全相同、37 进程存活、ETA 从 7,688s 涨到 11,369s ⇒ 已下令先诊断（ps/py-spy/nfsstat/dmesg）再按类处置，禁直接全杀。
- 仍未变的老待办：vision B4 的 MMVet / MathVista 需 `OPENAI_API_KEY`；336+anyres 需工程 scope。


- 写文件注意（记下）：本机编辑器通道会把 emoji、箭头、大于等于号转成乱码（实测 🚨 变乱码），所以本轮新指令块一律用「纯中文 + ASCII 符号」书写；归档搬运由 Python 原样搬迁，emoji 不受影响。

## ⚡ 2026-10-24 18:1x — data 迁移提速（85M 降优先级 · 用户令）

- 用户原话：「**85M 下载优先级不高。**」⇒ 不再为 85M 预留 NFS 带宽：迁移 `--bwlimit` **50000 → 300000 KiB/s**（≈51 MB/s → ≈307 MB/s，可调）。
- 新增 **`run/data_pipeline/migrate_to_nas_env_fast.sh`**（`BWLIMIT` 环境变量可覆盖、`0`=不限速；新增 `--partial` + `flock` 单实例锁；校验 shard+字节、先软链接后删源、源顺序均**与 v1 一致**）。
- 🚫 **不得就地编辑运行中的 `migrate_to_nas_env.sh`**：bash 按字节偏移增量读脚本，运行中改文件会读串行 ⇒ 必须"停旧 → 起新"。🚫 不得起第二个迁移实例（串行总量才可控）。
- 切换走 ops **RUN_ID 158**（STOP 脚本→SIGINT rsync→`setsid` 起新脚本→`du -sb` 60s 实测速率 + 剩余量/ETA）；`BAIZE_DATA_TASK.md` 顶部已下发（30,923B ✓，16:1x 报告令已归档）。
- 判据：实测 <80 MB/s ⇒ 瓶颈在 NFS/网卡而非限速，**如实记录、不得宣称"已提速"**。


## 🆕 最近操作（2026-10-25）

### 🚨 harness 运维令（用户直令 · 08:2x）：修复 claude-code / hermes / deepseek 的 0% 适配器 bug，修复期间这三路停跑
- 用户原话：「安排 harness 去排查和修复导致 claude-code/hermes/deepseek 通过率为0的适配器 bug，修复期间这三个就不要跑了。同时汇报其它四个 harness 截止目前各自的通过率（已跑完的部分）。」
- **下发** `run/BAIZE_HARNESS_TASK.md` 顶部新块（最高优先，commit `0bcd48ad` 已 push）：
  - **①只停这三路**（claude-code / hermes / deepseek-harness），按 `jobs_*`/`--project-name` 精确匹配、只 SIGTERM 对应 harbor 进程与容器；**cline-patched / codex / opencode / pi 一根汗毛不许动**；停止前先记录 batch/done/trial 列表，**已完成结果不许删**（修好要复跑对照）。
  - **②分开归因、6 条必查证据**：`verifier/reward.txt` 是否真写入（0 pass 可能=verifier 没跑/没找到 patch，而非答错）· 是否真调用模型（LLM 请求/tool call/token>0）· 37 err 的 traceback 归类 · 容器内 CLI 可用性 · **时间线（Gen7 pilot 里 hermes/deepseek 就已 0/5、claude-code 0/5+3/5 err ⇒ 老 bug 不是本轮新增）** · 与 cline/codex/pi 三个已知可用适配器做源码 diff。
  - **③修复闭环**：先 smoke oracle 可解 5 题，**判据 ≥1 pass**，再各跑 5 题确认；三路**逐个修逐个验**；🚫 不许放宽 verifier / 改 reward 口径 / 跳断言。
  - **④同时汇报四路**（`reward.txt` 口径，标注"部分结果·非最终"，并给 McNemar 初步或写"样本不足"）。
  - **⑤产出** `reports/report_harness_adapter_0pass_rootcause_zh.html`（中文 HTML 自包含）+ 补丁落 `run/harness/terminalbench/`。
  - 🚫 SWE-bench Verified 下载不停；TB 四路存活 harness 不停。
- **给用户的四路通过率快照（R490，10-25 07:31，全部为部分结果）**：cline-patched 61done/34P=**55.7%** · opencode 56/30=**53.6%** · codex 39/19=**48.7%** · pi 66/29=**43.9%**；0% 三路：claude-code 26done/0P、hermes FIN 50/0P（37err）、deepseek FIN 50/0P（37err）。
- **体积**：任务书 35.5KB → 归档 10-24 16:3x 闭合块（原文进 `run/ARCHIVE_OPERATOR_HARNESS.md` 顶部"归档 2026-10-25"节）→ **32,980B（32.2KB）**，仍略超 32KB 目标但与既有 29KB 量级一致，下轮由 agent 自滚。
- ⚠️ **当前 harness 状态 `WAITING: 1`**（30 分钟长睡）⇒ 本令要等下一轮唤醒（约 08:3x–09:0x）才执行；若要立即生效需在 `.29` 重启 `baize_harness_loop.sh`。

### 📦 data 运维令（用户直令 · 08:0x）：重新盘点 MiniCPM5 数据，`report_data_tokenized_inventory_zh.html` 返工重做
- 用户指出两处**漏源**：① `Ultra-FineWeb/tree/main/data` 下四个目录 **en / en_v1_4 / l1_en_hq / zh** 一个都没单列；② **UltraX-Preview** 没列。要求「**跟下载目录对应上，不要自己加戏，以下载目录为准，不要自己创造数据源**」。另点名「小学生错误」：④ 表中 `text/ 小计 3722.05B` 与下属各源加不上。
- **运维复核（本地已核实）**：旧报告 ③/④ 表里只有 en_v1_4 / UFW-L3 / Code L3 / Code L2 / Math L3 / Math L1 六行 + `text/` 历史三子集；**base-en、l1_en_hq、zh、UltraX-Preview 全部缺失**。且 `text/ 小计 = 3722.05B` 实为 **en_v1_4 2238.14 + code 550.07 + l3 658.91 + math 274.92 = 3722.04B（4 源）**，而原指令写「必须覆盖…以及 text/ 下其它任何 *.bin 所在目录」——**表头表述与实际行数不一致**，属同一类硬伤。
- **已下发** `run/BAIZE_DATA_TASK.md` **顶部新块**（最高优先）：三条硬口径（以下载目录为准 / 一一映射四子目录+UltraX / 小计禁手填必须脚本求和）、必做实测命令（`du -sb`+`find`+awk 按目录分组）、报告新结构（新增「目录清单 = ls 第一性证据」+「⑥ 与上一版勘误表」+ 附录 A 命令输出 / B 求和核对式 / C 历史参考值）、8 条自检清单、产出与归档。
- **铁律**：目录里没有的源不许编进表、不许改源名、不许合并目录凑行；估算/论文/历史值**永不入实测列与小计**；未分词源 token 列写「未分词（未实测）」，禁 N/A。
- **顺带修的两件事**：① 新块插入位置一度插错（跑到 10-24 18:1x 块之后），已重排到运维指令区最顶；② 任务书 34.9KB 超 32KB 红线 → 按体积规程把 3 个已闭合旧块（10-24 13:2x / 10-23 22:1x / 10-24 18:1x）**原文搬入** `run/ARCHIVE_OPERATOR_DATA.md` 顶部「归档 2026-10-25」节、只留 1 行指针 ⇒ **29,199B（28.5KB ✓）**。
- commit `d7a5d32f`，已 push，无 ahead/behind。
- **教训（记下）**：上一版报告的口径错误源于「按计划/记忆里的源列表做表」而非「按磁盘目录做表」；今后凡盘点类报告，一律先出 `ls` 目录清单，再逐目录填数。


### 📊 pretrain 运维令（用户直令 · 07:4x）：写「双机 16 卡吞吐优化与测试」报告
- 用户原话：「pretrain：关于16机吞吐量优化和测试，写个报告。」⇒ 按 SOP 写进 `run/BAIZE_PRETRAIN_2B_TASK.md` 运维指令区**顶部新块**（最高优先），commit `7c855ebc` 已 push。
- **为什么现在能写**：Task A 已完整闭合 —— 单机 e18 305,098 → **双机 e18 606,300 tok/s（扩展效率 99.4%）**；BF16 对照 528,016（**FP8 +14.8%**，Δloss 0.08%，显存≈持平）；Task B（NCCL/IB）已闭合 qps4(+0.0%)、qps8(+0.2%)，maxnch64 在测。
- **令的要求**（四段）：① 先判 Task B 是否在跑、**不盲目重跑**；在跑就并行写作，先出 `rev1（在测）`、闭合后 `rev2`；② 数据**只许引落盘日志**（master `Step Time` / worker `elapsed`，median 取 step 30–80），**#767 误报（512,801/84%/BF16+mock/64.4GB）必须写进 §6 纠错记录并作废**；③ 10 节结构（摘要/环境口径/扩展性主结果/精度消融/NCCL 全表/机制解释 99.4% 成因/与单机线对照/剩余优化排序/复现命令/数据溯源表）；④ 产出 `reports/report_pretrain_dualnode_throughput_zh.html`（中文 HTML 自包含）+ 可重生成脚本 `run/gen_dualnode_throughput_report.py`。
- **铁律**：纯写作零 GPU、测完即释放 16 卡、禁 mock 数字当扩展效率、未验证机制标「推测·未验证」、**报告禁 N/A/空单元格**（未测写原因）。任务书体积 31.1KB ≤32KB ✓。
- 预计下轮 pretrain 唤醒（loop 30min 节奏）读到并执行。


### pretrain eval: BaiZe-2B Mamba2-hybrid 长上下文推理成本基准（重测 + 报告）
- 用正确的 **BaiZe-2B Mamba2-hybrid**（NemotronH, 2.22B, 56层=24 SSM+4 Attn+28 MLP, 7.1%注意力）重测，替换旧 Xmodel Dense 数据
- 修复 SGLang `nemotron_h.py` L424 (`self.n_groups`→`self.mamba_n_groups`) + `config.json` `mamba_dt_limit`
- **64K→1M 全部成功**，2M OOM；64K prefill 41598 tok/s(+68%), decode 318(+57%)；单 H100 可服务至 1M
- 显存亚线性增长（73.15→76.71GB），SSM 状态 30.23GB 常量
- 报告：`reports/report_pretrain_longctx_infer_cost_3x2b_zh.html`（3模型对比）
- commit `1a304f509`，详见 `daily-memories/2026-10-24.md`

## 🆕 最近操作（2026-10-18）

### 🛠️ 三条运维令下发（用户直令 · 10:2x）：recruit 恢复 / harness 修中继 / data 修 git
- **recruit**：用户「Boss 登录态已修好」⇒ `WATCH_RECRUIT_TASK.md` 顶部新块：立即复扫 **bobbob / 曲先生 / 闫猛飞**（简历与 LLM/Agent 证据），**18:00 实习专场照常**；R25 口径不变（应届=校招、全职 1–5 年、只推 A/B、不约面）。
- **harness**：令其修复 **`.29` ops 中继**（同机）。依据：RUN_ID 123 自 09:54 无回执、`.last_run_id` 仍 **122**，而 pretrain（10:08）/harness（10:09）仍能 push ⇒ 中继进程停摆。要求**脚本文件方式**安全重启（🚫 禁止命令行组合 `pkill` + 启动），判据 **`.last_run_id 122→123`**；修好后继续 solo smoke → 7×5 pilot。
- **data**：判断「换 `.23` 代理时全局 export proxy」污染了 `git push` ⇒ `BAIZE_DATA_TASK.md` 顶部新块：git 一律 `env -u http_proxy -u https_proxy -u ALL_PROXY ...` 执行，🚫 不永久写 `git config` 代理；修好后立即续传 25 shard + 启分词。
- **中继命令**：RUN_ID 123 增补 `.12` 的 git 只读诊断（remote / status / proxy env / index.lock / `ls-remote` 有代理 vs 无代理对照），中继恢复后一并执行。
- 详见 `daily-memories/2026-10-18.md`。

### 📚 news：D-6 放行 —— **Lv.0 可选「连载模式」**，立即建书 + 只发前 3 章
- 用户答复 D-6：「**可以**」⇒ **Lv.0 允许直接选「连载模式」建书**，不再停在任务书 ①-3。
- 已改 `personal-watch/run/WATCH_NEWS_TASK.md` 顶部：① 前置检查压缩为 PLAN 指针（R1/R2 已完成，勿重复）；①.5 改为 **D-6 放行**；② 增加「**签约模式 = 连载模式**」；封面改用 R2 已做好的合规成片 `/home/liuyang/Desktop/超级智能2035_封面_600x800.jpg`（600×800、含书名+笔名「刘未央2035」）。
- 执行口径：**只发前 3 章**（第 1/2/3 章，配图仅 01/02/03）→ 等 1–3 个工作日审核 → 过审后 1–2 章/天；第 41 章补字（D-8）留到发布该章前处理。
- 任务书 **32,004B → 30,535B（≤32KB ✓）**。news loop 时窗 `07:00,09:30,12:00,15:00,18:00,21:30` ⇒ 下一次 **12:00** 必读本令（09:30 轮可能已读旧版）；如需立即，VM 上重启 `watch_news_loop.sh`（首轮立即执行）。
- 详见 `daily-memories/2026-10-18.md`。

### 🌐 data：`.25` proxy 503 → 改 `.23:13128` + hf-mirror 续传 `en_v1_4`（用户直令）
- 用户令：「data: 既然 172.19.92.25:13128 返回503，那就尝试用 172.19.92.23:13128+hf-mirror 来续传」
- 现状：43,520 parquet / 0 `.incomplete` / 4.1T / **85 of 110** snapshot 完成；wrapper 03:59 退出，**只差 25 shard**；`.25→hf.co` 503 已 ≈12h+。
- **根因**：`run/data_pipeline/download_en_v1_4.py` L26-27 与 `.sh` L11-12 **硬编码 `.25`** ⇒ 只 export 无效。已改为读 `HF_PROXY` / `HF_ENDPOINT`（未设时默认 `.23` + `https://hf-mirror.com`）；回 `.25` 只需 `HF_PROXY=.25` + `unset HF_ENDPOINT`。
- **已下发** `run/BAIZE_DATA_TASK.md` 顶部块（最高优先）：探针 4 条 → A/B/C 起训分支 → **按字节增长判活**（不看进程存活）→ 回报 25 shard 名单 + 实测 MB/s 与 ETA。范围仅 `en_v1_4`；85M 维持暂停。
- **中继**：`run/ops/inbox.md` **RUN_ID 121 → 122**，首块 = 只读探针（`.12` 中继若活着可立即给机读结论）。
- 体积：`BAIZE_DATA_TASK.md` 37,960B → 滚归档 3 个已闭合块（10-15 补下 RL-2609 / 10-14 恢复 4 路 / 10-14 `/nas_env`，原文移入 `ARCHIVE_OPERATOR_DATA.md`）→ **32,717B ✓**。
- 详见 `daily-memories/2026-10-18.md`。

## 🆕 最近操作（2026-10-17）

### 🎯 recruit 口径再纠正：应届 = 校招（不要）· 全职硬门槛 ≥1 年经验
- 用户令：「recruit：应届就是校招，不要校招，因为要明年才入职。至少1年工作经验。」
- **判据**：**应届生（含博士应届 / 硕士应届 / 26–27 届在校）= 校招 ⇒ 全职岗一律不推进**（删掉 R24 的「博士应届边界报备」例外）；**全职 = 1–5 年社招**（下限 **≥1 年正式经验**，实习/兼职不计；上限 5 年不变）。
- 已改权威 JD `run/recruit/hr/JD-AI-EDA-研究员-DRAM.md`（头部 + 岗位定位提醒 + 经验要求 + 派生 §1/§2/§4 共 6 处）与短名单顶部（R25 头 + 硬门槛/判据行）。
- 任务书 `run/WATCH_RECRUIT_TASK.md` 顶部新块（R25）：本轮唤醒重判 R24 的「边界 9 / 在校 17」→ 应届/在校全部 `not-eligible`（校招），产出 **§十二 R25**；已发 5 封不撤回；06:00 只在「1–5 年 + 非应届 + 证据齐」A/B 里选。
- **边界**：只约束全职岗；**实习岗不受影响**（18:00 实习专场照常）。任务书瘦身：R24 块已归档（块 L），TASK **32,752B（32.0KB ✓）**。
- 详见 `daily-memories/2026-10-17.md`。
### 📚 news 新任务：发布《超级智能2035》到番茄小说（**前置闸未过**）
- 用户令：把 `chapters_v1_1/` 42 章正文 + `images/` 配图发到番茄小说，创建连载作品；**先做前置检查，未通过不得建书**。
- 已下发 `personal-watch/run/WATCH_NEWS_TASK.md` 顶部最高优先块（30,384B）：① 素材路径（`/home/liuyang/...`，不存在则回退）② 字数核算 ③ 账号等级（Lv0/Lv1 只能完本签约 ⇒ 停止建书）→ Lv2+ 才建书（书名/分类/简介含「本故事纯属虚构」/封面 `00_stone_forest_architecture.jpg`）→ **先发 3 章**，过审后 1–2 章/天。
- **本机预量**：42 章 **中文字符 113,001 / 非空白 141,168（≈14.1 万）⇒ 未达 15 万门槛**（差 ~3.7 万中文字符 / ~0.9 万非空白）。最短 5 章（41/39/37/40/30）可作补写候选。
- 纪律：不伪造、不批量发布、登录/实名/验证码需真人即报 blocker；交付 `news/fanqie/PLAN.md` + 截图/URL，commit `news fanqie:`。
- ⏰ news loop 每天 **06:00 / 18:00** 唤醒 ⇒ 本任务实际开始时间 = **明早 06:00**。
- **22:4x 放行（用户已实名认证）**：任务书加 **①.6**——复核登录态 → 记录等级/笔名 → 建书（封面横图转 3:4 竖版）→ **只发前 3 章**；15/16/23/24/22 的配图先不插；每步截图+URL。任务书 **32,004B**（<32KB）。news 线下一轮（计划 06:00）执行；若要立即，VM 上重启 loop：`pkill -f '[w]atch_news_loop.sh'` → `setsid bash "$HOME/start_news_loop.sh" > /tmp/watch_news_loop.log 2>&1 &`。


### 🩺 harness 实况：oracle **2/5** + ops 中继被我误杀（已下发抢修）
- **harness loop 未卡死**：进程存活；18:24 那轮 cline `run timed out after 1500s` 被杀 → MEMORY 停在 18:14；19:30 又正常唤醒。
- **oracle -k 5 已于 18:04:54–18:12 跑完 = 2/5**（✅ adaptive-rejection-sampler / break-filter-js-from-html；❌ bn-fit-modify / build-cython-ext / build-pmars = **构建期拉包失败**）。⇒ 按任务书「oracle 必须 5/5」，**不得进 7×5 / 7×89**。
- **数据集已本地齐全**：`~/terminal-bench/` 89 个 `task.toml`，registry 13.6MB → **跑评测不需要 GitHub 认证**（OAuth 三次兑换失败均为 code/verifier 不匹配，已放弃）。
- **docker 组**：cline/loop **有**（gid 122）；**relay 没有** → RUN_ID 117 的 harbor 报 `Docker daemon is not running`。
- 🔴 **事故（我的责任）**：RUN_ID 117 的重启脚本把启动命令与 `pkill -f "[o]ps_relay.sh"` 放在同一条命令行 → **自匹配，把中继连同执行重启的 shell 一起杀掉**，RUN_ID 118 未被拾取。教训：**重启必须把启动命令写进脚本文件，再用单独一次调用执行**。
- 已下发 `run/BAIZE_HARNESS_TASK.md` 顶部 **P0 抢修块**（32,759B）：① 安全重启中继；② 用 `/tmp/tb_oracle_cfg_117.yaml`（`environment.extra_docker_compose=/tmp/network-host-overlay.yml`）重跑 3 个失败任务；③ 3/3 后再跑全量 oracle -k 5 到 5/5；**5/5 前禁止 pilot/全量**。原「Docker 权限」「清 /tmp」两块归档为「归档块 M」。
- 详见 `daily-memories/2026-10-17.md`。

### 🔧 pretrain 代修 ops 中继（用户令）
- 用户令：「pretrain 在 .29，现在空闲，让它去修复 ops 中继。」
- 已下发 `run/BAIZE_PRETRAIN_2B_TASK.md` 顶部 **P0 块**：把 4 行重启步骤写进 `/tmp/fix_relay_2040.sh` 再执行（`pgrep -f 'bash [o]ps_relay[.]sh' | xargs -r kill` → sleep → `setsid bash ops_relay.sh …` → 复查），**禁止在命令行里组合 pkill 与启动**（上次即因此自匹配误杀）。
- 判据：至少 1 个 `bash ops_relay.sh` 进程 + 日志无 error；**红线：不碰训练/torchrun/loop**。
- 12:2x「停 `.12` 迁 `.29`」原文归档为「归档块 N」，任务书 **32,587B → 30,284B**；仍生效要点（`.29` 固定 pretrain、不换机、已在跑不重启）保留一行指针。





### 🧪 harness 新指令：Terminal-Bench 2.0 · 7 harness × 89 task · kimi-k2.6-cloud
- 用户令：「harness：测完 glm53 7×300之后，开始基于kimi-k2.6做terminalbench的7 harness横评。」
- 已下发 `run/BAIZE_HARNESS_TASK.md` **顶部（T1，最高优先；T0 仍是 glm53 收口）**：T0 = pi 剩 32 条跑完 → glm53 最终版报告（全量 2100 配对 McNemar）→ push；T1 = 收口前只做纯 CPU/IO 前置（uv/Harbor/Docker、dataset、oracle 5×、适配器骨架，零 API）；T2 = 定稿后立即启动正式横评；🚫 不得为赶 T2 kill/降速 pi。
- 口径：TB2.0（arXiv:2601.11868，89 tasks，`terminal-bench@2.0`）· 7 harness（cline-patched/codex/hermes/opencode/claude-code/deepseek-harness/pi）· kimi-k2.6-cloud @ `/cloud/v1` · 7×89=623 · 每 harness 内串行 · 三列 resolved/failed/infra-or-quota · Wilson 95% CI + McNemar 精确检验 · 交付中文 HTML + 逐任务 JSON + 7 个 Harbor 适配器。
- 前置红线：**oracle 5/5** + **实拉 1 个 TB 任务镜像**；Docker/内网阻断 ⇒ 立即记 blocker（完整报错+已试命令），**不许伪造、不许空转**。
- 任务书同步瘦身：三条已闭块原文移入 `run/ARCHIVE_OPERATOR_HARNESS.md`（10-14 glm53 两连发 + 10-13 P1 剩余项）；`BAIZE_HARNESS_TASK.md` 31,372B→**31,212B（30.5KB ✓）**。
- 详见 `daily-memories/2026-10-17.md`。

### 📄 vision 新指令：ArmA 中文报告 + 归档 + open_clip × AIMv2-style 兼容性评估
- 用户令：「vision：把 ArmA 结果写成中文报告并归档。问题：open_clip 接口和AIMv2-style不能兼容吗？」
- 已下发 `run/BAIZE_VISION_TASK.md` 顶部：① 报告 `reports/report_vision_armA_openclip_result_zh.html`（ArmA ProtB **lp 58.03±0.02% / 5-NN 53.98%**；vs ④-4ep 67.05/42.35；**非单变量对照**必须声明）；② 归档 `EXPERIMENTS_VISION.md` §ArmA + `MEMORY_VISION.md`；③ 附录 A 回答兼容性；④ ArmB 代码（open_clip ViT-B/16 + 我们的 AIMv2-style，只变目标；预注册 lp ≥58.03、≥61.0% 且 5-NN ≥48.98% 接受）；⑤ **训练排队**（`.12` 8×H100 被 80B decay 全占，本轮只写代码/单测）。
- **兼容性口径（我已核实代码）**：**模型/推理接口兼容**（ArmA 本身就是 open_clip 模型 + ClipLoss，`armA_openclip_train.py:286-287`；导出只用 `encode_image`）；**open_clip 自带损失/训练循环不兼容**（无 patch 级目标、无 mask 采样），需自定义 `PatchPredictor`(≈0.66M)+patch tokens+loss/训练步，≈1–2 人日 CPU；predictor 不进推理图，不影响导出。
- 概念区分：官方 AIMv2=多模态自回归（`aimv2_ar`+decoder）；我们的 AIMv2-style=InfoNCE+masked patch MSE（`r9_train.py`）。
- 任务书瘦身：10-16 21:3x 效率块归档（30,719B→26,768B→插入后 31,830B=31.1KB ✓）。
- 详见 `daily-memories/2026-10-17.md`。

### 🎯 recruit 口径纠正：全职 = 助理研究员（1–5 年）+ 亮点门槛
- 用户令：「今天推的全职很多 10+ 年工作经验。我不是说了 1-5 年嘛，这是助理研究员岗位。而且也不出色，学校和工作起码要有点亮点吧。」
- **根因（运维口径错误）**：10-14(c) 把「3 年+」下调为「1 年+」时**漏了上限**；10-17 06:00 的 5 封推荐里 **4 人 10 年+**（洪晟彦/沈先生/张先生/李合敏），曲先生 3 年。
- 已改权威 JD `run/recruit/hr/JD-AI-EDA-研究员-DRAM.md`：标题→**助理研究员**；经验→**1–5 年（>5 年不推进）**；新增「**亮点要求**（学校或工作至少一项，带证据）」节 + 岗位定位提醒；派生判定 §2/§4 同步。
- 短名单 `run/recruit/全职短名单-AI+EDA研究员_2026-10-13.md`：标题→助理研究员 + 顶部 **2026-10-17 更正头**（R23「8 人达标」作废重判）。
- 任务书 `run/WATCH_RECRUIT_TASK.md` 顶部新块：下一唤醒**先重筛 61 会话 + 候选表**，产出 §十一 R24；已发 5 封不撤回、不补解释，台账标 `overqualified` 不再推进；18:00 **不发全职邮件**（守早 6 排期），新达标者留到下一 06:00；18:00 实习专场照常。
- 任务书体积：32,537B→（插入 4KB）36,397B→归档 10-16 排期块（块 K）后 **34,972B（34.2KB）**；<40KB 红线，agent 下轮按规程继续自滚到 ≤32KB。

### 🚀 vision 新指令：启动 ArmB（open_clip ViT-B/16 + AIMv2-style · 全量 8000 GPIC · 3 epoch）
- 用户令：「目标=AIMv2-style；数据=全量 8000 tar GPIC + CC12M + Amshaker；塔=open_clip ViT-B/16 86.2M；warmup=2000；LR=1e-3, min_lr=1e-4；GBS=8192, MBS=512（OOM→4096/256）；epoch=3；给 ETA；使用 open_clip 接口（便于 LLaVA-OneVision + lmms-eval）。」
- 已下发 `run/BAIZE_VISION_TASK.md` 顶部（最高优先）：AIMv2-style = InfoNCE(1.0) + masked patch MSE(1.0, mask 0.6)；数据 ≈117.25M 对 ×3 epoch；GBS8192 → **≈42,940 步**（14,313/epoch），回退 4096 → ≈85,876 步；save every 10k。
- **ETA**：ArmA 实测 6,902 samples/s → 预计 6,900–7,300 → **纯训练 13.4–14.2h**；+启动/ckpt/ProtB 1–2h ⇒ **总 15–16.5h**（110–120 GPU·h）。情景① `.29` 空：代码 1–2h 后起，约 **10-18 04:00–06:30** 完成；② 等 `.12`（pretrain 10-20 02:30 结束）→ **10-20 17:00–19:00** 完成。
- **open_clip 硬要求**：必须 `create_model_and_transforms('ViT-B-16')`；predictor 只为辅助头并剥离导出；patch tokens 必须复用同一次前向（禁止二次 forward）；新增 `mllm_bridge/open_clip_vitb16_768.py`（`baize-vitb16-768`, `encode_image`→[B,196,768]）+ `export_for_llava_ov.py` + CPU 单测。
- **资源**：`.12` 8×H100 被 pretrain 80B decay 全占 ⇒ **不 kill/不抢**；先探 `.29`（ssh nvidia-smi），空则立即起，否则写 `run_armB_when_free.sh` 轮询 `.12` 自动起。已在 `run/GPU29_ALLOC.md` 登记申请行。
- 任务书瘦身：归档 10-16 ArmA 块 + 10-13~10-16 历史指针，31,987B→**24,182B（23.6KB ✓）**。

### 🖥️ 跨机重排（用户直令）：pretrain → `.29`，vision → `.12`
- 用户令：「为什么 pretrain 占用 .12 呢？把它kill掉。pretrain用.29，vision用.12」
- **根因**：crash5/6 是 `.12` 本地 `emerging_optimizers 0.5.0a0` 与 Megatron API 不匹配；为用该本地安装把 80B decay 从 `.29` 迁到 `.12`——**临时兼容性迁机，不是永久分卡**。
- 已下发 `run/BAIZE_PRETRAIN_2B_TASK.md` 顶部：**先确认最新 ckpt（latest.pt@500 或 step_532000）→ SIGTERM→KILL 仅本任务 PID → 验证 `.12` 8 卡 0MiB → 写 `GPU12_RELEASED=1` → 到 `.29` preflight（版本/签名）→ `--resume` 起 v2**；配方不变；`.12` 不得再占。
- 已下发 `run/BAIZE_VISION_TASK.md` 顶部：`.12` 8 卡 = vision 独占；起训前查 pretrain 进程，若 ≤10min 未自停，**用户已授权 kill（仅此一次，只杀 `baize_xmodel25_decay*`）**；释放后立即按 ArmB 配方起训。不再探 `.29`/不再排队。
- 账本：`GPU29_ALLOC.md` +pretrain 8卡 ~64h；`GPU12_ALLOC.md` +vision 8卡 ~15–16.5h（均标「用户直令·已批准」）。
- **ETA**：pretrain 若从 ckpt@500 resume → 19,480 步 ×11.9s ≈ **64.4h** → 约 **10-20 05:00** 完成；若只能从 step_532000 重起 → 损失 ≤500 步（≈1.65h）。vision ArmB：代码 1–2h + 训练 13.4–14.2h + 收尾 1–2h ⇒ **10-18 04:00–06:30**。
- ⚠️ 状态矛盾：pretrain 记忆写 10:30 起 `.12` 占满，但 vision #130 在 11:1x 实测 `.12` 8 卡 0MiB、且 pretrain 10:38 后无提交——执行时以 `nvidia-smi` 原文为准；若 pretrain 已死，kill 为 no-op。

### ⚔️ 用户追加令（12:4x）：vision 立即 kill `.12` pretrain + ArmB 改 4 epoch；pretrain `.29` 重启、服务器固定
- 用户令：「让 vision 把 .12 pretrain 的训练进程杀掉，开始 vision 的工作。如果 3 个 epoch 只需 14h，那就预约 4 个 epoch，训练完了评测 ProtB。让 pretrain 在 .29 重启训练，以后不许随意换服务器。有问题上报或者自己解决。训练重启后上报 ETA。」
- **vision**：新块置顶（取代 12:2x 的「等 ≤10min」）——**立即 kill**：先记录 pretrain `latest.pt` 与 PID，`TERM`→60s→`KILL`，只杀 `baize_xmodel25_decay*`；8 卡 0MiB 后按 ArmB 起训。**epoch 3→4**：N≈117.25M×4=469.0M samples；GBS8192≈**57,250 步**（回退 4096≈114,500）；warmup/LR/MBS/AIMv2 不变。**ETA：纯训练 17.9–18.9h + 收尾 1–2h ⇒ 19–21h（143–151 GPU·h）**；13:30 起 → **10-18 08:30–10:30** 完成。训完立即 ProtB（同 armA 口径，输出 `armB_protb_vitb16_224_results.json`）。
- **pretrain**：追加第 ⑤ 条——`.29` 重启是硬指令，从最新 ckpt resume；**重启后 ≤30min 报 ETA**（机器/PID/resume step/s-per-step/tok/s/首 ckpt）；**服务器固定** `.29`=pretrain、`.12`=vision，未经明确批准不得再换机；故障就地修，修不了上报 blocker+选项。若 `.29` v2 compile 不生效（~184K tok/s / ~20s/step），按实测报（可能 ~108h）。
- **ETA**：pretrain 从 ckpt@500 → 19,480×11.9s≈64.4h → 约 10-20 05:00；若从 step_532000 → 66.0h → 约 10-20 06:40；若 compile 失效 → ~108h。
- 账本：`GPU12_ALLOC` 追加 4 epoch 行（~19–21h，取代 3 epoch 行）。

### 🩺 11:5x 各线巡检（用户令：查进展 + pretrain loop 挂了才用 ops 中继）
- **pretrain：loop 活着，无需 ops 中继**。`MEMORY_PRETRAIN_2B.md`（11:44 更新）实测：`.29` 08:44 起健康 RUNNING，step~860 @11:36，loss 2.03，**296.8K tok/s**，8 卡 100%/51.7GB，0 crash；**`.12` 已于 11:37 释放**（`GPU12_RELEASED=1`，0 compute apps）。#488 明确「停 .12 迁 .29」目标已达成、**不重启**。
- **已修正误伤指令**：pretrain 任务书 12:2x 块加「先查状态再动手」——`.29` 健康则在跑则不重启（重启会丢 860 步≈2.8h），只报 ETA；仅当挂了才按 ②③ 重启。
- **vision**：MEMORY 仍停在 11:13（wake #130，WAITING=1），11:12 后无新提交；按 loop 30min 节奏，下次唤醒 ~12:12，会读到 12:0x/12:4x 指令。`.12` 已空 ⇒ kill 为 no-op，可直接起 ArmB（但代码尚未写，预计 1–2h）。
- **data**：2 路下载健康（en_v1_4 70.1% / WebMix 3433 par，10:52 巡检）。
- **harness**：pi 268/300（2068/2100，562 resolved），ETA 16:00–20:30。
- **zhulong**：B.deepseek-v4-flash 复测 r1 跑中（09:17 起，PID 1721558），预计 12–13 点收。
- **news/research/recruit**：下一唤醒 18:00；recruit 18:00 先按新口径重筛（1–5 年 + 亮点）。
- **video**：EP03《种子》成片完成（52/52，267.97s），下一步 EP04。
- **ops 中继**：`last_run_id=110`、outbox 最后回执 **10-16 19:01** ⇒ 疑似停摆；已下发 **RUN_ID 111 只读探活**（loops + 双机 GPU + 训练进程），不启动/不 kill。若 111 无回执 ⇒ 中继也需重启（本机无法 SSH，需服务器侧拉起）。


## 🆕 最近操作（2026-10-16）

### 🚀 80B Decay 训练已在 .29 启动（Xmodel-2.5 step_532000 + Muon）
- 目标：用 BaiZe 自定义数据配比 + Muon optimizer 在 Xmodel-2.5 稳定末ckpt 上跑 80B decay，超越 Xmodel-2.5 final（CS8=65.40% / CX=32.90%）。
- 模型：1.35B params（2.70GB BF16），非 2B。checkpoint = `step_532000`。
- 配置：SEQ=4096, GBS=960, MBS=2, ITERS=20346（80B / 3.932M = 20346 步）, WARMUP=100, LR=1.67e-3 → 1e-5（WSD exponential）, SAVE_INTERVAL=2000。
- Muon BF16 兼容性修复：monkey-patch `newton_schulz` 接受 BF16 梯度，内部转 FP32 做 NS 正交化，结果转回 BF16（原 `p.grad = p.grad.float()` 会 TypeError）。
- Smoke test 通过：30/100 步完成，loss 11.76→2.18（快速下降正常），GPU 58.5GB/80GB，util 97-100%，~182K tok/s。
- 全量训练已启动：PID 2080678（torchrun），8 workers（PID 2082634-2082644），port 29815。输出 = `xmodel25_baize_80b_decay`。
- 预计耗时：~4.7 天（20346 步 × ~20s/步）。首次 ckpt 在 step 2000（~11h）。
- 脚本：`run/baize_xmodel25_decay.sh` + `run/baize_xmodel25_decay_train.py`。
- 日志：`/tmp/baize_xmodel25_decay_train.log`（注意：因第二次启动 EADDRINUSE 竞争产生 sparse file 空洞，读 log 需用 `cat /proc/<worker_pid>/fd/1 | strings | grep '^\[step'`）。
- commit 前缀 `pretrain decay80b:`。详见 `daily-memories/2026-10-16.md`。

## 🆕 最近操作（2026-10-14）

### 📋 pretrain 正式训练计划【v4 重做】（用户直令 · 10-14 晚）
- 用户逐条质问 v3 `reports/report_pretrain_formal_train_plan.html`（判**质量不合格**）：① 密度 tok/byte 0.0657–0.4977 为何差这么大；② 分词 `.bin` 里 1 token 几个字节（bin 字节/每 token 字节 = token 数）；③ 为何擅自断言「训 2,232B 需 ~52 天不现实」——**现实与否不由 agent 定**；④ 要**逐源准确 token 数**；⑤ **全量训练配比 + 每源平均采样次数**；⑥ 设 **D={100B,200B,400B,800B,1.6T,3.2T}**，预估 **8 常识均分**（arc_c/arc_e/boolq/hellaswag/obqa/piqa/sciq/winogrande）与 **6 复杂均分**（gsm8k/math/bbh/mmlu/humaneval/mbpp）。
- 已下发 `run/BAIZE_PRETRAIN_2B_TASK.md` 顶（最高优先）：产 **v4** 覆盖原文件 —— ① 逐源 token 从**分词后 .bin/.idx 实测**（先核实 dtype：vocab=129,281>65,536 ⇒ 大概率 4B，须以源码/文件头为证）；② **密度归因**（压缩态密度≠文本密度：du -sb 分母是压缩字节，混入压缩率+语言两因素）；③ **删主观判断**；④ 全量配比 + 采样次数表；⑤ **D 扫描 + 8/6 集能力预估**（用已有 ckpt 实测分数拟合 scaling + **web search** 借公开 scaling law，分「实测/拟合/外推」三档，3200B 需重复采样须声明）；⑥ 自包含 HTML + scaling 曲线图 + v3→v4 修订说明 + 诚实条款。纪律：🚫 不占 GPU · 每数可溯源 · commit `pretrain plan:`。详见 `daily-memories/2026-10-14.md`。

### ▶️ data 恢复全部 4 路下载（用户直令 · 10-14 晚）
- 用户令：「**data 数据下载 resume**。」⇒ 已下发 `run/BAIZE_DATA_TASK.md` 顶（最高优先）：**恢复 `en_v1_4` + `WebMix-38M` + `wit_base` + `InternVL-SA1B` 共 4 路**（**断点续传**，`.incomplete` 已留）；⚠️ **85M 维持暂停**（10-13 令，除非用户另指）。
- 要点：恢复前 `df -h`/`ls` 核余量与 `.incomplete`；`setsid` + 正确 PATH（防 `env: hf No such file`）；**「死/僵/速率趋零/PID 死 ⇒ 立即 kill+restart」**看护；落盘白名单不变（`en_v1_4` 文本语料按停前 `/nas_train` 原路径续传 = 既有例外）；**错峰** `.29` pretrain / `.12` vision。
- 停前基线：`en_v1_4` 32,995/56,461 ≈ **58.4%**（3.0T）· `WebMix` 78 parquet/59G · `wit` 79 parquet/70G · `InternVL` 303 tar/227G。
- commit 前缀 `data dl:`。详见 `daily-memories/2026-10-14.md`。

### 🔧 vision【放行并行】ArmC 期间先写 BaiZe ViT → HF wrapper + 自定义 LLaVA modeling（用户直令 · 10-14 晚）
- 用户拍板（回复「关注/风险」决策点）：**现在就并行写 ViT wrapper**（纯 CPU、不占 GPU）。已下发 `run/BAIZE_VISION_TASK.md` 顶（最高优先 · 但仍低于 ArmC 训练/评测监控）：① **BaiZe vision tower HF wrapper**（`run/vision/mllm_bridge/` — 包 `models.py:OpenVision2` 为 HF `PreTrainedModel`，`model_type: baize_vision` + `config.json`；输出 patch-level `[B,196,1024]`、跳过 `ReadoutHead`；从 ④-4ep ckpt `{'vision': sd}` 载入并 `strict=True` 打印 matched/missing/unexpected）；② **自定义 LLaVA modeling**（基于 `modeling_llavaonevision1_5.py`；projector=2 层 MLP 1024→2560；跳过 spatial merge、196 tokens 直出；Stage-1 固定 224）；③ **CPU 单测**（载入通过 / 形状 `[1,196,1024]` / 与原始 `OpenVision2.forward(return_patch=True)` 逐元素 allclose / projector `[1,196,1024]→[1,196,2560]`）；④ `README.md` 接口与 ms-swift 接入 + GPU smoke 前置清单；报告 `reports/report_vision_mllm_bridge_zh.html`。**纪律** = 🚫 不打断 ArmC 训练/eval chain（PID 3698490）· **零 GPU** · CPU/IO 与 ArmC NFS 冲突时让路 · commit 前缀 `vision mllm-bridge:` · 任务书自滚。依据 = 可行性报告 §4.3/§7（🔴 R1 最大工程量）+ §8.2/§8.3（#3#4 纯 CPU 可并行）。详见 `daily-memories/2026-10-14.md`。

### 📋 五项运维指令下发（用户直令 · 10-13 晚）
- **① data · HF 图文对数据集调研**（`run/BAIZE_DATA_TASK.md` 顶）：web search 为 **vision encoder 训练**找 HuggingFace **图文对数据集**，**硬口径 = image 带 bytes（非 url）**（HF `Image` feature / `datasets-server` features 为证）→ 中文 HTML `report_data_hf_imagetext_datasets_zh.html`；🚫 只调研不下数据、不打断 en_v1_4 / 85M。
- **② vision · 合并三数据集实验计划**（`run/BAIZE_VISION_TASK.md` 顶）：中文 HTML 计划，**GPIC + CC12M + Amshaker 合并 · GBS/MBS ×4 · LR ×2**，预估 **24h 预算内 N epoch 时间 + ProtB**；🚫 只出计划不起训。
- **③ pretrain · 正式训练计划书【重做】**（`run/BAIZE_PRETRAIN_2B_TASK.md` 顶）：用户判 v1 **不合格**（**仍假定总数据仅 100B**）→ 须按 **MiniCPM5 全量口径**回答：**总数据量 / 逐源 token / pretrain:decay 配比 / 总训练 token / 双机 16 卡墙钟**；数字可溯源，加「v1→v2 修订说明」。
- **④ harness · 通过率为何这么低**（`run/BAIZE_HARNESS_TASK.md` 顶）：web 外部对照 + **轨迹细析** → 判「**合理否 / 能力 vs 环境**」+ **提升机会点按预计增益从高到低排序** → 中文 HTML `report_harness_why_low_passrate_zh.html`。
- **⑤ recruit · 质询「今天为何一封简历邮件都没发」**（`doc/personal-watch/run/WATCH_RECRUIT_TASK.md` 顶）：令**先如实解释 06:00/18:00 两轮 + 0 封根因**，再**修复吞吐**（补核 publication / 补齐下载 / 用足 ≤20–30 上限 / 达标当轮即发）。**git 侧核**：本日仅第 16 轮（06:0x），0 达标 → 0 邮件。
- **流水**：见 `daily-memories/2026-10-13.md`。

### 📋 招聘口径变更（用户直令 · 10-13 晚）
- **两个 JD 均取消「四大 EDA 顶会（ICCAD/DAC/DATE/ASP-DAC）」门槛**：`研究员` 硬门槛【取消】· `实习` 优先项【移除】；**AI 顶会维持原状**（两岗均为「优先」，非硬门槛）；候选人若有 EDA 四大顶会仅作**加分**、**不再作达标条件**。
- 已改**源 JD**（`doc/personal-watch/run/recruit/hr/JD-AI-EDA-研究员-DRAM.md` §2+派生§2 · `JD-AI-EDA-实习生-DRAM.md` §2+派生§3）并在 `WATCH_RECRUIT_TASK.md` 顶下发令（令 agent 同步 `hr/MEMORY.md` §一/§二.1 + 按新口径重判候选表 + 补发达标推荐）。
- **📮 每日下限**（同日用户令）：「**每天优中选优，至少发几个简历过来。年底还是要招人。**」⇒ **每天至少推 3–5 份**简历 → `paul.liu@cxmt.com`（附 PDF）；**「优中选优」= 排序取 Top-N，非「达标才发」**；**不得 0 封**；18:00 收盘轮补足 ≥3。已下发 `WATCH_RECRUIT_TASK.md` 顶。

### 📋 pretrain 计划书【v3 再重做】（用户直令 · 10-13 晚）
- 用户否决 v2：**「300B」无出处、且与实盘「2,015B」自相矛盾**；**MiniCPM5 无独立训练论文**（`arXiv 2602.09003` 实为清华 UltraData **数据管理框架**论文，非 MiniCPM5 模型论文；300B 出自 **CSDN 二级源**）。
- 令 **v3**：**严格按「已下载 + 正在下载」实盘盘点**（`du` / 文件数）→ 换算 token → **总数 = 训练量**；🚫 禁引论文/CSDN 数字；每个 token 数须附**盘点命令**。已下发 `run/BAIZE_PRETRAIN_2B_TASK.md` 顶。

### 📋 vision 放行执行 + data 换下载目标（用户直令 · 10-13 晚）
- **vision**：**外部编码器 ProtB 做完后 → 执行「合并三数据集实验」**（GPIC+CC12M+Amshaker · **GBS/MBS ×4 · LR ×2** · **24h ≈3 epoch**）⇒ **放行起训**（覆盖前令「只出计划、不起训」）。已下发 `run/BAIZE_VISION_TASK.md` 顶。
- **data**：**暂停 85M**（保留已下 ~69.2%，不删）+ 下载 **HF 图文对 TOP-5 中「未下载」的 4 个**（① `MVRL/WebMix-38M` ② `VedaLabs/wit_base` ④ `hanlincs/InternVL-SA1B-Caption-WebDataset` ⑤ `HuggingFaceM4/the_cauldron`；③ `BLIP3o/...` **已在本地**跳過）⇒ **落 `/nas_inference/app.e0031982/datasets/` 或 `/nas_user/<user>/datasets/`，🚫 不放 `/nas_train`**。已下发 `run/BAIZE_DATA_TASK.md` 顶。

### 📋 任务书去粗体瘦身（用户直令 · 10-13 晚）
- 用户：「现在任务书里 ** 太多，把 ** 删掉就能大幅瘦身。」⇒ 已删除 **BaiZe 7 + personal-watch 4 = 11 份任务书**里的**全部 `**` 粗体标记**（**行内代码 / 代码块内的一律保留**），**共 -13,760 字符 ≈ -13.4KB**；**纯格式化，不改任何指令语义**（git 显示 1700 行改动、增删平衡）。
- ⚠️ **ZhuLong_DAC2027 的任务书**（`ZHULONG_TASK.md` 等）**未动**（另一项目线；如需处理请示）。

### 📋 vision 数据量口径更正（用户直令 · 10-13 晚）
- 用户质疑 `report_vision_merge3ds_bs4_lr2_plan_zh.html` 里 GPIC「~80–85M」太低（应 100M+）。**核实 = 用户对**：报告用了 **6233-tar 时代旧值**（合计 95.8M），而快照实为 **7437 GPIC tar**（`run/vision/data_snapshot_20261009.txt` 已核 **7437 行**）→ GPIC ≈ **93–94M**（全量 8000 tar = **101.1M**）→ 三集合计 ≈ **111M（快照）/ 118.1M（全量）**。报告**权重列(84%)与对数列(80-85M)自相矛盾**。
- 已下发 `run/BAIZE_VISION_TASK.md` 顶：令按**快照实盘**重算 GPIC/合计/权重/epoch 定义/步数/24h-epoch/ProtB 外推，每数附盘点命令，并加 EXPERIMENTS 口径订正。

### 📐 vision LR 缩放定则（用户直令 · 10-13 晚）
- 用户令：「搜一下 GBS ×4 时 LR 应该怎么变，不要胡咧咧。」→ 运维查证（带出处）：
  - **线性规则 = ×4**：Goyal 2017 (arXiv:1706.02677)「hyper-parameter-free linear scaling rule」+ warmup，batch 到 8192 无精度损失。
  - **B ∝ LR（含 Adam）**：Smith 2017 (arXiv:1711.00489)。
  - **次线性 √ = ×2**：工程惯例，**未取到一手出处** → 不得当权威引。
  - **实证必重调**：Shallue 2019 (JMLR 20 · arXiv:1811.03600) + Google Playbook；critical batch size（McCandlish 2018, arXiv:1812.06162）。
  - **对比学习**：SimCLR (arXiv:2002.05709) 「benefits from larger batch + more steps」。
- 已下发 `run/BAIZE_VISION_TASK.md` 顶：**默认 LR ×4（5e-4→2e-3）配 warmup**；**做 3 臂 LR 扫描 {×2, ×3, ×4} 取 ProtB 最优**；§3 改引文献；无出处的规则禁写「权威」。

## 🆕 最近操作（2026-10-12）

### 📋 七项运维指令下发（用户直令 · 10-12 晚）
- **① harness 深挖令**（`fea9b643`·`afa06b20`）：7×300 **module 失败 21.5% vs wrong-fix 48%（纠正旧 83%）** + 根因（**沙箱网络策略挡 `pip install -e .`**）+ **web 对照** → `report_harness_eval_rootcause.html`；**已令逐项修复 P0 + 重跑受影响 case**。🚫 不占 GPU。
- **② vision OV-1.5 复现计划**（`42d8c075`）：**基模 Qwen3.5-4B + ms-swift**，数据齐（除 85M），估 H100×8 → `report_vision_llava_ov15_repro_plan.html`（已交付）。
- **③ video 下一章**（`1a522061`）：暖阳后做 `13_外骨骼`；旧原型 legacy TTS ⇒ 重做（去 TTS）。✅ 已开跑。
- **④ video 推翻重做**（`9d3559cb`·`34ecbafa`）：**角色镜弃「T2I 首帧→I2V」⇒ 一律走 stem_fest 标准 `r2v`**；**现有 T2I→I2V 成果（18_暖阳 / 13_外骨骼）删除重做**；改 `PIPELINE.md`/`PLAYBOOK §3`。
- **⑤ recruit 人数上限 ×10**（`9606d8d9`）：`≤2–3 人/批` ⇒ **`≤20–30 人/批`**。
- **⑥ research 邮件**（`07f47211`·`b424233f`·`c1d0d90b`）：**每日论文日报**（选 3–5 篇下 PDF 发 `paul.liu@cxmt.com`，每天 1 封，`research/pdf/` 不入 git）；作者信**中文（中国人）+ 免审直发**。
- **⑦ recruit 第 2 个 JD（全职·研究员）**（`b6d48f6f`）：用户「两个 JD（实习 + 助研）」→ 录入 `JD-AI-EDA-研究员-DRAM.md`；令按 **EDA 四大顶会（硬门槛）** 筛**社招池**出**全职短名单**。
- **流水**：见 `daily-memories/2026-10-12.md`。

WAITING: 0

> ⚠️ **本文件在项目根**（`doc/BaiZe-ISEDA2027/`），是**运维侧**（指挥 4 条线的那个"我"）的状态文件。
> **不属于任何 agent 线** —— 4 条线的记忆在 `run/` 下：`MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md` / `MEMORY_VISION.md` / `MEMORY_HARNESS.md`。
> 日流水在根目录 `daily-memories/`（**不要**与 `run/daily-memories*/` 混）。
> 纪律：**`WAITING:` 只在顶部出现一次**；**≤32KB**，超限滚动到 `daily-memories/`。

---

## 0. 我是谁 / 我的角色

- 我是本项目 `doc/BaiZe-ISEDA2027` 的**外部运维**：**不登录训练机**。
- **下达通道** = 各任务书的 `## 🔧 运维指令区（OPERATOR NOTES）`（**改文件 + git commit/push**）。
- **查看通道** = 读各线的 `run/MEMORY_*.md` 顶部「进度快照」/「运维问答」+ `run/` 产物（`git pull` 即可，**不登录服务器**）。
- 我指挥的 4 条线：**pretrain**（`10.239.2.29`）· **data**（`.12`）· **vision**（`.12`）· **harness**（`.29`）。另有 **ops relay**（RUN_ID 机制，见 `run/ops/`）。

---

## 1. 每次「醒来」的固定动作（SOP）

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`
   （远端推进很快——各 agent 每次唤醒都可能 push；**不 pull 直接改会冲突**）。
2. **读本文件**：尤其 §3 在途任务 / §4 待拍板 / §5 铁律。
3. **读 4 条线状态**：各 `run/MEMORY_*.md` 顶部 + `git log --oneline -20` + `run/ops/.last_run_id`。
4. **处理回写**：有 agent 产物/答复 → 读、核、必要时答复（写进对应任务书运维指令区或该线「运维问答」）。
5. **下发新任务**：在对应任务书运维指令区加 **带日期的 block**（**越靠前越优先**；老块不改，留作历史）。
6. **提交**：`git add` **只加自己动的文件** → `commit` → `push`。**不要 `git add -A`**。
7. **回写本文件 + 当日 `daily-memories/<date>.md`**。

---

## 2. 通讯协议 / 接口（关键认知）

- **接口 = 任务书的「运维指令区」**，四条线**现在都有**：
  - `run/BAIZE_PRETRAIN_2B_TASK.md` · `run/BAIZE_DATA_TASK.md` · `run/BAIZE_VISION_TASK.md` · `run/BAIZE_HARNESS_TASK.md`
  - ⚠️ **pretrain / vision 的任务书原本没有该区，是 2026-10-03 由运维补上的**。
- **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；**新块放前面**，写清 **优先级 / 顺序 / 判据 / 铁律**。
- **各线回写位置**：`run/MEMORY_*.md`（状态头 + 进度快照 + 运维问答 + 流水）、`run/daily-memories*/`、`run/EXPERIMENTS_*.md`、各线产物目录。
- **ops relay**：还可经 `run/ops/inbox.md` 下 RUN_ID 命令（⚠️ **只执行第一个 ```bash 块**；下发须把新块放最前、旧块降级为 ```text、RUN_ID +1）。

---

## 3. 在途任务（截至 2026-10-08）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **pretrain** | 🆕 **10-09：队列已清空 → 已下发「提 3 个实验 idea」征询**。R3 BO ✅ 100/100（best=#8 score=0.4032）· R3 报告 ✅（`report_pretrain_r3_data_mix.html`）· P-8 PREP ✅ · **T3 ✅ 完成**（**P-8 最优配置 = `TP1·MBS2·bf16 = 249K tok/s`**；FP8 在 TP1 s=0.915 不能提速；recompute 对 SSM 无效）。**.29 8×H100 全空**. 已令：**纯写作零 GPU，提 3 个实验 idea 按价值排序 + 「是否直接起 P-8」建议** | `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` · `report_pretrain_r3_data_mix.html` · `report_pretrain_t3_train_speed_shortlist.html` | 🟢 `.cline_pretrain`；**P-8 暂缓令（10-02）仍未撤** |
| **vision** | 🟧 **AIMv2 缩放对比实验进行中（用户直令 10-08⑤ + 同日⑥ E2 变更）**：**E1 = 同族 OV2 w512/d30 126.78M** vs **E2 = 同族 w768/d30 284.54M（2.24×，只差宽度）**，均 224/p16、从零、同 AIMv2 objective + 同 94.9M + 同 1 epoch；主指标 IN-1k **lp Protocol B**（3 seeds）；判据 Δlp ±1.5pp。**agent 已完成**：smoke（E1 4697 / 官方臂 2347 img/s）· 登记 `.12` 8 卡 · `models.py` 加 width/depth override · 预注册初稿。✅ **收官（10-10 21:00）**：**Δlp（ProtB）= +0.17pp → 不可分辨**（旧「−5.59pp / Bigger is WORSE」＝ **schedule 伪影**，已盖棺）。E1fair ProtB=62.34±0.01%/ProtA=49.70%；E2fair ProtB=62.51±0.04%/ProtA=49.53%。**10-10 晚已下发「出 `report_vision_scaling_fair.html` 独立成果报告」+「下一步工作建议」征询**（均用户直令）；**成果报告已交付**（27KB）。`.12` 8 卡已释放。<br>🧪 **10-10 晚再下发「三变体实验」**（用户直令 · 最高优先）：以 **`E1fair`(w512)** 为 baseline（**不重跑**），**次序已定**（10-10 晚用户调整）：**① AdamW→Muon**（第一优先；ⓘ vision=**纯 PyTorch DDP**，无 `dist_muon` 开关；用上游 **`emerging_optimizers`**，照 **pretrain** 超参 momentum0.95/nesterov/ns5、同 LR）→ **② 全量数据 = `GPIC 全量`+`CC12M`+`Amshaker`**（**steps 按数据量算，可 >187,101**；⚠️ **数据+步数同变须披露**，不得称「纯数据消融」）→ **③ 分辨率 224→336：⏸ 暂缓（明天再说）**；判据 **Δlp vs `E1fair`（|Δ|<1.5pp 不可分辨）**。<br>🧭 **10-10 晚再下发「外部评审回应」**（外部质疑 ProtB 62.34% 偏低，经两轮辨析 → 收**回参照系**）：**③ 口径修订（标 "BaiZe internal protocol (ProtB)"、声明不可与外部同表、清理 CLIP/MAE/DINOv2 比较）→ ① 同模型 zs（做同模型 lp↔zs）→ ② 更强 probe 对照（k-NN/长步数/wd）→ ④ epoch 缩放（先 2 ep，判「预算不足 vs 特征问题」）**；③①② 零/轻 GPU 立即可做，④ 与变体实验统一排 `.12` 档期。 | `report_10_09_vision_overnight.html`（FINAL·§1–§15）· `report_vision_scaling_fair.html`（**已交付**）· `EXPERIMENTS_VISION.md §8.2` | 🟢 `.cline_vision`；**变体实验 + 外部评审回应（③①②④）待执行** |
| **data** | 🆕 **10-10 傍晚已下发「巡检并发下载」令**（用户直令）：data 线当前**同时跑两条下载** —— **`en_v1_4`**（`Ultra-FineWeb/data/ultrafineweb_en_v1_4`，56,461 文件/6.75TB，PID 2535486，parallel 24 workers）+ **`85M`**（`mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M`，用户另行同时下载）。已令 **纯巡检、分路回报各自【速度 + ETA】**（双口径 files/min+MB/s；85M 按**字节**算 ETA；注明两路**共享带宽争用**），**只读不 kill**（除僵死）。判据=字节增量/`/proc/io`，禁文件数比例估。⬅️ 前情 10-09③：三目录全量分词；GPIC ✅ 全完成；R3 ✅ 110/110；污染 220K docs 0 命中 → **P-8 数据层已全就绪** | `run/BAIZE_DATA_TASK.md` 顶部新块 · `run/MEMORY_DATA.md` | 🟢 `.cline_data`；**en_v1_4/85M 均非 44B 档阻塞项**<br>⚠️ **10-10 晚更正（用户核实）**：85M 总量 = **46.7TB**（HF 官方页）；data agent 唤醒 302 的「7701 parquet/27T/100%」**作废**（只数了本地 6 子集，**漏 `sa1b`+`zero250m` ≈9.85TB**；把「已下 27T」误当「总量」）。正解 ≈ **46.66TB / 12,124 files**，本地 ≈57%，剩余 ≈20TB，**ETA ≈14–25 天（非 10–30min）**。**已下发更正令**（要求按 HF API 逐子集重算 + 改正心跳）。 |
| **harness** | 🔄 **R2 7×100 运行中**（19:22 起，**7 路并行**，ETA ~10h → ~05:30 Oct 9；100 = **30 R1 + 70 stratified**）；② 轨迹报告 ✅ `report_harness_interaction_traces.html`（38KB；**20pp gap 归因**：no-patch 33% vs 10% · timeout 27% vs 0% · patch scope 4.2 vs 2.2 files；**诚实声明仅 `stdout_tail` 存活**）；R1 7×30 ✅（60.0%–40.0%）；报告 4 份已交付。**⑦ 已下发**：并发变更**追认**但须**披露口径**（首轮 serial=1 vs 本轮并行；30 复用 / 70 新跑须标注；监控 quota/timeout/no-patch 率）+ 报告补落根目录 | `run/harness/*.html` · `run/harness/kimi_pilot_results.json` | 🟢 `.cline_harness`；**不占 GPU**（与 pretrain R3 BO 无卡冲突，注意 CPU/IO） |

> ✅ **vision 叙事已决（2026-10-03 用户）：走 A = 保持「从零训练」**（"A 本身也是为了学习"）。
> → R9 的 **~25.1% 渐近 = 从零路线的如实上限**（负结果有价值）；**loss 轴 R11 = 主线**；**架构轴非主要杠杆**。
> → 登记 **R12（候选）**：仅补 **iGVLM 式指令条件化**（TuringViT 低优先 —— attention 仅占 0.7%）；**须先报"值不值得"再批**。
> → 参考 **`run/VISION_ARCH_FRONTIER_2026.md`**（前沿 5 方向 vs 我们 R8 已测 4 个的逐项对照）。

---

## 4. 待拍板 / 我欠的答复

- [x] 📦 **已闭合（2026-10-11 滚动归档）**：BaiZe-Hybrid 等参 Dense 中文对比报告（✅ `report_pretrain_baize_vs_dense_fair_zh.html`）· 夜班填空 T1/T2/T3（已撤销）· Muon vs AdamW（✅ 已完成，`dist_muon` 为 P-8 默认）· BaiZe vs MiniCPM5 公平对比盘点（✅ 报告已交付）· pretrain 3-idea 征询（✅ #251）· P-9 结果→P-8 seq/MBS/精度 · P-8 配置拍板（✅ P-8 已于 10-10 启动）—— 原文见 `daily-memories/2026-10-11.md`「从 MEMORY.md §4 滚动归档（二）」。
- [x] 📦 **已闭合（2026-10-11 滚动归档）**：**vision AIMv2 缩放 E1/E2**（已收官：Δlp(ProtB)=+0.17pp → 不可分辨）· **P-8 启动令再评估**（P-8 已于 10-10 按计划启动）—— 原文见 `daily-memories/2026-10-11.md`「从 MEMORY.md §4 滚动归档」。
- [x] 📦 **已闭合（2026-10-11 滚动归档）**：vision / harness 运维问答（已收齐并答复；后续 GPU 空窗任务已分别派为 vision「变体实验 + 外部评审回应」与 harness「7×300」）—— 原文见 `daily-memories/2026-10-11.md`「从 MEMORY.md §4 滚动归档（二）」。
> 📦 **§4 已闭合条目滚动归档**（2026-10-08 执行，原文未改一字）→ `daily-memories/2026-10-08.md`「从 MEMORY.md §4 滚动归档」= pretrain 四件（10-05 深夜2）· data/vision 三份 HTML（10-05 深夜2）· AIMv2 提速归因前置（10-05 晚）· data 三步令（10-06）· **harness deepseek 工具链（10-05，已装通）** · **R9「53M cap」口径修正（10-03）** · **R8「六架构=自研改编」结论边界（10-03，R13 官方对照已完成 79.81%）**。
- [ ] 💬 **另一「运维会话」在并行活动**（2026-10-04 深夜发现：origin 上出现**我没写过的 RUN_ID 63 诊断记录**）→ **需与用户确认是否统一到单一会话**，以免重复下发/互相覆盖。
> 📦 **归档指针（查旧决策去这里，勿再塞回本文件）**：① **`daily-memories/2026-10-03.md`「从 MEMORY.md 滚动归档」A 节** = D-CLEAN-2/-3 与回收量核实 · harness R1 沙箱路线 · GPIC E1 实测 + C1 口径 · H-A′ 放行 · docker 系降末选 · sudo 口令 · `ops_relay`「2 副本」误判结案 · 论文冻结 · vision 队列裁定 · data 白名单锁定；② **`daily-memories/2026-10-05.md`「从 MEMORY.md §4 滚动归档」** = 本区已闭合的 `[x]` 条目（AIMv2 改写授权 · D-CLEAN-4 定案 · harness 取 kimi · sglang 走 conda · 环境隔离纪律 · proxy 口径 · Claude Code 合规口径定案）—— **原文未改一字**。

> ③ **`daily-memories/2026-10-06.md`「从 MEMORY.md §4 滚动归档」**（2026-10-07 滚动）= **配比实验改道裁定 · 「实验」定义 5 条判据**。**原文未改一字。**
- [ ] ⛔ **loop 优化：暂不做**（用户 10-03 定；需回公司重启 loop）· **文档口径**：seq 统一 **4096**（残留 4094 待对齐：论文 `3_architecture.tex:31`/`4_llm_pretrain.tex:75,165` + P-8 脚本 `SEQ=4094`）· 是否把关键决策并进 `BAIZE_PROGRESS.html`（单一事实来源）。

---

## 5. 铁律与纪律

- 📛 **报告命名纪律（2026-10-25 用户令 · 全项目所有线）**：报告里**一律写 `cline`，🚫 不许写 `cline-patched`**（含 `ClinePatched` / `cline_patched` / `Cline-patched` 等一切变体）。用户原话：「以后在报告里不要写 cline-patched，就写 cline，否则容易造成误解。」
  - 理由：读者看到 "patched" 会误以为只跑了改造过的 Cline；实际差异仅在**接入层**（安装 CLI / 写 baseUrl / 参数大小写），原生工具循环未改。
  - **代码/脚本/配置里的真实标识符不改**（`cline_patched.py`、`terminalbench.agents.cline_patched`、`jobs_cline-patched/`），但报告引用必须转写为 `cline`。接入层适配如需交代，放附录/脚注一次即可。
  - 已批量修正 `reports/` 下 17 份历史报告（2026-10-25）。

- 🚫 **绝不打断正在跑的 long-run**（尤其 **P-5b**：改 MBS/精度/seq 会让 20B loss 曲线作废）。
- 🚫 **绝不 kill 各线 watchdog loop**（`baize_*_loop.sh`）；收敛后只置 `WAITING=1` 长睡。
- **`WAITING:` 纪律**：只在各 `MEMORY_*.md` **顶部出现一次**（否则误触发 30 分钟长睡）。
- **记忆体量 ≤32KB**（**本文件 + 4 线 `MEMORY_*.md` 均适用**；超限滚动到 `daily-memories*/`）。
- **不许猜**：源码结论贴 `路径:行号`；实验结论贴 **命令 + 原始输出**。
- 🧷 **两条常驻纪律（细则在任务书「常驻规则」区）**：**① 环境隔离** —— 训练/长跑 = 共享 `py310`，需大量装包 = 另起独立 conda env（P-9.8 armB 被污染崩溃的教训）；**② 外网命令带 proxy** —— cline 会话继承「无代理」env，`pip`/`git fetch|push`/`hf` 报 `Errno 101`/`http 000` 是**预期**（非禁网/非 key 问题），**凡访问外网的那条命令自己显式带 proxy**（内网 hub/网关/ssh 不带）。
- 🚫 **不许闭门造车**（**2026-10-03 教训**）：凡涉及"别人怎么做"的结论（架构 / loss / 评测 / 数据），**必须去读官方仓库或论文原文**（能 `git clone` 就 clone），**不得凭印象或二手描述下结论**——当天我就把 R8 的**自研改编**误当成"官方实现"来下了结论。
- **预注册判据先定后测**（P-9a-ext G、R11 都用了）。
- 🔒 **红线**：`EDA-Eval-PyAether` 158 任务只读隔离区**绝不可动**；base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k 均不可删。
- ⚠️ **`run/nemo_experiments` 含 P-5b 正在写的 ckpt**，且 **P-6② 要用其中 6 个里程碑 ckpt** → 只能「先列清单、保住最晚/最优 + 里程碑，再删早期项」。
- **不占 GPU 的线**（data/harness）也要**避让 `.29`/`.12` 的训练 I/O**。
- 🚫 **不得让多条线共用一份可变配置目录**（cline 已按线 `--data-dir` 隔离）—— **共用 = 迟早互相踩**（2026-10-04 的反复 Forbidden 就是这么来的）。
- 🚫 **relay 块内每条可能慢的命令都必须有界**（`timeout N`）；重活丢 **后台 `setsid nice -n 19` + 落盘 + `.done`**；**绝不对大目录做全树遍历**。

---

## 6. 关键路径与事实速查

- **关键路径**：`P-5b → P-9 → P-6② → P-8`（P-8 = Stage(i) 本体，周级墙钟，仍暂缓等 base + 配比）。
- 🔴 **配比搜索形态已改（2026-10-06）**：**不再用 2.2B 跑单臂**，改 **小代理（定案 `h=512/L=14`=96.8M = 1/23）× Optuna BO × 6 卡并行 × 1 天/段**；**24h 目标 200–400 trial**。锚点 = `ye2024datamixinglaws` + Xmodel-2 `400+ 次试验`。⇒ **「等配比」的等待时间从「周级」降到「2 天」。**
- **两条硬口径（2026-10-03 定）**：
  - **seq 统一 4096**（2 的幂 2¹²；**用户直令 2026-10-14**）；`4094` 是 P-8 脚本的**错误残留**（`baize_p8_train.sh:30`/`baize_p8_adamw_train.sh:33` = `SEQ=4094`，须改 4096；`EXPERIMENTS_PRETRAIN_2B.md:4`/`MEMORY_PRETRAIN_2B.md:183` 的「4094」记录一并更正）。**P-8 处置：让其按 4094 跑完（stable+decay 整轮），脚本改 4096 待 P-8 结束后再做；今后新 run 一律 4096。**
  - **每步 ≈ 4M token 不变量**：`4096↔GBS1024` · `8192↔512` · `16384↔256` · `2048↔2048`。**总步数 = 总token/4M，与 seq 无关**。
- **FP8 机制**：`s` 取决于 **GEMM 的 M**，大 GEMM `M = MBS × seq`；**`M≳16K` 才 `s>1`**（seq 与 MBS 是等价杠杆）。
- **vision 现状**：R9 lp 渐近 **25.1%**（当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结CLIP文本塔 + InfoNCE**；⚠️ **不是 GPIC**）；`attention flash` 仅占 GPU 自耗 **0.7%**（P-4 profile）。
- 🚩 **`launcher` 只暴露 MBS / TP / SP / seq-length / precision**（agent P-9 非 GPU 预研，2026-10-03）→ **P-9 只用已暴露开关、不改 recipe**；B/C/E/F 类（recompute / 通信重叠 / dataloader / attn-backend）**冻结**，其中 **NCCL（P-4 占 41.7%）** 收益最大 → 记录在案、**待批准后另开**。
- **磁盘**：`/nas_train` 207T/剩 ~31T（86%）· `/nas_inference` 剩 20T · `/nas_user` 剩 29T。
- 🪶 **任务书瘦身（长期纪律）**：loop 是 `prompt="$(< TASK_MD)"` → **任务书全文 = 每次唤醒的 prompt**，必须保持小；已闭合块要移出（归档不进 prompt）。历次瘦身数字见 `daily-memories/2026-10-0{3,5}.md`。
- **本机（Windows 侧）**：`C:\Users\liuyu\super_intelligence_2035`（git clone）；**可 fetch/pull/push GitHub**；**不能直连 `.12`/`.29`**（SSH 超时）——**通道就是 git**。
- 🔒 **cline 隔离目录（NFS 共享）**：`.cline_pretrain`（`.29`）· `.cline_vision` / `.cline_data`（`.12`）**均已切**、`Forbidden=0`、model=glm-5.2；`.cline_harness`（`.29`）**已建未切**。目录路径：`/nas_train/app.e0031982/.cline_<line>`。
- 🔎 **MCP / web search（2026-10-05 四线打通）**：`.29:8090` 的 `eda_fastmcp` SSE MCP 暴露 `cimi_search` / `cimi_fetch`（绑 `0.0.0.0` ⇒ `.12` 可跨机用）；**四线均实测成功（rc=0）**。⚠️ 配置路径「两台各一份」的坑见 §7。

---

## 7. 已知坑（会复发）

- 🟡 **`baize_vision_loop.sh` 无 `git pull`**（2026-10-03 复核脚本原文：只做 `git add -A` + `commit` + `push`，每 5h）—— **✅ 但不构成阻塞（用户 2026-10-03 确认）**：
  → **机制**：**仓库是共享的** —— **别的线（`baize_pretrain_loop.sh` / `baize_data_loop.sh` 都会 `fetch + pull --rebase --autostash`）拉一次，vision 在同一工作副本上就看到**我的任务书更新。→ 所以 `84d7990`（R11-L2 批准）**会经由 pretrain/data 的 pull 自然到达**，**无需任何专门处理**。
  → 🔧 **可选根治（需登机；非必须）**：`pkill -f baize_vision_loop.sh` → 照抄 `baize_pretrain_loop.sh`（自带 pull + 行首 `^WAITING:` 正则 + 只 add 本任务文件）→ 再 `setsid` 起。
  → ⚠️ 附带注意：它的 `git add -A` 会把**整棵树**的改动一起提交（不只 vision 文件）——共享副本上叠加时**可能误提交别线在途文件**。
- 🔴 **ops relay 的命令块：每一步都必须有界（2026-10-04 实测，我自己踩的坑）**：
  - **症状**：我在 RUN_ID 34 里写了 ① `fuser -v <dir>`（**没加 `timeout`**）② `grep -rln … /nas_train/app.e0031982/code`（该目录 **8 TiB**、海量文件）→ **块被卡住**，`timeout` 只杀 leader、**继承了 stdout 的子进程仍活着** → 中继读管道被挂住 → **`.last_run_id` 停摆 ~11 分钟**（自设 600s 超时都救不回）。
  - **铁律**：**每一条可能慢的命令都必须 `timeout N`**；**绝不对大目录做 `grep -r`/`du`/`find` 全树遍历**（改用：只扫小目录、`stat` 取 mtime、或把重活丢给**后台 `setsid nice -n 19`** + 写文件 + `.done` 标记，再由下一轮读）。
  - **正确的重活姿势**：`setsid nice -n 19 bash -c '… > /tmp/x.log 2>&1; echo done > /tmp/x.done' &` → 块本身秒回，结果边跑边落盘。
  - ℹ️ **中继会自愈**：RUN_ID 34 最终 `exit=124`（超时），但**它被杀之前已经把 `rm -rf` 跑了** → 后续块看到 "GONE" 秒过。⚠️ 所以**超时不等于没做**，务必用后续只读块核验事实（别信日志的"瞬时完成"）。

- `ops_relay.sh` 会跑出**多副本**（共享 `.last_run_id` → 重复执行）→ 保留 **`etimes` 最大**者。
- **WAITING 正则**：旧版 `WAITING:[* ]*1` 误匹配正文散文 → 已收紧为行首 `^WAITING:[[:space:]]*1`。
- `baize_vision_loop.sh` 只 push 不 pull 的缺陷**未修**（运行时不宜改脚本）→ 等它停再照抄 pretrain 新版。
- 本机 PowerShell 读 UTF-8 中文会乱码——**只影响显示**；校验用 `read_files`。
- 🌐 **本机外网「时通时断」的原因已查明（2026-10-03 用户确认）**：**用户开 VPN（用于 Google 搜索）时 GitHub 不通，关掉即通** → 抓 GitHub / HF 前先确认 **VPN 已关**；断连**重试即可**，不是仓库/权限问题。
- 🔴 **cline Token 额度会耗尽（2026-10-03 实测，重要）**：`/tmp/baize_harness_loop.log` 原文
  `error: 本次Token额度已用完，请等待16分钟6秒后重试` —— **但 cline 仍返回 `exit 0`** →
  **loop 分辨不出失败，只睡 30min 再试** → 表现为**"静默变慢"**（不是挂了）。4 线**共用同一 cline 模型**时会互相抢额度。
  → 排查入口：`/tmp/baize_*_loop.log`（**注意：`.29` 上只有 pretrain/harness；vision/data 在 `.12`，其日志不在 .29**）。
- 🔴🔴 **`.29` 的 cline 必须显式 `-k <key>`（2026-10-04 实战定位，~9h 停摆的真凶；含我自己的 4 次误修）**：
  - **现象**：`.29` 的 pretrain/harness 每个唤醒周期只打印 **`error: Forbidden`** + `cline returned (exit 0)` → loop 当成功、继续睡 → **完全静默**（pretrain 18 次 / harness 37 次）；同段 `.12` 的 vision/data 整夜正常。
  - **四路矩阵实证（RUN_ID 26，唯一可信依据）**：
    | 组 | env | 结果 |
    |:--|:--|:--|
    | V0 | 原样 | ❌ Forbidden |
    | V1 | 剥 `OPENAI_API_KEY+OPENAI_API_URL+API_TYPE` | ❌ |
    | V2 | V1 **+ 剥所有 `*_proxy`** | ❌ |
    | **V3** | **V2 + 显式 `-k <secrets 里的有效 key>`** | ✅ **OK** |
  - **叠加的两个故障**：① loop 继承的 `OPENAI_API_KEY=01_549…` 是**已吊销**的旧 key，**会覆盖** secrets.json 的有效 key（`02_088…`）→ 22:10–07:28 全程 Forbidden；② **即便**换掉/剥掉它，`.29` 的 cline **仍需显式 `-k`**（⚠️ **机制未完全解释**：07:28 那版不带 `-k` 也曾成功 11 分钟；而 `.12` 不带 `-k` 一直能跑）→ 故 **以 V3 为定稿**。
  - **已排除（都实测过）**：proxy 单独（`直连 200 / 走代理 503`，但剥掉不够）· `OPENAI_API_URL/API_TYPE` 单独 · 模型名 · `globalState.json`（`.29`/`.12` 字段一致）· **cline CLI 版本**（两台都是 **3.0.51**、安装于 2026-09-08；globalState 里的 4.1.21/4.0.8 是 VSCode 扩展版本，无关）· token 额度 · `.env` 里那几把 `*_API_KEY`（curl 全 **403**，不可用）。
  - **定稿修法**：两条 loop 顶部 `CLINE_KEY="$(sed -n 's/.*"openAiApiKey"…/\1/p' "$HOME/.cline/data/secrets.json")"`，cline 行 = `env -u <所有 *_proxy> -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE cline … -k "$CLINE_KEY" …`。**key 不落仓库**。
  - **可复用排查法（ops relay 只读块）**：① `pgrep -af 'baize_.*_loop.sh'` ② `grep -c 'error:.*Forbidden' /tmp/baize_*_loop.log`（**精确探针**；`grep -c Forbidden` 会数到 agent 散文，**假阳性**）③ `nvidia-smi` 看 GPU 是否空转 ④ **多把 key 分别 `curl /v1/chat/completions`** ⑤ **env 矩阵 smoke**（**必须逐一控制变量**）。
  - ⚠️ **我的两次次生错误（务必引以为戒）**：**(a)** 用 `python3 -c` 在 loop 里取 key → relay 的非交互 shell **PATH 里没有 python3** → 静默取不到、退回 stale key；**(b)** 写 env 矩阵时**漏剥 proxy** → 三组全红、得出"key 失效"的错误结论，白绕 3 轮。→ **每次只改一个变量，并在同一块里验证该变量确实生效**。
  - ⚠️ **复发预防**：轮换 cline key 时**必须同时更新 `.12` 与 `.29`**；日常体检跑 `grep -c 'error:.*Forbidden' /tmp/baize_*_loop.log`。
  - ✂️ **源头加固（RUN_ID 29，2026-10-04，用户批准）**：`.29` 的 **`~/.bashrc:170` 的 `export OPENAI_API_KEY=` 已原地注释**（**原值保留为注记**；备份 `~/.bashrc.bak.20261004-081247`）→ 目标是**单一真源 = `~/.cline/data/secrets.json`**。**`https_proxy`（同文件 :140）保留不动** —— 实测 `git ls-remote github` **无 proxy = FAIL / 有 proxy = OK**，删了 loop 的 push 就废。`API_TYPE`:169 / `OPENAI_API_URL`:171 保留（实测剥掉不足以修复）。
  - 📌 **`.12` 是现成范本**：它的 `.bashrc:143` 早就注释着 `# disabled: proxy DNS cannot resolve internal agi-gateway.cxmt.com`（9/29 那次修的）。
  - 🔧 **配套改动**：`run/harness/run_harness.py` 的 `ClineDriver` 改为 **`resolve_cline_key()` = env 优先、否则回退读 `~/.cline/data/secrets.json`**（并**纠正了原先写反的 GOTCHA 注释**）。→ 这样即使 env 里没有 key，driver 的 `available()` 也不会变 False。
  - ℹ️ **注意**：改 `.bashrc` **不影响已在运行的 loop**（进程 env 已固化），属"防未来"；loop 侧 V3 配方（剥 proxy + 显式 `-k`）保持不变。
- ⚠️ **`.29` 与 `.12` 的 `/tmp` 不共享** → 诊断 loop 日志必须**指明机器**；而**共享工作副本在 NFS**，所以**跨机能看到"别的线未提交的在途文件"**（这正是判断"某线是否在干活"的好办法）。
- ⚠️ **`ops_relay.sh` 的「多副本」是误判（2026-10-03 更正）**：`ps | grep ops_relay` 会看到 **2 行**，但其中一行是 relay **执行命令块时 fork 的子 shell**（`ppid` = 真 relay、`etimes≈0`）。→ **判别看 `ppid`**；**唯一真 relay 的 `ppid=1`**。🚫 **绝不要"把两个都杀掉"**（会切断远程通讯）。详见 `run/AGENTS.md` §3.5(1)。
- 🔴🔴 **4 条线共用一份 `~/.cline/data`（2026-10-04 定位，比 `-k` 更根本，会复发）**：`.29` 上 pretrain/harness 共用 `globalState.json`，harness 改成自己的 `gw_proxy` → pretrain 被指向死代理 → `Forbidden`（cline 仍 `exit 0` ⇒ 静默）—— 这就是「修好 key 后还复发」的原因。**修法 = 按线 `--data-dir`**（`/nas_train/app.e0031982/.cline_{pretrain,harness,vision,data}`；前三已切，harness 已建未切）。⚠️ 三个坑：① **`--data-dir` 指 data 目录本身**（文件放 `<D>/` 根）；② 只播 `globalState.json`+`secrets.json` 不够，**provider/base 在 `settings/`**（漏了报 `Cannot connect to API`）；③ **ssh 非交互 shell 无 `bun`** ⇒ 需 `export PATH=$HOME/.bun/bin:$PATH`。
- 🔴 **relay 块里凡「可能读 stdin」的命令（尤其是 cline smoke）必须加 `< /dev/null`** —— 否则它会把 ssh heredoc 里**剩余的脚本当 stdin 吃掉** → 输出莫名截断，我因此**误判成「嵌套 heredoc bug」白绕两轮**。
- 🔴 **relay smoke 必须复现「loop 的真实 (model, base) 配对」** —— `llm_pick` 会选中「**curl 探针 200 但 cline 实际 403**」的候选（`deepseek-v4-flash @ /v1`）→ 我已给 `llm_rotate.sh` 加 **「优先 glm-5.2」**（`glm-5.2 @ /cloud/v1` 实测 cline 可用）。
- 🔴 **下发 relay 块的「最后一步」= 核对两件事**：顶部 `<!-- RUN_ID -->` **已 +1**，且 **文件已 push**。RUN_ID 50 曾因头标没加（`rid == last`）**卡了整整一轮**。
- 🌐 **`.29`/`.12` 的 GitHub 通道会「时通时断」⇒ `origin/main` 落后 ≠ 线停摆！** 判据 = `grep -c 'error:.*Forbidden' /tmp/baize_*_loop.log`（应 0）+ `nvidia-smi` util（是否真空转）。抖动时 agent **照常在本地提交**、只是推不上（曾见 `.12` `ahead 16`、`.29` `fetch FAILED`）；恢复后**积压会自动回补**。
- 💬 **可能另有「并行运维会话」** —— 2026-10-04 深夜在 origin 见到**我没写过的 RUN_ID 63 记录** → **下发前先 `git pull --rebase`**，遇冲突**保留双方**，勿互相覆盖。
- 🪟 **本机（Windows）工具坑**：① PowerShell 下 `git commit -m "…"` 遇 `()` / `->` / 全角括号会报「字符串缺少终止符」→ **一律 `git commit -F <临时文件>`**；② `Select-String` 对**中文/`$tag[...]` 插值**匹配不可靠 → **中文校验改用 Python**；③ 控制台是 GBK → Python `print` 中文/emoji 会 `UnicodeEncodeError` → **把结果写文件再 `read_files`**。
- 🔎 **MCP 配置不走 `--data-dir`（会复发）**：固定读共享 `~/.cline/data/settings/cline_mcp_settings.json`（与 `--data-dir` 无关）；`.29`/`.12` **各自本地一份**（非 NFS）→ **修 MCP 两台都要修**。⚠️ 探针坑：① SSE 端点不能 `curl -w '%{http_code}'`（长连接 → 空输出 → 误判）→ 只取响应头 `curl -sS -D - -o /dev/null`；② `cline mcp list` 无效 → 正解 `cline config mcp`。
- 💡 **诊断教训**：`baize_p5b_train.log` **只在 START/END 写**；**逐迭代日志是 `/tmp/baize_p5b.log`**。
- 🏁 **改「已下发块」的关键参数 ⇒ 必须新起一个序号块置于最顶**（2026-10-08 竞态教训：⑤ 下发后 ~1h 才改 E2，agent 已按旧版 smoke/写预注册/排队）—— 只改原块正文不行，agent 的 `MEMORY` 里仍引用旧版。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **任务书同样 ≤32KB，且由各线 agent 自己滚动归档**（2026-10-06 用户裁定：与 MEMORY 同机制，**不再由运维代劳**；护栏 = 只搬迁已闭合块原文 + 留 1 行指针，不新增/不改写指令）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **📋 2026-10-14 pretrain 正式训练计划【v4 重做】**（用户直令）：判 v3 质量不合格。用户 6 问：① 密度 tok/byte 0.0657–0.4977 差异归因；② `.bin` 每 token 几字节（字节/每 token = token 数）；③ 删「52 天不现实」等主观判断（现实与否不由 agent 定）；④ 逐源**准确** token 数；⑤ 全量配比 + 每源采样次数；⑥ D={100B,200B,400B,800B,1.6T,3.2T} 的 **8 常识 / 6 复杂**均分预估。已下发 `run/BAIZE_PRETRAIN_2B_TASK.md` 顶：v4 覆盖原文件，逐源 token 从分词 `.bin/.idx` 实测（核实 dtype=2B/4B）· 密度归因（压缩态≠文本密度）· 删主观 · 采样次数表 · scaling 拟合+web search 外推（分实测/拟合/外推三档）· 自包含 HTML+曲线图+修订说明。commit `pretrain plan:`。

- **▶️ 2026-10-14 data 恢复下载**（用户直令）：「data 数据下载 resume。」⇒ 已下发 `run/BAIZE_DATA_TASK.md` 顶：**恢复 `en_v1_4` + `WebMix-38M` + `wit_base` + `InternVL-SA1B` 4 路**（断点续传，`.incomplete` 保留）；**85M 维持暂停**。停前基线：en_v1_4 58.4%(32,995/56,461) · WebMix 78 · wit 79 · InternVL 303。纪律：`df -h` 核余量 · `setsid`+正确 PATH · 死/僵/速率趋零即 kill+restart · 错峰 `.29`/`.12` · commit `data dl:`。

- **🔧 2026-10-14 vision 放行并行（ViT wrapper）**（用户直令）：用户拍板「现在就在 ArmC 期间并行写 ViT wrapper（纯 CPU）」。已下发 `run/BAIZE_VISION_TASK.md` 顶：BaiZe OpenVision2 → HF wrapper（patch-level `[B,196,1024]`、跳过 ReadoutHead、从 ④-4ep `{'vision': sd}` 载入）+ 自定义 LLaVA modeling（2 层 MLP 1024→2560、无 spatial merge、224）+ CPU 单测 + README + 中文报告 `report_vision_mllm_bridge_zh.html`；纪律 = 零 GPU · 不打断 ArmC 训练/eval · NFS 冲突让路 · commit 前缀 `vision mllm-bridge:`。

- **📐 2026-10-13 vision LR 缩放定则**（用户直令）：查证 GBS×4→LR 应变多少：线性规则(Goyal 2017 arXiv:1706.02677)=**×4**+warmup；B∝LR含Adam(Smith 2017 arXiv:1711.00489)；次线性√=×2(无一手出处)；实证必重调(Shallue 2019 arXiv:1811.03600)+critical batch(McCandlish 2018 arXiv:1812.06162)。已令 vision 默认 ×4 + 3 臂扫描{×2,×3,×4}。

- **📋 2026-10-13 vision 数据量口径更正**（用户直令）：报告 GPIC「~80–85M」= 6233-tar 旧值；快照实为 7437 GPIC tar → GPIC ≈93–94M（全量 8000 tar=101.1M）→ 三集合计 ≈111M/118.1M。已令按实盘重算。

- **📋 2026-10-13 任务书去粗体瘦身**（用户直令）：删除 BaiZe 7 + personal-watch 4 = 11 份任务书的全部 `**` 粗体标记（代码内保留），共 -13.4KB；仅格式化不改语义；ZhuLong 任务书未动。

- **📋 2026-10-13 vision 放行 + data 换下载目标**（用户直令）：vision 外部 ProtB 做完即跑「合并三数据集实验」（GBS/MBS×4·LR×2·24h≈3ep·放行起训）；data 暂停 85M（保留 69.2%）+ 下载 HF 图文对 TOP-5 未下的 4 个 → 落 /nas_inference 或 /nas_user 的 datasets（🚫 不放 /nas_train）。

- **📋 2026-10-13 pretrain 计划书【v3 再重做】**（用户直令）：用户否 v2「300B」无出处（MiniCPM5 无训练论文；`arXiv 2602.09003`=UltraData 数据框架论文非 MiniCPM5；300B 出自 CSDN 二级源）→ 令 v3 **按「已下载+正在下载」实盘盘点换算 token**，禁引论文数字。

- **📮 2026-10-13 招聘日更下限**（用户直令）：每天「优中选优」**至少推 3–5 份简历** → `paul.liu@cxmt.com`（附 PDF）；排序取 Top-N 非「达标才发」；**不得 0 封**；18:00 收盘轮补足。年底要招人。

- **📋 2026-10-13 招聘门槛下调**（用户直令）：两个 JD（研究员 + 实习生）均**取消「四大 EDA 顶会（ICCAD/DAC/DATE/ASP-DAC）」门槛**（研究员硬门槛取消 / 实习优先项移除），AI 顶会维持原状；改源 JD + 任务书下发令。

- **📋 2026-10-13 五项运维指令下发**（用户直令）：① data HF 图文对数据集调研（bytes 非 url）② vision 合并三数据集计划（GBS/MBS×4 · LR×2 · 24h）③ pretrain 正式训练计划书【重做】（按 MiniCPM5 全量口径 · 禁 100B）④ harness 通过率为何低（web 对照 + 轨迹 + 排序）⑤ recruit 质询 0 封推荐邮件（先解释后修复）。详见 `daily-memories/2026-10-13.md`。

- **📦 2026-10-09 全部 §9 流水已滚动归档**（2026-10-11 执行 · **原文未改一字**：改序/砍实验 · Muon 下发+NeMo 支持更正 · 夜班 T1/T2/T3 · GO #252 Dense L=36 · 3-idea 征询 · BaiZe-2B vs MiniCPM5 公平对比核查）→ `daily-memories/2026-10-11.md`「从 MEMORY.md §9 滚动归档」。**勿再塞回本文件。**

> 📦 **2026-10-08 流水已滚动归档** → `daily-memories/2026-10-08.md`（**原文未改一字**：harness R2 7×100 + 交互轨迹报告 · vision AIMv2 缩放 E1/E2 · pretrain R3 BO 下发 · vision/harness 运维问答征询 · 早/午论文更新两条）。**勿再塞回本文件。**


> 📦 **2026-10-07 流水已滚动归档** → `daily-memories/2026-10-07.md`（**原文未改一字**：harness 30 横评 · pretrain 2M–16M+显存归因+5 份研究 · data 解禁白名单 ＋ 撤销「15:30 定时停 UltraX」）。

> 📦 **2026-10-06 流水已滚动归档** → `daily-memories/2026-10-06.md`（data 三步令：Stable 200-trial · `s_step` 归因 166 ms · `.29` 8 卡搜第二轮）。

- **📦 旧流水已滚动归档** → `daily-memories/2026-10-06.md`（**原文未改一字**：10-06「第 6 轮」/「第 5 轮块」/「两条流水（复核②、改道）」）。**勿再塞回本文件。**



- **📦 2026-10-04 / 2026-10-05 的 §9 流水已滚动归档**（2026-10-06 执行，压回 §8 上限；**原文未改一字**）→ `daily-memories/2026-10-05.md` / `daily-memories/2026-10-04.md` 之「从 MEMORY.md §9 滚动归档」（内容：合规口径·红线·任务书瘦身·FP8 裁定·harness 换模型·文献重做·EDA MCP ＋ vision 双批准·R11-F·`.29` 停摆事故）。**勿再塞回本文件。**
