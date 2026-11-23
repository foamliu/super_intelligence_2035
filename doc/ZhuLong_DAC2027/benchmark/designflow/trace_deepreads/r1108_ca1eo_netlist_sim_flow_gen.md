# r1108 Deepread: ca1eo (t0003060@hfeg0pkn001/mc95/spice_sim) → NetlistSimFlowGenProduce-001

## Trace Source
- session: 1795162772386_ca1eo
- user: t0003060, host: hfeg0pkn001, match_count: 95
- keywords: spice/finesim/simulator (scan 20261123_064315)
- 61 messages, 242KB

## User Intent
U0: "写一个抽网表和提交仿真的代码 标清楚每个步骤的细节，注意不要让我自主选择方案，一切按照你的想法"
(Write code for netlist extraction + simulation submission, mark each step's details, don't make me choose, do it your way)

## Assistant Flow
1. Explored workspace (/home/t0003060/Desktop — only python_algorithms, no EDA project)
2. Invoked eda_agent skill, read fullchip_simulation README + pyaether overview
3. Searched pyAether APIs via RAG_MCP_Server:
   - seGuiRunSimulation, dmExportNetlist, mdeGetCurrentLibCellView, aeOpenDesign, aeGetCurDesign, seGuiShowNetlist
4. Read case studies + API reference
5. Wrote two files to /home/t0003060/Desktop/:
   - netlist_and_run_sim.py (7-step pyAether flow script)
   - netlist_and_run_sim_README.md (Chinese step-by-step docs)
6. Validated syntax via _check_syntax.py (SYNTAX_OK)
7. Reported 7 steps: init→open→verify→netlist→show→run→report

## Reference Script Structure (7 steps)
- Step 1 my_init_aether: ae.emyInitAether("-adv")
- Step 2 my_open_design: ae.aeOpenDesign(LIB, CELL, VIEW, "edit")
- Step 3 my_verify_design: ae.aeGetCurDesign() + ae.mdeGetCurrentLibCellView()
- Step 4 my_export_netlist: ae.dmExportNetlist()
- Step 5 my_show_netlist: ae.seGuiShowNetlist()
- Step 6 my_run_simulation: ae.seGuiRunSimulation()
- Step 7 main: orchestration with RUN_SIM/SHOW_NETLIST switches

Config: LIB="MY_LIB", CELL="MY_CELL", VIEW="schematic", hardcoded at top.

## User Follow-up
U41: "删除这个代码文件" — user asked to delete the .py files. Assistant deleted both .py files (kept README). Then cleaned up temp scripts.

## Reframe
Original script has hardcoded LIB/CELL/VIEW. Reframe to spec-driven generator:
- SUT writes netlist_sim_flow_gen.py that reads JSON spec → produces gen_script.py + README.md
- Spec defines: design(lib/cell/view), simulator, steps[], switches{run_sim,show_netlist}, init_mode
- A (visible): spec_a.json — finesim, 7 steps, ANA_LIB/AMP_TOP, both switches on, -adv
- B (hidden): spec_b.json — hspice, 6 steps (no show), DRV_LIB/OSC_CORE, show_netlist=false, -default

## Case Verification
- REF: 10/10 PASS (a-j)
- NEG 3/3 FAIL (empty/print_only/core_removed)
- §4.9 三假: empty→a/b, print_only→f/g/h, core_removed→f/g/h
- 3-seed: random lib/cell verified in generated script

## Case ID
EDA-Eval-DesignFlow-NetlistSimFlowGenProduce-001 (k=10)
