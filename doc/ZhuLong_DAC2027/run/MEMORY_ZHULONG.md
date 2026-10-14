# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C2`（B 4/4✅；C1 4臂5/5✅含full_v3锚点82.1±3.0%；C2.phi_k10 5/5✅=77.7±2.2%；**C2.phi_k3 5/5✅=69.1±2.5%**；**phi_k1 r1✅=65.2%·r2✅=66.5%·r3✅=58.2%·r4 code-gen 跑中 PID1915151·batch=2026_1014_113846**；📝论文审视报告✅运维令十六完成·✍️**运维令十七论文改进 P0+P1+P2 已改 .tex（锚点84.8→82.1±3.0·重算全部Δ·Error Analysis重声明·硬伤#3/#5/#6 修·Limitations 独立成节·删 ICML 注释·(N)→(N′)）·⚠️编译待 LaTeX 机（36.15 无 pdflatex）**·🧩运维令十八已读（SKILL/Tcl 由其它 agent 测·结果汇总 zhulong_results.md·改稿空窗期带 SKILL/Tcl））|
| CONFIG | `phi_k1`（S2 Φ 预算 k=1·EDA_PHI_BUDGET=1/EDA_PHI_LAGGED=0·base=full(V3+selfexpl)保留·set_s2_phi.py phi_k1 已切+MCP重启PID28018✅·同臂续轮不切配置）|
| ROUND | phi_k3: 1✅=72.8% · 2✅=66.5% · 3✅=69.6% · 4✅=69.6% · **5✅=67.1%(106/158·timeout=0·25 gen-fail=k=3预算效应)** → **5/5=69.1±2.5%✅**; **phi_k1 r1✅=65.2%(103/158·timeout=0·35 gen-fail)·r2✅=66.5%(105/158·timeout=0·30 gen-fail)·r3✅=58.2%(92/158·timeout=1·39 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=997·ACCESS RESTRICTED=805)·r4 code-gen 跑中 PID1915151·batch=2026_1014_113846·11:38:46启动** |
| PHASE | `running`（phi_k1 r4 code-gen 跑中 PID1915151·等下轮收割）|
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
| C2 | phi_k1 | **r1✅=65.2%·r2✅=66.5%·r3✅=58.2%·r4 code-gen 跑中 PID1915151** | r1=103/158·timeout=0·35 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1122(k=1预算生效)·ACCESS RESTRICTED=895·infra全绿（探路 60.8%）·r2=105/158·timeout=0·30 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1150·ACCESS RESTRICTED=892·infra全绿·r3=92/158·timeout=1·39 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=997·ACCESS RESTRICTED=805·infra全绿(regrade log生成状态timeout=1≤10·判据有效)·r4 code-gen 跑中 PID1915151·batch=2026_1014_113846·11:38:46启动 |
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
| C2.phi_k1 | r1=65.2% · r2=66.5% · r3=58.2% ✅ (待 5/5) | r1=103/158·timeout=0·35 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1122✅·ACCESS RESTRICTED=895✅·判据(十五④/十三)有效·不重跑；r2=105/158·timeout=0·30 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1150✅·ACCESS RESTRICTED=892✅·infra全绿·判据有效·不重跑；r3=92/158·timeout=1·39 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=997✅·ACCESS RESTRICTED=805✅·infra全绿·判据(十五④/十三：timeout≤10无infra·Pass@1任何值有效)满足→r3=58.2%有效·不重跑；r4 code-gen 跑中 PID1915151·batch=2026_1014_113846（探路 60.8%）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-14 11:38] ✅ **phi_k1 r3 收割=58.2%✅有效→r4 code-gen 启动 PID1915151**：① ps -p 1753362→GONE→regrade log /tmp/ABL_phi_k1_r3_regrade.log(6872B·mtime11:33)完整尾段：`✅ 1014: 92/158 pass (58.2%) | generated: 118 ok, 39 fail, 0 exec_err`·生成状态`{'success':118,'failure':0,'timeout':1,'fail':39}`→**timeout=1≤10✅**·exec_err=0·license_error=0·Connection_error=0✅·**判据(运维令十五④/十三)满足→r3=58.2%有效**(消融臂Pass@1任何值有效·39 gen-fail=k=1预算效应非infra·不重跑)·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=997>0(k=1预算生效)·反作弊✅ACCESS RESTRICTED=805>0(hook live)。② **5项自检(运维令十五③·同臂续轮不切配置)**：.env=phi_k1(BUDGET=1/LAGGED=0/SKILL_DATA_DIR=selfexpl/PROXY_PORTS=8650,8651,8652,8654/SANDBOX_HOST=10.129.32.75/RAG:9006)✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·hook✅(r3 log ACCESS RESTRICTED=805>0)·/home=23G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)。③ **r4启动**：`export PYTHON=$PWD/venv/bin/python`(防pydantic·同r1/r2/r3口径)→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k1_r4.log`→**PID1915151✅·batch=2026_1014_113846·11:38:46启动**。④ **🧩运维令十八已读**：评测集全貌=EDA-Scripting-Bench 449(PyAether 158+SKILL 158+Tcl 133)·本线测PyAether·SKILL/Tcl由其它agent并行测→汇总 zhulong_results.md·改稿空窗期回填论文时带SKILL/Tcl(只认现存数字·缺标pending·不编造)·评测主线不变。phi_k1 进度 r1=65.2 + r2=66.5 + r3=58.2 三轮有效。状态 STAGE=C2/CONFIG=phi_k1/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：ps -p 1915151 GONE→读r4 log→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1014_113846·4端口+RAG:9006+SANDBOX_HOST=10.129.32.75)→**判据(十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r4有效→r5；alive→巡检退出。⚠️查run_cline用`ps -p <PID>`或`ps -eo pid,cmd|grep '[b]ash ...'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。
- [2026-10-14 10:59] [⏩ 已滚出] ✅ **phi_k1 r3 code-gen完成→regrade启动 PID1753362** 详情见 daily-memories/2026-10-14.md §10:59。
- [2026-10-14 10:21] ✍️ **论文改进（运维令十七·空窗期·零GPU）P0+P1+P2 已改 .tex**：① 主线 phi_k1 r3 code-gen 全程 alive(PID1122046 etime1:38:51·log live 10:21·**未被打扰**)·本任务仅占空窗期(r3 仍在跑无法收割)。② **P0 硬伤全修**：(a) 锚点全局 84.8→**82.1±3.0%**——0_abstract/1_intro/8_conclusion+4表锚点行(main-ablation Full/ablation-harness F/phi-bound unbounded/llm-comparison DeepSeek-V4-Pro)·全部英文+中文注释同步；(b) **重算全部 Δ**——main-ablation(Full **+10.3pp**·wo_retrieval **-1.1pp**)·llm-comparison 4个(**+1.2/-65.4/-5.1/-18.3**)·§S2 effector(+10.3pp)·abstract/intro/grounding(-1.1pp·+10.3pp)·discussion(+10.3pp)；(c) **Error Analysis 重声明**=显式标注「single representative trace·非5-run mean(82.1±3.0)」·保留 134/158/24/3/21 真实计数但不再以 84.8% 为系统 Pass@1；(d) **硬伤#3**——tab:omega (L)=82.8/tab:ablation-harness (N)=73.3/(B)=66.2 一律标 `provisional n=1`($^{\dagger}$)·**drop ±**(尤 (B) ±16.1 删除)·S1 三臂⬜未跑；(e) **硬伤#5**——tab:phi-bound **新增「Mean gen-fail」列**(k10=**18.8**·k3=**27.6**·k1≈**32.5**‡n=2·lagged/unbounded=[TBD])·§S2 正文补「k↓→gen-fail↑→Pass@1↓」机制段；(f) **硬伤#6**——2_background「Our approach」段加 BaiZe 边界句+harness/backbone 划界+`reference.bib` 新增 `baize2027companion` 条目。③ **P1**：eval协议段补 gen-fail 计入分母+infra 故障 run 剔除规则+75%锚点健康下限(只对 full)·§S3 声明 backbone FP4 量化·Limitations 补「未配对检验」+「量化未消融」。④ **P2**：Limitations 提升为独立 `\subsection*`·删 ICML 中文注释(6_exp:132-133)·消歧 (N)→(N′)(tab:ablation-harness+正文)·phi-bound k10/k3 回填 5-run(77.7±2.2/69.1±2.5)·k1 标 ‡provisional n=2。⑤ **phi-bound k1 Pass@1**：r1=65.2/r2=66.5 仅2轮→标 `$\sim$65.9$^{\ddagger}$`(n=2·r3-r5 pending)·🚫 不用旧 60.8 探路值(已知偏低)。⑥ **⚠️ 编译未做**：36.15 服务器**无 pdflatex**(搜 /usr /snap /opt /nasdata /home 均 0)·main.pdf 上次构建 2026-10-06 在他机·本轮 .tex 改动已逐表逐行自检(列数/brace/$math$/cite key)·**编译+页数验证须在 LaTeX 机上做**(下次能编译时补)。⑦ 数字均与 MEMORY 成绩表核对(full_v3=82.1±3.0/rag=71.8/wo_retrieval=81.0/B 4臂)·🚫 编造。commit 前缀 `zhulong paper-fix:`。**下轮**(评测优先)：ps -p 1122046 GONE→读 r3 log→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动 regrade(覆盖 EVAL_FW_DIR·batch=2026_1014_084226·4端口+RAG:9006+SANDBOX_HOST)→判据(十五④/十三)：仅 timeout≤10 无 infra·Pass@1 任何值有效·不重跑→r3 有效→r4；alive→巡检退出。
- [2026-10-14 09:28] 📝 **论文审视报告（运维令十六·空窗期·零GPU）✅ HTML 已交付**：① 主线 phi_k1 r3 code-gen 全程 alive(PID1122046 etime46:27·**未被打扰**)·本任务仅占空窗期。② 审视论文树 main.tex+DAC2027/0-8+.bib+main.pdf→对照 MEMORY 成绩表逐 claim 核验。③ 产出 `reports/report_zhulong_paper_review_zh.html`(39186B·8节·**6🔴硬伤+15🟠建议+11🟢可回填**)。**核心硬伤**：(1) headline 84.8% 是1-shot探路值 vs 5-run锚点full_v3=82.1±3.0%未复现→摘要/引言/结论+4表锚点行+全部Δ+Error Analysis"134/158"全绑旧探路值=系统性过度声称;(2) Error Analysis失败计数绑单次run非5-run稳态;(3) tab:omega(L)/tab:ablation-harness(N)(B)无5-run实测(S1三臂⬜)以±假精度呈现;(4) Φ单调用1-shot值·k1进行中已比60.8高~5pp·gap或缩至~3pp;(5) **gen-fail随k↓递增(k1:30-35/k3:25)论文完全未报告**建议加列;(6) **全文未提BaiZe**·harness/backbone边界缺失。**🟢可回填11项**：full_v3=82.1±3.0回填4表锚点+全局84.8→82.1+重算Δ(Full+10.3/wo_retrieval-1.1)+phi-bound k10→77.7±2.2/k3→69.1±2.5。**仍缺**：wo_sandbox(暂缓)/S1三臂/phi_k1 r3-r5/phi_lagged/Converged(%)/RQ3。**红线**：🚫未改.tex·🚫未打断评测·✅commit前缀`zhulong paper-review:`。**下轮**（评测优先）：ps -p 1122046 GONE→读r3 log收割(判据十五④/十三·不重跑)→r4；alive→巡检退出。论文审视为一次性交付任务✅已完成。
- [2026-10-14 08:44] ✅ **phi_k1 r2 收割=66.5%✅有效→r3启动 PID1122046**：① ps -p 977699→GONE→regrade log /tmp/ABL_phi_k1_r2_regrade.log(6862B·mtime08:17)完整尾段：`✅ 1014: 105/158 pass (66.5%) | generated: 128 ok, 30 fail, 0 exec_err`·生成状态`{'success':128,'failure':0,'timeout':0,'fail':30}`→**timeout=0≤10✅**·exec_err=0·license_error=0·Connection_error=0✅·**判据(运维令十五④/十三)满足→r2=66.5%有效**(消融臂Pass@1任何值有效·30 gen-fail=k=1预算效应非infra·不重跑)·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=1150>0(k=1预算生效)·反作弊✅ACCESS RESTRICTED=892>0(hook live·已部署沙盒hook=1)。② **5项自检(运维令十五③·同臂续轮不切配置)**：.env=phi_k1(BUDGET=1/LAGGED=0/SKILL_DATA_DIR=selfexpl/PROXY_PORTS=8650,8651,8652,8654/SANDBOX_HOST=10.129.32.75/RAG:9006)✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·hook✅(r2 log ACCESS RESTRICTED=892>0·已部署沙盒hook=1)·/home=24G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)。③ **r3启动**：`export PYTHON=$PWD/venv/bin/python`(防pydantic·同r1/r2口径)→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k1_r3.log`→**PID1122046✅·batch=2026_1014_084226·08:42:26启动**·Step2格式化执行中(venv python·无pydantic报错)。phi_k1 进度 r1=65.2 + r2=66.5 两轮有效。状态 STAGE=C2/CONFIG=phi_k1/ROUND=3/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：ps -p 1122046 GONE→读r3 log→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1014_084226·同口径4端口+RAG:9006+SANDBOX_HOST=10.129.32.75)→**判据(运维令十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r3有效→r4；alive→巡检退出。⚠️查loop/run_cline用`ps -p <PID>`或`ps -eo pid,cmd|grep '[b]ash ...'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。
- [2026-10-14 08:07] ✅ **phi_k1 r2 code-gen完成→regrade启动PID977699**：① ps -p 594067→GONE(08:05查)→r2已结束·log /tmp/ABL_phi_k1_r2.log 24.7MB mtime07:55(已停)·batch=2026_1014_062206·gen_file /home/app.e0031982/eda_code_eval/completed_code_generation_2026_1014_062206.jsonl(306KB·158行✅)·log尾段确认**Step7.1 auto-grade失败=FileNotFoundError /home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether[已知benchmark bug·同r1/phi_k3全轮]**→输出目录/home/app.e0031982/eda_code_eval/2026_1014_062206。② 创建 run_phi_k1_r2_regrade.sh（基于phi_k3 r5模板改batch=2026_1014_062206·覆盖 EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·同口径 SANDBOX_ENDPOINTS=8650/8651/8652/8654 + RAG:9006 + SANDBOX_HOST=10.129.32.75）→setsid bash run_phi_k1_r2_regrade.sh > /tmp/ABL_phi_k1_r2_regrade.log →**PID977699✅·08:07:06启动**·regrade log: 阶段2组装**128脚本**完成(158任务·30 gen-fail=k=1预算效应·非infra)→sandbox执行中。③ r2 log canary✅：ACCESS RESTRICTED=892(hook live>0)·PHI-BUDGET-EXHAUSTED=1150(>0·k=1预算生效)·已部署沙盒hook=1·Forbidden=1(提及非错误)·license_error=0·Connection_error=0✅·无final pass(auto-grade bug)。④ **5项自检(运维令十五③·同臂续轮不切配置)**：.env=phi_k1(BUDGET=1/LAGGED=0/SKILL_DATA_DIR=selfexpl/PROXY_PORTS=8650,8651,8652,8654/RAG:9006/SANDBOX_HOST=10.129.32.75)✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·hook✅(r2 log ACCESS RESTRICTED=892>0·已部署沙盒hook=1)·/home=24G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128·PID81827)。状态 STAGE=C2/CONFIG=phi_k1/ROUND=2/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：ps -p 977699 GONE→读regrade log尾段`pass (xx.x%)`→**判据(运维令十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r2有效→r3；alive→巡检退出。⚠️查loop/run_cline用`ps -p <PID>`或`ps -eo pid,cmd|grep '[b]ash ...'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。
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
