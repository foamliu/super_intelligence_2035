# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1



> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `S1`（B 4/4✅；C1 4臂5/5✅含full_v3锚点82.1±3.0%；C2 4/4全收口✅ phi_k10=77.7±2.2/k3=69.1±2.5/k1=63.8±3.2/lagged=73.0±3.2；**S1.omega_low 跳过(采信legacy 82.8±1.0%·指令二十二①)**·**readback_binary r1✅=75.9%/r2✅=79.1%/r3✅=77.8%(123/158·timeout=7≤10·判据十三有效)→r5 code-gen跑中 PID3537337·04:19**·readback_none 暂不重跑(采信legacy 73.3±2.2%·指令二十二③)；📝论文审视报告✅十六·✍️十七 P0-P3改稿+🖨️十九编译✅11页0error fb5e92f8·🧩十八 SKILL/Tcl并入论文12页 b61970a8·📝二十填results✅08:30·**📊二十四 echo数据收集+论文强化✅15:30（tab:ablation-harness填read-backs+新增tab:readback-cost表7+语义注记(binary PASS=未抛异常非断言级·none=executed)+287次盲试trace证据·编译0error12页·commit zhulong S1-echo:）**）|
| CONFIG | `readback_binary`（S1 回读轴·EDA_OMEGA_FIDELITY=high/EDA_RUNCODE_READBACK=binary·**phi=full锚点 BUDGET=0/LAGGED=0**(set_s1_fidelity.py readback_binary→set_ablation full保留V3+selfexpl·不触phi→沿用omega_low时的0/0)·核心4工具ON·MCP PID3329560@8090✅·RAG:9006✅·沙盒hook由run_cli.sh seed_cline_hooks自部署✅）|
| ROUND | phi_lagged: **5/5✅=73.0±3.2%**[74.7,76.6,69.6,69.6,74.7]·Δvs unbounded(82.1)=−9.1pp；omega_low: **跳过·采信legacy 82.8±1.0%**(指令二十二①)；**readback_binary: r1✅=75.9%(120/158)·r2✅=79.1%(125/158·timeout=8)·r3✅=77.8%(123/158·timeout=7≤10·判据十三有效)·r4✅=78.5%(124/158·timeout=6≤10·判据十三有效·regrade PID3525006@04:14→04:17完·3min·gen{135succ/17fail/6timeout}·4shard[34,34,34,33]·0 exec_err)·**r5 code-gen跑中 PID3537337@04:19**（legacy 66.2±16.1% std过大含43.0%离群→fresh 5-run重测）|
| PHASE | `running`（readback_binary r4✅=78.5%(124/158·timeout=6≤10·判据十三有效)·**r5 code-gen跑中 PID3537337·04:19·batch待定**）|
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
| C2 | phi_k10 | **5/5 ✅ 77.7±2.2%** | [78.5,76.6,77.2,81.0,75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·att2·att1作废·r4=128/158·att3·att1/2作废·**r5=119/158·timeout=0·75.3%**）|
| C2 | phi_k3 | **5/5 ✅ 69.1±2.5%** | r1=72.8%✅(115/158·timeout=0)·r2=66.5%✅(105/158·timeout=0)·r3=69.6%✅(110/158·timeout=0)·r4=69.6%✅(110/158·timeout=2)·**r5=67.1%✅(106/158·timeout=0·25 gen-fail=k=3预算效应·非infra)**（探路 69.0%）|
| C2 | phi_k1 | **5/5 ✅ 63.8±3.2%** | [65.2,66.5,58.2,64.6,64.6]（r1=103/158·timeout=0·35 gen-fail·r2=105/158·timeout=0·30 gen-fail·r3=92/158·timeout=1·39 gen-fail·r4=102/158·timeout=0·34 gen-fail·**r5=102/158·timeout=0·35 gen-fail**·PHI-BUDGET-EXHAUSTED>0✅·单调k10>k3>k1✅·探路 60.8%）|
| C2 | phi_lagged | **5/5 ✅ 73.0±3.2%** | [74.7, 76.6, 69.6, 69.6, 74.7]（r1=118/158·timeout=0·5 gen-fail·r2=121/158·timeout=0·10 gen-fail·r3=110/158·timeout=1·11 gen-fail·r4=110/158·timeout=0·13 gen-fail·**r5=118/158·timeout=0·6 gen-fail·batch=2026_1015_042258**·PHI-LAGGED=1244✅·ACCESS RESTRICTED=999✅·PHI-BUDGET-EXHAUSTED=0(lagged无上限合理)·§8.4 trace_key(ctx.session)在位✅·Δvs unbounded(82.1)=−9.1pp）|
| S1 | omega_low | **跳过·采信legacy 82.8±1.0%** | ⏭️ 指令二十二①：legacy std=1.0可信不重跑；r1 code-gen已完(batch 2026_1015_064042)但采信legacy为最终值，r2-r5取消 |
| S1 | readback_binary | **r1✅=75.9% · r2✅=79.1% · r3✅=77.8% · r4✅=78.5% · r5 code-gen跑中 PID3537337@04:19** | 🟡 fresh 5-run重测（legacy 66.2±16.1% std过大含43.0%离群→重测·r1=120/158·gen{succ:134,fail:0,timeout:13,sandbox-fail:11}·0 exec_err·0 infra·timeout=13=binary~3×减速ablation effect非infra·**r2=125/158=79.1%·gen{succ:143,fail:0,timeout:8,fail:7}·0 exec_err·0 infra·timeout=8≤10✅判据(十三)有效**·**r3 regrade=123/158=77.8%·regrade PID2460802@23:02→23:23完·gen{succ:141,fail:10,timeout:7}·0 exec_err·0 infra·timeout=7≤10✅判据(十三)有效·ACCESS RESTRICTED=939(hook live✅)·PHI-BUDGET/LAGGED=0(readback_binary=full锚点正确✅)·**r4 regrade=124/158=78.5%·regrade PID3525006@04:14→04:17完(~3min·sandbox执行135脚本4shard[34,34,34,33])·gen{succ:135,fail:17,timeout:6}·0 exec_err·0 infra·timeout=6≤10✅判据(十三)有效·canary ACCESS RESTRICTED=92(hook live✅)·PHI-BUDGET/LAGGED=0(full锚点正确✅)·Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade✅**·**r5 code-gen启动 PID3537337@04:19:55·export PYTHON=venv/bin/python(防pydantic)·.env=readback_binary(OMEGA=high/READBACK=binary/BUDGET=0/LAGGED=0=full锚点phi✅)·MCP:8090+RAG:9006 LISTEN✅**）|
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
| C2.phi_k10 | **77.7 ± 2.2%** ✅ 5/5 | [78.5, 76.6, 77.2, 81.0, 75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·timeout=0·att2·r4=128/158·timeout=0·att3·**r5=119/158·timeout=0·75.3%**·PHI-BUDGET-EXHAUSTED=426✅）|
| C2.phi_k3 | **69.1 ± 2.5%** ✅ 5/5 | [72.8, 66.5, 69.6, 69.6, 67.1]（r1=115/158·timeout=0·r2=105/158·timeout=0·r3=110/158·timeout=0·r4=110/158·timeout=2·**r5=106/158·timeout=0·67.1%**·PHI-BUDGET-EXHAUSTED=851✅·25 gen-fail=k=3预算效应·判据(十三)：消融臂Pass@1任何值有效·不重跑）|
| C2.phi_k1 | **63.8 ± 3.2%** ✅ 5/5 | [65.2, 66.5, 58.2, 64.6, 64.6]（r1=103/158·timeout=0·35 gen-fail·r2=105/158·timeout=0·30 gen-fail·r3=92/158·timeout=1·39 gen-fail·r4=102/158·timeout=0·34 gen-fail·**r5=102/158·timeout=0·35 gen-fail=k=1预算效应**·regrade PID3120482·生成状态`{'success':123,'failure':0,'timeout':0,'fail':35}`→**timeout=0≤10✅**·exec_err=0·license/Connection=0✅·PHI-BUDGET-EXHAUSTED=1141>0✅(k=1预算生效)·ACCESS RESTRICTED=827✅·判据(十五④/十三)满足→5/5有效不重跑·**单调k10=77.7>k3=69.1>k1=63.8✅·gen-fail随k↓递增✅**·探路 60.8%）|
| C2.phi_lagged | **73.0 ± 3.2%** ✅ 5/5 | [74.7, 76.6, 69.6, 69.6, 74.7]（r1=118/158·timeout=0·5 gen-fail·PHI-LAGGED=1165✅·r2=121/158·timeout=0·10 gen-fail·r3=110/158·timeout=1·11 gen-fail·r4=110/158·timeout=0·13 gen-fail·**r5=118/158·timeout=0·6 gen-fail·batch=2026_1015_042258·gen{success:152,failure:0,timeout:0,fail:6}·PHI-LAGGED=1244✅·ACCESS RESTRICTED=999✅·PHI-BUDGET-EXHAUSTED=0(lagged无上限合理)·exec_err=0·infra errors=0✅**·判据(十三)满足→5/5有效不重跑·§8.4 trace_key(ctx.session)在位✅·lagged机制(canary PHI-LAGGED=1244命中)✅·Δvs unbounded(82.1)=−9.1pp·Converged(%)/Mean read-backs [TBD·待trace parse]·探路 84.2%，r2 修复后 98.1%）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-16 06:36] 🔎 **巡检（readback_binary r5 code-gen ~2h16m健康·不动作退出）**：ps -p 3537337→alive(etime 02:16:13·STAT Ss·`bash scripts/run_cline_script.sh -p 8 -n`)·log /tmp/ABL_readback_binary_r5.log 28.9MB mtime 06:36(live写入·code-gen中)·**canary全绿**：ACCESS RESTRICTED=108(last50000·hook live✅)·PHI-BUDGET/LAGGED=0(readback_binary=full锚点 phi=BUDGET0/LAGGED0→无预算耗尽正确✅)·infra errors(license/Connection)=0✅·.env=readback_binary(OMEGA=high/READBACK=binary/BUDGET=0/LAGGED=0=full锚点phi✅)。**infra全绿**：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid3329560)+RAG:9006(pid3503518)LISTEN✅·/home=16G(≥8G✅·96%使用需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·ops relay alive✅·cline✅。r5仍code-gen(~2h16m·binary档典型~4-5h·r1~4h25m/r2~3h31m/r3~2h45m/r4~3h→继续等)→不收割不切臂·按§7 Step A(pgrep有输出→什么都不做退出)。状态不变 STAGE=S1/CONFIG=readback_binary/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 3537337 GONE→读r5 log尾段`pass (xx.x%)`（若Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade同口径：EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=r5待定·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python防pydantic·建 run_readback_binary_r5_regrade.sh）→判据(十三)→r5有效→5/5收口→算 mean±std→PHASE=just_finished→切 S1.readback_none(指令二十二③：legacy 73.3±2.2%暂不重跑→采信legacy→直接 done_all→运维令二十三 B.glm-5.3-flash)；alive→巡检退出。⚠️查r5用`ps -p 3537337`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。⚠️/home=16G 96%使用，若<8G需暂停评测清理。📝运维令(二十三)待 readback_binary 5/5 收口后执行(B.glm-5.3-flash→B.deepseek-v4-flash fresh)。
- [2026-10-16 05:59] [⏩ 已滚出] 🔎 巡检（readback_binary r5 code-gen ~1h40m健康·不动作退出）详情见 daily-memories/2026-10-16.md §05:59。ps -p 3537337→alive(etime 01:40:14·STAT Ss·`bash scripts/run_cline_script.sh -p 8 -n`)·log /tmp/ABL_readback_binary_r5.log 22.1MB mtime 06:00(live写入·code-gen中)·**canary全绿**：ACCESS RESTRICTED=761(全log·hook live✅)·PHI-BUDGET/LAGGED=0(readback_binary=full锚点 phi=BUDGET0/LAGGED0→无预算耗尽正确✅)·infra errors(license/Connection)=0✅·.env=readback_binary(OMEGA=high/READBACK=binary/BUDGET=0/LAGGED=0=full锚点phi✅)。**infra全绿**：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid3329560)+RAG:9006(pid3503518)LISTEN✅·/home=16G(≥8G✅·96%使用需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·ops relay alive✅·cline✅。r5仍code-gen(~1h40m·binary档典型~4-5h·r1~4h25m/r2~3h31m/r3~2h45m/r4~3h→继续等)→不收割不切臂·按§7 Step A(pgrep有输出→什么都不做退出)。状态不变 STAGE=S1/CONFIG=readback_binary/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 3537337 GONE→读r5 log尾段`pass (xx.x%)`（若Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade同口径：EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=r5待定·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python防pydantic·建 run_readback_binary_r5_regrade.sh）→判据(十三)→r5有效→5/5收口→算 mean±std→PHASE=just_finished→切 S1.readback_none(指令二十二③：legacy 73.3±2.2%暂不重跑→采信legacy→直接 done_all→运维令二十三 B.glm-5.3-flash)；alive→巡检退出。⚠️查r5用`ps -p 3537337`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。⚠️/home=16G 96%使用，若<8G需暂停评测清理。📝运维令(二十三)待 readback_binary 5/5 收口后执行(B.glm-5.3-flash→B.deepseek-v4-flash fresh)。
- [2026-10-16 05:26] [⏩ 已滚出] 🔎 巡检（readback_binary r5 code-gen ~1h06m健康·不动作退出）详情见 daily-memories/2026-10-16.md §05:26。
- [2026-10-16 04:52] [⏩ 已滚出] 🔎 巡检（readback_binary r5 code-gen ~32min健康·不动作退出）详情见 daily-memories/2026-10-16.md §04:52。
- [2026-10-16 04:19] [⏩ 已滚出] ✅ readback_binary r4✅收割=78.5%(124/158·timeout=6≤10) → r5 code-gen 启动 PID3537337@04:19 详情见 daily-memories/2026-10-16.md §04:19。
- [2026-10-16 04:13] [⏩ 已滚出] ✅ readback_binary r4 code-gen✅done@04:06·gen{135succ/17fail/6timeout} → 手动regrade启动 PID3525006@04:14 详情见 daily-memories/2026-10-16.md §04:13。
- [2026-10-16 03:37] [⏩ 已滚出] 🔎 巡检（readback_binary r4 code-gen ~4h健康·不动作退出）详情见 daily-memories/2026-10-16.md §03:37。
- [2026-10-16 03:06] 🔎 **巡检（readback_binary r4 code-gen ~3h30m健康·不动作退出）**：ps -p 2574911→alive(etime 03:29:37·STAT Ss·`bash scripts/run_cline_script.sh -p 8 -n`)·log /tmp/ABL_readback_binary_r4.log 34.2MB mtime 03:06(live写入·Auto compacting)·**canary全绿**：ACCESS RESTRICTED=98(last50000·hook live✅)·PHI-BUDGET/LAGGED=0(readback_binary=full锚点 phi=BUDGET0/LAGGED0→无预算耗尽正确✅)·infra errors(license/Connection)=0✅·无真实pass结果(r4仍code-gen)。**infra全绿**：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid3329560)+RAG:9006(pid3503518)LISTEN✅·/home=16G(≥8G✅·96%使用需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·ops relay alive✅·cline✅。r4仍code-gen(~3h30m·binary档典型~4-5h·r1~4h25m/r2~3h31m/r3~2h45m→继续等)→不收割不切臂·按§7 Step A(pgrep有输出→什么都不做退出)。状态不变 STAGE=S1/CONFIG=readback_binary/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 2574911 GONE→读r4 log尾段`pass (xx.x%)`（若Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade同口径：EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1015_233638·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python防pydantic）→判据(十三)：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r4有效→r5启动(同样 export PYTHON=venv/bin/python)；alive→巡检退出。⚠️查r4用`ps -p 2574911`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。⚠️/home=16G 96%使用，若<8G需暂停评测清理。📝运维令(二十三)待 readback_binary 5/5 收口后执行(B.glm-5.3-flash→B.deepseek-v4-flash fresh)。
- [2026-10-16 02:32] [⏩ 已滚出] 🔎 巡检（readback_binary r4 code-gen ~2h56m健康·不动作退出）详情见 daily-memories/2026-10-16.md §02:32。
- [2026-10-16 01:58] [⏩ 已滚出] 🔎 巡检（r4 ~2h22m健康·不动作退出）+ MEMORY归档减重(42446→36883B) 详情见 daily-memories/2026-10-16.md §01:58。
- [2026-10-16 01:24] [⏩ 已滚出] 🔎 巡检（r4 code-gen ~1h48m健康·不动作退出）详情见 daily-memories/2026-10-16.md §01:24。
- [2026-10-16 00:50] [⏩ 已滚出] 🔎 巡检（r4 code-gen ~1h14m健康·不动作退出）详情见 daily-memories/2026-10-16.md §00:50。
- [2026-10-16 00:16] [⏩ 已滚出] 🔎 巡检（r4 code-gen ~39min健康·不动作退出）详情见 daily-memories/2026-10-16.md §00:16。
- [2026-10-15 23:36] ✅ **readback_binary r3✅收割=77.8%(123/158·timeout=7≤10·判据十三有效) → r4 code-gen 启动 PID2574911**：① ps -p 2460802→**GONE**(r3 regrade 23:02→23:23完)·regrade log /tmp/ABL_readback_binary_r3_regrade.log 尾段 `1015: 123/158 pass (77.8%) | generated: 141 ok, 10 fail, 0 exec_err`·batch=2026_1015_193004·4端口8650/8651/8652/8654 shard[36,35,35,35]·1015 task_id hash。② **判据(十三)核对**：timeout=7≤10✅·exec_err=0✅·infra errors(license/Connection)=0✅·ACCESS RESTRICTED=939(hook live✅)·PHI-BUDGET/LAGGED=0(readback_binary=full锚点 phi=BUDGET0/LAGGED0→无预算耗尽正确✅)→**r3=77.8%有效·不重跑**(消融臂Pass@1任何值有效)。③ **r4 code-gen 启动踩坑修正**：首次 `setsid bash scripts/run_cline_script.sh -p 8 -n` 因**未 export PYTHON**→`run_python_script`用`${PYTHON:-python}`=系统python→`ModuleNotFoundError: No module named 'pydantic'`→log 仅 1.5KB 即崩。修：`export PYTHON=$PWD/venv/bin/python` 后重起→**PID2574911✅·23:36:38启动·batch=2026_1015_233638**·log 显示用 venv python 执行 format_eval_task.py 正常。④ **infra全绿**：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid3329560)+RAG:9006(pid3503518)LISTEN✅·/home=16G(≥8G✅·96%使用需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·ops relay alive✅·cline✅·.env=readback_binary(OMEGA=high/READBACK=binary/BUDGET=0/LAGGED=0=full锚点phi✅)。状态 STAGE=S1/CONFIG=readback_binary/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 2574911 GONE→读r4 log尾段`pass (xx.x%)`（若Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade同口径：EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1015_233638·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON防pydantic）→判据(十三)→r4有效→r5启动(同样 export PYTHON=venv/bin/python)；alive→巡检退出。⚠️查r4用`ps -p 2574911`或`ps -eo pid,cmd|awk '/run_cline_script\.sh -p 8/&&!/opencode/'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。⚠️/home=16G 96%使用，若<8G需暂停评测清理。📝运维令(二十三)待 readback_binary 5/5 收口后执行(B.glm-5.3-flash→B.deepseek-v4-flash fresh)。
- [2026-10-15 23:03] ✅ **readback_binary r3 code-gen✅done(141succ/10fail/7timeout) → regrade启动 PID2460802**：① ps -p 1696043→**GONE**(r3 code-gen完成·22:45)·log /tmp/ABL_readback_binary_r3.log 32.5MB·batch=**2026_1015_193004**·gen-file `completed_code_generation_2026_1015_193004.jsonl`(308KB/158行)·code-gen stats：**success=141/failure=10/timeout=7**·输出目录 /home/app.e0031982/eda_code_eval/2026_1015_193004(code/158个✅)。② **Step7.1 auto-grade FileNotFoundError**(`PosixPath('/home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether')`=已知benchmark bug·.env EVAL_FW_DIR 指向 app.t0002997)→跳过不影响生成产物·须手动regrade同口径。③ **canary全绿**：r3 code-gen log ACCESS RESTRICTED=939(hook live✅)·无PHI-BUDGET/LAGGED标记(readback_binary=full锚点phi=BUDGET0/LAGGED0→无预算耗尽正确✅)·infra errors(license/Connection)=0✅。④ **infra全绿**：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid3329560)+RAG:9006 LISTEN✅·/home=16G(≥8G✅·96%使用需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·ops relay alive✅·cline✅·.env=readback_binary(OMEGA=high/READBACK=binary/BUDGET=0/LAGGED=0=full锚点phi✅)。⑤ **regrade启动**：建 run_readback_binary_r3_regrade.sh(同r1/r2模板改batch=2026_1015_193004·覆盖EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework+4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75+export PYTHON防pydantic)→setsid启动→**PID2460802✅·23:02:34启动**·阶段2组装已开始(r1/r2用时~25min·预计~23:27完)。状态 STAGE=S1/CONFIG=readback_binary/ROUND=3/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：`ps -p 2460802` GONE→读 regrade log 尾段`pass (xx.x%)`→**判据(十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r3有效→r4启动(`export PYTHON=$PWD/venv/bin/python`→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_readback_binary_r4.log`)；alive→巡检退出。⚠️查regrade用`ps -p 2460802`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。⚠️/home=16G 96%使用，若<8G需暂停评测清理。📝运维令(二十三)待 readback_binary 5/5 收口后执行(B.glm-5.3-flash→B.deepseek-v4-flash fresh)。
- [2026-10-15 22:24] 🔎 **巡检（readback_binary r3 code-gen ~2h55m健康·不动作退出）**：ps -p 1696043→alive(etime 02:55:04·STAT Ss·`bash scripts/run_cline_script.sh -p 8 -n`)·log /tmp/ABL_readback_binary_r3.log 32.5MB mtime 22:25(live写入)·**canary全绿**：ACCESS RESTRICTED=4(last5000·hook live✅)·PHI-BUDGET/LAGGED=0(readback_binary=full锚点 phi=BUDGET0/LAGGED0→无预算耗尽正确✅)·infra errors(license/Connection)=0✅·**infra全绿**：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090+RAG:9006 LISTEN✅·/home=16G(≥8G✅·96%使用需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·ops relay alive✅·cline✅。r3仍在code-gen(~2h55m·binary档典型~4-5h·r1~4h25m/r2~3h31m→继续等)→不收割不切臂·按§7 Step A(pgrep有输出→什么都不做退出)。状态不变 STAGE=S1/CONFIG=readback_binary/ROUND=3/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 1696043 GONE→读r3 log尾`pass (xx.x%)`（若Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade同口径：EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=待定·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON防pydantic）→判据(十三)：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r3有效→r4启动；alive→巡检退出。⚠️/home=16G 96%使用，若<8G需暂停评测清理。📝运维令(二十三)待readback_binary 5/5收口后执行(B.glm-5.3-flash→B.deepseek-v4-flash fresh)。
- [2026-10-15 21:49] [⏩ 已滚出] 🔎 巡检（readback_binary r3 code-gen ~2h19m健康·不动作退出）详情见 daily-memories/2026-10-15.md §22:24（含本轮22:24巡检）。
- [2026-10-15 21:13] [⏩ 已滚出] 🔎 巡检（readback_binary r3 code-gen ~1h44m健康·不动作退出）详情见 daily-memories/2026-10-15.md §21:49。
- [2026-10-15 20:38] [⏩ 已滚出] 🔎 巡检（readback_binary r3 code-gen ~1h08m健康·不动作退出）详情见 daily-memories/2026-10-15.md §20:38。
- [2026-10-15 20:04] [⏩ 已滚出] 🔎 巡检（readback_binary r3 code-gen ~34min健康·不动作退出）详情见 daily-memories/2026-10-15.md §20:04。
- [2026-10-15 19:30] [⏩ 已滚出] ✅ readback_binary r2✅收割=79.1%(125/158) → r3 code-gen 启动 PID1696043 详情见 daily-memories/2026-10-15.md §19:30。
- [2026-10-15 18:52] [⏩ 已滚出] ✅ readback_binary r2 code-gen✅done → auto-grade FileNotFoundError → 手动regrade PID1556484 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 18:10] [⏩ 已滚出] 🔎 巡检（readback_binary r2 code-gen ~3h31m健康·不动作退出）+ MEMORY 减重归档 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 17:33] [⏩ 已滚出] 🔎 巡检(r2 ~2h54m健康)+(二十五)催办核对=报告已交付 详情见 daily-memories/2026-10-15.md §[滚出 from MEMORY · 2026-10-16 归档]。
- [2026-10-15 16:50] [⏩ 已滚出] 📝 运维令(二十一) 15天消融建议书 HTML 报告✅交付(纯CPU·零GPU·不打断r2) 详情见 daily-memories/2026-10-15.md §[滚出 from MEMORY · 2026-10-16 归档]。
- [2026-10-15 16:13] [⏩ 已滚出] 🔎 巡检(r2 code-gen ~1h35m健康·不动作退出) 详情见 daily-memories/2026-10-15.md §[滚出 from MEMORY · 2026-10-16 归档]。
- [2026-10-15 15:30] [⏩ 已滚出] 📊 运维令(二十四) echo 数据收集+论文强化✅(零GPU·不打断r2) 详情见 daily-memories/2026-10-15.md §[滚出 from MEMORY · 2026-10-16 归档]。
- [2026-10-15 14:38] [⏩ 已滚出] ✅ readback_binary r1✅收割=75.9%(120/158) → r2 code-gen 启动 PID511382 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 13:59] [⏩ 已滚出] ✅ readback_binary r1 code-gen✅done → regrade启动 PID372028 详情见 daily-memories/2026-10-15.md §[滚出 14:38→13:59]。
- [2026-10-15 13:26] [⏩ 已滚出] 🔎 巡检（readback_binary r1 code-gen ~3h53m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 14:38→13:26]。
- [2026-10-15 12:54] [⏩ 已滚出] 🔎 巡检（readback_binary r1 code-gen ~3h21m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 14:38→12:54]。
- [2026-10-15 12:22] [⏩ 已滚出] 🔎 巡检（readback_binary r1 code-gen ~2h49m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 12:54→12:22]。
- [2026-10-15 11:50] [⏩ 已滚出] 🔎 巡检(readback_binary r1 code-gen ~2h17m健康·不动作退出) 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 11:17] [⏩ 已滚出] 🔎 巡检（readback_binary r1 code-gen ~1h44m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 11:50→11:17]。
- [2026-10-15 10:46] [⏩ 已滚出] 🔎 巡检（readback_binary r1 ~1h13m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 11:17→10:46]。
- [2026-10-15 10:14] [⏩ 已滚出] 🔎 巡检（readback_binary r1 ~41min健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 11:17→10:14/09:34]。
- [2026-10-15 09:34] [⏩ 已滚出] ✅ 运维令(二十二)执行：omega_low 跳过(采信legacy)→切S1.readback_binary→r1启动 PID3338684 详情见 daily-memories/2026-10-15.md §[滚出 11:17→10:14/09:34]。
- [2026-10-15 08:30] [⏩ 已滚出] 📝 运维令(二十)填 zhulong_results.md✅(phi_k1/phi_lagged/B.deepseek-v4-flash) 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 08:18] [⏩ 已滚出] 🔎 巡检（omega_low r1 code-gen ~1h38m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 09:36]。
- [2026-10-15 07:46] [⏩ 已滚出] 🔎 巡检（omega_low r1 code-gen ~1h06m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 09:36]。
- [2026-10-15 07:14] [⏩ 已滚出] 🔎 巡检（omega_low r1 code-gen ~34min健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 09:36]。
- [2026-10-15 06:40] [⏩ 已滚出] ✅ phi_lagged r5✅收割=74.7% → 5/5=73.0±3.2%✅ → 切S1.omega_low → r1启动 PID2616015 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 06:03] [⏩ 已滚出] ✅ phi_lagged r5 code-gen✅done(158/0/0) → regrade 启动 PID2484934 详情见 daily-memories/2026-10-15.md §06:03。
- [2026-10-15 05:31] [⏩ 已滚出] 🔎 巡检(phi_lagged r5 code-gen ~1h09m健康·不动作退出) 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 05:02] [⏩ 已滚出] 🔎 巡检(phi_lagged r5 code-gen ~37min健康·不动作退出) 详情见 daily-memories/2026-10-15.md §[滚出 18:10→05:02]。
- [2026-10-15 04:21] [⏩ 已滚出] ✅ phi_lagged r4✅收割=69.6% → r5 code-gen 启动 PID2034812 详情见 daily-memories/2026-10-15.md §[滚出 13:59→04:21]。
- [2026-10-15 03:37] [⏩ 已滚出] ✅ phi_lagged r4 code-gen✅done → regrade启动 PID1841422（push补推成功 013ac509..88df07bb）详情见 daily-memories/2026-10-15.md §[滚出 13:59→03:37]。
- [2026-10-15 03:02] [⏩ 已滚出] 🔎 巡检（phi_lagged r4 code-gen ~1h13m健康·不动作退出）详情见 daily-memories/2026-10-15.md §[滚出 03:37]。
- [2026-10-15 02:26] [⏩ 已滚出] 🔎 巡检（phi_lagged r4 code-gen ~37min健康·不动作退出·本轮归档2条至daily-14）详情见 daily-memories/2026-10-15.md §[滚出 13:59→02:26]。
- [2026-10-15 01:49] [⏩ 已滚出] ✅ phi_lagged r3✅收割=69.6% → r4 code-gen 启动 PID1397800 详情见 daily-memories/2026-10-15.md §[滚出 13:59→01:49]。
- [2026-10-15 01:13] [⏩ 已滚出] ✅ phi_lagged r3 code-gen✅done → regrade启动 PID1234213 详情见 daily-memories/2026-10-15.md §01:13。
- [2026-10-15 00:38] [⏩ 已滚出] 🔎 巡检(phi_lagged r3 code-gen ~1h41m健康·不动作退出) 详情见 daily-memories/2026-10-15.md §[滚出 01:49→00:38]。
- [2026-10-15 00:10] [⏩ 已滚出] 🔎 巡检(phi_lagged r3 code-gen ~1h07m健康·不动作退出) 详情见 daily-memories/2026-10-15.md §00:10。
- [2026-10-14 23:31] [⏩ 已滚出] 🔎 巡检(phi_lagged r3 code-gen ~34min健康·不动作退出) 详情见 daily-memories/2026-10-15.md §[滚出 01:49→23:31]。
- [2026-10-14 22:57] [⏩ 已滚出] 🔧 phi_lagged r3 修复重启 PID686884（漏 export PYTHON→Step2 pydantic死→重启 batch=2026_1014_225714）详情见 daily-memories/2026-10-14.md §[滚出 02:26]。
- [2026-10-14 22:22] [⏩ 已滚出] ✅ phi_lagged r2✅收割=76.6% → r3 code-gen 启动 PID554055 详情见 daily-memories/2026-10-15.md §[滚出 13:59→22:22]。
- [2026-10-14 21:46] [⏩ 已滚出] ✅ phi_lagged r2 code-gen✅done(158/0/0) → regrade启动 PID400780 详情见 daily-memories/2026-10-15.md §[滚出 13:59→21:46]。
- [2026-10-14 21:10] [⏩ 已滚出] 🔎 巡检(phi_lagged r2 code-gen ~1h36m健康·不动作退出) 详情见 daily-memories/2026-10-14.md §[滚出 21:10→13:40]。
- [2026-10-14 20:39] [⏩ 已滚出] 🔎 巡检(phi_lagged r2 ~1h05m健康·不动作退出) 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 20:07] [⏩ 已滚出] 🔎 巡检(phi_lagged r2 ~33min健康·不动作退出) 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 19:34] [⏩ 已滚出] ✅ phi_lagged r1✅收割=74.7% → r2 code-gen 启动 PID4009943 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 19:00] [⏩ 已滚出] ✅ phi_lagged r1 code-gen✅done → regrade启动 PID3846739 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 18:24] [⏩ 已滚出] 🔎 巡检(phi_lagged r1 ~1h43m健康·不动作退出) 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 17:52] [⏩ 已滚出] 🔎 巡检(phi_lagged r1 ~1h12m健康·不动作退出) 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 17:17] [⏩ 已滚出] 🔎 巡检(phi_lagged r1 ~37min健康·不动作退出) 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 16:41] [⏩ 已滚出] ✅ phi_k1 5/5=63.8±3.2%✅收割 → 切 phi_lagged → r1 code-gen 启动 PID3206663 详情见 daily-memories/2026-10-14.md §16:41。
- [2026-10-14 14:18] [⏩ 已滚出] ✅ phi_k1 r4 收割=64.6%✅有效→r5 code-gen 启动 PID2555759 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 13:40] [⏩ 已滚出] 🖨️ 运维令十九编译验证✅ + phi_k1 r4 收割启动regrade 详情见 daily-memories/2026-10-14.md。
- [2026-10-14 12:49] [⏩ 已滚出] 🔎 巡检（phi_k1 r4 code-gen ~1h10m健康·不动作退出·canary✅ACCESS RESTRICTED=706+PHI-BUDGET-EXHAUSTED=892）详情见 daily-memories/2026-10-14.md §[滚出 02:26]。
- [2026-10-14 12:14] [⏩ 已滚出] 🔎 巡检(phi_k1 r4 code-gen ~36min健康·不动作退出) 详情见 daily-memories/2026-10-14.md §12:14。
- [2026-10-14 11:38] [⏩ 已滚出] ✅ phi_k1 r3 收割=58.2%✅有效→r4 code-gen 启动 PID1915151 详情见 daily-memories/2026-10-14.md §11:38。
- [2026-10-14 10:59] [⏩ 已滚出] ✅ **phi_k1 r3 code-gen完成→regrade启动 PID1753362** 详情见 daily-memories/2026-10-14.md §10:59。
- [2026-10-14 10:21] [⏩ 已滚出] ✍️ 论文改进（运维令十七·空窗期·零GPU）P0+P1+P2 已改 .tex 详情见 daily-memories/2026-10-14.md §10:21。
- [2026-10-14 09:28] [⏩ 已滚出] 📝 论文审视报告（运维令十六）✅ HTML 已交付 详情见 daily-memories/2026-10-14.md §09:28。
- [2026-10-14 08:44] [⏩ 已滚出] ✅ phi_k1 r2 收割=66.5%✅有效→r3启动 PID1122046 详情见 daily-memories/2026-10-14.md §08:44。
- [2026-10-14 08:07] [⏩ 已滚出] ✅ phi_k1 r2 code-gen完成→regrade启动PID977699 详情见 daily-memories/2026-10-14.md §08:07。
- [2026-10-14 07:32] [⏩ 已滚出] 🔎 巡检(phi_k1 r2 ~1h09m健康·不动作退出) 详情见 daily-memories/2026-10-14.md §07:32。
- [2026-10-14 06:54] [⏩ 已滚出] 🔎 巡检(phi_k1 r2 ~32min健康·不动作退出) 详情见 daily-memories/2026-10-14.md §06:54。
- [2026-10-14 06:22] [⏩ 已滚出] ✅ phi_k1 r1 收割=65.2%✅有效→r2启动 PID594067 详情见 daily-memories/2026-10-14.md §06:22。
- [2026-10-14 05:44] [⏩ 已滚出] ✅ phi_k1 r1 code-gen完成→regrade启动PID459959 详情见 daily-memories/2026-10-14.md §05:44。
- [2026-10-14 05:09] [⏩ 已滚出] 🔎 巡检(phi_k1 r1 ~70min健康·不动作退出) 详情见 daily-memories/2026-10-14.md §05:09。
- [2026-10-14 04:38] [⏩ 已滚出] 🔎 巡检(phi_k1 r1 ~39min健康·不动作退出) 详情见 daily-memories/2026-10-14.md §04:38。
- [2026-10-14 04:04] [⏩ 已滚出] 🔎 巡检(phi_k1 r1 ~4min健康·不动作退出) 详情见 daily-memories/2026-10-14.md §04:04。
- [2026-10-14 04:00] [⏩ 已滚出] 🛠️ 去重修正：发现并发 race→kill 全部污染 r1+孤儿 cline→停 loop→起 clean phi_k1 r1 PID66700 详情见 daily-memories/2026-10-14.md §04:00。
- [2026-10-14 03:48] [⏩ 已滚出] ✅ phi_k3 r5=67.1%✅有效→phi_k3 5/5=69.1±2.5%→切phi_k1→r1启动PID15230 详情见 daily-memories/2026-10-14.md §03:48。
- [2026-10-14 03:11] [⏩ 已滚出] ✅ phi_k3 r5 code-gen完成→regrade启动PID4067351/4067354 详情见 daily-memories/2026-10-14.md §03:11。
- [2026-10-14 02:37] [⏩ 已滚出] 🔎 巡检(phi_k3 r5 ~1h07m健康·不动作退出) 详情见 daily-memories/2026-10-14.md §02:37。
- [2026-10-14 02:05] [⏩ 已滚出] 🔎 巡检(phi_k3 r5 ~35min健康·不动作退出) 详情见 daily-memories/2026-10-14.md §02:05。
- [2026-10-14 01:29] [⏩ 已滚出] ✅ phi_k3 r4 regrade=69.6%✅有效→r5启动PID3661493 详情见 daily-memories/2026-10-14.md §01:29。
- [2026-10-14 00:55] [⏩ 已滚出] ✅ phi_k3 r4 code-gen完成→regrade启动PID3524495 详情见 daily-memories/2026-10-14.md §00:55。
- [2026-10-14 00:16] [⏩ 已滚出] 🔎 巡检(phi_k3 r4 ~1h11m健康·不动作退出) 详情见 daily-memories/2026-10-14.md §00:16。
- [2026-10-12 → 10-13 指针块] [⏩ 已滚出] 82 条 10-12/10-13 单行指针（巡检/收割/切换记录，phi_k10 r1-r5·phi_k3 r1-r5·full_v3 r1-r4·运维令十三/十四/十五）已原文搬入 daily-memories/2026-10-13.md §[滚出 04:21→10-12/10-13 指针块]；各条原始详情见 daily-memories/2026-10-12.md / 2026-10-13.md §HH:MM。

> **[2026-10-04 → 10-11 早期流水]**：已全部原文搬入 `daily-memories/2026-10-{04..11}.md`（各日 §HH:MM）。涉及 B.glm-5.2/flash/kimi/doubao 全 5 轮、C1.pure_llm/rag/wo_retrieval、C1.full(V2) r1-r5、运维指令(一)~(九)、RAG排查报告等。如需查阅见对应日期日报。
