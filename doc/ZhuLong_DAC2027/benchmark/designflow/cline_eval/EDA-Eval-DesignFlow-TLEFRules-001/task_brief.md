交付接口：outputs/submit.zip 内含 lef_rules.py（接受一个 techlef 路径作命令行参数，stdout 输出 JSON 结构化汇总）、rules_report_A.md、README.md。
techlef 文件位于 assets/tech_thk2d0_m5.lef。
JSON schema：routing_layers[{name,direction,width,pitch[],max_width,area,offset,spacing_table}] / cut_layers[{name,spacing,adjacent_cuts_spacing}] / vias[{name,cuts,resistance,layers[]}] / viarules[{name,layers[],has_spacing,enclosures{},width_range{}}]。
