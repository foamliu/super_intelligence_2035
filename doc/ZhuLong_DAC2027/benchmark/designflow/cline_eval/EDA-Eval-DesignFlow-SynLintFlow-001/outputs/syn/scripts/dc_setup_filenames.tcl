# =============================================================================
# dc_setup_filenames.tcl : 定义综合流程全部目录 / 文件名变量
# =============================================================================

# ---- 设计属性 ----
set DESIGN_NAME     "cfreq_ctrl"
set TOP_MODULE      "cfreq_ctrl"

# ---- 项目根目录 (本脚本位于 syn/scripts/, 向上两级即 syn/) ----
set SYN_ROOT        [file normalize [file dirname [file dirname [info script]]]]

# ---- 子目录 ----
set SETUP_DIR       "${SYN_ROOT}/setup"
set SCRIPTS_DIR     "${SYN_ROOT}/scripts"
set SDC_DIR         "${SYN_ROOT}/sdc"
set DATA_DIR        "${SYN_ROOT}/data"
set NETLIST_DIR     "${SYN_ROOT}/netlist"
set REPORTS_DIR     "${SYN_ROOT}/reports"
set LOG_DIR         "${SYN_ROOT}/logs"

# ---- 输入文件 ----
set RTL_FILELIST    "${DATA_DIR}/syn_filelist.f"
set SDC_FILE        "${SDC_DIR}/${DESIGN_NAME}.sdc"

# ---- 输出文件 ----
set NETLIST_FILE    "${NETLIST_DIR}/${DESIGN_NAME}.mapped.v"
set DDC_FILE        "${NETLIST_DIR}/${DESIGN_NAME}.ddc"
set REPORT_PREFIX   "${REPORTS_DIR}/${DESIGN_NAME}"

# ---- 目录准备 ----
file mkdir $NETLIST_DIR
file mkdir $REPORTS_DIR
file mkdir $LOG_DIR