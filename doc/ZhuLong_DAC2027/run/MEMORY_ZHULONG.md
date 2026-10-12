# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C2`（B 4/4✅；C1 4臂5/5✅含full_v3锚点82.1±3.0%；**C2.phi_k10 r1✅78.5%有效→r2 running**）|
| CONFIG | `phi_k10`（S2 Φ 预算 k=10·EDA_PHI_BUDGET=10/EDA_PHI_LAGGED=0·base=full(V3+selfexpl)保留·set_s2_phi.py 只改预算不动 V3/SKILL_DATA_DIR✅）|
| ROUND | 2（phi_k10 r1✅=78.5%(124/158·timeout=2·§8.3 k臂PHI-BUDGET-EXHAUSTED=441trace>0)·r2 PID4022652 running·log /tmp/ABL_phi_k10_r2.log）|
| PHASE | `running`（r1有效→r2 code-gen进行中→下轮收割r2）|
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
| C1 | full(V2)（旧锚点）| **5/5 ✅ 81.4±4.1%** | [88.0,79.1,77.2,80.4,82.3]（r1=V3文档,r2-r5=V2无自探索→混配置→已由full_v3取代）|
| C1 | full_v3(自探索·正式锚点) | **5/5 ✅ 82.1±3.0%** | [77.8,86.1,81.6,82.3,82.9]（运维指令(十二)补跑「真full=自探索开」·V3+SKILL_DATA_DIR=./docs/skill_data_selfexpl·4端口8650set+RAG:9006·**未复现r1=88.0%**）|
| C2 | phi_k10 | 2/5 | 🔄 r1✅78.5%·r2 running(PID4022652) |
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
| B.deepseek-v4-flash | **16.7 ± 12.3%** | [9.5, 10.1, 19.0, 7.6, 37.3] |
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2] |
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9] |
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | **81.0 ± 4.5%** | [74.1, 86.1, 81.6, 79.7, 83.5] |
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9] |
| C1.full(V2)（旧锚点）| **81.4 ± 4.1%** | [88.0, 79.1, 77.2, 80.4, 82.3]（r1=V3文档混配置→已由full_v3取代）|
| C1.full_v3(自探索·正式锚点) | **82.1 ± 3.0%** ✅ 5/5 | [77.8, 86.1, 81.6, 82.3, 82.9]（运维指令(十二)补跑「真full」V3+自探索·r1=77.8%(123/158·timeout=1)·r2=86.1%(136/158·timeout=1)·r3=81.6%(129/158·timeout=4)·r4=82.3%(130/158·timeout=6)·r5=82.9%(131/158·timeout=5)·**未复现r1=88.0%**）|
| C2.phi_k10 | r1=78.5% | [78.5]（124/158·timeout=2·§8.3 PHI-BUDGET-EXHAUSTED=441trace·r2-r5待跑）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-12 20:17] 🔎 **巡检(phi_k10 r2 ~35min健康·不动作退出)**：pgrep run_cline_script→PID4022652 alive(etime34:40·STAT Ss)·log /tmp/ABL_phi_k10_r2.log 7.6MB mtime20:16(live)·**canary-by-log✅**：ACCESS RESTRICTED=463(hook live>0)·Forbidden=0✅·**§8.3 k臂✅**：`[PHI-BUDGET-EXHAUSTED]`=81 trace(>0·k=10预算约束生效)·run_code=1374·loop PID2302281✅有proxy(https_proxy=http://172.19.92.23:13128)·relay✅alive·/home=29G✅·git clean(ahead0/behind0)。状态不变 STAGE=C2/CONFIG=phi_k10/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。
- [2026-10-12 19:25] ✅ **phi_k10 r1 re-grade=78.5%✅有效→r2启动PID4022652**：ps -p 3875816→已结束·log /tmp/ABL_phi_k10_r1_regrade.log: `124/158 pass (78.5%)`·timeout=2·fail=16·exec_err=0·PASS_RATE=0.7848→**timeout=2≤10✅ 且 Pass@1=78.5%≥75%✅ → r1有效**。infra复检✅：/home=29G·4端口8650/8651/8652/8654 HTTP在听✅·MCP:8090在听✅·hook PreToolUse不存在(运行间隙预期·run_cli.sh Step5部署)·.env核验✅V3+selfexpl+PHI_BUDGET=10+LAGGED=0+8650set+RAG:9006·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=441trace>0·loop PID2302281✅有proxy·relay PID3277328✅alive。`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k10_r2.log 2>&1 < /dev/null &`→PID4022652✅·batch19:41:40。状态 STAGE=C2/CONFIG=phi_k10/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep有输出→巡检退出；无输出→re-grade同口径→timeout≤10且Pass@1≥75%→r2有效→r3。
- [2026-10-12 18:50] ✅ **phi_k10 r1 code-gen完成→auto-grade=1.9%(bug)→re-grade启动PID3875816**：pgrep run_cline_script→**无输出**=r1已结束·log /tmp/ABL_phi_k10_r1.log 23.9MB mtime18:44·统计:成功140/超时2/失败0(158任务)·batch2026_1012_164323·Step7.1 auto-grade=3/158(1.9%)=**已知benchmark bug**·gen_file completed_code_generation_2026_1012_164323.jsonl(158行/140ok)✅·hook PreToolUse已清理(code-gen后正常)·**canary✅**：ACCESS RESTRICTED=926(hook live)·Forbidden=0✅·**§8.3 k臂✅**：`[PHI-BUDGET-EXHAUSTED]`=441 trace(>0·k=10预算约束生效)·run_code=3361·已部署沙盒hook=1✅。`.env`核验✅：V3+selfexpl+PHI_BUDGET=10+LAGGED=0+8650set+RAG:9006。/home=13G✅。创建 `run/run_phi_k10_r1_regrade.sh`→`setsid bash ... > /tmp/ABL_phi_k10_r1_regrade.log 2>&1 &`→PID3875816✅(run_eval.py --lang pyAether --benchmark EDA-Eval-pyAether-158.jsonl)。loop PID2302281✅有proxy·relay PID3277328✅alive·§8.4 ctx.session修复在位(main.py:61-82)✅·git clean(ahead0/behind0)。状态 STAGE=C2/CONFIG=phi_k10/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：grep re-grade log→timeout≤10且Pass@1≥75%→r1有效→启动r2。
- [2026-10-12 18:32] 🔎 **巡检(phi_k10 r1 ~1h49m健康·不动作退出)**：pgrep run_cline_script→PID3158335 alive(etime01:49)·log /tmp/ABL_phi_k10_r1.log 22.8MB mtime18:32(live)·**canary-by-log✅**：ACCESS RESTRICTED=908(hook live>0)·Forbidden=0✅·**§8.3 k臂✅**：`[PHI-BUDGET-EXHAUSTED]`=403 trace(>0·k=10预算约束生效)·run_code=3305·loop PID2302281✅有proxy(https_proxy=http://172.19.92.23:13128)·relay PID3277328✅alive·/home=2G(用户授权口径·phi_k10已在跑不涉新起门槛)·git clean(ahead0/behind0)。状态不变 STAGE=C2/CONFIG=phi_k10/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。
- [2026-10-12 18:01] 🔎 **巡检(phi_k10 r1 ~1h17m健康·不动作退出)**：pgrep run_cline_script→PID3158335 alive(etime01:17:36·STAT Ss)·log /tmp/ABL_phi_k10_r1.log 16.0MB mtime18:01(live)·**canary-by-log✅**：ACCESS RESTRICTED=730(hook live>0)·Forbidden=0✅·**§8.3 k臂✅**：`[PHI-BUDGET-EXHAUSTED]`=244 trace(>0·k=10预算约束生效)·loop PID2302281✅有proxy·relay PID3277328✅alive·git clean(ahead0/behind0)。状态不变 STAGE=C2/CONFIG=phi_k10/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。
- [2026-10-12 17:27] 🔎 **巡检(phi_k10 r1 ~43min健康·不动作退出)**：pgrep run_cline_script→PID3158335 alive(etime43:11·STAT Ss)·log /tmp/ABL_phi_k10_r1.log 9.2MB mtime17:26(live)·**canary-by-log✅**：ACCESS RESTRICTED=532(hook live>0)·**§8.3 k臂✅**：`[PHI-BUDGET-EXHAUSTED]`=143 trace(>0·k=10预算约束生效)·Forbidden=0✅。loop PID2302281✅有proxy(https_proxy=http://172.19.92.23:13128)·relay PID3277328✅alive·/home=2G(用户授权full_v3口径·phi_k10已在跑不涉及新起门槛)。**补推成功**：上次2次push超时根因=本shell(opencode)无proxy→显式 `export https_proxy=http://172.19.92.23:13128` 后 `timeout 200 git push` exit0(81521673..e6847f81)·ahead0✅。状态不变 STAGE=C2/CONFIG=phi_k10/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。
- [2026-10-12 16:43] 🔄✅ **C1.just_finished→切C2.phi_k10+启动r1**：前置全过——loop PID2302281✅有proxy(https_proxy=http://172.19.92.23:13128)·relay PID3277328✅alive(last_run_id=64)·/home=2G(用户授权)·4端口8650/8651/8652/8654全OPEN✅·MCP18890旧残留(无关)·§8.4 ctx.session修复在位(main.py:61-82 `_trace_key_from_ctx`/`ctx.session`✅)·hook生命周期确认(run_cli.sh:125 seed→:366 rm，运行间隙无文件=预期)。`cp .env .env.bak_1791794457`→`venv/bin/python scripts/set_s2_phi.py phi_k10`✅(EDA_PHI_BUDGET=10/LAGGED=0·只改预算，V3+selfexpl+8650set全保留✅)→`stop.sh`exit0(已停止进程)→`start.sh`exit0(Uvicorn on 0.0.0.0:8090✅·API_DATA merged 521 entries)·cline_mcp_settings→`http://10.251.36.15:8090/mcp`✅(autoApprove含search_apis)。`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k10_r1.log 2>&1 &`→PID3158335✅·batch2026_1012_164323·158题·cline执行器·并行8·Step2进行中。**canary-by-log待下轮核**（run_cli.sh Step5部署hook后查「已部署沙盒hook」+ACCESS RESTRICTED>0；§8.3 k臂须有`[PHI-BUDGET-EXHAUSTED]`trace>0）。状态 STAGE=C2/CONFIG=phi_k10/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。⚠️**push 2次超时(网络慢非Forbidden,无报错原文)·commit d42d7614 ahead 1·下轮第一件事补推**。
- [2026-10-12 16:28] ✅ **full_v3 r5 re-grade=82.9%✅有效→5/5=82.1±3.0%→just_finished→三组对照表已交**：ps -p 2850305→**ALIVE:1(进程已结束)**·log /tmp/ABL_full_v3_r5_regrade.log(6878B·mtime16:06)·grep结果:`✅ 1012: 131/158 pass (82.9%) | generated: 145 ok, 8 fail`·PASS_RATE=0.8291·timeout=5·8 fail·0 exec_err→**timeout=5≤10✅ 且 Pass@1=82.9%≥75%✅ → r5有效**。5/5=[77.8,86.1,81.6,82.3,82.9]→mean=82.1±3.0%(python3 statistics.stdev)·V2(r2-r5)=79.8±2.1%·**未复现r1=88.0%**。loop PID2302281✅有proxy(https_proxy=http://172.19.92.23:13128)·relay PID3277328✅alive·/home=2G(用户授权·full_v3已完不阻塞)。MEMORY归档(lines65-233旧流水→daily-memories各日期)→33650B→~24KB。状态 STAGE=C1/CONFIG=full_v3/ROUND=5/PHASE=just_finished/WAITING=0/ERROR_COUNT=0。**下轮**：切C2.phi_k10：`cd $BASE_DIR && python scripts/set_s2_phi.py phi_k10 && bash scripts/stop.sh && bash scripts/start.sh && sleep 3`→canary→启动r1(`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k10_r1.log 2>&1 < /dev/null &`)→PHASE=running/WAITING=1。
- [2026-10-12 15:49] 🔧✅ **full_v3 r5 code-gen✅完成→auto-grade❌1.9%(benchmark bug)→re-grade启动PID2850305**：pgrep `run_cline_script`→**无输出**=r5已结束·log /tmp/ABL_full_v3_r5_8650set.log 25.8MB·统计:成功153/超时5/失败0(158任务)·batch2026_1012_131007·Step7.1 auto-grade=3/158(1.9%)=**已知benchmark bug**·gen_file completed_code_generation_2026_1012_131007.jsonl(158行/145ok)✅·hook PreToolUse已清理(code-gen后正常)·ACCESS RESTRICTED=894✅·Forbidden=0✅。创建 `run/run_full_v3_r5_regrade.sh`·`setsid bash ... > /tmp/ABL_full_v3_r5_regrade.log 2>&1 &`→PID2850305✅。
- [2026-10-12 15:13] 🔎 **巡检(full_v3 r5 code-gen ~123min健康·不动作退出)**：pgrep run_cline_script→有输出(PID2013673 alive~123min)·log 21MB mtime 15:11(live)·Forbidden=0✅·loop✅有proxy·relay alive·/home=3G(授权)。
- [2026-10-12 13:47] 🚨✅ 运维指令(十三)清除卡死 opencode + r5 巡检(code-gen 健康·不动作退出)：`pkill -9 -f 'glm/glm-5[.]2'`→无残留✅；relay PID3277328 alive✅；r5 PID2013673 alive·run_code=1390·ACCESS RESTRICTED=494(hook live✅)。
- [2026-10-12 13:10] [⏩ 已滚出] ✅ full_v3 r4 re-grade=82.3%✅有效→r5启动(PID2013673) 详情见 daily-memories/2026-10-12.md §13:10。
- [2026-10-12 12:58] [⏩ 已滚出] ✅ full_v3 r4 code-gen done→auto-grade 2.5%(bug)→re-grade启动PID1957360 详情见 daily-memories/2026-10-12.md §12:58。
- [2026-10-12 10:40] [⏩ 已滚出] ⠈ 巡检(full_v3 r4 code-gen ~43min 健康·不动作退出) 详情见 daily-memories/2026-10-12.md §10:40。
- [2026-10-12 09:54] [⏩ 已滚出] 🔧✅ full_v3 r3 re-grade=81.6%(129/158)有效→r4启动(PID1017587) 详情见 daily-memories/2026-10-12.md §09:54。
- [2026-10-12 07:04] [⏩ 已滚出] ✅ full_v3 r2 re-grade=86.1%(136/158)有效→r3启动(PID276519) 详情见 daily-memories/2026-10-12.md §07:04。
- [2026-10-12 03:29] [⏩ 已滚出] ✅ full_v3 r1 re-grade=77.8%(123/158)有效→r2启动(PID3619994) 详情见 daily-memories/2026-10-12.md §03:29。
- [2026-10-12 00:43] [⏩ 已滚出] ✅ r5 re-grade=82.3%→full(V2)5/5=81.4±4.1%→.env切V3+MCP重启+full_v3 r1启动 详情见 daily-memories/2026-10-12.md §00:43。

> **[2026-10-04 → 10-11 早期流水]**：已全部原文搬入 `daily-memories/2026-10-{04..11}.md`（各日 §HH:MM）。涉及 B.glm-5.2/flash/kimi/doubao 全 5 轮、C1.pure_llm/rag/wo_retrieval、C1.full(V2) r1-r5、运维指令(一)~(九)、RAG排查报告等。如需查阅见对应日期日报。
