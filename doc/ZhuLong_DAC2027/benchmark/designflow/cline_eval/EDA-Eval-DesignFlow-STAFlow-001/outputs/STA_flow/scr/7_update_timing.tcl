###############################################################################
# 7_update_timing.tcl -- 时序更新与自检
###############################################################################
puts "RM-Info: 7_update_timing: update_timing -full ..."
update_timing -full

check_timing -verbose > $RPT_DIR/${DESIGN_NAME}_check_timing_${CORNER}_${MODE}.rpt

puts "RM-Info: 7_update_timing: done."