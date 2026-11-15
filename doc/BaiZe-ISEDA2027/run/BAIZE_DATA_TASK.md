# BAIZE_DATA_TASK.md

> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」检查**：限制探索的禁令已删除；**数据安全类约束全部保留**（删源前校验、不挤他人带宽、不碰他人产物、磁盘红线）——它们防的是**数据损毁**，不是防尝试。**默认立场：数据筛选规则、抽样方法、质检策略由你自主决定，写清依据即可。**

> 🔴 **用户令 · 2026-11-15 09:0x（评估 5 个 agent datasets，有用则加入下载队列）· 高优先 · 未完成**

> **用户原话**：「data: 这些agent datasets 是否有用，有用就加入下载队列」+ 5 个 HF 链接

**我的初判（基于实查，你要自己复核并纠正我）**

| # | repo | 规模 | 性质 | **我的初判** |
|:--|:--|:--|:--|:--|
| 1 | `microsoft/orca-agentinstruct-1M-v1` | ~2.2GB | **纯合成**，GPT-4 生成，OpenAI messages 格式，**无真实工具执行** | 🟡 **低优先**（见下） |
| 2 | `Agent-Ark/Toucan-1.5M` | 待核实 | **495 个真实 MCP server / 2000+ 工具** 合成的 150 万条轨迹，含真实工具执行，多轮/并行调用；BFCL-V3 + MCP-Universe 上有增益 | ✅ **强烈建议下**（最贴我们） |
| 3 | `open-thoughts/AgentTrove` | 1.7M 行 | **terminus-2 / Harbor harness 格式**的真实 agent 轨迹（含 SWE、codeforces、SWE-smith 等），带 `reward` 与失败轨迹 | ✅ **强烈建议下**（与我们 harness 线同源） |
| 4 | `neulab/agent-data-collection` | **499 GB** | **ADP 统一协议**，把上面 3 个 + 20 多个源统一成 SFT 格式 | ⚠️ **去重后再决定**（见下） |
| 5 | `harvardMadsys/freeinference_agentic_trace` | 1.19M 请求 / 1.21M 工具调用 | **只有元数据，没有消息文本**（`No message text is released`） | ❌ **不能用于训练**，但对 harness 线的 workload 分析有用（见下） |

**逐条判断依据**

**① `microsoft/orca-agentinstruct-1M-v1` → 🟡 低优先**
- 纯合成（Azure GPT-4 生成），许可证 `cdla-permissive-2.0`，英文
- **关键缺陷**：它的"agentic"是**方法论层面的**（AgentInstruct 流程生成问答），**轨迹里没有真实工具调用/执行反馈**。我们要培养的是"按协议调工具并交付结果"，这种数据帮助有限
- ⇒ **先不下**，除非你在调研后认为需要补充通用指令遵循能力。若要下，优先级排在 2/3 之后

**② `Agent-Ark/Toucan-1.5M` → ✅ 强烈建议下**
- **最贴我们痛点**：495 个**真实 MCP server**、2000+ 工具、真实工具执行、多轮/顺序/并行调用 —— 这正是 **posttrain 那 1304 次工具调用被拒**要解决的问题
- 有配套 SFT 子集（119.3K：28.3K 原始 + 40K Irrelevance + 15.8K Diversify + 35.2K Multi-Turn），含 **Irrelevance 扩展**（教模型"不该调工具时别调"）—— 对减少无效调用特别有用
- license Apache-2.0
- ⇒ **下全量**

**③ `open-thoughts/AgentTrove` → ✅ 强烈建议下**
- **与我们 harness 线直接同源**：Harbor / terminus-2 格式，就是 harness 线做 SWE-bench / TB-2.1 用的那套框架
- 1.7M 行，来源含 `swesmith` / `codeforces` / `nl2bash` / `r2egym` / `staqc` / `freelancer` 等，**带 `reward`（0/1）**⇒ 可用于 RL
- ⇒ **下全量**；并**额外记录**：它与我们 harness 线的 Nemotron Terminal Corpus 同格式（AgentTrove 规模是它的 4 倍）

**④ `neulab/agent-data-collection` → ⚠️ 去重后再决定**
- **499 GB**，但**它里面已经包含了 #2 Toucan 和 #3 的部分来源**（`orca_agentinstruct`、`toucan_1_5m`、`nemotron_terminal_corpus`、`swe-smith`、`nebius_SWE-agent-trajectories` 等 20+ 源）
- 价值：**ADP 统一协议**把各源转成统一 SFT 格式（`sweagent` / `openhands` / `agentlab` 三种模板），省你自己写转换器
- 风险：**与 2/3 内容重叠**，全下 499GB 会重复存储
- ⇒ **做法**：先下 **ADP 的转换脚本和 schema**（GitHub `neulab/agent-data-protocol`，不含大数据），再**只挑 2/3 里没有的源**（例如 `code_feedback`、`codeactinstruct`、`mind2web`、`nnetnav-*`、`go-browse-wa`、`synatra`、`agenttuning_*`、`openhands`、`CharlieDreemur_OpenManus-RL`）。**下之前先出「重叠清单 + 建议下哪些子集」**给我确认

**⑤ `harvardMadsys/freeinference_agentic_trace` → ❌ 不能训练，但有别的用**
- **`No message text is released`** —— 只有请求时序、token 用量、工具名、工具调用参数结构、缓存块 ID，**没有实际对话内容**
- ⇒ **排除出训练数据队列**
- **但建议告知 harness 线**：它有 **14 种 harness（含 claude-code）+ 267 账户 + 16 周真实 agent workload**（1.19M 请求 / 1.21M 工具调用），对 harness 线做 **workload 特征分析、性能建模、真实调用分布** 有价值（不是训练用）。**你只需在 MEMORY 里记一行转告，不用自己深挖**

**执行要求**

1. **先核实再下**（不要信我和网上的说法）：对每个要下的 repo 用 `HfApi().dataset_info(repo_id, files_metadata=True)` 拿**精确文件数/字节数/子集列表/license**，写进 MEMORY
2. **下载队列（按优先级）**：
   - **P0（本轮就下）**：`Agent-Ark/Toucan-1.5M`、`open-thoughts/AgentTrove`
   - **P1（自己判断后直接下，不必回来确认）**：`neulab/agent-data-collection` —— **只下「非重叠子集」，禁止全量 499GB**。判定规则给你，自己执行：
     - **不许下**（与 P0 重复 / 可从 P0 派生）：`toucan_1_5m`、`orca_agentinstruct`、`nemotron_terminal_corpus`、`swe-smith`、`swe-gym_*`、`nebius_SWE-agent-trajectories`（若 AgentTrove 已覆盖）
     - **要下**（AgentTrove/Toucan 里没有、且对"工具调用能力"有新信息）：`code_feedback`、`codeactinstruct`、`mind2web`、`nnetnav-live`、`nnetnav-wa`、`go-browse-wa`、`synatra`、`agenttuning_*`（alfworld/db/kg/mind2web/os/webshop）、`openhands`、`CharlieDreemur_OpenManus-RL`、`mini-coder`、`logicstar_swe-star`、`swe-play-trajectories`
     - **执行方式**：`hf download neulab/agent-data-collection --include "<子集>/*"` 逐子集下，**每下完一个报体积 + `df -h /nas_user`**
     - **额外收货（别漏）**：把 ADP 转换脚本也拉下来（`git clone https://github.com/neulab/agent-data-protocol`，代码很小）——它把异构 agent 轨迹统一成 SFT 格式，**以后转换我们自己的 cline trace 也要用它**
     - **判定依据落盘**：写 `run/data/adp_subset_plan.md`（每个子集：下/不下 + 理由 + 与其他源的重复情况）。**你自行决定，不要回来问我**
   - **P2（不下，但可改判）**：`microsoft/orca-agentinstruct-1M-v1` —— 纯合成、无真实工具执行，判低价值。**若你核实后发现它的 messages 里其实含 function-call 结构，可在 MEMORY 写明后改判并下**
   - **P3（排除训练）**：`harvardMadsys/freeinference_agentic_trace` —— `No message text is released`，无对话内容。**不要下**；只需在 MEMORY 记一行转告 harness 线（14 种 harness / 267 账户 / 16 周真实 workload / 1.19M 请求 / 1.21M 工具调用，可用于 workload 分析，非训练用）

3. **落盘**：`/nas_user/app.e0031982/datasets/<org>/<name>/`（与 IFM 那批同级）
4. **护栏不变**：`nice -n 19` + `ionice -c3` + `max-workers 2` + `setsid` 后台；**不挤 StepC 分词与 pretrain 训练**；`/nas_user` 余量 <5T 暂停报运维
5. **执行顺序（重要，别四批一起抢带宽）**：
   - **Step 1**：先 `HfApi` 探测全部 5 个 repo + 写 `adp_subset_plan.md`（纯元数据，几分钟，不占带宽）
   - **Step 2**：P0 两个（Toucan → AgentTrove）**串行**下载
   - **Step 3**：P0 完成后，再按 `adp_subset_plan.md` 下 P1 的非重叠子集
   - **Step 4**：边下边做调研报告（调研纯 web，不占 NAS 带宽，可与下载并行）
   - ⚠️ 若 StepC 分词（PID1677655）出现速率下降，**立刻把下载让位**，等分词跑完再继续
6. **登记**：`DATA_MAPPING.md` 记录每个 repo 的 `repo_id / 类型(预训练·SFT·RL) / 规模 / license / 是否含真实工具执行 / 是否带 reward / 与我们已有数据的重叠情况`
7. **污染检查**（关键，不可省）：这些 agent 数据是否混入 **SWE-bench / Terminal-Bench / BFCL / MCP-Universe / HumanEval** 测试集 —— 尤其 `AgentTrove` 含 `swesmith`/`codeforces`，`neulab` 含 `swe-smith`，**必须核对是否与我们的评测集重叠**，重叠的要么剔除、要么在评测时换题


**验收**
1. 5 个 repo 的实测元数据（文件数/字节/license），与我的初判对照，**若我判断错了要指出并说明**
2. P0 两个已落盘 + `DATA_MAPPING.md` 登记 + `df -h /nas_user` 前后对比
3. `run/data/adp_subset_plan.md`（P1 每个子集的下/不下决策 + 理由）+ 实际下了哪些、共多少 GB
4. ADP 转换脚本已 clone 到位（`agent-data-protocol`）
5. 与 SWE-bench / TB-2.1 / BFCL / HumanEval 的**污染检查结论**（重叠 or 不重叠，要有依据）
6. 调研报告 `reports/report_data_math_code_datasets_survey_zh.html` 已交付


> 🔴 **用户令 · 2026-11-15 08:5x（下载 3 个 IFM 数学/代码数据集 + 调研更多可用数据集）· 最高优先 · 未完成**

> **用户原话**：「安排data下载：https://huggingface.co/datasets/IFM/MegaMath 、 https://huggingface.co/datasets/IFM/Math-Reasoning 、 https://huggingface.co/datasets/IFM/Code-Reasoning。同时请它调研一下，要提升LLM的数学和编码能力，还有那些数据集可以用。」「放在 /nas_user 下面」

**一、落盘位置（用户指定）**

```
/nas_user/app.e0031982/datasets/IFM/MegaMath/
/nas_user/app.e0031982/datasets/IFM/Math-Reasoning/
/nas_user/app.e0031982/datasets/IFM/Code-Reasoning/
```
（与既有 `stack-v3-train` 同级，沿用 `/nas_user/app.e0031982/datasets/` 规范）

**二、三个数据集的已知情报（我查到的，你要自己复核）**

| repo | 性质 | 规模（查到的） | 备注 |
|:--|:--|:--|:--|
| **IFM/MegaMath** | **数学预训练语料**（非 SFT） | **1.12 TB**；论文口径 371B tokens | 子集：`megamath-web`(279B) / `megamath-web-pro`(15B 高质量) / `megamath-code`(28B) / `megamath-qa` / `megamath-text-code-block` / `megamath-translated-code`。arXiv 2504.02807，license odc-by |
| **IFM/Math-Reasoning** | **数学推理 SFT 风格** | 待核实（K2 Horizon 系列，5 个子集） | "Mathematical problem solving and dialogue data for training models to **reason rather than to recall**" |
| **IFM/Code-Reasoning** | **代码推理 SFT 风格** | 待核实（K2 Horizon 系列，**7 个子集**） | "Code problem solving data with the reasoning shown, split into worked solutions / direct answers / synthesised tasks" |

⚠️ **重要提醒（必须自己核实，不要照抄网上的说法）**：`IFM/MegaMath` 与 `LLM360/MegaMath` **可能是同一份数据的镜像/同名仓库**（论文作者相同、子集命名一致）。请用 `hf api` 或 `HfApi().dataset_info()` 核实**两者的 file tree 与 commit sha**：
- 若**确为同一份** ⇒ 仍按用户令下 `IFM/MegaMath`，但在 `DATA_MAPPING.md` 注明「≡ LLM360/MegaMath（按 sha 校验）」，避免后续重复下载。
- 若**不同** ⇒ 记录差异（文件数/大小/子集）。

**三、执行要求**

1. **先探测再下载**：`HfApi().dataset_info(repo_id=..., files_metadata=True)` 拿到**精确文件数 / 总字节 / 子集列表**，把数字写进 MEMORY，**再决定下载策略**（MegaMath 1.12TB 属大件，见第 2 条）。
2. **MegaMath 分层下载（不要一把梭全量）**：1.12TB 全量下载会让 StepC 分词期间磁盘/带宽吃紧。按用途分层：
   - **第一批（必下）**：`megamath-web-pro/*`（15B tokens 高质量）+ `megamath-code/*`（28B）+ `megamath-qa/*` + `megamath-text-code-block/*` + `megamath-translated-code/*`（这些是"提升数学能力"ROI 最高的部分）
   - **第二批（按需）**：`megamath-web/*` 全量 279B tokens ≈ 1TB，**先算 `/nas_user` 余量再决定下多少**（可按 `CC-MAIN-<年份>` 分批）
   - 用 `--include` 精确控制，**下完第一批就先报一次进度**，不要闷头下 1TB。
3. **护栏（沿用既有规范）**：
   - `nice -n 19` + `ionice -c3`，`--max-workers 2`，`setsid` 后台 + 日志落 `/tmp/`
   - **不挤 StepC 分词**（当前 PID1677655，6124/8192=74.8%，ETA ~21:00）与 pretrain 训练（`.29`）
   - **磁盘红线**：`/nas_user` 余量 < 5T 就暂停报运维
   - 🚫 不碰 `/nas_train`、不碰他人数据集、不删源文件
4. **落盘后登记**：更新 `doc/BaiZe-ISEDA2027/run/data/DATA_MAPPING.md`（repo / 子集 / 文件数 / 字节 / sha256 / license / 用途），并在 MEMORY 写一行。

**四、调研任务：还有哪些数据集能提升数学与编码能力**

产出 **中文 HTML 报告**（`reports/report_data_math_code_datasets_survey_zh.html`，**≤200KB / 0 script / 0 外链 / 内联 SVG**），**只调研不下载**（与 11-04 那次调研口径一致）。

**至少要覆盖这些方向（我给的起点，你可以补充/推翻）**：

- **数学预训练语料**：`Nemotron-CC-Math`（ICLR2026，133B tokens，3+/4+ 两档；论文称 8B 模型上 MATH +4.8~12.6、MBPP+ +4.6~14.3，**已超越 MegaMath/FineMath/OpenWebMath**）、`FineMath`（4+/3+ 两档）、`OpenWebMath`、`DeepSeek-Math` 语料（未公开，仅作参照）、`MathPile`
- **数学 SFT / 推理链**：`OpenMathInstruct-2`、`NuminaMath-1.5`、`MetaMathQA`、`Orca-Math`、`MathScale/MathInstruct`
- **代码预训练**：`The Stack v2`、`Stack-Edu`、`SmolLM-Corpus` 里的 code 部分、`StarCoderData`
- **代码 SFT / 执行反馈**：`OpenCodeReasoning`（NVIDIA）、`Self-OSS-Instruct`、`CodeFeedback`、`Magicoder`、`APPS`/`TACO`/`CodeContests` 训练切分
- **可验证奖励的 RL 数据**（对 posttrain 的 RL 阶段有用）：数学可验答案集、代码单测可跑集 —— 要特别标注**是否自带可执行验证器**，因为这决定能不能直接用于 RL
- **中文数学/代码**（如果 pretrain 需要中文占比）：标注语言覆盖

**报告必含**：

1. **一句话结论** + Top-5 推荐（按"ROI × 与我们缺口的匹配度"排序，不是单纯比规模）
2. **总表**：`数据集 | repo | 领域(数学/代码) | 用途(预训练/SFT/RL) | 规模(tokens或GB) | 语言 | license | 是否需申请 | 是否自带验证器 | 推荐度`
3. **与我们现状的匹配分析**：我们已有 `stack-v3-train`（代码预训练）+ 本令新增的 3 个 IFM 集 ⇒ **还缺什么**（例如：可验证 RL 数据、竞赛级难题、多语言代码）
4. **每个推荐项的去 HF 实测证据**（repo 存在、体量、license），🚫 **不许只抄二手描述**——这条是我们踩过坑的
5. **风险与坑**：license 限制、是否含 benchmark 污染（**尤其要检查是否混入 GSM8K/MATH/HumanEval/MBPP 测试集**，这对我们的评测有直接威胁）、去重情况

**五、验收**
1. 三个 repo 的**精确文件数与字节数**（`HfApi` 实测，不是估）
2. `IFM/MegaMath` 与 `LLM360/MegaMath` 是否同一份（sha 级证据）
3. 第一批下载落盘 + `DATA_MAPPING.md` 登记 + `df -h /nas_user` 前后对比
4. 调研报告交付，含 Top-5 推荐 + 污染检查结论


### ✅ 用户令 · 2026-11-13 18:5x（ETA 审计）· ✅ 已确认 → 原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-13 ETA审计」；结论：本次下载 3.546TB（非15.9TB），剩余1.195TB，ETA保守~14.7h，StepC护栏已修复。

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

### 📦 归档指针 · 2026-11-11 ~ 11-12 三条已交付令（原文见 `ARCHIVE_OPERATOR_DATA.md`）
- **11-12 EDA 脚本价值分析** → V1~828 文件/~0.01B tok、V2~6854/~0.04B tok、V3~139518；Tcl 唯一显著命中 39.2% / SKILL 未检出 / PyAether 0；报告 `reports/report_data_stackv3_eda_script_value_zh.html`
- **11-12 stack-v3-train 2TB 分词** → 4600/4600 shard DONE（245.8B tok / 926GB）；rerun 40 shard 0 ERR；产物已搬 `/nas_user`
- **11-11 vision 图文对** → 归因 + 25 源盘点 + Top5；报告 `reports/report_vision_textpair_sourcing_zh.html`


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

### 📦 归档指针 · 2026-11-07 10:10「stack-v3-train 正式放行」· ✅ 已交付（2TB / 7 批 / 4600 parquet / 0 inc / ROI 复盘有价值 / 97.6% 独特）。原文见 `ARCHIVE_OPERATOR_DATA.md`

> **现行口径（不必回读原文）**：
> - **授权范围**：`HuggingFaceCode/stack-v3-train` **仅 train 分片**（🚫 full 113.7TB）；总量红线 2TB；每批 ≤300GB，逐批实测/校验/回填后 commit 再起下一批；`/nas_user` 余量 ≥5T 不足则暂停报运维
> - **"优质"判定**：Python（含 PyAether/EDA 工具链）> C/C++ > Verilog/SV > Tcl > Makefile/CMake/Shell/Bazel；剔除 minified / generated / vendored / test fixture / 纯配置大文件 / 单文件 >1MB 生成物；剔除无 license / 星数极低 / 空仓库 / 纯文档仓库
> - **每批必交付**：`du -sb` 字节 + 文件数 + `.incomplete` 数 + 语言分布与 token 估算（给方法）+ 过滤命中数 + `DATA_MAPPING.md` 增行
> - **2TB 完成后要复盘**：每 TB 的 token / 独特性 / 与 UltraData-Code L2/L3 重叠度（抽样 1 万文件估 n-gram）；**2TB 不是要"下满"，够用即停**
> - `the-stack-v2` 仍**禁下**；其余单集 <1TB 按 ROI 自排

---


### 📦 归档指针 · 2026-11-07 08:5x「代码语料放行 stack-v3-train」· ✅ 已交付（ROI表+8源25.14GB+stack-v3调研+2TB全下+ROI复盘）。现行要点：`the-stack-v2` 🚫禁下；`stack-v3-train` 仅 train 15.9TB（🚫 full 113.7TB）；其它单集 <1TB 按 ROI 自排；code 补料属**低压力背景任务**（用户：有也行无也行、不急、不挤 S1 带宽）。原文见 ARCHIVE「归档块 · 2026-11-11」

> 📦 **归档指针 · 2026-10-31 ~ 11-04 五条旧令**（原文见 `ARCHIVE_OPERATOR_DATA.md`）：11-04 B 类 agentic 下载 12/12 落地 78.73GiB ｜ 11-04 RL+数学+agentic 调研 + 复杂推理+代码 SFT 调研 → `report_data_reasoning_code_sft_survey_zh.html`(79KB)+`report_data_rl_math_survey_zh.html`(38KB)，口径=只调研不下载、真去 hf.co 核实、奖励信号单列、与盘上 12 源去重 ｜ 11-04 A 类长上下文下载 ｜ 11-04 85M 确认 ｜ 10-31 长上下文+agentic 调研 → `report_data_lc_agentic_survey_zh.html`(117KB)，decay-B 闸门 = `en_v1_4` 里 ≥32K 仅 2.52% token、≥128K 仅 0.03%，目标 ≥20%/≥1%
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


> 📦 **归档指针 · 2026-10-25 三条旧令**（均已在 `run/ARCHIVE_OPERATOR_DATA.md`）：
> - **11:0x「重盘盘点 + 未分词开跑」** → 已被 12:5x 令取代。要点：224 核是上限不是指标；分词器 `tokenizer_eod`（vocab 129,281 / pad 129,408）；产物落 `baize-data/tokenized/<镜像下载路径>/`；每前缀必须有 manifest；`setsid` 后台。
> - **10:3x「删不可对应产物」** → 已执行完毕：判定 110 shard，删 78（被 `full_*` 覆盖，3.69 TiB）+ 删 32（无法产物级对应，1.91 TiB），`baize-data/text/` 现 110 shard / 8.93 TB。
> - **08:0x「重写报告 v2」** → 已闭合，被 12:5x 令取代。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

> 📦 **归档指针 · 2026-10-17 ~ 10-23 六条旧令**（原文均已在 `run/ARCHIVE_OPERATOR_DATA.md` 或对应 daily）：
> - **10-23 22:1x**：代理走 92.25 + hf.co 直连；迁移铁律 = `rsync -a` 不用 `mv`、校验 shard+字节一致才删源、先建软链接、`/nas_env` 余量 ≥ 数据×1.1
> - **10-21 04:0x**：MiniCPM5 全量分词完成（574 shards / 1056.36B tokens / 4.24TB），env14 亦完成（110/110 / 8.88TB）
> - **10-20 15:5x**：en_v1_4 下载恢复完成
> - **10-18 21:0x**：env14 全量分词 110/110 完成（2238.14B tokens / 8.93TB）；"32 或 64 核"限速口径已被 10-25 的 96–224 四档标定取代
> - **10-18 10:2x**：git push 修复（需剥离 HF 代理：`env -u http_proxy -u https_proxy git push`）
> - **10-17**：本线 `/tmp` 残留清理完成

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的"等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X"只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

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
