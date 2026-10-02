# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 运维问答

> 外部运维在 `BAIZE_HARNESS_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **H_B_cline_done**（cline 源码分析已完成并交付 HTML；下一步 = 下一个 harness 或 H-A 可行性核查 §1.1） |
| WAITING | 0（无异步阻塞，应连续推进） |
| ERROR_COUNT | 0 |
| 更新 | 2026-10-02（完成 cline H-B 源码分析） |
| 产出 | ✅ `harness/cline_SOURCE_ANALYSIS.html`（自包含，46.5KB / 619 行，含总图 + 5 条线） |

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        H_B_cline_done
已完成:       cline harness 源码环境勘察 + Auto Compact 五条主线源码分析 + 报告 HTML 交付
当前动作:     更新 MEMORY（本条）
下一步:       (a) 下一个 harness 源码分析（opencode / deepseek harness 等，同格式）
              或 (b) H-A SWE-bench 横评 —— 但必先做 §1.1 可行性核查（尤其 Docker）
阻塞:         无
ERROR_COUNT:  0
```

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

- 2026-10-02 —— 运维创建 `BAIZE_HARNESS_TASK.md` + `baize_harness_loop.sh`，本文件初始化；待 ops 启动 loop。
- 2026-10-02 —— **H-B（cline）源码分析完成**，交付 `harness/cline_SOURCE_ANALYSIS.html`。关键证据路径（供后续 harness 复用 / 巡检）：
  - 压缩策略选择 `sdk/packages/core/src/extensions/context/compaction.ts:256/285/495/502`
  - 预算常量 `sdk/packages/core/src/extensions/context/compaction-shared.ts:13-19/51-70`
  - 请求组装 + prepareTurn 调用 `sdk/packages/agents/src/agent-runtime.ts:965-996/1381-1450`；溢出恢复 `:891-932`
  - 无损投影 `sdk/packages/core/src/session/services/message-builder.ts:1-10/105-107`
  - 检查点（git）`sdk/packages/core/src/hooks/checkpoint-hooks.ts:10/16-21`；sidecar schema/projection `sdk/packages/core/src/session/models/session-compaction.ts:25-34/161-190`；持久化守卫 `sdk/packages/core/src/runtime/host/local-runtime-host.ts:621/1297-1360`
  - Hook 边界 `sdk/packages/shared/src/agent.ts:374-402/485`；插件能力面 `sdk/packages/shared/src/extensions/contribution-registry.ts:120-141`
  - Focus Chain（已 stub）`apps/vscode/src/sdk/task-proxy.ts:144-145`；`apps/vscode/src/core/task/focus-chain/file-utils.ts`
  - 旧 context-window-utils 已删（`git show 1f31738b3`）；PR #12747（compaction sidecar）`git log --grep=12747` 验证存在。
  - ⚠️ 关键结论：任务书 5 条线基于**旧 vscode 架构名**（EditType/ContextUpdate/ContextPipeline/FocusChain），当前仓已 SDK 迁移，内核保留、形态迁移 —— 报告已逐线给「旧→新」对照。

