# trace_deepread: 1794535160342_suz5p (e03101 @ hfeg0pkn003, mc83, digital)

**session**: 1794535160342_suz5p, user e03101, host hfeg0pkn003/10.129.2.12, mc83, 628KB/180 msgs, ~10 real user turns.
**scan**: ssh_eda_search_20261113_131349, keywords verilog:422/netlist:306/schematic:28.

## USER turns (real tasks)
- **U#0 (msg0) 核心 produce-task #1**: `/proj/decqa/V0/simdir/verilog/PTE/e03101/lpddr6_tb_1008/netlist/V0_LP6TOP_2026Oct26.185525/netlist中原有的include的文件现在放在了/proj/decqa/V0/simdir/verilog/PTE/e03101/lpddr6_tb_1008/include中，请替换过去`. → agent read 55MB/1,109,736-line netlist, 写 fix_netlist_includes.py 扫描 `\`include "..."` 语句 → 找到 **15 条** active include 全指向旧路径, 验证每条在新 include 目录下有对应 `<cell>/netlist` 文件, 写 replace_includes.py 备份+逐行替换(保留行尾注释)+verify_replacement.py 校验(行数一致/仅 15 行变化/新路径全存在). 1-turn produce-task, A-faithful 合格(用户给 netlist 路径+新 include 目录, 未给 include regex/路径映射规则/校验逻辑).
- U#37: 分析 irun.log 错误 → ncelab `*E,TYCMPAT` (errforcebit 标量 -1 赋给 integer 数组). analysis.
- U#71/U#75/U#77: 澄清/Q&A (voltagemode info / errforcebit 功能解释). Q&A.
- **U#87 (msg87) produce-task #2**: `帮我修改A_Pattern和B_Pattern` → 改 A/B_Pattern_Sim.v 第 22 行 `errforcebit = -1` → `'{default:-1}` (struct 赋值). agent scan_patterns.py 确认各只 1 处, 备份, fix_patterns.py 替换(B 文件 0555 只读→chmod+改+恢复). produce-task.
- U#108/U#127/U#141: voltagemode info / 仿真文件梳理 / 新 log 定位. Q&A+debug.

## 合成计划 (B档, 用 U#0)
deliverable = 改私有 /proj/decqa/ netlist → INFEASIBLE (.75 Permission denied) → B档合成.
**archetype**: verilog-netlist-include-path-rewriter (新).
**ref**: netlist_include_rewrite_ref.py CLI(--netlist --new-include-dir --out). 规则: 解析 `\`include "PATH"`(双引号); 跳过注释行(`//`/`/*` 在 `\`include` 前); PATH 以 `/netlist` 结尾 → cell=basename(dirname(PATH)), new=`<newdir>/<cell>/netlist`; 否则 cell=basename(PATH), new=`<newdir>/<cell>`; 保留行尾注释; 输出改写 netlist + report.json{total_includes, skipped_comment, angle, mapping[old,new,cell], line_count}. 
**A**: netlist_A.v(8 active include + 2 注释 decoy + 1 angle decoy). **B**: hidden netlist_B.v(不同 cell 名/数量, 10 active + 3 注释 + 2 angle). 
**trap**: ⑪注释 decoy 不改写 ⑫angle <> 不改写 ⑬cell=basename(dirname) 非整路径 ⑭行尾注释保留 ⑮行数守恒 ⑯跨输入守卫 A=8≠B=10 击败 hardcoded_A ⑰3-seed 打乱 include 顺序 mapping 集不变.
**check.py**: 14 条件(a-n) B 内跑 SUT 脚本 vs ref oracle (subprocess 真跑).
