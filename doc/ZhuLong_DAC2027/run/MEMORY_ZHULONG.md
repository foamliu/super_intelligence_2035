# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（B 4/4✅；C1 pure_llm/rag/wo_retrieval 5/5✅；full(V2)锚点5/5✅=81.4±4.1%→运维指令(十二)补跑full_v3 r1 re-grade运行中）|
| CONFIG | `full_v3`（运维指令(十二)补跑「真full=自探索开」·.env切V3✅:API_INFO_MERGED_FILE=V3+SKILL_DATA_DIR=./docs/skill_data_selfexpl·4端口8650/8651/8652/8654✅+RAG:9006✅）|
| ROUND | 1（full_v3 第1轮）|
| PHASE | `running`（**full_v3 r1 code-gen✅完成→auto-grade❌1.3%(benchmark bug)→re-grade运行中·PID3478707·batch2026_1012_005319·log /tmp/ABL_full_v3_r1_regrade.log·158加载✅/144脚本组装✅→沙盒执行中(~10-20min)**。r1 code-gen stats:success=144/timeout=1/failure=0→timeout=1≤10✅·run_code=3407·ACCESS RESTRICTED=899✅·Forbidden=0✅。V2批full 5/5✅=81.4±4.1%已收割。loop PID61738✅有proxy·relay PID3277328✅alive。**下轮**:`pgrep -f run_eval.py`→有输出=巡检退出;无输出=收割r1 re-grade(grep pass\|PASS_RATE /tmp/ABL_full_v3_r1_regrade.log)→判据 timeout≤10且Pass@1≥75%→r1有效→r2→...→r5→5/5 mean±std→三组对照表(r1旧V3/full现V2=81.4±4.1%/full_v3新5轮)→是否复现r1~88%→进C2.phi_k10 |
| WAITING | 1 |
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-pro-fp4`（✅HTTP 200 新key e13f4f37 + /cloud/v1；r1-r3旧key 9eed3da1有效同后端 deepseek-v4-pro-260813, r4起新key）|

## 执行看板（15 臂 × 5 轮——已调换为 B→C1→C2→S1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| B | glm-5.2 | 5/5 ✅ | **83.3±3.1%** [84.2,87.3,84.2,79.1,81.6] |
| B | deepseek-v4-flash | 5/5 ✅ | **16.7±12.3%** [9.5,10.1,19.0,7.6,37.3] |
| B | kimi-k2.6-cloud | 5/5 ✅ | **77.0±1.6%** [79.1,76.6,77.2,74.7,77.2] |
| B | doubao-seed-2.0-pro-cloud | 5/5 ✅ | **63.8±1.4%** [63.9,64.6,61.4,65.2,63.9] |
| C1 | pure_llm | 5/5 ✅ | ✅ 10.5±1.9%（复用 legacy：[8.2,9.5,10.1,11.4,13.3]）|
| C1 | rag | 5/5 ✅ | **71.8±2.5%** [70.3,72.2,69.6,70.9,75.9] |
| C1 | wo_retrieval | 5/5 ✅ | **81.0±4.5%** [74.1,86.1,81.6,79.7,83.5] |
| C1 | full(V2)（锚点）| **5/5 ✅ 81.4±4.1%** | [88.0,79.1,77.2,80.4,82.3]（r1=V3文档,r2-r5=V2无自探索→混配置→运维指令(十二)补跑full_v3）|
| C1 | full_v3(自探索) | **r1 re-grade运行中** (PID3478707·batch2026_1012_005319·log /tmp/ABL_full_v3_r1_regrade.log) | 运维指令(十二)补跑「真full=自探索开」·.env切V3✅·r1 code-gen✅(timeout=1≤10)·auto-grade❌1.3%(bug)·re-grade沙盒执行中 |
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
| B.deepseek-v4-flash | **16.7 ± 12.3%** | [9.5, 10.1, 19.0, 7.6, 37.3]（r1=9.5% b2026_1006_022818；r2=10.1% b2026_1006_031227；r3=19.0% b2026_1006_034557；r4=7.6% b2026_1006_042140；r5=37.3% b2026_1006_045811, 0 Forbidden✅）|
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2]（b2026_1006_071809/100626/181646/204422/230904, 0 Forbidden✅）|
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9]（b2026_1007_010601/030335/050414/083426/095002, 0 Forbidden✅）|
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | **81.0 ± 4.5%** | [74.1, 86.1, 81.6, 79.7, 83.5]（r1=74.1%复用legacy；r2=86.1% b2026_1007_221959；r3=81.6% b2026_1008_015818；r4=79.7% b2026_1008_0507；r5=83.5% b2026_1008_081817, 0 Forbidden✅；旧r2作废0/158 pro-fp4 403不计数）|
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9]（b2026_1007_112101/131535/163343/183007/202448, 0 Forbidden✅；旧r3作废b2026_1007_151301 0/158不计数；legacy 68.2±7.4%作废）|
| C1.full(V2)（锚点）| **81.4 ± 4.1%** ✅ 5/5 | [88.0, 79.1, 77.2, 80.4, 82.3]（r1=88.0% b2026_1010_140631·V3文档；r2=79.1% b2026_1011_112839·V2·timeout=3；r3=77.2% b2026_1011_145925·V2·timeout=2；r4=80.4% b2026_1011_181038·V2·timeout=4；r5=82.3% b2026_1011_212324·V2·timeout=1·re-grade✅。**注**:r1=V3(10-10 15:32前),r2-r5=V2无自探索→混配置→运维指令(十二)补跑full_v3）|
| C1.full_v3(自探索) | ⏳ r1 running | 运维指令(十二)补跑「真full」(V3+自探索)·r1(batch2026_1012_005319)code-gen进行中 |

## 操作流水
- [2026-10-12 02:12] ⠈ **巡检(full_v3 r1 code-gen ~79min健康·不动作退出)**：pgrep run_cline_script→有输出(PID3005888·ELAPSED 4780s·RSS3072·Ss)·cline子进程PID3324057(ELAPSED45s=新task刚起)·log 18MB增长中·run_code=2744·ACCESS RESTRICTED=792✅(hook live)·Forbidden=0✅·MCP-32001timeout=16(正常per-call)·stats汇总未现(Step2·code-gen进行中)·batch2026_1012_005319。4端口4/4✅@10.129.32.75·.env复检:V3+selfexpl+8650set+RAG:9006+OMEGA=high+READBACK=full+PHI_BUDGET=0✅·MCP:8090+18890✅。loop PID61738✅有proxy·relay PID3277328✅alive(.last_run_id=48)·/home=4G(授权)。⚠️TASK书=39684B(~38.7KB)>32KB→下轮需归档(十)(十一)块。状态不变 C1/full_v3/r1/running/WAITING=1/ERROR_COUNT=0。下轮:pgrep→有=巡检;无=收割r1(re-grade:--benchmark EDA-Eval-pyAether-158.jsonl --lang pyAether·log /tmp/ABL_full_v3_r1_regrade.log)→timeout≤10且Pass@1≥75%→r1有效→r2→...→r5→三组对照表→进C2.phi_k10。
- [2026-10-12 01:29] 🔎 **巡检(full_v3 r1 code-gen ~46min健康·不动作退出)**：pgrep run_cline_script→有输出(PID3005888)·log 9.4MB mtime 01:30(增长中)·batch2026_1012_005319。.env复检V3+selfexpl+4端口8650set+RAG:9006+FEEDBACK=full✅。MCP PID3000860@8090✅。loop PID61738✅有proxy·relay PID3277328✅alive·/home=4G(授权)。MEMORY归档3条旧流水+精简看板/状态头→<32KB。状态不变 STAGE=C1/CONFIG=full_v3/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮:pgrep→有=巡检;无=收割r1(re-grade:--benchmark EDA-Eval-pyAether-158.jsonl --lang pyAether·log /tmp/ABL_full_v3_r1_regrade.log)→timeout≤10且Pass@1≥75%→r1有效→r2→...→r5→三组对照表→进C2.phi_k10。
- [2026-10-12 00:43] [⏩ 已滚出] ✅ r5 re-grade=82.3%→full(V2)5/5=81.4±4.1%→.env切V3+MCP重启+full_v3 r1启动 详情见 daily-memories/2026-10-12.md §00:43。
- [2026-10-12 00:07] [⏩ 已滚出] ✅ r5 code-gen完成→auto-grade❌1.9%(benchmark bug)→re-grade启动 详情见 daily-memories/2026-10-12.md §00:07。
- [2026-10-11 11:31] [⏩ 已滚出] 🔄 r2 re-run code-gen 启动·3项修复完成 详情见 daily-memories/2026-10-11.md §11:31。
- [2026-10-10 21:45→15:35] [⏩ 已滚出] 5条(运维指令六/四/三·巡检·exec_code patch) 详情见 daily-memories/2026-10-10.md。
- [2026-10-09 01:28] [⏩ 已滚出] ✅ C1.full r3 收割 63.3%→r4 启动 详情见 daily-memories/2026-10-09.md §01:28。
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

- [2026-10-08 ~ 10-10 10:18] [⏩ 已滚出] 10-08~10-10 早段流水（wo_retrieval r3-r5巡检 / full r1-r3 / r2-retest#1~#5 / pro-fp4 403 BLOCKED×11 / 换专属沙盒指令(一)→(二)）全部详情见 daily-memories/2026-10-08.md ~ daily-memories/2026-10-10.md。

- [2026-10-10 11:36] [⏩ 已滚出] 🔄 运维指令(一)换专属沙盒·pre-check②不过 详情见 daily-memories/2026-10-10.md（rolled 01:26）。
- [2026-10-10 12:15] [⏩ 已滚出] ⠈ 复检(端口仍全CLOSED·不动作) 同§12:52口径复检（端口仍全CLOSED,状态不变）详情见 daily-memories/2026-10-10.md（§12:52）。
- [2026-10-10 12:52] [⏩ 已滚出] ⠈ 复检(端口仍全CLOSED·不动作·第3次) 详情已搬入 daily-memories/2026-10-10.md（§12:52）。
- [2026-10-10 13:27] [⏩ 已滚出] ⠈ 复检(端口部分恢复·8667OPEN·3/4仍CLOSED) 详情见 daily-memories/2026-10-10.md（rolled 01:26）。
- [2026-10-10 14:04] [⏩ 已滚出] ✅ 三前置全过→C1.full r1 已启动(PID2518857) 详情见 daily-memories/2026-10-10.md（rolled 01:26）
- [2026-10-10 15:35] [⏩ 已滚出] 🔄 运维指令(二)执行→r1=88.0%保留+r2_new启动(PID2953852) 详情见 daily-memories/2026-10-10.md（rolled 01:26）。

- [2026-10-10 16:55] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段) 详情见 daily-memories/2026-10-10.md（rolled 01:26）。

- [2026-10-10 17:32] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段,2h) 详情见 daily-memories/2026-10-10.md（rolled 01:26）。
- [2026-10-10 18:06] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段,2.5h) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 18:40] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 19:14] [⏩ 已滚出] 🔻 r2_new 收割=73.4%❌ → 启动 r2_new2(retry#1) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 19:52] [⏩ 已滚出] ⠈ 巡检(r2_new2 code-gen 阶段) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 20:27] [⏩ 已滚出] ⠈ 巡检(r2_new2 code-gen 阶段,71m) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 20:49] [⏩ 已滚出] 🔬 根因排查完成(运维指令(四)/(三))·port 8667挂死+MCP 60s太短 详情见 daily-memories/2026-10-10.md §20:49。
- [2026-10-10 22:39] [⏩ 已滚出] 🔄 运维指令(七)执行+auth修复→r2_new重启(8端口) 详情见 daily-memories/2026-10-10.md §22:39。

- [2026-10-10 23:25] [⏩ 已滚出] 🔄 运维指令(八)执行→4端口回退+timeout:180→2/4端口挂死→blocked 详情见 daily-memories/2026-10-11.md §归档10-10。
- [2026-10-11 00:08] [⏩ 已滚出] ⠈ 巡检→发现 r2_new 已在运行（端口恢复·前轮agent启动未记录） 详情见 daily-memories/2026-10-11.md §归档10-11。
- [2026-10-11 00:52] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段 ~70%·不动作) 详情见 daily-memories/2026-10-11.md §00:52。
- [2026-10-11 01:26] [⏩ 已滚出] ⠈ 巡检(r2_new grading 阶段启动·不动作) 详情见 daily-memories/2026-10-11.md §01:26。
- [2026-10-11 02:05] [⏩ 已滚出] ⠈ 巡检(r2_new grading 阶段·不动作) 详情见 daily-memories/2026-10-11.md §02:05。
- [2026-10-11 02:41] [⏩ 已滚出] ⠈ 巡检(r2_new 仍跑·~3h·summary 未出·不动作) 详情见 daily-memories/2026-10-11.md §02:41。
- [2026-10-11 03:15] [⏩ 已滚出] ⠈ 巡检(r2_new 仍跑·~3.5h·summary 未出·不动作) 详情见 daily-memories/2026-10-11.md §03:15。
- [2026-10-11 03:49] [⏩ 已滚出] ⠈ 巡检(r2_new 仍跑·~4h5m·summary未出·不动作) 详情见 daily-memories/2026-10-11.md §03:49。
- [2026-10-11 04:24] [⏩ 已滚出] ⠈ 巡检(r2_new 末段·152/158 done·summary未出·不动作) 详情见 daily-memories/2026-10-11.md §04:24。
- [2026-10-11 05:01] [⏩ 已滚出] ⠈ 巡检(r2_new 末段·153/158 done·7 timeout≤10✅·5 remaining·summary未出·不动作) 详情见 daily-memories/2026-10-11.md §05:01。
- [2026-10-11 05:40] [⏩ 已滚出] ⠈ 巡检(r2_new 末段·156/158 done·timeout=10=≤10边界⚠️·2 remaining·summary未出·不动作) 详情见 daily-memories/2026-10-11.md §05:40。
- [2026-10-11 06:16] [⏩ 已滚出] ⠈ 巡检(r2_new 末段·156/158 done·timeout=10边界⚠️·summary未出·不动作) 详情见 daily-memories/2026-10-11.md §06:16。
- [2026-10-11 07:00] [⏩ 已滚出] ⠈ **收割 r2_new + infra 全挂→PHASE=blocked** 详情见 daily-memories/2026-10-11.md §07:00。
- [2026-10-11 08:18] [⏩ 已滚出] ⠈ **(九)执行确认+4端口恢复4/4健康✅→仅/home<8G阻塞→WAITING=1** 详情见 daily-memories/2026-10-11.md §08:18。
- [2026-10-11 08:57] [⏩ 已滚出] ⠈ 巡检(r2 batch2026_1011_083246已起跑·code-gen阶段·canary✅·4端口4/4✅@10.129.32.75·⚠️RAG:9006当时未监听·不动作) 详情见 daily-memories/2026-10-11.md §08:57。该批后判❌INVALIDATED(5.7%)。
- [2026-10-11 09:37] [⏩ 已滚出] ⏈ 巡检(r2 batch083246 code-gen 123/158·run_cline_script.sh已死·不动作) 详情见 daily-memories/2026-10-11.md §09:37。该批后判❌INVALIDATED(5.7%)。
- [2026-10-11 10:20] [⏩ 已滚出] ⏈ r2 batch083246 code-gen完成(158/158)→手动grading启动→结果5.7%❌INVALIDATED 详情见 daily-memories/2026-10-11.md §10:20。
- [2026-10-11 12:12] [⏩ 已滚出] ⠈ 巡检(r2 code-gen 43min 健康 不动作) 详情见 daily-memories/2026-10-11.md §14:18归档。
- [2026-10-11 12:22] [⏩ 已滚出] ⏈ 巡检(r2 code-gen 53min 健康 不动作) 详情见 daily-memories/2026-10-11.md §14:18归档。
- [2026-10-11 13:00] [⏩ 已滚出] ⏈ 巡检(r2 code-gen ~1h32m 健康 不动作) 详情见 daily-memories/2026-10-11.md §14:18归档。
- [2026-10-11 13:34] [⏩ 已滚出] ⏈ 巡检(r2 code-gen ~2h6m 146/158 done 健康 不动作) 详情见 daily-memories/2026-10-11.md §14:18归档。
- [2026-10-11 14:18] [⏩ 已滚出] 🔧 r2 code-gen完成→grading config bug修复→re-grade启动(PID518337) 详情见 daily-memories/2026-10-11.md §14:18。
- [2026-10-11 14:57] [⏩ 已滚出] ✅ r2 收割=79.1%有效→r3 启动(PID679772) 详情见 daily-memories/2026-10-11.md §14:57。
- [2026-10-11 15:35] [⏩ 已滚出] ⠈ 巡检(r3 code-gen ~38min 健康·不动作退出) 详情见 daily-memories/2026-10-11.md §15:35。
- [2026-10-11 16:10] [⏩ 已滚出] ⠈ 巡检(r3 code-gen ~1h11m 健康·不动作退出) 详情见 daily-memories/2026-10-11.md §17:20。
- [2026-10-11 16:44] [⏩ 已滚出] ⠈ 巡检(r3 code-gen ~1h45m 健康·不动作退出) 详情见 daily-memories/2026-10-11.md §17:20。
- [2026-10-11 17:20] [⏩ 已滚出] ⠈ 巡检(r3 code-gen ~2h21m 健康·不动作退出) 详情见 daily-memories/2026-10-11.md §17:20。
- [2026-10-11 17:55→18:48] [⎩ 已滚出] 🔧✅ r3 code-gen✅→auto-grade❌1.9%(bug)→re-grade✅122/158(77.2%)→r4启动(PID1428769)→巡检38min健康 详情见 daily-memories/2026-10-11.md §17:55/§18:09/§18:48。

- [2026-10-11 19:23] [⏩ 已滚出] ⠈ 巡检(r4 code-gen ~1h13m 健康·不动作退出) 详情见 daily-memories/2026-10-11.md §19:23。
- [2026-10-11 20:00] ⠈ **巡检(r4 code-gen ~1h50m 健康·不动作退出)**：pgrep `run_cline_script`→有输出(PID1428769·ELAPSED 01:50:11·RSS 3584·Ss)·log /tmp/ABL_full_r4_8650set.log 20MB/189738行·run_code=3441·ACCESS RESTRICTED=817✅(hook live)·Forbidden=0✅·stats汇总未现(Step2中·code-gen进行中)。4端口4/4✅@10.129.32.75·MCP:8090+18890✅·RAG:9006✅·loop PID61738✅有proxy(https_proxy=http://172.19.92.23:13128)·relay alive(.last_run_id=40)·/home=4G(用户授权)。按状态机 pgrep 有输出→不动作退出。状态不变 STAGE=C1/CONFIG=full/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮:pgrep→有=巡检;无=收割r4(re-grade同r3·--benchmark EDA-Eval-pyAether-158.jsonl --lang pyAether·log /tmp/ABL_full_r4_regrade.log)→timeout≤10且Pass@1≥75%→r4有效→r5→5/5 mean±std→回填5表→just_finished→C2.phi_k10。


- [2026-10-11 21:20] [⏩ 已滚出] ✅ r4收割=80.4%有效→r5启动(PID2181703) 详情见 daily-memories/2026-10-11.md §21:20。
- [2026-10-11 22:00] [⏩ 已滚出] ⠈ 巡检(r5 code-gen ~37min 健康·不动作退出) 详情见 daily-memories/2026-10-11.md §22:00。
- [2026-10-11 22:42] [⏩ 已滚出] 🔎✅ RAG排查完成→报告reports/RAG_AUDIT_2026-10-11.md 详情见 daily-memories/2026-10-11.md §22:42。
- [2026-10-12 02:50] ✅ **full_v3 r1 code-gen✅完成→auto-grade❌1.3%(benchmark bug)→re-grade启动(PID3478707)**：pgrep `run_cline_script`→无输出(PID3005888已结束)=full_v3 r1 eval完成。r1(batch2026_1012_005319)code-gen✅：stats success=144/timeout=1/failure=0→158/158 done·**timeout=1≤10✅**·run_code=3407·ACCESS RESTRICTED=899✅(hook live)·Forbidden=0✅·0 exec_err。**但auto-grade❌1.3%(2/158 pass)**：同根因(run_eval.py patch_config()默认替换benchmark→155/158 task_id未找到→仅3脚本组装)。**修复=re-grade**：创建run/run_full_v3_r1_regrade.sh(--benchmark EDA-Eval-pyAether-158.jsonl --lang pyAether + EVAL_FW_DIR)→setsid启动→log /tmp/ABL_full_v3_r1_regrade.log·PID3478707✅·**158加载✅(vs broken:3)·144脚本组装✅(vs broken:3)**→沙盒执行中(连接远程10.129.32.75:8650/8651/8652/8654✅)。.env复检:API_INFO_MERGED_FILE=V3✅+SKILL_DATA_DIR=skill_data_selfexpl✅+PROXY_PORTS=8650,8651,8652,8654✅+RAG:9006✅。loop PID61738✅有proxy·relay PID3277328✅alive·/home=4G(用户授权)。状态 STAGE=C1/CONFIG=full_v3/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮第一件事**：pgrep -f run_eval.py→有输出=巡检退出;无输出=grep -E 'pass \\(|PASS_RATE|通过率' /tmp/ABL_full_v3_r1_regrade.log | tail -10→拿Pass@1→判据 timeout≤10且Pass@1≥75%→r1有效→r2(log /tmp/ABL_full_v3_r2_8650set.log)→...→r5→5/5 mean±std→三组对照表→进C2.phi_k10。

- [2026-10-11 20:39] ✅ **r4 code-gen完成→auto-grade❌1.9%(benchmark bug)→re-grade启动(PID2014730)**：pgrep run_cline_script→无输出=r4 eval已结束。r4(batch2026_1011_181038)code-gen✅：stats success=154/timeout=4/failure=0→158/158 done·timeout=4≤10✅·run_code=4027·ACCESS RESTRICTED=911✅(hook live)·Forbidden=0✅·0 exec_err。**但auto-grade❌1.9%(3/158 pass)**：同根因(run_eval.py patch_config()默认替换benchmark为不存在的v20260416/v20260602→154/158“未找到task_id”→仅3脚本组装)，同r2/r3同根因。**修复=re-grade**：创建run/run_r4_grading.sh(--benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl --lang pyAether + EVAL_FW_DIR)→setsid启动→log /tmp/ABL_full_r4_regrade.log·PID2014730/2014736✅·**158加载✅(vs broken:3)·145脚本组装✅(vs broken:3)**→沙盒执行中(连接远程10.129.32.75:8650/8651/8652/8654全OPEN✅)。r1=88.0%✅+r2=79.1%✅+r3=77.2%✅。loop PID61738✅有proxy(https_proxy=http://172.19.92.23:13128)·relay alive(.last_run_id=40)·/home=4G(用户授权)。状态 STAGE=C1/CONFIG=full/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮第一件事**：pgrep -f run_eval.py→有输出=巡检退出;无输出=grep -E ‘pass \(|PASS_RATE|通过率|评估结果汇总’ /tmp/ABL_full_r4_regrade.log | tail -10→拿Pass@1→判据 timeout≤10且Pass@1≥75%→r4有效→r5(log /tmp/ABL_full_r5_8650set.log)→5/5=[88.0,79.1,77.2,r4,r5]mean±std→回填5表锚点→PHASE=just_finished→进C2.phi_k10。