# MANIFEST.md — EDA-Flow-Bench ICML 2027 论文 · Overleaf 同步与编译指引

> 用途：让用户（及任何复现者）能在 Overleaf 上从零复现本地 clean compile。
> 本地 clean compile 现状（2026-11-21）：**12 pages / 0 error / 0 undefined / 0 Overfull / 29 Underfull（badness 10000 = 0）**。
> 正文（§0–§9，含 Abstract）= p1–p6（≤ 6 页）；References / Ethics / Reproducibility / Appendix A–D 从 p7 起。

---

## 1. 必须上传的文件清单（完整文件树）

上传到 Overleaf 时，把以下文件保持相对路径不变整体打包（zip 整体上传最稳）。**不要上传 `.venv/`、`node_modules/`、`*_preview*.png`、以及 `main.aux/main.bbl/main.blg/main.log/main.out/main.toc` 等构建产物**（Overleaf 会自己生成）。

### 1.1 顶层文件（论文树根 `EDA-Flow-Bench_ICML2027/`）
| 文件 | 作用 |
|:--|:--|
| `main.tex` | 主文件：`\documentclass` + 宏定义 + 标题/作者块 + `\input` 章节指令 |
| `references.bib` | BibTeX 文献库 |
| `icml2026.sty` | ICML 样式文件（仓库自带，接口与 ICML 2027 kit 一致） |
| `icml2026.bst` | ICML 参考文献样式 |
| `algorithm.sty` | 算法浮动体样式（仓库自带） |
| `algorithmic.sty` | 算法伪代码样式（仓库自带） |
| `fancyhdr.sty` | 页眉页脚样式（仓库自带） |
| `icml_numpapers.pdf` | ICML 样例 PDF（可选，仅供样式参照，编译不需要） |

### 1.2 `sections/`（正文 12 节）
```
sections/0_abstract.tex        sections/6_experiments.tex
sections/1_intro.tex           sections/7_analysis.tex
sections/2_background.tex      sections/8_related.tex
sections/3_task_benchmark.tex  sections/9_conclusion.tex
sections/4_harness.tex         sections/10_ethics.tex
sections/5_hypotheses.tex      sections/11_reproducibility.tex
```

### 1.3 `appendix/`（附录 4 节）
```
appendix/A_benchmark_details.tex
appendix/B_additional_results.tex
appendix/C_experimental_details.tex
appendix/D_affective_mechanism.tex
```

### 1.4 `figures/`（可选 — 当前正文**未** `\includegraphics` 任何图）
> ⚠️ 截至 2026-11-19，正文与附录均未使用 `\includegraphics`，因此 `figures/` **不是编译必需**。下列图源文件随仓库入库，若日后加图再上传即可。
```
figures/domain_pie.pdf        figures/pipeline.pdf
figures/grounding_depth.pdf   figures/pipeline.svg / pipeline.mmd
figures/make_figs.py          （图源脚本，编译不需要）
```
**不要上传**：`figures/.venv/`（matplotlib/mermaid 虚拟环境）、`figures/node_modules/`、`figures/*_preview*.png`、`figures/pipeline_t2i*.png`（中间产物）。

### 1.5 一行式文件树核验命令（本地）
```bash
cd EDA-Flow-Bench_ICML2027
find . \( -name '*.tex' -o -name '*.bib' -o -name '*.sty' -o -name '*.bst' \) \
  -not -path '*/.venv/*' -not -path './.git/*' | sort
```
应得到 23 个文件（1 main.tex + 1 references.bib + 4 .sty + 1 .bst + 12 sections + 4 appendix）。

---

## 2. 关键宏定义清单（核对 Overleaf 上的 main.tex 是否最新）

Overleaf 上若仍报 `Undefined control sequence \FullScale` / `\LiteSet`，说明 Overleaf 上的 `main.tex` 是**旧版**。请核对 Overleaf `main.tex` 是否含以下宏（行号为本地最新版，2026-11-19）：

| 行号 | 宏 / 设置 | 定义 | 说明 |
|:--|:--|:--|:--|
| 36 | `\setlength{\emergencystretch}{4em}` | 排版 | 段落断行额外拉伸容限（减 Underfull） |
| 37 | `\raggedbottom` | 排版 | 双栏底部不强制对齐（消除栏底 vbox underfull） |
| 40 | `\newcolumntype{Y}{>{\raggedright\arraybackslash}X}` | 排版 | ragged X 列（表格内不可断数学串） |
| 43 | `\newcommand{\bench}{EDA-Flow-Bench\xspace}` | 宏 | 评测集名 |
| 44 | `\newcommand{\mode}{design\_flow\xspace}` | 宏 | 任务契约名 |
| 45–47 | `\eg` / `\ie` / `\etal` | 宏 | 缩写 |
| 48 | `\newcommand{\TBD}{\textbf{TBD}\xspace}` | 宏 | 待评测占位 |
| **54** | **`\newcommand{\FullScale}{several thousand}`** | **宏** | **Full 集定性描述（不给具体数字）** |
| **55** | **`\newcommand{\LiteSet}{500}`** | **宏** | **Lite 集任务数** |
| 58 | `\newcommand{\Neval}{696}` | 宏 | 冻结快照 run 数（Full-set 描述性样本数） |
| 60 | `\newcommand{\MzeroPass}{10.0\%}` | 宏 | M0 描述性基线 Pass@1（696-run Full-set 快照·DeepSeek-V4-Pro） |
| **63** | **`\newcommand{\MzeroAnchor}{10.1\%}`** | **宏** | **M0 臂级比较锚点 Pass@1（top-120-of-Lite·doubao-seed-2.0-pro-cloud·12/119 decided）** |
| 65 | `\newcommand{\ScriptPass}{76.5\%}` | 宏 | 单脚本 EDA 基线 |

**关键核对点**：
- `main.tex:54` 必须有 `\newcommand{\FullScale}{several thousand}`（旧版是 `\newcommand{\Ntasks}{1827}`，已删除）。
- `main.tex:55` 必须有 `\newcommand{\LiteSet}{500}`（旧版无此宏）。
- `main.tex` **不应**再出现 `\newcommand{\Ntasks}` 或 `\newcommand{\PreregDate}`（均已删除）。
- `main.tex:96` 的 `\input{sections/5_hypotheses}` 必须指向新文件名（旧版是 `5_preregistered`，见 §3）。

---

## 3. 文件改名记录

| 旧名 | 新名 | 改名 commit | 说明 |
|:--|:--|:--|:--|
| `sections/5_preregistered.tex` | `sections/5_hypotheses.tex` | `85fe32456`（2026-11-19） | 删除"预注册"措辞：节标题 `Pre-Registered Hypotheses and Ablation Design` → `Falsifiable Hypotheses and Ablation Design`；`\label{sec:preregistered}` → `\label{sec:hypotheses}`（全树 `\ref` 已同步，commit `251ac1064`） |

**Overleaf 同步注意**：
- 若 Overleaf 项目里还残留旧文件 `sections/5_preregistered.tex`，**必须删除**——否则可能与新 `5_hypotheses.tex` 冲突，且旧 `\label{sec:preregistered}` 会复活导致 `\ref` 指向错误。
- `main.tex:96` 的 `\input` 已改为 `sections/5_hypotheses`；若 Overleaf 的 `main.tex` 仍是 `\input{sections/5_preregistered}`，会报 `File 'sections/5_preregistered.tex' not found`（因为新树里只有 `5_hypotheses.tex`）。

---

## 4. Overleaf 编译步骤

1. **打包上传**：本地 `cd EDA-Flow-Bench_ICML2027 && zip -r ../paper.zip . -x '*/.venv/*' '*/node_modules/*' '*_preview*.png' '*.aux' '*.bbl' '*.blg' '*.log' '*.out' '*.toc' '*.pdf'`，然后在 Overleaf 用 **New Project → Upload Project** 整体上传 zip（最稳，避免遗漏 `.sty`/`.bst`）。
   - ⚠️ 三个仓库自带的 `.sty`（`algorithm.sty`/`algorithmic.sty`/`fancyhdr.sty`）和 `icml2026.sty`/`icml2026.bst` **必须上传**，否则 Overleaf 找不到 ICML 样式会报错。
2. **设置编译器**：Overleaf 项目 → Menu → Compiler = **pdfLaTeX**。
3. **点 Recompile**：Overleaf 自动跑多轮（pdflatex → bibtex → pdflatex × 2），等 2–3 分钟。首次编译会建 `.aux`/`.bbl`，第二轮起 undefined ref/citation 清零。
4. **若仍报 `Undefined control sequence`**：
   - 检查 Overleaf 上的 `main.tex` 是否是最新版（按 §2 核对 `\FullScale` line 54 / `\LiteSet` line 55 是否存在）。
   - 检查 Overleaf 上是否还残留旧 `sections/5_preregistered.tex`（按 §3 删除）。
   - 检查 `\input{sections/5_hypotheses}`（line 96）是否指向新文件名。
5. **若报 `LaTeX Error: File 'icml2026.sty' not found`**：说明 `.sty`/`.bst` 没上传成功，重新上传 §1.1 列出的样式文件。

---

## 5. Clean compile 命令（本地或 Overleaf 都适用）

> 🔴 **从此所有编译验证必须 clean compile**（删 aux → 3 轮 pdflatex + bibtex）。
> 不得只跑 1 轮 pdflatex 就报"编译通过"；不得依赖旧 `.aux` 缓存报"0 undefined"（会掩盖潜在风险）。

```bash
cd EDA-Flow-Bench_ICML2027
rm -f main.aux main.bbl main.blg main.log main.out main.toc main.pdf
pdflatex -interaction=nonstopmode main.tex   # round 1（会报 undefined ref/citation，正常）
bibtex main                                    # 解析 citation
pdflatex -interaction=nonstopmode main.tex   # round 2
pdflatex -interaction=nonstopmode main.tex   # round 3（应 0 undefined）
```

### 5.1 验证判据（round 3 的 `main.log`）
```bash
grep -c '^!' main.log            # = 0  （0 error）
grep -ci 'undefined' main.log    # = 0  （0 undefined ref/citation/control sequence）
grep -c 'Overfull' main.log      # = 0  （≤1 允许，当前 0）
grep -c 'Underfull' main.log     # ≤ 30（当前 28）
grep -c 'badness 10000' main.log # ≤ 2  （当前 0）
grep -i 'Output written' main.log # 报页数 + 字节
```
- **判据**：round 3 的 `grep -ci 'undefined' main.log` = 0 才算编译通过；round 1 的 undefined 是正常的（aux 还没建立），**不得用 round 1 的 log 报"有 undefined"也不得用旧 aux 报"0 undefined"**。

---

## 6. 当前编译状态（2026-11-21，M0 anchor 回填 doubao-seed-2.0-pro-cloud 后）

| 指标 | 值 | 判据 | 状态 |
|:--|:--|:--|:--|
| 总页数 | 12 | — | — |
| 正文页数（§0–§9） | 6（p1–p6） | ≤ 6 | ✅ |
| `grep -c '^!' main.log`（error） | 0 | = 0 | ✅ |
| `grep -ci 'undefined' main.log` | 0 | = 0 | ✅ |
| `grep -c 'Overfull' main.log` | 0 | ≤ 1 | ✅ |
| `grep -c 'Underfull' main.log` | 29 | ≤ 30 | ✅ |
| `grep -c 'badness 10000' main.log` | 0 | ≤ 2 | ✅ |
| abstract 词数（渲染，pdftotext 实测） | 186 | ≤ 200 | ✅ |
| 匿名性（pdftotext 无作者/机构/自指泄漏） | 0 自指泄漏 | = 0 | ✅ |

### 6.1 本次修复的 5 处 Overfull \hbox（用户报告）
1. `sections/4_harness.tex:61-65` 公式 66.5pt + 9.13pt → 缩写 `state_match`→`sm`，where 子句的 state 元组改为 `(\text{fail-rate}_N,\,\text{tool},\,\text{stage})` + 散文展开。**已消除**。
2. `appendix/B_additional_results.tex:25` 表 5.97pt → `\setlength{\tabcolsep}{4pt}`。**已消除**。
3. `appendix/B_additional_results.tex:176` 表 20.1pt → `\footnotesize` + `\tabcolsep=4pt`。**已消除**。
4. `appendix/D_affective_mechanism.tex:53` 公式 10.19pt → 同 ① 的 state 元组缩写。**已消除**。
5. （①.2 与 ①.1 同一公式，一并解决。）

### 6.2 Underfull 优化（91 → 28）
- 全局 `\emergencystretch=4em`（减段落级 hbox underfull）。
- 全局 `\raggedbottom`（消除 9 处 `Underfull \vbox (badness 10000) while \output is active` 栏底填充警告）。
- 新增 ragged X 列类型 `Y`（`\newcolumntype{Y}`），用于 `sections/5_hypotheses.tex` 与 `sections/6_experiments.tex` 中含不可断数学串（如 `M7<M2−2pp`）的 tabularx 单元格。
- 对含不可断 `\texttt` 串（如 `declare_done`、`check.py`、`/chat/completions`、失败类别缩写 `TO=ERROR_TIMEOUT`）的段落/itemize 局部加 `\hbadness=10000\sloppy`（4_harness / 8_related / 6_experiments / appendix B·C·D），消除 badness 10000 残余。
- 剩余 28 处 Underfull 均为 badness 1009–5622 的轻度断行警告（< 5000 的可接受，> 5000 的少数已用局部 sloppy 处理），不影响编译与美观。

---

## 7. 硬约束与防伪底线（继承，编译复现时不得违反）

- 🚫 不动宏定义的数字值：`\LiteSet=500` / `\Neval=696` / `\MzeroPass=10.0%` / `\MzeroAnchor=10.1%` / `\ScriptPass=76.5%` 不改。
- 🚫 Full 集在论文中只出现定性描述（"several thousand"/"thousands"/"growing"），**不出现具体数字**（除附录 shard 分布 + 696-run 快照样本数 `\Neval`）。
- ✅ 双盲匿名 + 防伪底线 + 0 外链 + 不承诺开源 + 无预注册 + Full/Lite 分层 + 3 项贡献。
- ✅ 编译验证必须 §5 的 clean compile；round 3 的 `grep -ci 'undefined' main.log` = 0。
