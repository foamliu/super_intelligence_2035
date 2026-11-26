# common_setup.tcl —— A 档真实环境（kaidi.wang / flow_pa_cpu_merged_top / DC NXT / hplp / WLM）
# 由工程提供；wlm_multibit.tcl source 本文件取用下列变量。

set DESIGN_NAME      pa_cpu_merged_top
set MB_LIB_PREFIX    DBCP51H180L6W25T5_MB_SVT
set MB_CELL_PATTERN  {MB[24]SDF*}
set OPT_MODE         timing_only
set CRITICAL_RANGE   0.1
set REPORTS_DIR      reports
