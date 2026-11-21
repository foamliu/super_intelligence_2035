# Deepread: 1795144839476_70aax — post-ATPG Verilog DFF Count + Distribution

## Trace metadata
- **session**: 1795144839476_70aax
- **user**: joeyz @ hfeg0plg54
- **mc**: 107 (schematic:33; netlist:60; waveform:14)
- **date**: 2026-11-21
- **agent**: GLM-5.2
- **msgs**: 199, 578KB

## Real work path (NFS, not sandboxable)
`/home/dfx/dev/cust2atpg/workdir/ddjob/atpg/rev0.4_zyk/tcl/tmp/netlist_verilog.atpg.out9_final.v`
— a post-ATPG scan-inserted Verilog netlist for customer-2 ATPG flow.

## User turns (verbatim)

- **U#0** (clock-structure analysis): user asks agent to analyze the clock structure of the netlist.
- **U#107** (clock-source trace): user asks agent to trace the clock source path for a specific instance `ChanMid.I_CMCenterR.I_ModeRegMR5_1717`.
- **U#118** (continuation): `jixu renwu` (continue task).
- **U#184** (DFF count + distribution — **seed turn**):
  `1.zheng ge design zhogn DFF shu liang , fen bu zai naxie shili zhong ?`
  (Pinyin input, verbatim preserved. Meaning: "1. The total DFF count in the whole design, and which instances they are distributed in?")

## User intent (U#184)

User wants the agent to:
1. Count the total number of DFF (D flip-flop) cells in the entire design.
2. Report which parent instances those DFFs are distributed across (i.e., group DFFs by their parent instance in the dot-separated hierarchy path).

This is a single-turn intent statement (no root-cause or solution provided by the user). The agent must produce a script that parses the Verilog netlist and emits a structured report.

## Synthesized A netlist (design_atpg_A.v)

Real NFS path not sandboxable → synthesized 3292B mini netlist preserving real hierarchy names and real DFF cell names from the trace:

- Hierarchy: `ChanMid.I_CMCenterR` / `CoreCtrl.I_DdrCtrl` / `TopMon.I_EventCnt`
- DFF cells: `SDFFARX1`, `SDFFSRX2`, `DFFHQX4`, `DFFARX1`, `SDFFHQX2` (real scan-DFF cell types)
- 12 DFFs across 3 parent instances, 4 DFFs each
- 6 non-DFF distractor gates: `INVX1`, `NAND2X1`, `MUX2X1`, `BUFX2`, `NOR2X1`, `LATCHX1` (latch — must NOT count as DFF)

## Hidden B netlist (design_atpg_B.v)

Token-disjoint from A (5 dimensions: module name, hierarchy instance names, DFF cell types, non-DFF gate types, filename):

- Hierarchy: `PipeStage.I_FifoCtrl` (5 DFF) / `Ifu.I_Decoder` (4 DFF) / `Lsu.I_AddrReg` (2 DFF)
- DFF types: `SDFFRPX1`, `DFFSQX2`, `DFFRX1`, `SDFFSPX4`
- 11 DFFs total
- Non-DFF distractor: `AOI21X1`, `OAI21X1`, `XNOR2X1`, `AND2X1`, `NOR3X1`, `LATQX1` (latch)

## DFF criterion

Cell name contains the substring `DFF`. Latches (`LATCH*` / `LAT*`) and purely combinational gates (`INV*`, `NAND*`, `MUX*`, `BUF*`, `NOR*`, `AOI*`, `OAI*`, `XNOR*`, `AND*`) are excluded.

## Reference produce-script (count_dff_dist.py)

CLI: `<netlist.v> [-o report.json]`

1. Read netlist text.
2. For each line, strip comments (`//`, `/*`, `*`).
3. Regex-match `cell instname(` (skip Verilog keywords).
4. If `DFF` substring in cell name → record DFF; parent = `instname.rsplit('.',1)[0]` (or `<top>` if no dot).
5. Otherwise → non-DFF gate counter.
6. Emit JSON `{total_dff, by_instance (sorted), dff_types (sorted), total_gates, non_dff_gates, non_dff_types}`.

## check.py (12 assertions a-l, 12312B, sha256=019bbc0f...)

- a) zip contains ≥1 .py script
- b) script py_compiles
- c) script runs on B (exit 0), writes JSON with keys `total_dff/by_instance/dff_types/non_dff_gates`
- d) B total_dff == 11
- e) B by_instance == `{Ifu.I_Decoder:4, Lsu.I_AddrReg:2, PipeStage.I_FifoCtrl:5}`
- f) B dff_types == `{DFFRX1:4, DFFSQX2:2, SDFFRPX1:3, SDFFSPX4:2}`
- g) B non_dff_gates ≥ 5 AND no `LATCH`/`LAT` cell appears in dff_types
- h) script runs on embedded A (base64, anti-hardcode) — exit 0
- i) A total_dff == 12 (A-gold, defeats B-only hardcode of the count)
- j) A by_instance == `{ChanMid.I_CMCenterR:4, CoreCtrl.I_DdrCtrl:4, TopMon.I_EventCnt:4}`
- k) A dff_types == `{DFFARX1:2, DFFHQX4:2, SDFFARX1:4, SDFFHQX2:2, SDFFSRX2:2}`
- l) 3-seed determinism: 3 runs on B produce md5-identical stdout

Plus independent `_gt_recount` line-based ground-truth recount (different regex strategy from a typical candidate, defeats regex gaming).

## §4.9 anti-hardcode

A embedded as base64 (4392 chars). A-gold cross-check (h-k) defeats B-only stubs:
- `fake_empty.py` → FAIL a
- `fake_print_only.py` (prints B JSON without parsing) → FAIL i
- `fake_core_deleted.py` (hardcodes B counts, skips parsing) → FAIL i

## Self-verification

- ref 12/12 PASS on B + ref on A produces A-gold + 3-seed md5 identical
- 3 negatives all FAIL (`NEG_RC=ALL FAIL`)
- k_check=12 (labeled a-l) == k_rationale=12 >= 8 GATE PASS ✓

## Notes

- A-faithful: prompt preserves user's verbatim pinyin input from U#184 (no paraphrasing, no correction of typo `zhogn`→`zhong`).
- task_brief.md (≤3 lines) describes the delivery interface only (CLI shape, JSON report fields, latch exclusion), not what to do.
- Hidden B + hidden_manifest.json do NOT ship to SUT sandbox (PreToolUse hook convention).
