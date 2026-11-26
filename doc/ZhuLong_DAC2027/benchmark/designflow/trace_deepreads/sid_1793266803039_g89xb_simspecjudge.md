# Deepread: g89xb — SimSpecJudge (Vcc2scAct multi-sim SPEC compare)

**Trace**: 1793266803039_g89xb.messages.json (tongni@hfeg0pkn001, mc=224, hspice 667/netlist 238)
**Session path**: 10.129.2.10:/home/tongni/.cline/data/sessions/1793266803039_g89xb/

## USER#0 (verbatim, A-档 提出需求轮)
"[sim-sp-gen]
/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp/ 路径下给出了对应的网表和SPEC 根据此跑对应的仿真"
- 给出 folder 路径（含 netlist + SPEC.sp）+ 任务（跑对应仿真）。
- 无根因/无修复方案 → clean A-档。

## Folder contents (msg#4 listing)
- `SPEC.sp` (984B, fetched verbatim — real SPEC thresholds, 5 categories)
- `tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_sim_schematic.netlist` (64KB)

## Workflow (323 msgs, 7 user turns)
USER#0 跑仿真 → assistant 用 sim-sp-gen skill 生成 4 类 .sp deck (tran/ac/ac_load/dc_capbi/tran_mc) →
bsub 提交 5 个 LSF 作业 (msg#122: 5 jobs PEND on fqueue3) → 跑在 hfeg0pfn119/120 →
measure 文件产出到 /proj/dscqa/.../2610sim_Vcc2scAct/{tran,ac,ac_load,dc_capbi,tran_mc}/ →
assistant 写 _analyze.py / measure_summarize.py / monitor.py 解析 .mt0/.ma0/.mc0 + 对比 SPEC →
USER#1-6: debug ac 挂/tran 没跑完/monitor 没效果 → 最终 monitor.py 出 SPEC 对比报告。

## Golden SPEC report (msg#315, user-accepted final summary)
| 仿真 | 状态 | 121 PVT corners / 500 MC |
|---|---|---|
| ac / ac_load | DONE | 121 corners |
| tran | DONE | 121 corners |
| tran_mc | DONE | 500 samples |
| dc_capbi | RUNNING | ~100/121 |

**AC/AC_LOAD — 全面 FAIL**: Gain≈21dB vs >40dB; GBW≈4.3kHz vs >1MHz; GM 为负 (.lstb 断点位置不对)
**TRAN_MC — PASS**: unload_mc 3σ=6.06mV<10mV; 1mA_mc 3σ=6.05mV<10mV
**TRAN — partial**:
  PASS: Vcc2sc_unload |Δ|=4.39mV<5mV; undershot min 0.882>0.87; undrmag max 17.1mV<30mV;
        overshot max 0.912<0.93; ring_ratio 6.9e-6<0.01
  FAIL: Vcc2sc_load1mA |Δ|=7.55mV>5mV; Rspon max 127.5ns>100ns; tsetting 20µs (dont care)

## Real MC stats (msg#181, primesim tran_mc log)
- vcc2sc_unload_mc: min=0.8962859 max=0.9089694
- vcc2sc_1ma_mc: mean=0.9004307 std=2.017315e-3 (3σ=6.05mV) min=0.8956204 max=0.9082541
- FineSim Successfully Completed, 6147 CPU-s, 1.71h, 8 threads, 2560MB peak

## Case design (SimSpecJudge-001, spice_sim A-faithful L2)
- **Deliverable**: `judge_sim_vs_spec.py <measure_dir> <spec_file> <out_json>` — parse HSPICE .mt0/.ma0/.mc0
  + SPEC.sp category thresholds → multi-category PASS/FAIL report JSON.
- **Distinct from Vcc2scVarJudge-001** (z6mt7, single .mt0 + single variation SPEC): this case is
  multi-measure-type (.mt0 tran + .ma0 ac + .mc0 mc), multi-metric (~10 SPEC metrics across 5 categories),
  multi-operator (>, <, dev<, 3sigma<, dontcare) + SPEC-file-parsing (not hardcoded thresholds).
- **Assets A**: SPEC.sp (verbatim) + reconstructed measure files (tran.mt0 12 corners, ac.ma0 12 corners,
  tran_mc.mc0 500-sample stats) faithfully reproducing golden PASS/FAIL.
- **hidden B**: DIFFERENT SPEC thresholds (looser unload ±10mV/mc 15mV/gain >30dB/gbw >500kHz/rspon <150ns;
  tighter load1mA ±2.5mV) + DIFFERENT measure values + 8 corners (A=12) → forces SPEC-parsing + generalization
  (hardcoding A's thresholds yields wrong B judgments: unload would wrongly FAIL, gain would wrongly FAIL,
  rspon would wrongly FAIL, unload_mc would wrongly FAIL).
- **reference**: judge_sim_vs_spec_ref.py (regex SPEC parser + column/stats measure parsers + aggregator).
- **check.py**: k=13 (a..m) — zip+py_compile/run-exit0/5-categories/tran unload PASS/load1mA FAIL/undershot PASS/
  tran_mc unload_mc PASS/ac Gain PASS/ac GBW PASS/rspon PASS(catch hardcode)/measured-values/n=8.

## Distinctness vs existing Vcc2sc cases
- Vcc2scActDeckGen-001 (b86q7): generate ONE .sp deck from netlist (deck-gen, not judge)
- Vcc2scPVTvar-001 (4ujp9): run hspice + PVT variation (B-档 synthesized run)
- Vcc2scVarJudge-001 (z6mt7): parse single .mt0 + single variation SPEC judge
- **SimSpecJudge-001 (this)**: parse 3 measure types + multi-category multi-operator SPEC + SPEC-file-parsing
  → distinct deliverable (multi-type SPEC-compliance report generator).
