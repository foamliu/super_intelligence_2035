# ZhuLong 论文审阅进度（参考文献 + 逻辑链 + 数字↔措辞一致性）

> 任务令：2026-10-29 21:5x（用户直令）。对象 = `doc/ZhuLong_DAC2027/ZhuLong_DAC2027/` @ HEAD `c78558a0`。
> 口径：数值正确性已确认 ⇒ 只查 ①参考文献 ②论文逻辑 ③数字↔措辞一致性。

## 基线信息
- HEAD: `c78558a0a30b03c1fc851652d98297ed69c2ddb7`
- bib 条目总数（reference.bib 实体）: 28（vaswani / openai-gpt4 / qwen3 / verigen / rtlcoder / dawning / autoeda / blocklove / agentforge / cline / mcp / seed / bge / faiss / pyaether / layoutcopilot / rag / chatcl / humaneval / iscript / pdagent / kaelbling / delage / thrun / austin / chateda / mcp4eda / liu-agentic）
- software.bib：**未被 `\bibliography` 引用**（main.tex 仅 `\bibliography{reference}`）→ 模板遗留，不审。
- 正文 `\cite` 唯一 key 数：**19**
- 孤儿条目（bib 有、正文未引用）：**10**（vaswani2017attention, openai2023gpt4, yang2025qwen3, thakur2023verigen, liu2023rtlcoder, chen2024dawning, blocklove2024eda, kumar2026agentforge, mcp2024protocol, jiang2024seed）
- main.bbl 条目数：19（= 引用的 19 个）
- 页数（mutool info）：**8**（任务书目标 7 = 正文 6 + refs 1 → ⚠️ 超目标 1 页，需在报告记录）
- pdftotext / pdfinfo：本机不可用 → 已用 mutool 实测 8 页
- main.log：0 undefined ref/citation；Overfull 1（1.3pt，可忽略）；Underfull 4（排版自然现象，`\raggedbottom`+短页）

## 计数（已完成）
| 项 | 已核 / 总数 |
|:--|:--|
| bib 条目元数据外部核验 | 28 / 28 ✅ |
| 正文 `\cite` 上下文判定 | 21 / 21 ✅ |
| claim 进映射表 | 8 / 8 ✅ |
| 数字↔措辞逐句 | 20+ / 全 ✅ |
| 逻辑断点清单 | 6 ✅ |

## 逐项进度
- [x] 通读全文 ✅
- [x] 建 claim→证据→结论 映射表（8 claim）
- [x] bib 逐条元数据核验（arXiv/doi.org/EconPapers/scixplorer/GitHub）
- [x] 每个 `\cite` 上下文判定 ✅/⚠️/❌
- [x] 数字↔措辞一致性表
- [x] 结构与元数据（main.tex / 页数 mutool=8）
- [x] 写 HTML 报告（46KB, 0 script, 0 外链）✅

## 关键发现摘要
- **P0×3**：① he2024chateda bib 伪造（eprint 2401.00754→天体物理，作者全错；真实=2308.10204）② wang2025mcp4eda bib 伪造（eprint 2502.18436→宇宙学，标题/作者全错；真实=2507.19570）③ main.pdf 与源码失配（stale 构建产物，PDF=81.4%/129/291-subset vs 源码=82.5%/130/449）
- **P1×6**：页数 8>7；delage DOI 错（指向 Song et al.）；pu2024rag venue 可疑（ICCAD 2024 vs TCAD 2025 44:4615）；核心逻辑断点（57.2pp 系统轴混杂 ε+执行器+检索 vs 23.7pp backbone；受控回读轴 7.1pp<23.7pp 结论会反转）；cost 口径 449 vs 291 可疑；10 个孤儿 bib
- **P2×12**：li2026pdagent 标题漏 /VLM；lee2025autoeda 作者不全；3 处 cite 上下文 ⚠️；孤儿 blocklove/chen2024dawning/jiang2024seed 标题小误；82.5%(130/158) 均值vs计数；12/9 分类+86.7%内省率自注待复核；software.bib 模板遗留；中文注释残留等
- ✅ 实验数字内部高度自洽（Wilson CI、组件差值、跨切片归因全可对齐）；57.2/23.7/7.1/76.9/19.7/68.6 全文一致；部署兜底句已按评审处理

## 交付物
- 报告：`doc/BaiZe-ISEDA2027/reports/report_zhulong_paper_detail_audit_zh.html`（复审 46KB → +§⑧ 跟踪后 55KB → wake#373 65KB → wake#374 69KB → wake#375 73KB → wake#377 77KB）
- 进度：本文件
- MEMORY：`MEMORY_ZHULONG.md` 顶部已写结论

## 操作流水
- [2026-10-30] 启动审阅：读全文 + 列 bib/cite 清单 + 页数实测（mutool=8 页）。
- [2026-10-30] bib 28 条 + cite 21 处外部核验完成；发现 2 条 P0 伪造条目 + 1 DOI 错 + 1 venue 可疑。
- [2026-10-30] 发现 main.pdf stale（PDF=81.4%/129/291 vs 源码=82.5%/130/449），P0-3。
- [2026-10-30] 建 claim 映射表(8) + 逻辑断点(6) + 数字↔措辞表(20+)；核心断点 LB1：57.2pp 系统轴混杂 ε vs backbone 23.7pp，受控回读轴仅 7.1pp<23.7pp。
- [2026-10-30] 写完 HTML 报告 46KB（0 script / 0 外链 / 标签配平）。
- [2026-10-30] 更新 MEMORY 顶部 + commit+push。
- [2026-10-30 wake#370] **审计后修订跟踪**：发现审成后平行改稿线提交 `91de519e2`（10:40）+ `cf7cfabc`（11:08），HEAD 由 `c78558a0` → `cf7cfabc`，论文树变更（reference.bib -101 行 / 1_intro.tex / main.tex / 6_exp.tex / main.pdf 重建）。逐项核验：P0①②（he2024chateda→2308.10204、wang2025mcp4eda→2507.19570）经 arXiv 主源 cimi_fetch 逐字核验为真 ✅；P0③ main.pdf 已重建 ✅；P1 10 孤儿 bib 全删 ✅；P1 57.2pp 逻辑断点 intro 措辞降级（"sets the ceiling"→"exceeds the backbone range"）⚠️部分解决；P2 6_exp 表注 dangling 指针已删 ✅。报告新增 §⑧ Post-Audit Revision Tracker（55470B / 0 script / 0 外链 / div 9·table 11 配平）。**原 3 P0 全部已被正确解决**；§①–⑦ 结论仍针对 c78558a0 基线，不自动等同当前 HEAD；完整重审需另下令。未改 .tex/.bib/figures（只审不改红线遵守）。
- [2026-10-30 wake#371] **§⑧ 跟踪再扩展**：HEAD 由 `cf7cfabc` 进一步推进至 `c931cef6`，新增 commit `83d4c49f6`（11:33，"condense redundant prose + conclusion/future work to 7 pages"）。`git show` 全文 diff 核验：6 个 .tex 文件 +14/−14 行纯 prose 压缩，**所有数字未变**（57.2/7.1/8.3/10.7/2.4pp/76.9%/Wilson CI/449/158/2245 全保留），main.pdf 重建。`mutool info main.pdf` 实测页数 = **7**（原审计 P1「页数 8>7」→ ✅ 已解决）。报告 §⑧ 新增第⑧行（页数解决）+ §⑧.1 P1 计数 4→3（余 delage DOI / pu2024rag venue / cost 口径）；§⑧ intro 与顶部 banner 更新 HEAD=c931cef6 + 三 commit 列表。**因 83d4c49f6 零数字变更，§①–⑦ 数字↔措辞与参考文献结论仍然有效**。报告 55470→57390B / 0 script / 0 外链 / div 9·table 11·tr 110 配平。未改 .tex/.bib/figures。完整重审仍需另下令。
- [2026-10-30 wake#373] **§⑧ 跟踪再扩展（HEAD c931cef6 → cb1c0adf2）**：发现 2 个新 commit：`d26874eb6`（13:30 "enable sigconf (de-anonymize), add Hongwen Li & Yiming Zhu, mark ... corresponding authors"）+ `cb1c0adf2`（13:40 "correct Hongwen Li email to howie.li@cxmt.com"）。`git diff c931cef6..cb1c0adf2` 核验：**仅 main.tex 作者块**（+13/−4 行：`[anonymous, sigconf]`→`[sigconf]`、新增 2 作者、3 通讯作者、邮箱更正）+ main.pdf 重建，**未触任何 .bib / 章节 .tex / 数字** → §①参考文献 / §②逻辑 / §③数字↔措辞 结论**仍然有效**。但发现 2 项审计相关问题：**(1) 🚨 新增 P0——去匿名化违反 DAC 2027 双盲审稿规则**：DAC 2027 CFP（cimi_search 2026-10-30 抓取 `dac.com/2027/program/research-manuscript-submissions`，WikiCFP/CallForPaper.org 同源引用 authority 3–4）明确 "Review is double-blind" + "maximum 6 pages + 1 additional references-only page"；DAC 2025 archive 亦载 "DAC manuscripts undergo a double-blind review process"。投稿稿（Stage 2 manuscript）必须匿名，当前 `sigconf`（非 anonymous）暴露真实作者/单位/邮箱 → 双盲违规，存在 desk-reject 风险。属"易修 P0"（恢复 `[anonymous, sigconf]` 即可），`sigconf`+通讯作者仅用于录用后 camera-ready。**(2) ⚠️ P1 页数再开（7→8）**：去匿名化加作者块致 main.pdf 由 7 回退至 8，`mutool info main.pdf` @ HEAD cb1c0adf2 实测 = 8 页，超 DAC 上限 7。报告 §⑧ 新增 P0 alert box + 第⑨/⑩行 + ⑧行状态改为"已解决后又再开"；§⑧.1 计数 P0 0→1、P1 3→4；§⑥ 未核实清单标注 DAC 规则✅已 web 核验 + 页数✅已实测。报告 57390→64675B / 0 script / 0 外链 / div 10·table 11·tr 112·h2 8 全配平 ✅。未改 .tex/.bib/figures（红线遵守）。**§①–⑦ 仍针对 c78558a0 基线**；完整重审需另下令。
- [2026-10-30 wake#374] **§⑧ 跟踪再扩展（HEAD cb1c0adf2 → fa8bbaa9）**：发现 1 个新 paper-tree commit `1db970598`（14:00 "zhulong auto-commit 2026-10-30 14:00:59"）。`git diff cb1c0adf2..fa8bbaa9 -- doc/ZhuLong_DAC2027/ZhuLong_DAC2027/` 核验：**仅 main.tex** 改动（+55 行），内容 = 在 `\microtypesetup{expansion=false}` 后、`\begin{document}` 前新增 `\makeatletter\def\@mkauthors@iii{...}\makeatother` 块，把 18 位作者从"竖排一列"改为"每行 3 人 × 6 行"并排网格，邮箱/单位汇总到网格下方；main.pdf 重建（743624→743567 B）。**未触任何 .bib / DAC2027/*.tex / figures / 任何数字** → §①参考文献 / §②逻辑 / §③数字↔措辞 结论**仍然有效**。`documentclass` 仍 `[sigconf]`（非 anonymous）→ P0⑨ 去匿名化双盲违规**维持**。`mutool info main.pdf` @ HEAD `fa8bbaa9` 实测仍 **8 页** → P1⑧ 页数超标**维持**（网格排版压缩了作者块纵向占用，但未使总页数回落至 7）。**新增 1 个 P2（⑪）**：以 `\makeatletter` 覆盖 acmart 内部宏 `\@mkauthors@iii` 属非标准定制，相机就绪阶段 acmart-validation 校验可能告警（作者块视觉/元数据抓取与 ACM 期望不符）——属"相机就妥阶段处理"次要合规风险，非投稿阻断。报告 §⑧ 新增第⑪行 + §⑧.1 加列"跟踪至 fa8bbaa9（wake#374）"（P0=1 不变 / P1=4 不变 / P2=11→12）+ banner/title/§⑥ 页数行/跟踪结论段更新 HEAD=fa8bbaa9。报告 64675→69288B / 0 script / 0 外链 / div 10·table 11·tr 113·h2 8 全配平 ✅。未改 .tex/.bib/figures（红线遵守）。**§①–⑦ 仍针对 c78558a0 基线**；完整重审需另下令。
- [2026-10-30 wake#375] **§⑧ 跟踪再扩展（HEAD fa8bbaa9 → ad448d3e4）**：发现 2 个新 paper-tree commit：`329f7b344`（14:40 "author block: 6-per-row grid; chairman Yiming Zhu last"）+ 自动提交 `ad448d3e4`（14:44 "zhulong auto-commit 2026-10-30 14:44:45"）。`git diff fa8bbaa9..ad448d3e4 -- doc/ZhuLong_DAC2027/ZhuLong_DAC2027/` 核验：**仅 main.tex**（+18/−15 行，含 main.aux/main.log 自动构建产物）改动，内容 = ① `\divide\author@bx@wd by 3`→`by 6`（3×6 网格改 6×3 网格、共 3 行）；② 新增 `\def\@authorfont{\Large}`（6 人/行较密，作者名字号 \LARGE→\Large 避免长名换行）；③ 通讯作者顺序由 Yiming Zhu/Hongwen Li/Yanfeng Li 改为 Yanfeng Li/Hongwen Li/Yiming Zhu（Yiming Zhu 末位作 chairman）。main.pdf 重建（743567→732702 B）。**未触任何 .bib / DAC2027/*.tex / figures / 任何数字** → §①参考文献 / §②逻辑 / §③数字↔措辞 结论**仍然有效**。`documentclass` 仍 `[sigconf]`（非 anonymous）→ P0⑨ 去匿名化双盲违规**维持**。`mutool info main.pdf` @ HEAD `ad448d3e4` 实测仍 **8 页** → P1⑧ 页数超标**维持**（6×3 比 3×6 更紧凑，但总页数未回落至 7）。**P2⑪ 维持且略加重**：本次在已有 `\@mkauthors@iii` 覆盖基础上又新增 `\@authorfont` 字体覆盖，属同类非标准 acmart 宏定制——**归并 ⑪ 计数、不新增独立 P2**，相机就绪 acmart-validation 校验风险同前。报告 §⑧ 新增第⑫行 + §⑧.1 加列"跟踪至 ad448d3e4（wake#375）"（P0=1 不变 / P1=4 不变 / P2=12 不变）+ banner/title/§⑥ 页数行/跟踪结论段更新 HEAD=ad448d3e4。报告 69288→72931B / 0 script / 0 外链 / div 10·table 11·tr 114·h2 8 全配平 ✅。未改 .tex/.bib/figures（红线遵守）。**§①–⑦ 仍针对 c78558a0 基线**；完整重审需另下令。
- [2026-10-30 wake#377] **§⑧ 跟踪再扩展（HEAD ad448d3e4 → 7910a924f）**：发现 2 个新 paper-tree commit：`8edcaf613`（16:43 "paper: future work (ii) -> long-term memory + recursive self-improvement (RSI)"）+ `7910a924f`（16:55 "paper: rebuild main.pdf to match future-work (ii) long-term memory + RSI"）。`git show 8edcaf613 -- DAC2027/8_conclusion.tex` 核验：**仅 conclusion future work item (ii) 措辞**改动（+2/−2 行："long-term memory of verified API constraints"→"long-term memory and recursive self-improvement (RSI)"，同步中文注释），**关键数字 76.9% pooled Pass@1 全句保留、未引入新 `\cite`、未改任一数字**（57.2/7.1/23.7/19.7/68.6/Wilson CI/449/158 全保留）。`git diff ad448d3e4..7910a924f -- reference.bib software.bib` 输出为空 → **未触任何 .bib**。main.pdf 重建（732702→732704 B）。→ §①参考文献 / §③数字↔措辞 结论**仍然有效**；§②逻辑：RSI 作为 future work 提出未承诺已验证主张，**不构成新逻辑断点**。`documentclass` 仍 `[sigconf]`（非 anonymous）→ P0⑨ 去匿名化双盲违规**维持**。`mutool info main.pdf` @ HEAD `7910a924f` 实测仍 **8 页** → P1⑧ 页数超标**维持**。本次未触 acmart 宏 → P2⑪ 维持原状、**不新增独立 P2**。报告 §⑧ 新增第⑬行 + §⑧.1 加列"跟踪至 7910a924f（wake#377）"（P0=1 不变 / P1=4 不变 / P2=12 不变）+ banner/title/§⑥ 页数行/跟踪结论段更新 HEAD=7910a924f。报告 72931→77261B / 0 script / 0 外链 / div 10·table 11·tr 115·h2 8 全配平 ✅。未改 .tex/.bib/figures（红线遵守）。**§①–⑦ 仍针对 c78558a0 基线**；完整重审需另下令。
