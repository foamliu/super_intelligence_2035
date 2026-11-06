##########################################################################################
# common_setup.tcl - CFREQ_CTRL VCS 覆盖率检查流程变量
#
# 参考: lagat_flow_ref/syn/setup/common_setup.tcl 变量接口
# 本文件被 scripts/cov.tcl source, 变量可由命令行/环境覆盖。
##########################################################################################

##################################################################
# Input variable defaults
##################################################################
if {![info exists ROOT_DIR]}         { set ROOT_DIR         [file normalize [file join [file dirname [info script]] ..]] }
if {![info exists DESIGN]}           { set DESIGN           "cfreq_ctrl" }
if {![info exists RTL_FILELIST]}     { set RTL_FILELIST     "$ROOT_DIR/data/syn_filelist.f" }
if {![info exists RTL_SOURCE_FORMAT]} { set RTL_SOURCE_FORMAT "verilog" }
if {![info exists COV_METRICS]}      { set COV_METRICS      "line+cond+tgl+fsm+branch" }
if {![info exists TB_FILE]}          { set TB_FILE          "$ROOT_DIR/data/tb_${DESIGN}.sv" }

##################################################################
# Design common variables
##################################################################
set DESIGN_NAME      $DESIGN
set DESIGN_STYLE     "flat"
set RTL_SOURCE_FILES $RTL_FILELIST

##################################################################
# Output Directories (相对 flow_<design>/ 运行目录)
##################################################################
set REPORTS_DIR    reports
set OUTPUTS_DIR    results