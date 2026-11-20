# Trace deepread — 1789713740053_1fgo2 (spice_sim, PrimeSim si.out perf diagnosis + probe/step tuning)

- **trace_source**: user `ynbai`, host `hfhds206`, session `1789713740053_1fgo2.messages.json` (955 KB, 99 msgs, ~13 user / 86 assistant), match_count 179.
- **keywords/tools**: netlist 193, hspice 6, schematic 4, pyAether 2. Tools: read_files 30, search_codebase 5, list_allowed_files 3, run_commands 1 (disabled), RAG search 1.
- **working context**: DRAM fullchip PrimeSim/FineSim transient signoff (`/proj/drvqa/V0/simdir/finesim/drvqaF/MatrixRun/...`). User reads real `si.out` reports to diagnose why a 1.98us transient takes 6.7h / 25h-CPU.

## User intent (verbatim, substantive turns)
- U#0: `can you read linux document, analys why sim too slow, primesim sim output report at .../primesim.Golden003_..._20260915PM.../si.out path`
- U#3: `compare with .../primesim.Golden003_..._20260901PM.../si.out, why 0901 fast & 0915 slow, with same primesim, any diff for netlist node number`
- U#4-#7: probe reduction — `如何实现probe信号的减少 ... 部分block probe较少信号，部分全部probe` + a real `.probe v(XIctop.XI_Channel.*) ...` list + `限制probe后的primesim输出文件.../si.out，probe数目是否有减少改善，仿真速度是否有改善`.
- U#8: `减少probe数量并没有有效降低transient的时间，是否有其他降低transient时长的方案`
- U#9-#12: `.tran` step segmentation — `对于trantime.sim当前为.tran 10ps 1979501ps，如何对关键时间段用小步长，非关键时间段用大步长 ... 在800ns处分段` + `分段会影响仿真精度么`.

## Assistant trajectory (real tool products in trace)
- read_files on real si.out excerpts (lines 1-100, 550-750, 950-1100, 1300-1450, 1580-1710, etc.) for the 0915-slow, 0901-fast, 0917-TT/SS runs.
- Produced three structured reports:
  1. **single-run diagnosis** (0915): total elapsed 24,271s (6.74h), transient 21,713s (89.5%), 968,787 time points, 6.9M MOS / 22.1M R / 43.7M C, `.IC` 978,040, peak mem 36.7 GB.
  2. **differential 0901 vs 0915**: 0901 is 1.85x FASTER despite 3.2x MORE devices and 8.5x more `.IC` (8,313,340 vs 978,040) → root cause is NOT size; it's threads (`-np 8` vs 4) + corner + burst mode. Probed signals 26.2M (0901) vs 9.14M (0915).
  3. **probe-reduction TT vs SS**: `.probe v(*)` (8.44M probed) vs limited probe (4.19M, ↓50.4%); output-prep time 312s→67s (↓78.5%); transient only marginally faster (probe cost is output/write, not matrix solve). Measures preserved.
- Proposed `.tran` segmentation (PrimeSim multi-`.tran`): `.tran 100ps 800n` + `.tran 10ps 1979501ps` (tstep = OUTPUT step; internal LTE step independent → measures preserved, output points reduced in quiet region). Noted 100ps still captures DDR5-2666 (tCK=750ps) edges.

## Case synthesis decision (B档, synthesized, L2)
- The sandbox (.75 FineSim V-2023.12) does NOT support multi-`.tran` segmentation (tested: `ERROR! no signal to print or probe`); and `reltol`/`finesim_*tol` relaxation did NOT change `# time points` at small scale (LTE clamped by tstep). So `.tran`-segmentation and tolerance-tuning sub-tasks are not reproducibly discriminative on .75.
- The **probe-trim** sub-task IS robustly reproducible on .75 FineSim: a deck with `.probe v(*)` (+ `.print` of many nodes) → `# probed signals: 88`; the same deck trimmed to `.probe v(in) v(out)` (+ `.print v(in) v(out)`) → `# probed signals: 2`, while `.measure tran tpd5`/`vout_mid` are IDENTICAL (probe selection affects only output/write cost, NOT matrix solve or measures). This directly mirrors the trace's TT-vs-SS probe-reduction finding (8.44M→4.19M probed, measures preserved, output-prep 312s→67s).
- **case = EDA-Eval-DesignFlow-ProbeTrim-001** (spice_sim, L2, B档): SUT submits `probe_trim.py` that takes an over-probed hidden B deck + the set of NEEDED signals (those referenced by `.measure`/`.print`), rewrites `.probe`/`.print` to keep ONLY needed signals, runs FineSim on BOTH full and trimmed decks, parses each `<stem>.log` for `# probed signals`, `# time points`, and the `.measure` results, and writes report.json. Check (14 conds a–n) verifies real FineSim ran (measures match GT), probe count was actually reduced, measures preserved within tol, trimmed deck has no `v(*)` wildcard and only needed signals, cross-input A guard, randomization, negatives.

## Real si.out numbers (gold-grounded, from trace tool_result excerpts)
- 0915-slow: `# signals with .IC: 978040`; DB Building mem 28566.7 MB; total elapsed 24,271s.
- 0901-fast: `.IC` 8,313,340; total elapsed 13,107s (3.64h); probed 26.2M; transient finished at 1419.473ns.
- 0917-TT: `# probed signals` 8,444,435; output-prep 312s. 0917-SS (limited probe): 4,187,262; output-prep 67s.
- (Used only for trace-fidelity grounding; the case's numerical GT comes from independent FineSim runs on the synthesized small-scale decks, not from these fullchip numbers.)
