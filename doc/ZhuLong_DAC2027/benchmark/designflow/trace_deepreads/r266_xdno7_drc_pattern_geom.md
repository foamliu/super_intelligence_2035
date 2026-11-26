# Deep-Read: r266 xdno7 (DrcPatternGeomGen-001)

## Trace
- session: 1790574393484_xdno7.messages.json
- user: kenwang @ hfeg0pkn004 (10.129.2.13)
- mc: 140, msgs: 343, agent: lead
- keywords: dbCreateRect:310, dbOpenCellViewByType:132, drc:118, dbCreatePolygon:103, ddGetObj:60, cellview:23, techfile:22, virtuoso:9
- domain: layout_virtuoso
- 4 sibling sessions (xdno7/dx2x0/pikns/re39c) — same task run multiple times

## Real Task
DRC QA test-pattern generation in Virtuoso SKILL. The user (kenwang) is building
SKILL scripts that auto-generate layout test patterns for DRC rules (AA.W.1 min-width,
M1.S.1 min-space). The patterns exercise the DRC deck with "good" (passing), "bad"
(failing + error mark), and "boundary" (at-limit) geometry variants across 11
pattern types (A=bar, B=3-parallel, C=5-dense, H=45°-diamond, J=jog, K=corner-bend,
L=L-polygon, U=U-polygon, O=ring/口, F=serpentine, G=step).

## User Turns (10 real)
1. Fix `*Error* eval: unbound variable - cvGood` in M1_S_1.il (structure corruption)
2. Learn autoPatternFamily docs, update width/space patterns per catalog principles
3. In AA_W_1, what's the purpose of width=0.3 L-pattern and width=0.2 U-pattern? Are these in design rule?
4. Fix them while keeping them
5. Good pattern = same structure as bad but no DRC error; values at value and value+grid
6. Add other types too
7. Fix `*Error* drqaCreateRectWidth: too many arguments (11 expected, 15 given)`
8. Same error at AA_W_1.il line 211
9. In bad pattern, width=0.249 口-pattern error marking layer doesn't cover fully; fix

## Agent Solution
- Fixed cvGood unbound variable (removed orphaned top-level code, restructured procedure)
- Refactored AA_W_1.il to 11 catalog-aligned types with GOOD/BAD/BOUNDARY variants
- wPass=0.0251 (value+grid), wFail=0.0249 (value-grid), wBoundary=0.0250 (exactly)
- Each pattern: drqaCreateRectWidth (11 params: cv, lpp, pt1, pt2, patId, classification,
  testValue, expectedViol, ruleUid, caseUid, branchUid)
- BAD patterns get mark layer (DRC_BAD/mark1): rect for most, polygon for diamond (H),
  full-bbox rect for ring (O)
- Ring via dbLayerAndNot (outer minus inner) — dbCreatePolygon can't do self-intersecting
- Diamond via 45° rotation formula (drqaRotatedVertices)
- Slot pitch 20.0um (catalog §3 isolation)

## Key Files (on hfeg0pkn004:/home/kenwang/.cline/scripts/data/)
- AA_W_1.il (435 lines, 21KB) — main width pattern generator
- M1_S_1.il — space pattern generator (not found at path, renamed)
- drqa_utils_v2.il — shared utility library
- auto_pattern_width.md (10KB) — full documentation with 11 type catalog
- autoPatternFamily/ — pattern family catalog docs

## Offline Redefinition (L2)
Real Virtuoso/OA/Calibre not sandbox-reproducible. The offline-izable core is the
**geometry computation**: given DRC rule parameters (min_value, grid, layer), compute
coordinates for all 11 pattern types × 3 classifications (GOOD/BAD/BOUNDARY), with
proper error-marking geometry. Redefined as stdlib python drc_pattern_geom_gen.py
reading config.json → writing patterns.json. No EDA execution needed.

## Hidden B
config_B: GT.W.1, layer=GT, min_value=0.030, grid=0.0001, rect_len=0.8, gap=15.0,
mark_purpose=mark2. Different rule/layer/value ensures candidate parameterized
correctly (not hardcoding AA.W.1 values).

## Case Structure
- assets/A: config_A.json (AA.W.1), AA_W_1.il (SKILL reference, helper procs),
  prompt.txt, task_brief.md (full 11-type catalog)
- hidden/B: config_B.json (GT.W.1), hidden_manifest.json
- reference: golden_solution.py, check.py (16 conditions a-p), 3 negatives,
  negative_selftest.py, reference_submit.zip
- k=16, domain=layout_virtuoso, level=L2, track=B-synthesized

## Self-Verification
- Golden 16/16 PASS (3-run sha256 consistent: b10ab44491c54becc8484272db84e4c8e83e433ed933d443dce8933864e85189)
- 3 negatives all FAIL (1/16, 3/16, 6/16)
- §4.9 three fakes all FAIL
- End-to-end via reference_submit.zip: 16/16 PASS
- k_check=16 (CONDITIONS list), k_rationale=16 → assertion gate PASS
