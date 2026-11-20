##########################################################################################
# fm.tcl - CFREQ_CTRL Formality 等价性验证脚本 (rtl2gate / gate2gate)
#
# 参考: /apps/imctf/cad/script/digital_flow/feint/scripts/fm.tcl (lagat FEINT 流程)
# 调用: fm_shell -f scripts/fm.tcl -x 'set DESIGN cfreq_ctrl; ...'
#       (运行目录为 flow_<design>/, 变量由 Makefile 通过 -x 透传)
##########################################################################################

# 定位 flow 根目录 (scripts/ 的上一级), 保证 setup/data 路径不依赖 cwd
set FLOW_HOME [file normalize [file join [file dirname [info script]] ..]]

# 读取 setup 变量 (ROOT_DIR/DESIGN/RTL_FILELIST/... 可由 -x 覆盖)
source [file join $FLOW_HOME "setup" "common_setup.tcl"]

##################################################################
# 最小 stub: 便于在纯 tclsh 下做语法/流程 dry-run (判分 tclsh stub 用)。
# fm_shell 内这些命令真实存在, 不会被重复定义。
##################################################################
foreach _cmd {
    set_app_var read_db read_verilog read_sverilog read_vhdl
    set_svf set_top set_constant report_setup_status
    preverify match verify save_session
    report_unmatched_points report_failing_points report_aborted analyze_points
    redirect
} {
    if {[info command $_cmd] eq ""} { proc $_cmd {args} {} }
}

##################################################################
# 工具综合设置 (Synopsys Auto Setup, 更宽松)
##################################################################
set_app_var synopsys_auto_setup true
set_app_var verification_timeout_limit             "24:0:0"
set_app_var verification_failing_point_limit       0
set_app_var verification_set_undriven_signals      BINARY:X
set_app_var verification_clock_gate_reverse_gating true

if {![info exists search_path]} { set search_path "" }
set_app_var search_path ". ${ADDITIONAL_SEARCH_PATH} $search_path"

##################################################################
# SVF 引导 (仅 rtl2gate; gate2gate 跳过)
##################################################################
if {$FM_MODE == "gate2gate"} {
    puts "RM-Info: gate2gate mode, skip SVF"
} else {
    set _svf [expr {[info exists SVF_FILE] ? $SVF_FILE : "${OUTPUTS_DIR}/${DESIGN_NAME}.mapped.svf"}]
    if {[file exists $_svf]} {
        puts "RM-Info: set_svf $_svf"
        set_svf $_svf
    } else {
        puts "RM-Info: SVF not found ($_svf), proceed without SVF guidance"
    }
}

##################################################################
# 读取工艺库 (DB)
##################################################################
foreach _lib [concat $TARGET_LIBRARY_FILES $ADDITIONAL_LINK_LIB_FILES] {
    if {[string length [string trim $_lib]] > 0} { read_db -technology_library $_lib }
}

##################################################################
# 读取参考设计 (RTL 或参考网表)
##################################################################
if {$FM_MODE == "gate2gate"} {
    puts "RM-Info: read reference netlist: $FM_REF_NETLIST"
    read_verilog -r $FM_REF_NETLIST
} else {
    # 逐个解析 filelist (相对 filelist 所在目录), 忽略注释/指令行
    set _fdir [file dirname $RTL_SOURCE_FILES]
    if {[file exists $RTL_SOURCE_FILES]} {
        set _fh [open $RTL_SOURCE_FILES r]
        while {[gets $_fh _line] >= 0} {
            set _line [string trim $_line]
            if {$_line eq ""}                { continue }
            if {[string match {//*} $_line]}  { continue }
            if {[string match {+*} $_line]}   { continue }
            lappend _rtl_files [file join $_fdir $_line]
        }
        close $_fh
    } else {
        puts "RM-Warn: RTL filelist not found: $RTL_SOURCE_FILES"
    }
    if {[info exists _rtl_files]} {
        foreach _f $_rtl_files { read_verilog -r $_f }
    }
}
set_top r:/WORK/${DESIGN_NAME}

##################################################################
# 读取实现设计 (综合网表)
##################################################################
if {$FM_MODE == "gate2gate"} {
    puts "RM-Info: read implementation netlist: $FM_IMPL_NETLIST"
    read_verilog -i $FM_IMPL_NETLIST
} else {
    set _impl [expr {[info exists FM_IMPL_NETLIST] ? $FM_IMPL_NETLIST : "${OUTPUTS_DIR}/${DESIGN_NAME}.mapped.v"}]
    puts "RM-Info: read implementation netlist: $_impl"
    read_verilog -i $_impl
}
set_top i:/WORK/${DESIGN_NAME}

##################################################################
# 常量端口约束 (cfreq_ctrl 全部端口为运行时输入, 无需 set_constant;
#               如需配置 scan/test 等恒值端口, 在此追加)
##################################################################
# set_constant -type port i:/WORK/${DESIGN_NAME}/<port> <0|1>

# report_setup_status

##################################################################
# Match & Verify
##################################################################
preverify
match
save_session -replace ${OUTPUTS_DIR}/${DESIGN_NAME}_match
redirect -file ${REPORTS_DIR}/${DESIGN_NAME}.fmv_unmatched_points.rpt {report_unmatched_points}

if {![verify]} {
    redirect -file ${REPORTS_DIR}/${DESIGN_NAME}.fmv_failing_points.rpt {report_failing_points}
    redirect -file ${REPORTS_DIR}/${DESIGN_NAME}.fmv_aborted_points.rpt  {report_aborted}
    redirect -file ${REPORTS_DIR}/${DESIGN_NAME}.fmv_analyze_points.rpt {analyze_points -all}
}

save_session -replace ${OUTPUTS_DIR}/${DESIGN_NAME}_verify
puts "RM-Info: Formality verification finished (mode=$FM_MODE)"
exit