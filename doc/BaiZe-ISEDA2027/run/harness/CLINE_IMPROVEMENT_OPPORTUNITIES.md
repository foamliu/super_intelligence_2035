# CLINE_IMPROVEMENT_OPPORTUNITIES.md — 对 cline 的改进机会点（H-D / D2）

> 版本 v1 · 2026-10-03 · 依据运维指令 2026-10-03 第 2 批 H-D。
> 方法：**四段式** —— ① 其它 harness 的做法（贴 `路径:行号` 原文）→ ② cline 现状（贴 `路径:行号`）→ ③ 差距 → ④ 改进建议 + 预期收益 + 风险 + 优先级。
> 五条主线（§2.2）**各至少 1 条**。每条标注：**可直接借鉴 / 需架构改动 / 不建议改**。
> 🚫 铁律：所有结论贴 `路径:行号` 原文，不许编造。
> cline 源根 `/nas_train/app.e0031982/harness/cline/`；其它 harness 源根见各自 `harness/<name>/`。

---

## 0. 阅读地图

| # | 主线 | 机会点一句话 | 类别 |
|:-:|:--|:--|:--|
| O1 | 线1 上下文注入/预处理 | 单一 memoized 投影终点 + 全链路 Telemetry，对齐 claude-code 归一化口径 | 可直接借鉴 |
| O2 | 线2 检查点/状态恢复 | 把「对话/压缩状态」与「文件快照」收进同一原子事务，消除 sidecar 漂移 | 需架构改动 |
| O3 | 线3 插件/Hook | 补 `PreCompact`/`PostCompact` 两个压缩生命周期 Hook，让 Auto Compact 可被观测/干预 | 可直接借鉴 |
| O4 | 线4 焦点链/任务状态 | 补回「任务目标/记忆」持久层（TodoWrite + Session Memory 形态），解耦长期目标与可压缩对话 | 需架构改动 |
| O5 | 线5 模型适配/降级 | token 计量改「服务端 usage 优先 + 保守兜底 + 命中回退压缩」，替代纯 3 字符/token | 可直接借鉴 |

---

## O1（线1 · 上下文注入与预处理管线）

### ① 其它 harness 的做法
claude-code 把「系统/用户上下文」做成 **memoized 单例**，并把投影收口到**单一归一化终点**：
> `claude-code/src/context.ts:116` `getSystemContext`、`:155` `getUserContext`（均 memoize）；投影终点 `claude-code/src/utils/messages.ts:1989` `normalizeMessagesForAPI`。

codex 把「投影注入」抽象为**可插拔 ContextContributor**（开放给插件）：见 `harness/codex_SOURCE_ANALYSIS.html` §4③「收（压缩）关、放（投影注入）开」。

### ② cline 现状
cline 的投影是**每请求重走 + 逐实例缓存**的 `MessageBuilder`：
> `cline/sdk/packages/core/src/session/services/message-builder.ts:105-107`
> ```ts
> /** Builds an API-safe message copy without mutating original conversation history. */
> export class MessageBuilder {
> ```

且 cline 自认存在**投影旁路 / Telemetry 盲区**：
> `cline/sdk/packages/core/src/extensions/context/compaction.ts:251-254`
> ```ts
> // Known gap: compactions performed via plugin `registerMessageBuilder()` or
> // via the `beforeModel` runtime hook bypass this wrapper entirely, so they
> // do not emit compaction telemetry. ...
> ```

### ③ 差距
- cline 的「无损投影」能力强（原始消息从不被改），但**没有单一 memoized 归一化终点**：`MessageBuilder` 每次请求重建，靠 `per-instance caches make this host state`（message-builder.ts:9）分摊成本，仍是「walk entire conversation」而非「增量 fold」。
- claude-code 的 `getSystemContext` **memoize 后稳定复用**，codex 把注入点**做成扩展插槽**；两者都比 cline 更「可增量、可观察」。

### ④ 改进建议 + 收益 + 风险 + 优先级
- **建议**：① 给 cline 加一个 **memoized 归一化终点**（等价 claude-code `normalizeMessagesForAPI`），把「系统提示 + 环境注入 + 文件剥离 + 过期内容改写」收口为一处；② 把 `registerMessageBuilder()` / `beforeModel` 两条旁路管线**纳入 Telemetry**（补上 compaction.ts:251-254 自认的盲区）。
- **预期收益**：投影成本从「每请求全量 walk」降到「增量/缓存」，延迟下降；Telemetry 补齐 → 压缩行为可端到端审计。
- **风险**：低（不动投影语义，只做收口与埋点）；需定义 memoize 失效时机。
- **优先级**：中。**类别：可直接借鉴**。

---

## O2（线2 · 检查点与状态恢复）

### ① 其它 harness 的做法
deepseek 用**事件溯源**：检查点 = append-only 事件流 flush，**「重放即回滚」**，无第二份状态需对齐（见 `harness/deepseek-harness_SOURCE_ANALYSIS.html` §线2）。
codex 把「摘要生成 / 新窗口 / WorldState 基线」三者**原子落进同一条 Rollout**，以 `window_id` 链提供审计与恢复锚：
> `codex-rs/core/src/state/auto_compact_window.rs` / `mod.rs:3752`（sidecar = `AutoCompactWindowIds(window_id 链)`）——见 `harness/codex_SOURCE_ANALYSIS.html` §3④「压缩 = 一个带 sidecar 的检查点事务」。

### ② cline 现状
cline 的检查点是**两套并存**：文件级用 **git stash/ref**，对话/压缩级用**独立 JSON sidecar**，各自成单：
> `cline/sdk/packages/core/src/hooks/checkpoint-hooks.ts:16-26`
> ```ts
> export interface CheckpointEntry {
> 	ref: string;         // git ref/stash
> 	createdAt: number;
> 	runCount: number;
> 	kind?: "stash" | "commit";
> }
> ```
> 压缩 sidecar schema/projection 见 `cline/sdk/packages/core/src/session/models/session-compaction.ts:25-34/161-190`；持久化守卫 `.../runtime/host/local-runtime-host.ts:621/1297-1360`。

且 sidecar 可靠性**曾被专项修复**（PR #12747「compaction sidecar」）——暴露了「两套状态各自落盘 → 会漂移」的固有缺陷。

### ③ 差距
- cline 的**文件状态**（git）与**对话/压缩状态**（sidecar JSON）是**两个事实源**，恢复时需人工对齐；一旦 sidecar 落盘失败（PR #12747 那类 bug），重启后阈值错乱、可能重复压缩。
- deepseek / codex 都**只有一个事实源**（事件流 / 带 window_id 的 Rollout），恢复语义单一、不漂移。

### ④ 改进建议 + 收益 + 风险 + 优先级
- **建议**：把「检查点」收敛为**一个原子事务**——文件快照 + 压缩摘要 + 阈值窗口**同一条记录**落盘（借鉴 codex 的 Rollout/window_id 链，或 deepseek 的 append-only 事件流）。
- **预期收益**：消除 PR #12747 类「sidecar 与文件状态不一致」整个 bug 类；恢复从「多源对齐」简化为「单源截断」。
- **风险**：**高**——涉及 git 检查点、事务存储、迁移兼容的核心重构。
- **优先级**：长期/架构项。**类别：需架构改动**。

---

## O3（线3 · 插件与 Hook 系统）

### ① 其它 harness 的做法
claude-code 的 Hook 事件面**最全**，且**显式包含压缩生命周期**：
> `claude-code/src/entrypoints/sdk/coreTypes.ts:25-53` —— `HOOK_EVENTS` 共 **27 个**，含 `'PreCompact'`、`'PostCompact'`；每个事件支持 `command / prompt / http / agent` 四种形态（`schemas/hooks.ts:30-53`）。

### ② cline 现状
cline 的运行时 Hook 只有 **7 个生命周期回调 + 1 个 `prepareTurn`**，**无压缩生命周期 Hook**：
> `cline/sdk/packages/shared/src/agent.ts:374-402`
> ```ts
> export interface AgentRuntimeHooks {
> 	beforeRun?/ afterRun?/ beforeModel?/ afterModel?/ beforeTool?/ afterTool?/ onEvent?;
> }
> ```
> `prepareTurn`（agent.ts:485-490）返回的消息「affect only the provider request … not persisted as session history」（agent.ts:481-483）。

### ③ 差距
- 任务书 §2.2 线3 核心问题「Auto Compact 能否插件化？Hook 能否拦到 `prepareTurn` 级底层节点？」——cline 的 `prepareTurn` 确是底层注入点，但**压缩（`createContextCompactionPrepareTurn`）在 Hook 之内、自身不暴露 Hook**：插件**观察不到也无法干预**「何时压缩、摘要是什么」。
- claude-code 用 `PreCompact`/`PostCompact` 直接回答（其压缩引擎仍硬编码，PreCompact 只能加指令、不能替换总结）。

### ④ 改进建议 + 收益 + 风险 + 优先级
- **建议**：给 `AgentRuntimeHooks` 增加 `beforeCompaction` / `afterCompaction`，让插件**观察**压缩触发、**注入**指令或拦截摘要。
- **预期收益**：直接回答「Auto Compact 能否插件化」= 能观测/干预、不能替换核心压缩算法，边界清晰；生态可做调优/审计/成本观测。
- **风险**：低（新增回调，不改既有 7 个 Hook 语义；调用序需文档化）。
- **优先级**：高。**类别：可直接借鉴**。

---

## O4（线4 · 焦点链 / 任务状态跨压缩存活）

### ① 其它 harness 的做法
claude-code 把「接下来要做什么」拆成**独立于对话历史的持久状态** + **自动记忆抽取**：
> `claude-code/src/tools/TodoWriteTool/TodoWriteTool.ts:65-94` —— `call({ todos })` 写进 `appState.todos`（session 状态，不随压缩丢）；
> `claude-code/src/services/SessionMemory/sessionMemory.ts:1-6` ——「automatically maintains a markdown file … forked subagent」后台抽取会话要点；
> `claude-code/src/services/extractMemories/extractMemories.ts:1-10` ——「Extracts durable memories … runs once at the end of each complete query loop」。

codex 用 `codex_state::ThreadGoal`（goal）+ `update_plan` 把目标/计划脱离对话历史（见 `harness/codex_SOURCE_ANALYSIS.html` §线4）。

### ② cline 现状
cline 的 Focus Chain **已被移除 / stub 化**：
> `cline/apps/vscode/src/sdk/task-proxy.ts:144`
> ```ts
> /** Focus chain checklist (stub — focus chain removed) */
> currentFocusChainChecklist?: null
> ```

### ③ 差距
- 任务书 §2.2 线4 原假设「Cline 有 Focus Chain todo 跨摘要存活」——**当前代码里已被移除**（`currentFocusChainChecklist?: null`），cline **不再有**「把『接下来做什么』与『可压缩对话』解耦」的持久层；压缩后「从停止处继续」只能重新依赖摘要文本。
- claude-code / codex 都有独立 goal/todo/memory 持久层。

### ④ 改进建议 + 收益 + 风险 + 优先级
- **建议**：① 补回 **TodoWrite 等价物**（任务清单存 session 状态，不随压缩丢）——低成本高价值；② 中长期补 **Session Memory / auto-memory**（后台 subagent 抽取要点落盘，跨 session 记忆）。
- **预期收益**：压缩后进度不丢；长期记忆跨会话复用，减少重复探索。
- **风险**：① 低；② 中（后台 subagent 抽取有成本/延迟，memory 文件污染需管控）。
- **优先级**：① 高（可直接借鉴）、② 中（需架构改动）。**类别：需架构改动（组合）**。

---

## O5（线5 · 模型能力适配与降级）

### ① 其它 harness 的做法
codex 的 token 计量是「**服务端 usage 观测优先，客户端估算兜底**」，并把「压缩」当作**模型降级第一闸门**：
> `codex-rs/core/src/state/auto_compact_window.rs:24-30`
> ```rust
> pub(crate) enum AutoCompactWindowPrefill {
>     ServerObserved(i64),   // 后端 usage 回报的真实 prompt tokens
>     Estimated(i64),        // 本地估算（精度较低）
> }
> ```
> `codex-rs/core/src/compact_model_fallback.rs:9-20` `should_retry_with_current_model`：遇 `ContextWindowExceeded / UsageLimitReached / ServerOverloaded / InvalidRequest` 先压缩+当前模型重试再降级。

claude-code 同样「usage 回执 + 粗略估算」并用：
> `claude-code/src/utils/tokens.ts:226` `tokenCountWithEstimation`（优先取 api `usage`，回退 `roughTokenCountEstimation`，默认 4 字符/token，见 `tokenEstimation.ts:203-208`）。

### ② cline 现状
cline 的 token 估算**只有「3 字符/token」静态系数**，且预算解析「模型不报窗口」时返回 `undefined`：
> `cline/sdk/packages/shared/src/llms/tokens.ts:8` `export const CHARS_PER_TOKEN = 3;`
> `cline/sdk/packages/core/src/extensions/context/compaction-shared.ts:13-15` `DEFAULT_MAX_INPUT_TOKENS = 128_000` / `CONTEXT_WINDOW_INPUT_RATIO = 0.9`
> `compaction-shared.ts:61-69` `resolveEffectiveMaxInputTokens`：`maxInputTokens` 空 → `contextWindow * 0.9`；`contextWindow` 也空 → `undefined`。

本地模型坑（任务书 §2.2 线5 Issue #7772）：`llama-server` 上下文窗口无法自动探测，Cline 默认按 128K → 触发阈值算错。

### ③ 差距
- cline **不用**服务端 `usage` 回升校准 token（codex/claude-code 都用），只靠 `3 字符/token` + `0.9` 窗口比。
- 「模型不报窗口」时 `resolveEffectiveMaxInputTokens` 返回 `undefined`（无保守兜底）→ 正面撞 Issue #7772。
- cline 的 Auto Compact 是 **per-provider 白名单**（Claude 4/GPT-5/Gemini 2.5/Grok 4），「谁被特殊对待」硬编码在 utils；codex 用 config 元数据三阶阈值（可参数化）。

### ④ 改进建议 + 收益 + 风险 + 优先级
- **建议**：① token 计量改「**服务端 usage 优先 + 3 字符/token 兜底**」（对齐 codex / claude-code）；② `resolveEffectiveMaxInputTokens` 无窗口信息时**给保守默认值而非 `undefined`**，并对本地模型做**显式窗口探测/可配置覆盖**（修 #7772）；③「provider 白名单」参数化为 config 元数据（对齐 codex）。
- **预期收益**：阈值准确 → 少溢出、少过早压缩；本地模型不踩 128K 假窗口；多窗口模型可移植。
- **风险**：低-中（①②增量；③ 需迁 hardcode 白名单到 config，测试面变宽）。
- **优先级**：高。**类别：可直接借鉴（①②）/ 需架构改动（③）**。

---

## 附：与矩阵的对应

本文件 5 条机会点，对应 `harness/HARNESS_COMPARE_MATRIX.html` 的 D1 对比矩阵（5 harness × 5 主线）。矩阵中「压缩策略 / 投影无损 / 检查点粒度 / hook 边界 / 降级触发」等子项是上面 ①② 证据的系统化展开；矩阵「机会点」列引用 O1–O5。