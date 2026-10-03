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

## 2.2 启动 archive 线（**历史回溯**）

```bash
cd <仓库根>/doc/personal-watch/run
git pull --rebase --autostash
setsid bash watch_archive_loop.sh > /tmp/watch_archive_loop.log 2>&1 < /dev/null &
```

**验证 / 停止**（把 `news` 换成 `archive`）：`pgrep -af 'watch_archive_loop.sh'` · `tail -f /tmp/watch_archive_loop.log` · `pkill -f 'watch_archive_loop.sh'`

> ⚠️ **前提**：运行机需能访问**新华网 / 人民网 / 中新网 / 央视网**（国内源，通常无碍）。
> 首轮做 **A1 端点勘察**（新华网优先）+ **A2 抽样计数**（2016–2026 每年条数）。
> ⏱ **同站限速 ≥2s**；🚫 **A3 全量抓取须 supervisor 批准**（先算代价）。
>
> ℹ️ **三条线可同时跑**：各自独立 loop / MEMORY / 产物；**都只 `git add` 本线文件**。

---

## 2.5 常用调参（都在 `watch_news_loop.sh` 顶部）

| 变量 | 默认 | 作用 / 备注 |
|:--|:--|:--|
| `MODEL` | `deepseek-flash` | 规范 ID（本机 DeepSeek 官方 API 仅 `deepseek-flash` / `deepseek-v4-pro`） |
| `THINKING` | `low` | **推理强度**：`none\|low\|medium\|high\|xhigh`。`deepseek-flash` provider 默认 `high`（想得久/费 token）→ 已降到 `low`；要更省设 `none` |
| `SLEEP_SHORT` | `60` | `WAITING=0`/失败重试（= BaiZe `SLEEP_BUSY`） |
| `SLEEP_LONG` | `1800` | `WAITING=1`（= BaiZe `SLEEP_WAIT`） |
| `CLINE_TIMEOUT` | `1500` | 单次 cline 上限（= BaiZe） |
| `PUSH_INTERVAL` | `18000` | git 兜底同步间隔（= BaiZe） |

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
