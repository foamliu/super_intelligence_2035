# personal-watch（观察哨）— 项目总纲 / Project README

> 本目录是**观察哨**：一个由 **supervisor（观察哨长）** 统筹、若干 **worker agent** 分头执行的**信息技术观察/采集**项目。
> 目标：为《超级智能2035》（作者刘杨/Foam）**持续、可溯源**地采集与"超级智能时代"相关的一手信号（新闻 / 论文 / 政策 / 产品）。
>
> 组织方式**仿照 `doc/BaiZe-ISEDA2027/`**：
> - **supervisor** 的记忆 = **本目录根** 的 `MEMORY.md` + `daily-memories/`（**醒来先读 MEMORY.md**）；
> - **worker agent** 的任务书 + 循环脚本 + 记忆 = `run/` 下（详见 §3）。
>
> ⚠️ 带 **[TBD]** / **⚠️** 的条目是**尚未确认**的，不要当成结论引用。

---

## 0. 一句话定位

> **BaiZe 在"训练模型"；观察哨在"训练注意力"——把外部世界喂给作者的一手信号，整理成可溯源、可复用的素材。**

- **不生产观点，只搬运事实**：每条结论必带 **来源 + 日期 + 链接**。
- **不做一次性搜索**：做成**常态化的哨位（loop）**，按节律持续采集、去重、归档。
- **与《超级智能2035》的关系**：优先采集与该书**核心命题**相关的信号（见 `run/WATCH_NEWS_TASK.md` §1 关注清单），供作者写作/修订时取用。

---

## 1. 角色与职责

| 角色 | 是谁 | 干什么 | 记忆位置 |
|:---|:---|:---|:---|
| **supervisor（观察哨长）** | 用户对话侧的那个"我"（Cline 会话） | **不亲自采集**：派活（改 `run/*_TASK.md` 运维指令区）、巡检（读 `run/MEMORY_*.md` 顶部快照）、汇总（写本目录 `MEMORY.md`） | 本目录根 `MEMORY.md` / `daily-memories/` |
| **worker agent（哨兵）** | `run/` 下各 `*_loop.sh` 拉起的 cline 循环 | 按各自任务书连续推进，产物写 `run/<线>/`，状态写 `run/MEMORY_<线>.md` | `run/MEMORY_<线>.md` / `run/daily-memories-<线>/` |

> supervisor **不登录任何服务器**；**下发通道 = 改任务书 + git push**，**查看通道 = git pull 读 worker 的 MEMORY/产物**。

---

## 2. 当前时间线（**2026-10-03 建哨**）

| 项 | 值 |
|:---|:---|
| 建哨日 | **2026-10-03** |
| 当前阶段 | **起步**：**news（新闻）+ research（论文）+ archive（历史回溯）** 三条线 |
| 规划中的线 | news：纠偏已闭环；research：已交付首轮；archive：**刚建线**（先做端点勘察 + 年条数估计） |

---

## 3. Agent 线（**当前 3 条**）

> **唯一权威**清单见 **`AGENTS.md`**（避免数错）。`run/` 下可能同时存在多个脚本，以 `AGENTS.md` 为准。

| 线 | 任务书 | loop 脚本 | 状态文件 | 产物 | 状态 |
|:---|:---|:---|:---|:---|:---|
| **news** | `run/WATCH_NEWS_TASK.md` | `run/watch_news_loop.sh` | `run/MEMORY_NEWS.md` | `run/news/` | 🔄 运行中（35 条真新闻） |
| **research** | `run/WATCH_RESEARCH_TASK.md` | `run/watch_research_loop.sh` | `run/MEMORY_RESEARCH.md` | `run/research/` | ✅ 运行中（首轮 34 篇） |
| **archive** 🆕 | `run/WATCH_ARCHIVE_TASK.md` | `run/watch_archive_loop.sh` | `run/MEMORY_ARCHIVE.md` | `run/archive/` | ⬜ 待启动（历史回溯） |

**news 线定位**：按关注清单（`WATCH_NEWS_TASK.md` §1）**常态化采集**超级智能/前沿 AI 相关的**新闻**，每轮产出一份**当日摘要** `run/news/<YYYY-MM-DD>.md`，并维护去重台账 `run/news/SEEN.md`。

**research 线定位**：**打通 arXiv API** 并**常态化采集 & 整理 AI 论文**，重点 **LLM / SLM / 多模态 / agent harness**。产出 `run/research/<YYYY-MM-DD>.md` 日报 + `SEEN.md`（**主键 arXiv ID**）+ `INDEX.md` + `papers.jsonl`（结构化台账）。**范式与铁律继承 news 线**。

**archive 线定位**：**历史回溯**（**不是日更**）—— 对**国内权威源**（新华网/人民网/中新网/央视网，**全程免 key**）在**指定时间窗**（当前 **2016–2026**）内做**端点勘察 → 抽样计数 → 按需抓取**。产物标 `🏷 类型：archive`，🚫 **不混入 news 的「日更 ≤72h」口径**；⏱ 同站限速 **≥2s**；**全量抓取须 supervisor 批准**。

---

## 4. 目录结构

```
doc/personal-watch/
├── README.md                      # 本文件（项目总纲）
├── MEMORY.md                      # ⭐ supervisor 长期记忆 —— 醒来先读
├── AGENTS.md                      # agent 状态总表（"谁在跑"的唯一权威）
├── report_10_03.html              # 对外工作汇报（自包含 HTML，对齐 BaiZe 报告范式）
├── daily-memories/                # supervisor 侧每日流水
└── run/                           # worker agent 编排 + 产物
    ├── README.md                  # run/ 使用说明（启动/巡检/调参）
    ├── WATCH_NEWS_TASK.md         # news 任务书（agent 只读）
    ├── watch_news_loop.sh         # news 循环脚本
    ├── MEMORY_NEWS.md             # news 运行时状态（含 WAITING）
    ├── daily-memories-news/       # news 每日流水
    ├── news/                      # news 产物（<date>.md + SEEN.md + INDEX.md + 免 key MCP）
    ├── WATCH_RESEARCH_TASK.md     # research 任务书（agent 只读）
    ├── watch_research_loop.sh     # research 循环脚本
    ├── MEMORY_RESEARCH.md         # research 运行时状态（含 WAITING）
    ├── daily-memories-research/   # research 每日流水
    ├── research/                  # research 产物（<date>.md + SEEN.md + INDEX.md + papers.jsonl + ARXIV_API.md + pdf/）
    ├── WATCH_ARCHIVE_TASK.md      # archive 任务书（历史回溯，agent 只读）
    ├── watch_archive_loop.sh      # archive 循环脚本
    ├── MEMORY_ARCHIVE.md          # archive 运行时状态（含 WAITING）
    ├── daily-memories-archive/    # archive 每日流水
    └── archive/                   # archive 产物（ENDPOINTS.md + COUNT_STUDY.md + <主题>-<窗口>.md）
```

---

## 5. 工作方式（supervisor SOP）

> 完整版见 `MEMORY.md` §1。

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`。
2. **读 `MEMORY.md`**：尤其 §3 在途任务 / §4 待拍板 / §5 铁律。
3. **读 worker 状态**：`run/MEMORY_NEWS.md` 顶部「进度快照」+ `run/news/` 最新产物 + `git log --oneline -20`。
4. **处理回写**：worker 有产物/提问 → 读、核、必要时答复（写进对应任务书的「运维指令区」）。
5. **下发新任务**：在 `run/WATCH_NEWS_TASK.md` 的「运维指令区」加 **带日期的 block**（**越靠前越优先**，老块不改）。
6. **提交**：`git add` **只加自己动的文件** → `commit` → `push`（🚫 **不要 `git add -A`**）。
7. **回写** `MEMORY.md` + 当日 `daily-memories/<date>.md`。

---

## 6. 通讯协议 / 接口

- **接口 = 任务书的「运维指令区」（OPERATOR NOTES）**：supervisor 通过改这段下发；worker **禁止修改**该段。
- **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；写清 **优先级 / 顺序 / 判据 / 铁律**；**新块放最前**。
- **worker 回写位置**：`run/MEMORY_NEWS.md`（状态头 + 进度快照 + 运维问答 + 流水）、`run/daily-memories-news/`、`run/news/`。
- **`WAITING` 纪律**：只在 `run/MEMORY_NEWS.md` **顶部单独一行**出现；正则 `^WAITING:[[:space:]]*1` 驱动 loop 睡眠时长。**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 7. 铁律（红线）

1. 🚫 **不许编造**：新闻条目**必带可点开的链接 + 发布日期 + 来源名**；无来源不收录。
2. 🚫 **不许把推测写成事实**：摘要里区分「原文说了什么」与「我们的判断（若写，需显式标注）」。
3. 🚫 **不采集付费墙内/需登录才能读的正文**：只引用公开可见的标题/摘要 + 链接。
4. ✅ **可溯源**：每条结论都能追到具体 URL；引用即贴链接。
5. ✅ **省 token**：任务书全文 = 每次唤醒的 prompt，**保持精简**；历史轮次归档到 `run/daily-memories-news/`，不进 prompt。
6. ⚠️ **礼仪/合规**：控制请求频率，避免对同一站点高频抓取；尊重 robots 与版权（只做摘要 + 链接，不整篇转载）。

---

## 8. 待办 / 已知问题

- [ ] **启动 news 线**（见 `run/README.md` 的启动命令）。
- [ ] 确认 worker 运行主机是否可访问外网 / MCP `web-search`（搜索能力是 news 线的硬依赖）。
- [ ] 待定：产出是否需要**周报合订**（把 7 天摘要合并成一份 `run/news/WEEKLY_<yyyy-Www>.md`）。
- [ ] 待定：是否增设 **paper 线**（arXiv/顶会）与 **news 线**并行。
