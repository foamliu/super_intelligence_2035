# Deepread — op8wj: Vcc2sc_stdby LDO multi-deck SPEC-comparison sim generation

## trace_source
- **session**: `1794397721848_op8wj` (dir: `1794397721848_op8wj/1794397721848_op8wj.messages.json`)
- **user**: tongni · **host**: hfeg0plg49 · **match_count**: 1521 · **domain**: spice_sim/characterization
- **size**: 930KB · **NMSG**: 194 · **agent**: lead
- **ts_range**: 2026-11-12 (session) / template files 2026-10-27~29

## 用户意图（real task summary）
给定 Vcc2sc_stdby LDO 的 testbench netlist + SPEC 指标清单，生成 Tran/AC/AC_load/DC_capbi/Tran_MC 等仿真 `.sp` 文件，运行仿真并比对 SPEC。

用户三轮驱动：
1. msg 0：调 sim-sp-gen skill，给 testbench netlist + SPEC → 生成多 deck .sp 文件
2. msg 68：「把这些仿真文件丢上仿真，并比对SPEC」→ 跑 hspice + 比对
3. msg 144：「为啥没有仿真结果」→ 排查 sim 产出

## SPEC 指标清单（`/home/tongni/Desktop/1_Vcc2sc_stdby/template/SPEC`，1434B）
5 段 × 共 ~18 个 .MEASURE 指标：
| 段 | 指标 | 含义 |
|---|---|---|
| ac_load | Vcc2sc_Gain_load1mA / PM / GM / GBW / f_3db | 1mA 负载下 AC 稳定性 |
| ac | Vcc2sc_Gain / PM / GM / GBW / f_3db | 轻载下 AC 稳定性 |
| dc_capbi | IVcc2sc | LDO Drop 30mV capbility（DC sweep） |
| tran_mc | Vcc2sc_unload_mc / Vcc2sc_1mA_mc | Monte Carlo 电压分布 |
| tran | Vcc2sc_unload / load1mA / undershot / undrmag / overshot / Rspon / tsetting / ring_ratio | PVT 瞬态响应 + 振铃判定 |

## .sp 模板结构（9 文件，均在 `template/` 目录）
每个 .sp 文件遵循固定 6 段结构：
1. `*******option**********` — `.inc hspiceconfig.sp`
2. `********netlist**************` — `.inc <netlist>.netlist`
3. `********power parameters*****` — `.inc power_tran.sp` + `.param res_sn=1 ...`
4. `********stimulus*************` — `.GLOBAL` + 电压源 pwl + iload + 分析类型（.tran/.ac/.dc）
5. `********measurement**********` — `.MEASURE` 语句（对应 SPEC 指标）
6. `********pvt******************` — `.inc pvt_vcc2sc.sp` 或 inline MC params

**分析类型分布**：
- `Vcc2scstdby_tran.sp`: .tran 1n 300u, iload pwl, 9 个 .MEASURE（稳态/undershoot/overshoot/响应时间/恢复时间/振铃）
- `Vcc2scstdby_ac.sp`: .ac DEC 100 1 10G, .lstb, 5 个 .MEASURE（Gain/PM/GM/GBW/f_3db）
- `Vcc2scstdby_ac_load.sp`: 同 ac 但 iload=1mA
- `Vcc2scstdby_dc_capbi.sp`: .dc pvalue 0.7 0.95 0.002, 1 个 .MEASURE（IVcc2sc at=0.87）
- `Vcc2scstdby_tran_mc.sp`: .tran 1n 300u sweep monte=500, 2 个 .MEASURE（MC 电压）
- `Vcc2scstdby_psrr.sp`: PSRR 分析
- `Vcc2scSense_delay.sp` / `Vcc2scSense_offset.sp` / `Vcc2scSense_offset_mc.sp`: sense amp delay/offset

## .inc 依赖路径（不可移植，case 合成需替换）
- hspiceconfig: `/proj/dscqa/V0/simdir/hspice/corner/hspiceconfig.sp`
- netlist: `/proj/dscqa/V0/workdir/tongni/simulation/tongni_..._Vcc2scStdby_sim_schematic_ALPS/....netlist`
- power: `/proj/dscqa/V0/simdir/hspice/corner/power_tran.sp`
- pvt: `/proj/dscqa/V0/simdir/hspice/corner/pvt_vcc2sc.sp` / `volt.sp` / `corner.sp`

## case 合成（r1260 已合成 → EDA-Eval-DesignFlow-Vcc2scMultiDeckSpecCompare-001）
**任务形态**：给定自包含 LDO behavioral netlist + SPEC 清单 + testbench stimulus 模板，生成多 deck .sp 文件并在 mock-hspice 上跑仿真，产出 SPEC-comparison 报告。

**自包含策略**（参照 B 现有 hspice-mock 模式，如 BistOscRccReorder/SpiceSim）：
1. **inline netlist**：合成简化 LDO behavioral 模型（EA + PFET + 反馈分压 + 补偿），variant A=GA70PM60（全 PASS）/ B=GA55PM45（部分 fail），替换 .inc netlist
2. **hspice-mock**：deck-driven python 桩，解析 .sp 的 `.meas <type> <name> param='value'` 语句回放测量值（与真 hspice param= 行为一致 → 36.15 mock 与 .75 real 结果一致），忠实缺失 .inc netlist 报 cannot-open-include abort rc=1
3. **SPEC 清单**：16 指标 4 段（tran 8 / ac 5 / dc_capbi 1 / tran_mc 2），目标范围
4. **check.py 13 conds (a-m)**：①zip 6 文件 ②6 段标记 ③tran .tran+>=8 meas ④ac .ac+.lstb+>=5 meas ⑤dc .dc+>=1 meas ⑥tran_mc sweep monte+>=2 meas ⑦.inc 便携 ⑧mock 跑 tran A Vcc2sc_unload≈0.900 ⑨spec_compare>=16 ⑩A 全 PASS ⑪B gen .inc B netlist ⑫B mock≈0.895≠A ⑬B spec_compare≈0.895
5. **hidden B**：variant GA55PM45 不同 LDO 参数，同 SPEC 范围
6. **negatives**：4 negs distinct first-fail {a,b,i,l}（empty/print_expected 缺 pvt 段/core_deleted spec_compare 仅 2 条/hardcode_a B 写 A 值）

**reframe**：ac_load 折叠进 ac（iload 参数化），保留 4 deck 覆盖 .tran/.ac/.dc/sweep monte 4 分析类型。

## 当前状态
- **r1260 已合成并交付**：EDA-Eval-DesignFlow-Vcc2scMultiDeckSpecCompare-001（cases/B/ + assets/ + reference/ + hidden/，已 push EDA-Flow-Bench master）
- **自验**：negative_selftest ref PASS 13/13 + 4 negs FAIL distinct{a,b,i,l} §4.9 trio 3-distinct NEG_RC=0；reference_submit.zip check.py PASS 13/13；SKIP_RUN run_one.sh 框架部署无报错
- **DEBT**: 0（op8wj 深读→合成本轮闭合）
- **ibtdi** (rose3wang, mc=121): peek 确认 wrong-domain（Verilog/RTL/STA timing-check，非 spice），mark parked
