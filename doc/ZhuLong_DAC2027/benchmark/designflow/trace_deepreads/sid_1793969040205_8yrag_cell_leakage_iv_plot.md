# Deepread: sid_1793969040205_8yrag — Cell Transistor Leakage I-V Chart from HSPICE .sw

- **session**: `1793969040205_8yrag` (mingyu1l @ hfeg0pkn002 / 10.129.2.11)
- **size**: 328,828 B / 46 msgs (25 user / 21 assistant)
- **mtime**: 2026-11-06 20:30 (fresh, found via 21:0x rescan cutoff 19:00)
- **domain**: characterization (DRAM cell transistor leakage I-V)
- **shard**: B
- **ledger**: claimed (mc=0, characterization)
- **case_id (planned)**: `EDA-Eval-DesignFlow-CellLeakageIvPlot-001`

## USER#0 verbatim (A-档 任务说明, 纯需求轮 ✓ — 给目标+方法, 未给根因/修复)

> /proj/drdxq/V0/workdir/mingyu1l/simulation/mingyu_study_tb_with_CWL_schematic_ALPS/cell_leakage/out_bounce 请你帮我把这个路径下面的 [cell_leakage_261106_2029.sw0 ~ .sw5 六个文件] 制作成图片 Professional semiconductor device characterization chart, scientific publication style: a 2x2 grid of subplots showing DRAM cell transistor leakage I-V curves, one subplot per device (NTK WL middle / top / bottom / BL Select). X-axis: gate voltage from -1V to +3V, linear scale. Y-axis: absolute drain current, logarithmic scale from 1e-16 to 1e-5 A. Each subplot contains 5 curves for process corners (TT/25°C black solid, SS/-40°C blue solid, SS/110°C blue dashed, FF/-40°C red solid, FF/110°C red dashed) with legend. Curve shape: near-flat GIDL region around 1e-15 A for negative gate voltage, a valley minimum near 0V, then exponential rise over ~8 decades up to 1e-5 A for positive gate voltage (subthreshold + turn-on). Clean white background, fine gridlines, crisp axis labels, title "Cell Transistor Leakage I-V per Device across Corners", blue-red-black professional palette.

**A-档 ② 检查**: 用户提需求(做图)+给详细图表规格(轴/颜色/曲线形状), 未给根因/未给修复方案 ✓ → 可作 A-档 任务说明。

## 真实资产 (attachments 候选)

- `/proj/.../out_bounce/cell_leakage_261106_2029.sw0` ~ `.sw5` (6 个 HSPICE ASCII 波形文件, 各 317,462 B)
- `/proj/.../out_bounce/cell_leakage_261106_2029.lis` (HSPICE log, 含 alter 顺序/温度)
- `/proj/.../out_bounce/cell_leakage_261106_2029.ms0.csv` (.meas 结果, 6 行 = 6 alter)
- `/proj/.../cell_leakage/top.sp` (网表: 4 器件 xmmn1a~xmmn4a, `.dc vwl -1 3 0.005` = 801 点)
- ⚠ 这些文件在 mingyu1l 私有 /proj/drdxq 下, e0031982 无读权限 → 合成时需自带便携 .sw 样本 (A=trace 格式复刻, B=不同器件/角)

## Assistant 工具链 (msg#1–#45)

1. `get_agent_policy_status` + `list_allowed_files` (确认可读 /rundata/drdxq/... 映射)
2. `read_files` .lis (1-120, 120-400) + ms0.csv → 6 alter, 温度 25/25/110/-40/110/-40
3. `list_allowed_files` 父目录 → 5 corner 子目录 (tt25/ss-40/ss110/ff-40/ff110)
4. `read_files` top.sp → 确认 alter↔corner↔sw 映射:
   | run | file | corner | | base | sw0 | TT/25 | | alter1 | sw1 | TT/25(重复) | | alter2 | sw2 | FF/110 | | alter3 | sw3 | FF/-40 | | alter4 | sw4 | SS/110 | | alter5 | sw5 | SS/-40 |
   器件映射: xmmn1a=NTK WL middle, xmmn2a=NTK WL top, xmmn3a=NTK WL bottom, xmmn4a=BL Select
   扫描: `.dc vwl -1 3 0.005` (801 点)
5. `read_files` agent-policy.json → 可写 /home/mingyu1l, python-runner (Python 3.7.1, 120s)
6. `editor` probe_sw.py → `run_approved_command` → 逆向 .sw 格式:
   - **HSPICE ASCII 格式** (非二进制)
   - 头部: `0030` (=30 输出变量) → 标题/日期 → 计数段 → 30 变量名 (`vwl, i(vd1a, v(g1a, i(vd2a, ... i(xmmn4a.mn1)`) → `$&%#` 数据起始标记
   - 数据段: 每行 6 个 13 字符定宽字段 (如 `-.1000000E+01`), 每扫描点 30 值占 5 行; 801 点 × 30 值 × 79 B = 316,395 B ≈ 文件 317,462 B ✓
   - 首点验证: vwl=-1.0, i(vd1a)=0.3016464E-15 = .meas igidl_1=3.016464e-16 ✓
   - 末尾哨兵值 `0.1000000E+31` (=1e30) 需剔除
7. `editor` plot_cell_leakage_iv.py (284 行, 分 3 段写入; 坑: editor `$&` 替换符 → 用 `"$" + "&%#"` 拼接规避)
8. `run_approved_command` ×3 (前 2 次失败: ① 标题含 `(` 误匹配变量名 → 改读头 4 字符 `0030`=nvars 取末尾 30 token; ② 数据多 1 值 = 末尾 1e30 哨兵 → 剔除)
9. **最终成功** (msg#45): `[ok] sw0~sw5: 801 pts, Vg -1..+3 V, i(vd1..4) match .meas (ileak_ch & igidl) within 0.1%` + 生成 2x2 PNG

## 金标准 (trace 末尾工具真实产物)

trace 末尾(msg#45)= tool result 脚本成功, 无显式用户"谢谢"接受语, 但**工具成功执行 = 用户得到所要图表** → 金标准 = 成功产物:
- 解析 6 个 .sw → 每 corner 4 器件 801 点 I-V (vwl, |i(vdXa)|)
- 与 .meas (igidl/ileak_ch) 交叉验证误差 <0.1%
- 2x2 PNG: 4 子图(每器件), 5 corner 曲线(TT/25 black, SS/-40 blue, SS/110 blue dashed, FF/-40 red, FF/110 red dashed), X=Vg -1..3 linear, Y=|Id| 1e-16..1e-5 log

## .sw ASCII 格式规格 (合成必备)

```
[4-char flag: "0030" = nvars=30]
[title line(s)]
[count segment]
[30 variable names, whitespace/newline separated, e.g.: vwl, i(vd1a, v(g1a, i(vd2a, v(g2a, i(vd3a, v(g3a, i(vd4a, v(g4a, i(xmmn1a.mn1, i(xmmn2a.mn1, i(xmmn3a.mn1, i(xmmn4a.mn1, ... )]
$&%#                            <- data start marker
[data: 13-char fixed-width fields, 6 per line, e.g. "-.1000000E+01"]
[801 points × 30 values = 24030 values]
[trailing sentinel: 0.1000000E+31 (=1e30) — strip]
```

## 合成规划 (CellLeakageIvPlot-001, characterization A-faithful L2)

- **交付**: 通用 `parse_sw_iv.py <sw_file> <out_dir>` 解析 HSPICE ASCII .sw → 提取 I-V (vwl + 4 器件 i(vdXa)/|Id|) → 写 `iv_data.json` (per corner: {device: {vg[], id_abs[]}}) + 生成 2x2 PNG chart → 打包 `outputs/submit.zip`
- **A/B 切分**: 
  - A = 便携 HSPICE deck (4 NMOS level-1, .dc vwl -1 3 0.005, 801 点) 跑 5 corner (.alter temp/model) → 生成 .sw0~.sw4 (TT/25, SS/-40, SS/110, FF/-40, FF/110); 器件名 xmmn1a~xmmn4a
  - hidden B = 不同便携 deck (4 NMOS 不同 W/L, .dc vwl -0.5 2.5 0.01 = 301 点, 5 corner 不同温度) → .sw0~.sw4; 器件名 xq1~xq4 (强制泛化解析, 非硬编 xmmn*)
- **reference**: `parse_sw_iv_ref.py` + `check.py` **k≥8 断言** (zip+py_compile/--help/A 解析 .sw 提取 801 点/A iv_data.json 4 器件 5 corner 齐全/A |Id| 与 HSPICE .meas 一致±1%/A PNG 存在+尺寸合理/B 解析 .sw 提取 301 点/B iv_data.json 4 器件 5 corner 齐全/B |Id| 与 HSPICE .meas 一致±1%/L2 HSPICE 真跑 B deck 生成 .sw job concluded/跨输入 B 器件名 xq* ≠ A xmmn* 且点数 301≠801) + negative/ (5 stub) + negative_selftest.py
- **L2**: check.py 在 .75 真跑 HSPICE 生成 B 的 .sw (DC sweep), 候选脚本解析 B .sw, 验证提取值 (参 LisMeasExtract-001 模式)
- **跨输入护栏**: A 器件 xmmn1a~/801 点 ≠ B 器件 xq1~/301 点; 硬编 A 器件名/点数在 B 失败
- **校准**: 需 .75 HSPICE 真跑 A/B deck 确认 .sw 格式 + .meas 值 (下轮合成时做)

## DEBT

本轮 fresh rescan (11-05 令, 42 host/cutoff 19:00/15 results/10 NEW/scout) + claim + deepread 消耗预算 → 合成留 **DEBT:1 下轮第一件事**。
