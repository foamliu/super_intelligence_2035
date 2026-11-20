# Deepread: 1792458709086_461oe — pyAether Workflow Documentation (整理 flow)

**Session**: `1792458709086_461oe.messages.json` (subdir `~/.cline/data/sessions/1792458709086_461oe/`)
**User**: ellawu @ 10.129.2.14
**Match count**: 24 (drc:157 dbopencv:67 — but core task is layout_aether workflow doc)
**Model**: GLM-5.2
**Messages**: 30 total
**Date**: 2026-11-19 (scout round r818)
**Domain filed**: layout_aether (shard C)

## User Intent (U#0, idx=0, verbatim)

```
<user_input>整理flow</user_input>
```

With an attached file `IMCutGenPGDummy_for_Stdcell.py` (24342 bytes / 532 lines) uploaded to
`~/.cline/data/sessions/1792458709086_461oe/uploads/`.

**Intent type**: produce-task / documentation. User wants the workflow of an existing pyAether
script "organized" (整理flow) into a readable document. Not a code-change request — a
document-generation / flow-explanation request.

## The Script (IMCutGenPGDummy_for_Stdcell.py)

A SKILL→pyAether converted standard-cell AA/PG DUMMY generation tool:

- **GUI builder** `IMCutGenAAPGDummy_for_Stdcel_GUI()`: hiCreateComboField (lib/cell),
  hiCreateFileSelectorField (select/skip cell lists), hiCreateStringField (streamIn lib, run dir),
  hiCreateAppForm + hiDisplayForm. Callback → `StdCellAdd_AADummy2_PGDummy`.
- **Main handler** `StdCellAdd_AADummy2_PGDummy(myForm)`: selects DRC rule deck by process
  (cxmt10G4plus/G4W/G4C/G5/V2B…), iterates selected cells, per-cell pipeline:
  `GetCellIdList → DeleteAddedDummy → RunStreamOutGDS → RunDRC → RunStreamInGDS → AddPropForCell`
  then `dbCrtInst` + `dbSmashInst` to merge dummy back.
- **SKILL-compat helpers** (from `ut.IMCutGlobal`): `strcat` (18×), `shell` (11×), `parseString` (2×),
  `car`/`last`/`nth` (1× each), `getWorkingDir` (2×), `printf` (2×), `leGlobalVariables` (attr access).
- **pyAether APIs**: `ae.aeGetCurDesign`, `ae.dbGetAllLibs`, `ae.dmGetObj`, `ae.dbOpenCV`,
  `ae.dbCrtInst`, `ae.dbSmashInst`, `ae.dbSaveCV`, `ae.dbCrtProp`, `ae.dbDelete`, `ae.dbValidP`,
  `ae.dbCreateLib`, `ae.aeError`, `ae.aeRedraw`; `hiCreate*`/`hiDisplayForm` (GUI).
- **String constants**: `"AT4.DUMMY2"` / `"PG.DUMMY"` lpp tags, `"Stdcel_Fill_AADummy2"` /
  `"Stdcel_Fill_PGDummy"` removeFlag props, `"auto_pgdm_std"` streamIn lib.
- 9 top-level defs, 4 global vars (StrmInLib/deck/layerMap/objMap).

## Assistant Workflow (msg 1–29)

1. Reads the attached script (msgs 1–8): identifies it as a pyAether AA/PG DUMMY generator,
   notes the GUI + per-cell pipeline structure.
2. U#24 (idx 24) user restates: 「梳理并文档化工作流」 — confirming the documentation intent.
3. Assistant produces **msg 29 = GOLD answer**: a 7494-char workflow markdown document with:
   - top-level function list (9 defs) with one-line role each
   - call graph (who-calls-whom among module-local defs)
   - SKILL-compat helper usage table (strcat/shell/parseString/car/last/nth/getWorkingDir/printf)
   - pyAether API call inventory
   - 6-step per-cell process pipeline (GetCellIdList→DeleteAddedDummy→RunStreamOutGDS→RunDRC→
     RunStreamInGDS→AddPropForCell)
   - 5-step detailed per-cell flow narrative (stream out → DRC → stream in → tag props → smash back)

## Reframe Decision (r818, B-synthesized)

The A档 gold (free-text workflow markdown) has **no hard ≥8 assertions** — it's a documentation
task whose quality is subjective. Reframed to a **pyAether workflow analyzer** (B档 synthesized):

- **Task**: build `pyaether_workflow_analyzer.py` that statically (`ast`) extracts a structured
  JSON "workflow document" from any pyAether-style script.
- **8 output keys**: top_level_functions / entry_function / call_graph / global_variables /
  skill_style_funcs / external_imports / process_steps / pyaether_api_calls.
- **Visible A** = cleaned `IMCutGenPGDummy_for_Stdcell.py` (~290 lines, 9 defs, preserves all
  SKILL helpers + pyAether APIs).
- **Hidden B** = synthesized `MyMetalFillCleanup` metal-fill cleanup script (8 defs, different
  function names / call graph / skill-func counts / API set) — structurally distinct, anti-hardcode.
- **k_check = 16** independent assertions (a–p): zip/compile/stdlib, CLI contract, B run + 8 keys,
  each of the 8 output fields exact-match, cross-input A guard, anti-hardcode (A/B distinct +
  no A-exclusive literals in B output), determinism (2× byte-identical), missing-input exit≠0.
- **§4.9 三假**: _neg_empty (FAIL b), _neg_print_only (FAIL c), _neg_core_deleted (FAIL d) +
  _neg_hardcode_a (FAIL d/p). All FAIL verified.

## Case Record

- **case-id**: `EDA-Eval-DesignFlow-PyaetherWorkflowAnalyzer-001`
- **file**: `cases/C/EDA-Eval-DesignFlow-PyaetherWorkflowAnalyzer-001.json`
- **ledger**: `trace_ledger_C.tsv` line 1311 → status `case`, case-id filed, domain `layout_aether`
- **self-verify**: ref PASS 16/16; all 4 negatives FAIL; THREE_FAKE_FAIL=1; determinism md5 match.
