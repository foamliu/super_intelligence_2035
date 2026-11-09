# Deepread: 1hei0 (kannik@hfeg0pkn001=10.129.2.10) — PowerPlan svwf signal expand

## Trace
- session: `1794035176106_1hei0.messages.json` (kannik, 1.28MB, 197 msgs, mc=199 digital markers)
- host: 10.129.2.10 (hfeg0pkn001), user: kannik, group drgqx
- ts first: 1794035176551 (2026-11-07 15:06)

## Conversation flow
- USER#0 (analysis): `/proj/drgqx/V0/simdir/verilog/kangyue/verilog.ddr5.drgqx.test/log.test/powerplan.x8 结合仿真环境，分析下为什么会报错？` → assistant greps xrun.log, analyzes bind errors (analysis-only, not a deliverable).
- USER#1 (analysis Q&A): `那为什么第一个bind的bind AG_Vad2BIAct没报错？？？？`
- USER#2/3 (intermediate, analysis continuation)
- **USER#last (PRODUCE-task, the viable turn)**:
  > `/proj/drgqx/V0/workdir/kannik/signalsforpowerplan.svwf`
  > 这个文件里面保存了一些信号，这些信号是一些电源的输入控制信号。帮我找出这些信号，在芯片中其他所有hireachy，并且保存在signalsnew.svwf文件里。
  > 网表可以参考/proj/drgqx/V0/simdir/verilog/kangyue/verilog.ddr5.drgqx.test/netlist/V0_WOWTOP_2026Nov6.122616/netlist
  > 务必要把所有bank group、所有bank里面的这些信号，全都找出来！！
  - A-faithful ✓: user states a GOAL (find power-control signals across ALL hierarchies, all bank groups/banks, save to signalsnew.svwf); does NOT give root cause or fix. Pure target request.

## Assistant produce (golden)
Assistant wrote a series of probe scripts then **`generate_svwf.py`** (the final golden, /home/kannik/generate_svwf.py, readable, 61 lines) + `search_signals.py` (145 lines, analysis/probe) + `verify_paths.py` (89 lines, verification).

### generate_svwf.py logic (THE GOLDEN, parameterizable)
Fixed hierarchy prefix `TOP.Chip.Ictop.I_Channel`. Emits a SimView Waveform Format (svwf) TCL file:
- Header: `# Mnemonic Maps`, `mmap new -reuse -name {Boolean as Logic} -radix %b`, `array unset createdGroup` / `array set createdGroup {}`.
- **Bank Group Power Control Signals**: cross-product of
  - halves: `['I_BnkGTopX4_Top','I_BnkGTopX4_Bot']` (2)
  - selectors: `['AC','BD','GE','HF']` (4)
  - path: `{pre}.{half}.I_BnkGTopX4_gut.I_BnkGTop_{sel}.I_AG_AnalogBankX2L_0`
    - `.I_AG_AnalogAryCtrlEdgeE` → 4 edge signals: `VblhhActEn_BK01, VblhhActEn_BK23, VblenActEn, VblhmActEn`
    - `.I_AG_AmpBankGlbCtrl` → 4 amp signals: `AryGlbActAmpEn0..3`
  - per group: 1 label line + 4+4=8 `waveform add -signals` lines
  - bank signal-add count = 2×4×8 = 64
- **Array VblhhDrvIn_Bot Signals**: cross-product of
  - halves: `['I_Array16G_T','I_Array16G_B']` (2)
  - bg_pairs: `['BGAB01','BGAB23','BGBB01','BGBB23','BGGB01','BGGB23','BGHB01','BGHB23']` (8)
  - regions: `['Far','Near']` (2)
  - path: `{pre}.{half}.I_Array2G_{bg}.I_Array1G_Top_{r}.I_m1G_TOP_{r}.I_R_XdecGap_32_{r}.VblhhDrvIn_Bot[1:0]`
  - per group: 1 label + 1 signal-add
  - array signal-add count = 2×8×2 = 32
- Footer: `waveform xview limits 0 34752.371ns`
- **Total signal-add lines = 64+32 = 96**; label lines = (2×4) + (2×8×2) = 8+32 = 40.

### svwf line format (exact, from golden)
```
set id [waveform add -label "............... {half}/{sel} ..............." -comment {}]
set id [waveform add -signals [subst  {
  {[format {{path}.{signal}}]}}
} ]]
```

## Permission reality
- Input `signalsforpowerplan.svwf` @ `/proj/drgqx/V0/workdir/kannik/` → **Permission denied** (e0031982 not in drgqx group; /proj/drgqx is `drwxr-s--- cadmin drgqx`).
- Netlist @ `/proj/drgqx/.../netlist` → also denied.
- Golden output `signalsnew.svwf` @ `/proj/drgqx/V0/workdir/kannik/` → denied (not readable).
- BUT assistant scripts in `/home/kannik/` (generate_svwf.py, search_signals.py, verify_paths.py) ARE readable (`-rw-rw-r-- kannik drgqx`).

⇒ **A-档 infeasible** (input + golden unreadable). → **B-档 synthesized**: golden = generate_svwf.py logic (parameterized cross-product → svwf). A = spec.json (the A config) + prompt (USER#last verbatim) + task_brief. hidden B = different spec (different halves/selectors/bg_pairs/regions/signals/prefix) → generator must produce correct svwf for B.

## Case build plan
- **case_id**: `EDA-Eval-DesignFlow-PowerPlanSignalExpand-001`
- **domain**: verification (verilog netlist / waveform signal expansion)
- **track**: B-档 synthesized; **level**: L1-static+subprocess
- **deliverable**: `gen_powerplan_svwf.py` — reads `spec.json` (argv[1]) + writes svwf (argv[2])
- **A assets**: `spec_a.json` (the 2/4/8/2 config above, faithful to golden) + `prompt.txt` (USER#last verbatim) + `task_brief.md` (≤3 lines: CLI contract)
- **hidden B**: `spec_b.json` — different config (5 selectors, 7 bg_pairs, 3 regions, different halves/insts/signals/prefix/xview) → counts differ from A (bank=2×5×7=70, array=2×7×3=42, total=112; A total=96)
- **check.py**: 16 assertions a-p (zip/script-runs/svf-structure/header/xview-B/bank-count/array-count/total/bank-path-no-A-literals/array-path-no-A-literals/edge-sigs-present/amp-sigs-present/array-sig-present/label-count/no-A-hardcode/determinism-3seed)
- **negatives**: noop / hardcode-A / stub; §4.9 fakes: empty/print/core
