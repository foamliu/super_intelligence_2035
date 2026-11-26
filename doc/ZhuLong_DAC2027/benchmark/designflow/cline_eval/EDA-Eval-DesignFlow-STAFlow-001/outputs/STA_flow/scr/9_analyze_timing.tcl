###############################################################################
# 9_analyze_timing.tcl -- 时钟 / 覆盖率 / 约束违反等分析报告
###############################################################################
puts "RM-Info: 9_analyze_timing: analyzing timing ..."

report_analysis_coverage > $RPT_DIR/${DESIGN_NAME}_report_analysis_coverage_${CORNER}_${MODE}.rpt

report_clock -skew -attribute > $RPT_DIR/${DESIGN_NAME}_report_clock_${CORNER}_${MODE}.rpt

report_constraint -all_violators -verbose > $RPT_DIR/${DESIGN_NAME}_report_constraint_${CORNER}_${MODE}.rpt

report_case_analysis > $RPT_DIR/${DESIGN_NAME}_report_case_analysis_${CORNER}_${MODE}.rpt

puts "RM-Info: 9_analyze_timing: done."