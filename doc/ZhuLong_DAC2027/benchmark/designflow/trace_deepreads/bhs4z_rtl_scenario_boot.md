# Deepread: bhs4z — 数字 RTL 设计 业务场景启动

- **trace_source**: user=e0025768, host=hfeg0pkn001, session=1788347732612_bhs4z.messages.json, match_count=38, agent=lead
- **size**: 52KB, 15 msgs (9 user / 6 assistant), dict format (version/updated_at/agent/sessionId/messages)
- **tools hit**: pyAether 7, schematic 2, netlist 7, "lang":"pyAether" 7, synthesis 1 (scan keywords); assistant tool calls: skills(1), RAG_MCP_Server__search_apis(4), RAG_MCP_Server__get_api_details(2), SandBox_MCP_Server__run_code(1)

## User turns (verbatim)
- USER#1 (msg 0, the ONLY real user input): `<user_input mode="act">启动业务场景: 数字 RTL 设计</user_input>`
  - **A-faithful verdict**: ✅ pure goal (启动=启动业务场景), no root cause, no fix proposed. Qualifies as A-faithful task statement.
- USER#2–9 (msg 2/4/5/7/8/10/11/13): all empty-text tool_result wrappers (not real user turns).

## Assistant flow
1. msg 1: thinking → load `eda-aether-init` skill (pyAether env activation: `ae.emyInitAether("-adv")` mandatory first).
2. msg 3: `RAG_MCP_Server__search_apis` ×2 ("digital RTL design create cell schematic", "RTL verilog design") → returns aeGenerateSchematicFromVerilog, aeGenSymbolAndSchematicByVerilog, aeCompileVerilogView, dmVerilogIn, dmGuiGenVerilogView, dmGuiCompileVerilogView, aeDesignIsSchematic, dmExportNetlist, seGuiShowNetlist, ...
3. msg 6: `RAG_MCP_Server__get_api_details` (aeCompileVerilogView, dmVerilogIn, aeGenerateSchematicFromVerilog, aeGenSymbolAndSchematicByVerilog, dmGuiGenVerilogView, dmGuiCompileVerilogView) + search "create library cell design open" → aeOpenDesign, openDesign, emyDesignGetLib, emyDesignOpenHier, mdeGetWindowLibCellView.
4. msg 9: get_api_details(aeOpenDesign, openDesign, emyDesignGetLib) + search "simulation netlist export run" → aeExportNetlistCDLShow, dmExportNetlist, seGuiShowNetlist, aeRegExportNetlistTrigger, seGuiRunSimulation.
5. msg 12: `SandBox_MCP_Server__run_code` (pyAether emyInitAether test) → FAIL (sandbox refused at 10.129.8.86:55209).
6. msg 14 (FINAL, gold standard): comprehensive markdown report:
   - 一、环境初始化要求: `ae.emyInitAether("-adv")` mandatory.
   - 二、核心能力 API 表 (10 rows): dmVerilogIn / dmGuiGenVerilogView / aeCompileVerilogView / dmGuiCompileVerilogView / aeGenerateSchematicFromVerilog / aeGenSymbolAndSchematicByVerilog / aeOpenDesign / dmExportNetlist+aeExportNetlistCDLShow / seGuiShowNetlist / seGuiRunSimulation.
   - 三、完整流程模板代码: emyInitAether → dmVerilogIn → dmGuiGenVerilogView → aeCompileVerilogView(['lib','cell','verilog']) → aeGenerateSchematicFromVerilog → aeOpenDesign → dmExportNetlist → seGuiRunSimulation.

## Gold standard (人工复核)
- 产物 = msg 14 的结构化能力报告 + 流程模板脚本。
- 判分取结构层：报告含 env_init 节 + API 表(N 条 RTL 相关) + 流程模板；模板 emyInitAether 先于任何 ae.*/dm.*/se.* 调用；流程 API 按 import→view→compile→schematic→open→netlist→simulate 顺序。
- 不取措辞 / 不取报告 Markdown 格式细节。

## Case 合成计划
- **case_id**: EDA-Eval-DesignFlow-RtlDesignScenarioBoot-001
- **domain**: eda_other (pyAether API discovery / digital RTL design scenario bootstrap)
- **track**: A-faithful
- **level**: L1-static + subprocess
- **prompt**: USER#1 逐字原文 + 交付接口
- **交付**: outputs/submit.zip 含 `generate_scenario_report.py`（读 config JSON → 产出 rtl_design_api_report.json + rtl_design_flow_template.py）
- **A 资产**: config_a.json（scenario="数字 RTL 设计", keywords=[verilog,rtl,schematic,netlist,compile], api_pool 15 条含 RTL-relevant + distractors[layout/design_check/design_access]）
- **隐藏 B**: config_b.json（scenario="模拟版图设计", keywords=[layout,pcell,rect,inst,via], 同 pool 但 relevant 集反转：layout APIs relevant, verilog APIs distractor）→ 结构对立防硬编码
- **check.py**: ~16 conds a-p（zip2files / py_compile / report env_init / api_table≥7 / 排除 distractor / 含 dmVerilogIn / 含 aeCompileVerilogView / 含 schematic_gen / 含 aeOpenDesign / 含 netlist_export / 含 seGuiRunSimulation / 模板 emyInitAether 先行[subprocess stub] / 流程 API 顺序 / B 报告含 layout 不含 verilog-as-flow / B≠A 反硬编码）
- **negative**: empty / print_expected / core_deleted / naive_hardcode_a (硬编码 A 报告，B 跑出 verilog → 被 cross-input guard 击杀) + naive_skip_env (不写 emyInitAether)
