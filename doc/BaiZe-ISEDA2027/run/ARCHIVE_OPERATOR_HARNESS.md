# ARCHIVE — 历史运维指令（源自 BAIZE_HARNESS_TASK.md）

> 运维 2026-10-05「任务书瘦身」时移出（**原文未改**，不改任何结论）。仅当需要查历史指令细节时再读。
## 归档 2026-10-25（由 BAIZE_HARNESS_TASK.md 搬入，原文未改）

### 📥 运维指令 · 2026-10-17（🧪 Terminal-Bench 2.0 · 7 harness × 89 task · kimi-k2.6-cloud）（已闭合，原文照搬）


> **用户令（2026-10-17）**：「harness：测完 glm53 7×300之后，开始基于kimi-k2.6做terminalbench的7 harness横评。」

**⓪ 执行顺序（硬约束）**
- **T0（先做，不得跳过）**：pi 剩余 **32 条**跑完 → 出 **glm53 7×300 最终版报告**（全量 2100 配对 McNemar）→ push。
- **T1（收口前允许做）**：纯 CPU/IO 前置 —— Docker/uv/Harbor 安装、dataset 拉取、oracle 5×、7 个适配器骨架与单测。**零 API 调用**、不干扰 pi。
- **T2（glm53 定稿 push 后立即启动）**：Terminal-Bench 正式横评。
- 🚫 不得为赶 T2 而 kill / 降速正在跑的 pi。

**① 基准与版本（先定后测）**
- 基准 = **Terminal-Bench 2.0**（Harbor 框架；论文 arXiv:2601.11868 记 **89 tasks**；数据集 **`terminal-bench@2.0`**）。
- 安装：`uv tool install harbor`（或 `pip install harbor`），**独立 uv/conda 环境**，🚫 不污染共享 `py310`。
- **Oracle 必须 5/5**：`uv run harbor run -d terminal-bench@2.0 --agent oracle -k 5 --n-concurrent 4`。oracle 不过 ⇒ 先修环境（Docker/镜像/网络），**环境失败不得算到 harness 头上**。
- 报告首段必须写明：`harbor --version`、`uv --version`、dataset 实际解析版本/commit、`docker version`、镜像 digest/拉取源；若实际任务数 ≠89，以实际为准并声明。

**② 7 harness（与 7×300 同一套，不得替换/合并）**
`cline-patched` / `codex` / `hermes` / `opencode` / `claude-code` / `deepseek-harness` / `pi`
- 每 harness 一个 **Harbor 自定义 agent**（`BaseAgent` / `BaseInstalledAgent` 子类，放 `run/harness/terminalbench/agents/<name>.py`），**保留原生工具循环**（读/写/执行/多轮修复）。
- 🚫 禁止「一个通用 shell agent 冒充 7 个」；🚫 禁止只换 system prompt 当不同 harness。
- 适配器验收：单任务上产出 **≥1 条工具调用轨迹 + 非空提交**，trace 落 `run/harness/terminalbench/traces/`。

**③ 模型与配额（逐字遵守）**
- backbone = **`kimi-k2.6-cloud`**，Base URL = **`http://agi-gateway.cxmt.com/cloud/v1`**，key 取 `doc/keys.txt` 同名项（与旧 7×300 完全一致；**报告/任务书不得明文打印 key**）。
- **同一 harness 全程只用一个模型**；换模型整臂重跑，禁止混算。
- 429/额度墙：**暂停等窗口**并记录等待秒数，不硬刷；`quota-blocked` 单列，**不计入 harness 失败**。
- 并发：每 harness 内 **并发 = 1**；7 路并行以「不触发 429」为限，触发即降到 2–3 路；所有结果带时间戳。

**④ 规模与判据（预注册，先写后跑）**
- 全量 = **7 × 89 = 623** 次（每任务每 harness 1 次，主口径 pass@1）。
- 先跑 **7 × 5 分层 pilot**（覆盖不同任务族）只用于验收 pipeline，**不得替代全量**。
- 主指标 **task resolution rate**；副指标 **timeout 率 / 无提交率 / 平均步数 / token 或 cost（若 Harbor 提供）**。
- 统计：**Wilson 95% CI**；7×7 **McNemar 精确检验**（同一批任务配对，报 b/c/p，不做挑选性比较）；给「最小可检测差值」说明。
- 三列口径 `resolved / failed / infra-or-quota`；某 harness infra 失败率 **>30% ⇒ 先停跑排障**，不得带病继续。

**⑤ 交付物**
1. `run/harness/terminalbench/`：7 适配器 + 启动脚本 + README（安装/复现命令/版本）+ mock 单测。
2. `run/harness/terminalbench_kimi_k2.6_results.json`（逐任务逐 harness：结果、耗时、token、失败类别、trace 路径）。
3. `reports/report_harness_terminalbench_7way_zh.html`：中文自包含；TL;DR / 总表（rate + CI）/ 逐任务热力表 / McNemar 矩阵 / 失败归因（环境 vs 能力 vs 适配器）/ 与 SWE-bench 7×300 结论对照 / **诚实条款**（内部口径、非官方榜、模型别名未经官方核验、dataset tag 会滚动）。
4. `MEMORY_HARNESS.md` 状态头 + 心跳。

**⑥ 纪律**
- 🚫 不占 GPU；与 `.12` 80B decay / vision **错峰 IO**（`nice -n 19`；禁止大目录全树遍历）。
- Docker 前置：`docker info` + `docker run --rm hello-world` + **实拉 1 个 TB 任务镜像**；内网阻断 ⇒ 立即在 MEMORY 记 **blocker + 完整报错 + 已试命令 + 替代方案**，**不许伪造结果、不许空跑**。
- commit 前缀 **`harness tb:`**；任务书/MEMORY ≤32KB 自滚归档；每个数字可溯源到 `文件:行` 或原始日志。
- 里程碑建议：T1 ≤2 次唤醒；pilot ≤24h；全量 ETA **3–5 天**（89×7，单任务 5–15min 量级，受配额/镜像拉取影响，报告须给实测 ETA）。



---


### 📥 运维指令 · 2026-10-24 16:3x（**TB 7 并发跑着的同时，后台下载 SWE-bench Verified 容器**）· 用户直令 · 最高优先

> 用户原话：「harness：启动 Terminal Bench 7 并发评测后，**开始下载 SWE-bench Verified 的容器**吧，以后把 SWE-bench 也刷一遍（**不是 Lite 而是更常用的 Verified**）」

**① 目标**
- 数据集：**SWE-bench Verified**（官方 500 题；`princeton-nlp/SWE-bench_Verified`）
- **🚫 不是 Lite**（之前跑的是 Lite 300，Verified 才是主流引用口径）
- 用途：TB 这轮跑完后，**7 harness × 500 题**刷一遍

**② 执行方式：后台并行，不阻塞 TB**
1. **TB 7×87 正在跑，优先级最高** —— 下载**必须限速**（参考 data 线的 `rsync --bwlimit` 做法），不能抢 TB 的 Docker 拉取带宽。
2. 下载走 **92.25 代理直连**（已验证可用；Docker Hub pull 已通过 dockerd 代理配通）。
3. **关键：先做去重体积估算**（2026-10-03 的老教训）：查 500 条对应镜像的 manifest → 报 **sum(size)** 与 **按 layer digest 去重后的实际下载量**；**500 张 ≠ 500 倍体积**。
4. **查磁盘**：`docker info | grep 'Docker Root Dir'` + `df -h`。若空间不足，**先报，别拉一半撑爆**。

**③ 下载策略**：**分批**（每批 50）+ **断点续跑**（`docker pull` 幂等，失败重试 2 次）+ 进度文件 `harness/swebench_verified_pull_progress.txt`；先拉基础层共享度高的（python/ubuntu 系列）。

**④ 交付**：体积估算小结 / 下载脚本 / MEMORY 记录启动时间与 ETA。

**⑤ 纪律**：🚫 不许影响 TB 7×87 进度；🚫 不 kill TB 的 7 个 harbor 进程；每轮唤醒并列报两条线进度；磁盘/带宽不足要明说并给替代方案。

---



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


## 📦 归档：2026-10-09⑧（7×100 HTML 报告 + 启动 7×300 + 三条硬约束）— 2026-10-11 R303 归档自 BAIZE_HARNESS_TASK.md

### 🆕 运维指令 · 2026-10-09⑧（① **7×100 HTML 报告** ② **启动 7×300 —— 并发已批准，附三条硬约束**）· **用户直令** · 最高优先

> **用户原话**：「**1. 给这次 7x100 的实验写个 html 报告 2. 开始 7x300，按照经验，可以并发。**」

**① 7×100 报告（新交付物）**
- 文件 `doc/BaiZe-ISEDA2027/report_harness_7x100.html`（house style：自包含 / 内联 SVG / 零外链 / ≤200KB）。
- 必备节：**HERO** 一句话结论 · **实验设置**（7 harness 版本 / 沙箱 / 判据 / 超时 / 题集规则 = `instance_selection_100.json` 的 `selection_rule` 原文）· **⚠️ 口径与并发**（serial(R1) vs 7 路并行(R2)；30 条 `--resume` 复用 vs 70 条新跑，**每行标 `R1复用`/`R2新跑`**）· **主结果表** 7×(done/resolved/pbf/blocked/scored/rate)+汇总（当前 **236 / 439 / 25**）· **每 repo × 7 harness 细分** · **blocked 专节**（25 例**逐条**根因 + 修复过程，**不许吞**）· **eval 环境限制专节**（非 django/sympy repo 的 `patch_applied=False` ⇒ 那些 0 分**不代表 harness 能力**）· 失败模式 · wall-time vs rate · 结论与局限。
- **每格数字须可复算**（给 JSON 字段口径或 `path:line`）；报告放 `doc/BaiZe-ISEDA2027/` 根。

**② 7×300：题集与工作量**
- **题集 = SWE-bench Lite 全量 300 条**（= codex 300-set 的 12 repo 全集），**7 harness 同一份**；100-set ⊂ 300-set ⇒ **`--resume` 复用已有 700 条**。**codex 已有全部 300（0 新跑）**，其余 6 家各 200 新跑 = **1200 runs**。
- **先报 ETA 再全速**（照 ⑤ 规矩）。实测依据：100 条串行共 **112.8h**，per-harness avg wall 415–999s ⇒ 6×200 串行 ≈ 各 23–42h；**7 路并行 wall ≈ 42h（hermes 瓶颈）**；harness 内并发 N ⇒ **≈42/N h**。

**②-A 🚨 起跑前必须改代码（三条缺一不可 —— 88 例 blocked 的根因就是路径没带 harness 维度）**

根因在 `run/harness/run_serial_kimi.py:238-239`：
```
238  workdir = WORKDIRS / instance["repo"].replace("/", "_")     # ← 只按 repo，7 harness 共用
239  rootfs_path = ROOTFS_TEMPLATES.get(instance["repo"], ROOTFS_DIR / instance_id)  # ← 共用
```
1. **workdir 隔离（必做，1 行）** ⇒ `WORKDIRS / <harness> / repo.replace("/","_")`：根除「Your local changes would be overwritten by checkout」（当前 22/25 blocked）。
2. **rootfs 全局锁（必做）**：`setup_rootfs()` 与 `eval_instance()` 是**唯二**碰共享 template testbed 的地方（`git fetch` 抢 `shallow.lock`）⇒ 用 `flock /nas_train/app.e0031982/harness_work/rootfs.lock` **只包这两段**；**agent 运行段保持无锁并行** ⇒ 吞吐不掉。🚫 不建议「每 harness 拷一份 rootfs」（`cp -a` ×7 harness ×12 repo 可能几百 GB）。
3. **harness 内并发 >1 ⇒ workdir 必须细到 per-instance**（`WORKDIRS/<harness>/<instance_id>`），否则同 repo 并发仍撞。

**②-B 资源红线（`.29` 不是私有机器）**
- harness 在 **`.29`**（`MEMORY_HARNESS.md:136`「.29 是 pretrain R2 训练机」），**pretrain 现在有活在跑** ⇒ **先在 `run/GPU29_ALLOC.md` 申请区追加一行**（7×300 / 预计 wall / CPU·内存·磁盘·网络档），**先到先得、🚫 不抢占**；起跑前先 `uptime` + `nvidia-smi` 核训练负载。
- ⚠️ **`/dev/shm` 是 tmpfs（吃内存）**，而 `WORKDIRS` 就在里面；per-harness 隔离后克隆份数 ×7 ⇒ **起跑前 `df -h /dev/shm && free -g`，原文抄进心跳**；不够 ⇒ 降 N 或迁盘（NFS+git tmp_pack 老问题）。
- **并发分档、逐档验**：N=1（7 路并行）→ 跑 30 条确认 **block=0** → N=2 → N=3；**任一档 block>0 立即停档并报根因**，🚫 不许带 block 硬冲。

**②-C 成功判据（硬）**
- 收尾时 **`blocked` 必须 = 0**（`quota-blocked` 同算失败）；**>0 ⇒ 报告逐条列 `instance_id` + 根因原文**，🚫 不许「差不多」。
- 口径逐字不变（同 backbone `kimi-k2.6-cloud` / 同沙箱 / 同判据 / 同 `PreToolUse`）。🚫 不删 `kimi_pilot_results.json`（`--resume` 靠它）；每完成一个 harness 即刷新 + commit（前缀 `harness R<N>: …`）。

**③ 顺序**：**① 先交**（纯 CPU/写作，不占串行槽）→ **②-A 改码 + 30 条冒烟验 block=0 + 报 ETA** → ② 起跑。

> **归档结论（2026-10-11）**：① 7×100 HTML 报告已交付 ✅（`report_harness_7x100.html`）；② 7×300 已启动 ✅（workdir 隔离修复 done, block=0 已验证, 2047/2100 = 97.5%, 554 resolved, 5 harness COMPLETE, hermes+claude-code 仍在跑）；②-C 成功判据待 7×300 完成后检查 blocked=0。本块已归档，7×300 监控继续在 MEMORY_HARNESS.md 顶部进行。

---

## 📦 §运维指令·2026-10-11（①文献借鉴 ②交互轨迹对比以 cline 为轴）→ 自 TASK 归档

> 结论：`report_harness_lit_ideas.html`(26.9KB) + `report_harness_trace_vs_cline.html`(50.2KB) 均已交付 ✅（commit 前缀 `harness rpt:`）。

**用户原话**：①「harness 看看这几天 research 积累的论文，找可借鉴 idea，写个 html 报告（中文版）。」②「分析各 harness 的交互轨迹，写个细致的分析报告（中文版），对比不同 harness 的优劣。当前 EDA Agent 我们基于 cline 开发，这个报告需要从各自 harness 跟 cline 的对比出发，提出对 cline 的改进意见。」

**性质**：纯分析 + 写作（读已有轨迹/JSON/报告）⇒ 🚫 不占 GPU、🚫 不打断在飞的 7×300。

**① 交付物 A（文献）**：`doc/BaiZe-ISEDA2027/report_harness_lit_ideas.html`
**② 交付物 B（轨迹分析）**：`doc/BaiZe-ISEDA2027/report_harness_trace_vs_cline.html`
两份均 中文 · 自包含单文件 · 内联 CSS/SVG · 零外链 · ≤200KB。

**交付物 A · 文献借鉴报告**：
- 输入（先 git pull）：research 线仓根相对 `doc/personal-watch/run/research/daily/2026-10-07.html` … `2026-10-11.html`（共 25 篇）+ `TOP_K.md`/`TOP_K.jsonl` + `papers.jsonl` + `TAKEAWAYS.md`。
- 关注面：code agent · harness 架构 · 交互轨迹与上下文压缩 · 工具调用与沙箱 · agent RL · SWE-bench 类评测协议 · 成本-性能。
- 每条 idea 必带：出处 + 一句话 + 与本线关系 + 借鉴成本 + 风险 + 价签；按可执行价值排序 TOP-5；区分「已验证」vs「仅灵感」。

**交付物 B · 交互轨迹对比分析（本批重点 · 必须更细）**：
- 定位：旧 `run/harness/report_harness_interaction_traces.html`（2026-10-08）已存在 ⇒ 必须更细，且以「各 harness vs cline」为轴，不得翻版。
- 数据源：`run/harness/kimi_pilot_results.json`（含 stdout_tail/model_patch/traces）· `logs_7x300/` · `SWEBENCH_COMPARE.html` · `HARNESS_7WAY_COMPARISON.html` · `analyze_traces.py`/`gen_trace_report*.py`。
- 必备 8 节：①HERO 一句话+TL;DR ②方法与口径（7 harness 版本/同 backbone/题集/判据/R1-R2 并发不可比性/轨迹缺失如实报）③逐 harness 剖析 7 段（工具集/循环控制/上下文管理压缩/计划 todo/patch 自检/失败恢复/何时停手/步数 wall-time，每段引 trace 证据）④跨 harness 对比矩阵（维度×7+cline 列）⑤各 harness 优劣 ⑥★cline 对比与改进 TOP-8（功能点+证据+预期收益+实现示意+优先级，区分已在 cline-patched 验过 vs 未验证）⑦证据索引（path:line/JSON 字段）⑧诚实条款。

**纪律**：🚫 不改 7×300 在飞任务/数值；已在 `CLINE_IMPROVEMENT_OPPORTUNITIES.md` + `CLINE_IMPROVEMENTS_TOP5.html` 提过的结论须沿用并标「已提过」；commit 前缀 `harness rpt:`；任务书 >32KB 自滚归档。


---

### 🆕 运维指令 · 2026-10-12（🔬 eval 基础设施失效 / module 安装失败 根因深挖 + 「分数偏低」外部对照复核）· 用户直令 · **最高优先**

> **用户原话（2026-10-12）**：「harness 7×300 是否有很多 module 无法安装的问题导致失败，这些问题能否解决？现在的分数显然比预期低很多，你可以 web search。」
> **性质**：**纯分析 + 归因 + 可解决性判断**（读现有 `kimi_pilot_results.json` / 日志 / `r1_eval.py` 等脚本 + 按需 web search）⇒ 🚫 **不占 GPU**；**凡需要重跑评测（改 patch 容错 / 环境装配等）的，先报「做法 / 成本 / ETA / 占用」再动（先报后跑）**。

**① 必须逐条回答（每条给证据，不得含糊）**：

1. **module / 环境安装失败到底占多少** —— 从 `kimi_pilot_results.json`（2100 entries）的 `eval` / `stdout_tail` / `classification` 字段**统计**：有多少失败的根因是「`ModuleNotFoundError` / `ImportError` / `No module named …` / pip/conda 依赖缺失 / 环境装配失败」，而非「模型改错」。给 **per-harness × per-failure-class 矩阵 + 占比**。
   ⚠️ **务必区分**：**【真·环境失败】** vs **【`pbf` = patch 应用成功但 FAIL_TO_PASS 未过（wrong-fix）】**—— 两者常被混谈（现有 `report_harness_swebench_analysis.html` 称 83% 失败是 wrong-fix，请复核是否与原始字段对得上）。
2. **根因定位** —— 我们 `r1_eval.py` 用 **unshare 沙箱（非 Docker）**；SWE-bench 官方是**每实例 conda env / repo 专属依赖 / 预构建镜像**。请确认：我们**有没有为每个 instance 装配其仓库依赖**，还是**共用一份 env**？（列 `r1_eval.py` / `run_harness.py` / `run_serial_kimi.py` 相关 `path:line` 为证。）并复核 `run/report_harness_7x300.html §8「eval 基础设施失效归因」`里「5 个 repo 因 eval …」的原始统计（是否实质 = 缺依赖/环境装配失败）。
3. **可解决性判断**（每项：做法 / 成本 / **预计能挽回多少 resolved** / 风险 / 依据），至少覆盖：
   - ① **per-instance 依赖装配**（照官方 `specs/` + `environment.yml`/conda，或改预构建 Docker 镜像）；
   - ② **patch 三级容错**（官方 `git apply` → `git apply --reject` → `patch --fuzz=5`；我们现仅单级 `git apply`，见 `SWEBENCH_OFFICIAL_CRITERIA_VERIFICATION.md §4`）—— 这条属**低成本高回报**，请明确估算「能救回多少题」；
   - ③ 超时 / 网络（`git_fetch 503`）/ quota 等 infra 失败。
4. **分数是否「比预期低很多」—— 外部对照（web search）** —— 查 SWE-bench / SWE-bench Lite（及 Verified）上**同类路线**的公开分数：agent harness + 强 backbone（如 SWE-agent / OpenHands / Aider / codex-cli / claude-code 等）的 pass@1，以及 **kimi-k2 系列**的公开 SWE-bench 数。明确回答：**cline 28.7% 是「我们口径/环境偏低」还是「与同类路线相当」**？给**对照表 + 来源 URL + 时效**；无法核实的显式标「未核实」。

**② 交付物**：`doc/BaiZe-ISEDA2027/report_harness_eval_rootcause.html`（**中文 · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB**），必备节：

1. **HERO 结论 + TL;DR**（一句话答「module/环境失败占比 = __%；可挽回约 __ 题；总分是否偏低」）。
2. **失败分类全景**（`resolved` / `pbf`-wrong-fix / **env-module-fail** / `blocked` / `quota` / `timeout`）per-harness 表 + 热力图。
3. **根因链路**（unshare 共享 env → 缺依赖 → 测试收集失败 → 被计入哪种失败类；附 `path:line`）。
4. **可解决项清单**（**P0 立即可做** vs **P1 需较大改造**），每项带成本 / 挽回估算 / 依据。
5. **分数外部对照**（我们 vs 同类，附来源 URL + 时效）。
6. **诚实条款**（300 题 / 单 backbone `kimi-k2.6-cloud` / eval 环境与官方差异 / web 时效）。

**③ 纪律**：🚫 **不改已发布的实验数值**（新统计只**只读** `kimi_pilot_results.json`；如需重跑一律走「先报后跑」）· web 论据带来源 + 时效 · commit 前缀 `harness rpt:` · 证据每格可复算（`path:line` 或 JSON 字段）· 任务书 >32KB **自滚归档**（本块加入后请自滚回 ≤32KB）。

---

### 🆕 运维指令 · 2026-10-12（🔬 cline vs opencode 谁更适合做 EDA agent harness 基座 · 深入对比 · 中文 HTML）· 用户直令 · 高优先

> **用户原话（2026-10-12）**：「关于 cline 和 opencode 哪个更适合做 EDA agent harness 的基座，半年前我们做了一些分析（`/nas_train/app.e0031982/code/super_intelligence_2035/doc/zhulong_doc/Cline vs OpenCode 对比.md`，NAS 上 harness 可直接读）。现在既然 harness 能看到两边的代码，请参考早前的分析，做更加深入的对比分析 html 报告（中文版），可以按需 web search。」—— 分析文件在 NAS 上，**只需给 file_path**。
> **性质**：**纯分析 + 写作**（读已有源码分析/轨迹/JSON + 按需 web search）⇒ 🚫 **不占 GPU、🚫 不打断在飞的 7×300 收尾**。

**① 交付物**：`doc/BaiZe-ISEDA2027/report_cline_vs_opencode_eda.html`（**中文 · 自包含单文件 · 内联 CSS/SVG · 零外链 · ≤200KB**）。

**② 输入（file_path，NAS 可直接读，勿把大文件整段读进上下文）**：
- 早前选型分析：`/nas_train/app.e0031982/code/super_intelligence_2035/doc/zhulong_doc/Cline vs OpenCode 对比.md`（2026-03-13，当年结论倾向 Cline CLI 2.0）
- 双方源码分析：`run/harness/cline_SOURCE_ANALYSIS.html` · `run/harness/opencode_SOURCE_ANALYSIS.html`
- 实测结果：`run/harness/kimi_pilot_results.json`（7×300，cline=86/300(28.7%) vs opencode=87/300(29.0%)）
- cline 改进/轨迹（结论须沿用并标「已提过」）：`report_harness_trace_vs_cline.html` · `run/harness/CLINE_IMPROVEMENT_OPPORTUNITIES.md` · `run/harness/CLINE_IMPROVEMENTS_TOP5.html`

**③ 必备节**：
1. **HERO 一句话结论 + TL;DR**。
2. **早前结论回顾**：2026-03 选型论据（Cline=逐操作审批/MCP 生态/Checkpoint/子Agent vs OpenCode=本地模型/多模态/MIT 宽松）与当年为何选 Cline。
3. **实测评比（核心增量）**：7×300 里 cline 86/300(28.7%) vs opencode 87/300(29.0%) **几乎打平（+0.3pp，无统计差别）**；从 `kimi_pilot_results.json` 抽**双方 wall-time / 步数 / token 量 / 失败分类(resolved·pbf·blocked·quota·np) / 同题重叠胜败**，逐项挂 JSON 字段证据。
4. **代码架构对比**：工具集 / 循环控制与停手 / 上下文管理与压缩 / 审批粒度(Human-in-the-loop) / MCP / checkpoint / patch 生成与自检 / 失败恢复 —— 结合两份 `*_SOURCE_ANALYSIS.html`。
5. **EDA 场景契合度**：不可逆操作安全(PDK 改参/仿真提交) / 变更管控 / MCP 封装 PyAether / 本地化离线部署 / 多模态扩展。
6. **半年来演进（web search 按需）**：两框架**最新版本/生态/维护活跃度/协议与安全变更**，标**检索时效**（距今 2026-03 的 delta）；🚫 无法核实的显式标「未核实」。
7. **综合结论**：谁更适合做 EDA agent harness 基座 + 理由（证据链或加权分）+ **风险 & 迁移成本** + 是否需「双轨并行」。
8. **诚实条款**：样本量(300 题/单 backbone kimi-k2.6-cloud)/eval 环境限制/web 时效对结论的约束。

**④ 纪律**：🚫 不改实验数值、不新跑评测 · **已在 `CLINE_IMPROVEMENT_OPPORTUNITIES.md` / `report_harness_trace_vs_cline.html` 提过的结论须沿用并标「已提过」**，本轮增量须显式列出 · web search 论据带来源+时效 · commit 前缀 `harness rpt:` · 证据索引每格可复算(path:line 或 JSON 字段) · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-12（🔧 **逐项修复 eval 基建缺陷 + 重跑受影响 case**）· 用户直令 · ⭐ 最高优先

> **用户原话（2026-10-12）**：「**harness 深挖后发现的各种导致分数偏低的问题可以解决吗？如果可以，让他一一解决，然后重跑这些 case。**」
> **运维答复**：**可以解决** —— 你自己的 `report_harness_eval_rootcause.html §4` 已给出 P0/P1 清单（含成本/预估挽回/风险）。⇒ **按本令执行：逐项修 → 重评/重跑 → 报前后对比**。

**① 逐项修复（先 P0，源自本线报告 §4.1）** —— 每项做完**就地验证**（用其对应失败实例，确认 env 装配 / `pip install -e .` / 测试收集 **当步通过**）：
1. **matplotlib**：pre-cache `freetype-2.6.1.tar.gz` 进 rootfs `build/`（或 manylinux wheel / 预编 `_c_internal_utils.so`）。（~2h）
2. **pytest**：修 rootfs conda env 版本冲突（`minversion requires pytest-2.0, actual pytest-0.1.dev1`）。（~1h）
3. **Unify：预置 pip wheels + 源码 tarball + build deps**（`PIP_NO_BUILD_ISOLATION=1`、预填 `~/.cache/pip`）—— **根修所有「外网下载」类失败**。（~4h）
4. **sphinx**：修 `base_commit` 不匹配（rootfs git 仓库 checkout 到正确 commit / 每实例 fresh clone）。（~2h）

**② 重跑口径（关键 · 先便宜后贵）**：
- **a) 优先「重评现存 patch」**（**不重跑 agent**）：凡当时**已产出 patch**、只是 env/测试没跑起来的（`env-or-patch-fail` 451 + sphinx patch-apply 92）⇒ **用修好的 rootfs 重跑 `r1_eval.py`**（同 4 级 patch 容错）。
- **b) 再「重跑 agent」**：仅对**当时没产出可用 patch** 的（`blocked`/`timeout`/`no-patch`；先做 P1 的「git fetch 重试 + 预克隆」修网络）才重跑 harness。
- **c) 范围**：**只重跑受影响的 case**（那 5 个 repo 的实例 + sphinx；**不要**全量 2100）；**保持原 7 harness + 同 backbone** 以保可比。**开工前在心跳写清：本次重跑 = 哪些 instance × 几个 harness × 预计条数/ETA**（先报后跑）。
- **d) 增量落盘 + 幂等可续**：新结果写**独立文件**（如 `harness/kimi_pilot_results.fix1.json`），🚫 **不覆盖** `kimi_pilot_results.json`；跑批幂等（已完成跳过）。

**③ 交付**：
- **追加/新出**：`report_harness_eval_rootcause.html` 加「**§7 修复与重跑结果：before/after per-repo resolved 表**」，或新出 `report_harness_eval_fix_rerun.html`（中文·自包含·零外链·≤200KB）。
- 报 **before/after**：resolved 数 · cline resolve rate（28.7% → ?）· eval-OK 口径 · 按 repo 的失败→通过翻转数；**与 §4 预估（P0 ~+22/harness）对照**。
- 留修复脚本 + 结果 JSON + 命令；`commit` 前缀 `harness fix:`。

**④ P1（需先报后跑）**：astropy（沙箱内存 / 预编译 wheel，~4h）· 网络 503 重试（~1h）· **per-instance 预构建 Docker（官方做法，~2-3 天、高风险）** —— **做前先在心跳报「做法 / 成本 / ETA / 占用」**，等运维确认再动。

**⑤ 纪律**：🚫 **不占 GPU** · 🚫 **不打扰 `.29` pretrain / 下载线的 I/O**（限流 `nice`）· 每项修复给**证据**（`test_output.txt` 前后 / rootfs 变化 / 命令）· **不改已发布数值**（新结果独立文件）· 任务书 >32KB 自滚归档。


---

## §运维指令·2026-10-13（🔬 通过率为何这么低）— 从 BAIZE_HARNESS_TASK.md 归档（2026-10-14）

### 🆕 运维指令 · 2026-10-13（🔬 通过率为何这么低 —— web 对照 + 轨迹细析 + 提升机会点按预计增益排序）· 用户直令 · 最高优先

> 用户令（2026-10-13）：「harness：首先 web search 后分析为什么通过率这么低；细致分析轨迹，回答通过率这么低是否合理、是否都是 LLM 能力不足所致，还是评测环境的问题？有哪些提升机会点？有哪些问题？如何解决，将建议按照预计提升从高到低排序。」
> 性质：读数据 + web（CPU，不占 GPU）；与 fix3 重评 / 下载错峰 IO，并行不冲突。

① 必答（逐条）：
1. web 外部对照：公开 SWE-bench(-Lite/Verified) 同类 agent 的 pass@1（Claude / Codex / kimi / Aider…）+ 官方 reference resolve rate → 明确答「cline 28.7%（eval-OK 口径 36.6%）是偏低 / 相当 / 被环境压制」，带来源 + 时效。
2. 是否合理 + 能力 vs 环境拆分：给量化拆分（agent 能力类失败 vs 评测环境/infra 类失败 ± 可挽回上限），引用已交付 `report_harness_eval_rootcause.html`（env 失败 21.5%、真 wrong-fix 48%、5 repo 系统性压制）。
3. 细致轨迹分析：从 `kimi_pilot_results.json`（2100）+ 交互轨迹（`stdout_tail`/trace）逐条解读代表案例（成功 / wrong-fix / blocked 各取样），给 文件:行 / 原文片段为证。
4. 提升机会点 + 问题 + 解法：按预计提升从高到低排序的表（每行：机会点 · 依据 · 做法 · 预计挽回 resolved 数或 pp · 成本 · ETA · 风险）。

② 交付：`doc/BaiZe-ISEDA2027/report_harness_why_low_passrate_zh.html`（中文 · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB）。节：TL;DR / 外部对照 / 能力 vs 环境拆解 / 代表轨迹逐条 / 排序后的提升机会点总表 / 结论与诚实条款。

③ 纪律：🚫 不占 GPU、不改已发布数值 · web 论据带来源 + 时效 · 结论须有证据（文件:行）· 与 fix3 并行不冲突 · commit 前缀 `harness rpt:` · 任务书 >32KB 自滚归档。

---

## §1.1-bis 无 Docker 路线 — 从 BAIZE_HARNESS_TASK.md 归档（2026-10-14，初始可行性核查阶段，已完成）

### 1.1-bis ⚠️ 无 Docker 路线（运维 2026-10-02 明确：公司内网无法 `docker pull`）

> 已查实的事实（官方仓库原文）：
> - SWE-bench 官方 harness 默认绑 Docker（README：「SWE-bench uses Docker for reproducible evaluations」；
>   2024-06-27 起改为「fully containerized evaluation harness using Docker」）。
> - 官方唯一的"无 Docker"本地后端是 Modal（云）：`--modal true` —— 但要外网。
> - `SWE-ReX`（SWE-agent 家族）支持 local / remote / Docker / Modal 等后端，
>   原文：「…executed locally or remotely in Docker containers, AWS remote machines, Modal, or something else…」+
>   「Support a broad range of platforms, including non-Linux machines without Docker」。
> - 🚫 `SWE-MiniSandbox` —— 在官方仓库中未找到该名称。请自行查证（有就给 URL + 它解决什么）；查不到就写"未找到"，不要猜。

> ### 🔑 关键认知：Docker 在这里不只是"隔离"，更是"per-instance 依赖环境的分发机制"
> 每个 instance 一个预构建镜像，装着该 repo 在该 `base_commit` 下正确的依赖。
> 换掉"隔离"很容易（bwrap / nsjail / local）；换掉"环境供应链"很难。

---

#### ⭐ 第 0 步（先做）：连通性测试 —— 分清「事实」与「推测」

> ### ⚠️ 运维更正（2026-10-02）：github 是可达的
> `.29` / `.12` 都能从 github `git clone` 代码 —— 本任务线用于发布任务的仓库本身就在 github 上，
> 所有 agent 的 `git fetch/pull/push` 一直正常。
> → 不要把"github 不可达"当作前提（那是把"爬取层面不可达"错当成了"git 不可达"）。
>
> ### 🔑 还必须分清另外两件被我混淆过的事
> | | 实际状态 | 依据 |
> |:--|:--|:--|
> | `docker` 命令可用吗 | ❌ 不可用（`docker info` → `NOT AVAILABLE`）| 实测（RUN_ID 5） |
> | 能不能 `docker pull` | ❓ 从未测过 | 此前只是推测，不要当事实 |
> → "没装 Docker" 与 "装了也 pull 不到镜像" 是两件完全不同的事，都要实测。

要测的清单（逐条记 `http_code` 或错误原文）

```bash
echo "=== A. GitHub（已知可达，复核 git 通道） ==="
timeout 20 git ls-remote https://github.com/SWE-bench/SWE-bench.git HEAD 2>&1 | head -2

echo "=== B. 依赖源（E′ 的关键待验项） ==="
for u in https://pypi.org/simple/ https://files.pythonhosted.org/ ; do
  printf '%-38s : ' "$u"; curl -sS -m 10 -o /dev/null -w '%{http_code}\n' "$u" 2>&1 | tail -1
done
# 内网镜像？（替换成你们实际的内网源）
pip config list 2>/dev/null; cat /etc/pip.conf ~/.pip/pip.conf ~/.config/pip/pip.conf 2>/dev/null

echo "=== C. Docker 相关（注意：docker 命令本身当前不可用） ==="
which docker dockerd podman nerdctl 2>/dev/null || echo "(no docker/podman CLI)"
curl -sS -m 10 -o /dev/null -w 'registry-1.docker.io : %{http_code}\n' https://registry-1.docker.io/v2/ 2>&1 | tail -1
curl -sS -m 10 -o /dev/null -w 'ghcr.io             : %{http_code}\n' https://ghcr.io/v2/ 2>&1 | tail -1

echo "=== D. SWE-bench 云（sb-cli 的命门） ==="
for u in https://api.swebench.com/ https://www.swebench.com/ ; do
  printf '%-38s : ' "$u"; curl -sS -m 10 -o /dev/null -w '%{http_code}\n' "$u" 2>&1 | tail -1
done
timeout 60 pip download sb-cli -d /tmp/sbcli_probe --no-deps 2>&1 | tail -3
```

判定（据此选路线）
| 测试结果 | 结论 |
|:--|:--|
| B（pypi/内网镜像）通 | ✅ E′ 完全可行 —— `git clone`（已成立）+ 装依赖 → 不需要 Docker |
| C 里能看到内网 registry 或 `docker pull` 成功 | ✅ 原路可行（最省事） |
| D 通（且合规批准） | ✅ sb-cli 可用 → 给最强 harness 拿标准分数 |
| B/C/D 全不通 | ⚠️ 才需要考虑自建沙箱 / 换口径 |

#### 🚫 关于 sb-cli 的合规红线（必须先确认，再上传任何东西）

`sb-cli` 的工作方式是 把 `predictions.json`（含 `model_patch`）上传到 SWE-bench 云端评测。
- ✅ 缓解：patch 针对的是开源 repo（django / sympy 等），不是我们的私有代码。
- ⚠️ 但：这是把代码片段发到外部服务 —— 公司政策可能不允许。
- → 要求：上传前必须由运维/合规确认。未经确认，不得使用 sb-cli 上传任何东西。
- 📌 另：sb-cli 需要邮箱 + 邮件验证码注册（`sb-cli gen-api-key <email>` → `verify-api-key <code>`），
  且有配额（`sb-cli quota <subset> <split>`）—— 这两条也要先记下来。

---

#### 路线优先级（连通性测试之后据此执行）

1. 若 `docker pull` 实测可行（或内网有 Harbor 镜像代理）→ 原路最省事（写清证据）。
2. ⭐ 路线 E′（推荐）：只挑 1–3 个高频 repo 的 instance
   - 统计 `SWE-bench Lite`(300) 的 repo 分布 → 挑占比最高的 1–3 个 repo。
   - `git clone` 该 repo @ `base_commit`（✅ github 已确认可达）+ 装该 repo 的依赖（待验 pypi/内网镜像）。
   - 几个 harness 跑同一批 instance → 公平横评成立。
   - ⚠️ 报告里必须标注：这是内部横评口径，不是标准 SWE-bench 分数，不能与 leaderboard 直接比。
   - 💡 加强版：`SWE-bench` 仓库里带着每个 instance 的镜像构建规格（`swebench/harness/`）——
     可直接照规格 build env，完全绕开 Docker Hub。
3. 路线 sn（若 D 通 且 合规批准）：`sb-cli` —— 给最强 harness 拿与 leaderboard 可比的标准分数。
4. 备选：自建轻量沙箱 —— `conda env per repo` + `bwrap` / `nsjail`（只替代"隔离"职责）。
5. 若以上都不可行 → 明确写"H-A 在受限前提下无法按标准口径进行"，
   并给替代评测口径建议，但不得把它称作 SWE-bench 结果。

---

## §P1 PLAN — 等运维确认（2026-10-13 06:11 报出 · 已被 2026-10-13 指令取代 · 2026-10-14 归档）

> **数据基础**（从 `kimi_pilot_results.json` 2100 条 + `fix1.json` 376 条实测）：
> - blocked: 50（matplotlib 31, django 10, sympy 6, sklearn 2, pytest 1；claude-code 15, hermes 15, deepseek 11, pi 5, codex 4）
> - quota-blocked: 14（全 django__django-16873，API 配额问题，非 infra）
> - no-patch: 4（全 deepseek，timeout）
> - astropy patch-not-applied: 28/42（eval env 失败，未纳入 fix1 的 5 repo 范围）
> - fix1 后仍 patch-not-applied: 97（mpl 30, sklearn 27, pytest 18, flask 14, sphinx 8）
> - **97 条根因已查清（§7）**：py_version_36_needs_38=42(pytest/sklearn/sphinx) · py_version_38_needs_39=30(全 matplotlib) · werkzeug_version=14(全 flask) · other=11
> - **新增 P1-1b**：per-repo Python 版本 conda env（3.8 for pytest/sklearn/sphinx, 3.9 for matplotlib）+ werkzeug 兼容版本预装 → 可修 86/97 条

| P1 项 | 做法 | 成本 | ETA | 占用 | 预估挽回 | 风险 |
|:--|:--|:--|:--|:--|:--|:--|
| **P1-1 astropy** | 预编译 astropy wheel（`pip wheel astropy`）+ 注入 `~/.cache/pip`；或增大 eval 沙箱 memory limit（cgroup）| ~4h | 批准后 4h | CPU+磁盘（编译 ~2GB），无 GPU | ~28 patch-apply 新增（resolved 数取决于 patch 质量）| 中：astropy C 扩展编译依赖多 |
| **P1-2 网络 503** | ① git fetch 加 3 次重试+指数退避 ② 预克隆 5 高频 repo 到本地缓存（`/dev/shm/repos/`），harness 从本地 clone | ~1h | 批准后 1h | CPU+磁盘（预克隆 ~5GB），无 GPU | 50 blocked → 可重跑 | 低：改 `run_serial_kimi.py` git 逻辑 |
| **P1-3 Docker** | per-instance 预构建 Docker（官方做法）| ~2-3 天 | 2-3 天 | 重 CPU+大量磁盘+Docker | 理论上覆盖全部 env 失败 | 🔴 **不可行**：本机 `docker info`→NOT AVAILABLE，内网无法 `docker pull`。**建议暂缓** |
| **②b 重跑 agent** | blocked(50)+no-patch(4)=54 条重跑 harness（同 7 harness+kimi-k2.6-cloud）；quota-blocked(14) 不重跑 | ~1h(并行)~5.4h(串行) | P1-2 后 ~1h | CPU+API 配额，无 GPU | 50 blocked → 重跑后估 ~5-10 resolved | 低：已验证流程 |

> **建议优先级**：P1-2（~1h, 低风险）→ ②b 重跑（~1h）→ P1-1（~4h）→ P1-3 暂缓。**等运维确认后执行**。

## §FIX2 RESULTS — P1-1b fix2 重评完成（2026-10-13 13:00 · 2026-10-14 归档）

> **fix2 重评 32 条（pytest 18 + flask 14）全部完成** ✅（5.6min total）。
> **修复措施**：pytest `pip install 'setuptools<70'` + flask `pip install 'werkzeug<2.3'`（均用现有 testbed env，无需 C 重建）。
>
> **pytest (18 条)**：**9 FLIPPED to RESOLVED** ✅ · 15/18 patch-applied（从 0/18！）· 3.6min
> - pytest-5227：7/7 harness 全部 RESOLVED（codex/pi/opencode/cline-patched/deepseek/claude-code/hermes）
> - pytest-5103：2/2 RESOLVED（pi/opencode）
> - pytest-5221：6/6 patch-applied 但 f2p=0/2（全未通过 — patch 全错，agent 能力限制）
> - pytest-11143/11148：3 条 patch 仍未 apply（pi 的 patch 有兼容性问题）
>
> **flask (14 条)**：**0 FLIPPED** · 13/14 patch-applied（从 0/14！）· 2.0min
> - flask-4045：7/7 patch-applied，f2p=1/2（1/2 fail-to-pass 通过 — patch 部分正确但不完整）
> - flask-4992：6/7 patch-applied，f2p=0/1（全未通过 — patch 质量限制）
> - 1 条未 apply：opencode/flask-4992
>
> **累计（fix1+fix2）**：574→617 resolved（27.3%→29.4%, +2.1pp）· +243 patch-applied
> **剩余 65 条 not-applied**：matplotlib 30（需 qhull+freetype build deps ~2h）· sklearn 27（需 build deps ~2h）· sphinx 8（待排查）
> **r1_eval.py fix2b**：`conda activate {env}` → `export PATH={env_path}/bin:$PATH`（chroot 内 conda activate 修复，正确保留）
> **下一步建议**：① matplotlib+sklearn 需额外 ~4h 安装 build deps + 重建 C 扩展（65 条中 57 条）② sphinx 8 条逐条排查 ③ **等运维确认后执行**

---

### §运维指令 · 2026-10-14（glm-5.3-flash 7×300：Base URL 更正 + 启动重测）· 原文（2026-10-17 由运维搬出，未改）

### 🆕 运维指令 · 2026-10-14（🔧 更正 glm-5.3-flash Base URL → `/v1`，去掉 cloud）· 用户直令 · 最高优先

> **用户令（2026-10-14）**：「harness: glm-5.3-flash 的 apikey 没问题，但是 base url 需要去掉 cloud。」（附：用户实测 `curl http://agi-gateway.cxmt.com/v1/chat/completions` 已 200 OK）

**① 更正上一指令的 Base URL（其余不变）**：
- ❌ 旧（错）：`http://agi-gateway.cxmt.com/cloud/v1`
- ✅ 新（对）：`http://agi-gateway.cxmt.com/v1`

**② 关键区别（务必注意）**：`glm-5.3-flash` 走 **`/v1`** 路径；而 `glm-5.2` 才走 `/cloud/v1`。**不要**沿用 glm-5.2 的 `/cloud/v1` 给 glm-5.3-flash（这正是之前 403 的根因）。

**③ 落地**：
- cline auth：`-p openai -k <key>` + `-b http://agi-gateway.cxmt.com/v1` + `-m glm-5.3-flash`。
- 同步更新 `launch_glm53_7x300.sh` / `run_serial_kimi.py` / `run_harness.py` 里所有 glm-5.3-flash 的 base url 为 `/v1`。
- 更新后先用 curl 探针复验 200（`GET/POST http://agi-gateway.cxmt.com/v1/chat/completions`，model=glm-5.3-flash），再 `bash launch_glm53_7x300.sh` 启动 7×300。

**④ 其余**：key / model name / 7×300 框架 / 独立 JSON / 对比报告要求一律不变（见上一指令）。🚫 不占 GPU、错峰 IO。commit 前缀 `harness glm53:`。

### 🆕 运维指令 · 2026-10-14（🚀 用 glm-5.3-flash 重测 7×300 —— 验证「能力是主因」）· 用户直令 · 最高优先

> **用户令（2026-10-14）**：「根据报告，harness 任务模型能力是 passrate 低的主因。既然如此，请 harness 使用更强的模型 glm-5.3-flash 重测 SWE-bench-Lite(300) 7×300。」

**背景**：审视结论 fix3/fix4 0-flip = **LLM 能力瓶颈（非 infra）**。现用更强 backbone `glm-5.3-flash` 重测，验证「换强模型 → passrate 显著提升」是否成立。

**① 模型（逐字遵守）**：
- model name：`glm-5.3-flash`
- API Key：`02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f`
- Base URL：`http://agi-gateway.cxmt.com/cloud/v1`

**② 跑法**：
- 复用 7×300 框架：7 harness（`cline-patched` / `codex` / `hermes` / `opencode` / `claude-code` / `deepseek-harness` / `pi`）× 300 SWE-bench-Lite，backbone 换成 `glm-5.3-flash`。
- 机制：`run_serial_kimi.py` 设 `HARNESS_MODEL=glm-5.3-flash`；cline auth 切 `-p openai -k <上述 key> -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.3-flash`（⚠️ 用 `/cloud/v1`，非 `/v1`）。
- 结果独立 JSON（建议 `glm53_pilot_results.json`），🚫 **不覆盖** `kimi_pilot_results.json`（保留旧 backbone 证据）。
- 幂等 `--resume`，沿用 `launch_7x300.sh` 模式（7 路并行、各自串行）。

**③ 对比与交付**：
- 与 `kimi-k2.6-cloud` 的 7×300 做**同 harness 逐项对比**（旧 574 resolved / 原口径）。
- 交付中文 HTML（如 `reports/report_harness_glm53_vs_kimi_7x300.html`）：TL;DR / 7 harness × (glm53 vs kimi) resolved + passrate / 能力提升量（若显著提升 → 证实「能力是主因」）/ 结论 + 诚实条款。

**④ 纪律**：
- 🚫 不占 GPU（SWE-bench = CPU + API 配额）；与 `.29` pretrain P-8 训练、`.12` data 下载**避让 IO**（`nice` 限流、错峰）。
- 开跑前 curl 探针确认 glm-5.3-flash key 可用（200）；监控 quota/timeout/no-patch 率。
- ETA ~42h（7 路并行），结果幂等可续。
- commit 前缀 `harness glm53:` · 任务书 >32KB 自滚归档。

---

### §运维指令 · 2026-10-13（P1 剩余项继续修 + 重评/重跑）· 原文（2026-10-17 由运维搬出，未改）

### 🆕 运维指令 · 2026-10-13（🔧 P1 剩余项继续修 + 重评/重跑）· 用户直令 · 最高优先

> 用户令（2026-10-13）：「harness 继续修。」—— 承接 fix1(34 flipped)+fix2(9 flipped) 已把 resolved 574→617（29.4%），现推进剩余 P1 项。
> 性质：CPU+磁盘，不占 GPU；与 `.29` pretrain 训练 / data 线下载错峰 IO（`nice` 限流）。

① 剩余项按此顺序修（每批开工前心跳报「instance×harness 条数 + ETA + 占用」→ 然后直接执行，不再逐条等确认；P1-3 Docker 冻结跳过）：
1. fix3：matplotlib(30) + sklearn(27) 的 C 扩展 build deps + 重评（~4h）
   - matplotlib：在 `testbed_py39` 装 qhull + freetype build deps → 重建 `_c_internal_utils` 等 C 扩展 → `pip install -e .` 通过 → 重评这 30 条。
   - sklearn：`testbed_py38` 装 build deps → 重建 sklearn C 扩展 → 重评 27 条。
   - 结果写独立 `kimi_pilot_results.fix3.json`（幂等 `--resume`）。
2. sphinx 8 条逐条排查：查 `base_commit` 可达性 / git checkout / 依赖；能修就修，修不了标「待 P1-3 Docker 或不可行」。
3. P1-1 astropy(28/42)：`pip wheel astropy` 预编译 + 注入 `~/.cache/pip`（或增大杀沙箱 memory cgroup）→ 重评 28 条（~4h）。
4. P1-2 网络 503 + ②b 重跑 agent：① git fetch 加 3 次重试+指数退避 + 预克隆 5 高频 repo（`/dev/shm/repos/`）；② 重跑 blocked(50) + no-patch(4)（quota-blocked 14 不重跑），同 7 harness + kimi-k2.6-cloud。（修 ~1h + 重跑 1–5.4h，CPU+API 配额）

② 前后对比与交付：新结果一律独立 JSON（fix3 / astropy / rerun）；更新 `report_harness_eval_fix_rerun.html` 追加 per-repo before/after；报累计 resolved 数 + cline resolve rate（29.4%→?），与 P0 预估（~+22/harness）对照；每项给证据（`test_output.txt` 前后 / rootfs 变化 / 命令）。

③ 纪律：🚫 不占 GPU · 🚫 不改已发布数值 · 🚫 P1-3 Docker 冻结 · 全批幂等可续 · commit 前缀 `harness fix:` · 任务书 >32KB 自滚归档。

---

## 归档块 M · 2026-10-17 两条运维块（Docker 权限复查 + 清理 .29 /tmp）— 2026-10-17 20:0x 运维搬出（原文，未改）

### 🆕 运维指令 · 2026-10-17（✅ Docker 权限已就绪 · 复查推进 TB 2.0）· 用户直令

> **用户令（2026-10-17）**：harness 若需 sudo 可用（密码另由运维掌握，🚫 不落盘不落库）；但运维已实测 Docker 权限**已 OK**。

**① Docker 复查（实测结论，harness 只需 `docker ps` 复核）**：`id -nG` 已含 `docker` 组；`docker ps` **无需 sudo 即可跑**（daemon 正常）。→ TB 2.0 的「Docker 权限」blocker **已解除**，不必再等 ops usermod。

**② 剩余 blocker**：仅 `terminal-bench@2.0` 数据集需 `harbor auth login`（GitHub OAuth，另行授权）。

**③ 行动**：Docker OK 后 → 推进 T1 剩余（dataset 拉取 + `oracle 5×`）→ T2 正式横评。若后续哪步确需 root（如改系统级配置），回报运维，由运维提供 sudo 执行，🚫 agent 不自行猜测 sudo 用途。

### 🆕 运维指令 · 2026-10-17（🧹 清理本线 .29 /tmp 残留）· 用户直令

> **用户令（2026-10-17）**：「让 harness 清理 .29 的 /tmp。」

**① 清理范围**：harness 线在 `.29` 的 `/tmp` 下旧残留（>1 天未动用的 claude-code/opencode 旧 workdirs 拷贝、rootfs 克隆、旧 log、旧测试床临时等）。⚠️ 运维已清掉最大头 `/tmp/claude-6218`（27G）。

**② 纪律**：
- 先 `du -sh /tmp/* 2>/dev/null | sort -rh | head -20` 盘点，**只清本线自己的、确认 >1 天未动**的，把要删清单抄进心跳再删。
- 🚫 不删：`/dev/shm/harness_work/workdirs/`（活跃评测在那边，不在 /tmp）、下载/克隆中、别线在途文件、<1 天的、`/tmp/systemd-*`。
- ✅ 清完报 `df -h /tmp` 前后对比 + 释放量。
- commit 前缀 `harness tmp-clean:` · 任务书 >32KB 自滚归档。



<!-- archived from BAIZE_HARNESS_TASK.md 2026-10-19 22:5x (closed 2026-10-18 blocks) -->
### 🆕 运维指令 · 2026-10-18 10:2x（🚨 **P0：先修复 `.29` 的 ops 中继，再继续 TB pilot**）· 用户直令 · 最高优先

> **背景**：RUN_ID 123（09:54 推送的只读探针）至今 `ops/.last_run_id` 仍为 **122**、outbox 无回执；而 pretrain（10:08）与 harness（10:09）仍能正常 push ⇒ 判定为 **`.29` 本机 ops 中继进程停摆/冻死**，不是网络。你与它在同一台机器，由你修复。
> ⚠️ **历史事故**：在命令行里把 `pkill -f "ops_relay.sh"` 与启动命令写在一起 → **自匹配**，把中继和执行重启的 shell 一起杀掉。**必须写进脚本文件再执行。**

**① 安全重启（照抄执行）**
```bash
cat > /tmp/fix_relay_1018.sh <<'EOF'
set -u
pgrep -f 'bash [o]ps_relay[.]sh' | xargs -r kill
sleep 2
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
setsid bash ops_relay.sh > /tmp/baize_ops_relay.log 2>&1 < /dev/null &
sleep 3
pgrep -af 'bash [o]ps_relay[.]sh' | cut -c1-140
tail -5 /tmp/baize_ops_relay.log
EOF
bash /tmp/fix_relay_1018.sh
```
- **判据**：≥1 个 `bash ops_relay.sh` 进程 + 日志出现 started；**30–90s 内 `.last_run_id` 应从 122 → 123**（123 已就绪，含 `.29` loop/GPU + `.12` data git 只读诊断）。
- 若 2 次仍不起 ⇒ 贴 `pgrep -af` / 日志原文报 blocker；🚫 不改 `ops_relay.sh` 本体、🚫 不杀 loop、🚫 不碰训练。

**② 修好后继续 TB**：10:09 已提交 `DockerEnvironment.exec()` 签名修复（`timeout→timeout_sec`、env 走参数，7 适配器 + `_base`）⇒ 直接重跑 **solo smoke（cline-patched × 1）**，通过后进 **7×5 pilot**。
**③ 红线**：只动 `.29` 本机；🚫 不占 GPU、不重启 `torchrun`；commit 前缀 `harness ops:`。

### 🆕 运维指令 · 2026-10-18（🚀 P0：从 solo smoke 推进到 **7×5 pilot**（不再只做单适配器验证））· 用户直令 · 最高优先

> **背景**：Oracle 5/5 ✅、7 适配器骨架 ✅、28/28 mock 单测 ✅、`_install_node` 已改 NVM+aliyun、launch 脚本已改本地 `-p` + `minimal2` overlay。**目前卡在"等 smoke"，已静止 1.5h。** 本令要求：**不再逐个逐个验，用一个 pilot 把 7 个适配器一次性打穿。**

**① 第一小时：solo smoke（只做 1 个，必须留证）**
- 选 **cline-patched** × **1 个任务**（用 `--pilot` 里的第 1 个任务，或最轻量那个）。
- 目的只有 4 个：**① NVM/镜像装包通 ② API 通（`wire_api=chat` 或 provider 正确） ③ agent 真跑起来（有 tool_calls） ④ trace 落盘可读**。
- 通过判据：容器内 `cline` 可执行 + 至少 1 条 API 200 + trace 文件非空 + 有 `tool_calls`。
- 失败 ⇒ 只修**不通过的那一项**（装包/网络/配置），再重跑**同一个** smoke；最多 3 次，仍不过就贴原文报 blocker（🚫 不要换任务掩盖问题）。

**② 紧接：7×5 pilot（35 trials，这是门禁）**
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench
bash launch_tb_7way.sh --pilot      # 7 harness × 5 tasks = 35 trials
```
- 7 路：cline-patched / codex / hermes / opencode / claude-code / deepseek-harness / pi。
- 模型：`kimi-k2.6-cloud`（若网关 401/403 ⇒ 按 ⑤ 处理，**不许硬跑**）。
- 每路必须输出：`install()` 是否成功、`resolved/failed/infra/quota` 四分类计数、trace 路径。
- **pilot 判据（先定）**：
  | 结果 | 结论 |
  |:--|:--|
  | infra 失败率 **≤ 20%** 且 **≥6 路有可运行 trial** | ✅ 放行 7×89 |
  | infra 失败率 20–50% | ⚠️ 先修 infra，**不放行全量** |
  | >50% 或 ≥3 路完全跑不起来 | 🔴 停，报 blocker（附每路失败原文） |

**③ 放行后：7×89 全量（623 trials）**
- 只在 ② 判据通过后启动；**每路串行、7 路按 429 自适应降并发**。
- 交付：`terminalbench_kimi_k2.6_results.json` + `reports/report_harness_terminalbench_7way_zh.html`（含 Wilson 95% CI、7×7 McNemar、quota 单列、版本表 + 诚实条款）。

**④ 资源与纪律**
- 只用 `.29` 的 CPU/磁盘（**不占 GPU**：`.29` 8 卡在跑 pretrain decay，🚫 不碰）；Docker 只在 `.29`。
- 与 data 错峰重 IO；`/tmp` 使用前先 `df`（`.29` 约 15G，**超 5G 的镜像/日志先清或换 `/nasdata`**）。
- 每次唤醒只推进一步（smoke → pilot → 全量）；`WAITING=1` 仅在真跑时置位。
- commit 前缀 `harness tb:`；MEMORY ≤32KB 自滚。

**⑤ 网关异常时**
- 若 `kimi-k2.6-cloud` 或网关整体 401/403：**立即停**，贴 `curl -i` 原文（含 `www-authenticate`/`server`），报 blocker；🚫 不要用假分数/跳过 trial 凑数，🚫 不要把 infra 失败算成 harness 失败。
### 🆕 运维指令 · 2026-10-19 23:1x（🔪 **P0：确认双 harness loop 后 kill `.12` 那个**）· 用户直令 · 最高优先

> 用户令（原文）：「如果确认有两个 harness loop，那么杀掉一个（ .12 的）」
> **背景**：agent 报阻塞「疑似 .12 PID 2663131 / .29 PID 1972249 双 harness loop 并发」→ 会导致重复唤醒、重复 commit、**ops 中继回执丢失（137/138/139）**。
> **🔒 执行纪律（吸取 R86 误杀教训·硬要求）**：
> 1. **先证明再动手**：必须在 **`.12` 与 `.29` 两台机分别**跑 `ps -eo pid,ppid,etimes,lstart,args | grep -iE 'harness.*loop' | grep -v grep`，**贴出两台机的原始输出**；
> 2. **判据**：只有**两台都确实存在一个 harness loop 进程**（且不是互为父子）才算「确认双 loop」；若只在一台看到 → **不 kill**，改为写清"未见双 loop"并退出；
> 3. **kill 方式**：🚫 **禁止 `pkill -f` / 禁止 cmdline 子串匹配**（R86 教训：loop 会把整份任务书当参数传进去，含 `e0031982`/`run_eval` 字面 ⇒ 误命中）。**必须**：`ps` 拿到 `.12` 上那个 loop 的**显式 PID** → `cat /proc/<PID>/cmdline` 打印前 80 字符**人工核对确实是 loop 而非 opencode 子进程** → `kill -TERM <PID>` → 等 10s → 仍在才 `kill -KILL <PID>`；
> 4. **只杀 loop 主进程**（`bash <...>harness_loop.sh` 那一行）；**不要**杀它的 opencode/cline 子进程（由 loop 自己收）；**不要**碰 `.29` 的任何进程；
> 5. **kill 后必查**：`.12` 上 `pgrep -f 'harness.*loop'` 应为空、`.29` 上应仍在；`ops_relay`（.29）仍活；**Gen5 pilot 不受影响**（pilot 在 `.29`，由 launch PID 1732377 驱动，不在 `.12`）；
> 6. 输出全部 `cut -c1-140`；结果写 `MEMORY_HARNESS.md` 心跳（≤6 行）+ `daily-memories-harness/`，commit `harness ops: kill .12 duplicate loop`。

**若确认双 loop 且已 kill `.12` 那个 → 继续原计划**：等 Gen5 最后两路（deepseek / pi）跑完 → 判门据（infra ≤20% AND ≥6/7 runnable）→ **hermes 须 Gen6 重测验证 R457 plugin fix**。



> **运维已直接改代码**：`run/harness/terminalbench/agents/hermes.py`（见 commit `R457`）。**agent 不需要再研究怎么修，只需验证 + 跑通 + 判门据。**
>
> **根因（已查明·权威依据）**：hermes-agent **不从 `~/.hermes/config.yaml` 读取自定义 provider**。provider 必须是**插件**：
> `$HERMES_HOME/plugins/model-providers/<name>/`，内含 `__init__.py`（调 `register_provider(profile)`）+ `plugin.yaml`（manifest）。
> 原代码把 `provider: kimi-proxy: {base_url, api_key, api_mode}` 写进 config.yaml ⇒ **被静默忽略** ⇒ `hermes --provider kimi-proxy` 报 **`Unknown provider kimi-proxy`**（Gen5 5/5 RuntimeError 的真正原因，与 R452 猜的"py3.14/uv 装不上"无关）。
> 依据：NousResearch/hermes-agent `plugins/model-providers/README.md`（"Each subdirectory is a self-contained provider profile plugin… `__init__.py` is imported and expected to call `providers.register_provider(profile)`"）。
>
> **R457 改了什么（3 处）**：
> 1. `install()` 新增 `_install_provider_plugin()`：`mkdir -p /root/.hermes/plugins/model-providers/kimi-proxy`，写入 `__init__.py`（`ProviderProfile(name='kimi-proxy', aliases=('kimi','kimi-cloud'), env_vars=('HERMES_KIMI_API_KEY','HERMES_KIMI_BASE_URL'), base_url=<TB_BASE_URL>)` + `register_provider(...)`）与 `plugin.yaml`（`kind: model-provider`）。
> 2. `run()` 的 config.yaml **删掉无效 provider 段**（只留 `agent.max_turns`）。
> 3. env 改为 **真实 key + 直连内网网关**（不再走本机 gw_proxy 的 dummy key）：`HERMES_KIMI_API_KEY`/`OPENAI_API_KEY` = 真实 key，`HERMES_KIMI_BASE_URL`/`OPENAI_BASE_URL` = `TB_BASE_URL`；`NO_PROXY` 含 `10.239.*,172.19.*`。
> 4. 顺带把 `exec_as_root` 换成基类 `_exec_in_container`（原来那个方法在基类里不存在）。

**① 验证（先只跑 1 题，别一上来 7×5）**
```bash
# 在 .29（docker 只在 .29）
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench
# 单题冒烟：只跑 fix-git 这一题，命中缓存镜像
harbor run -p <单题 dataset 目录> --agent hermes --model kimi-k2.6-cloud 2>&1 | tail -40
```
**通过判据**：日志里**不再出现** `Unknown provider kimi-proxy`；容器内 `ls -l /root/.hermes/plugins/model-providers/kimi-proxy/` 能看到 `__init__.py` + `plugin.yaml`；trial 能真正产生 tool_calls。

**② 若冒烟 PASS → 重跑 Gen5 的 hermes 一路（×5）**
- 其余 6 路**不重跑**（cline-patched 0.6 / codex 0.0 / opencode 0.4 已有效；claude-code/deepseek/pi 等当前 pilot 自己完成）。
- 汇聚后按判据：**infra ≤20% AND ≥6/7 runnable** → 过则放行 7×89；不过则报 blocker。

**③ 若冒烟 FAIL → 只报 blocker，不要再自己猜**
- 必须贴出：容器内 `hermes --version`、`hermes model list`（或 `hermes --help` 里 provider 相关段）、`ls -l /root/.hermes/plugins/model-providers/kimi-proxy/`、以及 trial 的 stderr 原文。
- 🚫 **不要**再改 `hermes.py`（已由运维维护），不要说"hermes 需要 py3.14"（该结论已被证伪）。
- 🚫 不要动运行中的其他 6 路 pilot。

**④ 纪律**
- 只碰 hermes 一路；🚫 不重启 .29 docker、不杀其他 trial、不启 7×89。
- 回报写 `MEMORY_HARNESS.md` 心跳（**≤6 行**，避免超 32KB）+ `daily-memories-harness/2026-10-19.md`，commit 前缀 `harness tb:`。

---ARCHIVE BOUNDARY 2026-10-23 R460---
### 🆕 运维指令 · 2026-10-23 22:1x（**用 `http_proxy` 装 `npm install -g`，装完退回无代理环境**）· 用户直令 · 最高优先

> 用户原话：「Harness: harness 想要 npm install -g 需要使用 http_proxy, 地址跟 https_proxy一样，但要小心这个代理会让agent无法访问大模型API，因此需要开新的环境，设置环境变量，安装后，退回到没有http_proxy的环境。」

**① 取代理值（只读，不改）**
- `echo "$https_proxy"`（或 `$HTTPS_PROXY`）→ **`http_proxy` 用它同一个地址**；记下原文（形如 `http://172.19.92.23:13128`）。

**② 在「独立环境」里装（关键：🚫 污染 agent 自身环境）**
- 🚫 **禁止**在 `~/.bashrc` / `/etc/profile` / 当前 loop 的 parent shell 里 `export http_proxy`（会让 cline/harness 自身的 LLM API 调用被代理 → 直接 403/超时/静默失败）。
- 正确做法（任选，推荐 A）：
  - **A（单命令隔离，首选）**：`env http_proxy="<同https_proxy>" https_proxy="<同>" NO_PROXY="10.129.32.75,localhost,127.0.0.1" npm install -g <pkg>`
  - **B（子 shell）**：`bash -c 'export http_proxy=... https_proxy=... NO_PROXY=...; npm install -g <pkg>'`（子 shell 退出后环境自动恢复）
  - **C（npm 原生参数，零环境变量）**：`npm install -g --proxy "<同>" --https-proxy "<同>" <pkg>`
- 若用了 `npm config set proxy/https-proxy`（临时手段），**装完必须 `npm config delete proxy && npm config delete https-proxy`**，并 `cat ~/.npmrc` 复核**不留 proxy 行**。

**③ 装完立刻「回到无代理环境」并验证**
- 在**不带** `http_proxy/https_proxy` 的新 shell 里验证（`env | grep -i proxy` 只应剩 loop 原有的 `https_proxy`，**不应有 `http_proxy`**）：
  - `npm ls -g --depth=0 | grep -E 'codex|claude'`
  - `codex --version` / `claude --version`（或该包官方二进制名）
- 再各跑 1 次**最小 smoke**（`--version` 之外的一次真实调用，例如 `codex --help` + 一次 API 往返），**必须证明 LLM API 仍可访问**（HTTP 200 / 正常响应）。

**④ 门据推进**
- 目标：把 gate 从 **5/7 → 6/7 或 7/7**（缺的正是 `codex` + `claude-code`，此前均为 `npm install -g` 超时）。
- 逐个修、逐个验证、逐个写进 gate 表（每修好 1 个就 commit 一次，前缀 `harness`）。
- **达到 ≥6/7 ⇒ 按既有计划启动 7×89 pilot**（每轮回报 pass/run 数），并回报门据变化；未达标只报 blocker（附 npm 报错原文 ≤20 行）。
- 同一包装失败 **≤2 次**，超过就换 C 方案（`--proxy` 参数）或报 blocker，🚫 死磕烧时间。

**⑤ 纪律**：🚫 不改上游 harness 源码；🚫 不把代理写进任何持久化配置；装完必须回到「无 `http_proxy`」的状态并在回复里贴 `env | grep -i proxy` 的原文为证。

### 🔧 运维指令 · 2026-10-23（**分阶段落盘：逐 harness 写报告，每段 ≤2500 token**）· 用户直令 · 最高优先

> 已确认你在「读源码分析」阶段干活正常，但 3600s 内完不成「7 个 harness 全部分析 + 写整份报告」→ 每轮超时、未落盘内容丢失。**必须分阶段落盘，禁止一口气写整份报告。**

1. **逐 harness 推进**：按 `cline → codex → hermes-agent → opencode → claude-code → deepseek-harness → pi` 顺序，**一次只分析 1 个 harness**。
2. **每分析完 1 个 harness 立即落盘**：把该 harness 的「压缩策略 / 触发阈值 / 保留策略 / 缺陷 + 代码证据(文件:行)」写成一段 HTML，**立即 append 写入** `reports/report_harness_context_compression_7way_zh.html`（或先写 `reports/_ctx_comp/<harness>.md` 中间件，最后合并）。
3. **每段 ≤ 2500 token（≈1800 汉字）**，控制篇幅；写完一个 harness **立即 commit/push**，再开始下一个。
4. 🚫 **禁止**一次性生成 7 个 harness 的分析文本再写文件（这正是超时根因）。
5. 7 个全写完后，最后合并出「对比总表 + TL;DR + 结论」。

commit 前缀 `harness hb:`。

### 🆕 运维指令 · 2026-10-23（📄 **比较 7 个 harness 的上下文压缩机制 → 中文 HTML 报告**）· 用户直令 · 最高优先

> 用户原话：「给 harness 下任务：看代码 /nas_train/app.e0031982/harness 比较7个harness的上下文压缩机制，写成html中文报告。」

**① 任务（H-B 源码分析，只读，不跑评测/不占 GPU）**
- 目标目录：`/nas_train/app.e0031982/harness/`（只读参考，🚫 勿改上游代码）。
- 7 个 harness（对应 TB 横评 7 路）：`cline` / `codex` / `hermes-agent` / `opencode` / `claude-code` / `deepseek-harness` / `pi`。
- 主题：**上下文压缩机制（context compaction / compression）**——包括但不限于：摘要(summarization)、截断(truncation)、token budget 管理、auto-compact 触发条件与阈值、压缩后保留/丢弃策略、历史消息折叠、工具调用轨迹裁剪、崩溃/超时恢复。**每条结论贴 `文件:行号` 原文证据，不许猜。**

**② 输出（中文自包含 HTML）**
- 文件：`reports/report_harness_context_compression_7way_zh.html`（内联样式，无外链/无脚本）。
- 结构：TL;DR → **对比总表**（每 harness 一行：压缩策略 / 触发阈值 / 保留策略 / 缺陷）→ 逐 harness 详述（带代码证据）→ **结合本项目教训**（我们 harness cline 的 Auto-compacting 超时问题）→ 总结与建议。
- commit 前缀 `harness hb:`。

**③ 纪律**：只读源码、不跑评测、不占 GPU；报告数字/结论可溯源 `文件:行`；MEMORY/任务书 ≤32KB 自滚归档。

---ARCHIVE BOUNDARY 2026-10-24 R475---

### 🔴 补充令 · 2026-10-24 09:2x（**用户提供关键线索：同事已通过 92.25 代理成功拉过 Docker 镜像；备选 92.23**）· 用户直令 · 最高优先

> 用户原话：「另外**有同事通过 92.25 代理成功拉取过 docker 镜像**，另外可能得代理则是 92.23」。
> **这直接推翻"MITM proxy blocks Docker Hub pull = 不可解"的结论** —— 之前 09:0x 令里的"阻塞"是**没配 dockerd 代理**造成的，不是网络不可达。

**① 优先级重排（这几条比 7 并发更重要，先做）**

| 优先 | 任务 |
|:--:|---|
| **P0** | **查清 15 个镜像的来源**（是 pull 来的还是 `docker load` 来的？`docker images` + `docker history` + 创建时间） |
| **P0** | **查 `dockerd` 是否配了代理**：`systemctl show docker --property=Environment`、`/etc/systemd/system/docker.service.d/*.conf`、`/etc/docker/daemon.json` |
| **P0** | **实测 `docker pull` 当前能否通**（用最小镜像 `hello-world` 试，贴**完整报错原文**） |
| **P1** | **按用户线索给 dockerd 配代理并验证**：先试 **`http://172.19.92.25:13128`**，不通再试 **`http://172.19.92.23:13128`** |
| **P1** | 通了之后 **pull 剩余 74 个镜像**（先查体积 + Docker Root Dir 剩余空间） |
| **P2** | 再谈 **7 并发**（09:0x 令已下发，镜像补齐后再切并发才有意义） |

**② dockerd 配代理的标准做法（按此执行，注意风险）**
```bash
# 1) 建 drop-in 配置（不直接改 docker.service）
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://172.19.92.25:13128"
Environment="HTTPS_PROXY=http://172.19.92.25:13128"
Environment="NO_PROXY=localhost,127.0.0.1,10.0.0.0/8,172.19.0.0/16"
EOF

# 2) 重载并重启（⚠️ 会短暂中断 docker，先确认没有正在跑的容器/评测）
sudo systemctl daemon-reload
sudo systemctl restart docker

# 3) 验证
sudo systemctl show docker --property=Environment | tr ' ' '\n' | grep -i proxy
docker pull hello-world          # 必须成功
```
- ⚠️ **重启 docker 会杀掉所有运行中容器** → **必须先确认 harness 的 7×15 v2（R473）是否在跑**；若在跑，**等它跑完或先记录进度再重启**，不许直接打断。
- ⚠️ 若 `docker.service` 被 systemd drop-in 忽略（有的发行版要用 `daemon.json` 的 `proxies` 字段），**两种方式都试并贴出哪种生效**。
- ⚠️ **92.25 不通就换 92.23**；两个都不通再报阻塞（附两次的完整报错）。

**③ 验证通过后：补齐镜像**
1. `docker images` 现有 15 个 + Terminal-Bench 89 题对应镜像：**列出缺哪 74 个**（取 task 的 Dockerfile / image 名）。
2. 查体积：**总下载量 + 按 layer digest 去重后的实际量**（很多题共享 base layer，别被"89 倍"吓到）。
3. 查 `docker info | grep 'Docker Root Dir'` + `df -h <该目录>`：**镜像落本地盘不是 NFS**，空间不够就先报，别拉一半撑爆。
4. **分批 pull**（每批 10 个，批间查剩余空间），失败的重试 2 次后记录。
5. **补满后**：7×89 才真正可跑，此时再切 7 并发。

**④ 回报**：15 个镜像来源 / dockerd 代理配置前后对比 / `hello-world` pull 结果 / 缺的 74 个清单 + 体积 / Docker Root Dir 剩余空间 / 补齐进度。

### 🔴 运维指令 · 2026-10-24 09:0x（**改成 7 并发跑（对齐 SWE-bench 做法）+ 回答"为何只有 15 题"**）· 用户直令 · 最高优先

> 用户原话：「harness：让他起**7 并发**评测（以前 SWE-bench 就是 7 并发），另外为啥 7×15，terminal bench 只有 15 道题吗？」

**① 立即回答（先答，写在 MEMORY 顶部，不许绕）**
- **Terminal-Bench 一共多少题？** 贴出数据集实际条数（`ls` tasks 目录 / 读 dataset 文件），并说明 **89 是不是全量**。
- **为什么只有 15 题参与？** 现在 MEMORY 里写的是「**15/89 task images only（MITM proxy blocks Docker Hub pull）**」——请核实并明确回答：
  - 是**本地只有 15 个镜像**（其余 74 个拉不下来）？还是**任务集本身只有 15 题**？
  - **能不能把剩下 74 个镜像拉下来？**（MITM proxy 挡 Docker Hub → 有没有替代源、离线 tar、或允许走代理 `docker pull` 的路径）—— 给出**可行/不可行 + 具体办法 + 预计耗时**。
  - 这是**当前最大的口径限制**，报告里必须写清"15/89 非全量"。

**② 改成 7 并发（用户明确要求）**
- 当前是**串行**（7 harness × 15 tasks 串行，ETA ~17h）。
- 改为 **7 并发**：**每个 harness 一个并发槽**（7 个 harness 同时跑，各自 15 题内部按需串行或再并行）。
  - 若 harbor 支持 `--parallel` / `--jobs` / `--max-workers`，**设 7**；
  - 若 harness 之间要隔离（端口/工作目录/容器），**务必做到互不干扰**：各自独立 `--jobs-dir`（**必须放 `/tmp`，不要 NFS**，R473 已踩过 Stale handle）、独立端口、独立 trace 目录。
- **执行前先做 30 秒资源评估**：7 并发同时跑 Terminal-Bench 容器，**CPU/内存/磁盘 IO 是否够**（每容器可能吃 2-4 核 + 数 GB）。不够就降到 N（给依据），**不要盲目开 7 导致全部 OOM/timeout**。
- **口径声明**：7 并发会引入资源竞争，**结果需注明"7-way concurrent"，与之前串行结果不可直接比**；若某 harness 因竞争超时，在报告里单独标注。

**③ 预期收益**：ETA 从 ~17h 压到 **~2.5-3h**（7 harness 并行，每 harness 15 题 × ~10min ≈ 2.5h）。

**④ 纪律**
- 🚫 不 kill v2（若已跑出部分结果，先让它跑完或记录已完成部分，再切 7 并发）
- ✅ 切换后必须报：并发数 / 每 harness 的 jobs-dir / 端口分配 / 前 10 分钟资源占用
- ✅ 报告里必须同时给出：**每 harness 逐题结果 + 汇总 + McNemar 配对检验 + "15/89 非全量"声明**

---ARCHIVE BOUNDARY 2026-10-24 R481---
