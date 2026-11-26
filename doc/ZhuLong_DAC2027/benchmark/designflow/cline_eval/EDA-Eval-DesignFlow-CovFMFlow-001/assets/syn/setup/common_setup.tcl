##########################################################################################
# common_setup.tcl - CFREQ_CTRL Design Compiler 综合流程设计/库变量
#
# 参考: lagat_flow_ref/syn/setup/common_setup.tcl (lagat FEINT 流程)
# 本文件被 scripts/dc.tcl source, 变量可由 Makefile 通过 dc_shell -x 覆盖。
##########################################################################################

##################################################################
# Input variable defaults (由 Makefile -x 传入, 此处给缺省值)
##################################################################
if {![info exists ROOT_DIR]}     { set ROOT_DIR     [file normalize [file join [file dirname [info script]] ..]] }
if {![info exists DESIGN]}       { set DESIGN       "cfreq_ctrl" }
if {![info exists RTL_FILELIST]} { set RTL_FILELIST "$ROOT_DIR/data/syn_filelist.f" }
if {![info exists SDC]}          { set SDC          "$ROOT_DIR/data/${DESIGN}.sdc" }
if {![info exists LINK_LIB_PATH]} { set LINK_LIB_PATH "$ROOT_DIR/data/lib" }
if {![info exists FM_MODE]}      { set FM_MODE      "" }
if {![info exists PT_CORNER]}    { set PT_CORNER    "" }

##################################################################
# Design common variables
##################################################################
set DESIGN_NAME                            $DESIGN
set INSERT_DFT                             false  ;# cfreq_ctrl 为模拟辅助小模块, 不插 DFT
set DESIGN_STYLE                           "flat"

##################################################################
# Tool Setup Variables
##################################################################
set DC_MAX_CORES                           4
set DCRM_ALIB_CACHE                        .

##################################################################
# Library Setup Variables
# 工艺: HL22 (lagat 项目), 综合角与 lagat 主流程一致:
#   ssg 0.72V -40C (CCS)
#   - ulvt: 高速路径   - lvt: 常规路径
# 如需换角, 修改为对应 PDK 目录下的 .db (ffg_0p88v_125c 等)。
##################################################################
set HL22_PDK_ROOT   "/apps/imctf/extpdk/HL22/LAGAT/Digital/current"

set TARGET_LIBRARY_FILES          "$HL22_PDK_ROOT/Au22_basic_ulvt/lib/Au22_basic_ulvt_ssg_0p72v_m40c_ccs.db \
                                   $HL22_PDK_ROOT/Au22_basic_lvt/lib/Au22_basic_lvt_ssg_0p72v_m40c_ccs.db"

set REFERENCE_LIBRARY             ""   ;# NDM reference library (flat flow 不用)
set ADDITIONAL_SEARCH_PATH        ""   ;# 追加搜索路径 (供所有工具使用)

# 追加 link 库: cfreq_ctrl 为纯数字小模块, 无模拟/IP 宏单元;
# 若后续引入 IP, 将其 .db 放入 data/lib 并在下方列出 (变量接口与 lagat 一致)。
set ADDITIONAL_LINK_LIB_FILES     ""

##################################################################
# Design Input Files
##################################################################
set RTL_SOURCE_FORMAT                              sverilog  ;# verilog | sverilog
set RTL_SOURCE_FILES                               $RTL_FILELIST
set DCRM_CONSTRAINTS_INPUT_FILE                    $SDC

##################################################################
# Output Directories (相对 flow_<design>/ 运行目录)
##################################################################
set REPORTS_DIR             reports
set OUTPUTS_DIR             results
