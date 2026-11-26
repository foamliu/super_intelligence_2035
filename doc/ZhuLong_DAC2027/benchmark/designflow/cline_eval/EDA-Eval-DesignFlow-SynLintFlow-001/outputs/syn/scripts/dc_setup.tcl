# =============================================================================
# dc_setup.tcl : cfreq_ctrl 综合流程顶层设置脚本
# 由 dc.tcl source。负责:
#   1) 计算项目根目录
#   2) source 文件名定义 (dc_setup_filenames.tcl)
#   3) source 公共设置 (common_setup.tcl)
#   4) 应用库 / search_path 与通用变量
# =============================================================================

set SYN_ROOT [file normalize [file dirname [file dirname [info script]]]]

source -echo -verbose ${SYN_ROOT}/scripts/dc_setup_filenames.tcl
source -echo -verbose ${SYN_ROOT}/setup/common_setup.tcl

# ---- 应用库设置 ----
set search_path     [concat ${ADDITIONAL_SEARCH_PATH} ${SYN_ROOT} ${SCRIPTS_DIR} ${DATA_DIR}]
set target_library  ${TARGET_LIBRARY_FILES}
set link_library    ${LINK_LIBRARY_FILES}
set symbol_library  ${SYMBOL_LIBRARY_FILES}

# ---- 通用读入 / 输出变量 ----
set hdlin_auto_save_templates        "true"
set verilogout_no_tri                "true"
set verilogout_show_unconnected_pins "true"
set compile_enable_auto_ungroup      "true"