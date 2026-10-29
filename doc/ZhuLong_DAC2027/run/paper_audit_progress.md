# paper_audit_progress.md — ZhuLong DAC2027 论文逐处核对进度

> 任务：运维令 2026-10-29 **21:5x（覆盖 21:3x）** — 论文逐处细节核对
> **口径**（用户原话）：「数字是没错的，主要核对参考文献，和论文逻辑。以及数字和措辞是否一致。」
> ⇒ **数字正确性已由用户确认**，不回溯 batch/regrade log 验数；只在**同一数字在文内自相矛盾**时才查 batch 一次。
> 审阅范围仅限：① 参考文献（逐条元数据 + 逐 `\cite` 上下文） ② 论文逻辑链 ③ 数字↔措辞一致性。
> 对象：`doc/ZhuLong_DAC2027/ZhuLong_DAC2027/`（main.tex + DAC2027/0~9 + reference.bib + software.bib + figures）·**只审不改**
> 审阅基线 commit：`0188e978b`（Merge），HEAD `40fbf3687`，关键改动 commit `59094e282`「陈熙元修改论文」(+58/−64, 9 tex)
> 报告路径：`doc/BaiZe-ISEDA2027/reports/report_zhulong_paper_detail_audit_zh.html`（~37KB · 0 `<script>` · 0 外链 · 标签平衡 · title 注明 main.tex@40fbf3687）

## 覆盖率计数（终态）

| 项 | 已覆盖 / 总数 | 状态 |
|:--|:-:|:--|
| main.tex 通读 | 1/1 | ✅ |
| 正文 tex 通读（0~9） | 10/10 | ✅（9_appendix 已删、无 \input） |
| reference.bib 条目外部核验 | 29/29 | ✅（19 cited + 10 uncited）·bib 100% 外部验 |
| software.bib 条目 | 10/10 | ✅（全部 unused 左余样例） |
| `\cite` 上下文逐条判定 | 22/22 | ✅（19 key 全有 bibitem + 3 重复 cite 上下文） |
| 论文逻辑链 claim 映射 | 9/9 | ✅（claim→loc→evidence→强度→verdict→建议） |
| 数字↔措辞 多处比对 | 16/16 | ✅（按句判措辞强度） |
| 59094e282 改动 diff 复核 | 9/9 tex | ✅ |
| LaTeX 编译/告警检查 | 已核 | ✅ 0 undefined ref/cite · 19/19 cite key 有 bibitem · 1 overfull(1.3pt) · 匿名·sigconf 双盲合规 · CCS 3条 + keywords 在位 |
| web 外部核验条数 | ≥52 | ✅（arXiv 18 + Crossref/DOI 4 + search 12 + GitHub/site 3 + DAC rules + software.bib 样例 + MCP 等）·**≥ bib 29 + 20** |
| 检查项总数 | ≥160 | ✅ |

## 问题计数（终态）

- **P0（阻断）**：0（21:5x 口径下数字已由用户确认，原 21:3x「数字不可溯源」P0 已撤销）
- **P1（严重）**：6
  - **P1-1** `he2024chateda`：arXiv:2401.00754 实为天体物理论文；真实 ChatEDA = arXiv:2308.10204，作者全错（bib ❌ + cite 上下文错配）
  - **P1-2** `wang2025mcp4eda`：arXiv:2502.18436 实为宇宙学论文；真实 MCP4EDA = arXiv:2507.19570（bib ❌）
  - **P1-3** `delage2010percentile`：DOI 10.1287/opre.1090.0711 实为 Song 库存论文；Delage&Mannor 标题/作者/卷/页均正确，仅 DOI 错（bib 元数据 ❌ / cite 上下文 ✅ 支持百分位 regret 论断）
  - **P1-4** §S3/abstract 概念漂移：57.2pp 标为"observation-fidelity axis"，实为系统级（Ω+effector）轴；纯 Ω 才是受控 7.1pp 阶梯——核心论点措辞与定义不一致
  - **P1-5** `6_exp §error-analysis` L109「82.5% (130/158)」：130/158=82.3%≠82.5%；82.5%×158=130.35（非整数）——**句内自相矛盾**（按 21:5x 唯一允许查 batch 的一次，zhulong_results.md 亦无 82.5/130/158 三联）
  - **P1-6** 提交版页数未实测：committed `main.pdf`=8 页但 stale（mtime 10:45 < commit 21:17）；临时编译因字体环境差异得 12 页不稳定；目标 body 6 + refs 1 = 7 页未实测确认
- **P2（轻微）**：12（4 处 title 微差 / 10 uncited 死条目 / software.bib unused / empyrean 403 / cadence 手册泛化 / pu2024rag venue 待核 / 等，详见报告 §4）

## 轮次流水

- [2026-10-29 21:4x] R1：完成内部证据收集（git show 59094e282、zhulong_results.md 比对、main.log/bbl 告警、label/ref 配对、temp 编译测页数）+ bib 外部 web 核验（arxiv 18 条 / crossref DOI / github / MCP / DAC rules / search）+ 写首版 HTML 报告（21:3x 口径，含 P0 数字溯源）+ 进度文件。
- [2026-10-29 21:5x] R2：**接到 21:5x 运维令（覆盖 21:3x）**，按用户原话「数字已确认·核对参考文献+逻辑+措辞」**撤销 R1 的 P0 数字溯源结论**，重写 HTML 报告为 21:5x 口径（三张必交表：ref-check / logic-chain / number↔wording + 断点清单 + 未核实清单），重写本进度文件。终态：**P0=0 / P1=6 / P2=12，bib 29/29 外部验，cite 22/22 判定，claim 9/9 映射，number↔wording 16/16 比对，web 核验 ≥52 条**。报告 ~37KB / 0 script / 0 外链 / 标签平衡 / title 注明 main.tex@40fbf3687。

## 结论

✅ 论文逐处核对完成（21:5x 口径）。**参考文献 3 处硬错（P1-1/2/3）+ 概念漂移 1 处（P1-4）+ 句内算术矛盾 1 处（P1-5）+ 页数未实测 1 处（P1-6）**，其余数字内部自洽且算术成立。所有 ❌/⚠️ 均可复现（arXiv/Crossref URL 或 file:line）。报告已交付，只审不改。
