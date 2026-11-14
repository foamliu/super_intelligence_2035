# Deepread · xhqs8 · spice testbench generation (spice_sim)

- **slug**: `1794547157832_xhqs8`
- **source**: daily-log mining r533 (eda_trace_2026111*.log), NOT in 1113 pool, NOT in any ledger → truly-NEW
- **user/host**: wzj @ hfeg0pkn002
- **mc**: 499 | **NMSG**: 520 | **size**: 2.1MB (2188289B, >2MB ⇒ deepread-only round, DEBT:1)
- **domain**: spice_sim (B)
- **USER#0**: 「帮我生成一个spice的testbench」(= generate a spice testbench)
- **USER#2**: same (repeated after "sd" typo)

## Tool chain (assistant)
- list_allowed_files: 54, read_files: 44, editor: 100, run_approved_command: 61, ask_question: 1, SandBox_MCP_Server__run_code: 1

## Key files (the real task arc)
- `/home/wzj/simulation/INV/hspiceD/schematic/netlist` — inverter netlist (read)
- `/home/wzj/simulation/latch_t/hspiceD/schematic/netlist` — latch netlist (read)
- `/home/wzj/gen_spice_tb.py` — python testbench generator (authored)
- `/home/wzj/spice_testbench.sp` — **the generated spice testbench (DELIVERABLE)**

## Case synthesis plan (next round, DEBT:1)
- **archetype**: spice_sim produce-task (L2 便携): generate a spice testbench for given hspiceD netlists
- **A (SUT-visible input)**: real INV + latch_t hspiceD netlists (scp from pkn002 next round)
- **B (hidden)**: structurally-same but different-value netlists (e.g. NAND2 + DFF), testbench must adapt
- **deliverable**: `outputs/submit.zip` containing the generated `.sp` testbench (+ generator if applicable)
- **check() ≥8 assertions**: ① zip has the .sp file ② .sp has .include of the netlist ③ stimulus section (voltage sources, transient/DC/AC analysis) ④ .measure statements present ⑤ valid hspice syntax (parseable, no unbalanced parens) ⑥ references the correct subcircuit/cell names from B's netlist ⑦ temperature/options set ⑧ runs to completion on B's netlist (subprocess) producing expected measure fields ⑨ negative: empty shell fails, print-only fails, reference-minus-core fails
- **trace_source**: {user: wzj, host: hfeg0pkn002, session_file: 1794547157832_xhqs8, match_count: 499, real_task_summary: "generate a spice testbench for INV/latch_t hspiceD netlists"}

## r533 discovery context
- Daily-log mining (eda_trace_2026111*.log, spice keywords, mc≥10) → 1181 unique slugs → 17 truly-NEW (not in 1113 pool ∪ 4-shard ledgers)
- xhqs8 = top CLEAN B-domain produce-task found among peeked 4 (2kj3r Python tooling REJECT, 43b70 greeting REJECT, 63yyw verilog analysis REJECT, xhqs8 CLEAN spice testbench)
- Sibling: 8w7t0 (mc499, same user wzj@pkn002) — likely related, defer
- This breaks the r531/r532 "fresh=0 true exhaustion" conclusion: the 1113 pool is exhausted, but the daily incremental log contains 17 truly-NEW spice candidates not captured by the 1113 snapshot. Daily-log mining is a viable unlock path beyond full-scan rescan.
