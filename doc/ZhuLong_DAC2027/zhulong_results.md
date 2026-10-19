# ZhuLong 试验原始分数汇总



> 评测集：EDA\-Scripting\-Bench，指标 Pass@1（%），每臂 N=5 轮。
> 
> 主干 LLM：DeepSeek\-V4\-Pro（C1\.full 锚点）。
> 
> 反作弊 hook 全程生效。
> 
> 知识库 V3，默认自探索 ON
> 
> Cline\-CLI 版本：3\.0\.51，@cline/core SDK 版本：0\.0\.71
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

* [x] **C1\.wo\_selfexp**（V2 自探索 OFF）— 刘杨 **81\.4 ± 4\.1%** · 陈熙元 **77\.3 ± 2\.9%** ✅ 5/5

* [x] **C1\.full**（V3 自探索 ON · 锚点）— 刘杨 **82\.1 ± 3\.0%** · 陈熙元 **81\.4 ± 1\.5%** ✅ 5/5

    

### S1：保真度消融（3 臂 × 5 轮 = 15 轮，legacy）



* [x] **S1\.omega\_low**（Ω L）— **82\.8 ± 1\.0%** ✅ 5/5（legacy）

* [x] **S1\.readback\_binary**（B）— **66\.2 ± 16\.1%** ✅ 5/5（legacy）

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
|r1|84\.2|56\.7|81\.8|57\.9|
|r2|87\.3|55\.4|83\.1|75\.4|
|r3|84\.2|46\.5|80\.5|49\.1|
|r4|79\.1|56\.1|81\.8|91\.2|
|r5|81\.6|57\.3|77\.9|68\.4|
|**mean±std**|**83\.3 ± 3\.1%**|**54\.4 ± 4\.5%**|**81\.0 ± 2\.0%**|**68\.4 ± 16\.2%**|



### B\.deepseek\-v4\-flash（DeepSeek\-V4 Flash）

DeepSeek 系列轻量模型，验证小参数量 backbone 能否驱动框架。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|60\.1|47\.8|72\.7|82\.5|
|r2|57\.0|47\.8|70\.1|73\.7|
|r3|62\.7|47\.1|70\.1|71\.9|
|r4|67\.7|48\.4|74\.0|54\.4|
|r5|53\.2|43\.9|67\.5|68\.4|
|**mean±std**|**60\.1 ± 5\.5%**|**47\.0 ± 1\.8%**|**70\.9 ± 2\.5%**|**70\.2 ± 10\.2%**|



### B\.kimi\-k2\.6\-cloud（Kimi\-K2\.6 Cloud）

Kimi 系列云端模型，测试框架对非 DeepSeek 系模型的兼容性与跨厂商泛化。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|79\.1|29\.9|77\.9|87\.7|
|r2|76\.6|58\.0|70\.1|84\.2|
|r3|77\.2|52\.9|79\.2|36\.8|
|r4|74\.7|55\.4|75\.3|86\.0|
|r5|77\.2|58\.6|76\.6|77\.2|
|**mean±std**|**77\.0 ± 1\.6%**|**51\.0 ± 12\.0%**|**75\.8 ± 3\.5%**|**74\.4 ± 21\.4%**|

> 陈熙元：skill r1，innovus r3通过率明显低于其他轮次，待重测
> 
> 



### B\.doubao\-seed\-2\.0\-pro\-cloud（Doubao\-Seed\-2\.0\-Pro Cloud）

豆包系列云端模型，进一步验证跨厂商泛化能力。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|63\.9|47\.1|66\.2|47\.4|
|r2|64\.6|45\.2|70\.1|42\.1|
|r3|61\.4|39\.5|68\.8|38\.6|
|r4|65\.2|40\.1|59\.7|38\.6|
|r5|63\.9|40\.8|61\.0|40\.4|
|**mean±std**|**63\.8 ± 1\.4%**|**42\.5 ± 3\.4%**|**65\.2 ± 4\.6%**|**41\.4 ± 3\.6%**|





### B\.glm\-5\.3\-flash（GLM\-5\.3 Flash）

GLM 新一代轻量模型，验证框架对 GLM 系轻量 backbone 的兼容性。

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|86\.1|58\.0|85\.7|84\.2|
|r2|84\.8|63\.7|83\.1|57\.9|
|r3|89\.2|56\.7|88\.3|59\.6|
|r4|87\.3|45\.9|87\.0|84\.2|
|r5|86\.7|61\.8|85\.7|89\.5|
|**mean±std**|**86\.8 ± 1\.6%**|**57\.2 ± 6\.9%**|**86\.0 ± 1\.9%**|**75\.1 ± 15\.1%**|



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
> 

|轮次|PyAether|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|
|r1|75\.9||||
|r2|79\.1||||
|r3|77\.8||||
|r4|78\.5||||
|r5|79\.1||||
|**mean±std**|**78\.1 ± 1\.3%**||||





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
|**Converged \(%\)**|**90\.4**（5\-run: \[89\.2, 90\.5, 91\.1, 91\.1, 89\.9\]）||||
|**Mean gen\-fail**|**17\.4**（5\-run: \[16, 15, 21, 16, 19\]）||||





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
|**Converged \(%\)**|**80\.4**（5\-run: \[81\.6, 79\.7, 77\.2, 81\.6, 81\.6\]）||||
|**Mean gen\-fail**|**27\.6**（5\-run: \[27, 31, 32, 23, 25\]）||||



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
|**Converged \(%\)**|**76\.3**（5\-run: \[77\.2, 77\.2, 75\.9, 75\.9,||||



> 各轮明细分：r1=103/158·35 gen\-fail·r2=105/158·30 gen\-fail·r3=92/158·39 gen\-fail·r4=102/158·34 gen\-fail·r5=102/158·35 gen\-fail（gen\-fail 随 k↓ 递增，k=1 预算效应非 infra）。PHI\-BUDGET\-EXHAUSTED=1141\>0✅（k=1 预算生效）。单调 k10=77\.7\>k3=69\.1\>k1=63\.8✅。
> 
> 





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
|**Converged \(%\)**|**97\.5**（5\-run: \[97\.5, 98\.7, 97\.5, 94\.9, 98\.7\]）||||
|**Mean gen\-fail**|**9\.0**（5\-run: \[5, 10, 11, 13, 6\]）||||



> 各轮明细分：r1=118/158·5 gen\-fail·r2=121/158·10 gen\-fail·r3=110/158·11 gen\-fail·r4=110/158·13 gen\-fail·r5=118/158·6 gen\-fail（gen\-fail=lagged 缓冲效应，非 infra）。PHI\-LAGGED 命中✅（lagged 机制生效），PHI\-BUDGET\-EXHAUSTED=0（lagged 无上限，合理）。Δvs unbounded\(82\.1\)=−9\.1pp。lagged 介于 k3\(69\.1\) 与 k10\(77\.7\) 之间。
> 
> 





> **注**：S2 四臂（phi\_k10 / phi\_k3 / phi\_k1 / phi\_lagged）均已 5/5 收口，可填论文 `tab:phi-bound` 的 mean±std。单调性 k10=77\.7\>k3=69\.1\>k1=63\.8✅；lagged=73\.0 介于 k3 与 k10 之间✅。gen\-fail 随 k↓ 递增（k=1 预算效应），与「k↓ → gen\-fail↑ → Pass@1↓」一致。Converged \(%\) 随 k↓ 递降（k10=90\.4 \> k3=80\.4 \> k1=76\.3），unbounded=99\.1，lagged=97\.5（无预算上限→高收敛）。
> 
> 
> 
> **unbounded（full\_v3 锚点）**：Pass@1 = **82\.1 ± 3\.0%** · Converged \(%\) = **99\.1**（5\-run: \[98\.7, 99\.4, 98\.7, 99\.4, 99\.4\]）· Mean gen\-fail = **10\.4**（5\-run: \[13, 9, 13, 9, 8\]）。
> 
> 
> 
> 



