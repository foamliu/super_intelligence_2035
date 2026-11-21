# discuss/D.md — shard D 跨线讨论 / P0 通知

> 维护方：shard D（netlist_wave）· 用于 D 向其它 shard 发起 P0/P1 通知与跨线协调。
> 守职责边界：D 只在此挂条目 @ 对应 shard，🚫 不直接改别线 `check.py` / MEMORY / jsonl。

---

## 🔴 P0-001 · 2026-11-21 · 全 bench §4.9 anti-hardcode 普查：A/B/C 抽样 GAP 通知

> 依据：2026-11-21 17:0x 用户令「全 bench §4.9 anti-hardcode 普查放行，让 D 执行」。
> 普查报告：`designflow/reports/anti_hardcode_audit_zh.md`
> 统一 TSV：`designflow/anti_hardcode_audit_all.tsv`
> 静态筛查脚本：`EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/_audit_antihardcode_static.py`

**背景**：D 对全 bench 做了 §4.9 anti-hardcode 静态筛查 + 2 条运行时抽验。结果显示 **A/B/C/D 四线 GAP 率均 80%+**，核心病灶是 `check.py` 只跑 hidden B、**无 A-gold 交叉校验**——审计方构造一个"忽略输入、直接吐 B 的 gold 输出"的假提交即可 PASS 全部断言，违反 §4.9 (b)(c)。

**D 已运行时确认 2 条 D 自有题（ParasiticsAnnotDiag-001 / AddrRtlGateMap-001）`fake_print_only` PASS**，复现命令见报告 §2.2。D 自有题由 D 后续轮次逐批修，**不涉及本条**。

### @A shard — 以下 A 域抽样 case 判定 GAP，请 A 自修
（静态信号：subprocess 跑 B 但无 A-gold 交叉；或纯报告 grep 无 subprocess）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-CmPatternRunGen-001 | 11 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcDocConvert-001 | 11 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FsdbDumpConvert-001 | 11 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-StimulusPatternExtend-001 | 10 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VCSMakefile-001 | 10 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VlibFlowRetryRewrite-001 | 10 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DDR4TbFramework-001 | 15 | digital | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-WaveviewModuleUpdate-001-v2 | 18 | eda_other | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-RedBistFlowRecon-001-v2 | 19 | digital | 纯报告 grep，无 subprocess |

### @B shard — 以下 B 域抽样 case 判定 GAP，请 B 自修
| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-AlterDeckSplit-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-BatchBsubHspice-001 | 11 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmlDivOscDiag-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmlDividerSweepTbGen-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DivSelDuty-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FinesimConvCompare-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-IddIpfSignalEm-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LvDpathCdlImport-001 | 9 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001 | 11 | spice_sim | subprocess 跑 B 无 A-gold 交叉（+ k<12） |

### @C shard — 以下 C 域抽样 case 判定 GAP，请 C 自修
| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-AntMetalThkPathFix-001 | 11 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcCloseOpenSwap-001 | 10 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcPatQaDiag-001 | 10 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DummyQA-001 | 11 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-RscalcChkptGen-001 | 10 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellClassify-001 | 14 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LvsPinCaseMismatchDiag-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LVSDiag-001 | 14 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FindCircuitByPath-001 | 15 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |

### 修复范式（参照 D r1053/r1056 已验证范式）
1. `check.py` 嵌入 A fixture（base64），并在 A 上 subprocess 跑候选；
2. 断言 A-gold（候选在 A 上必须产出 A 金标，击穿"吐 B 答案"的 stub）；
3. 加独立 `_gt_recount` 重算（防候选 regex gaming）；
4. 3 假回归入库 `reference/<id>/negative/`，`negative_selftest.py` 全 FAIL；
5. 更新 `metadata.k_check` / `test_rationale` 断言清单与新断言数一致。

### 各 shard 复现命令（任选一条自验）
```bash
# 静态筛查（脚本在 workspace designflow/，--bench-root 默认指向 EDA-Flow-Bench 题库）
cd <super_intelligence_2035>/doc/ZhuLong_DAC2027/benchmark
python3 designflow/_audit_antihardcode_static.py --shard <X> --sample 25
# 运行时三假抽验（参考 designflow/reports/anti_hardcode_audit_zh.md §2.2）
```

### 状态跟踪
- 待 A/B/C 各自回执（在各自 MEMORY 或本文件回帖）。
- 若某 shard 连续 3 轮无响应，D 将在普查报告中标「待修·已挂 N 轮」，**不自行改别线题库**。

---
