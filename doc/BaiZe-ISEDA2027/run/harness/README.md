# harness/ — BaiZe Harness 研究线产物目录

> 本目录存放 **H-A / H-B 的文本产物**（**入库**）。
> 原始仓库副本、SWE-bench 运行产物（预测 patch / 评测日志 / 容器）**不入库**，放 `harness/swebench_runs/`（已在 `.gitignore` 或由 loop 只 add 文本文件控制）。

## 计划产物

| 文件 | 来自 | 说明 |
|:--|:--|:--|
| `cline_SOURCE_ANALYSIS.html` | **H-B** | cline 源码分析（自包含；以 **Auto Compact** 为切入点，沿「上下文生命周期」展开 5 条线） |
| `<other>_SOURCE_ANALYSIS.html` | H-B | 其他 harness（opencode / deepseek harness 等）同格式 |
| `SWEBENCH_COMPARE.html` | **H-A** | SWE-bench 横评结果（口径 + 结果表 + 失败模式） |
| `swebench_runs/` | H-A | **原始产物，不入库** |

## H-B 报告的 5 条分析主线（详见 `../BAIZE_HARNESS_TASK.md` §2.2）

1. **上下文注入与预处理管线**（`ContextPipelinePrepareTurn`；`EditType`/`ContextUpdate` 的**无损投影**）
2. **检查点与状态恢复**（**非破坏性编辑 + 时间戳截断**；`compaction sidecar` / PR #12747）
3. **插件与 Hook 系统**（`beforeRun`/`afterRun`/`beforeTool`；`manifest.capabilities`；`setup(_api, ctx)`）
4. **焦点链与任务状态跨压缩存活**（Focus Chain —— 短期记忆 vs 长期目标解耦）
5. **模型能力适配与降级策略**（`context-window-utils.ts`；3 字符/token；Issue #7772）

## 纪律

- 🚫 **不许猜** —— 每条结论贴 `文件路径:行号` + 代码片段。
- 🚫 **不贴大段源码**（关键 5–15 行即可），其余给路径+行号。
- ✅ **每个机制必须画数据流**，并写清**代价与边界**。
- ✅ **必须有一张「上下文生命周期全景图」**，标出 5 条线各自位置。

