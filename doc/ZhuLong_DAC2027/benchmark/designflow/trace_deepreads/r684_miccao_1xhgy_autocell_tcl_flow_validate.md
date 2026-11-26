# Deepread: 1xhgy — AutoCell TCL Flow Generator (r684)

**Trace source**: miccao @ 10.129.32.47, session `1789895218929_1xhgy`, mc=434 (drc:1977/calibre:996/lvs:231/netlist:702/verilog:562/.gds:280).
**Domain**: physical_verify (AutoCell standard-cell TCL flow generation/validation — Calibre/DRC/LVS-adjacent standard-cell layout automation).
**Peek date**: 2026-11-17 r684. **Build**: DEFER to r685 (AutoCellTclFlowValidate-001).

## User intent (verbatim U#0 — the ONLY organic user turn)

U#0 is a ~3000-word **AutoCell TCL Flow Generator skill spec** (pasted by user as the task prompt). U#1/U#2 = 「继续」(non-independent). Key structure of the spec:

**Goal**: "Generate, modify, or validate a complete AutoCell standard-cell TCL flow with these eight files: run.tcl, layers.tcl, layer_functions.tcl, viadefs.tcl, globals.tcl, rules.tcl, place.tcl, route.tcl".

**3 work modes**: (1) Create — build all 8 from user/PDK inputs; (2) Modify — preserve existing flow, change requested objects; (3) Validate/fix — inspect structure/dependencies/references, report findings before repairing.

**Process type**: planar (channel_width sizing) OR finfet (nfin/fin_width/active-width). No cross-profile inference.

**Generation order**: layers.tcl → layer_functions.tcl → viadefs.tcl → globals.tcl → rules.tcl → place.tcl → route.tcl → run.tcl. `run.tcl` must source the 7 tech files in exactly that order. Final flow must: read netlists, create cells, configure placement+routing, call `generate_layout`, call `write_layout`.

**8 New-flow hard constraints**:
1. **Technology creation**: `tech -process` in `layers.tcl`; `run.tcl` must NOT create technology.
2. **Via separation**: via defs in `viadefs.tcl`; router instances `via ... -viadef ...` in `route.tcl`.
3. **Explicit placement mode**: exactly one of `auto` (set_placer, no read_placement) OR `replay` (read_placement JSON, no set_placer).
4. **Predictable GDS output**: `[file join $case_dir ...]` (no bare relative filenames).
5. **Explicit router contract**: `set_router` with `grid_map`, `pin_template`, `pin_grid`, `vdd_connector`, `vss_connector` (record omission reason).
6. **Explicit grid map**: map phys layers → grids from Flow Spec (no layer-name inference).
7. **Profile isolation**: no 7nm/DRAM geometry/GDS/rule/via/template defaults for another profile.
8. **Historical compatibility**: 7nm/DRAM differences = legacy facts; reproduce only in legacy-compat mode.

**Reference/naming constraints (structural rules)**:
- Declare layer in `layers.tcl` BEFORE setting function / using in via def / applying rule.
- Layer functions only for declared layers.
- Via defs reference declared cut/lower/upper layers.
- Via instance references existing via def.
- `grid_map` keys = declared phys layers; values = defined grids.
- `pin_template`/`pin_grid`/boundary/dummy/placement/PG connectors defined before `run.tcl` references.
- Device class/model names match netlist + netlist-reader args.
- Cell lists have matching netlist inputs; replay mode also matching placement JSON.
- `set_global_net` roles = replacement lists (re-exec replaces, not appends).
- No combining power domains/body-net aliases without user confirmation.

**Parameter provenance**: record source (user/pdk/existing_flow) for every process-specific value; missing → `TODO` or stop+ask.

**Optional GDS-to-PCell conversion** (only when user explicitly asks): `scripts/gds2pcell_wrapper.py` with `--target-lib`/`--pcell-lib`/`--gds-files`/`--cell-list`.

## Assistant behavior (what actually happened in trace)

**Off-track**: The assistant did NOT generate/validate the 8 AutoCell TCL files. Instead, it created `g5_*.sh`/`g5_*.py` batch runner scripts in `/home/miccao/.cline/scripts/data/` (g5_verify_env.sh, g5_make_joblist.sh, g5_run_one.sh, g5_batch_run.sh, g5_summarize.sh, g5_smoke.sh, g5_poll.sh, g5_boot.sh, g5_fix_netlists.py, g5_flatten_netlists.py, g5_debug_flat.py) — these are VCO DRC batch-running helpers, unrelated to the AutoCell TCL flow spec in U#0.

**Tool counts**: 324 msgs, 3 user turns, 177 tool_uses (62 editor, 46 run_approved_command, 35 read_files, 29 list_allowed_files, 2 search_codebase, 1 skills). Final assistant texts: "VCO 修复生效" / "DRC deck 编译成功，卡在 Calibre license" / "编辑器持续出错，新建独立文件" — env/license debugging, NOT AutoCell flow work.

**Interpretation**: User pasted the AutoCell TCL Flow Generator skill spec (likely as a skill/role definition), but the actual work the agent did was VCO DRC batch scripts (possibly a prior task context bleeding in, or the agent misread the spec as a system-prompt rather than a task). Either way, **the AutoCell 8-TCL-file deliverable was never produced** — this is a failed-task trace from the agent's side.

## Reframe plan: AutoCellTclFlowValidate-001 (build r685)

**Mode chosen**: **Validate** (mode 3 of the spec). Reason: Create mode requires a complete Flow Spec with all process-specific values (GDS mappings, via geometry, rule values, device models, routing grids) — too heavy to synthesize faithfully. Validate mode only needs (a) a candidate flow (8 .tcl files) + (b) the hard-constraint/structural rules (from the spec) → output a JSON validation report. Tractable + faithful to user intent (Validate is one of 3 declared modes).

**Deliverable**: `outputs/submit.zip` containing `validate_flow.py` (pure stdlib) + `validation_report.json`. The script reads 8 candidate .tcl files + a Flow Spec JSON, checks against 8 hard constraints + structural rules, outputs a JSON report with per-rule findings (pass/fail + evidence line numbers).

**Mock-behavioral reframe family**: belongs to C r645-r683 family. **Sub-type**: `autocell-tcl-flow-validate` — **TCL flow validator首例**, distinct vs r683 DrcLogPerfAnalysis (DRC log timing parse) / r682 DrcEnclosureRuleExtract (deck text rule classify) / r681 CalibreDfmCmdExtract (single-signal DFM cmd regex) / r679 LvsGuiConfigGen (SKILL→Python config generator). Core difference = **cross-file TCL reference validation** (8 files, layer/via/grid cross-refs) + **8 hard constraints semantic check** (not single-file regex).

**Fixture-cost档位**: ②source-semantic-parse (per D r785 4-档 spectrum). Fixture = skill spec text (U#0) + candidate .tcl files (text, line-parseable). Candidate must implement rule logic (cross-file ref resolution + semantic constraint checks), not pure regex. Not ④binary-mock (no TCL interpreter needed). This is the **C域首例 of D r785 第4子型 source-code-itself-as-fixture**.

**asset A** (visible): `flow_spec_A.json` (planar profile, 5 layers, 2 vias, 1 device, auto placement) + 8 .tcl files (`layers_A.tcl`...`run_A.tcl`) with **injected violations** (e.g., tech creation in run.tcl instead of layers.tcl → violates constraint 1; via def in route.tcl → violates constraint 2; bare relative GDS output → violates constraint 4; etc. — ~6-8 violations across the 8 constraints + structural rules).
**hidden B** (anti-hardcode, all-different): `flow_spec_B.json` (finfet profile, 6 layers, 3 vias, 2 devices, replay placement) + 8 .tcl files with **different violations** at different positions (e.g., via instance referencing non-existent via def → violates structural rule; grid_map key = undeclared layer → violates constraint 6; both set_placer AND read_placement → violates constraint 3; etc. — ~7-9 violations, count + positions ≠ A).
**hidden B2** (degenerate): `flow_spec_B2.json` (minimal, 2 layers, 1 via, 1 device) + 8 .tcl files, 0 violations (clean flow) — verifies the validator correctly reports "no violations" (false-positive guard).

**check() 16 conditions a-p** (draft):
- ①(a) zip + py_compile
- ②(b) B exit 0 + stdout non-empty + JSON has `findings` array + `summary` object
- ③(c) B correctly identifies constraint-1 violation (tech creation location)
- ④(d) B correctly identifies constraint-2 violation (via separation)
- ⑤(e) B correctly identifies constraint-3 violation (placement mode exclusivity)
- ⑥(f) B correctly identifies constraint-4 violation (GDS output path form)
- ⑦(g) B correctly identifies constraint-5 violation (router contract completeness)
- ⑧(h) B correctly identifies constraint-6 violation (grid_map key declaration)
- ⑨(i) B correctly identifies a structural rule violation (layer declared before use / via def references declared layers / via instance references existing via def — pick the one injected in B)
- ⑩(j) B correctly counts total violations (matches injected count for B)
- ⑪(k) B each finding has required fields (rule_id, severity, file, line, message)
- ⑫(l) B2 (clean flow) reports 0 violations (false-positive guard)
- ⑬(m) B violation set ≠ A violation set (anti-hardcode: different rules violated at different files/lines)
- ⑭(n) B rule_ids subset of the 8 hard constraints + structural rules enum (no invented rules)
- ⑮(o) deterministic: 3x byte-identical JSON output
- ⑯(p) anti-hardcode: B flow_spec differs from A (finfet vs planar, 6 vs 5 layers, 3 vs 2 vias, replay vs auto) + B .tcl file contents differ from A (different layer/via/device names, different violation positions)

**4 negatives**: empty_shell (syntax err → a) / print_expected_A (hardcode A's findings → m or j) / core_deleted_silent_error (empty output → b) / always_pass_stub (prints "OK" → c or j). All FAIL, first_fail ≥3 distinct.

**Distinctness check vs past C cases**: ✓ (TCL cross-file validator is new sub-type; no past case validates 8-file TCL flow against 8 hard constraints + structural rules).

## Trace source for metadata
```
trace_source:
  user: miccao
  host: 10.129.32.47
  session_file: 1789895218929_1xhgy.messages.json
  match_count: 434
  real_task_summary: "User pasted AutoCell TCL Flow Generator skill spec (8-file standard-cell TCL flow, 3 modes Create/Modify/Validate, 8 hard constraints + structural rules). Reframed as Validate-mode task (AutoCellTclFlowValidate-001): given candidate 8 .tcl files + Flow Spec JSON, validate against 8 hard constraints + structural rules, output JSON validation report."
```

## DEBT status
DEBT 1: deepread done (this note), case build deferred to r685 (40min budget insufficient for 16-condition check + 8 hard constraints implementation + 4 negatives + hidden B/B2 + §4.9 fakes + self-verify). r685 first task = build AutoCellTclFlowValidate-001.
