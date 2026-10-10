# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（Phase B 4/4✅；C1 pure_llm/rag/wo_retrieval 5/5✅；**full 锚点 r1=88.0%保留，r2-r5 换专属沙盒 8663/8666/8667/8670 重跑中**）|
| CONFIG | `full`（C1 第4臂=锚点；**2026-10-10 运维指令(二)：r1=88.0%保留作锚点，r2/r3/r4/r5 全部旧成绩作废（旧沙盒 8650-8654 已弃用），换专属沙盒 8663/8666/8667/8670 workdir e0031982_1~4 重跑**。key e13f4f37+/cloud/v1 pro-fp4 HTTP 200✅。**exec_code.py+run_on_sandbox.py 已 patch 加入 `host` 字段**（新沙盒必需，旧沙盒不需要））|
| ROUND | 2 |
| PHASE | `running`（**2026-10-10(二) r1保留+重跑r2-r5**：r1=88.0%✅保留作锚点。**r2_new(attempt#1)=73.4%❌低于75%判据**（116/158 pass, 131ok/23fail/0exec_err, timeout=4≤10✅ 但 Pass@1 73.4%<75%❌；根因=MCP pyAether 60s timeout 致 23 个 code-gen 失败）。**r2_new2(retry#1)已启动(PID4063726,batch2026_1010_191625,log /tmp/ABL_full_r2_new2.log)**：四 override /proc/4063726/environ✅；.env=8663/8666/8667/8670✅；0 Forbidden✅；ACCESS RESTRICTED=14 canary live✅；0 host-error✅。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new2(grep -E 'pass \(\|PASS_RATE\|评估结果汇总\|timeout' /tmp/ABL_full_r2_new2.log\|tail -10)→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new(log /tmp/ABL_full_r3_new.log)→r4_new→r5_new；仍不达标→retry#2(log /tmp/ABL_full_r2_new3.log)→retry#3→3次仍不达标→WAITING=1 等运维）|
| WAITING | 1 |
| ERROR_COUNT | 0（**2026-10-10(二) r1保留+重跑r2-r5，ERROR_COUNT 归零**。关键修复：exec_code.py/run_on_sandbox.py 加 host 字段）|
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
| C1 | full（锚点）| **r2_new2 retry#1 运行中** | 🔄2026-10-10(二) r1=88.0%✅保留作锚点；r2/r3/r4/r5 旧成绩全作废。换专属沙盒 8663/8666/8667/8670。host patch✅。**r2_new(attempt#1)=73.4%❌(<75%判据,116/158,timeout=4,MCP 60s timeout 致23 gen-fail)**→retry#1: **r2_new2 已启动(PID4063726,batch2026_1010_191625,log /tmp/ABL_full_r2_new2.log)** 四 override✅/0 Forbidden✅/ACCESS RESTRICTED=14 canary✅/0 host-error✅ |
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
| C1.full（锚点）| ⍌ 1/5 (r1=88.0%保留) **r2_new2 retry#1 运行中** | r1=88.0% ✅**保留**（0 timeout，旧沙盒正常时跑的）；r2=59.5% / r2-retest#1~#5 / r3=63.3% / r4=81.0% → 全部 ❌作废（旧沙盒 8650-8654 已弃用）。换专属沙盒 8663/8666/8667/8670 workdir e0031982_1~4 重跑。host patch✅。**r2_new(attempt#1)=73.4%❌低于75%判据**（116/158 pass, 131ok/23fail/0exec_err, timeout=4；根因 MCP pyAether 60s timeout 致 23 gen-fail）→**r2_new2(retry#1)已启动 PID4063726 batch2026_1010_191625 log /tmp/ABL_full_r2_new2.log** |

## 操作流水
- [2026-10-10 16:14] ⠈ 巡检(r2_new运行中·code-gen阶段·不动作)：PID2953852 alive(2429s≈40min),log 76967行/0 Forbidden✅/ACCESS RESTRICTED=445(canary live✅)/30 MCP-32001(code-gen正常)/0 pass(未进grading)。四override /proc/2953852/environ 4/4✅。真loop PID3579323 environ https_proxy✅(自检通过)。/home=4.4G⚠️(99%满,非三前置项)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮：pgrep→有输出=巡检退出;无输出=收割r2_new(grep -E 'pass \(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r2_new.log|tail -10)→判据timeout≤10且Pass@1≥75%→有效→启r3_new(/tmp/ABL_full_r3_new.log)→r4_new→r5_new→5/5=[r1=88.0(保留),r2_new,r3_new,r4_new,r5_new]算mean±std→回填锚点→PHASE=just_finished。
- [2026-10-10 15:35] [✅ exec_code.py+run_on_sandbox.py patch host 字段 → C1.full r2_new 启动] §运维指令(二)：r1=88.0%保留作锚点，r2/r3/r4/r5 全部旧成绩作废（旧沙盒 8650-8654 已弃用），换专属沙盒 8663/8666/8667/8670 workdir e0031982_1~4 重跑。**关键修复**：新沙盒要求 HTTP payload 含 `"host"` 字段（aether/virtuoso/waveview/innovus），旧 `exec_code.py`（run_code_http）只发 `{"code","lang"}`→patch 加 `_LANG_TO_HOST` 映射+payload 加 `host`；`run_on_sandbox.py`（grading 阶段）只发 `{"code"}`→patch 加 `lang`+`host`（env 可配,默认 pyAether/aether）。两文件 py_compile 通过✅。eda_fastmcp restart(PID2933041)✅。**沙盒实测 4/4 全过**：run_code_http 实跑 `print("hello from port XXXX")`→4端口全 "The code execution was successful"✅。清理 r1 孤儿进程（PID 2786005/2786006 timeout+cline from 2026_1010_140631 eval, parent=1 orphaned）✅。**r2_new 启动**（PID2953852,batch2026_1010_153503,log /tmp/ABL_full_r2_new.log）：四 override /proc/2953852/environ 全在✅(EVAL_FW_DIR/CLI_DATA_DIR=.cline_prof4_eval/data/PYTHON/https_proxy)；.env=8663/8666/8667/8670✅；0 Forbidden✅；ACCESS RESTRICTED=10→反作弊 hook live→canary PASS✅；0 host-field-error✅。**状态**：STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮：pgrep→有输出=巡检退出;无输出=收割 r2_new→判据 timeout≤10 且≥75%→启 r3_new。
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

- [2026-10-08 ~ 10-10 10:18] [⏩ 已滚出] 10-08~10-10 早段流水（wo_retrieval r3-r5巡检 / full r1-r3 / r2-retest#1~#5 / pro-fp4 403 BLOCKED×11 / 换专属沙盒指令(一)→(二)）全部详情见 daily-memories/2026-10-08.md ~ daily-memories/2026-10-10.md。

- [2026-10-10 11:36] 🔄 运维指令(一)换专属沙盒：全部C1.full作废→三项前置复检(①pro-fp4 HTTP=200✅curl 1.3s ②新端口8663/8666/8667/8670全CLOSED❌Connection refused,HTTP=000 ③eval IDLE✅r2-retest#5被ops kill,ps无残留,无Pass@1)→**pre-check②不过→不启动r1→WAITING=1等新沙盒恢复**。.env已改为8663/8666/8667/8670+e0031982_1~4@10.129.32.75。旧端口8650-8654仍OPEN(404)但红线🚫禁回退。/home=5.4G⚠️。状态更新 ROUND=1/ERROR_COUNT=0(归零)/全部C1.full成绩作废。下轮第一件事：复检8663/8666/8667/8670全OPEN→canary→启C1.full r1(四override,log /tmp/ABL_full_r1.log);仍CLOSED→WAITING=1。
- [2026-10-10 12:15] [⏩ 已滚出] ⠈ 复检(端口仍全CLOSED·不动作) 同§12:52口径复检（端口仍全CLOSED,状态不变）详情见 daily-memories/2026-10-10.md（§12:52）。
- [2026-10-10 12:52] [⏩ 已滚出] ⠈ 复检(端口仍全CLOSED·不动作·第3次) 详情已搬入 daily-memories/2026-10-10.md（§12:52）。
- [2026-10-10 13:27] ⠈ 复检(端口部分恢复·不动作·第4次)：三项前置复检 ①pro-fp4 HTTP=200✅(1.18s,key e13f4f37+/cloud/v1) ②**8667=404(OPEN✅新恢复!)，8663/8666/8670仍CLOSED❌(HTTP=000)**→仅1/4端口OPEN，需4/4才能并行分片→旧端口8650-8654仍OPEN(404)红线🚫禁回退 ③eval IDLE✅(pgrep无输出) → **pre-check②不过(3/4 CLOSED)→不启动r1→WAITING=1**。真loop PID3579323(PPID=1)environ https_proxy✅。/home=5.6G⚠️(99%满,低于8G)。.env确认=8663/8666/8667/8670+e0031982_1~4@10.129.32.75。状态不变 STAGE=C1/CONFIG=full/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**进展**：8667自12:52后恢复(沙盒正逐端口上线)。下轮第一件事：复检8663/8666/8670→全OPEN+三项全过→canary→启C1.full r1(四override,log /tmp/ABL_full_r1.log);仍有CLOSED→继续WAITING=1。
- [2026-10-10 14:04] ✅ 三前置全过→C1.full r1 已启动(PID2518857)：①pro-fp4 HTTP=200✅(1.29s,full key 02_...e13f4f37-836a-...+/cloud/v1) ②**新端口 8663/8666/8667/8670 全 OPEN✅(全 HTTP=404,非超时)**@10.129.32.75(13:27 仅 8667 OPEN→14:04 全恢复) ③eval IDLE✅(pgrep '^bash scripts/run_cline_script'无输出;r2-retest#4 已 kill 确认)。四 override 核验 /proc/2518857/environ 全在(EVAL_FW_DIR/CLI_DATA_DIR/PYTHON/https_proxy)✅。.env=8663/8666/8667/8670+e0031982_1~4✅。log /tmp/ABL_full_r1.log 已 3093 行/0 Forbidden✅/0 pass(尚在 code-gen 阶段)。真loop PID3579323 environ https_proxy✅(自检通过无需重启)。/home=5.5G⚠️(99%满,非三前置项)。状态不变 STAGE=C1/CONFIG=full/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r1(grep -E 'pass \(\|评估结果汇总\|timeout' /tmp/ABL_full_r1.log\|tail -10)→判据 timeout≤10 且 Pass@1≥75%→有效→启 r2(/tmp/ABL_full_r2.log)→r3→r4→r5→5/5 算 mean±std→回填锚点→PHASE=just_finished。
- [2026-10-10 15:35] 🔄 运维指令(二)执行：r1=88.0%✅保留作锚点（不重跑），r2/r3/r4/r5 旧成绩全作废→换专属沙盒 8663/8666/8667/8670 workdir e0031982_1~4 重跑。exec_code.py+run_on_sandbox.py 已 patch 加 host 字段（新沙盒必需）。沙盒实测 4/4 全过✅（run_code 实跑 print("hello")→4端口全 successful✅）。C1.full r2_new 已启动(PID2953852,batch2026_1010_153503,log /tmp/ABL_full_r2_new.log)：四 override /proc/2953852/environ✅ / .env=8663/8666/8667/8670✅ / 0 Forbidden✅ / ACCESS RESTRICTED=10 canary PASS✅ / 0 host-error✅。状态 ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。

- [2026-10-10 16:55] ⠈ 巡检(r2_new 运行中·code-gen 阶段·不动作)：eval PID2953852 alive, log 132688 行/mtime 16:55(活跃), 0 Forbidden✅, 0 host-error✅, ACCESS RESTRICTED=601(canary live✅), 149 MCP timeout(60s,code-gen 正常重试), 0 pass(尚未 grading)。四 override /proc/2953852/environ✅。真loop PID3579323 environ https_proxy✅(自检通过)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new(grep -E 'pass \\(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r2_new.log|tail -10)→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new(log /tmp/ABL_full_r3_new.log)→r4_new→r5_new→5/5=[r1=88.0(保留),r2_new,r3_new,r4_new,r5_new]算 mean±std→回填锚点→PHASE=just_finished。

- [2026-10-10 17:32] ⠈ 巡检(r2_new 运行中·code-gen 阶段·不动作)：eval PID2953852 alive(elapsed 01:57:51,PPID=1 setsid✅), log 180916 行/mtime 17:32:55(活跃增长), 0 Forbidden✅, 0 host-field-error✅(host patch 工作正常), ACCESS RESTRICTED=709(canary/反作弊 live✅), 0 MCP-timeout, 221 timeout(code-gen 阶段正常), 0 pass(尚未 grading)。sandbox 正常执行代码(run_code 调用含 successful/pyAether 代码可见✅)。四 override /proc/2953852/environ✅(EVAL_FW_DIR/CLI_DATA_DIR=.cline_prof4_eval/data/PYTHON/https_proxy 全在)。真loop PID3579323 environ https_proxy✅(自检通过无需重启)。/home=4.0G⚠️(99%满,低于8G,但 eval 数据在 /nasdata + log 在 /tmp,不影响本轮)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new(grep -E 'pass \\(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r2_new.log|tail -10)→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new(log /tmp/ABL_full_r3_new.log)→r4_new→r5_new→5/5=[r1=88.0(保留),r2_new,r3_new,r4_new,r5_new]算 mean±std→回填锚点→PHASE=just_finished。
- [2026-10-10 18:06] ⠈ 巡检(r2_new 运行中·code-gen 阶段·不动作)：eval PID2953852 alive(elapsed 02:31:41,PPID=1 setsid✅), log 24.3MB/mtime 18:06(活跃增长), 0 Forbidden✅, 0 host-field-error✅(host patch 工作正常), ACCESS RESTRICTED=835(canary/反作弊 live✅), MCP 60s timeout 若干(code-gen 正常重试), 尚无 评估结果汇总(未进 grading)。pgrep 'run_eval.py' 命中的 PID3764650/3766091 实为真loop(PPID=3579323)的 cline 编排进程(命令行含任务书文本故误匹配),非 grading。sandbox 正常执行代码(run_code 调用 successful/pyAether 可见✅)。四 override /proc/2953852/environ✅(EVAL_FW_DIR/CLI_DATA_DIR=.cline_prof4_eval/data/PYTHON/https_proxy 全在)。.env=8663/8666/8670/8670+e0031982_1~4@10.129.32.75✅。真loop PID3579323 environ https_proxy✅(自检通过无需重启)。/home=3.5G⚠️(100%满,低于8G,但 eval 数据在 /nasdata + log 在 /tmp,不影响本轮)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new(grep pass/PASS_RATE/评估结果汇总/timeout /tmp/ABL_full_r2_new.log|tail -10)→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new(log /tmp/ABL_full_r3_new.log)→r4_new→r5_new→5/5=[r1=88.0(保留),r2_new,r3_new,r4_new,r5_new]算 mean±std→回填锚点→PHASE=just_finished。
- [2026-10-10 18:40] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 19:14] 🔻 **r2_new(attempt#1)收割=73.4%❌低于75%判据** → 启动 r2_new2(retry#1)：eval PID2953852 已 DEAD✅(pgrep '^bash scripts/run_cline_script'=IDLE✅)。收割 `/tmp/ABL_full_r2_new.log`：`PASS_RATE: 0.7342 / 116/158 pass (73.4%) / 131 ok, 23 fail, 0 exec_err / timeout: 4`。**判据**：timeout=4≤10✅ 但 Pass@1=73.4%<75%❌ → **不达标**。根因分析：log 大量 `MCP error -32001: MCP request to "pyAether_MCP_server" timed out after 60s`（code-gen 阶段 pyAether MCP 响应慢），致 23 个任务 code-gen 失败（fail=23）。sandbox 本身正常（131 ok/0 exec_err/host patch✅/0 Forbidden✅）。**按任务书"最多重跑3次不达标"→启动 retry#1**：四 override(EVAL_FW_DIR/CLI_DATA_DIR=.cline_prof4_eval/data/PYTHON/https_proxy) + `setsid bash scripts/run_cline_script.sh -p 8 -n` → **r2_new2 已启动 PID4063726 batch2026_1010_191625 log /tmp/ABL_full_r2_new2.log**。核验：四 override /proc/4063726/environ✅ / 0 Forbidden✅ / ACCESS RESTRICTED=14 canary live✅ / 0 host-error✅ / .env=8663/8666/8667/8670✅。真loop PID3579323 environ https_proxy✅(自检通过)。/home=3.5G/100%⚠️(非阻断)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new2(grep -E 'pass \(\|PASS_RATE\|评估结果汇总\|timeout' /tmp/ABL_full_r2_new2.log\|tail -10)→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new(log /tmp/ABL_full_r3_new.log)→r4_new→r5_new；仍不达标→retry#2(log /tmp/ABL_full_r2_new3.log)→retry#3→3次仍不达标→WAITING=1 等运维。
- [2026-10-10 19:52] ⠈ 巡检(r2_new2 retry#1 运行中·code-gen 阶段·不动作)：eval PID4063726 alive(elapsed 36:43,PPID=1 setsid✅), log 7.8MB/72750行/mtime 19:53(活跃增长), 0 Forbidden✅, ACCESS RESTRICTED=452(canary/反作弊 live✅), MCP 60s timeout=26(code-gen 正常重试), 0 pass(尚未 grading), host-error grep 命中=中文文本误匹配非真实错误✅。sandbox 正常执行代码✅。四 override /proc/4063726/environ✅。.env=8663/8666/8667/8670+e0031982_1~4@10.129.32.75✅。真loop PID3579323 environ https_proxy✅(自检通过无需重启)。/home=3.5G/100%⚠️(非阻断)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new2→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new→r4_new→r5_new；仍不达标→retry#2(/tmp/ABL_full_r2_new3.log)→retry#3→3次仍不达标→WAITING=1 等运维。
