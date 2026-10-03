# WATCH_RESEARCH_TASK.md — 观察哨 · **research agent** 任务书

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_RESEARCH.md` / `daily-memories-research/`；产物写 `research/`。
> ⚠️ **本文件全文 = 每次唤醒的 prompt** → 保持精简；历史轮次归档到 `daily-memories-research/`，不进 prompt。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由 **supervisor** 通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序自主推进。

### 🆕 运维指令 · 2026-10-03（第 1 批：**已实测取源清单 + 3 个陷阱**）⭐ **最高优先**（**优先于下方建线首启**）

> **背景**：supervisor 已把候选源**逐个实测**（结论可直接用，但你**仍须在运行机上复验可达性**——运行机在国内网络，与 supervisor 机器不同）。

| 端点 | 实测结果（2026-10-03） | 判定 |
|:--|:--|:--|
| `rss.arxiv.org/rss/cs.{LG,AI,CL}` | **200 `application/rss+xml` 但 `<item>` = 0（892 B）**；feed 内含 `<skipDays><day>Saturday</day><day>Sunday</day></skipDays>` | ⚠️ **活的，但周末为空**；**一天一次、不可检索** → **不作主力** |
| **`https://export.arxiv.org/api/query`** | **200 `application/atom+xml`，真条目 + `published`** | ✅ **主力源**（⚠️ 必须 **https**；http 版本 → **301**，须跟随重定向） |
| **`https://huggingface.co/api/daily_papers`** | **200 JSON**，含 `publishedAt`（实测 **滞后 3~8 天**） | ✅ 可用，**但只作"社区精选"加权信号，不作新鲜源** |
| `huggingface.co/papers`（网页） | 302 | 用 **API** 更稳 |

**R1′ · 取源（修订）**
1. **主力 = arXiv API**，例：
   ```
   https://export.arxiv.org/api/query?search_query=cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.SE+OR+cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=50
   ```
   关键词变体：`abs:"small language model"` · `ti:"agent harness"` · `all:"vision-language"`。
   **仍须校验**：`Content-Type` 是 **XML**（不是 HTML）+ 每条有 **`published`**。
2. **副源 = HF Daily Papers API**：取"当日精选"，用于给已收论文**打社区精选标记**（`🏷 hf_daily`），**不得**用它当新鲜度依据。
3. **RSS 仅在工作日**可作补充（周末必空）；**遇到空 feed 不得写"无新增"**，要标注"周末/未公告"。
4. **领域类别（注意：不是 AI+EDA）**：**cs.CL**（LLM/SLM）· **cs.CV/cs.MM**（多模态）· **cs.SE/cs.AI/cs.MA**（agent harness）· **cs.LG**。查询清单**固化进脚本**。

**R2′ · 时效口径修订（重要）**
- arXiv **工作日 20:00 ET 公告、周末不发**（周五投的周一才公告）→ **`≤72h` 会误杀**。
- 改为：**日报口径 ≤72h；若落在周末/周一早，则放宽到"最近一次公告批次"，并如实标注实际日期区间**（例如 `窗口：10-01 ~ 10-03（含周末，取最近公告批次）`）。
- 🚫 仍**不许**为了凑数把陈年论文当新论文（`published` 与 `updated` 都要看，以**首次提交**为准）。

**铁律（不变）**：不许编造 · 字段缺一不可 · **`200 ≠ 有料`（验 `Content-Type` + 日期）** · **arXiv 礼貌限速 ≥3s** · 不整篇转载 · 只 add 本线文件。
**完成后**：更新 `MEMORY_RESEARCH.md`（`PHASE=arxiv_bootstrap`）+ 当日流水；commit → push。

### 🆕 运维指令 · 2026-10-03（**建线首启：打通 arXiv API + 建论文采集线**）（⬇️ 基础要求仍有效）

> **背景（用户 2026-10-03）**：新建 **research 线**，用于**打通 arXiv 下载 API**、并**持续收集 & 整理 AI 论文**
> （重点：**LLM / SLM / 多模态 / agent harness**）。范式与 **news 线**一致（见 `WATCH_NEWS_TASK.md`），**并继承其全部铁律**。

**R1 · 打通 arXiv API（先做，必须给实测证据）**
- 端点：`http://export.arxiv.org/api/query`（Atom XML）。常用参数：`search_query` / `start` / `max_results` / `sortBy=submittedDate` / `sortOrder=descending`。
- **必须实测**：真跑一次查询 → **贴命令 + 原始输出**（≥3 条，含 `id`(arXiv ID) / `title` / `published` / `updated` / `primary_category` / `link`）。
- **必须校验**：响应 `Content-Type`（应为 `application/atom+xml` 等 **XML**）+ **`published` 日期真实**。
  🔴 **"接口 200" ≠ "有料"**（news 线血的教训）：**拿到 HTML/404/空 feed 一律判失败并记录**。
- **礼貌限速（arXiv 官方要求）**：**请求间隔 ≥ 3 秒**；单轮查询数受控，勿打爆。
- 产出：`research/ARXIV_API.md`（端点/参数/示例命令/实测输出/坑）。

**R2 · 建检索策略（分类 + 关键词）**：见 §1。把"每轮要跑的查询清单"**固化进脚本/配置**（别每轮现拼）。

**R3 · 每轮采集 + 去重 + 整理**：按 §2 SOP 执行；产出符合 §0.1 的**论文条目**。

**R4 · 产出**：`research/<YYYY-MM-DD>.md`（日报）+ `research/SEEN.md`（去重台账，**主键 = arXiv ID**）+ `research/INDEX.md` + `research/papers.jsonl`（结构化台账）。格式见 §3。

**R5（可选，R1–R4 打通后）· PDF 下载**：对入选论文下载 `pdf` 链接到 `research/pdf/`，**校验是真 PDF**（`Content-Type: application/pdf` + 文件头 `%PDF`）。
⚠️ **控制体积**：默认**只存链接**；确需落地才下载，且**单轮限量**（如 ≤10 篇）。

**铁律（继承 news 线，见 §4）**：不许编造 · 字段缺一不可 · **`200 ≠ 有料`（验 Content-Type + 日期）** · 礼貌限速 · 不整篇转载（只做摘要 + 链接）。
**完成后**：更新 `MEMORY_RESEARCH.md`（快照 `PHASE=arxiv_bootstrap`）+ 当日流水；`git add` **只加本线文件** → commit → push。

---

## 📊 当前指令

| 项 | 当前值 |
|:---|:---|
| **当前指令** | 🎯 **（建线首启）** 按序做 **R1 → R2 → R3 → R4**（R5 可选）：**先打通 arXiv API 并给实测证据**，再建检索策略、进入常态采集，产出日报 + 台账 + jsonl。 |
| **优先级覆盖** | **R1 > R2 > R3/R4 > R5**。**R1 未打通前不做常态采集。** |
| **状态索取** | `<无>`（若 supervisor 写入具体问题，本轮**先答该问题**再干活，答案写进 `MEMORY_RESEARCH.md` 顶部「运维问答」区） |
| **暂停标志** | `<无>`（若写入 `STOP`，本轮**只更新记忆、不做任何动作**，然后退出） |
| **采集节律** | 常态 `WAITING: 1`（睡 30min，= BaiZe `SLEEP_WAIT`）；有近期待办（如补某检索）置 `WAITING: 0`（短睡 60s，= BaiZe `SLEEP_BUSY`） |

---

## 📊 进度快照（**每次唤醒必须更新**，供 supervisor 远程巡检）

> 固定格式写在 **`MEMORY_RESEARCH.md` 最顶部**，便于一条命令读到全局状态。

```
PHASE:        <当前阶段：arxiv_bootstrap / 常态采集>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
本轮新增:     <n> 篇（领域数：m）
阻塞:         <无 / 具体阻塞 + 需要 supervisor 做什么>
ERROR_COUNT:  <n>
```

⚠️ **`WAITING` 只写在 `MEMORY_RESEARCH.md` 的顶部单独一行**
（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
**绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行** —— 否则会误触发长睡。

**supervisor 巡检方式**：`git pull` 读 `MEMORY_RESEARCH.md` 顶部 + `research/` 下最新日报即可，**不需要登录服务器**。

---

## 0. 任务概述

**目的**：为《超级智能2035》（作者刘杨/Foam）**持续收集 & 整理** AI 领域**一手论文**，
重点 **LLM / SLM / 多模态 / agent harness**，供写作、选题、技术判断取用。**只搬运事实 + 忠实摘要，不生产观点。**

**产出**：
- `research/<YYYY-MM-DD>.md` —— 当日论文日报（积累式，同日多轮追加）；
- `research/SEEN.md` —— **去重台账**（**主键 = arXiv ID**）；
- `research/INDEX.md` —— 按日期索引 + 计数；
- `research/papers.jsonl` —— **结构化台账**（一行一篇）；
- `research/ARXIV_API.md` —— arXiv API 打通记录（R1 产物）。

---

## 0.1 什么是「可收录的论文」（入账判据 · **硬性**）

> ⚠️ 本线**只收"一手论文"**。不满足下面 4 条的一律**不算**（可另单列为"相关报道"，**不进论文台账**）。

**可收录论文 = 「arXiv 上的、与关注领域相关的、可核验的一手论文」。4 条必须同时成立：**

| # | 判据 | 说明 |
|:--|:--|:--|
| 1 | **来源** | **arXiv**（一手预印本）；**必须给 `arXiv ID` + `abs` 链接**（有 pdf 也给）。其它一手源（OpenReview / ACL Anthology）须**显式标注**。 |
| 2 | **时效** | `published`（首次提交）**≤ 72 小时**（日报口径）。**陈年经典不算**（除非 supervisor 点名）。<br>⚠️ **例外**：arXiv **周末不公告**（见运维指令 R2′）→ 落在**周末/周一早**时，可放宽到「**最近一次公告批次**」并**如实标注实际日期区间**。 |
| 3 | **可核验** | 齐备：`arXiv ID` + `标题` + `作者` + `提交/更新日期` + `主分类` + `链接`。 |
| 4 | **领域相关** | 命中 §1 关注领域。 |

**典型反例（不进论文台账）**：博客解读 / 媒体转述 / 二手综述 / 知乎推文 / 公众号文章
（若要留，放日报文末「**附录 · 相关报道**」并标 `🏷 类型：report`，**不计入论文数**）。

---

## 1. 关注领域（Watch List）

> 每轮**由上到下**逐领域检索；**没有就如实写"本领域无新增"**，不要凑数。查询清单应**固化进脚本/配置**（R2）。

| # | 领域 | arXiv 主分类 | 收什么 | 建议查询词 |
|:--|:--|:--|:--|:--|
| 1 | **LLM** | cs.CL · cs.LG | 预训练/规模律/指令微调/RLHF/推理/长上下文 | `large language model`、`scaling law`、`reasoning` |
| 2 | **SLM（小模型）** | cs.CL · cs.LG | 小模型/端侧/蒸馏/量化/高效推理 | `small language model`、`on-device`、`distillation` |
| 3 | **多模态** | cs.CV · cs.MM · cs.CL | VLM / MLLM / 图文视频理解 / 生成 | `vision-language model`、`multimodal`、`MLLM` |
| 4 | **agent harness** | cs.SE · cs.AI · cs.MA | code agent / tool use / harness / 评测基准 | `agent`、`tool use`、`SWE-bench`、`terminal-bench`、`multi-agent` |
| 5 | **邻域（可选）** | cs.AI · cs.LG | RAG / 评测 / 对齐安全（**仅当与 1–4 强相关**） | `retrieval augmented`、`benchmark`、`alignment` |

> ✅ 关注领域可被 supervisor 修改（改本表即可）。

---

## 2. 每轮采集 SOP（**每次唤醒照此执行**）

1. **读现状**：`MEMORY_RESEARCH.md` 顶部快照 + `research/SEEN.md`（已收录，避免重复）+ 当日日报（已写部分）。
2. **定窗口**：确认**上次采集时间**（见流水）→ 本轮优先覆盖**上次之后**的新提交。
3. **逐领域检索**：对 §1 每领域跑查询（`sortBy=submittedDate&sortOrder=descending`）；
   ⏱ **arXiv 礼貌限速：请求间隔 ≥ 3 秒**；**单轮查询总数受控**（建议 ≤ 12 次）。
4. **筛与去重**：与 `SEEN.md` 比对 **arXiv ID**（主键）→ 命中即跳过；只留命中 §1 且满足 §0.1 的条目。
5. **落盘**：新条目**追加**到 `research/<YYYY-MM-DD>.md`（§3 格式）+ 写入 `research/papers.jsonl` + `SEEN.md`。
6. **更新**：`research/INDEX.md` 计数；`MEMORY_RESEARCH.md` 快照 + `WAITING`；当日流水。
7. **提交**：`git add` **只加本线文件**（`MEMORY_RESEARCH.md` `research/` `daily-memories-research/`）→ `commit -m "research <date> <n> 篇"` → `push`。

> ⏱ **不要 sleep / 不要等待**：一轮做完就更新记忆并退出（loop 按 `WAITING` 决定何时唤醒下一轮）。

---

## 3. 输出格式

### `research/<YYYY-MM-DD>.md`（当日日报）

```markdown
# 论文日报 · <YYYY-MM-DD>

> 采集窗口：<上次时间> ~ <本次时间> ｜ 本轮新增：<n> 篇 ｜ 查询数：<m>

## 1. LLM
- **[标题]**（arXiv:<ID>，<提交/更新日期>）
  作者：<前 3 + et al>
  分类：<primary_category> ｜ 🏷 领域标签：<LLM/推理/长上下文…>
  一句话摘要：<中文，1~2 句，忠实原文，不抄整段>
  🔗 abs: <...> ｜ pdf: <...>
  （可选）💻 代码：<...>

## 2. SLM（小模型）
- ...（无新增则写：_本领域无新增_）
```

**字段硬要求**：`arXiv ID` + `标题` + `作者` + `日期` + `分类` + `🔗 abs` **缺一不可**。

### `research/SEEN.md`（去重台账）

```markdown
# SEEN — 已收录论文去重台账

| 首次收录 | arXiv ID | 标题 | 主分类 |
|:--|:--|:--|:--|
| 2026-10-03 | 2609.xxxxx | <标题> | cs.CL |
```

### `research/papers.jsonl`（结构化台账，一行一篇）

```json
{"arxiv_id":"2609.xxxxx","title":"...","authors":["..."],"submitted":"2026-10-02","updated":"2026-10-03","category":"cs.CL","areas":["LLM"],"summary_zh":"...","abs_url":"...","pdf_url":"...","first_seen":"2026-10-03"}
```

---

## 4. 铁律（红线，**违反即失败**）

1. 🚫 **不许编造**：**必带** `arXiv ID` + 链接 + 日期 + 作者；**无来源不收录**。搜不到就写"未找到"。
2. 🚫 **`200 ≠ 有料`**（news 线血的教训）：**必须校验 `Content-Type`（XML）+ `published` 日期真实**；
   **拿到 HTML / 404 / 空 feed 一律判失败并记录**，不得当成"无新增"。
3. 🚫 **不整篇转载**：摘要**自写**（1~2 句中文），**不得整段抄英文原文**；只给链接。
4. 🚫 **不把推测写成事实**：摘要忠实原文；判断类内容须显式标注"**我们的观察**"。
5. ⏱ **礼貌限速**：arXiv 请求间隔 **≥ 3 秒**；单轮查询数受控；**不并发打爆**。
6. 🚫 **不 `git add -A`**：只加本线文件（共享工作副本，会卷入他人在途文件）。
7. 🚫 **不在正文/快照/流水写以 `WAITING:` 开头的行**（会误触发 loop 长睡）。
8. ⚠️ **PDF 下载**：先验 `Content-Type: application/pdf` + 文件头 `%PDF`；**单轮限量**（≤10 篇），控制仓库体积。

---

## 5. 记忆维护（**硬性**）

> 理由：`MEMORY_RESEARCH.md` **每次唤醒都被 agent 全文读取** → 越大越烧 token。

- **上限**：`MEMORY_RESEARCH.md` 控制在 **≤ 32KB**；一旦超限即执行滚动。
- **滚动**：把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---

## 6. 附录 · 相关文件

- **本项目总纲**：`../README.md`；**supervisor 记忆**：`../MEMORY.md`；**agent 总表**：`../AGENTS.md`。
- **姊妹线（范式与铁律来源）**：`WATCH_NEWS_TASK.md`（news 线）+ `watch_news_loop.sh`。
- **arXiv API**：文档 https://info.arxiv.org/help/api/user-manual.html ｜ 端点 `http://export.arxiv.org/api/query`


