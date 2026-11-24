# Deepread: cxsbx — VDD/VSS stripe re-label + constraint audit

- session: `1795395238902_cxsbx` (e0047600 @ hfeg0pkn002, mc=176)
- scan keywords: `.gds:1102; lvs:64; drc:51; skipper:47; rtl:28; calibre:8`
- domain: **physical_verify** (GDS power-label re-flow + geometric constraint audit)
- source path on host: `/home/e0047600/.cline/data/sessions/1795395238902_cxsbx/1795395238902_cxsbx.messages.json` (2.1 MB, 355 msgs)

## Real task summary
User recovers a crashed session in `/home/e0047600/project_wzf/vdd_vss_replace_v2`.
The project is a Python tool (`vdd_vss_label_v2.py`, py3.11 + gdstk) that re-labels
VDD/VSS power labels on an SRAM-macro GDS (`HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1.gds`).

Two modes:
- **grid mode** — auto place PG labels on a 5×5 grid snapped to vertical metal stripes
  (95:353 = VSS, 95:354 = VDD), ~671 labels.
- **reference mode** (`--match-reference`) — replicate hand-placed `re_*.gds` PG labels, ~720.

Constraints verified by `_verify_v2.py` + `_check_constraints.py` (30 assertions):
1. delete old PG labels cleanly (layer 95:251), no recursion into subcells.
2. grid points on stripe center-line (≤0.002 µm), all on-metal.
3. texttype→net mapping 353=VSS / 354=VDD, zero mismatches.
4. left-area exclusion (`--exclude-left-x 5.0`): grid points whose y falls in the
   signal-pin y-band AND x<5.0 are dropped (grid mode only; reference mode = "参考即规范").
5. boundary: bottom/top/left/right edges all have landing points; last gap < pitch.
6. polygons & subcells untouched (zero geometry change).
7. reference mode: 720 labels, 718/720 intersect `re_*.gds`, 2 off-metal corrected.

Session work: revert a half-finished edit (9-param vs 7-param TypeError), pyc
golden-bytecode equivalence check, end-to-end smoke both modes, 30/30 constraint
audit PASS, manual sync, file cleanup.

## Synthesized case (r1054)
`VddVssStripeAudit-001` — SUT writes `relabel_audit.py` that ingests a GDS
label-table JSON export and emits an audit report (counts / per-label flags /
violations / boundary / summary). check.py runs it on **hidden input B**
(different stripe geometry + seeded violations: off-metal, off-center,
wrong-layer, wrong-net, left-exclusion, duplicate) and asserts ≥15 independent
fields. Anti-hardcode via hidden B; §4.9 fakes (empty/print-only/hardcode-A/
naive-count) all FAIL.

Self-contained: pure stdlib JSON (no gdstk / no GDS binary parse) — the
valuable physical_verify reasoning (stripe model, on-metal vs on-center,
texttype→net, left-exclusion, boundary coverage) is fully exercised.
