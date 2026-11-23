# Deepread: 1795078501935_2ajng (Innovus CCOPT cell extract + delete)

- **session**: 1795078501935_2ajng
- **user**: leo27li
- **host**: hfeg0pkn003 (ip 10.129.2.12)
- **match_count**: 82
- **domain**: pnr_signoff (innovus:243 dominant → shard A)
- **scan**: ssh_eda_search_20261123_064315/summary.tsv
- **session file (on .75)**: `/home/leo27li/.cline/data/sessions/1795078501935_2ajng/1795078501935_2ajng.messages.json` (355993 bytes, 76 msgs)
- **scp'd to eda_flow workdir**: `designflow_20261123-shA_DfA-r1020-cand_0/2ajng.messages.json`
- **status**: claimed (shard A) → marked case `EDA-Eval-DesignFlow-CcoptCellExtractDelete-001`

## Three user intents in trace

1. **"怎么创建2x4对于同样的macro"** → Innovus `create_inst_array` / `placeInstance` 2x4 macro array. Tool-usage Q&A; not a strong produce-task.
2. **"dbget top.bumps.netname -reg $a" debug** → Tcl `glob`/bracket matching with variables. Debug help; not a strong produce-task.
3. **"把这个报告里面的CCOPT的cell抓取出来" + "删除他们"** → extract CCOPT cells from Innovus `report_timing` report `new.rpt`, generate delete Tcl script. **Most concrete, checkable produce-task.** Selected.

## Intent #3 detail (selected for case)

User literal:
> /proj/lagat/V0_digital/workdir/leo27li/dram_tester_chip/run/rev20261117a_hl22_newoccsdc_wiscan_aocv_bigbuffer/new.rpt 把这个报告里面的CCOPT的cell抓取出来
> 删除他们

The real `new.rpt` is permission-denied on `.75` (lives under `/proj/lagat/...`), so attachment `new_A.rpt` is a synthesized faithful replica:
- Cadence Innovus 23.35-s106_1 header
- `report_timing -max_paths 3 -path_group TxClk5G_0`
- 3 timing paths, Point column has 4 unique `CCOPT_INST__` instances (also appearing as duplicated entries across paths to test dedup):
  - `CCOPT_INST__ccl_inv_30716`
  - `CCOPT_INST__ccl_inv_29479`
  - `CCOPT_INST__ccl_a_inv_29643`
  - `CCOPT_INST__ccl_a_inv_29441`
- Non-CCOPT noise present (DFFHQX4 registers, BUFHX8 buffers) — must NOT be extracted.

Trace gold (msg 61): Python regex parse report_timing rows, extract instance names starting with `CCOPT_INST__`, dedupe, output list + generate `deleteInst` Tcl.

## Case artefacts (in EDA-Flow-Bench repo)

- `cases/A/CcoptCellExtractDelete-001.json` — case JSON (mode design_flow, k_check=19, k_rationale=19, domain pnr_signoff)
- `assets/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/new_A.rpt` — visible report (4 CCOPT cells, TxClk5G_0)
- `assets/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/new_B.rpt` — hidden B report (6 CCOPT cells, RxCk2G5, disjoint from A)
- `assets/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/task_brief.md` — visible task brief
- `assets/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/hidden_manifest.md` — B ground truth (not shipped to SUT)
- `reference/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/check.py` — 19 assertions (a-s)
- `reference/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/extract_ccopt_ref.py` — gold solution
- `reference/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/neg_a_empty.py` — empty-shell fake
- `reference/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/neg_b_print_only.py` — hardcoded-A fake (passes A, fails B → anti-hardcode via B)
- `reference/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/neg_c_core_deleted.py` — copy-input fake
- `reference/EDA-Eval-DesignFlow-CcoptCellExtractDelete-001/negative_selftest.py` — bundled selftest

## Self-verify (2026-11-23)

- `negative_selftest.py`: reference 19/19 PASS, all 3 negatives FAIL ✓
- End-to-end via JSON-embedded test field: ref 19/19 PASS, neg-a 1 fail, neg-b 4 fails (anti-hardcode via B), neg-c 9 fails ✓

## 19 check() conditions (k_check=19, ≥8)

a zip_extract · b script_exists · c py_compile · d run_A · e A_count=4 · f A_cellset · g A_deleteInst_cmd · h A_no_false_pos · i A_dedup · j A_header · k run_B · l B_count=6 · m B_cellset(disjoint) · n B_no_leak(anti-hardcode) · o determinism · p subset_random · q anti_empty · r anti_print_only · s anti_core_deleted
