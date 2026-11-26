# Trace Deepread — btfno (wnyu / hfeahpc502 / mc134)

**trace**: 1794474582550_btfno.messages.json (129 msgs, 640KB, directory-format)
**user/host**: wnyu / hfeahpc502 (10.129.33.25)
**keywords**: netlist:609;analog:547;cmos:362;schematic:203;hspice:184;aether:176;virtuoso:50;pdk:46
**domain**: spice_sim (PLL LPF design + SPICE netlist structural analysis)
**tools**: netlist/hspice/schematic/dbGet/pyAether/spectre/virtuoso/calibre

## 用户意图弧
1. msg0: "PLL的LPF，我要用到的电阻res在哪里，你在m2701的lib里找下" → 找 PDK 电阻
2. msg52: "电阻我想用<24:0>这种比特的怎么设置" → 总线电阻接法
3. msg69: 读 LPF netlist (/proj/m2701/.../LPF/hspiceD/schematic/netlist/netlist)，"分析电路，内部电阻接<24:1>和<499:1>，既要改又要分析，包括调参" → **produce 角度**
4. msg114-128: VCTRL→Rz→VCTRLH 拓扑 Q&A / MOS 四端短接作用 / 跨 Rz 并联 MOS cap 必要性 → 纯 Q&A

## agent 产出（结构分析，4 类异常）
读 netlist (msg70) 后分析出：
- **XR1 VCTRL VCTRL rm1s**: 两端口电阻两端同 net (短路/占位)
- **switch_open/switch_close**: .subckt 定义但主电路未例化 (死代码)
- **XPM0/XPM2 prvt_ckt**: D/G/S/B 四端全接 VCTRL (Vgs=0 不导通，惰性器件)
- **R0 r=0.001** (switch_close 内): 近零电阻 (近短路)
还查到 rm1s 模型 Rsh≈0.507Ω/□ (M1 金属电阻)。

## A 档可行性
不可行：netlist 在 /proj/m2701/V0_DDR4 项目目录，对 e0031982 权限受限；
且 session 后半段(msg114-128)是交互式 Q&A 无产出脚本。
⇒ **B 档**：忠实复刻 netlist_A(4 类异常) + 合成 hidden B(变体) +
  lpf_anomaly_detector.py(静态结构异常检测器，4 类) + check.py 13 断言(独立复算GT)。

## 判定：做（B 档 produce-task，区别于既有 case）
DeckConsistencyCheck-001 = sim deck 三类一致性；NetlistModSummary-001 = 模块摘要；
本 case = SPICE 网表**结构异常/占位器件**检测（短接/死器件/死子电路/近零电阻），
方向不同，非 near-dup。
