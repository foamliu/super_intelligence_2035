# Deepread: 1789895218929_1xhgy — AutoCell TCL Flow Generator

## Trace info
- **anchor**: 1789895218929_1xhgy
- **user/host**: miccao @ hfeg0plg37
- **match_count**: 370 (mc≥100 ✓)
- **messages**: 324 total (180 user, 144 assistant)
- **domain**: eda_other (AutoCell standard-cell layout flow automation)
- **agent**: lead

## A档② judgment
- **user#0 verbatim** (9639 chars): `# AutoCell TCL Flow Generator` spec defining 8 TCL files (run/layers/layer_functions/viadefs/globals/rules/place/route), 3 work modes (Create/Modify/Validate), 2 process profiles (Planar/FinFET), generation+sourcing order, 8 hard constraints, naming constraints, parameter provenance, validation, delivery format. Tail: `/home/miccao/autocell/ddcpc/netlist/...` specific task (generate GDS, iterate DRC, per-cell logs).
- **judgment**: clean 提需求 (generate a complete AutoCell standard-cell TCL flow from spec + specific netlist/constraints) → **A档规则②合格 → A档 faithful** ✓
- **NOT**: root-cause/fix-given (user doesn't provide a fix), NOT summary/continuation, NOT Q&A

## Verb uniqueness
- **verb**: `autocell-tcl-flow-gen` (generate 8 TCL files for AutoCell standard-cell layout flow)
- Unique vs all 55 existing shard-A verbs ✓

## Case design
- **case_id**: EDA-Eval-DesignFlow-AutoCellTclFlow-001
- **deliverable**: submit.zip { generate_autocell_flow.py + report_A.json }
- **CLI**: `generate_autocell_flow.py --spec <spec.json> --skeleton <skeleton_dir> --out <out_dir>`
- **A visible bundle**: references/{pipeline.md, profile-planar.md, command-reference.md} + assets/skeleton/{8 .tcl templates with TODOs} + inputs/{spec_planar.json, cell_constraints.txt, netlist/invx1.v}
- **B hidden bundle**: inputs/spec_finfet.json (FinFET process, different layers/gds numbers/via geometry/rules/device sizing)
- **check.py**: 20 conditions a-t, pure stdlib python3 + tclsh (no AutoCell license needed)
  - a-b: zip contents + py_compile
  - c: run on A → 8 TCL files
  - d: run.tcl sourcing order (7 files in exact order)
  - e: tech -process in layers.tcl, NOT in run.tcl
  - f-h: layers/layer_functions/viadefs match spec
  - i-j: globals/rules match spec
  - k: placement mode (auto: set_placer, no read_placement)
  - l: set_router with 5 required params
  - m: generate_layout + write_layout in run.tcl
  - n: tclsh info complete for all 8 files
  - o: no TODO placeholders
  - p: [file join $case_dir ...] output path
  - q: run on B → 8 TCL files
  - r-t: cross-input guards (finfet process, finfet layers, finfet rules)

## Cross-input guard design
- A: planar process, layers {poly/active/nwell/contact/metal1-3/via1-2}, gds layers 1-14, rules {min_width_m1=0.06...}, device_sizing=channel_width
- B: finfet process, layers {fin/active_fin/nwell_fin/contact_fin/metal1-3/via1-2}, gds layers 5-24, rules {min_fin_width=0.008, min_fin_spacing=0.012...}, device_sizing=nfin
- B has 4 finfet-specific layers NOT in A (fin, active_fin, nwell_fin, contact_fin)
- B has 2 finfet-specific rules NOT in A (min_fin_width, min_fin_spacing)
- naive_hardcode_a (hardcodes planar) FAILS at (r) tech -process finfet and (s) finfet layers

## Self-verify results
- ref PASS 20/20 (a-t) ✓
- 5 negatives all FAIL ✓ (fake_empty→d, fake_print_expected→c, fake_core_deleted→e, naive_hardcode_a→f, fake_structure_only→f)
- §4.9 (a)(b)(c) 三假 all FAIL ✓
- NEG_RC=0 ✓
- k_rationale=k_check=20 ≥8 ✓ GATE PASS
- test==disk check.py roundtrip OK (10946 bytes) ✓
- test_rationale starts "20 条断言" with ①-⑳ ✓

## Build/append scripts
- `designflow/_append_autocell_tclflow_001.py`
- deepread: this file
