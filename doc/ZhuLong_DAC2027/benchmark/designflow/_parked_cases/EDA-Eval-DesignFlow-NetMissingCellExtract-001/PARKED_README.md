# PARKED — EDA-Eval-DesignFlow-NetMissingCellExtract-001

**Status:** parked (NOT appended to any shard jsonl). Built round r978 (2026-11-23),
then rolled back from EDA-Flow-Bench.

## Why parked

- Trace `1791963281932_4a852.messages.json` (user e0039602, host hfeg0plg85,
  mc=661) is **already claimed in shard A** as `EDA-Eval-DesignFlow-NetCellMap-001`
  (domain=digital, k=12, full AI-driven netlist rewrite + VCS elaboration).
- The fresh scan classifies this trace as **A-domain** (rtl/verif dominant),
  NOT a shard-C domain (physical_verify / layout_virtuoso / layout_aether /
  pg_layout). Shard C's `physical_verify` precedent is Calibre/LVS/DRC decks,
  AutoCell TCL, solido PVT, StarRC, PEX/ITF, DSPF RC — a Verilog netlist
  missing-cell parser does not fit.
- The cross-shard ledger mutex ("一 trace 一 case") REFUSEs a plain `claim`;
- The cross-shard ledger mutex ("一 trace 一 case") REFUSEs a plain `claim`;
  `mark --force` would override the guard against the existing A case.
- Root cause: trace was selected without first grepping the cross-shard ledger
  (lesson recorded in MEMORY_C r886 + r978).

## What this case is (orthogonal subtask, A-domain)

`netlist_missing_cell_deterministic_extract` — a deterministic pure-Python
parser that, given a Verilog netlist + a simlib library file, emits a JSON
report of every instance whose cell is NOT defined in simlib. NO LLM, NO VCS,
NO EDA tool — pure stdlib (re/json/sys). This is the deterministic first
stage the real trace user (e0039602) actually built before the AI-driven
cell-mapping stage that NetCellMap-001 covers.

- sample_a: 4 modules, 20 instances, 14 missing (10 distinct missing cells)
  — matches the real trace's 14 missing instances.
- hidden B: 6 modules, 28 instances, 12 missing (10 distinct missing cells,
  DISJOINT from A's missing set) — anti-hardcode.
- check.py: 15 independent conditions (a-o); reference solve.py PASS; 5
- check.py: 15 independent conditions (a-o); reference solve.py PASS; 5
  negatives (empty_shell/print_only/hardcode_b/naive_stub/delete_core) all
  FAIL on distinct conds (d/e/g/m/o). Fully self-verified.

## Possible rehome

This case is a valid **A-shard** (digital/eda_other) orthogonal-subtask case.
If shard A wants it, re-home: copy `assets/` + `reference/` into
`EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/{assets,reference}/EDA-Eval-DesignFlow-NetMissingCellExtract-001/`,
append a case record to `EDA-Eval-DesignFlow_A.jsonl` with
`metadata.domain=digital`, `metadata.trace_source` pointing at
`1791963281932_4a852` (same trace as NetCellMap-001, different subtask), and
`mark --force` the A ledger (or reuse the existing A row's case_id list).
The check.py / solve.py / negatives need no changes.
