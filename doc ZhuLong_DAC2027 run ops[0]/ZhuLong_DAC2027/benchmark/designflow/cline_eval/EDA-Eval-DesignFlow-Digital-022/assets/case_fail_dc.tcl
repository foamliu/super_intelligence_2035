# ============================================================
# case_fail: 插入 DFT 失败的脚本 (dc.tcl)
# 与 baseline (case1_dc.tcl) 仅在三处 DFT 配置不同, 导致 0 条扫描链。
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

# ---- 时钟门控风格: 误把控制信号改成 scan_mode (关键点 ①) ----
set_clock_gating_style -max_fanout 16 -control_point before -control_signal scan_mode

# ---- 扫描相关信号约束 ----
# scan_mode 被误标为 TestMode 扫描信号 (关键点 ②)
set_dft_signal -view existing_dft -type TestMode   -name scan_mode -port scan_mode -active_state 1 -test_mode all_dft
set_dft_signal -view spec         -type TestMode   -name scan_mode -port scan_mode -active_state 1 -test_mode all_dft
set_dft_signal -view existing_dft -type ScanEnable -port scan_enable -active_state 1 -test_mode all_dft
set_dft_signal -view spec         -type ScanEnable -port scan_enable -active_state 1 -test_mode all_dft

create_test_protocol

# ---- 综合 (预 DFT) ----
compile_ultra -no_autoungroup

# ---- DFT DRC / 预览 ----
dft_drc -verbose > reports/dft_drc.rpt
preview_dft > reports/preview_dft.rpt

# ---- 插入 DFT ----
# 实验性"自动修门控时钟"被打开 (关键点 ③)
set_dft_configuration -fix_clock_gating true
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