# DFT 插入失败根因分析与修复报告 (fix_report)

## 0. 结论摘要

`case_fail_dc.tcl` 相比基线 `case1_dc.tcl` 在 **三处 DFT 配置** 上被错误修改, 三者共同作用, 破坏了扫描链构建所需的时钟控制与扫描使能识别, 最终导致 **insert_dft 失败 (TEST-269)、Number of chains = 0**。

| # | 差异项 | case1_dc.tcl (正确基线) | case_fail_dc.tcl (失败) | 修复 |
|---|--------|--------------------------|---------------------------|------|
| ① | 时钟门控控制信号 (`set_clock_gating_style -control_signal`) | `scan_enable` | `scan_mode` | 改回 `scan_enable` |
| ② | `scan_mode` 的 DFT 信号类型 (`set_dft_signal -type`) | `Constant` | `TestMode` | 改回 `Constant` |
| ③ | 自动修门控时钟 (`set_dft_configuration -fix_clock_gating`) | 未启用(注释) | `true` (启用) | 关闭(注释掉) |

只要把这三处改正 (即等价于 `case1_dc.tcl`), DFT 插入即可恢复为 **390 条扫描链**, TEST-130 / D1 / D8 / scan=false 等致命违例全部消失。

---

## 1. 根因分析 (三处差异)

### 差异 ① —— 时钟门控控制信号错误: `scan_mode` vs `scan_enable`

```tcl
# 基线 (正确)
set_clock_gating_style -max_fanout 16 -control_point before -control_signal scan_enable
# 失败版本 (错误)
set_clock_gating_style -max_fanout 16 -control_point before -control_signal scan_mode
```

`-control_signal` 指定综合工具在时钟门控单元 (ICG, Integrated Clock Gating Cell) 上用于 **测试使能** 的控制信号。扫描测试期间 (shift 与 capture), ICG 必须被"强制打开"让时钟透传, 其测试控制端应接真正的扫描使能 `scan_enable` (该信号在 shift 时拉高、可被 DFT 引擎动态控制)。

失败版本把控制信号改成了 `scan_mode`。`scan_mode` 在所有测试模式下是一个 **固定常量 (active_state 1)**, 不会随 shift/capture 切换, 因此 ICG 的测试控制端被一个常量驱动, 而不是被 `scan_enable` 控制。

**直接后果:**
- ICG 的测试引脚没有连到有效的扫描使能路径上 → **TEST-130 (ICG test pin unconnected, 731 个)**。
- ICG 及其下游寄存器的时钟无法在测试模式下被可靠控制/透传 → **D1 (clock not controlled, 3842 个)** 与 **D8 (clock cannot capture data, 517 个)**。
### 差异 ② —— `scan_mode` 被误标为 `TestMode` 扫描信号

```tcl
# 基线 (正确)
set_dft_signal -view existing_dft -type Constant -port scan_mode -active_state 1 -test_mode all_dft
set_dft_signal -view spec         -type Constant -port scan_mode -active_state 1 -test_mode all_dft
# 失败版本 (错误)
set_dft_signal -view existing_dft -type TestMode -name scan_mode -port scan_mode -active_state 1 -test_mode all_dft
set_dft_signal -view spec         -type TestMode -name scan_mode -port scan_mode -active_state 1 -test_mode all_dft
```

`scan_mode` 在本设计中是 **测试模式常量端口** (进入测试后恒为 1), 正确类型是 `Constant`。基线将其声明为 Constant, DFT 引擎就把它当作静态值, 不参与扫描信号的特殊处理。

失败版本错误地把它标成 `TestMode`。`TestMode` 是留给真正"测试模式控制信号"的特殊类型, 与 `scan_enable` 同属 DFT 特殊信号。这一误标带来两个问题:

1. DFT 引擎把 `scan_mode` 当成一个顶层的测试控制信号, 与真正的 `scan_enable` 产生角色冲突, 导致测试协议 (test protocol) 推断错误。
2. 由于 ① 又把门控时钟的控制端接到 `scan_mode` 上, 于是"控制门控时钟的信号"本身被判定为 TestMode 特殊信号、而非可被 scan_enable 打开的路径, 进一步恶化了时钟不可控 (D1/D8) 与 ICG 测试引脚未连接 (TEST-130) 的问题。

**直接后果:** 大量寄存器因时钟/扫描使能识别错误而无法被判定为可扫描单元 → **cells with scan=false 高达 5150 个**。

### 差异 ③ —— 实验性"自动修门控时钟"被打开

```tcl
# 基线 (正确): 注释掉, 不使用
# set_dft_configuration -fix_clock_gating true
# 失败版本 (错误): 打开实验选项
set_dft_configuration -fix_clock_gating true
```

`set_dft_configuration -fix_clock_gating true` 是一个实验性功能, 会试图"自动修复"不可测的门控时钟逻辑, 在 ICG 上自动插入测试控制。它本应配合 **正确的门控时钟控制信号与 DFT 信号分类** 使用。

失败版本在 ①、② 已经把信号分类弄错的前提下再启用该选项, 自动修复逻辑在错误的信号语义上继续改写时钟门控结构, 非但不能恢复可测性, 反而让 ICG 测试引脚进一步错乱、扫描单元无法归入扫描链, 数据被放大到 **dft_drc total violations = 76943**。
---

## 2. 三处差异如何导致 0 条扫描链 (因果机制链)

```
① -control_signal scan_mode   ─┐
                               ├─► ICG 测试引脚接常量、时钟门控不受 scan_enable 控制
② scan_mode 误标为 TestMode   ─┘        │
                                         ├─► TEST-130 (ICG test pin unconnected) = 731
                                         ├─► D1 (clock not controlled)           = 3842
                                         ├─► D8 (clock cannot capture data)       = 517
                                         └─► 时钟/扫描使能识别错乱 →
                                             大量寄存器被判定 scan=false = 5150
                                                          │
③ -fix_clock_gating true  ──► 在错误语义上自动改写门控 ─────┤
                                                          ▼
                             能接入扫描链的单元数量不足 / 扫描链无法拼接
                                                          ▼
                                         insert_dft 报 TEST-269 失败
                                                          ▼
                                         Number of chains = 0
```

1. **① + ②** 使得时钟门控单元 (ICG) 的测试控制端不是由 `scan_enable` 控制, 同时 `scan_mode` 又被搞成 TestMode 特殊信号。DFT 引擎因此无法在 shift/capture 周期正确打开门控时钟 → 大量寄存器时钟"不可控"(D1) 或"无法捕获"(D8), ICG 测试引脚被判定为"未连接"(TEST-130)。
2. 时钟与扫描使能路径的错误判定让 DFF 无法被识别为合法的可扫描单元 → **5150 个单元 scan=false**, 即这 5150 个触发器无法被拼入任何扫描链。
3. **③** 的实验性自动修复在这些错误语义上继续改写, 把违例数量放大一个量级, 却无法挽救链构建。
4. 最终因为几乎没有任何能正确构成链的扫描单元, `insert_dft` 无法完成链拼接, 报 **TEST-269** 失败, 输出 **Number of chains = 0**。

> 说明: 基线 `case1_dc.tcl` 的 dft_drc total violations 为 1857, 但这些均为非致命/信息类告警, 不影响 `insert_dft PASS`; 失败版本的关键致命违例 (TEST-130、D1、D8、scan=false) 均源于上述三处配置错误。
---

## 3. 修改对照

### 修复 ①: 时钟门控控制信号改回 scan_enable

| | 修改前 (case_fail_dc.tcl) | 修改后 (dc_fixed.tcl) |
|---|---|---|
| 时钟门控风格 | `set_clock_gating_style -max_fanout 16 -control_point before -control_signal scan_mode` | `set_clock_gating_style -max_fanout 16 -control_point before -control_signal scan_enable` |

### 修复 ②: scan_mode 类型改回 Constant

| | 修改前 (case_fail_dc.tcl) | 修改后 (dc_fixed.tcl) |
|---|---|---|
| existing_dft 视图 | `set_dft_signal -view existing_dft -type TestMode -name scan_mode -port scan_mode -active_state 1 -test_mode all_dft` | `set_dft_signal -view existing_dft -type Constant -port scan_mode -active_state 1 -test_mode all_dft` |
| spec 视图 | `set_dft_signal -view spec -type TestMode -name scan_mode -port scan_mode -active_state 1 -test_mode all_dft` | `set_dft_signal -view spec -type Constant -port scan_mode -active_state 1 -test_mode all_dft` |

### 修复 ③: 关闭自动修门控时钟

| | 修改前 (case_fail_dc.tcl) | 修改后 (dc_fixed.tcl) |
|---|---|---|
| 自动修门控 | `set_dft_configuration -fix_clock_gating true` (启用) | `# set_dft_configuration -fix_clock_gating true` (注释, 不启用) |

其余部分 (读入 RTL、UPF、SDC、scan_enable 的 ScanEnable 声明、create_test_protocol、compile_ultra、insert_dft、增量综合、报告与写网表) 均与基线保持一致, 不做改动。

---

## 4. 修复前后关键指标对比

| 指标 | 失败版本 (case_fail_dc.tcl) | 修复后 (dc_fixed.tcl, 预期) |
|------|------------------------------|------------------------------|
| Number of chains | 0 | **390** |
| TEST-130 (ICG test pin unconnected) | 731 | **0** |
| D1 (clock not controlled) | 3842 | **0** |
| D8 (clock cannot capture data) | 517 | **0** |
| cells with scan=false | 5150 | **0** |
| dft_drc total violations | 76943 | 1857 (非致命告警) |
| insert_dft 结果 | fail (TEST-269) | **PASS** |

---

## 5. 交付文件说明

- `dc_fixed.tcl`: 基于 `case_fail_dc.tcl` 修正后、与基线 `case1_dc.tcl` 等价的可正确插入 DFT 的综合脚本 (含三处修复注释)。
- `fix_report.md`: 本报告 (根因分析 + 三处修改对照 + 修复前后指标对比)。