# BAIZE_HARNESS_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_HARNESS.md` / `daily-memories-harness/` / `harness/`（产物）。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序自主推进。

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

**代码位置**：`/nas_train/app.e0031982/harness/`（先 `ls` 看清有哪些 harness、各自是什么形态）

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
| 5 | **评测容器**：SWE-bench 官方评测需要 **Docker**（每实例一个容器）→ 本机 Docker 可用吗？| `docker ps` / `docker info`；**若不可用，明确写"不可用"并给替代方案** |
| 6 | **磁盘/时长预估**：跑 N 条大概要多久、多少磁盘 | 按单条实测反推 |

🚫 **第 0 步没通过（尤其 5）之前，不许"假装跑了"或"用其他指标代替 SWE-bench"** —— 如实报告阻塞。

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



