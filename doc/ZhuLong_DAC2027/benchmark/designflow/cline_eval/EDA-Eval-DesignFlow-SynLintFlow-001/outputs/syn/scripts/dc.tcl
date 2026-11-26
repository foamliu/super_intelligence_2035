# =============================================================================
# dc.tcl : cfreq_ctrl Design Compiler 综合主脚本
# 流程: setup -> read RTL -> elaborate/link -> SDC -> compile -> write outputs
# 由 Makefile 通过 "dc_shell -f scripts/dc.tcl" 调用 (工作目录 = syn/)
# =============================================================================

# ---- 0. 环境与设置 (定义目录/文件名并应用库设置) ----
source -echo -verbose ./scripts/dc_setup.tcl

# ---- 1. 读入 RTL 源文件列表 ----
read_file -format verilog ${RTL_FILELIST}

# ---- 2. 顶层设计 & 链接 / 唯一化 ----
current_design ${DESIGN_NAME}
link
uniquify

# ---- 3. 读入时序约束 ----
read_sdc ${SDC_FILE}

# ---- 4. 设计 / 时序检查 ----
check_design
check_timing

# ---- 5. 综合 ----
compile_ultra

# ---- 6. 输出网表 / 数据库 ----
change_names -rules verilog -hierarchy
write -format verilog -hierarchy -output ${NETLIST_FILE}
write -format ddc    -hierarchy -output ${DDC_FILE}

# ---- 7. 报告 ----
report_area                 -hierarchy > ${REPORT_PREFIX}.area.rpt
report_timing                            > ${REPORT_PREFIX}.timing.rpt
report_timing   -path full -max_paths 20 > ${REPORT_PREFIX}.timing_full.rpt
report_power                             > ${REPORT_PREFIX}.power.rpt
report_qor                               > ${REPORT_PREFIX}.qor.rpt
report_constraint -all_violators         > ${REPORT_PREFIX}.constraint.rpt

echo "cfreq_ctrl synthesis flow completed."
exit