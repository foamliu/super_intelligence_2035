# Deepread: as67p — TempHalfWL 模块功能分析问答

**trace**: `1793147699495_as67p` (easont@hfeg0tedaap02 = 10.129.32.82)
**host**: hfeg0tedaap02 (10.129.32.82, e0031982 身份 ssh 免密)
**shard**: D (schematic_netlist, mc=806, high D-purity: netlist + schematic + analog + waveview)
**session size**: 496 msgs, 13 real user inputs
**ledger**: claimed 2026-11-17 → case `EDA-Eval-DesignFlow-TempHalfWLModuleFuncExplainQA-001` (r791)
**asset reachability**: 原 `/rundata/ddgoa/V0/workdir/easont/simulation/ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim/cosim/netlist_AI` 跨用户 Permission denied ⇒ 按 synth_deck 模式（r768/r781/r790 pattern）从 trace read_files tool_results 18 段重建 asset A（744 行/37290B），保留真实模块/端口/实例名

---

## 用户真实意图（A 档 verbatim U#4）

> `读取/proj/ddgoa/V0/workdir/easont/simulation/ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim/cosim/netlist_AI,结合上面的fsdb分析，说明模块功能`

工程师 easont 在做 LPDDR5 DRAM 温度补偿设计时，读取 TempHalfWL 模块级 SPICE 网表（ALPS 仿真 cosim 输出），要求结合上文的 fsdb 波形分析说明该模块的功能。**意图类型**：netlist-grounded module-function explain Q&A（D 域第 5 子型，承 r768/r790 模式）。

## 金标准（assistant msg#96）

TempHalfWL = **LPDDR5 温度阈值译码器**（digital threshold decoder + interval window detector）：

1. **输入**：8-bit `Temp<0>..Temp<7>` 总线（温度码，来自温度传感器 ADC）。
2. **输入缓冲**：8 个 `XI187<0>..XI187<7>` invLx4 反相缓冲阵列 → `TempN<0>..TempN<7>`（互补码）。
3. **主使能** `selN26`：`Temp<5>,<4>,<7>` 经 nand2Lx1 树（XI_selN26_1..4）合成 `n_selN26` → invLx1 → `selN26`，active when T ≥ 10°C（Vcd ≥ 176）。
4. **逐位比较器阵列**：240 个 `XIcmp_1001..XIcmp_1240`，每 14-bit 阈值判决用 ~17 个比较器（nand2Lx1/nor2Lx1 链做 binary magnitude compare），生成 `_ge/_gen` 中间信号 → AND 主使能 `selN26` → 反相 → `bufLx4` → `gfilt` 抗毛刺滤波 → 14 个阈值判决信号 `sel28, sel32, sel35, sel40, sel43, sel47, sel50, sel54, sel58, sel61, sel68, sel76, sel85, sel90`（每个对应一个温度阈值 T ≥ 28/32/.../90°C）。
5. **区间检测**：12 个区间信号 `sel28to32, sel32to35, ..., sel76to85` 由 `xnor2Lx1(相邻阈值i, 阈值j)` + `invLx4` 产生，标识温度落在哪个区间。
6. **模块功能总结**：把 8-bit 温度码译码成 14 个温度阈值标志 + 12 个温度区间窗口，供下游 ZQ 校准 / Vref / WL 时序补偿使用。

## 资产重建（asset A）

- `netlist_A.sp`（744 行/37290B）：从 trace read_files 18 段 chunk 拼接，保留真实 SPICE 结构：
  - 27 个 `.SUBCKT`（switch_close/open, inv, bufLx4, invLx4, nand2Lx1, nor2Lx1, xnor2Lx1, nand4Lx2, aoi21Lx1, gfilt, ...）
  - 顶层 `TempHalfWL`（`* Cell : TempHalfWL` 注释 + `**TopDesStart`）
  - 8 个 `XI187<0>..7>` invLx4 缓冲阵列
  - `XI_selN26_1..4` nand2Lx1 主使能树
  - 240 个 `XIcmp_1001..1240` 比较器
  - 14 个 `XVfilt_selXX`/`selXX_raw` 阈值经 `gfilt` 滤波
  - 12 个 `xnor_selXXtoYY` + `invLx4` 区间信号
- `question_A.txt`：U#4 逐字（含 `/proj/ddgoa/...` 路径原文）

## Hidden B（结构变体，零标识符重叠）

`netlist_B.sp`（37636B）：identifier-renamed structural variant，保留同结构（8-bit 总线 / 8 缓冲 / 240 比较器 / 14 阈值 / 12 区间 / glitch filter / xnor gate）但标识符全改：

| A | B |
|---|---|
| `TempHalfWL` | `VoltTierDec` |
| `Temp<N>` / `TempN<N>` | `Vcd<N>` / `VcdN<N>` |
| `XI187<0..7>` | `XV298<0..7>` |
| `selN26` / `n_selN26` | `enV164` / `n_enV164` |
| `XIcmp_1001..` | `XVcmp_1001..` |
| `sel28..sel90`（14 阈值） | `vth128..vth190`（+100 平移） |
| `selN28..selN90`（反相阈值） | `vthn128..vthn190` |
| `gfilt` | `vfilt` |
| `net_28..` / `cmp28_ge..` | `vnet_128..` / `vmp128_ge..` |
| `sel28to32..sel76to85`（12 区间） | `vth128to132..vth176to185` |

**验证**：zero A-only substring leak in B；14 thresholds + 12 intervals + 240 comparators preserved；bus width 8 preserved。

## candidate.py（reference analyzer）

通用 SPICE netlist parser（无硬编码标识符），CLI: `python3 candidate.py <deck_dir>`：
- 找 `**TopDesStart` 前的 `* Cell : <name>` → top_cell_name
- 找 `X<prefix><0> <bus><0> <busN><0> ... invLx4` → buffer prefix + bus name
- 找 `* <name>: master enable` 注释 → master_enable_signal
- 找 `X<...>filt<...> ... <subckt>` → glitch_filter_subckt
- 阈值信号 = glitch filter 实例第 3 列（排除区间/`_raw`）
- 比较器前缀 = `X\w*cmp_\d` regex
- 区间信号 = `\b([a-zA-Z]+\d+to\d+)\b`（排除 `xnor_` 前缀）
- 输出 16 顶层键 JSON

**通用性**：同一脚本在 A 上产 `TempHalfWL/Temp/XI187/selN26/XIcmp_/gfilt/sel28..sel90/sel28to32..`，在 B 上产 `VoltTierDec/Vcd/XV298/enV164/XVcmp_/vfilt/vth128..vth190/vth128to132..`——证明非 canned。

## check.py（12 断言 a-l）

| label | assertion | negative that triggers it |
|---|---|---|
| a | zip 含 candidate.py | empty_zip |
| b | candidate.py py_compile | — |
| c | exit 0 + 合法 JSON + 16 必需键 | — |
| d | top_cell_name == `VoltTierDec` | fake_core_deleted |
| e | num_thresholds == 14 | fake_print_only |
| f | num_intervals == 12 | — |
| g | input_bus_width == 8 | — |
| h | ≥1 B-only grounding token | — |
| i | comparator == `XVcmp_` 且 buffer == `XV298` | — |
| j | glitch_filter == `vfilt` 且 gate == `xnor` | fake_naive |
| k | no A-only forbidden token leak | fake_hardcode_a |
| l | 3-run md5 一致 | — |

## 自验

- REF 12/12 PASS（reference_submit.zip on hidden B）
- 4 negatives FAIL distinct labels: fake_print_only→e / fake_core_deleted→d / fake_hardcode_a→k / fake_naive→j
- §4.9 三退化全 FAIL: empty_zip→a / print_only→e / core_deleted→d
- 3-run md5 一致（B: `ae64353191c0609e87ea4edbdb5d3ef2`，A: `bb0edf0038a6d0f26bbb755e69540e52`）
- embedded E2E roundtrip PASS（jsonl test 字段抽 check.py 跑 ref.zip）
- byte-sync test==disk（9661B）
- anti-hardcode: B 输出零 A-only token 泄漏；fake_hardcode_a 触发 (k)
- k_rationale == k_check == 12 ≥ 8 GATE PASS

## 账目

- D.jsonl 452→453
- ledger mark `as67p → case` (EDA-Eval-DesignFlow-TempHalfWLModuleFuncExplainQA-001)
- 📊 覆盖率 case 438→439/2907 mc≥10=15.1%
- discuss r791 mandatory due（r790 设下次 mandatory r791）— 本轮清付
