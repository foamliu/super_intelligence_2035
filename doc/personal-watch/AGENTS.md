# AGENTS.md — personal-watch（观察哨）自动化 agent / loop 状态总表

> **用途**：`run/` 下会有多个 `*_loop.sh` 与 `MEMORY_*.md`，本文件是**唯一权威**的"谁在跑"清单，避免数错。
>
> 最后更新：2026-10-03（建哨）

---

## 1. 活跃 agent

| Agent | loop 脚本 | 任务书 | 状态文件 | 日志目录 | 跑什么 | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| **news** 🆕 | `run/watch_news_loop.sh` | `run/WATCH_NEWS_TASK.md` | `run/MEMORY_NEWS.md` | `run/daily-memories-news/` | 按关注清单**常态化采集超级智能/前沿 AI 新闻**，产出 `run/news/<date>.md` 摘要 + `run/news/SEEN.md` 去重台账 | 🔄 运行中（纠偏中：中文权威源 / 新闻定义） |
| **research** 🆕 | `run/watch_research_loop.sh` | `run/WATCH_RESEARCH_TASK.md` | `run/MEMORY_RESEARCH.md` | `run/daily-memories-research/` | **① 借鉴**：与 BaiZe/ZhuLong 相关的前沿研究 → `TOP_K.*` + `TAKEAWAYS.md`；**② 科普**：《两分钟论文》视频 → `video/SHORTLIST.md` + `video/scripts/*.md`（+ 后续成片） | ✅ 运行中（61 篇；TOP-K/视频线刚派） |

> 🚫 **用户已定（2026-10-03）：暂不新增智能体。** 新职能**一律并入既有线**。
> 例：原 **archive（历史回溯）线已并入 news**（职能 = `news/archive/` + `news/analysis/`），脚手架已删除。
>
> 🔌 **运维通道（2026-10-05 新增）**：**ops 中继 `run/ops_relay.sh`**（纯 bash、零 token）——
> supervisor 写 `run/ops/inbox.md` → 中继执行 → 结果进 `run/ops/outbox.md`。
> ⭐ **loop 停/撞额度/OOM 时的唯一远程运维手段**（见 `run/ops/README.md`）。
> ⚠️ **启动必须** `setsid bash -c 'exec -a watch_ops_relay.sh bash ops_relay.sh' …`（否则 cmdline 只有 `bash ops_relay.sh`）；
> 停止只可用 `pkill -f watch_ops_relay.sh` 或 `kill "$(cat /tmp/watch_ops_relay.pid)"`（**别** `pkill -f ops_relay.sh`，会误杀 BaiZe 的中继）。
> 🛡 已加**单实例锁** `/tmp/watch_ops_relay.pid`（防双实例重复执行）；已修「只跑最大 RUN_ID → 静默跳过中间块」→ 现**按升序执行所有 pending 块**。
>
> 🎯 **两条线的长期目的**：**news → 三层「解耦」**：**L1 政治信号预警（核心）** / **L2 与股价的关联（探索性·非因果）** / **L3 算法交易（❄️ 冻结）**（见 `WATCH_NEWS_TASK.md` §0.0.0–§0.0.2）；
> **research → ① 借鉴 BaiZe/ZhuLong ② 《两分钟论文》科普视频**（见 `WATCH_RESEARCH_TASK.md` §0）。

> 🆕 **news 线（2026-10-03 新建）**：本哨位的**第一条线**。依赖**外网搜索**（MCP `web-search` / `search_news`）。
> **不占 GPU、不登录训练机**；唯一资源是**网络请求**，注意控制频率与合规（见任务书铁律）。
>
> 🆕 **research 线（2026-10-03 新建）**：依赖 **arXiv API**（`export.arxiv.org/api/query`）。**不占 GPU**；
> ⚠️ **礼貌限速**（arXiv 要求请求间隔 **≥3s**）；**继承 news 线全部铁律**，尤其 **"`200 ≠ 有料`"（验 `Content-Type` + `published`）**。
> 姊妹关系：**news 管"发生了什么"，research 管"研究界出了什么"**；两条线共用工作副本，**注意 loop 的 `git add` 只加本线文件**。

---

## 2. 已收敛 / 已停（**当前无**）

| 轮次 | loop 脚本 | 任务书 | 状态文件 | 终态 |
|:---|:---|:---|:---|:---|
| — | — | — | — | — |

> ⚠️ 各 loop 都是 `while true`；线收敛后若没 kill 干净会**一直空转烧 token**。
> 到机器上先确认：`pgrep -af 'watch_.*_loop.sh'`。

---

## 3. 脚本级约定（重启/新线时沿用）

| 约定 | 说明 |
|:---|:---|
| **push 前先同步** | `git fetch` → 必要时 `git pull --rebase --autostash origin main`（**只 push 不 pull** 会在远端前进后**永久卡死**） |
| **WAITING 正则** | 只认**行首** `^WAITING:[[:space:]]*1`（宽正则 `WAITING:[* ]*1` 会误匹配正文散文） |
| **兜底提交范围** | 只 `git add` **本线自己的文件**（🚫 不要 `git add -A`，会卷入其他线在途文件） |
| **每轮唤醒必须提交+推送**（2026-10-06 用户令） | **每次唤醒收尾自己 `commit+push`**（写心跳 → 写日报 → 提交推送 → `git status -sb` 自检）；🚫 **不许依赖 loop 兜底**（兜底只是保险丝）。判死判据：**心跳文件 >60min 无新提交 = 卡死** |
| **自适应睡眠** | `WAITING:0` → 短睡（近期待办）；`WAITING:1` → 长睡（常态省 token） |
| **任务书即 prompt** | loop 用 `prompt="$(< TASK_MD)"` → 任务书要**精简**，历史归档不进 prompt |

> `run/watch_news_loop.sh` **已从设计上避开**上述三处历史坑，可作为**新线的模板**。

---

## 4. 共享资源

- **共享工作副本**：同一个 git 仓库工作区。
  - **只需一个 agent `git pull`，其余立刻看到**——不要重复 pull。
  - 工作区里陌生的未提交改动**可能是别的线/兄弟项目（如 `BaiZe-ISEDA2027`）的在途文件** → 🚫 不要 clean / stash / reset。
- **网络**：news 线是**唯一重度使用外网**的线 → 控制单轮请求量、避免对同一站点高频抓取。

---

## 5. 📉 记忆体量维护

> **为什么**：loop 脚本对 `MEMORY_*.md` 只做 `grep '^WAITING:'`（近零成本），但 **cline agent 每次唤醒会把整个 `MEMORY_*.md` 读进上下文** → 文件越大，**每次唤醒烧的 token 越多**，且**无上限增长**。

**规程**：

1. **上限**：每个 `MEMORY_*.md` **≤ 32 KB**；**任务书 `WATCH_*_TASK.md` 同样 ≤ 32 KB（红线 40 KB）**。
   ⭐ **2026-10-06 用户裁定**：任务书的**归档也由各线 agent 自己滚动**（与 `MEMORY_*.md` 同机制），**不再依赖 supervisor** —— 只做「已闭合块原文搬迁 + 1 行指针」，不新增/不改写指令（见各任务书「5. 记忆维护」）。
2. **超限即滚动**：把**较早的流水条目**（**保留最近 ~20 条**）**追加**到 `daily-memories-<线>/<条目日期>.md`，再从 MEMORY 中删除这些旧条目。**归档原文不改**，且**不参与每次唤醒读取**。
3. **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条流水。
4. **纪律**：归档**不得改变任何结论**；`WAITING:` 纪律不变。

---

## 6. 🧭 supervisor 侧记忆

- **主记忆**：**项目根** `MEMORY.md`（即 `doc/personal-watch/MEMORY.md`）—— **supervisor「醒来」先读本文件**。
- **日流水**：**项目根** `daily-memories/<YYYY-MM-DD>.md`（记录：**用户指令 → 处置 → commit → worker 回报**）。
- **与 worker 的关系**：supervisor **不属于**任何 worker 线；通过**改任务书「运维指令区」+ `git push`** 下发，通过**读 `run/MEMORY_*` / `run/daily-memories-*` / 产物** 查看成果。
- ⚠️ **位置区分**：**supervisor 记忆在项目根**；**worker 线记忆在 `run/`**——**两者不要混**。
