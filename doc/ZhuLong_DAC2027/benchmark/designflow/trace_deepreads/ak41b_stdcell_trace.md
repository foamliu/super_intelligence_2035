# ak41b — stdcell bottom-up signal trace (trace_signal.py)

**Session**: `1789454597897_ak41b.messages.json` (pjli @ hfeg0plg06, mc=251, domain=schematic_netlist)
**Case**: `EDA-Eval-DesignFlow-StdcellTrace-001` (shard D, appended to `EDA-Eval-DesignFlow_D.jsonl` row 79)

## A-faithful turn (U#1)

> 我把名字里带 stdcells的lib叫stdcell库。你在找我发给你的信号hierarchy，你找与它相连的instance的输入的时候，你需要找与它相连的尽量底层的stdcell，比如，如果当前与它相连的instance不在stdcell库里，则再往更底层找。请你按照我上面的要求 修改/home/\<USER\>/Desktop/trace_signal.py 这个文件

Clean 提需求轮: user defines "stdcell库" = lib whose name contains `stdcells`, and asks to find, for a given signal hierarchy, the inputs of the *lowest-level* stdcell connected to it — if the currently-connected instance is not in a stdcell lib, descend deeper. No root-cause / no fix stated by the user → A-faithful.

## What the agent did (msg54–98)

The agent modified `trace_signal.py` (a Cadence-style structural Verilog netlist parser) with a sequence of editor edits:

1. **`parse_netlist`** — added extraction of `specparam CDS_LIBNAME="..."` into `modules[cur]['lib']` (per-module library metadata).
2. **`is_stdcell(cell, modules)`** — returns `True` if the cell's `lib` contains `stdcells` (case-insensitive), or if the cell has no module definition in the netlist (a terminal leaf).
3. **`find_stdcell_drivers(module_name, net, modules)`** — the core descent: find the net's output *drivers*; if a driver `is_stdcell` → record it; if not (a hierarchical non-stdcell instance) → recurse into `drv.cell` following the driver's output pin as the new net, accumulating `hops = [(instance, cell, pin), ...]`, until the actual driving stdcell instance(s) are reached. Loop-protected via a `seen` set.
4. **`driver_input_signals` / `instance_input_connections`** — report the functional input pins of those lowest-level stdcell drivers, separating supply pins (vss/vcc/vbn/vbp/...) from functional inputs.
5. **`net_references`** — uses `(?<![\w])...(?![\w])` lookarounds (later refined in U#99 for bus bit-selects) to match a net name inside connection expressions.

Later turns (U#99 bus bit-select regex fix, U#125 find_edge_time.py VCD edge finder, U#167 signal_edge_tracer.py, U#219/302 RunTrace debugging) are **separate tasks** — NOT this case. Only U#1's stdcell-lib-aware bottom-up descent is the A-faithful subject.

## Disk gold

`/home/pjli/Desktop/trace_signal.py` (715 lines) on hfeg0plg06 — fetched and read in full. The reference `trace_signal.py` in `reference/EDA-Eval-DesignFlow-StdcellTrace-001/` is a faithful trimmed adaptation (core parse + lib + is_stdcell + find_stdcell_drivers + driver_input_signals + `--json` report).

## Case design

- **Deliverable**: `submit.zip` containing `trace_signal.py` (the modified tracer).
- **Interface**: `python3 trace_signal.py --netlist <n.sv> --signal <hier> --json <report.json>` → JSON report `{target_signal, leaf_module, leaf_net, stdcell_drivers:[{module,instance,cell,output_pin,output_expr,is_stdcell,hops:[[inst,cell,pin],...],functional_inputs:[{pin,expr}],supply_pins:[{pin,expr}]}]}`.
- **Hidden B** (`assets/.../hidden/B/`): `netlist_B.sv` + `config_B.json` (ground-truth expected). B differs from A in module names, lib names (`degpa_digital` vs `degpa_prac`; `degpa_stdcells_v2` vs `degpa_stdcells`), hierarchy depth (4-hop vs 3-hop descent), target signal (`top.u_dsp.rslt` vs `top.u_ctrl.sig_out`), and bottom stdcell (3-input NOR3 vs 2-input NAND2). B also has a load stdcell `u_buf/BUFX1_B` reading the net as an input (must NOT be reported as a driver).
- **check.py**: 15 conditions (a–o). Runs the SUT's `trace_signal.py` ONLY on B (netlist copied to an isolated temp dir without `config_B.json`, so the tracer cannot read the ground truth). Validates the descent hops chain, the lowest-level stdcell cell/is_stdcell, functional vs supply input separation, cross-input guard (A tokens absent / B tokens present), load exclusion, and 3-seed determinism.
- **三假** (must FAIL distinct): `fake_empty`→c (no report), `fake_print_fixed_A`→d (hardcoded A target/leaf), `fake_core_deleted`→f (no descent, reports non-stdcell intermediate as driver).
- **Extra negatives**: `naive_flat` (flat + naive stdcell→f), `no_lib_filter` (all-stdcell, stops early→f), `include_supply` (supply not filtered→j/k).

## Self-verify

- Reference `trace_signal.py` on B → report matches `config_B.json.expected` exactly (4-hop descent to NOR3X1_B, 3 functional inputs p0/p1/p2, supply VSS/vss).
- `check.py` on gold submit.zip → **PASS 15/15**.
- `negative_selftest.py` → **6/6 negatives FAIL** (三假 distinct: c/d/f).
- k_rationale == k_check == 15 ≥ 8.
