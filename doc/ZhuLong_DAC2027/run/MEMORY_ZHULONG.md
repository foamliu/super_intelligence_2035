# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C2`（B 4/4✅；C1 4臂5/5✅含full_v3锚点82.1±3.0%；C2.phi_k10 5/5✅=77.7±2.2%；**C2.phi_k3 5/5✅=69.1±2.5%**；**phi_k1 r1 跑中 PID66700·batch=2026_1014_035939**）|
| CONFIG | `phi_k1`（S2 Φ 预算 k=1·EDA_PHI_BUDGET=1/EDA_PHI_LAGGED=0·base=full(V3+selfexpl)保留·set_s2_phi.py phi_k1 已切+MCP重启PID28018✅·r1 canary hook已部署）|
| ROUND | phi_k3: 1✅=72.8% · 2✅=66.5% · 3✅=69.6% · 4✅=69.6% · **5✅=67.1%(106/158·timeout=0·25 gen-fail=k=3预算效应)** → **5/5=69.1±2.5%✅**; **phi_k1 r1 code-gen✅(05:36停·batch=2026_1014_035939·158行)→auto-grade FileNotFoundError(已知bug)→regrade跑中 PID459959** |
| PHASE | `running`（phi_k1 r1 regrade 跑中 PID459959·等下轮收割）|
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
| C2 | phi_k1 | **r1 code-gen✅→regrade跑中 PID459959** | batch=2026_1014_035939·03:59起·05:36停·auto-grade FileNotFoundError(已知bug)·regrade 05:44起 PID459959·hook✅ACCESS RESTRICTED=895·PHI-BUDGET-EXHAUSTED=1122(k=1预算生效)·infra全绿（探路 60.8%）|
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
| C2.phi_k10 | **77.7 ± 2.2%** ✅ 5/5 | [78.5, 76.6, 77.2, 81.0, 75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·timeout=0·att2·r4=128/158·timeout=0·att3·**r5=119/158·timeout=0·75.3%**·PHI-BUDGET-EXHAUSTED=426✅）|
| C2.phi_k3 | **69.1 ± 2.5%** ✅ 5/5 | [72.8, 66.5, 69.6, 69.6, 67.1]（r1=115/158·timeout=0·r2=105/158·timeout=0·r3=110/158·timeout=0·r4=110/158·timeout=2·**r5=106/158·timeout=0·67.1%**·PHI-BUDGET-EXHAUSTED=851✅·25 gen-fail=k=3预算效应·判据(十三)：消融臂Pass@1任何值有效·不重跑）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-14 05:44] ✅ **phi_k1 r1 code-gen完成→regrade启动PID459959**：① pgrep run_cline_script→无输出·ps -p 66700→GONE → r1 已结束·log /tmp/ABL_phi_k1_r1.log 24.4MB mtime05:36(已停)·batch=2026_1014_035939·gen_file /home/app.e0031982/eda_code_eval/completed_code_generation_2026_1014_035939.jsonl(288KB·158行✅)·**Step7.1 auto-grade失败=FileNotFoundError /home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether[已知benchmark bug·.env EVAL_FW_DIR指向app.t0002997·同phi_k3 r1-r5]**→② 创建 run_phi_k1_r1_regrade.sh（基于r5脚本改batch=2026_1014_035939·覆盖 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·同口径 SANDBOX_ENDPOINTS=8650/8651/8652/8654 + RAG:9006 + SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python防pydantic）→setsid bash run_phi_k1_r1_regrade.sh > /tmp/ABL_phi_k1_r1_regrade.log →PID459959/459993✅·regrade log: 阶段2组装可执行脚本开始·加载158问题·流式读取 gen_file。③ r1 log canary✅：ACCESS RESTRICTED=895(hook live>0)·Forbidden=0·已部署沙盒hook=1✅·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=1122(>0·k=1预算约束生效)·infra全绿：license_error=0·Connection_error=0·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·/home=24G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)。状态 STAGE=C2/CONFIG=phi_k1/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_eval/regrade无输出→读regrade log→**判据(运维令十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r1有效→r2；pgrep有输出→巡检退出。
- [2026-10-14 05:09] 🔎 巡检(phi_k1 r1 ~70min健康·不动作退出)：PID66700 alive(etime1:10:28·STAT Ss)·log /tmp/ABL_phi_k1_r1.log 18.6MB mtime05:10(live)·canary✅：ACCESS RESTRICTED=726(hook live>0)·PHI-BUDGET-EXHAUSTED=869(>0·k=1预算生效)·Forbidden=1(提及非错误)·license_error=0·Connection_error=0✅·hook「已部署沙盒 hook」=1✅·无final pass(0)·gen_file未生成(code-gen仍在进行)。loop PID81827 alive(etime1:07:01·带proxy https_proxy=http://172.19.92.23:13128)✅。infra全绿：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·/home=24G✅·git clean✅。状态不变 STAGE=C2/CONFIG=phi_k1/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR·batch=2026_1014_035939)→判据(十五④/十三)→r1有效→r2。
- [2026-10-14 04:38] 🔎 巡检(phi_k1 r1 ~39min健康·不动作退出)：PID66700 alive(etime38:19·STAT Ss)·log /tmp/ABL_phi_k1_r1.log 10.4MB mtime04:37(live)·canary✅：ACCESS RESTRICTED=546(hook live>0)·PHI-BUDGET-EXHAUSTED=653(>0·k=1预算生效)·Forbidden=0·license_error=0·Connection_error=0✅·hook「已部署沙盒 hook」=1✅·无final pass(code-gen仍在进行)。loop PID81827 alive(etime35:19·STAT Ss·bash zhulong_loop.sh·带proxy https_proxy=http://172.19.92.23:13128)✅。infra全绿：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·/home=24G✅·git clean(up to date)✅。状态不变 STAGE=C2/CONFIG=phi_k1/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR·batch=2026_1014_035939)→判据(十五④/十三)→r1有效→r2。
- [2026-10-14 04:04] 🔎 巡检(phi_k1 r1 ~4min健康·不动作退出)：PID66700 alive(etime4:17·STAT Ss)·log /tmp/ABL_phi_k1_r1.log 960KB mtime04:03(live)·canary✅：ACCESS RESTRICTED=58(hook live>0)·PHI-BUDGET-EXHAUSTED=64(>0·k=1预算生效)·Forbidden=0·license_error=0·Connection_error=0✅·hook「已部署沙盒 hook」=1✅。loop PID81827 alive(etime00:30·ppid=1·04:00去重后带proxy重启)✅。infra全绿：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·/home=24G✅·.env=phi_k1(BUDGET=1/LAGGED=0/selfexpl)✅·git clean(041ac1e6 pushed)✅。状态不变 STAGE=C2/CONFIG=phi_k1/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR·batch=2026_1014_035939)→判据(十五④/十三)→r1有效→r2。
- [2026-10-14 04:00] 🛠️ **去重修正：发现并发 race→kill 全部污染 r1+孤儿 cline→停 loop→起 clean phi_k1 r1 PID66700**：① 复核发现 03:48 那条流水的判定**有误**——它保留的 PID15230 实为**并发 agent 在 03:47 起的 r1**（早于 03:51 MCP 重启，其 03:47–03:51 段 hit 旧 MCP PID8920 仍载 budget=3 → **budget 混跑污染**），而被它 kill 的 31880 才是 budget=1 的干净 r1；且它**保留了 loop PID1523407**→loop 又 spawn 新 agent 起了**更多重复 r1**（batch 2026_1014_034831 / 035211 两批 ~16 个孤儿 cline worker，杀 bash wrapper 后 cline 子进程 reparent 到 systemd 仍 hit 4 端口 → sandbox 端口争用污染 + 共写同一 /tmp/ABL_phi_k1_r1.log → log 交错损坏）。② **去重**：`pkill -9 -u app.e0031982 -f 'eda_code_eval/2026_1014_034'` + `'035'` + 按 PID 显式 kill 残留 cline（45580/45581/46806/46807/51555/51556/52869/52870…）→ 确认 `ps|grep EDA-Eval-PyAether|grep 2026_1014_034|035` = ALL_KILLED·`lsof ABL_phi_k1_r1.log` 无 writer。③ **停 loop 防再 race**：`pkill -f zhulong_loop.sh`→LOOP STOPPED（待 r1 稳定 + commit 后再带 proxy 重启）。④ `rm -f /tmp/ABL_phi_k1_r1.log`（损坏 log）。⑤ **5 项自检全绿**：.env=phi_k1(BUDGET=1/LAGGED=0/SKILL_DATA_DIR=selfexpl)✅·MCP:8090(pid28018)LISTEN✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·hook（log「已部署沙盒 hook」=1）✅·/home=24G✅。⑥ **起 clean r1**：`export PYTHON=$PWD/venv/bin/python`→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k1_r1.log`→**PID66700✅·batch=2026_1014_035939·03:59:39启动**·8 worker 各领 task 001–008·单批单写无碰撞·Step2 格式化完成·hook 已部署·sandbox 4 端口已清理。**r5 收割确认（独立复核）**：regrade log `106/158 pass (67.1%) | generated:133 ok,25 fail,0 exec_err`·timeout=0·无 infra 故障→r5=67.1% 有效（判据十三）→**phi_k3 5/5=[72.8,66.5,69.6,69.6,67.1]=69.1±2.5%✅**。状态 STAGE=C2/CONFIG=phi_k1/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script 有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知 bug)→手动 regrade（覆盖 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·同口径 4 端口+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON 防pydantic）→**判据(运维令十五④/十三)**：仅 timeout≤10 且无 infra 故障·Pass@1 任何值有效·不得因<75%重跑→r1 有效→r2。⚠️ **教训**：查 loop 勿用 `pgrep -f zhulong_loop`（会匹配 opencode cmdline 里的任务书文本→假阴/假阳），用 `ps -eo pid,cmd | grep zhulong_loop.sh`；杀 r1 须连 cline 子进程一起 kill（`pkill -u <user> -f '<batch>'`），否则 cline reparent 到 systemd 继续跑。
- [2026-10-14 03:48] ✅ **phi_k3 r5=67.1%✅有效→phi_k3 5/5=69.1±2.5%→切phi_k1→r1启动PID15230**：① regrade PID4067351已死→log /tmp/ABL_phi_k3_r5_regrade.log(6961B·mtime03:19)完整：`106/158 pass (67.1%) | generated: 133 ok, 25 fail, 0 exec_err`·batch=2026_1014_012928·生成状态`{'success':133,'failure':0,'timeout':0,'fail':25}`→**timeout=0≤10✅**·exec_err=0·license_error=0·Connection_error=0✅·**判据(运维令十五④/十三)满足→r5=67.1%有效**(消融臂Pass@1任何值有效·25 gen-fail=k=3预算效应非infra·不重跑)·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=851>0(k=3预算生效)·反作弊✅ACCESS RESTRICTED=845>0(hook live·已部署沙盒hook=1)。② **phi_k3 5/5=[72.8,66.5,69.6,69.6,67.1]→mean=69.1,std=2.5→69.1±2.5%✅**。③ **切phi_k1**：`./venv/bin/python scripts/set_s2_phi.py phi_k1`→EDA_PHI_BUDGET=1/EDA_PHI_LAGGED=0✅(set_s2_phi.py只改预算不动V3/SKILL_DATA_DIR=selfexpl)·`bash scripts/stop.sh && bash scripts/start.sh`→MCP:8090(pid8920)LISTEN✅·tools含search_apis✅。④ **phi_k1 r1启动**：`export PYTHON=$PWD/venv/bin/python`(防pydantic)·`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k1_r1.log`→PID15230✅·Step2格式化执行中。⑤ **loop状态**：原loop **PID1523407 一直alive且有proxy**(https_proxy=http://172.19.92.23:13128·etime10h50m·ppid=1·是本agent 5038 的祖父 via 5037)——早先"NO_LOOP"是pgrep被opencode cmdline(含任务书全文)污染的**假阴性**。误判下我多起了一个重复loop PID17152→它spawn了**重复opencode PID17159**+**重复phi_k1 r1 PID31880**(setsid detach·17159死后reparent到systemd)→**已全部kill(17159/31880/17152)**·保留原loop 1523407 + 我的r1 15230。原loop 1523407 将~30min后下次唤醒读更新后MEMORY巡检。**教训**：查loop用`ps -eo pid,cmd | grep zhulong_loop`或读/proc/<pid>/comm，勿用`pgrep -f`(会匹配opencode cmdline里的任务书文本)。infra全绿：4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·/home=24G✅·license_error/Connection_error=0✅。状态 STAGE=C2/CONFIG=phi_k1/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知benchmark bug)→手动regrade同口径(覆盖EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework)→**判据(运维令十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r1有效→r2。
- [2026-10-14 03:11] ✅ **phi_k3 r5 code-gen完成→regrade启动PID4067351/4067354**：① pgrep run_cline_script→无输出·ps -p 3661493→GONE → r5 已结束·log /tmp/ABL_phi_k3_r5.log 23.2MB mtime03:03(已停)·batch=2026_1014_012928·gen_file /home/app.e0031982/eda_code_eval/completed_code_generation_2026_1014_012928.jsonl(327KB·158行✅)·**Step7.1 auto-grade失败=FileNotFoundError /home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether[已知benchmark bug·.env EVAL_FW_DIR指向app.t0002997·同r1/r2/r3/r4]**→② 创建 run_phi_k3_r5_regrade.sh（基于r4脚本改batch=2026_1014_012928·覆盖 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·同口径 SANDBOX_ENDPOINTS=8650/8651/8652/8654 + RAG:9006 + SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python防pydantic）→setsid bash run_phi_k3_r5_regrade.sh > /tmp/ABL_phi_k3_r5_regrade.log →PID4067351/4067354✅·regrade log: 组装**133脚本**完成(158任务·25 gen-fail=k=3预算效应·非infra)→sandbox执行中。③ r5 log canary✅：ACCESS RESTRICTED=845(hook live>0)·Forbidden=0·已部署沙盒hook=1·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=851(>0·k=3预算约束生效)·infra全绿：license_error=0·Connection_error=0·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid1530852)LISTEN✅·/home=24G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)。状态 STAGE=C2/CONFIG=phi_k3/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_eval无输出→读regrade log→**判据(运维令十五④·十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r5有效→phi_k3 5/5 mean±std→just_finished→切phi_k1。
- [2026-10-14 02:37] 🔎 巡检(phi_k3 r5 ~1h07m健康·不动作退出)：PID3661493 alive(etime1:07:26·STAT Ss)·log /tmp/ABL_phi_k3_r5.log 17.0MB mtime02:36(live)·canary-by-log✅：ACCESS RESTRICTED=707(hook live>0)·Forbidden=0✅·已部署沙盒hook=1✅·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=634(>0·k=3预算约束生效)·无final pass(code-gen仍在进行)·infra全绿：/home=24G✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090 LISTEN✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)·.env=phi_k3(PHI_BUDGET=3/LAGGED=0/SKILL_DATA_DIR=selfexpl)✅·license_error/Connection_error=0✅·git clean。状态不变 STAGE=C2/CONFIG=phi_k3/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知benchmark bug)→手动regrade同口径→**判据(运维令十五④·十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r5有效→phi_k3 5/5 mean±std→just_finished→切phi_k1。
- [2026-10-14 02:05] 🔎 巡检(phi_k3 r5 ~35min健康·不动作退出)：PID3661493 alive(etime35:31·STAT Ss)·log /tmp/ABL_phi_k3_r5.log 8.9MB mtime02:05(live)·canary-by-log✅：ACCESS RESTRICTED=524(hook live>0)·Forbidden=0✅·已部署沙盒hook=1✅·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=370(>0·k=3预算约束生效)·无final pass(code-gen仍在进行)·infra全绿：/home=24G✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid1530852)LISTEN✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)·license_error=0·Connection_error=0✅。状态不变 STAGE=C2/CONFIG=phi_k3/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知benchmark bug)→手动regrade同口径→**判据(运维令十五④·十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r5有效→phi_k3 5/5 mean±std→just_finished→切phi_k1。
- [2026-10-14 01:29] ✅ **phi_k3 r4 regrade=69.6%✅有效→r5启动PID3661493**：① regrade PID3524495已死→log /tmp/ABL_phi_k3_r4_regrade.log(6880B·mtime01:05)完整：`110/158 pass (69.6%) | generated: 133 ok, 23 fail, 0 exec_err`·batch=2026_1013_230502·生成状态`{'success':133,'failure':0,'timeout':2,'fail':23}`→**timeout=2≤10✅**·exec_err=0·license_error=0·Connection_error=0✅·**判据(运维令十五④·十三)满足→r4=69.6%有效**(消融臂Pass@1任何值有效·23 gen-fail=k=3预算效应非infra·不重跑)·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=838>0(k=3预算生效)·反作弊✅ACCESS RESTRICTED=862>0(hook live·已部署沙盒hook=1)。② **5项自检(运维令十五③)**：.env=phi_k3(PHI_BUDGET=3/LAGGED=0/SKILL_DATA_DIR=selfexpl/V3保留)✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid1530852)LISTEN✅·hook✅(r4 log ACCESS RESTRICTED=862>0·已部署沙盒hook=1)·/home=24G✅·loop✅有proxy。③ **r5启动**：`export PYTHON=$PWD/venv/bin/python`(防ModuleNotFoundError:pydantic·同r2/r3/r4)→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k3_r5.log`→PID3661493✅·Step2格式化执行中(venv python·无pydantic报错)。phi_k3 进度 r1=72.8/r2=66.5/r3=69.6/r4=69.6 四轮均有效。状态 STAGE=C2/CONFIG=phi_k3/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知benchmark bug)→手动regrade同口径→**判据(运维令十五④·十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r5有效→phi_k3 5/5 mean±std→just_finished→切phi_k1。
- [2026-10-14 00:55] ✅ **phi_k3 r4 code-gen完成→regrade启动PID3524495**：① pgrep run_cline_script→无输出·ps -p 3106630→GONE → r4 已结束·log /tmp/ABL_phi_k3_r4.log 22.7MB mtime00:47(已停)·batch=2026_1013_230502·gen_file /home/app.e0031982/eda_code_eval/completed_code_generation_2026_1013_230502.jsonl(321KB·158行✅)·**Step7.1 auto-grade失败=FileNotFoundError /home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether[已知benchmark bug·.env EVAL_FW_DIR指向app.t0002997·同r1/r2/r3]**→② 创建 run_phi_k3_r4_regrade.sh（基于r3脚本改batch=2026_1013_230502·覆盖 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·同口径 SANDBOX_ENDPOINTS=8650/8651/8652/8654 + RAG:9006 + SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python防pydantic）→setsid bash run_phi_k3_r4_regrade.sh > /tmp/ABL_phi_k3_r4_regrade.log →PID3524492/3524495✅·regrade log: 组装**133脚本**完成(158任务·25 gen-fail=k=3预算效应·非infra)→sandbox执行中。③ r4 log canary✅：ACCESS RESTRICTED=862(hook live>0)·Forbidden=0·已部署沙盒hook=1·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=838(>0·k=3预算约束生效)·infra全绿：license_error=0·Connection_error=0·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid1530852)LISTEN✅·/home=24G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)。状态 STAGE=C2/CONFIG=phi_k3/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_eval无输出→读regrade log→**判据(运维令十五④·十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r4有效→r5。
- [2026-10-14 00:16] 🔎 巡检(phi_k3 r4 ~1h11m健康·不动作退出)：PID3106630 alive(etime1:11:36·STAT Ss)·log /tmp/ABL_phi_k3_r4.log 16.5MB mtime00:16(live)·canary-by-log✅：ACCESS RESTRICTED=697(hook live>0)·Forbidden=0✅·已部署沙盒hook=1✅·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=595(>0·k=3预算约束生效)·无final pass(code-gen仍在进行)·infra全绿：/home=24G✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid1530852)LISTEN✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)·license_error=0·Connection_error=0✅·git clean(up to date)。状态不变 STAGE=C2/CONFIG=phi_k3/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade(Step7.1 FileNotFoundError=已知benchmark bug)→手动regrade同口径→**判据(运维令十五④·十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r4有效→r5。
- [2026-10-13 23:41] [⏩ 已滚出] 🔎 巡检(phi_k3 r4 ~34min健康·不动作退出) 详情见 daily-memories/2026-10-13.md §23:41。
- [2026-10-13 23:05] [⏩ 已滚出] ✅ phi_k3 r3 regrade=69.6%✅有效→r4启动PID3106630 详情见 daily-memories/2026-10-13.md §23:05。
- [2026-10-13 22:23] [⏩ 已滚出] ✅ phi_k3 r3 code-gen完成→regrade启动PID2934058 详情见 daily-memories/2026-10-13.md §22:23。
- [2026-10-13 21:46] [⏩ 已滚出] 🔎 巡检(phi_k3 r3 ~1h42m健康·不动作退出) 详情见 daily-memories/2026-10-13.md §21:46。
- [2026-10-13 21:14] [⏩ 已滚出] 🔎 巡检(phi_k3 r3 ~1h10m健康·不动作退出) 详情见 daily-memories/2026-10-13.md §21:14。
- [2026-10-13 20:41] [⏩ 已滚出] 🔎 巡检(phi_k3 r3 ~37min健康·不动作退出) 详情见 daily-memories/2026-10-13.md §20:41。
- [2026-10-13 20:04] [⏩ 已滚出] ✅ phi_k3 r2 收割=66.5%✅有效→r3启动PID2329829 详情见 daily-memories/2026-10-13.md §20:04。
- [2026-10-13 19:27] [⏩ 已滚出] ✅ phi_k3 r2 code-gen完成→regrade启动PID2160638 详情见 daily-memories/2026-10-13.md §19:27。
- [2026-10-13 18:51] [⏩ 已滚出] 🔎 巡检(phi_k3 r2 ~1h40m健康·不动作退出) 详情见 daily-memories/2026-10-13.md §18:51。
- [2026-10-13 18:17] [⏩ 已滚出] 🔎 巡检(phi_k3 r2 ~1h05m健康·不动作退出) 详情见 daily-memories/2026-10-13.md §18:17。
- [2026-10-13 17:41] [⏩ 已滚出] 🔎 巡检(phi_k3 r2 ~29min健康·不动作退出) 详情见 daily-memories/2026-10-13.md §17:41。
- [2026-10-13 17:12] [⏩ 已滚出] ✅ 运维令(十五)执行：沙盒已重启，恢复试验→phi_k3 r2 跑中 详情见 daily-memories/2026-10-13.md §17:12。
- [2026-10-13 15:05] [⏩ 已滚出] 🛑 运维令(十四)执行完毕：暂停所有试验（沙盒重启中） 详情见 daily-memories/2026-10-13.md §15:05。
- [2026-10-13 14:43] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 att2 ~13min健康·不动作退出) 详情见 daily-memories/2026-10-13.md §14:43。
- [2026-10-13 14:27] [⏩ 已滚出] ❌🔄 phi_k3 r1 att1 regrade=72.8%(115/158)<75%→retry att2 code-gen启动 详情见 daily-memories/2026-10-13.md §14:27。
- [2026-10-13 14:04] [⏩ 已滚出] ✅ phi_k3 r1 code-gen完成→regrade启动PID628670 详情见 daily-memories/2026-10-13.md §14:04。
- [2026-10-13 13:53] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~86min健康·不动作退出) 详情见 daily-memories/2026-10-13.md §13:53。
- [2026-10-13 13:27] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~76min) 详情见 daily-memories/2026-10-13.md §13:27。
- [2026-10-13 13:02] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~51min) 详情见 daily-memories/2026-10-13.md §13:02。
- [2026-10-13 12:53] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~40min) 详情见 daily-memories/2026-10-13.md §12:53。
- [2026-10-13 12:28] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~15min) 详情见 daily-memories/2026-10-13.md §12:28。
- [2026-10-13 12:13] [⏩ 已滚出] ✅ phi_k10 r5 regrade=75.3%✅→5/5=77.7±2.2%→切phi_k3→r1启动PID136983 详情见 daily-memories/2026-10-13.md §12:13。
- [2026-10-13 11:49] [⏩ 已滚出] ✅ phi_k10 r5 code-gen完成→regrade PID47140 详情见 daily-memories/2026-10-13.md §11:49。
- [2026-10-13 11:14] [⏩ 已滚出] 🔎 巡检(phi_k10 r5 ~1h49m健康·不动作退出) 详情见 daily-memories/2026-10-13.md §11:14。
- [2026-10-13 10:40] [⏩ 已滚出] 🔎 巡检(phi_k10 r5 ~1h15m) 详情见 daily-memories/2026-10-13.md §10:40。
- [2026-10-13 10:37] [⏩ 已滚出] 🔎 巡检(phi_k10 r5 ~1h09m) 详情见 daily-memories/2026-10-13.md §10:37。
- [2026-10-13 10:04] [⏩ 已滚出] 🔎 巡检(phi_k10 r5 ~38min) 详情见 daily-memories/2026-10-13.md §10:04。
- [2026-10-13 10:01] [⏩ 已滚出] 🔎 巡检(phi_k10 r5 ~35min) 详情见 daily-memories/2026-10-13.md §10:01。
- [2026-10-13 09:31] [⏩ 已滚出] 🔎 巡检(phi_k10 r5 ~5min) 详情见 daily-memories/2026-10-13.md §09:31。
- [2026-10-13 09:25] [⏩ 已滚出] ✅ phi_k10 r4 att3 regrade=81.0%→r5启动 详情见 daily-memories/2026-10-13.md §09:25。
- [2026-10-13 08:57] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att3 ~1h41m) 详情见 daily-memories/2026-10-13.md §08:57。
- [2026-10-13 08:32] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att3 ~76min) 详情见 daily-memories/2026-10-13.md §08:32。
- [2026-10-13 08:22] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att3 ~67min) 详情见 daily-memories/2026-10-13.md §08:22。
- [2026-10-13 07:59] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att3 ~42min) 详情见 daily-memories/2026-10-13.md §07:59。
- [2026-10-13 07:49] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att3 ~33min) 详情见 daily-memories/2026-10-13.md §07:49。
- [2026-10-13 07:30] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att3 ~10min) 详情见 daily-memories/2026-10-13.md §07:30。
- [2026-10-13 07:16] [⏩ 已滚出] ❌🔄 phi_k10 r4 att2 regrade=74.1%<75%→retry att3 详情见 daily-memories/2026-10-13.md §07:16。
- [2026-10-13 07:12] [⏩ 已滚出] 🔄 phi_k10 r4 att2 regrade重启(duplicate conflict处理) 详情见 daily-memories/2026-10-13.md §07:12。
- [2026-10-13 06:51] [⏩ 已滚出] ✅ phi_k10 r4 att2 code-gen完成→re-grade启动 详情见 daily-memories/2026-10-13.md §06:51。
- [2026-10-13 06:18] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att2 ~1h04m) 详情见 daily-memories/2026-10-13.md §06:18。
- [2026-10-13 05:46] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att2 ~33min) 详情见 daily-memories/2026-10-13.md §05:46。
- [2026-10-13 05:43] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 att2 ~30min) 详情见 daily-memories/2026-10-13.md §05:43。
- [2026-10-13 05:13] [⏩ 已滚出] ❌🔄 phi_k10 r4 att1 regrade=63.3%<75%→retry att2 详情见 daily-memories/2026-10-13.md §05:13。
- [2026-10-13 05:10] [⏩ 已滚出] ✅ phi_k10 r4 code-gen完成→regrade已在跑 详情见 daily-memories/2026-10-13.md §05:10。
- [2026-10-13 04:37] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 ~1h07m) 详情见 daily-memories/2026-10-13.md §04:37。
- [2026-10-13 04:28] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 ~58min) 详情见 daily-memories/2026-10-13.md §04:28。
- [2026-10-13 04:05] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 ~35min) 详情见 daily-memories/2026-10-13.md §04:05。
- [2026-10-13 03:57] [⏩ 已滚出] 🔎 巡检(phi_k10 r4 ~27min) 详情见 daily-memories/2026-10-13.md §03:57。
- [2026-10-13 03:28] [⏩ 已滚出] ✅ phi_k10 r3 att2 regrade=77.2%→r4启动 详情见 daily-memories/2026-10-13.md §03:28。
- [2026-10-13 02:55] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 att2 regrade ~2min50s) 详情见 daily-memories/2026-10-13.md §02:55。
- [2026-10-13 02:51] [⏩ 已滚出] ✅ phi_k10 r3 att2 code-gen完成→regrade启动PID1775395 详情见 daily-memories/2026-10-13.md §02:51。
- [2026-10-13 02:21] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 att2 ~1h06m) 详情见 daily-memories/2026-10-13.md §02:21。
- [2026-10-13 02:18] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 att2 ~64min) 详情见 daily-memories/2026-10-13.md §02:18。
- [2026-10-13 01:49] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 att2 ~35min) 详情见 daily-memories/2026-10-13.md §01:49。
- [2026-10-13 01:17] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 att2 ~3min) 详情见 daily-memories/2026-10-13.md §01:17。
- [2026-10-13 01:13] [⏩ 已滚出] ❌🔄 phi_k10 r3 regrade=74.1%<75%→retry att2 PID1325264 详情见 daily-memories/2026-10-13.md §01:13。
- [2026-10-13 00:44] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 regrade ~3min) 详情见 daily-memories/2026-10-13.md §00:44。
- [2026-10-13 00:38] [⏩ 已滚出] ✅ phi_k10 r3 code-gen完成→regrade启动PID1189185 详情见 daily-memories/2026-10-13.md §00:38。
- [2026-10-13 00:12] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 ~103min健康·不动作退出) 详情见 daily-memories/2026-10-13.md §00:12。
- [2026-10-12 23:39] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 ~1h11m健康·不动作退出) 详情见 daily-memories/2026-10-12.md §23:39。
- [2026-10-12 23:32] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 ~1h04m健康·不动作退出) 详情见 daily-memories/2026-10-12.md §23:32。
- [2026-10-12 23:07] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 ~39min健康·不动作退出) 详情见 daily-memories/2026-10-12.md §23:07。
- [2026-10-12 23:01] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 ~32min健康·不动作退出) 详情见 daily-memories/2026-10-12.md §23:01。
- [2026-10-12 22:30] [⏩ 已滚出] 🔎 巡检(phi_k10 r3 ~2min健康·不动作退出) 详情见 daily-memories/2026-10-12.md §22:30。
- [2026-10-12 22:28] [⏩ 已滚出] ✅ phi_k10 r2 re-grade=76.6%✅有效→r3启动PID622197 详情见 daily-memories/2026-10-12.md §22:28。
- [2026-10-12 19:25] [⏩ 已滚出] ✅ phi_k10 r1 re-grade=78.5%✅有效→r2启动PID4022652 详情见 daily-memories/2026-10-12.md §19:25。
- [2026-10-12 18:50] [⏩ 已滚出] ✅ phi_k10 r1 code-gen完成→re-grade启动PID3875816 详情见 daily-memories/2026-10-12.md §18:50。
- [2026-10-12 18:32] [⏩ 已滚出] 🔎 巡检(phi_k10 r1 ~1h49m) 详情见 daily-memories/2026-10-12.md §18:32。
- [2026-10-12 18:01] [⏩ 已滚出] 🔎 巡检(phi_k10 r1 ~1h17m) 详情见 daily-memories/2026-10-12.md §18:01。
- [2026-10-12 17:27] [⏩ 已滚出] 🔎 巡检(phi_k10 r1 ~43min) 详情见 daily-memories/2026-10-12.md §17:27。
- [2026-10-12 16:43] [⏩ 已滚出] 🔄✅ C1.just_finished→切C2.phi_k10+启动r1 详情见 daily-memories/2026-10-12.md §16:43。
- [2026-10-12 16:28] [⏩ 已滚出] ✅ full_v3 r5 re-grade=82.9%→5/5=82.1±3.0%→just_finished 详情见 daily-memories/2026-10-12.md §16:28。
- [2026-10-12 15:49] [⏩ 已滚出] 🔧✅ full_v3 r5 code-gen→re-grade PID2850305 详情见 daily-memories/2026-10-12.md §15:49。
- [2026-10-12 15:13] [⏩ 已滚出] 🔎 巡检(full_v3 r5 ~123min) 详情见 daily-memories/2026-10-12.md §15:13。
- [2026-10-12 13:47] [⏩ 已滚出] 🚨✅ 运维指令(十三)清除卡死opencode+r5巡检 详情见 daily-memories/2026-10-12.md §13:47。
- [2026-10-12 13:10] [⏩ 已滚出] ✅ full_v3 r4 re-grade=82.3%✅有效→r5启动(PID2013673) 详情见 daily-memories/2026-10-12.md §13:10。
- [2026-10-12 12:58] [⏩ 已滚出] ✅ full_v3 r4 code-gen done→auto-grade 2.5%(bug)→re-grade启动PID1957360 详情见 daily-memories/2026-10-12.md §12:58。
- [2026-10-12 10:40] [⏩ 已滚出] ⠈ 巡检(full_v3 r4 code-gen ~43min 健康·不动作退出) 详情见 daily-memories/2026-10-12.md §10:40。
- [2026-10-12 09:54] [⏩ 已滚出] 🔧✅ full_v3 r3 re-grade=81.6%(129/158)有效→r4启动(PID1017587) 详情见 daily-memories/2026-10-12.md §09:54。
- [2026-10-12 07:04] [⏩ 已滚出] ✅ full_v3 r2 re-grade=86.1%(136/158)有效→r3启动(PID276519) 详情见 daily-memories/2026-10-12.md §07:04。
- [2026-10-12 03:29] [⏩ 已滚出] ✅ full_v3 r1 re-grade=77.8%(123/158)有效→r2启动(PID3619994) 详情见 daily-memories/2026-10-12.md §03:29。
- [2026-10-12 00:43] [⏩ 已滚出] ✅ r5 re-grade=82.3%→full(V2)5/5=81.4±4.1%→.env切V3+MCP重启+full_v3 r1启动 详情见 daily-memories/2026-10-12.md §00:43。

> **[2026-10-04 → 10-11 早期流水]**：已全部原文搬入 `daily-memories/2026-10-{04..11}.md`（各日 §HH:MM）。涉及 B.glm-5.2/flash/kimi/doubao 全 5 轮、C1.pure_llm/rag/wo_retrieval、C1.full(V2) r1-r5、运维指令(一)~(九)、RAG排查报告等。如需查阅见对应日期日报。
