# eypbp — PWL converter (waveform, A-faithful)

trace: 1791458509461_eypbp (joeyl@hfeg0plg74, mc=18, waveform)
session: 72 msgs. U#0 = clean single-shot 提需求 (未指出根因 ✓).

## U#0 verbatim (paths → basename for bench)
```
power.sp

这个是power导出的波形，链接应该是 VVDDQ VDDQ 0 PWL（……

请把它整理成
dqsn
这样的参考格式
```

## 数据格式（trace 实测）
**power.sp**（源，波形工具导出）:
```
Time [ns]\tV(DQS_TX) [mV]
0\t1099.197953
0.005\t1099.197982
...
```
- 1 表头 + 54186 数据点；时间 ns、电压 mV、tab 分隔；时间 0→152.8525 ns 不等间隔。

**dqsn**（参考格式，Custom WaveView SPICE PWL export）:
```
*** Custom WaveView SPICE PWL EXPORT (version T-2022.06-SP1 build Aug 20, ) ***
*** created at 19:26:25 on Thu Jul 23 2026
V_DQS_N DQS_N 0 PWL(
+ 0.000000E+00  1.300000E+00 
+ 339.772920E-07  1.303235E+00 
...
+ 34.530671E-06  1.299999E+00 
+)
```
- 2 行 `***` 注释头；源语句 `<inst> <node> 0 PWL(`；续行 `+ <t_s %.6E>  <v_V %.6E> `（列间两空格、行尾空格）；末行 `+)`。
- 用户指定源语句为 `VVDDQ VDDQ 0 PWL(`（NOT 从 dqsn 抄；dqsn 仅为格式模板）。

## agent 行为
- read_files power.sp + dqsn → 比对格式 → 写 convert_pwl.py（hardcoded SRC/DST/SOURCE_LINE="VVDDQ VDDQ 0 PWL("）。
- 首次 run_approved_command 报 "File overwrite"（os.replace 触发 guard）+ header 检测 bug（`len(parts)==2` 漏判 4-token 表头）→ 改 `open(DST,"x")` + `parts[0].lower().startswith("time")` → 成功。
- 输出 vddq：54190 行，结构对齐 dqsn；ns→s、mV→V、%.6E、`+)` 结尾。后续 U#22/U#49/U#58 扩展到多列 `other` 文件（follow-up 提需求，非根因）。

## 金标（通用化）
generic CLI converter `pwl_convert.py <in> <out> "<source_line>"`：解析 2-col `Time[ns]/V(sig)[mV]` → Custom WaveView PWL（*** 头 + 源语句 + `+ %.6E  %.6E ` 续行 + `+)`），ns→s、mV→V、严格校验（列数/数值/时间严格递增）。check 在隐藏 B 上跑 SUT 提交件。

## 合成
- config_A: signal V(DQS_TX), source `VVDDQ VDDQ 0 PWL(`, 11 点 0–0.5 ns step 0.05, v≈1099 mV。
- config_B: signal V(VTT_TX), source `VVTT VTT 0 PWL(`, 25 点 0–0.48 ns step 0.02, v≈750 mV（信号名/节点/点数/时程/电压量级均不同）。
- check.py 14 条件 a–n；ref PASS / negs ALL-FAIL / §4.9 三假 distinct≥3。
