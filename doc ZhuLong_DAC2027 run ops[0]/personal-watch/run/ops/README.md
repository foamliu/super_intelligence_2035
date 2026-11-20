# ops/ — personal-watch **运维中继**（git 中继的命令通道，**零 token**）

> 与 BaiZe 的 `doc/BaiZe-ISEDA2027/run/ops_relay.sh` 同构，但**修掉了它的已知坑**、并加了针对本线的拦截。

## 1. 为什么有它

- supervisor（Windows 侧）**原设计上不能 SSH** 到观察哨机器 → 只能走 git。
- ✅ **2026-10-07 起：用户已授权 supervisor SSH 直连**（`liuyang@106.54.228.191`，**凭据不落库**）⇒ 定位变为
  **中继 = 便利通道（异步/零 token）· SSH = 保底通道（同步/强干预）**。本次「loop 换档 + 中继解冻」就是用 SSH 完成的。
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
| 🩺 **活性可观测**（2026-10-07） | 只在有动作时打日志（**静默 ≠ 死，但静默 14h 也看不出来**） | ✅ **每 ~10min 一行 `💓` 心跳**（`last_run_id` / `inbox_max` / `tick`）+ 启动行带**脚本自身 HEAD 版本**（`HEAD=<sha>`）⇒ 一眼分辨「版本是否最新 / 还活着没有」 |
| 🧯 **命令块输出捕获**（2026-10-07 加固） | — | ✅ 改**落盘捕获**（不再 `out="$( … )"`）+ stdin 接 `/dev/null` ⇒ **根治「块里 `setsid … &` 起守护 → 管道写端永不关闭 → 父 bash 卡在 `pipe_read` 永久等 EOF」**（本线 2026-10-06 18:06 真实冻死 14h，见 §4.5） |
| 🔊 **git 失败可见**（2026-10-07） | — | ✅ `fetch` / `pull` 失败**打印真实原因**（旧版 `>/dev/null 2>&1 \|\| return 0` = **静默吞错** ⇒ 同步失败无人知） |
| 🔓 **单实例锁判活**（2026-10-07） | — | ✅ `kill -0` **＋核对 `/proc/<pid>/cmdline` 含 `ops_relay`**（防 PID 回收误挡启动）+ **`RELAY_FORCE=1` 强制接管**（仅在确认旧实例半死时用） |

## 4.5 🧯 已修故障：中继「活着但冻死」14h（2026-10-06 18:06 → 2026-10-07 08:15）

**症状**（极易误判为"正常待命"）：

| 判据 | 冻死时 | 正常时 |
|:--|:--|:--|
| `pgrep -af watch_ops_relay` / `kill -0 <pid>` | **通过** ⛔（最误导） | 通过 |
| `/tmp/watch_ops_relay.log` mtime | **14h 没动** | 每 ≤10min 有 `💓`（2026-10-07 后） |
| `ops/.last_run_id` | **永停**（inbox 已到 11，它还在 10） | 会跟上 |
| `/proc/<pid>/wchan` | **`pipe_read`** ⛔ | `do_wait` / `hrtimer_nanosleep` |
| `/proc/<pid>/fd/*` | **`pipe:[…]`（只读端）且无子进程** | 无异常管道 |
| `/proc/<pid>/io` 的 `syscr` | **不涨** | 持续涨 |

**根因**：老版 `run_once` 用 `out="$( cd … && timeout … bash -c … )"` 捕获输出；**命令块里 `setsid … &` 起的后台守护继承了该命令替换管道的写端且永不关闭** ⇒ 父 bash 在 `pipe_read` 上**永久等 EOF**（`timeout 600` 只杀得掉前台 bash，杀不掉已脱离的守护）。
**WSL 对照实测：旧法 8s（等守护退出）/ 新法 0s。**

**加固后的判活 / 处置**（已上机，commit `c8fcdb3c`）：

```bash
# ① 判活（新）：应见 ≤10min 一行心跳 + 首行带 HEAD
tail -3 /tmp/watch_ops_relay.log     # [relay] 💓 … alive pid=… last_run_id=… inbox_max=… tick=…
# ② 卡死判据：wchan == pipe_read ⇒ 立即处置（TERM 对它无效）
P="$(cat /tmp/watch_ops_relay.pid)"; cat /proc/$P/wchan; echo
# ③ 处置：留档旧日志 → kill -9 → 直接重启（pidfile 里 PID 已失效，新锁会自动放行）
cp /tmp/watch_ops_relay.log /tmp/watch_ops_relay.log.frozen-$(date +%m%d)
kill -9 "$P"
cd ~/super_intelligence_2035/doc/personal-watch/run && \
  setsid bash -c 'exec -a watch_ops_relay.sh bash ops_relay.sh' > /tmp/watch_ops_relay.log 2>&1 < /dev/null &
sleep 5; cat /tmp/watch_ops_relay.pid; head -1 /tmp/watch_ops_relay.log
# ④ 活性核验（不靠"看起来没事"）：wchan 应 ≠ pipe_read，且 12s 内 syscr 增长
Q="$(cat /tmp/watch_ops_relay.pid)"; cat /proc/$Q/wchan; echo
awk '/^syscr/{print "syscr#1="$2}' /proc/$Q/io; sleep 12; awk '/^syscr/{print "syscr#2="$2}' /proc/$Q/io
```

> ⚠️ **`RELAY_FORCE=1` 的适用边界**：它只跳过单实例锁。**若旧实例真的还活着并会干活（只是你认为它卡了）⇒ 会出现两个中继同时 push**。
> ⇒ 规矩：**先 `kill -9` 再起**（此时新锁会正确放行）；`RELAY_FORCE=1` 仅在「pidfile 指向的 PID 还活着且你已确认它半死」时用。

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
