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
- 报告：`doc/BaiZe-ISEDA2027/reports/report_zhulong_paper_detail_audit_zh.html`（46KB）
- 进度：本文件
- MEMORY：`MEMORY_ZHULONG.md` 顶部已写结论

## 操作流水
- [2026-10-30] 启动审阅：读全文 + 列 bib/cite 清单 + 页数实测（mutool=8 页）。
- [2026-10-30] bib 28 条 + cite 21 处外部核验完成；发现 2 条 P0 伪造条目 + 1 DOI 错 + 1 venue 可疑。
- [2026-10-30] 发现 main.pdf stale（PDF=81.4%/129/291 vs 源码=82.5%/130/449），P0-3。
- [2026-10-30] 建 claim 映射表(8) + 逻辑断点(6) + 数字↔措辞表(20+)；核心断点 LB1：57.2pp 系统轴混杂 ε vs backbone 23.7pp，受控回读轴仅 7.1pp<23.7pp。
- [2026-10-30] 写完 HTML 报告 46KB（0 script / 0 外链 / 标签配平）。
- [2026-10-30] 更新 MEMORY 顶部 + commit+push。
