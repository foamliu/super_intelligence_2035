# 论文修改建议汇总

## 1. 静态检查器解释不充分

### 论文原文
> The checker extracts every API call from the submitted code and validates each against the API documentation for four error classes: (i) fabricated APIs, (ii) wrong keyword arguments, (iii) native Python values passed to SWIG-wrapped type parameters, and (iv) swallowed exceptions (empty `except` blocks). Error-level findings are appended to the agent's response, enabling repair before final submission. The rules are derived from the API documentation and refined through extensive testing against real submissions.

**中文注释（原始）**  
> 检查器从提交的代码中提取每个API调用，并对照API文档验证四类错误：（i）捏造的API，（ii）错误的关键字参数，（iii）传递给SWIG封装类型参数的原生Python值，以及（iv）被吞没的异常（空的except块）。错误级别的发现被附加到智能体的响应中，使其能在最终提交前进行修复。规则来源于API文档，并通过大量真实提交的测试进行精炼。

### 建议修改
> The checker parses the submitted code into an AST, extracts all API calls, and validates each against the full API documentation for five error classes: (i)~fabricated APIs, (ii)~incorrect keyword arguments, (iii)~native Python values passed to SWIG-wrapped type parameters where the signature requires explicit `emyXxx` construction (both keyword and positional), (iv)~self-tests limited to weak assertions or silently swallowed exceptions, and (v)~`except` blocks that rationalize failure as expected---a pattern that circumvents the agent's own self-verification. Findings are classified as hard errors (surfaced to the agent for repair) or soft warnings (logged but suppressed). The rules are derived from the API documentation and refined through extensive testing against real submissions.

**中文注释（修改后）**  
> 检查器将提交的代码解析为AST，提取所有API调用，并对照完整API文档验证五类错误：（i）虚构的API，（ii）错误的关键字参数，（iii）签名要求显式emyXxx构造处传入原生Python值（含关键字与位置参数），（iv）仅限于弱断言或静默吞异常的自我测试，以及（v）将失败合理化为预期的except块——这种模式会规避智能体自身的自我验证。发现分为硬错误（暴露给智能体以修复）或软警告（记录但不暴露）。规则来源于API文档，并通过大量真实提交的测试进行精炼。

---

## 2. 静态检查器 "零误报" 的验证不足——展开解释

### 论文原文
> §3.4: "We validated the checker on all benchmark tasks' ground-truth solutions; it flagged none, confirming the zero-observed-false-positives claim."

**翻译**  
> 我们在 158 个 GT 解法上跑了检查器，一个都没报警 → 所以它零误报。

### 问题
这是个范围谬误。用一个简单的类比说明：  
你设计了一个癌症筛查试剂盒。你在 158 个健康人身上测试，结果一个都没误诊为癌症。你宣布：本试剂盒零假阳性。  
但真正需要测试的是：在那些看似有病但实际没病的人身上，会不会误诊？

同理，静态检查器的 "假阳性" 不是指它在 GT 解法上误报（GT 解法是专家写的，本来语法就规范，检查器当然不应该报），而是它在 Agent 生成的代码上误报——Agent 写的代码可能语法不标准但逻辑正确，如果检查器误判为错误并警告 Agent，就会误导 Agent 去修改本来正确的代码。

### 建议修改
> To validate precision, we conducted a two-tier audit. On all 158 ground-truth solutions, the checker raised no flags---a necessary sanity check, though human-written solutions follow conventions that agent code may not. We therefore inspected every checker-triggered finding across 446 agent submissions accumulated during development (spanning multiple LLM backbones and coding styles). The checker flagged 99 calls, each confirmed as a genuine API misuse---fabricated API names, incorrect keyword arguments, or unwrapped native values passed where a SWIG type was required. Zero false positives were observed.

**中文注释**  
> 为了验证精确率，我们进行了两级审计。在所有 158 个真值解上，检查器未发出任何标记——这是一项必要的健全性检查，尽管人类编写的解遵循的约定可能是智能体代码不遵循的。因此，我们检查了开发过程中积累的 446 份智能体提交中所有由检查器触发的发现（涵盖多个 LLM 后端和编码风格）。检查器标记了 99 次调用，每一次都被确认为真正的 API 误用——虚构的 API 名称、错误的关键字参数，或在需要 SWIG 类型处传递了未包装的原生值。观察到零假阳性。

---

## 3. 人工经验（§3.5）简短

### 论文原文
> ZhuLong-SE additionally injects human-crafted skills and rules into the harness. The skills cover API search strategy, command-family selection, a context-degradation guard, and SWIG type construction. The rules enforce code-generation discipline.

**中文注释**  
> ZhuLong-SE 还向 harness 中注入了人工编写的技能和规则。技能涵盖 API 搜索策略、命令族选择、上下文退化守卫和 SWIG 类型构造。规则强制执行代码生成纪律。

### 建议修改
> ZhuLong-SE additionally injects 4 hand-authored skills and 1 rule file into the harness. Unlike the self-evolving components that learn from runtime errors, these target failure patterns that execution traces capture poorly or not at all:
> - The **SWIG type-construction** skill documents 9 `emyXxx` types that require explicit `ae.X()` construction---a distinction traces rarely surface because native-to-SWIG mismatches often return `None` silently rather than raising TypeError.
> - The **context-degradation guard** prevents the agent from misinterpreting sandbox feedback: agents frequently treat a silent `None` return as a successful operation, or rationalize runtime errors as "environmental limitations" rather than code defects.
> - The **API search strategy** and **command-family selection** skills guide the agent through pyAether's 8,463 documented APIs, steering it toward the correct API family (e.g., `dbCrtXxx` vs. `cdfXxx`) and preventing unproductive search loops.
> 
> The rule file enforces behavioral discipline that static checking cannot verify---mandatory `get_api_details` verification before API use, reverse verification of creation operations, and search budgets. Together, the skills and rules provide a stable prior that the self-evolution layer (Section~\ref{sec:selfev}) extends through experience rather than relearning from scratch.

**中文注释（修改后）**  
> ZhuLong-SE 还向 harness 中注入了 4 个人工编写的技能和 1 个规则文件。与从运行时错误中学习的自进化组件不同，这些技能针对的是执行轨迹难以捕捉或完全无法捕捉的失败模式：
> - **SWIG 类型构造技能**：记录了 9 种必须用 ae.X() 显式构造的 emyXxx 类型——这一区别执行轨迹很难暴露，因为原生值与 SWIG 类型不匹配时常静默返回 None 而非抛出 TypeError。
> - **上下文退化守卫**：防止智能体误读沙箱反馈——智能体常将静默的 None 返回视为操作成功，或将运行时错误合理化解释为"环境限制"而非代码缺陷。
> - **API 搜索策略和命令族选择技能**：引导智能体穿越 pyAether 的 8463 条文档化 API，将其导向正确的 API 族（如 dbCrtXxx vs. cdfXxx），并防止无效的搜索循环。
> 
> 规则文件强制执行静态检查无法验证的行为纪律——API 使用前必须先调用 get_api_details 验证、创建操作后必须反向验证、以及搜索预算上限。技能和规则共同构成一个稳定的先验基础，自进化层（第~IV 节）在其上通过经验扩展，而非从零重新学习。

---

## 4. 数据集划分逻辑

### 旧 split 的问题
旧 split 按 (题目类别, 答案代码长度) 两个维度做分层抽样。  
**问题**：API 数量和难度没有关系。

### 新 split 的设计思路
- 24 次历史运行的完整数据（158 题 × 24 次）。对每个题，算出在这 24 次里它通过了几次：
  - 24/24 → 天花板题（谁都能过，没区分度）
  - 0/24 → 地板题（谁都过不了，也没区分度）
  - 12/24 → 波动题（时过时不过，有区分度）
- 另外，从 §8 的 human vs naked 6v6 对比中，有 9 道题是人类和裸基线表现不同的（真正的跨方法区分度题）。

### 完整分配逻辑（四层区分度分级 + 按类别分配）

1. **数据结构与配额约束**  
   对全部 158 题，取 24 批历史 baseline（覆盖不同模型版本与配置）的 binary pass/fail 结果，计算每题跨 24 批的 pass_rate 与方差（variance）。总量固定为 train 98 / val 20 / test 40，且 6 个 category 各自的 test/val/train 占比与旧 split 保持一致（如 DCC 类 46 题中 test = 11、val = 7），确保类别分布不因重分配而扭曲。

2. **四层区分度分级**（按区分能力从强到弱，层间互斥）  
   - **Tier 1**（§8 已知区分度，共 9 题）：来自 §8 human-vs-naked 对照实验锁定的题——人类手写代码通过而裸 Agent 失败（或反之），已知能分离强方法与弱方法。不论 pass_rate 高低，强制进入 test。  
   - **Tier 2**（高方差，variance > 0.10）：24 批 baseline 在该题上的表现波动大——有些方法能过、有些不能。方差大天然意味着区分度强。按方差降序优先进入 test。  
   - **Tier 3**（中等，0.05 < pass_rate < 0.95 且 variance ≤ 0.10）：不同方法表现一致但仍有提升空间（没到天花板也没跌到地板）。优先进入 val 作为 held-out 过拟合检测门，余量补入 train。  
   - **Tier 4**（非区分极端，pass_rate ≤ 0.05 或 ≥ 0.95，且 variance ≤ 0.10）：包括"天花板题"（24 批全过或近乎全过）和"地板题"（24 批全败或近乎全败）。所有 baseline 表现一致，方差 ≈ 0，无法区分任何两个方法。全部进入 train。

3. **Per-category 分配流程**  
   每个 category 内按 Tier 顺序依次分配：
   1. 先取该 category 内所有 Tier 1 题放入 test，消耗 test 配额；
   2. 再取 Tier 2 题按方差降序填入 test 剩余配额，填满为止；
   3. Tier 3 题先填满 val 配额，若 test 仍有余量则方差较高的补入，其余进入 train；
   4. Tier 4 题全部进入 train。

### 论文原文（旧描述）
> To evaluate self-evolution without ceiling effects---the Bare agent already passes 87\% of the 158 tasks---and to support held-out gating, we adopt an instance-disjoint \emph{challenge split} (train~98 / val~20 / test~40), in the spirit of EvoAgentBench's ability-supported yet instance-disjoint split~\cite{gao2026evoagentbench}. The split is stratified so that the test set concentrates more discriminative tasks, identified by testbench code length and the number of unique APIs used. Because the validation and test sets are small, every self-evolution evaluation is the mean of \textbf{five} independent runs with its standard deviation.

**中文注释（原）**  
> 为在没有天花板效应的情况下评估自进化——Bare智能体已通过158个任务中87\%——并支持留出门控，我们采用实例不相交的挑战划分（训练98/验证20/测试40），遵循EvoAgentBench的能力支撑但实例不相交划分的精神。该划分经过分层，使测试集集中于更具区分度的任务——以测试台代码长度和使用的唯一API数量为标识。由于验证集和测试集较小，每个自进化评估均为五次独立运行的平均值及其标准差。

### 建议修改（新描述）
> To evaluate self-evolution without ceiling effects---the Bare agent already passes 87\% of the 158 tasks---and to support held-out gating, we adopt an instance-disjoint \emph{challenge split} (train~98 / val~20 / test~40), in the spirit of EvoAgentBench's ability-supported yet instance-disjoint split~\cite{gao2026evoagentbench}. Tasks are allocated within each category by discriminative priority: per-task pass rates and inter-run variances are computed from 24 full-benchmark runs across six LLM backbones under varied harness configurations collected during development. High-variance tasks (inter-run variance $>$ 0.10) fill the test quota in descending variance order, followed by moderate-variance tasks for validation; tasks at both extremes---where all runs consistently pass ($\ge$ 95\%) or consistently fail ($\le$ 5\%)---are assigned to training, as near-zero variance yields no discriminative signal between methods. Because the validation and test sets are small, every self-evolution evaluation is the mean of \textbf{five} independent runs with its standard deviation.

**中文注释（新）**  
> 为在没有天花板效应的情况下评估自进化——Bare智能体已通过158个任务中87\%——并支持留出门控，我们采用实例不相交的挑战划分（训练98/验证20/测试40），遵循EvoAgentBench的能力支撑但实例不相交划分的精神。每题在各category内按区分度优先级分配：基于开发期间收集的六种LLM基座在多种框架配置下的24次全基准运行，计算每道题的通过率与跨运行方差。高方差题目（跨运行方差$>$0.10）按方差降序填入测试配额，中等方差题目填入验证集；两端的题目——所有运行一致通过（$\ge$95\%）或一致失败（$\le$5\%）——归入训练集，因为近零方差无法提供区分不同方法强弱的信号。由于验证集和测试集较小，每个自进化评估均为五次独立运行的平均值及其标准差。

---

## 5. 写侧门控消融实验

### 改动说明
删除原表 IV 中 `Scope Boundary` 和 `Disconfirmation Filter` 这两行。理由如下：

- **Scope Boundary**（`SE_ABLATION_SCOPE_BOUNDARY`）：它是 L0→L1 提取阶段的 prompt-level mechanism。LLM 在生成 scenario entry 时被要求标注 Precondition/Constraint；关掉它只是让 LLM 不标注边界，条目照样蒸馏。它的 ON/OFF 不会改变 L1→Skill 的蒸馏条目数。当前表用"条目数"做指标，对它来说是 wrong metric——ON=OFF 不能说明 gate 无效，只能说明指标不匹配。
  
- **Disconfirmation Filter**（`SE_ABLATION_DISCONFIRM_FILTER`）：它在蒸馏时过滤 disconfirm_count >= 2 的条目。24 题单轮蒸馏中，每条条目至多在 1 个 batch 中被 disconfirm，达不到 2 的阈值，因此开关对条目数逻辑上不可能产生差异。ON=OFF 不能说明 gate 无效，只能说明实验规模不足以评估它。

### 论文原文（含被删除行）

> To examine each gate's contribution, we ablate each write-side gate from Section~\ref{sec:se_distill}--\ref{sec:se_govern} (ground-truth anchoring, failure routing, the contradiction path, the scope boundary, and disconfirmation) by toggling it on and off. Full end-to-end ablation per gate is costly ($\sim$13\,h/round) and sparse in its signal because failure-triggered gates only operate on a few tasks per round. Following the shared-trace-pool design of Trace2Skill~\cite{ni2026trace2skill}, we freeze a pool of 24 distinct failure task traces accumulated across post-split batches and replay only the offline reflection chain, toggling one gate at a time, measuring knowledge quality rather than end-to-end Pass@1. Test failures are used only as inputs to this offline reflection; no knowledge produced from them is injected into any test evaluation, so their inclusion does not constitute test-set leakage. Table~\ref{tab:se_write_ablation} reports entry counts. Because the offline reflection LLM is not perfectly deterministic, the ON column varies by one across gates; we read only the gate-shaped deltas, not single-entry differences.

**原表格（带有待删除的两行）**

| Gate                     | ON | OFF |
|--------------------------|----|-----|
| Ground-Truth Anchoring   | 37 | 48  |
| Contradiction Path       | 37 | 54  |
| Routing                  | 36 | 37  |
| Scope Boundary           | 36 | 36  |   ← 删除
| Disconfirmation Filter   | 37 | 37  |   ← 删除

> The ablation isolates which gates earn their place. Ground-truth anchoring is the strongest: without it, 12 of 24 tasks yield at least one falsely verified entry, because the trace's self-report of success is trusted. The net entry count rises by 11 (from 37 to 48) rather than by 12, because one of the 12 false-verified tasks would have produced no entry under correct anchoring (its pitfall was never generated). The contradiction path trades quantity for precision: disabling it forces those tasks onto the error path, producing 17 more entries but of lower precision, since the error path mines pitfalls from stale, already-repaired errors. Routing itself matters mainly through the contradiction path it enables---disabling it forces all failed tasks onto the success branch, producing no pitfalls at all. The scope-boundary and disconfirmation gates do not trigger on this 24-task pool, so their contribution is left unverified by this ablation.

**中文注释（原）**  
> 消融实验分离了各门控的作用。真值锚定是最强的：没有它，24个任务中有12个产生至少一条假阳性已验证条目，因为轨迹的自报告成功被信任。净条目数增加了11条（从37到48）而非12条，因为12个假阳性验证任务中有一个在正确锚定下不会产生任何条目（其陷阱从未生成）。矛盾路径以数量换精度：禁用它将这些任务强制推入错误路径，产生多17条但精度更低的条目，因为错误路径从不新鲜、已修复的错误中挖掘陷阱。路由本身主要通过其启用的矛盾路径发挥作用——禁用它将所有失败任务强制推入成功分支，完全不产生陷阱。范围边界和证伪过滤门控在此24任务池上未触发，因此它们的贡献在此消融中未被验证。

---

### 建议修改（删除两行后的正文及表格）

> To examine each gate's contribution, we ablate each write-side gate from Section~\ref{sec:se_distill}--\ref{sec:se_govern} (ground-truth anchoring, failure routing, the contradiction path, the scope boundary, and disconfirmation) by toggling it on and off. Full end-to-end ablation per gate is costly ($\sim$13\,h/round) and sparse in its signal because failure-triggered gates only operate on a few tasks per round. Following the shared-trace-pool design of Trace2Skill~\cite{ni2026trace2skill}, we freeze a pool of 24 distinct failure task traces accumulated across post-split batches and replay only the offline reflection chain, toggling one gate at a time, measuring knowledge quality rather than end-to-end Pass@1. Test failures are used only as inputs to this offline reflection; no knowledge produced from them is injected into any test evaluation, so their inclusion does not constitute test-set leakage. Table~\ref{tab:se_write_ablation} reports entry counts. Because the offline reflection LLM is not perfectly deterministic, the ON column varies by one across gates; we read only the gate-shaped deltas, not single-entry differences.

**修改后的表格（删除了 Scope Boundary 和 Disconfirmation Filter）**

| Gate                     | ON | OFF |
|--------------------------|----|-----|
| Ground-Truth Anchoring   | 37 | 48  |
| Contradiction Path       | 37 | 54  |
| Routing                  | 36 | 37  |

> The ablation isolates which gates earn their place. Ground-truth anchoring is the strongest: without it, 12 of 24 tasks yield at least one falsely verified entry, because the trace's self-report of success is trusted. The net entry count rises by 11 (from 37 to 48) rather than by 12, because one of the 12 false-verified tasks would have produced no entry under correct anchoring (its pitfall was never generated). The contradiction path trades quantity for precision: disabling it forces those tasks onto the error path, producing 17 more entries but of lower precision, since the error path mines pitfalls from stale, already-repaired errors. Routing itself matters mainly through the contradiction path it enables---disabling it forces all failed tasks onto the success branch, producing no pitfalls at all.

> **新增修改部分**  
> Two write-side gates are excluded from Table~\ref{tab:se_write_ablation} because the 24-task single-iteration design cannot evaluate them. The Scope Boundary gate operates at the L0-to-L1 extraction stage: it instructs the LLM to annotate each verified entry with task-trace-observable preconditions and constraints. Its effect is on the descriptive precision of individual entries rather than on the number of entries distilled, and the entry-count metric reported in this table does not resolve it. The Disconfirmation Filter accumulates per-entry disconfirmation counts across batches and filters entries that fail in two or more batches; under a single distillation round, no entry can reach the threshold, making the filter structurally inactive regardless of its setting. Validating both gates requires multi-iteration experiments in which knowledge accumulates across rounds---a configuration beyond the scope of this ablation.

**中文注释（修改后完整）**  
> 消融实验分离了各门控的作用。真值锚定是最强的：没有它，24个任务中有12个产生至少一条假阳性已验证条目，因为轨迹的自报告成功被信任。净条目数增加了11条（从37到48）而非12条，因为12个假阳性验证任务中有一个在正确锚定下不会产生任何条目（其陷阱从未生成）。矛盾路径以数量换精度：禁用它将这些任务强制推入错误路径，产生多17条但精度更低的条目，因为错误路径从不新鲜、已修复的错误中挖掘陷阱。路由本身主要通过其启用的矛盾路径发挥作用——禁用它将所有失败任务强制推入成功分支，完全不产生陷阱。  
> 
> 有两个写侧门控未列入表中，原因是24任务的单轮迭代实验设计无法评估它们。范围边界门控运作在L0到L1的提取阶段：它要求LLM为每条已验证条目标注可从任务轨迹中观察到的前置条件和约束。其效果体现在单一条目的描述精度上，而非蒸馏产出的条目数上，本表报告的条目计数指标无法分辨它。证伪过滤门控通过跨批次累积每条条目的证伪计数，并过滤在两个或以上批次中均失败的条目来运作；在单轮蒸馏下，没有条目能达到其触发阈值，因此无论开关状态如何，过滤逻辑在结构上均不会激活。验证这两个门控需要知识跨轮累积的多轮迭代实验——这一配置超出了当前消融实验设计的范围。



# 熊博审稿意见

# ZhuLong (Self-Evolution) 审核简报

## 结论
论文在前序ZhuLong框架上增加受控自进化层，从"代理+文档补丁(3.2pp)"升级为"受控自学习超越人类经验(+14pp)"，实验严谨性大幅提升。核心弱点：SKILL声称无实验支撑、92.4%无置信区间。

## 优点
1. **创新性大幅提升**：三层记忆(L0/L1/L2) + 多重可靠性门控 + 防泄漏检索，构成非显然的系统设计
2. **反直觉发现**：陷阱预注入有害(−8.3pp)、仅名称检索优于完整序列(+5.0pp)——对领域有独立价值
3. **实验严谨性提升**：人类基线(77.5%)、5次运行±stddev、instance-disjoint分割、2×2析因设计
4. **错误分析深化**：111个失败跨5模型按异常类型分类(AssertionError 54.1%)
5. **自进化超越人类**：80.0% vs. 77.5%（+2.5pp），验证门控正确拒绝第3轮回退
6. **文献覆盖全面**：EDA脚本 + 自进化/记忆两条线均覆盖充分

## 关键弱点

| # | 弱点 | 严重性 |
|---|------|--------|
| 1 | **SKILL声称无实验**：摘要/结论提及支持SKILL，全文零SKILL实验 | �� 重大 |
| 2 | **92.4%无置信区间**：仅单次运行，与自进化的5运行标准不一致 | �� 重大 |
| 3 | **两个门控未验证**：scope-boundary和disconfirmation在消融中无触发 | �� 次要 |
| 4 | **挑战测试集仅40任务**：单一EDA域，泛化性待验证 | �� 次要 |
| 5 | **人类基线为单人**：一位工程师的4技能+1规则，代表性有限 | �� 次要 |

## 建议修改

1. �� 补充SKILL评估或从摘要删除SKILL声称
2. �� 补充92.4%的多次运行统计（与自进化标准一致）
3. �� 在正文中承认scope-boundary/disconfirmation的价值未经验证

## 其它建议

- 按场景/复杂度分层报告Pass@1
- 提供2-3个AssertionError失败案例
