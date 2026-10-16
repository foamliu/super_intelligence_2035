# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1
<!-- heartbeat 2026-10-17 00:35 -->



> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `B`（**S1 全收口✅**；**B.glm-5.3-flash 5/5✅=66.8±10.5%**[80.4,53.2,73.4,65.8,61.4]·运维令二十三 done；**B.deepseek-v4-flash fresh r1✅=8.2% · r2=⚠️infra作废(token额度耗尽HTTP429·待~00:52重跑)**·运维令二十三②替换legacy 16.7±12.3%）；B 4/4✅(glm-5.2/flash/kimi/doubao)+glm-5.3-flash 5/5✅+deepseek-v4-flash fresh r1✅r2作废待重跑；C1 4臂5/5✅含full_v3锚点82.1±3.0%；C2 4/4全收口✅；📝论文 tab:ablation-harness(B)已同步）|
| CONFIG | `deepseek-v4-flash`（B 模型消融·运维令二十三②fresh 5-run·full harness: OMEGA=high/READBACK=full/BUDGET=0/LAGGED=0/V3自探索·核心4工具ON·cline auth=openai-compatible deepseek-v4-flash@http://agi-gateway.cxmt.com/v1 key c43c1f4a✅(curl canary HTTP200)·MCP PID146061@8090✅·RAG:9006✅·沙盒hook由run_cli.sh seed_cline_hooks自部署✅）|
| ROUND | **B.deepseek-v4-flash r1✅=8.2%(13/158) · r2 = ⚠️ infra 作废·不计数（token 额度耗尽 HTTP429·全158 fail·待~00:52 重跑）**；B.glm-5.3-flash **5/5✅=66.8±10.5%**[80.4,53.2,73.4,65.8,61.4]|
| PHASE | `running`（B.deepseek-v4-flash **r2 作废·待重跑**：PID3825276 GONE@23:26·batch=2026_1016_232159·gen success=0/failure=158/timeout=0·全 158 任务 `本次Token额度已用完` HTTP429·infra 故障非消融效应·canary curl HTTP429 待恢复55m·额度恢复~00:52·下轮 canary 200→重跑 r2）·4端口8650/8651/8652/8654全OPEN✅·MCP:8090+RAG:9006 alive✅·/home=22G(≥8G✅·95%需关注)·loop有proxy✅·hook deploy@L21→remove@L832(正常清理)·PHI=0 full phi✅·infra errors=158(token quota)·ERROR_COUNT=1）|
| WAITING | 1 |
| ERROR_COUNT | 1（B.deepseek-v4-flash **r2 = ⚠️ infra 作废·不计数**：token 额度耗尽 HTTP429 `本次Token额度已用完`·全 158 code-gen 失败 success=0/failure=158/timeout=0·非真实消融效应·判据十三不适用因属 infra 故障·待额度恢复~00:52 重跑 r2） |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-pro-fp4`（✅HTTP 200 新key e13f4f37 + /cloud/v1；r1-r3旧key 9eed3da1有效同后端 deepseek-v4-pro-260813, r4起新key）|

## 执行看板（15 臂 × 5 轮——已调换为 B→C1→C2→S1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| B | glm-5.2 | 5/5 ✅ | **83.3±3.1%** [84.2,87.3,84.2,79.1,81.6] |
| B | deepseek-v4-flash | 5/5 ✅ | **16.7±12.3%** [9.5,10.1,19.0,7.6,37.3] |
| B | kimi-k2.6-cloud | 5/5 ✅ | **77.0±1.6%** [79.1,76.6,77.2,74.7,77.2] |
| B | doubao-seed-2.0-pro-cloud | 5/5 ✅ | **63.8±1.4%** [63.9,64.6,61.4,65.2,63.9] |
| B | glm-5.3-flash（运维令二十三新臂）| **5/5 ✅ 66.8±10.5%** | [80.4,53.2,73.4,65.8,61.4]（r1=127/158·timeout=9·r2=84/158·timeout=6·r3=116/158·timeout=0·r4=104/158·timeout=0·r5=97/158·timeout=0·各轮exec_err=0·判据十三有效·std=10.5轻量backbone高方差·glm-5.3-flash@/v1 key 6903b05e）|
| B | deepseek-v4-flash（fresh·运维令二十三②）| **r1✅8.2% · r2=⚠️infra作废(token额度耗尽HTTP429·待~00:52重跑)** | 🟡 fresh 5-run 替换 legacy 16.7±12.3%（r5=37.3离群·std过大）·r1=13/158·gen 13ok/145fail·timeout=0·exec_err=0·判据十三有效（弱backbone真实消融效应·与legacy r1=9.5%一致）·**r2=infra作废**：PID3825276 GONE@23:26·batch=2026_1016_232159·gen success=0/failure=158/timeout=0·全158任务`本次Token额度已用完`HTTP429·非消融效应·不计数不regrade·ERROR_COUNT=1·canary curl HTTP429待恢复55m·额度恢复~00:52→重跑r2 ·cline auth=openai-compatible deepseek-v4-flash@/v1 key c43c1f4a✅ |
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
| S1 | readback_binary | **5/5 ✅ 78.1 ± 1.3%** | [75.9,79.1,77.8,78.5,79.1]（fresh 重测·2026-10-15~16·替换 legacy 66.2±16.1% std 过大含 43.0% 离群·运维令二十二②·判据(十三)各轮 timeout=13/8/7/6/4·r5 regrade=79.1%(125/158)·exec_err=0·infra=0✅）|
| S1 | readback_none | **跳过·采信legacy 73.3±2.2%** | ⏭️ 指令二十二③：legacy std=2.2 可信不重跑 |

## 成绩记录（N=5 mean±std，Pass@1 %）

| 臂 | N=5 mean±std | 各轮原始值 |
|:--|:-:|:--|
| B.glm-5.2 | **83.3 ± 3.1%** | [84.2, 87.3, 84.2, 79.1, 81.6] |
| B.deepseek-v4-flash | **16.7 ± 12.3%** | [9.5, 10.1, 19.0, 7.6, 37.3] |
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2] |
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9] |
| B.glm-5.3-flash | **66.8 ± 10.5%** ✅ 5/5 | [80.4, 53.2, 73.4, 65.8, 61.4]（运维令二十三新臂·r1=127/158·timeout=9·r2=84/158·timeout=6·r3=116/158·timeout=0·r4=104/158·timeout=0·r5=97/158·timeout=0·各轮exec_err=0·判据十三有效·std=10.5轻量backbone高方差·glm-5.3-flash@/v1 key 6903b05e）|
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | **81.0 ± 4.5%** | [74.1, 86.1, 81.6, 79.7, 83.5] |
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9] |
| C1.full(V2)（旧锚点）| **81.4 ± 4.1%** | [88.0, 79.1, 77.2, 80.4, 82.3]（r1=V3文档混配置→已由full_v3取代）|
| C1.full_v3(自探索·正式锚点) | **82.1 ± 3.0%** ✅ 5/5 | [77.8, 86.1, 81.6, 82.3, 82.9]（运维指令(十二)补跑「真full」V3+自探索·r1=77.8%(123/158·timeout=1)·r2=86.1%(136/158·timeout=1)·r3=81.6%(129/158·timeout=4)·r4=82.3%(130/158·timeout=6)·r5=82.9%(131/158·timeout=5)·**未复现r1=88.0%**）|
| C2.phi_k10 | **77.7 ± 2.2%** ✅ 5/5 | [78.5, 76.6, 77.2, 81.0, 75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·timeout=0·att2·r4=128/158·timeout=0·att3·**r5=119/158·timeout=0·75.3%**·PHI-BUDGET-EXHAUSTED=426✅）|
| C2.phi_k3 | **69.1 ± 2.5%** ✅ 5/5 | [72.8, 66.5, 69.6, 69.6, 67.1]（r1=115/158·timeout=0·r2=105/158·timeout=0·r3=110/158·timeout=0·r4=110/158·timeout=2·**r5=106/158·timeout=0·67.1%**·PHI-BUDGET-EXHAUSTED=851✅·25 gen-fail=k=3预算效应·判据(十三)：消融臂Pass@1任何值有效·不重跑）|
| C2.phi_k1 | **63.8 ± 3.2%** ✅ 5/5 | [65.2, 66.5, 58.2, 64.6, 64.6]（r1=103/158·timeout=0·35 gen-fail·r2=105/158·timeout=0·30 gen-fail·r3=92/158·timeout=1·39 gen-fail·r4=102/158·timeout=0·34 gen-fail·**r5=102/158·timeout=0·35 gen-fail=k=1预算效应**·regrade PID3120482·生成状态`{'success':123,'failure':0,'timeout':0,'fail':35}`→**timeout=0≤10✅**·exec_err=0·license/Connection=0✅·PHI-BUDGET-EXHAUSTED=1141>0✅(k=1预算生效)·ACCESS RESTRICTED=827✅·判据(十五④/十三)满足→5/5有效不重跑·**单调k10=77.7>k3=69.1>k1=63.8✅·gen-fail随k↓递增✅**·探路 60.8%）|
| C2.phi_lagged | **73.0 ± 3.2%** ✅ 5/5 | [74.7, 76.6, 69.6, 69.6, 74.7]（r1=118/158·timeout=0·5 gen-fail·PHI-LAGGED=1165✅·r2=121/158·timeout=0·10 gen-fail·r3=110/158·timeout=1·11 gen-fail·r4=110/158·timeout=0·13 gen-fail·**r5=118/158·timeout=0·6 gen-fail·batch=2026_1015_042258·gen{success:152,failure:0,timeout:0,fail:6}·PHI-LAGGED=1244✅·ACCESS RESTRICTED=999✅·PHI-BUDGET-EXHAUSTED=0(lagged无上限合理)·exec_err=0·infra errors=0✅**·判据(十三)满足→5/5有效不重跑·§8.4 trace_key(ctx.session)在位✅·lagged机制(canary PHI-LAGGED=1244命中)✅·Δvs unbounded(82.1)=−9.1pp·Converged(%)=97.5·Mean read-backs/gen-fail=9.0·探路 84.2%，r2 修复后 98.1%）|
| S1.omega_low | **82.8 ± 1.0%** ✅（legacy·采信）| [82.8…]（指令二十二①：legacy std=1.0 可信不重跑）|
| S1.readback_binary | **78.1 ± 1.3%** ✅ 5/5（fresh）| [75.9, 79.1, 77.8, 78.5, 79.1]（fresh 重测·2026-10-15~16·替换 legacy 66.2±16.1% std 过大含 43.0% 离群·运维令二十二②·r1=120/158·r2=125/158·r3=123/158·r4=124/158·r5=125/158·各轮 timeout=13/8/7/6/4·exec_err=0·infra=0✅·判据(十三)有效·单调 N'(73.3)<B(78.1)<F(82.1)✅）|
| S1.readback_none | **73.3 ± 2.2%** ✅（legacy·采信）| [72.2, 70.3, 73.4, 75.9, 74.7]（指令二十二③：legacy std=2.2 可信不重跑）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-17 00:35] 🔎 **巡检（B.deepseek-v4-flash r2 待重跑·token 额度未恢复·不动作退出）**：canary curl POST /v1/chat/completions deepseek-v4-flash key c43c1f4a →**HTTP 429** `本次Token额度已用完，请等待17分钟18秒后重试`（00:35 实测·额度恢复 ~00:53·与23:56估计一致）。**infra 其余全绿**：loop有proxy(https_proxy=http://172.19.92.23:13128✅)·/home=22G(≥8G✅·95%需关注)·4端口8650/8651/8652/8654全OPEN✅·MCP:8090(pid146061)+RAG:9006(pid3503518)LISTEN✅·PID3825276 GONE（旧r2作废进程·无新run_cline_script在跑·pgrep命中=opencode cmdline任务书文本误报）。状态不变 STAGE=B/CONFIG=deepseek-v4-flash/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=1。**下轮**（评测优先）：① canary curl deepseek-v4-flash →若 HTTP 200（额度恢复~00:53后）→ `cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_deepseek-v4-flash_r2.log 2>&1 < /dev/null &` **重跑 r2**（新 batch·覆盖旧作废 batch 2026_1016_232159）→ WAITING=1；若仍 HTTP 429 → 继续等（巡检退出·不动作）。② r2 重跑后收割同 r1 口径（Step7.1 FileNotFoundError=已知 bug→手动 regrade：模板=run_deepseek-v4-flash_r1_regrade.sh 改 batch/GEN_FILE）→判据(十三)（B 模型臂非 full 锚点·Pass@1 任何值有效·不得因<75%重跑·但若再遇 token 额度耗尽 = infra 作废重跑）。⚠️/home=22G 95%若<8G 需暂停清理。📝deepseek-v4-flash 5/5 收口后：替换 zhulong_results.md B.deepseek-v4-flash 行(legacy 16.7±12.3%→fresh mean±std)；运维令(二十六) 之后接 C1.wo_selfexpl 干净 5-run（严格V2·自探索OFF·替换 81.4±4.1%†脚注）。
- [2026-10-16 23:56] ⚠️ **B.deepseek-v4-flash r2 = infra 作废·不计数（token 额度耗尽 HTTP429）→ ERROR_COUNT=1·WAITING=1·待额度恢复~00:52 重跑 r2**：① 巡检 `ps -p 3825276`→**GONE**（r2 code-gen 23:21:59 启动→~23:26 完成仅~4min·远短于 r1 ~7min·异常）·log /tmp/ABL_deepseek-v4-flash_r2.log 910 行 68KB·batch=**2026_1016_232159**·Step0-2 正常·Step3 hook deploy@L21→批量 8 worker@23:22:19。② **gen stats**：**success=0 / failure=158 / timeout=0**（全 158 任务失败）·jsonl 158 行 12166B（均为失败生成）·stats/failure=158。③ **根因**：grep `本次Token额度已用完` = **158 条**（每任务 1 条）·首次@L50(~23:22) `请等待1小时30分钟42秒`·末次@L822 `请等待1小时26分钟51秒`→额度恢复 ~23:26+1h27m ≈ **00:53**。④ **canary curl 确认**：POST /v1/chat/completions deepseek-v4-flash key c43c1f4a → **HTTP 429** `本次Token额度已用完，请等待55分钟54秒后重试`（23:56 实测·与日志一致·额度恢复 ~00:52）。⑤ **判据**：token 额度耗尽 = infra 故障（同 license 耗尽口径·§7 infra 作废规则）·非真实消融效应·**r2 作废·不计数·不 regrade**（success=0 regrade 仅得 infra 污染 0%·非真实结果）·ERROR_COUNT 0→**1**·WAITING=1。⑥ **infra 其余全绿**：4端口8650/8651/8652/8654全OPEN✅·MCP:8090(pid146061)+RAG:9006(pid3503518)LISTEN✅·/home=22G(≥8G✅·95%需关注)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·cline✅·cline auth=openai-compatible deepseek-v4-flash✅（额度耗尽是 gateway 侧限制·非 auth 配置问题·r1 同 key 正常跑通=证）。状态更新 STAGE=B/CONFIG=deepseek-v4-flash/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=1。**下轮**（评测优先）：① canary curl deepseek-v4-flash →若 HTTP 200（额度恢复）→ `cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_deepseek-v4-flash_r2.log 2>&1 < /dev/null &` **重跑 r2**（新 batch·覆盖旧作废 batch）→ WAITING=1；若仍 HTTP 429 → 继续等（巡检退出·不动作）。② r2 重跑后收割同 r1 口径（Step7.1 FileNotFoundError=已知 bug→手动 regrade：模板=run_deepseek-v4-flash_r1_regrade.sh 改 batch/GEN_FILE）→判据(十三)（B 模型臂非 full 锚点·Pass@1 任何值有效·不得因<75%重跑·但若再遇 token 额度耗尽 = infra 作废重跑）。⚠️r1 用了部分额度致 r2 立即撞墙·重跑 r2 前务必 canary 确认额度已恢复。⚠️/home=22G 95%若<8G 需暂停清理。📝deepseek-v4-flash 5/5 收口后：替换 zhulong_results.md B.deepseek-v4-flash 行(legacy 16.7±12.3%→fresh mean±std)；运维令(二十六) 之后接 C1.wo_selfexpl 干净 5-run（严格V2·自探索OFF·替换 81.4±4.1%†脚注）。：① `ps -p 3781234`→**GONE**(r1 code-gen完成@23:19·仅~7min·deepseek-v4-flash弱backbone生成快但失败多)·log /tmp/ABL_deepseek-v4-flash_r1.log·batch=**2026_1016_231244**·`[format_cli_gene_code2jsonl] Done: 24 tasks to jsonl`·gen文件 completed_code_generation_2026_1016_231244.jsonl(77543B·远小于glm-5.3-flash~500KB→弱backbone生成少)·Step7.1 auto-grade FileNotFoundError(已知bug)→手动regrade。② **canary全绿**：ACCESS RESTRICTED=210(r1 code-gen全程·hook live✅)·PHI-BUDGET/LAGGED=0(full锚点 B模型臂无phi预算正确✅)·infra errors(license/Connection/forbidden)=0✅·timeout dir=0✅。③ **regrade启动**：建 run_deepseek-v4-flash_r1_regrade.sh(同glm-5.3-flash r5模板改batch=2026_1016_231244+GEN_FILE·EVAL_FW_DIR+4端口+RAG:9006+SANDBOX_HOST+export PYTHON)→setsid启动→done@23:20:56·Phase2组装13脚本→Phase3 sandbox执行·`1016: 13/158 pass (8.2%) | generated: 13 ok, 145 fail, 0 exec_err`·PASS_RATE=0.0823。④ **判据(十三)核对**：timeout=0≤10✅·exec_err=0✅·infra errors=0✅→**r1 有效（B模型臂非full锚点·Pass@1任何值有效·不得因<75%重跑）**·ERROR_COUNT 保持0·8.2%=弱backbone真实消融效应（与legacy r1=9.5%一致·非infra）。⑤ **r2启动**：`export PYTHON=$PWD/venv/bin/python`→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_deepseek-v4-flash_r2.log 2>&1 < /dev/null &`·**PID3825276**·batch=**2026_1016_232159**·log Step0/1流入✅。状态更新 STAGE=B/CONFIG=deepseek-v4-flash/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：`ps -p 3825276` alive→巡检退出；GONE→读 r2 log 尾段（24→jsonl·Step7.1 FileNotFoundError=已知bug→手动regrade同口径：模板=run_deepseek-v4-flash_r1_regrade.sh 改 batch/GEN_FILE）→**判据(十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r2有效→r3启动(同命令·export PYTHON)。⚠️查r2用`ps -p 3825276`勿用pgrep -f。⚠️/home=22G 95%若<8G需暂停清理。📝deepseek-v4-flash 5/5收口后：替换 zhulong_results.md B.deepseek-v4-flash 行(legacy 16.7±12.3%→fresh mean±std)；运维令(二十六) 之后接 C1.wo_selfexpl 干净 5-run（严格V2·自探索OFF·替换 81.4±4.1%†脚注）。
- [2026-10-16 23:18] [⏩ 已滚出] ✅ B.glm-5.3-flash r5✅收割=61.4% → 5/5收口=66.8±10.5% → 回填 zhulong_results.md → 切 B.deepseek-v4-flash fresh r1 启动 PID3781234@23:12 详情见 daily-memories/2026-10-16.md §[滚出 2026-10-17 00:35]（r1已于23:23收割为8.2%→r2启动，见23:23/23:56条）。
- [2026-10-16 22:36] [⏩ 已滚出] ✅ B.glm-5.3-flash r5 code-gen✅done@21:53 → 手动regrade启动 PID3660682@22:35 详情见 daily-memories/2026-10-16.md §[滚出 2026-10-17 00:35]（已由23:18收割为61.4%→5/5收口→切deepseek-v4-flash r1）。
- [2026-10-16 21:14] [⏩ 已滚出] ✅ B.glm-5.3-flash r4✅收割=65.8% → r5 code-gen 启动 PID3384667@21:14 详情见 daily-memories/2026-10-16.md §[滚出 23:18]（已由22:36推进·r5 regrade→23:18收割为61.4%→5/5收口→切deepseek-v4-flash r1）。
- [2026-10-16 20:36] [⏩ 已滚出] ✅ B.glm-5.3-flash r4 code-gen✅done@20:13 → 手动regrade启动 PID3249224@20:36 详情见 daily-memories/2026-10-16.md §[滚出 23:18]（已由21:14收割为65.8%→r5启动）。
- [2026-10-16 20:00] [⏩ 已滚出] 🔎 巡检（r4 code-gen ~37min健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 23:18]。
- [2026-10-16 19:23] [⏩ 已滚出] ✅ B.glm-5.3-flash r3✅收割=73.4% → r4 code-gen 启动 PID2994878@19:23 详情见 daily-memories/2026-10-16.md §[滚出 23:18]（已由20:36推进→21:14收割为65.8%）。
- [2026-10-16 18:47] [⏩ 已滚出] ✅ B.glm-5.3-flash r3 code-gen✅done@18:42 → 手动regrade启动 PID2886374@18:46 详情见 daily-memories/2026-10-16.md §18:47（已由19:23收割为73.4%→r4启动）。
- [2026-10-16 18:13] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r3 code-gen ~38min健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 18:47]。
- [2026-10-16 17:35] [⏩ 已滚出] ✅ B.glm-5.3-flash r2✅收割=53.2% → r3 code-gen 启动 PID2635004@17:34 详情见 daily-memories/2026-10-16.md §17:35（已由18:47推进·r3 regrade→19:23收割为73.4%→r4启动）。
- [2026-10-16 16:55] [⏩ 已滚出] ✅ B.glm-5.3-flash r2 code-gen✅done@16:26 → 手动regrade启动 PID2460997@16:55 详情见 daily-memories/2026-10-16.md §[滚出 23:18]（已由17:35推进→18:47 r3 regrade→19:23收割为73.4%）。
- [2026-10-16 16:14] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r2 code-gen ~3h34m健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 17:35]。
- [2026-10-16 15:37] 🔎 **巡检（B.glm-5.3-flash r2 code-gen ~2h57m健康·不动作退出）**：ps -p 1253562→alive(etime 02:57:15·STAT Ss·`bash scripts/run_cline_script.sh -p 8 -n`)·log 11.5MB mtime 15:36(live写入)。canary全绿·infra全绿·无pass结果。状态不变。详情见 daily-memories/2026-10-16.md §15:37。
- [2026-10-16 15:01] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r2 code-gen ~2h21m健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 17:35]。
- [2026-10-16 14:24] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r2 code-gen ~1h44m健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 17:35]。
- [2026-10-16 13:48] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r2 code-gen ~1h08m健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 17:35]。
- [2026-10-16 12:40] ✅ **B.glm-5.3-flash r1✅收割=80.4% → r2 code-gen启动 PID1253562@12:40**：① r1 regrade 12:04启动→12:22完成，`/tmp/ABL_glm-5.3-flash_r1_regrade.log` 尾段 `1016: 127/158 pass (80.4%) | generated: 147 ok, 2 fail, 0 exec_err`·gen stats `{'success':147,'failure':0,'timeout':9,'fail':2}`·PASS_RATE=0.8038·pyAether_aether 127/147=0.8639·unknown 0/11(11条=code-gen timeout=9+fail=2 未组装脚本)·执行结果归档 output_evaluation/20261016_1222_app.e0031982/。② 判据(十三)核对：timeout=9≤10✅·exec_err=0✅·无 license/Connection_error/端口宕✅→**r1 有效（消融臂 Pass@1 任何值有效，不得因<75%重跑）**·ERROR_COUNT 保持0。③ infra 全绿：4端口8650/8651/8652/8654@10.129.32.75 全OPEN✅·MCP:8090(HTTP404=alive)+RAG:9006(HTTP404=alive)✅·/home=15G(≥8G✅·97%使用需关注，若<8G需暂停清理)·loop有proxy(https_proxy=http://172.19.92.23:13128✅)·cline✅。④ r2 启动：`export PYTHON=$PWD/venv/bin/python` → `setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_glm-5.3-flash_r2.log 2>&1 < /dev/null &`·**PID1253562**·batch=2026_1016_124025·log 正常 Step0/1/1.5/2 流入✅。状态更新 STAGE=B/CONFIG=glm-5.3-flash/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：`ps -p 1253562` alive→巡检退出；GONE→读 r2 log 尾段（若 Step7.1 auto-grade FileNotFoundError=已知bug→手动regrade同口径：EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1016_124025·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75·export PYTHON=venv/bin/python 防pydantic·模板=run_glm-5.3-flash_r1_regrade.sh 改 batch 即可）→判据(十三)：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r2有效→r3启动(同 r2 命令·export PYTHON)。⚠️查r2用`ps -p 1253562`勿用pgrep -f。⚠️/home=15G 97%若<8G需暂停清理。📝运维令(二十三) 5/5收口后接 B.deepseek-v4-flash fresh 5-run。
- [2026-10-16 12:04] [⏩ 已滚出] ✅ B.glm-5.3-flash r1 code-gen✅done@12:02 → 手动regrade启动 PID1137656@12:04 详情见 daily-memories/2026-10-16.md §12:04（已由12:40收割为80.4%→r2启动）。
- [2026-10-16 11:25] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r1 code-gen ~3h13m健康·不动作退出）详情见 daily-memories/2026-10-16.md §11:25。
- [2026-10-16 10:47] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r1 code-gen ~2h35m健康·不动作退出）详情见 daily-memories/2026-10-16.md §10:47。
- [2026-10-16 10:13] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r1 code-gen ~2h01m健康·不动作退出）详情见 daily-memories/2026-10-16.md §10:13。
- [2026-10-16 09:37] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r1 code-gen ~1h24m健康·不动作退出）详情见 daily-memories/2026-10-16.md §09:37。
- [2026-10-16 09:01] [⏩ 已滚出] 🔎 巡检（B.glm-5.3-flash r1 code-gen ~49min健康·不动作退出）+ 任务书归档减重 详情见 daily-memories/2026-10-16.md §09:01。
- [2026-10-16 08:15] [⏩ 已滚出] ✅ readback_binary r5✅收割=79.1% → 5/5=78.1±1.3% → S1 done_all → 运维令二十三 B.glm-5.3-flash r1 启动 PID148637@08:12·batch=2026_1016_081219 + 论文同步(0 error 12页) 详情见 daily-memories/2026-10-16.md §08:15。
- [2026-10-16 07:23] [⏩ 已滚出] ✅ readback_binary r5 code-gen✅done → 手动regrade启动 PID4178662 详情见 daily-memories/2026-10-16.md §07:23（已由08:15收割为79.1%→5/5收口）。
- [2026-10-16 06:36] [⏩ 已滚出] 🔎 巡检（readback_binary r5 code-gen ~2h16m健康·不动作退出）详情见 daily-memories/2026-10-16.md §06:36。
- [2026-10-16 05:59] [⏩ 已滚出] 🔎 巡检（readback_binary r5 code-gen ~1h40m健康·不动作退出）详情见 daily-memories/2026-10-16.md §05:59。
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
- [2026-10-15 23:36] [⏩ 已滚出] ✅ readback_binary r3✅收割=77.8% → r4 code-gen 启动 PID2574911 详情见 daily-memories/2026-10-16.md §[滚出 23:36]。
- [2026-10-15 23:03] [⏩ 已滚出] ✅ readback_binary r3 code-gen✅done → regrade启动 PID2460802 详情见 daily-memories/2026-10-16.md §[滚出 23:03]。
- [2026-10-15 22:24] [⏩ 已滚出] 🔎 巡检（readback_binary r3 code-gen ~2h55m健康·不动作退出）详情见 daily-memories/2026-10-16.md §[滚出 22:24]。
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
- [2026-10-15 指针块] [⏩ 已滚出] 16 条 10-15(00:10→08:30) 单行指针（phi_lagged r3-r5 收割/巡检/切换·omega_low r1 巡检·运维令二十填results·切S1.readback_binary）已原文搬入 daily-memories/2026-10-15.md §[滚出 18:10→05:02 / 09:36 / 13:59→04:21 / 01:49→00:38]；各条原始详情见对应日期日报 §HH:MM。
- [2026-10-14 指针块] [⏩ 已滚出] 38 条 10-14 单行指针（phi_lagged r1-r3·phi_k1 r1-r5 收割/巡检/切换·运维令十六/十七/十九·论文改进）已原文搬入 daily-memories/2026-10-14.md §[滚出 10-14 指针块]；各条原始详情见 daily-memories/2026-10-14.md §HH:MM。
- [2026-10-12 → 10-13 指针块] [⏩ 已滚出] 82 条 10-12/10-13 单行指针（巡检/收割/切换记录，phi_k10 r1-r5·phi_k3 r1-r5·full_v3 r1-r4·运维令十三/十四/十五）已原文搬入 daily-memories/2026-10-13.md §[滚出 04:21→10-12/10-13 指针块]；各条原始详情见 daily-memories/2026-10-12.md / 2026-10-13.md §HH:MM。

> **[2026-10-04 → 10-11 早期流水]**：已全部原文搬入 `daily-memories/2026-10-{04..11}.md`（各日 §HH:MM）。涉及 B.glm-5.2/flash/kimi/doubao 全 5 轮、C1.pure_llm/rag/wo_retrieval、C1.full(V2) r1-r5、运维指令(一)~(九)、RAG排查报告等。如需查阅见对应日期日报。
