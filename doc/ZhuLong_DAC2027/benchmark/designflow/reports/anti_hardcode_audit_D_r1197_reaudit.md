# Anti-Hardcode Audit D — r1197 Reaudit Report

**Date**: 2026-11-23 (r1197)
**Shard**: D (netlist_wave: analog_context, schematic_netlist, waveform)
**Trigger**: r1196 MEMORY noted audit_D.tsv had 24 GAPs after stale-correction pass; this round re-audited all 24 via runtime check (instead of static analysis).

## Method

Wrote `reaudit_gap_D_r1197.py` which, for each of the 24 GAPs in `audit_D.tsv`:
1. Resolves reference dir (handles `EDA-Eval-DesignFlow-` prefix variants + bare names).
2. Runs `python3 check.py` (self-test) — captures rc + last lines.
3. Runs `python3 negative_selftest.py` (at ref root OR in `negative/` subdir) — recognizes 14+ pass-markers across cases (`ALL_NEG_FAIL = True`, `NEG_RC=0`, `NEG_SELFTEST PASS`, `ALL GOOD`, `all_fail=True`, `ALL negatives FAIL`, etc.). Excludes the inverted marker `NEGATIVES PASS (BUG): N` when N>0.
4. Heuristic on check.py source for anti-hardcode presence (`anti-hardcode`, `mock a`, `a-gold`, `a_prime`, `a fixture`, `a_dir`, `a_sp`, `a_rm`, `spec_a`, `structurally different from a`, `b vs a`, `hardcode of a's`, etc.).
5. Decision: PASS(stale-corrected) iff self-test PASS ∧ neg_selftest PASS ∧ anti-hardcode present.

## Result

| Verdict | r1196 | r1197 | Δ |
|:--|--:|--:|--:|
| PASS | 464 | 477 | +13 |
| PASS(inline) | 72 | 72 | 0 |
| GAP | 24 | 11 | −13 |

**13 stale-corrected PASS** (audit was static; runtime confirms compliant):

| case_id | k | reason r1196 missed |
|:--|--:|:--|
| EDA-Eval-DesignFlow-CABufDiffPairOPCheck-001 | 14 | anti-hardcode phrased as `neg_hardcode_b 跑 A 出的 vov 与 A 真值差异` + `a_dir = workdir/A` (heuristic missed "a_dir") |
| EDA-Eval-DesignFlow-IddMeasPostProcess-001 | 12 | negative/ subdir (`negative/negative_selftest.py`) not ref root |
| EDA-Eval-DesignFlow-IddTreeAnalyze-001 | 15 | negative/ subdir + phrased "ALL GOOD" not in marker list |
| EDA-Eval-DesignFlow-IrunLogNetlistMissingModDiagQA-001 | 14 | negative/ subdir + "ALL NEGATIVES FAIL (expected)" marker missed |
| EDA-Eval-DesignFlow-LvsConcatDiagQA-001 | 14 | negative/ subdir |
| EDA-Eval-DesignFlow-MosfetBlockInventoryQA-001 | 17 | negative/ subdir + "NEG_RC: ALL FAIL" marker missed |
| EDA-Eval-DesignFlow-OpenDmViewsProduce-001 | 12 | negative/ subdir + "negative_selftest: ALL NEGATIVES FAIL ✓" marker missed |
| EDA-Eval-DesignFlow-StdcellRerunCollect-001 | 14 | `a_dir = workdir/A` phrasing missed by heuristic |
| EDA-Eval-DesignFlow-StdcellStatusPartition-001 | 12 | negative/ subdir + "NEG_RC=0" marker missed |
| EDA-Eval-DesignFlow-TbFamilyMergeConverted-001 | 16 | "NEGATIVES PASS (BUG): 0" was incorrectly excluded (0 = no bugs) |
| EDA-Eval-DesignFlow-TbFamilyResultVerify-001 | 15 | `a_dir = workdir/A` + "NEGATIVE SELFTEST PASS" marker missed |
| EDA-Eval-DesignFlow-TrMatchHelper-001 | 14 | condition `m` is anti-hardcode but audit's static scan missed it |
| EDA-Eval-DesignFlow-VddSensTDCRootCause-001 | 12 | r1171 added 6 conditions (m-r) testing A-numbers-hardcode-on-B → FAIL; phrasing "hardcode of A's numbers" missed |

**11 real GAPs remain** (need actual fixes — not done this round):

| case_id | k | gap type | fix needed |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-FuseAddrCompare-001 | 35 | selftest=FAIL | broken self-test (check.py expects argv) |
| EDA-Eval-DesignFlow-NetlistSvRulesReorg-001 | 22 | neg=MISSING | add negative/ + negative_selftest.py |
| EDA-Eval-DesignFlow-NetlistVdomPrefixCount-001 | 35 | neg=MISSING | add negative/ + negative_selftest.py |
| ParasiticsAnnotDiag-001 | 9 | selftest=FAIL | broken (k<10, also too few conditions) |
| EDA-Eval-DesignFlow-StdcellFullAdderBuild-001 | 12 | selftest=FAIL | missing `solution_build_adder.py` |
| TotemLayermapFatalDiag-001 | 16 | selftest=FAIL | broken self-test |
| TsCodeComp3bitLogicDiffQA-001 | 16 | selftest=FAIL | broken self-test |
| EDA-Eval-DesignFlow-TscodecompTruthTable-001 | 18 | neg=MISSING | add negative/ + negative_selftest.py |
| EDA-Eval-DesignFlow-VerdictJoinPassLib-001 | 15 | selftest=FAIL | broken self-test |
| EDA-Eval-DesignFlow-WvEdgeTiming-001 | 17 | selftest=FAIL | broken: missing `assets/.../hidden/sig_B1.txt` |
| WvLdqPadShiftCmp-001 | 16 | neg=MISSING | has `negative/{empty,no_header}.vec` (real neg inputs) but no fake-submit negative_selftest.py |

## Recommendation for next rounds

1. **4 neg=MISSING** (smallest fix, ~30 min each): add `negative/{neg_print_only.py, neg_core_deleted.py, neg_hardcode_a.py}` + `negative_selftest.py` for `NetlistSvRulesReorg-001`, `NetlistVdomPrefixCount-001`, `TscodecompTruthTable-001`, `WvLdqPadShiftCmp-001`. The check.py for each already has anti-hardcode (conditions n-p test anti-hardcode / negative inputs), so only the §4.4 fake-submit negative bundle is missing.
2. **7 selftest=FAIL** (broken cases, harder): each requires debugging why `python3 check.py` exits non-zero. Several look like simple path bugs (WvEdgeTiming needs `assets/.../hidden/sig_B1.txt` which exists in assets/ but check.py runs from ref dir; StdcellFullAdderBuild needs `solution_build_adder.py` next to check.py). These are case-internal bugs, not anti-hardcode gaps — fix in dedicated rounds.
3. **Audit hygiene**: the r1196 + r1197 stale-correction (87→24→11 GAP) reveals that **static audit over-counts GAPs** because it can't see runtime-passing negative_selftest.py in `negative/` subdir + misses inline anti-hardcode phrasings (`a_dir`, `a_gold`, "hardcode of A's numbers"). Future audits should default to runtime re-audit.

## Files modified this round

- `designflow/anti_hardcode_audit_D.tsv` — 13 rows: verdict GAP→PASS, anti_hardcode→y, negative_present→y, gaps→stale-corrected note
- `designflow/reports/anti_hardcode_audit_D_r1197_reaudit.md` — this report
- `agent_workspace/designflow/reaudit_gap_D_r1197.py` — reaudit script (EDA-Flow-Bench repo)
- `agent_workspace/designflow/reaudit_apply_r1197.py` — apply-corrected-verdicts script (EDA-Flow-Bench repo)

## Cross-shard note

The same stale-audit pattern likely affects shards A/B/C (their audits also used static analysis). Per task §4 discipline, **D does not modify other shards' cases or audits**. If a future round does cross-shard reclaim, the same `reaudit_gap_*.py` script can be reused (parameterize `REF_ROOT` + gap list).
