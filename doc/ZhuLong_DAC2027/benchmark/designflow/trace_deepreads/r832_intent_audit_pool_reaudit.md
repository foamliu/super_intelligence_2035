# r832 意图审计 + 候选池重审（2026-11-15 用户令 · 最高优先）

## 背景
A-pure 选料枯竭（r760/r761/r824/r826/r831 多轮终证 + 本轮 fresh cross-ref 再确认：candidates_mc10 A-domain kw 命中 top 全跨域 hspice/virtuoso/netlist → B/C/D，非 A-pure；coverage 422%）。本轮按 2026-11-15 用户令「重审已造的题与候选池」做 intent audit + pool reaudit，是 11-15 令以来 A shard 首次系统执行。

## 一、已造题意图审计（intent_audit_A.tsv，26 题）

审最近 24 题 + 中段 2 题（lines 390-415）。逐题三问：①问的是 trace 用户真实想干的事吗 ②check 是否超出原始意图 ③是否旧配额降级裁剪。

**结果：keep=26 / off_intent=0 / over_constrained=0 / downgraded=0。**

- 全部忠实还原 trace 用户意图，prompt 多用用户原话（A 档 trace-faithful）或合成真实场景（B 档），未发现为凑 L2/L3 配额硬加步骤或为通过率区间改题。
- 关键正向证据：6 题属旧规则会判 weak 的类型，新初衷下正确保留——
  - VwlnDftSignalExplain-001（doc-search/retrieval-Q&A「测试VWLN使用什么DFT」）
  - StaInterruptCauseAnalyze-001 / GenLibCornerEmptyAnalyze-001 / MakeTcUvmFallbackDiagnose-001 / RandAddrOverflowDiagnose-001（debug-Q&A/分析诊断）
  - PprRandomBankExplain-001 / SignalBusNameCheckExplain-001（explain-Q&A 代码理解）
  - SpiceStructAnalyze-001 / RdcViolCatalog-001（doc/extraction）
  - SkillReviewAskEda-001（skill-creator meta-task）
  - 11-15 reaudit「analysis-Q&A/doc-search/debug-Q&A/env-config 全部恢复为可造」在 A shard 题库中已落地。
- 无 over_constrained：check 要求均收敛在用户真实交付物（脚本/报告/补丁/例化），未塞用户没要求的文件结构/实现路径。
- 无 downgraded：未发现旧配额把真实任务裁剪后入库的痕迹。

**数据质量附注**：A.jsonl 415 行中 262 行用 `task_id` 字段、153 行用 `id` 字段（两代 schema 共存），merge 主 jsonl 由 build 脚本归一为 `id`。非缺 id bug，但建议后续统一源 case 用 `id`。

## 二、候选池重审（pool_reaudit_A.tsv，20 题代表性样本 / 191 parked A-pure 全量已扫）

逐项重判旧「不可造」候选。11-15 令：唯一排除标准只剩 (1)无真实 trace (2)写不出 toothy check；其余类型（Q&A/doc-search/explain/env-config）全部恢复为可造。

**结果：旧可造池无新增（0 条被旧规则误杀的 A-pure 候选可复活）。**

191 条 parked A-pure 候选重判分类：
1. **类型理由作废但重判仍不可造**（6 条：t2qp9/2h3mf/78z8d/kvv66/0yyhj/d1cg3-bxnc8）——旧判「Q&A not design_flow」类型理由作废，但重判仍命中排除标准(2)：trace 无 accepted deliverable/gold，single how-to 答案难写 hidden-B toothy self-contained check。
2. **内容原因维持不可造**（绝大多数）：wrong-domain（9knot→C char / rc0jh→analog / d1cg3→spice / 4xt0p→analog）、templated canned 会话无真实意图（zggtc/qvkte）、infra 请求（7bqnr/xgcnn）、meta 询问（ztom2/bxnc8）、duplicate（fbuip/ggmdz）、pruned/missing file（fefaj/vke2w/18ry4/fg7ey/ijm3f）、kw-noise analog（36yj3/g9e41/5hbdw/rser7/5c450/tx5s5）、cross-shard collision（7j1bw→D）、交互太薄无 gold（it6n4）。
3. **附注**：旧 parked 理由中引「§5 L2/L3-only 准入」「analysis-only 判 weak」等旧规则已随 11-15 令作废；但绝大多数 parked 候选同时命中内容性排除标准，故维持 parked 不变。

## 三、结论
- A shard 题库（415 题）经抽样审计无意图违背，旧规则误杀的题已在新初衷下造回（r817-r831 多个 Q&A/explain/doc-search case 落库为证）。
- 候选池无被旧规则误杀可复活的 A-pure 料——枯竭是真实的（A-pure mc≥10/5 池耗尽 + parked 重判无新增），不是旧筛子造成的假象。
- 下一步：(a)继续扫历史存量题（已审 26/415，进度 6.3%）(b)等运维新全量扫描扩池（11-19 扫描仅 12h 前，本日尚可再扫 1 次）(c)phantom-revival bug code-fix。

## 产出
- designflow/intent_audit_A.tsv（26 行）
- designflow/pool_reaudit_A.tsv（20 行代表性样本）
- 本笔记
