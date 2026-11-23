# Deepread: qm71w — FindCir4CrossProbe_wx (naming violation cross-probe CSV)

## Trace source
- session: 1795069196158_qm71w.messages.json
- user: xiwang @ hfeg0plg107
- mc: 134 (schematic:130;analog:64;pyaether:168;cmos:269;verilog:184)
- nmsgs: 306
- domain: schematic_netlist

## User intent
用户 xiwang 调用 FindCir4CrossProbe_wx skill, 在 DDGOA V0 设计库 (根 /proj/ddgoa/V0/libs) 中:
1. 扫描设计层次 → fullmap.json (9.3MB, 8985 parents, rooted at WOWTOP)
2. 找命名违规 cell (下划线规则 + verilog keyword 规则)
3. 生成 cross-probe CSV (一行一个违规 cell 实例, 含 hierPath 实例路径 + 总线展开)

## Agent tool chain
- list_allowed_files / read_files: 探索工作目录, 读 fullmap.json 结构
- editor: 写 name_rules.py (命名规则检查), find_name_violations.py (BFS 从 WOWTOP 找违规 cell), builder_violation.py (DFS 拼 hierPath + bus 展开 + CSV 输出)
- run_approved_command (shell-runner / python-runner): 运行脚本, 发现 4106/9438 cell 违反下划线规则, 40 seeds → 47448 rows

## Checkable kernel (离线)
- Input: fullmap.json = {parent_key "lib/cell/view": {child_cell: [[inst_name, child_lib], ...]}}
- Process:
  1. BFS from root → all reachable cells
  2. Underscore rule: cell name contains "_" → violation
  3. DFS from root, first level only follows top_label instance; each violating cell instance recorded; recurse into violating cells that have children
  4. Bus expand: XI3<1:0> → XI3<0>, XI3<1>
  5. CSV: item,hierPath,dbType,instName,libName,cellName,viewName,propertyName,propertyValue,findByProperty
- Output: cross-probe CSV

## Case synthesized
- ID: EDA-Eval-DesignFlow-HierNameViolateCrossProbeProduce-001
- Domain: schematic_netlist, L1
- k_check: 14
- A: fullmap_A.json (6 rows, 5 violating cells, 1 bus)
- B1: fullmap_B1.json (12 rows, 4 violating cells, 2 buses × 4-bit + multi-instance DQBlock)
- B2: fullmap_B2.json (3 rows, 2 violating cells, 1 bus 2-bit)
- §4.9 三假 + hardcode_a 全 FAIL
- 内核与 r1214(.map P|N|I)/r1213(SPICE hier+dc stim)/r1209(Verilog hier)/HierNetTrace(SPICE X positional)/NetlistHierarchyExtractQA(col-count table) 全不相交
