# Deepread: 1791790886127_58vqx (xinqiaoz / hfeg0pkn005)

## Session Metadata
- **sid**: 1791790886127_58vqx
- **user**: xinqiaoz
- **host**: hfeg0pkn005 (10.129.2.14)
- **mc**: 875
- **tools**: 1006 calibre, 1 virtuoso
- **keywords**: pdk:3140; drc:2078; calibre:1456; .gds:154; gdsii:23; lvs:22; skipper:9; rtl:3
- **nmsgs**: 472, 245 tool_use calls (107 editor, 61 read_files, 46 run_approved_command, 25 list_allowed_files)

## User Intent (chronological)
1. Read handoff prompt → understand PDK QA system background
2. Explore test data dir `/home/pdk/peiyaoz/00_Dummy/deck/DYT4E_WHCFP_LHCRP_DHCFP/` (read-only)
3. **Main task**: Test two existing checks (DummySyntaxCheck, LayerDuplicatesCheck):
   - Create test cases (good + bad) in `tests/` dir (separate from existing DRC tests)
   - Good case + bad case for each check, full verification
   - Test data files can be derived from existing deck files with minor tweaks
   - Run `DummyQa.py` → keep generated report files for review
   - Source deck dir is read-only: copy files out before modifying
4. Don't modify `dummySyntaxCheck` source code directly; use monkey-patch in test scripts
5. Report files → project `.tmp/` dir, not `/tmp`
6. Generate HANDOFF document for session continuity

## Key Files in PDK QA System
- `DUMMY/DummyQa.py` — main QA orchestrator
- `DUMMY/text/DummySyntaxCheck.py` — SVRF syntax checker (class DummySyntaxCheck)
- `DUMMY/text/LayerDuplicatesCheck.py` — layer duplicates checker (class LayerDuplicatesCheck)
- `DRC/text/DrcSyntaxCheck.py` — DRC syntax checker (reference for DRC module)
- `DRC/tests/drcSyntax/run_test.py` — existing DRC test pattern (reference)

## Test Data Created
- `tests/data/good_syntax.svrf` — valid SVRF (passes syntax check)
- `tests/data/bad_syntax.svrf` — malformed SVRF (syntax errors)
- `tests/data/good_layer.svrf` — no layer conflicts
- `tests/data/bad_layer.svrf` — 6 conflict types (layerMap2_1, layerMap1_2, layerTextMap2_1, nameToLayer, etc.)
- `tests/data/config.ini` — test configuration
- `tests/data/many_switches.svrf` — additional edge case
- `tests/data/setlayer_test.svrf` — for setLayerInfo override test

## Test Scripts Created
- `tests/test_env.py` — shared environment (path resolution, result printing)
- `tests/syntaxCheck/run_test.py` — DummySyntaxCheck test suite (good/bad + setLayerInfo)
- `tests/layerDuplicatesCheck/run_test.py` — LayerDuplicatesCheck test suite (good/bad + setLayerInfo override)
- `tests/run_all_tests.py` — master runner
- `tests/index.md` — test documentation

## Key Decisions
- Monkey-patch approach: don't modify source code, patch in test scripts
- Test data based on real PDK deck files (DYT4E_WHCFP_LHCRP_DHCFP)
- Reports to `.tmp/` directory (not `/tmp`)
- LayerDuplicatesCheck has `setLayerInfo()` API for pre-parsed data injection

## Synthesized Case (B档)
- **task_id**: EDA-Eval-DesignFlow-DrcSyntaxTest-001
- **domain**: pnr_signoff
- **track**: B (synthesized from trace, simplified PDK QA system)
- **A-faithful elements**: xinqiaoz user, PDK QA Dummy module, DummySyntaxCheck + LayerDuplicatesCheck, good/bad test case pattern, monkey-patch discipline, report generation, SVRF deck format
- **Simplifications**: Self-contained pdk_qa system (no DrcInfo/DRC module dependency), simplified SVRF format, 3 conflict types instead of 6, no SSH to remote environment
- **Hidden B**: Different deck (frame-level vs chip-level) with different errors for cross-input guard
- **12 check assertions**: structure, test data, scripts, good/bad pass/fail, cross-input guard, report, source integrity
