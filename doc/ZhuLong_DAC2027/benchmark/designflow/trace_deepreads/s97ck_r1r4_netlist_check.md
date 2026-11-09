# trace_deepread: s97ck R1-R4 netlist static check (tongni @ hfeg0pkn001)

## trace 元信息
- session: `1794217104209_s97ck.messages.json` (tongni @ hfeg0pkn001 / 10.129.2.10)
- size: 258622 B, 20 msgs, agent=lead, updated 2026-11-09T09:44:28Z
- match_count: 160 (spice_sim dominant)
- skill: `sim-sp-gen` (仿真文件生成 / netlist static check)

## 用户轮（A-faithful 选轮评估）
- **U#0 (msg 0)**: 嵌入 skill_instructions(sim-sp-gen) + 隐含请求「检查 R1-R2」（在 skill args 里）—— skill-trigger 轮，非纯需求轮
- **U#10 (msg 10)**: `[sim-sp-gen] /proj/dscqa/V0/workdir/tongni/simulation/dscqa_analog_AG_VisoRef_schematic_ALPS/dscqa_analog_AG_VisoRef_schematic.netlist 检查R1-R4` —— **提出需求（检查 R1-R4），未给根因/方案** → A-faithful 合格 ✓
- **U#14 (msg 14)**: `/proj/dscqa/V0/workdir/tongni/simulation/AI_test_sim_logic_test_1_schematic_ALPS/AI_test_sim_logic_test_1_schematic.netlist 再给出这个R1-R4的报告` —— 第二个 netlist 的同型请求

## assistant 工具链
- list_allowed_files (skill scripts dir + /proj simulation dir)
- run_approved_command: `r1r2_report.py <netlist>` (msg 7) → R1+R2 报告 (msg 8)
- run_approved_command: `run_netlist_checks.py <netlist>` (msg 11) → R1-R4 合并报告 (msg 12)
- run_approved_command: `run_netlist_checks.py <netlist2>` (msg 15) → 第二 netlist R1-R4 (msg 16)
- run_approved_command: `r3_fanout_report.py <netlist2>` (msg 17) → R3 完整 (msg 18, 因合并输出截断补跑)

## 金标准（trace tool_results 内完整捕获）
- netlist1 (dscqa_analog_AG_VisoRef_schematic) R1-R4 gold: msg 12
  - R1: AG_CXcap2S55x56(no dom)/AG_VisoRefAnalog(vdd1+vss)/AG_VisoRefClpComp(vcc+vdd1+vss)/AG_VisoRefLogic(vcc+vdd1+vss)/AG_VisoRefTempSlpAnalog...
  - R2: net027 跨域 invLx8(VCC)↔invMx2(MEDIUM)
- netlist2 (AI_test_sim_logic_test_1_schematic) R1-R4 gold: msg 16 + R3 补 msg 18
  - R1: AG_Vcc2scLogicActSpare(vcc+vss)/invLx1/invLx16/invVx2/invVx8(vdd1+vss)...
  - R3: Total top-level instances=74, Stdcell=65, fanout alert
  - R4: AG_Vcc2scLogicActSpare spare check

## 附件获取（BLOCKER → 绕过）
- **BLOCKER**: 真实 netlist 在 `/proj/dscqa/V0/workdir/tongni/simulation/...` 与 `/rundata/dscqa/V0/simdir/finesim/workdir/tongni/...` 均对 e0031982 **permission-denied**（tongni-owned）；trace 内 assistant 用 run_approved_command 直接跑脚本（未 read_files netlist），故 netlist 内容**不在 trace tool_results**。
- **绕过（B-synthesized）**：skill 脚本（r1r2_report.py/r3_fanout_report.py/r4_spare_report.py/run_netlist_checks.py）位于 `/home/tongni/.cline/skills/sim-sp-gen/scripts/`，权限 `-rw-rw-r--`（others=r）→ **e0031982 可读**。读取后理解 R1-R4 逻辑（suffix→domain 分类、层次化 scope-aware 跨域检测、顶层扇出、Spare 40% 充分性），合成 4 份同格式 SPICE netlist（A 可见 + B1/B2/B3 隐藏），用真实 skill 脚本作 reference 解，trace gold report 作结构校验基准。

## 判定
- **CLEAN produce-task**（spice_sim，B-synthesized）：用户提需求「检查 R1-R4」未给根因 → A-faithful 选轮合格；真实 netlist 不可读 → 降级为 B-synthesized（合成输入 + 真实 skill 脚本作 ref）。
- domain: spice_sim（netlist 静态检查，sim-sp-gen skill 域）
- level: L1（离线 Python 解析 SPICE netlist，不跑 EDA 工具）
- case: EDA-Eval-DesignFlow-R1R4NetlistCheck-001, k=13
