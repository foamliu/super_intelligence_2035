###############################################################################
# 10_rpt.tcl -- 汇总报告 / 生成 .sdc / 保存 session / 退出
###############################################################################
puts "RM-Info: 10_rpt: final reports + session ..."

report_qor > $RPT_DIR/${DESIGN_NAME}_report_qor_${CORNER}_${MODE}.rpt

# 生成派生约束文件(sdc 输出件，存放到 sdc/ 目录)
write_sdc $SDC_DIR/${DESIGN_NAME}_${CORNER}_${MODE}.sdc

# 保存 session 供 pt_shell 交互式继续调试(session 输出件)
save_session $SESSION_DIR/$SESSION_NAME

puts "RM-Info: STA flow done: $DESIGN_NAME ($CORNER/$MODE)"
puts "RM-Info: reports -> $RPT_DIR"
puts "RM-Info: sdc     -> $SDC_DIR/${DESIGN_NAME}_${CORNER}_${MODE}.sdc"
puts "RM-Info: session -> $SESSION_DIR/$SESSION_NAME"

exit