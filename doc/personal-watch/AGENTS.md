# AGENTS.md — personal-watch（观察哨）自动化 agent / loop 状态总表

> **用途**：`run/` 下会有多个 `*_loop.sh` 与 `MEMORY_*.md`，本文件是**唯一权威**的"谁在跑"清单，避免数错。
>
> 最后更新：2026-10-07（**唤醒节律：每 30 分钟 → 每天 2 次定时 06:00 / 18:00**）

---

## 1. 活跃 agent

| Agent | loop 脚本 | 任务书 | 状态文件 | 日志目录 | 跑什么 | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| **news** 🆕 | `run/watch_news_loop.sh` | `run/WATCH_NEWS_TASK.md` + **P0 规格 `run/NEWS_PRICE_SIGNAL_SPEC.md`** | `run/MEMORY_NEWS.md` | `run/daily-memories-news/` | ⭐ **P0（2026-10-07 起）：新闻信号 → 资产价格** —— 十年多资产价格数据（≥20 标的 / 6 类 / 2016–2026）+ **滞后相关/预测力研究（先预注册）** → `run/news/signal/`（`PREREG.md` `lag_corr.csv` `LAG_CORR.md` `FINDINGS.md`）+ **每日两报**（**06:00 生成早报 / 18:00 优化晚报**）。<br>（P2 顺手，不追量）按关注清单常态化采集 AI 新闻 → `run/news/<date>.md` + `SEEN.md` | 🔄 运行中（P0 第 11 批刚派 R1）· ⏰ **定时唤醒：每天 2 次 06:00 / 18:00** |
| **research** 🆕 | `run/watch_research_loop.sh` | `run/WATCH_RESEARCH_TASK.md` | `run/MEMORY_RESEARCH.md` | `run/daily-memories-research/` | **① 借鉴**：与 BaiZe/ZhuLong 相关的前沿研究 → `TOP_K.*` + `TAKEAWAYS.md`；**② 科普**：《两分钟论文》视频 → `video/SHORTLIST.md` + `video/scripts/*.md`（+ 后续成片） | ✅ 运行中（61 篇；TOP-K/视频线刚派）· ⏰ **定时唤醒：每天 2 次 06:00 / 18:00** |

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
| **每轮唤醒必须提交+推送**（2026-10-06 用户令） | **每次唤醒收尾自己 `commit+push`**（写心跳 → 写日报 → 提交推送 → `git status -sb` 自检）；🚫 **不许依赖 loop 兜底**（兜底只是保险丝）。**判死判据**：⚠️ **2026-10-07 起本两线改为「每天 2 次定时唤醒」⇒ 旧的「心跳 >60min 无提交 = 卡死」不再适用**；改判 **loop 存活标记 `/tmp/watch_<线>_loop.hb`（每 5 分钟刷新）+ 日志尾部 `⏰ 定时模式：下次唤醒 = …`** |
| ⏰ **定时唤醒**（2026-10-07 用户令） | **每 30 分钟 → 每天 2 次：06:00 / 18:00**（`SCHEDULE_HOURS=6,18`，本地时区）。时窗内**纯 bash 分段睡**（`SLEEP_CHUNK=300s`，**零 token**）；时窗内致命错**最多重试 1 次**（`SCHEDULE_RETRY_MAX`），之后等下个时窗。⚠️ **一次唤醒 ≈ 半天工作量 ⇒ 当轮做满、别留碎活**（下一轮 12h 后）。回退旧节律：环境变量 `WATCH_SCHEDULE_HOURS=` 置空。✅ **启后秒级自检**：日志头两行应打印 `⏰ 定时模式已启用：唤醒时窗 = 6,18` + `⏰ 时窗参考：此刻之后的下一个时窗 = …`（**这条是给中继/巡检核验用的**，不必等 25min 首轮跑完）。⚠️ **重启 loop 会立刻多跑一轮**（首轮唤醒不等时窗 ⇒ 多烧一轮 cline）⇒ **别做无谓重启** |
| **自适应睡眠**（**仅旧模式 / 回退时生效**） | `WAITING:0` → 短睡（近期待办）；`WAITING:1` → 长睡（常态省 token） |
| 🔴 **启动必须带 PATH（2026-10-06 血泪）** | **只用「登录 shell」起 loop**：`setsid bash -lc "exec bash <run>/watch_news_loop.sh" …`。**否则非登录 shell 的 PATH 里没有 `cline`** ⇒ loop 会**每轮 `env: 'cline': No such file` 静默空转**（进程/git 全正常，极难察觉）。✅ 启后自检：`command -v cline` 有输出 + 日志见 `invoking cline` 且无 `No such file` |
| 🔌 **中继（ops 通道）健康**（2026-10-07 血泪） | 中继可能**活着但冻死**：`pgrep` 有、`kill -0` 通过，**却 14h 不干活**（本次实际发生：命令块里 `setsid … &` 的守护持有命令替换管道写端 ⇒ 父 bash 卡 `pipe_read` 永久等 EOF）⇒ **不许只靠 `pgrep` 判活**。判据 = 日志 ≤10min 一行 `💓` 心跳 + `/proc/<pid>/wchan` **≠ `pipe_read`**。冻死处置 / 保底通道见 `run/ops/README.md` §4.5。**supervisor 现有 SSH 直连**（用户 2026-10-07 授权，凭据不落库）⇒ 中继只是「便利」，不是唯一通道 |
| **任务书即 prompt** | loop 用 `prompt="$(< TASK_MD)"` → 任务书要**精简**，历史归档不进 prompt |

> `run/watch_news_loop.sh` **已从设计上避开**上述三处历史坑，可作为**新线的模板**。

---

## 4. 共享资源

- **共享工作副本**：同一个 git 仓库工作区。
  - **只需一个 agent `git pull`，其余立刻看到**——不要重复 pull。
  - 工作区里陌生的未提交改动**可能是别的线/兄弟项目（如 `BaiZe-ISEDA2027`）的在途文件** → 🚫 不要 clean / stash / reset。
  - ⚠️ **`pull --rebase --autostash` 之后必查 `git stash list`**（2026-10-07 血泪）：共享工作区里可能**躺着历史 autostash**（本次发现 1 条 10-06 冲突事故的残留，含 research 线 `research/raw/2026-10-06-fetch-r56.json` 的 **60 行旧快照**，而 HEAD 里该文件已是 **3227 行**）。自动回放失败时它会**静默留在 stash 里**，无人发现 —— 直到某天被误 `pop` 成脏树。
    - 🚫 **禁止**用 `git stash pop` 或 `git checkout stash@{N} -- <path>` 去"恢复"它：前者**一冲突就把共享工作区弄脏 ⇒ 阻塞所有线的 pull**（10-06 停摆 5h 即此类）；后者**连 index 一起写**（status 会变成 `M `(已暂存)，你会误以为"只是工作区变了"）。
    - ✅ 规矩：① 先用 `git diff 'stash@{N}' HEAD -- <path>` 判断是否**陈旧残留**（**base 是空 blob / 旧内容 = 陈旧**，别拿它覆盖前进后的 HEAD）；② 真需要回正用 **`git checkout HEAD -- <path>`**（**index + 工作区一起刷**）；③ 陈旧残留 → 记下 `git stash drop` 打出的 dangling SHA 再丢弃。
    - ✅ **同步后自检三连**：`git status --porcelain`（干净）/ `git stash list`（空）/ `git rev-list --left-right --count origin/main...HEAD`（`0 0`）。
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
