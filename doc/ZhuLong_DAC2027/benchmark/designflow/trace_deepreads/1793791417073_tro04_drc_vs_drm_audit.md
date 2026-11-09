# Deepread: 1793791417073_tro04 (jiaqis / hfeg0plg09 / physical_verify)

**Session**: 1793791417073_tro04
**User**: jiaqis
**Host**: hfeg0plg09 (10.129.x)
**Status**: completed
**Messages**: 137 (1 user turn, 27 assistant turns)
**Match count**: 125 (keywords: drc:5762, .def:998, calibre:21, lvs:17)
**Layout-affinity score**: 5800 (high — pure DRC, no sim keywords)
**Date**: 2026-11-10 (session mtime 2026-09-17, captured in scan ssh_eda_search_20261109_224902)

## User intent (U#0, original)

> 请检查去一下，这个drm中的rule是否都在这个drc中存在，将drm中存在但是drc中不存在和drc中存在但是drm中不存在的分别列出来，给我出一个报告，详细的描述一下。检查出现什么异常的情况也放在报告中。

**Attachments**:
- `35H_DRC_Cal_V0d1a_Rev13_1P22M_16F1xa1x1xb1ya6y4yy_6B2v2z1u.drc` (8.2 MB, Calibre DRC deck)
- `CXMT_35H_Design_Manual_V0.1_Rev13_S12_20261030.drm` (944 KB, design manual TSV)

## Classification

- **Task type**: produce-task (生成报告) ✓
- **User did NOT give root cause or fix** ✓ (只提需求"列出差异+出报告")
- **Accepted gold**: assistant 完成分析，生成报告文件，status=completed ✓
- **Domain**: physical_verify (DRC rule audit / coverage comparison)
- **Level**: L1→L2 (offline Python parsing of real DRC deck + DRM manual; check runs candidate via subprocess on hidden B)

## Assistant tool chain (72 tool calls)

1. `list_allowed_files` (3) — 查看工作区
2. `run_commands` (2) — 查 uploads + 文件行数
3. `editor` (33) — 写 Python 脚本: analyze_structure.py, extract_rules.py, extract_drc.py, extract_drc2.py, inspect_drc.py, drm_firstcols.py, compare.py, compare2.py
4. `run_approved_command` (28) — 执行 Python 脚本
5. `read_files` (6) — 读中间结果

**Key scripts**: parse DRM (TSV: id/description/label/op/value) → extract rule IDs; parse DRC (Calibre deck) → extract rule references; compare → matched/missing/standalone.

## Gold result (assistant final output)

- DRM: 5718 unique rule IDs (去重)
- DRC: 24045 rule blocks (去重)
- Coverage: exact 3170 (55.4%), split 431 (7.5%), covered 91 (1.6%), alias ...
- 报告文件生成并验证完成

## Benchmark case design

**Case ID**: EDA-Eval-DesignFlow-DrcVsDrmRuleAudit-001

**A (SUT-visible)**: synthetic DRM (15 rules, TSV) + synthetic DRC (20 rules, Calibre deck format with `// Rule: <id>` annotations). Same format as real trace, smaller scale.

**B (hidden, 3 pairs)**:
- B:  20 DRM, 25 DRC (15 matched, 5 missing, 10 standalone)
- B2: 18 DRM, 22 DRC (14 matched, 4 missing, 8 standalone)
- B3: 22 DRM, 28 DRC (16 matched, 6 missing, 12 standalone)

**Reference**: `compare_rules.py` — parse DRM IDs (regex on col 1), parse DRC IDs (from `// Rule:` comments), set intersection/difference → JSON report.

**check.py**: 15 conditions (a-o), runs candidate on all 3 hidden pairs, verifies matched/missing/standalone sets + counts + disjointness + coverage + no-duplicates. All 3 pairs must match — defeats hardcoded/print-only stubs.

**Negatives**: naive_stub (empty lists), print_only (hardcoded B answer, fails on B2/B3), deleted_core (only matched, no missing/standalone). All FAIL ✓.

**§4.9 fake submissions**: (a) empty shell FAIL, (b) print-only FAIL, (c) deleted-core FAIL ✓.

## Why this seed was missed by previous saturation rounds

Previous rounds (r299-r318) sorted candidates by `match_count` (mc) and checked the top-mc pool. This seed has mc=125 (moderate), but layout-affinity score=5800 (very high — pure DRC, zero sim keywords). The mc-sort approach missed it. r319 corrected by computing layout-affinity score (lay − 0.6×sim) using the keywords column (col 5, `name:count;` format), finding 767 non-ledgered candidates with score≥100 and 910 with score≥10. This overturns the "natural saturation" conclusion.
