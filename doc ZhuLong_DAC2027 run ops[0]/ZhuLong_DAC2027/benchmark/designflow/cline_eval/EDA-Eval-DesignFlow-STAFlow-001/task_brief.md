# 交付接口

交付 `outputs/submit.zip`，解压后顶层为 `STA_flow/` 目录，须含下列文件结构（验收只读此结构，不实跑 pt_shell）：

STA_flow/README.md
STA_flow/setup/common_setup.tcl
STA_flow/scr/: sta_main.tcl + 10 个编号步骤 tcl（1_setup, 2_read_lib, 3_read_design, 4_read_constraint, 5_read_parasitic, 6_check_design, 7_update_timing, 8_report_timing, 9_analyze_timing, 10_rpt）
STA_flow/run/: run_sta.csh, run_demo.csh

判分器把隐藏的 demo design 放入 `STA_flow/data/` 后静态校验脚本结构与参数化泛型。参考流见附件 feint_reference/（pt.tcl.excerpt + common_setup.tcl.excerpt）。
