# Deepread: 1795245585227_iwrr4 — Calibre DRC UT Isolation Check

## Trace Source
- **session**: 1795245585227_iwrr4
- **user**: xydou
- **host**: hfeg0pkn003 (10.129.2.12)
- **match_count**: 483
- **scan**: ssh_eda_search_20261122_172249
- **keywords**: calibre:1460;drc:1009;.gds:182;pyaether:178;cellview:146;aether:127;dbshape:68;dbget:55

## Real Task Summary
User asked agent to learn the CXMT G4C LP Calibre DRC UT check rule set (`calibreDRC_UTCheck.rule`, 3821 lines + 5 macro files), then write a **Calibre DRC UT include script** (SVRF format) that checks isolation uniformity around AT4 resistors:

1. **Check_AT4RES_ISO_dist_m**: Distance from PG_DUMMY outer edge → AT4_PCH inner edge must be ≤ 0.4um in every orthogonal direction (up/down/left/right)
2. **Check_AT4RES_ISO_symTB_m**: Top distance must equal bottom distance
3. **Check_AT4RES_ISO_symLR_m**: Left distance must equal right distance

Key iterations:
- v0.0.1: Initial 4um threshold, resistor-edge → PCH-edge measurement
- v0.0.2: Verified with Calibre v2020.1_36.18 on synthetic testcases; fixed chained-NOT syntax bug
- Threshold changed to 0.4um per user request
- Measurement path refined: PG_DUMMY outer edge → AT4_PCH inner edge (not resistor edge)
- Highlight changed to rectangle between PG_DUMMY and AT4_PCH inner edge, merged per side
- v0.0.6 (final): All layer constructions deferred INTO rule blocks for Calibre INCLUDE window compatibility (avoids "undefined layer" and "duplicate layer" errors)

## Key SVRF Techniques Used
- `VARIABLE` for tunable thresholds (_AT4RES_gap_max_=0.4, _AT4RES_win_=5.0)
- `COPY` tech layers (AT4_resistance, AT4_PCH, PG_DUMMY) inside rule blocks
- `GROW TOP/BOTTOM/LEFT/RIGHT BY` for directional measurement columns
- Boolean ops: `AND`, `NOT` (split into two-step assignments for Calibre syntax), `OR`
- `LENGTH (ANGLE layer == 90/0)` for edge length measurement (vertical=90, horizontal=0)
- `DFM PROPERTY SELECT SECONDARY ... OVERLAP SELECT ... [-= expr]` for per-frame MAX/MIN symmetry comparison
- `MERGE (OR ...)` for unified output highlight
- `GROW ... LEFT BY x RIGHT BY x` to expand highlight into full-width rectangle per side

## Final Deliverable
A single `.rule` file (SVRF text) containing:
- 2 VARIABLE declarations
- 3 rule blocks (dist_m, symTB_m, symLR_m)
- Each block: layer COPY → directional columns → gap regions → mid regions (dummy-to-PCH) → edge measurement → violation filter → merged rectangle highlight

## Verification
- Synthetic test matrix 12/12: res_ok (0 violations), res_tb_bad (dist+symTB), res_dist_bad (dist only), res_lr_bad (symLR only)
- Real layout test: dist=8, symTB=18, symLR=4 violations on `/proj/ddgoa/V0/workdir/xydou/test/test/layout/layout.oa`

## Domain Classification
- **Shard C**: physical_verify (Calibre DRC rule writing)
- C-dominant keywords: calibre, drc, .gds, pyaether, aether
- No cross-shard concern (no waveview/innovus/synthesis dominance)
