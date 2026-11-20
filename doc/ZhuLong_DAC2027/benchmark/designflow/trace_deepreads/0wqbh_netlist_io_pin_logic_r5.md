# Deepread: 1794470412317_0wqbh (tongni@hfeg0plg65)

- **Session**: 1794470412317_0wqbh
- **User**: tongni
- **Host**: hfeg0plg65 (10.129.8.103)
- **Messages**: 434
- **Match count**: 218
- **Keywords**: netlist:653; analog:485; schematic:138; hspice:63; opamp:32; mosfet:26; rtl:8; aether:4
- **D-purity**: 0.99 (pure schematic_netlist/analog_context)
- **Selected for**: r769, case `EDA-Eval-DesignFlow-NetlistIOPinLogicCheck-001`

## Real Task

用户 tongni 要求分析 HSPICE 网表 `zmh_AI_VtscRef_standard_tb_sim_schematic.netlist` 的输入输出 Pin。网表 1504 行，顶层 subckt `VtscRef_standard_tb` 含 23 端口。助手用 `run_approved_command` + `editor` 执行 Python 分析脚本，沿标准单元引脚惯例（信号在前，Y 在最后，之后 inh_v* 电源）逐级追溯 `AG_VtscRefLogic` 内 `invLx4`/`invLx8`/`bufLx8`/`nand2Lx1`/`nand3Lx1` 链。

## Key Findings

### Pin Classification
- **OUTPUT (logic)**: `Vtsc2Vcc` (invLx8 XI53 驱动), `VtscAmpDis` (bufLx8 XI4 驱动)
- **OUTPUT (analog)**: `VtscRef` (挂 Cgatein 电容负载, pass gate 驱动)
- **FEEDBACK**: `Fbin` (net9), `Fbout` (net1) — 顶层 `v0 net1 net9` 短接
- **INPUT (testmode)**: `cm0_ag_ShftVtsc<2:0>` (shift 码), `cm1_ag_AdjVtsc<4:0>` (trim 码), `cm1_ag_RegLbias` (偏置修调)
- **POWER**: `PwrOn2`, `PwrOn3`, `PwrOnLsVdd1`
- **REFERENCE**: `GlbRef08` (0.8V), `GlbRef10` (1.0V)
- **SUPPLY**: `inh_vcc`, `inh_vdd1`, `inh_vss`, `inh_vwlp`

### Boolean Logic (R5 Functional Derivation)
```
shft<k>  = cm0_ag_ShftVtsc<k> & PwrOn3       (nand2Lx1 → invLx4)
shftF<0> = !shft<0>                            (invLx4)
net3     = !(shft<2> & shft<1> & shft<0>)     (nand3Lx1)
net9     = !(shft<2> & shft<1> & shftF<0>)    (nand3Lx1)
net6     = !net9 = shft<2> & shft<1> & !shft<0> (invLx4)
Vtsc2Vcc = net6                                (invLx4 → invLx8 双反)
VtscAmpDis = !(net3 & !net6) = (shift==111)|(shift==110) (nand2Lx1 → inv → inv → buf)
```

### Truth Table (PwrOn3=1)
| shift | Vtsc2Vcc | VtscAmpDis |
|-------|----------|------------|
| 000-101 | 0 | 0 |
| 110 | 1 | 1 |
| 111 | 0 | 1 |

### User Turn Selection (A档)
- **Prompt = verbatim U#1**: "分析一下这个网表的输入输出 Pin" (提出需求型，非给根因/fix 型)
- A档 trace-faithful：prompt 直接取用户首个需求表达 turn

## Case Design

- **A (visible)**: `VtscRef_standard_tb.netlist` — reconstructed from trace (same port names, same logic chain, inv_bit=0 → trigger=110)
- **B (hidden)**: `Vref_adj_standard_tb` — different names, inv_bit=1 → trigger=101
- **B2 (anti-hardcode)**: `VccSel_standard_tb` — inv_bit=2 → trigger=011
- **SUT**: `netlist_io_analyzer.py` — parse netlist, classify pins, derive boolean logic, output JSON
- **check.py**: 20 assertions on B + B2 anti-hardcode + 3-seed determinism

## Session Evolution
1. U#1: 分析网表 I/O Pin → 助手分类 23 端口（沿驱动来源，非凭网名）
2. U#2: 能根据输入输出检查功能吗 → 助手推导 Vtsc2Vcc/VtscAmpDis 布尔等式
3. U#3: 推导结论作为 Skill R5 check → 助手产出 R5 报告（等式+真值表）
4. U#5: cm1_ag_RegLbias 修调偏置电流 → 助手修正报告措辞
5. U#6: 识别运放 → 助手识别 AG_VnocVdleqVtscRefAmpCore (213 管)
6. U#7: 固化 R5 格式到 sim-sp-gen Skill → 助手编写 r5_functional_report.py
7. U#14: 第二个网表上验证 R5 通用性 → 助手在 tongni_DSCQA_2nd 上跑 R5
8. U#17: always on 默认 pvss，不能只凭功能字面推断 → 助手修正实际功能检查
