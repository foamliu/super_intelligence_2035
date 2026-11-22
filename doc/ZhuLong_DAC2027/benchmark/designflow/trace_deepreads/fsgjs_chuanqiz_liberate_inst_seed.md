# trace_deepread: 1795152806205_fsgjs (chuanqiz @ hfeg0pnd001)

**Session**: `1795152806205_fsgjs.messages.json` (278 KB, 66 msgs, dict format: version/updated_at/agent/sessionId/messages/system_prompt)
**User**: chuanqiz  **Host**: hfeg0pnd001 (10.129.32.189)  **match_count**: 194 (netlist:161 schematic:83 spectre:6 cellview:18 skill:17 virtuoso:6 dbGet:4)
**Source**: fresh `eda_trace_20261122.log` (generated 20261122_000001, 4059 qualifying sessions) — NOT stale summary.tsv.
**Domain**: schematic_netlist (D-pure, netlist-dominant)

## 真实任务（用户原话）
- msg#0: 「读取 analogIP 库下的 CustomDlyNcCtrlIP」
- msg#24: 「请参考 /proj/dejoa/V0/simdir/char/chuanqiz/tt_25_0p9_compress/sisregular/analogIP/control 目录下的 instance 文件，依据电路图编写 analogIP library 下的 CustomDlyNcCtrlIP cell 的 instance」

## agent 工具链（tool_use counts）
RAG_MCP_Server__search_apis:2, get_agent_policy_status:1, list_allowed_files:3, editor:6, run_approved_command:2, RAG_MCP_Server__get_api_details:2, SandBox_MCP_Server__run_code:14, read_files:3, ask_question:1

关键 SKILL 探针（msg#15/#17/#19/#34/#36）：`dbOpenCellViewByType("analogIP" "CustomDlyNcCtrlIP" "schematic" "" "r")` 读 schematic/symbol，`cv~>instances`（143 实例），`cv~>bterms`/`cv~>pins`（顶层端口 In/Out/OutN + bus cm1_ro_NcDly[4:0]）。

## 交付（agent 终态）
`CustomDlyNcCtrlIP.inst`（Liberate instance 文件）+ `gen_inst_CustomDlyNcCtrlIP.il`（SKILL 生成+自测脚本，fprintf 写 .inst，自测「PASS: all 13 required lines present」）。
.inst 结构：power_meas_supplies {vcc vbp vccz} / power_meas_grounds {vss vbn vssz} / configure_force_mpw ncmpw / 4× add_back_bias_supplies / set_netlist_file [get_location]/netlists/CustomDlyNcCtrlIP.spf_RC / add_pin In/Out/OutN/cm1_ro_NcDly[4:0] / set_subckt_ports {In Out OutN cm1_ro_NcDly_4..0} / add_function Out=In OutN=!In / create_parameter cut_netlist / state_partitions none/one/all。

## reframe 决策
真实资产 /proj/dejoa/V0/simdir/char/chuanqiz/ 属 chuanqiz 私有（本机 e0031982 无读权限，run_commands 实测 Permission denied）→ B-grade synthesized：
原理图派生字段整理为结构化 **cell manifest(JSON)**，A=真实 CustomDlyNcCtrlIP manifest，候选写通用 `gen_inst.py`（数据驱动 manifest→.inst，总线 msb→lsb 展开）。
- 隐藏 B = ClkBufTrio（3 supplies/3 back_bias/5 pins/总线 data[7:0] 8 位/funcs Q=Clk,Qb=!Clk，每维度与 A 不相交）
- 隐藏 A' = RstSync2（2 supplies/2 back_bias/3 pins/总线 sel[2:0] 3 位/单 func，反硬编码第三交叉，token 与 A/B 全维不相交）

## 合成结果（r1119）
**EDA-Eval-DesignFlow-LiberateInstGenQA-001**（schematic_netlist, L1, k_check=k_rationale=16）
- check.py 16 条(a-p)：B 侧(a-k) supplies/grounds/back_bias/netlist/pins/subckt_ports(8位展开)/functions/state_partitions + A' 反硬code交叉(l-o) + 确定性(p)
- §4.9 三假 empty→c/print_only→c/core_deleted→f + hardcode_a→d + hardcode_b→m(7 neg ALL FAIL, 5 distinct≥3)
- 自验：ref 16/16 PASS + 7 neg ALL FAIL
- D.jsonl 554→555, test 字段 byte-sync sha=69cc4b8b82c0b9952d1b057dc988e0549cbc5e14fe1a551a6ae4acff2468b5ac/size=10688
- 台账 fsgjs → case

## dup-check（r1113 lesson）
chuanqiz 已有 2 case（jojdp=CustomDlyIoLogicExplainQA / prsvc=IOStaticLogicDeriveProduce），均不同 task family（IO 逻辑/自定义延迟 vs Liberate inst 生成）、不同 session。LiberateInstGenQA 无 dup。✓
