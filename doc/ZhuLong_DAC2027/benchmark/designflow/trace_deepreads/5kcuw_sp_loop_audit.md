# 深读笔记 — 5kcuw (ghyang@10.129.2.12, mc70, schematic_netlist)

**session**: 1790241654352_5kcuw.messages.json (N=67 msgs, 5 user turns)
**trace_source**: user=ghyang, host=10.129.2.12, session_file=1790241654352_5kcuw.messages.json, match_count=70
**domain**: schematic_netlist (FineSim SPICE 激励文件循环语法审查 + 修复)

## 用户轮（A-faithful 取 U#0 逐字原文）
- **U#0（A-faithful 任务说明，逐字）**：「帮我检查这份仿真激励文件 /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist/stimulus_PatternAll.sp中的R 循环和for 循环的使用是否符合仿真器的要求，如果不符合应该改成什么样的规范，它被用于同路径下的sim_w0w1r1w0r0_normalYio_PN.sp文件」
  - 纯提需求（审查 + 不合规则重写为规范），用户未给根因/未给修复方案 → A-faithful 合格。
- U#1：问合规的循环写法（前4周期 + 每4周期一循环 + for 写 32 组信号线）— 后续轮，不进 A 档 prompt。
- U#2：贴报错日志 `sim_..._testfor.log` 求分析。
- U#3：`tb_w0` measure 找不到 targ。
- U#4：abs 之后第二次过目标值的时间（cross=2/rise=2 不成功）。

## agent 流程（msg1-67）
1. read_files 读 stimulus_PatternAll.sp + sim_..._PN.sp + finesim_option + 同目录其他 stimulus（stimulus_0911.sp / stimulus_Pattern1.sp / w0w1r1w0r0.sp）。
2. 从 `sim_w0w1r1w0r0_normalYio_PN.log` 第 77 行确认仿真器 = **Synopsys FineSim V-2023.12-1**（mode promd/spicead）。
3. **关键发现（A#10/A#13/A#19）**：
   - **问题 1 `.for` 循环（约 190-194 行）**：日志 `WARNING! Unknown command '.for' is ignored`。FineSim **不支持 `.for`**，整块被忽略 → VDatain<{i}> 4 个脉冲源从未创建。
     原写法：
     ```
     .param i=0
     .for i=0 to 3
     VDatain<{i}> Datain<{i}> 0 pulse (pv...)
     ```
   - **问题 2 PWL `R` 重复（166 行）**：日志 `ERROR! incomplete resistor 'r'`。FineSim **不支持 PWL 的 `R` repeat 关键字**；`+ R` 续行被误解析为电阻元件声明（缺两节点 → incomplete resistor）。
     原写法：
     ```
     vwren_dsain wren_dsain 0 pwl (
     ...
     + R
     ```
4. **推荐合规方案（A#16）**：
   - 32 组相同信号线：① 子电路实例化 ② 总线展开 `<0:31>` ③ 显式展开。
   - `.for` → 显式 unroll 或总线展开。
   - PWL `R` → 显式重复时间点对（unroll repeat）。
5. agent 因 /proj 路径 policy 不可写（A#11/A#12 `get_agent_policy_status`），未直接改文件，交付**审查报告 + 手动修改说明**（A#13）。

## 金标准（trace 末尾用户实际接受的结果）
- 用户未明确"接受"某文件（U#1-U#4 是追问/扩展），但 agent 的核心交付 = **审查报告 + 推荐修复**。A-faithful 金标准取 agent 的修复逻辑：检测 `.for` 与 PWL `R` 两处不合规 → unroll `.for` 为显式实例 + 展开 `R` 为显式 PWL 时间点 → 输出合规激励 + 审查报告。
- 真实 /proj stimulus 经 policy 不可附加 → **B-grade synthesized**（忠实编码两处 bug 结构）。

## 合成设计（B-grade synthesized, L1）
- 资产 A = `stimulus_PatternAll.sp`：含 `.for i=0 to N-1` 块（N 个 VData<{i}> 脉冲源）+ PWL `+ R` 重复（base 4 点 + R）+ 其他保留内容（.param/.tran/.meas/注释）。
- 金标 `gen_fix_stimulus_ref.py`（CLI `<stimulus.sp> [--out] [--report]`）：解析 `.for ... .endfor` → unroll N 显式行（{i}→索引）；解析 PWL `+ R` → 展开 base 点为 nrep 次重复（每次时间偏移 tperiod）；其余行原样保留；写合规激励 + 审查报告（两问题 + 修复动作）。
- 隐藏 B = `stimulus_B.sp`（不同 N/nrep/tperiod/pvdd + 信号名 VAddr/vclk）；B2 = `stimulus_B2.sp`（cross-input guard）。
- check 14-16 条件：结构/run/无 .for/无 +R/unroll 计数/PWL 展开计数/保留内容/报告两问题/报告修复动作/反硬编码 A/跨输入 B2/CLI/确定性。

## 教训（预记）
- SPICE 激励 FineSim 不支持 `.for` + PWL `R` 是 schematic_netlist L1 可验好范式（两 bug 类天然丰富条件）。
- 反硬编码双轴：B 不同 N/nrep/信号名 + B2 不同 → 击破硬编码-A 与硬编码-B。
