# Deepread: 1794466529228_2397x (e0015056 / hfeg0pkn002) · 2026-11-13 r484

## Session meta
- slug: 1794466529228_2397x, user: e0015056, host: hfeg0pkn002 (10.129.2.12)
- mc: 610, keywords: schematic 302 / hspice 162 / netlist 8
- NMSG: 49, format: role-based (role/content/ts/metadata/trace_id)
- tools: read_files 5, list_allowed_files 2, run_approved_command 5, editor 4, SandBox run_code 8

## User request (原话)
「/proj/decqa/V0/simdir/finesim/decqaF/Netlists/Netlist_Vcap_20260707PM
帮我整理这个电路的所有模块介绍」

## Workflow
1. agent 探索目录 → 发现主网表 decqa_top_LP6TOP_config_Vcap_trans.netlist (~463K 行)
2. 分段 read_files 读网表（>50K 行，需分段）
3. 写 parse_netlist_modules.py 解析 .SUBCKT 定义（遇 editor 6460 字超限 → 拆分 → 结构错乱 → rm 重写 → SandBox run_code ASCII 限制 → 纯 ASCII 版本成功）
4. run_approved_command (python-runner) 跑解析器 → 7799 modules / 12 libraries
5. SandBox run_code 进一步分析：per-library unique module count、top-level LP6TOP 实例提取
6. LP6TOP 是开放式顶层网表（无 .SUBCKT 包装），**TopDesStart 标记顶层起点 (line 462742)
7. top-level instances: 149 (switch_close 79, tmpTieDown 28, DqLdMdl 28, parasiticRC2 12...)
8. 读取 Presim 配置 (lib.defs, no_vcap, ignore_cells)
9. 输出完整模块介绍报告（LP6TOP = LPDDR6 DRAM 顶层设计）

## Key structural facts (for case building)
- 网表格式: .SUBCKT/.subckt + .ENDS/.ends (大小写混用)
- Library 头: `* Library : <name>`, Cell 头: `* Cell : <name>`
- 器件首字母: M=MOS, R/r=Res, C/c=Cap, X=SubInst
- 顶层: **TopDesStart 标记，X 开头为实例，类型名 = 含=的 token 前一个 token
- 实际网表文件权限受限(e0015056 owned)，无法直接 scp → 用 deepread 结构信息构建 trimmed trace-faithful netlist

## Case decision
- task_id: EDA-Eval-DesignFlow-NetlistModSummary-001
- domain: spice_sim, layer: L2
- deliverable: netlist_module_parser.py (解析网表输出 JSON 摘要)
- Input A: trimmed netlist (21 modules, 6 libs, 13 top-level instances)
- Hidden B: variant (19 modules, 7 libs incl analog_lib, 11 top-level instances)
- check.py: 10 assertions (k_check=k_rationale=10≥8)
- 3 negatives: hardcoded_A/always_pass/empty → all FAIL
- §4.9: empty FAIL(a), hardcoded_A FAIL(b), core_removed FAIL(f)
