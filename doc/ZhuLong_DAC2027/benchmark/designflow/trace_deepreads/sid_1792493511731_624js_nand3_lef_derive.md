# Deep-read: 1792493511731_624js (johnl, hfeg0pfn119) — pg_layout LEF derive

## Trace identity
- session_file: `1792493511731_624js.messages.json` (+ `.messages.archive.json`, 8.8 MB)
- user: johnl · host: hfeg0pfn119 · summary match_count: 80 · tools: 165 innovus (pure-innovus dominant)
- active file 75 msgs (PrimeTime STA continuation); archive 2882 msgs (the real PR/LEF work)
- session dir: `/home/johnl/.cline/data/sessions/1792493511731_624js/`
- ledger status: claimed r154 → case `EDA-Eval-DesignFlow-Nand3LefDeriveAudit-001` (pg_layout)

## Real task (from archive user turns, idx 421/699/761...)
GenLEF (`ski-genlef`) produced a LEF for cell `nand3LVSx1` whose **prBoundary was lost**. The
GenLEF log reported `FINDBOUNDARY-INFO: nand3LVSx1 prBoundary=3.88x6.71@(0,0) src_OA` but then
`ERROR: (dbCreateRect) Extra arguments` / `Cell 'nand3LVSx1' does not have layer '235:250'`, so the
boundary rect was never created. The emitted LEF header consequently collapsed to the
**integer-extreme sentinel**:

```
MACRO nand3LVSx1
  CLASS BLOCK ;
  ORIGIN -214748.3647 -214748.3647 ;
  FOREIGN nand3LVSx1 214748.3647 214748.3647 ;
  SIZE 0.0001 BY 0.0001 ;
  SYMMETRY X Y R90 ;
```
(±214748.3647 = INT32_MAX / DBU(10000); SIZE 0.0001 BY 0.0001 = the degenerate fallback.)

The user (johnl) repeatedly instructed (idx 699, 761, 782, 1843, 1905, 1926):
- confirmed true value: source OA `emyPRBoundary.find(cv.getTopBlock())` → **(0,0)–(3.88,6.71) µm, DBU=10000**
- derive an **independent派生 LEF** from the true prBoundary (don't touch source OA/GDS/LEF/PDK;
  don't run P&R; don't guess CLASS/SITE/SYMMETRY)
- only fix SIZE/ORIGIN/FOREIGN; preserve PIN/OBS geometry, Y=OUTPUT, vcc!=POWER, vss!=GROUND
- deliver reproducible script + derived LEF + before/after diff + per-item verification

## Assistant's verified fix (tool_result idx 769 / 1913)
Script `/home/johnl/derive_lef.py`, boundary source `/home/johnl/prb/prb_points.txt`
(`nand3LVSx1 0,0;0,6.71;3.88,6.71;3.88,0`). Coordinate check showed LEF pin/OBS/power-rail
coords already in the source OA coordinate system (vss! rail Y −0.41..+0.41 centered on 0;
vcc! rail Y 6.30..7.12 centered on 6.71) → ORIGIN=(0,0), FOREIGN=(0,0). Diff applied:
```
-  ORIGIN -214748.3647 -214748.3647 ;
-  FOREIGN nand3LVSx1 214748.3647 214748.3647 ;
-  SIZE 0.0001 BY 0.0001 ;
+  ORIGIN 0.000 0.000 ;
+  FOREIGN nand3LVSx1 0.000 0.000 ;
+  SIZE 3.880 BY 6.710 ;
```
Five-point verification all PASS: SIZE 3.880 BY 6.710; ORIGIN 0.000 0.000; FOREIGN 0.000 0.000;
Y DIRECTION OUTPUT; vcc!/vss! INOUT+POWER/GROUND; geometry diff 0; no integer-extreme pattern.
Deliverables: `nand3LVSx1_derived.lef` (2719 B), `derive_lef.py`.

## Generalized rule (for the case)
Given a (lost-prBoundary) input LEF + true prBoundary (xmin,ymin,xmax,ymax) µm:
- SIZE  = (xmax−xmin) BY (ymax−ymin)
- ORIGIN = (xmin, ymin)
- FOREIGN refpoint = (xmin, ymin)   [cell-local origin coincides with prBoundary min corner]
- detect integer-extreme sentinel (|v|≥214748 or SIZE<0.001) → must be replaced, not kept
- edit ONLY the SIZE/ORIGIN/FOREIGN lines; preserve every other line (PIN/OBS/USE/DIRECTION/CLASS/SITE/SYMMETRY), line count unchanged

## Case shape (L1-boundary, faithful-seed-B-synthesized)
- A asset (SUT-visible): `nand3LVSx1_A.lef` (buggy GenLEF output, integer-extreme header + full
  PIN/OBS body) + `prb_A.txt` (`0,0,3.88,6.71`) + prompt.md + task_brief.md
- deliverable: SUT writes `derive_lef.py` (<input.lef> <prb.txt> <output.lef>; rewrites only
  SIZE/ORIGIN/FOREIGN from prBoundary; preserves rest; --help/-h; malformed → exit 1)
- hidden B (base64 in check.py): B1 (nand3LVSx1, prb 1.20,0.50,5.00,7.21 → SIZE 3.800 BY 6.710,
  ORIGIN/FOREIGN 1.200 0.500 — non-zero min exposes both naive bugs); B2 cross-input guard
  (inv2xLVSx1, prb 0,0,2.40,4.00, pins IN/OUT/VDD/VSS — no nand3/Y/vcc!/vss! tokens); B3
  malformed (no MACRO/SIZE → exit 1)
- 14 check conditions (a–n): compile/CLI/B1 output/SIZE/ORIGIN/FOREIGN/sentinel-gone/PIN-OBS
  preserved/only-3-lines-changed/B2 cross-input cell-name guard/B2 USE preserved/B3 exit/
  determinism/anti-naive
- gold `derive_lef_ref.py`; 5 negatives + negative_selftest; §4.9 three fakes FAIL
