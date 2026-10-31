# BAIZE_VISION_TASK.md
### 🚀 运维令 · 2026-10-31 11:0x（**审校 BaiZe 论文第 6 章「视觉编码器」，出中文 HTML 修订计划**）· 用户直令 · 最高优先

> **用户令**：「让 pretrain 和 vision 看看 BaiZe 论文中各自的章节，出一版中文 HTML 修订计划：哪里跟事实不符，计划怎么改。」

**背景**：论文已压到 ISEDA 6 页正文上限（实测全文 6 页，参考文献也在 6 页内）。你的第 6 章现在是 **0.3 页的占位式精简版**（`BaiZe-ISEDA2027/ISEDA2027/6_vision_encoder.tex`，仅 3 段 + 2 个 `\paragraph`），是我按用户「只留最终结果、中间过程全删」临时写的。**下一版由你重写**，本轮先出修订计划。

#### ① 先读（逐字读完再动笔）
```
cd doc/BaiZe-ISEDA2027 && git pull --rebase
cat BaiZe-ISEDA2027/ISEDA2027/6_vision_encoder.tex
```
对照源：`run/EXPERIMENTS_VISION.md`（§R8–R13 全部记录）、`run/MEMORY_VISION.md`、`reports/report_vision_*.html`。

#### ② 运维已发现的疑点（**逐条核实并给结论**）
1. **参数口径很可能错（P0）**：现文写「width-$1024$/depth-$30$ ... $126.8$M ($505.2$M at full width)」。但 `EXPERIMENTS_VISION.md` L129 明确训练用的是 **w512（126.78M）**——「512」是**宽度档位号**，不是 hidden width。**请查清：OpenVision2 实际 hidden width / depth？126.8M 对应哪个档？505.2M 是哪个配置？**
2. **「Both terms are required」可能过强**：原四臂消融的结论是「突破依赖对比锚点与稠密项的**交互**，单独任一项都不充分」，且只在**单一 token 预算（15.4M）**下做过。给出该结论能支持的严格措辞。
3. **`+12.4pp` 基准**：核实 19.76% 与 7.40% 是否确为**同样本量**。
4. **`20.27%@176M` vs `19.76%@55.3M` 可比性**：前者 3 epoch、后者单 epoch，是否需标 epoch？
5. **缺什么**：没提 IN-1k lp 绝对值低（19.76%）在 EDA 语境的含义；没提 Stage-1W/2W 与本节关系。判断该不该补。

#### ③ 交付物（唯一硬交付）
`reports/report_vision_paper_revise_plan_zh.html` —— 中文、单文件自包含、**0 `script`/0 外链/0 CDN**、标签配平、**≥18KB**；生成器 `vision/generate_paper_revise_plan_report.py`（幂等，重跑两次逐字节相同）；commit `vision paper-plan:`，push。

**必须含 6 节**：① 现状逐句摘录 + 标注「✅属实 / ⚠️存疑 / ❌不符事实」+ 证据（文件+行号）；② 不符事实清单表（位置/现文/事实/来源/严重度 P0-P2）；③ 改写方案（**可直接替换 `.tex` 的英文目标文本**，逐段「改前→改后」）；④ 篇幅预算（**半页 ≈45-50 行**，说明删了什么、为何可删）；⑤ 仍需的实验（无实测支撑的如实列出，不许编）；⑥ 自检清单。

#### ④ 红线
- 🚫 **本轮只出计划，不改 `.tex`**（改稿等确认后下一轮做）。
- 🚫 **不伪造数字**；未实测写「待核」或「估算」。
- 🚫 **不得恢复用户明令删除的内容**（六架构对比、SSM 崩溃叙事、AR 范式探索、Muon 消融、ProtB/epoch 缩放、AIMv2 四臂细节）——只能在计划里作「支撑证据」，**不得进正文**。
- 🚫 不动 `4_llm_pretrain.tex`（pretrain 线负责）。
- 🚫 章节里有 `% 中文：` 双语注释行，**不得删**；改写时同步更新中文。
- 体积：任务书 ≤32KB；本令未完成前不许归档。

### 🚀 运维令 · 2026-10-31 08:4x（**起草「波形图强化」中文 HTML 计划书：交互式 RL + WaveView 实操**）· 用户直令 · 最高优先

> **用户原话**：「给vision发个任务，起草中文HTML计划书：如何强化MLLM读懂波形图的能力。提示：我们有WaveView软件的license，也有可以操作WaveView的Tcl文档，可否通过跟环境交互的强化学习使得MLLM在读懂波形图方面游刃有余？这个MLLM最终目的是嵌入到EDA agent 烛龙做个能帮忙读懂仿真结果波形图的工具，帮助烛龙在芯片设计工作流编排方面走的更远。另外它也是烛龙论文future work中multimodal grounding努力的一部分。」

**交付物（唯一硬交付）**：`reports/report_vision_wave_rl_plan_zh.html` —— 中文、单文件自包含、**0 `script`/0 外链/0 CDN**、标签配平、**≥28KB**；生成器 `vision/generate_wave_rl_plan_report.py`（幂等，重跑两次逐字节相同）；commit `vision wave-rl-plan:`，push。

#### ① 与前作的边界（先讲清楚，别重复造轮子）
`reports/report_vision_waveform_zh.html`（2026-10-30 已交付）讲的是「看懂波形需要哪些能力 / 怎么造数据 / 怎么 SFT 与评测」，RL 在其中仅一句「可选 Stage-3W、风险高」。
本计划书**不重写它**，只把「与 WaveView 环境交互的 RL」从一句可选项展开成可执行技术路线；基线数字（4 类波形 / 四层能力梯度 / waveform 368 命中 / WaveQA 设计）**直接引用，不重新调研、不重新估算**。

#### ② 必须回答的 9 个问题（逐条成节，缺一不可）
1. **为什么必须「交互」而非「看图猜」**：论证单凭静态截图做数值量测有原理性上限（像素量化/抗锯齿/分辨率 vs token 预算）。定分工：**看图定性 → 调工具定量**，模型的职责是**决定看什么、量哪里**，精确值由工具读出。
2. **与烛龙的接口契约**：工具名 `waveform_read`，输入 = 自然语言问题 + FSDB 路径，输出 = **结构化 JSON（值+单位+证据坐标）**而非自然语言；说明如何嵌进烛龙 `run_code` 闭环，以及**为何它提升 Ω（观测似然）保真度**——显式接上烛龙论文 *observation-fidelity bound*（gap 上界由 Ω 决定、与模型规模无关）。**这是本计划书的理论锚点，必须写。**
3. **RL 环境设计（核心）**：把 WaveView 包成 **Gym 风格确定性环境**：action = **受控 Tcl 子集**（非任意 Tcl，兼顾安全与可判分）；observation = 紧凑文本/数值观测 +（可选）视窗截图；含终止条件、步数上限、失败惩罚、**单 episode 内 wv 调用上限**（见 ③ 崩溃阈值）。
4. **奖励设计（可验证、防 hack）**：主奖励 = **数值相对误差分档**（如 1%/5%/10%），非文本相似度；加**证据奖励**（真的调用了对应工具并给出正确坐标）与**稠密中间奖励**；**anti-hacking**：禁直输 GT 常量、禁跳过工具、隐藏 FSDB + 隐藏题双盲抽检。
5. **数据从哪来（可行性论证）**：三级——① 合成（自造激励/开源仿真器，GT 天然可得）；② 真实（烛龙 waveform trace 中可复现 FSDB，用**同一 WaveView 命令回放**取 GT）；③ 派生（换信号/时间窗/量测目标扩题）。给**各来源题量 × GT 可靠性**对比表。
6. **训练配方**：SFT 冷启动（必须，否则 RL 无有效动作分布）→ RL；GRPO / PPO 二选一**论证倾向 GRPO**（无 value 网络、2B 省显存）；**动作必须是合法 Tcl 子集，非法直接 mask**；2B 容量取舍；**与视觉的分工**：RL 学「调什么」，视觉管「看哪儿」。
7. **评测协议**：WaveQA-RL（held-out，与训练**不同 FSDB**）；三层指标 = 量测准确率 / 端到端成功率 / 工具调用效率（步数）；**必须有两条参照线**：「无工具（纯看图）」与「Oracle Tcl」，否则无法证明 RL 增益来自学习而非工具；护栏 MMStar/MMBench ≤1pp；**预注册判据** + 决策树。
8. **成本与 ETA**：SFT / RL 各自 GPU·h；**采样吞吐以 wv 调用开销为瓶颈，不能只算 GPU**；pilot(N 题) → 全量 两档；风险登记表。
9. **落地与论文贡献**：从「烛龙的一个 tool」→「multimodal grounding 的实证」；给出**可写入烛龙 future work / 后续论文的实验设计**（变量、对照组、期望结论），并说明与 ZhuLong 现有 grounding 框架的关系。

#### ③ 必须复用的实测事实（repo 内已核实，直接引用标来源；**不要重新调研**）
来源：`doc/ZhuLong_DAC2027/benchmark/designflow/trace_deepreads/` 的 as67p / fa3cd 深读笔记。
- **后端**：`wv -ace_no_gui`（Tcl），比 fscript **快约 16x**。
- **可用 API**：`sx_open_sim_file_read`、`sx_signal`（不存在→**空句柄不抛错**）、`sx_wave_is_logic/is_analog`、`sx_number_of_bits`、`sx_wave_to_list`（**无时间戳**）、`sx_dump_hier`（只列 scope）、`sx_exit`。
- **崩溃阈值（必须进环境设计）**：单进程**连续调用 ≥5 次**即 S01 crash（`sx_crash.sx`），fresh tmp + `HOME` 隔离无效 ⇒ 工程实践**每次最多 3 次**。**决定 episode 动作预算与"重启环境"设计**。
- **真实踩坑（做成 RL 训练信号）**：① scope 前缀随仿真器变（FineSim SPICE 用裸名 `v(sig<0>)`，Verilog 用 `top.sig` 且 `v()` 包装不行）；② `sx_signal` 多参数时**静默丢弃**不存在信号；③ `.tbl` 头关键字是 `XVAL` 非 `TIME`，表头被**重写**为 `scope.v(net)`；④ 时间窗过滤会把「有信号但窗口内无点」滤成空，与「信号不存在」**同一句话无法区分**。这四条正是"看图猜"学不到、交互式 RL 必须学会区分的。
- **规模**：698 机 trace 中 waveform 368 命中（引既往报告）；案例 L2、每例 12 条 check。
- **模型侧**：BaiZe-2B MLLM（ArmE-R2 系），沿用既有报告的 Stage-1W/2W 设计。

#### ④ 纪律与红线
- 🚫 **只写计划书**：不训练、不起 RL、不跑 WaveView、不动 GPU。本机无 FSDB、无 license ⇒ 所有"实测"**只能引用既有落盘记录**，不可臆造。
- 🚫 数字标来源：实测写「实测（来源）」；推算写「**估算**」；拿不准写「待核」。**禁止估算冒充实测**。
- 🚫 不得声称「已跑通 RL / 已提升 XX%」——本轮零实验。
- 🚫 不得发明 WaveView API（清单外的标「待核」，注明需在 .75 沙盒验证）。
- 🚫 WaveView **不是可任意脚本化的开放环境**：license 与厂商合规单独成节（沙盒隔离 / 只读打开 / 不写回设计库 / 不反向工程）。
- 体积：任务书 **≤32KB**（>40KB 红线）；超了只归档**已闭合**块（本条未完成前不许归档）。
- 收尾：更新 `run/MEMORY_VISION.md` 心跳（写 `未完成指令：无`）→ `WAITING: 1`。



### [已完成] §运维直令·2026-10-30 22:2x（写「2B MLLM 看懂波形图」能力与评测报告）· ✅ 已完成（wake#424 2026-10-30 23:10 交付 `reports/report_vision_waveform_zh.html` 45236B/666行/6节/14表/0script/0外链/标签配平；覆盖任务定义(4类波形×4层看懂)/能力拆解(5层)/数据(合成+真实698机368命中)/训练(Stage-1W→Stage-2W·可选RL)/评测(WaveQA≥300题+MMStar/MMBench护栏≤1pp)/成本ETA(pilot 2万题/10GPU·h·全量10.6万/24GPU·h)；数字全溯源实测；只写报告不训练；commit 83591a2b1）

> **用户令**：「vision：写个报告，如何让2B MLLM能看懂波形图，如何具备能力，如何评测该能力。」

交付 `reports/report_vision_waveform_zh.html`（中文、单文件自包含、无外链），必须回答：
1. **任务定义**：波形图分几类（SPICE tran/ac 曲线、眼图、时序/时钟图、DRC/LVS 报告截图），各类要看懂什么（趋势 / 参数测量 / 异常定位 / 因果解释）。
2. **能力拆解**：分辨率与 anyres、轴刻度 OCR、几何量测（周期/幅度/上升沿/占空比）、多子图对齐、领域语义（器件/工艺）。
3. **数据**：合成波形（matplotlib 参数可控，自动生成"数值/比较/因果"三类 QA）+ 真实截图（698 机 trace 中 waveform 368 命中，可深读取样）；标注协议 + 一致性抽检。
4. **训练**：stage-1 对齐 → stage-2 专项 SFT（可选 RL）；2B 容量下的取舍（分辨率 vs token 预算）。
5. **评测**：自建 WaveQA（≥300 题，数值/多选/开放）+ ChartQA/DocVQA 迁移项；指标（数值相对误差、多选准确率、解释事实性）；**预注册判据**（目标 +X pp）与回归护栏（MMStar/MMBench 掉幅 ≤1pp）。
6. **成本与 ETA**：数据量/token 预算/GPU 小时/风险；给"最小可行 pilot（2 万题）"与全量两档。

🚫 本轮只写报告不训练；不伪造任何 API key 或评测数字。



> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### [已完成] §运维令·2026-10-28 17:3x（OCR 合成数据 10M 质量偏差裁定：接受现状）· 用户直令 · ✅ 已完成（wake#330 2026-10-28 18:0x）

> **用户裁定（2026-10-28）**：10M OCR 合成数据集（9,999,999 样本 / 2000 tars / 470GB）**接受现状（accept as-is）**。
>
> **裁定内容**：
> 1. 两处质量偏差**均接受**，不重生成、不做 index 过滤：
>    - ① 文本 SHA1 去重 2.4486%（>1% 目标，244,858 多余）—— 合成文本组合空间有限所致，可接受；
>    - ② 泄漏 113 命中（leak_rate=1.16e-5）—— 短串巧合（如 `0.29`→`029`），非真实泄漏，可接受。
> 2. 数据集 DATASET_CARD 中已有的偏差记录**保留不动**（如实披露原则）。
> 3. 该 10M 数据集可用于后续 vision encoder 预训练 / OCR SFT，**不需要再等待质量裁定**。
>
> **agent 执行清单**：
> 1. ✅ 在 `MEMORY_VISION.md` 顶部状态头中，将待等项 ①（22:4x 质量偏差裁定）标记为 **✅ 已裁定：接受现状**。
> 2. ✅ 在 `EXPERIMENTS_VISION.md` §18（OCR 合成 10M）补充 1 行：「2026-10-28 用户裁定：接受现状（accept as-is），不重生成/不过滤」。
> 3. ✅ 写心跳 + 日报 + commit（`vision ocr-accept:` 前缀）+ push。
> 4. ✅ 本指令完成后标 `✅ 已完成`。
>
> **注意**：本指令**只裁定数据质量**，**不启动** encoder 训练或 OCR SFT（仍需用户另行批预算 = 待等项 ②）。

### [已归档] §运维令·2026-10-26 08:2x（写最近工作报告 · 中文 HTML）**已完成**（wake#279 交付 `reports/report_vision_recent_work_zh.html` 40423B/5节+7子节/0 script/0外链/标签配平/≥15KB + 生成器 `vision/generate_recent_work_report.py`；覆盖 ArmD-R2/ArmE发散→ArmE-R2(ProtB lp 68.236 vs ArmD-R2 64.34·12集 26.10%不可分辨·传递性)/Stage-2 原版780k/OCR 调研·SFT方案·10M合成数据集(470GB/2000tar·去重2.4486%/泄漏113如实披露)；数字全溯源 EXPERIMENTS §14-§18；commit 847ce67eb）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-25 22:4x（生成 1000 万 OCR 图文对，供 vision encoder 预训练）**已完成** （wake#275 全量 DONE ok=9,999,999/fail=0/2000 shard tars+preview_10k.tar/470GB(0.5046TB)/893.6 img/s/3h6m30s · 8 类 cat_counts==plan · 加载器兼容已验真 build_gpic_loader→(16,3,224,224) finite · 报告 `reports/report_vision_ocr_synth10m_zh.html`(15754B/8节/0 script/0外链) + 5 脚本 `vision/ocr_synth/*.py` + EXPERIMENTS §18 + index.jsonl(9.999M) + STATS/VALIDATION/DATASET_CARD/MANIFEST + preview_200.html + preview_10k.tar；wake#276 复核完整性一致）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。**两处质量偏差如实记录**：①文本 SHA1 去重 2.4486%>1% 目标（dup_pass=false，留 9,755,141 唯一 / 244,858 多余；合成文本组合空间有限所致）；②泄漏 113 命中（leak_rate=1.16e-5，短串巧合如 0.29→029 非真实泄漏；内联护栏路径错为空操作，真实复检读 OCRBench/DocVQA/ChartQA parquet；InfoVQA parquet 未找到）。**待用户裁定**：接受 / index 过滤补救（留 9,755,141 唯一）/ 扩语料重生成。本轮只造数据不启 encoder 训练（等用户批预算）。需要时再读。

### [已归档] §运维令·2026-10-25 19:5x（路线①细化为执行方案报告）**已完成**（wake#272 交付 `reports/report_vision_ocr_sft_plan_zh.html` 22,706B / 9 节 + 一页纸清单 / 0 script / 0 外链；配比 英30/中20/混排10/文档15/图表10/公式10/低质手写5，SFT=ArmE-R2 stage3500+LoRA r64+LR1e-5+70:30 混 780k，判据 OCRBench >=+2pp）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-25 17:5x（OCR 类评测偏低：web search 调研「合成数据补强 OCR」并写报告）**已完成**（wake#271 交付 `reports/report_vision_ocr_synthdata_zh.html` 29177B/8节/0 script/0外链/标签配平/≥15KB + 生成器 `vision/generate_ocr_synthdata_report.py` + EXPERIMENTS §16；四臂四集实测+7类18法调研；单一建议=路线①低成本合成OCR识别对+专项SFT，判据 OCRBench≥+2pp；commit `vision ocr-report:`）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维指令·2026-10-24 16:1x（写「下一步如何提升 ProtB 与 MLLM 成绩」报告）**已完成**（wake#250 交付 `reports/report_vision_next_steps_protb_mllm_zh.html` 21.1KB / 8 节 / 0 script / 0 外链，后续 A3 + B4 已执行）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

### [已归档] §运维指令·2026-10-24 10:3x（ArmE-R2 完整实验报告）**已完成**（wake#247 交付 `reports/report_vision_armE_r2_20261024_zh.html` 26,522B / 7 节；wake#267 复核仍在位）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

> **已归档**（2026-10-24 11:43）：ArmE 停止降 LR 重跑 / 启动 ArmE（ViT-L14）/ Stage-2 改原版 780k 三块 —— 原文均在 `run/ARCHIVE_OPERATOR_VISION.md`。


### 📦 运维指令 · 2026-10-20 08:2x（**ArmD-R2：LR 1e-3 / min_LR 1e-5 / 数据不变**）· 用户直令 · 最高优先 — 已归档

> **已闭合**（ArmD-R2 全链路 DONE 2026-10-21：①训练✅63400步 / ②ProtB✅lp64.3373·5-NN55.956 / ③MLLM三阶段✅Stage-2原版数据 / ④12集✅avg26.12% / ⑤报告✅）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-21 归档）。**结论**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp/Δ5-NN+1.238pp 双双正向；MLLM下游几乎持平→ProtB→MLLM传递性再次证伪。ArmD-R2 是 ArmE 的对照基线（口径值见上方 ArmE 块口径表）。需要时再读。
> **已归档**（2026-10-24 11:43）：🔥 运维令 · 2026-10-19 22:5x（**立即启动 ArmD，不要再 idle**）· 用户直令「vision：尽快启动」 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 📦 已归档（08:2x）：ArmD 原始块（2026-10-19 21:2x）

> 已被 **08:2x「ArmD-R2」块**取代（LR 2e-3→1e-3，数据不变）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-17（📄 ArmA 中文报告 + 🔌 open_clip×AIMv2-style 兼容性工程评估）**已完成**（wake#133 交付 `run/reports/report_vision_armA_openclip_result_zh.html` 249行/§1-§6+附录A兼容性(模型/推理兼容·loss/训练环不兼容·4步做法+代码行号)+附录B官方AIMv2 vs 本仓AIMv2-style概念澄清；数字全溯源 EXPERIMENTS §10(lp58.03±0.02/5-NN53.98/Δlp−9.02pp·Δ5-NN+11.63pp·非单变量·不得写「AIMv2好9pp」)；commit `vision armA:` 2f15f88eb；③ArmB 已被12:0x取代并训完评完）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`（wake#285 补标+归档）。需要时再读。


> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> 不得回退：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---


> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）


- 🚫 不许闭门造车：涉及"别人怎么做"（架构/loss/评测/数据）必须去读官方仓库或论文原文（能 clone 就 clone）—— 不得凭二手描述下结论（本线已因此出错一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂必须报「参数量 + 训练 token + 每步耗时」，不许只比 acc。
- 预注册：判据先定后测，不许事后改。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ 21KB、`MEMORY_VISION.md` ≈ 32KB（已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_VISION.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的巡检/流水条目（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
