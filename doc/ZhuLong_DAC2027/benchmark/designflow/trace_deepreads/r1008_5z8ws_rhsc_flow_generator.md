# r1008 deepread — 5z8ws RedHawk-SC flow script generator

**session**: `1795139793140_5z8ws.messages.json`
**user/host**: e0047472 @ hfeg0plg53 (mc=18)
**domain**: eda_other (A shard)
**scan**: ssh_eda_search_20261122_172249 (reused from r1001-r1007)
**fresh status**: absent from all 4 shard ledgers before claim (verified by fresh-diff)

## Keyword profile (scan)
`netlist:17 innovus:4` — digA filter (verilog/rtl/synopsys/innovus/tcl etc,排除 drc/lvs/virtuoso/...)
passed; netlist+innovus dominant → A-pure eda_other/digital front.

## Session structure (50 msgs, 28 user turns)
3 sub-tasks:
1. **U#0** Innovus `place_design` error: "Design has util 203.7% > 100%, placer cannot proceed"
   (density screens / softBlockages / partial blockages) — analysis Q&A via AskEDA/cimi-kb-search
   (RAGFlow API key not configured → fallback). Not selected (analysis, no produce deliverable).
2. **U#5/U#11** "redhawk sc 的流程" + "写一个redhawk sc运行的脚本供我参考" — **SELECTED** produce-task.
3. **U#21** "找一份redhawk sc的user guide" — agent searched /apps/Ansys/ARB/RedHawk_SC_rhel7_2023_R2.2/doc/
   training/RedHawk-SC_User_Manual.pdf (19.1 MB). Doc-search, not selected.

## Trace gold (U#11 → agent deliverable)
Agent queried AskEDA (hit RedHawk-SC_User_Manual.pdf score 0.86), confirmed 8-stage standard flow,
then created `/home/e0047472/rhsc_flow_example.tcl` (6084 B / 124 lines) via editor tool:

```
[0] CPU/env          set_multi_cpu_usage -local_cpu 8
[1] Output dirs      set OUT_DIR ./output; set RPT_DIR ./reports; file mkdir
[2] Tech setup       load_tech_files -lef_files {...} -tech_file ... -map_file ...
[3] Load design      load_design_files -design_data ... -netlist_files {...}
                    load_power_intent -upf_files ...  (+ commented -cpf_files)
                    load_parasitic_files -spef_files {...}
[4] Power network    setup_power_network -power_nets {VDD} -ground_nets {VSS}
                    perform_preanalysis
[5] Power calc       set_power_analysis_mode -method vectorless ...
                    load_activity_files -file ... -format tcf
                    perform_power_analysis -mode averaged  (+ commented vector_based block)
[6] Rail             perform_rail_analysis -power {VDD} -ground {VSS}
                    perform_dynamic_rail_analysis -mode vector_based ...
[7] EM               perform_em_analysis -mode static; -mode dynamic
[8] Output/reports   write_rail_output -format gds -output_dir $OUT_DIR
                    generate_rail_reports -report_dir $RPT_DIR
                    puts "INFO: ..."
```

## Case design (produce-task generalization)
Single-shot script → **scenario-driven generator** `gen_rhsc_flow.py <scenario.json> <output.tcl>`:
reads a JSON scenario spec (tech_setup / design_setup / power_network / power_calc{method
vectorless|vector_based, activity_format tcf|saif|vcd|fsdb, power_mode averaged|time_based +
time_range} / rail_analysis{static_rail, dynamic_rail, dynamic_rail_mode} / em_analysis{static_em,
dynamic_em} / cpu_count / output_dir / report_dir) → emits a customized 8-stage TCL flow with
chosen branch uncommented + opposite branch commented-out.

## Fixtures
- **A** (visible): scenario_A.json — CXTV1_DBC_6in1TC_top, tt0p8v_0c, cpu8, ./out_A/./rpt_A,
  vectorless/tcf/averaged, VDD+VSS (1+1 nets), upf, 1 netlist + 1 spef, both rail, em static+dynamic.
- **hidden B**: scenario_B.json — DDR5_PHY_TOP_wrap, ss0p72v_125c, cpu16, ./results_B/./reports_B,
  vector_based/fsdb/time_based 0-2500, VDD+VDDIO+VDDQ + VSS+VSSIO (3+2 nets), cpf, 2 netlists + 2
  spefs, dynamic rail only (static_rail=false), em static only (dynamic_em=false).
  All concrete values differ from A. B-specific anchors: DDR5_PHY_TOP_wrap / ss0p72v_125c / VDDIO /
  VDDQ / VSSIO / cpf / fsdb / time_based / ddr5_phy_B / results_B / reports_B / ./data/.

## check.py — 21 independent assertions (k=21)
zip含脚本 ②py_compile ③B subprocess exit0+非空TCL ④def+import+>200B反print-only
⑤B锚点全出现 ⑥A锚点全不泄漏(反硬编码) ⑦cpu16(反8) ⑧load_tech_files含B全lef/tech/map
⑨load_design_files含B def+全部netlist ⑩cpf uncommented+upf commented ⑪load_parasitic含B全spef
⑫setup_power_network 3+2 nets含VDDIO/VDDQ(反A 1+1) ⑬perform_preanalysis ⑭vector_based uncommented
+vectorless commented+fsdb+time_based 0-2500(反averaged) ⑮dynamic_rail vector_based uncommented+
static commented ⑯em static uncommented+dynamic commented ⑰OUT_DIR=results_B+RPT_DIR=reports_B+
write_rail_output+generate_rail_reports ⑱stage banner 0..8 单调 ⑲3次md5一致 ⑳无参exit非零(反空壳)
㉑不存在scenario exit非零(反静默通过)

## Verification
- reference gen_rhsc_flow.py: in-place PASS, E2E-from-jsonl-test-field PASS (21/21)
- §4.9 three-fake: neg_empty / neg_print_only / neg_core_deleted ALL FAIL
- negative_selftest: ref PASS + 3 negs FAIL ✓
- A.jsonl appended; ledger 5z8ws claimed→case
