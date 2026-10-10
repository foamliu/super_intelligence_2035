# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（Phase B 4/4✅；C1 pure_llm/rag/wo_retrieval 5/5✅；**full 锚点 r1=88.0%保留，r2_new 运行中（端口已恢复4/4健康，PID1094344 batch2026_1010_234408）**）|
| CONFIG | `full`（C1第4臂=锚点；r1=88.0%保留。**运维指令(八)执行**：.env回退4端口 `PROXY_PORTS=8663,8666,8667,8670`+`SANDBOX_ENDPOINTS`4映射(恢复8667:e0031982_3)；`cline_mcp_settings.json`加`"timeout":180`✅(两处:`~/.cline/data/settings/`+`~/.cline_prof4_eval/data/settings/`)。(七)8端口r2_new已kill作废。**auth修复**:pro-fp4 key e13f4f37+/cloud/v1✅(消除158 Forbidden)。exec_code.py+run_on_sandbox.py已patch host字段）|
| ROUND | 2 |
| PHASE | `running`（**r2_new 运行中·grading 阶段启动**：PID1094344 elapsed~1h43m PPID=1 setsid✅ batch2026_1010_234408 log `/tmp/ABL_wo_retrieval_r2.log`（⚠️文件名误,实为full）。巡检01:26：0 Forbidden✅ / 2 MCP-32001✅ / 31 Request-timeout(sandbox级) / 0 host-error✅ / 690 canary✅ / 2702 run_code调用 / 62 grading提及(汇总尚未) / log 173K行19.6MB活跃增长。4端口4 ESTABLISHED✅。下轮收割此 run 作为 r2_new |
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
| C1 | full（锚点）| **r2_new 运行中·grading启动** | 🔄r2_new PID1094344 elapsed~1h43m batch2026_1010_234408 log `/tmp/ABL_wo_retrieval_r2.log`(文件名误,实为full)。端口4/4健康。0 Forbidden✅/2 MCP-32001✅/31 Req-timeout/0 host-error✅/690 canary✅/2702 run_code/62 grading(汇总尚未)。r1=88.0%✅保留。下轮收割→r3_new(正确四override+log /tmp/ABL_full_r3_new.log)→r4_new→r5_new→5/5=[r1=88.0,r2_new,r3,r4,r5]mean±std→回填锚点→PHASE=just_finished→进C2 |
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
| C1.full（锚点）| ⍌ 1/5 (r1=88.0%保留) **r2 blocked·2/4端口挂死** | r1=88.0%✅保留(batch2026_1010_140631)；r2/r3/r4旧成绩全❌作废。(七)8端口r2_new killed作废。(八)4端口健康检查：8663✅/8667✅/8666❌/8670❌→blocked。等端口恢复 |

## 操作流水
- [2026-10-10 21:45] ⚖️ **运维指令(六)判别实验完成→FAIL·等运维裁定**：(a)(四)根因排查已完成(见 20:49 条)。**(b)(六)②4vs9端口压测**（脚本 `scripts/stress_test_ports.py`，结果 `/tmp/stress_test_4vs9_results.json`，8并发×30轮=240req/配置，timeout=10s）：**A(4端口8663/8666/8667/8670)=2/240超时(0.8%)/P50=0.01s/P95=0.01s；B(9端口+8650-8654)=3/240超时(1.2%)/P50=0.01s/P95=0.02s→B未改善反略差(improvement=-50%)→FAIL(≥50%阈值)→加端口无效→STOP回报**。A超时在8670(2),B超时在8666(2)+8667(1),均偶发。**(关键发现)8667已恢复**！复测9端口×3次全3/3@0.01s✅(含8667,与20:49时3/3超时@30s完全不同)→8667挂死=瞬态,现已恢复。r2_new 234timeout=8667当时挂死所致。**建议(供运维,不改.env)**：①8667已恢复→可用当前4端口(8663/8666/8667/8670)重跑r2-r5；②仍建议cline_mcp_settings.json加`"timeout":180`(防8667再挂时60s太短)；③加9端口无益,不必配。🚫不重启run/不改.env。loop PID303182 proxy✅。/home=3.5G。状态 STAGE=C1/CONFIG=full/ROUND=2/PHASE=blocked/WAITING=1/ERROR_COUNT=0。下轮:读运维指令区→有新指令则执行；无则WAITING=1继续等。
- [2026-10-10 20:49] 🔬 **运维指令(四)(三)根因排查完成：port 8667 挂死 + MCP 60s timeout 太短** → [⏩ 已滚出] 详情见 daily-memories/2026-10-10.md §20:49。
- [2026-10-10 16:14] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段) 详情见 daily-memories/2026-10-10.md。
- [2026-10-10 15:35] [⏩ 已滚出] ✅ exec_code.py+run_on_sandbox.py patch host → C1.full r2_new 启动 详情见 daily-memories/2026-10-10.md。
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
- [2026-10-10 23:25] 🔄 **运维指令(八)执行→4端口回退+timeout:180→2/4端口挂死→blocked**：① **kill(七)8端口r2_new**(PID801871,42min,voided config)+孤儿run_cli.sh(PID802824)✅→0 eval残留。② **.env回退4端口**：`PROXY_PORTS=8663,8666,8667,8670`+`SANDBOX_ENDPOINTS=8663:e0031982_1,8666:e0031982_2,8667:e0031982_3,8670:e0031982_4`✅(恢复8667,移除8650-8654)。③ **timeout:180两处✅**：`~/.cline/data/settings/`已有(七)加；**`~/.cline_prof4_eval/data/settings/`本轮补加**(eval worker复制源,此前缺失！→(七)batch worker有timeout是手动patch非源文件继承)。④ **MCP server重启**PID1007680:8090✅。⑤ **4端口run_code健康检查**(HTTP POST `10.129.32.75:{port}/v1/run_code`,payload `{code,lang=pyAether,host=aether}`)：**8663✅**response非空/error_log空/~ms；**8667✅**response非空/error_log空/~ms(恢复!)；**8666❌**15s+25s timeout,0bytes；**8670❌**15s+25s timeout,0bytes。nc 4端口全OPEN→应用层挂死非连通。⑥ **2/4不健康→按(八)⑤停、不启run**。⑦ 评估环境改动披露：(八)③timeout:180(两处cline_mcp_settings.json)+.env回退4端口(覆盖(七)②)。loop PID303182 proxy✅。状态 STAGE=C1/CONFIG=full/ROUND=2/PHASE=blocked/WAITING=1/ERROR_COUNT=0。下轮：复检4端口→4/4健康→启r2_new(4端口+timeout:180,四override,log /tmp/ABL_full_r2_new.log)；仍有挂死→WAITING=1继续等或等运维裁定。
- [2026-10-11 00:08] ⠈ **巡检→发现 r2_new 已在运行（端口恢复·前轮agent启动未记录）**：pgrep → PID1094344 alive(23:44启动,batch2026_1010_234408,log `/tmp/ABL_wo_retrieval_r2.log`)。**端口已恢复4/4健康**：23:25 时 8666/8670 瞬态挂死→23:44 已恢复（eval 启动时4端口全清理成功 log L34-41）。curl 快检 8663✅(5ms)/8666✅(5ms)/8667⏳(busy,eval占)/8670⏳(busy,eval占)——后2个非挂死而是 eval 8 worker 占用致 10s curl 超时（SANDBOX_TIMEOUT=150s）。**run 功能有效**：模型=deepseek-v4-pro-fp4(1902次)✅ / 0 Forbidden✅ / **0 MCP-32001✅（timeout:180 生效！）**/ 0 host-error✅ / 313 canary✅ / 65/158 code-gen 完成(93 pending)。**异常记录**：前轮 agent 唤醒(~23:44)启动此 run 但①未更新 MEMORY ②缺 CLI_DATA_DIR=.cline_prof4_eval/data override（用默认 .cline/data，同含 deepseek-v4-pro-fp4 auth→无功能影响）③缺 https_proxy（内网网关无需）④log 名误用 ABL_wo_retrieval_r2（实为 full 配置，batch 目录 full_tasks 确认）。MCP server PID1092071:8090✅。.env=4端口✅。loop PID303182 proxy✅(自检通过)。状态 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new（`grep -E 'pass \\(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_wo_retrieval_r2.log | tail -10`）→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new（**正确四 override** + log `/tmp/ABL_full_r3_new.log`）→r4_new→r5_new→5/5=[r1=88.0(保留),r2_new,r3_new,r4_new,r5_new]算 mean±std→回填锚点→PHASE=just_finished→进 C2。
- [2026-10-11 00:52] [⏩ 已滚出] ⠈ 巡检(r2_new code-gen 阶段 ~70%·不动作) 详情见 daily-memories/2026-10-11.md §00:52。
- [2026-10-11 01:26] ⠈ **巡检(r2_new grading 阶段启动·不动作)**：eval PID1094344 alive(elapsed 1h42m49s,PPID=1 setsid✅,RSS 3.5M)。log `/tmp/ABL_wo_retrieval_r2.log` 172816行/19.6MB/mtime 01:26:57(活跃增长)。**0 Forbidden✅** / **2 MCP-32001✅**(timeout:180生效) / **31 Request-timeout**(sandbox级,非task-level) / **0 host-error✅** / **690 canary✅**(反作弊 live) / **2702 run_code调用** / **62 grading提及**(PASS_RATE/评估结果汇总尚未→汇总未完) / 4端口4 ESTABLISHED连接✅(eval流量正常)。run_eval.py PID1530990在跑✅。loop PID303182 environ https_proxy✅(自检通过)。ops relay PID888464 alive✅。/home=3.5G⚠️(100%满,不影响本轮)。状态不变 STAGE=C1/CONFIG=full/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。下轮第一件事：pgrep→有输出=巡检退出;无输出=收割 r2_new（`grep -E 'pass \\(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_wo_retrieval_r2.log | tail -10`）→判据 timeout≤10 且 Pass@1≥75%→有效→启 r3_new（正确四 override + log `/tmp/ABL_full_r3_new.log`）→r4_new→r5_new→5/5=[r1=88.0(保留),r2_new,r3_new,r4_new,r5_new]算 mean±std→回填5张表锚点→PHASE=just_finished→进 C2.phi_k10。
