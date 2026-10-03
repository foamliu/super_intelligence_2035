# BAIZE_HARNESS_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_HARNESS.md` / `daily-memories-harness/` / `harness/`（产物）。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序自主推进。
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



