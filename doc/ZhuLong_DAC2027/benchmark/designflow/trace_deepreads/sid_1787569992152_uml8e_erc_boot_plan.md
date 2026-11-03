# 深读笔记: 1787569992152_uml8e (e0024597/hfeg0pkn005, mc=342)

## UI 节选
- UI#0 (纯需求 A-档 seed): "ERC_AI_CHECK 代码在 ERC/codes下，请基于codes下的run_all.sh，对ERC/drcpa/下的数据文件跑完所有follow"
- UI#1: tool JSON parse err (噪音)
- UI#2: "I will provide LLM credentials (API URL, API key, model name)" (ask_question 选项选择)
- UI#3: "Use the pyAether sandbox LLM instead (if available)" (选项选择)
- UI#4: "Run in deterministic mode (LLM-free, no API needed, lower recall) — proceed now" (选项选择)

## trace 11+ 轮真实迭代
agent 探目录→读 run_all.sh/README→发现 3 问题：(1)数据文件在 drcpa/ 但 run_all.sh 从 codes/ 自动探测→copy；(2)default python3(3.7.1) 缺共享库→/usr/bin/python3(3.6.8)；(3)无 LLM config→ask_question→用户选 deterministic。

跑 pipeline→Step1 NameError SUPPLY_NET_PATTERNS undefined→查根因：prepare_new_netlist.py 的 patch_script() 贪婪正则 `STDCELL_LIB_PATTERNS\s*=\s*\[.*?\n\]`+re.DOTALL 从 STDCELL_LIB_PATTERNS=[ 吃到 SUPPLY_NET_PATTERNS 末尾 ]，删了 BLACKBOX+SUPPLY 定义→从 tar 恢复原 analyze_errors_v1.py + Step0 加 --no-patch。

Step1 retry→ProcessPoolExecutor(initializer=) 需 3.7+，3.6.8 太老→改 wrapper symlink python3.11/3.12→Step1 跑通 11567 errors(~3min)→final_report.csv(5.1MB)+unique_voltage_nodes.csv(271KB)→Step2 sort_voltage_nodes greedy set cover→top_refined_merged.csv。

Step3 Virtuoso→top_cell 自动检测为 TECHLIB/ddr5top(错，因 top_lib 空回退 cds.lib 第一个 DEFINE)→查 netlist header `drcpa_top/DDR5TOP/schematic`→修 project_config.json top_lib=drcpa_top→Virtuoso OA sysname=unknown→OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x 修→但仍 `cannot open drcpa_top/ddr5top` 因 /proj/drcpa 750 cadmin:drcpa user in guest 无权。

Step3-4 阻塞→best-effort: top_refined_verified.csv=copy top_refined_merged + dummy cell_chains.csv(全 PORT)→generate_forcenet.py→forceNet_spice.txt(7.5KB/101 cells/144 nets)成功。最终 agent 给完整 Pipeline Execution Summary。

## A-档 disqualified 理由
gold=run_all.sh 改动 + forceNet_spice.txt 依赖：私有 ERC_AI_CHECK 代码(analyze_errors_v1.py 7160+行/prepare_new_netlist.py/run_verification_pipeline.py/sort_voltage_nodes.py/generate_forcenet.py)、36MB netlist/12.5MB ERC CSV(drcpa 私有)、Virtuoso+/proj/drcpa 权限。沙盒不可复现→B-档 synthesized L1-boundary。

## 合成 case (EDA-Eval-DesignFlow-ERCBootPlan-001)
合成 erc_boot_planner.py 把上述 6 类修复决策固化为静态探测+JSON boot-plan。26 条断言 a-r。详见 MEMORY_DESIGNFLOW_C.md r55 流水。
