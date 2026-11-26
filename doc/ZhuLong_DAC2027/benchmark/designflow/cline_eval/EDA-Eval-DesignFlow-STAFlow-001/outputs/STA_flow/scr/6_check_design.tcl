###############################################################################
# 6_check_design.tcl -- 设计 / 约束自检
###############################################################################
puts "RM-Info: 6_check_design: checking design ..."

check_constraints -verbose > $RPT_DIR/${DESIGN_NAME}_check_constraints_${CORNER}_${MODE}.rpt

report_design > $RPT_DIR/${DESIGN_NAME}_report_design_${CORNER}_${MODE}.rpt

puts "RM-Info: 6_check_design: done."