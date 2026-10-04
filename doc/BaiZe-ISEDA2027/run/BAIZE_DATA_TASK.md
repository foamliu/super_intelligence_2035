# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。
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

### 📉 记忆维护规程（2026-10-03 运维新增，**硬性**）
> 理由：`MEMORY_*.md` **每次唤醒都被 agent 全文读取** → 越大越烧 token。当前 `MEMORY_DATA.md` ≈ **85KB（超标）**。
- **上限**：本线 `MEMORY_DATA.md` 控制在 **≤ 32KB**；**下次唤醒立即执行一次滚动归档**。
- **滚动**：把**较早的唤醒流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-data/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 「进度快照」③ 「运维问答」（**这一区不清**，因运维靠它读答复）④ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---



| 项 | 当前值 |
|:---|:---|
| **🆕 D-CLEAN-4（2026-10-04 · 最新）** | 🔴 **`/nas_train` 需要清理 → 用 sudo 盘点各目录大小，找可删除的大目录，重点 `/nas_train/app.e0031982`**；**只盘点不删除**；🚫 绝不整树 `du`（只用 `df` + 有界定向 `du`，每条带 `timeout`）→ 详见顶部「运维指令 · 2026-10-04（D-CLEAN-4）」 |
| **🆕 下载白名单（2026-10-03 最新 · 覆盖一切下载类指令）** | **只下 ① `ultrafineweb_l1_en_hq` + `ultrafineweb_zh`（base 族剩余）② GPIC**；🔴 **立即停 `ultrafineweb_en_v1_4`**（43 天 / 非必需 / 阻塞后两项）；🚫 **白名单外一律不下载、不调研、不推荐**（含 `UltraX-Preview`）→ 详见顶部「运维指令 · 2026-10-03（下载白名单锁定）」 |
| **当前指令** | 🎯 **（2026-10-01 夜 · 三次修订）按序做这几件**：<br>**① ⭐ 重下 `UltraData-SFT-2605`** —— 运维**已在 HF 网页点同意条款**（原先 `gated=auto` 卡住，落盘只有 README + LICENSE + 179 个 `.lock`）。下完报**实际字节数 + 文件数 + 与 HF 官方清单的一致性**。<br>**② 🔴 当前主攻 = §0.3 + §0.4「R2 阶段」** —— 上一轮 R 的**事实层合格、结论层不合格**（两处）：<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.3（LLM 侧 / P-8 数据方案）**：你拿 **"BaiZe 计划未用"** 当理由跳过了 `Ultra-FineWeb`(base) / `UltraX-Preview` / `UltraData-RL-2609`，**那是循环论证**（计划是在不知道这些源存在时定的）。<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.4（视觉侧 / 找更多图文对）**：你**自己**给了「视觉编码器训练数据**严重不足**」的结论（`en500k` 仅 50 万对、LLaVA 85M 的 caption 99.7–100% 被截断），**却从没去 HF 找过任何通用图文对** —— 反而把问题缩小成「要不要找 EDA 版图/原理图」然后答「不值得」。**那是答错了题。**<br>&nbsp;&nbsp;&nbsp;&nbsp;**本轮两份都要交**：**8 源事实表填满（无 `?`）· base vs L3 重叠率数字 · P-8 三档投料+下载清单** **＋** **本地多模态源逐条实测 · ≥10 个 HF 通用图文对候选（含实测短 caption 率）· 前 3 推荐 + 下载命令**。<br>&nbsp;&nbsp;&nbsp;&nbsp;🚫 **禁止"待定"/"视情况"/"不在计划内"/"不值得找"（除非先给出找过的清单与规模）**；**若判定为新增且磁盘允许 → 直接开始下载**。<br>&nbsp;&nbsp;&nbsp;&nbsp;💡 **⚠️ 一条新增的硬筛条件（运维补充）**：**必须筛掉「只有 image URL、没有 image bytes」的数据集** —— 本地 `Recap-DataComp-1B` 就是**只有 URL**，而那些 URL **绝大多数被公司网络限制、下不下来**，**等于不可用**。<br>&nbsp;&nbsp;&nbsp;&nbsp;**→ A / B 两表都要新增「图像形态」列（`bytes` / `URL-only` / 待抽验），且必须抽分片实测取证（贴原文）；URL-only 一票否决、不得进推荐。**<br>&nbsp;&nbsp;&nbsp;&nbsp;⚠️ 预期会被淘汰的"大集"：`LAION-*` / `COYO-700M` / `DataComp-1B` / `DFN-*` / `RedCaps` / `YFCC` / `CC12M` / `CC3M` / `SBU` / `WIT` / `PixelProse` / **`Recap-DataComp-1B`（已确认）** —— 若大集普遍 URL-only，<b>请把重心转到"小一些但真的带图"的集</b>，并如实说明这个现实。<br>**③ 🚫 两条硬规矩（运维 2026-10-02）**：**（a）10 月份不要再提任何"领域化"相关的事** —— EDA / 领域语料 / Stage (ii)「领域模型」**全部留白**（运维：「一段时间有一段时间的主要矛盾」→ 当月专注 **Stage (i) 与 Stage (iii)**）；⚠️ 唯一例外：`EDA-Eval-PyAether` 158 任务的**黑名单红线照常执行**。**（b）当前主攻 = §0.5 + §0.6 + §0.7** —— **§0.5**：推 `Ultra-FineWeb`(base) 下载 + 处置 `/nas_train` 1.67TB 旧副本；**§0.6**：🎯 **P-8 数据配方 —— follow MiniCPM5/Xmodel-2 的 WSD 双阶段配比**（用 Xmodel-2 Table 2 的 8 个 + Table 3 的 6 个做代理指标做实验定）；<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.7 🆕（运维 2026-10-02 追加）**：① 🚫 **停掉 85M（LLaVA）下载**（优先级最低，释放带宽给 base 与 gpic）；② ⭐ **给出 base 下载 ETA**（分"复用旧副本/不复用"两种）；③ ⭐⭐ **复用 `/nas_train` 那 1286 个 `ultrafineweb_en`（≈1.67TB ≈ 全量 56%，省 ≈2 天）**；<br>&nbsp;&nbsp;&nbsp;&nbsp;**优先级**：**base（stage (i) 要用）> 配比实验 > gpic（stage (iii) 要用）> 85M（已停）**。 |
| **优先级覆盖** | **§0.5/§0.6/§0.7（base 下载与估时 / base-en 复用 / P-8 配比实验）> 其他一切**；<br>SFT-2605 重下**继续并行**（已过半）；<br>🚫 **85M（LLaVA）下载已按要求停下**；<br>`phase1/2/4`（重 I/O，等下载）**本阶段不碰**；<br>🚫 **领域化相关一律不碰**（10 月份） |
| **状态索取** | `<无>`（若运维写入具体问题，本轮**先答该问题**再干活，答案写进 `MEMORY_DATA.md` 顶部的"运维问答"区） |
| **暂停标志** | `<无>`（若写入 `STOP`，本轮**只更新记忆、不做任何 I/O 与数据处理**，然后退出） |

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

## 0. 🎯 当前主攻

> **R 阶段（只答两问）✅ 已收敛** → 产出 `run/DATA_RESEARCH.md` v1.1（事实层扎实）。
>
> | 节 | 状态 |
> |:--|:--|
> | §0.1 / §0.2 | ⏹ **历史**（R 阶段的两问，已完成；§0.2 已被 §0.4 取代） |
> | **§0.3** | 🔴 **当前主攻（LLM 侧）** —— P-8 数据方案 |
> | **§0.4** | 🔴 **当前主攻（视觉侧）** —— vision encoder 训练数据：去 HF 找更多通用图文对 |
>
> 原因：上一轮 R 的**事实层合格、结论层不合格**（两处，详见 §0.3 与 §0.4 开头）。
> **本轮两份都必须给出可执行的结论。**

---


---

## 📁 调研轮次已归档（**为省 prompt token**）

`§0.1 / §0.2 / §0.3 / §0.4`（R 与 R2 调研）的完整任务原文已移至 **`run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md`**。

- 这些**均已完成**；结论以 `DATA_RESEARCH.md` / `DATA_LEDGER.md` / `MEMORY_DATA.md` 为准。
- **需要时再去读归档**；**不要**把整份归档读进上下文。
- 当前主攻 = **§0.5 / §0.6 / §0.7**（见下方）。

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

## 0.6 🎯 R4 阶段 —— **P-8 数据配方：follow MiniCPM5 / Xmodel-2 的 WSD 双阶段配比**（运维 2026-10-02 指令）

> ### 定位
> 运维明确：**P-8 的数据方案要「follow MiniCPM5」** —— 即 **WSD 的两段各用不同配比**：
>
> | 阶段 | 数据源（运维给的假设） | 主次 |
> |:--|:--|:--|
> | **Stable**（WSD 的 S 段） | `Ultra-FineWeb`(**base**) · `UltraX-Preview` · `UltraData-Math` · `UltraData-Code` | **以前两者为主** |
> | **Decay**（WSD 的 D 段） | `Ultra-FineWeb-L3` · `UltraData-Math` · `UltraData-Code` · **`UltraData-SFT-2605`** · **`UltraData-SFT-Agent-2609`** | 适当配比 |
>
> **配比不是拍的，要做实验定** —— 由你（data agent）来设计并跑。

### 🔴 一条可能改变全局的发现（来自 `Xmodel-2/xmodel-2.tex:144-154`，请务必读原节）

Xmodel-2 的 decay 段配比搜索结论：

> - 把搜索空间收敛到**两个问题**：**① SFT 数据的总体占比；② SFT 内部的类别分布**
> - **跑了 400+ 次试验** → 最优 **SFT 占比落在 60%–69%**，实际取 **64%**
> - SFT-Mixed 由 **5 类构成：Mathematics / Code / Logic / Knowledge / Commonsense**（**CoT 归入 Logic**）
> - **数学与代码的「指令格式」数据 > 「预训练格式」数据**
> - SimHash 去重（bucket 1M）**+1.7%**；整体复杂推理 **+29.31%**

⚠️ **关键含义**：**SFT 数据是进到「预训练 decay 段」里的，而不是事后再做一遍独立的 SFT** ——
这与运维给的 decay 假设（含 `SFT-2605` + `SFT-Agent-2609`）**一致**，也与 MiniCPM 的路线一致。
→ **它模糊了 Stage (i)/(ii) 的边界**：**decay 段本身就是"带 SFT 数据的退火"**。
→ **必须在报告里点明这一点**（这是 P-8 配方的核心）。

**另一条法理依据**（供报告引用）：`xmodel-2.tex:142` 引 `ye2024datamixinglaws` ——
**「小模型上的配比实验可以有效迁移到更大模型」** → **所以我们可以在小规模上搜配比**，不必在全量上试。

### A. 先**核实**运维的假设（不许直接采信，也不许否掉）

1. **MiniCPM5 的 stable/decay 两段各用了哪些源、什么占比？**
   - 上轮结论是「模型卡**未公开逐源百分比**」→ **本轮再查**：模型卡 / 技术报告 / `openbmb/MiniCPM5` collection 的 dataset card / UltraData 平台论文（arxiv 2602.09003）。
   - **若仍查不到** → 写「未找到」+ 列出查阅清单，**但运维给的这张表就作为"待验证的工作假设"直接用**（见 B）。
2. **确认 `UltraX-Preview` 与 `Ultra-FineWeb`(base) 的关系**（上轮已知 UltraX 里有一支叫 `UltraX-Ultra-FineWeb`）→ **是否重复**？

### B. ⭐⭐ 配比搜索实验（**本轮的核心**）

**搜索设计（照 Xmodel-2 的思路收敛空间）**：

| 段 | 候选源 | 代理指标 | 备注 |
|:--|:--|:--|:--|
| **Stable** | `base` · `UltraX-Preview` · `Math` · `Code` | **Xmodel-2 Table 2 的 8 个**（Commonsense） | 运维假设"以 base / UltraX 为主" |
| **Decay** | `L3` · `Math` · `Code` · `SFT-2605` · `SFT-Agent-2609` | **Xmodel-2 Table 3 的 6 个**（Complex Reasoning） | ⚠️ **必查 SFT 占比**（Xmodel-2 是 **60–69%**） |

**两套代理指标的确切清单**（已从本地 tex 核出，照用）：
- **Table 2（8 个）**：`ARC-C` · `ARC-E` · `BoolQ` · `HellaSwag` · `OpenBookQA` · `PiQA` · `SciQ` · `Winogrande`（+ Avg）
  —— 出处 `Xmodel-2/xmodel-2.tex:198,207`
- **Table 3（6 个）**：`GSM8K` · `MATH` · `BBH` · `MMLU` · `HumanEval` · `MBPP`
  —— 出处 `Xmodel-2/xmodel-2.tex:73,253,260`

**执行要求**：
1. **不要在 2.2B 全量上试** —— 用**小模型 / 短跑**搜（依据 Data Mixing Laws）。
   **基线口径**：复用 Round 1/2 的 8 卡 setup 与 5000 步短地平线，或更短。
2. **每轮训练后跑上面两套指标**（**评测基建已就绪**：P-6 已把 `ckpt → HF → lm_eval 8 集` 打通，
   见 `MEMORY_PRETRAIN_2B.md`；Table 3 的 6 个需另接，评估一下工作量）。
3. **给出可执行的配比建议**（不是"趋势"，是**具体百分比**），并说明**试验次数与置信度**。
4. **明确 SFT 占比**：这是 Xmodel-2 说最关键的一个轴。

> ### 🎯 **用哪台机器 —— 运维定的规则（2026-10-02）**
> **配比实验用「它所服务的那个正式训练」所用的机器**（因为配比实验与正式训练之间有依赖关系）：
>
> | 配比实验服务于谁 | 用哪台 | 卡 |
> |:--|:--|:--|
> | **LLM pretrain（P-8，即 §0.6 的 WSD 双阶段）** | **`.29`** | LLM 的卡 |
> | **vision（若将来也做配比）** | **`.12`** | vision 的卡 |
>
> **→ 本节 §0.6 的配比实验用 `.29`**（运维原话：**LLM pretrain 的正式训练依赖配比实验**）。
> ⚠️ **`.29` 上的排期**：P-4R（1 卡，≤2h）→ **配比实验** → 恢复 P-5b。
> **三者都在 `.29`，需要串行/让卡 —— 请先出方案与 ETA，再由运维排。**
> ⚠️ **`.12` 上 vision 的 R9 正在用 8 卡 → 不要占 `.12`。**

### C. 交付物
1. **`run/DATA_MIX_RECIPE.md`**（新文件）：
   - 运维假设的**核实结论**（或"未找到"+采纳为工作假设）
   - **两段的配比建议**（具体百分比 + 理由 + 试验次数）
   - **代理指标的实测值**（Table 2 / Table 3 分项 + Avg）
   - **可复现命令**
2. **P-8 数据就绪清单**：每个源是否就位、缺多少、下载/切分 ETA。
3. 更新 `MEMORY_DATA.md` + `DATA_LEDGER.md` + git push。

### 完成判据
- [ ] 运维假设**已核实**（或明确"未找到"+ 列出查阅清单）
- [ ] **Stable 段**配比给出**具体百分比** + Table 2 实测
- [ ] **Decay 段**配比给出**具体百分比**（**含 SFT 占比**）+ Table 3 实测
- [ ] 报告里**点明"decay 段即带 SFT 的退火"**这一含义
- [ ] 🚫 **全轮不得出现领域化相关内容**（运维硬规矩）

---


---
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

## 1.1 数据落盘地图（实测背景 · 2026-10-01 勘定）

> 本节由**实地探查**得出，用于纠正本任务书成稿时对数据位置的误记。
> 每轮唤醒 / phase 复核时以此节为索引，`DATA_LEDGER.md` 为实测明细，二者互相印证；**最终一律以实测为准**。

**三块挂载 + 三条 HF 组织名线索**（HuggingFace 数据集按 `org/repo` 落盘）：

| 挂载 | 定位 | 关键内容 |
|:---|:---|:---|
| `/nas_train/app.e0031982/datasets/` | **多模态主库**（生产 + 派生） | `mvp-lab/`（LLaVA-OneVision-1.5 全家桶）、`baize-vision/`、coco/gqa/imagenet/laion2B/FineVision/LLaVA-Pretrain/MMMU… |
| `/nas_inference/app.e0031982/datasets/` | **只读源 / 下载中转**（**纯文本主力在此**） | `openbmb/`（Ultra-FineWeb-L3、UltraData-Code/Math/SFT-2605/SFT-Agent-2609）、`stanford-vision-lab/gpic` |
| `/nas_user/app.e0031982/datasets/` | 少量多模态 / 领域语料 | `mvp-lab/`（OV1.5 webdataset、OV2）、`BLIP3o/`、`UCSC-VLAA/`、`Amshaker/`、`ayoubkirouane/`、`cxmt/` |

**① 多模态主库 —— `/nas_train/app.e0031982/datasets/`**
- `mvp-lab/`（⚠️ 是连字符 **`mvp-lab`**，不是 `mvp_lab`）— LLaVA-OneVision-1.5 系列：
  - `LLaVA-OneVision-1.5-Instruct-Data`（183 个任务子集，SFT / 对齐主体）
  - `LLaVA-OneVision-1.5-Mid-Training-85M`（子集 coyo/datacomp1b/imagenet/laioncn/mint/obelics —— 即 phase0 已盘点项）
  - webdataset 派生：`-packed-webdataset` / `-webdataset` / `-webdataset-16384` / `Quick-Start-3M` / `MultiMixQA-opt46|47`
  - `LLaVA-OneVision-1.5-RL-Data`、`LLaVA-558K-Webdataset`、`LLaVA-NeXT-780k*`
- `openbmb/Ultra-FineWeb`（纯文本，**仅** Ultra-FineWeb 基础版，非完整 Ultra-* 套件）
- `baize-vision/`（en500k / eval5k —— vision agent 派生产出）
- 其他多模态（可选补充源）：`coco`、`gqa`、`imagenet-1k`、`laion2B-en-aesthetic`、`FineVision`(188 子集)、`LLaVA-Pretrain`(664 子集)、`MMMU`、`ocr_vqa`、`textvqa`、`vg`、`conceptual-captions-12m-webdataset`、`LLaVA-CC3M-Pretrain-595K`、`LLaVA-Instruct-150K`
- 非数据（勿混）：`stanford-corenlp-full-2016-10-31`（NLP 工具，非斯坦福视觉数据）

**② 纯文本主力 —— `/nas_inference/app.e0031982/datasets/openbmb/`**
- `Ultra-FineWeb-L3`（Stage(i) 主体）、`UltraData-Code` / `UltraData-Math`（退火源）、`UltraData-SFT-2605` / `UltraData-SFT-Agent-2609`（Stage(ii) SFT）
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/openbmb`，实际在 **`/nas_inference`** 挂载。

**③ 斯坦福视觉数据 —— `/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic`**
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/stanford-vision-lab`，实际在 **`/nas_inference`**。`gpic`（含 train / test / reference_stats）。

**④ 少量多模态 / 领域 —— `/nas_user/app.e0031982/datasets/`**
- `mvp-lab/`：`LLaVA-OneVision-1.5-Mid-Training-85M-webdataset`、`LLaVA-OneVision-2-Data`、`ov2_quickstart`
- `BLIP3o/BLIP3o-Pretrain-Long-Caption`、`UCSC-VLAA/Recap-DataComp-1B`、`Recap-DataComp-1B`
- `Amshaker/Mobile-O-Pre-Train`、`ayoubkirouane/CircuitVQA`
- `cxmt/`（EDA / 电路相关标注与 benchmark —— ~~phase3 领域排查时可查~~ **🚫 该线已取消，不再排查**）

> 对数据 agent 的影响：phase0 已盘点的主路径（`/nas_inference/openbmb`、`/nas_train/datasets/mvp-lab`）正确；
> 但 phase0 尚未覆盖 `②` 里的 Ultra-FineWeb 基础版（`/nas_train/.../openbmb`）、`③ stanford-vision-lab/gpic`、`④ /nas_user` 整块 —— 后续 phase 复核时把这些补齐进 DATA_LEDGER。

---

## 2. 阶段与推荐执行顺序

```
推荐顺序： 【🎯 当前】phase1 validate（含 ① SFT-2605 重下） → phase0 inventory ✅ → phase5 isolation ✅ → phase2 text → phase4 mm → phase6 handoff
🚫 phase3 domain —— **已取消，从流水线移除**（见运维指令区 ②）
```

> **为什么 phase5（污染隔离）排在最前**：它必须在**任何"训练可消费产物"产出之前**就位。
> 如果先切了数据再立闸，已经切好的数据要全部重扫、甚至重切——**白做一遍**。

| 阶段 | 做什么 | 完成判据 |
|:---|:---|:---|
| **R** `research` 🎯 **当前主攻** | 用 `cimi-search` / `cimi-fetch` **只回答 §0 的两个问题**（LLM 数据够不够+配比 / Vision 数据够不够+配比） | `DATA_RESEARCH.md`：两问各四小项全有结论 |
| **phase0** `inventory` ✅ | 对 `/nas_inference` 与 `/nas_train` 上每条数据线**实测**：文件数、总字节、目录结构、抽样看格式；确认哪些路径真实存在 | `DATA_LEDGER.md` 初版；**与方案 §1 的差异逐条列出** |
| **phase5** `isolation` | 建 EDA-Eval-PyAether 的黑名单指纹 + 训练集侧扫描脚本 + SFT 同闸 | `CONTAMINATION_CHECK.md` 初版 + 可复用脚本 |
| **phase1** `validate` | 下载完整性（parquet 全量可开 / tar 可解 / shard 无缺号）；损坏清单 | 损坏/缺失清单 + 校验命令 |
| **phase2** `text` | 通用文本分词打包成 `.bin/.idx`（stable 主体 + 退火源），**复用 Round 1 脚本** | 训练实测能加载并跑 10 步冒烟 |
| **phase3** `domain` 🚫 **已取消** | ~~EDA 领域语料排查（有哪些、在哪、能否导出/授权）→ 确认后入库并过闸~~<br>**运维 2026-10-01 正式取消**：评测 prompt 由 docstring 生成、**与语料天然同源**，"把测试集放进训练集"没有意义 | —（不再产出） |
| **phase4** `mm` | 多模态下载完成后：校验 → 统计 → 切子集 → webdataset 打包 → held-out 评估集 | Stage (iii) 能直接开跑 |
| **phase6** `handoff` | 清单终版 + 污染报告终版 + 结果 HTML + 可复现命令 | 可交接给训练 |

---

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

## 4. git 与共享工作区规则

### 4.1 前提：这是一个**共享工作副本**

**本任务、vision 任务、pretrain 任务共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

- **只需一个人 pull，其余立刻看到**：别的 agent 拉取后，你读到的 `$TASK_MD` 与所有文件同步更新。**不要重复 pull。**
- 工作区里**陌生的未提交改动很可能是别的任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉别人的成果。
- 多个 loop 各自 `git add -A && commit && push`（每 5 小时），**会互相把对方在途文件一起提交**，这是既有设计的已知副作用，**不要去"修正"它**。

### 4.2 你的 git 操作规程

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_DATA.md DATA_LEDGER.md CONTAMINATION_CHECK.md run/data_pipeline/ daily-memories-data/`
   🚫 **不要用 `git add -A`**——会把别的任务的在途文件卷进你的提交。
3. 若 behind / diverged：`git pull --rebase origin main`。
   - `cannot rebase: You have unstaged changes` → 是**多方在途改动**：先 commit 自己要提交的文件再 rebase；🚫 不要 stash/丢弃别人的改动。
   - `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：等 30–60 秒重试（≤3 次）；仍失败就记一行流水并**跳过本次 git 操作**。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind。
5. 流水记一行 git 结果。

> 参照：vision agent 在 `daily-memories-vision/2026-10-01.md:198` 用 `git pull --rebase` 恢复过，沿用同一做法。

### 4.3 数据产物**不入库**

`.bin/.idx`、webdataset tar、原始数据集**一律不提交 git**。只提交：`doc/` 下的文本（md/html/json）与 `run/` 下的**脚本**。
在报告与流水中写清产物的**绝对路径 + 规模 + 校验和**，训练侧据此取用。

---

## 5. 资源与约束

- **节点**：本 agent 常驻 `10.239.2.12`（主机 `whag0pgpuap12`）；数据在 NFS（`/nas_inference` 只读源、`/nas_train` 产出）。
- ⚠️ **与 GPU 任务共享 NFS 与带宽**：
  - **本节点 `.12` 有 2 个 HF 下载任务在跑**（`hf download`，2026-10-01 实测，各已运行约 1 小时+）：
    1. `mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M` → 写入 `/nas_train/app.e0031982/datasets/`（多模态下载进行中）
    2. `stanford-vision-lab/gpic` → 写入 `/nas_inference/app.e0031982/datasets/`（带 HF token；⚠️ token 已暴露在进程参数里，建议轮换，勿写进文档/日志）
    **下载期间不要做重 I/O / 全量扫描**，会互相拖慢
  - vision 任务需要一次"**无争用的干净吞吐测量**（R2-4）" → 启动重 I/O 前先读 `run/MEMORY_VISION.md` 看它进度，**优先避让**
  - pretrain 任务在 `10.239.2.29` 跑训练（另有协调规则）
- **不占用 GPU**（本任务不是 GPU 任务）；也**绝不杀他人进程**。
- **每轮唤醒单次预算 ≈ 25 分钟**；有长时任务时把 `WAITING` 置 1 让 loop 拉长睡眠。

---

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

