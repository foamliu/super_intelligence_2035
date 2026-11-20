# dm280 深读 · PG dummy fill deck dispatch extension (ellawu@10.129.2.14)

**trace**: `1789992388375_dm280.messages.json` (366KB, 35 msgs, 2 real user turns)
**source**: `1793271148453_c6hvf`? no — `1789992388375_dm280`, user=ellawu, host=10.129.2.14, mc=38
**keywords**: calibre:225;cadence:194;drc:188;aether:90;.gds:67;lib.defs:32;techfile:6;verilog:2
**domain**: physical_verify (PG_DUMMY deck dispatch for cxmtG4C process family)
**buildable**: YES (B档 reframe) — trace ends unresolved but intent + source code recoverable

## Real user turns

**U#0** (verbatim, trace-faithful):
```
elif Process.get() == "cxmtG4C" or Process.get() == "cxmtG6_1C2A" or Process.get() == "cxmt10G7" or Process.get() == "cxmtV3" or Process.get() == "cxmtV2B":
        layerMap = f"/apps/imctf/libs/dfii/{Process.get()}/current/layer.map"
        deck = "/proj/shdc/cad/script/PG_DUMMY/cxmtG4C/G4C_AA_PG_dummy_fill_for_Logic.rule"
```
User pasted the cxmtG4C-family dispatch snippet from `genPGDummy_for_Logic.py` line 181-183.

**U#12** (verbatim, trace-faithful, Chinese pinyin with typos):
```
duishuyu cxmtG4C xiangmude drgqx rangtadexunxing follow drvsa
```
Parse: 「对属于 cxmtG4C 项目的 drgqx 让它的运行 follow drvsa」
= "For cxmtG4C process's project 'drgqx', make its execution follow 'drvsa'."

## Assistant behavior (trace)

- search_codebase for "cxmtG4C|layerMap.*deck" → found 20 results in 15 files; the snippet appears in 3 files: `genPGDummy_for_Logic.py`, `gen_preAA_G5_CIP.py`, `gen_preAA_G5_CIP_final.py` (all line 181).
- read_files `genPGDummy_for_Logic.py:170-200` → got the full G4PLUS/G5/G4C dispatch block.
- read_files `genPGDummy_for_Logic.py:130-250` → got `specialProjList = ["dejoa","ddjoc"]` (line 166) and the `if projName in specialProjList: sed special_project No→Yes` mechanism (lines 425, 488).
- read_files `genPGDummy_for_Logic.py:1-100` → got revision history (v2.0 "support G4C/drgpa", v2.4 "support cxmtG6_1C2A/drgpx", v2.6 "add specialProjList to divide G4B and G4B_CIP", v3.2 "update specialProjList add ddjoc").
- search_codebase for "drvsa", "drv", "drgqx" → **No results found**. Neither "drvsa" nor "drgqx" appear anywhere in the 15-file codebase.
- read_files `genPGDummy_for_Logic.py:400-500` → got the `if projName in specialProjList: sed ...` special_project flag injection logic.
- read_files `IMCutGenPGDummy_for_Logic.py` → got the skill version with `processList` (13 supported processes).
- ask_question to clarify "drvsa" / "drgqx" → **timed out** (no user response).
- Final assistant text: "I cannot find 'drgqx' or 'drvsa' anywhere in the existing code. ... I can see the clear pattern of the code and can make a reasonable interpretation." → **trace ends without resolution**.

## Recoverable source code (from trace tool_results)

**genPGDummy_for_Logic.py key blocks**:
- Line 58: `processList = ["cxmt10G4plus","cxmtG4B_CIP","cxmtG4W","cxmt10G5","cxmtG5_CIP","cxmt10G6","cxmt10G4plus_DDR","cxmtG4C","cxmt10G4plus_HBM","cxmtG6_1C2A","cxmt10G7","cxmtV3","cxmtV2B"]` (13 supported processes)
- Line 146 comment: `#project_list = ["ddcpb","drjpa","ddjoc","drcqa","ddjna","drgpa","idjoa","dhjob"]` (historical project list — note drgpa is the existing cxmtG4C project)
- Line 166: `specialProjList = ["dejoa","ddjoc"]` (projects that get `special_project=Yes` in deck)
- Lines 169-183: process→(layerMap, deck) dispatch
  - G4PLUS_GROUP = ["cxmt10G4plus","cxmtG4B_CIP","cxmtG4W","cxmt10G6","cxmt10G4plus_DDR","cxmt10G4plus_HBM"] → layerMap=`/apps/imctf/libs/dfii/cxmt10G4plus/current/layer.map`, deck=`/proj/shdc/cad/script/PG_DUMMY/cxmtG4B_CIP/G4plus_AA_PG_dummy_fill_for_Logic.rule`
  - G5_GROUP = ["cxmt10G5","cxmtG5_CIP"] → layerMap=`/apps/imctf/libs/dfii/cxmt10G5/current/layer.map`, deck=`/proj/shdc/cad/script/PG_DUMMY/cxmtG5/G5_AA_PG_dummy_fill_for_Logic.rule`
  - G4C_GROUP = ["cxmtG4C","cxmtG6_1C2A","cxmt10G7","cxmtV3","cxmtV2B"] → layerMap=f-string `/apps/imctf/libs/dfii/{process}/current/layer.map`, deck=`/proj/shdc/cad/script/PG_DUMMY/cxmtG4C/G4C_AA_PG_dummy_fill_for_Logic.rule`
- Lines 194-199: processname_new + deck_STI
  - DDR/HBM alias: `if process in ["cxmt10G4plus_DDR","cxmt10G4plus_HBM"]: processname_new = "cxmt10G4plus"` else `processname_new = process`
  - `deck_STI = f"/apps/imctf/runset/calibre/{processname_new}/current/{project}/runset/calibreSTIcmp.rule"`
- Lines 247-251: preAA_rule_template per process
  - G5_CIP → `rule/gen_preAA_G5_CIP.rule`; G4C → `rule/gen_preAA_G4C.rule`; else default
- Line 326: precision = "10000" for ["cxmt10G5","cxmtG5_CIP","cxmtG4C","cxmtG6_1C2A","cxmt10G7","cxmtV3","cxmtV2B"], else "1000"
- Lines 425, 488: `if projName in specialProjList: sed -i 's,set special_project No,set special_project Yes,' deckName`

## B档 reframe (case `EDA-Eval-DesignFlow-PGDeckDispatch-001`)

**Why not A档**: trace-faithful A档 requires trace-end gold (user-accepted result); trace ends unresolved (assistant asked clarification, timed out, gave up). No gold.

**B档 reframe**: extract the dispatch logic into a clean Python function. The user's intent ("drgqx follows drvsa") is interpreted as: add "drgqx" to `specialProjList` so it gets `special_project=Yes` treatment (the same mechanism dejoa/ddjoc use). "drvsa" is interpreted as a reference to the specialProjList mechanism (since drvsa doesn't exist in codebase, but specialProjList is the only "follow a pattern" mechanism for projects).

**Task**: SUT writes `pg_deck_dispatch.py` that (1) loads a dispatch table JSON (path=argv[1]), (2) resolves dispatch for (process, project) given as argv[2]/argv[3], (3) **adds "drgqx" to the table's specialProjList** (the extension — drgqx follows the special_project=Yes pattern).

**Visible A** (`dispatch_table_A.json`): the current dispatch table with A's process groups + A's specialProjList=["dejoa","ddjoc"] + A's deck paths. Does NOT include drgqx.

**Hidden B** (base64 inline in check.py): different process names in groups, different specialProjList base (e.g., ["drvsa","xxproj"]), different deck path roots. SUT's solution must work on B by reading B's table and adding "drgqx" to B's specialProjList.

**14 assertions (a-n)**: zip valid; py_compile; run B exit 0 + JSON; layerMap for G4PLUS/G5/G4C groups; deck per group; processname_new DDR/HBM alias; deck_STI f-string; preAA template; precision; special_project=Yes for specialProjList+drgqx; special_project=No otherwise; unsupported process error.

**Anti-hardcode**: B differs from A in process names, specialProjList base, deck path roots, project names.

**Negatives (4)**: empty (→a/b), print_only (→c), hardcode_a (→d-n), no_extension (→m — drgqx not added).

**Domain**: physical_verify (PG_DUMMY deck dispatch is a physical verification step — Calibre DRC deck selection for dummy fill).
**Layer**: L1 (offline Python, no EDA tool execution).
**档**: B (synthesized from trace; trace-faithful A档 gold missing).
**子型**: pg-dummy-deck-dispatch-extension.
