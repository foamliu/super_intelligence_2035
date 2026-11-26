# 深读笔记 · i7eyp (johnl@hfeg0pkn001, mc39, 185 msgs, 899KB)

## trace_source
- user: johnl, host: hfeg0pkn001 (10.129.2.10), session: 1793932764787_i7eyp.messages.json
- match_count: 39 (kw: synopsys:271 verilog:38 aether:27 pyaether:23 schematic:8 ...)
- tools col: 23 pyAether 8 schematic 2 synthesis 2 cellview 1 netlist 1 dbCreateRect
- 选取原因：daily-log 11/08 fresh-on-disk 兜底捞到（11/05 scan 候选已被 cline 清盘）；
  johnl i7eyp = synopsys:271 synthesis 重，digi>ana，digital 域；185 msgs 可控；929KB→899KB。

## 用户轮（A-faithful rule2 评估）
- **U#0（clean 需求，A-faithful rule2 OK）**：「/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/run_dc.sh  synth.tcl  T_mBistTopNew.sdc  这几个是在本机之前跑通过的dc脚本。后面带copy的是其他环境迁移过来的脚本 我现在要跑迁移过来的在本机，你需要帮我修改迁移过来的脚本以便能在本机运行，库要换一下 [3 个 .db 库路径]  rtl 用这个[rowred_behavioral.restored.v]  请进行修改 修改后diff 检查修改前后的必要性和准确性 然后跑dc，你要在 scripts/data/ 下单独建立一个工程目录并且所有用到的文件复制到这个目录里 不能引用其他目录到文件」
- U#2-4：file-listing tool_results（非用户意图）
- U#6/10/14...：tool_results
- U#184：「继续」（continue，会话末尾，DC 多次超时后用户催继续）
- 无其他 clean 需求轮；gold 取 agent 的迁移产物。

## agent 工具链（关键节点）
1. read_files 原 + copy 三件套（run_dc.sh/synth.tcl/T_mBistTopNew.sdc + 带 copy 的迁移版）
2. run_approved_command(python-runner) check_files.py 验证 3 库 + RTL + dc_shell 存在
3. dc_shell query_lvs_lib.tcl 探 LVS 库名 → `SS_0p98_m40c`（与 GS 库同名！）
4. dc_shell test_merge_libs.tcl 同载 3 库 → GS 2 cells, custom 4 cells, LVS 93+57 cells
5. **关键发现**：copy 的 cell regex `(LV|L|GS)x[0-9]+` 匹配不了 LVS cells（`invLVSx1` → `LV` 命中后剩 `Sx1` 不匹配 `x[0-9]+`）→ 必须改 `(LVS|LV|L|GS)`
6. project_setup.py 建自包含工程 dc_addr_to_region_run/，复制 RTL + 3 .db + 脚本
7. editor/create_project_files 写 adapted synth.tcl（分块，多次超 6000 字符限制 → split）
8. fix map rule 转义 `\\[` → `\[`
9. fix_target_lib：target_library 用 .db 路径（非逻辑名）
10. run_dc.sh 跑 DC → compile Pass1 area=202617.7 slack=0.00 312 cells allowed（策略生效），但 sandbox 超时 SIGKILL（多次）
11. write_clean_synth.py 简化 compile（去 -area_high_effort_script/-incremental）再跑 → 仍超时
12. 会话末尾 U#184「继续」后无更多消息（任务未完全收尾，但脚本迁移正确、DC 已成功编译到 mapping）

## gold（agent 真实产物，已 scp 验证）
- /home/johnl/.cline/scripts/data/dc_addr_to_region_run/{synth.tcl(148行/5420B), run_dc.sh(18行/669B), timing_constraints.tcl(46行/1737B)}
- DC log（run_20261106_105536_1TSx/dc.log）：compile Pass1 area 202617.7 slack 0.00，312 cells allowed，CELL_POLICY 生效

## 迁移 diff（copy → gold，可断言的事实）
**synth.tcl**：
1. 绝对路径 `/home/EDA/rowred_work/...` → `${SCRIPT_DIR}/...`（自包含，RTL=${SCRIPT_DIR}/rtl/rowred_behavioral.restored.v, CONSTRAINTS=${SCRIPT_DIR}/timing_constraints.tcl）
2. 单库 `LIB_DB stdcells.db` → 3 库 `LIB_DB_GS/LIB_DB_CUSTOM/LIB_DB_LVS`，各 `read_db`
3. `target_library` = 3 个 .db 文件路径列表（非逻辑名 rowred_behavioral_cell_mapping_area_objective）
4. cell regex `(LV|L|GS)` → `(LVS|LV|L|GS)`（修 LVS 命中 bug）+ 加 `mx[0-9]+|mxi[0-9]+` 前缀
5. CUSTOM_CELLS 从 8 个裁到 4 个（新库实际有的：latqn_RowRed_AF_lvclk1 / latbank_RowRed_AF2_invLVSx1 / latbank_RowRed_AF4_invLVSx1 / xnor2_RowRed_cmp4_invLVSx1）
6. 硬编 cell 计数断言 `!= 633 / != 239 / != 394` 删除 → 改为遍历 `get_libs` 动态计 allowed/blocked
7. `LIB_NAME` 单名删除；skip gtech/standard.sldb
8. compile 简化 `compile_ultra`（去 -area_high_effort_script + -incremental，超时缓解）
9. define_name_rules map 保留 `\[` `\]` 转义
10. TOP = R_RowRed1024_full（不变）

**run_dc.sh**：绝对 SCRIPT_DIR/OUTPUT_ROOT + dc 绝对路径 + eda-guard → `$(dirname BASH_SOURCE)` 自包含 + bare `dc_shell -no_gui -f synth.tcl | tee dc.log`

**timing_constraints.tcl**：内容等价于 copy sdc（apply_synthesis_constraints + apply_hold_constraints 同 procs/时钟/约束），重排格式 + line continuation

## case 设计（A 档 faithful, L2-static, digital）
- prompt = U#0 原文
- 资产 A = copy 三件套 + lib_metadata.json（3 库 db 名/逻辑名、custom_cells、top、rtl 名、extra prefixes）
- 隐藏 B = 合成 copy_B（不同 top/db名/custom cells/硬编计数）+ lib_metadata_B.json，与 A 零标识符重叠
- 候选 = dc_script_migrate.py（读 copy + metadata，产 adapted synth.tcl/run_dc.sh/timing_constraints.tcl 到自包含工程）
- check 14 conds (a-n)：subprocess 真跑候选于隐藏 B + 静态解析 adapted 脚本
- gold 事实断言：3 库 read_db、target_library=.db 路径、regex 含 LVS、CUSTOM_CELLS=B 的、无 /home 绝对路径、TOP=B 的、硬编计数删除、map \[ \]、run_dc.sh 自包含、A 反硬编守卫、B' 确定性

## 与既有 DC case 区分
- r156 DCDirSwitch / r191 DcSynthAnalyze / r202 DcLogErrDiagnose：分别是目录切换/综合产物分析/日志诊断
- i7eyp DcScriptMigrate = 跨环境脚本迁移（路径自包含 + 多库替换 + cell regex bug 修复 + 动态计数），不同子任务
