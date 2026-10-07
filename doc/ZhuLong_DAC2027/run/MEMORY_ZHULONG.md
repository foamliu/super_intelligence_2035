# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（组件消融；Phase B 已完成 4/4 ✅，C1.pure_llm 5/5 + C1.rag 5/5 ✅，**切 wo_retrieval**）|
| CONFIG | `wo_retrieval`（C1 第 3 臂，r1=74.1% 复用 legacy，**r2 运行中** PID 3132954 batch 2026_1007_221959；rag 5/5=71.8±2.5% 已收割）|
| ROUND | 2 |
| PHASE | `running`（**C1.wo_retrieval r2 已启动**（rag r5 收割 75.9% 120/158 b2026_1007_202448 0 Forbidden✅→5/5=71.8±2.5%→PHASE=just_finished→set_ablation.py wo_retrieval + stop.sh&&start.sh 重启 MCP→r2 PID 3132954 b2026_1007_221959。検索3件套 OFF / run_code ON✅；/proc environ 三 override✅ EVAL_FW_DIR/CLI_DATA_DIR=.cline_prof4_eval/data/PYTHON；pro-fp4 active✅ 132 mentions 0 leak / 0 Forbidden✅ / 170KB 活跃 / ACCESS RESTRICTED 32× canary PASS。infra 端口 OPEN✅ /nasdata 370G✅ /home 5.7G(非阻断)。运维复检 legacy 2455466✅ ops 2665949✅ zhulong_loop 3579323✅。**下轮**：pgrep 无输出→grep PASS_RATE /tmp/ABL_wo_retrieval_r2.log 取 r2→记成绩→ROUND≤5 启 r3，⚠️ r3/r4/r5 启动必带 EVAL_FW_DIR override + CLI_DATA_DIR pro-fp4 隔离 + https_proxy）|
| WAITING | 1 |
| ERROR_COUNT | 0（C1.rag r3 作废=infra 额度耗尽，不计数；已重跑恢复）|
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-pro-fp4`（**已恢复 HTTP 200，C1/C2/S1 均用 pro-fp4**）|

## 执行看板（15 臂 × 5 轮——已调换为 BâC1âC2âS1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| B | glm-5.2 | 5/5 ✅ | **83.3±3.1%** [84.2,87.3,84.2,79.1,81.6]（r5=81.6% 129/158 batch 2026_1005_233928, 0 Forbidden ✅）|
| B | deepseek-v4-flash | 5/5 ✅ | **16.7 ± 12.3%** [9.5,10.1,19.0,7.6,37.3]（r1=9.5%(15/158,b2026_1006_022818); r2=10.1%(16/158,b2026_1006_031227); r3=19.0%(30/158,b2026_1006_034557); r4=7.6%(12/158,15ok/143fail/0exec_err,b2026_1006_042140); r5=37.3%(59/158,67ok/90fail/0exec_err,b2026_1006_045811), 0 Forbidden ✅ 全程）|
| B | kimi-k2.6-cloud | 5/5 ✅ | **77.0±1.6%** [79.1,76.6,77.2,74.7,77.2]（r5=77.2% 122/158 batch 2026_1006_230904, 137ok/21fail/0exec_err, 0 Forbidden ✅, kimi active ✅）|
| B | doubao-seed-2.0-pro-cloud | 5/5 ✅ | **63.8±1.4%** [63.9,64.6,61.4,65.2,63.9]（r5=63.9% 101/158 b2026_1007_095002, 0 Forbidden ✅, doubao active ✅）|
| C1 | pure_llm | 5/5 â | â 10.5Â±1.9%ï¼å¤ç¨ legacyï¼[8.2,9.5,10.1,11.4,13.3]ï¼|
| C1 | rag | 5/5 ✅ | **71.8±2.5%** [70.3,72.2,69.6,70.9,75.9]（r5=75.9% 120/158 batch 2026_1007_202448, 151 ok/7 fail/0 exec_err, 0 Forbidden ✅；legacy 68.2±7.4% 作废→本线重跑）|
| C1 | wo_retrieval | 1/5→r2 ▶（r2 运行中）| r1=74.1% 复用 legacy；**r2 运行中**(PID 3132954, b2026_1007_221959)；旧 r2 infra 作废(pro-fp4 403)已剔除 |
| C1 | fullï¼éç¹ï¼| 1-5/5 | â¬ï¼æ¢è·¯ 84.8%ï¼|
| C2 | phi_k10 | 1-5/5 | â¬ï¼æ¢è·¯ 75.3%ï¼|
| C2 | phi_k3 | 1-5/5 | â¬ï¼æ¢è·¯ 69.0%ï¼|
| C2 | phi_k1 | 1-5/5 | â¬ï¼æ¢è·¯ 60.8%ï¼|
| C2 | phi_lagged | 1-5/5 | â¬ï¼æ¢è·¯ 84.2%ï¼r2 ä¿®å¤å 98.1%ï¼|
| S1 | omega_low | 1-5/5 | â¬ï¼æ§ 5-run å·²åº r1=81.6 / r2=82.3ï¼å¾å®æ¯å¦å»¶ç»­ï¼|
| S1 | readback_binary | 1-5/5 | â¬ |
| S1 | readback_none | 1-5/5 | â¬ |

## 成绩记录（N=5 mean±std，Pass@1 %）

| 臂 | N=5 mean±std | 各轮原始值 |
|:--|:-:|:--|
| B.glm-5.2 | **83.3 ± 3.1%** | [84.2, 87.3, 84.2, 79.1, 81.6] |
| B.deepseek-v4-flash | **16.7 ± 12.3%** | r1=9.5%（15/158, batch 2026_1006_022818）；r2=10.1%（16/158, batch 2026_1006_031227）；r3=19.0%（30/158, batch 2026_1006_034557）；r4=7.6%（12/158, 15 ok/143 fail/0 exec_err, 0 Forbidden ✅, batch 2026_1006_042140）；r5=37.3%（59/158, 67 ok/90 fail/0 exec_err, 0 Forbidden ✅, batch 2026_1006_045811）|
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2]（r1=79.1% 125/158 b2026_1006_071809；r2=76.6% 121/158 b2026_1006_100626；r3=77.2% 122/158 b2026_1006_181646；r4=74.7% 118/158 b2026_1006_204422；r5=77.2% 122/158 b2026_1006_230904, 137 ok/21 fail/0 exec_err, 0 Forbidden ✅ 全程）|
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9]（r1=63.9% 101/158 b2026_1007_010601；r2=64.6% 102/158 b2026_1007_030335；r3=61.4% 97/158 b2026_1007_050414；r4=65.2% 103/158 b2026_1007_083426；r5=63.9% 101/158 b2026_1007_095002, 0 Forbidden ✅ 全程）|
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | r1=74.1（r2 运行中）| [74.1]（r1 复用 legacy；r2 运行中 PID 3132954 b2026_1007_221959；旧 r2 作废 0/158 pro-fp4 403 不计数）|
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9]（r1=70.3% 111/158 b2026_1007_112101；r2=72.2% 114/158 b2026_1007_131535；r3=69.6% 110/158 b2026_1007_163343；r4=70.9% 112/158 b2026_1007_183007；r5=75.9% 120/158 b2026_1007_202448, 151 ok/7 fail/0 exec_err, 0 Forbidden ✅ 全程；旧 r3 作废 b2026_1007_151301 0/158 不计数；legacy 68.2±7.4% 作废）|

## 操作流水
- [2026-10-07 18:29] [✅ C1.rag r3 收割 69.6%→r4 启动] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（§18:29，rolled-from-MEMORY 2026-10-07 20:24）。
- [2026-10-07 16:34] [✅ C1.rag r3 重跑启动（pro-fp4 额度恢复 HTTP 200@16:32:44）] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 18:29）。
- [2026-10-07 15:47] [⚠️ infra C1.rag r3 作废（pro-fp4 额度耗尽 0/158）→待 ~16:32 quota 恢复后重跑，不动作退出] [⏩ 已滚出] 详情已原文搬入 daily-memories/2026-10-07.md（rolled-from-MEMORY 2026-10-07 18:29）。
- [2026-10-07 15:11] [✅ C1.rag r2 收割 72.2%→r3 启动] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**无输出**（r2 PID 1937775 gone, log mtime 14:57:57）→ 进入打分。**打分**：`grep -E 'pass \(\|PASS_RATE\|评估结果汇总' /tmp/ABL_rag_r2.log`→PASS_RATE=0.7215 / **114/158 pass (72.2%)** / generated 142 ok/16 fail/0 exec_err, **0 Forbidden✅**, batch 2026_1007_131535。**r2=72.2%** ✅。**核验**：`grep -c Forbidden`=0✅；ACCESS RESTRICTED 1427×（反作弊 hook live✅ canary PASS）；pro-fp4 mentions 4732 / other-model leak 0✅；输出目录 `/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/20261007_1457_app.e0031982`（EVAL_FW_DIR override 生效✅，非 .env:243 := 默认崩路径）。ROUND 2→3≤5→启 r3。**r3 启动**（复用 r1/r2 姿势：EVAL_FW_DIR override 防 .env:243 := 默认崩 + CLI_DATA_DIR=.cline_prof4_eval/data pro-fp4 隔离）：`cd $BASE_DIR && export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework && export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data && export PYTHON=$BASE_DIR/venv/bin/python && setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_rag_r3.log 2>&1 < /dev/null &`→**PID 2208135**, batch **2026_1007_151301**, 8 worker/158 题/-n, log=/tmp/ABL_rag_r3.log。**canary+验证**：① /proc/2208135/environ 确认 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework✅ CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data✅ PYTHON✅；② log 已写入 9.6KB 活跃增长（Step 0-2 推进✅，Memory Bank 注入禁用 -n✅）。.env 仍 rag 态（EDA_MCP_TOOLS_DISABLED=clean_workdir,probe_pyAether_code,cimi_search,cimi_fetch,vqa,query_memory_bank,run_code → 检索3件套 ON / run_code OFF）✅，同臂不切 set_ablation。**infra**：8090/8653/8664/8665/8669 全 OPEN✅；/nasdata 373G free✅；/home 99%/5.8G（非硬阻断，我方产物落 /nasdata）。**运维复检**：legacy 组件 loop PID 2455466 alive✅（指令五满足）；ops relay PID 2665949 alive✅（`.last_run_id`=21=inbox RUN_ID 21，无新指令，指令八满足）；zhulong_loop PID 3579323 alive✅；conductor 未触碰（红线）。**已收割**：Phase B 4/4✅；C1.pure_llm 5/5 复用 legacy=10.5±1.9%✅；C1.rag r1=70.3%/r2=72.2%✅，r3 运行中。**状态**：STAGE=C1 / CONFIG=rag / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r3（pgrep 无输出→grep PASS_RATE /tmp/ABL_rag_r3.log 取 r3 Pass@1→记成绩→ROUND≤5 启 r4，⚠️ r4 启动必带 EVAL_FW_DIR override + CLI_DATA_DIR pro-fp4 隔离 + https_proxy push）。
- [2026-10-07 13:51] [🩾 C1.rag r2 健康巡检→仍在跑（code-gen 阶段 ~37min），不动作退出] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**有输出**（PID 1937775 alive, etime≈36:43, stat=Ss, batch 2026_1007_131535）→ r2 仍在运行 → **判据：什么都不做退出**，WAITING 保持 1。**健康核验**：log=/tmp/ABL_rag_r2.log 10.6MB 活跃增长（mtime 13:51）；`grep -c Forbidden`=0 ✅；ACCESS RESTRICTED 886×（反作弊 hook live ✅ canary PASS）；pro-fp4 active ✅（2382 mentions，0 other-model leak）；尚无 PASS_RATE 汇总行→r2 仍在代码生成阶段。**infra**：8090/8653/8664/8665/8669 全 OPEN ✅；/nasdata 374G free ✅；/home 99%/5.8G（非硬阻断，我方产物落 /nasdata）。**运维复检**：legacy 组件 loop PID 2455466 alive ✅（指令五满足）；ops relay PID 2665949 alive ✅（`.last_run_id`=21=inbox RUN_ID 21，无新指令，指令八满足）；zhulong_loop PID 3579323 alive ✅；conductor 未触碰（红线）。**git**：commit c379c2e2（`zhulong C1.rag r2 health-check + MEMORY 滚动`）→ push **成功**（⚠️ 首次无代理超时 exit=124；设 `https_proxy=http://172.19.92.23:13128` 后 `ed72426a..c379c2e2 main->main` exit=0 ✅）。`git status -sb`=`## main...origin/main` 无 ahead/behind ✅。**状态不变**：STAGE=C1 / CONFIG=rag / ROUND=2 / PHASE=running / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r2（pgrep 无输出→grep PASS_RATE /tmp/ABL_rag_r2.log 取 r2 Pass@1→记成绩→ROUND≤5 启 r3，⚠️ r3 启动必带 EVAL_FW_DIR override + CLI_DATA_DIR pro-fp4 隔离 + https_proxy）。**记忆维护**：滚出 10:30/12:00/12:35 三条已闭合健康巡检至 daily-memories/2026-10-07.md（原文自 git HEAD 恢复）→ MEMORY 30.7KB ✅。

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
- [2026-10-07 06:39] [🔧⚠️ 重打分 v1 卡住→kill→v2 重启（source .env 修正 SANDBOX_ENDPOINTS）] v1（PID 1033263）assemble 完成后 sandbox 阶段卡住：log 冻结 10min 无进展，`ss` 见 `SYN-SENT 10.129.32.75:8665`（连接不建立）。**根因**：v1 启动只 `export EVAL_FW_DIR=...` 但**未 source .env**→`SANDBOX_ENDPOINTS` 缺失→run_eval.py 回退单端口（config.yaml `sandbox.url=10.129.32.75:8660`，但实际连了 8665 不可达）→卡。**.env 真实端点**=SANDBOX_ENDPOINTS=`8650/8651/8652/8654`（10.129.32.75，均 REACHABLE ✅），非 infra 检查用的 8664/8665/8653/8669。**修正**：kill 1033263 + 清孤儿 run_on_sandbox.py（PID 1033276/1033281，ppid=1）→ v2 重启 `set -a;source .env;set +a;export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework;.../venv/bin/python scripts/run_eval.py -g completed_code_generation_2026_1007_050414.jsonl` → **PID 1059448**。**验证 v2**：assemble 158 完成 ✅；`ss` 见 `ESTAB 10.129.32.75:8650/8654`（多端口并行✅，worker 1059474/1059475）；孤儿已清（仅 1059xxx 进程存活）。**git**：push 直连 github 失败（port 443 timeout 134s）→ 加 `https_proxy=http://172.19.92.23:13128` 重试 → `7cfd9d26..582617a6 main->main` exit=0 ✅（git status 无 ahead/behind）。**状态**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=1。退出等下轮唤醒 harvest v2 重打分。





- [2026-10-07 07:17] [🩾 B.doubao-seed-2.0-pro-cloud r3 重打分 v2 仍在跑（shard_3 执行中）→ 不动作退出] §7 步骤 A（PHASE=running）：`pgrep -f 'run_eval.py -g completed_code_generation_2026_1007_050414'`→**有输出**（PID 1059448 alive，etime≈2290s≈38min）→ 重打分 v2 仍在运行 → **判据：什么都不做退出**，WAITING 保持 1。**进度核验**：4 shard 中 shard_0/1/2 已完成（output_evaluation/tmp/execution_results_shard_{0,1,2}.jsonl mtime 06:39-06:57），shard_3 仍在执行（execution_results_shard_3.jsonl mtime **07:17:27** 活跃写入，9107 bytes vs 已完成 shard ~14KB ≈ 60% 进度）；`run_on_sandbox.py` PID 1059464→1059475 `--workers 1` 串行执行 shard_3 的 40 脚本；`ss` 见 `ESTAB 10.129.32.75:8654`（sandbox 连接活跃✅）；8654 reachable ✅。log=/tmp/RESCORE_doubao_r3.log 11 行（assemble 完成后无新日志行=正常，sandbox 阶段输出到 shard jsonl）。**infra**：8650/8651/8652/8654 全 OPEN ✅（实际 sandbox 端点）；8653/8669 OPEN ✅；8664/8665 CLOSED（非实际 sandbox 端点，infra 检查用端口，不影响 eval）；/nasdata 371G free ✅；/home 5.8G/99%（非硬阻断，我方产物落 /nasdata）。运维复检：legacy 组件 loop PID 2455466 alive ✅；ops relay PID 2665949 alive ✅（`.last_run_id`=21=inbox RUN_ID 21，无新指令）；zhulong_loop PID 3579323 alive ✅；conductor 未触碰（红线）。**状态不变**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=1。退出等下轮唤醒 harvest 重打分 v2（pgrep run_eval 无输出→grep PASS_RATE /tmp/RESCORE_doubao_r3.log 取 r3 Pass@1 → 记成绩、ERROR_COUNT 归 0 → ROUND≤5 启 r4，**⚠️ r4/r5 启动必带 EVAL_FW_DIR override + source .env**）。


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

- [2026-10-07 22:18] [✅ C1.rag r5 收割 75.9%→5/5=71.8±2.5%→切 C1.wo_retrieval r2 启动] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**无输出**（r5 PID 2885147 已结束，log mtime 22:00）→ 进入打分。**打分**：`grep -E 'pass \(|PASS_RATE|评估结果汇总' /tmp/ABL_rag_r5.log`→PASS_RATE=0.7595 / **120/158 pass (75.9%)** / generated 151 ok/7 fail/0 exec_err, **0 Forbidden✅**, batch 2026_1007_202448。**r5=75.9%** ✅。**算 mean±std**：[70.3,72.2,69.6,70.9,75.9]→mean=71.78 std(n-1)=2.493→**C1.rag=71.8±2.5%**。ROUND 6>5→PHASE=just_finished、WAITING=0。**步骤 B 切 C1.wo_retrieval**（C1 第 3 臂；r1=74.1% 复用 legacy，从 r2 续跑）：① `venv/bin/python scripts/set_ablation.py wo_retrieval`→EXIT=0（検索3件套 OFF / run_code ON）；② `bash scripts/stop.sh && bash scripts/start.sh`→STOP/START EXIT=0，MCP 重启监听 8090；③ .env EDA_MCP_TOOLS_DISABLED=...,get_api_details,search_apis,search_apis_by_keyword（run_code 不在 disabled→ON✅）。**Gate**：8090/8653/8664/8665/8669/9006 全 OPEN✅ /nasdata 370G✅ /home 5.7G(非阻断) EDA-Eval-Framework✅ CLI_DATA_DIR=.cline_prof4_eval/data✅。**r2 启动**（EVAL_FW_DIR override 防 .env:243 := 默认崩 + CLI_DATA_DIR pro-fp4 隔离）：`cd $BASE_DIR && export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework && export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data && export PYTHON=$BASE_DIR/venv/bin/python && setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_wo_retrieval_r2.log 2>&1 < /dev/null &`→**PID 3132954**（ppid=1 detached✅）batch **2026_1007_221959** 8worker/158/-n。**验证**：pgrep alive✅；log 170KB 活跃；0 Forbidden✅；ACCESS RESTRICTED 32×（canary PASS✅）；pro-fp4 active✅ 132 mentions 0 leak✅；log tail 见 run_code 调用（wo_retrieval: 検索 OFF / run_code ON✅）。**运维复检**：legacy 2455466✅（指令五）；ops 2665949✅（`.last_run_id`=21，指令八）；zhulong_loop 3579323✅；conductor 未触碰。**已收割**：Phase B 4/4✅；C1.pure_llm 5/5=10.5±1.9%✅；**C1.rag 5/5=71.8±2.5%✅**；C1.wo_retrieval r2 运行中（r1=74.1% 复用 legacy）。**状态**：STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / PHASE=running / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r2（pgrep 无输出→grep PASS_RATE /tmp/ABL_wo_retrieval_r2.log 取 r2→记成绩→ROUND≤5 启 r3，⚠️ r3/r4/r5 启动必带 EVAL_FW_DIR override + CLI_DATA_DIR pro-fp4 隔离 + https_proxy）。

- [2026-10-07 22:58] [🩾 C1.wo_retrieval r2 健康巡检（仍在跑）] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**有输出** PID 3132954 alive✅（batch 2026_1007_221959，启动于 22:18，已跑 ~40min）→ log 9.27MB 活跃（mtime 22:58）→ **eval 仍在跑，不动作退出**。**健康**：0 Forbidden✅；ACCESS RESTRICTED 498×（canary PASS✅ 反作弊 hook 全程生效）；2 个 "infra" 命中均为 agent 推理文本（"infrastructure"/"test infrastructure"）非真错误✅；无 pass/汇总→未结束。**infra**：8653/8664/8665/8669/8090 全 OPEN✅ /nasdata 369G free✅。**运维复检**：legacy 2455466✅（指令五）；ops 2665949✅（`.last_run_id`=21）；zhulong_loop 3579323✅。git clean/in-sync✅。**状态不变**：STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / PHASE=running / WAITING=1 / ERROR_COUNT=0。已 commit+push（本轮心跳）。退出，下轮复检 r2 是否结束。

- [2026-10-07 23:32] [🩾 C1.wo_retrieval r2 健康巡检 #2（仍在跑）] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**有输出** PID 3132954 alive✅（batch 2026_1007_221959，启动于 22:18，已跑 ~74min）→ log **16.8MB** 活跃（mtime 23:33，22:58 时 9.27MB→+7.5MB 持续增长）→ **eval 仍在跑，不动作退出**。**健康**：0 Forbidden✅；ACCESS RESTRICTED **708×**（498→708，canary PASS✅ 反作弊 hook 全程生效）；pro-fp4 active✅ 6308 mentions；run_code 3557 calls / generated 599（wo_retrieval: 検索 OFF / run_code ON，agent 靠 run_code 自行探索 API✅）；无 pass/汇总→未结束。**infra**：8653/8664/8665/8669/8090/9006 全 OPEN✅ /nasdata 369G free✅ /home 5.7G(99% 非阻断，我方产物 symlink→/nasdata✅)。**运维复检**：legacy 2455466✅（指令五）；ops 2665949✅（`.last_run_id`=21，指令八）；zhulong_loop 3579323✅；conductor 未触碰。git clean/in-sync✅。**状态不变**：STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / PHASE=running / WAITING=1 / ERROR_COUNT=0。已 commit+push（本轮心跳）。退出，下轮复检 r2 是否结束（pgrep 无输出→grep PASS_RATE /tmp/ABL_wo_retrieval_r2.log 取 r2→记成绩→ROUND≤5 启 r3）。

- [2026-10-08 00:08] [🩾 C1.wo_retrieval r2 健康巡检 #3（仍在跑）] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**有输出** PID 3132954 alive✅（batch 2026_1007_221959，启动于 22:18，已跑 ~110min）→ log **22.3MB** 活跃（mtime 00:08，23:32 时 16.8MB→+5.5MB 持续增长）→ **eval 仍在跑，不动作退出**。**健康**：0 Forbidden✅；ACCESS RESTRICTED **814×**（708→814，canary PASS✅ 反作弊 hook 全程生效）；pro-fp4 active✅ 8460 mentions；run_code 4475 calls（wo_retrieval: 検索 OFF / run_code ON，agent 靠 run_code 自行探索 API✅）；无 pass/汇总→未结束。**infra**：8653/8664/8665/8669/8090/9006 全 OPEN✅ /nasdata 369G free✅ /home 5.7G(99% 非阻断，我方产物 symlink→/nasdata✅)。**运维复检**：legacy 2455466✅（指令五）；ops 2665949✅（`.last_run_id`=21，指令八）；zhulong_loop 3579323✅；conductor 未触碰。**状态不变**：STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / PHASE=running / WAITING=1 / ERROR_COUNT=0。已 commit+push（本轮心跳）。退出，下轮复检 r2 是否结束。
