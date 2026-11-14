# deepread: 1791963281932_4a852 (NetlistLibCellMap-001)

- **trace**: e0039602 @ hfeg0plg95, mc=688, 555 msgs, act mode, multi-turn
- **domain**: schematic_netlist (netlist:2752 / lvs:164 / schematic:44 / verilog:94)
- **session file**: `/home/e0039602/.cline/data/sessions/1791963281932_4a852/1791963281932_4a852.messages.json` (2.3MB)

## Task
User has a Verilog netlist with cells not defined in `simlib_base.sv`. Replace each undefined cell with a valid library physical cell (inv_base / inven_base / invhiz_base / fba* / passg_base / latch_base etc., all with built-in vcc_/vss_/vbulkn_/vbulkp_ pins), following 11 strict mapping rules:
1. highest-abstraction mapping (don't replicate transistor skeleton, don't split to bare nn/pp); CMOS inv pair → single inv_base
2. delay/timing on physical cells; pure logic merge with & / |
3. power/substrate pin fidelity (vssz→vss_, NMOS bulk→vbulkn_, vcc→vcc_ & vbulkp_)
4. enable/complement path X-propagation + contention safety
5. no UDP primitives for pure logic (dangling power legs)
6. avoid bare nn/pp stacks unless no physical cell can realize the function
7. dead-node cleanup: driven-but-never-read internal wires → driver removed
8. charge-hold nodes (latch QN) → trireg (medium) #(…)
9. style: `celldefine/`endcelldefine, spec_gates_begin/end, specparam *`CDLYW, port/param order
10. preserve all params & connections
11. print each replacement (original line → replaced line); don't rewrite the file; verify via truth-table enumeration (z, hold, X)

## Evolution
- U#52: user pastes "standard answer" netlist (IO_rsnand21nand31_DL_ACT_MERGE_READ) → assistant does detailed diff: strength positional vs named, instance renumbering, fgc_pwrstate_monitor ports, `celldefine wrappers, specparam timing
- U#77: evolve into automation project — run.py top-level script calling AI API (deepseek-v4-flash @ http://10.129.8.86:8899) to do end-to-end conversion, output a text file "line N: original → replacement"
- Assistant uses editor + run_approved_command (python-runner) repeatedly; hits API timeout/model-name issues

## Why B-grade synthesized reframe
Original netlist + simlib_base.sv are private on e0039602's host (/home/e0039602/Documents/netlist_change_copy/), unreachable. Synthesize a small netlist_A.v (5 modules) + simlib_base.sv (7 physical cells) mirroring the real task's rule structure; candidate writes convert_cells.py; judge swaps hidden B (5 modules, different names) and re-runs.

## Case produced
- **case_id**: EDA-Eval-DesignFlow-NetlistLibCellMap-001
- **D.jsonl**: 394 → 395
- **check.py**: 21 conditions (a–u), L2 真跑 subprocess, anti-hardcode, B2/B3 robustness, determinism, §4.9 triple-degenerate
- **REF**: PASS 21/21; 4 negatives all FAIL (c/h/j/s)
- **k_rationale == k_check == 21**
