# BAIZE_HARNESS_TASK.md

> 📛 **命名常驻规程（2026-10-25 用户令 · 所有线通用的报告纪律）**：**报告里一律写 `cline`，🚫 不许写 `cline-patched`**。
> - 同理：`ClinePatched` / `cline_patched` / `Cline-patched` 等任何变体**均禁止出现在报告正文、表格、图例、TL;DR、结论**里。
> - 理由（用户原话）：「以后在报告里不要写 cline-patched，就写 cline，否则容易造成误解。」——读者会误以为"只跑了被改造过的 Cline"，而实际差异只在接入层（装 CLI / 写 baseUrl / 参数大小写），原生工具循环未改。
> - **代码/脚本/配置里的标识符不改**（`cline_patched.py`、`terminalbench.agents.cline_patched:ClinePatched`、`jobs_cline-patched/` 是真实路径，改了会跑不起来）；**但报告里凡引用必须转写成 `cline`**。
> - 如需交代接入层适配，放在**附录或脚注**写一次即可，正文一律 `cline`。

### 🚨 运维令 · 2026-10-25 08:2x（**排查并修复 claude-code / hermes / deepseek 通过率 0% 的适配器 bug；修复期间这三个停跑**）· 用户直令 · 最高优先
> 用户原话：「安排 harness 去排查和修复导致 claude-code/hermes/deepseek 通过率为0的适配器 bug，修复期间这三个就不要跑了。同时汇报其它四个 harness 截止目前各自的通过率（已跑完的部分）。」
> **① 立即动作：停掉这三个（只停这三个）**
> - **停**：`claude-code`（26/87 done，**0 pass**）、`hermes`（FIN 50/87，**0 pass**，37 err）、`deepseek-harness`（FIN 50/87，**0 pass**，37 err）。
> - **继续跑**：`cline-patched`、`codex`、`opencode`、`pi` —— 🚫 不许 kill / 重启 / 改动它们的容器与 launcher。
> - 停法：按 `jobs_*` 目录名 / `--project-name` 精确匹配，**只 SIGTERM 这三路的 harbor 进程与容器**，逐个确认再停。
> - 停完立刻回报：停了哪些 PID / 容器 + 四个存活 harness 未受影响（贴 `ps` / `docker ps` 证据）。

> **② 排查（先定位再动手，禁止盲改）** — 三者症状不同，必须分开归因
> | harness | 症状 | 待验假设 |
> |:--|:--|:--|
> | `claude-code` | 26 done / **0 pass**，最慢（~1.7/h），有 err | ① CLI 未进容器/PATH；② 非交互模式下只输出计划不执行；③ AgentTimeoutError 占主导 → 未产出 patch；④ 工具调用协议与 harbor 不匹配 |
> | `hermes` | FIN 50 / **0 pass**，**37 err**（RuntimeError/NonZeroAgentExit） | 适配器入口/退出码处理错 → 一起步就非零退出 |
> | `deepseek-harness` | FIN 50 / **0 pass**，**37 err** | 同 hermes；另查模型名/endpoint/base_url 是否配错（可能没连上模型就"成功"返回空） |
> **必查证据（贴原文，不许只写结论）**
> 1. **`verifier/reward.txt` 是否真被写入**——0 pass 可能是 verifier 没跑/没找到 patch，而非答错；与 `cline-patched` 的 pass 样本对比文件结构。
> 2. **agent 是否真调用了模型**：抓失败 trial 的 `agent.log`/`session.json`/trace，确认有 LLM 请求、有 tool call、token>0。
> 3. **37 err 完整堆栈**：`RuntimeError`/`NonZeroAgentExit` 逐条归类合并计数，贴前 3 条 traceback。
> 4. **容器内 CLI 可用性**：`docker exec` 进失败容器验 `which <cli>` / `--version`。
> 5. **时间线**：Gen7 pilot 里 hermes/deepseek **就是 0/5 且 no errors**、claude-code 0/5+3/5 err ⇒ **这是从 pilot 就没修的老 bug，不是本轮新增**，写进结论，别再"发现 0%"。
> 6. **源码 diff**：读 harbor `terminalbench.agents.{hermes,deepseek_harness,claude_code}` 三个类 + 一个已知可用的（cline/codex/pi），指出差在哪几行。

> **③ 修复（最小验证闭环）**
> - 修完**不许直接上 87 题**：先跑 **oracle 已知可解的 5 题**（从 R473 oracle 15/15 里那 11 道可解题中挑）做 smoke，**判据 = 至少 1 道 pass**；0 pass 不算修好，回去继续查。
> - smoke 过再各跑 5 题确认稳定；仍 0 pass ⇒ 判定「未修复」+ 写清卡点，不许含糊过关。
> - 三个**逐个修、逐个验**（不许三个一起改一起测，要能归因）。
> - 🚫 不许放宽 verifier / 改 reward 口径 / 跳断言来"让它通过"；🚫 不许改另外四个 harness 的任何配置。

> **④ 同时汇报：其它四个 harness 的通过率（已跑完部分）**
> 用 `verifier/reward.txt` 口径，逐 harness 给：**done / pass / 通过率 / err 数 / 预计完成时间**，标注「**部分结果，非最终**」。
> R490 快照如下，**你要用自己最新实测覆盖它，不许照抄**：
> cline-patched 61done/34P=55.7% · opencode 56/30=53.6% · codex 39/19=48.7% · pi 66/29=43.9%
> - 另给四路两两 **McNemar 初步配对**（样本不足就写「暂不出」）。
> - ⚠️ codex 已知 err 偏高：**标注但不要停**（用户只要求停那三个）。

> **⑤ 产出**
> - `reports/report_harness_adapter_0pass_rootcause_zh.html`（中文 HTML 自包含）：症状表 → 逐 harness 根因 → 证据（日志片段/traceback）→ 修复 diff → smoke 结果 → 未修复写卡点。
> - 补丁落 `run/harness/terminalbench/`（保留原文件 + 说明改了什么）。
> - `MEMORY_HARNESS.md` 首部新块 + `run/daily-memories-harness/2026-10-25.md`；commit 前缀 `harness adapter-fix:`。
> - 🚫 **SWE-bench Verified 下载不停**；TB 四个存活 harness 也不停。

> **🚫 铁律**
> - **只停这三个**：claude-code / hermes / deepseek-harness；其它四个一根汗毛都不许动。
> - 停之前**先记录**各自 batch 目录、done 数、已跑 trial 列表；已完成结果**一律保留落盘不许删**（修好要复跑对照）。
> - 🚫 不许把「0 pass」直接归因为「模型不行」——先证明 agent 真调用了模型并产出 patch。
> - 🚫 不许编造/估算通过率；一律 `reward.txt` 实测，取不到写「未取到 + 原因」。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。
### 📦 §运维指令·2026-10-24 16:3x（TB 7 并发 + 后台下载 SWE-bench Verified 容器）**已闭合**（R480 已交付体积估算、下载脚本与后台启动）→ 原文归档 → `run/ARCHIVE_OPERATOR_HARNESS.md`。**结论**：SWE-bench Verified=500 题非 Lite；去重后 ~30–60GB（sum raw ~575GB）；Docker Root Dir /data 6.3T free 够；分批 50 + 断点续跑 + 进度文件 `harness/swebench_verified_pull_progress.txt`；实测瓶颈=**Docker Hub 匿名限速 100 manifest/h（共享 IP）**，~20/h，0 failed。需要时再读。

> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_HARNESS.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。
### 📦 §补充令·2026-10-24 09:2x（92.25 代理配 dockerd）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：daemon.json proxies 已配 172.19.92.25:13128，docker pull 实测成功，89 张 TB 镜像已补齐。需要时再读。
### 📦 §运维指令·2026-10-24 09:0x（7 并发 + 15/89 答疑）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：TB=89 题全量，7 并发已于 R479 启动(7×87)，Q&A 见 MEMORY。需要时再读。



### 📦 §运维指令·2026-10-23 22:1x（npm install -g 代理安装）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：Gate 7/7 已达成(R466)，codex+claude-code 均已 npm install -g 成功。需要时再读。
### 📦 §运维指令·2026-10-23（分阶段落盘写报告）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：H-B 7way 上下文压缩报告已分阶段落盘并交付。需要时再读。
### 📦 §运维指令·2026-10-23（📄 比较7个harness上下文压缩机制→HTML报告）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：report_harness_context_compression_7way_zh.html 已交付。需要时再读。
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



