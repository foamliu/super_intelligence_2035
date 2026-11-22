# r1057 shard B — §4.9 selftest harness audit (systematic r1056 follow-up)

**Round**: r1057 (2026-11-23, 0-case stop-loss round #19 + ledger governance)
**Trigger**: r1056 found a `negative_selftest.py` WORKDIR_ROOT `dirname` multi-layer path bug
in DutyOffsetAlertMaxProduce-001 (dirname x3 → `benchmarks/` instead of `EDA-Eval-DesignFlow/`,
making all 3 negs false-pass via "missing hidden B file" precondition). r1056 next-step
explicitly recommended a same-type排查 on historical cases. This note records that audit.

## Scan method
`scan_selftest_bug.py` (/home/app.e0031982/.cache/df_scan/) ran all 232 B.jsonl cases'
`negative_selftest.py` (45s timeout each, 8-way parallel) and flagged the r1056 bug
signature: **all negs fail with the SAME precondition message** (hidden/missing/not found/
ENOENT/precondition/workdir). Output: /home/app.e0031982/.cache/df_scan/selftest_scan_results.json.

## Scan results (232 B cases)
| status | count | meaning |
|---|---|---|
| NO_SELFTEST | 136 | case has B.jsonl entry but no `reference/<id>/negative/negative_selftest.py` (legacy pre-§4.9 gap) |
| OK | 69 | selftest runs, negs produce ≥2 distinct assertion messages |
| NO_FAIL_LINES | 25 | selftest runs but my regex missed its output format (false alarm — manual sample confirmed all OK) |
| SAME_MSG_NO_PRECOND | 2 | false alarm (HspiceAlterTrnPredictor-001: 6 negs × distinct msgs; PostSimUncommentFix-001: 3 negs × {g,i}/{d,f,j}/{d,f,j}) |
| BUG_SUSPECT (r1056 pattern) | **0** | no case exhibits the exact r1056 same-precondition-msg bug |
| TIMEOUT / ERROR | 0 | — |

**Conclusion**: the r1056 bug was a one-off, NOT a systemic issue. No other B case has the
same "all negs false-pass via identical precondition" pattern.

## Real defects found (manual inspection of NO_FAIL_LINES sample)

### Defect A — EDA-Eval-DesignFlow-SharedLibDeployFix-001 (selftest harness path bug, FIXED)
- **Symptom**: `negative_selftest.py` printed `no hidden found` and exited 2 — negs NEVER ran.
- **Root cause**: `BENCH_ROOT = os.path.dirname(os.path.dirname(CASE))` where
  `CASE = os.path.dirname(REF)` = `reference/` (NOT the case dir). So `BENCH_ROOT` =
  `benchmarks/` (one level too high), and `os.walk(BENCH_ROOT/assets)` = `benchmarks/assets`
  which doesn't exist → no `hidden_manifest.json` found → exit 2.
  Exactly the r1056 shape (WORKDIR_ROOT miscalc → precondition fails before negs run).
- **2nd bug in same file**: the `os.walk` found the FIRST dir containing
  `hidden_manifest.json` — could be ANY of 2334 cases' hidden/, not necessarily this case's.
- **Fix applied** (committed this round): replaced walk with direct case-specific path
  `hidden = os.path.join(BENCH_ROOT, "assets", CASE_ID, "hidden")` where
  `BENCH_ROOT = os.path.dirname(os.path.dirname(REF))` = `EDA-Eval-DesignFlow/`.
- **Verified**: all 3 negs (naive_copy_all.sh / always_ok.sh / hardcoded_A.sh) now correctly
  FAIL (rc=1) → `ALL FAIL` → selftest exits 0. §4.9 三假齐 now genuinely holds for this case.

### Defect B — EDA-Eval-DesignFlow-SharedLibDeployFix-001 (REF solution broken, NOT FIXED this round)
- **Symptom**: REF solution `fix_missing_libs.sh` run against clean hidden B → check.py
  returns rc=1 with `FAIL: FAILED conditions: d, e, h`.
  - (d) "all expected missing non-system libs copied (count == expected)" — FAIL
  - (e) "no system/glibc libs present in P010/tool/lib/lib after fix" — FAIL
  - (h) "sourcing setup_env.sh then running gxrc_t exits 0" — FAIL
- **Tested on**: clean hidden B restored via `git checkout` (no prior neg mutation).
  REF still FAILs → not a dirty-state artifact.
- **Implication**: §6 step 2 ("reference/ 参考解跑 check() 必 PASS") is violated.
  The case is broken at the reference-solution level — adding it to B.jsonl was improper
  (or check.py / hidden B drifted after the case was added).
- **Action**: NOT fixed this round (out of scope — needs investigation of whether ref
  solution, check.py, or hidden B drifted). Case should be flagged in
  `designflow/rewrite_queue.tsv` for separate remediation. My selftest harness fix (Defect A)
  is still correct and necessary — §4.9 三假齐 (negs FAIL) now holds; but the case overall
  is NOT §4.9-compliant because REF doesn't PASS.

### Defect C — EDA-Eval-DesignFlow-SaDcSweepTbGen-001 (selftest references missing ref file, NOT FIXED)
- **Symptom**: `negative_selftest.py` crashes at line 40 with
  `FileNotFoundError: .../reference/EDA-Eval-DesignFlow-SaDcSweepTbGen-001/sa_dc_sweep_tb_gen_ref.py`.
- **Root cause**: selftest hardcodes `ref_py = os.path.join(REF_DIR, "sa_dc_sweep_tb_gen_ref.py")`
  but REF_DIR contains only `check.py` — the reference solution file is missing.
  Searched REF_DIR + assets/ + negative/: no `*ref*` python file exists anywhere for this case.
- **Implication**: §6 step 2 REF PASS sanity check cannot run. The REF PASS half of §4.9
  self-verification is impossible for this case. Either the ref file was lost (git history
  check needed) or the selftest was committed against a ref file that never existed.
- **Action**: NOT fixed this round (needs git archaeology to recover the ref file or
  confirm it never existed). Flagged for separate remediation.

## Broader finding: 136/232 B cases (59%) lack negative_selftest.py
These are legacy cases added before §4.9 enforcement (negative_selftest.py + ≥2 negs +
all-FAIL selftest became a hard requirement). They predate r1011's ghost-case cleanup
and the r1042 "negative_selftest.py 补齐" campaign. Not a "bug" per se, but a §4.9 audit
coverage gap: for these 136 cases, the 三假齐 (a)(b)(c)退化提交回归 cannot be re-verified
without first building the selftest harness. Sample-checked 5 of the 136 — none have
`reference/<id>/negative/` directory at all (just `check.py` in REF_DIR).

**Recommendation for future rounds**: when a 0-case stop-loss round has no §4.9 queue
and no new scan, the highest-value ledger-governance action is to progressively build
`negative_selftest.py` for the 136 legacy cases (prioritizing high-mc / recent cases),
each accompanied by a REF PASS sanity check that would catch Defect-B-style ref-broken
cases. This is a multi-round campaign, not a single-round task.

## What this round changed
- **Fixed**: `benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-SharedLibDeployFix-001/negative/negative_selftest.py` (Defect A — path bug + walk-specificity bug).
- **No case produced** (0-case stop-loss round #19; fresh B-spice pool still exhausted;
  no new scan on .75 today). B.jsonl unchanged at 544.
- **No MEMORY_B structural change** — appended r1057 line + this deepread note pointer.
