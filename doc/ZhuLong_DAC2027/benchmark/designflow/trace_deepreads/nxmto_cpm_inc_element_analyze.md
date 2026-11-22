# Deepread: nxmto — pdsong PDN CPM .inc element analyzer

- **session**: `1795054205299_nxmto.messages.json` (pdsong @ hfeg0pkn004, mc=196, 467 msgs / 2.27MB)
- **domain**: pg_layout (PDN / power-ground analysis; CPM extraction)
- **trace_source**: real user pdsong, host hfeg0pkn004, session_file 1795054205299_nxmto.messages.json
- **cross-shard check**: 4-shard ledger grep `nxmto` → 0 hits (truly fresh); pdsong has 2 prior C cases (LvsSvdbRepDirStat-001 plwnn, PcCoordUniformSample-001 n1o7a) + 1 D case (CpmNetlistToSymbol-001 amius) — all different sessions & different subtasks. Subtype `cpm_inc_netlist_element_counter` is首例.

## User intent (real task)
pdsong runs DDR5 PDN IR-drop flow with Apache Totem CPM (Chip Power Model) extraction.
Sweeping CPM extraction point-ratio (0p04 / 0p1 / 0p16 / 0p2 / 0p3 / 0p4 / 0p6 / 0p8 / 1 / 1p2)
produces a `Chip_Power_Model_SubCircuit.sp.inc` per variant — a SPICE subcircuit netlist
(`.subckt POWERMODEL <rails...>` + R/C/L/G(VCCS) elements + `* pad <rail> <idx>` and
`* cpm_...` comment lines per bump). User asked agent to:
1. compare dc results across sample ratios
2. compare two `.inc` files for R/C/L/VCCS/per-bump differences (msg#285, #340)
3. extract CPM runtime from run.log (msg#161-181)
4. count original PCP/PCN sample points per power (msg#430-458)
5. generate a reusable skill (msg#207 → built `pdn_dc_analyze` skill)

## Agent tool usage
editor 66, list_allowed_files 55, run_approved_command 40, read_files 36.
Key scripts written: `perform_dc_vss.sp`, `plot_dc_compare.py`, `extract_cpm_time.py`,
`compare_inc.py` (msg#293-308), `count_orig_points.py`, `count_shapes.py`, plus a full
skill at `/home/pdsong/.cline/skills/pdn_dc_analyze/`.

## Reframe decision (clean offline Python subproblem)
The `.inc` element/subckt/port analysis is a clean, fully-judgeable pure-Python subtask
(no Totem/Redhawk/Calibre dependency, no pyAether, standard library only). Real run on
1p2 vs 0p6 variants:
- 1p2: 144.75MB / 1802941 lines / subckts=[POWERMODEL] / R=2454 C=2141 L=699 G=380 / pad_lines=1797125 / total=5674
- 0p6: 72.06MB / 903773 lines / R=2161 C=2157 L=451 G=306 / pad_lines=898556 / total=5075

Synthesized small A/B samples preserve the format & differentiating structure:
- A (1p2-like): 40 lines, 6 rails, R=8 C=6 L=4 G=3 J=1, pad=13, total=22
- B (0p6-like, hidden): 30 lines, 4 rails, R=5 C=7 L=2 G=2 M=1, pad=9, total=17
Different port count (6 vs 4), different element counts, different pad_comment_lines,
different element-type presence (A has J, B has M) → strong anti-hardcode differentiation.

## Case artifact
- **task_id**: EDA-Eval-DesignFlow-CpmIncNetlistAnalyze-001
- **subtype**: cpm_inc_netlist_element_counter
- **k_check = k_rationale = 20** (①-⑳)
- check.py 20 条独立断言：zip/py_compile/B 上 rc==0+report.json/JSON 合法/顶层键/per-file 键/7 类 elements/B 元件计数==oracle/total_elem==sum/subckts==[POWERMODEL]/ports==oracle/pad_comment_lines==oracle/lines==oracle/size_bytes==真实/diff.subckt_names_identical+only_in_a/b/diff.elem_ratios[r/c/l/g]/diff.total_elem_ratio/3-seed 确定性/§4.9c A/A-swap anti-hardcode(Files.a AND files.b 均==A oracle)/files.a in B-report ==A oracle
- negatives: empty_shell→③, print_only→③, hardcode_b→⑲, naive_stub→⑧, delete_core→⑫ (全 FAIL distinct)
- ref solve.py PASS 20/20; negative_selftest ALL EXPECTATIONS SATISFIED

## Lesson
Apache Totem/Redhawk CPM extraction produces a SPICE subcircuit `.inc` whose element
inventory (R/C/L/VCCS) directly reflects PDN model fidelity vs extraction density.
Parsing this `.inc` (element count by first-letter, .subckt name+port extraction,
pad/cpm comment counting, two-variant diff) is a clean, high-signal, fully-offline
subproblem — a productive reframe from a session that is otherwise heavy on
runtime-log parsing & plot generation. The format conventions (uppercase subckt name,
`* cpm_`/`* pad ` comment markers, `+`/`$` continuation exclusion) must be preserved
exactly for the counts to match the engineer's mental model.
