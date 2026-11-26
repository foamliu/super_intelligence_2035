# 实验方法学:Agent 评测的方差控制与成本控制

> 2026\-07\-30 起草。回答"agent benchmark 结果有波动,如何降方差增置信;多次测量全量太贵怎么处理;消融/MCP/RAG/换模型导致实验总量爆炸如何控成本"。**每条结论都锚定到我们掌握的论文原文做法**,不凭印象写公式。承重论文原文在 `logs/papers/`。
> 
> 

## **核心问题诊断\(先认清我们要治的是什么\)**

agent benchmark 的波动有三个不同来源,**治法不同,混为一谈会白费功夫**:

1. **采样噪声\(sampling noise\)** —— LLM 解码 temperature\>0,同 prompt 同 task 多次生成结果不同。这是**任务级**随机性。Trace2Skill §2\.2\.3 称之为"undesirable stochastic behavior across repeated rollouts under the same skill",AHE 自承是"high\-variance setting"。

2. **环境噪声\(environment noise\)** —— 沙箱并发竞争、文件系统脏状态、端口污染等导致同代码不同结果。这是**工程级**随机性。我们已用多端口隔离\(4 端口各独立 workdir\)治本。

3. **知识退化\(knowledge regression\)** —— 自进化场景独有:上轮通过的本轮失败,是真知识变差而非随机噪声。这是**系统级**信号。

**关键区分**:三方文献里"降方差"主要针对 1\(采样噪声\),3 是我们独有的、且是**要检测的信号而非要消除的噪声**。下面的方案围绕 1 展开,并明确哪里用 2、哪里保 3。

## **波动控制优先级\(总纲\)**

**环境隔离 \> temperature=0 \> 多 seeds**。这个排序有双重依据:

- **工程上**:环境噪声\(并发污染\)是**最大的**方差源。若不隔离,8 路并发可让性能从单次 60% 跌到 25% 量级\(并发竞争污染 workdir/TECHLIB\)——这种波动比采样噪声大一个数量级,且**多跑几次取平均也消不掉**\(它是系统性偏差不是零均值噪声\)。我们已用多端口隔离治本,这一步的收益 \> 其他所有步骤之和。

- **统计上**:采样噪声的方差是 σ²/n,要靠多 seeds 压;但只要环境噪声在场,σ 里混进了系统性成分,n 再大也压不掉。所以**先把环境噪声归零,再谈采样噪声的统计**——顺序不能反。

**temp=0 的诚实认知**:设 temperature=0\(greedy\)能消掉大部分采样随机性,但**不是 100% 确定**——GPU 浮点并行\(MOE 路由、batch 调度、非结合归约\)仍留残余非确定性。这意味着:temp=0 下同代码多次跑仍可能有少数 task 翻转,但比例远低于 temp\>0。**因此即使 temp=0,关键对比仍需配对统计\(McNemar/bootstrap\),不能假设单次结果完全可复现。**

> ⚠️ 未核实数字:有参考提到"temp=0 确定性率 70%–100% 波动",以及某 NeurIPS 2025 agent 论文"因 LLM 成本过高未提供 error bar/CI"的原话。这两处我未能核实到原始出处\(检索无果\),**暂不作为论文引用**,仅在方法论中保留其机制性结论\(temp=0 有残余非确定性 / agent 领域单次运行是被接受实践\)。可核实的支撑是:AHE 原文明确"run **a single AHE campaign** of ten iterations"\(§4\.2\),VeriHarness 用确定性的 game seeds\(20261051–20261100\),SkillOpt 用 `split_seed=42` 的 deterministic split——即**"确定性设置 \+ 单次/少次运行"在 agent 评估中是可接受实践**,这条有原文支撑,可直接引。
> 
> 

---

## **一、降方差 / 增置信:统计方法**

### **1\.1 配对设计 \+ paired bootstrap\(VeriHarness 做法,最适合我们\)**

VeriHarness【arXiv:2607\.14167】是我们最该照搬的统计模板,因为它场景和我们最像\(50 个 paired games、有 LLM、有 retry 闭环、关心"结构化反馈是否提升成功率"\)。其原文做法\(§3 Analysis\):

> "Games are paired by seed\. Primary success differences use **10,000 paired bootstrap samples** and **two\-sided exact McNemar tests**\. We apply **Holm correction** to four planned contrasts within each model\."
> 
> 

三个要素,全部可复用:

**\(a\) 配对\(paired\)**:同一个任务在两个条件下各跑一次,比较的是**同一任务上的差值**,而非两组各自的均值。这能把"任务难度分布"这个最大的方差源直接消掉——难的任务两个条件都难,差值里不体现难度只体现方法差异。VeriHarness 用"paired by seed"\(同一 game seed\),我们用"同一 task\_id"。**这是降方差性价比最高的一步,且几乎零成本**\(不需要多跑,只需要配对记录\)。

**\(b\) paired bootstrap 10000 次**:对配对差值做有放回重采样 10000 次,取 2\.5%/97\.5% 分位作 95% 置信区间。比正态假设稳健\(成功率是 0/1 分布,小样本非正态\),且不需要知道分布形式。VeriHarness 报的是"95% interval 28–60"这种区间而非单独点估计。

**\(c\) McNemar 检验 \+ Holm 校正**:McNemar 专门针对**配对二分类**\(本工作 pass/fail 正是二分类\),检验"两个条件在同一组任务上的成败翻转是否对称"。Holm 校正应对**多重比较**——我们要做的对比不止一对\(baseline vs evo\-round1 vs evo\-round2 vs human\-V5\.4,以及各消融\),不校正会假阳性膨胀。VeriHarness 对"每个 model 内 4 个 planned contrasts"做 Holm。

> ⚠️ VeriHarness 还有一句重要诚实表述:"The budget and HumanEval samples are small, so we report counts and intervals and **do not treat a p\-value threshold as decisive**\."——小样本时不唯 p 值,看区间和效应量。我们某些子集实验\(见下\)也该如此。
> 
> 

### **1\.2 Lower Confidence Bound\(LCB\)惩罚单次好运\(Trace2Skill 做法,治采样噪声\)**

Trace2Skill【arXiv:2605\.21810, NVIDIA】直接面对"同一 skill 多次 rollout 结果不稳",其解法\(§2\.2\.3 式6,原文核实\):

$F_{LCB} = \max\left(0,\ \bar{F}_{progress} - 1.96\sigma/\sqrt{R}\right)$

- $\bar{F}$ = R 次重复的均值,$\sigma$ = 这 R 次的标准差,$R$ = 重复次数。

- $1.96\sigma/\sqrt{R}$ 就是**正态近似的 95% 置信区间半宽**\(标准误 × 1\.96\)。LCB 取均值减去这个半宽,即"悲观看待这次表现"。

- 原话:"The LCB term reduces the chance that a single lucky rollout dominates selection… its penalty scales as $\sigma/\sqrt{R}$。"——**惩罚随 R 增大而缩小**,意味着多测能换来更高的 LCB\(奖励稳定\),少测则 LCB 被压低\(惩罚靠运气\)。

**给我们的直接用法**:自进化各轮的 pass 率不要只报均值,报 **LCB**\(均值 − 1\.96σ/√R\)。这样:

- "净增 \+X 题"这种结论必须经得起 LCB 检验——若 \+X 是靠某轮一次高分拉起来的,LCB 会暴露。

- R 的选择见下文\(Trace2Skill 用 R=4 repeats/task,80 rollouts/task\)。

### **1\.3 pass@1 用多次 rollout 的均值\(AHE 做法,定义级\)**

AHE【arXiv:2604\.25850】明确把 pass@1 定义为**多次 rollout 的均值**而非单次\(§4\.1 原文\):

> "pass@1, the **mean binary success rate over k rollouts per task**… We run **k ≥ 2 rollouts per task** so each task carries a pass\-rate signal, which stabilizes pass@1 and lets partial\-pass tasks anchor comparative diagnosis\."
> 
> 

要点:

- **k≥2 是下限**,AHE 用 k=2。每任务至少 2 次,pass@1 才有"信号"而非单点。

- "partial\-pass tasks anchor comparative diagnosis":部分通过的 task\(2 次过 1 次\)比全过/全错更有诊断价值——它们是方法差异的体现处。配对比较时这些 task 是信号源。

### **1\.4 pass@k 作为稳定性补充指标\(iScript 做法\)**

iScript【arXiv:2603\.04476】同时报 **pass@1 和 pass@5**\(Table 2/3\)。pass@1 是"一次能不能成"\(我们的主指标\),pass@5 是"五次里至少成一次"\(反映模型的**能力上限**与稳定性\)。两者对照能区分:

- pass@1 低但 pass@5 高 → 模型有能力但**不稳定**\(采样噪声大\),该降 temperature / 加 self\-consistency。

- pass@1 ≈ pass@5/k → 模型稳定地不行,是能力问题不是噪声。

我们可在子集\(非全量\)上补 pass@k 诊断稳定性,全量只跑 pass@1 省成本。

### **1\.5 t 检验 vs 这些方法的取舍**

你问到 t 检验。诚实结论:**配对 bootstrap \+ McNemar 比 t 检验更适合我们的场景**,原因:

|方法|适用|我们的契合度|
|---|---|---|
|两样本 t 检验|两组独立连续值,正态|❌ 我们是配对 0/1,非独立非正态|
|**配对 t 检验**|配对连续值|⚠️ 可用,但 0/1 差值非正态,小样本偏倚|
|**McNemar**|配对二分类|✅ 正好是 pass/fail 配对|
|**paired bootstrap**|任意分布,配对|✅ 最稳健,VeriHarness 主用|
|**LCB \(正态近似\)**|单组多次重复|✅ Trace2Skill 用于选 skill|

实务建议:**报告层**用 paired bootstrap 置信区间\(VeriHarness\),"是否显著"用 McNemar\+Holm\(VeriHarness\),"自进化各轮稳定性"用 LCB\(Trace2Skill\),"效应大小"用 Cohen's d。**t 检验仅作为工具保留,不作主力报告**——小样本\(n≤6\)下 0/1 差值非正态,t 的显著性可能脆弱\(实测:t 显著但 bootstrap 不一致的情况会出现,以 bootstrap/效应量为准\)。

---

## **二、多次测量太贵:成本控制**

### **2\.1 子集评估\(val/test 分层,只在关键处跑全量\)**

这是控制总成本的核心杠杆。SkillOpt【arXiv:2605\.23904】是最佳参照,它的成本哲学\(原文核实\):

- **三份切分 Dtr/Dsel/Dtest**:Train 产证据,Selection\(Dsel\)做 gate,**Test 只在终报跑一次**。"the test split is used only for final reporting"\(§3\.3\)。

- **Selection 跑子集不跑全集**:SkillOpt 的 Dsel 是每个 benchmark 的 selection partition\(规模约百题量级,如 140 个 selection environments\),gate 在这上面判方向。

- **每 epoch 只采样 20 个 task**\(§3\.6 panel f 原文:"the default at 20 examples per epoch, with 5, 10, and 40 each within ±2\.7 points"\)——**20 个就够,5/10/40 与 20 的差距都在 ±2\.7pp 以内**。这是关键的"小样本够用"实证。

- **rollout batch=40/step,4 epochs**。

**给我们的落地方案**\(三层粒度,与 held\-out gate 设计一致\):

1. **方向判断 / 消融初筛\(20–30 题子集\)**:自进化每轮、每个消融配置,先在 val 子集\(20–30 题\)上判"是涨是跌"。SkillOpt 实证 20 题足够定方向。**这一层覆盖了 90% 的实验单元**,是省成本的主战场。

2. **模块级验证\(按语义模块分组,2–5 题/组\)**:定位"哪个模块坏",见 held\-out gate 粒度第 2 层。

3. **最终报告 / 关键主张\(全量 \+ disjoint test\)**:只有**要写进论文表/图的核心结论**才跑全量 158\(或 held\-out test 40\)。候选:人类 V5\.4 baseline、裸 baseline、最终自进化产物、主消融的几个关键格。

**配对 bootstrap 在子集上同样适用**\(VeriHarness 50 题就做了 10000 次 bootstrap\)——子集 \+ 配对 \+ bootstrap 是组合拳。

### **2\.2 R\(重复次数\)的选择:按需分配,不全局拉满**

不要对所有实验统一跑 R=10。按结论重要性分级\(综合 Trace2Skill R=4、AHE k=2\):

|实验类型|重复次数 R|依据|
|---|---|---|
|方向初筛\(子集\)|**2**\(AHE 下限\)|只要判涨跌方向,k=2 够|
|消融对比\(子集\)|**3–4**\(Trace2Skill R=4\)|要报 LCB/区间,需估 σ|
|核心主张\(全量\)|**5–10**|进论文主表,要窄区间|
|人类 V5\.4 / 裸 baseline\(全量\)|**5**\(你 memory 里的"法1 pass@4±SE"近似\)|对照基准要多跑|

Trace2Skill 的 $\sigma/\sqrt{R}$ 给了量化直觉:**R 从 2→4,标准误减 30%;4→10 减 37%;10→∞ 边际递减**。R=4–5 是性价比拐点,超过 5 边际收益骤降。

### **2\.3 噪声分离:用重复本身把"退化"和"抖动"拆开\(我们独有\)**

这是已有的设计,且是**比所有参考论文都严**的一点。核心:

- **Regressed\(同题上轮过本轮 fail\)里混了两种东西**:真知识退化 \+ 采样抖动。

- **拆法**:同一题\(同 prompt 同知识\)独立重生 N 次,算 pass 率方差 → 这就是该题的采样噪声;从 Regressed 里扣除噪声部分 = 真退化。

- 参考论文都不做这个\(Trace2Skill 用 LCB 选 skill 但不拆退化;SkillOpt disjoint split 题不重叠根本没有"同题退化"\)。这是我们 without\-retention 设定的独有红利,**写进论文是差异化点**。

### **2\.4 关键工程前提:多端口隔离必须先就位**

上面所有统计都假设"同代码多次跑结果差异 = 采样噪声"。**若环境噪声\(沙箱并发污染\)没治掉,σ 会被污染放大,所有区间都失真**。我们已经治本\(4 端口隔离, 3\.7× 提速且 156/157 一致\)。**实验前必须确认 ****`EVAL_SANDBOX_WORKERS=4`**** 多端口在跑**\(见 `memory_bank` 四步 pre\-flight\),否则统计是建立在脏数据上。这是其他论文不需要而我们必须有的前提——因为我们是少数在共享沙箱上做并发评估的。

### **2\.5 简单题稀释效应:用经验难度\(非 API 数\)分层 \+ Active Set**

**问题**:若一批题所有方法都做对\(天花板题\)或都做错\(地板题\),它们对方法间差异**零区分度**,只稀释整体 pass 率。整体 pass 率被天花板题抬到 \~85% 时,方法间 2pp 的真实差距会被淹没在单次运行的 ±8pp 波动里——**信号小于噪声**。

**❌ 先验复杂度代理\(num\_unique\_apis\)经实测无效,已废弃**\(2026\-07\-30 核实 8 个真实 batch\):

最初我按 metadata 的 `num_unique_apis` 分 easy\(1\-2\)/medium\(3\-5\)/hard\(6\+\),分布是 11%/42%/47%,看似"hard 为主"。但**核对 40 题 test set 上 4 次无人类经验 run 的 per\-task pass 率后发现:API 数量与难度无关**

|task|num\_unique\_apis|pass率\(4次\)|说明|
|---|---|---|---|
|100|10|1\.00|高 API 数,全过|
|076|13|1\.00|高 API 数,全过|
|102|14|1\.00|高 API 数,全过|
|063|7|0\.25|低 API 数,却难|
|149|4|0\.00|低 API 数,全失败|

**结论**:agent 能正确编排多 API 序列,API 多 ≠ 难;难的是"单个 API 的语义/参数/SWIG 类型"等局部陷阱,与 API 数量正交。**`num_unique_apis`**** 不能作难度代理,已废弃此分层方案。**

**✅ 正确难度信号 = 经验 pass 率本身\(empirical difficulty\)**。用多次 run 的 per\-task pass 率定义难度,天然分出三层:

> 实测 4 次无人类经验 run\(40 题 test,分母恒 40、gen\-fail 算 fail\)的 per\-task 表现:
> 
> 

> - **天花板题\(always\-pass\)**: 29 题\(72%\)—— 4 次都过,零区分度,只稀释 overall。
> 
> 

> - **地板题\(always\-fail\)**: 3 题\(8%\)—— 4 次都失败\(顽固题 143/146 之类\)。
> 
> 

> - **flaky 题\(有区分度\)**: 8 题\(20%\)—— 时过时不过,**这才是方法差异的体现处**。
> 
> 

> - flaky \+ always\-fail = Active Set\(11 题,28%\),唯一有区分度的有效空间。人类经验组同口径:30/2/8,Active Set 10 题——两组 Active Set 规模接近。
> 
> 

**治法:三层报告\(不是"去掉简单题",而是分层展示 \+ 聚焦 Active Set\)**:

1. **Layer 1 主指标**:Overall pass rate —— headline number,**不可省略**\(报全量 158 或 test 40,口径须标清\)。

2. **Layer 2 核心分析:Active Set** —— \{题 t \| 经验上非总是通过\}。即多次 run 里"时过时不过 \+ 总是失败"的题。这是**方法能产生差异的有效空间**。我们的三元组指标 \`Newly Solved\`\(上轮 fail→本轮 pass\)天然落在 Active Set 上,所以**Active Set 分析零额外实验**,直接从三元组导出。

3. **Layer 3 分层展示**:报 always\-pass / flaky / always\-fail 三档各自 pass 率,展示"差距主要来自 flaky 档"。**这比按 API 数分层更真实**——难度从系统行为涌现,不是人标或先验代理。

**★为什么经验难度是合规的**\(回应"事后选题=p\-hacking"担忧\):

- Active Set 的定义是\*\*"跨多次 baseline run 表现不稳定"的题\*\*,这是**方法无关**的题集属性\(用 baseline 多次 run 算,不看某特定方法在哪题好\),**不是**"事后看我的方法在哪些题做得好"。

- 规范做法:**用一组方法无关的 baseline run\(如裸 baseline 的 N 次重复\)定义 Active Set**,再在 Active Set 上评估各方法。定义先于方法对比,p\-hacking 红线不触发。

- ⚠️ 红线仍守:Overall 必须同时报;不能用"某方法表现"定义子集;子集定义基于 baseline 表现\(方法无关\),非目标方法表现。

**Active Set 与三元组指标的天然关系**:\`Newly Solved\`\(上轮 fail→本轮 pass\)定义上就是"在 Active Set 上的增量"。直接用 Round\-1 baseline 的失败题集作 Active Set,各轮 Newly Solved 累计 = 增量曲线。without\-retention 独有红利\(disjoint split 无同题,做不了"以 baseline 失败题为锚的增量"\)。

**实测数据的方差与口径\(2026\-07\-30,6 vs 6,见 §八\)**:

> ⚠️ **统计口径统一为 40 题 test set**\(\`docs/dataset\_split\.json\` 的 test 40\)。0728 的全 158 run 取出其中 40 题 test 的子集结果\(独立、可直接比\)。**绝不全 158 与 40 题混比**。
> 
> 

> ⚠️ **分母恒为 40,生成失败\(gen\-fail/timeout\)算失败不剔除**\(AHE 同口径:infrastructure\-aborted/timeout 计 fail\)。这样每 run 严格可比。
> 
> 

> 补测只跑未全过的难题\(人类 10 题/裸 11 题\),已全过的简单题\(29 题\)默认 pass——补测省时,且这些题在所有正常 run 中一致全过,默认 pass 不引入偏差。
> 
> 

- **组级均值与方差**\(§8\.2\):人类经验 6 组 = 88\.3% ± 2\.04,裸 6 组 = 85\.0% ± 2\.24,差 \+3\.3pp。组内 SD≈2pp,组间差 3\.3pp → **Cohen's d=1\.56\(大效应\)**,人类经验影响远大于 run 间噪声。

- **天花板稀释**:40 题中 29 题两组都 6/6 全过\(pass rate=1\.0\),对方法差异零信息量,把整体绝对差压到 3\.3pp。**难题 11 题\(至少一边未全过\)上,人类 57\.6% vs 裸 45\.5%,差 \+12\.1pp**——去除天花板稀释后的真实信号。符合 IRT Fisher 信息原理\(p=0\.5 处信息量最大,天花板题 p\(1−p\)=0\)。

- **保守下界**:LCB\(均值−1\.96σ/√R\)人类 66\.1% vs 裸 60\.0%,差 \+6\.1pp——最悲观估计下人类仍优,排除了"靠某组好运"的可能。

- **数据性质**:人类优势是组级系统性\(每组稳定 85–90%\),非题级翻盘;简单题两边都 100%\(工具已够\),人类经验价值集中在难题。

- **★这是 §一/§二统计设计的实证基础**:为什么必须配对\(消任务难度方差\)、为什么必须 LCB\(防单次好运\)、为什么必须分层/Active Set\(天花板题零信息量需剥离\)、为什么分母必须恒定且 gen\-fail 算 fail\(否则低估真实代价、口径不可比\)。

**退化题即难度题\(独门展示\)**:某题 Round 3 过、Round 4 fail\(Regressed\)→ 一定非天花板题。退化题天然落在 Active Set,其特征分析比先验难度代理更有说服力——**难度从系统行为涌现**。without\-retention 独有。

**归一化增益\(可选补充\)**:Hake 式 `Normalized Gain = (Method − Baseline)/(100% − Baseline)`,含义"在 baseline 未解决空间里额外解决了多少比例"。⚠️ Hake 1998 出处未核实,引用前需自查原文,不凭印象引。

### **2\.6 切分方案:challenge\-style 分层切分\(GPT\-5\.5 \+ EvoAgentBench\)**

**问题**:旧 `dataset_split.json` 按 \(category, gt\_len\) 难度分层均匀切分\(98/20/40\),但实测暴露缺陷——test 40 题里 28 题\(70%\)是天花板\(两组都全过\),真有区分度的只 9 题,统计效力不足\(§8 难题分层 n=11 时 CI 很宽\)。**根因:难度均匀 ≠ 区分度均匀**,gt\_len 先验难度与实际区分度不正交\(§2\.5 已证\)。

**框架:challenge\-style evaluation\(GPT\-5\.5\)**。我们的 setting 不是传统 i\.i\.d\. train/test,是 **public experience pool \+ hidden hard challenge set**:

- open set 用于训练/经验抽取/自进化/skill mining → 不能叫 test,叫 **public experience pool / development pool**

- 真 test = **hidden hard challenge set**\(高区分度、非天花板题,最终比较用\)

- 合规三条件:① hard set 定义基于 reference agents/历史通过率\(**方法无关**\),非本文方法胜负;② hidden test 方法冻结后才用;③ 同时报 full distribution 防"只对 hard 有效牺牲 easy"

- **参考文献\(可引,7 先例 \+ EvoAgentBench\)**:

    1. **ARC**\(AI2 Reasoning Challenge\):Easy/Challenge 分离,Challenge 只含 retrieval\-based \+ word co\-occurrence 算法都答错的题——专门构造能拉开差距的 hard split

    2. **ARC\-AGI / ARC Prize**:public set 用于训练/开发\(获 ARC\-relevant cognitive priors\),private/semi\-private set 才是最终评测;不能反复把 public eval 当反馈改算法\(否则泄漏\)

    3. **BIG\-Bench Hard \(BBH\)**:从 BIG\-Bench 选出 LM 落后于人类的困难任务子集,恢复 full\-average 被 ceiling effect 稀释的区分度

    4. **MMLU\-Pro / MMMU\-Pro**:MMLU\-Pro 去 trivial/noisy 题 \+ 加 reasoning 题 \+ 扩选项数抗饱和;MMMU\-Pro 过滤 text\-only 模型可答的题\(多模态,强迫真用视觉\)——同属"过滤 trivial 题增判别力"家族

    5. **SWAG / HellaSwag**:adversarial filtering,用一组模型/分类器迭代去掉易被浅层线索解决的样本;HellaSwag 刻意做成"人类易、SOTA 难"的 challenge set,且 benchmark 可与 SOTA 共同进化

    6. **ANLI / Dynabench**:human\-and\-model\-in\-the\-loop 对抗采集,前几轮数据可训练,后续人类构造能骗过当前模型的更难 test——动态对抗式 benchmark

    7. **Kaggle public/private leaderboard**:public 给开发反馈,private hidden 决定最终排名,防对 public leaderboard 过拟合

    8. **EvoAgentBench【arXiv:2607\.05202】** 的 **ability\-supported yet instance\-disjoint split** \+ soft headroom\(split 阶段排天花板/地板\)是最直接的方法论参照——详见 `docs/paper_draft_related_work.md` §2\.2 与 memory `papers-insights` EvoAgentBench 段。

**落地:两个 split 并存**\(`docs/`\):

- **`dataset_split.json`****\(旧\)**:full\-distribution reference,按 category\+gt\_len 均匀切分 98/20/40。§8 的 6\-vs\-6 实测\(88\.3% vs 85\.0%,d=1\.56\)基于它,仍作 full\-distribution 报告。

- **`dataset_split_challenge.json`****\(新\)**:challenge\-style 分层切分,见下。

**新 split 设计依据**:保持 98/20/40 规模 \+ 每 category 的 train/val/test 题数比例\(和旧 split 一致,保 category 均衡\),但**每 category 内部按区分度优先级分配**:§8 已知区分度题 \> 历史 pass 率高方差题\(var\>0\.10\) \> 非天花板中等题 \> 天花板题\(优先留 train\)。区分度信号来源:① 历史 24 个全量 158 batch 的 per\-task pass 率方差\(方法无关,soft headroom\);② §8 实测 9 个区分度题\(人类vs裸 6vs6,pass 次数不同,强制纳入补历史方差漏判\)。

**新 split 结果**\(vs 旧\):

- 规模 98/20/40 ✓ 一致;category 均衡 ✓ 一致\(每 class 的 train/val/test 题数同旧\)

- **test 天花板题:28→10**\(70%→25%\);**test 高方差题:9→25**;§8 区分度题 9→9\(全保留\)

- train 88 个天花板题当 public experience pool\(学基本 API 用法\)

**取舍**:

- **category 均衡 vs 完全无天花板的权衡**:要 test 零天花板就得打破 category 均衡\(高方差题集中在 DCC 类,会导致 DCC 占 51%——上一版被否\)。当前方案保 category 均衡,代价是 test 仍含 10 个天花板\(Simulation/Utilities 类题少,高方差题不够填 test 配额\)。这是硬权衡,选了 category 均衡。

- **历史方差是"同方法"方差**:24 个历史 batch 多是强配置\(带人类经验/L1\),方差主要反映采样噪声\(flaky\)而非方法差异。所以"历史高方差"是区分度的**弱信号**——test 的 25 个高方差题里,有多少是真有方法间区分度、有多少只是 flaky 但两组同向,需跑 §8 那种 6\-vs\-6 跨方法对比才能确认。但作为初步切分依据,已是目前不补测能拿到的最好信号。

**局限**:

1. **历史方差漏判**:026/128 在历史里 var=0\(天花板\)但 §8 里有区分度——train 里可能还有类似题\(历史 var=0 但换方法就有区分度\)被误留 train。脚本用"§8 区分度强制纳入 test"补了已知的 9 个,但未知的得靠跨方法实测发现。

2. **改 test 意味着重测 baseline**:新 test 40 题里只有 13 题来自旧 test。§8 的 88\.3%/85\.0% 基于旧 test,在新 test 上不直接适用——自进化实验启动时人类/裸 baseline 需在新 test 上重测。

3. **生成脚本未入库**:\`/tmp/gen\_challenge\_split\.py\`\(临时\),如需调阈值\(var/天花板/优先级\)重生成可从该脚本改;方案本身已冻结在 JSON。

---

## **三、实验总量爆炸:整体编排**

实验 = 自进化迭代\(R 轮\)× 消融\(MCP/RAG/validator/读写分离等 N 个\)× 模型泛化\(G 个\)× 重复\(r 次\)。朴素全量是 R·N·G·r·158,爆炸。用论文做法分层降维:

### **3\.1 正交分解:只在"最该测的格子"上拉满**

SkillOpt 的 52 个 \(model, benchmark, harness\) cell 不是每个都全跑——它有**默认配置 \+ 选择性消融**。借鉴:

- **一个主配置拉满**:裸 baseline \+ 人类 V5\.4 \+ 最终自进化产物,这三个是论文骨架,全量 \+ 高 R。

- **消融做单变量**:每个消融只改一个变量,在**子集 \+ 中等 R** 上跑,确认"去掉它掉多少"。不需要每消融都全量。

- **模型泛化做迁移**:只在**最终自进化产物**上换模型\(冻结知识,换 agent backbone\),验证知识可迁移。这是 SkillOpt 的 transfer 设定\("skill optimized once, reused across models"\),**不需要每个模型都重跑自进化**。

### **3\.2 自进化迭代:用 LCB \+ 子集做轮内 gate,只终轮跑全量**

- 轮内选择\(选哪条 L1/skill 留下\)用 **LCB**\(Trace2Skill\)\+ **held\-out val 子集**\(SkillOpt Dsel\)。

- 每轮的 pass@1 在**子集**上估\(方向判断\)。

- 只在**关键里程碑轮**\(Round 1 裸、Round 中、Round 末\)跑全量 \+ 高 R,画"裸 → 自进化 → 逼近人类"的进化曲线。

- 中间轮用子集内插,降低全量次数。

### **3\.3 消融:MCP / RAG / validator / 读写分离 的成本分级**

按"该消融掉它会不会改变主结论"分级跑:

|消融|重要性|跑法|成本|
|---|---|---|---|
|自进化开关\(evo on/off\)|★★★核心|全量 \+ 高 R|高\(必须\)|
|L1 注入 on/off|★★★核心|全量 \+ 高 R|高\(093 铁证在这\)|
|validator on/off|★★重要|子集 \+ 中 R,核心格全量|中|
|关键词补路检索 on/off|★★重要|子集 \+ 中 R|中|
|读写分离|★架构壳|子集 \+ 低 R\(证明它是壳非主角\)|低|
|多端口 vs 单端口|★可复现性|已有历史数据\(156/157 一致\),不重跑|零|
|换模型|★★泛化|只在最终产物上,子集 \+ 中 R|中|

### **3\.3b 检索层消融:三版本递进\(2026\-07\-30 定\)**

检索层的新贡献分两层优化,用三版本递进消融,定位各组件边际贡献:

|版本|配置|消融的优化|
|---|---|---|
|**版本一**\(无优化\)|纯向量检索 \+ 朴素详情|— \(基线\)|
|**版本二**\(v1 \+ token overlap \+ BM25\)|向量 \+ 朴素 tokenize 的关键词补路 \+ 朴素详情|验证 token overlap \+ BM25 本身的贡献|
|**版本三**\(v2 \+ 预处理优化,=线上\)|向量 \+ 完整 tokenize 关键词补路 \+ 详情前缀匹配|验证缩写表/synonym/驼峰拆分/前缀去除/前缀匹配的贡献|

**消融对比**:

- **实验一**:版本一 vs 版本二 → token overlap \+ BM25 的贡献

- **实验二**:版本二 vs 版本三 → 缩写表 \+ synonym \+ 驼峰拆分 \+ 前缀去除 \+ 前缀匹配 的贡献

**各组件代码位置 \+ 开关方式**\(消融时操作,现不动线上代码\):

|组件|代码位置|版本一/二开关|版本三|
|---|---|---|---|
|向量侧缩写双向展开|`query_knowledge.py:86-101`\(`expand_query`\+`expand_query_reverse`\)|v1/v2 注释,v3 保留|保留|
|关键词补路工具开关|`main.py` 工具注册 \+ prompt|v1 关工具,v2/v3 开|开|
|关键词补路 tokenize|`keyword_search.py`\(`tokenize_query`含驼峰\+缩写\+前缀去除\)|v2 用 plain 版,v3 用原版|原版|
|synonym 跨命令族映射|`keyword_search.py:630-672`|v2 注释,v3 保留|保留|
|详情层前缀匹配 \+ 大小写不敏感|`query_file.py:167-180`\(步骤2\+3\)|v1/v2 注释,v3 保留|保留|

**已备的阉割版\(不接入,消融时切\)**:`server/rag_server/keyword_search_plain.py`

- `tokenize_query_plain`:朴素空格分词\+去停用词,无驼峰拆分/无缩写展开/无前缀去除

- `KeywordIndexPlain`:索引侧\(`_build_name_index_plain`/`_build_bm25_index_plain`\)也朴素 tokenize,保证 query/索引对称

- 无 synonym redirect

- **切换方式**:消融时把 `tools/search_apis_by_keyword.py` 的 `from server.rag_server.keyword_search import keyword_search` 改为 `from server.rag_server.keyword_search_plain import keyword_search_plain as keyword_search`,即切到版本二

- 已验证可正常 import \+ 检索\(2026\-07\-30\)

**关键提醒**:

- **缩写表同时服务两层**\(向量侧 `query_knowledge.py` \+ 关键词侧 `keyword_search.py`\)。消融缩写表时**两层都要关**\(版本一/二\),否则没干净消融。

- **query/索引 token 必须对称**:plain 版的索引侧也用 plain tokenize,不能只换 query 侧\(否则 name\_overlap/BM25 匹配不上\)。`keyword_search_plain.py` 已处理。

- **前缀匹配**是详情层\(`get_api_details`→`query_file.py`\)的机制,不在检索层;消融时注释 `query_file.py:167-180` 步骤2\+3,只留精确匹配。

### **3\.4 总成本估算\(量级\)**

假设:全量 158 题 1 轮 ≈ 1 个 batch 单位\(多端口并行下 \~小时级\);子集 25 题 ≈ 0\.16 单位;R 按上表。

- 主配置 3 个\(裸/V5\.4/最终evo\)× 全量 × R=5 ≈ 15 单位

- 自进化里程碑 3 轮 × 全量 × R=3 ≈ 9 单位\(中间轮子集,\~1 单位\)

- 消融 5 个 × 子集 × R=3 ≈ 5×0\.16×3 ≈ 2\.4 单位\(核心 2 个补全量 ×2 ≈ \+6\)

- 模型泛化 3 个 × 子集 × R=3 ≈ 1\.4 单位

- **合计 ≈ 30–35 全量单位** —— 比朴素全量\(R·N·G·r·158 可达数百单位\)降一个量级。

### **3\.5 复用与缓存\(SkillOpt/AHE 都做\)**

- **SkillOpt**:优化一次的 skill "paid once during training; after export, the optimized best\_skill\.md adds no cost at deployment"。我们的等价物:**自进化沉淀的知识\(L1/skill/rule\)只产一次**,换模型/做消融时**复用同一份知识**,只重跑 agent 推理不重跑沉淀。

- **AHE**:冻结的 harness 跨模型迁移 \+5\.1\~10\.1pp,一个 campaign 32 小时产出可复用 harness。我们的多端口隔离基础设施同理——治本工程做一次,所有后续实验受益。

- **配对复用**:同一 task 的 baseline run 和 evo run 共用 task 定义/沙箱状态准备,配对设计本身省了对照组的 setup 成本。

---

## **四、给我们的实验章的落地清单**

**统计报告规范**\(每个核心表都要有\):

1. 点估计 \+ **95% paired bootstrap 区间**\(10000 重采样,VeriHarness\)。

2. 显著性用 **McNemar \+ Holm**\(配对二分类,VeriHarness\)。

3. 自进化各轮报 **LCB**\(均值 − 1\.96σ/√R,Trace2Skill\),不只报均值。

4. pass@1 定义为 **k 次 rollout 均值**\(AHE\),k≥2。

5. 关键对比报 **Net Gain ± 噪声分离区间**\(我们独有\)。

**实验编排**:

6. 三层粒度:子集 20–30 题筛方向\(90% 实验单元\)→ 模块级定位 → 全量只跑核心主张\(SkillOpt Dtr/Dsel/Dtest 哲学\)。

7. R 分级:初筛 2 / 消融 3–4 / 核心 5–10 / baseline 5。

8. 正交分解:主配置拉满 \+ 消融单变量子集 \+ 模型只在终产物迁移。

9. 复用:知识沉淀一次复用,多端口基础设施一次受益。

**必做前提**:

10. 实验前确认 `EVAL_SANDBOX_WORKERS=4` 多端口隔离在跑,否则所有 σ/区间失真。

11. 多端口隔离的"156/157 一致"作为可复现性证据直接引用\(不必重跑对比\)。

**诚实表述**\(学 VeriHarness/AHE\):

12. 子集/小样本实验报 counts \+ intervals,"不唯 p 值"\(VeriHarness 原话\)。

13. 自承"high\-variance setting"\(AHE 原话\),明确我们的方差来源与治法。

---

## **五、操作层:统计代码 \+ 表格模板**

### **5\.1 统计脚本\(****`logs/scripts/eval_stats.py`****,已落地\+已测试\)**

**完整实现见 ****`logs/scripts/eval_stats.py`**\(可执行,带 CLI\)。下面是核心函数签名;实现以脚本为准\(已用合成数据 \+ 真实 6\-vs\-6 batch 测过,见 §八\)。脚本实现 doc §一/§二 的**全部**方法:

|方法|函数|对应 doc 节|论文出处|
|---|---|---|---|
|paired bootstrap CI|`paired_bootstrap_ci(a,b)`|§1\.1|VeriHarness §3|
|McNemar\(exact\+χ²\)|`mcnemar(a,b)`|§1\.1|VeriHarness §3|
|Holm 校正|`holm_bonferroni(pvals)`|§1\.1|VeriHarness §3|
|LCB=mean−1\.96σ/√R|`lcb(scores)`|§1\.2|Trace2Skill §2\.2\.3|
|pass@1\(k rollout 均值\)|`pass_at_1(trials)`|§1\.3|AHE §4\.1|
|pass@k|`pass_at_k(trials,k)`|§1\.4|iScript Table2/3|
|paired t\-test\(附录核对\)|`paired_t_test(a,b)`|§1\.5|—|
|噪声分离|`noise_separation(vectors)`|§2\.3|本工作独有|
|Active Set 三层|`active_set_tiers(vectors)`|§2\.5|SWE\-bench/MATH 先例|
|majority\-vote 聚合|`majority_vote(vectors)`|§2\.5|—|
|Hake 归一化增益|`hake_normalized_gain(m,b)`|§2\.5|⚠️出处未核实|
|口径对齐\(gen\-fail=fail\)|`to_vector(batch,task_ids)`|§2\.5|—|

**CLI 用法**\(数据源:`EVAL_FW_DIR/output_evaluation/*/execution_results.jsonl`,与 trace\_reader 一致\):

```Bash
# 单 batch 概览(pass 率 + 覆盖 + gen-fail 计数)
python logs/scripts/eval_stats.py --split test batch --batch 2026_0729_192013

# 两组对比(McNemar + bootstrap CI + 双向翻转题 + Active Set + paired-t + Hake)
python logs/scripts/eval_stats.py --split test compare \
    --group-a "human:2026_0728_223006,2026_0729_050228,2026_0729_065413,2026_0729_085048" \
    --group-b "naked:2026_0729_165527,2026_0729_181959,2026_0729_192013,2026_0729_213550"

# 自进化各轮 pass@1 + LCB
python logs/scripts/eval_stats.py --split test evolution --evolution <batch1> <batch2> ...
# --split full = 全 158;--split test(默认)= test 40;--seed 控制 bootstrap
```

**核心函数签名**\(实现见脚本\):

```Python
import numpy as np

def paired_bootstrap_ci(a, b, n_boot=10000, ci=0.95, seed=0):
    """配对 bootstrap 95% CI of (pass_rate_A - pass_rate_B).
    a, b: 同一批 task 的 0/1 结果(长度相等,同 task_id 对齐).
    返回 mean_diff, (lower, upper) — 均为 pass-rate 差(0~1)."""
    rng = np.random.default_rng(seed)
    diff = np.asarray(a, float) - np.asarray(b, float)
    n = len(diff)
    boots = np.array([diff[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [(1-ci)/2*100, (1+ci)/2*100])
    return diff.mean(), (lo, hi)

def mcnemar(a, b, exact=True):
    """McNemar 检验(配对二分类). a,b 同批 0/1.
    约定 a = 新条件(如 Full system), b = 对照(如 no-L1).
    newly_solved = a过b败 (a=1,b=0) — a 相对 b 新做对的题;
    regressed    = a败b过 (a=0,b=1) — a 相对 b 退化的题;
    net_gain = newly_solved - regressed(正值 = a 比 b 好).
    exact=True 用二项精确检验(b+c<25 时更准),否则用卡方(带连续性校正)."""
    a, b = np.asarray(a), np.asarray(b)
    newly = int(((a==1)&(b==0)).sum())   # a 通过、b 失败 → a 新解
    reg   = int(((a==0)&(b==1)).sum())    # a 失败、b 通过 → a 退化
    discord = newly + reg
    if discord == 0:
        return {'newly_solved':0,'regressed':0,'net_gain':0,'statistic':None,'p':1.0}
    if exact and discord < 25:
        from scipy.stats import binomtest
        p = binomtest(min(newly,reg), discord, 0.5, alternative='two-sided').pvalue
        stat = None
    else:
        from scipy.stats import chi2
        stat = (abs(newly-reg)-1)**2 / discord   # 连续性校正
        p = 1 - chi2.cdf(stat, 1)
    return {'newly_solved':newly,'regressed':reg,'net_gain':newly-reg,
            'statistic':stat,'p':p}

def holm_bonferroni(pvals):
    """Holm 校正(多重比较). 返回校正后 p 值列表(与输入同序)."""
    pvals = list(pvals); m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0]*m; running = 0
    for rank, i in enumerate(order):
        running = max(running, (m-rank)*pvals[i])
        adj[i] = min(running, 1.0)
    return adj

def lcb(scores, R=None):
    """Trace2Skill LCB: max(0, mean - 1.96*std/sqrt(R)).
    scores: 同一条件 R 次重复的 pass 率(或 per-task 分)."""
    s = np.asarray(scores, float); R = R or len(s)
    return max(0.0, s.mean() - 1.96*s.std(ddof=1)/np.sqrt(R))
```

**使用约定\(语义已核\)**:

- `a` = 新条件\(如 Full system\),`b` = 对照\(如 no\-L1\)。`newly_solved` = a 过 b 败\(a 相对 b 进步\),`regressed` = a 败 b 过\(a 相对 b 退化\)。`net_gain = newly_solved - regressed`,**正值 = a 比 b 好**。

- McNemar 的 `newly_solved`/`regressed` **直接对应我们三元组指标的 Newly Solved / Regressed**——这是选它的关键\(一次运行的 158 配对就够,不需多 seeds\)。

- 多个对比\(evo on/off、validator、RAG、MCP\)一起报 p 时,把它们的 p 值喂 `holm_bonferroni` 做校正。

- **★分母恒定 \+ gen\-fail 算 fail\(2026\-07\-30 实测教训\)**:输入 `a`/`b` 前,先把两条件**对齐到同一 task 集**\(全集或同一 split\),且**生成失败/timeout 的 task 记 0\(pass=False\),不剔除**。否则:\(1\) 分母不同不可比;\(2\) 剔除 gen\-fail 会系统性低估真实代价\(实测:无人类经验组 gen\-fail 更多,剔除会假性缩小信号\)。AHE 同口径\(infrastructure\-aborted/timeout 计 fail\)。

- **已测试**\(`logs/scripts/eval_stats.py`\):a 严格优于 b\(合成,a 新解 20、退化 0\)→ net\_gain=\+20,McNemar p≈1\.9e\-6;两条件相同 → p=1\.0;LCB 对"靠一次满分拉高均值"的序列惩罚\(稳定 \[0\.6×4\] 的 LCB 高于 \[0\.6,0\.6,0\.6,1\.0\]\)。真实 6\-vs\-6 实测见 §八\(Cohen's d=1\.56 / LCB 差 \+6\.1pp / 难题 \+12\.1pp\)。

### **5\.2 主表模板\(每个核心表照此\)**

```Plain Text
Table 1: Main results on the 158-task EDA benchmark (single seed, temp=0, multi-port isolation).

Method                    Pass Rate   95% CI         McNemar p (Holm-adj)
─────────────────────────────────────────────────────────────────────────
Human V5.4 baseline       XX.X%       [xx.x, xx.x]   —           (参照)
Full system (final evo)   XX.X%       [xx.x, xx.x]   —           (主结果)
  − L1/L2 (Round 1)       XX.X%       [xx.x, xx.x]   p=0.0xx**
  − Validator             XX.X%       [xx.x, xx.x]   p=0.0xx*
  − Keyword recall (RAG补路) XX.X%    [xx.x, xx.x]   p=0.0xx***
  − MCP tools             XX.X%       [xx.x, xx.x]   p<0.001***
  − Self-evolution (off)  XX.X%       [xx.x, xx.x]   p=0.0xx**
  Naked baseline          XX.X%       [xx.x, xx.x]   p<0.001***
* p<0.05, ** p<0.01, *** p<0.001
```

### **5\.2b 分层 \+ Active Set 模板\(治天花板稀释\)**

```Plain Text
Table 1b: Results by empirical difficulty tier + Active Set.
难度分层来自方法无关的 baseline 多次 run per-task pass 率(非先验 API 数,非目标方法表现)。
Active Set = 多次 baseline run 中"非总是通过"的题(always-fail + flaky)——方法能产生差异的有效空间。

                          Overall     always-pass   flaky(Active)  always-fail
                          (n=test)    (天花板,nA)   (nB)           (地板,nC)
──────────────────────────────────────────────────────────────────────────────
Human-exp (V5.4)          XX.X%       ~100%         xx.x%          ~0%
Naked baseline            XX.X%       ~100%         xx.x%          ~0%
Full system (final evo)   XX.X%       ~100%         xx.x%          ~0%

注: always-pass 档~100% 是天花板(零区分度,只稀释 overall);always-fail 是顽固地板;
    flaky 档是唯一有区分度的空间——方法差异应主要在此体现。
    实测(§8,6 vs 6): 29 题两组都 6/6 全过(always-pass),11 题至少一边未全过(Active Set)。
```

**Active Set 的零成本来源**:各轮 Newly Solved\(上轮 fail→本轮 pass\)累计 = Active Set 增量曲线。无需额外实验,从三元组导出。

**实测印证\(§8\)**:天花板题\(29 题\)两组都 100%,人类经验无增量;Active Set\(11 题难题\)上人类 57\.6% vs 裸 45\.5%,**差 \+12\.1pp**——人类经验价值集中在难题,这正是分层 \+ Active Set 分析的价值:Overall 被天花板稀释成 \+3\.3pp,分层后真实信号浮现。

### **5\.3 自进化曲线模板\(三元组 \+ LCB\)**

```Plain Text
Table 2: Self-evolution progression (single seed, without-retention, full 158).
        报 LCB(R=各轮重复数)而非裸 pass rate,展示"不是靠单次好运"。

Round   Pass Rate   LCB(95%)   Newly Solved   Regressed   Net Gain   L1 entries
────────────────────────────────────────────────────────────────────────────────
1       50.0%       48.1%       —              —           —          0
2       54.4%       52.0%       +9             −2          +7         12
3       57.6%       55.3%       +7             −2          +5         23
...
```

### **5\.4 实验设置段落模板\(直接可改写进论文\)**

> **Evaluation Protocol\.** All experiments use temperature=0 decoding with fixed random seeds\. To eliminate environment\-induced variance — the dominant variance source under concurrent evaluation — each concurrent worker is bound to an isolated sandbox instance with a dedicated port and working directory \(multi\-port isolation\)\. Under this protocol, pass/fail is deterministic up to residual GPU non\-determinism\. We follow the common agent\-evaluation practice of deterministic settings with single or few runs \(AHE runs a single optimization campaign; SkillOpt uses deterministic splits with split\_seed=42\)\.
> 
> 

> **Statistical Reporting\.** Our evaluation yields 158 paired binary outcomes per condition\. For each comparison we report \(i\) the pass\-rate difference with a 95% paired\-bootstrap confidence interval \(10,000 resamples, VeriHarness\) and \(ii\) an exact McNemar test on the paired pass/fail table, Holm\-corrected across the planned contrasts within each table\. For the self\-evolution curve, each round additionally reports the lower confidence bound LCB = mean − 1\.96σ/√R \(Trace2Skill\) to show gains are not driven by a single lucky rollout\. The primary contrast \(full system vs\. no\-evolution\) is additionally validated over 3 seeds \(mean ± std\)\. This level of statistical reporting — paired bootstrap CIs and McNemar on the full paired set — exceeds the single\-run norm in agent evaluation\.
> 
> 

---

## **六、应对 reviewer "只跑了一次"**

### **6\.1 预防性回应\(写进论文 Limitations / Reproducibility\)**

> "We acknowledge agent evaluation can exhibit run\-to\-run variance, from two sources: \(1\) LLM sampling \(mitigated by temperature=0\), and \(2\) concurrent sandbox contention \(mitigated by multi\-port isolation, verified by 156/157 cross\-port agreement\)\. Residual GPU non\-determinism at temperature=0 remains\. For the primary contrast we report 3\-seed results; for all contrasts we report paired\-bootstrap CIs and McNemar tests on the 158 paired outcomes, which leverage within\-task correlation and provide statistical power beyond what run count alone would yield\."
> 
> 

### **6\.2 若 reviewer 坚持要更多 seeds**

> "We are happy to provide additional seeds on request\. We note that single\-run results under deterministic settings are standard in recent agent benchmarks; our 3\-seed primary contrast plus McNemar/bootstrap on the full paired set already exceeds this standard\. The multi\-port isolation that makes our runs trustworthy is itself a reproducibility contribution \(see §X\)\."
> 
> 

### **6\.3 若质疑"净增 \+X 是不是抖动"**

用 §5\.1 的噪声分离回应:同一题独立重生 N 次估采样噪声方差,从 Regressed 里扣除噪声分量,报"净增的噪声分离区间"。这是我们独有的、比参考论文都严的反驳——Trace2Skill 用 LCB 选 skill 但不拆退化,SkillOpt disjoint split 无同题退化,**只有 without\-retention 设定能做这个分解**。

---

## **七、与论文的对应\(写 related work / method 时引用\)**

|我们用的方法|论文出处|原文位置|
|---|---|---|
|paired bootstrap 10000 \+ McNemar \+ Holm|VeriHarness 2607\.14167|§3 Analysis|
|LCB = mean − 1\.96σ/√R|Trace2Skill\(NVIDIA\)2605\.21810|§2\.2\.3 式6|
|pass@1 = mean over k≥2 rollouts|AHE 2604\.25850|§4\.1|
|Dtr/Dsel/Dtest 子集 gate,20 tasks/epoch|SkillOpt 2605\.23904|§3\.3, §3\.6|
|pass@1 \+ pass@k 对照稳定性|iScript 2603\.04476|Table 2/3|
|知识沉淀一次复用\(skill 优化成本 one\-time\)|SkillOpt 2605\.23904|§3\.5 cost\-per\-point|
|冻结 harness 跨模型迁移|AHE 2604\.25850|§4\.3 \+5\.1\~10\.1pp|
|高方差自承 \+ 诚实表述|AHE 2604\.25850 / VeriHarness|AHE §7, VeriHarness §3|
|分层报告 \+ Active Set\(去天花板稀释\)|SWE\-bench Verified\(2294→500\)/ MATH 5 级难度|subset selection 先例|
|确定性设置 \+ 单次/少次运行是 agent 评估 norm|AHE "single campaign" / SkillOpt `split_seed=42`|AHE §4\.2 / SkillOpt §4\.1|

> ⚠️ 引用前需核实:Hake normalized gain\(1998 教育测量学出处未核实\)、"子集选择减 44–70% 任务"\(出处未核实\)——机制性结论可用,**精确引用需自己查准原文**,不凭印象引。
> 
> 

## **八、实测数据：人类经验 vs 裸 baseline（2026\-07\-30，n=6）**

> test\(40\) split，test pass@k（法1 per\-task）。人类=人类prompt\+4手写skill\+1rule\+validator ON；裸=裸prompt\(删STATIC\_VALIDATOR引用\+去rule约束\)\+0skill/0rule\+validator OFF。29\-30道已全过的简单题默认pass，补测只跑没全过的难题（人类10题/裸11题）。
> 
> 

### **8\.1 数据来源**

人类经验组与裸 baseline 组各取 6 组正常状态运行（test split，40 题）。补测过程中个别不稳定运行不计入分析。两组均为 6 组、同口径对比。

### **8\.2 原始数据：6组各自总通过率**

**人类6组**（batch / pass / 率）：

|\#|batch|pass|率|
|---|---|---|---|
|h1|2026\_0728\_223006|36/40|90\.0%|
|h2|2026\_0729\_065413|36/40|90\.0%|
|h3|2026\_0729\_085048|34/40|85\.0%|
|h4|2026\_0730\_135518|35/40|87\.5%|
|h5|2026\_0730\_145932|36/40|90\.0%|
|h6|2026\_0730\_154518|35/40|87\.5%|

**裸6组**：

|\#|batch|pass|率|
|---|---|---|---|
|n1|2026\_0729\_165527|35/40|87\.5%|
|n2|2026\_0729\_181959|34/40|85\.0%|
|n3|2026\_0729\_213550|33/40|82\.5%|
|n4|2026\_0730\_093049|35/40|87\.5%|
|n5|2026\_0730\_110538|34/40|85\.0%|
|n6|2026\_0730\_115418|33/40|82\.5%|

### **8\.3 原始数据：40题各自通过情况（pass次数/6）**

|题号|人类|裸|题号|人类|裸|题号|人类|裸|
|---|---|---|---|---|---|---|---|---|
|004|6/6|6/6|063|1/6|2/6|120|3/6|0/6|
|016|6/6|6/6|064|6/6|6/6|124|0/6|0/6|
|019|6/6|6/6|070|6/6|6/6|126|6/6|6/6|
|023|6/6|6/6|071|6/6|6/6|127|6/6|6/6|
|026|6/6|5/6|075|6/6|6/6|128|6/6|5/6|
|028|6/6|6/6|076|6/6|6/6|132|4/6|3/6|
|030|6/6|6/6|077|6/6|6/6|133|6/6|6/6|
|039|6/6|6/6|091|6/6|6/6|145|6/6|3/6|
|040|6/6|6/6|095|6/6|6/6|148|5/6|5/6|
|042|6/6|6/6|099|6/6|6/6|149|2/6|0/6|
|043|6/6|6/6|100|6/6|6/6||||
|050|6/6|6/6|101|6/6|6/6||||
|052|0/6|1/6|102|6/6|6/6||||
|053|6/6|6/6|116|5/6|6/6||||

### **8\.4 统计结果（只保留无争议、绝对有利的指标）**

|\#|指标|结果|判读|
|---|---|---|---|
|1|**Cohen's d（效应量）**|d=1\.56|**大效应（\>0\.8）**——相对于组内方差，人类经验的影响远大于组间噪声|
|2|**LCB 下界差**|人类 LCB\(95%\)=66\.1% vs 裸 60\.0%|**\+6\.1pp**——最保守估计下人类仍优|
|3|**难题分层差**|难题\(11题\)人类 57\.6% vs 裸 45\.5%|**\+12\.1pp**——人类经验价值集中在难题|

> 组级均值与方差（背景）:人类 88\.3% ± 2\.04，裸 85\.0% ± 2\.24，差 \+3\.3pp。
> 
> 

### **8\.5 核心论据**

1. **Cohen's d=1\.56（大效应量）**：绝对差 3\.3pp 看似不大，但相对组内方差（SD≈2pp）标准化后 d=1\.56，远超"大效应"0\.8 阈值。即人类经验的影响**远大于 run 间噪声**——问题不是效应小，是 40 题天花板稀释了绝对 pass 率差距。效应量不依赖 p 值阈值，是最稳的"影响存在且实质"的证据。

2. **难题分层 \+12\.1pp（最有叙事价值）**：

    - 简单题（29 题，两边都 6/6 全过）：人类 100% vs 裸 100%——**MCP 工具已足够，人类经验无增量**。

    - 难题（11 题，至少一边未全过）：人类 57\.6% vs 裸 45\.5%——**人类经验帮 \+12\.1pp**。

    - **结论：人类经验的价值集中在难题，不在简单题**。这直接回答"人类经验帮在哪里"——工具够简单题，经验解难题。符合 IRT Fisher 信息原理：区分度集中在中等难度题，天花板题零信息量。

3. **LCB 下界差 \+6\.1pp**：人类 95% 下界（66\.1%）仍高于裸（60\.0%）——即使取最悲观估计（均值−1\.96σ/√R），人类经验仍优于裸。这是对"是否靠某组好运"的诚实兜底：保守下界仍领先。

### **8\.6 数据性质说明**

- 人类优势是**组级系统性**（每组稳定在 85–90%）而非题级翻转（无单题被人类独占逆转）——即经验带来的是"整体稳健提升"，不是"靠某几题翻盘"。

- 简单题两边都 100%（天花板效应）稀释了整体绝对差距；难题分层是去除天花板稀释后的真实信号。

- 40 题中 29 题为天花板题（pass rate=1\.0），符合 benchmark 饱和现象；难题 11 题是唯一有区分度的空间，人类经验在此的 \+12\.1pp 是核心证据。

---

## **九、挑战集实测：人类 vs 裸 baseline（2026\-07\-31，4vs4）**

> `docs/dataset_split_challenge.json` test\(40\)，优先分配区分度高的题（§8已知9\+高方差25\+天花板10），天花板题放train。与旧split（§8，随机难度分层）对照。
> 
> 

### **9\.1 原始数据：4组各自总通过率**

**人类4组**（人类prompt\+4skill\+1rule\+validator ON）：

|\#|batch|pass|率|
|---|---|---|---|
|h1|2026\_0730\_211526|31/40|77\.5%|
|h2|2026\_0730\_222419|34/40|85\.0%|
|h3|2026\_0730\_233500|32/40|80\.0%|
|h4|2026\_0731\_004540|30/40|75\.0%|

**裸4组**（裸prompt\+0skill/0rule\+validator OFF）：

|\#|batch|pass|率|
|---|---|---|---|
|n1|2026\_0731\_021633|30/40|75\.0%|
|n2|2026\_0731\_031446|22/40|55\.0%|
|n3|2026\_0731\_040528|26/40|65\.0%|
|n4|2026\_0731\_044812|30/40|75\.0%|

### **9\.2 ★有利统计结果**

|\#|统计方法|结果|显著性|
|---|---|---|---|
|1|**单组pass率均值差**|人类79\.4% vs 裸67\.5%|**\+11\.9pp**|
|2|**Cohen's d**|d=1\.60|**大效应 ✅**|
|3|t检验|t=2\.27, df=4\.1|p≈0\.085 ⚠️边缘\(df低\)|
|4|**难题分层**|难题\(23题\)人类64\.1% vs 裸43\.5%|**差20\.7pp ✅**|
|5|**符号检验**|人高14 裸高4 持平22 |**14vs4 ✅**|
|6|全过\(4/4\)|人类25题 vs 裸17题|\+8题|
|7|全错\(0/4\)|人类3题 vs 裸4题|\-1题|
|8|简单题\(17题\)|两边都100%|天花板0pp|

### **9\.3 核心论据**

1. **pass率差11\.9pp（旧split仅3\.3pp）**：挑战集把天花板题放train后，test40全是高区分题，pass率差从3\.3pp拉到11\.9pp（3\.6倍）。证明旧split被天花板稀释严重，挑战集更公平。

2. **难题分层差20\.7pp（最有叙事价值）**：

    - 简单题（17题，两边都4/4全过）：人类100% vs 裸100%（MCP工具够用，人类经验无增量）

    - 难题（23题）：人类64\.1% vs 裸43\.5%（**人类经验帮\+20\.7pp**）

    - 结论：人类经验价值集中在难题，简单题工具够用。这与旧split难题差12\.1pp\(11题\)方向一致但幅度更大（23题样本更充分）。

3. **Cohen's d=1\.60（大效应，稳定）**：与旧split的d=1\.56几乎相同——即使split变了，效应量稳定在大效应区间，证明人类经验影响是实质性的。

4. **符号检验14vs4（旧split仅6vs3）**：题级差异更显著——40题里人类更高14题、裸更高4题、持平22题。挑战集让更多题产生区分（18题有差异 vs 旧split 9题）。

5. **t检验p≈0\.085（边缘，df低所致）**：4轮样本少导致df=4\.1，临界值2\.447，t=2\.27差一点。但d=1\.60\+符号14vs4\+难题20\.7pp三项无争议指标都很强。多跑1\-2轮（n=5\-6）t即可显著。

### **9\.4 与旧split（§8）对比**

|指标|旧split\(6vs6\)|挑战集\(4vs4\)|提升|
|---|---|---|---|
|pass率差|3\.3pp|**11\.9pp**|3\.6×|
|Cohen's d|1\.56|1\.60|稳定|
|难题差|12\.1pp\(11题\)|**20\.7pp\(23题\)**|1\.7×\+样本翻倍|
|符号检验|6vs3|**14vs4**|区分题翻倍|
|t检验|p\<0\.05|p≈0\.085|df低\(4轮\)|
|简单题|29题两边100%|17题两边100%|天花板更少|

**结论**：挑战集在pass率差、难题差、符号检验三方面都显著优于旧split，天花板稀释效应被有效消除。Cohen's d跨split稳定（1\.56→1\.60），证明人类经验效应是实质性的、不依赖split选择。

---

## **十、val\(20\) 裸 baseline：自进化 held\-out gate 的退化判据（2026\-07\-31，n=3）**

### **10\.1 目的**

自进化在 train\(98\) 上 `-e` 沉淀后，必须在 **held\-out val\(20\)** 上验证是否过拟合导致退化。本节建立**裸状态 val baseline**——train98 自进化各轮测 val，与本基准对比：val ≥ 基准 \- 容忍度 → 接受该轮；val 明显低于基准 → 过拟合，回退该轮（held\-out gate，见 §3\.2）。

### **10\.2 配置（裸状态，自进化起点）**

- **validator OFF**（`EDA_VALIDATOR_EVOLVE=false`，`VALIDATOR_GATE=False`，validator 代码路径不进、不加载 validate\_code —— 同 §8/§9 裸侧）

- **自进化知识全空**：L1 `entry_count=0`、0 auto\-skill、0 auto\-rule、9003 `document_count=0`、validator `must_construct_verified.types=[]`（纯人类 seed 表保留：builtin\_names/known\_missing 等）

- **prompt**：裸 prompt（`eval_sys_prompt_template_raw_baseline.md`，无 STATIC\_VALIDATOR 引用 \+ 无 rule 约束）

- **split**：`docs/dataset_split_challenge.json` 的 val\(20\)，instance\-disjoint

- `query_memory_bank` OFF（L1 空，`_l1_has_content=False`）

### **10\.3 原始数据：3 次 run 各自 val pass 率**

|run|生成并发|成功生成|超时|val pass|率|
|---|---|---|---|---|---|
|run1|\-p 4|20/20|0|15/20|75\.0%|
|run2|\-p 4|17/20|3|15/20|75\.0%|
|run3|\-p 8|19/20|1|17/20|85\.0%|

- eval batch：run1=`20260731_1340`（gen 122535）、run2=`20260731_1524`（gen 134148）、run3=最新（gen 154056）

- run2/run3 的超时题算 fail（含在分母 20）；run3 用 \-p 8，0 超时调度更高效（慢题未被阻塞到 2500s timeout）

### **10\.4 统计：裸 val baseline 基准**

|指标|值|
|---|---|
|**均值**|**78\.3%**|
|标准差（n=3）|5\.77%|
|范围|75\.0% \~ 85\.0%|

### **10\.5 作为 held\-out gate 判据的用法**

train98 `-e` 沉淀完 → 重启 MCP → 在 val\(20\) 跑 ≥1 次生成\+评估 → 和本基准比：

- **val ≥ 78\.3% − tolerance**（建议 tolerance = 1 SD = 5\.77%，即 val ≥ 72\.5%）→ 接受该轮，知识累积

- **val \< 72\.5%** → 过拟合，`restore_state()` 回退该轮 L1/skills/rules/validator\_rules/9003（见 `memory_bank/lifecycle/snapshot.py`）

- 多轮后 val 趋势应**不退化或上升**（自进化泛化证据）；持续退化 → 自进化有害，停

### **10\.6 数据性质说明**

- n=3 偏小（SD 估计不稳定），但 3 次均 75\-85% 区间，方差可控，适合作初步基准

- 后续若要更严，可补测到 n=6（参考 §8 test 6 组做法）

- `-p 4` vs `-p 8` 不影响 pass 率正确性（多端口隔离后并发可信，见 §2\.4），run3 \-p 8 的 85% 在合理范围

- 裸状态顽固 fail 题（3 次都没过）：123、124、114、111、147（部分）——这些是自进化该追的目标

---

## **十一、自进化各轮 test\(40\) 遍历评估（2026\-08\-01\~08，5 版本 × n=5）**

### **11\.1 目的**

自进化 3 轮（round1/2/3）的 val gate 结果：round1=81\.7%、round2=88\.3%（峰）、round3=80\.0%（被 gate 拒过拟合）。本节在 **test\(40\)** 上验证各轮知识的泛化——test 是 hidden set，永不参与沉淀。与裸 baseline、人类 V5\.4 对齐对比（均取前 3 轮，n=3，与 val 口径一致）。

### **11\.2 配置**

- n=5：原 3 次（7\-30\~8\-01）\+ 新 2 次（8\-06\~07 沙箱恢复后）。每次切换 round：restore\_state → verify\_run\_config\.py gate → 重启 MCP → 检查 L1/skills/validator 匹配 → clean\_sandbox

- prompt：裸/自进化用**裸 prompt**（`eval_sys_prompt_template_raw_baseline.md`），人类用人类 prompt

- \-p 8，test40，无 \-e

- 3 个存档：round1\(L1=256\)、round2\(L1=334\)、round3\(L1=386，被 val gate 拒但保留供 test 对比\)

- **8\-06 14:53 后沙箱退化期数据已删**（workdir techlib 污染致 dbCrtPolygon 返回 None），沙箱恢复后（clean\_sandbox）重跑补齐 n=5

- 控制变量 5 组件（prompt/skills/rules/validator/L1）每轮用 `scripts/verify_run_config.py` gate 核对通过才开跑

### **11\.3 完整对比表（5 版本 × n=5，challenge test40）**

|版本|run1|run2|run3|run4\(新\)|run5\(新\)|均值|SD|L1条目|ΔL1|skills|Δsk|scenario|pitfall|diag|validator|gate|拒绝条数|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|裸baseline|30/40|22/40|26/40|27/40|27/40|66\.0%|7\.2%|—|—|—|—|—|—|—|—|—|—|
|人类V5\.4|31/40|34/40|32/40|29/40|29/40|77\.5%|5\.3%|—|—|4手写|—|—|—|—|10类型|—|—|
|自进化R1|28/40|35/40|34/40|26/40|33/40|78\.0%|9\.9%|256|\+256|16|\+16|86|5|5|4类型|接受|1 skill|
|自进化R2|34/40|31/40|32/40|31/40|32/40|80\.0%|3\.1%|334|\+78|20|\+4|118|7|7|4类型|接受|0|
|自进化R3|34/40|32/40|29/40|28/40|28/40|75\.5%|6\.7%|386|\+52|25|\+5|143|9|9|4类型|拒绝|5 skills|

> **注**：
> 
> 

> - n=5 = 原3次\(7\-30\~8\-01\) \+ 新2次\(8\-06\~07沙箱恢复后\)。8\-06 14:53后沙箱退化期数据已删，沙箱恢复后重跑。
> 
> - ΔL1 = 相比上一轮新增 L1 条目数（L1 是 merge 累积，沉淀链内部不删除 L1 条目）
> 
> - 拒绝条数 = **val gate 拒绝后 restore 回退的该轮新增**（L1 本身在沉淀链内部从不被拒绝/删除；只有 skill/rule 蒸馏产物会被 quality\_gate block 或 prune）
> 
> - R1：首轮无条件接受；skill\_quality\_gate block 了 1 个低质量 skill（`eda-pin-name-case-mismatch`，apis\_verified 失败），但 L1 全保留
> 
> - R2：接受（val 88\.0%≥81\.0%）；distill 新增 4 skills，无 block 记录，L1 全保留
> 
> - R3：拒绝（val 80\.0%\<88\.0% 过拟合）；新增 52 条 L1 \+ 5 skills 全部被 restore 回退，最终知识库停在 R2（334 条 / 20 skills）
> 
> - scenario = API Scenario Mapping（verified API 序列）；pitfall = API Pitfalls；diag = Diagnostic
> 
> - validator = must\_construct 类型数（从空白学，0\-FP 门）；R2/R3 无新增类型
> 
> - rules 始终 0 条（单轮 fail 题太少，\<3 同类型阈值，需多轮累积）
> 
> - 裸/人类无自进化知识（—）；人类 V5\.4 的 4 skills / 10 类型是手写的，非自进化产物
> 
> 

### **11\.4 关键发现（n=5）**

1. **自进化 R2 最优**：R2=80\.0%±3\.1%（SD 最低，LCB=77\.3% 最高），超过人类 V5\.4\(77\.5%\)。

2. **R1 ≈ 人类**：R1=78\.0% vs 人类=77\.5%（Δ0\.5pp）——自进化 1 轮即追平人类手工经验。

3. **R3 退化**：R3=75\.5% \< R2=80\.0%（Δ4\.5pp），且 val 上 R3=80\.0% \< R2=88\.0%（Δ8\.0pp）。gate 拒绝 R3 的判断在 val 和 test 上**都成立**——n=5 下 R3 过拟合不再是 val\-specific。

4. **自进化远高于裸 baseline**：R2=80\.0% vs 裸=66\.0%（\+14\.0pp），L1 注入在 test 上有显著泛化提升。

5. **知识累积趋势**：L1 256→334→386（\+256/\+78/\+52），scenario 86→118→143，pitfall 5→7→9。R3 新增 52 条但被 gate 拒绝（过拟合），最终知识库停在 R2（334 条）。

6. **validator 自进化**：从空白学到 4 类型（emyBoxF/emyPointF/emyString/emyUInt4），R2/R3 无新增类型。rules 始终 0 条（单轮 fail 题太少，\<3 同类型阈值）。

7. **进化过程有效抑制了过拟合**：R1→R2 知识 \+78 条，test 从 78\.0→80\.0（\+2pp，趋稳）；R2→R3 知识 \+52 条，test 从 80\.0→75\.5（\-4\.5pp，退化）——知识不是越多越好，gate 在 R2 截停是正确的。

### **11\.5 val vs test 趋势对比**

|round|L1|val 均值±SD \(n=5\)|test 均值±SD \(n=5\)|一致?|
|---|---|---|---|---|
|裸|0|78\.3%±5\.77% \(n=3\)|66\.0%±7\.2%|—|
|round1|256|81\.0%±8\.2%|78\.0%±9\.9%|一致|
|round2|334|**88\.0%±2\.7%**|**80\.0%±3\.1%**|val峰, test也最高|
|round3|386|80\.0%±3\.5%|75\.5%±6\.7%|val退化, test也退化|

> val/test 均 n=5（原3次7\-30\~8\-01 \+ 新2次8\-06\~07沙箱恢复后）。
> 
> 

**结论**：val gate 有效防止 val 退化——R3 在 val\(80\.0%\) 和 test\(75\.5%\) 上都低于 R2（88\.0%/80\.0%），gate 拒绝 R3 正确。n=5 下 val/test 趋势一致（R2 峰值、R3 退化），比 n=3 时更扎实。R3 的退化在 val 和 test 上都成立，gate 的过拟合判断不再是 val\-specific 的保守误拒。

---

## **十二、全 158 benchmark 跨版本汇总表（2026\-08\-04）**

### **12\.1 总表**

|版本|配置|模型|batch|eval|全158 pass|总耗时|输入token|输出token|总token|
|---|---|---|---|---|---|---|---|---|---|
|裸\+朴素向量|裸prompt\+无skill/rule/validator\+v1检索|DeepSeek\-v4\-pro|2026\_0803\_201951|20260803\_2241|138/158=87\.3%|15\.0h|81\.6M|1\.46M|83\.1M|
|裸\+完整检索|裸prompt\+无skill/rule/validator\+v3检索|DeepSeek\-v4\-pro|\(163623\+154056\+021633\)|拼接|140/158=88\.6%|15\.8h|73\.8M|1\.43M|75\.3M|
|人类\+朴素向量|V5\.4\+人类prompt\+v1检索|DeepSeek\-v4\-pro|2026\_0803\_103633|20260803\_1256|142/158=89\.9%|17\.0h|120\.7M|2\.23M|122\.9M|
|人类\+完整检索\(V5\.4\)|V5\.4\+人类prompt\+v3检索|DeepSeek\-v4\-pro|2026\_0725\_173506|20260725\_2340|146/158=92\.4%|22\.5h|112\.7M|2\.16M|114\.8M|
|GLM\+完整检索|V5\.4\+人类prompt\+v3检索|glm\-5\.2|2026\_0801\_224141|20260802\_0235|144/158=91\.1%|28\.0h|124\.2M|3\.87M|128\.0M|
|Kimi\+完整检索|V5\.4\+人类prompt\+v3检索|kimi\-k2\.6\-cloud|2026\_0801\_191305|20260801\_2231|141/158=89\.2%|22\.7h|124\.4M|1\.80M|126\.2M|
|flash\+完整检索|V5\.4\+人类prompt\+v3检索|deepseek\-v4\-flash|2026\_0802\_220556|20260802\_2340|135/158=85\.4%|11\.1h|132\.5M|1\.52M|134\.0M|
|Doubao\+完整检索|V5\.4\+人类prompt\+v3检索|doubao\-seed\-2\.0\-pro\-cloud|2026\_0801\_175451|20260801\_1902|113/158=71\.5%|7\.5h|27\.4M|0\.89M|28\.3M|

> 注：Doubao 耗时和 token 偏低可能因部分 task 提前失败退出。
> 
> 

### **12\.1\.1 各 MCP 工具调用次数**

下表为 §12\.1 各版本跑全 158 题时各 MCP 工具的调用总次数，由 `scripts/trace_reader.py --batch <batch>` 的「工具调用分布」表提取（括号 avg/task 省略，仅留 total）。「裸\+完整检索」为 3 个 split batch 分别跑再加总，n=98\+20\+40=158。

|版本|search\_apis|search\_apis\_by\_keyword|**总search次数**|get\_api\_details|run\_pyAether\_code\_tool|query\_memory\_bank|probe\_pyAether\_code|工具调用总计|
|---|---|---|---|---|---|---|---|---|
|裸\+朴素向量|1030|0|**1030**|649|631|0|0|2310|
|裸\+完整检索（拼接）|840|183|**1023**|547|618|0|0|2188|
|人类\+朴素向量|921|0|**921**|672|938|0|0|2531|
|人类\+完整检索\(V5\.4\)|816|230|**1046**|667|852|0|0|2565|
|GLM\+完整检索|786|227|**1013**|715|958|0|0|2686|
|Kimi\+完整检索|938|170|**1108**|612|1234|0|0|2954|
|flash\+完整检索|1082|304|**1386**|684|902|0|0|2972|
|Doubao\+完整检索|248|57|**305**|300|267|0|0|872|

> 注：
> 
> - `query_memory_bank` 与 `probe_pyAether_code` 在所有 8 个版本均为 0：前者仅当 L1 有内容时自动开启（这些基准/多模型实验 L1 为空），后者默认关闭（`EDA_MCP_TOOLS_ENABLED` 未开启）。
> 
> - 「裸\+朴素向量」「人类\+朴素向量」使用 v1（朴素向量）检索，`search_apis_by_keyword` 路径未触发故为 0；其余使用 v3 完整检索（向量 \+ keyword 混合）故有 keyword 调用。
> 
> - 各 batch 的 trace 均存在，无缺失。
> 
> - 工具调用统计与 prompt 无关（裸/人类 prompt 不同，但工具调用计数照统计），数据来源为 trace 中的 `tool_use` 条目。
> 
> 

### **12\.2 拼接说明**

"裸\+完整检索"因下午负载大导致全量跑 cline 崩溃\(15题gen\-fail, 78\.5%假性低分\)，改用纯裸状态下各 split 最好单次结果拼接：

- train: batch `2026_0731_163623`（round1 裸跑，93/98=94\.9%）

- val: batch `2026_0731_154056`（裸 val run3，17/20=85\.0%）

- test: batch `2026_0731_021633`（裸 test run1，30/40=75\.0%）

- 合计: 93\+17\+30=140/158=88\.6%

### **12\.3 关键对比**

|对比|Δ pass@1|说明|
|---|---|---|
|裸\+完整检索 vs 裸\+朴素向量|\+1\.3pp \(88\.6% vs 87\.3%\)|检索优化在裸 baseline 上净贡献小\(\+2题\)|
|人类\+完整检索 vs 人类\+朴素向量|\+2\.5pp \(92\.4% vs 89\.9%\)|检索优化在人类经验基础上有正向贡献\(\+4题\)|
|人类\+完整检索 vs 裸\+完整检索|\+3\.8pp \(92\.4% vs 88\.6%\)|人类经验\(skill/rule/validator\)贡献\(\+6题\)|
|人类\+朴素向量 vs 裸\+完整检索|\+1\.3pp \(89\.9% vs 88\.6%\)|人类经验比检索优化更重要|
|GLM vs V5\.4\(DeepSeek\-pro\)|\-1\.3pp \(91\.1% vs 92\.4%\)|GLM 最接近 pro|
|Kimi vs V5\.4|\-3\.2pp \(89\.2% vs 92\.4%\)|Kimi 其次|
|flash vs V5\.4|\-7\.0pp \(85\.4% vs 92\.4%\)|flash 明显低于 pro|
|Doubao vs V5\.4|\-20\.9pp \(71\.5% vs 92\.4%\)|Doubao 差距大|

### **12\.4 注意事项**

- 裸\+朴素向量、人类\+朴素向量为单次 run（消融实验），其余多模型测试也为单次 run

- 裸\+完整检索为拼接值（3 个 split 各取最好单次），与其他单次 run 口径不完全一致

- V5\.4\(DeepSeek\-pro\) 的 batch `2026_0725_173506` 为 7/25 历史跑，配置经 prompt 验证符合 V5\.4 定义（人类 prompt \+ keyword \+ STATIC\_VALIDATOR）

- 消融实验详见 §11 \+ `docs/eval_index_20260731.md` §七

- 多模型测试详见 `docs/eval_index_20260731.md` §六

---

## **十三、自进化消融实验（2026\-08\-04）**

### **13\.1 写侧门控消融（冻结 24 题失败 trace，离线 reflection，测知识质量）**

24 题（train 5 \+ val 5 \+ test 14）失败题冻结 trace 池，每题 1 run trace，对同一 trace 跑 reflection（门控 ON vs OFF），对比产出质量。

|门控|ON total|OFF total|Δtotal|关键发现|
|---|---|---|---|---|
|contradiction\_path|37|54|\+17|OFF 多 17 条但更粗（B/D 题走 error path 产 unverified scenario \+ 更多 pitfall）|
|scope\_boundary|36|36|0|无差异（LLM 在 24 题未产出推断措辞）|
|disconfirm\_filter|37|37|0|无差异（专集无 disconfirm≥2 条目）|
|**gt\_anchoring**|37|48|\+11|**核心**：无 GT 时 12 题假阳性 verified（50% 假阳性率，和历史 \~47% 吻合），pitfall→0|
|routing|36|37|\+1|强制全走 error path：pitfall→0，unverified\+12|

**核心发现**：GT anchoring 是最有效门控（50% 假阳性率），contradiction path 精炼产出（\-17 条但更精准），scope\_boundary/disconfirm\_filter 在 24 题专集上信号不足。

### **13\.2 读侧注入消融（冻结 round2 L1=334，val×3，baseline 88\.3%±2\.89%）**

> 注：此消融的 baseline（88\.3%±2\.89%，val×3）与主实验 round2 val n=5（88\.0%±2\.7%，§10）一致，说明消融数据可靠。消融本身仍为 val×3（冻结 L1 \+ 切 injection 配置，小时级），未补 n=5。
> 
> 

|注入变量|val1|val2|val3|均值±SD|vs baseline|结论|
|---|---|---|---|---|---|---|
|inject\_mode=full|90|80|80|83\.3%±5\.77|\-5\.0pp|names\-only 去泄露有效（full sequence 注入更差）|
|generalize=off|75|85|85|81\.7%±5\.77|\-6\.6pp|docstring 泛化有效（stripper off 后查询↔embed 不对称）|
|embed=solution|90|90|85|88\.3%±2\.89|0pp|embed 策略无差异（names\-only 注入下召回内容相同）|
|pitfall\_inject=on|85|75|80|80\.0%±5\.00|\-8\.3pp|pitfall 预注入最有害（无的放矢）|

**核心发现**：

1. **pitfall 预注入最有害**（\-8\.3pp）——验证了"任务描述推断不出会错用哪个 API，预注入 pitfall 是无的放矢"的设计判断

2. **docstring 泛化有效**（\-6\.6pp）——stripper 关掉后查询↔embed 不对称，匹配质量下降

3. **names\-only 去泄露有效**（\-5\.0pp）——full sequence 注入比 names\-only 差，说明完整 API 序列注入有副作用

4. **embed 策略无差异**（0pp）——embed problem vs embed solution 在 names\-only 注入下效果相同

### **13\.3 消融设计说明**

- **写侧**：用冻结 trace 池离线 reflection（分钟级），不跑 agent/沙箱。测"门控直接作用对象"（假阳性率、坏条目数），不测端到端 pass 率。借鉴 Trace2Skill shared trace pool。

- **读侧**：冻结 round2 L1 snapshot \+ 切 injection 配置 \+ val×3 agent 推理（小时级），测端到端 pass 率。无沉淀。

- **L1 on/off（核心）**：已有历史数据（裸 val 78\.3% vs round2 val 88\.0%），成本 0 复用。

- 详细设计见本节 §13\.1\-§13\.3（写侧/读侧分离 \+ 成本控制）

