# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（组件；S1 段跳过，见任务书运维指令（四））|
| CONFIG | `wo_retrieval` |
| ROUND | 2（r1=74.1% 复用 legacy；从 r2 续跑）|
| PHASE | `running`（运维已填实起始点 2026-10-04）|
| WAITING | 1（语义 = eval 跑着 / 等 infra 就绪；非"待拍板"）|
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | `glm-5.2`（编排模型；deepseek-v4-pro-fp4 额度已耗尽故更换）|

## 执行看板（15 臂 × 5 轮）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| S1 | omega_low | 1-5/5 | ⬜（旧 5-run 已出 r1=81.6 / r2=82.3，待运维定是否延续）|
| S1 | readback_binary | 1-5/5 | ⬜ |
| S1 | readback_none | 1-5/5 | ⬜ |
| C1 | pure_llm | 1-5/5 | ⬜（探路 1-shot 11.4%）|
| C1 | rag | 1-5/5 | ⬜（探路 70.3%）|
| C1 | wo_retrieval | 1-5/5 | ⬜（探路 81.6%）|
| C1 | full（锚点）| 1-5/5 | ⬜（探路 84.8%）|
| C2 | phi_k10 | 1-5/5 | ⬜（探路 75.3%）|
| C2 | phi_k3 | 1-5/5 | ⬜（探路 69.0%）|
| C2 | phi_k1 | 1-5/5 | ⬜（探路 60.8%）|
| C2 | phi_lagged | 1-5/5 | ⬜（探路 84.2%，r2 修复后 98.1%）|
| B | glm-5.2 | 1-5/5 | ⬜ |
| B | deepseek-v4-flash | 1-5/5 | ⬜ |
| B | kimi-k2.6-cloud | 1-5/5 | ⬜ |
| B | doubao-seed-2.0-pro-cloud | 1-5/5 | ⬜ |

## 成绩记录（N=5 mean±std，Pass@1 %）

| 臂 | N=5 mean±std | 各轮原始值 |
|:--|:-:|:--|
| （空 — 待开跑） | — | [] |

## 操作流水

- [2026-10-04] [bootstrap] 合并任务书/loop/MEMORY 初始化：`ZHULONG_TASK.md` + `zhulong_loop.sh` + 本文件创建。PHASE=init、WAITING=1。待运维确认 infra（license / shard 端口 8664·8665·8653·8669 / `/home` 磁盘 ≥8G）与起始点后，首周期 canary + 切 `S1.omega_low` 启动 r1。