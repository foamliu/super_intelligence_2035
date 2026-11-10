# Deepread: ow6zk — Fuse Uncalled Regression/Pattern Audit

**Session**: `1793589539062_ow6zk`  
**User**: wenzhuod @ hfeg0pkn003  
**Match count**: 40 (verilog:665, digital-dominant)  
**Case built**: `EDA-Eval-DesignFlow-FuseUncalledAudit-001` (shard A, r324)  
**Date**: 2026-11-10  

## Task (A-faithful)

USER#0 逐字:
> 找出 run_fuse.sh 里哪些 fuse 相关的 Regressions 和 patterns 没被调用

This is a clean **produce** task: the user wants a tool/script that audits fuse
regression coverage — which Regressions and cmds_fuse pattern files are NOT
invoked by `run_fuse.sh`.

## Trace evolution (43 msgs, 321KB)

- **USER#0**: Original request (above).
- Agent reads `run_fuse.sh` — discovers it contains bash single-quote blocks
  (lines 3–46 and 58–89) that silently disable every `-sr` command whose source
  line falls inside them.
- Agent reads `Regressions/` directory (44 regression base files, each with
  `.inc` includes pointing to `patterns/cmds_testmode/cmds_fuse/*.v` files).
- Agent reads `cmds_fuse/` inventory (79 `.v` pattern files).
- Agent produces a coverage report: active=1 (tm_fuse_rowcol), quoted=23,
  commented=2, uncalled_reg=19, dangling=1 (tm_fuse_col_DisRpEcc),
  pulled=24, uncalled_patterns=55/79.

## Key difficulty

The bash single-quote blocks are the crux. A naive reader would treat all 26
`-sr` commands as active, but only 1 (tm_fuse_rowcol, line 50) is outside both
quote blocks and not commented. The other 23 are inside quote blocks (quoted =
disabled), and 2 are `#` commented. This distinction is what makes the case
non-trivial and checkable.

## Reframe

**Spec-driven-generator + static-verification** (matching SignalXrefBuilder-001
/ MonErrScanReport-001 pattern):

- **Deliverable**: `gen_fuse_audit.py` (stdlib generator) + `spec_a.json`
- **Generator**: reads spec.json → emits `fuse_audit_analyzer.py` (bakes spec
  via `json.loads(repr(json.dumps(spec)))`)
- **Analyzer**: parses run_fuse_sh quote_blocks + commands, classifies -sr
  commands as active/quoted/commented, computes uncalled_regressions,
  dangling_refs, pulled_per_reg, all_pulled, uncalled_patterns → writes
  report.json + report.md

## Spec design

### spec_a.json (faithful to ow6zk trace)

- run_fuse_sh: 2 quote blocks (lines 3-46, 58-89), 26 commands
- regressions: 44 bases (tm_fuse_*), with .inc includes
- cmds_fuse_inventory: 79 pattern files (FsPgm_Fuse*.v)
- Faithful numbers: active=1, quoted=23, commented=2, uncalled_reg=19,
  dangling=1, pulled=24, uncalled_patterns=55

### spec_b.json (hidden, isomorphic)

- run_fuse_sh: 1 quote block, different line ranges
- regressions: different bases (tm_xif_*), with .inc includes
- cmds_fuse_inventory: different patterns (XifPgm_*.v)
- Isomorphic numbers: active=3 (incl. dangling tm_xif_ghost), quoted=18,
  uncalled_reg=18, inv=52, pulled=23, uncalled_patterns=29

## check.py (16 conditions a-p)

a: zip valid + gen + spec_a  
b: gen py_compile  
c: gen on spec_b → analyzer  
d: analyzer py_compile  
e: analyzer runs, writes report_b.json + report_b.md  
f: report_b.json valid JSON + required fields + counts  
g: active_refs == independent recompute  
h: quoted_refs == independent recompute  
i: commented_refs == independent recompute  
j: uncalled_regressions == independent recompute  
k: dangling_refs == independent recompute  
l: pulled_per_reg == independent recompute  
m: all_pulled == independent recompute  
n: uncalled_patterns == independent recompute  
o: anti-hardcode-A (B tokens present, A tokens absent in analyzer_b)  
p: anti-trivial + 3-seed determinism  

## Self-verification

- Gold reference_submit.zip: **PASS 16/16**
- 6 negatives: **ALL FAIL** (NEG_RC=0)
  - fake_empty → cond c
  - fake_print_a → cond c
  - fake_core_deleted → cond g
  - naive_all_pull → cond e
  - naive_ignore_quotes → cond e
  - hardcode_a → cond g
- §4.9 (a)(b)(c): fake_empty, fake_print_a, fake_core_deleted all FAIL ✓
- test_sha8 = edd8d006 (test field == disk check.py bytes, sha roundtrip OK)

## Notes

- This is the 16th clean-produce-scarcity context evaluation.
- ow6zk found via strict core-verilog filter (298 candidates, mc>=15) +
  cross-shard exclusion (975 sessions) + batch-peek of 5 fresh candidates.
- Remote NFS recovered this round (was broken in r321); ssh-peek to remote
  hosts works again.
- ow6zk was the best of 5 peeked: clean A-faithful produce, focused, checkable.
