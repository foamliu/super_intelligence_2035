# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `B`（大模型消融；**已调换**：因 pro-fp4 额度 403 阻塞 C1，先跑 Phase B）|
| CONFIG | `doubao-seed-2.0-pro-cloud`（B 第 4 臂，r3 运行中）|
| ROUND | 3 |
| PHASE | `running`（B.doubao-seed-2.0-pro-cloud r3 **生成完成(158ok/0fail,b2026_1007_050414)但 Step7.1 eval 崩溃→重打分 v2 中**：① v1=PID1033263 仅 export EVAL_FW_DIR 未 source .env→SANDBOX_ENDPOINTS 缺失→卡单端口(10.129.32.75:8665 SYN-SENT)→已 kill+清孤儿(1033276/1033281)；② v2=PID1059448 `set -a;source .env;set +a`+EVAL_FW_DIR override→多端口 8650/8651/8652/8654 并行(ESTAB✅)，log=/tmp/RESCORE_doubao_r3.log，assemble 158 完成→sandbox 4 分片执行中(预计~30min)；根因=r3 启动漏 export EVAL_FW_DIR→.env:243 默认 app.t0002997 路径不存在→restore_config 崩；r1=63.9%、r2=64.6% 已收割；前序 glm-5.2=83.3±3.1%/flash=16.7±12.3%/kimi=77.0±1.6% ✅；下轮唤醒：pgrep run_eval 无输出→grep PASS_RATE /tmp/RESCORE_doubao_r3.log 取 r3→记成绩→ROUND≤5 启 r4，**⚠️r4/r5 启动必带 EVAL_FW_DIR override + source .env（SANDBOX_ENDPOINTS）**）|
| WAITING | 1 |
| ERROR_COUNT | 1（r3 Step7.1 eval 崩溃→重打分中）|
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | `glm-5.2`（编排模型；deepseek-v4-pro-fp4 额度已耗尽故更换）|

## 执行看板（15 臂 × 5 轮——已调换为 BâC1âC2âS1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| B | glm-5.2 | 5/5 ✅ | **83.3±3.1%** [84.2,87.3,84.2,79.1,81.6]（r5=81.6% 129/158 batch 2026_1005_233928, 0 Forbidden ✅）|
| B | deepseek-v4-flash | 5/5 ✅ | **16.7 ± 12.3%** [9.5,10.1,19.0,7.6,37.3]（r1=9.5%(15/158,b2026_1006_022818); r2=10.1%(16/158,b2026_1006_031227); r3=19.0%(30/158,b2026_1006_034557); r4=7.6%(12/158,15ok/143fail/0exec_err,b2026_1006_042140); r5=37.3%(59/158,67ok/90fail/0exec_err,b2026_1006_045811), 0 Forbidden ✅ 全程）|
| B | kimi-k2.6-cloud | 5/5 ✅ | **77.0±1.6%** [79.1,76.6,77.2,74.7,77.2]（r5=77.2% 122/158 batch 2026_1006_230904, 137ok/21fail/0exec_err, 0 Forbidden ✅, kimi active ✅）|
| B | doubao-seed-2.0-pro-cloud | 3/5 ▶（r3 生成完成→重打分中）| r1=63.9%（101/158, b2026_1007_010601, 0 Forbidden ✅, doubao active ✅）; r2=64.6%（102/158, b2026_1007_030335, 158 ok/0 fail/0 exec_err, 0 Forbidden ✅, doubao active ✅）; r3 生成完成(158ok/0fail, b2026_1007_050414, 0 Forbidden ✅)但 Step7.1 eval 崩(漏 EVAL_FW_DIR)→重打分 v2 PID 1059448（source .env→多端口8650-8654并行）log=/tmp/RESCORE_doubao_r3.log |
| C1 | pure_llm | 5/5 â | â 10.5Â±1.9%ï¼å¤ç¨ legacyï¼[8.2,9.5,10.1,11.4,13.3]ï¼|
| C1 | rag | 0/5 | â¬ï¼legacy 68.2Â±7.4% ä½åºâé¡»æ¬çº¿éè·ï¼|
| C1 | wo_retrieval | 1/5 â r2 â¸ï¼pro-fp4 403 é»å¡âå¾ Phase B å®æåéè¯ï¼| r1=74.1% å¤ç¨ legacyï¼r2 infra ä½åºï¼pro-fp4 403ï¼|
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
| B.doubao-seed-2.0-pro-cloud | [TBD]（3/5，r3 重打分中）| r1=63.9%（101/158, PASS_RATE=0.6392, b2026_1007_010601, 0 Forbidden ✅, doubao active ✅）; r2=64.6%（102/158, PASS_RATE=0.6456, b2026_1007_030335, 158 ok/0 fail/0 exec_err, 0 Forbidden ✅, doubao active ✅）; r3 生成完成(158ok/0fail, b2026_1007_050414)但 eval 崩(漏 EVAL_FW_DIR→.env:243 默认 app.t0002997 路径不存在)→重打分 v2 PID 1059448（source .env→SANDBOX_ENDPOINTS 8650/8651/8652/8654 并行）log=/tmp/RESCORE_doubao_r3.log |
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | r1=74.1（r2 infra 作废；pro-fp4 403→待 Phase B 完成后重试）| [74.1]（r1 复用 legacy；r2 0/158 Forbidden 作废）|

## 操作流水

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
- [2026-10-07 05:01] [✅ B.doubao-seed-2.0-pro-cloud r2 收割 64.6% → r3 启动] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**无输出**（r2 PID 586670 已不在，log mtime 04:48:37 已结束）→ 进入打分。打分：`grep 'pass (|PASS_RATE|评估结果汇总' /tmp/ABL_doubao-seed-2.0-pro-cloud_r2.log`→**102/158 pass (64.6%)**，PASS_RATE=0.6456，generated 158 ok/0 fail/0 exec_err，batch 2026_1007_030335。**模型核验**：AI SDK 警告含 `openai-compatible.chat / doubao-seed-2.0-pro-cloud`（非 glm）✅；`grep -c Forbidden`=**0** ✅。infra：8664/8665/8653/8669 全 OPEN ✅、/nasdata 372G free ✅、/home 99%/6G（非硬阻断，我方产物落 /nasdata）。**r2=64.6%**（r1=63.9%、r2=64.6% 两轮稳定）。ROUND=3≤5 → 启动 r3。**启动 r3**：`CLI_DATA_DIR=/nasdata/app.e0031982/.cline_doubao_eval/data setsid bash scripts/run_cline_script.sh -p 8 -n`（full 配置不切 set_ablation，doubao CLI_DATA_DIR 隔离复用 r1/r2）→ **PID 854474**, batch **2026_1007_050414**, 8 worker/158 题/-n, log=/tmp/ABL_doubao-seed-2.0-pro-cloud_r3.log。验证：pgrep PID 854474 alive ✅；模型=doubao-seed-2.0-pro-cloud ✅；0 Forbidden ✅；log 218KB 活跃增长，43 cline worker 活跃。运维复检：legacy 组件 loop PID 2455466 ✅；zhulong_loop PID 3579323 ✅；ops relay PID 2665949 ✅（.last_run_id=21=inbox RUN_ID 21，无新指令）；conductor 未触碰（红线）。**状态**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r3。
- [2026-10-07 05:44] [🩺 B.doubao-seed-2.0-pro-cloud r3 健康巡检 → 不动作退出] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**有输出**（PID 854474 alive，etime≈2434s≈40.6min，batch 2026_1007_050414）→ r3 仍在运行 → **判据：什么都不做退出**，WAITING 保持 1。**健康核验**：r3 log=/tmp/ABL_doubao-seed-2.0-pro-cloud_r3.log 6.37MB mtime 05:44 活跃增长 ✅；tail 见 live agent 活动（thinking + sandbox `ACCESS RESTRICTED` = 反作弊 hook live，agent 正推进 pyAether 代码）✅；`grep -c Forbidden`=**0** ✅；`grep -cE 'pass \(|PASS_RATE|评估结果汇总'`=0（尚未到评分段，仍在跑任务）✅。infra：端口 8664/8665/8653/8669 全 OPEN ✅、/nasdata 372G free ✅、/home 99%/5.8G（非硬阻断，我方产物落 /nasdata）。运维指令复检：(五) legacy 组件 loop PID 2455466 alive ✅（etime≈3.6d）；(八) ops relay PID 2665949 alive ✅（`ops/.last_run_id`=21=inbox `RUN_ID: 21`，已追平无新指令）；zhulong_loop PID 3579323 alive ✅；conductor 未触碰（红线）。**状态不变**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r3（pgrep 无输出→grep PASS_RATE 取 r3 → 记成绩 → ROUND≤5 启 r4）。
- [2026-10-07 06:21] [🔧 B.doubao-seed-2.0-pro-cloud r3 生成完成→Step7.1 eval 崩溃→重打分启动] §7 步骤 A（PHASE=running）：`pgrep '^bash scripts/run_cline_script'`→**无输出**（r3 PID 854474 已结束，log mtime 05:53）→ 进入打分。**打分**：`grep -cE 'pass \\(|PASS_RATE|评估结果汇总' /tmp/ABL_doubao-seed-2.0-pro-cloud_r3.log`=**0**（无汇总行）→ **判据：打分失败 ❌ EVAL_FAILED**。**诊断**：r3 log 末尾 `[Step 7.1] 评估失败 (跳过, 不影响生成产物)`；traceback=`FileNotFoundError: PosixPath('/home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether')` 于 `restore_config()`（run_eval.py:198，`git checkout config.yaml` cwd=EVAL_FW 不存在）。**根因**：r3 启动命令（见 05:01 流水）只 export 了 `CLI_DATA_DIR`，**漏 export EVAL_FW_DIR**→run_cline_script.sh source .env:243 `EVAL_FW_DIR=${EVAL_FW_DIR:=/home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether}` 取默认值（他用户路径，不存在）→ eval 崩。**r1/r2 对比**：r1 log 52260 行 EVAL_FW=/nasdata/app.e0031982/code/EDA-Eval-Framework（r1/r2 启动带 EVAL_FW_DIR override→eval 正常）。**生成产物完整性**：158 对话→158 重命名 benchmark ID→completed_code_generation_2026_1007_050414.jsonl=158 行 ✅（生成阶段不依赖 EVAL_FW_DIR，仅 eval 依赖）；0 Forbidden ✅；doubao active ✅。→ **生成有效、仅打分崩** = §7「重打分」retry 场景（非 infra 作废、非生成失败）。**重打分启动**：确认 legacy 非 mid-eval（无 run_eval/sandbox/assemble 进程；legacy loop log 空）+ 4 端口 OPEN + EDA-Eval-Framework config.yaml git-clean → `cd $BASE_DIR && EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework EVAL_ROOT_DIR=/home/app.e0031982/eda_code_eval EVAL_SANDBOX_WORKERS=4 setsid .../venv/bin/python scripts/run_eval.py -g completed_code_generation_2026_1007_050414.jsonl > /tmp/RESCORE_doubao_r3.log 2>&1` → **PID 1033263**。**验证**：restore_config 未崩 ✅；[阶段2] assemble 158 脚本完成 ✅；进程 alive ✅。**ERROR_COUNT=0→1**（<3，retry 中）。infra：8664/8665/8653/8669 全 OPEN ✅、/nasdata 372G ✅、/home 99%/6G（非硬阻断）。运维复检：legacy 组件 loop PID 2455466 ✅；ops relay PID 2665949 ✅（.last_run_id=21，无新指令）；zhulong_loop PID 3579323 ✅；conductor 未触碰（红线）。**状态**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=1。退出等下轮唤醒 harvest 重打分（pgrep run_eval 无输出→grep PASS_RATE /tmp/RESCORE_doubao_r3.log 取 r3→记成绩→ROUND≤5 启 r4，**⚠️ r4/r5 启动必带 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework override**）。
- [2026-10-07 06:39] [🔧⚠️ 重打分 v1 卡住→kill→v2 重启（source .env 修正 SANDBOX_ENDPOINTS）] v1（PID 1033263）assemble 完成后 sandbox 阶段卡住：log 冻结 10min 无进展，`ss` 见 `SYN-SENT 10.129.32.75:8665`（连接不建立）。**根因**：v1 启动只 `export EVAL_FW_DIR=...` 但**未 source .env**→`SANDBOX_ENDPOINTS` 缺失→run_eval.py 回退单端口（config.yaml `sandbox.url=10.129.32.75:8660`，但实际连了 8665 不可达）→卡。**.env 真实端点**=SANDBOX_ENDPOINTS=`8650/8651/8652/8654`（10.129.32.75，均 REACHABLE ✅），非 infra 检查用的 8664/8665/8653/8669。**修正**：kill 1033263 + 清孤儿 run_on_sandbox.py（PID 1033276/1033281，ppid=1）→ v2 重启 `set -a;source .env;set +a;export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework;.../venv/bin/python scripts/run_eval.py -g completed_code_generation_2026_1007_050414.jsonl` → **PID 1059448**。**验证 v2**：assemble 158 完成 ✅；`ss` 见 `ESTAB 10.129.32.75:8650/8654`（多端口并行✅，worker 1059474/1059475）；孤儿已清（仅 1059xxx 进程存活）。**git**：push 直连 github 失败（port 443 timeout 134s）→ 加 `https_proxy=http://172.19.92.23:13128` 重试 → `7cfd9d26..582617a6 main->main` exit=0 ✅（git status 无 ahead/behind）。**状态**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=1。退出等下轮唤醒 harvest v2 重打分。





- [2026-10-07 07:17] [🩾 B.doubao-seed-2.0-pro-cloud r3 重打分 v2 仍在跑（shard_3 执行中）→ 不动作退出] §7 步骤 A（PHASE=running）：`pgrep -f 'run_eval.py -g completed_code_generation_2026_1007_050414'`→**有输出**（PID 1059448 alive，etime≈2290s≈38min）→ 重打分 v2 仍在运行 → **判据：什么都不做退出**，WAITING 保持 1。**进度核验**：4 shard 中 shard_0/1/2 已完成（output_evaluation/tmp/execution_results_shard_{0,1,2}.jsonl mtime 06:39-06:57），shard_3 仍在执行（execution_results_shard_3.jsonl mtime **07:17:27** 活跃写入，9107 bytes vs 已完成 shard ~14KB ≈ 60% 进度）；`run_on_sandbox.py` PID 1059464→1059475 `--workers 1` 串行执行 shard_3 的 40 脚本；`ss` 见 `ESTAB 10.129.32.75:8654`（sandbox 连接活跃✅）；8654 reachable ✅。log=/tmp/RESCORE_doubao_r3.log 11 行（assemble 完成后无新日志行=正常，sandbox 阶段输出到 shard jsonl）。**infra**：8650/8651/8652/8654 全 OPEN ✅（实际 sandbox 端点）；8653/8669 OPEN ✅；8664/8665 CLOSED（非实际 sandbox 端点，infra 检查用端口，不影响 eval）；/nasdata 371G free ✅；/home 5.8G/99%（非硬阻断，我方产物落 /nasdata）。运维复检：legacy 组件 loop PID 2455466 alive ✅；ops relay PID 2665949 alive ✅（`.last_run_id`=21=inbox RUN_ID 21，无新指令）；zhulong_loop PID 3579323 alive ✅；conductor 未触碰（红线）。**状态不变**：STAGE=B / CONFIG=doubao-seed-2.0-pro-cloud / ROUND=3 / PHASE=running / WAITING=1 / ERROR_COUNT=1。退出等下轮唤醒 harvest 重打分 v2（pgrep run_eval 无输出→grep PASS_RATE /tmp/RESCORE_doubao_r3.log 取 r3 Pass@1 → 记成绩、ERROR_COUNT 归 0 → ROUND≤5 启 r4，**⚠️ r4/r5 启动必带 EVAL_FW_DIR override + source .env**）。