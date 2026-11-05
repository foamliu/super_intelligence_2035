# Deepread: sid 1793792373749_l5r0u — IO buffer 参数调参 (elianaz@hfeg0pkn002)

- trace: `/home/elianaz/.cline/data/sessions/1793792373749_l5r0u/1793792373749_l5r0u.messages.json` (1.20MB, 230 msgs)
- model: deepseek-v4-flash, cwd `/home/elianaz`, started 2026-11-04 11:39 UTC, status idle
- match_count=218, spice tools: 125 hspice(finesim)/44 netlist/10 pyAether/4 schematic (spice_ratio 满足 ≥35%)
- domain: spice_sim (A-档 trace-faithful)

## 用户首轮意图（逐字，clean 提出需求轮 — 无根因/无方案）
> `@/rundata/drcoa/V0/simdir/finesim/workdir/elianaz/simulation/99_IO_buffer/001_z_top_drgqa_slow_MC_PDA_TT.sp用这个文件跑仿真，调整参数值，使measure得到的data_H的值大于等于0.99*VDDQ，data_L的值小于等于0.001，参数范围如下LR56大于等于2.5u，小于等于3.5u，LMP12大于等于0.5u，小于等于1.5u，WMP12大于等于5u，小于等于6u，WP1大于等于1u，小于等于3.5u，WN1大于等于1u，小于等于3.5u`

判定为 clean A-档提出需求轮：用户给文件 + 明确 SPEC(data_H≥0.99*VDDQ, data_L≤0.001) + 5 参数范围，要求"跑仿真并调参"。无根因、无修复方案。

## 输入 .sp 结构（真实 001_z_top_drgqa_slow_MC_PDA_TT.sp, 4668B, 119 行）
- Option/Model: `.inc finesim_option_new` + `.lib model.sp tt` + bjt/res/nicap/diode_tt
- 基础 corner 0: TT, .temp 25, VDDQ=1.1
- 5 可调参数(行 53-57): WP1=2.25u, WN1=2.75u, LR56=4u, LMP12=1.2u, WMP12=5.4u
- netlist: `.inc IO_DqPrampBuf.spf.TYP_25_RCC_1030` + XIO_DqPrampBuf 实例 + switch.sp
- 仿真: `.tran 5p 50n sweep monte=50`
- measure: `.meas tran data_H find v(d_out) at 8n` / `.meas tran data_L find v(d_out) at 35n`
- 3 个 .alter corner:
  - alter#1: ss, -40°C, VDDQ=0.94
  - alter#2: fs, 110°C, VDDQ=1.3
  - alter#3: fs, 110°C, VDDQ=1.5  ← 最差 corner

## 仿真结果（真实 .mt0.csv, 61722B, 50 monte/run × 4 corner）
- corner 0 (TT/25/1.1V): data_h≈1.1(=VDDQ ✓), data_l~4e-8 (✓)
- corner 3 (FS/110/1.5V): data_h ~1.5µV（远低于 0.99*1.5=1.485V）→ FAIL
- 根因(assistant A#229 诊断): 高电压+高温+fast-NMOS/slow-PMOS → NMOS pull-down 过强相对 PMOS pull-up

## agent 交付（金标准）
- `optimize_io_buffer.py` (11373B): regex 解析 .param → 替换 5 参数 → 改 monte 运行数 → 调 finesim → 解析 .mt0.csv → per-corner pass/fail
- 6 个 combo deck (combo1: WP1=3u WN1=2u LR56=3.5u LMP12=800n WMP12=5.8u，全部在范围内)
- `run_finesim.sh`: 循环跑 6 combo
- 调参方向(物理): LR56↓(削弱 pull-down leg) / LMP12↓(短 PMOS→强) / WMP12↑(宽 PMOS→强) / WP1↑(宽 pre-driver PMOS) / WN1↓(窄 pre-driver NMOS→弱 contention)

## case 抽取（EDA-Eval-DesignFlow-IoBufParamTune-001, spice_sim A-faithful L2）
交付 = 通用 `tune_io_buffer.py <input.sp> <output_dir>`：解析 deck 5 可调 .param + .alter corner VDDQ + .meas → 识别最高 VDDQ 最差 corner → 在用户范围内按物理方向调参 → 产 tuned .sp(仅改 5 .param 行) + report.json。
- assets A: 真实 .sp(verbatim) + prompt.txt(原话逐字) + task_brief.md(≤3 行接口)
- hidden B: 3 corner(TT/40C/1.21V, SS/-25C/1.02V, FS/125C/1.62V)，measure at 6n/30n，起始参数 WP1=2.0u WN1=3.2u LR56=4.2u LMP12=1.4u WMP12=5.1u(≠A)，netlist include 不同 → 强制通用解析防硬编码
- check.py k=13 断言 a..m: zip+py_compile / B exit0+产物 / report 6 键 / 5 参数在范围 / 5 参数已改 / .meas 保留 / .tran 保留 / .inc/.lib 行数不变 / 仅改 5 .param 行 / 最差 corner VDDQ=1.62 / 方向与 sign 一致 / original_params=B 实际值(防硬编码) / measure_targets 编码 SPEC
- negatives 4: naive_empty / naive_midpoint / hardcode_A / copy_input + ref_minus_core §4.9(c)
- self-verify ALL PASS: ref PASS(13/13) + 4 negs FAIL @ 预期 + §4.9 三假(空壳/print_stub/ref_minus_core)全 FAIL
- 断言闸门: k_rationale=13=k_check=13≥8 ✓
