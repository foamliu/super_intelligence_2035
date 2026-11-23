# r1125 (2026-11-24) — 0-case stop-loss 轮 · B-spice fresh 池耗尽确认

## 背景
r1124 已为 0-case stop-loss（6 peek 全 reject）。本轮继续验证池是否真耗尽。

## 选料
- 源池：`designflow/b_fresh_1123_Bonly_538.tsv`（538 条 B-only fresh）
- spice-dominant 过滤（top_kw ∈ hspice/finesim/spectre/siliconsmart/ngspice/spice/custom_sim）→ 34 候选
- 扣台账已 ledgered（1730 sids）→ 30 真 unledgered
- 按 mc 降序取 top3 peek（mc6/mc4/mc3，已是无 mc≥5 之外的残段最高）：
  1. **v0mky** e0035227@hfeg0plg54 mc6 hspice:9 → "电源网络 IR-drop" 12msgs，vague 单句，off-domain（IR-drop 属 PG/电源，非 B spice produce）
  2. **b99hz** e0041392@hfeg0plg77 mc4 hspice:25 → "在askeda上查询一下：Nnospice仿真器的精度有哪些？分别如何配置？" 7msgs，doc-search Q&A，同 r1114 已拒同 user pattern
  3. **danx7** wnyu@hfeg0plg07 mc3 hspice:4 → "hi" / "LPDDR6你有了解吗" 8msgs，general Q&A，无 produce 齿

## 结论
3 peek 全 reject（Q&A / doc-search / vague / off-domain 四类无 produce 齿意图）。

## 止损依据（§6）
- r1114：peek 10 全 reject
- r1124：peek 6 全 reject
- r1125：peek 3 全 reject
- **累计 3 轮 19 peek，0 produce 触达**。高 mc fresh B-spice 池在 r1065–r1125 多轮消耗后残存 fresh 的 produce 密度趋 0。
- r1123 的 6mbnf（mc274 hspice:667 88%）是该段最后一条真 produce trace，与残存 fresh（最高 mc6，spice 占比 < 1.2%）形成断崖。
- 残存 unledgered spice-dom 候选全部 mc≤6 且 spice 关键词密度极低（hspice:2–9），属「扫描噪声边缘」而非真 produce 意图。

## 动作
- 3 候选 claim + park 入台账（防复检）：v0mky / b99hz / danx7
- 台账 1735 → 1738（+3 parked）
- 判定：**扩池无效**，需新 scan 或转 §4.9 自查 / ledger 治理

## 下一步建议
1. 等待新 scan（>mc10 hspice/finesim/spectre dominant 段）注入 fresh 池
2. 或探低 mc（<200）但 high spice-density 段（如 hspice:>500 占比 >50%），用 keyword ratio 而非纯 mc 排序
3. 或转 §4.9 自查：审计已落库 case 的 hidden B anti-hardcode / negative selftest 完整性
