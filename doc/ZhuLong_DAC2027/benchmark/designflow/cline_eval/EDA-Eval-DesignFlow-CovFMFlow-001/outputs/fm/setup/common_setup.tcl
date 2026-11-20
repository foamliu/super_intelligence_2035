##########################################################################################
# common_setup.tcl - CFREQ_CTRL Formality 形式验证流程设计/库变量
#
# 参考: lagat_flow_ref/syn/setup/common_setup.tcl (lagat FEINT 流程)
# 本文件被 scripts/fm.tcl source, 变量可由 Makefile 通过 fm_shell -x 覆盖。
##########################################################################################

##################################################################
# Input variable defaults (由 Makefile -x 传入, 此处给缺省值)
##################################################################
if {![info exists ROOT_DIR]}         { set ROOT_DIR         [file normalize [file join [file dirname [info script]] ..]] }
if {![info exists DESIGN]}           { set DESIGN           "cfreq_ctrl" }
if {![info exists RTL_FILELIST]}     { set RTL_FILELIST     "$ROOT_DIR/data/syn_filelist.f" }
if {![info exists RTL_SOURCE_FORMAT]} { set RTL_SOURCE_FORMAT "verilog" }
if {![info exists FM_MODE]}          { set FM_MODE          "rtl2gate" }
if {![info exists FM_REF_NETLIST]}   { set FM_REF_NETLIST   "$ROOT_DIR/data/netlist/${DESIGN}.mapped.v" }
if {![info exists FM_IMPL_NETLIST]}  { set FM_IMPL_NETLIST  "$ROOT_DIR/data/netlist/${DESIGN}.mapped.v" }
if {![info exists SVF_FILE]}         { set SVF_FILE         "$ROOT_DIR/data/${DESIGN}.svf" }
if {![info exists PROJECT_HOME]}     { set PROJECT_HOME     "$ROOT_DIR/../" }

##################################################################
# Design common variables
##################################################################
set DESIGN_NAME                 $DESIGN
set DESIGN_STYLE                "flat"
set RTL_SOURCE_FILES            $RTL_FILELIST

##################################################################
# Library Setup Variables
# 工艺: HL22 (lagat 项目), 与综合/syn 流程一致:
#   ssg 0.72V -40C (CCS); ulvt 高速路径 + lvt 常规路径
##################################################################
set HL22_PDK_ROOT   "/apps/imctf/extpdk/HL22/LAGAT/Digital/current"

set TARGET_LIBRARY_FILES        "$HL22_PDK_ROOT/Au22_basic_ulvt/lib/Au22_basic_ulvt_ssg_0p72v_m40c_ccs.db \
                                 $HL22_PDK_ROOT/Au22_basic_lvt/lib/Au22_basic_lvt_ssg_0p72v_m40c_ccs.db"
set ADDITIONAL_LINK_LIB_FILES   ""
set ADDITIONAL_SEARCH_PATH      ""

##################################################################
# Output Directories (相对 flow_<design>/ 运行目录)
##################################################################
set REPORTS_DIR    reports
set OUTPUTS_DIR    results