# AGENTS.md — personal-watch（观察哨）自动化 agent / loop 状态总表

> **用途**：`run/` 下会有多个 `*_loop.sh` 与 `MEMORY_*.md`，本文件是**唯一权威**的"谁在跑"清单，避免数错。
>
> 最后更新：2026-10-03（建哨）

---

## 1. 活跃 agent

| Agent | loop 脚本 | 任务书 | 状态文件 | 日志目录 | 跑什么 | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| **news** 🆕 | `run/watch_news_loop.sh` | `run/WATCH_NEWS_TASK.md` | `run/MEMORY_NEWS.md` | `run/daily-memories-news/` | 按关注清单**常态化采集超级智能/前沿 AI 新闻**，产出 `run/news/<date>.md` 摘要 + `run/news/SEEN.md` 去重台账 | ⬜ 待启动 |

> 🆕 **news 线（2026-10-03 新建）**：本哨位的**第一条线**。依赖**外网搜索**（MCP `web-search` / `search_news`）。
> **不占 GPU、不登录训练机**；唯一资源是**网络请求**，注意控制频率与合规（见任务书铁律）。

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

1. **上限**：每个 `MEMORY_*.md` **≤ 32 KB**。
2. **超限即滚动**：把**较早的流水条目**（**保留最近 ~20 条**）**追加**到 `daily-memories-<线>/<条目日期>.md`，再从 MEMORY 中删除这些旧条目。**归档原文不改**，且**不参与每次唤醒读取**。
3. **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条流水。
4. **纪律**：归档**不得改变任何结论**；`WAITING:` 纪律不变。

---

## 6. 🧭 supervisor 侧记忆

- **主记忆**：**项目根** `MEMORY.md`（即 `doc/personal-watch/MEMORY.md`）—— **supervisor「醒来」先读本文件**。
- **日流水**：**项目根** `daily-memories/<YYYY-MM-DD>.md`（记录：**用户指令 → 处置 → commit → worker 回报**）。
- **与 worker 的关系**：supervisor **不属于**任何 worker 线；通过**改任务书「运维指令区」+ `git push`** 下发，通过**读 `run/MEMORY_*` / `run/daily-memories-*` / 产物** 查看成果。
- ⚠️ **位置区分**：**supervisor 记忆在项目根**；**worker 线记忆在 `run/`**——**两者不要混**。
