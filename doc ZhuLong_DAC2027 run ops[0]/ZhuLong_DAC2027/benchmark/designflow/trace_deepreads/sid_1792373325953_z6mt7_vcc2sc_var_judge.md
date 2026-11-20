# Trace deepread — sid 1792373325953_z6mt7 (Vcc2scStdby tran PVT-variation SPEC judge)

- **session**: `/home/tongni/.cline/data/sessions/1792373325953_z6mt7/1792373325953_z6mt7.messages.json`
- **user/host**: tongni @ hfeg0pkn001 (10.129.2.10)
- **match_count**: 83 (hspice 351 / netlist 29 / calibre 8 / schematic 3 → ratio 0.898)
- **size**: 392,651 B, 121 messages
- **snapshot**: 19:2x rescan `ssh_eda_search_20261105_192825/spice_candidates_NEW.tsv` (NEW vs 10-28)
- **domain**: spice_sim (finesim PVT-corner tran + .MEASURE parse + SPEC judge)

## User intent (verbatim, A-档 clean 提出需求轮)

USER#0 (原文逐字):
> /home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scstdby_tran.sp 用 bsub -q fqueue3 finesim -i Vcc2scstdby_tran.sp -o /proj/dscqa/V0/simdir/hspice/tongni/7_Vcc2scStdby/261019sim_Vcc2scStdby_tran/ 这个语句丢仿真，/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scstdby_tran_SPEC.sp这个是我们的SPEC，variation 是 所有corner的电压的分布范围要小于5mV，所以你要读取measure的文件，做判断，并给出优化策略

= clean A-档: gives sim command + SPEC file + **quantifiable SPEC (variation < 5mV across all corners)** + task (read measure file, judge, give optimization strategy). No root cause, no fix proposed.

USER#91 (mid-session, after sim done): "现在仿真已经跑完了， 你帮我分析一下是否 符合Spec的标准，并给出优化意见" — reaffirms the same goal.

## Assistant tool chain (key)

1. list_allowed_files / read_files → SPEC.sp + tran.sp + check_vcc2sc_stdby_var.py + wrapper
2. run_approved_command → ls outdir, cat pvt_vcc2sc.sp corner file
3. **env debugging arc** (msgs 15-43): LSF `res` launcher crashed because agent's `LD_PRELOAD` (new libstdc++ needing GLIBC_2.18) leaked into job env → fix by NOT using `bsub -env all`, building minimal clean env. Then license env (`SNPSLMD_LICENSE_FILE`/`LM_LICENSE_FILE`) had to be forwarded explicitly.
4. submit_finesim.sh → bsub job 993022 (5 PVT alter blocks: base/typ/low/high/ulow, 121 actual corner rows after MC unfold)
5. poll_wait.sh (repeated) → sim DONE ~2.8h, no ERROR
6. read_files mt0:1-15 → real `.mt0` format recovered (see below)
7. run_check.sh → checker FAIL (case-sensitivity bug: finesim lowercases metric names `vcc2sc_load1ma` vs SPEC `Vcc2sc_load1mA`)
8. editor fix checker → case-insensitive metric match + min/max corner bug fix
9. analyze_detail.py → per-temperature breakdown
10. run_final.sh → final judgment + optimization

## Real artifacts (fetched to .75 workdir)

- **Vcc2scstdby_tran_SPEC.sp** (2 lines, verbatim):
  ```
  Vcc2sc_unload Variation<5mV
  Vcc2sc_load1mA Variation<5mV
  ```
- **Vcc2scstdby_tran.sp** (28 lines, verbatim): `.tran 1n 300u`, `iload` PWL (0→0.1mA@50u→1mA@100u→0.1mA@150u), two `.MEASURE TRAN ... AVG V(Vcc2sc!)`:
  - `Vcc2sc_unload FROM=60u TO=70u` (the 0.1mA segment — "unload" is actually 0.1mA, noted in optimization)
  - `Vcc2sc_load1mA FROM=110u TO=120u` (the 1mA segment)
  - `.inc pvt_vcc2sc.sp` (5 alter blocks)
- **check_vcc2sc_stdby_var.py** (182 lines, fetched verbatim): the golden checker (post-fix). Parses `.mt0`/`.ms0`/`.mm*`, case-insensitive metric match, computes variation=max-min, judges vs SPEC limit, reports min/max corner.
- **Vcc2scstdby_tran.mt0** (permission-denied via scp, owned tongni:dscqa 660): real format recovered from trace read_files (lines 1-15):
  ```
  $DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0
  .TITLE '*******option**********'
    vcc2sc_unload vcc2sc_load1ma         temper         alter#
       9.0122e-01     9.0044e-01     8.5000e+01     1.0000e+00
       9.0016e-01     8.9964e-01    -4.0000e+01     2.0000e+00
       ... (12 rows verbatim, 121 total)
  ```
  → faithfully reconstruct 121 rows matching golden summary (see case assets).

## Golden SPEC judgment (ASST#120, the accepted final answer)

Sim: job 993022 DONE, 2.8h, 121 PVT corners, no ERROR. Measure file `Vcc2scstdby_tran.mt0`.

| 指标 | 限值 | min | max | variation | 判定 |
|---|---|---|---|---|---|
| Vcc2sc_unload `V(Vcc2sc!) 60u~70u` | <5 mV | 897.24 mV | 902.37 mV | **5.130 mV** | **FAIL** (超 2.6%) |
| Vcc2sc_load1mA `V(Vcc2sc!) 110u~120u` | <5 mV | 886.30 mV | 901.56 mV | **15.260 mV** | **FAIL** (超 3 倍) |

Overall SPEC = **FAIL**. mean: unload 0.900699, load1mA 0.898408.

Per-temperature breakdown:
| 温度 | corner 数 | unload var | load1mA var |
|---|---|---|---|
| 85°C (typ/base) | 1 | — | — |
| -40°C (low) | 60 | 3.70 mV | 10.94 mV |
| 130°C (high) | 60 | 1.82 mV | **15.26 mV** |

- load1mA min @ alter 115, max @ alter 83 (both 130°C) → 真正超标点集中在 130°C 高温 + 工艺散布
- unload 跨温度漂移 (冷端低 897mV, 热端高 902mV)

## Root cause + optimization (accepted)

1. **电路级 (优先最高)**: 提高误差放大器/环路直流增益 (减小 load regulation 及 PVT 敏感性)；加强输出级驱动/降低输出电阻 (针对 1mA 满载, 增大输出管尤其热端/慢 corner)；确认带宽/稳定性 (1mA 阶跃后无振铃).
2. **参考/失调优化**: 0.9V 参考 + 放大器输入失调温度补偿/工艺修调 (trim)，把 -40°C 与 130°C 中心值拉齐.
3. **测试/测量方法级**: "unload" 实为 0.1mA 负载 (PWL 50~100µs=0.1mA)，若 SPEC 本意 0mA 应调整 iload；121 corner 用 max-min 判 5mV 苛刻，建议同时看 3σ.
4. **收敛性**: unload 仅超 0.13mV，先锁最小/最大角点复核 (-40°C alt100 最低, 130°C alt86 最高).

## Case design (A-档 trace-faithful, L2)

- **case_id**: `EDA-Eval-DesignFlow-Vcc2scVarJudge-001`
- **deliverable**: `judge_vcc2sc_var.py <mt0> <spec> <out.json>` — parse finesim `.mt0` (skip `$DATA1`/`.TITLE` header, read column header `vcc2sc_unload vcc2sc_load1ma temper alter#`), extract per-metric values, compute variation (max-min) + mean + n_corners, case-insensitive match SPEC metrics → judge PASS/FAIL, per-temperature breakdown, root-cause hints + optimization suggestions → structured JSON.
- **assets/A**: reconstructed `Vcc2scstdby_tran.mt0` (121 rows, FAIL, golden stats), real `SPEC.sp`, real `tran.sp`, `prompt.txt` (verbatim USER#0), `task_brief.md` (≤3 lines).
- **hidden B**: `Vcc2scstdby_tran_B.mt0` (different: 81 corners, 3 temp blocks 25/-40/125°C, **PASS unload 3.2mV / FAIL load1mA 8.5mV**, different metric names `vcc2sc_vout_light vcc2sc_vout_full`, different alter numbering 1..81) + `SPEC_B.sp` (limits <4mV). Forces generalization (no hardcode of 121/-40/130/Vcc2sc names/5mV).
- **reference**: `judge_vcc2sc_var_ref.py` + `check.py` (k≥8 assertions) + negatives + negative_selftest.
