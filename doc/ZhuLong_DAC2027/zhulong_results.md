# ZhuLong 假期试验原始分数汇总（2026\-10\-08）



> 评测集：EDA\-Scripting\-Bench，指标 Pass@1（%），每臂 N=5 轮。
> 
> 主干 LLM：DeepSeek\-V4\-Pro（C1\.full 锚点）。
> 
> 反作弊 hook 全程生效。
> 
> 





## 总览

|阶段|臂|N=5 mean±std|状态|
|---|---|---|---|
|B|glm\-5\.2|**83\.3 ± 3\.1%**|5/5 ✅|
|B|deepseek\-v4\-flash|**16\.7 ± 12\.3%**|5/5 ✅|
|B|kimi\-k2\.6\-cloud|**77\.0 ± 1\.6%**|5/5 ✅|
|B|doubao\-seed\-2\.0\-pro\-cloud|**63\.8 ± 1\.4%**|5/5 ✅|
|C1|pure\_llm|10\.5 ± 1\.9%|5/5 ✅（复用 legacy）|
|C1|rag|**71\.8 ± 2\.5%**|5/5 ✅|
|C1|wo\_retrieval|**81\.0 ± 4\.5%**|5/5 ✅|
|C1|full（锚点）|—（探路 84\.8%）|1/5 ▶ r1 运行中|
|S1|omega\_low \(Ω L\)|**82\.8 ± 1\.0%**|5/5 ✅（legacy）|
|S1|readback\_binary \(B\)|**66\.2 ± 16\.1%**|5/5 ✅（legacy）|
|S1|readback\_none \(N\)|**73\.3 ± 2\.2%**|5/5 ✅（legacy）|
|S2|phi\_k10|75\.3%|1\-shot 探路 ✅（legacy）|
|S2|phi\_k3|69\.0%|1\-shot 探路 ✅（legacy）|
|S2|phi\_k1|60\.8%|1\-shot 探路 ✅（legacy）|
|S2|phi\_lagged|84\.2%|1\-shot 探路 ✅（legacy）|





## Phase B：大模型消融（固定 ZhuLong 框架，换 LLM）



### B\.glm\-5\.2（GLM\-5\.2）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|84\.2|||||
|r2|87\.3|||||
|r3|84\.2|||||
|r4|79\.1|||||
|r5|81\.6|||||
|**mean±std**|**83\.3 ± 3\.1%**|||||
|||||||



### B\.deepseek\-v4\-flash（DeepSeek\-V4\-Flash）



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



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|63\.9|||||
|r2|64\.6|||||
|r3|61\.4|||||
|r4|65\.2|||||
|r5|63\.9|||||
|**mean±std**|**63\.8 ± 1\.4%**|||||
|||||||



---



## C1：组件消融（固定 LLM=DeepSeek\-V4\-Pro，逐组件开关）



### C1\.pure\_llm（纯 LLM，核心 4 工具全关）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|8\.2||35\.0|3\.9|15\.8|
|r2|9\.5||33\.8|2\.6|24\.6|
|r3|10\.1||29\.3|1\.3|21\.1|
|r4|11\.4||34\.4|3\.9|19\.3|
|r5|13\.3||33\.8|2\.6|19\.3|
|**mean±std**|**10\.5 ± 1\.9%**||**33\.2 ± 2\.3%**|**2\.9 ± 1\.1%**|**20\.0 ± 3\.2%**|



### C1\.rag（仅检索、关 sandbox）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|70\.3|72\.2|42\.0|51\.9|54\.4|
|r2|72\.2||50\.3|51\.9|57\.9|
|r3|69\.6||48\.4|50\.6|50\.9|
|r4|70\.9||49\.0|57\.1|52\.6|
|r5|75\.9||47\.8|50\.6|45\.6|
|**mean±std**|**71\.8 ± 2\.5%**||**47\.5% ± 3\.2%**|**52\.5% ± 2\.7%**|**52\.3% ± 4\.5%**|



### C1\.wo\_retrieval（仅 sandbox、关检索 3 件套）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|74\.1|||||
|r2|86\.1|||||
|r3|81\.6|||||
|r4|79\.7|||||
|r5|83\.5|||||
|**mean±std**|**81\.0 ± 4\.5%**|||||
|||||||



### C1\.full（完整系统，锚点）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|—|79\.1|61\.8|84\.4|80\.7|
|r2|—|80\.4|60\.5|85\.7|66\.7|
|r3|—|77\.8|62\.4|88\.3|66\.7|
|r4|—|76\.6|61\.8|85\.7|86\.0|
|r5|—|72\.8|61\.1|85\.7|61\.4|
|**mean±std**|—|**77\.3** ± 2\.9|**61\.5** ± 0\.7|**86\.0** ± 1\.4|**72\.3** ± 10\.5|
|||||||



---



## S1：保真度消融（固定 LLM=DeepSeek\-V4\-Pro，逐保真度轴开关）



> 数据来源：legacy `MEMORY_s1_full.md`（PHASE=done\_all，2026\-10\-03 14:18 收口）。
> 
> 3 臂 × 5 轮全部完成，反作弊 hook 全程启用。
> 
> 



### S1\.omega\_low（Ω 文档保真度=low，核心 4 工具全开 \+ readback=full）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|81\.6|||||
|r2|82\.3|||||
|r3|84\.2|||||
|r4|82\.9|||||
|r5|82\.9|||||
|**mean±std**|**82\.8 ± 1\.0%**|||||



### S1\.readback\_binary（readback=binary，Ω=high）



|轮次|PyAether（刘杨）|PyAether（陈熙元）|SKILL|TCL\_WaveView|TCL\_Innovus|
|---|---|---|---|---|---|
|r1|56\.3|||||
|r2|74\.1|||||
|r3|75\.3|||||
|r4|43\.0|||||
|r5|82\.3|||||
|**mean±std**|**66\.2 ± 16\.1%**|||||



### S1\.readback\_none（readback=none，Ω=high）



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



> 数据来源：legacy `MEMORY_s2_1shot.md`（PHASE=done\_all，1\-shot 探路）。
> 
> 每臂仅 1 轮探路值（非 5\-run mean±std），Converged% / Mean read\-backs 同步报告。
> 
> phi\_unbounded ≡ full 锚点（84\.8%），跳过不跑。
> 
> 



|臂|Pass@1 \(%\)|通过数|Converged \(%\)|Mean read\-backs|batch ID|备注|
|---|---|---|---|---|---|---|
|phi\_k10|75\.3|119/158|91\.1 \(144/158\)|9\.58|2026\_0928\_220542|deny\[PHI\-BUDGET\]=59；14 条 cancelled|
|phi\_k3|69\.0|109/158|79\.1 \(125/158\)|8\.18|2026\_0929\_005419|deny\[PHI\-BUDGET\]=105；33 条 cancelled|
|phi\_k1|60\.8|96/158|71\.5 \(113/158\)|8\.66|2026\_0929\_033533|deny\[PHI\-BUDGET\]=152；45 条 cancelled|
|phi\_lagged|84\.2|133/158|98\.1 \(155/158\)|—|2026\_0929\_110309|r2（r1 batch 2026\_0929\_061645 因 lag 审计 fail 作废）；lag==1 审计 133/158 精确通过|



> **注**：S2 各臂为 1\-shot 探路值，需 5\-run 重跑后方可填论文 `tab:phi-bound` 的 mean±std。cancelled = agent 超额重试后自身终止（非 hook 中断）。
> 
> 



---



## Legacy 组件消融参考（已作废）



> 数据来源：legacy `MEMORY_component_full.md`。rag 全 5 轮在 BM25\-only 降级态测得（RAG recall 端口 9012 无监听，降级为 BM25），**已作废**，本线已用真语义检索态重跑（见 C1\.rag 71\.8±2\.5%）。
> 
> 



|臂|N=5 mean±std|各轮原始值|状态|
|---|---|---|---|
|rag \(legacy, BM25\-only\)|~~68\.2 ± 7\.4%~~|\[71\.5, 70\.3, 75\.3, 68\.4, 55\.7\]|❌ 作废（端口错配降级态）|



---



## 备注



1. **数据来源**：`run/MEMORY_ZHULONG.md` §成绩记录（本线 B/C1）\+ legacy `MEMORY_s1_full.md`（S1）\+ legacy `MEMORY_s2_1shot.md`（S2）\+ legacy `MEMORY_component_full.md`（legacy rag 参考），每个数字可回溯到 \(config, run\_id, batch\) 级别。

2. **pure\_llm**：5 轮数据复用 legacy 组件线结果（同一配置、同一评测协议、反作弊 hook 下），非假期新跑。

3. **S1 保真度消融**（omega\_low / readback\_binary / readback\_none）：5 轮数据全部来自 legacy `MEMORY_s1_full.md`（2026\-09\-29 至 10\-03 跑完，PHASE=done\_all）。反作弊 hook 全程启用、冻结。omega\_low r1/r3、readback\_none r2 各有 1 次 attempt 因 /home 磁盘满或崩溃风暴作废后重跑恢复。

4. **S2 Φ 轴**（phi\_k10/k3/k1/lagged）：1\-shot 探路值来自 legacy `MEMORY_s2_1shot.md`（2026\-09\-28 至 09\-29 跑完，PHASE=done\_all）。phi\_lagged r1 因 lag 审计 fail（槽位跨 trace 泄漏）作废，r2 修复后通过。各臂仅 1 轮，需 5\-run 重跑后方可填论文 mean±std。

5. **legacy rag**（68\.2±7\.4%）：因 RAG recall 端口 9012 无监听降级为 BM25\-only，已作废；本线已用真语义检索态（端口 9006）重跑为 71\.8±2\.5%。

6. **rag r3**：曾因 infra 额度耗尽作废（batch 2026\_1007\_151301, 0/158），已重跑恢复为 69\.6%。

7. **wo\_retrieval r2**：旧 r2 因 pro\-fp4 403 全军覆没作废（0/158），已重跑恢复为 86\.1%。

8. **C1\.full**：1\-shot 探路值 84\.8%（134/158）为 2026\-09\-28 实测；5\-run r1 于 10\-08 11:47 启动，运行中。

9. **Δ 计算**：效应量由同批 mean 相减得出。已完成的 5\-run Δ：pure\_llm→rag = \+61\.3 pp（71\.8−10\.5）。涉及 full 的 Δ 待 full 5\-run 收割后从同批数据算出。

10. **本机无 pdflatex**：论文 \.tex 已更新实测值，PDF 编译需在 Windows MiKTeX 或装有 LaTeX 的环境执行。

## 



