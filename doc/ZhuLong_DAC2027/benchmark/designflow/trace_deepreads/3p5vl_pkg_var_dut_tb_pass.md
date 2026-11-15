# Deepread: 3p5vl — package 变量如何在 DUT 和 TB 之间传递值 (verification analysis-Q&A)

- **session**: 1792902413837_3p5vl.messages.json
- **user**: alanji  **host**: hfeg0plg49/hfeg0plg99/hfeg0plg100  **mc**: 275  **domain**: verification (本 shard A 域)
- **agent**: lead (cline)  **n_msgs**: 122  **size**: 1.7MB
- **trace_source**: scan ssh_eda_search_20261115_081559, A-domain mc>=5 候选 (verilog:1952/netlist:712/systemverilog:151/rtl:111)

## 用户原话 (USER#0, 逐字)
> `/rundata/ddgoa/V0/simdir/verilog/alanji/verilog.lpddr5.ddgoa.alanji.Sep30.105051/` 这个目录下的分步编译，package 里面的变量如何在DUT 和 TB 之间传递值，用的脚本是当前目录下vim8, 命令是：`./vsim8 -s -d "LPDDR5G LocalPower STEP_BUILD USESDF PWRBC" --simspeedup "gen all" --ncconfig "+ncnowarn+TRTDECAY +ncnowarn+CSINFI +ncsdf_nocheck_celltype" --tool xrun -q vbatch_lp -l 1025 &`

## 用户真实意图 (任务初衷铁律1)
**analysis-Q&A**: 理解 LPDDR5 仿真目录的分步编译流程 + package 变量在 DUT/TB 间的传递机制。用户要的是**分析结论**（不是 ship 工具/脚本）。属于 11-15 令恢复的 analysis-Q&A 合法任务形态。旧筛子 r316 判 "analysis-only how-to = weak" 已按新标准作废。

## Agent 工具链
1. list_allowed_files 探索 simdir (depth 2) → 发现 lpddr5_package.sv / arb_package.sv / lpddr5_test.sv / lpddr5_interface.sv / aa.sv / libs_bind.sv / config/ / bin/
2. list_allowed_files bin/ + config/
3. run_commands 被 disabled (raw shell disabled)
4. read_files 读 lpddr5_package.sv / lpddr5_test.sv / arb_package.sv / config/cds.lib / config/verilog.rc
5. read_files 读 bin/vsim / bin/vsimxrun / aa.sv / config/tbconfig
6. list_allowed_files depth 1 hidden
7. 多轮 read_files 读 vsim8 脚本 (1622-1641 行 xrun 命令生成段) + libs/simlib_*.sv
8. 用户多次纠正 agent 不准确的分析 → agent 最终给出严谨结论

## 关键产物 / 分析结论 (evidence anchor)
1. **Package 文件**: `lpddr5_package.sv` (主 package), `arb_package.sv` (arb package), `shared_pkg.sv` (定义 `lpddr5_shared_pkg`)
2. **import 机制**: `import lpddr5_shared_pkg::*` — 在 `module TOP` 内部 (top.sv line 55) vs lib 文件外部 `ifdef STEP_BUILD` 条件 import
3. **编译顺序 (vsim8 脚本, snapshot gen 模式 gen_run_snapshot==1)**:
   - line 1622: `lpddr5_package.sv`
   - line 1623: `arb_package.sv`
   - line 1624: `lpddr5_interface.sv` (含 channel_interface)
   - line 1625: `shared_pkg.sv` (lpddr5_shared_pkg 定义)
   - line 1638: `-v libs/simlib_*.svp` + `-v libs/simlib_*.sv`
   - line 1703: `netlist/.../WOWTOP.sv`
4. **关键发现 (用户纠正后)**:
   - **snapshot 模式** (`--simspeedup "gen all"`, gen_run_snapshot==1): shared_pkg.sv 在 -v libs 之前编译 → import 可见 ✅ (当前用法正确)
   - **正常模式** (gen_run_snapshot==0): 只编译 top.sv → import 在 module TOP 内部 → lib cell 模块看不见 🔴
5. **vsim8 命令**: `vsim8 -s -d "LPDDR5G LocalPower STEP_BUILD USESDF PWRBC" --simspeedup "gen all" --tool xrun -q vbatch_lp -l 1025`
6. **条件编译**: `ifdef STEP_BUILD` 控制 import 是否生效 + channel_interface 来源 (proj_special.sv if/else 分支)

## 可判分性评估 (P-006 (C) 分流)
- **evidence-anchor 强**: package 文件名 + import 语句 + vsim8 行号 (1622-1641, 1703) + STEP_BUILD 条件 + snapshot/normal 模式对比 — 全可逐 token 回溯 A 文件
- **结论 (C)-(A) 可造**: v2 还原 analysis-Q&A 形态, 交付 `pkg_var_pass_analysis_report.json` only, check() content-correctness + evidence-verification + B judge-self-check (隐藏 B = 另一套 package 结构/编译顺序) + 3-seed
- **A 资产**: lpddr5_package.sv + arb_package.sv + shared_pkg.sv + lpddr5_test.sv + top.sv (excerpt) + vsim8 脚本 (1622-1641 行段) — 需从 .75 scp 并 sanitize (去 /rundata 私有路径)
- **B 资产**: 不同 package 名/变量/import 位置/编译顺序 (judge-self-check only, 内嵌 check.py _parse)

## 合成计划 (下一轮, DEBT)
1. scp A 文件 (lpddr5_package.sv / arb_package.sv / shared_pkg.sv / lpddr5_test.sv / vsim8 脚本段) → sanitize
2. 建 hidden B (不同 package 结构)
3. check.py ≥8 断言: content (package names / import mechanisms / compile order / STEP_BUILD conditional / snapshot vs normal / vsim8 command) + evidence-verification + B judge-self-check + 3-seed
4. reference report + negatives (empty/print-no-ev/wrong-conclusion) + selftest
5. 自验 + 追加 A.jsonl

## 旧筛子记录
- r316 (2026-11-10): parked, "analysis-only how-to = weak, not produce/diagnosis"
- 11-15 令: analysis-Q&A 全部恢复为可造 → 本案复活
