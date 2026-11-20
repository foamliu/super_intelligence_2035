# Deepread — nmanu (gokuguo @ 10.129.35.74) — ErcRulecheckStatsScan-001

## Trace source
- session: `1793669028784_nmanu` (mc=13, keywords lvs:428/virtuoso:213)
- host: 10.129.35.74, user: gokuguo
- 38 msgs, 21 user msgs
- assistant tools: editor(7) + run_approved_command(7) + read_files(1) + list_allowed_files(1)

## User intent (verbatim, A-faithful)
- **U#0/U#1**: "读取 `/proj/lacaa/V0_FS_Virtuoso_test/workdir/gokuguo/LVS/Libs_run/FSP51H204L6W35T6_BASE_SVT/1103/LVS_20261103_091614/FSP51H204L6W35T6_BASE_SVT` 下每个文件夹内的 `erc.rep`，帮我找到 `RULECHECK gate_to_pg ......................... TOTAL Result Count = 0 (0)`，这里的 Count 是否都是 0？你能理解我的意思吗？注意你只能读，不能删除任何东西。"
- **U#9**: "都统计一下吧。" (follow-up: stats of ALL RULECHECK items)

## Real task
Batch scan 463 LVS-run subfolders for erc.rep; find RULECHECK gate_to_pg TOTAL Result Count, report whether all are 0; then count stats of ALL RULECHECK items (per-rule folders/nonzero/notexec).

## Real deliverable (accepted by user)
- `/home/gokuguo/check_gate_to_pg.py` (initial: scan gate_to_pg only)
- `/home/gokuguo/stats_all_rulecheck.py` (extended: stats of all RULECHECK items)
- `/home/gokuguo/gate_to_pg_full_list.csv` + `/home/gokuguo/rulecheck_summary.txt` + `/home/gokuguo/all_rulecheck_full.csv`
- Real summary: TOTAL subfolders=463, missing erc.rep=0, gate_to_pg nonzero=0 (all 0), pathchk_no_label nonzero=433, nwell_floating NOT EXECUTED=455, 4T_EGATE/pickup_check/DFM_* NOT EXECUTED=463.

## Reframe (mock-behavioral, C-domain first: erc-report-batch-rulecheck-stats)
- Real path `/proj/lacaa/...` is private/path-dependent → reframe as provided `A/` directory tree of 12 synthetic erc.rep files (same `--- RULECHECK RESULTS STATISTICS` format as real Calibre ERC).
- Real deliverable = 3 files (csv + txt + csv) → reframe as single JSON report (checkable via JSON parse).
- Candidate = `erc_rulecheck_stats.py` (pure stdlib): `--base <dir>`, scans subfolders for erc.rep, parses statistics section with regex `^RULECHECK\s+(.+?)\s\.{3,}\s(.+)$` + `Result\s+Count\s*=\s*(\d+)`, extracts rule->int|None(NOT EXECUTED)|str(other), outputs JSON with total_subfolders/missing_rep/gate_to_pg/all_rules/rules_with_nonzero/stats.
- distinct vs r697 PgDummyFillFlowOrganize=TVF deck single-file structural extract / r695 RsCalcFlowCompare=multi-file .rvn CSV parse + reduction% compare / r694 SkillFileBatchTransform=batch file text transform / r692 AetherAutorouteTraceRuleDiag=manual search + error diagnose / r690 DrcVarMisMatchDiag=diagnose existing report = **本例 batch-tree-scan + statistics-section-extract + per-rule stats aggregator**.

## Asset design (A/B/B2 disjoint)
- **A** (visible, 12 folders): AIOI21D1_SampleA ... INVx1_SampleA. gate_to_pg all 0 (user's "yes all 0"). pathchk_no_label nonzero (1) in 5 folders. nwell_floating NOT EXECUTED in 10. 4T_EGATE/pickup_check/DFM_LDEX/DFM_GATE/DFM_SDB NOT EXECUTED in all 12. 17 rules.
- **B** (hidden main, 9 folders, anti-hardcode): BD2D1_SampleB ... BXOR_SampleB. gate_to_pg nonzero (2) in 3 folders (BD2D1/BD2D2/BNTSEL). pathchk_no_label all 0 (anti A's 5). nwell_floating all 0 (anti A's 10 notexec). 4T_EGATE/pickup_check/DFM_* NOT EXECUTED in all 9. **B-only rule b_substrate_check** nonzero (1) in 4 folders (BSAMP/BDECAP/BFLIPFLOP/BXOR). 18 rules. Folder names ∩ A = ∅.
- **B2** (hidden edge, 6 folders): CD2D1_SampleC ... CFLIPFLOP_SampleC. 1 missing erc.rep (CDECAP_SampleC). 2 folders (CNTSEL/CFLIPFLOP) have erc.rep but gate_to_pg NOT in stats section. Other 3 (CD2D1/CD2D2/CSAMP) have gate_to_pg=0. 12 rules. Folder names ∩ A ∩ B = ∅.

## check() 16 conditions (a-p)
a. zip contains erc_rulecheck_stats.py | b. py_compile | c. B exit 0 + valid JSON | d. B 6 top-level keys | e. B total_subfolders==9 (anti A 12) | f. B missing_rep==0 | g. B gate_to_pg.all_zero==false (anti A true) | h. B gate_to_pg.nonzero_count==3 | i. B gate_to_pg.nonzero_folders has BD2D1_SampleB count 2 | j. B all_rules[gate_to_pg].nonzero==3 | k. B all_rules[pathchk_no_label].nonzero==0 (anti A 5) | l. B all_rules[nwell_floating].notexec==0 (anti A 10) | m. B all_rules[4T_EGATE].notexec==9 | n. B all_rules has b_substrate_check nonzero==4 (B-only) | o. B rules_with_nonzero has both gate_to_pg + b_substrate_check | p. B2 missing_rep==1 AND gate_to_pg.not_present==2 (edge).

## Negatives (4 distinct first-fails)
- neg1_empty_shell → (c) | neg2_only_print_A → (e) | neg3_no_core_logic → (g) | neg4_always_pass_stub → (p)

## Self-verify
- gold 16/16 PASS on A/B/B2 ✓
- 4 negatives ALL FAIL, 4 distinct first-fails (c/e/g/p) ✓
- §4.9 three fakes (空壳/只print A/删核心) = neg1/neg2/neg3 all FAIL ✓
- determinism: B twice byte-identical (md5 987eb63ac3578e99b25b961143e80111) ✓
- A∩B∩B2 folder names disjoint ✓; A∩B rule profiles inverted (gate_to_pg/pathchk_no_label/nwell_floating) + B-only b_substrate_check ✓
- k_rationale = k_check = 16 >= 8 GATE PASS ✓
- jsonl test field round-trip: extract -> check.py -> run on reference_submit.zip -> True ✓
