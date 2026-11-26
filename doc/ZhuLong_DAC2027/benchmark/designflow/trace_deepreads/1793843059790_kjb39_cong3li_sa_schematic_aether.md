# Deepread: 1793843059790_kjb39 (cong3li @ hfeg0pkn004) — SA Schematic Aether

- **sid**: 1793843059790_kjb39  | **user**: cong3li | **host**: hfeg0pkn004 (10.129.2.13) / hfeg0plg72 (10.129.8.110)
- **mc**: 205 | **keywords**: aether:815;pyaether:586;schematic:434;netlist:235;pdk:90;verilog:87;cellview:85;dbget:65
- **domain**: layout_aether (pyAether schematic construction)
- **trace shape**: 137 messages, 1 user turn (conceptual Q → build request), assistant = 22 list_allowed_files + 23 read_files + 11 editor + 9 RAG search_apis + 3 get_api_details + 1 SandBox run_code + 3 run_approved_command + 3 search_codebase
- **sandbox state**: pyAether bridge (SandBox_MCP_Server) NOT running (Connection refused) — agent could not execute build, wrote script + netlist as static deliverables instead

## Real task (verbatim first user msg)
> tWL是测量连SWD的那条WL的50%电压到SWD远端50%电压的时间还是在离SWD最近的那个MAT的WL50%电压到远端WL50%电压的时间

User then asked whether the agent can build circuits in EDA; picked **Aether/pyAether**. The evolved task: write a pyAether script that builds a **DRAM latch-type bitline Sense Amplifier (SA)** schematic in Aether.

## Deliverable (what the agent produced)
1. **`sa_netlist.sp`** — SPICE subckt `SA BLT BLC SAP SAN CSB DLT DLC`:
   - PMOS latch: MP1 (d=BLT g=BLC s=SAP), MP2 (d=BLC g=BLT s=SAP)
   - NMOS latch: MN1 (d=BLT g=BLC s=SAN), MN2 (d=BLC g=BLT s=SAN)
   - Column-select pass gates: MN3 (d=DLT g=CSB s=BLT), MN4 (d=DLC g=CSB s=BLC)
   - W=1u L=0.18u M=1
2. **`build_sa_schematic.py`** — pyAether script:
   - CONFIG block: LIB="MY_LIB", CELL="SA", VIEW="schematic", TECHLIB/PDK_LIB/NCELL/PCELL="" (auto-discover), NVIEW/PVIEW="symbol"
   - `discover_cell()` — scans dbGetAllLibs/dbGetAllCells/dbAllCellViews for nch/nmos/n18 & pch/pmos/p18
   - `place()` = dbCrtInst; `add_pin()` = dbCrtSymbolPin; `wire()` = dbCrtSchWire
   - `main()` — emyInitAether("-adv"); discover N/P; dbCreateLib if missing; dbNewCV/dbOpenCV(MY_LIB, SA, schematic); place 6 insts:
     - MP1@(0,8) MP2@(4,8) [PMOS]; MN1@(0,2) MN2@(4,2) [NMOS]; MN3@(0,-2) MN4@(4,-2) [NMOS]
   - `main2(cv)` — add 7 pins: BLT(-8,5) BLC(-8,3) DLT(14,5) DLC(14,3) [IO]; CSB(14,-2) SAP(2,14) SAN(2,-6) [input]
   - `main3(cv)` — 13 dbCrtSchWire calls: BLT→MP1.d, BLC→MP2.d, cross-couple (MP1.g↔BLC, MP2.g↔BLT), SAP rail, shared BLT/BLC, N-latch cross, col-select gates=CSB, SAN rail
   - `__main__` — run main+main2+main3, aeSaveFile (fallback cv.save)

## Why this is a good design_flow case (B-synthesized, L1)
- **Produce deliverable** (a runnable pyAether schematic-builder script) — not pure Q&A
- **Checkable by static analysis** (L1): the script's structure is verifiable without a live Aether bridge (which the trace itself couldn't start) → parse the .py for dbCrtInst/dbCrtSymbolPin/dbCrtSchWire calls, inst names, pin names/dirs, cross-coupling wire pattern, save call, CONFIG parameterization
- **Hidden B**: script must be parameterized (CONFIG block) so substituting B's LIB/CELL/NCELL/PCELL still yields a structurally valid builder; a script that hardcodes "MY_LIB"/"SA" in the body fails B
- **Diversification**: r383=physical_verify, r384=pg_layout → r385=layout_aether (lowest-coverage domain, only 10/71 fresh per r382 note)

## Case plan
- case_id: EDA-Eval-DesignFlow-SASchematicAether-001
- domain: layout_aether | track: B-synthesized | level: L1
- k=12 (a-l): zip-has-script / emyInitAether / create+open CV / 6 dbCrtInst {MP1..MN4} / PMOS-vs-NMOS cell split / 7 pins {BLT,BLC,SAP,SAN,CSB,DLT,DLC} / pin dirs / dbCrtSchWire wiring≥8 / cross-coupling / save call / CONFIG parameterization / hidden-B substitution generality
- negatives: empty-shell / print-only stub / ref-minus-core (drop dbCrtInst+dbCrtSymbolPin+dbCrtSchWire)
