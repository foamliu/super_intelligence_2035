# 深读笔记 · qyroq · shanksw@10.129.32.75 · mc=21 · schematic_netlist

**session**: 1793877732979_qyroq | **user**: shanksw | **host**: 10.129.32.75 (hfhds201, .75 本机) | **match_count**: 21 | **keywords**: netlist:31;lvs:9;aether:8;analog:5;lib.defs:2;cmos:2;.cdl:2

## 用户原话（5 轮迭代，逐字）

- U#0: 「你好，目前从DDGOA中WOWTOP里面的CMLeft里，从CMLeft里出来的cm1的testmode,所有在WOWTOP里面，从CMLeft里面出来的信号，前三个字符是"cm1"都算是cm1的testmode, cm1 testmode个数有多少个？」
- U#1: 「在上面这些cm1的testmode中，有多少是接向vdd2h电压域的？有多少是接向vintcore电压域的？除此之外，还有接向其它电压域的吗？」
- U#2: 「统计下目前DDGOA的WOWTOP中，CMLeft/CMDqL/CMCenterL/CMCenterR/CMDqR/CMRight/CMAryA这些电路模块中，分别有多少个CmLatchX5L电路模块？」
- U#3: 「统计...CMLeft/CMCenterR/CMCenterL/CMDqL/CMDqR/CMRight中，从...里出来的cm1的testmode,有多少连接器件的vcc端口有多少是vdd2h电压域？有多少连接器件的vcc端口是vint电压域？...前三个字符是"cm1"都算是cm1的testmode」
- U#4: 「统计...有多少连接器件的vcc端口有多少是vdd2h! ？有多少连接器件的vcc端口是vintcore! ？...」

## 真实资产
- `/home/shanksw/netlist.presim~`：~101MB flat SPICE 网表（DDGOA WOWTOP fullchip），7687 个 .SUBCKT
- `/home/shanksw/cmleft_body.txt`：806 行，CMLeft .SUBCKT 体（agent 预提取）
- XI_CMLeft_712 实例位于 parent subcircuit `ChanEdgeL`（byte 23080836，body len 94378）

## agent 工具链（17 个脚本迭代）
count_cm1_outputs.py → explore_dom{,2,3,4,5}.py → classify_dom{,2,3,4,5}.py → classify_final.py → explore_subs.py → count_latch.py → verify_latch.py → count_cm1_dom_permodule.py → inspect_dq.py → inspect_power.py → inspect_vcc_dom.py → inspect_vcc_assign.py → count_cm1_dom_v2.py

## 关键技术发现（金标准）

1. **cm1 testmode 计数**：CMLeft 端口 990 个，cm1* 前缀 704 个（cm1_ag_ 556 + cm1_fc_ 76 + cm1_ro_ 58 + cm1_ts_ 13 + cm1_vblhtemp_ 1）。每个 `<n>` 都是独立单 bit 端口（无多位总线）。

2. **电压域分类机制**：在 CMLeft `.SUBCKT` 体内，只看 `X` 实例行（数字单元，如 bufLx16/dlyg0of8Ls2/CmFsLatchX5L），观察每条 X 行的电源引脚 token（inh_vdd2h/inh_vintcore/inh_vdd1）。cm1 信号所连 X 行的 inh_* token 决定其电压域。
   - **关键陷阱**：`.SUBCKT CMLeft` 头部 `+` 续行（L20）列出全部 pass-through 电源端口（inh_vdd2h/inh_vss/inh_vintcore/inh_vdd1/inh_vintcoredq/inh_vintbus...）与 cm1_ts 信号共现。naive grep 全行共现会把 12 个 cm1_ts 误判为 vintcore。正确做法：**排除 .SUBCKT 头部及 + 续行，只看 X 实例行**。结果：704 cm1 全部 vdd2h，0 vintcore。

3. **CmLatchX5L 实例计数**：按 .SUBCKT 作用域（.SUBCKT xxx ... .ENDS xxx）统计 X 行末 token == CmLatchX5L 的行数。全局 335 实例 + 1 .SUBCKT 定义 + 1 .ENDS + 1 注释 = 338 词法引用。7 模块内：CMLeft=44, CMDqL=45, CMCenterL=46, CMCenterR=54, CMDqR=43, CMRight=46, CMAryA=51（共 329）。变体 CmFsLatchX5L/CmLatchX5Unit/CmLatchX5Initial 不计。

4. **DQ 模块特殊电源**：CMDqL/CMDqR 的 cm1 信号所连数字单元 VCC 端口叫 `inh_vcc`（非 inh_vdd2h），是 DQ 逻辑专用电源。LvlShftVint2Vcc* 电平转换器证 inh_vcc ≠ vintcore。

5. **6 模块最终汇总**：CMLeft 704(vdd2h) / CMCenterR 636(vdd2h) / CMCenterL 646(629 vdd2h + 17 pass-through) / CMDqL 320(vcc) / CMDqR 383(vcc) / CMRight 363(vdd2h) = 共 3052，vdd2h 2332 / vcc 703 / vintcore 0 / other 17。

## 合成映射（A/B/C 全不相交）
| 维度 | A(可见) | B(隐藏) | C(嵌入 check) |
|---|---|---|---|
| 模块 | PwrCtrlA-F (6) | VoltRefA-E (5) | CurrSenseA-C (3) |
| 前缀 | pa1 | vb2 | cs3 |
| 电源域 | vdda/vddb/vddc | vaa/vbb/vcc | vxx/vyy/vzz |
| 目标单元 | PwrLatchX3R | VoltLatchX2S | CurrLatchX4T |
| 陷阱域 | vddb==0 | vbb==0 | vyy==0 |
| 总前缀 | 36 | 35 | 18 |
| 总单元 | 18 | 20 | 9 |

## task family dup-check
现有 netlist 解析类 case：TscodecompTruthTable(CDL 门级真值表仿真) / NetlistSvRulesReorg(SystemVerilog 规则重组) / PwrSpVSrcBitExpand(pwr deck v-source 比特展开) / SpiceMeasGroupExpand(.meas 族扩组) / CdsLibNetlistInventory(lib.defs 网表清单) — 本 case = SPICE flat 网表多模块 .SUBCKT 作用域解析 + 前缀端口计数 + X 实例行电源 token 电压域分类(头部+续行 pass-through 陷阱排除) + 目标单元实例计数, 机制不同 ✓
