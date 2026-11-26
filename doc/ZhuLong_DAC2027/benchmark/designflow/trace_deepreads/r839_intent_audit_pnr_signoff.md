# r839 意图审计 — pnr_signoff 历史存量批（32 case）

**轮次**: r839 (2026-11-20, 0-case 意图审计轮)
**触发**: A-pure 枯竭（r838 第 8 次确认，无新扫描）+ 2026-11-15 最高优先令「意图审计续」+ DEBT(a)「优先 eda_other/pnr_signoff 历史存量」
**审计范围**: A.jsonl 全部 pnr_signoff 域未审计 case = 32 条
**审计前进度**: 120/415 ≈ 28.9% → **审计后 152/415 ≈ 36.6% (+32)**

## 判定分布

| 判定 | 数量 | 说明 |
|:--|--:|:--|
| keep | 32 | 全部忠实溯源真实 trace，分析/审计/修复/produce 意图保留 |
| off_intent | 0 | 未发现凑配额硬加步骤 |
| over_constrained | 0 | 未发现判分超用户原始意图 |
| downgraded | 0 | 未发现用户真实任务被降级/裁剪 |

**结论**：与 r836（batch2 generic-named 40 题 keep）/ r837（40 对 v1-v2，v2 全 keep）一致——旧 L1/L2/L3 配额扭曲是「选题模具」问题（Q&A/analysis/env-config 判 weak 不造），**未扭曲已造题内容**。本批 32 条 pnr_signoff case 均忠实还原用户真实意图。

## 形态分布（观察）

pnr_signoff 域 32 条 case 形态分布：
- **analysis-Q&A / debug-Q&A / 审计类**（11-15 reaudit 后合法）：AprLogAudit, AprSetupAudit, GenLefConsistAudit, InnovusLogAudit, IrResultMissingNetDiagnose, SpefAnnotAudit, SpefLogAnalyze, GenLibCornerEmptyAnalyze, StaInterruptCauseAnalyze, RcmaxTreeCompare, SpfNetCapDiff — 共 ~11 条，纯分析/审计意图，check 校验报告 JSON/JSON
- **produce-task / flow-build 类**：AprStampFix, CalibreOpen1Fix, CdlBodyMapFix, CdlVbnBulkRemap, DRCDeckOpt, DrcSyntaxTest, ETMExtract, FlowGuide, IMPSR1253VddPmFix, LefFilelistGen, OstrichSpefRCFactor, PTStaFlowBuild, PyShebangFix, RedhawkGenInputs, STAFlow, SdcCdcFix, SpfRcSummaryGen, StaStepDriverGen, StarRCDspfFlow, StarRCFlow, UpfIntentExtract — 共 ~21 条，check 校验脚本/tcl 真跑产文件

形态多样，符合 pnr_signoff 域真实用户任务分布（既有写 flow 脚本，也有分析日志/诊断报错）。

## NEAR-DUP 复核（3 对，非 intent 违反，flag cross-case dedup）

通过 session_file/host 核验，3 对 near-dup 确认是**不同 session**（非重复造题），但主题高度重合，建议 cross-case dedup 专门轮复核：

| 对 | user | session A | session B | 主题 | 处置建议 |
|:--|:--|:--|:--|:--|:--|
| CdlBodyMapFix-001 ≈ CdlVbnBulkRemap-001 | johnl | 748ox@hfeg0pfn119 (mc123) | dnkz8@hfeg0plg99 (mc99) | T_IsmTop XI37 buffer bulk vbn→vss/vbp→vcc 重映射 | 同 user 同问题不同机两次跑，flag dedup，倾向保留其一 |
| PTStaFlowBuild-001 ≈ STAFlow-001 | e0046913 | j35ie@hfeg0pkn003 (mc11) | f9heo@hfeg0pkn003 (mc94) | PrimeTime STA flow scaffold (run/+scr/编号tcl) | 同 user 同host 同STA flow 不同session，flag dedup |
| AprLogAudit-001 ≈ IMPSR1253VddPmFix-001 | alan3zh | z5wxj@hfeg0pkn001 (mc2327) | i9chj@hfeg0plg49 (mc401) | Innovus IMPSR-1253 VDD_PM 诊断 | 同 user 同告警不同 host/session，AprLogAudit=B档可复用审计器 vs IMPSR1253VddPmFix=A档定点修复，不同 reframe，flag dedup |

**注**：SpefAnnotAudit-001 (haoyut, w4x70, iejoad 项目) 与 SpefLogAnalyze-001 (haoyut, vo5f5, drgqx 项目) 经核为**不同项目**，非 near-dup，不 flag。

## 用户集群观察（非 intent 违反，flag 覆盖度）

- **e0046913 (QianYuting) CXDP STA flow cluster**：6 条 case（ETMExtract, PTStaFlowBuild, STAFlow, StaStepDriverGen, GenLibCornerEmptyAnalyze, StaInterruptCauseAnalyze）均围绕 CXDP STA flow，各有 distinct 子任务（ETM 抽 db / flow scaffold / driver / gen_lib 报错 / 中断分析）。单 user 集中度高，但每条子任务独立可判分。flag cluster for coverage review（非 dedup）。
- **simplec StarRC cluster**：2 条（SpfRcSummaryGen, StarRCFlow），不同子任务（RC 汇总 CSV vs flow 自动化），独立。

## 6 v1-missing 案（r837 新增 DEBT(g)）本轮未触

本轮审计的 32 条 pnr_signoff case 无 v1/v2 对（均为单一版本），未触 r837 DEBT(g) 的 6 v1-missing 案（PRStartMethodSelect/RdcViolCatalog/RedBistFlowRecon/WtmWriteArrayScope/ToolRcFormatMapQa/PkgVarPassDutTb）。留待专门 git history 核查轮。

## 产物

- `designflow/intent_audit_A.tsv`：120 → 152 行（+32）
- 本深读笔记
- A.jsonl 415 不变 · cases/A 不变 · 台账 A 685 不变

## 纪律

守任务初衷第 1 条（任务形态=用户意图）+ §4.3/§4.6 硬闸门 + shard 纪律（只审计 A 域 case）。本轮无 eda_flow session 操作（纯本机 jsonl 审计）。
