# Deepread: 1791797848827_mac8s — DDR6TOP Netlist Hierarchy / Function Analysis

- **SID**: 1791797848827_mac8s
- **User**: e0014036
- **Host**: hfeg0pkn004 (10.129.2.13)
- **Domain**: schematic_netlist
- **mc**: 114 (netlist:114)
- **Grade**: B (synthesized — private /rundata 719K-line netlist unreproducible)

## User Intent (msg 0)

Continuation note: analyze the latest DDR6TOP Verilog netlist (719,514 lines) and produce a **confirmed location table** for the hierarchy:

```
DDR6TOP └─ I_DDR6TOP_R (DDR6TOP_R) └─ I_Channel (Channel)
   ├─ I_ChanPSD1
   ├─ I_Controller
   └─ I_R_NorECSRA
```

with exact netlist line numbers, module definition locations, and functional notes. The spec provides known/partial line numbers and lists TBD items (exact start/end of ChanPSD0, Controller, R_NorECSRA; module definition locations; confirmation of parent-child containment).

## Assistant Tool Chain (msgs 1-9)

- `read_files` ranged reads of the 719K-line netlist at specific line windows (712075-712120, 714940-714960, etc.)
- `read_files` on `simlib_dscqa_digital.sv` (functional sim library, ~51.5K lines) to find Controller/R_NorECSRA
- `list_allowed_files` to resolve symlinks
- Binary search probing across 604K-712K region to locate `module ChanPSD0 (`
- Cross-referencing verification env files (ddr6_specdef.sv, ddr6_timing.sv, etc.)

## Golden Result (msg 10)

Comprehensive architecture report:
1. **Corrected hierarchy tree** with confirmed line ranges for all blocks (DDR6TOP 718664-719514, DDR6TOP_R 716302-718653, Channel I_Channel 718182-718652, ChanPSD0 I_ChanPSD1 714943-715238, I_ChanPSD0 715239-716143, ChanEdgeL 716144-716290)
2. **New confirmed functional blocks**: AG_Vcc2scGlobal (9-stage SA power distribution), DQPSD (DQ/DQS interface), D_RepeaterL (left signal distribution hub, ~240 ports), BTI aging monitor (~20 ring oscillators), fuse-trim system (3-segment: Left/Mid/Right)
3. **Controller/R_NorECSRA conclusion**: inside ChanPSD0 subtree (1-604K region, post-ordered), NOT in simlib (design-level cells only in main netlist)
4. **Verification env cross-reference**: ddr6_test.sv, ddr6_model.v, patterns/ (CA parity, CK sync, cmd cancel — all DDR6 features)

## Real Artifacts / Format

- **Input**: Verilog gate-level netlist (719K lines, post-ordered, module definitions before use)
- **Output**: Markdown hierarchy location table (Hierarchy | Cell | Instance | Netlist Start | Netlist End | Module Def Start | Module Def End | Notes) + functional notes
- **Key parsing challenge**: post-ordered netlist (leaf defs first, then composites, top last); instance line ranges = instantiation line to matching `);`; same instance names (I_Controller) appear in both I_ChanPSD0 and I_ChanPSD1 — distinguish by parent containment

## Synthesis Plan (B-grade)

Self-contained **Netlist Hierarchy Locator** task:
- **Visible A**: small Verilog netlist (~200 lines, MEM_TOP → MEM_R → CHAN → SUBCHAN×2 (CTRL_UNIT + ECS_UNIT each) + EDGE_BLK), post-ordered. Agent writes a general parser tool.
- **Hidden B**: different design (DDR8_TOP → DDR8_R → LINK → LANE×3 (DECODER + CRC_UNIT each) + TERM_BLK), different names, 3 lanes (not 2), different line counts. check.py runs candidate's tool on B.
- **Deliverable**: `outputs/submit.zip` containing `hierarchy_locator.py` that takes `<netlist_path> <output_json>` and emits JSON with modules (name, def_start, def_end) + instances (parent, name, cell, start, end).
- **check.py**: ≥12 conditions on B output vs ground-truth parser (top def range, key instance start/end, parent containment of same-named instances, module def of leaf cells, total counts, 3-lane generalization).
- **Anti-hardcode**: B differs from A in names/scale/structure → hardcoded A answers fail naturally.
