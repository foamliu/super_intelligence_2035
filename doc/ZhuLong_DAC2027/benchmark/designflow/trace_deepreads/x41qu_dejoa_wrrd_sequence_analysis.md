# x41qu — dejoa LPDDR6 verification directory + wrrd_sequence analysis · r707 deepread

- **session**: `1794551664857_x41qu` · user `chuanqiz` @ `hfeg0pkn005` (10.129.2.14) · mc=158
- **size**: 632,901 B / 86 msgs / 6 user-text-turns / ~40 tool_uses
- **keywords**: verilog:865;analog:633;.def:32;netlist:22;cmos:10;aether:8;waveview:2;lvs:2
- **path**: `/home/chuanqiz/.cline/data/sessions/1794551664857_x41qu/1794551664857_x41qu.messages.json`
- **old parked** (ledger L553): r545 "analysis Q&A (6 user inputs all 分析作用/如何实现), verilog:865 but Q&A not produce-task" — **新标准(11-15)下复活**：analysis-Q&A / code-comprehension 是合法 design_flow 任务。

## 用户轮（6 个）
1. msg[0] (U#0): `/proj/dejoa/V0/simdir/verilog/chuanqiz/lpddr6_dejoa/dejoa 帮忙分析这个目录下各个文件的作用`
2. msg[18] (U#18): `分析下wrrd_sequence这个用例是如何实现的？`
3. msg[50] (U#50): `分析下refresh_sequence这个用例是如何实现的？`
4. msg[63] (U#63): `分析下Active.run的具体实现`
5. msg[76] (U#76): `genpat_Active.pl这个脚本的作用`
6. msg[82] (U#82): `怎么调整linux display` (off-topic env config, 本题无关)

## agent 工具链（~40 calls）
- list_allowed_files: 浏览 dejoa 顶层 + bin/config/coverage/patterns/Regressions 等子目录
- read_files: 读 top.sv / lpddr6_test.sv / lpddr6_package.sv / lpddr6_model.v / lpddr6_specdef.sv / lpddr6_interface.sv / compare_tasks.sv / lpddr6_tasks.sv / lpddr6_idd_tasks.sv / Pattern_tasks.v / A_Pattern_Sim.v / pevave_tasks.sv / proj_monitors.sv / proj_special.sv / glitch_check.sv / dft_tasks.sv / timing_load.sv / sim.sh / runtestcase / runtestcase_refresh / run_tapeout_* / probe.tcl / timing_table / patterns/cmds_wrrd_sequence/{patlist,genpat_pde.pl,Wr24..._sameBG.v,write24_read24.v} / Regressions/{wrrd_sequence.run,wrrd_sequence.inc,refresh.run,refresh.inc,Active.run,Active.inc} / patterns/cmds_refresh/{RefabRefdb.v,refresh_checker/checker.v} / patterns/cmds_Active/{cmds_Active.inc, Actx1_..., Actx2_..., genpat_Active.pl, patlist}
- search_codebase / editor + run_approved_command (python-runner): grep wrrd_sequence/refresh 调用链
- 最终 ask_question(U#82 之前已结束 wrrd/refresh/Active 三段分析)

## 诊断/分析（agent 三段交付，msg[17]/[49]/[62]）

### 1. 目录文件用途（msg[17]）
dejoa 是 LPDDR6 存储器验证环境（TOP 模块 + lpddr6_test 驱动 + 参考模型 + 网表，bin/vsim 启动）。顶层文件：top.sv(仿真顶层) / lpddr6_test.sv(核心驱动/pattern 生成器) / lpddr6_package.sv(SV package) / lpddr6_specdef.sv(规格参数 RANK/DQ/WCK/...) / lpddr6_interface.sv(物理引脚接口) / lpddr6_model.v(参考行为模型 v1.5) / lpddr6_tasks.sv(pin 驱动 task) / lpddr6_idd_tasks.sv(IDD 测量) / compare_tasks.sv(输出比对) / dft_tasks.sv(DFT) / Pattern_tasks.v / A_Pattern_Sim.v 等。

### 2. wrrd_sequence 实现（msg[49]）— 本题核心
**调度链路**：`runtestcase` → `./bin/vsim -sr wrrd_sequence --regnameb=wrrd_sequence -d "LocalPower ALL_REVD_FUSE HSPEED DEFF USESDF CBT_SPEED_LIMIT"`。vsim 取 `-sr`/`--regnameb` 定位 `Regressions/wrrd_sequence.run`（cp 成 `A_Pattern_Sim.v`，主流程）+ `Regressions/wrrd_sequence.inc`（cp 成 `A_Pattern_tasks.v`，pattern 任务清单）。`lpddr6_test.sv` 编译时 `` `include "Pattern_tasks.v" ``，主 `initial pattern_run` 块（L12944）`` `include "A_Pattern_Sim.v" `` 直接执行 `.run` 内容。

**wrrd_sequence.run**：`regression_name = "write_read_burst_chunk&order"`；`Config_Timing(TS_1600)` → `PowerUp()` → `compare_enable("all")`；link-ECC 随机错误注入；`parameter PAT_NUM = 1`；`ifdef HSPEED parameter ARCH_NUM = 3`（else 2）；随机 shuffle 速度节点（`SetDataRateSpeedMR` usrspeedrequire 3200/3200→9600/9600）；`for j<PAT_NUM case(pattern_num[j]) 'd0: write24_read24(.bg(random_bg()),.ba(random_bk()),.row(random_row()),.col0/.col1/.col2(random_col()),.num(...))`。

**wrrd_sequence.inc**：仅 active `` `include "patterns/cmds_wrrd_sequence/write24_read24.v" ``（其余 13 个 Wr24/Wr48 组合全注释）。

**write24_read24.v**：`task write24_read24(reg[GROUP_BITS-1:0] bg, reg[BANK_BITS-1:0] ba, reg[ROW_ADDR_BITS-1:0] row, reg[COL_ADDR_BITS-1:0] col0, col1, col2, integer num)` — 7 形参。Active + Write×4（+SEFF 翻倍）+ Read×4。

### 3. refresh / Active（msg[62]/后续，本题不直接覆盖）
`refresh_sequence` 不存在（全树搜不到），同构的是 `refresh`（`Regressions/refresh.run` 294 行，PAT_NUM=100，68 个刷新/RFM sub-pattern）。Active.run 类似调度链。

## B 档合成（code-comprehension 通用解析器）
- **case_id**: EDA-Eval-DesignFlow-DejoaWrrdSeqAnalyze-001 (verification, C-A, L1, k=19)
- **交付**: `analyze_dejoa_wrrd_sequence.py(dejoa_dir) -> dict` 通用解析器（正则解析 runtestcase/-sr/--regnameb/-d、.run regression_name/PAT_NUM/ARCH_NUM(HSPEED)/case dispatch/speeds、.inc active includes、pattern .v task name+args、lpddr6_test.sv pattern block label、specdef DQ_BITS/RANK_NUM/CA_BITS、top.sv include）。
- **A 档**（trace-faithful 节选，给 SUT 看）: dejoa_A/ 下 7 文件（runtestcase / top.sv / lpddr6_test.sv(pattern_run 块) / lpddr6_specdef.sv / Regressions/wrrd_sequence.run / wrrd_sequence.inc / patterns/cmds_wrrd_sequence/write24_read24.v）。
- **B 档 hidden**（check() 只跑 B，≥12 维全异）: project lpddr7_memx, sr/regnameb=rwseq_x, regression_name="read_write_burst_pair&addr", PAT_NUM=4, ARCH_NUM(HSPEED)=2, case dispatch ['d0,'d1,'d2,'d3], dispatched_task=write32_read32, task_args=8(增 col3), speed_configs=[4800,4800](+11200), defines drop CBT_SPEED_LIMIT add WL_CHECK, specdef DQ_BITS=16/RANK_NUM=4/CA_BITS=6, pattern_run_block_label=pattern_exec, inc active=patterns/cmds_rwseq_x/write32_read32.v。
- **check 19 条 a-s**: a 脚本非空 / b-n 13 字段==B / o-p-q specdef 三参数==B / r anti-hardcode(A vs B ≥6 字段不同, 反 print-B-truth) / s top_includes_test。
- **自验**: ref PASS 19/19 · 4 neg 全 FAIL @ distinct assertions (neg_empty→a/JSON, neg_print_expected→r, neg_core_deleted→a+b/c/d, neg_hardcode_A→b/c/d) · negative_selftest ALL_FAIL_OK · §4.9 三假(空zip/print-expected/core-deleted)全 FAIL。
