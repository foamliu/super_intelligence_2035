交付：outputs/submit.zip，解压后为 STA flow 脚手架（run/ 下一个 cshell 运行脚本，scr/ 下 sta_main.tcl + 1_setup.tcl … 10_rpt.tcl 编号 Tcl 脚本）。
约束：cshell 运行脚本须支持 -corner/-mode 传参；Tcl 脚本经 sta_main.tcl 按编号顺序 source；不要求真跑 PrimeTime，只需可被静态校验的完整脚本结构。
