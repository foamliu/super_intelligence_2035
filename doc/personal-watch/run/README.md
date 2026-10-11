# run/ — personal-watch worker agent 编排目录

> 本目录存放**观察哨**各 worker 线的**任务书 + 循环脚本 + 运行时记忆 + 产物**。
> 范式照抄 `doc/BaiZe-ISEDA2027/run/`。

---

## 1. 文件命名约定（每条线一组）

| 文件 | 作用 | 谁可写 |
|:---|:---|:---|
| `<线>_TASK.md`（如 `WATCH_NEWS_TASK.md`） | **只读任务书**。**全文 = 每次唤醒的 prompt** → 保持精简；含「运维指令区」。 | supervisor 写；agent **只读** |
| `<线>_loop.sh`（如 `watch_news_loop.sh`） | 自适应唤醒循环（`prompt="$(< TASK_MD)"` → `cline` → git 兜底同步）。 | supervisor 写 |
| `MEMORY_<线>.md`（如 `MEMORY_NEWS.md`） | 运行时状态（顶部 `WAITING:` + 进度快照 + 运维问答 + 流水）。 | agent 写 |
| `daily-memories-<线>/<date>.md` | 该线每日流水（归档，不进 prompt）。 | agent 写 |
| `<线>/`（如 `news/`） | 该线产物目录。 | agent 写 |

---

## 2. 启动 news 线（**在可出外网的机器上**）

```bash
cd <仓库根>/doc/personal-watch/run
# 先同步（共享工作副本，别人可能已推进）
git pull --rebase --autostash

# 启动（脱离进程组，防工具超时误杀；日志重定向到 /tmp）
setsid bash watch_news_loop.sh > /tmp/watch_news_loop.log 2>&1 < /dev/null &
```

**验证**：

```bash
pgrep -af 'watch_news_loop.sh'          # 应恰好 1 个进程
tail -f /tmp/watch_news_loop.log        # 看 [loop] 唤醒日志
```

**停止**：

```bash
pkill -f 'watch_news_loop.sh'
```

> ⚠️ **前提**：运行机器需**能访问外网**且 cline 已挂 **`web-search` MCP**（bocha）或可用通用搜索工具
> （`web_search` / `search_news` / `fetch_page`）。否则 news 线**拿不到条目**，会空转。

---

## 2.1 启动 research 线（**在可出外网的机器上**）

```bash
cd <仓库根>/doc/personal-watch/run
git pull --rebase --autostash
setsid bash watch_research_loop.sh > /tmp/watch_research_loop.log 2>&1 < /dev/null &
```

**验证 / 停止**（把 `news` 换成 `research`）：

```bash
pgrep -af 'watch_research_loop.sh'          # 应恰好 1 个进程
tail -f /tmp/watch_research_loop.log
pkill -f 'watch_research_loop.sh'
```

> ⚠️ **前提**：运行机器需能访问 **`export.arxiv.org`**（arXiv API）。
> 首轮执行 **R1（打通 arXiv API）**：**必须给实测证据**（真查询 + 条目 + `published` 日期 + `Content-Type`），
> 且遵守 **arXiv 礼貌限速（请求间隔 ≥ 3 秒）**。
>
> ℹ️ **两条线可同时跑**：它们各自有独立 loop / MEMORY / 产物目录；共享工作副本——
> 两个 loop 都**只 `git add` 本线文件**，互不干扰。

---

> ℹ️ **两条线可同时跑**（news / research）：各有独立 loop / MEMORY / 产物；**都只 `git add` 本线文件**。
> 📌 **原 archive 线已并入 news**（不单独启动）—— 其任务见 `WATCH_NEWS_TASK.md` **第 7 批（N1 十年回溯 / N2 价格相关性）**，
> 产物落在 `news/archive/`（索引）与 `news/analysis/`（图表/相关性）。

---

## 2.3 启动 recruit 线（**在持 Boss 登录态的那台机器上** · 🆕 2026-10-11 立线）

> ⚠️ recruit 线要驱动 **浏览器（Boss 登录态 + playwright-mcp）** ⇒ **与 news/research 不同**，它**必须跑在持有 Boss 登录态的机器**上（当前 = 本 Windows 机）。
> Windows 请用 **Git Bash / WSL**（需 GNU `date -d`）；`setsid` 在 Git Bash 可能没有 ⇒ 用 `nohup ... &`。

```bash
cd <仓库根>/doc/personal-watch/run
git pull --rebase --autostash

# Linux/WSL:
setsid bash watch_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 < /dev/null &
# Git Bash（无 setsid）:
# nohup bash watch_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 &
```

**验证**（启动横幅第 3 行会打印 `🧬 继承源 HR_DIR=…`）：

```bash
pgrep -af 'watch_recruit_loop.sh'          # 应恰好 1 个进程
tail -20 /tmp/watch_recruit_loop.log       # 看 [loop] 模式横幅 + 🧬 继承源自检
```

**停止**：`pkill -f watch_recruit_loop.sh`

> 🧬 **继承源**：`$HR_DIR` = `C:\Users\liuyu\HR`（可用环境变量 `WATCH_HR_DIR` 覆盖）——
> agent 唤醒先读该目录的 `MEMORY.md` / `USER.md` / `AGENTS.md` / `memory/`（记忆 + 能力），
> 细见任务书 `WATCH_RECRUIT_TASK.md` §0。**原始数据/PII 留在 `$HR_DIR`，不进本仓库**。
> ⚠️ **对外动作默认关闭**：采集/分级/复核/起草/归档自主；**发消息 / 抓简历 / 代点「同意·拒绝」需运维指令区显式授权一批**；**约面控件永不碰**。

---

## 2.2 启动 **ops 中继**（⭐ 强烈建议：loop 停了也能远程运维）

> **为什么**：worker loop 一旦**停了 / 撞额度 / OOM**，`git log` 上"什么都看不到"。
> 中继是**纯 bash、零 token、不依赖 cline**，**loop 停着也能执行诊断与运维命令**。

```bash
cd <仓库根>/doc/personal-watch/run
git pull --rebase --autostash
setsid bash ops_relay.sh > /tmp/watch_ops_relay.log 2>&1 < /dev/null &
pgrep -af 'watch_ops_relay.sh'      # 应恰好 1 个
tail -5 /tmp/watch_ops_relay.log    # [relay] started ...
```

**用法**：supervisor 在 `run/ops/inbox.md` 新增 `## RUN_ID N` + 一个 ```bash 块 → push；
中继执行后把结果 append 到 `run/ops/outbox.md` → push；supervisor `pull` 即读到。
（**已内置 RUN_ID 1 = 诊断块**：进程 / 日志 / **OOM** / 资源 / cline base / git 状态。）

**停止**：`pkill -f watch_ops_relay.sh`
> ⚠️ **不要** `pkill -f ops_relay.sh` —— 会**顺带杀掉 BaiZe 的中继**（本机另一条运维信道）。
> 🚫 **绝不要把中继当"可随意杀"的进程** —— 它是唯一的远程通道。
> 🩺 **判活（2026-10-07 起）**：日志**每 ~10min 一行 `💓` 心跳**（含 `last_run_id`/`tick`），启动行带 `HEAD=<sha>`（脚本版本）。
> ⛔ **不能只靠 `pgrep` 判活**：中继可能**活着但冻死**（`kill -0` 也通过，却 14h 不干活）—— 判据是 **日志 mtime + `/proc/<pid>/wchan`（不该是 `pipe_read`）**；处置见 `ops/README.md` §4.5。
> ✅ **保底通道**：supervisor 现**有 SSH 直连**（用户 2026-10-07 授权）⇒ 中继冻死/不可用时**不必再等它**，直接上机（本次「loop 换档 + 中继解冻」即如此完成）。

详见 `ops/README.md`（含**我们相对 BaiZe 版的修复**：多段 RUN_ID 共存、新增 `git clean -fdx` / `git reset --hard` / 杀中继 的拦截）。

---

## 2.5 常用调参（都在 `watch_news_loop.sh` 顶部）

| 变量 | 默认 | 作用 / 备注 |
|:--|:--|:--|
| `MODEL` | `deepseek-flash` | 规范 ID（本机 DeepSeek 官方 API 仅 `deepseek-flash` / `deepseek-v4-pro`） |
| `THINKING` | `low` | **推理强度**：`none\|low\|medium\|high\|xhigh`。`deepseek-flash` provider 默认 `high`（想得久/费 token）→ 已降到 `low`；要更省设 `none` |
| `SLEEP_SHORT` | `60` | **仅旧模式**：`WAITING=0`/失败重试（= BaiZe `SLEEP_BUSY`） |
| `SLEEP_LONG` | `1800` | **仅旧模式**：`WAITING=1`（= BaiZe `SLEEP_WAIT`） |
| ⏰ `SCHEDULE_HOURS` | `6,18` | **定时唤醒时窗**（本地时区）= **每天 2 次：06:00 / 18:00**（2026-10-07 用户令，防烧自己 token）。可用环境变量 `WATCH_SCHEDULE_HOURS` 覆盖；**置空 ⇒ 回退 WAITING 自适应** |
| `SLEEP_CHUNK` | `300` | 时窗内分段睡：每 5 分钟刷新存活标记（**不调 cline = 零 token**） |
| `SLEEP_RETRY` / `SCHEDULE_RETRY_MAX` | `300` / `1` | 时窗内致命错的重试等待 / **同窗最多重试次数**（🚫 防 60s 死循环烧 token） |
| `LOOP_HB` | `/tmp/watch_<线>_loop.hb` | **零 token 存活标记**（判活用；本两线**不再**用「>60min 无提交」判死） |
| — | — | 启动后**日志头两行**即打印 `⏰ 定时模式已启用：唤醒时窗 = 6,18` + `⏰ 时窗参考：此刻之后的下一个时窗 = …` ⇒ **秒级核验运行中的模式**（不必等首轮 cline 跑完） |
| `CLINE_TIMEOUT` | `1500` | 单次 cline 上限（= BaiZe） |
| `PUSH_INTERVAL` | `1800` | git 兜底同步间隔（2026-10-06 由 `18000`/5h → 30min；**现仅在每次唤醒后触发**，即 ~2 次/天） |

> ⚠️ **改 `watch_news_loop.sh` 后必须重启 loop 才生效**（bash 不会重读已在运行的脚本）。

---

## 3. 新建更多线的模板

照抄 news 一组文件，替换 `<线>` 名即可（loop 脚本**已内置**三处防坑）：

1. **push 前先 `fetch + pull --rebase --autostash`**（只 push 不 pull 会永久卡死）；
2. **`WAITING` 正则收紧为行首** `^WAITING:[[:space:]]*1`（宽正则会误匹配正文散文）；
3. **兜底提交只 `git add` 本线文件**（🚫 `git add -A` 会卷入他人在途文件）。

并在 `../AGENTS.md` §1 登记该线，在 `../README.md` §3 补一行。

---

## 4. 巡检（supervisor / 用户）

```bash
git pull --rebase --autostash
sed -n '1,40p' MEMORY_NEWS.md     # 读 news 线顶部进度快照
ls -1 news/                       # 看已产出摘要
git log --oneline -20 -- .
```

> supervisor **不需要登录服务器**：`git pull` 即可读到 worker 的状态与产物。
