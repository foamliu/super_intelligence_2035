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
