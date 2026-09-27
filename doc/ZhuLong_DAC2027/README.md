# ZhuLong (DAC 2027) — 实验执行规格 / Experiment Execution Spec

本文件面向**执行实验的 agent 与操作人**。它规定：要测什么、每个配置怎么配、每步必须记录什么、
哪些红线不能碰、以及交付前怎么自检。**在动手前请完整读一遍。**

---

## 0. 权威边界（Authority）

| 角色 | 路径 | 说明 |
|---|---|---|
| **论文权威树** | `ZhuLong_DAC2027/ZhuLong_DAC2027/` | 唯一可编辑的 LaTeX 树。`main.tex` → `DAC2027/{0..8}_*.tex` |
| **理论权威** | `Grounding/ICML2028/` | L1–L4 层级、grounding gap、$\Phi$ 的正式定义。**任何理论表述冲突以它为准** |
| 非权威 | `ZhuLong_ASPDAC2027/` | 旧稿，只读参考，**不要改动** |
| 非权威 | 任何 `*.orig` / 顶层散落副本 | 备份残留，**不要改动、不要引用** |

**仓库性质**：这是**纯 LaTeX 仓库，不含 harness 代码**。harness（提供 `search_apis` /
`get_api_details` / `run_code` 三个 MCP 工具的 agent 运行时）在别处，本文档只描述如何配置它。

### 0.1 术语表（必须逐字沿用，不得自造同义词）

| 符号 | 含义 | 论文中的角色 |
|---|---|---|
| $\mathcal{K}$ | 冻结的静态先验（L1–L3，编码于 LLM 参数） | S3 变的就是它 |
| $\Omega$ | 观测通道（似然）：把环境事实返回给 agent | S1 变的就是它 |
| $\Phi$ | 信念更新：$b_t \mapsto b_{t+1}$ | S2 变的就是它 |
| L1–L4 | 知识层级；**L4 必须"被读到"而非"被回忆到"** | §4 全篇 |
| ICL-type autonomous agent | 无显式后验、靠 in-context learning 维持信念状态的自主 agent | `3_design.tex` §Overall Architecture 首段定义 |

---

## 1. 本任务要交付什么

把论文里所有 `[TBD]` 替换为**实测值**。清单见 §6——**共 6 张表、56 个 `[TBD]` 占位（分布在 30 行）**。
不允许留臆造值；未测完的必须显式标注为 provisional。

---

## 2. 冻结项（Frozen setup — 所有配置共用，不得变动）

除非某一行的定义明确要求改变该项，以下全部冻结：

- **数据集**：`EDA-Eval-PyAether`，158 个 PyAether 任务（见 `5_bench.tex` 的两个 Dataset 小节）。
  任务三要素 = 自然语言 prompt + 函数签名 + 断言测试代码。
- **通过判据**：生成的代码在 PyAether sandbox 中**无错误执行**且**全部断言通过**
  （见 `5_bench.tex` §Evaluation Protocol）。指标 `Pass@1 = 通过任务数 / 158 × 100%`。
- **超时**：单次执行 **2500 秒**（见 `6_exp.tex` §Benchmark and Evaluation Protocol）。
- **单 trace 原则**：一个任务只跑一条 trace，agent 可以在该 trace 内通过 $\Phi$ 反复迭代，
  **但任务绝不跨 trace 重启**（同上节）。
- **重复次数**：每个配置**统一 5 次独立运行**（已取消分层），每次**重排任务顺序**且使用**全新 agent context**
  （同上节）。准确率报告为 **mean Pass@1 $\pm$ std**（不是单次值）。**完整报告口径见 §4.1。**
- **主 backbone**：`DeepSeek-V4-Pro`（见 `6_exp.tex` §LLM Backbones）。
  **只有 S3（`tab:llm-comparison`）才换 backbone。**
- **检索默认配置**：name+description 索引的向量检索（见 `6_exp.tex` §Baselines and ZhuLong Variants）。
  只有 S1 才显式改变该索引保真度。
- **反作弊 `PreToolUse` hook**：**必须全程启用且在所有实验臂之间完全一致**（它属于冻结设置，
  不是被消融的变量）。详见 §3.4 与 §3.5。

> ⚠️ `6_exp.tex` 的中文注释里曾残留"最多 2 轮重新规划 / 最多 3 次完整运行"（废弃旧协议，
> 与"单 trace、不跨 trace 重启"矛盾）——**已修正**。若你仍看到该说法，说明改动被回退，
> 请以本节为准并把它改回来。**本任务一律以 §2 为准。**

---

## 3. 各配置怎么配（关键技术结论）

### 3.1 MCP handler 里实现（**观测内容类**消融；零风险，不碰 Cline 源码）

三个工具是**你们自己的 MCP server**提供的（见 `3_design.tex` §Overall Architecture），所以绝大多数消融就是改你们自己的返回逻辑：

| 消融 | 在 handler 里怎么做 |
|---|---|
| 关执行器（`ZhuLong w/o Sandbox`、RAG baseline） | **不注册** `run_code`，或注册后直接返回"工具不可用" |
| 关检索（`ZhuLong w/o Retrieval`） | 不注册 `search_apis` / `get_api_details` |
| 回读保真度 (N)/(B)/(F) | 改 `run_code` 的**返回负载**：(N) 无返回/仅"已执行"；(B) 仅 pass/fail；(F) stdout + 异常栈 + 逐断言结果 + 状态查询（默认） |
| $\Omega$ 保真度阶梯 (L)/(H)/(H+E) | 改 `search_apis` 的**索引与排序质量**：仅 API 名 → 加描述/BM25/缩写展开/同义词重定向 → 再加离线自探索结论 |
| **$\Phi$ 的 $k$ 预算** | 可在此计数，但**推荐改用 §3.2 的 hook 实现**（理由见下） |
| $\Phi$ lagged | 见 **§3.6**：第 $n$ 次回读返回第 $n{-}1$ 次执行产生的状态（定义须逐字实现） |

**分工原则**：

- **观测内容类**消融（回读保真度 (N)/(B)/(F)、$\Omega$ 索引保真度）→ **只能在 handler 里做**，因为它本质是"返回什么内容"。
- **调用次数类**消融（$\Phi$ 的 $k$ 预算）→ **推荐用 hook 做**。这样 `run_code` 的工具实现**在所有臂中逐字不变**，
  变的只是框架层的策略；同时复用你们**已在生产验证**的反作弊 hook 链路，消融更干净、更易辩护。

### 3.2 hook 路线：你们的评测框架**已经在用**（推荐用于 $\Phi$ 预算）

**已确认事实**（官方文档 + `cline-main@4.1.17` 源码）：

- 你们的评测框架**已经应用一个 `PreToolUse` hook 防作弊** → 说明"在工具边界拦截调用"这条链路**在生产中已验证可用**，
  不需要再做可行性验证。
- **hooks 目录**（官方文档 `getting-started/config`，以此为准）：
  - 全局 `~/.cline/hooks/`
  - 兼容路径 `~/Documents/Cline/Hooks/`
  - 项目级 `.cline/hooks/`
  - 另有 CLI 参数 `--hooks-dir <path>`（`apps/cli/src/commands/program.ts:73`）、
    及对应环境变量 `CLINE_HOOKS_DIR`（`apps/cli/src/main.ts:796-797`），
    用于**额外**追加一个 hooks 目录。
  > ⚠️ 目录写错时 hook 会**静默不生效**。请在实际框架里确认反作弊 hook 装载自哪个目录，
  > 并在 §8 的冒烟验证中确认它真的被加载。
- **适用范围**：官方文档明确 **hooks/plugins 目前只适用于 SDK / CLI / Kanban，不适用于 VS Code 与 JetBrains 扩展**。
  → 这解释了 `local-runtime-bootstrap.ts:396-397` 的宿主差异：**批量评测必须走 CLI/SDK 路径**，否则 hook 不生效。
- hook 的 `cancel` 是被持续维护的一等能力（CHANGELOG 4.1.17：*"wait for `PostToolUse` hooks so their output and
  `cancel` control are honored"*）。

文件式 hook 事件名（`hook-file-config.ts:17-43`）：
`PreToolUse`、`PostToolUse`、`PreCompact`、`TaskStart`、`TaskResume`、`TaskCancel`、`TaskComplete`、
`TaskError`、`UserPromptSubmit`、`SessionShutdown`。

**$\Phi$ 预算的做法**：新增一个 `PreToolUse` hook，计数同一 trace 内的 `run_code` 调用；
超限时返回 `{"cancel": true, "errorMessage": "[PHI-BUDGET-EXHAUSTED] ..."}`。

> 其余 Cline 原生机制（备用）：工具策略 `policy.enabled === false` → `agent-runtime.ts:1750-1751` 自动 skip；
> 任务级硬上限 `maxIterations`（`shared/src/session/runtime-config.ts:56`）；原生结束原因枚举
> `completed`/`max_iterations`/`aborted`/`mistake_limit`/`error`（`shared/src/agents/types.ts:546-559`）；
> 空转检测 `core/src/runtime/safety/loop-detection.ts`。

### 3.3 $\Phi$ 预算的语义约束（**最容易做错，务必按此执行**）

- 预算约束的是"agent **能执行/能观测多少次**"，**绝不是**"agent **何时必须提交**"。
- 实现方式是**在工具边界拒绝调用**（agent 收到 error 后继续自主运行），
  **严禁**中断 trace、改写任务、或以任何方式逼迫/提示 agent 提前提交。
- 理由：一旦改变终止行为，测到的就是"人为干预"而非 $\Phi$。
- **必须同时报告 `Converged (%)`**（见 §4），否则紧预算造成的提前停止会被误读为"收敛"。

### 3.4 多重 hook 的合并语义（必读，否则归因会错）

源码 `sdk/packages/core/src/hooks/hook-file-hooks.ts:129-160`：

- `cancel` 是**按 OR 合并**：`cancel: current.cancel === true || next.cancel === true` →
  **任一 hook 取消，该次调用即被拒绝**。
- `cancelReason` 与 `context` 是**用换行符拼接**的。

由此得到三条硬性要求：

1. 你们的**反作弊 hook 与 $\Phi$ 预算 hook 会共存且同时生效**——不会互相覆盖，这是好事。
2. 但**拒绝原因文本会被拼接**，从而**无法区分是哪条 hook 拒的**。因此预算 hook 的错误信息
   **必须带唯一前缀**（如 `[PHI-BUDGET-EXHAUSTED]`）；否则 trace 级归因、`Converged (%)`
   与失败分析都会错标。
3. 每条 trace 必须记录**被哪条 hook 拒绝**（见 §4 的 `denied_by_hook` 字段）。

### 3.5 反作弊 hook：必须冻结、必须验证、必须披露

**作用**（简述；**具体规则请直接读 hook 源码**，本文件不复述）：工具白名单（拦 `run_commands`、
`search_codebase` 等），并把文件读写限制在一个新建的空目录内，以防泄题。

**为什么这是红线而不是细节**：历史上**未做隔离时，pure LLM 曾多次得到 >98\%**。
也就是说——**hook 一旦静默失效，整批数据会瞬间变成"抄答案"的成绩，而且表面上完全正常**。
> 该分数是**内部信息，不得写入论文**。论文只做定性说明（"答案可从环境中获得"），
> 不带数字、也不引入额外的复现说明负担——见 §5 红线 8。

因此：

- 它必须在**所有实验臂之间完全一致**，绝不能只在一个臂里启用/关闭。
- **每个批次开跑前必须做 canary 验证**（见 §8）：故意触发一次应被拒绝的调用，确认它真的被拒。
- 被它拒绝而失败的 trace **不能**与"能力不足"的失败混在一起统计，须按 §4 字段单独归类。
- 论文 §6 已写明该隔离；**若你改了 hook 的任何规则，必须同步更新论文那句话**。

### 3.6 `Φ lagged` 档的精确定义（必须逐字实现）

**定义（滞后 = 1 次执行）**：设一条 trace 内的 `run_code` 调用依次编号 $1,2,\dots,n$。
第 $n$ 次调用返回的状态 = **第 $n{-}1$ 次调用产生**的状态；第 $1$ 次调用返回
"尚无先前状态"的占位说明（占位，不是空错误）。

**等价说法**：agent 在决定第 $n$ 次执行时，手上最新的观测是第 $n{-}2$ 次执行的结果——
即它**永远不会在执行下一步之前看到上一步的结果**。

**实现要求**：

- 在 handler 内维护"上一次执行结果"的**单槽缓冲**（L=1 故用单槽，不是队列）。
- **必须**在 trace 元数据中记录每次回读实际报告的来源序号 `reported_call_index`，
  使审计者可验证滞后量恰好为 1（见 §4）。
- 其余一切不变：`run_code` 照常执行、执行次数**不设上限**、LLM 与 $\Omega$ 不变。

**为什么取 L=1 而非 L=2**：

- L=1 是**信息损失最小**的滞后（只有第 1 次回读没有状态），因此把"陈旧"与"信息量减少"
  这两个因素分离开；更大的 L 会额外丢掉开头的观测，使该臂与更小的 $k$ 臂难以区分。
- L=1 已经是一次**范畴性**违反，而非边际扰动：agent 从此**始终**在不知道上一步结果的情况下
  决定下一步，闭环被系统性地切掉一步。若 L=1 测不出效应，再上 L=2，并在正文**如实报告 L=1 无效应**。

**为什么滞后按 `run_code` 次数计，而不能按轮次或墙钟**：

- 只有 `run_code` 调用是规范意义上的离散事件；该 agent 没有"轮次"（见 §3.3）。
- 设计状态**只在 agent 执行时**改变，所以"设计动态的时间尺度"在操作上就等于"执行间隔"。
  按墙钟计会把机器速度混进来，按模型轮次计会把推理长度混进来。

**为什么这一档不可删，且与 $k$ 轴不可互相替代**：

- $k$ 轴变的是**证据的量**，lagged 变的是**证据的时效**，二者是不同的失效模式。
- §4 原则 3 的第一句是"$\Phi$ 的更新率必须超过 L4 动态的时间尺度，否则 $b_t$ 会陈旧"——
  **只有 lagged 档检验这句话**。删掉它，该原则在实验中将完全未被检验。

---

## 4. 每条 trace 必须记录的元数据（缺一项则消融不可解释）

每条 trace 落盘以下字段：

| 字段 | 来源 | 用途 |
|---|---|---|
| `task_id`, `run_id`, `config_id` | 你们 | 主键 |
| `pass` (bool) | 断言结果 | Pass@1 |
| **`finish_reason`** | Cline 原生枚举（§3.2） | 区分**自终止 / 预算耗尽 / 崩溃** |
| **`timed_out`** (bool) | 2500 s | 区分超时 |
| `run_code_calls` | handler 计数 | `Mean read-backs`、$\Phi$ 预算校验 |
| `search_apis_calls`, `get_api_details_calls` | handler 计数 | `tab:tool-breakdown` |
| `iterations` | Cline 原生 | 计算"有效更新比"（`run_code_calls` / `iterations`） |
| `wall_clock_s` | 运行器 | 成本表 |
| **`denied_by_hook`** | 你们 hook 的日志 | 区分「反作弊拒绝」与「$\Phi$ 预算耗尽」 |
| **`deny_reason`** | hook 返回的 `errorMessage` | 归因；预算档的文本须含 `[PHI-BUDGET-EXHAUSTED]` 前缀 |
| **`reported_call_index`** | `Φ lagged` 档的 handler | 验证滞后量恰好 = 1（见 §3.6） |

> ⚠️ 若有 trace 因**反作弊 hook** 拒绝而失败，它既不是 $\Phi$ 失效也不是能力不足——
> 必须单列一类，并从 Pass@1 的解释中排除（或至少显式标注）。
> 同理，反作弊拒绝也会进入 `finish_reason`，不要把它误记为 `max_iterations`。

### 4.1 报告口径：哪些列写 `mean ± std`（**不是所有表格**）

加 `±` 之前先判断该列的**聚合单元**。混用会让读者把"跨运行标准差"与"跨 trace 的比例"当成同一种东西。

| 聚合单元 | 出现在 | 写法 | 说明 |
|---|---|---|---|
| **跨 5 次运行的准确率** | `Pass@1` 列（5 张表） | `78.5 $\pm$ 1.8` | ✅ **只有这一类是 mean ± std** |
| **由均值算出的差值** | `Δ` 列（`tab:main-ablation`、`tab:llm-comparison`） | `+43.0 pp`（**不加 ±**） | 加 `±` 会被误读成"差值的标准差"；Δ 由同表均值算出 |
| **跨 trace 汇总的比例/计数** | `Converged (%)`、`Mean read-backs`、`Avg/Trace` | 单值（**不加 ±**） | 其变异主要来自 trace 之间而非运行之间，跨运行的 std 会**严重低估** |
| **确定性/结构性量** | `tab:selfdoc-cost`、`tab:scenario-distribution`、`tab:error-categories` | 单值 | 与运行无关，mean ± std 无意义 |

**其他规则**：

- **`±` 的含义只解释一次**（论文 §6.2 已有全局约定），**不要逐表重复**——版面紧张，表注越长越容易出错。
- 表头保持 `Pass@1 (\%)` 不变；单元格里的 `x ± y` 已自说明格式。
- **5 次运行的 `std` 不是显著性**：它描述运行间波动，**不能**用来判定 `Δ` 是否为真。
  若散布与 `Δ` 同量级（如 `+3.2 pp`），必须在正文写明这一点（论文 §7 局限性已承认功效不足）。
- 所有配置 **k 统一为 5**，故 `Pass@k`（若报告）口径一致；将来若改动 k，须在表注写明且**不得跨 k 比较**。
- `tab:selfdoc-efficiency` 的 `#Calls`/`Traces` 是**每次运行一个总量**，可写 mean ± std；但 `Avg/Trace` 是比值，
  按上表第三行处理为单值。

**`Converged (%)`** := `finish_reason == completed` 的 trace 占比。
报告时必须把它**紧挨 Pass@1** 放置，因为紧预算下的低 Pass@1 可能只是"被切断"而非"更新失效"。

---

## 5. 红线（不得违反）

1. **不得复活被否决的表述。** 尤其：
   - 不得把"轮次 / rounds"作为 $\Phi$ 的操作轴（该 agent 没有规范意义上的轮次）；
   - 不得引入 "two-regime bottleneck law" / "ceiling" 式自创定律；
   - 不得自创符号方案（如四符号 I/S 体系）或重新划分 $\mathcal{K}$/$\Omega$ 的内容边界。
2. **不得改动 `tab:llm-comparison` 的结构**（列/行口径已锁定，改动前必须先确认）。
3. **不得承诺开放任务用例。** 开源承诺只覆盖 harness / schema / protocol，
   **不含** benchmark 任务本体（已在 5 处统一，见 `1_intro.tex`）。
4. **不得在未测的情况下填写数字**；未测保持 `[TBD]` 或显式写 provisional。
5. **`tab:omega` 存在跨稿口径冲突，选值前必须先统一配置定义**：
   - 本文：`(N)`=23.6、`(L)`=[TBD]、`(H)`=[TBD]、`(H+E)`=78.5
   - ICML 稿：同一阶梯报为 `(N)`=0.0、`(L)`=59.5、`(H)`=87.3
   两套的 `(N)` 基线口径不同（23.6 = Pure LLM baseline；0.0 = 完全无观测），
   **必须先确定"无观测"的实测定义，再决定引用哪一组，不得混用。**
6. **反作弊 hook 不得成为变量。** 它必须在所有臂中保持一致，且**必须在论文 §6 实验设置中披露**；
   因它被拒而失败的 trace 必须单独归类（见 §3.5、§4）。
7. **不得把 hook 拒绝原因混在一起。** 各 hook 的 `errorMessage` 必须用唯一前缀区分，
   否则无法判断某次调用被拒是"反作弊"还是"预算耗尽"（见 §3.4）。
8. **不得把内部反作弊数据写入论文。** 例如"未隔离时 pure LLM 的得分"这类内部观察，
   论文中**只做定性表述、不带数字**——带数字就必须保证其准确性并补充配套实验说明，
   该成本与论文主旨无关（论文 §6 现有表述已是这个尺度，不要加数字）。

---

## 6. 回填清单（共 6 表 / 56 个 `[TBD]` / 30 行）

> **路径**均相对 `ZhuLong_DAC2027/ZhuLong_DAC2027/DAC2027/`。
> **行号会随每次编辑漂移，不要依赖行号定位。** 请用标签或 §7 的命令 (5) 扫描 `[TBD]` 定位。
> **重复次数已统一为 5**（`tab:selfdoc-cost` 为离线一次性测量，记 1）；`±` 只加在 Pass@1 / Δ 中的 Pass@1 上，
> 口径见 §4.1。

| # | 表标签 / 文件 | 需要填的值 | `[TBD]` 数 | 依赖的配置 |
|---|---|---|---|---|
| 1 | `tab:selfdoc-cost`（`3_design.tex`） | 6 项离线成本指标 | 6 | 离线自探索日志（**1 次，无重复**） |
| 2 | `tab:main-ablation`（`6_exp.tex`） | 7 行的 **std**（均值见 §6.1，需一并重测） | 7 | 对应 6 个配置，各 5 次 |
| 3 | `tab:omega`（`6_exp.tex`） | (N)/(L)/(H)/(H+E) 的 Pass@1 与 std | 6 | S1 文档轴，各 5 次 |
| 4 | `tab:ablation-harness`（`6_exp.tex`） | (N)/(B)/(F) 的 Pass@1、std、`Mean read-backs` | 9 | S1 回读轴，各 5 次 |
| 5 | `tab:phi-bound`（`6_exp.tex`） | $k{=}1,3,10$、lagged、unbounded 的 Pass@1、std、`Converged (%)` | 14 | S2 $\Phi$ 轴，各 5 次（§3.3、§3.6） |
| 6 | `tab:llm-comparison`（`6_exp.tex`） | 5 个 backbone 的 Pass@1、std、$\Delta$ | 14 | S3，各 5 次 |

补充：**RQ3（`6_exp.tex` 的 `sec:cross-language` 小节）需要新测 SKILL 与 Tcl 两个切片**并分切片报告。
关注点是**各配置的排序与差距量级是否保持**，不是绝对准确率一致。

### 6.1 临时数字清单（非 `[TBD]`，但论文自称 provisional，需一并重测）

这些数字**已写入正文/表格**，一旦重测结果不同必须全部同步替换（含中文注释）：

| 数字 | 含义 | 主要位置 / 定位方式 |
|---|---|---|
| 78.5 | ZhuLong (Full) Pass@1 | `6_exp.tex` 多处、`0_abstract.tex`、`8_conclusion.tex`；搜 `78.5` |
| 75.3 / 37.3 | w/o Self-Expl. / w/o Sandbox | `tab:main-ablation`、§S2 正文 |
| 32.3 / 23.6 | RAG / Pure LLM | `tab:main-ablation`、`tab:omega` |
| 34.2 | w/o Retrieval | `tab:main-ablation` |
| +43.0 / −41.2 / −44.3 / +3.2 / +5.0 (pp) | 各效应量 | 评测协议段与 §S2 正文（搜 `pp`） |
| 124 / 34 · 13 / 21 | 通过数 / 失败数 · 生成阶段 / 执行阶段失败 | §Error Analysis 开头 |
| 12 / 9 | `tab:error-categories` 两类根因计数 | `tab:error-categories` |
| 243 / 220 · 6,791 / 5,845 · 30.9 / 24.1 | `tab:selfdoc-efficiency` | `tab:selfdoc-efficiency` |
| 3,203/2,812 · 1,151/1,255 · 2,437/1,778 | `tab:tool-breakdown` | `tab:tool-breakdown` |

> 替换数字时**务必同时更新同表内的 $\Delta$ 列与正文里引用的该数字**，否则表格与正文会互相矛盾。
> 论文中所有 `78.5` 必须在全仓库范围内保持一致（含 `0_abstract.tex` 与 `8_conclusion.tex`）。

---

## 7. 交付前自检（必须实际执行）

```powershell
Set-Location 'C:\Users\liuyu\ZhuLong_DAC2027\ZhuLong_DAC2027'

# (1) 编译 —— 必须连跑两遍，使交叉引用收敛
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

# (1b) 交叉引用是否已收敛 —— 第二遍后不应再出现该警告
Select-String -Path .\main.log -Pattern 'Label\(s\) may have changed'

# (2) 错误 / 未定义 / 重复定义 —— 期望输出「无」
Select-String -Path .\main.log -Pattern '^! |Undefined control sequence|LaTeX Error|multiply defined|undefined references'

# (3) 排版溢出 —— 期望 >20pt 的 Overfull 为 0
Select-String -Path .\main.log -Pattern 'Overfull \\hbox \((2[0-9]|[3-9][0-9]|[0-9]{3,})\.'

# (4) 禁用词扫描 —— 期望全 0
foreach($p in @('budget of observations','read-back budget','no principled mechanism',
                'interrupting the agent mid-flight','two-regime','ceiling law')){
  $r = Get-ChildItem .\DAC2027\*.tex | Select-String -SimpleMatch $p
  if($r){ "[HIT] $p" } else { "[OK ] $p" }
}

# (5) 剩余 [TBD] 盘点
Get-ChildItem .\DAC2027\*.tex | Select-String -SimpleMatch '[TBD]'
```

> 命令 (5) 输出的是**匹配行数**（当前基线 = **30 行 / 56 个 `[TBD]`**）。
> 由于多数行内含多个 `[TBD]`（`Pass@1` 与其 `std` 各一个），**行数本来就少于占位数**，
> 这是正常的、**不是**缺漏。逐表占位数见 §6：`selfdoc-cost` 6 + `main-ablation` 7 +
> `omega` 6 + `harness` 9 + `phi` 14 + `llm` 14 = **56**。
> 填完后行数应降为 0 或仅剩你决定延后的那几张表。

> **工具提示**：本机 MiKTeX 会在结束时打印
> `pdflatex: major issue: So far, you have not checked for MiKTeX updates.`，
> 这会使 PowerShell 把它当成原生错误并中断同一条命令串的后续输出——**它与编译成败无关**，
> 属正常现象。若被中断，用 `Start-Process pdflatex -ArgumentList ...,-Wait -NoNewWindow`
> 或把每条命令分开执行即可。
>
> **编码提醒**：`.tex` 文件为 UTF-8（含中文注释）。PowerShell 控制台默认 GBK，
> 直接 `Get-Content` 看中文会乱码——**这不是文件损坏**。核查中文请用 UTF-8 感知的方式读取。

---

## 8. 建议执行顺序（按此顺序可最早暴露风险）

1. **冒烟验证（先做，20 分钟）**：
   - **(0) canary（最重要，先做这个）**：故意触发一次**应被拒绝**的调用（例如 `run_commands`，
     或读写工作目录之外的路径），确认它**真的被拒**。
     若未被拒 → hook 未加载，**立即停止，该批次一切数据作废**
     （历史教训：无隔离时 pure LLM 曾得到 >98\%；该数字仅限内部，**勿写入论文**）。
   - (a) harness 能起；(b) 三个工具（`search_apis` / `get_api_details` / `run_code`）被调用；
   - (c) trace 元数据（§4）能落盘；
   - (d) 反作弊 hook 的拒绝原因能到达 trace 元数据且可辨识；
   - (e) 若同时挂载 $\Phi$ 预算 hook，确认**两条 hook 的拒绝原因没有互相污染**（见 §3.4）。
   → 这一步能提前暴露"hook 未装载"或"归因混乱"这类致命问题。
2. **冻结基线复现**：跑 ZhuLong (Full)，核对能否复现 ~78.5。
   **若不能复现，先停下对齐协议**，不要继续跑其余配置。
3. **S1 文档轴**（`tab:omega` 的 (L)/(H)）：只需改索引，改动最小、风险最低。
4. **S1 回读轴**（`tab:ablation-harness`）：改 `run_code` 返回负载。
5. **S2 $\Phi$ 轴**（`tab:phi-bound`）：**最后做**，因为 §3.3 的语义约束最容易做错，
   且必须先确保 `Converged (%)` 采集正确。
6. **S3 backbone 轴**（`tab:llm-comparison`）：5 个 backbone × 5 次运行，成本最高，可并行。
7. **离线成本表**（`tab:selfdoc-cost`）：独立于在线评测，可随时并行补测。
8. **RQ3 跨工具链**：需要 SKILL / Tcl 切片先建好，依赖最重，放最后。

## 9. 填写规则

- 每个数字必须能回溯到 `(config_id, run_id)` 级别的原始记录；**报告里要说明原始数据放在哪**。
- **每配置统一 5 次运行**；Pass@1 报告 **mean $\pm$ std**（std = 5 次运行的标准差）。不要只报最好的一次。
- **哪个列写 `±` 严格按 §4.1**：只有 Pass@1 写；`Δ` 与比例/计数类列（`Converged (%)`、`Mean read-backs`、
  `Avg/Trace`）**一律不加**。
- 效应量（$\Delta$）与主表数字必须**从同一批数据算出**，不得跨批次拼。
- **`std` 不是显著性**：不要因为两组 `std` 重叠与否就下结论。当 `Δ` 与散布同量级时（如 `+3.2 pp`），
  **必须在正文注明统计功效不足**（论文 §7 已把 `+3.2 pp` 定位为"互补增益而非头条结论"，不要改写成强主张）。


