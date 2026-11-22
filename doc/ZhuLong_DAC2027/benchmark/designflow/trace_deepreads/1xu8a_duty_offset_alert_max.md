# deepread: 1xu8a — cspad_duty.mt0 pduty-offset processing → DutyOffsetAlertMaxProduce-001

**session**: `1794813983875_1xu8a.messages.json` (terrytao @ hfeg0plg74, mc9, spice_sim)
**scan**: `ssh_eda_search_20261121_151844/summary.tsv` (spice-dom: hspice:20 pdk:16 netlist:8)
**nmsg**: 79 (1.0MB), 3 sub-tasks

## Real user intent (verbatim, sub-task 1 = the case)

- U0: "把/rundata/ddgot/V0_Lay_20260723/simdir/finesim/workdir/terrytao/simulation/sim_cspadtiming_1113/result_duty/cspad_duty.mt0中dutyout列的数据按如下方式处理，所在行pduty为0.3的减0.7，0.5的减0.5，0.7的减0.3，处理后的数据去绝对值，以表格形式展示每个alert处理后数据的最大值，并将数据乘以227"
- U14: "将处理好的数据展示"（每行处理值）
- U20: "展示每个alert处理后数据的最大值和对应数据乘以227的值"（每 alert 的 max + 对应行 ×227）
- U36: "最大值 乘以227更正为乘以454"（multiplier 修正 227→454）

Sub-tasks 2/3（msgs 46-79）= delayvsvoltage corner .sp 生成 + run 脚本更新，不取（与本 case 无关）。

## .mt0 文件结构（从 trace tool_result 完整确认）

路径 `/rundata/ddgot/.../result_duty/cspad_duty.mt0`（FineSimPro 测量输出，e0031982 无读权限，从 trace 重建）。
列：`index  pvrefcs  pduty  tout  outh  dutyout  temper  alter#`
- pduty ∈ {0.3, 0.5, 0.7}（占空比设定值）
- pvrefcs ∈ {0.13, 0.30}（参考电压 corner）
- alter# = 1..9（9 个 alert/温度组）
- temper = {45, 130, 88, -33, -40, 130, 88, -33, -40}
- 每个 alter# 多行（pduty × pvrefcs 组合）

## 处理逻辑（agent 最终交付，msg 34/44 验证）

```
offset_map = {0.3: 0.7, 0.5: 0.5, 0.7: 0.3}   # offset = 1.0 - pduty
processed = abs(dutyout - offset_map[pduty])
per alter#: max_processed = max(processed) over rows in that alter
result = max_processed * multiplier   # multiplier = 454 (corrected from 227)
```

## 最终结果（msg 44，multiplier=454，9 alerts）

| alter# | temper | max\|dutyout−offset\| | ×454 | max_row(idx,pvrefcs,pduty,dutyout) |
|---|---|---|---|---|
| 1 | 45 | 0.018989 | 8.621052 | idx=3, pvrefcs=0.13, pduty=0.7, dutyout=0.281010900 |
| 2 | 130 | 0.028876 | 13.109838 | idx=3, pvrefcs=0.13, pduty=0.7, dutyout=0.271123704 |
| 3 | 88 | 0.029795 | 13.526746 | idx=3, pvrefcs=0.13, pduty=0.7, dutyout=0.270205405 |
| 4 | -33 | 0.035257 | 16.006557 | idx=3, pvrefcs=0.13, pduty=0.7, dutyout=0.264743265 |
| 5 | -40 | 0.035501 | 16.117265 | idx=9, pvrefcs=0.30, pduty=0.7, dutyout=0.264499416 |
| 6 | 130 | 0.020986 | 9.527437 | idx=2, pvrefcs=0.13, pduty=0.5, dutyout=0.520985544 |
| 7 | 88 | 0.014654 | 6.652766 | idx=8, pvrefcs=0.30, pduty=0.5, dutyout=0.514653670 |
| 8 | -33 | 0.002451 | 1.112593 | idx=8, pvrefcs=0.30, pduty=0.5, dutyout=0.502450646 |
| 9 | -40 | 0.002008 | 0.911443 | idx=3, pvrefcs=0.13, pduty=0.7, dutyout=0.297992417 |

验证：alter 1: |0.281010900 − 0.3| = 0.0189891 ✓, ×454 = 8.6211 ✓

## Reframe → EDA-Eval-DesignFlow-DutyOffsetAlertMaxProduce-001 (produce, L1, pure Python)

**Form**: `duty_offset_alert_max.py --mt0 <path> --spec <spec.json> --out <path>`
- spec.json: `{"pduty_offset_map": {"0.3":0.7,"0.5":0.5,"0.7":0.3}, "multiplier": 454}`
- Parse .mt0 列 by name (index/pvrefcs/pduty/tout/outh/dutyout/temper/alter#)
- Group rows by alter#
- For each row: offset = spec.pduty_offset_map[str(pduty)]; processed = abs(dutyout - offset)
- Per alter#: find max(processed), record the row (index/pvrefcs/pduty/dutyout/offset)
- Output JSON: `{alerts: [{alter, temper, max_raw, max_multiplied, max_row:{...}}], multiplier, n_alerts}`

**A** (assets/.../dir_A): cspad_duty_A.mt0 (5 alters × 6 rows = 30 data rows, pduty∈{0.3,0.5,0.7}, pvrefcs∈{0.13,0.30}, multiplier=454) + spec_A.json + prompt.md
**hidden B** (assets/.../hidden/dir_B): cspad_duty_B.mt0 (7 alters × 4 rows = 28 data rows, pduty∈{0.4,0.6}, pvrefcs∈{0.20,0.35}, multiplier=300) + spec_B.json
五重 anti-hardcode: pduty 集合 / offset map / multiplier / alter 数 / pvrefcs 集合 全异于 A

**check.py 12 条** (a-l):
①(a) zip+py_compile+size>200 ②(b) B exit0+output JSON ③(c) JSON 含 {alerts,multiplier,n_alerts} ④(d) n_alerts==7 (B alter count) ⑤(e) 每 alert 含 {alter,temper,max_raw,max_multiplied,max_row} ⑥(f) max_raw == 独立 oracle 复算(abs(dutyout-offset_map[pduty]) per alter max) ⑦(g) max_multiplied == max_raw × multiplier_B(300) ⑧(h) max_row 字段一致(offset=spec_B[pduty], |dutyout-offset|==max_raw, alter 一致) ⑨(i) 所有 max_raw >= 0 (abs 已取) ⑩(j) anti-hardcode: A pduty(0.3/0.5/0.7) + A multiplier(454) 缺席; B pduty(0.4/0.6) + B multiplier(300) 在场 ⑪(k) 分组正确: 每 alert 的 max_row.alter == alert.alter (无跨组混合) ⑫(l) 3-seed 确定性 (PYTHONHASHSEED=1/2/3 输出 sha256 一致)

**核心齿**: ⑥abs+offset 减法(反 naive 只 max dutyout) + ⑦×multiplier_B(反硬编码 454) + ⑧pduty→offset 查表(反硬编码 A map) + ⑩anti-hardcode(反硬编码 A) + ⑪分组(反跨组混合)

**3 negs**: neg_empty(空→a size0) / neg_print_only(硬编码 A 结果→d n_alerts=5≠7 + j A 在场) / neg_core_removed(真解析但 max(dutyout) 无 offset 减法→f max_raw 错). §4.9 三假全 FAIL ✓.

**distinct**: vs Mt0PvrefAbsGroupStat(declanzh yez2i, group by pvref, voffset abs min/max, 无 offset 减法 无 multiplier) / DutyMeasMt0Report(bolint 9e4kf, 跑 finesim + .measure duty PUP/PDN 提取, 无 alter 分组 无 offset) / Mt0AggregateGen(declanzh b8fi1, 多 .mt0 文件聚合 min/max, 无 pduty-offset) / Mt0AggMinMax(declanzh ie8du, 多 .mt0 abs min/max, 无 alter 分组) — 本 case=单 .mt0 + alter# 分组 + pduty→offset 减法 + abs + per-alert max + ×multiplier, 无重复 ✓.
