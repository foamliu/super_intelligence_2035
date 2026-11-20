# Deepread — trace 1794377042867_o5njo (xrxiong@hfeg0pkn001, digital, mc67)

**Round**: r701 (shard A, parked_reaudit revival, single-round closure)
**Source**: parked_reaudit_A.tsv REVIVABLE_QA, trace_avail=EXISTS, parked reason "r505: irun.log sim-error analysis Q&A REJECT" — invalid weak-filter rejection per 2026-11-15 reaudit mandate (analysis/Q&A is a valid user intent).
**User**: xrxiong
**Host**: hfeg0pkn001 (10.129.32.110)
**Session**: 1794377042867_o5njo.messages.json (36 msgs, 292812 B)
**Domain**: digital (shard A owned)
**Task form**: debug-Q&A / log-interpretation
**A档 feasibility**: **Infeasible** — real build dir `/proj/drvqa/V0/simdir/verilog/xrxiong/sim_dlut_perf/drgoa/gen/cyclic_weight__burty_num=5_x_num=5_y_num=20_z_num=41_sim_time=1/` owned by `cadmin:drvqa` (drwxr-s---); e0031982 denied on .75 local and via SSH to hfeg0pkn001 (agent ran as xrxiong with access). → **B档 synthesized**.

## User verbatim (U#0)

```
/proj/drvqa/V0/simdir/verilog/xrxiong/sim_dlut_perf/drgoa/gen/cyclic_weight__burty_num=5_x_num=5_y_num=20_z_num=41_sim_time=1/irun.log
分析这个日志，仿真哪个地方出错了？
```

## Agent trace summary (msg #1–#35)

- read_files irun.log (9624 lines, compile phase errors: 0) → checked tail
- Found 3 `ncelab: *E,CUVPOM` errors at lines (verbatim from agent's final answer msg #35):
  - `ncelab: *E,CUVPOM (./top.sv,182|2): Port name 'AC' is invalid or has multiple connections.`
  - `ncelab: *E,CUVPOM (./top.sv,191|8): Port name 'PracMode' is invalid or has multiple connections.`
  - `ncelab: *E,CUVPOM (./top.sv,210|17): Port name 'cm1_ro_DiscardDis' is invalid or has multiple connections.`
- Final line: `irun: *E,ELBERR: Error during elaboration (status 1), exiting.`
- read_files top.sv lines 174-233 → top module instantiates `DLUT_SIM_TOP` with `.AC('d0)` (line 182), `.PracMode('b0)` (line 191), `.cm1_ro_DiscardDis('d0)` (line 210)
- list_allowed_files → identified rhr_netlist.sv as the netlist
- read_files rhr_netlist.sv lines 8094-8161 → `DLUT_SIM_TOP` module port list (extracted verbatim):
  ```
  module DLUT_SIM_TOP (
      ISMSelRHR, POINTER_SKIP_FLAG, RA_OCU_BIT, RRHit_NormRef,
      RRHit_RHR, RfshNormal, SelRst, BANK_ACTIVE_NO_REF, DRFMEn, GReset, GResetN,
      OSC1, OSC2, OSC3, Osc2_125n, PRE, PulseModeN, RA, REF_Window, RHR_Window,
      RRASTD, RST_BUFN, RandomNumber, SampleDRFM, Section_Enable_Pre, SrefOsc,
      cm0_ro_RefCntRst, cm0_ts_FsPgm, cm1_rf_RHR2Disable, cm1_rf_RHR2Rate,
      cm1_ro_DLUTDIS0p5, cm1_ro_DLUTDep1, cm1_ro_DLUTRstBonus, cm1_ro_DisUnder2,
      cm1_ro_DiscardCtrl, cm1_ro_OscSelLFSR0RST, cm1_ro_PoissonSample,
      cm1_ro_PoissonSmp2T, cm1_ro_RHCntSkip, cm1_ro_RHDiscardDisable,
      cm1_ro_RHDiscardRate, cm1_ro_RHDiscard12, cm1_ro_RHRSkipDis,
      cm1_ro_RHSampleDisable, cm1_ro_RHSampleRate, cm1_ro_TRNGClkEn,
      cm1_ro_TRNGLFSREn, cm1_ro_TRNGPoissonEn, cm1_ro_TRNGSmpRate,
      cm1_ro_longDiscard, inh_vcc, inh_vss, inh_vbp, inh_vbn, inh_vdbias
  );
  ```
- Cross-check: `AC`, `PracMode`, `cm1_ro_DiscardDis` are NOT in this port list (note: `cm1_ro_RHDiscardDisable` and `cm1_ro_RHDiscard12` exist but `cm1_ro_DiscardDis` does not; `PulseModeN` exists but `PracMode` does not)
- Netlist generator date: Wed Nov 11 13:38:44 2026 (regenerated; top.sv still uses old port names)

## Root cause class

**CUVPOM** (Cadence ncelab: "Port name is invalid or has multiple connections") → **ELBERR** (elaboration exit status 1). Root: top.sv instantiates `DLUT_SIM_TOP` with 3 ports that don't exist in the (regenerated) module definition.

## Distinctness from prior A-shard cases

- **r698 XrunCuvmurDiagnose-001** = `*E,CUVMUR` (unresolved design unit — module defined in netlist but never compiled into worklib). Different error code, different failure mechanism.
- **r699 XrunTypeerrDiagnose-001** = `*E,TYPEERR` (bit-select index expression type illegal — string variable used as bit-select index). Different error code, different failure mechanism.
- **This case (r701)** = `*E,CUVPOM` (port name invalid — connected port doesn't exist in module definition). Third distinct root-cause class in the xrun/irun elaboration-failure family.

## Synthesized case

- **Case ID**: `EDA-Eval-DesignFlow-IrunCuvpomDiagnose-001`
- **Class**: C-A debug-Q&A / log-interpretation
- **Doc tier**: B (A infeasible)
- **A档 mini-project**: `assets/IrunCuvpomDiagnose-001/irun_cuvpom_proj/` (irun.log + top.sv + rhr_netlist.sv + verilogrun + task_brief.md). All error codes / port names / line numbers / module port list faithfully reproduced from agent's verbatim trace extraction.
- **B 隐藏变体** (base64-embedded in check.py, never enters SUT sandbox): module=RR_SIM_TOP, invalid_ports=[WRST, RefMode, cm1_ro_ForceDis], lines=[145, 159, 178], netlist_file=rr_netlist.sv. ≥10 维度全异 anti-hardcode. Disturbed B' (1 CUVPOM line removed → count 3→2) and B'' (module renamed in netlist → module_definition_found True→False) verify dynamic parsing.
- **Deliverable**: `analyze_irun_cuvpom.py` (generic irun.log CUVPOM analyzer + top.sv instance-module extractor + netlist module-port-list parser + cross-check)
- **check 15 条 a-o** (12 base a-l + 3 dynamic m/n/o): script non-empty / failing_step / primary_error_code / elaboration_error_code / cuvpom_count / invalid_port_names set / invalid_port_lines set / instance_module / module_definition_found / module_definition_file / port_cross_check / root_cause content + anti-hardcode + B' dynamic count + B'' dynamic def_found
- **Self-verification (all PASS)**:
  - [1] ref check on reference_submit.zip: PASS (15/15 assertions)
  - [2] negative_selftest: 4 negs (empty/print-expected/hardcoded-A/core-deleted) all FAIL (correct)
  - [3] §4.9 three fakes (empty-shell/print-expect/deleted-core) all FAIL (correct)
- **A.jsonl**: 355 → 356
- **trace_ledger_A.tsv**: o5njo parked → case (case_id=IrunCuvpomDiagnose-001)
- **parked_reaudit_A.tsv**: o5njo revivable yes → done
