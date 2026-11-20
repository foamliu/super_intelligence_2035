###############################################################################
# sta_main.tcl -- PrimeTime STA flow 主控脚本
#
# 按读入顺序依次 source 编号步骤脚本，编号即执行顺序。
# 执行方式(示例):
#   pt_shell -f ./scr/sta_main.tcl -x 'set DESIGN xxx; set CORNER xxx; set MODE xxx'
#
# 脚本会先自动定位 ROOT_DIR(本脚本所在 scr/ 的上一级)，再 source
# setup/common_setup.tcl(变量中枢) 与 scr/ 下 10 个编号步骤脚本。
###############################################################################

# ---- 定位 flow 根目录与 scr 目录(除非 -x 已显式传入) ----
if {![info exists ROOT_DIR] || [string length $ROOT_DIR] == 0} {
    set _main_file [info script]
    if {[string length $_main_file] > 0} {
        set SCR_DIR  [file normalize [file dirname $_main_file]]
        set ROOT_DIR [file normalize [file dirname $SCR_DIR]]
    } else {
        set ROOT_DIR "."
        set SCR_DIR  "$ROOT_DIR/scr"
    }
}
if {![info exists SCR_DIR] || [string length $SCR_DIR] == 0} {
    set SCR_DIR "$ROOT_DIR/scr"
}
set SETUP_DIR "$ROOT_DIR/setup"

puts "RM-Info: sta_main: ROOT_DIR = $ROOT_DIR"
puts "RM-Info: sta_main: SCR_DIR  = $SCR_DIR"

# ---- 变量中枢：所有默认值集中于此，可被 -x 覆盖 ----
source "$SETUP_DIR/common_setup.tcl"

# ---- 预建输出件目录 ----
foreach _d [list $LOG_DIR $RPT_DIR $SDC_DIR $SESSION_DIR] {
    if {![file exists $_d]} { file mkdir $_d }
}

# ---- 按编号顺序读入流程步骤 ----
source "$SCR_DIR/1_setup.tcl"
source "$SCR_DIR/2_read_lib.tcl"
source "$SCR_DIR/3_read_design.tcl"
source "$SCR_DIR/4_read_constraint.tcl"
source "$SCR_DIR/5_read_parasitic.tcl"
source "$SCR_DIR/6_check_design.tcl"
source "$SCR_DIR/7_update_timing.tcl"
source "$SCR_DIR/8_report_timing.tcl"
source "$SCR_DIR/9_analyze_timing.tcl"
source "$SCR_DIR/10_rpt.tcl"

puts "RM-Info: sta_main: STA flow completed for $DESIGN_NAME ($CORNER/$MODE)."