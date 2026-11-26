# Deepread: sid 1793864423469_6c7d2 — FullAdder_4 gate-level schematic build+verify (layout_aether)

- **trace**: 1793864423469_6c7d2 (sinanz @ hfeg0pkn005, mc=322, 226 msgs, 1.4MB messages.json)
- **keywords** (summary.tsv): schematic:611;netlist:583;lvs:278;aether:275;pyaether:244;cellview:176;cmos:161;verilog:152
- **tool profile**: 553 schematic · 440 netlist · 177 pyAether · 63 "lang":"pyAether" · 47 dbCreateInst · 43 cellview · 25 hspice · 4 virtuoso
- **domain**: layout_aether (pyAether schematic construction in Aether)

## User intent (msg 0, verbatim core)
> 你现在你是一个资深的全定制电路设计工程师。接下来你需要学习 /ai_sandbox/trgqa/V0_die2/agentdir/sinanz/Skills 放置的2个skill，它们分别让你能够查看和分析Aether里面的电路，以及能够让你自主编辑和构建新电路，然后在 /proj/trgqa/V0_die2/workdir/sinanz/Test_ZSN 下生成一个名为 FullAdder_4 的单bit全加器电路。你可以调用公共库 /proj/trgqa/V0_die2/libs/stdcells_ac 的单元，但绝对不能改动公共库的东西。

## Skills learned
- `Skills/ReadSchematic.md` (sch-reader): pyAether OA schematic reader — I/O pins, instances, nets, shapes, circuit function.
- `Skills/SchematicEdit.md` (sch-edit): "once and done" recipe for editing/building schematics — net rename (electrical `net.name` vs visible `emyText.text`), wire labels, autopin short cleanup (delete `basic/ipin,opin` insts + `P__` pins), no spurious "Y" net.

## Real artifacts (read back from messages.json tool_results)
### build_full_adder4.py (msg 30)
Builds FullAdder_4 in lib Test_ZSN:
- gates: IXOR1/IXOR2 (xor2Lx1 @ (0,0)/(3.5,0)), IAND1/IAND2 (and2Lx1 @ (0,-3)/(3.5,-3)), IOR1 (or2Lx1 @ (7,-1.5))
- termnet: IXOR1{A:A,B:B,Y:n_ab_xor} IXOR2{A:n_ab_xor,B:CIN,Y:SUM} IAND1{A:A,B:B,Y:n_ab_and} IAND2{A:n_ab_xor,B:CIN,Y:n_cin_xor} IOR1{A:n_ab_and,B:n_cin_xor,Y:COUT}
- io: A/B/CIN=input, SUM/COUT=output; power pw: vcc→vcc!, vss→vss!, vbp→vbp!, vbn→vbn!
- steps: dbNewCellView→aeOpenDesign(edit)→dbCreateInst per gate→dbCrtNet all nets→set instTerm.net (signal + power)→dbCrtTerm/dbCrtPinByNet per port→aeCrtWireLabelsAndPins→destroy autopin ipin/opin + spurious Y net + P__ pins→relabel emyText to real net names→aeSaveDesign
- expected nets (12): A,B,CIN,SUM,COUT,n_ab_xor,n_ab_and,n_cin_xor,vcc!,vss!,vbp!,vbn!

### verify_full_adder4.py (msg 36)
Opens FullAdder_4/schematic read-only and checks:
- NETS: expected set {A,B,CIN,SUM,COUT,n_ab_xor,n_ab_and,n_cin_xor,vcc!,vss!,vbp!,vbn!}; assert "Y" not in nets
- TERMINALS: set via nets' terms; expected [A,B,CIN,SUM,COUT]
- INSTANCES + instTerm→net: exp_conn (same termnet) per instance; power terms → bang nets; CONNECT_OK flag
- SHAPES: emyLine/emyText counts + text label histogram

## L1-boundary extraction (live Aether + /proj/trgqa blocked on .75 sandbox)
Real L2 = pyAether building FullAdder_4 in live Aether on /proj/trgqa/V0_die2 — blocked (no Aether install, /proj/trgqa unreadable by sandbox user). Verifiable core = the gate-level netlist **synthesizer + topology/logic verifier** that captures build_full_adder4.py + verify_full_adder4.py without live Aether:

`gate_netlist_build_verify.py` (pure stdlib): given a spec JSON (gates/connections/ports/power/logic), synthesize canonical netlist (instances + nets + terminal→net + ports + power) and verify (1) topology — nets exact set, no spurious Y, instances name/master/pos, instTerm→net, power→bang, port dirs, no dangling internal; (2) logic — parse master name → (gate_type, n_inputs), exhaustive 2^k gate-level simulation vs spec.logic boolean expr.

## Case design
- **case id**: EDA-Eval-DesignFlow-GateNetlistBuildVerify-001 (layout_aether, B-synthesized, L1-boundary)
- **A (visible)**: spec_A.json = FullAdder_4 (5 gates xor2/and2/or2, 5 ports, 12 nets, logic SUM=A^B^CIN / COUT=(A&B)|((A^B)&CIN))
- **hidden B**: spec_B.json = MUX2_4g (invLx1 + 2×and2Lx1 + or2Lx1, 4 ports A/B/S/Y, logic Y=(A&~S)|(B&S), truth [0,0,0,1,1,0,1,1]) — structurally disjoint (inv master, different #gates/#ports/logic/table) → kills hardcode-A
- **hidden B2 (cross-input guard)**: spec_B2.json = HalfAdder_2g (xor2 + and2, 4 ports, SUM=A^B / CARRY=A&B) — different scale/logic → kills hardcoded tables again
- **grader**: 16 conditions (a–p): zip/py_compile/stdlib, A run, report keys, A nets exact, A instances/masters/pos, A connections+power, A ports, A topology.all, A logic.ok, A SUM table, A COUT table, hidden B topology+logic.ok, hidden B Y table, hidden B2 topology+logic+SUM+CARRY, determinism+leakage.
- **TEETH**: hardcode-A fails (n) (B's Y table wrong); print-fixed fails (e)/(k) (no real nets/table); core-deleted fails (j) (logic.ok=False); empty fails (a); must parse inv master (m); must simulate (not lookup) (k/l/m/n/o).
- **negatives**: empty_shell→(a), print_fixed→(e), core_deleted→(j), hardcode_A→(n). NEG_RC=0. §4.9 (a)(b)(c) all FAIL.
- **determinism**: report sha256 stable across 2 runs (sorted_keys+indent2+trailing newline).
- k_rationale = k_check = 16 ≥ 8 ✓.
