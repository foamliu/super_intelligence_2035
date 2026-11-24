# r1132 (2026-11-24) — 0-case 治理轮 · 跨 shard §4.9 negative_selftest 完整性审计

## 背景
r1131 stop-loss 第 4 轮确认 b_fresh_r1126_xshard_dedup.tsv 的 spice≥5 段（43 候选）系统性 peek 完，低 spice-ratio 段 produce 密度趋 0。r1131 下一步建议 #3 = §4.9 跨 shard 审计（A/C/D negative_selftest.py 完整性，r1126 已确认 B 100%）。本轮执行该建议。

## 前置确认
1. **新 scan 检查**：eda_flow open_session(hfhds201) → `ls /home/t0002965/log/ssh_eda_search_* | tail` → 最新仍 `20261124_023802`（r1131 同源），无新 scan 到达。fresh B-spice 池耗尽条件延续。
2. **stop-loss 条件复核**：mc≥5 连 4 轮 0 case（r1124/r1125/r1126/r1131），每轮真 peek ≥10 本域 fresh，符合「扩池无效 → 转 §4.9 自查 / ledger 治理」闸门。残存 5 候选为 spice<5 或 mc≤2 极低密度噪声，低于 mc≥5 生产力门槛，不需 peek。

## 本轮工作：跨 shard §4.9 negative_selftest.py 完整性审计

### 方法
对每个 shard 的 cases/<shard>/*.json 提取 case_id，检查 `reference/<case_id>/negative/negative_selftest.py` 或 `reference/<case_id>/negative_selftest.py` 是否存在。

### 结果

| shard | cases 总数 | 有 refdir+selftest | **缺 selftest（§4.9 gap）** | 无 refdir（inline-test 类） |
|:--:|--:|--:|--:|--:|
| A | 565 | 457 | **13** | 95 |
| B | 562 | 501 | **0** ✓ | 61 |
| C | 615 | 489 | **9** | 117 |
| D | 647 | 479 | **5** | 163 |
| **合计** | 2389 | 2016 | **27** | 436 |

- **B §4.9 = 100%**（0 gap），reconfirm r1126 结论。
- **A/C/D 共 27 个 §4.9 gap**（含 1 个 `__pycache__` 非 case，实际 26 个真 gap）。

### 26 个真 §4.9 gap 清单（供各 shard agent 修复）

**Shard A（13）**：
AgentCodeStructAnalyze-001 · CPU8bitVerilog-001 · DDR4TbFramework-001 · DrcSyntaxTest-001 · GgFlowReport-001 · IrunIllegalLogParser-001 · LPDDR6CACodecProduce-001 · PwrSeqRecoveryProduce-001 · RandcaseWeightZeroTrfcQA-001 · RhrRefreshTimingQA-001 · VltRetryWave2-001 · WlMonitorLogicViewAnalyze-001 · XsCheckReportDiag-001

**Shard C（9）**：
CalibreLvsRulePtnFix-001 · CdlPortStats-001 · DrcDeckOptimize-001 · InnovusFpLogDiag-001 · PwrViaAgentGen-001 · RscalcLabel-001 · SASchematicAether-001 · SvrfPvrsRuleTranslate-001 · EncloseSide1PatternGen-001

**Shard D（5）**：
NetlistSvRulesReorg-001 · NetlistVdomPrefixCount-001 · VerdictJoinPassPassLib-001 · TotemLayermapFatalDiag-001（+ __pycache__ 非 case 已剔除）

### 抽检确认（3 个 gap 真实性）
- `LPDDR6CACodecProduce-001`(A)：有 check.py(9849B) + __pycache__，无 negative/ dir → 真 gap
- `CalibreLvsRulePtnFix-001`(C)：有 check.py(11470B) + solution.py(11498B)，无 negative/ dir → 真 gap
- `NetlistSvRulesReorg-001`(D)：有 check.py(20744B) + __pycache__，无 negative/ dir → 真 gap

三例均「有 check.py 但无 negative_selftest.py + 无 negative/ 错解」，符合 §4.9 gap 定义（缺负样本入库 + 缺自检 harness）。

### "无 refdir" 类（436 个，未深查）
这些 case 的 `test` 字段内联在 JSON 里（如 B 的 AcSimHowtoGuide-001，test len=9044 str），reference/ 无对应目录。可能是 inline-check 或 guide/Q&A 类 case，negative 样本可能内联或缺失。属另一调查线，本轮不展开（超预算）。

## 台账动作
- 本轮 0 claim / 0 mark（无新 case、无新 parked）
- 台账 B 维持 1758（case 592 · parked 1166）
- eda_flow session `default_designflow-b_shardB-r1132_0` 已 close

## 指标
- 📊 trace 覆盖率: covered=592/target=4529=13.1%(mc>=10, 不变，无新 case)
- 🎯 通过率: 最近20条 20/20=100%(观察值, 不变)
- 📦 MEMORY_B <32KB ✓
- DEBT: 0

## 结论与下一步
1. **B §4.9 selftest 100% reconfirm**（r1126 结论延续有效）。
2. **跨 shard §4.9 gap = 26 个真 gap**（A:13 C:9 D:5），已落本笔记供各 shard agent 在其治理轮修复。这些 gap 违反 §4.4「负样本入库」+ §4.9 自检 harness 要求，应限期补齐 negative/ + negative_selftest.py + ≥2 错解。
3. **无新 scan**，fresh B-spice 池耗尽条件延续。维持 stop-loss 状态。
4. 下一步选项：① 等新 scan 注入高 mc spice-dominant 段；② 527j4 专项 build 轮（需 scp 80MB DSPF + 前序 session，预估 2-3 轮）；③ 协调 A/C/D agent 修复 26 个 §4.9 gap；④ 深查 436 个"无 refdir"inline-test 类 case 的 negative 完整性。
