# deepread — 4a852 (e0039602 @ hfeg0plg85) · round r978 · 0-case (cross-shard collision + domain mismatch)

**Session:** `1791963281932_4a852.messages.json` · user `e0039602` · host `hfeg0plg85` · mc=661
**Scan classification:** rtl/verif dominant → **A-domain** (digital), NOT C-domain.
**Round r978 outcome:** 0-case (rolled back). Case assets parked under `_parked_cases/EDA-Eval-DesignFlow-NetMissingCellExtract-001/`.

## What was built (then parked)

Subtask `netlist_missing_cell_deterministic_extract` — the deterministic pure-Python
first stage the real trace user (e0039602) actually built: a Verilog netlist parser
that lists every instance whose cell is NOT defined in `simlib_base.sv`, emitting a
structured JSON report. NO LLM, NO VCS, NO EDA tool — pure stdlib (re/json/sys).

This is an **orthogonal subproblem** to shard-A's `EDA-Eval-DesignFlow-NetCellMap-001`
(same trace, different subtask): NetCellMap-001 covers the AI-driven full netlist
rewrite + VCS elaboration (k=12); this case covers only the deterministic
missing-cell extractor (k=15).

- sample_a: 4 modules, 20 instances, **14 missing** (10 distinct missing cells:
  nand2IOLVx2, nand3IOLVx2, ntn_lv, ptn_lv, invDSx1×3, invCS×2, invhizCS,
  invenCS, parasiticRC2, invenLVSx1×2) — matches the real trace's 14 missing
  instances (msg #272 real output).
- hidden B: 6 modules, 28 instances, **12 missing** (10 distinct missing cells
  DISJOINT from A: bufLV_drv, delayRC3, invLVSx2, invenIOLV, keeperRC,
  mux4IOLV, nor2LVx2, ntn_io, ptn_io, tg_lv) — anti-hardcode.
- check.py: 15 independent conditions (a-o); reference solve.py PASS; 5
  negatives (empty_shell/print_only/hardcode_b/naive_stub/delete_core) all FAIL
  on distinct conds (d/e/g/m/o). Fully self-verified via negative_selftest.py.
- Real subprocess execution on hidden B (cond d); 3-seed PYTHONHASHSEED
  determinism (cond n); anti-hardcode cross-input guard on A (cond o).

## Why parked (NOT appended to C.jsonl)

1. **Cross-shard collision.** `4a852` is already `case` in shard A as
   `EDA-Eval-DesignFlow-NetCellMap-001` (domain=digital, 2026-11-04). The
   cross-shard ledger mutex ("一 trace 一 case") REFUSEs a plain `claim` in
   shard C; `mark --force` would override the guard against the existing A case.
2. **Domain mismatch.** The fresh scan classifies this trace as A-domain
   (rtl/verif dominant). Shard C's allowed domains are strictly
   physical_verify / layout_virtuoso / layout_aether / pg_layout. C's
   `physical_verify` precedent is Calibre/LVS/DRC decks, AutoCell TCL, solido
   PVT, StarRC, PEX/ITF, DSPF RC — a Verilog netlist missing-cell parser does
   NOT fit. Forcing domain=physical_verify would misdomain the case and risk a
   near-dup/misdomain flag in anti-hardcode audits.
3. **Root cause** (process defect, same lesson as r886): the trace was selected
   for shard C WITHOUT first grepping the cross-shard ledger
   (`grep <sid> trace_ledger_{A,B,C,D}.tsv`). The earlier session's summary
   asserted "physical_verify" but the ledger evidence (A row domain=digital +
   C fresh-scan note "dominant=rtl/verif A-domain") contradicts that.

## Lesson (reinforces r886)

**选料前必先 `grep <sid> trace_ledger_{A,B,C,D}.tsv` 跨 shard 去重，并核对 scan
的 domain 分类与目标 shard 的允许域。** Netlist cell-extraction / Verilog parsing
是 A-domain (digital/eda_other)，不是 C-domain physical_verify。C-domain 的
physical_verify 限定 Calibre/LVS/DRC-deck/SVRF/PEX-ITF/DSPF-RC/StarRC/solido-PVT
等物理验证工具操纵类任务。

## Rehome path (if shard A wants it)

This is a valid A-shard orthogonal-subtask case. Re-home: copy `assets/` +
`reference/` from `_parked_cases/EDA-Eval-DesignFlow-NetMissingCellExtract-001/`
into `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/{assets,reference}/`, append
a case record to `EDA-Eval-DesignFlow_A.jsonl` with `metadata.domain=digital` and
`metadata.trace_source` pointing at `1791963281932_4a852` (same trace as
NetCellMap-001, different subtask). check.py / solve.py / negatives need no
changes.
