# Deepread: 7ycbz — DDR4 DQS duty/skew window-averaged measurement (joeyl)

- **trace**: `1791958847728_7ycbz.messages.json` (joeyl @ hfeg0pkn004, mc=53, hspice=274, finesim, 249 msgs, 1.5MB)
- **session path**: `/home/joeyl/.cline/data/sessions/1791958847728_7ycbz/1791958847728_7ycbz.messages.json`
- **tool histogram**: 274 hspice / 69 netlist / 10 schematic / 9 pyAether (FineSim tran + .mt0.csv + python post-processing)

## Real task (user voice)

- **T0** (pure need, A-档 compliant): `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/003_gain/002_wckdiff_gain_tran.sp  请看这个激励，我想测它一段时间的平均duty和skew，目前的这种测量方式只能测量单个duty或skew，且因为测量的信号由divider生成，边沿个数不确定，经常多量或少量一个周期，你有办法解决这个问题吗？`
- **T58**: `所以是要仿真完后额外运行后面的python3命令么` → confirmed workflow (sim then python post-process).
- **T60**: `我直接跑仿真发现好多error` → diagnosed: errors are harmless (reserved RISE/FALL=1..32 but only 14-15 real edges in window; FineSim writes literal `error` for nonexistent edges).
- **T79** (deliverable spec): `能不能做2个通用的处理文件，一个python程序，一个可编辑的cfg文件，cfg文件中包括 1.delay 2.number 3.duty 4.vth 5.edge(rise/fall) 6.skew(两两一组) 7.dir(抓取目录下所有tr0)  最终生成一个csv，如果duty或者skew不填，那就不生成对应的值`

## What the agent did

1. Read the deck + historical `tran1/*.mt0.csv` (FineSim measform=3). Confirmed the bug: hardcoded `td=3.065n + rise=5/fall=6` → some alter rows `duty_out0=1.47~1.53` (extra cycle) and `skew2=2.4e-10` (5 UI, should 1 UI).
2. Built `gen_meas_edges.py` → generates 256 `.meas` statements that dump EVERY vth-crossing time (rise/fall × 4 signals × 32 idx) into `.mt0.csv`.
3. Built `avg_duty_skew.py` — window-averaged duty & skew from `.mt0.csv`:
   - complete-cycle pairing (pair rise→next-fall→next-rise, drop partial boundary cycles)
   - cross-period skew wraparound (mod UI → [-UI/2, +UI/2))
   - glitch filtering (reject double-edges)
   - "error"/missing edge handling
4. Validated with synthetic data (ALL TESTS PASSED at a50: duty 50.0000%, skew matches constructed values to 1ps, glitch injected → still correct) + real `tran1/*.mt0.csv`.
5. **T79 pivot**: user asked for a generic python+cfg that reads `.tr0` binary directly. Agent spent ~20 iterations (a80-a247) reverse-engineering the FineSim binary `.tr0` format (name encoding, row-major vs column-major, time units, data-start offset) — got CLOSE (found 1949 names, stride 1955 floats, 2823 rows matching elog) but never closed the column-mapping. Editor tool kept intermittently dropping the `path` parameter, blocking progress. **Session ends with .tr0 parser incomplete.**

## Gold standard (what was actually validated & accepted)

The `.mt0.csv` edge-dump + `avg_duty_skew.py` averaging approach (steps 1-4) was validated and accepted. The `.tr0` direct-read (T79) did NOT complete. → The portable sub-skill = **edge-time dump + window-averaged duty/skew with complete-cycle pairing + cross-period skew wraparound + edge-count ambiguity resolution**.

## Distinct vs existing B cases

- Tr0TrTfMeas = single tr/tf measure; OtaAcReport = AC metric extraction; CTLEtranChar = transient eye; TaperBufOpt = DOE PDP; PorCapSweep = POR cap sweep; SiOutDiag/LvlshftBsubDiag/SaNPsimDiag = sim failure diagnosis.
- **This case = multi-period window-averaged duty & skew with edge-count ambiguity resolution + configurable cfg + CSV report** (shard B first "duty/skew averaging" case). Distinct sub-skill.

## Portable design (case EDA-Eval-DesignFlow-DutySkewAvg-001)

- Edge-time dump as clean long CSV (`sig,dir,idx,time`; `time="error"` for reserved-but-nonexistent edges) — models the real FineSim `.mt0.csv` edge-dump + the "error" literal pattern. Edge times derived from REAL HSPICE PULSE ramp crossing maths (tr/tf ramps at vth), so physically faithful.
- 4-phase same-frequency outs (out0/out1/out2/out3, different per-signal pw → duty & rise/fall skew differ) + a pw-drift duty signal `dut` (so `delay` parameter matters).
- Candidate delivers `duty_skew_avg.py` (CLI: `<edges_csv> <cfg_json> <out_csv>`) + `out_A.csv`.
- check.py 16 conditions (a-p): zip/py_compile/B-exit/header/A-match(duty+skew)/B-match(duty+skew)/ambiguity/cross-input/error-handling/duty-only/skew-only/edge-dir/delay/number.
- Hidden B: different P (1.5 vs 1.0), pw (duty 0.33-0.48 vs 0.45-0.55), phase, window (delay 3.2/tstop 13.4 vs 2.5/10.5), edge direction (fall vs rise), wrap_period (1.5 vs 1.0).
- Core traps: (1) naive fixed-index `rise=5/fall=6` gives negative duty (dangling fall at window start) → (i); (2) cross-input hardcode-A → (g)(h)(j); (3) crash on "error" → (k)(c); (4) print-expected → (e)(f); (5) edge-direction ignored → (n); (6) delay ignored → (o) via pw-drift `dut`.

## Selftest (local)

- ref **PASS 16/16**; 5 negatives ALL FAIL with distinct fail sets:
  - naive_empty → all (a-p)
  - naive_fixed_index (§4.9c core-deleted: ambiguity resolution removed) → e,f,g,h,i,n,o
  - naive_hardcode_a (cross-input attack) → g,h,i,j,l,m,n,o  [passes e,f]
  - naive_print_expected (§4.9b) → e,f,g,h,i,j,l,m,n,o  [fails e,f on A]
  - naive_crash_on_error → a,c,d,e,f,g,h,i,j,k,l,m,n,o,p  [crash c,k]
- §4.9 three fakes (empty/print-expected/core-deleted) all FAIL.
- test field == disk check.py (md5 58121592cf64227e64e7366965c00e32, 13740B, roundtrip OK).
- Assertion gate: k_rationale = k_check = 16 ≥ 8 ✓.

## Lessons

1. FineSim binary `.tr0` format is hard to reverse-engineer blind (row-major, 1955-float stride, variable-length name padding, ns time scale) — the agent burned 20+ iterations and never finished. The validated, portable sub-skill is the `.mt0.csv` edge-dump + averaging, NOT binary `.tr0` parsing.
2. The "edge-count ambiguity" is real: window placement creates a dangling fall before the first rise → naive `fall[k]-rise[k]` gives negative duty; correct = pair rise with NEXT fall bounded by next rise.
3. Cross-period skew wraparound (out2→out0 = -0.3P not +0.7P) is a distinct trap from duty.
4. To make `delay` a testable parameter, the dump must span wider than the measurement window AND a signal must have non-constant duty (pw drift) — otherwise duty is delay-invariant for a regular pulse.
5. To make `edge` (rise vs fall) a testable parameter, paired signals need different pw (so fall-phase ≠ rise-phase offset).
