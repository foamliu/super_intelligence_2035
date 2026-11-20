# Deepread: 1793861310425_dmk4f — Aether FullAdder builder (layout_aether)

**trace**: sinanz@10.129.2.14 (hfeg0plg014) session 1793861310425_dmk4f
(mc=87, agent=lead, 66 msgs, 560KB, 2026-11-05; claimed r808 shard C)

## User intent (verbatim U#0)
"我在路径/ai_sandbox/trgqa/V0_die2/agentdir/sinanz/Skills 放置了2个skill...
帮我在我的个人工作路径/proj/trgqa/V0_die2/workdir/sinanz/Test_ZSN下生成一个名为
FullAdder_2的单bit全加器电路。你可以调用公共库/proj/trgqa/V0_die2/libs的单元...
基本逻辑单元在/proj/trgqa/V0_die2/libs/stdcells_ac，但注意绝对不能改动它们。"
+ std-cell naming convention tutorial (or2Lx1 = OR, 2 inputs, L-type, x1 size).

## Assistant execution (SandBox_MCP_Server__run_code, pyAether, 14 calls)
- A#24-28: dbOpenCVByType probe existing FullAdder / FullAdder_1b (instances/nets/terms/shapes)
- A#37: BUILD — dbNewCellView(Test_ZSN, FullAdder_2, schematic) + aeOpenDesign(edit) +
  aeGetCurDesign + instantiate stdcells_ac masters (om(lib,cell) helper)
- A#39-47: verify FullAdder_2 — instances, nets, terms, emyText/emyLine shapes, net binding
- A#49-51: cleanup — delete extraneous ipin/opin instances, stray net Y/terminal Y
- A#53: final verify — REOPEN FullAdder_2 (instances/nets/terms counts)
- A#63: GOLD SANITY — reopen FullAdder_2 + stdcells_ac masters readable:
  xor2Lx1, and2Lx1, or2Lx1 (the 3 std cells used in a full adder)

## Full-adder decomposition (gold algorithm)
sum  = a XOR b XOR cin   -> 2x xor2Lx1
cout = (a AND b) OR ((a XOR b) AND cin) -> 2x and2Lx1 + 1x or2Lx1
  (or equivalent: cout = (a&b)|(b&cin)|(a&cin) -> 3x and2Lx1 + 1x or3)
Std cells used (confirmed A#63): xor2Lx1, and2Lx1, or2Lx1 from stdcells_ac.
Ports: a, b, cin (in); sum, cout (out). Cell name: FullAdder_2 in lib Test_ZSN.

## pyAether API surface (from trace)
ae.emyInitAether("-adv"); ae.emyString(s); ae.dbOpenCVByType(lib,cell,view,view,mode);
ae.dbNewCellView(lib,cell,view,view); ae.aeOpenDesign(lib,cell,view,mode=edit);
ae.aeGetCurDesign(); ae.aeDesignIsEditable(cur);
cv.instances / cv.nets / cv.terms / cv.terminals / cv.shapes;
i.name / i.libName / i.cellName / i.viewName / i.instTerms; t.name / t.net.name;
t.getTermType(); type(sh).__name__ == 'emyLine'|'emyText'; sh.text / sh.dbuOrigin;
i.destroy(); net.instTerms.

## Case plan (next round, B-file reframe — A-file needs live Aether, unshippable)
- Deliverable: full_adder_builder.py — pyAether stdlib script that builds a full-adder
  schematic by instantiating stdcells_ac std cells + wiring nets.
- Visible A: task_brief.md = user verbatim U#0 request + std-cell naming tutorial +
  stdcells_ac cell list (xor2Lx1/and2Lx1/or2Lx1/invLx1/nand2Lx1/nor2Lx1...).
- Hidden B: build a DIFFERENT cell — e.g. HalfAdder_1b (sum=a XOR b, cout=a AND b;
  1x xor2Lx1 + 1x and2Lx1, ports a/b/sum/cout, no cin) OR a 2-input AND gate And2_custom.
  B differs from A in: cell name, port set, std-cell instance set, net wiring.
- check() pattern = mock-pyAether capture (offline, no live Aether needed):
  1. check() writes a mock pyAether.py into temp dir (records all ae.* calls into a list)
  2. sys.path.insert temp dir, import SUT full_adder_builder.py (runs `import pyAether as ae`)
  3. validate recorded call graph against B expected structure
- >=8 assertions (draft):
  (1) script py_compiles + stdlib/pyAether imports only
  (2) called ae.emyInitAether
  (3) created/opened cellview with B cell name (HalfAdder_1b) in lib Test_ZSN — NOT A FullAdder_2 [anti-hardcode]
  (4) instantiated exactly the B-required std cells from stdcells_ac (xor2Lx1 + and2Lx1 for half-adder) — counts match
  (5) did NOT instantiate A-only cells (no second xor2Lx1 / no or2Lx1 for half-adder) [anti-hardcode A]
  (6) created/declared B port terminals (a, b, sum, cout — no cin for half-adder)
  (7) wired sum net to xor2Lx1 output; wired cout net to and2Lx1 output
  (8) wired xor2Lx1 inputs to a,b; and2Lx1 inputs to a,b
  (9) called ae.aeOpenDesign(edit) or dbNewCellView (editable mode) — actually creates, not just reads
  (10) idempotent: running twice produces same call graph (no duplicate instances)
  (11) degenerate: empty/print-only script -> no ae.dbNewCellView call -> FAIL
  (12) core-deleted (no instantiation) -> (4) FAIL
- negatives: _neg_empty (README only), _neg_print_only (prints "FullAdder built" no ae calls),
  _neg_hardcode_a (builds FullAdder_2 not B HalfAdder_1b -> (3)(5) FAIL),
  _neg_core_deleted (opens but no instances -> (4) FAIL).
- ref PASS: reference full_adder_builder_ref.py (parameterized by cell spec) runs through mock -> all 12 pass.
- k_rationale = k_check = 12 >= 8 OK

## Risk / open question
- mock-pyAether must be faithful enough that a correct SUT script `import pyAether` binds to
  the mock and the script ae.* calls are captured. SUT may use `from pyAether import emyInitAether`
  — mock must expose both module-level and callable forms. Mitigate: mock exposes a generic
  __getattr__ returning a recorder callable, so ANY ae.X(...) call is captured.
- SUT might guard `import pyAether` in try/except (aether not in SUT sandbox) — the SUT IS the
  design_flow sandbox which HAS eda_flow MCP but the script runs as a standalone .py in
  check() temp dir (no aether). So the SUT script MUST be written to `import pyAether` at
  top level (the mock provides it). Task brief must instruct: "ship a pyAether script that
  would build the circuit when run in an Aether environment".

## Selection context (r808)
r808 spent the round scanning 10+ fresh mc>=10 candidates for shard C (physical_verify).
Finding: the best shard-C traces (sk6cg DRC-log, ziv3j CDL-audit) are ALREADY cases
(DrcLogTeardownReport-001 by C 11-06, CdlXistorAudit-001 by D 11-06). The remaining
fresh high-keyword sessions are mostly wrong-domain (digital verilog sim / synthesis
migration / SV testbench) where drc/lvs/calibre keyword counts come from PATH references,
not actual physical_verify work; or Q&A-only with no checkable deliverable (x0ib4 PEX Q&A,
qky0j netlist-analysis Q&A, n1crk AutoCell TCL incomplete). dmk4f is the only FRESH
layout_aether trace with a concrete build task + real pyAether execution, reserved for
next round via claim. See MEMORY_C r808 entry for the full rejected-candidate list.
