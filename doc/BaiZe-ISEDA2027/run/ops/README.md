# ops/ — 经 git 中继的远程命令通道

> **为什么存在**：Windows 侧运维**无法 SSH** 到 GPU 服务器（`10.239.2.29` / `10.239.2.12`），
> 只能用 git 与服务器交互。而现成的 3 个 agent 每次唤醒要跑 25 分钟 cline 且烧 token，
> 不适合"跑几条 shell 命令看看环境"这种需求。
>
> 本通道是一条 **纯 bash、零 token、高频**（默认 ~20s 轮询 / ~60s fetch）的命令执行与回收路径。

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

```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
git pull --rebase
setsid bash ops_relay.sh > /tmp/baize_ops_relay.log 2>&1 < /dev/null &
```

停止：`pkill -f ops_relay.sh`

## 3. 参数（`ops_relay.sh` 顶部可改）

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

- 本通道**不替代** data agent 的 `phase0` 正式盘点——中继给快速答案，`phase0` 出正式清单
- 共享工作副本：本通道只 `git add` 自己的 `ops/` 文件，不用 `git add -A`
- 与 vision / pretrain / data 三个 agent 共用同一份工作副本与同一块 NFS，
  重 I/O 命令请避开 vision 的 R2-4（干净吞吐测量）

## 6. 首次预置的命令

`inbox.md` 里已预置 **RUN_ID 1：GPU 服务器环境摸底**——包括主机/CPU/内存/磁盘/GPU、
正在运行的 loop 与训练进程、远端 `10.239.2.12` 的状态、git 状态、
数据根目录清单、关键数据集规模、python/torch 版本、repo 布局。
**启动后约 1 分钟就能拿到第一批环境实况。**

---

## 9. 双机中继（2026-10-24 起）：每台服务器一个，**任务按机器投递**

两台机各跑一个 `ops_relay_v2.sh`（v1 `ops_relay.sh` 共用 `.last_run_id`，会**双执行**，已废弃）。

**投递语法**（写在 `inbox.md` 第 3 行的注释里）：

| 写法 | 谁执行 |
|---|---|
| `<!-- RUN_ID: 163 -->` | **both** —— 两台机各执行一次 |
| `<!-- RUN_ID: 164 \| TARGET: 29 -->` | **只在 `.29`** |
| `<!-- RUN_ID: 165 \| TARGET: 12 -->` | **只在 `.12`** |

**游标**：每台机各一份 `ops/.last_run_id.<TAG>`（TAG = hostname 末尾两位，如 `29` / `12`）。
- 不是投给本机的 RUN_ID **不会推进**本机游标 ⇒ 之后的 `both` 或投给本机的更大 RUN_ID 仍会执行。
- 因此 `TARGET` 只影响"这一条给谁"，不会漏掉后续任务。

**启动 / 停止**

```bash
# 启动（每台机各执行一次；TAG 自动从 hostname 取）
setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops_relay_v2.sh \
  > /tmp/baize_ops_relay.<TAG>.log 2>&1 < /dev/null &
# 停止
pkill -f ops_relay_v2.sh
```

**注意**：两台机**共享同一个 NFS 工作副本**，所以 `inbox.md`/`outbox.md`/`state` 都是同一份文件；
v2 用"每机一份 state"消除了 v1 的抢单竞态，但 **`git push` 仍可能撞车**（v2 已内置 3 次重试 + rebase）。

---


## 7. 已知环境事实：节点外网 / 代理（2026-10-15 实测）

| 节点 | 直连外网 | github 需要 | HF 数据需要 |
|:--|:--|:--|:--|
| `.29`（whag0pgpuap29，中继主机） | ✅ **直连可用**（github/hf.co 均 200） | 直连即可（proxy 也 200） | 直连或 92.25 |
| `.12`（whag0pgpuap12，vision 线） | ❌ **直连 github `000`（不可达）** | **`http://172.19.92.23:13128`** | **`http://172.19.92.25:13128` 直连 hf.co**（🚫 不用 hf-mirror） |

**口径（用户直令 2026-10-15）**：**连 github 用 92.23；下数据用 92.25 直连 hf.co。**

### ⚠️ `.12` 的 git push 曾长期失败（2026-10-15 已修）

- **症状**：vision loop 日志反复 `push FAILED … Failed to connect to github.com port 443 … Network is unreachable`；
  叠加共享工作副本偶发 `.git/index.lock` 被占（`fatal: Unable to write new index file`）⇒ **提交推不出来**（12:15→18:29 有 6 小时在 git 上看不到进展）。
- **根因**（RUN_ID 94 实测）：`.12` **直连 github = `000`**，而该机 **git 全局/仓库级都没有 `http.proxy` 配置、loop 环境也没有 proxy 变量** ⇒ git 走直连必然失败。
- **修法（已实施，RUN_ID 94）**——**写在 git 配置层**，因为 vision loop 调 cline 时会 `env -u http_proxy -u https_proxy …` **剥掉 proxy 环境变量**，只有 git config 能存活：
  ```bash
  # 在 .12 上（用户 app.e0031982，共享 NFS HOME）
  git config --global http.proxy  http://172.19.92.23:13128
  git config --global https.proxy http://172.19.92.23:13128
  git ls-remote origin HEAD        # 验证（返回 HEAD sha 即通）
  ```
- **验证**：`.12` 上 `git ls-remote origin HEAD` ✅ 返回 sha；`git ls-remote` 走同一 remote/凭据，读写路径一致。
- **注意**：`.12` 与 `.29` **共用 NFS HOME 与工作副本** ⇒ 该 `--global` 配置对两机生效；但**若 `.12` 直连恢复**，建议移除该配置以免绕路（`git config --global --unset http.proxy`）。

---

## 8. ⚠️ 中继命令三条硬教训（2026-10-15 实测踩坑）

| # | 坑 | 现象 | 正确做法 |
|:--|:--|:--|:--|
| 1 | **`pgrep/pkill -f <串>` 会误伤 cline** | loop 把**整份任务书当参数**传给 `cline`（`cline -c … "$prompt"`）⇒ **任务书里出现的任何字符串都会匹配到 cline 进程**。2026-10-15 我用 `pgrep -f 'precache_benchmarks.py'` 取到的 PID **其实是 cline** | ① 取 PID 后**逐个核对 cmdline**、**排除含 `cline`/`bun` 的**；② 杀进程优先 `kill <PID>`；③ **writer 侧**：命令块里**别写会被 `-f` 匹配的敏感串**（`[p]recache…` 括号技巧**只防自匹配、不防 cline**） |
| 2 | **输出被 20000 字符截断** | 那次把 cline 的 33KB cmdline dump 出来 ⇒ 真正的 `[1]`–`[5]` 结果**全被截掉**，等于白跑一轮 | 大输出先 `cut -c1-140`/`head`；🚫 **不 dump `/proc/<pid>/cmdline`**（它可能就是整份任务书） |
| 3 | **SIGTERM 未必有效** | `pkill -f …` 打到 cline，但它**忽略 SIGTERM 继续存活**（precache 的 python 则正常退出） | 要停 cline 用 `kill -9`，且**先确认目标 PID 不是 cline** |

> 📌 同批经验（正向）：**HF 缓存迁移**用 `cp -a`（跨 FS，勿硬链）→ 实测把 `~/.cache/huggingface` 里已下的 lmms-lab 基准拷进新 `HF_HOME` 后，体积 6.3G→**22.4G**、precache 直接跳到 `[3/17]`（跳过已下集）⇒ **省 ~16GB 下载**。
