# 论文刷新记录 · 2026-11-10（基于 696-run 全量评测）

> 触发：DesignFlow 全量评测批次 `run_batch_20261109_171201` 跑完
> （696 例，8 workers，24h10m；`PASS 62 / FAIL 558 / ERROR 70 / ABSENT 6`；`62/626 = 9.9%`）。
> 本文档记录：**改了什么、依据是什么、哪些还没做、为什么**。

## 1. 改了什么（文件 → 变更）

| 文件 | 变更 |
|---|---|
| `main.tex` | `\Ntasks` 1007→**1026**（A200+B240+C289+D297，出处见各 shard MEMORY）；新增 `\Neval{696}`，并注明「结果句只用 \Neval」 |
| `sections/0_abstract.tex` | 去 "best frontier model"；改「单一骨干 + 冻结 696-run 快照 + 62/620」；76%→**76.5%**；7×→**7.1×**（并注明 CI 重叠） |
| `sections/1_intro.tex` | 同上；删掉「scaling 53%→76% 未弥合差距」的跨基准推断，改为**假设**表述；贡献项补 trace anatomy |
| `sections/2_benchmark.tex` | 四组不再写死任务数（会立刻过期）；明确「活基准 1026 / 评测快照 696」双口径；图 1 题注改为 696-run 分布 |
| `sections/4_experiments.tex` | 表 2 增 `ERROR`/`ABSENT` 两列（13 行全对齐 696）；Overall 行 62/558/70/6/696/10.0；加**口径脚注**（620/626/696 + Wilson CI）；删空壳多模型表；RQ3 改为**开放问题**；领域差距段加 CI 与「排序稳健、比值不稳健」 |
| `sections/5_analysis.tex` | 失败分类法：删 `~45/40/15`（无数据支撑），改为**可核验的协议 + run 级锚点**；深度分箱改为与图 3 完全一致（19.4/14.3/11.3/9.3/5.1/2.9）；图 3 题注去掉因果断言；**新增 §5.3 Trace Anatomy 试点研究**（47 份真实 trace 实测）；威胁一节补 3 条（单骨干/冻结快照/轨迹样本偏差） |
| `sections/7_conclusion.tex` | 76%→76.5%；加 62/620 与快照口径；因果断言降级为「排序稳定」 |
| `appendix/A_benchmark_details.tex` | 分片计数改 200/240/289/297=1026；保留 T12 的 TODO 注释（268 工程师 / 42 工作站 / 698 主机 / 224 用户三处口径未统一，**未擅自改数字**） |
| `appendix/B_additional_results.tex` | 逐域表说明对齐；删除全是 `---` 的 per-model 表，改文字说明；失败分类法 TODO 改为协议 + 工具指向；token/成本由「TODO」改为**实测行为学数据**（30 份 aggregate：中位 0.71M in / 55.6k out） |
| `figures/make_figs.py` | 饼图数据源改为**评测快照 696**（与表 2 Total 列同源）；深度曲线改**精确均值**；无 SVG 转换器时优雅跳过而不是报错；hostname 匿名化（见下） |
| `appendix/C_experimental_details.tex` | `agi-gateway.cxmt.com` → `agi-gateway.internal`（**双盲**：原文泄露公司域名），verbatim 降字号消除 45.9pt 溢出 |
| `figures/domain_pie.pdf` / `grounding_depth.pdf` | 重新生成并逐图目视核对 |

## 2. 为什么这么改（证据链）

- 一律以 **批次输出** 为准：62/558/70/6=696，`62/620=10.0%`（已判定）、`62/626=9.9%`、`62/696=8.9%`。
- 逐域数字全部可回溯到 `tab:full-domain-results`：13 行 `PASS+FAIL+ERROR+ABSENT == Total`，
  列合计 62/558/70/6/696，`Pass%=100*PASS/(PASS+FAIL)` 四舍五入到 0.1 —— 已由
  `table_check.py` 直接解析 .tex 复核（见 `table_check.out.txt`）。
- Wilson CI / 三种分母敏感性：`ci_wilson.py` → `ci_wilson.out.txt`。
- 论文侧不一致之处来自 `AUDIT_triage_refresh.md`（TOP-10，逐条 file:line）。
- 新增 §5.3 的每个数字来自 `local48_metrics.json`（`trace_anatomy.py` 实测，含交叉校验：
  `n_tool_calls` 两条独立计数路径 1371 vs 1371，diff=0）。

## 3. 明确没做的（以及原因）

1. **558 个 FAIL 的逐 run 归因没有写进论文**。原因：新批次的 trace 在集群
   `/nasdata/.../run_batch_20261109_171201`，**本机无法访问**（10.239.x / 10.129.x TCP 全 timeout），
   本地只有 11-03~11-06 的 48 份旧 trace，且**不含 judge verdict**（无法由此推出 PASS/FAIL）。
   ⇒ 论文只写「run 级锚点 + 协议」，把逐类占比留给 camera-ready；工具已就绪（见下）。
2. **多骨干对比未填**。只有 DeepSeek-V4-Pro 有数；其余 4 个骨干每跑一遍 696-run ≈ 24h×1 批，
   合计约 5 个机器日。
3. **用户/主机口径未统一**（268 工程师 / 42 工作站 vs 698 主机 / 224 去重用户）。
   这是数据侧事实问题，不是排版问题，**需要确认后再改**，已在 A.4 留 TODO。
4. `main.bbl` 未提交（`.gitignore` 忽略 `*.bbl`）；投稿前需本地跑
   `pdflatex → bibtex → pdflatex → pdflatex`（缺 bibtex 时会报 2 条 undefined citation）。

## 4. 剩下的一步（在集群上跑，约 2 分钟～数分钟）

```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage

# 1) 先探查批次目录结构（不写任何文件）
python3 05_batch_triage.py \
  --batch /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/run_batch_20261109_171201 \
  --cases /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl \
  --out results --dry-run

# 2) 正式跑（产出 triage_summary.json + tables/*.tex + report.md）
python3 05_batch_triage.py --batch <同上> --cases <同上> --out results --emit-tex

# 3) 把 results/ 提交回仓库（只提交聚合结果，不要提交原始 trace）
git add results && git commit -m "eval_triage: 696-run failure attribution" && git push
```

> 若 step 1 的 `--dry-run` 显示「0 命中判分证据」，说明批次目录结构与启发式不符：
> 先 `find <RUN_DIR> -maxdepth 2 | head -50` 看清布局，再按
> `TRACE_TRIAGE_RUNBOOK.md` 的排查表加参数。
