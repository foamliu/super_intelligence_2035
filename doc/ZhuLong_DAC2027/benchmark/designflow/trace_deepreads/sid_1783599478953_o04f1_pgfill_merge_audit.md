# Deepread: sid_1783599478953_o04f1 — Virtuoso power-fill merge audit

- **trace**: `1783599478953_o04f1` (user e0014566 @ hfeg0pkn005, mc=182, 247 msgs, 551KB)
- **domain**: layout_virtuoso (power-fill merge audit)
- **shard**: C  ·  **level**: L1-boundary (live Virtuoso blocked in .75 → pure-stdlib Python replica)
- **case_id**: `EDA-Eval-DesignFlow-PgFillMergeAudit-001`

## 真实用户意图（3 轮原话）
1. 「请你检查下原始的输入layout... 输出的power fill cell... 另外我给你一个参考是我手动调入 power fill cell 到原layout 中的：test_20260708」
2. 「这个test_20260709就是我手动复制了一份 test_20260528， 然后手动将 power fill cell 加了进去」
3. 「先重新跑一遍流程，看看你生成的merge 后的layout, 是不是与我手动操作的一致。」

→ A-档 faithful：核对 auto-merge layout vs 手动 reference layout 是否一致。

## 真实数据（SKILL tool_results, idx 17/19/21/25/27/29/31/33/35/37/55/67/75/242/244）
- original BBox `((-0.33475 -96.525) (144.375 5.175))`；pgfill BBox `((0.0 -86.95) (144.375 5.175))`
- original 241 shapes (119 unique)：M1:63 / M2:44 / M3:58 / M4:34 / M5:42
- pgfill 47 shapes：M1:11 / M2:10 / M3:14 / M4:8 / M5:4
- merged/ref 各 120 shapes (119 unique) + 1 个 M5 残留重复 shape
- ref instance：`austin_new/test_20260528_auto_pgfill` @ origin nil, R0, transform `((0.0 0.0) "R0" 1.0)`
- 只有 2 个 M1 shape 带 net `VSS!`
- M5 真新增 fill 3 个；M5 残留 dup `(-0.33475 -39.075) (1.28475 -38.575)`
- idx 242 确认 **PERFECT MATCH**：auto merged == manual ref，120 shapes，全层 M&R 一致

## 合成方案（L1-boundary 纯 stdlib）
- `pgfill_merge_audit.py`：读 layouts JSON，比 merged vs reference：bbox / instance / 每层 unique-bbox 集合（merged_only/ref_only/common）/ 每层 dup 计数 / M5 新增 fill（merged M5 unique − original M5 unique）/ net 注释（layer,bbox,net 多重集）/ coverage_gaps / verdict(PERFECT_MATCH|MISMATCH)
- 三个规格：A(visible, PERFECT_MATCH) · B(hidden, MISMATCH：M5 merged_only=1/ref_only=1 + dups_merged M5=1/dups_ref=0 + net 错位) · B2(cross-input guard, PERFECT_MATCH, M4 dup)
- check.py：15 条独立断言 a–o，clean-room oracle 独立重算期望报告；subprocess 真跑 B；3-seed 确定性 + 无泄漏；B2 跨输入守卫
- k_rationale = k_check = 15 ≥ 8

## 自验
- 参考解跑 check() → PASS（HERE/hidden 与 workdir/hidden 两条解析路径均 PASS）
- §4.9 三假（empty / print-expected / core-deleted）全 FAIL
- negative_selftest NEG_RC=0（5 个负样本全 FAIL）
