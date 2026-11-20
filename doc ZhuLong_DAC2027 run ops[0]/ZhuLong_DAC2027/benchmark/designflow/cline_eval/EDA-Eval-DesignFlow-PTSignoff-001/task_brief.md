# 交付接口
- 交付 `outputs/submit.zip`，内含 4 个文件：`tcl/pt_sta.tcl`、`setup/common_setup.tcl`、`run_pt.csh`、`README.md`。
- 入口契约：`mode=design_flow`，`entry_point=outputs/submit.zip`，`test=check(submit.zip, workdir)`。
- 资产（本目录）：`postroute.v`（布线后网表）、`routed.spef`（StarRC 提取的寄生 SPEF）、`mapped.sdc`（约束，set_max_delay 0.5）。库 `data/ss_text.db`（库名 `SS_0p98_m40c`）由环境预编译，脚本按路径引用即可。
