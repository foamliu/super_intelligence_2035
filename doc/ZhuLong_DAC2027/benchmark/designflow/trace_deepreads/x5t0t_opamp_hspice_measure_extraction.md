# x5t0t — 两级 Miller 补偿运放 HSPICE AC `.measure` 提取深读笔记

- **trace**: `1792205753795_x5t0t.messages.json`，user `brian`，host `hfeg0plg95`，match_count 497
- **cwd**: `/home/brian/spice/opamp_design`（spice/opamp 仿真目录）
- **规模**: 313 msgs（160 user / 153 assistant），tool_use：editor 54 + run_approved_command 53 + read_files 36 + 其余
- **关键字**: opamp:756 / hspice:461 / netlist:281 / synopsys:100
- **领域判定**: characterization（HSPICE AC 仿真 + `.measure ac` 指标提取 + spec 合规判定；与 9knot/ws2bi 同 family，本 trace 多了完整两级 Miller 运放 netlist + 7 条 `.measure` 的具体口径）

## 用户首条（也是唯一 substantive）prompt

> `make a simple OP AMP. gain over 1000, phase margin over 60 degree, gain bandwidth 1M`

此后 313 msgs 基本都是 agent 自驱迭代（编辑 netlist → 跑 hspice → 读 .ma0/.lis → 改 sizing → 再跑），用户只在末段给 1-2 条确认/纠偏。

## flow 主线（agent 自驱 sizing 迭代）

```
editor: opamp_testbench.sp  ──┐
run_approved_command: hspice64 -i opamp_testbench.sp -o sim  ──┐
read_files: sim.ma0 / sim.lis  ──┐  解析 $DATA1 / .measure 结果
  ↓ (dc_gain/ugf/phase_ugf/pm/gm_freq/gm_db/bw3db 7 字段)
  ↓ 迭代 sizing (W1/W6/Cc/Rz) → 再 editor → 再 hspice → ...
终版: dc_gain 实测仅 3.83 dB（设计未收敛，agent 自述 "31 dB gain, take a different approach"）
```

trace 中 agent 始终**手动**编辑 netlist + 手动跑 hspice + 手动读 `.ma0`，没把"跑仿真+解析 measure+给合规判定"沉淀成可复用工具——这正是本 case 抽取的子流。

## HSPICE 调用方式（本 case 抽取的可复用子流）

trace 用 `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice64 -i <netlist> -o <prefix>` 跑 AC：

- 输入 netlist 含 `.subckt OPAMP ...`（NMOS 输入两级 Miller 补偿 + nulling 电阻 Rz）+ `.ac dec 200 1 100meg` + 7 条 `.measure ac`
- 7 条 `.measure ac`：`dc_gain`、`ugf`、`phase_ugf`、`pm`、`gm_freq`、`gm_db`、`bw3db`
- 输出：`<prefix>.ma0`（$DATA1 表，含 7 measure 值 + temper + alter#）+ `<prefix>.lis`（人类可读 log）
- **`.ma0` $DATA1 解析规则**（实测）：
  - drop `$DATA1` 行 + `.TITLE` 行 + header token 行（`dc_gain/ugf/phase_ugf/pm/gm_freq/gm_db/bw3db/temper/alter#/$data1`）
  - 剩余 token 固定顺序 = 7 measure 值 + temper + alter#
  - `failed`（case-insensitive）→ null（HSPICE 在 measure 找不到目标点时返回字面量 `failed`，不是数字）
- NTK/PTK 是 subckt，实例化必须用 `X` 前缀（NOT `M`），否则 hspice 报 `unknown model`

## 工艺/模型

- **foundry**: CXMT Redwood Commodity 19nm，imc19n v1.09p3
- **model**: `/apps/imctf/models/imc19n/1.09p3/Model_v1d09p3.sp`（trace 与 .75 同路径）
- **器件**: NTK/PTK 厚氧 subckt（VDD=3.3V）
- **hspice**: `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice64`（trace 与 .75 同路径，headless 可跑）

## 终版 netlist 结构（asset A，trace sizing）

```
.subckt OPAMP IN INP OUT VDD VSS
  * 输入级（NMOS 差分对，NTK 厚氧）
  X1 IN  N1 VDD VSS  NTK  W=8u L=1u     ; M1
  X2 INP N1 VDD VSS  NTK  W=8u L=1u     ; M2 (matched)
  ...
  * 第二级 + Miller 补偿 + nulling 电阻
  X6 ... PTK  W=30u L=1u                ; 输出级
  Cc  N3 OUT  2p                         ; Miller cap
  Rz  N4 N3  10k                         ; nulling resistor
.ends
VDD VDD 0 3.3
VSS VSS 0 0
.ac dec 200 1 100meg
.measure ac dc_gain  ...
.measure ac ugf       ...
.measure ac phase_ugf ...
.measure ac pm        ...
.measure ac gm_freq   ...
.measure ac gm_db     ...
.measure ac bw3db     ...
```

## .75 hspice 沙盒实测（asset A vs 隐藏 B ground truth）

| 字段 | A = opamp_testbench.sp (trace sizing: W1=8u/W6=30u/Cc=2p/Rz=10k) | B = opamp_hidden.sp (variant sizing: W1=40u/W6=120u/Cc=4p/Rz=20k) |
|:--|:--|:--|
| dc_gain | 3.8333 dB | -21.1171 dB |
| ugf | 4.17e6 Hz | `failed` → null |
| phase_ugf | 121.0461° | `failed` → null |
| pm | 301.0461° | `failed` → null |
| gm_freq | `failed` → null | `failed` → null |
| gm_db | 28.0642 | 25.1404 |
| bw3db | 6.821e6 Hz | `failed` → null |

**关键 discriminator**：B 大量字段 `failed` → null（ugf/phase_ugf/pm/gm_freq/bw3db 全空），而 gm_db 仍为有效数 25.14。若 SUT 的提取器把 `failed` 当数字或忽略 → 与 GT 不对齐 → FAIL。这逼 SUT 必须正确实现 `failed`→null 映射。

## 本 case 抽取的 L2 子流（不要求 SUT 重新设计运放）

SUT 交付**通用** HSPICE `.measure` 提取器 `extract_opamp_metrics.py`：
1. 接收 netlist 路径 + spec 阈值
2. 在 .75 沙盒真跑 `hspice64 -i <netlist> -o <prefix>`（subprocess，必须 exit 0）
3. 解析 `<prefix>.ma0` 的 $DATA1 表 → 7 measure 字段 + temper + alter#
4. `failed`（case-insensitive）→ null
5. 输出 JSON report（schema：每个字段 {value, unit, spec, met} + 整体 verdict）
6. spec 合规判定：dc_gain>60dB、ugf≈1MHz（±20%）、pm>60°、bw3db>0、gm_db>10dB；任一字段为 null → 该字段 met=false

`check()` 在隐藏 netlist B 上跑 SUT 的提取器，并与 .75 独立重跑的 HSPICE ground truth 逐字段对齐（含 `failed`→null 的对齐），18 条件 a-q（a=zip 提取 guard，b-q=17 独立断言），test_rationale 17 条断言（a 不计入）。

## 与同 family trace 的差异

| trace | family | 抽取子流 | case |
|:--|:--|:--|:--|
| 9knot | characterization | SiliconSmart lib char debug | 9knot→LibCell-001 域? |
| ws2bi | characterization | hspice .tr/.tran duty `.measure` | ws2bi→SpiceSim-001? |
| **x5t0t** | **characterization** | **hspice .ac + 7 measure 提取 + spec 合规** | **x5t0t→OpampChar-001** |
| n91pk/wb03t | spice_sim (CTLE) | CTLE AC spec compliance | n91pk→CTLESpec-001, wb03t→CTLEAC-001 |

x5t0t 与 n91pk/wb03t 都做 AC spec compliance，但 x5t0t 是**通用 .measure 提取器**（任何 netlist 都能跑，不硬编码 CTLE 字段），而 CTLESpec/CTLEAC 是 CTLE 专用。x5t0t 填的是 characterization 域"通用 .meas 提取"空白，与 CTLE 系列正交。
