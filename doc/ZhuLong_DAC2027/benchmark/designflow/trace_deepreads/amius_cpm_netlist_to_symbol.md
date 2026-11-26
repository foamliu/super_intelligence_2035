# trace_deepread: 1793668594900_amius (pdsong@hfeg0pkn004, mc=272) — CpmNetlistToSymbol

**session**: 64 msgs, cline v3, path `/home/pdsong/.cline/data/sessions/1793668594900_amius/1793668594900_amius.messages.json`
**domain**: schematic_netlist (SPICE CPM subcircuit → Aether symbol)
**A-faithful 选取**: U#0 纯提需求「如何直接将一个只包含RC的netlist直接转换成一个symbol」+ U#1 提供真实 netlist 路径 `Chip_Power_Model_SubCircuit.sp.inc`。用户未给根因/修复方案 → 符合 A 档。

## 用户意图（逐字）
- U#0: 「如何直接将一个只包含RC的netlist直接转换成一个symbol」
- U#1: 「以下是对应的netlist: /proj/drjqa/V0/workdir/pdsong/simulation/PDN_sim/Vtb1_powerCap_split2_FOR_DRCOA/gp/asim_power_scratch.gv_perbump/Chip_Power_Model_SubCircuit.sp.inc」

## agent 工具链
1. skills(eda_agent) → list_allowed_files/read_files SKILL.md
2. RAG_MCP_Server__search_apis (create symbol / import netlist / dbCrtInst / dbCrtSchPin) + get_api_details(aeGenerateSchematicFromVerilog, dbCrtSymbolPin, dmGuiGenSymbolView)
3. search_codebase(GenSymbolFromSchematic|cdlIn) → 结论：Aether 无一键 RC→symbol，只有 Verilog-in
4. SandBox_MCP_Server__run_code probe pyAether (connection refused)
5. U#1 → read_files 真实 netlist → run_approved_command net_parse.py 解析
6. editor 写 cpm_to_symbol.py → run_approved_command 验证

## 关键产物（gold = agent 实际产出，人工复核）
**netlist 真实解析结果**（agent run_approved_command 输出，MSG#56/60）:
- `.SUBCKT PowerModel <47 端子>`，`+` 续行 9 行，含真实 PDN 节点名（vssdll_PDN_*/vss_*/vdll_*/vdpg_*/vddq_*/vddqca_*/*_pad）
- 元件计数：R=3007, L=1190, C=2351, G=253（VCCS）→ 非「只含 RC」
- 47 个端子（全部端口，无 0/gnd 地节点）

**gold 脚本 `cpm_to_symbol.py`**（MSG#57 editor new_text，逐字保留逻辑）:
- `parse_subckt(path) -> (pins, counts)`：跳 `*` 注释/`.ends`/`.end`/`.param`；`.subckt`(case-insensitive) 收 toks[2:] 中无 `=` 的 token；`+` 续行 in_subckt 时并入 pins；元件按 toks[0][0].upper() 分类计数；`\\` 续行符替换为空格
- `layout_pins(pins, pin_pitch=2.0) -> {pin: ((x,y), orient)}`：half=(n+1)//2 左列、余右列；L=max(half,len(right),1)；box_h=(L-1)*pitch；左 (-5.0, -box_h/2+i*pitch) R180，右 (5.0, ...) R0
- CLI `python3 cpm_to_symbol.py <netlist> [lib] [cell]` 打印 SUBCKT pins/Element types/Pin layout/First 6/Last 3；RUN_IN_AETHER=1 时 ae.emyInitAether + dbNewCV + dbOpenCV + dbCrtSymbolPin 建 symbol

## 用户接受
trace 末尾 agent 给出完整方案（47 引脚 symbol + netlist view 建议），用户未拒绝 = 接受。后续无新需求轮。

## case 合成决策
- **A 资产**：真实 47 端子名逐字保留（红线 #2 不脱敏；只有 key/token/密码掩码）；内部 RLC 元件集缩减（真实文件 /proj/drjqa 在 .75 permission denied 不可读，仅 trace tool_result 给出前 26 行 + 解析结果）。元件名 pattern 忠实复刻（R0_1/R_1_1/C_2_x/L_1_x/G0_xx，内部节点 n48/n49）。symbol 任务只需 pin 列表，元件缩减不改语义。
- **hidden B**：完全合成，DDR5-style pvdd/pvss bump 名，25 端子，inline `PARAM_XY=1.0` 须排除，计数 R=80/C=60/L=25/G=10。
- **判分**：check.py 导入候选模块调 parse_subckt/layout_pins + CLI smoke，18 条件 a-r，跨输入护栏用 A（47/120-90-40-15）击败 hardcode-B。
