# 与既有「Agent Harness 源码分析」研究线的重合与差异对照

> 依据 `BAIZE_HARNESS_TASK.md` §0 🔍 的运维指示：合并前先摸清家底（只读），出「重合与差异对照表」。
> 本文件是**本线自己的产物**，落 `harness/` 目录；上游 `/nas_train/app.e0031982/harness/` 只读不改。

---

## 0. 既有线家底（只读勘察结论，2026-10-02）

| 项 | 结论 |
|:---|:---|
| 位置 | `/nas_train/app.e0031982/harness/`（**与本线 `/run/harness/` 不同目录**） |
| 文件日期 | Sep 4 – Sep 15（早于本线创建 Oct 2） |
| 任务书 | `analyze_harness_sources.md`（11.8KB）：5 项目 × 8 机制（M1–M8）代码级分析 + HTML 报告 |
| 状态 | `MEMORY.md` = 「已完成」，5 项目 100%，M1–M8 全 ✅（复验 #489） |
| 主产出 | `report.html`（24,552 bytes / 257 行 / 8 张 table） |
| 证据目录 | `evidence/`、`mechanisms/` **为空**（证据沉淀于 report.html） |
| 情景记忆 | `daily-memories/2026-09-04 ~ 09-15`（10 个文件，后续每天 7–74 万字，多为复验流水） |
| loop | `loop.sh`：cline **自评循环** 3000 轮（自评分 <95 就继续），**当前未运行**（`pgrep -af 'harness/loop.sh'` 无匹配） |
| 5 个 harness 副本 | `claude-code/` `cline/` `codex/` `deepseek-harness/` `opencode/`（各带 `.git`） |

> ⚠️ 这里「cline」是 cline 社区的 cline（`/nas_train/app.e0031982/harness/cline/`），
> 与本线 `baize_harness_loop.sh` 调用 `bun .../bin/cline` 是**不同东西**（后者是 cline CLI 工具本体）。

### 既有一线的分析粒度：**机制级广度，非证据级深度**

**关键事实（可复现）**：
```bash
grep -oE '[a-zA-Z0-9_/.-]+\.[a-z]{2,4}:[0-9]+' /nas_train/app.e0031982/harness/report.html | wc -l
# → 0   （report.html 里没有任何 `文件:行号` 形式的代码证据引用）
grep -cE ':[0-9]+' /nas_train/app.e0031982/harness/report.html
# → 28  （这 28 处是散文里的时间/数字，如「16:04」「8 机制」，不是代码引用）
```
→ **上游报告是「架构级/机制级」横向对比，没有粘贴 `路径:行号` 的代码原文证据**，不符合本任务书 §2.1 铁律。

---

## 1. 三分类对照表（上游产出 vs 本任务书 §2.2 的 5 条线）

| 本任务 5 条线（§2.2） | 上游是否覆盖 | 判定 | 说明与本线增量 |
|:---|:---|:---|:---|
| **线1 上下文注入与预处理管线**（`ContextPipelinePrepareTurn` / `EditType`·`ContextUpdate` 无损投影） | 上游 M3「上下文压缩」、M1「Agent Loop」有**概述**，但**无 `ContextPipelinePrepareTurn` 调用点定位、无「原始消息 vs 投影视图」对照、无数据流图** | **B（做了但不符合要求）** | 我方需定位调用点、画出数据流、给出「无损投影」证据原文 |
| **线2 检查点与状态恢复**（非破坏性编辑 + 时间戳截断；compaction sidecar / PR #12747） | 上游 M4「会话/状态存储」仅到「SQLite+文件回退」粒度；**完全没碰「时间戳截断 + sidecar 持久化 + PR #12747」这条支线** | **C（我方增量）** | PR #12747 / sidecar / 时间戳截断 rollback 是我方独有增量 |
| **线3 插件与 Hook 系统**（hook 点清单 / `manifest.capabilities` / Auto Compact 可否插件化） | 上游 M6「扩展机制与生命周期」有概述，但**未回答「Auto Compact 能否插件化」这个核心问题、未列 hook 点全文** | **B** | 我方需列全 hook 点 + 回答扩展边界问题 |
| **线4 焦点链 / 任务状态跨压缩存活**（Focus Chain / todo） | 上游 M8「子 Agent / 多 Agent」、M4 均**未覆盖「短期对话 vs 长期 todo 解耦」这一特定命题** | **C（我方增量）** | 我方独有 |
| **线5 模型能力适配与降级**（`context-window-utils` / 3字符/token / Issue #7772） | 上游**未覆盖** token 计数与 provider 降级妥协清单 | **C（我方增量）** | 我方独有；含 Issue #7772 |

### 上游可**直接引用**的东西（A 类）

| 上游产出 | 可直接引用的价值 |
|:---|:---|
| 5 项目的**架构范式总图**（单体→插件化：claude-code 单体 / cline 分层 SDK / codex Rust 微内核 / deepseek-harness 全插件 Cordis / opencode Effect DI） | 作为本线各 harness 报告的**背景参照**，不用重做架构总览 |
| 5 项目「共同技术选择」：MCP、OpenTelemetry、SQLite、流式 SSE/WS | 作为**横评背景** |
| 每个项目的**机制级标签**（如 opencode = EffectStream，deepseek = Cordis 全插件，codex = 三层沙盒） | 作为**进一步深挖的起点/索引** |

---

## 2. 上游 M1–M8 ↔ 本线 5 条线的映射

| 上游机制 | 本线对应 | 关系 |
|:---|:---|:---|
| M1 Agent Loop | 线1 预处理管线（loop 内的 prepareTurn 环节） | 上游有 loop 概述，缺 prepareTurn 深挖 |
| M2 工具系统与执行管道 | （本任务书未单列，属于横评背景） | 上游可借鉴 |
| M3 上下文压缩 | 线1/线2/线4（Auto Compact 主战场） | **上游只到「压缩策略种类」粒度，缺触发点/回滚/sidecar** |
| M4 会话/状态存储 | 线2 检查点、线4 todo 持久化 | 上游只到「SQLite+文件」，缺时间戳截断 |
| M5 安全/权限/沙盒 | H-A（SWE-bench 沙箱） | 上游有架构概述，可作 H-A 沙箱路线参照 |
| M6 扩展机制与生命周期 | 线3 插件与 Hook | 上游缺 hook 点全文 + 扩展边界判定 |
| M7 并发与错误恢复 | 线2 sidecar 可靠性 | 侧链 |
| M8 子 Agent / 多 Agent | 线4（task 状态） | 侧链 |

---

## 3. 合并结论与执行顺序

1. **不重复上游已做的架构总览**；每个 harness 报告直接以「架构范式」作为背景一句话带过，正文聚焦 5 条线**证据级**深挖。
2. **我方增量（C 类）**是核心价值：线2 检查点/sidecar/PR #12747、线4 焦点链解耦、线5 模型降级 —— 这些都是上游**完全没做**的。
3. 旧的 `report.html` / `analyze_harness_sources.md` 作为**输入引用**（路径见上表 §0），不复制内容。
4. 🚫 不改动 `/nas_train/app.e0031982/harness/` 任何东西；不启动其 `loop.sh`（已确认未运行）。

> 上游报告路径：`/nas_train/app.e0031982/harness/report.html`（可作背景参照）；上游任务书：`/nas_train/app.e0031982/harness/analyze_harness_sources.md`。