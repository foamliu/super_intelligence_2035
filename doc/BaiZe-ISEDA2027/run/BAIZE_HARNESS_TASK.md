# BAIZE_HARNESS_TASK.md

> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_HARNESS.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。
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

### 📦 运维指令 · 2026-10-19 23:1x（🔪 P0：kill .12 双 loop + R457 hermes plugin fix 详述）— 已归档 → ARCHIVE_OPERATOR_HARNESS.md（2026-10-23 R460 归档）
### 📦 运维指令 · 2026-10-18 10:2x（修 .29 ops 中继 P0）+ 2026-10-18（7×5 pilot 推进）— 已归档

> **已闭合**：中继已修（R440+ 持续健康，.last_run_id 追至 139）；pilot 已由 R446~R457 承接至 Gen5。原文移至 `run/ARCHIVE_OPERATOR_HARNESS.md`。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 🆕 运维指令 · 2026-10-17 20:0x（🚨 P0 抢修：重启 ops 中继 + 重跑 3 个失败 oracle 任务）
> ⏩ 已闭合（oracle 5/5 已达成；中继已恢复）→ `daily-memories-harness/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-17（🧪 Terminal-Bench 2.0 · 7 harness × 89 task · kimi-k2.6-cloud）· 用户直令 · 最高优先（T1；T0 仍是 glm53 收口）

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


### 🆕 运维指令 · 2026-10-16（▶️ **重启未跑完的 4 路评测，把 188 条补完**）· 最高优先
> ⏩ 已闭合（188 条已补完，glm53 7×300 2100/2100）→ `daily-memories-harness/2026-10-16.md`。

### 🆕 运维指令 · 2026-10-16（📊 glm53 7×300 评测结果中文 HTML 报告）· 用户直令 · 最高优先
> ✅ 已交付（`report_harness_glm53_7x300_zh.html`）→ 详情 `daily-memories-harness/2026-10-16.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_HARNESS.md` / `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）/ `daily-memories-harness/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `harness 归档: …` 前缀。
> 本轮动作：本任务书现 ≈32KB（已贴上限）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底同步一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_HARNESS.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_HARNESS.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_HARNESS.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-harness/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md \
              doc/BaiZe-ISEDA2027/run/harness doc/BaiZe-ISEDA2027/run/daily-memories-harness
   git commit -m "harness R<N>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。
> 📦 §运维口径（2026-10-05 深夜4 · Claude Code 合规口径）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：遥测已关、claude-code 已恢复横评。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · 授权自装 deepseek-harness 工具链）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：node22+rust 已装、deepseek-harness 已 build，待并入横评。需要时再读。

> 📦 §运维指令·2026-10-07（📊 昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：report_10_07_harness_overnight.html 已交付（27187B，自包含内联SVG，R118→R134，codex 43/96/161，总 resolved 61）。需要时再读。

> 📦 §运维指令·2026-10-07⑥（7-way: Hermes + Pi）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：7-way 横评全完成（cline-patched 60.0% · Pi 60.0% · Hermes 53.3% · opencode 50.0% · codex 46.7% · claude-code 43.3% · deepseek-harness 40.0%）。需要时再读。


> 📦 §运维指令·2026-10-07（30 × 5 harness 横评）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：5-way 横评完成（cline-patched 18/30, codex 14/30, opencode 7/30, claude-code 19/30, deepseek-harness 进行中 22/30）。已被 10-07⑥「7-way」取代。需要时再读。


> 📦 §运维指令·2026-10-05（晚 · 扩 300）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：被 10-07「先做 30 横评」取代。需要时再读。


### 🆕 运维口径 · 2026-10-05（你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测）

> 定位（运维 2026-10-05 13:2x，跨线）：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（见 `baize_data_loop.sh:114-120` / `baize_harness_loop.sh:106-116`）——目的是给内网网关鉴权（不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ 你（agent）会话里每条命令都继承了「无代理」env。
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 `Network is unreachable`（Errno 101）/ http `000` 是预期现象：🚫 不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题——别把它写进结论。
> 🔧 正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）：凡访问外网的那一条命令，自己显式带上代理（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都不要带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ 同机反证：`run/harness/r1_eval.py:144-148` 正是显式钉 proxy + 阿里云索引，所以同一台 `.29` 上 pip 装包一直成功；relay 侧 git 也通（`run/ops/outbox.md` RUN_ID 28：「外网 无 proxy=FAIL / 有 proxy=OK」，内网网关两种都 200）。
> 🚫 装包别动共享 py310 env（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令·2026-10-05（🔄 横评换「冷门模型」+ 严格串行）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：已切换 kimi-k2.6-cloud + 串行=1 + quota 三列报告，被 2026-10-07「30×5」块取代。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_HARNESS_TASK.md` ≈ 30KB、`MEMORY_HARNESS.md` ≈ 30KB（两者都已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_HARNESS.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）；
  ③ 较早的巡检条目（保留最近 ~20 条） → `daily-memories-harness/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 「运维问答」④ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---



| 项 | 当前值 |
|:---|:---|
| 当前指令 | 🎯 （2026-10-02 首启）两条线，按序做：<br>① H-B 源码分析（先开始） —— 分析 `/nas_train/app.e0031982/harness` 下各 harness 的源码，从 cline 开始，产出自包含 HTML 报告。分析主线见 §2。<br>② H-A SWE-bench 横评 —— 用 SWE-bench 评测几个 agent harness（cline / opencode / deepseek harness 等）并对比。⚠️ 先做可行性核查（§1.1），再定规模，不要一上来跑全量。<br>🚫 两条铁律：<b>不许猜</b>（源码结论必须贴文件+行号原文）；<b>每个结论必须可复现</b>（命令+输出）。 |
| 优先级覆盖 | H-B（源码分析）> H-A（SWE-bench）；<br>H-A 只在环境与数据集核查通过后才进入实跑。 |
| 状态索取 | `<无>`（若运维写入具体问题，本轮先答该问题再干活，答案写进 `MEMORY_HARNESS.md` 顶部「运维问答」区） |
| 暂停标志 | `<无>`（若写入 `STOP`，本轮只更新记忆、不做任何动作，然后退出） |

---

## 📊 进度快照（每次唤醒必须更新，供远程巡检）

> 固定格式写在 `MEMORY_HARNESS.md` 最顶部，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_HARNESS.md` 的顶部单独一行
（`baize_harness_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行 —— 否则会误触发 30 分钟长睡。

运维巡检方式：外部运维 `git pull` 读 `MEMORY_HARNESS.md` 顶部 + `harness/` 下的报告即可，不需要登录服务器。

---

## 0. 任务概述

目的：横向理解「agent harness」这一类系统 —— 它们的工程实现差异，以及它们在真实软件工程任务上的能力差异。

| 线 | 内容 | 产出 |
|:--|:--|:--|
| H-B | 源码分析（从 cline 开始） | `harness/<name>_SOURCE_ANALYSIS.html`（自包含） |
| H-A | SWE-bench 横评（cline / opencode / deepseek harness 等） | `harness/SWEBENCH_COMPARE.html` + 结果表 |

代码位置：`/nas_train/app.e0031982/harness/`

> ## 🔍 重要：该目录下已存在一条「同类研究线」（运维 2026-10-02 指示：可以合并）
>
> 首次勘察（RUN_ID 5）发现 `/nas_train/app.e0031982/harness/` 里不只有 5 个 harness 源码，还有：
> ```
> claude-code/  cline/  codex/  deepseek-harness/  opencode/     ← 5 个 harness
> loop.sh                                                          ← 它自己的 loop
> MEMORY.md                                                        ← 它自己的状态文件
> daily-memories/  evidence/  mechanisms/                          ← 它自己的记忆与证据目录
> analyze_harness_sources.md   (11.8 KB)                           ← 已有源码分析文档
> report.html                  (24.6 KB)                           ← 已有报告
> ```
> 文件日期为 Sep 4 – Sep 15，早于本线创建（Oct 2），非本线产物。
>
> ### ✅ 运维确认 + 指示（2026-10-02）
> - 运维确认：9 月初确实下发过一次「5 个 harness 比较」的任务（就是这条线）；
> - ⚠️ 它的 `loop.sh` 早已停掉 → 不会与我们冲突，也不要去重启它；
> - 指示：可以合并。
>
> → 所以它的产物是「纯输入」：`analyze_harness_sources.md` / `report.html` / `evidence/` / `mechanisms/`
> 都是可复用的既有素材，但其结论需要按我们的 5 条主线重新审视（它的分析角度可能不同）。
>
> 你要做的（H-B 开始前先做）：
> 1. 先把这条既有线的家底摸清（只读，不要改动它）：
>    - `MEMORY.md`：它的 PHASE / 已完成 / 产出
>    - `loop.sh`：它跑什么、是否还在运行（`pgrep -af 'harness/loop.sh'`）
>    - `analyze_harness_sources.md`：已有的分析到什么程度
>    - `report.html`：已有报告覆盖什么
>    - `evidence/` `mechanisms/`：已有的证据与机制梳理
> 2. 出一份「重合与差异对照表」：它的产出 vs 本任务书 §2.2 的 5 条主线 ——
>    哪些已经做过（可直接引用）· 哪些做了但不符合我们的分析要求（需重做）· 哪些完全没做（我们的增量）。
> 3. 产出统一落到本线的 `harness/` 目录（`doc/BaiZe-ISEDA2027/run/harness/`），
>    旧的 `report.html` / `analyze_harness_sources.md` 作为输入引用（给出路径）。
> 4. ⚠️ 不要删、不要改 `/nas_train/app.e0031982/harness/` 里的任何东西 ——
>    合并 = 在我们这边整合，不是去动它的目录。
> 5. 🚫 不要去启动它的 `loop.sh`（避免两个同类 loop 抢 token）。


---

## 1. H-A —— SWE-bench 横评

### 1.1 🔴 第 0 步（必做，先做）：可行性核查

在跑任何评测之前，逐条查清并报给运维：

| # | 查什么 | 怎么查 |
|:--|:--|:--|
| 1 | `harness/` 下有哪些 harness、各自版本 / 形态（CLI？插件？）| `ls -la` + 各自 `README` / `package.json` / `pyproject.toml` |
| 2 | 每个 harness 怎么启动、接什么模型（是否要 API key、能否接本地模型）| 读文档 + 试 `--help` |
| 3 | 模型可用性：本机能调哪些模型？（DeepSeek API？本地 vLLM？）| 实测一次最小调用 |
| 4 | SWE-bench 数据集：能否取到？取哪个子集？ | `swebench` 包 / HF 数据集；建议先 `SWE-bench Lite`(300) 或再抽 50 条 |
| 5 | 评测容器 / 沙箱：见下方「§1.1-bis 无 Docker 路线」 | `docker info`；不可用就按 §1.1-bis 改道 |
| 6 | 磁盘/时长预估：跑 N 条大概要多久、多少磁盘 | 按单条实测反推 |

🚫 第 0 步没通过之前，不许"假装跑了"或"用其他指标冒充 SWE-bench" —— 如实报告阻塞。

> 📦 §1.1-bis 无 Docker 路线 + 连通性测试 + sb-cli 合规 + 路线优先级 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：R1 unshare 沙箱路线已选定并实现，2100 条评测已完成，pypi/内网镜像可用，docker 不可用。需要时再读。

### 1.2 评测设计（核查通过后）

1. 统一口径（否则不可比）：
   - 同一子集（同一批 instance_id）
   - 同一模型（同一 provider / 同一 checkpoint）
   - 同一 timeout、同一 max turns / 预算
   - 同一评测脚本（SWE-bench 官方 harness）
2. 规模：先 20–50 条跑通全流程 → 报初步结果 → 再由运维决定是否放大。
3. 每个 harness 报：`resolve rate（主）` · `平均轮数` · `平均 token` · `平均墙钟` · `成本` · `失败模式分类`
4. 诚实性：失败的实例要保留日志；不许只报成功案例。

### 1.3 H-A 交付物
1. `harness/SWEBENCH_COMPARE.html`（自包含：口径 · 结果表 · 每个 harness 的失败模式 · 原始日志路径）
2. `harness/swebench_runs/`（原始预测 patch + 评测输出，不入库）
3. `MEMORY_HARNESS.md` 记录可复现命令

---
## 3. 约束

- 仓库与产物：分析产物写 `doc/BaiZe-ISEDA2027/run/harness/`（文本 md/html 入库）；
  原始仓库副本 / 大数据 / 日志不入库。
- 共享工作副本：`run/` 是多 agent 共享的（vision / pretrain / data 也在用）——
  🚫 不要 `git add -A`，只提交本任务的 `harness/` 与 `MEMORY_HARNESS.md`、`daily-memories-harness/`。
- git 规则：push 前先 `fetch` + `pull --rebase --autostash`（照抄 `baize_data_loop.sh` 的做法）。
- 资源：SWE-bench 评测可能很吃 CPU/磁盘/Docker —— 先报预算再跑，
  ⚠️ 注意 `.12`/`.29` 上另有训练在下（见 `AGENTS.md`），重 I/O 要避让。
- 🚫 不碰其他 agent 的任务书与记忆文件。
- 诚实：没跑通就写没跑通；没查到就写没查到。不要编造 API 行为。

---

## 4. 记忆管理

- `run/MEMORY_HARNESS.md` — 运行时状态（PHASE / WAITING / ERROR_COUNT / 看板 / 流水）
- `run/daily-memories-harness/$(date +%F).md` — 当日操作日志
- `run/harness/` — 分析报告与（不入库的）运行产物

启动恢复：读 `MEMORY_HARNESS.md` → 当日日志 → 判断下一步 → 执行 → 回写。



