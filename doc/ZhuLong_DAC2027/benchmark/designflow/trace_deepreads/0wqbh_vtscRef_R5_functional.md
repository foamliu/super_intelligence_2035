# Deep-read: 1794470412317_0wqbh (tongni @ hfeg0pkn004 / 10.129.2.13)

- **session**: 1794470412317_0wqbh.messages.json (227 msgs, 1.25MB, dir-format clines session)
- **match_count**: 38 · **keywords**: netlist:187;analog:61;schematic:59;hspice:46;mosfet:4;opamp:2;pyaether:1;aether:1
- **tools**: 53 editor / 24 read_files / 23 run_approved_command / 7 list_allowed_files

## 用户真实任务（trace-faithful）
tongni 对网表 `zmh_AI_VtscRef_standard_tb_sim_schematic.netlist`（VtscRef 电压参考 + 数字控制逻辑，sim-schematic）做 **R5 功能推导**：从网表连接关系推导顶层「输入→输出」的组合逻辑功能，产出布尔等式 + 真值表；识别运放核拓扑；区分两条修调路径；并把推导固化成可复用 `r5_functional_report.py` 集成进 `sim-sp-gen` skill 的 `run_netlist_checks.py`（R1-R4 之后自动触发 R5）。

## 关键推导结果（来自 assistant 真实工作）
- **顶层 I/O**：`cm0_ag_ShftVtsc<2:0>` + `PwrOn3` = 输入；`Vtsc2Vcc`/`VtscAmpDis` = 逻辑输出（名字像输入，实际是 AG_VtscRefLogic 内 invLx8/bufLx8 驱动的状态输出）；`VtscRef` = 参考输出（顶层挂 Cgatein 负载）。
- **Vtsc2Vcc** = `PwrOn3 & shft<2> & shft<1> & !shft<0>` → shift code **110**
- **VtscAmpDis** = `PwrOn3 & shft<2> & shft<1>` → shift codes **110, 111**
- **运放核** `AG_VnocVdleqVtscRefAmpCore`：NMOS 输入差分对 + cascode + PMOS 电流镜，两级折叠式（213 管，位于 AG_VtscRefAnalog 内）。
- **修调路径**：`cm1_ag_AdjVtsc<4:0>` → VtscRef **电压**修调；`cm1_ag_RegLbias` → 经 lvlshft→HbiasV 修调**稳压器偏置电流**（两条不同路径，曾误把 RegLbias 当电压修调，用户纠正后改对）。

## case 化决策（A 档 trace-faithful → B 档便携化）
真实网表 1.25MB 且 /rundata 路径 .75 不可读，故按 trace 结构**忠实重建紧凑网表**（保留真实块名 AG_VtscRefLogic/AG_VnocVdleqVtscRefAmpCore/AG_VtscRefAnalog、真实 stdcell 链 nand2Lx1/invLx4/nand3Lx1、真实等式 code110/110-111、NMOS 输入对拓扑）。
- **A（可见）**：code110 逻辑 + NMOS 输入对运放
- **B（隐藏）**：code101/011 逻辑 + PMOS 输入对运放（结构不同，非换文件名）
- 判分：subprocess 在 B 上跑候选脚本，独立 oracle 复算 B 真值表+拓扑+修调，跨输入 guard 在 A 上重跑抓写死，12 条独立断言，3 negative 全 FAIL。

## 为什么前 8 轮（r506-r512）漏掉它
前轮按 mc desc 看 fresh，被高 mc 跨域噪声（xbl88 mc420 netlist-only）占满视线；0wqbh mc=38 不在 top，但 keyword 构成是**真正 analog/spice 签名**（analog+schematic+hspice+mosfet+opamp，无 drc/verilog/innovus 噪声），spice-ratio=12.7% 不高但**绝对 hspice 计数 46 + mosfet/opamp 上下文**是真实 spice_sim 任务。本轮改用 keyword 构成（非纯 spice-ratio）筛出。

→ 交付：EDA-Eval-DesignFlow-VtscRefR5Logic-001（spice_sim, L2, k=12, ref 12/12 PASS, 3 fake + 3 neg FAIL）
