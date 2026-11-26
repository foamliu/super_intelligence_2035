# Deepread r254 — genvz (adaml) — emy2netlist CDL extraction

- session: `1793857741122_genvz.messages.json`
- user: adaml @ hfeg0pkn002 (10.129.2.11), mc=183, agent=lead
- domain: layout_aether (Aether EDA — emy2netlist CLI CDL extraction)
- NEW user adaml (first case in shard C)
- round: 254, case-id: `EDA-Eval-DesignFlow-EmyCdlNetlistExtract-001`

## User real intent (U#23, proposing need, no root cause given)

> "[calibre-lvs] /proj/drvsa/V0/workdir/kaixuanx/4PGen_Sleep/Idle_enable 用API接口 emy2netlist试试看抽取上面这个cell的CDL，这次是eather的EDA"

User wants to use the Aether `emy2netlist` API/CLI to extract a CDL netlist for cell `4PGen_Sleep/Idle_enable`. No root cause / fix proposed — pure proposing-need → A/B档合格 seed.

## Trace flow (deepread via probe2.py/probe3.py)

1. agent activated eda_agent skill → RAG search `search_apis(query="emy2netlist", host="aether")` → no direct hit
2. grep'd `/apps/imctf/cad/init/settings_aether/python_ae/` → found `emy2netlist` CLI referenced in `cxmt_schematic_batchGenerateCDLNetlist.py`
3. verified `emy2netlist` binary at `/apps/empyrean/tools/aether_new/bin/emy2netlist`; `AETHER_HOME=/apps/empyrean/tools/aether_new/tools/aether`
4. ran in `/proj/drvsa/V0/workdir/adaml/emy2list_Idle_enable`:
   ```
   emy2netlist 4PGen_Sleep Idle_enable schematic \
       -t cdl -ntlviewlist auCdl schematic -ntlstoplist auCdl \
       -o Idle_enable.cdl -resThrhd 2000 -pow VDD! -gnd GND! \
       -ignoreCheck -pin -cdlIncFile empty_device.spi
   ```
5. 3 pitfalls hit & resolved:
   - (1) `emy2netlist` reads `lib.defs` from cwd — auto-creates a default if missing → library not found
   - (2) must `INCLUDE /proj/.../lib.defs` so TECHLIB/basic (MOS masters ptn_lv_pc60/ntn_lv_pc60) resolve → else "Unbound instance"
   - (3) `-ignoreCheck` skips precheck but "Unbound instance" is a HARD error still requiring the lib.defs fix
6. RC=0, stdout: `Successfully exported design 4PGen_Sleep/Idle_enable/schematic!`
7. CDL output (2439 bytes):
   ```
   .SUBCKT Idle_enable DLLLock Idle IdleB IdleEN LMDone ReadEN VDD VSS
   *.PININFO ...
   XI0 .../nand_x1 ...
   XI1 .../nor_x1 ...
   XI2 .../nand_x2 ...
   XI3 .../inv_x2 ...
   XM0 ... ptn_lv_pc60 ...
   XM1 ... ntn_lv_pc60 ...
   .ENDS
   ```

## B-synthesized decision

Real cell `4PGen_Sleep/Idle_enable` not accessible from e0031982's pyAether sandbox (`dbGetLibCells` returned None for basic/TECHLIB/test_lib_ae). So built a parameterized offline CDL extractor grounded on the trace's `emy2netlist` command + 3 documented pitfalls, feeding synthesized schematic-hierarchy JSON dumps.

## Case design

- script: `emy_cdl_extract.py <hierarchy.json> -o <out.cdl>` (stdlib only)
- input JSON schema: `{cell, lib, view, options, lib_defs:{cwd,includes,libraries}, include_files:{path:{libraries}}, cells:{name:{pins,pininfo,instances:[{name,nets,master,lib}]}}}`
- behaviours grounded on 3 pitfalls:
  - resolve lib.defs INCLUDE chain (cwd libraries + each include's libraries merged)
  - top cell's lib must be in resolved map (else "Library not found")
  - `ignoreCheck=false` → precheck every instance master exists in cells dict; `true` → skip precheck (MOS masters not in cells still emitted)
  - emit `.INCLUDE <path>` for each resolved include
  - emit `.SUBCKT <cell> <pins>` + `*.PININFO` + instance lines `<name> <nets> <master>` + `.ENDS`
  - "Unbound instance" hard error: instance lib not in resolved map → non-zero exit (NOT skipped by ignoreCheck)
  - stdout summary JSON
- A (visible): Idle_enable hierarchy (8 pin / 6 instance / 1 include / 2 libs via INCLUDE)
- hidden B: Ldo_top (6 pin / 7 instance / different libs/instances/include chain — structurally different)
- hidden B2: Buf_x1 degenerate (1 cell / 0 instance / 0 include)
- hidden B3: EMPTY (0 pin / 0 instance)
- hidden B4: Bad_top (Unbound instance — lib 'ghost_lib' not in resolved map → must non-zero exit with 'Unbound')

## Self-verification

- golden self-test: 16/16 PASS ✓
- negative_selftest: 5/5 all FAIL ✓ (empty_shell→a, print_expected→d/e/f/h/m, hardcoded_A→d/e/f/h/i/m, core_deleted→h/i, stub_no_parse→c/d/e/f/g/h)
- §4.9 three-fake-submit (empty/print-expected/core-deleted): all FAIL ✓
- 3-seed determinism: sha256(output_B) stable ✓
- test field == disk check.py byte-equal ✓ (11614B)
- k_rationale=16=k_check(a-p)≥8 ✓
- stdlib only (no forbidden imports) ✓

## Ledger

- genvz marked case (layout_aether) in trace_ledger_C.tsv
- jsonl_C: 243 → 244 lines (244/1511 = 16.2% trace coverage)
- DEBT: 0
