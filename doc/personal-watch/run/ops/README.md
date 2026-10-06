# ops/ — personal-watch **运维中继**（git 中继的命令通道，**零 token**）

> 与 BaiZe 的 `doc/BaiZe-ISEDA2027/run/ops_relay.sh` 同构，但**修掉了它的已知坑**、并加了针对本线的拦截。

## 1. 为什么有它

- supervisor（Windows 侧）**不能 SSH** 到观察哨机器 → 只能走 git。
- **worker loop 停 / 撞额度 / OOM 时，git 上"什么都看不到"** —— 本中继**不依赖 cline、不依赖额度**，
  **loop 停着也能执行诊断与运维命令**（这是它最大价值）。

## 2. 工作方式

```
supervisor：编辑 ops/inbox.md（新增 `## RUN_ID N` + 一个 ```bash 块）→ git push
   ↓
中继：每 ~60s fetch → 发现 RUN_ID 变大 → 执行该块 → 结果 append 到 ops/outbox.md → commit+push
   ↓
supervisor：git pull → 读 ops/outbox.md
```

## 3. 启动 / 停止（**在观察哨机器上**）

```bash
cd ~/super_intelligence_2035/doc/personal-watch/run
git pull --rebase --autostash
# ⭐ 必须用 exec -a 起：否则 cmdline 只有 "bash ops_relay.sh"（与 BaiZe 撞名，且 pkill -f watch_ops_relay.sh 匹配不到）
setsid bash -c 'exec -a watch_ops_relay.sh bash ops_relay.sh' > /tmp/watch_ops_relay.log 2>&1 < /dev/null &

cat /tmp/watch_ops_relay.pid          # ⭐ 数实例**以 pidfile 为准**（最可靠）
ps -o pid,etime,args -p "$(cat /tmp/watch_ops_relay.pid)"   # 确认它还在
tail -5 /tmp/watch_ops_relay.log      # 看 [relay] started（首行含 pid= / pidfile=）
```
**停止**（两种都行）：`pkill -f watch_ops_relay.sh` 或 `kill "$(cat /tmp/watch_ops_relay.pid)"`
> ⚠️ **不要用 `pgrep -af <脚本名>` 去"数实例"** —— bash 的 `$(...)` fork 子 shell **不 exec、沿用父进程 argv**，
> 会被 `pgrep/ps` 误当成"新实例"（`etime 00:00` 的幽灵）。2026-10-05 我就因此**误报过"出现第三个中继"**。
> 判定实例数请以 **pidfile** 或 `ps -o pid,etime` 中 **etime 较大者**为准。
> 🛡 **单实例锁**：脚本用 `/tmp/watch_ops_relay.pid` 防重复启动（**发现已在跑则新实例自动退出**）——
> 修复 2026-10-05 实测的「**两个中继并存 → 同一 RUN_ID 被跑两遍、提交两遍**」。
> ⚠️ **不要** `pkill -f ops_relay.sh` —— 裸 cmdline 会**连带匹配到 BaiZe 的中继**。

> 🚫 **绝不要杀中继来"重启它"之外的任何目的** —— 它是你唯一的远程通道（BaiZe 那边有"绝不 kill watchdog"的教训）。

## 4. 与 BaiZe 版的差异（**我们修掉/加强了什么**）

| 项 | BaiZe 版 | 本版 |
|:--|:--|:--|
| **命令块解析** | ⚠️ **只执行文件里第一个 ```bash 块** → 新命令**静默失效**（他们踩过） | ✅ **支持多段 `## RUN_ID N` 共存**，把 `> .last_run_id` 的块**按升序全部执行** —— 既修 BaiZe「漏末尾」，也修本版早期「只跑最大 → **静默跳过中间块**」（RUN_ID 4 即因此丢失） |
| **单实例** | 无 | ✅ **`/tmp/watch_ops_relay.pid` 单实例锁**（防「两实例并存 → 同一 RUN_ID 跑两遍 + 提交两遍」） |
| **进程可辨识** | — | ✅ 启动用 `exec -a watch_ops_relay.sh` → `pgrep/-pkill -f` **又准、又不误伤同名 cmdline** |
| **危险模式** | `rm -rf /`·`mkfs`·`dd`·fork bomb | ＋**`git clean -fdx`**（会删掉别线在途文件）· **`git reset --hard`** · **杀 `ops_relay`**（别断信道） |
| 提交范围 | 只 add `ops/` | 只 add `ops/`（`outbox.md`/`inbox.md`/`.last_run_id`） |

## 5. ⚠️ 安全（务必知悉）

- 这本质是**远程代码执行通道**：**能 push 的人 = 能在这台机上执行命令**。
  → **仓库必须保持 private**；🚨 与 **`doc/keys.txt` 入仓**（见 `../DEPLOY_CHECKLIST.md` §6）叠加时风险放大 → **请轮换 Key**。
- **每条命令原文记入 `outbox.md`**（审计留痕）。
- 危险模式拦截**只是"防手滑"，不是安全边界**。
- 单块 **600s 超时**；输出超 **20000 字符**截断；长输出请自行 `cut -c1-140`。

## 6. 常见用途（直接用）

| 场景 | 写进 `inbox.md` 的块 |
|:--|:--|
| **诊断 loop 为何停** | 见 `inbox.md` **RUN_ID 1**（进程/日志/OOM/资源/cline base/git 状态） |
| **重启 loop** | `pkill -f 'watch_news_loop.sh'; sleep 2; cd ~/super_intelligence_2035/doc/personal-watch/run && setsid bash watch_news_loop.sh > /tmp/watch_news_loop.log 2>&1 < /dev/null &` |
| **看心跳（新增条款）** | `tail -5 ~/super_intelligence_2035/doc/personal-watch/run/daily-memories-*/$(date +%F).md` |
| **看额度/鉴权** | `tail -30 /tmp/watch_news_loop.log \| grep -iE '额度\|429\|403'` |
