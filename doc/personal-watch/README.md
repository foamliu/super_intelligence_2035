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
| 当前阶段 | **三条线**：**news（新闻+回溯+分析）+ research（论文+TOP-K）** + 🆕 **recruit（Boss 招聘链路，继承 `C:\Users\liuyu\HR`）**（**2026-10-11 用户令新增第 3 条线**；原「暂不新增智能体」作废） |
| 规划中的线 | 新线一律**以用户明确指令为准**（例：原 archive 线已并入 news；recruit 线 2026-10-11 立线）。 |

---

## 3. Agent 线（**当前 3 条** · 🆕 recruit 线 2026-10-11 立线）

> **唯一权威**清单见 **`AGENTS.md`**（避免数错）。`run/` 下可能同时存在多个脚本，以 `AGENTS.md` 为准。

| 线 | 任务书 | loop 脚本 | 状态文件 | 产物 | 状态 |
|:---|:---|:---|:---|:---|:---|
| **news** | `run/WATCH_NEWS_TASK.md` | `run/watch_news_loop.sh` | `run/MEMORY_NEWS.md` | `run/news/` | ✅ 运行中（54 条真新闻；**新增 ① 十年回溯 ② 价格相关性**） |
| **research** | `run/WATCH_RESEARCH_TASK.md` | `run/watch_research_loop.sh` | `run/MEMORY_RESEARCH.md` | `run/research/` | ✅ 运行中（61 篇；**新增 TOP-K 排序**） |
| **recruit** 🆕 | `run/WATCH_RECRUIT_TASK.md` | `run/watch_recruit_loop.sh` | `run/MEMORY_RECRUIT.md` | `run/recruit/` | 🆕 立线（**继承 `C:\Users\liuyu\HR`**；**对外动作默认关闭**，须跑在持 Boss 登录态的机器） |

**news 线定位**：**三类产出，口径严格分开** ——
① **新闻日报** `run/news/`（§0.1：**≤72h 真新闻**）；
② **历史回溯** `run/news/archive/`（`type: archive`；**只取 标题+日期+来源+链接**，🚫 不抓正文）；
③ **数据分析** `run/news/analysis/`（统计 / **相关性** / 图表，**数据来源必须标注**）。
> 📌 **原 `archive` 线（历史回溯）已按用户指示并入 news 线**（不再单独成线）。
> 🧭 **三层「解耦」而非「串联」（用户 2026-10-03 定调）** —— **串联会导致成功率乘法衰减**（`p1×p2×p3 → 0`），故**三层各自独立评估**（见 `WATCH_NEWS_TASK.md` §0.0.0）：
> **L1 政治信号预警（核心 · P0）**：用**新华社文本**预测**政经举措**（什么动作 + 大致时间）→ `news/policy/`（N3）；**验收看信息质量（覆盖/准确率/提前期/基线），不看收益率**。
> **L2 与股价的关联（探索性 · P2）**：可做，但 ⚠️ **明确"非因果"** —— 🚫 禁用「影响/导致/利好」；产物用 `news/policy/EXPLORE.*`（N4）。
> **L3 算法交易：❄️ 冻结** —— **L1 扎实之前不碰**（N5）。
> ⚖️ 政治话题**只做公开数据的描述性/统计性分析**；产出为**研究性观察，非投资建议**。

**research 线定位**（**用户 2026-10-03 明确两大目的**）：
- **目的 1 · 借鉴**：找与 **BaiZe / ZhuLong** 相关的前沿研究**以资借鉴**（刘杨 = **长鑫存储 AI 研究院**）→ `TOP_K.md`/`TOP_K.jsonl`（质量 × 相关性，≤30d）+ **`TAKEAWAYS.md`**（≤5 条可借鉴结论）；相关面含**半导体/EDA/存储**视角。
- **目的 2 · 科普**：找有潜力的论文做 **《两分钟论文》** 科普视频，**发 B站/抖音 → 涨粉变现** → `research/video/SHORTLIST.md`（选题表）+ `research/video/scripts/<arXiv ID>.md`（两分钟中文口播稿）；（后续成片）。
> ⚠️ **两个目的口径不同，选题必须分开**（勿混）。
> 📧 **已登记未来职能**：给论文作者**发邮件**做学术交流 —— **未获用户批准前不得发送**。

**recruit 线定位**（🆕 **2026-10-11 用户令立线**；**继承 `C:\Users\liuyu\HR` 的记忆与能力**）：
- **目的**：把 `C:\Users\liuyu\HR` 的 **Boss 直聘招聘 agent** 收编为观察哨第 3 条线 —— **继承其记忆**（判定口径 / 达标者花名册 / 平台事实 / 铁律 / 教训 + 用户模型）与**能力**（Boss 页面操作 SOP + `screen.py`/`city_scan.py` + 话术库），并**常态化推进招聘链路**（采集 → 分级 → 复核口径 → 起草 → 收简历归档 → 交 HR）。
- **单一权威**：`C:\Users\liuyu\HR` 仍是**规范活工作区**（原始数据 + 记忆 + 能力）；本仓库只放**编排 + 本线记忆摘要 + 指针 + 非 PII 产物**（不复制 HR 的 4 个记忆文件，避免两处权威打架）。
- **⚠️ 对外动作闸门**：本线是**唯一有对外副作用**的线（给真人发消息）⇒ **默认保守**：采集/分级/复核/起草/归档/记忆 **自主**；**发消息 / 抓简历 / 代点「同意·拒绝」需运维指令区显式授权一批**；**约面控件永不碰**（面试由公司 HR 统一约）。
- **运行位置**：**持 Boss 登录态 + playwright-mcp 的机器**（当前 = 本 Windows 机，用 Git Bash/WSL）—— 与跑在远端 Linux 的 news/research 不同。
- 🚫 **PII 红线**：`boss_candidates.*`（含 `securityId`）、`简历/*.pdf`、`boss_chat*.png`、cookie **一律不入 git**。

### 3.1 启动 recruit loop（**本机 = 持 Boss 登录态 + playwright-mcp 的机器**）

> ⚠️ **与 news / research 不同**：recruit 要驱动**浏览器**（Boss 登录态在 MCP 默认 context 里）⇒ **不能**跑在远端 Linux，必须跑在**持有 Boss 登录态的机器**上（当前 = 本 Windows 机）。
> Windows 用 **Git Bash / WSL**（需 GNU `date -d`；Git Bash 无 `setsid`）。**改了 `watch_recruit_loop.sh` 后必须重启 loop 才生效。**

```bash
cd <仓库根>/doc/personal-watch/run
git pull --rebase --autostash          # 共享工作副本，先同步

# Linux / WSL：
setsid bash watch_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 < /dev/null &
# Git Bash（无 setsid）：
# nohup bash watch_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 &
```

**验证**（启动横幅第 3 行即打印 `🧬 继承源 HR_DIR=…`，不必等首轮跑完）：

```bash
pgrep -af 'watch_recruit_loop.sh'      # 应恰好 1 个进程
tail -20 /tmp/watch_recruit_loop.log   # 看 [loop] 模式横幅 + 🧬 继承源自检 + ⏰ 下次唤醒
```

**停止**：`pkill -f watch_recruit_loop.sh`

| 项 | 值 |
|:---|:---|
| **继承源 `$HR_DIR`** | `C:\Users\liuyu\HR`（可用环境变量 **`WATCH_HR_DIR`** 覆盖）—— loop 启动会自检其 `MEMORY.md / USER.md / AGENTS.md` 是否存在 |
| **唤醒节律** | 每天 2 次 **06:00 / 18:00**（`SCHEDULE_HOURS=6,18`，可用 **`WATCH_SCHEDULE_HOURS`** 覆盖；置空 ⇒ 回退 WAITING 自适应） |
| **存活标记** | `/tmp/watch_recruit_loop.hb`（零 token，每 5 分钟刷新） |
| **日志** | `/tmp/watch_recruit_loop.log` |
| **⚠️ 对外动作** | **默认关闭** —— 发消息 / 抓简历 / 代点「同意·拒绝」需运维指令区**显式授权一批**；**约面控件永不碰** |

> 完整调参见 `run/README.md §2.3`；本线的继承映射与红线见 `run/recruit/README.md` + `run/WATCH_RECRUIT_TASK.md §0`。

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
    ├── news/                      # news 产物：<date>.md + SEEN.md + INDEX.md + 免 key MCP
    │   ├── archive/               #   ② 历史回溯（xinhua-<年>.jsonl.gz + PROGRESS.md + INDEX_FILES.md）
    │   └── analysis/              #   ③ 数据分析（XINHUA_2016_2026.html + corr.csv + NEWS_vs_PRICES.html）
    ├── WATCH_RESEARCH_TASK.md     # research 任务书（agent 只读）
    ├── watch_research_loop.sh     # research 循环脚本
    ├── MEMORY_RESEARCH.md         # research 运行时状态（含 WAITING）
    ├── daily-memories-research/   # research 每日流水
    ├── research/                  # research 产物（<date>.md + SEEN.md + INDEX.md + papers.jsonl + TOP_K.* + ARXIV_API.md + video/ + pdf/）
    ├── WATCH_RECRUIT_TASK.md      # recruit 任务书（agent 只读；🆕 继承 C:\Users\liuyu\HR）
    ├── watch_recruit_loop.sh      # recruit 循环脚本（定时 6,18；须跑在持 Boss 登录态的机器）
    ├── MEMORY_RECRUIT.md          # recruit 运行时状态（含「🧬 继承摘要」指针）
    ├── daily-memories-recruit/    # recruit 每日流水
    ├── recruit/                   # recruit 产物（STATE.md + drafts/ + reports/；★ 只放非 PII，见 .gitignore）
    ├── ops_relay.sh               # ⭐ ops 中继（纯 bash、零 token 的命令通道；loop 停着也能运维）
    ├── ops/                       #   中继的 inbox.md（下发）/ outbox.md（结果）/ .last_run_id
    ├── DEPLOY_CHECKLIST.md        # 新机 bring-up · cline 配置重建 · 2 核加固 · systemd 自启
    └── LLM_ROTATE_INTEGRATION.md  # 额度/鉴权自动轮换接入方案（复用 BaiZe 的 llm_rotate.sh）
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
- [ ] **启动 recruit 线**（🆕 见 **§3.1**；**须在持 Boss 登录态的机器**）—— 首轮唤醒读 `C:\Users\liuyu\HR` 记忆 + 巡检 Boss + 产出 `run/recruit/STATE.md`。
- [ ] 确认 worker 运行主机是否可访问外网 / MCP `web-search`（搜索能力是 news 线的硬依赖）。
- [ ] 待定：产出是否需要**周报合订**（把 7 天摘要合并成一份 `run/news/WEEKLY_<yyyy-Www>.md`）。
- [ ] 待定：是否增设 **paper 线**（arXiv/顶会）与 **news 线**并行。
