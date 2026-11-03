###############################################################################
# 1_setup.tcl -- 环境配置 / 工具选型 / 输出目录
###############################################################################
puts "RM-Info: 1_setup: ================== Environment setup =================="
puts "RM-Info: 1_setup: design_name = $DESIGN_NAME"
puts "RM-Info: 1_setup: corner      = $CORNER (PT_CORNER=$PT_CORNER)"
puts "RM-Info: 1_setup: mode        = $MODE (PT_MODE=$PT_MODE)"
puts "RM-Info: 1_setup: pt_version  = $PT_VERSION"
puts "RM-Info: 1_setup: pt_root     = $PT_ROOT"

# ---- 输出件目录(log / rpt / sdc / session) ----
foreach _d [list $LOG_DIR $RPT_DIR $SDC_DIR $SESSION_DIR] {
    if {![file exists $_d]} { file mkdir $_d }
}

# ---- 全局开关 / 命令日志 ----
set sh_enable_page_mode          false
set sh_command_log_file          "$LOG_DIR/${DESIGN_NAME}_${CORNER}_${MODE}_command.log"
set sh_source_uses_search_path   true
# demo 过程中出错继续收集全部报告；正式 signoff 可改为 false
set sh_continue_on_error         true

# ---- search path：'.' + 用户附加路径 + 数据目录 ----
set search_path ". $ADDITIONAL_SEARCH_PATH $DATA_DIR $search_path"

puts "RM-Info: 1_setup: search_path = $search_path"