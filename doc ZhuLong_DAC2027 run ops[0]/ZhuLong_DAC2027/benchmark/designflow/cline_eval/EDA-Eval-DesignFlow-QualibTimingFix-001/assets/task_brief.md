交付：outputs/submit.zip，解压后为单个脚本 qualib_timing_fix.py。
A 输入：assets/fixtures/CXN4HCSPS512X8M4B2C1R1W1BW1RE1_FS/ 下的 .v 与 .lib，以及 assets/fixtures/report/（含 X_S_Check_inspection.html 与 result_xcheck_Verilog_Tmlib/*timing_constraint.html）。
程序 CLI：python3 qualib_timing_fix.py <verilog> <lib> <html_dir> <out_dir>，在 out_dir 写出 fix_report.json + <model>_fixed.v；脚本须通用、不硬编码 A 的 pin/弧，对结构不同的隐藏 SRAM 模型也能正确诊断与修复。
