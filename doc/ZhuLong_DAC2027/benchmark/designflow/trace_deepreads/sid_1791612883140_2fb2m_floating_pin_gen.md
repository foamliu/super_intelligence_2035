# Deepread: 1791612883140_2fb2m — Floating Pin Generation (SKILL layout_virtuoso)

## Trace meta
- **session**: 1791612883140_2fb2m.messages.json (ellawu @ hfeg0pkn005, mc=130)
- **size**: 130 msgs, ~452KB
- **date**: 2026-10-10
- **domain**: layout_virtuoso (SKILL script modification)
- **track**: A-档 faithful (single pure-intent user turn)
- **L-level**: L1-boundary (static SKILL source analysis, no live Virtuoso needed)

## User intent (verbatim, A-档 seed)
USER[0] (the ONLY user turn):
> 在这个脚本的基础上设计浮pin的功能（除了vcc vss）
>
> --- Attached files ---
> [Attached file: cxmt_autoPR_generatePortText.il → uploads/cxmt_autoPR_generatePortText.il]

Pure intent — user wants floating-pin (浮pin) support added to the attached SKILL script, excluding VCC/VSS power pins. No root-cause/fix given. Perfect A-档 seed.

## Original script analysis (asset A = uploads/cxmt_autoPR_generatePortText.il, 391 lines, 21178 bytes)
`cxmt_autoPR_generatePortText.il` — CXMT Memory Tech auto-PR port-text generator:
- **`cxmt_generatePortText(@optional laycvId appDBoxFlag selInstNameList)`** — main entry. Opens schematic (schcvId), traces top-level terminals via `schTraceNetToConn` to build `pinTerminal_table` (maps `instName#pinName` → terminalName). Splits instance names (`<...>` bus expansion). Calls `cxmt_generatePortTextCell`.
- **`cxmt_generatePortTextInSelectedInst(@optional appDBoxFlag)`** — wrapper: uses geGetSelSet() to get selected instances, calls main with selInstNameList.
- **`cxmt_autoPR_generatePortText_SpltInst(instNameList)`** — bus-name splitter via dbProduceMemName.
- **`cxmt_generatePortTextCell(laycvId pinTerminal_table instNameList)`** — the core. For each instance, finds label-type pins (labelList_org = shapes with objType=="label" && purpose=="pin") and shape-type pins (hierPinList = shapes with pin!=nil or objType!="label" && purpose=="pin"):
  - **Label-type pins**: if `updatepinTerminal_table[instName#labelName]` exists (connected) → dbCreateLabel at labelLocation with project-specific font sizing (case projectName_autoPR: dqrmb=0.1, degpa=0.01, dqpoa=0.2, drgpa=0.02, default=0.05; ADIE_PERI cell uses orient, non-ADIE uses "R90"). Dedup via bBoxMapLabel_table. **Pins NOT in table (floating) are SILENTLY SKIPPED.**
  - **Shape-type pins (hierPinList)**: if connected → leCreatePin (top-level pin) + dbCreateLabel + dbCreateTextDisplay (project-specific: drgpa=0.02, degpa=0.01, decoa=0.04, default=0.04). **Floating shape pins SILENTLY SKIPPED.**
- **`schTraceNetToConn(cvId netName pinTerminal_table visitedCellList topTerm)`** — recursive net tracer (loads .simrc.cdl for HNL user-short, walks sigId~>netAnalogs~>memInstTerms, maps inst terms to top terminal names).

## Real product (gold standard = /home/ellawu/Desktop/cxmt_autoPR_generatePortText.il, 477 lines, 26567 bytes)
Assistant modified the script (after extensive editor-tool struggles with size limits) adding floating-pin support. Final summary (msg 129):

1. **New global `floatingPinSkipList = list("VCC" "VSS")`** (line 38) — pin names NOT getting floating labels; case-insensitive; extensible.
2. **New helper `cxmt_isFloatingPinSkipped(pinName)`** (lines 45-55) — iterates floatingPinSkipList, `upperCase()` comparison, returns t/nil.
3. **`cxmt_generatePortText`** — added `(floatingPinFlag t)` optional param; passes to cell proc.
4. **`cxmt_generatePortTextInSelectedInst`** — added `(floatingPinFlag t)` param; passes through.
5. **`cxmt_generatePortTextCell`** — added `(floatingPinFlag t)` param + new locals (floatingPinName, keyName, pinTermName); refactored strcat keys into `keyName` var; added two new `elseif` branches:
   - **Label-type floating pin** (elseif `floatingPinFlag && !cxmt_isFloatingPinSkipped(labelId~>theLabel)`): creates dbCreateLabel with **original pin name** (floatingPinName = labelId~>theLabel, NOT from updatepinTerminal_table), project-specific font sizing (same dqrmb/degpa/dqpoa/drgpa/default), ADIE_PERI vs non-ADIE_PERI orientation, dedup via bBoxMapLabel_table + createdTextList.
   - **Shape-type floating pin** (elseif `floatingPinFlag && pinTermName && !cxmt_isFloatingPinSkipped(pinTermName)`): creates dbCreateLabel with original pin name, **NO leCreatePin** (no top-level pin — floating/unconnected), simpler font sizing (dqrmb/dqpoa/default), dedup via createdTextList + bBoxMapLabel_table.

### Backward compatibility
- floatingPinFlag defaults to `t` (enabled) — existing callers get new behavior.
- Disable via `cxmt_generatePortText(?floatingPinFlag nil)`.
- Connected-pin logic fully preserved (the if-branch for updatepinTerminal_table hits unchanged).

## L1-boundary design
Candidate = modified SKILL .il script (SUT modifies asset A, submits in submit.zip). check.py does STATIC analysis of the submitted .il (no live Virtuoso). Hidden B = renamed-identifier variant of A (procedures: cxmtGenPortTxtB/cxmtGenPortTxtCellB/..., projects: projQb/projEb/projPb/projRb) for anti-hardcoding (submitted must not contain B names; floating-pin logic must use generic object attributes).

## 14 assertions (a–n)
①zip+.il≥400 lines valid text ②floatingPinSkipList defined with VCC/VSS ③cxmt_isFloatingPinSkipped helper with upperCase case-insensitive ④cxmt_generatePortText has floatingPinFlag param default t ⑤cxmt_generatePortTextCell has floatingPinFlag param default t ⑥label-type floating branch (elseif floatingPinFlag && !skipped, dbCreateLabel with original pin name) ⑦shape-type floating branch (elseif floatingPinFlag && pinTermName && !skipped, dbCreateLabel, NO leCreatePin) ⑧project-specific font sizing in floating branches (≥3 project variants) ⑨no leCreatePin in floating shape branch ⑩dedup via bBoxMapLabel_table/createdTextList in floating branches ⑪generic attributes (labelId~>theLabel / pinTermName, not hardcoded pin literals) ⑫anti-leak: submitted does NOT contain B's unique identifiers ⑬connected-pin logic preserved (updatepinTerminal_table if-branch still present) ⑭floatingPinFlag default t + balanced structure (let/prog, no syntax breakage)
