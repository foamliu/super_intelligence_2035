# BAIZE_HARNESS_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_HARNESS.md` / `daily-memories-harness/` / `harness/`（产物）。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_HARNESS.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序自主推进。
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

### 🆕 运维指令 · 2026-10-05（晚 · ✅ 批准「扩 300」= **先扩 kimi**；+ 环境隔离纪律）· 高优先 · **已批准**

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


### 🆕 运维口径 · 2026-10-05（**你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测**）

> **定位（运维 2026-10-05 13:2x，跨线）**：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（见 `baize_data_loop.sh:114-120` / `baize_harness_loop.sh:106-116`）——**目的是给内网网关鉴权**（不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ **你（agent）会话里每条命令都继承了「无代理」env。**
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 **`Network is unreachable`（Errno 101）/ http `000`** 是**预期现象**：🚫 **不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题**——**别把它写进结论**。
> 🔧 **正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）**：**凡访问外网的那一条命令，自己显式带上代理**（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都**不要**带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ **同机反证**：`run/harness/r1_eval.py:144-148` 正是**显式钉 proxy + 阿里云索引**，所以**同一台 `.29`** 上 pip 装包一直成功；relay 侧 git 也通（`run/ops/outbox.md` RUN_ID 28：「外网 无 proxy=FAIL / 有 proxy=OK」，内网网关两种都 200）。
> 🚫 **装包别动共享 py310 env**（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

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

### 📉 记忆维护规程（2026-10-03 运维新增，**硬性**）
> 理由：`MEMORY_*.md` **每次唤醒都被 agent 全文读取** → 越大越烧 token。本线 `MEMORY_HARNESS.md` ≈ **18KB（当前未超标，保持即可）**。
- **上限**：本线 `MEMORY_HARNESS.md` 控制在 **≤ 32KB**；一旦超限即执行滚动。
- **滚动**：把**较早的巡检条目**（保留最近 ~20 条）**追加**到 `daily-memories-harness/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 ③ 「运维问答」④ 最近 ~20 条。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---



| 项 | 当前值 |
|:---|:---|
| **当前指令** | 🎯 **（2026-10-02 首启）两条线，按序做**：<br>**① H-B 源码分析（先开始）** —— 分析 `/nas_train/app.e0031982/harness` 下各 harness 的源码，**从 cline 开始**，产出**自包含 HTML 报告**。分析主线见 §2。<br>**② H-A SWE-bench 横评** —— 用 **SWE-bench** 评测几个 agent harness（cline / opencode / deepseek harness 等）并**对比**。⚠️ **先做可行性核查（§1.1），再定规模**，不要一上来跑全量。<br>🚫 **两条铁律**：<b>不许猜</b>（源码结论必须贴文件+行号原文）；<b>每个结论必须可复现</b>（命令+输出）。 |
| **优先级覆盖** | **H-B（源码分析）> H-A（SWE-bench）**；<br>H-A 只在**环境与数据集核查通过后**才进入实跑。 |
| **状态索取** | `<无>`（若运维写入具体问题，本轮**先答该问题**再干活，答案写进 `MEMORY_HARNESS.md` 顶部「运维问答」区） |
| **暂停标志** | `<无>`（若写入 `STOP`，本轮**只更新记忆、不做任何动作**，然后退出） |

---

## 📊 进度快照（**每次唤醒必须更新**，供远程巡检）

> 固定格式写在 **`MEMORY_HARNESS.md` 最顶部**，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ **`WAITING` 只写在 `MEMORY_HARNESS.md` 的顶部单独一行**
（`baize_harness_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
**绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行** —— 否则会误触发 30 分钟长睡。

**运维巡检方式**：外部运维 `git pull` 读 `MEMORY_HARNESS.md` 顶部 + `harness/` 下的报告即可，**不需要登录服务器**。

---

## 0. 任务概述

**目的**：横向理解「agent harness」这一类系统 —— **它们的工程实现差异**，以及**它们在真实软件工程任务上的能力差异**。

| 线 | 内容 | 产出 |
|:--|:--|:--|
| **H-B** | **源码分析**（从 **cline** 开始） | `harness/<name>_SOURCE_ANALYSIS.html`（自包含） |
| **H-A** | **SWE-bench 横评**（cline / opencode / deepseek harness 等） | `harness/SWEBENCH_COMPARE.html` + 结果表 |

**代码位置**：`/nas_train/app.e0031982/harness/`

> ## 🔍 **重要：该目录下已存在一条「同类研究线」（运维 2026-10-02 指示：可以合并）**
>
> 首次勘察（RUN_ID 5）发现 `/nas_train/app.e0031982/harness/` 里**不只有 5 个 harness 源码**，还有：
> ```
> claude-code/  cline/  codex/  deepseek-harness/  opencode/     ← 5 个 harness
> loop.sh                                                          ← 它自己的 loop
> MEMORY.md                                                        ← 它自己的状态文件
> daily-memories/  evidence/  mechanisms/                          ← 它自己的记忆与证据目录
> analyze_harness_sources.md   (11.8 KB)                           ← 已有源码分析文档
> report.html                  (24.6 KB)                           ← 已有报告
> ```
> **文件日期为 Sep 4 – Sep 15**，**早于本线创建（Oct 2）**，**非本线产物**。
>
> ### ✅ 运维确认 + 指示（2026-10-02）
> - **运维确认**：**9 月初确实下发过一次「5 个 harness 比较」的任务**（就是这条线）；
> - **⚠️ 它的 `loop.sh` 早已停掉** → **不会与我们冲突**，也**不要**去重启它；
> - **指示：可以合并**。
>
> **→ 所以它的产物是「纯输入」**：`analyze_harness_sources.md` / `report.html` / `evidence/` / `mechanisms/`
> 都是**可复用的既有素材**，但**其结论需要按我们的 5 条主线重新审视**（它的分析角度可能不同）。
>
> **你要做的（H-B 开始前先做）**：
> 1. **先把这条既有线的家底摸清**（**只读**，不要改动它）：
>    - `MEMORY.md`：它的 PHASE / 已完成 / 产出
>    - `loop.sh`：它跑什么、是否还在运行（`pgrep -af 'harness/loop.sh'`）
>    - `analyze_harness_sources.md`：已有的分析**到什么程度**
>    - `report.html`：已有报告**覆盖什么**
>    - `evidence/` `mechanisms/`：已有的证据与机制梳理
> 2. **出一份「重合与差异对照表」**：它的产出 vs 本任务书 §2.2 的 5 条主线 ——
>    **哪些已经做过（可直接引用）· 哪些做了但不符合我们的分析要求（需重做）· 哪些完全没做（我们的增量）**。
> 3. **产出统一落到本线的 `harness/` 目录**（`doc/BaiZe-ISEDA2027/run/harness/`），
>    **旧的 `report.html` / `analyze_harness_sources.md` 作为输入引用**（给出路径）。
> 4. ⚠️ **不要删、不要改** `/nas_train/app.e0031982/harness/` 里的任何东西 ——
>    **合并 = 在我们这边整合，不是去动它的目录**。
> 5. 🚫 **不要**去启动它的 `loop.sh`（避免两个同类 loop 抢 token）。


---

## 1. H-A —— SWE-bench 横评

### 1.1 🔴 第 0 步（**必做，先做**）：可行性核查

**在跑任何评测之前**，逐条查清并**报给运维**：

| # | 查什么 | 怎么查 |
|:--|:--|:--|
| 1 | `harness/` 下**有哪些 harness**、各自**版本 / 形态**（CLI？插件？）| `ls -la` + 各自 `README` / `package.json` / `pyproject.toml` |
| 2 | 每个 harness **怎么启动**、**接什么模型**（是否要 API key、能否接本地模型）| 读文档 + 试 `--help` |
| 3 | **模型可用性**：本机能调哪些模型？（DeepSeek API？本地 vLLM？）| 实测一次最小调用 |
| 4 | **SWE-bench 数据集**：能否取到？取哪个子集？ | `swebench` 包 / HF 数据集；**建议先 `SWE-bench Lite`(300) 或再抽 50 条** |
| 5 | **评测容器 / 沙箱**：见下方「§1.1-bis 无 Docker 路线」 | `docker info`；**不可用就按 §1.1-bis 改道** |
| 6 | **磁盘/时长预估**：跑 N 条大概要多久、多少磁盘 | 按单条实测反推 |

🚫 **第 0 步没通过之前，不许"假装跑了"或"用其他指标冒充 SWE-bench"** —— 如实报告阻塞。

### 1.1-bis ⚠️ **无 Docker 路线（运维 2026-10-02 明确：公司内网无法 `docker pull`）**

> **已查实的事实（官方仓库原文）**：
> - SWE-bench 官方 harness **默认绑 Docker**（README：「SWE-bench uses **Docker** for reproducible evaluations」；
>   2024-06-27 起改为「**fully containerized** evaluation harness using Docker」）。
> - **官方唯一的"无 Docker"本地后端是 Modal（云）**：`--modal true` —— 但要外网。
> - **`SWE-ReX`**（SWE-agent 家族）支持 **local / remote / Docker / Modal 等后端**，
>   原文：「…executed **locally** or remotely in Docker containers, AWS remote machines, Modal, or something else…」+
>   「Support a broad range of platforms, **including non-Linux machines without Docker**」。
> - 🚫 **`SWE-MiniSandbox`** —— **在官方仓库中未找到该名称**。**请自行查证**（有就给 URL + 它解决什么）；**查不到就写"未找到"，不要猜**。

> ### 🔑 关键认知：Docker 在这里**不只是"隔离"，更是"per-instance 依赖环境的分发机制"**
> 每个 instance 一个**预构建镜像**，装着**该 repo 在该 `base_commit` 下正确的依赖**。
> **换掉"隔离"很容易**（bwrap / nsjail / local）；**换掉"环境供应链"很难**。

---

#### ⭐ 第 0 步（**先做**）：**连通性测试 —— 分清「事实」与「推测」**

> ### ⚠️ 运维更正（2026-10-02）：**github 是可达的**
> **`.29` / `.12` 都能从 github `git clone` 代码** —— **本任务线用于发布任务的仓库本身就在 github 上**，
> 所有 agent 的 `git fetch/pull/push` **一直正常**。
> → **不要把"github 不可达"当作前提**（那是把"爬取层面不可达"错当成了"git 不可达"）。
>
> ### 🔑 还必须分清另外两件**被我混淆过**的事
> | | 实际状态 | 依据 |
> |:--|:--|:--|
> | **`docker` 命令可用吗** | ❌ **不可用**（`docker info` → `NOT AVAILABLE`）| **实测（RUN_ID 5）** |
> | **能不能 `docker pull`** | ❓ **从未测过** | **此前只是推测，不要当事实** |
> → **"没装 Docker" 与 "装了也 pull 不到镜像" 是两件完全不同的事**，**都要实测**。

**要测的清单（逐条记 `http_code` 或错误原文）**

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

**判定（据此选路线）**
| 测试结果 | 结论 |
|:--|:--|
| **B（pypi/内网镜像）通** | ✅ **E′ 完全可行** —— `git clone`（已成立）+ 装依赖 → 不需要 Docker |
| **C 里能看到内网 registry 或 `docker pull` 成功** | ✅ 原路可行（最省事） |
| **D 通（且合规批准）** | ✅ sb-cli 可用 → 给最强 harness 拿标准分数 |
| **B/C/D 全不通** | ⚠️ 才需要考虑自建沙箱 / 换口径 |

#### 🚫 关于 sb-cli 的合规红线（**必须先确认，再上传任何东西**）

`sb-cli` 的工作方式是 **把 `predictions.json`（含 `model_patch`）上传到 SWE-bench 云端评测**。
- ✅ **缓解**：patch 针对的是**开源 repo**（django / sympy 等），**不是我们的私有代码**。
- ⚠️ **但**：**这是把代码片段发到外部服务** —— **公司政策可能不允许**。
- **→ 要求**：**上传前必须由运维/合规确认**。**未经确认，不得使用 sb-cli 上传任何东西。**
- 📌 另：sb-cli 需要**邮箱 + 邮件验证码**注册（`sb-cli gen-api-key <email>` → `verify-api-key <code>`），
  且**有配额**（`sb-cli quota <subset> <split>`）—— 这两条也要先记下来。

---

#### 路线优先级（**连通性测试之后**据此执行）

1. **若 `docker pull` 实测可行**（或内网有 Harbor 镜像代理）→ **原路最省事**（写清证据）。
2. **⭐ 路线 E′（推荐）：只挑 1–3 个高频 repo 的 instance**
   - 统计 `SWE-bench Lite`(300) 的 **repo 分布** → 挑**占比最高的 1–3 个 repo**。
   - **`git clone` 该 repo @ `base_commit`**（✅ github 已确认可达）+ **装该 repo 的依赖**（待验 pypi/内网镜像）。
   - 几个 harness 跑**同一批 instance** → **公平横评成立**。
   - ⚠️ **报告里必须标注**：这是**内部横评口径**，**不是标准 SWE-bench 分数，不能与 leaderboard 直接比**。
   - 💡 **加强版**：`SWE-bench` 仓库里带着**每个 instance 的镜像构建规格**（`swebench/harness/`）——
     **可直接照规格 build env**，完全绕开 Docker Hub。
3. **路线 sn（若 D 通 且 合规批准）：`sb-cli`** —— 给最强 harness 拿**与 leaderboard 可比**的标准分数。
4. **备选：自建轻量沙箱** —— `conda env per repo` + **`bwrap` / `nsjail`**（只替代"隔离"职责）。
5. **若以上都不可行** → 明确写"**H-A 在受限前提下无法按标准口径进行**"，
   并给**替代评测口径**建议，**但不得把它称作 SWE-bench 结果**。







### 1.2 评测设计（**核查通过后**）

1. **统一口径**（否则不可比）：
   - **同一子集**（同一批 instance_id）
   - **同一模型**（同一 provider / 同一 checkpoint）
   - **同一 timeout**、**同一 max turns / 预算**
   - **同一评测脚本**（SWE-bench 官方 harness）
2. **规模**：**先 20–50 条**跑通全流程 → 报初步结果 → **再由运维决定是否放大**。
3. **每个 harness 报**：`resolve rate（主）` · `平均轮数` · `平均 token` · `平均墙钟` · `成本` · `失败模式分类`
4. **诚实性**：失败的实例要**保留日志**；**不许只报成功案例**。

### 1.3 H-A 交付物
1. `harness/SWEBENCH_COMPARE.html`（自包含：口径 · 结果表 · 每个 harness 的失败模式 · 原始日志路径）
2. `harness/swebench_runs/`（原始预测 patch + 评测输出，**不入库**）
3. `MEMORY_HARNESS.md` 记录**可复现命令**

---
## 3. 约束

- **仓库与产物**：分析产物写 `doc/BaiZe-ISEDA2027/run/harness/`（**文本 md/html 入库**）；
  **原始仓库副本 / 大数据 / 日志不入库**。
- **共享工作副本**：`run/` 是**多 agent 共享**的（vision / pretrain / data 也在用）——
  🚫 **不要 `git add -A`**，只提交本任务的 `harness/` 与 `MEMORY_HARNESS.md`、`daily-memories-harness/`。
- **git 规则**：push 前**先 `fetch` + `pull --rebase --autostash`**（照抄 `baize_data_loop.sh` 的做法）。
- **资源**：SWE-bench 评测可能**很吃 CPU/磁盘/Docker** —— **先报预算再跑**，
  ⚠️ 注意 `.12`/`.29` 上另有训练在下（见 `AGENTS.md`），**重 I/O 要避让**。
- 🚫 **不碰**其他 agent 的任务书与记忆文件。
- **诚实**：**没跑通就写没跑通**；**没查到就写没查到**。**不要编造 API 行为。**

---

## 4. 记忆管理

- `run/MEMORY_HARNESS.md` — 运行时状态（PHASE / WAITING / ERROR_COUNT / 看板 / 流水）
- `run/daily-memories-harness/$(date +%F).md` — 当日操作日志
- `run/harness/` — 分析报告与（不入库的）运行产物

启动恢复：读 `MEMORY_HARNESS.md` → 当日日志 → 判断下一步 → 执行 → 回写。



