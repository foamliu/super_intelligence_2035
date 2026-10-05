# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C1`（组件；S1 段跳过，见任务书运维指令（四））|
| CONFIG | `wo_retrieval` |
| ROUND | 2（r1=74.1% 复用 legacy；从 r2 续跑）|
| PHASE | `blocked`（⚠️ infra：r2 作废，pro-fp4 额度 403）|
| WAITING | 1（⚠️ infra 原地复检：pro-fp4 额度 403）|
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | `glm-5.2`（编排模型；deepseek-v4-pro-fp4 额度已耗尽故更换）|

## 执行看板（15 臂 × 5 轮）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| S1 | omega_low | 1-5/5 | ⬜（旧 5-run 已出 r1=81.6 / r2=82.3，待运维定是否延续）|
| S1 | readback_binary | 1-5/5 | ⬜ |
| S1 | readback_none | 1-5/5 | ⬜ |
| C1 | pure_llm | 5/5 ✅ | ✅ 10.5±1.9%（复用 legacy：[8.2,9.5,10.1,11.4,13.3]）|
| C1 | rag | 0/5 | ⬜（legacy 68.2±7.4% 作废→须本线重跑）|
| C1 | wo_retrieval | 1/5 → r2 ⚠️infra作废 | r1=74.1% 复用 legacy；r2 0/158 Forbidden（providers.json被污染+pro-fp4额度403）|
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
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | r1=74.1（r2⚠️infra作废）| [74.1]（r1 复用 legacy；r2=0/158 Forbidden 作废；r2-r5 待重跑）|

## 操作流水

- [2026-10-04] [bootstrap] 合并任务书/loop/MEMORY 初始化：`ZHULONG_TASK.md` + `zhulong_loop.sh` + 本文件创建。PHASE=init、WAITING=1。待运维确认 infra（license / shard 端口 8664·8665·8653·8669 / `/home` 磁盘 ≥8G）与起始点后，首周期 canary + 切 `S1.omega_low` 启动 r1。
- [2026-10-04 ~21:54] [infra-check] **合并线首次真正被唤醒**（RUN_ID 8 修 `cline auth -b` 消除 `error: Forbidden` 后，loop PID 1755841 成功调起 cline=本 agent）。§7 步骤 0 infra 三项校验：① shard 端口 8664/8665/8653/8669 **全 OPEN** ✅；② `run_code` **可执行** ✅（pyAether 探针回 `INFRA_PROBE_OK`/`2`，license 在）；③ `/home` = **99% / 6G available** ⚠️ **低于 ≥8G 门槛**。**我方产物实落 `/nasdata`**：`du -sh /home/app.e0031982`=3.8M（非我方占满；`/home` 共 20+ 用户），`/nasdata`=28%/381G free、`/tmp`=54%/22G free。**按运维 2026-10-04(三) 指令**：`/home` 满即如实记录「我方产物落 /nasdata」+ **保持 WAITING=1 原地等**，是否放宽 `/home≥8G` 门槛**待运维拍板**。→ **未 canary、未切臂、未启动 r1**，状态不变（PHASE=init / STAGE=S1 / CONFIG=omega_low / ROUND=1 / WAITING=1）。退出等下轮唤醒复检。
- [2026-10-04 ~23:20] [⚠️ infra] **r2 作废诊断 + providers.json 修复**。batch 2026_1004_230754 = **0 success / 158 failure / 0 timeout**（`stats/success`=0、`stats/failure`=158、`generated_solutions/`=0 文件；log "❌ 无可执行脚本"）。根因双重：① `~/.cline/data/settings/providers.json` 在 23:01 被污染——写入 glm-5.2 key `c2759d74` + baseUrl `/cloud/v1`，但 model 仍 `deepseek-v4-pro-fp4` → key/model/endpoint 三不匹配 → 全部 "error: Forbidden"（run_cli.sh 复制 providers.json 到各 worker，故 8 worker 全受影响）。② 即使 key 修复后，`deepseek-v4-pro-fp4` 在 `http://agi-gateway.cxmt.com/v1` 返回 **HTTP 403**（额度耗尽；curl 实测确认）。**已修复 providers.json**：`cline auth -p openai -k 02_...c43c1f4a... -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-pro-fp4` → providers.json 恢复 deepseek key + `/v1` ✅、secrets.json 更新 ✅。但 **pro-fp4 403 未恢复** → 仍无法跑评测。**按 §7 infra 作废规则**：r2 **不计数**、记 ⚠️ infra、WAITING=1 原地复检、ERROR_COUNT **不增**（infra 非评测失败）。**唯一阻塞项 = deepseek-v4-pro-fp4 额度 403**，待运维恢复后重跑 r2。注：deepseek-v4-flash 在 /v1 可用 ✅、glm-5.2 在 /cloud/v1 可用 ✅，但任务书 §2 规定 C1 主基座 = deepseek-v4-pro-fp4（不可擅换）。状态：PHASE=blocked / STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / WAITING=1 / ERROR_COUNT=0。
- [2026-10-04 ~23:05] [conflict-resolved+infra+canary+r2-start] **第 3 次唤醒→首次真正推进**。① **解决 MEMORY git merge 冲突**（`UU`；运维四起始点 C1/wo_retrieval/R2/running vs agent 旧 S1/omega_low/R1/init）→ 采纳运维版本。② **infra 新三项校验**（运维四放宽 `/home` 门槛后）：`/nasdata` 可写 ✅（381G free）、shard 8664/8665/8653/8669 全 OPEN ✅、`run_code` 可执行 ✅（pyAether 探针 `INFRA_PROBE_OK`/`2`）。`/home`=99%/5.9G 但不再作硬阻断。③ **canary 通过**：驱动 `scripts/cline_hooks/PreToolUse` 干测 4 组（run_commands→DENY ✅ / read_files `/etc/passwd`→DENY ✅ / read_files ws 内→ALLOW ✅ / mcp__search_apis→ALLOW ✅）。④ **.env**=wo_retrieval ✅（`EDA_MCP_TOOLS_DISABLED` 含检索 3 件套 OFF、run_code ON）；MCP app PID 691966 运行中。⑤ **legacy 数据入成绩表**：pure_llm 10.5±1.9%（[8.2,9.5,10.1,11.4,13.3]）、wo_retrieval r1=74.1%（log 确认 PASS_RATE=0.7405）。⑥ **启动 wo_retrieval r2**：首次缺 `PYTHON`/`EVAL_FW_DIR` env 报 `ModuleNotFoundError: pydantic` → 补 env 重启成功；batch=2026_1004_230754，PID 1896664，8 worker，全量 158 题，log=`/tmp/ABL_wo_retrieval_r2.log`。状态：PHASE=running / STAGE=C1 / CONFIG=wo_retrieval / ROUND=2 / WAITING=1 / ERROR_COUNT=0。退出等下轮唤醒（pgrep 无输出后 grep `pass (xx.x%)` 取 r2 Pass@1）。
- [2026-10-04 ~22:28] [infra-check] **第 2 次唤醒复检**（loop PID 1755841 健康，ppid=1；本 cline 会话即证 loop 无 `-b` 错误；relay PID 1071337 健康，RUN_ID 9–14 全 exit=0）。§7 步骤 0 infra 三项复校验：① shard 8664/8665/8653/8669 **全 OPEN** ✅；② `run_code` **可执行** ✅（pyAether 探针回 `INFRA_PROBE_OK`/`2`）；③ `/home` = **99% / 6.0G available** ⚠️ **仍低于 ≥8G 门槛**（无变化；`du -sh /home/app.e0031982`=3.8M；我方产物落 `/nasdata`=28%/381G free、`/tmp`=22G free）。运维侧最新 inbox=**RUN_ID 14**（只读接管尽调，**非放宽 `/home` 门槛的指令**）。→ 仍**未 canary、未切臂、未启动 r1**，状态不变（PHASE=init / STAGE=S1 / CONFIG=omega_low / ROUND=1 / WAITING=1）。**唯一阻塞项 = `/home` 6G<8G，待运维拍板是否放宽**。退出等下轮唤醒复检。