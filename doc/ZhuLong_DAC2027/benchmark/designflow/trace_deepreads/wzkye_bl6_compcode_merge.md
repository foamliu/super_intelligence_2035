# Deepread: 1792634547955_wzkye (gracew / hfeg0pkn004, mc=129)

## Trace facts
- scan: refined-A filter r422 (.75 Python A-specific, top_tool∈{verilog,rtl,systemverilog,...}, a>2c/b/n, a≥20, excl 410 A-ledger anchors) → 575 fresh strict-A candidates; wzkye selected
- session: 1792634547955_wzkye.messages.json (281 KB / 4618 lines extracted as wzkye_full.txt on .75 workdir, 568 msgs)
- agent: cline v3.0.51 (act mode, deepseek-lead)
- kw: verilog/rtl/systemverilog dominant; c/b = 0 (clean A-dominant digital)
- host: hfeg0pkn004, user gracew (fresh for shard A)

## User asks (produce-task — user gave RULES, not root cause)
The user is building a SystemVerilog testbench for LPDDR5/6 DDR6 and needs a
"compcode comparison" expected-value model for the BL6 (burst-length 6)
2-bank CP-fail random test. Across the session the user supplies the
fault-classification + merge RULES (CPFailN 36-bit active-low layout, 16
CP code-groups, ECC/RED pair bits, 4-level per-bank classification, the
CPCODE[16] table, and the 2-bank → 8-bit DQ merge table) and asks the agent
to implement them as a Python reference model that the SV testbench will
check against. The user does NOT give a root cause / diagnosis — they give a
spec and ask for an implementation. → A-faithful produce-task qualifies.

## Agent actions
- editor ×97, run_approved_command ×52 (and other tool calls)
- implemented Python reference model: `bl6_bank_lvl` (per-bank 0..3 fault
  level), `bl6_bank_code` (per-bank repairable low6 code), `bl6_merge`
  (2-bank → 8-bit DQ) plus `compute` wrapper
- wrote `test_bl6_merge.py` — a Python self-check that verifies a 10-row
  merge truth table (the user-provided merge cases) end-to-end
- iterated against the user's rule clarifications until the model matched
  the expected DQ values

## A-faithful verdict
FEASIBLE produce-task — user supplied rules + expected values, agent
produced a verifiable Python model. The trace IS A-faithful.

## B档 rationale
The trace agent's deliverable is a SystemVerilog-testbench-coupled Python
model whose exact API surface and merge-table rows are entangled with the
user's private TB context (10-row table, SV-side calling convention). To
make a self-contained, offline-verifiable benchmark deliverable we
re-synthesise the SAME algorithm (BL6 compcode 2-bank 8-bit DQ generator)
as a pure-stdlib `bl6_compcode.py` with a clean 4-function API
(bank_lvl / bank_code / merge / compute) + CLI, driven by external vector
files. The spec.md captures the user's rules verbatim (CPFailN layout,
level table, CPCODE table, merge table); the A/B vector files are fresh
inputs (A uses CP groups 0/1; B uses 5/9/10/11/3/7/12/15) so a memorising
SUT cannot pass B. → B档 synthesized, A-faithful at the algorithm/rules
level.

## B档 synthesis (Bl6CompcodeMerge-001)
- deliverable = bl6_compcode.py (pure stdlib): bank_lvl(cpn)→0..3,
  bank_code(cpn)→low6, merge(a_lvl,a_code,b_lvl,b_code)→8-bit,
  compute(cpn_a,cpn_b)→8-bit; CLI reads vector pairs, prints 0x%02X DQ.
- A (visible): cpfail_vectors_A.txt — 8 pairs (CP0 repairable, pure RED,
  CP0+RED lvl3, ECC-only, 2-groups, both-CP0-same) + spec.md
- B (hidden): cpfail_vectors_B.txt — 14 pairs with DIFFERENT CP groups
  (5,9,10,11,3,7,12,15) and combos (both-same CP5, both-diff CP5 vs CP12,
  both-unrepairable, 3-groups, repairable-vs-lvl3, group0 two-fail-single-
  group, ECC-only, pure-RED, CP3+RED lvl3)
- check.py: 22 conditions (a-p) + independent bit-string/char-scan oracle
  (vs reference integer bit-shift/modulo, two implementations to avoid
  shared-bug masking); 4 negatives (naive_empty / print_only /
  core_removed [drop both-repairable-diff→0x34, surgical: only d+k_diff
  fail] / hardcoded_A) + negative_selftest; §4.9 (a)(b)(c) fake-submits
  all FAIL; 3-seed shuffle determinism (o); edge ECC→0x31 / RED→0x32 (p).
