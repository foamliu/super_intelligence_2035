# ops/ — 经 git 中继的远程命令通道（ZhuLong DAC2027 版）

> **为什么存在**：Windows 侧运维**无法 SSH** 到 GPU 服务器（36.15 / 2.12），
> 只能用 git 与服务器交互。ZhuLong loop 每次唤醒跑 45 分钟 cline 且烧 token，
> 不适合"跑几条 shell 命令看看环境"这种需求。
>
> 本通道是一条 **纯 bash、零 token、高频**（默认 ~20s 轮询 / ~60s fetch）的命令执行与回收路径。
>
> ⚠️ **本 ops 路径 `doc/ZhuLong_DAC2027/run/ops/` 与 BaiZe 的 `doc/BaiZe-ISEDA2027/run/ops/` 相互独立**，
> 各有各的 relay 进程、inbox/outbox、与 last_run_id。互不干扰。

---

## 1. 怎么用（运维侧，三步）

```
① 编辑 ops/inbox.md  ——  在 ```bash 块里写命令，把 <!-- RUN_ID: N --> 改成 N+1
② git push
③ 等 1~2 分钟 → git pull → 读 ops/outbox.md 末尾（最新结果在文件最下方）
```

- **整块会被当成一个脚本执行**：可以写变量、循环、管道、`ssh`
- **只有 `RUN_ID` 增大才会执行**：避免重复跑；也避免因为改动空白而误触发
- 想跑第二批就再写一个块、把 RUN_ID 加到 2（历史命令覆盖掉即可，outbox 保留全部结果）

## 2. 怎么启动（服务器侧，一次）

<div class="callout warn">
  <b>路径前缀：</b>以下以 2.12 开发机路径 <code>/nas_train/</code> 为例。36.15 服务器上启动时请将 <code>/nas_train/</code> 替换为 <code>/nasdata/</code>。
</div>

```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
git pull --rebase
setsid bash zhulong_ops_relay.sh > /tmp/zhulong_ops_relay.log 2>&1 < /dev/null &
```

停止：`pkill -f zhulong_ops_relay.sh`

## 3. 参数（`zhulong_ops_relay.sh` 顶部可改）

| 变量 | 默认 | 含义 |
|:---|:---|:---|
| `POLL` | 20 | 本地轮询间隔（秒） |
| `FETCH_EVERY` | 3 | 每 N 次轮询做一次 `git fetch`（=> 默认约 60s 拉一次远端） |
| `CMD_TIMEOUT` | 600 | 单个命令块总超时（秒），超时被 `timeout` 终止并记录 |
| `MAX_OUT_CHARS` | 20000 | 单次输出截断上限 |

## 4. ⚠️ 安全边界（**必须知悉**）

这是一条**远程代码执行通道**。请确保：

1. **仓库保持 private** —— 任何能 `push` 的人都能在服务器上执行命令
2. **每条被执行的命令都原文记入 `outbox.md`**，作为审计留痕（不要删）
3. 脚本里只有**防手滑**级别的危险模式拦截（`rm -rf /`、`mkfs`、`dd of=/dev/` 等），
   **它不是安全边界**，不要依赖它
4. 不需要时**直接 `pkill` 掉**，不要长期挂着

## 5. 与其他 agent 的关系

- 本通道**不替代** zhulong_loop.sh 的正式启动——中继给快速答案，zhulong_loop.sh 出正式评测
- 共享工作副本：本通道只 `git add` 自己的 `ops/` 文件，不用 `git add -A`
- 与主 loop（zhulong_loop.sh）共用同一份工作副本与同一块 NFS，
  重 I/O 命令请避开评测运行窗口（查看 MEMORY_ZHULONG.md 的 WAITING 判断当前评测状态）

## 6. 首次预置的命令

`inbox.md` 里已预置 **RUN_ID 1：ZhuLong 环境摸底**——包括主机/CPU/内存/磁盘/GPU、
四 shard 端口（8664/8665/8653/8669）监听状态、EDA license 可用性、
正在运行的 loop 与评测进程、git 状态、repo 布局。
**启动后约 1 分钟就能拿到第一批环境实况。**
