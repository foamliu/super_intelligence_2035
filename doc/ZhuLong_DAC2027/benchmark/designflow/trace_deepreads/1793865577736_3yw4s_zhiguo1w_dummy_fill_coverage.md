# Deep-read: 1793865577736_3yw4s — zhiguo1w / hfeg0plg76 (mc=78, physical_verify)

**Shard C round r394 case source trace.**
**Case produced:** `EDA-Eval-DesignFlow-DummyFillCoverageAnalyzer-001`

## 1. Trace identity
- session: `1793865577736_3yw4s` (108 msgs, 9.4 MB messages file)
- host: `hfeg0plg76` / user: `zhiguo1w`
- mc=78 (drc:32; calibre:18; aether:14; virtuoso:8) → C-shard physical_verify dominant
- task status: completed

## 2. Real task summary
USER asks why the SOH dummy fill only generates **2 blocks** for a **5×5 target rectangle**. The agent parses the **8.5 MB** `calibreDummy_chip.rule_ai` Calibre SVRF dummy-fill rule deck, extracts the fill-layer geometry for ARZ / WLZ (stripe width, pitch, long-edge expand distance, MINLENGTH), then parses the generated `ARZ.gds` (20244 polygons, bbox x∈[630.08, 1179.92], W=549.84, coverage ≈15.7%) and `WLZ.gds` (7872 polygons, coverage ≈64%). The agent explains that the fill band = target edges expanded by `<expand>` µm, and the stripes are filtered by `MINLENGTH` — so even though the stripe pitch would permit many stripes, only those whose band dimension exceeds `MINLENGTH` survive. This is why SOH dummy looks "long but sparse" (only 2 blocks).

## 3. Why this trace → case
- **physical_verify C-shard domain** ✓ (Calibre DRC dummy-fill SVRF rule deck)
- **produce-task** (clean "explain why" → agent writes analysis tooling) ✓
- **synthesizable**: the core insight (static rule-deck → coverage推算 without running Calibre) is a clean build-tool direction; the 8.5 MB real rule_ai + real .gds files are too big / too PDK-sensitive to embed in the SUT sandbox, so a synthesized small A/B pair preserving the SVRF拓扑 is the right B档 choice.
- **not exhausted**: ledger showed this candidate fresh (not yet `case`).

## 4. Case design (B档 synthesized)
- **Gold**: `dummy_fill_analyzer.py` — parses SVRF (`LAYER MAP`/`LAYER Array_`/`array_long_edge ==angle`/`EXPAND EDGE OUTSIDE BY`/`DFM FILL STRIPE w s DIR MINLENGTH`), then computes per-layer geometry per the model in `prompt.txt`:
  - V-stripe (angle==0): `band_W=target_w`, `band_H=min(border-2·excl, target_h+2·expand)`, `count=floor(band_W/pitch)`, MINLENGTH filter `band_H<min → count=0`, `dummy=count·w·band_H`, `band=band_W·band_H`.
  - H-stripe (angle==90): mirror with `band_W=min(border-2·excl, target_w+2·expand)`, `band_H=target_h`.
  - Totals: `total_dummy_area`, `total_band_area`, `emptyerr_area`, `coverage_pct`.
- **Visible A**: 3 fill layers ARZ (V) / WLZ (H) / XXZ (V, MINLENGTH-filtered), target 5×5 border 500 → coverage **61.36%**, total_dummy 2531.771.
- **Hidden B**: 3 fill layers SN1 (V) / BLZ (H) / YYZ (V, MINLENGTH-filtered), target 8×3 border 800, different gds layer nums (946/949/952) → coverage **64.27%**, total_dummy 2712.322.
- **Cross-input guard**: A coverage 61.36 ≠ B coverage 64.27 → prevents hardcoding.

## 5. Ground-truth (gold output)
| | A | B |
|---|---|---|
| layer 1 (V) | ARZ count=62 band_h=499.4 dummy=1548.14 | SN1 count=100 band_h=318.12 dummy=1654.224 |
| layer 2 (H) | WLZ count=41 band_w=319.88 dummy=983.631 | BLZ count=37 band_w=547.84 dummy=1058.098 |
| layer 3 (V, filt) | XXZ count=0 (band_h=6<10) | YYZ count=0 (band_h=4<10) |
| total_dummy | 2531.771 | 2712.322 |
| total_band | 4126.4 | 4220.48 |
| coverage_pct | 61.36 | 64.27 |

## 6. check.py — 14 independent conditions (a-n, exceeds ≥8 gate)
- a: zip valid + 1 .py; b: py_compile; c: argparse --rule/--layout; d: SVRF keywords; e: VERTICAL+HORIZONTAL; f: MINLENGTH filter branch
- g: subprocess on hidden B → valid JSON; h: 3 layers SN1/BLZ/YYZ; i: SN1 count=100 band_h≈318.12; j: BLZ count=37 band_w≈547.84; k: YYZ MINLENGTH-filtered count=0; l: totals; m: coverage≈64.27; n: cross-input guard A coverage≈61.36 ≠ B
- 2 subprocess 真跑 (cond g + cond n)

## 7. Negatives (4) — all FAIL
- `fake_empty.py` → fails c (no argparse)
- `fake_print_expected.py` → fails d (no SVRF keywords)
- `fake_hardcode_b.py` → fails d (no SVRF keywords)
- `core_deleted.py` → fails k (MINLENGTH filter core deleted → YYZ count=133≠0)
- §4.9 three-fake-submit: empty / print-expected / core-deleted all covered.

## 8. Self-verify results
- `negative_selftest.py`: ALL GOOD (4 negatives FAIL, gold PASS 14 conds)
- E2E (staged workdir + gold zip): PASS, B coverage=64.27, A coverage=61.36

## 9. Files
- assets: `rule_deck_A.svrf`, `layout_params_A.json`, `hidden/{rule_deck_B.svrf,layout_params_B.json,hidden_manifest.json}`, `prompt.txt`, `task_brief.md`
- reference: `dummy_fill_analyzer.py` (gold), `check.py`, `negative/{fake_empty,fake_print_expected,fake_hardcode_b,core_deleted,negative_selftest}.py`
- appended to `EDA-Eval-DesignFlow_C.jsonl` (line 300)
- ledger marked: `1793865577736_3yw4s → case`
