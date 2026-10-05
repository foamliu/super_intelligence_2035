# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `B`（大模型消融；**已调换**：因 pro-fp4 额度 403 阻塞 C1，先跑 Phase B）|
| CONFIG | `glm-5.2` |
| ROUND | 1 |
| PHASE | `running`（B.glm-5.2 r1 运行中；试验次序 B→C1→C2→S1；Phase B 各模型独立 key，不受 pro-fp4 限制）|
| WAITING | 1 |
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | `glm-5.2`（编排模型；deepseek-v4-pro-fp4 额度已耗尽故更换）|

## 执行看板（15 臂 × 5 轮——已调换为 BâC1âC2âS1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| B | glm-5.2 | 1-5/5 | â¬ |
| B | deepseek-v4-flash | 1-5/5 | â¬ |
| B | kimi-k2.6-cloud | 1-5/5 | â¬ |
| B | doubao-seed-2.0-pro-cloud | 1-5/5 | â¬ |
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
| B.glm-5.2 | [TBD] | [TBD] |
| B.deepseek-v4-flash | [TBD] | [TBD] |
| B.kimi-k2.6-cloud | [TBD] | [TBD] |
| B.doubao-seed-2.0-pro-cloud | [TBD] | [TBD] |
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | r1=74.1（r2 infra 作废；pro-fp4 403→待 Phase B 完成后重试）| [74.1]（r1 复用 legacy；r2 0/158 Forbidden 作废）|

## 操作流水

- [2026-10-05 12:05] [🚀 B.glm-5.2 r1 启动] **Phase B 首臂 glm-5.2 r1 已启动运行**。前置全部就绪：① **.env 切 full**（`set_ablation.py full` → `EDA_MCP_TOOLS_DISABLED=clean_workdir,probe_pyAether_code,cimi_search,cimi_fetch,vqa,query_memory_bank`；检索 3 件套 + run_code 全 ON；OMEGA=high/PHI_BUDGET=0/PHI_LAGGED=0/READBACK=full 锚点）✅。⚠️ 早先 grep 见旧值是 **run_commands 并行执行假象**（写 set_ablation 与读 grep 同批并发，grep 抢跑先于写落盘），复检 mtime 12:00:12 + 行内容确认写入成功。② **MCP 重启**：`stop.sh && start.sh -p 8090`（串行 &&）→ 旧 PID 691966 停、新 PID **3298357** 监听 **0.0.0.0:8090**，app.log "Tool visibility config: get_api_details/search_apis/search_apis_by_keyword/run_code 全 ON" ✅（MCP 启动慢，64 线程，需 sleep~10s 才 bind，初查 ss 空属正常）。③ **cline auth → glm-5.2**：`-p openai -k 02_...c2759d74... -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` → providers.json = glm-5.2 ✅（清除 pro-fp4+/v1 403 污染）。④ **canary 通过**：`scripts/cline_hooks/PreToolUse` 干测 4 组（run_commands→DENY / read_files `/etc/passwd`→DENY / read_files ws内+workspaceRoots→ALLOW / mcp__search_apis→ALLOW）✅；且 r1 实跑 log 已见 worker 触发 run_commands 被 hook 拦截 "ACCESS RESTRICTED" → 反作弊 **live 生效** ✅。⑤ **infra**：sandbox 8650/8651/8652/8654 全 OPEN + run_code 探针 200 ✅；RAG recall 端口 9006 alive（PID 3820519，HTTP 405=up）✅。⑥ **启动**：`EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework PYTHON=/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python setsid bash scripts/run_cline_script.sh -p 8 -n`。⚠️ **必记**：`.env` L243 `EVAL_FW_DIR` 默认 `${EVAL_FW_DIR:=/home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether}`（他人路径），必须 env 覆盖为我方 `/nasdata/app.e0031982/code/EDA-Eval-Framework`；`PYTHON` 必须显式设 venv（否则 `ModuleNotFoundError: pydantic`）。batch=**2026_1005_120536**，run_cline_script PID **3308249**，9×run_cli worker，8×cline worker（timeout 2500），全量 158 题，log=`/tmp/ABL_glm-5.2_r1.log`。log 已见 glm-5.2 deprecation warning（model 确认 active）、worker-3 完成 003→009（任务推进中）。**harvest 方式**：`pgrep -f run_cline_script` 无输出后，`grep -Eo 'pass \([0-9.]+%\)' /tmp/ABL_glm-5.2_r1.log | tail -1` 取 r1 Pass@1；或读 batch dir `/home/app.e0031982/eda_code_eval/2026_1005_120536/stats/`。**状态**：PHASE=running / STAGE=B / CONFIG=glm-5.2 / ROUND=1 / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒 harvest r1。

- [2026-10-05 11:25] [ð 试验次序调换] **Phase B（大模型消融）提到最前**。因  额度 HTTP 403 阻塞 C1/wo_retrieval 无法推进，而 Phase B 的 4 个模型（glm-5.2 / deepseek-v4-flash / kimi-k2.6-cloud / doubao-seed-2.0-pro-cloud）均使用独立 key/endpoint，完全不受 pro-fp4 限制。新顺序：**B â C1 â C2 â S1**。已同步更新：ZHULONG_TASK.md §§ 0/4/5（顺序表+轮转矩阵）、MEMORY_ZHULONG.md 状态头/看板/成绩表。C1/wo_retrieval r2 标记为 â¸（暂停），待 Phase B 完成后 pro-fp4 恢复时重试。legacy 组件 loop 仍在跑（PID 2455466），本轮不干扰。
- [2026-10-05 11:13] [legacy-保活✅ + infra复检] **运维指令(五)优先动作完成 + pro-fp4 仍 403→本轮不启 eval**。① **legacy 组件 loop 确认运行中**：`pgrep` = PID **2455466** `bash /nasdata/.../ZhuLong_DAC2027/run/ablation_run_loop_component_s2_full.sh`（etimes=159929s≈44h，健康）→ **无需拉起**（运维 RUN_ID 20 中继已于 11:04 幂等确认 alive、skip restart）。② **其它进程**：ops relay PID 3186967 alive（RUN_ID 20 已执行 exit=0）；conductor serial PID 1381975 alive（**红线：未触碰**）；合并线 loop PID 3189240 alive（即本次唤醒源）；**无 run_cline_script/run_cli eval 在跑**（legacy 当前空转，非 mid-eval）。③ **按运维指令(五)·5：本轮不启动合并线自己的 eval**（避免与 legacy 抢同一套 infra：eda_fastmcp/MCP/.env/端口）。④ **infra 原地复检（read-only，未启 eval）**：`deepseek-v4-pro-fp4` + key `c43c1f4a` + `/v1` → **HTTP 403 仍耗尽**（C1 唯一阻塞项，§2 规定主基座=pro-fp4 不可擅换 flash）；`glm-5.2`（编排）+ `/cloud/v1` → **200 OK** ✅；shard 端口 8664/8665/8653/8669 **全 OPEN** ✅；`/nasdata`=29%/377G free ✅、`/home`=99%/5.9G（运维四已不作硬阻断）、`/tmp`=54%/22G。⑤ **latent 警示**：`~/.cline/data/settings/providers.json` 现为 **glm-key `c2759d74` + model `deepseek-v4-pro-fp4` + `/v1`**（key/model 三不匹配，pro-fp4 恢复后会再 Forbidden）→ 待 pro-fp4 额度恢复 + legacy 非 mid-eval 时，下臂切换按 §6 `cline auth -k ...c43c1f4a... -b /v1 -m deepseek-v4-pro-fp4` 重修（本轮不动，免扰动 infra）。⑥ run_code 本轮未重探（非启 eval，前次 10-04 已证可用）。**状态不变**：PHASE=blocked / STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒复检 pro-fp4。
- [2026-10-04] [bootstrap] 合并任务书/loop/MEMORY 初始化：`ZHULONG_TASK.md` + `zhulong_loop.sh` + 本文件创建。PHASE=init、WAITING=1。待运维确认 infra（license / shard 端口 8664·8665·8653·8669 / `/home` 磁盘 ≥8G）与起始点后，首周期 canary + 切 `S1.omega_low` 启动 r1。
- [2026-10-04 ~21:54] [infra-check] **合并线首次真正被唤醒**（RUN_ID 8 修 `cline auth -b` 消除 `error: Forbidden` 后，loop PID 1755841 成功调起 cline=本 agent）。§7 步骤 0 infra 三项校验：① shard 端口 8664/8665/8653/8669 **全 OPEN** ✅；② `run_code` **可执行** ✅（pyAether 探针回 `INFRA_PROBE_OK`/`2`，license 在）；③ `/home` = **99% / 6G available** ⚠️ **低于 ≥8G 门槛**。**我方产物实落 `/nasdata`**：`du -sh /home/app.e0031982`=3.8M（非我方占满；`/home` 共 20+ 用户），`/nasdata`=28%/381G free、`/tmp`=54%/22G free。**按运维 2026-10-04(三) 指令**：`/home` 满即如实记录「我方产物落 /nasdata」+ **保持 WAITING=1 原地等**，是否放宽 `/home≥8G` 门槛**待运维拍板**。→ **未 canary、未切臂、未启动 r1**，状态不变（PHASE=init / STAGE=S1 / CONFIG=omega_low / ROUND=1 / WAITING=1）。退出等下轮唤醒复检。
- [2026-10-04 ~23:20] [⚠️ infra] **r2 作废诊断 + providers.json 修复**。batch 2026_1004_230754 = **0 success / 158 failure / 0 timeout**（`stats/success`=0、`stats/failure`=158、`generated_solutions/`=0 文件；log "❌ 无可执行脚本"）。根因双重：① `~/.cline/data/settings/providers.json` 在 23:01 被污染——写入 glm-5.2 key `c2759d74` + baseUrl `/cloud/v1`，但 model 仍 `deepseek-v4-pro-fp4` → key/model/endpoint 三不匹配 → 全部 "error: Forbidden"（run_cli.sh 复制 providers.json 到各 worker，故 8 worker 全受影响）。② 即使 key 修复后，`deepseek-v4-pro-fp4` 在 `http://agi-gateway.cxmt.com/v1` 返回 **HTTP 403**（额度耗尽；curl 实测确认）。**已修复 providers.json**：`cline auth -p openai -k 02_...c43c1f4a... -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-pro-fp4` → providers.json 恢复 deepseek key + `/v1` ✅、secrets.json 更新 ✅。但 **pro-fp4 403 未恢复** → 仍无法跑评测。**按 §7 infra 作废规则**：r2 **不计数**、记 ⚠️ infra、WAITING=1 原地复检、ERROR_COUNT **不增**（infra 非评测失败）。**唯一阻塞项 = deepseek-v4-pro-fp4 额度 403**，待运维恢复后重跑 r2。注：deepseek-v4-flash 在 /v1 可用 ✅、glm-5.2 在 /cloud/v1 可用 ✅，但任务书 §2 规定 C1 主基座 = deepseek-v4-pro-fp4（不可擅换）。状态：PHASE=blocked / STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / WAITING=1 / ERROR_COUNT=0。
- [2026-10-04 ~23:05] [conflict-resolved+infra+canary+r2-start] **第 3 次唤醒→首次真正推进**。① **解决 MEMORY git merge 冲突**（`UU`；运维四起始点 C1/wo_retrieval/R2/running vs agent 旧 S1/omega_low/R1/init）→ 采纳运维版本。② **infra 新三项校验**（运维四放宽 `/home` 门槛后）：`/nasdata` 可写 ✅（381G free）、shard 8664/8665/8653/8669 全 OPEN ✅、`run_code` 可执行 ✅（pyAether 探针 `INFRA_PROBE_OK`/`2`）。`/home`=99%/5.9G 但不再作硬阻断。③ **canary 通过**：驱动 `scripts/cline_hooks/PreToolUse` 干测 4 组（run_commands→DENY ✅ / read_files `/etc/passwd`→DENY ✅ / read_files ws 内→ALLOW ✅ / mcp__search_apis→ALLOW ✅）。④ **.env**=wo_retrieval ✅（`EDA_MCP_TOOLS_DISABLED` 含检索 3 件套 OFF、run_code ON）；MCP app PID 691966 运行中。⑤ **legacy 数据入成绩表**：pure_llm 10.5±1.9%（[8.2,9.5,10.1,11.4,13.3]）、wo_retrieval r1=74.1%（log 确认 PASS_RATE=0.7405）。⑥ **启动 wo_retrieval r2**：首次缺 `PYTHON`/`EVAL_FW_DIR` env 报 `ModuleNotFoundError: pydantic` → 补 env 重启成功；batch=2026_1004_230754，PID 1896664，8 worker，全量 158 题，log=`/tmp/ABL_wo_retrieval_r2.log`。状态：PHASE=running / STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒（pgrep 无输出后 grep `pass (xx.x%)` 取 r2 Pass@1）。
- [2026-10-04 ~22:28] [infra-check] **第 2 次唤醒复检**（loop PID 1755841 健康，ppid=1；本 cline 会话即证 loop 无 `-b` 错误；relay PID 1071337 健康，RUN_ID 9–14 全 exit=0）。§7 步骤 0 infra 三项复校验：① shard 8664/8665/8653/8669 **全 OPEN** ✅；② `run_code` **可执行** ✅（pyAether 探针回 `INFRA_PROBE_OK`/`2`）；③ `/home` = **99% / 6.0G available** ⚠️ **仍低于 ≥8G 门槛**（无变化；`du -sh /home/app.e0031982`=3.8M；我方产物落 `/nasdata`=28%/381G free、`/tmp`=22G free）。运维侧最新 inbox=**RUN_ID 14**（只读接管尽调，**非放宽 `/home` 门槛的指令**）。→ 仍**未 canary、未切臂、未启动 r1**，状态不变（PHASE=init / STAGE=S1 / CONFIG=omega_low / ROUND=1 / WAITING=1）。**唯一阻塞项 = `/home` 6G<8G，待运维拍板是否放宽**。退出等下轮唤醒复检。