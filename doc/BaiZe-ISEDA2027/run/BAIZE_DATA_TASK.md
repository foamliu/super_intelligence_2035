# BAIZE_DATA_TASK.md

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 🔴 运维令 · 2026-11-07 10:10（**`stack-v3-train` 正式放行：ROI 高，先下 2TB 优质子集**）· 用户直令 · 最高优先 · 未完成

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


### 🔴 运维令 · 2026-11-07 08:5x（**代码语料放行：`stack-v3-train` 可考虑，`the-stack-v2` 禁下，其余单集 <1TB 放行 —— 你自己按 ROI 从高到低排优先级下载**）· 用户直令 · 最高优先 · ⚠️ 未完成

> **用户原话**：「report_data_lc_agentic_survey_zh.html 这个报告我看了。bigcode/the-stack-v2 占用空间太大，不能下载。HuggingFaceCode/stack-v3-train 可以考虑，其它单集 <1TB 的也可以放行。让它自己排个优先级，从 ROI 从高到低开始下载吧。」

> **补充语境（用户 2026-11-07 追加）**：「pretrain 还缺 code 数据，现在 code 占比才 19%，低于我在 Xmodel 训练时使用的量（25%）。……增加 code 配比这件事**不急**，所以可以按 data 的喜好**慢慢来**。**有也行，无也行。快也行，慢也行。**……UltraData-Code L2/L3 pretrain 已经在训练了，**后续考虑 stack-v3-train**。」
>
> ⇒ **本令的优先级定位**：code 数据补料 = **低压力背景任务**，🚫 不要挤占 S1 训练带宽、🚫 不要为了赶进度牺牲质量。可以慢慢下、分批下、挑着下。

**① 三条硬口径（不可改）**

| 数据集 | 结论 | 依据 |
|:--|:--|:--|
| `bigcode/the-stack-v2` | 🚫 **禁止下载** | 67.5TB full / **32.1TB dedup**，且需与 SoftwareHeritage/INRIA 签协议 + gated |
| `HuggingFaceCode/stack-v3-train` | ⚠️ **可以考虑**（非无条件放行） | **train 15.9TB**（full 113.7TB，🚫 不许下 full）；ODC-By、非 gated、**文件内容内联**（比 v2 的 SWHID 引用形态更实用） |
| 其它**单集 < 1TB** | ✅ **放行**（你自行判断 ROI） | 见下方 §② 候选池 |

> 🚫 **单集 ≥1TB 一律不下载**，包括 `stack-v3-train` 的 full 版（113.7TB）与 `AlienKevin/SWE-ZERO-12M-trajectories`(111G 可下，但要注意它不是 <1TB 的问题而是性价比)。若你认为某 ≥1TB 集必须下，**先报运维批准**，🚫 不许自行开工。

**② 允许放行的候选池（从 `report_data_lc_agentic_survey_zh.html` 提取，单集均 <1TB）**

- **长上下文 E 类**（部分已下载，见 `DATA_MAPPING.md` §E，🚫 不重复下）：`ysngkil/whole-books` 25.3G · `princeton-nlp/prolong-data-512K` 114G（**代码仓库级，ROI 高**）· `openbmb/InfLLM-V2-data-5B` 15G · `self-long/RULER-llama3-1M` 5.1G · `caskcsg/NExtLong-128K-dataset` 20.5G · `THUDM/LongAlign-10k` 0.6G · `ghostcc3/mix-context-post-training-128k` 32.5G · `yuyijiong/LongData-Corpus` 36.1G(gated) · `birgermoell/oellm-longctx-tokenized-...-pilot-v1` · `deepmind/pg19`(仅脚本)
- **新增候选**（报告中出现、尚未下载）：`caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3` · `THUDM/LongWriter-6k` · `utter-project/LongBlocks` · `zai-org/LongBench-v2` · `alea-institute/kl3m-data` · `common-pile/arxiv_papers_filtered` · `common-pile/project_gutenberg_filtered` · `NovaSky-AI/SkyRL-v0-293-data` · `Nethraaaaa81/swev-trm-trajectories-25models` · `harborframework/terminal-bench-2`（⚠️ 评测集，仅去污染）
- **B 类 agentic 补漏**：`nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1`（报告中出现，未在 F 节）

**③ 你要自己做的事：排 ROI 优先级 → 从高到低下载**

**③-0 · Code 补料专项（用户 11-07 重点，但明确「不急、有也行无也行」）**

- 盘上 code 源仅 `UltraData-Code-L2`(421.45B tok)+`L3`(128.62B tok)=**550.1B tok**，占全量 **12.23%**（总 4,498.6B）。
- ⚠️ 用户称 **S1 实际配比 19%**，与上不符 ⇒ **查清口径**：`EXPERIMENTS_PRETRAIN_2B.md:15` 记的是 `L3(86)+code(10)+math(4)`。查 S1 配比配置/启动脚本，明确「19%」分母（shard 采样权重？文件大小？token？），**结论写进 `DATA_MAPPING.md` 一节**。
- 缺口（仅量级参考，非 KPI）：25% 目标需 1,125B tok，缺 ≈575B tok ≈ 2–2.5TB 原始数据。

**要做的**：①查 `stack-v3-train` 子集/分片结构，给出只下代码相关的 `--include` 方案（15.9TB train，评估按语言筛能否压到 2TB 内）②把它放进 ROI 排序做主力候选 ③节奏自定（可分批/夜间/`nice -n 19` + `--max-workers 2`），🚫 不与 S1 抢带宽 ④**不把 25% 当 KPI**，做多少算多少，但每次下载须记清 token 增量。

---

1. **ROI 评估表**（写进 `DATA_MAPPING.md` 新节）：每候选评 5 维 —— ①相关性（PyAether/EDA 代码/agentic）②单位成本收益（GB vs token vs 独特性）③可用性（gated/协议/格式）④质量风险（license/污染/清洗）⑤落地成本（下载时长 + 转换）
2. **排序 + 按序下载**（≥1TB 的须先报批）；**总量 ≤1.5TB**（/nas_inference 29T 可用，留余量给分词产物），超限先报。

**④ 落盘与纪律（沿用 11-04 令）**

- 落盘 `/nas_inference/app.e0031982/datasets/<repo原名>/`；gated 源用已配 token（`.29` `~/.cache/huggingface/token`）；走代理 `HTTPS_PROXY=http://172.19.92.25:13128`
- `setsid` 后台 + `/tmp/data_download_*.log`；🚫 不挤 S1（`nice`、`--max-workers 4`、留带宽）；断点续传
- 🚫 `ia03/terminal-bench` / `harborframework/terminal-bench-2` 等**评测集只进去污染黑名单，禁入训练**
- 下载完写 `DATA_MAPPING.md` 新节（`du -sb` + `find | wc -l` + `incomplete` 三项核对）；commit `data 下载:`
- 🚫 token 不得写入表/日报/commit

> **完成标记**：ROI 评估表 + 下载（含本轮已完成部分）落盘核对齐全 ⇒ 本行改 `✅ 已交付`；未完成 ⇒ `WAITING: 0`（60s 后继续）。

---

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

评测集本体路径（用于建黑名单，只读，绝不写入任何训�
