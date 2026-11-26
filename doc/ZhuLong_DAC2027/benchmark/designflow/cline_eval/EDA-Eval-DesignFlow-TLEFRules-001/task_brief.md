交付接口：outputs/submit.zip 内含 lef_rules.py（接受一个 techlef 路径作命令行参数，stdout 输出 JSON 结构化汇总）、rules_report_A.md、README.md。
techlef 文件位于 assets/tech_thk2d0_m5.lef。
JSON schema：routing_layers[{name,direction,width,pitch[],max_width,area,offset,spacing_table}] / cut_layers[{name,spacing,adjacent_cuts_spacing}] / vias[{name,cuts,resistance,layers[]}] / viarules[{name,layers[],has_spacing,enclosures{},width_range{<layer>:"<min> TO <max>"}}]。width_range 是 dict，键=层名(如 M1)，值="min TO max" 字符串(如 "0.88 TO 14")，不是嵌套 dict。
