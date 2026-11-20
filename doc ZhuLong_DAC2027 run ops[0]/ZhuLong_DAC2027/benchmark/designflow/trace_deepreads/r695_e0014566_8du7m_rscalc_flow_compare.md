# r695 deepread — 8du7m (e0014566 @ hfeg0plg58, mc411)

**Source**: `/home/e0014566/.cline/data/sessions/1785498914896_8du7m/1785498914896_8du7m.messages.json` (379 msgs, 192 user / 187 assistant)

## User intent (verbatim)

U#0: `<user_input mode="act">read the prompt_flow.md and do the job in it.</user_input>`

The "job" is defined in `/home/e0014566/test_layout_rscalc_flow/prompt_flow.md` — a **Layout Resistance Optimization Workflow** spec combining three Virtuoso tools in a loop:

```
Original Layout --> RsCalc (baseline) --> resistance_baseline
        |
        v
  +- AutoVia (add vias) ----> PowerFill (power fill) --> RsCalc (verify) --> resistance_optimized
  |                                                                                    |
  +-- Compare: reduction = (baseline-optimized)/baseline                              |
         +-- reduction >= target? --YES---> DONE [OK]                                 |
         +-- NO & iterations < max? --YES--> iterate (use optimized as next input)    |
         +-- NO & iterations >= max ---> STOP [X] (report best result)               +
```

Flow control: `target_reduction_pct=30`, `max_iterations=3` (in `flow_control.config`, auto-generated from `layout_rscalc_flow.config`).

## Real deliverable (per spec Step 5)

Step 5 "Compare & Iterate" — the user's actual end-goal:
1. Build a comparison table: per check point (net, layer, position), baseline R, optimized R, reduction %, meets target?
2. Iteration decision logic: DONE (all meet target) / ITERATE (current < max, not all meet) / STOP (max reached, not all meet)
3. If STOP: report best result + suggest manual tuning.

Steps 1-4 (RsCalc / AutoVia / PowerFill / RsCalc-verify runs) are Virtuoso execution — require real Virtuoso + private OA layout (`/proj/train/AI_Virtuoso/ver/rscalc_flow/e0030265`) + private GDS (`/rundata/.../testa.gds`). **Not portable to sandbox.**

## Assistant behavior (trace summary)

- A#1-9: read prompt_flow.md + layout_rscalc_flow.config + flow_control.config + gen_tool_configs.py + 3 SKILL.md + 3 gen_*_agent.py → understood flow structure.
- A#11-75: Step 1 baseline RsCalc — ran `gen_tool_configs.py`, `gen_rscalc_agent.py`, launched Virtuoso batch (nohup), waited sleep 180, grepped DONE!/Error, found baseline .rvn files at `/proj/train/AI_Virtuoso/ver/rscalc_flow/e0030265/rscalc/testa/RSDB_{vdd,vbb,M1}/*.rvn`.
- A#77-135: Step 2 AutoVia — edited `layout_rscalc_flow.config` (filled pwrNets="M1 vdd vbb"), re-ran gen_tool_configs, gen_autovia_agent, launched Virtuoso, waited, found autovia output GDS.
- A#109-127: created `create_autovia_output.il` to copy autovia output cell.
- A#123-265: Step 3 PowerFill — struggled with `genPowerFill.py` (Python 3.7 / Calibre / cds.lib issues), edited genPowerFill.py 3x, created `create_powerfill_output.il`, waited through 4 retry rounds (powerfill_run*.log).
- A#270-377: Step 4 Verification RsCalc — ran gen_rscalc_agent with `rscalc_verify.config`, struggled through 4 retry rounds (rscalc_verify_run*.log), edited rscalc_verify.config, never reached Step 5 Compare.

~50+ Virtuoso batch launches, ~30 sleep waits, ~20 log greps. **Step 5 (Compare & Iterate) was never reached** — the actual deliverable was never produced.

## Key real file formats (grounding for reframe)

### flow_control.config (real, from trace)
```
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; flow_control.config (AUTO-GENERATED from layout_rscalc_flow.config)
;; Do not edit manually -- edit layout_rscalc_flow.config instead
;; Controls the iteration loop of the resistance optimization flow.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

target_reduction_pct = 30
max_iterations       = 3
```

### .rvn file format (real, from trace)
File: `RSDB_vdd/vdd.rvn`:
```
LV+RSView:NodeList,3
1,34,"vdd","M1",5.5498,-2.1450,5.5503,-2.0200,"vdd",5.5500,-2.0825,16.7159996,,,,,,,,,0
2,29,"vdd","M1",6.3498,-2.1450,6.3502,-2.0200,"vss",6.3500,-2.0825,14.0279999,,,,,,,,,0
3,24,"vdd","M1",7.0747,-2.1450,7.0753,-2.0200,"vdd",7.0750,-2.0825,11.5920000,,,,,,,,,0
4,17,"vdd","M1",8.3748,-2.1450,8.3752,-2.0200,"vdd",8.3750,-2.0825,7.2240005,,,,,,,,,0
```

CSV columns (quoted strings handle commas):
- 1: row index
- 2: node_id
- 3: net_name ("vdd")
- 4: layer ("M1")
- 5-6: x1, y1 (start point)
- 7-8: x2, y2 (end point)
- 9: net_name2
- 10-11: mid_x, mid_y
- **12: resistance value (Ohm)** ← THE KEY VALUE per spec
- 13-25: empty fields
- last: 0

Each row = one check point (net, layer, position pair). Each .rvn file = one net/layer combination (file name = `{net}_{layer}.rvn` or directory `RSDB_{net}/{net}.rvn`).

`RSDB_vbb/vbb.rvn` and `RSDB_M1/M1.rvn` had only the header `LV+RSView:NodeList,3` (no data rows) in the trace — i.e., those nets had no measurable resistance nodes.

## Reframe (mock-behavioral, per 11-15 task初心)

**Real intent preserved**: Step 5 Compare & Iterate — compare baseline vs optimized .rvn resistance, compute reduction %, decide DONE/ITERATE/STOP, report best.

**Necessarily out-of-scope**: Steps 1-4 Virtuoso execution (requires real Virtuoso + private OA layout + private GDS — not portable to sandbox, not checkable without real EDA).

**New sub-type**: `flow-orchestrator-compare-report` — multi-input (.rvn files + config) → structured JSON comparison report + iteration decision. **Distinct** vs prior C cases:
- r694 skill_file_batch_transform = text batch transform + rename
- r692 aether_autoroute_trace_rule_diag = manual search + error diagnose
- r690 drc_var_mismatch_diag = diagnose existing report
- r688 svrf_pvrs_convert = SVRF→PVRS translate
- r687 drc_pg_open_rule_gen = spec→SVRF generate
- r685 auto_cell_tcl_flow_validate = validate existing TCL
- r682 drc_enclosure_rule_extract = deck rule classify
- **r695 (this) = multi-file .rvn parse + reduction % compute + DONE/ITERATE/STOP decision + best-result report** (new: flow-orchestrator-compare-report)

**Deliverable**: `rscalc_flow_compare.py` (pure stdlib) that:
- Reads `flow_control.config` → `target_reduction_pct`, `max_iterations`
- Reads `baseline/*.rvn` → per-row {check_point_id, net, layer, x1, y1, x2, y2, resistance}
- Reads `iter<N>/*.rvn` for each available iteration → per-row optimized resistance
- Computes per-check-point per-iteration: `reduction_pct = (baseline - optimized) / baseline * 100`, `meets_target = reduction_pct >= target_reduction_pct`
- Decision logic:
  - If at any iteration ALL check points meet target → `decision=DONE`, `best_iteration=that iteration`
  - Else if `current_iteration < max_iterations` AND more iterations available → `decision=ITERATE`
  - Else (max reached without all meeting) → `decision=STOP`, `best_iteration=iteration with highest min reduction`
- Outputs structured JSON to stdout with keys: `config`, `baseline`, `iterations`, `comparison`, `decision`, `best_iteration`, `best_summary`
- Deterministic (sort_keys=True, indent=2)

**Asset A (visible)**: flow_control.config (target=30, max=3) + baseline/{vdd_M1.rvn with 4 rows, vbb_M1.rvn with 3 rows, M1_M1.rvn with 3 rows} + iter1/{*.rvn with ~50% reduction, all meet 30%} → decision DONE at iter1.

**Hidden B (STOP case, anti-hardcode)**: flow_control.config (target=40, max=2) + different .rvn values + iter1 + iter2 (both below 40%) → decision STOP at iter2.

**Hidden B2 (ITERATE case, edge)**: flow_control.config (target=50, max=3) + different .rvn values + iter1 only (below 50%) → decision ITERATE (current=1 < max=3).

**check() 16 conditions a-p**: see check.py.

**Teeth**: anti-hardcode (B has different .rvn values / config → must compute from B, not print A), deterministic, 3 decision-logic branches tested (DONE via A ref / STOP via B / ITERATE via B2), 4 negatives (empty/print/no-core/always-pass) all FAIL.
