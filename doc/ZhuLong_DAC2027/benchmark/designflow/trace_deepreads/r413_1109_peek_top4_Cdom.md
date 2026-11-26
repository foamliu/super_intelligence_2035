# r413 peek — 11/09 scan top fresh-against-all-4 C-domain-dominant 候选 4 peek 全 REJECT

**日期**: 2026-11-12 (r413, shard C 维护轮)
**扫描源**: /home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv (11/09 scan, 12801 mc≥10 fresh-after-C-ledger, 547 distinct C-domain-dominant fresh-against-all-4)
**方法**: candidates mc≥10 + C-keyword filter + exclude all-4-shard ledger (2620 sids) + C-domain-dominant (C-kw ≥50% of kw hits AND C-kw count ≥20) → 按 mc 降序取 top 4 fresh-against-all-4 peek

## mc-matrix（11/05 快照，shard A 尚未换池 → 11/09；user令 rule 4 凭据）

```
python3 trace_ledger.py --shard C mc-matrix --src summary_1105.tsv
# 数据行 = 5822 → 去重 session = 2163（shard C keywords 过滤后）
# 台账已动过 session = 2796（case/seeded=660, parked=1859）
mc>=10  池总量 1699  已动过 1432  未动过(可做) 267   ← mc10.fresh=267 ≠ 0（不写池耗尽）
```

## 4 候选 peek 结果

| # | sid | user | host | kw | mc | REJECT 原因 |
|---|---|---|---|---|---|---|
| 1 | 1789003454557_ot5fh | miccao | hfhds201 | drc:785;calibre:45 | 144 | **near-dup** — skill `/calibre-drc-log-analysis` 跑 DDR5TOP_DFM0909/rundrc.log 拆解；与 4 existing case 同 archetype：DrcLogTeardownReport-001 / DrcLogAnalyzer-001 / DRCLogTeardown-001 / DrcLogHugeCellOverlap-001（同 skill，同 log-teardown 输出形态）。USER#0=slash-command invoke，USER#2=skill body 7831 chars，assistant 跑 grep/awk/sed 拆 143439 行 log 产 6-stage 报告 |
| 2 | 1794012967757_ouzip | xxchen | hfeg0pkn001 | drc:623;.gds:193 | 224 | **continuation/env-probe** — USER#0="Context summary: 任务(a)防御性修复已完成..."（任务恢复 context）+ USER#1="阅读AGENTS.md 阅读PROJECT.md"（env-probe），123 msgs 多轮项目 session（DRC_pattern_tool QA），非 clean single-turn produce-demand |
| 3 | 1792135522206_9lnqe | xinqiaoz | hfeg0pkn005 | drc:1026;pdk:937;calibre:341 | 226 | **near-dup** — USER#0 clean demand「新增 DUMMY 检查项 dummyMaskVsFracture，帮我写 config.ini」；但 xinqiaoz 已 31 mentions in jsonl_C，DUMMY-config 主题 11 mentions，11+ existing DUMMY case（DummyQaCliNoConfig / DummyQaDataPrep / DummyCfgCheck / DummyBorderRcaGen / DummyDeck / DummyFillCoverageAnalyzer / DummyGeoVerify / DummyHeaderQaResolver / DummyMeas / BlkDummyClipPipelineExtract / AnalogGroupCfgMergeDummy）—— 同 archetype heavily covered |
| 4 | 1792052491292_p5laa | xinqiaoz | hfeg0pkn005 | drc:1876;pdk:873;calibre:295 | 267 | **task-resume** — USER#0="# 任务恢复 + 环境健康检查（Dummy 知识迁移，Plan v2.1 final，阶段 E 执行中断续接）..."（9127 chars 任务恢复 prompt），119 msgs，非 clean produce-demand |

## 结论

**8th 独立复验质量饱和**（r404-r410 7 连续维护轮 + r413 本轮）。11/09 scan top 4 fresh-against-all-4 C-domain-dominant 高 mc 候选（mc 144-267，覆盖高 mc 段）peek 全 REJECT：
- 2 near-dup（同 archetype 已 heavily covered：DRC-log-teardown 4 case / DUMMY-config 11+ case）
- 1 continuation/env-probe
- 1 task-resume

**与 r410 结论一致**：饱和约束 = archetype+gate（非 threshold）；mc≥10 池数量未枯竭（mc10.fresh=267≠0），但 fresh 候选主题已被现有 308 case 覆盖（C 域 4 archetype 饱和：DRC-log-teardown / DUMMY-config / DRC-deck-opt / DRC-pattern-QA）。

**shard A 尚未换池 11/05 → 11/09**（mc_matrix.src 仍=summary_1105.tsv，11/12 03:2x 确认）。换池是潜在 unblocker（11/09 scan 已含 12801 fresh candidates，但 top 仍是同 archetype near-dup；需 A 换池后 mc-matrix 重算确认 fresh-against-all-4 池规模）。

**未 claim 新 session**（无 candidate 通过 peek）。ledger_C 698 行不变，jsonl_C 308 不变。
