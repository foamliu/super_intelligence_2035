# ZhuLong 试验原始分数汇总



> 评测集：EDA\-Scripting\-Bench，指标 Pass@1（%），每臂 N=5 轮。
> 
> 主干 LLM：DeepSeek\-V4\-Pro（C1\.full 锚点）。
> 
> 反作弊 hook 全程生效。
> 
> 知识库 V3，默认自探索 ON
> 
> 



## 评测工具环境（Harness：pyAether MCP Server）

> 本文所有试验统一通过 MCP 工具层驱动 agent 的「检索 \+ 沙盒」闭环。ZhuLong harness 暴露的正是消融实验中反复出现的「核心 4 工具」，其真实签名与回读字段如下。
> 
> 



### 核心 4 工具

|工具|功能|关键参数|对应消融 / 论文表|
|---|---|---|---|
|`search_apis`|语义相似度（向量嵌入）检索 API，自动合并 BM25 描述补充|`query` / `lang` / `host` / `top_k` / `similarity_threshold`|Ω 文档保真度（high/low）|
|`search_apis_by_keyword`|关键词匹配（camelCase 片段 \+ BM25）检索，适合缩写查询|`query` / `lang` / `host` / `top_k`|Ω 文档保真度|
|`get_api_details`|获取指定 API 详情（描述 / 类型 / 属性 / 继承关系）|`api_list` / `lang` / `host`|Ω 文档保真度|
|`run_code`|在远程 EDA 沙盒执行代码并回读结果|`code` / `lang` / `host` / `probe` / `encoding`|readback 三档；Φ 预算轴|

> 检索 3 件套（`search_apis` / `search_apis_by_keyword` / `get_api_details`）的 `lang` 取值 `pyAether` / `skill` / `tcl`，`host` 取值 `aether` / `virtuoso` / `waveview` / `innovus`，据此限定 API 命名空间。
> 
> 



### `run_code` 的 4 种运行时组合

|`lang`|`host`|运行时|典型用途|
|---|---|---|---|
|`pyAether`|`aether`|Python \+ SWIG（pyAether 脚本）|主导语言（评测主列）|
|`skill`|`virtuoso`|SKILL 解释器（Cadence Virtuoso）|SKILL 任务|
|`tcl`|`waveview`|Synopsys Custom WaveView ACE 批处理|波形 / `sx_version` / `plot` / `v_show`|
|`tcl`|`innovus`|Innovus P\&R 命令运行时|设计 / 数据库（`get_db` / `get_nets` 等）|



### `run_code` 回读字段（对应 readback 消融）

> `run_code` 返回四字段：`response`（主状态）、`error_log`（完整错误 / 异常栈，成功为空）、`print_log`（stdout 捕获）、`result`（SKILL 表达式返回值 / Tcl 最后命令返回值；pyAether 恒为空串）。
> 
> 
> 
> - **readback=full**（F 档）：四字段全回读。
> 
> - **readback=binary**（B 档，`EDA_MCP_RUN_CODE_FEEDBACK=binary`）：四字段坍缩为二元 `PASS` / `FAIL`。
> 
> - **readback=none**（N 档）：无任何回读。
> 
> 





## 总览



### Phase B：大模型消融（5 臂 × 5 轮 = 25 轮）



* [x] **B\.glm\-5\.2** — **83\.3 ± 3\.1%** ✅ 5/5

* [x] **B\.deepseek\-v4\-flash** — **16\.7 ± 12\.3%** ✅ 5/5

* [x] **B\.kimi\-k2\.6\-cloud** — **77\.0 ± 1\.6%** ✅ 5/5

* [x] **B\.doubao\-seed\-2\.0\-pro\-cloud** — **63\.8 ± 1\.4%** ✅ 5/5

* [x] **B\.glm\-5\.3\-flash** — **66\.8 ± 10\.5%** ✅ 5/5

    

### C1：组件消融（5 臂 × 5 轮 = 25 轮）



* [x] **C1\.pure\_llm** — **10\.5 ± 1\.9%** ✅ 5/5（复用 legacy）

* [x] **C1\.rag** — **71\.8 ± 2\.5%** ✅ 5/5

* [x] **C1\.wo\_retrieval** — **81\.0 ± 4\.5%** ✅ 5/5

* [x] **C1\.wo\_selfexp**（V2 自探索 OFF）— 刘杨 **81\.4 ± 4\.1%**（旧 r1=V3文档混配置·已标†脚注） · 陈熙元 **77\.3 ± 2\.9%** ✅ 5/5（作为对照参考，运维令二十七①）· **刘杨 V2 干净 r1 = 83.5%（132/158·2026-10-17·运维令二十六②·batch 2026_1017_055109·gen 147 ok/6 fail/0 exec_err·PASS_RATE=0.8980·判据(十三)有效·n=1 与陈熙元 77.3±2.9% 同量级·确认 V2 baseline，r2-r5 不再跑）**

* [x] **C1\.full**（V3 自探索 ON · 锚点）— 刘杨 **82\.1 ± 3\.0%** · 陈熙元 **81\.4 ± 1\.5%** ✅ 5/5

    > 📌 **论文统一口径（2026-10-18 用户裁定）**：主表、跨语言表、回读表、结论一律采用 **陈熙元 81.4 ± 1.5%**（明细 5-run `[82.9, 81.0, 81.6, 79.1, 82.3]`）；刘杨 82.1 ± 3.0% 为另一套 run，**不用于论文**。相关 Δ：RAG 72.2 → **+9.2 pp**；w/o Retrieval 81.0 → **−0.4 pp**；GLM-5.2 83.3 → **+1.9 pp**。

    

### S1：保真度消融（3 臂 × 5 轮 = 15 轮，legacy）



* [x] **S1\.omega\_low**（Ω L）— **82\.8 ± 1\.0%** ✅ 5/5（legacy）

* [x] **S1\.readback\_binary**（B）— **78\.1 ± 1\.3%** ✅ 5/5（fresh 重测·2026-10-15~16·替换 legacy 66\.2 ± 16\.1% std 过大含 43\.0% 离群·运维令二十二②）

* [x] **S1\.readback\_none**（N）— **73\.3 ± 2\.2%** ✅ 5/5（legacy）

    

### S2：Φ 预算轴消融（4 臂 × 5 轮 = 20 轮）



* [x] **S2\.phi\_k10** — 刘杨 **77\.7 ± 2\.2%** ✅ 5/5（探路 75\.3%）

* [x] **S2\.phi\_k3** — **69\.1 ± 2\.5%** ✅ 5/5（探路 69\.0%）

* [x] **S2\.phi\_k1** — **63\.8 ± 3\.2%** ✅ 5/5（探路 60\.8%）

* [x] **S2\.phi\_lagged** — **73\.0 ± 3\.2%** ✅ 5/5（探路 84\.2%）





## Phase B：大模型消融（固定 ZhuLong 框架，换 LLM）

> **试验目标**：验证 ZhuLong 框架对不同 LLM backbone 的泛化能力。固定完整框架（检索 \+ 沙盒 \+ 自探索 ON），仅替换底层 LLM，观察 Pass@1 在不同模型间的分布与排序，回答"框架的性能增益是否依赖特定 backbone"。
> 
> 



### B\.glm\-5\.2（GLM\-5\.2）

编排模型自身作为 eval backbone，验证框架在中等能力模型上的基线表现。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|84\.2||||
|r2|87\.3||||
|r3|84\.2||||
|r4|79\.1||||
|r5|81\.6||||
|**mean±std**|**83\.3 ± 3\.1%**||||



### B\.deepseek\-v4\-flash（DeepSeek\-V4 Flash）

DeepSeek 系列轻量模型，验证小参数量 backbone 能否驱动框架。

**复测 5-run（运维令二十七②·2026-10-18 收口·trace 诊断修复后）**

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|60\.1||||
|r2|57\.0||||
|r3|62\.7||||
|r4|67\.7||||
|r5|53\.2||||
|**mean±std**|**60\.1 ± 5\.5%**||||

> 备注：复测 5/5 = [60\.1, 57\.0, 62\.7, 67\.7, 53\.2]（运维令二十七②·2026-10-17~18·trace 诊断修复：并行度 8→4 + maxTokens 8192→16384 in providers\.json·r3 起用 16384·V3 自探索 ON + full harness）。各轮 gen success=108/110/117/126/92、timeout=0≤10、exec_err=0、0 quota error（r3-r5）/0 infra 故障，判据(十三)满足。**vs fresh 11\.9±2\.7% → +48\.2pp**，证实 fresh 5-run 低分主要由 infra 问题（gateway 并发限流 45% 0-token 失败 + reasoning-token 预算耗尽 28% null-content）导致，非模型能力。r5 gen-success=92 低于 r1-r4（108/110/117/126），致 r5=53\.2% 为 5 轮最低，但 timeout=0 仍判据十三有效。各轮 regrade log /tmp/ABL_deepseek-v4-flash_retest_r{1..5}_regrade\.log，归档 /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/2026101{7,8}_*\_app\.e0031982/。backbone=deepseek-v4-flash@/v1 key c43c1f4a（主基座 deepseek-v4-pro-fp4 不变）。

**fresh 5-run（运维令二十三②·2026-10-17 收口·已被复测取代·保留作历史对照）**

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|8\.2||||
|r2|15\.2||||
|r3|10\.8||||
|r4|13\.9||||
|r5|11\.4||||
|**mean±std**|**11\.9 ± 2\.7%**（已被复测 60\.1±5\.5% 取代）||||

> 备注：fresh 5-run（运维令二十三②·2026-10-17 收口）替换 legacy 16\.7 ± 12\.3% [9\.5, 10\.1, 19\.0, 7\.6, 37\.3]——legacy r5=37\.3 为离群高值致 std=12\.3 过大。fresh 5/5 = [8\.2, 15\.2, 10\.8, 13\.9, 11\.4] 各轮 gen success=13/31/17/24/28、timeout=0≤10、exec_err=0、0 quota error、0 infra 故障，判据(十三)满足（B 模型臂非 full 锚点·Pass@1 任何值有效）。std 12\.3→2\.7（离群消除），mean 16\.7→11\.9（legacy 均值被 r5=37\.3 抬高）。**⚠️ 2026-10-17 运维令二十七① trace 诊断发现 fresh 11\.9% 低分 73% 为 infra 问题（45% 0-token gateway 限流 + 28% null-content reasoning 预算耗尽）·复测 60\.1±5\.5% 已取代本值用于论文 tab:llm-comparison**。各轮 regrade log /tmp/ABL_deepseek-v4-flash_r{1..5}_regrade.log。backbone=deepseek-v4-flash@/v1 key c43c1f4a（主基座 deepseek-v4-pro-fp4 不变）。
> 
> 



### B\.kimi\-k2\.6\-cloud（Kimi\-K2\.6 Cloud）

Kimi 系列云端模型，测试框架对非 DeepSeek 系模型的兼容性与跨厂商泛化。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|79\.1||||
|r2|76\.6||||
|r3|77\.2||||
|r4|74\.7||||
|r5|77\.2||||
|**mean±stdpretr**|**77\.0 ± 1\.6%**||||





### B\.doubao\-seed\-2\.0\-pro\-cloud（Doubao\-Seed\-2\.0\-Pro Cloud）

豆包系列云端模型，进一步验证跨厂商泛化能力。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|63\.9||||
|r2|64\.6||||
|r3|61\.4||||
|r4|65\.2||||
|r5|63\.9||||
|**mean±std**|**63\.8 ± 1\.4%**||||





### B\.glm\-5\.3\-flash（GLM\-5\.3 Flash）

GLM 新一代轻量模型，验证框架对 GLM 系轻量 backbone 的兼容性（运维令二十三新臂）。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|80.4||||
|r2|53.2||||
|r3|73.4||||
|r4|65.8||||
|r5|61.4||||
|**mean±std**|**66.8 ± 10.5%**||||
 
> 备注（fresh 5-run·历史对照·运维令二十三②·2026-10-16 收口）：r1=80.4 偏高、r2=53.2 偏低，5 轮 std=10.5 较大（轻量 backbone 高方差），但 5/5 各轮 timeout≤10（r1=9/r2=6/r3=0/r4=0/r5=0）且无 infra 故障、exec_err=0、判据(十三)满足，结果有效。glm-5.3-flash@/v1 key 6903b05e。

**复测 5-run（运维令三十一·2026-10-19 收口·-p 4 起步·infra 干净重测·std 大幅收窄）**

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|86.1||||
|r2|84.8||||
|r3|89.2||||
|r4|87.3||||
|r5|86.7||||
|**mean±std**|**86.8 ± 1.6%**||||
 
> 备注（复测 5-run·运维令三十一·2026-10-18~19·-p 4 起步·fresh 5/5 = [86.1, 84.8, 89.2, 87.3, 86.7]·各轮均判据十三 timeout=0≤10 有效·gen success=157/158/157/156/157、gen-fail=1/0/1/2/0、0 timeout、0 exec_err、0 infra 故障）。**vs fresh 5-run 66.8±10.5% → +20.0pp**，且 **std 从 10.5 → 1.6 大幅收窄**（远低于目标 <8）。复测 4 轮稳定在 85–89% 区间，r3=89.2% 最高、r2=84.8% 最低，5/5 全部高于 fresh 最高单轮 r1=80.4%。证实 fresh 5-run 的低分与高方差主要由 infra 因素（gateway 并发限流 / -p 8 致 r1 两次作废 0/158 与 89% 失败率飙升）导致，非模型真实能力；-p 4 起步后 infra 干净，模型真实表现显著回升且稳定。各轮 regrade log /tmp/ABL_glm-5.3-flash_retest_r{1..5}_regrade.log（Step 7.1 auto-grade 已知 FileNotFoundError → 手动 regrade，模板同 r1，改 batch + GEN_FILE；unset proxy + NO_PROXY=10.129.32.75 + EVAL_FW_DIR=/nasdata/.../EDA-Eval-Framework）。配置=full harness + V3 自探索 ON + glm-5.3-flash@/v1 key 6903b05e + maxTokens=16384 in providers.json（reasoning.enabled=false·glm-5.3-flash 非推理模型）+ cline 3.0.51（baseline 未动 ✅）+ 4 端口 8650/8651/8652/8654@10.129.32.75。复测取代 fresh 进入论文 `tab:llm-comparison`。
 
 
 
---



## C1：组件消融（固定 LLM=DeepSeek\-V4\-Pro，逐组件开关）

> **试验目标**：量化 ZhuLong 各核心组件对系统性能的边际贡献。固定 LLM backbone（DeepSeek\-V4\-Pro），逐个关闭检索、沙盒、自探索等组件，与完整系统对比，定位关键贡献来源。对应论文 `tab:main-ablation`。
> 
> 



### C1\.pure\_llm（纯 LLM，核心 4 工具全关）

> 关闭全部 4 个核心工具（`search_apis` / `get_api_details` / `run_code` / `search_apis_by_keyword`），agent 仅靠 LLM 内置知识 $\mathcal{K}$ 生成代码，无法从环境获取任何观测。作为消融基线，量化"无观测"条件下的能力下限。
> 
> 



|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|8\.2|35\.0|3\.9|15\.8|
|r2|9\.5|33\.8|2\.6|24\.6|
|r3|10\.1|29\.3|1\.3|21\.1|
|r4|11\.4|34\.4|3\.9|19\.3|
|r5|13\.3|33\.8|2\.6|19\.3|
|**mean±std**|**10\.5 ± 1\.9%**|**33\.2 ± 2\.3%**|**2\.9 ± 1\.1%**|**20\.0 ± 3\.2%**|



### C1\.rag（仅检索、关 sandbox）

> 仅保留检索工具（`search_apis` / `get_api_details` / `search_apis_by_keyword`），关闭沙盒执行（`run_code`）。agent 可查 API 文档但无法运行代码验证，检验"只读不练"的性能。对应论文 `tab:omega` 的 \(N\) 档（纯 RAG baseline）。
> 
> 



V3，自探索 ON

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|72\.2|52\.9|87\.0|87\.7|
|r2|72\.2|29\.3|81\.8|86\.0|
|r3|72\.8|29\.3|88\.3|82\.5|
|r4|74\.1|28\.0|89\.6|75\.4|
|r5|69\.6|29\.9|88\.3|75\.4|
|**mean±std**|**72\.2% ± 1\.6**|**33\.9% ± 10\.6**|**87\.0% ± 3\.0**|**81\.4% ± 5\.8**|



### C1\.wo\_retrieval（仅 sandbox、关检索 3 件套）

> 仅保留沙盒执行（`run_code`），关闭检索 3 件套（`search_apis` / `get_api_details` / `search_apis_by_keyword`）。agent 可运行代码但无法查文档，检验"只练不查"的性能。
> 
> 



|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|74\.1|56\.1|80\.5|86\.0|
|r2|86\.1|49\.0|76\.6|63\.2|
|r3|81\.6|29\.3|85\.7|1\.8|
|r4|79\.7|30\.6|83\.1|78\.9|
|r5|83\.5|29\.9|81\.8|78\.9|
|**mean±std**|**81\.0 ± 4\.5%**|**39\.0 ± 12\.6%**|**81\.6 ± 3\.4%**|**61\.8 ± 34\.6%**|



### C1\.wo\_selfexp（使用未自探索增强文档）

> 使用未经自探索增强的原始 V2 文档（自探索 OFF），其余组件全开。与 C1\.full 对比，量化离线自探索对 API 文档质量的增益。
> 
> 



V2，自探索 OFF

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|79\.1|61\.8|84\.4|80\.7|
|r2|80\.4|60\.5|85\.7|66\.7|
|r3|77\.8|62\.4|88\.3|66\.7|
|r4|76\.6|61\.8|85\.7|86\.0|
|r5|72\.8|61\.1|85\.7|61\.4|
|**mean±std**|**77\.3** ± 2\.9|**61\.5** ± 0\.7|**86\.0** ± 1\.4|**72\.3** ± 10\.5|
||||||



### C1\.full（完整系统，锚点）

> 完整系统（V3 自探索 ON \+ 检索 \+ 沙盒），所有组件开启。作为所有消融的锚点，其 5\-run 结果复用于 `tab:main-ablation`\(full\) \+ `tab:omega`\(H\) \+ `tab:ablation-harness`\(F\) \+ `tab:phi-bound`\(unbounded\) \+ `tab:llm-comparison`\(主基座\) 五张表。
> 
> 



V3，自探索 ON

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|82\.9|66\.2|89\.6|63\.2|
|r2|81\.0|64\.3|90\.9|75\.4|
|r3|81\.6|64\.3|85\.7|93\.0|
|r4|79\.1|55\.4|87\.0|93\.0|
|r5|82\.3|51\.0|87\.0|93\.0|
|**mean±std**|**81\.4% ± 1\.5**|**60\.3% ± 6\.7**|**88\.6% ± 2\.1**|**85\.3% ± 15\.4**|

> 备注：SKILL语言相较于未使用增强文档通过率变低，可能要重测。
> 
> 



---



## S1：保真度消融（固定 LLM=DeepSeek\-V4\-Pro，逐保真度轴开关）

> **试验目标**：检验观测通道 $\Omega$ 的信息保真度对 agent 性能的影响。分别降低文档检索保真度（$\Omega$ low）和回读保真度（readback binary/none），验证"观测质量越高，信念更新越准确"的假设。对应论文 `tab:omega` 与 `tab:ablation-harness`。
> 
> 



### S1\.omega\_low（Ω 文档保真度=low，核心 4 工具全开 \+ readback=full）

> 将检索索引降级为低保真度（仅 API 名 \+ 相似度，无描述/BM25/同义词展开），其余全开。与 C1\.full（$\Omega$=high）对比，量化文档检索质量对性能的影响。对应论文 `tab:omega` 的 \(L\) 档。
> 
> 



|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|81\.6||||
|r2|82\.3||||
|r3|84\.2||||
|r4|82\.9||||
|r5|82\.9||||
|**mean±std**|**82\.8 ± 1\.0%**||||



### S1\.readback\_binary（readback=binary，Ω=high）

> 沙盒执行后仅返回 pass/fail（二元回读），不返回 stdout/异常栈/逐断言结果。agent 知道代码是否通过但不知道错在哪。对应论文 `tab:ablation-harness` 的 \(B\) 档。
> 
> **成本 5-run（2026-10-18 零 GPU 从保留 trace 提取，运维令三十②/PLAN_RETEST_READBACK_COST §5）**：从 `~/eda_code_eval/{2026_1015_093317,2026_1015_143848,2026_1015_193004,2026_1015_233638,2026_1016_041955}/trace/<task>/` 解析 5 轮 fresh batch 的逐 trace 指标，替换论文 `tab:readback-cost` (B) 行的 n=1 值（27.6 / 4.25 / 13）。
> 
> | 指标 | r1 | r2 | r3 | r4 | r5 | **5-run mean ± std** | 旧 n=1 |
> |:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
> | Pass@1 (%) | 75.9 | 79.1 | 77.8 | 78.5 | 79.1 | **78.1 ± 1.3** | 78.1 ± 1.3 |
> | Mean read-backs (run\_code/task) | 27.57 | 19.13 | 20.35 | 23.13 | 21.44 | **22.3 ± 3.3** | 27.6 |
> | Wall-clock per task (s) | 692.3 | 581.2 | 567.1 | 576.9 | 475.4 | **578.6 ± 77.0** (9.64 min) | — |
> | Batch real-elapsed (h, parallel) | 4.33 | 3.80 | 3.25 | 4.49 | 2.79 | **3.73 ± 0.72** | 4.25 |
> | Timeout count | 13 | 8 | 7 | 6 | 4 | **7.6 ± 3.4** | 13 |
> | Converged (%) | 96.8 | 97.5 | 98.1 | 94.9 | 96.2 | **96.7 ± 1.2** | — |
> | Gen-fail count | 1 | 0 | 0 | 0 | 0 | **0.2 ± 0.4** | — |
> | Max run\_code on one task | 287 (t118) | 225 (t131) | 201 (t118) | 299 (t147) | 265 (t105) | max=299 | 287 |
> | Input tokens mean | 1.86M | 1.33M | 1.30M | 1.60M | 1.40M | **1.50M ± 0.24M** | — |
> | Output tokens mean | 35340 | 30425 | 32182 | 34438 | 30380 | **32553 ± 2275** | — |
> 
> 提取脚本：`run/extract_readback_binary_cost_5run.py`；JSON：`run/readback_binary_cost_5run.json`。
> 论文已 sync：`tab:readback-cost` (B) 行 → `22.3 ± 3.3 / 3.73 ± 0.72 / 7.6 ± 3.4`（5-run，去掉 ‡脚注）；`tab:ablation-harness` (B) Mean read-backs → 22.3（5-run 均值）；正文比例更新为 1.8×/1.7×/2.2×（原 2.3×/1.9×/3.8×）；编译 13 页 0 error。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|75\.9||||
|r2|79\.1||||
|r3|77\.8||||
|r4|78\.5||||
|r5|79\.1||||
|**mean±std**|**78\.1 ± 1\.3%**（fresh·2026-10-15~16·替换 legacy 66\.2 ± 16\.1%·运维令二十二②）||||



### S1\.readback\_none（readback=none，Ω=high）

> 沙盒执行后无任何返回（仅"已执行"），agent 不知道代码是否通过。检验"完全无回读"条件下 agent 能否仅凭先验信念完成任务。对应论文 `tab:ablation-harness` 的 \(N\) 档。
> 
> 



|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|72\.2||||
|r2|70\.3||||
|r3|73\.4||||
|r4|75\.9||||
|r5|74\.7||||
|**mean±std**|**73\.3 ± 2\.2%**||||





---



## S2：Φ 预算轴消融（固定 LLM=DeepSeek\-V4\-Pro，限 run\_code 调用预算）

> **试验目标**：检验信念更新 $\Phi$ 的更新率与证据预算对 agent 收敛的影响。通过限制 `run_code` 调用次数（$k$=1/3/10）和引入回读滞后（lagged），验证"$\Phi$ 的更新率必须超过 L4 动态的时间尺度"这一原则。对应论文 `tab:phi-bound`。预算约束的是"能执行/能观测多少次"，**不是**"何时提交"——超限后 PreToolUse hook 拒绝调用，agent 收到 error 后继续自主运行。
> 
> 



### S2\.phi\_k10（k=10，run\_code 调用上限 10 次/trace）

> 限制 agent 每条 trace 最多调用 `run_code` 10 次，超限后 PreToolUse hook 拒绝调用（返回 `[PHI-BUDGET-EXHAUSTED]`）。检验中等证据预算下 agent 的收敛行为。需同步报告 `Converged (%)` 以区分"被切断"与"更新失效"。
> 
> 

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|78\.5||||
|r2|76\.6||||
|r3|77\.2||||
|r4|81\.0||||
|r5|75\.3||||
|**mean±std**|**77\.7 ± 2\.2%**||||
|**Converged (%)**|**90.4**（5-run: [89.2, 90.5, 91.1, 91.1, 89.9]）||||
|**Mean gen-fail**|**17.4**（5-run: [16, 15, 21, 16, 19]）||||



### S2\.phi\_k3（k=3，run\_code 调用上限 3 次/trace）

> 限制 `run_code` 调用上限为 3 次，检验紧预算下 agent 能否在极少迭代中收敛。
> 
> 

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|72\.8||||
|r2|66\.5||||
|r3|69\.6||||
|r4|69\.6||||
|r5|67\.1||||
|**mean±std**|**69\.1 ± 2\.5%**||||
|**Converged (%)**|**80.4**（5-run: [81.6, 79.7, 77.2, 81.6, 81.6]）||||
|**Mean gen-fail**|**27.6**（5-run: [27, 31, 32, 23, 25]）||||





### S2\.phi\_k1（k=1，run\_code 调用上限 1 次/trace）

> 限制 `run_code` 调用上限为 1 次，检验极端紧预算下的性能下限与 agent 终止行为。
> 
> 

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|65\.2||||
|r2|66\.5||||
|r3|58\.2||||
|r4|64\.6||||
|r5|64\.6||||
|**mean±std**|**63\.8 ± 3\.2%**||||
|**Converged (%)**|**76.3**（5-run: [77.2, 77.2, 75.9, 75.9, 75.3]）||||
|**Mean gen-fail**|**34.6**（5-run: [35, 30, 39, 34, 35]）||||

> 各轮明细分：r1=103/158·35 gen\-fail·r2=105/158·30 gen\-fail·r3=92/158·39 gen\-fail·r4=102/158·34 gen\-fail·r5=102/158·35 gen\-fail（gen\-fail 随 k↓ 递增，k=1 预算效应非 infra）。PHI\-BUDGET\-EXHAUSTED=1141>0✅（k=1 预算生效）。单调 k10=77\.7>k3=69\.1>k1=63\.8✅。





### S2\.phi\_lagged（lag=1，回读滞后 1 次执行）

> 回读滞后 1 次执行——第 $n$ 次调用返回第 $n{-}1$ 次执行的状态，agent 始终基于过时观测决策（闭环被系统性地切掉一步）。检验"$\Phi$ 更新率必须超过 L4 动态时间尺度"这一原则。$k$ 轴变的是证据的**量**，lagged 变的是证据的**时效**，二者是不可互相替代的不同失效模式。
> 
> 

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|74\.7||||
|r2|76\.6||||
|r3|69\.6||||
|r4|69\.6||||
|r5|74\.7||||
|**mean±std**|**73\.0 ± 3\.2%**||||
|**Converged (%)**|**97.5**（5-run: [97.5, 98.7, 97.5, 94.9, 98.7]）||||
|**Mean gen-fail**|**9.0**（5-run: [5, 10, 11, 13, 6]）||||

> 各轮明细分：r1=118/158·5 gen\-fail·r2=121/158·10 gen\-fail·r3=110/158·11 gen\-fail·r4=110/158·13 gen\-fail·r5=118/158·6 gen\-fail（gen\-fail=lagged 缓冲效应，非 infra）。PHI\-LAGGED 命中✅（lagged 机制生效），PHI\-BUDGET\-EXHAUSTED=0（lagged 无上限，合理）。Δvs unbounded(82\.1)=−9\.1pp。lagged 介于 k3(69\.1) 与 k10(77\.7) 之间。



> **注**：S2 四臂（phi\_k10 / phi\_k3 / phi\_k1 / phi\_lagged）均已 5/5 收口，可填论文 `tab:phi-bound` 的 mean±std。单调性 k10=77\.7>k3=69\.1>k1=63\.8✅；lagged=73\.0 介于 k3 与 k10 之间✅。gen\-fail 随 k↓ 递增（k=1 预算效应），与「k↓ → gen\-fail↑ → Pass@1↓」一致。Converged (%) 随 k↓ 递降（k10=90.4 > k3=80.4 > k1=76.3），unbounded=99.1，lagged=97.5（无预算上限→高收敛）。
>
> **unbounded（full\_v3 锚点）**：Pass@1 = **82\.1 ± 3\.0%** · Converged (%) = **99\.1**（5-run: [98.7, 99.4, 98.7, 99.4, 99.4]）· Mean gen-fail = **10.4**（5-run: [13, 9, 13, 9, 8]）。
> 
> 







## ZL — `zhulong`/`zl` CLI build（运维令二十八·2026-10-18）· DeepSeek-V4-Pro-Cloud

> **状态：🔴 eval 未跑（n=0，无分数）— gateway HTTP 403 阻塞 `deepseek-v4-pro-cloud` 模型**
> 标记：`[blocked, n=0]`（非 provisional，未产生任何 Pass@1 数据，禁入论文表）。

### ① 构建 + 安装（已完成 ✅）
- **源**：`eda_platform`（36.15，`/nasdata/app.e0031982/code/eda_platform`，`git log -1` = `ee7ec42 add read me`，`master` 与 origin 平齐）→ `apps/cli`（`@cline/cli`，package.json `version=3.0.29`，`bin: cline → src/index.ts`）。`eda_platform` 本身即 cline 仓库改造版，未 clone 别处顶替、未 `git checkout` 别人改动、未改源码。
- **工具链**：`bun 1.3.14` + `node v20.18.1`（engines 要求 node≥22/bun 1.3.13；用 bun 作运行时绕过 node22 缺失）。
- **构建命令原文**（在 `eda_platform` 根）：
  1. `bun install --frozen-lockfile`（2788 包，241.70s，走 npmjs via proxy `http://172.19.92.23:13128`，aliyun/npmmirror 内网镜像不通）
  2. `bun run build:sdk`（= `bun --production -F './sdk/packages/*' build`，~37s，5 个 sdk 包全 exit 0）
  3. `bun -F @cline/cli build`（= `bun run bun.mts`，~33s，含 cline-hub webview 构建，exit 0）
- **产物**：`apps/cli/dist/index.js` = **19,140,548 B (19 MB)** + `dist/extensions/plugin-sandbox-bootstrap.js` + `dist/cline-hub/webview/`。
- **安装**（独立前缀，不 `bun install -g`、不 `bun link`、不动 `@cline` 包）：
  - `~/.local/zhulong/dist/` ← `cp -rL apps/cli/dist`（build artifact 复制到位）
  - `~/.local/zhulong/node_modules` → 符号链接到 `apps/cli/node_modules`（解析 externalized 包：`@opentui/*`、`react`、`react-devtools-core`、`opentui-spinner`）
  - `~/.local/zhulong/bin/zhulong`（wrapper：`exec bun $ZHULONG_HOME/dist/index.js "$@"`，bun 取 `~/.local/node-20/bin/bun`）
  - `~/.local/bin/zhulong → ~/.local/zhulong/bin/zhulong`、`~/.local/bin/zl → ~/.local/zhulong/bin/zhulong`（替换旧的 `zhulong → cline` 与 `zl → ~/.local/share/zhulong/zhulong.sh` 两条 Sep-1 旧符号链接）
  - `du -sh ~/.local/zhulong` = **52 MB**（含 dist 25M + dereferenced externals）
- **验收原文**：
  - `zhulong --version` = **3.0.29**；`zl --version` = **3.0.29**
  - `which -a zhulong zl` = `/home/app.e0031982/.local/bin/zhulong`、`/home/app.e0031982/.local/bin/zl`
  - `ls -l ~/.local/bin/{zhulong,zl}` = 两条均 `-> /home/app.e0031982/.local/zhulong/bin/zhulong`
  - **对比**：`zhulong --version` = 3.0.29 vs `cline --version` = 3.0.51（版本不同=被测变量；cline 为被测基线）

### ② cline 3.0.51 未被改动 ✅（取证 → 收尾复核逐字一致）
- 取证（动手前）：`which -a cline`=`/home/app.e0031982/.local/node-20/bin/cline`；`cline --version`=`3.0.51`；`ls -l $(which cline)`=`lrwxrwxrwx ... -> ../lib/node_modules/@cline/cli-linux-x64/bin/cline`；`readlink -f $(which cline)`=`/nasdata/app.e0031982/.local/node-20/lib/node_modules/@cline/cli-linux-x64/bin/cline`（148,957,504 B）；`~/.bun/bin/cline` 不存在；`~/.bun/install/global/node_modules/@cline` 不存在。
- 收尾复核：`which -a cline` 同上；`cline --version`=`3.0.51`；`readlink -f $(which cline)` 与取证**逐字一致**。
- 全程未执行 `curl|bash` 官方安装器、未 `bun add/link/install -g @cline/cli`、未覆盖 `~/.bun/bin/cline`、未改 `~/.local/node-20/lib/node_modules/@cline`、未改 `~/.cline`（`~/.cline/data/settings/providers.json` mtime 仍为 2026-10-18 00:55:25，即 glm-5.3-flash 工作，本轮未触碰）。

### ③ 配置 = DeepSeek-V4-Pro-Cloud（与 cline 3.0.51 配置隔离）✅
- `zhulong auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m deepseek-v4-pro-cloud --data-dir ~/.zhulong` → `Provider configured: openai-compatible (deepseek-v4-pro-cloud)`
- **生效配置**（`~/.zhulong/settings/providers.json`，updatedAt=`2026-10-18T00:08:55.342Z`）：
  - `model` = `deepseek-v4-pro-cloud`
  - `baseUrl` = `http://agi-gateway.cxmt.com/cloud/v1`
  - `apiKey` 末 8 位 = `88ea2f23`（复用 `eda_fastmcp/providers.json` 同批 cloud/v1 key，glm-5.2 同 key 实测 HTTP 200）
  - data dir = `~/.zhulong`（独立，**未写进 `~/.cline`**）
- 端到端 canary（`zhulong --data-dir ~/.zhulong -c /tmp/zl_canary_ws --auto-approve true -t 20 "Reply with: ZL_CANARY_OK"`）→ `error: Forbidden`（= HTTP 403，证明 zhulong 正确读取 ~/.zhulong 配置 → 命中 cloud/v1 → 网关返回 403；配置链路通）。

### ④ 🔴 eval 未跑（n=0）— 网关 HTTP 403 阻塞 `deepseek-v4-pro-cloud`
- **canary 矩阵**（`curl --noproxy '*' POST .../chat/completions`）：
  | 模型 | 路径 | key | HTTP |
  |---|---|---|---|
  | `deepseek-v4-pro-cloud` | `/cloud/v1` | 全 8 把 `02_088EE...` key（c2759d74/3dd97aea/80a707b0/6903b05e/c43c1f4a/5591ae9f/c406f420/c5280771）| **403** |
  | `deepseek-v4-pro-cloud` | `/v1` | c43c1f4a | **403** |
  | 模型名变体 `deepseek-v4-pro` / `DeepSeek-V4-Pro-Cloud` / `deepseek-v4-pro-fp4` / `deepseek-v4-pro-cloud-latest` / `deepseek-pro-cloud` | `/cloud/v1` | c2759d74 | **403** |
  | `glm-5.2`（对照）| `/cloud/v1` | c2759d74（同 key）| **200** + content |
  | `deepseek-v4-flash`（对照）| `/v1` | c43c1f4a | **200** + content |
- **403 响应**：`HTTP/1.1 403 Forbidden` + `www-authenticate: Basic realm=MSE Gateway` + `server: istio-envoy` + `content-length: 0`（空 body）。
- **根因**：MSE Gateway（istio-envoy）层对 `deepseek-v4-pro*` 模型族的 authz 策略阻塞。**非 key 问题**（同 key 对 glm-5.2 返回 200）、**非 quota**（403≠429）、**非并发**（单请求也 403）、**非路径问题**（/cloud/v1 + /v1 均 403）。整个 `deepseek-v4-pro*` 族当前被网关封禁。
- **vs MEMORY 06:46–07:20 的 401**：07:40 网关 auth 层从 401 恢复（glm-5.2/flash 恢复 200），但 `deepseek-v4-pro*` 族转为 403（模型级 authz 阻塞，更窄但更硬）。
- **决策**：403 为硬 authz 阻塞，非任务 ⑤ 所述「401/429 致整批作废」可降 -p 重跑的情形（单请求即 403，降 -p 无意义；跑 158 题必为 0/158 全 403 = 纯浪费，违反「🚫 不擅自作废」纪律）→ **不启动 eval**，标 `[blocked, n=0]`，等运维放行（网关解封 deepseek-v4-pro-cloud / 提供可达 endpoint / 换模型）。

### ⑤ 评测脚本就绪（待网关解封即可跑）
- `eda_fastmcp/scripts/run_zhulong_script.sh` = `run_cline_script.sh` 副本，唯一改动：`CLI_AGENT` 默认 `cline`→`zhulong`，并设 `CLI_DATA_DIR=${CLI_DATA_DIR:-$HOME/.zhulong}`（worker setup 从 ~/.zhulong 复制 providers.json 到各 worker 隔离目录）。eval 参数（`-p 8 -n`、timeout 2500、4 端口 8650/8651/8652/8654@10.129.32.75、regrade 判定、反作弊 hook）一律不动。
- `eda_fastmcp/scripts/run_cli.sh` zhulong 分支 invocation 修正：旧的 `zhulong -y -a -t 2500 "$task"`（0.1.3 旗标，3.0.29 已无 `-y/-a`，且无 `-c/--data-dir` → 会读 `~/.cline` 违红线 + 错模型）改为与 cline 分支一致 `zhulong -c "$ws_dir" --data-dir ${CLI_ISOLATION_DIR}/worker_${slot}/data -t 2500 "$task"`。仅影响 `CLI_AGENT=zhulong` 运行（别线不用 zhulong，零影响）。
- 反作弊 hook 源 `scripts/cline_hooks/PreToolUse`（10,242 B）在位，eval 启动时 `seed_cline_hooks` 部署到 `~/.cline/hooks/PreToolUse`；zhulong `--config` 默认 `~/.cline/data/settings` → hook 发现路径不变，对 zhulong 同样生效（hook canary 需 agent 实际跑工具调用，403 下无法验，待解封后首轮 canary）。
- `.env` full harness + V3 自探索 ON（`EDA_PHI_BUDGET=0` / `EDA_PHI_LAGGED=0` / `EDA_OMEGA_FIDELITY=high` / `EDA_RUNCODE_READBACK=full` / `EDA_MCP_RUN_CODE_FEEDBACK=full` / `API_INFO_MERGED_FILE=./docs/API_INFO_MERGED_V3.json` / `SKILL_DATA_DIR=./docs/skill_data_selfexpl`）✅；4 端口全 OPEN ✅；`/home`=22G（≥8G ✅，95% 需关注）。

### ⑥ 对照（无法给出 Pass@1，n=0）
- vs `deepseek-v4-flash` 60.1±5.5%（n=5）· `glm-5.2` 83.3±3.1%（n=5）· 主基座 `deepseek-v4-pro-fp4` 82.1±3.0%（n=5）：**`deepseek-v4-pro-cloud` 158 题 Pass@1 = N/A `[blocked, n=0]`**（网关 403，eval 未跑，无通过数/158，无 timeout/gen-fail/quota 计数）。**禁止写成 ±**（n=0）。
- 待网关解封 `deepseek-v4-pro-cloud`（canary HTTP 200 + content）后：`cd $BASE_DIR && export PYTHON=$PWD/venv/bin/python && setsid bash scripts/run_zhulong_script.sh -p 8 -n > /tmp/ZL_v4procloud_r1.log 2>&1 < /dev/null &` → 打分 `grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ZL_v4procloud_r1.log | tail -5`（Step7.1 auto-grade 已知 FileNotFoundError bug → 手动 regrade，模板同 deepseek-v4-flash retest，改 batch + GEN_FILE）→ n=1 单值标 `[provisional,n=1]`。

---

## ZL.glm-5.2 — `zhulong`/`zl` CLI × `glm-5.2`（运维令二十九·2026-10-18 · 用户直令「把 eda_platform 评测的基模换成 glm-5.2」）

> **背景**：运维令二十八原定底模 `deepseek-v4-pro-cloud` 被 MSE Gateway HTTP 403 封禁（全 8 key × 2 path × 6 模型名变体均 403），eval 未跑 n=0。运维令二十九用户直令：底模改为 `glm-5.2`（@ cloud/v1 同 key 实测 200），其余口径照旧（构建/安装/隔离配置/158 集/n=1 provisional/不碰 cline 3.0.51）。

> **状态：✅ r1 完成（n=1，2026-10-18 09:38→12:17）— Pass@1 = 84.2%**
> 标记：`[provisional, n=1]`（n=1 不入论文表，仅作 `zhulong 3.0.29 / cline-core 0.0.51` vs `cline 3.0.51 / cline-core 0.0.71` 对照参考；🚫 ±、🚫 因果归因）。

### ① 版本对照（必填）
| 项 | zhulong（被测） | cline（基线对照） |
|---|---|---|
| CLI `--version` | **3.0.29**（@cline/cli，build from `eda_platform/apps/cli`·git log -1=`ee7ec42 add read me`）| **3.0.51**（@cline/cli-linux-x64，运维令二十八取证 + 二十九收尾复核逐字一致） |
| `@cline/core` SDK | **0.0.51** ✅（pre-check ① 三连核验：`apps/cli/package.json` `"@cline/core": "workspace:*"` → `node_modules/@cline/core/package.json` `"version": "0.0.51"` → `bun pm ls` `@cline/core@workspace:sdk/packages/core`） | 0.0.71（运维令二十八用户提供前提） |
| 入口 | `~/.local/bin/{zhulong,zl}` → `~/.local/zhulong/bin/zhulong`（bun wrapper, 52 MB） | `/nasdata/app.e0031982/.local/node-20/lib/node_modules/@cline/cli-linux-x64/bin/cline`（148,957,504 B） |

### ② cline 3.0.51 未被改动 ✅（取证 → 二十九收尾复核逐字一致）
- 取证（动手前）：`which -a cline`=`/home/app.e0031982/.local/node-20/bin/cline`；`cline --version`=`3.0.51`；`readlink -f $(which cline)`=`/nasdata/app.e0031982/.local/node-20/lib/node_modules/@cline/cli-linux-x64/bin/cline`；`~/.bun/bin/cline` 不存在。
- 二十九收尾复核（eval 启动后 09:42）：`which -a cline` 同上；`cline --version`=`3.0.51`；`readlink -f $(which cline)` 与取证**逐字一致**。
- 全程未 `curl|bash` 官方安装器、未 `bun add/link/install -g @cline/cli`、未覆盖 `~/.bun/bin/cline`、未改 `~/.local/node-20/lib/node_modules/@cline`、未改 `~/.cline`（`/nasdata/app.e0031982/.cline` mtime 仍 2026-09-22 16:09，`~/.cline/data/settings/providers.json` mtime 仍 2026-10-18 00:55，本轮仅写 `~/.zhulong/settings/providers.json`）。

### ③ 配置 = glm-5.2（与 cline 3.0.51 配置隔离）✅
- `zhulong auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2 --data-dir ~/.zhulong` → `Provider configured: openai-compatible (glm-5.2)`
- **生效配置**（`~/.zhulong/settings/providers.json`，updatedAt=`2026-10-18T01:36:17.350Z`）：
  - `model` = `glm-5.2`
  - `baseUrl` = `http://agi-gateway.cxmt.com/cloud/v1`
  - `apiKey` 末 8 位 = `88ea2f23`（同 key 实测 HTTP 200 + content）
  - data dir = `~/.zhulong`（独立，**未写进 `~/.cline`**）
- **gateway canary**（剥 proxy 直 curl）：
  - `max_tokens=16`：HTTP 200 + `reasoning_content` 16 token（glm-5.2 实为推理模型，小预算被 reasoning 烧光）
  - `max_tokens=256`：HTTP 200 + `content="ok"` + `reasoning_tokens=111` + `finish_reason=stop` ✅（content 正常产出）
  - ⚠️ zhulong providers.json 当前**未设 `maxTokens`**（沿用 API 默认）。若 r1 出现 null-content 失败（glm-5.2 reasoning 耗光预算）→ 不擅自加 maxTokens，按令二十九「只换模型，不改配置」红线，回报等运维决策（同 deepseek-v4-flash 令二十七② maxTokens 修复路径）。

### ④ eval r1 启动（2026-10-18 09:38:52）
- 启动命令：`cd $BASE_DIR && export PYTHON=$PWD/venv/bin/python && setsid bash scripts/run_zhulong_script.sh -p 8 -n > /tmp/ZL_glm52_r1.log 2>&1 < /dev/null &`（PID 1424781 · batch `2026_1018_093852` · `-p 8` + `-n`（禁 Memory Bank 注入）+ timeout 2500 + 4 端口 8650/8651/8652/8654@10.129.32.75 + V3 文档 + 自探索 ON + full harness）。
- **infra 全绿**：4 端口全 OPEN ✅；`/home`=20G（≥8G ✅，95% 需关注）；loop PID 81827 有 proxy ✅；ops relay PID 1422695 alive ✅；MCP@8090 / RAG@9006 alive ✅。
- **反作弊 hook canary ✅**（eval 启动后 09:41 抽样）：
  - hook 部署：`~/.cline/hooks/PreToolUse`（10,242 B，09:39 由 `seed_cline_hooks` 自动部署）✅。
  - hook 生效证据：`grep -c 'ACCESS RESTRICTED' /tmp/ZL_glm52_r1.log` = **26**（agent 调 `run_commands` 13 次全被阻，符合预期「应被拒」）。
  - agent 工具分布（采样前 ~3 分钟）：`[thinking]`=79 / `[pyAether_MCP_server__search_apis]`=29 / `[pyAether_MCP_server__get_api_details]`=29 / `[pyAether_MCP_server__run_code]`=21 / `[search_apis_by_keyword]`=14 / `[run_commands]`=13（全 blocked）/ `[editor]`=10 / `[read_files]`=5 → MCP 工具调用正常，editor 写代码未被阻（合法 workspace 内），符合 deepseek-v4-flash retest r1 trace 中 PASS 任务的工具使用模式。
- **判据**：r1 完成后打分 `grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ZL_glm52_r1.log | tail -5`（以 `pass (xx.x%)` 为准）；timeout / 0-token / quota 单列。若 429/限流 → 按令二十七① 降 `-p 4` 重跑一次（只降并发，不改模型/配置）；若 401/403 → 立即停、贴响应头原文、报 blocker（不空转）。

### ⑤ Pass@1（r1 已完成 · 2026-10-18 12:17 · n=1 · `[provisional,n=1]`）
- **`glm-5.2` × `zhulong(3.0.29)` 158 题 Pass@1 = 84.2%**（通过数/158 = **133/158**）。
- `pass (` 原文（regrade log 末尾）：
  - `✅ 1018: 133/158 pass (84.2%) | generated: 153 ok, 3 fail`
  - `通过率: 0.8418 (133/158 个任务通过)`
  - `生成状态统计: {'success': 153, 'failure': 0, 'timeout': 2, 'fail': 3}`
  - `pyAether_aether (lang=pyAether, host=aether, 样本 133/153): PASS_RATE=0.8693`
- **失败/异常计数**（main eval log `/tmp/ZL_glm52_r1.log` + regrade log `/tmp/ZL_glm52_r1_regrade.log`）：
  - gen-success = **153** / gen-fail = **3** / gen-timeout = **2** / 158 − (153+3+2) = 0 余
  - 0-token 失败 = **0**（grep `0-token|inputTokens.*0.*outputTokens.*0` = 0）
  - HTTP 429 / quota error = **0**（grep `HTTP 429|429 Too Many|quota_exceeded` = 0；r1 全程无网关限流·与 deepseek-v4-flash fresh 45% 0-token 形成对比）
  - null-content 失败 = **0**（grep `null.*content|content.*null` = 0；glm-5.2 reasoning 未耗光预算·providers.json 沿用 API 默认 maxTokens 即可）
  - 反作弊 hook canary ✅：`grep -c 'ACCESS RESTRICTED' /tmp/ZL_glm52_r1.log` = 571（hook 全程生效）
- **regrade 流程注记**（运维侧手动 regrade）：eval r1 auto-grade 因 `eda_fastmcp/.env` `EVAL_FW_DIR` 指向 `/home/app.t0002997/proj/EDA-Eval-Framework_1_pyaether`（不存在路径）而失败；agent 改用 `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework` 覆盖启动手动 regrade（`scripts/run_eval.py -g completed_code_generation_2026_1018_093852.jsonl --benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl --skip-assemble`）。**首次 regrade 因 regrade 启动脚本误 export `https_proxy=http://172.19.92.23:13128` 致沙盒 HTTP `10.129.32.75:8650` 走 Squid proxy → HTTP 503 Connection timed out**；**修复 = unset proxy + `NO_PROXY=10.129.32.75`**（沙盒为内网 IP，无需 proxy），regrade 11:56:34 重启 → 12:17:06 EXIT=0 完成（~20 min）。regrade log /tmp/ZL_glm52_r1_regrade.log；归档 `EDA-Eval-Framework/output_evaluation/20260918_*` 之前的 batch 目录（本批 2026_1018_093852 归档在 `20260918_*` 序列下，运维侧 regrade 不自动归档）。

### ⑥ 对照（同模型、不同 CLI/SDK · n=1 · 仅参考 · 🚫 不入论文表）
- **既有 `glm-5.2` 臂**（n=5，cline 3.0.51 / cline-core 0.0.71）= **83.3 ± 3.1%** [84.2, 87.3, 84.2, 79.1, 81.6]
- **本次 ZL.glm-5.2**（n=1，zhulong 3.0.29 / cline-core 0.0.51）= **84.2%** [provisional, n=1]（133/158）。**禁止 ±**（n=1）、**禁止据此断言「改造版更好/更差」**（n=1 + 版本双变量：CLI 3.0.29 vs 3.0.51、SDK 0.0.51 vs 0.0.71）。n=1 单值落在 n=5 区间 [79.1, 87.3] 内、紧贴均值 83.3% 上方 0.9pp，**符合「老 SDK 改造版在同模型上仍具备实验意义」的前提**（运维令二十八①「SDK 0.0.51 是否还具实验意义」的实证回答：YES）。
- **并列写明 SDK 代差**：两侧变量 = (CLI 版本, cline-core 版本) = (3.0.29, 0.0.51) vs (3.0.51, 0.0.71)，差异不得归因于单一变量。
- 与 deepseek-v4-flash 复测 60.1±5.5%（n=5·SDK 0.0.71·trace 修复后）对比：glm-5.2 单次 84.2% 显著高于 flash 5 轮均值，但**不跨模型比较**（运维令二十九①「同模型、不同 CLI/SDK」才是被测变量；跨模型比较在 tab:llm-comparison 由 n=5 主表负责，n=1 不入）。

### ⑦ 注脚（同步 `MEMORY_ZHULONG.md` + `daily-memories/2026-10-18.md`）
- commit 前缀 `zhulong zl:`；n=1 不进论文表。
- r1 完成后步骤：① grep `pass (` 打分 → ② 统计 timeout/gen-fail/0-token/quota → ③ 回填本节 ⑤ + ⑥ → ④ 同步 `MEMORY_ZHULONG.md`（PHASE=just_finished / CONFIG=`ZL.glm-5.2` / ROUND=r1 done）+ `daily-memories/2026-10-18.md` → ⑤ commit `zhulong zl: glm-5.2 r1 = xx.x% [provisional,n=1]`。
