# 交付接口

- 输入：assets/ 目录下的附件（rtl/addr_to_rowcol_region.v 与 lib/stdcells_ac_FF_1p3_m40c.db）。
- 交付：把 prompt 要求产出的所有文件打包成 outputs/submit.zip（文件平铺或放在同一子目录），判分器静态校验脚本结构与参数化泛型，不会真正启动 dc_shell。
