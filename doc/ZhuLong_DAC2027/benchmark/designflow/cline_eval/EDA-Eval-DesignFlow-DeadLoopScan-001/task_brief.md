交付接口：outputs/submit.zip 内含 dead_loop_scan.py（纯 Python 标准库，无第三方依赖）。
CLI: python3 dead_loop_scan.py <sv_file>  （扫描 SystemVerilog 文件中的循环构造，统计 forever/for/while/do/repeat 各类循环的行号与数量，识别可能无法终止的死循环候选并给出原因，将 forever 监视器/驱动线程归为 intentional，输出结构化 JSON 到 stdout）
工作目录下的 global_dldo_bind_A.sv 对应 prompt 中 /proj/ddgoa/.../proj_common_files/global_dldo_bind.sv 的真实文件快照（fixture，只读分析，不要修改）。
