# r841 — intent audit: verification 历史存量批 (99 case)

> 2026-11-15 最高优先令「重审已造的题与候选池」续做。本批审 verification 域剩余 99 条 standalone case（不含 r837 已审的 14 v1/v2 对）。

## 范围

- A.jsonl verification 域 130 case，r837 已审 31（含 14 v2 + 14 v1 + 3 standalone），本批审剩余 99 standalone。
- 全部为非 v2 case：无 -v2/-v3 后缀，无 v1/v2 对照对 → downgraded 判定不适用（downgraded 仅针对旧配额 v1 被 v2 reframe 替代的情形）。

## 方法

逐条比对 `metadata.trace_source.real_task_summary`（用户真实意图）vs `prompt`（case 任务说明）vs `metadata.test_rationale`（判分断言清单），按三个审计问题判定：

1. case 问的是 trace 里用户真实想干的事吗？→ 全部 yes（produce-task case 用户原话明确要求写/改/生成；analysis-Q&A case 用户原话明确要求分析/解读；debug-Q&A case 用户原话明确要求诊断失败；doc-search case 用户原话明确要求查文档）。
2. check() 判分要求是否超出用户原始意图？→ 全部 no（check 校验用户真实想要的产物/知识结构；§5 reframe 的 analysis/debug-Q&A→script 是 headless 不可复现时的合法 reframe，校验用户真实想要的分析结论结构，非超意图加难）。
3. 是否因旧配额降级/裁剪后入库？→ 全部 no（本批无 v2 对，无旧配额 v1 可下线）。

## 形态分布（99 case）

| 形态 | 数量 | 说明 |
|:--|--:|:--|
| debug-Q&A→produce-task(reframe) | 48 | 用户原话诊断仿真失败/报错，原 trace 不可 headless 复现 → §5 reframe 为可判分诊断/修复脚本 |
| produce-task | 23 | 用户原话明确要求写/改/生成 testbench/pattern/makefile/script |
| analysis-Q&A→produce-task(reframe) | 21 | 用户原话分析/解读/审查，原 trace 不可 headless 复现 → §5 reframe 为可判分分析脚本 |
| flow-driving/flow-build | 4 | 用户原话搭建验证 flow（DFT TestMAX / Formality r2r / VPS regr） |
| debug-Q&A | 2 | 用户原话诊断，交付诊断报告（不 reframe 为脚本） |
| analysis-Q&A | 1 | 用户原话分析，交付分析报告 |

## 样本深核（12 例，逐条核对 real_task_summary vs prompt vs check）

| case_id | user | 形态 | 判定 | 核验 |
|:--|:--|:--|:--|:--|
| DejoaWrrdSeqAnalyze-001 | chuanqiz | analysis-Q&A→script | keep | U#0「分析这个目录下各个文件的作用」+U#18「分析下wrrd_sequence这个用例是如何实现的」→ case prompt 用原话, check 校验 wrrd_sequence 实现分析结论 |
| DqselDefineMismatchQA-001 | tongfanl | debug-Q&A | keep | U#64「分析下DQSELH和DQSEL_LH两个define的关系」→ case prompt 用原话, check 校验 define 关系诊断结论(r823 已造 case) |
| EDA-Eval-DesignFlow-CdlVerilogConv-001 | dsgao | produce-task | keep | 「把这个网表用 verilog 等价描述出来，然后验证」→ case 要求 CDL→verilog 转换+vcs+Formality LEC, check 校验产物 |
| EDA-Eval-DesignFlow-CmpTaskZeroDelayOscDiagnose-001 | xy1zhang | debug-Q&A→script | keep | xrun *W,TRZDGOC 诊断「755和791行内容相同会导致什么后果」→ case 诊断 0 延时震荡根因, check 校验诊断结论 |
| EDA-Eval-DesignFlow-CrStateDesyncFix-001 | shanliny | produce-task | keep | build_rand mismatch 诊断修复 → case 诊断 CR 状态不同步根因, check 校验修复 |
| EDA-Eval-DesignFlow-Ddr6WtmTbComplete-001 | tongfanl | produce-task | keep | 「帮我完善下WTM005_function_combine.v，完善其中的命令」→ case 补全 13 条 DDR6 命令, check 校验 testbench |
| EDA-Eval-DesignFlow-DeadLoopScan-001 | xingx | debug-Q&A | keep | 「check if there is any dead loop in global_dldo_bind.sv」→ case 只读检查死循环, check 校验死循环识别结论 |
| EDA-Eval-DesignFlow-FmRtl2RtlFlow-001 | e0046913 | flow-build | keep | 「参考feint的formality脚本，开发rtl2rtl功能」→ case 开发 fm_r2r flow, check 校验 flow 产物 |
| EDA-Eval-DesignFlow-FsdbVerdiInteg-001 | lorikx | produce-task | keep | 「修改testbench和makefile，生成fsdb并用verdi查看」→ case 改 VCD→FSDB, check 校验产物 |
| EDA-Eval-DesignFlow-IrunLogPrintRank-001 | lein | analysis-Q&A→script | keep | 「分析这个日志文件 都有哪些打印 按打印量最多依次列出」→ B档 synthesized(15GB log 不可 headless), check 校验打印分类排序脚本 |
| EDA-Eval-DesignFlow-Lpddr5CovTermitFix-001 | t0002470 | produce-task | keep | legal_0cycle 覆盖率收敛「修复 directed_coverage_patterns.v」→ case 修复 .termit, check 校验修复 |
| EDA-Eval-DesignFlow-VcsEquiv-001 | johnl | produce-task | keep | 「用 VCS 验证 RTL 与门级网表功能一致」→ case 搭 RTL vs gate 等价性验证, check 校验产物 |

12 例全 keep，check 字段直接映射用户原话无加难。

## 结论

- 判定：keep=99 / off_intent=0 / over_constrained=0 / downgraded=0。
- verification 域 130/130 审完 ✅。
- 与 r836/r837/r839/r840 一致：旧配额扭曲是「选题模具」问题（v1 强制 produce-task），非「已造题内容」问题；本批 standalone case 已按 11-15 reaudit 后口径入库，全部忠实用户意图。
- 唯一保留的排除标准（无真实 trace / 写不出有牙 check）本批无触发。

## 审计进度

- 累计：324/415 = 78.0%（含本批 +99 keep）
- 剩余：119（全在 digital 域，A 核域）
- 下轮：digital 历史存量批（审完即 415/415 = 100%）
