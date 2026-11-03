###############################################################################
# 8_report_timing.tcl -- 主要时序报告(setup / hold / min_max / global)
###############################################################################
puts "RM-Info: 8_report_timing: generating timing reports ..."

report_timing -delay max -slack_lesser_than 0.0 -nosplit -input -net -path_type full \
    > $RPT_DIR/${DESIGN_NAME}_report_timing_setup_${CORNER}_${MODE}.rpt

report_timing -delay min -slack_lesser_than 0.0 -nosplit -input -net -path_type full \
    > $RPT_DIR/${DESIGN_NAME}_report_timing_hold_${CORNER}_${MODE}.rpt

report_timing -delay min_max -slack_lesser_than 0.0 -nosplit \
    > $RPT_DIR/${DESIGN_NAME}_report_timing_minmax_${CORNER}_${MODE}.rpt

report_global_timing > $RPT_DIR/${DESIGN_NAME}_report_global_timing_${CORNER}_${MODE}.rpt

puts "RM-Info: 8_report_timing: done."