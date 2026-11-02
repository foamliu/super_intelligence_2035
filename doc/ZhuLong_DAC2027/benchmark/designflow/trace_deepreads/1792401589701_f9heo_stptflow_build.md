# 深读笔记 — 1792401589701_f9heo — PrimeTime STA flow 构建

- **trace_source**: user=`e0046913`, host=`hfeg0pkn003`(10.129.2.12), session_file=`1792401589701_f9heo.messages.json`, match_count=94, tools=`synopsys:236;cadence:103;innovus:51;genus:39;voltus:36;calibre:30;hspice:29;primetime:22`
- **规模**: 185 msgs, 814KB messages.json
- **真实任务摘要**: 用户在 `/rundata/lacaa/TV1_digital/simdir/yutingq/STA` 构建 PrimeTime STA flow，用 demo 跑通；cshell 运行脚本放 `run/`，tcl 步骤脚本放 `scr/` 按读入顺序编号 `sta_main.tcl;1_setup.tcl;...;10_rpt.tcl`；需环境配置/工具选型/子模块 lib 读入；选项传参适配不同 corner/mode；参考 `/apps/imctf/cad/script/digital_flow/feint` 的 Synopsys PT reference flow；工具 `/apps/synopsys/primetime`，需 `module load` 取 license。

## A 档选轮
- **选轮 #0**（逐字原文，纯提出需求，无根因/修复方案）：
  > 尝试为我在当前目录下（/rundata/lacaa/TV1_digital/simdir/yutingq/STA）构建一个STA flow,工具为PrimeTime，并使用一个demo来跑通。我已经生成了几个关键的文件层次，分别用于存放各种输出件log、rpt、sdc（生成后缀为.sdc的文件）、session（用于在pt_shell中交互）等。我希望任务运行的目录在run下面（因此需要在run目录编写任务运行脚本，我希望这个脚本以cshell语言编写），我希望过程中各个环节读入的脚本存放在scr目录下，且以tcl语言来编写，各个过程中脚本按照读入顺序进行编号（如：sta_main.tcl;1_setup.tcl;2_read_constranit.tcl;……;10_rpt.tcl）。我需要enable几个关键的feature：环境配置、工具选型、子模块lib输入件读入，并且可以通过选项传参来适配不同corner、模式。你可以参考/apps/imctf/cad/script/digital_flow/feint下的synopsys pt reference flow的做法。工具是/apps/synopsys/primetime，但值得提醒的是你可能需要module load 才能正确获取license.
- 第二条用户轮 #169（README 改英文）属格式修正，不取作任务说明。

## 真实 assistant 工具链与产物
- 58 次 `editor` 写入 + 31 次 `run_approved_command` 执行。
- 前半段大量 probe（smoke_pt*.sh / probe_loader.sh / probe_libstdcxx.sh）解决 PT 启动问题（module load ds/pt、GLIBCXX 污染、LD_LIBRARY_PATH 注入）。
- 最终产物 `/home/e0046913/STA_flow/`（已 scp 回 .75，tar 取回）：
  - `setup/common_setup.tcl`（4277B）：变量枢纽，STA_ROOT/SCR_DIR/DATA_DIR/LOG/RPT/SDC/SESSION，DESIGN/PT_CORNER/MODE/LIB_PROFILE 有 `info exists` 守卫（可被 `-x` 覆盖），`switch -exact -- $LIB_PROFILE { tutorial {core_typ.db} hl22 {corner-keyed ccs .db per VT} }`
  - `scr/sta_main.tcl`：source common_setup + 按 `STA_STEP_LIST` 顺序 source 1_setup..10_rpt
  - `scr/1_setup.tcl`：建输出目录 + `set_app_var search_path` + `sh_continue_on_error false`
  - `scr/2_read_lib.tcl`：`read_db` 每个 ANALYSIS_LIBRARY_FILES + ADDITIONAL_LINK_LIB_FILES + `target_library`/`link_path`
  - `scr/3_read_design.tcl`：`read_verilog` NETLIST_FILES(默认 `data/$DESIGN/$DESIGN.vg`) + `current_design` + `link_design`
  - `scr/4_read_constraint.tcl`：`read_sdc`，按 MODE 解析 `sdc/${DESIGN}_${MODE}.sdc` 优先，回退 `sdc/${DESIGN}.sdc`
  - `scr/5_read_parasitic.tcl`：`read_spef` SPEF_FILES（空则跳过）
  - `scr/6_check_design.tcl`：`check_timing -verbose` → rpt（注：PT 无 check_design）
  - `scr/7_update_timing.tcl`：条件 `set_propagated_clock`（PROPAGATE_CLK）+ `update_timing -full`
  - `scr/8_report_timing.tcl`：`report_timing -delay_type max`(setup) + `-delay_type min`(hold)
  - `scr/9_analyze_timing.tcl`：`report_constraint -all_violators` + `report_clock` + `report_clock_timing skew` + `report_analysis_coverage`
  - `scr/10_rpt.tcl`：`write_sdc` + `save_session` + 写 `run/sta.done` marker
  - `run/run_sta.csh`（7589B）：cshell，`-design/-corner/-mode/-profile/-ptver/-ideal_clock/-extra` 选项解析（switch/while），`module load ds/pt/$PTVER`，`pt_shell -f scr/sta_main.tcl -x "set ..."`，PASS/FAIL 判 `run/sta.done`
  - `run/run_demo.csh`：跑 2 corner（tt0p8v25c/func + ss0p72vm40c/func -ideal_clock）
  - `deploy_to_STA.csh` / `README.md`
- 金标准 = 该 STA_flow/ 树（真实工具产物，人工复核脚本结构合理且匹配 feint reference 模式）。

## 合成决策
- domain = `pnr_signoff`（PrimeTime STA 是签核链路核心）。
- 档位 = **A 档 trace-faithful**（选轮 #0 逐字原文，纯需求无根因）。
- 难度层级 = L1-boundary：交付脚本树，判分静态校验结构 + csh 语法 + tcl 命令内容 + 泛型（不真启 pt_shell，因 license/二进制 .db 在判分环境不可用；与 InnovusLaunchDiag-001/FormalityLaunchDiag-001 同模式）。
- **A（SUT 可见）**：prompt.txt（#0 逐字）+ task_brief.md（≤3 行接口）+ feint_reference/{pt.tcl,common_setup.tcl}.excerpt + demo_design/mac/{mac.vg,mac_func.sdc,mac.spef} + libs/core_typ.db（文本 stub）。
- **B（隐藏）**：alu8 设计（8-bit ALU vs 16-bit MAC，加 scan_en 扫描 mux）/ corner ss0p72vm40c+ff1p16v0c / mode func+scan（mode-specific SDC `alu8_scan.sdc` 含 `set_case_analysis`）/ lib alu8_typ.db @0.72V/-40C。结构与取值全异于 A，击穿任何硬编码 A 字面量的解。
- **check.py**（20 条断言 a–t）：静态结构(a-e) + 每步 tcl 命令内容(f-m) + run_sta.csh 选项/pt_shell/done 判定(n-p) + B 执行 csh -n subprocess(q) + 泛型(用 $DESIGN/$PT_CORNER/$MODE 不硬编码 mac/tt0p8v25c)(r) + 3-seed 随机化(s) + 鲁棒(-bogus 退出)(t)。
- **negatives**：empty_shell / print_expected_b / naive_hardcode_a（硬编码 mac/tt0p8v25c）/ core_deleted（删 7_update_timing）四错解全 FAIL；§4.9 三假（空壳/print expected/删核心）全 FAIL。
