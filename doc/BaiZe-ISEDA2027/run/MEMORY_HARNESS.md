# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 运维问答

> 外部运维在 `BAIZE_HARNESS_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **H_0_bootstrap**（任务线刚创建，尚未开始；下一步 = 环境勘察 `ls -la /nas_train/app.e0031982/harness`） |
| WAITING | 0（无异步阻塞，应连续推进） |
| ERROR_COUNT | 0 |
| 更新 | 2026-10-02（由运维创建任务线与 loop，待 ops 启动） |
| 产出 | **尚无** —— 目标：`harness/cline_SOURCE_ANALYSIS.html`（H-B）+ `harness/SWEBENCH_COMPARE.html`（H-A） |

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        H_0_bootstrap
已完成:       任务书 + loop 已就位（运维）
当前动作:     <待首次唤醒>
下一步:       ls -la /nas_train/app.e0031982/harness → 摸清有哪些 harness
阻塞:         无（未启动）
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

