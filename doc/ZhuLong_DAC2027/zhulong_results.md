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





## 总览

### Phase B：大模型消融（5 臂 × 5 轮 = 25 轮）

- [x] **B\.glm\-5\.2** — **83\.3 ± 3\.1%** ✅ 5/5
- [x] **B\.deepseek\-v4\-flash** — **16\.7 ± 12\.3%** ✅ 5/5 ⚠️ 刘杨标注"有问题，待复测"
- [x] **B\.kimi\-k2\.6\-cloud** — **77\.0 ± 1\.6%** ✅ 5/5
- [x] **B\.doubao\-seed\-2\.0\-pro\-cloud** — **63\.8 ± 1\.4%** ✅ 5/5
- [ ] **B\.glm\-5\.3\-flash** — ⬜ 0/5

### C1：组件消融（5 臂 × 5 轮 = 25 轮）

- [x] **C1\.pure\_llm** — **10\.5 ± 1\.9%** ✅ 5/5（复用 legacy）
- [x] **C1\.rag** — **71\.8 ± 2\.5%** ✅ 5/5
- [x] **C1\.wo\_retrieval** — **81\.0 ± 4\.5%** ✅ 5/5
- [x] **C1\.wo\_selfexp**（V2 自探索 OFF）— 刘杨 **81\.4 ± 4\.1%** · 陈熙元 **77\.3 ± 2\.9%** ✅ 5/5
- [x] **C1\.full**（V3 自探索 ON · 锚点）— 刘杨 **82\.1 ± 3\.0%** · 陈熙元 **81\.4 ± 1\.5%** ✅ 5/5

### S1：保真度消融（3 臂 × 5 轮 = 15 轮，legacy）

- [x] **S1\.omega\_low**（Ω L）— **82\.8 ± 1\.0%** ✅ 5/5（legacy）
- [x] **S1\.readback\_binary**（B）— **66\.2 ± 16\.1%** ✅ 5/5（legacy）
- [x] **S1\.readback\_none**（N）— **73\.3 ± 2\.2%** ✅ 5/5（legacy）

### S2：Φ 预算轴消融（4 臂 × 5 轮 = 20 轮）

- [x] **S2\.phi\_k10** — 刘杨 **77\.7 ± 2\.2%** ✅ 5/5（探路 75\.3%）
- [ ] **S2\.phi\_k3** — 探路 69\.0% 🔄 r1 运行中
- [ ] **S2\.phi\_k1** — 探路 60\.8% ⬜ 0/5
- [ ] **S2\.phi\_lagged** — 探路 84\.2% ⬜ 0/5





## Phase B：大模型消融（固定 ZhuLong 框架，换 LLM）

> **试验目标**：验证 ZhuLong 框架对不同 LLM backbone 的泛化能力。固定完整框架（检索 + 沙盒 + 自探索 ON），仅替换底层 LLM，观察 Pass@1 在不同模型间的分布与排序，回答"框架的性能增益是否依赖特定 backbone"。



### B\.glm\-5\.2（GLM\-5\.2）

> 编排模型自身作为 eval backbone，验证框架在中等能力模型上的基线表现。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|84\.2|||||
|r2|87\.3|||||
|r3|84\.2|||||
|r4|79\.1|||||
|r5|81\.6|||||
|**mean±std**|**83\.3 ± 3\.1%**|||||
|||||||



### B\.deepseek\-v4\-flash（DeepSeek\-V4 Flash）

> DeepSeek 系列轻量模型，验证小参数量 backbone 能否驱动框架。⚠️ 刘杨标注"有问题，待复测"（方差极大，r5=37\.3% 异常）。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|9\.5|||||
|r2|10\.1|||||
|r3|19\.0|||||
|r4|7\.6|||||
|r5|37\.3|||||
|**mean±std**|**16\.7 ± 12\.3%**|||||
|||||||

> 刘杨：有问题，待复测
> 
> 



### B\.kimi\-k2\.6\-cloud（Kimi\-K2\.6 Cloud）

> Kimi 系列云端模型，测试框架对非 DeepSeek 系模型的兼容性与跨厂商泛化。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|79\.1|||||
|r2|76\.6|||||
|r3|77\.2|||||
|r4|74\.7|||||
|r5|77\.2|||||
|**mean±std**|**77\.0 ± 1\.6%**|||||
|||||||





### B\.doubao\-seed\-2\.0\-pro\-cloud（Doubao\-Seed\-2\.0\-Pro Cloud）

> 豆包系列云端模型，进一步验证跨厂商泛化能力。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|63\.9|||||
|r2|64\.6|||||
|r3|61\.4|||||
|r4|65\.2|||||
|r5|63\.9|||||
|**mean±std**|**63\.8 ± 1\.4%**|||||
|||||||





### B\.glm\-5\.3\-flash（GLM\-5\.3 Flash）

> GLM 新一代轻量模型，待测。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1||||||
|r2||||||
|r3||||||
|r4||||||
|r5||||||
|**mean±std**||||||
|||||||



---



## C1：组件消融（固定 LLM=DeepSeek\-V4\-Pro，逐组件开关）

> **试验目标**：量化 ZhuLong 各核心组件对系统性能的边际贡献。固定 LLM backbone（DeepSeek\-V4\-Pro），逐个关闭检索、沙盒、自探索等组件，与完整系统对比，定位关键贡献来源。对应论文 `tab:main-ablation`。



### C1\.pure\_llm（纯 LLM，核心 4 工具全关）

> 关闭全部 4 个核心工具（`search_apis` / `get_api_details` / `run_code` / 自探索），agent 仅靠 LLM 内置知识 $\mathcal{K}$ 生成代码，无法从环境获取任何观测。作为消融基线，量化"无观测"条件下的能力下限。



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|8\.2||35\.0|3\.9|15\.8|
|r2|9\.5||33\.8|2\.6|24\.6|
|r3|10\.1||29\.3|1\.3|21\.1|
|r4|11\.4||34\.4|3\.9|19\.3|
|r5|13\.3||33\.8|2\.6|19\.3|
|**mean±std**|**10\.5 ± 1\.9%**||**33\.2 ± 2\.3%**|**2\.9 ± 1\.1%**|**20\.0 ± 3\.2%**|



### C1\.rag（仅检索、关 sandbox）

> 仅保留检索工具（`search_apis` / `get_api_details`），关闭沙盒执行（`run_code`）。agent 可查 API 文档但无法运行代码验证，检验"只读不练"的性能。对应论文 `tab:omega` 的 (N) 档（纯 RAG baseline）。

V3，自探索 ON

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|70\.3|||||
|r2|72\.2|||||
|r3|69\.6|||||
|r4|70\.9|||||
|r5|75\.9|||||
|**mean±std**|**71\.8 ± 2\.5%**|||||



### C1\.wo\_retrieval（仅 sandbox、关检索 3 件套）

> 仅保留沙盒执行（`run_code`），关闭检索 3 件套（`search_apis` / `get_api_details` / 关键词搜索）。agent 可运行代码但无法查文档，检验"只练不查"的性能。



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|74\.1|||||
|r2|86\.1|||||
|r3|81\.6|||||
|r4|79\.7|||||
|r5|83\.5|||||
|**mean±std**|**81\.0 ± 4\.5%**|||||
|||||||



### C1\.wo\_selfexp（使用未自探索增强文档）

> 使用未经自探索增强的原始 V2 文档（自探索 OFF），其余组件全开。与 C1\.full 对比，量化离线自探索对 API 文档质量的增益。

V2，自探索 OFF

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|88\.0|79\.1|61\.8|84\.4|80\.7|
|r2|79\.1|80\.4|60\.5|85\.7|66\.7|
|r3|77\.2|77\.8|62\.4|88\.3|66\.7|
|r4|80\.4|76\.6|61\.8|85\.7|86\.0|
|r5|82\.3|72\.8|61\.1|85\.7|61\.4|
|**mean±std**|**81\.4 ± 4\.1%**|**77\.3** ± 2\.9|**61\.5** ± 0\.7|**86\.0** ± 1\.4|**72\.3** ± 10\.5|
|||||||

> ⚠️ r1=88\.0% 为 V3 文档混配置异常高值，不可复现（详见 `run/reports/R1_ANOMALY_ANALYSIS_2026-10-11.html`）。r2–r5 为纯 V2 无自探索配置。



### C1\.full（完整系统，锚点）

> 完整系统（V3 自探索 ON + 检索 + 沙盒），所有组件开启。作为所有消融的锚点，其 5\-run 结果复用于 `tab:main-ablation`(full) + `tab:omega`(H) + `tab:ablation-harness`(F) + `tab:phi-bound`(unbounded) + `tab:llm-comparison`(主基座) 五张表。

V3，自探索 ON

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|77\.8|82\.9|66\.2|89\.6|63\.2|
|r2|86\.1|81\.0|64\.3|90\.9|75\.4|
|r3|81\.6|81\.6|64\.3|85\.7|93\.0|
|r4|82\.3|79\.1|55\.4|87\.0|93\.0|
|r5|82\.9|82\.3|51\.0|87\.0|93\.0|
|**mean±std**|**82\.1 ± 3\.0%**|**81\.4% ± 1\.5**|**60\.3% ± 6\.7**|**88\.6% ± 2\.1**|**85\.3% ± 15\.4**|
|||||||

> 备注：SKILL语言相较于未使用增强文档通过率变低，可能要重测。
> 
> 



---



## S1：保真度消融（固定 LLM=DeepSeek\-V4\-Pro，逐保真度轴开关）

> **试验目标**：检验观测通道 $\Omega$ 的信息保真度对 agent 性能的影响。分别降低文档检索保真度（$\Omega$ low）和回读保真度（readback binary/none），验证"观测质量越高，信念更新越准确"的假设。对应论文 `tab:omega` 与 `tab:ablation-harness`。

> 数据来源：legacy `MEMORY_s1_full.md`（PHASE=done\_all，2026\-10\-03 14:18 收口）。
> 
> 3 臂 × 5 轮全部完成，反作弊 hook 全程启用。
> 
> 



### S1\.omega\_low（Ω 文档保真度=low，核心 4 工具全开 \+ readback=full）

> 将检索索引降级为低保真度（仅 API 名 + 相似度，无描述/BM25/同义词展开），其余全开。与 C1\.full（$\Omega$=high）对比，量化文档检索质量对性能的影响。对应论文 `tab:omega` 的 (L) 档。



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|81\.6|||||
|r2|82\.3|||||
|r3|84\.2|||||
|r4|82\.9|||||
|r5|82\.9|||||
|**mean±std**|**82\.8 ± 1\.0%**|||||



### S1\.readback\_binary（readback=binary，Ω=high）

> 沙盒执行后仅返回 pass/fail（二元回读），不返回 stdout/异常栈/逐断言结果。agent 知道代码是否通过但不知道错在哪。对应论文 `tab:ablation-harness` 的 (B) 档。



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|56\.3|||||
|r2|74\.1|||||
|r3|75\.3|||||
|r4|43\.0|||||
|r5|82\.3|||||
|**mean±std**|**66\.2 ± 16\.1%**|||||



### S1\.readback\_none（readback=none，Ω=high）

> 沙盒执行后无任何返回（仅"已执行"），agent 不知道代码是否通过。检验"完全无回读"条件下 agent 能否仅凭先验信念完成任务。对应论文 `tab:ablation-harness` 的 (N) 档。



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|72\.2|||||
|r2|70\.3|||||
|r3|73\.4|||||
|r4|75\.9|||||
|r5|74\.7|||||
|**mean±std**|**73\.3 ± 2\.2%**|||||





---



## S2：Φ 预算轴消融（固定 LLM=DeepSeek\-V4\-Pro，限 run\_code 调用预算）

> **试验目标**：检验信念更新 $\Phi$ 的更新率与证据预算对 agent 收敛的影响。通过限制 `run_code` 调用次数（$k$=1/3/10）和引入回读滞后（lagged），验证"$\Phi$ 的更新率必须超过 L4 动态的时间尺度"这一原则。对应论文 `tab:phi-bound`。预算约束的是"能执行/能观测多少次"，**不是**"何时提交"——超限后 PreToolUse hook 拒绝调用，agent 收到 error 后继续自主运行。



> 数据来源：legacy `MEMORY_s2_1shot.md`（PHASE=done\_all，1\-shot 探路）。
> 
> 各臂仅有 1 轮探路值（r1），r2–r5 待 5\-run 重跑。Converged% / Mean read\-backs 同步报告。
> 
> **phi\_k10 已完成 5/5**（刘杨列），其余三臂仍为 1\-shot 探路。
> 
> phi\_unbounded ≡ full 锚点（82\.1 ± 3\.0%），跳过不跑。
> 
> cancelled = agent 超额重试后自身终止（非 hook 中断）。
> 
> 



### S2\.phi\_k10（k=10，run\_code 调用上限 10 次/trace）

> 限制 agent 每条 trace 最多调用 `run_code` 10 次，超限后 PreToolUse hook 拒绝调用（返回 `[PHI-BUDGET-EXHAUSTED]`）。检验中等证据预算下 agent 的收敛行为。需同步报告 `Converged (%)` 以区分"被切断"与"更新失效"。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|78\.5|||||
|r2|76\.6|||||
|r3|77\.2|||||
|r4|81\.0|||||
|r5|75\.3|||||
|**mean±std**|**77\.7 ± 2\.2%**|||||





### S2\.phi\_k3（k=3，run\_code 调用上限 3 次/trace）

> 限制 `run_code` 调用上限为 3 次，检验紧预算下 agent 能否在极少迭代中收敛。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|69\.0|||||
|r2||||||
|r3||||||
|r4||||||
|r5||||||
|**mean±std**||||||





### S2\.phi\_k1（k=1，run\_code 调用上限 1 次/trace）

> 限制 `run_code` 调用上限为 1 次，检验极端紧预算下的性能下限与 agent 终止行为。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|60\.8|||||
|r2||||||
|r3||||||
|r4||||||
|r5||||||
|**mean±std**||||||





### S2\.phi\_lagged（lag=1，回读滞后 1 次执行）

> 回读滞后 1 次执行——第 $n$ 次调用返回第 $n{-}1$ 次执行的状态，agent 始终基于过时观测决策（闭环被系统性地切掉一步）。检验"$\Phi$ 更新率必须超过 L4 动态时间尺度"这一原则。$k$ 轴变的是证据的**量**，lagged 变的是证据的**时效**，二者是不可互相替代的不同失效模式。

|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|84\.2|||||
|r2||||||
|r3||||||
|r4||||||
|r5||||||
|**mean±std**||||||



> **注**：S2 各臂当前仅有 1\-shot 探路值（r1），需 5\-run 重跑后方可填论文 `tab:phi-bound` 的 mean±std。
> 
> 





