# Deepread: 5i5bo (zqzhan @ hfeg0pkn002, mc=155) — 2StepOC 功能检查与优化分析

## Trace meta
- session: `1793857124040_5i5bo.messages.json` (134 msgs, 842KB)
- user: zqzhan @ hfeg0pkn002 (10.129.2.11)
- domain hits: drc:387 schematic:314 netlist:269 lvs:117 dbget:114 pyaether:103 dbopencv:55 cmos:54
- storage: **dir-based** `/home/zqzhan/.cline/data/sessions/1793857124040_5i5bo/1793857124040_5i5bo.messages.json`
- 资产路径: `/proj/drcpa/V0/workdir/zqzhan/simulation/drcpa_work_RasSim_Banklogic_Xdec_Array_schematic_ALPS/` (e0031982 **无读权限** → B-grade synthesized)

## 用户意图流（user turns）
| # | 内容 | 性质 |
|---|------|------|
| U#0 | "这个飞书文档你可以阅读吗" (link) | 边际(读文档) |
| U#22 | "我保存了 pyAether_API.md 到 /ai_sandbox/..." | 提供上下文 |
| U#32 | "你是不是可以检查电路的连接关系是否完整" | 子任务(连接检查) |
| U#44 | "input.sp 你先学习下这个仿真pattern文件" | 提供资产 |
| U#48 | "先继续读 stimulus_2stepOC.sp / measure_2StepOC.sp，把激励和测量点搞懂" | 引导深读 |
| **U#64** | **"最终目的是让你帮我检查2StepOc功能，看看有没有什么优化的空间…2Step OC功能就是SA的OC阶段，会分两步打开NCS和PCS，对应SanEn和SapEn信号第一个pulse的上升沿是分步打开的"** | **★主任务(A-grade seed: 提出目标, 未给根因/修复)** |
| U#124 | "现在是暂停了吗" | meta |

## 助手 gold 链路
1. 读 pyAether_API.md (1507行, scheme gen & netlist API 参考)
2. 写 check_connectivity.py (dbSeCheckDesignInfo / dbSeCheckCrossView / net审计 / dbSeHierCheck)
3. 读 input.sp (115行, TT corner/45C/pvcc=1.1, finesim_mode=promd, G5_CIP_Model, 768Meg/384Meg 存储)
4. 读 stimulus_2stepOC.sp (81行, 5组信号: SaNP trim / 2StepOC核心 / OcOff trim / NcAdj码 / 其他)
5. 读 measure_2StepOC.sp (2052行, N=0..255, sapenbusec35→sanenbusec35 传递延迟, 256窗口×rise+fall)
6. grep netlist 定位子电路: RasSim_2stepOcCtrl / R_TwoStepOCtrimDly / RasSim_NcCtrl_LPwr / R_SaCtrol
7. 输出完整2StepOC链路分析 + 优化点

## 2StepOC 功能链路（gold 分析, msg#133）
**核心思想**: SA的SecEnOn复制一份, 一路经4-bit可编程RC延迟, 由TwoStepOc开关选择, 使NCS与PCS(SanEn/SapEn)上升沿错开→"分两步打开"

1. **控制/trim码选择 `RasSim_2stepOcCtrl`**: 按温度分区(HT/LT/NT)+P/N switch, 用mxi2CSx2在Dly/Dly2两组码间选择→输出`cm1_ro_2StepOcDlyo<3:0>`
2. **可编程延迟单元 `R_TwoStepOCtrimDly`(核心)**: In→输入级→RC梯(PMOS上拉1/2/4/8/16 + Cthin二进制定权电容)→invGSx1→Out; 4个trim bit经开关接/断电容改变延迟
3. **NCS/PCS控制 `RasSim_NcCtrl_LPwr`**: 两路mxi2LVx1复用器在"直接SecEnOn"与"延迟SecEnOn_2stepOC"间切换; NCS/PCS分别经不同延迟分支生成
4. **SA控制→SanEn/SapEn `R_SaCtrol`**: OcNcsG/OcPcsG→SanEn2G/SapEn2G及各分区SanEn/SapEn
5. **阵列内**: sanenbusec35/sapenbusec35(测量点), 两路上升沿差=2-step实际skew

## stimulus 关键参数 (A=真实)
- t0=60ns, 仿真=512周期(Step1前256关, Step2后256开)
- `cm1_ro_2StepOC`: [0,256t0)低 / [256t0,512t0)高
- `cm1_ro_2StepOcDly<3:0>`: one-hot bit0→[2t0,4t0) bit1→[4t0,8t0) bit2→[8t0,16t0) bit3→[16t0,32t0)
- `cm1_ro_2StepOcDly2<3:0>`: 反向one-hot (bit3→[2t0,4t0)…bit0→[16t0,32t0))
- `cm1_ro_NcAdj<5:0>`=110110, `cm1_ro_NcAdjHT<5:0>`=011011

## measure 关键参数 (A=真实)
- trig: `v(xi147.xi_m768meg.sapenbusec35)` val=pvpcsg/2 rise=1
- targ: `v(xi147.xi_m768meg.sanenbusec35)` val=pvdleq/2 rise=1
- 窗口: td='2*t0*n', n=0..255 (256窗口×rise+fall=512条.meas)

## B-grade 合成策略
资产不可读(/proj/drcpa private) → 合成 A/B 两套 SPICE 文件复刻上述结构:
- A: TT/45C/pvcc=1.1/t0=60ns/512周期/256窗口/4-bit延迟
- B: LT/-40C/pvcc=1.0/t0=50ns/384周期/192窗口/5-bit延迟 (规模/取值/结构均不同)
- netlist 含 RasSim_2stepOcCtrl / R_TwoStepOCtrimDly / RasSim_NcCtrl_LPwr / R_SaCtrol 子电路定义
- 交付: analyze_2stepoc.py → 解析4类SPICE文件 → report.json
- check: 在B上跑, 14条断言验证报告结构+事实(含反硬编码A≠B + 3-seed一致性)

## 判分歧义风险
- 无: gold 分析是事实性的(解析SPICE→提取参数), 判分对结构化字段
