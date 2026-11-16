# r658 deepread — xdwang / eo84n / netlist-to-schematic-builder

- session: 1794401065591_eo84n.messages.json
- user: xdwang @ hfeg0plg94 (10.129.8.226), mc=413
- domain: layout_aether (Aether schematic creation from netlist)
- model: glm-5.3-flash (cxmt-glm), 231 msgs, 1.53MB
- host tools: SandBox_MCP_Server__run_code (pyAether bridge) — real Aether cellview ops

## User turns (提出需求型, A档合规)
- U#1: "check this schematic and feed back: how much inverters in this schematic" (analysis — count inverters in TimingCtrl)
- U#2: "add 1 inverter to the net 'Eqmsa'" (place invLVx1 I10, A→Eqmsa, Y→Eqmsa_n)
- U#3: "creat a new circuit 'INV' in this lib and realize a inverter function"
- U#4: "creat circuit according to this netlist in lib: .../00_DSCQA_Array_xdw"  ← core produce-task
- U#5: "add wire connect for all net(not include power) for easier human viewing"
- U#6: "add label to each wire according to the net nane in netlist"

## Gold (assistant delivered + self-verified, design saved 20:57:58)
Recreate **top-level TimingCtrl/schematic** in lib 00_DSCQA_Array_xdw from ALPS netlist:
- top pins: Active (input), Reset (input), Eqmsa (output)
- 15 instances: 3× invLVx1, 8× Delay_Rise, 1× rsnor23LVx1, 1× and2CSx1, 1× nand2CSx1, 1× nor2CSx1
- supply nets: vcc!, vss!, vbp!, vbn! (excluded from wires)
- signal nets (22 electrical nets total): Active, Active1–Active4, Precharge, Precharge1–Precharge4, Reset, Sensing, net3, net5, net6, net7, Eqmsa
- wires added for all multi-terminal signal nets (U#5)
- net-name labels added on each net's own wire (dbCrtSchWireName on net.getShapes()), 14 labels correctly attached; Active4/Precharge2 unlabeled (wire-merge artifact, electrical intact)
- A#150: "every connection matches the netlist" + cell persisted on disk (sch.oa)
- A#230: "design saved, electrical circuit fully intact"

## Reframe (B档 mock-behavioral reframe, subtype `netlist-to-schematic-builder`)
Real netlist at /proj/dscqa/.../netlist (sandbox-unreachable) → synthesize mock ALPS netlist as asset A.
Deliverable = `build_schematic_from_netlist.py` (pure stdlib) that parses a SPICE netlist:
- top `.subckt` → top_cell + top pin names
- `.pins <name>:<dir>` directive → pin directions
- `I<name> <master> <pin>=<net> ...` → instances (name, master, port→net map)
- net classification: power (trailing `!` or supply name vcc/vss/vdd/gnd/vbp/vbn) vs signal
- output JSON: {top_cell, top_pins[{name,dir}], instances[{name,master,pins{port:net}}], nets[{name,type}], wires[{net,points?}], labels[{net,label}]}
- wires for signal nets only; label == net name per netlist
distinct vs r657=3d-lvs-gui-config / r656=via-enclosure-dist / r655=polygon-orientation / r652=pex-batch-path / r650=cut-layer-idx / r645=svrf-antenna.

## check() plan (≥8 teeth, hidden B + B2 reverse-hardcode)
run `python build_schematic_from_netlist.py <hidden_B.sp>` → parse JSON → assert:
top_cell==B name (not hardcoded TimingCtrl); top_pins count+names+dirs; instance count; each instance master+port→net; power-net classification (vcc!/vss! excluded from wires); signal-net wires present; label==net name; net connectivity; B2 different netlist → different counts (anti-hardcode); determinism; AST no hardcoded A masters.
