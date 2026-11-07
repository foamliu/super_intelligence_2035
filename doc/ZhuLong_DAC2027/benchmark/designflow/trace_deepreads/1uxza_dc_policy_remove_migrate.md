# trace_deepread: 1793933023338_1uxza (johnl@hfeg0pkn001)

- session: `1793933023338_1uxza.messages.json` (561 KB, 72 msgs, new cline dir format)
- user: johnl · host: hfeg0pkn001 · mc: 302 (234 innovus + 39 synthesis + 28 netlist — daily-log markers; actual content is DC synthesis, "innovus" 是扫描误标)
- domain: digital (DC synthesis script migration)

## 用户意图 (verbatim)
- USER#0: "/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/run_dc.sh ... synth.tcl ... T_mBistTopNew.sdc  这几个是在本机之前跑通过的dc脚本。后面带copy的是其他环境迁移过来的脚本 我现在要跑迁移过来的在本机，你需要帮我修改迁移过来的脚本以便能在本机运行，库要换一下 [3 个 .db 库路径] 用上面这三个库，rtl 用这个[restored.v] 请进行修改 修改后diff 检查...然后跑dc，你要在.../data/ 下单独建立一个工程目录并且所有用到的文件复制到这个目录里 不能引用其他目录到文件"
- USER#28 (refinement): "不用管原来的检查啊不准用的啥的所有的都可以用" → 删除 cell policy
- USER#30: "继续"

## 助手工具链
list_allowed_files → read_files(copy scripts + ref scripts) → editor(inspect_rowred.py) → run_approved_command(python-runner 探测库) → editor(probe_libs.tcl) → run_approved_command(shell-runner dc_shell 探测库内部名/cell) → 探测 lvs 库(180 cell LVS 系列) + GS 库(61) + rowred 库(4 custom) + 库名碰撞(GS/lvs 同名 SS_0p98_m40c 但 cell 名不相交) → RTL 端口确认 → editor(run_dc.sh/synth.tcl/timing_constraints.tcl/README) → run_approved_command(make_diffs.sh) → run_approved_command(launch_dc.sh) → poll → DC 跑通(R_RowRed1024_full 12824 cells 8197 comb+4626 seq 0 unmapped MAPPING_PASS hold) → verify_project.sh 自包含性验证

## gold (用户接受的结果)
- `/home/johnl/.cline/scripts/data/RowRed/run_dc.sh` (953B): SCRIPT_DIR=RowRed, OUTPUT_ROOT=$SCRIPT_DIR/outputs, dc_shell from PATH (command -v), 无 eda-guard, RTL 存在性检查, hold_mapped.v 产物检查, tee dc.log
- `/home/johnl/.cline/scripts/data/RowRed/synth.tcl` (4556B): RTL=RowRed/rtl/rowred_behavioral.restored.v, LIB_DBS=[GS.db, rowred.db, lvs.db], target_library=$LIB_DBS, read_db each, **policy 整段删除** (无 CUSTOM_CELLS/ORDINARY_CELL_PATTERN/633 计数/set_dont_use)，仅 remove_attribute 清 dont_use/dont_touch 标记，check_mapping 仅 is_unmapped, compile_ultra + hold repair 全保留
- `/home/johnl/.cline/scripts/data/RowRed/timing_constraints.tcl` (1812B): = copy sdc + 迁移注释头，功能零改动(无路径/cell 引用)

## 与 r214 DcScriptMigrate-001 (i7eyp) 的关系
同源(johnl RowRed behavioral DC 迁移, 同 3 库同 4 custom cells 同 top R_RowRed1024_full, i7eyp=1793932764787 vs 1uxza=1793933023338, 相隔 4 分钟)。但任务角度互补：
- i7eyp/r214: KEEP + FIX policy (修 ORDINARY_CELL_PATTERN 的 LVS 漏匹配 bug, 保留白名单/dont_use)
- 1uxza/r217: REMOVE policy entirely (用户明示"所有的都可以用")
→ 作 distinct case 交付 (check 测相反变换)

## benchmark case
EDA-Eval-DesignFlow-DcPolicyRemoveMigrate-001 (digital, L2-static, 15 conds a-o, A档 faithful)
