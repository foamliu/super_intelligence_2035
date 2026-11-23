# Ledger ↔ cases/ Reconciliation Report — r1033 (2026-11-23)

## Context
Shard A ledger `trace_ledger_A.tsv` vs `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/A/*.json`.
Pre-fix drift: 49 orphan files (file exists, no ledger case_id) / 71 phantom ledger cids (case_id in ledger, no file) / 2 empty-case_id rows / 1 duplicate-session row.

## Fixes applied this round (5, all verified trace_source.session_file == ledger session)

| # | session | fix | verified |
|---|---------|-----|----------|
| 1 | 1793004252449_aet4o.messages.json | removed 1 of 2 identical rows (SramFarCellSelect-001-v2) | ✅ |
| 2 | 1791790886127_58vqx | empty case_id → EDA-Eval-DesignFlow-DrcSyntaxTest-001 | ✅ ts match |
| 3 | 1794553984282_g5ise | empty case_id → EDA-Eval-DesignFlow-VltRetryWave2-001 (note already said so) | ✅ ts match |
| 4 | 1789624027491_t45kv | PRStartMethodSelect-001 → -001-v2 (v1 file absent, v2 exists) | ✅ ts match |
| 5 | 1792033394584_xd7ut | WtmWriteArrayScope-001 → -001-v2 (v1 file absent, v2 exists) | ✅ ts match |

Post-fix: 45 orphan / 68 phantom / 0 empty / 0 dup-sess; covered 499→498 (dedup removed 1 phantom count). distinct case_ids now == case rows (498).

## Remaining drift (needs careful per-case work — NOT touched this round)

### A. v2-both-exist orphans (≈36): v2 file exists, v1 file ALSO exists, ledger tracks only v1
Per 11-15 order "重做 = 新增 v2 + 标 v1 retired (不删)", v1 should be marked retired and v2 added as active.
Current ledger has no "retired" status; blindly adding v2 rows would create duplicate sessions.
**Recommended**: extend ledger status enum {case, parked, ...} → {case, retired, parked, ...}; mark v1 retired, add v2 active. This would raise true coverage by ~36. Needs design decision (do retired v1 count in denominator?).
Examples: CdlNetlistAnalyze-001 (+-v2), DcSynthAnalyze-001 (+-v2), FloorplanTclAudit-001 (+-v2), ... (full list in r1033 analysis output).

### B. non-v2 orphan files (≈11): file exists, no ledger entry, naming may mismatch
- CadenceVipLinkErrorDiagnose-001, CosimSetup-001, DrcSyntaxTest-001 *(fixed this round: was 58vqx empty-cid)*, IrunWarnClassify-001 *(ledger has "IrunWarnClassifyProduce-001" — Produce/no-Produce variant)*, MrrDqExpFlowAnalyze-001, RunScenarioExtractProduce-001, V2lvsCdlCheck-001, VltRetryWave2-001 *(fixed this round)*, VsimCmdReformatDedupProduce-001, WaveSig-001, XrunCuvunfSegfaultDiagnose-001.
**Recommended**: per-case check file task_id vs ledger cid variants (Produce/no-Produce, prefix/no-prefix); backfill missing rows or fix cid spelling.

### C. phantom ledger cids (≈68): case_id in ledger, no matching file
Mix of (i) old "EDA-Eval-DesignFlow-Digital-NNN" seeded entries never materialized as cases/, (ii) naming-variant of an existing file, (iii) genuinely missing case file.
**Recommended**: per-case grep file by trace_source.session_file; if a file exists under a different name → fix cid; if no file at all → mark parked/retired (don't count in coverage).

## Note
This round was a 0-case governance round (13th consecutive): scan quota used today (r1019 06:43), mc≥5 A-pure fresh viable pool = 0 (7 rotation-evaporated phantoms), parked-revival 63y2k failed 3 ways (r1032). Next real case opportunity: 11-24 scan quota recovery → new full 698-machine scan → POOL_SWITCH → immediate peek (<24h, before rotation).
