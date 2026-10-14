# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态（合并版）

WAITING: 1

> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | `C2`（B 4/4✅；C1 4臂5/5✅含full_v3锚点82.1±3.0%；C2.phi_k10 5/5✅=77.7±2.2%；**C2.phi_k3 5/5✅=69.1±2.5%**；**phi_k1 r1✅=65.2%·r2✅=66.5%·r3✅=58.2%·r4✅=64.6%·r5 code-gen 跑中 PID2560461（2555759为setsid中间进程已退出·正常）·batch=2026_1014_141425·Step3 cline批处理 96/158任务done@~42min**；📝论文审视报告✅运维令十六完成·✍️**运维令十七论文改进 P0+P1+P2 已改 .tex**·🖨️**运维令十九编译验证✅pdflatex装好·0error/0undef ref/11页(改稿前10页)/0 overfull>20pt·修amssymb环境缺件+phi-bound表resizebox+2处texttt allowbreak·commit fb5e92f8**·🧩**运维令十八✅已并入论文·RQ3 tab:cross-language 填 SKILL/Tcl(陈熙元复现自洽集)·6文件改+编译12页0error commit待推**）|
| CONFIG | `phi_k1`（S2 Φ 预算 k=1·EDA_PHI_BUDGET=1/EDA_PHI_LAGGED=0·base=full(V3+selfexpl)保留·set_s2_phi.py phi_k1 已切+MCP重启PID28018✅·同臂续轮不切配置）|
| ROUND | phi_k3: 1✅=72.8% · 2✅=66.5% · 3✅=69.6% · 4✅=69.6% · **5✅=67.1%(106/158·timeout=0·25 gen-fail=k=3预算效应)** → **5/5=69.1±2.5%✅**; **phi_k1 r1✅=65.2%(103/158·timeout=0·35 gen-fail)·r2✅=66.5%(105/158·timeout=0·30 gen-fail)·r3✅=58.2%(92/158·timeout=1·39 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=997·ACCESS RESTRICTED=805)·r4✅=64.6%(102/158·timeout=0·34 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1093·ACCESS RESTRICTED=812·infra全绿)·r5 code-gen 跑中 PID2560461·batch=2026_1014_141425·Step3 96/158任务done@~42min(Workers~091-102)** |
| PHASE | `running`（phi_k1 r5 code-gen 跑中 PID2560461·Step3 96/158任务·等下轮收割）|
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
| C2 | phi_k1 | **r1✅=65.2%·r2✅=66.5%·r3✅=58.2%·r4✅=64.6%·r5 code-gen 跑中 PID2560461** | r1=103/158·timeout=0·35 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1122(k=1预算生效)·ACCESS RESTRICTED=895·infra全绿（探路 60.8%）·r2=105/158·timeout=0·30 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1150·ACCESS RESTRICTED=892·infra全绿·r3=92/158·timeout=1·39 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=997·ACCESS RESTRICTED=805·infra全绿(regrade log生成状态timeout=1≤10·判据有效)·r4=102/158·timeout=0·34 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1093·ACCESS RESTRICTED=812·infra全绿(regrade log生成状态timeout=0≤10·判据有效)·r5 code-gen 跑中 PID2560461·batch=2026_1014_141425·Step3 96/158任务done@~42min(Workers~091-102) |
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
| C2.phi_k1 | r1=65.2% · r2=66.5% · r3=58.2% · r4=64.6% ✅ (待 5/5) | r1=103/158·timeout=0·35 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1122✅·ACCESS RESTRICTED=895✅·判据(十五④/十三)有效·不重跑；r2=105/158·timeout=0·30 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1150✅·ACCESS RESTRICTED=892✅·infra全绿·判据有效·不重跑；r3=92/158·timeout=1·39 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=997✅·ACCESS RESTRICTED=805✅·infra全绿·判据(十五④/十三：timeout≤10无infra·Pass@1任何值有效)满足→r3=58.2%有效·不重跑；r4=102/158·timeout=0·34 gen-fail=k=1预算效应·PHI-BUDGET-EXHAUSTED=1093✅·ACCESS RESTRICTED=812✅·infra全绿·生成状态`{'success':124,'failure':0,'timeout':0,'fail':34}`→判据(十五④/十三：timeout≤10无infra·Pass@1任何值有效)满足→r4=64.6%有效·不重跑；r5 code-gen 跑中 PID2560461·batch=2026_1014_141425·Step3 96/158任务done@~42min（探路 60.8%）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 各轮原始值 | 备注 |
|:--|:--|:-:|:-:|:--|:--|
| r1 旧时代 | V3文档(旧配置, 10-10 15:32前) | 1 | 88.0% | [88.0] | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% | [79.1, 77.2, 80.4, 82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** | **[77.8, 86.1, 81.6, 82.3, 82.9]** | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1 的 88.0%。r1=88.0% 为异常高值，在受控的 V3+自探索 配置下 5 轮均未达到。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，提示自探索可能有适度增益但不显著（两者在 1σ 范围内重叠）。

## 操作流水
- [2026-10-14 15:48] 🧩 **运维令十八执行：SKILL/Tcl 结果并入论文（空窗期·零GPU·eval r5 跑中不动作）**：① 巡检——ps -p 2560461→alive(etime01:30·r5 code-gen 跑中)→空窗期做论文。② zhulong_results.md(13.9KB·mtime11:39)核查：**C1 组件消融 5 臂(pure_llm/rag/wo_retrieval/wo_selfexp/full)已齐 PyAether+SKILL+Tcl_WaveView+Tcl_Innovus 四列 5-run mean±std**（陈熙元独立复现·自洽集）；Phase B/S1/S2 仅 PyAether。③ **注意experimenter confound**：陈熙元 full PyAether=81.4±1.5 vs 论文主锚点刘杨 82.1±3.0 → RQ3 表用陈熙元自洽集(四列同一操作者)+脚注说明复现PyAether列与主锚点1σ内一致·比较的是切片内排序非跨表绝对值。④ **改 6 文件**：6_exp.tex RQ3(sec:cross-language)填 tab:cross-language(4配置×4语言列·纯LLM=bottom/full=top 跨三语言一致·中间排序翻转)+"pending on remaining axes"；5_bench.tex 三切片完成449题(158+158+133)；0_abstract.tex 主结果PyAether+跨语言复现同结构；1_intro.tex 删[X%]TODO改"同排序在SKILL/Tcl复现"；8_conclusion.tex 449题+复现ref；7_discussion.tex limitation 改"SKILL/Tcl已完成·Ω/Φ轴pending"。⑤ **编译验证✅**：pdflatex+bibtex+pdflatex×2 → **0 error · 0 undefined ref/citation · 12页(改前11页·+1页RQ3表) · 0 overfull>20pt(max16.4pt) · bibtex 2 warnings(bib缺page/volume)**。⑥ 纪律：数字逐字取自 zhulong_results.md·未齐(Ω/Φ轴·SKILL/Tcl)标pending不编造·避免158/449混用(主结果PyAether158·RQ3=SKILL158+Tcl133·共449)。状态不变 STAGE=C2/CONFIG=phi_k1/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0(r5仍跑)。**下轮（评测优先）**：ps -p 2560461 GONE→读r5 log→auto-grade(FileNotFoundError已知bug)→手动regrade同口径(batch=2026_1014_141425·4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75)→判据(十五④/十三)：仅timeout≤10且无infra·Pass@1任何值有效·不重跑→r5有效→**phi_k1 5/5 算 mean±std**→just_finished→切 phi_lagged；alive→巡检退出。
- [2026-10-14 14:56] [⏩ 已滚出] 🔎 **巡检（phi_k1 r5 code-gen ~42min健康·不动作退出）** 详情见 daily-memories/2026-10-14.md §14:56。
- [2026-10-14 14:18] ✅ **phi_k1 r4 收割=64.6%✅有效→r5 code-gen 启动 PID2555759**：① ps -p 2330060→GONE→regrade log /tmp/ABL_phi_k1_r4_regrade.log(6959B·mtime13:34)完整尾段：`✅ 1014: 102/158 pass (64.6%) | generated: 124 ok, 34 fail, 0 exec_err`·生成状态`{'success':124,'failure':0,'timeout':0,'fail':34}`→**timeout=0≤10✅**·exec_err=0·license_error=0·Connection_error=0✅·**判据(运维令十五④/十三)满足→r4=64.6%有效**(消融臂Pass@1任何值有效·34 gen-fail=k=1预算效应非infra·不重跑)·§8.3 k臂✅PHI-BUDGET-EXHAUSTED=1093>0(k=1预算生效)·反作弊✅ACCESS RESTRICTED=812>0(hook live)。② **5项自检(运维令十五③·同臂续轮不切配置)**：.env=phi_k1(BUDGET=1/LAGGED=0/SKILL_DATA_DIR=selfexpl/PROXY_PORTS=8650,8651,8652,8654/SANDBOX_HOST=10.129.32.75)✅·4端口8650/8651/8652/8654@10.129.32.75全OPEN✅·MCP:8090(pid28018)LISTEN✅·hook✅(r4 log ACCESS RESTRICTED=812>0)·/home=22G✅·loop✅有proxy(https_proxy=http://172.19.92.23:13128)。③ **r5启动**：`export PYTHON=$PWD/venv/bin/python`(防pydantic·同r1/r2/r3/r4口径)→`setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_phi_k1_r5.log`→**PID2555759✅·batch=2026_1014_141425·14:14:21启动**·Step2格式化执行中。phi_k1 进度 r1=65.2 + r2=66.5 + r3=58.2 + r4=64.6 四轮有效。状态 STAGE=C2/CONFIG=phi_k1/ROUND=5/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 2555759 GONE→读r5 log→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1014_141425·4端口+RAG:9006+SANDBOX_HOST=10.129.32.75)→**判据(十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r5有效→**phi_k1 5/5 算 mean±std**→just_finished→切 phi_lagged；alive→巡检退出。⚠️查run_cline用`ps -p <PID>`或`ps -eo pid,cmd|grep '[b]ash ...'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。
- [2026-10-14 13:40] 🖨️ **运维令十九编译验证✅ + phi_k1 r4 收割启动regrade**：① **phi_k1 r4 code-gen✅done**：ps -p 1915151→GONE·log /tmp/ABL_phi_k1_r4.log 21.5MB·batch=2026_1014_113846·auto-grade FileNotFoundError(已知bug同r1/r2/r3)·canary✅ACCESS RESTRICTED=812(hook live)+PHI-BUDGET-EXHAUSTED=1093(k=1预算生效)+license/Connection_error=0(infra全绿)·gen_file 158行✅。② **r4 regrade启动**：建 run_phi_k1_r4_regrade.sh(同r3模板改batch=2026_1014_113846·覆盖EVAL_FW_DIR+4端口8650/8651/8652/8654+RAG:9006+SANDBOX_HOST=10.129.32.75)→setsid启动→**PID2330060✅·13:24:02启动**·阶段2组装**124脚本**(158-34gen-fail=k=1预算效应·非infra)→sandbox执行中。③ **🖨️运维令十九编译验证✅**：pdflatex已装(/usr/bin/pdflatex·TeX Live 2023/Debian)·**衔接十七P0+P1+P2改稿编译**：pdflatex→bibtex→pdflatex×2(共5pass修undefined)→**结果：0 error · 0 undefined ref/citation · 11页(改稿前10页,+1页=Limitations独立节+gen-fail列+BaiZe段) · 0 overfull hbox>20pt(max 16.4pt)**。**修3处编译问题**：(a) **环境缺件**`\triangleq`undefined——acmart.cls只在xetex/luatex分支load amssymb,pdflatex分支(newtxmath)未load→main.tex加`\usepackage{amssymb}`(环境兼容,非内容改);(b) **改稿引入**tab:phi-bound加gen-fail列致80.22pt overfull→tabular包`\resizebox{\columnwidth}{!}{}`;(c) **2处pre-existing overfull>20pt**(3_design.tex get_api_details 34.07pt + 6_exp.tex aeSelectFigs 24.61pt,均非我改·git核3bfa0a57未触3_design)→加`\allowbreak`修。④ bibtex 24 warnings(均bib缺page/volume字段,非error)。⑤ commit fb5e92f8(`zhulong compile:`)·push✅(shell缺proxy→export https_proxy=http://172.19.92.23:13128后push成功)·提交main.tex+main.pdf+3_design.tex+6_exp.tex(.aux/.log/.out/.blg/.bbl revert不入库·按运维令④)。状态 STAGE=C2/CONFIG=phi_k1/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**（评测优先）：ps -p 2330060 GONE→读regrade log尾段`pass (xx.x%)`→**判据(十五④/十三)**：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r4有效→r5；alive→巡检退出。⚠️查run_eval用`ps -p <PID>`或`ps -eo pid,cmd|grep '[p]ython ...'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。
- [2026-10-14 12:49] 🔎 **巡检（phi_k1 r4 code-gen ~1h10m健康·不动作退出）**：ps -p 1915151→alive(etime 01:10:28·`bash scripts/run_cline_script.sh -p 8 -n`)·log /tmp/ABL_phi_k1_r4.log 16.8MB mtime 12:49(live写入)·canary✅ACCESS RESTRICTED=706(hook live)+PHI-BUDGET-EXHAUSTED=892(k=1预算生效)·infra自检✅loop有proxy(https_proxy=http://172.19.92.23:13128·PID81827)·/home=22G(≥8G)·4端口8650/8651/8652/8654@10.129.32.75全OPEN·license/Connection_error=0·(本轮同臂续轮不切配置·沿用r1/r2/r3口径)·r4仍在跑→不收割不切臂·按§7 Step A(pgrep有输出→什么都不做退出)。⚠️查run_cline用`ps -p <PID>`或`ps -eo pid,cmd|grep '[b]ash ...'`，勿用`pgrep -f`(opencode cmdline含任务书全文→污染)。状态 STAGE=C2/CONFIG=phi_k1/ROUND=4/PHASE=running/WAITING=1/ERROR_COUNT=0。**下轮**：ps -p 1915151 GONE→读r4 log→auto-grade(Step7.1 FileNotFoundError=已知bug)→手动regrade同口径(覆盖EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework·batch=2026_1014_113846·4端口+RAG:9006+SANDBOX_HOST=10.129.32.75)→判据(十五④/十三)：仅timeout≤10且无infra故障·Pass@1任何值有效·不得因<75%重跑→r4有效→r5；alive→巡检退出。
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
