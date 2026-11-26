交付：outputs/submit.zip，含一个可运行的 Python 脚本 `delete_pg.py`（CLI: `python3 delete_pg.py <input.lib> <output.lib>`，纯标准库实现，不依赖第三方库）。
脚本读取输入 .lib，按 prompt 的 3 条规则删除 pg_pin(VDD/VSS) 块（用大括号深度匹配整块）及任何含 "VDD" 或 "VSS" 的行，把清洗后的 .lib 写到 output 路径。
判分时会用一份结构不同的隐藏 .lib（B）重新运行你的脚本，校验清洗结果结构与跨输入一致性。
