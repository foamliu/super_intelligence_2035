# Trace Deepread: d1cg3 — FineSim DC 不收敛 how-to Q&A

**Session**: 1792042544705_d1cg3.messages.json
**User**: t0002441 @ hfhds201 (10.129.32.75)
**MC**: 103 (synopsys:2984; hspice:185; spectre:40; cadence:22; netlist:21)
**Domain**: spice_sim
**File**: 68 msgs / 1021KB, in subdirectory `1792042544705_d1cg3/`
**Date**: 2026-10-15

## 用户意图

用户只问了一个问题：
> Finesim仿真报DC不收敛的错误, 可能的原因及解决方案有哪些?

这是典型的 how-to 知识问答：用户遇到 FineSim DC 不收敛，想知道原因和解决方案。

## 助手工具链

1. 尝试 skills (ask-eda not found) → eda_agent skill
2. list_allowed_files 探索文件系统
3. search_codebase 搜 FineSim/DC/convergence (无结果)
4. list_allowed_files 探索 /apps → /apps/synopsys → /apps/synopsys/finesim
5. 定位 FineSim 文档目录: /apps/synopsys/finesim/P-2019.06-SP2-4/doc/
6. read_files 读 FineSim 文档 HTML (finesim_options.06.036.htm, finesim_pro.03.01.htm, topicmap.xml, finesim_options.06.005.htm, finesim_spice.04.04.htm)
7. 基于文档+专业知识给出结构化指南

## 助手最终回答（关键知识点）

### DC 不收敛典型现象
- "DC analysis did not converge"
- "The last step failed to converge"
- "Cannot find DC operating point"
- "Gmin stepping failed"

### 三类原因
1. **电路拓扑**：浮空节点、电压源短路、电容/电感开路、无 DC 通路
2. **模型/参数**：模型参数不合理、模型收敛性差(BSIM4/PSP)、初始条件不当、温度极端
3. **仿真选项**：ITL1 不足、RELTOL/ABSTOL/VNTOL 过严、GMIN 过低

### FineSim 特有选项
- finesim_dcstep=1 (DC 步进法)
- finesim_gmin=1e-12 (Gmin 步进)
- finesim_srcstep=1 (电源步进)
- finesim_damp=1 (阻尼 Newton)
- finesim_maxdciter=500 (最大 DC 迭代)
- finesim_dc_restart=1 (不收敛自动重启)
- finesim_accuratedc=1 (精确 DC)
- finesim_force_converge=1 (强制收敛)

### 四种收敛方法
1. Gmin stepping: 从大 Gmin 逐步减小
2. Source stepping: 从零逐步增加电源
3. DC sweep: .DC VDD 0 1.8 0.1 替代 .OP
4. Pseudo-transient: 转化为瞬态问题

### 诊断流程
1. 检查 .lis 文件定位不收敛节点
2. 使用 .PRINT DC V(all_nodes) 输出节点电压
3. 检查模型参数范围
4. 逐步简化电路，二分法定位
5. 尝试 HSPICE/Spectre 排除工具差异
6. 重点关注报错节点周边子电路

### 分级配置模板
- Level 1: RELTOL=1e-4, ABSTOL=1e-9, VNTOL=1e-6, ITL1=500, GMIN=1e-12
- Level 2: + finesim_srcstep=1, finesim_dcstep=1
- Level 3: + finesim_gmin=1e-9, finesim_damp=1
- Level 4: + CONVERGE=1, finesim_force_converge=1

## Case 合成决策

- **A 档不可行**：真实 FineSim 文档在 .75 /apps/synopsys/ 下，是 Synopsys 商业许可文档，不可离线打包进沙盒
- **B 档 synthesized**：用 doc_ref.json 概括文档结构（选项名/方法名/描述），A 用浮空节点场景的合成 run.log + netlist.sp，B 用电压源短路场景（全异根因/错误标记/节点）
- **判分有牙**：error_messages + root_cause_category 必须从日志动态解析（cross-input guard 验证），4 种收敛方法全覆盖，FineSim 特有选项 ≥4，标准 SPICE 选项 ≥4
- **新形态首例**：FineSim DC 不收敛 how-to 指南首例 + DC 收敛诊断分级配置模板首例
