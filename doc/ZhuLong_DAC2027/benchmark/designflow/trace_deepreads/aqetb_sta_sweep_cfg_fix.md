# Deepread: 1794807450388_aqetb (e0046913 @ hfeg0pkn004, mc85, pnr_signoff/STA)

**r768 选料 · claim aqetb (r761 parked ALIVE 最高 mc 剩余) + 造题 1 case**

## 选料背景

r767 治理轮 re-mark r761 parked 8 条 ALIVE 候选 note → "ALIVE, 优先 claim+造题"，
其中 aqetb mc85 是**最高 mc 剩余 ALIVE A-pure**（uyvi5 mc164/r766、0arn6 mc20/r765 已 case）。
本轮兑现 r767 下轮建议(a) — claim aqetb 深读 + 造题。

## trace 概况

- session: `1794807450388_aqetb` @ hfeg0pkn004 (10.129.2.13), 用户 e0046913
- size: 845KB / 184 msgs
- 命中: netlist/pt_shell/primetime/synthesis 强 A-pure pnr_signoff/STA
- liveness: r765 目录感知复查 ALIVE（r760/r761 NOFILE 误判 SUPERSEDED）

## 深读结论 — turn-12 选定

session 含多轮对话。turn-1 用户问如何跑 cla_top 所有 corner STA，agent 解释 `make sta_sweep`
两坑（坑1: sweep 只传 CORNER 不传 LIB_CORNER → 5 corner 共用同一 lib；坑2: `make sta` recipe
`rm -rf sta_*` + 共用 output tag → 后跑 corner 覆盖前跑）与 `corner:LIBCORNER:OUTPUT_TAG` 三元组正确做法。
**turn-12** 用户发「按照以上描述，帮我直接修改脚本」→ 单轮 produce-task/脚本修改意图明确。

## 与 uyvi5(r766) / 0arn6(r765) 的区分

| case | round | trace | 意图 | 交付 |
|---|---|---|---|---|
| StaInterruptCauseAnalyze-001 | r765 | 0arn6 mc20 | debug-Q&A 诊断 run 中断 | 中文 markdown 诊断报告 |
| StaRunEval-001 | r766 | uyvi5 mc164 | analysis-Q&A 评估已跑 STA 结果 | 中文 markdown 评估报告 |
| **StaSweepCfgFix-001** | **r768** | **aqetb mc85** | **produce-task 修改脚本** | **Makefile + CXDP_STA_CFG** |

三者意图/根因/交付形态均不同，无重复。

## 产出 case

- id: `EDA-Eval-DesignFlow-StaSweepCfgFix-001`
- domain: pnr_signoff / mode: design_flow / entry_point: outputs/submit.zip
- k_check = k_rationale = 15
- A assets: run/Makefile (trimmed 保留 sta_sweep/dirs/defaults/sta/common/delete_old_data/run_pt 结构) + run/CXDP_STA_CFG (原 2-corner) + run/CFG_VARS (project lib-corner mapping) + README.md
- B hidden: hidden/CXDP_STA_CFG_B (3-corner v2.0_* tags, judge-only)
- check.py 双层判分: ① mock-exec SUT sta_sweep (stub `sta` echo per-iter CORNER/LIB_CORNER/TAG, 无需 PrimeTime) → 解析 5 次迭代三变量; ② B specificity oracle: SUT 解 hidden B CFG 须得 3 corner 而非 A 的 2 + tag v2.0_ 前缀; ③ shuffle 随机化 corner 顺序测不变性
- 15 断言: ①zip 含两文件 ②sta_sweep recipe 存在 ③传三变量 ④解析三元组 ⑤三元组格式 ⑥5 corners 匹配 ⑦mock 跑 5 次 ⑧正确 lib 配对 ⑨唯一 tag ⑩v1.0_<LIB> 约定 ⑪B anti-hardcoding ⑫无 B 签名 ⑬shuffle-invariant ⑭sta/common 保留 ⑮non-stub 行数
- negatives (5): neg1_noop→② / neg2_print_expected→③ / neg3_core_deleted→② / neg4_old_unchanged→③ / neg5_hardcode_b→⑨
- 自验: ref PASS 15/15 + 5 neg 全 FAIL

## 收尾

- A.jsonl 388→389 (local gitignored index)
- ledger aqetb: parked → case (EDA-Eval-DesignFlow-StaSweepCfgFix-001)
- EDA-Flow-Bench assets/reference: 已 bench-shard sweep 入库 (commit 11747a587)
- super_intelligence_2035: MEMORY_A r768 + trace_ledger_A.tsv commit 1559f162a (push origin main)
- eda_flow session closed (workdir cleaned)
- trace 覆盖率 368→369/4012 = 9.2%

## 下轮建议

余 7 ALIVE 候选待续 claim 造题: i7d8w mc143 / 8akpt mc66 / najzl mc44 / ejpf0 mc48 / c8v5k mc54 / twfqn mc39(digital) / u5wma mc46(digital)。
次高 mc = i7d8w mc143，A-pure 池仍远未枯竭，mc≥5 止损未触发。
