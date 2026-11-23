# Deepread: 1794808950452_6rxeo — CML Divider Duty/Lock Analyzer

**User**: joeyl @ hfeg0plg74
**Session**: 1794808950452_6rxeo.messages.json (121 msgs, 570KB)
**Domain**: characterization (B shard)
**mc**: 68 (keywords: .lef:494;netlist:435;transistor:38;opamp:27;hspice:6;schematic:8;cmos:6)

## User Intent (U0)

joeyl 在做 DDR4 DQS 的 CML divider characterization。divider 前级是 CML，电源 0.875V。
选通管 XNM4/XNM5 刚从 `nulvt_ckt` 改成 `nlvt_ckt`（为了在更高共模下让 nmos 更好关断）。
需要跑 Vref(0.4~0.7, step 0.1) × Swing(0.05~0.2, step 0.05) = 16 combos × 5 corners = 80 点
FineSim tran sim，检查 4 相输出（f0/f1/r0/r1）连续 5 次的 duty 是否都在 50%±2%，以及
divider 是否 lock。

bench: `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/5_DIVIDER/2_TRAN.sp`
handoff: `/ai_sandbox/m2701/V0_DDR4/agentdir/joeyl/HANDOFF_CML_divider_v3.md`

## Assistant Actions (121 msgs)

1. **msg 1-42**: 读 bench + handoff，探索 netlist，确认选通管位置（XNM4/XNM5），
   diff netlist 版本确认 nulvt→nlvt 变更。ask_question 确认选通管 = 时钟转向管对。
2. **msg 44-49**: 读 5-corner include + 现有 sweep DB，确认 `.pt0` 格式
   (`v(f0) v(f1) v(r0) v(r1) v(wckt)`)。计划：建 `nl_pyb` netlist + sweep runner。
3. **msg 49-53**: editor 创建修改后 netlist `nl_pyb`（XNM4/XNM5 = nlvt_ckt），
   创建 sweep runner `run_swvref.py`（基于 handoff 的 run_swvref.py）。
4. **msg 55-57**: 单 combo 验证（s0p05_v0p6），5 corner .pt0 全产出。验证 TB config。
5. **msg 59-67**: 写 **analyze_pyb.py** — duty cycle 分析器：
   - `load(path)`: 解析 .pt0（跳 `.` 行，header = 首个非 float 行，rest = 数据）
   - `xcross(rows,ci,mm,direction)`: midpoint 零交叉检测（rise: (p-mm)<0<=(v-mm)）
   - `duty_per_cycle(rows,ci,mm)`: 相邻上升沿间，第一个下降沿 → duty = (tf-t0)/per
   - `analyze(path,t0,duty_tol)`: 截取 t0 后稳态段，算 T_in(wckt)/T_out(f0)/ratio/locked/duty/skew
   - `report(tg)`: 按 corner 打表（duty%/skew%/max|dev|/DUTY-PASS）
   - lock 阈值初始 0.45 < ratio < 0.55
6. **msg 67-69**: 调整 PASS 标准：locked + 4 相 avg duty 全在 50±2%。验证 s0p05_v0p6 全 5 corner PASS。
7. **msg 69-92**: 跑完整 16 combos × 5 corners = 80 点（逐 combo 串行，因工具有 wall-clock 限制）。
8. **msg 92-96**: 写 **sum_pyb.py** — 矩阵汇总：SWING×VREF × corner 的 lock/duty-pass 矩阵 +
   cross-corner max avg-duty deviation 矩阵。
9. **msg 98-104**: 修 analyze_pyb.py 加 `__main__` guard + sum_pyb.py mode arg。
10. **msg 108-114**: **发现 lock 阈值 bug**：SS130 @ s0p05_v0p7 ratio=0.4504 被旧阈值(>0.45)放过，
    实际是 degraded ÷2.2（3.96G 而非 4.4G）。收紧到 `0.47 < ratio < 0.53`（匹配 handoff LOCK 定义）。
11. **msg 116-120**: 全 80 点验证 + 最终报告。

## Reframe

**case = EDA-Eval-DesignFlow-DividerDutyAnalyzerProduce-001**

把 `analyze_pyb.py` 行为程序化为独立 Python 脚本 `divider_duty_analyzer.py <pt0> <spec.json> <out.json>`：
- 读 FineSim .pt0 (time + v(f0)/v(f1)/v(r0)/v(r1)/v(wckt))
- 截取 t0 后稳态段
- midpoint 零交叉检测每相 duty cycle
- lock 判定 ratio = T_in/T_out, locked = lock_lo < ratio < lock_hi
- f0-r0 正交 skew%
- 输出 JSON: {T_in, T_out, ratio, locked, swing_mV, skew_pct, phases{...}, duty_pass}

**L1 纯 Python 无 EDA 依赖**，domain=characterization。

**A** (visible): 1 sample .pt0 (f_in=25.2GHz, ratio=0.5 locked, duty_f0=51%/f1=49%/r0=50.5%/r1=49.5%, skew=25%)
**hidden B** (4-file sweep grid, 全异 A):
- s0p08_v0p45: locked, duty pass (48.5/51.5/52.0/48.0)
- s0p08_v0p65: **UNLOCKED** ratio=0.44, duty fail (65/35/60/40) — 核心齿
- s0p18_v0p45: locked, duty pass (51.5/48.5/49.5/50.5)
- s0p18_v0p65: locked, **duty FAIL** (53.5/46.5/50.0/50.0) — 核心齿

**check.py 10 条件 (a-j)**: zip+compile+size / 4文件exit0+JSON / 8顶层键 / ratio<0.01 /
locked精确 / duty<0.5pp / skew<0.5pp / duty_pass精确 / anti-hardcode / 3-seed确定性

**3 negs**: neg1_empty(→a) / neg2_print_only(硬编A值→d/e/h) / neg3_core_removed(硬编locked+duty_pass=True→d/e/h)

§4.9 三假齐: (a)空壳→fail(a) (b)print-only→fail(d) (c)core-removed→fail(d) ✓
REF 10/10 PASS ✓, negative_selftest 3/3 FAIL ✓
