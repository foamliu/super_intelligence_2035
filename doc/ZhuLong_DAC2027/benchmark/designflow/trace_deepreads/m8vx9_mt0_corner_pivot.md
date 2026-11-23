# m8vx9 — FineSim 多 corner .mt0 measure 列透视聚合器

- **trace**: t0002805 @ hfeg0pkn005, sid=1794885567290_m8vx9, mc=220, domain=spice_sim (B shard)
- **来源**: fresh_Bspice_r1050.tsv, cross-4-shard-ledger 全 NONE ✓ (r1079 选料)
- **scan**: ssh_eda_search_20261123_064315
- **文件**: 237 msgs / 1.06MB, scp 自 hfeg0pkn005:/home/t0002805/.cline/data/sessions/1794885567290_m8vx9/

## 用户真实意图（多段，单一主题：FineSim .measure 电流测量 + mt0 数据处理）

t0002805 在 ddgoa 项目做 BIST 振荡器 (BistOscNew) 的 FineSim 仿真，围绕两个反相器链 ROsc 电路：
1. `PM_invGFx1_f1_sub_Test`（单电源 vdd2h=0.94V，只地门控）
2. `Rosc_GP`（vcc=1.05V，电源+地双门控，含 vccz/vssz 虚拟节点）

用户想测 31/32 个反相器各自的平均电流，写 `.meas tran ... avg i(...)`，全报 `can't find device`。

## 关键根因（assistant 诊断，msg 122-165）

- `i(vdd2h)`（顶层电压源）✓ 成功 → mt0 给出 `-1.2751e-09`
- `i(XI_PM_invx1_2<0>.inh_vcc)` ✗ → 数组(bus)实例 + 子电路端子，FineSim `.measure` 不支持
- `i(XI_PM_invx1_2<0>.XIinv_0.XMMN0)` ✗ → 数组实例下标穿透叶子 MOS，依然 `can't find device`（即使 log 电容警告里该器件真实存在）
- 结论：**数组实例 `<N>` 在 `.measure` 的 `i()` 里不能穿透**；只能测顶层源 `i(vdd2h)` 拿总电流，或拆数组改单实例。

## 本轮 reframe 选料段（msg 188-213）：mt0 多 corner 透视聚合

用户后续切到 BistOscNew 振荡器周期测量，目录：
`/proj/ddgoa/V0/workdir/t0002805/simulation/ddgoa_cmos_digital_BistOscNew_schematic_ALPS/sim_2026_11_20_5ns_test/`

含 10 个 corner 的 `.mt0` 文件（FineSim `$DATA1` 格式）。用户原话：
> "这个路径下的所有mt0 里面的period1t 下的数据都要列出来 然后第一行是数据分类 分类名称就是 这些.mt0的名称"

### mt0 真实格式（从 trace tool_result 提取，msg 196/202/206）
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=9
.TITLE '.option PARHIER = LOCAL'
      index    trim23 trim22 trim21 trim20 trim13 trim12 trim11 trim10  period1t  period2t  period4t  temper  alter#
   1.0000e+00  0...0   ...     0       0       0       0       0       0    5.9080e-09 1.1817e-08  error  2.5000e+01 1.0000e+00
   2.0000e+00  1...1   ...     1       1       1       1       1       1    2.8695e-09 5.7424e-09  error  2.5000e+01 1.0000e+00
```
- 第 1 行 `$DATA1 ... PARAM_COUNT=N`
- 第 2 行 `.TITLE '...'`
- 第 3 行 列名（whitespace 分隔）
- 第 4+ 行 数据（科学计数，`error` 表示该 measure 失败）
- 每个 corner 2 个 trim 扫描点（index 1 全 trim=0，index 2 全 trim=1）

### 10 corner 真实 period1t / period2t（msg 206）
| corner | idx1 p1 | idx1 p2 | idx2 p1 | idx2 p2 | temper |
|---|---|---|---|---|---|
| FF0p105V25C | 5.908e-09 | 1.1817e-08 | 2.8695e-09 | 5.7424e-09 | 25 |
| FF0p105V30C | 6.6593e-09 | 1.3324e-08 | 3.2023e-09 | 6.4107e-09 | 30 |
| FF0p105V45C | 6.6226e-09 | 1.324e-08 | 3.1876e-09 | 6.3832e-09 | 45 |
| FF0p105V85C | 6.4992e-09 | 1.2988e-08 | 3.1329e-09 | 6.2633e-09 | 85 |
| SS0p92V130C | 6.542e-09 | 1.3093e-08 | 3.6414e-09 | 7.2734e-09 | 130 |
| SS0p92VN40Ctest | 6.8783e-09 | 1.3762e-08 | 4.1278e-09 | 8.2489e-09 | -40 |
| TT0p105V25C | 6.7537e-09 | 1.3511e-08 | 3.3116e-09 | 6.635e-09 | 25 |
| TT0p105V30C | 6.7486e-09 | 1.35e-08 | 3.3179e-09 | 6.6389e-09 | 30 |
| TT0p105V45C | 6.7232e-09 | 1.3426e-08 | 3.3094e-09 | 6.6279e-09 | 45 |
| TT0p105V85C | 7.1776e-09 | 1.4325e-08 | 3.2966e-09 | 6.5721e-09 | 85 |

period4t 全 error。

### assistant 交付（msg 213）
生成 `BistOsc_period1t.xlsx`，sheet1「period1t」宽表：第一行 = 10 个 .mt0 文件名（corner 分类），下两行 = index 1/2 的 period1t 值；sheet2 长表含 period2t。用 openpyxl。

## reframe（独立可程序化，L1 纯 Python 无 EDA 依赖）

`mt0_corner_pivot.py <spec.json> <out.json>`:
- spec.json: `{ "dir": "<mt0 目录>", "target": "<measure 列名，如 period1t>" }`
- 解析目录下所有 `*.mt0`（FineSim `$DATA1` 格式：line1 header 含 PARAM_COUNT，line2 .TITLE，line3 列名 whitespace 分隔，line4+ 数据行，`error` 表失败）
- 提取每个 corner 的 `target` 列（按 index 行）
- 输出 JSON:
  - `target`: 目标列名
  - `corners`: 排序后的 corner 文件名列表
  - `indices`: 所有出现过的 index 排序
  - `param_count`: 从 line1 解析
  - `header`: 列名顺序
  - `wide`: `{corner: {index: value_or_None}}`（error→None）
  - `long`: `[{corner, index, value, is_error}]`
  - `error_cells`: `[{corner, index}]`
  - `summary`: `{corner: {n_valid, n_error, min, max, mean}}`（仅 numeric）
  - `temper`: `{corner: temper}`

**核心齿**:
1. FineSim `$DATA1` 格式解析（PARAM_COUNT、列名行、科学计数、`error` token）
2. 任意 target 列泛化（不硬编 period1t）
3. error → None 转换 + error_cells 统计
4. 宽表透视（corner×index）+ 长表 + 每角 summary（min/max/mean 排除 error）
5. temper 列提取

## case ID
EDA-Eval-DesignFlow-Mt0CornerPivotAggregate-001

## A（真实，可见）
10 个真实 corner .mt0（period1t/period2t，2 trim 行，period4t error），spec_A target=period1t。

## hidden B（五重 anti-hardcode）
①不同设计（DFE 时钟振荡器）②target=freq_mhz（异 A period1t）③8 corner 异 A 10 ④4 trim 扫描点 异 A 2 ⑤freq 值量级不同 + error 分布在不同 corner/index（非全 error 非全有效）；corner 名/temper/PARAM_COUNT 全异 A。
