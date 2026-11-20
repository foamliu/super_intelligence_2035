# Deepread: bgrlw — R_RfIPRHRadd module-purpose explain Q&A

**session**: 1791524223726_bgrlw · **user**: xrxiong · **host**: hfeg0plg74(10.129.8.112) · **mc**: 38 · **domain**: schematic_netlist
**trace_source**: xrxiong@hfeg0plg74 / 1791524223726_bgrlw.messages.json (23 msgs, 849KB)

## 用户原话（逐字，substantive user turns）

| msg | 用户原话 | 附件 |
|-----|---------|------|
| 0 | 读取这个网表 | netlist = R_RHDLUTFull_TestBench_TRNG_PRACAddSub2_Verilog_TOP (658KB testbench) |
| 2 | R_RfIPRHRadd这个模块的作用失身吗 | — |
| 5 | 读取这个网表 | netlist = R_RfIPRHRadd (7.4KB, self-contained) |
| 7 | SecEnDly的作用是什么 | — |
| 9 | 读取这个网表 | netlist = R_RfIPRHRadd (re-read, timestamp diff) |
| 13 | 读取这个网表，这个网表是另一个模块 | netlist = R_RHRAddrLat (24KB) |
| 15 | 读取这个网表，这个网表是另一个模块 | netlist = R_RHRCalCtrl_PRAC_PreACRst (20KB) |
| 17 | RfshExt和RfshIP还有Rfsh的关系 | — |
| 19 | RRASTD是什么的缩写 | — |
| 21 | 这个信号和Section 时能信号的前后关系理论上应该怎么样 | — |

## 用户核心意图

netlist-grounded module-purpose explain Q&A：用户读 Verilog 网表，问「模块作用是什么 / 信号作用是什么 / 信号间关系 / 缩写含义 / 时序关系」。全程无脚本产物，纯解释型 Q&A。旧规则判 "netlist explain Q&A no deliverable" 不可造；按 11-15 新标准 = 真实用户意图，可造。

## 助手解释（gold 参考）

1. **R_RfIPRHRadd 模块作用**：RfshIP = Refresh In-Progress, RHR = Row Hammer Refresh, add = Address。DFF(ffrqCSx1 I18) 在 RRASTD 上升沿采样 Rfsh → RfshIP_pre → SR 锁存器(rsnor22CSx1 I7) 保持 RfshIP → SecEnDly 延迟链清除。
2. **SecEnDly**：SecEn → dlyg4of8CSs1 → dlybiasn250ps → dlybiasn1250ps → SecEnDly（~1.5ns 延迟），控制 RfshIP 清除时机。
3. **RfshExt/RfshIP/Rfsh 关系**：Rfsh(输入脉冲) → RfshIP(R_RfIPRHRadd 输出, DFF+SR锁存) → RfshExt(R_RHRCalCtrl 中透明锁存器 latrqCSx2 在 RfshIP 窗口锁存 Rfsh)。
4. **RRASTD**：Row RAS sTrobe Delayed = RasEnBnk，行地址选通延迟，用作 DFF 采样时钟。
5. **RRASTD vs SecEn 时序**：RRASTD 是采样时钟节拍，SecEn→SecEnDly 控制 RfshIP 清除窗口。

## R_RfIPRHRadd 网表结构（A 资产，7.4KB self-contained）

4 delay-cell 子模块（dlyg0of4GSs2_ut/dlyg0of4GSs2/dlyg0of8CSs1_ut/dlyg4of8CSs1）+ 顶层 R_RfIPRHRadd。
顶层端口：output RfshIP/RfshIP_Add/RfshIP_B/RfshIP_preB, input CkeRowSCmosRst/GResetN/PulseModeN/RHRExt/RRASTD/Rfsh/SecEn/prePulse, inout inh_vss/vcc/vbn/vbp/vdbias。
实例：rsnor22CSx1 I7(SR锁存), invLx1/invCSx1/invCSx2/invCSx4/invCSx16/invGSx1/invGSx2/invGSx4(反相器), nand2Lx1/nand2GSx1, nor2CSx1, ffrqCSx1 I18(DFF), dlyg0of4GSs2/dlyg4of8CSs1/dlybiasn250ps/dlybiasn1250ps(延迟链)。
关键内部信号：SecEnDly, PreRst, RfshIP_pre, net1-net19。

## case 设计（套 #29/#32/#33 v2 netlist-grounded explain pattern）

- **case_id**: RfIPRHRaddModuleExplainQA-001
- **domain**: schematic_netlist
- **form**: Q&A/模块功能解释 → netlist-grounded extraction tool（候选写 netlist_module_explain.py 读 Verilog 网表+问题→结构化解释 JSON）
- **A**: 真实 R_RfIPRHRadd 网表 + 逐字问题
- **B1**: 合成 R_RfshGateSel 变体（structurally different, 同功能 archetype）
- **B2**: 小型变体
- **B3**: trivial 单反相器（优雅降级）
- **check.py**: ~15 cond，grounding + 反硬编码 + data-driven + 优雅降级 + 确定性
