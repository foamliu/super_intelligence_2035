# 6qt0a — DRAM RasBnkLogic 延迟链 trace 深读

**trace**: `1792831256137_6qt0a` · user `harrywu` @ `hfeg0pkn002` · mc=319
**tools**: 838 netlist / 834 hspice / 338 schematic / 3 cellview / 2 virtuoso (spice_ratio 0.41，纯 spice/netlist 表征流)
**session**: 2026-10-24 08:40 → 10-27 08:12，`failed` (terminal_marker `failed_external_process_exit`，stale_session_reconciler 收尾，非任务失败)
**model**: deepseek-v4-flash (cxmt-deepseek-flash)
**cwd**: `/ai_sandbox/dscqa/V0/agentdir/harrywu`，workspace `/proj/dscqa/V0/agentdir/harrywu/simulation/RasBnkLogic`

## 用户意图演进（12 个用户轮）
1. msg[0]: 「Understand the function of the netlist circuit in this file」(RasBnkLogic 网表)
2. msg[18]: 「Set the interface to Chinese」
3. msg[20]: **核心需求**——「As a new engineer... I need to immediately know exactly which cell can adjust the delay of which signal. Develop a tool/agent/skill to generate a signal chain containing only delay cells, through which users can quickly identify delay cells that require adjustment.」
4. msg[80]: 「Develop it as a Skill, so that you can directly invoke it when I put forward relevant requirements」
5. msg[111]: 「SapEn2 的延迟链是什么」
6. msg[120]: 修订建议——SapEn2 没回溯到输入端口、cm 信号默认 0 屏蔽部分路径、RSTN 常置 1
7. msg[223]: 「SapEn2输出整条延迟链」
8. msg[233]: 质疑为何继续回溯 SaIn 之前的信号（cm1_ro_2StepSa<3>=0 屏蔽 2ndSaOn/SanEnIn2Dly），要求解决方案
9. msg[285]: 给出信号值 `cm1_ro_2StepSa<3>=0 / cm1_ro_2StepSaAct<3>=0 / cm1_ro_2StepSaN<3>=1`
10. msg[325]: **关键转折**——「The delay cell chain also requires determining whether it is valid for the rising edge or the falling edge, so it is very difficult to make a judgment solely based on the netlist. We can adopt a static simulation scheme to trace those delay cells, and then develop a complete solution based on this idea.」
11. msg[361]: **可复现子技能**——「Use the fineism tool to run the simulation yourself, and integrate this process into the skill. Before each run, ask the user whether to re-run the simulation or directly analyze based on the on-site waveform; if there is an existing waveform, prompt the user to input the path.」
12. msg[405]: 提供激励路径 `/proj/dscqa/V0/agentdir/harrywu/simulation/RasBnkLogic/psf/input_lv.sp`
13. msg[433]: 「text limit reached, continue in new session」

## agent 工具链（211 tool_use：editor 81 / run_approved_command 61 / read_files 41）
- `inventory.py` → `delay_chains.py`（网表解析 + 延迟链提取，`--top-signal`/`--trace`/`--stimuli`）
- 反复迭代 `probe.py`/`probe2.py`/`probe_const.py`/`probe_const2.py` 调试回溯逻辑（SapEn2 未回溯到输入端口、cm 常量屏蔽路径）
- `polarity.py`——极性（上升/下降沿）传播器
- `sim_runner.py` + `fsdb_edge_analyzer.py`——FineSim 仿真 + FSDB 边沿分析（msg[361] 后）
- 部署为 Skill `dram-delay-chain`（`/home/harrywu/.cline/skills/dram-delay-chain/`）
- 末轮 `sim_runner.py input_lv.sp --check`

## 可复现子技能抽取（用于 benchmark case）
真实 trace 不可移植部分：(a) RasBnkLogic 是 CXMT foundry DRAM 网表（不可进 .75）；(b) FineSim + FSDB 波形（.75 只有 HSPICE，无 FSDB）；(c) 网表解析回溯逻辑高度项目特定。

**可复现内核** = msg[325]+[361] 的 L2 子技能：**「跑瞬态仿真、按极性传播沿方向、逐级量传播延时」**。
- 输入：网表 + stage_list（每级 cell_type/in_net/out_net/ctrl_const）+ stim_spec（pulse + edge 方向）
- 输出：每级 {极性, in_edge/out_edge, t_in/t_out, prop_delay} + total
- 真陷阱：(1) 极性须按 (cell_type, ctrl_const) 推导（INV/NAND2@vdd/NOR2@vss=inverting；BUF/AND2@vdd=non-inverting），从 stim edge 累积 XOR 传播；(2) `.measure cross=1 td=stim_td-0.1n` 抓有效沿后首个过零点（rise/fall stim 通用）；(3) `.lis` 输出 `t_x=   5.0500n` 带 `n` 后缀，须剥离转 ns。

→ 落地 **EDA-Eval-DesignFlow-DelayChainEdgeMeas-001**（spice_sim, B档 synthesized, L2, track faithful）：自包含 level-1 MOS 延迟链（INV/NAND2/NOR2/BUF/AND2 混合极性），agent 交付测量工具，check 用隐藏 B（不同 model/sizing/vdd/级数/级序/stim edge=fall）重跑 + 参考解 GT 校验 14 条断言。

## claim/状态
- 2026-11-02 19:3x claim 6qt0a（spice_sim）
- 交付 EDA-Eval-DesignFlow-DelayChainEdgeMeas-001（.75 HSPICE 自验：ref 14/14 PASS；3 negative 全 FAIL；§4.9 三假提交全 FAIL）
