# AUDIT — EDA-LiveFlow-Bench 数字与论断一致性审计（read-only refresh）

- 审计对象：`doc/ZhuLong_DAC2027/EDA-LiveFlow-Bench_ICML2027/`（main.tex + sections/*.tex + appendix/*.tex + figures/make_figs.py）
- 唯一真值（ground truth，2026-11-09 全量批次 `run_batch_20261109_171201`）：

```
batch: /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/run_batch_20261109_171201
jsonl: .../benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl
total: 696 cases, 8 workers
result: {'ERROR': 70, 'FAIL': 558, 'PASS': 62, 'ABSENT': 6}
pass rate: 62/626 = 9.9%   (PASS+FAIL+ABSENT)
           62/620 = 10.0%   (PASS+FAIL，论文当前口径)
```

  该批次在论文目录内留有原始日志 `results.txt`（GB18030 编码），内容与真值**逐字一致**，可直接作为脚注出处引用：

```
========== 批次汇总 ==========
batch: /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/run_batch_20261109_171201
jsonl: /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl
total: 696 cases, 8 workers
结果: {'ERROR': 70, 'FAIL': 558, 'PASS': 62, 'ABSENT': 6}
通过率: 62/626 = 9.9%
```

- 本次审计**未修改任何 .tex/.py**；所有数字均由下列脚本实跑得到（输出同目录留存）：

| 脚本 | 作用 | 输出 |
|---|---|---|
| `eval_triage/ci_wilson.py` | 62/620、62/626、62/696 与 13 域 Wilson 95% CI、分箱核对、口径敏感性 | `ci_wilson.out.txt` |
| `eval_triage/ledger_scan.py` | 全文扫描 696/62/558/70/6/620/626/10.0/9.9/76.5/76/1007 的 file:line | `ledger_scan.out.txt` |
| `eval_triage/table_check.py` | 直接解析两个 .tex 表格，逐行验 PASS+FAIL、Pass% 四舍五入、列合计 | `table_check.out.txt` |
| `eval_triage/log_check.py` | 解析临时目录 main.log：页数、Overfull、undefined、warning | `log_check.out.txt`, `log_check_after_bibtex.out.txt` |

- 环境：Windows / PowerShell / Python 3.10.11 / TinyTeX `C:\tools\TinyTeX\bin\windows`。编译在 `D:\TEMP\audit_lfb_compile` 副本中进行，论文目录未产生任何 .aux/.log。

**一句话结论**：数值本身基本没错（13 域 PASS/FAIL/ERROR/ABSENT 与真值完全吻合，逐行四舍五入 0 偏差），问题集中在 **口径披露（620 vs 626 vs 696）、无证据的强断言（"多模型/最优"、~45-40-15 失败分布、RQ3 结论、图注"model scaling 无法弥合"）、tab:main-results 的 Total 列自相矛盾（列合计 696、Overall 却写 620）、以及 1007 与 964 的任务总数冲突**。

---

## §1 数字台账（reconciliation）

扫描范围：`main.tex`, `sections/*.tex`, `appendix/*.tex`, `figures/make_figs.py`（`ledger_scan.py` 实跑，命中 48 行）。
判定：**OK** = 与真值一致且口径自洽；**需改** = 与真值不符或与上下文口径冲突；**口径不清** = 数字对但读者无法复算（缺分母/缺来源）。

### 1.1 `696`（评测用例数）— 数字全对，但多处未点明分母

| file:line | 原文片段 | 判定 |
|---|---|---|
| sections/0_abstract.tex:8 | `on the full 696-task evaluation` | 口径不清（同句 10.0% 分母是 620，读者按 696 复算得 8.9%） |
| sections/0_abstract.tex:9 | 中文注释同句 | 口径不清 |
| sections/1_intro.tex:21 | `on the full 696-task evaluation` | 口径不清 + 见 §4(a) `multiple frontier LLMs` |
| sections/1_intro.tex:22 | 中文注释 | 口径不清 |
| sections/1_intro.tex:30 | `a 10.0\% ceiling on the full 696-task set` | OK |
| sections/1_intro.tex:31 | 中文注释 | OK |
| sections/4_experiments.tex:34 | `\caption{... full 696-task evaluation. Pass\% = PASS/(PASS+FAIL).}` | OK（caption 已点明分母） |
| sections/4_experiments.tex:35 | 中文 caption 注释 | OK |
| sections/4_experiments.tex:62 | `% Full evaluation: 696 cases total (62 PASS + 558 FAIL + 70 ERROR + 6 ABSENT).` | **OK（全篇唯一完整台账，建议提升为正文脚注）** |
| sections/4_experiments.tex:64 | 中文同句 | OK |
| sections/4_experiments.tex:67 | `full evaluation of 696 tasks ... 10.0\% (62/620 decided cases; 70 ERROR and 6 ABSENT excluded...)` | OK（本句写法最规范，建议以它为模板） |
| sections/4_experiments.tex:68 | 中文同句 | OK |
| sections/4_experiments.tex:90 | `\caption{Impact of LLM backbone (full harness, 696-task evaluation).}` | 需改（表内仅 1 个模型有数，见 §4a） |
| sections/4_experiments.tex:91 | 中文 caption | 需改 |
| sections/5_analysis.tex:13 | `from the full 696-task run (70 ERROR, 6 ABSENT, 558 FAIL)` | OK（数字对；其后的 ~45/40/15 无支撑，见 §4b） |
| sections/5_analysis.tex:14 | 中文同句 | OK |
| sections/5_analysis.tex:30 | `Pass@1 取自 696 个任务的完整评测` | OK |
| sections/7_conclusion.tex:7 | `Our full 696-task evaluation reveals ...` | 口径不清（同句 `76\%` 与 §4 的 76.5% 冲突，见 1.9） |
| sections/7_conclusion.tex:8 | 中文同句 | 口径不清 |
| appendix/B_additional_results.tex:11 | `2026-11-09 full evaluation (696 cases ...)` + `10.0\% (62 PASS / 620 decided cases); 70 ERROR and 6 ABSENT ... excluded` | OK（附录写法最规范） |
| appendix/B_additional_results.tex:12 | 中文同句 | OK |
| appendix/B_additional_results.tex:17 | `\caption{... (696 cases, ... 8 workers, 2400s timeout). Pass\% = PASS/(PASS+FAIL); ERROR and ABSENT are excluded ...}` | OK |
| appendix/B_additional_results.tex:18 | 中文 caption | OK |
| appendix/B_additional_results.tex:39 | `\textbf{Total} & 62 & 558 & 70 & 6 & \textbf{696} & 10.0` | OK |
| appendix/B_additional_results.tex:74 | `[TODO: ... Preliminary overall estimate from the 696-task run: $\sim$45/40/15 ...]` | 需改（删分布数字，见 §4b） |
| appendix/B_additional_results.tex:75 | 中文 TODO | 需改 |
| figures/make_figs.py:170 | `# Pass@1 values mapped from the 2026-11-09 full evaluation (696 cases, 13` | 需改（数值硬编码，见 §5） |

### 1.2 `62`（PASS）— 全部 OK

| file:line | 原文片段 | 判定 |
|---|---|---|
| sections/4_experiments.tex:58 | `\textbf{Overall} & \textbf{62} & \textbf{558} & \textbf{620} & \textbf{10.0}` | OK（62 = 13 行 PASS 之和，已实算） |
| sections/4_experiments.tex:62,63,64,65 | 注释台账 `62 PASS` / `62/620 = 10.0%` | OK |
| sections/4_experiments.tex:67,68 | 正文 `62/620 decided cases` | OK |
| appendix/B_additional_results.tex:11,12 | 正文 `62 PASS / 620 decided cases` | OK |
| appendix/B_additional_results.tex:39 | `Total & \textbf{62}` | OK |

### 1.3 `558`（FAIL）— 全部 OK

`4_experiments.tex:58`（Overall 行）、`:62`、`:64`（注释）、`5_analysis.tex:13`、`:14`、`B_additional_results.tex:39`。
13 行列合计实算 = 558，与真值一致（见 §3）。

### 1.4 `70`（ERROR）— 数字 OK，但方法论章节**从未定义 ERROR**

| file:line | 原文片段 | 判定 |
|---|---|---|
| sections/4_experiments.tex:62,64 | 注释台账 `70 ERROR` | OK |
| sections/4_experiments.tex:67,68 | `70 ERROR and 6 ABSENT excluded from the denominator` | OK |
| sections/5_analysis.tex:13,14 | `(70 ERROR, 6 ABSENT, 558 FAIL)` | OK |
| appendix/B_additional_results.tex:11,12 | 同 | OK |
| appendix/B_additional_results.tex:39 | `Total ... \textbf{70}` | OK |

> 口径不清：ERROR 的判据（2400s 超时？MCP 断连？agent 崩溃？）在 §2/§3/§4 一次都没出现。70/696 = 10.06% 的 ERROR 率本身需要解释——若多为基础设施故障，620 口径可辩护；若多为 agent 主动放弃，则**必须计入分母**（即 626 或 696 口径）。建议在 §4 setup 补一句 ERROR 定义。

### 1.5 `6`（ABSENT）— 全部 OK

`4_experiments.tex:62,64,67,68`、`5_analysis.tex:13,14`、`B_additional_results.tex:11,12,39` —— 均指 ABSENT=6，与真值一致。

排除的假阳性（`ledger_scan` 命中但与 ABSENT 无关）：`main.tex:75`（`sections/6_related`）、`1_intro.tex:24`（`第 6 段`）、`4_experiments.tex:46`（`eda\_other & 6 &` = PASS 数）、`B_additional_results.tex:28`（digital 行 ERROR=6）、`:34`（eda_other PASS=6）、`make_figs.py:75/179/184`（色值/图例）。

### 1.6 `620`（当前分母）— 口径自洽，但有 1 处自相矛盾

| file:line | 原文片段 | 判定 |
|---|---|---|
| sections/4_experiments.tex:58 | `\textbf{Overall} & 62 & 558 & \textbf{620} & 10.0` | **需改**：同表 13 行 `Total` 列合计 = **696**（列语义是"该域全部 run"），Overall 的 Total 却写 620 → 同一列混用两种口径 |
| sections/4_experiments.tex:63,65 | `62/620 = 10.0%` 注释 | OK |
| sections/4_experiments.tex:67,68 | `62/620 decided cases` | OK |
| appendix/B_additional_results.tex:11,12 | `62 PASS / 620 decided cases` | OK |

### 1.7 `626` / `9.9` — **全篇 .tex 命中 0 处**

| file:line | 原文片段 | 判定 |
|---|---|---|
| （无 .tex 命中） | — | **需改**：runner 官方口径是 `62/626 = 9.9%`；论文只报 620 → 审稿人拿 jsonl 复算会得 9.9%，形成"两个真值" |
| results.txt:8 | `通过率: 62/626 = 9.9%` | （非 .tex；证据文件，建议保留并在脚注引用） |

### 1.8 `10.0` — 15 处数值全部 OK，但**无一处给置信区间**

命中位置：`0_abstract.tex:8,9`；`1_intro.tex:21,22,30,31`；`4_experiments.tex:58,63,65,67,68,98`；`7_conclusion.tex:7,8`；`8_ethics.tex:16,17`；`B_additional_results.tex:11,12,39,61`。

判定：与 62/620 = 10.0000% 实算一致。但 95% Wilson CI = **[7.9%, 12.6%]**（§2）——即 10.0% / 9.9% / 8.9% 在统计上不可区分。必须加脚注（§2 提供可直接粘贴的英文/中文版本）。

### 1.9 `76.5` vs `76` — 单脚本基准对比值**前后不一致（高杀伤）**

| file:line | 原文片段 | 判定 |
|---|---|---|
| sections/4_experiments.tex:67 | `the 76.5\% reported on EDA-Scripting-Bench` | OK（references.bib:note 亦为 76.5\%） |
| sections/4_experiments.tex:68 | 中文同句 | OK |
| sections/0_abstract.tex:8 | `versus 76\% on single-script EDA benchmarks` | **需改**（统一 76.5\%） |
| sections/0_abstract.tex:9 | 中文 | 需改 |
| sections/1_intro.tex:21 | `far below the 76\% reported on single-script EDA benchmarks` | **需改** |
| sections/1_intro.tex:22 | 中文 | 需改 |
| sections/4_experiments.tex:110 | `the orchestration gap (10.0\% vs.\ 76\%)` | **需改** |
| sections/4_experiments.tex:111 | 中文 | 需改 |
| sections/7_conclusion.tex:7 | `while LLM agents achieve 76\% ...` | **需改** |
| sections/7_conclusion.tex:8 | 中文 | **需改** |

### 1.10 附带发现 A：`\Ntasks = 1007` vs 13 域清单合计 `964`（高杀伤）

| file:line | 原文片段 | 判定 |
|---|---|---|
| main.tex:40 | `\newcommand{\Ntasks}{1007}` | 口径不清 |
| sections/2_benchmark.tex:65-71 | `Digital front (194)` + `SPICE (220)` + `Physical (267)` + `Schematic (283)` = **964** | **需改**：四项相加 964，与 1007 差 43 个任务无处解释（实算见 `ci_wilson.py` SECTION E） |
| appendix/A_benchmark_details.tex:53 | `A:199 B:235 C:284 D:289 = \Ntasks{} cases` | OK（199+235+284+289 = 1007，实算一致）——说明 1007 本身没错，是 §2 的域清单漏了 43 个 |
| figures/make_figs.py:48-62, 161 | 13 域计数逐项硬编码，`total = sum(sizes)` = **964**，图内标题打印 `N=964 tasks` | **需改**（图内写 964，caption 写 1007，同页冲突） |
| sections/2_benchmark.tex:81 | `\caption{Domain distribution across \Ntasks{} tasks ...}` | 需改 |

### 1.11 附带发现 B：用户数 `268` vs `224`

| file:line | 原文片段 | 判定 |
|---|---|---|
| sections/0_abstract.tex:4 | `traces of 268 engineers` | 口径不清 |
| sections/1_intro.tex:13 | `traces of 268 engineers ... across 42 workstations` | 口径不清（另：`42 workstations` vs `698 hosts`，两个数差 16 倍，需说明 42 是"参与贡献的工作站"） |
| sections/2_benchmark.tex:11 | `1{,}511 candidates from 224 unique users` | **需改**（与 268 直接冲突） |
| appendix/A_benchmark_details.tex:53 | `268 users` | OK（与 abstract 一致） |

### 1.12 附带发现 C：2_benchmark.tex:11 `0\% rejection rate`

一段说预筛器"filters non-design-flow sessions (Q&A, permission-denied, tool-not-found)"，紧接着说"with **0% rejection rate**"。既然过滤了也不拒任何一条，等于预筛器未被验证过；这是很容易被质疑的"自相矛盾式"表述，建议改为统计口径（如"rejection rate < 1%（n=1511 抽样 100 条复核）"）或直接删掉该从句。


---

## §2 分母与置信区间（脚本实跑，输出原样粘贴）

脚本：`eval_triage/ci_wilson.py`（stdlib only，`from math import sqrt, erfc`）。
运行：`python ci_wilson.py`（完整输出见 `ci_wilson.out.txt`）。

### 2.1 三种分母的 p̂ 与 Wilson 95% CI

```
==============================================================================
SECTION A  Grand totals from run_batch_20261109_171201
==============================================================================
PASS=62  FAIL=558  ERROR=70  ABSENT=6  ->  sum=696   (expected 696)

estimator                k/n     note                               p_hat %  Wilson 95% CI  width pp
-----------------------  ------  ---------------------------------  -------  -------------  --------
PASS/(PASS+FAIL)         62/620  paper's current denominator (620)  10.00    [7.88, 12.61]  4.73
PASS/(PASS+FAIL+ABSENT)  62/626  ABSENT treated as failure (626)    9.90     [7.80, 12.49]  4.69
PASS/all 696 cases       62/696  ERROR counted as non-pass (696)    8.91     [7.01, 11.26]  4.24

delta between the 620 and 626 point estimates: 10.00% - 9.90% = 0.096 pp
620-CI and 626-CI overlap -> the '9.9' vs '10.0' decimal is noise, NOT a finding.
```

**解读（可直接用于 rebuttal）**
- 620 与 626 只差 **0.096 个百分点**，两条 CI 几乎完全重合（[7.88,12.61] vs [7.80,12.49]）。"9.9 还是 10.0"不是科学问题，是口径披露问题。
- 620 与 696 差 **1.09pp**（10.00 vs 8.91），这才是审稿人会追问的：**10.06% 的 run 是 ERROR，必须解释**。

### 2.2 13 个域各自的 p̂ 与 Wilson 95% CI

```
==============================================================================
SECTION B  Per-domain p_hat and Wilson 95% CI  (n = PASS+FAIL)
==============================================================================
domain             PASS/decided  p_hat %  Wilson 95% CI  width pp  flag
-----------------  ------------  -------  -------------  --------  -----------------------------
pnr_signoff        5/24          20.83    [9.24, 40.47]  31.2      SMALL n<30 -> CI uncomparable
characterization   5/26          19.23    [8.51, 37.88]  29.4      SMALL n<30 -> CI uncomparable
eda_other          6/33          18.18    [8.61, 34.39]  25.8
pg_layout          4/28          14.29    [5.70, 31.49]  25.8      SMALL n<30 -> CI uncomparable
schematic_netlist  13/113        11.50    [6.85, 18.69]  11.8
digital            5/45          11.11    [4.84, 23.50]  18.7
layout_virtuoso    4/39          10.26    [4.06, 23.58]  19.5
analog_context     4/43          9.30     [3.68, 21.60]  17.9
verification       3/33          9.09     [3.14, 23.57]  20.4
spice_sim          8/95          8.42     [4.33, 15.75]  11.4
waveform           2/39          5.13     [1.42, 16.89]  15.5
physical_verify    2/68          2.94     [0.81, 10.10]  9.3
layout_aether      1/34          2.94     [0.52, 14.92]  14.4

column sums: PASS=62  FAIL=558  ERROR=70  ABSENT=6  case-total=696
decided=620   p_hat=10.0000%  -> rounds to 10.0%

Weighting sensitivity (case-pooled vs mean-of-domain-rates):
  case-pooled (62/620)          = 10.00%
  unweighted mean of 13 domains = 11.02%
```

**n<30、CI 宽到不可比较的域**：`pnr_signoff` (n=24, 宽 31.2pp)、`characterization` (n=26, 29.4pp)、`pg_layout` (n=28, 25.8pp)。
`pnr_signoff 20.8%` 的 CI 是 [9.2, 40.5]、`characterization 19.2%` 是 [8.5, 37.9]——paper 用它们支撑"标准化流程域通过率约为整体两倍"，该句只能写成描述性，不能写成结论性。

### 2.3 "~7× 域间差距"是否成立

```
==============================================================================
SECTION C  Domain-gap claims (abstract / intro / concl. / Sec.4)
==============================================================================
best  (pnr_signoff)     = 20.83%  CI [9.2, 40.5]  (n=24)
worst (physical_verify) = 2.94%  CI [0.8, 10.1]  (n=68)
tie   (layout_aether)   = 2.94%  CI [0.5, 14.9]  (n=34)
ratio best/worst        = 7.08x (paper says ~7x)
CAVEAT: best-domain lower bound 9.24% vs worst-domain upper bound 10.10% -> intervals OVERLAP.
        With overlapping Wilson CIs (n=24 vs n=68), the ~7x ranking is a point-
        estimate, not a significant one: +-1 PASS in pnr_signoff moves it to 24.0% / 17.4%.
        two-proportion z = 2.84  (two-sided p = 0.0045); CIs overlap is the conservative view ->
        report the intervals, and phrase the gap as descriptive, not significant.
```

**要点**：7.08× 算术正确；但 95% CI **区间重叠**（9.24% vs 10.10%），且两个检验给出矛盾信号（CI 重叠 vs z=2.84, p=0.0045）→ 结论对方法敏感。**+1 个 PASS 就把 pnr_signoff 从 20.8% 推到 24.0%**。
→ 保留 20.8% / 2.9% 作为描述性数字可以，但 "the gap is driven by ..."（因果断言）超出证据，需降级（§4c/§4d）。
→ `layout_aether` 实为 **1/34**，CI 上界 14.9%；"both 2.9%" 是 2/68 = 1/34 的巧合，写成 "both 2.9%" 容易被误读为"两个独立证据"。


### 2.4 结果构成（供脚注引用）

```
==============================================================================
SECTION G  Outcome mix over all 696 runs (for the 'error rate' footnote)
==============================================================================
  PASS     62    8.91% of 696    10.00% of 620
  FAIL    558   80.17% of 696    90.00% of 620
  ERROR    70   10.06% of 696    11.29% of 620
  ABSENT    6    0.86% of 696     0.97% of 620
  decided fraction = 89.08% of 696
```

### 2.5 推荐口径（一句话）

> **主口径 = `62/620`（10.0%，PASS+FAIL decided），但必须在同一脚注里给出 626 与 696 两个备选 + 95% Wilson CI + ERROR 率；所有表格 Pass% 一律显式标注 `decided` 分母。**

理由：(1) 620 已是 13 域表格 Pass% 的实际分母，保留它改动最小；(2) 70 个 ERROR 未判定，当失败处理在方法学上不成立，但**必须披露**；(3) ABSENT 6 个严格说要算失败，量级仅 0.1pp，脚注足矣。

### 2.6 可直接粘贴的英文脚注（主用，长版）

```latex
% 建议位置：sections/4_experiments.tex:67，紧跟 "\textbf{10.0\%}" 之后
\footnote{All pass rates use the \emph{decided} denominator
(PASS$+$FAIL $=620$). The full batch comprises 696 runs: 62 PASS, 558 FAIL,
70 ERROR (harness/tool infrastructure, undecided) and 6 ABSENT
(task assets unavailable). Counting ABSENT as failure gives $62/626=9.9\%$
(95\% Wilson CI [7.8, 12.5]); counting ERROR as failure gives $62/696=8.9\%$
([7.0, 11.3]). Our headline figure is $62/620=10.0\%$ (95\% Wilson CI
[7.9, 12.6]); the three estimators lie within 1.1\,pp of each other and their
confidence intervals overlap, so no conclusion in this paper depends on the
choice of denominator.}
```

短版（版面紧张时用）：

```latex
\footnote{Pass rates use the decided denominator (PASS$+$FAIL$=620$):
$62/620=10.0\%$ (95\% Wilson CI [7.9, 12.6]). Counting the 6 ABSENT runs as
failures gives $62/626=9.9\%$ ([7.8, 12.5]); counting the 70 ERROR runs as
failures gives $62/696=8.9\%$ ([7.0, 11.3]).}
```

### 2.7 中文注释版（放进 .tex 的 `%` 行）

```latex
% 脚注口径说明：所有通过率使用"已判定分母"(PASS+FAIL=620)：
%   62/620 = 10.0%（Wilson 95% CI [7.9, 12.6]）。
% 全批次 696 例 = 62 PASS + 558 FAIL + 70 ERROR（框架/工具基础设施故障，未判定）
%   + 6 ABSENT（任务资产缺失）。
% 若把 6 个 ABSENT 计为失败：62/626 = 9.9%（CI [7.8, 12.5]）；
% 若把 70 个 ERROR 计为失败：62/696 = 8.9%（CI [7.0, 11.3]）。
% 三个估计量相差 ≤1.1pp 且置信区间重叠，故本文任何结论都不依赖分母选择。
```


---

## §3 表格算术校验（`table_check.py` 直接解析 .tex，实跑输出）

方法：正则解析两张表的 body 行（`sections/4_experiments.tex:44-56`、`appendix/B_additional_results.tex:25-37`），逐行验 `PASS+FAIL`、`round(100*PASS/(PASS+FAIL),1)`、列合计与 Overall 行。**所有数字都是从 .tex 里读出来再算的，不是手抄。**

### 3.1 tab:main-results（§4 表）

```
########## sections/4_experiments.tex  rows 44-56 ##########
  ln domain                 P    F   E   A  Tot  P+F   calc%   tex%  verdict
  44 pnr\_signoff           5   19   0   0   25   24   20.83   20.8  Total col 25 != PASS+FAIL 24 (Total is the 696-case count incl. ERROR/ABSENT)
  45 characterization       5   21   0   0   28   26   19.23   19.2  Total col 28 != PASS+FAIL 26 (...)
  46 eda\_other             6   27   0   0   38   33   18.18   18.2  Total col 38 != PASS+FAIL 33 (...)
  47 pg\_layout             4   24   0   0   28   28   14.29   14.3  OK
  48 schematic\_netlist    13  100   0   0  131  113   11.50   11.5  Total col 131 != PASS+FAIL 113 (...)
  49 digital                5   40   0   0   51   45   11.11   11.1  Total col 51 != PASS+FAIL 45 (...)
  50 layout\_virtuoso       4   35   0   0   40   39   10.26   10.3  Total col 40 != PASS+FAIL 39 (...)
  51 analog\_context        4   39   0   0   55   43    9.30    9.3  Total col 55 != PASS+FAIL 43 (...)
  52 verification           3   30   0   0   38   33    9.09    9.1  Total col 38 != PASS+FAIL 33 (...)
  53 spice\_sim             8   87   0   0  104   95    8.42    8.4  Total col 104 != PASS+FAIL 95 (...)
  54 waveform               2   37   0   0   47   39    5.13    5.1  Total col 47 != PASS+FAIL 39 (...)
  55 physical\_verify       2   66   0   0   73   68    2.94    2.9  Total col 73 != PASS+FAIL 68 (...)
  56 layout\_aether         1   33   0   0   38   34    2.94    2.9  Total col 38 != PASS+FAIL 34 (...)
  column sums: PASS=62 FAIL=558 ERROR=0 ABSENT=0 TotalCol=696 decided=620
  recomputed overall = 62/620 = 10.0000% -> 10.0
  tex Overall row (line 58): ['Overall', '62', '558', '620', '10.0']
  -> arithmetic defects: 0  []
```

**结论：逐行核验 Pass% 无偏差。** 实测 p̂ 与四舍五入结果：

| 域 | PASS/decided | 精确 p̂ | 应显示 | tex 显示 | 判定 |
|---|---|---|---|---|---|
| pnr_signoff | 5/24 | 20.8333 | 20.8 | 20.8 | ✔ |
| characterization | 5/26 | 19.2308 | 19.2 | 19.2 | ✔ |
| eda_other | 6/33 | 18.1818 | 18.2 | 18.2 | ✔ |
| pg_layout | 4/28 | 14.2857 | 14.3 | 14.3 | ✔ |
| schematic_netlist | 13/113 | 11.5044 | 11.5 | 11.5 | ✔ |
| digital | 5/45 | 11.1111 | 11.1 | 11.1 | ✔ |
| layout_virtuoso | 4/39 | 10.2564 | 10.3 | 10.3 | ✔ |
| analog_context | 4/43 | 9.3023 | 9.3 | 9.3 | ✔ |
| verification | 3/33 | 9.0909 | 9.1 | 9.1 | ✔ |
| spice_sim | 8/95 | 8.4211 | 8.4 | 8.4 | ✔ |
| waveform | 2/39 | 5.1282 | 5.1 | 5.1 | ✔ |
| physical_verify | 2/68 | 2.9412 | 2.9 | 2.9 | ✔ |
| layout_aether | 1/34 | 2.9412 | 2.9 | 2.9 | ✔ |
| **Overall** | **62/620** | **10.0000** | **10.0** | **10.0** | ✔ |

**唯一问题（结构，非算术）**：`Total` 列的语义是"该域全部 run 数"（含 ERROR/ABSENT，合计 **696**），但 Overall 行写 **620**（decided）。同列混用两种口径，且 12/13 行 `PASS+FAIL ≠ Total`。这是审稿人一定会算的第一件事。

**修复方案（推荐 B）**
- A. 把 Overall 的 Total 改 **696** → 最小改动，但 `25 vs 5+19` 仍扎眼。
- B.（推荐）`Total` 前加 `ERROR` / `ABSENT` 两列，与附录表统一 → `5+19+0+1=25`、Overall `62+558+70+6=696` 全部自洽。
- C. 删掉 `Total` 列。

### 3.2 tab:full-domain-results（附录 B 表）

```
########## appendix/B_additional_results.tex  rows 25-37 ##########
  ln domain                 P    F   E   A  Tot  P+F   calc%   tex%  verdict
  25 schematic\_netlist    13  100  18   0  131  113   11.50   11.5  OK
  26 spice\_sim             8   87   7   2  104   95    8.42    8.4  OK
  27 physical\_verify       2   66   4   1   73   68    2.94    2.9  OK
  28 digital                5   40   6   0   51   45   11.11   11.1  OK
  29 analog\_context        4   39  12   0   55   43    9.30    9.3  OK
  30 waveform               2   37   8   0   47   39    5.13    5.1  OK
  31 layout\_virtuoso       4   35   0   1   40   39   10.26   10.3  OK
  32 layout\_aether         1   33   4   0   38   34    2.94    2.9  OK
  33 verification           3   30   5   0   38   33    9.09    9.1  OK
  34 eda\_other             6   27   4   1   38   33   18.18   18.2  OK
  35 pg\_layout             4   24   0   0   28   28   14.29   14.3  OK
  36 characterization       5   21   2   0   28   26   19.23   19.2  OK
  37 pnr\_signoff           5   19   0   1   25   24   20.83   20.8  OK
  column sums: PASS=62 FAIL=558 ERROR=70 ABSENT=6 TotalCol=696 decided=620
  recomputed overall = 62/620 = 10.0000% -> 10.0
  tex Overall row (line 39): ['Total', '62', '558', '70', '6', '696', '10.0']
  -> arithmetic defects: 0  []
```

**结论：逐行核验无偏差。** 13 行 `PASS+FAIL+ERROR+ABSENT = Total` 全部成立；列合计 `62/558/70/6`、行合计 `696` 与真值完全一致；Overall `62/620 = 10.0` 与 620 口径自洽。

### 3.3 两表交叉一致性

| 检查项 | 结果 |
|---|---|
| 两表 13 行是同一集合 | ✔（排序不同：§4 按 Pass% 降序，附录按案量降序） |
| PASS/FAIL 逐行相同 | ✔ 13/13 |
| 列合计 | ✔ PASS 62 / FAIL 558 / ERROR 70 / ABSENT 6；行合计 696；decided 620 |
| Overall 10.0 与 620 口径 | ✔ 62/620 = 10.0000 |
| caption 声明的 Pass% 定义与数据一致 | ✔ 两表均 `PASS/(PASS+FAIL)` |
| §5 引用的 20.8 / 19.2 / 18.2 | ✔ 与表一致 |

**建议**：附录表是主表的 100% 重排（信息冗余）。ICML 11 页的预算下，最划算的是**主文表补 ERROR/ABSENT 两列、删附录重复表**（或把附录表改成按 4 个 area group 聚合）。


---

## §4 论断审计（claim vs evidence）

### 4(a) "the best frontier model achieves only 10.0%" + 多模型表的 "---" —— **不成立，必须改**

**证据现状**
- `sections/4_experiments.tex:22` 正文列出 5 个模型：`DeepSeek-V4-Pro (primary), GLM-5.2, Kimi-K2.6, DeepSeek-V4-Flash, Doubao-Seed-2.0-Pro`。
- `sections/4_experiments.tex:94-103` 表 `tab:llm-comparison` 只有 4 行（**Doubao 直接消失**），其中 3 行是 `---`。
- `appendix/B_additional_results.tex:48` 自己写着：`[TODO: multi-model comparison. Currently only DeepSeek-V4-Pro has data; GLM-5.2 / Kimi-K2.6 / DeepSeek-V4-Flash are pending.]`
- 全篇只有 **1 个模型、1 次评测**的数据点：10.0%。

**因此以下三处强断言都缺证据：**

| file:line | 现文 | 问题 |
|---|---|---|
| 0_abstract.tex:8 | `the best frontier model achieves only \textbf{10.0\% Pass@1}` | "best" 隐含做过模型间比较；实际只测了 1 个 |
| 1_intro.tex:21 | `We evaluate multiple frontier LLMs ... the best system achieves only 10.0\%` | 同上，"multiple" 是事实性陈述 |
| 4_experiments.tex:110 | `scaling the backbone ... 23.3pp ... We expect a similar pattern ... confirming that tool-chain grounding depth, not model size, is the binding constraint` | 23.3pp 来自 **EDA-Scripting-Bench**，不是本基准；`expect` 与 `confirming` 逻辑自相矛盾 |

**改写建议（可直接替换）**

`0_abstract.tex:8` 英文：
```latex
Under a controlled harness, a single frontier backbone (DeepSeek-V4-Pro) reaches only
\textbf{10.0\%} Pass@1 (62/620 decided runs) on the full 696-run evaluation---versus the
76.5\% reported for single-script EDA benchmarks---which suggests that multi-step flow
orchestration is qualitatively harder than isolated code generation.
```
`0_abstract.tex:9` 中文注释：
```latex
% 在受控框架下，单一前沿骨干模型（DeepSeek-V4-Pro）在 696 个 run 的完整评测上仅达到
% 10.0%（62/620 已判定 run）——而单脚本 EDA 基准上报告的是 76.5%——这暗示多步流程编排
% 在本质上比孤立的代码生成更难。
```

`1_intro.tex:21` 英文：
```latex
We evaluate a frontier LLM agent (DeepSeek-V4-Pro) under a controlled Cline harness and
obtain a striking result: it achieves only \textbf{10.0\%} Pass@1 on the full 696-run
evaluation, far below the 76.5\% reported on single-script EDA benchmarks~\cite{zhu2026edascript}.
```
`1_intro.tex:22` 中文注释：
```latex
% 我们在受控的 Cline 框架下评测了一个前沿 LLM 智能体（DeepSeek-V4-Pro），得到一个引人
% 注目的结果：它在 696 个 run 的完整评测上仅取得 10.0% Pass@1，远低于单脚本 EDA 基准上
% 报告的 76.5%。
```

`tab:llm-comparison` 的处理（三选一）：
- **A（推荐，成本最低）**：整表删除。`4_experiments.tex:105-108` 注释已承认"多模型对比数据待补"；把一张 3/4 行是 `---` 的表放进投稿版是明确的减分项。RQ3 相应改写成 open question（见 4(d)）。
- B：保留但改名 `\caption{Single-backbone evaluation (multi-model sweep pending).}`，表体只留 `DeepSeek-V4-Pro & 10.0`，删掉 `---` 行。
- C：真跑完剩下 4 个模型（每个 696 run；按本批次 ~24h/8 workers 估，5 模型 ≈ 5 天机器时间）。

> 同一问题波及 `1_intro.tex:21` 的 `scaling the backbone from 53\% to 76\% on simpler tasks`：53% 与 76.5% **都是 EDA-Scripting-Bench 的数**，本基准没有 backbone 扫描，不能表述为"本基准亦如此"。


### 4(b) §5 failure taxonomy 的 "~45% / ~40% / ~15%" —— **唯一完全没有实测支撑的分类数字，建议整段替换**

**问题定位**
- `sections/5_analysis.tex:13-23`：把 558 个 FAIL 分成 45/40/15，同时又写 `preliminary estimates derived from inspecting a sample of failed traces` 和 `a fully systematic per-trace labeling is left to future work`。
- `appendix/B_additional_results.tex:74`：`[TODO: ... Preliminary overall estimate from the 696-task run: $\sim$45/40/15 ...]`
- **无任何 jsonl 字段能支撑这三个数字**：jsonl 只记录终态（PASS/FAIL/ERROR/ABSENT），没有 per-assertion 的失败模式标注。而且 45+40+15 = 100%，形式上像"基于全量标注"，与"sample of failed traces"自相矛盾。
- 附带：`(1) No-output` 的定义里混进了 ERROR，而 ERROR 已被排除在 620 分母之外——分类的分母（558？620？628？）从未说明。

**建议改成"方法学协议 + 已知锚点"（不编造分布）**

`sections/5_analysis.tex:13` 英文替换（整段）：
```latex
\textbf{Taxonomy protocol.} We define three mutually exclusive failure modes over the
696 runs: (i) \emph{no-output / aborted}, where the run terminates in ERROR (70 runs)
or yields no \texttt{submit.zip} (a subset of the 6 ABSENT runs); (ii) \emph{semantic /
partial failure}, where a deliverable exists but at least one reference assertion fails
(a subset of the 558 FAIL runs); and (iii) \emph{contract / format failure}, where the
content is plausible but file-layout or naming assertions fail. The current batch
records only the terminal status per run, not which assertion failed first, so the only
quantities we can report with certainty are the run-level outcome counts
(PASS 62 / FAIL 558 / ERROR 70 / ABSENT 6 of 696). We deliberately make \emph{no}
quantitative claim about the split among (i)--(iii); a systematic per-trace labelling
pass (two annotators, Cohen's $\kappa$ reported) is in progress and will appear in the
camera-ready version.
```
`sections/5_analysis.tex:14` 中文注释：
```latex
% \textbf{分类协议。} 我们在 696 个 run 上定义三类互斥的失败模式：(i) 无输出/中止——
% run 以 ERROR 终止（70 个），或未产出 submit.zip（6 个 ABSENT 的子集）；(ii) 语义/部分
% 失败——有交付件但至少一条参考断言不通过（558 个 FAIL 的子集）；(iii) 契约/格式失败——
% 内容合理但文件结构或命名断言不通过。当前批次只记录每个 run 的终态，不记录哪条断言先
% 失败，因此能确证给出的只有 run 级结果计数（PASS 62 / FAIL 558 / ERROR 70 / ABSENT 6，
% 共 696）。我们刻意不对 (i)-(iii) 的占比作任何定量断言；系统性的逐轨迹标注（双标注员、
% 报告 Cohen's kappa）正在进行，将在 camera-ready 版本给出。
```

`sections/5_analysis.tex:16-23`（三个 `\textbf` 条目）**保留定性描述，删掉括号里的百分比**：
- `\textbf{(1) No-output failures ($\sim$45\%).}` → `\textbf{(1) No-output / aborted failures.}`
- `\textbf{(2) Partial-output failures ($\sim$40\%).}` → `\textbf{(2) Semantic / partial failures.}`
- `\textbf{(3) Format failures ($\sim$15\%).}` → `\textbf{(3) Contract / format failures.}`
- 各条目里的 "They are concentrated in the deepest-grounding domains---physical\_verify and layout\_aether" 同样是未验证的分布断言 → 改为 `Among the failed traces we inspected, the aborted cases were concentrated in physical\_verify and layout\_aether.`（明确样本性质）

`appendix/B_additional_results.tex:74-75` 替换（删数字）：
```latex
[TODO: failure-category breakdown by domain (no-output / partial / format), stacked bar
chart + table. The current batch records only terminal status per run, so we report the
outcome anchors (62 PASS / 558 FAIL / 70 ERROR / 6 ABSENT of 696) and defer the
per-category split until the systematic labelling pass is complete.]
```
```latex
% [待办：各领域失败类别分解（无输出 / 部分输出 / 格式），堆叠柱状图 + 表。当前批次只记录
% 每个 run 的终态，故仅给出结果锚点（62 PASS / 558 FAIL / 70 ERROR / 6 ABSENT，共 696），
% 逐类别占比待系统性标注完成后再报告。]
```

> **为什么必须删**：这是全文唯一一处"没有对应数据字段"的定量结果。审稿人若要求放出标注脚本/标注数据，交不出来；而删掉它不损失任何结论 —— "编排失败 ≠ 代码生成失败"本来靠 grounding-depth 与 ERROR/ABSENT 锚点就能讲清楚。


### 4(c) §5 grounding_depth 三档区间 14–21% / 8–14% / 3–5% —— **三档全部与 §4 表格不符，逐档核对如下**

脚本输出（`ci_wilson.py` SECTION D）：

```
Depth 1--2  paper says 14--21% | actual min=18.18% max=20.83% | unweighted mean=19.42% | case-pooled=19.28% (16/83)
Depth 3--5  paper says 8--14 % | actual min=8.42% max=14.29% | unweighted mean=10.57% | case-pooled=10.35% (41/396)
Depth 6+    paper says 3--5  % | actual min=2.94% max=5.13% | unweighted mean=3.67% | case-pooled=3.55% (5/141)
```

| 档位（§5_analysis.tex:33/35/37） | 该档包含的域 | §4 表中实际值 | 宣称区间 | 判定 | 建议值 |
|---|---|---|---|---|---|
| Depth 1–2 | pnr 20.8 / char 19.2 / eda\_other 18.2 | **18.2 – 20.8** | `14--21\%` | **不符**（下界 14 是 pg\_layout 的 14.3，被错误地算进了本档的"下界"） | `18.2--20.8\%` |
| Depth 3–5 | pg 14.3 / sch 11.5 / dig 11.1 / virt 10.3 / ana 9.3 / ver 9.1 / spice 8.4 | **8.4 – 14.3** | `8--14\%` | **不符**（上界 14.3 > 14） | `8.4--14.3\%` |
| Depth 6+ | waveform 5.1 / phys 2.9 / aeth 2.9 | **2.9 – 5.1** | `3--5\%` | **不符**（双端越界：5.1 > 5，2.9 < 3） | `2.9--5.1\%` |

**替换文本**

`sections/5_analysis.tex:33`：
```latex
\item \textbf{Depth 1--2} (pnr\_signoff, characterization, eda\_other): 18.2--20.8\% pass.
```
`sections/5_analysis.tex:35`：
```latex
\item \textbf{Depth 3--5} (pg\_layout, schematic\_netlist, digital, layout\_virtuoso,
analog\_context, verification, spice\_sim): 8.4--14.3\% pass.
```
`sections/5_analysis.tex:37`：
```latex
\item \textbf{Depth 6+} (waveform, physical\_verify, layout\_aether): 2.9--5.1\% pass.
```
中文注释行（34/36/38）同步改为 `18.2--20.8\%` / `8.4--14.3\%` / `2.9--5.1\%`。

**此外还有两处结构性问题（比区间更严重）**

1. **正文 3 档 vs 图 6 档不一致**：正文把 13 域压成 3 档，而 `figures/make_figs.py:181-184` 画的是 **6 个点**（1.5 / 3 / 4 / 5 / 6 / 7，标注 `pg_layout` / `schematic+digital` / `spice+verif+layout` / `waveform` / `phys_verify+layout`）。读者对不上正文的 3 档。→ 要么正文改成 6 档，要么图改成 3 档（推荐图改 3 档，与正文一致）。
2. **"单调下降"是构造出来的**：`sections/5_analysis.tex:44` 图注称 `Pass@1 decreases monotonically with tool-chain grounding depth`，但深度分档是作者手工指定的（`make_figs.py:174-180` 注释），并非从数据估计——只要分档顺序定了，"单调"必然成立。这是循环论证，必须降级为 `Domains grouped by our depth annotation show a monotone ordering by construction; the annotation is a design decision, not a measured quantity.`

### 4(d) RQ3 "We expect..." —— **属于未验证假设，且与同一句的 "confirming" 直接冲突**

`sections/4_experiments.tex:110` 现文：
> On EDA-Scripting-Bench, scaling the backbone ... 23.3pp ... while scaling the harness ... 56.8pp---the grounding axis is binding. **We expect a similar pattern on \bench**: the orchestration gap (10.0\% vs.\ 76\%) is too large to be closed by model scaling alone, **confirming that** tool-chain grounding depth, not model size, is the binding constraint (RQ3).

问题：①"expect" 是假设，②紧接的"confirming" 是结论 —— **一句话里同时假设和确认**；③bench 上没有任何 backbone 扫描；④10.0% vs 76.5% 是跨基准比较（不同任务、不同工具、不同年份），不能作为"model scaling 不够"的证据。

**替换文本（英文）**
```latex
On EDA-Scripting-Bench~\cite{zhu2026edascript}, scaling the backbone from weakest to
strongest yields a 23.3\,pp improvement, while improving observation fidelity (the
harness) yields 56.8\,pp---there, the grounding axis dominates. We \emph{hypothesise}
that the same holds on \bench: the 10.0\% ceiling is far below the 76.5\% reported for
single-script tasks on a different benchmark, and closing such a gap by backbone scaling
alone seems implausible. We stress that this remains an \emph{untested hypothesis}:
Table~\ref{tab:llm-comparison} contains a single backbone, so \bench{} currently
provides no evidence for or against it. RQ3 is therefore left open, and a full
backbone sweep is the first item on our camera-ready agenda.
```
**替换文本（中文注释）**
```latex
% 在 EDA-Scripting-Bench 上，把骨干模型从最弱换到最强带来 23.3pp 提升，而改进观测保真度
% （框架）带来 56.8pp——在该基准上接地维度占主导。我们"假设"\bench{} 上同样如此：10.0%
% 的天花板远低于另一基准上单脚本任务报告的 76.5%，仅靠骨干扩展弥合这样的差距似乎不现实。
% 但必须强调这只是"未经检验的假设"：表~\ref{tab:llm-comparison} 只有一个骨干模型，因此
% \bench{} 目前既不能支持也不能反驳它。RQ3 因此保持开放，完整骨干扫描是本稿 camera-ready
% 的首要事项。
```

RQ3 的提问方式（`4_experiments.tex:15`）也建议从 `Does scaling the backbone close the orchestration gap, or is it bounded by tool-chain grounding?` 保留不动——问题本身没问题，是答案被提前写死了。

### 4(e) 其他需要降级的断言（按杀伤力排序）

| # | file:line | 现文 | 问题 | 建议 |
|---|---|---|---|---|
| e1 | 5_analysis.tex:44（图注） | `The gap is not closed by model scaling, indicating a grounding bottleneck.` | 没有 model-scaling 实验，"not closed by model scaling" 无证据 | 删该句，改为 `Pass@1 by depth annotation (see §\ref{sec:grounding-depth}); the ordering is descriptive.` |
| e2 | 0_abstract.tex:10 / 1_intro.tex:21 / 5_analysis.tex:29 | `Failure analysis reveals the gap is driven by tool-chain grounding depth` / `We show this gap is driven by ...` | "driven by" 是因果断言；实际只有相关性 + 手工分档 | 改 `is associated with` / `is consistent with` |
| e3 | 4_experiments.tex:74 | `This $\sim$7$\times$ gap is not explained by task difficulty alone---all domains require EDA domain knowledge. The difference lies in tool-chain grounding depth` | 排除了一个混杂因素就宣称找到原因；且 7× 的 CI 重叠（§2.3） | `A point-estimate gap of 7$\times$ separates the extremes, though the per-domain intervals overlap; we attribute it, tentatively, to tool-chain grounding depth` |
| e4 | 4_experiments.tex:98 + 90（表+caption） | `Impact of LLM backbone` 表只有 1 行有数 | 见 4(a) | 删表或改名单骨干 |
| e5 | 1_intro.tex:13 + 0_abstract.tex:4 vs 2_benchmark.tex:11 | `268 engineers` vs `224 unique users` | 人数口径冲突 | 统一（推荐 268，并在 §2 注明 224 是"mc≥30 候选会话的去重用户数"） |
| e6 | 2_benchmark.tex:11 | `with 0\% rejection rate` | 说预筛器过滤了非设计流会话，却拒 0 条 → 自相矛盾 | 改为抽样复核口径，或删该从句 |
| e7 | 2_benchmark.tex:65-71 + fig 81 | 四组 194+220+267+283 = **964** ≠ `\Ntasks`=1007 | 见 §1.10 | 补齐 43 个任务，或改为 `\Ntasks{}=964` / 显式说明"实测子集" |
| e8 | 5_analysis.tex:60 | `top 3 domains = 44\%`、`digital/verification 13\%` | 用的是 **696 评测集**的计数（44.3% / 12.8%），但 §2 的域分布用的是 964/1007 语料 → 同一个"分布"在两个节里分母不同 | 明确 `of the 696 evaluated runs` |


---

## §5 图管线审计（`figures/make_figs.py`）

### 5.1 硬编码的数字清单

| 行 | 硬编码内容 | 与 §4/§5 的一致性 |
|---|---|---|
| 48-62 | 13 域**任务计数**：spice\_sim 177, schematic\_netlist 166, physical\_verify 106, layout\_aether 66, analog\_context 63, digital 59, layout\_virtuoso 57, verification 55, waveform 54, eda\_other 53, characterization 43, pg\_layout 38, pnr\_signoff 27 | **与 `sections/2_benchmark.tex:65-71` 逐项一致 ✔**；但合计 **964**，与 `\Ntasks`=1007 差 43（§1.10） |
| 93, 161 | `total = sum(sizes)` → 图内标题打印 `Domain distribution (N=964 tasks, 13 domains)` | **与 caption 的 `\Ntasks{}` = 1007 冲突 ✘**（同一页：图上 964、caption 1007） |
| 170-180（注释） | `Depth 1-2: pnr 20.8 + char 19.2 + eda_other 18.2 -> ~19`；`Depth 3: pg_layout 14.3 -> 14`；`Depth 4: schematic 11.5 + digital 11.1 -> 11`；`Depth 5: virt 10.3 + ana 9.3 + ver 9.1 + spice 8.4 -> 9`；`Depth 6: waveform 5.1 -> 5`；`Depth 7+: phys 2.9 + aeth 2.9 -> 3` | 逐项与 §4 表一致 ✔（`ci_wilson.py` 复算 19.42/14.29/11.31/9.28/5.13/2.94 → 19/14/11/9/5/3 ✔）；但这是**等权域平均**，与 62/620 的 case-pooled 口径不同 |
| 181-184 | `depth_mid = [1.5,3,4,5,6,7]`、`pass_rate = [19,14,11,9,5,3]`、`depth_labels` | 与 §5 正文的 **3 档**（1–2 / 3–5 / 6+）**不一致 ✘** |
| 192-194 | `text-in/text-out`、`moderate grounding`、`deep tool chaining` | 定性标签，无数字问题 |
| 200 | `ax.set_ylim(-2, 26)` | 与 `ax.text(..., 23, ...)` 绑定；若上界变化需同步 |

**关键事实：`make_figs.py` 完全不读 jsonl/status 文件。** `domain_pie.pdf` 用任务语料计数，`grounding_depth.pdf` 用**手工抄写的 6 个 Pass@1 值**。→ **换批次不会自动刷新任何图**。

### 5.2 不一致项汇总（3 项）

1. **N = 964（图内）vs 1007（caption / `\Ntasks`）** —— 同一页可见冲突。
2. **6 个深度点（图）vs 3 个深度档（正文 §5）** —— 读者无法对照。
3. **等权平均 vs case-pooled** —— `Depth 3-5` 图上是 9%（域等权 9.28%），case-pooled 10.35%；`Depth 1-2` 19%（等权 19.42%）vs 19.28%（pooled）。差异不大，但 caption 必须声明"domain-averaged, unweighted"。

### 5.3 最小改动方案（刷新为"从数据读"）

**改动 1 — 域计数与 Pass@1 改为读批次产物**
在 `make_figs.py` 顶部（替换 48-62 的 13 元组）：
```python
import json, collections
JSONL = "<batch_dir>/status.jsonl"          # run_batch_20261109_171201 的产物
counts, outcome = collections.Counter(), collections.Counter()
for line in open(JSONL, encoding="utf-8"):
    r = json.loads(line)
    counts[r["domain"]] += 1                          # 字段名按实际 schema 调整
    outcome[(r["domain"], r["status"])] += 1          # PASS/FAIL/ERROR/ABSENT
GROUP = {"spice_sim": "SPICE / char", "schematic_netlist": "Schematic / analog",
         "physical_verify": "Physical / layout", "layout_aether": "Physical / layout",
         "analog_context": "Schematic / analog", "digital": "Digital front",
         "layout_virtuoso": "Physical / layout", "verification": "Digital front",
         "waveform": "Schematic / analog", "eda_other": "Digital front",
         "characterization": "SPICE / char", "pg_layout": "Physical / layout",
         "pnr_signoff": "Digital front"}
ORDER = sorted(counts, key=lambda d: -counts[d])
domains = [(d, counts[d], GROUP[d]) for d in ORDER]
```
（`domain_colors` 字典 71-89、标签排布 92-165 都不用动。）

**改动 2 — `grounding_depth.pdf` 按 bin 现算**
把 `make_figs.py:181-182` 替成：
```python
BINS = [("1-2", ["pnr_signoff", "characterization", "eda_other"], 1.5),
        ("3-5", ["pg_layout", "schematic_netlist", "digital", "layout_virtuoso",
                 "analog_context", "verification", "spice_sim"], 4.0),
        ("6+",  ["waveform", "physical_verify", "layout_aether"], 7.0)]
def bin_rate(ds):                       # case-pooled，与 §4 表同口径
    k = sum(outcome[(d, "PASS")] for d in ds)
    n = sum(outcome[(d, "PASS")] + outcome[(d, "FAIL")] for d in ds)
    return 100.0 * k / n
depth_mid = np.array([b[2] for b in BINS])
pass_rate = np.array([bin_rate(b[1]) for b in BINS])
```
→ 3 个点，与正文 3 档对齐（同时也消除了 5.2 的第 2、3 项不一致）。

**改动 3 — 让 N 自动一致**：`total` 由 `sum(sizes)` 直接得出后，`2_benchmark.tex:81` 的 caption 不应再写 `\Ntasks{}`。**先解决 §1.10 的 43 个任务归属**，再决定 caption 用 964 还是 1007。

**改动 4（最省事，若短期不刷新）**：`make_figs.py:161` 标题去掉 N（`Domain distribution (13 domains)`），`2_benchmark.tex:81` caption 改为 `the 964 tasks carrying a curated domain label`——一句话消除同页冲突。

> `figures/pipeline.pdf` 由 `pipeline.svg` 经 cairosvg 渲染，与数字无关。本次**未运行** `make_figs.py`（避免覆盖论文目录里的既有 PDF），只做静态核对。


---

## §6 编译体检（临时目录副本，论文目录零污染）

### 6.1 命令

```powershell
$src='D:\...\EDA-LiveFlow-Bench_ICML2027'
$tmp="$env:TEMP\audit_lfb_compile"
if(Test-Path $tmp){Remove-Item -Recurse -Force $tmp}
Copy-Item -Path (Join-Path $src '*') -Destination $tmp -Recurse -Force

cd $tmp
$env:PATH = 'C:\tools\TinyTeX\bin\windows;' + $env:PATH
pdflatex.exe -interaction=nonstopmode -file-line-error main.tex   # pass 1
pdflatex.exe -interaction=nonstopmode -file-line-error main.tex   # pass 2
python log_check.py D:\TEMP\audit_lfb_compile\main.log
```

实际临时目录：`D:\TEMP\audit_lfb_compile`（`.aux/.log/.pdf` 只在此产生，论文目录未新增任何文件）。

### 6.2 结果摘要

| 指标 | 两遍 pdflatex（任务要求） | bibtex + 两遍 pdflatex（对照） |
|---|---|---|
| 是否成功 | **成功**（exit 0，无 `!` 错误） | 成功（exit 0） |
| 页数 | **11 页** | **11 页** |
| `!` 硬错误 | **0** | 0 |
| Overfull \hbox 总数 / **>20pt 条数** | 5 / **3** | 5 / **3** |
| Underfull \hbox / \vbox | 69 / 3 | 70 / 3 |
| **Undefined citations** | **2**（`rao2026sap`, `sulthanpete2026nyris`） | **0** |
| **Undefined references** | **0** | **0** |
| warning 行数 | 5 | 1（仅 hyperref empty anchor） |

`log_check.py` 在两遍 pdflatex 后的输出（`log_check.out.txt`，原样粘贴）：

```
Output written: Output written on main.pdf (11 pages, 257253 bytes)

'!' hard errors: 0

Overfull \hbox total: 5   >20pt: 3
    45.9pt  Overfull \hbox (45.92218pt too wide) in paragraph at lines 35--35
    29.8pt  Overfull \hbox (29.83337pt too wide) in paragraph at lines 37--47
    26.9pt  Overfull \hbox (26.88324pt too wide) in paragraph at lines 54--54
    11.6pt  Overfull \hbox (11.57347pt too wide) in paragraph at lines 54--54
     6.0pt  Overfull \hbox (5.96777pt too wide) in paragraph at lines 21--42

Underfull \hbox: 69
Underfull \vbox: 3

Undefined citations: 2 unique=['rao2026sap', 'sulthanpete2026nyris']
Undefined references: 0 unique=[]
  'There were undefined citations' present: True
  'There were undefined references' present: False

Total warning lines: 5; first 10:
  L445: Package hyperref Warning: Ignoring empty anchor on input line 66.
  L692: Package natbib Warning: Citation `rao2026sap' on page 8 undefined on input line 7.
  L695: Package natbib Warning: Citation `sulthanpete2026nyris' on page 8 undefined on input line 7.
  L878: Package natbib Warning: There were undefined citations.
  L887: LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
```

### 6.3 Overfull >20pt 定位（按 log 里的文件标记回溯到源文件）

| 宽度 | 源位置 | 内容 | 建议修法 |
|---|---|---|---|
| **45.9pt** | `appendix/C_experimental_details.tex:35`（`verbatim` 里的 `providers.json`，报 "lines 35--35"） | `"baseURL": "http://agi-gateway.cxmt.com/cloud/v1",` | verbatim 行太长：拆行 / 改 `\scriptsize` / 缩短 URL |
| **29.8pt** | `appendix/A_benchmark_details.tex:37-47`（`tab:keywords`） | `\begin{tabular}{@{}llp{0.52\linewidth}@{}}` 的关键词列 | `p{0.52\linewidth}` → `p{0.45\linewidth}` |
| **26.9pt** | `sections/2_benchmark.tex:54`（`tab:task-schema` 的 `\texttt{outputs/submit.zip}` 行，报 "lines 54--54"） | `\OT1/pcr/m/n/9 outputs/submit.zip` | 单元格加 `\allowbreak`：`\texttt{outputs/{\allowbreak}submit.zip}` |
| 11.6pt | 同 `2_benchmark.tex` 表内 | — | 可忽略 |
| 6.0pt | `sections/2_benchmark.tex:21--42` | — | 可忽略 |

> 只有 3 条 >20pt，全在表格/附录；45.9pt 那条在双栏里越界约 1.6cm，camera-ready 前建议修掉。

### 6.4 两个必须修的问题

**1) undefined citations（2 条）**
`references.bib:91` (`rao2026sap`) 与 `references.bib:99` (`sulthanpete2026nyris`) 在 bib 里**存在**，但论文目录里的 `main.bbl` 是旧的、不含这两条，而 `sections/9_reproducibility.tex:7` 引用了它们。我在临时副本里补跑 `bibtex main` + 两遍 pdflatex 后：

```
Output written on main.pdf (11 pages, 258205 bytes)
Undefined citations: 0 unique=[]
Undefined references: 0 unique=[]
'!' hard errors: 0
Total warning lines: 1
  L444: Package hyperref Warning: Ignoring empty anchor on input line 66.
```

**修法**：投稿前跑完整链 `pdflatex → bibtex main → pdflatex → pdflatex`，并把更新后的 `main.bbl` 一并提交（或让 CI 每次重建）。

**2) 两遍 pdflatex 后仍有 `Label(s) may have changed`**
交叉引用要**三遍**才收敛（我在 pass 3 验证：该 warning 消失，PDF 稳定在 257253 字节）。`main.tex:9` 注释写的是四步链，实际要再补一次 `pdflatex`。

### 6.5 其他

- 图表引用：undefined references = **0**，`\ref`/`\label` 全部解析。
- 缺包：无（TinyTeX 已含 icml2026.sty / booktabs / algorithm / algorithmic / multirow / tabularx）。
- 页数 **11 页**（含 references、不含 appendix）。ICML 正文 8 页限制需作者自行确认——本次只报页数，不做页限判定。


---

## TOP 10 必改项（按对审稿人的杀伤力排序）

> 格式：`file:line` → 现文 → 改为 → 一句话理由

### T1. §5 失败分类的 ~45/40/15 是全文唯一无数据支撑的定量结果
- **位置**：`sections/5_analysis.tex:16`、`:19`、`:22`（+ `appendix/B_additional_results.tex:74`）
- **现文**：`\textbf{(1) No-output failures ($\sim$45\%).}` / `($\sim$40\%).` / `($\sim$15\%).`
- **改为**：删三个括号百分比（条目名改 `No-output / aborted failures.`、`Semantic / partial failures.`、`Contract / format failures.`）；`sections/5_analysis.tex:13` 整段替换为 §4(b) 的 "Taxonomy protocol" 段；附录 `B:74` 删 `$\sim$45/40/15`，改报 `62/558/70/6 of 696` 锚点。
- **理由**：jsonl 无 per-assertion 失败模式字段，三个数字凭空而来且和为 100%（形式上冒充全量标注）；这是"编造数据"指控唯一的落脚点。

### T2. "the best frontier model" / "multiple frontier LLMs" —— 只测了 1 个模型
- **位置**：`sections/0_abstract.tex:8`、`sections/1_intro.tex:21`
- **现文**：`the best frontier model achieves only 10.0\% Pass@1` / `We evaluate multiple frontier LLMs ... the best system achieves only 10.0\%`
- **改为**：`a single frontier backbone (DeepSeek-V4-Pro) reaches only 10.0\% (62/620 decided runs)` / `We evaluate a frontier LLM agent (DeepSeek-V4-Pro)`（完整句见 §4(a)）。
- **理由**：`best`/`multiple` 是可证伪的事实陈述，而 `tab:llm-comparison` 三行是 `---`、附录 `B:48` 自认 "pending"。

### T3. `tab:llm-comparison` 整表是空壳（3/4 行 "---"，且漏掉 Doubao）
- **位置**：`sections/4_experiments.tex:88-104`（caption `Impact of LLM backbone`）、`appendix/B_additional_results.tex:51-68`（`tab:per-model` 同样 4 行 `---`）
- **现文**：`DeepSeek-V4-Pro & 10.0` + `GLM-5.2 & ---` + `Kimi-K2.6 & ---` + `DeepSeek-V4-Flash & ---`
- **改为**：删两表（推荐）；或 caption 改 `Single-backbone evaluation` 并只留一行；同时把 `4_experiments.tex:22` 的 5 模型清单与表对齐。
- **理由**：投稿版放"全是 ---"的表等于自己宣布实验没做完；§4:22 列 5 个模型、表里只有 4 行亦自相矛盾。

### T4. RQ3 段落 "We expect ... confirming that ..." —— 假设当结论
- **位置**：`sections/4_experiments.tex:110`（中文 `:111`）
- **现文**：`We expect a similar pattern on \bench: ... confirming that tool-chain grounding depth, not model size, is the binding constraint (RQ3).`
- **改为**：§4(d) 的替换段（`We hypothesise ... this remains an untested hypothesis ... RQ3 is therefore left open`）。
- **理由**：同一句里"期待"与"证实"并存；且 10.0% vs 76.5% 是跨基准比较，不能支撑"model scaling 不够"。

### T5. §5 三档区间全部与 §4 表格不符
- **位置**：`sections/5_analysis.tex:33`、`:35`、`:37`（中文 `:34/:36/:38`）
- **现文**：`14--21\%` / `8--14\%` / `3--5\%`
- **改为**：`18.2--20.8\%` / `8.4--14.3\%` / `2.9--5.1\%`
- **理由**：三档六个端点有五个越界（14 是不属本档的 pg_layout 的 14.3；14.3>14；5.1>5；2.9<3），读一遍 §4 表即可发现——最廉价的攻击点。

### T6. `tab:main-results` 的 `Total` 列混口径（列合计 696，Overall 写 620）
- **位置**：`sections/4_experiments.tex:58`（body `:44-56`）
- **现文**：`\textbf{Overall} & \textbf{62} & \textbf{558} & \textbf{620} & \textbf{10.0}`
- **改为**：加 `ERROR`/`ABSENT` 两列（与附录表统一），Overall 行 `62 & 558 & 70 & 6 & 696 & 10.0`；或最小改动把 Overall 的 Total 改 `696`（caption 已声明 `Pass\% = PASS/(PASS+FAIL)`）。
- **理由**：12/13 行 `PASS+FAIL ≠ Total`、同列合计 696 而合计行写 620 —— 审稿人算的第一道算术题。

### T7. 分母只报 620，从不提 626 / 9.9%（与 runner 官方输出不一致）
- **位置**：`sections/4_experiments.tex:67`（另 `0_abstract.tex:8`、`B_additional_results.tex:11`）
- **现文**：只有 `10.0\% (62/620 decided cases)`，无 CI、无 626/696
- **改为**：在 `\textbf{10.0\%}` 后插入 §2.6 的脚注（三口径 + Wilson CI + ERROR 率）。
- **理由**：runner 自己打印 `62/626 = 9.9%`；读者拿 jsonl 复算得 9.9%，会怀疑论文挑分母。一条脚注即可消除。

### T8. `\Ntasks = 1007` 与 13 域清单合计 964 冲突（且图内写 N=964）
- **位置**：`main.tex:40`、`sections/2_benchmark.tex:65-71`、`:81`、`figures/make_figs.py:48-62,161`
- **现文**：`\newcommand{\Ntasks}{1007}`；四组 `194+220+267+283`（=964）；caption `Domain distribution across \Ntasks{} tasks`；图标题 `N=964 tasks`
- **改为**：补齐 43 个任务的域归属（最好用 jsonl 的 domain 计数）；短期无法补齐则把 §2 四组标为 `964 tasks with a curated domain label`，并让 caption 与图标题一致。
- **理由**：同页图与 caption 写两个不同的 N；附录 `A:53` 的 `A+B+C+D = 1007` 又说明 1007 是对的，等于自认 §2 少列 43 个任务。

### T9. `76%` 与 `76.5%` 全篇不一致（6 处 vs 2 处）
- **位置**：`sections/0_abstract.tex:8`、`sections/1_intro.tex:21`、`sections/4_experiments.tex:110`、`sections/7_conclusion.tex:7`（及对应中文注释行）
- **现文**：`versus 76\% on single-script EDA benchmarks`
- **改为**：统一 `76.5\%`（与 `sections/4_experiments.tex:67` 及 `references.bib` 的 `note={... 76.5\% Pass@1}` 一致）。
- **理由**：同一被引数字在摘要写 76、§4 写 76.5；这会直接影响"差距有多大"的观感，且引用核对必然发现。

### T10. 图注里的无证据因果断言（"not closed by model scaling"）
- **位置**：`sections/5_analysis.tex:44`（中文 `:45`）
- **现文**：`\caption{Pass@1 decreases monotonically with tool-chain grounding depth. The gap is not closed by model scaling, indicating a grounding bottleneck.}`
- **改为**：`\caption{Pass@1 by grounding-depth bin (domains grouped by our annotation; binning is a design choice, not a measured quantity). The ordering is descriptive and does not by itself establish causality.}`
- **理由**：没有 model-scaling 实验，也没有"深度"的测量——分档手工指定，"单调下降"因此是构造出来的（循环论证）。

---

### 备选（T11–T14，时间允许再改）
- **T11** `sections/2_benchmark.tex:11`：`0\% rejection rate` 与"预筛器过滤非设计流会话"自相矛盾 → 改抽样复核口径或删该从句。
- **T12** `0_abstract.tex:4` / `1_intro.tex:13` 的 `268 engineers` vs `2_benchmark.tex:11` 的 `224 unique users` → 统一并说明关系（另 `42 workstations` vs `698 hosts` 需加定语）。
- **T13** `sections/5_analysis.tex:60`：`top 3 = 44\%` / `13\%` 用的是 **696 评测集**计数（实算 44.3% / 12.8%），而 §2 的分布用 964/1007 语料 → 句内注明 `of the 696 evaluated runs`。
- **T14** 编译：补跑 `bibtex main` 修掉 2 条 undefined citation（`rao2026sap`、`sulthanpete2026nyris`，见 `sections/9_reproducibility.tex:7`），编译链补成三遍 pdflatex；顺手修 3 条 >20pt Overfull（§6.3）。

---

## 附：本次审计产出清单

```
doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/
├── AUDIT_triage_refresh.md          <- 本报告
├── ci_wilson.py                     <- Wilson CI / 分箱 / 口径敏感性（stdlib only）
├── ci_wilson.out.txt
├── ledger_scan.py                   <- 数字台账扫描
├── ledger_scan.out.txt
├── table_check.py                   <- 两张表的算术校验（解析 .tex）
├── table_check.out.txt
├── log_check.py                     <- LaTeX log 解析
├── log_check.out.txt                <- 两遍 pdflatex
└── log_check_after_bibtex.out.txt   <- bibtex + 两遍 pdflatex（对照）
```

**未修改任何论文源文件**（无 .tex/.py/.bib/.bbl 改动），未运行任何 git 状态变更命令，未在论文目录产生 .aux/.log/.pdf。所有编译产物位于 `D:\TEMP\audit_lfb_compile`。

