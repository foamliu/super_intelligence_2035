# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（Phase B 4/4✅；C1 pure_llm/rag/wo_retrieval 5/5✅；**full 锚点 r1=88.0%✅保留 r2=59.5%❌作废(39 timeouts,需复测) r3=63.3%❌作废(需复测) r4 运行中(b2026_1009_094504,新key e13f4f37)**）|
| CONFIG | `full`（C1 第4臂=锚点；r1=88.0%✅保留 r2=59.5%❌作废(39 timeouts)→复测 r3=63.3%❌作废→复测 **r4 运行中** b2026_1009_094504 PID 3302534 新key e13f4f37+/cloud/v1 pro-fp4 已恢复HTTP 200）|
| ROUND | 4 |
| PHASE | `running`（C1.full r4 **grading阶段**：run_eval.py child 611439 沙箱执行140脚本中(~1h48m, 16:29起算); generation已完成 140ok/12fail/**6 timeout**(≤10✅,待PASS_RATE≥75%判定)。0 Forbidden✅ infra /home13G✅ 沙箱404✅ loop3579323(proxy✅) ops✅ legacy✅ git clean✅。**下轮第一件事**：pgrep→running=巡检退出; done→收割r4(grep pass/PASS_RATE+timeout数)→判据(timeout≤10且≥75%)→有效→retest r2(/tmp/ABL_full_r2_retest.log)→r3(/tmp/ABL_full_r3_retest.log)→r5→mean±std([r1=88.0,r2',r3',r4,r5])→just_finished→回填5表→C2; 作废→WAITING=1复检）|
| WAITING | 1 |
| ERROR_COUNT | 2（C1.full r2 首启缺四override→158 Forbidden=config失败非infra,已重跑恢复[但该r2=59.5%现因39 timeouts被运维2026-10-09三判❌作废,需复测]; r4 连续2次infra作废(pro-fp4 403额度耗尽)非eval失败不计ERROR_COUNT。r2/r3 作废属服务不稳定非config失败,不计ERROR_COUNT）|
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-pro-fp4`（**✅已恢复 HTTP 200（新 key e13f4f37 + /cloud/v1）**；r1/r2/r3 用旧 key 9eed3da1 全部有效(同后端 deepseek-v4-pro-260813)，无需重跑；r4 起用新 key）|

## 执行看板（15 臂 × 5 轮——已调换为 B→C1→C2→S1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| B | glm-5.2 | 5/5 ✅ | **83.3±3.1%** [84.2,87.3,84.2,79.1,81.6]（r5=81.6% 129/158 batch 2026_1005_233928, 0 Forbidden ✅）|
| B | deepseek-v4-flash | 5/5 ✅ | **16.7 ± 12.3%** [9.5,10.1,19.0,7.6,37.3]（r1=9.5%(15/158,b2026_1006_022818); r2=10.1%(16/158,b2026_1006_031227); r3=19.0%(30/158,b2026_1006_034557); r4=7.6%(12/158,15ok/143fail/0exec_err,b2026_1006_042140); r5=37.3%(59/158,67ok/90fail/0exec_err,b2026_1006_045811), 0 Forbidden ✅ 全程）|
| B | kimi-k2.6-cloud | 5/5 ✅ | **77.0±1.6%** [79.1,76.6,77.2,74.7,77.2]（r5=77.2% 122/158 batch 2026_1006_230904, 137ok/21fail/0exec_err, 0 Forbidden ✅, kimi active ✅）|
| B | doubao-seed-2.0-pro-cloud | 5/5 ✅ | **63.8±1.4%** [63.9,64.6,61.4,65.2,63.9]（r5=63.9% 101/158 b2026_1007_095002, 0 Forbidden ✅, doubao active ✅）|
| C1 | pure_llm | 5/5 ✅ | ✅ 10.5±1.9%（复用 legacy：[8.2,9.5,10.1,11.4,13.3]）|
| C1 | rag | 5/5 ✅ | **71.8±2.5%** [70.3,72.2,69.6,70.9,75.9]（r5=75.9% 120/158 batch 2026_1007_202448, 151 ok/7 fail/0 exec_err, 0 Forbidden ✅；legacy 68.2±7.4% 作废→本线重跑）|
| C1 | wo_retrieval | 5/5 ✅ | **81.0±4.5%** [74.1,86.1,81.6,79.7,83.5]（r1=74.1% 复用 legacy；r2=86.1% 136/158 b2026_1007_221959；r3=81.6% 129/158 b2026_1008_015818；r4=79.7% 126/158 b2026_1008_0507；r5=83.5% 132/158 b2026_1008_081817 147ok/8fail/0exec_err 0 Forbidden✅ 全程）|
| C1 | full（锚点）| r1✅+r2❌作废+r3❌作废+r4 grading中 | r1=88.0% 139/158 b2026_1008_114702 150ok/7fail/0exec_err 0 Forbidden✅**保留**; r2=59.5% 94/158 b2026_1008_150357 **❌作废(39 timeouts→r2-retest)**; r3=63.3% 100/158 b2026_1008_222842 **❌作废(→r3-retest)**; r4 b2026_1009_094504 PID 3302534 **grading阶段**(gen 140ok/12fail/6timeout, run_eval.py执行中) 0 Forbidden✅(判据:timeout≤10且≥75%) |
| C2 | phi_k10 | 1-5/5 | ⬜（探路 75.3%）|
| C2 | phi_k3 | 1-5/5 | ⬜（探路 69.0%）|
| C2 | phi_k1 | 1-5/5 | ⬜（探路 60.8%）|
| C2 | phi_lagged | 1-5/5 | ⬜（探路 84.2%，r2 修复后 98.1%）|
| S1 | omega_low | 1-5/5 | ⬜（旧 5-run 已出 r1=81.6 / r2=82.3，待定是否延续）|
| S1 | readback_binary | 1-5/5 | ⬜ |
| S1 | readback_none | 1-5/5 | ⬜ |

## 成绩记录（N=5 mean±std，Pass@1 %）

| 臂 | N=5 mean±std | 各轮原始值 |
|:--|:-:|:--|
| B.glm-5.2 | **83.3 ± 3.1%** | [84.2, 87.3, 84.2, 79.1, 81.6] |
| B.deepseek-v4-flash | **16.7 ± 12.3%** | r1=9.5%（15/158, batch 2026_1006_022818）；r2=10.1%（16/158, batch 2026_1006_031227）；r3=19.0%（30/158, batch 2026_1006_034557）；r4=7.6%（12/158, 15 ok/143 fail/0 exec_err, 0 Forbidden ✅, batch 2026_1006_042140）；r5=37.3%（59/158, 67 ok/90 fail/0 exec_err, 0 Forbidden ✅, batch 2026_1006_045811）|
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2]（r1=79.1% 125/158 b2026_1006_071809；r2=76.6% 121/158 b2026_1006_100626；r3=77.2% 122/158 b2026_1006_181646；r4=74.7% 118/158 b2026_1006_204422；r5=77.2% 122/158 b2026_1006_230904, 137 ok/21 fail/0 exec_err, 0 Forbidden ✅ 全程）|
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9]（r1=63.9% 101/158 b2026_1007_010601；r2=64.6% 102/158 b2026_1007_030335；r3=61.4% 97/158 b2026_1007_050414；r4=65.2% 103/158 b2026_1007_083426；r5=63.9% 101/158 b2026_1007_095002, 0 Forbidden ✅ 全程）|
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | **81.0 ± 4.5%** | [74.1, 86.1, 81.6, 79.7, 83.5]（r1=74.1% 复用 legacy；r2=86.1% 136/158 b2026_1007_221959 149ok/4fail/0exec_err 0 Forbidden✅；r3=81.6% 129/158 b2026_1008_015818 146ok/7fail/0exec_err 0 Forbidden✅；r4=79.7% 126/158 b2026_1008_0507 145ok/10fail/0exec_err 0 Forbidden✅；r5=83.5% 132/158 b2026_1008_081817 147ok/8fail/0exec_err 0 Forbidden✅；旧 r2 作废 0/158 pro-fp4 403 不计数）|
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9]（r1=70.3% 111/158 b2026_1007_112101；r2=72.2% 114/158 b2026_1007_131535；r3=69.6% 110/158 b2026_1007_163343；r4=70.9% 112/158 b2026_1007_183007；r5=75.9% 120/158 b2026_1007_202448, 151 ok/7 fail/0 exec_err, 0 Forbidden ✅ 全程；旧 r3 作废 b2026_1007_151301 0/158 不计数；legacy 68.2±7.4% 作废）|
| C1.full（锚点）| ⍌ 4/5 进行中 | r1=88.0%（139/158, 150 ok/7 fail/0 exec_err, 0 Forbidden ✅, batch b2026_1008_114702）；r2=59.5%（94/158, 140 ok/14 fail/0 exec_err, 0 Forbidden ✅, ⚠️39 timeouts, batch b2026_1008_150357）；r3=63.3%（100/158, 150 ok/5 fail/0 exec_err, 0 Forbidden ✅, batch b2026_1008_222842）；r4 运行中 b2026_1009_094504 PID 3302534（新key e13f4f37+/cloud/v1 re-auth后重启, 0 Forbidden ✅）|

## 操作流水
- [2026-10-09 01:28] [⏩ 已滚出] ✅ C1.full r3 收割 63.3%→r4 启动（四 override PID 649691 batch 2026_1009_012854）+ proxy/ops/legacy自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§01:28，rolled-from-MEMORY 2026-10-09 07:45）。
- [2026-10-08 22:25] [✅ C1.full r2 收割 59.5%→r3 启动] [⎩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§22:25，rolled-from-MEMORY 2026-10-09 01:28）。
- [2026-10-08 14:20] [✅ C1.full r1 收割 88.0%→r2 启动] [⎩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§14:20，rolled-from-MEMORY 2026-10-09 01:28）。
- [2026-10-08 11:42] [✅ C1.wo_retrieval r5 收割 83.5%→5/5=81.0±4.5%→切 C1.full 锚点 r1 启动] [⎩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§11:42，rolled-from-MEMORY 2026-10-08 22:25）。
- [2026-10-08 08:18] [✅ C1.wo_retrieval r4 收割 79.7%→r5 启动] [⎩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§08:18，rolled-from-MEMORY 2026-10-08 11:42）。


- [2026-10-08 05:05] [✅ C1.wo_retrieval r3 收割 81.6%→r4 启动] [⎩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§05:05，rolled-from-MEMORY 2026-10-08 07:37）。

- [2026-10-07 18:29] [✅ C1.rag r3 收割 69.6%→r4 启动] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（§18:29，rolled-from-MEMORY 2026-10-07 20:24）。
- [2026-10-07 16:34] [✅ C1.rag r3 重跑启动（pro-fp4 额度恢复 HTTP 200@16:32:44）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 18:29）。
- [2026-10-07 15:47] [⚠️ infra C1.rag r3 作废（pro-fp4 额度耗尽 0/158）→待 ~16:32 quota 恢复后重跑，不动作退出] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 18:29）。
- [2026-10-07 15:11] [✅ C1.rag r2 收割 72.2%→r3 启动] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（§15:11，rolled-from-MEMORY 2026-10-08 01:58）。
- [2026-10-07 13:51] [🩾 C1.rag r2 健康巡检→仍在跑（code-gen ~37min）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（§13:51，rolled-from-MEMORY 2026-10-08 01:58）。

- [2026-10-07 13:12]  [✅ C1.rag r1 收割 70.3%→r2 启动] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 16:34）。



- [2026-10-07 11:04]  [✅ B.doubao r5 收割 63.9%→Phase B 完成 4/4→pro-fp4 恢复 HTTP 200→切 C1.rag r1 启动] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 16:34）。

- [2026-10-07 03:42] [⎩ 已滚出] B.doubao r2 健康巡检（不动作退出·生成段）已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 07:17）。

- [2026-10-07 03:01] [⎩ 已滚出] B.doubao r1 收割 63.9%→r2 启动详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 07:17）。

- [2026-10-07 02:22] [⏩ 已滚出] B.doubao-seed-2.0-pro-cloud r1 健康巡检（仍在跑·评分段）+ push 重试说明已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 03:42）。

- [2026-10-07 01:49] [⏩ 已滚出] B.doubao-seed-2.0-pro-cloud r1 健康巡检（仍在跑·生成段）已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 03:42）。



- [2026-10-07 01:06] [⎩ 已滚出] B.kimi r5 收割 77.2%→5/5 完成 77.0±1.6%→切 B.doubao r1 启动详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 07:17）。


- [2026-10-07 00:24] [⎩ 已滚出] B.kimi r5 健康巡检（仍在跑，不动）已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 07:17）。

- [2026-10-06 23:48] [⎩ 已滚出] B.kimi r5 健康巡检（仍在跑，不动）已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 07:17）。


- [2026-10-06 23:08] [⎩ 已滚出] B.kimi r4 收割 74.7%→r5 启动详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 07:17）。

- [2026-10-06 22:30/21:58/21:25] [⏩ 已滚出] B.kimi-k2.6-cloud r4 三次健康巡检（均「仍在跑，不动」）已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-06 23:10）。


- [2026-10-06 20:44] [⎩ 已滚出] B.kimi r3 收割 77.2%→r4 启动详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 07:17）。

- [2026-10-06 20:10] [⎩ 已滚出] B.kimi r3 健康巡检（仍在跑，不动）已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 07:17）。

- [2026-10-06 19:37] [⏳ B.kimi-k2.6-cloud r3 健康巡检 → 仍在跑，不动] §7 步骤 A：`pgrep '^bash scripts/run_cline_script'`→**有输出**（PID 3583097 仍存活，etime ~4874s≈81min）。健康核验：r3 log mtime 19:37（11.8MB，active），tail 见 live cline thinking（emyDesign/block/pyAether 任务推进中）；尚无 `pass (/PASS_RATE` 汇总行→r3 未结束；`grep -c Forbidden`=0 ✅（kimi-k2.6-cloud active ✅，独立 CLI_DATA_DIR 隔离完好）。判据 pgrep 有输出→什么都不做退出，WAITING 保持 1。下轮唤醒复检 r3（无输出则 harvest r3 Pass@1）。

- [2026-10-06 19:02] [⎩ 已滚出] B.kimi r3 健康巡检+ops中继复检+git补推已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 07:17）。


- [2026-10-06 18:17] [⏩ 已滚出] B.kimi r2 收割 76.6%→r3 启动详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 06:21）。

- [2026-10-06 11:15] [⏩ 已滚出] B.kimi r2 健康巡检详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 06:21）。
- [2026-10-06 10:04] [⏩ 已滚出] B.kimi r1 收割 79.1%→r2 启动详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 06:21）。

- [2026-10-06 07:18–09:31] *B.kimi-k2.6-cloud r1 health-check + 启动（07:18 r1 启动 / 07:52·08:24·08:59·09:31 健康巡检不动作退出）已滚出至 daily-memories/2026-10-06.md（rolled-from-MEMORY 段 + 当日摘要 07:18/07:52/08:24，2026-10-06 18:17 滚动以保 <=32KB）。*

- [2026-10-06 07:07] [⎩ 已滚出] B.deepseek-v4-flash r5 收割→臂完成 16.7±12.3% 详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 07:17）。
- [2026-10-06 04:56] [⏩ 已滚出] B.deepseek-v4-flash r4 收割 7.6% → r5 启动详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-06 23:48）。
- [2026-10-06 02:30–04:21] [⏩ 已滚出] B.glm-5.2 r5 收割→切 flash + B.deepseek-v4-flash r1/r2/r3 收割详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 01:10）。


- [2026-10-05 12:05] [🚀 B.glm-5.2 r1 启动 → 已滚出] Phase B 首臂 glm-5.2 r1 前置+启动详情（.env 切 full / MCP 重启 PID 3298357:8090 / cline auth glm-5.2 key c2759d74 / canary 4 组通过 / infra 8650-8654+9006 / 启动 PID 3308249 batch 2026_1005_120536）已原文搬入 daily-memories/2026-10-05.md（rolled-from-MEMORY 2026-10-06 20:50）。

- [2026-10-05 11:25] [ð 试验次序调换] **Phase B（大模型消融）提到最前**。因  额度 HTTP 403 阻塞 C1/wo_retrieval 无法推进，而 Phase B 的 4 个模型（glm-5.2 / deepseek-v4-flash / kimi-k2.6-cloud / doubao-seed-2.0-pro-cloud）均使用独立 key/endpoint，完全不受 pro-fp4 限制。新顺序：**B â C1 â C2 â S1**。已同步更新：ZHULONG_TASK.md §§ 0/4/5（顺序表+轮转矩阵）、MEMORY_ZHULONG.md 状态头/看板/成绩表。C1/wo_retrieval r2 标记为 â¸（暂停），待 Phase B 完成后 pro-fp4 恢复时重试。legacy 组件 loop 仍在跑（PID 2455466），本轮不干扰。
- [2026-10-04/05 早期流水] *legacy-保活(10-05 11:13)+bootstrap(10-04)+infra-check(10-04 ~21:54) 已滚出至 daily-memories/2026-10-05.md 与 2026-10-04.md（rolled-from-MEMORY 段，2026-10-06 10:08 滚动以保 <=32KB）。*
- [2026-10-06 05:32–06:35] [⏩ 已滜出] B.deepseek-v4-flash r5 健康巡检（06:35/06:03/05:32）+ 07:07 r5 收割 37.3%→致完成 16.7±12.3% 详情已原文搬入 daily-memories/2026-10-06.md（rolled-from-MEMORY 2026-10-07 03:05）。
- [2026-10-07 04:22] [⏩ 已滚出] B.doubao-seed-2.0-pro-cloud r2 健康巡检（不动作退出，r2 PID 586670 仍在跑）详情已原文搬入 daily-memories/2026-10-07.md（该轮记录，已被 05:01 r2 收割 64.6% 闭合）。
- [2026-10-07 05:01] [⏩ 已滚出] ✅ B.doubao-seed-2.0-pro-cloud r2 收割 64.6% → r3 启动 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 11:04）。
- [2026-10-07 05:44] [⏩ 已滚出] 🩺 B.doubao-seed-2.0-pro-cloud r3 健康巡检 → 不动作退出 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 11:04）。
- [2026-10-07 06:21] [⏩ 已滚出] 🔧 B.doubao-seed-2.0-pro-cloud r3 生成完成→Step7.1 eval 崩溃→重打分启动 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 11:04）。
- [2026-10-07 06:39] [⏩ 已滚出] 🔧⚠️ 重打分 v1… 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-08 05:05）。





- [2026-10-07 07:17] [⏩ 已滚出] 🩾 B.doubao-seed-2.0-pro-cloud r3 重打分 v2 仍在跑… 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-08 05:05）。


- [2026-10-07 08:32] [⏩ 已滚出] ✅ B.doubao r3 重打分 v2→r4 启动 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 14:34）。
- [2026-10-07 09:10] [⏩ 已滚出] 🩾 B.doubao r4 健康巡检 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 14:34）。



- [2026-10-07 09:47] [⏩ 已滚出] ✅ B.doubao r4 收割 65.2%→r5 启动 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 14:34）。

- [2026-10-07 07:57] [⏩ 已滚出] 🩾 B.doubao-seed-2.0-pro-cloud r3 重打分 v2 仍在跑（shard_3 ~70%→不动作退出） 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 11:04）。
- [2026-10-07 10:30] [⏩ 已滚出] 🩾 B.doubao r5 健康巡检 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 13:51）。

- [2026-10-07 12:00] [⏩ 已滚出] 🩾 C1.rag r1 健康巡检#1 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 13:51）。

- [2026-10-07 12:35] [⏩ 已滚出] 🩾 C1.rag r1 健康巡检#2 + ⚠️git push 失败 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 13:51）。
- [2026-10-07 14:34] [⏩ 已滚出] 🩾 C1.rag r2 健康巡检（code-gen ~80min）详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 19:47）。

- [2026-10-07 21:00 已滚出] 🩾 C1.rag r3/r4 健康巡检流水（17:17/17:50/19:09/19:47）已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 21:00）。
- [2026-10-07 20:24] [✅ C1.rag r4 收割 70.9%→r5 启动] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 22:18）。
- [2026-10-07 21:00] [🩾 C1.rag r5 健康巡检 #1（仍在跑）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 22:18）。
- [2026-10-07 21:38] [🩾 C1.rag r5 健康巡检 #2（仍在跑）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 22:18）。

- [2026-10-07 22:18] [✅ C1.rag r5 收割 75.9%→5/5=71.8±2.5%→切 C1.wo_retrieval r2 启动] [⎩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（§22:18，rolled-from-MEMORY 2026-10-08 11:42）。

- [2026-10-07 22:58] [⏩ 已滚出] 🩾 C1.wo_retrieval r2 健康巡检 #1 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-08 12:27）。

- [2026-10-07 23:32] [⏩ 已滚出] 🩾 C1.wo_retrieval r2 健康巡检 #2 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-08 12:27）。

- [2026-10-08 00:08] [⏩ 已滚出] 🩾 C1.wo_retrieval r2 健康巡检 #3（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（rolled-from-MEMORY 2026-10-08 19:55）。

- [2026-10-08 00:42] [⏩ 已滚出] 🩾 C1.wo_retrieval r2 健康巡检 #4（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（rolled-from-MEMORY 2026-10-08 19:55）。

- [2026-10-08 01:19] [⏩ 已滚出] 🩾 C1.wo_retrieval r2 健康巡检 #5（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（rolled-from-MEMORY 2026-10-08 19:55）。

- [2026-10-08 01:58] [✅ C1.wo_retrieval r2 收割 86.1%→r3 启动] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**无输出**（r2 PID 3132954 gone, log mtime 01:23, size 31.8MB）→ 进入打分。**打分**：`grep -E 'pass \(|PASS_RATE|评估结果汇总' /tmp/ABL_wo_retrieval_r2.log`→PASS_RATE=0.8608 / **136/158 pass (86.1%)** / generated 149 ok/4 fail/0 exec_err, **0 Forbidden✅**, batch 2026_1007_221959。**r2=86.1%** ✅。**核验**：`grep -c Forbidden`=0✅；ACCESS RESTRICTED 990×（反作弊 hook live✅ canary PASS）；pro-fp4 mentions 12290 / other-model leak 0✅；run_code 6312 calls（wo_retrieval: 検索 OFF / run_code ON✅）。**.env wo_retrieval 态确认**：line226 EDA_MCP_TOOLS_DISABLED=clean_workdir,probe_pyAether_code,cimi_search,cimi_fetch,vqa,query_memory_bank,**get_api_details,search_apis,search_apis_by_keyword**（検索3件套 OFF✅ / run_code 不在禁用表→ON✅）→ 同臂不切 set_ablation。ROUND 2→3≤5→启 r3。**r3 启动**（复用 r2 姿势 + 显式 https_proxy）：`cd $BASE_DIR && export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework && export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data && export PYTHON=$BASE_DIR/venv/bin/python && export https_proxy=http://172.19.92.23:13128 && setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_wo_retrieval_r3.log 2>&1 < /dev/null &`→**PID 3591824**（ppid=1 setsid detached✅，stat=Ss）batch **2026_1008_0158** 8worker/158/-n，log=/tmp/ABL_wo_retrieval_r3.log。**canary+验证**：① /proc/3591824/environ 四 override✅ EVAL_FW_DIR/CLI_DATA_DIR=.cline_prof4_eval/data/PYTHON/https_proxy=172.19.92.23:13128；② 0 Forbidden✅；③ ACCESS RESTRICTED 30×（反作弊 hook live✅ canary PASS）；④ pro-fp4 mentions 96 / other-model leak 0✅；⑤ log 178KB 活跃增长✅（run_code 66 calls，wo_retrieval 検索 OFF / run_code ON✅）。**infra**：8653/8664/8665/8669/8090/9006 全 OPEN✅ /nasdata 368G free✅ /home 99%/5.7G（非阻断，我方产物落 /nasdata）。**运维复检**：legacy 组件 loop PID 2455466 alive✅（指令五满足）；ops relay PID 2665949 alive✅（`.last_run_id`=21=inbox RUN_ID 21，无新指令，指令八满足）；zhulong_loop PID 3579323 alive✅；conductor 未触碰（红线）。**已收割**：Phase B 4/4✅；C1.pure_llm 5/5=10.5±1.9%✅；C1.rag 5/5=71.8±2.5%✅；C1.wo_retrieval r1=74.1%/r2=86.1%✅，r3 运行中。**状态**：STAGE=C1 / CONFIG=wo_retrieval / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r3（pgrep 无输出→grep PASS_RATE /tmp/ABL_wo_retrieval_r3.log 取 r3 Pass@1→记成绩→ROUND≤5 启 r4，⚠️ r4/r5 启动必带 EVAL_FW_DIR override + CLI_DATA_DIR pro-fp4 隔离 + https_proxy）。

- [2026-10-08 04:31] [⏩ 已滚出] 🩾 C1.wo_retrieval r3 健康巡检 #4（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（rolled-from-MEMORY 2026-10-08 05:05）。

- [2026-10-08 05:45] [⏩ 已滚出] 🩾 C1.wo_retrieval r4 健康巡检 #1（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（rolled-from-MEMORY 2026-10-08 07:01）。

- [2026-10-08 06:24] [⏩ 已滚出] 🩾 C1.wo_retrieval r4 健康巡检 #2（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（rolled-from-MEMORY 2026-10-08 07:01）。

- [2026-10-08 07:01] [⏩ 已滚出] 🩾 C1.wo_retrieval r4 健康巡检 #3（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（§07:01，rolled-from-MEMORY 2026-10-08 08:18）。

- [2026-10-08 07:37] [⏩ 已滚出] 🩾 C1.wo_retrieval r4 健康巡检 #4（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（§07:37，rolled-from-MEMORY 2026-10-08 08:18）。

- [2026-10-08 08:59] [⏩ 已滚出] 🩾 C1.wo_retrieval r5 健康巡检 #1（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（§08:59，rolled-from-MEMORY 2026-10-08 09:33）。

- [2026-10-08 09:33] [🩾 C1.wo_retrieval r5 健康巡检 #2（仍在跑）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§09:33，rolled-from-MEMORY 2026-10-08 11:42）。

- [2026-10-08 10:09] [🩾 C1.wo_retrieval r5 健康巡检 #3（仍在跑）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§10:09，rolled-from-MEMORY 2026-10-08 11:42）。

- [2026-10-08 10:48] [📝 国庆假期进展 HTML 报告] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§10:48，rolled-from-MEMORY 2026-10-08 11:42）。

- [2026-10-08 12:27] [🩾 巡检：报告已提交✅ + proxy 自检通过✅ + full r1 仍在跑 + 任务书归档] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§12:27，rolled-from-MEMORY 2026-10-08 13:10）。

- [2026-10-08 13:10] [🩾 C1.full r1 健康巡检 #1（仍在跑）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§13:10，rolled-from-MEMORY 2026-10-08 14:20）。

- [2026-10-08 13:44] [🩾 C1.full r1 健康巡检 #2（仍在跑·grading 阶段）+ 补推 ahead1] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§13:44，rolled-from-MEMORY 2026-10-08 14:20）。

- [2026-10-08 15:04] [⏩ 已滚出] ❌→✅ C1.full r2 首启 EVAL_FAILED（缺四 override→158 Forbidden+grading crash）→重跑带 override→PID 1505377 运行中。详情已原文搬入 daily-memories/2026-10-08.md（§15:04，rolled-from-MEMORY 2026-10-08 16:15）。

- [2026-10-08 15:39] [⏩ 已滚出] 🩾 C1.full r2 健康巡检 #1（仍在跑）详情已原文搬入 daily-memories/2026-10-08.md（§15:39，rolled-from-MEMORY 2026-10-08 16:15）。

- [2026-10-08 16:15] [⏩ 已滚出] 🩾 C1.full r2 健康巡检 #2（仍在跑·~72min）+ 🚨论文树红线告警（git clean已消解）详情已原文搬入 daily-memories/2026-10-08.md（§16:15，rolled-from-MEMORY 2026-10-08 16:52）。

- [2026-10-08 16:52] [🩾 C1.full r2 健康巡检 #3（仍在跑·~108min）+ proxy自检通过 + 论文树告警已消解] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§16:52，rolled-from-MEMORY 2026-10-08 17:27）。

- [2026-10-08 17:27] [⏩ 已滚出] 🩾 C1.full r2 健康巡检 #4（仍在跑·~143min）+ proxy自检通过 详情已原文搬入 daily-memories/2026-10-08.md（§17:27，rolled-from-MEMORY 2026-10-08 18:03）。

- [2026-10-08 18:03] [⏩ 已滚出] 🩾 C1.full r2 健康巡检 #5（仍在跑·~180min·grading阶段）+ proxy自检通过 详情已原文搬入 daily-memories/2026-10-08.md（§18:03，rolled-from-MEMORY 2026-10-08 18:42）。

- [2026-10-08 18:42] [⏩ 已滚出] 🩾 C1.full r2 巡检#6（仍在跑·~219min·grading）+ proxy✅ + infra端口订正 详情已原文搬入 daily-memories/2026-10-08.md（§18:42，rolled-from-MEMORY 2026-10-08 19:20）。

- [2026-10-08 19:20] [⏩ 已滚出] 🩾 C1.full r2 巡检#7（仍在跑·~258min·grading外部执行）+ proxy自检通过 详情已原文搬入 daily-memories/2026-10-08.md（§19:20，rolled-from-MEMORY 2026-10-08 19:55）。

- [2026-10-08 19:55] [⏩ 已滚出] 🩾 C1.full r2 巡检#8（仍在跑·~292min·grading外部执行）+ proxy自检通过 详情已原文搬入 daily-memories/2026-10-08.md（§19:55，rolled-from-MEMORY 2026-10-08 20:33）。

- [2026-10-08 20:33] [⏩ 已滚出] 🩾 C1.full r2 巡检#9（仍在跑·~330min·grading外部执行）+ proxy自检通过 详情已原文搬入 daily-memories/2026-10-08.md（§20:33，rolled-from-MEMORY 2026-10-08 21:08）。

- [2026-10-08 21:08] [⏩ 已滚出] 🩾 C1.full r2 巡检#10（仍在跑·~364min）详情已原文搬入 daily-memories/2026-10-08.md（§21:08）。

- [2026-10-08 21:47] [🩾 C1.full r2 巡检#11（仍在跑·~402min·grading外部执行）+ proxy自检通过] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§21:47，rolled-from-MEMORY 2026-10-08 23:08）。

- [2026-10-08 23:08] [🩾 C1.full r3 巡检#1（仍在跑·~40min·generation阶段）+ proxy自检通过] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§23:08，rolled-from-MEMORY 2026-10-09 00:49）。

- [2026-10-08 23:42] [🩾 C1.full r3 巡检#2（仍在跑·~74min·generation阶段）+ proxy自检通过] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-08.md（§23:42，rolled-from-MEMORY 2026-10-09 00:49）。

- [2026-10-09 00:16] [⏩ 已滚出] 🩾 C1.full r3 巡检#3（仍在跑·~108min·generation阶段）+ proxy自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§00:16，rolled-from-MEMORY 2026-10-09 02:08）。

- [2026-10-09 00:49] [⏩ 已滚出] 🩾 C1.full r3 巡检#4（仍在跑·~141min·generation阶段）+ proxy/ops/legacy自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§00:49，rolled-from-MEMORY 2026-10-09 02:08）。

- [2026-10-09 02:08] [⏩ 已滚出] ❌→✅ C1.full r4 首跑infra作废(ECONNRESET)→重跑启动+ops重启 详情已原文搬入 daily-memories/2026-10-09.md（§02:08，rolled-from-MEMORY 2026-10-09 02:20）。

- [2026-10-09 02:20] [⏩ 已滚出] 🚨 BLOCKED: pro-fp4 403额度耗尽→r4两次infra作废→WAITING等恢复 详情已原文搬入 daily-memories/2026-10-09.md（§02:20）。

- [2026-10-09 03:02] [⏩ 已滚出] 🚨 BLOCKED续: pro-fp4仍403→继续WAITING等恢复 详情已原文搬入 daily-memories/2026-10-09.md（§03:02）。

- [2026-10-09 03:40] [⏩ 已滚出] 🚨 BLOCKED续: pro-fp4仍403→继续WAITING等恢复(第3次复检) 详情已原文搬入 daily-memories/2026-10-09.md（§03:40）。

- [2026-10-09 04:16] [⏩ 已滚出] 🚨 BLOCKED续: pro-fp4仍403→继续WAITING等恢复(第4次复检) 详情已原文搬入 daily-memories/2026-10-09.md（§04:16）。
- [2026-10-09 04:49] [⏩ 已滚出] 🚨 BLOCKED续：pro-fp4仍403→继续WAITING等恢复(第4次复检后) 详情已原文搬入 daily-memories/2026-10-09.md（§04:49）。
- [2026-10-09 05:24] [⏩ 已滚出] 🚨 BLOCKED续(第5次复检)：pro-fp4 直连仍 HTTP 403 → 继续 WAITING=1；⚠️发现代理伪装 200+HTML 假阳性 详情已原文搬入 daily-memories/2026-10-09.md（§05:24，rolled-from-MEMORY 2026-10-09 06:00）。

- [2026-10-09 06:00] [⏩ 已滚出] 🚨 BLOCKED续(第6次复检)：pro-fp4 直连仍 HTTP 403 → 继续 WAITING=1，状态不变 + proxy自检方法订正(取真loop PID) 详情已原文搬入 daily-memories/2026-10-09.md（§06:00，rolled-from-MEMORY 2026-10-09 06:37）。

- [2026-10-09 06:37] [⏩ 已滚出] 🚨 BLOCKED续(第7次复检)：pro-fp4 直连仍 HTTP 403 → 继续 WAITING=1，状态不变 + proxy自检通过(真loop PID3579323) 详情已原文搬入 daily-memories/2026-10-09.md（§06:37，rolled-from-MEMORY 2026-10-09 07:10）。

- [2026-10-09 07:45] [⏩ 已滚出] 🚨 BLOCKED续(第9次复检)：pro-fp4 直连仍 HTTP 403 → 继续 WAITING=1，状态不变 详情已原文搬入 daily-memories/2026-10-09.md（§07:45，rolled-from-MEMORY 2026-10-09 08:25）。

- [2026-10-09 08:25] [⏩ 已滚出] 🚨 BLOCKED续(第10次复检)：pro-fp4 直连仍 HTTP 403 → 继续 WAITING=1，状态不变 详情已原文搬入 daily-memories/2026-10-09.md（§08:25，rolled-from-MEMORY 2026-10-09 09:01）。

- [2026-10-09 09:01] [⏩ 已滚出] 🚨 BLOCKED续(第11次复检)：pro-fp4 直连仍 HTTP 403 → 继续 WAITING=1 详情已原文搬入 daily-memories/2026-10-09.md（§09:01，rolled-from-MEMORY 2026-10-09 09:45）。

- [2026-10-09 09:45] [⏩ 已滚出] ✅ pro-fp4 已恢复(新key e13f4f37 HTTP 200)→eval backbone re-auth→C1.full r4 启动(b2026_1009_094504 PID 3302534, 四override齐全, 0 Forbidden✅) 详情已原文搬入 daily-memories/2026-10-09.md（§09:45）。
- [2026-10-09 10:25] [⏩ 已滚出] 巡检 r4 运行中 + 收到运维2026-10-09(三)复测指令→已更新MEMORY复测流程 详情已原文搬入 daily-memories/2026-10-09.md（§10:25）。

- [2026-10-09 11:04] [⏩ 已滚出] 🩾 C1.full r4 巡检#2（仍在跑·~1h19m·generation阶段）+ 自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§11:04）。
- [2026-10-09 11:38] [⏩ 已滚出] 🩾 C1.full r4 巡检#3（仍在跑·~1h54m·generation阶段·task137）+ 自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§11:38）。
- [2026-10-09 12:12] [⏩ 已滚出] C1.full r4 巡检#4（仍在跑·~2h27m·task156/158）详情已原文搬入 daily-memories/2026-10-09.md（§12:12）。
- [2026-10-09 12:45] [⏩ 已滑出] C1.full r4 巡检#5（仍在跑·~3h00m·generation阶段）+ 自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§12:45）。
- [2026-10-09 13:23] [⏩ 已滚出] C1.full r4 巡检#6（仍在跑·~3h38m·task120）+ 自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§13:23）。
- [2026-10-09 13:59] [⏩ 已滚出] C1.full r4 巡检#7（仍在跑·~4h15m·task120）+ 自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§13:59）。
- [2026-10-09 14:37] [⏩ 已滚出] C1.full r4 巡检#8（仍在跑·~4h52m·task142 generation阶段）+ 自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§14:37）。
- [2026-10-09 15:14] [⏩ 已滚出] 🩾 C1.full r4 巡检#9（仍在跑·~5h29m·grading阶段·gen 140ok/12fail/6timeout）+ 全自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§15:14）。

- [2026-10-09 15:52] [⏩ 已滚出] 🩾 C1.full r4 巡检#10（仍在跑·~6h08m·grading阶段·run_eval.py etime 1h12m）+ 全自检通过 详情已原文搬入 daily-memories/2026-10-09.md（§15:52）。

- [2026-10-09 16:29] [🩾 C1.full r4 巡检#11（仍在跑·~6h44m·**grading阶段**·run_eval.py 611439 etime 1h48m 沙箱执行140脚本中）+ 全自检通过] pgrep → PID 3302534 仍在跑(etime 06:43:41, State=Ss, ppid=1✅); 子进程 611439=run_eval.py(etime 01:47:51, State=S); log 25.3MB last write 14:41:34(grading阶段正常无新输出); grep PASS_RATE/评估结果汇总=0 尚无最终结果。generation: 140ok/12fail/6timeout(6≤10✅,待PASS_RATE≥75%)。r4仍在跑未收割→本轮=巡检,不动作,不打断r4。自检：loop 3579323(ppid=1,etime 2d22h) environ含 https_proxy=http://172.19.92.23:13128 ✅(注:`pgrep -f 'zhulong_loop.sh'`误匹配cline编排进程1160429,真loop=3579323); 沙箱8650-8654全404✅ /home 13G(97%)✅(≥8G) git `## main...origin/main` clean✅(带proxy pull→Already up to date)。记忆维护：MEMORY 34533B>32KB→滚出巡检#10(15:52)为1行指针(原文在daily §15:52)。状态：STAGE=C1/CONFIG=full/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=2。下轮第一件事(不变)：pgrep→有输出=巡检退出; 无输出→收割r4→判据(timeout≤10且≥75%)→有效→retest r2(/tmp/ABL_full_r2_retest.log)→r3(/tmp/ABL_full_r3_retest.log)→r5→mean±std([r1=88.0,r2',r3',r4,r5])→just_finished→回填5表→C2。


