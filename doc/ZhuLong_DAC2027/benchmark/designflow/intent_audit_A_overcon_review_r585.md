# intent_audit_A — over_constrained 逐读复审 (r585, 2026-11-15)

> 承 r584: 「over_constrained 本轮未确认(需逐读 check.py, 留下一批)」。本文件 = r585 完成该批次复审的证据。
> 口径: r584 strict-口径 (任务形态=用户意图)。

## 一、over_constrained 复审结论

**over_constrained = 0**（313 题全审）。

复审方法: 对 300 keep 题逐题比对 `user_intent_from_trace`(tsv col2) vs `test_rationale`(jsonl, check 断言清单) vs `prompt`(用户原话)。判定 check 是否**超出**用户原始意图（要求特定文件结构/实现路径/命名，超乎用户所求）。

发现: check 中的结构化断言（zip 必需文件 / py_compile / subprocess 真跑 / report.json 顶层键 / 跨输入守护）分两类，**均不构成 over_constrained**:
1. **用户明示的结构要求**（如 EmXlsModel 用户原话"每个 sheet 名作为类名…驼峰命名"→ check 断言 5 容器类+5 Row 类+驼峰）= 忠实，非超意。
2. **benchmark 牙齿要求**（§4.2 subprocess 在 B 上真跑 / §4 hidden-B 跨输入守护 / 反硬编）= 评测质量门禁，非对用户意图的扩张。

故 over_constrained 维持 0。

## 二、重大发现: off_intent 被 r584 低估（strict-口径复审 keep 集的副产品）

r584 仅 strict-复审了「最近 50 题」，对 300 keep 沿用 r555-r559 的**过渡口径**（允许 analysis→script 判 keep）。r584 MEMORY 已明示「r555-r559 旧审 294/294 keep 采用此过渡口径, r584 严格口径取代之」——但**取代工作未覆盖 keep 集全量**。

r585 对 300 keep 做 strict-口径复审（用户原话 vs case 交付形态），发现 **15 条 clear off_intent** 被过渡口径误判 keep（同 r584 的 13 off_intent 完全同型: Q&A/分析/解释/诊断/概念 trace 被合成成 Python 脚本+JSON 代码生成任务）。

### 15 条 clear off_intent（已 reclassify keep→off_intent in intent_audit_A.tsv）

trace 用户意图 = 纯 Q&A/分析/解释/诊断/概念（用户原话无"写脚本/生成工具"请求），case 却要求交付 .py 脚本 + report.json:

| case_id | trace 用户意图 (Q&A/分析类) | case 交付 (代码生成) |
|---|---|---|
| EDA-Eval-DesignFlow-LibPVT-001 | 列出表格…哪些 PVT | pvt_parse.py + JSON |
| EDA-Eval-DesignFlow-PTVersionRecon-001 | 分析目录区别…选哪个版本 | pt_version_recon.py |
| EDA-Eval-DesignFlow-FloorplanTclAudit-001 | 解释一下这个脚本 | audit_pre_floorplan.py |
| EDA-Eval-DesignFlow-IrunSimDiagnose-001 | 分析出错的原因 | 诊断脚本 |
| EDA-Eval-DesignFlow-DcSynthAnalyze-001 | 分析 cla_top 综合情况 | analyze_syn.py + JSON |
| RedBistFlowRecon-001 | 看下 redbist 测试流程…怎么产生期望值 | 重构脚本 |
| EDA-Eval-DesignFlow-DcLogErrDiagnose-001 | 请问如何解决 dc.log 报错 | 诊断脚本 |
| EDA-Eval-DesignFlow-DcUpfPgDiagnose-001 | 分析 log 报错原因及方案 | 诊断脚本 |
| EDA-Eval-DesignFlow-SocProjStructAnalyze-001 | 分析项目…介绍…分为哪些 | 结构分析脚本 |
| EDA-Eval-DesignFlow-AsyncResetSyncRelease-001 | 异步复位同步释放电路是什么样的 | reset_sync_model.py |
| EDA-Eval-DesignFlow-WaveviewModuleUpdate-001 | 怎么更新到最新版 | update_waveview.py |
| EDA-Eval-DesignFlow-SacapSignalMissingDiagnose-001 | 为什么没有识别信号 | 诊断脚本 |
| EDA-Eval-DesignFlow-CdlNetlistAnalyze-001 | 分析一下这个网表 | analyze_netlist.py |
| EDA-Eval-DesignFlow-SramFarCellSelect-001 | 为我分析…应选取哪个 cell | analyze_farthest_cell.py |
| EDA-Eval-DesignFlow-RtlBistInventory-001 | 分析/讲解结构及功能/不要修改 | analyze_rtl.py + JSON |

### 7 条 borderline（暂 keep, 已在 tsv 标 review_pending, 下轮逐读 check.py+prompt 复审）

trace 有 retrieval/process 倾向（"把路径找出来"/"找到数据差别"/"找出没被调用"），介于"给答案"与"产工具"之间，需逐读 case prompt 是否忠实保留用户原话还是 B-synth 改写成 produce-task:

- EDA-Eval-DesignFlow-SramPipelineMisalignDiag-001 (诊断, B-synth 改写"写一个工具")
- EDA-Eval-DesignFlow-RcmaxTreeCompare-001 ("找到数据差别")
- SimRunDepExtract-001 ("把路径都找出来")
- EDA-Eval-DesignFlow-SignalXrefBuilder-001 (信号交叉引用, prompt 显式写脚本)
- EDA-Eval-DesignFlow-SignalRunXref-001 (信号→.run 交叉引用, prompt 显式写脚本)
- EDA-Eval-DesignFlow-FuseUncalledAudit-001 ("找出…没被调用")
- EDA-Eval-DesignFlow-FsdbTogglePatch-001 ("需要怎么修改", Q&A vs 改造)

### 复审后判为 keep 的 (legitimate produce-task, 用户明示要产物)

- EmXlsModel-001 (用户原话"封装出读取文件的类…驼峰")
- SimSpeedupMonitor-001 (用户原话"写一个 Python 脚本 optimize_monitor.py")
- VcdToFsdbMigration-001 (用户原话"请修改 testbench 和 makefile")
- SpfCouplingParser-001 (用户原话"转化为排版规律的 csv 文件")
- SweepMeasFix-001 (flow-driving, "利用这两个脚本完成数据收集")

## 三、统计变更

| 维度 | r584 | r585 |
|---|---|---|
| keep | 300 | 285 |
| off_intent | 13 | 28 (13 + 15 新增) |
| over_constrained | 0 (未审) | 0 (全审确认) |
| downgraded | 1 | 1 |
| borderline 待复审 | — | 7 |

## 四、处置

- 15 新 off_intent: 同 r584 处置 — **重做(v2)**, 不删旧 case (jsonl 行保留作旧规则证据), 不下线; v2 还原为原始 Q&A/分析任务形态, check() 刭结构化答案/报告。
- off_intent 累计 28 条 v2 重做队列（r584 13 + r585 15），分多轮做。
- 7 borderline: 下轮逐读 check.py + prompt 复审定夺。

## 五、方法与被排除项

- 24 候选由启发式预筛 (analysis-verb in intent AND no write-verb in prompt AND code-deliverable in rationale) 产出, 逐条人工读 prompt[:600] + rationale + intent col 定夺。
- 272/300 keep 题在 A.jsonl 有 test_rationale (28 题在 audit 但不在 A.jsonl, 多为合并主 jsonl / retired / 跨 shard 误入, 未审, 留下批)。
- "从未审"(no-trace) 与 "no-verifiable-goal" 候选不在本轮 scope (属候选池重审 pool_reaudit, r584 已 DONE)。
