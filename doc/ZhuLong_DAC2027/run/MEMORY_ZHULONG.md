# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C2`（B 4/4✅；C1 4臂5/5✅含full_v3锚点82.1±3.0%；**C2.phi_k10 5/5✅=77.7±2.2%**；phi_k3 r1=72.8%✅有效→**r2 跑中**(运维令十五恢复)）|
| CONFIG | `phi_k3`（S2 Φ 预算 k=3·EDA_PHI_BUDGET=3/EDA_PHI_LAGGED=0·base=full(V3+selfexpl)保留·set_s2_phi.py 只改预算不动 V3/SKILL_DATA_DIR✅）|
| ROUND | 1✅=72.8% → **r2 跑中**(PID1555901·log /tmp/ABL_phi_k3_r2.log·Step3 code-gen·hook✅ACCESS RESTRICTED=14·PHI-BUDGET-EXHAUSTED=0(早期·k=3稍后累计)·timeout=0) |
| PHASE | `running`（运维令(十五)：沙盒已重启，恢复试验·从phi_k3 r2继续·r1=72.8%不回退）|
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
| C2 | phi_k3 | 1✅→**r2跑中** | r1=72.8%✅(115/158·timeout=0·运维令十三:消融臂Pass@1任何值有效)·att2被运维令十四kill(不重跑)·**运维令十五恢复→r2启动PID1555901**（探路 69.0%）|
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
| C2.phi_k10 | **77.7 ± 2.2%** ✅ 5/5 | [78.5, 76.6, 77.2, 81.0, 75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·timeout=0·att2·r4=128/158·timeout=0·att3·**r5=119/158·timeout=0·75.3%**·PHI-BUDGET-EXHAUSTED=426✅）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-13 17:12] ✅ **运维令(十五)执行：沙盒已重启，恢复试验→phi_k3 r2 跑中**：① **5项自检**：`.env` PHI_BUDGET=0(沙盒重启还原)→**修**：`venv/bin/python scripts/set_s2_phi.py phi_k3`→EDA_PHI_BUDGET=3/LAGGED=0·V3+selfexpl保留✅；4端口8650/8651/8652/8654 在**sandbox host 10.129.32.75**全OPEN+run_code实跑返`hello`✅(localhost测3/4 CLOSED是red herring·eval走SANDBOX_HOST)；MCP `bash stop.sh && start.sh`重启→:8090在听✅·tools/list含get_api_details/search_apis✅；hook `~/.cline/hooks/PreToolUse`在位(mtime 10-13 14:31)·r1 att2 log取证 ACCESS RESTRICTED=496>0·PHI-BUDGET-EXHAUSTED=287>0·"已部署沙盒 hook"✅；`df -BG /home`=27G✅；loop PID有proxy✅。② **infra修复记**：首次r2启动`ModuleNotFoundError: pydantic`→`run_cline_script.sh`用`${PYTHON:-python}`·start.sh设PYTHON但**未export**·沙盒重启后shell无PYTHON→fallback系统python缺pydantic→**修**：`export PYTHON=$PWD/venv/bin/python`后重起(venv pydantic 2.12.5✅)·首次r2死在Step2无code-gen·安全重起。③ **r2启动**：`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k3_r2.log`→PID1555901✅·Step3 code-gen中·hook已部署·ACCESS RESTRICTED=14>0·PHI-BUDGET-EXHAUSTED=0(早期·k=3稍后累计)·timeout=0·/home=26G。④ 状态 STAGE=C2/CONFIG=phi_k3/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。**判据(运维令十五④·十三)**：仅 timeout≤10 且无infra故障·Pass@1任何值有效·不得因<75%重跑。**下轮**：pgrep有输出→巡检退出；无输出→auto-grade→re-grade→timeout≤10且无infra故障→r2有效→r3。
- [2026-10-13 15:05] 🛑 **运维令(十四)执行完毕：暂停所有试验（沙盒重启中）**：① 检测phi_k3 r1 att2 code-gen仍在跑（`run_cline_script.sh`父进程已退出但`run_cli.sh`×8 worker + cline子进程~17个仍活·batch=2026_1013_143053·已到task 115-122/158）→ `kill -9`杀`run_cli.sh`(PID757xxx) + 全部cline worker→`ps aux|grep 2026_1013_143053|wc -l`=0✅·att2未完成(114/158 tasks done)·不grading。② **运维令(十三)修正生效**：phi_k3 r1 att1=72.8%(115/158·timeout=0)判为**有效**（消融臂Pass@1任何值都有效·75%下限只适用于full锚点）→ **r1记72.8%**·ERROR_COUNT=0·att2被kill不重跑。③ 状态更新：PHASE=standby（运维令十四：沙盒重启中，暂停试验）·WAITING=1·ERROR_COUNT=0·ROUND=1✅→待恢复后从r2继续。④ **不动`.env`/端口/MCP/hook**（沙盒重启由运维/用户操作）。⑤ 等运维下达「沙盒已就绪，可恢复试验」指令后再继续·恢复时从phi_k3 r2开始·不回退已完成轮次。loop PID2302281仍在跑（有proxy✅）。
- [2026-10-13 14:43] 🔎 巡检(phi_k3 r1 att2 ~13min健康·不动作退出)：PID756199 alive(etime=12:40)·log 2.83MB growing·ACCESS RESTRICTED=150✅·PHI-BUDGET-EXHAUSTED=133✅(k=3预算生效)·timeout=1(低)·/home=28G✅·端口8652 OPEN/8650·8651·8654 CLOSED(3/4·eval正在跑·不阻塞)·loop PID464225有proxy✅·状态不变·WAITING=1。**下轮**：pgrep有输出→巡检退出；无输出→auto-grade→re-grade→timeout≤10且Pass@1≥75%→r1有效→r2。
- [2026-10-13 14:27] ❌🔄 **phi_k3 r1 att1 regrade=72.8%(115/158)<75%→retry att2 code-gen启动**：发现PID628670已死（首次regrade log仅到阶段2）→首次重启regrade发生两进程竞态（第一次run合并0条结果+第二次仅合并91/131条→51.9%假低值）→清理output_dir+杀残留进程→第三次干净regrade完成(14:18-14:26,8min)→**131条结果全合并·0 unknown bug·115/158=72.8%·timeout=0·PASS_RATE=0.7278**·判据 timeout=0≤10✅ 但 Pass@1=72.8%<75%❌→ERROR_COUNT=1→启动att2 code-gen：`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k3_r1_att2.log 2>&1 < /dev/null &`→infra全绿：/home=29G✅·4端口8650/8651/8652/8654全OPEN✅·MCP PID131513✅·loop PID464225有proxy✅·状态 STAGE=C2/CONFIG=phi_k3/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=1。**下轮**：pgrep run_cline_script有输出→巡检退出；无输出→auto-grade→re-grade→timeout≤10且Pass@1≥75%→r1有效→r2。
- [2026-10-13 14:04] ✅ **phi_k3 r1 code-gen完成→regrade启动PID628670**：pgrep run_cline_script无输出→已结束·auto-grade log: `131 ok, 27 fail, 0 exec_err, timeout=0, PASS_RATE=0.0127(1.3% bug)`·batch=completed_code_generation_2026_1013_121129.jsonl·创建`run_phi_k3_r1_regrade.sh`→`setsid bash run_phi_k3_r1_regrade.sh > /tmp/ABL_phi_k3_r1_regrade.log 2>&1 &`→PID628668/628670✅·regrade log: 131脚本组装完成→执行中·infra全绿：/home=29G✅·4端口8650/8651/8652/8654全OPEN✅·hook✅(ACCESS RESTRICTED=846>0)·§8.3 k臂✅(PHI-BUDGET-EXHAUSTED=864>0·k=3预算生效)·loop PID464225✅有proxy·状态不变·WAITING=1。**下轮**：pgrep run_eval无输出→读regrade log→timeout≤10且Pass@1≥75%→r1有效→r2；<75%→retry att2。
- [2026-10-13 13:53] 🔎 巡检(phi_k3 r1 ~86min健康·不动作退出)：PID136983 alive(etime=1:25:31)·log 19MB growing(13:27时17MB)·ACCESS RESTRICTED=822✅·PHI-BUDGET-EXHAUSTED=790✅(k=3预算生效)·timeout提及=24(not final)·/home=28G✅·loop PID464225有proxy✅·状态不变·WAITING=1。**下轮**：pgrep有输出→巡检退出；无输出→auto-grade→re-grade→timeout≤10且Pass@1≥75%→r1有效→r2。
- [2026-10-13 13:27] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~76min) 详情见 daily-memories/2026-10-13.md §13:27。
- [2026-10-13 13:02] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~51min) 详情见 daily-memories/2026-10-13.md §13:02。
- [2026-10-13 12:53] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~40min) 详情见 daily-memories/2026-10-13.md §12:53。
- [2026-10-13 12:28] [⏩ 已滚出] 🔎 巡检(phi_k3 r1 ~15min) 详情见 daily-memories/2026-10-13.md §12:28。
- [2026-10-13 12:13] ✅ **phi_k10 r5 regrade=75.3%✅有效→5/5=77.7±2.2%→just_finished→切phi_k3→r1启动PID136983**：regrade log /tmp/ABL_phi_k10_r5_regrade.log: `119/158 pass (75.3%) | generated: 139 ok, 19 fail, 0 exec_err`·PASS_RATE=0.7532·timeout=0→**timeout=0≤10✅ 且 Pass@1=75.3%≥75%✅ → r5有效**·phi_k10 5/5=[78.5,76.6,77.2,81.0,75.3]→**mean=77.7±2.2%**·PHASE=just_finished→切phi_k3：`set_s2_phi.py phi_k3`→EDA_PHI_BUDGET=3/LAGGED=0·V3+selfexpl保留✅·`stop.sh && start.sh`→MCP:8090(404)✅·4端口8650/8651/8652/8654全OPEN✅·hook✅(run_cli.sh自动部署)·`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k3_r1.log 2>&1 < /dev/null &`→PID136983✅·canary(r1 log): ACCESS RESTRICTED=28(hook live>0)✅·**§8.3 k臂✅**PHI-BUDGET-EXHAUSTED=4(>0·k=3预算约束生效)·infra全绿：/home=29G✅·loop PID464225✅有proxy·状态 STAGE=C2/CONFIG=phi_k3/ROUND=1/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：pgrep有输出→巡检退出；无输出→auto-grade→re-grade→timeout≤10且Pass@1≥75%→r1有效→r2。
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
