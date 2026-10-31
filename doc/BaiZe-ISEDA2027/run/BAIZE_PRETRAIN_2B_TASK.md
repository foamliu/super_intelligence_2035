# BAIZE_PRETRAIN_2B_TASK.md
### 🚀 运维令 · 2026-10-31 11:2x（**直接落地改稿：`4_llm_pretrain.tex` + 刷新摘要/intro 等章节，提交并推送**）· 用户直令 · 最高优先

> **用户原话（2026-10-31 11:2x）**：「请 pretrain 自行修改 4_llm_pretrain.tex 并推送&提交；请 pretrain 把摘要、intro等其他章节也刷新；各自注意篇幅」

**背景**：上一令（10:0x）你已交 `reports/report_pretrain_paper_revise_plan_zh.html`（1 P0 + 6 P1 + 6 P2 + 7 段改前→改后）。**本令解除「只出计划不改 tex」的限制：直接改稿、commit、push。**

#### ① 改 `BaiZe-ISEDA2027/ISEDA2027/4_llm_pretrain.tex`（按 #998 计划逐条落地）
1. **P0 必修**：`88--176B` → 实值 **`83.9B`**（占 2.94T 的 **2.85%**），写清推导（基数 × 比例），不许留歧义。
2. **6 条 P1 全处理**：`88:8:4` → **`74:19:7`**（或保留 88:8:4 但注明「BO design prior，实测 74:19:7」）· `92 GPU·h` → **`~82`** · `41.6K` → **`39,377`** · 补回 `\cite{openbmb2026minicpm5}` · 补半句解释 **warmup 2000（生产，0.29%）vs 250（搜索，5%）** · 补回 **Feasibility（Megatron-Core 复用 56 层）** 一句。
3. 6 条 P2 一并处理（可并入上述改写）。
4. 🚫 不得改坏 #998 已标「✅ 属实」的数字；🚫 不伪造未实测值（无实测写「估算/待核」）。
5. `% 中文：` 双语注释行**不得删**，改写英文时同步更新中文。

#### ② 刷新 `0_abstract.tex`（**当前有硬伤，必改**）
- 现文仍写 **`44B / 1.357 / 412 GPU-hours`** —— 废弃旧口径，与第 4 章（2.94T / loss 2.151 / ~82 GPU·h）**直接冲突**。
- 改为与 ch3/ch4 一致：2.22B 参数 · 56 层混合（4 层 attention）· **2.94T token / 700k 步（GBS 256 × 16K）** · S1 实测 **iter 30,660 / loss 2.151 / 598K tok/s** · 峰值 **613,992 tok/s** · 搜索预算 **~82 GPU·h**。
- 摘要其余每个数字都与对应章节对账；对不上就改摘要（摘要服从实测），并在变更说明列清单。

#### ③ 刷新 `1_intro.tex` 等其他章节
- `1_intro.tex`：口径统一到 ch4（两段制 WSD、ABF θ=1e6 / max_pos=1M、2.94T、2.22B），删改与实测不符的句子。
- 顺带扫 `2_related_work.tex` / `5_llm_posttrain.tex` / `9_conclusion.tex` 中**凡出现旧口径（44.4B / 1.357 / 412 GPU·h / 44B）或与 ch4 冲突的句子**一并修正（只改本线事实句，不改论证结构）。
- 🚫 **不动 `6_vision_encoder.tex`（vision 线本轮在重写）**；🚫 不动 `7_mllm.tex` 正文。

#### ④ 篇幅硬约束（用户点名「注意篇幅」）
- 全文（正文 + 参考文献）**≤ 6 页**；第 4 章预算 **≈1.6 页**，改稿不得膨胀。
- 每次改完 `pdflatex → bibtex → pdflatex → pdflatex` 三连，**ERR=0 / UNDEF=0**，实测 PDF 页数；超页按「删中间过程、保最终数字」自行取舍。
- 🚫 **不 commit `main.pdf`**（vision 线同批在改，二进制必冲突；最终 PDF 由运维统一编译提交）。
- 提交前 `git pull --rebase`，只 `git add` 自己的 `.tex` + 自己的报告。

#### ⑤ 交付
1. commit `pretrain paper:` + push（消息写清改了哪几个文件 + 页数实测）。
2. `reports/report_pretrain_paper_edit_zh.html`（中文/单文件/0 script/0 外链/≥10KB）：逐条「改前→改后」+ 证据（文件+行号）+ 页数实测 + 未采用项及原因。
3. `MEMORY_PRETRAIN_2B.md` 顶部登记（含页数、ERR/UNDEF）。🚫 不碰 GPU、不打断 S1（iter ~30,660/700k）。

> 📦 体积：本令约 2.1KB，任务书入令后约 34KB（**<40KB 红线，允许**）；需瘦身可归档已标 `[已完成]` 的 10-31 09:1x 块，🚫 **不得归档本令**。



### 🚀 运维令 · 2026-10-31 11:0x（**审校 BaiZe 论文第 4 章「预训练」，出中文 HTML 修订计划**）· 用户直令 · 最高优先

> **用户令**：「让 pretrain 和 vision 看看 BaiZe 论文中各自的章节，出一版中文 HTML 修订计划：哪里跟事实不符，计划怎么改。」

**背景**：论文已压到 ISEDA 6 页正文（实测全文 6 页，参考文献也在内）。你的第 4 章被我按用户指示**大幅压缩**：
- 12 小节 → **7 小节**，13 张表 → **5 张表**，文件 63KB → 20KB
- 删掉的：`Why the budget is this small`（文献对比）、mixture-BO 详细论证、独立 Search Budget 小节，以及 8 张表（`tab:wsd`/`tab:stable-blend`/`tab:longctx-budget`/`tab:mix-topk`/`tab:llm-stages`/`tab:longctx-eval`/`tab:longctx-ppl`/`tab:longctx-cost`）
- **压缩是我做的，可能有事实错漏 —— 这正是要你审的。**

#### ① 先读
```
cd doc/BaiZe-ISEDA2027 && git pull --rebase
cat BaiZe-ISEDA2027/ISEDA2027/4_llm_pretrain.tex          # 当前压缩版（~170 行，含中文注释）
git show f4db0347d                                        # 压缩提交（含 diff）
git show e85e5dc68 --stat                                 # 同一次修正
```
对照源：`code/baize-llm/configs/*.env`、`run/MEMORY_PRETRAIN_2B.md`、`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`、`code/baize-llm/docs/LONGCTX_ABF_PLAN.md`。

#### ② 运维已知的疑点（**逐条核实并给结论**）
1. **压缩是否导致失实（P0）**：我把 13 张表压到 5 张、把长上下文 7 个小节压成 2 节。**请逐句核对现文的每个数字与断言**，凡因压缩而走样、断章取义、丢掉前提的，全部列出。重点核：`2.94T`/`3.02T`/`700k`/`14k`/`6k`、`613,992`、`351,526`、`iter 30,660`、`loss 2.151`、`598K tok/s`、`2.52%/0.03%/889`、`2.2054`/`2.6739±0.0469`。
2. **`88--176B` 长上下文预算**：现文写「LC 占 decay 的 30–40%，即 $88$–$176$B」。核：基数用的是 decay 的 10% 还是 15%？下界 88B 对应 10%×30%？表述是否自洽？
3. **`tab:longctx-train` 的 64K/128K 吞吐（≈180K/≈90K）**：仍是**外推**，表里标了 (est.)。核是否属实，或能否实测回填。
4. **`§4.1 架构选型` 只留两句**：丢掉了原来「Feasibility: Megatron-Core 复用 56 层模式」那条理由。判断是否该补回一句。
5. **`§4.7 长上下文能力与推理成本`**：我把 PPL 表和推理成本表压成了一段文字，PPL 值 `83.2→51.5→53.3→53.0→55.8→55.4` 与原表是否完全一致？`41.6K tok/s`、`172s`、`34.7GB`、`455K` 是否属实？
6. **`§4.4 数据`**：把 7 源比例写成了一句话，比例值与 `configs/blend_s1_preblend.tsv` 是否一致（0.65/0.05/0.04/0.05/0.02/0.15/0.04）？

#### ③ 交付物（唯一硬交付）
`reports/report_pretrain_paper_revise_plan_zh.html` —— 中文、单文件自包含、**0 `script`/0 外链/0 CDN**、标签配平、**≥20KB**；生成器 `pretrain/generate_paper_revise_plan_report.py`（幂等）；commit `pretrain paper-plan:`，push。

**必须含 6 节**：① 现状逐句摘录 + 标注「✅属实 / ⚠️存疑 / ❌不符事实」+ 证据（文件+行号）；② 不符事实清单表（位置/现文/事实/来源/严重度 P0-P2）；③ **改写方案（可直接替换 `.tex` 的英文目标文本，逐段「改前→改后」）**，且**必须守住 6 页正文上限**；④ 篇幅账（当前第 4 章约 1.6 页，改写后预计多少，如何不超）；⑤ 仍需的实验（无实测支撑的数字如实列出）；⑥ 自检清单。

#### ④ 红线
- 🚫 **本轮只出计划，不改 `.tex`**（改稿等我确认后下一轮做）。
- 🚫 **不伪造数字**；未实测写「待核」或「估算」，禁止估算冒充实测。
- 🚫 **不得把已删内容整段塞回**（用户明确要 6 页）：需要恢复的内容只能在计划里说明，并给出「为腾版面删掉哪段作为交换」。
- 🚫 只谈 `4_llm_pretrain.tex` + `reference.bib` 本线条目；不动 `6_vision_encoder.tex`（vision 线负责）。
- 🚫 章节里有 `% 中文：` 双语注释行，**不得删**；改写时同步更新中文。
- 🚫 **不碰 GPU / 不打断 S1 训练**（当前 iter ~30,660/700k）。
- 体积：任务书 ≤32KB；本令未完成前不许归档。

### [已完成] 🚀 运维令 · 2026-10-31 09:1x（**接手维护 BaiZe 论文「预训练」章节**）· 用户直令 · 最高优先

> **用户令**：「下发指令给 pretrain agent 去改（论文预训练章节）。」

**背景（先读，决定你改什么）**：运维上一轮已经**手工改过一遍**并已 commit 入 main（`c40b6faf0`→rebase 后 `3c82ffe01`，标题 `BaiZe paper: pretrain 章节改写——删除 44.4B 旧生产跑，新增 WSD decay 两段制与长上下文训练`）。从**本轮起，论文预训练章节由你（pretrain 线）负责维护**；运维不再代替你改。**你的任务 = 在既有修订基础上做专业化审校与补全，不是从零重写。**

#### ① 先读懂现状（本轮第一步，禁止跳过）
```bash
cd doc/BaiZe-ISEDA2027 && git pull --rebase
git log --oneline -5 -- BaiZe-ISEDA2027/ISEDA2027/4_llm_pretrain.tex   # 看运维改了什么
git show 3c82ffe01 -- BaiZe-ISEDA2027/ISEDA2027/4_llm_pretrain.tex      # 逐行 diff（主修订）
git show 9337de26e                                                      # 伪造引用勘误
```
结构（14 小节，**4.3 / 4.6 / 4.11 为新增**）：4.1 架构选型 → 4.2 NeMo 框架 → **4.3 WSD 两段 decay** → 4.4 生产前搜索 → 4.5 数据 → **4.6 长上下文数据前置条件** → 4.7 混比搜索 → 4.8 搜索预算 → 4.9 搜索结果 → 4.10 全量生产 → **4.11 长上下文训练（主体）** → 4.12 能力与推理成本。

#### ② 本轮必须做的 6 件事
1. **事实核校（最高优先）**：每个数字与 `code/baize-llm/configs/*.env`、`run/MEMORY_PRETRAIN_2B.md`、`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 对账。重点：`2.94T`、`4.19M/step`、`700k/14k/6k 步`、`3.02T`、`613,992`、`351,526`、`29,900 iter`、`2.166 loss`、`~590K tok/s`、`2.52%/0.03%/889`。不符立即改，并列「原值→新值→证据」。
2. **更新 4.10 的「in progress」**到执笔时的真实 iter/loss/tok/s/ckpt（现 #995 = iter 30660、loss~2.151、~598K tok/s、ckpt@30000）。必须写「at the time of writing + 日期」，不留会过期的裸数字。
3. **64K/128K 吞吐**：表 11 里 ≈180K/≈90K 是外推。能实测就回填，**不能测就保留 est.，禁止改成「实测」**。
4. **审校 4.11 三条强主张**：「2.2B 长文数据需求不高于 8B 级」「25–176B 位于公开量级之上（保守）」「decay-B 不回升 LR」——站不住就按本项目口径改写并给依据，别照抄。
5. **补 decay-A 内容**：至少写清配比来源（`configs/blend_decay.tsv`：SFT-2605 0.60 / Agent-2609 0.12 / ufw_en_l3_qa 0.18 / ufw_zh 0.04 / math_l3 0.04 / code_l3 0.02）与「为何先 16K 退火再进长上下文」的因果，别只写 queued。
6. **编译验收（硬门禁）**：
```bash
cd BaiZe-ISEDA2027
pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
grep -c '^!' main.log                                   # 必须 0
grep 'LaTeX Warning: \(Reference\|Citation\)' main.log   # 必须空
grep 'Overfull \\hbox' main.log                          # 允许 2 条，均在 6_vision_encoder.tex
```
🚫 编译不过不许 commit。

#### ③ 已知遗留问题（本轮一并处理）
- **`chen2024dataeng` 已由运维处理完毕（2026-10-31）**：该条目在 arXiv 上**不存在，属伪造引用**（连同「128K 只需 0.5–5B token」的说法一起删除）；现 §4.11 只引 **已核实的** ProLong-8B（ACL 2025，40B token）与 LongRoPE2（arXiv 2502.20082，10B token），论证方向改为「我们 25–176B ≥ 公开量级，属保守；该预算是 floor 不是 ceiling」。**你不需要再查这条**；但若你在审校中发现其它引用可疑，按同样纪律处理：**查不到就删，不许凭记忆保留**。
- `4_llm_pretrain.tex.bak_annotated`（已删除，别重建）：改动对照靠 `git show 3c82ffe01` 即可，**不要在 `ISEDA2027/` 目录下留任何非编译输入的副本**。
- 摘要 `0_abstract.tex` 仍写「≈44B tokens / final loss 1.357 / ≈412 GPU-hours」，**与新正文矛盾**。本轮**不改摘要**（跨章节，另派），但要在回复里指出并登记待办。

#### ④ 红线
- 🚫 **不碰 GPU / 不打断 S1**（700k 步是主线）；写作纯 CPU。
- 🚫 **不伪造数字**：未实测写 `estimated`，拿不准写「待核」；禁止估算冒充实测。
- 🚫 **只改 `4_llm_pretrain.tex` + `reference.bib` 本线条目**；其它章节（abstract/intro/arch/posttrain/vision/mllm/domain/conclusion）**只报告不改**。
- 🚫 `.tex` 里不许留 `<!-- CHANGED -->` 标注。
- commit 前缀 `pretrain paper:`，**message 逐条列「改了哪些数字+依据」**；push 被拒就 rebase 重推，失败写进心跳。

#### ⑤ 交付与收尾
- 交付 = 可编译的 `4_llm_pretrain.tex`（0 error）+ commit + push；
- 心跳给出：① 核校数字与改动处数；② 编译证据（`^!` / 未定义引用 / Overfull / 页数）；③ 待办（摘要口径、64K/128K 实测、`chen2024dataeng`）。
- 体积：任务书 **≤32KB**（>40KB 红线）；已归档 10-30 的 1M 报告令腾空间，**新令未完成前不许归档**。



### [已完成] 🚨 2026-10-30 22:2x 运维直令：写「1M 长上下文 + 95% 大海捞针」技术报告 · ✅ 已完成（#983 2026-10-30 23:17 交付 `reports/report_pretrain_1m_needle_zh.html` 33,667B/6节+总结路线图/0 script/0外链，覆盖现状基线-怎么做到1M-怎么到>95% needle-实验矩阵6组-取舍建议-与Qwen/Llama3对比；commit d0424c1f1）→ 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-10-31」节。需要时再读。



> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 📦 §运维令 2026-10-29 14:1x（整理并提交 baize-llm 独立仓库）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：✅ commit e1c6be4 pushed to origin/master，28 files（README 19.6KB + configs/9 + scripts/18 + docs/2 + .gitignore），symlink 已删除+纳入 .gitignore，ls-remote 匹配。需要时再读。

### [运维令] 2026-10-28 17:0x（**预训练项目目录定位：脚本&文档落在 `/nas_train/app.e0031982/code/baize-llm/baize-llm`，后续训练从此启动**）· 用户直令 · 最高优先

> 用户原话（2026-10-28 17:0x）：「安排 pretrain 往项目目录 /nas_train/app.e0031982/code/baize-llm/baize-llm 写脚本&文档。后续训练从项目目录启动。」

**① 项目目录定位（运维已核现状）**：`/nas_train/app.e0031982/code/baize-llm/baize-llm` 当前是 symlink → `super_intelligence_2035/code/baize-llm`（已含 `configs/`/`scripts/`/`docs/`/`README.md` 14.3KB）。外层 `/nas_train/app.e0031982/code/baize-llm/` 是独立 git 仓库（README 仅 582B、另有 symlink）。

**② 要求**：脚本（`train.sh`/`pre_blend.py`/`gen_blend.py`/`check_rope.py`/`check_longctx_data.py`/`activate_preblend.sh` 等）与文档**全部落在该项目目录并 git 提交**；`README.md` 补全到「从零按 README 即可在项目目录启动训练」的程度（目录结构 / 启动命令 / 三阶段 S→S2→Decay 口径 / 配置说明 / 依赖环境）。

**③ 后续训练启动口径（硬性）**：一律 `bash /nas_train/app.e0031982/code/baize-llm/baize-llm/scripts/train.sh <stage>` 启动；🚫 不再从 `run/` 散落脚本启动。`common.env` 的 `BAIZE_TRAIN_CODE` 与启动文档与此路径对齐。

**④ 优先级**：不打断主线——先续跑 en_v1_4 pre-blend 剩余 s012-s015 → activate → 起 S（双机 16 卡 GBS256）；本令的「脚本&文档落项目目录」可在起 S 后的空档补齐。

commit `pretrain 项目:`。

> 📦 §运维令 2026-10-28 11:5x（blend 逻辑中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：报告已交付 `reports/report_pretrain_blend_logic_zh.html`（11KB, commit aa6d3eddf），澄清训练时不会串行出不同源（索引层交错）。需要时再读。

> 📦 §运维令 2026-10-28 10:0x（预训练计划定稿）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31」节；**结论**：计划已定稿并执行，GBS=256/2.94T/700k运行中，pre-blend完成/nw=8恢复/613K，Decay后置待data线。需要时再读。

> 📦 §运维令 2026-10-28 09:3x（锁定 613K 配置 + spawn 调优）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：613K 配方已冻结（16K/CP1/DP16/FP8/graph-OFF），根因=数据加载串行化(nw=0)，spawn 路径被 10:0x pre-blend 取代。需要时再读。

> 📦 §运维提示 2026-10-27 15:2x（cimi MCP web search 已配好）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：MCP 工具就绪（cimi_search/cimi_fetch/vqa/text_to_image），授权永久有效。需要时再读。

> 📦 §运维令 2026-10-27 13:1x（杀掉 S1 + spawn smoke）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：S1 已杀，spawn 方案被 2026-10-28 10:0x pre-blend 取代。需要时再读。
> 📦 §运维令 2026-10-27 10:4x（不放弃：spawn 验证 + web 调研）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：spawn 被 pre-blend 取代；web 调研授权仍有效（见 15:2x）。需要时再读。
> 📦 §运维提示 2026-10-27 09:2x（DataLoader OOM fork-COW 根因 + spawn 方案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：fork-COW 是 RSS 累积根因，spawn 方案被 pre-blend 取代。需要时再读。

> 📦 §运维提示 2026-10-27 08:4x（内存使用率>95%触发告警）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：内存纪律已纳入日常监控，调试时盯内存+swap，逼近95%先降载。需要时再读。

> 📦 §运维令 2026-10-26 22:0x（S1 吞吐对齐 613,992：归因 + 方案 A/B/C）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#798 归因=gbs128 固定开销摊薄不足；吞吐目标 ≥600K 由后续 10:4x/13:1x 令推进（spawn 验证中）。参数口径 2.220B 仍有效。需要时再读。


> 📦 §运维令 2026-10-26 21:3x（RoPE θ 未生效：评估 + 方案 + 重启）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：θ=1e6 实现路径(ii) `--rotary-base` CLI + recipe 透传，commit ae3a093，三重验证 PASS；#799 运行时确认 θ=1e6 + 0崩；rank15 崩因=DDP DETAIL wrapper（非θ）；--dir 修正已落地。**仍有效红线**：check_rope.py PASS 需 ckpt（待 S1 重启）；lr-decay-shape exponential Decay 前验证。需要时再读。


> 📦 §运维令 2026-10-26 19:2x（预训练正式落地并开跑）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31」节；**结论**：全10步已完成，S1运行中(iter30660/700k,loss2.151,~598K tok/s)，TB6006常驻，RoPE PASS，Decay阻塞待data线。需要时再读。

> 📦 §运维令 15:3x（预训练构想报告 + ETA）**已完成**（#794：`report_pretrain_baize2b_pretrain_plan_zh.html` 22.5KB；§五执行口径已补）→ 原文归档 run/ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 14:3x（补写 #792 双机实测进吞吐报告）**已完成**（#793：报告 14,208→20,888B）→ 原文同上归档。
> 📦 §运维令 13:2x（FP8 真实数据 16K/32K 实测）**已完成**（#792：16K=613,992 / 32K CP2=351,526）→ 原文同上归档。
> 📦 §运维令 11:1x（双机 16 卡调优 seq16K/32K）**已完成**（#791 8卡首跑 + #792 双机实测覆盖）→ 原文同上归档。
> 📦 §运维令 09:1x（优化 16K/32K 吞吐至 600K+）**已完成**（#791 8卡 + #792 双机 16K=613,992 ≥600K）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 08:2x（写最近工作报告 · 中文 HTML）**已完成**（#790，report_pretrain_recent_work_zh.html 20KB）→ 原文同上归档。
> 📦 §运维令 2026-10-25 23:0x（通宵攻坚：tokens/microbatch 悬崖）**已完成**（#784–#789：真因=CUDA Graph 顶格停滞·关 graph 修复·16K 双机 613,992 达标；根因报告 + seqlen rev3）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 2026-10-25 20:2x（seq 掉速排查初版）已并入 23:0x 通宵令 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-25 17:5x（seq×tok/step 16卡网格）已完成（cfg1-4 OK）→ ARCHIVE_OPERATOR_PRETRAIN.md；注意「seq≥8192 崩 5x」已被 cfg0a 证伪。需要时再读。
> 📦 §运维令 2026-10-25 07:4x（双机 16 卡吞吐报告）已完成（#770-#776）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-24 23:5x（双机调通→吞吐优化）已完成（606,300 tok/s）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维指令 2026-10-24 16:0x（305K 最佳实践+longctx 报告）已完成 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

> 📦 §2026-10-16:4x（#548 误判更正）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#548 误判根因=NFS 旧日志，判活规则已修正。需要时再读。

> 📦 §2026-10-16:2x（P0 resume + 长期授权）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 resume 闭环，长期授权训练挂了自行重启。需要时再读。


> 📦 §2026-10-17 两块（P0 中继抢修 / `_orig_mod` 崩溃修复）均已闭合 → 原文已在 `daily-memories/2026-10-17.md`；结论：中继 PID2706247 健康（RUN_ID118-122 exit=0）；`_orig_mod` 修复验证通过，断点续跑至 6890/19980 无崩。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）
> 📦 已归档（R3配比 / LaTeX / R2收官 / T3）→ `ARCHIVE_OPERATOR_PRETRAIN.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）原文搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `pretrain 归档: …` 前缀。
> 本轮动作：本任务书现 ≈40KB（已过 40KB 红线）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_PRETRAIN.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_PRETRAIN.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_PRETRAIN_2B.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B.md \
              doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/daily-memories
   git commit -m "pretrain #<轮次>: <一句话>"   # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

> 📦 §2026-10-05（3项：sglang上界+对比+环境）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：sglang vllm env 可用(0.5.9), proxy=172.19.92.25:13128, P-9.11 prefill 2.18×, 128K failed。需要时再读。
### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_PRETRAIN_2B_TASK.md` ≈ 38KB、`MEMORY_PRETRAIN_2B.md` ≈ 14KB。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` 等；
  ④ 较早的唤醒流水（保留最近 ~20 条） → `daily-memories/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变（正文/流水/快照里不得再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · 现行部分（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 Round 1（S0–S5） 均已完成并归档 →
> `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`（需要时再去读，不要把整份读进上下文）。

> 📦 §P-6 lm_eval 8集+scaling law（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；结论：P-6① Avg=0.4395@655M, P-6② 48/48 runs Avg 33.26%→49.22% R²=0.986, 55%→~55B tok. 需要时再读。
> 📦 §P-7 训练吞吐核查（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；结论： dense +8% (not +24%), hybrid 85.6K vs dense 89.7K. 需要时再读。

> 📦 §P-8 细节 + R2.3 交付物（P-8 已完成：10590步/44.4B tok/final loss 1.357）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-8 AdamW 44.4B 训练完成，14集eval CS8=49.21%/CX=6.81%，ckpt@iter_1149 已保存。需要时再读。

> 📦 §R2.4 约束（R2 实验预算/超时裁剪/vision 让行；R2 P-1~P-8 已全部完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md。**仍有效条款**：绝不杀他人进程 / 收尾不杀 loop（见 git 同步规则）。需要时再读。

---



> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（必读，2026-10-01 新增，每次唤醒都要走）

### 前提：这是一个共享工作副本

vision 任务的 agent 与本任务共用同一份工作副本——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

因此：
- 只需一个人 pull，另一个立刻看到：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  不要重复 pull，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里陌生的未提交改动很可能是 vision 任务的在途文件。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，会互相把对方在途的文件一起提交。
  这是既有设计的已知副作用，不要试图"修正"它。

### 但 loop 本身只 push 不 pull

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
所以 pull 必须由你（agent）来做。

每次唤醒按顺序执行：

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. 提交时显式指定你自己的文件：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 不要用 `git add -A`——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 behind / diverged：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是双方的在途改动：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → 另一个 agent 正在做 git 操作：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并跳过本次 git 操作，下次唤醒再试。
   - 🚫 绝不 `git push --force`；🚫 绝不 `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——沿用同一做法。

---


---

