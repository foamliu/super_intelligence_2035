# 深读：6qt0a — DRAM RasBnkLogic 网表 delay-cell 信号链追踪工具

## 元信息
- session: 1792831256137_6qt0a
- user: harrywu @ hfeg0pkn002
- mc: 319 (kw: netlist/schematic/analog)
- size: 3.6MB, 435 msgs, 15 user turns
- cwd: /home/harrywu
- netlist: /proj/dscqa/V0/agentdir/harrywu/simulation/RasBnkLogic/netlist (14750+ lines, DRAM Ras Bank Logic)

## 真实用户意图（逐字原文轮）
- U[0]: `/proj/dscqa/V0/agentdir/harrywu/simulation/RasBnkLogic Understand the function of the netlist circuit in this file`
- U[1]: `Set the interface to Chinese`
- **U[2]（提出需求轮，A 档候选）**: `As a new engineer who is encountering this circuit for the first time, I need to immediately know exactly which cell in the circuit can adjust the delay of which signal, please Develop a tool, agent, skill, or similar utility to generate a signal chain containing only delay cells, through which users can quickly identify one or multiple delay cells that require adjustment.`
- U[3]: `Develop it as a Skill, so that you can directly invoke it when I put forward relevant requirements`
- U[4]: `SapEn2 的延迟链是什么`
- U[5]（给出根因+修复，A 档禁用）: `Revise it, and here are a few suggestions: 1. SapEn2 failed to trace the input port and only traced up to SanpDlyA. Could there be no delaycell in the preceding part? 2. All cm signals default to 0... 3. By default, only the input port RasEnBnk has a waveform...`
- U[8]: `SapEn2输出整条延迟链`
- U[9]（给出根因）: `Why don't we keep tracing the signals before SaIn? Since the signal cm1_ro_2StepSa<3> is 0, cm1_ro_2StepSaN<3> will be 1, which will mask both the delay' signal of 2ndSaOn and SanEnIn2Dly...`

## 真实流程
harrywu 在分析 DRAM RasBnkLogic 网表（反熔丝/eFuse Ras Bank Logic）。新工程师需要快速知道哪个 delay cell 调整哪个信号的延迟。agent 读 netlist（14750 行），识别 delay cell（名含 Dly：SanpDlyA/SanDly/SanEnIn2Dly/2ndSaOn 等），从目标信号 SapEn2 反向追踪 delay-cell-only 链。

## A 档资格判定
- U[2] 纯提需求（"Develop a tool to generate a signal chain containing only delay cells"），未给根因 → A 合规
- 但 gold = agent 构建的 tool，trace 经多轮修订（U[5]/U[8]/U[9] 给根因+修复），无明确 user-accepted final produce（trace ends mid-revision）→ **B 档 synthesized**
- live netlist 14750 行不可附加 + cm-mask 语义复杂 → 合成小子集网表（保留 delay-cell 链结构 + non-delay cell + cm 控制信号）

## B 档合成设计
- 工具 gen_delay_chain.py(--netlist --target --delay-pattern --outdir)：解析 .SUBCKT + 实例，从 target 反向追踪 delay-cell-only 链
- 约定：subckt 首端口=输出，次端口=输入
- 停止规则：top 输入端口(port) / non-delay cell 驱动(non_delay_cell) / 无驱动(no_driver)
- 输出 chain.json(结构化) + chain.txt(人类可读 source→target 链)
- A=ras_bnk_logic_A.sp(target=SapEn2, pattern=Dly, 链长 3 SanpDlyA→SanDly→SanEnIn2Dly, source=RasEnBnk port)
- hidden B=ras_bnk_logic_B.sp(链长 2, source port, pattern Dly) 反硬编码长度
- hidden B2=ras_bnk_logic_B2.sp(链长 3, pattern Delay 不同, cells DelayA/B/C) 反硬编码 cell 名+模式
- hidden B3=ras_bnk_logic_B3.sp(链长 1, non-delay BufX 中断, stopped=non_delay_cell) 测 non-delay 停止规则
- 16 条件 a-p：zip/py_compile/B 运行/target/source/长度/cell 模式/链连通/source 是端口/排除 non-delay/可读/B2 跨输入/B3 non-delay 中断/元数据/确定性
