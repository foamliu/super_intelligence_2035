###############################################################################
# common_setup.tcl -- PrimeTime STA flow variable hub
#
# 所有变量都提供默认值(default)。它们通过 pt_shell 的 -x 选项(或 source 之前的
# set 命令)即可被外部覆盖，从而实现"按 corner / mode 传参适配"。
#
# 变量命名与 feint 参考流(/apps/imctf/cad/script/digital_flow/feint)保持一致。
# 核心规则：`if {![info exists VAR]}` 保证默认值只在未定义时生效，
# 即 -x 传入的同名变量优先级最高。
###############################################################################

###################################################################
# Flow directory layout
###################################################################
if {![info exists ROOT_DIR]}     { set ROOT_DIR     "." }
if {![info exists SCR_DIR]}      { set SCR_DIR      "$ROOT_DIR/scr" }
if {![info exists SETUP_DIR]}    { set SETUP_DIR    "$ROOT_DIR/setup" }
if {![info exists DATA_DIR]}     { set DATA_DIR     "$ROOT_DIR/data" }

# 输出件层次(用户已生成的层次)
if {![info exists LOG_DIR]}      { set LOG_DIR      "$ROOT_DIR/log" }
if {![info exists RPT_DIR]}      { set RPT_DIR      "$ROOT_DIR/rpt" }
if {![info exists SDC_DIR]}      { set SDC_DIR      "$ROOT_DIR/sdc" }
if {![info exists SESSION_DIR]}  { set SESSION_DIR  "$ROOT_DIR/session" }

###################################################################
# Design / Corner / Mode
###################################################################
if {![info exists DESIGN]}       { set DESIGN       "demo" }
if {![info exists DESIGN_NAME]}  { set DESIGN_NAME  "$DESIGN" }
if {![info exists CORNER]}       { set CORNER       "tt0p8v25c" }
if {![info exists PT_CORNER]}    { set PT_CORNER    "$CORNER" }
if {![info exists MODE]}         { set MODE         "func" }
if {![info exists PT_MODE]}      { set PT_MODE      "$MODE" }

###################################################################
# Tool selection (module / version)
###################################################################
if {![info exists PT_VERSION]}   { set PT_VERSION   "U-2022.12-SP5" }
if {![info exists PT_ROOT]}      { set PT_ROOT      "/apps/synopsys/primetime" }

###################################################################
# Library inputs (子模块 lib 输入件)
###################################################################
if {![info exists ANALYSIS_LIBRARY_FILES]}     { set ANALYSIS_LIBRARY_FILES    "" }
if {![info exists ADDITIONAL_LINK_LIB_FILES]}  { set ADDITIONAL_LINK_LIB_FILES "" }
if {![info exists ADDITIONAL_SEARCH_PATH]}     { set ADDITIONAL_SEARCH_PATH    "" }

###################################################################
# Netlist / Constraint / Parasitic inputs
###################################################################
if {![info exists NETLIST_FILES]}    { set NETLIST_FILES    "" }
if {![info exists CONSTRAINT_FILES]} { set CONSTRAINT_FILES "" }
if {![info exists PARASITIC_FILES]}  { set PARASITIC_FILES  "" }
if {![info exists PARASITIC_PATHS]}  { set PARASITIC_PATHS  "" }
if {![info exists POCVM_FILES]}      { set POCVM_FILES      "" }

###################################################################
# Session / naming
###################################################################
if {![info exists SESSION_NAME]} { set SESSION_NAME "${DESIGN_NAME}_${CORNER}_${MODE}_ss" }

###################################################################
# 通用工具：按扩展名在指定目录(含一级子目录，如 data/lib)中查找文件。
# 用于 demo design 未显式指定 lib/netlist/sdc/spef 时的自动发现。
###################################################################
proc sta_find_files {dir patterns} {
    set out {}
    foreach pat $patterns {
        foreach m [glob -nocomplain -types f [file join $dir $pat]] {
            lappend out $m
        }
        foreach m [glob -nocomplain -types f [file join $dir * $pat]] {
            lappend out $m
        }
    }
    return [lsort -unique $out]
}