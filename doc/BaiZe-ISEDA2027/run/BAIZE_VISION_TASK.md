# BAIZE_VISION_TASK.md
### 🚀 运维令 · 2026-10-31 16:0x（**把 ViT-L 68.236% + MLLM 11 集 26.10% 写进论文：ch6 / ch7 / 摘要 / intro，MME 只呈现不计均值**）· 用户直令 · 最高优先

> **用户原话**：「vision 可以汇报 openclip + ViT-L 的结果嘛，不是达到 60+%嘛」「而且这个结果还有 MLLM 12 集的结果对吧，这个表格也可以报在 MLLM 这节啊。安排 vision 去更新一下，第6章第7章摘要和 intro 都更新一下。」「好的 MME 只呈现 不参与取均值」

**改动范围**：`6_vision_encoder.tex`、`7_mllm.tex`、`0_abstract.tex`、`1_intro.tex`。**只改这 4 个文件**（其余章节由 pretrain 线管）。

#### ① 必须写进论文的两组实测（运维已核，直接引用，禁止改写数字）
**A. 编码器（ProtB 线性探测，3 seeds）** —— `run/vision/armE_r2_20261022_protb_vitl14_224_results.json`
| | ArmE-R2 (ViT-L/14, 304M) | ArmD-R2 (ViT-B/16, 86M) | Δ |
|:--|--:|--:|--:|
| lp top-1 | **68.236 ± 0.018** | 64.337 | **+3.90** |
| 5-NN | **58.904** | 55.956 | +2.95 |
（另：ckpt60000 = 68.3067 ± 0.0155 / 5-NN 59.002；ArmC 62.332、ArmB 62.093）

**B. MLLM 下游（12 项 lmms-eval，Stage-2 step3500）** —— `EXPERIMENTS_VISION.md` §15.5
| 集 | ArmE-R2 | ArmD-R2 | 集 | ArmE-R2 | ArmD-R2 |
|:--|--:|--:|:--|--:|--:|
| ai2d | 60.65 | 60.49 | countbench | 10.59 | 9.98 |
| realworldqa | 45.36 | 46.41 | docvqa_val | 7.35 | 7.44 |
| mmmu_val | 44.00 | 42.67 | ocrbench | 1.60 | 1.60 |
| blink | 38.88 | 39.59 | infovqa_val | 16.18 | 16.59 |
| mmstar | 27.17 | 27.07 | chartqa | 12.16 | 12.92 |
| mmmu_pro | 23.12 | 22.60 | **11 集平均** | **26.10** | **26.12** |
| MME（**仅呈现，不计均值**） | perception 596.75 / cognition 250.71 / total 847.46 | 见源文件 | | | |

#### ② 三条硬性口径（**写错即返工**）
1. **MME 不进平均**：均值只对 **11 集**取算术平均（**26.10%**），MME 单列呈现原始分（perception/cognition/total）。🚫 **不得写「12 集平均」**。表格里 MME 那行要标明「not included in the mean」。
2. **不得把 68.236% 和 19.76% 混为一谈**：两者是**不同模型**——
   - **19.76%** = OpenVision2 **w512（126.8M）**，AIMv2-style，单 epoch 子集
   - **68.236%** = **ViT-L/14（304M）** + open_clip，**不同塔、不同规模、不同训练配方**
   - 论文里必须明确区分；ch6 现在只写了 w512，要补上 ViT-L 这一档。
3. **三变量+容量混杂，禁止单变量归因**：ArmE-R2 vs ArmD-R2 的 Δlp=+3.90pp 是 **塔容量(B→L, 86→304M) + peak LR(1e-3→5e-4) + warmup(2000→3000)** 三项共同作用。🚫 **不得写成「ViT-L 比 ViT-B 好 3.9pp」**。原文措辞见 `EXPERIMENTS_VISION.md` §15.1/§15.3 的红线注。

#### ③ 论文怎么组织（**别只堆表，要出论点**）
论文的真发现是**「编码器指标 ↑ 但下游不 ↑」**：
- ch6 报 **ProtB 68.236%**（编码器质量档位，含 w512 与 ViT-L 两档对比）+ 三变量混杂声明
- ch7 报 **11 集平均 26.10% vs 26.12%（−0.02pp）** + MME 单列
- 两章一起支撑这个判断：**编码器 ProtB 领先 3.9–5.9pp，但 MLLM 下游持平 ⇒ 瓶颈不在视觉塔容量，而在别处（224px 单块、MLLM 架构、或代理任务与下游的传递性）**。这比只报高位数更有分量，也是实验记录自己给出的结论（§15.6 第 3 条）。

#### ④ 诚实性条款（必须进正文，可压成一句）
> 内部 ProtB / lmms-eval 口径，非官方榜；单 backbone、单预算点；MLLM 三阶段单 seed；224px 单块（无 anyres），细粒度任务天然偏低；Stage-2 用原版 quick-start 数据。

#### ⑤ 篇幅（**硬约束**）
- 全文正文 **≤6 页**（参考文献不计）。ch6 预算 **≤0.6 页**、ch7 **≤0.8 页**。
- ch7 原有的 `[TBD]` 删除，改为真实结果。
- 每改一次跑 `pdflatex→bibtex→pdflatex×2`，**ERR=0 / UNDEF=0**，实测页数；超页按「删论证、保数字」取舍。
- 🚫 **不 commit `main.pdf`**（pretrain 线同批在改）。
- `% 中文：` 双语注释行**不得删**，改写时同步更新中文。

#### ⑥ 摘要与 intro
- **摘要**：加一句视觉侧实测（可写「vision encoder reaches 68.2% linear-probe on an internal protocol; the MLLM stage averages 26.1% over 11 multimodal benchmarks」）。🚫 摘要里**不得只挑 68.2% 而不提下游持平**，否则误导。
- **intro**：把「五阶段」叙述里的 (iii)(iv) 从「设计」改为已有实测，一句话即可。
- 两处都只加**一句**，不得膨胀。

#### ⑦ 交付
1. 改稿 commit `vision paper:` + push（只 add 这 4 个 `.tex` + 自己的报告，先 `git pull --rebase`）。
2. `reports/report_vision_paper_results_zh.html`（中文/单文件/0 script/0 外链/**≥15KB**）：两组结果全表（含 MME 单列）+ 论文里怎么写的 + 三变量混杂说明 + 篇幅账 + 页数实测。
3. `MEMORY_VISION.md` 顶部登记（含 ERR/UNDEF/页数）。

#### ⑧ 红线
- 🚫 只改这 4 个文件；**不动 `4_llm_pretrain.tex` / `3_architecture.tex`**（pretrain 线在审订）。
- 🚫 **不伪造**：表中每个数字必须能在 `armE_r2_20261022_protb_vitl14_224_results.json` 或 `EXPERIMENTS_VISION.md` §15.5 找到。
- 🚫 不得把 MME 当百分比混入均值。
- 🚫 不得恢复六架构对比 / SSM 崩溃 / AR 范式 / Muon 等已删内容。
- 提交前 `git pull --rebase`；push 被拒重试，失败写进心跳。
- 体积：本令未完成前**不得归档**。

### [已完成] 🚀 运维令 · 2026-10-31 11:2x（**直接重写第 6 章 `6_vision_encoder.tex`，提交并推送**）· 用户直令 · 最高优先 · ✅ 已完成（wake#437+#439 2026-10-31 14:0x 交付 6_vision_encoder.tex 18行/6页/ERR=0/UNDEF=0 + report_vision_paper_edit_zh.html 10429B + commit f2ca45de5/e5145dc85）

> **用户原话（2026-10-31 11:2x）**：「请 vision 自行修改 第6张视觉编码器 并推送&提交；各自注意篇幅」

**背景**：论文已压到 ISEDA **6 页**（正文+参考文献均在 6 页内）。第 6 章现在是运维按「只留最终结果」临时写的 **0.3 页占位版**（3 段 + 2 个 `\paragraph`）。09:4x 的「出计划」令由本令**升级为直接改稿**：计划内容并入本轮变更说明即可，不必先单独交计划。

#### ① 重写内容（只留最终结果）
写实保留：选定 **OpenVision2（126.8M / width 512）** · 目标函数（InfoNCE + 掩码块重建 1:1、掩码率 0.6）· 最终 **lp top-1 19.76% @55.3M / 20.27% @176M** · **+12.4pp vs 对比基线** · **224/16（196 token）** · 「196 token 能否迁移到细节密集视图」留给 stage (iv) 测试。
🚫 中间过程**一律不进正文**：六架构对比 / SSM 崩塌 / AR 范式探索 / Muon 消融 / ProtB-epoch 缩放 / AIMv2 消融 —— 只在变更说明的「已删清单」里点名，**不许塞回论文**（用户明确要 6 页）。

#### ② 事实核对（改稿前必做）
- 每个数字到 `run/EXPERIMENTS_VISION.md`（§R8–R13）与 `run/MEMORY_VISION.md` 找证据，变更说明里给 **文件 + 行号**；无实测写「估算/待核」，🚫 不许估算冒充实测。
- 重点核：**参数口径**（旧稿曾写 width-1024/126.8M，实际 **w512 = 126.78M**）· `+12.4pp` 的基准是谁 · `20.27%` 与 `19.76%` 是否可比（不同 token 预算）· 「两个损失项都必需」表述是否过强（**有消融证据才写**）。

#### ③ 篇幅硬约束（用户点名「注意篇幅」）
- 第 6 章预算 **≤1.5 页**（目标 ~1 页）；全文（正文+参考文献）**≤6 页**。
- 改完 `pdflatex → bibtex → pdflatex → pdflatex` 三连：**ERR=0 / UNDEF=0**，实测页数；超页自行压缩（删形容词/合并段落，**不删实测数字**）。
- 🚫 **不 commit `main.pdf`**（pretrain 线同批在改，二进制必冲突；最终 PDF 由运维统一编译提交）。
- 🚫 不动 `0_abstract.tex` / `1_intro.tex` / `4_llm_pretrain.tex`（pretrain 线本轮在改）；提交前 `git pull --rebase`，只 `git add` 自己的 `.tex` + 报告。

#### ④ 交付
1. commit `vision paper:` + push（消息写清页数与 ERR/UNDEF）。
2. `reports/report_vision_paper_edit_zh.html`（中文/单文件/0 script/0 外链/≥10KB）：逐段「改前→改后」+ 事实依据（文件+行号）+ 页数实测 + **已删中间过程清单**（证明没把用户删掉的内容塞回）。
3. `MEMORY_VISION.md` 顶部登记。🚫 不启训练、不占 GPU。

> 📦 体积：本令约 2.0KB，任务书入令后约 38.9KB（**<40KB 红线**）；需瘦身可归档已标 `[已完成]`/`[已归档]` 块，🚫 **不得归档本令**。



> 📦 §运维令·2026-10-31 11:0x（审校第6章出修订计划）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#436 交付 report_vision_paper_revise_plan_zh.html，已被 11:2x 令升级为直接改稿并执行完毕。需要时再读。



> 📦 §运维令·2026-10-31 08:4x（波形图强化RL计划书）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#435 交付 report_vision_wave_rl_plan_zh.html 59241B/12节，覆盖9个必答问题+WaveView API实测事实引用。需要时再读。



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
