# ============================================================
# dc_fixed.tcl: 修复 DFT 插入失败的脚本
# 基于 case_fail_dc.tcl 修正三处 DFT 配置差异, 使其等价于
# 基线 case1_dc.tcl 的正确配置 (修复后可恢复 390 条扫描链)。
#
# 三处修复 (与 case1_dc.tcl 基线一致):
#   [修复 ①] set_clock_gating_style 的控制信号由 scan_mode 改回 scan_enable
#   [修复 ②] scan_mode 由 -type TestMode 改回 -type Constant
#   [修复 ③] 关闭实验性的 -fix_clock_gating (不改动/注释掉)
# ============================================================

source scripts/dc_setup.tcl
source scripts/dc_setup_filenames.tcl

define_design_lib WORK -path ./WORK

# ---- 预编译处理 ----
source sdc/dont_use.tcl
set_svf results/PuTopDftEcc.svf

# ---- 读入 RTL ----
analyze -format sverilog -vcs "-f ../../flist/files_PuTopDftEcc.f"
elaborate PuTopDftEcc
current_design PuTopDftEcc

# ---- 电源意图 ----
load_upf ./scripts/pu_core.upf

# ---- 时序约束 ----
source ./sdc/PuTopDftEcc.sdc

# ---- 时钟门控风格: 测试使能用 scan_enable [修复 ①] ----
# 不能把 ICG 的测试控制信号设成 scan_mode(常量), 必须用 scan_enable
# 这样测试期间扫描使能才能正确控制门控时钟, 保证 shift/capture 时钟可达。
set_clock_gating_style -max_fanout 16 -control_point before -control_signal scan_enable

# ---- 扫描相关信号约束 ----
# scan_mode 是"测试模式常量"信号, 不是 TestMode 特殊扫描信号 [修复 ②]
# scan_enable 才是真正的 ScanEnable 扫描使能信号。
set_dft_signal -view existing_dft -type Constant   -port scan_mode   -active_state 1 -test_mode all_dft
set_dft_signal -view spec         -type Constant   -port scan_mode   -active_state 1 -test_mode all_dft
set_dft_signal -view existing_dft -type ScanEnable -port scan_enable -active_state 1 -test_mode all_dft
set_dft_signal -view spec         -type ScanEnable -port scan_enable -active_state 1 -test_mode all_dft

create_test_protocol

# ---- 综合 (预 DFT) ----
compile_ultra -no_autoungroup

# ---- DFT DRC / 预览 ----
dft_drc -verbose > reports/dft_drc.rpt
preview_dft > reports/preview_dft.rpt

# ---- 插入 DFT ----
# [修复 ③] 实验性"自动修门控时钟"保持关闭 (不使用 -fix_clock_gating)
# set_dft_configuration -fix_clock_gating true
insert_dft

# ---- 增量综合 ----
compile_ultra -incremental

# ---- 报告与写网表 ----
report_area   > reports/area.rpt
report_timing > reports/timing.rpt
report_scan_path -view existing_dft -chain all > reports/scan.rpt
change_names -rules verilog -hierarchy
write -format verilog -hierarchy -output results/PuTopDftEcc_postdft.v
write_scan_def -output results/PuTopDftEcc.scandef
write_sdf results/PuTopDftEcc.sdf

exit