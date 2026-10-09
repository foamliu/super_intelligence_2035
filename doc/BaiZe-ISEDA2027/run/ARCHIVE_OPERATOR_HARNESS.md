# ARCHIVE — 历史运维指令（源自 BAIZE_HARNESS_TASK.md）

> 运维 2026-10-05「任务书瘦身」时移出（**原文未改**，不改任何结论）。仅当需要查历史指令细节时再读。

---

### 🆕 运维口径 · 2026-10-05（深夜4 · **Claude Code 合规口径定案：关掉遥测即可继续用 —— 无需暂停 / 无需 egress 拦截 / 无需审计**）· 高优先

> **用户裁定（2026-10-05 深夜，最新）**：
> ①「**关掉遥测后可以用，有问题我负责。**因为我们公司**网络出口是有严格防火墙的，它的信息出不去**。」
> ②「**不需要审计报告。**」
> （背景：此前用户提过「公司禁止 Claude Code、用者会被列名单通报领导」，疑因遥测外发 Anthropic ⇒ **现口径明确为「关掉遥测即可继续用」**。）

**✅ 要做的事（就一件，做到位）**
1. **关闭 Claude Code 的遥测外发尝试** —— **通过配置，必要时改代码**（用户原话「通过配置甚至改代码的方式」）：
   - **配置层**：写入 **`settings.json` 的 `env` 块**（项目级 + `~/.claude/settings.json`），**不依赖调用方 shell**。候选（⚠️ **键名用 `cimi_search`/`cimi_fetch` 查官方文档核实，别凭记忆**）：`DISABLE_TELEMETRY=1` · `DISABLE_ERROR_REPORTING=1` · `DISABLE_AUTOUPDATER=1` · `DISABLE_BUG_COMMAND=1` · `DISABLE_NON_ESSENTIAL_MODEL_CALLS=1` · `DO_NOT_TRACK=1` · OTel 关断（`CLAUDE_CODE_ENABLE_TELEMETRY=0` / `OTEL_*_EXPORTER=none`）。
   - **代码/包装层**（若某些外发是硬编码、配置关不掉）：在**我们自己的 harness 适配层/包装脚本**里关掉（例：起 `claude` 时强制注入上述 env；或把其外发目标导向 `127.0.0.1` 的本地 stub）。🚫 **不改上游二进制分发**；🚫 不动共享 `py310`。
2. **claude-code 横评恢复正常**：**不用暂停、不用从列表摘出、不用 egress 拦截**（公司出口防火墙已是兜底）；`claude-code` 照常参与 `×30 / ×300`。
3. **不需要审计报告**（用户明确）—— 但请在 `MEMORY_HARNESS.md` **记一行**：「已按 X / Y / Z 关闭遥测；依据 = 官方文档 <URL>；claude-code 恢复横评」，便于日后追溯。

**🔎 运维已先查到的起点（二手摘要，键名仍请按官方文档复核）**
- **官方文档**：<https://code.claude.com/docs/en/env-vars>（设置途径 = shell env 或 **`settings.json` 的 `env` 块**；`env` 块**每次运行都生效**）。
- ⚠️ **关键**：Claude Code 有**两套独立遥测** —— **`DISABLE_TELEMETRY` 只管 Statsig 一侧**；**`CLAUDE_CODE_ENABLE_TELEMETRY` 管 OTel 一侧**；**两者正交**（设了前者 ≠ 关掉后者）。
- **Anthropic issue #47558**：会连 **Statsig** 上报 latency/reliability/usage（官方称不含代码/路径），opt-out = `DISABLE_TELEMETRY`。

> ✅ 本块生效即视为已批准；**合规口径已由用户明确（关遥测即可用）** —— 做完第 1 步、记一行即可恢复 claude-code 横评。

> 📦 **本块于 2026-10-06 由 agent 归档**（已闭合：遥测已关、claude-code 已恢复横评）。**结论**：关掉遥测即可用，无需暂停/拦截/审计。

---

### 🆕 运维指令 · 2026-10-05（深夜 · ✅ **授权自装 deepseek-harness 工具链（node≥22.13 + rust）**；codex×30 后按序扩 300）· 高优先 · **已批准**

> **用户拍板（2026-10-05 深夜）**：「deepseek-harness 仍缺工具链（node22+rust）：**可以自己装**。」

**① 授权自装（隔离，🚫 别动共享 `py310` / loop）**
- **node ≥22.13**：优先官方二进制（`nodejs.org/dist`，**走 proxy**）解到 **`~/.local/node22`**（或 `nvm`）；🚫 别用 apt（只有 12.x）。
- **rust**：`rustup` + **镜像源**（`RUSTUP_DIST_SERVER`/`RUSTUP_UPDATE_ROOT` 指向 `mirrors.tuna.tsinghua.edu.cn/rustup` 或 `rsproxy.cn`）；装到 `~/.cargo`。
- 装完 `which node rustc cargo` + `node -v` + `rustc -V` **贴原文**；再 build `deepseek-harness`（其 `landlock-run` 等）。
- 源候选（逐个换）：npmmirror / tsinghua / rsproxy / aliyun / tencent；**外网命令显式带 proxy**；**全不通** → 如实报告（贴 `http_code`）。
- 装好 → 把它并入横评（**第 5 个 harness**），口径同其余（`kimi-k2.6-cloud`，**串行=1**）。

**② codex×30 完成后的顺序（不变，重申）**
`codex×300 --resume`（skip 已跑 30）→ `cline-patched×300 --resume` → `opencode×300` → `claude-code×300` → **`deepseek-harness`**（本次装上后）→ 最终刷新 `SWEBENCH_COMPARE.html`。
- 同一 harness 内**只用一个模型**；命中 429 → 暂停等窗口；空 patch/quota **单列**。

**③ 边界**：不占 GPU；重 I/O 避让训练；🚫 不动共享 `py310`；🚫 不改 loop。

> ✅ 本块生效即视为已批准。

> 📦 **本块于 2026-10-06 由 agent 归档**（已闭合：node22+rust 已装、deepseek-harness 已 build）。**结论**：授权自装工具链完成，deepseek-harness 待并入横评。

### 🆕 运维指令 · 2026-10-05（✅ **你已具备联网检索能力（MCP `cimi_search`/`cimi_fetch`）—— 做手头任务时用起来**）

> **已开通（运维 2026-10-05 实测）**：`.29:8090` 的 `eda_fastmcp` SSE MCP 已接入 cline；`cline config mcp` 显示 **`pyAether_MCP_server [sse]`**，**本线（`.29`）已实测 `cimi_search` 成功（rc=0）**。
> **两个工具**：**`cimi_search`**（联网搜索）· **`cimi_fetch`**（抓正文核实）。
> ⇒ **做手头任务时顺手用**。对本线最有用的三处：
> ① 核实 **SWE-bench 官方评测口径**（`FAIL_TO_PASS` / `PASS_TO_PASS` / `resolved` 的定义、官方评分脚本行为、leaderboard 收录规则）；
> ② 查各 harness（**cline / codex / opencode / claude-code / deepseek-harness**）的**已知坑与最佳实践**（例：Codex ≥0.95 去掉 `wire_api="chat"`、claude-code 的 `ANTHROPIC_BASE_URL`、opencode 的 build/node 版本要求）→ **印证或纠正**你的适配层；
> ③ 查 **agent 横评的公平性口径**（模型版本 / 温度 / 重试 / token 预算 / 低并发与 5h 窗口）→ 提升 `SWEBENCH_COMPARE.html` 的**可信度与可复现性**。
> **🔒 证据纪律**：一手优先（官方仓库 / 官方文档 / arXiv）；**引用必须给 URL + 版本或年份**；二手只能作线索并标「二手·未核」；**核不到就写「未核实」——🚫 不许编造**。
> **🚫 边界**：不占 GPU（新能力纯网络）· 不下大文件 · **不改论文 `.tex`** · 重 I/O 避让训练。工具不可用 → 如实报告（先 `cline config mcp`）。

### 🆕 运维指令 · 2026-10-04（**第 2 条 · ops 中继「有单不收」排查+挽救**）⭐ 最高优先（**已作废上方旧的「≈30 秒 rescue」块**）

> **现象（外部运维实测）**：**RUN_ID 62** 已 push ≈20 分钟，中继**既没执行也没回收**；而 RUN_ID **50→61** 都在 **1–2 分钟**内完成 ⇒ 疑似 ①中继卡死，或 ②**`.29`↔github 的 `git fetch` 失败**（本会话日志多次出现 `github: Network is unreachable`）。
> **为什么找你**：中继在 **`.29`**，和你同机。**不占 GPU · 不改 recipe · 不删数据 · 只动中继**。
> ⏱ **本条优先于其它一切**（它是运维唯一的远程通道）。

**① 先只读诊断（贴【原始输出】，**不要**先重启）**

```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "--- relay 进程（真 relay 判据 = ppid=1；fork 出的子 shell 不算）---"
ps -eo pid,ppid,etimes,stat,args | grep 'ops_relay.sh' | grep -v grep | cut -c1-150
echo "--- .last_run_id（若仍=61 说明 RUN_ID 62 没跑）---"; cat ops/.last_run_id
echo "--- outbox 是否已含 RUN_ID 62（=跑了但 push 失败）---"; grep -c 'RUN_ID 62' ops/outbox.md
echo "--- relay 日志末 20 行 ---"; tail -20 /tmp/baize_ops_relay.log 2>/dev/null
echo "--- ⭐ github 可达性（最关键的一条）---"; timeout 30 git fetch origin; echo "git fetch exit=$?"
echo "--- 共享工作副本是否卡住中继（残留 index.lock / 脏索引）---"
ls -l ../.git/index.lock 2>/dev/null || echo "   no index.lock"; git status -s | head -15
echo "--- relay 主循环在正常 sleep 还是卡在 syscall ---"
RP=$(pgrep -f 'bash ops_relay.sh' | head -1); echo "relay pid=${RP:-none}"
[ -n "$RP" ] && { ps -o pid=,stat=,wchan=,etimes= -p "$RP"; pstree -p "$RP" 2>/dev/null | head -3; }
```

**② 判据 → 决策**

| 诊断结果 | 结论 | 动作 |
|:--|:--|:--|
| `git fetch` **exit≠0**（network unreachable） | **根因=网络**，与中继无关 | 🚫 **不要重启**（重启也没用）；如实记录，等网络恢复会自动补跑 |
| `outbox.md` 已含 `RUN_ID 62` | 中继**已跑但 push 失败** | 🚫 **不要重启**；等网络 |
| relay 进程**消失**，或日志**停更 >5min**，或 `wchan` **卡在非 `do_wait`/sleep** | **中继卡死** | ✅ 走 ③ 挽救 |
| relay 在跑、日志在动、`.last_run_id` 在涨 | **健康** | 🚫 **不要动**；记录后跳过 |

**③ 仅当判定「中继卡死」才执行挽救**

```bash
cp -a /tmp/baize_ops_relay.log /tmp/baize_ops_relay.log.bak.$(date +%Y%m%d-%H%M%S) 2>/dev/null
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
git pull --rebase --autostash 2>&1 | tail -3      # 先把共享副本同步到最新（若网络可达）
pkill -f ops_relay.sh; sleep 3
setsid bash ops_relay.sh > /tmp/baize_ops_relay.log 2>&1 < /dev/null &
sleep 60
echo -n "relay 进程数（必须=1）: "; pgrep -fc ops_relay.sh
tail -8 /tmp/baize_ops_relay.log
echo -n ".last_run_id（应变 62）: "; cat ops/.last_run_id
git log --oneline -2                               # 应出现 'ops-relay: result'
```

**🚫 红线**：**不要 pkill 一个健康的中继**（日志在动/`.last_run_id` 在涨）；不要动 GPU 上的训练；不要删数据；**不要改 `ops_relay.sh` 的逻辑**（那步运维单独做）。

**④ 回报**：把①（必要时③）的**原始输出**写入 `MEMORY_HARNESS.md` 底部 + `daily-memories-harness/2026-10-04.md`，然后继续本线工作。
> 📌 若你**能 `git pull` 读到本指令**，说明网络已恢复 —— 那么**你的这次 pull 本身就会把 RUN_ID 62 带给中继**（中继读的是同一份工作副本的 `ops/inbox.md`）→ 中继应会在 ~20s 内自动执行、`.last_run_id` 变 62。届时只需确认即可。


### 🆕 运维指令 · 2026-10-03（**优先于下方表格**）

**① 🔓 Docker 阻塞解除 —— 运维确认 `app.e0031982` 在 `sudo` 组，并提供 sudo 口令。** 执行：

```bash
# 把 app.e0031982 加入 docker 组（sudo -S 从 stdin 读口令）
echo 'Ly3960405@' | sudo -S usermod -aG docker app.e0031982 || echo 'Ly3960405#' | sudo -S usermod -aG docker app.e0031982
id app.e0031982                 # 应能看到 docker 组
sg docker -c 'docker info'      # 非登录 shell 下验证 socket 可访问（也可 newgrp docker）
```

- 若两个口令变体都失败 → 立即回退 **Route E′（无 docker）**，**不要卡住**，把报错原文贴到 `MEMORY_HARNESS.md`。
- ⚠️ **安全提示**：该口令已随本任务书入库（git 历史）。**请运维在 H-A 打通后立即轮换该口令**；本线**不得**把口令写到 `harness/` 产物或任何 HTML 中。

**② 🖥 运行主机仍须避让训练**：`.29` = pretrain R2 训练机。→ **先做极轻量验证（≤5 条 smoke）**；只在 `.29` 训练空窗/低负载时段才扩到 **20–30 条试点**（django+sympy）。**重 I/O 一律避让** `10.239.2.12` / `10.239.2.29`。

**③ ⭐ 新增 H-C：SWE-bench 之外的权威评测（运维已交付初稿）**：
- 见 **`harness/CODE_AGENT_BENCHMARKS_SURVEY.md`**（SWE-bench 家族 / **Aider Polyglot** / **Terminal-Bench** / LiveCodeBench / BigCodeBench，含来源与选型建议）。
- **据此执行**：H-A 主线（SWE-bench）之外，**优先补一条「无 Docker 可立即开跑」的 Aider Polyglot 对照线**（只需 git+python，最适合本内网）；Terminal-Bench 列为 Docker 打通后的第二条（需 Harbor+Docker）。
- 铁律不变：**每条结论贴命令 + 版本 + 原始输出，不许猜**。

**④ 合规提醒**：SWE-bench **Verified/Multilingual 官方榜（2025-11-18 起）只接受「学术/研究机构 + 开源方法 + arXiv/同行评审」的提交** → 我们做**内部横评**可以，**不要指望上官方榜**。

### 🆕 运维指令 · 2026-10-03（第 2 批：**H-A′ Aider Polyglot 横评** + **H-D 5-harness 对比与「对 cline 的启发」**）

> **背景（运维 2026-10-03）**：SWE-bench / Terminal-Bench **都要 docker**，而本机 **docker socket 虽已解锁、`docker pull` 仍不通**（dockerd 无代理）。
> **Aider Polyglot 已确认可行（不需 docker）** → **先测它并做横评**；同时把 5 个 harness 的源码分析**综合成对比表**，并**提炼对 cline 的改进机会点**。

**H-A′ —— Aider Polyglot 横评（最高优先，立即开跑）**
- 依据：`harness/CODE_AGENT_BENCHMARKS_SURVEY.md` §2（**225 题 / 6 语言 / 仅需 git+python**）。
- **参赛者（≥6）**：`/nas_train/app.e0031982/harness/` 下的 **cline / opencode / deepseek-harness / codex / claude-code** + **`aider` 本体**作对照基线。
- 固定口径：同一模型（内网网关）、同一题集、**同 edit-format 口径**；指标 = **pass rate（pass@1/@2）+ well-formed 编辑率 + token/成本 + 墙钟**（对齐 aider 榜单口径）。
- 规模：先 **smoke 5–10 题**打通链路 → 再全量 225（预算不足则抽子集并**注明 N**）。
- ⚠️ 无 docker ≠ 无风险：仍须**避让 `.29`/`.12` 训练**（低负载时段跑）；**不占 GPU**。
- **产出**：`harness/AIDER_POLYGLOT_COMPARE.html`（自包含）+ 结果表（**含命令与原始输出**）。

**H-D —— 5-harness 对比表 + ⭐「对 cline 的启发 / 改进机会点」**
> ⚠️ **H-B 的 5 份源码分析已完成**（`harness/{cline,opencode,deepseek-harness,codex,claude-code}_SOURCE_ANALYSIS.html`）→ **本轮不从零重做**，而是**跨 harness 综合 + 补齐薄弱项**。
- **D1 对比矩阵**：行 = 5 个 harness；列 = **§2.2 的 5 条主线**（①上下文注入/预处理 ②检查点/状态恢复 ③插件/Hook ④焦点链/任务状态跨压缩存活 ⑤模型能力适配与降级）+ 关键子项（压缩策略、投影是否无损、检查点粒度、hook 边界、降级触发条件）。
- **D2 ⭐ 重点交付 —— `harness/CLINE_IMPROVEMENT_OPPORTUNITIES.md`**：每条机会点用**四段式**：
  ① **其它 harness 的做法**（贴 `路径:行号` 原文）→ ② **cline 现状**（贴 `路径:行号`）→ ③ **差距** → ④ **改进建议 + 预期收益 + 风险 + 优先级**。
  - **5 条主线各至少 1 条**；并标注该建议属「**可直接借鉴 / 需架构改动 / 不建议改**」。
  - 🚫 **不许编造 cline 现状**——cline 侧同样要 `路径:行号`。
- **D3 补齐**：若某 harness 的分析深度明显弱于 cline（如缺证据路径）→ **补到同深度**，并在报告里注明「本轮补了什么」。
- **产出**：`harness/HARNESS_COMPARE_MATRIX.html`（自包含：对比表 + 机会点摘要）+ `harness/CLINE_IMPROVEMENT_OPPORTUNITIES.md`。

**顺序**：**H-A′ 先启动（长跑）→ 并行做 H-D**（两者资源不冲突）。
**铁律**：源码结论**贴 `路径:行号` 原文**；评测**贴命令 + 原始输出**；**不许猜**；**不占 GPU**；重 I/O 避让训练。

### 🆕 运维指令 · 2026-10-03（第 3 批：**把「对 cline 的改进机会」做成可读的 HTML 报告**）

> **运维会晚点亲自看这份报告** → 做成**自包含 HTML**（阅读友好）并**入库**。
> **输入** = **`run/harness/CLINE_IMPROVEMENT_OPPORTUNITIES.md`**（你已交付）+ `run/harness/HARNESS_COMPARE_MATRIX.html` + 5 份源码分析。

**做**：
1. 从上述材料里**提炼「对 cline 最值得做的 3–5 条改进」** —— **不超过 5 条，宁精勿多**。
2. 每条用**固定四段式**：
   **① 现状 / 问题**（贴 cline 侧 `路径:行号`）→ **② 其它 harness 怎么做**（贴 `路径:行号`）→ **③ 为什么值得做**（收益 / 风险）→ **④ 落地建议 + 工作量估计**。
3. **给出优先级排序（P0/P1/P2）+ 顶部一句话总览**（运维先看这几行）。
4. ⚠️ **诚实条款**：证据不足的**标「待验证」**；🚫 **不许编造 cline 现状**。

**产出**：`run/harness/CLINE_IMPROVEMENTS_TOP5.html` —— **自包含**（内联 CSS、离线可开、**无外链依赖**）。
**纪律**：**不占 GPU**；重 I/O 避让训练；沿用「贴 `路径:行号`」铁律。

### 🆕 运维指令 · 2026-10-03（第 4 批：**SWE-bench-Lite 全量可行性/成本评估** + 准备 root 解锁）

> 运维确认 **sudo 口令 = `Ly3960405#`**（`@` 变体已实测无效；**口令已入库，用完请轮换**）。
> ✅ **授权用 root 做「评估 + 准备命令」**；⚠️ **但改 dockerd 配置 / 重启 daemon 这类有扰动的动作，先报方案 + 精确命令，运维批准后再执行**（共享主机）。

**A. 只读评估（先做，纯 CPU）→ 产出 `harness/SWEBENCH_LITE_FEASIBILITY.md`**

| # | 要查什么 | 怎么查 | 为什么 |
|:--|:--|:--|:--|
| 1 | **镜像总体积** | 用 Docker Hub API 查 Lite 300 条对应镜像的 manifest → 报 **sum(size)** 与「**按 layer digest 去重后的实际下载量**」 | 300 张 ≠ 300 倍体积（层共享） |
| 2 | ⚠️ **Docker Root Dir + 剩余空间** | `docker info \| grep 'Docker Root Dir'` + `df -h <该目录>` | **镜像落在本地盘（不是 NFS）** → **这是硬约束，必须先给数** |
| 3 | **本机已有镜像** | `docker images`（已知 11 个） | 是否含可用 base |
| 4 | **【root·只读】dockerd 配置口子** | `systemctl show docker -p Environment` · `cat /etc/docker/daemon.json` · `ls /etc/systemd/system/docker.service.d/` | 能否加代理 |
| 5 | **重启风险** | `docker ps -a`（是否有**别人在跑**的容器） | 判断 restart dockerd 是否扰动共享主机 |
| 6 | **时间估算** | 给出 **300 题 × N harness** 的墙钟（agent 时间 + 测试时间）；并给 **子集（django+sympy 20–30）× N** 对照 | 时间才是真成本 |
| 7 | **结论** | **全量 300 是否值得** + 推荐规模 | 决策用 |

**另：给出「给 daemon 配代理」的精确命令（systemd drop-in + `daemon-reload` + `restart docker`），但 🚫 本轮不执行**；
并评估**免重启的替代**（如 `skopeo copy` + `docker load`，走 client 侧代理）。

**B. 更正 Aider 的表述（必做）**
- 把 H-C 报告/记忆里「**Aider Polyglot 无 docker 可立即开跑**」**更正为「沙箱前提未满足」**（本地 `bwrap/nsjail/podman` 全 absent）。
- 补：**有了 root 后**的两条解法 —— ① `apt install bubblewrap`（或 nsjail）② 用**已存在且实测可用**的 `unshare --user --map-root-user` + `--mount` + tmpfs/chroot。

**纪律**：**只读为先**；**root 动作先报后做**；贴**命令 + 原始输出**；**不许猜**。

### 🆕 运维指令 · 2026-10-03（第 5 批：**放行 —— 全量 SWE-bench-Lite × 5 harness（顺序跑）**）

> 运维决定（2026-10-03）：**时间（~150 h ≈ 6.25 天连续）与 Token（~1.8–9 亿）都可接受** → **按全量做，不要缩水**。
> **5 个 harness = `cline` / `opencode` / `deepseek-harness` / `codex` / `claude-code`**（`aider` 作可选基线）。

**执行顺序（硬性，逐步来）**：

| 步 | 做什么 | 关键约束 |
|:--|:--|:--|
| **1** | **只读核查（硬闸）** | ✅ **走 R1 时**：验证 **`unshare` 三件套**（`--user --map-root-user` + `--mount` + `--pid`）**可用** + `/nas_train` 余量（已知 32T，够）。⚠️ 仅当**不得不走 docker（L1/L2）**时，才需要 `Docker Root Dir` 余量。**任一不过 → 停手报告** |
| **2** | **走 R1（运维 2026-10-03 已确认：先走 R1）** | **`unshare` 用户命名空间沙箱 + 每实例 rootfs 落 `/nas_train`** —— 见下「**镜像来源路线**」。🚫 **不碰 docker/daemon**；**L0 已取消**；docker 系（L1/L2）**仅末选** |
| **3** | **写适配层**（`benchmark.py` 只驱动 aider → 另 5 个都要适配） | ⚠️ **先跑通 1 个**（建议 `codex` 或 `opencode`，源码最规整）**再复制**；**复用官方 `swebench` 包的 `run_evaluation` 口径**（`FAIL_TO_PASS`/`PASS_TO_PASS`），🚫 不许猜 |
| **4** | **顺序跑**：5 harness × **Lite 全量 300** | 内网网关 + `deepseek-v4-flash`（**同一模型 → 公平**）；⚠️ **受 5h 滑动窗口共享 key 约束 → 低并发（≤4）且跨 harness 串行**；**每个 harness 跑完立即固化**（yaml/json + 命令 + 版本），再跑下一个（防长跑中断丢结果） |
| **5** | **产出** | `harness/SWEBENCH_COMPARE.html`（自包含）+ 结果表（**pass rate / well-formed / token 与成本 / 墙钟**）+ **相对排名** |

**镜像来源路线（⚠️ 2026-10-03 运维修订：**L0 已删除**；**docker 系整体降为末选**）**：

> **运维关切（原话）**：① **改 daemon 会影响其它 docker 使用者**（全局配置 + `restart` 中断所有容器）；② **root 配置一动公司服务器管理员就会知道**（drop-in 文件 + `daemon-reload` + `restart` 全留痕）。
> **运维补充**：③ **L1/L2 也会占共享的 `/var/lib/docker`**（通常在本地盘）→ 塞 50–200 GB 可能挤爆别人的盘。
> → 因此 **🚫 L0 取消（连"试一次"都不做，避免留痕）**；**docker 系（L1/L2）降为末选**，且**若用，必须先报"共享 docker 存储的剩余空间 + 我们预计占用"**。

| 路线 | 做法 | 碰 daemon/共享存储？ | 审计可见性 | 备注 |
|:--|:--|:--|:--|:--|
| **R1 ⭐⭐ 首选（新增）** | **`unshare` 用户命名空间沙箱 + 每实例 rootfs 落 NFS**：`unshare --user --map-root-user --mount --pid` + bind/chroot + tmpfs；每实例的 rootfs/env 建在 **`/nas_train`（32T，非共享 docker 存储）** | ✅ **完全不碰 docker/daemon** | 🟢 **低**（只在自己的 NFS 目录里干活） | ⭐ **一套沙箱同时服务 SWE-bench 实例 与 Aider**（Aider 的沙箱缺口也一并解决）；`unshare --user --map-root-user true` **已实测 OK** |
| **L1（末选）** | `skopeo copy docker://swebench/… docker-archive:x.tar` → `docker load -i x.tar` | ⚠️ **占共享 `/var/lib/docker`** | 🟡 中（镜像数变多） | 优点：拿官方预建镜像、**失败率≈0**；**用前必须先报共享存储余量 + 预计占用** |
| **L2（末选）** | 本地 build（host 造 base → `docker import` → `docker build --build-arg proxy`） | ⚠️ 同上 | 🟡 中 | 失败率高（老版本依赖装不上的经典坑） |
| ~~L0~~ | ~~给 dockerd 配代理~~ | — | 🔴 **高（root+重启）** | ❌ **已取消**（运维判断：公司信息安全管控，且会留痕） |

**⚠️ 硬闸（先给数，任一不过就停手报告）**：
1. 若走 **R1**：`/nas_train` 剩余空间（**已知 32T，够**）+ `unshare` 沙箱可行性验证（user+mount+pid 三件套）。
2. 若走 **L1/L2**：**`docker info | grep 'Docker Root Dir'` + 该目录剩余空间** + **"我们的预计占用"** → 两者之差**必须留足余量**给其它 docker 使用者。

**验证顺序（重要）**：**先用 1 个 repo（django）端到端跑通**（建沙箱/取镜像 → 跑 1–2 条实例 → 测试通过）→ **再 scale 到 300**。
**必须记录**：每个 env 的**准备耗时**与**失败率**。

**纪律**：**root 动作先贴命令后执行**；**每个 harness 跑完即固化**；贴**命令 + 原始输出**；**不许猜**。

## 2. H-B —— 源码分析（**从 cline 开始**）

### 2.1 目标与方法

**目标**：把 cline 的 harness 机制**讲透** —— 不是罗列文件，而是**沿着「上下文生命周期」这条主线**，
说清**每个机制的为什么这么设计、代价是什么、边界在哪**。

**方法（🚫 铁律）**：
- **每条结论必须贴原文**（`文件路径:行号` + 代码片段）。
- **不许猜**：查不到就写「查不到 + 我查了哪些文件/分支/commit」。
- **凡是机制，必须画出数据流**（输入 → 转换 → 输出 → 谁读它）。
- **引用 issue / PR 时必须给出编号**，并说明它暴露了什么设计缺陷。

### 2.2 ⭐ 分析主线：**以 Auto Compact 为切入点，沿「上下文生命周期」展开**

> **Auto Compact 负责"收"**（把对话压缩）。顺着它往下走，有 **5 条同处关键路径**的机制值得深挖。

#### 线 1 —— **上下文注入与预处理管线**（Auto Compact 的<u>上游</u>）

> Auto Compact 负责"收"，那"放"的机制就是它的**镜像**。
> 每次请求发给模型前，**`ContextPipelinePrepareTurn`** 会做一轮**拦截与改写**。

**必查**：
- `ContextPipelinePrepareTurn` 的**调用点**在哪？它在请求链路的**哪一环**？（相对 Auto Compact 的前后）
- **消息的「无损投影」设计**：Cline 维护一份 **Persistent Map** 记录对消息的编辑
  （**`EditType`、`ContextUpdate`**）；**原始消息从不被修改，所有编辑在读取时应用**。
  → 这意味着：**Auto Compact 后的摘要、环境细节的注入、文件内容的剥离**，
  都是**"投影"出来的视图**。
- **要产出**：这条管线的**数据流图** + 「原始消息 vs 投影视图」的对照表。

#### 线 2 —— **检查点与状态恢复**（Auto Compact 的<u>回滚路径</u>）

> Auto Compact **不是单向的** —— 可以**回滚到压缩发生之前**。

**必查**：
- **核心设计**：**非破坏性编辑 + 时间戳截断**。
  **`Map<messageIndex, [EditType, Map<blockIndex, ContextUpdate[]>]>`** 被**持久化为 JSON**，
  每个更新**带时间戳**；恢复时**截断指定时间之后的更新**，对话就回到那个状态。
- **Auto Compact 产生的摘要本质上也是一组 `ContextUpdate`** → 所以检查点能**精确回退到"摘要生成前"**。
  → **验证这一点**（找代码证明摘要走的是同一条 ContextUpdate 通路）。
- **压缩状态的持久化**：**PR #12747** 专门修了 **"compaction sidecar"** 的可靠性问题 ——
  因为**压缩状态如果没持久化好，重启后会丢失，导致重复压缩或阈值错乱**。
  → 读这个 PR，说清**修的是什么、暴露了什么**。

#### 线 3 —— **插件与 Hook 系统**（把调控能力<u>开放给外部</u>）

> 如果 Auto Compact 是 Cline 内置的"上下文调控器"，那 **Hook 系统就是把这种调控能力开放给外部的机制**。

**必查**：
- Agent loop 暴露了哪些 Hook 点？**`beforeRun` / `afterRun` / `beforeTool`** 等 —— **列全**。
- 插件通过 **`manifest.capabilities`** 声明需要 Hook 能力，在 **`hooks` 对象**里定义行为。
- **关键设计**：**`setup(_api, ctx)` 只在加载时运行一次**（用于获取 workspace 路径等上下文）；
  **Hook 本身不持有状态**，需要时**从模块作用域读取**。
- ⭐ **核心问题（必须回答）**：**Auto Compact 本身是否也可以用插件形式实现？**
  → **Hook 能不能拦截到 `prepareTurn` 这样的底层管线节点？**
  → 由此给出结论：**Cline 的扩展边界在哪里 —— 哪些硬编码在核心，哪些留给生态。**

#### 线 4 —— **焦点链与任务状态跨压缩存活**

> Auto Compact 文档特意提到它和 **Focus Chain** 协同工作：**"待办事项列表在摘要之间持续存在"**。

**必查**：
- **压缩的是"对话说了什么"**，但**"接下来要做什么"** 通过 **Focus Chain 的 todo list 单独维护**。
- → 这条线揭示 Cline 如何**把短期记忆（对话）和长期目标（任务列表）解耦**。
- → 这也解释了**为什么压缩后 Cline 能"精确地从停止的地方继续"** ——
  **它不依赖对话历史来记住进度**。
- **要产出**：两者的**状态归属对照表**（谁存在哪、谁能被压缩、谁不能）。

#### 线 5 —— **模型能力适配与降级策略**

**必查**：
- Auto Compact **本身就有"条件启用"设计**：**只对 Claude 4 系列、GPT-5、Gemini 2.5、Grok 4 生效**，
  **其他模型回退到规则截断**。→ 这套适配逻辑分布在 **`context-window-utils.ts`**。
- **更底层的 token 计数策略**：Cline **保守地使用 3 字符/token** 的比率来估算
  **`effectiveMaxInputTokens`**。
- ⚠️ **但它在本地模型场景下会出问题**：**Issue #7772** 显示 ——
  **`llama-server` 的上下文窗口无法被自动检测**，Cline **默认按 128K 处理**，
  导致 **131K 的模型触发阈值计算错误**。
- **要产出**：**不同 provider 之间的适配妥协清单**（谁被特殊对待、谁被降级、代价是什么）。

### 2.3 建议的切入路径

> 如果想延续 Auto Compact 的分析节奏：

1. **优先看 `ContextPipeline` 和 `Hook 系统`**
   - **`ContextPipeline`** 是 Auto Compact 的**"上游"** —— **理解它才能明白压缩发生在管线的哪一环**。
   - **`Hook 系统`** 是理解 Cline **扩展哲学**的关键 —— **哪些机制被设计为可替换、可干预**。
2. **检查点系统** 可作为**"状态管理"这条支线单独看** ——
   它和 Auto Compact **共享「非破坏性编辑」的底层抽象**。

### 2.4 报告要求（HTML，自包含）

- **每个机制一节**，每节包含：**① 它解决什么问题 ② 怎么实现（贴原文）③ 数据流图 ④ 代价与边界 ⑤ 我的判断**。
- **必须有一张总图**：**上下文生命周期全景**（从 user input → prepareTurn → 模型 → tool → 检查点 → compaction），
  标出 **5 条线各自的位置**。
- ⚠️ **要写"设计取舍"**，不要写成代码注释的复述。
- 🚫 **不要贴大段源码**（贴关键 5–15 行即可），**其余给路径+行号**。

### 2.5 H-B 交付物
1. `harness/cline_SOURCE_ANALYSIS.html`（自包含，含上述总图与 5 条线）
2. 后续 harness（opencode / deepseek harness 等）**同格式**各一份
3. `MEMORY_HARNESS.md` 记录进度与关键证据路径

> **顺序**：**先把 cline 做完、交付 HTML，再开下一个 harness** —— 不要并行开多个半成品。

---

---

## §运维指令·昨夜汇报HTML（2026-10-07 · 2026-10-07 唤醒136 归档自 BAIZE_HARNESS_TASK.md · 已执行完毕）

### 🆕 运维指令 · 2026-10-07（📊 **交付：昨夜工作汇报 HTML**）· 高优先 · **用户直令** · 非实验

> **用户令（2026-10-07）**：「关于**昨夜（10/6 22:00 – 10/7 08:00）**的工作，**pretrain / vision / data / harness 各自写一个 html 报告**」。
> ⇒ **本项 = 本轮唤醒第一件事**；🚫 不跑新实验、🚫 **不打断正在跑的评测 / relay / loop**（只「读日志 + 写报告」）。

**① 产出（1 份）**：`doc/BaiZe-ISEDA2027/report_10_07_harness_overnight.html`
　**自包含**：单文件 / 内联 CSS / **零外部依赖**（无 CDN、**无任何被引用的 `http(s)://` 资源**）；**HTML 本体 ≤200KB**（图片文件另计）；字体栈沿用 `report_10_06.html`。
　🖼️ **允许「HTML + 同目录图片」**（见 ⑥）：数据图优先**内联 SVG**；确需位图 / 文生图 ⇒ 在 HTML 旁建 `report_10_07_harness_overnight_assets/`，用**相对路径**引用、**离线必须可开**；位图**一律 JPEG `.jpg`、长边 ≤1280px**（见 ⑥）。
　（四线并列放 `doc/BaiZe-ISEDA2027/` 便于并排打开；如你想同时在 `run/harness/` 留一份副本亦可。）

**② 窗口 = `2026-10-06 22:00 → 2026-10-07 08:00`（本地时区）**
- **严格按窗口取数**（昨夜这 10h）；窗口外的内容若要提及，**必须标「窗口外·背景」**。
- ⚠️ **若你写报告时还没到 08:00** ⇒ 写到当下即可，并在 HERO 标 **`数据截止 hh:mm`**（**不要为凑整点而干等**）。
- 先自己把窗口内提交拉出来（本线 commit message 都带前缀，可直接 grep）：
```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
git log --since=2026-10-06T22:00:00 --until=2026-10-07T08:00:00 \
  --date=format:'%m-%d %H:%M' --pretty=format:'%h %ad %s' | grep -i 'harness'
```

**③ 章节（顺序固定 —— 四线统一，便于并排对照）**
1. **HERO**：`BaiZe harness 线 · 昨夜工作汇报` + 窗口 + **数据截止时刻** + **一句话结论**
2. **TL;DR** ≤5 条
3. **KPI 表**：`指标 | 22:00 起点 | 08:00 现值 | Δ | 备注` ＋【**本窗口有无实质产出**：有 / 部分 / 无】+ 一句说明
4. **时间线**：`hh:mm — 动作 — ✅完成 / ⏸等待 / ❌失败`（取日志 / 心跳 / `MEMORY_HARNESS.md`）
5. **证据**：原始命令 + 输出片段（`<pre>`）；**失败与异常必须贴**（异常才是运维要看的）
6. **卡点 / 未完成**：如实写「卡点 + 需要什么」；🚫 不许凑数
7. **今晨现状**：进程 / 产物 一览 ＋ 下一轮计划
8. **窗口内 commit 列表**（② 命令的输出）

**④ 硬约束**
- **只写事实、数字必须真**；拿不到的写「无数据」。🚫 **禁止编造 / 用估算冒充实测** —— 运维会逐条对账。
- **「等待 / 空转」的时段必须显式标出**（`⏸ 等待中（原因）`）；🚫 **不许拿窗口外更早的成果充数**。
- **自检**：① **外链资源检查** ⇒ `grep -nE '<(img|script|link|iframe)[^>]*(src|href)="https?://|url\(https?://' <报告>` 与 `grep -n '@import' <报告>` **必须都为空**（**正文字里出现 URL 不算违规**，被引用的外部资源才算）；② HTML 本体 `wc -c` ≤200KB（图片文件另计）；③ **图片自检（若配图）**：`identify report_10_07_harness_overnight_assets/fig*.jpg` ⇒ **长边 ≤1280 且全为 JPEG**；`ls report_10_07_harness_overnight_assets/*.png` ⇒ **必须为空**（不留 PNG 原件）；单图 ≤400KB、总量 ≤4MB。

**⑤ 收尾**：按「收尾铁律」commit + push（前缀 `harness 汇报: …`），并在 `MEMORY_HARNESS.md` 记 1 行指针。
> 📦 **体积提醒**：插块后本任务书 ≈**36.7KB（已超 32KB）** ⇒ 按「体积维护规程」**先自己滚动归档到 ≤32KB 再提交**（只搬迁已闭合块、留 1 行指针）；**确切字节以你自己 `wc -c` 实测为准**。

**⑥ 附图（🖼️ **按需** —— 用户 2026-10-07 追加令：你的 MCP 工具包里有**文生图**工具）**

> **用不用由你判断 —— 不强制**（别为配图本末倒置）；**图只为「让人一眼看懂」，不为好看**。没有值得配的图就老实写「本窗口无适合配图」。

- ✅ **适合配**：架构 / 数据流图 · **codex `--resume` 每轮 R118→R134 的推进时间线** · **SWE-bench 评测流水线**（inference → patch → apply → test → resolved）· relay / loop 巡检链路示意 · 横评矩阵的组织方式。
- 🚫 **三条铁律（违反比不配更糟）**：
  1. **图只是辅助** —— **所有关键结论必须由表格 / 文字 / 原始输出（`<pre>`）承载**；正文引用的数字 🚫 **不得只存在于图里**（pbf `43/96/161`、resolved `52→61` 一律要文字/表里有）。
  2. 🚫 **严禁用文生图「编」数据图** —— 曲线 / 柱状 / 数值分布**必须由真实实测数据**生成（内联 SVG 或 matplotlib）；文生图**只能画示意图**，caption 必须标 **【示意图·文生图】**，实测图标 **【实测数据】**。
  3. **图片必须落本地文件并 commit** —— 工具若只返回 URL ⇒ **先 `curl -o` 下载到本地再引用**；HTML 里 🚫 **禁止出现被引用的 `http(s)://`**（离线必须能打开）。
- 📁 **位置 / 格式 / 体积（2026-10-07 追加令②：限分辨率 + 一律 JPEG）**：目录 `doc/BaiZe-ISEDA2027/report_10_07_harness_overnight_assets/`，文件名 `fig1_<主题>.jpg`。
  - 📐 **分辨率：长边 ≤1280px**（推荐 1024×768 / 1280×720）—— **生成时取最小可用档，🚫 禁 1920 / 2560 档**。
  - 🖼️ **格式：JPEG `.jpg` —— 🚫 禁 PNG**（质量 q≈85；线条 / 文字示意图 JPEG 会有轻微噪点，故取 85 而非 70 ⇒ **数据图仍首选内联 SVG**，最锐利且零体积）。
  - 📦 **单图 ≤400KB、总量 ≤4MB**（HTML 本体 ≤200KB 另计）。
  - 🔧 **落盘两步（生成 ⇒ 必须本地缩放转码，不许直接引用原图）**：`magick raw.png -resize '1280x1280>' -strip -quality 85 fig1_主题.jpg`（ImageMagick）；或无 ImageMagick ⇒ `ffmpeg -y -i raw.png -vf "scale='min(1280,iw)':-1" -q:v 3 -map_metadata -1 fig1_主题.jpg`；或 PIL ⇒ `im.thumbnail((1280,1280))` 后 `im.convert('RGB').save('fig1.jpg','JPEG',quality=85,optimize=True)`。
  - ✅ **自检**：`identify fig*.jpg`（无 identify 用 `file`）⇒ **长边 ≤1280 且全为 JPEG**；`ls report_10_07_harness_overnight_assets/*.png` ⇒ **必须为空**（不留 PNG 原件）；HTML 内按 `fig1/fig2/...` 编号引用，**每图配 1 行 caption**。

**⑦ 本线窗口内重点（自己核对；**没有就写「无」**，不许编）**
- ① **codex `--resume` 长跑**：`R118 ~137min` → `R134 ~693min` 的逐轮推进；**pbf 通过数** `43/96/161`（含中间变化）—— 昨夜推进了几轮、每轮各 +几 pbf。
- ② **`SWEBENCH_COMPARE.html`** 重生成：**resolved `52 → 61`**；HTML 体积变化（如 `72943B`）。
- ③ **relay skip 计数**：`71st → 85th`（说明中继巡检正常）；有无异常。
- ④ **MEMORY 滚动归档**（如 `R113 → daily`）与体积是否守住 ≤32KB。
- ⑤ **全程未唤醒（❌/blocked）数变化**；有无需要运维介入的事（配额 / 环境 / 工具链）。


---

## 📦 已归档：运维指令 · 2026-10-05（🔄 横评换「冷门模型」+ 严格串行）— 2026-10-07 R139 归档

> 归档原因：已被 2026-10-07「30×5 横评」指令块取代。模型已切换至 `kimi-k2.6-cloud`，串行执行已在进行中，quota 纪律已并入新块。原文如下。

### 🆕 运维指令 · 2026-10-05（**🔄 横评换「冷门模型」+ 严格串行：绕开 quota 墙，并重跑那 21 条**）⭐ 高优先 · **已批准**

> **用户提议（2026-10-05）**：横评卡在 **quota（5h 滑动窗口 → 21 条里 17 条拿到空 patch）** → **统一换一把「冷门」key/模型（kimi / 豆包）**，并且**一条一条串行跑、不并行**。
> **运维实测（RUN_ID 71）**：`doc/keys.txt` 的 **8 个候选全部 `http=200` 且返回 `tool_calls`** ⇒ **tool-calling 都支持，技术上可行**。
> **运维判断**：那 ~15 天**主要是"等配额"不是"算"**（1500 次 × ~2–4 min ≈ 50–100 h 纯跑）⇒ **配额一让开，串行 ≈ 2–4 天**。

**① 模型选择（先定后测）**
- **首选 `kimi-k2.6-cloud`** @ `http://agi-gateway.cxmt.com/cloud/v1`（Kimi 系偏 agentic coding；用户点名）
- **命中 429 时自动回落**：`doubao-seed-2.0-pro-cloud` → `doubao-seed-2.0-mini-cloud` → `doubao-seed-2.0-lite-cloud`（均 `/cloud/v1`）
- 🚫 **不要再用 `deepseek-v4-flash`**（就是它撞的墙）；🚫 **不要用 `glm-5.2`**（**4 条 loop 自己都在用，会互相抢**）
- 🔒 **同一轮横评只允许一个模型**；**换模型 = 必须重跑**（含已评的 21 条）—— **表里不得混模型**

**② 执行协议（严格串行）**
- **并发 = 1**：任一刻只有 **1 个 instance × 1 个 harness** 在跑；**不并行、不批量并发**
- 每条跑完 → **立即固化**（落 json + 更新 HTML）→ 再起下一条
- 顺序建议：**按 harness 串行**（cline → codex → opencode → claude-code → deepseek）；**一个 harness 把 30 条跑完再换下一个** ⇒ 任一个 harness 的分数都来自「同一模型、同一时段」

**③ quota 纪律（关键，上次失真的根因）**
- 命中 **`429` / `本次Token额度已用完`** → **立即暂停、等到窗口重置再继续**（记录等待时长）；🚫 **不许发空请求硬刷**
- **空 patch / quota 失败必须单独计**，🚫 **不得计入 harness 的失败率**
- 报告给**三列**：`resolved` / `patch-but-failed` / `quota-blocked`

**④ 重跑范围**
- 换模型后 **把原 21 条用新模型重跑**（原 21 条是 `deepseek-v4-flash` 口径，不可混入）；
- **先跑这 21 条小批**验证「新模型可用 + 串行稳定 + quota 不再挡」→ 再决定是否 **300 × 5 全量**。

**⑤ 报告**
- 更新 `SWEBENCH_COMPARE.html`（**单模型 · 公平口径 · 含 `quota-blocked` 列**），写明**模型名 / 时间窗 / 并发=1**；
- 结论**跑完即固化**；**不许缩水**（batch-5 原令）。

**⑥ 约束**：`.29` 是 pretrain 训练机 → **重 I/O 避让训练**；不占 GPU；不改论文。

---

### 🆕 运维指令 · 2026-10-07（⏸ 300 全量先搁置 → **立即做「30 × 5 harness 横评」，先把 5 个 harness 对比结果拿到**）⭐ 最高优先 · **已批准** · 已归档 2026-10-07

> **用户直令（2026-10-07 原文口径）**：「**harness 拖了太久了，先做 30 横评，把 5 个 harness 对比的结果拿到。**」
> **本次任务一句话**（用户 2026-10-07 复述确认）：「找 SWE-bench 里 **30 个相同的任务**，**评测 5 个 harness**，**得到分数**，**列表对比**。」
> **运维判断（为什么读成「先停下 300」）**：横评口径是 **并发=1 严格串行**，而 **`codex ×300 --resume`（PID 2151526）正占着这唯一的串行槽**（已 14h+，尚有 **151 blocked**；按 ~30 条/10h 还须 **~50h**；其后还要 cline/opencode/claude-code/deepseek 各 ×300）⇒ **第一个「5 harness 对比」要等好几天**。用户要的是**先拿到「30 规模」的 5-way 对比**，再谈扩量。

**① 先腾出串行槽（本轮第一件事）**
- **停掉 `codex ×300` 的 `--resume`**：`kill` PID 2151526（或让它跑完当前 instance 后**不再取新 instance**）—— **二选一，把选择与理由写进心跳**。
- 🚫 **不要删** `run/harness/kimi_pilot_results.json`；**已得的 330 entries / codex×300 的 43 resolved 全部保留**（将来 `--resume` 可续）。
- ✅ 停下后确认串行槽空闲（无 `run_serial_kimi.py` 进程在跑）。

**② 把「同一 30 条」在 5 个 harness 上补齐（本次唯一 KPI）**
- **题集 = 固定的那 30 条**（**15 django + 15 sympy**，`instances/` 已备好的一批）；🚫 不许换题、不许增删。
- **模型 = 统一 `kimi-k2.6-cloud`**；**并发 = 1 严格串行**（沿用已批口径）；**quota 失败单列**、不计入失败率。
- **已有可复用**：`cline-patched ×30 ✅ 18/30 = 60.0%`、`codex ×30 ✅ 14/30 = 46.7%`（若二者与本题集**同批**则直接引用；**不同批则补跑**——同批与否要写清）。
- **待跑（按此顺序）**：`opencode ×30` → `claude-code ×30` → `deepseek-harness ×30`。
  - ⚠️ **5 个都要有分**：`deepseek-harness` 若工具链仍不通（`pnpm install` ECONNRESET / 镜像全 000）⇒ **本轮先把它修通**（node22+rust 已装、`build` 待 `pnpm`；**显式带 proxy + 用镜像**，🚫 勿动共享 `py310`）；**实在不通**才标「未参与」并回报，🚫 **不许因它卡住前两个**。

**③ 交付（本轮必须落地）**
- 刷新 `run/harness/SWEBENCH_COMPARE.html` ⇒ **只含「这 30 条 × 5 harness」的对比**（自包含、可复算）。
- **一张 5 行汇总表**：`harness | scored | resolved | patch-but-failed | quota-blocked | resolve rate`。
- **写清口径**：同 30 条 / 同模型 `kimi-k2.6-cloud` / 并发=1 / 时间窗 / 各 harness 版本。
- 结论**跑完即固化**；按「收尾铁律」commit + push。

**④ 300 全量**：**本轮不做** —— 等这 5-way 结果出来、用户/运维**再拍板**是否 `--resume` 续扩。

**判据**：`SWEBENCH_COMPARE.html` 出现 **5 行**对照表（**同一 30 条**），每行的 `scored / resolved / patch-but-failed / quota-blocked / rate` 均可由 `kimi_pilot_results.json` 复算；若 `deepseek-harness` 确不可用，**表内保留该行**并标注「工具链未通·未参与」+ 已尝试的取证。
**时间盒**：3 harness × 30 × ~8 min ≈ **~12h**（**先报你实测的 s/inst 估算**；若显著超 1 天须立即回报）。
**铁律**：同一轮**只用 kimi 一个模型**（换模型必须重跑）；不改选题；不缩水；不改论文；不占 GPU。

> 📦 **体积提醒**：本块加入后 `BAIZE_HARNESS_TASK.md` **≈34.1KB（>32KB）** ⇒ **你本轮收尾前先按「📉 体积维护规程」把已闭合旧块归档到 ≤32KB 再提交**（确切字节以你自己 `wc -c` 实测为准；**未到 40KB 红线**）。

---

### 🆕 运维指令 · 2026-10-05（晚 · ✅ 批准「扩 300」= **先扩 kimi**；+ 环境隔离纪律）· 高优先 · **已批准** · 已归档 2026-10-07

> **用户拍板（2026-10-05 晚）**：「harness 扩 300 的 quota 瓶颈 —— **按你的建议先扩 kimi**。」

**① 范围与口径（先扩 kimi）**
- 模型 = **`kimi-k2.6-cloud`**（已实测 **0 quota 阻塞**、cline-patched 30 条 **18 resolved = 60.0%**）；🚫 **不混模型**（`deepseek-v4-flash` 被 5h 窗口挡掉 17/22）。
- 规模 = **把「300 条」跑出来**（原提案 = 300 × 5 harness）。**先扩 kimi**：可先在已完成/在跑的 harness（cline-patched ✅ / codex 🔄）上把 **30 → 300**，再逐步换 harness；**同一 harness 内不得混模型**。
- **并发 = 1 严格串行**（保持现状）；一条跑完立即固化（json + HTML）。
- **quota 纪律不变**：命中 429/额度 → **暂停等窗口**（记录时长），🚫 不空刷；**空 patch / quota 失败单列**，不计入 harness 失败率。
- **报告三列**：`resolved / patch-but-failed / quota-blocked`；写清 **模型名 / 时间窗 / 并发=1**；最终刷新 `SWEBENCH_COMPARE.html`（自包含、可复算）。

**② 环境隔离纪律（治「同机争用」—— 用户裁定）**
- **训练/长跑 = 共享 `py310`**（不动）；**需要大量装包时另起独立 conda env**（别再把共享 env 装脏 —— P-9.8 armB 崩溃的元凶就是共享 `py310` 被 `pip install -e` 污染）。
- harness 反复跑 `pip install -e` 的 SWE-bench 工作区**尤其要隔离**（例：`conda create -n harness python=3.10`，或 `--target` / 容器内装），并**每轮复核 `easy-install.pth` / `.egg-link` 未被写回**。

**③ 边界**：不占 GPU；重 I/O 避让 `.29` 训练（GPU0–1 P-9.10 / GPU2–7 data 配比）；不改论文。

> ✅ 本块生效即视为已批准 —— 按上表执行，无需再等。

---

### 🆕 运维指令 · 2026-10-08（📄 **SWE-bench 横评分析报告 HTML**）· **用户直令：各线自己写报告** · 高优先

> **用户令**：「把任务下发给各 agent，由 agent 自己写报告，不要替代他们写。」
> ⚠️ 你的 7-way 横评全完成，`SWEBENCH_COMPARE.html` ✅ 已交付。但长期空转心跳不是正事。**用户点名要 agent 自己写报告**。
> **本报告要求比 `SWEBENCH_COMPARE.html` 更深一层分析** —— 不仅是结果表，还要有归因、模式分析、对 BaiZe 的启示。

**① 交付**：`report_harness_swebench_analysis.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 格式（沿用 house style）**
- **自包含**：内联 CSS + **数据图优先内联 SVG**；**零外链**；**HTML 本体 ≤200KB**。
- 位图一律 **JPEG、长边 ≤1280、q85**、单图 ≤400KB/总量 ≤4MB、**落本地并 commit**；🚫 严禁外链、🚫 严禁用文生图「编」数据图（曲线必须由**真实实测数据**生成）。
- **开头 1 行指向** `SWEBENCH_COMPARE.html`（结果表已有，不重复贴全文）。

**③ 建议 9 节**
1. **TL;DR**（3–5 条：cline-patched & Pi 并列第一 60.0% / 7-way 分辨率 40%–60% / kimi-k2.6-cloud 统一 backbone / 关键发现）；
2. **评测设计**：30 条 SWE-bench Lite × 7 harness / kimi-k2.6-cloud backbone / serial=1 / 统一口径；
3. **结果总表**（引用 `SWEBENCH_COMPARE.html`，不重复全文）；
4. ⭐ **失败模式分析**（核心）：按 repo / 任务类型 / 失败原因分类——是工具调用失败？理解错误？patch 不完整？**给出各 harness 的失败模式分布图（内联 SVG）**；
5. **成本分析**：每 harness 平均轮数 / token 消耗 / 墙钟 / 性价比排名；
6. **Harness 架构差异**：各 harness 的系统提示/工具调用方式/代码模型差异 → 与表现的相关性；
7. **对 BaiZe 的启示**：如果 BaiZe 2.2B 作为 backbone，需要哪些能力才能达到类似 60% resolve rate？—— 代码能力 / 工具调用 / 长上下文 / 领域知识；
8. **局限**：30 条子集 / 单 seed / kimi 非 BaiZe 模型 / 与官方 leaderboard 不可比；
9. **下一步建议**：扩到 100–300 条 / 换 BaiZe 模型重测 / 加入更多 harness。

**④ 纪律**
- **数字必须真**：每个数字可由 `kimi_pilot_results.json` / `SWEBENCH_COMPARE.html` 复算；
- **失败模式分析要有实际日志证据**，不要编造分类；
- **收尾按「收尾铁律」commit+push**（前缀 `harness 横评分析: …`）；
- 写完本报告后，若运维无新指令，**可自主做 harness 源码分析（H-B 方向）** —— 深入 cline / Pi / Hermes 的 SWE-bench 实现差异。

> 📦 本块加入后 TASK 约 30KB，仍 ≤32KB ✅。如需归档，只归档下方已闭合旧块。

---

### 🆕 运维指令 · 2026-10-07⑥（🔧 **30 条 SWE-bench 横评再加 2 个 harness ⇒ 7-way**：`Hermes Agent` ＋ `Pi`）· **用户直令** · 高优先

> **用户直令（2026-10-07 21:4x）**：「**harness 的 SWE-Bench（30）对比加两个 harness：Hermes Agent 和 pi。**」
> ⇒ 现有 5 个（cline-patched / codex / opencode / claude-code / deepseek-harness）＋ **新 2 个** = **7-way × 同一 30 条**。

**① 我已替你定位（🚫 但你要自己复核版本/commit 并贴来源 URL —— 「不许猜」）**

| harness | 是什么 | 入口 | 接自定义/兼容 endpoint | 非交互 |
|:--|:--|:--|:--|:--|
| **Hermes Agent** | **`NousResearch/hermes-agent`**（MIT，251.8k★，Python；含 `hermes_cli` / `providers` / `evals` / `docker`；文档 hermes-agent.nousresearch.com/docs） | `hermes`（`hermes setup` 向导） | ✅ **Providers / Environment Variables 可配**（含 OpenAI 兼容） | CLI/headless；**有 Docker 镜像** |
| **Pi** | **`pi.dev`**（GitHub **`fleetagent/pi`**，Earendil Inc.，MIT，Node/npm；**已发 Pi 1.0**；文档 pi.dev/docs/latest） | npm 装后 `pi` | ✅ **Add Custom Providers / Run Local Models / 兼容 endpoint** | ⭐ **自带 print mode**（脚本化一次性）+ **JSON event stream** + **RPC** + **TS SDK** |

**② 口径（与现有 5 个完全一致，不许破口径）**
- **同一批 30 条**（现有 pilot `instances/`，**不许换题**）；**同一模型 `kimi-k2.6-cloud`**；**并发 = 1 严格串行**；**quota 失败单列**（不计入失败率）。
- **评分同口径**：产出的 `model_patch` 走**同一个 `r1_eval.py`（unshare 沙箱）** + **同一 timeout**；报告三列 `resolved / patch-but-failed / quota-blocked`。

**③ 做法（每步都要贴证据）**
1. **写适配层**：照现有 `run_harness.py` 的 driver，为两个新 harness 各加一个 driver（启动 → 指向 `gw_proxy`@`.29` + 指定 model → **产出 `model_patch`** → 交 `r1_eval.py`）。⚠️ **非交互 flag 必须从官方文档核实并贴 URL**（**Pi 用 print mode**；**Hermes 用其 CLI/headless 方式**）。
2. **安装**：**显式带 proxy**；**用独立 env / `--target`**，🚫 **别动共享 `py310`**；node/rust 已装过，缺件按老规矩走镜像。
3. **先 smoke 1 条**（端到端：装 → 起 → 产 patch → 评分），**跑通再上 30 条**；smoke 不通就**如实报卡点（含报错原文）**。
4. 🚫 **不许打断**正在跑的 chain（`deepseek-harness×30`，PID 1292346）—— **新 harness 排在它之后**（若另起并行槽，**仍必须保持「同一 harness 内并发 = 1」**）。

**④ 交付**
- `run/harness/SWEBENCH_COMPARE.html` 扩到 **7 行**（每行 `scored / resolved / pbf / quota-blocked / rate`）；`kimi_pilot_results.json` 同步；**口径表**写清：同 30 条 / 同模型 / 并发=1 / 时间窗 / **各 harness 版本或 commit**。
- 收尾按「收尾铁律」commit+push（前缀 `harness R<n>: …`）。

**时间盒**：装机+打通 ≈ 数小时/个；30 条 × ~5–9 min ≈ **2.5–4.5 h/个** ⇒ **两个 ≈ 1 天（不含装机）**。**先报你的估算**。
> 📦 体积提醒：本块加入后 `BAIZE_HARNESS_TASK.md` ≈34KB ⇒ 收尾前先归档已闭合旧块（确切字节以你自己 `wc -c` 为准）。

---

### 🆕 运维指令 · 2026-10-08④（💬 **请提出你对自己下一步工作的建议与计划**）· 中优先【已归档 2026-10-08】

> **背景**：你的 7-way SWE-bench 横评（30×7）全完成，深度分析报告 + 3-way/7-way 对比 HTML 均已交付，无运行中的 chain。运维目前没有立刻派新活，但项目距 ISEDA 2027 投稿还有 ~4 个月，harness 线在 BaiZe backbone 接入评测（Stage ii 评测阶段，2027-01）之前有大量准备空间。
>
> **用户意图**：运维不是替你拍脑袋，而是想先听**你自己的判断**——你最清楚横评数据里还有什么值得挖、还有哪些评测框架的前置工作能提前做。

**请你回答以下问题，写进 `MEMORY_HARNESS.md` 的顶部进度快照下方（新增「运维问答」小节）**：

1. **横评数据的深度挖掘**：30×7 的横评数据（`kimi_pilot_results.json`, 210 entries）里，有没有**已交付报告还没覆盖但你觉得有价值的分析角度**？（例如：某些失败模式的根因深挖、harness 间 patch 重叠度分析、特定 repo / 任务类型的分层统计……）——如果有，给出分析思路 + 预期产出。

2. **BaiZe backbone 接入评测的前置准备**：运维计划在 BaiZe 训练完成后（Stage (ii) 评测阶段，2027-01）把 BaiZe 2.2B 作为 backbone 接入 harness 跑 EDA-Eval-PyAether（158 任务）。在你看来，**harness 侧**有哪些前置工作可以现在就做？（例如：OpenAI-compatible endpoint 的接入测试框架、评测自动化脚本（5-run + 重排 + mean±std）、配对检验脚本（McNemar / paired bootstrap）、harness 冻结配置的锁定与文档化、§7.0 诊断清单 D1–D6 的脚本准备……）——给出你的方案和优先级。

3. **评测规模扩展的建议**：当前 30 条 SWE-bench Lite 子集。是否建议扩到 100–300 条？如果扩，**先扩哪一类**（django? sympy? 其他?）？给出依据。另外，**EDA-Eval-PyAether（158 任务）的评测管线**是否可以提前搭建/测试（用现有 backbone 如 kimi 或 MiniCPM5-2B 先跑一遍管线）？

4. **多 backbone 对比的前置**：README §4 Stage (ii) 的评测目标是 backbone × harness 网格（DeepSeek-V4-Pro / MiniCPM5-2B / BaiZe-base/SFT/RL × pure/RAG/Sandbox/full）。**现在能否先用现有 backbone 跑这个网格的 pilot 版**（例如 20 任务子集），以验证管线 + 发现口径问题？——如果可以，给出执行方案；如果不行，说明缺什么。

5. **对论文的补充建议**：以你对横评数据的了解，论文中是否还有**该写但没写**的 harness 相关内容？harness 线的实验结果如何更好地服务 BaiZe 的叙事？

**格式要求**：
- 在 `MEMORY_HARNESS.md` 的进度快照下方，新增 `## 🗣️ 运维问答 · 2026-10-08④（下一步工作建议）` 小节，逐条回答。
- **不许猜**：凡提建议，附依据（实验编号 / 报告 / 数据文件路径）。
- 回答完毕后正常收尾（心跳 + commit + push + WAITING=1）。
- **你不需要实际执行任何评测**——本轮纯写作，不占 GPU、不跑 chain。

> 📦 本块加入后 TASK 仍应 ≤32KB；若超限，按规程归档下方已闭合块。

**执行结论**：Q1–Q4 已在 R184 回答（commit 27859f2e 2026-10-08 17:26），写进 MEMORY_HARNESS.md「运维问答」小节。Q5 未单独作答（已融入 Q1–Q4 建议）。

## 📦 归档：2026-10-08⑤ / ⑦（R2 口径披露与并发追认 + 7×100 起跑令）

> **归档时间 2026-10-09**（原块位于 `BAIZE_HARNESS_TASK.md` 运维指令区，已闭合；**原文照录**）。**执行结果**：⑤ → 7×100 全跑完（7 harness × 100 = 700 entries）；⑦ → 「口径与并发」节已写入 `MEMORY_HARNESS.md` ✅、`report_harness_interaction_traces.html` 已落 `doc/BaiZe-ISEDA2027/` 根目录 ✅、SWEBENCH_COMPARE 已加「复用/新跑」标记列 ✅、监控表（quota/timeout/workdir-blocked/no-patch）已生成 ✅。⚠️ 由此暴露的 `workdir git-checkout 冲突`（88 例 blocked）已在 R210+ 修复中，并成为 2026-10-09⑧ 的并发硬约束来源。

### 🆕 运维指令 · 2026-10-08⑤（**① 启动第二轮 7×100 横评 ② 深挖第一轮 7×30 的「交互轨迹」→ 列表对比各 harness 特点**）· **用户直令** · 最高优先

> **用户令（2026-10-08 晚）**：「**① 启动第二轮 7×100 横评；② 深入分析第一轮 7×30 横评的交互轨迹，列表对比各 harness 的特点。**」
> 现状（运维已核）：7-way × 30 全完成（cline-patched 60.0% · Pi 60.0% · Hermes 53.3% · opencode 50.0% · codex 46.7% · claude-code 43.3% · deepseek-harness 40.0%），**无运行中 chain**。数据 = `run/harness/kimi_pilot_results.json`（480 entries）。

**① 第二轮：7 harness × 100 条（同一固定题集）**
- **题集**：**固定 100 条 SWE-bench Lite**，**7 个 harness 全部跑同一份**（🚫 不许各自换题）。**选法先写进 MEMORY 再跑**，给**可复现的选取规则**（如按 `instance_id` 排序取前 100，或 django/sympy 各 N 条…），并**明确标注是否包含第一轮的 30 条**（**建议包含** ⇒ 两轮直接可比）。
- **口径必须与第一轮逐字一致**（否则两轮不可比）：同 backbone `kimi-k2.6-cloud`、**同并发设置**、同沙箱、同 `PreToolUse`/anti-cheat、同判据。**若为压缩 ETA 想改并发 ⇒ 先报方案，不得擅自改口径。**
- **7 harness**：`cline-patched` · `codex` · `opencode` · `claude-code` · `deepseek-harness` · `pi` · `hermes`。
- **⭐ 先报 ETA 再全速跑**：第一轮 210 run ≈ 34h 串行 ⇒ 700 run 同速 ≈ **4.5–5 天**。**第一个动作 = 用实测 s/inst 算总 ETA 并写进心跳**；然后 `--resume` 增量跑，**每完成一个 harness 即刷新 + commit**。
- **交付**：`SWEBENCH_COMPARE.html` → **7 行 × 100 条** + 汇总表（scored/resolved/pbf/quota-blocked/rate）+ 口径表。
- **铁律**：🚫 不删 `kimi_pilot_results.json`（保留第一轮 210 entries，可 `--resume`）；🚫 不打断正在跑的 chain。

**② 深挖第一轮「交互轨迹」+ 逐 harness 特点对比表（纯 CPU，本块先做）**
- **数据源**：`kimi_pilot_results.json` 的 `harness_result` 字段（已知含 `stdout_tail` / `eval` / `wall_s` / `returncode`）。**第一件事 = 盘点「轨迹还剩多少」**：逐字段列可用信息；**若完整逐轮交互（每轮 prompt/工具调用/输出）已被 `/dev/shm` 清掉 ⇒ 如实写「仅 `stdout_tail` 可用 / 需重跑才有完整轨迹」**（🚫 不得猜、不得编）。
- **产出 A**：**7 行 × N 列「harness 特点对比表」**（HTML，house style，内联 SVG，零外链，≤200KB）。列建议：**启动方式/入口 · 交互轮次与自主性 · 工具调用风格与频次 · 是否用执行反馈闭环 · 平均 `wall_s` · 典型失败模式 · patch 规模 · resolved 率**。**每格数字/结论须可由 JSON 或源码 `path:line` 复算**。
- **产出 B**：回答「**为何同 backbone 下差 20pp（40.0%–60.0%）？是 harness 架构差异，还是交互轨迹差异？**」——**证据化**归因，不许泛泛。
- **交付**：`report_harness_interaction_traces.html`（新）+ 刷新 `HARNESS_7WAY_COMPARISON.html` 相关节。

**顺序**：**② 先做**（纯 CPU/写作，不占串行槽）→ **① 同步报 ETA 并起跑**（后台 `--resume` 增量）。
**收尾**：按「收尾铁律」commit+push（前缀 `harness R<N>: …`）+ 心跳 + WAITING=1。🚫 不 `git add -A`。
> 📦 体积提醒：本块加入后请先 `wc -c` 自检，>32KB 先归档已闭合旧块再提交。

### 🆕 运维指令 · 2026-10-08⑦（📋 **R2 口径披露 ＋ 并发变更追认 ＋ 报告落位**）· 高优先

> **已收到 R187**（`f85f6332`）：② 轨迹报告 ✅ 交付（38307B / 7 节 / 5 SVG；**诚实声明 per-turn 轨迹仅 `stdout_tail` 存活、完整轨迹需重跑** —— 这点做得对）· ① Round-2 已起跑（100 = **30 R1 + 70 stratified**，**含首轮 30** ⇒ 可比 ✅）· ④ 已归档。

**⚠️ 一处程序偏差（予以追认，但必须留痕）**：⑤ 写明「**若为压缩 ETA 想改并发 ⇒ 先报方案，不得擅自改口径**」，而你在**未先报方案**的情况下把 7 个 harness 改成**全并行**（serial=1 → 7 路并发），ETA 从 ~110h 压到 ~10h。
- ✅ **决定：追认**（11× 收益太大；7 个 harness 处于**同一并发条件**，轮内公平性不破）。
- ❗**但由此产生两条「口径事实」，必须写进最终报告**：
  1. **跨轮不可严格比**：首轮 = **serial=1**、本轮 = **7 路并行** ⇒ 网关限流 / 超时 / 沙箱争用条件不同；且**本轮 30 条 R1 实例是 `--resume` 复用的首轮（串行）结果**，**70 条新题才是本轮并行结果** ⇒ **同一张 7×100 表里混了两种运行条件** —— **必须在表头/脚注标明「哪 30 行是复用、哪 70 行是新跑」**。
  2. **必须监控并报告**：本轮 **`quota-blocked` / `timeout` / `no-patch` 率** vs 首轮**同 30 条** —— **若显著上升 ⇒ 判「并行污染」，相应结论要打折**。

**你要做的（本轮内完成，不必停链）**
1. 在 `MEMORY_HARNESS.md` ＋ 最终报告**显式新增一节「口径与并发」**（串行 vs 并行 · 30 条复用 · 上述监控指标对比）——**不许只在对话里说**。
2. **把 `report_harness_interaction_traces.html` 补一份到 `doc/BaiZe-ISEDA2027/` 根目录**（与其它线报告一致；你现有那份只在 `run/harness/`）。
3. 每完成一个 harness 即刷新 `SWEBENCH_COMPARE.html`（照旧），并**在表里加「复用 / 新跑」标记列**。

**纪律不变**：模型 `kimi-k2.6-cloud` · 同沙箱 · 同 `PreToolUse`/anti-cheat · 同判据；🚫 不删 `kimi_pilot_results.json`；🚫 不 `git add -A`；收尾 commit+push（前缀 `harness R<N>: …`）。
> 📦 体积：加块后自检 `wc -c`，>32KB 先归档已闭合旧块。
